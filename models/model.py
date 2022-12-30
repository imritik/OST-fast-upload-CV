from models.db import db

class Keyword(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    file = db.relationship(
        "KeywordFile", backref=db.backref('keyword', uselist=False), lazy='dynamic')
    is_active = db.Column(db.Boolean, default=False, nullable=False)


class KeywordFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    primaryfile = db.Column(db.LargeBinary(), nullable=False)
    secondaryfile = db.Column(db.LargeBinary())

    keyword_id = db.Column(db.Integer, db.ForeignKey('keyword.id'))

    def __repr__(self) -> str:
        return self.name