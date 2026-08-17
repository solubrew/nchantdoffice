# Directory Structure Report

**Root:** `/home/solubrew/.senbai/workspace/projects/nchantdoffice`
**Maximum Depth:** 4
**Include Hidden Files:** False
**Generated:** 2026-07-16 21:16:32

> **STALE SNAPSHOT (2026-08-16, gamma `5b6397e`).** This file
> was generated 2026-07-16 and predates the
> T-NEW-110..147 burst. **Do not rely on it for current state.**
> Regenerate before consuming:
>
> ```bash
> tree -L 4 -I '__pycache__|*.egg-info|node_modules|.ruff_cache|.pytest_cache|dist' .
> ```
>
> Notable drift since this snapshot was generated:
>
> - `nchantdoffice/config.py` was referenced in CHANGES.md
>   `[Unreleased]` "Added" but never existed on `gamma` —
>   configuration lives in `nchantdoffice/utilities/config.py`
>   + `nchantdoffice/utilities/constants.py`.
> - `tests/unit/` has 18 top-level entries (the 2026-07-16
>   snapshot showed 0 — the unit suite was added during the
>   T-NEW-058..137 burst).
> - `tests/qt_parent/` has 1 entry (`server.py`) — T-NEW-122
>   prep for Qt-using tests.
> - `nchantdoffice/sync/` is still here (subprocess + QLocalServer
>   helpers — predates this snapshot; ignore the wording above
>   that said it was added).
> - `nchantdoffice/dialogs/` and `nchantdoffice/widgets/` were
>   re-organised (T-NEW-114, T-NEW-130, T-NEW-138..141).
> - `STATE.md` is gone — the README no longer references it
>   either; project status now lives in `TODOs.md` §1.
>
> For the live tree snapshot use `tree` per the command above,
> or read the [`README.md`](./README.md) §"Project Structure"
> block (manually maintained, last edited 2026-08-16).

---

