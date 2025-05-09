"""
Utilities for dealing with keyframes in maya
"""
from maya import cmds

from as_maya_tools.utilities import timeline_utils


def get_keyframe_list(frame_range="selected_key_range", frequency=1, **kwargs):
    """
    Get a list of keyframes with a specified frequency
    :param str frame_range: animation_range, playback_range, selected_key_range string options
    :param int frequency: separation between keyframes
    :return list(list(int)): list of keyframes TODO: make it return a list(int)
    """
    keyframe_range_options = ["animation_range", "playback_range", "selected_key_range"]
    if frame_range not in keyframe_range_options:
        cmds.warning("keyframe range not specified properly. keyframe_range argument accepts animation_range, playback_range, selected_key_range")
        return None
        
    if frame_range == "animation_range":
        keyframe_range = timeline_utils.get_animation_range()
    if frame_range == "playback_range":
        keyframe_range = timeline_utils.get_playback_range()
    if frame_range == "selected_key_range":
        keyframe_range = timeline_utils.get_selected_key_range()
        
    frames = []
    for keyframe in range(int(keyframe_range[0]), int(keyframe_range[1] + frequency)):
        frames.append(keyframe)
        
    frame_chunks = list(chunk_list(frames, chunk_size=frequency))
    return frame_chunks


def chunk_list(list_item, chunk_size=1):
    """
    chunk a list into equal sizes
    :param list list_item: list to chunk
    :param int chunk_size: max size of chunk
    """

    for i in list(range(0, len(list_item), chunk_size)):
        yield list_item[i:i + chunk_size]