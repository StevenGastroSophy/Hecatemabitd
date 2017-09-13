from threading import Lock
from flask import Flask, render_template, request, url_for, redirect, jsonify, session
from flask_session import Session
from flask_socketio import SocketIO, emit, disconnect
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, InputRequired
from os import getenv, environ
import sys
import time
from math import modf
from random import randint
from hmodel import db, slidepics, products, productpictures, order, orderitems, hecatestatus


async_mode = None
mabitdpostgre = getenv('mabitdpostgre', None)
ConfigSecretKey = getenv('mabitdconfigsecretkey', None)
AppSecretKey = getenv('mabitdappsecretkey', None)

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
app.config['SESSION_TYPE'] = 'filesystem'
#app.config['SESSION_TYPE'] = 'sqlalchemy'
#app.config['SESSION_SQLALCHEMY'] = db
Session(app)
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()

app.secret_key = AppSecretKey

def create_app():
    with app.app_context():
        # Extensions like Flask-SQLAlchemy now know what the "current" app
        # is while within this block. Therefore, you can now run........
        db.create_all()
    return app

#產生檔案路徑
def pathbyname(name, ext):
    return '{folder}/{file}.{filetype}'.format(folder = 'img', file = name, filetype = ext)

#產生訂單編號
def createcode(time):
    INTtimestamp = int(time)
    RandomThree = randint(100,999)
    millisecond = int(round(modf(time)[0],2)*100)
    return str(INTtimestamp)+str(RandomThree)+str(millisecond)

#將純數字的價格轉成瑪奇格式的價格
def mabipricestyle(price):
    if int(price) >= 10000 and int(int(price)%10000) != 0:
        return '萬'.join([str(int(int(price)/10000)), str(int(int(price)%10000))])
    elif int(price) >= 10000 and int(int(price)%10000) == 0:
        return str(int(int(price)/10000))+'萬'
    else:
        return str(price)

#將瑪奇格式的價格轉成純數字的價格
def demabipricestyle(price):
    if '萬' in price and  price.split('萬')[1]:
        return int(price.split('萬')[0])*10000+int(price.split('萬')[1])
    elif '萬' in price and not price.split('萬')[1]:
        return int(price.strip('萬'))*10000
    else:
        return int(price)
    
#查詢資料庫內的產品資料
class readproduct:
    def __init__(self, data_object, defaultid = None):
        self.data_products = data_object #傳入資料庫查詢物件
        self.defaultid = defaultid #傳入預設的產品名稱，可選值
        
    @property
    def productdict(self):
        productdict = dict()
        #data_products回傳list的情況
        if isinstance(self.data_products, list):
            for data in self.data_products:
                productdict[data.name] = [pathbyname(data.productpictures.picname, data.productpictures.picext), 
                                          pathbyname(data.productpictures.psqname, data.productpictures.psqext),
                                          data.id,
                                          mabipricestyle(data.price), #瑪奇格式,XXXX萬XXXX
                                          data.description]
            return productdict
        #data_products回傳單個物件的情況
        else:
            productdict[self.data_products.name] = [pathbyname(self.data_products.productpictures.picname, self.data_products.productpictures.picext), 
                                                    pathbyname(self.data_products.productpictures.psqname, self.data_products.productpictures.psqext),
                                                    self.data_products.id,
                                                    mabipricestyle(self.data_products.price), #瑪奇格式,XXXX萬XXXX
                                                    self.data_products.description]
            return productdict
    @property
    def productlist(self):
        if isinstance(self.data_products, list):
            productlist = [data.name for data in self.data_products]
            return productlist
        else:
            raise Exception("productlist只能在data_object回傳list的情況使用")
    @property
    def defaultproduct(self):
        if isinstance(self.data_products, list):
            if self.defaultid:
                for data in self.data_products:
                    if  data.id == self.defaultid:
                        print("defaultproduct is "+data.name)
                        return data.name
            else:
               raise Exception("記得在建立readproduct實例的時候傳入defaultid")                     
        else:
            raise Exception("defaultproduct只能在data_object回傳list的情況使用")

