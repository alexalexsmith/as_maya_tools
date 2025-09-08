"""
Create and manage jiggle rigs user interface
"""

try:
    from PySide2 import QtWidgets, QtCore, QtGui
    from shiboken2 import wrapInstance
except ModuleNotFoundError:
    from PySide6 import QtWidgets, QtCore, QtGui
    from shiboken6 import wrapInstance

from maya import cmds

from as_maya_tools.utilities.qt_utils import DockableMainWindowAbstract, TreeWidgetRightClickSupportAbstract
from as_maya_tools.utilities import jiggle_utils, timeline_utils
from as_maya_tools import SELECTION_SET_DIRECTORY, STYLE_SHEETS_PATH
from as_maya_tools.stylesheets import guiResources
        
        
class SquareButton(QtWidgets.QPushButton):
    def resizeEvent(self, event):
        # Force the button to be square (width = height)
        size = min(self.width(), self.height())
        self.setFixedSize(QtCore.QSize(size, size))
        super().resizeEvent(event)

        
class JiggleRigsTreeView(TreeWidgetRightClickSupportAbstract):
    """
    Tree widget to display and manage attribute switching
    """
    
    HEADER_LABELS = ["Active","Name"]
        
    def _pop_up_menu(self):
        """
        Create custom pop up menu
        """
        #self.header().hide()
        self.resizeColumnToContents(0)
        self.setColumnWidth(0, 200)
        self.setColumnWidth(1, 250)
        self.create_new_jiggle_rig_action = self.popup_menu.addAction("Create Jiggle Rig")
        self.delete_jiggle_rig_action = self.popup_menu.addAction("Delete Jiggle Rig")
        self.bake_jiggle_rigs_action = self.popup_menu.addAction("Bake Jiggle Rig")
        self.select_jiggle_rig_action = self.popup_menu.addAction("Select Jiggle Rig") # TODO: select connected node
        
