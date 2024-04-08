import os
import sys
import shutil
from datetime import datetime
from PySide6.QtWidgets import QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFileDialog
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from gui.messages_gui import MessageHandler

class OtherWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout_widget = QVBoxLayout(self)
        self.layout_widget.setAlignment(Qt.AlignmentFlag.AlignTop)

        git_btn_layout = QHBoxLayout()
        git_label = QLabel("GitHub Repository:", self)
        git_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        git_btn_layout.addWidget(git_label)

        self.btn_github = QPushButton("Open GitHub", self)
        self.btn_github.clicked.connect(self.open_github)
        git_btn_layout.addWidget(self.btn_github)

        self.layout_widget.addLayout(git_btn_layout)

        backup_btn_layout = QHBoxLayout()
        backup_label = QLabel("Create backup of current saves:", self)
        backup_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        backup_btn_layout.addWidget(backup_label)

        self.btn_second = QPushButton("Create backup", self)
        self.btn_second.clicked.connect(self.create_manual_backup)
        backup_btn_layout.addWidget(self.btn_second)

        self.layout_widget.addLayout(backup_btn_layout)

    def open_github(self):
        github_url = QUrl("https://github.com/glikoliz/Elden-chaos")
        QDesktopServices.openUrl(github_url)

    def create_manual_backup(self):
        appdata_path = self.get_appdata_path()

        backups_dir = os.path.join(os.getcwd(), 'backups')
        if not os.path.exists(backups_dir):
            os.makedirs(backups_dir)

        current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_dir_name = f"manual_backup_{current_datetime}"
        backup_dir_path = os.path.join(backups_dir, backup_dir_name)

        try:
            shutil.copytree(appdata_path, backup_dir_path)
            MessageHandler.show_message(f"Backup created successfully:\n{backup_dir_path}")
        except Exception as e:
            MessageHandler.show_error_message(f"An error occurred during backup creation: {str(e)}")

    def get_appdata_path(self):
        appdata_path = os.path.join(
            os.environ['USERPROFILE'], 'AppData', 'Roaming', 'EldenRing')
        while not os.path.exists(appdata_path):
            MessageHandler.show_error_message("The specified folder does not exist. Select folder with your saves")
            
            appdata_path = QFileDialog.getExistingDirectory(
                self, "Select saves folder")
        return appdata_path