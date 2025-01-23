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


def lock_selected_in_place():
    """toggle lock and unlock selected controls in place. only works per frame"""

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
        constraint_utils.create_parent_constraint(
            parent=lock_in_place_locator,
            child=item,
            maintain_offset=True)
