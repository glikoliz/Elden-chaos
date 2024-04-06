from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QFrame,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsRectItem,

)
from PySide6.QtCore import QRect, Qt, QPropertyAnimation, Slot
from PySide6.QtGui import QBrush, QPen, QColor
CHAOS_TIMER_MS = 30000
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
                          self.screen().size().height() // 50)

        self.labels = [QLabel(self) for _ in range(4)]
        self.rects = [QGraphicsRectItem() for _ in range(4)]
        self.gray_rects = [QGraphicsRectItem() for _ in range(4)]

        for rect, gray_rect in zip(self.rects, self.gray_rects):
            rect.setBrush(QBrush(QColor("green")))
            rect.setPen(QPen(Qt.NoPen))
            gray_rect.setBrush(QBrush(QColor("gray")))
            gray_rect.setPen(QPen(Qt.NoPen))
            self.scene.addItem(rect)
            self.scene.addItem(gray_rect)

        self.scene.setSceneRect(
            0, 0, self.screen().size().width(), self.screen().size().height())
        self.scene.setBackgroundBrush(Qt.transparent)
        self.overlay_controller.updateSignal.connect(self.update_overlay_text)

    @Slot(list, int, int)
    def update_overlay_text(self, queue, value, i):
        screen = self.screen().size().width()
        label_height = self.labels[0].fontMetrics().height()

        if value == -1:
            for k in range(3):
                self.labels[k].setText(queue[k])
                self.labels[k].setGeometry(self.labels[k + 1].x(),
                                           self.labels[k + 1].y() - 40,
                                           self.labels[k].fontMetrics().horizontalAdvance(
                                               self.labels[k].text()),
                                           40)
                self.rects[k].setRect(self.rects[k + 1].rect().x(),
                                      self.rects[k + 1].rect().y() - 40,
                                      self.rects[k + 1].rect().width(),
                                      self.rects[k + 1].rect().height())

                self.gray_rects[k].setRect(self.gray_rects[k + 1].rect().x(),
                                           self.gray_rects[k +
                                                           1].rect().y() - 40,
                                           self.gray_rects[k +
                                                           1].rect().width(),
                                           self.gray_rects[k + 1].rect().height())
            return

        rect_width = 70
        fill_width = (value / 100) * rect_width
        gray_width = rect_width - fill_width
        x = 0

        if value == 0:
            self.rects[i].setRect(0, 0, 0, 0)
            self.gray_rects[i].setRect(0, 0, 0, 0)
        else:
            self.rects[i].setRect(screen - rect_width - 10,
                                  i * 40 + self.screen().size().height() // 50 + 5,
                                  fill_width,
                                  label_height - 5)

            self.gray_rects[i].setRect(self.rects[i].rect().x() + fill_width,
                                       self.rects[i].rect().y(),
                                       gray_width,
                                       self.rects[i].rect().height())
            x -= 70
        self.labels[i].setText(queue[i])
        x += screen - \
            self.labels[i].fontMetrics().horizontalAdvance(
                self.labels[i].text()) - 20
        self.labels[i].setGeometry(x,
                                   self.screen().size().height() // 50 + 40 * i,
                                   self.labels[i].fontMetrics().horizontalAdvance(
                                       self.labels[i].text()),
                                   40)

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
