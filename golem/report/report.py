import os
import shutil
from datetime import datetime, timedelta

from golem.core import test_directory
from golem.core.project import Project
from golem.report.execution_report import execution_report_path
from golem.core import utils


def get_last_execution_timestamps(projects=None, execution=None, limit=None, last_days=None):
    """Get the last n execution timestamps from all the executions of
    a list of projects.

    If projects is not provided, all projects will be selected.
    If execution is provided, projects should be a list of one.

    Timestamps are in descending order.
    """
    start_timestamp = None
    if last_days is not None and last_days != 0:
        start_datetime = datetime.today() - timedelta(days=last_days)
        start_timestamp = utils.get_timestamp(start_datetime)

    last_timestamps = {}
    # if no projects provided, select every project
    if not projects:
        projects = test_directory.get_projects()
    for project in projects:
        last_timestamps[project] = {}
        report_path = Project(project).report_directory_path
        # if execution is not provided, select all executions
        if execution and os.path.isdir(os.path.join(report_path, execution)):
            executions = [execution]
        else:
            executions = next(os.walk(report_path))[1]
        for e in executions:
            exec_path = os.path.join(report_path, e)
            timestamps = next(os.walk(exec_path))[1]
            timestamps = sorted(timestamps, reverse=True)
            if limit is not None:
                limit = int(limit)
                timestamps = timestamps[:limit]
            if start_timestamp is not None:
                timestamps = [t for t in timestamps if t >= start_timestamp]
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
        errors.append(f'Execution {execution} of project {project} does not exist')
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
        errors.append(f'Execution for {project} {execution} {timestamp} does not exist')
    return errors
