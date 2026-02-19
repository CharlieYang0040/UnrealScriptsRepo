import os
import subprocess
import xml.etree.ElementTree as ET
import sys

def get_locks():
    """SVN 서버 상태를 조회하여 잠금 정보를 파싱합니다."""
    print("🔄 SVN 저장소 상태를 확인 중입니다... (잠시만 기다려주세요)")
    
    try:
        # 한글 윈도우 인코딩 대응 (cp949)
        cmd = 'svn status --xml -u'
        output = subprocess.check_output(cmd, shell=True).decode('cp949', errors='ignore')
    except subprocess.CalledProcessError as e:
        print(f"❌ SVN 명령 실행 실패: {e}")
        return {}

    try:
        root = ET.fromstring(output)
    except ET.ParseError:
        print("❌ XML 데이터 분석 실패.")
        return {}

    locks_by_user = {}

    for entry in root.findall('target/entry'):
        path = entry.get('path')
        repos_status = entry.find('repos-status')
        
        if repos_status is not None:
            lock = repos_status.find('lock')
            if lock is not None:
                owner = lock.find('owner').text
                if owner not in locks_by_user:
                    locks_by_user[owner] = []
                locks_by_user[owner].append(path)
    
    return locks_by_user

def unlock_files(files):
    """주어진 파일 리스트에 대해 강제 잠금 해제를 수행합니다."""
    total = len(files)
    print(f"\n🚀 총 {total}개의 파일에 대해 잠금 해제를 시도합니다...")

    success_count = 0
    for idx, filepath in enumerate(files, 1):
        filename = os.path.basename(filepath)
        print(f"[{idx}/{total}] Unlocking: {filename}")
        try:
            subprocess.call(f'svn unlock --force "{filepath}"', shell=True)
            success_count += 1
        except Exception as e:
            print(f"  └─ 실패: {e}")

    print(f"\n✨ 완료! (성공: {success_count} / 전체: {total})")

def show_user_files(user, files):
    """특정 사용자가 잠근 파일의 상세 경로를 출력합니다."""
    print(f"\n🔍 ['{user}'] 님이 잠근 파일 목록 ({len(files)}개):")
    print("-" * 80)
    for path in files:
        # 보기 편하게 상대 경로로 변환 시도
        try:
            display_path = os.path.relpath(path)
        except ValueError:
            display_path = path
        print(f" - {display_path}")
    print("-" * 80)
    input("\n메뉴로 돌아가려면 Enter를 누르세요...")

def main():
    locks_by_user = get_locks()

    if not locks_by_user:
        print("\n✅ 현재 잠겨있는 파일이 없습니다.")
        return

    user_list = sorted(locks_by_user.keys())

    while True:
        # 화면 클리어 (선택 사항, 필요 없으면 주석 처리)
        # os.system('cls' if os.name == 'nt' else 'clear')

        print("\n" + "="*60)
        print(f"{'No':<4} | {'USER (OWNER)':<20} | {'LOCKED FILES'}")
        print("="*60)
        
        for idx, user in enumerate(user_list, 1):
            count = len(locks_by_user[user])
            print(f"{idx:<4} | {user:<20} | {count} files")

        print("="*60)
        print("[옵션]")
        print(f" - {'숫자':<10} : 해당 사용자의 잠금 즉시 해제 (예: 1)")
        print(f" - {'v 숫자':<10} : 해당 사용자의 파일 상세 보기 (예: v 1)")
        print(f" - {'ALL':<10} : 모든 사용자의 잠금 해제")
        print(f" - {'q':<10} : 종료")
        
        choice = input("\n👉 선택: ").strip().lower()

        if choice == 'q' or not choice:
            print("종료합니다.")
            break

        # 상세 보기 기능 (v 숫자)
        if choice.startswith('v '):
            try:
                idx = int(choice.split()[1]) - 1
                if 0 <= idx < len(user_list):
                    target_user = user_list[idx]
                    show_user_files(target_user, locks_by_user[target_user])
                    continue # 루프 처음으로
                else:
                    print("❌ 잘못된 번호입니다.")
                    continue
            except (IndexError, ValueError):
                print("❌ 올바른 형식이 아닙니다. (예: v 1)")
                continue

        # 전체 해제
        if choice == 'all':
            print("\n⚠️ 모든 사용자의 잠금을 해제합니다.")
            confirm = input("진행하시겠습니까? (y/n): ")
            if confirm.lower() == 'y':
                for user in locks_by_user:
                    unlock_files(locks_by_user[user])
                break # 작업 완료 후 종료
            else:
                print("취소되었습니다.")
                continue

        # 개별 해제 (숫자만 입력 시)
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(user_list):
                target_user = user_list[idx]
                target_files = locks_by_user[target_user]
                
                print(f"\n['{target_user}'] 님의 잠금을 해제합니다.")
                unlock_files(target_files)
                
                # 해당 유저 처리 후 목록에서 제거하고 계속할지, 종료할지 결정
                del locks_by_user[target_user]
                user_list.remove(target_user)
                if not user_list:
                    print("모든 잠금이 해제되었습니다. 종료합니다.")
                    break
            else:
                print("❌ 잘못된 번호입니다.")

if __name__ == "__main__":
    main()