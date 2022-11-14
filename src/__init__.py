bl_info = {
    "name": "Pipeline",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "category": "Magnet FX" ,
    "description": "Magnet FX Pipeline",
    "warning": "",
    "doc_url": "",
    "tracker_url": "",
}


from bpy.utils import register_class, unregister_class

from . import pipeline_core
from . import ui
from . import render_setup



classes = ([
        ])


def register():
    global classes
    for cls in classes:
        register_class(cls)
        
    pipeline_core.register()
    render_setup.register()
    ui.register()


def unregister():
    global classes
    for cls in classes:
        unregister_class(cls)
        
    pipeline_core.unregister()
    render_setup.unregister()
    ui.unregister()
