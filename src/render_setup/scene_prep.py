import bpy
from bpy.utils import register_class, unregister_class
from bpy_extras.io_utils import ImportHelper

import os
import json

from .. import helper




# ------------------------------------------------------------------------
#    GLOBAL PATHS
# ------------------------------------------------------------------------


render_configs = "D:\\Projects\\Blender_Pipeline_02\\pipeline_assets\\Assets\\Configs\\render_configs.json"
base_product_lighting = "D:\\Projects\\Blender_Pipeline_02\\pipeline_assets\\Assets\\Lighting\\Base_Product_Lighting.blend"
base_product_lighting_hdr = "D:\\Projects\\Blender_Pipeline_02\\asset_library\\HDRI\\Custom\\Metro_desaturated_blender.hdr"

KB_cam_product_renderings = "D:\\Projects\\Blender_Pipeline_02\\pipeline_assets\\Assets\Cameras\\Knorr_Bremse_Products_Default_Cam.blend"

KB_comp_group = "D:\\Projects\\Blender_Pipeline_02\\pipeline_assets\\Assets\\Comp\\Blender_Comp_Nodes\\KB_Compositing.blend"


"""
render_configs = "D:\\Projects\\Blender_Pipeline_02\\assets\pipeline_assets\\Assets\\Configs\\render_configs.json"
base_product_lighting = "W:\\Blender_Pipeline\\Assets\\Lighting\\Base_Product_Lighting.blend"
base_product_lighting_hdr = "W:\\Blender_Asset_Library\\HDRI\\Custom\\Metro_desaturated_blender.hdr"

KB_cam_product_renderings = "W:\Blender_Pipeline\Assets\Cameras\\Knorr_Bremse_Products_Default_Cam.blend"
#KB_comp_group = "Y:\\_Team\Jonas\\Blender Pipeline Tests\\coupler_capaxia\\coupler_capaxia_aces_comp.blend"

KB_comp_group = "W:\\Blender_Pipeline\\Assets\\Comp\\Blender_Comp_Nodes\\KB_Compositing.blend"
"""




# ------------------------------------------------------------------------
#    HELPER
# ------------------------------------------------------------------------

def update_comp_output_paths(layer_name):
    currentScene = bpy.context.window.scene.name

    if helper.check_node_exists("KB_Compositing_Group"):

        #get file output
        #TODO: get the file
        #file_output = bpy.context.scene.node_tree.nodes.new(type = "CompositorNodeOutputFile")
        file_output = bpy.context.scene.node_tree.nodes[layer_name]

        #update comp file output nodes
        #set output path in file output
        file_output.base_path = bpy.data.scenes[currentScene].rlm.output_dir
        file_output.file_slots[0].path = "OUTPUT_Comp/v" + "%02d"%(bpy.data.scenes[currentScene].rlm.version,) + "/" + bpy.path.basename(bpy.context.blend_data.filepath).split(".blend")[0] + "_" + layer_name.replace(" ", "_")




# ------------------------------------------------------------------------
#    ADDON DEPENDENCY CHECK
# ------------------------------------------------------------------------

def addonCheckRenderLayerManager():

    enabledAddonsList = []

    for addon in bpy.context.preferences.addons:
        enabledAddonsList.append(addon.module)

    #print(enabledAddonsList)

    if "node_renderlayer_manager" not in enabledAddonsList:
        bpy.ops.preferences.addon_enable(module="node_renderlayer_manager")








# ------------------------------------------------------------------------
#    UPDATE RENDER OUTPUTS OPERATOR
# ------------------------------------------------------------------------

