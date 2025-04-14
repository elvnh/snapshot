import tomllib
from dataclasses import dataclass
from pathlib import Path
import argparse

@dataclass
class AppConfig:
    output_dir: Path
    max_failures: int
    test_configs: {}
    options: argparse.Namespace # TODO: handle this in a better way

@dataclass
class TestConfig:
    name: str
    command: str             # The command to run test
    return_code: int = 0     # Expected return code


def parse_app_config(args) -> AppConfig:
    # TODO: handle if file doesn't exist
    with open(args.config, 'rb') as f:
        data = tomllib.load(f)
        output_dir = "output" if "output_dir" not in data else data["output_dir"]
        max_failures = None if "max_failures" not in data else data["max_failures"]

        test_configs = {}

        for s in data["tests"].items():
            name = s[0]
            test_conf = TestConfig(name, **s[1])
            test_configs[name] = test_conf

        return AppConfig(Path(output_dir), max_failures, test_configs, args)
