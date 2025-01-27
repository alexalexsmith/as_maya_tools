# as_maya_tools
## Summary:
variety of scripts and tools to speedup animation workflow in maya

# Tool List

## Attributes
### reset transforms
Set transforms on selected objects to default value
```
from as_maya_tools.animation import attributes;attributes.reset_transforms()
```

### reset translation
Set translation on selected objects to default value
```
from as_maya_tools.animation import attributes;attributes.reset_translation()
```

### reset rotation
Set rotation on selected objects to default value
```
from as_maya_tools.animation import attributes;attributes.reset_rotation()
```

### reset scale
Set scale on selected objects to default value
```
from as_maya_tools.animation import attributes;attributes.reset_scale()
```

### reset selected attributes
Set atributes selected in the channelbox to default value
```
from as_maya_tools.animation import attributes;attributes.reset_selected_attributes()
```

## Motion trails
### create motion trail
Create a motion trail for selected objects. Motion trail will be made visible even if isolate is on in viewport
```
from as_maya_tools.animation import motion_trails;motion_trails.create()
```

### toggle motion trail visibility
Toggle visibility of motion trails
```
from as_maya_tools.animation import motion_trails;motion_trails.toggle_visibility()
```

### select motion trails
Select all motion trails in the scene
```
from as_maya_tools.animation import motion_trails;motion_trails.select()
```

### delete motion trails
Delete all motion trails in the scene
```
from as_maya_tools.animation import motion_trails;motion_trails.delete()
```

## Misc Scripts
### create locator at selected
Create locator(s) on selected object(s)
```
from as_maya_tools.animation import quick_scripts;quick_scripts.create_locator_at_selected()
```

### locked selected in place
Lock selected object(s) in place
```
from as_maya_tools.animation import quick_scripts;quick_scripts.lock_selected_in_place()
```

## Snapping
### snap a to b
Snap first selection to second selection
```
from as_maya_tools.animation import snapping;snapping.snap_a_to_b()
```

## TimeLine
### set playback slider to selected keys
Set the adjustable playback slider min-max value to the highlighted frame range
```
from as_maya_tools.animation import timeline;timeline.set_playbackslider_to_selected_keys()
```

## Rig Selection
### select all
Select all controls on a rig. Requires rig context definition .json file 
```
from as_maya_tools.animation import rig_selection;rig_selection.select_all()
```

### select mirror
Select controls on the opposing side of a rig. Requires rig context definition .json file 
```
from as_maya_tools.animation import rig_selection;rig_selection.select_mirror()
```
:param bool add: option to keep original selection when selecting mirrored controls. default is false

### select set
Select set of controls the current selection belongs to. Requires rig context definition .json file 
```
from as_maya_tools.animation import rig_selection;rig_selection.select_set()
```
