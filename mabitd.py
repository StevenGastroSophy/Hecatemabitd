from flask import Flask, render_template, request, url_for, redirect
from hmodel import *

def pathbyname(name, ext):
    return '{folder}/{file}.{filetype}'.format(folder = 'img', file = name, filetype = ext)

@app.route('/', methods=['GET'])
def index():
    data_slidepics = slidepics.query.order_by(slidepics.id).all()

    slidelist = [pathbyname(data.name,data.ext) for data in data_slidepics]
    print(slidelist)

    data_products = products.query.order_by(products.id).all()

    productdict = dict()
    productlist = list()
    for data in data_products:
        productdict[data.name] = [pathbyname(data.picname, data.picext), data.external, pathbyname(data.psqname, data.psqext)]
        productlist.append(data.name)
        print(data.name)

    print(productdict)
    print(productlist)
    return render_template('index.html', slidelist = slidelist, productdict = productdict, productlist = productlist)


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=os.environ['PORT'])


