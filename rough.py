import keras
import cv2
import numpy as np
import imutils
from PIL import Image,ImageTk













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



@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("ml.html",{"request": request,"idd":1,"name":""})




from keras.preprocessing.image import img_to_array
from keras.applications import imagenet_utils
from fastapi import  File, UploadFile
import io

def prepare_image(image, target):
    # if the image mode is not RGB, convert it
    if image.mode != "RGB":
        image = image.convert("RGB")
    # resize the input image and preprocess it
    image.save("img.jpg")

    image = image.resize(target)
    image = img_to_array(image)
    image = np.expand_dims(image, axis=0)
    image = imagenet_utils.preprocess_input(image)

    # return the processed image
    return image

from keras import backend as K

def get_model():

    model =  keras.models.Sequential()

    model.add(keras.layers.InputLayer(input_shape=(224, 224, 3)))

    model.add(keras.layers.Conv2D(32, (3, 3), padding="same", activation="relu"))
    model.add(keras.layers.MaxPooling2D(pool_size=(2, 2)))

    model.add(keras.layers.Conv2D(64, (3, 3), padding="same", activation="relu"))
    model.add(keras.layers.MaxPooling2D(pool_size=(2, 2)))

    model.add(keras.layers.Conv2D(128, (3, 3), padding="same", activation="relu"))
    model.add(keras.layers.MaxPooling2D(pool_size=(2, 2)))

    model.add(keras.layers.Flatten())
    model.add(keras.layers.Dense(128,activation='relu' ))
    model.add(keras.layers.Dense(8, activation='softmax'))

    model.load_weights('my_model_weights.h5')
    return model


from keras.models import load_model
import time
@app.post("/classify")
def predict(request: Request, file: bytes = File(...)):
    print(222222,file,len(file))
    if len(file)==0:
        return templates.TemplateResponse("ml.html",{"request": request,"idd":1,"name":""})
    else:

        dictreverse =  {0 : 'bharatanatyam',
                        1 : 'kathak' ,
                        2 : 'kathakali',
                        3 : 'kuchipudi',
                        4 : 'manipuri',
                        5 : 'mohiniyattam',
                        6 : 'odissi',
                        7 : 'sattriya'}



        model = get_model()




        image = Image.open(io.BytesIO(file))
        # prepare_image(image, (224,224))
        # image.save("img.jpg")
        img = prepare_image(image, target=(224, 224))



        img = cv2.imread("img.jpg") 
        img = cv2.resize(img,(224,224))
        img = np.expand_dims(img, axis=0)

        print(8888888888888888)
        print(img.shape)

        ans = model.predict(img/255)
        ind = np.argmax(ans)
        name = dictreverse[ind]
        print(name)

        K.clear_session()
        return templates.TemplateResponse('ml.html',{"request": request,"name":name,"idd":2})







# img = cv2.imread("img1.jpg") 
# cv2.imshow("45",img)
# cv2.waitKey(0)

# print(7666666666666)
# img = cv2.resize(img,(224,224))
# print(66666666666666666)
# img = np.expand_dims(img, axis=0)
# print(8888888888888888)

# print(img.shape)
# ans = model.predict(img/255)

# ind = np.argmax(ans)
# print(dictreverse[ind])