#結帳頁(/pay)表單        
class PayForm(FlaskForm):
    User_id = StringField(validators=[InputRequired(), DataRequired()])
    Hope_time = SelectField(choices=[('{h}:00'.format(h=i),'{h}:00'.format(h=i)) for i in range(19,25)],validators=[DataRequired()])
    Hope_channel = SelectField(choices=[(str(i), str(i)) for i in range(1,13)],validators=[DataRequired()])
    PS = TextAreaField()

#訂單查詢頁(/yourorder)表單
class OrderForm(FlaskForm):
    Order_code = IntegerField(validators=[InputRequired(), DataRequired()])

#檢查session裡面的price跟資料庫是否一致
def CheckSession(session, productdict):
    session_in = session
    try:
        for i in range(len(session_in['name'])):
            if productdict[session_in['name'][i]][3] != session_in['price'][i]: #如果session的價格跟查到的價格不一樣
                print(session_in['name'][i]+'\'s price has been modified from '+str(session['price'][i]))
                session['price'][i] = productdict[session_in['name'][i]][3]
                session['subtotal'][i] = mabipricestyle(demabipricestyle(productdict[session_in['name'][i]][3])*int(session['quantity'][i])) #session['quantity'][i]是string
                session['totalamount'] = mabipricestyle(sum([demabipricestyle(subtotal) for subtotal in session['subtotal']]))
                print(session_in['name'][i]+'\'s price has been modified to '+str(session['price'][i]))
            elif i == (len(session_in['name'])-1):
                print('All prices were checked')
            else:
                pass
    except:
        pass
        

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

#接收購物車訊息，記錄於session
@app.route('/_update_cart', methods=['POST'])
def update_cart():
    namelist = request.form.getlist('namelist[]')
    session['name'] = namelist
    print(session.get('name'))
    pricelist = request.form.getlist('pricelist[]')
    session['price'] = pricelist #['XXXX萬XXXX','YYY萬YYYY']
    print(session.get('price')) 
    quantitylist = request.form.getlist('quantitylist[]')
    session['quantity'] = quantitylist #[X,Y]
    print(session.get('quantity'))
    subtotallist = request.form.getlist('subtotallist[]')
    session['subtotal'] = subtotallist #['XXXX萬XXXX','YYY萬YYYY']
    print(session.get('subtotal'))
    
    totalamount = request.form.get('totalamount')
    session['totalamount'] = totalamount #XXXX萬XXXX
    print(session.get('totalamount'))
    CartCount = request.form.get('CartCount')
    session['CartCount'] = CartCount #X
    print('CartCount is'+str(session.get('CartCount')))
    PackCount = request.form.get('PackCount') #Y
    session['PackCount'] = PackCount
    print(session.get('PackCount'))
    return 'OK', 200

#用ajax刷新結帳頁面
@app.route('/_paycontent_reset', methods=['GET'])
def reset_paycontent():
    data_object = products.query.order_by(products.id).all()
    getproduct = readproduct(data_object)
    productdict = getproduct.productdict
    resultdict = dict()
    resultdict['resultpic'] = [productdict[name][0] for name in session.get('name')]
    resultdict['resultname'] = session.get('name')
    resultdict['resultprice'] = session.get('price')
    resultdict['resultquantity'] = session.get('quantity')
    resultdict['resultsubtotal'] = session.get('subtotal')
    resultdict['resulttotalamount'] = session.get('totalamount')
    resultdict['PackCount'] = session.get('PackCount')
    print('/_paycontent_reset success!')
    return jsonify(resultdict)

#用ajax調整當前顯示的產品內容
@app.route('/_another_product', methods=['GET'])
def another_product():
    productname = request.args.get('productname')
    data_object = products.query.filter_by(name=productname).first()
    getproduct = readproduct(data_object)
    productdict = getproduct.productdict
    resultdict = dict()
    resultdict['resultpic'] = productdict[productname][0]
    resultdict['resultname'] = productname
    resultdict['resultprice'] = productdict[productname][3]
    resultdict['resultdescription'] = productdict[productname][4]
    return jsonify(resultdict)

