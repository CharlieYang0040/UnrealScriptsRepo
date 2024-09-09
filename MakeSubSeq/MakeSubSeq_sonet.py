import unreal
from typing import List, Type

# 라이트 액터를 서브 시퀀스에 연결
def link_light_actors_to_sequence(LIT_sub_sequence_path: str):
    editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    allActors = editor_actor_subsystem.get_all_level_actors()

    find_lightActor_classList = [unreal.DirectionalLight, unreal.SkyLight, unreal.PostProcessVolume, unreal.ExponentialHeightFog, unreal.SkyAtmosphere]
    
    possessableActor_classList = [
        actor for actor in allActors 
        if any(isinstance(actor, cls) for cls in find_lightActor_classList)
    ]
    
    spawnableActor_classList = [
        cls for cls in find_lightActor_classList 
        if not any(isinstance(actor, cls) for actor in possessableActor_classList)
    ]

    sub_sequence = unreal.load_asset(LIT_sub_sequence_path, unreal.LevelSequence)
    
    for actor in possessableActor_classList:
        sub_sequence.add_possessable(actor)
        print(f"{actor} has been created and linked to the sequence.")
    
    for cls in spawnableActor_classList:
        sub_sequence.add_spawnable_from_class(cls)
        print(f"{cls} has been created and linked to the sequence.")

# 문자열을 불리언 값으로 변환
def str_to_bool(s: str) -> bool:
    if s.lower() == "true":
        return True
    elif s.lower() == "false":
        return False
    raise ValueError(f"Cannot convert {s} to a boolean value")

# 서브 시퀀스 에셋 이름 생성
def get_unique_asset_name(part, shot_name, project_name, ProjectName_CheckBox, directory):
    # Unreal Engine의 에셋 경로 형식으로 변경
    asset_directory = directory.replace("\\", "/")  # ~/LIT
    if ProjectName_CheckBox == "true":
        base_name = f"{part}_SUB_{project_name}_{shot_name}"  # LIT_SUB_2024_Enchantress_Shot_02_03
    else:
        base_name = f"{part}_SUB_{shot_name}"  # LIT_SUB_Shot_02_03

    # 초기 버전 번호 설정
    counter = 2
    asset_name = f"{base_name}_{counter:02d}"  # LIT_SUB_Shot_02_03_01

    # 디렉토리 내의 모든 에셋 경로를 가져옴
    existing_assets = unreal.EditorAssetLibrary.list_assets(asset_directory)

    # 에셋 경로에서 이름을 추출하여 확인
    for asset_path in existing_assets:
        asset = unreal.EditorAssetLibrary.load_asset(asset_path)
        exist_asset_name = unreal.SystemLibrary.get_object_name(asset)
        if exist_asset_name.startswith(base_name):
            try:
                # 버전 번호 추출 및 비교
                version_str = exist_asset_name.split("_")[-1]
                asset_counter = int(version_str)
                counter = max(counter, asset_counter + 1)
            except ValueError:
                continue

    # 최종 에셋 이름 생성
    asset_name = f"{base_name}_{counter - 1:02d}"
    asset_path = f"{asset_directory}/{asset_name}"

    # 에셋이 이미 존재하면 메세지 표시 및 카운터 증가
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

def create_shot(ProjectSelected: str, ProjectName_CheckBox: str, LIT_CheckBox: str, FX_CheckBox: str, ANI_CheckBox: str):
    # 프로젝트 선택 콤보박스에서 선택된 프로젝트 이름 가져오기
    game_name = ProjectSelected
    print(f"game_name : {game_name}")

    # 최소 하나의 파트를 선택했는지 확인
    if LIT_CheckBox == "false" and FX_CheckBox == "false" and ANI_CheckBox == "false":
        unreal.EditorDialog.show_message(
            message_type=unreal.AppMsgType.OK,
            title="경고",
            message="최소 하나의 파트를 선택해주세요."
            )
        return

    # 체크박스 선택 여부 딕셔너리 생성
    checkBox_dict = {
        "LIT": str_to_bool(LIT_CheckBox),
        "FX": str_to_bool(FX_CheckBox),
        "ANI": str_to_bool(ANI_CheckBox)
    }

    partList = ["LIT", "FX", "ANI"]
    partSelected = []

    for part in partList:
        if checkBox_dict[part]:
            partSelected.append(part)

    print(f"partSelected : {partSelected}")

    # 새 레벨 시퀀스 에셋 생성
    current_level_sequence = unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()
    shot_name = current_level_sequence.get_name()
    print(f"shot_name : {shot_name}")
    shot_path = current_level_sequence.get_path_name()
    shot_package_path = "/".join(shot_path.split("/")[:-1]) #/Game/A_Cinematic_Workspace/Sequencer/2024_Enchantress/Shot
    print(f"shot_package_path : {shot_package_path}")
    # 상위 폴더 이름을 project_name으로 변수 추가
    project_name = shot_package_path.split("/")[-2]
    print(f"project_name : {project_name}")

    for part in partSelected:
        sub_package_path = shot_package_path + f"/Subsequence/{part}"
        asset_name = get_unique_asset_name(part, shot_name, project_name, ProjectName_CheckBox, sub_package_path)
        # 서브 시퀀스 에셋 생성
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        if asset_name == "break":
            break
        else:
            sub_sequence_asset = asset_tools.create_asset(
                asset_name=asset_name,
                package_path=sub_package_path,
                asset_class=unreal.LevelSequence,
                factory=unreal.LevelSequenceFactoryNew()
                )
    
        # 메인 레벨 시퀀스 로드
        main_sequence_path = shot_path
        print(f"main_sequence_path : {main_sequence_path}")
        main_sequence = unreal.load_asset(main_sequence_path, unreal.LevelSequence)
        print(f"main_sequence : {main_sequence}")
        # 메인 시퀀스에 서브시퀀스 트랙 추가
        sub_track = main_sequence.add_track(unreal.MovieSceneSubTrack)
    
        # 시작과 종료 프레임 가져오기
        playback_range = main_sequence.get_playback_range()
        print(f"playback_range : {playback_range}")
        playback_start = playback_range.inclusive_start
        playback_end = playback_range.exclusive_end

        # 서브시퀀스 섹션 추가 및 설정
        sub_section = sub_track.add_section()
        sub_section.set_sequence(sub_sequence_asset)
        sub_section.set_range(playback_start, playback_end)  # 시작과 종료 프레임 설정

        # part가 LIT일 경우, 서브 시퀀스에 라이트 액터 연결
        if part == "LIT":
            LIT_sub_sequence_path = sub_sequence_asset.get_path_name()
            link_light_actors_to_sequence(LIT_sub_sequence_path)
