from config import *


def snapshot():
    # read config
    cfg = parse_config_file('config.toml')
    print(cfg)

    # create directories
    setup_directories(cfg)

    # check flags

    # gather tests

    # execute tests

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
