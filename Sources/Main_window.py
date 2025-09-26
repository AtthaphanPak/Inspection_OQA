import os
import sys
import glob
import time
import cv2
import configparser
from PyQt6 import uic
from datetime import datetime
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QApplication, QDialog, QMainWindow, QMessageBox

from Login_window import LoginWindow
from Instructions_window import InstructionWindow
from SubPart_window import SubPartWindow
from Vision_Command import send_command
from fitsdll import Convert_Data, fn_Handshake, fn_Log, fn_Query
from usb_cam import capture_frames_cams

class MainAppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --disable-software-rasterizer"
        self.exit_confirm_enabled = True
        self.config = configparser.ConfigParser()
        pcname = os.environ['COMPUTERNAME']
        print("PCNAME:\t",pcname)
        try:
            self.config.read("C:\Projects\Inspection_OQA\Properties\Config.ini")
            self.CAM1_IP = self.config["CAMERA"].get("CAMERA_1_IP", "")
            self.CAM1_PORT = int(self.config["CAMERA"].get("CAMERA_1_PORT", ""))
            self.model = self.config["DEFAULT"].get("MODEL", "")
            self.operation = self.config["DEFAULT"].get("OPERATION", "")
            self.LogPath = self.config["DEFAULT"].get("LogPath", "")
            self.call_program = self.config["CAMERA"].get("CALL_PROGRAM", "")
            self.mode = self.config["DEFAULT"].get("mode", "")
        except Exception as e:
            QMessageBox.critical(None, "Close Program", f"{e}\nPlease check config.ini")
            self.exit_confirm_enabled = False
            quit()

        os.makedirs(self.LogPath, exist_ok=True)
        
        self.clear_log()
        
        self.en = ""
        self.sn = ""
        self.promname = ""
        self.serial_log_path = ""
        self.program_list = []
        self.program_index = 0
        self.All_Result = []
        self.Result_images = {
            "Top": None,
            "0": None,
            "1": None,
            "2": None,
            "3": None
        }

        uic.loadUi("C:\Projects\Inspection_OQA\Sources\GUI\Main_GUI.ui", self)

        self.stackedWidget.setCurrentIndex(0)

        # action Button 
        self.finishButton.clicked.connect(self.open_result)
        self.recapButton.clicked.connect(self.retries)
        self.LogoutButton.clicked.connect(self.logout)

        QTimer.singleShot(100, self.start_login_flow)

    def clear_log(self):
        self.result_image_list = []
        self.result_txt_list = []
        folder_bin = os.path.join(self.LogPath, "bin")
        os.makedirs(folder_bin, exist_ok=True)
        jpeg_files = glob.glob(os.path.join(self.LogPath, "*.jpeg"))
        txt_files = glob.glob(os.path.join(self.LogPath, "*.txt"))
        
        excess_files = jpeg_files + txt_files
        if excess_files:
            for flie in excess_files:
                os.rename(flie, os.path.join(folder_bin, os.path.basename(flie)))

    def start_login_flow(self):
        # print("LOGIN")
        self.setEnabled(False)
        self.recapButton.hide()
        self.finishButton.hide()
        self.login = LoginWindow()        
        if self.login.exec() != QDialog.DialogCode.Accepted:
            # print("CLOSE")
            self.exit_confirm_enabled = False
            QApplication.quit()
            quit() 

        self.en = self.login.user_input
            
        QTimer.singleShot(100, self.start_instruction_flow)

    def logout(self):
        # self.move_retries()
        self.clear_log()
        self.Mainlabel.setText("Waiting . . .")
        self.stackedWidget.setCurrentIndex(0)
        QTimer.singleShot(100, self.start_login_flow)

    def start_instruction_flow(self):
        print("INSTRUCTION")
        self.recapButton.hide()
        self.finishButton.hide()
        self.Instruction = InstructionWindow(self.mode, index=0)
        if self.Instruction.exec() != QDialog.DialogCode.Accepted:
            return
        self.mode = self.Instruction.mode
        
        if self.Instruction.status == "LOGOUT":
            print("LOGOUT")
            self.logout()
            return
        else:
            sn = self.Instruction.serial_value
            print(self.model)
            print(sn)
            if self.mode.upper() == "PRODUCTION":

                handshake_status = fn_Handshake(self.model, self.operation, sn)
                print(handshake_status)
                if handshake_status == True:   
                    self.sn = sn

                else: 
                    QMessageBox.critical(self, "Handcheck FAIL", f"Serial: {sn} has no test in this station.")
                    QTimer.singleShot(100, self.start_instruction_flow)
                    return
            else:
                self.sn = sn
            
            now = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
            self.serial_log_path = os.path.join(self.LogPath, f"{self.sn}_{now}")
            os.makedirs(self.serial_log_path, exist_ok=True)

            self.subserial = SubPartWindow(sn, self.mode)
            
            if self.subserial.exec() != QDialog.DialogCode.Accepted:
                return

            self.df_subpart = self.subserial.sub_serial

            if self.df_subpart == "LOGOUT":
                return self.logout()

            print(self.df_subpart)
            self.enDisplay.setText(self.en)
            self.serialDisplay.setText(self.sn)
            self.StationDisplay.setText(self.operation)
            self.ModeDisplay.setText(self.mode)
            self.All_Result = []

            QTimer.singleShot(100, self.start_trigger_flow)

    def retries(self):
        print("retries")
        for i in range(5):
            print(f"REMOVE IMG {i+1}")
            label = getattr(self, f"Img_{i+1}")
            label.clear()

        self.Result_images = {
            "Top": None,
            "0": None,
            "1": None,
            "2": None,
            "3": None
        }

        jpeg_files = glob.glob(os.path.join(self.serial_log_path,"**.jpeg"))
        print("jpeg_files:\t",jpeg_files)
        if jpeg_files:
            for file in jpeg_files:
                os.remove(file)
                print("jpeg_files remove:\t",file)
                # des = os.path.join(self.retries_path, os.path.basename(file))
                # os.replace(file, des)
            time.sleep(10)
        
        self.start_trigger_flow()

    def start_trigger_flow(self):
        self.stackedWidget.setCurrentIndex(1)
        IP = self.CAM1_IP
        PORT = self.CAM1_PORT
        
        # change program number
        send_command(IP, PORT, f'PW,00\r')
        # print("change program number")
        # Write filename
        response = send_command(IP, PORT, f'FNW,1,0,{self.sn}\r')
        print("Write filename")
        if response.split(":")[0] != "TCP Error":
            # trigger Result
            response = send_command(IP, PORT, 'T1\r')
            # print("trigger Result")
            if response.split(":")[0] != "TCP Error":
                self.setEnabled(True)

            time.sleep(3)

            IV_img = None
            for i in range(5):
                time.sleep(1)
                if IV_img == None:
                    IV_img = self.find_result_files()
                else:
                    break
            else:
                print("File not found.")

            self.Result_images["Top"] = IV_img  
            pixmap_top = QPixmap(IV_img)
            label = getattr(self, f"Img_5")
            label.setPixmap(
                    pixmap_top.scaled(
                        label.width(),
                        label.height(),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                )

            frames = capture_frames_cams()
            now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            for i in range(4):
                f = frames.get(i)
                if f is None:
                    print(f"[!] cam{i} returned None")
                    getattr(self, f"Img_{i+1}").clear()
                    continue

                fullpath = os.path.join(self.LogPath, self.serial_log_path, f"cam_USB_{i}_{now}.jpeg")
                cv2.imwrite(fullpath, f)
                self.Result_images[f"{i}"] = fullpath
                # --- show on QLabel ---
                rgb = cv2.cvtColor(f, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb.shape
                qimg = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
                pixmap = QPixmap.fromImage(qimg)

                label = getattr(self, f"Img_{i+1}")
                label.setPixmap(
                    pixmap.scaled(
                        label.width(),
                        label.height(),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                )

                self.recapButton.show()
                self.finishButton.show()

        else:
            self.setEnabled(True)
            QMessageBox.critical(self, "ERROR MESSAGE", "FAIL\ncan't communicate with camera, please contact your supervisor")
            self.exit_confirm_enabled = False
            QApplication.quit()
            
    def open_result(self):
        print("upload_result")
        self.setEnabled(False)
        # print(self.Result_images)

        fits_df = {
            "Operation": self.operation,
            "EN": self.en,
            "SN Scanner": self.sn,
            "WO#": fn_Query(self.model, "S500", self.sn, "WO#"),
            "SN  XCVR":  self.df_subpart["SN  XCVR"],
            "SN PCBA":  self.df_subpart["SN PCBA"],
            "SN Polygon sensor": self.df_subpart["SN Polygon sensor"],
            "SN Polygon (MES Barcode)": self.df_subpart["SN Polygon (MES Barcode)"],
            "SN Fold Mirror": self.df_subpart["SN Fold Mirror"],
            "SN LATM": self.df_subpart["SN LATM"],
            "Top view": self.Result_images["Top"],
            "Front view": self.Result_images["0"],
            "Back view": self.Result_images["1"],
            "Left side view": self.Result_images["2"],
            "Right side view": self.Result_images["3"],
            "Result": "PASS"
        }

        if self.mode.upper() == "PRODUCTION":
            parameters = Convert_Data(fits_df.keys())
            values = Convert_Data(fits_df.values())
            log_status = fn_Log(self.model, self.operation, parameters, values)
            if log_status == True:
                QMessageBox.information(self, "FITs success", "Success uploaded data to FITs")
            else:
                QMessageBox.critical(self, "Failed uploaded data to FITs", log_status)

        for i in range(5):
             label = getattr(self, f"Img_{i+1}")
             label.clear()  
        PassInstruction = InstructionWindow(self.mode, index=1)
        result = PassInstruction.exec()
        print("Finish")
        if result == QDialog.DialogCode.Accepted:
            print("True")
            self.start_instruction_flow()
        else:
            print("False")
            self.start_instruction_flow()

        self.setEnabled(True)

    def find_result_files(self):
        print("Find img file")
        now = datetime.now().strftime("%b%d%Y")
        pattern_base = os.path.join(self.LogPath, f"{self.sn}_*_{now}_")
        print("pattern_base:\t", pattern_base + "*.jpeg")
        
        jpeg_files = glob.glob(pattern_base + "*.jpeg")
        print(jpeg_files)
        latest_jpeg = max(jpeg_files, key=os.path.getmtime)
        if latest_jpeg:
            print(latest_jpeg)
            des = os.path.join(self.serial_log_path, os.path.basename(latest_jpeg))
            os.replace(latest_jpeg, des)
        return des

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainAppWindow()
    main_window.showFullScreen()
    sys.exit(app.exec())