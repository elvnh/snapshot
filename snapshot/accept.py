from directories import *


def accept_output(cfg: AppConfig, test: TestInstance):
    received_file = get_received_output_file(cfg, test)
    expected_file = get_expected_output_file(cfg, test)

    assert received_file.exists()

    expected_file.write_bytes(received_file.read_bytes())
