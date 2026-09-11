# NchantdOffice / Nchantrs / Pyffice — Long-Term Performance Plan

> **Scope.** A code-evidence-grounded long-term plan for reducing wall-clock time,
> memory, and latency in the `nchantdoffice` desktop application and its two
> supporting libraries (`nchantrs` framework, `pyffice` office suite). Covers
> startup time, runtime UI responsiveness, throughput on compute-heavy paths
> (spreadsheets, image/PDF, CAD), and memory growth. **No code changes
> recommended in this document** — only direction, order, and justification.
>
> **Repos audited (read-only):**
> - `nchantdoffice` — `/home/solubrew/.hermes/projects/nchantdoffice` — 103 .py files, ≈60K LOC
> - `nchantrs` — `/home/solubrew/.hermes/projects/nchantrs` — 247 .py files (59 .yaml)
> - `pyffice` — `/home/solubrew/.hermes/projects/pyffice` — 129 .py files
>
> **Empirical evidence source:** `nchantdoffice/profile.json` + `profile.html`
> captured under `~/ENVs/uh` (the boot environment actually used in production).
> The profile is a Scorpion/CPU-style capture of a single 152-second run of
> `python -m nchantdoffice`.
>
> **Date:** 2026-09-10. **Branch policy:** gamma (per `STATE.md` and
> `README.md`). This plan supersedes nothing in `TODOs.md` / `CHANGES.md`; it
> is additive.

---

## Executive Summary

**The single biggest performance problem is not "Python is slow." It is
"Python does everything, on the GUI thread, in one process, at boot, with
no indexes and no streaming."** A 152-second run climbs from 289 MB to
**19.1 GB** of RSS without stabilizing — that is a leak, not a workload.
Almost all of the perceived slowness the user reports comes from five
classes of issue that are cheaper to fix than a rewrite:

1. **Startup import storm** — `pandas`, `numpy`, `pyffice.document`,
   `MicroMole`, `pycurity`, `aiohttp` are imported eagerly at
   `nchantdoffice.models:25–48`. `import nchantdoffice` pays the cold-cost
   even for `--help`.
2. **PyYAML as the boot CPU hotspot** — `yaml/scanner.py` accumulates
   6,567 % of CPU-time across 32 functions in the profile. YAML parsing
   is pure-Python and runs over the whole 355-line `models.yaml` plus
   the `kahndor` config chain on every boot.
3. **The SQLite layer is unindexed and synchronous** — 0 `CREATE INDEX`
   in the whole project, 0 `PRAGMA journal_mode = WAL`. Reads are
   `SELECT *` into pandas DataFrames on the GUI thread.
    INDEXes are handled in the squirl layer by the models.yaml index list 

4. **The widget layer uses `QTableWidget` + per-cell `setCellWidget`** —
   the editable spreadsheet builds N×M child widgets per sheet, then
   `insertRow(self.table.rowCount())` on every row — quadratic memory
   and paint cost.
5. **One QThread in the entire app, for `.pyof` import** —
   `widgets/controls/toolboxes.py:1367` is the only background worker.
   Everything else (codec download, update check, license bootstrap,
   tree repopulation, document open) runs on the GUI thread.

**Recommendation:** a **5-phase staged plan** that captures **70–85 % of the
gainable speedup with a fraction of the rewrite risk** of going to Rust
or C. The Rust/C rewrite is real and should happen, but only after the
low-risk wins are in and the hot paths are profiled at 5-second
resolution (the current profile is summary data; we need line-level
samples before deciding what to write in another language).

---

## 1. Evidence Base

### 1.1 What the existing profile actually tells us

The `nchantdoffice/profile.json` is a **scorpion-style CPU/memory
capture** (not a memray allocation trace). One process, ~152 s wall
(34.8 s of it under active CPU sampling — the memory sampler kept
running after the CPU tracker stopped), 1 single thread observed.
Headline numbers:

| Metric | Value |
|---|---|
| Program | `nchantdoffice/__main__.py` |
| Wall time | 152 s (34.8 s under CPU sampling) |
| Peak RSS | **19,171 MB** at 152 s (rising throughout — no plateau) |
| Python fraction of peak | 92 % |
| Largest single allocator | `diskcache/core.py:666` (10 MB growth, 100 % Python) |
| Files tracked | 10 |
| Memory samples | 15 (10 s spacing) |

**Memory timeline** (peak RSS, MB):
```
10s  →  289 MB
20s  →  468 MB
30s  →  870 MB
40s  → 1026 MB
50s  → 1218 MB
62s  → 1493 MB
72s  → 1800 MB
82s  → 2079 MB
92s  → 2421 MB
102s → 2670 MB
112s → 2964 MB
122s → 3271 MB
132s → 3304 MB
142s → 4523 MB     ← acceleration point
152s →19,171 MB    ← runaway growth, process not terminating
```

