"""
Copy/Paste settings ui
COPY arguments:
-all_keyframes: bool (copy all keyframes option. If false it will use the selected keyframes)
PASTE arguments:
-use_selection: bool (option to use the current selection. If false it will use the node names stored )
-use_current_time: bool (option to apply the animation at the current time. if false it will use the stored time)
-replace: bool (option to remove the current animation in the frame range before applying animation TODO:not implemented in backend yet)
-reverse: bool (option to reverse the animation when applying. Reverse is applied to the keyframe position and tangent positions, not the value)
"""
try:
    from PySide2 import QtWidgets, QtCore, QtGui
    from shiboken2 import wrapInstance
except ModuleNotFoundError:
    from PySide6 import QtWidgets, QtCore, QtGui
    from shiboken6 import wrapInstance

from as_maya_tools.utilities.qt_utils import DockableMainWindowAbstract
from as_maya_tools.utilities import json_utils, performance_utils
from as_maya_tools.animation import timeline
from as_maya_tools import COPY_PASTE_KEYFRAME_SETTINGS_PATH, STYLE_SHEETS_PATH
from as_maya_tools.stylesheets import guiResources


DEFAULT_COPY_PASTE_KEYFRAME_SETTINGS = \
    {
        "all_keyframes": False,
        "use_selection": True,
        "use_current_time": True,
        "reverse": False,
        "search_replace": False,
        "search_string": "",
        "replace_string": ""
    }


