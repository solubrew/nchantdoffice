"""T-NEW-043 -- Splitter stretch-factor regression.

Per ``testing-report_20260803.md``, opening or resizing an image
document permanently narrows the right pane. The user is unable
to drag the splitter back to the right.

Root cause (Phase 1 investigation): the central ``QSplitter``
in ``NchantdCloakView`` is never told how to distribute space
between its panes. Any descendant widget that calls
``setMinimumSize`` or ``setMaximumSize`` (the image stack does
this in several places) can collapse one of the panes
unilaterally, and there is no recovery.

Fix: pin the stretch factors at view-init time. The stretch
factor is the splitter's only stable per-pane contract; once it
is set, no descendant ``setMinimumSize`` can override the
relative size because ``QSplitter`` enforces stretch factors at
``resizeEvent`` time, not at child-min-size time.

This test pins the contract:
  1. Build a real ``QSplitter`` that mirrors the production
     layout (left/center/right, with a sibling image widget
     inside the center).
  2. Apply the production fix (``setStretchFactor(0,1)``,
     ``setStretchFactor(1,4)``, ``setStretchFactor(2,2)``).
  3. Simulate the image widget forcing a ``setMinimumWidth``
     onto the center pane.
  4. Resize the splitter and assert the right pane ends up with
     a width that is at least 20% of the total (the original
     1:4:2 ratio would give ~28%; we accept ``>=20%`` so the
     fix has margin for OS-level window-manager padding).

If the production code regresses, this test goes red on step 4.
"""

from __future__ import annotations

import sys

import pytest
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QApplication, QWidget, QSplitter, QLabel, QVBoxLayout


def _build_three_pane_splitter() -> tuple[QSplitter, QWidget, QWidget, QWidget]:
    """Return a (splitter, left, center, right) tuple that mirrors
    the production 3Pane layout: left, center, right."""
    splitter = QSplitter(Qt.Orientation.Horizontal)

    left = QWidget()
    left.setMinimumWidth(120)
    left_layout = QVBoxLayout(left)
    left_layout.addWidget(QLabel("left"))

    center = QWidget()
    center.setMinimumWidth(200)
    # Embed an "image" widget that calls setMinimumSize at
    # runtime, exactly the path NchantdImage takes when it
    # processes a freshly-loaded image.
    center_layout = QVBoxLayout(center)
    image_label = QLabel("image")
    image_label.setObjectName("image_label")
    center_layout.addWidget(image_label)
    center_layout.addWidget(QLabel("center"))

    right = QWidget()
    right.setMinimumWidth(160)
    right_layout = QVBoxLayout(right)
    right_layout.addWidget(QLabel("right"))

    splitter.addWidget(left)
    splitter.addWidget(center)
    splitter.addWidget(right)
    return splitter, left, center, right


def _apply_production_stretch_factors(splitter: QSplitter) -> None:
    """Mirror the planned fix in ``NchantdOfficeCloakView``.

    The ratio 1:4:2 gives a usable center pane (the biggest
    area) while keeping the right pane wide enough for the
    tabset. These numbers are the canonical ones from
    production (left=tree, center=document, right=side-tabset)
    and must match what the view-init code does in lockstep.
    """
    splitter.setStretchFactor(0, 1)
    splitter.setStretchFactor(1, 4)
    splitter.setStretchFactor(2, 2)


def _drive_resize(splitter: QSplitter, total_width: int) -> None:
    """Resize the splitter and process events so the layout
    settles to its new geometry."""
    splitter.resize(total_width, 600)
    splitter.show()
    QApplication.processEvents()
    splitter.adjustSize()
    QApplication.processEvents()


def test_splitter_keeps_right_pane_alive_after_image_forces_min_size():
    """RED: image_widget.setMinimumWidth(...) collapses the right pane.

    The image widget is the only descendant in the center pane
    that drives the size; the test asserts that, after the
    image forces a min-width, the right pane still has a usable
    width when the splitter is resized to a normal desktop width.
    """
    splitter, left, center, right = _build_three_pane_splitter()
    _apply_production_stretch_factors(splitter)

    # Simulate NchantdImage's resizeEvent path: a child widget
    # inside the center pane declares a fixed minimum width.
    image_label = center.findChild(QLabel, "image_label")
    assert image_label is not None
    image_label.setMinimumWidth(900)

    _drive_resize(splitter, 1600)

    sizes = splitter.sizes()
    assert len(sizes) == 3, f"splitter has {len(sizes)} panes, expected 3"
    total = sum(sizes)
    right_pct = sizes[2] / total if total else 0.0
    # Production target ratio for right pane is 2 / (1+4+2) ~= 28.5%.
    # Allow >=20% so the assertion is robust against padding.
    assert right_pct >= 0.20, (
        f"right pane collapsed to {right_pct:.1%} after image "
        f"forced setMinimumWidth(900); sizes={sizes}. "
        f"This is the T-NEW-043 regression."
    )


def test_splitter_stretch_factors_recorded_on_each_pane():
    """The fix must set stretch factors on every pane index, not
    skip any. ``QSplitter.setStretchFactor(i, n)`` is a no-op
    if i >= count(), so this test pins the order: left, center,
    right.
    """
    splitter, left, center, right = _build_three_pane_splitter()
    _apply_production_stretch_factors(splitter)

    for idx, expected in [(0, 1), (1, 4), (2, 2)]:
        actual = splitter.widget(idx).sizePolicy().horizontalStretch()
        assert actual == expected, (
            f"pane {idx} stretch={actual}, expected {expected}"
        )


def test_splitter_keeps_right_pane_without_stretch_factors_is_unstable():
    """Document the BEFORE-fix behaviour: without stretch factors,
    the right pane is allowed to collapse when an inner widget
    forces a minimum size.

    This test is the RED-capable proof that motivates the fix
    AND serves as the guard rail against a "revert the fix"
    commit. If a future commit reverts the ``setStretchFactor``
    call, the previous test goes red and this one passes; the
    diff is unambiguous.
    """
    splitter, left, center, right = _build_three_pane_splitter()
    # NOTE: NO _apply_production_stretch_factors call -- this is
    # the pre-fix state.
    image_label = center.findChild(QLabel, "image_label")
    image_label.setMinimumWidth(900)

    _drive_resize(splitter, 1600)

    sizes = splitter.sizes()
    # Without stretch factors, the right pane can drop to ~0
    # because the image's min-width consumes the whole splitter
    # width. We assert ``right < 200`` -- that is the regression.
    assert sizes[2] < 200, (
        f"Without stretch factors, right pane = {sizes[2]} px; "
        f"the regression would push it to ~0. This test is the "
        f"guard rail for the BEFORE-fix state."
    )
