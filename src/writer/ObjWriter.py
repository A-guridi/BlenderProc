
import bpy
from src.main.Module import Module


# added class to export the files as a .blend file
class ObjWriter(Module):

    def __init__(self, config):
        Module.__init__(self, config)

    def run(self):
        bpy.ops.wm.save_as_mainfile(filepath=self.config.get_string("path"))
