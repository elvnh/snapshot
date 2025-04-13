import difflib

from test import *
from directories import *

class CompareResultKind(Enum):
    PASS = 0
    FAIL = 1
    MISSING_EXPECTED = 2

# TODO: instead only return if failed
@dataclass
class CompareResult:
    kind: CompareResultKind
    diff: [str] = None

def compare_test_output_files(config: AppConfig, test_instance: TestInstance) -> CompareResult:
    input_file = test_instance.input_file
    test_name = test_instance.config.name

    received_file = get_received_output_file(config, test_name, input_file)
    expected_file = get_expected_output_file(config, test_name, input_file)

    assert(received_file.exists())

    if not expected_file.exists():
        return CompareResult(kind=CompareResultKind.MISSING_EXPECTED)
    else:
        with open(received_file, 'r') as recv, open(expected_file, 'r') as exp:
            diff = list(difflib.unified_diff(exp.readlines(), recv.readlines(), lineterm=''))

            if diff:
                return CompareResult(kind=CompareResultKind.FAIL, diff=diff)
            else:
                return CompareResult(kind=CompareResultKind.PASS)
