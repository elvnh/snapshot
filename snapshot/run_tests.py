import subprocess
import shutil
import shlex
import re

from comparison import *


# TODO: multithread
# Returns tuple of (passed, failed)
def execute_test_commands(config: AppConfig, tests: [TestInstance]) -> ([TestResult], [TestResult]):
    passed = []
    failed = []

    for t in tests:
        cmd = format_command(t.config.command, t.input_file)
        output_file = get_received_output_file(config, t)
        exec_result = execute_command(cmd, output_file)

        if exec_result.returncode != t.config.return_code:
            fail = TestResult(t, TestResultKind.FAILED_EXECUTION, exec_result.returncode)
            failed.append(fail)

            if len(failed) >= config.max_failures:
                break
        else:
            success = TestResult(t, TestResultKind.PASSED_EXECUTION)
            passed.append(success)

    return (passed, failed)


def execute_command(command: str, output_file: Path) -> subprocess.CompletedProcess:
    with open(output_file, "w") as f:
        return subprocess.run(command, shell=True, stdout=f, stderr=f)


def format_command(command: str, filename: Path) -> str:
    return re.sub('{file}', shlex.quote(str(filename)), command)
