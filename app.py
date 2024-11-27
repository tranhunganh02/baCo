import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout
from live_camera_tab import LiveCameraTab
from saved_images_tab import SavedImagesTab


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Red Light Violation Detection")
        self.setGeometry(100, 100, 900, 600)

        # Create tab widget
        self.tabs = QTabWidget()

        # Create individual tabs
        self.live_camera_tab = LiveCameraTab(self)
        self.saved_images_tab = SavedImagesTab(self)

        # Add tabs to the widget
        self.tabs.addTab(self.live_camera_tab, "Live Camera")
        self.tabs.addTab(self.saved_images_tab, "Saved Images")
         # Start camera immediately when the application starts
        self.live_camera_tab.start_camera()

        # Set central widget
        self.setCentralWidget(self.tabs)

        # Connect tab change event
        self.tabs.currentChanged.connect(self.on_tab_change)

    def on_tab_change(self, index):
        if index == 0:  # Live Camera tab
            self.live_camera_tab.start_camera()
        else:  # Saved Images tab
            self.live_camera_tab.stop_camera()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_app = MainApp()
    main_app.show()
    sys.exit(app.exec_())
