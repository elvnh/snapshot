from run_tests import *
from accept import *
from concurrent import futures

"""
TODO:
  - make subparsers share arguments etc
  - allow setting user specified file as expected output
  - running from different directory
  - nicer printing
  - reuse printing functionality
  - check that destination file names aren't already taken
  - tests
  - verbose option
  - allow aborting after certain amount of failures
"""

def snapshot():
    parser = create_parser()
    args = parser.parse_args()

    cfg = parse_app_config(args)

    setup_directories(cfg)

    test_configs = get_test_configs(cfg, args)
    test_instances = None

    if hasattr(args, 'input_files'):
        test_instances = gather_test_instances(test_configs, args.input_files)

        # TODO: remove args argument to command functions
    if args.command == 'run':
        run(cfg, test_instances)
    elif args.command == 'accept':
        accept(cfg, test_instances, args)
    elif args.command == 'diff':
        diff(cfg, test_instances, args)
    elif args.command == 'unaccept': # TODO: better name
        unaccept(cfg, test_instances, args)
    elif args.command == 'rm':
        rm(cfg, test_instances, args)
    elif args.command == 'clean':
        clean(cfg, test_instances, args)
    else:
        parser.print_help()


def clean(config: AppConfig, tests: [TestInstance], args):
    shutil.rmtree(config.output_dir)


def unaccept(config: AppConfig, tests: [TestInstance], args):
    for t in tests:
        expected = get_expected_output_file(config, t)
        should_unaccept = True

        if config.options.interactive and t.input_file.exists():
            should_unaccept = yes_no_prompt(
                f"Would you like too discard expected output for file '{t.input_file}' in test "
                f"'{t.config.name}'?",
                'n'
            )

        if should_unaccept:
            expected.unlink()


def rm(config: AppConfig, tests: [TestInstance], args):
    for t in tests:
        received = get_received_output_file(config, t)
        expected = get_expected_output_file(config, t)

        if received.exists() or expected.exists():
            should_remove = True

            if config.options.interactive:
                should_remove = yes_no_prompt(
                    "Would you like to remove the received and expected outputs for "
                    f"file '{t.input_file}' in test '{t.config.name}'?", 'n'
                )

            if should_remove:
                received.unlink(missing_ok=True)
                expected.unlink(missing_ok=True)


def diff(config: AppConfig, tests: [TestInstance], args):
    diff_count = 0

    with futures.ThreadPoolExecutor(config.options.jobs) as tp:
        futs = []

        for test in tests:
            fut = tp.submit(compare_test_output_files, config, test)
            futs.append(fut)

        for fut in futs:
            result = fut.result()

            if result:
                diff_count += 1

                print(f"Received output for file '{test.input_file}' in test '{test.config.name}' "
                      "differs from expected output:")
                print_diff(result)

                if config.options.interactive:
                    response = yes_no_prompt(
                        'Would you like to accept the received output as expected output?', 'n'
                    )

                    if response:
                        # TODO: print this in accept_output instead
                        print('Accepting received output as expected output.')
                        accept_output(config, test)

    print(f"Found diffs in {diff_count}/{len(tests)} tests.")


def run(config: AppConfig, test_instances: [TestInstance]):
    # TODO: if concurrent job count is 1, use a regular for loop instead
    # TODO: don't give each thread only one test at a time, instead split up
    #  test array into equally divided segments and give to threads
    passed = []
    failed = []

    threads = config.options.jobs
    with futures.ThreadPoolExecutor(threads) as tp:
        futs = []

        for test in test_instances:
            fut = tp.submit(run_single_test, config, test)

            futs.append(fut)

        for fut in futs:
            result = fut.result()

            if result.kind == TestResultKind.FAILED_COMPARISON or \
               result.kind == TestResultKind.MISSING_EXPECTED:
                # Test failed but has a chance of succeeding if user
                # accepts the new output
                should_save = config.options.save

                if config.options.interactive:
                    if result.kind == TestResultKind.FAILED_COMPARISON:
                        print(f"Output for file '{result.test.input_file}' in test "
                              f"'{result.test.config.name}' differs from expected output:")
                        print_diff(result.data)
                    elif result.kind == TestResultKind.MISSING_EXPECTED:
                        print(f"\nNo expected output for file '{result.test.input_file}' in test "
                              f"'{result.test.config.name}'.")

                    should_save = yes_no_prompt(
                        "Would you like to accept the new received output?", 'n'
                    )

                if should_save:
                    result.kind = TestResultKind.PASSED_COMPARISON
                    accept_output(config, result.test)
                    passed.append(result)
                else:
                    failed.append(result)
            else:
                passed.append(result)

    fail_count = len(failed)
    pass_count = len(passed)
    total_count = fail_count + pass_count

    print(f"\nPassed {pass_count}/{total_count} tests.\n")

    for fail in failed:
        if fail.kind is TestResultKind.MISSING_EXPECTED:
            print(f"Input file '{fail.test.input_file}' lacks expected output for "
                  f"test '{fail.test.config.name}'.")
        elif fail.kind is TestResultKind.FAILED_COMPARISON:
            print(f"Test:  '{fail.test.config.name}'")
            print(f"Input: '{fail.test.input_file}'")
            print('Failed due to differing outputs:')

            print_diff(fail.data)
        else:
            assert False


