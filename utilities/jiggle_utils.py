"""
Utilities for jiggle rig
Use Case:
-select animation control and apply jiggle simulation
-option between position and rotation jiggle
-existing animation will be baked into the jiggle
-revising animation will require deleting jiggle rig or baking jiggle rig
-If a constraint connection already exists on the animation control, jiggle rig creation will be denied
"""
from maya import cmds

from as_maya_tools.utilities import performance_utils, attribute_utils, constraint_utils, timeline_utils, maya_node_utils, decorators

JIGGLE_RIG_TAG = "JIGGLE_RIG_TAG"

class JiggleRig(object):
    """
    Jiggle rig
    """
    def __init__(self, **kwargs):
        """
        Init a jiggle rig instance
        """
        self.main_group = None # maya_node_utils.MayaNode: Group containing all jiggle rig nodes
        self.transform = None # attribute_utils.Transform: Node connected to jiggle rig
        self.transform_constraint = None # constraint connecting transform to jiggle rig
        self.jiggle_geometry = None # maya_node_utils.MayaNode: Geometry with jiggle deform applied
        self.jiggle_deform_node = None # maya_node_utils.MayaNode: Jiggle deformer node
        self.disk_cache_node = None # str: disk cache node to store jiggle deform cache
        self.animation_data_locator = None #  maya_node_utils.MayaNode: locator with original animation baked to it. Animation is baked across the animation frame range
        self.jiggle_locator = None #  maya_node_utils.MayaNode: Locator attached to the jiggle geometry. The passed node will be constrained to this
        
    @decorators.suspend_refresh
    @decorators.undoable_chunk
    @decorators.maintain_selection
    def create_jiggle_rig(self, name="jiggle_rig_01", node=None, **kwargs):
        """
        Create a jiggle rig
        :param str name: name of jiggle rig
        :param str node: node to attach to jiggle rig
        """
        self._init_transform(node, **kwargs)
        if self.transform is None:
            return
        self._create_main_group(name)
        if self.main_group is None:
            return
        self._create_jiggle_geometry()
        self._create_jiggle_deform_node()
        self._create_animation_data_locator()
        self._create_jiggle_locator()
        # build connections and create parent hierarchy
        self._build_rig()
        return
        
    def get_jiggle_rig(self, name):
        """
        Get an existing jiggle rig
        :param str name: name of jiggle rig
        """
        if not performance_utils.obj_exists("{0}.{1}".format(name, JIGGLE_RIG_TAG)):
            return
        self.main_group = maya_node_utils.MayaNode(node = name)
        self.transform_constraint = maya_node_utils.MayaNode(node = cmds.listConnections("{0}.transform_constraint".format(self.main_group.long_name))[0])
        self.jiggle_geometry = maya_node_utils.MayaNode(node = cmds.listConnections("{0}.jiggle_geometry".format(self.main_group.long_name))[0])
        self.jiggle_deform_node = maya_node_utils.MayaNode(node = cmds.listConnections("{0}.jiggle_deform_node".format(self.main_group.long_name))[0])
        self.disk_cache_node = maya_node_utils.MayaNode(node = cmds.listConnections("{0}.disk_cache_node".format(self.main_group.long_name))[0])
        self.animation_data_locator = maya_node_utils.MayaNode(node = cmds.listConnections("{0}.animation_data_locator".format(self.main_group.long_name))[0])
        self.jiggle_locator = maya_node_utils.MayaNode(node = cmds.listConnections("{0}.jiggle_locator".format(self.main_group.long_name))[0])
        self.transform = maya_node_utils.MayaNode(node = cmds.listRelatives(self.transform_constraint.long_name, parent=True, fullPath=True)[0])
        
    def _create_main_group(self, name):
        """
        init the name. make sure the name is unique
        :param str name: name of jiggle rig
        """
        if not performance_utils.obj_exists(name):
            self.main_group = maya_node_utils.MayaNode(node= cmds.group(name=name, empty=True))
            # This attribute is used as a tag to declair it as a jiggle rig
            cmds.addAttr(self.main_group.long_name, keyable=False, attributeType="message", longName=JIGGLE_RIG_TAG)
            return
        performance_utils.message("A Node named {0} already exists. Use a unique name".format(name))
        
    def _init_transform(self, node, require_translation=True, require_rotation=True, **kwargs):
        """
        init the node as a transform object from the attribute_utils module
        :param str node: node to attach to jiggle rig
        :param bool require_translation: option to require tranlation attibutes to be open
        :param bool require_rotation: option to require rotation attributes to be open
        """
        if not performance_utils.obj_exists(node):
            performance_utils.message("{0} node doesn't exist".format(node))
            return
            
        transform = attribute_utils.Transform(node)
        if require_translation:
            for attribute in transform.translate:
                if attribute.is_locked():
                    performance_utils.message("{0} Is locked so the jiggle rig cannot be connected properly".format(attribute.attribute_path))
                    return
                if attribute.get_connections():
                    for connection in attribute.get_connections():
                        if "Constraint" in cmds.nodeType(connection):
                            performance_utils.message("{0} has an existing constraint connection and cannot be connected to a jiggle rig".format(transform.transform_node))
                            return
        if require_rotation:
            for attribute in transform.rotate:
                if attribute.is_locked():
                    performance_utils.message("{0} Is locked so the jiggle rig cannot be connected properly".format(attribute.attribute_path))
                    return
                if attribute.get_connections():
                    for connection in attribute.get_connections():
                        if "constraint" in cmds.nodeType(connection):
                            performance_utils.message("{0} has an existing constraint connection and cannot be connected to a jiggle rig".format(transform.transform_node))
                            return
                
        self.transform = attribute_utils.Transform(node)
        
    def _create_jiggle_geometry(self, size=2):
        """
        create the jiggle geometry
        :param float size: size of jiggle geometry
        """
        position = self.transform.get_translation(world_space=True)
        vertex_points = [position,(position[0] + size, position[1] + size, position[2]),(position[0] - size, position[1] + size, position[2])]
        self.jiggle_geometry = cmds.polyCreateFacet(name="{0}_jiggle_geometry".format(self.main_group.short_name), point=vertex_points)[0]
        self.jiggle_geometry = maya_node_utils.MayaNode(node=self.jiggle_geometry)

        
    def _create_animation_data_locator(self):
        """
        Init the animation data locator
        """
        self.animation_data_locator = cmds.spaceLocator(name="{0}_animation_data_locator".format(self.main_group.short_name))[0]
        self.animation_data_locator = maya_node_utils.MayaNode(node=self.animation_data_locator)
        temp_constraint = constraint_utils.create_parent_constraint(
            parent=self.transform.transform_node,
            child=self.animation_data_locator.long_name,
            maintain_offset=False)
            
        animation_range = timeline_utils.get_animation_range()
        
        cmds.bakeResults(
            self.animation_data_locator.long_name,
            time=(animation_range[0],animation_range[1]),
            simulation=True)
        cmds.delete(temp_constraint)
        
    def _create_jiggle_deform_node(self, stiffness=0.4, damping=0.4, weight=0.8):
        """
        Create a jiggle deform on selected mesh. Can select mesh or Transform with mesh object
        :param str mesh: name of mesh to apply deform to
        :param str name: name of deformer node
        :param float stiffness: stiffness value
        :param float damping: damping value
        :param float weight: weight value
        :return str: name of jiggle deform node
        """
        jiggle_deform_node = cmds.deformer(self.jiggle_geometry.shape, name="{0}_jiggle_deform_node".format(self.main_group.short_name), type="jiggle")[0]
        self.jiggle_deform_node = maya_node_utils.MayaNode(node=jiggle_deform_node)
        
        # connect time node to jiggle deform node
        cmds.connectAttr("time1.outTime", "{0}.currentTime".format(self.jiggle_deform_node.long_name))
        
        # create caching node
        self.disk_cache_node = cmds.createNode("diskCache", name="{0}_jiggle_disk_cache".format(self.main_group.short_name))
        self.disk_cache_node = maya_node_utils.MayaNode(node=self.disk_cache_node)
        cmds.setAttr("{0}.hiddenCacheName".format(self.disk_cache_node.long_name), "{0}_jiggle_disk_cache".format(self.main_group.short_name), type="string")
        cmds.setAttr("{0}.cacheType".format(self.disk_cache_node.long_name), "mcj", type="string")
        cmds.connectAttr("{0}.diskCache".format(self.disk_cache_node.long_name), "{0}.diskCache".format(self.jiggle_deform_node.long_name))
        
        # set attributes
        cmds.setAttr("{0}.enable".format(self.jiggle_deform_node.long_name), 0)
        cmds.setAttr("{0}.stiffness".format(self.jiggle_deform_node.long_name), stiffness)
        cmds.setAttr("{0}.damping".format(self.jiggle_deform_node.long_name), damping)
        cmds.setAttr("{0}.jiggleWeight".format(self.jiggle_deform_node.long_name), weight)
        
    def _create_jiggle_locator(self):
        """
        create the jiggle locator attached to the jiggle geometry
        """
        self.jiggle_locator = maya_node_utils.MayaNode(node=cmds.spaceLocator(name="{0}_jiggle_locator".format(self.main_group.short_name))[0])
        cmds.pointOnPolyConstraint("{0}.vtx[0]".format(self.jiggle_geometry.long_name), self.jiggle_locator.long_name)
        
    def _build_rig(self):
        """
        Parent and attach all rig elements together
        """
        self.animation_data_locator.set_parent(self.main_group)
        self.jiggle_geometry.set_parent(self.animation_data_locator)
        self.jiggle_locator.set_parent(self.main_group)
        
        # Attach transform node to jiggle. This inits the transform constraint
        self.transform_constraint = constraint_utils.create_parent_constraint(
            parent=self.jiggle_locator.long_name,
            child=self.transform.transform_node,
            maintain_offset=True)[0]
        self.transform_constraint = maya_node_utils.MayaNode(node=self.transform_constraint)
        
        # Connect jiggle attributes to main group
        self._connect_jiggle_attributes_to_main_group()
        
        # Connect all the rig components to the main group to access later
        self._connect_rig_items_to_main_group()
        
        # hide main group
        self.main_group.set_visible(0)
    
    def _connect_jiggle_attributes_to_main_group(self):
        """
        Connect the jiggle attributes to the main group
        """
        hide_attributes = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"]
        for attribute in hide_attributes:
            cmds.setAttr("{0}.{1}".format(self.main_group.long_name, attribute), keyable=False, channelBox=False)
            
        cmds.addAttr(
            self.main_group.long_name,
            attributeType="double",
            longName="stiffness",
            defaultValue=0.3,
            hidden=False,
            keyable=True
        )
        cmds.addAttr(
            self.main_group.long_name,
            attributeType="double",
            longName="damping",
            defaultValue=0.3,
            hidden=False,
            keyable=True
        )
        cmds.addAttr(
            self.main_group.long_name,
            attributeType="double",
            longName="jiggleWeight",
            defaultValue=0.8,
            hidden=False,
            keyable=True
        )
        
        cmds.connectAttr("{0}.{1}".format(self.main_group.long_name, "stiffness"), "{0}.{1}".format(self.jiggle_deform_node.long_name, "stiffness"))
        cmds.connectAttr("{0}.{1}".format(self.main_group.long_name, "damping"), "{0}.{1}".format(self.jiggle_deform_node.long_name, "damping"))
        cmds.connectAttr("{0}.{1}".format(self.main_group.long_name, "jiggleWeight"), "{0}.{1}".format(self.jiggle_deform_node.long_name, "jiggleWeight"))
    
    def _connect_rig_items_to_main_group(self):
        """
        connect rig nodes to the main group node via message attribute
        """
        self._connect_to_message_attribute(self.transform_constraint, "transform_constraint")
        self._connect_to_message_attribute(self.jiggle_geometry, "jiggle_geometry")
        self._connect_to_message_attribute(self.jiggle_deform_node, "jiggle_deform_node")
        self._connect_to_message_attribute(self.disk_cache_node, "disk_cache_node")
        self._connect_to_message_attribute(self.animation_data_locator, "animation_data_locator")
        self._connect_to_message_attribute(self.jiggle_locator, "jiggle_locator")
        
    def _connect_to_message_attribute(self, maya_node_item, name):
        """
        connect an item to the main group
        :param maya_node_utils.MayaNode maya_node_item: maya node item to connect
        """
        # Create message attribute
        cmds.addAttr(self.main_group.long_name, keyable=False, attributeType="message", longName=name)
        cmds.addAttr(maya_node_item.long_name, keyable=False, attributeType="message", longName=name)
        
        # Connect to the attribute
        cmds.connectAttr("{0}.{1}".format(maya_node_item.long_name, name), "{0}.{1}".format(self.main_group.long_name, name))
        
        

