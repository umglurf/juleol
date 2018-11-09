from flask import Flask, Blueprint, render_template, request, session, jsonify, redirect, url_for, flash, current_app
from flask_bcrypt import Bcrypt
from functools import wraps
from juleol import db
from juleol.haavard import haavard
from sqlalchemy import exc
from wtforms import Form, IntegerField, validators, HiddenField, PasswordField, TextField
from wtforms.widgets.html5 import NumberInput

bp = Blueprint('admin', __name__)

bcrypt = Bcrypt()

class TastingForm(Form):
    year = IntegerField('Year', [validators.input_required(), validators.NumberRange(2000, 2100)], widget = NumberInput(min=2000, max=2100))
    beers = IntegerField('Number of beers', [validators.input_required(), validators.NumberRange(1, 100)], widget = NumberInput(min=1, max=100))

class ParticipantForm(Form):
    name = TextField("Name", [validators.input_required(), validators.Length(1, 255)])
    password = PasswordField("Password", [validators.input_required(), validators.Length(1,255)])

class ParticipantPasswordForm(Form):
    password = PasswordField("Password", [validators.input_required(), validators.Length(1,255)])

class BeerNameForm(Form):
    name = TextField("Name", [validators.input_required(), validators.Length(1, 255)])

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not haavard.authorized:
            return redirect(url_for("oauth_haavard.login"))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/admin/', methods=["GET", "POST"])
@login_required
def admin_index():
    form = TastingForm(request.form)
    if request.method == "POST" and form.validate():
        try:
            tasting = db.Tastings(year=form.year.data)
            db.db.session.add(tasting)
            for i in range(1, form.beers.data + 1):
                beer = db.Beers(tasting = tasting, number = i, name = "Unrevealed {}".format(i))
                db.db.session.add(beer)
            db.db.session.commit()
            flash("Tasting for year {} created".format(form.year.data))
        except exc.SQLAlchemyError as e:
            db.db.session.rollback()
            current_app.logger.error("Error creating tasting: {}".format(e))
            flash("Error creating tasting for year {}".format(form.year.data), 'error')

    tastings = db.Tastings.query.all()
    return render_template('admin.html', tastings = tastings, form = form)

@bp.route('/admin/<int:year>', methods=["GET", "POST"])
@login_required
def admin_year(year):
    tasting = db.Tastings.query.filter(db.Tastings.year == year).first()
    if not tasting:
        flash("Invalid year")
        return redirect(url_for('admin_index'))

    form = ParticipantForm(request.form)
    return render_template('admin_year.html', tasting = tasting, participant_form=form)

@bp.route('/admin/<int:year>/participant', methods=["POST"])
@login_required
def new_participant(year):
    tasting = db.Tastings.query.filter(db.Tastings.year == year).first()
    if not tasting:
        flash("Invalid year")
        return redirect(url_for('admin_index'))

    form = ParticipantForm(request.form)
    if form.validate():
        try:
            password = bcrypt.generate_password_hash(form.password.data)
            participant = db.Participants(tasting = tasting, name = form.name.data, password = password)
            db.db.session.add(participant)
            for beer in tasting.beers:
                look = db.ScoreLook(tasting = tasting, beer = beer, participant = participant)
                db.db.session.add(look)
                smell = db.ScoreSmell(tasting = tasting, beer = beer, participant = participant)
                db.db.session.add(smell)
                taste = db.ScoreTaste(tasting = tasting, beer = beer, participant = participant)
                db.db.session.add(taste)
                aftertaste = db.ScoreAftertaste(tasting = tasting, beer = beer, participant = participant)
                db.db.session.add(aftertaste)
                xmas = db.ScoreXmas(tasting = tasting, beer = beer, participant = participant)
                db.db.session.add(xmas)
            db.db.session.commit()
            flash("Participant {} added".format(form.name.data))
        except exc.SQLAlchemyError as e:
            db.db.session.rollback()
            app.logger.error("Error creating participant: {}".format(e))
            flash("Error creating participant")
    else:
        flash("Invalid form data")

    return redirect("/admin/{}".format(year))

@bp.route('/admin/<int:year>/participant/<int:participant_id>', methods=["POST"])
@login_required
def update_participant(year, participant_id):
    tasting = db.Tastings.query.filter(db.Tastings.year == year).first()
    if not tasting:
        flash("Invalid year")
        return redirect(url_for('admin_index'))

    participant = db.Participants.query.filter(db.Participants.tasting == tasting).filter(db.Participants.id == participant_id).first()
    if not participant:
        flash("Invalid participant")
        return redirect("/admin/{}".format(year))

    form = ParticipantPasswordForm(request.form)
    if form.validate():
        try:
            password = bcrypt.generate_password_hash(form.password.data)
            participant.password = password
            db.db.session.commit()
            flash("Password updated")
        except exc.SQLAlchemyError as e:
            db.db.session.rollback()
            current_app.logger.error("Error updating password: {}".format(e))
            flash("Error updating password")
    else:
        flash("Invalid form data")

    return redirect("/admin/{}".format(year))

@bp.route('/admin/beer/<int:beer_id>', methods=["PUT"])
@login_required
def beer(beer_id):
    beer = db.Beers.query.filter(db.Beers.id == beer_id).first()
    if not beer:
        response = jsonify(error = "Invalid beer id")
        response.status_code = 404
        return response
    form = BeerNameForm(request.form)
    if form.validate():
        try:
            beer.name = form.name.data
            db.db.session.add(beer)
            db.db.session.commit()
            return jsonify(message="Beer name updated")
        except exc.SQLAlchemyError as e:
            db.db.session.rollback()
            current-app.logger.error("Error updating password: {}".format(e))
            response = jsonify(error = "Error updating beer name")
            response.status_code = 500
            return response
    else:
        response = jsonify(error = "Invalid arguments")
        response.status_code = 400
        return response
