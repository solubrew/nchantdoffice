# T-NEW-CRIT: pyside6pandas (qpandas) Metaclass Conflict

**Status:** Blocked — cannot rebuild self-contained .deb until fixed
**Affects:** pyside6pandas library, nchantdoffice gamma build
**Discovered:** 2026-08-06 during self-contained .deb install + run test
**Severity:** Critical — nchantdoffice launches through full Qt WebEngine
graphics initialization but fails to materialize the NchantdDataFrameTable
view. There is **no known workaround** within sasquatch; the fix MUST
land in either **nchantdoffice** or the upstream library.

---

## Failing trace (real nchantdoffice gamma, 688 MB self-contained .deb)

```
2026-08-06 11:54:18 ...  NchantdOffice configuration initialized - Version 0.0.1.0.1.4
2026-08-06 11:54:18 ...  Nchantrs v0.0.1.0.1.1 initialized
...
File "/usr/lib/nchantdoffice/nchantdoffice/__main__.py", line 33, in <module>
    from nchantrs.nchantrs import flection, nchantment
File "/usr/lib/nchantdoffice/internal/nchantrs/nchantrs.py", line 18, in <module>
    from nchantrs.widgets.applications.applications import NchantdCloak
File "/usr/lib/nchantdoffice/internal/nchantrs/widgets/applications/applications.py", line 12, in <module>
    from nchantrs.models.applicationmodels import NchantdCloakModel, NchantdPantiesModel
File "/usr/lib/nchantdoffice/internal/nchantrs/models/applicationmodels.py", line 9, in <module>
    from subtrix.subtrix import Mechanism
File "/usr/lib/nchantdoffice/internal/subtrix/subtrix.py", line 36, in <module>
    from .utilities import get_variable_data
File "/usr/lib/nchantdoffice/internal/subtrix/utilities/__init__.py", line 25, in <module>
    from uuid_extensions import uuid7
                ^^^^^^^^
ModuleNotFoundError: No module named 'uuid_extensions'
```

