from app import db


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    hash = db.Column(db.String(64))


class Word(db.Model):
    __tablename__ = 'words'

    id = db.Column(db.String(128), primary_key=True)
    text = db.Column(db.String(256))
    count = db.Column(db.Integer)
    comment_id = db.Column(db.ForeignKey('comments.id'))
    comment = db.relationship('Comment', backref='words')