class MAGNETFX_OT_UpdateRenderOutputs(bpy.types.Operator):
    """Update all render outputs"""
    bl_idname = "magnetfx.update_all_render_outputs"
    bl_label = "Update all render outputs"
    bl_options = {'INTERNAL'}


    def execute(self, context):
        
        bpy.ops.rlm.create_nodes()


        try:
            comp_group = bpy.context.scene.node_tree.nodes["KB_Compositing_Group"]
        except:
            comp_group = None
            print("No Blender comp available")

        #connect nodes
        product_renderOut = bpy.context.scene.node_tree.nodes.get("Product-RLM")
        productAO_renderOut = bpy.context.scene.node_tree.nodes.get("Product_AO-RLM")
        productShadowAO_renderOut = bpy.context.scene.node_tree.nodes.get("Floor_Shadow_AO-RLM")
        #print(productRenderOut.name)

        #temp workaround to reactivate data pass
        #TODO: add the data layer to the node creation via RLM plugin (check how to add it via the save template function of RLM plugin like with the cryptomattes)
        bpy.context.window.view_layer = bpy.context.scene.view_layers["Product"]
        bpy.context.view_layer.cycles.denoising_store_passes = True

        if comp_group:
            bpy.context.scene.node_tree.links.new(product_renderOut.outputs["Image"], comp_group.inputs[0])
            bpy.context.scene.node_tree.links.new(product_renderOut.outputs["Alpha"], comp_group.inputs[1])
            bpy.context.scene.node_tree.links.new(product_renderOut.outputs["Denoising Normal"], comp_group.inputs[2])
            bpy.context.scene.node_tree.links.new(product_renderOut.outputs["Denoising Albedo"], comp_group.inputs[3])

            bpy.context.scene.node_tree.links.new(productAO_renderOut.outputs["Image"], comp_group.inputs[4])
            bpy.context.scene.node_tree.links.new(productShadowAO_renderOut.outputs["Image"], comp_group.inputs[5])

            #update_comp_output_paths()
            update_comp_output_paths("Composite Preview")
            update_comp_output_paths("Product")
            update_comp_output_paths("Product AO")
            update_comp_output_paths("Ground AO")
    
        

        self.report({"INFO"}, "Render Outputs Updated")
        return {"FINISHED"}





# ------------------------------------------------------------------------
#    Import Camera for Automatic Render Setup via Render Config
# ------------------------------------------------------------------------

def import_camera_from_render_config(config_name):
    #TODO: set camera in settings (depents on cam name from appended file?)

    with open(render_configs, "r") as f:
            data = json.load(f)

    #set render
    for p in data["projects"]:
        if p["name"] == config_name:
            try:
                camera_path = p["camera_import"]
                helper.append_item(camera_path, "Object", "Camera", False)
            except:
                print("No Camera in Render Config")

    f.close()





# ------------------------------------------------------------------------
#    LOAD RENDER CONFIG
# ------------------------------------------------------------------------

