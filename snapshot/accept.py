from directories import *


def accept_output(cfg: AppConfig, test_cfg: TestConfig, filename: Path):
    received_file = get_received_output_file(cfg, test_cfg.name, filename)
    expected_file = get_expected_output_file(cfg, test_cfg.name, filename)

    assert received_file.exists()

    expected_file.write_bytes(received_file.read_bytes())
