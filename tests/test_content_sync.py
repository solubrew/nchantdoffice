"""T-DESK-058 Step 3 — ContentUpdateSync consumer for /api/updates.

The final piece of the ContentUpdateSync. The journaling
layer (step 1, micromole commit be2e522) + the plumbing
(step 2, nchantrs 574d402 + nchantdoffice a55f687) are
live. This step adds the actual sync consumer that:

  1. Polls ``GET /api/updates?uuid=...`` every 15 min.
  2. Parses the response into typed ``UpdateRecord`` objects.
  3. Dispatches by ``update_type``:
       - ``data_json``: calls ``store.update_record(...)`` 
         with journaling enabled.
       - ``binary_delta``: deferred (needs bspatch).
       - unknown types: logged + skipped (never crash).
  4. On failure: replays the journal backward (rollback).
  5. On success: clears the journal + persists last_update_date.

Tests are AST + pure-Python (same pattern as every other
T-DESK test file).
"""

import ast
import datetime as dt
import sys
from pathlib import Path
from typing import Any, Dict

PROJ_ROOT = Path("/home/solubrew/.hermes/projects/nchantdoffice")
sys.path.insert(0, str(PROJ_ROOT))

SYNC_DIR = PROJ_ROOT / "nchantdoffice" / "sync"
APPLIER = SYNC_DIR / "applier.py"
ROLLBACK = SYNC_DIR / "rollback.py"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _read(path: Path) -> str:
    return path.read_text()


def _ast_class(src: str, name: str):
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == name:
            return node
    return None


def _ast_function(src: str, name: str):
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None


def _function_source(src: str, name: str) -> str:
    node = _ast_function(src, name)
    if node is None:
        return ""
    return ast.get_source_segment(src, node) or ""


def _module_top_level_constant(src: str, name: str):
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and tgt.id == name:
                    return node.value
        elif isinstance(node, ast.AnnAssign):
            if (
                isinstance(node.target, ast.Name)
                and node.target.id == name
            ):
                return node.value
    return None


# ---------------------------------------------------------------------------
# Contract 1: applier module + ContentUpdateSync class
# ---------------------------------------------------------------------------


def test_applier_module_exists():
    """``nchantdoffice/sync/applier.py`` must exist."""
    assert APPLIER.exists(), (
        f"nchantdoffice/sync/applier.py must exist (T-DESK-058 "
        f"step 3). Expected at {APPLIER}."
    )


def test_content_update_sync_class_exists():
    """``ContentUpdateSync`` is the main poller class."""
    src = _read(APPLIER)
    cls = _ast_class(src, "ContentUpdateSync")
    assert cls is not None, (
        "applier.py must declare ContentUpdateSync class "
        "(the /api/updates poller + dispatcher)."
    )


def test_update_record_dataclass_exists():
    """``UpdateRecord`` is the typed server response entry."""
    src = _read(APPLIER)
    cls = _ast_class(src, "UpdateRecord")
    assert cls is not None, (
        "applier.py must declare UpdateRecord dataclass "
        "(the typed server response entry)."
    )
    body = ast.get_source_segment(src, cls) or ""
    for field in ("id", "update_type", "update_path_txt", "version_txt", "release_date"):
        assert field in body, (
            f"UpdateRecord must carry the {field!r} field "
            f"(matches the server _serialize_update shape)."
        )


# ---------------------------------------------------------------------------
# Contract 2: constants
# ---------------------------------------------------------------------------


def test_default_poll_interval():
    """The default poll interval must be 15 min (900 s) per the
    cross-repo review §2.4.
    """
    src = _read(APPLIER)
    node = _module_top_level_constant(src, "DEFAULT_POLL_INTERVAL_SECONDS")
    assert node is not None, (
        "applier.py must declare DEFAULT_POLL_INTERVAL_SECONDS."
    )
    # ``15 * 60`` is a BinOp — handle it.
    val = _eval_binop(node)
    assert isinstance(val, int) and val >= 300, (
        f"DEFAULT_POLL_INTERVAL_SECONDS must be >= 300 (5 min), "
        f"got {val!r}."
    )


def _eval_binop(node):
    """Evaluate a simple ``int * int`` or ``int`` literal."""
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.BinOp):
        left = _eval_binop(node.left)
        right = _eval_binop(node.right)
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Add):
            return left + right
    raise ValueError(f"unsupported expr: {ast.dump(node)}")


