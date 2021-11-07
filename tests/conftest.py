# SPDX-FileCopyrightText: 2020 Håvard Moen <post@haavard.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import pytest

from betamax import Betamax
from betamax_serializers import pretty_json
import juleol
import juleol.db
from flask import current_app
from flask_dance.consumer.storage import MemoryStorage
from flask_dance.contrib.google import google
from unittest.mock import patch, MagicMock, Mock

GOOGLE_OAUTH_TOKEN = '{"access_token": "test-token"}'

logging.basicConfig(level=logging.DEBUG)


Betamax.register_serializer(pretty_json.PrettyJSONSerializer)
with Betamax.configure() as config:
    config.cassette_library_dir = "tests/cassettes"
    config.define_cassette_placeholder("<AUTH_TOKEN>", GOOGLE_OAUTH_TOKEN)
    config.default_cassette_options["serialize_with"] = "prettyjson"


class TestConfig(object):
    TESTING = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    ENV = "test"
    SECRET_KEY = "test"


@pytest.fixture
def app():
    app = juleol.create_app(TestConfig)
    return app


@pytest.fixture
def betamax_google(app, request):
    @app.before_request
    def wrap_google_with_betamax():
        recorder = Betamax(app.config["user_oauth"])
        # add record='all' to record new session
        recorder.use_cassette("client_authorized")
        recorder.start()

        @app.after_request
        def unwrap(response):
            recorder.stop()
            return response

    return app


@pytest.fixture
def betamax_google_fail(app, request):
    @app.before_request
    def wrap_google_with_betamax():
        recorder = Betamax(app.config["user_oauth"])
        # add record='all' to record new session
        recorder.use_cassette("client_authorized_fail")
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
        with patch("juleol.db.Participants") as MockParticipants:
            with patch("juleol.db.Tastings") as MockTastings:
                test_tasting = juleol.db.Tastings()
                test_tasting.year = 2000
                MockTastings.query.all.return_value = [test_tasting]
                MockTastings.query.filter.return_value.first.return_value = test_tasting
                MockTastings.query.filter.return_value.filter.return_value.first.return_value = (
                    test_tasting
                )

                test_participant = juleol.db.Participants()
                test_participant.id = 1
                test_participant.name = "test"
                test_participant.email = "test@example.com"
                test_participant.tasting = test_tasting
                MockParticipants.query.filter.return_value.first.return_value = (
                    test_participant
                )
                MockParticipants.query.filter.return_value.filter.return_value.first.return_value = (
                    test_participant
                )

                yield client


@pytest.fixture
def client_invalid_email(app):
    client = app.test_client()

    with app.app_context():
        with patch("juleol.db.Participants") as MockParticipants:
            with patch("juleol.db.Tastings") as MockTastings:
                test_tasting = juleol.db.Tastings()
                test_tasting.year = 2000
                MockTastings.query.all.return_value = [test_tasting]
                MockTastings.query.filter.return_value.first.return_value = test_tasting
                MockTastings.query.filter.return_value.filter.return_value.first.return_value = (
                    test_tasting
                )

                MockParticipants.query.filter.return_value.first.return_value = None
                MockParticipants.query.filter.return_value.filter.return_value.first.return_value = (
                    None
                )

                yield client


@pytest.fixture
def client_authorized(client, monkeypatch):
    storage = MemoryStorage({"access_token": GOOGLE_OAUTH_TOKEN})
    monkeypatch.setattr(current_app.blueprints["google"], "storage", storage)

    with client.session_transaction() as sess:
        sess["_user_id"] = 1

    yield client


@pytest.fixture
def admin_client(app, monkeypatch):
    client = app.test_client()

    with app.app_context():
        storage = MemoryStorage({"access_token": "fake-token"})
        monkeypatch.setattr(app.blueprints["github"], "storage", storage)

        yield client


@pytest.fixture
def admin_noauth_client(app, monkeypatch):
    client = app.test_client()

    with app.app_context():
        storage = MemoryStorage()
        monkeypatch.setattr(app.blueprints["github"], "storage", storage)

        yield client
