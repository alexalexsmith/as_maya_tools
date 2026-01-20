"""
keyframe dragger context tools
"""
from maya import cmds
from maya import OpenMaya

from as_maya_tools.utilities import performance_utils, keyframe_utils


class TweenDragger(performance_utils.Dragger):

    def __init__(self,name = 'tweendragger',title = 'TweenDragger',defaultValue=0.5,minValue=None,maxValue=None,multiplier=0.01,cursor='hand'):
        performance_utils.Dragger.__init__(self, defaultValue=defaultValue, minValue=minValue, maxValue=maxValue, name=name, title=title)
        
        nodes = cmds.ls(selection=True)
        
        if nodes is None or len(nodes) == 0:
            performance_utils.message("no nodes specified to copy keyframes", position='midCenterTop', record_warning=True)
            return
            
        self.current_time = cmds.currentTime(query=True)
        self.curves = {}
        for node in nodes:
            animatable_attributes = cmds.listAttr(node, keyable=True, unlocked=True, shortNames=True)
            # skipping node if no animatable attributes are available
            if not animatable_attributes or len(animatable_attributes) == 0:
                continue
                
            for attribute in animatable_attributes:
            
                previous_keyframe = cmds.findKeyframe(f"{node}.{attribute}", which="previous")
                next_keyframe = cmds.findKeyframe(f"{node}.{attribute}", which="next")
                if not previous_keyframe:
                    continue
                if not next_keyframe:
                    continue
                # set keyframe to be manipulated
                cmds.setKeyframe(f"{node}.{attribute}",time=(self.current_time,))
                previous_keyframe_data = keyframe_utils.get_keyframe_data(node, attribute, previous_keyframe)
                next_keyframe_data = keyframe_utils.get_keyframe_data(node, attribute, next_keyframe)
                data = {}
                data["previous_keyframe_data"] = previous_keyframe_data
                data["next_keyframe_data"] = next_keyframe_data
                self.curves[f"{node}.{attribute}"] = data
                
        self.setTool()
        onscreenInstructions = 'Drag left or right to scale toward the previous or next keyframe value'
        self.drawString(onscreenInstructions)
        OpenMaya.MGlobal.displayWarning(onscreenInstructions)
                
    def dragLeft(self):
        '''
        Activated by the left mouse button, this scales keys toward or away from their default value.
        '''
        self.drawString('Scale '+str(int(self.x*100))+' %')
        for curve in self.curves:
            #cmds.keyframe(f"{node}.{attribute}", time=(current_time,), valueChange=previous_keyframe_data["value"]+((next_keyframe_data["value"]-previous_keyframe_data["value"])*value))
            cmds.keyframe(
                curve,
                time=(self.current_time,),
                valueChange=self.curves[curve]["previous_keyframe_data"]["value"]+((self.curves[curve]["next_keyframe_data"]["value"]-self.curves[curve]["previous_keyframe_data"]["value"])*self.x))
                