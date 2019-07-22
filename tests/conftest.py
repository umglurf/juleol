import pytest
import juleol
import juleol.db
from unittest.mock import patch

class TestConfig(object):
  DEBUG = True
  TESTING = True
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
  ENV = 'test'
  SECRET_KEY = 'test'

@pytest.fixture
def client():
    app = juleol.create_app(TestConfig)
    client = app.test_client()
    
    with app.app_context():
        with patch('juleol.db.Participants') as MockParticipant:
            with patch('juleol.db.Tastings') as MockTastings:
                from flask_bcrypt import Bcrypt
                bcrypt = Bcrypt()

                test_tasting = juleol.db.Tastings()
                test_tasting.year = 2000
                MockTastings.query.all.return_value = [test_tasting]
                MockTastings.query.filter.return_value.first.return_value = test_tasting
                MockTastings.query.filter.return_value.filter.return_value.first.return_value = test_tasting

                test_participant = juleol.db.Participants()
                test_participant.id = 1
                test_participant.name = 'test'
                test_participant.password = bcrypt.generate_password_hash('test')
                test_participant.tasting = test_tasting
                MockParticipant.query.filter.return_value.first.return_value = test_participant
                MockParticipant.query.filter.return_value.filter.return_value.first.return_value = test_participant
    
                yield client