def create_jiggle_rig_from_selection(**kwargs):
    """
    create jiggle rigs from selection
    """
    selection = cmds.ls(selection=True)
    if len(selection) < 1:
        performance_utils.message("No objects selected. Select a node to apply jiggle rig to")
        
    for item in selection:
        index = 0
        name = item.replace(":", "_")
        indexed_name = "{0}_{1}".format(name, index)
        while performance_utils.obj_exists(indexed_name):
            index += 1
            indexed_name = "{0}_{1}".format(name, index)
            
        try:
            jiggle_rig_instance = JiggleRig(**kwargs)
            jiggle_rig_instance.create_jiggle_rig(name=indexed_name, node=item, **kwargs)
        except Exception as e:
            print(e)
            
    return


def get_all_jiggle_rigs():
    """
    Get all existing jiggle rigs
    """
    transform_nodes = cmds.ls(type="transform")
    jiggle_rigs = []
    for transform_node in transform_nodes:
        if cmds.listAttr(transform_node, string=JIGGLE_RIG_TAG):
            jiggle_rigs.append(transform_node)
    return jiggle_rigs
    
    
def select_jiggle_rigs(rig_names):
    """
    Select jiggle rigs
    :param list[str] rig_name: names of jiggle rigs
    """
    if len(rig_names) < 1:
        return
    for rig_name in rig_names:
        if not performance_utils.obj_exists("{0}.{1}".format(rig_name, JIGGLE_RIG_TAG)):
            continue
    cmds.select(rig_names, replace=True)
    return
    
    
def delete_jiggle_rigs(rig_names):
    """
    Delete jiggle rigs
    :param list[str] rig_names: names of rigs to delete
    """
    if len(rig_names) < 1:
        return
    cmds.delete(rig_names)
    

@decorators.suspend_refresh
@decorators.undoable_chunk
def bake_jiggle_rigs(rig_names):
    """
    Bake all jiggle rigs passed
    :param list[str] rig_names: list of jiggle rig names
    """
    if len(rig_names) < 1:
        return
    transform_nodes = []
    
    # Get all the jiggle rig main groups for deletion and transforms for baking
    for rig_name in rig_names:
        if not performance_utils.obj_exists("{0}.{1}".format(rig_name, JIGGLE_RIG_TAG)):
            continue
        jiggle_rig_instance = JiggleRig()
        jiggle_rig_instance.get_jiggle_rig(rig_name)
        transform_nodes.append(jiggle_rig_instance.transform.long_name)
        
    # Use animation from range for bake
    animation_range = timeline_utils.get_animation_range()
    cmds.bakeResults(
        transform_nodes,
        time=(animation_range[0],animation_range[1]),
        simulation=True)
        
    # delete jiggle rigs
    delete_jiggle_rigs(rig_names)
    return