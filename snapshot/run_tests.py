import subprocess
import shutil
import shlex
import re

from comparison import *
from accept import *


def run_single_test(config: AppConfig, test_instance: TestInstance) -> TestResult:
    result = execute_test_command(config, test_instance)

    if result.kind is TestResultKind.PASSED_EXECUTION:
        cmp_result = compare_test_output_files(config, result.test)

        if cmp_result is None:
            print(f"\nNo expected output for file '{result.test.input_file}' in test "
                  f"'{result.test.config.name}'.")
            # Unable to compare since there is no expected output
            should_save = config.options.save

            if config.options.interactive:
                should_save = prompt_to_save_output(config, result.test)

            if should_save:
                # Save received output as expected
                print('Saving output as expected output.\n')
                result.kind = TestResultKind.PASSED_COMPARISON
                accept_output(config, result.test)
            else:
                result.kind = TestResultKind.MISSING_EXPECTED
        elif cmp_result == []:
            # No diff between received and expected output, count as pass
            result.kind = TestResultKind.PASSED_COMPARISON
        else:
            # Diff between received and expected output
            should_save = config.options.save

            if config.options.interactive:
                print(f"Output for file '{result.test.input_file}' in test "
                      f"'{result.test.config.name}' differs from expected output:")
                print_diff(cmp_result)

                should_save = yes_no_prompt(
                    "Would you like to accept the new received output?", 'n'
                )

            if should_save:
                result.kind = TestResultKind.PASSED_COMPARISON

                accept_output(config, result.test)
            else:
                assert result.kind is TestResultKind.PASSED_EXECUTION

                result.kind = TestResultKind.FAILED_COMPARISON
                result.data = cmp_result

    return result;


def execute_test_command(config: AppConfig, test: TestInstance) -> TestResult:
    cmd = format_command(test.config.command, test.input_file)
    output_file = get_received_output_file(config, test)
    exec_result = execute_command(cmd, output_file)

    if exec_result.returncode != test.config.return_code:
        fail = TestResult(test, TestResultKind.FAILED_EXECUTION, exec_result.returncode)
        return fail
    else:
        success = TestResult(test, TestResultKind.PASSED_EXECUTION)
        return success


def execute_command(command: str, output_file: Path) -> subprocess.CompletedProcess:
    with open(output_file, "w") as f:
        return subprocess.run(command, shell=True, stdout=f, stderr=f)


def format_command(command: str, filename: Path) -> str:
    return re.sub('{file}', shlex.quote(str(filename)), command)
