from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QMainWindow
)
from PySide6.QtCore import QThread, QTimer, Signal

import sys
from threading import Thread
from pymem import Pymem
from time import sleep, time

from lib.getaddress import get_random_func, get_dbg_func
from lib.funcs import Funcs

from gui.config_gui import EffectsApp
from gui.messages_gui import MessageHandler
from gui.overlay_gui import Overlay
from gui.other_gui import OtherWidget

CHAOS_TIMER_MS = 30000


class OverlayController(QThread):
    updateSignal = Signal(list, int, int)

    def __init__(self, overlay):
        super().__init__()
        self.overlay = overlay
        self.queue = ["", "", "", ""]
        self.i = 6

    def run(self):
        try:
            Pymem('eldenring.exe')
        except:
            MessageHandler.show_error_message("Couldn't find eldenring.exe")
            return
        self.i += 1
        effect_class, effect_name, effect_time = get_dbg_func(self.i)

        self.queue.pop(0)
        self.queue.append(effect_name)
        if (self.i != 7):
            self.updateSignal.emit(self.queue, -1, 2)

        # effect_class, effect_name, effect_time = get_random_func()
        # while effect_name in self.queue:
        #     effect_class, effect_name, effect_time = get_random_func()

        Thread(target=self.start_effect, args=(
            effect_class, effect_name, effect_time, self.i+3)).start()

        if effect_time == 0:
            self.updateSignal.emit(self.queue, 0, 3)
        else:
            self.updateSignal.emit(self.queue, 100, 3)

        QTimer.singleShot(0, self.overlay.start_animation)

    def start_effect(self, effect_class, effect_name, effect_time, ok):
        funcs = Funcs()
        while funcs.is_player_in_cutscene():
            sleep(0.5)
        counter = 0
        # effect = effect_class()
        # effect.onStart()
        if effect_time == 0:
            # while effect.onTick() != -1:
            #     counter += 1
            #     if (counter >= 120):
            #         break
            #     sleep(1)
            pass
        else:
            start = time()
            i = time()-start
            while i < effect_time:
                if funcs.is_player_in_cutscene():
                    while funcs.is_player_in_cutscene():
                        sleep(0.5)
                    start = time()-i
                # effect.onTick()
                self.updateSignal.emit(
                    self.queue, 100-(i/effect_time)*100, ok-self.i)
                sleep(0.5)
                i = time()-start

        self.updateSignal.emit(self.queue, 0, ok-self.i)
        self.queue[ok-self.i] = effect_name
        # effect.onStop()

    def stop_overlay(self):
        if self.overlay:
            self.overlay.hide()
            self.overlay.frame.resize(0, 0)
            self.overlay.animation_object.stop()

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
        self.widget_other = OtherWidget()
        self.btn_widget1 = QPushButton("Start Mod")
        self.btn_widget2 = QPushButton("Config")
        self.btn_widget3 = QPushButton("Other")
        self.btn_widget3.clicked.connect(self.showWidget3)
        # self.setupWidget3()

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

    # def setupWidget3(self):
    #     self.layout_widget3 = QVBoxLayout(self.widget_other)
    #     self.layout_widget3.setAlignment(Qt.AlignmentFlag.AlignTop)
    #     layout_button_description = QHBoxLayout()
    #     description_label = QLabel("GitHub Repository:", self.widget_other)
    #     description_label.setAlignment(Qt.AlignmentFlag.AlignTop)
    #     layout_button_description.addWidget(description_label)

    #     self.btn_github = QPushButton("GitHub Repository", self.widget_other)
    #     self.btn_github.clicked.connect(self.openGitHub)
    #     layout_button_description.addWidget(self.btn_github)

    #     self.layout_widget3.addLayout(layout_button_description)



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
