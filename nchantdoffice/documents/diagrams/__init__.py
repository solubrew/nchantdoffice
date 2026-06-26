"""
Nchantd Office - Diagrams Document Module

Diagram and flowchart documents for the Nchantd Office system.
Provides diagramming capabilities for visualizing processes, flows, and structures.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


class DiagramType(Enum):
    """Types of diagrams supported."""
    FLOWCHART = "flowchart"
    SEQUENCE = "sequence"
    CLASS = "class"
    STATE = "state"
    ENTITY = "entity"
    GANTT = "gantt"
    PIE = "pie"
    TIMELINE = "timeline"
    MINDMAP = "mindmap"
    ORG = "org"


class DiagramShape(Enum):
    """Shape types for diagram nodes."""
    RECTANGLE = "rectangle"
    ROUNDED_RECTANGLE = "rounded_rectangle"
    DIAMOND = "diamond"
    CIRCLE = "circle"
    OVAL = "oval"
    PARALLELOGRAM = "parallelogram"
    HEXAGON = "hexagon"
    CYLINDER = "cylinder"
    DATABASE = "database"


@dataclass
class DiagramNode:
    """A node in a diagram."""
    id: str
    label: str
    shape: DiagramShape = DiagramShape.RECTANGLE
    style: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DiagramEdge:
    """A connection between nodes."""
    source: str
    target: str
    label: Optional[str] = None
    style: str = "solid"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Diagram:
    """A diagram document."""
    title: str
    diagram_type: DiagramType = DiagramType.FLOWCHART
    nodes: List[DiagramNode] = field(default_factory=list)
    edges: List[DiagramEdge] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_node(self, node: DiagramNode) -> None:
        """Add a node to the diagram."""
        self.nodes.append(node)

    def add_edge(self, edge: DiagramEdge) -> None:
        """Add an edge to the diagram."""
        self.edges.append(edge)

    def to_dict(self) -> Dict[str, Any]:
        """Convert diagram to dictionary."""
        return {
            "title": self.title,
            "type": self.diagram_type.value,
            "nodes": [
                {
                    "id": n.id,
                    "label": n.label,
                    "shape": n.shape.value,
                    "style": n.style,
                    **n.metadata
                }
                for n in self.nodes
            ],
            "edges": [
                {
                    "source": e.source,
                    "target": e.target,
                    "label": e.label,
                    "style": e.style,
                    **e.metadata
                }
                for e in self.edges
            ],
            "metadata": self.metadata
        }


class Diagrams:
    """Manager for diagram documents."""
    
    def __init__(self):
        """Initialize the diagrams manager."""
        self.diagrams: Dict[str, Diagram] = {}
    
    def create_diagram(
        self,
        title: str,
        diagram_type: DiagramType = DiagramType.FLOWCHART
    ) -> Diagram:
        """Create a new diagram."""
        diagram = Diagram(title=title, diagram_type=diagram_type)
        self.diagrams[title] = diagram
        return diagram
    
    def get_diagram(self, title: str) -> Optional[Diagram]:
        """Get a diagram by title."""
        return self.diagrams.get(title)
    
    def list_diagrams(self) -> List[str]:
        """List all diagram titles."""
        return list(self.diagrams.keys())


def create_flowchart(title: str) -> Diagram:
    """Create a flowchart diagram."""
    return Diagram(title=title, diagram_type=DiagramType.FLOWCHART)


def create_sequence_diagram(title: str) -> Diagram:
    """Create a sequence diagram."""
    return Diagram(title=title, diagram_type=DiagramType.SEQUENCE)


def create_class_diagram(title: str) -> Diagram:
    """Create a class diagram."""
    return Diagram(title=title, diagram_type=DiagramType.CLASS)


def create_entity_diagram(title: str) -> Diagram:
    """Create an entity-relationship diagram."""
    return Diagram(title=title, diagram_type=DiagramType.ENTITY)


def create_gantt_chart(title: str) -> Diagram:
    """Create a Gantt chart."""
    return Diagram(title=title, diagram_type=DiagramType.GANTT)


def create_mindmap(title: str) -> Diagram:
    """Create a mind map."""
    return Diagram(title=title, diagram_type=DiagramType.MINDMAP)