def accept(cfg: AppConfig, tests: [TestInstance], args: [str]):
    for t in tests:
        if t.input_file.exists():
            expected_file = get_expected_output_file(cfg, t)
            diff = compare_test_output_files(cfg, t)

            if diff or not expected_file.exists():
                should_accept = True

                if cfg.options.interactive:
                    should_accept = yes_no_prompt(
                        f"\nWould you like to accept output for file '{t.input_file}' "
                        f"in test '{t.config.name}'?", 'n')

                if should_accept:
                    accept_output(cfg, t)
        else:
            assert False


def run_single_test(config: AppConfig, test_instance: TestInstance) -> TestResult:
    result = execute_test_command(config, test_instance)

    if result.kind is TestResultKind.PASSED_EXECUTION:
        diff = compare_test_output_files(config, result.test)

        if diff is None:
            result.kind = TestResultKind.MISSING_EXPECTED
        elif diff == []:
            # No diff between received and expected output, count as pass
            result.kind = TestResultKind.PASSED_COMPARISON
        else:
            # Diff between received and expected output
            result.kind = TestResultKind.FAILED_COMPARISON
            result.data = diff

    return result;


def get_test_configs(config: AppConfig, args: [str]) -> [TestConfig]:
    tests = []

    if args.tests == ['*']:
        tests = list(config.test_configs.values())
    else:
        split = args.tests[0].split(',')

        for t in split:
            if t in config.test_configs.keys():
                tests.append(config.test_configs[t])
            else:
                print(f'No test called {t}.')
                assert False

    return tests


def gather_test_instances(test_configs: [TestConfig], files: [str]) -> [TestInstance]:
    result: [TestInstance] = []

    for test_cfg in test_configs:
        for f in files:
            path = Path(f)

            # TODO: proper error handling
            if not path.exists():
                print(f'No file called {f}')
                assert False
            else:
                test = TestInstance(test_cfg, Path(f))

            result.append(test)

    return result


def prompt_to_save_output(config: AppConfig, test: TestInstance) -> bool:
    result = yes_no_prompt('Would you like to save received output as expected output?', 'n')

    if result is not None:
        return result


def yes_no_prompt(prompt: str, default: chr) -> bool:
    assert default == 'y' or default == 'n'

    while True:
        print(prompt, '', end='')

        if default == 'y':
            print('[Y/n]')
        else:
            print('[y/N]')

        i = getch().lower()

        if i == '\n':
            i = default

        if i == 'y':
            return True
        elif i == 'n':
            return False
        else:
            print(f"Please respond by clicking y, n or Enter.\n")


def getch():
    import sys, termios, tty

    fd = sys.stdin.fileno()
    orig = termios.tcgetattr(fd)

    try:
        tty.setcbreak(fd)  # or tty.setraw(fd) if you prefer raw mode's behavior.
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSAFLUSH, orig)

def create_parser():
    parser = argparse.ArgumentParser(prog='snapshot')

    parser.add_argument('config', help='TOML config file.')
    parser.add_argument('-t', '--tests', help='Which tests to run.', nargs=1, default=['*'])
    parser.add_argument('-i', '--interactive', help='Interactive mode.', action='store_true')
    parser.add_argument('-j', '--jobs', default=1, type=int,
                            help='Maximum number of concurrent threads used.')

    subparsers = parser.add_subparsers(dest='command')

    run_parser = subparsers.add_parser('run', help='Run tests')
    run_parser.add_argument('input_files', nargs='+', help='Files to run tests on.')
    run_parser.add_argument('-s', '--save', action='store_true', default=False, help='Automatically accept all output.')


    accept_parser = subparsers.add_parser('accept', help='Accept received output.')
    accept_parser.add_argument('input_files', nargs='+', help='Files to accept.')

    unaccept_parser = subparsers.add_parser('unaccept', help='Unaccept received output.')
    unaccept_parser.add_argument('input_files', nargs='+', help='Files to unaccept.')

    rm_parser = subparsers.add_parser('rm', help='Remove received and expected output.')
    rm_parser.add_argument('input_files', nargs='+', help='Files to remove.')

    diff_parser = subparsers.add_parser('diff', help='Display difference between expected and received output files.')
    diff_parser.add_argument('input_files', nargs='+', help='Files to diff.')

    clean_parser = subparsers.add_parser('clean', help='Clean all expected and received files.')

    return parser

import cProfile
import pstats

if __name__ == '__main__':
    #cProfile.run('snapshot()', sort=pstats.SortKey.CUMULATIVE)
    snapshot()
