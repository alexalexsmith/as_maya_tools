"""
Functions that speed up maya or replace maya cmds for better performance
"""

import maya.api.OpenMaya as OpenMaya
from maya import cmds, mel



def obj_exists(name):
    """
    check if an object, plug, attribute path exists in the current maya scene
    :param str name: name of node, plug, or attribute path
    :return bool: exists
    """
    selection = OpenMaya.MSelectionList()
    try:
        selection.add(name)
        return True
    except RuntimeError:
        return False
        
        
def message(message, position='midCenterTop', record_warning=True):
    """
    A nicer way to display messages to the user
    :param str message: text to display to user
    :param str position: The position that the message will appear at relative to the active viewport. The supported positions are:
                            "topLeft"
                            "topCenter"
                            "topRight"
                            "midLeft"
                            "midCenter"
                            "midCenterTop"
                            "midCenterBot"
                            "midRight"
                            "botLeft"
                            "botCenter"
                            "botRight"
    :param bool record_warning: Option to record the warning in the script output
    """
    
    OpenMaya.MGlobal.displayWarning(message)
    fadeTime = min(len(message)*100, 2000)
    cmds.inViewMessage( amg=message, pos=position, fade=True, fadeStayTime=fadeTime, dragKill=True)
    if record_warning:
        cmds.warning(message)
        
        
def progress_bar(status_string, max_value):
    """maya's main progress bar at lower left hand corner
    :param str status_string: status string when beginProgress is True
    :param int max_value: size of steps to show accurate percentage of action completion
    :return str gMainProgressBar: name of mayas main progress bar"""

    gMainProgressBar = mel.eval('$maya_main_progress_bar = $gMainProgressBar');
    cmds.progressBar(gMainProgressBar,
                     edit=True,
                     beginProgress=True,
                     isInterruptable=True,
                     status=status_string,
                     maxValue=max_value)
    return gMainProgressBar
    
    
class Dragger(object):

    def __init__(self,
                 name = 'mlDraggerContext',
                 title = 'Dragger',
                 defaultValue=0,
                 minValue=None,
                 maxValue=None,
                 multiplier=0.01,
                 cursor='hand'
                 ):

        self.multiplier = multiplier
        self.defaultValue = defaultValue
        self.minValue = minValue
        self.maxValue = maxValue
        #self.cycleCheck = cmds.cycleCheck(query=True, evaluation=True)

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

        self.anchorPoint = cmds.draggerContext(self.draggerContext, query=True, anchorPoint=True)
        self.button = cmds.draggerContext(self.draggerContext, query=True, button=True)

        # This turns off the undo queue until we're done dragging, so we can undo it.
        cmds.undoInfo(openChunk=True)


    def drag(self, *args):
        '''
        This is what is actually run during the drag, updating the coordinates and calling the
        placeholder drag functions depending on which button is pressed.
        '''

        self.dragPoint = cmds.draggerContext(self.draggerContext, query=True, dragPoint=True)

        #if this doesn't work, try getmodifier
        self.modifier = cmds.draggerContext(self.draggerContext, query=True, modifier=True)

        self.x = ((self.dragPoint[0] - self.anchorPoint[0]) * self.multiplier) + self.defaultValue
        self.y = ((self.dragPoint[1] - self.anchorPoint[1]) * self.multiplier) + self.defaultValue

        if self.minValue is not None and self.x < self.minValue:
            self.x = self.minValue
        if self.maxValue is not None and self.x > self.maxValue:
            self.x = self.maxValue

        #dragString
        if self.modifier == 'control':
            if self.button == 1:
                self.dragControlLeft(*args)
            elif self.button == 2:
                self.dragControlMiddle(*args)
        elif self.modifier == 'shift':
            if self.button == 1:
                self.dragShiftLeft(*args)
            elif self.button == 2:
                self.dragShiftMiddle(*args)
        else:
            if self.button == 1:
                self.dragLeft()
            elif self.button == 2:
                self.dragMiddle()

        cmds.refresh()

    def release(self, *args):
        '''
        Be careful overwriting the release method in child classes. Not closing the undo chunk leaves maya in a sorry state.
        '''
        # close undo chunk and turn cycle check back on
        cmds.undoInfo(closeChunk=True)
        #cmds.cycleCheck(evaluation=self.cycleCheck)
        mel.eval('SelectTool')

    def drawString(self, message):
        '''
        Creates a string message at the position of the pointer.
        '''
        cmds.draggerContext(self.draggerContext, edit=True, drawString=message)

    def dragLeft(self,*args):
        '''Placeholder for potential commands. This is meant to be overridden by a child class.'''
        pass

    def dragMiddle(self,*args):
        '''Placeholder for potential commands. This is meant to be overridden by a child class.'''
        pass

    def dragControlLeft(self,*args):
        '''Placeholder for potential commands. This is meant to be overridden by a child class.'''
        pass

    def dragControlMiddle(self,*args):
        '''Placeholder for potential commands. This is meant to be overridden by a child class.'''
        pass

    def dragShiftLeft(self,*args):
        '''Placeholder for potential commands. This is meant to be overridden by a child class.'''
        pass

    def dragShiftMiddle(self,*args):
        '''Placeholder for potential commands. This is meant to be overridden by a child class.'''
        pass

    #no drag right, because that is monopolized by the right click menu
    #no alt drag, because that is used for the camera

    def setTool(self):
        cmds.setToolTo(self.draggerContext)