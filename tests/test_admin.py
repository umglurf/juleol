import json
from juleol import db
import pytest
from sqlalchemy import exc
from unittest.mock import patch, MagicMock

def test_login(admin_noauth_client, monkeypatch):
    ret = admin_noauth_client.get('/admin/')
    assert ret.status_code == 302