class JiggleRigsTreeViewItem(QtWidgets.QTreeWidgetItem):
    """
    Jiggle rig QTreeWidgetItem
    """
    def __init__(self, parent=None,rig_node=None):
        super(JiggleRigsTreeViewItem, self).__init__(parent)
        self.jiggle_rig_node = rig_node
        self.setText(1, rig_node)
        # setting tree items
        self.enable_item = QtWidgets.QTreeWidgetItem(["Enable", 0])
        flags = self.enable_item.flags()
        self.enable_item.setFlags(flags & ~QtCore.Qt.ItemIsSelectable)
        
        self.translation_item = QtWidgets.QTreeWidgetItem(["Translation", 0])
        flags = self.translation_item.flags()
        self.translation_item.setFlags(flags & ~QtCore.Qt.ItemIsSelectable)
        
        self.rotation_item = QtWidgets.QTreeWidgetItem(["Rotation", 0])
        flags = self.rotation_item.flags()
        self.rotation_item.setFlags(flags & ~QtCore.Qt.ItemIsSelectable)
        
        self.stiffness_item = QtWidgets.QTreeWidgetItem(["Stiffness", 0])
        flags = self.stiffness_item.flags()
        self.stiffness_item.setFlags(flags & ~QtCore.Qt.ItemIsSelectable)
        
        self.damping_item = QtWidgets.QTreeWidgetItem(["Damping", 0])
        flags = self.damping_item.flags()
        self.damping_item.setFlags(flags & ~QtCore.Qt.ItemIsSelectable)
        
        self.weight_item = QtWidgets.QTreeWidgetItem(["Weight", 0])
        flags = self.weight_item.flags()
        self.weight_item.setFlags(flags & ~QtCore.Qt.ItemIsSelectable)
        # setting widgets
        self.enable_checkbox = QtWidgets.QCheckBox()
        
        self.translation_checkbox = QtWidgets.QCheckBox()
        
        self.rotation_checkbox = QtWidgets.QCheckBox()
        
        self.stiffness_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.stiffness_slider.setTickInterval(1)
        self.stiffness_slider.setRange(1,100)
        self.stiffness_slider.setProperty("Color", "Primary")
        
        self.damping_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.damping_slider.setTickInterval(1)
        self.damping_slider.setRange(1,100)
        self.damping_slider.setProperty("Color", "Primary")
        
        self.weight_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.weight_slider.setTickInterval(1)
        self.weight_slider.setRange(1,100)
        self.weight_slider.setProperty("Color", "Primary")
        # add setting items to jiggle rig item
        self.addChild(self.enable_item)
        self.addChild(self.translation_item)
        self.addChild(self.rotation_item)
        self.addChild(self.stiffness_item)
        self.addChild(self.damping_item)
        self.addChild(self.weight_item)
        
        # set values to match jiggle rig settings
        self._set_setting_widget_values()
        # set up socket connection callbacks
        self._setup_socket_connections()
        
    def _setup_socket_connections(self):
        """
        setup callbacks
        """
        self.enable_checkbox.stateChanged.connect(self._callback_active_checkbox_changed)
        self.translation_checkbox.stateChanged.connect(self._callback_translation_checkbox_changed)
        self.rotation_checkbox.stateChanged.connect(self._callback_rotation_checkbox_changed)
        self.stiffness_slider.valueChanged.connect(self._callback_stiffness_slider_changed)
        self.damping_slider.valueChanged.connect(self._callback_damping_slider_changed)
        self.weight_slider.valueChanged.connect(self._callback_weight_slider_changed)
        
    def _set_setting_widget_values(self):
        """
        set the value of each setting widget to match the jiggle rig node settings
        """
        if cmds.getAttr(f"{self.jiggle_rig_node}.enable") == 3:
            self.enable_checkbox.setChecked(True)
        else:
            self.enable_checkbox.setChecked(False)
            
        self.translation_checkbox.setChecked(cmds.getAttr(f"{self.jiggle_rig_node}.Translation"))
        self.rotation_checkbox.setChecked(cmds.getAttr(f"{self.jiggle_rig_node}.Rotation"))
        self.stiffness_slider.setValue(int(cmds.getAttr(f"{self.jiggle_rig_node}.stiffness")*100))
        self.damping_slider.setValue(int(cmds.getAttr(f"{self.jiggle_rig_node}.damping")*100))
        self.weight_slider.setValue(int(cmds.getAttr(f"{self.jiggle_rig_node}.jiggleWeight")*100))
        
    def _callback_active_checkbox_changed(self):
        """
        callback active checkbox changed
        """
        if self.enable_checkbox.isChecked():
            cmds.setAttr(f"{self.jiggle_rig_node}.enable", 3)
        else:
            cmds.setAttr(f"{self.jiggle_rig_node}.enable", 1)
    
    def _callback_translation_checkbox_changed(self):
        """
        callback translation checkbox changed
        """
        cmds.setAttr(f"{self.jiggle_rig_node}.Translation", self.translation_checkbox.isChecked())
        
    def _callback_rotation_checkbox_changed(self):
        """
        callback rotation checkbox changed
        """
        cmds.setAttr(f"{self.jiggle_rig_node}.Rotation", self.rotation_checkbox.isChecked())
        
    def _callback_stiffness_slider_changed(self):
        """
        callback stiffness slider changed
        """
        cmds.setAttr(f"{self.jiggle_rig_node}.stiffness", self.stiffness_slider.value()/100)
        
    def _callback_damping_slider_changed(self):
        """
        callback damping slider changed
        """
        cmds.setAttr(f"{self.jiggle_rig_node}.damping", self.damping_slider.value()/100)
        
    def _callback_weight_slider_changed(self):
        """
        callback weight slider changed
        """
        cmds.setAttr(f"{self.jiggle_rig_node}.jiggleWeight", self.weight_slider.value()/100)
        