```text
nchantdoffice/
├── cmds/
│   ├── run/
│   │   ├── _data_/
│   │   │   ├── install.yaml [1.2 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 08:11:54
│   │   │   ├── launch.yaml [94.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 08:11:54
│   │   │   └── run.yaml [22.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 08:11:54
│   │   ├── install.py [1.9 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 08:11:54
│   │   ├── launch.py [2.0 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 08:11:54
│   │   └── run.py [2.5 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 08:11:54
│   ├── zz-hist_/
│   │   ├── run_gui.sh [353.0 B]  last modified: 2026-06-30 12:02:38  last accessed: 2026-07-16 09:08:24
│   │   ├── runNchantdAXN.py [817.0 B]  last modified: 2026-06-30 12:02:38  last accessed: 2026-07-16 09:08:24
│   │   ├── runNchantdOfficePaid.py [1.8 KB]  last modified: 2026-06-30 12:02:38  last accessed: 2026-07-16 09:08:24
│   │   ├── runNchantdOfficePremium.py [1.8 KB]  last modified: 2026-06-30 12:02:38  last accessed: 2026-07-16 09:08:24
│   │   ├── runNchantdTool.py [2.8 KB]  last modified: 2026-06-30 12:02:38  last accessed: 2026-07-16 09:08:24
│   │   └── test_runNchantdOffice.py [2.3 KB]  last modified: 2026-06-30 12:02:38  last accessed: 2026-07-16 09:08:24
│   ├── nchantrs_applicationviews.log [0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 15:09:13
│   ├── nchantrs_dialogs.log [0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 15:09:13
│   ├── profile.html [6.3 MB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   ├── profile.json [4.6 MB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   ├── profile.svg [1.1 MB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   ├── runNchantdDocument.py [3.8 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   ├── runNchantdOffice.py [3.9 KB]  last modified: 2026-07-16 20:39:04  last accessed: 2026-07-16 20:39:04
│   ├── runTest.py [2.0 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   └── sync.sh [1.1 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
├── docs/
│   ├── api/
│   │   ├── __main__.md [25.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.__main__.md [53.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.cli.md [43.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.md [35.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.models.md [49.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.nchantdoffice.md [63.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.views.md [47.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.advertisements.md [81.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.catalogs.md [69.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.documents.audio.md [83.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.documents.charts.md [85.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.documents.documents.md [91.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.documents.engrg.cad.md [91.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.documents.engrg.charts.md [97.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.documents.engrg.database.md [101.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.documents.engrg.engineering.md [107.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.documents.engrg.freecad.md [99.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.documents.engrg.md [83.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.documents.engrg.process.md [99.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.documents.engrg.tasks.md [95.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.documents.filesystems.md [95.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.documents.finance.finance.md [103.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.documents.finance.md [87.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.documents.forms.md [83.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.documents.games.games.md [95.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.documents.games.md [83.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.documents.games.nchantris.md [103.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.documents.journal.md [87.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.documents.managers.calendars.md [109.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.documents.managers.contacts.md [107.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.documents.managers.md [89.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.documents.managers.travel.md [103.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.documents.md [71.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.documents.media.audio.md [95.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.documents.media.forms.md [95.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.documents.media.images.md [97.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.documents.media.md [83.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.documents.media.notes.md [95.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.documents.media.pdfs.md [93.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.documents.media.scripts.md [99.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.documents.media.shows.md [95.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.documents.media.video.md [95.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.documents.notebooks.md [91.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.documents.pdf.md [79.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.documents.presentation.md [97.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.documents.spreadsheet.md [95.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.documents.surveys.md [87.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.documents.text.md [81.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.documents.web.md [79.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.extensions.extensions.md [95.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.extensions.md [73.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.md [51.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.settings.md [69.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.tabs.md [61.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.tags.md [61.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.timelines.md [71.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── nchantdoffice.widgets.trees.md [63.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   └── nchantdoffice.widgets.widgets.md [67.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   ├── index.md [239.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 08:11:54
│   ├── nchantrs_webview_render_fixes.md [10.8 KB]  last modified: 2026-07-08 22:08:14  last accessed: 2026-07-16 08:11:54
│   └── reference.md [104.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
├── nchantdoffice/
│   ├── _data_/
│   │   ├── cli.yaml [0 B]  last modified: 2026-07-16 20:39:04  last accessed: 2026-07-16 20:39:04
│   │   ├── config.yaml [0 B]  last modified: 2026-07-16 20:39:04  last accessed: 2026-07-16 20:39:04
│   │   ├── models.yaml [23.7 KB]  last modified: 2026-07-16 17:19:22  last accessed: 2026-07-16 17:19:28
│   │   ├── nchantdoffice.yaml [2.4 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   └── views.yaml [0 B]  last modified: 2026-07-16 20:39:04  last accessed: 2026-07-16 20:39:04
│   ├── dialogs/
│   │   ├── _data_/
│   │   │   ├── dialogs.yaml [0 B]  last modified: 2026-07-16 20:39:04  last accessed: 2026-07-16 20:39:04
│   │   │   ├── documents.yaml [4.2 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   │   ├── imports.yaml [298.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   │   └── notifications.yaml [0 B]  last modified: 2026-07-16 20:39:04  last accessed: 2026-07-16 20:39:04
│   │   ├── dialogs.py [3.3 KB]  last modified: 2026-07-16 17:19:22  last accessed: 2026-07-16 17:19:28
│   │   ├── documents.py [13.9 KB]  last modified: 2026-07-16 17:19:22  last accessed: 2026-07-16 17:19:28
│   │   ├── imports.py [4.8 KB]  last modified: 2026-07-16 17:19:22  last accessed: 2026-07-16 17:19:28
│   │   └── notifications.py [2.0 KB]  last modified: 2026-07-16 17:19:22  last accessed: 2026-07-16 17:19:28
│   ├── updates/
│   │   ├── _data_/
│   │   │   └── db.yaml [11.3 KB]  last modified: 2026-07-16 17:19:22  last accessed: 2026-07-16 17:19:28
│   │   └── db.py [2.5 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   ├── utilities/
│   │   ├── _data_/
│   │   │   ├── config.yaml [889.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   │   ├── constants.yaml [0 B]  last modified: 2026-07-16 20:39:04  last accessed: 2026-07-16 20:39:04
│   │   │   ├── imports.yaml [0 B]  last modified: 2026-07-16 20:39:04  last accessed: 2026-07-16 20:39:04
│   │   │   ├── links.yaml [0 B]  last modified: 2026-07-16 20:39:04  last accessed: 2026-07-16 20:39:04
│   │   │   ├── policies.yaml [0 B]  last modified: 2026-07-16 20:39:04  last accessed: 2026-07-16 20:39:04
│   │   │   ├── users.yaml [1.1 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   │   └── utilities.yaml [0 B]  last modified: 2026-07-16 20:39:04  last accessed: 2026-07-16 20:39:04
│   │   ├── config.py [4.8 KB]  last modified: 2026-07-16 17:19:22  last accessed: 2026-07-16 17:19:28
│   │   ├── constants.py [969.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── imports.py [3.0 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── links.py [4.6 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── policies.py [1.8 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── users.py [2.5 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   └── utilities.py [4.8 KB]  last modified: 2026-07-08 22:13:22  last accessed: 2026-07-16 09:08:24
│   ├── widgets/
│   │   ├── _data_/
│   │   │   ├── advertisements.yaml [0 B]  last modified: 2026-07-16 17:19:22  last accessed: 2026-07-16 19:54:32
│   │   │   ├── catalogs.yaml [211.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   │   ├── settings.yaml [751.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   │   ├── tabs.yaml [0 B]  last modified: 2026-07-16 17:19:22  last accessed: 2026-07-16 19:54:32
│   │   │   ├── tags.yaml [0 B]  last modified: 2026-07-16 17:19:22  last accessed: 2026-07-16 19:54:32
│   │   │   ├── trees.yaml [0 B]  last modified: 2026-07-16 17:19:22  last accessed: 2026-07-16 19:54:32
│   │   │   └── widgets.yaml [0 B]  last modified: 2026-07-16 17:19:22  last accessed: 2026-07-16 19:54:32
│   │   ├── config/
│   │   │   ├── _data_/
│   │   │   │   └── ...
│   │   │   ├── accounts.py [15.8 KB]  last modified: 2026-07-16 17:19:22  last accessed: 2026-07-16 17:19:28
│   │   │   ├── apis.py [3.2 KB]  last modified: 2026-07-16 17:19:22  last accessed: 2026-07-16 17:19:28
│   │   │   ├── automations.py [2.7 KB]  last modified: 2026-07-16 17:19:22  last accessed: 2026-07-16 17:19:28
│   │   │   ├── help.py [3.9 KB]  last modified: 2026-07-16 17:19:22  last accessed: 2026-07-16 17:19:28
│   │   │   ├── journal.py [13.9 KB]  last modified: 2026-07-16 17:19:22  last accessed: 2026-07-16 17:19:28
│   │   │   ├── security.py [2.0 KB]  last modified: 2026-07-16 17:19:22  last accessed: 2026-07-16 17:19:28
│   │   │   ├── settings.py [19.1 KB]  last modified: 2026-07-16 17:19:22  last accessed: 2026-07-16 17:19:28
│   │   │   ├── sources.py [18.1 KB]  last modified: 2026-07-16 17:19:22  last accessed: 2026-07-16 17:19:28
│   │   │   ├── storage.py [5.2 KB]  last modified: 2026-07-16 17:19:22  last accessed: 2026-07-16 17:19:28
│   │   │   └── uninstall.py [2.0 KB]  last modified: 2026-07-16 17:19:22  last accessed: 2026-07-16 17:19:28
│   │   ├── controls/
│   │   │   ├── _data_/
│   │   │   │   └── ...
│   │   │   ├── buttons.py [3.1 KB]  last modified: 2026-07-16 17:19:22  last accessed: 2026-07-16 17:19:28
│   │   │   ├── menus.py [2.0 KB]  last modified: 2026-07-16 17:19:22  last accessed: 2026-07-16 17:19:28
│   │   │   ├── toolbars.py [13.5 KB]  last modified: 2026-07-16 17:19:22  last accessed: 2026-07-16 17:19:28
│   │   │   └── toolboxes.py [19.4 KB]  last modified: 2026-07-16 17:19:22  last accessed: 2026-07-16 17:19:28
│   │   ├── documents/
│   │   │   ├── _data_/
│   │   │   │   └── ...
│   │   │   ├── analytics/
│   │   │   │   └── ...
│   │   │   ├── atnrg/
│   │   │   │   └── ...
│   │   │   ├── managers/
│   │   │   │   └── ...
│   │   │   ├── media/
│   │   │   │   └── ...
│   │   │   ├── workbooks/
│   │   │   │   └── ...
│   │   │   ├── __init__.py [659.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   │   ├── documents.py [29.2 KB]  last modified: 2026-07-16 17:19:22  last accessed: 2026-07-16 17:19:28
│   │   │   └── journal.py [13.3 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── items/
│   │   │   ├── _data_/
│   │   │   │   └── ...
│   │   │   └── items.py [10.0 KB]  last modified: 2026-07-16 17:19:22  last accessed: 2026-07-16 17:19:28
│   │   ├── panes/
│   │   │   ├── _data_/
│   │   │   │   └── ...
│   │   │   ├── charts.py [36.5 KB]  last modified: 2026-07-16 17:19:22  last accessed: 2026-07-16 17:19:28
│   │   │   ├── documents.py [26.4 KB]  last modified: 2026-07-16 17:19:22  last accessed: 2026-07-16 17:19:28
│   │   │   ├── files.py [4.8 KB]  last modified: 2026-07-16 17:19:22  last accessed: 2026-07-16 17:19:28
│   │   │   ├── models.py [3.0 KB]  last modified: 2026-07-16 17:19:22  last accessed: 2026-07-16 17:19:28
│   │   │   ├── new.py [17.9 KB]  last modified: 2026-07-16 17:19:22  last accessed: 2026-07-16 17:19:28
│   │   │   ├── objects.py [6.2 KB]  last modified: 2026-07-16 17:19:22  last accessed: 2026-07-16 17:19:28
│   │   │   ├── panes.py [1.4 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   │   ├── search.py [10.4 KB]  last modified: 2026-07-16 17:19:22  last accessed: 2026-07-16 17:19:28
│   │   │   ├── sources.py [26.4 KB]  last modified: 2026-07-16 17:19:22  last accessed: 2026-07-16 17:19:28
│   │   │   └── weather.py [2.3 KB]  last modified: 2026-07-16 17:19:22  last accessed: 2026-07-16 17:19:28
│   │   ├── __init__.py [0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 15:09:13
│   │   ├── advertisements.py [2.0 KB]  last modified: 2026-07-08 22:08:14  last accessed: 2026-07-16 09:08:24
│   │   ├── catalogs.py [11.0 KB]  last modified: 2026-07-16 17:19:22  last accessed: 2026-07-16 17:19:28
│   │   ├── settings.py [4.2 KB]  last modified: 2026-07-16 17:19:22  last accessed: 2026-07-16 17:19:28
│   │   ├── tabs.py [6.7 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── tags.py [2.7 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── trees.py [8.1 KB]  last modified: 2026-07-16 17:19:22  last accessed: 2026-07-16 17:19:28
│   │   └── widgets.py [7.1 KB]  last modified: 2026-07-16 20:39:04  last accessed: 2026-07-16 20:39:04
│   ├── wizards/
│   │   ├── _data_/
│   │   │   └── wizards.yaml [275.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   └── wizards.py [15.4 KB]  last modified: 2026-07-16 17:19:22  last accessed: 2026-07-16 17:19:28
│   ├── __init__.py [313.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 08:11:54
│   ├── __main__.py [2.6 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 08:11:54
│   ├── cli.py [13.4 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   ├── config.py [18.0 KB]  last modified: 2026-07-16 17:19:22  last accessed: 2026-07-16 17:19:28
│   ├── models.py [93.3 KB]  last modified: 2026-07-16 17:19:22  last accessed: 2026-07-16 17:19:28
│   ├── nchantdoffice.py [5.5 KB]  last modified: 2026-07-16 17:19:22  last accessed: 2026-07-16 17:19:28
│   └── views.py [2.4 KB]  last modified: 2026-07-16 17:19:22  last accessed: 2026-07-16 17:19:28
├── tests/
│   ├── fixtures/
│   │   ├── test.bmp [1.8 MB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── test.csv [848.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── test.ctd [8.2 MB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── test.dia [1.4 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── test.doc [28.5 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── test.docx [704.0 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── test.gif [1.1 MB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── test.html [4.7 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── test.jpeg [30.6 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── test.json [127.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── test.mkv [15.9 MB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
│   │   ├── test.mm [10.0 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:25
│   │   ├── test.mp3 [1.4 MB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:25
│   │   ├── test.pdf [3.8 MB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:25
│   │   ├── test.png [36.8 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:25
│   │   ├── test.sqlite [22.6 MB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:25
│   │   ├── test.txt [19.1 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:25
│   │   ├── test.xlsx [5.8 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:25
│   │   └── test.yaml [280.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:25
│   └── unit/
│       ├── _data_/
│       │   ├── modelsTEST.yaml [3.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:25
│       │   ├── nchantdofficeTEST.yaml [3.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:25
│       │   ├── utilitesTEST.yaml [3.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:25
│       │   └── viewsTEST.yaml [3.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:25
│       ├── dialogs/
│       │   ├── _data_/
│       │   │   └── ...
│       │   ├── dialogsTEST.py [5.4 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:25
│       │   ├── documentsTEST.py [4.4 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:25
│       │   ├── importsTEST.py [6.6 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:25
│       │   └── notificationsTEST.py [3.3 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:25
│       ├── extensions/
│       │   ├── _data_/
│       │   │   └── ...
│       │   └── packages/
│       │       └── ...
│       ├── updates/
│       │   └── dbTEST.py [3.0 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:25
│       ├── utilities/
│       │   ├── _data_/
│       │   │   └── ...
│       │   ├── configTEST.py [3.9 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:25
│       │   ├── importsTEST.py [4.1 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:25
│       │   ├── linksTEST.py [3.6 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:25
│       │   ├── policiesTEST.py [3.0 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:25
│       │   ├── usersTEST.py [3.4 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:25
│       │   └── utilitiesTEST.py [2.7 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:25
│       ├── widgets/
│       │   ├── _data_/
│       │   │   └── ...
│       │   ├── atnr/
│       │   │   └── ...
│       │   ├── boards/
│       │   │   └── ...
│       │   ├── config/
│       │   │   └── ...
│       │   ├── controls/
│       │   │   └── ...
│       │   ├── documents/
│       │   │   └── ...
│       │   ├── items/
│       │   │   └── ...
│       │   ├── library/
│       │   │   └── ...
│       │   ├── panes/
│       │   │   └── ...
│       │   ├── advertisementsTEST.py [4.3 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:25
│       │   ├── catalogsTEST.py [7.0 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:25
│       │   ├── settingsTEST.py [5.4 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:25
│       │   ├── tabsTEST.py [3.3 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:25
│       │   ├── tagsTEST.py [4.3 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:25
│       │   ├── timelinesTEST.py [3.4 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:25
│       │   ├── treesTEST.py [3.3 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:25
│       │   └── widgetsTEST.py [3.6 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:25
│       ├── wizards/
│       │   └── wizardsTEST.py [4.2 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:25
│       ├── __init__.py [36.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:25
│       ├── __init__TEST.py [2.3 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:25
│       ├── __main__TEST.py [2.6 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:25
│       ├── modelsTEST.py [29.2 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:25
│       ├── nchantdofficeTEST.py [4.8 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:25
│       ├── test_config.py [1.6 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:25
│       └── viewsTEST.py [3.3 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:25
├── CHANGES.md [4.9 KB]  last modified: 2026-07-16 17:19:22  last accessed: 2026-07-16 17:19:28
├── CLI.md [1.3 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 08:11:54
├── CODING_STANDARDS.md [19.3 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
├── directory_tree.md [20.5 KB]  last modified: 2026-07-16 17:19:22  last accessed: 2026-07-16 17:19:28
├── LICENSE [897.0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
├── license_dependencies.txt [15.3 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
├── mkdocs.yml [4.1 KB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 08:11:54
├── nchantrs_dialogs.log [0 B]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 15:09:13
├── profile.html [15.7 MB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
├── profile.json [14.1 MB]  last modified: 2026-06-27 23:55:05  last accessed: 2026-07-16 09:08:24
├── PROJECT_TRACKER.yaml [40.8 KB]  last modified: 2026-07-08 22:08:14  last accessed: 2026-07-16 08:11:54
├── pyproject.toml [7.4 KB]  last modified: 2026-07-08 22:08:14  last accessed: 2026-07-16 08:11:54
├── reachable=False [0 B]  last modified: 2026-07-08 22:08:14  last accessed: 2026-07-16 15:09:13
├── README.md [3.3 KB]  last modified: 2026-07-16 17:19:22  last accessed: 2026-07-16 17:19:28
├── requirements.txt [251.5 KB]  last modified: 2026-07-08 22:08:14  last accessed: 2026-07-16 09:08:24
├── STATE.md [6.0 KB]  last modified: 2026-07-16 17:24:36  last accessed: 2026-07-16 17:24:39
├── test.ipynb [1.6 KB]  last modified: 2026-07-08 22:08:14  last accessed: 2026-07-16 09:08:24
├── TODOs.md [4.5 KB]  last modified: 2026-07-16 17:19:22  last accessed: 2026-07-16 17:19:28
└── uv.lock [937.4 KB]  last modified: 2026-07-08 22:08:14  last accessed: 2026-07-16 09:08:25
```

*File sizes are human-readable. Timestamps are in the local system timezone.*