def SetRenderConfigSettings(config_name):


    #-------  Helper  -------#
    currentScene = bpy.context.window.scene.name

    
    def create_comp_outputs(layer_name):
        #create file output
        file_output = bpy.context.scene.node_tree.nodes.new(type = "CompositorNodeOutputFile")
        
        file_output.name = layer_name
        file_output.label = layer_name
        file_output.format.file_format = "PNG"
        
        if layer_name == "Composite Preview":
            bpy.context.scene.node_tree.links.new(comp_group.outputs["Composite"], file_output.inputs[0])
        else:
            #connect comp group to file output
            bpy.context.scene.node_tree.links.new(comp_group.outputs[layer_name], file_output.inputs[0])
        
        #set output path in file output
        file_output.base_path = bpy.data.scenes[currentScene].rlm.output_dir
        file_output.file_slots[0].path = "OUTPUT_Comp/v" + "%02d"%(bpy.data.scenes[currentScene].rlm.version,) + "/" + bpy.path.basename(bpy.context.blend_data.filepath).split(".blend")[0] + "_" + layer_name.replace(" ", "_")


    def CheckNodeExists(node_name):
        try:
            bpy.context.scene.node_tree.nodes[node_name]
            return True
        except:
            return False




    #-------  Load Config -------#

    #### File Paths ####
    filepath = bpy.data.filepath
    scene_directory = os.path.dirname(filepath)
    scene_subdirectories = scene_directory.split("_3D")



    #### Base Settings ####

    #set renderer to cycles
    #bpy.context.scene.render.engine = "CYCLES"

    #enable transparent for alpha
    bpy.context.scene.render.film_transparent = True
    bpy.data.scenes[currentScene].cycles.film_transparent_glass = True

    #disable tiling
    bpy.context.scene.cycles.use_auto_tile = False

    #set output format
    bpy.context.scene.render.image_settings.file_format = "OPEN_EXR"

    #deactivate Master layer for rendering
    try:
        bpy.context.scene.view_layers["Master"].use = False
    except:
        pass



    #load render config file and set attributes
    with open(render_configs, "r") as f:
        data = json.load(f)

    #set render
    for p in data["projects"]:
        if p["name"] == config_name:
            #normal projects like "A666" in the projects root mount need a different path
            if p["name"] == "Default Still Rendering":
                bpy.data.scenes[currentScene].rlm.output_dir = scene_subdirectories[0] + "_COMPOSITING\\" + scene_subdirectories[1] + "\\3D_Elements\\"
            else:
                bpy.data.scenes[currentScene].rlm.output_dir = p["path_compositing"] + scene_subdirectories[1] + "\\3D_Elements\\"

            
            bpy.context.scene.render.engine = p["renderer"]
            if p["renderer"] == "CYCLES":
                bpy.context.scene.cycles.device = p["rendering_device"]
            
            bpy.context.scene.render.resolution_x = p["resolution_width"]
            bpy.context.scene.render.resolution_y = p["resolution_height"]

            bpy.context.scene.cycles.adaptive_min_samples = p["render_min_samples"]
            bpy.context.scene.cycles.samples = p["render_max_samples"]
            bpy.context.scene.cycles.adaptive_threshold = p["render_noise_threshold"]

            if p["animation"]:
                bpy.context.scene.frame_start = p["frame_start"]
                bpy.context.scene.frame_end = p["frame_end"]
            else:
                bpy.context.scene.frame_start = 1
                bpy.context.scene.frame_end = 1

            """
            if p["path_3d"] not in filepath:
                print("path not matching!")
                self.report({"INFO"}, "Base lighting setup loaded")
            else:
                print("path_3d: " + p["path_3d"])
                print("filepath: " + filepath)
                print("path matching!")
                """

    f.close()

    #set output name
    bpy.data.scenes[currentScene].rlm.output_name = "{rlayer}/{version}/{rlayer}_{rpass}_"

    #recreate render output nodes
    bpy.ops.rlm.create_nodes()

    #enable denoise data pass
    #temp workaround to reactivate data pass
    #TODO: add the data layer to the node creation via RLM plugin (check how to add it via the save template function of RLM plugin like with the cryptomattes)
    bpy.context.window.view_layer = bpy.context.scene.view_layers["Product"]
    bpy.context.view_layer.cycles.denoising_store_passes = True
    


    #-------  Create Comp File Output Nodes for KB Renderings -------#
    if config_name == "Knorr Bremse":
        #append comp node group
        #TODO: also imports a camera?!
        helper.append_item(KB_comp_group, "NodeTree", "KB_Compositing", True)

        #check if KB comp group was already created
        if not CheckNodeExists("KB_Compositing_Group"):

            #create KB_Compositing node group
            comp_group = bpy.context.scene.node_tree.nodes.new("CompositorNodeGroup")
            comp_group.name = "KB_Compositing_Group"
            comp_group.node_tree = bpy.data.node_groups["KB_Compositing"]


            


            #create comp file outputs
            create_comp_outputs("Composite Preview")
            create_comp_outputs("Product")
            create_comp_outputs("Product AO")
            create_comp_outputs("Ground AO")

        else:
            comp_group = bpy.context.scene.node_tree.nodes["KB_Compositing_Group"]
        
        #connect nodes
        product_renderOut = bpy.context.scene.node_tree.nodes.get("Product-RLM")
        productAO_renderOut = bpy.context.scene.node_tree.nodes.get("Product_AO-RLM")
        productShadowAO_renderOut = bpy.context.scene.node_tree.nodes.get("Floor_Shadow_AO-RLM")
        #print(productRenderOut.name)

        bpy.context.scene.node_tree.links.new(product_renderOut.outputs["Image"], comp_group.inputs[0])
        bpy.context.scene.node_tree.links.new(product_renderOut.outputs["Alpha"], comp_group.inputs[1])
        bpy.context.scene.node_tree.links.new(product_renderOut.outputs["Denoising Normal"], comp_group.inputs[2])
        bpy.context.scene.node_tree.links.new(product_renderOut.outputs["Denoising Albedo"], comp_group.inputs[3])

        bpy.context.scene.node_tree.links.new(productAO_renderOut.outputs["Image"], comp_group.inputs[4])
        bpy.context.scene.node_tree.links.new(productShadowAO_renderOut.outputs["Image"], comp_group.inputs[5])





# ------------------------------------------------------------------------
#    LOAD BASE LIGHTING
# ------------------------------------------------------------------------