class JiggleRigsManagerUI(DockableMainWindowAbstract):
    """
    Noise Generation settings ui
    """
    WINDOW_NAME = "Jiggle Manager"

    Q_OBJECT_NAME = "jiggle_manager"
    
    STYLE_SHEET_PATH = "{0}/theme/Flat/Dark/Cyan/Pink.qss".format(STYLE_SHEETS_PATH)
    
    def __init__(self, parent=None):
        super(JiggleRigsManagerUI, self).__init__(parent)
        
        self._refresh_jiggle_rig_treeview()
        

    def _ui(self):
        """
        UI to be built
        """
        # Frames, Groups and Layouts
        self.creation_deletion_management_layout = QtWidgets.QHBoxLayout(self)
        self.playback_layout = QtWidgets.QHBoxLayout(self)
        self.jiggle_rig_treeview_layout = QtWidgets.QVBoxLayout(self)
        self.jiggle_rig_treeview_groupbox = QtWidgets.QGroupBox(self)
        self.jiggle_rig_treeview_groupbox.setTitle("Jiggle Rigs")
        self.jiggle_rig_treeview_groupbox.setProperty("Color", "Primary")
        self.baking_playback_groupbox = QtWidgets.QGroupBox(self)
        self.baking_playback_groupbox.setTitle("Baking/Playback")
        self.baking_playback_groupbox.setProperty("Color", "Primary")
        
        # Widgets
        self.create_new_jiggle_rig = QtWidgets.QPushButton("Create Jiggle Rig",self)
        self.delete_jiggle_rig = QtWidgets.QPushButton("Delete Jiggle Rig",self)
        self.bake_jiggle_rig = QtWidgets.QPushButton("Bake Jiggle Rig",self)
        self.playback_button = QtWidgets.QPushButton("Preview",self)
        #self.playback_button.setIcon(QtGui.QIcon(":/QtTheme/icon/triangle_right/#00bcd4.svg"))
        self.jiggle_rigs_treeview = JiggleRigsTreeView()
        
        # CONNECT UI
        # Upper Layout
        self.creation_deletion_management_layout.addWidget(self.create_new_jiggle_rig)
        self.creation_deletion_management_layout.addWidget(self.delete_jiggle_rig)
        # playback layout
        self.playback_layout.addWidget(self.bake_jiggle_rig)
        self.playback_layout.addWidget(self.playback_button)
        # treeview layout
        #self.jiggle_rig_treeview_layout.addLayout(self.playback_layout)
        self.jiggle_rig_treeview_layout.addWidget(self.jiggle_rigs_treeview)
        self.jiggle_rig_treeview_groupbox.setLayout(self.jiggle_rig_treeview_layout)
        self.baking_playback_groupbox.setLayout(self.playback_layout)
        # main layout
        self.main_layout.addLayout(self.creation_deletion_management_layout)
        self.main_layout.addWidget(self.jiggle_rig_treeview_groupbox)
        self.main_layout.addWidget(self.baking_playback_groupbox)
        
        self.setLayout(self.main_layout)
        
    def _setup_socket_connections(self):
        """
        setup socket connections
        """
        self.create_new_jiggle_rig.pressed.connect(self._callback_create_jiggle_rig)
        self.delete_jiggle_rig.pressed.connect(self._callback_delete_jiggle_rig)
        self.bake_jiggle_rig.pressed.connect(self._callback_bake_jiggle_rigs)
        self.playback_button.pressed.connect(self._callback_play_simulation)
        
        self.jiggle_rigs_treeview.create_new_jiggle_rig_action.triggered.connect(self._callback_create_jiggle_rig)
        self.jiggle_rigs_treeview.delete_jiggle_rig_action.triggered.connect(self._callback_delete_jiggle_rig)
        self.jiggle_rigs_treeview.select_jiggle_rig_action.triggered.connect(self._callback_select_jiggle_rigs)
        self.jiggle_rigs_treeview.bake_jiggle_rigs_action.triggered.connect(self._callback_bake_jiggle_rigs)
        
    def _refresh_jiggle_rig_treeview(self):
        """
        List all jiggle rigs in the scene
        """
        jiggle_rigs = jiggle_utils.get_all_jiggle_rigs()
        self.jiggle_rigs_treeview.clear()
        for jiggle_rig in jiggle_rigs:
                jiggle_rig_item_widget = JiggleRigsTreeViewItem(rig_node=jiggle_rig)
                self.jiggle_rigs_treeview.setItemWidget(jiggle_rig_item_widget.enable_item, 1, jiggle_rig_item_widget.enable_checkbox)
                self.jiggle_rigs_treeview.setItemWidget(jiggle_rig_item_widget.translation_item, 1, jiggle_rig_item_widget.translation_checkbox)
                self.jiggle_rigs_treeview.setItemWidget(jiggle_rig_item_widget.rotation_item, 1, jiggle_rig_item_widget.rotation_checkbox)
                self.jiggle_rigs_treeview.setItemWidget(jiggle_rig_item_widget.stiffness_item, 1, jiggle_rig_item_widget.stiffness_slider)
                self.jiggle_rigs_treeview.setItemWidget(jiggle_rig_item_widget.damping_item, 1, jiggle_rig_item_widget.damping_slider)
                self.jiggle_rigs_treeview.setItemWidget(jiggle_rig_item_widget.weight_item, 1, jiggle_rig_item_widget.weight_slider)
                self.jiggle_rigs_treeview.addTopLevelItem(jiggle_rig_item_widget)
        self.jiggle_rigs_treeview.expandAll()
        return
        
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

    def _callback_play_simulation(self):
        """
        Playback the silulation callback
        """
        timeline_utils.play_simulation()
        
    def _callback_select_jiggle_rigs(self):
        """
        Select jiggle rigs
        """
        selected_jiggle_rigs = self._get_selected_jiggle_rigs_from_tree_view()
        jiggle_utils.select_jiggle_rigs(selected_jiggle_rigs, selection="animation_control")
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
            jiggle_rigs.append(item.jiggle_rig_node)
        return jiggle_rigs