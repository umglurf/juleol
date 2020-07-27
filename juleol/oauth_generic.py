from flask_dance.consumer import OAuth2ConsumerBlueprint
from functools import partial
from flask.globals import LocalProxy, _lookup_app_object
try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack


def make_oauth_blueprint(
        client_id=None, client_secret=None, scope=None, redirect_url=None,
        redirect_to=None, login_url=None, authorized_url=None,
        session_class=None, storage=None):

    oauth_generic_bp = OAuth2ConsumerBlueprint(
        "oauth_generic", __name__,
        client_id=client_id,
        client_secret=client_secret,
        scope=scope,
        redirect_url=redirect_url,
        redirect_to=redirect_to,
        login_url=login_url,
        authorized_url=authorized_url,
        session_class=session_class,
        storage=storage,
    )
    oauth_generic_bp.from_config['authorization_url'] = 'OAUTH_AUTHORIZATION_URL'
    oauth_generic_bp.from_config['token_url'] = 'OAUTH_TOKEN_URL'
    oauth_generic_bp.from_config['client_id'] = 'OAUTH_CLIENT_ID'
    oauth_generic_bp.from_config['client_secret'] = 'OAUTH_CLIENT_SECRET'

    @oauth_generic_bp.before_app_request
    def set_applocal_session():
        ctx = stack.top
        ctx.oauth_generic = oauth_generic_bp.session

    return oauth_generic_bp


oauth = LocalProxy(partial(_lookup_app_object, "oauth_generic"))
