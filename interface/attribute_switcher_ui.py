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

from PySide2 import QtWidgets, QtCore, QtGui

from maya import cmds

from as_maya_tools.utilities.qt_utils import DockableMainWindowAbstract, TreeWidgetRightClickSupportAbstract
from as_maya_tools.utilities import json_utils, attribute_utils, performance_utils
from as_maya_tools import NOISE_GENERATION_SETTINGS_PATH, STYLE_SHEETS_PATH


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
        self.Remove_attribute = self.popup_menu.addAction("Remove Attribute")
        
    def add_attribute_item(self, attribute_path):
        """add the tree view item to this tree view widget"""
        for attribute in self.attributes:
            if attribute_path == attribute.attribute_path:
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
            
    def remove_attribute_item(self):
        """
        remove item from tree view
        """
        if not self.selectedItems():
            return
        for item in self.selectedItems():
            item.setHidden(True)
            self.attributes.remove(item)

    def get_attribute_control(self, attribute_path):
        """
        Get the appropriate widget for the attribute
        """
        attribute_control = None
        attribute_type = cmds.getAttr(attribute_path, type=True)
        attribute_object = attribute_utils.Attribute(attribute_path)
        
        if attribute_type == "double":
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
            

class AttributeSwitcherUI(DockableMainWindowAbstract):
    """
    Noise Generation settings ui
    """
    WINDOW_NAME = "Attribute Switcher"

    Q_OBJECT_NAME = "attribute_switcher"
    
    #STYLE_SHEET_PATH = "{0}/mortarheadd.qss".format(STYLE_SHEETS_PATH)
    
    def __init__(self, parent=None):
        super(AttributeSwitcherUI, self).__init__(parent)

    def _ui(self):
        """
        UI to be built
        """
        # Frames, Groups and Layouts
        # main_layout is created in parent class
        self.top_buttons_layout = QtWidgets.QHBoxLayout(self)
        
        # Widgets
        self.load_button = QtWidgets.QPushButton("Load Attribute", self)
        self.remove_button = QtWidgets.QPushButton("Remove Attribute", self)
        self.switch_button = QtWidgets.QPushButton("Switch", self)
        self.attribute_tree_widget = AttributeTreeWidget()
        
        # Connect UI
        self.top_buttons_layout.addWidget(self.load_button)
        self.top_buttons_layout.addWidget(self.remove_button)
        self.main_layout.addLayout(self.top_buttons_layout)
        self.main_layout.addWidget(self.attribute_tree_widget)
        self.main_layout.addWidget(self.switch_button)
        
        self.setLayout(self.main_layout)

    def _setup_socket_connections(self):
        """
        setup socket connections
        """
        self.load_button.clicked.connect(self._callback_load_attributes)
        self.remove_button.clicked.connect(self.attribute_tree_widget.remove_attribute_item)
        
        self.attribute_tree_widget.load_attribute.triggered.connect(self._callback_load_attributes)
        self.attribute_tree_widget.Remove_attribute.triggered.connect(self.attribute_tree_widget.remove_attribute_item)

        self.switch_button.clicked.connect(self._callback_space_switch)

    def _callback_load_attributes(self):
        """
        Load attributes from based on selection
        """
        selection = cmds.ls(selection=True)
        if not selection:
            return
        for node in selection:    
            attribute_path = None
            for attribute in cmds.channelBox('mainChannelBox', query=True, selectedMainAttributes=True):
                attribute_path = "{0}.{1}".format(node, attribute)
                if not performance_utils.obj_exists(attribute_path):
                    continue
                self.attribute_tree_widget.add_attribute_item(attribute_path)    
        return

    def _callback_space_switch(self):
        """
        space switch all loaded attributes
        """
        for attribute_item in self.attribute_tree_widget.attributes:
            attribute_utils.space_switch(
                attribute_item.attribute_path,
                attribute_item.get_attribute_control_value())
