import os
import json
from types import SimpleNamespace

import pytest

from golem.test_runner import test_runner
from golem.test_runner.conf import ResultsEnum
from golem.execution_runner import execution_runner
from golem.gui import gui_utils
from golem.core import settings_manager
from golem.core import test as test_module


SUCCESS_MESSAGE = 'Test Result: SUCCESS'
CODE_ERROR_MESSAGE = 'Test Result: CODE ERROR'
FAILURE_MESSAGE = 'Test Result: FAILURE'
ERROR_MESSAGE = 'Test Result: ERROR'
SKIPPED_MESSAGE = 'Test Result: SKIPPED'


def _define_browsers_mock(selected_browsers):
    default_browsers = gui_utils.get_supported_browsers_suggestions()
    return execution_runner.define_browsers(selected_browsers, [], default_browsers)


def _mock_report_directory(testdir, project, test_name):
    path = os.path.join(testdir, 'projects', project, 'reports', 'single_tests',
                        test_name, '00001')
    os.makedirs(path)
    return path


def _read_report_json(report_directory):
    report_path = os.path.join(report_directory, 'report.json')
    with open(report_path) as f:
        return json.load(f)


@pytest.fixture(scope="function")
def runfix(project_class, test_utils):
    """A fixture that
      Uses a project fix with class scope,
      Creates a random test
      Creates a report directory for a future execution
      Gets the settings and browser values required to run test
      Can run the test provided the test code
      Can read the json report
    """
    testdir, project = project_class.activate()
    test_name = test_utils.create_random_test(project)
    report_directory = _mock_report_directory(testdir, project, test_name)
    settings = settings_manager.get_project_settings(project)
    browser = _define_browsers_mock(['chrome'])[0]
    env_name = None

    def run_test(code, test_data={}, secrets={}, from_suite=False):
        test_module.edit_test_code(project, test_name, code, [])
        test_runner.run_test(testdir, project, test_name, test_data, secrets, browser,
                             env_name, settings, report_directory, from_suite=from_suite)

    def read_report():
        return _read_report_json(report_directory)

    fix = SimpleNamespace(testdir=testdir, project=project, test_name=test_name,
                          report_directory=report_directory, settings=settings,
                          browser=browser, run_test=run_test, read_report=read_report)
    return fix


class TestGetSetName:

    def test___get_set_name(self):
        test_data = {
            'username': 'user01',
            'set_name': 'set01'
        }
        assert test_runner._get_set_name(test_data) == 'set01'

    def test___get_set_name__no_set_name_present(self):
        test_data = {
            'username': 'user01',
            'password': 'password01'
        }
        actual_value = test_runner._get_set_name(test_data)
        # Python 3.4 result not in order TODO
        assert actual_value in ['user01', 'password01']

    def test___get_set_name__empty_data(self):
        test_data = {}
        assert test_runner._get_set_name(test_data) == ''


