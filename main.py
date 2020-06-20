from flask import Flask, render_template, url_for, request, redirect,Response,send_file
# from testing.retro_project.gln.test.recur_syn import get_roots
from pymongo import MongoClient
import pymongo
from pprint import pprint
from cachetools import cached, TTLCache
from flask import session
import copy




class Connect(object):
    @staticmethod    
    def get_connection():
        return MongoClient("mongodb://user:user@34.70.51.139:27017/?authSource=temp&readPreference=primary&appname=MongoDB%20Compass&ssl=false")
connection = Connect.get_connection()

client = pymongo.MongoClient("mongodb://user:user@34.70.51.139:27017/?authSource=temp&readPreference=primary&appname=MongoDB%20Compass&ssl=false")
db=client.temp



app = Flask(__name__)
app.secret_key = "super secret key"

from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem.Draw import rdMolDraw2D
from rdkit.Chem import MolFromSmiles
from rdkit.Chem.rdDepictor import Compute2DCoords

jsonFileData={}
import json

@app.route('/')
def root():
    return render_template('index.html')






def getTemplateId(pathkey,pathvalue,template,Id):
    details = db.reactionSmiles.find({"documentId":Id})
    text = ""
    for inventory in details:
        # print(12,inventory['paragraphText'])
        print(67554)
        if 'paragraphText' in inventory:
            text = inventory['paragraphText']
            print(13,text)
            break
    return text
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
    if request.method == "GET":
        # molByUser = request.form["molByUser"]          # for post request
        molByUser = request.args.get("molByUser","")     # for get request
        print("user has entered",molByUser)
        with open('predictions2.json', "r", encoding="utf-8")  as f:
            jsonFileData = json.load(f)
        # jsonFileData = get_roots(molByUser)
        session['jsonFileData'] = jsonFileData


        # print(1,jsonFileData,1)                 # jsonFileData is the dict or json file

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
            # text = getTemplateId(pathkeys[0],pathvalues[0],templateName,Id)
            # headingText.append(text)
            array.append(image)
        # print(array)
        print("length of array for details.html",len(array))
        return render_template('details.html',images=array,headingText=headingText)
    else:
        return render_template('details.html',images=[],headingText=[])


 








@app.route('/next', methods=['GET','POST'])
def next():
    global jsonFileData
    ind=int(request.args.get('ind'))
    noted = jsonFileData["top_k"][ind]
    pathname = noted['path']
    templateName = noted['template']
    Id = noted['temp_id']

    pathvalues = list(pathname.values())[0]
    head = list(pathname.keys())[0]
    print(56,head)

    data1 = []
    data2 = []
    for i,j in pathvalues.items():
        # print(23,i,j)
        data2.append(i)
        template = Chem.MolFromSmarts(templateName)
        path=Chem.MolFromSmiles(i)


        Compute2DCoords(path)
        drawer = rdMolDraw2D.MolDraw2DSVG(250, 250)
        drawer.DrawMolecule(path)
        drawer.FinishDrawing()
        svg = drawer.GetDrawingText()
        data1.append(svg)

    return render_template('next.html' , data1 = data1 , data2 = data2 , parent = head , head = head , headIndex = ind)








def findValues1(pathvalues):
    data1 = []
    data2 = []
    for i,j in pathvalues.items():
        # print(23,i,j)
        data2.append(i)
        # template = Chem.MolFromSmarts(templateName)
        path=Chem.MolFromSmiles(i)


        Compute2DCoords(path)
        drawer = rdMolDraw2D.MolDraw2DSVG(250, 250)
        drawer.DrawMolecule(path)
        drawer.FinishDrawing()
        svg = drawer.GetDrawingText()
        data1.append(svg)
    return data1,data2

@app.route('/prevnext', methods=['GET','POST'])
def prevnext():
    global jsonFileData
    if request.method == "GET":
        currIndex = int(request.args.get("currIndex","")  )
        head = request.args.get("head","")  
        headIndex = int(request.args.get("headIndex","") ) 
        operation = request.args.get("operation","") 
        currentMol = request.args.get("currentMol","") 

        print(000,operation,head,headIndex,currIndex,currentMol,000)

        if operation == "Next":
            arr = []
            arr.append(jsonFileData["top_k"][headIndex]["path"])

            flag = 0
            found = 0
            while 1:
                arrCopy = copy.deepcopy(arr)
                length = len(arrCopy)
                print("length of array of objects = ",length)
                if length == 0:
                    flag=1
                    break
                for loop in arrCopy:
                    # print()
                    # print(arrCopy)
                    # print(loop)
                    # print(loop.values())
                    # print(34,list(loop.values())[0])
                    # print()

                    if currentMol in list(loop.keys()):
                        found = 1
                        break
                    else:
                        for item in list(loop.values()):
                            # Check if dictionary is empty  
                            res = bool(item) 
                            if res:
                                arr.append(item)
                        arr.remove(loop)

                if found == 1:
                    break

            print("we were searching next for = ",loop[currentMol])
            data1 , data2 = findValues1(loop[currentMol])
                

        return render_template('next.html' , data1 = data1 , data2 = data2 , head = head , headIndex = headIndex)



















@app.route('/getDetails', methods=['GET','POST'])
def getDetails():
    if request.method == "GET":
        return render_template('index.html')
    elif request.method == "POST":
        global jsonFileData
        index = request.json.get("index")
        # print(index)



        headingText=[]
        paragraphText = []

        item = jsonFileData["top_k"][index]
        pathname = item['path']
        templateName = item['template']
        Id = item['temp_id']
        pathkey = list(pathname.keys())[0]
        pathvalue = list(pathname.values())[0]

        details = db.reactionSmiles.find({"documentId":Id})
        text = ""
        for inventory in details:
            print(67554)
            if 'paragraphText' in inventory:
                text = inventory['paragraphText']
                break
        # text = "A 2.00 g portion of 2-methoxy-4-methylbenzoic acid was dissolved in 10 ml of sulfuricacid. With stirring at 0\u00b0 C., 0.88 ml of concentrated nitric acid was added thereto dropwise. After 4 hours of stirring at room temperature, and ice water was added. The thus formed crystals were collected by filtration, dried under a reduced pressure and then purified by column chromatography (chloroform:methanol=30:1) to give 1.32 g of 2-methoxy-4-methyl-5-nitrobenzoic acid as yellow crystals.A 2.00 g portion of 2-methoxy-4-methylbenzoic acid was dissolved in 10 ml of sulfuric acid. With stirring at 0\u00b0 C., 0.88 ml of concentrated nitric acid was added thereto dropwise. After 4 hours of stirring at room temperature, and ice water was added. The thus formed crystals were collected by filtration, dried under a reduced pressure and then purified by column chromatography (chloroform:methanol=30:1) to give 1.32 g of 2-methoxy-4-methyl-5-nitrobenzoic acid as yellow crystals."
        return json.dumps({"text":text,"example":123})


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



@app.route('/d')
def d():

    # func1()
    return render_template('d.html')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)