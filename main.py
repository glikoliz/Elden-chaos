import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFrame,
    QMainWindow,
    QDesktopWidget,
    
)
from PyQt5.QtCore import QRect, Qt, QThread, QTimer, QPropertyAnimation, QUrl
from PyQt5.QtGui import QDesktopServices
import pymem
import threading
from lib.getaddress import get_random_func
from dbg.test_gui import EffectsApp

pm = None


class OverlayController(QThread):
    def __init__(self, overlay):
        super().__init__()
        self.overlay = overlay
        self.queue = ["", "", ""]
        self.i = 0

    def run(self):
        global pm

        if pm:
            func, name = get_random_func(self.i)
            self.i += 1
            threading.Thread(target=func).start()
            self.queue.pop(0)
            self.queue.append(name)
            self.overlay.changeText(self.queue)
        else:
            print("Couldn't find eldenring.exe")
        QTimer.singleShot(0, self.overlay.start_animation)

    def stop_overlay(self):
        self.i = 0
        self.overlay.hide()
        self.overlay.frame.resize(0, 0)
        self.overlay.animation_object.stop()


class Overlay(QWidget):
    def __init__(self, overlay_controller):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet(
            """
            QWidget {
                font-size: 30px;
            }
            QLabel {
                color: white;
            }
        """
        )

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.overlay_controller = overlay_controller
        self.frame = QFrame(self)
        self.frame.setStyleSheet("background-color: red;")
        self.frame.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.frame.move(0, 0)
        self.frame.resize(1920, 20)

        self.label1 = QLabel("", self)
        self.label2 = QLabel("", self)
        self.label3 = QLabel("", self)

    def changeText(self, que):
        screen = QDesktopWidget().screenGeometry()
        self.label1.setText(que[0])
        self.label2.setText(que[1])
        self.label3.setText(que[2])
        label_width1 = self.label1.fontMetrics().width(self.label1.text())
        label_width2 = self.label2.fontMetrics().width(self.label2.text())
        label_width3 = self.label3.fontMetrics().width(self.label3.text())
        self.label1.setGeometry(
            screen.width() - label_width1, self.frame.y() + 30, label_width1, 35
        )
        self.label2.setGeometry(
            screen.width() - label_width2, self.label1.y() + 40, label_width2, 35
        )
        self.label3.setGeometry(
            screen.width() - label_width3, self.label2.y() + 40, label_width3, 35
        )
        self.layout.setAlignment(Qt.AlignTop | Qt.AlignRight)

    def start_animation(self):
        self.animation_object = QPropertyAnimation(self.frame, b"geometry")
        self.animation_object.setDuration(15000)  # ms
        self.animation_object.finished.connect(self.animation_finished)
        self.animation_object.setStartValue(QRect(0, 0, 0, 20))
        self.animation_object.setEndValue(
            QRect(
                0,
                0,
                QApplication.desktop().screenGeometry().width(),
                QApplication.desktop().screenGeometry().height() // 50,
            )
        )
        self.animation_object.start()

    def animation_finished(self):
        print("Animation finished")
        if not self.isHidden():
            self.overlay_controller.run()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.overlay_controller = OverlayController(None)
        self.overlay = Overlay(self.overlay_controller)

        self.button_start = QPushButton("Start mod(start the game first)", self)
        self.button_stop = QPushButton("Stop mod and hide overlay", self)

        self.label1 = QLabel("", self)
        self.label1.setStyleSheet(
            """
            color: green;
            font-weight: bold;
            padding: 5px;
        """
        )

        layout = QVBoxLayout(self)
        layout.addWidget(self.button_start)
        layout.addWidget(self.button_stop)
        layout.addWidget(self.label1)

        self.button_start.clicked.connect(self.show_overlay)
        self.button_stop.clicked.connect(self.overlay_controller.stop_overlay)

    def show_overlay(self):
        global pm

        try:
            pm = pymem.Pymem("eldenring.exe")
            self.label1.setText("")
            self.overlay_controller.overlay = self.overlay
            if not self.overlay.isVisible() or self.overlay.isHidden():
                self.overlay.showFullScreen()
                self.overlay.setHidden(False)
                self.overlay_controller.run()
        except:
            self.label1.setText("Couldn't find eldenring.exe")


class MainAppWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.widget1 = MainWindow()
        self.widget2 = EffectsApp()
        self.btn_widget1 = QPushButton("Start Mod")
        self.btn_widget2 = QPushButton("Config")

        self.widget3 = QWidget()
        self.btn_widget3 = QPushButton("Other")
        self.btn_widget3.clicked.connect(self.showWidget3)
        self.setupWidget3()

        self.btn_widget1.clicked.connect(self.showWidget1)
        self.btn_widget2.clicked.connect(self.showWidget2)
        self.btn_widget3.clicked.connect(self.showWidget3)

        self.setGeometry(100, 100, 500, 300)

        widgets_layout = QVBoxLayout()
        widgets_layout.addWidget(self.widget1)
        widgets_layout.addWidget(self.widget2)
        widgets_layout.addWidget(self.widget3)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.btn_widget1)
        buttons_layout.addWidget(self.btn_widget2)
        buttons_layout.addWidget(self.btn_widget3)

        buttons_layout.setSpacing(0)

        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)
        central_layout.addLayout(buttons_layout)
        central_layout.addLayout(widgets_layout)

        self.setCentralWidget(central_widget)
        self.setWindowTitle("Main window")

        self.widget2.hide()
        self.widget3.hide()

    def showWidget1(self):
        self.widget1.show()
        self.widget2.hide()
        self.widget3.hide()

    def showWidget2(self):
        self.widget1.hide()
        self.widget2.show()
        self.widget3.hide()

    def showWidget3(self):
        self.widget1.hide()
        self.widget2.hide()
        self.widget3.show()
    def setupWidget3(self):
        self.layout_widget3 = QVBoxLayout(self.widget3)
        
        layout_button_description = QHBoxLayout()

        description_label = QLabel("GitHub Repository:", self.widget3)
        layout_button_description.addWidget(description_label)

        self.btn_github = QPushButton("GitHub Repository", self.widget3)
        self.btn_github.clicked.connect(self.openGitHub)
        layout_button_description.addWidget(self.btn_github)

        self.layout_widget3.addLayout(layout_button_description)
    def openGitHub(self):
        github_url = QUrl("https://github.com/glikoliz/Elden-chaos")
        QDesktopServices.openUrl(github_url)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_app_window = MainAppWindow()
    main_app_window.show()
    sys.exit(app.exec_())
