"""T-NEW-158 -- Referral desktop passphrase guard: replace placeholder marker.

``widgets/config/referral_panel.py:395`` carries an
unnumbered `# T-NEW-XXX:` marker that the operator
documented against the canonical T-NEW-158 number. The
guard implementation is already in place
(``_qt_passphrase_prompt`` at referral_panel.py:453 +
``_pykey_prompt`` test sentinel): the marker is just
un-numbered.

This card pins the canonical T-NEW-158 number in the
source comment + the docstring so the umbrella audit and
T-NEW-026 cross-references resolve cleanly.

Sweep: just the marker replacement + the docstring
mention. No behaviour change.
"""

import ast
import re
from pathlib import Path

REFERRAL_PANEL_PATH = (
    Path(__file__).parents[1] / "nchantdoffice/widgets/config/referral_panel.py"
)


def test_t_new_xxx_marker_replaced():
    """The placeholder ``# T-NEW-XXX:`` marker is gone (or properly numbered)."""
    src_text = REFERRAL_PANEL_PATH.read_text()
    has_t_new_xxx = re.search(r"#\s*T-NEW-XXX\s*:", src_text) is not None
    assert not has_t_new_xxx, (
        f"referral_panel.py still has a `# T-NEW-XXX:` marker. "
        f"T-NEW-158 replaces it with the canonical number. "
        f"Audit found this at line 395 (the PyKeyStore "
        f"passphrase-prompt guard site)."
    )


def test_t_new_158_marker_present():
    """The canonical T-NEW-158 marker is present."""
    src_text = REFERRAL_PANEL_PATH.read_text()
    has_t_new_158 = "T-NEW-158" in src_text
    assert has_t_new_158, (
        "referral_panel.py should reference T-NEW-158 as the "
        "umbrella card for the Qt masked-entry passphrase "
        "guard. The implementation is in place; the marker "
        "needs the canonical number."
    )


def test_qt_passphrase_prompt_still_exists():
    """``_qt_passphrase_prompt`` helper is still defined (no regression)."""
    tree = ast.parse(REFERRAL_PANEL_PATH.read_text())
    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_qt_passphrase_prompt":
            found = True
            break
    assert found, (
        "_qt_passphrase_prompt must remain — the Qt "
        "QInputDialog.getText wrapper that prevents PyKeyStore's "
        "getpass fallback. T-NEW-158 is a doc-only card; "
        "no helper was removed."
    )
