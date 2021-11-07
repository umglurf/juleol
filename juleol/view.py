# SPDX-FileCopyrightText: 2020 Håvard Moen <post@haavard.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import (
    Blueprint,
    render_template,
    request,
    session,
    jsonify,
    redirect,
    url_for,
    flash,
    current_app,
)
from flask_dance.consumer import oauth_authorized
from flask_login import current_user, login_required, login_user, logout_user
import oauthlib.oauth2.rfc6749.errors
from juleol import db
import re
from sqlalchemy import exc
from wtforms import Form, IntegerField, validators, SelectField
from wtforms.widgets.html5 import NumberInput

bp = Blueprint("view", __name__)


class LoginForm(Form):
    year = SelectField("Year", [validators.input_required()], coerce=int)


class RatingForm(Form):
    look = IntegerField(
        "Look (0-3)",
        [validators.optional(), validators.NumberRange(0, 3)],
        widget=NumberInput(min=0, max=3),
    )
    smell = IntegerField(
        "Smell (0-3)",
        [validators.optional(), validators.NumberRange(0, 3)],
        widget=NumberInput(min=0, max=3),
    )
    taste = IntegerField(
        "Taste (0-9)",
        [validators.optional(), validators.NumberRange(0, 9)],
        widget=NumberInput(min=0, max=9),
    )
    aftertaste = IntegerField(
        "Aftertaste (0-5)",
        [validators.optional(), validators.NumberRange(0, 5)],
        widget=NumberInput(min=0, max=5),
    )
    xmas = IntegerField(
        "Xmas (0-3)",
        [validators.optional(), validators.NumberRange(0, 3)],
        widget=NumberInput(min=0, max=3),
    )


@oauth_authorized.connect
def logged_in(blueprint, token):
    if not token:
        flash("Failed to log in", "error")
        return False

    blueprint.token = token
    if blueprint == current_app.config.get("admin_bp"):
        return True

    if not "participant_year" in session:
        return False

    try:
        resp = blueprint.session.get(current_app.config["user_info_path"])
        print(resp)
        if not resp.ok:
            flash("Error getting userdata", "error")
            return False
        email = resp.json()["email"]
    except oauthlib.oauth2.rfc6749.errors.TokenExpiredError:
        return redirect(url_for(current_app.config.get("user_oauth_login")))

    tasting = db.Tastings.query.filter(
        db.Tastings.year == session["participant_year"]
    ).first()
    participant = (
        db.Participants.query.filter(db.Participants.tasting == tasting)
        .filter(db.Participants.email == email)
        .first()
    )
    if participant:
        login_user(participant)
        flash("Login successfull")
    else:
        flash(
            "No user with email {} registered for year {}".format(
                email, session["participant_year"]
            ),
            "error",
        )
        return False


@bp.route("/login", methods=["POST"])
def login():
    form = LoginForm(request.form)
    form.year.choices = [(t.year, t.year) for t in db.Tastings.query.all()]
    if not form.validate():
        flash(f"Invalid year", "error")
        return redirect(url_for("view.index"))

    session["participant_year"] = form.year.data
    return redirect(url_for(current_app.config.get("user_oauth_login")))


