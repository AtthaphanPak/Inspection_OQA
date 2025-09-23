import socket
import time

def send_command(IP: str, PORT: int, command: str, wait=0.1):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(3)
            s.connect((IP, PORT))
            s.sendall(command.encode("utf-8"))
            time.sleep(wait)
            return s.recv(1024).decode().strip()
    except Exception as e:
        return f"TCP Error: {e}"   

def check_IV3_connection(IP: str, PORT: int):
    try:
        response = send_command(IP, PORT, "VR\r")
        return "TCP Error" not in response
    except Exception as e:
        print("IV3 check failed:", e)
        return False

# serial = "0000000000000000000000"
# HOST_IP = "169.254.148.225"
# PORT = 8500
# response = send_command(HOST_IP, PORT, f'FNW,1,0,{serial}\r')
# # response = send_command(HOST_IP, PORT, f'FNW,1,0,{serial}\r')
# print(response)
# response = send_command(HOST_IP, PORT, 'T2\r')

# print(response)