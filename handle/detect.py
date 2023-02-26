import torch
import numpy as np
import pandas
import cv2
import json
import time

class YoloDetect():
    def __init__(self):
        self.model = torch.hub.load("ultralytics/yolov5", "yolov5m") #Truy cập đường dẫn đến model yolov5, lấy model yolov5small https://github.com/ultralytics/yolov5
        self.alert_color = (0,255,0)
        self.prev_frame_time = 0
        self.new_frame_time = 0

    def detect(self, frame):
        self.results = self.model(frame)
        self.pandas_table = self.results.pandas().xyxy[0] #https://github.com/ultralytics/yolov5/issues/3473#issuecomment-1230626263
        self.height, self.width = frame.shape[:2]
        frame = cv2.rectangle(frame, (0, self.height-40), (self.width, self.height), (0, 0, 255), -1)
        #print(pandas_table.to_json(orient = "records"))

        # Convert table to json
        self.json_str = self.pandas_table.to_json(orient = "records")
        self.json_array = json.loads(self.json_str)

        # Find the largest area of object
        for detected_object in self.json_array:
            if detected_object.get("name") != "person":
                self.largest_obj = detected_object
                break
            self.largest_obj = self.json_array[0]
        self.largest_area = 0
        for detected_object in self.json_array:
            #print(detected_object.get("name")) #Export classes names of objects
            self.label = detected_object.get("name")
            confidence = float(detected_object.get("confidence"))
            #print(confidence)
            # Check and pass person objects
            if self.label != 'person' and confidence >= 0.60:
                xmin, ymin = int(detected_object.get("xmin")), int(detected_object.get("ymin")) # Get json value
                xmax, ymax = int(detected_object.get("xmax")), int(detected_object.get("ymax"))

                self.obj_area = (xmax-xmin) * (ymax-ymin) 
                if self.obj_area > self.largest_area:
                    self.largest_obj = detected_object
                    self.largest_area = self.obj_area
                    

        # Draw bouding box for largest object without person
        confidence = float(self.largest_obj.get("confidence"))
        x = int(self.width/2)-10*(len(self.largest_obj.get("name")+str(round(confidence*100))))
        y = self.height-12
        if self.largest_obj.get("name") != "person" and confidence >= 0.60:
            #print(self.largest_obj.get("confidence"))
            xmin, ymin = int(self.largest_obj.get("xmin")), int(self.largest_obj.get("ymin")) # Get json value
            xmax, ymax = int(self.largest_obj.get("xmax")), int(self.largest_obj.get("ymax"))
            frame = cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
            frame = cv2.flip(frame, 1)
            frame = cv2.putText(frame, self.largest_obj.get("name")+": "+str(round(confidence*100))+"%", 
                                (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            #print(self.largest_obj.get("name"))
        else:
            frame = cv2.flip(frame, 1)

        return cv2.imencode('.jpg', frame)[1].tobytes() #frame


class YoloDetectImg():
    def __init__(self):
        self.model = torch.hub.load("ultralytics/yolov5", "yolov5m")

    def detect(self, img_path, option): # 1: return img, 2: return object's name
        #img = cv2.imread(img_path)
        img = img_path
        results = self.model(img)
        pandas_table = results.pandas().xyxy[0]

        vn_classes = ["con người", "xe đạp", "xe hơi", "xe máy", "máy bay", "xe buýt", "tàu hoả", "xe tải", "con thuyền", "đèn giao thông",
              "cột cứu hoả", "biển báo", "máy thu tiền đỗ xe", "ghế dài", "con chim", "con mèo", "con chó", "con ngựa", 
              "con cừu", "con bò", "con voi", "con gấu", "ngựa vằn", "hươu cao cổ", "ba lô", "cái ô", "túi xách", "cà vạt", 
              "va li", "dĩa nhựa ném", "ván trượt", "ván trượt tuyết", "trái bóng", "con diều", "gậy bóng chày", "găng tay bóng chày",
              "ván trượt", "ván lướt", "vợt tennis", "chai nước", "ly rượu", "cái cốc", "cái nĩa", "con dao", "cái thìa", "cái tô", "trái chuối", 
              "trái táo", "bánh kẹp", "trái cam", "bông cải", "cà rốt", "hot dog", "pizza", "bánh vòng", "bánh kem", 
              "cái ghế", "ghế tựa", "chậu hoa", "cái giường", "bàn ăn", "nhà vệ sinh", "ti vi", "laptop", "chuột máy tính", 
              "điều khiển", "bàn phím", "điện thoại", "lò vi sóng", "lò nướng", "máy nướng", "bồn rửa", "tủ lạnh", "cuốn sách", 
              "đồng hồ", "bình hoa", "cây kéo", "gấu bông", "máy sấy", "bàn chải"]
        #print(pandas_table)

        # Convert table to json
        json_str = pandas_table.to_json(orient = "records")
        json_array = json.loads(json_str)

        # Find the largest area of object
        largest_obj = {'xmin': 0, 'ymin': 0, 'xmax': 0, 'ymax': 0, 'confidence': 0, 'class': 0, 'name': 'None'}
        largest_area = 0
        for detected_object in json_array:
            #print(detected_object.get("name")) #Export classes names of objects
            label = detected_object.get("name")
            confidence = float(detected_object.get("confidence"))
            index = detected_object.get("class")
            # Check and pass person objects
            if label != 'person' and confidence >= 0.50 and index != 0:
                xmin, ymin = int(detected_object.get("xmin")), int(detected_object.get("ymin")) # Get json value
                xmax, ymax = int(detected_object.get("xmax")), int(detected_object.get("ymax"))

                obj_area = (xmax-xmin) * (ymax-ymin) 
                if obj_area > largest_area:
                    largest_obj = detected_object
                    largest_area = obj_area

        # Draw bouding box for largest object     
        if option == 1:
            label = largest_obj.get("name")
            index = largest_obj.get("class")
            confidence = float(detected_object.get("confidence"))
            if label != 'person' and confidence >= 0.50 and index != 0:    
                """print(largest_obj.get("name"))
                print(largest_obj.get("confidence"))
                print(largest_obj.get("class"))"""
                largest_obj_name = vn_classes[index]
                print(largest_obj_name)
                return largest_obj_name
            else:
                return print("None")
        elif option == 0:
            xmin, ymin = int(largest_obj.get("xmin")), int(largest_obj.get("ymin")) # Get json value
            xmax, ymax = int(largest_obj.get("xmax")), int(largest_obj.get("ymax"))
            window = cv2.rectangle(img, (xmin, ymin), (xmax, ymax), (0, 0, 255), 2)
            window = cv2.putText(window, label, (xmin, ymin-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            return window

def test(window):
    cv2.imshow("YOLO", window)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# detector = YoloDetectImg()
# img_path = "person2.jpg"
# img = cv2.imread(img_path)
# processed_img = detector.detect(img, 1)
# #test(processed_img)