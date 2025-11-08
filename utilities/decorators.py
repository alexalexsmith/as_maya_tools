"""
Decorators
"""
from functools import wraps

from maya import cmds

from as_maya_tools.utilities import performance_utils


def set_pref_anim_blend_with_existing_connections(func):
    """
    Decorator to change the 'animBlendingOpt' preference to 'blend with existing connections' when executing func.
    The initial user preferences are restored after the execution of func.
    """

    @wraps(func)
    def _wrapper_set_anim_blend_with_existing_connections(*args, **kwargs):
        # Store initial blending options
        user_blending_options = cmds.optionVar(query='animBlendingOpt')
        # Set blending options to blend with existing connections
        cmds.optionVar(intValue=('animBlendingOpt', 1))

        try:
            # Execute the function
            return func(*args, **kwargs)
        except Exception:
            raise  # will raise original error
        finally:
            # restore original blending options
            cmds.optionVar(intValue=('animBlendingOpt', user_blending_options))

    return _wrapper_set_anim_blend_with_existing_connections


def suspend_refresh(func):
    """
    Decorator to suspend the refresh when executing func.
    Similar to the disableViewport decorator.
    More info at: https://www.toadstorm.com/blog/?p=424
    """

    @wraps(func)
    def _wrapper_suspend_refresh(*args, **kwargs):
        # Suspend refresh
        cmds.refresh(suspend=True)
        try:
            # Execute the function
            return func(*args, **kwargs)
        except Exception:
            raise  # will raise original error
        finally:
            # reactivate refresh
            cmds.refresh(suspend=False)

    return _wrapper_suspend_refresh


def undoable_chunk(func):
    """
    Puts the wrapped `func` into a single Maya Undo action
    """

    @wraps(func)
    def _wrapper_undoable_chunk(*args, **kwargs):
        # start an undo chunk
        cmds.undoInfo(openChunk=True)
        try:
            return func(*args, **kwargs)
        except Exception:
            raise  # will raise original error
        finally:
            # after calling the func, end the undo chunk
            cmds.undoInfo(closeChunk=True)

    return _wrapper_undoable_chunk
    
    
def maintain_selection(func):
    """
    Maintain the Original selection
    """
    @wraps(func)
    def _wrapper_mantain_selection(*args, **kwargs):
        selection = cmds.ls(selection=True)
        try:
            return func(*args, **kwargs)
        except Exception:
            raise  # will raise original error
        finally:
            if len(selection) == 0:
                return
            for item in selection:
                if not performance_utils.obj_exists(item):
                    return
            cmds.select(selection, replace=True)
                
    return _wrapper_mantain_selection
    
    
def base_animation_layer_unlock(func):
    """
    Makes sure the base animation layer is unlocked when code needs to set keyframes. If locked, layer is relocked after completion
    """
    @wraps(func)
    def _wrapper_base_animation_layer_unlock(*args, **kwargs):
        #function
        base_anim_layer_lock_value = False
        try:
            if cmds.animLayer("BaseAnimation", query=True, exists=True):
                if cmds.animLayer("BaseAnimation", query=True, lock=True):
                    base_anim_layer_lock_value = True
                    cmds.animLayer("BaseAnimation", edit=True, lock=False)
        except Exception:
            raise  # will raise original error
        finally:
            if cmds.animLayer("BaseAnimation", query=True, exists=True):
                cmds.animLayer("BaseAnimation", edit=True, lock=base_anim_layer_lock_value)
        
    return _wrapper_base_animation_layer_unlock
    