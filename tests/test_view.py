import pytest
import json
from juleol import db
from sqlalchemy import exc
from unittest.mock import patch, MagicMock

def test_index(client):
    with patch('juleol.db.Tastings') as MockTastings:
        test_tasting = db.Tastings()
        test_tasting.year = 2000
        MockTastings.query.all.return_value = [test_tasting]
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
    #test invalid password
    ret = client.post("/login", data={'name': 'test', 'password': 'bogus', 'year': '2000'})
    assert ret.status_code == 200
    assert b'Invalid user or password' in ret.data

    #test invalid username
    ret = client.post("/login", data={'name': 'bogus', 'password': 'bogus', 'year': '2000'})
    assert ret.status_code == 200
    assert b'Invalid user or password' in ret.data

    #test invalid year
    ret = client.post("/login", data={'name': 'test', 'password': 'test', 'year': '200'})
    assert ret.status_code == 200
    assert b'Not a valid choice' in ret.data

    #test if participant: path
    db.Participants.query.filter.return_value.filter.return_value.first.return_value = None
    ret = client.post("/login", data={'name': 'test', 'password': 'test', 'year': '2000'})
    assert ret.status_code == 200
    assert b'Invalid user or password' in ret.data

def test_invalid_userid_in_session(client):
    ret = client.post("/login", data={'name': 'test', 'password': 'test', 'year': '2000'})
    assert ret.status_code == 302
    ret = client.get('/rate/2000')
    assert ret.status_code == 200
    db.Participants.query.filter.return_value.first.return_value = None
    ret = client.get('/rate/2000')
    assert ret.status_code == 302

def test_result(client):
    beer_sum = MagicMock()
    beer_sum.name = 'test'
    beer_sum.number = 1
    beer_sum.sum = 10
    beer_sum.avg = 42
    beer_sum.std = 13
    beer_sum.heat_id = None
    beer_sum2 = MagicMock()
    beer_sum2.name = 'test 2'
    beer_sum2.number = 2
    beer_sum2.sum = 10
    beer_sum2.avg = 42
    beer_sum2.std = 13
    beer_sum2.heat_id = 1
    participant = MagicMock()
    participant.id = 1
    participant.name = 'foo'
    db.Participants.query.filter.return_value.all.return_value = [participant]
    with patch('juleol.db.get_beer_scores', return_value = {
        'totals': [
            beer_sum,
            beer_sum2
        ],
        'details': []
        }):

        ret = client.get('/result/2000', headers={'Content-Type': 'application/json'})
        assert ret.status_code == 200
        data = json.loads(ret.data)
        assert 'beer_scores' in data
        assert 'participants' in data
        assert len(data['beer_scores']) == 2
        assert data['beer_scores']['1']['name'] == 'test'
        assert data['beer_scores']['1']['sum'] == 10
        assert data['beer_scores']['1']['average'] == 42
        assert data['beer_scores']['1']['stddev'] == 13
        assert data['participants']['1']['name'] == 'foo'

        ret = client.get('/result/2000')
        assert ret.status_code == 200
        assert b'<tr id="beer_1">' in ret.data
        assert b'<td>1</td>' in ret.data
        assert b'<td>10</td>' in ret.data
        assert b'<td>42.00</td>' in ret.data
        assert b'<td>13.00</td>' in ret.data
        assert b'<tr id="beer_2">' in ret.data

        ret = client.get('/result/2000?heat=1', headers={'Content-Type': 'application/json'})
        assert ret.status_code == 200
        data = json.loads(ret.data)
        assert 'beer_scores' in data
        assert 'participants' in data
        assert len(data['beer_scores']) == 1


def test_invalid_result_year(client):
    db.Tastings.query.filter.return_value.first.return_value = None
    ret = client.get('/result/1000')
    assert ret.status_code == 302
    assert ret.headers['Location'] == 'http://localhost/'

def test_result_participant(client):
    score = MagicMock()
    score.number = 1
    score.name = 'test 1'
    score.look = 1
    score.smell = 1
    score.taste = 1
    score.aftertaste = 1
    score.xmas = 1
    score.heat_id = None
    score2 = MagicMock()
    score2.number = 1
    score2.name = 'test 2'
    score2.look = 1
    score2.smell = 1
    score2.taste = 1
    score2.aftertaste = 1
    score2.xmas = 1
    score2.heat_id = 1
    score2.heat_name = 'test'
    with patch('juleol.db.participant_scores', return_value = [
        score,
        score2
        ]):
        ret = client.get('/result/2000/1')
        assert ret.status_code == 200
        assert b'<td>test 1</td>' in ret.data
        assert b'<td>test 2</td>' in ret.data

        ret = client.get('/result/2000/1?heat=1')
        assert ret.status_code == 200
        assert not b'<td>test 1</td>' in ret.data
        assert b'<td>test 2</td>' in ret.data

def test_result_invalid_participant(client):
    db.Participants.query.join.return_value.filter.return_value.filter.return_value.one.return_value = None
    ret = client.get('/result/2000/1')
    assert ret.status_code == 302
    assert ret.headers['Location'] == 'http://localhost/'

