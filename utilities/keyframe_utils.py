"""
Utilities for dealing with keyframes in maya
"""
from maya import cmds, mel

from as_maya_tools.utilities import timeline_utils, json_utils, performance_utils, maya_node_utils, decorators
from as_maya_tools import KEYFRAME_DATA_PATH


COPY_KEYFRAME_DATA = "COPY_KEYFRAME_DATA"


def get_keyframe_list(frame_range="selected_key_range", frequency=1, **kwargs):
    """
    Get a list of keyframes with a specified frequency
    :param str frame_range: animation_range, playback_range, selected_key_range string options
    :param int frequency: separation between keyframes
    :return list(list(int)): list of keyframes TODO: make it return a list(int)
    """
    keyframe_range_options = ["animation_range", "playback_range", "selected_key_range"]
    if frame_range not in keyframe_range_options:
        cmds.warning(
            "keyframe range not specified properly. keyframe_range argument accepts animation_range, playback_range, selected_key_range")
        return None

    if frame_range == "animation_range":
        keyframe_range = timeline_utils.get_animation_range()
    if frame_range == "playback_range":
        keyframe_range = timeline_utils.get_playback_range()
    if frame_range == "selected_key_range":
        keyframe_range = timeline_utils.get_selected_key_range()

    frames = []
    for keyframe in range(int(keyframe_range[0]), int(keyframe_range[1] + frequency)):
        frames.append(keyframe)

    frame_chunks = list(chunk_list(frames, chunk_size=frequency))
    return frame_chunks


def chunk_list(list_item, chunk_size=1):
    """
    chunk a list into equal sizes
    :param list list_item: list to chunk
    :param int chunk_size: max size of chunk
    """

    for i in list(range(0, len(list_item), chunk_size)):
        yield list_item[i:i + chunk_size]


@decorators.end_progress_bar_function
def copy_keyframes(all_keyframes=False, **kwargs):
    """
    copy animation from selected objects
    :param bool all_keyframes: option to save all keyframes
    """
    nodes = cmds.ls(selection=True)
    if nodes is None or len(nodes) == 0:
        performance_utils.message("no nodes specified to copy keyframes", position='midCenterTop', record_warning=True)
        return

    main_data = {}
    animation_data = {}
    nodes_meta = []
    key_frame_range_meta = []

    # store selected attribute if user wants to save out specific attributes
    selected_attributes = cmds.channelBox('mainChannelBox', query=True, selectedMainAttributes=True)

    # get frame range for keyframes
    frame_range = None
    if not all_keyframes:
        frame_range = [cmds.currentTime(query=True), cmds.currentTime(query=True)]
        gPlayBackSlider = mel.eval('$tmp = $gPlayBackSlider')
        if cmds.timeControl(gPlayBackSlider, query=True, rangeVisible=True):
            frame_range = cmds.timeControl(gPlayBackSlider, query=True, rangeArray=True)
            
    main_progress_bar = performance_utils.progress_bar("copying animation", len(nodes))
    
    for node in nodes:
        cmds.progressBar(main_progress_bar, edit=True,step=1, status=(f"copying animation from {node}"))
        animatable_attributes = cmds.listAttr(node, keyable=True, unlocked=True, shortNames=True)

        # skipping node if no animatable attributes are available
        if not animatable_attributes or len(animatable_attributes) == 0:
            continue

        attribute_data = {}
        for attribute in animatable_attributes:

            # skipping non selected attributes if there are attributes selected
            if selected_attributes and not attribute in selected_attributes:
                continue

            # determine frame range to query keyframe data from
            key_frames = cmds.keyframe(
                f"{node}.{attribute}",
                query=True,
                timeChange=True)
            if frame_range:
                key_frames = cmds.keyframe(
                    f"{node}.{attribute}",
                    query=True,
                    timeChange=True,
                    time=(frame_range[0], frame_range[1]))

            # If no keyframes are found store the current value as backup
            current_value = cmds.getAttr(f"{node}.{attribute}")

            key_frame_data = {}
            # only try to store keyframe data if there is any
            if key_frames:
                for key_frame in key_frames:

                    # storing the keyframe range 'meta data'
                    key_frame_range_meta.append(key_frame)

                    # getting keyframe data
                    key_frame_data[key_frame] = get_keyframe_data(node, attribute, key_frame)
            value_data = {}
            value_data["current_value"] = current_value
            value_data["key_frame_data"] = key_frame_data
            attribute_data[attribute] = value_data
        animation_data[node] = attribute_data

        # store included nodes meta data
        nodes_meta.append(node)

    # avoid writing out empty data if no keyframe data was extracted
    if len(nodes_meta) == 0:
        performance_utils.message("no keyframe data was found", position='midCenterTop', record_warning=True)
        return

    main_data["nodes"] = nodes_meta
    main_data["keyframe_range"] = sorted(list(set(key_frame_range_meta)))
    main_data["animation_data"] = animation_data
    # save data in json file
    json_utils.write_json_file(KEYFRAME_DATA_PATH, COPY_KEYFRAME_DATA, main_data)
    cmds.progressBar(main_progress_bar, edit=True, endProgress=True)


