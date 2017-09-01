from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class slidepics(db.Model):
    __tablename__ = 'slidepics'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    ext = db.Column(db.String(64))


class products(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    code = db.Column(db.String(256))
    picname = db.Column(db.String(256))
    picext = db.Column(db.String(64))
    psqname = db.Column(db.String(256))
    psqext = db.Column(db.String(64))
    external = db.Column(db.String(256))
    price = db.Column(db.Integer)
    description = db.Column(db.String(256))

