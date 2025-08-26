"""
Motion trails scripts
"""

from maya import cmds, mel

from as_maya_tools.utilities import timeline_utils


def toggle_visibility():
    """Toggle all greasePencil/bluePencil visibility"""
    all_model_panels = cmds.getPanel(type='modelPanel')

    # Using the current model panel to set the toggle for the rest of the model panels
    # This resolves the issue of any model panels toggling opposite on/off values
    # TODO:check they type of modelPanel to avoid errors 
    current_state = cmds.modelEditor(cmds.getPanel(wf=True), query=True, bluePencil=True)
    for model_panel in all_model_panels:
        cmds.modelEditor(model_panel, edit=True, bluePencil=not current_state)

        # Make sure greasePencil is included in any viewport isolation by default
        isolate_state = cmds.isolateSelect(model_panel, query=True, state=True)
        if isolate_state:
            cmds.select("greasePencil*", r=True)
            cmds.select("bluePencil*", add=True)
            cmds.isolateSelect(model_panel, addSelected=True)
            
            
def import_grease_pencil(offset_to_first_frame=True):
    """
    Import the grease pencil and place the frames at the current timeslider min frame
    :param bool offset_to_first_frame: option to offset the bluepencil frames to the first animation frame usefull when importing from syncsketch
    """
    cmds.bluePencilFrame(importFrames=True)
    if offset_to_first_frame:
        drawing_frame_range = [0, timeline_utils.get_playback_range()[1] - timeline_utils.get_playback_range()[0]]
        first_frame = float(timeline_utils.get_playback_range()[0])-1
        cmds.bluePencilFrame(move=(first_frame, drawing_frame_range[0], drawing_frame_range[1]))
    return