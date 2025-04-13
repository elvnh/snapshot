from test import *

def setup_directories(cfg: AppConfig):
    cfg.output_dir.mkdir(exist_ok=True)

    for test in cfg.test_configs.items():
        received_dir = get_received_output_dir(cfg, test[1])
        expected_dir = get_expected_output_dir(cfg, test[1])

        received_dir.mkdir(exist_ok=True, parents=True)
        expected_dir.mkdir(exist_ok=True, parents=True)


def get_test_output_dir(config: AppConfig, test_cfg: TestConfig) -> Path:
    return Path(config.output_dir / test_cfg.name)


def get_received_output_dir(config: AppConfig, test_cfg: TestConfig) -> Path:
    return Path(get_test_output_dir(config, test_cfg) / "received")


def get_expected_output_dir(config: AppConfig, test_cfg: TestConfig) -> Path:
    return Path(get_test_output_dir(config, test_cfg) / "expected")

def get_received_output_file(config: AppConfig, test: TestInstance) -> Path:
    return Path(get_received_output_dir(config, test.config) / test.input_file)


def get_expected_output_file(config: AppConfig, test: TestConfig) -> Path:
    return Path(get_expected_output_dir(config, test.config) /  test.input_file)
