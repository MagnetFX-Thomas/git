import bpy
from bpy.utils import register_class, unregister_class

import os
import sys
import subprocess
import shutil
from pathlib import Path

from . import helper





# ------------------------------------------------------------------------
#    GLOBAL PATHS
# ------------------------------------------------------------------------
"""
addons_pipeline = "W:\\Blender_Pipeline\\Addons_Pipeline\\Addons\\"
addons_pipeline_third_party = "W:\\Blender_Pipeline\\Addons_Pipeline\\Addons_ThirdParty\\"

addon_path_dream_textures = "W:\\Blender_Pipeline\\Addons_Pipeline\\Addons_ThirdParty_Extra\\dream_textures\\"


ACES_path = "W:\\ACES_Blender\\config.ocio"
ACES_windows_set_env_batch = "W:\ACES_Blender\ACES_set_env_variable.bat"

baseStartupFolder = "W:\\Blender_Pipeline\\Assets\\Startup_Scene\\"

librariesRoot = "W:\\Blender_Asset_Library"

render_configs = "W:\\Blender_Pipeline\\Assets\\Configs\\render_configs.json"
texture_bake_presets = "W:\\Blender_Pipeline\\Assets\\SimpleBake_Presets"
"""

addons_pipeline = "D:\\Projects\\Blender_Pipeline\\Addons_Pipeline\\Addons\\"
addons_pipeline_third_party = "D:\\Projects\\Blender_Pipeline_02\\pipeline_assets\\addons\\Addons_Third_Party\\"

addon_path_dream_textures = "W:\\Blender_Pipeline\\Addons_Pipeline\\Addons_ThirdParty_Extra\\dream_textures\\"

ACES_path = "D:\\Projects\\Blender_Pipeline_02\\pipeline_assets\\ACES_Blender\\config.ocio"
ACES_windows_set_env_batch = 'D:\Projects\Blender_Pipeline_02\pipeline_assets\ACES_Blender\ACES_set_env_variable.bat'

baseStartupFolder = "D:\\Projects\\Blender_Pipeline\\Pipeline_Assets\\"

#librariesRoot = "D:\\Library\\Blender_Asset_Library"
librariesRoot = "D:\\Projects\\Blender_Pipeline_02\\asset_library"



render_configs = "D:\\Projects\\Blender_Pipeline\\Scripting\\json\\render_configs.json"
texture_bake_presets = "D:\\Projects\\Blender_Pipeline\\Pipeline_Assets\\bake_presets"




# ------------------------------------------------------------------------
#    USER PATHS
# ------------------------------------------------------------------------

user_path = bpy.utils.resource_path('USER')
config_path = os.path.join(user_path, "config\\")
addon_path = os.path.join(user_path, "scripts\\addons\\")











# ------------------------------------------------------------------------
#    PIPELINE INSTALLS
# ------------------------------------------------------------------------

#-------  Install Inhouse Magnet FX Blender Addons -------#
class MAGNETFX_OT_InstallPipelineAddons(bpy.types.Operator):
    """Setup Magnet FX Blender Addons"""
    bl_idname = "magnetfx.addons_setup"
    bl_label = "MFX - Install Magnet FX Addons"
    bl_options = {'INTERNAL'}


    def execute(self, context):

        #install third-party addons
        helper.install_addons_from_folder(addons_pipeline_third_party)

        #install inhouse addons
        #helper.install_addons_from_folder(addons_pipeline)
        
        #update all assets
        bpy.ops.magnetfx.update_asset_libraries()


        self.report({"INFO"}, "Magnet FX Addons installed")
        return {"FINISHED"}




#-------  Install Default Startup Scene -------#
class MAGNETFX_OT_StartupSceneSetup(bpy.types.Operator):
    """Setup Startup Scene"""
    bl_idname = "magnetfx.startup_scene_setup"
    bl_label = "MFX - Setup Startup Scene"
    bl_options = {'INTERNAL'}


    def execute(self, context):

        #TODO: get the current version of the user folder to install stuff indipendent from version - done
        #TODO: prompt if the startup file already exists, so the user can decide if he or she wants to really reinstall the base setup

        def RestartBlender():
            #restart blender
            py = os.path.join(os.path.dirname(__file__), "console_toggle.py")
            filepath = bpy.data.filepath

            if (filepath != ""):
                subprocess.Popen([sys.argv[0], filepath, '-P', py])
            else:
                subprocess.Popen([sys.argv[0],'-P', py])
            
            bpy.ops.wm.quit_blender()


        baseStartupFile = "startup.blend"
        filename = Path(config_path + baseStartupFile)

        if not filename.exists():
            print("No startup config file found. Installing base startup config and restarting Blender")
            shutil.copyfile(baseStartupFolder + baseStartupFile, config_path + baseStartupFile)
        else:
            print("Found startup file! Creating backup and installing base startup config")
            shutil.copyfile(config_path + baseStartupFile, config_path + "BACKUP_" + baseStartupFile)  
            shutil.copyfile(baseStartupFolder + baseStartupFile, config_path + baseStartupFile)

        RestartBlender()

        return {"FINISHED"}





# ------------------------------------------------------------------------
#    INSTALL DREAM TEXTURES ADDON (THIRD-PARTY)
# ------------------------------------------------------------------------

