import json
from juleol import db
import pytest
from sqlalchemy import exc
from unittest.mock import patch, MagicMock

def test_login(admin_noauth_client):
    ret = admin_noauth_client.get('/admin/')
    assert ret.status_code == 302
    assert ret.headers['Location'] == 'http://localhost/admin/login/github'

def test_admin_base(admin_client):
    with patch('juleol.db.Tastings') as MockTastings:
        test_tasting = db.Tastings()
        test_tasting.year = 2000
        MockTastings.query.all.return_value = [test_tasting]

        ret = admin_client.get('/admin/')
        assert ret.status_code == 200
        assert b'<li class="list-group-item list-group-item-secondary"><a class="text-primary" href="/admin/2000">2000</a></li>' in ret.data

def test_add_tasting(admin_client):
    with patch('juleol.db.Tastings') as TastingsMock:
        with patch('juleol.db.Beers') as BeersMock:
            with patch('juleol.db.db.session') as SessionMock:
                ret = admin_client.post('/admin/', data={'year': 2000, 'beers': 2})
                assert ret.status_code == 200
                expected = [({'year': 2000},)]
                assert TastingsMock.call_args_list == expected
                expected = [
                        ({'number': 1, 'name': 'Unrevealed 1', 'tasting': db.Tastings(year = 2000)},),
                        ({'number': 2, 'name': 'Unrevealed 2', 'tasting': db.Tastings(year = 2000)},)
                ]
                assert BeersMock.call_args_list == expected
                assert SessionMock.mock_calls[0][0] == 'add'
                assert SessionMock.mock_calls[0][1] == (db.Tastings(year = 2000),)
                assert SessionMock.mock_calls[1][0] == 'add'
                assert SessionMock.mock_calls[1][1] == (db.Beers(number = 1, name = 'Unrevealed 1', tasting = db.Tastings(year = 2000)),)
                assert SessionMock.mock_calls[2][0] == 'add'
                assert SessionMock.mock_calls[2][1] == (db.Beers(number = 2, name = 'Unrevealed 2', tasting = db.Tastings(year = 2000)),)
                assert SessionMock.mock_calls[3][0] == 'commit'

def test_add_tasting_fail(admin_client):
    with patch('juleol.db.db.session') as SessionMock:
        SessionMock.commit.side_effect = exc.SQLAlchemyError()
        ret = admin_client.post('/admin/', data={'year': 2000, 'beers': 2})
        assert ret.status_code == 200
        assert b'Error creating tasting' in ret.data
        assert SessionMock.mock_calls[4][0] == 'rollback'

def test_year(admin_client):
    with patch('juleol.db.Tastings') as TastingsMock:
        test_tasting = db.Tastings()
        test_tasting.year = 2000
        TastingsMock.query.filter.return_value.first.return_value = test_tasting
        ret = admin_client.get('/admin/2000')
        assert ret.status_code == 200
        TastingsMock.query.filter.return_value.first.return_value = None
        ret = admin_client.get('/admin/2000')
        assert ret.status_code == 302
        assert ret.headers['Location'] == 'http://localhost/admin/'
        ret = admin_client.get('/admin/')
        assert b'Invalid year' in ret.data

