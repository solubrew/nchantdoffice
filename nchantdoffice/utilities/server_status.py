# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
    docid: nchantdoffice-server-status
    name: Server Connection Status Indicator
    description: >
        T-DESK-063 (cross-repo review §2.9): 4-state machine
        + status-bar widget that tells the user whether the
        desktop can reach nchantdoffice.com.

        The state machine (``ServerStatus``) is Qt-independent
        — pure Python so the test layer can exercise it
        without a QApplication. The status-bar widget
        (``ServerStatusWidget``) is a thin QLabel that
        observes the state machine and re-renders on every
        transition; it's defined under a try/except so the
        pure class loads cleanly even when Qt is unavailable.

        States:
          CONNECTED  — last successful call < 1 min ago
          DEGRADED   — last successful call 1–5 min ago
          OFFLINE    — last successful call > 5 min ago,
                       OR the most recent call failed
          UNKNOWN    — no successful call AND no failure yet
                       (fresh process, no network activity)

        Consumer pattern (mirrors ``UpdateChecker``'s
        best-effort contract): every server call wraps
        itself in ``with timed_call(s):`` and the manager
        records success or failure based on whether the
        block raised.
    version: 1.0.0
    authority: filesystem
    security: seclvl2
    <(WT)>: -32
"""
# -*- coding: utf-8 -*-
# ======================================Standard Library Modules======================================================||
import contextlib
import datetime as dt
from typing import Optional

# ======================================3rd Party Library Modules=====================================================||
# (none — Qt import is gated below)

# ======================================Solutions Brewer Library Modules=============================================||
from kahndor.logma import Logma

logma = Logma(__name__)

# ---------------------------------------------------------------------------
# T-DESK-063 — module-level constants
# ---------------------------------------------------------------------------

# The 4 states. Pinning the literal names so a refactor that
# drops one state fails the AST contract test.
STATE_CONNECTED: str = "connected"
STATE_DEGRADED: str = "degraded"
STATE_OFFLINE: str = "offline"
STATE_UNKNOWN: str = "unknown"

# Thresholds (seconds since last successful call).
#   < CONNECTED_THRESHOLD_SECONDS → CONNECTED
#   < DEGRADED_THRESHOLD_SECONDS  → DEGRADED
#   otherwise                     → OFFLINE
# Tunable in source — an operator can bump them later if
# the default thresholds feel too aggressive.
CONNECTED_THRESHOLD_SECONDS: int = 60
DEGRADED_THRESHOLD_SECONDS: int = 5 * 60

# Human-readable labels for the status bar.
_STATE_LABELS: dict = {
    STATE_CONNECTED: "Connected",
    STATE_DEGRADED: "Degraded",
    STATE_OFFLINE: "Offline",
    STATE_UNKNOWN: "Unknown",
}

# Unicode emojis for the status bar.
_STATE_GLYPHS: dict = {
    STATE_CONNECTED: "\U0001F7E2",  # green circle
    STATE_DEGRADED: "\U0001F7E1",  # yellow circle
    STATE_OFFLINE: "\U0001F534",   # red circle
    STATE_UNKNOWN: "\u26AA",       # white circle
}


# ---------------------------------------------------------------------------
# T-DESK-063 — ServerStatus (pure, Qt-independent)
# ---------------------------------------------------------------------------


class ServerStatus:
    """State machine for the desktop → server connection.

    Threading: NOT thread-safe. The desktop is single-threaded
    on the Qt main loop, so all transitions happen on the
    main thread and no lock is needed.

    The state is COMPUTED, not stored: ``state()`` reads the
    last-success timestamp + last-failure flag and decides
    which bucket the current moment falls into. This means
    a long-running process naturally transitions
    CONNECTED → DEGRADED → OFFLINE as the last success ages,
    without any timer firing.
    """

    def __init__(self) -> None:
        self._last_success: Optional[dt.datetime] = None
        self._last_failure: Optional[dt.datetime] = None
        # ``_failure_flag`` is True between a ``record_failure``
        # call and the NEXT ``record_success``. Without it,
        # a single failure followed by silence would look
        # "connected" once the age-based math caught up. The
        # flag short-circuits that — the moment we fail, we
        # are OFFLINE until we succeed again.
        self._failure_flag: bool = False

    # ------------------------------------------------------------------
    # Transition triggers
    # ------------------------------------------------------------------

    def record_success(
        self, when: Optional[dt.datetime] = None
    ) -> "ServerStatus":
        """Record a successful server call.

        Args:
            when: injected datetime (for tests). Defaults
                to ``datetime.now(timezone.utc)``.
        """
        self._last_success = when if when is not None else _now()
        self._failure_flag = False
        logma.info("[server_status] success recorded")
        return self

    def record_failure(
        self, when: Optional[dt.datetime] = None
    ) -> "ServerStatus":
        """Record a failed server call.

        Sets the failure flag, which forces ``state()`` to
        return ``STATE_OFFLINE`` until the next success.
        """
        self._last_failure = when if when is not None else _now()
        self._failure_flag = True
        logma.info(
            "[server_status] failure recorded (forcing OFFLINE "
            "until next success)"
        )
        return self

    # ------------------------------------------------------------------
    # State computation
    # ------------------------------------------------------------------

    def state(self, when: Optional[dt.datetime] = None) -> str:
        """Return the current state.

        Logic:
          1. If a failure is flagged and no later success,
             → STATE_OFFLINE (the most recent call failed).
          2. If we've never had any call,
             → STATE_UNKNOWN.
          3. Otherwise compute age-since-last-success:
                < CONNECTED_THRESHOLD_SECONDS → CONNECTED
                < DEGRADED_THRESHOLD_SECONDS  → DEGRADED
                otherwise                      → OFFLINE
        """
        now = when if when is not None else _now()

        # Rule 1: failure flag wins.
        if self._failure_flag:
            return STATE_OFFLINE

        # Rule 2: never had a call.
        if self._last_success is None and self._last_failure is None:
            return STATE_UNKNOWN

        # Rule 3: age-since-last-success.
        if self._last_success is None:
            # Only failures so far → UNKNOWN isn't right
            # (we know the server is unreachable). The failure
            # flag above already covers the "we tried" case.
            return STATE_UNKNOWN

        age = (now - self._last_success).total_seconds()
        if age < CONNECTED_THRESHOLD_SECONDS:
            return STATE_CONNECTED
        if age < DEGRADED_THRESHOLD_SECONDS:
            return STATE_DEGRADED
        return STATE_OFFLINE

    # ------------------------------------------------------------------
    # UI helpers
    # ------------------------------------------------------------------

    def state_label(self) -> str:
        """Return a short human-readable label for the status
        bar (e.g. "Connected", "Degraded", "Offline",
        "Unknown"). The label reflects the current ``state()``.
        """
        return _STATE_LABELS.get(self.state(), _STATE_LABELS[STATE_UNKNOWN])

    def state_glyph(self) -> str:
        """Return a Unicode emoji for the status bar
        (🟢 / 🟡 / 🔴 / ⚪). The glyph reflects the
        current ``state()``.
        """
        return _STATE_GLYPHS.get(self.state(), _STATE_GLYPHS[STATE_UNKNOWN])

    def state_display(self) -> str:
        """Return ``"<glyph> <label>"`` for one-shot status-bar
        updates. Combines ``state_glyph()`` + ``state_label()``.
        """
        return f"{self.state_glyph()} {self.state_label()}"

    # ------------------------------------------------------------------
    # Diagnostics (for tests + the Settings panel)
    # ------------------------------------------------------------------

    @property
    def last_success(self) -> Optional[dt.datetime]:
        """When the last successful call was recorded
        (``None`` if never). Exposed for the Settings panel
        so the user can see "last successful call: 4 min ago".
        """
        return self._last_success

    @property
    def last_failure(self) -> Optional[dt.datetime]:
        """When the last failed call was recorded (``None``
        if never). Exposed for the Settings panel.
        """
        return self._last_failure


# ---------------------------------------------------------------------------
# T-DESK-063 — timed_call context manager
# ---------------------------------------------------------------------------


@contextlib.contextmanager
def timed_call(
    status: ServerStatus,
    when: Optional[dt.datetime] = None,
):
    """Wrap a server call so success/failure is recorded
    automatically.

    Usage::

        from nchantdoffice.utilities.server_status import (
            ServerStatus, timed_call,
        )

        SERVER_STATUS = ServerStatus()

        def some_api_call():
            with timed_call(SERVER_STATUS):
                response = requests.get("https://...")
                response.raise_for_status()
                return response.json()

    On clean exit: records success.
    On any exception: records failure AND re-raises the
    original exception (the manager is transparent — it does
    NOT swallow errors).
    """
    try:
        yield
    except BaseException:
        status.record_failure(when=when)
        raise
    else:
        status.record_success(when=when)


# ---------------------------------------------------------------------------
# T-DESK-063 — module-level singleton (for the convenience case)
# ---------------------------------------------------------------------------

# The "global" instance every consumer wraps. Module-level
# so consumers don't have to thread an instance through
# every call site (mirrors the pattern in
# ``base_layer.REFRESH_INTERVAL_SECONDS``).
DEFAULT_STATUS: ServerStatus = ServerStatus()


# ---------------------------------------------------------------------------
# T-DESK-063 — Qt widget (optional, guarded)
# ---------------------------------------------------------------------------

try:
    from nchantrs.libraries import pyqt as _pyqt

    class ServerStatusWidget(_pyqt.QLabel):  # type: ignore[misc]
        """Status-bar ``QLabel`` that observes a
        ``ServerStatus`` instance and re-renders on every
        transition.

        Usage::

            label = ServerStatusWidget(DEFAULT_STATUS, parent=main_window)
            main_window.statusBar().addPermanentWidget(label)
        """

        def __init__(
            self,
            status: ServerStatus = DEFAULT_STATUS,
            parent=None,
        ) -> None:
            super().__init__(parent)
            self._status = status
            self._render()
            # Tick every 5 s to re-render the age-based
            # CONNECTED → DEGRADED → OFFLINE transitions
            # without requiring a server call to trigger
            # them. Cheap (one timer, one label update).
            self._timer = _pyqt.QTimer(self)
            self._timer.setInterval(5000)
            self._timer.timeout.connect(self._render)
            self._timer.start()

        def _render(self) -> None:
            self.setText(self._status.state_display())

        # Expose the observed status so callers can
        # ``record_success`` / ``record_failure`` from elsewhere.
        @property
        def status(self) -> ServerStatus:
            return self._status

except ImportError:
    # Qt unavailable — the pure ServerStatus class still
    # works. The widget is optional; the test layer (and
    # any headless deployment) doesn't need it.
    ServerStatusWidget = None  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# T-DESK-063 — internal helpers
# ---------------------------------------------------------------------------


def _now() -> dt.datetime:
    """Return the current UTC time. Isolated so tests can
    monkey-patch (and so the ``when=`` injection pattern is
    the only blessed path for time control)."""
    return dt.datetime.now(dt.timezone.utc)


__all__ = [
    "ServerStatus",
    "ServerStatusWidget",
    "timed_call",
    "DEFAULT_STATUS",
    "STATE_CONNECTED",
    "STATE_DEGRADED",
    "STATE_OFFLINE",
    "STATE_UNKNOWN",
    "CONNECTED_THRESHOLD_SECONDS",
    "DEGRADED_THRESHOLD_SECONDS",
]