class CopyPasteKeyframesUI(DockableMainWindowAbstract):
    """
    Copy paste keyframes UI
    """
    WINDOW_NAME = "Copy Paste Keyframes"

    Q_OBJECT_NAME = "copy_paste_keyframes"

    STYLE_SHEET_PATH = "{0}/theme/Flat/Dark/Cyan/Pink.qss".format(STYLE_SHEETS_PATH)

    def __init__(self, parent=None):
        super(CopyPasteKeyframesUI, self).__init__(parent)

    def _ui(self):
        # Frames, Groups and Layouts
        # main_layout is created in parent class
        # self.main_layout = QtWidgets.QVBoxLayout(self)
        self.copy_settings_groupbox = QtWidgets.QGroupBox(self)
        self.copy_settings_groupbox.setTitle("Copy Settings")
        self.paste_settings_groupbox = QtWidgets.QGroupBox(self)
        self.paste_settings_groupbox.setTitle("Paste Settings")
        self.copy_settings_layout = QtWidgets.QVBoxLayout(self)
        self.paste_settings_layout = QtWidgets.QVBoxLayout(self)
        self.action_layout = QtWidgets.QHBoxLayout(self)
        # copy setting widgets
        self.all_keyframes_checkbox = QtWidgets.QCheckBox(self)
        self.all_keyframes_checkbox.setText("All Keyframes")
        # paste settings widgets
        self.use_selection_checkbox = QtWidgets.QCheckBox(self)
        self.use_selection_checkbox.setText("Use Selection")
        self.use_current_time_checkbox = QtWidgets.QCheckBox(self)
        self.use_current_time_checkbox.setText("Use Current Time")
        self.reverse_keyframes_checkbox = QtWidgets.QCheckBox(self)
        self.reverse_keyframes_checkbox.setText("Reverse Keyframes")
        # search and replace widgets
        self.search_and_replace_checkbox = QtWidgets.QCheckBox(self)
        self.search_and_replace_checkbox.setText("Search and Replace")
        self.search_line_edit = QtWidgets.QLineEdit()
        self.search_line_edit.setPlaceholderText("Search")
        self.replace_line_edit = QtWidgets.QLineEdit()
        self.replace_line_edit.setPlaceholderText("Replace")
        # action buttons
        self.copy_button = QtWidgets.QPushButton("Copy Keyframes", self)
        self.paste_button = QtWidgets.QPushButton("Paste Keyframes", self)
        # build copy settings layout
        self.copy_settings_layout.addWidget(self.all_keyframes_checkbox)
        self.copy_settings_groupbox.setLayout(self.copy_settings_layout)
        # build paste settings layout
        self.paste_settings_layout.addWidget(self.use_selection_checkbox)
        self.paste_settings_layout.addWidget(self.use_current_time_checkbox)
        self.paste_settings_layout.addWidget(self.reverse_keyframes_checkbox)
        self.paste_settings_layout.addWidget(self.search_and_replace_checkbox)
        self.paste_settings_layout.addWidget(self.search_line_edit)
        self.paste_settings_layout.addWidget(self.replace_line_edit)
        self.paste_settings_groupbox.setLayout(self.paste_settings_layout)
        # build action layout
        self.action_layout.addWidget(self.copy_button)
        self.action_layout.addWidget(self.paste_button)
        # parent to main layout
        self.main_layout.addWidget(self.copy_settings_groupbox)
        self.main_layout.addWidget(self.paste_settings_groupbox)
        self.main_layout.addLayout(self.action_layout)
        self.setLayout(self.main_layout)

        # Get the settings before setting anything up to avoid overwriting the settings while creating the ui
        copy_paste_keyframe_settings = json_utils.read_offset_json_file(COPY_PASTE_KEYFRAME_SETTINGS_PATH, "copy_paste_keyframe_settings")
        self._init_settings(settings=copy_paste_keyframe_settings)

    def _init_settings(self, settings=None):
        """
        initiate the selection settings. use default settings if none exist
        """
        if settings is None:
            json_utils.write_json_file(
                COPY_PASTE_KEYFRAME_SETTINGS_PATH,
                "copy_paste_keyframe_settings",
                DEFAULT_COPY_PASTE_KEYFRAME_SETTINGS)
            settings = json_utils.read_offset_json_file(
                COPY_PASTE_KEYFRAME_SETTINGS_PATH,
                "copy_paste_keyframe_settings")

        if self._is_corrupt_settings(DEFAULT_COPY_PASTE_KEYFRAME_SETTINGS, settings):
            json_utils.write_json_file(
                COPY_PASTE_KEYFRAME_SETTINGS_PATH,
                "copy_paste_keyframe_settings",
                DEFAULT_COPY_PASTE_KEYFRAME_SETTINGS)
            settings = json_utils.read_offset_json_file(
                COPY_PASTE_KEYFRAME_SETTINGS_PATH,
                "copy_paste_keyframe_settings")

        settings = json_utils.read_offset_json_file(COPY_PASTE_KEYFRAME_SETTINGS_PATH,
                                                    "copy_paste_keyframe_settings")

        self.all_keyframes_checkbox.setChecked(settings["all_keyframes"])
        self.use_selection_checkbox.setChecked(settings["use_selection"])
        self.use_current_time_checkbox.setChecked(settings["use_current_time"])
        self.reverse_keyframes_checkbox.setChecked(settings["reverse"])
        self.search_and_replace_checkbox.setChecked(settings["search_replace"])
        self.search_line_edit.setText(settings["search_string"])
        self.replace_line_edit.setText(settings["replace_string"])

    def _is_corrupt_settings(self, default_settings, settings):
        """
        check if the settings file is corrupt
        :param dict default_settings: the default settings containing proper formatting
        :param dict settings:  settings to check for corruption
        :return: bool
        """
        for setting_key in default_settings:
            if not setting_key in settings:
                return True
            if type(default_settings[setting_key]) != type(settings[setting_key]):
                return True
        return False

    def _update_settings(self):
        """
        update settings json file
        """
        copy_paste_keyframe_settings={}
        copy_paste_keyframe_settings["all_keyframes"] = self.all_keyframes_checkbox.isChecked()
        copy_paste_keyframe_settings["use_selection"] = self.use_selection_checkbox.isChecked()
        copy_paste_keyframe_settings["use_current_time"] = self.use_current_time_checkbox.isChecked()
        copy_paste_keyframe_settings["reverse"] = self.reverse_keyframes_checkbox.isChecked()
        copy_paste_keyframe_settings["search_replace"] = self.search_and_replace_checkbox.isChecked()
        copy_paste_keyframe_settings["search_string"] = self.search_line_edit.text()
        copy_paste_keyframe_settings["replace_string"] = self.replace_line_edit.text()
        json_utils.write_json_file(COPY_PASTE_KEYFRAME_SETTINGS_PATH, "copy_paste_keyframe_settings",
                                   copy_paste_keyframe_settings)

    def _setup_socket_connections(self):
        """
        setup socket connections
        """
        # settings updates
        self.all_keyframes_checkbox.stateChanged.connect(self._update_settings)
        self.use_selection_checkbox.stateChanged.connect(self._update_settings)
        self.use_current_time_checkbox.stateChanged.connect(self._update_settings)
        self.reverse_keyframes_checkbox.stateChanged.connect(self._update_settings)
        self.search_and_replace_checkbox.stateChanged.connect(self._update_settings)
        self.search_line_edit.textChanged.connect(self._update_settings)
        self.replace_line_edit.textChanged.connect(self._update_settings)
        # actions
        self.copy_button.pressed.connect(self._callback_copy_keyframe_action)
        self.paste_button.pressed.connect(self._callback_paste_keyframe_action)

    def _callback_copy_keyframe_action(self):
        """
        copy keyframe callback
        :return:
        """
        timeline.copy_keyframes()
        performance_utils.message(message="Copied Keyframes", record_warning=False)

    def _callback_paste_keyframe_action(self):
        """
        paste keyframe callback
        :return:
        """
        timeline.paste_keyframes()
        performance_utils.message(message="Pasted Keyframes", record_warning=False)
