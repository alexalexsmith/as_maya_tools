"""
Utilities for creating, updating and managing selection sets
"""
import os

from maya import cmds

from as_maya_tools.utilities import json_utils, performance_utils
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
            namespace, name = node.rsplit(":", 1)
        data[node] = {"namespace": namespace, "name": name}
    directory = SELECTION_SET_DIRECTORY
    if sub_folder:
        directory = os.path.join(directory, sub_folder)
    json_utils.write_json_file(directory, file_name, data)


def delete_selection_set(sub_folder=None, file_name="selection_set", **kwargs):
    """
    delete the selection set .json file
    """
    directory = SELECTION_SET_DIRECTORY
    if sub_folder:
        directory = os.path.join(directory, sub_folder)
    file_path = os.path.join(directory, "{0}.json".format(file_name))
    if os.path.exists(file_path):
        os.remove(file_path)


def get_selection_set(
        sub_folder=None,
        file_name="selection_set",
        use_file_namespace=False,
        use_selected_namespace=True,
        use_scene_namespace=False,
        scene_namespace="",
        search_and_replace=False,
        search_string="",
        replace_string="",
        **kwargs):
    """
    Returns list of nodes from the given selection set
    :param str sub_folder: Sub-folder within the selection set directory
    :param str file_name: Name of the selection set
    :param bool use_selected_namespace: option to use the namespace of selected nodes
    :param str scene_namespace: namespace to overide stored namespace 
    """
    directory = SELECTION_SET_DIRECTORY
    if sub_folder:
        directory = os.path.join(directory, sub_folder)
    selection_set_data = json_utils.read_offset_json_file(directory, file_name)

    namespaces = None
    if use_scene_namespace:
            namespaces = [scene_namespace]

    if use_selected_namespace:
        selected_nodes = cmds.ls(selection=True)
        namespaces = get_namespaces_from_nodes(selected_nodes)

    selection_set = []
    for node in selection_set_data:

        # storing nodes base name for search and replace. for now only using replace on base name
        name_space = selection_set_data[node]["namespace"]
        node_base_name = selection_set_data[node]["name"]
        if search_and_replace:
            node_base_name = node_base_name.replace(search_string, replace_string)

        # adding any nodes without a namespace first
        if not name_space:
            # Any nodes in the selection set without a namespace are added directly, If they currently exist
            if performance_utils.obj_exists(node_base_name):
                selection_set.append(node_base_name)
            continue

        # rebuilding node name with namespace if namespaces are supplied
        if namespaces:
            # Replace stored namespace with selected nodes namespaces
            for namespace in namespaces:
                # Rebuild the control name with the namespaces of selected nodes
                rebuilt_name = "{0}:{1}".format(namespace, node_base_name)
                # Only add the node if it currently exists
                if performance_utils.obj_exists(rebuilt_name):
                    selection_set.append(rebuilt_name)
        else:
            # Use the stored namespace if no nodes with namespaces are selected
            rebuilt_node_name = f"{name_space}:{node_base_name}"
            # Only add the node if it currently exists
            if performance_utils.obj_exists(rebuilt_node_name):
                selection_set.append(rebuilt_node_name)
    return selection_set


def get_namespaces_from_nodes(nodes):
    """
    return a list of namespaces associated with the given nodes. return None if no namespaces are found
    """
    namespaces = []
    for node in nodes:
        if ":" in node:
            namespace, _ = node.rsplit(":", 1)
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
        
    