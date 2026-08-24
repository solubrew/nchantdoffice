# T-NEW-144b implementation plan — multi-format external editing umbrella

**Author:** agent session 2026-08-19
**Repo:** `nchantdoffice` (`/home/solubrew/.hermes/projects/nchantdoffice`)
**Branch:** `gamma`
**Status:** Draft (waiting for operator direction on scope)

## Context

`T-NEW-144b` is the active umbrella for **multi-format external editing** across the desktop widget tree. The umbrella replaces the deferred "PUSH to 0.0.3 force external until" / "PUSH to 0.0.3" markers that currently hardcode `set_location("external")` in 13 widget classes, with a proper **location-driven routing layer** that honours both internal-blob and external-file origins.

Two children already shipped under this umbrella:

- **T-NEW-148 / `NchantdOfficeScript`** — `9f18e30` (syntax-aware atomic external save, internal save untouched). The canonical reference pattern for the umbrella.
- **T-NEW-159 / `NchantdOfficePDF`** — `cbec5b3` + `4a7914c` (internal binary blob; external file-only since the PDF widget is read-only).

Per `TODOs.md §Active umbrella sequencing`:

> Work proceeds one document type at a time. The phased children completed so far: ... **No two formats move forward in parallel.**

The umbrella has scope across **13 widget classes** that hardcode `self.document.set_location("external")` and ship the **# PUSH-to-0.0.3** markers that block the internal-blob routing. Each one needs the same shape of fix:

- Replace `set_location("external")` hardcode with a `self.document.location` thread-through (default in `initModel`, hint in `open_file`).
- Wire `populate_document` to dispatch on `self.document.location` (internal → blob, external → file_path, cloud → future connector).
- Wire `save` / external-save seam so external location writes back to disk (per the Script seam).

## Affected sites (23 call sites across 13 classes)

| File | Class | Line | What |
|---|---|---:|---|
| `media/scripts.py` | `NchantdOfficeScript` | 221 | `initView` hardcode (reference impl — already wired) |
| `media/scripts.py` | `NchantdOfficeScript` | 1174 | `open_file` hardcode (reference impl — already wired) |
| `media/images.py` | `NchantdOfficeImage` | 784 | `initView` hardcode — **T-NEW-160** |
| `media/images.py` | `NchantdOfficeImage` | 1306 | `open_file` hardcode — **T-NEW-160** |
| `media/sketches.py` | `NchantdOfficeSketch` | 1077 | `initView` hardcode |
| `media/pdfs.py` | `NchantdOfficePDF` | 195 | `initView` hardcode (read-only — partial fix) |
| `media/forms.py` | `NchantdOfficeForm` | 77 | `initView` hardcode |
| `media/forms.py` | `NchantdOfficeFormManager` | 415 | `open_file` hardcode |
| `workbooks/matricies.py` | `NchantdOfficeMatrix` | 171 | `initView` hardcode |
| `workbooks/matricies.py` | `NchantdOfficeMatrix` | 1860 | (cmd save chain — re-route) |
| `workbooks/notebooks.py` | `NchantdOfficeNotebook` | 237 | `initView` hardcode — **T-NEW-160a** (both internal+external work today) |
| `workbooks/notebooks.py` | `NchantdOfficeNotebook` | 1172 | `open_file` hardcode — **T-NEW-160a** |
| `managers/calendars.py` | `NchantdOfficeCalendar` | 614 | `initView` hardcode |
| `managers/filesystems.py` | `NchantdCompressPane` | 96 | `initView` hardcode |
| `managers/filesystems.py` | `NchantdOfficeFileSystem` | 1372, 1431 | populate/open branches hardcode |
| `analytics/analytics.py` | `NchantdOfficeChart` | 225 | `initView` hardcode |
| `atnrg/prompts.py` | `NchantdContextListPane` | 92 | `initView` hardcode |
| `atnrg/prompts.py` | `NchantdOfficePromptManager` | 196 | `initView` hardcode |
| `atnrg/prompts.py` | `NchantdOfficePrompt` | 287 | `initView` hardcode |
| `atnrg/browsers.py` | `NchantdOfficeWebBrowser` | 118 | `initView` hardcode (already partially wired, but caller still hardcodes) |
| `atnrg/contacts.py` | `NchantdOfficeContact` | 88 | `initView` hardcode |
| `atnrg/contacts.py` | `NchantdOfficeRolodex` | 239 | `initView` hardcode |
| `documents/documents.py` | `NchantdOfficeDocument` | 1156, 1207 | `populate_data` / `save` — these are the parent contract (already correct; do not touch) |

## Plan: phased TDD cards (one per format, no parallelism)

The umbrella's "no two formats move forward in parallel" rule means **one card per widget class**. Each card is a single TDD commit. The cards below are sized for one focused TDD cycle each (matching the velocity we established across T-NEW-148 / T-NEW-159 / T-NEW-167..169).

