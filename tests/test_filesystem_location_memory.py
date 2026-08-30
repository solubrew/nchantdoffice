"""T-NEW-068 — Tests for NchantdFilesystem location memory.

Per `testing-report_20260810.md` lines 26–27:
> "NchantdFilesystem still no maintaining location to
> return back to ... need to nailed down the interface inputs".

This file pins 6 invariants the T-NEW-068 implementation
promises:

  1. ``test_resolve_restore_path_returns_last_root`` —
     ``_resolve_restore_path()`` returns
     ``config.dikt["last_root_path"]`` when set.

  2. ``test_resolve_restore_path_falls_back_to_doc`` —
     when ``last_root_path`` is unset, returns
     ``self.document.file_path``.

  3. ``test_resolve_restore_path_ignores_empty_string`` —
     whitespace-only or empty ``last_root_path`` is treated
     as unset.

  4. ``test_resolve_restore_path_ignores_non_string`` —
     non-string ``last_root_path`` (e.g. None, int) is
     treated as unset.

  5. ``test_cmd_set_root_persists_last_root_path`` —
     ``cmd_set_root(path=...)`` writes the path to
     ``config.dikt["last_root_path"]``.

  6. ``test_cmd_go_home_accepts_explicit_path_kwarg`` —
     ``cmd_go_home(path="/custom")`` sets
     ``fs_tree.current_level_path`` and persists the path.

Tests use the ``_filesystem_class_or_skip()`` helper that
handles the upstream qpandas metaclass conflict (same
pattern as ``test_filesystem_persistence.py``). Each test
exercises a single method/helper — never the full
``initView`` chain, which triggers a Qt widget tree
construction that segfaults in the sasquatch venv.
"""

import os
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
import pytest

# Helper so item-assignment persists (MagicMock absorbs it as a call).
class _DictLike(dict):
    pass


class _FsTree:
    def __init__(self, current_level_path):
        self.current_level_path = current_level_path

PROJ_ROOT = Path("/home/solubrew/.hermes/projects/nchantdoffice")
sys.path.insert(0, str(PROJ_ROOT))

import nchantdoffice.models  # noqa: F401


def _filesystem_class_or_skip():
    """Return the filesystem class, or skip the test if the upstream
    qpandas metaclass conflict prevents the import chain.
    Same helper as test_filesystem_persistence.py.
    """
    try:
        from nchantdoffice.widgets.documents.managers.filesystems import (
            NchantdOfficeFileSystem,
        )
    except TypeError as exc:
        if "metaclass conflict" in str(exc):
            pytest.skip(
                "qpandas metaclass conflict blocks NchantdOfficeFileSystem "
                "import — upstream nchantrs issue, not test code",
                allow_module_level=False,
            )
        raise
    return NchantdOfficeFileSystem


def _bare_filesystem(
    last_root_path=None, document_file_path="/initial/file/path",
):
    """Build a bare NchantdOfficeFileSystem instance with mocked
    internal state. Mirrors the test pattern in
    test_filesystem_persistence.py — we don't call __init__
    because that requires a Qt parent.

    ``config.dikt`` is a ``_DictLike`` (subclass of dict) so that
    item-assignment ``dikt["key"] = value`` persists — MagicMock
    absorbs item-assignments as method calls and the value is lost.
    ``fs_tree`` uses ``_FsTree`` for the same reason.
    """
    fs_cls = _filesystem_class_or_skip()
    fs = fs_cls.__new__(fs_cls)
    fs.config = SimpleNamespace(dikt=_DictLike())
    if last_root_path is not None:
        fs.config.dikt["last_root_path"] = last_root_path
    fs.file_path = document_file_path
    from unittest.mock import MagicMock
    fs.fs_tree = MagicMock()
    fs.fs_tree.set_root = MagicMock()
    # Use _FsTree for current_level_path so assignment persists
    # (MagicMock.attr = value is lost on the next access).
    fs.fs_tree.__dict__["current_level_path"] = "/initial/current_level_path"
    fs.custom_root = None  # required by cmd_go_home guard
    fs.document = MagicMock()
    fs.document.file_path = fs.file_path
    fs.document.open_file = MagicMock()
    fs.populate_document = MagicMock()
    fs.app = None  # guard super().save() from accessing self.app.view
    fs._save = MagicMock()  # stub out the internal save impl
    # Bind the real impls we want to call directly.
    fs._resolve_restore_path = (
        fs_cls._resolve_restore_path.__get__(fs)
    )
    fs.show_tree = fs_cls.show_tree.__get__(fs)
    fs.cmd_set_root = fs_cls.cmd_set_root.__get__(fs)
    fs.cmd_go_home = fs_cls.cmd_go_home.__get__(fs)
    return fs


