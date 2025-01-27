"""
Rig selection utilities
"""
import os
import re

from maya import cmds

from as_maya_tools import USER_DATA_PATH

# based on AdvancedSkeleton rig builds https://animationstudios.com.au/
DEFAULT_RIG_SELECTION_CONTEXT = \
    {
        "node_types": ("nurbsCurve", "objectSet"),
        "all": ("ControlSet", "FaceControlSet"),
        "position":
            {
                "regrex": r".*(_L|_R)$",
                "side": ("_L", "_R"),
            },
        "sets":
            {
                "head": ("Head", "Neck", "SplineN"),
                "eye": ("Eye", "EyeBrow", "Brow"),
                "eyelid": ("Lid", "lid"),
                "mouth": ("Jaw", "Mouth", "Lip", "Tongue", "Teeth", "Smile", "Phonemes"),
                "ear": ("Ear", "EarLobe"),
                "spine": ("Spine", "spine"),
                "arm": ("Scapular", "Scapula", "Arm", "Elbow", "Shoulder", "Wrist"),
                "hand": ("Hand", "Thumb", "Index", "Middle", "Ring", "Pinky", "Fingers"),
                "legs": ("Leg", "Hip", "Knee", "Ankle", "Toes", "Heel", "Pelvis", "Rump"),
                "foot": ("Foot", "Toe", "toe"),
                "tail": ("Tail", "tail"),
            },
        "subsets":
            {
                "ik": ("IK"),
                "fk": ("FK"),
                "bend": ("Bend"),
            },
        "exclude": ("Part", "EyeRegion", "EyeBrowRegion"),
    }


class RigControl(object):
    """
    Rig control object
    """

    def __init__(self, rig_context, node):
        """
        :param dict rig_context: rig context dictionary
        :param str node: name of the control node
        """
        self.rig_context = rig_context
        self.full_name = node
        self.name = None
        self.namespace = None
        self.side = None
        self.set = None
        self.subset = None

        self._init_name()
        self._init_side()
        self._init_set()
        self._init_subset()

    def _init_name(self):
        """init the name and namespace for the control"""
        self.name = self.full_name
        if ":" in self.full_name:
            self.namespace, self.name = self.full_name.split(":")

    def _init_side(self):
        """init the side of the control"""
        side_match = re.match(self.rig_context["position"]["regrex"], self.name)
        if side_match:
            self.side = side_match.group(1)

    def _init_set(self):
        """init the set the control belongs to"""
        for set_name in self.rig_context["sets"]:
            for set_definition in self.rig_context["sets"][set_name]:
                if set_definition in self.name:
                    self.set = set_name
                    break

    def _init_subset(self):
        """init the subset for the control"""
        for subset in self.rig_context["subsets"]:
            for subset_definition in subset:
                if subset_definition in self.name:
                    self.subset = subset
                    break


def get_all_controls(**kwargs):
    """
    get all controls based on selection and rig context
    TODO: implement ability to determine context of rig based on selected node
    :return list[str] all_controls: list of all control node names, or a set node containing all controls
    """
    rig_context = get_selection_rig_context(**kwargs)
    nodes = cmds.ls(selection=True)
    rig_controls = get_rig_control_objects_from_list(rig_context, nodes, **kwargs)

    if len(rig_controls) == 0:
        print("No rig controls found in selection")
        return []
    all_controls = []
    for rig_control in rig_controls:
        if rig_control.namespace:
            for node_name in rig_context["all"]:
                control_to_add = "{0}:{1}".format(rig_control.namespace, node_name)
                if not cmds.objExists(control_to_add):
                    continue
                all_controls.append(control_to_add)
        else:
            if not cmds.objExists(rig_context["all"]):
                continue
            all_controls.append(rig_context["all"])
    return all_controls


