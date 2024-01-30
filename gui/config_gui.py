import sys
import json
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QCheckBox,
    QScrollArea,
    QPushButton,
    QHBoxLayout,
    QDialog,
    QLineEdit,
    QLabel,
    QSpacerItem,
    QSizePolicy,
    QMessageBox
)
from PySide6.QtCore import Qt
from functools import partial

from gui.settings_gui import Effect_settings
from gui.messages_gui import MessageHandler

class EffectsApp(QWidget):
    def __init__(self):
        super().__init__()

        with open("resources/effects_list.json", "r") as file:
            effects_data = json.load(file)

        layout = QVBoxLayout()

        effects_widget = QWidget()
        effects_layout = QVBoxLayout(effects_widget)
        effects_widget.setVisible(False)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        toggle_checkbox = QCheckBox("Show/Hide effects")
        toggle_checkbox.setChecked(False)
        toggle_checkbox.stateChanged.connect(
            lambda state: self.toggle_effects(effects_widget, state, scroll_area)
        )
        layout.addWidget(toggle_checkbox)

        self.effect_checkboxes = []
        for effect in effects_data:
            effect_layout = QHBoxLayout()
            effect_checkbox = QCheckBox(effect["description"])
            effect_checkbox.setChecked(effect["active"])
            effect_layout.addWidget(effect_checkbox)
            effect_button = QPushButton("Open")
            effect_button.clicked.connect(partial(self.open_new_window, effect))
            effect_layout.addWidget(effect_button)
            effects_layout.addLayout(effect_layout)
            self.effect_checkboxes.append(effect_checkbox)

        scroll_area.setWidget(effects_widget)

        layout.addWidget(scroll_area)

        horizontal_layout = QHBoxLayout()
        scroll_area.hide()

        save_button = QPushButton("Save", self)
        save_button.clicked.connect(self.save)
        default_button = QPushButton("Default settings", self)
        default_button.clicked.connect(self.default_settings_return)

        horizontal_layout.addWidget(save_button)
        horizontal_layout.addWidget(default_button)

        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer)

        layout.addLayout(horizontal_layout)

        self.setGeometry(100, 100, 500, 300)

        self.setLayout(layout)

        self.setWindowTitle("Effects")
        self.show()

    def toggle_effects(self, effects_widget, state, scroll_data):
        effects_widget.setVisible(state == 2)
        scroll_data.show()

    def save(self):
        try:
            with open("resources/effects_list.json", "r") as file:
                effects_list = json.load(file)
        except:
            MessageHandler.show_error_message("Something wrong. make sure that resources folder in the same folder as your main.exe file")
            return
        for checkbox, effect_data in zip(self.effect_checkboxes, effects_list):
            effect_data["active"] = int(checkbox.isChecked())

        with open("resources/effects_list.json", "w") as file:
            json.dump(effects_list, file, indent=2)
        MessageHandler.show_message("Your settings changed succesfully")

    def default_settings_return(self):
        try:
            with open("resources/default_effects.json", "r") as file:
                effects_list = json.load(file)
        except:
            MessageHandler.show_error_message("Something wrong. make sure that resources folder in the same folder as your main.exe file")
            return

        with open("resources/effects_list.json", "w") as file:
            json.dump(effects_list, file, indent=2)
        MessageHandler.show_message("Default settings restored succesfully")

    def open_new_window(self, effect_data):
        self.new_window = Effect_settings(effect_data)
        self.new_window.show()




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EffectsApp()
    sys.exit(app.exec())