def test_create_participant(admin_client):
    with patch('juleol.db.Tastings') as TastingsMock:
        TastingsMock.query.filter.return_value.first.return_value = None
        ret = admin_client.post('/admin/2000/participant')
        assert ret.status_code == 302
        assert ret.headers['Location'] == 'http://localhost/admin/'
        ret = admin_client.get('/admin/')
        assert b'Invalid year' in ret.data

        test_tasting = db.Tastings()
        test_tasting.year = 2000
        test_beer = db.Beers()
        test_beer.name = 'test beer'
        test_beer.number = 1
        test_tasting.beers = [test_beer]
        test_tasting.participants = []
        TastingsMock.query.filter.return_value.first.return_value = test_tasting

        ret = admin_client.post('/admin/2000/participant', data={'name': 'test'})
        assert ret.status_code == 302
        assert ret.headers['Location'] == 'http://localhost/admin/2000'
        ret = admin_client.get('/admin/2000')
        assert b'Invalid form data' in ret.data

        with patch('juleol.db.Beers') as BeersMock:
            with patch('juleol.db.Participants') as ParticpantsMock:
                with patch('juleol.db.ScoreTaste') as MockScoreTaste:
                    with patch('juleol.db.ScoreAftertaste') as MockScoreAftertaste:
                        with patch('juleol.db.ScoreLook') as MockScoreLook:
                            with patch('juleol.db.ScoreSmell') as MockScoreSmell:
                                with patch('juleol.db.ScoreXmas') as MockScoreXmas:
                                    with patch('juleol.db.db.session') as SessionMock:
                                        from flask_bcrypt import Bcrypt
                                        bcrypt = Bcrypt()

                                        ret = admin_client.post('/admin/2000/participant', data={'name': 'test', 'password': 'test'})
                                        assert ret.status_code == 302
                                        assert ret.headers['Location'] == 'http://localhost/admin/2000'
                                        assert ParticpantsMock.mock_calls[0][2]['tasting'] == test_tasting
                                        assert ParticpantsMock.mock_calls[0][2]['name'] == 'test'
                                        assert bcrypt.check_password_hash(ParticpantsMock.mock_calls[0][2]['password'], 'test')

                                        assert MockScoreLook.mock_calls[0][2]['tasting'] == test_tasting
                                        assert MockScoreLook.mock_calls[0][2]['beer'] == test_beer

                                        assert MockScoreSmell.mock_calls[0][2]['tasting'] == test_tasting
                                        assert MockScoreSmell.mock_calls[0][2]['beer'] == test_beer

                                        assert MockScoreTaste.mock_calls[0][2]['tasting'] == test_tasting
                                        assert MockScoreTaste.mock_calls[0][2]['beer'] == test_beer

                                        assert MockScoreAftertaste.mock_calls[0][2]['tasting'] == test_tasting
                                        assert MockScoreAftertaste.mock_calls[0][2]['beer'] == test_beer

                                        assert MockScoreXmas.mock_calls[0][2]['beer'] == test_beer
                                        assert MockScoreXmas.mock_calls[0][2]['tasting'] == test_tasting

                                        assert SessionMock.mock_calls[0][0] == 'add'
                                        assert SessionMock.mock_calls[0][1] == (db.Participants(name = 'test', password = 'test', tasting = test_tasting),)
                                        assert SessionMock.mock_calls[1][0] == 'add'
                                        assert SessionMock.mock_calls[1][1] == (db.ScoreLook(tasting = test_tasting, beer = test_beer, participant = db.Participants(name = 'test', password = 'test', tasting = test_tasting)),)
                                        assert SessionMock.mock_calls[2][0] == 'add'
                                        assert SessionMock.mock_calls[2][1] == (db.ScoreSmell(tasting = test_tasting, beer = test_beer, participant = db.Participants(name = 'test', password = 'test', tasting = test_tasting)),)
                                        assert SessionMock.mock_calls[3][0] == 'add'
                                        assert SessionMock.mock_calls[3][1] == (db.ScoreTaste(tasting = test_tasting, beer = test_beer, participant = db.Participants(name = 'test', password = 'test', tasting = test_tasting)),)
                                        assert SessionMock.mock_calls[4][0] == 'add'
                                        assert SessionMock.mock_calls[4][1] == (db.ScoreAftertaste(tasting = test_tasting, beer = test_beer, participant = db.Participants(name = 'test', password = 'test', tasting = test_tasting)),)
                                        assert SessionMock.mock_calls[5][0] == 'add'
                                        assert SessionMock.mock_calls[5][1] == (db.ScoreXmas(tasting = test_tasting, beer = test_beer, participant = db.Participants(name = 'test', password = 'test', tasting = test_tasting)),)
                                        assert SessionMock.mock_calls[6][0] == 'commit'

                                        SessionMock.reset_mock()
                                        SessionMock.commit.side_effect = exc.SQLAlchemyError()
                                        ret = admin_client.post('/admin/2000/participant', data={'name': 'test', 'password': 'test'})
                                        assert ret.status_code == 302
                                        assert ret.headers['Location'] == 'http://localhost/admin/2000'
                                        ret = admin_client.get('/admin/2000')
                                        assert b'Error creating participant' in ret.data
                                        assert SessionMock.mock_calls[7][0] == 'rollback'