@bp.route("/logout", methods=["GET"])
def logout():
    session_delete_ok = True
    if current_app.config.get("user_oauth").authorized:
        if current_app.config.get("USER_OAUTH_PROVIDER", "google") == "google":
            token = current_app.blueprints["google"].token["access_token"]
            try:
                resp = current_app.config.get("user_oauth").post(
                    "https://accounts.google.com/o/oauth2/revoke",
                    params={"token": token},
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
                session_delete_ok = resp.ok
                if not resp.ok:
                    current_app.logger.error(
                        "Logout failure, response from google: {}".format(resp.text)
                    )
                else:
                    del current_app.blueprints["google"].token
            except oauthlib.oauth2.rfc6749.errors.TokenExpiredError:
                # if token has expired, there is no need to revoke it
                pass

    if session_delete_ok:
        flash("Logout successfull")
        session.pop("participant_year", None)
        logout_user()
    else:
        flash("Failed to log out", "error")

    return redirect(url_for("view.index"))


@bp.route("/", methods=["GET"])
def index():
    form = LoginForm(request.form)
    form.year.choices = [(t.year, t.year) for t in db.Tastings.query.all()]
    tastings = db.Tastings.query.all()
    return render_template(
        "index.html", tastings=tastings, participant=current_user, form=form
    )


@bp.route("/result/<int:year>")
def result(year):
    tasting = db.Tastings.query.filter(db.Tastings.year == year).first()
    if not tasting:
        flash("Invalid year", "error")
        return redirect(url_for("view.index"))

    beer_scores = db.get_beer_scores(tasting)
    heat = request.args.get("heat")
    if heat is not None and re.match("^[0-9]{1,2}$", heat):
        heat = int(heat)
        beer_scores["totals"] = [s for s in beer_scores["totals"] if s.heat_id == heat]
    else:
        heat = None
    participants = db.Participants.query.filter(
        db.Participants.tasting_id == tasting.id
    ).all()

    if request.headers.get("Content-Type", "") == "application/json":
        result = {}
        result["beer_scores"] = {}
        for score in beer_scores["totals"]:
            s = int(score.sum) if score.sum else None
            a = float(score.avg) if score.avg else None
            d = float(score.std) if score.std else None
            result["beer_scores"][score.number] = {
                "name": score.name,
                "sum": s,
                "average": a,
                "stddev": d,
            }
        result["participants"] = {}
        for participant in participants:
            result["participants"][participant.id] = {"name": participant.name}
        return jsonify(result)
    else:
        return render_template(
            "result.html",
            beer_scores=beer_scores,
            tasting=tasting,
            participants=participants,
            heat=heat,
        )


@bp.route("/result/<int:year>/<int:participant_id>")
def participant_result(year, participant_id):
    participant = (
        db.Participants.query.join(db.Tastings)
        .filter(db.Participants.id == participant_id)
        .filter(db.Tastings.year == year)
        .one()
    )
    if not participant:
        flash("Invalid participant", "error")
        return redirect(url_for("view.index"))

    scores = db.participant_scores(participant)
    heat = request.args.get("heat")
    if heat is not None and re.match("^[0-9]{1,2}$", heat):
        heat = int(heat)
        scores = [s for s in scores if s.heat_id == heat]
    else:
        heat = None
    return render_template(
        "participant_result.html", participant=participant, scores=scores, heat=heat
    )


@bp.route("/rate/<int:year>", methods=["GET"])
@login_required
def rate(year):
    if not current_user.tasting.year == year:
        flash("Invalid year for this user", "error")
        return redirect(url_for("view.index"))
    form = RatingForm()
    heat = request.args.get("heat")
    if heat is not None and re.match("^[0-9]{1,2}$", heat):
        heat = int(heat)
    else:
        heat = None
    return render_template("rate.html", form=form, heat=heat)


@bp.route("/rate/<int:year>/<int:beer_number>", methods=["GET", "PUT"])
@login_required
def rate_beer(year, beer_number):
    if not current_user.tasting.year == year:
        response = jsonify(error="Invalid year for this user")
        response.status_code = 400
        return response

    beer = (
        db.Beers.query.filter(db.Beers.tasting == current_user.tasting)
        .filter(db.Beers.number == beer_number)
        .first()
    )
    if not beer:
        response = jsonify(error="Invalid beer")
        response.status_code = 400
        return response

    if request.method == "GET":
        taste = (
            db.ScoreTaste.query.filter(db.ScoreTaste.participant == current_user)
            .filter(db.ScoreTaste.beer == beer)
            .first()
        )
        aftertaste = (
            db.ScoreAftertaste.query.filter(
                db.ScoreAftertaste.participant == current_user
            )
            .filter(db.ScoreAftertaste.beer == beer)
            .first()
        )
        look = (
            db.ScoreLook.query.filter(db.ScoreLook.participant == current_user)
            .filter(db.ScoreLook.beer == beer)
            .first()
        )
        smell = (
            db.ScoreSmell.query.filter(db.ScoreSmell.participant == current_user)
            .filter(db.ScoreSmell.beer == beer)
            .first()
        )
        xmas = (
            db.ScoreXmas.query.filter(db.ScoreXmas.participant == current_user)
            .filter(db.ScoreXmas.beer == beer)
            .first()
        )

        data = {
            "taste": taste.score,
            "aftertaste": aftertaste.score,
            "look": look.score,
            "smell": smell.score,
            "xmas": xmas.score,
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
            look = (
                db.ScoreLook.query.filter(db.ScoreLook.participant == current_user)
                .filter(db.ScoreLook.beer == beer)
                .first()
            )
            look.score = form.look.data
            db.db.session.add(look)
        if form.smell.data is not None:
            smell = (
                db.ScoreSmell.query.filter(db.ScoreSmell.participant == current_user)
                .filter(db.ScoreSmell.beer == beer)
                .first()
            )
            smell.score = form.smell.data
            db.db.session.add(smell)
        if form.taste.data is not None:
            taste = (
                db.ScoreTaste.query.filter(db.ScoreTaste.participant == current_user)
                .filter(db.ScoreTaste.beer == beer)
                .first()
            )
            taste.score = form.taste.data
            db.db.session.add(taste)
        if form.aftertaste.data is not None:
            aftertaste = (
                db.ScoreAftertaste.query.filter(
                    db.ScoreAftertaste.participant == current_user
                )
                .filter(db.ScoreAftertaste.beer == beer)
                .first()
            )
            aftertaste.score = form.aftertaste.data
            db.db.session.add(aftertaste)
        if form.xmas.data is not None:
            xmas = (
                db.ScoreXmas.query.filter(db.ScoreXmas.participant == current_user)
                .filter(db.ScoreXmas.beer == beer)
                .first()
            )
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
