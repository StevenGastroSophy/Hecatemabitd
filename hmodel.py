from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class slidepics(db.Model):
    __tablename__ = 'slidepics'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False, unique=True)
    ext = db.Column(db.String)


class products(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False, unique=True)
    codename = db.Column(db.String, unique=True)
    description = db.Column(db.Text)
    price = db.Column(db.Integer, nullable=False)
    productpictures_id = db.Column(db.Integer, db.ForeignKey('productpictures.id'))
    orderitems= db.relationship('orderitems',
                               backref='products',
                               lazy='dynamic')

class productpictures(db.Model):
    __tablename__ = 'productpictures'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    picname = db.Column(db.String, unique=True)
    picext = db.Column(db.String)
    psqname = db.Column(db.String, unique=True)
    psqext = db.Column(db.String)
    products= db.relationship('products',
                               backref='productpictures',
                               lazy='dynamic')

class order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, nullable=False)
    hope_time = db.Column(db.String, nullable=False)
    channel = db.Column(db.String, nullable=False)
    ps = db.Column(db.String)
    code= db.Column(db.String, nullable=False, unique=True)
    totalamount = db.Column(db.Integer, nullable=False)
    orderitems= db.relationship('orderitems',
                               backref='order',
                               lazy='dynamic')

class orderitems(db.Model):
    __tablename__ = 'orderitems'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Integer, nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    products_id = db.Column(db.Integer, db.ForeignKey('products.id'))
        
class hecatestatus(db.Model):
    __tablename__ = 'hecatestatus'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status = db.Column(db.String, nullable=False)
    channel = db.Column(db.String)

