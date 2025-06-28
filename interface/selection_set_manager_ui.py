"""
User interface for managing rig selection options
"""
import os
try:
    from PySide2 import QtWidgets, QtCore, QtGui
    from shiboken2 import wrapInstance
except ModuleNotFoundError:
    from PySide6 import QtWidgets, QtCore, QtGui
    from shiboken6 import wrapInstance
    
    
from as_maya_tools.utilities.qt_utils import DockableMainWindowAbstract, TreeWidgetRightClickSupportAbstract
from as_maya_tools.utilities import selection_set_utils
from as_maya_tools import SELECTION_SET_DIRECTORY, STYLE_SHEETS_PATH


class CustomQFrame(QtWidgets.QFrame):
    """
    Custom QFrame with set style to keep my QFrames consistent
    """
    def __init__(self, parent=None):
        super(CustomQFrame, self).__init__(parent)
        self.setFrameStyle(QtWidgets.QFrame.StyledPanel | QtWidgets.QFrame.Plain)

        
class SelectionSetTreeView(TreeWidgetRightClickSupportAbstract):
    """
    Tree widget to display and manage attribute switching
    """
    
    HEADER_LABELS = ["Selection Sets"]
        
    def _pop_up_menu(self):
        """
        Create custom pop up menu
        """
        self.create_new_selection_set_action = self.popup_menu.addAction("Create A New Selection Set From Selection")
        self.add_to_existing_selection_set_action = self.popup_menu.addAction("Add Selected Nodes From Selected Selection Sets")
        self.remove_from_existing_selection_set_action = self.popup_menu.addAction("Remove Selected Nodes From Selected Selection Sets")
        self.select_nodes_action = self.popup_menu.addAction("Select Nodes From Selected Selection Sets")
        

class SelectionSetManagerUI(DockableMainWindowAbstract):
    """
    Noise Generation settings ui
    """
    WINDOW_NAME = "Selection Set Manager"

    Q_OBJECT_NAME = "selection_set_manager"
    
    #STYLE_SHEET_PATH = "{0}/mortarheadd.qss".format(STYLE_SHEETS_PATH)
    
    def __init__(self, parent=None):
        super(SelectionSetManagerUI, self).__init__(parent)
        

    def _ui(self):
        """
        UI to be built
        """
        # Frames, Groups and Layouts
        self.selection_set_file_management_layout = QtWidgets.QHBoxLayout(self)
        
        # Widgets
        self.set_file_combobox = QtWidgets.QComboBox(self)
        self.new_set_file_button = QtWidgets.QPushButton("New Set File",self)
        self.delete_set_file_button = QtWidgets.QPushButton("Delete Set File",self)
        self.selection_set_treeview = SelectionSetTreeView()
        
        # Connect UI
        # Upper Layout
        self.selection_set_file_management_layout.addWidget(self.set_file_combobox)
        self.selection_set_file_management_layout.addWidget(self.new_set_file_button)
        self.selection_set_file_management_layout.addWidget(self.delete_set_file_button)
        
        self.main_layout.addLayout(self.selection_set_file_management_layout)
        self.main_layout.addWidget(self.selection_set_treeview)
        
        self.setLayout(self.main_layout)
        
        
    def _callback_create_new_selectionset_file(self):
        """
        Create a new selection set file
        """
        return
        
    def _callback_delete_selectionset_file(self):
        """
        Delete selection set file
        """
        return