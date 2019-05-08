"""The Golem GUI web application"""
import os
import sys

from flask import Flask, g, render_template
from flask_login import current_user, LoginManager

import golem
from . import gui_utils, report_parser, user
from .gui_utils import (project_exists, gui_permissions_required,
                        report_permissions_required)
from golem.core import session, settings_manager, utils, errors
from .api import api_bp
from .web_app import webapp_bp
from .report import report_bp


def create_app():
    """Call this function to create a Golem GUI app object.
    If called externally (e.g.: from a WSGI server) the cwd
    should be a valid Golem test directory"""
    if not session.testdir:
        testdir = os.getcwd()
        if not utils.is_valid_test_directory(testdir):
            sys.exit(errors.invalid_test_directory.format(testdir))
        else:
            session.testdir = testdir
    if not session.settings:
        session.settings = settings_manager.get_global_settings()
    app = Flask(__name__)
    app.secret_key = gui_utils.get_secret_key()
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['GOLEM_VERSION'] = golem.__version__
    login_manager = LoginManager()
    login_manager.login_view = 'webapp.login'
    login_manager.init_app(app)
    app.register_blueprint(webapp_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(api_bp)

    @login_manager.user_loader
    def load_user(user_id):
        return user.get_user_from_id(user_id)

    # @login_manager.unauthorized_handler
    # def unauthorized_callback():
    #     return redirect('/login/?next=' + request.path)

    @app.before_request
    def before_request():
        g.user = current_user

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('404.html', message=error.description), 404

    return app
