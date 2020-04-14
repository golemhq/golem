import os

from golem.report import report


class TestGetLastExecution:

    def test_get_last_executions(self, project_function, test_utils):
        _, project = project_function.activate()

        # suite does not exist
        last_exec = report.get_last_executions([project], 'suite_does_not_exist')
        assert last_exec[project] == {}

        # suite with no executions
        suite_name = 'suite1'
        test_utils.create_test(project, name='test1')
        test_utils.create_suite(project, name=suite_name, tests=['test1'])

        assert last_exec[project] == {}

        # suite with one execution
        timestamp = test_utils.run_suite(project, suite_name)
        last_exec = report.get_last_executions([project], suite_name)
        assert last_exec[project] == {suite_name: [timestamp]}

        # multiple executions
        timestamps = [timestamp]
        timestamps.append(test_utils.run_suite(project, suite_name))
        timestamps.append(test_utils.run_suite(project, suite_name))
        last_exec = report.get_last_executions([project], suite_name, limit=2)
        assert len(last_exec[project][suite_name]) == 2
        assert last_exec[project][suite_name][0] == timestamps[1]
        assert last_exec[project][suite_name][1] == timestamps[2]


class TestDeleteExecution:

    def test_delete_execution(self, project_class, test_utils):
        _, project = project_class.activate()
        execution = test_utils.execute_random_suite(project)
        assert os.path.isdir(execution['exec_dir'])

        errors = report.delete_execution(project, execution['suite_name'], execution['timestamp'])

        assert errors == []
        assert not os.path.isdir(execution['exec_dir'])
