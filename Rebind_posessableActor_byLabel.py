import unreal

def fix_bindings_ue5_6_subsystem():
    # 1. 시퀀서 가져오기
    sequence = unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()
    if not sequence:
        unreal.log_error("에러: 시퀀서가 열려있지 않습니다.")
        return

    # 2. [핵심] 레벨 시퀀스 에디터 서브시스템 가져오기 (5.6 버전의 새로운 담당자)
    ls_system = unreal.get_editor_subsystem(unreal.LevelSequenceEditorSubsystem)
    if not ls_system:
        unreal.log_error("에러: LevelSequenceEditorSubsystem을 찾을 수 없습니다.")
        return

    # 3. 월드 액터 매핑 (이름 -> 액터)
    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    world_actors = actor_subsystem.get_all_level_actors()
    
    actor_map = {}
    for actor in world_actors:
        label = str(actor.get_actor_label())
        actor_map[label] = actor
    
    # 4. 바인딩 복구
    bindings = sequence.get_bindings()
    fixed_count = 0
    
    unreal.log_warning(f"--- [UE 5.6.1] 서브시스템을 통한 복구 시작 ({len(bindings)}개) ---")

    for binding in bindings:
        binding_name = str(binding.get_display_name())
        
        if binding_name in actor_map:
            target_actor = actor_map[binding_name]
            
            try:
                # [핵심] 서브시스템의 함수 사용
                # 인자 순서: ([액터 리스트], 바인딩_프록시)
                ls_system.add_actors_to_binding([target_actor], binding)
                
                fixed_count += 1
                unreal.log(f"[연결 성공] {binding_name}")
                
            except Exception as e:
                unreal.log_error(f"[실패] {binding_name}: {e}")
        else:
            pass

    unreal.log_warning(f"--- 작업 완료: 총 {fixed_count}개 연결됨 ---")
    
    # 갱신
    unreal.LevelSequenceEditorBlueprintLibrary.refresh_current_level_sequence()

# 실행
fix_bindings_ue5_6_subsystem()