"""
advanced skeleton IKFK switch extracted so I can manage it better
"""

from maya import cmds
import maya.api.OpenMaya as om

        
IKFK_ARM_NODES = ("FKIKArm", "Shoulder", "Elbow", "Wrist", "PoleArm", "Arm")
IKFK_LEG_NODES = ("FKIKLeg", "Hip", "PoleLeg", "Leg", "Knee", "Ankle")
ARM_FK_SNAP_NODES = ("Shoulder", "Elbow", "Wrist")
LEG_FK_SNAP_NODES = ("Hip", "Knee", "Ankle")


def selection_changed_callback_switch_ikfk():
    """
    function to switch between IK and FK interpolation using a SelectionChanged callback in Maya
    """
    selection = cmds.ls(selection=True)
    if len(selection) < 0:
        return
    for node in selection:
        side=None
        if node.endswith("_L"):
            side ="L"
        if node.endswith("_R"):
            side ="R"
        if not side:
            return
        if not ":" in node:
            return
        
        namespace, base_name = node.split(":")# If no namespace this will throw an error!!!!
        fkik_node = None
        if "IKArm" in node:
            print("to IK we go!!!!")
            fkik_node = "{0}:FKIKArm_{1}".format(namespace, side)
            ik_handle = "{0}:IKArm_{1}".format(namespace, side)
            cmds.setAttr("{0}.FKIKBlend".format(fkik_node), 10)
                
        if "IKLeg" in node:
            print("to IK we go!!!!")
            fkik_node = "{0}:FKIKLeg_{1}".format(namespace, side)
            ik_handle = "{0}:IKLeg_{1}".format(namespace, side)
            cmds.setAttr("{0}.FKIKBlend".format(fkik_node), 10)
            
        for control_base_name in ARM_FK_SNAP_NODES:
            if control_base_name in node:
                print("to FK we go!!!!")
                fkik_node = "{0}:FKIKArm_{1}".format(namespace, side)
                ik_handle = "{0}:IKArm_{1}".format(namespace, side)
                cmds.setAttr("{0}.FKIKBlend".format(fkik_node), 0)
                
        for control_base_name in LEG_FK_SNAP_NODES:
            if control_base_name in node:
                print("to FK we go!!!!")
                fkik_node = "{0}:FKIKLeg_{1}".format(namespace, side)
                ik_handle = "{0}:IKLeg_{1}".format(namespace, side)
                cmds.setAttr("{0}.FKIKBlend".format(fkik_node), 0)
                
        if not fkik_node:
            return
            
        ik_fk_switch = cmds.getAttr("{0}.FKIKBlend".format(fkik_node))
        # tool only works if these values are set like this :(
        cmds.setAttr("{0}.stretchy".format(ik_handle),10)
        cmds.setAttr("{0}.Lenght1".format(ik_handle),1)
        cmds.setAttr("{0}.Lenght2".format(ik_handle),1)


def match_ikfk(*args, **kwargs):
    """
    match ik to fk or fk to ik dependant on the FKIK control blend attribute values
    """
    selection = cmds.ls(selection=True)
    if len(selection) < 0:
        return
    for node in selection:
        side=None
        if node.endswith("_L"):
            side ="L"
        if node.endswith("_R"):
            side ="R"
        if not side:
            return
        if not ":" in node:
            return
        
        namespace, base_name = node.split(":")# If no namespace this will throw an error!!!!
        fkik_node = None
        for snap_node in IKFK_ARM_NODES:
            if snap_node in node:
                fkik_node = "{0}:FKIKArm_{1}".format(namespace, side)
                ik_handle = "{0}:IKArm_{1}".format(namespace, side)
                continue
                
        for snap_node in IKFK_LEG_NODES:
            if snap_node in node:
                fkik_node = "{0}:FKIKLeg_{1}".format(namespace, side)
                ik_handle = "{0}:IKLeg_{1}".format(namespace, side)
                continue
        
        if not fkik_node:
            return
            
        ik_fk_switch = cmds.getAttr("{0}.FKIKBlend".format(fkik_node))
        # tool only works if these values are set like this :(
        cmds.setAttr("{0}.stretchy".format(ik_handle),10)
        cmds.setAttr("{0}.Lenght1".format(ik_handle),1)
        cmds.setAttr("{0}.Lenght2".format(ik_handle),1)
        
        if ik_fk_switch == 10:
            match_fk_to_ik(node, side)
        if ik_fk_switch == 0:
            match_ik_to_fk(node, side)


