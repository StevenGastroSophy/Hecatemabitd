from flask import Flask, render_template, request, url_for, redirect, jsonify
from hmodel import *

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
            price = mabipricestyle(data.price)
            self.productdict[data.name] = [pathbyname(data.picname, data.picext),
                                           pathbyname(data.psqname, data.psqext),
                                           data.id,
                                           price,
                                           data.description,
                                           data.external]
            self.productlist.append(data.name)

@app.route('/_another_product')
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
    return render_template('products.html', productdict = getproduct.productdict, productlist = getproduct.productlist, default = getproduct.defaultproduct)


@app.route('/', methods=['GET'])
def index():
    data_slidepics = slidepics.query.order_by(slidepics.id).all()
    slidelist = [pathbyname(data.name,data.ext) for data in data_slidepics]
    print(slidelist)

    getproduct = readproduct(products.id)
    getproduct.addstuff()
    return render_template('index.html', slidelist = slidelist, productdict = getproduct.productdict, productlist = getproduct.productlist)


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=os.environ['PORT'])


