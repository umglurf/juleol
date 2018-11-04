from flask import Flask
import os

def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object('juleol.default_config')
    if 'JULEOL_SETTINGS' in os.environ:
        app.config.from_envvar('JULEOL_SETTINGS')

    if test_config:
        app.config.from_object(test_config)

    from juleol import admin, db, view, haavard
    app.register_blueprint(admin.bp)
    app.register_blueprint(view.bp)
    # Change these to lines to use another authentication
    haavard_bp = haavard.make_haavard_blueprint(redirect_to="admin.admin_index")
    app.register_blueprint(haavard_bp, url_prefix="/admin/login")

    db.db.init_app(app)

    return app