def test_rate(client):
    ret = client.get('/rate/2000')
    assert ret.status_code == 302
    assert ret.headers['Location'] == 'http://localhost/login'
    ret = client.post("/login", data={'name': 'test', 'password': 'test', 'year': '2000'})
    ret = client.get('/rate/2000')
    assert ret.status_code == 200

    ret = client.get('/rate/2001')
    assert ret.status_code == 302

def test_rate_invalid_year(client):
    ret = client.post("/login", data={'name': 'test', 'password': 'test', 'year': '2000'})
    ret = client.get('/rate/1000/1')
    assert ret.status_code == 400

def test_rate_invalid_beer(client):
    with patch('juleol.db.Beers') as MockBeers:
        ret = client.post("/login", data={'name': 'test', 'password': 'test', 'year': '2000'})
        MockBeers.query.filter.return_value.filter.return_value.first.return_value = None
        ret = client.get('/rate/2000/1')
        assert ret.status_code == 400

def test_get_rate_beer(client):
    ret = client.post("/login", data={'name': 'test', 'password': 'test', 'year': '2000'})
    with patch('juleol.db.Beers') as MockBeers:
        with patch('juleol.db.ScoreTaste') as MockScoreTaste:
            with patch('juleol.db.ScoreAftertaste') as MockScoreAfterTaste:
                with patch('juleol.db.ScoreLook') as MockScoreLook:
                    with patch('juleol.db.ScoreSmell') as MockScoreSmell:
                        with patch('juleol.db.ScoreXmas') as MockScoreXmas:
                            test_beer = db.Beers()
                            test_beer.id = 1
                            test_beer.name = 'test'
                            db.Beers.query.filter.return_value.filter.return_value.first.return_value = test_beer
                            test_score = MagicMock()
                            test_score.score = 10
                            db.ScoreTaste.query.filter.return_value.filter.return_value.first.return_value = test_score
                            db.ScoreAftertaste.query.filter.return_value.filter.return_value.first.return_value = test_score
                            db.ScoreLook.query.filter.return_value.filter.return_value.first.return_value = test_score
                            db.ScoreSmell.query.filter.return_value.filter.return_value.first.return_value = test_score
                            db.ScoreXmas.query.filter.return_value.filter.return_value.first.return_value = test_score
                            ret = client.get('/rate/2000/1')
                            assert ret.status_code == 200
                            data = json.loads(ret.data)
                            assert data['taste'] == 10
                            assert data['aftertaste'] == 10
                            assert data['look'] == 10
                            assert data['smell'] == 10
                            assert data['xmas'] == 10

def test_put_rate_beer(client):
    ret = client.post("/login", data={'name': 'test', 'password': 'test', 'year': '2000'})
    with patch('juleol.db.Beers') as MockBeers:
        with patch('juleol.db.ScoreTaste') as MockScoreTaste:
            with patch('juleol.db.ScoreAftertaste') as MockScoreAfterTaste:
                with patch('juleol.db.ScoreLook') as MockScoreLook:
                    with patch('juleol.db.ScoreSmell') as MockScoreSmell:
                        with patch('juleol.db.ScoreXmas') as MockScoreXmas:
                            test_beer = db.Beers()
                            test_beer.id = 1
                            test_beer.name = 'test'
                            db.Beers.query.filter.return_value.filter.return_value.first.return_value = test_beer
                            test_score = MagicMock()
                            test_score.score = 0
                            db.ScoreTaste.query.filter.return_value.filter.return_value.first.return_value = test_score
                            db.ScoreAftertaste.query.filter.return_value.filter.return_value.first.return_value = test_score
                            db.ScoreLook.query.filter.return_value.filter.return_value.first.return_value = test_score
                            db.ScoreSmell.query.filter.return_value.filter.return_value.first.return_value = test_score
                            db.ScoreXmas.query.filter.return_value.filter.return_value.first.return_value = test_score

                            ret = client.put('/rate/2000/1', data={'look': 'bogus'})
                            assert ret.status_code == 400
                            assert b'Not a valid integer value' in ret.data
                            ret = client.put('/rate/2000/1', data={'smell': 10})
                            assert ret.status_code == 400
                            assert b'Number must be between' in ret.data

                            with patch('juleol.db.db.session') as SessionMock:
                                ret = client.put('/rate/2000/1', data={'taste': 1})
                                assert test_score.score == 1
                                ret = client.put('/rate/2000/1', data={'aftertaste': 3})
                                assert test_score.score == 3
                                ret = client.put('/rate/2000/1', data={'smell': 2})
                                assert test_score.score == 2
                                ret = client.put('/rate/2000/1', data={'look': 1})
                                assert test_score.score == 1
                                ret = client.put('/rate/2000/1', data={'xmas': 2})
                                assert test_score.score == 2

                                SessionMock.commit.side_effect = exc.SQLAlchemyError()
                                ret = client.put('/rate/2000/1', data={'xmas': 2})
                                assert ret.status_code == 500
                                assert b'Error updating scores' in ret.data