def test_update_participant(admin_client):
    with patch('juleol.db.Tastings') as TastingsMock:
        test_tasting = db.Tastings()
        test_tasting.year = 2000
        TastingsMock.query.filter.return_value.first.return_value = test_tasting
        TastingsMock.query.filter.return_value.first.return_value = None
        ret = admin_client.post('/admin/2000/participant/1')
        assert ret.status_code == 302
        ret = admin_client.get('/admin/')
        assert b'Invalid year' in ret.data

        TastingsMock.query.filter.return_value.first.return_value = test_tasting
        with patch('juleol.db.Participants') as ParticipantsMock:
            ParticipantsMock.query.filter.return_value.filter.return_value.first.return_value = None
            ret = admin_client.post('/admin/2000/participant/1')
            assert ret.status_code == 302
            assert ret.headers['Location'] == 'http://localhost/admin/2000'
            ret = admin_client.get('/admin/2000')
            assert b'Invalid participant' in ret.data

            test_participant = db.Participants()
            test_participant.tasting = test_tasting
            ParticipantsMock.query.filter.return_value.filter.return_value.first.return_value = test_participant
            ret = admin_client.post('/admin/2000/participant/1')
            assert ret.status_code == 302
            assert ret.headers['Location'] == 'http://localhost/admin/2000'
            ret = admin_client.get('/admin/2000')
            assert b'Invalid form data' in ret.data

            with patch('juleol.db.db.session') as SessionMock:
                ret = admin_client.post('/admin/2000/participant/1', data={'password': 'test'})
                assert ret.status_code == 302
                assert ret.headers['Location'] == 'http://localhost/admin/2000'
                from flask_bcrypt import Bcrypt
                bcrypt = Bcrypt()
                assert bcrypt.check_password_hash(test_participant.password, 'test')
                assert SessionMock.mock_calls[0][0] == 'add'
                assert SessionMock.mock_calls[0][1] == (test_participant, )
                assert SessionMock.mock_calls[1][0] == 'commit'

                SessionMock.reset_mock()
                SessionMock.commit.side_effect = exc.SQLAlchemyError()
                ret = admin_client.post('/admin/2000/participant/1', data={'password': 'test'})
                assert ret.status_code == 302
                assert ret.headers['Location'] == 'http://localhost/admin/2000'
                ret = admin_client.get('/admin/2000')
                assert b'Error updating password' in ret.data
                assert SessionMock.mock_calls[2][0] == 'rollback'

