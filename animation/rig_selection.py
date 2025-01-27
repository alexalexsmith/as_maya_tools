"""
Rig selection tool for selecting predefined selection sets
selection set definitions are defined based on a specified {rig context} rig select definition file in the users
as_maya_tools data directory
"""
from maya import cmds

from as_maya_tools.utilities import rig_select_utils


def select_all(**kwargs):
    """
    select all rig controls
    """
    all_controls = rig_select_utils.get_all_controls(**kwargs)
    _select_nodes(all_controls, **kwargs)
    return


def select_mirror(add=False, **kwargs):
    """
    select the controls on the opposite side of the rig
    :param bool add: option to add the selected controls to the current selection
    """
    mirror_controls = rig_select_utils.get_mirror_controls(**kwargs)
    # clear selection if user doesn't want to add to selection
    if not add:
        cmds.select(clear=True)
    _select_nodes(mirror_controls, **kwargs)
    return


def select_set(**kwargs):
    """
    select all controls from the selection set the current selection belongs to
    """
    set_controls = rig_select_utils.get_set_controls(**kwargs)
    _select_nodes(set_controls, **kwargs)
    return


def create_temp_selection_set(**kwargs):
    """
    create a temporary selection set based on the current selection
    """
    return


def select_temp_selection_set(**kwargs):
    """
    select the temporary selection set if it exists
    """
    return


def _select_nodes(nodes, visible=False, **kwargs):
    """
    select items in the scene
    :param nodes: list of nodes to select
    :param visible: option to select only visible controls
    """
    # checks to avoid attempting to select empty list
    if not nodes:
        print("node selection list is empty")
        return
    if len(nodes) == 0:
        print("node selection list is 0")
        return
    # remove duplicates in list of nodes
    nodes = set(nodes)
    if visible:
        cmds.select(nodes, add=True, visible=True)
    else:
        cmds.select(nodes, add=True)
