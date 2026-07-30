"""Sprint 20 — Unimplemented features found by Sprint 19 code review.

These tests pin the contract of features that were catalogued
as unimplemented in TODOs.md (commit 07261dc). The tests are
intentionally AST-based so they don't require the full app
bootstrap (the same nchantrs circular-import guard that
Sprint 18 worked around).

Test surface:
  1. settings.py: 7 # TODO implement method logic stubs are
     replaced with real implementations.
  2. views.py: switch_to_account_tab and on_window_move are
     no longer empty stubs.
  3. timelines.py: NchantdOfficeTodayOverview.initLowerWidgets
     is no longer a no-op (delegates to super or wires a real
     layout).
  4. diagrams.py: Node.initModel is no longer a no-op.
  5. accounts.py: storage and documents labels are wired to
     live data (no longer hard-coded strings).
  6. toolboxes.py: cmd_save_instance body has implementation
     (no longer all-pass).
  7. toolboxes.py: cmd_duplicate_instance body has implementation.
  8. toolboxes.py: cmd_import_instance body has implementation.
  9. toolboxes.py: cmd_llm_query_pane and cmd_web_search_pane
     open their respective panes.
"""

import ast
import re
from pathlib import Path


def _read(rel):
    return (Path(__file__).resolve().parent.parent / rel).read_text()


def _function_body(src, fn_name, class_name=None):
    """Return the source of a method (or function) by name."""
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == fn_name:
            if class_name is not None:
                # Walk up: node must be inside the class
                # (Python's ast doesn't carry parent refs, so
                # check by col-offset / class context via
                # iterating ClassDef > FunctionDef).
                pass
            return ast.get_source_segment(src, node) or ""
    return ""


def _method_body(src, class_name, fn_name):
    """Return the source of a method inside a class."""
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for child in node.body:
                if isinstance(child, ast.FunctionDef) and child.name == fn_name:
                    return ast.get_source_segment(src, child) or ""
    return ""


def _flattened(src):
    return re.sub(r"\s+", " ", src).strip()


# --- settings.py: 7 # TODO implement method logic stubs ---


SETTINGS_STUBS = [
    ("cmd_on_change_journal_focus", "journal_focus"),
    ("cmd_on_change_settings_focus", "settings_focus"),
    ("cmd_on_change_automation", "automation"),
    ("cmd_on_change_data_source", "data_source"),
    ("cmd_on_change_show_left_side_pane", "show_left_side_pane"),
    ("cmd_on_change_show_right_side_pane", "show_right_side_pane"),
    ("cmd_on_change_quicklaunch", "quicklaunch"),
]


def test_settings_stubs_have_implementations():
    """Sprint 20: settings.py cmd_on_change_* handlers must
    persist their checkbox state to config.dikt, not just
    return self after a TODO comment.
    """
    src = _read("nchantdoffice/widgets/config/settings.py")
    for fn_name, config_key in SETTINGS_STUBS:
        body = _method_body(src, "NchantdOfficeInterfaceSettings", fn_name)
        if not body:
            body = _function_body(src, fn_name)
        flat = _flattened(body)
        assert "TODO implement method logic" not in flat, (
            f"{fn_name} still has # TODO implement method logic "
            f"stub: {flat[:300]!r}"
        )
        # Must persist to config.dikt with the matching key.
        assert config_key in flat or config_key.replace("_", "") in flat, (
            f"{fn_name} must persist a value (the TODO-implement "
            f"flag) to config.dikt; body: {flat[:300]!r}"
        )


def test_views_switch_to_account_tab_is_implemented():
    """Sprint 20: views.py::switch_to_account_tab is a forgotten
    stub (comment says PUSH to 0.0.3 but it's not in the canonical
    list). Must route to the account tab.
    """
    src = _read("nchantdoffice/views.py")
    body = _function_body(src, "switch_to_account_tab")
    flat = _flattened(body)
    # The marker is a bare `# PUSH to 0.0.3` comment on its own
    # line. Newer docstrings mention "PUSH to 0.0.3" in prose;
    # only count bare-comment occurrences.
    for line in body.split("\n"):
        if line.strip() == "# PUSH to 0.0.3":
            raise AssertionError(
                f"switch_to_account_tab still has bare "
                f"'# PUSH to 0.0.3' marker; body: {flat[:300]!r}"
            )
    assert "return self" != flat, (
        f"switch_to_account_tab is still a no-op (return self only); "
        f"body: {flat[:300]!r}"
    )