This is **not a linear pattern**. The curve is super-linear in the
second half (1.4 GB → 19 GB in 10 s is a 13× jump). One of three
things is happening, and we cannot tell which from this summary:

1. **Real leak** in `diskcache`, `squirl` connection pool, or the
   pandas DataFrame lifecycle during tree refresh.
2. **Materialization** of a giant string — e.g. `pyof` import reading
   a 14 MB file through YAML/JSON path, or `referral.py` scanning
   memory.
3. **Scalene artifact** — the profile was taken via `scalene` and the
   19 GB could include mapped file pages (`profile.json` itself is
   14 MB; `profile.html` is 16 MB — these grow with sample data).

**The first phase of the plan must re-run this capture with memray
on the running app, not at boot**, to resolve what is actually
leaking.

### 1.2 Top CPU hotspots (from the same capture)

```
  6666.667%  threading.py           (signal/thread spin)
   942.811%  urllib3/util/connection.py
   653.097%  yaml/scanner.py        32 functions
   381.463%  yaml/reader.py          4 functions
   129.966%  kahndor/kahndor.py      3 functions  ← USER CONFIG
    40.052%  diskcache/core.py       6 functions
    12.514%  typing.py               9 functions
     4.247%  matplotlib/colors.py    1 function
```

These percentages exceed 100 % because `scorpion` reports
per-CPU-core utilization. The relative ranking is still meaningful:

- **PyYAML scanner is the dominant project-code hotspot** by a wide
  margin. It is also the *only* third-party dep actively called
  during this profile (32 distinct scanner functions sample).
- **`kahndor.py`** is the next project-code hotspot. `load`,
  `Instruct.override`, `Instruct.clear_meta` — this is the config
  system parsing `models.yaml` / `nchantrs.yaml` repeatedly.
- **`matplotlib.colors`** appears despite the app not visibly using
  matplotlib. Some transitive import pulls it in; that's a free win
  to remove.
- **`diskcache.core.Disk.fetch`** is the largest per-line memory
  growth point (+10 MB). This is the same line that shows up at
  max_footprint_fname. Diskcache is used as a KV cache; we are
  probably storing large serialized objects we shouldn't.

### 1.3 Static-analysis findings (file:line)

Subagents reviewed code architecture in parallel with this profile
analysis. Concrete hot-paths identified (this list is what the plan
acts on):

| Finding | Source | Severity |
|---|---|---|
| `models.py:25–48` — eager imports of `pandas`, `numpy`, `pyffice`, `MicroMole`, `pycurity`, `subtrix.uuid`, plus `nchantdoffice.widgets.catalogs` (which itself imports pandas at `catalogs.py:22`). Every `nchantdoffice.*` import pays this cost. | code | **P0** |
| `models.py:5,955 LOC` — single class `NchantdOfficeCloakModel` with 50+ `get_*` methods. Hard to lazy-load because everything reaches through one file. | code | **P0** |
| `widgets/tables.py:73–109` — `setCellWidget` for every editable cell; `widgets/documents/workbooks/matricies.py` ~25 calls to `QTableWidgetItem()` and `insertRow(self.table.rowCount())` at lines 2040, 2168. | code | **P0** |
| `widgets/trees.py:97` — `QTreeWidget` with `clear() + addTopLevelItem(...)` on every refresh (`toolboxes.py:1450`). Zero `fetchMore`/`canFetchMore` anywhere. | code | **P1** |
| `catalogs.py:75–80` — 4 × `.sort_values(...)` + `drop_duplicates` + 2 × `reset_index` on a DataFrame inside `initModel()`. Each `.sort_values` materializes a new frame. | code | **P0** |
| `nchantdoffice/models.py` — 10 `SELECT *` reads via `get_view_documents_all` / `get_application_documents` (lines 1600, 1632, 1685, 1775, 1794, 2037, 2052, 2058, 2186, 2194, 2236). | code | **P1** |
| `models.py:1500–1520` `delete_tab` — N+1 `SELECT pid_txt FROM doc_tab WHERE tid_txt = ?` even when the tab is in memory; schema drift (column `tid_txt` vs `tid`) is wrapped in try/except. | code | **P1** |
| **Zero `CREATE INDEX` in the project. Zero `PRAGMA journal_mode = WAL`.** 11 schema-management hits in `updates/db.py`, all `CREATE TABLE` / `CREATE VIEW`. | code | **P1** |
| `wizards.py:182–188` — `OpenH264Downloader().download_and_extract()` runs **synchronously** on the GUI thread. The previous `CodecDownloadThread` path is commented out. | code | **P1** |
| `nchantdoffice.py:88–104` — `update_checker.check()` does a network round-trip on `run_on_launch`. Wrapped in try/except so it never *blocks* failure, but adds latency. | code | **P2** |
| `license/remote.py:537, :543` — `asyncio.run(...)` wraps every sync bootstrap/refresh, blocking the calling thread (often GUI) on a full event-loop creation+teardown. | code | **P2** |
| `widgets/controls/toolboxes.py:1367` `_PyofImportWorker` is the **only QThread** in the entire app. | code | **P1** (this is the *fix target*, not the problem) |
| `nchantrs/__init__.py` does eager `logging.basicConfig(...)` at import time — every downstream import runs it. | code | **P3** |
| `nchantrs/nchantrs.py:17` `import tracemalloc` and `:118–147` `analyze_strings/memory_analysis/memory_summary` — only used when `debug=True` but always imported. | code | **P3** |
| `models.py:44–45` — `from pyffice.document import PyfficeDocument` and `from pyffice.pyffice import PyfficeCodex` at module top. `pyffice/__init__.py` already uses lazy `__getattr__` for `PyfficeCodex` etc. — but the consumer is forcing eager import. | code | **P1** |
| `pyffice/` — `numpy`, `cv2`, `PIL`, `pandas`, `openpyxl`, `docx`, `PyPDF2`, `fitz`, `matplotlib` are imported **eagerly** in the *individual modules* (e.g. `images/utilities.py:21–22`, `matrix/matrix.py:21`, `matrix/spreadsheet.py:28`). | code | **P2** (this is fine for `pyffice` itself; bad for `nchantdoffice` callers) |
| `pyffice/container/__init__.py:18–22` — `from pyffice.container.{zip,tar,rar,sevenzip,binary} import (...)` — eager import of every archive format. | code | **P2** |
| `pyffice/diagrams/__init__.py:23–34` — eager import of `pyffice.diagrams.diagrams` + `pyffice.diagrams.formats` on first `import pyffice.diagrams`. | code | **P3** |
| `squirl/squirl/objnql/sonql.py:99–146` — **already has a real connection pool** with `max_connections`, `timeout`, `check_same_thread=False`. The infrastructure exists; consumers just don't pass a `ConnectionConfig`. | code | positive signal |

