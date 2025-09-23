from PyQt6 import uic
from PyQt6.QtWidgets import QDialog
from CloseEvent import ConfirmCloseMixin

class LoginWindow(QDialog, ConfirmCloseMixin):
    def __init__(self):
        super().__init__()
        uic.loadUi("C:\Projects\Inspection_OQA\Sources\GUI\Login_GUI.ui", self)
        
        self.enLineEdit.setFocus()
        self.enLineEdit.returnPressed.connect(self.LoginButton.click)

        self.LoginButton.clicked.connect(self.login_clicked)
        
    def login_clicked(self):
        self.user_input = self.enLineEdit.text()
        
        if len(self.user_input) == 6:
            print(f"Welcome User {self.user_input}")
            self.accept()
        
        else:
            self.label_Error.setText("Please check your EN")
            self.label_Error.setStyleSheet("color: red;")