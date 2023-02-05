from flask import Flask
from flask_cors import CORS, cross_origin
from flask import request
from pymongo import MongoClient
import numpy as np
import cv2
import base64
from bson import ObjectId
from handle.detect import detect
app = Flask(__name__)

# APPLY FLASK CORS
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config["URL_DB"] = "mongodb+srv://albert:162003@cluster0.ned4xp7.mongodb.net/?retryWrites=true&w=majority"

# SETUP DB
db_client = MongoClient(app.config["URL_DB"])
db = db_client['khkt_db']
tables = db['khkt_tables']


def convectBase64toImg(img):
    try:
        img = np.fromstring(
            base64.b64decode(img), dtype=np.uint8)
        img = cv2.imdecode(img, cv2.IMREAD_ANYCOLOR)
    except:
        return None
    return img


@app.route('/face_detect', methods=['POST'])
@cross_origin(origin='*')
def nhandienkhuonmat_process():
    img_base64 = request.json['data_base64']
    img_base64 = img_base64.replace("data:image/webp;base64,", "")
    img_detect = convectBase64toImg(img_base64)
    kq = detect(img_detect)
    return {
        "text_detect": kq
    }


@app.route('/ids', methods=['GET'])
@cross_origin(origin='*')
def ids():
    lessons = []
    for id in tables.find():
        id = str(ObjectId(id['_id']))
        lesson = tables.find_one({"_id": ObjectId(id)})['title']
        lessons.append({
            "id": id,
            "lesson": lesson
        })
    data = tables.find_one({"_id": ObjectId(lessons[0]["id"])})
    Title = data['title']
    Lamquen = data['val_Lamquen']
    Danhvan = data['val_Danhvan']
    Tapdoc = data['val_Tapdoc']
    Timvan = data['val_Timvan']
    return {
        "lessons": lessons,
        "data": {
            "title": Title,
            "lamquen": Lamquen,
            "danhvan": Danhvan,
            "tapdoc": Tapdoc,
            "timvan": Timvan
        }

    }


@app.route('/data_lesson', methods=['POST'])
@cross_origin(origin='*')
def data_lesson():
    id = request.json['id']
    data = tables.find_one({"_id": ObjectId(id)})
    Title = data['title']
    Lamquen = data['val_Lamquen']
    Danhvan = data['val_Danhvan']
    Tapdoc = data['val_Tapdoc']
    Timvan = data['val_Timvan']
    return {
        "title": Title,
        "lamquen": Lamquen,
        "danhvan": Danhvan,
        "tapdoc": Tapdoc,
        "timvan": Timvan
    }


# Start Backend
if __name__ == '__main__':
    app.run(host='0.0.0.0', port='6868')
