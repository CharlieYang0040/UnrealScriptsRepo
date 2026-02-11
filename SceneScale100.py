import unreal
import math

def scale_down_preserve_sign(scale_factor=0.01, pivot_location=unreal.Vector(0, 0, 0)):
    selected_actors = unreal.EditorLevelLibrary.get_selected_level_actors()
    
    if not selected_actors:
        unreal.log_warning("선택된 액터가 없습니다.")
        return

    with unreal.ScopedEditorTransaction("Scale Down 1/100 (Keep Negative)"):
        
        for actor in selected_actors:
            # 1. 위치 이동 (기존과 동일)
            current_loc = actor.get_actor_location()
            relative_vector = current_loc - pivot_location
            scaled_vector = relative_vector * scale_factor
            new_loc = pivot_location + scaled_vector
            actor.set_actor_location(new_loc, False, False)
            
            # 2. 크기 스케일링 (수정된 로직)
            current_scale = actor.get_actor_scale3d()
            
            # 일단 곱하기
            new_x = current_scale.x * scale_factor
            new_y = current_scale.y * scale_factor
            new_z = current_scale.z * scale_factor

            # 3. 안전장치 수정 (절대값 사용)
            # 0.0001 보다 작고, -0.0001 보다 큰 구간(0에 근접한 구간)만 차단
            min_limit = 0.0001

            # X축 검사
            if abs(new_x) < min_limit:
                new_x = min_limit if new_x >= 0 else -min_limit
            
            # Y축 검사
            if abs(new_y) < min_limit:
                new_y = min_limit if new_y >= 0 else -min_limit

            # Z축 검사
            if abs(new_z) < min_limit:
                new_z = min_limit if new_z >= 0 else -min_limit

            # 최종 적용
            actor.set_actor_scale3d(unreal.Vector(new_x, new_y, new_z))

    unreal.log(f"작업 완료: 음수 스케일을 유지하며 {scale_factor}배로 축소했습니다.")

# 실행
scale_down_preserve_sign(0.01, unreal.Vector(0, 0, 0))