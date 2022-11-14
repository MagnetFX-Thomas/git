import bpy
from bpy.utils import register_class, unregister_class


# ------------------------------------------------------------------------
#    BLENDER TOPBAR MENU
# ------------------------------------------------------------------------

class TOPBAR_MT_MagnetFX_PipelineSetup_SubMenu(bpy.types.Menu):
    bl_label = "Pipeline Setup"

    def draw(self, context):
        layout = self.layout
        layout.operator("magnetfx.addons_setup", text = "Install/Update Magnet FX Addons")

        layout = self.layout
        layout.operator("magnetfx.startup_scene_setup", text = "Install Base Startup Scene")
        
        layout1 = self.layout
        layout1.operator("magnetfx.aces_setup", text = "Auto configure ACES color profiles")

        layout2 = self.layout
        layout2.operator("magnetfx.update_asset_libraries", text = "Update Magnet FX asset libraries")





class TOPBAR_MT_MagnetFX_ThirdPartySetup_SubMenu(bpy.types.Menu):
    bl_label = "Third-Party Addons"

    def draw(self, context):
        layout = self.layout
        layout.operator("magnetfx.install_dmream_textures_addon", text = "Install Dream Textures Addon")





class TOPBAR_MT_MagnetFX_Settings_SubMenu(bpy.types.Menu):
    bl_label = "Settings"

    def draw(self, context):
        layout = self.layout
        layout.operator("magnetfx.open_render_configs_file", text = "Open Render Config File")





class TOPBAR_MT_MagnetFX(bpy.types.Menu):
    bl_label = "Magnet FX"

    def draw(self, context):
        layout = self.layout
        layout.menu("TOPBAR_MT_MagnetFX_PipelineSetup_SubMenu")
        layout.menu("TOPBAR_MT_MagnetFX_ThirdPartySetup_SubMenu")
        layout.menu("TOPBAR_MT_MagnetFX_Settings_SubMenu")

    def menu_draw(self, context):
        self.layout.menu("TOPBAR_MT_MagnetFX")





classes = ([
        TOPBAR_MT_MagnetFX_PipelineSetup_SubMenu,
        TOPBAR_MT_MagnetFX_ThirdPartySetup_SubMenu,
        TOPBAR_MT_MagnetFX_Settings_SubMenu,
        TOPBAR_MT_MagnetFX
        ])


def register():
    global classes
    for cls in classes:
        register_class(cls)
    
    bpy.types.TOPBAR_MT_editor_menus.append(TOPBAR_MT_MagnetFX.menu_draw)
        
    #pipeline_core.register()


def unregister():
    bpy.types.TOPBAR_MT_editor_menus.remove(TOPBAR_MT_MagnetFX.menu_draw)

    global classes
    for cls in classes:
        unregister_class(cls)
        
    
    #pipeline_core.unregister()
