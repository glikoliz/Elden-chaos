import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QLabel,
    QDesktopWidget,
    QFrame,
    QMainWindow,
    QMenuBar,
    QMenu,
    QAction,
    QDialog,
)
from PyQt5.QtCore import QRect, Qt, QThread, QTimer, QPropertyAnimation
import pymem
from time import sleep, time
import random
from lib.getaddress import get_address_list, get_random_func
import effects.effects as call
import threading

pm = None


class OverlayController(QThread):
    def __init__(self, overlay):
        super().__init__()
        self.overlay = overlay
        self.queue = ["", "", ""]
        self.i = 4
        # self.run()

    def run(self):
        global pm
        # print(pm)

        if pm:
            # func, name = call.dbg_get_func(self.i)
            func, name=get_random_func(self.i)
            self.i += 1
            threading.Thread(target=func, args=(get_address_list(pm),)).start()
            # threading.Thread(target=call.WARP, args=(pm, get_final_list(pm))).start()
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
        self.animation_object.setEndValue(QRect(0, 0, 1920, 20))
        self.animation_object.start()

    def animation_finished(self):
        print("Animation finished")
        # self.start_animation()
        if not self.isHidden():
            self.overlay_controller.run()


class MainWindow(QMainWindow):
    def __init__(self):
        
        super().__init__()
        menuBar = QMenuBar(self)
        fileMenu = QMenu("&Settings", self)
        menuBar.addMenu(fileMenu)
        self.setMenuBar(menuBar)
        self.setGeometry(100, 100, 400, 200)
        self.setWindowTitle("Main Window")
        self.overlay_controller = OverlayController(None)

        self.overlay = Overlay(self.overlay_controller)

        self.button_start = QPushButton("Start mod", self)
        self.button_stop = QPushButton("Stop mod and hide overlay", self)

        self.label1 = QLabel("", self)
        self.label1.setStyleSheet(
            """
            color: green;
            font-weight: bold;
            border: 2px solid green;
            padding: 5px;
        """
        )

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        central_layout = QVBoxLayout(central_widget)
        central_layout.addWidget(self.button_start)
        central_layout.addWidget(self.button_stop)
        central_layout.addWidget(self.label1)

        self.button_start.clicked.connect(self.show_overlay)
        self.button_stop.clicked.connect(self.overlay_controller.stop_overlay)


    def show_overlay(self):
        global pm
        
        try:
            pm = pymem.Pymem("eldenring.exe")

            self.label1.setText("")
            self.overlay_controller.overlay = self.overlay
            # print(self.overlay.isHidden())
            if not self.overlay.isVisible() or self.overlay.isHidden():
                self.overlay.showFullScreen()
                self.overlay.setHidden(False)
                # self.overlay_controller.start()
                self.overlay_controller.run()
        except:
            self.label1.setText("Couldn't find eldenring.exe")




if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = MainWindow()

    main_window.show()
    

    sys.exit(app.exec_())
