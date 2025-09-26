import cv2, time

def capture_frames_cams(mapping=(0,1,2,3), w=640, h=480, fps=30,
                        flush=5, retries=5, delay=0.02):
    frames = {}
    for logical_idx, real_idx in enumerate(mapping):
        cap = cv2.VideoCapture(real_idx, cv2.CAP_DSHOW)
        if not cap.isOpened():
            print(f"[Cam{logical_idx}] open failed @ real {real_idx}")
            frames[logical_idx] = None
            continue
        # ตั้งค่า
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,  w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
        cap.set(cv2.CAP_PROP_FPS,          fps)
        try: cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        except: pass
        try: cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        except: pass
        # flush buffer กันรูปเก่า
        for _ in range(max(1, flush)):
            cap.grab()
        # ดึงภาพล่าสุด
        ok, img = cap.retrieve()
        tries = 0
        while (not ok or img is None or img.size == 0) and tries < retries:
            time.sleep(delay)
            cap.grab()
            ok, img = cap.retrieve()
            tries += 1
        if ok and img is not None and img.size > 0:
            frames[logical_idx] = img.copy()  # copy เพื่อกัน reference เก่า
            print(f"[Cam{logical_idx}] captured")
        else:
            frames[logical_idx] = None
            print(f"[Cam{logical_idx}] capture failed")
        cap.release()
    return frames