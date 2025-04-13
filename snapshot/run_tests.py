import subprocess
import shutil
import shlex
import re

from comparison import *


# TODO: multithread
def run_tests(config: AppConfig, tests: [TestInstance], max_failures: int) -> [TestExecutionResult]:
    results = []
    failures = 0

    for t in tests:
        cmd = format_command(t.config.command, t.input_file)
        output_file = get_received_output_file(config, t)
        exec_result = execute_command(cmd, output_file)

        if exec_result.returncode != t.config.return_code:
            fail = TestExecutionResult(TestExecutionResultKind.FAIL, t, exec_result.returncode)
            results.append(fail)

            failures += 1

            if failures >= max_failures:
                break
        else:
            passed = TestExecutionResult(TestExecutionResultKind.PASS, t)
            results.append(passed)

    return results


def execute_command(command: str, output_file: Path) -> subprocess.CompletedProcess:
    with open(output_file, "w") as f:
        return subprocess.run(command, shell=True, stdout=f, stderr=f)


def format_command(command: str, filename: Path) -> str:
    return re.sub('{file}', shlex.quote(str(filename)), command)
