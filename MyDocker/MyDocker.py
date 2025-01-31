from krita import *  # Krita API
from PyQt5.QtCore import Qt, QSize  # Qt constants
from PyQt5.QtWidgets import (  # PyQt5 widgets
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QSlider, QLabel, QPushButton, QMessageBox
)
from PyQt5.QtGui import QIcon, QPixmap, QImage  # For handling images
import cv2
import numpy as np

class MyDocker(DockWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My Docker")  # Set the title of the Docker
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

        # Tab 1: Blur options and slider
        self.tab1 = QWidget()
        self.tab1_layout = QVBoxLayout()
        self.tab1.setLayout(self.tab1_layout)

        # Create buttons for blur options with sample images
        self.gaussian_button = self.create_blur_button("Gaussian")
        self.bilateral_button = self.create_blur_button("Bilateral")
        self.median_button = self.create_blur_button("Median")

        # Add buttons to tab1 layout
        self.tab1_layout.addWidget(self.gaussian_button)
        self.tab1_layout.addWidget(self.bilateral_button)
        self.tab1_layout.addWidget(self.median_button)

        # Create a slider for intensity
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(1)  # Minimum intensity
        self.slider.setMaximum(15)  # Maximum intensity
        self.slider.setValue(5)  # Default intensity
        self.slider.setTickInterval(1)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.hide()  # Hide slider initially

        # Add slider to tab1 layout
        self.tab1_layout.addWidget(self.slider)

        # Connect buttons to their respective functions
        self.gaussian_button.clicked.connect(self.show_gaussian_slider)
        self.bilateral_button.clicked.connect(self.show_bilateral_slider)
        self.median_button.clicked.connect(self.show_median_slider)
        self.slider.valueChanged.connect(self.apply_blur)

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
        self.tab_widget.addTab(self.tab1, "Blur Options")
        self.tab_widget.addTab(self.tab2, "Tab 2")
        self.tab_widget.addTab(self.tab3, "Tab 3")

        # Initialize blur type
        self.blur_type = None

    def create_blur_button(self, text):
        """Create a button with a preview of the current canvas and text below."""
        button = QPushButton(text)
        button.setIconSize(QSize(100, 100))  # Set icon size
        button.setToolTip(f"Apply {text} blur to the canvas")
        return button

    def update_button_previews(self):
        """Update the preview images on the buttons based on the current canvas."""
        document = Krita.instance().activeDocument()
        if not document:
            return

        # Get the active layer
        layer = document.activeNode()
        if not layer:
            return

        # Convert the layer to a numpy array
        pixel_data = layer.projectionPixelData(0, 0, document.width(), document.height())
        image = np.frombuffer(pixel_data, dtype=np.uint8)
        image = image.reshape(document.height(), document.width(), 4)  # RGBA

        # Convert to BGR for OpenCV
        bgr_image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)

        # Generate previews for each blur type
        gaussian_preview = self.apply_blur_to_image(bgr_image, "gaussian", self.slider.value())
        bilateral_preview = self.apply_blur_to_image(bgr_image, "bilateral", self.slider.value())
        median_preview = self.apply_blur_to_image(bgr_image, "median", self.slider.value())

        # Set preview images to buttons
        self.set_button_preview(self.gaussian_button, gaussian_preview, "Gaussian")
        self.set_button_preview(self.bilateral_button, bilateral_preview, "Bilateral")
        self.set_button_preview(self.median_button, median_preview, "Median")

    def set_button_preview(self, button, image, text):
        """Set a preview image and text to a button."""
        # Convert the image to QPixmap
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        qimage = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)

        # Set icon and text
        button.setIcon(QIcon(pixmap))
        button.setText(text)

    def apply_blur_to_image(self, image, blur_type, intensity):
        """Apply the selected blur to an image and return the result."""
        if blur_type == "gaussian":
            kernel_size = intensity if intensity % 2 != 0 else intensity + 1  # Ensure odd kernel size
            blurred_image = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
        elif blur_type == "bilateral":
            blurred_image = cv2.bilateralFilter(image, intensity, 75, 75)
        elif blur_type == "median":
            kernel_size = intensity if intensity % 2 != 0 else intensity + 1  # Ensure odd kernel size
            blurred_image = cv2.medianBlur(image, kernel_size)
        else:
            blurred_image = image  # No blur applied

        return blurred_image

    def show_gaussian_slider(self):
        """Show slider for Gaussian blur."""
        self.blur_type = "gaussian"
        self.slider.show()
        self.update_button_previews()

    def show_bilateral_slider(self):
        """Show slider for Bilateral blur."""
        self.blur_type = "bilateral"
        self.slider.show()
        self.update_button_previews()

    def show_median_slider(self):
        """Show slider for Median blur."""
        self.blur_type = "median"
        self.slider.show()
        self.update_button_previews()

    def apply_blur(self, value):
        """Apply the selected blur to the active canvas."""
        if not self.blur_type:
            return

        # Get the active document
        document = Krita.instance().activeDocument()
        if not document:
            QMessageBox.warning(self, "Error", "No active document found!")
            return

        # Get the active layer
        layer = document.activeNode()
        if not layer:
            QMessageBox.warning(self, "Error", "No active layer found!")
            return

        # Convert the layer to a numpy array
        pixel_data = layer.projectionPixelData(0, 0, document.width(), document.height())
        image = np.frombuffer(pixel_data, dtype=np.uint8)
        image = image.reshape(document.height(), document.width(), 4)  # RGBA

        # Convert to BGR for OpenCV
        bgr_image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)

        # Apply the selected blur
        blurred_image = self.apply_blur_to_image(bgr_image, self.blur_type, value)

        # Convert back to RGBA
        rgba_image = cv2.cvtColor(blurred_image, cv2.COLOR_BGR2RGBA)

        # Update the layer with the blurred image
        layer.setPixelData(rgba_image.tobytes(), 0, 0, document.width(), document.height())
        document.refreshProjection()

    def canvasChanged(self, canvas):
        """
        This method is called whenever the active canvas changes.
        You can use it to update your Docker's UI based on the new canvas.
        """
        print("Active canvas changed!")
        # Update button previews when the canvas changes
        self.update_button_previews()

# Register the Docker with Krita
Krita.instance().addDockWidgetFactory(DockWidgetFactory("MyDocker", DockWidgetFactoryBase.DockRight, MyDocker))