import unreal

LOG_PREFIX = "[DisableSubseqTracks]"

def _get_focused_level_sequence() -> unreal.LevelSequence:
    seq = unreal.LevelSequenceEditorBlueprintLibrary.get_focused_level_sequence()
    if not seq:
        unreal.log_error(f"{LOG_PREFIX} No focused Level Sequence. Open a Sequencer first.")
    return seq

def _try_call(obj, name, *args, **kwargs):
    if obj and hasattr(obj, name):
        try:
            return getattr(obj, name)(*args, **kwargs)
        except Exception:
            return None
    return None

def _collect_tracks(seq: unreal.LevelSequence):
    """가능한 모든 경로로 트랙 수집 (master_tracks, find_master_tracks_by_type, get_tracks)."""
    tracks = []
    ms = _try_call(seq, "get_movie_scene")

    # LevelSequence / MovieScene의 master_tracks
    for owner in (seq, ms):
        t = _try_call(owner, "get_master_tracks")
        if t:
            for x in t:
                if x not in tracks:
                    tracks.append(x)
        # 타입별 조회
        for cls in (unreal.MovieSceneCinematicShotTrack, unreal.MovieSceneSubTrack):
            t2 = _try_call(owner, "find_master_tracks_by_type", cls)
            if t2:
                for x in t2:
                    if x not in tracks:
                        tracks.append(x)

    # 최후수단: get_tracks()
    for owner in (ms, seq):
        t3 = _try_call(owner, "get_tracks")
        if t3:
            for x in t3:
                if x not in tracks:
                    tracks.append(x)

    return tracks

def _iter_shot_subsections(master_seq: unreal.LevelSequence):
    """마스터 시퀀스의 모든 Shot 섹션(MovieSceneSubSection)을 yield."""
    # 샷은 마스터의 시네마틱 샷 트랙/서브트랙에 들어있음
    for track in _collect_tracks(master_seq):
        if isinstance(track, (unreal.MovieSceneCinematicShotTrack, unreal.MovieSceneSubTrack)):
            secs = _try_call(track, "get_sections") or []
            for sec in secs:
                if isinstance(sec, unreal.MovieSceneSubSection):
                    yield sec

def _get_level_sequence_from_subsection(subsec: unreal.MovieSceneSubSection):
    seq = _try_call(subsec, "get_sequence")
    if not seq:
        try:
            seq = subsec.get_editor_property("sub_sequence")
        except Exception:
            seq = None
    return seq if isinstance(seq, unreal.LevelSequence) else None

def _disable_track(track) -> bool:
    """트랙 비활성화를 다양한 방식으로 시도."""
    # 1) set_is_eval_disabled
    if hasattr(track, "set_is_eval_disabled"):
        try:
            track.set_is_eval_disabled(True)
            return True
        except Exception:
            pass
    # 2) set_enabled(False)
    if hasattr(track, "set_enabled"):
        try:
            track.set_enabled(False)
            return True
        except Exception:
            pass
    # 3) 에디터 프로퍼티 경유
    for prop in ("eval_disabled", "enabled", "is_enabled"):
        try:
            if track.has_editor_property(prop):
                # enabled류는 True가 기본이니 False로 세팅
                val = False if "enabled" in prop else True
                track.set_editor_property(prop, val)
                return True
        except Exception:
            pass
    # 4) eval_options.enable (구버전 호환)
    try:
        eval_opts = track.get_editor_property("eval_options")
        if hasattr(eval_opts, "enable"):
            if getattr(eval_opts, "enable"):
                setattr(eval_opts, "enable", False)
                track.set_editor_property("eval_options", eval_opts)
                return True
    except Exception:
        pass
    return False

def _disable_section(sec) -> bool:
    """섹션 비활성화(보조)."""
    # 1) 공통 에디터 프로퍼티
    try:
        if sec.get_editor_property("is_active"):
            sec.set_editor_property("is_active", False)
            return True
    except Exception:
        pass
    # 2) 함수형 세터
    if hasattr(sec, "set_is_active"):
        try:
            sec.set_is_active(False)
            return True
        except Exception:
            pass
    # 3) eval_options.enable (구버전 호환)
    try:
        eval_opts = sec.get_editor_property("eval_options")
        if hasattr(eval_opts, "enable") and getattr(eval_opts, "enable"):
            setattr(eval_opts, "enable", False)
            sec.set_editor_property("eval_options", eval_opts)
            return True
    except Exception:
        pass
    return False

def _disable_all_subsequence_tracks_in_sequence(seq: unreal.LevelSequence) -> (int, int):
    """
    샷 시퀀스 내부의 MovieSceneSubTrack(서브시퀀스 트랙)을 찾아 트랙/섹션을 비활성화.
    반환: (disabled_tracks, disabled_sections)
    """
    ms = _try_call(seq, "get_movie_scene")
    if not ms:
        return (0, 0)

    # 후보 트랙 모으기
    candidate_tracks = []
    for t in _collect_tracks(seq):
        if isinstance(t, unreal.MovieSceneSubTrack):
            candidate_tracks.append(t)

    # 디버깅: 아무것도 못찾을 경우 트랙 구성 로그
    if not candidate_tracks:
        unreal.log_warning(f"{LOG_PREFIX} No MovieSceneSubTrack found in '{seq.get_name()}'. Dumping track classes for debug:")
        for t in _collect_tracks(seq):
            try:
                unreal.log(f"{LOG_PREFIX}   Track: {t.get_display_name()} [{t.get_class().get_name()}]")
                secs = _try_call(t, "get_sections") or []
                for s in secs:
                    unreal.log(f"{LOG_PREFIX}     Section: {s.get_name()} [{s.get_class().get_name()}]")
            except Exception:
                pass
        return (0, 0)

    disabled_tracks = 0
    disabled_sections = 0

    for track in candidate_tracks:
        # 1) 트랙 자체 비활성화
        if _disable_track(track):
            disabled_tracks += 1

        # 2) 트랙의 모든 섹션(=MovieSceneSubSection)도 보조적으로 비활성화
        secs = _try_call(track, "get_sections") or []
        for sec in secs:
            if isinstance(sec, unreal.MovieSceneSubSection):
                if _disable_section(sec):
                    disabled_sections += 1

    return (disabled_tracks, disabled_sections)

def _save_if_dirty():
    try:
        unreal.EditorAssetLibrary.save_loaded_assets()
    except Exception:
        pass

def run():
    master = _get_focused_level_sequence()
    if not master:
        return

    total_tracks = 0
    total_secs = 0
    visited = 0

    with unreal.ScopedEditorTransaction("Disable subsequence tracks in shots"):
        for shot_subsec in _iter_shot_subsections(master):
            shot_seq = _get_level_sequence_from_subsection(shot_subsec)
            if not shot_seq:
                continue
            visited += 1
            dt, ds = _disable_all_subsequence_tracks_in_sequence(shot_seq)
            total_tracks += dt
            total_secs += ds
            unreal.log(f"{LOG_PREFIX} Shot '{shot_seq.get_name()}': disabled tracks={dt}, sections={ds}")

        _save_if_dirty()

    unreal.log(f"{LOG_PREFIX} Done. Shots visited: {visited}, disabled_tracks: {total_tracks}, disabled_sections: {total_secs}")

# 즉시 실행
run()
