"""T-NEW-149: Matrix cell edits mirror into internal document content."""
from types import SimpleNamespace

import nchantdoffice.models  # noqa: F401
from nchantdoffice.widgets.documents.workbooks.matricies import NchantdOfficeMatrix


class _Signal:
    def __init__(self):
        self.values = []

    def emit(self, value):
        self.values.append(value)


class _Item:
    def __init__(self, row, column, text):
        self._row = row
        self._column = column
        self._text = text

    def row(self):
        return self._row

    def column(self):
        return self._column

    def text(self):
        return self._text


def _matrix(grid=None):
    matrix = NchantdOfficeMatrix.__new__(NchantdOfficeMatrix)
    matrix.document = SimpleNamespace(content={"grid": grid or []})
    matrix.dataChanged = _Signal()
    return matrix


def test_cell_change_mirrors_value_into_document_grid():
    matrix = _matrix()
    matrix.on_cell_changed(_Item(0, 0, "42"))
    assert matrix.document.content["grid"] == [["42"]]


def test_cell_change_preserves_non_square_grid_and_expands_target():
    matrix = _matrix([["a", "b"]])
    matrix.on_cell_changed(_Item(1, 1, "c"))
    assert matrix.document.content["grid"] == [["a", "b"], ["", "c"]]


def test_cell_change_preserves_existing_formulas():
    matrix = _matrix([["old"]])
    matrix.document.content["formulas"] = {"A1": "=1+1"}
    matrix.on_cell_changed(_Item(0, 0, "2"))
    assert matrix.document.content["formulas"] == {"A1": "=1+1"}
    assert matrix.dataChanged.values == [{"address": "A1", "value": "2"}]