class MAGNETFX_OT_InstallDreamTexturesAddon(bpy.types.Operator):
    """Install Dream Textures Addon"""
    bl_idname = "magnetfx.install_dmream_textures_addon"
    bl_label = "Install Dream Textures Addon"
    bl_options = {'INTERNAL'}


    def execute(self, context):

        #install third-party addons
        helper.install_addons_from_folder(addon_path_dream_textures)

        modelPath = addon_path_dream_textures
        modelAddonPath = addon_path + "dream_textures\\stable_diffusion\\models\\ldm\\stable-diffusion-v1\\"
        modelFile = "model.ckpt"

        print("Copy model file to user folder")

        #copy model file to user addon folder
        shutil.copyfile(modelPath + modelFile, modelAddonPath + modelFile)

        #open readme
        os.startfile(addon_path_dream_textures + "readme.txt")

        self.report({"INFO"}, "Dream Textures Addon installed")
        return {"FINISHED"}





# ------------------------------------------------------------------------
#    OPEN RENDER CONFIG JSON
# ------------------------------------------------------------------------

class MAGNETFX_OT_OpenRenderConfig(bpy.types.Operator):
    """Open Render Config File"""
    bl_idname = "magnetfx.open_render_configs_file"
    bl_label = "Open Render Config File"
    bl_options = {'INTERNAL'}


    def execute(self, context):
        print("OPEN SETTINGS")
        #open readme
        os.startfile(render_configs)
        

        self.report({"INFO"}, "Open Render Config")
        return {"FINISHED"}





# ------------------------------------------------------------------------
#    INSTALL/UPDATE MAGNET FX ASSET LIBRARY
# ------------------------------------------------------------------------

class MAGNETFX_OT_UpdateAssetLibraries(bpy.types.Operator):
    """Update Magnet FX Asset Libraries"""
    bl_idname = "magnetfx.update_asset_libraries"
    bl_label = "MFX - Update Magnet FX Asset Libraries"


    def execute(self, context):

        def addonEnabledCheck(addon_name):
            enabledAddonsList = []

            for addon in bpy.context.preferences.addons:
                enabledAddonsList.append(addon.module)

            if addon_name in enabledAddonsList:
                return True
            else:
                return False

        installedAssetLibraries = []

        #get installed libraries
        for lib in bpy.context.preferences.filepaths.asset_libraries:
            installedAssetLibraries.append(lib.path)


        for path, subdirs, files in os.walk(librariesRoot):
            for file in files:
                if file.endswith(".blend"):
                    filePath = os.path.join(path, file)
                    libraryPath = os.path.split(filePath)[0]
                    
                    #add new asset libraries
                    if libraryPath not in installedAssetLibraries:
                        print("New asset library added: " + libraryPath)
                        bpy.ops.preferences.asset_library_add(directory = libraryPath)
                        installedAssetLibraries.append(libraryPath)


        #HDRI wizard refresh
        if addonEnabledCheck("hdri_wizard"):
            bpy.ops.hdriw.manage(mode="RESCAN")






        ####### Install/Update Bake Presets

        modelPath = addon_path_dream_textures
        #modelAddonPath = addon_path + "dream_textures\\stable_diffusion\\models\\ldm\\stable-diffusion-v1\\"
        #modelFile = "model.ckpt"

        print("Copy bake presets to user folder")

        bake_presets = os.listdir(texture_bake_presets)

        print(user_path)
        print(os.path.basename(user_path))

        user_bake_presets_path = os.path.split(user_path)[0] + "\\data\\SimpleBake\\"


        for file in os.listdir(texture_bake_presets):
            #print(bake_presets_path + "\\" + file)
            #print(user_bake_presets_path + file)
            shutil.copyfile(texture_bake_presets + "\\" + file, user_bake_presets_path + file)




     


        self.report({"INFO"}, "Magnet FX asset libraries updated")
        return {"FINISHED"}







# ------------------------------------------------------------------------
#    CONFIGURE ACES PROFILES VIA OCIO ENVIRONMENT VARIABLE
# ------------------------------------------------------------------------

class MAGNETFX_OT_SetupACES(bpy.types.Operator):
    """Setup ACES"""
    bl_idname = "magnetfx.aces_setup"
    bl_label = "MFX - Setup ACES color profiles"
    bl_options = {'INTERNAL'}


    def execute(self, context):
        
        def Setup_ACES():
            if not os.getenv("OCIO") == ACES_path:
                print("ACES is not set up")
                self.report({"INFO"}, "Configuring ACES color profiles. Restaring Blender.")

                if bpy.data.is_saved:
                    #save current file before restarting blender
                    bpy.ops.wm.save_mainfile()

                #set environment variable windows
                subprocess.call([ACES_windows_set_env_batch])
                
                #set blender's internal environment variable
                os.environ["OCIO"] = ACES_path
                
                #restart blender
                py = os.path.join(os.path.dirname(__file__), "console_toggle.py")
                filepath = bpy.data.filepath
                if (filepath != ""):
                    subprocess.Popen([sys.argv[0], filepath, '-P', py])
                else:
                    subprocess.Popen([sys.argv[0],'-P', py])
                bpy.ops.wm.quit_blender()
                
            else:
                self.report({"INFO"}, "ACES color profiles already configured")


        Setup_ACES()

        return {"FINISHED"}





classes = ([
        MAGNETFX_OT_InstallPipelineAddons,
        MAGNETFX_OT_StartupSceneSetup,
        MAGNETFX_OT_InstallDreamTexturesAddon,
        MAGNETFX_OT_OpenRenderConfig,
        MAGNETFX_OT_UpdateAssetLibraries,
        MAGNETFX_OT_SetupACES
        ])


def register():
    
    global classes
    for cls in classes:
        register_class(cls)


def unregister():
    global classes
    for cls in classes:
        unregister_class(cls)