# TestRunner decision table
#
# CE : code error
# S  : success
# F  : failure
# E  : error
#
#                        *   *   *   *   *   *   *       *       *   *       *       *       *       *   *   *   *           *       *   *   *                   *           *
#                        A0  A1  A2  A3  A4  A5  A6  A7  A8  A9  B0  B1  B2  B3  B4  B5  B6  B7  B8  B9  C0  C1  C2  C3  C4  C5  C6  C7  C8  C9  D0  D1  D2  D3  D4  D5  D6  D7  D8  D9  E0  E1  E2  E3  E4  E5
# import error test      Y   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N
# import error page      N   Y   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N
# soft error in setup    .   .   N   N   Y   N   N   N   N   N   N   Y   N   N   N   N   N   Y   Y   Y   Y   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   Y   Y   N   N   N   N   N   N   N   N
# exception in setup     .   .   N   .   .   .   .   .   .   .   Y   Y   Y   Y   Y   Y   Y   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N
# failure in setup       .   .   N   Y   Y   Y   Y   Y   Y   Y   .   .   .   .   .   .   .   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N   N
# soft error in test     .   .   N   .   .   .   .   .   .   .   .   .   .   .   .   .   .   N   N   N   N   N   Y   N   N   N   N   N   N   Y   N   N   N   N   N   Y   Y   Y   Y   Y   Y   N   N   N   N   N
# exception in test      .   .   N   .   .   .   .   .   .   .   .   .   .   .   .   .   .   N   N   N   N   .   .   .   .   .   .   .   Y   Y   Y   Y   Y   Y   Y   N   N   N   N   N   N   N   N   N   N   N
# failure in test        .   .   N   .   .   .   .   .   .   .   .   .   .   .   .   .   .   N   N   N   N   Y   Y   Y   Y   Y   Y   Y   .   .   .   .   .   .   .   N   N   N   N   N   N   N   N   N   N   N
# soft error in teardown .   .   N   N   N   Y   N   Y   N   Y   N   N   Y   N   Y   N   Y   N   Y   N   N   N   N   Y   Y   N   Y   N   N   N   Y   Y   N   Y   N   N   N   Y   Y   N   N   Y   N   Y   N   Y
# exception in teardown  .   .   N   N   N   N   Y   Y   .   .   N   N   N   Y   Y   .   .   N   N   Y   .   N   N   N   Y   Y   .   .   N   N   N   Y   Y   .   .   N   N   N   N   Y   .   N   Y   Y   .   .
# failure in teardown    .   .   N   N   N   N   .   .   Y   Y   N   N   N   .   .   Y   Y   N   N   .   Y   N   N   N   .   .   Y   Y   N   N   N   .   .   Y   Y   N   N   N   N   .   Y   N   .   .   Y   Y
#
# result                 CE  CE  S   F   F   F   F   F   F   F   CE  CE  CE  CE  CE  CE  CE  E   E   CE  F   F   F   F   F   F   F   F   CE  CE  CE  CE  CE  CE  CE  E   E   E   E   E   E   E   CE  CE  F   F
# setup is run           N   N   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y
# test is run            N   N   Y   N   N   N   N   N   N   N   N   N   N   N   N   N   N   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y
# teardown is run        N   N   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y


