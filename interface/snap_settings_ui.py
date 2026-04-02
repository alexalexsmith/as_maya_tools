"""
Snap settings ui
"""

try:
    from PySide2 import QtWidgets, QtCore, QtGui
    from shiboken2 import wrapInstance
except ModuleNotFoundError:
    from PySide6 import QtWidgets, QtCore, QtGui
    from shiboken6 import wrapInstance
    
from as_maya_tools.utilities.qt_utils import DockableMainWindowAbstract
from as_maya_tools.utilities import json_utils
from as_maya_tools.animation import snapping
from as_maya_tools import SNAP_SETTINGS_PATH, STYLE_SHEETS_PATH
from as_maya_tools.stylesheets import guiResources


DEFAULT_SNAP_SETTINGS ={
    "translation":True,
    "rotate":True,
    "scale":True
}

class SnapSettingsUI(DockableMainWindowAbstract):
    """
    Noise Generation settings ui
    """
    WINDOW_NAME = "Snap Settings"

    Q_OBJECT_NAME = "snap_settings"
    
    STYLE_SHEET_PATH = "{0}/theme/Flat/Dark/Cyan/Pink.qss".format(STYLE_SHEETS_PATH)
    
    def __init__(self, parent=None):
        super(SnapSettingsUI, self).__init__(parent)
        

    def _ui(self):
        """
        UI to be built
        """
        # Frames, Groups and Layouts
        # main_layout is created in parent class
        # self.main_layout = QtWidgets.QVBoxLayout(self)
        self.settings_groupbox = QtWidgets.QGroupBox(self)
        self.settings_groupbox.setTitle("Snap Settings")
        self.settings_layout = QtWidgets.QVBoxLayout(self)
        
        # Widgets        
        self.translate_checkbox = QtWidgets.QCheckBox(self)
        self.translate_checkbox.setText("Translate")
        
        self.rotate_checkbox = QtWidgets.QCheckBox(self)
        self.rotate_checkbox.setText("Rotate")
        
        self.scale_checkbox = QtWidgets.QCheckBox(self)
        self.scale_checkbox.setText("Scale")
        
        self.snap_a_to_b_button = QtWidgets.QPushButton("Snap A to B", self)
        
        
        # Connect UI
        self.settings_layout.addWidget(self.translate_checkbox)
        self.settings_layout.addWidget(self.rotate_checkbox)
        self.settings_layout.addWidget(self.scale_checkbox)
        self.settings_groupbox.setLayout(self.settings_layout)
        
        self.main_layout.addWidget(self.settings_groupbox)
        self.main_layout.addWidget(self.snap_a_to_b_button)
        
        self.setLayout(self.main_layout)
        
        # Get the settings before setting anything up to avoid overwriting the settings while creating the ui
        snap_settings = json_utils.read_offset_json_file(SNAP_SETTINGS_PATH, "snap_settings")
        
        self._init_settings(settings = snap_settings)
            
    def _init_settings(self, settings=None):
        """
        initiate the selection settings. use default settings if none exist
        """        
        if settings is None:
            json_utils.write_json_file(SNAP_SETTINGS_PATH, "snap_settings", DEFAULT_SNAP_SETTINGS)
            settings = json_utils.read_offset_json_file(SNAP_SETTINGS_PATH, "snap_settings")
        
        self.translate_checkbox.setChecked(settings["translate"])
        self.rotate_checkbox.setChecked(settings["rotate"])
        self.scale_checkbox.setChecked(settings["scale"])
        
    def _update_settings(self):
        """
        update settings json file
        """
        snap_settings={}
        snap_settings["translate"] = self.translate_checkbox.isChecked()
        snap_settings["rotate"] = self.rotate_checkbox.isChecked()
        snap_settings["scale"] = self.scale_checkbox.isChecked()
        
        json_utils.write_json_file(SNAP_SETTINGS_PATH, "snap_settings", snap_settings)
        
    def _setup_socket_connections(self):
        """
        setup socket connections
        """
        self.translate_checkbox.stateChanged.connect(self._update_settings)
        self.rotate_checkbox.stateChanged.connect(self._update_settings)
        self.scale_checkbox.stateChanged.connect(self._update_settings)
        self.snap_a_to_b_button.pressed.connect(self._callback_snap_button_pressed)
        
    def _callback_snap_button_pressed(self):
        """
        callback action on snap button press
        """
        snapping.snap_a_to_b(
            translation=self.translate_checkbox.isChecked(),
            rotation=self.rotate_checkbox.isChecked(),
            scale=self.scale_checkbox.isChecked()
            )
        