#-------  Load Base Lighting Setup -------#
class MAGNETFX_OT_LoadBaseLightSetup(bpy.types.Operator):
    """Load Base Light Setup"""
    bl_idname = "magnetfx.load_base_lighting"
    bl_label = "Load Base Lighting Setup"
    #bl_options = {'INTERNAL'}


    def execute(self, context):


        ######################################### !!!!!!!!!!!!!!!!!!! TODO: appendCollection into helper? or change the append item to also support collections?


        #-------  Helper Functions -------#
        def appendCollection(filepath, collectionName):
            #file_path = base_product_lighting
            inner_path = "Collection"
            #object_name = "Lighting"
            
            bpy.ops.wm.append(
            filepath = os.path.join(filepath, inner_path, collectionName),
            directory = os.path.join(filepath, inner_path),
            filename = collectionName,
            do_reuse_local_id = True
            )




        def linkToNewCollection(object, collection):
            #TODO: What if an object is linked to more than one collection?
            try:
                #what if the object is linked to more collections?
                currentCollection = object.users_collection[0]
                
                collection.objects.link(object)
                currentCollection.objects.unlink(object)
                
            except:
                pass
        
        
        #load HDR via HDRI Wizard addon
        bpy.ops.hdriw.set_image(name = "Metro_desaturated", filename = base_product_lighting_hdr)
        
        
        #append lighting collection

        #TODO: check if lighting collection exists, if not create it
        #append lighting and reflection geo collections from the base lighting file
        appendCollection(base_product_lighting, "Lighting")
        #CreateCollection("Additional Lights")
        #appendCollection(base_product_lighting, "Product Lights Default")
        #appendCollection(base_product_lighting, "Reflection_Geo")
        


        """
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        #BUG: Sometomes doesn't work as intended...needs to check if there is a lighting layer. AND WE NEED TO DELETE THE "COLLECTION" COLLECTION!!!!!!!!!!!!!!!!!!!
        bpy.data.collections["Lighting"].children.link(bpy.data.collections["Product Lights Default"])
        bpy.context.scene.collection.children.unlink(bpy.data.collections["Product Lights Default"])

        bpy.data.collections["Lighting"].children.link(bpy.data.collections["Additional Lights"])
        bpy.context.scene.collection.children.unlink(bpy.data.collections["Additional Lights"])
        """

        

        
        lightList = [obj for obj in list(bpy.context.scene.objects) if obj.type == "LIGHT"]
        for object in lightList:
            #print(object)
            linkToNewCollection(object, bpy.data.collections['Lighting'])


        #link appended lights and reflection grids to the lighting collection if there already is one
        for obj in bpy.context.scene.objects:
            if obj.name.startswith("ReflectionGrid"):
                collection_to_delete = obj.users_collection[0]
                linkToNewCollection(obj, bpy.data.collections["Lighting"])
        
        
        if collection_to_delete.name != "Lighting":
            bpy.data.collections.remove(collection_to_delete)
        
        
        self.report({"INFO"}, "Base lighting setup loaded")
        return {"FINISHED"}





# ------------------------------------------------------------------------
#    SELECT CUSTOM HDR
# ------------------------------------------------------------------------

#-------  Select Custom HDR -------#
class MAGNETFX_OT_SelectHDR(bpy.types.Operator, ImportHelper):
    """Load a custom HDR"""
    bl_idname = "magnetfx.open_filebrowser"
    bl_label = "Select Custom HDR"
    
    filter_glob: bpy.props.StringProperty(
        default='*.hdr;*.exr',
        options={'HIDDEN'}
    )
    


    def execute(self, context):
        """Set chosen HDR environment"""

        filename, extension = os.path.splitext(self.filepath)

        bpy.ops.hdriw.set_image(name = filename.split("\\")[-1], filename = self.filepath)
        
        return {'FINISHED'}








# ------------------------------------------------------------------------
#    LOAD RENDER CONFIG OPERATOR
# ------------------------------------------------------------------------