### 1.4 What the existing profile does NOT tell us

We **cannot** decide what to rewrite in Rust/C from this capture
alone. It is summary data with 15 memory samples over 152 s. We
need:

- A **memray** allocation trace (`memray run --native python -m
  nchantdoffice`) so we see exactly which call sites allocate the
  bytes in the curve above.
- A **py-spy dump** during a representative user action (open
  spreadsheet, open image, open PDF, run a calculation) at
  100 Hz — not just at boot.
- A **scorpion line-level trace** on the same actions, so we see
  per-function CPU time, not per-file.

**Phase 0 of the plan is exactly this measurement pass.**

---

## 2. Strategic Options (the user's question)

The user explicitly asked about four acceleration strategies. Here is
the honest answer before the plan, then the plan itself.

### 2.1 Move the back end to Rust?

**Verdict: yes, but only for the right pieces, and not first.**

Rust would replace Python in **a few specific layers**:

- `squirl.sonql` — the SQLite layer. A Rust implementation using
  `rusqlite` + connection pool would (a) eliminate GIL contention,
  (b) cut parse/serialize time on wide DataFrames, (c) give us a
  shared library both the desktop and any future `nchantdoffice.com`
  server can call. **High value.** Likely 5–10× speedup on
  table-scan paths and on `writeDF` for wide tables.
- `kahndor` — the YAML-based config system. Rust with `serde_yaml`
  is ~30× faster than PyYAML on the same config tree. Since the
  profile shows YAML scanning dominates boot CPU, **this is the
  single highest-bang-per-buck Rust target.** Could move from
  6,500 % PyYAML time to <500 % curosr `serde_yaml` time on boot.
- `pyffice.matrix` — pure-Python matrix ops over DataFrames. A Rust
  `polars`-backed replacement or a thin Rust + numpy crate wrapper
  would help large workbooks. **Medium value** — depends on usage
  data we don't have yet.
- `pyffice.images` — image processing loops over `PIL.Image`. Rust
  with `image` + `rayon` for parallelism would help batch
  operations but the desktop's image path is single-image so the
  gain is modest. **Low value.**

**Why not first.** Writing `nchantdoffice.models` (5,955 LOC) or
the widget layer in Rust is wrong — those layers are mostly Qt
bindings and glue code where Python is *fine*. The cost of a
binding layer (`pyo3`, `maturin`) is real and ongoing. Doing it
before we know which 5 % of the code is on the hot path is
premature optimization.

### 2.2 Create C-based modules?

**Verdict: don't, unless it's already on the path.**

The C-extension route (`CPython` C-API, Cython, cffi) is mostly
subsumed by Rust+`pyo3` today. Cython has a learning-curve problem
for a small team. cffi is for wrapping existing C libs (e.g.
`libjpeg`), which is not what we need.

