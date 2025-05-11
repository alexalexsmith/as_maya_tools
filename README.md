# as_maya_tools
## Summary:
variety of scripts and tools to speedup animation workflow in maya
## How To Use:
Place as_maya_tools in your maya scripts folder. run any of the below python commands to use the script or tool.
If you want to use a tool in a marking menu or run it through mel for any reason, wrap the command with the mel command python("")
example:
```
python("from as_maya_tools.animation import attributes;attributes.reset_transforms()")
```
See mel documentation for more information on the python() command
https://help.autodesk.com/cloudhelp/2024/ENU/Maya-Tech-Docs/Commands/python.html

## Contact:
If you need help with anything you can send an email to alex.animationtd@gmail.com

# Tool List

## Attributes
### attribute switcher ui
Ui for switching attributes while maintaining the objects transform position. Also knows as a spaceswitch tool
```
from as_maya_tools.interface import attribute_switcher_ui;attribute_switcher_ui_instance = attribute_switcher_ui.AttributeSwitcherUI.load_ui()
```

### noise settings ui
Ui for generating noise on attributes selected in the main channel box across keyframes selected in the timeline
```
from as_maya_tools.interface import noise_settings_ui;noise_settings_ui_instance = noise_settings_ui.NoiseGenerationSettingsUI.load_ui()
```

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
Set attributes selected in the channelbox to default value
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

### lock selected in place
Lock selected object(s) in place
```
from as_maya_tools.animation import quick_scripts;quick_scripts.lock_selected_in_place()
```

### attach_locator_to_selection
attach a locator to the selected transform or vertex
```
from as_maya_tools.animation import quick_scripts;quick_scripts.attach_locator_to_selection()
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
### rig selection settings ui
UI for managing selection settings
```
from as_maya_tools.interface import rig_selection_settings_ui;rig_selection_settings_ui_instance = rig_selection_settings_ui.RigSelectionSettingsUI.load_ui()
```

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

### create temp selection set
Create an overwritable selection set
```
from as_maya_tools.animation import rig_selection;rig_selection.create_temp_selection_set()
```

### select temp selection set
Select the items in a selection set created using the create temp selection set command. Selection is namespace agnostic. 
The tool will use any and all namespaces in the current selection. If nothing is selected, the stored namespace will be used.
nodes in the selection set without a namespace will be added either way
```
from as_maya_tools.animation import rig_selection;rig_selection.select_temp_selection_set()
```
