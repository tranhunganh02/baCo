import os
import cv2
import time
from collections import defaultdict
import numpy as np
from ultralytics import YOLO

# Load the YOLOv8 model
model = YOLO("yolov8_trained_toy_data_ver2.pt")

# Open the webcam (0 is the default camera, you can change it if you have multiple cameras)
cap = cv2.VideoCapture(0)

# Store the track history
track_history_below_roi = defaultdict(lambda: False)  # Track objects below ROI

# roi_point position (vạch đèn đỏ)
roi_points = [(600, 500), (1200, 500)]
is_red_light = True  # Giả sử đèn đỏ đang bật

classList = ['car', 'green_light', 'motocycle', 'red_light']



def is_below_roi(y_object):
    """Kiểm tra xem đối tượng có nằm dưới vạch không"""
    return y_object > roi_points[0][1] - 20

def is_above_roi(y_object):
    """Kiểm tra xem đối tượng có vượt lên trên vạch không"""
    return y_object < roi_points[0][1] + 20

def save_image(frame, track_id, x, y, w, h):
    # Tạo thư mục lưu ảnh nếu chưa có
    if not os.path.exists("saved_images"):
        os.makedirs("saved_images")
    
    # Tạo tên file dựa trên thời gian hiện tại và track_id
    filename = f"saved_images/track_{track_id}_{int(time.time())}.jpg"
    
    # Cắt phần ảnh chứa đối tượng
    x1, y1 = int(x -( w + 100 )/ 2), int(y - ( h  + 100 )/ 2)
    x2, y2 = int(x +( w + 100 )/ 2), int(y + ( h  + 100 )/ 2)
    cropped_image = frame[y1:y2, x1:x2]

    
    # Lưu khung hình đã cắt dưới dạng file ảnh
    # Lưu khung hình dưới dạng file ảnh
    cv2.imwrite(filename, cropped_image)
    print(f"Image saved: {filename}")

# Loop through the webcam feed frames
while cap.isOpened():
    # Read a frame from the webcam
    success, frame = cap.read()

    if success:
        # Run YOLOv8 tracking on the frame, persisting tracks between frames
        results = model.track(frame, persist=True)
        
        # Visualize the results on the frame
        annotated_frame = results[0].plot()

        try:
            # Get the boxes and track IDs
            boxes = results[0].boxes.xywh.cpu()
            track_ids = results[0].boxes.id.int().cpu().tolist()
            classes = results[0].boxes.cls.int().cpu().tolist()

            is_red_light = any(classList[c] == 'red_light' for c in classes)

            for box, track_id in zip(boxes, track_ids):
                x, y, w, h = box
                x, y = float(x), float(y)
    
                # Nếu đối tượng đang nằm dưới vạch roi (vùng đèn đỏ)
                if is_below_roi(y):
                    track_history_below_roi[track_id] = True  # Đánh dấu là đối tượng đang dưới ro
                    #cv2.polylines(annotated_frame, y, isClosed=False, color=(230, 230, 230), thickness=10)
                    print(f"Track ID: {track_id} is below ROI : {y}")
                    

                # Nếu đối tượng trước đó ở dưới vạch, và giờ vượt lên trên vạch
                if track_history_below_roi.get(track_id) and is_above_roi(y):
                    #cv2.polylines(annotated_frame, y, isClosed=False, color=(230, 230, 230), thickness=10)
                    print(f"Track ID: {track_id} has crossed the ROI - Red light violation!")
                    if is_red_light:
                        save_image(frame, track_id, x, y, w, h)  # Lưu ảnh khi đối tượng vượt vạch
                    track_history_below_roi[track_id] = False  # Đánh dấu là đối tượng đã vượt qua
                        
        except Exception as e:
            print(f"An exception occurred: {e}")
            
        # Vẽ vạch ROI
        if len(roi_points) == 2:
            cv2.line(annotated_frame, roi_points[0], roi_points[1], (0, 0, 255), 2)
        
        # Hiển thị khung hình đã được vẽ kết quả
        cv2.imshow("YOLOv8 Tracking", annotated_frame)

        # Thoát nếu nhấn phím 'q'
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        # Thoát vòng lặp nếu không còn khung hình nào
        break

# Giải phóng camera và đóng cửa sổ hiển thị
cap.release()
cv2.destroyAllWindows()
