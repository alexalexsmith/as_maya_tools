"""
quick scripts usually assigned to hotkeys to perform quick actions
"""
from maya import cmds

from as_maya_tools.utilities import constraint_utils


def create_locator_at_selected():
    """Create a locator at the current position of the selected object(s)"""
    selected_nodes = cmds.ls(selection=True)
    if not selected_nodes:
        return
    for selected_node in selected_nodes:
        locator = cmds.spaceLocator()
        selected_node_matrix = cmds.xform(selected_node, query=True, matrix=True, ws=True)
        cmds.xform(locator, matrix=list(selected_node_matrix), ws=True)


# TODO: I want to add options to exclude certain transform attributes, allowing for things like rolling in place
def lock_selected_in_place(rotation=True, location=True):
    """
    toggle lock and unlock selected controls in place. only works per frame
    :param bool rotation: Lock rotation
    :param bool location: Lock location
    """

    # remove lock in place
    if cmds.objExists("lock_in_place_locator"):
        constraints = constraint_utils.get_parent_connected_constraints("lock_in_place_locator")
        connected_controls = []
        for constraint in constraints:
            if constraint.child:
                connected_controls.append(constraint.child)

        if len(connected_controls) > 0:
            cmds.setKeyframe(connected_controls)
        cmds.delete("lock_in_place_locator")
        return

    # Create lock in place
    selection = cmds.ls(selection=True)
    lock_in_place_locator = cmds.spaceLocator(name="lock_in_place_locator")
    for item in selection:
        if rotation and location:
            constraint_utils.create_parent_constraint(
                parent=lock_in_place_locator,
                child=item,
                maintain_offset=True)
        if rotation and not location:
            constraint_utils.create_orient_constraint(
                parent=lock_in_place_locator,
                child=item,
                maintain_offset=True)
        if not rotation and location:
            constraint_utils.create_point_constraint(
                parent=lock_in_place_locator,
                child=item,
                maintain_offset=True)
                
                
def attach_locator_to_selection():
    """
    Attach a locator to the selected tranform or vertex
    """
    selection = cmds.ls(selection=True)
    for item in selection:
        locator = cmds.spaceLocator()[0]
        if ".vtx[" in item:
           cmds.select(item, replace=True)
           cmds.select(locator, add=True)
           cmds.pointOnPolyConstraint() 
           continue
        constraint_utils.create_parent_constraint(
                parent=item,
                child=locator,
                maintain_offset=False)
        
    
    
def create_mmv_offset_controls():
    """
    create a simple offset control rig. if objects are selected,they will be constrained to the end of the control rig
    """
    selection = cmds.ls(selection=True)
    ctrl_normal_direction = (0, 1, 0)
    main_ctrl = cmds.circle(name="mmv_offset_ctrl_01", nr=ctrl_normal_direction, r=4)
    second_ctrl = cmds.circle(name="mmv_offset_ctrl_02", nr=ctrl_normal_direction, r=3.5)
    end_ctrl = cmds.circle(name="mmv_offset_ctrl_03", nr=ctrl_normal_direction, r=3)
    cmds.parent(second_ctrl, main_ctrl)
    cmds.parent(end_ctrl, second_ctrl)
    if selection:
        for node in selection:
            constraint_utils.create_parent_constraint(
                parent=end_ctrl,
                child=node,
                maintain_offset=True)
            
            
def create_control():
    """
    attach a control for each selected object. control will follow object
    """
    selection = cmds.ls(selection=True)
    ctrl_normal_direction = (0, 1, 0)
    for node in selection:
        control_basename = node
        if ":" in control_basename:
            control_basename = node.split(":")[-1]
        control = cmds.circle(name="{0}_ctrl".format(control_basename), nr=ctrl_normal_direction, r=4)
        offset_group = cmds.group(control, name="{0}_offset".format(control_basename))
        constraint_utils.create_parent_constraint(
            parent=node,
            child=offset_group,
            maintain_offset=False)