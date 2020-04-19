import os
import shutil

from golem.core import test_directory
from golem.core.project import Project
from golem.report.execution_report import suite_execution_path


def get_last_executions(projects=None, suite=None, limit=5):
    """Get the last n executions from all the suites of
    a list of projects.

    If projects is not provided, all projects will be selected.
    If suite is provided, projects should be a list of one.
    Returns a list of executions (timestamps strings)
    in descending order for each suite with executions
    for each selected project.
    """
    last_executions = {}
    # if no projects provided, select every project
    if not projects:
        projects = test_directory.get_projects()
    for project in projects:
        last_executions[project] = {}
        report_path = Project(project).report_directory_path
        executed_suites = []
        # if suite is not provided, select all suites with executions
        if suite:
            if os.path.isdir(os.path.join(report_path, suite)):
                executed_suites = [suite]
        else:
            executed_suites = next(os.walk(report_path))[1]
            executed_suites = [x for x in executed_suites if x != 'single_tests']
        for s in executed_suites:
            suite_path = os.path.join(report_path, s)
            suite_executions = next(os.walk(suite_path))[1]
            suite_executions = sorted(suite_executions)
            limit = int(limit)
            suite_executions = suite_executions[-limit:]
            if len(suite_executions):
                last_executions[project][s] = suite_executions
            else:
                last_executions[project][s] = []
    return last_executions


def is_execution_finished(path, sets):
    """Is a suite execution finished.

    It is considered finished when all the tests contain
    a `report.json` file
    """
    if sets:
        is_finished = True
        for data_set in sets:
            report_path = os.path.join(path, data_set, 'report.json')
            if not os.path.exists(report_path):
                is_finished = False
    else:
        is_finished = False
    return is_finished


def delete_execution(project, suite, execution):
    errors = []
    path = suite_execution_path(project, suite, execution)
    if os.path.isdir(path):
        try:
            shutil.rmtree(path)
        except:
            pass
    else:
        errors.append('Execution for {} {} {} does not exist'.format(project, suite, execution))
    return errors
