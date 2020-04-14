import os
import shutil

from golem.core import session
from golem.core.project import Project


def get_last_executions(projects=None, suite=None, limit=5):
    """Get the last n executions.

    Get the executions of one suite or all the suites,
    one project or all the projects.

    Returns a list of executions (timestamps strings)
    ordered in descendant order by execution time and
    limited by `limit`
    """
    last_execution_data = {}
    path = os.path.join(session.testdir, 'projects')
    # if no projects provided, search every project
    if not projects:
        projects = next(os.walk(path))[1]
    for project in projects:
        last_execution_data[project] = {}
        report_path = os.path.join(path, project, 'reports')
        executed_suites = []
        # use one suite or all the suites
        if suite:
            if os.path.isdir(os.path.join(report_path, suite)):
                executed_suites = [suite]
        else:
            executed_suites = next(os.walk(report_path))[1]
            executed_suites = [x for x in executed_suites if x != 'single_tests']
        for s in executed_suites:
            suite_path = os.path.join(report_path, s)
            suite_executions = next(os.walk(suite_path))[1]
            last_executions = sorted(suite_executions)
            limit = int(limit)
            last_executions = last_executions[-limit:]
            if len(last_executions):
                last_execution_data[project][s] = last_executions
    return last_execution_data


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


def suite_execution_path(project, suite, execution):
    return os.path.join(Project(project).report_directory_path, suite, execution)