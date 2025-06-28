"""
Functions that speed up maya or replace maya cmds for better performance
"""

import maya.api.OpenMaya as OpenMaya
from maya import cmds



def obj_exists(name):
    """
    check if an object, plug, attribute path exists in the current maya scene
    :param str name: name of node, plug, or attribute path
    :return bool: exists
    """
    selection = OpenMaya.MSelectionList()
    try:
        selection.add(name)
        return True
    except RuntimeError:
        return False
        
        
def message(message, position='midCenterTop', record_warning=True):
    """
    A nicer way to display messages to the user
    :param str message: text to display to user
    :param str position: The position that the message will appear at relative to the active viewport. The supported positions are:
                            "topLeft"
                            "topCenter"
                            "topRight"
                            "midLeft"
                            "midCenter"
                            "midCenterTop"
                            "midCenterBot"
                            "midRight"
                            "botLeft"
                            "botCenter"
                            "botRight"
    :param bool record_warning: Option to record the warning in the script output
    """
    
    OpenMaya.MGlobal.displayWarning(message)
    fadeTime = min(len(message)*100, 2000)
    cmds.inViewMessage( amg=message, pos=position, fade=True, fadeStayTime=fadeTime, dragKill=True)
    if record_warning:
        cmds.warning(message)