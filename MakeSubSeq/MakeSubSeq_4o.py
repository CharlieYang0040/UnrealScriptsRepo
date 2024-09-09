import unreal

# 라이트 액터를 서브 시퀀스에 연결
def link_light_actors_to_sequence(sub_sequence, possessable_actors, spawnable_classes):
    for actor in possessable_actors:
        sub_sequence.add_possessable(actor)
        print(f"{actor} has been created and linked to the sequence.")
    for cls in spawnable_classes:
        sub_sequence.add_spawnable_from_class(cls)
        print(f"{cls} has been created and linked to the sequence.")

def get_light_actors(editor_actor_subsystem, actor_classes):
    all_actors = editor_actor_subsystem.get_all_level_actors()
    possessable_actors = []
    spawnable_classes = []

    for cls in actor_classes:
        actors = unreal.EditorFilterLibrary.by_class(all_actors, cls)
        if actors:
            possessable_actors.extend(actors)
        else:
            spawnable_classes.append(cls)

    return possessable_actors, spawnable_classes

def str_to_bool(s):
    if s.lower() == "true":
        return True
    elif s.lower() == "false":
        return False
    else:
        raise ValueError(f"Cannot convert {s} to a boolean value")

def get_unique_asset_name(part, shot_name, project_name, include_project_name, directory):
    asset_directory = directory.replace("\\", "/")
    base_name = f"{part}_SUB_{project_name}_{shot_name}" if include_project_name else f"{part}_SUB_{shot_name}"
    counter = 2
    asset_name = f"{base_name}_{counter:02d}"
    existing_assets = unreal.EditorAssetLibrary.list_assets(asset_directory)

    for asset_path in existing_assets:
        asset = unreal.EditorAssetLibrary.load_asset(asset_path)
        exist_asset_name = unreal.SystemLibrary.get_object_name(asset)
        if exist_asset_name.startswith(base_name):
            try:
                version_str = exist_asset_name.split("_")[-1]
                asset_counter = int(version_str)
                counter = max(counter, asset_counter + 1)
            except ValueError:
                continue

    asset_name = f"{base_name}_{counter - 1:02d}"
    asset_path = f"{asset_directory}/{asset_name}"

    if unreal.EditorAssetLibrary.does_asset_exist(asset_path):
        exist_message = unreal.EditorDialog.show_message(
            message_type=unreal.AppMsgType.YES_NO,
            title="경고",
            message=f"{base_name}_{counter - 1:02d} : 시퀀스가 이미 존재합니다.\n{base_name}_{counter:02d} : 이름으로 생성하시겠습니까?\n아니요를 선택하면 작업이 취소됩니다."
        )
        if exist_message == unreal.AppReturnType.YES:
            asset_name = f"{base_name}_{counter:02d}"
        else:
            asset_name = "break"

    return asset_name

def create_shot(project_selected, project_name_checkbox, lit_checkbox, fx_checkbox, ani_checkbox):
    game_name = project_selected
    print(f"game_name : {game_name}")

    if not any(map(str_to_bool, [lit_checkbox, fx_checkbox, ani_checkbox])):
        unreal.EditorDialog.show_message(
            message_type=unreal.AppMsgType.OK,
            title="경고",
            message="최소 하나의 파트를 선택해주세요."
        )
        return

    checkBox_dict = {
        "LIT": str_to_bool(lit_checkbox),
        "FX": str_to_bool(fx_checkbox),
        "ANI": str_to_bool(ani_checkbox)
    }

    part_selected = [part for part, selected in checkBox_dict.items() if selected]
    print(f"partSelected : {part_selected}")

    current_level_sequence = unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()
    shot_name = current_level_sequence.get_name()
    shot_path = current_level_sequence.get_path_name()
    shot_package_path = "/".join(shot_path.split("/")[:-1])
    project_name = shot_package_path.split("/")[-2]

    for part in part_selected:
        sub_package_path = f"{shot_package_path}/Subsequence/{part}"
        asset_name = get_unique_asset_name(part, shot_name, project_name, project_name_checkbox, sub_package_path)
        if asset_name == "break":
            break

        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        sub_sequence_asset = asset_tools.create_asset(
            asset_name=asset_name,
            package_path=sub_package_path,
            asset_class=unreal.LevelSequence,
            factory=unreal.LevelSequenceFactoryNew()
        )

        main_sequence = unreal.load_asset(shot_path, unreal.LevelSequence)
        sub_track = main_sequence.add_track(unreal.MovieSceneSubTrack)
        playback_range = main_sequence.get_playback_range()
        sub_section = sub_track.add_section()
        sub_section.set_sequence(sub_sequence_asset)
        sub_section.set_range(playback_range.inclusive_start, playback_range.exclusive_end)

        if part == "LIT":
            editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
            possessable_actors, spawnable_classes = get_light_actors(editor_actor_subsystem, [
                unreal.DirectionalLight, unreal.SkyLight, unreal.PostProcessVolume, unreal.ExponentialHeightFog, unreal.SkyAtmosphere
            ])
            link_light_actors_to_sequence(sub_sequence_asset, possessable_actors, spawnable_classes)
