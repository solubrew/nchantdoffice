# T-NEW-CRIT: pyside6pandas (qpandas) Metaclass Conflict

**Status:** Blocking — self-contained .deb launch fails
**Affects:** pyside6pandas library, nchantdoffice gamma build
**Discovered:** 2026-08-06 during self-contained .deb install + run test
**Severity:** Critical — nchantdoffice launches through full Qt WebEngine
graphics initialization but crashes when instantiating
`NchantdDataFrameTable`. No workaround within sasquatch; fix must land
in nchantdoffice gamma.

---

## ⚠️ Update (2026-08-06): the QObject fix **causes a segfault**

I initially recommended `class NchantdWidgetMixin(QObject):` as a
1-line surgical fix. **Don't apply that change.** Per user testing
(Solubrew, 2026-08-06): applying the QObject change causes a
**segmentation fault at runtime**.

### Why it segfaults

Inheriting from `QObject` forces the MRO to call `QObject.__init__`
**exactly once** with a `(parent)` argument. The nchantrs widget
pattern uses old PyQt5-style cooperative `super().__init__()` calls
that don't pass a parent:

```python
class NchantdWidgetMixin(object):
    pass  # never calls super().__init__, no parent state

class NchantdDataFrameTable(NchantdWidgetMixin, qpandas.DataTableWidget):
    def __init__(self, parent=None, cfg=None):
        super().__init__()  # ⚠ passes NO parent — breaks QObject's C++ tracking
```

When NchantdWidgetMixin becomes `QObject`-derived, this `super().__init__()`
walks the MRO and calls `QObject.__init__` without a parent argument.
PySide6's `sip.wrappertype` then gets confused about Qt's C++ ownership
tracking → SIGSEGV.

**The fix must be at the call site, not in the mixin.**

---

## Failing trace

```
File "/usr/lib/nchantdoffice/internal/nchantrs/widgets/tables/tables.py",
line 479, in <module>
    class NchantdDataFrameTable(NchantdWidgetMixin, qpandas.DataTableWidget):
TypeError: metaclass conflict: the metaclass of a derived class must
be a (non-strict) subclass of the metaclasses of all its bases
```

### Two bases

