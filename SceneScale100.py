import unreal

# ========================================================
# [설정 영역]
# ========================================================
TARGET_SCALE_FACTOR = 0.01   # 1/100 축소
MIN_SCALE_LIMIT = 0.0001     # 최소 크기 제한

# True로 설정하면: 선택된 액터 중 '첫 번째' 액터의 위치를 기준으로 삼습니다.
# False로 설정하면: 아래 MANUAL_PIVOT 값을 사용합니다.
USE_FIRST_ACTOR_AS_PIVOT = True 

MANUAL_PIVOT = unreal.Vector(0, 0, 0) # 수동 기준점
# ========================================================

def scale_down_preserve_sign(scale_factor, min_limit):
    selected_actors = unreal.EditorLevelLibrary.get_selected_level_actors()
    
    if not selected_actors:
        unreal.log_warning("선택된 액터가 없습니다.")
        return

    # --- [기준점 결정 로직] ---
    if USE_FIRST_ACTOR_AS_PIVOT:
        # 선택된 액터 중 첫 번째 녀석의 위치를 가져옴
        pivot_actor = selected_actors[0]
        pivot_location = pivot_actor.get_actor_location()
        pivot_name = pivot_actor.get_actor_label()
        unreal.log(f"기준점 자동 설정됨: '{pivot_name}'의 위치 {pivot_location}")
    else:
        pivot_location = MANUAL_PIVOT
        unreal.log(f"기준점 수동 설정됨: {pivot_location}")
    # -----------------------

    transaction_name = f"Scale Change x{scale_factor} (Pivot: {pivot_location})"
    
    with unreal.ScopedEditorTransaction(transaction_name):
        for actor in selected_actors:
            # 1. 위치 이동
            current_loc = actor.get_actor_location()
            relative_vector = current_loc - pivot_location
            scaled_vector = relative_vector * scale_factor
            new_loc = pivot_location + scaled_vector
            actor.set_actor_location(new_loc, False, False)
            
            # 2. 크기 스케일링
            current_scale = actor.get_actor_scale3d()
            new_x = current_scale.x * scale_factor
            new_y = current_scale.y * scale_factor
            new_z = current_scale.z * scale_factor

            # 3. 안전장치
            if abs(new_x) < min_limit: new_x = min_limit if new_x >= 0 else -min_limit
            if abs(new_y) < min_limit: new_y = min_limit if new_y >= 0 else -min_limit
            if abs(new_z) < min_limit: new_z = min_limit if new_z >= 0 else -min_limit

            actor.set_actor_scale3d(unreal.Vector(new_x, new_y, new_z))

    unreal.log("작업 완료.")

if __name__ == "__main__":
    scale_down_preserve_sign(TARGET_SCALE_FACTOR, MIN_SCALE_LIMIT)