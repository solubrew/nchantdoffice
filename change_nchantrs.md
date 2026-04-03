# NchantRS Library Changes Required

## Issue Summary
The `NchantdCanvas` class from `nchantrs.widgets.canvases.canvases` does not support direct rendering via QPainter in its paintEvent. When attempting to create a QPainter instance on the canvas widget, it fails with:
```
QPainter::begin: Paint device returned engine == 0, type: 1
```

This prevents the NchantdOfficeSketch drawing application from displaying rendered graphics on the canvas.

## Required Changes

### Option 1: Add Paint Engine Support (Recommended if NchantdCanvas is a custom widget)

If `NchantdCanvas` is a custom QWidget subclass, ensure it properly supports QPainter:

**File: `nchantrs/widgets/canvases/canvases.py`**

```python
class NchantdCanvas(QWidget):  # or whatever base class it currently uses

    def __init__(self, parent=None, cfg=None):
        super().__init__(parent)
        # ... existing initialization ...

        # Ensure the widget can be painted on
        self.setAttribute(Qt.WA_OpaquePaintBackground, False)
        self.setAttribute(Qt.WA_NoSystemBackground, False)

    def paintEvent(self, event):
        """Handle paint events - allow subclasses to override or extend."""
        # Call parent implementation if it exists
        super().paintEvent(event)

        # Create painter for this widget
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw custom content here or allow subclasses to add content
        # via a hook method
        if hasattr(self, '_custom_paint'):
            self._custom_paint(painter, event)

        painter.end()
```

### Option 2: Provide Pixmap Display Method (Simpler Alternative)

Add a method to NchantdCanvas that allows external code to set a pixmap for display:

**File: `nchantrs/widgets/canvases/canvases.py`**

```python
class NchantdCanvas(...):

    def __init__(self, parent=None, cfg=None):
        super().__init__(parent)
        # ... existing initialization ...
        self._display_pixmap = None

    def setDisplayPixmap(self, pixmap):
        """Set a pixmap to be displayed on this canvas."""
        self._display_pixmap = pixmap
        self.update()

    def paintEvent(self, event):
        """Paint the canvas and any overlay pixmap."""
        super().paintEvent(event)

        if self._display_pixmap and not self._display_pixmap.isNull():
            painter = QPainter(self)
            painter.drawPixmap(0, 0, self._display_pixmap)
            painter.end()
```

### Option 3: Expose Internal Drawing Surface (If NchantdCanvas wraps another widget)

If `NchantdCanvas` is a wrapper around QGraphicsView or similar:

**File: `nchantrs/widgets/canvases/canvases.py`**

```python
class NchantdCanvas(...):

    def getDrawingSurface(self):
        """
        Return the actual widget that can be painted on.
        This might be the viewport of a QGraphicsView or similar.
        """
        # If NchantdCanvas wraps a QGraphicsView:
        if hasattr(self, 'viewport'):
            return self.viewport()

        # If it wraps a QScrollArea:
        if hasattr(self, 'widget'):
            return self.widget()

        # Otherwise return self
        return self
```

## Current Workaround in NchantdOffice

Currently using a QLabel overlay as a workaround:
```python
self.drawing_overlay = QLabel(self.canvas)
self.drawing_overlay.setAttribute(Qt.WA_TransparentForMouseEvents)
self.drawing_overlay.setPixmap(rendered_pixmap)
```

This works but is not ideal because:
1. Adds extra widget layer
2. Mouse event pass-through may have edge cases
3. Less efficient than direct rendering

## Recommendation

Implement **Option 2** (setDisplayPixmap method) as it:
- Minimal change to existing code
- Clean API for external drawing
- Maintains encapsulation
- Compatible with existing architecture

## Usage After Changes

Once changes are implemented, NchantdOfficeSketch will use:

```python
# Render shapes to pixmap
pixmap = QPixmap(canvas_size)
painter = QPainter(pixmap)
# ... draw shapes ...
painter.end()

# Display on canvas
self.canvas.setDisplayPixmap(pixmap)
```

## Additional Information Needed

Please confirm:
1. What is the base class of NchantdCanvas? (QWidget, QGraphicsView, QScrollArea, etc.)
2. Does NchantdCanvas currently have a paintEvent implementation?
3. Is there any existing mechanism for rendering custom content on NchantdCanvas?
