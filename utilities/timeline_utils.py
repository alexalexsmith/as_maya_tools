from maya import cmds, mel


def get_animation_range():
    """
    Returns the current playback range.
    """
    return [cmds.playbackOptions(q=True, animationStartTime=True), cmds.playbackOptions(q=True, animationEndTime=True)]


def get_playback_range():
    """
    Returns the playback range
    """
    return [cmds.playbackOptions(q=True, minTime=True), cmds.playbackOptions(q=True, maxTime=True)]


def get_selected_key_range():
    """
    Returns the range of selected keys in the timeline
    """
    time_slider = mel.eval("$constraint_manager_time_slider = $gPlayBackSlider")
    return cmds.timeControl(time_slider, query=True, rangeArray=True)


def set_playback_range(start, end):
    """
    Sets the playback range.
    """
    cmds.playbackOptions(edit=True, minTime=start), cmds.playbackOptions(edit=True, maxTime=end)

