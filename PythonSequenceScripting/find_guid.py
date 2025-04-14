import unreal

# 선택된 바인딩들을 가져옵니다.
selected_bindings = unreal.LevelSequenceEditorBlueprintLibrary.get_selected_bindings()

if not selected_bindings:
    unreal.log_warning("선택된 바인딩이 없습니다.")
else:
    for binding in selected_bindings:
        # 사용 가능한 프로퍼티 목록 출력해서 어떤 값들이 있는지 확인
        available_props = dir(binding)
        unreal.log("바인딩 '{}'의 프로퍼티 목록: {}".format(binding.get_display_name(), available_props))
        
        # binding_id 프로퍼티 사용 시도 (MovieSceneBindingProxy에는 binding_id가 존재할 수 있습니다)
        try:
            binding_id = binding.get_editor_property("binding_id")
            unreal.log("바인딩 '{}': binding_id = {}".format(binding.get_display_name(), binding_id))
        except Exception as e:
            unreal.log_warning("바인딩 '{}': binding_id를 가져오지 못했습니다. 에러: {}".format(binding.get_display_name(), e))
