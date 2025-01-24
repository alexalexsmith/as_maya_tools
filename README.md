# as_maya_tools
## Summary:
variety of scripts and tools to speedup animation workflow in maya

## Tool List
### reset transforms
```
from as_maya_tools.animation import attributes;attributes.reset_transforms()
```
Set transforms on selected objects to default value

### reset translation
```
from as_maya_tools.animation import attributes;attributes.reset_translation()
```
Set translation on selected objects to default value

### reset rotation
```
from as_maya_tools.animation import attributes;attributes.reset_rotation()
```
Set rotation on selected objects to default value

### reset scale
```
from as_maya_tools.animation import attributes;attributes.reset_scale()
```
Set scale on selected objects to default value

### reset selected attributes
```
from as_maya_tools.animation import attributes;attributes.reset_selected_attributes()
```
Set atributes selected in the channelbox to default value

### create motion trail
```
from as_maya_tools.animation import motion_trails;motion_trails.create()
```
Create a motion trail for selected objects. Motion trail will be made visible even if isolate is on in viewport

### toggle motion trail visibility
```
from as_maya_tools.animation import motion_trails;motion_trails.toggle_visibility()
```
Toggle visibility of motion trails

### select motion trails
```
from as_maya_tools.animation import motion_trails;motion_trails.select()
```
Select all motion trails in the scene

### delete motion trails
```
from as_maya_tools.animation import motion_trails;motion_trails.delete()
```
Delete all motion trails in the scene

### create locator at selected
```
from as_maya_tools.animation import quick_scripts;quick_scripts.create_locator_at_selected()
```
Create locator(s) on selected object(s)

### locked selected in place
```
from as_maya_tools.animation import quick_scripts;quick_scripts.lock_selected_in_place()
```
Lock selected object(s) in place

### snap a to b
```
from as_maya_tools.animation import snapping;snapping.snap_a_to_b()
```
Snap first selection to second selection

### set playback slider to selected keys
```
from as_maya_tools.animation import timeline;timeline.set_playbackslider_to_selected_keys()
```
Set the adjustable playback slider min-max value to the highlighted frame range


