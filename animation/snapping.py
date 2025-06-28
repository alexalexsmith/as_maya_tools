"""
snapping scripts
"""
from maya import cmds
from as_maya_tools.utilities import xform_utils


def snap_a_to_b(translation=True, rotation=True, scale=False, **kwargs):
    """
    snap first selected object to second selected object
    """
    selection = cmds.ls(selection=True)
    if len(selection) < 2:
        print("select 2 items to snap")
        return
    b = selection[-1]
    for a in selection:
        if a == b:
            return
        xform_utils.snap_a_to_b(a, b, translation=translation, rotation=rotation, scale=scale, **kwargs)

