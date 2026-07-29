"""Sprint 12 — T-NEW-013 PUSH 0.0.3 tag regression test.

User-stated directive (2026-07-29): the encrypt/decrypt feature
must be labelled with the PUSH 0.0.3 tag and documented as
deferred work. This test guards against accidentally removing
the marker when refactoring the cipher stubs.
"""

import ast
from pathlib import Path


def test_panes_documents_carries_push_003_on_cipher_stubs():
    """All four encode64/decode64/encrypt/decrypt methods in
    ``nchantdoffice/widgets/panes/documents.py`` must carry a
    ``# PUSH 0.0.3`` marker with the T-NEW-013 reference.
    """
    root = Path(__file__).resolve().parent.parent
    src = (root / "nchantdoffice/widgets/panes/documents.py").read_text()
    tree = ast.parse(src)

    methods = {"decode64", "decrypt", "encode64", "encrypt"}
    found = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in methods:
            body_src = ast.get_source_segment(src, node) or ""
            found[node.name] = body_src

    missing = methods - found.keys()
    assert not missing, f"Missing methods: {missing}"

    for name, body in found.items():
        assert "PUSH 0.0.3" in body, (
            f"NchantdOfficeDocument.{name}() must carry a '# PUSH "
            f"0.0.3' marker (T-NEW-013 deferred cipher integration). "
            f"Got body: {body!r}"
        )
        assert "T-NEW-013" in body, (
            f"NchantdOfficeDocument.{name}() must reference "
            f"T-NEW-013 in its # PUSH 0.0.3 marker."
        )

    # Methods are currently no-op stubs with a logma.warning —
    # ensure the body shape (logma.warning present, encode64/
    # decode64 do the base64 round-trip) is preserved.
    for name in ("decode64", "encode64"):
        assert "decode64(self.content).decode(\"utf-8\")" in found[name] or \
               "encode64(self.content.encode(\"utf-8\"))" in found[name]

    for name in ("decrypt", "encrypt"):
        assert "logma.warning(" in found[name], (
            f"{name}() must keep its logma.warning no-op stub."
        )
