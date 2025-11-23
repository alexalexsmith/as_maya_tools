"""
Timeline scripts
"""
from maya import cmds
from as_maya_tools.utilities import timeline_utils, keyframe_utils, json_utils
from as_maya_tools import COPY_PASTE_KEYFRAME_SETTINGS_PATH


def set_playbackslider_to_selected_keys():
    """
    Set playback slider to selected keys
    """
    timeline_utils.set_playback_range(
        timeline_utils.get_selected_key_range()[0],
        timeline_utils.get_selected_key_range()[1]
    )
    cmds.selectKey(clear=True)


def copy_keyframes():
    settings = json_utils.read_offset_json_file(COPY_PASTE_KEYFRAME_SETTINGS_PATH,
                                                "copy_paste_keyframe_settings")
    if settings is None:
        settings = {}
    keyframe_utils.copy_keyframes(**settings)
    return

def paste_keyframes():
    settings = json_utils.read_offset_json_file(COPY_PASTE_KEYFRAME_SETTINGS_PATH,
                                                "copy_paste_keyframe_settings")
    if settings is None:
        settings = {}
    keyframe_utils.paste_keyframes(**settings)
    return
