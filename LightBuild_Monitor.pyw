import ctypes
import time
import random
import datetime

# 윈도우 API 상수
MOUSEEVENTF_MOVE = 0x0001
KEYEVENTF_KEYUP = 0x0002
VK_F15 = 0x7E # F15 키 코드 (작업에 방해 안 됨)

def send_input_signal():
    """
    강력한 신호 전송:
    1. 마우스를 크게 움직임 (100픽셀)
    2. F15 키를 눌렀다  뗌 (키보드 활동으로 인식)
    """
    # 1. 마우스 오른쪽으로 100픽셀 이동
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_MOVE, 100, 0, 0, 0)
    time.sleep(0.1)
    
    # 2. 마우스 왼쪽으로 100픽셀 이동 (원위치)
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_MOVE, -100, 0, 0, 0)
    time.sleep(0.1)

    # 3. F15 키 입력 (누름 -> 뗌)
    ctypes.windll.user32.keybd_event(VK_F15, 0, 0, 0)
    ctypes.windll.user32.keybd_event(VK_F15, 0, KEYEVENTF_KEYUP, 0)

def main():
    try:
        while True:
            # 60초 ~ 180초 (1분~3분) 사이 랜덤
            # *중요: 주기를 짧게 줄였습니다. 온타임 반응 속도가 빠를 수 있음
            wait_time = random.randint(60, 180)
            
            time.sleep(wait_time)
            send_input_signal()
            
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()