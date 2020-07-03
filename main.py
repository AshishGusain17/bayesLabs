
from fastapi import FastAPI,Form,Depends
from pydantic import BaseModel
from typing import Optional
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.responses import Response
from fastapi.templating import Jinja2Templates

from pymongo import MongoClient
import pymongo
from pprint import pprint
from cachetools import cached, TTLCache
import copy

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")






class Connect(object):
    @staticmethod    
    def get_connection():
        return MongoClient("mongodb://user:user@34.70.51.139:27017/?authSource=temp&readPreference=primary&appname=MongoDB%20Compass&ssl=false")
connection = Connect.get_connection()

client = pymongo.MongoClient("mongodb://user:user@34.70.51.139:27017/?authSource=temp&readPreference=primary&appname=MongoDB%20Compass&ssl=false")
db=client.temp


from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem.Draw import rdMolDraw2D
from rdkit.Chem import MolFromSmiles
from rdkit.Chem.rdDepictor import Compute2DCoords

jsonFileData={}
jsonFileData2={}
import json

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html",{"request": request})



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


class Form1(BaseModel):
    molByUser: str = Form(...)

@app.get('/details')
def getDetails(request: Request,Form1: Form1 = Depends()):
    global jsonFileData
    molByUser = Form1.molByUser

    print("user has entered",molByUser)
    with open('predictions2.json', "r", encoding="utf-8")  as f:
        jsonFileData = json.load(f)
    # jsonFileData = get_roots(molByUser)


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
    return templates.TemplateResponse('details.html',{"request": request,"images":array,"headingText":headingText})


@app.post('/details')
def postDetails(request: Request):
    global jsonFileData
    return templates.TemplateResponse('details.html',{"request": request,"images":[],"headingText":[]})








class Form2(BaseModel):
    ind: str = Form(...)

@app.get('/next')
def next(request: Request,Form2: Form2 = Depends()):
    global jsonFileData
    ind=int(Form2.ind)
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

    return templates.TemplateResponse('next.html' , {"request": request , "data1": data1 , "data2": data2 , "parent": head , "head": head , "headIndex": ind})











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

class Form3(BaseModel):
    currIndex: str = Form(...)
    head: str = Form(...)
    headIndex: str = Form(...)
    operation: str = Form(...)
    currentMol: str = Form(...)

@app.get('/prevnext')
def prevnext(request: Request,Form3: Form3 = Depends()):
    global jsonFileData
    currIndex = int(Form3.currIndex)
    head = Form3.head
    headIndex = int(Form3.headIndex)
    operation = Form3.operation
    currentMol = Form3.currentMol

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
            

    return templates.TemplateResponse('next.html' , {"request": request , "data1": data1 , "data2": data2 , "head": head , "headIndex": headIndex})























@app.get('/getDetails')
def getGetDetails(request: Request):
    return templates.TemplateResponse('index.html' , {"request": request})

class Form4(BaseModel):
    index: str = Form(...)

@app.post('/getDetails')
def postGetDetails(request: Request,Form4: Form4 ):
# def postGetDetails(request: Request,response_class=Response):

    global jsonFileData
    index = int(Form4.index)

    headingText=[]
    paragraphText = []

    item = jsonFileData["top_k"][index]
    pathname = item['path']
    templateName = item['template']
    Id = item['temp_id']
    pathkey = list(pathname.keys())[0]
    pathvalue = list(pathname.values())[0]

    # details = db.reactionSmiles.find({"documentId":Id})
    # text = ""
    # for inventory in details:
    #     print(67554)
    #     if 'paragraphText' in inventory:
    #         text = inventory['paragraphText']
    #         break
    text = "A 2.00 g portion of 2-methoxy-4-methylbenzoic acid was dissolved in 10 ml of sulfuricacid. With stirring at 0\u00b0 C., 0.88 ml of concentrated nitric acid was added thereto dropwise. After 4 hours of stirring at room temperature, and ice water was added. The thus formed crystals were collected by filtration, dried under a reduced pressure and then purified by column chromatography (chloroform:methanol=30:1) to give 1.32 g of 2-methoxy-4-methyl-5-nitrobenzoic acid as yellow crystals.A 2.00 g portion of 2-methoxy-4-methylbenzoic acid was dissolved in 10 ml of sulfuric acid. With stirring at 0\u00b0 C., 0.88 ml of concentrated nitric acid was added thereto dropwise. After 4 hours of stirring at room temperature, and ice water was added. The thus formed crystals were collected by filtration, dried under a reduced pressure and then purified by column chromatography (chloroform:methanol=30:1) to give 1.32 g of 2-methoxy-4-methyl-5-nitrobenzoic acid as yellow crystals."
    return json.dumps({"text":text,"example":123})









class Form5(BaseModel):
    index: str = Form(...)
    
@app.get('/getTree')
def getTree(request: Request,Form5: Form5 = Depends()):
    index = int(Form5.index)
    return templates.TemplateResponse('tree.html' , {"request": request , "index": index})



class Form6(BaseModel):
    index: str = Form(...)

@app.post('/getReaction')
def getReaction(request: Request,Form6: Form6):
    index = int(Form6.index)
    print("getReaction mol index = ",index)
    details = db.reactionSmiles.find({"documentId":Id})

    reaction = ""
    for inventory in details:
        if 'reactionSmiles' in inventory:
            reaction = inventory['reactionSmiles']
            break
    return json.dumps({"reaction":reaction})


class Form7(BaseModel):
    index: str = Form(...)

@app.post('/getPopup')
def getPopup(request: Request,Form7: Form7):
    global jsonFileData2

    with open('predictions.json', "r", encoding="utf-8")  as f:
        jsonFileData2 = json.load(f)
    # jsonFileData2 = get_roots(molName)
    # session['jsonFileData2'] = jsonFileData2


    array=[]
    headingText=[]
    paragraphText = []
    for item in jsonFileData2["top_k"]:
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
    return json.dumps({"images":array,"headingText":headingText})

















# class User(BaseModel):
#     email: str
#     password: str

# class Item(BaseModel):
#     name: str
#     price: float
#     is_offer: Optional[bool] = None









# from flask import *  
# app = Flask(__name__) 
# import os 
# app.secret_key = os.urandom(24)


# @app.route('/')  
# def home():  
#     res = make_response("<h4>session variable is set, <a href='/get'>Get Variable</a></h4>")  
#     session['response']='session#1'  
#     return res;  


# @app.route('/get')  
# def getVariable():  
#     print(session)
#     if 'response' in session:  
#         s = session['response']
#         return render_template('session.html',name = s)  


# if __name__ == '__main__':  
#     app.run(debug = True)  











































# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Optional[str] = None):
#     return {"item_id": item_id, "q": q}

# @app.put("/items/{item_id}")
# def update_item(item_id: int, item: Item):
#     return {"item_name": item.name, "item_id": item_id}



# @app.post("/login")
# def login(user: User):
#     # ...
#     # do some magic
#     # ...
#     return {"msg": "login successful"}