#結帳頁面
@app.route('/pay', methods=['GET', 'POST'])
def paymentpage():
    form = PayForm()
    
    if request.method == 'GET':
        try:
            if int(session['CartCount']) > 0:
                data_object = products.query.order_by(products.id).all()
                getproduct = readproduct(data_object)
                productdict = getproduct.productdict
    
                CheckSession(session, productdict)
        
                data_hecatestatus = hecatestatus.query.first()
                status = data_hecatestatus.status
                channel = data_hecatestatus.channel

                return render_template('payment.html',
                                       productdict = productdict,
                                       form = form,
                                       status = status,
                                       channel = channel,
                                       async_mode=socketio.async_mode)
            else:
                return redirect(url_for('productpage'))
        except:
            print('Redirect')
            return redirect(url_for('productpage'))
    if request.method == 'POST':
        try:
            if int(session['CartCount']) > 0 and form.validate_on_submit():
                print("Validate!")
                data_object = products.query.order_by(products.id).all()
                getproduct = readproduct(data_object)
                productdict = getproduct.productdict
                
                CheckSession(session, productdict)

                Orderitem=dict()
                Orderitem['name'] = session.get('name')
                Orderitem['price'] = session.get('price')
                Orderitem['quantity'] = session.get('quantity')
                Orderitem['subtotal'] = session.get('subtotal')
                Orderitem['totalamount'] = session.get('totalamount')
                Orderitem['PackCount'] = session.get('PackCount')

                session.clear()
                
                User_id = form.User_id.data
                Hope_time = form.Hope_time.data
                Hope_channel = form.Hope_channel.data
                PS = form.PS.data

                timestamp = time.time()
                code = createcode(timestamp)

                new_order = order(username = User_id,
                                  hope_time = Hope_time,
                                  channel = Hope_channel,
                                  ps = PS,
                                  code = code,
                                  totalamount = demabipricestyle(Orderitem.get('totalamount')))
                orderitemlist = [orderitems(name = Orderitem['name'][i],
                                            price = demabipricestyle(Orderitem['price'][i]),
                                            quantity = Orderitem['quantity'][i],
                                            subtotal = demabipricestyle(Orderitem['subtotal'][i]), order=new_order) for i in range(int(Orderitem['PackCount']))]
                db.session.add(new_order)
                for data in orderitemlist:
                     db.session.add(data)
                db.session.commit()

                data_hecatestatus = hecatestatus.query.first()
                status = data_hecatestatus.status
                channel = data_hecatestatus.channel

                return render_template('paysuccess.html',
                                       productdict = productdict,
                                       Orderitem = Orderitem,
                                       User_id = User_id,
                                       Hope_time = Hope_time,
                                       Hope_channel = Hope_channel,
                                       PS = PS,
                                       code = code,
                                       status = status,
                                       channel = channel,
                                       async_mode=socketio.async_mode)
            else:
                print('Redirect due to invalid value')
                return redirect(url_for('productpage'))
        except:
            print('Redirect')
            return redirect(url_for('productpage'))       

