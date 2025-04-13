import argparse

from run_tests import *
from accept import *

# TODO: store args in AppConfig

def snapshot():
    # Read config
    cfg = parse_config_file('config.toml')

    # Create directories
    setup_directories(cfg)

    parser = argparse.ArgumentParser(prog='snapshot')

    parser.add_argument('config', help='TOML config file.')
    parser.add_argument('--tests', help='Which tests to run.', nargs='+', default='*')

    subparsers = parser.add_subparsers(dest='command')

    run_parser = subparsers.add_parser('run', help='Run tests')
    run_parser.add_argument('input_files', nargs='+', help='Files to run tests on.')
    run_parser.add_argument('--save', action='store_true', default=False, help='Automatically accept all output.')

    accept_parser = subparsers.add_parser('accept', help='Accept received output.')
    accept_parser.add_argument('input_files', nargs='+', help='Files to accept.')

    args = parser.parse_args()
    tests = get_test_configs(cfg, args)

    if args.command == 'run':
        run(cfg, tests, args)
    elif args.command == 'accept':
        accept(cfg, tests, args)
    else:
        parser.print_help()


def run(config: AppConfig, tests_to_run: [TestConfig], args):
    # TODO: call function to gather and validate input files as Path array
    test_instances = gather_tests(tests_to_run, args.input_files)

    # Execute tests
    test_exec_results = run_tests(config, test_instances, config.max_failures)

    failures = sum([1 for x in test_exec_results if x.kind == TestExecutionResultKind.FAIL])

    # TODO: report all failed executions before running tests

    # Go through all tests and compare outputs
    for result in test_exec_results:
        # Only continue running tests if we haven't exceeded max failures.
        # Otherwise, only report the failed executions and then stop.
        if result.kind == TestExecutionResultKind.PASS and failures < config.max_failures:
            cmp_result = compare_test_output_files(config, result.test)

            if args.save:
                accept_output(config, result.test.config, result.test.input_file)
            else:
                if cmp_result.kind == CompareResultKind.FAIL:
                    print(f'File {result.test.input_file} differs from expected counterpart:')

                    for line in cmp_result.diff:
                        # TODO: colored diff print
                        print(line)

                        failures += 1
                elif cmp_result.kind == CompareResultKind.MISSING_EXPECTED:
                    # TODO: save if --save flag is present
                    print(f'File {result.test.input_file} lacks an expected counterpart.')
                    failures += 1
        elif result.kind == TestExecutionResultKind.FAIL:
            print(f"Failed to run test '{result.test.config.name}' with input file '{result.test.input_file}'.")
        else:
            assert False


def accept(cfg: AppConfig, tests: [TestConfig], args: [str]):
    for t in tests:
        for f in args.input_files:
            accept_output(cfg, t, f)


def get_test_configs(config: AppConfig, args: [str]) -> [TestConfig]:
    tests = []

    if args.tests == '*':
        tests = list(config.test_configs.values())
    else:
        for t in args.tests:
            if t in config.test_configs.keys():
                tests.append(config.test_configs[t])
            else:
                print(f'No test called {t}.')
                assert False

    return tests


if __name__ == '__main__':
    snapshot()
