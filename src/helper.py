import bpy
import os
import zipfile

# ------------------------------------------------------------------------
#    INSTALL ADDONS FROM FOLDER
# ------------------------------------------------------------------------

def install_addons_from_folder(addonsFolderPath):

    addonsFileList = os.listdir(addonsFolderPath)

    #get addon name for Blender
    for addonFile in addonsFileList:
        if addonFile.endswith(".py"):
            addonName = os.path.splitext(addonFile)[0]

        elif addonFile.endswith(".zip"):
            addonZip = zipfile.ZipFile(addonsFolderPath + addonFile)
            zip_fileList = addonZip.namelist()
            addonName = zip_fileList[0].split('/')[0]
            

        bpy.ops.preferences.addon_install(filepath = addonsFolderPath + addonFile)
        bpy.ops.preferences.addon_enable(module = addonName)





# ------------------------------------------------------------------------
#    CHECK NODE EXISTS
# ------------------------------------------------------------------------

def check_node_exists(node_name):
    try:
        bpy.context.scene.node_tree.nodes[node_name]
        return True
    except:
        return False




# ------------------------------------------------------------------------
#    APPEND ITEM
# ------------------------------------------------------------------------
def append_item(filepath, innerPath, itemName, override: bool):
    #innerPath = "Collection"
    
    bpy.ops.wm.append(
    filepath = os.path.join(filepath, innerPath, itemName),
    directory = os.path.join(filepath, innerPath),
    filename = itemName,
    do_reuse_local_id = override
    )





    







# ------------------------------------------------------------------------
#    CREATE COLLECTION
# ------------------------------------------------------------------------

def create_collection(name):
            
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
#    LINK OBJECT TO NEW COLLECTION
# ------------------------------------------------------------------------
        
def link_object_to_collection(object, collection):
    #TODO: What if an object is linked to more than one collection?
    try:
        currentCollection = object.users_collection[0]
        collection.objects.link(object)
        currentCollection.objects.unlink(object)          
    except:
        pass