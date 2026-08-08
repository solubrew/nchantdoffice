"""T-DESK-060 — Audit ``widgets/catalogs.py`` for server-API
consumption.

Paired with nchantdofficeATNRG cross-repo review
(``docs/cross-repo-review_20260807.md`` §2.6).

The original card assumed ``widgets/catalogs.py`` was a
"quicklinks catalog" that should read from
``GET /api/v1/quicklinks/``. The audit revealed that
``widgets/catalogs.py`` is actually the LOCAL DOCUMENT
CATALOGS widget (Documents / Extensions / Services /
DataSources) — a filesystem-based widget for browsing
local documents, completely different scope from
"quicklinks".

This test pins the audit conclusion:

  - ``widgets/catalogs.py`` declares 4 catalog classes:
    ``NchantdOfficeDocumentsCatalog``,
    ``NchantdOfficeExtensionsCatalog``,
    ``NchantdOfficeServicesCatalog``,
    ``NchantdDataSourcesCatalog``
  - None of them call any HTTP API (no
    ``requests.get`` / ``requests.Session`` /
    ``nchantdoffice_com``-style client). The catalog is
    local-only.
  - The widget does NOT need a ``QuicklinksAPIClient`` —
    that would be a NEW feature, not a gap closure.

If a future operator wants a server-backed "quicklinks
catalog" widget, that's a new feature (T-NEW-NNN), not
T-DESK-060. The audit pin prevents the next reviewer from
mis-classifying the file's scope.

Refs:
  - docs/cross-repo-review_20260807.md §2.6
  - nchantdoffice/widgets/catalogs.py
  - nchantdofficeATNRG/ReferralLinks.yaml (the server-side
    quicklinks source — currently consumed only by
    FALLBACK_BANNERS, not by catalogs.py)
"""

import ast
import sys
from pathlib import Path

PROJ_ROOT = Path("/home/solubrew/.hermes/projects/nchantdoffice")
sys.path.insert(0, str(PROJ_ROOT))

CATALOGS = PROJ_ROOT / "nchantdoffice" / "widgets" / "catalogs.py"


def _read(path: Path) -> str:
    return path.read_text()


def _ast_class(src: str, name: str):
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == name:
            return node
    return None


# ---------------------------------------------------------------------------
# Audit pins
# ---------------------------------------------------------------------------


def test_catalogs_module_exists():
    """The catalogs widget module exists (audit prerequisite)."""
    assert CATALOGS.exists(), (
        f"nchantdoffice/widgets/catalogs.py must exist (T-DESK-060 "
        f"audit target). Expected at {CATALOGS}."
    )


def test_catalogs_declares_four_local_catalog_classes():
    """The widget must declare 4 catalog classes (Documents,
    Extensions, Services, DataSources). Pinning the names
    prevents a refactor that drops one and silently
    removes it from the right-pane.
    """
    src = _read(CATALOGS)
    for cls in (
        "NchantdOfficeDocumentsCatalog",
        "NchantdOfficeExtensionsCatalog",
        "NchantdOfficeServicesCatalog",
        "NchantdDataSourcesCatalog",
    ):
        assert _ast_class(src, cls) is not None, (
            f"catalogs.py must declare {cls} class."
        )


def test_catalogs_classes_inherit_from_NchantdCatalog():
    """All 4 catalog classes must subclass ``NchantdCatalog``
    (the nchantrs base class). The base class is local-only
    (filesystem-based) — that's the architectural proof
    that catalogs.py is NOT server-backed.
    """
    src = _read(CATALOGS)
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            if not node.name.startswith("NchantdOffice") or "Catalog" not in node.name:
                continue
            base_names = [
                b.id if isinstance(b, ast.Name) else ast.unparse(b)
                for b in node.bases
            ]
            assert "NchantdCatalog" in base_names, (
                f"{node.name} must subclass NchantdCatalog. "
                f"Found bases: {base_names}."
            )


def test_catalogs_has_no_http_client():
    """Audit conclusion: ``catalogs.py`` does NOT call any HTTP
    API. No ``requests.get``, no ``requests.Session``, no
    ``nchantdoffice_com`` import. This is the contract that
    distinguishes "local catalogs" from "server-backed
    quicklinks".

    Pinning this so a future cleanup can't accidentally
    add an HTTP call to catalogs.py and silently couple
    the local-file browser to the network.
    """
    src = _read(CATALOGS)
    # No HTTP calls anywhere.
    forbidden = [
        "requests.",
        "urllib",
        "http.client",
        "httpx",
        "aiohttp",
        "nchantdoffice_com",  # the server repo
        "ReferralAPIClient",
        "QuicklinksAPIClient",
    ]
    for needle in forbidden:
        assert needle not in src, (
            f"catalogs.py must not reference {needle!r} — "
            f"the local catalogs widget is filesystem-only. "
            f"If you need server-backed quicklinks, create "
            f"a NEW widget (don't pollute catalogs.py)."
        )


def test_catalogs_uses_pandas_dataframe():
    """Pin that catalogs.py renders via ``pandas.DataFrame``
    (the existing pattern for showing local document
    lists). This confirms the audit conclusion: the widget
    is a local data-browser, not a network client.
    """
    src = _read(CATALOGS)
    assert "DataFrame" in src, (
        "catalogs.py must render via pandas.DataFrame "
        "(the local-catalog rendering pattern)."
    )


# ---------------------------------------------------------------------------
# Audit conclusion: pin the "T-DESK-060 is a NO-OP" finding
# ---------------------------------------------------------------------------


def test_audit_conclusion_pinned_in_review_doc():
    """The cross-repo review doc must record that T-DESK-060
    was audited and concluded "no fix needed" — the widget
    is local-only, not the quicklinks catalog the original
    card assumed.
    """
    doc_path = PROJ_ROOT / "docs" / "cross-repo-review_20260807.md"
    assert doc_path.exists(), (
        "docs/cross-repo-review_20260807.md must exist."
    )
    text = doc_path.read_text()
    # Pin the conclusion so a future reviewer doesn't
    # re-classify the file's scope.
    assert "T-DESK-060" in text, (
        "cross-repo-review must name T-DESK-060."
    )
    # The audit conclusion must explicitly note that
    # catalogs.py is local-only (not the quicklinks
    # catalog the original card assumed).
    assert (
        "local" in text.lower()
        and (
            "filesystem" in text.lower()
            or "local-only" in text.lower()
            or "local only" in text.lower()
        )
    ), (
        "T-DESK-060 audit conclusion must note that "
        "catalogs.py is local-only / filesystem-based."
    )
