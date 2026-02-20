import os
import shutil
import sys
import subprocess
import configparser
import xml.etree.ElementTree as ET

# 설정 파일 이름
CONFIG_FILE = 'svn_manager_config.ini'

class ConfigManager:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = configparser.ConfigParser()
        self.load_config()

    def load_config(self):
        if not os.path.exists(self.config_path):
            self.create_default_config()
            print(f"✅ 기본 설정 파일이 생성되었습니다: {self.config_path}")
            print("설정 파일을 확인하고 경로를 수정한 후 다시 실행해주세요.")
            os.startfile(self.config_path)
            sys.exit(0)
        
        try:
            self.config.read(self.config_path, encoding='utf-8')
        except Exception as e:
            print(f"❌ 설정 파일 로드 중 오류 발생: {e}")
            sys.exit(1)

    def create_default_config(self):
        self.config['PATHS'] = {
            'ENGINE_PATH': r'F:\ProjectOdin_Q\QTClient\Engine',
            'PROJECT_PATH': r'F:\ProjectOdin_Q\QTClient\ProjectQT'
        }
        with open(self.config_path, 'w', encoding='utf-8') as f:
            self.config.write(f)

    def get_paths(self):
        return {
            'ENGINE': self.config['PATHS'].get('ENGINE_PATH', ''),
            'PROJECT': self.config['PATHS'].get('PROJECT_PATH', ''),
            # 기본 cinematic workspace 경로 유추 (필요 시 config에 추가 가능하지만 일단 ProjectQT 내부로 가정)
            'CINE_WORKSPACE': os.path.join(self.config['PATHS'].get('PROJECT_PATH', ''), r'Content\A_Cinematic_Workspace')
        }

