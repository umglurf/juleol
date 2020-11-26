# SPDX-FileCopyrightText: 2020 Håvard Moen <post@haavard.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from functools import wraps
from juleol import db
from sqlalchemy import exc
from wtforms import Form, BooleanField, IntegerField, validators, StringField
from wtforms.fields.html5 import EmailField
from wtforms.widgets.html5 import NumberInput

bp = Blueprint('admin', __name__)


class TastingForm(Form):
    year = IntegerField(
        'Year',
        [validators.input_required(), validators.NumberRange(2000, 2100)],
        widget=NumberInput(min=2000, max=2100)
        )
    beers = IntegerField(
        'Number of beers',
        [validators.input_required(), validators.NumberRange(1, 100)],
        widget=NumberInput(min=1, max=100)
        )


class LockedForm(Form):
    locked = BooleanField("Locked", [validators.input_required(), validators.AnyOf([True, False])])


class ParticipantForm(Form):
    name = StringField("Name", [validators.input_required(), validators.Length(1, 255)])
    email = EmailField("Email", [validators.input_required(), validators.Length(1, 255), validators.Email()])


class ParticipantEmailForm(Form):
    email = EmailField("Email", [validators.input_required(), validators.Length(1, 255), validators.Email()])


class BeerHeatForm(Form):
    heat = IntegerField("Heat", [validators.input_required()])


class BeerNameForm(Form):
    name = StringField("Name", [validators.input_required(), validators.Length(1, 255)])


class NoteForm(Form):
    note = StringField("Note", [validators.input_required()])


class HeatForm(Form):
    name = StringField("Heat", [validators.input_required()])


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_app.config.get('admin_oauth').authorized:
            return redirect(url_for(current_app.config.get('admin_oauth_login')))
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
                new_beer = db.Beers(tasting=tasting, number=i, name="Unrevealed {}".format(i))
                db.db.session.add(new_beer)
            db.db.session.commit()
            flash("Tasting for year {} created".format(form.year.data))
        except exc.SQLAlchemyError as e:
            db.db.session.rollback()
            current_app.logger.error("Error creating tasting: {}".format(e))
            flash("Error creating tasting for year {}".format(form.year.data), 'error')

    tastings = db.Tastings.query.all()
    return render_template('admin.html', tastings=tastings, form=form)


@bp.route('/admin/<int:year>', methods=["GET"])
@login_required
def admin_year(year):
    tasting = db.Tastings.query.filter(db.Tastings.year == year).first()
    if not tasting:
        flash("Invalid year", 'error')
        return redirect(url_for('admin.admin_index'))

    participant_form = ParticipantForm(request.form)
    note_form = NoteForm(request.form)
    heat_form = HeatForm(request.form)
    return render_template(
        'admin_year.html',
        tasting=tasting,
        participant_form=participant_form,
        note_form=note_form,
        heat_form=heat_form
        )


@bp.route('/admin/tasting/<int:year>', methods=["PUT"])
@login_required
def update_tasting(year):
    tasting = db.Tastings.query.filter(db.Tastings.year == year).first()
    if not tasting:
        response = jsonify(error="Invalid year")
        response.status_code = 404
        return response

    locked_form = LockedForm(request.form)
    if locked_form.validate():
        try:
            tasting.locked = locked_form.locked.data
            db.db.session.add(tasting)
            db.db.session.commit()
            return jsonify(message="Locked status updated")
        except exc.SQLAlchemyError as e:
            db.db.session.rollback()
            current_app.logger.error("Error updating tasting: {}".format(e))
            response = jsonify(error="Error updating tasting")
            response.status_code = 500
            return response
    else:
        response = jsonify(error="Invalid arguments")
        response.status_code = 400
        return response


