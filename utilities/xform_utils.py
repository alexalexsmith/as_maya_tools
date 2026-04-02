"""
xform utilities
"""
from maya import cmds

from as_maya_tools.utilities import attribute_utils


def snap_a_to_b(a, b, translation=True, rotation=True, scale=False, **kwargs):
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
        


def snap_to_first(
                    nodes,
                    translate_x=True, 
                    translate_y=True, 
                    translate_z=True, 
                    rotate_x=True, 
                    rotate_y=True, 
                    rotate_z=True, 
                    scale_x=False, 
                    scale_y=False, 
                    scale_z=False, 
                    **kwargs):
    """
    Snap all selected nodes to the first selection
    :param scale_x:
    :param scale_y:
    :param scale_z:
    :param rotate_x:
    :param rotate_y:
    :param rotate_z:
    :param translate_x:
    :param translate_y:
    :param translate_z:
    :param list[str] nodes: list of node names
    """
    snap_node = nodes[0]
    translation_vector = cmds.xform(snap_node, query=True, translation=True, ws=True)
    rotation_vector = cmds.xform(snap_node, query=True, rotation=True, ws=True)
    scale_vector = cmds.xform(snap_node, query=True, scale=True, ws=True)
    for node in nodes:
        if node == snap_node:
            continue
            
        # Translation Vector swap
        if not translate_x:
            node_translation_vector = cmds.xform(node, query=True, translation=True, ws=True)
            translation_vector[0] = node_translation_vector[0]
        if not translate_y:
            node_translation_vector = cmds.xform(node, query=True, translation=True, ws=True)
            translation_vector[1] = node_translation_vector[1]
        if not translate_z:
            node_translation_vector = cmds.xform(node, query=True, translation=True, ws=True)
            translation_vector[2] = node_translation_vector[2]
            
        # Rotation Vector swap
        if not rotate_x:
            node_rotation_vector = cmds.xform(node, query=True, rotation=True, ws=True)
            rotation_vector[0] = node_rotation_vector[0]
        if not rotate_y:
            node_rotation_vector = cmds.xform(node, query=True, rotation=True, ws=True)
            rotation_vector[1] = node_rotation_vector[1]
        if not rotate_z:
            node_rotation_vector = cmds.xform(node, query=True, rotation=True, ws=True)
            rotation_vector[2] = node_rotation_vector[2]
            
        # Scale Vactor snap
        if not scale_x:
            node_scale_vector = cmds.xform(node, query=True, scale=True, ws=True)
            scale_vector[0] = node_scale_vector[0]
        if not scale_y:
            node_scale_vector = cmds.xform(node, query=True, scale=True, ws=True)
            scale_vector[1] = node_scale_vector[1]
        if not scale_z:
            node_scale_vector = cmds.xform(node, query=True, scale=True, ws=True)
            scale_vector[2] = node_scale_vector[2]
        
        # Snap Translation
        if translate_x or translate_y or translate_z:
            cmds.xform(a, translation=list(translation_vector), ws=True)
            
        # Snap Rotation
        if rotate_x or rotate_y or rotate_z:
            cmds.xform(a, rotation=list(rotation_vector), ws=True)
        
        # Snap Scale
        if scale_x or scale_y or scale_z:
            cmds.xform(a, scale=list(scale_vector), ws=True)