### Card 1 — T-NEW-160 (NchantdOfficeImage)

**Scope:** thread `location` through `initView` + `open_file`, wire `save` external-seam.

- `widgets/documents/media/images.py:784` — `initView` hardcode removed; route `populate_data` / `connect_to_file` / branch on `self.document.location`.
- `widgets/documents/media/images.py:1306` — `open_file` hardcode removed; only set the location hint when the user is opening from disk.
- `widgets/documents/media/images.py` — `save()` mirrors the Script seam: after `super().save()`, write the image bytes back to `self.file_path` when `location == "external"` and the path is set. Image format is binary (not syntax-aware), so the export is a straight `QPixmap` / `QImage` save.
- New TDD test file `tests/test_t_new_160_image_external_save.py` covering:
  - `initView` no longer hardcodes `set_location("external")` (the hardcode marker is gone from the source).
  - `open_file` no longer hardcodes (the call is omitted when file is None; only fires when file is set).
  - `save` external-seam: writes bytes to disk when `location == "external"`, is a no-op when `location == "internal"`.

**Estimated size:** 1 commit, ~80 lines new.

### Card 2 — T-NEW-160a (NchantdOfficeNotebook)

**Scope:** the special case where **both internal (`notebook_bytes`) and external (`.ipynb` write) already work**. The pending work is **default-origin threading** — `initView` hardcodes `"external"` even when the doc was opened from the database.

- `widgets/documents/workbooks/notebooks.py:237` — `initView` no longer hardcodes; defaults to `None`/config if no `last_notebook_path` was opened in this session.
- `widgets/documents/workbooks/notebooks.py:1172` — `open_file` no longer hardcodes; only sets `external` when the file came from disk (the existing scheduled-reload handler at line 232 already handles the DB case).
- Existing `save()` at `widgets/documents/workbooks/notebooks.py:1207` is already correct (external-write + DB-persist for save_mode="to_dict"/"both"); needs no change.
- New TDD test file `tests/test_t_new_160a_notebook_default_origin.py` covering:
  - `initView` no longer hardcodes `set_location("external")`.
  - When `last_notebook_path` is empty, the doc keeps its existing location (None defaults to internal).
  - `save` external-seam unchanged: writes `.ipynb` when `location == "external"`.

**Estimated size:** 1 commit, ~50 lines new (mostly the comment).

### Card 3 — T-NEW-160b (NchantdOfficeSketch + Forms + Cells + Chart + Browsers + Calendars + Filesystems + Prompts + Contacts)

**Scope:** the remaining 11 widgets that hardcode `"external"`. The pattern is identical across all of them — **drop the hardcode, route on `self.document.location`**.

Decision needed before starting this card: **do all 11 in one large commit, or one commit per widget?** The umbrella rule ("no two formats in parallel") suggests **one commit per widget** is safer (smaller diffs are easier to revert if a behavior shift breaks the live flow). Total: ~11 commits.

