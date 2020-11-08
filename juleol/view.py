from flask import Blueprint, render_template, request, session, jsonify, redirect, url_for, flash, g, current_app
import oauthlib.oauth2.rfc6749.errors
from functools import wraps
from juleol import db
import re
from sqlalchemy import exc
from wtforms import Form, IntegerField, validators, SelectField
from wtforms.widgets.html5 import NumberInput

bp = Blueprint('view', __name__)


class LoginForm(Form):
    year = SelectField("Year", [validators.input_required()], coerce=int)


class RatingForm(Form):
    look = IntegerField(
        'Look (0-3)',
        [validators.optional(), validators.NumberRange(0, 3)],
        widget=NumberInput(min=0, max=3)
        )
    smell = IntegerField(
        'Smell (0-3)',
        [validators.optional(), validators.NumberRange(0, 3)],
        widget=NumberInput(min=0, max=3)
        )
    taste = IntegerField(
        'Taste (0-9)',
        [validators.optional(), validators.NumberRange(0, 9)],
        widget=NumberInput(min=0, max=9)
        )
    aftertaste = IntegerField(
        'Aftertaste (0-5)',
        [validators.optional(), validators.NumberRange(0, 5)],
        widget=NumberInput(min=0, max=5)
        )
    xmas = IntegerField(
        'Xmas (0-3)',
        [validators.optional(), validators.NumberRange(0, 3)],
        widget=NumberInput(min=0, max=3)
        )


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' in session:
            g.participant = db.Participants.query.filter(db.Participants.id == session['user_id']).first()
            if not g.participant:
                flash("Invalid user", "error")
                session.pop('participant_year', None)
                session.pop('user_id', None)
                return redirect(url_for("view.index"))
        else:
            flash("Login required", "error")
            return redirect(url_for("view.index"))
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    form.year.choices = [(t.year, t.year) for t in db.Tastings.query.all()]
    if request.method == "POST":
        if form.validate():
            session['participant_year'] = form.year.data
            if current_app.config.get('user_oauth').authorized:
                return redirect(url_for("view.login"))
            else:
                return redirect(url_for(current_app.config.get('user_oauth_login')))
        else:
            flash("Invalid year", 'error')
            return redirect(url_for("view.index"))

    if not 'participant_year' in session:
        flash("No year selected", "error")
        return redirect(url_for("view.index"))
    if not current_app.config.get('user_oauth').authorized:
        return redirect(url_for(current_app.config.get('user_oauth_login')))
    if current_app.config.get('USER_OAUTH_PROVIDER', 'google') == 'google':
        try:
            resp = current_app.config.get('user_oauth').get("/oauth2/v1/userinfo")
            if not resp.ok:
                flash("Error getting userdata from google", "error")
                return redirect(url_for("view.index"))
            email = resp.json()['email']
        except oauthlib.oauth2.rfc6749.errors.TokenExpiredError:
            return redirect(url_for(current_app.config.get('user_oauth_login')))

    tasting = db.Tastings.query.filter(db.Tastings.year == session['participant_year']).first()
    participant = db.Participants.query.filter(
        db.Participants.tasting == tasting
        ).filter(
            db.Participants.email == email
            ).first()
    if participant:
        session['user_id'] = participant.id
        flash("Login successfull")
        return redirect(url_for("view.index"))
    else:
        flash("No user with email {} registered for year {}".format(email, session['participant_year']), "error")
        return redirect(url_for("view.index"))

