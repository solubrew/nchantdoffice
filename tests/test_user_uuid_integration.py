"""T-NEW-042 (DESK-0): NchantdOfficeUser integration as canonical UUID.

Pins the contract that:
  - user_config.py has a `user.uuid` field in DEFAULTS
  - user_config.py exposes get_user_uuid() / set_user_uuid()
  - NchantdOfficeUser has a persist_uuid() method
  - NchantdOfficeCloak.__init__ instantiates self.user = NchantdOfficeUser(self)
  - NchantdOfficeCloak.__init__ replaces hardcoded application_NCD
    with the user's actual UUID (self.user.uuid)
  - The UUID is stable across launches (read from user config,
    generated on first launch, persisted thereafter)
  - No env vars used (T-NEW-070 hard-break)
"""
import ast
from pathlib import Path

USERS = Path(
    "/home/solubrew/.hermes/projects/nchantdoffice/"
    "nchantdoffice/utilities/users.py"
)
USER_CONFIG = Path(
    "/home/solubrew/.hermes/projects/nchantdoffice/"
    "nchantdoffice/utilities/user_config.py"
)
CLOAK = Path(
    "/home/solubrew/.hermes/projects/nchantdoffice/"
    "nchantdoffice/nchantdoffice.py"
)


def _read(p):
    return p.read_text()


def test_user_config_has_user_uuid_field():
    """user_config.py DEFAULTS must include user.uuid (default: '' — first-launch)."""
    src = _read(USER_CONFIG)
    assert '"user"' in src or "'user'" in src, (
        "user_config.py DEFAULTS must include a 'user' section"
    )
    assert '"uuid"' in src or "'uuid'" in src, (
        "user_config.py DEFAULTS must include 'user.uuid' field "
        "(empty by default — generated on first launch)"
    )


def test_user_config_exposes_get_user_uuid():
    src = _read(USER_CONFIG)
    tree = ast.parse(src)
    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "get_user_uuid":
            found = True
            break
    assert found, "user_config.get_user_uuid() must exist"


def test_user_config_exposes_set_user_uuid():
    src = _read(USER_CONFIG)
    tree = ast.parse(src)
    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "set_user_uuid":
            found = True
            break
    assert found, "user_config.set_user_uuid() must exist"


def test_nchantd_office_user_has_persist_uuid_method():
    """NchantdOfficeUser must have persist_uuid() that reads/writes user_config."""
    src = _read(USERS)
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "NchantdOfficeUser":
            body = ast.unparse(node)
            assert "def persist_uuid" in body, (
                "NchantdOfficeUser.persist_uuid() must exist "
                "(T-NEW-042 DESK-0)"
            )
            assert "user_config" in body, (
                "persist_uuid() must use user_config (T-NEW-070 hard-break)"
            )
            return
    assert False, "NchantdOfficeUser class must exist"


def test_cloak_instantiates_nchantd_office_user():
    """NchantdOfficeCloak.__init__ must instantiate NchantdOfficeUser
    (currently it's never instantiated — that's the 'weak use')."""
    src = _read(CLOAK)
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "NchantdOfficeCloak":
            body = ast.unparse(node)
            assert "NchantdOfficeUser" in body, (
                "NchantdOfficeCloak must instantiate NchantdOfficeUser "
                "(T-NEW-042 DESK-0 — currently never instantiated)"
            )
            assert "self.user" in body or "self._user" in body, (
                "The user singleton must be stored as self.user "
                "so other components can read it"
            )
            return
    assert False, "NchantdOfficeCloak class must exist"


def test_cloak_no_longer_has_hardcoded_application_ncd():
    """The hardcoded application_NCD UUID must be replaced by
    the per-install UUID from NchantdOfficeUser.uuid."""
    src = _read(CLOAK)
    assert '"40c94efb-d374-437f-a48b-3c6b843fd110"' not in src, (
        "NchantdOfficeCloak must NOT hardcode application_NCD — "
        "use the per-install UUID from NchantdOfficeUser.uuid "
        "(T-NEW-042 DESK-0)"
    )
    # But the field must still exist (it's referenced elsewhere)
    assert "application_NCD" in src, (
        "application_NCD field must remain (just sourced from "
        "the user UUID, not a constant)"
    )


def test_users_no_env_var_reads():
    """users.py must not read env vars (T-NEW-070 hard-break)."""
    src = _read(USERS)
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute):
                if func.attr in ("getenv", "environ"):
                    raise AssertionError(
                        f"users.py must not use os.{func.attr} "
                        f"(line {node.lineno})"
                    )


# ============================================================================
# T-NEW-042b: NchantdUser parent.device requirement fix
# ============================================================================
# Original DESK-0 wired NchantdOfficeUser(self) into
# NchantdOfficeCloak.__init__, but didn't satisfy the
# parent's requirement that parent.device exist.
# NchantdUser.__init__ reads `self.parent.device.user` at
# line 65 — without setting self.device, the attribute
# access raises AttributeError ("'NchantdOfficeCloak'
# object has no attribute 'device'").
#
# Fix: set self.device = Device() BEFORE
# NchantdOfficeUser(self) is constructed. The Device
# class is from pycurity.pyvice and has a no-arg
# constructor that sets `.user`, `.mac`, `.home`, etc.


def test_cloak_sets_self_device_before_user_construction():
    """NchantdOfficeCloak.__init__ must set self.device
    BEFORE NchantdOfficeUser(self) is constructed.

    Without this, the parent's NchantdUser.__init__ tries
    to read `self.parent.device.user` and crashes with
    AttributeError (real-world bug reported 2026-08-11 14:21).
    """
    src = _read(CLOAK)
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.ClassDef)
            and node.name == "NchantdOfficeCloak"
        ):
            body = ast.unparse(node)
            # Find the position of self.device = ... and of
            # NchantdOfficeUser(self) — the device assignment
            # must come first.
            device_pos = body.find("self.device")
            user_pos = body.find("NchantdOfficeUser(self)")
            assert device_pos != -1, (
                "NchantdOfficeCloak must set self.device "
                "(T-NEW-042b — Device() instance for NchantdUser parent)"
            )
            assert user_pos != -1, (
                "NchantdOfficeCloak must instantiate NchantdOfficeUser"
            )
            assert device_pos < user_pos, (
                f"self.device must be set BEFORE NchantdOfficeUser(self) "
                f"(device at position {device_pos}, user at {user_pos}). "
                f"Otherwise parent NchantdUser.__init__ crashes on "
                f"`self.parent.device.user`."
            )
            assert "Device" in body, (
                "self.device must be set to a Device() instance "
                "(from pycurity.pyvice)"
            )
            return
    assert False, "NchantdOfficeCloak class must exist"
