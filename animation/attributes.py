"""
attribute scripts
"""
from maya import cmds
from as_maya_tools.utilities.attribute_utils import Transform, Attribute


def reset_transforms():
    """
    set all transformation to default
    """
    selected_nodes = cmds.ls(selection=True)
    if not selected_nodes:
        return
    for selected_node in selected_nodes:
        node = Transform(selected_node)
        for attribute in (node.translate + node.rotate + node.scale):
            if not attribute.is_keyable():
                continue
            attribute.set_value(attribute.get_default_value())
    return


def reset_translation():
    """
    set translation attributes to default
    """
    selected_nodes = cmds.ls(selection=True)
    if not selected_nodes:
        return
    for selected_node in selected_nodes:
        node = Transform(selected_node)
        for attribute in node.translate:
            if not attribute.is_keyable():
                continue
            attribute.set_value(attribute.get_default_value())
    return


def reset_rotation():
    """
    set rotation attributes to default
    """
    selected_nodes = cmds.ls(selection=True)
    if not selected_nodes:
        return
    for selected_node in selected_nodes:
        node = Transform(selected_node)
        for attribute in node.rotate:
            if not attribute.is_keyable():
                continue
            attribute.set_value(attribute.get_default_value())
    return


def reset_scale():
    """
    set scale attributes to default
    """
    selected_nodes = cmds.ls(selection=True)
    if not selected_nodes:
        return
    for selected_node in selected_nodes:
        node = Transform(selected_node)
        for attribute in node.scale:
            if not attribute.is_keyable():
                continue
            attribute.set_value(attribute.get_default_value())
    return


def reset_selected_attributes():
    """set selected attributes to default"""
    selected_nodes = cmds.ls(selection=True)
    if not selected_nodes:
        return
    selected_attr = cmds.channelBox('mainChannelBox', query=True, selectedMainAttributes=True)
    for attribute in selected_attr:
        for selected_node in selected_nodes:
            attribute_object = Attribute("{0}.{1}".format(selected_node, attribute))

            if not cmds.objExists(attribute_object):
                continue
            attribute_object.set_value(attribute_object.get_default_value())
