import ui_videoplayer
from PyQt5 import QtCore
from PyQt5 import QtWidgets
import VideoProcess
import serial.tools.list_ports
from PyQt5.QtGui import QFont

pauseFont = QFont()
playFont = QFont()
pauseFont.setPointSize(15)
playFont.setPointSize(40)


class GUIApp(ui_videoplayer.Ui_MainWindow, QtCore.QObject):
    videoProcessRequest = QtCore.pyqtSignal(str)
    videoPlayPauseRequest = QtCore.pyqtSignal()
    file = None
    videoPlayer = None
    videoPresent = False
    workerThread = None
    playSignal = QtCore.pyqtSignal()

    def __init__(self, main_window):
        super().__init__()
        self.setupUi(main_window)
        self.videoPlayer = VideoProcess.VideoProcess()
        self.progressBar.hide()

        self.playButton.setDisabled(True)
        self.blockSizeSlider.setTickInterval(2)
        self.blockSizeSlider.setSingleStep(2)
        self.playSignal.connect(self.videoPlayer.play)
        self.videoPlayer.errorSignal.connect(self.errorSignalCallback)
        self.videoPlayer.progressBarStatus.connect(self.progressBarCallback)
        self.videoPlayer.rawFrameReady.connect(self.displayRawFrame)  # Connect your signals/slots
        self.videoPlayer.processedFrameReady.connect(self.displayProcessedFrame)
        self.videoPlayer.updateBS.connect(self.updateBlockSizeLabel)
        self.videoPlayer.setupSlider.connect(self.initSlider)
        self.videoPlayer.updateConstant.connect(self.updateCLabel)
        self.playBackSlider.sliderPressed.connect(self.sliderPressedCallback)
        self.playBackSlider.sliderReleased.connect(self.videoPlayer.sliderReleasedCallback)
        self.blockSizeSlider.valueChanged.connect(self.videoPlayer.updateBlockSize)
        self.videoPlayer.enableStream.connect(self.streamOn)
        self.videoPlayer.updateSlider.connect(self.moveSlider)
        self.fileInputButton.clicked.connect(self.BrowseFile)
        self.constantThresholdSlider.valueChanged.connect(self.videoPlayer.updateC)
        self.goToStartButton.clicked.connect(self.goToStart)
        self.playButton.clicked.connect(self.changePlayStatus)
        self.workerThread = QtCore.QThread()
        self.rawVideoLabel.setScaledContents(True)
        self.processedVideoLabel.setScaledContents(True)
        self.blockSizeLabel.setText(str(self.blockSizeSlider.value()))
        self.constantLabel.setText(str(self.constantThresholdSlider.value()))
        self.streamCheckBox.stateChanged.connect(self.checkStateCallback)
        self.comPortsListButton.clicked.connect(self.ListCOMPorts)
        self.comPortsConnectButton.clicked.connect(self.videoPlayer.connect)
        self.comPortsListBox.currentIndexChanged.connect(self.PortSelectionChanged)
        self.invertCheckBox.stateChanged.connect(self.invertCheckHandler)
        self.comPortsListBox.setDisabled(True)
        self.goToStartButton.setDisabled(True)
        self.streamCheckBox.setDisabled(True)
        self.invertCheckBox.setDisabled(True)
        self.ListCOMPorts()

    def invertCheckHandler(self):
        if self.invertCheckBox.isChecked():
            self.videoPlayer.invert = 1
        else:
            self.videoPlayer.invert = 0

    def checkStateCallback(self):
        if self.streamCheckBox.isChecked():
            self.videoPlayer.streamChecked = True
        else:
            self.videoPlayer.streamChecked = False

    def ListCOMPorts(self):
        self.videoPlayer.COMPorts = list(serial.tools.list_ports.comports())
        i = 0
        if self.videoPlayer.COMPorts is not None:
            self.comPortsListBox.setDisabled(False)
        self.comPortsListBox.clear()
        for port in self.videoPlayer.COMPorts:
            self.comPortsListBox.addItem(str(port))
            i = i+1
        self.label.setText("Found {} device(s)".format(i))
        self.PortSelectionChanged()

        if i == 0:
            self.comPortsListBox.setDisabled(True)

    def PortSelectionChanged(self):
        index = self.comPortsListBox.currentIndex()
        print(self.videoPlayer.COMPorts[index][0])
        self.videoPlayer.activePort = self.videoPlayer.COMPorts[index][0]

    def BrowseFile(self):
        self.file, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Select Video", "",
                                                                "Video files (*.mp4 *.mpeg *.mpg *.mkv)")
        if self.file:
            self.progressBar.show()
            self.initVideoThread()
            self.videoPlayer.newVideoAdded()
            self.videoPresent = True
            self.playButton.setDisabled(False)
            self.goToStartButton.setDisabled(False)
            self.fileInputButton.setDisabled(True)
            self.fileInputTextEdit.setReadOnly(True)
            self.fileInputTextEdit.setPlainText(self.file)
            self.invertCheckBox.setDisabled(False)
            self.streamCheckBox.setDisabled(False)

    def displayRawFrame(self, raw_frame):
        self.rawVideoLabel.setPixmap(raw_frame)

    def displayProcessedFrame(self, processed_frame):
        self.processedVideoLabel.setPixmap(processed_frame)

    def streamOn(self):
        self.streamCheckBox.setChecked(True)

    def progressBarCallback(self, value):
        self.progressBar.setValue(value)
        self.label.setText("Loading video...")
        if value == 100:
            self.progressBar.hide()
            self.label.setText("Video loaded successfully. ✔")

    def errorSignalCallback(self, error):
        self.label.setText(str(error))

    def initVideoThread(self):
        if self.videoPresent:
            del self.videoPlayer
            self.videoPlayer = VideoProcess.VideoProcess()
        self.videoPlayer.file = self.file
        self.videoPlayer.moveToThread(self.workerThread)
        self.workerThread.start()

    def changePlayStatus(self):
        self.videoPlayer.playFlag = not self.videoPlayer.playFlag
        self.playButton.setFont(pauseFont)
        pauseFont.setPointSize(15)

        if self.videoPlayer.playFlag:
            self.playButton.setFont(pauseFont)
            self.playButton.setText(" ▌▌")
        else:
            self.playButton.setFont(playFont)
            self.playButton.setText(" ▶ ")

        if self.videoPlayer.playFlag:
            self.playSignal.emit()

    def blockSizeChanged(self, value):
        self.blockSizeLabel.setText(str(value))

    def goToStart(self):
        self.videoPlayer.currentFrame = 1
        self.videoPlayer.emitProcessedFrame(self.videoPlayer.frames[1])
        self.videoPlayer.emitRawFrame(self.videoPlayer.frames[1])

    def sliderPressedCallback(self):
        self.videoPlayer.playFlag = False
        self.playButton.setFont(playFont)
        self.playButton.setText(" ▶ ")

    def initSlider(self, total_frames):
        self.playBackSlider.setMinimum(1)
        self.playBackSlider.setMaximum(total_frames)
        self.playBackSlider.setSliderPosition(2)
        self.playBackSlider.valueChanged.connect(self.videoPlayer.sliderChangeCallback)

    def moveSlider(self, frame_number):
        self.playBackSlider.setValue(frame_number)

    def updateBlockSizeLabel(self, size):
        self.blockSizeLabel.setText(str(size))

    def updateCLabel(self, size):
        self.constantLabel.setText(str(size))
