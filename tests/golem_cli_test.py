import os
import csv
import string
import random
import pytest

import golem
from golem.cli import messages, commands
from golem.core import errors, test_directory


class TestGolemHelp:

    run_commands = [
        ('golem', messages.USAGE_MSG),
        ('golem -h', messages.USAGE_MSG),
        ('golem --help', messages.USAGE_MSG),
        ('golem -h run', messages.RUN_USAGE_MSG),
        ('golem -h gui', messages.GUI_USAGE_MSG),
        ('golem -h createproject', messages.CREATEPROJECT_USAGE_MSG),
        ('golem -h createtest', messages.CREATETEST_USAGE_MSG),
        ('golem -h createsuite', messages.CREATESUITE_USAGE_MSG),
        ('golem -h createsuperuser', messages.CREATESUPERUSER_USAGE_MSG),
        ('golem run -h', messages.RUN_USAGE_MSG),
        ('golem gui -h', messages.GUI_USAGE_MSG),
    ]

    @pytest.mark.slow
    @pytest.mark.parametrize('command,expected', run_commands)
    def test_golem_command_output(self, command, expected, testdir_session, test_utils):
        os.chdir(testdir_session.path)
        result = test_utils.run_command(command)
        assert result == expected

    @pytest.mark.slow
    def test_golem_help_from_non_golem_dir(self, dir_function, test_utils):
        # current directory is not a Golem directory
        assert dir_function.path == os.getcwd()
        result = test_utils.run_command('golem -h')
        assert result == messages.USAGE_MSG


class TestGolemDirArg:
    """Test the --golem-dir arg.
    This enables Golem to be called from any directory.
    """

    @pytest.mark.slow
    def test_specify_golem_test_directory_path(self, dir_function, test_utils):
        """The path to the Golem test directory can be specified
        using the golem-dir argument
        """
        os.chdir(dir_function.path)
        golem_dir_name = 'golem_dir'
        golem_directory = os.path.join(dir_function.path, golem_dir_name)
        commands.createdirectory_command(golem_directory, download_drivers=False)

        # createproject command in a non golem directory
        # without golem-dir argument
        command = 'golem createproject project_one'
        result = test_utils.run_command(command)
        msg = (f'Error: {dir_function.path} is not an valid Golem test directory; '
               '.golem file not found')
        assert msg in result

        # specify golem-dir with absolute path
        command = f'golem --golem-dir {golem_directory} createproject project_two'
        result = test_utils.run_command(command)
        assert 'Project project_two created' in result

        # specify golem-dir with relative path
        command = f'golem --golem-dir {golem_dir_name} createproject project_three'
        result = test_utils.run_command(command)
        assert 'Project project_three created' in result

    @pytest.mark.slow
    def test_golem_dir_arg_does_not_point_to_test_directory(self, dir_function, test_utils):
        """Passing an invalid golem-dir argument value"""
        os.chdir(dir_function.path)
        dir_name = 'dir_one'
        dir_path = os.path.join(dir_function.path, dir_name)

        error_msg = 'Error: {} is not an valid Golem test directory; .golem file not found'
        command = 'golem --golem-dir {} createproject project_two'

        # invalid golem-dir with relative path
        result = test_utils.run_command(command.format(dir_name))
        assert error_msg.format(dir_path) in result

        # invalid golem-dir with absolute path
        result = test_utils.run_command(command.format(dir_path))
        assert error_msg.format(dir_path) in result


