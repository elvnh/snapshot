import argparse


from comparison import *

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

    args = parser.parse_args()

    if args.command == 'run':
        run(cfg, args)
    else:
        parser.print_help()


def run(config: AppConfig, args: [str]):
    # Gather tests
    tests_to_run = []

    if args.tests == '*':
        tests_to_run = list(config.test_configs.values())
    else:
        for t in args.tests:
            if t in config.test_configs.keys():
                tests_to_run.append(config.test_configs[t])
            else:
                print(f'No test called {t}.')
                assert False

    # TODO: gather_tests should check that all files exist
    test_instances = gather_tests(tests_to_run, args.input_files)

    # Execute tests
    test_exec_results = run_tests(config, test_instances)

    # TOOD: Check if we have exceeded max failures already

    # Go through all tests and compare outputs
    for result in test_exec_results:
        if result.kind == TestExecutionResultKind.PASS:
            cmp_result = compare_test_output_files(config, result.test)

            if cmp_result.kind == CompareResultKind.FAIL:
                print(f'File {result.test.input_file} differs from expected counterpart:')

                for line in cmp_result.diff:
                    print(line)
                pass
            if cmp_result.kind == CompareResultKind.MISSING_EXPECTED:
                print(f'File {result.test.input_file} lacks an expected counterpart.')
                pass
        else:
            assert False

if __name__ == '__main__':
    snapshot()
