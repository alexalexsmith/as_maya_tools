"""
Dragger utilities for creating viewport dragging tools
"""
import maya.api.OpenMaya as OpenMaya
from maya import cmds, mel

from as_maya_tools.utilities import qt_utils


class Dragger(object):
    """
    Dragger tool abstract. Used to run functions using the mouse drag to adjust values
    """

    def __init__(self,
                 name='dragger_context_tool',
                 title='Dragger',
                 default_value=0,
                 min_value=None,
                 max_value=None,
                 multiplier=0.01,
                 cursor='hand'
                 ):

        self.multiplier = multiplier
        self.default_value = default_value
        self.min_value = min_value
        self.max_value = max_value
        self.cursor_label = qt_utils.CursorLabel()
        self.cursor_label.show()

        self.draggerContext = name
        if not cmds.draggerContext(self.draggerContext, exists=True):
            self.draggerContext = cmds.draggerContext(self.draggerContext)

        cmds.draggerContext(self.draggerContext, edit=True,
                            pressCommand=self.press,
                            dragCommand=self.drag,
                            releaseCommand=self.release,
                            cursor=cursor,
                            drawString=title,
                            undoMode='all'
                            )

    def press(self, *args):
        '''
        Be careful overwriting the press method in child classes, because of the undoInfo openChunk
        '''

        self.anchor_point = cmds.draggerContext(self.draggerContext, query=True, anchorPoint=True)
        self.button = cmds.draggerContext(self.draggerContext, query=True, button=True)

        # This turns off the undo queue until we're done dragging, so we can undo it.
        cmds.undoInfo(openChunk=True)

    def drag(self, *args):
        '''
        This is what is actually run during the drag, updating the coordinates and calling the
        placeholder drag functions depending on which button is pressed.
        '''
        # show curser label when drag is activated

        self.dragPoint = cmds.draggerContext(self.draggerContext, query=True, dragPoint=True)

        # if this doesn't work, try getmodifier
        self.modifier = cmds.draggerContext(self.draggerContext, query=True, modifier=True)

        self.x = ((self.dragPoint[0] - self.anchor_point[0]) * self.multiplier) + self.default_value
        self.y = ((self.dragPoint[1] - self.anchor_point[1]) * self.multiplier) + self.default_value

        if self.min_value is not None and self.x < self.min_value:
            self.x = self.min_value
        if self.max_value is not None and self.x > self.max_value:
            self.x = self.max_value

        # dragString
        if self.modifier == 'control':
            if self.button == 1:
                self.drag_control_left(*args)
            elif self.button == 2:
                self.drag_control_middle(*args)
        elif self.modifier == 'shift':
            if self.button == 1:
                self.drag_shift_left(*args)
            elif self.button == 2:
                self.drag_shift_middle(*args)
        else:
            if self.button == 1:
                self.drag_left()
            elif self.button == 2:
                self.drag_middle()

        cmds.refresh()

    def release(self, *args):
        '''
        Be careful overwriting the release method in child classes. Not closing the undo chunk leaves maya in a sorry state.
        '''
        # close undo chunk and turn cycle check back on
        cmds.undoInfo(closeChunk=True)
        self.cursor_label.close()
        mel.eval('SelectTool')

    def set_curser_label(self, message):
        '''
        Creates a string message at the position of the pointer
        '''
        self.cursor_label.setText(message)

    def drag_left(self, *args):
        '''Placeholder for potential commands. This is meant to be overridden by a child class.'''
        pass

    def drag_middle(self, *args):
        '''Placeholder for potential commands. This is meant to be overridden by a child class.'''
        pass

    def drag_control_left(self, *args):
        '''Placeholder for potential commands. This is meant to be overridden by a child class.'''
        pass

    def drag_control_middle(self, *args):
        '''Placeholder for potential commands. This is meant to be overridden by a child class.'''
        pass

    def drag_shift_left(self, *args):
        '''Placeholder for potential commands. This is meant to be overridden by a child class.'''
        pass

    def drag_shift_middle(self, *args):
        '''Placeholder for potential commands. This is meant to be overridden by a child class.'''
        pass

    # no drag right, because that is monopolized by the right click menu
    # no alt drag, because that is used for the camera

    def set_tool(self):
        cmds.setToolTo(self.draggerContext)
