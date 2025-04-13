from config import *

@dataclass
class TestInstance:
    config: TestConfig
    input_file: Path


def gather_tests(test_configs: [TestConfig], files: [str]) -> [TestInstance]:
    result: [TestInstance] = []

    for test_cfg in test_configs:
        for f in files:
            # TODO: Validate that files exist
            test = TestInstance(test_cfg, Path(f))

            result.append(test)

    return result


def format_command(command: str, filename: Path) -> str:
    return re.sub('{file}', shlex.quote(str(filename)), command)
