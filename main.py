from flask import Flask, render_template, url_for, request, redirect,Response,send_file
# from testing.retro_project.gln.test.recur_syn import get_roots
from pymongo import MongoClient
import pymongo
from pprint import pprint
from cachetools import cached, TTLCache
from flask import session





# class Connect(object):
#     @staticmethod    
#     def get_connection():
#         return MongoClient("mongodb://user:user@34.69.67.3:27017/?authSource=temp&readPreference=primary&appname=MongoDB%20Compass&ssl=false")
# connection = Connect.get_connection()

# client = pymongo.MongoClient("mongodb://user:user@34.69.67.3:27017/?authSource=temp&readPreference=primary&appname=MongoDB%20Compass&ssl=false")
# db=client.temp



app = Flask(__name__)
# app.secret_key = "super secret key"

from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem.Draw import rdMolDraw2D
from rdkit.Chem import MolFromSmiles
from rdkit.Chem.rdDepictor import Compute2DCoords

jsonFileData={}
import json

@app.route('/')
def index():
    return render_template('index.html')






def getTemplateId(pathkey,pathvalue,template,Id):
    details = db.reactionSmiles.find({"headingText":"3-Bromopropyl methanesulfonate"})
    print(details)
    for inventory in details:
        print(inventory['_id'])
        # print(inventory)
    return details
def func(pathname,pathkey,pathvalue,template):
    template = Chem.MolFromSmarts(template)
    pathname = Chem.MolFromSmiles(pathkey)
   
    # pathname.GetSubstructMatches(template)
    # a=pathname.GetSubstructMatches(template)
    # z = Chem.Draw.MolToImage(pathname, size=(300, 300), kekulize=True, wedgeBonds=True, useSVG=True,highlightAtoms=list(a[0]))
    # z.save("pathname.png","PNG")
    # Compute2DCoords(z)
    drawer = rdMolDraw2D.MolDraw2DSVG(250, 250)


    hit_bonds = []
    hit_ats = list(pathname.GetSubstructMatch(template))
    for bond in template.GetBonds():
        aid1 = hit_ats[bond.GetBeginAtomIdx()]
        aid2 = hit_ats[bond.GetEndAtomIdx()]
        hit_bonds.append(pathname.GetBondBetweenAtoms(aid1,aid2).GetIdx())
    rdMolDraw2D.PrepareAndDrawMolecule(drawer , pathname, highlightAtoms=hit_ats,highlightBonds=hit_bonds)


    drawer.DrawMolecule(pathname)
    drawer.FinishDrawing()
    # print(drawer.GetDrawingText())
    return drawer.GetDrawingText()

@app.route('/details',methods=["GET","POST"])
def details():
    global jsonFileData
    if request.method == "POST":
        molByUser = request.form["molByUser"]
        print("user has entered",molByUser)
        with open('predictions.json', "r", encoding="utf-8")  as f:
            jsonFileData = json.load(f)
        # jsonFileData = get_roots(molByUser)


        print(1,jsonFileData,1)                 # jsonFileData is the dict or json file

        array=[]
        headingText=[]
        paragraphText = []
        for item in jsonFileData["top_k"]:
            pathname = item['path']
            templateName = item['template']
            Id = item['temp_id']
            pathkeys = list(pathname.keys())
            pathvalues = list(pathname.values())
            # print(pathkeys)
            # print(pathvalues)
            image = func(pathname,pathkeys[0],pathvalues[0],templateName)
            # details = getTemplateId(pathkeys[0],pathvalues[0],templateName,Id)
            array.append(image)
        # print(array)
        print("length of array for details.html",len(array))
        return render_template('details.html',images=array)
    else:
        return render_template('details.html',images=[])


 








@app.route('/next', methods=['GET','POST'])
def next():
    global jsonFileData
    ind=int(request.args.get('ind'))
    nextArray = []
    noted = jsonFileData["top_k"][ind]
    pathname = noted['path']
    templateName = noted['template']
    Id = noted['temp_id']

    pathvalues = list(pathname.values())[0]
    # print(pathvalues)

    for i,j in pathvalues.items():
        template = Chem.MolFromSmarts(templateName)
        pathname=Chem.MolFromSmiles(i)


        Compute2DCoords(pathname)
        drawer = rdMolDraw2D.MolDraw2DSVG(250, 250)
        drawer.DrawMolecule(pathname)
        drawer.FinishDrawing()
        svg = drawer.GetDrawingText()
        nextArray.append(svg)
    # print(nextArray)
    return render_template('next.html' , data = nextArray)






# def smiles_to_svg(smiles):
#     molecule = MolFromSmiles(smiles)
#     Compute2DCoords(molecule)
#     drawer = rdMolDraw2D.MolDraw2DSVG(250, 250)
#     drawer.DrawMolecule(molecule)
#     drawer.FinishDrawing()
#     return drawer.GetDrawingText()
# @app.route('/c', methods=['POST'])
# def c():
#     rough = session.get('d') 
#     print(session)
#     smiles = request.json.get("smiles")
#     svg = smiles_to_svg(smiles)
#     return svg
# @app.route('/rough')
# def rough():

#     return render_template('c.html')



# @app.route('/d')
# def d():
#     session['d']=11111111
#     print("d" , session, "d")

#     ass = session.get('ass')
#     print(2,rough,2)
#     # func1()
#     return render_template('d.html')


if __name__ == "__main__":
    app.run(app.run(host='127.0.0.1', port=8080))
