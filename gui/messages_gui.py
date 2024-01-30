from PySide6.QtWidgets import QMessageBox
class MessageHandler():
    def show_message(message):
        msg = QMessageBox()
        # msg.setIcon(QMessageBox.Critical)
        msg.setText(message)
        msg.setWindowTitle("Message")
        msg.exec()
    def show_error_message(error_message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(error_message)
        msg.setWindowTitle("Error")
        msg.exec()