@decorators.end_progress_bar_function
@decorators.undoable_chunk
def paste_keyframes(use_selection=True, use_current_time=True, reverse=False, replace=False, **kwargs):
    """
    paste animation
    :param bool use_selection: option to use the current selection to paste keyframes
    :param bool use_current_time: option to paste animation using current time as offset
    :param bool reverse: option to reverse keyframes
    :param bool replace: option to replace animation in the keyframe range
    """
    # read saved animation json file
    anim_data = json_utils.read_offset_json_file(KEYFRAME_DATA_PATH, COPY_KEYFRAME_DATA)
    
    nodes = anim_data["nodes"]
    
    if use_selection:
        nodes = cmds.ls(selection=True)
    if nodes is None or len(nodes) == 0:
        performance_utils.message("no nodes specified to paste keyframes", position='midCenterTop', record_warning=True)
        return

    if not anim_data:
        performance_utils.message("no copied keyframe data found", position='midCenterTop', record_warning=True)
        return

    # determine the animation offset from original
    animation_offset = 0
    if use_current_time:
        animation_offset = anim_data["keyframe_range"][0] - cmds.currentTime(query=True)
        
    main_progress_bar = performance_utils.progress_bar("pasting animation", len(nodes))

    for i, node in enumerate(nodes):
        # skip any object that doesn't exist in the current maya session
        if not performance_utils.obj_exists(node):
            continue
        
        cmds.progressBar(main_progress_bar, edit=True, step=1, status=(f"pasting animtion to {node}"))
        
        node_key = list(anim_data["animation_data"])[
            i % len(anim_data["animation_data"])]  # animation data will loop until selected node list ends
        for attribute_key in anim_data["animation_data"][node_key]:

            # make sure attribute exists on this node before going any further
            # TODO: may need to check if attribute is not connected to other nodes
            animatable_attributes = cmds.listAttr(node, keyable=True, unlocked=True, shortNames=True)
            if attribute_key not in animatable_attributes:
                continue

            # setting the order keyframes are applied
            key_frames_data = anim_data["animation_data"][node_key][attribute_key]["key_frame_data"]

            # use the current time stored value if no keyframes are stored
            if len(key_frames_data) == 0:
                cmds.setAttr(
                    f"{node}.{attribute_key}",
                    anim_data["animation_data"][node_key][attribute_key]["current_value"])
                continue

            # Reverse keyframes
            # TODO: this needs to reverse the curve not the keyframe list
            key_frames = []
            for key_frame_key in key_frames_data:
                key_frames.append(key_frame_key)
            if reverse:
                reverse_keyframes = []
                for key_frame in reversed(key_frames):
                    reverse_keyframes.append(key_frame)
                key_frames = reverse_keyframes


            # set keyframes on nodes
            for key_frame, key_frame_key in zip(key_frames_data, key_frames):

                # getting the keyframe time including any offsets
                key_frame_time = float(key_frame) - animation_offset

                set_keyframe(
                    node,
                    attribute_key,
                    key_frame_time,
                    anim_data["animation_data"][node_key][attribute_key]["key_frame_data"][key_frame_key]["value"],
                    anim_data["animation_data"][node_key][attribute_key]["key_frame_data"][key_frame_key]["in_tangent"],
                    anim_data["animation_data"][node_key][attribute_key]["key_frame_data"][key_frame_key]["out_tangent"],
                    anim_data["animation_data"][node_key][attribute_key]["key_frame_data"][key_frame_key]["in_angle"],
                    anim_data["animation_data"][node_key][attribute_key]["key_frame_data"][key_frame_key]["in_weight"],
                    anim_data["animation_data"][node_key][attribute_key]["key_frame_data"][key_frame_key]["ix"],
                    anim_data["animation_data"][node_key][attribute_key]["key_frame_data"][key_frame_key]["iy"],
                    anim_data["animation_data"][node_key][attribute_key]["key_frame_data"][key_frame_key]["lock"],
                    anim_data["animation_data"][node_key][attribute_key]["key_frame_data"][key_frame_key]["out_angle"],
                    anim_data["animation_data"][node_key][attribute_key]["key_frame_data"][key_frame_key]["out_weight"],
                    anim_data["animation_data"][node_key][attribute_key]["key_frame_data"][key_frame_key]["ox"],
                    anim_data["animation_data"][node_key][attribute_key]["key_frame_data"][key_frame_key]["oy"],
                    anim_data["animation_data"][node_key][attribute_key]["key_frame_data"][key_frame_key]["weight_lock"],
                    anim_data["animation_data"][node_key][attribute_key]["key_frame_data"][key_frame_key]["weighted_tangents"],
                )
    cmds.progressBar(main_progress_bar, edit=True, endProgress=True)



