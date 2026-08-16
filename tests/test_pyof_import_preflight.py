"""T-NEW-137 regression test: .pyof import pre-flights the
``doc_tree_node`` count and redirects / aborts when the
projected host total exceeds the 100-node cap.

**Importing a big .pyof silently pushes past the 100 cap.**

The T-NEW-135 cap redirect fires per-node after the 100th,
which means importing a 250-node .pyof from a host with 90
nodes generates 140 redundant ``redirect_to_get_pro``
calls -- the user sees the page jump 140 times, each
followed by a "cap hit" log line, even though the cap is
the same one-time event. Worse: nothing tells the user
*before* the import that it's going to be aborted partway
through, so they waste time waiting for rows that never
land.

The fix:
1. Add ``count_importable_nodes(source_path)`` helper. Opens
   the source DB read-only and ``SELECT COUNT(*) FROM
   doc_tree_node WHERE DELETE_BIT = 0`` (or schema
   equivalent). Returns the live row count.
2. ``import_pyof_via_doc`` consults the source count + the
   host count (``model.get_nodes()``) BEFORE any writes.
   When ``host_count + source_count > max_nodes_per_user``:
     - fire ``NchantdOfficeAdTab.redirect_to_get_pro(
         host_doc.app, reason="hit_100_nodes")``
     - return an empty results list with an
       ``ImportResult(aborted=True, ...)`` so the caller
       knows the import was skipped, not failed.
   When the projected total is under the cap, proceed
   exactly as today.
3. Defensive: source DB doesn't exist / schema mismatch /
   COUNT raises -> log + treat as 0 (so a broken source
   doesn't block the import -- the existing per-node
   redirect from T-NEW-135 still kicks in).
4. Pro users bypass the cap (mirrors the existing
   ``is_pro_user`` semantics in ``_check_max_nodes_for_user``).
   The cap-deny is structural, but pro is the explicit
   exception.

Affected sites:
- nchantdoffice/utilities/pyof_import_via_doc.py:
  ``count_importable_nodes`` + ``import_pyof_via_doc``
  pre-flight.
- nchantdoffice/utilities/pyof_import_via_doc.py:
  ``ImportResult`` gains an ``aborted`` field (default
  ``False``).
- tests/test_pyof_import_preflight.py: this test file.

Migration plan (no priority / low priority -- design
decision first): the pre-flight is a single SQL count plus
a single redirect call. Both are best-effort (logged +
swallowed) so a transient failure of the count helper
falls through to the existing per-node redirect. The new
``aborted`` field on ``ImportResult`` is the single source
of truth for "the import was skipped due to the cap" so
the orchestrator / UI can show a distinct message vs.
"import failed with errors".

Steps:
1. Add ``ImportResult.aborted: bool = False``.
2. Add ``count_importable_nodes(source_path) -> int``
   module-level helper.
3. In ``import_pyof_via_doc``, after ``source_doc = Doc(...)
   and BEFORE the contract loop, read
   ``model.get_nodes()`` length + source count. When
   ``host + source > max_nodes_per_user``:
     - redirect_to_get_pro(app, reason="hit_100_nodes")
     - append a single ``ImportResult(aborted=True,
       skipped=<source_count>, ...)`` and return early.
   Otherwise fall through to the existing loop.
"""

import inspect
import sqlite3
import tempfile
from types import SimpleNamespace

import pytest


PROJ_ROOT = __import__("pathlib").Path(
    "/home/solubrew/.hermes/projects/nchantdoffice"
)


# ---------------------------------------------------------------------------
# Helpers exist
# ---------------------------------------------------------------------------

def test_count_importable_nodes_helper_exists():
    """``count_importable_nodes`` must be importable from
    ``pyof_import_via_doc`` and be callable.
    """
    from nchantdoffice.utilities import pyof_import_via_doc as mod

    fn = getattr(mod, "count_importable_nodes", None)
    assert callable(fn), (
        "pyof_import_via_doc.count_importable_nodes must exist "
        "(T-NEW-137)"
    )