The operator mandate ("match velocity to task size") suggests **clustering similar widgets** — the atnrg/* group (browsers, contacts, prompts) and the media/* group (sketches, forms, pdfs) cluster naturally by shared `set_location` idiom.

**Recommendation:** ship this card as 3 grouped commits:

- Commit B1: atnrg/* (browsers, contacts, prompts — 5 call sites in 5 classes)
- Commit B2: media/* (sketches, forms, pdfs — 4 call sites in 4 classes)
- Commit B3: managers/* + workbooks/* + analytics/* (calendars, filesystems, matrix, chart — 6 call sites in 6 classes)

Each commit is one TDD test file + the source patches for that group. RED→GREEN proven per group.

### Card 4 — `documents.py` (parent contract verification)

**Scope:** verify the parent `NchantdOfficeDocument.save()` (line 1203) and `populate_document()` (line 1197) already handle location correctly with the existing internal + external branches. The 2 hardcodes at `documents.py:1156 + 1207` are in `populate_data` and `save_external` (already deferred-method comments).

Per T-NEW-144b scoping: these are the parent contract that the children will delegate to. They should stay as-is. **No fix needed** — they're the canonical implementation that the new logic delegates to.

## Risks and open questions

1. **The `populate_document` signature inconsistency** — some widgets override `populate_document(self)` (no args); others override `populate_document(self, file=None)` (NchantdOfficeImage, NchantdOfficeNotebook, NchantdOfficeWebBrowser). The Script pattern uses `populate_document()` (no args, location-aware). To ship Card 1 cleanly I need to confirm the parent `populate_document` signature, then thread the same pattern in children.
2. **The `set_location("external")` hardcode is sometimes intentional** — `cmd_load_external_file` and similar cmd_* handlers legitimately want to set the location (the file came from disk). The plan keeps these; only the `initView` and `open_file` (no-arg) hardcodes get removed.
3. **`NchantdCompressPane`** at `filesystems.py:96` is an unexpected class — it's the "Compress" pane (a tools/utilities widget, not a document widget). It uses `set_location("external")` to flag the active file path but doesn't follow the populate/save contract. Card 3 will need to handle it as a special case (probably just remove the hardcode, no save seam needed).
4. **`NchantdOfficeCellBorderFormats`** at `matricies.py:171` — same as above; it's a sub-widget for formatting, not a document. The `set_location("external")` here is a flag for the matrix parent, not a location contract. Card 3 treats it as a special case.

## Decision points for the operator

- **Card 3 commit strategy:** one commit per widget (11 commits) vs grouped by dir (3 commits)? The umbrella rule says "one document type at a time"; grouped commits slightly violate that. **My recommendation:** one commit per widget for the atnrg/* + media/* groups (small per-widget), then assess if the manager/workbook groups should stay separate.
- **Card 1 `save` external-seam:** Script uses syntax-aware exporter. Image uses binary (QPixmap). Should I keep the save seam **single-method per widget** (matches Script) or **factor a shared helper** into `documents.py` (DRY)? The latter reduces duplication but widens the diff; the former is the safer first commit. **My recommendation:** one method per widget, no shared helper.
- **Card 1 `populate_data` vs `populate_document`:** the parent `NchantdOfficeDocument.populate_data` at line 1156 hardcodes `set_location("internal")` (correct), then calls `self.save()`. The Image widget should mirror this — when the doc is internal, `populate_data` already routes correctly. I need to confirm the path works for Image before card 1 ships.

## Migration plan (sequenced commits)

```
T-NEW-160      -- images.py      InitView + open_file + save external seam
T-NEW-160a     -- notebooks.py   InitView + open_file (save already correct)
T-NEW-160b/B1  -- atnrg/*        5 widgets: InitView + open_file
T-NEW-160b/B2  -- media/*        4 widgets: InitView + open_file (Image excluded; pdfs gets partial)
T-NEW-160b/B3  -- manager/+wb   6 widgets: InitView + open_file (compress/cells as special cases)
```

Total: ~6 commits, ~300-450 lines new, ~20-30 new tests.

Each commit lands one RED→GREEN cycle with the canonical Script pattern as the reference.

## Out of scope

- The 4 cipher markers (T-NEW-013) tracked separately; not in scope here.
- The 15 `# RESERVED for <feature>; see T-NEW-161` markers already relabeled; not in scope here.
- T-NEW-152/153/154/155/156/157/158 (P1 operator workflow) tracked separately; not in scope here.
- The cloud-location `connect_to_file()` deferred method (`raise Exception("Internal and Cloud locations not supported yet")` at `documents.py:1043`) — the cloud connector is a 0.0.3+ feature; the umbrella defers that to a future card.
- **The Jupyter/file-extract/kahndor/squirl layers under the umbrella** — when internal `notebook_bytes` are read, the `populate_document` flow uses `self.document.open_file` which expects a path. If the bytes are coming from a DB blob, we need a `notebook_bytes` path or an adapter. Card 2 may surface this. The umbrella's scope ends at "the document.location contract is honored by the widget"; deeper storage plumbing is out of scope.

## Tasks

- [ ] **T-NEW-160**: ship Card 1 (Image external-seam). Format: RED test first, then source patch mirroring Script seam. Commit on gamma.
- [ ] **T-NEW-160a**: ship Card 2 (Notebook default-origin). Format: same.
- [ ] **T-NEW-160b/B1**: ship atnrg/* group (5 widgets).
- [ ] **T-NEW-160b/B2**: ship media/* group (4 widgets).
- [ ] **T-NEW-160b/B3**: ship manager/+wb group (6 widgets with 2 special cases).
- [ ] Update `TODOs.md` `Active umbrella sequencing` block after each card lands.
- [ ] Commit `tests` files alongside source commits (matches operator convention from T-NEW-148 onward).

## Refs

- `TODOs.md §Active umbrella sequencing` — umbrella sequencing rule ("no two formats in parallel")
- `TODOs.md §In-code marker audit` — the original 14 `set_location("external")` marker tally
- `nchantdoffice/widgets/documents/media/scripts.py:1399-1434` — T-NEW-148 canonical save seam
- `nchantdoffice/widgets/documents/media/scripts.py:1444-1483` — T-NEW-148 canonical `_write_external_file` helper
- `nchantdoffice/widgets/documents/media/images.py:1315-1329` — the existing `populate_document` dispatch that Card 1 will extend
- `nchantdoffice/widgets/documents/documents.py:1197-1213` — the parent `NchantdOfficeDocument.save()` (canonical contract)
- `nchantdoffice/widgets/documents/documents.py:1153-1158` — the parent `populate_data()` (already correctly routes "internal")
