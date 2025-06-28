"""
Utilities for space switching
"""
from maya import cmds
from as_maya_tools.utilities import attribute_utils, timeline_utils, decorators


SPACESWITCH_FRAMERANGE_OPTIONS = ["Current Frame", "Selected Frames", "Time Slider Range", "Animation Range", "Frame Range", "All Keyframes"]


@decorators.suspend_refresh
@decorators.undoable_chunk
def space_switch(attribute_paths, value, frame_range="current frame", keyed_frames=False):
    """
    maintain transform position after changing an attribute.
    :param str attribute_path:  attribute path
    :param float/int value: new value to set attribute to
    """
    if not isinstance(attribute_paths, list):
        attribute_paths = (attribute_paths)
    
    # Get a list of keyframes to perform switch over. This will set the same keyframes accross all attributes passed
    keyframes = []
    for attribute_path in attribute_paths:
        attribute_object = attribute_utils.Attribute(attribute_path)
        keyframes += get_keyframe_range(attribute_object, frame_range=frame_range, keyed_frames=keyed_frames)
    
    # Remove duplicates from keyframe list
    keyframes = list(dict.fromkeys(keyframes))
    
    # TODO: if switching all frames, need to first bake all motion then switch
    if not keyed_frames:
        for frame in keyframes:
            for attribute_path in attribute_paths:
                cmds.currentTime(frame, edit=True)
                cmds.setKeyframe(attribute_object.node)
    
    for frame in keyframes:
        cmds.currentTime(frame, edit=True)
        for attribute_path in attribute_paths:
            attribute_object = attribute_utils.Attribute(attribute_path)
            do_space_switch(attribute_object, value)
            continue


def do_space_switch(attribute_object, value):
    """
    Do space switch
    :param Attribute attribute_object: Attribute object
    """
    restore_matrix = cmds.xform(attribute_object.node, query=True, matrix=True, ws=True)
    attribute_object.set_value(value)
    cmds.xform(attribute_object.node, matrix=restore_matrix, ws=True)
    cmds.setKeyframe(attribute_object.node)
    

def get_keyframe_range(attribute_object, frame_range=None, keyed_frames=False, **kwargs):
    """
    Return a list of keyframes based on given frame_range string
    :param str range: options include current frame, selected frames, time slider range, animation range
    """
    node_keyframes = cmds.keyframe(attribute_object.node, query=True, timeChange=True)
    if not node_keyframes:
        node_keyframes = []
        
    node_keyframes = list(dict.fromkeys(node_keyframes))
    node_keyframes.sort()

    keyframe_range = []
        
    if frame_range == "Current Frame":
        keyframe_range.append(cmds.currentTime(query=True))

    if frame_range == "Selected Frames":
        for keyframe in range(int(timeline_utils.get_selected_key_range()[0]), int(timeline_utils.get_selected_key_range()[1])):
            if keyed_frames:
                if not float(keyframe) in node_keyframes:
                    continue
            keyframe_range.append(keyframe)
        
    if frame_range == "Time Slider Range":
        for keyframe in range(int(timeline_utils.get_playback_range()[0]), int(timeline_utils.get_playback_range()[1])+1):
            if keyed_frames:
                if not  float(keyframe) in node_keyframes:
                    continue
            keyframe_range.append(keyframe)
        
    if frame_range == "Animation Range":
        for keyframe in range(int(timeline_utils.get_animation_range()[0]), int(timeline_utils.get_animation_range()[1])+1):
            if keyed_frames:
                if not  float(keyframe) in node_keyframes:
                    continue
            keyframe_range.append(keyframe)
            
    if frame_range == "All Keyframes":
        keyframe_range = node_keyframes
        
    return keyframe_range