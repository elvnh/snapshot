from run_tests import *
from accept import *


# TODO: make subparsers share arguments etc
# TODO: comma separated tests flag
# TODO: allow setting user specified file as expected output
# TODO: running from different directory


def snapshot():
    parser = create_parser()
    args = parser.parse_args()

    cfg = parse_app_config(args)

    setup_directories(cfg)

    test_configs = get_test_configs(cfg, args)
    test_instances = None

    if hasattr(args, 'input_files'):
        test_instances = gather_test_instances(test_configs, args.input_files)

    if args.command == 'run':
        run(cfg, test_instances, args)
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
        expected = get_expected_output_file(config, t.config.name, t.input_file)
        expected.unlink()


def rm(config: AppConfig, tests: [TestInstance], args):
    for t in tests:
        received = get_received_output_file(config, t.config.name, t.input_file)
        expected = get_expected_output_file(config, t.config.name, t.input_file)

        received.unlink(missing_ok=True)
        expected.unlink(missing_ok=True)


def diff(config: AppConfig, tests: [TestInstance], args):
    for t in tests:
        for f in args.input_files:
            cmp_result = compare_test_output_files(config, t)
            if cmp_result.kind != CompareResultKind.PASS:
                # TODO: if interactive, let user accept
                print(f"Received output for file '{f}' differs from expected output:")
                print_diff(cmp_result.diff)


def run(config: AppConfig, test_instances: [TestInstance], args):
    # to_compare: tests that successfully ran but need their outputs verifier
    # failed: tests that failed to run
    to_compare, failed = execute_test_commands(config, test_instances, config.max_failures)
    passed = []

    for result in to_compare:
        # Go through all candidates and compare their outputs to expected
        assert result.kind is TestResultKind.PASSED_EXECUTION

        if len(failed) >= config.max_failures:
            break

        cmp_result = compare_test_output_files(config, result.test)

        if cmp_result is None:
            # Unable to compare since there is no expected output
            if config.options.save:
                # Save received output as expected
                print(f"No expected output for file '{result.test.input_file}' in test "
                      f"'{result.test.config.name}', saving as expected.")
                result.kind = TestResultKind.PASSED_COMPARISON
                passed.append(result)
                accept_output(config, result.test)

            else:
                result.kind = TestResultKind.MISSING_EXPECTED
                failed.append(result)
        elif cmp_result == []:
            # No diff between received and expected output, count as pass
            result.kind = TestResultKind.PASSED_COMPARISON
            passed.append(result)
        else:
            # Diff between received and expected output
            if config.options.save:
                result.kind = TestResultKind.PASSED_COMPARISON
                passed.append(result)

                print(f"No expected output for file '{result.test.input_file}' in test "
                      f"'{result.test.config.name}', saving as expected.")
                accept_output(config, result.test)
            else:
                assert result.kind is TestResultKind.PASSED_EXECUTION
                result.kind = TestResultKind.FAILED_COMPARISON
                result.data = cmp_result
                failed.append(result)

    fail_count = len(failed)
    pass_count = len(passed)
    total_count = fail_count + pass_count

    print(f"\nPassed {pass_count}/{total_count} tests.\n")

    for fail in failed:
        if fail.kind is TestResultKind.MISSING_EXPECTED:
            print(f"File '{fail.test.input_file}' lacks expected output for "
                  f"test '{fail.test.config.name}'.")
        elif fail.kind is TestResultKind.FAILED_COMPARISON:
            print(f"Test:  '{fail.test.config.name}'")
            print(f"Input: '{fail.test.input_file}'")
            print('Failed due to differing outputs:')

            print_diff(fail.data)
        else:
            assert False


def accept(cfg: AppConfig, tests: [TestConfig], args: [str]):
    for t in tests:
        for f in args.input_files:
            accept_output(cfg, t)


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


def create_parser():
    parser = argparse.ArgumentParser(prog='snapshot')

    parser.add_argument('config', help='TOML config file.')
    parser.add_argument('-t', '--tests', help='Which tests to run.', nargs=1, default=['*'])

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


if __name__ == '__main__':
    snapshot()
