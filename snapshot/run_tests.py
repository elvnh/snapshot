import subprocess
import shutil
import shlex
import re

from comparison import *
from accept import *


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
