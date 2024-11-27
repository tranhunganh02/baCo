from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QListWidget, QListWidgetItem, QPushButton
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt
import os

class SavedImagesTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Set up layout
        self.layout = QVBoxLayout()

        # Button to reload images
        self.reload_button = QPushButton("Reload Images", self)
        self.reload_button.clicked.connect(self.load_saved_images)
        self.layout.addWidget(self.reload_button)

        # List to show saved images
        self.image_list = QListWidget(self)
        self.image_list.itemClicked.connect(self.show_selected_image)
        self.layout.addWidget(self.image_list)

        # Label to show the selected image
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.image_label)

        # Set the fixed size for QLabel to 400x300
        self.image_label.setFixedSize(400, 300)

        self.setLayout(self.layout)

        # Load saved images
        self.load_saved_images()

    def load_saved_images(self):
        """ Load saved images into the QListWidget """
        self.image_list.clear()
        if os.path.exists("saved_images"):
            image_files = [f for f in os.listdir("saved_images") if f.endswith(".jpg") or f.endswith(".png")]
            if image_files:
                for filename in image_files:
                    image_path = os.path.join("saved_images", filename)
                    pixmap = QPixmap(image_path)
                    
                    # Check if the image was loaded successfully
                    if not pixmap.isNull():
                        # Create a list item and set the pixmap as an icon (thumbnail)
                        item = QListWidgetItem(QIcon(pixmap.scaled(64, 64, Qt.KeepAspectRatio)), filename)
                        self.image_list.addItem(item)
                    else:
                        self.image_list.addItem(f"Error loading {filename}")
            else:
                self.image_list.addItem("No images saved yet")
        else:
            self.image_list.addItem("No images saved yet")

    def show_selected_image(self, item):
        """ Show selected image in QLabel """
        filename = item.text()
        image_path = os.path.join("saved_images", filename)

        # Check if the image exists
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)

            # Check if the image was loaded successfully
            if not pixmap.isNull():
                # Scale the image to fit the fixed size 400x300 while keeping the aspect ratio
                self.image_label.setPixmap(pixmap.scaled(600, 400, Qt.KeepAspectRatio))
            else:
                self.image_label.setText("Could not load image")
        else:
            self.image_label.setText("Image does not exist")
