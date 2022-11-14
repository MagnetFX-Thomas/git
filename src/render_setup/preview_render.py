import bpy
from bpy.utils import register_class, unregister_class
import math





# ------------------------------------------------------------------------
#    CREATE PREVIEW ANIMATION OPERATOR
# ------------------------------------------------------------------------

class MAGNETFXOT_AddPreviewKeys(bpy.types.Operator):
    """Create Preview Animation"""
    bl_idname = "magnetfx.create_preview_animation"
    bl_label = "Create Preview Keys on Selection"
    bl_options = {'INTERNAL'}


    def execute(self, context):

        #TODO: check if the selection is valid? (no cam or light)


        def setKeysPreviews_allSides(axis, degree, frame):
            bpy.context.active_object.rotation_euler[axis] = math.radians(degree)
            bpy.context.active_object.keyframe_insert(data_path ="rotation_euler",frame = frame)
            
            #revert
            bpy.context.active_object.rotation_euler[axis] = math.radians(0)


        product_selection = bpy.context.selected_objects

        if not product_selection:
            self.report({"ERROR"}, "Select the product first and then run the automation again")
            return {"CANCELLED"}

        #default rotation - set key - frame 1
        bpy.context.active_object.keyframe_insert(data_path ="rotation_euler",frame = 1)

        #preview rotation
        setKeysPreviews_allSides(2, 180, 2)
        setKeysPreviews_allSides(1, 90, 3)
        setKeysPreviews_allSides(1, -90, 4)

        bpy.context.scene.frame_set(1)

        #set frame range for rendering in scene
        bpy.context.scene.frame_start = 1
        bpy.context.scene.frame_end = 4


        self.report({"INFO"}, "Preview keys added to selection")
        return {"FINISHED"}





# ------------------------------------------------------------------------
#    REMOVE PREVIEW ANIMATION OPERATOR
# ------------------------------------------------------------------------

class MAGNETFXOT_RemoveAnimation(bpy.types.Operator):
    """Remove Animation"""
    bl_idname = "magnetfx.remove_animation"
    bl_label = "Remove All Keys from Selection"
    bl_options = {'INTERNAL'}


    def execute(self, context):

        def removeAnimation(obj):
            obj.animation_data_clear()


        bpy.context.scene.frame_set(1)
        removeAnimation(bpy.context.active_object)

        #set frame start and end to 1 for stills
        bpy.context.scene.frame_start = 1
        bpy.context.scene.frame_end = 1
        

        self.report({"INFO"}, "Animation was deleted from selected object")
        return {"FINISHED"}





classes = ([
        MAGNETFXOT_AddPreviewKeys,
        MAGNETFXOT_RemoveAnimation
        ])



def register():
    
    global classes
    for cls in classes:
        register_class(cls)



def unregister():
    global classes
    for cls in classes:
        unregister_class(cls)