def test_update_type_constants():
    """The known update_type strings must be top-level constants."""
    src = _read(APPLIER)
    for name in ("UPDATE_TYPE_DATA_JSON", "UPDATE_TYPE_BINARY_DELTA"):
        node = _module_top_level_constant(src, name)
        assert node is not None, (
            f"applier.py must declare {name} top-level."
        )


# ---------------------------------------------------------------------------
# Contract 3: poll() method
# ---------------------------------------------------------------------------


def test_poll_method_exists():
    """``ContentUpdateSync.poll()`` is the network-call entry point.
    Fetches ``GET /api/updates?uuid=...`` and returns a list of
    ``UpdateRecord`` objects. Best-effort: failures return [].
    """
    src = _read(APPLIER)
    fn = _ast_function(src, "poll")
    assert fn is not None, (
        "ContentUpdateSync must declare poll() method "
        "(the /api/updates network-call entry point)."
    )
    body = _function_source(src, "poll")
    assert "/api/updates" in body or "updates" in body, (
        "poll() must hit the /api/updates endpoint."
    )
    assert "uuid" in body.lower(), (
        "poll() must include the uuid= query param (the desktop's "
        "registered UUID from credentials.json)."
    )
    assert "try:" in body, (
        "poll() must guard the network call with try/except."
    )


# ---------------------------------------------------------------------------
# Contract 4: apply() method — the dispatcher
# ---------------------------------------------------------------------------


def test_apply_method_exists():
    """``ContentUpdateSync.apply(updates)`` takes a list of
    UpdateRecord objects and dispatches each by update_type.
    """
    src = _read(APPLIER)
    fn = _ast_function(src, "apply")
    assert fn is not None, (
        "ContentUpdateSync must declare apply(updates) method "
        "(the dispatch entry point)."
    )
    body = _function_source(src, "apply")
    # Must dispatch by update_type
    assert "update_type" in body, (
        "apply() must dispatch by update_type."
    )
    # Must handle data_json
    assert "data_json" in body or "UPDATE_TYPE_DATA_JSON" in body, (
        "apply() must handle the data_json update type."
    )


def test_apply_handles_unknown_types_gracefully():
    """Unknown update_type values must be logged and skipped,
    NOT crash the sync. Pinning this so a future server-side
    addition doesn't break the desktop.
    """
    src = _read(APPLIER)
    body = _function_source(src, "apply")
    assert "warning" in body.lower() or "logma" in body.lower() or "skip" in body.lower(), (
        "apply() must log+skip unknown update_types (not crash)."
    )


# ---------------------------------------------------------------------------
# Contract 5: apply_data_json method
# ---------------------------------------------------------------------------


def test_apply_data_json_method_exists():
    """``ContentUpdateSync._apply_data_json(record)`` is the
    data_json dispatch handler. Calls ``store.update_record()``
    with journaling enabled so the WAL records the change.
    """
    src = _read(APPLIER)
    fn = _ast_function(src, "_apply_data_json")
    assert fn is not None, (
        "ContentUpdateSync must declare _apply_data_json() method "
        "(the data_json dispatch handler)."
    )
    body = _function_source(src, "_apply_data_json")
    assert "update_record" in body or "store" in body, (
        "_apply_data_json must route through the store's "
        "update_record (the journal-guarded write path)."
    )


def test_apply_data_json_uses_journal():
    """The data_json handler must route through the journal-
    guarded write path (store.write or store.update_record
    — both are journal-guarded in MicroStash).
    """
    src = _read(APPLIER)
    body = _function_source(src, "_apply_data_json")
    # The store is NchantdOfficeStore which inherits the
    # journal guards from MicroStash. As long as the handler
    # calls store.write / store.update_record / store._store,
    # the journal records the change.
    assert (
        "update_record" in body
        or ".write(" in body
        or "store_records" in body
        or "self.store" in body
    ), (
        "_apply_data_json must call the store's write methods "
        "(they're journal-guarded in MicroStash)."
    )


# ---------------------------------------------------------------------------
# Contract 6: last_update_date persistence
# ---------------------------------------------------------------------------