def test_create_heat(admin_client):
    with patch('juleol.db.Tastings') as TastingsMock:
        test_tasting = db.Tastings()
        test_tasting.year = 2000
        TastingsMock.query.filter.return_value.first.return_value = test_tasting
        TastingsMock.query.filter.return_value.first.return_value = None
        ret = admin_client.post('/admin/2000/heat')
        assert ret.status_code == 302
        ret = admin_client.get('/admin/')
        assert b'Invalid year' in ret.data

        TastingsMock.query.filter.return_value.first.return_value = test_tasting
        with patch('juleol.db.Heats') as HeatsMock:
            ret = admin_client.post('/admin/2000/heat')
            assert ret.status_code == 302
            assert ret.headers['Location'] == 'http://localhost/admin/2000'
            ret = admin_client.get('/admin/2000')
            assert b'Invalid form data' in ret.data

            with patch('juleol.db.db.session') as SessionMock:
                ret = admin_client.post('/admin/2000/heat', data={'name': 'test'})
                assert ret.status_code == 302
                assert ret.headers['Location'] == 'http://localhost/admin/2000'
                assert HeatsMock.mock_calls[0][2]['name'] == 'test'
                assert HeatsMock.mock_calls[0][2]['tasting'] == test_tasting
                assert SessionMock.mock_calls[0][0] == 'add'
                assert SessionMock.mock_calls[0][1] == (db.Heats(name = 'test', tasting = test_tasting), )
                assert SessionMock.mock_calls[1][0] == 'commit'

                SessionMock.reset_mock()
                SessionMock.commit.side_effect = exc.SQLAlchemyError()
                ret = admin_client.post('/admin/2000/heat', data={'name': 'test'})
                assert ret.status_code == 302
                assert ret.headers['Location'] == 'http://localhost/admin/2000'
                ret = admin_client.get('/admin/2000')
                assert b'Error creating heat' in ret.data
                assert SessionMock.mock_calls[2][0] == 'rollback'

def test_get_update_heat(admin_client):
    with patch('juleol.db.Heats') as HeatsMock:
        db.Heats.query.filter.return_value.first.return_value = None
        ret = admin_client.get('/admin/heat/1')
        assert ret.status_code == 404
        assert json.loads(ret.data)['error'] == 'Invalid heat id'

        test_heat = db.Heats()
        test_heat.id = 1
        test_heat.name = 'test'
        db.Heats.query.filter.return_value.first.return_value = test_heat
        ret = admin_client.get('/admin/heat/1')
        assert ret.status_code == 200
        data = json.loads(ret.data)
        assert data['id'] == 1
        assert data['name'] == 'test'

        with patch('juleol.db.db.session') as SessionMock:
            ret = admin_client.put('/admin/heat/1')
            assert ret.status_code == 400
            assert json.loads(ret.data)['error'] == 'Invalid arguments'
            ret = admin_client.put('/admin/heat/1', data = {'name': 'new test'})
            assert ret.status_code == 200
            assert json.loads(ret.data)['message'] == 'Heat updated'
            assert test_heat.name == 'new test'
            assert SessionMock.mock_calls[0][0] == 'add'
            assert SessionMock.mock_calls[0][1] == (test_heat,)
            assert SessionMock.mock_calls[1][0] == 'commit'

            SessionMock.reset_mock()
            ret = admin_client.delete('/admin/heat/1')
            assert ret.status_code == 200
            assert json.loads(ret.data)['message'] == 'Heat deleted'
            assert SessionMock.mock_calls[0][0] == 'delete'
            assert SessionMock.mock_calls[0][1] == (test_heat,)
            assert SessionMock.mock_calls[1][0] == 'commit'

            SessionMock.reset_mock()
            SessionMock.commit.side_effect = exc.SQLAlchemyError()
            ret = admin_client.put('/admin/heat/1', data = {'name': 'new test'})
            assert ret.status_code == 500
            assert json.loads(ret.data)['error'] == 'Error updating heat'
            ret = admin_client.delete('/admin/heat/1')
            assert ret.status_code == 500
            assert json.loads(ret.data)['error'] == 'Error deleting heat'
            assert SessionMock.mock_calls[2][0] == 'rollback'

