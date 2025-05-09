# TODO: add support for Pyside6 and shiboken6(maya 2025)
from PySide2 import QtWidgets, QtCore, QtGui
import shiboken2

from maya import cmds
import maya.OpenMayaUI as omui
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin


def get_maya_main_widget():
    """
    Get pointer to Maya's main window
    """
    maya_main_window_pointer = omui.MQtUtil.mainWindow()
    return shiboken2.wrapInstance(int(maya_main_window_pointer), QtWidgets.QWidget)


class DockableMainWindowAbstract(MayaQWidgetDockableMixin, QtWidgets.QMainWindow):
    """
    Abstract class to be subclassed for dockable windows in maya
    :param bool dockable: option to make window dockable. default is True
    :param str(file_path) stype_sheet: option to add a .qss style sheet to the window

    """

    WINDOW_NAME = None

    Q_OBJECT_NAME = None
    
    STYLE_SHEET_PATH = None

    def __init__(self, parent=None, *args, **kwargs):
        super(DockableMainWindowAbstract, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)

        self.setWindowTitle(self.WINDOW_NAME)
        self.setObjectName(self.Q_OBJECT_NAME)

        self._init_ui(*args, **kwargs)
        
        self._setup_socket_connections()
        self._set_style_sheet(self.STYLE_SHEET_PATH)
        
    def _set_style_sheet(self):
        """set the style sheet"""
        if self.STYLE_SHEET_PATH is None:
            return
            
        file = QtCore.QFile(self.STYLE_SHEET_PATH)
        file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text)
        stream = QtCore.QTextStream(file)
        self.setStyleSheet(stream.readAll())

    def closeEvent(self, event):
        """
        On close delete from memory
        """
        super(DockableMainWindowAbstract, self).closeEvent(event)
        self.deleteLater()

    def _ui(self):
        """
        UI widget to be implemented in subclass
        """
        return NotImplemented

    def _init_ui(self, style_sheet=None, status_bar=False, menu_bar=False, tool_bar=False, *args, **kwargs):
        """initialize the ui"""
        if style_sheet:
            self._set_style_sheet(style_sheet)

        if status_bar:
            self._init_status_bar()

        if menu_bar:
            self._init_menu_bar()

        if tool_bar:
            self._init_tool_bar()

        self._central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self._central_widget)
        self._central_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.main_layout = QtWidgets.QVBoxLayout()
        self._central_widget.setLayout(self.main_layout)
        self.main_layout.setStretch(1, 1)

        self._ui()

    def _init_status_bar(self):
        """
        Init status Bar widget
        """
        #NOTE: Setup the status Bar with options
        self._status_bar = QtWidgets.QStatusBar()
        self._status_bar.showMessage("Status bar ready.")
        self.setStatusBar(self._status_bar)

        #NOTE: Sets status bar object Name to "statusBar" and changes the color
        self._status_bar.setObjectName("statusBar")
        self.setStyleSheet("#statusBar {background-color:#faa300;color:#fff}")

    def _init_menu_bar(self):
        """
        Menu Bar Implementation Template
        """
        self.menu_bar = QtWidgets.QMenuBar()
        """ NOTE: example usage
        self._fileMenu = self._addMenuBarMenu('File', icon=None)
        self._saveAction = self._addMenuBarAction(
            self._fileMenu, 
            'Save File', 
            icon=None, 
            statusTip='Some Status Here'
        )
        self._fileMenu.addAction(self._saveAction)
        """
        self.setMenuBar(self.menu_bar)

    def _init_tool_bar(self):
        """
        Sets up optional Toolbar for the UI
        """
        self._toolbar = QtWidgets.QToolBar(self)
        self.addToolBar(QtCore.Qt.LeftToolBarArea, self._toolbar)
        self._toolbar.setIconSize(QtCore.QSize(self.toolbarIconSize, self.toolbarIconSize))

    def _addMenuBarMenu(self, menuName, icon=None):
        """
        Called when Status Bar State is Changed
        """
        newMenuItem = None
        if icon and os.path.isfile(icon):
            _icon = QtGui.QIcon()
            _iconPix = QtGui.QPixmap(icon)
            _icon.addPixmap(_iconPix, QtGui.QIcon.Active, QtGui.QIcon.On)
            newMenuItem = self.menuBar.addMenu(_icon, menuName)
        else:
            newMenuItem = self.menuBar.addMenu(menuName)
        return newMenuItem

    def _addMenuBarAction(self, parentMenu, itemName, icon=None,
                          statusTip=None, data=None, checkable=False):
        """
        adds menu bar action item to parent menu

        :param QMenu parentMenu: parent meny for action
        "param str itemName: name for action label
        :param str icon: optional icon file to use for action item
        :parma str statusTip: optional status tip to display for action
        :param object data: optional data for action item to hold
        :parma bool checkable: does action item have a checkbox
        """
        actionItem = None
        if not parentMenu:
            return None

        actionItem = parentMenu.addAction(itemName)

        if icon and os.path.isfile(icon):
            _icon = QtGui.QIcon()
            _iconPix = QtGui.QPixmap(icon)
            _icon.addPixmap(_iconPix, QtGui.QIcon.Normal, QtGui.QIcon.On)
            actionItem.setIcon(_icon)

        if statusTip:
            actionItem.setStatusTip(str(statusTip))

        if data:
            actionItem.setData(data)

        actionItem.setCheckable(checkable)
        return actionItem

    def _setup_socket_connections(self):
        """
        setup socket connections in subclass
        """
        return NotImplemented

    def _set_style_sheet(self, style_sheet):
        """set the style sheet"""
        file = QtCore.QFile(style_sheet)
        file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text)
        stream = QtCore.QTextStream(file)
        self.setStyleSheet(stream.readAll())

    @classmethod
    def load_ui(cls, dockable=True, *args, **kwargs):
        """
        load the ui. close any existing instance of the window
        :return QMainWindow: returns window instance
        """
        # UI workspace Control needs to be deleted to create a new instance
        work_space_control = "{0}WorkspaceControl".format(cls.Q_OBJECT_NAME)
        if cmds.workspaceControl(work_space_control, q=True, exists=True):
            cmds.workspaceControl(work_space_control, e=True, close=True)
            cmds.deleteUI(work_space_control, control=True)

        maya_window = get_maya_main_widget()
        for qt_object in maya_window.children():
            if not isinstance(qt_object, QtWidgets.QWidget):
                continue
            if qt_object.windowTitle() == cls.WINDOW_NAME:
                qt_object.close()
        ui = cls(*args, **kwargs)
        ui.show(dockable=dockable)
        ui.raise_()
        return ui
        
        
class TreeWidgetRightClickSupportAbstract(QtWidgets.QTreeWidget):
    """
    Custom Tree Widget With default right click menu support
    """

    HEADER_LABELS = None
    FONT = "Verdana"
    FONT_SIZE = 10

    def __init__(self, parent=None, *args, **kwargs):
        super(TreeWidgetRightClickSupportAbstract, self).__init__(parent=parent, *args, **kwargs)
        #self.setFont(QtGui.QFont(self.FONT, self.FONT_SIZE, QtGui.QFont.Bold))
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setHeaderLabels(self.HEADER_LABELS)
        self.setAlternatingRowColors(True)
        self._init_popup_menu()

    def _init_popup_menu(self):
        """Build Main UI elements"""
        #  NOTE: creates the connections for popup menus
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_popup)
        #  NOTE: Init a popup menu
        self.popup_menu = QtWidgets.QMenu()
        self._pop_up_menu()

    def _pop_up_menu(self):
        """
        Create custom pop up menu
        """
        return NotImplemented

    def show_popup(self, position):
        """
        Shows Custom Popup menus for User

        :param QPosition position: passed by signal where to display popup
        """
        _value = self.popup_menu.exec_(self.mapToGlobal(position))
