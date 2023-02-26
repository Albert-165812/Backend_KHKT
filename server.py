import json
from flask import Flask, send_file
from flask_cors import CORS, cross_origin
from flask import request
from flask_socketio import SocketIO, emit
from pymongo import MongoClient
import numpy as np
import cv2
import base64
from bson import ObjectId
from handle.detect import YoloDetectImg
from urllib.parse import unquote
import os

app = Flask(__name__)


# APPLY FLASK CORS
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['allowedHeaders'] = ['sessionId', 'Content-Type'],
app.config['exposedHeaders'] = ['sessionId'],
app.config['Access-Control-Allow-Origin'] = '*'
app.config['SECRET_KEY'] = 'top-secret!'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['UPLOADED_PHOTOS_DEST'] = 'src/image/'
app.config["URL_DB"] = "mongodb+srv://albert:162003@cluster0.ned4xp7.mongodb.net/?retryWrites=true&w=majority"
socketio = SocketIO(app, cors_allowed_origins="*")

# SETUP DB
db_client = MongoClient(app.config["URL_DB"])
db = db_client['khkt_db']
tables = db['khkt_tables']

print("wait data")
lesson = []
Lamquen = []
Kechuyen = []
Danhvan = []
Ontap = []
img_Lamquen = []
img_Kechuyen = []
img_Danhvan = []
img_Ontap = []
ids = []
list_id = []
chuong = []
dt_id = []

for id in tables.find():
    id = str(ObjectId(id['_id']))
    dt_id.append({
        "id": id
    })
    if (len(ids) == 0):
        ids.append(tables.find_one({"_id": ObjectId(id)})['chuong'])
        chuong.append({
            "chuong": "Chương "+str(ids.index(tables.find_one({"_id": ObjectId(id)})['chuong'])+1),
            "study": [],
        })
        list_id.append({
            "chuong": "Chương "+str(ids.index(tables.find_one({"_id": ObjectId(id)})['chuong'])+1),
            "ids": []
        })
    if (tables.find_one({"_id": ObjectId(id)})['chuong'] not in str(ids)):
        ids.append(tables.find_one({"_id": ObjectId(id)})['chuong'])
        chuong.append({
            "chuong": "Chương "+str(ids.index(tables.find_one({"_id": ObjectId(id)})['chuong'])+1),
            "study": [],
        })
        list_id.append({
            "chuong": "Chương "+str(ids.index(tables.find_one({"_id": ObjectId(id)})['chuong'])+1),
            "ids": []
        })
for id in tables.find():
    id = str(ObjectId(id['_id']))
    for i in range(0, len(tables.find_one({"_id": ObjectId(id)})['data_lesson'])):
        if ("Lamquen" in str(tables.find_one({"_id": ObjectId(id)})['data_lesson'][i])):
            Lamquen = tables.find_one({"_id": ObjectId(id)})['data_lesson'][i]
            if (Lamquen["Lamquen"] != ""):
                for lL in tables.find_one({"_id": ObjectId(id)})['data_lesson'][i]["Lamquen"]:
                    lL["img"] = unquote(lL["img"])[85:]
        if ("Kechuyen" in str(tables.find_one({"_id": ObjectId(id)})['data_lesson'][i])):
            Kechuyen = tables.find_one({"_id": ObjectId(id)})['data_lesson'][i]
            if (Kechuyen["Kechuyen"] != ""):
                for lK in tables.find_one({"_id": ObjectId(id)})['data_lesson'][i]["Kechuyen"]:
                    for lC in lK["content"]:
                        lC["img"] = unquote(lC["img"])[85:]
        if ("Danhvan" in str(tables.find_one({"_id": ObjectId(id)})['data_lesson'][i])):
            Danhvan = tables.find_one({"_id": ObjectId(id)})['data_lesson'][i]
            if (Danhvan["Danhvan"] != ""):
                for lD in tables.find_one({"_id": ObjectId(id)})[
                        'data_lesson'][i]["Danhvan"]:
                    lD["img"] = unquote(lD["img"])[85:]
                    img_Danhvan.append(unquote(lD["img"]))
        if ("Ontap" in str(tables.find_one({"_id": ObjectId(id)})['data_lesson'][i])):
            Ontap = tables.find_one({"_id": ObjectId(id)})['data_lesson'][i]
            if (Ontap["Ontap"] != ""):
                for lO in tables.find_one({"_id": ObjectId(id)})[
                        'data_lesson'][i]["Ontap"]:
                    lO["img"] = unquote(lO["img"])[85:]
    chuong[ids.index(tables.find_one({"_id": ObjectId(id)})['chuong'])]["study"].append({
        "baihoc": tables.find_one({"_id": ObjectId(id)})['baihoc'],
        "study": {
            "Lamquen": Lamquen,
            "Danhvan": Danhvan,
            "Kechuyen": Kechuyen,
            "Ontap": Ontap
        }
    })
    list_id[ids.index(tables.find_one({"_id": ObjectId(id)})['chuong'])]["ids"].append({
        "id": id,
        "baihoc": tables.find_one({"_id": ObjectId(id)})['baihoc'],
    })
    Lamquen = ''
    Danhvan = ''
    Kechuyen = ''
    Ontap = ''
    img_Lamquen = []
    img_Kechuyen = []
    img_Danhvan = []
    img_Ontap = []

