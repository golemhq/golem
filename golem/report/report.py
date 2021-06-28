import os
import shutil

from golem.core import test_directory
from golem.core.project import Project
from golem.report.execution_report import execution_report_path


def get_last_execution_timestamps(projects=None, execution=None, limit=5):
    """Get the last n execution timestamps from all the executions of
    a list of projects.

    If projects is not provided, all projects will be selected.
    If execution is provided, projects should be a list of one.

    Timestamps are in descending order.
    """
    last_timestamps = {}
    # if no projects provided, select every project
    if not projects:
        projects = test_directory.get_projects()
    for project in projects:
        last_timestamps[project] = {}
        report_path = Project(project).report_directory_path
        executions = []
        # if execution is not provided, select all executions
        if execution:
            if os.path.isdir(os.path.join(report_path, execution)):
                executions = [execution]
        else:
            executions = next(os.walk(report_path))[1]
        for e in executions:
            exec_path = os.path.join(report_path, e)
            timestamps = next(os.walk(exec_path))[1]
            timestamps = sorted(timestamps)
            limit = int(limit)
            timestamps = timestamps[-limit:]
            if len(timestamps):
                last_timestamps[project][e] = timestamps
            else:
                last_timestamps[project][e] = []
    return last_timestamps


def delete_execution(project, execution):
    errors = []
    path = os.path.join(Project(project).report_directory_path, execution)
    if os.path.isdir(path):
        try:
            shutil.rmtree(path)
        except Exception as e:
            errors.append(repr(e))
    else:
        errors.append('Execution {} of project {} does not exist'.format(execution, project))
    return errors


def delete_execution_timestamp(project, execution, timestamp):
    errors = []
    path = execution_report_path(project, execution, timestamp)
    if os.path.isdir(path):
        try:
            shutil.rmtree(path)
        except Exception as e:
            errors.append(repr(e))
    else:
        errors.append('Execution for {} {} {} does not exist'
                      .format(project, execution, timestamp))
    return errors
