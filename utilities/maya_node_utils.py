"""
Utilities for managing maya nodes
"""
from maya import cmds

from as_maya_tools.utilities import performance_utils


class MayaNode(object):
    """Maya node class"""

    def __init__(self, node=None, *args, **kwargs):
        self.long_name = None
        self.namespace = None
        self.short_name = None
        self.shape = None
        self.visibility = None
        self._init_maya_node(node)

    def _init_maya_node(self, node):
        """init the maya node name
        :param str node: name of node"""
        transform = cmds.ls(node, long=True)[0]
        shape = None
        if cmds.objectType(transform) == "transform":
            # some nodes don't have a shape node under them
            test_shape = cmds.listRelatives(node, shapes=True)
            if test_shape:
                shape = test_shape[0]
        # Joints are very "special"
        elif cmds.objectType(transform) == "joint":
            pass
        elif cmds.objectType(transform) == "parentConstraint":
            pass
        else:
            # Some non transform nodes don't have a transform node above them (Nucleus),
            # I will handle those as a transform for simplicity
            test_transform = cmds.listRelatives(node, parent=True, fullPath=True)
            if test_transform:
                shape = node
                transform = test_transform[0]
        self.long_name = transform
        if ":" in self.long_name.split("|")[-1]:
            self.namespace = self.long_name.split("|")[-1].rsplit(":", 1)[0]
            self.short_name = self.long_name.split("|")[-1].rsplit(":", 1)[1]
        else:
            self.short_name = self.long_name.split("|")[-1]
        self.shape = shape

    def select(self):
        """select the node in viewport"""
        cmds.select(self.long_name, replace=True)

    def delete_node(self):
        """delete the node if it exists"""
        if self.long_name:
            if performance_utils.obj_exists(self.long_name):
                cmds.delete(self.long_name)

    def get_attribute(self, attribute, shape=False):
        """get the full path of the attribute. useful when setting and connection attributes
        :param str attribute: name of attribute
        :param bool shape: whether attribute belongs to shape
        :return str: full path of attribute"""
        node_name = self.long_name
        if shape:
            node_name = self.shape
        return "{0}.{1}".format(node_name, attribute)

    def set_parent(self, maya_node):
        """set the parent of this MayaNode
        :param MayaNode maya_node: node to set as parent"""
        new_name = cmds.parent(self.long_name, maya_node.long_name)
        #  update the long name to match the new path name
        self.long_name = cmds.ls(new_name, long=True)[0]
        return self

    def set_name(self, name):
        """set the name of the node
        :param str name: new name"""
        new_name = cmds.rename(self.long_name, name)
        self._init_maya_node(new_name)  # need to re init this node after name change

    def set_visible(self, option):
        """set the visibility
        :param bool option: set visible or not"""
        cmds.setAttr("{0}.visibility".format(self.long_name), option)

    def set_translation(self, translation):
        """set the translation of this node
        :param tuple(float, float, float) translation: translation position to set"""
        cmds.xform(self.long_name, translation=translation, worldSpace=True)
        return

    def refresh_name(self):
        """used to refresh the name if the long name is updated due to hierarchy change"""
        if cmds.objExists(self.long_name):
            return self
        self.long_name = cmds.ls(self.short_name, long=True)[0]
        return self