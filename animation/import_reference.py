"""
Import an image sequence for use as reference
TODO
possible features
-attach to selected camera(if camera is selected)
-polygon plane option maybe
-convert movie file to image sequence if possible. use ffmpeg?
"""

import re, os
from PySide2 import QtWidgets

from maya import cmds

from as_maya_tools.utilities import timeline_utils

FILE_EXTENSIONS = [".png", ".jpg", ".tiff"] # add more file formats here
IMAGESEQUENCE_REGREX = "^(.*)(?<!\d)(\d+)\.(\w+)$"


def import_image(**kwargs):
    """Import image sequence as imageplane node"""
    image_path = get_image_file_path(**kwargs)

    if not image_path:
        return
    image_suquence_range = get_image_sequence_first_and_last_frame(image_path)
    
    image_name = get_image_name(image_path)

    image_plane = cmds.imagePlane(
        name=image_name,
        maintainRatio=1,
        lookThrough="persp",
        fileName=image_path
    )
    cmds.setAttr("{0}.useFrameExtension".format(image_plane[1]), 1)
    connections = cmds.listConnections("{0}.frameExtension".format(image_plane[1]), skipConversionNodes=True, plugs=True)
    for connection in connections:
        cmds.disconnectAttr(connection, "{0}.frameExtension".format(image_plane[1]))
        
    playback_slider_start_frame = timeline_utils.get_playback_range()[0]
    refernece_start_frame_offset = playback_slider_start_frame
    reference_end_frame_offset = (image_suquence_range[1] - image_suquence_range[0]) + playback_slider_start_frame
    cmds.setKeyframe(
        image_plane[1],
        attribute="frameExtension",
        value=image_suquence_range[0],
        time=[refernece_start_frame_offset, refernece_start_frame_offset],
        inTangentType="linear",
        outTangentType="linear"
        )
    cmds.setKeyframe(
        image_plane[1],
        attribute="frameExtension",
        value=image_suquence_range[1],
        time=[reference_end_frame_offset, reference_end_frame_offset],
        inTangentType="linear",
        outTangentType="linear"
        )
    
    
def get_image_name(image_path):
    """get the image name from a path. name will be fixed to be compatible with maya nodes
    :param str image_path: path to image
    :return str: image name
    """
    image_name_and_extension = image_path.split("/")[-1]
    for file_extension in FILE_EXTENSIONS:
        if image_name_and_extension.endswith(file_extension):
            image_name = image_name_and_extension.split(file_extension)[0]
            return get_maya_node_name(image_name)


def get_image_file_path(parent=None, **kwargs):
    """Get a saved .mcon file using a Qt file dialog
    :param QtWidget parent: parent of file dialog
    :return str: file_path
    """
    file_extensions = " ".join(["*{}".format(extension) for extension in FILE_EXTENSIONS])
    file_filter = "Image ({0})".format(file_extensions)
    response = QtWidgets.QFileDialog().getOpenFileName(
        parent=parent,
        caption="Import Image",
        filter=file_filter,
        initialFilter=file_filter
    )
    file_path = response[0]
    return file_path
    
# TODO: This function will get used a lot. maya node handling utilities?
def get_maya_node_name(string):
    """get string only containing legal characters for a maya node. Replace illegal characters with "_"
    :param str string: string to be checked and fixed
    :return str: fixed_name
    """
    regex = r"[^a-zA-Z0-9]"
    subst = "_"
    fixed_name = re.sub(regex, subst, string, 0, re.MULTILINE)
    return fixed_name
    
    
def get_image_sequence_first_and_last_frame(image_path):
    """
    Get the image sequence first and last frame
    """
    # If not image sequence return None
    image_sequence_file_directory = os.path.dirname(image_path)
    file_name = os.path.basename(image_path)
    files_in_directory = os.listdir(image_sequence_file_directory)
    sequence_values = []
    for file in files_in_directory:
        if not re.match(IMAGESEQUENCE_REGREX, file):
            continue
        int_value = int(re.match(IMAGESEQUENCE_REGREX, file).groups()[1])
        sequence_values.append(int_value)
    sequence_values.sort()
    return (sequence_values[0],sequence_values[-1])