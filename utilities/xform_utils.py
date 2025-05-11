"""
xform utilities
"""
from maya import cmds

from as_maya_tools.utilities import attribute_utils


def snap_a_to_b(a, b, translation=True, rotation=True, scale=False):
    """
    Snap node a to node b world position
    :param string a: name of node
    :param string b: name of node
    :param bool translation: option to match translation
    :param bool rotation: option to match rotation
    :param bool scale: option to match scale
    """
    if translation:
        b_transform_pos = cmds.xform(b, query=True, translation=True, ws=True)
        cmds.xform(a, translation=list(b_transform_pos), ws=True)

    if rotation:
        b_rotation_pos = cmds.xform(b, query=True, rotation=True, ws=True)
        cmds.xform(a, rotation=list(b_rotation_pos), ws=True)

    if scale:
        b_scale_pos = cmds.xform(b, query=True, scale=True, ws=True)
        cmds.xform(a, scale=list(b_scale_pos), ws=True)