def match_fk_to_ik(node, side):
    """
    match fk to ik controls
    :param str node: name of node belonging to IK/FK system
    """
    # TODO: try to make this more universal
    #arm
    fk_snap_nodes = None
    
    for snap_node in IKFK_ARM_NODES:
        if snap_node in node:
            fk_snap_nodes = ARM_FK_SNAP_NODES
            continue
            
    for snap_node in IKFK_LEG_NODES:
        if snap_node in node:
            fk_snap_nodes = LEG_FK_SNAP_NODES
            continue
            
    if not fk_snap_nodes:
        cmds.warning("select an IK or FK control")
        return
        
    namespace, base_name = node.split(":")
    
    for snap_node in fk_snap_nodes:
        ctrl_name = "{0}:FK{1}_{2}".format(namespace, snap_node, side)
        snap_position_node_name = "{0}:IKX{1}_{2}".format(namespace, snap_node, side)
        snap_to_matrix = cmds.xform(snap_position_node_name, query=True, matrix=True, ws=True)
        cmds.xform(ctrl_name, matrix=list(snap_to_matrix), ws=True)
        cmds.setKeyframe(ctrl_name)


def match_ik_to_fk(node, side):
    """
    match ik to fk controls
    :param str node: name of node belonging to IK/FK system
    """
    ik_matrix_offset_dict = get_ik_matrix_offset_dict(node, side)
    
    if not ik_matrix_offset_dict:
        cmds.warning("Unable to get ik controls for switch")
        return
    
    # match ik control
    offset_mmatrix = om.MMatrix(ik_matrix_offset_dict["ik_matrix"])
    parent_world_matrix = om.MMatrix(cmds.xform(ik_matrix_offset_dict["ik_control_snap_bone"], q=True, matrix=True, ws=True))
    paste_matrix = offset_mmatrix * parent_world_matrix
    cmds.xform(ik_matrix_offset_dict["ik_control"], matrix=list(paste_matrix), ws=True)
    cmds.setKeyframe(ik_matrix_offset_dict["ik_control"])
    
    # match pole vector control
    offset_mmatrix = om.MMatrix(ik_matrix_offset_dict["pole_matrix"])
    parent_world_matrix = om.MMatrix(cmds.xform(ik_matrix_offset_dict["pole_control_snap_bone"], q=True, matrix=True, ws=True))
    paste_matrix = offset_mmatrix * parent_world_matrix
    cmds.xform(ik_matrix_offset_dict["pole_control"], matrix=list(paste_matrix), ws=True)
    cmds.setKeyframe(ik_matrix_offset_dict["pole_control"])
    
   