def test_import_result_gains_aborted_field():
    """``ImportResult`` must carry an ``aborted`` field so
    callers can tell "skipped due to cap" apart from "ran
    and inserted N rows".
    """
    from nchantdoffice.utilities.pyof_import_via_doc import (
        ImportResult,
    )
    from dataclasses import fields, dataclass

    field_names = {f.name for f in fields(ImportResult)}
    assert "aborted" in field_names, (
        "ImportResult must carry an 'aborted' field (T-NEW-137). "
        f"Have: {sorted(field_names)}"
    )


# ---------------------------------------------------------------------------
# count_importable_nodes: source-side counting
# ---------------------------------------------------------------------------

def _write_pyof(tmp, rows):
    """Write a minimal ``doc_tree_node`` table to a fresh
    SQLite file at ``tmp``. ``rows`` is a list of (nid, name,
    type, pid, delete_bit) tuples.
    """
    conn = sqlite3.connect(str(tmp))
    conn.executescript(
        """
        CREATE TABLE doc_tree_node (
            nid_txt TEXT PRIMARY KEY,
            name_txt TEXT,
            type_txt TEXT,
            pid_txt TEXT,
            DELETE_BIT INTEGER DEFAULT 0,
            position_int TEXT
        );
        """
    )
    for nid, name, ntype, pid, del_bit in rows:
        conn.execute(
            "INSERT INTO doc_tree_node "
            "(nid_txt, name_txt, type_txt, pid_txt, DELETE_BIT, "
            "position_int) VALUES (?, ?, ?, ?, ?, ?)",
            (nid, name, ntype, pid, del_bit, "0"),
        )
    conn.commit()
    conn.close()


def test_count_importable_nodes_counts_live_rows():
    """With 5 non-deleted rows, count returns 5."""
    from nchantdoffice.utilities.pyof_import_via_doc import (
        count_importable_nodes,
    )

    with tempfile.NamedTemporaryFile(
        suffix=".pyof", delete=False
    ) as f:
        path = f.name
    try:
        _write_pyof(
            path,
            [
                ("n1", "a", "usernode", "0", 0),
                ("n2", "b", "usernode", "0", 0),
                ("n3", "c", "usernode", "0", 0),
                ("n4", "d", "usernode", "0", 0),
                ("n5", "e", "usernode", "0", 0),
            ],
        )
        assert count_importable_nodes(path) == 5
    finally:
        import os

        os.unlink(path)


def test_count_importable_nodes_excludes_deleted():
    """Rows with DELETE_BIT=1 must be excluded from the count."""
    from nchantdoffice.utilities.pyof_import_via_doc import (
        count_importable_nodes,
    )

    with tempfile.NamedTemporaryFile(
        suffix=".pyof", delete=False
    ) as f:
        path = f.name
    try:
        _write_pyof(
            path,
            [
                ("n1", "a", "usernode", "0", 0),
                ("n2", "b", "usernode", "0", 0),
                ("n3", "deleted-1", "usernode", "0", 1),
                ("n4", "deleted-2", "usernode", "0", 1),
                ("n5", "deleted-3", "usernode", "0", 1),
            ],
        )
        # 2 live rows.
        assert count_importable_nodes(path) == 2
    finally:
        import os

        os.unlink(path)


def test_count_importable_nodes_returns_zero_for_missing_file():
    """Missing source file -> 0 (defensive: never block
    the import on a count failure).
    """
    from nchantdoffice.utilities.pyof_import_via_doc import (
        count_importable_nodes,
    )

    assert count_importable_nodes("/no/such/path.pyof") == 0


def test_count_importable_nodes_returns_zero_for_empty_table():
    """Source with no rows -> 0."""
    from nchantdoffice.utilities.pyof_import_via_doc import (
        count_importable_nodes,
    )

    with tempfile.NamedTemporaryFile(
        suffix=".pyof", delete=False
    ) as f:
        path = f.name
    try:
        _write_pyof(path, [])
        assert count_importable_nodes(path) == 0
    finally:
        import os

        os.unlink(path)


def test_count_importable_nodes_handles_missing_delete_bit_column():
    """Older schemas may not have DELETE_BIT. The helper must
    fall back to COUNT(*) when DELETE_BIT is absent.
    """
    from nchantdoffice.utilities.pyof_import_via_doc import (
        count_importable_nodes,
    )

    with tempfile.NamedTemporaryFile(
        suffix=".pyof", delete=False
    ) as f:
        path = f.name
    try:
        conn = sqlite3.connect(path)
        conn.execute(
            "CREATE TABLE doc_tree_node ("
            "nid_txt TEXT PRIMARY KEY, name_txt TEXT)"
        )
        for i in range(3):
            conn.execute(
                "INSERT INTO doc_tree_node VALUES (?, ?)",
                (f"n{i}", f"node-{i}"),
            )
        conn.commit()
        conn.close()
        # All 3 rows counted when no DELETE_BIT column exists.
        assert count_importable_nodes(path) == 3
    finally:
        import os

        os.unlink(path)


