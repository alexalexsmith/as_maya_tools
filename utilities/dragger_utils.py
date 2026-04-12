"""
Dragger utilities for creating viewport dragging tools
"""
import maya.api.OpenMaya as OpenMaya
from maya import cmds, mel

from as_maya_tools.utilities import qt_utils, maya_utils


class Dragger(object):
    """
    Dragger tool abstract. Used to run functions using the mouse pre_drag to adjust values
    """
    NAME = None
    TITLE = None
    CURSOR = None
    DEFAULT_VALUE = None

    def __init__(self,
                 min_value=None,
                 max_value=None,
                 multiplier=0.01,
                 *args,
                 **kwargs
                 ):

        self.y = None
        self.x = None
        self.modifier = None  # NOTE: only 3 options "shift", "ctrl", "other". other is the alt key
        self.drag_point = None
        self.multiplier = multiplier
        self.min_value = min_value
        self.max_value = max_value
        self.cursor_label = self.__init_cursor_label(self.TITLE)

        self.dragger_context = self.NAME
        if not cmds.draggerContext(self.dragger_context, exists=True):
            self.dragger_context = cmds.draggerContext(self.dragger_context)

        cmds.draggerContext(self.dragger_context, edit=True,
                            pressCommand=self.__press,
                            dragCommand=self.__drag,
                            releaseCommand=self.__release,
                            cursor=self.CURSOR,
                            drawString=self.TITLE,
                            undoMode='all'
                            )
        try:
            self._init_subclass(*args, **kwargs)
            self.set_tool()
        except Exception:
            self.__release(*args, **kwargs)

    def _init_subclass(self, *args, **kwargs):
        """
        _init_subclass function for all subclasses. Raise an error when checking for failures
        """
        return

    @staticmethod
    def __init_cursor_label(label):
        """
        Initialize the cursor label
        :param label: string label to display
        :return: qt_utils.CursorLabel()
        """
        cursor_label = qt_utils.CursorLabel()
        cursor_label.setText(label)
        cursor_label.show()
        return cursor_label

    def __press(self, *args, **kwargs):
        """
        private press function. Undo chunk is opened here
        :return: None
        """
        self.anchor_point = cmds.draggerContext(self.dragger_context, query=True, anchorPoint=True)
        self.button = cmds.draggerContext(self.dragger_context, query=True, button=True)
        cmds.undoInfo(openChunk=True)
        self.press(*args, **kwargs)

    def press(self, *args, **kwargs):
        """
        Press function to be overwritten by subclass
        """
        return

    def __drag(self, *args, **kwargs):
        """
        private pre_drag function
        :return: None
        """

        self.drag_point = cmds.draggerContext(self.dragger_context, query=True, dragPoint=True)
        self.modifier = cmds.draggerContext(self.dragger_context, query=True, modifier=True)

        self.pre_drag(*args, **kwargs)

        self.x = ((self.drag_point[0] - self.anchor_point[0]) * self.multiplier) + self.DEFAULT_VALUE
        self.y = ((self.drag_point[1] - self.anchor_point[1]) * self.multiplier) + self.DEFAULT_VALUE

        if self.min_value is not None and self.x < self.min_value:
            self.x = self.min_value
        if self.max_value is not None and self.x > self.max_value:
            self.x = self.max_value

        self.drag(*args, **kwargs)

        self.set_cursor_label_drag_display(*args, **kwargs)
        cmds.refresh()

    def pre_drag(self, *args, **kwargs):
        """
        Pre Drag function to be overwritten by subclass
        """
        return

    def drag(self, *args, **kwargs):
        """
        Drag function to be overwritten by subclass
        """

    def set_cursor_label_drag_display(self, *args, **kwargs):
        """
        defines what is displayed on the cursor label and how it looks when dragging
        """
        self.cursor_label.setText(str(int(self.x * 100)))
        if int(self.x * 100) > 100 or int(self.x * 100) < 0:
            self.cursor_label.set_color("red")
        else:
            self.cursor_label.set_color("white")

    def __release(self, *args, **kwargs):
        """
        private release function
        """
        self.release()
        cmds.undoInfo(closeChunk=True)
        self.cursor_label.close()
        mel.eval('SelectTool')

    def release(self, *args, **kwargs):
        """
        release function to be overwritten by subclass
        """
        return

    def set_tool(self):
        cmds.setToolTo(self.dragger_context)