@app.route('/yourorder', methods=['GET', 'POST'])
def orderpage():
    form = OrderForm()
    
    if request.method == 'GET':
        data_object = products.query.order_by(products.id).all()
        getproduct = readproduct(data_object)
        productdict = getproduct.productdict
        
        CheckSession(session, productdict)
        
        data_hecatestatus = hecatestatus.query.first()
        status = data_hecatestatus.status
        channel = data_hecatestatus.channel

        return render_template('yourorder.html',
                                form = form,
                                status = status,
                                channel = channel,
                                async_mode=socketio.async_mode)
    if request.method == 'POST':
        if form.validate_on_submit():
            print("Validate!")
            data_object = products.query.order_by(products.id).all()
            getproduct = readproduct(data_object)
            productdict = getproduct.productdict
                
            CheckSession(session, productdict)

            data_hecatestatus = hecatestatus.query.first()
            status = data_hecatestatus.status
            channel = data_hecatestatus.channel
                
            Order_code = form.Order_code.data
            try:
                order_object = order.query.filter_by(code=str(Order_code)).first()
                order_id = order_object.id
                order_totalamount = order_object.totalamount
                orderitems_object = orderitems.query.filter_by(order_id=order_id).all()
                Orderitem=dict()
                Orderitem['name'] = [data.name for data in orderitems_object]
                Orderitem['price'] = [mabipricestyle(data.price) for data in orderitems_object]
                Orderitem['quantity'] = [data.quantity for data in orderitems_object]
                Orderitem['subtotal'] = [mabipricestyle(data.subtotal) for data in orderitems_object]
                Orderitem['totalamount'] = mabipricestyle(order_totalamount)
                Orderitem['PackCount'] = len(Orderitem.get('name'))
                User_id = order_object.username
                Hope_time = order_object.hope_time
                Hope_channel = order_object.channel
                PS = order_object.ps
                
                return render_template('paysuccess.html',
                                       productdict = productdict,
                                       Orderitem = Orderitem,
                                       User_id = User_id,
                                       Hope_time = Hope_time,
                                       Hope_channel = Hope_channel,
                                       PS = PS,
                                       code = Order_code,
                                       status = status,
                                       channel = channel,
                                       async_mode=socketio.async_mode)
            except:
                return render_template('yourorderfailed.html',
                                       status = status,
                                       channel = channel,
                                       async_mode=socketio.async_mode)
                
        else:
            print('Redirect due to invalid value')
            return redirect(url_for('yourorder'))      

#產品頁面，接受傳入預設顯示的產品編號
@app.route('/products', methods=['GET'])
def productpage():
    if request.args.get('default'):
        defaultproductid = int(request.args.get('default'))
    else:
        defaultproductid = 1
    data_object = products.query.order_by(products.id).all()
    getproduct = readproduct(data_object, defaultproductid)
    productdict = getproduct.productdict
    productlist = getproduct.productlist
    defaultproduct = getproduct.defaultproduct

    CheckSession(session, productdict)

    print('加載productpage',str(session.get('CartCount')))
    data_hecatestatus = hecatestatus.query.first()
    status = data_hecatestatus.status
    channel = data_hecatestatus.channel
    return render_template('products.html',
                           productdict = productdict,
                           productlist = productlist,
                           default = defaultproduct,
                           status = status,
                           channel = channel,
                           async_mode=socketio.async_mode)

#首頁
@app.route('/', methods=['GET'])
def index():
    data_slidepics = slidepics.query.order_by(slidepics.id).all()
    slidelist = [pathbyname(data.name,data.ext) for data in data_slidepics]

    data_object = products.query.order_by(products.id).all()
    getproduct = readproduct(data_object)
    productdict = getproduct.productdict
    productlist = getproduct.productlist

    CheckSession(session, productdict)

    data_hecatestatus = hecatestatus.query.first()
    status = data_hecatestatus.status
    channel = data_hecatestatus.channel
    return render_template('index.html',
                           slidelist = slidelist,
                           productdict = productdict,
                           productlist = productlist,
                           status = status,
                           channel = channel,
                           async_mode=socketio.async_mode)

def check_status():
    while True:
        socketio.sleep(10)
        create_app().app_context().push()
        data_hecatestatus = hecatestatus.query.first()
        status = data_hecatestatus.status
        channel = data_hecatestatus.channel
        socketio.emit('my_response',
                      {'status': status, 'channel': channel},
                      namespace='/status')

@socketio.on('connect', namespace='/status')
def check_thread():
    global thread
    with thread_lock: #thread_lock.acquire() = __enter__跟thread_lock.release() = __exit__
        if thread is None:
            thread = socketio.start_background_task(target=check_status)

if __name__ == '__main__':
    socketio.run(app,host='0.0.0.0',port=environ['PORT'])


