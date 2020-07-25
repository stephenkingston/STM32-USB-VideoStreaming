from PyQt5 import QtCore
import cv2
from PyQt5.QtGui import QImage, QPixmap
from PyQt5 import QtGui
import serial
comport = 'COM6'

class VideoProcess(QtCore.QThread):
    rawFrameReady = QtCore.pyqtSignal(QPixmap)
    processedFrameReady = QtCore.pyqtSignal(QPixmap)
    progressBarStatus = QtCore.pyqtSignal(int)
    errorSignal = QtCore.pyqtSignal(Exception)
    setupSlider = QtCore.pyqtSignal(int)
    updateSlider = QtCore.pyqtSignal(int)
    updateBS = QtCore.pyqtSignal(int)
    updateConstant = QtCore.pyqtSignal(int)
    playPauseSignal = QtCore.pyqtSignal()
    enableStream = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.currentFrame = 1
        self.file = None
        self.video2 = None
        self.totFrames = 0
        self.currentFrame = 1
        self.playFlag = False
        self.video2 = None
        self.BLOCK_SIZE = 7
        self.THRESHOLDING_CONSTANT = 4
        self.delay = 25
        self.frames = []
        self.lowerRAMUsage = False
        self.streamChecked = False
        self.activePort = None
        self.ser = None
        self.invert = 0

    def newVideoAdded(self):
        self.video2 = cv2.VideoCapture(self.file)
        self.totFrames = self.video2.get(cv2.CAP_PROP_FRAME_COUNT) - 1
        self.setupSlider.emit(self.totFrames)

        while True:
            _, f = self.video2.read()
            if self.lowerRAMUsage is True:
                height, width, channel = f.shape
                resized = cv2.resize(f, None, fx=128.0 / width, fy=64.0 / height)
                self.frames.append(resized)
            else:
                self.frames.append(f)
            current = self.video2.get(cv2.CAP_PROP_POS_FRAMES)
            self.progressBarStatus.emit(int((current/self.totFrames) * 100.0))
            if current == self.totFrames:
                print("Video loaded!")
                break

        self.emitProcessedFrame(self.frames[1])
        self.emitRawFrame(self.frames[1])

    @QtCore.pyqtSlot(QPixmap)
    def run(self):
        pass

    def connect(self):
        try:
            self.ser = serial.Serial()
            self.ser.baudrate = 115200
            self.ser.timeout = 10
            self.ser.port = str(self.activePort)
            self.ser.open()
            self.errorSignal.emit(Exception("Connected via the selected port: " + self.activePort))
            self.enableStream.emit()
        except Exception as e:
            self.errorSignal.emit(e)

    def startPlay(self):
        self.playFlag = not self.playFlag
        self.play()

    def emitRawFrame(self, rawFrame):
        height, width, channel = rawFrame.shape
        bytesPerLine = 3 * width
        rawQImg = QImage(rawFrame.data, width, height, bytesPerLine, QImage.Format_BGR888)
        self.rawFrameReady.emit(QPixmap(rawQImg))

    def emitProcessedFrame(self, inputFrame):
        processedFrame = self.processFrame(inputFrame)
        if self.invert == 1:
            processedFrame = cv2.bitwise_not(processedFrame)
        height, width = processedFrame.shape
        bytesPerLine = 1 * width
        qImg = QImage(processedFrame.data, width, height, bytesPerLine, QImage.Format_Grayscale8)
        self.processedFrameReady.emit(QPixmap(qImg))

        if self.invert == 1:
            bw_values = [[1 for j in range(0, 128)] for i in range(0, 64)]
        else:
            bw_values = [[0 for j in range(0, 128)] for i in range(0, 64)]
        for i in range(0, 64):
            for j in range(0, 128):
                c = qImg.pixel(j, i)
                colors = QtGui.QColor(c).getRgb()
                if self.invert == 1:
                    if colors[0] != 255:
                        bw_values[i][j] = 0
                else:
                    if colors[0] != 0:
                        bw_values[i][j] = 1
        try:
            if self.streamChecked:
                self.writeToMCU(bw_values)
        except Exception as e:
            print(e)

    def processFrame(self, f):
        if self.lowerRAMUsage is False:
            height, width, channel = f.shape
            resized = cv2.resize(f, None, fx=128.0 / width, fy=64.0 / height)
            gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        else:
            gray = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
        processed = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                          cv2.THRESH_BINARY, self.BLOCK_SIZE, self.THRESHOLDING_CONSTANT)
        return processed

    def play(self):
        while self.playFlag is True:
            self.updateSlider.emit(self.currentFrame)
            if self.currentFrame == self.totFrames - 1:
                break
            cv2.waitKey(self.delay)

    def sliderChangeCallback(self, frame_number):
        self.currentFrame = frame_number + 1
        self.emitRawFrame(self.frames[self.currentFrame - 2])
        self.emitProcessedFrame(self.frames[self.currentFrame - 2])

    def sliderReleasedCallback(self):
        self.playFlag = False
        pass

    def updateBlockSize(self, size):
        if size % 2 == 0:
            pass
        else:
            self.BLOCK_SIZE = size
            self.updateBS.emit(size)

    def updateC(self, value):
        self.THRESHOLDING_CONSTANT = value
        self.updateConstant.emit(value)

    def writeToMCU(self, bw_values):
        bytesToSend = []
        try:
            for row in range(1, 9):
                for column in range(1, 129):
                    bitstring = ''
                    for line in range(1, 9):
                        bitstring = bitstring + str(bw_values[(row * 8) - line][column - 1])
                    bytesToSend.append((int(bitstring, 2)))
            for x in range(0, 128):
                for byt in bytesToSend[x * 64:(x + 1) * 64]:
                    self.ser.write(byt.to_bytes(1, byteorder='big'))
        except Exception as e:
            self.errorSignal.emit(e)

    def __exit__(self):
        self.video.cleanup()