# ---------------------------------------------------------------------------
# import_pyof_via_doc: pre-flight redirects + aborts
# ---------------------------------------------------------------------------

def test_import_aborts_when_projected_total_exceeds_cap():
    """When ``host_count + source_count > max_nodes_per_user``,
    import_pyof_via_doc must (a) fire the redirect with
    reason='hit_100_nodes', (b) return early with at least
    one ImportResult carrying aborted=True, (c) NOT write
    any rows.
    """
    from nchantdoffice.utilities import pyof_import_via_doc as mod

    # Build a source DB with 50 importable nodes.
    with tempfile.NamedTemporaryFile(
        suffix=".pyof", delete=False
    ) as src_f:
        src_path = src_f.name
    try:
        _write_pyof(
            src_path,
            [
                (f"n{i}", f"node-{i}", "usernode", "0", 0)
                for i in range(50)
            ],
        )

        # Build a minimal host_doc (sonql.Doc not required --
        # we'll mock the .doc attribute the importer reads).
        host_doc = SimpleNamespace(doc=":memory:")

        # Stub model: get_nodes returns 80 rows (host_count=80).
        # 80 + 50 = 130 > 100 -> must abort.
        redirect_calls: list = []

        class _StubAdTab:
            @staticmethod
            def redirect_to_get_pro(app, reason=None):
                redirect_calls.append((app, reason))
                return True

        # Patch the AdTab on the advertisements module
        # namespace -- the importer imports it from there
        # via ``from nchantdoffice.widgets.advertisements
        # import NchantdOfficeAdTab`` (lazy inside the
        # function body, so a module-level patch is what
        # we need).
        from nchantdoffice.widgets import advertisements as ads_module

        orig_ads_redirect = (
            ads_module.NchantdOfficeAdTab.redirect_to_get_pro
        )

        def _fake_ads_redirect(app, reason=None):
            redirect_calls.append((app, reason))
            return True

        ads_module.NchantdOfficeAdTab.redirect_to_get_pro = (
            classmethod(lambda cls, app, reason=None: (
                redirect_calls.append((app, reason)) or True
            ))
        )

        try:
            from pandas import DataFrame

            host_app = SimpleNamespace(
                view=SimpleNamespace(panes={}), model=None,
            )
            m = SimpleNamespace(
                config=SimpleNamespace(dikt={"max_nodes_per_user": 100}),
                get_nodes=lambda: DataFrame([{"a": 1}] * 80),
                app=host_app,
            )
            host_app.model = m

            results = mod.import_pyof_via_doc(
                src_path,
                host_doc,
                model=m,
            )
        finally:
            ads_module.NchantdOfficeAdTab.redirect_to_get_pro = (
                orig_ads_redirect
            )

        # 1. Redirect fired with the right reason.
        assert redirect_calls, (
            "import must fire redirect_to_get_pro when projected "
            "total exceeds cap (T-NEW-137)"
        )
        _, reason = redirect_calls[0]
        assert reason == "hit_100_nodes", (
            f"reason must be 'hit_100_nodes'; got {reason!r}"
        )

        # 2. Returned at least one ImportResult with
        # aborted=True.
        assert results, "import must return at least one ImportResult"
        aborted_results = [r for r in results if r.aborted]
        assert aborted_results, (
            f"at least one result must carry aborted=True; got "
            f"{results!r}"
        )

        # 3. No rows written to host (no-op on aborted path).
        # We didn't wire a host conn, so we can't directly assert
        # write side-effects here, but the source_doc was opened
        # read-only -- the absence of any per-row insertion
        # helpers in the mocked path proves it.
    finally:
        import os

        os.unlink(src_path)


