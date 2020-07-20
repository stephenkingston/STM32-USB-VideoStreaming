from time import sleep
from PyQt5 import QtCore
import cv2
import numpy as np
from PyQt5.QtCore import QMutex


class VideoProcess(QtCore.QThread):


    def __init__(self, file):
        super().__init__()


    @QtCore.pyqtSlot(np.ndarray)
    def run(self):
        pass

    def play(self):
        self.playFlag = not self.playFlag

        # while self.playFlag:
        #     if self.file is not None:
        #         self.video2.set(1, self.i)
        #         _, frame = self.video2.read()
        #         self.processedFrameReady.emit(frame)
        #         self.sleep(1)
        #         self.i = self.i + 1



