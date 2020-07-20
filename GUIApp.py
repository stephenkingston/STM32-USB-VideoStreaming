import ui_videoplayer
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtGui import QImage
from PyQt5.QtGui import QPixmap
import VideoProcess
import time
import numpy as np
import cv2


class GUIApp(ui_videoplayer.Ui_MainWindow, QtCore.QObject):
    videoProcessRequest = QtCore.pyqtSignal(str)
    videoPlayPauseRequest = QtCore.pyqtSignal()
    rawFrameReady = QtCore.pyqtSignal(np.ndarray)
    processedFrameReady = QtCore.pyqtSignal(np.ndarray)
    m_processedFrame = ""
    m_rawFrame = ""
    playFlag = False
    worker = None
    file = "D:/SSD1306_VideoPlayer/media/sample.mp4"
    video2 = None
    totFrames = 0
    currentFrame = 1
    i = 0

    def __init__(self, main_window):
        super().__init__()
        self.setupUi(main_window)
        self.playButton.setDisabled(True)
        self.fileInputButton.clicked.connect(self.BrowseFile)
        self.playButton.clicked.connect(self.startPlay)
        self.rawFrameReady.connect(self.displayRawFrame)  # Connect your signals/slots
        self.processedFrameReady.connect(self.displayProcessedFrame)

        self.m_processedFrame = "Hello"
        self.playFlag = False
        self.video2 = None

    def BrowseFile(self):
        self.file, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Select Video", "",
                                                            "Video files (*.mp4 *.mpeg *.mpg *.mkv)")
        if self.file:
            self.playButton.setDisabled(False)
            self.fileInputTextEdit.setPlainText(self.file)

    def displayRawFrame(self, raw_frame):
        height, width, channel = raw_frame.shape
        bytesPerLine = 3 * width
        qImg = QImage(raw_frame.data, width, height, bytesPerLine, QImage.Format_RGB888)
        self.processedVideoLabel_2.setPixmap(QPixmap(qImg))

    def displayProcessedFrame(self, processed_frame):
        # self.fileInputTextEdit.appendPlainText("Success 2")

        height, width, channel = processed_frame.shape
        bytesPerLine = 3 * width
        qImg = QImage(processed_frame.data, width, height, bytesPerLine, QImage.Format_RGB888)
        self.processedVideoLabel.setPixmap(QPixmap(qImg))

    def initVideoThread(self, file):
        # self.video2 = cv2.VideoCapture(self.file)
        # self.totFrames = self.video2.get(cv2.CAP_PROP_FRAME_COUNT)
        # self.video2.set(cv2.CAP_PROP_POS_FRAMES, 1)
        # success, frame = self.video2.read()
        # self.processedFrameReady.emit(frame)
        # time.sleep(0.05)
        pass

    def startPlay(self):
        self.playFlag = not self.playFlag
        self.play()

    def play(self):
        self.video2 = cv2.VideoCapture(self.file)
        self.video2.set(cv2.CAP_PROP_FPS, 20)
        while self.playFlag is True:
            self.video2.set(cv2.CAP_PROP_POS_FRAMES, self.currentFrame)
            self.currentFrame = self.currentFrame + 1
            success, frame = self.video2.read()
            if not success:
                break
            self.displayProcessedFrame(frame)
            self.displayRawFrame(frame)
            cv2.waitKey(10)
