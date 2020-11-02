import pytest
from betamax import Betamax
import juleol
import juleol.db
from flask import current_app
from flask_dance.consumer.storage import MemoryStorage
from flask_dance.contrib.google import google
from unittest.mock import patch, MagicMock

GOOGLE_OAUTH_TOKEN = 'fake-token'

with Betamax.configure() as config:
    config.cassette_library_dir = "tests/cassettes"
    config.define_cassette_placeholder("<AUTH_TOKEN>", GOOGLE_OAUTH_TOKEN)

class TestConfig(object):
    TESTING = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    ENV = 'test'
    SECRET_KEY = 'test'

@pytest.fixture
def app():
    app = juleol.create_app(TestConfig)
    return app

@pytest.fixture
def betamax_google(app, request):
    @app.before_request
    def wrap_google_with_betamax():
        recorder = Betamax(app.config['user_oauth'])
        # add record='all' to record new session
        recorder.use_cassette("client_authorized")
        recorder.start()

        @app.after_request
        def unwrap(response):
            recorder.stop()
            return response
    return app


@pytest.fixture
def client(app):
    client = app.test_client()

    with app.app_context():
        with patch('juleol.db.Participants') as MockParticipants:
            with patch('juleol.db.Tastings') as MockTastings:
                test_tasting = juleol.db.Tastings()
                test_tasting.year = 2000
                MockTastings.query.all.return_value = [test_tasting]
                MockTastings.query.filter.return_value.first.return_value = test_tasting
                MockTastings.query.filter.return_value.filter.return_value.first.return_value = test_tasting

                test_participant = juleol.db.Participants()
                test_participant.id = 1
                test_participant.name = 'test'
                test_participant.email = 'test@example.com'
                test_participant.tasting = test_tasting
                MockParticipants.query.filter.return_value.first.return_value = test_participant
                MockParticipants.query.filter.return_value.filter.return_value.first.return_value = test_participant

                yield client

@pytest.fixture
def client_invalid_email(app):
    client = app.test_client()

    with app.app_context():
        with patch('juleol.db.Participants') as MockParticipants:
            with patch('juleol.db.Tastings') as MockTastings:
                test_tasting = juleol.db.Tastings()
                test_tasting.year = 2000
                MockTastings.query.all.return_value = [test_tasting]
                MockTastings.query.filter.return_value.first.return_value = test_tasting
                MockTastings.query.filter.return_value.filter.return_value.first.return_value = test_tasting

                MockParticipants.query.filter.return_value.first.return_value = None
                MockParticipants.query.filter.return_value.filter.return_value.first.return_value = None

                yield client


@pytest.fixture
def client_authorized(client, monkeypatch):
    storage = MemoryStorage({"access_token": GOOGLE_OAUTH_TOKEN})
    monkeypatch.setattr(current_app.blueprints['google'], "storage", storage)

    yield client


@pytest.fixture
def admin_client(app, monkeypatch):
    client = app.test_client()

    with app.app_context():
        storage = MemoryStorage({"access_token": "fake-token"})
        monkeypatch.setattr(app.blueprints['github'], "storage", storage)

        yield client


@pytest.fixture
def admin_noauth_client(app, monkeypatch):
    client = app.test_client()

    with app.app_context():
        storage = MemoryStorage()
        monkeypatch.setattr(app.blueprints['github'], "storage", storage)

        yield client
