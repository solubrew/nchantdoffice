"""Slim-ad layout ladder tests for NchantdOfficeAdTab.

The right-pane Ad tab picks its slim-ad layout (full / stack3 /
stack5) from the pane's current height via
``NchantdOfficeAdTab._ad_layout_for_height``. The default
docked-state layout is now **stack5** (5 compact boxes), up
from stack2 — the user has a tall right pane that wastes
vertical space with only 2 ads.

These tests pin the ladder (without importing PySide6 / the
full Qt stack — we parse the source file directly):

  - height >= 620   -> ``LAYOUT_STACK3``
  - 380 <= height < 620 -> ``LAYOUT_STACK5``
  - height < 380    -> ``LAYOUT_FULL``

Plus class-attribute presence (so a typo'd rename breaks the
build) and a check that ``initModel`` and ``initView`` no
longer default to ``LAYOUT_STACK2`` (regression guard — the
old default is exactly the bug the user reported).
"""
import ast
import sys
from pathlib import Path

import pytest

PROJ_ROOT = Path("/home/solubrew/.hermes/projects/nchantdoffice")
sys.path.insert(0, str(PROJ_ROOT))

BROWSERS = (
    PROJ_ROOT
    / "nchantdoffice"
    / "widgets"
    / "documents"
    / "atnrg"
    / "browsers.py"
)


def _read(path: Path) -> str:
    return path.read_text()


def _find_class(src: str, name: str):
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == name:
            return node
    return None


def _find_function(class_node, name: str):
    for node in class_node.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None


def _get_int_constant(class_node, name: str):
    """Read an ``X = 620`` assignment on the class body."""
    for node in class_node.body:
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if (
                    isinstance(tgt, ast.Name)
                    and tgt.id == name
                    and isinstance(node.value, ast.Constant)
                ):
                    return node.value.value
    return None


def _get_str_constant(class_node, name: str):
    for node in class_node.body:
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if (
                    isinstance(tgt, ast.Name)
                    and tgt.id == name
                    and isinstance(node.value, ast.Constant)
                ):
                    return node.value.value
    return None


def _function_source(class_node, name: str) -> str:
    fn = _find_function(class_node, name)
    if fn is None:
        return ""
    return ast.unparse(fn)


@pytest.fixture(scope="module")
def ad_tab_class_node():
    src = _read(BROWSERS)
    cls = _find_class(src, "NchantdOfficeAdTab")
    if cls is None:
        pytest.fail(
            "NchantdOfficeAdTab class missing from "
            f"{BROWSERS} — did the file get refactored?"
        )
    return cls


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


def test_stack5_layout_constant_present(ad_tab_class_node):
    """LAYOUT_STACK5 = 'stack5' must be a class attr."""
    val = _get_str_constant(ad_tab_class_node, "LAYOUT_STACK5")
    assert val == "stack5", (
        "NchantdOfficeAdTab.LAYOUT_STACK5 must be the string "
        f"'stack5'; got {val!r}"
    )


def test_stack5_min_height_present(ad_tab_class_node):
    """STACK5_MIN_HEIGHT = 380 must be declared."""
    val = _get_int_constant(ad_tab_class_node, "STACK5_MIN_HEIGHT")
    assert val == 380, (
        "STACK5_MIN_HEIGHT must be 380px (the floor below which "
        "the slim pane is too short for 5 boxes); got {val!r}"
    )


def test_stack3_min_height_unchanged(ad_tab_class_node):
    """STACK3_MIN_HEIGHT stays at 620 — stack3 still needs a tall pane."""
    val = _get_int_constant(ad_tab_class_node, "STACK3_MIN_HEIGHT")
    assert val == 620, (
        "STACK3_MIN_HEIGHT must remain 620px — the tall-pane "
        f"threshold; got {val!r}"
    )


# ---------------------------------------------------------------------------
# _ad_layout_for_height ladder
# ---------------------------------------------------------------------------


def test_layout_ladder_picks_stack3_for_tall_pane(ad_tab_class_node):
    """height >= 620 -> 'stack3'."""
    src = _function_source(ad_tab_class_node, "_ad_layout_for_height")
    assert "STACK3_MIN_HEIGHT" in src, (
        "_ad_layout_for_height must consult STACK3_MIN_HEIGHT "
        "for the tall-pane stack3 pick."
    )
    assert "LAYOUT_STACK3" in src


def test_layout_ladder_picks_stack5_for_mid_pane(ad_tab_class_node):
    """380 <= height < 620 -> 'stack5' (NEW default docked layout)."""
    src = _function_source(ad_tab_class_node, "_ad_layout_for_height")
    assert "STACK5_MIN_HEIGHT" in src, (
        "_ad_layout_for_height must consult STACK5_MIN_HEIGHT "
        "for the mid-pane stack5 pick — the new default layout."
    )
    assert "LAYOUT_STACK5" in src


def test_layout_ladder_falls_back_to_full(ad_tab_class_node):
    """height < 380 -> 'full' (single hero)."""
    src = _function_source(ad_tab_class_node, "_ad_layout_for_height")
    assert "LAYOUT_FULL" in src
    assert src.count("return self.LAYOUT_FULL") >= 1


# ---------------------------------------------------------------------------
# Default-layout regression guard
# ---------------------------------------------------------------------------


def test_initModel_defaults_to_stack5_not_stack2(ad_tab_class_node):
    """initModel must default the URL to stack5, not stack2.

    Regression guard: the user-reported bug was that the docked
    Ad tab only showed 2 ad boxes (stack2). initModel pinned
    that default — now it must pin stack5 instead.
    """
    src = _function_source(ad_tab_class_node, "initModel")
    assert "_ad_url_for_layout(self.LAYOUT_STACK5)" in src, (
        "initModel must default the URL to LAYOUT_STACK5 "
        "(the new dense layout for the docked Ad tab)."
    )
    assert "_ad_url_for_layout(self.LAYOUT_STACK2)" not in src, (
        "initModel must NOT default to LAYOUT_STACK2 — that "
        "was the bug producing only 2 ad boxes."
    )


def test_initView_defaults_to_stack5_not_stack2(ad_tab_class_node):
    """initView's _current_layout seed must be stack5."""
    src = _function_source(ad_tab_class_node, "initView")
    assert "self._current_layout = self.LAYOUT_STACK5" in src, (
        "initView must seed _current_layout with LAYOUT_STACK5 "
        "so the first resize settles on the new dense layout."
    )
    assert "self._current_layout = self.LAYOUT_STACK2" not in src


def test_initView_compares_against_stack5(ad_tab_class_node):
    """The `desired != LAYOUT_STACK2` reload guard must now
    compare against LAYOUT_STACK5 (otherwise the first tick
    after initView reloads stack2 unnecessarily)."""
    src = _function_source(ad_tab_class_node, "initView")
    assert "desired != self.LAYOUT_STACK5" in src, (
        "initView must guard `desired != self.LAYOUT_STACK5` "
        "so the reload only fires when the actual resize picks "
        "something other than the new default."
    )
    assert "desired != self.LAYOUT_STACK2" not in src
