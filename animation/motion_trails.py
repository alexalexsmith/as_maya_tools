"""
Motion trails scripts
"""

from maya import cmds, mel

from as_maya_tools.utilities import timeline_utils


def create():
    """Create a standard motion trail on the selected objects"""
    selected_nodes = cmds.ls(selection=True)
    if not selected_nodes:
        return
    frame_range = get_timeline_range()
    motion_trail = cmds.snapshot(motionTrail=1, increment=1, startTime=frame_range[0], endTime=frame_range[1], n="motionTrail_")
    #mel.eval("snapshot  -motionTrail 1  -increment 1 -startTime `playbackOptions -query -min` -endTime `playbackOptions -query -max`;")

    all_model_panels = cmds.getPanel(type='modelPanel')
    for model_panel in all_model_panels:

        # Make sure motion trail is visible by default after creation
        cmds.modelEditor(model_panel, edit=True, motionTrails=True)

        # Make sure motion trail is included in any viewport isolation by default
        isolate_state = cmds.isolateSelect(model_panel, query=True, state=True)
        if isolate_state:
            cmds.select("motionTrail*", r=True)
            cmds.isolateSelect(model_panel, addSelected=True)
    return


def toggle_visibility():
    """Toggle all motion trails visibility"""
    all_model_panels = cmds.getPanel(type='modelPanel')

    # Using the current model panel to set the toggle for the rest of the model panels
    # This resolves the issue of any model panels toggling opposite on/off values
    current_state = cmds.modelEditor(cmds.getPanel(wf=True), query=True, motionTrails=True)
    for model_panel in all_model_panels:
        cmds.modelEditor(model_panel, edit=True, motionTrails=not current_state)

        # Make sure motion trail is included in any viewport isolation by default
        isolate_state = cmds.isolateSelect(model_panel, query=True, state=True)
        if isolate_state:
            cmds.select("motionTrail*", r=True)
            cmds.isolateSelect(model_panel, addSelected=True)


def select():
    """select all motion trails"""
    cmds.select("motionTrail*", r=True)


def delete():
    """delete all motion trails"""
    cmds.delete("motionTrail*")
    
    
def get_timeline_range():
    """
    Get the time line range for the motion trail creation
    If a range of keys are selected use that range else use timeslider range
    """
    frame_range = timeline_utils.get_selected_key_range()
    print("selected range is {0}".format(frame_range))
    if frame_range[1]-frame_range[0] == 1:
        frame_range = timeline_utils.get_playback_range()
        print("timeline range is {0}".format(frame_range))
    return frame_range