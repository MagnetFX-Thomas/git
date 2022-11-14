# ------------------------------------------------------------------------
#    MAGNET FX RENDER LAYER SETUP
# ------------------------------------------------------------------------
        

        #--------------------
        #### TODO ####

        # floor reflection layer workaround
        # create floor with correct shader  --  or do another script for default light, floor, cam?
        # default cam setup for 0,0,0?
        # add shadow catcher pass


from bpy.utils import register_class, unregister_class

import bpy
import os


#materialLibrary = "W:\\Blender_Asset_Library\\Materials\\MaterialLibrary.blend"

materialLibrary = "D:\\Projects\\Blender_Pipeline_02\\asset_library\\Materials\\MaterialLibrary.blend"




# ------------------------------------------------------------------------
#    CREATE RENDER LAYER OPERATOR
# ------------------------------------------------------------------------

class MAGNETFX_OT_create_render_setup(bpy.types.Operator):
    """Create automatic render setup"""
    bl_idname = "magnetfx.create_render_layer"
    bl_label = "Create Render Layer"
    bl_options = {"REGISTER", "UNDO"}



    # ------------------------------------------------------------------------
    #    Class Properties
    # ------------------------------------------------------------------------
    
    createViewLayerProduct: bpy.props.BoolProperty(
        name = "Product Render Layer",
        default = True,
    )

    createViewLayerProductAO: bpy.props.BoolProperty(
        name = "Product AO Render Layer",
        default = True,
    )

    createViewLayerFloorShadowAO: bpy.props.BoolProperty(
        name = "Floor Shadow AO Render Layer",
        default = True,
    )

    createViewLayerFloorReflection: bpy.props.BoolProperty(
        name = "Floor Reflection Render Layer",
        default = False,
    )

    createFloor: bpy.props.BoolProperty(
        name = "Create Floor",
        default = True,
    )





    def execute(self, context):

        # ------------------------------------------------------------------------
        #    Scene Data
        # ------------------------------------------------------------------------

        currentScene = bpy.context.window.scene.name

        # ------------------------------------------------------------------------
        #    View Layer Functions
        # ------------------------------------------------------------------------

        def CreateViewLayer(name):   

            viewLayerExists = False
            
            #check if view layer already exists
            viewLayer_list = bpy.data.scenes[currentScene].view_layers
            
            for layer in viewLayer_list:
                if layer.name == name:
                    viewLayerExists = True
            
            #create view layer
            if not viewLayerExists:
                new_view_layer = bpy.ops.scene.view_layer_add(type = "NEW")
                bpy.context.view_layer.name = name
                bpy.data.scenes[currentScene].view_layers[name].use_pass_z = True
                bpy.context.view_layer.cycles.denoising_store_passes = True
        
        

        def removeViewLayer(viewLayerName):
            for vl in bpy.context.scene.view_layers:
                if vl.name == viewLayerName:
                    bpy.context.scene.view_layers.remove(vl)
        
        
        
        
        
        # ------------------------------------------------------------------------
        #    Collection Functions
        # ------------------------------------------------------------------------
        
        def linkToNewCollection(object, collection):
            #TODO: What if an object is linked to more than one collection?
            try:
                currentCollection = object.users_collection[0]
                collection.objects.link(object)
                currentCollection.objects.unlink(object)          
            except:
                pass




        def CreateCollection(name):
            
            #get collections in scene
            collectionList = bpy.data.collections
            collectionListNames = []
            
            for collection in collectionList:
                collectionListNames.append(collection.name)
            
            #if collection is not in scene yet, create and link it
            if name not in collectionListNames:
                #print("Collection " + name + " needed")
                
                new_collection = bpy.data.collections.new(name)

                #link new collection to scene collection as child
                bpy.context.scene.collection.children.link(new_collection)
                print("Collection " + name + " created")
            
        

        # ------------------------------------------------------------------------
        #    Append Asset Function
        # ------------------------------------------------------------------------

        def appendItem_override(filepath, innerPath, itemName):
            #innerPath = "Collection"
            
            bpy.ops.wm.append(
            filepath = os.path.join(filepath, innerPath, itemName),
            directory = os.path.join(filepath, innerPath),
            filename = itemName, 
            do_reuse_local_id = True
            )


        def SetCollectionRenderOptions(collection_name, type):
            
            def traverse_tree(t):
                yield t
                for child in t.children:
                    yield from traverse_tree(child)

            #get master layer collection
            layer_coll_master = bpy.context.view_layer.layer_collection

            #search for the matching layer collection for the current active view layer and set render flags
            for layer_coll in traverse_tree(layer_coll_master):
                if layer_coll.collection.name == collection_name:
                    
                    if type == "exclude":
                        layer_coll.exclude = True
                        break
                    elif type == "indirect_only":
                        layer_coll.indirect_only = True
                        break
                    elif type == "holdout":
                        layer_coll.holdout = True
                        break
                    else:
                        print("Unkown argument in SetCollectionRenderOptions()")
                        break


        # ------------------------------------------------------------------------
        #    Material Functions
        # ------------------------------------------------------------------------

        def CreateMaterial_Basic(name):
                new_material = bpy.data.materials.new(name = name)
                new_material.use_nodes = True
                
                


        def CreateMaterial_AO():           
            #create material
            new_material = bpy.data.materials.new(name = "Ambient_Occlusion_Pipeline")
            new_material.use_nodes = True

            #shortcut
            new_material_nodes = new_material.node_tree.nodes

            #delete Principled BSDF node
            new_material.node_tree.nodes.remove(new_material.node_tree.nodes["Principled BSDF"])

            #create shader nodes and set default values
            material_output = new_material_nodes.get("Material Output")
            node_emission = new_material_nodes.new(type="ShaderNodeEmission")
            node_ambient_occlusion = new_material_nodes.new(type="ShaderNodeAmbientOcclusion")
            node_ambient_occlusion.samples = 64
            node_bright_contrast = new_material_nodes.new(type = "ShaderNodeBrightContrast")
            node_bright_contrast.inputs[1].default_value = 1.0
            node_bright_contrast.inputs[2].default_value = 1.5

            #link nodes
            #shortcut
            materialLinks = new_material.node_tree.links

            materialLinks.new(node_emission.outputs[0], material_output.inputs[0])
            materialLinks.new(node_ambient_occlusion.outputs[1], node_emission.inputs[1])
            materialLinks.new(node_ambient_occlusion.outputs[0], node_bright_contrast.inputs[0])
            materialLinks.new(node_bright_contrast.outputs[0], node_emission.inputs[0])
            
            return new_material





        # ------------------------------------------------------------------------
        #    Create Floor
        # ------------------------------------------------------------------------
        def CreateFloor():
            
            #check if floor exists
            floorExists = bpy.context.scene.objects.get("Floor")
            
            if floorExists:
                print ("Floor already in scene")
                selectedObject = bpy.context.scene.objects.get("Floor")
            else:
                bpy.ops.mesh.primitive_plane_add(size = 100, calc_uvs = True, enter_editmode = False, align = 'WORLD', location = (0, 0, 0), rotation = (0, 0, 0), scale = (0, 0, 0))
                selectedObject = bpy.context.active_object
                selectedObject.name = "Floor"
                
            #link floor to Environment collection
            linkToNewCollection(selectedObject, bpy.data.collections['Environment'])





        # ------------------------------------------------------------------------
        #    MAIN OPERATOR
        # ------------------------------------------------------------------------

        #create collections for product renderings
        CreateCollection("Product")
        CreateCollection("Environment")
        CreateCollection("Cams")
        CreateCollection("Lighting")




        #sort cams and lights into designated collections
        cameraList = [obj for obj in list(bpy.context.scene.objects) if obj.type == "CAMERA"]
        for object in cameraList:
            #print(object)
            linkToNewCollection(object, bpy.data.collections['Cams'])
        

        lightList = [obj for obj in list(bpy.context.scene.objects) if obj.type == "LIGHT"]
        for object in lightList:
            #print(object)
            linkToNewCollection(object, bpy.data.collections['Lighting'])




        #rename default view layer to "Master"
        try:
            bpy.data.scenes[currentScene].view_layers['ViewLayer']
            bpy.data.scenes[currentScene].view_layers['ViewLayer'].name = "Master"
        except:
            pass





        # ------------------------------------------------------------------------
        #    VIEW LAYER CREATION
        # ------------------------------------------------------------------------

        #-------  create view layer - PRODUCT -------#
        if self.createViewLayerProduct:
            CreateViewLayer("Product")
            bpy.context.window.view_layer = bpy.context.scene.view_layers['Product']
            #SetCollectionRenderOptions("Environment", "indirect_only")
            SetCollectionRenderOptions("Environment", "exclude")
            #SetCollectionRenderOptions("Product", "exclude")
        else:
            removeViewLayer("Product")




        #-------  create view layer - PRODUCT_AO -------#
        if self.createViewLayerProductAO:
            CreateViewLayer("Product_AO")
            bpy.context.window.view_layer = bpy.context.scene.view_layers['Product_AO']
            SetCollectionRenderOptions("Environment", "indirect_only")
            SetCollectionRenderOptions("Lighting", "exclude")


            AO_shader_exists = bpy.data.materials.get("Ambient_Occlusion_Pipeline")

            if AO_shader_exists:
                #assign existing one as override
                bpy.data.scenes[currentScene].view_layers['Product_AO'].material_override = bpy.data.materials.get("Ambient_Occlusion_Pipeline")
            else:
                #create AO shader and set layer override
                bpy.data.scenes[currentScene].view_layers['Product_AO'].material_override = CreateMaterial_AO()
        else:
            removeViewLayer("Product_AO")




        #-------  create view layer - FLOOR_SHADOW_AO -------#
        if self.createViewLayerFloorShadowAO:
            CreateViewLayer("Floor_Shadow_AO")
            bpy.context.window.view_layer = bpy.context.scene.view_layers['Floor_Shadow_AO']
            SetCollectionRenderOptions("Product", "indirect_only")
            SetCollectionRenderOptions("Lighting", "exclude")

            AO_shadow_shader_exists = bpy.data.materials.get("KB_AO_Ground")

            if AO_shadow_shader_exists:
                #assign existing one as override
                bpy.data.scenes[currentScene].view_layers['Floor_Shadow_AO'].material_override = bpy.data.materials.get("KB_AO_Ground")
            else:
                #create AO shader and set layer override
                appendItem_override(materialLibrary, "Material", "KB_AO_Ground")
                bpy.data.scenes[currentScene].view_layers['Floor_Shadow_AO'].material_override = bpy.data.materials.get("KB_AO_Ground")

        else:
            removeViewLayer("Floor_Shadow_AO")




        #-------  create view layer - FLOOR_REFLECTION -------#
        if self.createViewLayerFloorReflection:
            CreateViewLayer("Floor_Reflection")
            bpy.context.window.view_layer = bpy.context.scene.view_layers['Floor_Reflection']
            SetCollectionRenderOptions("Product", "indirect_only")
        
        else:
            removeViewLayer("Floor_Reflection")





        # ------------------------------------------------------------------------
        #    FLOOR CREATION
        # ------------------------------------------------------------------------

        #create floor with a base material
        if self.createFloor:
            CreateFloor()

            #create and assign base floor material
            floor_shader_exists = bpy.data.materials.get("floor_material")

            #check if floor_materials basic shader exists in this scene
            if not floor_shader_exists:
                CreateMaterial_Basic("floor_material")

            #check if floor has no material slot >> add slow and assign material
            if len(bpy.data.objects['Floor'].data.materials) < 1:
                bpy.data.objects['Floor'].data.materials.append(bpy.data.materials.get("floor_material"))







        #switch to master layer
        bpy.context.window.view_layer = bpy.context.scene.view_layers["Master"]

                
        return {"FINISHED"}






classes = ([
        MAGNETFX_OT_create_render_setup
        ])



def register():
    
    global classes
    for cls in classes:
        register_class(cls)

def unregister():
    global classes
    for cls in classes:
        unregister_class(cls)