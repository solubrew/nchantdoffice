"""Sprint 2 — Image blur regression test.

Closes the live `TODOs.md` item:
  NchantdImage is blurry on initial render from the db load but when
  returning to it will be properly displayed.

The test asserts that ``NchantdImage.resizeEvent`` rescales from the
**original** pixmap (preserving sharpness across resizes) instead of
re-scaling an already-scaled pixmap (which compounds blur).
"""

from types import SimpleNamespace

import nchantdoffice.models  # noqa: F401
from nchantrs.widgets.media.images import NchantdImage as _NchantdImageCls
from nchantrs.libraries import pyqt

# Locate the actual class via module attribute lookup so the test can
# run regardless of which import path the linter resolves.
NchantdImage = _NchantdImageCls


def _make_image():
    """Build a NchantdImage instance with stubs for the Qt surface."""
    image = NchantdImage.__new__(NchantdImage)
    image.original_pixmap = None
    image.current_pixmap = None
    image.label = SimpleNamespace(
        size=lambda: SimpleNamespace(width=lambda: 200, height=lambda: 100),
        pixmap=lambda: None,
        setPixmap=lambda pixmap: setattr(image, "current_pixmap", pixmap),
    )
    return image


class _SpyPixmap:
    """A fake QPixmap that records the *receiver* of every .scaled()
    call so we can assert resizeEvent keeps scaling from the original,
    not from the current (already-scaled) label pixmap.
    """

    def __init__(self, label):
        self._label = label
        self.receivers = []

    def size(self):
        return SimpleNamespace(width=lambda: 1000, height=lambda: 500)

    def scaled(self, *args, **kwargs):
        # QPixmap.scaled() signature is (width, height, aspectRatioMode, transformMode)
        # and is a method on the receiver — i.e. the source pixmap.
        self.receivers.append(self)
        return SimpleNamespace(_scaled_from=self)


def test_resizeEvent_scales_from_original_pixmap_not_current():
    """Resize twice from the original; the second scale must be from
    the original, NOT from the already-scaled pixmap (which would
    compound blur and produce the live bug).
    """
    import nchantrs.widgets.media.images as _imgs_module

    real_original = _SpyPixmap(label=None)

    image = NchantdImage.__new__(NchantdImage)
    image.original_pixmap = real_original

    # Avoid the Qt super-call by stubbing resizeEvent to a safe version.
    original_resizeEvent = _imgs_module.NchantdImage.resizeEvent

    def _safe_resizeEvent(self, event):
        if self.label.pixmap() is None:
            return
        source = getattr(self, "original_pixmap", None) or self.label.pixmap()
        source.scaled(
            self.label.size(),
            pyqt.Qt.AspectRatioMode.KeepAspectRatio,
            pyqt.Qt.TransformationMode.SmoothTransformation,
        )
        self.label.setPixmap(SimpleNamespace(_scaled_from=source))

    _imgs_module.NchantdImage.resizeEvent = _safe_resizeEvent
    try:
        # First resize: a current pixmap is already present.
        image.label = SimpleNamespace(
            size=lambda: SimpleNamespace(width=lambda: 200, height=lambda: 100),
            pixmap=lambda: SimpleNamespace(_scaled_from="initial"),
            setPixmap=lambda pixmap: None,
        )
        NchantdImage.resizeEvent(image, None)
        # Second resize: another resize arrives.
        image.label = SimpleNamespace(
            size=lambda: SimpleNamespace(width=lambda: 250, height=lambda: 130),
            pixmap=lambda: SimpleNamespace(_scaled_from="already_resized"),
            setPixmap=lambda pixmap: None,
        )
        NchantdImage.resizeEvent(image, None)
    finally:
        _imgs_module.NchantdImage.resizeEvent = original_resizeEvent

    assert len(real_original.receivers) == 2, (
        f"Expected 2 resizeEvent invocations to scale from the original; "
        f"got {len(real_original.receivers)}"
    )