def get_mirror_controls(**kwargs):
    """
    get the mirror controls based on selection and rig context
    :return list[str] mirror_controls: list of mirror control node names
    """
    rig_context = get_selection_rig_context(**kwargs)
    nodes = cmds.ls(selection=True)
    rig_controls = get_rig_control_objects_from_list(rig_context, nodes, **kwargs)

    mirror_controls = []
    for rig_control in rig_controls:
        if not rig_control.side:
            continue
        position_regrex_match = re.search(rig_context["position"]["regrex"], rig_control.name)
        if position_regrex_match:
            side = position_regrex_match.group(1)
            if side in (rig_context["position"]["side"])[0]:
                side = (rig_context["position"]["side"])[1]
            else:
                side = (rig_context["position"]["side"])[0]
            start, end = position_regrex_match.span(1)
            mirror_name = "{0}{1}{2}".format(rig_control.name[:start], side, rig_control.name[end:])
            if rig_control.namespace:
                control_to_add = "{0}:{1}".format(rig_control.namespace, mirror_name)
                if not cmds.objExists(control_to_add):
                    continue
                mirror_controls.append("{0}:{1}".format(rig_control.namespace, mirror_name))
            else:
                if not cmds.objExists(mirror_name):
                    continue
                mirror_controls.append(mirror_name)
    return mirror_controls


def get_set_controls(ignore_side=False, **kwargs):
    """
    get set controls based on selection and rig context
    :param bool ignore_side: ignore side when checking for set controls
    :return list[str] set_controls: list of set control node names
    """
    rig_context = get_selection_rig_context(**kwargs)
    nodes = cmds.ls(selection=True)
    rig_controls = get_rig_control_objects_from_list(rig_context, nodes, **kwargs)

    all_controls_raw = get_all_controls(**kwargs)
    all_controls = []
    for control in set(all_controls_raw):
        # Filer objectSets and control nodes into a full list of control node names
        if cmds.nodeType(control) == "objectSet":
            control_list = cmds.sets(control, query=True)
            all_controls += get_rig_control_objects_from_list(rig_context, control_list, **kwargs)
        else:
            rig_control = get_rig_control_object(rig_context, control, **kwargs)
            if rig_control:
                rig_controls.append(rig_control)
    # create a list of controls belonging to the same set as the initial selection
    set_controls = []
    for rig_control in rig_controls:
        for control in all_controls:
            if not control.set == rig_control.set:
                continue
            if not ignore_side:
                if rig_control.side == control.side:
                    set_controls.append(control.full_name)
                continue
            set_controls.append(control.full_name)

    return set_controls


def get_rig_control_objects_from_list(rig_context, nodes, **kwargs):
    """
    get a list of rig controls from passed list
    :param dict rig_context: rig context dictionary
    :param list[str] nodes: list of nodes to get rig controls from
    :return list[Rig_Control]: list of rig control objects
    """
    rig_controls = []
    for node in nodes:
        rig_control = get_rig_control_object(rig_context, node, **kwargs)
        if rig_control:
            rig_controls.append(rig_control)
    return rig_controls


def get_rig_control_object(rig_context, node, **kwargs):
    """
    Get a single rig control object. pass each node through a set of filters
    :param dict rig_context: rig context dictionary
    :param str node: node to get rig control from
    :return RigControl: rig control object if valid, else None
    """
    shape_node = cmds.listRelatives(node, shapes=True, path=True)
    if not shape_node:
        shape_node = node
    else:
        shape_node = shape_node[0]
    if not cmds.nodeType(shape_node) in rig_context["node_types"]:
        return None
    for exclusion_name in rig_context["exclude"]:
        if exclusion_name in node:
            return None
    return RigControl(rig_context, node)


def get_rig_context_path(**kwargs):
    """
    get the rig selection context path where all rig context files are to be stored
    Create the directory if it doesn't exist
    """
    rig_selection_context = os.path.join(USER_DATA_PATH, "rig_selection_context")
    if not os.path.exists(rig_selection_context):
        os.makedirs(rig_selection_context)
    return rig_selection_context


def get_selection_rig_context(rig_context="default", **kwargs):
    """
    get the selection rig context
    :param rig_context: string representing the rig context to be retrieved
    :return dict rig_context: rig context dictionary
    """
    if rig_context == "default":
        # create user data directories
        return DEFAULT_RIG_SELECTION_CONTEXT
