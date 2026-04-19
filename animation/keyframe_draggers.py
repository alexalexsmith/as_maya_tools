"""
Dragger context tools
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

    def _init_subclass(self, *args, **kwargs):
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

    def press(self, *args, **kwargs):
        """
        Actions taking place on press action
        """
        # set keyframe will set a keyframe on all attributes
        cmds.setKeyframe()

    def drag(self, *args, **kwargs):
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
    You can use translate, rotate, scale bool parameters from math_utils.lerp_matrix() to define what gets lerped
    """
    NAME = "WorldSpace Tween Dragger"
    TITLE = "WorldSpace Tween Dragger"
    CURSOR = "hand"
    DEFAULT_VALUE = 0.5
    ICON = f"{ICONS}/wstweendragger.png"
    TRANSFORM_ATTRIBUTES = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"]

    def __init__(self, *args, **kwargs):
        super(WSTweenDragger, self).__init__(*args, **kwargs)

    def _init_subclass(self, *args, **kwargs):
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

            if not cmds.findKeyframe(node, curve=True):
                continue

            previous_keyframe = cmds.findKeyframe(node, which="previous")  # NOTE: default is current time
            next_keyframe = cmds.findKeyframe(node, which="next")  # NOTE: default is current time

            # get the world matrix values
            pre_frame_matrix = OpenMaya.MMatrix(cmds.getAttr(f"{node}.worldMatrix", time=previous_keyframe))
            next_frame_matrix = OpenMaya.MMatrix(cmds.getAttr(f"{node}.worldMatrix", time=next_keyframe))

            data = {"pre_frame_matrix": pre_frame_matrix, "next_frame_matrix": next_frame_matrix}
            self.node_data[node] = data

            if len(self.node_data) == 0:
                maya_utils.message("No nodes found to tween", record_warning=False)
                raise ValueError("No nodes found to tween. Make sure there are keyframes to tween and transform attributes are keyable")

    def press(self, *args, **kwargs):
        """
        Actions taking place on press action
        """
        # set keyframes on transform attributes
        cmds.setKeyframe()

    def drag(self, *args, **kwargs):
        """
        Actions activated by left drag
        """
        for node in self.node_data:
            # get lerped matrix values
            lerped_matrix = math_utils.lerp_matrix(self.node_data[node]["pre_frame_matrix"],
                                                   self.node_data[node]["next_frame_matrix"],
                                                   self.x,
                                                   *args, **kwargs)
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

    def _init_subclass(self, *args, **kwargs):
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

    def press(self, *args, **kwargs):
        """
        Actions taking place on press action
        """
        # set keyframe will set a keyframe on all attributes
        cmds.setKeyframe()

    def drag(self, *args, **kwargs):
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


class CurveValueDragger(dragger_utils.Dragger):
    """
    Slide the current attribute values along the curve value
    """
    NAME = "Curve Value Dragger"
    TITLE = "Curve Value Dragger"
    CURSOR = "hand"
    DEFAULT_VALUE = 0.0
    MAX_MULTIPLIER = 1.0  # NOTE: the fastest the drag value will raise or lower
    MIN_MULTIPLIER = 0.1  # NOTE: the slowest the drag value will raise or lower
    ICON = f"{ICONS}/curvevaluedragger.png"

    def __init__(self, *args, **kwargs):
        super(CurveValueDragger, self).__init__(*args, **kwargs)

    def _init_subclass(self, *args, **kwargs):
        """
        init the dragger tool data
        """
        nodes = cmds.ls(selection=True)

        if nodes is None or len(nodes) == 0:
            maya_utils.message("0 nodes selected", position='midCenterTop', record_warning=False)
            raise ValueError("0 transform nodes selected")

        self.nodes = {}
        for node in nodes:
            attributes = cmds.listAttr(node, keyable=True, unlocked=True, shortNames=True)
            # skipping node if no animatable attributes are available
            if not attributes or len(attributes) == 0:
                continue

            self.nodes[node] = []
            for attribute in attributes:

                previous_keyframe = cmds.findKeyframe(f"{node}.{attribute}", which="previous")
                next_keyframe = cmds.findKeyframe(f"{node}.{attribute}", which="next")
                if not previous_keyframe:
                    continue
                if not next_keyframe:
                    continue

                self.nodes[node].append(f"{node}.{attribute}")

    def press(self, *args, **kwargs):
        """
        Actions taking place on press action
        """
        # set keyframe will set a keyframe on all attributes
        cmds.setKeyframe()

    def _set_cursor_label_drag_display(self, *args, **kwargs):
        """
        defines what is displayed on the cursor label and how it looks when dragging
        """
        self.cursor_label.set_color("white")
        label = f"frame:{round(self.time_drag,3)}"
        self.cursor_label.setText(label)

    def drag(self, *args, **kwargs):
        """
        Actions activated by left drag
        """
        self.time_drag = cmds.currentTime(query=True) + self.x

        for node in self.nodes:
            for attribute in self.nodes[node]:
                value = cmds.getAttr(attribute, time=self.time_drag)
                cmds.setAttr(attribute, value)


