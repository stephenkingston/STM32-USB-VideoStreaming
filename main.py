import GUIApp
from PyQt5 import QtWidgets
import sys
import VideoProcess


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = GUIApp.GUIApp(MainWindow)

    MainWindow.show()
    sys.exit(app.exec_())
