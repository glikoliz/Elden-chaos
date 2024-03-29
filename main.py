from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFrame,
    QMainWindow,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsRectItem,

)
from PySide6.QtCore import QRect, Qt, QThread, QTimer, QPropertyAnimation, QUrl, Signal, Slot
from PySide6.QtGui import QDesktopServices, QBrush, QPen, QColor

import sys
from threading import Thread
from pymem import Pymem
from time import sleep, time

from lib.getaddress import get_random_func, get_dbg_func
from gui.config_gui import EffectsApp
from gui.messages_gui import MessageHandler
from lib.funcs import Funcs

CHAOS_TIMER_MS = 30000


class OverlayController(QThread):
    updateSignal = Signal(list, int, int)

    def __init__(self, overlay):
        super().__init__()
        self.overlay = overlay
        self.queue = ["", "", ""]
        self.i = 6

    def run(self):
        try:
            Pymem('eldenring.exe')
        except:
            MessageHandler.show_error_message("Couldn't find eldenring.exe")
            return
        self.i += 1
        effect_class, effect_name, effect_time = get_dbg_func(self.i)
        # effect_class, effect_name, effect_time = get_random_func()
        # while effect_name in self.queue:
        #     effect_class, effect_name, effect_time = get_random_func()
            
        Thread(target=self.start_effect, args=(
            effect_class, effect_name, effect_time, self.i+2)).start()
        self.queue.pop(0)
        self.queue.append(effect_name)
        if effect_time==0:
            self.updateSignal.emit(self.queue, 0, 2)
        else:
            self.updateSignal.emit(self.queue, 100, 2)
            
        QTimer.singleShot(0, self.overlay.start_animation)

    def start_effect(self, effect_class, effect_name, effect_time, ok):
        funcs = Funcs()
        while funcs.is_player_in_cutscene():
            sleep(0.5)
        counter = 0
        effect = effect_class()
        effect.onStart()
        self.overlay.change_text(self.queue)
        if effect_time == 0:
            while effect.onTick() != -1:
                counter += 1
                if (counter >= 120):
                    break
                sleep(1)
        else:
            start = time()
            i = time()-start
            while i < effect_time:
                if funcs.is_player_in_cutscene():
                    while funcs.is_player_in_cutscene():
                        sleep(0.5)
                    start=time()-i
                    pass
                effect.onTick()
                self.updateSignal.emit(self.queue, 100-(i/effect_time)*100, ok-self.i)
                sleep(0.5)
                i = time()-start
        
        self.updateSignal.emit(self.queue, 0, ok-self.i)
        self.queue[ok-self.i] = effect_name
        effect.onStop()

    def stop_overlay(self):
        if self.overlay:
            self.overlay.hide()
            self.overlay.frame.resize(0, 0)
            self.overlay.animation_object.stop()


