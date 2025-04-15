from enum import Enum
from dataclasses import dataclass
from config import *


# A test that is yet to be executed
@dataclass
class TestInstance:
    config: TestConfig
    input_file: Path


class TestResultKind(Enum):
    FAILED_EXECUTION = 0
    PASSED_EXECUTION = 1
    MISSING_EXPECTED = 2
    FAILED_COMPARISON = 3
    PASSED_COMPARISON = 4


@dataclass
class TestResult:
    test: TestInstance
    kind: TestResultKind
    data: any = None

    def fail(self) -> bool:
        return self.kind == TestResultKind.FAILED_EXECUTION or \
            self.kind == TestResultKind.MISSING_EXPECTED or \
            self.kind == TestResultKind.FAILED_COMPARISON
