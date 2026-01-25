"""
User interface for managing rig selection options
TODO: implement the search/replace options 
"""
import os

try:
    from PySide2 import QtWidgets, QtCore, QtGui
    from shiboken2 import wrapInstance
except ModuleNotFoundError:
    from PySide6 import QtWidgets, QtCore, QtGui
    from shiboken6 import wrapInstance

from maya import cmds

from as_maya_tools.utilities.qt_utils import DockableMainWindowAbstract, TreeWidgetRightClickSupportAbstract, \
    ConfirmDialog, InformationDialog
from as_maya_tools.utilities import selection_set_utils, json_utils
from as_maya_tools import SELECTION_SET_DIRECTORY, SELECTION_SET_MANAGER_SETTINGS_PATH, STYLE_SHEETS_PATH
from as_maya_tools.stylesheets import guiResources

DEFAULT_SELECTION_SET_MANAGER_SETTINGS = \
    {
        "sub_folder": "",
        "use_file_namespace": True,
        "use_selected_namespace": False,
        "use_scene_namespace": False,
        "scene_namespace": "",
        "search_and_replace": False,
        "search_string": "",
        "replace_string": ""
    }


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

    HEADER_LABELS = ["Name"]

    def _pop_up_menu(self):
        """
        Create custom pop up menu
        """
        self.create_new_selection_set_action = self.popup_menu.addAction("Create New Selection Set")
        self.delete_selection_set_action = self.popup_menu.addAction("Delete Selection Set")