| Class | Source | Metaclass |
|---|---|---|
| `NchantdWidgetMixin` | `internal/nchantrs/widgets/widgets.py:78` | `type` (plain Python) |
| `qpandas.DataTableWidget` | `internal/nchantrs/libraries/qpandas.py:86` | `sip.wrappertype` (PySide6's Qt metaclass) when `pyside6pandas` is bundled |

When `pyside6pandas` is bundled (always in the self-contained `.deb`
because it's a transitive wheel dep), `qpandas.DataTableWidget`
resolves to the real Qt-based class. Python's MRO rule rejects
multiple-inheritance when metaclasses aren't compatible.

### Why `QObject` fix doesn't work

`QObject.__init__` requires a parent. The nchantrs widgets use
`super().__init__()` (no args) — Qt's C++ ownership tracker sees no
parent and segfaults on first method call.

---

## Recommended fix — composition in `tables.py` (Option 3)

**Sidesteps the conflict entirely without touching the mixin used by
8+ other widgets (`NchantdLabel`, `NchantdProgressBar`,
`NchantdGroup`, etc.).** A real `qpandas.DataTableWidget` subclass
holds a small helper instance that IS a `NchantdWidgetMixin`;
`__getattr__` delegation exposes the mixin's API.

File: `internal/nchantrs/widgets/tables/tables.py`

```diff
-class NchantdDataFrameTable(NchantdWidgetMixin, qpandas.DataTableWidget):
-    """A pandas-backed table widget."""
-
-    def __init__(self, parent=None, cfg=None) -> None:
-        super().__init__()
-        self.parent = parent
-        self.config = kahndor.Instruct(pxcfg).select('NchantdDataFrameTable').override(parent.config).override(cfg)
-        self.model = qpandas.DataFrameModel()
-        logma.info(f'NchantdDataFrameTable initialized')
-
-    def initModel(self, df=None) -> Any:
-        super().initModel()
-        if df is None:
-            df = DataFrame()
-        self.model.setDataFrame(df)
-        return self
+class NchantdDataFrameTable(qpandas.DataTableWidget):
+    """A pandas-backed table widget with NchantdWidgetMixin
+    behavior composed via a helper instance (sidesteps
+    pyside6pandas metaclass conflict)."""
+
+    def __init__(self, parent=None, cfg=None) -> None:
+        super().__init__(parent)  # qpandas MRO must get parent
+        self._nchantd = _NchantdWidgetHelper(self, parent=parent, cfg=cfg)
+        logma.info(f'NchantdDataFrameTable initialized')
+
+    def __getattr__(self, name):
+        # Delegate NchantdWidgetMixin behavior via the helper.
+        if name.startswith('_') or name in type(self).__dict__:
+            raise AttributeError(name)
+        helper = self.__dict__.get('_nchantd')
+        if helper is not None and hasattr(helper, name):
+            return getattr(helper, name)
+        raise AttributeError(name)
+
+    def initModel(self, df=None) -> Any:
+        super().initModel()
+        if df is None:
+            df = DataFrame()
+        self.model.setDataFrame(df)
+        return self
+
+class _NchantdWidgetHelper(NchantdWidgetMixin):
+    """Carries NchantdWidgetMixin's behavior as a non-Qt delegate.
+    Instantiated once per NchantdDataFrameTable to expose the
+    mixin's API without forcing Qt metaclass constraints on it."""
+    def __init__(self, owner_widget, parent=None, cfg=None):
+        self.widget = owner_widget  # back-ref for any callsites
+        super().__init__(parent=parent, cfg=cfg)
+
+    def app(self):
+        p = self.parent
+        return p.app if p else None
+    # ... implement only the methods NchantdDataFrameTable actually USES.
+    # The full NchantdWidgetMixin surface is ~15 methods — qpandas already
+    # provides many of them. Audit with grep first.
```

### Why this works

- **`NchantdWidgetMixin` is untouched** — no segfault for the 8 other
  widgets that mix it with real Qt widgets
- **`NchantdDataFrameTable` only inherits from `qpandas.DataTableWidget`**
  (not `NchantdWidgetMixin`), so no metaclass conflict
- **`_NchantdWidgetHelper` is `NchantdWidgetMixin(object)`** — plain
  Python class, no Qt constraints
- **Method delegation via `__getattr__`** preserves the existing API;
  call sites don't need updates

---

## Migration plan

1. **Branch:** in the nchantdoffice repo,
   `git checkout -b fix/pyside6pandas-metaclass-composition gamma`
2. **Audit** which `NchantdWidgetMixin` methods are called on
   `NchantdDataFrameTable` instances elsewhere in nchantdoffice:
   ```bash
   cd /home/solubrew/.hermes/projects/nchantdoffice
   grep -rn "NchantdDataFrameTable\." --include="*.py" | \
       grep -E "\.(app|context_menu|action|init_variables|initModel|initView|initWidget|handler|max_width|min_width|name|widget_initialized)\b"
   ```
3. **Edit** `internal/nchantrs/widgets/tables/tables.py` per the diff above
4. **Implement** the methods on `_NchantdWidgetHelper` that audit
   revealed are called — only those, nothing more
5. **Run nchantdoffice locally**:
   ```bash
   PYTHONPATH=./nchantdoffice:./internal/nchantrs python -m nchantdoffice.__main__
   ```
   (or `sasquatch run`) — should launch without segfault
6. **Add regression test** in
   `internal/nchantrs/tests/unit/test_tables_composition.py`:
   - Imports `tables.py` (the failure point)
   - Instantiates `NchantdDataFrameTable()` headlessly
   - Asserts `app()` and delegated methods return non-None
7. **Push & merge:**
   ```bash
   git add internal/nchantrs/widgets/tables/tables.py \
           internal/nchantrs/tests/unit/test_tables_composition.py
   git commit -m "fix(nchantrs): resolve pyside6pandas metaclass conflict
   via composition"
   ```
8. **Sasquatch rebuild** (in this workspace):
   ```bash
   cd /home/solubrew/.hermes/projects/nchantdoffice
   git pull origin gamma --no-rebase
   cd /home/solubrew/.hermes/projects/sasquatch
   /home/solubrew/ENVs/sasquatch/bin/sasquatch build deb \
       -p /home/solubrew/.hermes/projects/nchantdoffice
   ```
9. **Smoke-test the new .deb** before declaring victory

---

## Alternative fixes (not recommended for immediate unblock)

### Option 1 — upstream fix in pyside6pandas

File at https://github.com/jrlamar/pyside6pandas. Changes needed:

```python
# pyside6pandas/views/DataTableView.py
class DataTableWidget(QObject, ...):
    """Add QObject to bases so plain-python mixins can compose."""
```

Realistically — this needs upstream maintainer cooperation and
depends on shiboken internals. Not viable as an immediate unblock.

### Option 3B — pin pyside6pandas to a pre-metaclass version

Inspect old pyside6pandas releases for one whose `DataTableWidget`
doesn't inherit Qt (was added in some later version). Pin to that
in nchantdoffice's `[project.dependencies]`. Last resort — may break
other features that depend on modern pyside6pandas.

### Option 4 — different table library

Replace `qpandas` with a different pandas DataFrame widget
(e.g. `pandas-qt`, `QtPandas` from `qtcharts`, hand-rolled). Major
refactor — out of scope.

---

## Priority

**Critical / P1.** Until this is fixed, the self-contained .deb is
not runnable — nchantdoffice launches its Qt event loop but the
data-table view (one of the primary UI elements) crashes before
being rendered.

## T-XXXX-NNN placeholder

T-NEW-CRIT-PYS6PD-COMP (next available critical-bug T-number;
append `-COMP` for the composition variant).

## Owner / Estimate

- **Owner:** Solubrew (nchantdoffice gamma maintainer)
- **Estimate:** 30 min for the composition refactor + 1 hour for
  verification + 17 min for `sasquatch build deb` rebuild +
  push/pull = **~3 hours total wall clock**.

---

## What sasquatch did this session to get us here

Each fix below is in sasquatch gamma as of `29e349f`:

1. `self_contained` is the default for deb, rpm, appimage (no `--source-only` CLI flag yet — TODO)
2. `ensure_ref_checked_out()` honors `@gamma` in pyproject's file:// URLs — fixes imports of `thingery`, `kahndor`, `pyurity`, etc.
3. PEP 420 namespace package detection — `pyurity/pytime.py` now bundled (no `__init__.py` required)
4. `[tool.setuptools.dynamic.dependencies]` parsing — `uuid7` now bundled via requirements.txt → uuid_extensions shim
5. `internal/` added to PYTHONPATH so SB companion imports resolve
6. Pre-flight checks + `SASQUATCH_WRAPPER_DEBUG=1` for clean error messages

What's **NOT** a sasquatch issue: the metaclass conflict is in
**nchantrs gamma** code (`internal/nchantrs/widgets/tables/tables.py`).

---

**Workaround in the meantime:** None within sasquatch. Build the app
on Ubuntu directly (without the `.deb`), OR use a UI tool that
doesn't trigger `NchantdDataFrameTable` instantiation.
