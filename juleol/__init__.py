# SPDX-FileCopyrightText: 2020 Håvard Moen <post@haavard.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import Flask
from flask_migrate import Migrate
from flask_dance.contrib.github import make_github_blueprint, github
from flask_dance.contrib.google import make_google_blueprint, google
import juleol.oauth_generic
import os


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object('juleol.default_config')
    if 'JULEOL_SETTINGS' in os.environ:
        app.config.from_envvar('JULEOL_SETTINGS')

    if test_config:
        app.config.from_object(test_config)

    from juleol import admin, db, view, oauth_generic
    app.register_blueprint(admin.bp)
    app.register_blueprint(view.bp)

    if app.config.get('ADMIN_OAUTH_PROVIDER', 'github') == 'oauth-generic':
        admin_oauth_bp = oauth_generic.make_oauth_blueprint(redirect_to="admin.admin_index")
        app.config['admin_oauth'] = juleol.oauth_generic.oauth
        app.config['admin_oauth_login'] = 'oauth_generic.login'
    elif app.config.get('ADMIN_OAUTH_PROVIDER', 'github') == 'github':
        admin_oauth_bp = make_github_blueprint(redirect_to="admin.admin_index")
        app.config['admin_oauth'] = github
        app.config['admin_oauth_login'] = 'github.login'
    else:
        raise Exception('Unknown admin oauth provider configured')
    app.register_blueprint(admin_oauth_bp, url_prefix="/admin/login")

    if app.config.get('USER_OAUTH_PROVIDER', 'google') == 'google':
        user_oauth_bp = make_google_blueprint(redirect_to='view.login', scope="openid https://www.googleapis.com/auth/userinfo.email")
        app.config['user_oauth'] = google
        app.config['user_oauth_login'] = 'google.login'
    else:
        raise Exception('Unknown user oauth provider configured')
    app.register_blueprint(user_oauth_bp, url_prefix="/login")

    db.db.init_app(app)
    Migrate(app, db.db)

    return app
