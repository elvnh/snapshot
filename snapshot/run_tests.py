import subprocess
import shutil
import shlex
import re

from comparison import *


# TODO: multithread
# Returns tuple of (passed, failed)
def run_tests(config: AppConfig, tests: [TestInstance], max_failures: int) -> ([TestResult], [TestResult]):
    passed = []
    failed = []

    for t in tests:
        cmd = format_command(t.config.command, t.input_file)
        output_file = get_received_output_file(config, t)
        exec_result = execute_command(cmd, output_file)

        if exec_result.returncode != t.config.return_code:
            fail = TestResult(t, TestResultKind.FAILED_EXECUTION, exec_result.returncode)
            failed.append(fail)

            if failures >= max_failures:
                break
        else:
            success = TestResult(t, TestResultKind.PASSED_EXECUTION)
            passed.append(success)

    return (passed, failed)


"""
def collect_test_results(config: AppConfig, exec_results: TestExecutionResult, failures: int) -> [CompareResult|TestExecutionResult]:
    results = []

    for result in exec_results:
        if result.kind == TestExecutionResultKind.PASS and failures < config.max_failures:
            cmp_result = compare_test_output_files(config, result.test)

            if cmp_result.kind == CompareResultKind.FAIL or \
               cmp_result.kind == CompareResultKind.MISSING_EXPECTED:
                failures += 1

            results.append(cmp_result)
        else:
            failures += 1
            results.append(result)

        return results
"""

def execute_command(command: str, output_file: Path) -> subprocess.CompletedProcess:
    with open(output_file, "w") as f:
        return subprocess.run(command, shell=True, stdout=f, stderr=f)


def format_command(command: str, filename: Path) -> str:
    return re.sub('{file}', shlex.quote(str(filename)), command)
