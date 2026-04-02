"""
Functions that replace maya functions for speed
Common maya functions to reduce redundancies or forcing everything to be included in an object
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
        
        
def get_current_camera():
    '''
    Returns the camera that you're currently looking through.
    If the current highlighted panel isn't a modelPanel,
    '''

    panel = cmds.getPanel(withFocus=True)

    if cmds.getPanel(typeOf=panel) != 'modelPanel':
        #just get the first visible model panel we find, hopefully the correct one.
        for p in cmds.getPanel(visiblePanels=True):
            if cmds.getPanel(typeOf=p) == 'modelPanel':
                panel = p
                cmds.setFocus(panel)
                break

    if cmds.getPanel(typeOf=panel) != 'modelPanel':
        OpenMaya.MGlobal.displayWarning('Please highlight a camera viewport.')
        return False

    camShape = cmds.modelEditor(panel, query=True, camera=True)
    if not camShape:
        return False

    camNodeType = cmds.nodeType(camShape)
    if cmds.nodeType(camShape) == 'transform':
        return camShape
    elif cmds.nodeType(camShape) in ['camera','stereoRigCamera']:
        return cmds.listRelatives(camShape, parent=True, path=True)[0]   
        
        
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
                     max_value=max_value)
    return gMainProgressBar
    
    
class Dragger(object):
    """
    Dragger tool abstract. Used to run functions using the mouse drag to adjust values
    """
    def __init__(self,
                 name = 'mlDraggerContext',
                 title = 'Dragger',
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
        self.cursor_hud = None
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

        self.x = ((self.dragPoint[0] - self.anchorPoint[0]) * self.multiplier) + self.default_value
        self.y = ((self.dragPoint[1] - self.anchorPoint[1]) * self.multiplier) + self.default_value

        if self.min_value is not None and self.x < self.min_value:
            self.x = self.min_value
        if self.max_value is not None and self.x > self.max_value:
            self.x = self.max_value

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
        #if self.hud:
        #    cmds.headsUpDisplay( self.hud, rem=True )
        mel.eval('SelectTool')

    def drawString(self, message):
        '''
        Creates a string message at the position of the pointer
        This only works in the legacy viewport, need Viewport2.0 compatability
        '''
        cmds.draggerContext(self.draggerContext, edit=True, drawString=message)
        #self.hud = cmds.headsUpDisplay('drag_HUD',
        #                                section=1,
        #                                block=0,
        #                                label='Drag:',
        #                                command=lambda: message,
        #                                event='timeChanged')

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