"""T-NEW-050 regression test: ``get_links`` / ``get_view_link`` must
return a DataFrame, not ``self``.

The live crash (testing-report_20260803.md) was::

    AttributeError: 'NchantdOfficeStore' object has no attribute
    '_build_filter_config'

This happened because ``NchantdOfficeCloakModel.get_links`` was a
PUSH 0.0.3 stub returning ``self``, so ``get_view_link`` called
``.empty`` on the model object (not a DataFrame).

The fix:
1. ``NchantdOfficeCloakModel.get_links`` now delegates to
   ``self.store.get_links(...)`` and returns a DataFrame.
2. ``NchantdOfficeStore.get_view_link`` has a ``hasattr`` guard.
3. nchantrs' store ``get_links`` already uses ``_build_where_clause``
   (the renamed method) — fixed post-report.
"""

from pandas import DataFrame


def _bare_model():
    """Create a minimal NchantdOfficeCloakModel without running __init__."""
    from nchantdoffice.models import NchantdOfficeCloakModel
    model = NchantdOfficeCloakModel.__new__(NchantdOfficeCloakModel)
    return model


def test_get_links_is_not_a_stub():
    """``get_links`` must NOT return ``self`` — it should return a DataFrame."""
    model = _bare_model()
    result = model.get_links()
    assert result is not model, (
        "get_links must not return self — it was a PUSH 0.0.3 stub"
    )
    assert hasattr(result, "empty"), (
        f"get_links must return a DataFrame-like object, got {type(result)}"
    )


def test_get_links_accepts_filter_args():
    """``get_links`` must accept name/description/type_/tag/url/db kwargs."""
    import inspect
    from nchantdoffice.models import NchantdOfficeCloakModel

    sig = inspect.signature(NchantdOfficeCloakModel.get_links)
    params = list(sig.parameters.keys())
    assert "name" in params, f"get_links must accept 'name' kwarg, got {params}"
    assert "db" in params, f"get_links must accept 'db' kwarg, got {params}"


def test_get_links_delegates_to_store():
    """get_links must call self.store.get_links with the filter args."""
    model = _bare_model()

    captured = {}

    class FakeStore:
        def get_links(self, name=None, description=None, type_=None,
                      tag=None, url=None, db="db"):
            captured["name"] = name
            captured["description"] = description
            captured["type_"] = type_
            captured["tag"] = tag
            captured["url"] = url
            captured["db"] = db
            return DataFrame([{"url_ltxt": "https://example.com", "name_txt": "test"}])

    model.store = FakeStore()
    result = model.get_links(name="test", url="https://example.com")

    assert captured["name"] == "test"
    assert captured["url"] == "https://example.com"
    assert not result.empty
    assert result.iloc[0]["url_ltxt"] == "https://example.com"


def test_store_get_view_link_hasattr_guard():
    """``NchantdOfficeStore.get_view_link`` must guard df.empty with hasattr."""
    import inspect
    from nchantdoffice.models import NchantdOfficeStore

    src = inspect.getsource(NchantdOfficeStore.get_view_link)
    assert 'hasattr(df, "empty")' in src, (
        "get_view_link must guard df.empty with hasattr to avoid "
        "AttributeError when df is not a DataFrame"
    )


def test_store_get_view_link_exists():
    """NchantdOfficeStore must have a get_view_link method."""
    from nchantdoffice.models import NchantdOfficeStore
    assert hasattr(NchantdOfficeStore, "get_view_link"), (
        "NchantdOfficeStore must have get_view_link"
    )


def test_model_get_link_delegates_to_store():
    """``NchantdOfficeCloakModel.get_link`` must delegate to store."""
    model = _bare_model()

    class FakeStore:
        def get_view_link(self, name=None, **kwargs):
            return f"https://link-for-{name}"

    model.store = FakeStore()
    link = model.get_link("test-link")
    assert link == "https://link-for-test-link"
