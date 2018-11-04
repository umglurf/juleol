import pytest
import juleol
import juleol.db
from flask_bcrypt import Bcrypt

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
    
    bcrypt = Bcrypt()
    with app.app_context():
        juleol.db.db.create_all()
        tasting = juleol.db.Tastings(year=2000)
        juleol.db.db.session.add(tasting)
        participant = juleol.db.Participants(tasting = tasting, name = 'test', password = bcrypt.generate_password_hash('test'))
        juleol.db.db.session.add(participant)
        juleol.db.db.session.commit()
        
    yield client
