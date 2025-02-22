"""
Utilities for managing constraints
"""

from maya import cmds

from as_maya_tools.utilities.decorators import set_pref_anim_blend_with_existing_connections


CONSTRAINT_TYPES = ("parentConstraint")


class Constraint(object):
    """
    class for managing a constraint node
    """
    def __init__(self, constraint_node):
        self.name = constraint_node
        self.type = cmds.nodeType(constraint_node)
        self.parents = None
        self.child = None
        self.pair_blend = None

        self._init_parents()
        self._init_child()
        self._init_pair_blend_node()

    def _init_parents(self):
        """init the parents of the constraint"""
        parent_list = []
        target_attribute = "{0}.target".format(self.name)
        parent_target_attribute = "targetMesh" if self.type == "pointOnPolyConstraint" else "targetParentMatrix"
        for target_index in range(cmds.getAttr(target_attribute, size=True)):

            target_attr_connection = cmds.listConnections(
                "{0}[{1}].{2}".format(target_attribute, target_index, parent_target_attribute),
                destination=False,
                source=True)

            if not target_attr_connection:
                continue

            parent_name = str(target_attr_connection[0])
            parent_list.append(ConstraintParent(parent_name, target_index))

        if parent_list:
            self.parents = parent_list

    def _init_child(self):
        """init the child of the constraint"""
        child_connection = "{0}.constraintParentInverseMatrix".format(self.name)
        if cmds.objExists(child_connection):
            children_list = cmds.listConnections(
                child_connection, destination=False, source=True
            )
            if children_list:
                self.child = children_list[0]

    def _init_pair_blend_node(self):
        """get the attached pair blend node if it exists"""
        constraint_connections = cmds.listConnections(self.name, skipConversionNodes=True)
        for connection in constraint_connections:
            if cmds.nodeType(connection) == "pairBlend":
                self.pair_blend = connection

    def delete(self):
        """Delete the constraint and any leftover nodes"""
        cmds.delete(self.name)
        if cmds.objExists(self.pair_blend):
            cmds.delete(self.pair_blend)


class ConstraintParent(object):
    """constraint parent object"""
    def __init__(self, node, index):
        """
        :param str node: name of parent node
        :param int index: target index
        """
        self.name = node
        self.index = index


def get_parent_connected_constraints(node):
    """
    return a list of connected constraints where the node is the parent
    :param str node: name of node to retrieve constraints from
    :return list [Constraint()]: list of connected constraints
    """
    # get a list of connected constraints where the node is the parent
    connections = cmds.listConnections(
        "{0}.parentMatrix".format(node),
        connections=True,
        plugs=False,
        type="parentConstraint"
    )
    # check the shape node for constraints as well
    shape = cmds.listRelatives(node, shapes=True, path=True)[0]
    if cmds.nodeType(shape) == "mesh":
        shape_node_connections = cmds.listConnections('{0}.worldMesh'.format(shape), connections=True, plugs=False)
        if shape_node_connections:
            connections = connections + shape_node_connections
            connections = set(connections)
            if '{0}.worldMesh'.format(shape) in connections:
                connections.remove('{0}.worldMesh'.format(shape))

    if '{0}.parentMatrix'.format(node) in connections:
        connections.remove('{0}.parentMatrix'.format(node))
    connected_constraints = []
    for item in set(connections):
        if cmds.nodeType(item) == "parentConstraint":
            connected_constraints.append(Constraint(item))
    return connected_constraints


def get_locked_transforms(item):
    """get locked transforms of passed item
    :param str item: name of object to check
    :return [list,list,list]: translate rotate and scale locked axis ex: ['tx','ty'],['ry'],['sx','sy','sz']"""
    locked_translate=[]
    locked_rotate=[]
    locked_scale = []
    attribute_lists = {"t":locked_translate, "r":locked_rotate, "s":locked_scale}

    for attribute in ["t","r","s"]:
        for axis in ["x","y","z"]:
            if cmds.getAttr("{0}.{1}{2}".format(item, attribute, axis),lock=True):
                attribute_lists[attribute].append(axis)

    return locked_translate, locked_rotate, locked_scale


