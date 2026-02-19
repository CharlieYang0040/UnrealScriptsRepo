import unreal

# 1. 시네마틱 라이브러리 강제 로드
# (모듈 이름은 파일명과 같아야 합니다. 예: CinematicShotLib.py라면 CinematicShotLib)
try:
    import CinematicQuery
    import CinematicUtils
    import CinematicRender
    
    # 2. 변경사항 즉시 반영 (리로드)
    import importlib
    importlib.reload(CinematicQuery)
    importlib.reload(CinematicUtils)
    importlib.reload(CinematicRender)

    unreal.log("✅ [Init] Python Modules Loaded Successfully for Blueprints!")

except ImportError as e:
    unreal.log_error(f"❌ [Init] Failed to load Python modules: {e}")