from flask_dance.consumer import OAuth2ConsumerBlueprint
from functools import partial
from flask.globals import LocalProxy, _lookup_app_object
try:
        from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack

def make_haavard_blueprint(
        client_id=None, client_secret=None, scope=None, redirect_url=None,
        redirect_to=None, login_url=None, authorized_url=None,
        session_class=None, storage=None):

    haavard_oauth_bp = OAuth2ConsumerBlueprint(
            "oauth_haavard", __name__,
            client_id = client_id,
            client_secret = client_secret,
            scope=scope,
            base_url = 'https://haavard.name',
            token_url = 'https://haavard.name/oauth/token/',
            authorization_url = 'https://haavard.name/oauth/authorize/',
            redirect_url=redirect_url,
            redirect_to=redirect_to,
            login_url=login_url,
            authorized_url=authorized_url,
            session_class=session_class,
            storage=storage,
    )
    haavard_oauth_bp.from_config['client_id'] = 'HAAVARD_OAUTH_CLIENT_ID'
    haavard_oauth_bp.from_config['client_secret'] = 'HAAVARD_OAUTH_CLIENT_SECRET'

    @haavard_oauth_bp.before_app_request
    def set_applocal_session():
        ctx = stack.top
        ctx.haavard_oauth = haavard_oauth_bp.session

    return haavard_oauth_bp
    
haavard = LocalProxy(partial(_lookup_app_object, "haavard_oauth"))
