import pytest
from juleol import db

def test_index(client):
    ret = client.get('/')
    assert ret.status_code == 200
    assert b'/result/2000' in ret.data
    assert b'Enter rating' not in ret.data

def test_login(client):
    ret = client.post("/login", data={'name': 'test', 'password': 'test', 'year': '2000'})
    assert ret.status_code == 302
    ret = client.get('/')
    assert b'Enter rating' in ret.data
    ret = client.get('/logout')
    assert ret.status_code == 302
    ret = client.get('/')
    assert b'Enter rating' not in ret.data

def test_login_fail(client):
    ret = client.post("/login", data={'name': 'test', 'password': 'bogus', 'year': '2000'})
    assert ret.status_code == 200
    assert b'Invalid user or password' in ret.data
    ret = client.post("/login", data={'name': 'bogus', 'password': 'bogus', 'year': '2000'})
    assert ret.status_code == 200
    assert b'Invalid user or password' in ret.data

def test_rate(client):
    ret = client.get('/rate/2000')
    assert ret.status_code == 302
    assert ret.headers['Location'] == 'http://localhost/login'
    ret = client.post("/login", data={'name': 'test', 'password': 'test', 'year': '2000'})
    ret = client.get('/rate/2000')
    assert ret.status_code == 200
    ret = client.get('/rate/2001')
    assert ret.status_code == 302
