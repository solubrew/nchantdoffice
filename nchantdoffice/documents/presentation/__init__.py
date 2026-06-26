"""Presentation document module for nchantdoffice.

Provides PowerPoint (PPTX) and OpenDocument (ODP) presentation support.
"""

import sys
import os

# Add pyffice path for imports
PYFFICE_PATH = "/home/solubrew/.senbai/workspace/projects/pyffice"
if PYFFICE_PATH not in sys.path:
    sys.path.insert(0, PYFFICE_PATH)

from .presentation import Presentation

__all__ = ['Presentation']