# ---------------------------------------------------------------------------
# _resolve_restore_path tests
# ---------------------------------------------------------------------------


def test_resolve_restore_path_returns_last_root():
    """``_resolve_restore_path`` returns last_root_path when set."""
    fs = _bare_filesystem(last_root_path="/home/user/projects")
    result = fs._resolve_restore_path()
    assert result == "/home/user/projects", (
        f"expected '/home/user/projects'; got {result!r}"
    )


def test_resolve_restore_path_falls_back_to_doc():
    """When last_root_path is unset, returns document.file_path."""
    fs = _bare_filesystem(last_root_path=None)
    result = fs._resolve_restore_path()
    assert result == "/initial/file/path", (
        f"expected document.file_path='/initial/file/path'; got {result!r}"
    )


def test_resolve_restore_path_ignores_empty_string():
    """Whitespace-only last_root_path is treated as unset."""
    fs = _bare_filesystem(last_root_path="   ")
    result = fs._resolve_restore_path()
    assert result == "/initial/file/path", (
        f"whitespace-only last_root_path should be ignored; "
        f"got {result!r}"
    )


def test_resolve_restore_path_ignores_non_string():
    """Non-string last_root_path (None, int, list) is treated as unset."""
    for bad_value in [None, 42, ["path"], {"k": "v"}]:
        fs = _bare_filesystem(last_root_path=bad_value)
        result = fs._resolve_restore_path()
        assert result == "/initial/file/path", (
            f"non-string last_root_path={bad_value!r} should fall back; "
            f"got {result!r}"
        )


# ---------------------------------------------------------------------------
# cmd_set_root / cmd_go_home / show_tree tests
# ---------------------------------------------------------------------------


def test_cmd_set_root_persists_last_root_path():
    """``cmd_set_root(path=...)`` writes to config.dikt["last_root_path"]."""
    fs = _bare_filesystem()
    fs.cmd_set_root(path="/srv/data/2024")
    assert fs.config.dikt["last_root_path"] == "/srv/data/2024", (
        f"cmd_set_root should persist path; got "
        f"{fs.config.dikt.get('last_root_path')!r}"
    )


def test_cmd_set_root_no_path_uses_current_level_path():
    """cmd_set_root() with no args falls back to fs_tree.current_level_path."""
    fs = _bare_filesystem()
    fs.fs_tree.current_level_path = "/current/dir"
    fs.cmd_set_root()
    assert fs.config.dikt["last_root_path"] == "/current/dir"


def test_cmd_go_home_accepts_explicit_path_kwarg():
    """cmd_go_home(path=...) navigates to the explicit path."""
    fs = _bare_filesystem()
    fs.cmd_go_home(path="/custom/home")
    assert fs.fs_tree.current_level_path == "/custom/home", (
        f"current_level_path should be '/custom/home'; got "
        f"{fs.fs_tree.current_level_path!r}"
    )
    assert fs.config.dikt["last_root_path"] == "/custom/home", (
        f"last_root_path should be '/custom/home' after cmd_go_home; "
        f"got {fs.config.dikt.get('last_root_path')!r}"
    )


def test_cmd_go_home_default_uses_expanduser_home():
    """cmd_go_home() with no args defaults to expanduser('~')."""
    fs = _bare_filesystem()
    fs.cmd_go_home()
    expected = os.path.expanduser("~")
    assert fs.fs_tree.current_level_path == expected, (
        f"default cmd_go_home should use expanduser('~')={expected!r}; "
        f"got {fs.fs_tree.current_level_path!r}"
    )


def test_show_tree_persists_last_root_path():
    """Direct show_tree(path=...) calls also persist last_root_path."""
    fs = _bare_filesystem()
    fs.show_tree("/explicit/dir")
    assert fs.config.dikt["last_root_path"] == "/explicit/dir", (
        f"show_tree should persist last_root_path; got "
        f"{fs.config.dikt.get('last_root_path')!r}"
    )
