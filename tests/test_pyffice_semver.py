"""Sprint 16 — T-NEW-005 (item 2) Pyffice semver regression test.

Per user correction (2026-07-29): the three version-control
objects are:

  1. ``doc_media`` / ``doc_media_content`` integer-based
     per-save iteration counter.
  2. **Pyffice class semver** — each PyfficeDocument subclass
     has its OWN serialization version (because each can
     have a different ``to_dict()`` schema). Implemented as
     ``SERIALIZATION_VERSION`` (a 3-tuple) on each class, with
     ``PyfficeUnit.to_dict`` recording
     ``meta_data["schema_version"]`` so the receiving side
     can dispatch upgrade paths per class.
  3. Primary instance registry (``app_instance`` table) —
     tracks locations/metadata of OTHER app instances.

This test pins #2.
"""


def test_pyffice_exposes_version_and_version_info():
    """T-NEW-005 (item 2) package-level: ``pyffice.__version__``
    and ``pyffice.__version_info__`` are both exposed and
    consistent with each other (the string is the dotted
    form of the tuple).
    """
    import pyffice

    assert hasattr(pyffice, "__version__"), (
        "pyffice must expose __version__ (the canonical "
        "semver string) so callers can compare versions."
    )
    assert hasattr(pyffice, "__version_info__"), (
        "pyffice must expose __version_info__ as a 3-tuple "
        "for programmatic comparison."
    )
    assert isinstance(pyffice.__version_info__, tuple)
    assert len(pyffice.__version_info__) == 3, (
        f"__version_info__ must be (MAJOR, MINOR, PATCH); "
        f"got {pyffice.__version_info__}"
    )
    expected = ".".join(str(p) for p in pyffice.__version_info__)
    assert pyffice.__version__ == expected, (
        f"__version__ ({pyffice.__version__!r}) must equal "
        f"the dotted form of __version_info__ ({expected!r})."
    )


def test_each_pyffice_class_has_own_serialization_version():
    """T-NEW-005 (item 2) per-class: each PyfficeDocument
    subclass declares its own ``SERIALIZATION_VERSION`` (a
    3-tuple) so receivers can dispatch upgrade paths per
    class (a Diagram's schema can change independently of a
    Spreadsheet's).
    """
    from pyffice.document import (
        PyfficeDocument,
        PyfficeDocumentManager,
        PyfficeDeque,
        PyfficeUnit,
    )

    classes = [
        PyfficeUnit,
        PyfficeDocument,
        PyfficeDocumentManager,
        PyfficeDeque,
    ]
    # Plus the document-type subclasses the user named
    # explicitly: PyfficeScript, PyfficeMatrix, PyfficeImage,
    # etc. Some live in modules that may not be importable
    # in the sasquatch test env, so we look them up by name
    # via the package's public surface where possible.
    try:
        from pyffice.script.script import PyfficeScript

        classes.append(PyfficeScript)
    except ImportError:
        pass
    try:
        from pyffice.matrix.matrix import PyfficeMatrix

        classes.append(PyfficeMatrix)
    except ImportError:
        pass
    try:
        from pyffice.notebooks.notebooks import PyfficeNotebook

        classes.append(PyfficeNotebook)
    except ImportError:
        pass
    try:
        from pyffice.diagrams.diagrams import PyfficeDiagram

        classes.append(PyfficeDiagram)
    except ImportError:
        pass
    try:
        from pyffice.filesystems.filesystems import PyfficeFileSystem

        classes.append(PyfficeFileSystem)
    except ImportError:
        pass

    for cls in classes:
        assert hasattr(cls, "SERIALIZATION_VERSION"), (
            f"{cls.__name__} must declare SERIALIZATION_VERSION."
        )
        version = cls.SERIALIZATION_VERSION
        assert isinstance(version, tuple), (
            f"{cls.__name__}.SERIALIZATION_VERSION must be a "
            f"3-tuple; got {type(version).__name__}."
        )
        assert len(version) == 3, (
            f"{cls.__name__}.SERIALIZATION_VERSION must be "
            f"(MAJOR, MINOR, PATCH); got {version}."
        )
        for p in version:
            assert isinstance(p, int) and p >= 0, (
                f"{cls.__name__}.SERIALIZATION_VERSION entries "
                f"must be non-negative integers; got {version}."
            )


def test_pyffice_unit_to_dict_records_schema_version():
    """T-NEW-005 (item 2): ``PyfficeUnit.to_dict`` records
    ``meta_data["schema_version"]`` (per-class) and
    ``meta_data["semver"]`` (package-level) so the receiving
    side knows BOTH which Pyffice version produced the
    payload AND which class schema to dispatch.
    """
    from pyffice.document import PyfficeUnit
    import pyffice

    unit = PyfficeUnit()
    unit.did = "test-id"
    unit.name = "hello"
    unit.content = "world"

    payload = unit.to_dict()
    assert "meta_data" in payload, (
        "PyfficeUnit.to_dict must include the meta_data dict."
    )

    semver = payload["meta_data"].get("semver")
    assert semver == pyffice.__version__, (
        f"meta_data['semver'] must equal pyffice.__version__ "
        f"({pyffice.__version__!r}); got {semver!r}."
    )

    schema_version = payload["meta_data"].get("schema_version")
    assert schema_version == list(PyfficeUnit.SERIALIZATION_VERSION), (
        f"meta_data['schema_version'] must equal the list form "
        f"of {PyfficeUnit.__name__}.SERIALIZATION_VERSION "
        f"({list(PyfficeUnit.SERIALIZATION_VERSION)}); got "
        f"{schema_version!r}."
    )


def test_pyffice_document_to_dict_records_its_own_schema_version():
    """T-NEW-005 (item 2): the per-class schema version is
    looked up on ``self.SERIALIZATION_VERSION``, not on the
    package's ``__version__`` — so a subclass can move to a
    new schema version independently of its siblings.
    """
    from pyffice.document import PyfficeDocument, PyfficeDocumentManager

    doc = PyfficeDocument()
    doc.name = "sample"
    payload = doc.to_dict()
    assert (
        payload["meta_data"]["schema_version"]
        == list(PyfficeDocument.SERIALIZATION_VERSION)
    )

    mgr = PyfficeDocumentManager()
    mgr.name = "manager"
    payload = mgr.to_dict()
    assert (
        payload["meta_data"]["schema_version"]
        == list(mgr.SERIALIZATION_VERSION)
        == list(PyfficeDocumentManager.SERIALIZATION_VERSION)
    )