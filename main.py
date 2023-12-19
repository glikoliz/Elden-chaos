import sys
from PyQt5.QtWidgets import QApplication, QWidget, QFrame, QVBoxLayout, QLabel, QDesktopWidget, QPushButton
from PyQt5.QtCore import QRect, QPropertyAnimation, Qt, QThread, QObject, QTimer
import keyboard
from time import sleep
class AnimationController(QObject):
    def __init__(self, myApp):
        super().__init__()
        self.myApp = myApp

    def run(self):
        i = 0
        ok = ["One", "Two", "Threedasdssadsdasdadsasdasadsdasd", "Four", "Five", "Six"]
        queue = ["", "", ""]
        queue.append(ok[i])
        queue.pop(0)
        i += 1
        while True:
            if keyboard.is_pressed("["):
                queue.pop(0)
                queue.append(ok[i])
                self.myApp.changeText(queue)
                i += 1
                QTimer.singleShot(0, self.myApp.start_animation)
                sleep(1)
class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet('''
            QWidget {
                font-size: 30px;
            }
            QLabel {
                color: white;
            }
        ''')        

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.frame = QFrame(self)
        self.frame.setStyleSheet('background-color: red;')
        self.frame.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.frame.move(0, 0)
        self.frame.resize(10, 20)

        self.label1 = QLabel("", self)
        self.label2 = QLabel("", self)
        self.label3 = QLabel("", self)

        self.animation_object = QPropertyAnimation(self.frame, b'geometry')
        self.animation_object.setDuration(5000)  # ms
        self.animation_object.finished.connect(self.animation_finished)
        self.animation_object.setStartValue(QRect(0, 0, 0, 20))
        self.animation_object.setEndValue(QRect(0, 0, 1920, 20))


    def changeText(self, que):
        screen = QDesktopWidget().screenGeometry()
        self.label1.setText(que[0])
        self.label2.setText(que[1])
        self.label3.setText(que[2])
        label_width1=self.label1.fontMetrics().width(self.label1.text())
        label_width2=self.label2.fontMetrics().width(self.label2.text())
        label_width3=self.label3.fontMetrics().width(self.label3.text())
        self.label1.setGeometry(screen.width() - label_width1, self.frame.y() + 30, label_width1, 30)
        self.label2.setGeometry(screen.width() - label_width2, self.label1.y() + 40, label_width2, 30)
        self.label3.setGeometry(screen.width() - label_width3, self.label2.y() + 40, label_width3, 30)
        self.layout.setAlignment(Qt.AlignTop | Qt.AlignRight)
    
    def start_animation(self):
        self.animation_object.start()

    def animation_finished(self):
        print("Animation finished")
        self.start_animation()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    myApp = MyApp()
    myApp.showFullScreen()
    controller = AnimationController(myApp)
    thread = QThread()
    controller.moveToThread(thread)
    thread.started.connect(controller.run)
    thread.start()
    sys.exit(app.exec_())

