from flask import Flask, render_template

app = Flask(__name__)

from golem.core import utils

@app.route("/")
def hello():
    projects = utils.get_projects()
    global_settings = utils.get_global_settings()
    data = {
        'projects': projects,
        'global_settings': global_settings}
    return render_template('index.html', data)

if __name__ == "__main__":
    app.run(debug=True)