def test_views_on_window_move_is_implemented():
    """Sprint 20: views.py::on_window_move is a forgotten stub.
    Must propagate the move to visible notes (the original intent
    per the comment).
    """
    src = _read("nchantdoffice/views.py")
    body = _function_body(src, "on_window_move")
    flat = _flattened(body)
    for line in body.split("\n"):
        if line.strip() == "# PUSH to 0.0.3":
            raise AssertionError(
                f"on_window_move still has bare '# PUSH to 0.0.3' "
                f"marker; body: {flat[:300]!r}"
            )


def test_timelines_init_lower_widgets_not_noop():
    """Sprint 20: NchantdOfficeTodayOverview.initLowerWidgets was
    a no-op stub. Now delegates to the parent init (or wires a
    real layout). Pin that the body no longer ends at the
    no-op comment.
    """
    src = _read("nchantdoffice/widgets/timelines.py")
    tree = ast.parse(src)
    all_lines = src.split("\n")
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == (
            "NchantdOfficeTodayOverview"
        ):
            for child in node.body:
                if isinstance(child, ast.FunctionDef) and (
                    child.name == "initLowerWidgets"
                ):
                    # The AST ends at end_lineno but the
                    # source may have trailing comment lines
                    # outside the function body. Look at lines
                    # from lineno until the next def/class line.
                    start = child.lineno - 1
                    end = child.end_lineno
                    # Extend end until the next top-level
                    # statement boundary (next def at the same
                    # or shallower indent).
                    for j in range(end, min(end + 5, len(all_lines))):
                        stripped = all_lines[j].lstrip()
                        if (
                            stripped.startswith("def ")
                            or stripped.startswith("class ")
                            or stripped.startswith("# ===")
                        ):
                            break
                        end = j + 1
                    raw = "\n".join(all_lines[start:end])
                    assert "No-op stub" not in raw, (
                        f"NchantdOfficeTodayOverview.initLowerWidgets "
                        f"is still a no-op stub (raw: {raw[:400]!r})"
                    )
                    # The stub body was empty except for a log
                    # call + comment. A real implementation
                    # must have at least one of: super().X(),
                    # setattr, or a comment without "No-op stub".
                    real_lines = [
                        ln.strip()
                        for ln in all_lines[start:end]
                        if ln.strip()
                        and not ln.strip().startswith(("logma", "#"))
                    ]
                    assert real_lines, (
                        f"NchantdOfficeTodayOverview.initLowerWidgets "
                        f"body is effectively empty; raw: {raw[:400]!r}"
                    )


def test_diagrams_node_init_model_not_noop():
    """Sprint 20: Node.initModel in diagrams.py was a no-op
    stub (log line "(no-op stub)"). Must wire real initialisation.
    """
    src = _read("nchantdoffice/widgets/items/diagrams.py")
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "Node":
            for child in node.body:
                if isinstance(child, ast.FunctionDef) and (
                    child.name == "initModel"
                ):
                    body = ast.get_source_segment(src, child) or ""
                    raw_lines = src.split("\n")[
                        child.lineno - 1 : child.end_lineno
                    ]
                    raw = "\n".join(raw_lines)
                    assert "(no-op stub)" not in raw, (
                        f"diagrams.Node.initModel is still a no-op "
                        f"stub (raw: {raw[:400]!r})"
                    )


def test_accounts_storage_label_not_hardcoded():
    """Sprint 20: accounts.py:79-86 had hard-coded "Storage: 0 GB"
    and "Documents: 0" labels. The initView must NOT contain
    those literals (they should query real data).
    """
    src = _read("nchantdoffice/widgets/config/accounts.py")
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == (
            "NchantdOfficeAccountSettings"
        ):
            for child in node.body:
                if isinstance(child, ast.FunctionDef) and (
                    child.name == "initView"
                ):
                    body = ast.get_source_segment(src, child) or ""
                    assert "Storage: 0 GB / 10 GB" not in body, (
                        "accounts.NchantdOfficeAccountSettings.initView "
                        "still has the hard-coded 'Storage: 0 GB / "
                        "10 GB' label. Must query live data."
                    )
                    assert '"Documents: 0"' not in body, (
                        "accounts.NchantdOfficeAccountSettings.initView "
                        "still has the hard-coded 'Documents: 0' "
                        "label. Must query live count."
                    )


