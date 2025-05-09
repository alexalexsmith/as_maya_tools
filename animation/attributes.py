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
    selected_attributes = cmds.channelBox('mainChannelBox', query=True, selectedMainAttributes=True)
    for attribute in selected_attributes:
        for selected_node in selected_nodes:
            attribute_object = Attribute("{0}.{1}".format(selected_node, attribute))
            print(attribute_object.attribute_path)
            if not cmds.objExists(attribute_object.attribute_path):
                continue
            attribute_object.set_value(attribute_object.get_default_value())
            
            
def reset_keyable_attributes():
    """set selected attributes to default"""
    selected_nodes = cmds.ls(selection=True)
    if not selected_nodes:
        return
    for selected_node in selected_nodes:
        keyable_attributes = cmds.listAttr(selected_node ,keyable=True, unlocked=True)
        if not keyable_attributes:
            continue
        for attribute in keyable_attributes:
            attribute_object = Attribute("{0}.{1}".format(selected_node, attribute))

            if not cmds.objExists(attribute_object.attribute_path):
                continue
            attribute_object.set_value(attribute_object.get_default_value())