@bp.route('/admin/<int:year>/participant', methods=["POST"])
@login_required
def new_participant(year):
    tasting = db.Tastings.query.filter(db.Tastings.year == year).first()
    if not tasting:
        flash("Invalid year", 'error')
        return redirect(url_for('admin.admin_index'))

    form = ParticipantForm(request.form)
    if form.validate():
        try:
            participant = db.Participants(tasting=tasting, name=form.name.data, email=form.email.data)
            db.db.session.add(participant)
            for beer in tasting.beers:
                look = db.ScoreLook(tasting=tasting, beer=beer, participant=participant)
                db.db.session.add(look)
                smell = db.ScoreSmell(tasting=tasting, beer=beer, participant=participant)
                db.db.session.add(smell)
                taste = db.ScoreTaste(tasting=tasting, beer=beer, participant=participant)
                db.db.session.add(taste)
                aftertaste = db.ScoreAftertaste(tasting=tasting, beer=beer, participant=participant)
                db.db.session.add(aftertaste)
                xmas = db.ScoreXmas(tasting=tasting, beer=beer, participant=participant)
                db.db.session.add(xmas)
            db.db.session.commit()
            flash("Participant {} added".format(form.name.data))
        except exc.SQLAlchemyError as e:
            db.db.session.rollback()
            current_app.logger.error("Error creating participant: {}".format(e))
            flash("Error creating participant", 'error')
    else:
        flash("Invalid form data", 'error')

    return redirect("/admin/{}".format(year))


@bp.route('/admin/<int:year>/participant/<int:participant_id>', methods=["POST"])
@login_required
def update_participant(year, participant_id):
    tasting = db.Tastings.query.filter(db.Tastings.year == year).first()
    if not tasting:
        flash("Invalid year", 'error')
        return redirect(url_for('admin.admin_index'))

    participant = db.Participants.query.filter(
        db.Participants.tasting == tasting
        ).filter(
            db.Participants.id == participant_id
            ).first()
    if not participant:
        flash("Invalid participant", 'error')
        return redirect("/admin/{}".format(year))

    form = ParticipantEmailForm(request.form)
    if form.validate():
        try:
            participant.email = form.email.data
            db.db.session.add(participant)
            db.db.session.commit()
            flash("Email updated", 'error')
        except exc.SQLAlchemyError as e:
            db.db.session.rollback()
            current_app.logger.error("Error updating email: {}".format(e))
            flash("Error updating email", 'error')
    else:
        flash("Invalid form data", 'error')

    return redirect("/admin/{}".format(year))


@bp.route('/admin/<int:year>/heat', methods=["POST"])
@login_required
def new_heat(year):
    tasting = db.Tastings.query.filter(db.Tastings.year == year).first()
    if not tasting:
        flash("Invalid year", 'error')
        return redirect(url_for('admin.admin_index'))

    form = HeatForm(request.form)
    if form.validate():
        try:
            heat = db.Heats(tasting=tasting, name=form.name.data)
            db.db.session.add(heat)
            db.db.session.commit()
            flash("Heat added")
        except exc.SQLAlchemyError as e:
            db.db.session.rollback()
            current_app.logger.error("Error creating heat: {}".format(e))
            flash("Error creating heat", 'error')
    else:
        flash("Invalid form data", 'error')

    return redirect("/admin/{}".format(year))


@bp.route('/admin/heat/<int:heat_id>', methods=["GET", "PUT", "DELETE"])
@login_required
def update_heat(heat_id):
    heat = db.Heats.query.filter(db.Heats.id == heat_id).first()
    if not heat:
        response = jsonify(error="Invalid heat id")
        response.status_code = 404
        return response
    if request.method == 'GET':
        return jsonify({'id': heat.id, 'name': heat.name})
    elif request.method == 'PUT':
        form = HeatForm(request.form)
        if form.validate():
            try:
                heat.name = form.name.data
                db.db.session.add(heat)
                db.db.session.commit()
                return jsonify(message="Heat updated")
            except exc.SQLAlchemyError as e:
                db.db.session.rollback()
                current_app.logger.error("Error updating heat: {}".format(e))
                response = jsonify(error="Error updating heat")
                response.status_code = 500
                return response
        else:
            response = jsonify(error="Invalid arguments")
            response.status_code = 400
            return response
    elif request.method == 'DELETE':
        try:
            db.db.session.delete(heat)
            db.db.session.commit()
            return jsonify(message="Heat deleted")
        except exc.SQLAlchemyError as e:
            db.db.session.rollback()
            current_app.logger.error("Error deleting heat: {}".format(e))
            response = jsonify(error="Error deleting heat")
            response.status_code = 500
            return response


