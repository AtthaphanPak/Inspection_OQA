from PyQt6.QtWidgets import QMessageBox, QApplication

class ConfirmCloseMixin():
    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, 
            "Exit Confirmation",
            "Are you sure you want to exit the program?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            QApplication.quit()
        else:
            event.ignore()