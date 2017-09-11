from threading import Lock
from flask import Flask, render_template, request, url_for, redirect, jsonify, session
from flask_session import Session
from flask_socketio import SocketIO, emit, disconnect
import os
import sys
import time
from math import modf
from random import randint
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField , TextAreaField
from wtforms.validators import DataRequired, NumberRange, InputRequired
from hmodel import db, slidepics, products, productpictures, hecatestatus


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

def pathbyname(name, ext):
    return '{folder}/{file}.{filetype}'.format(folder = 'img', file = name, filetype = ext)

def createcode(time):
    timestamp = int(time)
    RandomThree = randint(100,999)
    millisecond = int(round(modf(time)[0],2)*100)
    return str(timestamp)+str(RandomThree)+str(millisecond)

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
        
class PayForm(FlaskForm):
    User_id = StringField(validators=[InputRequired(), DataRequired()])
    Hope_time = StringField()
    Hope_channel = IntegerField(validators=[NumberRange(message='請填入1到12分流', min=1, max=12)])
    PS = TextAreaField()

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
        except PermissionError:
            print('Redirect')
            return redirect(url_for('productpage'))
    if request.method == 'POST':
        try:
            if int(session['CartCount']) > 0 and form.validate_on_submit():
                print("Validate!")
                User_id = form.User_id.data
                Hope_time = form.Hope_time.data
                Hope_channel = form.Hope_channel.data
                PS = form.PS.data

                time = time.time()
                code = createcode(time)

                return str(User_id)+str(Hope_time)+str(Hope_channel)+str(PS)+" code is "+code 
            else:
                print('Redirect')
                return redirect(url_for('productpage'))
        except PermissionError:
            print('Redirect')
            return redirect(url_for('productpage'))       


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
    socketio.run(app,host='0.0.0.0',port=os.environ['PORT'])


