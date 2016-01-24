from flask import Flask, render_template

app = Flask(__name__)

from golem.core import utils

@app.route("/")
def home():
    projects = utils.get_projects()
    global_settings = utils.get_global_settings()
    data = {
        'projects': projects,
        'global_settings': global_settings}
    return render_template('index.html', data=data)


@app.route("/project/<project>/")
def project(project):

    projects = utils.get_projects()
    
    test_cases = utils.get_test_cases(project)

    suites = utils.get_suites(project)

    #global_settings = utils.get_global_settings()
    data = {
    	'project': project,
        'projects': projects,
        'test_cases': test_cases,
        'suites': suites}
    return render_template('project.html', data=data)

@app.route("/project/<project>/test/<selected_test_case>/")
def test_case(project, selected_test_case):
    test_case = list()
    data = dict()
    #fetch projects
    projects = utils.get_projects()
    #fetch selected test case
    test_case = utils.get_selected_test_case(project, selected_test_case) #fix if selected test case does not exists
    #fetch test case data file
    test_data = utils.get_test_data(project, selected_test_case)
    data = {
        'projects': projects,
        'test_case': test_case,
        'selected_test_case': selected_test_case,
        'project': project,
        'test_data': test_data}
    return render_template('test.html', data=data)

if __name__ == "__main__":
    app.run(debug=True)