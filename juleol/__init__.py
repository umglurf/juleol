from flask import Flask
from flask_migrate import Migrate
from flask_dance.contrib.github import make_github_blueprint, github
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
    # Change these two lines to use another authentication
    # also modify the login_required function in admin.py
    if app.config.get('OAUTH_PROVIDER', 'github') == 'oauth-generic':
        oauth_bp = oauth_generic.make_oauth_blueprint(redirect_to="admin.admin_index")
        app.config['oauth'] = juleol.oauth_generic.oauth
        app.config['oauth_login'] = 'oauth_generic.login'
    elif app.config.get('OAUTH_PROVIDER', 'github') == 'github':
        oauth_bp = make_github_blueprint(redirect_to="admin.admin_index")
        app.config['oauth'] = github
        app.config['oauth_login'] = 'github.login'
    else:
        raise Exception('Unknown oauth provider configured')
    app.register_blueprint(oauth_bp, url_prefix="/admin/login")

    db.db.init_app(app)
    migrate = Migrate(app, db.db)

    return app
