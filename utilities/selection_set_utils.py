"""
Utilities for creating, updating and managing selection sets
"""
import os

from maya import cmds

from as_maya_tools.utilities import json_utils
from as_maya_tools import SELECTION_SET_DIRECTORY


def create_selection_set(sub_folder=None, file_name="selection_set", **kwargs):
    """
    Create a new selection set with the given name.
    :param sub_folder: Sub-folder within the selection set directory
    :param file_name: Name of the selection set
    """
    selected_nodes = cmds.ls(selection=True)
    if not selected_nodes or len(selected_nodes) == 0:
        print("No nodes selected. Selection set was not created.")
        return
    data = {}
    for node in selected_nodes:
        name = node
        namespace = None
        if ":" in node:
            namespace, name = node.split(":")
        data[node] = {"namespace": namespace, "name": name}
    directory = SELECTION_SET_DIRECTORY
    if sub_folder:
        directory = os.path.join(directory, sub_folder)
    json_utils.write_json_file(directory, file_name, data)


def create_selection_set_file():
    """
    create selection set file to store selection sets
    """
    return
    
    
def create_selection_set_data():
    """
    create selection set data to store in a selection set file
    """
    return


def get_selection_set(sub_folder=None, file_name="selection_set", **kwargs):
    """
    Returns list of nodes from the given selection set
    :param sub_folder: Sub-folder within the selection set directory
    :param file_name: Name of the selection set
    """
    directory = SELECTION_SET_DIRECTORY
    if sub_folder:
        directory = os.path.join(directory, sub_folder)
    selection_set_data = json_utils.read_offset_json_file(directory, file_name)
    selected_nodes = cmds.ls(selection=True)
    namespaces = get_namespaces_from_nodes(selected_nodes)
    selection_set = []
    for node in selection_set_data:
        if not selection_set_data[node]["namespace"]:
            # Any nodes in the selection set without a namespace are added directly, If they currently exist
            if cmds.objExists(node):
                selection_set.append(node)
            continue
        if namespaces:
            # Replace stored namespace with selected nodes namespaces
            for namespace in namespaces:
                # Rebuild the control name with the namespaces of selected nodes
                rebuilt_name = "{0}:{1}".format(namespace, selection_set_data[node]["name"])
                # Only add the node if it currently exists
                if cmds.objExists(rebuilt_name):
                    selection_set.append(rebuilt_name)
        else:
            # Use the stored namespace if no nodes with namespaces are selected
            # Only add the node if it currently exists
            if cmds.objExists(node):
                selection_set.append(node)
    return selection_set


def get_namespaces_from_nodes(nodes):
    """
    return a list of namespaces associated with the given nodes. return None if no namespaces are found
    """
    namespaces = []
    for node in nodes:
        if ":" in node:
            namespace, _ = node.split(":")
            namespaces.append(namespace)
    return namespaces if len(namespaces) > 0 else None
    
    
class SelectionSetFile(object):
    """
    Class for managing selection set files and their data
    """
    
    def __init__(self, file_path):
        """
        init the selection set file
        :param str file_path: path for selection set file 
        """
        self.file_path = file_path
        
    def create_file(self):
        """
        create the selection set file
        """
        directory = os.path.join(directory, sub_folder)
        json_utils.write_json_file(directory, file_name, data)
        
        return
        
    def delete_file(self):
        """
        delete the selection set file
        """
        
    def create_selection_set(self, selection_set):
        """
        Create a selection set
        :param str selection_set: name of selection set to create
        """
        
    def delete_selection_set(self, selection_set):
        """
        Create a selection set
        :param str selection_set: name of selection set to create
        """
        
    def add_selected_nodes_to_selection_set(self, selection_set):
        """
        Add nodes selected in viewport to passed selection set
        :param str selection_set: name of selection set to add to
        """
        
    def remove_selected_nodes_to_selection_set(self, selection_set):
        """
        Remove nodes selected in viewport to passed selection set
        :param str selection_set: name of selection set to add to
        """
        
    