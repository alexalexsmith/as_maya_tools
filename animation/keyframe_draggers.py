"""
keyframe dragger context tools
"""
from maya import cmds
from maya.api import OpenMaya

from as_maya_tools.utilities import maya_utils, keyframe_utils, math_utils, dragger_utils


class TweenDragger(dragger_utils.Dragger):

    def __init__(self,
                 name='tweendragger',
                 title='TweenDragger',
                 default_value=0.5,
                 min_value=None,
                 max_value=None,
                 multiplier=0.01,
                 cursor='hand'):
        dragger_utils.Dragger.__init__(self, default_value=default_value, min_value=min_value, max_value=max_value,
                                       name=name, title=title)

        nodes = cmds.ls(selection=True)

        if nodes is None or len(nodes) == 0:
            maya_utils.message("no nodes specified to copy keyframes", position='midCenterTop', record_warning=True)
            self.release()
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
                cmds.setKeyframe(f"{node}.{attribute}", time=(self.current_time,))
                previous_keyframe_data = keyframe_utils.get_keyframe_data(node, attribute, previous_keyframe)
                next_keyframe_data = keyframe_utils.get_keyframe_data(node, attribute, next_keyframe)
                data = {"previous_keyframe_data": previous_keyframe_data, "next_keyframe_data": next_keyframe_data}
                self.curves[f"{node}.{attribute}"] = data
        self.set_curser_label("dragtween")
        self.set_tool()

    def drag_left(self):
        """
        Activated by the left mouse button, this scales keys toward or away from their default value.
        """
        self.set_curser_label(str(self.x))
        for curve in self.curves:
            cmds.keyframe(
                curve,
                time=(self.current_time,),
                valueChange=self.curves[curve]["previous_keyframe_data"]["value"] + ((self.curves[curve][
                                                                                          "next_keyframe_data"][
                                                                                          "value"] - self.curves[curve][
                                                                                          "previous_keyframe_data"][
                                                                                          "value"]) * self.x))


class WSTweenDragger(dragger_utils.Dragger):

    def __init__(self, name='wstweendragger', title='WorldSpaceTweenDragger', default_value=0.5, min_value=None,
                 max_value=None, multiplier=0.01, cursor='hand'):
        dragger_utils.Dragger.__init__(self, default_value=default_value, min_value=min_value, max_value=max_value,
                                       name=name, title=title)

        nodes = cmds.ls(selection=True)

        if nodes is None or len(nodes) == 0:
            maya_utils.message("no nodes specified to copy keyframes", position='midCenterTop', record_warning=True)
            self.release()
            return

        self.current_time = cmds.currentTime(query=True)
        self.curves = {}
        for node in nodes:

            animatable_attributes = cmds.listAttr(node, keyable=True, unlocked=True, shortNames=True)
            # skipping node if no animatable attributes are available
            if not animatable_attributes or len(animatable_attributes) == 0:
                continue

            previous_keyframe = cmds.findKeyframe(node, which="previous")
            next_keyframe = cmds.findKeyframe(node, which="next")
            if not previous_keyframe:
                continue
            if not next_keyframe:
                continue
            # set keyframe to be manipulated
            cmds.setKeyframe(node, time=(self.current_time))

            # get the worldmatrix values
            pre_frame_matrix = OpenMaya.MMatrix(cmds.getAttr(f"{node}.worldMatrix", time=previous_keyframe))
            next_frame_matrix = OpenMaya.MMatrix(cmds.getAttr(f"{node}.worldMatrix", time=next_keyframe))

            data = {"pre_frame_matrix": pre_frame_matrix, "next_frame_matrix": next_frame_matrix}
            self.curves[node] = data
        self.set_curser_label("left click and drag to tween motion")
        self.set_tool()

    def drag_left(self):
        """
        Activated by the left mouse button, this scales keys toward or away from their default value.
        """
        self.set_curser_label(str(self.x))
        for curve in self.curves:
            # get lerp values
            lerped_matrix = math_utils.lerp_matrix(self.curves[curve]["pre_frame_matrix"],
                                                   self.curves[curve]["next_frame_matrix"], self.x)
            cmds.xform(matrix=lerped_matrix, ws=True)


class CameraDepthDragger(dragger_utils.Dragger):

    def __init__(self,
                 name='mlCameraDepthDraggerContext',
                 min_value=None,
                 max_value=None,
                 default_value=0,
                 title='CameraDepth'):

        dragger_utils.Dragger.__init__(self, default_value=default_value, min_value=min_value, max_value=max_value,
                                       name=name, title=title)

        # get the camera that we're looking through, and the objects selected
        cam = maya_utils.get_current_camera()
        sel = cmds.ls(sl=True)

        if not sel:
            OpenMaya.MGlobal.displayWarning('Please make a selection.')
            self.release()
            return

        # get the position of the camera in space and convert it to a vector
        cam_pnt = cmds.xform(cam, query=True, worldSpace=True, rotatePivot=True)
        self.cameraVector = math_utils.Vector(cam_pnt[0], cam_pnt[1], cam_pnt[2])

        self.objs = list()
        self.vector = list()
        self.normalized = list()
        for obj in sel:
            # make sure all translate attributes are settable
            if not cmds.getAttr(obj + '.translate', settable=True):
                print('not settable')
                continue

            # get the position of the objects as a vector, and subtract the camera vector from that
            obj_pnt = cmds.xform(obj, query=True, worldSpace=True, rotatePivot=True)
            obj_vec = math_utils.Vector(obj_pnt[0], obj_pnt[1], obj_pnt[2])
            self.objs.append(obj)
            self.vector.append(obj_vec - self.cameraVector)
            self.normalized.append(self.vector[-1].normalized())

        if not self.objs:
            OpenMaya.MGlobal.displayWarning('No selected objects are freely translatable')
            return

        if len(sel) != len(self.objs):
            OpenMaya.MGlobal.displayWarning('Some objects skipped, due to not being freely translatable')

        self.set_tool()

    def drag_mult(self, mult):
        # as the mouse is dragging, update the position of each object by muliplying
        # the vector and adding to the original position
        for obj, v, n in zip(self.objs, self.vector, self.normalized):
            vector = (n * self.x * mult) + v + self.cameraVector

            cmds.move(vector[0], vector[1], vector[2], obj, absolute=True, worldSpace=True)

    def drag_left(self):
        """
        drag normal speed
        """
        self.drag_mult(4)