def _handle_skip_attributes_per_child(child, skip_translate=[], skip_rotate=[], skip_scale=[]):
    """handle the skip attribute per child"""

    skip_translate_arg, skip_rotate_arg, skip_scale_arg = skip_translate[:], skip_rotate[:], skip_scale[:]

    locked_t, locked_r, locked_s = get_locked_transforms(child)
    for locked_attr, skip_attribute in zip((locked_t,locked_r,locked_s),(skip_translate_arg,skip_rotate_arg,skip_scale_arg)):
        for axis in locked_attr:
            if axis not in skip_attribute:
                skip_attribute.append(axis)
    return skip_translate_arg, skip_rotate_arg, skip_scale_arg

# Constraint Functions
@set_pref_anim_blend_with_existing_connections
def create_parent_constraint(parent=None, child=None, maintain_offset=True, skip_translate=[], skip_rotate=[], **kwargs):
    """create parent constraint
    :param str parent: parent of constraint
    :param str child: child of constraint
    :param bool maintain_offset: maintain current offset
    :param list skip_translate: translate attributes to skip
    :param list skip_rotate:rotate attributes to skip
    :return str constraint: constraint created"""
    skip_translate_arg, skip_rotate_arg, skip_scale_arg = _handle_skip_attributes_per_child(
        child,
        skip_translate=skip_translate,
        skip_rotate=skip_rotate)
    constraint = cmds.parentConstraint(parent,
                                       child,
                                       maintainOffset=maintain_offset,
                                       skipTranslate=skip_translate_arg,
                                       skipRotate=skip_rotate_arg)
    return constraint


@set_pref_anim_blend_with_existing_connections
def create_point_constraint(parent=None, child=None, maintain_offset=True, skip_translate=[], **kwargs):
    """create point constraint
    :param str parent: parent of constraint
    :param str child: child of constraint
    :param bool maintain_offset: maintain current offset
    :param list skip_translate: translate attributes to skip
    :return str constraint: constraint created"""
    skip_translate_arg, skip_rotate_arg, skip_scale_arg = _handle_skip_attributes_per_child(
        child,
        skip_translate=skip_translate)
    constraint = cmds.pointConstraint(parent, child, maintainOffset=maintain_offset, skip=skip_translate_arg)

    return constraint


@set_pref_anim_blend_with_existing_connections
def create_orient_constraint(parent=None, child=None, maintain_offset=True, skip_rotate=[], **kwargs):
    """create orient constraint
    :param str parent: parent of constraint
    :param str child: child of constraint
    :param bool maintain_offset: maintain current offset
    :param list skip_rotate:rotate attributes to skip
    :return str constraint: constraint created"""
    skip_translate_arg, skip_rotate_arg, skip_scale_arg = _handle_skip_attributes_per_child(
        child,
        skip_rotate=skip_rotate)
    constraint = cmds.orientConstraint(parent, child, maintainOffset=maintain_offset, skip=skip_rotate_arg)

    return constraint


@set_pref_anim_blend_with_existing_connections
def create_scale_constraint(parent=None, child=None, maintain_offset=True, skip_scale=[], **kwargs):
    """create scale constraint
    :param str parent: parent of constraint
    :param str child: child of constraint
    :param bool maintain_offset: maintain current offset
    :param list skip_scale: scale attributes to skip
    :return str constraint: constraint created"""
    skip_translate_arg, skip_rotate_arg, skip_scale_arg = _handle_skip_attributes_per_child(
        child,
        skip_scale=skip_scale)
    constraint = cmds.scaleConstraint(parent, child, maintainOffset=maintain_offset, skip=skip_scale_arg)

    return constraint


@set_pref_anim_blend_with_existing_connections
def create_aim_constraint(parent=None, child=None, maintain_offset=True, skip_rotate=[], **kwargs):
    """create scale constraint
    :param str parent: parent of constraint
    :param str child: child of constraint
    :param bool maintain_offset: maintain current offset
    :param list skip_rotate: scale attributes to skip
    :return str constraint: constraint created"""
    skip_translate_arg, skip_rotate_arg, skip_scale_arg = _handle_skip_attributes_per_child(
        child,
        skip_scale=skip_rotate)
    constraint = cmds.aimConstraint(parent, child, maintainOffset=maintain_offset, skip=skip_rotate_arg)

    return constraint