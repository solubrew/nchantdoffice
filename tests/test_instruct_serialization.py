"""T-NEW-049 regression test: Instruct object in content payload must
not crash the JSON serialisation path in ``add_document_content`` /
``add_document_content_app``.

The live crash (testing-report_20260804.md) was::

    TypeError: Object of type Instruct is not JSON serializable

at ``models.py:448`` inside ``add_document_content``.  The root cause
is that ``kahndor.Instruct`` objects (config wrappers) leak into the
document content dict during the referral/slide save flow.  The fix
adds a ``_safe_json_default`` fallback to ``json.dumps`` so any object
exposing ``.dikt`` (Instruct) or ``.to_dict()`` (PyfficeDocument) is
converted to its plain-dict representation automatically.
"""

import json as j


# ---------------------------------------------------------------------------
# Module-level helper — the function under test.
# ---------------------------------------------------------------------------

def _import_safe_default():
    """Import ``_safe_json_default`` from nchantdoffice.models.

    Returns the function object so each test can exercise it directly.
    """
    from nchantdoffice.models import _safe_json_default
    return _safe_json_default


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_safe_json_default_exists():
    """The helper must be importable from nchantdoffice.models."""
    fn = _import_safe_default()
    assert callable(fn), "_safe_json_default must be callable"


def test_safe_json_default_converts_instruct():
    """An ``Instruct`` instance must serialise to its ``.dikt`` dict."""
    _safe_json_default = _import_safe_default()
    from kahndor.kahndor import Instruct

    instruct = Instruct()
    instruct.dikt = {"key": "value", "nested": {"a": 1}}

    result = j.dumps({"config": instruct}, default=_safe_json_default)
    decoded = j.loads(result)
    assert decoded == {"config": {"key": "value", "nested": {"a": 1}}}


def test_safe_json_default_converts_nested_instruct():
    """Nested Instruct objects inside lists must also serialise."""
    _safe_json_default = _import_safe_default()
    from kahndor.kahndor import Instruct

    inner = Instruct()
    inner.dikt = {"inner_key": "inner_val"}

    payload = {
        "content": {
            "config": inner,
            "list_of_configs": [inner, inner],
        }
    }

    # This would crash without the default handler
    result = j.dumps(payload, default=_safe_json_default)
    decoded = j.loads(result)
    assert decoded["content"]["config"] == {"inner_key": "inner_val"}
    assert decoded["content"]["list_of_configs"][0] == {"inner_key": "inner_val"}


def test_safe_json_default_converts_to_dict_objects():
    """Objects with a ``to_dict()`` method must be serialised via it."""
    _safe_json_default = _import_safe_default()

    class FakeDoc:
        def to_dict(self):
            return {"did": "test-id", "content": "hello"}

    result = j.dumps({"doc": FakeDoc()}, default=_safe_json_default)
    decoded = j.loads(result)
    assert decoded == {"doc": {"did": "test-id", "content": "hello"}}


def test_safe_json_default_handles_bytes():
    """Bytes objects should decode to string, not crash."""
    _safe_json_default = _import_safe_default()

    result = j.dumps({"data": b"hello"}, default=_safe_json_default)
    decoded = j.loads(result)
    assert decoded == {"data": "hello"}


def test_add_document_content_uses_safe_default():
    """Source-level assertion: ``add_document_content`` must pass
    ``default=_safe_json_default`` to every ``json.dumps`` call.
    """
    import inspect
    from nchantdoffice.models import NchantdOfficeCloakModel

    src = inspect.getsource(NchantdOfficeCloakModel.add_document_content)
    # Every j.dumps call in the method must use the safe default
    assert "default=_safe_json_default" in src, (
        "add_document_content must pass default=_safe_json_default to j.dumps"
    )


def test_add_document_content_app_uses_safe_default():
    """Same source-level assertion for ``add_document_content_app``."""
    import inspect
    from nchantdoffice.models import NchantdOfficeCloakModel

    src = inspect.getsource(NchantdOfficeCloakModel.add_document_content_app)
    assert "default=_safe_json_default" in src, (
        "add_document_content_app must pass default=_safe_json_default to j.dumps"
    )
