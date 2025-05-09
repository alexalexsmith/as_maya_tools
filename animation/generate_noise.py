"""
Generate noise on animation
"""
import random

from maya import cmds

from as_maya_tools.utilities import keyframe_utils, random_utils, json_utils
from as_maya_tools import NOISE_GENERATION_SETTINGS_PATH


ATTRIBUTES = ["translateX","translateY","translateZ","rotateX","rotateY","rotateZ","scaleX","scaleY","scaleZ"]


# get selected keys and attributes
def generate_noise_on_selection():
    """
    Generate noise animation on selected objects, uses selected attributes if attributes are selected in channelBox
    """
    # getting only selected nodes
    nodes = cmds.ls(selection=True)
    if nodes is None:
        print("nothing selected")
        return
    
    # get any selected attributes, else use all transform attributes as default 
    attributes = cmds.channelBox('mainChannelBox', query=True, selectedMainAttributes=True)
    if attributes is None:
        attributes = ATTRIBUTES
        
    settings = _get_noise_settings()
    
    # get keyframes to generate keys on
    keyframes = keyframe_utils.get_keyframe_list(**settings)
    
    # generate random animation
    random_utils.generate_noise_on_attributes(nodes, attributes, keyframes, **settings)
                
                
def _get_noise_settings():
    """
    Get selection settings file
    """
    settings = {}
    rig_selection_settings = json_utils.read_offset_json_file(NOISE_GENERATION_SETTINGS_PATH, "noise_generation_settings")
    if rig_selection_settings:
        settings = rig_selection_settings
        
    return settings