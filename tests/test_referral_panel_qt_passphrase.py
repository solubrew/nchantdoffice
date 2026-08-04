"""TDD tests for the desktop passphrase dialog for the Referral Panel.

The desktop must NEVER trigger the CLI ``getpass`` prompt. The
panel must offer a masked Qt dialog instead, and the dialog must
be reachable through the panel's own configuration surface so
host code can override it in tests.
"""


def test_referral_panel_prompts_for_passphrase_via_qt_dialog(monkeypatch):
    """When the panel instantiates ``PyKeyStore`` for the
    affiliate_id lookup, it must supply a ``passphrase_prompt``
    callback that opens a Qt masked-entry dialog instead of
    letting PyKeyStore call ``getpass.getpass``.

    The test asserts the panel wires the callback (not whether
    Qt is reachable in the headless env) by patching
    ``pycurity.pykey.PyKeyStore`` (the canonical import site the
    panel uses) to capture the ``passphrase_prompt`` argument
    and return a sentinel value.
    """
    sentinel = "sentinel-from-desktop-dialog"
    captured = {}

    class _StubKeyStore:
        def __init__(self, **kwargs):
            captured.update(kwargs)
            self._passphrase_input = sentinel

        def get(self, service):
            return {"public_id": sentinel}

    import pycurity.pykey as pykey
    monkeypatch.setattr(pykey, "PyKeyStore", _StubKeyStore)

    import nchantdoffice.widgets.config.referral_panel as rp
    panel = rp.NchantdOfficeReferralPanel.__new__(rp.NchantdOfficeReferralPanel)
    panel.user = None
    panel.referral_code = None
    panel.share_urls = {}
    panel.earnings_data = {}
    panel.invitations_remaining = 0
    panel.config = type("Cfg", (), {"dikt": {}})()
    panel.app = type("App", (), {"model": type("M", (), {"codex": type("C", (), {"init_config": lambda self, d: None})()})()})()
    # The production panel accepts a ``_pykey_prompt`` override
    # for testability. Without a Qt event loop the production
    # fallback dialog returns "", which is the canonical "no
    # key" signal PyKeyStore already handles. The test asserts
    # the override path is honoured when supplied.
    panel._pykey_prompt = lambda: sentinel
    panel._load_or_generate_code()
    assert captured.get("passphrase_prompt") is not None, (
        "referral_panel must pass a passphrase_prompt callback to "
        "PyKeyStore so the desktop can supply a Qt dialog value."
    )
    result = captured["passphrase_prompt"]()
    assert result == sentinel, (
        f"Qt prompt callback should yield the sentinel value, got {result!r}"
    )
