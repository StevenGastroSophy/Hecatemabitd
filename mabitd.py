from threading import Lock
from flask import Flask, render_template, request, url_for, redirect, jsonify, session
from flask_socketio import SocketIO, emit, disconnect
import os
import sys
from hmodel import db, slidepics, products, hecatestatus


async_mode = None
mabitdpostgre = os.getenv('mabitdpostgre', None)
ConfigSecretKey = os.getenv('mabitdconfigsecretkey', None)
AppSecretKey = os.getenv('mabitdappsecretkey', None)

if mabitdpostgre is None:
    print('Specify mabitdpostgre as environment variable.')
    sys.exit(1)
if ConfigSecretKey is None:
    print('Specify mabitdconfigsecretkey as environment variable.')
    sys.exit(1)
if AppSecretKey is None:
    print('Specify mabitdappsecretkey as environment variable.')
    sys.exit(1)

app = Flask(__name__)
app.config['SECRET_KEY'] = ConfigSecretKey
app.config['SQLALCHEMY_DATABASE_URI'] = mabitdpostgre
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
db.init_app(app)
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()

app.secret_key = AppSecretKey

def pathbyname(name, ext):
    return '{folder}/{file}.{filetype}'.format(folder = 'img', file = name, filetype = ext)

def mabipricestyle(price):
    pricelist = []
    w = int(int(price )/10000)
    k = int(int(price )%10000)
    if w  is not 0:
        pricelist.append(str(w))
    if k  is not 0:
        pricelist.append(str(k))
    else:
        pricelist.append('')
    return '萬'.join(pricelist)

class readproduct:
    def __init__(self, orderby):
        self.data_products = products.query.order_by(orderby).all()
        self.productdict = dict()
        self.productlist = list()
    def addstuff(self, defaultid = None):
        self.defaultproduct = None
        print("defaultid is "+str(defaultid))
        print("self.defaultproduct is "+str(self.defaultproduct))
        for data in self.data_products:
            if defaultid:
                if data.id == defaultid:
                    self.defaultproduct = data.name
                    print("self.defaultproduct is "+str(self.defaultproduct))
            
            self.productdict[data.name] = [pathbyname(data.picname, data.picext),
                                           pathbyname(data.psqname, data.psqext),
                                           data.id,
                                           data.price,
                                           data.description,
                                           data.external]
            self.productlist.append(data.name)

@app.route('/_update_cart', methods=['POST'])
def update_cart():
    namelist = request.form.getlist('namelist[]')
    session['name'] = namelist
    print(session.get('name'))
    pricelist = request.form.getlist('pricelist[]')
    session['price'] = pricelist
    print(session.get('price'))
    quantitylist = request.form.getlist('quantitylist[]')
    session['quantity'] = quantitylist
    print(session.get('quantity'))
    totalamount = request.form.get('totalamount')
    session['totalamount'] = totalamount
    print(session.get('totalamount'))
    CartCount = request.form.get('CartCount')
    session['CartCount'] = CartCount
    print(session.get('CartCount'))
    return 'OK', 200

def create_app():
    with app.app_context():
        # Extensions like Flask-SQLAlchemy now know what the "current" app
        # is while within this block. Therefore, you can now run........
        db.create_all()
    return app

def check_status():
    while True:
        socketio.sleep(10)
        create_app().app_context().push()
        data_hecatestatus = hecatestatus.query.first()
        status = data_hecatestatus.status
        channel = data_hecatestatus.channel
        print(status, channel)
        socketio.emit('my_response',
                      {'status': status, 'channel': channel},
                      namespace='/test')

#上下線調整功能暫時開放所有人使用
@app.route('/status/online/<int:channel>', methods=['GET'])
def switch_online(channel):
    if 0< channel <=99:
        hecatestatus.query.filter_by(id=1).update({'status':'ONLINE', 'channel': channel})
        db.session.commit()
        return 'ONLINE '+str(channel)
    else:
        abort(404)

@app.route('/status/offline', methods=['GET'])
def switch_offline():
    hecatestatus.query.filter_by(id=1).update({'status':'OFFLINE', 'channel': 0})
    db.session.commit()
    return 'OFFLINE'

@app.route('/_another_product', methods=['GET'])
def another_product():
    productname = request.args.get('productname')
    getproduct = readproduct(products.id)
    getproduct.addstuff()
    resultdict = dict()
    resultdict['resultpic'] = getproduct.productdict[productname][0]
    resultdict['resultname'] = productname
    resultdict['resultprice'] = getproduct.productdict[productname][3]
    resultdict['resultdescription'] = getproduct.productdict[productname][4]
    return jsonify(resultdict)

@app.route('/products', methods=['GET'])
def productpage():
    defaultproductid = int(request.args.get('default'))
    print("defaultproductid is "+str(defaultproductid))
    print(type(defaultproductid))
    getproduct = readproduct(products.id)
    getproduct.addstuff(defaultproductid)

    CartNameList = session.get('name')
    CartPriceList = session.get('price')
    CartQuantityList = session.get('quantity')
    if session.get('totalamount'):
        totalamount = session.get('totalamount')
    else:
        totalamount = 0
    if session.get('CartCount'):
        Cartcount = session.get('CartCount')
    else:
        Cartcount = 0

    data_hecatestatus = hecatestatus.query.first()
    status = data_hecatestatus.status
    channel = data_hecatestatus.channel
    return render_template('products.html',
                           productdict = getproduct.productdict,
                           productlist = getproduct.productlist,
                           default = getproduct.defaultproduct,
                           CartNameList = CartNameList,
                           CartPriceList = CartPriceList,
                           CartQuantityList = CartQuantityList,
                           totalamount = totalamount,
                           CartCount = Cartcount,
                           status = status,
                           channel = channel,
                           async_mode=socketio.async_mode)


@app.route('/', methods=['GET'])
def index():
    data_slidepics = slidepics.query.order_by(slidepics.id).all()
    slidelist = [pathbyname(data.name,data.ext) for data in data_slidepics]
    print(slidelist)

    getproduct = readproduct(products.id)
    getproduct.addstuff()

    CartNameList = session.get('name')
    CartPriceList = session.get('price')
    CartQuantityList = session.get('quantity')
    if session.get('totalamount'):
        totalamount = session.get('totalamount')
    else:
        totalamount = 0
    if session.get('CartCount'):
        Cartcount = session.get('CartCount')
    else:
        Cartcount = 0
    data_hecatestatus = hecatestatus.query.first()
    status = data_hecatestatus.status
    channel = data_hecatestatus.channel
    return render_template('index.html',
                           slidelist = slidelist,
                           productdict = getproduct.productdict,
                           productlist = getproduct.productlist,
                           CartNameList = CartNameList,
                           CartPriceList = CartPriceList,
                           CartQuantityList = CartQuantityList,
                           totalamount = totalamount,
                           CartCount = Cartcount,
                           status = status,
                           channel = channel,
                           async_mode=socketio.async_mode)

@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock: #thread_lock.acquire() = __enter__跟thread_lock.release() = __exit__
        if thread is None:
            thread = socketio.start_background_task(target=check_status)

if __name__ == '__main__':
    socketio.run(app,host='0.0.0.0',port=os.environ['PORT'])


