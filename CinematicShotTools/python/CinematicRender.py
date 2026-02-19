import unreal
import os
import re
import time

@unreal.uclass()
class CinematicRenderLib(unreal.BlueprintFunctionLibrary):

    # ==============================================================================
    # [⚙️ 설정 구역] 샷 번호 범위에 따른 레벨 지정
    # 형식: (시작번호, 끝번호, "레벨 에셋 경로")
    # 위에서부터 순서대로 검사하며, 조건에 맞으면 즉시 해당 맵을 적용하고 멈춥니다.
    # ==============================================================================
    SHOT_MAP_RULES = [
        (0,    1300, "/Game/A_Cinematic_Workspace/BG/MAPS/07_EnvCinema/Prologue_Cinema/Prologue_Cinema_P.Prologue_Cinema_P"),
        (1301, 5000, "/Game/A_Cinematic_Workspace/BG/MAPS/07_EnvCinema/Prologue_Cinema/Prologue_Cinema_P1.Prologue_Cinema_P1")
    ]
    # ==============================================================================
    
    @unreal.ufunction(static=True, params=[unreal.Array(str), str, bool], ret=str, meta=dict(Category="Cinematic Render"))
    def add_shots_to_mrq(shot_paths, preset_path, clear_queue=False):
        """
        [Fix] 00_Shot_XXXX 형식의 이름에서 정확히 샷 번호를 추출하도록 정규식 수정.
        """
        
        subsystem = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)
        if not subsystem: return "Error: MRQ Subsystem missing."
        pipeline_queue = subsystem.get_queue()

        preset_asset = unreal.load_asset(preset_path) if preset_path else None

        # 기본 맵 (현재 열린 맵)
        default_map_path = None
        try:
            current_world = unreal.EditorLevelLibrary.get_editor_world()
            if current_world:
                default_map_path = unreal.SoftObjectPath(current_world.get_path_name())
        except: pass

        added_count = 0
        
        unreal.log(f"🚀 Batch Adding {len(shot_paths)} shots with Fix...")

        with unreal.ScopedEditorTransaction("Add Batch Render Jobs") as trans:
            
            if clear_queue:
                pipeline_queue.delete_all_jobs()

            # 템플릿 생성
            template_job = pipeline_queue.allocate_new_job(unreal.MoviePipelineExecutorJob)
            template_job.job_name = "Template_Job"
            if default_map_path: template_job.map = default_map_path
            if preset_asset: template_job.set_configuration(preset_asset)

            for path in shot_paths:
                new_job = pipeline_queue.duplicate_job(template_job)
                
                shot_name = os.path.basename(path).split('.')[0]
                new_job.job_name = shot_name
                new_job.sequence = unreal.SoftObjectPath(path)
                
                # --- [수정된 맵 결정 로직] ---
                target_map_soft = default_map_path
                
                # [수정] "Shot_" 뒤에 오는 숫자만 찾음 (앞의 00_ 무시)
                # 대소문자 무시 플래그(?i) 추가: Shot_0100, shot_0100 모두 인식
                match = re.search(r"Shot_(\d+)", shot_name, re.IGNORECASE)
                
                if match:
                    shot_num = int(match.group(1)) # "0100" -> 100, "2600" -> 2600
                    
                    found = False
                    for start, end, map_path_str in CinematicRenderLib.SHOT_MAP_RULES:
                        if start <= shot_num <= end:
                            target_map_soft = unreal.SoftObjectPath(map_path_str)
                            # 디버깅 로그 (확인 후 주석 처리 가능)
                            # unreal.log(f"🎯 Shot {shot_num} -> Map Assigned: {os.path.basename(map_path_str)}")
                            found = True
                            break
                    
                    if not found:
                        unreal.log_warning(f"⚠️ No map rule found for Shot {shot_num}. Using default.")
                else:
                    unreal.log_warning(f"⚠️ Could not parse shot number from: {shot_name}. Using default.")

                if target_map_soft:
                    new_job.map = target_map_soft
                # -----------------------------
                
                added_count += 1

            pipeline_queue.delete_job(template_job)

        unreal.SystemLibrary.execute_console_command(None, "NomadTab.Spawn MovieRenderPipeline")

        msg = f"✅ Added {added_count} shots."
        unreal.log(msg)
        return msg

