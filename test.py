import cv2
from ultralytics import YOLO
import time

# Tải mô hình YOLOv8 đã huấn luyện
model = YOLO('yolov8_trained.pt')  # Thay đường dẫn tới mô hình của bạn

video_path = 'traffic01.mp4'  # Thay đường dẫn tới video của bạn
cap = cv2.VideoCapture(video_path)

# Kiểm tra nếu mở video thành công
if not cap.isOpened():
    print("Error: Không thể mở video.")
    exit()

frame_skip = 2  # Số khung hình bỏ qua để tăng tốc độ xử lý
frame_id = 0  # Khởi tạo biến đếm khung hình

# Xử lý từng khung hình
while cap.isOpened():
    start_time = time.time()  # Đo thời gian bắt đầu xử lý khung hình

    ret, frame = cap.read()
    if not ret:
        break

    # Bỏ qua các khung hình dựa trên frame_skip
    if frame_id % frame_skip == 0:
        # Resize khung hình để giảm độ phân giải và tăng tốc độ xử lý
        frame = cv2.resize(frame, (1200, 500))  # Thay đổi kích thước tùy theo yêu cầu

        # Phát hiện đối tượng trong khung hình
        results = model(frame)

        # Vẽ các đối tượng được phát hiện lên khung hình
        annotated_frame = results[0].plot()

        # Hiển thị khung hình đã được chú thích
        cv2.imshow('YOLOv8 Detection', annotated_frame)

    frame_id += 1

    # Tính toán và in FPS để theo dõi hiệu suất
    end_time = time.time()
    fps = 1 / (end_time - start_time)
    print(f"FPS: {fps:.2f}")

    # Nhấn 'q' để thoát khỏi video
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Giải phóng tài nguyên
cap.release()
cv2.destroyAllWindows()
