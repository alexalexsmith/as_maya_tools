"""
Rig selection tool for selecting predefined selection sets
selection set definitions are defined based on a specified {rig context} rig select definition file in the users
as_maya_tools data directory
"""
from maya import cmds

from as_maya_tools.utilities import rig_definition_utils, selection_set_utils, json_utils
from as_maya_tools import RIG_SELECTION_SETTINGS_PATH

# Temp selection set file name
TEMP_SELECTION_SET = "temp_selection_set"


def select_all(**kwargs):
    """
    select all rig controls
    """
    settings = _get_selection_settings()
    all_controls = rig_definition_utils.get_all_controls(**settings)
    _select_nodes(all_controls, **settings)
    return


def select_mirror(add=False, **kwargs):
    """
    select the controls on the opposite side of the rig
    :param bool add: option to add the selected controls to the current selection
    """
    settings = _get_selection_settings()
    mirror_controls = rig_definition_utils.get_mirror_controls(**settings)
    # clear selection if user doesn't want to add to selection
    if not add:
        cmds.select(clear=True)
    _select_nodes(mirror_controls, **settings)
    return


def select_set(**kwargs):
    """
    select all controls from the selection set the current selection belongs to
    """
    settings = _get_selection_settings()
    set_controls = rig_definition_utils.get_set_controls(**settings)
    _select_nodes(set_controls, **settings)
    return


def create_temp_selection_set(**kwargs):
    """
    create a temporary selection set based on the current selection
    """
    selection_set_utils.create_selection_set(file_name=TEMP_SELECTION_SET, **kwargs)
    return


def select_temp_selection_set(**kwargs):
    """
    select the temporary selection set if it exists
    """
    settings = _get_selection_settings()
    selection_set = selection_set_utils.get_selection_set(file_name=TEMP_SELECTION_SET, **kwargs)
    # I think clearing the current selection makes sense
    cmds.select(clear=True)
    _select_nodes(selection_set, **settings)
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
        

def _get_selection_settings():
    """
    Get selection settings file
    """
    settings = {}
    rig_selection_settings = json_utils.read_offset_json_file(RIG_SELECTION_SETTINGS_PATH, "rig_selection_settings")
    if rig_selection_settings:
        settings = rig_selection_settings
    return settings