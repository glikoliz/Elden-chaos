import sys
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFrame,
    QMainWindow,
    QMessageBox,
)
from PySide6.QtCore import QRect, Qt, QThread, QTimer, QPropertyAnimation, QUrl
from PySide6.QtGui import QDesktopServices
from pymem import Pymem
import threading
import re
from lib.getaddress import get_random_func, get_dbg_func
from gui.config_gui import EffectsApp

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
            func, name, time = get_dbg_func(self.i)
            func, name, time = get_random_func()
            self.i += 1
            threading.Thread(target=func, args=(time,)).start()
            self.queue.pop(0)
            self.queue.append(name)
            self.overlay.changeText(self.queue)
        else:
            print("Couldn't find eldenring.exe")

        QTimer.singleShot(0, self.overlay.start_animation)

    def stop_overlay(self):
        if self.overlay:
            self.i = 0
            self.overlay.hide()
            self.overlay.frame.resize(0, 0)
            self.overlay.animation_object.stop()


class Overlay(QWidget):
    def __init__(self, overlay_controller):
        super().__init__()
        # print(self.screen())
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
        self.frame.resize(self.screen().size().width(), 20)

        self.label1 = QLabel("", self)
        self.label2 = QLabel("", self)
        self.label3 = QLabel("", self)

    def changeText(self, que):
        screen = self.screen().size().width()
        self.label1.setText(que[0])
        self.label2.setText(que[1])
        self.label3.setText(que[2])
        label_width1 = self.label1.fontMetrics().horizontalAdvance(self.label1.text())
        label_width2 = self.label2.fontMetrics().horizontalAdvance(self.label2.text())
        label_width3 = self.label3.fontMetrics().horizontalAdvance(self.label3.text())
        self.label1.setGeometry(
            screen - label_width1, self.frame.y() + 30, label_width1, 35
        )
        self.label2.setGeometry(
            screen - label_width2, self.label1.y() + 40, label_width2, 35
        )
        self.label3.setGeometry(
            screen - label_width3, self.label2.y() + 40, label_width3, 35
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
                self.screen().size().width(),
                self.screen().size().height() // 50,
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
            pm = Pymem("eldenring.exe")
        except:
            show_error("Couldn't find eldenring.exe\nLoad to the game and then start")
            return
        if get_errors(pm) == -1:
            return
        self.label1.setText("")
        self.overlay_controller.overlay = self.overlay
        if not self.overlay.isVisible() or self.overlay.isHidden():
            self.overlay.showFullScreen()
            self.overlay.setHidden(False)
            self.overlay_controller.run()

            # self.label1.setText("Couldn't find eldenring.exe")


class MainAppWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.widget_main = MainWindow()
        self.widget_config = EffectsApp()
        self.btn_widget1 = QPushButton("Start Mod")
        self.btn_widget2 = QPushButton("Config")

        self.widget_other = QWidget()
        self.btn_widget3 = QPushButton("Other")
        self.btn_widget3.clicked.connect(self.showWidget3)
        self.setupWidget3()

        self.btn_widget1.clicked.connect(self.showWidget1)
        self.btn_widget2.clicked.connect(self.showWidget2)
        self.btn_widget3.clicked.connect(self.showWidget3)

        self.setGeometry(100, 100, 500, 300)

        widgets_layout = QVBoxLayout()
        widgets_layout.addWidget(self.widget_main)
        widgets_layout.addWidget(self.widget_config)
        widgets_layout.addWidget(self.widget_other)

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

        self.widget_config.hide()
        self.widget_other.hide()

    def showWidget1(self):
        self.widget_main.show()
        self.widget_config.hide()
        self.widget_other.hide()

    def showWidget2(self):
        self.widget_main.hide()
        self.widget_config.show()
        self.widget_other.hide()

    def showWidget3(self):
        self.widget_main.hide()
        self.widget_config.hide()
        self.widget_other.show()

    def setupWidget3(self):
        self.layout_widget3 = QVBoxLayout(self.widget_other)

        layout_button_description = QHBoxLayout()

        description_label = QLabel("GitHub Repository:", self.widget_other)
        layout_button_description.addWidget(description_label)

        self.btn_github = QPushButton("GitHub Repository", self.widget_other)
        self.btn_github.clicked.connect(self.openGitHub)
        layout_button_description.addWidget(self.btn_github)

        self.layout_widget3.addLayout(layout_button_description)

    def openGitHub(self):
        github_url = QUrl("https://github.com/glikoliz/Elden-chaos")
        QDesktopServices.openUrl(github_url)


def show_error(error_message):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText(error_message)
    msg.setWindowTitle("Error")
    msg.exec()
    # sys.exit(app.exec())


def get_errors(pm):  # TODO:make a checkbox to disable this function
    try:
        import psutil

        for proc in psutil.process_iter():
            if proc.name() == "EasyAntiCheat_EOS.exe":
                show_error("EAC isn't disabled")
                return -1
    except:
        pass
    try:
        current_version = pm.read_string(pm.base_address + 0x2B76F64, 9).split("#")[0]
        mod_version = "1.10.1"
        if current_version != mod_version:
            show_error(
                f"Wrong version. Your game version is {current_version}, mod version is for {mod_version}"
            )
            return -1
    except:
        pass
    return 0


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_app_window = MainAppWindow()
    main_app_window.show()
    sys.exit(app.exec())