class LerpSnapDragger(dragger_utils.Dragger):
    """
    Lerp objects towards first selection
    You can use translate, rotate, scale bool parameters from math_utils.lerp_matrix() to define what gets lerped
    """
    NAME = "Lerp Snap Dragger"
    TITLE = "Lerp Snap Dragger"
    CURSOR = "hand"
    DEFAULT_VALUE = 0.0
    ICON = f"{ICONS}/lerpsnapdragger.png"

    def __init__(self, *args, **kwargs):
        super(LerpSnapDragger, self).__init__(*args, **kwargs)

    def _init_subclass(self, *args, **kwargs):
        """
        init the dragger tool data
        """
        nodes = cmds.ls(selection=True)

        if nodes is None or len(nodes) < 2:
            maya_utils.message("Not enough nodes selected. Select at least 2 nodes", position='midCenterTop', record_warning=False)
            raise ValueError("Not enough nodes selected. Select at least 2 nodes")

        self.snap_node_matrix = OpenMaya.MMatrix(cmds.xform(nodes[0], query=True, matrix=True, ws=True))
        self.node_data = {}
        for node in nodes:
            node_matrix = OpenMaya.MMatrix(cmds.xform(node, query=True, matrix=True, ws=True))
            self.node_data[node] = node_matrix

    def drag(self, *args, **kwargs):
        """
        Actions activated by left drag
        """
        for node in self.node_data:
            # get lerped matrix values
            lerped_matrix = math_utils.lerp_matrix(self.node_data[node],
                                                   self.snap_node_matrix,
                                                   self.x,
                                                   *args, **kwargs)
            cmds.xform(node, matrix=lerped_matrix, ws=True)


class CameraDepthDragger(dragger_utils.Dragger):
    """
    Lerp objects position towards or away from camera position
    """
    NAME = "Camera Depth Dragger"
    TITLE = "Camera Depth Dragger"
    CURSOR = "hand"
    DEFAULT_VALUE = 0.0
    ICON = f"{ICONS}/cameradepthdragger.png"

    def __init__(self, *args, **kwargs):
        super(CameraDepthDragger, self).__init__(*args, **kwargs)

    def _init_subclass(self, *args, **kwargs):
        """
        init the dragger tool data
        """
        # get the camera that we're looking through, and the objects selected
        camera = maya_utils.get_current_camera()
        nodes = cmds.ls(selection=True)

        if nodes is None or len(nodes) == 0:
            maya_utils.message("0 nodes selected", record_warning=False)
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
            maya_utils.message("No selected objects are translatable", record_warning=False)
            raise ValueError("No selected objects are translatable")

        if len(nodes) != len(self.node_data):
            maya_utils.message("Some selected objects cannot be translated", record_warning=True)

    def _set_cursor_label_drag_display(self, *args, **kwargs):
        """
        defines what is displayed on the cursor label and how it looks when dragging
        """
        self.cursor_label.set_color("white")
        label = f"X:{round(self.lerp_vector[0], 3)} Y:{round(self.lerp_vector[1], 3)} Z:{round(self.lerp_vector[2], 3)}"
        self.cursor_label.setText(label)

    def drag(self, *args, **kwargs):
        """
        pre_drag normal speed
        """
        self.lerp_vector = [0, 0, 0]
        for node in self.node_data:
            self.lerp_vector = math_utils.lerp_vector(self.node_data[node], self.camera_position, self.x)
            cmds.move(self.lerp_vector[0], self.lerp_vector[1], self.lerp_vector[2], node, absolute=True, worldSpace=True)
