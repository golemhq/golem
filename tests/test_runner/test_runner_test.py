import os
import json

from golem.test_runner import test_runner, execution_logger
from golem.test_runner.start_execution import define_drivers
from golem.gui import gui_utils
from golem.core import settings_manager


def _define_drivers_mock(selected_drivers):
    default_browsers = gui_utils.get_supported_browsers_suggestions()
    return define_drivers(selected_drivers, [], default_browsers)


class Test__get_set_name:

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
        assert test_runner._get_set_name(test_data) == 'user01'

    def test___get_set_name__empty_data(self):
        test_data = {}
        assert test_runner._get_set_name(test_data) == ''


class Test___print_test_info:

    def test___print_test_info(self, caplog):
        logger = execution_logger.get_logger()
        test_name = 'test01'
        browser = _define_drivers_mock(['chrome'])[0]
        test_data = {
            'key1': 'a',
            'key2': 'b'
        }
        test_runner._print_test_info(logger, test_name, browser, test_data)
        assert caplog.records[0].message == 'Test execution started: test01'
        assert caplog.records[1].message == 'Browser: chrome'
        assert caplog.records[2].message == 'Using data:\n    key1: a\n    key2: b\n'

    def test___print_test_info__with_env(self, caplog):
        logger = execution_logger.get_logger()
        test_name = 'test01'
        browser = _define_drivers_mock(['chrome'])[0]
        test_data = {
            'key1': 'a',
            'key2': 'b',
            'env': {
                'url': 'http://',
                'username': 'myusername'
            }
        }
        test_runner._print_test_info(logger, test_name, browser, test_data)
        assert caplog.records[0].message == 'Test execution started: test01'
        assert caplog.records[1].message == 'Browser: chrome'
        assert caplog.records[2].message == 'Using data:\n    key1: a\n    key2: b\n    url: http://\n'

    def test___print_test_info__no_data(self, caplog):
        logger = execution_logger.get_logger()
        test_name = 'test01'
        browser = _define_drivers_mock(['chrome'])[0]
        test_data = {}
        test_runner._print_test_info(logger, test_name, browser, test_data)
        assert caplog.records[0].message == 'Test execution started: test01'
        assert caplog.records[1].message == 'Browser: chrome'
        assert len(caplog.records) == 2


# TestRunner decision table
#
# CE : code error
# S  : success
# F  : failure
# E  : error
#
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
# result                 CE  CE  S   F   F   F   F   F   F   F   CE  CE  CE  CE  CE  CE  CE  E   E   E   E   F   F   F   F   F   F   F   CE  CE  CE  CE  CE  CE  CE  E   E   E   E   E   E   E   CE  CE  F   F
# setup is run           N   N   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y
# test is run            N   N   Y   N   N   N   N   N   N   N   N   N   N   N   N   N   N   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y
# teardown is run        N   N   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y   Y