def run_svn_command(command, path, stream_output=False):
    """지정된 경로에서 SVN 명령을 실행하고 출력을 반환합니다. stream_output=True이면 실시간 출력."""
    full_cmd = f'svn {command}'
    try:
        if stream_output:
            # 실시간 출력 (Update 등 오래 걸리는 작업용)
            process = subprocess.Popen(full_cmd, cwd=path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                try:
                    print(line.decode('cp949', errors='ignore').strip())
                except:
                    pass
            process.wait()
            return "STREAMED"
        else:
            # 결과 반환용
            # cp949 인코딩 처리 (한글 윈도우)
            output = subprocess.check_output(full_cmd, cwd=path, shell=True, stderr=subprocess.STDOUT).decode('cp949', errors='ignore')
            return output
    except subprocess.CalledProcessError as e:
        print(f"❌ SVN 명령 실패 ({command}): {e.output.decode('cp949', errors='ignore')}")
        return None

def get_svn_status(path):
    """
    svn status --xml 명령을 사용하여 파일 상태를 파싱합니다.
    Returns:
        dict: { 'modified': [], 'unversioned': [], 'conflicted': [], 'added': [], 'deleted': [], 'missing': [] }
    """
    print(f"🔄 상태 확인 중... ({path})")
    
    cmd = 'status --xml'
    output = run_svn_command(cmd, path)
    
    if not output:
        return {}

    results = {
        'modified': [],
        'unversioned': [],
        'conflicted': [],
        'added': [],
        'deleted': [],
        'missing': []
    }

    try:
        root = ET.fromstring(output)
        for entry in root.findall('target/entry'):
            filepath = entry.get('path')
            # 절대 경로로 변환
            abs_path = os.path.join(path, filepath) if not os.path.isabs(filepath) else filepath
            
            wc_status = entry.find('wc-status')
            if wc_status is not None:
                item = wc_status.get('item')
                # status mapping
                if item == 'modified':
                    results['modified'].append(abs_path)
                elif item == 'unversioned':
                    results['unversioned'].append(abs_path)
                elif item == 'conflicted':
                    results['conflicted'].append(abs_path)
                elif item == 'added':
                    results['added'].append(abs_path)
                elif item == 'deleted':
                    results['deleted'].append(abs_path)
                elif item == 'missing':
                    results['missing'].append(abs_path)
    except ET.ParseError:
        print("❌ XML 파싱 에러")
    
    return results

def confirm_action(files, action_name, is_destructive=False):
    """
    작업 수행 전 사용자 확인을 받습니다.
    is_destructive가 True이면 더 강력한 경고를 표시합니다.
    """
    if not files:
        print(f"\nℹ️ {action_name} 대상 파일이 없습니다.")
        return False

    print(f"\n⚠️ 다음 {len(files)}개 파일에 대해 [{action_name}] 작업을 수행합니다:")
    for f in files[:10]: # 10개까지만 표시
        print(f" - {f}")
    if len(files) > 10:
        print(f" ... 외 {len(files) - 10}개 파일")

    if is_destructive:
        print("\n🔥 [주의] 이 작업은 돌이킬 수 없습니다! 신중하게 결정해주세요.")
        confirm = input(f"정말로 진행하시겠습니까? (y/n): ").strip().lower()
    else:
        confirm = input(f"진행하시겠습니까? (y/n): ").strip().lower()

    if confirm == 'y':
        return True
    
    print("❌ 작업이 취소되었습니다.")
    return False

def reset_engine(path):
    print(f"\n🚀 [Engine] 초기화 프로세스를 시작합니다... ({path})")
    status = get_svn_status(path)
    
    if not any(status.values()):
        print("✅ 변경사항이 없습니다. 엔진이 깨끗한 상태입니다.")
        return

    # 1. Conflict (충돌) 처리
    if status['conflicted']:
        print(f"\n🔥 충돌(Conflict)이 발생한 파일이 {len(status['conflicted'])}개 있습니다!")
        if confirm_action(status['conflicted'], "충돌 해결 (서버 버전으로 강제 동기화 추천)"):
            print("1. 서버 버전(Theirs-full)으로 덮어쓰기 (추천)")
            print("2. 내 버전(Mine-full) 유지하기")
            print("3. 변경사항 취소(Revert)")
            
            choice = input("👉 선택 (1/2/3): ").strip()
            if choice == '1':
                run_svn_command('resolve --accept theirs-full -R .', path)
            elif choice == '2':
                run_svn_command('resolve --accept mine-full -R .', path)
            elif choice == '3':
                run_svn_command('revert -R .', path)
            else:
                print("❌ 올바른 선택이 아닙니다. 건너뜁니다.")

    # 2. Modified (수정됨) & Missing (삭제됨) -> Revert
    revert_targets = status['modified'] + status['missing'] + status['deleted']
    if revert_targets:
        if confirm_action(revert_targets, "변경사항 원복(Revert)", is_destructive=True):
            print("🔄 Revert 실행 중...")
            # 일괄 revert
            run_svn_command('revert -R .', path)
            print("✅ Revert 완료.")

    # 3. Unversioned (버전 관리 안됨) & Added -> Delete
    delete_targets = status['unversioned'] + status['added']
    if delete_targets:
        if confirm_action(delete_targets, "불필요한 파일 삭제(Delete)", is_destructive=True):
            print("🗑️ 삭제 실행 중...")
            for target in delete_targets:
                try:
                    target_path = os.path.join(path, target)
                    if os.path.isdir(target_path):
                        shutil.rmtree(target_path)
                    else:
                        os.remove(target_path)
                    print(f" - Deleted: {target}")
                except Exception as e:
                    print(f"❌ 삭제 실패 ({target}): {e}")
            print("✅ 삭제 완료.")
    
    print("\n✨ 엔진 초기화 작업이 완료되었습니다.")

def manage_project(path, cine_path):
    print(f"\n🚀 [ProjectQT] 상태 관리 프로세스를 시작합니다... ({path})")
    status = get_svn_status(path)
    
    total_changes = sum(len(v) for v in status.values())
    if total_changes == 0:
        print("✅ 변경사항이 없습니다.")
        return

    print(f"\n📦 총 {total_changes}개의 변경사항이 감지되었습니다.")
    for category, files in status.items():
        if files:
            print(f" - {category.upper()}: {len(files)}개")
            for f in files[:5]:
                print(f"   └ {os.path.basename(f)}")
            if len(files) > 5:
                print(f"   └ ... 외 {len(files)-5}개")

    print("\n[작업 선택]")
    print("1. Commit (A_Cinematic_Workspace 내부만)")
    print("2. Commit (전체 변경사항 - *주의*)")
    print("3. Revert (변경사항 취소 - *주의: 되돌릴 수 없음*)")
    print("4. Pass (건너뛰기)")
    
    choice = input("👉 선택 (1/2/3/4): ").strip()
    
    if choice == '1':
        # Commit (Cinematic Workspace only)
        # 해당 경로 내부의 파일만 필터링하거나, 커밋 시 경로를 지정하면 됨.
        # 여기서는 경로를 직접 지정해서 커밋.
        print(f"\n🎥 [A_Cinematic_Workspace] 커밋을 진행합니다.")
        print(f"경로: {cine_path}")
        
        # 실제 변경사항이 있는지 해당 경로 기준으로 체크해볼 수도 있음 (생략 가능하지만 안전하게 check)
        # svn status를 전체로 봤으니, 해당 경로가 포함된 파일이 있는지 확인
        cine_changes = []
        all_changed_files = []
        for file_list in status.values():
            all_changed_files.extend(file_list)
        
        # 경로 정규화해서 비교
        norm_cine_path = os.path.normpath(cine_path).lower()
        for f in all_changed_files:
            if os.path.normpath(f).lower().startswith(norm_cine_path):
                cine_changes.append(f)
        
        if not cine_changes:
            print("⚠️ A_Cinematic_Workspace 내부에 변경사항이 없습니다.")
            return

        print(f"대상 파일: {len(cine_changes)}개")
        for f in cine_changes[:5]:
             print(f" - {os.path.basename(f)}")
        
        log_msg = input("📝 커밋 메시지를 입력하세요 (Enter: 취소): ").strip()
        if log_msg:
            print("커밋 중...")
            # 특정 경로만 커밋
            run_svn_command(f'commit -m "{log_msg}" "{cine_path}"', path, stream_output=True)
            print("✅ 커밋 완료.")
        else:
            print("커밋이 취소되었습니다.")

    elif choice == '2':
        # Commit (All)
        print("\n⚠️ 프로젝트 전체 커밋을 진행합니다.")
        log_msg = input("📝 커밋 메시지를 입력하세요 (Enter: 취소): ").strip()
        if log_msg:
            print("커밋 중...")
            run_svn_command(f'commit -m "{log_msg}"', path, stream_output=True)
            print("✅ 커밋 완료.")
        else:
            print("커밋이 취소되었습니다.")
            
    elif choice == '3':
        # Revert
        revert_targets = status['modified'] + status['missing'] + status['deleted'] + status['conflicted']
        if revert_targets:
            if confirm_action(revert_targets, "프로젝트 변경사항 원복(Revert)", is_destructive=True):
                print("🔄 Revert 실행 중...")
                run_svn_command('revert -R .', path, stream_output=True)
                print("✅ Revert 완료.")
        else:
            print("Revert 가능한 파일이 없습니다.")
            
    elif choice == '4':
        print("건너뜁니다.")
    else:
        print("잘못된 입력입니다.")

def show_status_summary(engine_path, project_path):
    print("\n🔍 전체 SVN 상태 요약 정보를 조회합니다...")
    
    paths = {
        'Engine': engine_path,
        'ProjectQT': project_path
    }

    for name, path in paths.items():
        print(f"\n[{name}] ({path})")
        status = get_svn_status(path)
        
        total_changes = sum(len(v) for v in status.values())
        if total_changes == 0:
            print("  ✅ 변경사항 없음 (Clean)")
        else:
            for category, files in status.items():
                if files:
                    print(f"  - {category.upper()}: {len(files)}개")
                    # 간단히 3개까지만 보여줌
                    for f in files[:3]:
                        print(f"    └ {os.path.basename(f)}")
                    if len(files) > 3:
                        print(f"    └ ... 외 {len(files)-3}개")

def show_menu():
    print("\n" + "="*50)
    print("   SVN Reset Manager - 엔진/프로젝트 초기화 도구")
    print("="*50)
    print("1. [Update] 전체 최신버전 받기 (Engine + ProjectQT)")
    print("2. [Status] 전체 상태 요약 확인")
    print("3. [Engine] 초기화 (Revert, Delete Unversioned)")
    print("4. [ProjectQT] 상태 관리 (Commit, Revert)")
    print("q. 종료")
    print("-" * 50)

def get_base_dir():
    """
    어떤 환경(순수 파이썬, PyInstaller, Nuitka 등)에서 실행되더라도
    항상 메인 실행 파일(.exe 또는 .py)이 있는 폴더의 절대 경로를 반환합니다.
    """
    # 1. Nuitka로 빌드된 환경인지 체크
    if "__compiled__" in globals():
        return os.path.dirname(os.path.abspath(sys.argv[0]))
    
    # 2. PyInstaller로 빌드된 환경인지 체크
    elif getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    
    # 3. 일반 파이썬 스크립트(.py)로 실행된 경우
    else:
        return os.path.dirname(os.path.abspath(__file__))

def main():
    # 설정 로드
    if getattr(sys, 'frozen', False):
        # PyInstaller로 빌드된 경우 실행 파일 위치 기준
        script_dir = os.path.dirname(sys.executable)
    else:
        # 일반 스크립트 실행
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
    # 수정된 경로 탐색 로직 적용!
    script_dir = get_base_dir()
    config_path = os.path.join(script_dir, CONFIG_FILE)
    config_mgr = ConfigManager(config_path)
    paths = config_mgr.get_paths()

    print(f"SVN Manager 시작... (Target: {paths['ENGINE']})")

    while True:
        show_menu()
        choice = input("👉 선택: ").strip().lower()

        if choice == 'q':
            print("종료합니다.")
            break
        elif choice == '1':
            print("\n📥 전체 업데이트(Update)를 시작합니다...")
            print(f"--- Engine ({paths['ENGINE']}) ---")
            run_svn_command('update', paths['ENGINE'], stream_output=True)
            print(f"\n--- ProjectQT ({paths['PROJECT']}) ---")
            run_svn_command('update', paths['PROJECT'], stream_output=True)
            print("\n✅ 업데이트 완료.")
        elif choice == '2':
            show_status_summary(paths['ENGINE'], paths['PROJECT'])
        elif choice == '3':
            reset_engine(paths['ENGINE'])
        elif choice == '4':
            manage_project(paths['PROJECT'], paths['CINE_WORKSPACE'])
        else:
            print("잘못된 입력입니다.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🚫 사용자에 의해 강제 종료되었습니다.")
        sys.exit(0)