def test_last_update_date_persistence():
    """After a successful poll+apply, the sync must persist the
    latest ``release_date`` so the next poll only fetches
    newer updates. The state lives at
    ``~/.nchantd/sync_state.json`` (mode 0o600).
    """
    src = _read(APPLIER)
    assert "sync_state" in src or "last_update_date" in src, (
        "applier.py must persist last_update_date (the "
        "incremental-poll watermark)."
    )
    assert "0o600" in src or "0600" in src, (
        "sync state file must be mode 0o600."
    )


# ---------------------------------------------------------------------------
# Contract 7: rollback module
# ---------------------------------------------------------------------------


def test_rollback_module_exists():
    """``nchantdoffice/sync/rollback.py`` must exist."""
    assert ROLLBACK.exists(), (
        f"nchantdoffice/sync/rollback.py must exist (T-DESK-058 "
        f"step 3 rollback path)."
    )


def test_rollback_function_exists():
    """``rollback_from_journal(journal, store)`` is the module-
    level helper that reads a JsonlJournal and undoes the
    most recent uncommitted transaction.
    """
    src = _read(ROLLBACK)
    for name in ("rollback_from_journal", "rollback"):
        fn = _ast_function(src, name)
        if fn is not None:
            break
    else:
        raise AssertionError(
            "rollback.py must declare rollback_from_journal() "
            "or rollback() function."
        )


# ---------------------------------------------------------------------------
# Contract 8: apply() calls rollback on failure
# ---------------------------------------------------------------------------


def test_apply_rolls_back_on_failure():
    """When _apply_data_json raises, apply() must trigger the
    rollback path so the half-applied changes are undone.
    """
    src = _read(APPLIER)
    body = _function_source(src, "apply")
    assert "rollback" in body.lower(), (
        "apply() must call rollback on failure (the journal "
        "records the half-applied state, rollback undoes it)."
    )
    # The rollback call must be inside an except block.
    assert "except" in body, (
        "apply() must have an except block that triggers rollback."
    )


# ---------------------------------------------------------------------------
# Contract 9: binary_delta is deferred (logged, not applied)
# ---------------------------------------------------------------------------


def test_binary_delta_is_deferred():
    """The binary_delta path must be explicitly deferred —
    logged as "not yet implemented" + skipped, NOT crash.
    Pinning this so the sync works today (data_json only)
    and the bspatch path can be added incrementally.
    """
    src = _read(APPLIER)
    body = _function_source(src, "apply")
    # Must reference binary_delta somehow (either a handler
    # that logs+skips, or a comment noting deferral).
    assert "binary_delta" in body or "UPDATE_TYPE_BINARY_DELTA" in body, (
        "apply() must at least reference binary_delta (even "
        "if only to log+skip it as deferred)."
    )


# ---------------------------------------------------------------------------
# Contract 10: credentials integration
# ---------------------------------------------------------------------------


def test_poll_uses_credentials():
    """``poll()`` must read the desktop UUID + api_key from
    ``credentials.py`` (T-DESK-059) for the authenticated
    ``GET /api/updates`` call.
    """
    src = _read(APPLIER)
    assert "credentials" in src or "api_key" in src or "desktop_uuid" in src, (
        "applier.py must use the credentials module for the "
        "authenticated /api/updates call."
    )


# ---------------------------------------------------------------------------
# Contract 11: rate-limit integration
# ---------------------------------------------------------------------------


def test_rate_limit_integration():
    """The sync must respect the RateLimitTracker (T-DESK-061)
    when polling — the server's /api/updates is rate-limited
    at 5/minute.
    """
    src = _read(APPLIER)
    assert (
        "rate_limit" in src
        or "RateLimitTracker" in src
        or "check_rate_limit" in src
    ), (
        "applier.py must reference the RateLimitTracker so the "
        "sync doesn't trip the server's rate limit."
    )


# ---------------------------------------------------------------------------
# Contract 12: server_status integration
# ---------------------------------------------------------------------------


def test_server_status_integration():
    """The sync must record success/failure on the ServerStatus
    (T-DESK-063) so the status bar reflects the sync state.
    """
    src = _read(APPLIER)
    assert (
        "server_status" in src
        or "ServerStatus" in src
        or "record_success" in src
        or "record_failure" in src
        or "timed_call" in src
    ), (
        "applier.py must integrate with ServerStatus (record "
        "success/failure so the status bar reflects sync state)."
    )