def get_ik_matrix_offset_dict(node, side):
    """
    :param str node: name of node belonging to IK/FK system
    """
    # Figure out which controls to use
        
    # assuming there is always a namespace
    namespace, base_name = node.split(":")
    
    # Get what type of ik system it is and grab the controls
    ik_chain_bone = None
    ik_pole_bone = None
    ik_control = None
    pole_control = None
    ik_control_snap_bone = None
    pole_control_snap_bone = None
    
    for snap_node in IKFK_ARM_NODES:
        if snap_node in node:
            ik_chain_bone = "{0}:IKXWrist_{1}".format(namespace, side)
            ik_pole_bone = "{0}:IKXElbow_{1}".format(namespace, side)
            ik_control = "{0}:IKArm_{1}".format(namespace, side)
            pole_control = "{0}:PoleArm_{1}".format(namespace, side)
            ik_control_snap_bone = "{0}:FKWrist_{1}".format(namespace, side)
            pole_control_snap_bone = "{0}:FKElbow_{1}".format(namespace, side)
            
    for snap_node in IKFK_LEG_NODES:
        if snap_node in node:
            ik_chain_bone = "{0}:IKXAnkle_{1}".format(namespace, side)
            ik_pole_bone = "{0}:IKXKnee_{1}".format(namespace, side)
            ik_control = "{0}:IKLeg_{1}".format(namespace, side)
            pole_control = "{0}:PoleLeg_{1}".format(namespace, side)
            ik_control_snap_bone = "{0}:FKAnkle_{1}".format(namespace, side)
            pole_control_snap_bone = "{0}:FKKnee_{1}".format(namespace, side)
            
    for node_name in [ik_chain_bone, ik_pole_bone, ik_control, pole_control, ik_control_snap_bone, pole_control_snap_bone]:
        if not node_name:
            return None
        
    # Build dict
    ik_snap_matrix_dict = {}
    ik_snap_matrix_dict["ik_matrix"] = get_matrices_offset_dict(ik_chain_bone, ik_control)
    ik_snap_matrix_dict["pole_matrix"] = get_matrices_offset_dict(ik_pole_bone, pole_control)
    ik_snap_matrix_dict["ik_control"] = ik_control
    ik_snap_matrix_dict["pole_control"] = pole_control
    ik_snap_matrix_dict["ik_control_snap_bone"] = ik_control_snap_bone
    ik_snap_matrix_dict["pole_control_snap_bone"] = pole_control_snap_bone
    
    return ik_snap_matrix_dict


# NOTE: this calculation can cause issues where the shear value is manipulated. This can cause the IK control to explode into the nether
def get_matrices_offset_dict(parent, child):
    """get the matrices offset dict
    :param str parent: parent to relate offset to
    :param list[str] children: children to compare
    :return dict: each key, named child, holding the offset matrix"""


    # Using open maya to do the matrix math to get the offset
    parent_matrix = om.MMatrix(cmds.xform(parent, query=True, matrix=True, ws=True))
    child_matrix = om.MMatrix(cmds.xform(child, query=True, matrix=True, ws=True))
    offset_mmatrix = child_matrix * parent_matrix.inverse()
    return list(offset_mmatrix)


# Mouse click callbacks
"""
DragRelease
SelectionChanged

"""