def test_create_note(admin_client):
    with patch('juleol.db.Tastings') as TastingsMock:
        test_tasting = db.Tastings()
        test_tasting.year = 2000
        TastingsMock.query.filter.return_value.first.return_value = test_tasting
        TastingsMock.query.filter.return_value.first.return_value = None
        ret = admin_client.post('/admin/2000/note')
        assert ret.status_code == 302
        ret = admin_client.get('/admin/')
        assert b'Invalid year' in ret.data

        TastingsMock.query.filter.return_value.first.return_value = test_tasting
        with patch('juleol.db.Notes') as NotesMock:
            ret = admin_client.post('/admin/2000/note')
            assert ret.status_code == 302
            assert ret.headers['Location'] == 'http://localhost/admin/2000'
            ret = admin_client.get('/admin/2000')
            assert b'Invalid form data' in ret.data

            with patch('juleol.db.db.session') as SessionMock:
                ret = admin_client.post('/admin/2000/note', data={'note': 'test'})
                assert ret.status_code == 302
                assert ret.headers['Location'] == 'http://localhost/admin/2000'
                assert NotesMock.mock_calls[0][2]['note'] == 'test'
                assert NotesMock.mock_calls[0][2]['tasting'] == test_tasting
                assert SessionMock.mock_calls[0][0] == 'add'
                assert SessionMock.mock_calls[0][1] == (db.Notes(note = 'test', tasting = test_tasting), )
                assert SessionMock.mock_calls[1][0] == 'commit'

                SessionMock.reset_mock()
                SessionMock.commit.side_effect = exc.SQLAlchemyError()
                ret = admin_client.post('/admin/2000/note', data={'note': 'test'})
                assert ret.status_code == 302
                assert ret.headers['Location'] == 'http://localhost/admin/2000'
                ret = admin_client.get('/admin/2000')
                assert b'Error creating note' in ret.data
                assert SessionMock.mock_calls[2][0] == 'rollback'

def test_get_update_note(admin_client):
    with patch('juleol.db.Notes') as NotesMock:
        db.Notes.query.filter.return_value.first.return_value = None
        ret = admin_client.get('/admin/note/1')
        assert ret.status_code == 404
        assert json.loads(ret.data)['error'] == 'Invalid note id'

        test_note = db.Notes()
        test_note.id = 1
        test_note.note = 'test'
        db.Notes.query.filter.return_value.first.return_value = test_note
        ret = admin_client.get('/admin/note/1')
        assert ret.status_code == 200
        data = json.loads(ret.data)
        assert data['id'] == 1
        assert data['note'] == 'test'

        with patch('juleol.db.db.session') as SessionMock:
            ret = admin_client.put('/admin/note/1')
            assert ret.status_code == 400
            assert json.loads(ret.data)['error'] == 'Invalid arguments'
            ret = admin_client.put('/admin/note/1', data = {'note': 'new test'})
            assert ret.status_code == 200
            assert json.loads(ret.data)['message'] == 'Note updated'
            assert test_note.note == 'new test'
            assert SessionMock.mock_calls[0][0] == 'add'
            assert SessionMock.mock_calls[0][1] == (test_note,)
            assert SessionMock.mock_calls[1][0] == 'commit'

            SessionMock.reset_mock()
            ret = admin_client.delete('/admin/note/1')
            assert ret.status_code == 200
            assert json.loads(ret.data)['message'] == 'Note deleted'
            assert SessionMock.mock_calls[0][0] == 'delete'
            assert SessionMock.mock_calls[0][1] == (test_note,)
            assert SessionMock.mock_calls[1][0] == 'commit'

            SessionMock.reset_mock()
            SessionMock.commit.side_effect = exc.SQLAlchemyError()
            ret = admin_client.put('/admin/note/1', data = {'note': 'new test'})
            assert ret.status_code == 500
            assert json.loads(ret.data)['error'] == 'Error updating note'
            ret = admin_client.delete('/admin/note/1')
            assert ret.status_code == 500
            assert json.loads(ret.data)['error'] == 'Error deleting note'
            assert SessionMock.mock_calls[2][0] == 'rollback'