class TestRunTest:

    # A0
    def test_run_test__import_error_on_test(self, runfix, caplog):
        """The test fails with 'code error' when it has a syntax error
        Test result is code error"""
        code = """
description = 'some description'

# missing colon
def test(data)
step('this step wont be run')
"""
        runfix.run_test(code)
        # verify console logs
        records = caplog.records
        assert records[0].message == 'Test execution started: {}'.format(runfix.test_name)
        assert records[1].message == 'Browser: chrome'
        assert records[2].levelname == 'ERROR'
        error_contains = 'def test(data)\n                 ^\nSyntaxError: invalid syntax'
        assert error_contains in records[2].message
        assert records[3].message == CODE_ERROR_MESSAGE
        # verify report.json
        report = runfix.read_report()
        assert report['browser'] == 'chrome'
        assert report['description'] is None  # description could not be read
        assert report['environment'] == ''
        assert len(report['errors']) == 1
        assert report['errors'][0]['message'] == 'SyntaxError: invalid syntax'
        assert error_contains in report['errors'][0]['description']
        assert report['result'] == ResultsEnum.CODE_ERROR
        assert report['set_name'] == ''
        assert report['steps'] == []
        assert report['test_case'] == runfix.test_name
        assert report['test_data'] == {}

    # A1
    def test_run_test__import_error_page(self, runfix, caplog, test_utils):
        """The test fails with 'code error' when an imported page has a syntax error"""
        page_code = """
element1 = ('id', 'someId'
element2 = ('css', '.oh.no')
"""
        page_name = test_utils.create_random_page(runfix.project, code=page_code)
        code = """
pages = ['{}']
def setup(data):
    step('this step wont be run')
def test(data):
    step('this step wont be run')
def teardown(data):
    step('this step wont be run')
""".format(page_name)
        runfix.run_test(code)
        # verify console logs
        records = caplog.records
        assert records[0].message == 'Test execution started: {}'.format(runfix.test_name)
        assert records[1].message == 'Browser: chrome'
        assert records[2].levelname == 'ERROR'
        error_contains_one = "element2 = ('css', '.oh.no')\n           ^\n" \
                             "SyntaxError: invalid syntax"
        error_contains_two = "element2 = ('css', '.oh.no')\n    ^\n" \
                             "SyntaxError: invalid syntax"  # Python 3.8 version
        assert error_contains_one in records[2].message or \
               error_contains_two in records[2].message
        assert records[3].message == CODE_ERROR_MESSAGE
        # verify report.json
        report = runfix.read_report()
        assert report['browser'] == 'chrome'
        assert report['description'] is None  # description could not be read
        assert report['environment'] == ''
        assert len(report['errors']) == 1
        assert 'SyntaxError: invalid syntax' in report['errors'][0]['message']
        assert error_contains_one in report['errors'][0]['description'] or \
               error_contains_two in report['errors'][0]['description']
        assert report['result'] == ResultsEnum.CODE_ERROR
        assert report['set_name'] == ''
        assert report['steps'] == []
        assert report['test_case'] == runfix.test_name
        assert report['test_data'] == {}
        assert 'test_elapsed_time' in report
        assert 'test_timestamp' in report
        assert len(report.keys()) == 11

    # A2
    def test_run_test__success(self, runfix, caplog):
        """Test runs successfully"""
        code = """
description = 'some description'

def setup(data):
    step('setup step')

def test(data):
    step('test step')

def teardown(data):
    step('teardown step')
"""
        runfix.run_test(code)
        # verify console logs
        records = caplog.records
        assert records[0].message == 'Test execution started: {}'.format(runfix.test_name)
        assert records[1].message == 'Browser: chrome'
        assert records[2].message == 'setup step'
        assert records[3].message == 'test step'
        assert records[4].message == 'teardown step'
        assert records[5].message == SUCCESS_MESSAGE
        # verify report.json
        report = runfix.read_report()
        assert report['browser'] == 'chrome'
        assert report['description'] == 'some description'
        assert report['environment'] == ''
        assert report['errors'] == []
        assert report['result'] == ResultsEnum.SUCCESS
        assert report['set_name'] == ''
        assert report['steps'] == [
            {'message': 'setup step', 'screenshot': None, 'error': None},
            {'message': 'test step', 'screenshot': None, 'error': None},
            {'message': 'teardown step', 'screenshot': None, 'error': None},
        ]
        assert report['test_case'] == runfix.test_name
        assert report['test_data'] == {}
        assert 'test_elapsed_time' in report
        assert 'test_timestamp' in report
        assert len(report.keys()) == 11

    # A2
    @pytest.mark.slow
    def test_run_test__success_with_data(self, runfix, caplog):
        """Test runs successfully with test data"""
        code = """
description = 'some description'
    
def setup(data):
    step('setup step')

def test(data):
    step('test step')

def teardown(data):
    step('teardown step')
"""
        test_data = dict(username='username1', password='password1')
        secrets = dict(very='secret')
        runfix.run_test(code, test_data=test_data, secrets=secrets)
        # verify console logs
        records = caplog.records
        assert records[0].message == 'Test execution started: {}'.format(runfix.test_name)
        assert records[1].message == 'Browser: chrome'
        # Python 3.4 results not in order TODO
        value_a = 'Using data:\n    username: username1\n    password: password1'
        value_b = 'Using data:\n    password: password1\n    username: username1'
        assert records[2].message in [value_a, value_b]
        assert records[3].message == 'setup step'
        assert records[4].message == 'test step'
        assert records[5].message == 'teardown step'
        assert records[6].message == SUCCESS_MESSAGE
        # verify report.json
        report = runfix.read_report()
        assert report['browser'] == 'chrome'
        assert report['description'] == 'some description'
        assert report['environment'] == ''
        assert report['errors'] == []
        assert report['result'] == ResultsEnum.SUCCESS
        # Python 3.4 TODO
        assert report['set_name'] in ['username1', 'password1']
        assert report['steps'] == [
            {'message': 'setup step', 'screenshot': None, 'error': None},
            {'message': 'test step', 'screenshot': None, 'error': None},
            {'message': 'teardown step', 'screenshot': None, 'error': None},
        ]
        assert report['test_case'] == runfix.test_name
        assert report['test_data'] == {'username': "'username1'", 'password': "'password1'"}
        assert 'test_elapsed_time' in report
        assert 'test_timestamp' in report
        assert len(report.keys()) == 11

    # A3
    def test_run_test__AssertionError_in_setup(self, runfix, caplog):
        """The test ends with 'failure' when the setup function throws AssertionError.
        Test is not run
        Teardown is run
        """
        code = """
description = 'desc'

def setup(data):
    fail('setup step fail')

def test(data):
    step('test step')

def teardown(data):
    step('teardown step')
"""
        runfix.run_test(code)
        # verify console logs
        records = caplog.records
        assert records[0].message == 'Test execution started: {}'.format(runfix.test_name)
        assert records[1].message == 'Browser: chrome'
        assert records[2].levelname == 'ERROR'
        assert 'setup step fail' in records[2].message
        assert 'AssertionError: setup step fail' in records[2].message
        assert records[3].message == 'teardown step'
        assert records[4].message == FAILURE_MESSAGE
        # verify report.json
        report = runfix.read_report()
        assert report['description'] == 'desc'
        assert len(report['errors']) == 1
        assert 'setup step fail' in report['errors'][0]['message']
        assert report['result'] == ResultsEnum.FAILURE
        assert report['steps'][0]['message'] == 'Failure'
        assert 'AssertionError: setup step fail' in report['steps'][0]['error']['description']
        assert report['steps'][1]['message'] == 'teardown step'

    # A4
    @pytest.mark.slow
    def test_run_test__failure_and_error_in_setup(self, runfix, caplog):
        """The test ends with 'failure' when the setup function throws AssertionError,
        even when there's an error in setup
        Test is not run
        Teardown is run
        """
        code = """
description = 'desc'

def setup(data):
    error('error in setup')
    fail('setup step fail')

def test(data):
    step('test step')

def teardown(data):
    step('teardown step')
"""
        runfix.run_test(code)
        # verify console logs
        records = caplog.records
        assert records[5].message == FAILURE_MESSAGE
        # verify report.json
        report = runfix.read_report()
        assert len(report['errors']) == 2
        assert report['result'] == ResultsEnum.FAILURE
        assert len(report['steps']) == 3
        assert report['errors'][0]['message'] == 'error in setup'
        assert report['errors'][1]['message'] == 'AssertionError: setup step fail'

    # A5
    def test_run_test__failure_in_setup_error_in_teardown(self, runfix, caplog):
        """Setup throws AssertionError
        Teardown throws error
        Test ends with 'failure'
        test() is not run
        """
        code = """
description = 'desc'

def setup(data):
    fail('setup step fail')

def test(data):
    step('test step')

def teardown(data):
    step('teardown step')
    error('error in teardown')
"""
        runfix.run_test(code)
        # verify console logs
        records = caplog.records
        assert records[5].message == FAILURE_MESSAGE
        # verify report.json
        report = runfix.read_report()
        assert len(report['errors']) == 2
        assert report['result'] == ResultsEnum.FAILURE
        assert len(report['steps']) == 3
        assert report['errors'][0]['message'] == 'AssertionError: setup step fail'
        assert report['errors'][1]['message'] == 'error in teardown'

    # A6
    @pytest.mark.slow
    def test_run_test__failure_in_setup_exception_in_teardown(self, runfix, caplog):
        """Setup throws AssertionError
        Teardown throws AssertionError
        Test ends with 'failure'
        test() is not run
        """
        code = """
description = 'desc'

def setup(data):
    fail('setup step fail')

def test(data):
    step('test step')

def teardown(data):
    step('teardown step')
    foo = bar
"""
        runfix.run_test(code)
        # verify console logs
        records = caplog.records
        assert records[5].message == FAILURE_MESSAGE
        # verify report.json
        report = runfix.read_report()
        assert len(report['errors']) == 2
        assert report['result'] == ResultsEnum.FAILURE
        assert len(report['steps']) == 3
        assert report['errors'][0]['message'] == 'AssertionError: setup step fail'
        assert report['errors'][1]['message'] == "NameError: name 'bar' is not defined"

    # A8
    @pytest.mark.slow
    def test_run_test__failure_in_setup_failure_in_teardown(self, runfix, caplog):
        """Setup throws AssertionError
        Teardown throws exception
        Test ends with 'failure'
        test() is not run
        """
        code = """
description = 'desc'

def setup(data):
    fail('setup step fail')

def test(data):
    step('test step')

def teardown(data):
    fail('failure in teardown')
"""
        runfix.run_test(code)
        # verify console logs
        records = caplog.records
        assert records[4].message == FAILURE_MESSAGE
        # verify report.json
        report = runfix.read_report()
        assert len(report['errors']) == 2
        assert report['result'] == ResultsEnum.FAILURE
        assert len(report['steps']) == 2
        assert report['errors'][0]['message'] == 'AssertionError: setup step fail'
        assert report['errors'][1]['message'] == 'AssertionError: failure in teardown'

    # B0
    def test_run_test__exception_in_setup(self, runfix, caplog):
        """Setup throws exception
        Test ends with 'code error'
        test() is not run
        teardown() is run
        """
        code = """
description = 'desc'

def setup(data):
    foo = bar

def test(data):
    step('test step')

def teardown(data):
    step('teardown step')
"""
        runfix.run_test(code)
        # verify console logs
        records = caplog.records
        assert records[4].message == CODE_ERROR_MESSAGE
        # verify report.json
        report = runfix.read_report()
        assert len(report['errors']) == 1
        assert report['result'] == ResultsEnum.CODE_ERROR
        assert len(report['steps']) == 2
        assert report['errors'][0]['message'] == "NameError: name 'bar' is not defined"

    # B1
    def test_run_test__exception_and_error_in_setup(self, runfix, caplog):
        """Setup has error and throws exception
        Test ends with 'code error'
        test() is not run
        teardown() is run
        """
        code = """
description = 'desc'

def setup(data):
    error('setup error')
    foo = bar

def test(data):
    step('test step')

def teardown(data):
    step('teardown step')
"""
        runfix.run_test(code)
        # verify console logs
        records = caplog.records
        assert records[5].message == CODE_ERROR_MESSAGE
        # verify report.json
        report = runfix.read_report()
        assert report['result'] == ResultsEnum.CODE_ERROR
        assert len(report['steps']) == 3
        assert len(report['errors']) == 2
        assert report['errors'][0]['message'] == 'setup error'
        assert report['errors'][1]['message'] == "NameError: name 'bar' is not defined"

    # B3
    def test_run_test__exception_in_setup_exception_in_teardown(self, runfix, caplog):
        """Setup throws exception
        Teardown throws exception
        Test ends with 'code error'
        test() is not run
        """
        code = """
description = 'desc'

def setup(data):
    foo = bar

def test(data):
    step('test step')

def teardown(data):
    foo = baz
"""
        runfix.run_test(code)
        # verify console logs
        records = caplog.records
        assert records[4].message == CODE_ERROR_MESSAGE
        # verify report.json
        report = runfix.read_report()
        assert report['result'] == ResultsEnum.CODE_ERROR
        assert len(report['steps']) == 2
        assert len(report['errors']) == 2
        assert report['errors'][0]['message'] == "NameError: name 'bar' is not defined"
        assert report['errors'][1]['message'] == "NameError: name 'baz' is not defined"

    # B5
    def test_run_test__exception_in_setup_failure_in_teardown(self, runfix, caplog):
        """Setup throws exception
        Teardown throws AssertionError
        Test ends with 'code error'
        test() is not run
        """
        code = """
description = 'desc'

def setup(data):
    foo = bar

def test(data):
    step('test step')

def teardown(data):
    fail('teardown failure')
"""
        runfix.run_test(code)
        # verify console logs
        records = caplog.records
        assert records[4].message == CODE_ERROR_MESSAGE
        # verify report.json
        report = runfix.read_report()
        assert report['result'] == ResultsEnum.CODE_ERROR
        assert len(report['steps']) == 2
        assert len(report['errors']) == 2
        assert report['errors'][0]['message'] == "NameError: name 'bar' is not defined"
        assert report['errors'][1]['message'] == 'AssertionError: teardown failure'

    # B7
    def test_run_test__error_in_setup(self, runfix, caplog):
        """Setup has error
        test() is run
        teardown() is run
        """
        code = """
description = 'desc'

def setup(data):
    error('setup error')

def test(data):
    step('test step')

def teardown(data):
    step('teardown step')
"""
        runfix.run_test(code)
        # verify console logs
        records = caplog.records
        assert records[5].message == ERROR_MESSAGE
        # verify report.json
        report = runfix.read_report()
        assert report['result'] == ResultsEnum.ERROR
        assert len(report['steps']) == 3
        assert len(report['errors']) == 1
        assert report['errors'][0]['message'] == "setup error"

    # B9
    def test_run_test__error_in_setup_exception_in_teardown(self, runfix, caplog):
        """Setup has error
        Teardown throws exception
        test() is run
        """
        code = """
description = 'desc'

def setup(data):
    error('setup error')

def test(data):
    step('test step')

def teardown(data):
    foo = bar
"""
        runfix.run_test(code)
        # verify console logs
        records = caplog.records
        assert records[5].message == CODE_ERROR_MESSAGE
        # verify report.json
        report = runfix.read_report()
        assert report['result'] == ResultsEnum.CODE_ERROR
        assert len(report['steps']) == 3
        assert len(report['errors']) == 2
        assert report['errors'][0]['message'] == 'setup error'
        assert report['errors'][1]['message'] == "NameError: name 'bar' is not defined"

    # C0
    def test_run_test__error_in_setup_failure_in_teardown(self, runfix, caplog):
        """Setup has error
        Teardown throws AssertionError
        test() is run
        """
        code = """
description = 'desc'

def setup(data):
    error('setup error')

def test(data):
    step('test step')

def teardown(data):
    fail('teardown fail')
"""
        runfix.run_test(code)
        # verify console logs
        records = caplog.records
        assert records[5].message == FAILURE_MESSAGE
        # verify report.json
        report = runfix.read_report()
        assert report['result'] == ResultsEnum.FAILURE
        assert len(report['steps']) == 3
        assert len(report['errors']) == 2
        assert report['errors'][0]['message'] == 'setup error'
        assert report['errors'][1]['message'] == 'AssertionError: teardown fail'

    # C1
    def test_run_test__failure_in_test(self, runfix, caplog):
        """test() throws AssertionError
        teardown() is run
        """
        code = """
description = 'desc'

def setup(data):
    step('setup step')

def test(data):
    step('test step')
    fail('test fail')

def teardown(data):
    step('teardown step')
"""
        runfix.run_test(code)
        # verify console logs
        records = caplog.records
        assert records[6].message == FAILURE_MESSAGE
        # verify report.json
        report = runfix.read_report()
        assert report['result'] == ResultsEnum.FAILURE
        assert len(report['steps']) == 4
        assert len(report['errors']) == 1
        assert report['errors'][0]['message'] == 'AssertionError: test fail'

    # C2
    def test_run_test__failure_and_error_in_test(self, runfix, caplog):
        """test() has error and throws AssertionError
        teardown() is run
        """
        code = """
description = 'desc'

def setup(data):
    step('setup step')

def test(data):
    error('test error')
    fail('test fail')

def teardown(data):
    step('teardown step')
"""
        runfix.run_test(code)
        # verify console logs
        records = caplog.records
        assert records[6].message == FAILURE_MESSAGE
        # verify report.json
        report = runfix.read_report()
        assert report['result'] == ResultsEnum.FAILURE
        assert len(report['steps']) == 4
        assert len(report['errors']) == 2
        assert report['errors'][0]['message'] == 'test error'
        assert report['errors'][1]['message'] == 'AssertionError: test fail'

    # C5
    def test_run_test__failure_in_test_exception_in_teardown(self, runfix, caplog):
        """test() throws AssertionError
        teardown() throws exception
        """
        code = """
description = 'desc'

def setup(data):
    step('setup step')

def test(data):
    fail('test fail')

def teardown(data):
    foo = bar
"""
        runfix.run_test(code)
        # verify console logs
        records = caplog.records
        assert records[5].message == FAILURE_MESSAGE
        # verify report.json
        report = runfix.read_report()
        assert report['result'] == ResultsEnum.FAILURE
        assert len(report['steps']) == 3
        assert len(report['errors']) == 2
        assert report['errors'][0]['message'] == 'AssertionError: test fail'
        assert report['errors'][1]['message'] == "NameError: name 'bar' is not defined"

    # C7
    def test_run_test__failure_in_test_failure_in_teardown(self, runfix, caplog):
        """test() throws AssertionError
        teardown() throws AssertionError
        """
        code = """
description = 'desc'

def setup(data):
    step('setup step')

def test(data):
    fail('test fail')

def teardown(data):
    fail('teardown fail')
"""
        runfix.run_test(code)
        # verify console logs
        records = caplog.records
        assert records[5].message == FAILURE_MESSAGE
        # verify report.json
        report = runfix.read_report()
        assert report['result'] == ResultsEnum.FAILURE
        assert len(report['steps']) == 3
        assert len(report['errors']) == 2
        assert report['errors'][0]['message'] == 'AssertionError: test fail'
        assert report['errors'][1]['message'] == 'AssertionError: teardown fail'

    # C8
    def test_run_test__exception_in_test(self, runfix, caplog):
        """test() throws exception"""
        code = """
description = 'desc'

def setup(data):
    step('setup step')

def test(data):
    foo = bar

def teardown(data):
    step('teardown step')
"""
        runfix.run_test(code)
        # verify console logs
        records = caplog.records
        assert records[5].message == CODE_ERROR_MESSAGE
        # verify report.json
        report = runfix.read_report()
        assert report['result'] == ResultsEnum.CODE_ERROR
        assert len(report['steps']) == 3
        assert len(report['errors']) == 1
        assert report['errors'][0]['message'] == "NameError: name 'bar' is not defined"

    # C9
    def test_run_test__error_and_exception_in_test(self, runfix, caplog):
        """test() throws error and AssertionError
        teardown()
        """
        code = """
description = 'desc'

def setup(data):
    step('setup step')

def test(data):
    error('error in test')
    foo = bar

def teardown(data):
    step('teardown step')
"""
        runfix.run_test(code)
        # verify console logs
        records = caplog.records
        assert records[6].message == CODE_ERROR_MESSAGE
        # verify report.json
        report = runfix.read_report()
        assert report['result'] == ResultsEnum.CODE_ERROR
        assert len(report['steps']) == 4
        assert len(report['errors']) == 2
        assert report['errors'][0]['message'] == 'error in test'
        assert report['errors'][1]['message'] == "NameError: name 'bar' is not defined"

    # D4
    def test_run_test__exception_in_test_failure_in_teardown(self, runfix, caplog):
        """test() throws exception
        teardown() throws AssertionError
        """
        code = """
description = 'desc'

def setup(data):
    step('setup step')

def test(data):
    foo = bar

def teardown(data):
    fail('teardown fail')
"""
        runfix.run_test(code)
        # verify console logs
        records = caplog.records
        assert records[5].message == CODE_ERROR_MESSAGE
        # verify report.json
        report = runfix.read_report()
        assert report['result'] == ResultsEnum.CODE_ERROR
        assert len(report['steps']) == 3
        assert len(report['errors']) == 2
        assert report['errors'][0]['message'] == "NameError: name 'bar' is not defined"
        assert report['errors'][1]['message'] == 'AssertionError: teardown fail'

    # D7
    def test_run_test__error_in_setup_test_and_teardown(self, runfix, caplog):
        """setup(), test() and teardown() have errors
        """
        code = """
description = 'desc'

def setup(data):
    error('setup error')

def test(data):
    error('test error')

def teardown(data):
    error('teardown error')
"""
        runfix.run_test(code)
        # verify console logs
        records = caplog.records
        assert records[5].message == ERROR_MESSAGE
        # verify report.json
        report = runfix.read_report()
        assert report['result'] == ResultsEnum.ERROR
        assert len(report['steps']) == 3
        assert len(report['errors']) == 3
        assert report['errors'][0]['message'] == 'setup error'
        assert report['errors'][1]['message'] == 'test error'
        assert report['errors'][2]['message'] == 'teardown error'

    # TestRunner decision table: Skip is True
    #
    # CE : code error
    # S  : success
    # F  : failure
    # SK : skip
    #
    #                        S0  S1  S2
    # Skip is True           Y   Y   Y
    # Import error test      N   N   Y
    # Import error page      N   N   .
    # Run from suite         N   Y   .
    #
    # result                 S   SK  CE
    # setup is run           Y   N   N
    # test is run            Y   N   N
    # teardown is run        Y   N   N

    # S0
    def test_run_test__skip_true__not_from_suite(self, runfix, caplog):
        code = ('skip = True\n'
                'def setup(data):\n'
                '    step("setup")\n'
                'def test(data):\n'
                '    step("test")\n'
                'def teardown(data):\n'
                '    step("teardown")')
        runfix.run_test(code, from_suite=False)
        # verify console logs
        records = caplog.records
        assert records[2].message == 'setup'
        assert records[3].message == 'test'
        assert records[4].message == 'teardown'
        assert records[5].message == SUCCESS_MESSAGE
        # verify report.json
        report = runfix.read_report()
        assert report['result'] == ResultsEnum.SUCCESS

    # S1
    def test_run_test__skip_true__from_suite(self, runfix, caplog):
        code = ('skip = True\n'
                'def setup(data):\n'
                '    step("setup")\n'
                'def test(data):\n'
                '    step("test")\n'
                'def teardown(data):\n'
                '    step("teardown")')
        runfix.run_test(code, from_suite=True)
        # verify console logs
        records = caplog.records
        assert records[2].message == 'Skip'
        assert records[3].message == SKIPPED_MESSAGE
        # verify report.json
        report = runfix.read_report()
        assert report['result'] == ResultsEnum.SKIPPED

    # S1
    def test_run_test__skip_true__syntax_error(self, runfix, caplog):
        """when test with skip=True has an error on import the test
        ends with code error
        """
        code = ('skip = True\n'
                'def test(data)\n'
                '    step("test")\n')
        runfix.run_test(code, from_suite=True)
        # verify console logs
        records = caplog.records
        assert records[2].levelname == 'ERROR'
        assert records[3].message == CODE_ERROR_MESSAGE
        # verify report.json
        report = runfix.read_report()
        assert len(report['errors']) == 1
        assert report['errors'][0]['message'] == 'SyntaxError: invalid syntax'
        assert report['result'] == ResultsEnum.CODE_ERROR