"""
ActiveViewChanged
ChannelBoxLabelSelected
ColorIndexChanged
CurveRGBColorChanged
DagObjectCreated
DisplayColorChanged
DisplayPreferenceChanged
DisplayRGBColorChanged
DragRelease
EditModeChanged
GhostListChanged
LiveListChanged
MenuModeChanged
ModelPanelSetFocus
NameChanged
NewSceneOpened
PolyUVSetChanged
PolyUVSetDeleted
PostSceneRead
PostSceneSegmentChanged
PostToolChanged
PreFileNew
PreFileNewOrOpened
PreFileOpened
PreSelectionChangedTriggered
RebuildUIValues
RecentCommandChanged
Redo
RenderSetupSelectionChanged
RenderViewCameraChanged
SceneImported
SceneOpened
SceneSaved
SceneSegmentChanged
SelectModeChanged
SelectPreferenceChanged
SelectPriorityChanged
SelectTypeChanged
SelectionChanged
SequencerActiveShotChanged
SetModified
SoundNodeAdded
SoundNodeRemoved
ToolChanged
ToolDirtyChanged
ToolSettingsChanged
UFESelectionChanged
Undo
UvTileProxyDirtyChangeTrigger
activeHandleChanged
activeTexHandleChanged
angularToleranceChanged
angularUnitChanged
animLayerAnimationChanged
animLayerBaseLockChanged
animLayerGhostChanged
animLayerLockChanged
animLayerRebuild
animLayerRefresh
axisAtOriginChanged
cacheDestroyed
cachingEvaluationModeChanged
cachingPreferencesChanged
cachingSafeModeChanged
cameraChange
cameraDisplayAttributesChange
colorMgtConfigChanged
colorMgtConfigFileEnableChanged
colorMgtConfigFilePathChanged
colorMgtEnabledChanged
colorMgtOCIORulesEnabledChanged
colorMgtOutputChanged
colorMgtPlayblastOutputChanged
colorMgtPrefsReloaded
colorMgtPrefsViewTransformChanged
colorMgtRefreshed
colorMgtUserPrefsChanged
colorMgtWorkingSpaceChanged
constructionHistoryChanged
cteEventClipEditModeChanged
cteEventKeyingTargetForClipChanged
cteEventKeyingTargetForInvalidChanged
cteEventKeyingTargetForLayerChanged
currentContainerChange
currentSoundNodeChanged
customEvaluatorChanged
dbTraceChanged
deleteAll
displayLayerAdded
displayLayerChange
displayLayerDeleted
displayLayerManagerChange
displayLayerVisibilityChanged
freezeOptionsChanged
glFrameTrigger
graphEditorChanged
graphEditorOutlinerHighlightChanged
graphEditorOutlinerListChanged
graphEditorParamCurveSelected
gridDisplayChanged
idle
idleHigh
idleVeryLow
interactionStyleChanged
lightLinkingChanged
lightLinkingChangedNonSG
linearToleranceChanged
linearUnitChanged
metadataVisualStatusChanged
modelEditorChanged
nurbsCurveRebuildPrefsChanged
nurbsToPolygonsPrefsChanged
nurbsToSubdivPrefsChanged
passContributionMapChange
playbackByChanged
playbackModeChanged
playbackRangeAboutToChange
playbackRangeChanged
playbackRangeSliderChanged
playbackSpeedChanged
polyCutUVEventTexEditorCheckerDisplayChanged
polyCutUVShowTextureBordersChanged
polyCutUVShowUVShellColoringChanged
polyCutUVSteadyStrokeChanged
polyTopoSymmetryValidChanged
poseEditorTreeviewSelectionChanged
preferredRendererChanged
profilerSelectionChanged
quitApplication
rangeSliderUIChanged
redoXformCmd
renderLayerChange
renderLayerManagerChange
renderPassChange
renderPassSetChange
renderPassSetMembershipChange
renderSetupAutoSave
resourceLimitStateChange
sculptMeshCacheBlendShapeListChanged
sculptMeshCacheCloneSourceChanged
selectionConstraintsChanged
selectionPipelineChanged
serialExecutorFallback
shapeEditorTreeviewSelectionChanged
snapModeChanged
softSelectOptionsChanged
start3dPaintTool
startColorPerVertexTool
stop3dPaintTool
stopColorPerVertexTool
symmetricModellingOptionsChanged
tabletModeChanged
teClipAdded
teClipModified
teClipRemoved
teCompositionActiveChanged
teCompositionAdded
teCompositionNameChanged
teCompositionRemoved
teEditorPrefsChanged
teMuteChanged
teTrackAdded
teTrackModified
teTrackNameChanged
teTrackRemoved
texMoveContextOptionsChanged
texRotateContextOptionsChanged
texScaleContextOptionsChanged
texWindowEditorCheckerDensityChanged
texWindowEditorCheckerDisplayChanged
texWindowEditorClose
texWindowEditorDisplaySolidMapChanged
texWindowEditorImageBaseColorChanged
texWindowEditorShowup
threadCountChanged
timeChanged
timeUnitChanged
transformLockChange
undoSupressed
undoXformCmd
workspaceChanged
xformConstraintOptionsChanged
"""