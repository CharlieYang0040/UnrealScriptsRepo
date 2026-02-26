import os
import shutil
import sys
import subprocess
import getpass
import xml.etree.ElementTree as ET

# ==============================================================================
# ANSI Escape Codes for Colors (No external dependencies)
# ==============================================================================
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'

def print_c(text, color=None, bold=False, end='\n'):
    """Helper function to print colored text"""
    prefix = ""
    if bold: prefix += Colors.BOLD
    if color: prefix += color
    sys.stdout.write(f"{prefix}{text}{Colors.RESET}{end}")
    sys.stdout.flush()

# ==============================================================================
# 경로 자동 탐색 (INI 파일 제거)
# ==============================================================================
def find_project_root(start_dir):
    """현재 위치에서 상위 폴더로 올라가며 .uproject 파일을 찾습니다."""
    current_dir = os.path.abspath(start_dir)
    while True:
        # 현재 폴더 내 uproject 확인
        for f in os.listdir(current_dir):
            if f.endswith('.uproject'):
                return current_dir
                
        parent_dir = os.path.dirname(current_dir)
        # 드라이브 최상단 도달 시 종료
        if parent_dir == current_dir:
            return None
        current_dir = parent_dir

def auto_detect_paths():
    """배치 파일 로직과 동일하게 프로젝트 루트와 엔진 경로를 자동 탐색합니다."""
    script_dir = get_base_dir()
    project_root = find_project_root(script_dir)
    
    if not project_root:
        print_c("❌ 프로젝트 루트를 찾을 수 없습니다! (.uproject 파일 탐색 실패)", Colors.RED, bold=True)
        print_c("스크립트가 프로젝트 폴더 내부에 있는지 확인해주세요.", Colors.YELLOW)
        sys.exit(1)

    # 파이썬 배치 파일과 동일한 구조로 엔진 경로 역추적
    # 프로젝트 상위(ProjectOdin_Q) -> QTClient -> Engine
    # ProjectQT와 Engine은 형제 폴더라고 가정
    repo_root = os.path.dirname(project_root)  # 예: QTClient
    engine_root = os.path.join(repo_root, "Engine")
    
    if not os.path.exists(engine_root):
        print_c(f"❌ 엔진 폴더를 찾을 수 없습니다: {engine_root}", Colors.RED, bold=True)
        print_c("프로젝트 폴더(ProjectQT)와 엔진 폴더(Engine)가 같은 위치에 있는지 확인해주세요.", Colors.YELLOW)
        sys.exit(1)

    return {
        'ENGINE': os.path.abspath(engine_root),
        'PROJECT': os.path.abspath(project_root),
        'CINE_WORKSPACE': os.path.abspath(os.path.join(project_root, r'Content\A_Cinematic_Workspace'))
    }

