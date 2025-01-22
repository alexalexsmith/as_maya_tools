"""
snapping scripts
"""
from maya import cmds


def snap_a_to_b():
    """
    snap first selected object to second selected object
    """
    selection = cmds.ls(selection=True)
    if len(selection) != 2:
        print("select 2 items to snap")
        return
    a = selection[1]
    b = selection[0]
    copy_matrix = cmds.xform(a, query=True, matrix=True, ws=True)
    cmds.xform(b, matrix=list(copy_matrix), ws=True)