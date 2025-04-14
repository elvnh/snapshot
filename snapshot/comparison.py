import difflib

from test import *
from directories import *


def compare_test_output_files(config: AppConfig, test_instance: TestInstance) -> [str]:
    input_file = test_instance.input_file
    test_name = test_instance.config.name

    received_file = get_received_output_file(config, test_instance)
    expected_file = get_expected_output_file(config, test_instance)


    if not received_file.exists() or not expected_file.exists():
        return None # No comparison could be made
    else:
        with open(received_file, 'r') as recv, open(expected_file, 'r') as exp:
            diff = list(difflib.unified_diff(exp.readlines(), recv.readlines(), lineterm='\n'))

            if diff:
                diff[0] = f"{diff[0].rstrip()} {str(expected_file)}\n"
                diff[1] = f"{diff[1].rstrip()} {str(received_file)}\n"

                return diff
            else:
                return []


def print_diff(diff_lines: [str]):
    green = '\x1b[32m'
    red = '\x1b[31m'
    cyan = '\x1b[36m'
    bold = '\x1b[1m'
    reset = '\x1b[0m'

    print(bold + red + diff_lines[0] + reset, end='')
    print(bold + green + diff_lines[1] + reset, end='')

    for line in diff_lines[2:]:
        output = None

        if line[0] == '-':
            output = red + line + reset
        elif line[0] == '+':
            output = green + line + reset
        elif line[0] == '@':
            output = cyan + line + reset
        else:
            output = line

        print(output, end='')

    print()
