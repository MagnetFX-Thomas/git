import bpy
from bpy.utils import register_class, unregister_class


# ------------------------------------------------------------------------
#    AUTOMATIC RENDER SETUP PANEL
# ------------------------------------------------------------------------

class MAGNETFX_PT_AutomaticRenderSetup(bpy.types.Panel):
    bl_label = "Automatic Render Setup"
    bl_idname = "MAGNETFX_PT_AutomaticRenderSetup"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Magnet FX"
    bl_options = {"DEFAULT_CLOSED"}
 
    def draw(self, context):
        layout = self.layout


        layout = self.layout
        layout.operator("mfx.automatic_render_setup")





# ------------------------------------------------------------------------
#    SCENE PREP PANEL
# ------------------------------------------------------------------------

class MAGNETFX_PT_ScenePrep(bpy.types.Panel):
    bl_label = "Scene Prep"
    bl_idname = "MAGNETFX_PT_ScenePrep"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Magnet FX"
 
    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator("magnetfx.create_render_layer")
 
        layout.separator()
 
        row = layout.row()
        row.operator("magnetfx.load_base_lighting")
        
        row = layout.row()
        row.operator("magnetfx.open_filebrowser")
        
        layout.separator()

        layout = self.layout
        layout.operator("mfx.load_render_config")

        layout.separator()

        layout = self.layout
        layout.operator("magnetfx.scene_cleanup")





# ------------------------------------------------------------------------
#    PREVIEW PANEL
# ------------------------------------------------------------------------

class MAGNETFX_PT_ProductPreview(bpy.types.Panel):
    bl_label = "Product Preview"
    bl_idname = "MAGNETFX_PT_ProductPreview"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Magnet FX"
    bl_options = {"DEFAULT_CLOSED"}
 
    def draw(self, context):
        layout = self.layout
 
        row = layout.row()
        row.operator("magnetfx.create_preview_animation")
        
        row = layout.row()
        row.operator("magnetfx.remove_animation")





# ------------------------------------------------------------------------
#    RENDER OUTPUT PANEL
# ------------------------------------------------------------------------

class MAGNETFX_PT_RenderOutput(bpy.types.Panel):
    bl_label = "Render Output"
    bl_idname = "MAGNETFX_PT_RenderOutput"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Magnet FX"
 



    def execute(self, context):
        currentScene = bpy.context.window.scene.name

        bpy.data.scenes[currentScene].rlm.output_name = "{rlayer}/{version}/{rlayer}_{rpass}_"




    def draw(self, context):

        file_format = context.scene.render.image_settings.file_format
        #view_layer = context.scene.view_layers[context.scene.rlm.active_renderlayer_index]

        layout = self.layout

        row = layout.row()
        row.prop(context.scene.rlm, "output_dir", text="")

        row = layout.row()
        row.prop(context.scene.rlm, "output_name", text="")
        row.menu("RLM_MT_renderlayer_tokens", text="", icon='DOWNARROW_HLT')
        #bpy.data.scenes[currentScene].rlm.output_name = "{rlayer}/{version}/{rlayer}_{rpass}_"
 
        layout.separator()

        layout = self.layout
        row = layout.row()


        image_settings = context.scene.render.image_settings
        layout.template_image_settings(image_settings, color_management=False)

        row = layout.row()
        row.prop(context.scene.render, "film_transparent", text="Transparent Background")

        #TODO: transparent glass checkbox works but is greyd out?
        
        row = layout.row()
        row.prop(context.scene.cycles, "film_transparent_glass", text="Transparent Glass")
        row.active = context.scene.render.film_transparent and context.scene.cycles.film_transparent_glass
        row.prop(context.scene.cycles, "film_transparent_roughness", text="Roughness Threshold")





# ------------------------------------------------------------------------
#    RENDER PROPERTIES PANEL
# ------------------------------------------------------------------------

class MAGNETFX_PT_RenderProperties(bpy.types.Panel):
    bl_label = "Render Properties"
    bl_idname = "MAGNETFX_PT_RenderProperties"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Magnet FX"



    def draw(self, context):
        layout = self.layout
        row = layout.row()

        cscene = context.scene.cycles

        row = layout.row()
        layout.use_property_split = True
        layout.use_property_decorate = False
        heading = layout.column(align=True, heading="Noise Threshold")
        row = heading.row(align=True)
        row.prop(cscene, "use_adaptive_sampling", text="")
        sub = row.row()
        sub.active = cscene.use_adaptive_sampling
        sub.prop(cscene, "adaptive_threshold", text="")

        col = layout.column(align=True)
        if cscene.use_adaptive_sampling:
            col.prop(cscene, "samples", text=" Max Samples")
            col.prop(cscene, "adaptive_min_samples", text="Min Samples")
        else:
            col.prop(cscene, "samples", text="Samples")
        col.prop(cscene, "time_limit")





# ------------------------------------------------------------------------
#    RENDERING PANEL
# ------------------------------------------------------------------------

class MAGNETFX_PT_Rendering(bpy.types.Panel):
    bl_label = "Rendering"
    bl_idname = "MAGNETFX_PT_Rendering"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Magnet FX"


    def draw(self, context):
        currentScene = bpy.context.window.scene.name

        layout = self.layout

        row = layout.row()
        row.label(text = "Version:")
        row.prop(context.scene.rlm, 'version', text = "")
    

        layout.separator()

        row = layout.row()
        row.label(text = "Camera:")
        row.prop(context.scene, "camera", text = "")

        layout.separator()

        row = layout.row()
        row.label(text = "Output Path:")
        row.label(text = bpy.data.scenes[currentScene].rlm.output_dir)

        layout.separator()

        row = layout.row()
        row.prop(context.scene.render, "resolution_x", text = "Width")
        row.prop(context.scene.render, "resolution_y", text = "Height")

        row = layout.row()
        row.prop(context.scene.render, "resolution_percentage", slider = True, text = "Resolution Scale")

        row = layout.row()
        row.label(text = "Frame Range:")
        row.prop(context.scene, "frame_start", text = "")
        row.prop(context.scene, "frame_end", text = "")

        layout.separator()
        layout.separator()

        ###### TODO: render via operator has no option to set animation flag?! Make an extra class, there you can use the python function
        

        layout = self.layout
        layout.operator("magnetfx.update_all_render_outputs", text = ">>> UPDATE OUTPUT PATHS <<<")

        layout.separator()

        row = layout.row()
        #row.operator("render.render", text = "Render Local")
        row.operator("render.render", text = "Rendln Local")

        ###### TODO: deadline installation for submit check
        row = layout.row()
        row.operator("ops.submit_blender_to_deadline", text = "Rendln via Deadline")





classes = ([
        MAGNETFX_PT_AutomaticRenderSetup,
        MAGNETFX_PT_ScenePrep,
        MAGNETFX_PT_ProductPreview,
        MAGNETFX_PT_RenderOutput,
        MAGNETFX_PT_RenderProperties,
        MAGNETFX_PT_Rendering
        ])



def register():

    global classes
    for cls in classes:
        register_class(cls)



def unregister():

    global classes
    for cls in classes:
        unregister_class(cls)
