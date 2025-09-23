from datetime import datetime
import os, glob

LogPath = "D:\OQA\Log"
sn = "0000000000000000000000"

now = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
serial_log_path = os.path.join(LogPath, f"{sn}_{now}")
os.makedirs(serial_log_path)

def find_result_files():
    now = datetime.now().strftime("%b%d%Y")
    pattern_base = "D:\\OQA\\Log\\0000000000000000000000_*_Sep222025_"
    print(pattern_base + "*.jpeg")

    jpeg_files = glob.glob(pattern_base + "*.jpeg")
    print(jpeg_files)
    latest_jpeg = max(jpeg_files, key=os.path.getmtime)
    if latest_jpeg:
        print(latest_jpeg)
        des = os.path.join(serial_log_path, os.path.basename(latest_jpeg))
        # os.replace(latest_jpeg, des)
    
    return des

path = find_result_files()
print(path)