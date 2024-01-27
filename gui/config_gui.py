import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QCheckBox, QScrollArea, QPushButton, QHBoxLayout, QDialog, QLineEdit, QLabel
from PySide6.QtCore import Qt
import json
from functools import partial
class Effect_settings(QWidget):
    def __init__(self, data_dict):
        super().__init__()

        with open("resources/default_effects.json", "r") as default_file:
            default_data = json.load(default_file)
        for i in range(len(default_data)):
            if(default_data[i]['name']==data_dict['name']):
                default_data=default_data[i]
                break
            
        self.name_edit = QLineEdit()
        self.description_edit = QLineEdit()
        self.sleep_time_edit = QLineEdit()
        self.active_edit = QLineEdit()
        self.chance_edit = QLineEdit()
        self.save_button = QPushButton("Save")

        self.setup_ui(default_data)
        self.update_data(data_dict)

    def setup_ui(self, default_data):
        print(default_data)
        layout = QVBoxLayout(self)
        layout.addWidget(self.create_labeled_edit("Description:", self.description_edit, f"Def: {default_data['description']}", ''))
        layout.addWidget(self.create_labeled_edit("Sleep Time:", self.sleep_time_edit, f"Def: {default_data['sleep_time']}", ''))
        layout.addWidget(self.create_labeled_edit("Chance:", self.chance_edit, f"Def: {default_data['chance']}", ''))

        layout.addWidget(self.save_button)
        self.save_button.clicked.connect(self.save_data)

    def create_labeled_edit(self, label_text, line_edit, message_text, default_value):
        widget = QWidget()
        h_layout = QHBoxLayout(widget)

        label = QLabel(label_text)
        h_layout.addWidget(label)

        line_edit.setText(default_value)
        h_layout.addWidget(line_edit)

        message_label = QLabel(message_text)
        h_layout.addWidget(message_label)

        return widget

    def update_data(self, data_dict):
        self.name_edit.setText(data_dict['name'])
        self.description_edit.setText(data_dict['description'])
        self.sleep_time_edit.setText(str(data_dict['sleep_time']))
        self.active_edit.setText(str(data_dict['active']))
        self.chance_edit.setText(str(data_dict['chance']))

    def save_data(self):
        with open("resources/effects_list.json", "r") as file:
            current_data = json.load(file)

        for item in current_data:
            if item['name'] == self.name_edit.text():
                item.update({
                    "name": item['name'],
                    "description": self.description_edit.text(),
                    "sleep_time": int(self.sleep_time_edit.text()),
                    "active": item['active'],
                    "chance": int(self.chance_edit.text())
                })
                break

        with open("resources/effects_list.json", "w") as file:
            json.dump(current_data, file, indent=2)
        self.close()

class EffectsApp(QWidget):
    def __init__(self):
        super().__init__()

        with open('resources/effects_list.json', 'r') as file:
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
        toggle_checkbox.stateChanged.connect(lambda state: self.toggle_effects(effects_widget, state, scroll_area))
        layout.addWidget(toggle_checkbox)

        self.effect_checkboxes = []
        for effect in effects_data:
            effect_layout = QHBoxLayout()
            effect_checkbox = QCheckBox(effect['description'])
            effect_checkbox.setChecked(effect['active'])
            effect_layout.addWidget(effect_checkbox)
            effect_button = QPushButton("Open")
            effect_button.clicked.connect(partial(self.open_new_window, effect))

            effect_layout.addWidget(effect_button)
            effects_layout.addLayout(effect_layout)
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
        with open('resources/effects_list.json', 'r') as file:
            effects_list = json.load(file)

        for checkbox, effect_data in zip(self.effect_checkboxes, effects_list):
            effect_data["active"] = int(checkbox.isChecked())

        with open('resources/effects_list.json', 'w') as file:
            json.dump(effects_list, file, indent=2)

    def open_new_window(self, effect_data):
        self.new_window = Effect_settings(effect_data)
        self.new_window.show()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = EffectsApp()
    sys.exit(app.exec())
