from collections import OrderedDict

import colorama

from golem.test_runner.conf import ResultsEnum


def _get_symbol_and_color(result):
    if result == ResultsEnum.SUCCESS:
        symbol = '.'  # '✓'
        color = colorama.Fore.GREEN
    elif result in [ResultsEnum.CODE_ERROR, ResultsEnum.ERROR]:
        symbol = 'E'
        color = colorama.Fore.RED
    elif result == ResultsEnum.FAILURE:
        symbol = 'F'
        color = colorama.Fore.RED
    else:
        symbol = '?'
        color = colorama.Fore.YELLOW
    return symbol, color


def _print_test_file_section(test_file_tests):
    print('------------------------------------------------------------------')
    first_test = test_file_tests[0]
    # if the test file only has one test, the test name is 'test' and the result is
    # success then the test file section is simplified to a single line
    if len(test_file_tests) == 1 and first_test['test'] == 'test' and \
            first_test['result'] == ResultsEnum.SUCCESS:
        symbol, color = _get_symbol_and_color(first_test['result'])
        print(first_test['test_file'], first_test['set_name'],
              color + symbol + colorama.Fore.RESET)
    else:
        print(first_test['test_file'], first_test['set_name'])
        not_success = []
        for test in test_file_tests:
            if test['result'] != ResultsEnum.SUCCESS:
                not_success.append(test)
            symbol, color = _get_symbol_and_color(test['result'])
            print('  ' + color + symbol + colorama.Fore.RESET + ' ' + test['test'])
        # list each test in this test file that was not a success
        for i, test in enumerate(not_success):
            print()
            print('{}) {}'.format(i + 1, test['test']))
            for error in test['errors']:
                print(error['message'])
                if error['description']:
                    print(error['description'])


def report_to_cli(report):
    # group each test by test_file.set_name
    unique_test_files = {}
    for test in report['tests']:
        test_file_id = '{}.{}'.format(test['test_file'], test['set_name'])
        if test_file_id not in unique_test_files:
            unique_test_files[test_file_id] = []
        unique_test_files[test_file_id].append(test)
    print()
    print('Result:')
    for test_file in unique_test_files:
        _print_test_file_section(unique_test_files[test_file])


def print_totals(report):
    if report['total_tests'] > 0:
        result_string = ''
        for result, number in OrderedDict(report['totals_by_result']).items():
            result_string += ' {} {},'.format(number, result)
        elapsed_time = report['net_elapsed_time']
        if elapsed_time > 60:
            in_elapsed_time = 'in {} minutes'.format(round(elapsed_time / 60, 2))
        else:
            in_elapsed_time = 'in {} seconds'.format(elapsed_time)
        output = 'Total: {} tests,{} {}'.format(report['total_tests'], result_string[:-1], in_elapsed_time)
        print()
        print(output)