@bp.route('/logout', methods=["GET"])
def logout():
    session_delete_ok = True
    if current_app.config.get('user_oauth').authorized:
        if current_app.config.get('USER_OAUTH_PROVIDER', 'google') == 'google':
            token = current_app.blueprints["google"].token["access_token"]
            try:
                resp = current_app.config.get('user_oauth').post(
                    "https://accounts.google.com/o/oauth2/revoke",
                    params={"token": token},
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                session_delete_ok = resp.ok
                if not resp.ok:
                    current_app.logger.error("Logout failure, response from google: {}".format(resp.text))
            except oauthlib.oauth2.rfc6749.errors.TokenExpiredError:
            # if token has expired, there is no need to revoke it
                pass

    if session_delete_ok:
        flash("Logout successfull")
        session.pop('participant_year', None)
        session.pop('user_id', None)
    else:
        flash("Failed to log out", "error")

    return redirect(url_for('view.index'))


@bp.route('/', methods=["GET"])
def index():
    form = LoginForm(request.form)
    form.year.choices = [(t.year, t.year) for t in db.Tastings.query.all()]
    tastings = db.Tastings.query.all()
    participant = None
    if 'user_id' in session:
        participant = db.Participants.query.filter(db.Participants.id == session['user_id']).first()
    return render_template('index.html', tastings=tastings, participant=participant, form=form)


@bp.route('/result/<int:year>')
def result(year):
    tasting = db.Tastings.query.filter(db.Tastings.year == year).first()
    if not tasting:
        flash("Invalid year", 'error')
        return redirect(url_for('view.index'))

    beer_scores = db.get_beer_scores(tasting)
    heat = request.args.get('heat')
    if heat is not None and re.match("^[0-9]{1,2}$", heat):
        heat = int(heat)
        beer_scores['totals'] = [s for s in beer_scores['totals'] if s.heat_id == heat]
    else:
        heat = None
    participants = db.Participants.query.filter(db.Participants.tasting_id == tasting.id).all()

    if request.headers.get('Content-Type', '') == 'application/json':
        result = {}
        result['beer_scores'] = {}
        for score in beer_scores['totals']:
            s = int(score.sum) if score.sum else None
            a = float(score.avg) if score.avg else None
            d = float(score.std) if score.std else None
            result['beer_scores'][score.number] = {
                    'name': score.name,
                    'sum': s,
                    'average': a,
                    'stddev': d
                    }
        result['participants'] = {}
        for participant in participants:
            result['participants'][participant.id] = {'name': participant.name}
        return jsonify(result)
    else:
        return render_template('result.html', beer_scores=beer_scores, tasting=tasting, participants=participants, heat=heat)


@bp.route('/result/<int:year>/<int:participant_id>')
def participant_result(year, participant_id):
    participant = db.Participants.query.join(
        db.Tastings
        ).filter(
            db.Participants.id == participant_id
            ).filter(
                db.Tastings.year == year
                ).one()
    if not participant:
        flash("Invalid participant", 'error')
        return redirect(url_for('view.index'))

    scores = db.participant_scores(participant)
    heat = request.args.get('heat')
    if heat is not None and re.match("^[0-9]{1,2}$", heat):
        heat = int(heat)
        scores = [s for s in scores if s.heat_id == heat]
    else:
        heat = None
    return render_template('participant_result.html', participant=participant, scores=scores, heat=heat)


@bp.route('/rate/<int:year>', methods=["GET"])
@login_required
def rate(year):
    if not g.participant.tasting.year == year:
        flash("Invalid year for this user", "error")
        return redirect(url_for('view.index'))
    form = RatingForm()
    heat = request.args.get('heat')
    if heat is not None and re.match("^[0-9]{1,2}$", heat):
        heat = int(heat)
    else:
        heat = None
    return render_template('rate.html', form=form, heat=heat)


@bp.route('/rate/<int:year>/<int:beer_number>', methods=["GET", "PUT"])
@login_required
def rate_beer(year, beer_number):
    if not g.participant.tasting.year == year:
        response = jsonify(error="Invalid year for this user")
        response.status_code = 400
        return response

    beer = db.Beers.query.filter(db.Beers.tasting == g.participant.tasting).filter(db.Beers.number == beer_number).first()
    if not beer:
        response = jsonify(error="Invalid beer")
        response.status_code = 400
        return response

    if request.method == 'GET':
        taste = db.ScoreTaste.query.filter(
            db.ScoreTaste.participant == g.participant
            ).filter(
                db.ScoreTaste.beer == beer
                ).first()
        aftertaste = db.ScoreAftertaste.query.filter(
            db.ScoreAftertaste.participant == g.participant
            ).filter(
                db.ScoreAftertaste.beer == beer
                ).first()
        look = db.ScoreLook.query.filter(
            db.ScoreLook.participant == g.participant
            ).filter(
                db.ScoreLook.beer == beer
                ).first()
        smell = db.ScoreSmell.query.filter(
                db.ScoreSmell.participant == g.participant
                ).filter(
                    db.ScoreSmell.beer == beer
                    ).first()
        xmas = db.ScoreXmas.query.filter(
            db.ScoreXmas.participant == g.participant
            ).filter(
                db.ScoreXmas.beer == beer
                ).first()

        data = {
                'taste': taste.score,
                'aftertaste': aftertaste.score,
                'look': look.score,
                'smell': smell.score,
                'xmas': xmas.score
                }

        return jsonify(data)

    if beer.tasting.locked:
        response = jsonify(error="Tasting is locked")
        response.status_code = 403
        return response
    form = RatingForm(request.form)
    if not form.validate():
        error_msg = ["{}: {}".format(k, ", ".join(v)) for k, v in form.errors.items()]
        response = jsonify(error=error_msg)
        response.status_code = 400
        return response

    try:
        if form.look.data is not None:
            look = db.ScoreLook.query.filter(
                db.ScoreLook.participant == g.participant
                ).filter(
                    db.ScoreLook.beer == beer
                    ).first()
            look.score = form.look.data
            db.db.session.add(look)
        if form.smell.data is not None:
            smell = db.ScoreSmell.query.filter(
                db.ScoreSmell.participant == g.participant
                ).filter(
                    db.ScoreSmell.beer == beer
                    ).first()
            smell.score = form.smell.data
            db.db.session.add(smell)
        if form.taste.data is not None:
            taste = db.ScoreTaste.query.filter(
                db.ScoreTaste.participant == g.participant
                ).filter(
                    db.ScoreTaste.beer == beer
                    ).first()
            taste.score = form.taste.data
            db.db.session.add(taste)
        if form.aftertaste.data is not None:
            aftertaste = db.ScoreAftertaste.query.filter(
                db.ScoreAftertaste.participant == g.participant
                ).filter(
                    db.ScoreAftertaste.beer == beer
                    ).first()
            aftertaste.score = form.aftertaste.data
            db.db.session.add(aftertaste)
        if form.xmas.data is not None:
            xmas = db.ScoreXmas.query.filter(
                db.ScoreXmas.participant == g.participant
                ).filter(
                    db.ScoreXmas.beer == beer
                    ).first()
            xmas.score = form.xmas.data
            db.db.session.add(xmas)
        db.db.session.commit()
    except exc.SQLAlchemyError as e:
        db.db.session.rollback()
        current_app.logger.error("Error updating scores: {}".format(e))
        response = jsonify(error="Error updating scores")
        response.status_code = 500
        return response

    return jsonify(message="Data updated")
