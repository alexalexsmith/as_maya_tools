"""
Random generation utilities
"""
import random

from maya import cmds

from as_maya_tools.utilities import performance_utils, attribute_utils


# get selected keys and attributes
def generate_noise_on_attributes(nodes, attributes, keyframes, amplitude=1, frequency=1, seed=None, use_current_value=True, **kwargs):
    """
    Generate noise animation on selected objects
    :param list(str) nodes: list of node paths
    :param list(str) attributes: list of attributes
    :param float amplitude: amplitude range of noise
    :param int frequency: frequency of noise
    :param bool use_current_value: option to apply nose over the current value 
    """
    for node in nodes:
        if not cmds.nodeType(node) == "transform":
            continue
            
        transform_object = attribute_utils.Transform(node)
        for attribute in attributes:
            if not performance_utils.obj_exists("{0}.{1}".format(node, attribute)):
                continue
                
            # Add random value(within amplidude range) keyframes to selected attributes
            for frame in keyframes:
                if seed:
                    random.seed(seed)
                random_number = random.uniform(-1*amplitude, 1*amplitude)
                if use_current_value:
                
                    # add the value to the current value
                    random_number = cmds.getAttr("{0}.{1}".format(node, attribute)) + random_number
                cmds.setKeyframe(node, attribute=attribute, time=frame[0], value=random_number) # Because the keyframe list I am passing here is a list of lists. it's wonky but ok for now 