class Test_run_test:

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

    # SUCCESS TESTS

    # A2
    def test_run_test__success(self, project_function_clean, caplog):
        """Test runs successfully"""
        testdir = project_function_clean['testdir']
        project = project_function_clean['name']
        test_name = 'test1'
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
        browser = _define_drivers_mock(['chrome'])[0]
        # run test
        test_runner.run_test(workspace=testdir, project=project,
                             test_name=test_name, test_data={},
                             browser=browser, settings=settings,
                             report_directory=report_directory)
        # verify console logs
        records = caplog.records
        assert records[0].message == 'Test execution started: {}'.format(test_name)
        assert records[1].message == 'Browser: chrome'
        assert records[2].message == 'setup step'
        assert records[3].message == 'test step'
        assert records[4].message == 'teardown step'
        assert records[5].message == 'Test end: success'
        # verify report.json
        report = self._read_report_json(report_directory)
        assert report['browser'] == 'chrome'
        assert report['description'] == 'some description'
        assert report['environment'] == ''
        assert report['errors'] == []
        assert report['result'] == 'success'
        assert report['set_name'] == ''
        assert report['short_error'] == ''
        assert report['steps'] == ['setup step', 'test step', 'teardown step']
        assert report['test_case'] == 'test1'
        assert report['test_data'] == {}
        assert 'test_elapsed_time' in report
        assert 'test_timestamp' in report
        assert len(report.keys()) == 12

    # A2
    def test_run_test__success_with_data(self, project_function_clean, caplog):
        """Test runs successfully with test data"""
        testdir = project_function_clean['testdir']
        project = project_function_clean['name']
        test_name = 'test1'
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
        browser = _define_drivers_mock(['chrome'])[0]
        test_data = dict(username='username1', password='password1')
        # run test
        test_runner.run_test(workspace=testdir, project=project,
                             test_name=test_name, test_data=test_data,
                             browser=browser, settings=settings,
                             report_directory=report_directory)
        # verify console logs
        records = caplog.records
        assert records[0].message == 'Test execution started: {}'.format(
            test_name)
        assert records[1].message == 'Browser: chrome'
        assert records[2].message == 'Using data:\n    username: username1\n    password: password1\n'
        assert records[3].message == 'setup step'
        assert records[4].message == 'test step'
        assert records[5].message == 'teardown step'
        assert records[6].message == 'Test end: success'
        # verify report.json
        report = self._read_report_json(report_directory)
        assert report['browser'] == 'chrome'
        assert report['description'] == 'some description'
        assert report['environment'] == ''
        assert report['errors'] == []
        assert report['result'] == 'success'
        assert report['set_name'] == 'username1'
        assert report['short_error'] == ''
        assert report['steps'] == ['setup step', 'test step',
                                   'teardown step']
        assert report['test_case'] == 'test1'
        assert report['test_data'] == {'username': "'username1'", 'password': "'password1'"}
        assert 'test_elapsed_time' in report
        assert 'test_timestamp' in report
        assert len(report.keys()) == 12

    # ERRORS in import_modules

    # A0
    def test_run_test__import_error_on_test(self, project_function_clean,
                                            caplog):
        """The test fails with 'code error' when it has a syntax error
        Test result is code error"""
        testdir = project_function_clean['testdir']
        project = project_function_clean['name']
        test_name = 'test1'
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
        browser = _define_drivers_mock(['chrome'])[0]

        test_runner.run_test(workspace=testdir, project=project,
                             test_name=test_name, test_data={},
                             browser=browser, settings=settings,
                             report_directory=report_directory)
        # verify console logs
        records = caplog.records
        assert records[0].message == 'Test execution started: {}'.format(
            test_name)
        assert records[1].message == 'Browser: chrome'
        assert records[2].levelname == 'ERROR'
        error_contains = 'def test(data)\n                 ^\nSyntaxError: invalid syntax'
        assert error_contains in records[2].message
        assert records[3].message == 'Test end: code error'
        # verify report.json
        report = self._read_report_json(report_directory)
        assert report['browser'] == 'chrome'
        assert report['description'] == None # description could not be read
        assert report['environment'] == ''
        assert len(report['errors']) == 1
        assert error_contains in report['errors'][0]
        assert report['result'] == 'code error'
        assert report['set_name'] == ''
        assert report['short_error'] == ''
        assert report['steps'] == []
        assert report['test_case'] == 'test1'
        assert report['test_data'] == {}

    # A1
    def test_run_test__import_error_page_object(self, project_function_clean, caplog):
        """The test fails with 'code error' when an imported page has a syntax error"""
        testdir = project_function_clean['testdir']
        project = project_function_clean['name']
        test_name = 'test1'
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
        report_directory = self._mock_report_directory(testdir, project,
                                                       test_name)
        settings = settings_manager.get_project_settings(testdir, project)
        browser = _define_drivers_mock(['chrome'])[0]
        test_runner.run_test(workspace=testdir, project=project,
                             test_name=test_name, test_data={},
                             browser=browser, settings=settings,
                             report_directory=report_directory)
        # verify console logs
        records = caplog.records
        assert records[0].message == 'Test execution started: {}'.format(
            test_name)
        assert records[1].message == 'Browser: chrome'
        assert records[2].levelname == 'ERROR'
        error_contains = "element2 = ('css', '.oh.no')\n           ^\nSyntaxError: invalid syntax"
        assert error_contains in records[2].message
        assert records[3].message == 'Test end: code error'
        # verify report.json
        report = self._read_report_json(report_directory)
        assert report['browser'] == 'chrome'
        assert report['description'] == None  # description could not be read
        assert report['environment'] == ''
        assert len(report['errors']) == 1
        assert error_contains in report['errors'][0]
        assert report['result'] == 'code error'
        assert report['set_name'] == ''
        assert report['short_error'] == ''
        assert report['steps'] == []
        assert report['test_case'] == 'test1'
        assert report['test_data'] == {}
        assert 'test_elapsed_time' in report
        assert 'test_timestamp' in report
        assert len(report.keys()) == 12

    # A3
    def test_run_test__TestFailure_in_setup(self, project_function_clean, caplog):
        """The test ends with 'failure' when the setup function throws TestFailure.
        Test is not run
        Teardown is run
        """
        testdir = project_function_clean['testdir']
        project = project_function_clean['name']
        test_name = 'test1'
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
        report_directory = self._mock_report_directory(testdir, project,
                                                       test_name)
        settings = settings_manager.get_project_settings(testdir, project)
        browser = _define_drivers_mock(['chrome'])[0]
        test_runner.run_test(workspace=testdir, project=project,
                             test_name=test_name, test_data={},
                             browser=browser, settings=settings,
                             report_directory=report_directory)
        # verify console logs
        records = caplog.records
        assert records[0].message == 'Test execution started: {}'.format(
            test_name)
        assert records[1].message == 'Browser: chrome'
        assert records[2].levelname == 'ERROR'
        assert 'setup failed' in records[2].message
        assert 'setup step fail' in records[2].exc_text
        assert records[3].message == 'teardown step'
        assert records[4].message == 'Test end: failure'
        # verify report.json
        report = self._read_report_json(report_directory)
        assert report['description'] == 'desc'
        assert len(report['errors']) == 1
        assert 'setup step fail' in report['errors'][0]
        assert report['result'] == 'failure'
        assert report['steps'] == ['teardown step']

    # A3
    def test_run_test__AssertionError_in_setup(self, project_function_clean, caplog):
        """The test ends with 'failure' when the setup function throws AssertionError.
        Test is not run
        Teardown is run
        """
        testdir = project_function_clean['testdir']
        project = project_function_clean['name']
        test_name = 'test1'
        content = """
description = 'desc'

def setup(data):
    assert 1 == 2

def test(data):
    step('test step')

def teardown(data):
    step('teardown step')
"""
        self._create_test(testdir, project, test_name, content)
        report_directory = self._mock_report_directory(testdir, project,
                                                       test_name)
        settings = settings_manager.get_project_settings(testdir, project)
        browser = _define_drivers_mock(['chrome'])[0]
        test_runner.run_test(workspace=testdir, project=project,
                             test_name=test_name, test_data={},
                             browser=browser, settings=settings,
                             report_directory=report_directory)
        # verify console logs
        records = caplog.records
        assert records[0].message == 'Test execution started: {}'.format(
            test_name)
        assert records[1].message == 'Browser: chrome'
        assert records[2].levelname == 'ERROR'
        assert 'setup failed' in records[2].message
        assert 'assert 1 == 2' in records[2].exc_text
        assert records[3].message == 'teardown step'
        assert records[4].message == 'Test end: failure'
        # verify report.json
        report = self._read_report_json(report_directory)
        assert report['description'] == 'desc'
        assert len(report['errors']) == 1
        assert 'assert 1 == 2' in report['errors'][0]
        assert report['result'] == 'failure'
        assert report['steps'] == ['teardown step']


