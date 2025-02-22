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

    WINDOW_NAME = None

    Q_OBJECT_NAME = None

    def __init__(self, parent=None, *args, **kwargs):
        super(DockableMainWindowAbstract, self).__init__(parent)
        self.setWindowTitle(self.WINDOW_NAME)
        self.setObjectName(self.Q_OBJECT_NAME)

        self._init_ui(*args, **kwargs)

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

    def _init_ui(self, *args, **kwargs):
        """initialize the ui"""
        self._central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self._central_widget)
        self._central_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self._main_layout = QtWidgets.QVBoxLayout()
        self._central_widget.setLayout(self._main_layout)
        self._main_layout.setStretch(1, 1)

        self._ui()

    @classmethod
    def load_ui(cls):
        """
        load the ui. close any existing instance of the window
        :return QMainWindow: returns window instance
        """
        # UI workspace Control needs to be deleted to create a new instance
        try:
            cmds.deleteUI("{0}WorkspaceControl".format(cls.Q_OBJECT_NAME))
        except Exception as e:
            pass
        ui = cls()
        ui.show(dockable=True)
        ui.raise_()
        return ui