class MAGNETFX_OT_Load_Render_Config(bpy.types.Operator):
    """Load Render Presets"""
    bl_idname = "mfx.load_render_config"
    bl_label = "Load Render Config"
    bl_category = "MFX Pipeline"
    
    
    
    def item_callback(self, context):
        projectConfigList = ()

        with open(render_configs, "r") as f:
            data = json.load(f)
        
        for p in data["projects"]:
            projectConfigList += ((p["name"], p["name"], p["name"]),)

        f.close()

        return projectConfigList




    render_config : bpy.props.EnumProperty(
        name="Render Config",
        description="Load Render Configuration",
        items=item_callback,
        default=None,
        update=None,
        get=None,
        set=None)
    
    
    

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "render_config")
        
    
    def execute(self, context):

        currentScene = bpy.context.window.scene.name

        ################################## LOAD CONFIG PART

        #check if Render Layer Manager addon is activated
        addonCheckRenderLayerManager()

        #check if the scene is saved to get the correct output path
        if not bpy.data.is_saved:
            self.report({"ERROR"}, "Save the scene first")
            return {"CANCELLED"}
        
        #TODO: check file path with the location of the blend file
        currentScene = bpy.context.window.scene.name
        filepath = bpy.data.filepath.replace('\\', '/').split("_3D")[0]
        


        ############## !!! setting AOV needs rework! uses the index of the render layer list right now, not good.....
        #TODO: BUG!!! cryptomatte pass is added to the selected layer in RLM, it can be added to the wrong layer by accident!!!
        #TODO: checkboxes for useful passes via UI
        
        #switch to layer index 1 (product layer)
        bpy.data.scenes[currentScene].rlm.active_renderlayer_index = 1
        
        #add cryptomatte pass
        bpy.context.scene.rlm.use_cryptomatte_multilayer_exr = True

        rlayer = bpy.context.view_layer
        image_settings = bpy.context.view_layer.image_settings


        rlayer.passes.clear()

        item_sub_1 = rlayer.passes.add()
        item_sub_1.name = 'CryptoMaterial'
        item_sub_1.custom_name = 'CryptoMaterial'
        item_sub_1.selected = False
        item_sub_1.image_settings.name = ''
        item_sub_1.image_settings.file_format = 'OPEN_EXR_MULTILAYER'
        item_sub_1.image_settings.color_mode = 'RGBA'
        item_sub_1.image_settings.color_depth = '32'
        item_sub_1.image_settings.display_device = '---'
        item_sub_1.image_settings.compression = 15
        item_sub_1.image_settings.exr_codec = 'ZIP'
        item_sub_1.image_settings.jpeg2k_codec = 'JP2'
        item_sub_1.image_settings.quality = 90
        item_sub_1.image_settings.tiff_codec = 'DEFLATE'
        item_sub_1.image_settings.use_cineon_log = False
        item_sub_1.image_settings.use_jpeg2k_cinema_48 = False
        item_sub_1.image_settings.use_jpeg2k_cinema_preset = False
        item_sub_1.image_settings.use_jpeg2k_ycc = False
        item_sub_1.image_settings.use_preview = False
        item_sub_1.image_settings.use_zbuffer = False
        item_sub_1.image_settings.color_space = 'Raw'
        item_sub_1.image_settings.view_transform = '---'
        item_sub_1.image_settings.save_as_render = False



        SetRenderConfigSettings(self.render_config)


        #-------  Warning if project paths from blender file and outout render path are not amtching -------#
        renderPath = bpy.data.scenes[currentScene].rlm.output_dir

        if filepath not in renderPath:
            self.report({"WARNING"}, "Blender file location and render output path are not matchnig!")


        return {'FINISHED'}   





# ------------------------------------------------------------------------
#    SCENE CLEANUP
# ------------------------------------------------------------------------

class MAGNETFX_OT_Scene_CleanUp(bpy.types.Operator):
    """Clean Up Scene"""
    bl_idname = "magnetfx.scene_cleanup"
    bl_label = "Scene Clean Up"
    bl_options = {'INTERNAL'}


    def execute(self, context):
        print("cleanup!")
        #clean up unused data blocks
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)

        #clean up unused linked data blocks
        bpy.ops.outliner.orphans_purge(do_local_ids=False, do_linked_ids=True, do_recursive=True)

        #clean up unused local data blocks
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=False, do_recursive=True)


        self.report({"INFO"}, "Scene clean up finished")
        return {"FINISHED"}





# ------------------------------------------------------------------------
#    AUTOMATIC RENDER SETUP
# ------------------------------------------------------------------------

