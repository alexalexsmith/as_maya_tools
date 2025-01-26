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

    def __init__(self, parent=None):
        super(DockableMainWindowAbstract, self).__init__(parent)
        self.setWindowTitle(self.WINDOW_NAME) |
        self.setObjectName(self.Q_OBJECT_NAME)

    def closeEvent(self, event):
        """
        On close delete from memory
        """
        super(DockableMainWindowAbstract, self).closeEvent(event)
        self.deleteLater()

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