class TestTestRunnerSetExecutionModuleValues:

    def test_set_execution_module_runner_values(self, project_class, test_utils):
        testdir, project = project_class.activate()
        test_name = test_utils.create_random_test(project)
        test = test_module.Test(project, test_name)
        report_directory = _mock_report_directory(testdir, project, test_name)
        settings = settings_manager.get_project_settings(project)
        browser = _define_browsers_mock(['chrome'])[0]
        test_data = {}
        secrets = {}
        env_name = 'foo'
        runner = test_runner.TestRunner(testdir, project, test_name, test_data, secrets,
                                        browser, env_name, settings, report_directory)
        runner._set_execution_module_values()
        from golem import execution
        attrs = [x for x in dir(execution) if not x.startswith('_')]
        assert len(attrs) == 20
        assert execution.browser is None
        assert execution.browser_definition == browser
        assert execution.browsers == {}
        assert execution.steps == []
        assert execution.data == {}
        assert execution.secrets == {}
        assert execution.description is None
        assert execution.errors == []
        assert execution.settings == settings
        assert execution.test_name == test_name
        assert execution.test_dirname == test.dirname
        assert execution.test_path == test.path
        assert execution.project_name == project
        assert execution.project_path == test.project.path
        assert execution.testdir == testdir
        assert execution.report_directory == report_directory
        assert execution.logger is None
        assert execution.timers == {}
        assert execution.tags == []
        assert execution.environment == env_name
