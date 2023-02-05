import time
import json
import cv2
import pandas
import numpy as np
import torch


def detect(img):
    text = YoloDetectImg().detect(img, 1)
    return text


class YoloDetect():
    def __init__(self):
        # Truy cập đường dẫn đến model yolov5, lấy model yolov5small https://github.com/ultralytics/yolov5
        self.model = torch.hub.load("ultralytics/yolov5", "yolov5s")
        self.alert_color = (0, 255, 0)
        self.prev_frame_time = 0
        self.new_frame_time = 0

    def detect(self, frame):
        self.results = self.model(frame)
        # https://github.com/ultralytics/yolov5/issues/3473#issuecomment-1230626263
        self.pandas_table = self.results.pandas().xyxy[0]
        self.height, self.width = frame.shape[:2]
        frame = cv2.rectangle(frame, (0, self.height-40),
                              (self.width, self.height), (0, 0, 255), -1)
        # print(pandas_table.to_json(orient = "records"))

        # Convert table to json
        self.json_str = self.pandas_table.to_json(orient="records")
        self.json_array = json.loads(self.json_str)

        # Find the largest area of object
        for detected_object in self.json_array:
            if detected_object.get("name") != "person":
                self.largest_obj = detected_object
                break
            self.largest_obj = self.json_array[0]
        self.largest_area = 0
        for detected_object in self.json_array:
            # print(detected_object.get("name")) #Export classes names of objects
            self.label = detected_object.get("name")
            # Check and pass person objects
            if self.label != 'person':
                xmin, ymin = int(detected_object.get("xmin")), int(
                    detected_object.get("ymin"))  # Get json value
                xmax, ymax = int(detected_object.get("xmax")), int(
                    detected_object.get("ymax"))

                self.obj_area = (xmax-xmin) * (ymax-ymin)
                if self.obj_area > self.largest_area:
                    self.largest_obj = detected_object
                    self.largest_area = self.obj_area

        # Draw bouding box for largest object without person
        if self.largest_obj.get("name") != "person":
            xmin, ymin = int(self.largest_obj.get("xmin")), int(
                self.largest_obj.get("ymin"))  # Get json value
            xmax, ymax = int(self.largest_obj.get("xmax")), int(
                self.largest_obj.get("ymax"))
            frame = cv2.rectangle(frame, (xmin, ymin),
                                  (xmax, ymax), (0, 255, 0), 2)
            frame = cv2.flip(frame, 1)
            frame = cv2.putText(frame, self.largest_obj.get("name"), (int(self.width/2)-10*len(
                self.largest_obj.get("name")), self.height-12), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            print(self.largest_obj.get("name"))
        else:
            frame = cv2.flip(frame, 1)

        return cv2.imencode('.jpg', frame)[1].tobytes()  # frame


class YoloDetectImg():
    def __init__(self):
        self.model = torch.hub.load("ultralytics/yolov5", "yolov5s")

    def detect(self, img_path, option):  # 1: return img, 2: return object's name
        # img = cv2.imread(img_path)
        img = img_path
        results = self.model(img)
        pandas_table = results.pandas().xyxy[0]

        # Convert table to json
        json_str = pandas_table.to_json(orient="records")
        json_array = json.loads(json_str)

        # Find the largest area of object
        largest_obj = json_array[0]
        largest_area = 0
        for detected_object in json_array:
            # Export classes names of objects
            # print(detected_object.get("name"))
            label = detected_object.get("name")
            # Check and pass person objects
            if label != 'person':
                xmin, ymin = int(detected_object.get("xmin")), int(
                    detected_object.get("ymin"))  # Get json value
                xmax, ymax = int(detected_object.get("xmax")), int(
                    detected_object.get("ymax"))

                obj_area = (xmax-xmin) * (ymax-ymin)
                if obj_area > largest_area:
                    largest_obj = detected_object
                    largest_area = obj_area

                if option == 1:
                    print(largest_obj.get("name"))
                    return largest_obj.get("name")
                elif option == 2:
                    return window

        # Draw bouding box for largest object
        xmin, ymin = int(largest_obj.get("xmin")), int(
            largest_obj.get("ymin"))  # Get json value
        xmax, ymax = int(largest_obj.get("xmax")), int(largest_obj.get("ymax"))
        window = cv2.rectangle(img, (xmin, ymin), (xmax, ymax), (0, 0, 255), 2)
        window = cv2.putText(window, label, (xmin, ymin-10),
                             cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)


def test(window):
    cv2.imshow("YOLO", window)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


"""
detector = YoloDetectImg()
img_path = "article_photo1_330.jpg"
processed_img = detector.detect(img_path)
test(processed_img)
"""