@unreal.uclass()
class CinematicInspectorLib(unreal.BlueprintFunctionLibrary):

    @unreal.ufunction(static=True, params=[str], ret=str, meta=dict(Category="Cinematic Forensic"))
    def run_smart_profiling(sequence_path):
        """
        [Final Solution] Time Measurement -> Component Audit
        시간 측정 대신, 시퀀스 내부 구성을 뜯어서 '성능 점수(Load Score)'를 산출합니다.
        Game(CPU) 부하와 GPU 부하를 분리해서 진단합니다.
        """
        
        # 시퀀스 로드
        sequence = unreal.load_asset(sequence_path)
        if not sequence: return "[Error] Load Failed."

        bindings = sequence.get_bindings()
        
        # --- 점수판 (Scoreboard) ---
        cpu_score = 0   # Game Thread 부하 (Spawnable, Logic)
        gpu_score = 0   # GPU 부하 (Lights, VDB, Translucency)
        
        # --- 카운터 ---
        cnt_spawnables = 0
        cnt_lights_shadow = 0
        cnt_lights_simple = 0
        cnt_vdb = 0
        cnt_niagara = 0
        cnt_rect_lights = 0 # 렉트 라이트는 GPU 킬러
        
        heavy_assets_list = []

        # --- 감시 대상 키워드 ---
        GPU_HEAVY_CLASSES = {
            "HeterogeneousVolume": 50,  # VDB (매우 무거움)
            "VolumetricCloud": 30,      # 구름
            "NiagaraComponent": 10,     # 파티클 (보통)
            "RectLight": 20,            # 렉트 라이트 (그림자 비용 비쌈)
            "CineCameraActor": 0,       # 카메라는 GPU 비용 없음
        }

        for binding in bindings:
            # 1. CPU 부하 분석 (Spawnable 여부)
            # 바인딩된 템플릿 가져오기
            obj_template = binding.get_object_template()
            
            # 템플릿이 존재하면 대부분 Spawnable (Sequence가 소유함)
            # Possessable은 보통 ID로만 연결됨.
            if obj_template:
                cnt_spawnables += 1
                cpu_score += 2.0 # Spawnable 하나당 CPU 부하 점수 2점
                
                # 2. GPU 부하 분석 (컴포넌트 뜯어보기)
                class_obj = obj_template.get_class()
                class_name = class_obj.get_name()
                display_name = binding.get_display_name()
                
                # 라이트 정밀 검사
                if "Light" in class_name:
                    # Cast Shadows 체크 (템플릿의 프로퍼티 읽기)
                    try:
                        # 기본적으로 그림자가 켜져있다고 가정하고 체크
                        casts_shadows = True 
                        # 템플릿에서 속성을 읽어올 수 있다면 읽음 (파이썬 제약으로 어려울 수 있음)
                        # 여기서는 클래스 타입으로 판별
                        
                        if "RectLight" in class_name:
                            cnt_rect_lights += 1
                            gpu_score += 25 # 렉트 라이트 그림자는 매우 비쌈
                            heavy_assets_list.append(f"🔦 [RectLight] {display_name}")
                        elif "Point" in class_name or "Spot" in class_name:
                            cnt_lights_shadow += 1
                            gpu_score += 10 # 일반 그림자 라이트
                    except:
                        pass
                
                # 이펙트/볼륨 정밀 검사
                is_heavy_asset = False
                for keyword, score in GPU_HEAVY_CLASSES.items():
                    if keyword in class_name:
                        # 렉트 라이트는 위에서 처리했으므로 패스
                        if keyword == "RectLight": continue
                        
                        if keyword == "HeterogeneousVolume":
                            cnt_vdb += 1
                            heavy_assets_list.append(f"☁️ [VDB] {display_name}")
                        elif keyword == "NiagaraComponent":
                            cnt_niagara += 1
                        
                        gpu_score += score
                        is_heavy_asset = True
                        break

        # --- 리포트 작성 ---
        report = []
        report.append(f"🔎 Scene Audit: {sequence_path.split('.')[-1]}")
        report.append("=" * 40)
        
        # 1. CPU 진단 (Game Thread)
        report.append(f"[1] CPU / Game Thread Analysis")
        report.append(f" • Spawnable Objects: {cnt_spawnables}")
        
        if cnt_spawnables >= 50:
            report.append(f"   🛑 CRITICAL: Too many Spawnables!")
            report.append(f"   -> This is why your 'Game' time is 25ms+.")
            report.append(f"   -> ACTION: Convert to 'Possessables'.")
        elif cnt_spawnables >= 20:
            report.append(f"   ⚠️ Warning: High Spawnable count.")
        else:
            report.append(f"   ✅ CPU Load is manageable.")

        # 2. GPU 진단 (Render Thread)
        report.append(f"\n[2] GPU / Render Thread Analysis")
        report.append(f" • Est. GPU Score: {gpu_score} pts")
        
        if cnt_rect_lights > 0:
            report.append(f"   🔦 Rect Lights: {cnt_rect_lights} (Very Heavy Shadows)")
        if cnt_vdb > 0:
            report.append(f"   ☁️ VDB Volumes: {cnt_vdb} (Volumetric Cost)")
        if cnt_lights_shadow > 0:
            report.append(f"   💡 Other Lights: {cnt_lights_shadow}")
        if cnt_niagara > 0:
            report.append(f"   ✨ Niagara Systems: {cnt_niagara}")

        if gpu_score > 100:
            report.append(f"   🛑 CRITICAL: GPU is overloaded (65ms+ likely)")
            report.append(f"   -> Too many overlapping lights/volumes.")
        elif gpu_score > 50:
             report.append(f"   ⚠️ Warning: GPU load is high.")
        else:
             report.append(f"   ✅ GPU seems optimized.")

        # 3. 주요 범인 리스트
        if heavy_assets_list:
            report.append(f"\n[3] 🚨 Heavy Asset List (Top culprits)")
            for item in heavy_assets_list[:10]:
                report.append(f"   - {item}")
        
        return "\n".join(report)