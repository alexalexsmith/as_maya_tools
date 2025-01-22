"""
Utilities for managing attributes
"""
from maya import cmds


class Transform(object):
    def __init__(self, transform_node):
        self.transform_node = transform_node

        self.translate_x = Attribute("{0}.tx".format(transform_node))
        self.translate_y = Attribute("{0}.ty".format(transform_node))
        self.translate_z = Attribute("{0}.tz".format(transform_node))

        self.rotate_x = Attribute("{0}.rx".format(transform_node))
        self.rotate_y = Attribute("{0}.ry".format(transform_node))
        self.rotate_z = Attribute("{0}.rz".format(transform_node))

        self.scale_x = Attribute("{0}.sx".format(transform_node))
        self.scale_y = Attribute("{0}.sy".format(transform_node))
        self.scale_z = Attribute("{0}.sz".format(transform_node))

        self.visibility = Attribute("{0}.v".format(transform_node))

        self.translate = [self.translate_x, self.translate_y, self.translate_z]
        self.rotate = [self.rotate_x, self.rotate_y, self.rotate_z]
        self.scale = [self.scale_x, self.scale_y, self.scale_z]


class Attribute(object):
    def __init__(self, attribute_path):
        self.attribute_path = attribute_path
        self.node, self.attribute = attribute_path.split(".")
        self.type = cmds.getAttr(attribute_path, type=True)
        self.value = cmds.getAttr(attribute_path)

    def is_selected(self):
        """
        Get if the attribute is selected in the mainChannelBox
        NOTE: if the node that owns the attribute is not selected at the time of execution, this method not work as expected
        """
        selected_attributes = cmds.channelBox('mainChannelBox', query=True, selectedMainAttributes=True)
        if not selected_attributes:
            return False
        if self.attribute in selected_attributes:
            return True
        return False

    def is_keyable(self):
        return cmds.getAttr(self.attribute_path, keyable=True)

    def get_default_value(self):
        """
        return the default value.
        NOTE: This cmd returns a list. using [0] to return a single value
        """
        return cmds.attributeQuery(self.attribute, node=self.node, listDefault=True)[0]

    def set_value(self, value):
        cmds.setAttr(self.attribute_path, value)
