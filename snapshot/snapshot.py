import argparse
import re
from dataclasses import dataclass
import shlex
import shutil
import subprocess
import difflib
from enum import Enum

from tests import *

def snapshot():
    # Read config
    cfg = parse_config_file('config.toml')

    # Create directories
    setup_directories(cfg)

    parser = argparse.ArgumentParser(prog='snapshot')

    parser.add_argument('config', help='TOML config file.')
    parser.add_argument('--tests', help='Which tests to run.', nargs='+', default='*')

    subparsers = parser.add_subparsers(dest='command')

    run_parser = subparsers.add_parser('run', help='Run tests')
    run_parser.add_argument('input_files', nargs='+', help='Files to run tests on.')

    args = parser.parse_args()

    if args.command == 'run':
        # Gather tests
        tests_to_run = []

        if args.tests == ['*']:
            tests_to_run = list(cfg.test_configs.values())
        else:
            for t in args.tests:
                if t in cfg.test_configs.keys():
                    tests_to_run.append(cfg.test_configs[t])
                else:
                    print(f'No test called {t}.')
                    assert False

        test_instances = gather_tests(tests_to_run, args.input_files)
    else:
        parser.print_help()


def setup_directories(cfg: AppConfig):
    cfg.output_dir.mkdir(exist_ok=True)

    for test in cfg.test_configs.items():
        received_dir = get_received_output_dir(cfg, test[0])
        expected_dir = get_expected_output_dir(cfg, test[0])

        received_dir.mkdir(exist_ok=True, parents=True)
        expected_dir.mkdir(exist_ok=True, parents=True)


def get_test_output_dir(config: AppConfig, test_name: str) -> Path:
    return Path(config.output_dir / test_name)


def get_received_output_dir(config: AppConfig, test_name: str) -> Path:
    return Path(get_test_output_dir(config, test_name) / "received")


def get_expected_output_dir(config: AppConfig, test_name: str) -> Path:
    return Path(get_test_output_dir(config, test_name) / "expected")


def get_received_output_file(config: AppConfig, test_name: str, filename: Path) -> Path:
    return Path(get_received_output_dir(config, test_name) /  filename)


def get_received_output_file(config: AppConfig, test_name: str, filename: Path) -> Path:
    return Path(get_expected_output_dir(config, test_name) /  filename)


if __name__ == '__main__':
    snapshot()
