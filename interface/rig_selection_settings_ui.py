"""
User interface for managing rig selection options
"""
import os
from PySide2 import QtWidgets, QtCore, QtGui

from as_maya_tools.utilities.qt_utils import DockableMainWindowAbstract
from as_maya_tools.utilities import json_utils
from as_maya_tools import RIG_DEFINITION_CONTEXT_PATH, RIG_SELECTION_SETTINGS_PATH, STYLE_SHEETS_PATH


DEFAULT_RIG_SELECTION_SETTINGS = \
    {
        "rig_definition_context":"default",
        "visible":False,
        "keyed":False,
        "ignore_side":False,
        "subset_filter":False
    }

class CustomQFrame(QtWidgets.QFrame):
    """
    Custom QFrame with set style to keep my QFrames consistent
    """
    def __init__(self, parent=None):
        super(CustomQFrame, self).__init__(parent)
        self.setFrameStyle(QtWidgets.QFrame.StyledPanel | QtWidgets.QFrame.Plain)



class RigSelectionSettingsUI(DockableMainWindowAbstract):
    """
    Rig selection settings ui
    """
    WINDOW_NAME = "Rig Selection Settings"

    Q_OBJECT_NAME = "rig_selection_settings"
    
    #STYLE_SHEET_PATH = "{0}/mortarheadd.qss".format(STYLE_SHEETS_PATH)
    
    def __init__(self, parent=None):
        super(RigSelectionSettingsUI, self).__init__(parent)
        

    def _ui(self):
        """
        UI to be built
        """
        # Frames, Groups and Layouts
        # main_layout is created in parent class
        # self.main_layout = QtWidgets.QVBoxLayout(self)
        self.context_picker_frame = CustomQFrame(self)
        self.context_picker_layout = QtWidgets.QVBoxLayout(self)
        self.settings_groupbox = QtWidgets.QGroupBox(self)
        self.settings_groupbox.setTitle("Selection Settings")
        self.settings_layout = QtWidgets.QGridLayout(self)
        
        # Widgets
        self.rig_definition_context_label = QtWidgets.QLabel()
        self.rig_definition_context_label.setText("Rig Definition Context")
        
        self.rig_definition_context_combobox = QtWidgets.QComboBox()
        
        self.visible_setting_checkbox = QtWidgets.QCheckBox(self)
        self.visible_setting_checkbox.setText("Visible")
        self.keyed_setting_checkbox = QtWidgets.QCheckBox(self)
        self.keyed_setting_checkbox.setText("Keyed")
        self.ignore_side_setting_checkbox = QtWidgets.QCheckBox(self)
        self.ignore_side_setting_checkbox.setText("Ignore Side")
        self.subsetfilter_setting_checkbox = QtWidgets.QCheckBox(self)
        self.subsetfilter_setting_checkbox.setText("Subset Filter")
        
        # Connect UI
        self.context_picker_layout.addWidget(self.rig_definition_context_label)
        self.context_picker_layout.addWidget(self.rig_definition_context_combobox)
        self.context_picker_frame.setLayout(self.context_picker_layout)
        
        self.settings_layout.addWidget(self.visible_setting_checkbox, 0, 0)
        self.settings_layout.addWidget(self.keyed_setting_checkbox, 0 , 1)
        self.settings_layout.addWidget(self.ignore_side_setting_checkbox, 1, 0)
        self.settings_layout.addWidget(self.subsetfilter_setting_checkbox, 1, 1)
        self.settings_groupbox.setLayout(self.settings_layout)
        
        self.main_layout.addWidget(self.context_picker_frame)
        self.main_layout.addWidget(self.settings_groupbox)
        
        self.setLayout(self.main_layout)
        
        # Get the settings before setting anything up to avoid overwriting the settings while creating the ui
        rig_selection_settings = json_utils.read_offset_json_file(RIG_SELECTION_SETTINGS_PATH, "rig_selection_settings")
        
        self._populate_rig_definition_combobox()
        self._init_rig_selection_settings(settings = rig_selection_settings)
        
    def _populate_rig_definition_combobox(self):
        """
        Populate the rig definition combobox with all saved rig context definition files
        """
        for file in os.listdir(RIG_DEFINITION_CONTEXT_PATH):
            if file.endswith(".json"):
                self.rig_definition_context_combobox.addItem(os.path.splitext(os.path.basename(file))[0])
        if self.rig_definition_context_combobox.count() == 0:
            self.rig_definition_context_combobox.addItem("default")
            
    def _init_rig_selection_settings(self, settings=None):
        """
        initiate the selection settings. use default settings if none exist
        """
        if settings is None:
            json_utils.write_json_file(RIG_SELECTION_SETTINGS_PATH, "rig_selection_settings", DEFAULT_RIG_SELECTION_SETTINGS)
        settings = json_utils.read_offset_json_file(RIG_SELECTION_SETTINGS_PATH, "rig_selection_settings")
        
        self.rig_definition_context_combobox.setCurrentText(settings["rig_definition_context"])
        
        self.visible_setting_checkbox.setChecked(settings["visible"])
        self.keyed_setting_checkbox.setChecked(settings["keyed"])
        self.ignore_side_setting_checkbox.setChecked(settings["ignore_side"])
        self.subsetfilter_setting_checkbox.setChecked(settings["subset_filter"])
        
    def _update_settings(self):
        """
        update settings json file
        """
        rig_selection_settings={}
        rig_selection_settings["rig_definition_context"] = self.rig_definition_context_combobox.currentText()
        rig_selection_settings["visible"] = self.visible_setting_checkbox.isChecked()
        rig_selection_settings["keyed"] = self.keyed_setting_checkbox.isChecked()
        rig_selection_settings["ignore_side"] = self.ignore_side_setting_checkbox.isChecked()
        rig_selection_settings["subset_filter"] = self.subsetfilter_setting_checkbox.isChecked()
        
        json_utils.write_json_file(RIG_SELECTION_SETTINGS_PATH, "rig_selection_settings", rig_selection_settings)
        
    def _setup_socket_connections(self):
        """
        setup socket connections
        """
        self.rig_definition_context_combobox.currentTextChanged.connect(self._update_settings)
        self.visible_setting_checkbox.stateChanged.connect(self._update_settings)
        self.keyed_setting_checkbox.stateChanged.connect(self._update_settings)
        self.ignore_side_setting_checkbox.stateChanged.connect(self._update_settings)
        self.subsetfilter_setting_checkbox.stateChanged.connect(self._update_settings)
        