"""
Attribute switcher ui
load an attribute into the ui and set a values
The tool will update the value while maintaining the transform position
Ideas:
-load multiple attributes
-choose multiple controls to include in the maintain transform position function
-import and export setups
Attribute Types
Float, Bool, Enum, Integer
"""

try:
    from PySide2 import QtWidgets, QtCore, QtGui
    from shiboken2 import wrapInstance
except ModuleNotFoundError:
    from PySide6 import QtWidgets, QtCore, QtGui
    from shiboken6 import wrapInstance

from maya import cmds

from as_maya_tools.utilities.qt_utils import DockableMainWindowAbstract, TreeWidgetRightClickSupportAbstract
from as_maya_tools.utilities import json_utils, attribute_utils, spaceswitch_utils, performance_utils
from as_maya_tools import SPACE_SWITCHER_SETTINGS_PATH, STYLE_SHEETS_PATH



DEFAULT_SPACE_SWITCHER_SETTINGS = \
    {
        "frame_range":"current frame",
        "keyed_frames":False,
        "attribute_paths":[]
    }


class CustomQFrame(QtWidgets.QFrame):
    """
    Custom QFrame with set style to keep my QFrames consistent
    """
    def __init__(self, parent=None):
        super(CustomQFrame, self).__init__(parent)
        self.setFrameStyle(QtWidgets.QFrame.StyledPanel | QtWidgets.QFrame.Plain)


class AttributeTreeWidgetItem(QtWidgets.QTreeWidgetItem):
    """
    Treewidgetitem for displaying loaded attributes
    """
    def __init__(self, attribute_path=None, attribute_control=None, parent=None):
        super(AttributeTreeWidgetItem, self).__init__(parent)
        self.attribute_path = attribute_path
        self.attribute_control = attribute_control

    def get_attribute_control_value(self):
        """
        get the attribute controls current value
        """
        if isinstance(self.attribute_control, QtWidgets.QDoubleSpinBox):
            return self.attribute_control.value()
        if isinstance(self.attribute_control, QtWidgets.QSpinBox):
            return self.attribute_control.value()
        if isinstance(self.attribute_control, QtWidgets.QCheckBox):
            return self.attribute_control.isChecked()
        if isinstance(self.attribute_control, QtWidgets.QComboBox):
            return self.attribute_control.currentIndex()


class AttributeTreeWidget(TreeWidgetRightClickSupportAbstract):
    """
    Tree widget to display and manage attribute switching
    """
    HEADER_LABELS = ["Attribute", "Value"]
        
    def _pop_up_menu(self):
        """
        Create custom pop up menu
        """
        self.attributes = []
        self.load_attribute = self.popup_menu.addAction("Load Attribute")
        self.remove_attribute = self.popup_menu.addAction("Remove Attribute")
        self.select_node = self.popup_menu.addAction("Select Node")
        
    def add_attribute_item(self, attribute_path):
        """add the tree view item to this tree view widget"""
        for attribute in self.attributes:
            if attribute_path == attribute.attribute_path:
                return
        if not performance_utils.obj_exists(attribute_path):
            return
        attribute_control = self.get_attribute_control(attribute_path)
        if attribute_control:
            qtree_item = AttributeTreeWidgetItem(
                parent=self,
                attribute_path=attribute_path,
                attribute_control=attribute_control)
            qtree_item.setText(0, attribute_path)
            self.setItemWidget(qtree_item, 1, qtree_item.attribute_control)
            self.attributes.append(qtree_item)
            
        self.resizeColumnToContents(0)
            
    def remove_attribute_item(self):
        """
        remove item from tree view
        """
        if not self.selectedItems():
            return
        for item in self.selectedItems():
            item.setHidden(True)
            self.attributes.remove(item)
            
    def select_maya_node(self):
        """
        select the nodes affected by selected attribute items
        """        
        if not self.selectedItems():
            return
        cmds.select(clear=True)
        for item in self.selectedItems():
            cmds.select(attribute_utils.Attribute(item.attribute_path).node, add=True)
        

    def get_attribute_control(self, attribute_path):
        """
        Get the appropriate widget for the attribute
        """
        attribute_control = None
        attribute_type = cmds.getAttr(attribute_path, type=True)
        attribute_object = attribute_utils.Attribute(attribute_path)
        
        DOUBLE_ATTRIBUTE_TYPES = ["double", "doubleLinear", "doubleAngle"]
        if attribute_type in DOUBLE_ATTRIBUTE_TYPES:
            attribute_control = QtWidgets.QDoubleSpinBox()
            attribute_control.setMaximum(attribute_object.get_maximum())
            attribute_control.setMinimum(attribute_object.get_minimum())
            attribute_control.setValue(attribute_object.get_value())
            
        if attribute_type == "long":
            attribute_control = QtWidgets.QSpinBox()
            attribute_control.setMaximum(attribute_object.get_maximum())
            attribute_control.setMinimum(attribute_object.get_minimum())
            attribute_control.setValue(attribute_object.get_value())
            
        if attribute_type == "bool":
            attribute_control = QtWidgets.QCheckBox()
            attribute_control.setChecked(attribute_object.get_value())
            
        if attribute_type == "enum":
            attribute_control = QtWidgets.QComboBox()
            enum_values = attribute_object.get_enum_values()
            for enum_value in enum_values:
                attribute_control.addItem(enum_value)
            attribute_control.setCurrentIndex(attribute_object.get_value())
            
        return attribute_control
            

