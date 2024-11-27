import cv2
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer
from ultralytics import YOLO
import time
import os
from datetime import datetime


classList = ['car', 'green_light', 'motocycle', 'red_light']


class LiveCameraTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Initialize YOLO model
        try:
            self.model = YOLO("yolov8_trained_toy_data_ver2.pt")
        except Exception as e:
            print(f"Error loading YOLO model: {e}")

        # Set up camera
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Could not open camera.")

        # Set up the layout
        self.layout = QVBoxLayout()

        # Label for camera feed
        self.camera_label = QLabel(self)
        self.layout.addWidget(self.camera_label)

        self.setLayout(self.layout)

        # Initialize ROI points and timer
        self.roi_points = [(300, 300), (650, 300)]
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)

        # Flag to store if red light is on
        self.is_red_light = True

        # Track history
        self.track_history_below_roi = {}

    def is_below_roi(self, y_object):
        return y_object > self.roi_points[0][1]

    def is_above_roi(self, y_object):
        return y_object < self.roi_points[0][1]

    def save_image(self, frame, track_id, x, y, w, h):
        if not os.path.exists("saved_images"):
            os.makedirs("saved_images")
        
        # Lấy thời gian hiện tại và định dạng
        current_time = datetime.now().strftime("%H-%M-%S | %d-%m-%Y")
        filename = f"saved_images/{current_time}.jpg"  # Đặt tên file theo định dạng mới

        cropped_image = frame[int(y - (h + 200) / 2):int(y + (h + 200) / 2),
                            int(x - (w + 200) / 2):int(x + (w + 200) / 2)]
        cv2.imwrite(filename, cropped_image)

    def update_frame(self):
        success, frame = self.cap.read()
        if success:
            frame = cv2.resize(frame, (900, 600))
            results = self.model.track(frame, persist=True)
            annotated_frame = results[0].plot()

            try:
                boxes = results[0].boxes.xywh.cpu()
                track_ids = results[0].boxes.id.int().cpu().tolist()
                classes = results[0].boxes.cls.int().cpu().tolist()
                confidences = results[0].boxes.conf.cpu().tolist()

                # Check if red light is detected
                # self.is_red_light = any(classList[c] == 'red_light' for c in classes)

                for box, track_id, cls, conf in zip(boxes, track_ids, classes, confidences):
                    x, y, w, h = box

                    # Only process objects with confidence > 0.75
                    if conf > 0.75:
                        # If red light is detected
                        if self.is_red_light:
                            if self.is_below_roi(y):
                                self.track_history_below_roi[track_id] = True
                                print(f"Track ID: {track_id} is below ROI : {y}")

                            if self.track_history_below_roi.get(track_id) and self.is_above_roi(y):
                                print(f"Track ID: {track_id} has crossed the ROI - Red light violation!")
                                self.save_image(frame, track_id, x, y, w, h)
                                self.track_history_below_roi[track_id] = False



            except Exception as e:
                print(f"Error: {e}")

            # Draw ROI line
            cv2.line(annotated_frame, self.roi_points[0], self.roi_points[1], (0, 0, 255), 2)

            # Convert frame to RGB for PyQt display
            rgb_image = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            converted_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.camera_label.setPixmap(QPixmap.fromImage(converted_image))

    def start_camera(self):
        self.timer.start(30)

    def stop_camera(self):
        self.timer.stop()

    def closeEvent(self, event):
        self.cap.release()