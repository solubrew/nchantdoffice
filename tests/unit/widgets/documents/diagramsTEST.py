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

# ======================================Solutions Brewer Library Modules==============================================||
from condor import condor
from ogma.logma import Logma

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", ".yaml")


# Main application to demonstrate the diagram editor
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    # Create and configure the diagram editor
    editor = DiagramEditor()
    editor.setWindowTitle("Diagram Editor with Connection Points")
    editor.resize(800, 600)

    # Add example nodes
    node_a = editor.add_node(-100, 0, label="A")
    node_b = editor.add_node(100, 0, label="B")
    node_c = editor.add_node(0, -100, label="C")

    # Add example edges
    editor.add_edge(node_a, node_b, "right", "left")  # Edge from right A to left B
    editor.add_edge(node_b, node_c, "top", "bottom")  # Edge from top B to bottom C
    editor.add_edge(node_c, node_a, "left", "right")  # Edge from left C to right A

    # Show the diagram editor
    editor.show()
    sys.exit(app.exec())

from Orange.widgets.canvas import CanvasScene, CanvasView
from PySide6.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsRectItem,
    QGraphicsPolygonItem,
    QGraphicsTextItem,
)
from PySide6.QtGui import QBrush, QPen, QColor, QPolygonF
from PySide6.QtCore import Qt, QPointF

# Main application to demonstrate the diagram editor
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Create and configure the diagram editor
    canvas = DiagramCanvasView()
    canvas.setWindowTitle("Diagram Editor (OrangeCanvas)")
    canvas.resize(800, 600)

    # Add example shapes
    canvas.add_rectangle(50, 50, 100, 60, label="Rectangle")
    canvas.add_circle(200, 100, 40, label="Circle")
    canvas.add_polygon(
        400,
        200,
        [QPointF(0, 0), QPointF(80, 40), QPointF(60, 120), QPointF(-40, 80)],
        label="Polygon",
    )

    # Show the diagram editor
    canvas.show()
    sys.exit(app.exec())

# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
