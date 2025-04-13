from dataclasses import dataclass
from enum import Enum
import subprocess
import shutil
import shlex
import re

from directories import *

@dataclass
class TestInstance:
    config: TestConfig
    input_file: Path

class TestExecutionResultKind(Enum):
    PASS = 0
    FAIL = 1

@dataclass
class TestExecutionResult:
    kind: TestExecutionResultKind
    test: TestInstance
    return_code: int = None


def gather_tests(test_configs: [TestConfig], files: [str]) -> [TestInstance]:
    result: [TestInstance] = []

    for test_cfg in test_configs:
        for f in files:
            # TODO: Validate that files exist
            test = TestInstance(test_cfg, Path(f))

            result.append(test)

    return result


# TODO: multithread
def run_tests(config: AppConfig, tests: [TestInstance]) -> [TestExecutionResult]:
    results = []

    for t in tests:
        cmd = format_command(t.config.command, t.input_file)
        output_file = get_received_output_file(config, t.config.name, t.input_file)
        exec_result = execute_command(cmd, output_file)

        if exec_result.returncode != t.config.return_code:
            fail = TestExecutionResult(TestExecutionResultKind.FAIL, t, exec_result.returncode)

            results.append(fail)
        else:
            passed = TestExecutionResult(TestExecutionResultKind.PASS, t)
            results.append(passed)

    return results


def execute_command(command: str, output_file: Path) -> subprocess.CompletedProcess:
    with open(output_file, "w") as f:
        return subprocess.run(command, shell=True, stdout=f, stderr=f)


def format_command(command: str, filename: Path) -> str:
    return re.sub('{file}', shlex.quote(str(filename)), command)
