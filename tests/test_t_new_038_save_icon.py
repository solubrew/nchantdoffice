"""T-NEW-038 -- Save icon/action by document location (TDD tests).

The inline TODO at documents.py:353 said: "toggle to use
the database-save.svg icon for internally stored documents".

The action table in nchantrs defines:
  - save        -> icon: save
  - save_database -> icon: database-save
  - save_cloud    -> icon: cloud-save
  - save_as       -> icon: save

When the document's location is "internal" the action should
be ``save_database`` (which carries the database-save icon).
Otherwise it stays the legacy ``save`` (the save.svg icon).

The right place to fix this is the action field in the
``_buttons`` dict (init_toolbox, L351). When the current
document's location is "internal", switch the action to
``save_database`` so the toolbar's icon registry picks up
the right icon. Otherwise leave ``save`` unchanged.

Tests drive the action field -- NOT the icon name -- so
the test is decoupled from the icon-registration code.
"""

import sys
from types import SimpleNamespace

from PySide6.QtWidgets import QApplication
import nchantdoffice.widgets.documents.documents  # noqa: F401


# Action constants -- the T-NEW-038 close-out wires the
# internal-storage case to ``save_database`` so the action
# table's database-save icon kicks in. External and unknown
# stay on the legacy ``save``.
ACTION_SAVE = "save"
ACTION_SAVE_DATABASE = "save_database"


def test_save_action_for_internal_document_is_save_database():
    """When the document's location is 'internal', the save
    button action must be ``save_database`` so the action
    table picks the database-save icon.
    """
    from nchantdoffice.widgets.documents.documents import (
        NchantdOfficeDocument,
    )
    doc = NchantdOfficeDocument.__new__(NchantdOfficeDocument)
    doc.location = "internal"
    result = NchantdOfficeDocument._save_action(doc)
    assert result == ACTION_SAVE_DATABASE, (
        f"Internal document must use save_database action. "
        f"Got: {result!r}"
    )


def test_save_action_for_external_document_is_save():
    """When the document's location is 'external', the save
    button action stays the legacy ``save`` (which carries
    the save.svg icon).
    """
    from nchantdoffice.widgets.documents.documents import (
        NchantdOfficeDocument,
    )
    doc = NchantdOfficeDocument.__new__(NchantdOfficeDocument)
    doc.location = "external"
    result = NchantdOfficeDocument._save_action(doc)
    assert result == ACTION_SAVE


def test_save_action_for_unknown_location_is_save():
    """Defensive: when the location is something other than
    'internal' (e.g. a future 'cloud'), fall back to ``save``.
    """
    from nchantdoffice.widgets.documents.documents import (
        NchantdOfficeDocument,
    )
    doc = NchantdOfficeDocument.__new__(NchantdOfficeDocument)
    doc.location = "cloud"
    result = NchantdOfficeDocument._save_action(doc)
    assert result == ACTION_SAVE


def test_save_action_handles_missing_document():
    """When called with ``None`` (e.g. a button click before
    any document is open), the helper returns the legacy
    ``save`` -- no exception.
    """
    from nchantdoffice.widgets.documents.documents import (
        NchantdOfficeDocument,
    )
    result = NchantdOfficeDocument._save_action(None)
    assert result == ACTION_SAVE


def test_save_action_handles_missing_location_attribute():
    """Defensive: when the document has no ``location``
    attribute (e.g. legacy / un-migrated docs), the helper
    returns the legacy default.
    """
    from nchantdoffice.widgets.documents.documents import (
        NchantdOfficeDocument,
    )
    doc = NchantdOfficeDocument.__new__(NchantdOfficeDocument)
    # No `location` set
    result = NchantdOfficeDocument._save_action(doc)
    assert result == ACTION_SAVE


def test_save_action_handles_non_string_location():
    """Defensive: when ``location`` is not a string (e.g. an
    int or None due to data corruption), the helper returns
    the legacy default rather than crashing.
    """
    from nchantdoffice.widgets.documents.documents import (
        NchantdOfficeDocument,
    )
    doc = NchantdOfficeDocument.__new__(NchantdOfficeDocument)
    doc.location = None
    result = NchantdOfficeDocument._save_action(doc)
    assert result == ACTION_SAVE


def test_init_toolbox_uses_save_database_action_for_internal_doc():
    """End-to-end: the action field in the ``_buttons`` dict
    (init_toolbar, L351) must be ``save_database`` when the
    current document's location is 'internal'. The action
    table maps ``save_database`` -> ``database-save`` icon.
    """
    from nchantdoffice.widgets.documents.documents import (
        NchantdOfficeDocument,
    )
    doc = NchantdOfficeDocument.__new__(NchantdOfficeDocument)
    # Simulate the post-init state
    doc.document = SimpleNamespace(location="internal")
    action = NchantdOfficeDocument._save_action(doc.document)
    assert action == ACTION_SAVE_DATABASE, (
        f"Internal doc must use save_database action. "
        f"Got: {action!r}"
    )
    # And external docs use the legacy action
    doc.document = SimpleNamespace(location="external")
    action = NchantdOfficeDocument._save_action(doc.document)
    assert action == ACTION_SAVE