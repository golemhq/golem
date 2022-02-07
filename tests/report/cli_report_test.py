import pytest


SUCCESS_MESSAGE = 'Test Result: SUCCESS'


class TestReportToCli:

    def test_report_to_cli_one_test_file(self, project_module, test_utils, caplog, capsys):
        _, project = project_module.activate()
        test_file = test_utils.create_random_test(project)
        suite_name = test_utils.create_suite(project, tests=[test_file])
        test_utils.run_suite(project, suite_name)
        out, err = capsys.readouterr()
        lines = out.splitlines()
        assert lines[-5] == 'Result:'
        assert lines[-4] == '------------------------------------------------------------------'
        assert test_file in lines[-3]  # cannot capture colored char
        assert lines[-2] == ''
        assert lines[-1].startswith('Total: 1 tests, 1 success in')

    def test_report_to_cli_multiple_tests(self, project_module, test_utils, caplog, capsys):
        _, project = project_module.activate()
        test_file_one = test_utils.random_string()
        code = 'def test_foo(data):\n' \
               '    assert 2 == 2\n' \
               'def test_bar(data):\n' \
               '    assert False'
        test_utils.create_test(project, test_file_one, content=code)
        suite_name = test_utils.create_suite(project, tests=[test_file_one])
        with pytest.raises(SystemExit) as w:
            test_utils.run_suite(project, suite_name)
        out, err = capsys.readouterr()
        lines = out.splitlines()
        assert lines[-16] == 'Result:'
        assert lines[-15] == '------------------------------------------------------------------'
        assert lines[-14] == test_file_one + ' '
        assert 'test_foo' in lines[-13]  # cannot capture colored char
        assert 'test_bar' in lines[-12]
        assert lines[-11] == ''
        assert lines[-10] == '1) test_bar'
        assert lines[-9] == 'AssertionError: '
        assert lines[-4] == '    assert False'
        assert lines[-3] == 'AssertionError'
        assert lines[-2] == ''
        assert 'Total: 2 tests, 1 success, 1 failure in' in lines[-1]
