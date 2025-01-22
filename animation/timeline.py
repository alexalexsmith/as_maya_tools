"""
Timeline scripts
"""
from maya import cmds
from as_maya_tools.utilities import timeline_utils


def set_playbackslider_to_selected_keys():
    """
    Set playback slider to selected keys
    """
    timeline_utils.set_playback_range(
        timeline_utils.get_selected_key_range()[0],
        timeline_utils.get_selected_key_range()[1]
    )