def run_svn_command(command, path, stream_output=False, status_msg=None):
    """지정된 경로에서 SVN 명령을 실행하고 출력을 반환합니다."""
    full_cmd = f'svn {command}'
    try:
        if status_msg:
            print_c(f"⏳ {status_msg}...", Colors.CYAN)
            
        if stream_output:
            process = subprocess.Popen(full_cmd, cwd=path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                try:
                    # SVN 스트림 출력은 별도 색상 없이 출력
                    print(line.decode('cp949', errors='ignore').strip())
                except:
                    pass
            process.wait()
            return "STREAMED"
        else:
            output = subprocess.check_output(full_cmd, cwd=path, shell=True, stderr=subprocess.STDOUT).decode('cp949', errors='ignore')
            return output
            
    except subprocess.CalledProcessError as e:
        print_c(f"❌ SVN 명령 실패 ({command}):\n{e.output.decode('cp949', errors='ignore')}", Colors.RED, bold=True)
        return None

def get_svn_status(path):
    """svn status --xml 명령을 사용하여 파일 상태를 파싱합니다."""
    cmd = 'status --xml'
    output = run_svn_command(cmd, path, status_msg=f"상태 확인 중... ({os.path.basename(path)})")
    
    results = {'modified': [], 'unversioned': [], 'conflicted': [], 'added': [], 'deleted': [], 'missing': []}
    if not output: return results

    try:
        root = ET.fromstring(output)
        for entry in root.findall('target/entry'):
            filepath = entry.get('path')
            abs_path = os.path.join(path, filepath) if not os.path.isabs(filepath) else filepath
            
            wc_status = entry.find('wc-status')
            if wc_status is not None:
                item = wc_status.get('item')
                if item in results:
                    results[item].append(abs_path)
    except ET.ParseError:
        print_c("❌ XML 파싱 에러", Colors.RED)
    
    return results

def confirm_action(files, action_name, is_destructive=False):
    """작업 수행 전 사용자 확인을 받습니다."""
    if not files:
        print_c(f"\nℹ️ {action_name} 대상 파일이 없습니다.", Colors.CYAN)
        return False

    print_c(f"\n⚠️ 다음 {len(files)}개 파일에 대해 [{action_name}] 작업을 수행합니다:", Colors.YELLOW, bold=True)
    
    # 간이 테이블 출력
    print_c("-" * 60)
    for i, f in enumerate(files[:10], 1):
        print_c(f" {i:2d}. {os.path.basename(f)}")
    if len(files) > 10:
        print_c(f" ... 외 {len(files) - 10}개 파일")
    print_c("-" * 60)

    if is_destructive:
        print_c("\n🔥 [주의] 이 작업은 돌이킬 수 없습니다! 신중하게 결정해주세요.", Colors.RED, bold=True)
        msg_text = "정말로 진행하시겠습니까? (y/n): "
    else:
        msg_text = "진행하시겠습니까? (y/n): "

    print_c(msg_text, Colors.YELLOW, bold=True, end='')
    confirm = input().strip().lower()

    if confirm == 'y':
        return True
    
    print_c("❌ 작업이 취소되었습니다.", Colors.YELLOW)
    return False

def reset_engine(path):
    print_c(f"\n🚀 [Engine] 초기화 프로세스를 시작합니다... ({path})", Colors.CYAN, bold=True)
    status = get_svn_status(path)
    
    if not any(status.values()):
        print_c("✅ 변경사항이 없습니다. 엔진이 깨끗한 상태입니다.", Colors.GREEN)
        return

    # 1. Conflict 처리
    if status['conflicted']:
        print_c(f"\n🔥 충돌(Conflict)이 발생한 파일이 {len(status['conflicted'])}개 있습니다!", Colors.RED, bold=True)
        if confirm_action(status['conflicted'], "충돌 해결 (서버 버전으로 강제 동기화 추천)"):
            print_c(" 1. 서버 버전(Theirs-full)으로 덮어쓰기 (추천)", Colors.GREEN)
            print_c(" 2. 내 버전(Mine-full) 유지하기", Colors.GREEN)
            print_c(" 3. 변경사항 취소(Revert)", Colors.GREEN)
            
            print_c("👉 선택 (1/2/3): ", Colors.YELLOW, bold=True, end='')
            choice = input().strip()
            
            if choice == '1':
                run_svn_command('resolve --accept theirs-full -R .', path, status_msg="충돌 해결 중")
            elif choice == '2':
                run_svn_command('resolve --accept mine-full -R .', path, status_msg="충돌 해결 중")
            elif choice == '3':
                run_svn_command('revert -R .', path, status_msg="복구 중")

    # 2. Modified & Missing -> Revert
    revert_targets = status['modified'] + status['missing'] + status['deleted']
    if revert_targets:
        if confirm_action(revert_targets, "변경사항 원복(Revert)", is_destructive=True):
            run_svn_command('revert -R .', path, status_msg="Revert 실행 중")
            print_c("✅ Revert 완료.", Colors.GREEN)

    # 3. Unversioned & Added -> Delete
    delete_targets = status['unversioned'] + status['added']
    if delete_targets:
        if confirm_action(delete_targets, "불필요한 파일 삭제(Delete)", is_destructive=True):
            print_c("⏳ 삭제 실행 중...", Colors.CYAN)
            for target in delete_targets:
                try:
                    target_path = os.path.join(path, target)
                    if os.path.isdir(target_path):
                        shutil.rmtree(target_path)
                    else:
                        os.remove(target_path)
                except Exception as e:
                    print_c(f"❌ 삭제 실패 ({target}): {e}", Colors.RED)
            print_c("✅ 삭제 완료.", Colors.GREEN)
    
    print_c("\n✨ 엔진 초기화 작업이 완료되었습니다.", bold=True)

def get_svn_username(path):
    """SVN 설정에 등록된 현재 사용자의 이름(author)을 가져와 한글명으로 변환합니다."""
    # svn info 로 마지막 커밋자 또는 기본 설정 유저 가져오기 시도 
    # (여기서는 svn config 의 auth 내역을 간접 확인하거나 가장 최근 자신의 폴더 커밋 기록을 참고)
    # 완전한 로컬 svn username을 알기 가장 쉬운 방법은 svn info --show-item last-changed-author 지만,
    # 보통 auth cache 된걸 알기 위해 아래 명령 사용
    import re
    username = ""
    try:
        # svn auth 캐시 리스트에서 유저 정보를 긁어옵니다.
        output = subprocess.check_output('svn auth', shell=True, stderr=subprocess.STDOUT).decode('cp949', errors='ignore')
        for line in output.split('\n'):
            if "Username:" in line:
                username = line.split(":", 1)[1].strip()
                break
    except:
        pass

    # 영문 SVN 아이디 -> 한글 이름 맵핑 딕셔너리
    # 실시간 SVN 로그 기반으로 A_Cinematic_Workspace 팀원들을 추출하여 자동 등록했습니다.
    name_mapping = {
        "anhyeonsu": "안현수",
        "choiyunhee": "최윤희",
        "gildaeseong": "길대성",
        "jinseongin": "진성인",
        "jungsuhyunB": "정수현",
        "kangheemin": "강희민",
        "kangminji": "강민지",
        "kimbyeongsoo": "김병수",
        "kimkyungchan": "김경찬",
        "kimseunghyeok": "김승혁",
        "leesangwon": "이상원",
        "limjiseong": "임지성",
        "parkjisu": "박지수",
        "parkyoonseo": "박윤서",
        "songyongho": "송용호",
        "umsuvin": "엄수빈",
        "yanghyeoncheol": "양현철",
        "yangsunjung": "양선정",
        "superaccount": "관리자",
        "Lion-yanghyeoncheol": "양현철"
    }

    # SVN 아이디가 비어있거나 맵핑 사전에 지정되지 않은 경우 사용자가 직접 입력
    if not username or username not in name_mapping:
        if username:
            print_c(f"⚠️ 등록되지 않은 SVN 유저명입니다: {username}", Colors.YELLOW)
        else:
            print_c("⚠️ SVN 유저정보를 찾을 수 없습니다.", Colors.YELLOW)
            
        print_c("👉 본인의 한글 이름을 직접 입력해주세요: ", Colors.CYAN, bold=True, end='')
        manual_name = input().strip()
        return manual_name if manual_name else "이름미상"

    return name_mapping[username]

def manage_project(path, cine_path):
    print_c(f"\n🚀 [ProjectQT] 상태 관리 프로세스를 시작합니다... ({path})", Colors.CYAN, bold=True)
    status = get_svn_status(path)
    
    total_changes = sum(len(v) for v in status.values())
    if total_changes == 0:
        print_c("✅ 변경사항이 없습니다.", Colors.GREEN)
        return

    print_c(f"\n📦 총 {total_changes}개의 변경사항이 감지되었습니다.", Colors.CYAN)
    
    print_c(f"{'상태':<15} | {'개수':<5} | {'예시 파일'}", Colors.MAGENTA, bold=True)
    print_c("-" * 60)
    for category, files in status.items():
        if files:
            examples = ", ".join([os.path.basename(f) for f in files[:3]])
            if len(files) > 3:
                examples += f" 외 {len(files)-3}개"
            print_c(f"{category.upper():<15} | {len(files):<5} | {examples}")
    print_c("-" * 60)

    print_c("\n[어떤 작업을 하시겠습니까?]", Colors.CYAN, bold=True)
    print_c("  1. 📤 내 작업물 커밋하기 (A_Cinematic_Workspace 내부만 올리기)", Colors.GREEN)
    print_c("  2. 📤 프로젝트 전체 커밋 (전체 변경사항 무조건 올리기 - ", Colors.GREEN, end='')
    print_c("*주의*", Colors.RED, bold=True, end=')\n')
    print_c("  3. 🔄 작업 내역 모두 취소 (최신 상태로 강제 되돌리기 - ", Colors.GREEN, end='')
    print_c("*주의: 복구 불가*", Colors.RED, bold=True, end=')\n')
    print_c("  4. ➡️  그냥 나가기 (건너뛰기)", Colors.GREEN)
    
    print_c("👉 선택 (1/2/3/4): ", Colors.YELLOW, bold=True, end='')
    choice = input().strip()
    
    if choice == '1':
        print_c(f"\n🎥 [A_Cinematic_Workspace] 커밋을 진행합니다.\n경로: {cine_path}", Colors.CYAN)
        
        cine_changes = []
        all_changed_files = []
        for file_list in status.values():
            all_changed_files.extend(file_list)
        
        norm_cine_path = os.path.normpath(cine_path).lower()
        for f in all_changed_files:
            if os.path.normpath(f).lower().startswith(norm_cine_path):
                cine_changes.append(f)
        
        if not cine_changes:
            print_c("⚠️ A_Cinematic_Workspace 내부에 변경사항이 없습니다.", Colors.YELLOW)
            return

        print_c("-" * 60)
        for f in cine_changes[:5]:
            print_c(f" - {os.path.basename(f)}")
        print_c("-" * 60)
        
        # SVN 사용자명 가져오기 & 한글 변환
        korean_name = get_svn_username(path)
        prefix = f"[영상실/{korean_name}]"
        
        print_c(f"💡 SVN 계정 정보({korean_name})를 사용하여 커밋합니다.", Colors.CYAN)
        print_c(f"📝 {prefix} 뒤에 붙을 내용을 입력하세요 (빈 칸: 취소): ", bold=True, end='')
        log_msg = input().strip()
        
        if log_msg:
            full_msg = f"{prefix} {log_msg}"
            run_svn_command(f'commit -m "{full_msg}" "{cine_path}"', path, stream_output=True)
            print_c("✅ 커밋 완료.", Colors.GREEN)
        else:
            print_c("커밋이 취소되었습니다.", Colors.YELLOW)

    elif choice == '2':
        print_c("\n⚠️ 프로젝트 전체 커밋을 진행합니다.", Colors.RED, bold=True)
        
        korean_name = get_svn_username(path)
        prefix = f"[영상실/{korean_name}]"
        
        print_c(f"💡 SVN 계정 정보({korean_name})를 사용하여 커밋합니다.", Colors.CYAN)
        print_c(f"📝 {prefix} 뒤에 붙을 내용을 입력하세요 (빈 칸: 취소): ", bold=True, end='')
        log_msg = input().strip()
        
        if log_msg:
            full_msg = f"{prefix} {log_msg}"
            run_svn_command(f'commit -m "{full_msg}"', path, stream_output=True)
            print_c("✅ 커밋 완료.", Colors.GREEN)
        else:
            print_c("커밋이 취소되었습니다.", Colors.YELLOW)
            
    elif choice == '3':
        revert_targets = status['modified'] + status['missing'] + status['deleted'] + status['conflicted']
        if revert_targets:
            if confirm_action(revert_targets, "프로젝트 변경사항 원복(Revert)", is_destructive=True):
                run_svn_command('revert -R .', path, stream_output=True)
                print_c("✅ Revert 완료.", Colors.GREEN)
        else:
            print_c("Revert 가능한 파일이 없습니다.", Colors.CYAN)

def cleanup_svn(engine_path, project_path):
    print_c(f"\n🧹 SVN 클린업(Cleanup)을 시작합니다...", Colors.CYAN, bold=True)
    
    print_c(f"--- Engine ({engine_path}) ---", Colors.CYAN)
    run_svn_command('cleanup', engine_path, stream_output=True)
    
    print_c(f"\n--- ProjectQT ({project_path}) ---", Colors.CYAN)
    run_svn_command('cleanup', project_path, stream_output=True)
    
    print_c("\n✅ SVN 클린업 완료. (Lock 해제 및 찌꺼기 정리)", Colors.GREEN)

def show_status_summary(engine_path, project_path):
    print_c("\n🔍 전체 SVN 상태 요약 정보를 조회합니다...", Colors.CYAN)
    paths = {'Engine': engine_path, 'ProjectQT': project_path}

    for name, path in paths.items():
        print_c(f"\n[{name}] ({path})", Colors.CYAN, bold=True)
        status = get_svn_status(path)
        total_changes = sum(len(v) for v in status.values())
        
        if total_changes == 0:
            print_c("  ✅ 변경사항 없음 (Clean)", Colors.GREEN)
        else:
            print_c("-" * 60)
            print_c(f"  {'Category':<15} | {'Count':<5} | {'Files'}", Colors.CYAN)
            print_c("-" * 60)
            for category, files in status.items():
                if files:
                    examples = ", ".join([os.path.basename(f) for f in files[:3]])
                    if len(files) > 3:
                        examples += f" 외 {len(files)-3}개"
                    print_c(f"  {category.upper():<15} | {len(files):<5} | {examples}")

def launch_unreal_engine(engine_path, project_path):
    print_c(f"\n🚀 언리얼 엔진 실행을 준비합니다...", Colors.CYAN, bold=True)
    
    uproject_file = None
    if os.path.exists(project_path):
        for f in os.listdir(project_path):
            if f.endswith('.uproject'):
                uproject_file = os.path.join(project_path, f)
                break
                
    if not uproject_file:
        print_c(f"❌ '{project_path}' 내에서 .uproject 파일을 찾을 수 없습니다.", Colors.RED)
        return

    rel_python_path = r"Content\A_Cinematic_Workspace\Lighting\HC\CinematicShotTools\Python"
    my_python_dir = os.path.join(project_path, rel_python_path)
    
    if not os.path.exists(os.path.join(my_python_dir, "init_unreal.py")):
        print_c(f"❌ Python 스크립트 경로를 찾을 수 없습니다:\n   {my_python_dir}", Colors.RED)
        return
        
    os.environ['UE_PYTHONPATH'] = my_python_dir
    print_c(f"✅ UE_PYTHONPATH 설정됨:\n   {my_python_dir}", Colors.GREEN)

    engine_exe = os.path.join(engine_path, r"UE5.6.1\Engine\Binaries\Win64\UnrealEditor.exe")
    if not os.path.exists(engine_exe):
        alt_exe = os.path.join(engine_path, r"Engine\Binaries\Win64\UnrealEditor.exe")
        if os.path.exists(alt_exe):
            engine_exe = alt_exe
        else:
            print_c(f"❌ 언리얼 엔진 실행 파일을 찾을 수 없습니다:\n   {engine_exe}", Colors.RED)
            return
            
    print_c(f"✅ 엔진 실행 파일 확인됨:\n   {engine_exe}", Colors.GREEN)
    print_c(f"\nLaunching Unreal Editor...\nProject: {uproject_file}\n", bold=True)
    
    try:
        subprocess.Popen([engine_exe, uproject_file], creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)
        print_c("✅ 엔진 백그라운드 실행을 시작했습니다! 잠시 기다려주세요.", Colors.GREEN)
    except Exception as e:
        print_c(f"❌ 엔진 실행 중 오류 발생: {e}", Colors.RED)

def show_menu():
    print_c("\n" + "="*55, Colors.CYAN)
    print_c(" 🎬 [SVN Manager] 시네마틱 작업 도우미 🎬", Colors.YELLOW, bold=True)
    print_c("="*55, Colors.CYAN)
    
    print_c("\n[바로가기]", Colors.CYAN, bold=True)
    print_c("  0. 🚀 언리얼 엔진 실행        (현 프로젝트로 에디터 열기)", Colors.GREEN)
    
    print_c("\n[업데이트 (최신화)]", Colors.CYAN, bold=True)
    print_c("  1. ⏬ 시네마틱 파트 업데이트  (A_Cinematic_Workspace 폴더만)", Colors.GREEN)
    print_c("  2. ⏬ 프로젝트 전체 업데이트  (Engine + ProjectQT 전체)", Colors.GREEN)

    print_c("\n[작업 관리]", Colors.CYAN, bold=True)
    print_c("  3. 🔍 내 변경사항 요약 보기   (현재 수정/추가된 파일 확인)", Colors.GREEN)
    print_c("  4. 📤 프로젝트 작업 커밋/취소 (ProjectQT 데이터 올리기/되돌리기)", Colors.GREEN)
    print_c("  5. 🗑️ 엔진 폴더 초기화        (Engine 폴더의 찌꺼기 파일 정리)", Colors.GREEN)
    print_c("  6. 🧹 SVN 클린업 실행         (Lock 걸림, 오류 시 찌꺼기 청소)", Colors.GREEN)

    print_c("\n  q. ❌ 프로그램 종료", Colors.RED)
    print_c("-" * 55, Colors.CYAN)

def get_base_dir():
    if "__compiled__" in globals():
        return os.path.dirname(os.path.abspath(sys.argv[0]))
    elif getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

def main():
    # 윈도우 환경에서 ANSI escape sequence 활성화
    os.system('color') 

    paths = auto_detect_paths()

    print_c(f"\nSVN Manager 시작... (Project: {os.path.basename(paths['PROJECT'])})", Colors.GREEN, bold=True)

    while True:
        show_menu()
        print_c("👉 선택 (0~6/q): ", Colors.YELLOW, bold=True, end='')
        choice = input().strip().lower()

        if choice == 'q':
            print_c("종료합니다.", Colors.CYAN)
            break
        elif choice == '0':
            launch_unreal_engine(paths['ENGINE'], paths['PROJECT'])
        elif choice == '1':
            if os.path.exists(paths['CINE_WORKSPACE']):
                print_c(f"\n📥 [시네마틱 파트] 업데이트를 시작합니다...\n경로: {paths['CINE_WORKSPACE']}", Colors.CYAN, bold=True)
                run_svn_command('update', paths['CINE_WORKSPACE'], stream_output=True)
                print_c("\n✅ 시네마틱 파트 업데이트 완료.", Colors.GREEN)
            else:
                print_c(f"\n❌ 폴더가 아직 존재하지 않습니다 (전체 업데이트를 한 번 수행해주세요):\n   {paths['CINE_WORKSPACE']}", Colors.RED)
        elif choice == '2':
            print_c("\n📥 전체 업데이트(Update)를 시작합니다... (시간이 다소 소요될 수 있습니다)", Colors.CYAN)
            print_c(f"--- Engine ({paths['ENGINE']}) ---", Colors.CYAN, bold=True)
            run_svn_command('update', paths['ENGINE'], stream_output=True)
            print_c(f"\n--- ProjectQT ({paths['PROJECT']}) ---", Colors.CYAN, bold=True)
            run_svn_command('update', paths['PROJECT'], stream_output=True)
            print_c("\n✅ 전체 업데이트 완료.", Colors.GREEN)
        elif choice == '3':
            show_status_summary(paths['ENGINE'], paths['PROJECT'])
        elif choice == '4':
            manage_project(paths['PROJECT'], paths['CINE_WORKSPACE'])
        elif choice == '5':
            reset_engine(paths['ENGINE'])
        elif choice == '6':
            cleanup_svn(paths['ENGINE'], paths['PROJECT'])
        else:
            print_c("잘못된 입력입니다.", Colors.RED)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_c("\n\n🚫 사용자에 의해 강제 종료되었습니다.", Colors.RED, bold=True)
        sys.exit(0)
