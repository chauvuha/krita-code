from krita import Extension, Krita
from PyQt5.QtWidgets import QMessageBox
class TestPlugin(Extension):
    def __init__(self, parent):
        super().__init__(parent)
    def setup(self):
        pass
    def createActions(self, window):
        action = window.createAction("testPlugin", "Test Plugin", "tools/scripts")
        action.triggered.connect(self.showMessage)
    def showMessage(self):
        QMessageBox.information(None, "Test Plugin", "Hello! Your plugin is working!")
Krita.instance().addExtension(TestPlugin(Krita.instance()))