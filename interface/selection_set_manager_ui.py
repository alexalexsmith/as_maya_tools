"""
User interface for managing rig selection options
TODO: tool should avoid listing the temp selection set and creating selection sets without a sub folder
"""
import os

try:
    from PySide2 import QtWidgets, QtCore, QtGui
    from shiboken2 import wrapInstance
except ModuleNotFoundError:
    from PySide6 import QtWidgets, QtCore, QtGui
    from shiboken6 import wrapInstance

from maya import cmds

from as_maya_tools.utilities.qt_utils import DockableMainWindowAbstract, TreeWidgetRightClickSupportAbstract
from as_maya_tools.utilities import selection_set_utils
from as_maya_tools import SELECTION_SET_DIRECTORY, STYLE_SHEETS_PATH


class CustomQFrame(QtWidgets.QFrame):
    """
    Custom QFrame with set style to keep my QFrames consistent
    """

    def __init__(self, parent=None):
        super(CustomQFrame, self).__init__(parent)
        self.setFrameStyle(QtWidgets.QFrame.StyledPanel | QtWidgets.QFrame.Plain)


class SelectionSetTreeView(TreeWidgetRightClickSupportAbstract):
    """
    Tree widget to display and manage attribute switching
    """

    HEADER_LABELS = ["Selection Sets"]

    def _pop_up_menu(self):
        """
        Create custom pop up menu
        """
        self.create_new_selection_set_action = self.popup_menu.addAction("Create New Selection Set")
        self.delete_selection_set_action = self.popup_menu.addAction("Delete Selection Set")


