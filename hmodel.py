from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class slidepics(db.Model):
    __tablename__ = 'slidepics'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ext = db.Column(db.String)


class products(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    code = db.Column(db.String)
    description = db.Column(db.Text)
    price = db.Column(db.Integer)
    productpictures_id = db.Column(db.Integer, db.ForeignKey('productpictures.id'))


class productpictures(db.Model):
    __tablename__ = 'productpictures'
    id = db.Column(db.Integer, primary_key=True)
    picname = db.Column(db.String)
    picext = db.Column(db.String)
    psqname = db.Column(db.String)
    psqext = db.Column(db.String)
    products= db.relationship('products',
                               backref='productpictures',
                               lazy='dynamic')

        
class hecatestatus(db.Model):
    __tablename__ = 'hecatestatus'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String)
    channel = db.Column(db.String)

