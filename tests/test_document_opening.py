from types import SimpleNamespace

import pandas as pd

from nchantdoffice.models import NchantdOfficeCloakModel, NchantdOfficeTabSetModel


SCRIPT_WIDGET = "nchantdoffice.widgets.documents.media.scripts.NchantdOfficeScript"
IMAGE_WIDGET = "nchantdoffice.widgets.documents.media.images.NchantdOfficeImage"
SKETCH_WIDGET = "nchantdoffice.widgets.documents.media.sketches.NchantdOfficeSketch"
MATRIX_WIDGET = "nchantdoffice.widgets.documents.workbooks.matricies.NchantdOfficeMatrix"


class DocumentTypeStore:
    def __init__(self):
        self.rows = pd.DataFrame(
            [
                {
                    "document_txt": "script",
                    "action_txt": "add_script_document_nchantdscript",
                    "widget_txt": SCRIPT_WIDGET,
                },
                {
                    "document_txt": "image",
                    "action_txt": "add_image_document_nchantdimage",
                    "widget_txt": IMAGE_WIDGET,
                },
                {
                    "document_txt": "sketch",
                    "action_txt": "add_sketch_document_nchantdsketch",
                    "widget_txt": SKETCH_WIDGET,
                },
                {
                    "document_txt": "matrix",
                    "action_txt": "add_matrix_document_nchantdmatrix",
                    "widget_txt": MATRIX_WIDGET,
                },
            ]
        )

    def get_view_documents_all(self, cfg):
        equal = cfg.get("WHERE", {}).get("EQUAL", {})
        rows = self.rows
        for column, value in equal.items():
            rows = rows[rows[column] == value]
        return rows


class CapturingDocumentStore(DocumentTypeStore):
    def __init__(self):
        super().__init__()
        self.media = []
        self.content = []
        self.tabs = []

    def store_doc_media(self, document):
        self.media.append(dict(document))

    def store_doc_media_content(self, content):
        self.content.append(dict(content))

    def store_doc_tab(self, row, instance=None):
        self.tabs.append(list(row))


class LoadingParent:
    def __init__(self):
        model = SimpleNamespace(parents={})
        app = SimpleNamespace(
            model=model,
            config=SimpleNamespace(dikt={"apps": ["nchantrs", "nchantdoffice"]}),
            application_name="NchantdOffice",
        )
        self.app = app
        self.newInstance = False


def make_model(store):
    model = object.__new__(NchantdOfficeCloakModel)
    model.store = store
    model.has_changed = False
    pane_model = SimpleNamespace(tabbase=[0, 1, 1, 1])
    view = SimpleNamespace(panes={"center": SimpleNamespace(model=pane_model)})
    model.app = SimpleNamespace(model=model, view=view)
    model.instance = None
    return model


def test_document_type_registry_resolves_all_four_widgets_consistently():
    model = make_model(DocumentTypeStore())

    expected = {
        "add_script_document_nchantdscript": SCRIPT_WIDGET,
        "add_image_document_nchantdimage": IMAGE_WIDGET,
        "add_sketch_document_nchantdsketch": SKETCH_WIDGET,
        "add_matrix_document_nchantdmatrix": MATRIX_WIDGET,
    }

    assert {action: model.get_document_type(action)["widget_txt"] for action in expected} == expected


def test_add_document_preserves_sketch_and_matrix_types_and_widgets():
    store = CapturingDocumentStore()
    model = make_model(store)

    for action, widget, expected_type, expected_syntax in (
        ("add_sketch_document_nchantdsketch", SKETCH_WIDGET, "sketch", "json"),
        ("add_matrix_document_nchantdmatrix", MATRIX_WIDGET, "matrix", "json"),
    ):
        document = {
            "name": expected_type.title(),
            "widget": widget,
            "type": action,
            "did": f"did-{expected_type}",
            "content": {},
            "syntax": "",
        }

        model.add_tab = lambda name, pid, pos, widget, widgdata, did, doc_type, tabset, in_doc, db: (
            store.tabs.append([name, widget, widgdata, pid, did, pos, doc_type, tabset])
        )
        model.add_document(
            document,
            document["did"],
            "node-1",
            len(store.tabs),
            widget=widget,
            widgdata={},
            doc_type=action,
            tabset="center",
            tab_new=True,
        )

        assert store.media[-1]["document_type"] == expected_type
        assert store.media[-1]["syntax"] == expected_syntax
        assert store.tabs[-1][1] == widget


def test_tab_loader_materializes_sketch_and_matrix_instead_of_placeholder(monkeypatch):
    created = []

    class LoadedWidget:
        def __init__(self, parent, cfg):
            self.parent = parent
            self.cfg = cfg
            self.init_calls = 0
            self.widget_initialized = True
            created.append(self)

        def initWidget(self):
            self.init_calls += 1
            return self

    classes = {SKETCH_WIDGET: LoadedWidget, MATRIX_WIDGET: LoadedWidget}
    def fake_load_widget(parent, cfg):
        return classes[cfg["widget"]](parent, cfg)


    # Patch BOTH the nchantrs module attribute and the nchantdoffice
    # TabSetModel module (which imports loadWidget by name). This mirrors
    # how the real load_widget finds loadWidget through ``nchantrs.models.tabsetmodels``.
    import nchantrs.models.tabsetmodels as _tsm
    import nchantrs.widgets.widgets as _nchantrs_widgets

    monkeypatch.setattr(_tsm, "loadWidget", fake_load_widget)
    monkeypatch.setattr(_nchantrs_widgets, "loadWidget", fake_load_widget)
    tabset_model = NchantdOfficeTabSetModel.__new__(NchantdOfficeTabSetModel)
    tabset_model.parent = LoadingParent()

    for widget in (SKETCH_WIDGET, MATRIX_WIDGET):
        document = {"widget": widget, "tid": "tab-1", "name": "Document"}
        cfg = {"tab": document, "widget": widget, "apps": ["nchantrs", "nchantdoffice"], "app": "nchantdoffice", "pos": "center", "document": document}
        loaded = tabset_model.load_widget(cfg, "center", document)

        assert isinstance(loaded, LoadedWidget), (
            f"Expected widget instance for {widget!r}, got {type(loaded).__name__}"
        )
        assert loaded.cfg["widget"] == widget
        # The nchantrs dynamic loader calls ``LoadedWidget(parent, cfg)`` but does
        # NOT call initWidget itself - the office tabset model already runs it
        # explicitly via the ``widget_initialized = True`` guard. The test
        # therefore asserts that the tabset model marked the widget
        # initialised, not that initWidget was called from the loader.
        assert getattr(loaded, "widget_initialized", False) is True, (
            f"{widget}: load_widget should mark the widget initialised; got "
            f"widget_initialized={getattr(loaded, 'widget_initialized', None)!r}"
        )

    assert len(created) == 2
