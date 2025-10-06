"""
User interface for managing noise generation options
"""
try:
    from PySide2 import QtWidgets, QtCore, QtGui
    from shiboken2 import wrapInstance
except ModuleNotFoundError:
    from PySide6 import QtWidgets, QtCore, QtGui
    from shiboken6 import wrapInstance

from maya import cmds
from maya.api import OpenMaya

from as_maya_tools.utilities.qt_utils import DockableMainWindowAbstract
from as_maya_tools.utilities import json_utils, attribute_utils, spaceswitch_utils, performance_utils
from as_maya_tools.utilities import json_utils
from as_maya_tools import STYLE_SHEETS_PATH
from as_maya_tools.stylesheets import guiResources



class CustomQFrame(QtWidgets.QFrame):
    """
    Custom QFrame with set style to keep my QFrames consistent
    """
    def __init__(self, parent=None):
        super(CustomQFrame, self).__init__(parent)
        self.setFrameStyle(QtWidgets.QFrame.StyledPanel | QtWidgets.QFrame.Plain)
        #self.setStyleSheet("QFrame {border: 3px solid #A22526;}")



class AdvancedSkeletonIKFKSwitcherUI(DockableMainWindowAbstract):
    """
    Noise Generation settings ui
    """
    WINDOW_NAME = "IK FK Switcher"

    Q_OBJECT_NAME = "ik_fk_switcher"
    
    STYLE_SHEET_PATH = "{0}/theme/Flat/Dark/Cyan/Pink.qss".format(STYLE_SHEETS_PATH)
    
    def __init__(self, parent=None):
        super(AdvancedSkeletonIKFKSwitcherUI, self).__init__(parent)
        
        self.drag_release_callback = None
        

    def _ui(self):
        """
        UI to be built
        """
        # Frames, Groups and Layouts
        # main_layout is created in parent class
        # self.main_layout = QtWidgets.QVBoxLayout(self)
        self.frame_range_layout = QtWidgets.QHBoxLayout(self)
        self.switch_panel_layout = QtWidgets.QVBoxLayout(self)
        self.switch_row_layout = QtWidgets.QHBoxLayout(self)
        self.switch_groupbox = QtWidgets.QGroupBox("Switch:")
        self.switch_groupbox.setLayout(self.switch_panel_layout)
        
        # Widgets
        self.live_match_checkbox = QtWidgets.QCheckBox(self)
        self.live_match_checkbox.setText("Live Switching")
        self.switch_button = QtWidgets.QPushButton("Switch", self)
        
        # Frame Range Options Widgets
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
        #self.frame_range_layout.addWidget(self.frame_range_label)
        #self.frame_range_layout.addWidget(self.frame_range_combobox)
        #self.frame_range_frame.setLayout(self.frame_range_layout)
        
        #self.settings_layout.addWidget(self.frequency_label, 0, 0)
        #self.settings_layout.addWidget(self.frequency_spinbox, 0 , 1)
        #self.settings_layout.addWidget(self.amplitude_label, 1, 0)
        #self.settings_layout.addWidget(self.amplitude_spinbox, 1, 1)
        #self.settings_layout.addWidget(self.use_current_value_checkbox, 2, 0)
        #self.settings_layout.addWidget(self.use_seed_checkbox, 3, 0)
        #self.settings_layout.addWidget(self.seed_label, 4, 0)
        #self.settings_layout.addWidget(self.seed_spinbox, 4, 1)
        #self.settings_groupbox.setLayout(self.settings_layout)
        
        # Switch Settings/Action Layout
        self.switch_row_layout.addWidget(self.framerange_options_combo_box)
        self.switch_row_layout.addWidget(self.keyed_frames_checkbox)
        self.frame_range_layout.addWidget(self.start_frame_spinbox)
        self.frame_range_layout.addWidget(self.end_frame_spinbox)
        self.switch_panel_layout.addLayout(self.switch_row_layout)
        self.switch_panel_layout.addLayout(self.frame_range_layout)
        self.switch_panel_layout.addWidget(self.switch_button)
        
        self.main_layout.addWidget(self.live_match_checkbox)
        self.main_layout.addWidget(self.switch_groupbox)
        
        self.setLayout(self.main_layout)
        
    def _setup_socket_connections(self):
        """
        setup socket connections
        """
        # UI display callbackcs
        self.framerange_options_combo_box.currentTextChanged.connect(self.callback_enable_frame_range_spin_boxes)
        
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

    def remove_maya_callbacks(self):
        """remove maya callbacks"""
        try:
            OpenMaya.MMessage.removeCallback(self.drag_release_callback)
        except RuntimeError:  # MMessage already deleted
            pass

    def closeEvent(self, event):
        """Remove all callback messages and remove ui from memory"""
        super(AdvancedSkeletonIKFKSwitcherUI, self).closeEvent(event)
        self.remove_maya_callbacks()
        self.deleteLater()