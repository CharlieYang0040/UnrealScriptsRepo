import unreal

LOG_PREFIX = "[EnableSubseqTracks]"

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

    # 바인딩(오브젝트) 트랙 수집 (UE5.6 대응)
    for owner in (seq, ms):
        bindings = _try_call(owner, "get_bindings")
        if bindings:
            for b in bindings:
                # BindingProxy → tracks
                bt = _try_call(b, "get_tracks") or []
                for x in bt:
                    if x not in tracks:
                        tracks.append(x)
                # 타입별도 시도
                for cls in (unreal.MovieSceneSubTrack, unreal.MovieSceneTrack):
                    bt2 = _try_call(b, "find_tracks_by_type", cls) or []
                    for x in bt2:
                        if x not in tracks:
                            tracks.append(x)

    return tracks

def _iter_shot_subsections(master_seq: unreal.LevelSequence):
    """마스터 시퀀스의 모든 Shot 섹션(MovieSceneSubSection)을 yield."""
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

def _enable_track(track) -> bool:
    """트랙 활성화를 다양한 방식으로 시도."""
    # 1) set_is_eval_disabled(False)
    if hasattr(track, "set_is_eval_disabled"):
        try:
            track.set_is_eval_disabled(False)
            return True
        except Exception:
            pass
    # 1.1) set_eval_disabled(False) (함수명 변형 호환)
    if hasattr(track, "set_eval_disabled"):
        try:
            track.set_eval_disabled(False)
            return True
        except Exception:
            pass
    # 2) set_enabled(True)
    if hasattr(track, "set_enabled"):
        try:
            track.set_enabled(True)
            return True
        except Exception:
            pass
    # 3) 에디터 프로퍼티 경유
    #    enabled / is_enabled 계열은 True, eval_disabled는 False가 되어야 활성
    for prop in ("enabled", "is_enabled"):
        try:
            if track.has_editor_property(prop):
                track.set_editor_property(prop, True)
                return True
        except Exception:
            pass
    for prop in ("eval_disabled",):
        try:
            if track.has_editor_property(prop):
                track.set_editor_property(prop, False)
                return True
        except Exception:
            pass
    # 3.5) row-level 비활성 해제 시도
    for prop in ("row_eval_disabled", "rows_eval_disabled"):
        try:
            if track.has_editor_property(prop):
                val = track.get_editor_property(prop)
                # 배열/단일 모두 대응
                if isinstance(val, (list, tuple)):
                    changed = False
                    new_val = []
                    for v in val:
                        nv = False if isinstance(v, bool) else v
                        new_val.append(nv)
                        changed = changed or (nv != v)
                    if changed:
                        track.set_editor_property(prop, new_val)
                        return True
                elif isinstance(val, bool) and val:
                    track.set_editor_property(prop, False)
                    return True
        except Exception:
            pass
    # 4) eval_options.can_evaluate 계열 (엔진 버전 호환)
    try:
        eval_opts = track.get_editor_property("eval_options")
        changed = False
        for attr in ("can_evaluate", "b_can_evaluate", "enable"):
            if hasattr(eval_opts, attr):
                if not getattr(eval_opts, attr):
                    setattr(eval_opts, attr, True)
                    changed = True
                break
        if changed:
            track.set_editor_property("eval_options", eval_opts)
            return True
    except Exception:
        pass

    # 5) 트랙 뮤트 해제 (UI 비활성 상태 해소)
    for setter in ("set_is_muted", "set_muted", "set_mute"):
        if hasattr(track, setter):
            try:
                getattr(track, setter)(False)
                return True
            except Exception:
                pass
    for prop in ("mute", "muted", "is_muted"):
        try:
            if track.has_editor_property(prop):
                if track.get_editor_property(prop):
                    track.set_editor_property(prop, False)
                    return True
        except Exception:
            pass

    # 6) Sequencer Scripting 확장 API 사용
    try:
        ext = getattr(unreal, "MovieSceneTrackExtensions", None)
        if ext:
            if hasattr(ext, "set_evaluation_enabled"):
                ext.set_evaluation_enabled(track, True)
                return True
            # row 기반 API 시도
            num_rows = 1
            if hasattr(ext, "get_num_rows"):
                try:
                    num_rows = max(1, int(ext.get_num_rows(track)))
                except Exception:
                    num_rows = 1
            # enabled 방식
            if hasattr(ext, "set_row_evaluation_enabled"):
                any_row = False
                for i in range(num_rows):
                    try:
                        ext.set_row_evaluation_enabled(track, i, True)
                        any_row = True
                    except Exception:
                        pass
                if any_row:
                    return True
            # disabled 방식
            for fn in ("set_row_evaluation_disabled", "set_row_eval_disabled"):
                if hasattr(ext, fn):
                    any_row = False
                    for i in range(num_rows):
                        try:
                            getattr(ext, fn)(track, i, False)
                            any_row = True
                        except Exception:
                            pass
                    if any_row:
                        return True
    except Exception:
        pass

    return _is_track_enabled(track)

