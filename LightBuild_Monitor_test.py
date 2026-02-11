import ctypes
import time

# 윈도우 API 구조체 정의
class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]

def get_idle_time():
    """윈도우가 인식하는 '마지막 입력 후 지난 시간(ms)'을 가져옵니다."""
    lii = LASTINPUTINFO()
    lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
    ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii))
    
    millis = ctypes.windll.kernel32.GetTickCount() - lii.dwTime
    return millis

def send_fake_input():
    """가짜 마우스 신호 전송"""
    # 마우스 이동 (상대 좌표 1픽셀)
    ctypes.windll.user32.mouse_event(0x0001, 1, 0, 0, 0)

print("--- 진단 시작 ---")
print("3초간 마우스와 키보드에서 손을 떼세요...")
time.sleep(3) 

before_input = get_idle_time()
print(f"1. 가짜 신호 전송 전 대기 시간: {before_input}ms")

print(">> 파이썬으로 가짜 신호 발사!")
send_fake_input()
time.sleep(0.1) # 신호 처리 대기

after_input = get_idle_time()
print(f"2. 가짜 신호 전송 후 대기 시간: {after_input}ms")

print("-" * 30)

# 결과 분석
if after_input < 100:
    print("결과: [OS 통과] 윈도우는 속았습니다.")
    print("해석: 윈도우 시간은 0으로 초기화되었습니다.")
    print("      그런데도 온타임에 걸렸다면, 온타임이 'LLKHF_INJECTED' 플래그를 체크해서 무시하는 것입니다.")
else:
    print("결과: [OS 차단] 윈도우가 신호를 무시했습니다.")
    print("해석: 보안 프로그램이 아주 강력해서 파이썬의 신호 자체를 차단하고 있습니다.")