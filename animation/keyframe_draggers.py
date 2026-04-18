"""
keyframe dragger context tools
"""
from maya import cmds
from maya.api import OpenMaya

from as_maya_tools.utilities import maya_utils, keyframe_utils, math_utils, dragger_utils, attribute_utils
from as_maya_tools import ICONS


class TweenDragger(dragger_utils.Dragger):
    """
    Drag context tool to lerp attribute value between previous and next keyframe value
    """
    NAME = "Tween Dragger"
    TITLE = "Tween Dragger"
    CURSOR = "hand"
    DEFAULT_VALUE = 0.5
    ICON = f"{ICONS}/tweendragger.png"

    def __init__(self, *args, **kwargs):
        super(TweenDragger, self).__init__(*args, **kwargs)

    def _init_subclass(self):
        """
        init the dragger tool data
        """
        nodes = cmds.ls(selection=True)

        if nodes is None or len(nodes) == 0:
            maya_utils.message("0 nodes selected", position='midCenterTop', record_warning=False)
            raise ValueError("0 transform nodes selected")

        self.attributes = None
        self.attribute_data = {}
        for node in nodes:
            self.attributes = cmds.listAttr(node, keyable=True, unlocked=True, shortNames=True)
            # skipping node if no animatable attributes are available
            if not self.attributes or len(self.attributes) == 0:
                continue

            for attribute in self.attributes:

                previous_keyframe = cmds.findKeyframe(f"{node}.{attribute}", which="previous")
                next_keyframe = cmds.findKeyframe(f"{node}.{attribute}", which="next")
                if not previous_keyframe:
                    continue
                if not next_keyframe:
                    continue

                previous_keyframe_data = cmds.getAttr(f"{node}.{attribute}", time=previous_keyframe)
                next_keyframe_data = cmds.getAttr(f"{node}.{attribute}", time=next_keyframe)
                data = {"previous_keyframe_value": previous_keyframe_data, "next_keyframe_value": next_keyframe_data}
                self.attribute_data[f"{node}.{attribute}"] = data

        if not self.attributes or len(self.attributes) == 0:
            maya_utils.message("No attributes found to tween", position='midCenterTop', record_warning=False)
            raise ValueError("No attributes found to tween")

    def press(self):
        """
        Actions taking place on press action
        """
        # set keyframe will set a keyframe on all attributes
        cmds.setKeyframe()

    def drag(self):
        """
        Actions activated by left drag
        """
        for attribute in self.attribute_data:
            cmds.keyframe(
                attribute,
                time=(cmds.currentTime(query=True),),
                valueChange=math_utils.lerp(
                    self.attribute_data[attribute]["previous_keyframe_value"],
                    self.attribute_data[attribute]["next_keyframe_value"],
                    self.x)
            )


class WSTweenDragger(dragger_utils.Dragger):
    """
    World space tween dragger tool
    """
    NAME = "WorldSpace Tween Dragger"
    TITLE = "WorldSpace Tween Dragger"
    CURSOR = "hand"
    DEFAULT_VALUE = 0.5
    ICON = f"{ICONS}/wstweendragger.png"
    TRANSFORM_ATTRIBUTES = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"]

    def __init__(self, *args, **kwargs):
        super(WSTweenDragger, self).__init__(*args, **kwargs)

    def _init_subclass(self):
        """
        init the dragger tool data
        """
        nodes = cmds.ls(selection=True)
        self.attributes = []

        if nodes is None or len(nodes) == 0:
            maya_utils.message("0 nodes selected", position='midCenterTop', record_warning=False)
            raise ValueError("0 transform nodes selected")

        self.node_data = {}
        for node in nodes:
            animatable_attributes = cmds.listAttr(node, keyable=True, unlocked=True, shortNames=True)
            # skipping node if no animatable attributes are available
            if not animatable_attributes or len(animatable_attributes) == 0:
                continue

            for attribute in animatable_attributes:
                if attribute in self.TRANSFORM_ATTRIBUTES:
                    self.attributes.append(f"{node}.{attribute}")

            previous_keyframe = cmds.findKeyframe(node, which="previous")
            next_keyframe = cmds.findKeyframe(node, which="next")
            if not previous_keyframe:
                continue
            if not next_keyframe:
                continue

            # get the world matrix values
            pre_frame_matrix = OpenMaya.MMatrix(cmds.getAttr(f"{node}.worldMatrix", time=previous_keyframe))
            next_frame_matrix = OpenMaya.MMatrix(cmds.getAttr(f"{node}.worldMatrix", time=next_keyframe))

            data = {"pre_frame_matrix": pre_frame_matrix, "next_frame_matrix": next_frame_matrix}
            self.node_data[node] = data

    def press(self):
        """
        Actions taking place on press action
        """
        # set keyframes on transform attributes
        cmds.setKeyframe()

    def drag(self):
        """
        Actions activated by left drag
        """
        for node in self.node_data:
            # get lerped matrix values
            lerped_matrix = math_utils.lerp_matrix(self.node_data[node]["pre_frame_matrix"],
                                                   self.node_data[node]["next_frame_matrix"], self.x)
            cmds.xform(node, matrix=lerped_matrix, ws=True)