class SelectionSetManagerUI(DockableMainWindowAbstract):
    """
    Noise Generation settings ui
    """
    WINDOW_NAME = "Selection Set Manager"

    Q_OBJECT_NAME = "selection_set_manager"

    # STYLE_SHEET_PATH = "{0}/mortarheadd.qss".format(STYLE_SHEETS_PATH)

    def __init__(self, parent=None):
        super(SelectionSetManagerUI, self).__init__(parent)

        self.selection_set_create_folder_dialog = None
        self.selection_set_create_dialog = None

    def _ui(self):
        """
        UI to be built
        """
        # Frames, Groups and Layouts
        self.selection_set_file_management_layout = QtWidgets.QHBoxLayout(self)
        self.selection_set_creation_layout = QtWidgets.QHBoxLayout(self)

        # Widgets
        # file managment
        self.set_folder_combobox = QtWidgets.QComboBox(self)
        self.new_set_file_button = QtWidgets.QPushButton("New Set File", self)
        self.delete_set_file_button = QtWidgets.QPushButton("Delete Set File", self)
        # selection set creation
        self.create_selection_set_button = QtWidgets.QPushButton("Create Selection Set", self)
        self.delete_selection_set_button = QtWidgets.QPushButton("Delete Selection Set", self)
        # treeview interface
        self.selection_set_treeview = SelectionSetTreeView()

        # Connect UI
        # file management layout
        self.selection_set_file_management_layout.addWidget(self.set_folder_combobox)
        self.selection_set_file_management_layout.addWidget(self.new_set_file_button)
        self.selection_set_file_management_layout.addWidget(self.delete_set_file_button)
        # selection set creation layout
        self.selection_set_creation_layout.addWidget(self.create_selection_set_button)
        self.selection_set_creation_layout.addWidget(self.delete_selection_set_button)
        # assign layout to main layout 
        self.main_layout.addLayout(self.selection_set_file_management_layout)
        self.main_layout.addLayout(self.selection_set_creation_layout)
        self.main_layout.addWidget(self.selection_set_treeview)

        self.setLayout(self.main_layout)

        self._callback_populate_selection_set_folder_combobox()
        self._callback_populate_tree_view()

    def _setup_socket_connections(self):
        """
        setup socket connections
        """
        # ui callbacks
        self.set_folder_combobox.currentTextChanged.connect(self._callback_populate_tree_view)
        # treeview rightclick actions
        self.selection_set_treeview.create_new_selection_set_action.triggered.connect(
            self._show_selection_set_create_dialog)
        self.selection_set_treeview.delete_selection_set_action.triggered.connect(
            self._callback_delete_selection_set_file)
        # function callbacks
        self.selection_set_treeview.itemSelectionChanged.connect(self._callback_select_selection_set_nodes)
        self.delete_selection_set_button.pressed.connect(self._callback_delete_selection_set_file)
        self.delete_set_file_button.pressed.connect(self._callback_delete_selection_set_folder)
        # dialog callbacks
        self.new_set_file_button.pressed.connect(self._show_selection_set_create_folder_dialog)
        self.create_selection_set_button.pressed.connect(self._show_selection_set_create_dialog)

    def _callback_populate_selection_set_folder_combobox(self):
        """
        update selection set folder combobox
        """
        self.set_folder_combobox.clear()
        for folder in os.listdir(SELECTION_SET_DIRECTORY):
            if os.path.isdir(os.path.join(SELECTION_SET_DIRECTORY, folder)):
                self.set_folder_combobox.addItem(folder)
        return

    def _callback_populate_tree_view(self):
        """
        update treeview
        """
        self.selection_set_treeview.clear()
        if self.set_folder_combobox.currentText() == "":
            return
        for file in os.listdir(os.path.join(SELECTION_SET_DIRECTORY, self.set_folder_combobox.currentText())):
            if file.endswith(".json"):
                selection_set_item_widget = QtWidgets.QTreeWidgetItem([os.path.splitext(os.path.basename(file))[0], 0])
                self.selection_set_treeview.addTopLevelItem(selection_set_item_widget)
        return

    def _show_selection_set_create_dialog(self, *args):
        """
        Create a new selection set file
        """
        try:
            self.selection_set_create_dialog.close()
            self.selection_set_create_dialog.deleteLater()
        except (AttributeError, RuntimeError):
            pass
        self.selection_set_create_dialog = SelectionSetCreate(self)
        self.selection_set_create_dialog.show()

    def _show_selection_set_create_folder_dialog(self, *args):
        """
        Launch SimitRigCreatorDialog
        """
        try:
            self.selection_set_create_folder_dialog.close()
            self.selection_set_create_folder_dialog.deleteLater()
        except (AttributeError, RuntimeError):
            pass
        self.selection_set_create_folder_dialog = SelectionSetCreateFolder(self)
        self.selection_set_create_folder_dialog.show()

    def _callback_delete_selection_set_folder(self):
        """
        Delete selection set folder
        """
        sub_folder = self.set_folder_combobox.currentText()
        directory = os.path.join(SELECTION_SET_DIRECTORY, sub_folder)
        print(directory)
        if os.path.exists(directory):
            os.rmdir(directory)
        self._callback_populate_selection_set_folder_combobox()
        return

    def _callback_delete_selection_set_file(self):
        """
        Delete selection set file
        """
        # TODO: add warning dialog to avoid accidental deletion
        sub_folder = self.set_folder_combobox.currentText()
        for file_name in self._get_selected_selection_sets_from_tree_view():
            selection_set_utils.delete_selection_set(sub_folder=sub_folder, file_name=file_name)
        self._callback_populate_tree_view()
        return

    def _callback_select_selection_set_nodes(self):
        """
        Select selection set nodes based on treeview selection
        """
        sub_folder = self.set_folder_combobox.currentText()
        nodes = list()
        for file_name in self._get_selected_selection_sets_from_tree_view():
            nodes += selection_set_utils.get_selection_set(sub_folder=sub_folder, file_name=file_name)
        cmds.select(clear=True)
        cmds.select(nodes, add=True)

    def _get_selected_selection_sets_from_tree_view(self):
        """Get a list of names from the tree view selection
        :return: selection_sets
        :rtype: list[str]
        """
        selection_sets = list()
        for item in self.selection_set_treeview.selectedItems():
            selection_sets.append(item.text(0))
        return selection_sets


