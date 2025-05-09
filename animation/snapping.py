"""
snapping scripts
"""
from maya import cmds


def snap_a_to_b(translation=True, rotation=True, scale=False):
    """
    snap first selected object to second selected object
    """
    selection = cmds.ls(selection=True)
    if len(selection) < 2:
        print("select 2 items to snap")
        return
    snap_to_node = selection[-1]
    for node in selection:
        if node == snap_to_node:
            return
        
        if translation:
            snap_to_matrix = cmds.xform(snap_to_node, query=True, translation=True, ws=True)
            cmds.xform(node, translation=list(snap_to_matrix), ws=True)
            
        if rotation:
            snap_to_matrix = cmds.xform(snap_to_node, query=True, rotation=True, ws=True)
            cmds.xform(node, rotation=list(snap_to_matrix), ws=True)
            
        if scale:
            snap_to_matrix = cmds.xform(snap_to_node, query=True, scale=True, ws=True)
            cmds.xform(node, scale=list(snap_to_matrix), ws=True)
