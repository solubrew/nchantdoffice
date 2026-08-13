"""T-NEW-051/052 — ``app_action`` schema resilience + lookup() try/except.

History:
- T-NEW-051 originally added ``position_int`` to ``app_action`` in both
  nchantdoffice and nchantrs. The user found the column was breaking
  live behavior (queries that did not expect it, ordering by accident,
  migration friction) and removed it from nchantrs gamma
  (commit f70a885, 2026-08-09). The nchantdoffice side mirrored this
  by reverting the column in commit 46b0cb8.
- T-NEW-052 resilient ``lookup()`` stays — the DB read in
  ``nchantrs.utilities.utils.lookup`` is wrapped in try/except so a
  query failure (missing column or otherwise) doesn't crash toolbar
  init. This is independent of the column question and keeps the
  toolbar init alive across schema drift.

This file is now two tests:
1. ``app_action`` schema MUST NOT have ``position_int`` (in both repos).
2. ``nchantrs.utilities.utils.lookup`` MUST wrap the DB read in try/except.
"""

import yaml


def test_app_action_lacks_position_int_nchantdoffice():
    """nchantdoffice app_action schema must NOT include position_int.

    Reverted in 46b0cb8. The column was added in 7ee2f65 then reverted
    because live behavior broke. The ordering-by-position_int contract
    was the wrong forcing function; other tables (doc_tab, document_tab)
    retain the column where it actually drives a display order.
    """
    with open("nchantdoffice/_data_/models.yaml") as f:
        data = yaml.safe_load(f)

    tables = data["NchantdOfficeCloakModel"]["dstruct"]["database"]["objects"]["table"]
    app_action = tables["app_action"]
    col_names = [c["name"] for c in app_action["columns"]]
    assert "position_int" not in col_names, (
        f"app_action columns must NOT include 'position_int' (reverted in 46b0cb8). "
        f"Got: {col_names}"
    )


def test_app_action_lacks_position_int_nchantrs():
    """nchantrs app_action schema must NOT include position_int.

    Removed from nchantrs gamma in commit f70a885 (2026-08-09). Live
    behavior broke when the column was present; the user removed it.
    """
    import os
    nchantrs_yaml = os.path.join(
        os.path.dirname(__import__('nchantrs').__file__),
        "models", "_data_", "applicationmodels.yaml"
    )
    with open(nchantrs_yaml) as f:
        data = yaml.safe_load(f)

    # Navigate to the app_action table definition
    tables = data["NchantdPantiesModel"]["dstruct"]["database"]["objects"]["table"]
    app_action = tables["app_action"]
    col_names = [c["name"] for c in app_action["columns"]]
    assert "position_int" not in col_names, (
        f"app_action columns must NOT include 'position_int' (removed in f70a885). "
        f"Got: {col_names}"
    )


def test_lookup_wraps_db_read_in_try_except():
    """Source-level assertion: ``lookup()`` must have a try/except
    around the DB read so a query error doesn't crash toolbar init.

    T-NEW-052 stays — independent of the position_int removal. The
    resilient lookup is the actual fix that kept toolbar init alive
    when the schema column was first added across repos.
    """
    import inspect
    from nchantrs.utilities import utils

    src = inspect.getsource(utils.lookup)
    assert "except Exception" in src, (
        "lookup() must wrap the DB read in try/except (T-NEW-052)"
    )
    assert "app_action DB read failed" in src, (
        "lookup() must log the DB read failure (T-NEW-052)"
    )
