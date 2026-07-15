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
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsEllipseItem,
    QGraphicsLineItem,
    QGraphicsTextItem,
    QGraphicsItem,
)
from PySide6.QtGui import QPen, QBrush, QColor
from PySide6.QtCore import Qt, QPointF

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from kahndor.logma import Logma
from nchantrs.libraries import pyqt
from nchantrs.widgets.canvases import NchantdCanvas
from nchantrs.widgets.controls.toolbars import NchantdButtonBar
from nchantrs.widgets.widgets import NchantdWidget, NchantdWidgetMixin
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument
from pyffice.diagrams.diagrams import PyfficeNode, PyfficeEdge

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "diagrams.yaml")


class NchantdOfficeDiagramEdge(NchantdWidgetMixin, pyqt.QGraphicsLineItem):
    """
    Represents a line connecting two nodes, with locking connection points.
    """

    def __init__(self, source_node, target_node, source_connection="bottom", target_connection="top", cfg=None):
        super().__init__()
        self.init_variables()
        self.config = kahndor.Instruct(pxcfg).select("NchantdOfficeDiagramEdge").override(cfg)
        self.source_node = source_node
        self.target_node = target_node
        self.source_connection = source_connection
        self.target_connection = target_connection
        self.setPen(pyqt.QPen(pyqt.black, 2))  # Black line with 2px width

        # Register this edge with the nodes
        self.source_node.add_edge(self)
        self.target_node.add_edge(self)

        # Initial update of the line position
        self.update_position()

    def update_position(self):
        """
        Dynamically update the positions of the edge endpoints.
        """
        source_point = self.source_node.scenePos() + self.source_node.lock_connection(self.source_connection)
        target_point = self.target_node.scenePos() + self.target_node.lock_connection(self.target_connection)
        self.setLine(source_point.x(), source_point.y(), target_point.x(), target_point.y())


class NchantdOfficeDiagramNode(NchantdWidgetMixin, pyqt.QGraphicsEllipseItem):
    """
    A draggable node with connection points for edges.
    """

    def __init__(self, x, y, radius=20, label=None, color=QColor(100, 150, 255), cfg=None):
        """"""
        super().__init__(-radius, -radius, 2 * radius, 2 * radius)
        self.init_variables()
        self.config = kahndor.Instruct(pxcfg).select("NchantdOfficeDiagramNode").override(cfg)
        self.document = PyfficeNode()
        self.radius = radius
        self.setBrush(pyqt.QBrush(color))
        self.setPen(pyqt.QPen(pyqt.black))
        self.setFlag(pyqt.QGraphicsItem.ItemIsMovable)  # Allow dragging
        self.setFlag(pyqt.QGraphicsItem.ItemSendsScenePositionChanges)  # Notify movement
        self.edges = []  # Store edges connected to this node
        self.setPos(x, y)
        if label:
            self.label = pyqt.QGraphicsTextItem(label, parent=self)
            self.label.setPos(-radius / 2, radius)

        # Define connection points (top, right, bottom, left)
        self.connection_points = {
            "top": pyqt.QPointF(0, -radius),
            "right": pyqt.QPointF(radius, 0),
            "bottom": pyqt.QPointF(0, radius),
            "left": pyqt.QPointF(-radius, 0),
        }
        self.left_top_text_box = None
        self.left_middle_text_box = None
        self.left_bottom_text_box = None
        self.center_top_text_box = None
        self.center_middle_text_box = None
        self.center_bottom_text_box = None
        self.right_top_text_box = None
        self.right_middle_text_box = None
        self.right_bottom_text_box = None

    def add_edge(self, edge):
        """
        Add an edge to the list of connected edges.
        """
        self.edges.append(edge)

    def remove_edge(self, edge):
        """
        Remove an edge from the list of connected edges.
        """
        if edge in self.edges:
            self.edges.remove(edge)

    def sceneEvent(self, event):
        """
        Update attached edges automatically when the node is moved.
        """
        for edge in self.edges:
            edge.update_position()
        return super().sceneEvent(event)

    def lock_connection(self, target_connection):
        """
        Lock into the nearest connection point.
        """
        return self.connection_points[target_connection]

    def initView(self):
        """"""
        cfg = {}
        self.left_top_text_box = self.NchantdTextBox(self.parent, self.config.override(cfg)).initWidget()
        cfg = {}
        self.left_middle_text_box = self.NchantdTextBox(self.parent, self.config.override(cfg)).initWidget()
        cfg = {}
        self.left_bottom_text_box = self.NchantdTextBox(self.parent, self.config.override(cfg)).initWidget()
        cfg = {}
        self.center_top_text_box = self.NchantdTextBox(self.parent, self.config.override(cfg)).initWidget()
        cfg = {}
        self.center_middle_text_box = self.NchantdTextBox(self.parent, self.config.override(cfg)).initWidget()
        cfg = {}
        self.center_bottom_text_box = self.NchantdTextBox(self.parent, self.config.override(cfg)).initWidget()
        cfg = {}
        self.right_top_text_box = self.NchantdTextBox(self.parent, self.config.override(cfg)).initWidget()
        cfg = {}
        self.right_middle_text_box = self.NchantdTextBox(self.parent, self.config.override(cfg)).initWidget()
        cfg = {}
        self.right_bottom_text_box = self.NchantdTextBox(self.parent, self.config.override(cfg)).initWidget()
        return self

    def initModel(self):
        """"""
        return self

    def initWidget(self, pos=0):
        """"""
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