class SpaceSwitcherUI(DockableMainWindowAbstract):
    """
    Noise Generation settings ui
    """
    WINDOW_NAME = "Space Switcher"

    Q_OBJECT_NAME = "space_switcher"
    
    #STYLE_SHEET_PATH = "{0}/Combinear.qss".format(STYLE_SHEETS_PATH)
    
    def __init__(self, parent=None):
        super(SpaceSwitcherUI, self).__init__(parent)

    def _ui(self):
        """
        UI to be built
        """
        # main_layout is created in parent class
        # Frames, Groups and Layouts
        self.switch_panel_layout = QtWidgets.QVBoxLayout()
        self.switch_row_layout = QtWidgets.QHBoxLayout(self)
        self.frame_range_layout = QtWidgets.QHBoxLayout(self)
        self.switch_panel_layout = QtWidgets.QVBoxLayout()
        self.switch_row_layout = QtWidgets.QHBoxLayout(self)
        self.switch_groupbox = QtWidgets.QGroupBox("Switch:")
        self.switch_groupbox.setLayout(self.switch_panel_layout)
        
        self.top_buttons_layout = QtWidgets.QHBoxLayout(self)
        
        # Widgets
        self.load_button = QtWidgets.QPushButton("Load Attribute", self)
        self.remove_button = QtWidgets.QPushButton("Remove Attribute", self)
        self.switch_button = QtWidgets.QPushButton("Switch", self)
        self.attribute_tree_widget = AttributeTreeWidget()
        
        # FramRange Options Widgets
        self.keyed_frames_checkbox = QtWidgets.QCheckBox(self)
        self.keyed_frames_checkbox.setText("Keyed Frames")
        self.framerange_options_combo_box = QtWidgets.QComboBox(self)
        self.framerange_options_combo_box.setMinimumHeight(25)
        for action in spaceswitch_utils.SPACESWITCH_FRAMERANGE_OPTIONS:
            self.framerange_options_combo_box.addItem(action)
            
        # Create frame range spin box
        self.start_frame_spinbox = QtWidgets.QSpinBox(self)
        self.start_frame_spinbox.setMaximum(999999)
        self.start_frame_spinbox.setMinimum(-999999)
        
        # Set default start frame range
        self.start_frame_spinbox.setValue(cmds.playbackOptions(q=True, minTime=True))
        self.end_frame_spinbox = QtWidgets.QSpinBox(self)
        self.end_frame_spinbox.setMaximum(999999)
        self.end_frame_spinbox.setMinimum(-999999)
        
        # Set default end frame range
        self.end_frame_spinbox.setValue(cmds.playbackOptions(q=True, maxTime=True))
        self.start_frame_spinbox.setEnabled(False)
        self.end_frame_spinbox.setEnabled(False)
        
        # Connect UI
        # Upper Layout
        self.top_buttons_layout.addWidget(self.load_button)
        self.top_buttons_layout.addWidget(self.remove_button)
        self.main_layout.addLayout(self.top_buttons_layout)
        self.main_layout.addWidget(self.attribute_tree_widget)
        
        # Switch Settings/Action Layout
        self.switch_row_layout.addWidget(self.framerange_options_combo_box)
        self.switch_row_layout.addWidget(self.keyed_frames_checkbox)
        self.frame_range_layout.addWidget(self.start_frame_spinbox)
        self.frame_range_layout.addWidget(self.end_frame_spinbox)
        self.switch_panel_layout.addLayout(self.switch_row_layout)
        self.switch_panel_layout.addLayout(self.frame_range_layout)
        self.switch_panel_layout.addWidget(self.switch_button)
        self.main_layout.addWidget(self.switch_groupbox)
        
        self.setLayout(self.main_layout)
        
        # Get the settings before setting anything up to avoid overwriting the settings while creating the ui
        settings = json_utils.read_offset_json_file(SPACE_SWITCHER_SETTINGS_PATH, "space_switcher_settings")
        
        self._init_settings(settings = settings)
        
    def _init_settings(self, settings = None):
        """
        init the settings from a json file
        """
        if settings is None:
            json_utils.write_json_file(SPACE_SWITCHER_SETTINGS_PATH, "space_switcher_settings", DEFAULT_SPACE_SWITCHER_SETTINGS)
            settings = json_utils.read_offset_json_file(SPACE_SWITCHER_SETTINGS_PATH, "space_switcher_settings")
            
        self.framerange_options_combo_box.setCurrentText(settings["frame_range"])
        self.keyed_frames_checkbox.setChecked(settings["keyed_frames"])
        for attribute_path in settings["attribute_paths"]:
            self.attribute_tree_widget.add_attribute_item(attribute_path)
            
    def _update_settings(self):
        """
        update settings json file
        """
        settings={}
        settings["frame_range"] = self.framerange_options_combo_box.currentText()
        settings["keyed_frames"] = self.keyed_frames_checkbox.isChecked()
        
        attribute_paths = []
        for attribute_item in self.attribute_tree_widget.attributes:
            attribute_paths.append(attribute_item.attribute_path)
        settings["attribute_paths"] = attribute_paths
        
        json_utils.write_json_file(SPACE_SWITCHER_SETTINGS_PATH, "space_switcher_settings", settings)

    def _setup_socket_connections(self):
        """
        setup socket connections
        """
        # update settings file callbacks
        self.framerange_options_combo_box.currentTextChanged.connect(self._update_settings)
        self.keyed_frames_checkbox.stateChanged.connect(self._update_settings)
        
        # UI display callbackcs
        self.framerange_options_combo_box.currentTextChanged.connect(self.callback_enable_frame_range_spin_boxes)
        
        # UI button function callbacks
        self.load_button.clicked.connect(self._callback_load_attributes)
        self.remove_button.clicked.connect(self._callback_remove_attribute)
        self.switch_button.clicked.connect(self._callback_space_switch)
        
        # TreeView action menu callbacks
        self.attribute_tree_widget.load_attribute.triggered.connect(self._callback_load_attributes)
        self.attribute_tree_widget.remove_attribute.triggered.connect(self._callback_remove_attribute)
        self.attribute_tree_widget.select_node.triggered.connect(self._callback_select_node)
        
    def callback_enable_frame_range_spin_boxes(self, value):
        """Enable or disable frame range spin boxes based on UI settings
        :param str value: value that determines enabled state, on state triggered by "Frame Range"
        """
        if value == "Frame Range":
            self.start_frame_spinbox.setEnabled(True)
            self.end_frame_spinbox.setEnabled(True)
        else:
            self.start_frame_spinbox.setEnabled(False)
            self.end_frame_spinbox.setEnabled(False)

    def _callback_load_attributes(self):
        """
        Load attributes from based on selection
        """
        selection = cmds.ls(selection=True)
        if not selection:
            return
        for node in selection:    
            attribute_path = None
            selected_attributes = cmds.channelBox('mainChannelBox', query=True, selectedMainAttributes=True)
            if not selected_attributes:
                return
            for attribute in selected_attributes:
                attribute_path = "{0}.{1}".format(node, attribute)
                if not performance_utils.obj_exists(attribute_path):
                    continue
                self.attribute_tree_widget.add_attribute_item(attribute_path)
        self._update_settings()
        
    def _callback_remove_attribute(self):
        """
        Remove attributes based on TreeView selection
        """
        self.attribute_tree_widget.remove_attribute_item()
        self._update_settings()
        
    def _callback_select_node(self):
        """
        Select the node of the currently selected item in the treeview
        """
        self.attribute_tree_widget.select_maya_node()
        

    def _callback_space_switch(self):
        """
        space switch all loaded attributes
        """
        attribute_paths = []
        if len(self.attribute_tree_widget.attributes) < 1:
            return
            
        for attribute_item in self.attribute_tree_widget.attributes:
            attribute_paths.append(attribute_item.attribute_path)
            
        spaceswitch_utils.space_switch(
            attribute_paths,
            attribute_item.get_attribute_control_value(),
            frame_range=self.framerange_options_combo_box.currentText(),
            keyed_frames=self.keyed_frames_checkbox.isChecked()
        )