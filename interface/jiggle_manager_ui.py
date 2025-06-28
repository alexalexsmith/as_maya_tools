"""
Create and manage jiggle rigs user interface
"""

try:
    from PySide2 import QtWidgets, QtCore, QtGui
    from shiboken2 import wrapInstance
except ModuleNotFoundError:
    from PySide6 import QtWidgets, QtCore, QtGui
    from shiboken6 import wrapInstance

from as_maya_tools.utilities.qt_utils import DockableMainWindowAbstract, TreeWidgetRightClickSupportAbstract
from as_maya_tools.utilities import jiggle_utils
from as_maya_tools import SELECTION_SET_DIRECTORY, STYLE_SHEETS_PATH


class CustomQFrame(QtWidgets.QFrame):
    """
    Custom QFrame with set style to keep my QFrames consistent
    """
    def __init__(self, parent=None):
        super(CustomQFrame, self).__init__(parent)
        self.setFrameStyle(QtWidgets.QFrame.StyledPanel | QtWidgets.QFrame.Plain)

        
class JiggleRigsTreeView(TreeWidgetRightClickSupportAbstract):
    """
    Tree widget to display and manage attribute switching
    """
    
    HEADER_LABELS = ["Jiggle Rigs"]
        
    def _pop_up_menu(self):
        """
        Create custom pop up menu
        """
        self.create_new_jiggle_rig_action = self.popup_menu.addAction("Create Jiggle Rig")
        self.delete_jiggle_rig_action = self.popup_menu.addAction("Delete Jiggle Rig")
        self.bake_jiggle_rigs_action = self.popup_menu.addAction("Bake Jiggle Rig")
        self.select_jiggle_rig_action = self.popup_menu.addAction("Select Jiggle Rig")
        

class JiggleRigsManagerUI(DockableMainWindowAbstract):
    """
    Noise Generation settings ui
    """
    WINDOW_NAME = "Jiggle Rig Manager"

    Q_OBJECT_NAME = "jiggle_rigs_manager"
    
    #STYLE_SHEET_PATH = "{0}/mortarheadd.qss".format(STYLE_SHEETS_PATH)
    
    def __init__(self, parent=None):
        super(JiggleRigsManagerUI, self).__init__(parent)
        
        self._refresh_jiggle_rig_treeview()
        

    def _ui(self):
        """
        UI to be built
        """
        # Frames, Groups and Layouts
        self.creation_deletion_management_layout = QtWidgets.QHBoxLayout(self)
        
        # Widgets
        self.create_new_jiggle_rig = QtWidgets.QPushButton("Create Jiggle Rig",self)
        self.delete_jiggle_rig = QtWidgets.QPushButton("Delete Jiggle Rig",self)
        self.bake_jiggle_rig = QtWidgets.QPushButton("Bake Jiggle Rig",self)
        self.jiggle_rigs_treeview = JiggleRigsTreeView()
        
        # Connect UI
        # Upper Layout
        self.creation_deletion_management_layout.addWidget(self.create_new_jiggle_rig)
        self.creation_deletion_management_layout.addWidget(self.delete_jiggle_rig)
        self.creation_deletion_management_layout.addWidget(self.bake_jiggle_rig)
        
        self.main_layout.addLayout(self.creation_deletion_management_layout)
        self.main_layout.addWidget(self.jiggle_rigs_treeview)
        
        self.setLayout(self.main_layout)
        
        
    def _refresh_jiggle_rig_treeview(self):
        """
        List all jiggle rigs in the scene
        """
        jiggle_rigs = jiggle_utils.get_all_jiggle_rigs()
        self.jiggle_rigs_treeview.clear()
        for jiggle_rig in jiggle_rigs:
                jiggle_rig_item_widget = QtWidgets.QTreeWidgetItem([jiggle_rig, 0])
                self.jiggle_rigs_treeview.addTopLevelItem(jiggle_rig_item_widget)
        return
        
    def _setup_socket_connections(self):
        """
        setup socket connections
        """
        self.create_new_jiggle_rig.pressed.connect(self._callback_create_jiggle_rig)
        self.delete_jiggle_rig.pressed.connect(self._callback_delete_jiggle_rig)
        self.bake_jiggle_rig.pressed.connect(self._callback_bake_jiggle_rigs)
        
        self.jiggle_rigs_treeview.itemSelectionChanged.connect(self._callback_select_jiggle_rigs)
        
        self.jiggle_rigs_treeview.create_new_jiggle_rig_action.triggered.connect(self._callback_create_jiggle_rig)
        self.jiggle_rigs_treeview.delete_jiggle_rig_action.triggered.connect(self._callback_delete_jiggle_rig)
        self.jiggle_rigs_treeview.select_jiggle_rig_action.triggered.connect(self._callback_select_jiggle_rigs)
        self.jiggle_rigs_treeview.bake_jiggle_rigs_action.triggered.connect(self._callback_bake_jiggle_rigs)
        
    
    def _callback_create_jiggle_rig(self):
        """
        Create a new selection set file
        """
        jiggle_utils.create_jiggle_rig_from_selection(require_translation=False, require_rotation=False)
        self._refresh_jiggle_rig_treeview()
        return
        
    def _callback_delete_jiggle_rig(self):
        """
        Delete selection set file
        """
        selected_jiggle_rigs = self._get_selected_jiggle_rigs_from_tree_view()
        jiggle_utils.delete_jiggle_rigs(selected_jiggle_rigs)
        self._refresh_jiggle_rig_treeview()
        return
        
    def _callback_select_jiggle_rigs(self):
        """
        Select jiggle rigs
        """
        selected_jiggle_rigs = self._get_selected_jiggle_rigs_from_tree_view()
        jiggle_utils.select_jiggle_rigs(selected_jiggle_rigs)
        return
        
    def _callback_bake_jiggle_rigs(self):
        """
        Bake jiggle rigs
        """
        selected_jiggle_rigs = self._get_selected_jiggle_rigs_from_tree_view()
        jiggle_utils.bake_jiggle_rigs(selected_jiggle_rigs)
        self._refresh_jiggle_rig_treeview()
        return
        
    def _get_selected_jiggle_rigs_from_tree_view(self):
        """Get a list of names from the tree view selection
        :return: constraint_names
        :rtype: list[str]
        """
        jiggle_rigs = list()
        for item in self.jiggle_rigs_treeview.selectedItems():
            jiggle_rigs.append(item.text(0))
        return jiggle_rigs