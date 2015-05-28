from django.shortcuts import render

from golem.core import utils

def index(request):
    projects = utils.get_projects()
    global_settings = utils.get_global_settings()
    data = {
        'projects': projects,
        'global_settings': global_settings}
    return render(request, 'index.html', data)


def project(request, project):
    if request.method == 'GET':
        data = dict()

        #fetch projects
        projects = utils.get_projects()

        test_cases = utils.get_test_cases(project)

        suites = utils.get_suites(project)

        data = {
            'project': project,
            'projects': projects,
            'test_cases': test_cases,
            'suites': suites}
        return render(request, 'project.html', data)



def test(request, project, test):
    if request.method == 'GET':
        test_case = list()
        data = dict()

        #fetch projects
        projects = utils.get_projects()

        #fetch selected test case if selected test case is defined
        test_case = utils.get_selected_test_case(project, test)


        #fetch test data file
        test_data = utils.get_test_data(project, test)

        print test_data
        data = {
            'projects': projects,
            'test_case': test_case,
            'selected_test_case': test,
            'project': project,
            'test_data': test_data}
        return render(request, 'test.html', data)

def suite(request, project, suite):
    if request.method == 'GET':
        tests = list()
        data = dict()
        suite_data = dict()

        #fetch projects ##repeated in each view...
        projects = utils.get_projects()

        #fetch suite test cases
        tests = utils.get_suite_test_cases(project, suite)

        #fetch suite test data
        #suite_data = utils.get_test_data(project, test) not yet


        data = {
            'projects': projects,
            'tests': tests,
            'suite_data': suite_data,
            'project': project,
            'suite': suite}
        return render(request, 'suite.html', data)










