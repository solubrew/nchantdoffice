"""T-NEW-116 regression: Jupyter server default working
directory is ``~/Documents/NchantdLibrary`` when no file
path is set.

The Jupyter subprocess is spawned with a ``cwd`` so the
notebook tree shown in the Jupyter webview starts at the
user's library directory. The current code uses
``dirname(self.file_path)`` when a file is set, but falls
back to the bare process cwd (``os.getcwd()``) when no
file is set -- which on a packaged install may be the
application bundle directory (read-only, no notebooks).

The fix: when no file is set, use
``~/Documents/NchantdLibrary`` (created if missing).
When set, keep the existing
``dirname(self.file_path)`` behaviour.

Tests (TDD):
- behavioural (no file_path): the computed cwd is
  ``~/Documents/NchantdLibrary``, and the directory
  exists after the call.
- behavioural (file_path set): the cwd is the file's
  parent directory (unchanged).
- source-level: the cwd-resolution branch reads from
  ``get_user_library_dir()`` (or equivalent) and creates
  the directory when missing.
"""
import inspect
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

# T-NEW-074 Task 9: keep Qt on the headless offscreen platform
# before any PySide6 import so the integration test does not
# need a real display.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402

from nchantdoffice.widgets.documents.workbooks.notebooks import (
    NchantdOfficeNotebook,
)


def test_default_cwd_is_nchantd_library_dir(tmp_path, monkeypatch):
    """T-NEW-116: when ``self.file_path`` is None or empty,
    the Jupyter server's cwd is the user's NchantdLibrary
    directory under ~/Documents, created if missing.
    """
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    # expanduser("~") also reads $HOME; patch os.path.expanduser
    # to resolve to our tmp_path so the test is hermetic.
    import os.path as _ospath
    monkeypatch.setattr(_ospath, "expanduser", lambda p: str(tmp_path) if p == "~" else _ospath.expanduser(p))
    fake_home = tmp_path
    expected_dir = fake_home / "Documents" / "NchantdLibrary"

    notebook = NchantdOfficeNotebook.__new__(NchantdOfficeNotebook)
    notebook.file_path = None

    cwd = notebook._resolve_jupyter_cwd()
    assert Path(cwd) == expected_dir, (
        f"default Jupyter cwd must be {expected_dir} (T-NEW-116); "
        f"got {cwd}"
    )
    assert expected_dir.exists(), (
        f"default Jupyter cwd must be created if missing "
        f"(T-NEW-116); {expected_dir} does not exist"
    )


def test_file_path_cwd_is_file_parent(tmp_path):
    """T-NEW-116 (regression guard): when a file path IS
    set, the cwd is the file's parent directory (unchanged
    from the pre-fix behaviour).
    """
    real_file = tmp_path / "subdir" / "notebook.ipynb"
    real_file.parent.mkdir(parents=True)
    real_file.write_text("{}")

    notebook = NchantdOfficeNotebook.__new__(NchantdOfficeNotebook)
    notebook.file_path = str(real_file)

    cwd = notebook._resolve_jupyter_cwd()
    assert Path(cwd) == real_file.parent, (
        f"file-path Jupyter cwd must be the file's parent "
        f"(T-NEW-116 backward compat); got {cwd}"
    )


def test_resolve_jupyter_cwd_helper_exists():
    """T-NEW-116 (source-level): the resolution logic must
    be in a dedicated helper (not inlined in
    ``start_jupyter_server``) so the test can drive it
    without instantiating a Jupyter subprocess.
    """
    assert hasattr(NchantdOfficeNotebook, "_resolve_jupyter_cwd"), (
        "NchantdOfficeNotebook must define _resolve_jupyter_cwd "
        "(T-NEW-116)."
    )


def test_start_jupyter_server_calls_resolve_cwd(monkeypatch, tmp_path):
    """T-NEW-116 (source-level): the start_jupyter_server
    branch must delegate to ``_resolve_jupyter_cwd`` rather
    than inlining the cwd resolution (which would defeat
    the test).
    """
    src = inspect.getsource(NchantdOfficeNotebook.start_jupyter_server)
    assert "_resolve_jupyter_cwd" in src, (
        f"start_jupyter_server must call _resolve_jupyter_cwd "
        f"(T-NEW-116). Got:\n{src[:3000]}"
    )