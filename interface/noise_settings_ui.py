"""
User interface for managing noise generation options
"""
from PySide2 import QtWidgets, QtCore, QtGui

from as_maya_tools.utilities.qt_utils import DockableMainWindowAbstract
from as_maya_tools.utilities import json_utils
from as_maya_tools import NOISE_GENERATION_SETTINGS_PATH, STYLE_SHEETS_PATH

from as_maya_tools.animation import generate_noise


DEFAULT_NOISE_GENERATION_SETTINGS = \
    {
        "frame_range":"selected_key_range",
        "frequency":1,
        "amplitude":1,
        "use_current_value":True,
        "seed":False
    }

class CustomQFrame(QtWidgets.QFrame):
    """
    Custom QFrame with set style to keep my QFrames consistent
    """
    def __init__(self, parent=None):
        super(CustomQFrame, self).__init__(parent)
        self.setFrameStyle(QtWidgets.QFrame.StyledPanel | QtWidgets.QFrame.Plain)
        #self.setStyleSheet("QFrame {border: 3px solid #A22526;}")



class NoiseGenerationSettingsUI(DockableMainWindowAbstract):
    """
    Noise Generation settings ui
    """
    WINDOW_NAME = "Noise Generation"

    Q_OBJECT_NAME = "noise_generation"
    
    #STYLE_SHEET_PATH = "{0}/mortarheadd.qss".format(STYLE_SHEETS_PATH)
    
    def __init__(self, parent=None):
        super(NoiseGenerationSettingsUI, self).__init__(parent)
        

    def _ui(self):
        """
        UI to be built
        """
        # Frames, Groups and Layouts
        # main_layout is created in parent class
        # self.main_layout = QtWidgets.QVBoxLayout(self)
        self.frame_range_frame = CustomQFrame(self)
        self.frame_range_layout = QtWidgets.QVBoxLayout(self)
        self.settings_groupbox = QtWidgets.QGroupBox(self)
        self.settings_groupbox.setTitle("Noise Settings")
        self.settings_layout = QtWidgets.QGridLayout(self)
        
        # Widgets
        self.frame_range_label = QtWidgets.QLabel()
        self.frame_range_label.setText("Frame Range")
        
        self.frame_range_combobox = QtWidgets.QComboBox()
        
        self.frequency_label = QtWidgets.QLabel()
        self.frequency_label.setText("Frequency")
        self.frequency_spinbox = QtWidgets.QSpinBox(self)
        self.frequency_spinbox.setMaximum(999999)
        self.frequency_spinbox.setMinimum(1)
        
        self.amplitude_label = QtWidgets.QLabel()
        self.amplitude_label.setText("Amplitude")
        self.amplitude_spinbox = QtWidgets.QSpinBox(self)
        self.amplitude_spinbox.setMaximum(999999)
        self.amplitude_spinbox.setMinimum(-999999)
        
        self.use_current_value_checkbox = QtWidgets.QCheckBox(self)
        self.use_current_value_checkbox.setText("Use Current Value")
        
        self.use_seed_checkbox = QtWidgets.QCheckBox(self)
        self.use_seed_checkbox.setText("Use Seed")
        
        self.seed_label = QtWidgets.QLabel()
        self.seed_label.setText("Seed")
        self.seed_spinbox = QtWidgets.QSpinBox(self)
        self.seed_spinbox.setMaximum(999999)
        self.seed_spinbox.setMinimum(1)
        
        
        # Connect UI
        self.frame_range_layout.addWidget(self.frame_range_label)
        self.frame_range_layout.addWidget(self.frame_range_combobox)
        self.frame_range_frame.setLayout(self.frame_range_layout)
        
        self.settings_layout.addWidget(self.frequency_label, 0, 0)
        self.settings_layout.addWidget(self.frequency_spinbox, 0 , 1)
        self.settings_layout.addWidget(self.amplitude_label, 1, 0)
        self.settings_layout.addWidget(self.amplitude_spinbox, 1, 1)
        self.settings_layout.addWidget(self.use_current_value_checkbox, 2, 0)
        self.settings_layout.addWidget(self.use_seed_checkbox, 3, 0)
        self.settings_layout.addWidget(self.seed_label, 4, 0)
        self.settings_layout.addWidget(self.seed_spinbox, 4, 1)
        self.settings_groupbox.setLayout(self.settings_layout)
        
        self.generate_noise_button = QtWidgets.QPushButton("Generate Noise", self)
        
        self.main_layout.addWidget(self.frame_range_frame)
        self.main_layout.addWidget(self.settings_groupbox)
        self.main_layout.addWidget(self.generate_noise_button)
        
        self.setLayout(self.main_layout)
        
        # Get the settings before setting anything up to avoid overwriting the settings while creating the ui
        noise_generation_settings = json_utils.read_offset_json_file(NOISE_GENERATION_SETTINGS_PATH, "noise_generation_settings")
        
        self._populate_frame_range_combobox()
        self._init_noise_generation_settings(settings = noise_generation_settings)
        # update any ui draw features
        self._enable_seed_spin_boxes()
        
    def _populate_frame_range_combobox(self):
        """
        Populate the rig definition combobox with all saved rig context definition files
        """
        keyframe_range_options = ["animation_range", "playback_range", "selected_key_range"]
        for option in keyframe_range_options:
            self.frame_range_combobox.addItem(option)
            
    def _init_noise_generation_settings(self, settings=None):
        """
        initiate the selection settings. use default settings if none exist
        """        
        if settings is None:
            json_utils.write_json_file(NOISE_GENERATION_SETTINGS_PATH, "noise_generation_settings", DEFAULT_NOISE_GENERATION_SETTINGS)
        settings = json_utils.read_offset_json_file(NOISE_GENERATION_SETTINGS_PATH, "noise_generation_settings")
        
        self.frame_range_combobox.setCurrentText(settings["frame_range"])
        
        self.frequency_spinbox.setValue(settings["frequency"])
        self.amplitude_spinbox.setValue(settings["amplitude"])
        self.use_current_value_checkbox.setChecked(settings["use_current_value"])
        
        if settings["seed"] == None:
            self.use_seed_checkbox.setChecked(False)
            self.seed_spinbox.setValue(1)
        else:
            self.use_seed_checkbox.setChecked(True)
            self.seed_spinbox.setValue(settings["seed"])
        
    def _update_settings(self):
        """
        update settings json file
        """
        noise_generation_settings={}
        noise_generation_settings["frame_range"] = self.frame_range_combobox.currentText()
        noise_generation_settings["frequency"] = self.frequency_spinbox.value()
        noise_generation_settings["amplitude"] = self.amplitude_spinbox.value()
        noise_generation_settings["use_current_value"] = self.use_current_value_checkbox.isChecked()
        if not self.use_seed_checkbox.isChecked():
            noise_generation_settings["seed"] = None
        else:
            noise_generation_settings["seed"] = self.seed_spinbox.value()
        
        json_utils.write_json_file(NOISE_GENERATION_SETTINGS_PATH, "noise_generation_settings", noise_generation_settings)
        
    def _setup_socket_connections(self):
        """
        setup socket connections
        """
        self.frame_range_combobox.currentTextChanged.connect(self._update_settings)
        self.frequency_spinbox.valueChanged.connect(self._update_settings)
        self.amplitude_spinbox.valueChanged.connect(self._update_settings)
        self.use_current_value_checkbox.stateChanged.connect(self._update_settings)
        self.use_seed_checkbox.stateChanged.connect(self._update_settings)
        self.use_seed_checkbox.stateChanged.connect(self._enable_seed_spin_boxes)
        self.seed_spinbox.valueChanged.connect(self._update_settings)
        self.generate_noise_button.pressed.connect(generate_noise.generate_noise_on_selection)
        
    def _enable_seed_spin_boxes(self):
        """
        Enable or disable seed spin boxes based on UI settings
        """
        self.seed_spinbox.setEnabled(self.use_seed_checkbox.isChecked())
        self.seed_label.setEnabled(self.use_seed_checkbox.isChecked())
        