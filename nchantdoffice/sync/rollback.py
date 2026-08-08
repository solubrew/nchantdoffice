# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
    docid: nchantdoffice-sync-rollback
    name: Journal-Based Rollback
    description: >
        T-DESK-058 Step 3: the rollback path for the
        ContentUpdateSync. When ``_apply_data_json`` raises
        mid-apply, the journal records an ABORT entry. This
        module reads the journal, finds uncommitted
        transactions, and undoes the mutations.

        The rollback is conservative: it only reverses
        transactions whose last journal entry is ``begin``
        (no matching ``commit`` or ``abort``). Already-
        committed transactions are left untouched.
    version: 1.0.0
    authority: filesystem
    security: seclvl2
    <(WT)>: -32
"""
# -*- coding: utf-8 -*-
# ======================================Standard Library Modules======================================================||
import json
from typing import Any, Dict, List, Optional

# ======================================3rd Party Library Modules=====================================================||

# ======================================Solutions Brewer Library Modules=============================================||
from kahndor.logma import Logma

logma = Logma(__name__)


def rollback_from_journal(journal, store) -> int:
    """Roll back uncommitted transactions from a JsonlJournal.

    Args:
        journal: a ``micromole.journal.JsonlJournal`` instance
            with entries on disk.
        store: the ``NchantdOfficeStore`` (or any MicroStash
            subclass) to undo mutations on.

    Returns the number of transactions rolled back.

    Algorithm:
      1. Read all journal entries.
      2. Group by ``tx_id`` and find transactions whose last
         entry is ``begin`` (no ``commit`` or ``abort``).
      3. For each uncommitted transaction, attempt to reverse
         the mutation:
           - ``INSERT`` → ``DELETE`` the inserted rows
           - ``UPDATE`` → ``UPDATE`` back to the old values
             (if available in the journal data)
           - ``DELETE`` → re-``INSERT`` (if data is available)
      4. If reversal fails, log the error (best-effort — don't
         crash the rollback path itself).

    Note: the rollback is best-effort. The journal records the
    mutation arguments, but reversing them requires knowing
    the old values (which the journal may not have captured
    for UPDATE operations). The most reliable rollback is for
    INSERT → DELETE (we know the PK we inserted).
    """
    entries = journal.entries()
    if not entries:
        return 0

    # Group entries by tx_id and find uncommitted transactions.
    tx_states: Dict[str, str] = {}  # tx_id → last status
    tx_data: Dict[str, Dict] = {}   # tx_id → begin entry data
    for entry in entries:
        tx_id = entry.tx_id if hasattr(entry, "tx_id") else entry.get("tx_id", "")
        status = entry.status if hasattr(entry, "status") else entry.get("status", "")
        tx_states[tx_id] = status
        if status == "begin":
            data = entry.data if hasattr(entry, "data") else entry.get("data", {})
            tx_data[tx_id] = data

    # Find uncommitted transactions (last status = "begin").
    uncommitted = [
        tx_id for tx_id, status in tx_states.items()
        if status == "begin" and tx_id in tx_data
    ]

    rolled_back = 0
    for tx_id in uncommitted:
        data = tx_data[tx_id]
        operation = data.get("operation", "")
        table = data.get("table", "")

        try:
            if _try_reverse(store, operation, table, data):
                rolled_back += 1
                # Mark as aborted in the journal.
                journal.abort(tx_id)
        except Exception as e:
            logma.error(
                f"[rollback] failed to reverse tx {tx_id} "
                f"({operation} on {table}): {e}",
                exc_info=True,
            )

    if rolled_back > 0:
        logma.info(
            f"[rollback] rolled back {rolled_back} uncommitted "
            f"transactions"
        )
    return rolled_back


def _try_reverse(
    store: Any,
    operation: str,
    table: str,
    data: Dict,
) -> bool:
    """Attempt to reverse a single mutation. Returns True on
    success, False if the reversal can't be determined.

    Conservative: only reverses INSERT → DELETE (we know the
    rows we inserted). UPDATE and DELETE reversals require
    old-value snapshots which the current journal doesn't
    capture — those are logged as "can't reverse" and left
    for manual intervention.
    """
    if operation == "INSERT" and table:
        # The INSERT data contains the payload that was stored.
        # To reverse: delete the rows we just inserted.
        # The payload shape varies (store_records vs _store);
        # extract the PK if possible.
        payload = data.get("data", data)
        try:
            if isinstance(payload, dict) and "payload" in payload:
                records = payload.get("payload", [])
                # records is a list of lists; the first column
                # is typically the PK.
                for record in records:
                    if isinstance(record, (list, tuple)) and len(record) > 0:
                        pk = record[0]
                        if pk:
                            store.delete_record(table, primary_key=pk)
                            return True
            # Fallback: if we can't extract the PK, at least
            # log the reversal attempt.
            logma.warning(
                f"[rollback] can't extract PK from INSERT "
                f"payload for table {table} — manual "
                f"intervention may be needed"
            )
            return False
        except Exception as e:
            logma.warning(
                f"[rollback] INSERT reversal failed: {e}"
            )
            return False

    # UPDATE / DELETE: we don't have old-value snapshots in
    # the current journal (step 1 records the mutation args,
    # not the pre-mutation state). These are logged + left.
    if operation in ("UPDATE", "DELETE"):
        logma.info(
            f"[rollback] {operation} reversal not implemented "
            f"(no old-value snapshot in journal) for table "
            f"{table} — transaction {data.get('tx_id', '?')} "
            f"left for manual review"
        )
        return False

    return False


__all__ = ["rollback_from_journal"]
