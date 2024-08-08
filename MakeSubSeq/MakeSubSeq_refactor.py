import unreal

# Helper function to filter and gather possessable and spawnable actors
def gather_actors(editor_actor_subsystem, light_actor_classes):
    all_actors = editor_actor_subsystem.get_all_level_actors()
    possessable_actors = []
    spawnable_actors = []

    for cls in light_actor_classes:
        filtered_actors = unreal.EditorFilterLibrary.by_class(all_actors, cls)
        print(f"Filtered Class : {filtered_actors}")
        possessable_actors.extend(filtered_actors)

        if not any(isinstance(actor, cls) for actor in possessable_actors):
            spawnable_actors.append(cls)
    
    return possessable_actors, spawnable_actors

# Function to link light actors to a sequence
def link_light_actors_to_sequence(LIT_sub_sequence_path):
    editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    light_actor_classes = [unreal.DirectionalLight, unreal.SkyLight, unreal.PostProcessVolume, unreal.ExponentialHeightFog, unreal.SkyAtmosphere]

    possessable_actors, spawnable_actors = gather_actors(editor_actor_subsystem, light_actor_classes)

    sub_sequence = unreal.load_asset(LIT_sub_sequence_path, unreal.LevelSequence)

    for actor in possessable_actors:
        sub_sequence.add_possessable(actor)
        print(f"{actor} has been created and linked to the sequence.")

    for cls in spawnable_actors:
        sub_sequence.add_spawnable_from_class(cls)
        print(f"{cls} has been created and linked to the sequence.")

# Function to convert string to boolean
def str_to_bool(s):
    if s.lower() == "true":
        return True
    elif s.lower() == "false":
        return False
    else:
        raise ValueError(f"Cannot convert {s} to a boolean value")

# Function to get a unique asset name
def get_unique_asset_name(part, shot_name, project_name, project_name_checkbox, directory):
    asset_directory = directory.replace("\\", "/")
    base_name = f"{part}_SUB_{project_name}_{shot_name}" if project_name_checkbox.lower() == "true" else f"{part}_SUB_{shot_name}"

    counter = 2
    asset_name = f"{base_name}_{counter:02d}"

    existing_assets = unreal.EditorAssetLibrary.list_assets(asset_directory)

    for asset_path in existing_assets:
        asset = unreal.EditorAssetLibrary.load_asset(asset_path)
        exist_asset_name = unreal.SystemLibrary.get_object_name(asset)
        if exist_asset_name.startswith(base_name):
            try:
                asset_counter = int(exist_asset_name.split("_")[-1])
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
            return "break"

    return asset_name

# Main function to create a shot and handle sub sequences
def create_shot(project_selected, project_name_checkbox, lit_checkbox, fx_checkbox, ani_checkbox):
    game_name = project_selected
    print(f"game_name : {game_name}")

    if not (str_to_bool(lit_checkbox) or str_to_bool(fx_checkbox) or str_to_bool(ani_checkbox)):
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
    print(f"shot_name : {shot_name}")
    shot_path = current_level_sequence.get_path_name()
    shot_package_path = "/".join(shot_path.split("/")[:-1])
    print(f"shot_package_path : {shot_package_path}")
    project_name = shot_package_path.split("/")[-2]
    print(f"project_name : {project_name}")

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
        playback_start = playback_range.inclusive_start
        playback_end = playback_range.exclusive_end

        sub_section = sub_track.add_section()
        sub_section.set_sequence(sub_sequence_asset)
        sub_section.set_range(playback_start, playback_end)

        if part == "LIT":
            LIT_sub_sequence_path = sub_sequence_asset.get_path_name()
            link_light_actors_to_sequence(LIT_sub_sequence_path)