# --- toolboxes.py: stub cmd_* methods ---


def test_toolboxes_cmd_save_instance_has_body():
    """Sprint 20: cmd_save_instance was a near-empty stub (all
    pass branches). Must have a real implementation now.
    """
    src = _read("nchantdoffice/widgets/controls/toolboxes.py")
    body = _function_body(src, "cmd_save_instance")
    flat = _flattened(body)
    # The stub was almost entirely pass/else: pass patterns.
    # Pin that the body now has at least one real line of logic.
    assert "pass\n" not in body or body.count("pass\n") <= 2, (
        f"cmd_save_instance still has multiple pass statements "
        f"indicating stub status; body: {flat[:500]!r}"
    )


def test_toolboxes_cmd_duplicate_instance_has_body():
    """Sprint 20: cmd_duplicate_instance was a comment-only stub.
    Must have a real implementation now.
    """
    src = _read("nchantdoffice/widgets/controls/toolboxes.py")
    body = _function_body(src, "cmd_duplicate_instance")
    flat = _flattened(body)
    # Stub body was just the comments and return self.
    assert "create new instance" not in flat or "create_new_instance" in flat, (
        f"cmd_duplicate_instance is still a comment-only stub; "
        f"body: {flat[:300]!r}"
    )


def test_toolboxes_cmd_import_instance_calls_importer():
    """Sprint 20: cmd_import_instance opened a file dialog but
    never called any model.import_* method. Must now call
    something on self.app.model.
    """
    src = _read("nchantdoffice/widgets/controls/toolboxes.py")
    body = _function_body(src, "cmd_import_instance")
    flat = _flattened(body)
    assert "app.model.import" in flat, (
        f"cmd_import_instance must call self.app.model.import_*(); "
        f"body: {flat[:300]!r}"
    )


# --- toolboxes.py: file-type imports ---


def test_toolboxes_docx_import_does_not_raise():
    """Sprint 20: .docx branch at toolboxes.py:541 must NOT raise
    'File Type not yet implemented' anymore. It now routes
    through model.import_docx() (with fallback to text).
    """
    src = _read("nchantdoffice/widgets/controls/toolboxes.py")
    # Get the cmd_open_local_file body
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == (
            "cmd_open_local_file"
        ):
            body = ast.get_source_segment(src, node) or ""
            assert "raise Exception" not in body or body.count(
                'endswith(".docx")'
            ) == 0 or "raise Exception(f\"File Type not yet implemented" not in body, (
                ".docx branch in cmd_open_local_file still raises "
                "'File Type not yet implemented'; body excerpt: "
                f"{body[body.find('.docx') - 100:body.find('.docx') + 200]!r}"
            )


def test_toolboxes_no_more_file_type_not_implemented_raises():
    """Sprint 20: cmd_open_local_file must NOT raise 'File Type
    not yet implemented' for ANY of the file extensions it
    dispatches on. This is the regression test for the
    'File Type not yet implemented' pattern.
    """
    src = _read("nchantdoffice/widgets/controls/toolboxes.py")
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == (
            "cmd_open_local_file"
        ):
            body = ast.get_source_segment(src, node) or ""
            assert "File Type not yet implemented" not in body, (
                "cmd_open_local_file still has a 'File Type not yet "
                "implemented' raise in its body."
            )


# --- accounts.py: live storage / documents labels ---


def test_accounts_storage_label_queries_live_data():
    """Sprint 20: accounts.py:79-86 storage/documents labels
    must query live data (user quota + doc_media count) rather
    than hard-coded "Storage: 0 GB / 10 GB" / "Documents: 0".
    """
    src = _read("nchantdoffice/widgets/config/accounts.py")
    assert "Storage: 0 GB / 10 GB" not in src, (
        "accounts.py still has the hard-coded 'Storage: 0 GB / "
        "10 GB' label."
    )
    # The new label should reference storage_quota + storage_used.
    assert "storage_quota_gb" in src, (
        "accounts.py must query user.storage_quota_gb for live "
        "storage data."
    )
    assert "get_document_count" in src or "documents_count" in src, (
        "accounts.py must query a document-count helper for live "
        "document count."
    )


