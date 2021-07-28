import bpy
from src.main.Module import Module
from src.mitsuba_export.export import MitsubaFileExport


from bpy.types import Operator, AddonPreferences
from bpy.props import StringProperty, BoolProperty
import os
import sys

from src.mitsuba_export.file_api import FileExportContext, Files
from src.mitsuba_export.materials import export_world
from src.mitsuba_export.geometry import GeometryExporter
from src.mitsuba_export.lights import export_light
from src.mitsuba_export.camera import export_camera

from bpy_extras.io_utils import ExportHelper, axis_conversion, orientation_helper

import mitsuba
mitsuba.set_variant('scalar_spectral_polarized')


# added class to export the files as a .blend file
class MitsubaExporter():
    def __init__(self):
        self.reset()
        self.prefs = bpy.path.abspath("/home/ubuntu/mitsuba2/build")
        self.set_path(self.prefs)

    def reset(self):
        self.export_ctx = FileExportContext()
        self.geometry_exporter = GeometryExporter()

    def set_path(self, mts_build):
        '''
        Set the different variables necessary to run the addon properly.
        Add the path to mitsuba binaries to the PATH env var.
        Append the path to the python libs to sys.path

        Params
        ------

        mts_build: Path to mitsuba 2 build folder.
        '''
        os.environ['PATH'] += os.pathsep + os.path.join(mts_build, 'dist')
        sys.path.append(os.path.join(mts_build, 'dist', 'python'))

    def run(self):
        # run the export of files
        # Conversion matrix to shift the "Up" Vector. This can be useful when exporting single objects to an existing mitsuba scene.
        axis_mat = axis_conversion(
            to_forward=self.axis_forward,
            to_up=self.axis_up,
        ).to_4x4()
        self.export_ctx.axis_mat = axis_mat
        self.export_ctx.export_ids = self.export_ids
        self.export_ctx.set_filename(self.filepath, split_files=self.split_files)

        # Switch to object mode before exporting stuff, so everything is defined properly
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT')

        #scene integrator
        integrator = {
            'type': 'path',
            'max_depth': context.scene.cycles.max_bounces
        }
        self.export_ctx.data_add(integrator)

class ObjWriter(Module):

    def __init__(self, config):
        Module.__init__(self, config)

    def run(self):
        blend_path = self.config.get_string("path")
        bpy.ops.wm.save_as_mainfile(filepath=blend_path)

        exporter = MitsubaExporter()