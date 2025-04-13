import tomllib
from dataclasses import dataclass
from pathlib import Path

@dataclass
class AppConfig:
    output_dir: Path
    max_failures: int
    test_configs: {}


@dataclass
class TestConfig:
    name: str
    command: str             # The command to run test
    return_code: int = 0     # Expected return code


def parse_config_file(path: Path) -> AppConfig:
    with open(path, 'rb') as f:
        data = tomllib.load(f)
        output_dir = "output" if "output_dir" not in data else data["output_dir"]
        max_failures = None if "max_failures" not in data else data["max_failures"]

        test_configs = {}

        for s in data["tests"].items():
            name = s[0]
            test_conf = TestConfig(name, **s[1])
            test_configs[name] = test_conf

        return AppConfig(Path(output_dir), max_failures, test_configs)