class TestGolemRun:

    @pytest.mark.slow
    def test_golem_run_test(self, project_session, test_utils):
        path, project = project_session.activate()
        os.chdir(path)
        test = 'test2'
        test_utils.create_test(project, test)
        result = test_utils.run_command(f'golem run {project} {test}')
        assert f'INFO Test execution started: {test}' in result
        assert 'INFO Browser: chrome' in result
        assert 'INFO Test Result: SUCCESS' in result

    @pytest.mark.slow
    def test_golem_run_suite_with_no_tests(self, project_session, test_utils):
        path, project = project_session.activate()
        os.chdir(path)
        suite = 'suite2'
        test_utils.create_suite(project, suite)
        result = test_utils.run_command(f'golem run {project} {suite}')
        assert 'No tests found for suite suite2' in result

    @pytest.mark.slow
    def test_golem_run_no_args(self, project_session, test_utils):
        testdir, _ = project_session.activate()
        os.chdir(testdir)
        result = test_utils.run_command('golem run')
        expected = messages.RUN_USAGE_MSG
        expected += '\nProjects:'
        for project in test_directory.get_projects():
            expected += f'\n  {project}'
        assert result == expected

    @pytest.mark.slow
    def test_golem_run_test_b_flag(self, project_session, test_utils):
        path, project = project_session.activate()
        os.chdir(path)
        test = 'test2'
        test_utils.run_command(f'golem createtest {project} {test}')
        result = test_utils.run_command(f'golem run {project} {test} -b firefox')
        assert f'INFO Test execution started: {test}' in result
        assert 'INFO Browser: firefox' in result
        assert 'INFO Test Result: SUCCESS' in result

    @pytest.mark.slow
    def test_golem_run_not_match_test_or_suite(self, project_session, test_utils):
        path, project = project_session.activate()
        os.chdir(path)
        test = 'test001_does_not_exist'
        result = test_utils.run_command(f'golem run {project} {test}')
        expected = (f'golem run: error: the value {test} does not match '
                    'an existing test, suite or directory')
        assert result == expected

    @pytest.mark.slow
    def test_golem_run_project_does_not_exist(self, testdir_session, test_utils):
        testdir = testdir_session.activate()
        os.chdir(testdir)
        project = 'project_does_not_exist_4564546'
        test = 'test002_does_not_exist'
        result = test_utils.run_command(f'golem run {project} {test}')
        assert result == f'golem run: error: the project {project} does not exist'

    @pytest.fixture(scope="class")
    def _project_with_suite(self, project_class, test_utils):
        """A fixture of a project with class scope with one suite with
        one test
        """
        testdir, project = project_class.activate()
        suite_name = 'suite1'
        test_utils.create_test(project, name='test1')
        test_utils.create_suite(project, name=suite_name, content=None, tests=['test1'])
        project_class.suite_name = suite_name
        return project_class

    @pytest.mark.slow
    def test_generate_reports(self, _project_with_suite, test_utils):
        """Assert that the reports are generated by default in the
        report directory and with name: 'report'
        """
        testdir, project = _project_with_suite.activate()
        suite_name = _project_with_suite.suite_name
        os.chdir(testdir)
        timestamp = '0.1.2.3.001'
        cmd = f'golem run {project} {suite_name} -r html html-no-images junit --timestamp {timestamp}'
        test_utils.run_command(cmd)
        reportdir = os.path.join(testdir, 'projects', project, 'reports', suite_name, timestamp)
        assert os.path.isfile(os.path.join(reportdir, 'report.html'))
        assert os.path.isfile(os.path.join(reportdir, 'report-no-images.html'))
        assert os.path.isfile(os.path.join(reportdir, 'report.xml'))
        # report.json is generated by default
        assert os.path.isfile(os.path.join(reportdir, 'report.json'))

    @pytest.mark.slow
    def test_generate_reports_with_report_folder(self, _project_with_suite, test_utils):
        """Assert that the reports are generated in the report-folder"""
        testdir, project = _project_with_suite.activate()
        suite_name = _project_with_suite.suite_name
        os.chdir(testdir)
        timestamp = '0.1.2.3.002'
        reportdir = os.path.join(testdir, 'report-folder')
        cmd = f'golem run {project} {suite_name} -r html html-no-images junit json ' \
              f'--report-folder {reportdir} --timestamp {timestamp}'
        test_utils.run_command(cmd)
        assert os.path.isfile(os.path.join(reportdir, 'report.html'))
        assert os.path.isfile(os.path.join(reportdir, 'report-no-images.html'))
        assert os.path.isfile(os.path.join(reportdir, 'report.xml'))
        assert os.path.isfile(os.path.join(reportdir, 'report.json'))

    @pytest.mark.slow
    def test_generate_reports_with_report_folder_report_name(self, _project_with_suite,
                                                             test_utils):
        """Assert that the reports are generated in the report-folder with report-name"""
        testdir, project = _project_with_suite.activate()
        suite_name = _project_with_suite.suite_name
        os.chdir(testdir)
        timestamp = '0.1.2.3.003'
        reportdir = os.path.join(testdir, 'projects', project, 'reports', suite_name, timestamp)
        report_name = 'foo'
        cmd = f'golem run {project} {suite_name} -r html html-no-images junit json ' \
              f'--report-name {report_name} --timestamp {timestamp}'
        test_utils.run_command(cmd)
        assert os.path.isfile(os.path.join(reportdir, 'foo.html'))
        assert os.path.isfile(os.path.join(reportdir, 'foo-no-images.html'))
        assert os.path.isfile(os.path.join(reportdir, 'foo.xml'))
        assert os.path.isfile(os.path.join(reportdir, 'foo.json'))

    @pytest.mark.slow
    def test_generate_reports_with_report_folder_report_name(self, _project_with_suite,
                                                             test_utils):
        """Assert that the reports are generated in the report-folder with report-name"""
        testdir, project = _project_with_suite.activate()
        suite_name = _project_with_suite.suite_name
        os.chdir(testdir)
        timestamp = '0.1.2.3.004'
        reportdir = os.path.join(testdir, 'report-folder')
        report_name = 'foo'
        cmd = f'golem run {project} {suite_name} -r html html-no-images junit json ' \
              f'--report-folder {reportdir} --report-name {report_name} --timestamp {timestamp}'
        test_utils.run_command(cmd)
        assert os.path.isfile(os.path.join(reportdir, 'foo.html'))
        assert os.path.isfile(os.path.join(reportdir, 'foo-no-images.html'))
        assert os.path.isfile(os.path.join(reportdir, 'foo.xml'))
        assert os.path.isfile(os.path.join(reportdir, 'foo.json'))

    @pytest.mark.slow
    def test_golem_run__cli_log_level_arg(self, project_session, test_utils):
        """Set cli-log-level arg, overrides default level (INFO)"""
        path, project = project_session.activate()
        os.chdir(path)
        test_name = test_utils.random_string()
        test_content = ('def test(data):\n'
                        '  log("info msg", "INFO")\n'
                        '  log("warning msg", "WARNING")\n')
        test_utils.create_test(project, test_name, test_content)
        command = f'golem run {project} {test_name} --cli-log-level WARNING'
        result = test_utils.run_command(command)
        assert 'INFO info msg' not in result
        assert 'WARNING warning msg' in result


