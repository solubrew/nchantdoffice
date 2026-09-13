# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
    docid:
    name: Ad Tab Telemetry Emitter
    description: >
        T-NEW-167: emits ad-tab telemetry events to the server.

        Captures per event:
          - event_type: rotation | render | click | tab_top |
            session_tick
          - layout + slot_index: which ad box in which layout
          - stack_position + is_on_top: the Ad tab's position in
            the right-pane tabset and whether it is the current
            tab at emit time (rotation is only SEEABLE if the tab
            is on top — that's the whole point of the flag)
          - client_instance_id: desktop_uuid from install_store
            (falls back to install_id)
          - client_user_id: app.model.user.id (nullable —
            anonymous/offline users still emit)
          - session_age_seconds: seconds since app launch
          - client_ts: emitter-side wall clock (server also
            stamps its own server_ts + client_ip)
        transport: POST /api/ads/telemetry/events, fire-and-
        forget over QNetworkAccessManager; failures are logged
        and dropped (no retry queue — this is analytics, not
        billing).
    file-version: 1.0.0
---
<(USAGE)>:    # import inside NchantdOfficeAdTab (browsers.py); instantiated lazily in initView
<(CONTENTS)>: # AdTabTelemetry : emitter object hung off the Ad tab
<(SPECIAL)>:  # never raises — telemetry must not break the ad surface
---
<(SPECIAL)>:
    - Fire-and-forget: emit() never blocks the UI thread.
    - Identity is best-effort: missing install_store or user model
      just degrades fields to None, never raises.
---
"""

from __future__ import annotations

import time

# -- @_@] ------------------------------------------------------------------*

import logma

# -- @_@] ------------------------------------------------------------------*

__all__ = ["AdTabTelemetry"]


class AdTabTelemetry:
    """Fire-and-forget telemetry emitter for the Ad tab.

    Hung off :class:`NchantdOfficeAdTab`. Owns a
    ``QNetworkAccessManager`` (created lazily so the module can be
    imported headless in AST tests), the app-open timestamp, and
    the last-known stack position / on-top state.
    """

    #: Server ingest endpoint (T-NEW-167).
    TELEMETRY_URL_PATH = "/api/ads/telemetry/events"

    #: Batch cap mirror of the server's max_batch_size.
    MAX_BATCH_SIZE = 200

    #: Session ticks flush at most every 30s.
    SESSION_TICK_INTERVAL_S = 30

    def __init__(self, ad_tab) -> None:
        self._tab = ad_tab
        self._nam = None  # lazy QNetworkAccessManager
        self._t0 = time.time()
        self._last_stack_position = None
        self._last_on_top = None

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    def _identity(self):
        """Return ``(client_instance_id, client_user_id)``.

        instance id = ``desktop_uuid`` from install_store
        (server-issued at activation), falling back to
        ``install_id`` (generated locally), then '' if install
        store is unreadable. user id = ``app.model.user.id``,
        None when logged out / offline.
        """
        inst = ""
        uid = None
        try:
            from nchantdoffice.license.install_store import InstallStore
            record = InstallStore().get_or_create()
            inst = (
                record.get("desktop_uuid")
                or record.get("install_id")
                or ""
            )
        except Exception:
            inst = ""
        try:
            from pyqt import QApplication
            user = QApplication.instance().model.user
            uid = getattr(user, "id", None)
        except Exception:
            uid = None
        return inst, uid

    # ------------------------------------------------------------------
    # Context
    # ------------------------------------------------------------------

    def _tab_context(self):
        """Return ``(stack_position, is_on_top)`` for the Ad tab.

        stack_position = index of this tab in its parent QTabWidget
        (None when the tab isn't in a tabset yet — mid-construction
        or hidden for Pro users). is_on_top = whether the parent
        tabset's current widget is this tab, i.e. the user can
        actually SEE the ad surface right now.
        """
        tab = self._tab
        try:
            parent = tab.parent()
            # Walk up to the owning QTabWidget.
            tabset = None
            walker = parent
            for _ in range(4):
                if walker is None:
                    break
                if hasattr(walker, "indexOf") and hasattr(walker, "currentWidget"):
                    tabset = walker
                    break
                walker = walker.parent()
            if tabset is None:
                return None, None
            idx = tabset.indexOf(tab)
            if idx < 0:
                return None, None
            return idx, tabset.currentWidget() is tab
        except Exception:
            return None, None

    def _session_age_seconds(self):
        """Seconds since the emitter (== app surface) started."""
        return int(time.time() - self._t0)

    # ------------------------------------------------------------------
    # Event builders
    # ------------------------------------------------------------------

    def build_event(self, event_type, *, layout=None, slot_index=None, campaign_slug=None):
        """Build one telemetry payload dict (pure — unit-testable)."""
        stack_pos, on_top = self._tab_context()
        inst, uid = self._identity()
        return {
            "event_type": event_type,
            "campaign_slug": campaign_slug,
            "layout": layout,
            "slot_index": slot_index,
            "stack_position": stack_pos,
            "is_on_top": on_top,
            "client_instance_id": inst,
            "client_user_id": uid,
            "session_age_seconds": self._session_age_seconds(),
            "client_ts": _iso_now(),
            "schema_version": 1,
        }

    def build_batch(self, events):
        """Wrap events in the ingest envelope (capped)."""
        if not events:
            return None
        return {
            "schema_version": 1,
            "events": list(events)[: self.MAX_BATCH_SIZE],
        }

    # ------------------------------------------------------------------
    # Transport
    # ------------------------------------------------------------------

    def _post(self, payload):
        """Fire-and-forget POST. Never raises."""
        try:
            nam = self._ensure_nam()
            if nam is None:
                return
            from pyqt import QNetworkRequest, QUrl
            base = _server_base()
            if not base:
                return
            request = QNetworkRequest(QUrl(base + self.TELEMETRY_URL_PATH))
            request.setHeader(
                QNetworkRequest.ContentTypeHeader, "application/json"
            )
            body = _json_dumps(payload).encode("utf-8")
            nam.post(request, body)
        except Exception as exc:
            logma.warning(f"[ad_telemetry] post failed (non-blocking): {exc}")

    def _ensure_nam(self):
        if self._nam is None:
            try:
                from pyqt import QNetworkAccessManager
                self._nam = QNetworkAccessManager(self._tab)
            except Exception:
                self._nam = None
        return self._nam

    # ------------------------------------------------------------------
    # Public emit hooks (called from browsers.py)
    # ------------------------------------------------------------------

    def emit_rotation(self, layout):
        """Ad page finished loading after a rotation tick."""
        try:
            event = self.build_event(
                "rotation", layout=layout
            )
            self._last_stack_position = event["stack_position"]
            self._last_on_top = event["is_on_top"]
            self._post(self.build_batch([event]))
        except Exception as exc:
            logma.warning(f"[ad_telemetry] emit_rotation failed: {exc}")

    def emit_click(self, layout, slot_index, campaign_slug):
        """User clicked an ad box (ncho:// interception or external)."""
        try:
            event = self.build_event(
                "click",
                layout=layout,
                slot_index=slot_index,
                campaign_slug=campaign_slug,
            )
            self._post(self.build_batch([event]))
        except Exception as exc:
            logma.warning(f"[ad_telemetry] emit_click failed: {exc}")

    def emit_session_tick(self):
        """Periodic heartbeat while the app is open."""
        try:
            event = self.build_event("session_tick")
            self._post(self.build_batch([event]))
        except Exception as exc:
            logma.warning(f"[ad_telemetry] emit_session_tick failed: {exc}")

    def url_params(self):
        """Query-string params for the slim-ad page URL.

        The page's render beacon reads these via sendBeacon so
        page-level events carry the same identity as desktop
        events. Returns an empty string when the instance id is
        unknown (page beacon adds nothing the desktop emitter
        wouldn't already provide — avoids orphan rows).
        """
        try:
            inst, uid = self._identity()
            if not inst:
                return ""
            from urllib.parse import urlencode
            stack_pos, on_top = self._tab_context()
            params = {
                "inst": inst,
                "uid": uid if uid is not None else "",
                "ut": self._session_age_seconds(),
                "stk": stack_pos if stack_pos is not None else "",
                "top": 1 if on_top else 0,
            }
            return urlencode(params)
        except Exception:
            return ""


# ---------------------------------------------------------------------------
# Module-level helpers (kept pure for AST tests)
# ---------------------------------------------------------------------------


def _iso_now():
    """UTC ISO timestamp for client_ts."""
    import datetime as dt
    return dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")


def _server_base():
    """Server base URL from the unified urls config."""
    try:
        from nchantdoffice.utilities.urls import server_base_url
        return server_base_url().rstrip("/")
    except Exception:
        return ""


def _json_dumps(payload):
    import json
    return json.dumps(payload)