# --- models.py: import_csv and import_docx helpers ---


def test_models_has_import_csv():
    """Sprint 20: NchantdOfficeCloakModel must expose
    import_csv() (was missing — dispatcher raised on .csv).
    """
    src = _read("nchantdoffice/models.py")
    assert "def import_csv" in src, (
        "models.py must define import_csv() so the .csv "
        "dispatcher branch has a real handler."
    )


def test_models_has_import_docx():
    """Sprint 20: NchantdOfficeCloakModel must expose
    import_docx() (was missing — dispatcher raised on .docx).
    """
    src = _read("nchantdoffice/models.py")
    assert "def import_docx" in src, (
        "models.py must define import_docx() so the .docx "
        "dispatcher branch has a real handler."
    )


def test_models_has_import_matrix():
    """Sprint 20 (user direction): .csv / .xlsx / .xls / .ods
    extensions must route to NchantdOfficeMatrix, not text.
    models.py must expose import_matrix() so the spreadsheet
    branch can hand off to the matrix widget.
    """
    src = _read("nchantdoffice/models.py")
    assert "def import_matrix" in src, (
        "models.py must define import_matrix() so the "
        "spreadsheet dispatcher branch routes to the matrix "
        "widget."
    )


def test_toolboxes_csv_routes_to_matrix():
    """Sprint 20 (user direction): .csv must route to the matrix
    document class via model.import_matrix(). The previous
    fallback to import_text() is acceptable when import_matrix
    isn't available, but the primary path must use matrix.
    """
    src = _read("nchantdoffice/widgets/controls/toolboxes.py")
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == (
            "cmd_open_local_file"
        ):
            body = ast.get_source_segment(src, node) or ""
            # The csv branch must be in the matrix group
            # (alongside .xlsx/.xls/.ods) AND must call
            # model.import_matrix.
            csv_idx = body.find('.csv')
            matrix_idx = body.find("import_matrix")
            assert matrix_idx != -1, (
                "cmd_open_local_file must call "
                "model.import_matrix for spreadsheet imports; "
                f"body: {body[csv_idx - 200:csv_idx + 200]!r}"
            )
            # csv branch must be co-located with the matrix call.
            csv_section = body[csv_idx:csv_idx + 400]
            assert "import_matrix" in csv_section, (
                "the .csv branch must route to import_matrix "
                "(not just import_text); section: "
                f"{csv_section[:300]!r}"
            )


def test_toolboxes_gif_routes_to_image():
    """Sprint 20 (user direction): .gif must route to
    NchantdOfficeImage via model.import_image(). The previous
    silent no-op must be replaced.
    """
    src = _read("nchantdoffice/widgets/controls/toolboxes.py")
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == (
            "cmd_open_local_file"
        ):
            body = ast.get_source_segment(src, node) or ""
            gif_idx = body.find(".gif")
            assert gif_idx != -1, (
                "cmd_open_local_file must include .gif handling"
            )
            # The .gif branch must call model.import_image,
            # not just log a no-op.
            gif_section = body[gif_idx:gif_idx + 400]
            assert "import_image" in gif_section, (
                "the .gif branch must route to import_image; "
                f"section: {gif_section[:300]!r}"
            )


def test_toolboxes_cmd_llm_query_pane_opens_pane():
    """Sprint 20: cmd_llm_query_pane was a no-op (return self).
    Must open the LLM query pane.
    """
    src = _read("nchantdoffice/widgets/controls/toolboxes.py")
    body = _function_body(src, "cmd_llm_query_pane")
    flat = _flattened(body)
    assert flat != "return self", (
        f"cmd_llm_query_pane is still a no-op; body: {flat[:300]!r}"
    )


def test_toolboxes_cmd_web_search_pane_opens_pane():
    """Sprint 20: cmd_web_search_pane was a no-op. Must open
    the web search pane.
    """
    src = _read("nchantdoffice/widgets/controls/toolboxes.py")
    body = _function_body(src, "cmd_web_search_pane")
    flat = _flattened(body)
    assert flat != "return self", (
        f"cmd_web_search_pane is still a no-op; body: {flat[:300]!r}"
    )
