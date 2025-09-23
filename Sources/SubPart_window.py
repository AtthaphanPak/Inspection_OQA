# import os
# import sys
from PyQt6 import uic
from PyQt6.QtWidgets import QDialog, QApplication
from CloseEvent import ConfirmCloseMixin
from fitsdll import fn_Query

class SubPartWindow(QDialog):
    def __init__(self, serial, mode):
        self.sn = serial
        self.mode = mode
        super().__init__()
        uic.loadUi("C:\Projects\Inspection_OQA\Sources\GUI\Sub-Part_window.ui", self)
        self.XCVR.setFocus()
        self.XCVR.returnPressed.connect(self.PCBA.setFocus)
        self.PCBA.returnPressed.connect(self.Poly_Sensor.setFocus)
        self.Poly_Sensor.returnPressed.connect(self.Poly_MES.setFocus)
        self.Poly_MES.returnPressed.connect(self.Fold.setFocus)
        self.Fold.returnPressed.connect(self.LATM.setFocus)
        # self.LATM.returnPressed.connect(self.StartButton.click)

        self.StartButton.clicked.connect(self.Start_clicked)
        self.LogoutButton.clicked.connect(self.logout)
        print("SubPartWindow")
        
    def Start_clicked(self):
        print("Start_clicked")
        self.sub_serial = {}
        if self.mode == "PRODUCTION":
            if fn_Query("SCANNER", "S200A", self.sn, "SN  XCVR") == self.XCVR.text():
                self.sub_serial["SN  XCVR"] = self.XCVR.text()
            else:
                self.Error_label.setStyleSheet("color: red;")
                self.Error_label.setText("SN XCVR not correct")
                self.XCVR.setText("")
                return
            
            if fn_Query("SCANNER", "S200A", self.sn, "SN PCBA") == self.PCBA.text():
                self.sub_serial["SN PCBA"] = self.PCBA.text()
            else:
                self.Error_label.setStyleSheet("color: red;")
                self.Error_label.setText("SN PCBA not correct")
                self.PCBA.setText("")
                return

            if fn_Query("SCANNER", "S200A", self.sn, "SN Polygon sensor") == self.Poly_Sensor.text():
                self.sub_serial["SN Polygon sensor"] = self.Poly_Sensor.text()
            else:
                self.Error_label.setStyleSheet("color: red;")
                self.Error_label.setText("SN Polygon sensor not correct")
                self.Poly_Sensor.setText("")
                return

            if fn_Query("SCANNER", "S300A", self.sn, "SN Polygon (MES Barcode)") == self.Poly_MES.text():
                self.sub_serial["SN Polygon (MES Barcode)"] = self.Poly_MES.text()
            else:
                self.Error_label.setStyleSheet("color: red;")
                self.Error_label.setText("SN Polygon (MES Barcode) not correct")
                self.Poly_MES.setText("")
                return

            if fn_Query("SCANNER", "S400A", self.sn, "SN Fold Mirror") == self.Fold.text():       
                self.sub_serial["SN Fold Mirror"] = self.Fold.text()
            else:
                self.Error_label.setStyleSheet("color: red;")
                self.Error_label.setText("SN Fold Mirror not correct")
                self.Fold.setText("")
                return

            if fn_Query("SCANNER", "S400A", self.sn, "SN LATM") == self.LATM.text():
                self.sub_serial["SN LATM"] = self.LATM.text()
            else:
                self.Error_label.setStyleSheet("color: red;")
                self.Error_label.setText("SN LATM not correct")
                self.LATM.setText("")
                return
        else:
            self.sub_serial["SN  XCVR"] = self.XCVR.text()
            self.sub_serial["SN PCBA"] = self.PCBA.text()
            self.sub_serial["SN Polygon sensor"] = self.Poly_Sensor.text()
            self.sub_serial["SN Polygon (MES Barcode)"] = self.Poly_MES.text()
            self.sub_serial["SN Fold Mirror"] = self.Fold.text()
            self.sub_serial["SN LATM"] = self.LATM.text()
            
        # print(self.sub_serial)
        self.accept()
    
    def logout(self):
        self.sub_serial = "LOGOUT"
        self.accept()
        
    def closeEvent(self, event):
        return event.ignore()
    
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     main_window = SubPartWindow("Serial")
#     main_window.showFullScreen()
#     sys.exit(app.exec())