print("done data")


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
    kq = YoloDetectImg().detect(img_detect, 1)
    if (kq == None):
        return {
            "text_detect": "no detection"
        }
    emit_client_local("TextoAlertWeb", "Page_detect", kq)
    return {
        "text_detect": kq
    }


@app.route('/data', methods=['GET'])
@cross_origin(origin='*')
def data():
    global dt_id, list_id, chuong
    return {
        "list_id": dt_id,
        "ids": list_id,
        "listchuong": chuong,
    }


@app.route('/page_current', methods=['POST'])
@cross_origin(origin='*')
def page_current():
    id = request.json["page"]
    data = {
        "task": "alertPageCurr",
        "place": "none",
        "content": id,
    }
    emit_page_curr(data["task"], data["place"], data["content"])
    return "done"


@app.route('/state_choosen', methods=['POST'])
@cross_origin(origin='*')
def choosen_current():
    id = request.json["state"]
    data = {
        "task": "alertStateChoosen",
        "place": "none",
        "content": id,
    }
    emit_page_curr(data["task"], data["place"], data["content"])
    return "done"


@app.route('/src/image/<chuong>/<bai>/<path:filename>')
@cross_origin(origin='*')
def get_image(chuong, bai, filename):
    return send_file(os.getcwd()+'/src/image/'+chuong+'/'+bai+'/'+filename, mimetype='image/jpeg')


@app.route('/data_lesson', methods=['POST'])
@cross_origin(origin='*')
def data_lesson():
    global list_id, chuong
    id = request.json['id']
    for i in list_id:
        for e in i["ids"]:
            if (id in str(e)):
                print(i["ids"][i["ids"].index(e)]["baihoc"], i["chuong"])
                for item in chuong:
                    if (item["chuong"] == i["chuong"]):
                        for itbaihoc in item["study"]:
                            if (itbaihoc["baihoc"] == i["ids"][i["ids"].index(e)]["baihoc"]):
                                return itbaihoc
    return "pass"


def emit_client_local(task, place, content):
    data = {
        "task": task,
        "place": place,
        "content": content
    }
    print(data)
    socketio.emit("message_client_local", data)


def emit_client_web(task, place, content):
    data = {
        "task": task,
        "place": place,
        "content": content
    }
    print(data)
    socketio.emit("message_client_web", data)


def emit_page_curr(task, place, content):
    data = {
        "task": task,
        "place": place,
        "content": content
    }
    print(data)
    socketio.emit("message_page_curr", data)


@socketio.on('server_client_web')
def handle_message(data):
    print("data client web: ", data)


@socketio.on('server_client_local')
def handle_message(data):
    print("data client local: ", data)
    emit_client_web(data["task"], data["place"], data["content"])


@socketio.on('page_curr')
def handle_message(data):
    print("page_curr: ", data)
    # emit_page_curr(data["task"], data["place"], data["content"])


# Start Backend
if __name__ == '__main__':
    # from waitress import serve
    # serve(app=socketio, host="0.0.0.0", port=6868)
    socketio.run(app, host="0.0.0.0", port=6868)
