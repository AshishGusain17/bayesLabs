from flask import Flask, render_template, url_for, request, redirect,Response,send_file
# from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import cv2
from cam_shift import *
from mean_shift import *
from mouse_click_event import *
import time



from pymongo import MongoClient
import pymongo
from pprint import pprint




class Connect(object):
    @staticmethod    
    def get_connection():
        return MongoClient("mongodb://user:user@34.69.67.3:27017/?authSource=temp&readPreference=primary&appname=MongoDB%20Compass&ssl=false")
connection = Connect.get_connection()


client = pymongo.MongoClient("mongodb://user:user@34.69.67.3:27017/?authSource=temp&readPreference=primary&appname=MongoDB%20Compass&ssl=false")
db=client.temp






import csv 
import requests 
import xml.etree.ElementTree as ET 
import copy



st = time.time()


array = []
def funcParse(xmlFile):
    global ct ,array
    # create element tree object 
    print(xmlFile)
    tree = ET.parse(xmlFile) 

    # get root element 
    root = tree.getroot() 

    length = len(root.findall("./"))
    # print(length)

    for ind in range(length): 

        obj = {}
        for child in root[ind][0]: 
            # print(1,child)
            # print(2,child.tag)
            indice = child.tag.find("}")
            # print(child.tag[ind+1:])
            # print(4,child.text)
            left = child.tag[indice + 1 : ]
            right = child.text
            obj[left] = right


        obj["collectionName"] = root[ind][1].text
        ct = ct+1
        array.append(obj)
        print(ct)
        if ct % 50000==0:
            db.collectionName.insert_many(array)
            array = copy.deepcopy([])
    # db.collectionName.insert_many(array)






ct = 0
import os

curr = "no6"
pYear = os.listdir(os.path.join("allfiles" , curr))
print(pYear)

for folderYear in pYear:
    pYear = os.listdir(os.path.join("allfiles" , curr , folderYear ))

    for xmlFile in pYear:
        pathname = os.path.join( "allfiles" , curr , folderYear , xmlFile)
        funcParse(pathname)
    #     break
    # break

db.collectionName.insert_many(array)
# print(array)
print(len(array))
print("total doc=",len(array))
fi = time.time()
print((fi-st))

# 184.7
# 587.6
# 2058937 - 1808937 =250000
# 649918
# 666523
# 622812


















