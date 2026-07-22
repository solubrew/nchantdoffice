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
from os.path import dirname, join, exists

# ======================================3rd Party Library Modules=====================================================||

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from nchantrs.libraries import pyqt
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument
from kahndor.logma import Logma
from nchantrs.widgets.media.editors.editors import NchantdLabeledEntry
from nchantrs.widgets.controls.advanced_buttons import NchantdEnableSpinBox
from nchantrs.widgets.media.editors.selectors import NchantdDropDownActivator, NchantdDropDown
from nchantrs.widgets.panes.panes import NchantdPane
from nchantrs.widgets.controls.buttons import NchantdButton
from nchantdoffice.widgets.panes.files import NchantdFileDetailsPane

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "pdfs.yaml")


class NchantdPageAddToolPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdPageAddToolPane").override(cfg))

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
        """"""
        super().initView(cfg)
        group = pyqt.QGroupBox("Page Sequence Control Tool: ")
        layout = pyqt.QVBoxLayout()
        group.setLayout(layout)
        pages = ["Page0", "Page1", "Page2", "Page3"]
        for page in pages:
            cfg = {
                "label": page,
                "layout": "horizontal",
                "size": ["auto", "auto"],
                "handler": self.cmd_page_number_change,
            }
            pageW = NchantdEnableSpinBox(self, cfg).initWidget()
            layout.addWidget(pageW)
        cfg = {
            "action": "open_local",
            "layout": "horizontal",
            "label": "Open File: ",
            "tooltip": "Open File to Combine Pages",
            "handler": self.cmd_open_file,
        }
        self.open_file_button = NchantdButton(self, cfg).initWidget()
        layout.addWidget(self.open_file_button)
        self.layout.addWidget(group)
        return self

    def cmd_page_number_change(self):
        """"""
        # TODO implement method

    def cmd_open_file(self):
        """"""
        # TODO implement method

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdOfficePDF(NchantdOfficeDocument):
    """"""

    def __init__(self, parent=None, cfg=None):
        """"""
        super().__init__("Nchantd PDF", parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficePDF").override(cfg))
        self.view = pyqt.QPdfView()
        self.annotations = None  # Store all drawing annotations as a list
        self.current_page = None  # Track the current PDF page
        self.document = None
        self.drawing = None  # Track whether the user is currently drawing
        self.pdf_page_image = None  # Loaded PDF page as an image
        self.pen = None
        self.previous_point = None  # Store the previous drawing point
        self.current_page = 0
        self.scale = 1.0
        self.text_instances = []
        self.selected_text = ""
        self.selection_start = None
        self.selection_end = None

    def initModel(self):
        """"""
        super().initModel()
        document = {"document": self.config.dikt.get("document", {})}
        logma.json(self.config.dikt["document"])
        self.document = self.app.model.codex.init_pdf(document)
        self.document.load_document()
        logma.json(self.document.to_dict())
        self.initialize_context_menu("context.document.pdf")
        return self

    def initView(self, cfg=None):
        """
        need a navigation bar at the top
        ideally an expandable index pane
        :return:
        """
        if cfg is None:
            cfg = {}
        cfg["buttons"] = {49: "_insert_stretch"}
        cfg["buttons"][10] = {"action": "set_markup_edit", "handler": ""}
        # cfg["buttons"][11] = {"action": "", "handler": ""}
        super().initView(cfg)

        self.view.setPageMode(pyqt.QPdfView.PageMode.MultiPage)
        # This is where the file is opened and set to be viewed in the application
        # end
        self.pdf = pyqt.QPdfDocument(self.view)
        logma.info(f"File Path {self.document.file_path}")
        if self.document.file_path is not None:
            self.open_file(self.document.file_path)

        # FIX: Add PDF view to existing layout instead of replacing it
        # The toolbar was already added by super().initView(), so we just add this widget

        self.layout.addWidget(self.view)

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def cmd_open_local_file(self, event=None, *args, **kwargs):
        """"""
        super().cmd_open_local_file(event, *args, **kwargs)
        if self.local_file is not None:
            if exists(self.local_file):
                self.open_file(self.local_file)
        return self

    def init_drawer_document_config(self):
        """"""
        items = self.toolbox_config[100].get("items", {})
        cnt = 0
        default_action = {"action": "insert_generic_action", "type": "custom"}
        if cnt not in items:
            items[cnt] = default_action
        cfg = {"label": "File Name: ", "layout": "horizontal"}
        self.file_pane = NchantdFileDetailsPane(self, cfg)
        items[cnt]["widget"] = self.file_pane
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action
        cfg = {
            "label": "Page Count:",
            "layout": "horizontal",
            "handler": self.cmd_page_count_change,
            "value": self.get_page_count() or "",
        }
        self.label_entry = NchantdLabeledEntry(self, cfg)
        items[cnt]["widget"] = self.label_entry
        return items

    def cmd_page_count_change(self):
        """"""
        # TODO implement method

    def get_page_count(self):
        """"""
        # TODO implement method

    def init_drawer_document_tools(self):
        """"""
        items = self.toolbox_config[200].get("items", {})
        cnt = 0
        default_action = {"action": "insert_generic_action", "type": "custom"}
        if cnt not in items:
            items[cnt] = default_action
        cfg = {
            "label": "Current Format: ",
            "layout": "horizontal",
            "handler": self.cmd_image_format_change,
            "value": self.get_file_format(),
        }
        self.image_format_entry = NchantdLabeledEntry(self, cfg)
        items[cnt]["widget"] = self.image_format_entry
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action
        cfg = {
            "label": "Convert Format",
            "layout": "horizontal",
            "handler": self.cmd_image_convert_change,
            "value": self.get_file_convert(),
        }
        self.image_conversion_select = NchantdDropDownActivator(self, cfg)
        items[cnt]["widget"] = self.image_conversion_select
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action
        cfg = {"label": "Add Pages", "layout": "horizontal"}
        self.page_add_pane = NchantdPageAddToolPane(self, cfg)
        items[cnt]["widget"] = self.page_add_pane
        cnt += 1
        return items

    def init_drawer_quickstart(self):
        """"""
        items = {}
        return items

    def init_pen(self, color=None, width=None, style=None, alpha=255, pen=None, *args, **kwargs):
        """"""
        # Pen properties for drawing
        if color is None:
            color = pyqt.Qt.red
        self.pen = pyqt.QPen(color)
        if width is None:
            width = 3
        self.pen.setWidth(width)
        return self

    def init_toolbox(self):
        """"""
        super().init_toolbox()
        self.toolbox_config[100]["items"] = self.init_drawer_document_config()
        self.toolbox_config[200]["items"] = self.init_drawer_document_tools()
        # PUSH to 0.0.3
        # self.toolbox_config[300]["items"] = self.init_drawer_quickstart()

    def cmd_image_format_change(self):
        """"""
        # TODO implement method

    def cmd_image_convert_change(self):
        """"""
        # TODO implement method

    def get_file_format(self):
        """"""
        # TODO implement method

    def get_file_convert(self):
        """"""
        # TODO implement method

    def get_content(self):
        """"""
        return super().get_content()

    def open_file(self, file=None):
        """"""
        if file is None:
            file = self.file_path
        self.document.open_file(file)  # The Pyffice document is not connected directly with the viewable pdf render
        self.document.set_location("external")
        self.populate_document()
        return self

    def populate_document(self):
        """"""
        if self.document.file_path is None:
            return
        self.pdf.load(self.document.file_path)
        self.view.setDocument(self.pdf)
        return self

    def save(self):
        """"""
        super().save()
        return self

    def load_page(self):
        """Load and display the current page with text extraction"""
        # page = self.document.extract_text(self.current_page)
        page = self.pdf_document[self.current_page]
        # Get page as pixmap
        mat = fitz.Matrix(self.scale, self.scale)
        pix = page.get_pixmap(matrix=mat)
        img_data = pix.tobytes("ppm")
        pixmap = pyqt.QPixmap()
        pixmap.loadFromData(img_data)
        # Extract text with position information
        self.text_instances = page.get_text("dict")
        self.pdf_label.setPixmap(pixmap)
        self.pdf_label.resize(pixmap.size())

    def get_text_at_position(self, pos):
        """Find text at a given position"""
        for block in self.text_instances["blocks"]:
            if "lines" not in block:
                continue

            for line in block["lines"]:
                for span in line["spans"]:
                    bbox = span["bbox"]
                    rect = pyqt.QRect(
                        int(bbox[0] * self.scale),
                        int(bbox[1] * self.scale),
                        int((bbox[2] - bbox[0]) * self.scale),
                        int((bbox[3] - bbox[1]) * self.scale),
                    )

                    if rect.contains(pos):
                        return span["text"], rect, span
        return None, None, None

    def select_text_in_area(self, start_pos, end_pos):
        """Select all text within the defined area"""
        selected_text = ""
        selection_rects = []

        for block in self.text_instances["blocks"]:
            if "lines" not in block:
                continue

            for line in block["lines"]:
                for span in line["spans"]:
                    bbox = span["bbox"]
                    rect = pyqt.QRect(
                        int(bbox[0] * self.scale),
                        int(bbox[1] * self.scale),
                        int((bbox[2] - bbox[0]) * self.scale),
                        int((bbox[3] - bbox[1]) * self.scale),
                    )

                    # Check if the span intersects with selection area
                    selection_area = pyqt.QRect(
                        min(start_pos.x(), end_pos.x()),
                        min(start_pos.y(), end_pos.y()),
                        abs(end_pos.x() - start_pos.x()),
                        abs(end_pos.y() - start_pos.y()),
                    )

                    if selection_area.intersects(rect):
                        selected_text += span["text"]
                        selection_rects.append(rect)

        return selected_text, selection_rects

    def mouse_press_event(self, event: pyqt.QMouseEvent):
        if event.button() == pyqt.Qt.MouseButton.LeftButton:
            self.selection_start = event.pos()
            self.selection_end = event.pos()

    def mouse_move_event(self, event: pyqt.QMouseEvent):
        if self.selection_start:
            self.selection_end = event.pos()
            self.update_selection_display()

    def mouse_release_event(self, event: pyqt.QMouseEvent):
        if self.selection_start and self.selection_end:
            selected_text, rects = self.select_text_in_area(self.selection_start, self.selection_end)

            if selected_text.strip():
                self.selected_text = selected_text
                logma.info(f"Selected text: {self.selected_text}")

                # Copy to clipboard
                clipboard = pyqt.QApplication.clipboard()
                clipboard.setText(self.selected_text)

        self.selection_start = None
        self.selection_end = None

    def update_selection_display(self):
        """Update the display to show current selection"""
        if not self.selection_start or not self.selection_end:
            return

        # Redraw the page with selection highlight
        page = self.pdf_document[self.current_page]
        mat = fitz.Matrix(self.scale, self.scale)
        pix = page.get_pixmap(matrix=mat)
        img_data = pix.tobytes("ppm")

        pixmap = pyqt.QPixmap()
        pixmap.loadFromData(img_data)

        # Draw selection rectangle
        painter = pyqt.QPainter(pixmap)
        pen = pyqt.QPen(pyqt.QColor(0, 120, 215, 100))
        painter.setPen(pen)
        painter.setBrush(pyqt.QColor(0, 120, 215, 50))

        selection_rect = pyqt.QRect(
            min(self.selection_start.x(), self.selection_end.x()),
            min(self.selection_start.y(), self.selection_end.y()),
            abs(self.selection_end.x() - self.selection_start.x()),
            abs(self.selection_end.y() - self.selection_start.y()),
        )

        painter.drawRect(selection_rect)
        painter.end()

        self.pdf_label.setPixmap(pixmap)


class NchantdOfficePDFMarkup(pyqt.QGraphicsView):
    def __init__(self, pdf_document, parent=None):
        super().__init__(parent)

        self.pdf_document = pdf_document  # The loaded PDF document
        self.scene = pyqt.QGraphicsScene(self)  # Scene that displays the PDF page
        self.setScene(self.scene)

        self.current_page = 0  # Track the current PDF page
        self.pdf_page_image = None  # Loaded PDF page as an image
        self.annotations = []  # Store all drawing annotations as a list
        self.drawing = False  # Track whether the user is currently drawing
        self.previous_point = pyqt.QPointF()  # Store the previous drawing point

        # Pen properties for drawing
        self.pen = pyqt.QPen(pyqt.Qt.red)
        self.pen.setWidth(3)

        # Enable scrollable and zoomable behavior
        self.setRenderHint(pyqt.QPainter.Antialiasing)
        self.setTransformationAnchor(pyqt.QGraphicsView.AnchorUnderMouse)
        self.setDragMode(pyqt.QGraphicsView.ScrollHandDrag)

    def initView(self):
        """"""
        # self.canvas = NchantdCanvas(self, cfg).initWidget()
        # self.canvas.setSizePolicy(pyqt.QSizePolicy.Expanding, pyqt.QSizePolicy.MinimumExpanding)
        # self.layout.addWidget(self.canvas)
        #
        # self.current_page = 0  # Track the current PDF page
        # self.pdf_page_image = None  # Loaded PDF page as an image
        # self.annotations = []  # Store all drawing annotations as a list
        # self.drawing = False  # Track whether the user is currently drawing
        # self.previous_point = pyqt.QPointF()  # Store the previous drawing point
        #
        # # Enable scrollable and zoomable behavior
        # self.setRenderHint(pyqt.QPainter.Antialiasing)
        # self.setTransformationAnchor(pyqt.QGraphicsView.AnchorUnderMouse)
        # self.setDragMode(pyqt.QGraphicsView.ScrollHandDrag)

    def load_page(self):
        """Render the current PDF page onto the QGraphicsScene."""
        if not self.pdf_document:
            return

        page = self.pdf_document.page(self.current_page)
        if page is None:
            return

        # Render the PDF page into a QImage
        pdf_size = page.pageSize()
        self.pdf_page_image = pyqt.QImage(pdf_size.width() * 2, pdf_size.height() * 2, pyqt.QImage.Format_ARGB32)
        self.pdf_page_image.fill(pyqt.Qt.white)
        painter = pyqt.QPainter(self.pdf_page_image)
        page.render(painter)
        painter.end()

        # Add the rendered page to the scene
        self.scene.clear()
        self.scene.setSceneRect(0, 0, self.pdf_page_image.width(), self.pdf_page_image.height())
        self.scene.addPixmap(self.pdf_page_image)

        # Reapply all previous annotations
        self.render_annotations()

    def render_annotations(self):
        """Reapply all previously drawn annotations."""
        for start_point, end_point in self.annotations:
            self.scene.addLine(start_point.x(), start_point.y(), end_point.x(), end_point.y(), self.pen)

    def mousePressEvent(self, event: pyqt.QMouseEvent):
        """Begin drawing when the user presses the left mouse button."""
        if event.button() == pyqt.Qt.LeftButton:
            self.drawing = True
            # Map the mouse position to the scene coordinates
            self.previous_point = self.mapToScene(event.pos())

    def mouseMoveEvent(self, event: pyqt.QMouseEvent):
        """Draw lines as the user moves the mouse."""
        if self.drawing:
            current_point = self.mapToScene(event.pos())  # Map the mouse position to the scene
            # Draw a line from the previous point to the current point
            self.scene.addLine(
                self.previous_point.x(),
                self.previous_point.y(),
                current_point.x(),
                current_point.y(),
                self.pen,
            )
            # Save the annotation
            self.annotations.append((self.previous_point, current_point))
            # Update the previous point
            self.previous_point = current_point

    def mouseReleaseEvent(self, event: pyqt.QMouseEvent):
        """Stop drawing when the user releases the mouse button."""
        if event.button() == pyqt.Qt.LeftButton:
            self.drawing = False

    def next_page(self):
        """Navigate to the next page of the PDF."""
        if self.current_page < self.pdf_document.pageCount() - 1:
            self.current_page += 1
            self.load_page()

    def previous_page(self):
        """Navigate to the previous page of the PDF."""
        if self.current_page > 0:
            self.current_page -= 1
            self.load_page()

    def clear_drawings(self):
        """Clear all drawing annotations on the current page."""
        self.pdf_viewer.annotations.clear()
        self.pdf_viewer.load_page()

    def cmd_set_markup_edit(self, event=None, *args, **kwargs):
        """"""
        # need to switch viewers should this be an single class or a swap tab initialization?
        # what happens when you switch back...print image to pdf?

        # i think direct edit of the PDF is something we are going to avoid initially
        #
        # launch pop
        text = "Performing a Markup will create a new tab copy of this PDF and must be exported if a new PDF is needed."


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
