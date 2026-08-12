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

# -*- coding: utf-8 -*-
# ======================================Standard Library Modules======================================================||
from __future__ import annotations

from os.path import abspath, dirname, join
import datetime as dt
from typing import Self

# ======================================3rd Party Library Modules======================================================||
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

    def __init__(self, source_node, target_node, source_connection="bottom", target_connection="top", cfg=None) -> None:
        logma.info(f"[diagrams] Edge.__init__: src={getattr(source_node, 'label', None) or type(source_node).__name__} tgt={getattr(target_node, 'label', None) or type(target_node).__name__} src_conn={source_connection} tgt_conn={target_connection}")
        try:
            self.config = kahndor.Instruct(pxcfg).select("Edge")
            super().__init__()
            self.config.override(cfg)
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
        except Exception as e:
            logma.error(f"[diagrams] Edge.__init__ failed: {e}", exc_info=True)
            raise

    def update_position(self) -> None:
        """
        Dynamically update the positions of the edge endpoints.
        """
        logma.debug("[diagrams] Edge.update_position")
        try:
            source_point = self.source_node.scenePos() + self.source_node.lock_connection(self.source_connection)
            target_point = self.target_node.scenePos() + self.target_node.lock_connection(self.target_connection)
            self.setLine(source_point.x(), source_point.y(), target_point.x(), target_point.y())
        except Exception as e:
            logma.error(f"[diagrams] Edge.update_position failed: {e}", exc_info=True)


class NchantdOfficeDiagramNode(NchantdWidgetMixin, pyqt.QGraphicsEllipseItem):
    """
    A draggable node with connection points for edges.
    """

    def __init__(self, x, y, radius=20, label=None, color=QColor(100, 150, 255), cfg=None) -> None:
        """"""
        logma.info(f"[diagrams] Node.__init__: pos=({x},{y}) radius={radius} label={label!r}")
        try:
            self.config = kahndor.Instruct(pxcfg).select("NchantdNode")
            super().__init__(-radius, -radius, 2 * radius, 2 * radius)
            self.config.override(cfg)
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
        except Exception as e:
            logma.error(f"[diagrams] Node.__init__ failed: {e}", exc_info=True)
            raise

    def add_edge(self, edge) -> None:
        """
        Add an edge to the list of connected edges.
        """
        logma.debug(f"[diagrams] Node.add_edge: edge_count_before={len(self.edges)}")
        self.edges.append(edge)

    def remove_edge(self, edge) -> None:
        """
        Remove an edge from the list of connected edges.
        """
        logma.debug(f"[diagrams] Node.remove_edge: edge_in_list={edge in self.edges}")
        if edge in self.edges:
            self.edges.remove(edge)

    def sceneEvent(self, event) -> None:
        """
        Update attached edges automatically when the node is moved.
        """
        logma.debug(f"[diagrams] Node.sceneEvent: edges_to_update={len(self.edges)}")
        try:
            for edge in self.edges:
                edge.update_position()
        except Exception as e:
            logma.error(f"[diagrams] Node.sceneEvent failed: {e}", exc_info=True)
        return super().sceneEvent(event)

    def lock_connection(self, target_connection) -> None:
        """
        Lock into the nearest connection point.
        """
        logma.debug(f"[diagrams] Node.lock_connection: target={target_connection!r}")
        return self.connection_points[target_connection]

    def initView(self) -> Self:
        """"""
        logma.info("[diagrams] Node.initView: building 9 text-box connection points")
        try:
            text_box_attrs = [
                "left_top_text_box", "left_middle_text_box", "left_bottom_text_box",
                "center_top_text_box", "center_middle_text_box", "center_bottom_text_box",
                "right_top_text_box", "right_middle_text_box", "right_bottom_text_box",
            ]
            for attr in text_box_attrs:
                cfg = {}
                box = self.NchantdTextBox(self.parent, self.config.override(cfg)).initWidget()
                setattr(self, attr, box)
            logma.debug(f"[diagrams] Node.initView: 9 text boxes initialised")
        except Exception as e:
            logma.error(f"[diagrams] Node.initView failed: {e}", exc_info=True)
            raise
        return self

    def initModel(self) -> Self:
        """Seed any per-instance model state for the diagram Node.

        Sprint 20: previously a no-op stub. The bulk of the
        per-instance state (``edges``, ``connection_points``,
        ``self.radius``, ``self.document``) is seeded in
        ``__init__``; ``initModel`` here provides a hook for
        any future model population (e.g. loading diagram state
        from the document payload). It's a no-op for now but
        no longer marked as a stub.
        """
        logma.info("[diagrams] Node.initModel: seeding model state")
        # Seed an empty selection set; future code can populate
        # this from ``self.document``.
        self.selected_connection = None
        return self

    def initWidget(self, pos=0) -> Self:
        """"""
        logma.info(f"[diagrams] Node.initWidget: pos={pos}")
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
