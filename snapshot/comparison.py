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


MAX_DIFF_CHARS = 10000

def print_diff(diff_lines: [str], no_truncate: bool):
    green = '\x1b[32m'
    red = '\x1b[31m'
    cyan = '\x1b[36m'
    bold = '\x1b[1m'
    reset = '\x1b[0m'

    print(bold + red + diff_lines[0] + reset, end='')
    print(bold + green + diff_lines[1] + reset, end='')

    char_count = 0
    for line in diff_lines[2:]:
        char_count += len(line)

        if no_truncate:
            truncated = line
        else:
            truncated = line[0:MAX_DIFF_CHARS]

        if not no_truncate and len(truncated) < len(line):
            truncated += f"{reset}...\n(output truncated, run with -T or --no-truncate-diffs if you wish to see all output)\n"

        output = None

        if truncated[0] == '-':
            output = red + truncated + reset
        elif truncated[0] == '+':
            output = green + truncated + reset
        elif truncated[0] == '@':
            output = cyan + truncated + reset
        else:
            output = truncated

        print(output, end='')

        if not no_truncate and char_count > MAX_DIFF_CHARS:
            break

    print()