def get_keyframe_data(node, attribute, key_frame):
    """
    Get single keyframe's data
    :return dict: keyframe data
    """
    value = cmds.getAttr(
        f"{node}.{attribute}",
        time=key_frame)
    in_tangent = cmds.keyTangent(
        f"{node}.{attribute}",
        query=True,
        inTangentType=True,
        time=(key_frame, key_frame))[0]
    out_tangent = cmds.keyTangent(
        f"{node}.{attribute}",
        query=True,
        outTangentType=True,
        time=(key_frame, key_frame))[0]
    in_angle = cmds.keyTangent(
        f"{node}.{attribute}",
        query=True,
        inAngle=True,
        time=(key_frame, key_frame))[0]
    in_weight = cmds.keyTangent(
        f"{node}.{attribute}",
        query=True,
        inWeight=True,
        time=(key_frame, key_frame))[0]
    ix = cmds.keyTangent(
        f"{node}.{attribute}",
        query=True,
        ix=True,
        time=(key_frame, key_frame))[0]
    iy = cmds.keyTangent(
        f"{node}.{attribute}",
        query=True,
        iy=True,
        time=(key_frame, key_frame))[0]
    lock = cmds.keyTangent(
        f"{node}.{attribute}",
        query=True,
        lock=True,
        time=(key_frame, key_frame))[0]
    out_angle = cmds.keyTangent(
        f"{node}.{attribute}",
        query=True,
        outAngle=True,
        time=(key_frame, key_frame))[0]
    out_weight = cmds.keyTangent(
        f"{node}.{attribute}",
        query=True,
        outWeight=True,
        time=(key_frame, key_frame))[0]
    ox = cmds.keyTangent(
        f"{node}.{attribute}",
        query=True,
        ox=True,
        time=(key_frame, key_frame))[0]
    oy = cmds.keyTangent(
        f"{node}.{attribute}",
        query=True,
        oy=True,
        time=(key_frame, key_frame))[0]
    weight_lock = cmds.keyTangent(
        f"{node}.{attribute}",
        query=True,
        weightLock=True,
        time=(key_frame, key_frame))[0]
    weighted_tangents = cmds.keyTangent(
        f"{node}.{attribute}",
        query=True,
        weightedTangents=True,
        time=(key_frame, key_frame))[0]

    key_frame_data = {
                    "value": value,
                    "weight_lock": weight_lock,
                    "weighted_tangents": weighted_tangents,
                    "lock": lock,
                    "in_tangent": in_tangent,
                    "in_angle": in_angle,
                    "in_weight": in_weight,
                    "ix": ix,
                    "iy": iy,
                    "out_tangent": out_tangent,
                    "out_angle": out_angle,
                    "out_weight": out_weight,
                    "ox": ox,
                    "oy": oy,
                }
    return key_frame_data


