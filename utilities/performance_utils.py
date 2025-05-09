"""
Functions that speed up maya or replace maya cmds with better performance
"""

import maya.api.OpenMaya as OpenMaya



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