def _is_track_enabled(track) -> bool:
    """트랙의 현재 활성 상태를 최대한 신뢰성 있게 판정."""
    # eval_disabled 우선 확인
    try:
        if track.has_editor_property("eval_disabled"):
            if bool(track.get_editor_property("eval_disabled")):
                return False
    except Exception:
        pass
    # mute 계열 확인 (뮤트면 비활성로 간주)
    try:
        for prop in ("mute", "muted", "is_muted"):
            if track.has_editor_property(prop):
                if bool(track.get_editor_property(prop)):
                    return False
    except Exception:
        pass
    # enabled / is_enabled 확인
    for prop in ("enabled", "is_enabled"):
        try:
            if track.has_editor_property(prop):
                return bool(track.get_editor_property(prop))
        except Exception:
            pass
    # eval_options 내부 플래그 확인
    try:
        eval_opts = track.get_editor_property("eval_options")
        for attr in ("can_evaluate", "b_can_evaluate", "enable"):
            if hasattr(eval_opts, attr):
                return bool(getattr(eval_opts, attr))
    except Exception:
        pass
    # 판단 불가 시 활성로 간주 (엔진 기본값)
    return True

def _enable_section(sec) -> bool:
    """섹션 활성화."""
    # 1) 공통 에디터 프로퍼티
    try:
        # is_active가 False였을 때 True로
        if not sec.get_editor_property("is_active"):
            sec.set_editor_property("is_active", True)
            return True
    except Exception:
        pass
    # 2) 함수형 세터
    if hasattr(sec, "set_is_active"):
        try:
            sec.set_is_active(True)
            return True
        except Exception:
            pass
    # 3) eval_options.enable (구버전 호환)
    try:
        eval_opts = sec.get_editor_property("eval_options")
        if hasattr(eval_opts, "enable") and not getattr(eval_opts, "enable"):
            setattr(eval_opts, "enable", True)
            sec.set_editor_property("eval_options", eval_opts)
            return True
    except Exception:
        pass
    return False

def _enable_all_subsequence_tracks_in_sequence(seq: unreal.LevelSequence) -> (int, int):
    """
    샷 시퀀스 내부의 MovieSceneSubTrack(서브시퀀스 트랙)과 그 섹션들을 활성화.
    반환: (enabled_tracks, enabled_sections)
    """
    ms = _try_call(seq, "get_movie_scene")
    if not ms:
        return (0, 0)

    # 후보 트랙 모으기: 모든 트랙 대상 (UE5.6 Deactivate 토글 대응)
    candidate_tracks = list(_collect_tracks(seq))

    enabled_tracks = 0
    enabled_sections = 0

    for track in candidate_tracks:
        # 1) 트랙 자체 활성화
        if _enable_track(track):
            enabled_tracks += 1

        # 2) 하위 섹션들도 활성화 (타입 불문)
        secs = _try_call(track, "get_sections") or []
        for sec in secs:
            if _enable_section(sec):
                enabled_sections += 1

    return (enabled_tracks, enabled_sections)

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

    with unreal.ScopedEditorTransaction("Enable subsequence tracks in shots"):
        for shot_subsec in _iter_shot_subsections(master):
            shot_seq = _get_level_sequence_from_subsection(shot_subsec)
            if not shot_seq:
                continue
            visited += 1
            et, es = _enable_all_subsequence_tracks_in_sequence(shot_seq)
            total_tracks += et
            total_secs += es
            unreal.log(f"{LOG_PREFIX} Shot '{shot_seq.get_name()}': enabled tracks={et}, sections={es}")

        _save_if_dirty()

    unreal.log(f"{LOG_PREFIX} Done. Shots visited: {visited}, enabled_tracks: {total_tracks}, enabled_sections: {total_secs}")

# 즉시 실행
run()
