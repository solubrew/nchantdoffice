"""T-NEW-051/052 regression test: ``app_action`` schema must include
``position_int`` and ``lookup()`` must survive DB errors gracefully.

The live crash (testing-report_20260804.md):

  1. ``ORDER BY position_int`` fails because the column doesn't exist.
  2. ``Action show_pane_left Lookup Config is Empty`` — because the
     query failure leaves the action cache empty and ``lookup()``
     raises.

The fix:
1. ``position_int`` column added to ``app_action`` table in both
   ``nchantdoffice/_data_/models.yaml`` and
   ``nchantrs/models/_data_/applicationmodels.yaml``.
2. ``lookup()`` wraps the DB read in try/except.
"""

import yaml


def test_app_action_has_position_int_nchantdoffice():
    """nchantdoffice app_action schema must include position_int."""
    with open("nchantdoffice/_data_/models.yaml") as f:
        data = yaml.safe_load(f)

    tables = data["NchantdOfficeCloakModel"]["dstruct"]["database"]["objects"]["table"]
    app_action = tables["app_action"]
    col_names = [c["name"] for c in app_action["columns"]]
    assert "position_int" in col_names, (
        f"app_action columns must include 'position_int'. Got: {col_names}"
    )


def test_app_action_has_position_int_nchantrs():
    """nchantrs app_action schema must include position_int."""
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
    assert "position_int" in col_names, (
        f"app_action columns must include 'position_int'. Got: {col_names}"
    )


def test_lookup_wraps_db_read_in_try_except():
    """Source-level assertion: ``lookup()`` must have a try/except
    around the DB read so a query error doesn't crash toolbar init."""
    import inspect
    from nchantrs.utilities import utils

    src = inspect.getsource(utils.lookup)
    assert "except Exception" in src, (
        "lookup() must wrap the DB read in try/except (T-NEW-052)"
    )
    assert "app_action DB read failed" in src, (
        "lookup() must log the DB read failure (T-NEW-052)"
    )