class DefaultTweenDragger(dragger_utils.Dragger):
    """
    World space tween dragger tool
    """
    NAME = "Default Tween Dragger"
    TITLE = "Default Tween Dragger"
    CURSOR = "hand"
    DEFAULT_VALUE = 0.5
    ICON = f"{ICONS}/defaulttweendragger.png"

    def __init__(self, *args, **kwargs):
        super(DefaultTweenDragger, self).__init__(*args, **kwargs)

    def _init_subclass(self):
        """
        init the dragger tool data
        """
        nodes = cmds.ls(selection=True)

        if nodes is None or len(nodes) == 0:
            maya_utils.message("0 nodes selected", position='midCenterTop', record_warning=False)
            raise ValueError("0 transform nodes selected")

        self.attributes = None
        self.attribute_data = {}
        for node in nodes:
            self.attributes = cmds.listAttr(node, keyable=True, unlocked=True, shortNames=True)
            # skipping node if no animatable attributes are available
            if not self.attributes or len(self.attributes) == 0:
                continue

            for attribute in self.attributes:

                previous_keyframe = cmds.findKeyframe(f"{node}.{attribute}", which="previous")
                next_keyframe = cmds.findKeyframe(f"{node}.{attribute}", which="next")
                if not previous_keyframe:
                    continue
                if not next_keyframe:
                    continue

                as_attribute = attribute_utils.Attribute(f"{node}.{attribute}")
                default_value = as_attribute.get_default_value()
                current_value = as_attribute.value

                data = {"default_value": default_value, "current_value": current_value}
                self.attribute_data[f"{node}.{attribute}"] = data

        if not self.attributes or len(self.attributes) == 0:
            maya_utils.message("No attributes found to tween", position='midCenterTop', record_warning=False)
            raise ValueError("No attributes found to tween")

    def press(self):
        """
        Actions taking place on press action
        """
        # set keyframe will set a keyframe on all attributes
        cmds.setKeyframe()

    def drag(self):
        """
        Actions activated by left drag
        """
        for attribute in self.attribute_data:
            cmds.keyframe(
                attribute,
                time=(cmds.currentTime(query=True),),
                valueChange=math_utils.lerp(
                    self.attribute_data[attribute]["default_value"],
                    self.attribute_data[attribute]["current_value"],
                    self.x)
            )


class CameraDepthDragger(dragger_utils.Dragger):
    """
    World space tween dragger tool
    """
    NAME = "Camera Depth Dragger"
    TITLE = "Camera Depth Dragger"
    CURSOR = "hand"
    DEFAULT_VALUE = 0.5
    ICON = f"{ICONS}/cameradepthdragger.png"

    def __init__(self, *args, **kwargs):
        super(CameraDepthDragger, self).__init__(*args, **kwargs)

    def _init_subclass(self):
        """
        init the dragger tool data
        """
        # get the camera that we're looking through, and the objects selected
        camera = maya_utils.get_current_camera()
        nodes = cmds.ls(selection=True)

        if nodes is None or len(nodes) == 0:
            maya_utils.message("0 nodes selected", position='midCenterTop', record_warning=False)
            raise ValueError("0 transform nodes selected")

        # get the position of the camera in space and convert it to a vector
        self.camera_position = cmds.xform(camera, query=True, worldSpace=True, rotatePivot=True)

        self.node_data = {}
        for node in nodes:
            # make sure all translate attributes are settable
            if not cmds.getAttr(f"{node}.translate", settable=True):
                continue

            # get the position of the objects as a vector, and subtract the camera vector from that
            node_position = cmds.xform(node, query=True, worldSpace=True, rotatePivot=True)
            self.node_data[node] = node_position

        if not self.node_data:
            OpenMaya.MGlobal.displayWarning('No selected objects are freely translatable')
            return

        if len(nodes) != len(self.node_data):
            OpenMaya.MGlobal.displayWarning('Some objects skipped, due to not being freely translatable')

    def _set_cursor_label_drag_display(self, *args, **kwargs):
        """
        defines what is displayed on the cursor label and how it looks when dragging
        """
        self.cursor_label.set_color("white")
        label = f"X:{round(self.lerp_vector[0], 3)} Y:{round(self.lerp_vector[1], 3)} Z:{round(self.lerp_vector[2], 3)}"
        self.cursor_label.setText(label)

    def drag(self):
        """
        pre_drag normal speed
        """
        self.lerp_vector = [0, 0, 0]
        for node in self.node_data:
            self.lerp_vector = math_utils.lerp_vector(self.node_data[node], self.camera_position, self.x)
            cmds.move(self.lerp_vector[0], self.lerp_vector[1], self.lerp_vector[2], node, absolute=True, worldSpace=True)
