from enum import Enum
from dataclasses import dataclass
from config import *

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
