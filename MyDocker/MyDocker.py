from krita import DockWidget, DockWidgetFactory, DockWidgetFactoryBase, Krita
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QSlider, QLabel, 
    QFrame, QPushButton, QButtonGroup, QRadioButton
)
from PyQt5.QtGui import QImage, QPixmap
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
        self.min_kernel_percentage = 1.5  # Minimum kernel size percentage
        self.max_kernel_percentage = 4.9  # Maximum kernel size percentage
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
        self.gaussian_radio = QRadioButton("Gaussian")
        self.gaussian_radio.clicked.connect(lambda: self.filter_selected("gaussian"))
        self.gaussian_layout.addWidget(self.gaussian_radio)
        self.filter_group.addButton(self.gaussian_radio)
        
        # Bilateral filter option
        self.bilateral_box = QFrame()
        self.bilateral_box.setFrameShape(QFrame.Box)
        self.bilateral_layout = QVBoxLayout()
        self.bilateral_box.setLayout(self.bilateral_layout)
        self.bilateral_radio = QRadioButton("Bilateral")
        self.bilateral_radio.clicked.connect(lambda: self.filter_selected("bilateral"))
        self.bilateral_layout.addWidget(self.bilateral_radio)
        self.filter_group.addButton(self.bilateral_radio)
        
        # Median filter option
        self.median_box = QFrame()
        self.median_box.setFrameShape(QFrame.Box)
        self.median_layout = QVBoxLayout()
        self.median_box.setLayout(self.median_layout)
        self.median_radio = QRadioButton("Median")
        self.median_radio.clicked.connect(lambda: self.filter_selected("median"))
        self.median_layout.addWidget(self.median_radio)
        self.filter_group.addButton(self.median_radio)
        
        # Add filter boxes to tab1 layout
        self.tab1_layout.addWidget(self.gaussian_box)
        self.tab1_layout.addWidget(self.bilateral_box)
        self.tab1_layout.addWidget(self.median_box)
        
        # Create a slider for kernel size percentage
        self.slider_label = QLabel("Kernel Size (%): 1.5%")
        self.slider_label.hide()
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(15)  # Represent 1.5% as 15 (to avoid floating-point issues)
        self.slider.setMaximum(49)  # Represent 4.9% as 49
        self.slider.setValue(15)    # Default to 1.5%
        self.slider.valueChanged.connect(self.update_kernel_size_label)
        self.slider.valueChanged.connect(self.update_preview)
        self.slider.hide()
        
        # Add slider and label to tab1 layout
        self.tab1_layout.addWidget(self.slider_label)
        self.tab1_layout.addWidget(self.slider)
        
        # Preview widget
        self.preview_label = QLabel("Preview will appear here")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("background-color: black; color: white;")
        
        # Set a minimum size for the preview label to make it larger
        self.preview_label.setMinimumSize(400, 400)  # Adjust the size as needed
        
        # Add the preview label to the layout
        self.tab1_layout.addWidget(self.preview_label)
        
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
        self.tab_widget.addTab(self.tab1, "Value")
        self.tab_widget.addTab(self.tab2, "Tab 2")
        self.tab_widget.addTab(self.tab3, "Tab 3")

    def filter_selected(self, filter_type):
        self.current_filter = filter_type
        self.slider_label.show()
        self.slider.show()
        self.update_preview(self.slider.value())

    def update_kernel_size_label(self, value):
        # Convert slider value to percentage (e.g., 15 -> 1.5%)
        kernel_percentage = value / 10.0
        self.slider_label.setText(f"Kernel Size (%): {kernel_percentage:.1f}%")

    def update_preview(self, value):
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
                
                # Calculate kernel size based on slider value
                kernel_percentage = value / 10.0  # Convert slider value to percentage
                hw_max = max(gray.shape)
                kernel_size = int(hw_max * (kernel_percentage / 100.0))
                if kernel_size % 2 == 0:
                    kernel_size += 1  # Ensure kernel size is odd
                
                # Apply selected filter
                if self.current_filter == "gaussian":
                    filtered = cv2.GaussianBlur(gray, (kernel_size, kernel_size), 0)
                elif self.current_filter == "bilateral":
                    filtered = cv2.bilateralFilter(gray, kernel_size, 75, 75)
                elif self.current_filter == "median":
                    filtered = cv2.medianBlur(gray, kernel_size)
                
                # Convert back to RGBA for preview
                if len(img.shape) > 2:
                    filtered_rgba = cv2.cvtColor(filtered, cv2.COLOR_GRAY2BGRA)
                else:
                    filtered_rgba = cv2.cvtColor(filtered, cv2.COLOR_GRAY2BGRA)
                
                # Convert the filtered image to QImage for preview
                height, width, channel = filtered_rgba.shape
                bytes_per_line = 4 * width
                qimage = QImage(filtered_rgba.data, width, height, bytes_per_line, QImage.Format_ARGB32)
                pixmap = QPixmap.fromImage(qimage)
                
                # Scale the pixmap to fit the preview label
                self.preview_label.setPixmap(pixmap.scaled(self.preview_label.width(), self.preview_label.height(), Qt.KeepAspectRatio))

    def canvasChanged(self, canvas):
        if canvas:
            document = Krita.instance().activeDocument()
            if document:
                print(f"Active document: {document.name()}")

# Register the Docker with Krita
Krita.instance().addDockWidgetFactory(DockWidgetFactory("MyDocker", DockWidgetFactoryBase.DockRight, MyDocker))