from krita import DockWidget, DockWidgetFactory, DockWidgetFactoryBase, Krita
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QSlider, QLabel, 
    QFrame, QPushButton, QButtonGroup, QRadioButton
)
import sys
sys.path.append("/Users/chauvu/krita-opencv-env/lib/python3.10/site-packages")
import cv2
print(cv2.__version__)
import numpy as np

class MyDocker(DockWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My Docker")
        self.current_filter = None
        self.kernel_percentages = [0.015, 0.025, 0.049]  # 1.5%, 2.5%, 4.9%
        self.setUI()

    def setUI(self):
        # Main widget
        self.main_widget = QWidget()
        self.setWidget(self.main_widget)
        
        # Main layout
        self.main_layout = QVBoxLayout()
        self.main_widget.setLayout(self.main_layout)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        # Tab 1: Filter options and slider
        self.tab1 = QWidget()
        self.tab1_layout = QVBoxLayout()
        self.tab1.setLayout(self.tab1_layout)
        
        # Create filter selection group
        self.filter_group = QButtonGroup()
        
        # Gaussian filter option
        self.gaussian_box = QFrame()
        self.gaussian_box.setFrameShape(QFrame.Box)
        self.gaussian_layout = QVBoxLayout()
        self.gaussian_box.setLayout(self.gaussian_layout)
        self.gaussian_radio = QRadioButton("Gaussian Blur")
        self.gaussian_radio.clicked.connect(lambda: self.filter_selected("gaussian"))
        self.gaussian_layout.addWidget(self.gaussian_radio)
        self.filter_group.addButton(self.gaussian_radio)
        
        # Bilateral filter option
        self.bilateral_box = QFrame()
        self.bilateral_box.setFrameShape(QFrame.Box)
        self.bilateral_layout = QVBoxLayout()
        self.bilateral_box.setLayout(self.bilateral_layout)
        self.bilateral_radio = QRadioButton("Bilateral Filter")
        self.bilateral_radio.clicked.connect(lambda: self.filter_selected("bilateral"))
        self.bilateral_layout.addWidget(self.bilateral_radio)
        self.filter_group.addButton(self.bilateral_radio)
        
        # Median filter option
        self.median_box = QFrame()
        self.median_box.setFrameShape(QFrame.Box)
        self.median_layout = QVBoxLayout()
        self.median_box.setLayout(self.median_layout)
        self.median_radio = QRadioButton("Median Blur")
        self.median_radio.clicked.connect(lambda: self.filter_selected("median"))
        self.median_layout.addWidget(self.median_radio)
        self.filter_group.addButton(self.median_radio)
        
        # Add filter boxes to tab1 layout
        self.tab1_layout.addWidget(self.gaussian_box)
        self.tab1_layout.addWidget(self.bilateral_box)
        self.tab1_layout.addWidget(self.median_box)
        
        # Create a slider (hidden by default)
        self.slider_label = QLabel("Intensity:")
        self.slider_label.hide()
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(2)  # For the three percentages
        self.slider.setValue(0)
        self.slider.valueChanged.connect(self.apply_filter)
        self.slider.hide()
        
        # Add slider and label to tab1 layout
        self.tab1_layout.addWidget(self.slider_label)
        self.tab1_layout.addWidget(self.slider)
        
        # Tab 2: Simple label
        self.tab2 = QWidget()
        self.tab2_layout = QVBoxLayout()
        self.tab2.setLayout(self.tab2_layout)
        self.label_tab2 = QLabel("This is Tab 2")
        self.tab2_layout.addWidget(self.label_tab2)
        
        # Tab 3: Another label
        self.tab3 = QWidget()
        self.tab3_layout = QVBoxLayout()
        self.tab3.setLayout(self.tab3_layout)
        self.label_tab3 = QLabel("This is Tab 3")
        self.tab3_layout.addWidget(self.label_tab3)
        
        # Add tabs to the tab widget
        self.tab_widget.addTab(self.tab1, "Filters")
        self.tab_widget.addTab(self.tab2, "Tab 2")
        self.tab_widget.addTab(self.tab3, "Tab 3")

    def filter_selected(self, filter_type):
        self.current_filter = filter_type
        self.slider_label.show()
        self.slider.show()
        self.apply_filter(self.slider.value())

    def apply_filter(self, value):
        document = Krita.instance().activeDocument()
        if document and self.current_filter:
            # Get the active node (layer)
            node = document.activeNode()
            if node:
                # Convert Krita image to numpy array
                bounds = node.bounds()
                pixel_data = node.pixelData(bounds.x(), bounds.y(), bounds.width(), bounds.height())
                img = np.frombuffer(pixel_data, dtype=np.uint8).reshape(bounds.height(), bounds.width(), 4)
                
                # Convert to grayscale if needed
                if len(img.shape) > 2:
                    gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
                else:
                    gray = img
                
                # Calculate kernel size
                hw_max = max(gray.shape)
                kernel_size = int(hw_max * self.kernel_percentages[value])
                if kernel_size % 2 == 0:
                    kernel_size += 1
                
                # Apply selected filter
                if self.current_filter == "gaussian":
                    filtered = cv2.GaussianBlur(gray, (kernel_size, kernel_size), 0)
                elif self.current_filter == "bilateral":
                    filtered = cv2.bilateralFilter(gray, kernel_size, 75, 75)
                elif self.current_filter == "median":
                    filtered = cv2.medianBlur(gray, kernel_size)
                
                # Convert back to RGBA
                if len(img.shape) > 2:
                    filtered_rgba = cv2.cvtColor(filtered, cv2.COLOR_GRAY2BGRA)
                else:
                    filtered_rgba = cv2.cvtColor(filtered, cv2.COLOR_GRAY2BGRA)
                
                # Update the layer
                node.setPixelData(filtered_rgba.tobytes(), bounds.x(), bounds.y(), bounds.width(), bounds.height())
                document.refreshProjection()

    def canvasChanged(self, canvas):
        if canvas:
            document = Krita.instance().activeDocument()
            if document:
                print(f"Active document: {document.name()}")

# Register the Docker with Krita
Krita.instance().addDockWidgetFactory(DockWidgetFactory("MyDocker", DockWidgetFactoryBase.DockRight, MyDocker))


# test code in case everything broke
# from krita import DockWidget, DockWidgetFactory, DockWidgetFactoryBase, Krita
# from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget
# class MyDocker(DockWidget):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("My Docker")
        
#         # Create a simple UI
#         self.main_widget = QWidget()
#         self.layout = QVBoxLayout()
#         self.label = QLabel("Hello, Krita!")
#         self.layout.addWidget(self.label)
#         self.main_widget.setLayout(self.layout)
#         self.setWidget(self.main_widget)

# # Register the docker with Krita
# Krita.instance().addDockWidgetFactory(
#     DockWidgetFactory("MyDocker", DockWidgetFactoryBase.DockRight, MyDocker)
# )