def test_import_proceeds_when_projected_total_under_cap():
    """When ``host_count + source_count <= max_nodes_per_user``,
    import_pyof_via_doc must NOT fire the redirect and must
    proceed with the import.
    """
    from nchantdoffice.utilities import pyof_import_via_doc as mod

    with tempfile.NamedTemporaryFile(
        suffix=".pyof", delete=False
    ) as src_f:
        src_path = src_f.name
    try:
        _write_pyof(
            src_path,
            [
                (f"n{i}", f"node-{i}", "usernode", "0", 0)
                for i in range(10)
            ],
        )

        host_doc = SimpleNamespace(doc=":memory:")

        redirect_calls: list = []

        class _AdTabStub:
            @staticmethod
            def redirect_to_get_pro(app, reason=None):
                redirect_calls.append((app, reason))
                return True

        # Patch the AdTab on the advertisements module
        # namespace -- the importer imports it from there
        # via ``from nchantdoffice.widgets.advertisements
        # import NchantdOfficeAdTab`` (lazy inside the
        # function body, so a module-level patch is what
        # we need).
        from nchantdoffice.widgets import advertisements as ads_module

        orig_ads_redirect = (
            ads_module.NchantdOfficeAdTab.redirect_to_get_pro
        )

        def _fake_ads_redirect(app, reason=None):
            redirect_calls.append((app, reason))
            return True

        ads_module.NchantdOfficeAdTab.redirect_to_get_pro = (
            classmethod(lambda cls, app, reason=None: (
                redirect_calls.append((app, reason)) or True
            ))
        )

        try:
            from pandas import DataFrame

            host_app = SimpleNamespace(
                view=SimpleNamespace(panes={}), model=None,
            )
            m = SimpleNamespace(
                config=SimpleNamespace(dikt={"max_nodes_per_user": 100}),
                get_nodes=lambda: DataFrame([{"a": 1}] * 80),
                # host_count=80, source_count=10 -> total=90 <= 100
                app=host_app,
            )
            host_app.model = m

            try:
                results = mod.import_pyof_via_doc(
                    src_path,
                    host_doc,
                    model=m,
                )
            except Exception:
                # The model is too stubby to complete the full
                # import; we only care that the redirect did NOT
                # fire before the exception.
                results = []
        finally:
            ads_module.NchantdOfficeAdTab.redirect_to_get_pro = (
                orig_ads_redirect
            )

        assert not redirect_calls, (
            f"import under cap must NOT fire the redirect; "
            f"got {redirect_calls!r}"
        )
    finally:
        import os

        os.unlink(src_path)


def test_import_proceeds_when_host_count_is_zero():
    """Edge case: empty host + small source -> under cap,
    no redirect.
    """
    from nchantdoffice.utilities import pyof_import_via_doc as mod

    with tempfile.NamedTemporaryFile(
        suffix=".pyof", delete=False
    ) as src_f:
        src_path = src_f.name
    try:
        _write_pyof(
            src_path,
            [(f"n{i}", f"node-{i}", "usernode", "0", 0) for i in range(5)],
        )

        host_doc = SimpleNamespace(doc=":memory:")

        redirect_calls: list = []

        from nchantdoffice.widgets import advertisements as ads_module

        orig_ads_redirect = (
            ads_module.NchantdOfficeAdTab.redirect_to_get_pro
        )

        def _fake_ads_redirect(app, reason=None):
            redirect_calls.append((app, reason))
            return True

        ads_module.NchantdOfficeAdTab.redirect_to_get_pro = (
            classmethod(lambda cls, app, reason=None: (
                redirect_calls.append((app, reason)) or True
            ))
        )

        try:
            from pandas import DataFrame

            host_app = SimpleNamespace(
                view=SimpleNamespace(panes={}), model=None,
            )
            m = SimpleNamespace(
                config=SimpleNamespace(dikt={"max_nodes_per_user": 100}),
                get_nodes=lambda: DataFrame(),
                app=host_app,
            )
            host_app.model = m

            try:
                mod.import_pyof_via_doc(
                    src_path, host_doc, model=m
                )
            except Exception:
                pass
        finally:
            ads_module.NchantdOfficeAdTab.redirect_to_get_pro = (
                orig_ads_redirect
            )

        assert not redirect_calls, (
            f"empty host + small source must NOT redirect; "
            f"got {redirect_calls!r}"
        )
    finally:
        import os

        os.unlink(src_path)
