from flask import Flask, render_template, url_for, request, redirect,Response,send_file
# from testing.retro_project.gln.test.recur_syn import get_roots
from pymongo import MongoClient
import pymongo
from pprint import pprint


class Connect(object):
    @staticmethod    
    def get_connection():
        return MongoClient("mongodb://user:user@34.69.67.3:27017/?authSource=temp&readPreference=primary&appname=MongoDB%20Compass&ssl=false")
connection = Connect.get_connection()


client = pymongo.MongoClient("mongodb://user:user@34.69.67.3:27017/?authSource=temp&readPreference=primary&appname=MongoDB%20Compass&ssl=false")
db = client.get_database('beta')
app = Flask(__name__)


from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem.Draw import rdMolDraw2D
from rdkit.Chem import MolFromSmiles
from rdkit.Chem.rdDepictor import Compute2DCoords


import json
with open('predictions.json', "r", encoding="utf-8")  as f:
    data = json.load(f)
# data = get_roots("predictions.json")

@app.route('/')
def index():
    return render_template('index.html')


def func(pathname,pathkey,pathvalue,templateName,Id):
    template = Chem.MolFromSmarts(templateName)
    pathname=Chem.MolFromSmiles(pathkey)
    pathname.GetSubstructMatches(template)
   
    print(pathvalue)
    ct = 2
    data = []
    for k,v in pathvalue.items():
        print(k,v)
        # data.append()

    Compute2DCoords(pathname)
    drawer = rdMolDraw2D.MolDraw2DSVG(250, 250)
    drawer.DrawMolecule(pathname)
    drawer.FinishDrawing()
    # print(drawer.GetDrawingText())
    return drawer.GetDrawingText()

@app.route('/details')

def details():

    array=[]
    for item in data["top_k"]:
        pathname = item['path']
        templateName = item['template']
        Id = item['temp_id']
        # print(pathname)
        # print(templateName)
        # print(Id)
        pathkeys = list(pathname.keys())
        pathvalues = list(pathname.values())
        # print(pathkeys)
        # print(pathvalues)
        image = func(pathname,pathkeys[0],pathvalues[0],templateName,Id)
        array.append(image)
    # print(array)
    print("length of array for details.html",len(array))
    return render_template('details.html',images=array)


 








@app.route('/next', methods=['GET'])
def next():
    ind=int(request.args.get('ind'))
    nextArray = []
    noted = data["top_k"][ind]
    pathname = noted['path']
    templateName = noted['template']
    Id = noted['temp_id']
    # print(pathname)
    # print(templateName)
    # print(Id)
    pathvalues = list(pathname.values())[0]
    print(pathvalues)


    for i,j in pathvalues.items():
        # template = Chem.MolFromSmarts(templateName)
        pathname=Chem.MolFromSmiles(i)
        # pathname.GetSubstructMatches(template)


        Compute2DCoords(pathname)
        drawer = rdMolDraw2D.MolDraw2DSVG(250, 250)
        drawer.DrawMolecule(pathname)
        drawer.FinishDrawing()
        # print(drawer.GetDrawingText())
        svg = drawer.GetDrawingText()
        nextArray.append(svg)
    print(nextArray)




    return render_template('next.html' , data = nextArray)






@app.route('/d')
def d():
    # func1()
    return render_template('d.html')


if __name__ == "__main__":
    app.run(debug=True)
