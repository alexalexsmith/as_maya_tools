"""
rig selection settings ui
"""
from PySide2 import QtWidgets, QtCore, QtGui

from maya import cmds

from as_maya_tools.utilities.qt_utils import DockableMainWindowAbstract


class CustomQFrame(QtWidgets.QFrame):
    """Class to define ui frame style for the ui"""
    def __init__(self, *args, **kwargs):
        super(CustomQFrame, self).__init__(*args, **kwargs)
        self.setFrameStyle(QtWidgets.QFrame.StyledPanel | QtWidgets.QFrame.Raised)
        self.setLineWidth(3)


class RigSelectionSettingsUI(DockableMainWindowAbstract):
    """
    Rig selection settings UI
    """
    WINDOW_NAME = "Rig Selection Settings"

    Q_OBJECT_NAME = "rig_selection_settings"

    def __init__(self, parent=None):
        super(RigSelectionSettingsUI, self).__init__(parent=parent)

    def _ui(self):
        """
        rig selection settings ui elements
        """
        # Frames, Groups and Layouts
        self.rig_context_dropdown_layout = QtWidgets.QVBoxLayout(self)
        self.selection_preferences_group = QtWidgets.QGroupBox("Selection Settings:")
        self.selection_preferences_layout = QtWidgets.QGridLayout(self)

        # WIDGETS:
        # rig definition context settings widgets
        self.rig_context_definition_label = QtWidgets.QLabel(self)
        self.rig_context_definition_label.setText("Rig Context Definition")
        #  rig definition context settings combo box and populating
        self.rig_context_definition_combo_box = QtWidgets.QComboBox(self)
        self.rig_context_definition_combo_box.setMinimumHeight(25)
        if get_rig_context_definition_files():
            for action in get_rig_context_definition_files():
                self.rig_context_definition_combo_box.addItem(action)
        # selection preferences labels
        self.visible_label = QtWidgets.QLabel(self)
        self.visible_label.setText("visible")
        self.keyed_label = QtWidgets.QLabel(self)
        self.keyed_label.setText("keyed")
        self.subtype_label = QtWidgets.QLabel(self)
        self.subtype_label.setText("subtype filer")
        # selection preferences checkboxes
        self.visible_checkbox = QtWidgets.QCheckBox(self)
        self.keyed_checkbox = QtWidgets.QCheckBox(self)
        self.subtype_checkbox = QtWidgets.QCheckBox(self)

        # BUILD LAYOUTS:
        # build rig context definition layout
        self.rig_context_dropdown_layout.addWidget(self.rig_context_definition_label)
        self.rig_context_dropdown_layout.addWidget(self.rig_context_definition_combo_box)
        # build selection prefs layout
        self.selection_preferences_layout.addWidget(self.visible_label, 0, 0)
        self.selection_preferences_layout.addWidget(self.visible_checkbox, 0, 1)
        self.selection_preferences_layout.addWidget(self.keyed_label, 1, 0)
        self.selection_preferences_layout.addWidget(self.keyed_checkbox, 1, 1)
        self.selection_preferences_layout.addWidget(self.subtype_label, 2, 0)
        self.selection_preferences_layout.addWidget(self.subtype_checkbox, 2, 1)
        # add group layout
        self.selection_preferences_group.setLayout(self.selection_preferences_layout)
        # Add everything to the main layout
        self._main_layout.addLayout(self.rig_context_dropdown_layout)
        self._main_layout.addWidget(self.selection_preferences_group)


def get_rig_context_definition_files():
    """
    Return a list of rig definition context files
    """
    rig_context_definition_files = ("default", "fake_example", "another_fake_context")
    return rig_context_definition_files