class SelectionSetManagerUI(DockableMainWindowAbstract):
    """
    Selection set manager
    """
    WINDOW_NAME = "Selection Set Manager"

    Q_OBJECT_NAME = "selection_set_manager"

    STYLE_SHEET_PATH = "{0}/theme/Flat/Dark/Cyan/Pink.qss".format(STYLE_SHEETS_PATH)

    def __init__(self, parent=None):
        super(SelectionSetManagerUI, self).__init__(parent)
        self.selection_set_create_folder_dialog = None
        self.selection_set_create_dialog = None

    def _ui(self):
        """
        UI to be built
        """
        # Frames, Groups and Layouts
        self.main_splitter = QtWidgets.QSplitter()
        self.left_panel_layout = QtWidgets.QVBoxLayout(self)
        self.right_panel_layout = QtWidgets.QVBoxLayout(self)
        self.selection_set_file_management_layout = QtWidgets.QHBoxLayout(self)
        self.namespace_settings_groupbox = QtWidgets.QGroupBox(self)
        self.namespace_settings_groupbox.setTitle("Namespace Settings")
        self.namespace_settings_groupbox.setProperty("Color", "Primary")
        self.namespace_settings_layout = QtWidgets.QVBoxLayout(self)
        self.search_and_replace_settings_groupbox = QtWidgets.QGroupBox(self)
        self.search_and_replace_settings_groupbox.setTitle("Search and Replace")
        self.search_and_replace_settings_groupbox.setProperty("Color", "Primary")
        self.search_and_replace_settings_layout = QtWidgets.QVBoxLayout(self)
        self.selection_set_creation_layout = QtWidgets.QHBoxLayout(self)
        self.selection_set_management_layout = QtWidgets.QVBoxLayout(self)
        self.selection_set_tree_groupbox = QtWidgets.QGroupBox(self)
        self.selection_set_tree_groupbox.setTitle("Selection Sets")
        self.selection_set_tree_groupbox.setProperty("Color", "Primary")

        # Widgets
        # file managment
        self.set_folder_combobox = QtWidgets.QComboBox(self)
        self.new_set_folder_button = QtWidgets.QPushButton("New Set Folder", self)
        self.delete_set_folder_button = QtWidgets.QPushButton("Delete Set Folder", self)
        # namespace settings widgets
        self.use_file_namespace_button = QtWidgets.QRadioButton("Use File Namespace", self)
        self.use_selection_namespace_button = QtWidgets.QRadioButton("Use Selection Namespace", self)
        self.use_scene_namespace_button = QtWidgets.QRadioButton("Use Scene Namespace", self)
        self.scene_namespaces_combobox = QtWidgets.QComboBox(self)
        self.name_space_combo_box_items = []  # NOTE: this is a var to store combo box items as a list of strings
        # search and replace settings widgets
        self.search_and_replace_checkbox = QtWidgets.QCheckBox(self)
        self.search_and_replace_checkbox.setText("Search and Replace")
        self.search_line_edit = QtWidgets.QLineEdit()
        self.search_line_edit.setPlaceholderText("Search")
        self.replace_line_edit = QtWidgets.QLineEdit()
        self.replace_line_edit.setPlaceholderText("Replace")
        # selection set creation
        self.create_selection_set_button = QtWidgets.QPushButton("Create Selection Set", self)
        self.delete_selection_set_button = QtWidgets.QPushButton("Delete Selection Set", self)
        # treeview interface
        self.selection_set_treeview = SelectionSetTreeView()
        self.selection_set_treeview.setProperty("Color", "Primary")
        self.selection_set_treeview.header().hide()

        # Connect UI
        # file management layout
        self.selection_set_file_management_layout.addWidget(self.set_folder_combobox)
        self.selection_set_file_management_layout.addWidget(self.new_set_folder_button)
        self.selection_set_file_management_layout.addWidget(self.delete_set_folder_button)
        # namespace settings layout
        self.namespace_settings_layout.addWidget(self.use_file_namespace_button)
        self.namespace_settings_layout.addWidget(self.use_selection_namespace_button)
        self.namespace_settings_layout.addWidget(
            self.use_scene_namespace_button)
        self.namespace_settings_layout.addWidget(self.scene_namespaces_combobox)
        self.namespace_settings_groupbox.setLayout(self.namespace_settings_layout)
        # search and replace settings layout
        self.search_and_replace_settings_layout.addWidget(self.search_and_replace_checkbox)
        self.search_and_replace_settings_layout.addWidget(self.search_line_edit)
        self.search_and_replace_settings_layout.addWidget(self.replace_line_edit)
        self.search_and_replace_settings_groupbox.setLayout(self.search_and_replace_settings_layout)
        # selection set management layout
        self.selection_set_creation_layout.addWidget(self.create_selection_set_button)
        self.selection_set_creation_layout.addWidget(self.delete_selection_set_button)
        self.selection_set_management_layout.addLayout(self.selection_set_creation_layout)
        self.selection_set_management_layout.addWidget(self.selection_set_treeview)
        self.selection_set_tree_groupbox.setLayout(self.selection_set_management_layout)
        # build left panel
        self.left_panel_layout.addLayout(self.selection_set_file_management_layout)
        self.left_panel_layout.addLayout(self.selection_set_creation_layout)
        self.left_panel_layout.addWidget(self.selection_set_tree_groupbox)
        # build right panel
        self.right_panel_layout.addWidget(self.namespace_settings_groupbox)
        self.right_panel_layout.addWidget(self.search_and_replace_settings_groupbox)
        # build panels
        self.left_panel_widget = QtWidgets.QWidget(self)
        self.right_panel_widget = QtWidgets.QWidget(self)
        self.left_panel_widget.setLayout(self.left_panel_layout)
        self.right_panel_widget.setLayout(self.right_panel_layout)
        self.main_splitter.addWidget(self.left_panel_widget)
        self.main_splitter.addWidget(self.right_panel_widget)
        # assign layout to main layout 
        self.main_layout.addWidget(self.main_splitter)

        self.setLayout(self.main_layout)

        # confirm dialogs
        self.delete_folder_confirm_dialog = ConfirmDialog(
            self,
            window_title="Warning",
            message="Are you sure you want to permanently delete the selection set folder?")
        self.delete_selectionset_confirm_dialog = ConfirmDialog(
            self,
            window_title="Warning",
            message="Are you sure you want to permanently delete the selection set file?")
        self.no_selectionset_folder_information_dialog = InformationDialog(
            self,
            window_title="Warning",
            message="No selection set created\nYou need to create a folder to store your selection sets first")
        self.selection_sets_in_folder_information_dialog = InformationDialog(
            self,
            window_title="Warning",
            message="There are still selection sets in the folder\nDelete the selection sets first")

        # Get the settings before setting anything up to avoid overwriting the settings while creating the ui
        selection_set_manager_settings = json_utils.read_offset_json_file(SELECTION_SET_MANAGER_SETTINGS_PATH,
                                                                          "selection_set_manager_settings")

        self._callback_populate_selection_set_folder_combobox()

        self._callback_populate_namespace_combobox()

        self._callback_init_selection_set_manager_settings(settings=selection_set_manager_settings)

        self._callback_use_scene_namespace()
        self._callback_search_and_replace()
        self._callback_populate_tree_view()

    def _setup_socket_connections(self):
        """
        setup socket connections
        """
        # ui callbacks
        self.use_file_namespace_button.toggled.connect(self._callback_update_settings_file)
        self.use_selection_namespace_button.toggled.connect(self._callback_update_settings_file)
        self.use_scene_namespace_button.toggled.connect(self._callback_use_scene_namespace)
        self.set_folder_combobox.currentTextChanged.connect(self._callback_selection_set_folder_changed)
        self.scene_namespaces_combobox.currentTextChanged.connect(self._callback_update_settings_file)
        self.search_and_replace_checkbox.stateChanged.connect(self._callback_search_and_replace)
        self.search_line_edit.textChanged.connect(self._callback_update_settings_file)
        self.replace_line_edit.textChanged.connect(self._callback_update_settings_file)
        # treeview callbacks
        self.selection_set_treeview.create_new_selection_set_action.triggered.connect(
            self._show_selection_set_create_dialog)
        self.selection_set_treeview.delete_selection_set_action.triggered.connect(
            self._callback_delete_selectionset_action_triggered)
        self.selection_set_treeview.clicked.connect(self._callback_select_selection_set_nodes)
        self.selection_set_treeview.itemSelectionChanged.connect(self._callback_select_selection_set_nodes)

        # button callbacks
        self.delete_selection_set_button.pressed.connect(self._callback_delete_selectionset_action_triggered)
        self.delete_set_folder_button.pressed.connect(self._callback_delete_folder_action_triggered)

        # dialog callbacks
        self.new_set_folder_button.pressed.connect(self._show_selection_set_create_folder_dialog)
        self.create_selection_set_button.pressed.connect(self._show_selection_set_create_dialog)
        self.delete_folder_confirm_dialog.accepted.connect(self._callback_delete_selection_set_folder)
        self.delete_selectionset_confirm_dialog.accepted.connect(self._callback_delete_selection_set_file)

    def _callback_init_selection_set_manager_settings(self, settings=None):
        """
        initiate the selection set manager settings. use default settings if none exist
        """
        if settings is None:
            json_utils.write_json_file(SELECTION_SET_MANAGER_SETTINGS_PATH, "selection_set_manager_settings",
                                       DEFAULT_SELECTION_SET_MANAGER_SETTINGS)
        if self._is_corrupt_settings(DEFAULT_SELECTION_SET_MANAGER_SETTINGS, settings):
            json_utils.write_json_file(SELECTION_SET_MANAGER_SETTINGS_PATH, "selection_set_manager_settings",
                                       DEFAULT_SELECTION_SET_MANAGER_SETTINGS)
        settings = json_utils.read_offset_json_file(SELECTION_SET_MANAGER_SETTINGS_PATH,
                                                    "selection_set_manager_settings")
        # If the settings is "" then we do nothing
        if not settings["sub_folder"] == "":
            # if the folder doesn't exist then we do nothing
            if settings["sub_folder"] in os.listdir(SELECTION_SET_DIRECTORY):
                self.set_folder_combobox.setCurrentText(settings["sub_folder"])

        self.use_file_namespace_button.setChecked(settings["use_file_namespace"])
        self.use_selection_namespace_button.setChecked(settings["use_selected_namespace"])
        self.use_scene_namespace_button.setChecked(settings["use_scene_namespace"])

        # set the combo box namespace text
        if settings["scene_namespace"] in self.name_space_combo_box_items:
            self.scene_namespaces_combobox.setCurrentText(settings["scene_namespace"])

        self.search_and_replace_checkbox.setChecked(settings["search_and_replace"])
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

    def _callback_update_settings_file(self):
        """
        update settings file
        """
        selection_set_manager_settings = {}
        selection_set_manager_settings["use_file_namespace"] = self.use_file_namespace_button.isChecked()
        selection_set_manager_settings["use_selected_namespace"] = self.use_selection_namespace_button.isChecked()
        selection_set_manager_settings["sub_folder"] = self.set_folder_combobox.currentText()
        selection_set_manager_settings["use_scene_namespace"] = self.use_scene_namespace_button.isChecked()
        selection_set_manager_settings["scene_namespace"] = self.scene_namespaces_combobox.currentText()
        selection_set_manager_settings["search_and_replace"] = self.search_and_replace_checkbox.isChecked()
        selection_set_manager_settings["search_string"] = self.search_line_edit.text()
        selection_set_manager_settings["replace_string"] = self.replace_line_edit.text()
        json_utils.write_json_file(SELECTION_SET_MANAGER_SETTINGS_PATH, "selection_set_manager_settings",
                                   selection_set_manager_settings)

    def _callback_delete_folder_action_triggered(self):
        """
        on delete folder action triggered
        """
        if self.set_folder_combobox.currentText() == "":
            return
        # if there are selection sets in the folder we cancel the action 
        if len(os.listdir(os.path.join(SELECTION_SET_DIRECTORY, self.set_folder_combobox.currentText()))) > 0:
            self.selection_sets_in_folder_information_dialog.show()
            return
        self.delete_folder_confirm_dialog.exec_()  # exec_() causes weird error making button not update from the push color

    def _callback_delete_selectionset_action_triggered(self):
        """
        on delete selecton set action triggered
        """
        if self.set_folder_combobox.currentText() == "":
            return
        self.delete_selectionset_confirm_dialog.exec_()  # exec_() causes weird error making button not update from the push color

    def _callback_use_scene_namespace(self):
        """
        use scene namespace callback
        """
        self.scene_namespaces_combobox.setEnabled(self.use_scene_namespace_button.isChecked())
        self._callback_update_settings_file()

    def _callback_search_and_replace(self):
        """
        search and replace option check state callback action
        """
        self.search_line_edit.setEnabled(self.search_and_replace_checkbox.isChecked())
        self.replace_line_edit.setEnabled(self.search_and_replace_checkbox.isChecked())
        self._callback_update_settings_file()

    def _callback_populate_selection_set_folder_combobox(self):
        """
        update selection set folder combobox
        """
        self.set_folder_combobox.clear()
        # need to make sure the SELECTION_SETS folder is created on first use
        if not os.path.isdir(SELECTION_SET_DIRECTORY):
            os.makedirs(SELECTION_SET_DIRECTORY)
            return
        for folder in os.listdir(SELECTION_SET_DIRECTORY):
            if os.path.isdir(os.path.join(SELECTION_SET_DIRECTORY, folder)):
                self.set_folder_combobox.addItem(folder)
        return

    def _callback_populate_namespace_combobox(self):
        """
        update namespace option in namespace combo box
        """
        self.scene_namespaces_combobox.clear()
        scene_namespaces = cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True)
        for scene_namespace in scene_namespaces:
            # there are some namespaces that we can skip because they aren't related to node references
            if scene_namespace in ["UI", "shared"]:
                continue
            self.scene_namespaces_combobox.addItem(scene_namespace)
            self.name_space_combo_box_items.append(scene_namespace)
        return

    def _callback_selection_set_folder_changed(self):
        """
        selection set folder changed callback
        """
        self._callback_update_settings_file()
        self._callback_populate_tree_view()

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
        if self.set_folder_combobox.currentText() == "":
            self.no_selectionset_folder_information_dialog.show()
            return
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
        if os.path.exists(directory):
            os.rmdir(directory)
        self._callback_populate_selection_set_folder_combobox()
        return

    def _callback_delete_selection_set_file(self):
        """
        Delete selection set file
        """
        sub_folder = self.set_folder_combobox.currentText()
        for file_name in self._get_selected_selection_sets_from_tree_view():
            selection_set_utils.delete_selection_set(sub_folder=sub_folder, file_name=file_name)
        self._callback_populate_tree_view()
        return

    def _callback_select_selection_set_nodes(self):
        """
        Select selection set nodes based on treeview selection
        """
        nodes = list()
        settings = json_utils.read_offset_json_file(SELECTION_SET_MANAGER_SETTINGS_PATH,
                                                    "selection_set_manager_settings")

        for file_name in self._get_selected_selection_sets_from_tree_view():
            nodes += selection_set_utils.get_selection_set(
                file_name=file_name,
                **settings
            )
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
