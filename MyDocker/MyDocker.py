from krita import *  # Krita API
from PyQt5.QtCore import Qt  # Qt constants
from PyQt5.QtWidgets import (  # PyQt5 widgets
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QSlider, QLabel, QFrame
)

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

        # Tab 1: Three smaller boxes and a slider
        self.tab1 = QWidget()
        self.tab1_layout = QVBoxLayout()
        self.tab1.setLayout(self.tab1_layout)

        # Create three smaller boxes
        self.box1 = QFrame()
        self.box1.setFrameShape(QFrame.Box)
        self.box1.setFixedSize(100, 50)
        self.box1.setStyleSheet("background-color: red;")

        self.box2 = QFrame()
        self.box2.setFrameShape(QFrame.Box)
        self.box2.setFixedSize(100, 50)
        self.box2.setStyleSheet("background-color: green;")

        self.box3 = QFrame()
        self.box3.setFrameShape(QFrame.Box)
        self.box3.setFixedSize(100, 50)
        self.box3.setStyleSheet("background-color: blue;")

        # Add boxes to tab1 layout
        self.tab1_layout.addWidget(self.box1)
        self.tab1_layout.addWidget(self.box2)
        self.tab1_layout.addWidget(self.box3)

        # Create a slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(50)
        self.slider.valueChanged.connect(self.slider_changed)

        # Add slider to tab1 layout
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
        self.tab_widget.addTab(self.tab1, "Tab 1")
        self.tab_widget.addTab(self.tab2, "Tab 2")
        self.tab_widget.addTab(self.tab3, "Tab 3")

    def slider_changed(self, value):
        print(f"Slider value changed to: {value}")

    def canvasChanged(self, canvas):
        """
        This method is called whenever the active canvas changes.
        You can use it to update your Docker's UI based on the new canvas.
        """
        print("Active canvas changed!")
        # Get the active document
        document = Krita.instance().activeDocument()
        if document:
            print(f"Active document: {document.name()}")

# Register the Docker with Krita
Krita.instance().addDockWidgetFactory(DockWidgetFactory("MyDocker", DockWidgetFactoryBase.DockRight, MyDocker))