def test_update_beer(admin_client):
    with patch('juleol.db.Beers') as BeersMock:
        db.Beers.query.filter.return_value.first.return_value = None
        ret = admin_client.put('/admin/beer/1')
        assert ret.status_code == 404
        assert json.loads(ret.data)['error'] == 'Invalid beer id'

        test_beer = db.Beers()
        test_beer.id = 1
        test_beer.number = 1
        test_beer.name = 'test beer 1'
        db.Beers.query.filter.return_value.first.return_value = test_beer
        ret = admin_client.put('/admin/beer/1')
        assert ret.status_code == 400
        assert json.loads(ret.data)['error'] == 'Invalid arguments'

        with patch('juleol.db.db.session') as SessionMock:
            ret = admin_client.put('/admin/beer/1', data={'name': 'new name'} )
            assert ret.status_code == 200
            assert json.loads(ret.data)['message'] == 'Beer name updated'
            assert test_beer.name == 'new name'
            assert SessionMock.mock_calls[0][0] == 'add'
            assert SessionMock.mock_calls[0][1] == (test_beer,)
            assert SessionMock.mock_calls[1][0] == 'commit'

            SessionMock.reset_mock()
            SessionMock.commit.side_effect = exc.SQLAlchemyError()
            ret = admin_client.put('/admin/beer/1', data={'name': 'new name'} )
            assert ret.status_code == 500
            assert json.loads(ret.data)['error'] == 'Error updating beer name'
            assert SessionMock.mock_calls[0][0] == 'add'
            assert SessionMock.mock_calls[0][1] == (test_beer,)
            assert SessionMock.mock_calls[1][0] == 'commit'
            assert SessionMock.mock_calls[2][0] == 'rollback'

            with patch('juleol.db.Heats') as HeatsMock:
                test_heat = db.Heats()
                test_heat.id = 1
                test_heat.name = 'test'

                db.Heats.query.filter.return_value.filter.return_value.first.return_value = None
                ret = admin_client.put('/admin/beer/1', data={'heat': 1} )
                assert ret.status_code == 404
                assert json.loads(ret.data)['error'] == 'Invalid heat'

                db.Heats.query.filter.return_value.filter.return_value.first.return_value = test_heat
                SessionMock.reset_mock()
                SessionMock.commit.side_effect = None
                ret = admin_client.put('/admin/beer/1', data={'heat': 1} )
                assert ret.status_code == 200
                assert json.loads(ret.data)['message'] == 'Beer heat updated'
                assert test_beer.name == 'new name'
                assert SessionMock.mock_calls[0][0] == 'add'
                assert SessionMock.mock_calls[0][1] == (test_beer,)
                assert SessionMock.mock_calls[1][0] == 'commit'
                assert test_beer.heat == test_heat

                SessionMock.commit.side_effect = exc.SQLAlchemyError()
                SessionMock.reset_mock()
                ret = admin_client.put('/admin/beer/1', data={'heat': 1} )
                assert ret.status_code == 500
                assert json.loads(ret.data)['error'] == 'Error updating beer heat'
                assert SessionMock.mock_calls[2][0] == 'rollback'

def test_delete_beer_heat(admin_client):
    with patch('juleol.db.Beers') as BeersMock:
        db.Beers.query.filter.return_value.first.return_value = None
        ret = admin_client.delete('/admin/beer/1/heat')
        assert ret.status_code == 404
        assert json.loads(ret.data)['error'] == 'Invalid beer id'

        with patch('juleol.db.db.session') as SessionMock:
            test_beer = db.Beers()
            test_beer.id = 1
            test_beer.number = 1
            test_beer.name = 'test beer 1'
            test_beer.heat = 1
            db.Beers.query.filter.return_value.first.return_value = test_beer
            ret = admin_client.delete('/admin/beer/1/heat')
            assert ret.status_code == 200
            assert json.loads(ret.data)['message'] == 'Beer heat deleted'
            assert SessionMock.mock_calls[0][0] == 'add'
            assert SessionMock.mock_calls[0][1] == (test_beer,)
            assert SessionMock.mock_calls[1][0] == 'commit'
            assert test_beer.heat is None

            SessionMock.commit.side_effect = exc.SQLAlchemyError()
            SessionMock.reset_mock()
            ret = admin_client.delete('/admin/beer/1/heat')
            assert ret.status_code == 500
            assert json.loads(ret.data)['error'] == 'Error deleting beer heat'
            assert SessionMock.mock_calls[2][0] == 'rollback'