class Overlay(QWidget):
    def __init__(self, overlay_controller):
        super().__init__()
        self.setGeometry(0, 0, self.screen().size().width(),
                         self.screen().size().height())
        self.overlay_controller = overlay_controller
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

        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene, self)
        self.view.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy(Qt.ScrollBarAlwaysOff))
        self.view.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy(Qt.ScrollBarAlwaysOff))
        self.view.setFrameStyle(QFrame.NoFrame)

        self.view.setAttribute(Qt.WA_TranslucentBackground)
        self.view.setStyleSheet("background: transparent;")

        self.frame = QFrame(self)
        self.frame.setStyleSheet("background-color: red;")
        self.frame.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.frame.move(0, 0)
        self.frame.resize(self.screen().size().width(),
                          self.screen().size().height()//50)

        self.labels = [QLabel(self), QLabel(self), QLabel(self)]
        self.rects = [
            self.scene.addRect(0, 0, 70, 0, QPen(
                Qt.NoPen), QBrush(QColor("green"))),
            self.scene.addRect(0, 0, 70, 0, QPen(
                Qt.NoPen), QBrush(QColor("green"))),
            self.scene.addRect(0, 0, 70, 0, QPen(Qt.NoPen), QBrush(QColor("green")))]
        self.gray_rects = [
            QGraphicsRectItem(), QGraphicsRectItem(), QGraphicsRectItem()]
        self.scene.addItem(self.gray_rects[0])
        self.scene.addItem(self.gray_rects[1])
        self.scene.addItem(self.gray_rects[2])

        self.scene.setSceneRect(
            0, 0, self.screen().size().width(), self.screen().size().height())
        self.scene.setBackgroundBrush(Qt.transparent)

        # self.worker = Worker()
        self.overlay_controller.updateSignal.connect(self.set_rectangles)

    @Slot(list, int, int)
    def set_rectangles(self, queue, value, i):
        screen = self.screen().size().width()
        label_height = self.labels[0].fontMetrics().height()
        rect_width = 70
        fill_width = (value/100)*70
        gray_width = rect_width - fill_width

        if value == 0:
            self.rects[i].setRect(0, 0, 0, 0)
            self.gray_rects[i].setRect(0, 0, 0, 0)
        else:
            self.rects[i].setRect(
                screen - rect_width - 10, i*40 + self.screen().size().height()//50 + 5, fill_width, label_height - 5)
            self.gray_rects[i].setBrush(QBrush(QColor("gray")))
            self.gray_rects[i].setPen(QPen(Qt.NoPen))
            self.gray_rects[i].setRect(self.rects[i].rect().x(
            )+fill_width, self.rects[i].rect().y(), gray_width, self.rects[i].rect().height())

    def change_text(self, queue):
        screen=self.screen().size().width()
        for k in range(len(queue)):
            self.labels[k].setText(queue[k])
            self.labels[k].setGeometry(screen - self.labels[k].fontMetrics().horizontalAdvance(self.labels[k].text()) - 70 -
                        20, self.screen().size().height()//50 + 40*k, self.labels[k].fontMetrics().horizontalAdvance(self.labels[k].text()), 40)
                
    def start_animation(self):
        self.animation_object = QPropertyAnimation(self.frame, b"geometry")
        self.animation_object.setDuration(CHAOS_TIMER_MS)
        self.animation_object.finished.connect(self.animation_finished)
        self.animation_object.setStartValue(
            QRect(0, 0, 0, self.screen().size().height()//50))
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
        if not self.isHidden():
            self.overlay_controller.run()


class MainWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.overlay_controller = OverlayController(None)
        self.overlay = Overlay(self.overlay_controller)
        self.button_start = QPushButton("Start mod", self)
        self.button_stop = QPushButton("Stop mod and hide overlay", self)

        self.label1 = QLabel("", self)

        layout = QVBoxLayout(self)
        layout.addWidget(self.button_start)
        layout.addWidget(self.button_stop)
        layout.addWidget(self.label1)

        self.button_start.clicked.connect(self.show_overlay)
        self.button_stop.clicked.connect(self.overlay_controller.stop_overlay)

    def show_overlay(self):
        self.overlay_controller.overlay = self.overlay
        if not self.overlay.isVisible() or self.overlay.isHidden():
            if get_errors() == -1:
                return
            self.overlay.showFullScreen()
            self.overlay.setHidden(False)
            self.overlay_controller.run()


class MainAppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 500, 300)

        self.widget_main = MainWidget()
        self.widget_config = EffectsApp()
        self.widget_other = QWidget()
        self.btn_widget1 = QPushButton("Start Mod")
        self.btn_widget2 = QPushButton("Config")
        self.btn_widget3 = QPushButton("Other")
        self.btn_widget3.clicked.connect(self.showWidget3)
        self.setupWidget3()

        self.btn_widget1.clicked.connect(self.showWidget1)
        self.btn_widget2.clicked.connect(self.showWidget2)
        self.btn_widget3.clicked.connect(self.showWidget3)

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
        self.layout_widget3.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_button_description = QHBoxLayout()
        description_label = QLabel("GitHub Repository:", self.widget_other)
        description_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_button_description.addWidget(description_label)

        self.btn_github = QPushButton("GitHub Repository", self.widget_other)
        self.btn_github.clicked.connect(self.openGitHub)
        layout_button_description.addWidget(self.btn_github)

        self.layout_widget3.addLayout(layout_button_description)

    def openGitHub(self):
        github_url = QUrl("https://github.com/glikoliz/Elden-chaos")
        QDesktopServices.openUrl(github_url)


def get_errors():  # TODO:make a checkbox to disable this function
    try:
        pm = Pymem('eldenring.exe')
    except:
        MessageHandler.show_error_message(
            "Couldn't find eldenring.exe\nLoad to the game and then start")
        return -1
    try:
        import psutil
        for proc in psutil.process_iter():
            if proc.name() == "EasyAntiCheat_EOS.exe":
                MessageHandler.show_error_message("EAC isn't disabled")
                return -1
    except:
        pass
    try:
        current_version = pm.read_string(
            pm.base_address + 0x2B76F64, 9).split("#")[0]
        mod_version = "1.10.1"
        if current_version != mod_version:
            MessageHandler.show_error_message(
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
