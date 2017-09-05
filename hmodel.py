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
    description = db.Column(db.String(256))
    picname = db.Column(db.String(256))
    picext = db.Column(db.String(64))
    psqname = db.Column(db.String(256))
    psqext = db.Column(db.String(64))
    price = db.Column(db.Integer)

class hecatestatus(db.Model):
    __tablename__ = 'hecatestatus'
    id = db.Column(db.String(256), primary_key=True)
    status = db.Column(db.String(256))
    channel = db.Column(db.String(256))