class SelectionSetCreateFolder(QtWidgets.QDialog):
    """
    Window for creating selectionset sub folder
    """

    def __init__(self, parent):
        super(SelectionSetCreateFolder, self).__init__(parent)
        self._window_name = "Create Folder"
        self._parent = parent
        # Create Widgets
        self._customUI()

        # Connect Signals
        self._setupSocketConnections()

    def keyPressEvent(self, event):
        """
        get key press event enter or return and run command for that key
        """
        super(SelectionSetCreateFolder, self).keyPressEvent(event)
        if event.key() in [QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter]:
            self._callback_create_folder()

    def _customUI(self):
        """
        target name custom ui
        """
        self.setWindowTitle(self._window_name)
        self._main_layout = QtWidgets.QVBoxLayout(self)
        self.resize(200, 100)
        self._name_row_layout = QtWidgets.QHBoxLayout(self)
        self._confirm_row_layout = QtWidgets.QHBoxLayout(self)

        self._name_label = QtWidgets.QLabel(self)
        self._name_label.setText("Folder Name")
        self._name_line_edit = QtWidgets.QLineEdit()
        self._name_line_edit.setPlaceholderText("Folder Name")

        self._btn_ok = QtWidgets.QPushButton("OK")
        self._btn_cancel = QtWidgets.QPushButton("Cancel")

        self._name_row_layout.addWidget(self._name_label)
        self._name_row_layout.addWidget(self._name_line_edit)

        self._confirm_row_layout.addWidget(self._btn_ok)
        self._confirm_row_layout.addWidget(self._btn_cancel)

        self._main_layout.addLayout(self._name_row_layout)
        self._main_layout.addLayout(self._confirm_row_layout)

        self._name_line_edit.setFocus()

    def _setupSocketConnections(self):
        """
        Create signal and slot connections for within the UI
        """
        self._btn_ok.clicked.connect(self._callback_create_folder)
        self._btn_cancel.clicked.connect(self._cancel_dialog)
        self._main_layout.keyPressEvent = self.keyPressEvent

    def _callback_create_folder(self):
        """
        Make sure the name is valid before creating simitRig
        """
        folder_name = self._name_line_edit.text()
        folder_path = os.path.join(SELECTION_SET_DIRECTORY, folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        self._parent._callback_populate_selection_set_folder_combobox()
        self.close()

    def _cancel_dialog(self):
        """
        close the dialog
        """
        self.close()

    def closeEvent(self, event):
        """
        On close delete from memory
        """
        super(SelectionSetCreateFolder, self).closeEvent(event)
        self.deleteLater()


class SelectionSetCreate(QtWidgets.QDialog):
    """
    Window for creating selection set
    """

    def __init__(self, parent):
        super(SelectionSetCreate, self).__init__(parent)
        self._window_name = "Create Selection Set"
        self._parent = parent
        # Create Widgets
        self._customUI()

        # Connect Signals
        self._setupSocketConnections()

    def keyPressEvent(self, event):
        """
        get key press event enter or return and run command for that key
        """
        super(SelectionSetCreate, self).keyPressEvent(event)
        if event.key() in [QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter]:
            self._callback_create_folder()

    def _customUI(self):
        """
        target name custom ui
        """
        self.setWindowTitle(self._window_name)
        self._main_layout = QtWidgets.QVBoxLayout(self)
        self.resize(200, 100)
        self._name_row_layout = QtWidgets.QHBoxLayout(self)
        self._confirm_row_layout = QtWidgets.QHBoxLayout(self)

        self._name_label = QtWidgets.QLabel(self)
        self._name_label.setText("Name")
        self._name_line_edit = QtWidgets.QLineEdit()
        self._name_line_edit.setPlaceholderText("Name")

        self._btn_ok = QtWidgets.QPushButton("OK")
        self._btn_cancel = QtWidgets.QPushButton("Cancel")

        self._name_row_layout.addWidget(self._name_label)
        self._name_row_layout.addWidget(self._name_line_edit)

        self._confirm_row_layout.addWidget(self._btn_ok)
        self._confirm_row_layout.addWidget(self._btn_cancel)

        self._main_layout.addLayout(self._name_row_layout)
        self._main_layout.addLayout(self._confirm_row_layout)

        self._name_line_edit.setFocus()

    def _setupSocketConnections(self):
        """
        Create signal and slot connections for within the UI
        """
        self._btn_ok.clicked.connect(self._callback_create_selection_set)
        self._btn_cancel.clicked.connect(self._cancel_dialog)
        self._main_layout.keyPressEvent = self.keyPressEvent

    def _callback_create_selection_set(self):
        """
        create selection set in the selection set sub folder
        """
        file_name = self._name_line_edit.text()
        sub_folder = self._parent.set_folder_combobox.currentText()
        selection_set_utils.create_selection_set(sub_folder=sub_folder, file_name=file_name)
        self._parent._callback_populate_tree_view()
        self.close()

    def _cancel_dialog(self):
        """
        close the dialog
        """
        self.close()

    def closeEvent(self, event):
        """
        On close delete from memory
        """
        super(SelectionSetCreate, self).closeEvent(event)
        self.deleteLater()