@bp.route('/admin/<int:year>/note', methods=["POST"])
@login_required
def new_note(year):
    tasting = db.Tastings.query.filter(db.Tastings.year == year).first()
    if not tasting:
        flash("Invalid year", 'error')
        return redirect(url_for('admin.admin_index'))

    form = NoteForm(request.form)
    if form.validate():
        try:
            note = db.Notes(tasting=tasting, note=form.note.data)
            db.db.session.add(note)
            db.db.session.commit()
            flash("Note added")
        except exc.SQLAlchemyError as e:
            db.db.session.rollback()
            current_app.logger.error("Error creating note: {}".format(e))
            flash("Error creating note", 'error')
    else:
        flash("Invalid form data", 'error')

    return redirect("/admin/{}".format(year))


@bp.route('/admin/note/<int:note_id>', methods=["GET", "PUT", "DELETE"])
@login_required
def update_note(note_id):
    note = db.Notes.query.filter(db.Notes.id == note_id).first()
    if not note:
        response = jsonify(error="Invalid note id")
        response.status_code = 404
        return response
    if request.method == 'GET':
        return jsonify({'id': note.id, 'note': note.note})
    elif request.method == 'PUT':
        form = NoteForm(request.form)
        if form.validate():
            try:
                note.note = form.note.data
                db.db.session.add(note)
                db.db.session.commit()
                return jsonify(message="Note updated")
            except exc.SQLAlchemyError as e:
                db.db.session.rollback()
                current_app.logger.error("Error updating note: {}".format(e))
                response = jsonify(error="Error updating note")
                response.status_code = 500
                return response
        else:
            response = jsonify(error="Invalid arguments")
            response.status_code = 400
            return response
    elif request.method == 'DELETE':
        try:
            db.db.session.delete(note)
            db.db.session.commit()
            return jsonify(message="Note deleted")
        except exc.SQLAlchemyError as e:
            db.db.session.rollback()
            current_app.logger.error("Error deleting note: {}".format(e))
            response = jsonify(error="Error deleting note")
            response.status_code = 500
            return response


@bp.route('/admin/beer/<int:beer_id>', methods=["PUT"])
@login_required
def beer(beer_id):
    beer = db.Beers.query.filter(db.Beers.id == beer_id).first()
    if not beer:
        response = jsonify(error="Invalid beer id")
        response.status_code = 404
        return response
    heat_form = BeerHeatForm(request.form)
    name_form = BeerNameForm(request.form)
    if heat_form.validate():
        heat = db.Heats.query.filter(db.Heats.tasting == beer.tasting).filter(db.Heats.id == heat_form.heat.data).first()
        if not heat:
            response = jsonify(error='Invalid heat')
            response.status_code = 404
            return response
        try:
            beer.heat = heat
            db.db.session.add(beer)
            db.db.session.commit()
            return jsonify(message="Beer heat updated")
        except exc.SQLAlchemyError as e:
            db.db.session.rollback()
            current_app.logger.error("Error updating beer: {}".format(e))
            response = jsonify(error="Error updating beer heat")
            response.status_code = 500
            return response
    if name_form.validate():
        try:
            beer.name = name_form.name.data
            db.db.session.add(beer)
            db.db.session.commit()
            return jsonify(message="Beer name updated")
        except exc.SQLAlchemyError as e:
            db.db.session.rollback()
            current_app.logger.error("Error updating beer: {}".format(e))
            response = jsonify(error="Error updating beer name")
            response.status_code = 500
            return response
    else:
        response = jsonify(error="Invalid arguments")
        response.status_code = 400
        return response


@bp.route('/admin/beer/<int:beer_id>/heat', methods=["DELETE"])
@login_required
def beer_heat_delete(beer_id):
    beer = db.Beers.query.filter(db.Beers.id == beer_id).first()
    if not beer:
        response = jsonify(error="Invalid beer id")
        response.status_code = 404
        return response
    try:
        beer.heat = None
        db.db.session.add(beer)
        db.db.session.commit()
        return jsonify(message="Beer heat deleted")
    except exc.SQLAlchemyError as e:
        db.db.session.rollback()
        current_app.logger.error("Error updating beer: {}".format(e))
        response = jsonify(error="Error deleting beer heat")
        response.status_code = 500
        return response
