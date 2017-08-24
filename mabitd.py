from flask import Flask, render_template, request, url_for, redirect, jsonify
from hmodel import *

def pathbyname(name, ext):
    return '{folder}/{file}.{filetype}'.format(folder = 'img', file = name, filetype = ext)

@app.route('/_another_product')
def another_product():
    data_products = products.query.order_by(products.id).all()

    productdict = dict()
    productlist = list()
    for data in data_products:
        pricelist = []
        w = int(int(data.price )/10000)
        k = int(int(data.price )%10000)
        if w  is not 0:
            pricelist.append(str(w))
        if k  is not 0:
            pricelist.append(str(k))
        else:
            pricelist.append('')
        data.price  = '萬'.join(pricelist)
        productdict[data.name] = [pathbyname(data.picname, data.picext), pathbyname(data.psqname, data.psqext), data.id, data.price, data.description, data.external]
        productlist.append(data.name)
        print(data.name)

    print(productdict)
    print(productlist)
    productname = request.args.get('productname')
    print(productname)
    resultdict = dict()
    resultdict['resultpic'] = productdict[productname][0]
    resultdict['resultname'] = productname
    resultdict['resultprice'] = productdict[productname][3]
    resultdict['resultdescription'] = productdict[productname][4]
    return jsonify(resultdict)

@app.route('/products', methods=['GET'])
def productpage():
    defaultproductid = int(request.args.get('default'))
    print("defaultproductid is"+str(defaultproductid))
    print(type(defaultproductid))

    data_products = products.query.order_by(products.id).all()

    productdict = dict()
    productlist = list()
    for data in data_products:
        print(data.id)
        print(type(data.id))
        if data.id == defaultproductid:
            defaultproduct = data.name
            print("defaultproduct is"+str(defaultproduct))   
        pricelist = []
        w = int(int(data.price )/10000)
        k = int(int(data.price )%10000)
        if w  is not 0:
            pricelist.append(str(w))
        if k  is not 0:
            pricelist.append(str(k))
        else:
            pricelist.append('')
        data.price  = '萬'.join(pricelist)
        productdict[data.name] = [pathbyname(data.picname, data.picext), pathbyname(data.psqname, data.psqext), data.id, data.price, data.description, data.external]
        productlist.append(data.name)
        print(data.name)

    print(productdict)
    print(productlist)
    return render_template('products.html', productdict = productdict, productlist = productlist, default = defaultproduct)


@app.route('/', methods=['GET'])
def index():
    data_slidepics = slidepics.query.order_by(slidepics.id).all()

    slidelist = [pathbyname(data.name,data.ext) for data in data_slidepics]
    print(slidelist)

    data_products = products.query.order_by(products.id).all()

    productdict = dict()
    productlist = list()
    for data in data_products:
        pricelist = []
        w = int(int(data.price )/10000)
        k = int(int(data.price )%10000)
        if w  is not 0:
            pricelist.append(str(w))
        if k  is not 0:
            pricelist.append(str(k))
        else:
            pricelist.append('')
        data.price  = '萬'.join(pricelist)
        productdict[data.name] = [pathbyname(data.picname, data.picext), pathbyname(data.psqname, data.psqext), data.id, data.price, data.description, data.external]
        productlist.append(data.name)
        print(data.name)

    print(productdict)
    print(productlist)
    return render_template('index.html', slidelist = slidelist, productdict = productdict, productlist = productlist)


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=os.environ['PORT'])


