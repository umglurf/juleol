from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import union_all

db = SQLAlchemy()

class Admins(db.Model):
    id = db.Column(db.Integer, autoincrement=True, nullable=False, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)

class Tastings(db.Model):
    id = db.Column(db.Integer, autoincrement=True, nullable=False, primary_key=True)
    year = db.Column(db.Integer, nullable=False, unique=True)
    beers = db.relationship('Beers', back_populates='tasting')
    participants = db.relationship('Participants', back_populates='tasting')
    score_tastes = db.relationship('ScoreTaste', back_populates='tasting')
    score_aftertastes = db.relationship('ScoreAftertaste', back_populates='tasting')
    score_smells = db.relationship('ScoreSmell', back_populates='tasting')
    score_looks = db.relationship('ScoreLook', back_populates='tasting')
    score_xmases = db.relationship('ScoreXmas', back_populates='tasting')

class Beers(db.Model):
    id = db.Column(db.Integer, autoincrement=True, nullable=False, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    number = db.Column(db.SmallInteger, nullable=False)
    tasting_id = db.Column(db.Integer, db.ForeignKey('tastings.id'), nullable=False)
    tasting = db.relationship('Tastings', back_populates='beers')
    score_tastes = db.relationship('ScoreTaste', back_populates='beer')
    score_aftertastes = db.relationship('ScoreAftertaste', back_populates='beer')
    score_smells = db.relationship('ScoreSmell', back_populates='beer')
    score_looks = db.relationship('ScoreLook', back_populates='beer')
    score_xmases = db.relationship('ScoreXmas', back_populates='beer')
    __table_args__ = (db.UniqueConstraint('number', 'tasting_id'), )

class Participants(db.Model):
    id = db.Column(db.Integer, autoincrement=True, nullable=False, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    tasting_id = db.Column(db.Integer, db.ForeignKey('tastings.id'), nullable=False)
    tasting = db.relationship('Tastings', back_populates='participants')
    score_tastes = db.relationship('ScoreTaste', back_populates='participant')
    score_aftertastes = db.relationship('ScoreAftertaste', back_populates='participant')
    score_smells = db.relationship('ScoreSmell', back_populates='participant')
    score_looks = db.relationship('ScoreLook', back_populates='participant')
    score_xmases = db.relationship('ScoreXmas', back_populates='participant')
    __table_args__ = (db.UniqueConstraint('name', 'tasting_id'), )

class ScoreTaste(db.Model):
    id = db.Column(db.Integer, autoincrement=True, nullable=False, primary_key=True)
    score = db.Column(db.SmallInteger, nullable=False)
    beer_id = db.Column(db.Integer, db.ForeignKey('beers.id'), nullable=False)
    beer = db.relationship('Beers', back_populates='score_tastes')
    participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'), nullable=False)
    participant = db.relationship('Participants', back_populates='score_tastes')
    tasting_id = db.Column(db.Integer, db.ForeignKey('tastings.id'), nullable=False)
    tasting = db.relationship('Tastings', back_populates='score_tastes')
    __table_args__ = (db.UniqueConstraint('name', 'tasting_id'), )
    __table_args__ = (db.UniqueConstraint('tasting_id', 'participant_id', 'beer_id'), )

class ScoreAftertaste(db.Model):
    id = db.Column(db.Integer, autoincrement=True, nullable=False, primary_key=True)
    score = db.Column(db.SmallInteger, nullable=True)
    beer_id = db.Column(db.Integer, db.ForeignKey('beers.id'), nullable=False)
    beer = db.relationship('Beers', back_populates='score_aftertastes')
    participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'), nullable=False)
    participant = db.relationship('Participants', back_populates='score_aftertastes')
    tasting_id = db.Column(db.Integer, db.ForeignKey('tastings.id'), nullable=False)
    tasting = db.relationship('Tastings', back_populates='score_aftertastes')
    __table_args__ = (db.UniqueConstraint('name', 'tasting_id'), )
    __table_args__ = (db.UniqueConstraint('tasting_id', 'participant_id', 'beer_id'), )

class ScoreSmell(db.Model):
    id = db.Column(db.Integer, autoincrement=True, nullable=False, primary_key=True)
    score = db.Column(db.SmallInteger, nullable=True)
    beer_id = db.Column(db.Integer, db.ForeignKey('beers.id'), nullable=False)
    beer = db.relationship('Beers', back_populates='score_smells')
    participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'), nullable=False)
    participant = db.relationship('Participants', back_populates='score_smells')
    tasting_id = db.Column(db.Integer, db.ForeignKey('tastings.id'), nullable=False)
    tasting = db.relationship('Tastings', back_populates='score_smells')
    __table_args__ = (db.UniqueConstraint('name', 'tasting_id'), )
    __table_args__ = (db.UniqueConstraint('tasting_id', 'participant_id', 'beer_id'), )

class ScoreLook(db.Model):
    id = db.Column(db.Integer, autoincrement=True, nullable=False, primary_key=True)
    score = db.Column(db.SmallInteger, nullable=True)
    beer_id = db.Column(db.Integer, db.ForeignKey('beers.id'), nullable=False)
    beer = db.relationship('Beers', back_populates='score_looks')
    participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'), nullable=False)
    participant = db.relationship('Participants', back_populates='score_looks')
    tasting_id = db.Column(db.Integer, db.ForeignKey('tastings.id'), nullable=False)
    tasting = db.relationship('Tastings', back_populates='score_looks')
    __table_args__ = (db.UniqueConstraint('name', 'tasting_id'), )
    __table_args__ = (db.UniqueConstraint('tasting_id', 'participant_id', 'beer_id'), )

class ScoreXmas(db.Model):
    id = db.Column(db.Integer, autoincrement=True, nullable=False, primary_key=True)
    score = db.Column(db.SmallInteger, nullable=True)
    beer_id = db.Column(db.Integer, db.ForeignKey('beers.id'), nullable=False)
    beer = db.relationship('Beers', back_populates='score_xmases')
    participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'), nullable=False)
    participant = db.relationship('Participants', back_populates='score_xmases')
    tasting_id = db.Column(db.Integer, db.ForeignKey('tastings.id'), nullable=False)
    tasting = db.relationship('Tastings', back_populates='score_xmases')
    __table_args__ = (db.UniqueConstraint('name', 'tasting_id'), )
    __table_args__ = (db.UniqueConstraint('tasting_id', 'participant_id', 'beer_id'), )

def get_beer_scores(tasting):
    s1 = db.session.query(Beers.id.label('beer_id'), Beers.tasting_id.label('tasting_id'), Beers.number.label('number'), ScoreLook.score.label('score'), ScoreLook.participant_id.label('participant_id')).join(ScoreLook)
    s2 = db.session.query(Beers.id.label('beer_id'), Beers.tasting_id.label('tasting_id'), Beers.number.label('number'), ScoreSmell.score.label('score'), ScoreSmell.participant_id.label('participant_id')).join(ScoreSmell)
    s3 = db.session.query(Beers.id.label('beer_id'), Beers.tasting_id.label('tasting_id'), Beers.number.label('number'), ScoreTaste.score.label('score'), ScoreTaste.participant_id.label('participant_id')).join(ScoreTaste)
    s4 = db.session.query(Beers.id.label('beer_id'), Beers.tasting_id.label('tasting_id'), Beers.number.label('number'), ScoreAftertaste.score.label('score'), ScoreAftertaste.participant_id.label('participant_id')).join(ScoreAftertaste)
    s5 = db.session.query(Beers.id.label('beer_id'), Beers.tasting_id.label('tasting_id'), Beers.number.label('number'), ScoreXmas.score.label('score'), ScoreXmas.participant_id.label('participant_id')).join(ScoreXmas)
    s = union_all(s1, s2, s3, s4, s5).alias('s')
    scores = db.session.query(db.func.sum(s.c.score).label('sum'), s.c.beer_id.label('beer_id'), Participants.id.label('participant_id')).join(Participants, s.c.participant_id == Participants.id).group_by(Participants.id, s.c.beer_id, s.c.tasting_id).subquery()
    details = {}
    for beer in Beers.query.filter(Beers.tasting_id == tasting.id).all():
        details[beer.number] = db.session.query(scores.c.sum, Participants.name).join(Participants, Participants.id == scores.c.participant_id).join(Beers, Beers.id == scores.c.beer_id).filter(Beers.id == beer.id).all()
    return {
            "totals": db.session.query(db.func.sum(scores.c.sum).label('sum'), db.func.avg(scores.c.sum).label('avg'), db.func.std(scores.c.sum).label('std'), Beers.name, Beers.number).join(Beers, Beers.id == scores.c.beer_id).filter(Beers.tasting_id == tasting.id).group_by(scores.c.beer_id).all(),
            "details": details
            }

def participant_scores(participant):
    scores = db.session.query(Beers.number, Beers.name, ScoreLook.score.label('look'), ScoreSmell.score.label('smell'), ScoreTaste.score.label('taste'), ScoreAftertaste.score.label('aftertaste'), ScoreXmas.score.label('xmas')).\
            join(ScoreLook).\
            join(ScoreSmell).\
            join(ScoreTaste).\
            join(ScoreAftertaste).\
            join(ScoreXmas).\
            filter(ScoreLook.participant_id == participant.id).\
            filter(ScoreSmell.participant_id == participant.id).\
            filter(ScoreTaste.participant_id == participant.id).\
            filter(ScoreAftertaste.participant_id == participant.id).\
            filter(ScoreXmas.participant_id == participant.id).\
            order_by(Beers.number).\
            all()
    return scores

#return db.session.query(scores, Beers.name).join(Beers, Beers.id == scores.c.beer_id).filter(Beers.tasting_id == tasting.id).all()
#d.db.session.query(scores, d.Participants.name).filter(scores.c.beer_id == 228).join(d.Participants, d.Participants.id == scores.c.participant_id).all()
#d.db.session.query(d.db.func.sum(scores.c.sum), d.db.func.avg(scores.c.sum), d.db.func.std(scores.c.sum), scores.c.beer_id).filter(scores.c.beer_id > 227).filter(scores.c.beer_id < 231).group_by(scores.c.beer_id).all()
