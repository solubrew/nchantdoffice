# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
        docid:
        name:
        description: >
        version: 0.0.0.0.0.0
        authority: filesystem
        security: seclvl2
        <(WT)>: -32
"""

# -*- coding: utf-8 -*
# ======================================Standard Library Modules======================================================||
from os.path import abspath, dirname, join
import datetime as dt

# ======================================3rd Party Library Modules=====================================================||
from PySide6.QtWebEngineWidgets import QWebEngineView
from pythreejs import *
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtkmodules.vtkIOGeometry import vtkSTLReader
from vtkmodules.vtkRenderingCore import (
    vtkRenderer,
    vtkRenderWindow,
    vtkActor,
    vtkPolyDataMapper,
)
from vtkmodules.vtkCommonColor import vtkNamedColors
from pyqtgraph.opengl import GLViewWidget, GLMeshItem
from stl import mesh as stl_mesh  # Install with `pip install numpy-stl`
from pythreejs import (
    # STLLoader,
    PerspectiveCamera,
    Scene,
    MeshStandardMaterial,
)
from pythreejs import SpotLight, Mesh
import numpy as np
from stl import mesh  # From numpy-stl
from pythreejs import (
    BufferGeometry,
    BufferAttribute,
    PerspectiveCamera,
    Material,
    Mesh,
    Scene,
    DirectionalLight,
    AmbientLight,
    Renderer,
    OrbitControls,
)

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from kahndor.logma import Logma
from nchantrs.widgets.controls.toolbars import NchantdButtonBar

from nchantdoffice.widgets.documents.atnrg.browsers.browsers import NchantdOfficeWebBrowser
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument
from pyffice.cad.cad import PyfficeCADManager
import subprocess

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)
# pg.setConfigOption("debug", True)
# ====================================================================================================================||
pxcfg = join(here, "_data_", "cad.yaml")


class NchantdOfficeCAD(NchantdOfficeDocument):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        self.config = kahndor.Instruct(pxcfg).select("NchantdOfficeCAD")
        if self.parent:
            self.config.override(parent.config)
        super().__init__("Nchantd CAD", self)
        self.config.override(cfg)
        self.canvas = None
        self.shape_toolbar = None
        self.space = None
        self.document = None
        self.space_layout = None
        self.toolbar_layout = None

    def initModel(self):
        """"""
        super().initModel()
        self.document = PyfficeCADManager()
        return self

    def initView(self):
        """"""
        super().initView()
        cfg = {"layout": "horizontal", "justify": "right"}
        buttons = {0: "save", 1: "print", 2: "launch_toolbox", 3: "cancel"}
        self.button_bar = NchantdButtonBar(self, cfg).initWidget(buttons)
        self.layout.addWidget(self.button_bar)
        # 3D Viewer using pyqtgraph's OpenGL GLViewWidget
        # render_type = "pyqtgraph"
        # render_type = "pythreejs"
        render_type = "vtk"
        if render_type == "pyqtgraph":
            self.view = GLViewWidget()
            self.view.setCameraPosition(distance=50)
            self.view.setSizePolicy(2, 2)
            self.view.setBackgroundColor("white")
            self.view.setMinimumSize(800, 600)
            self.layout.addWidget(self.view)
            self.load_openscad_object()
            self.view.show()
        elif render_type == "vtk":
            self.view = QVTKRenderWindowInteractor(self)

            self.renderer = vtkRenderer()
            self.colors = vtkNamedColors()
            self.renderer.SetBackground(self.colors.GetColor3d("White"))  # Set background color to black

            # Add the renderer to the render window
            self.view.GetRenderWindow().AddRenderer(self.renderer)
            self.interactor = self.view.GetRenderWindow().GetInteractor()
            self.load_stl_file()
            self.view.show()
            self.layout.addWidget(self.view)

        elif render_type == "pythreejs":
            cfg = {}
            self.browser = NchantdOfficeWebBrowser(self, cfg).initWidget()
            self.layout.addWidget(self.browser)
            # self.load_and_render_stl()
            # self.load_stl()
            self.render_stl_to_html()

        #        cfg = {}
        #        self.space = NchantdSpace(self, cfg).initWidget()
        #        self.space_layout.addWidget(self.space)
        #        self.layout.addLayout(self.space_layout)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def load_and_render_stl(self):
        """Open an STL file and render it using pythreejs in an HTML view."""
        stl_file = join(here, "_data_", "output.stl")
        if stl_file:
            # Generate HTML for STL rendering
            self.stl_html = self.render_stl_to_html(stl_file)
            # Set the HTML content in the web engine view
            self.web_view.setHtml(self.stl_html)

    def load_openscad_object(self):
        # Open file dialog to load an OpenSCAD file
        # file_dialog = QFileDialog()
        # file_path, _ = file_dialog.getOpenFileName(self, "Open OpenSCAD File", "", "OpenSCAD Files (*.scad)")
        file_path = join(here, "_data_", "test.scad")
        if file_path:
            # Render the OpenSCAD file to an STL file
            stl_file = join(here, "_data_", "output.stl")
            self.render_openscad_to_stl(file_path, stl_file)
            # Load the STL file into a 3D mesh and display it
            self.display_stl(stl_file)
            # Clean up temporary STL file
            # os.remove(stl_file)

    def load_stl(self):
        """
        Load an STL file and return its geometry for use in pythreejs.
        """
        file_path = join(here, "_data_", "output.stl")
        # Load the STL file
        stl_mesh = mesh.Mesh.from_file(file_path)

        # Extract vertices and faces
        vertices = np.array(stl_mesh.vectors).reshape(-1, 3)  # Vertex positions
        faces = np.arange(len(vertices))  # Generate indices automatically

        # Create geometry
        geometry = BufferGeometry(
            attributes={
                "position": BufferAttribute(vertices, normalized=False),
            }
        )
        return geometry

    def load_stl_file(self):
        """Open a dialog to load an STL file and render it."""
        stl_file = join(here, "_data_", "output.stl")
        if stl_file:
            # Read the STL file
            stl_reader = vtkSTLReader()
            stl_reader.SetFileName(stl_file)

            # Set up a mapper
            mapper = vtkPolyDataMapper()
            mapper.SetInputConnection(stl_reader.GetOutputPort())

            # Set up an actor (3D object)
            actor = vtkActor()
            actor.SetMapper(mapper)

            # Assign a color to the STL model
            actor.GetProperty().SetColor(self.colors.GetColor3d("Orange"))

            # Clear current objects in the renderer and add the actor
            self.renderer.RemoveAllViewProps()
            self.renderer.AddActor(actor)

            # Reset the camera to fit the newly loaded STL model
            self.renderer.ResetCamera()

            # Start or render the window
            self.view.GetRenderWindow().Render()

    def render_openscad_to_stl(self, scad_file_path, output_stl_path):
        """Use OpenSCAD to render a scad file into an STL file."""
        try:
            # Call OpenSCAD from the command line to render the .scad file
            command = ["openscad", "-o", output_stl_path, scad_file_path]
            subprocess.check_call(command)
        except FileNotFoundError:
            print("Make sure OpenSCAD is installed and added to your PATH.")
        except subprocess.CalledProcessError as e:
            print(f"OpenSCAD rendering failed: {e}")

    def display_stl(self, stl_file_path):
        """Load and display the STL file in the GLViewWidget."""
        # Read the STL file using NumPy-STL
        stl_mesh_data = stl_mesh.Mesh.from_file(stl_file_path)

        # Extract vertex and face data
        vertices = stl_mesh_data.vectors.reshape(-1, 3)
        faces = []

        # Create face indices (required for GLMeshItem)
        for i in range(0, len(vertices), 3):
            faces.append([i, i + 1, i + 2])

        # Create a GLMeshItem for rendering
        mesh_item = GLMeshItem(
            vertexes=vertices,
            faces=faces,
            shader="shaded",
            smooth=True,
            color=(1, 0, 0, 1),
        )

        # Clear the GLViewWidget and add the new mesh
        self.view.clear()
        self.view.addItem(mesh_item)

    def render_stl_to_html(self):  # , file_path):
        """Render STL to an HTML string using pythreejs."""
        # # Load STL data
        # with open(file_path, "rb") as f:
        #     stl_loader = STLLoader()
        #     stl_data = stl_loader.load(f)

        stl_data = self.load_stl()

        # Create a material for rendering the STL
        material = MeshStandardMaterial(color="orange", metalness=0.5, roughness=0.7)

        # Create a mesh from the geometry and material
        stl_mesh = Mesh(geometry=stl_data, material=material, position=[0, 0, 0])

        # Set up the scene
        scene = Scene(
            children=[
                stl_mesh,
                DirectionalLight(color="white", intensity=0.8, position=[5, 5, 5]),
                AmbientLight(color="white", intensity=0.5),
            ]
        )

        # Camera
        camera = PerspectiveCamera(position=[15, 15, 15], up=[0, 0, 1])
        camera.lookAt([0, 0, 0])
        # Controls (Rotation, Zoom, Pan)
        controls = OrbitControls(controlling=camera)
        # Renderer
        renderer = Renderer(camera=camera, scene=scene, controls=[controls], width=800, height=600)

        # Convert the Renderer to an HTML element
        return renderer.to_html()


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
