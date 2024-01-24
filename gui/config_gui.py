import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QCheckBox, QScrollArea, QPushButton
from PyQt5.QtCore import Qt
import json

class EffectsApp(QWidget):
    def __init__(self):
        super().__init__()

        with open('effects_list.json', 'r') as file:
            effects_data = json.load(file)

        layout = QVBoxLayout()

        effects_widget = QWidget()
        effects_layout = QVBoxLayout(effects_widget)
        effects_widget.setVisible(False)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setHorizontalScrollBarPolicy(0) 
        toggle_checkbox = QCheckBox("Show/Hide effects")
        toggle_checkbox.setChecked(False)
        toggle_checkbox.stateChanged.connect(lambda state: self.toggle_effects(effects_widget, state, scroll_area))
        layout.addWidget(toggle_checkbox)

        self.effect_checkboxes = []
        for effect in effects_data:
            effect_checkbox = QCheckBox(effect['description'])
            effect_checkbox.setChecked(effect['active'])
            effects_layout.addWidget(effect_checkbox)
            self.effect_checkboxes.append(effect_checkbox)

        scroll_area.setWidget(effects_widget)

        layout.addWidget(scroll_area)
        scroll_area.hide()

        save_button = QPushButton("Save", self)
        save_button.clicked.connect(self.save)
        layout.addWidget(save_button, alignment=Qt.AlignRight | Qt.AlignBottom)
        self.setGeometry(100, 100, 500, 300)

        self.setLayout(layout)

        self.setWindowTitle('Effects')
        self.show()

    def toggle_effects(self, effects_widget, state, scroll_data):
        effects_widget.setVisible(state == 2)
        scroll_data.show()

    def save(self):
        with open('effects_list.json', 'r') as file:
            effects_list = json.load(file)

        for checkbox, effect_data in zip(self.effect_checkboxes, effects_list):
            effect_data["active"] = int(checkbox.isChecked())

        with open('effects_list.json', 'w') as file:
            json.dump(effects_list, file, indent=2)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = EffectsApp()
    sys.exit(app.exec_())