**One legitimate C-target.** If profiling shows that a single
Python function is a hot inner loop with no Qt or DB dependency
(e.g. the cell-by-cell editor loop in `matricies.py`), then a
Cython `nogil=True` module can be a fast win with low risk.
This is a *per-function* decision, not a strategic direction.

**Don't** try to write the desktop's UI layer in C. PySide6 is
already C++ under the hood; Python is a thin script layer on top.

### 2.3 Implement async / multiprocess in pure Python?

**Verdict: yes, and this is the highest-impact early move.**

This is **Phase 2** of the plan below. Specifically:

- **Adopt `QThreadPool` + `QRunnable`** for every operation that
  currently blocks the GUI thread (codec download, update check,
  license bootstrap, document open, spreadsheet load). The
  framework is already imported (`nchantrs/libraries/pyqt.py:28–29`).
- **Use `concurrent.futures.ThreadPoolExecutor` for I/O and
  `ProcessPoolExecutor` for CPU** in `pyffice` (image batches, PDF
  render, CAD). `pyffice` currently has **zero** threading/
  subprocess calls — every port runs serially.
- **Use `asyncio` properly** in `license/remote.py` instead of
  `asyncio.run()` wrappers — switch to `qasync` to bridge with the
  Qt event loop so the GUI thread isn't blocked.

Multiprocessing specifically (separate processes) is **not** a
fit for the Qt desktop because Qt objects can't cross process
boundaries cleanly. We would still use multiprocessing for
**headless batch jobs** (the `flection` entry point already
attempts this via `pyularity` — see `nchantrs/nchantrs.py:84–116`).
A `ProcessPoolExecutor` inside `pyffice.compute` for batch
operations is appropriate.

### 2.4 Just optimize the existing Python?

**Verdict: yes, and this is phase 1.**

There is a large bag of cheap Python wins available before we
touch the toolchain:

- Lazy imports via `__getattr__` (PEP 562) — `pyffice/__init__.py`
  already shows the pattern.
- Stop re-parsing YAML on every config access.
- Fix the `catalogs.py` DataFrame sort chain.
- Add SQLite indexes; enable WAL; switch from `SELECT *` to
  column projection; pass `ConnectionConfig` to `sonql`.
- Replace `QTableWidget` + `setCellWidget` with `QTableView` +
  `QAbstractTableModel` + a delegate for editing.
- Replace `QTreeWidget` + `clear() + addTopLevel` with
  `QAbstractItemModel` + `fetchMore`.
- Cache `diskcache` results that are recomputed on every boot.

Realistically this buys 50–70 % of the achievable gain in pure
Python and de-risks the Rust rewrite (we will know which exact
functions to target).

---

## 3. The Recommended Plan

Five phases over **6–12 months**. Each phase is independently
shippable and produces a measurable improvement on a defined
metric. **All phases after Phase 0 are gated on Phase 0
measurements.**

### Phase 0 — Measurement (2–4 weeks)

**Goal.** Replace the current summary profile with line-level,
allocation-level, and per-action traces. Until this is done, all
later phases are partially guesswork.

**Deliverables.**

1. **Memray allocation trace at boot.**
   ```bash
   QT_QPA_PLATFORM=offscreen memray run \
     --native -o memray-boot.bin \
     python -m nchantdoffice
   memray flamegraph memray-boot.bin -o memray-boot.html
   ```
   Output: which call sites allocate the bytes in the 19 GB curve.

2. **Per-action `py-spy dump` on five canonical user actions:**
   - Boot to first paint (already have this; redo with line-level).
   - Open a 1000-row notebook.
   - Open a 50-page PDF.
   - Import a `.pyof` (test data already exists at
     `widgets/controls/toolboxes.py:_PyofImportWorker`).
   - Run a calc in `widgets/documents/workbooks/calculators.py`.

3. **`scorpion --line` capture** with the same actions so we get
   per-line Python time, not just per-file. The existing profile
   already proved the tool works.

4. **A reproducible benchmark harness** — synthetic documents
   (1k-row CSV, 50-page PDF, 4 MP photo) committed to the repo
   so we can compare phases. Place under `bench/` at the repo
   root; run on a defined machine spec.

5. **A baseline `perf.md`** committed to the repo capturing
   boot time, peak RSS at boot+30s, peak RSS at boot+5min, and
   the 5 user-action timings. Every phase updates this doc and
   the diff is the evidence the phase shipped.

**Exit criteria.** A benchmark that fits in CI. The commit
includes the harness, the baseline numbers, and the
representative data.

**Risk.** Low. We are not changing code, only measuring.

---

### Phase 1 — Cheap Python wins (4–8 weeks)

**Goal.** Capture the 50–70 % gain available without touching the
toolchain. Ship each item as its own PR so we can attribute gains.

**Sub-phases, in priority order:**

