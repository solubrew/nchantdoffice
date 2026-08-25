# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
    docid: nchantdoffice-sync-applier
    name: Content Update Sync Applier
    description: >
        T-DESK-058 Step 3: the ContentUpdateSync consumer for
        ``GET /api/updates``. Polls the server for available
        content updates (config changes, quicklink catalog
        refreshes, sample documents) and applies them to the
        desktop's local DB through the journal-guarded
        persistence chain.

        The sync is data_json-only in this iteration. The
        binary_delta path (bspatch) is deferred — logged
        + skipped so a server-side binary_delta push doesn't
        crash the sync.

        Integration:
          - micromole.journal.JsonlJournal (step 1) — WAL
            recording every mutation
          - NchantdOfficeStore(journal_path=...) (step 2) —
            the store is journal-enabled
          - credentials.load_credentials() — desktop UUID +
            api_key for the authenticated poll
          - rate_limit.RateLimitTracker — respects the
            server's 5/min limit on /api/updates
          - server_status.timed_call — records success /
            failure so the status bar reflects sync state
    version: 1.0.0
    authority: filesystem
    security: seclvl2
    <(WT)>: -32
"""
# -*- coding: utf-8 -*-
# ======================================Standard Library Modules======================================================||
import datetime as dt
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

# ======================================3rd Party Library Modules=====================================================||
import requests

# ======================================Solutions Brewer Library Modules=============================================||
from kahndor.logma import Logma

logma = Logma(__name__)

# ---------------------------------------------------------------------------
# T-DESK-058 Step 3 — constants
# ---------------------------------------------------------------------------

# Default poll interval (15 min per cross-repo review §2.4).
DEFAULT_POLL_INTERVAL_SECONDS: int = 15 * 60

# Known update_type values (per the server's free-form
# String(64) column — these are the documented values, but
# the applier must handle unknown types gracefully).
UPDATE_TYPE_DATA_JSON: str = "data_json"
UPDATE_TYPE_BINARY_DELTA: str = "binary_delta"

# HTTP timeout for the poll call.
_HTTP_TIMEOUT: float = 10.0

# T-NEW-070 (DESK-3 hard-break): NCHANT_DATA_DIR env var
# removed. The state dir now comes from the user config
# file via get_cache_dir(). Tests that need a custom state
# dir should override via monkeypatch on
# nchantdoffice.utilities.user_config.get_cache_dir.
from nchantdoffice.utilities.user_config import get_cache_dir  # noqa: E402
_STATE_DIR = get_cache_dir()
_STATE_PATH = _STATE_DIR / "sync_state.json"


# ---------------------------------------------------------------------------
# UpdateRecord — typed server response entry
# ---------------------------------------------------------------------------


@dataclass
class UpdateRecord:
    """A single entry from ``GET /api/updates``.

    Fields mirror the server's ``_serialize_update`` shape
    (see nchantdoffice_com/app/services/desktop_bridge.py).
    """

    id: int = 0
    os_txt: str = ""
    version_txt: str = ""
    release_date: str = ""
    update_type: str = ""
    update_path_txt: str = ""

    @classmethod
    def from_response(cls, payload: Dict[str, Any]) -> "UpdateRecord":
        """Build from a server response dict. Defensive
        against missing keys (the server is the source of
        truth; the desktop tolerates partial responses)."""
        return cls(
            id=int(payload.get("id", 0)),
            os_txt=str(payload.get("os_txt", "")),
            version_txt=str(payload.get("version_txt", "")),
            release_date=str(payload.get("release_date", "")),
            update_type=str(payload.get("update_type", "")),
            update_path_txt=str(payload.get("update_path_txt", "")),
        )


# ---------------------------------------------------------------------------
# ContentUpdateSync — the poller + dispatcher
# ---------------------------------------------------------------------------


class ContentUpdateSync:
    """Caller-driven content update sync.

    The caller (startup hook or 15-min timer) decides when
    to call ``sync_once()``. The class does not start any
    background thread.

    Usage::

        sync = ContentUpdateSync(store=my_journal_enabled_store)
        sync.sync_once()  # poll + apply + persist watermark
    """

    def __init__(
        self,
        store=None,
        base_url: Optional[str] = None,
        timeout: float = _HTTP_TIMEOUT,
    ) -> None:
        # DESK T-NEW-052: resolve from the unified URL config when
        # the caller doesn't pin a base_url. Operators can switch
        # the content-sync endpoint via XDG ``urls.sync_url``.
        if base_url is None:
            from nchantdoffice.utilities.urls import sync_url
            base_url = sync_url()
        self.store = store
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = requests.Session()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def sync_once(self) -> int:
        """Poll the server for new updates and apply them.

        Returns the number of updates successfully applied
        (0 when no updates available or server unreachable).

        Flow:
          1. Enable journaling on the store (derives path from
             the store's own DB path).
          2. Load credentials (desktop_uuid + api_key).
          3. Load last_update_date watermark.
          4. Poll ``GET /api/updates``.
          5. Apply each update (dispatch by update_type).
          6. Persist the new watermark.
          7. Record success/failure on ServerStatus.
        """
        # Enable journaling (derived from the store's own path).
        if self.store is not None and getattr(self.store, "_journal", None) is None:
            self.store.enable_journal()
        from nchantdoffice.utilities.server_status import (
            timed_call,
            DEFAULT_STATUS,
        )

        updates = self.poll()
        if not updates:
            return 0

        applied = self.apply(updates)

        # Persist the watermark after a successful apply.
        if applied > 0:
            latest = max(u.release_date for u in updates if u.release_date)
            self._save_last_update_date(latest)

        # Record success on the server status tracker.
        DEFAULT_STATUS.record_success()
        return applied

    # ------------------------------------------------------------------
    # Network: poll the server
    # ------------------------------------------------------------------

    def poll(self) -> List[UpdateRecord]:
        """Fetch ``GET /api/updates?uuid=<desktop_uuid>`` and
        return a list of ``UpdateRecord`` objects.

        Best-effort: any failure returns an empty list (the
        caller treats empty as "no updates" — no crash).
        """
        # Load credentials for the authenticated poll.
        creds = self._load_credentials()
        if creds is None:
            logma.info("[sync] no credentials — skipping poll")
            return []

        desktop_uuid = creds.get("desktop_uuid", "")
        api_key = creds.get("api_key", "")
        if not desktop_uuid:
            logma.warning("[sync] no desktop_uuid — skipping poll")
            return []

        # Rate-limit check (T-DESK-061).
        if not self._check_rate_limit():
            logma.info("[sync] rate-limited — skipping poll")
            return []

        # Build the query with the last_update_date watermark.
        last_update_date = self._load_last_update_date()
        params: Dict[str, str] = {"uuid": desktop_uuid}
        if last_update_date:
            params["last_update_date"] = last_update_date

        headers: Dict[str, str] = {}
        if api_key:
            headers["x-api-key"] = api_key

        try:
            response = self._session.get(
                f"{self.base_url}/api/updates",
                params=params,
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json() if response.content else []
        except (requests.RequestException, ValueError) as e:
            logma.warning(f"[sync] poll failed: {e}")
            # Record failure on server status.
            from nchantdoffice.utilities.server_status import DEFAULT_STATUS
            DEFAULT_STATUS.record_failure()
            return []

        if not isinstance(data, list):
            logma.warning(f"[sync] unexpected response type: {type(data)}")
            return []

        return [UpdateRecord.from_response(entry) for entry in data]

    # ------------------------------------------------------------------
    # Dispatch: apply updates by type
    # ------------------------------------------------------------------

    def apply(self, updates: List[UpdateRecord]) -> int:
        """Apply a list of updates. Returns the count of
        successfully applied updates.

        Dispatches by ``update_type``:
          - ``data_json``: route through the store's journal-
            guarded ``update_record``.
          - ``binary_delta``: deferred — logged + skipped.
          - unknown: logged + skipped (never crash).
        """
        applied = 0
        for record in updates:
            try:
                if record.update_type == UPDATE_TYPE_DATA_JSON:
                    self._apply_data_json(record)
                    applied += 1
                elif record.update_type == UPDATE_TYPE_BINARY_DELTA:
                    logma.info(
                        f"[sync] skipping binary_delta update "
                        f"{record.id} (bspatch not yet implemented — "
                        f"T-DESK-058 deferred)"
                    )
                else:
                    logma.warning(
                        f"[sync] unknown update_type "
                        f"{record.update_type!r} for update "
                        f"{record.id} — skipping"
                    )
            except Exception as e:
                logma.error(
                    f"[sync] apply failed for update {record.id} "
                    f"({record.update_type}): {e}",
                    exc_info=True,
                )
                # Rollback the failed transaction using the journal.
                self._rollback_last()
                # Don't re-raise — continue with the next update.
                # The journal records the abort; the next sync
                # retry will pick up from the watermark.
        return applied

    # ------------------------------------------------------------------
    # Type handlers
    # ------------------------------------------------------------------

    def _apply_data_json(self, record: UpdateRecord) -> None:
        """Apply a ``data_json`` update.

        Fetches the JSON payload from ``update_path_txt``
        (a URL or local path) and routes it through the
        store's ``update_record`` — which is journal-guarded
        in MicroStash (step 1).
        """
        if self.store is None:
            logma.warning("[sync] no store — skipping data_json apply")
            return

        # Fetch the JSON payload.
        payload = self._fetch_payload(record.update_path_txt)
        if payload is None:
            logma.warning(
                f"[sync] could not fetch payload for update "
                f"{record.id} at {record.update_path_txt}"
            )
            return

        # The payload is a store-compatible dict:
        #   {"table": {<table_name>: {"records": [...], "columns": [...]}}}
        # Route it through the store's write method (which is
        # journal-guarded in MicroStash).
        if isinstance(payload, dict) and "table" in payload:
            # Extract the table name for the journal entry.
            table = ", ".join(payload["table"].keys())
            column = list(payload["table"].keys())[0]
            # Use update_record (journal-guarded).
            self.store.update_record(payload, column, record.id, "db")
        else:
            logma.warning(
                f"[sync] data_json payload for update {record.id} "
                f"doesn't match the store dict shape — skipping"
            )

    # ------------------------------------------------------------------
    # Rollback (delegates to sync/rollback.py)
    # ------------------------------------------------------------------

    def _rollback_last(self) -> None:
        """Roll back the most recent uncommitted transaction
        using the journal. Delegates to ``rollback.py``.
        """
        if self.store is None or getattr(self.store, "_journal", None) is None:
            return
        try:
            from nchantdoffice.sync.rollback import rollback_from_journal
            rollback_from_journal(self.store._journal, self.store)
        except Exception as e:
            logma.error(f"[sync] rollback failed: {e}", exc_info=True)

    # ------------------------------------------------------------------
    # Payload fetcher
    # ------------------------------------------------------------------

    def _fetch_payload(self, path_or_url: str) -> Optional[Dict]:
        """Fetch a JSON payload from a URL or local path.
        Returns None on any failure.
        """
        if not path_or_url:
            return None
        try:
            if path_or_url.startswith("http"):
                response = self._session.get(
                    path_or_url, timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
            else:
                # Local file path.
                p = Path(path_or_url)
                if p.exists():
                    return json.loads(p.read_text(encoding="utf-8"))
                return None
        except Exception as e:
            logma.warning(f"[sync] payload fetch failed for {path_or_url}: {e}")
            return None

    # ------------------------------------------------------------------
    # Credentials + watermark helpers
    # ------------------------------------------------------------------

    def _load_credentials(self) -> Optional[Dict[str, Any]]:
        """Load desktop credentials from credentials.py."""
        try:
            from nchantdoffice.utilities.credentials import load_credentials
            creds = load_credentials()
            if creds is None:
                return None
            return {
                "desktop_uuid": getattr(creds, "desktop_uuid", ""),
                "api_key": getattr(creds, "api_key", ""),
            }
        except Exception as e:
            logma.warning(f"[sync] credentials load failed: {e}")
            return None

    def _load_last_update_date(self) -> str:
        """Load the incremental-poll watermark from sync_state.json."""
        try:
            if not _STATE_PATH.exists():
                return ""
            raw = _STATE_PATH.read_text(encoding="utf-8")
            state = json.loads(raw)
            return str(state.get("last_update_date", ""))
        except Exception:
            return ""

    def _save_last_update_date(self, date_str: str) -> None:
        """Persist the watermark to sync_state.json (mode 0o600)."""
        try:
            _STATE_DIR.mkdir(parents=True, exist_ok=True)
            state = {"last_update_date": date_str}
            _STATE_PATH.write_text(
                json.dumps(state, indent=2), encoding="utf-8"
            )
            os.chmod(_STATE_PATH, 0o600)
        except OSError as e:
            logma.warning(f"[sync] state save failed: {e}")

    # ------------------------------------------------------------------
    # Rate-limit check
    # ------------------------------------------------------------------

    def _check_rate_limit(self) -> bool:
        """Check the RateLimitTracker (T-DESK-061). Returns
        True if the poll is allowed, False if rate-limited.
        """
        try:
            from nchantdoffice.utilities.rate_limit import RateLimitTracker
            # Use a module-level singleton so the tracker state
            # persists across poll() calls.
            global _rate_limiter
            if "_rate_limiter" not in globals() or _rate_limiter is None:
                _rate_limiter = RateLimitTracker()
            allowed = _rate_limiter.check_rate_limit("/api/updates")
            if allowed:
                _rate_limiter.record_request("/api/updates")
            return allowed
        except Exception:
            # If the rate-limit module is unavailable, allow
            # the call (best-effort).
            return True


# Module-level rate-limiter singleton.
_rate_limiter = None


__all__ = [
    "ContentUpdateSync",
    "UpdateRecord",
    "DEFAULT_POLL_INTERVAL_SECONDS",
    "UPDATE_TYPE_DATA_JSON",
    "UPDATE_TYPE_BINARY_DELTA",
]
