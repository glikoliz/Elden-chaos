from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QHBoxLayout
import json
from gui.messages_gui import MessageHandler

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
        layout = QVBoxLayout(self)
        layout.addWidget(self.create_labeled_edit("Description:", self.description_edit, f"Default: {default_data['description']}", ''))
        layout.addWidget(self.create_labeled_edit("Sleep Time:", self.sleep_time_edit, f"Default: {default_data['sleep_time']}", ''))
        layout.addWidget(self.create_labeled_edit("Chance:", self.chance_edit, f"Default: {default_data['chance']} (Range is 1-10, don't use more than that)", ''))

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
        if(int(self.chance_edit.text())>10 or int(self.chance_edit.text())<1):
            MessageHandler.show_message("Chance must be in range of 1-10")
            return
        
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