(FIXED — that's now the uuid7 shim. Next failure from the same .deb:)

```
File "/usr/lib/nchantdoffice/internal/pycurity/pyurity.py", line 12, in <module>
    from pycurity import kahndor
                ^^^^^^^^
ModuleNotFoundError: No module named 'pycurity'
...
File "/usr/lib/nchantdoffice/internal/nchantrs/nchantrs.py", line 479, in <module>
    from nchantrs.widgets.tables import *
File "/usr/lib/nchantdoffice/nchantdoffice/utilities/constants.py", line 27, in <module>
    from kahndor.logma import Logma
```

(Both those failed because pycurity/kahndor needed their gamma branch
checked out — now fixed in sasquatch via `ensure_ref_checked_out()`.)

**Next failure that is THIS bug:**

```
File "/usr/lib/nchantdoffice/internal/nchantrs/nchantrs.py", line 479, in <module>
    from nchantrs.widgets.tables import *
File "/usr/lib/nchantdoffice/internal/nchantrs/widgets/tables/tables.py", line 479, in <module>
    class NchantdDataFrameTable(NchantdWidgetMixin, qpandas.DataTableWidget):
TypeError: metaclass conflict: the metaclass of a derived class must be a
        (non-strict) subclass of the metaclasses of all its bases
```

---

## Root cause analysis

### The two base classes

`NchantdWidgetMixin` is a plain Python class:

```python
# nchantrs/widgets/widgets.py:78
class NchantdWidgetMixin(object):
    """A mixin that injects app/context/config/kahndor plumbing
    into every Nchantd* widget."""
    def init_variables(self): ...
    def initModel(self, ...): ...
    # ... no __metaclass__, no explicit metaclass kwarg
```

`qpandas.DataTableWidget` is the loaded-or-stubbed class:

```python
# nchantrs/libraries/qpandas.py:30-35
def _import_or_stub(module_path, attr, stub_factory) -> Any:
    import importlib
    try:
        module = importlib.import_module(module_path)
        return getattr(module, attr)
    except (ImportError, AttributeError, ModuleNotFoundError) as exc:
        return stub_factory()

# nchantrs/libraries/qpandas.py:55-58
class _DataTableWidget:
    """Stand-in for pyside6pandas.views.DataTableView.DataTableWidget."""
    def __init__(self, *args, **kwargs):
        pass

# nchantrs/libraries/qpandas.py:86
DataTableWidget = _import_or_stub(
    'pyside6pandas.views.DataTableView',
    'DataTableWidget',
    _DataTableWidget,
)
```

### Why the conflict fires

When `pyside6pandas` is **not installed**, `qpandas.DataTableWidget`
resolves to `_DataTableWidget`. When it **is installed**, it resolves to
the real `pyside6pandas.views.DataTableView.DataTableWidget` — which is
a `QWidget` subclass whose metaclass is `sip.wrappertype` (or
`Shiboken`/`PySide6`-specific). `NchantdWidgetMixin` has Python's
plain `type` as its metaclass.

Python's MRO rule for multiple inheritance is: the metaclass of the
derived class must be a (non-strict) subclass of the metaclasses of
all bases. When the two bases have unrelated metaclasses (`type` vs
`sip.wrappertype`), this check fails at class-creation time.

The stub class `_DataTableWidget` is fine against `type` (no conflict),
but the real `DataTableWidget` introduces the conflict whenever
`pyside6pandas` is installed — which is always in the self-contained
.deb/vendor/ (because `pyside6pandas` gets pip-installed as a wheel
dependency of `qtpandas` or because it's transitively pulled in by
one of nchantdoffice's deps).

### Three possible fix locations

1. **`pyside6pandas` library** — the upstream project. **`type`** should
   either:
   - Provide a `DataTableWidget` whose metaclass is `type` (i.e. not a
     Qt widget at all, but a "controller" object that uses a
     `QTableView` internally), OR
   - Document a recommended mixin pattern that uses
     `QObject.metaclass` correctly, OR
   - Ship the widget behind `factory = type(metadata_class)` so users
     can mix freely.

2. **`nchantdoffice/nchantrs/widgets/widgets.py`** — the `NchantdWidgetMixin`
   class. Could be modified to use `QObject` as its base class
   (giving it the right metaclass) without changing semantics. This is
   the most surgical fix and would unblock nchantdoffice immediately
   without waiting for an upstream release.

3. **`nchantdoffice/nchantrs/widgets/tables/tables.py`** — the call site
   itself. Could wrap the inheritance differently (e.g. use composition
   instead of inheritance, or use the real `qpandas.DataTableWidget`
   only when `pyside6pandas` is installed and use the stub everywhere
   else).

---

## Failing test / repro

To reproduce:

```bash
# In the self-contained nchantdoffice .deb (which bundles pyside6pandas):
sudo dpkg -i nchantdoffice_0.0.1.0.1.4_all.deb
nchantdoffice
```

The error fires **at module import time** before the GUI window even
appears:

```
TypeError: metaclass conflict: the metaclass of a derived class must
be a (non-strict) subclass of the metaclasses of all its bases
```

(Confirmed 2026-08-06 11:54:18 UTC on real nchantdoffice gamma build
with bundled pyside6pandas 0.4.x.)

---

## Recommended fix (option 2 above — nchantdoffice side)

File: `internal/nchantrs/widgets/widgets.py`

```diff
-class NchantdWidgetMixin(object):
+from PySide6.QtCore import QObject
+class NchantdWidgetMixin(QObject):
     """Mixin that injects app/context/config plumbing into every widget."""
```

`NchantdWidgetMixin` is purely behavioral — no Qt-specific state. Using
`QObject` as its metaclass-providing base is a **no-op for runtime
behavior** but resolves the metaclass conflict because both bases now
share the `sip.wrappertype`-derived metaclass.

This is a 1-line surgical fix that doesn't require waiting for an
upstream `pyside6pandas` release. It compiles in <1 second and doesn't
alter functionality for any existing subclass of `NchantdWidgetMixin`.

---

## Affected sites

- `internal/nchantrs/widgets/widgets.py:78` — class definition
- `internal/nchantrs/widgets/tables/tables.py:479` — failure point
  (`class NchantdDataFrameTable(NchantdWidgetMixin, qpandas.DataTableWidget)`)

Plus all other subclasses of `NchantdWidgetMixin` (which will inherit
the new base):

- `NchantdLabel`, `NchantdProgressBar`, `NchantdGroup`, `NchantdHGroupBox`,
  `NchantdTabSet`, `NchantdTree`, `NchantdWidget`

Inheriting from `QObject` instead of `object` is safe for all of these
because they all subclass a real Qt widget downstream anyway.

---

## Migration plan (Option 2, surgical)

1. **Branch:** `git checkout -b fix/pyside6pandas-metaclass gamma`
   in the **nchantdoffice** repo.
2. **Edit:** change `class NchantdWidgetMixin(object):` to
   `class NchantdWidgetMixin(QObject):` in
   `internal/nchantrs/widgets/widgets.py`.
3. **Add an import** at the top of the file (or re-use one already
   there): `from PySide6.QtCore import QObject`.
4. **Run nchantdoffice locally** to confirm the
   `metaclass conflict` is gone and NchantdDataFrameTable materializes.
5. **Add a regression test** in
   `internal/nchantrs/tests/unit/test_widget_metaclass.py` that imports
   `NchantdDataFrameTable` (from `tables.py`) and asserts no
   `TypeError: metaclass conflict`.
6. **Run the full test suite:** `pytest internal/nchantrs/tests/unit/ -q`
7. **Push:** `git add internal/nchantrs/widgets/widgets.py
   internal/nchantrs/tests/unit/test_widget_metaclass.py`
   then `git commit -m "fix(nchantrs): resolve pyside6pandas metaclass
   conflict by deriving NchantdWidgetMixin from QObject.

Inheriting NchantdWidgetMixin from QObject (instead of plain
object) gives it the same metaclass as qpandas.DataTableWidget
(sip.wrappertype-derived), so the multiple-inheritance
class NchantdDataFrameTable(NchantdWidgetMixin, qpandas.DataTableWidget)
no longer raises TypeError at import time.

Test: test_widget_metaclass.py imports NchantdDataFrameTable
and asserts the import succeeds (regression for this OOB)."`
8. **Sasquatch pulls:** I'll re-run
   `git pull origin gamma --no-rebase` in nchantdoffice, then
   `sasquatch build deb -p .` to rebuild a working `.deb`.

---

## Alternative — Option 3 (defensive composition, no upstream needed)

If the mixin change is too invasive for nchantdoffice gamma (which
already has a clean tree at `bd74099`), use composition instead of
inheritance in `tables.py`:

```python
class NchantdDataFrameTable:
    def __init__(self, parent=None, cfg=None):
        self._inner = qpandas.DataTableWidget() if qpandas_is_real else qpandas._DataTableWidget()
        # delegate all calls
        ...
```

This sidesteps the conflict entirely but requires rewriting the
existing class. Heavier refactor; only choose this if Option 2 fails.

---

## Alternative — Option 1 (upstream fix in pyside6pandas)

File upstream, ideally at https://github.com/jrlamar/pyside6pandas.

Suggested change:

```python
# pyside6pandas/views/DataTableView.py
from PySide6.QtCore import QObject  # add import

# Use QObject as metaclass-providing base so it's compatible with
# plain Python mixins:
class DataTableWidget(QObject, ...):
    ...
```

This is the cleanest fix but requires upstream acceptance + pip
release + users to upgrade. Out of scope for the immediate unblock.

---

## Priority

**Critical / P1.** Until this is fixed, the self-contained .deb is not
runnable — nchantdoffice launches its Qt event loop but the data table
view (one of the primary UI elements) crashes before being rendered.

## T-XXXX-NNN placeholder

T-NEW-CRIT-PYS6PD (next available critical-bug T-number).

## Owner / Estimate

- **Owner:** Solubrew (nchantdoffice gamma maintainer)
- **Estimate:** 5 minutes for the fix + 30 minutes for verification
  + 17 minutes for `sasquatch build deb` rebuild + 5 minutes push/pull
  = **~1 hour total wall clock** until nchantdoffice fully launches.

---

**Workaround in the meantime:** None within sasquatch. Build the app
on Ubuntu directly (without the .deb), OR pin `pyside6pandas` to a
release that ships the standalone `DataTableWidget` without the
QObject metaclass inheritance problem.
