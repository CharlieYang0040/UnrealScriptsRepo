import subprocess

def open_edge_in_dev_mode(url, user_agent):
    # Edge 브라우저의 전체 경로를 사용
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    
    # Edge 실행 명령어 (개발자 도구를 열도록 설정)
    command = [
        edge_path,
        "--new-window",
        "--auto-open-devtools-for-tabs",  # 개발자 도구를 자동으로 엽니다
        f"--user-agent={user_agent}",     # 사용자 에이전트를 설정
        url
    ]
    
    # Edge 실행
    subprocess.run(command, check=True)

if __name__ == "__main__":
    url = "https://rink.kakaogames.com/"
    user_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
    
    open_edge_in_dev_mode(url, user_agent)