1. **Lazy imports in `nchantdoffice/models.py`** (PR: "models
   lazy-load heavy deps").
   - Move `pandas`, `numpy`, `pyffice.document`, `pyffice.pyffice`,
     `MicroMole`, `pycurity`, `subtrix.uuid`, and
     `nchantdoffice.widgets.catalogs` out of module scope and into
     the methods that actually use them. Use the
     `pyffice/__init__.py` `__getattr__` pattern.
   - Split `models.py` into `models/{documents,users,trees,dbupdate}.py`
     along existing method boundaries. `NchantdOfficeCloakModel`
     becomes a thin facade that imports from sub-modules on first
     attribute access.
   - Expected gain: 1.5–3 s off cold boot; 30–60 % drop in RSS at
     boot.

2. **YAML once at boot, not on every config access** (PR:
   "kahndor cache").
   - Wrap every `kahndor.load(...)` call site so the result is
     `functools.lru_cache`'d on the file path + mtime.
   - Replace the `models.py` import side-effect of loading all
     `_data_/*.yaml` with a single load keyed by config name.
   - Expected gain: 30–70 % drop in `yaml/scanner.py` time per
     boot.

3. **Fix the `catalogs.py` sort chain** (PR: "catalogs single-pass
   sort").
   - Replace the 4 × `.sort_values(...)` chain with a single
     `sort_values(by=[...])` and dedupe via `drop_duplicates`.
     Add a benchmark under `bench/catalogs_sort.py` showing
     before/after on the 1000-document synthetic catalog.
   - Expected gain: 5–10× speedup on `initModel()` for catalogs
     with >100 docs.

4. **Add SQLite indexes + WAL** (PR: "db indexes + WAL").
   - In `updates/db.py`, after each `CREATE TABLE`, add a
     `CREATE INDEX IF NOT EXISTS` on the columns the
     `get_view_documents_all` and `get_application_documents`
     queries filter by (need to confirm columns; the
     subagent flagged `pid_txt`, `tid_txt`, `pid_txt`, `nodetyp`,
     and timestamp columns).
   - Open connections with `journal_mode=WAL`,
     `synchronous=NORMAL`, `temp_store=MEMORY`, `mmap_size=2GB`.
   - Wire `nchantdoffice.models` to pass a `ConnectionConfig` to
     `squirl.objnql` rather than re-creating raw sqlite3
     connections.
   - Expected gain: 5–50× on queries that currently scan (depends
     on row count; no current row count data — Phase 0 must
     measure first).

5. **Defer boot-path network** (PR: "boot net async").
   - Re-enable `CodecDownloadThread` (the path at
     `wizards.py:182–186` is commented out). Move
     `update_checker.check()` and `OpenH264Downloader` to a
     `QTimer.singleShot(0, …)` after first paint. Wrap
     `license/remote.py:537, :543` in a proper Qt-asyncio bridge
     (`qasync`) so we stop paying `asyncio.run` setup cost.
   - Expected gain: removes the 5–30 s UI freeze on first
     install / refresh flows.

6. **Replace `QTableWidget` + `setCellWidget` with
   `QTableView` + `QAbstractTableModel`** (PR: "spreadsheet
   model").
   - In `widgets/tables.py:73–109`, build a `NchantdTableModel`
     that wraps the in-memory data and emits `dataChanged` on
     edits. Move the `QDateTimeEdit`/`QComboBox`/`QCheckBox`/
     `QSpinBox` to a `QStyledItemDelegate` so we only build them
     for the *active* cell, not every cell.
   - In `widgets/documents/workbooks/matricies.py`, replace the
     `QTableWidgetItem()` ×25 sites with `model.setData(...)`
     calls. Reserve `setRowCount(...)` for the bulk sizing pass.
   - Expected gain: 10–100× on editable spreadsheets; the
     subagent's worst case (1,000 child widgets per sheet)
     becomes zero.

7. **Replace `QTreeWidget` with `QAbstractItemModel` +
   `fetchMore`** (PR: "tree model").
   - Convert `widgets/trees.py:97 NchantdApplicationTree` and
     `widgets/controls/toolboxes.py:1450 refresh path` to a
     `QAbstractItemModel` that returns `canFetchMore=True` for
     unexpanded nodes. Back it with `squirl.objnql` paged
     queries (`LIMIT 200 OFFSET 0`).
   - Expected gain: removes the clear+repopulate freeze on
     `.pyof` import of large trees.

**Phase 1 cumulative target.** Boot time −40 % to −60 %.
Peak RSS at boot +30 s: −30 % to −50 %. Spreadsheet open on a
1000-row workbook: −50 % to −90 %.

**Risk.** Medium. The widget model conversion (items 6, 7) is the
riskiest piece because it touches every consumer of the current
`QTableWidget` API. Recommend landing items 1–5 first (low risk,
high gain) before starting 6 and 7.

---

### Phase 2 — Concurrency (4–8 weeks, starts overlapping Phase 1)

**Goal.** Move blocking work off the GUI thread. Establish the
worker pattern so future compute paths have a place to plug in.

**Sub-phases:**

1. **`QThreadPool` runner in `nchantrs/libraries`** (PR: "worker
   pool").
   - Add `nchantrs.workers.run_in_threadpool(fn, *args, on_done=None,
     on_error=None)` — a thin wrapper around `QThreadPool.globalInstance().start(QRunnable)`.
   - Migrate the existing `_PyofImportWorker` at
     `widgets/controls/toolboxes.py:1367` to use the new wrapper.
   - Migrate `OpenH264Downloader.download_and_extract` to use it.
   - Migrate `update_checker.check()` and the asyncio bridges in
     `license/remote.py`.

2. **Document-open as a background task** (PR: "async doc open").
   - Wrap `models.NchantdOfficeCloakModel.get_document(...)` in a
     worker that returns a `QFuture`-like wrapper or signals on
     completion. UI shows a spinner during open; the GUI thread
     never blocks >50 ms on a doc.

3. **`pyffice` ports concurrency** (PR: "pyffice workers").
   - Add a `pyffice.workers` module exposing a
     `ThreadPoolExecutor` (default size = `os.cpu_count()`) and a
     `ProcessPoolExecutor` for batch jobs.
   - Migrate the importable CPU ports:
     `images.utilities`, `images.palettes`, `matrix.spreadsheet`,
     `matrix.matrix` to use them for batch operations. Leave
     single-call paths synchronous.

4. **Bridge `asyncio` and Qt** (PR: "qasync bridge").
   - Replace `asyncio.run` in `license/remote.py:537, :543` with
     a `qasync.QEventLoop` so the existing async functions can be
     `await`ed directly from Qt slots.
   - Expected gain: removes the event-loop startup cost per
     license call (~50–200 ms each).

**Phase 2 cumulative target.** Perceived latency to first
interaction: −70 %. Update check and license bootstrap no longer
freeze the UI.

**Risk.** Medium. Threading bugs are hard to repro; recommend
adding a stress-test harness in `bench/stress_qthread.py` before
starting.

---

### Phase 3 — Rust where it pays (8–16 weeks)

**Goal.** Replace the two highest-RoI layers with Rust + `pyo3`
+ `maturin`, kept behind feature flags so we can roll back per
layer.

**Sub-phases (in priority order):**

1. **`kahndor-rs`** — reimplement the config system in Rust with
   `serde_yaml` + `serde_json`. Expose the same Python API via
   `pyo3`. Use `lru` for the cache.
   - **Rationale.** Phase 0 will confirm PyYAML is the dominant
     CPU hotspot; this is the cleanest extraction (pure data, no
     Qt).
   - **Cost.** ~6–10 engineer-weeks for a clean
     forward-compatible reimplementation.
   - **Expected gain.** 10–30× on YAML parse; ~10 % off boot.

2. **`sonql-rs`** — reimplement the `squirl.objnql` SQLite layer
   in Rust using `rusqlite` + a typed query builder. Keep the
   `pandas.DataFrame` boundary — `pyo3` can hand back a
   `numpy.ndarray` view that pandas wraps.
   - **Rationale.** Already has a pool; a Rust pool can hold
     open transactions and skip the per-query GIL/socket setup.
   - **Cost.** ~12–20 engineer-weeks including integration tests
     with existing schemas.
   - **Expected gain.** 5–10× on `SELECT *` paths; 2–5× on
     `writeDF` for wide tables; eliminates GIL contention for
     concurrent readers.

3. **Optional: `pyffice.compute`** — a Rust + `polars` replacement
   for `pyffice.matrix.matrix` and `pyffice.matrix.spreadsheet`
   pure-Python ops.
   - **Rationale.** Phase 0 will tell us whether these are on the
     hot path. Likely yes for users with >10K-row workbooks.
   - **Cost.** ~8–12 engineer-weeks.
   - **Expected gain.** 5–20× on big-workbook math.

**Phase 3 cumulative target.** Boot time −70 %. DB-heavy
operations −80 %. Workbook math −50 % to −80 %.

**Risk.** High but bounded. Each sub-phase is shippable and
reversible behind a feature flag (`NCHANTDOFFICE_USE_NATIVE_KAHNDOR=1`).
Recommend not starting Phase 3 until Phase 1 has shipped and the
benchmark harness from Phase 0 is in CI.

---

### Phase 4 — Cache and memory shape (4–6 weeks, overlaps Phase 3)

**Goal.** Eliminate the RSS growth curve seen in the profile.

**Sub-phases:**

1. **Replace `diskcache` with `redis` or in-memory `lru`** for the
   transient cache. Audit every `diskcache.Cache(...)`
   instantiation and ensure eviction is configured.
2. **Squirl connection pool audit.** Confirm the `sonql`
   `ConnectionConfig` is reused (not per-call). Confirm
   `check_same_thread=False` is set so the pool can serve the
   `QThreadPool` workers from Phase 2.
3. **`pandas.DataFrame` lifecycle review.** Many sites in
   `models.py` create DataFrames on the fly; audit for retention
   by parent widgets. Switch to `pd.DataFrame` writes with
   `del` in `finally:` blocks where the frame is large.
4. **Memory limit + restart.** As an interim measure, watch the
   process RSS and offer a graceful restart at 4 GB. The
   in-process fix is in Phase 4; the restart is the user-visible
   safety net.

**Phase 4 cumulative target.** Stable RSS; no 19 GB curve.

**Risk.** Low. Most of this is hygiene + an audit.

---

### Phase 5 — Sustained cadence (ongoing)

**Goal.** Make perf gains non-regressive.

1. **`perf.md` in CI.** Run the Phase 0 benchmark on every PR;
   fail the PR if boot time regresses >5 %. Re-baseline monthly.
2. **`py-spy` flamegraph in CI on schedule.** Weekly cron,
   attached to `perf.md`. Manual review monthly.
3. **No new `QTableWidget` / `QTreeWidget` use.** Lint rule via
   `ruff` custom check (or pre-commit grep) blocking new
   `setCellWidget` / `addTopLevelItem` usages. Exception list
   lives in `pyproject.toml` with reason per entry.
4. **No new module-level heavy imports.** Lint rule banning
   `import pandas`, `import numpy`, `import pyffice.document`,
   `import pyffice.pyffice`, `import aiohttp`, `import matplotlib`
   outside `pyffice` package boundary.
5. **Dependency budget.** Track cold-boot import time per
   dependency; ban new deps that add >100 ms cold boot.

---

## 4. Cost & ROI Summary

| Phase | Effort (eng-weeks) | Target Gain (perceived latency) | Risk |
|---|---|---|---|
| 0 — Measurement | 2–4 | enables everything else | Low |
| 1 — Cheap Python | 4–8 | 40–60 % | Low–Med |
| 2 — Concurrency | 4–8 | 70 % | Medium |
| 3 — Rust | 8–20 (split per layer) | 70–80 % cumulative | High (per layer) |
| 4 — Memory | 4–6 | stable RSS | Low |
| 5 — Cadence | ongoing | keeps gains | Low |

**Total estimate to "fast enough for normal users":** ~22–40
engineer-weeks, achievable in one quarter with a small focused
team. Most of that is Phase 1 + Phase 2; Phase 3 is optional
but high-payoff once we have Phase 0 data confirming the
targets.

---

## 5. What we are explicitly NOT doing (and why)

- **Not rewriting `models.py` (5,955 LOC) in Rust.** Almost all of
  it is glue and Qt-binding code where Python is fine. The cost
  would dominate Phase 3 for no measurable gain.
- **Not rewriting `widgets/` in C++. PySide6 is already C++; the
  Python is a thin script layer.
- **Not adopting Qt6 advanced features (e.g. QML, scene graph)
  for perf reasons.** That is a separate UX-modernization
  project; conflating it with perf would balloon scope.
- **Not moving to a different DB engine.** SQLite is the right
  answer for a desktop app with local data; the issue is
  indexes + WAL + connection pooling, not the engine.
- **Not pursuing `mypyc` or PyPy.** `mypyc` doesn't compile Qt
  apps cleanly; PyPy has poor PySide6 support. Both would be
  distractions.
- **Not pursuing distributed compute (Dask, Ray).** This is a
  desktop app; parallelism target is the local box.
- **Not adopting a micro-framework like Flet.** The PySide6 stack
  is committed; rewriting the UI is out of scope for "perf".

---

## 6. Open Questions for the Operator

These are decisions the plan depends on but I cannot answer
alone. Please confirm before Phase 1 starts:

1. **Acceptable boot time target?** Plan assumes "≤3 s cold boot
   to first paint on the reference machine". Confirm.
2. **Acceptable peak RSS at idle?** Plan assumes "≤500 MB".
   Currently 1.5 GB at 60 s. Confirm.
3. **PySide6 only?** The plan keeps PySide6. If Qt6/QML is on
   the table for UX reasons, Phase 3 will need to plan around it.
4. **Backward-compat budget?** The Rust rewrite of `kahndor`
   will preserve the public API but the internal data layout may
   change. Confirm we accept that risk for the gain.
5. **CI machine spec.** Phase 0 benchmark needs a fixed
   hardware profile; otherwise perf tracking is noise. Suggest
   the same machine used for the existing memray capture.
6. **Target user population.** Solo power users vs multi-user
   enterprise changes which Phase 3 sub-phases pay off. The plan
   currently weights toward solo power users (large workbooks,
   batch image import).

---

## 7. Appendix — File:line Index of Hotspots

This is the cross-reference for the audit. Use it when sizing
PRs.

### nchantdoffice (desktop)

| File:line | Issue | Phase |
|---|---|---|
| `models.py:25–48` | Eager heavy imports | 1.1 |
| `models.py:5955 LOC` | Monolithic model | 1.1 |
| `models.py:1600, 1632, 1685, 1775, 1794, 2037, 2052, 2058, 2186, 2194, 2236` | `SELECT *` reads | 1.4 |
| `models.py:1500–1520` | `delete_tab` N+1 | 1.4 |
| `widgets/tables.py:73–109` | `setCellWidget` per cell | 1.6 |
| `widgets/documents/workbooks/matricies.py:2040, 2168` | `insertRow(rowCount())` | 1.6 |
| `widgets/documents/workbooks/matricies.py` ~25 sites | `QTableWidgetItem()` | 1.6 |
| `widgets/trees.py:97` | `QTreeWidget` | 1.7 |
| `widgets/controls/toolboxes.py:1450` | tree `clear()` + repopulate | 1.7 |
| `widgets/controls/toolboxes.py:1367` | `_PyofImportWorker` (the *one* QThread) | 2.1 |
| `catalogs.py:75–80` | 4 sorts + dedupe + 2 reset | 1.3 |
| `widgets/panes/new.py:35` | eager `pyffice.web.url` | 1.1 |
| `widgets/documents/atnrg/contacts.py:35`, `prompts.py:51`, `dialogs.py:27`, `dialog_documents.py:27` | eager pyffice imports | 1.1 |
| `wizards.py:182–188` | Sync codec download | 1.5 |
| `nchantdoffice.py:88–104` | Sync update check | 1.5 |
| `nchantdoffice.py:155` | Sync select_initial_node | 1.5 |
| `__init__.py:5–12` | Eager `utilities.constants` import | 1.1 |
| `updates/db.py` (all) | 0 `CREATE INDEX`, 0 `PRAGMA journal_mode` | 1.4 |

### nchantrs (framework)

| File:line | Issue | Phase |
|---|---|---|
| `nchantrs.py:17` | `import tracemalloc` always | 3 (cleanup) |
| `nchantrs.py:118–147` | `analyze_strings`/`memory_analysis`/`memory_summary` always imported | 3 |
| `nchantrs.py:55–82` `nchantment` | 5-step serial boot | 1.5, 2 |
| `__init__.py` | Eager `logging.basicConfig` | 3 |
| `widgets/browsers/downloads.py:551` | `CodecDownloadThread` exists but is not used | 2.1 |
| `widgets/browsers/services.py:93` | One ad-hoc `threading.Thread` for port-check | 2.1 (use pool) |
| `libraries/pyqt.py:28–29` | Imports `QThread`, `QThreadPool` (good) | (already there) |

### pyffice (library)

| File:line | Issue | Phase |
|---|---|---|
| `__init__.py:35–50` | `__getattr__` lazy export (good — model for nchantdoffice) | n/a |
| `images/utilities.py:21–22` | `cv2` + `numpy` eager | 2.3 |
| `images/pdfs.py:22–25` | `PyPDF2` + `fitz` eager | 2.3 |
| `images/palettes.py:20` | `PIL.Image` eager | 2.3 |
| `images/images.py:26` | PIL eager | 2.3 |
| `matrix/spreadsheet.py:28` | `pandas` eager | 2.3 |
| `matrix/matrix.py:21` | `pandas` eager | 2.3 |
| `ports/msports.py:19–23` | `openpyxl` ×4 eager | 2.3 |
| `script/script.py:20–22` | `docx` eager | 2.3 |
| `items/items.py:20` | `pandas` eager | 2.3 |
| `items/colors.py:24–29` | `cv2` + `numpy` + `PIL` + `matplotlib` eager | 2.3, 4 |
| `container/__init__.py:18–22` | All 5 archive formats eager | 2.3 |
| `diagrams/__init__.py:23–34` | diagrams eager | 2.3 |

### squirl (DB layer)

| File:line | Issue | Phase |
|---|---|---|
| `objnql/sonql.py:99–146` | Real pool already exists | 1.4 (use it) |
| `objnql/sonql.py` | No built-in paging | 1.7 (need fetchMore paged reads) |
| `orgnql/gronql.py:63` | Direct `sqlite3.connect` outside pool | 1.4 |

---

## 8. References

- **Existing profile:** `/home/solubrew/.hermes/projects/nchantdoffice/profile.json`,
  `profile.html`
- **State docs:** `nchantdoffice/README.md`, `nchantrs/STATE.md`,
  `pyffice/README.md`
- **Known perf discussions:** `nchantdoffice/docs/webview-perf-review_*.md`
  (the "blank load commits LATE and wins" webview perf issue),
  `nchantdoffice/docs/update-process-review_20260810.md`
- **Skills used:** `multi-repo-analysis`,
  `sb-stack-codebase-review`, `codebase-inspection`

— end of plan —
