"""T-NEW-163 — models.py PUSH-to-0.0.3 no-op stubs are fixed.

The 2026-08-18 PUSH-to-0.0.3 marker sweep filed T-NEW-163 covering three
genuinely forgotten no-op stubs in ``NchantdOfficeCloakModel``:

    - ``get_node_name`` — returns ``self`` (the Sprint-20 anti-pattern)
    - ``get_tab_name``  — returns ``self``
    - ``get_urls(tag)`` — returns ``[]``

None of these are called anywhere in the codebase (grep-verified), so
they're genuinely orphaned stubs, not APIs with intentional contracts.
The tests pin a real implementation contract:

    - ``get_node_name`` returns the name of ``self.current_node``
    - ``get_tab_name`` returns the name of ``self.current_tab``
    - ``get_urls(tag)`` returns a list (not the model ``self``)

This file is the AST-style regression scaffold: each test uses
``NchantdOfficeCloakModel.__new__`` to skip ``__init__`` (mirroring
``test_get_view_link.py``) and stubs ``self.current_node`` /
``self.current_tab`` to keep the assertions deterministic.
"""

from pandas import DataFrame


def _bare_model():
    """Create a minimal NchantdOfficeCloakModel without running __init__."""
    from nchantdoffice.models import NchantdOfficeCloakModel

    return NchantdOfficeCloakModel.__new__(NchantdOfficeCloakModel)


def test_get_node_name_is_not_a_self_returning_stub():
    """``get_node_name`` must NOT return ``self`` — the PUSH 0.0.3 stub did."""
    model = _bare_model()
    result = model.get_node_name()
    assert result is not model, (
        "get_node_name must not return self — it was a PUSH 0.0.3 stub "
        f"(returned {type(result).__name__})"
    )


def test_get_node_name_returns_current_node_name_string():
    """``get_node_name`` returns the name of ``self.current_node``."""
    model = _bare_model()
    # Inject a stub current_node that mimics the row-shape downstream
    # code expects (a Series-like with a ``name_txt`` column).
    node_row = {"nid_txt": "nid-1", "name_txt": "research"}
    model.current_node = type("Row", (), node_row)()

    name = model.get_node_name()
    assert name == "research", (
        f"get_node_name must return current_node.name_txt, got {name!r}"
    )
    assert isinstance(name, str), (
        f"get_node_name must return str, got {type(name).__name__}"
    )


def test_get_node_name_returns_none_when_no_current_node():
    """``get_node_name`` returns ``None`` when ``current_node`` is unset."""
    model = _bare_model()
    # No current_node attribute set at all.
    name = model.get_node_name()
    assert name is None, (
        f"get_node_name must return None when current_node is missing, "
        f"got {name!r}"
    )


def test_get_tab_name_is_not_a_self_returning_stub():
    """``get_tab_name`` must NOT return ``self`` — the PUSH 0.0.3 stub did."""
    model = _bare_model()
    result = model.get_tab_name()
    assert result is not model, (
        "get_tab_name must not return self — it was a PUSH 0.0.3 stub "
        f"(returned {type(result).__name__})"
    )


def test_get_tab_name_returns_current_tab_name_string():
    """``get_tab_name`` returns the name of ``self.current_tab``."""
    model = _bare_model()
    tab_row = {"tid_txt": "tid-1", "name_txt": "scratch"}
    model.current_tab = type("Row", (), tab_row)()

    name = model.get_tab_name()
    assert name == "scratch", (
        f"get_tab_name must return current_tab.name_txt, got {name!r}"
    )
    assert isinstance(name, str), (
        f"get_tab_name must return str, got {type(name).__name__}"
    )


def test_get_tab_name_returns_none_when_no_current_tab():
    """``get_tab_name`` returns ``None`` when ``current_tab`` is unset."""
    model = _bare_model()
    name = model.get_tab_name()
    assert name is None, (
        f"get_tab_name must return None when current_tab is missing, "
        f"got {name!r}"
    )


def test_get_urls_returns_a_list_not_self():
    """``get_urls(tag)`` must return a list, not ``self`` (the stub)."""
    model = _bare_model()
    result = model.get_urls()
    assert result is not model, (
        "get_urls must not return self — it was a PUSH 0.0.3 stub"
    )
    assert isinstance(result, list), (
        f"get_urls must return list, got {type(result).__name__}"
    )


def test_get_urls_returns_empty_list_when_no_store():
    """``get_urls(tag)`` returns ``[]`` (not ``None``) when store is absent."""
    model = _bare_model()
    result = model.get_urls()
    # Defensive default: empty list, NOT None (callers can iterate without
    # None-checks). Mirrors the prior stub's [] return on the success path.
    assert result == [], (
        f"get_urls must return [] when no store, got {result!r}"
    )