def set_keyframe(
        node,
        attribute,
        key_frame,
        value,
        in_tangent,
        out_tangent,
        in_angle,
        in_weight,
        ix,
        iy,
        lock,
        out_angle,
        out_weight,
        ox,
        oy,
        weight_lock,
        weighted_tangents):
    """
    set the keyframe data
    :param str node: owner of keyframe
    :param str attribute: attribute to set keyframes on
    :param float key_frame: keyframe
    :param float/bool/int value: value to set
    :param str in_tangent: in tangent type
    :param str out_tangent: out tangent type
    :param float in_weight: in weight value
    :param float ix: in tangent x value
    :param float iy: in tangent y value
    :param bool lock: tangent locked value
    :return:
    """
    cmds.setKeyframe(
        f"{node}.{attribute}",
        time=key_frame,
        value=value,)

    cmds.keyTangent(
        f"{node}.{attribute}",
        edit=True,
        absolute=True,
        inTangentType=in_tangent,
        outTangentType=out_tangent,
        time=(key_frame, key_frame))

    cmds.keyTangent(
        f"{node}.{attribute}",
        edit=True,
        weightedTangents=weighted_tangents,
        time=(key_frame, key_frame))

    if weighted_tangents:
        cmds.keyTangent(
            f"{node}.{attribute}",
            edit=True,
            absolute=True,
            weightLock=weight_lock,
            time=(key_frame, key_frame))

    cmds.keyTangent(
        f"{node}.{attribute}",
        edit=True,
        lock=lock,
        time=(key_frame, key_frame))

    if not weighted_tangents:
        cmds.keyTangent(
            f"{node}.{attribute}",
            edit=True,
            absolute=True,
            inWeight=in_weight,
            time=(key_frame, key_frame))
        cmds.keyTangent(
            f"{node}.{attribute}",
            edit=True,
            absolute=True,
            outWeight=out_weight,
            time=(key_frame, key_frame))

    cmds.keyTangent(
        f"{node}.{attribute}",
        edit=True,
        absolute=True,
        ix=ix,
        time=(key_frame, key_frame))
    cmds.keyTangent(
        f"{node}.{attribute}",
        edit=True,
        absolute=True,
        iy=iy,
        time=(key_frame, key_frame))
    cmds.keyTangent(
        f"{node}.{attribute}",
        edit=True,
        absolute=True,
        inAngle=in_angle,
        time=(key_frame, key_frame))
    cmds.keyTangent(
        f"{node}.{attribute}",
        edit=True,
        absolute=True,
        outAngle=out_angle,
        time=(key_frame, key_frame))
    cmds.keyTangent(
        f"{node}.{attribute}",
        edit=True,
        absolute=True,
        ox=ox,
        time=(key_frame, key_frame))
    cmds.keyTangent(
        f"{node}.{attribute}",
        edit=True,
        absolute=True,
        oy=oy,
        time=(key_frame, key_frame))