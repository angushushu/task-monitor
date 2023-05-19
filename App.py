from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QMainWindow
from Model import Model
from View import View
from Controller import Controller

class Application:
    def __init__(self):
        import sys
        self.app = QApplication(sys.argv)
        MainWindow = QMainWindow()
        self.model = Model()
        self.view = View(MainWindow, self.model)
        self.controller = Controller(self.model, self.view)

    def run(self):
        self.view.show()
        self.app.exec()

if __name__ == "__main__":
    app = Application()
    app.run()