class TestGolemCreateProject:

    @pytest.mark.slow
    def test_golem_createproject(self, testdir_session, test_utils):
        testdir_session.activate()
        os.chdir(testdir_session.path)
        project = test_utils.random_string()
        result = test_utils.run_command(f'golem createproject {project}')
        assert result == f'Project {project} created'
        projects = test_directory.get_projects()
        assert project in projects

    @pytest.mark.slow
    def test_golem_createproject_no_args(self, testdir_session, test_utils):
        testdir_session.activate()
        os.chdir(testdir_session.path)
        result = test_utils.run_command('golem createproject')
        expected = ('usage: golem createproject [-h] project\n'
                    'golem createproject: error: the following '
                    'arguments are required: project')
        assert result == expected

    @pytest.mark.slow
    def test_golem_createproject_project_exists(self, project_session, test_utils):
        path, project = project_session.activate()
        os.chdir(path)
        result = test_utils.run_command(f'golem createproject {project}')
        expected = f"golem createproject: error: a project with name '{project}' already exists"
        assert result == expected


class TestGolemCreateSuite:

    @pytest.mark.slow
    def test_golem_createsuite(self, project_session, test_utils):
        testdir, project = project_session.activate()
        os.chdir(testdir)
        suite = test_utils.random_string()
        result = test_utils.run_command(f'golem createsuite {project} {suite}')
        assert result == f'Suite {suite} created for project {project}'
        spath = os.path.join(project_session.path, 'suites', suite+'.py')
        assert os.path.isfile(spath)

    @pytest.mark.slow
    def test_golem_createsuite_no_args(self, project_session, test_utils):
        path, _ = project_session.activate()
        os.chdir(path)
        result = test_utils.run_command('golem createsuite')
        expected = ('usage: golem createsuite [-h] project suite\n'
                    'golem createsuite: error: the following arguments '
                    'are required: project, suite')
        assert result == expected

    @pytest.mark.slow
    def test_golem_createsuite_project_does_not_exist(self, testdir_session, test_utils):
        testdir_session.activate()
        os.chdir(testdir_session.path)
        project = 'project_does_not_exist'
        suite = 'suite_test_00002'
        result = test_utils.run_command(f'golem createsuite {project} {suite}')
        expected = f'golem createsuite: error: a project with name {project} ' \
                   'does not exist'
        assert result == expected

    @pytest.mark.slow
    def test_golem_createsuite_already_exists(self, project_session, test_utils):
        path, project = project_session.activate()
        os.chdir(path)
        suite = test_utils.random_string()
        command = f'golem createsuite {project} {suite}'
        test_utils.run_command(command)
        result = test_utils.run_command(command)
        expected = 'golem createsuite: error: A suite with that name already exists'
        assert result == expected


