import os
import json

from golem.test_runner import test_runner
from golem.test_runner.execution_runner import define_browsers
from golem.gui import gui_utils
from golem.core import settings_manager


def _define_browsers_mock(selected_browsers):
    default_browsers = gui_utils.get_supported_browsers_suggestions()
    return define_browsers(selected_browsers, [], default_browsers)


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

    def _create_test(self, testdir, project, name, content):
        path = os.path.join(testdir, 'projects', project, 'tests', name + '.py')
        with open(path, 'w+') as f:
            f.write(content)

    def _create_page(self, testdir, project, name, content):
        path = os.path.join(testdir, 'projects', project, 'pages', name + '.py')
        with open(path, 'w+') as f:
            f.write(content)

    def _mock_report_directory(self, testdir, project, test_name):
        path = os.path.join(testdir, 'projects', project, 'reports', 'single_tests',
                            test_name, '00001')
        os.makedirs(path)
        return path

    def _read_report_json(self, report_directory):
        report_path = os.path.join(report_directory, 'report.json')
        with open(report_path) as f:
            return json.load(f)

    # A2
    def test_run_test__success(self, project_function_clean, caplog, test_utils):
        """Test runs successfully"""
        testdir = project_function_clean.testdir
        project = project_function_clean.name
        test_name = test_utils.random_numeric_string(10)
        content = """
description = 'some description'

def setup(data):
    step('setup step')

def test(data):
    step('test step')

def teardown(data):
    step('teardown step')
"""
        self._create_test(testdir, project, test_name, content)
        report_directory = self._mock_report_directory(testdir, project, test_name)
        settings = settings_manager.get_project_settings(testdir, project)
        browser = _define_browsers_mock(['chrome'])[0]
        # run test
        test_runner.run_test(workspace=testdir, project=project, test_name=test_name,
                             test_data={}, secrets={}, browser=browser, settings=settings,
                             report_directory=report_directory)
        # verify console logs
        records = caplog.records
        assert records[0].message == 'Test execution started: {}'.format(test_name)
        assert records[1].message == 'Browser: chrome'
        assert records[2].message == 'setup step'
        assert records[3].message == 'test step'
        assert records[4].message == 'teardown step'
        assert records[5].message == 'Test Result: SUCCESS'
        # verify report.json
        report = self._read_report_json(report_directory)
        assert report['browser'] == 'chrome'
        assert report['description'] == 'some description'
        assert report['environment'] == ''
        assert report['errors'] == []
        assert report['result'] == 'success'
        assert report['set_name'] == ''
        assert report['steps'] == [
            {'message': 'setup step', 'screenshot': None, 'error': None},
            {'message': 'test step', 'screenshot': None, 'error': None},
            {'message': 'teardown step', 'screenshot': None, 'error': None},
        ]
        assert report['test_case'] == test_name
        assert report['test_data'] == {}
        assert 'test_elapsed_time' in report
        assert 'test_timestamp' in report
        assert len(report.keys()) == 11

    # A2
    def test_run_test__success_with_data(self, project_function_clean, caplog, test_utils):
        """Test runs successfully with test data"""
        testdir = project_function_clean.testdir
        project = project_function_clean.name
        test_name = test_utils.random_numeric_string(10)
        content = """
description = 'some description'
    
def setup(data):
    step('setup step')

def test(data):
    step('test step')

def teardown(data):
    step('teardown step')
"""
        self._create_test(testdir, project, test_name, content)
        report_directory = self._mock_report_directory(testdir, project,
                                                       test_name)
        settings = settings_manager.get_project_settings(testdir, project)
        browser = _define_browsers_mock(['chrome'])[0]
        test_data = dict(username='username1', password='password1')
        secrets = dict(very='secret')
        # run test
        test_runner.run_test(workspace=testdir, project=project, test_name=test_name,
                             test_data=test_data, secrets=secrets, browser=browser, settings=settings,
                             report_directory=report_directory)
        # verify console logs
        records = caplog.records
        assert records[0].message == 'Test execution started: {}'.format(
            test_name)
        assert records[1].message == 'Browser: chrome'
        # Python 3.4 results not in order TODO
        value_a = 'Using data:\n    username: username1\n    password: password1\n'
        value_b = 'Using data:\n    password: password1\n    username: username1\n'
        assert records[2].message in [value_a, value_b]
        assert records[3].message == 'setup step'
        assert records[4].message == 'test step'
        assert records[5].message == 'teardown step'
        assert records[6].message == 'Test Result: SUCCESS'
        # verify report.json
        report = self._read_report_json(report_directory)
        assert report['browser'] == 'chrome'
        assert report['description'] == 'some description'
        assert report['environment'] == ''
        assert report['errors'] == []
        assert report['result'] == 'success'
        # Python 3.4 TODO
        assert report['set_name'] in ['username1', 'password1']
        assert report['steps'] == [
            {'message': 'setup step', 'screenshot': None, 'error': None},
            {'message': 'test step', 'screenshot': None, 'error': None},
            {'message': 'teardown step', 'screenshot': None, 'error': None},
        ]
        assert report['test_case'] == test_name
        assert report['test_data'] == {'username': "'username1'", 'password': "'password1'"}
        assert 'test_elapsed_time' in report
        assert 'test_timestamp' in report
        assert len(report.keys()) == 11

    # A0
    def test_run_test__import_error_on_test(self, project_function_clean, caplog, test_utils):
        """The test fails with 'code error' when it has a syntax error
        Test result is code error"""
        testdir = project_function_clean.testdir
        project = project_function_clean.name
        test_name = test_utils.random_numeric_string(10)
        content = """
description = 'some description'

# missing colon
def test(data)
    step('this step wont be run')
"""
        self._create_test(testdir, project, test_name, content)
        report_directory = self._mock_report_directory(testdir, project,
                                                       test_name)
        settings = settings_manager.get_project_settings(testdir, project)
        browser = _define_browsers_mock(['chrome'])[0]
        test_runner.run_test(workspace=testdir, project=project, test_name=test_name,
                             test_data={}, secrets={}, browser=browser, settings=settings,
                             report_directory=report_directory)
        # verify console logs
        records = caplog.records
        assert records[0].message == 'Test execution started: {}'.format(
            test_name)
        assert records[1].message == 'Browser: chrome'
        assert records[2].levelname == 'ERROR'
        error_contains = 'def test(data)\n                 ^\nSyntaxError: invalid syntax'
        assert error_contains in records[2].message
        assert records[3].message == 'Test Result: CODE ERROR'
        # verify report.json
        report = self._read_report_json(report_directory)
        assert report['browser'] == 'chrome'
        assert report['description'] is None  # description could not be read
        assert report['environment'] == ''
        assert len(report['errors']) == 1
        assert report['errors'][0]['message'] == 'SyntaxError: invalid syntax'
        assert error_contains in report['errors'][0]['description']
        assert report['result'] == 'code error'
        assert report['set_name'] == ''
        assert report['steps'] == []
        assert report['test_case'] == test_name
        assert report['test_data'] == {}

    # A1
    def test_run_test__import_error_page_object(self, project_function_clean,
                                                caplog, test_utils):
        """The test fails with 'code error' when an imported page has a syntax error"""
        testdir = project_function_clean.testdir
        project = project_function_clean.name
        test_name = test_utils.random_numeric_string(10)
        content = """
pages = ['page1']

def setup(data):
    step('this step wont be run')

def test(data):
    step('this step wont be run')

def teardown(data):
    step('this step wont be run')
"""
        self._create_test(testdir, project, test_name, content)
        page_content = """
element1 = ('id', 'someId'
element2 = ('css', '.oh.no')
"""
        self._create_page(testdir, project, 'page1', page_content)
        report_directory = self._mock_report_directory(testdir, project, test_name)
        settings = settings_manager.get_project_settings(testdir, project)
        browser = _define_browsers_mock(['chrome'])[0]
        test_runner.run_test(workspace=testdir, project=project, test_name=test_name,
                             test_data={}, secrets={}, browser=browser, settings=settings,
                             report_directory=report_directory)
        # verify console logs
        records = caplog.records
        assert records[0].message == 'Test execution started: {}'.format(test_name)
        assert records[1].message == 'Browser: chrome'
        assert records[2].levelname == 'ERROR'
        error_contains = "element2 = ('css', '.oh.no')\n           ^\nSyntaxError: invalid syntax"
        assert error_contains in records[2].message
        assert records[3].message == 'Test Result: CODE ERROR'
        # verify report.json
        report = self._read_report_json(report_directory)
        assert report['browser'] == 'chrome'
        assert report['description'] is None  # description could not be read
        assert report['environment'] == ''
        assert len(report['errors']) == 1
        assert 'SyntaxError: invalid syntax' in report['errors'][0]['message']
        assert error_contains in report['errors'][0]['description']
        assert report['result'] == 'code error'
        assert report['set_name'] == ''
        assert report['steps'] == []
        assert report['test_case'] == test_name
        assert report['test_data'] == {}
        assert 'test_elapsed_time' in report
        assert 'test_timestamp' in report
        assert len(report.keys()) == 11

    # A3
    def test_run_test__AssertionError_in_setup(self, project_function_clean,
                                               caplog, test_utils):
        """The test ends with 'failure' when the setup function throws AssertionError.
        Test is not run
        Teardown is run
        """
        testdir = project_function_clean.testdir
        project = project_function_clean.name
        test_name = test_utils.random_numeric_string(10)
        content = """
description = 'desc'

def setup(data):
    fail('setup step fail')

def test(data):
    step('test step')

def teardown(data):
    step('teardown step')
"""
        self._create_test(testdir, project, test_name, content)
        report_directory = self._mock_report_directory(testdir, project, test_name)
        settings = settings_manager.get_project_settings(testdir, project)
        browser = _define_browsers_mock(['chrome'])[0]
        test_runner.run_test(workspace=testdir, project=project, test_name=test_name,
                             test_data={}, secrets={}, browser=browser, settings=settings,
                             report_directory=report_directory)
        # verify console logs
        records = caplog.records
        assert records[0].message == 'Test execution started: {}'.format(test_name)
        assert records[1].message == 'Browser: chrome'
        assert records[2].levelname == 'ERROR'
        assert 'setup step fail' in records[2].message
        assert 'AssertionError: setup step fail' in records[2].message
        assert records[3].message == 'teardown step'
        assert records[4].message == 'Test Result: FAILURE'
        # verify report.json
        report = self._read_report_json(report_directory)
        assert report['description'] == 'desc'
        assert len(report['errors']) == 1
        assert 'setup step fail' in report['errors'][0]['message']
        assert report['result'] == 'failure'
        assert report['steps'][0]['message'] == 'Failure'
        assert 'AssertionError: setup step fail' in report['steps'][0]['error']['description']
        assert report['steps'][1]['message'] == 'teardown step'

    # A4
    def test_run_test__failure_and_error_in_setup(self, project_function_clean,
                                                  caplog, test_utils):
        """The test ends with 'failure' when the setup function throws AssertionError,
        even when there's an error in setup
        Test is not run
        Teardown is run
        """
        testdir = project_function_clean.testdir
        project = project_function_clean.name
        test_name = test_utils.random_numeric_string(10)
        content = """
description = 'desc'

def setup(data):
    error('error in setup')
    fail('setup step fail')

def test(data):
    step('test step')

def teardown(data):
    step('teardown step')
"""
        self._create_test(testdir, project, test_name, content)
        report_directory = self._mock_report_directory(testdir, project, test_name)
        settings = settings_manager.get_project_settings(testdir, project)
        browser = _define_browsers_mock(['chrome'])[0]
        test_runner.run_test(workspace=testdir, project=project, test_name=test_name,
                             test_data={}, secrets={}, browser=browser, settings=settings,
                             report_directory=report_directory)
        # verify console logs
        records = caplog.records
        assert records[5].message == 'Test Result: FAILURE'
        # verify report.json
        report = self._read_report_json(report_directory)
        assert len(report['errors']) == 2
        assert report['result'] == 'failure'
        assert len(report['steps']) == 3
        assert report['errors'][0]['message'] == 'error in setup'
        assert report['errors'][1]['message'] == 'AssertionError: setup step fail'

    # A5
    def test_run_test__failure_in_setup_error_in_teardown(self, project_function_clean,
                                                          caplog, test_utils):
        """Setup throws AssertionError
        Teardown throws error
        Test ends with 'failure'
        test() is not run
        """
        testdir = project_function_clean.testdir
        project = project_function_clean.name
        test_name = test_utils.random_numeric_string(10)
        content = """
description = 'desc'

def setup(data):
    fail('setup step fail')

def test(data):
    step('test step')

def teardown(data):
    step('teardown step')
    error('error in teardown')
"""
        self._create_test(testdir, project, test_name, content)
        report_directory = self._mock_report_directory(testdir, project, test_name)
        settings = settings_manager.get_project_settings(testdir, project)
        browser = _define_browsers_mock(['chrome'])[0]
        test_runner.run_test(workspace=testdir, project=project, test_name=test_name,
                             test_data={}, secrets={}, browser=browser, settings=settings,
                             report_directory=report_directory)
        # verify console logs
        records = caplog.records
        assert records[5].message == 'Test Result: FAILURE'
        # verify report.json
        report = self._read_report_json(report_directory)
        assert len(report['errors']) == 2
        assert report['result'] == 'failure'
        assert len(report['steps']) == 3
        assert report['errors'][0]['message'] == 'AssertionError: setup step fail'
        assert report['errors'][1]['message'] == 'error in teardown'

    # A6
    def test_run_test__failure_in_setup_exception_in_teardown(self, project_function_clean,
                                                              caplog, test_utils):
        """Setup throws AssertionError
        Teardown throws AssertionError
        Test ends with 'failure'
        test() is not run
        """
        testdir = project_function_clean.testdir
        project = project_function_clean.name
        test_name = test_utils.random_numeric_string(10)
        content = """
description = 'desc'

def setup(data):
    fail('setup step fail')

def test(data):
    step('test step')

def teardown(data):
    step('teardown step')
    foo = bar
"""
        self._create_test(testdir, project, test_name, content)
        report_directory = self._mock_report_directory(testdir, project, test_name)
        settings = settings_manager.get_project_settings(testdir, project)
        browser = _define_browsers_mock(['chrome'])[0]
        test_runner.run_test(workspace=testdir, project=project, test_name=test_name,
                             test_data={}, secrets={}, browser=browser, settings=settings,
                             report_directory=report_directory)
        # verify console logs
        records = caplog.records
        assert records[5].message == 'Test Result: FAILURE'
        # verify report.json
        report = self._read_report_json(report_directory)
        assert len(report['errors']) == 2
        assert report['result'] == 'failure'
        assert len(report['steps']) == 3
        assert report['errors'][0]['message'] == 'AssertionError: setup step fail'
        assert report['errors'][1]['message'] == "NameError: name 'bar' is not defined"

    # A8
    def test_run_test__failure_in_setup_failure_in_teardown(self, project_function_clean,
                                                            caplog, test_utils):
        """Setup throws AssertionError
        Teardown throws exception
        Test ends with 'failure'
        test() is not run
        """
        testdir = project_function_clean.testdir
        project = project_function_clean.name
        test_name = test_utils.random_numeric_string(10)
        content = """
description = 'desc'

def setup(data):
    fail('setup step fail')

def test(data):
    step('test step')

def teardown(data):
    fail('failure in teardown')
"""
        self._create_test(testdir, project, test_name, content)
        report_directory = self._mock_report_directory(testdir, project, test_name)
        settings = settings_manager.get_project_settings(testdir, project)
        browser = _define_browsers_mock(['chrome'])[0]
        test_runner.run_test(workspace=testdir, project=project, test_name=test_name,
                             test_data={}, secrets={}, browser=browser, settings=settings,
                             report_directory=report_directory)
        # verify console logs
        records = caplog.records
        assert records[4].message == 'Test Result: FAILURE'
        # verify report.json
        report = self._read_report_json(report_directory)
        assert len(report['errors']) == 2
        assert report['result'] == 'failure'
        assert len(report['steps']) == 2
        assert report['errors'][0]['message'] == 'AssertionError: setup step fail'
        assert report['errors'][1]['message'] == 'AssertionError: failure in teardown'

    # B0
    def test_run_test__exception_in_setup(self, project_function_clean,
                                          caplog, test_utils):
        """Setup throws exception
        Test ends with 'code error'
        test() is not run
        teardown() is run
        """
        testdir = project_function_clean.testdir
        project = project_function_clean.name
        test_name = test_utils.random_numeric_string(10)
        content = """
description = 'desc'

def setup(data):
    foo = bar

def test(data):
    step('test step')

def teardown(data):
    step('teardown step')
"""
        self._create_test(testdir, project, test_name, content)
        report_directory = self._mock_report_directory(testdir, project, test_name)
        settings = settings_manager.get_project_settings(testdir, project)
        browser = _define_browsers_mock(['chrome'])[0]
        test_runner.run_test(workspace=testdir, project=project, test_name=test_name,
                             test_data={}, secrets={}, browser=browser, settings=settings,
                             report_directory=report_directory)
        # verify console logs
        records = caplog.records
        assert records[4].message == 'Test Result: CODE ERROR'
        # verify report.json
        report = self._read_report_json(report_directory)
        assert len(report['errors']) == 1
        assert report['result'] == 'code error'
        assert len(report['steps']) == 2
        assert report['errors'][0]['message'] == "NameError: name 'bar' is not defined"

    # B1
    def test_run_test__exception_and_error_in_setup(self, project_function_clean,
                                                    caplog, test_utils):
        """Setup has error and throws exception
        Test ends with 'code error'
        test() is not run
        teardown() is run
        """
        testdir = project_function_clean.testdir
        project = project_function_clean.name
        test_name = test_utils.random_numeric_string(10)
        content = """
description = 'desc'

def setup(data):
    error('setup error')
    foo = bar

def test(data):
    step('test step')

def teardown(data):
    step('teardown step')
"""
        self._create_test(testdir, project, test_name, content)
        report_directory = self._mock_report_directory(testdir, project, test_name)
        settings = settings_manager.get_project_settings(testdir, project)
        browser = _define_browsers_mock(['chrome'])[0]
        test_runner.run_test(workspace=testdir, project=project, test_name=test_name,
                             test_data={}, secrets={}, browser=browser, settings=settings,
                             report_directory=report_directory)
        # verify console logs
        records = caplog.records
        assert records[5].message == 'Test Result: CODE ERROR'
        # verify report.json
        report = self._read_report_json(report_directory)
        assert report['result'] == 'code error'
        assert len(report['steps']) == 3
        assert len(report['errors']) == 2
        assert report['errors'][0]['message'] == 'setup error'
        assert report['errors'][1]['message'] == "NameError: name 'bar' is not defined"

    # B3
    def test_run_test__exception_in_setup_exception_in_teardown(self, project_function_clean,
                                                                caplog, test_utils):
        """Setup throws exception
        Teardown throws exception
        Test ends with 'code error'
        test() is not run
        """
        testdir = project_function_clean.testdir
        project = project_function_clean.name
        test_name = test_utils.random_numeric_string(10)
        content = """
description = 'desc'

def setup(data):
    foo = bar

def test(data):
    step('test step')

def teardown(data):
    foo = baz
"""
        self._create_test(testdir, project, test_name, content)
        report_directory = self._mock_report_directory(testdir, project, test_name)
        settings = settings_manager.get_project_settings(testdir, project)
        browser = _define_browsers_mock(['chrome'])[0]
        test_runner.run_test(workspace=testdir, project=project, test_name=test_name,
                             test_data={}, secrets={}, browser=browser, settings=settings,
                             report_directory=report_directory)
        # verify console logs
        records = caplog.records
        assert records[4].message == 'Test Result: CODE ERROR'
        # verify report.json
        report = self._read_report_json(report_directory)
        assert report['result'] == 'code error'
        assert len(report['steps']) == 2
        assert len(report['errors']) == 2
        assert report['errors'][0]['message'] == "NameError: name 'bar' is not defined"
        assert report['errors'][1]['message'] == "NameError: name 'baz' is not defined"

    # B5
    def test_run_test__exception_in_setup_failure_in_teardown(self, project_function_clean,
                                                              caplog, test_utils):
        """Setup throws exception
        Teardown throws AssertionError
        Test ends with 'code error'
        test() is not run
        """
        testdir = project_function_clean.testdir
        project = project_function_clean.name
        test_name = test_utils.random_numeric_string(10)
        content = """
description = 'desc'

def setup(data):
    foo = bar

def test(data):
    step('test step')

def teardown(data):
    fail('teardown failure')
"""
        self._create_test(testdir, project, test_name, content)
        report_directory = self._mock_report_directory(testdir, project, test_name)
        settings = settings_manager.get_project_settings(testdir, project)
        browser = _define_browsers_mock(['chrome'])[0]
        test_runner.run_test(workspace=testdir, project=project, test_name=test_name,
                             test_data={}, secrets={}, browser=browser, settings=settings,
                             report_directory=report_directory)
        # verify console logs
        records = caplog.records
        assert records[4].message == 'Test Result: CODE ERROR'
        # verify report.json
        report = self._read_report_json(report_directory)
        assert report['result'] == 'code error'
        assert len(report['steps']) == 2
        assert len(report['errors']) == 2
        assert report['errors'][0]['message'] == "NameError: name 'bar' is not defined"
        assert report['errors'][1]['message'] == 'AssertionError: teardown failure'

    # B7
    def test_run_test__error_in_setup(self, project_function_clean, caplog, test_utils):
        """Setup has error
        test() is run
        teardown() is run
        """
        testdir = project_function_clean.testdir
        project = project_function_clean.name
        test_name = test_utils.random_numeric_string(10)
        content = """
description = 'desc'

def setup(data):
    error('setup error')

def test(data):
    step('test step')

def teardown(data):
    step('teardown step')
"""
        self._create_test(testdir, project, test_name, content)
        report_directory = self._mock_report_directory(testdir, project, test_name)
        settings = settings_manager.get_project_settings(testdir, project)
        browser = _define_browsers_mock(['chrome'])[0]
        test_runner.run_test(workspace=testdir, project=project, test_name=test_name,
                             test_data={}, secrets={}, browser=browser, settings=settings,
                             report_directory=report_directory)
        # verify console logs
        records = caplog.records
        assert records[5].message == 'Test Result: ERROR'
        # verify report.json
        report = self._read_report_json(report_directory)
        assert report['result'] == 'error'
        assert len(report['steps']) == 3
        assert len(report['errors']) == 1
        assert report['errors'][0]['message'] == "setup error"

    # B9
    def test_run_test__error_in_setup_exception_in_teardown(self, project_function_clean,
                                                            caplog, test_utils):
        """Setup has error
        Teardown throws exception
        test() is run
        """
        testdir = project_function_clean.testdir
        project = project_function_clean.name
        test_name = test_utils.random_numeric_string(10)
        content = """
description = 'desc'

def setup(data):
    error('setup error')

def test(data):
    step('test step')

def teardown(data):
    foo = bar
"""
        self._create_test(testdir, project, test_name, content)
        report_directory = self._mock_report_directory(testdir, project, test_name)
        settings = settings_manager.get_project_settings(testdir, project)
        browser = _define_browsers_mock(['chrome'])[0]
        test_runner.run_test(workspace=testdir, project=project, test_name=test_name,
                             test_data={}, secrets={}, browser=browser, settings=settings,
                             report_directory=report_directory)
        # verify console logs
        records = caplog.records
        assert records[5].message == 'Test Result: CODE ERROR'
        # verify report.json
        report = self._read_report_json(report_directory)
        assert report['result'] == 'code error'
        assert len(report['steps']) == 3
        assert len(report['errors']) == 2
        assert report['errors'][0]['message'] == 'setup error'
        assert report['errors'][1]['message'] == "NameError: name 'bar' is not defined"

    # C0
    def test_run_test__error_in_setup_failure_in_teardown(self, project_function_clean,
                                                          caplog, test_utils):
        """Setup has error
        Teardown throws AssertionError
        test() is run
        """
        testdir = project_function_clean.testdir
        project = project_function_clean.name
        test_name = test_utils.random_numeric_string(10)
        content = """
description = 'desc'

def setup(data):
    error('setup error')

def test(data):
    step('test step')

def teardown(data):
    fail('teardown fail')
"""
        self._create_test(testdir, project, test_name, content)
        report_directory = self._mock_report_directory(testdir, project, test_name)
        settings = settings_manager.get_project_settings(testdir, project)
        browser = _define_browsers_mock(['chrome'])[0]
        test_runner.run_test(workspace=testdir, project=project, test_name=test_name,
                             test_data={}, secrets={}, browser=browser, settings=settings,
                             report_directory=report_directory)
        # verify console logs
        records = caplog.records
        assert records[5].message == 'Test Result: FAILURE'
        # verify report.json
        report = self._read_report_json(report_directory)
        assert report['result'] == 'failure'
        assert len(report['steps']) == 3
        assert len(report['errors']) == 2
        assert report['errors'][0]['message'] == 'setup error'
        assert report['errors'][1]['message'] == 'AssertionError: teardown fail'

    # C1
    def test_run_test__failure_in_test(self, project_function_clean, caplog, test_utils):
        """test() throws AssertionError
        teardown() is run
        """
        testdir = project_function_clean.testdir
        project = project_function_clean.name
        test_name = test_utils.random_numeric_string(10)
        content = """
description = 'desc'

def setup(data):
    step('setup step')

def test(data):
    step('test step')
    fail('test fail')

def teardown(data):
    step('teardown step')
"""
        self._create_test(testdir, project, test_name, content)
        report_directory = self._mock_report_directory(testdir, project, test_name)
        settings = settings_manager.get_project_settings(testdir, project)
        browser = _define_browsers_mock(['chrome'])[0]
        test_runner.run_test(workspace=testdir, project=project, test_name=test_name,
                             test_data={}, secrets={}, browser=browser, settings=settings,
                             report_directory=report_directory)
        # verify console logs
        records = caplog.records
        assert records[6].message == 'Test Result: FAILURE'
        # verify report.json
        report = self._read_report_json(report_directory)
        assert report['result'] == 'failure'
        assert len(report['steps']) == 4
        assert len(report['errors']) == 1
        assert report['errors'][0]['message'] == 'AssertionError: test fail'

    # C2
    def test_run_test__failure_and_error_in_test(self, project_function_clean,
                                                 caplog, test_utils):
        """test() has error and throws AssertionError
        teardown() is run
        """
        testdir = project_function_clean.testdir
        project = project_function_clean.name
        test_name = test_utils.random_numeric_string(10)
        content = """
description = 'desc'

def setup(data):
    step('setup step')

def test(data):
    error('test error')
    fail('test fail')

def teardown(data):
    step('teardown step')
"""
        self._create_test(testdir, project, test_name, content)
        report_directory = self._mock_report_directory(testdir, project, test_name)
        settings = settings_manager.get_project_settings(testdir, project)
        browser = _define_browsers_mock(['chrome'])[0]
        test_runner.run_test(workspace=testdir, project=project, test_name=test_name,
                             test_data={}, secrets={}, browser=browser, settings=settings,
                             report_directory=report_directory)
        # verify console logs
        records = caplog.records
        assert records[6].message == 'Test Result: FAILURE'
        # verify report.json
        report = self._read_report_json(report_directory)
        assert report['result'] == 'failure'
        assert len(report['steps']) == 4
        assert len(report['errors']) == 2
        assert report['errors'][0]['message'] == 'test error'
        assert report['errors'][1]['message'] == 'AssertionError: test fail'

    # C5
    def test_run_test__failure_in_test_exception_in_teardown(self, project_function_clean,
                                                             caplog, test_utils):
        """test() throws AssertionError
        teardown() throws exception
        """
        testdir = project_function_clean.testdir
        project = project_function_clean.name
        test_name = test_utils.random_numeric_string(10)
        content = """
description = 'desc'

def setup(data):
    step('setup step')

def test(data):
    fail('test fail')

def teardown(data):
    foo = bar
"""
        self._create_test(testdir, project, test_name, content)
        report_directory = self._mock_report_directory(testdir, project, test_name)
        settings = settings_manager.get_project_settings(testdir, project)
        browser = _define_browsers_mock(['chrome'])[0]
        test_runner.run_test(workspace=testdir, project=project, test_name=test_name,
                             test_data={}, secrets={}, browser=browser, settings=settings,
                             report_directory=report_directory)
        # verify console logs
        records = caplog.records
        assert records[5].message == 'Test Result: FAILURE'
        # verify report.json
        report = self._read_report_json(report_directory)
        assert report['result'] == 'failure'
        assert len(report['steps']) == 3
        assert len(report['errors']) == 2
        assert report['errors'][0]['message'] == 'AssertionError: test fail'
        assert report['errors'][1]['message'] == "NameError: name 'bar' is not defined"

    # C7
    def test_run_test__failure_in_test_failure_in_teardown(self, project_function_clean,
                                                           caplog, test_utils):
        """test() throws AssertionError
        teardown() throws AssertionError
        """
        testdir = project_function_clean.testdir
        project = project_function_clean.name
        test_name = test_utils.random_numeric_string(10)
        content = """
description = 'desc'

def setup(data):
    step('setup step')

def test(data):
    fail('test fail')

def teardown(data):
    fail('teardown fail')
"""
        self._create_test(testdir, project, test_name, content)
        report_directory = self._mock_report_directory(testdir, project, test_name)
        settings = settings_manager.get_project_settings(testdir, project)
        browser = _define_browsers_mock(['chrome'])[0]
        test_runner.run_test(workspace=testdir, project=project, test_name=test_name,
                             test_data={}, secrets={}, browser=browser, settings=settings,
                             report_directory=report_directory)
        # verify console logs
        records = caplog.records
        assert records[5].message == 'Test Result: FAILURE'
        # verify report.json
        report = self._read_report_json(report_directory)
        assert report['result'] == 'failure'
        assert len(report['steps']) == 3
        assert len(report['errors']) == 2
        assert report['errors'][0]['message'] == 'AssertionError: test fail'
        assert report['errors'][1]['message'] == 'AssertionError: teardown fail'

    # C8
    def test_run_test__exception_in_test(self, project_function_clean, caplog, test_utils):
        """test() throws exception"""
        testdir = project_function_clean.testdir
        project = project_function_clean.name
        test_name = test_utils.random_numeric_string(10)
        content = """
description = 'desc'

def setup(data):
    step('setup step')

def test(data):
    foo = bar

def teardown(data):
    step('teardown step')
"""
        self._create_test(testdir, project, test_name, content)
        report_directory = self._mock_report_directory(testdir, project, test_name)
        settings = settings_manager.get_project_settings(testdir, project)
        browser = _define_browsers_mock(['chrome'])[0]
        test_runner.run_test(workspace=testdir, project=project, test_name=test_name,
                             test_data={}, secrets={}, browser=browser, settings=settings,
                             report_directory=report_directory)
        # verify console logs
        records = caplog.records
        assert records[5].message == 'Test Result: CODE ERROR'
        # verify report.json
        report = self._read_report_json(report_directory)
        assert report['result'] == 'code error'
        assert len(report['steps']) == 3
        assert len(report['errors']) == 1
        assert report['errors'][0]['message'] == "NameError: name 'bar' is not defined"

    # C9
    def test_run_test__error_and_exception_in_test(self, project_function_clean,
                                                   caplog, test_utils):
        """test() throws error and AssertionError
        teardown()
        """
        testdir = project_function_clean.testdir
        project = project_function_clean.name
        test_name = test_utils.random_numeric_string(10)
        content = """
description = 'desc'

def setup(data):
    step('setup step')

def test(data):
    error('error in test')
    foo = bar

def teardown(data):
    step('teardown step')
"""
        self._create_test(testdir, project, test_name, content)
        report_directory = self._mock_report_directory(testdir, project, test_name)
        settings = settings_manager.get_project_settings(testdir, project)
        browser = _define_browsers_mock(['chrome'])[0]
        test_runner.run_test(workspace=testdir, project=project, test_name=test_name,
                             test_data={}, secrets={}, browser=browser, settings=settings,
                             report_directory=report_directory)
        # verify console logs
        records = caplog.records
        assert records[6].message == 'Test Result: CODE ERROR'
        # verify report.json
        report = self._read_report_json(report_directory)
        assert report['result'] == 'code error'
        assert len(report['steps']) == 4
        assert len(report['errors']) == 2
        assert report['errors'][0]['message'] == 'error in test'
        assert report['errors'][1]['message'] == "NameError: name 'bar' is not defined"

    # D4
    def test_run_test__exception_in_test_failure_in_teardown(self, project_function_clean,
                                                             caplog, test_utils):
        """test() throws exception
        teardown() throws AssertionError
        """
        testdir = project_function_clean.testdir
        project = project_function_clean.name
        test_name = test_utils.random_numeric_string(10)
        content = """
description = 'desc'

def setup(data):
    step('setup step')

def test(data):
    foo = bar

def teardown(data):
    fail('teardown fail')
"""
        self._create_test(testdir, project, test_name, content)
        report_directory = self._mock_report_directory(testdir, project, test_name)
        settings = settings_manager.get_project_settings(testdir, project)
        browser = _define_browsers_mock(['chrome'])[0]
        test_runner.run_test(workspace=testdir, project=project, test_name=test_name,
                             test_data={}, secrets={}, browser=browser, settings=settings,
                             report_directory=report_directory)
        # verify console logs
        records = caplog.records
        assert records[5].message == 'Test Result: CODE ERROR'
        # verify report.json
        report = self._read_report_json(report_directory)
        assert report['result'] == 'code error'
        assert len(report['steps']) == 3
        assert len(report['errors']) == 2
        assert report['errors'][0]['message'] == "NameError: name 'bar' is not defined"
        assert report['errors'][1]['message'] == 'AssertionError: teardown fail'

    # D7
    def test_run_test__error_in_setup_test_and_teardown(self, project_function_clean,
                                                        caplog, test_utils):
        """setup(), test() and teardown() have errors
        """
        testdir = project_function_clean.testdir
        project = project_function_clean.name
        test_name = test_utils.random_numeric_string(10)
        content = """
description = 'desc'

def setup(data):
    error('setup error')

def test(data):
    error('test error')

def teardown(data):
    error('teardown error')
"""
        self._create_test(testdir, project, test_name, content)
        report_directory = self._mock_report_directory(testdir, project, test_name)
        settings = settings_manager.get_project_settings(testdir, project)
        browser = _define_browsers_mock(['chrome'])[0]
        test_runner.run_test(workspace=testdir, project=project, test_name=test_name,
                             test_data={}, secrets={}, browser=browser, settings=settings,
                             report_directory=report_directory)
        # verify console logs
        records = caplog.records
        assert records[5].message == 'Test Result: ERROR'
        # verify report.json
        report = self._read_report_json(report_directory)
        assert report['result'] == 'error'
        assert len(report['steps']) == 3
        assert len(report['errors']) == 3
        assert report['errors'][0]['message'] == 'setup error'
        assert report['errors'][1]['message'] == 'test error'
        assert report['errors'][2]['message'] == 'teardown error'