class MAGNETFX_OT_AutomaticRenderSetup(bpy.types.Operator):
    """Automatic Render Setup"""
    bl_idname = "mfx.automatic_render_setup"
    bl_label = "Automatic Render Setup"
    bl_category = "MFX Pipeline"
    


    ############################################### LOAD CONFIG PART ######

    auto_setups : bpy.props.EnumProperty(
        name="Automatic Render Setups",
        description="Automatic Render Setups",
        items = [("KB_Product", "Knorr Bremse Product Rendering", "Execute Automatic Render Setup for KB Products")],
        default=None,
        update=None,
        get=None,
        set=None)
    
    
    

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "auto_setups")
        
    
    def execute(self, context):

        currentScene = bpy.context.window.scene.name
        
        #check if the scene is saved to get the correct output path
        if not bpy.data.is_saved:
            self.report({"ERROR"}, "Save the scene first")
            return {"CANCELLED"}


        ############################################### MOVE TO CENTER PART ######

        product_selection = bpy.context.selected_objects

        if not product_selection:
            self.report({"ERROR"}, "Select the product first and then run the automation again")
            return {"CANCELLED"}

        print("---------")
        print(product_selection[0].name)

        zOffset = 0.38
        transform_offset = bpy.data.objects[product_selection[0].name].dimensions.z * 0.5 + zOffset

        bpy.context.scene.objects[product_selection[0].name].location = (0, 0, transform_offset)



        helper.append_item(KB_cam_product_renderings, "Object", "Camera", False)

        #load cam from render config
        #import_camera_from_render_config("Knorr Bremse")



        ############################################### CREATE RENDER LAYER ######

        bpy.ops.magnetfx.create_render_layer()

        #link selection to product collection
        helper.link_object_to_collection(product_selection[0], bpy.data.collections['Product'])



        ############################################### LOAD BASE LIGHTING ######

        bpy.ops.magnetfx.load_base_lighting()

        #check if Render Layer Manager addon is activated
        addonCheckRenderLayerManager()

        #TODO: check if the scene is saved to get the correct output path !!!

        if not bpy.data.is_saved:
            self.report({"ERROR"}, "Save the scene first")
            return {"CANCELLED"}



        ############## !!! setting AOV needs rework! uses the index of the render layer list right now, not good.....
        #TODO: BUG!!! cryptomatte pass is added to the selected layer in RLM, it can be added to the wrong layer by accident!!!
        #TODO: checkboxes for useful passes via UI
        
        #switch to layer index 1 (product layer)
        bpy.data.scenes[currentScene].rlm.active_renderlayer_index = 1
        
        

        #add cryptomatte pass
        bpy.context.scene.rlm.use_cryptomatte_multilayer_exr = True

        rlayer = bpy.context.view_layer
        image_settings = bpy.context.view_layer.image_settings


        rlayer.passes.clear()

        item_sub_1 = rlayer.passes.add()
        item_sub_1.name = 'CryptoMaterial'
        item_sub_1.custom_name = 'CryptoMaterial'
        item_sub_1.selected = False
        item_sub_1.image_settings.name = ''
        item_sub_1.image_settings.file_format = 'OPEN_EXR_MULTILAYER'
        item_sub_1.image_settings.color_mode = 'RGBA'
        item_sub_1.image_settings.color_depth = '32'
        item_sub_1.image_settings.display_device = '---'
        item_sub_1.image_settings.compression = 15
        item_sub_1.image_settings.exr_codec = 'ZIP'
        item_sub_1.image_settings.jpeg2k_codec = 'JP2'
        item_sub_1.image_settings.quality = 90
        item_sub_1.image_settings.tiff_codec = 'DEFLATE'
        item_sub_1.image_settings.use_cineon_log = False
        item_sub_1.image_settings.use_jpeg2k_cinema_48 = False
        item_sub_1.image_settings.use_jpeg2k_cinema_preset = False
        item_sub_1.image_settings.use_jpeg2k_ycc = False
        item_sub_1.image_settings.use_preview = False
        item_sub_1.image_settings.use_zbuffer = False
        item_sub_1.image_settings.color_space = 'Raw'
        item_sub_1.image_settings.view_transform = '---'
        item_sub_1.image_settings.save_as_render = False



        SetRenderConfigSettings("Knorr Bremse")

        #enable denoise data pass
        bpy.context.view_layer.cycles.denoising_store_passes = True
        
        return {'FINISHED'}   







classes = ([
        MAGNETFX_OT_UpdateRenderOutputs,
        MAGNETFX_OT_LoadBaseLightSetup,
        MAGNETFX_OT_SelectHDR,
        MAGNETFX_OT_Load_Render_Config,
        MAGNETFX_OT_Scene_CleanUp,
        MAGNETFX_OT_AutomaticRenderSetup
        ])



def register():
    
    global classes
    for cls in classes:
        register_class(cls)

def unregister():
    global classes
    for cls in classes:
        unregister_class(cls)