class TestGolemCreateTest:

    @pytest.mark.slow
    def test_golem_createtest(self, project_session, test_utils):
        testdir, project = project_session.activate()
        os.chdir(testdir)
        test = test_utils.random_string()
        result = test_utils.run_command(f'golem createtest {project} {test}')
        assert result == f'Test {test} created for project {project}'
        tpath = os.path.join(project_session.path, 'tests', f'{test}.py')
        assert os.path.isfile(tpath)

    @pytest.mark.slow
    def test_golem_createtest_no_args(self, project_session, test_utils):
        path, project = project_session.activate()
        os.chdir(path)
        result = test_utils.run_command('golem createtest')
        expected = ('usage: golem createtest [-h] project test\n'
                    'golem createtest: error: the following arguments '
                    'are required: project, test')
        assert result == expected

    @pytest.mark.slow
    def test_golem_createtest_project_not_exist(self, testdir_session, test_utils):
        testdir = testdir_session.activate()
        os.chdir(testdir)
        project = 'project_not_exist'
        test = 'test_0004'
        result = test_utils.run_command(f'golem createtest {project} {test}')
        expected = f'golem createtest: error: a project with name {project} ' \
                   'does not exist'
        assert result == expected

    @pytest.mark.slow
    def test_golem_createtest_already_exists(self, project_session, test_utils):
        path, project = project_session.activate()
        os.chdir(path)
        test = test_utils.random_string()
        cmd = f'golem createtest {project} {test}'
        test_utils.run_command(cmd)
        result = test_utils.run_command(cmd)
        expected = 'golem createtest: error: A test with that name already exists'
        assert result == expected


class TestGolemFileValidation:

    @pytest.mark.slow
    def test_golem_file_does_not_exist(self, testdir_class, test_utils):
        testdir = testdir_class.activate()
        os.chdir(testdir)
        golem_file_path = os.path.join(testdir, '.golem')
        os.remove(golem_file_path)
        command = 'golem createproject project01'
        result = test_utils.run_command(command)
        assert result == errors.invalid_test_directory.format(testdir)


class TestCreateSuperUserCommand:

    @pytest.mark.slow
    def test_createsuperuser_command(self, testdir_class, test_utils):
        testdir = testdir_class.activate()
        os.chdir(testdir)
        username = test_utils.random_string(10)
        command = f'golem createsuperuser --username {username} --password 123456 --noinput'
        result = test_utils.run_command(command)
        assert result == f'Superuser {username} was created successfully.'

    @pytest.mark.slow
    def test_createsuperuser_command_noinput_missing_args(self, testdir_class, test_utils):
        """username and password are required for --noinput"""
        testdir = testdir_class.activate()
        os.chdir(testdir)
        username = test_utils.random_string(10)
        command = 'golem createsuperuser --username xxx --noinput'
        result = test_utils.run_command(command)
        assert result == 'Error: --username and --password are required for --noinput.'
        command = 'golem createsuperuser --password xxx --noinput'
        result = test_utils.run_command(command)
        assert result == 'Error: --username and --password are required for --noinput.'


class TestGolemVersion:

    @pytest.mark.slow
    def test_golem_version(self, testdir_session, test_utils):
        testdir = testdir_session.activate()
        os.chdir(testdir)
        result = test_utils.run_command('golem --version')
        assert result == f'Golem version {golem.__version__}'

    @pytest.mark.slow
    def test_golem_version_from_non_golem_dir(self, dir_function, test_utils):
        assert dir_function.path == os.getcwd()
        result = test_utils.run_command('golem -v')
        assert result == f'Golem version {golem.__version__}'
