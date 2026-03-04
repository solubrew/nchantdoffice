# STATE.md - NchantdOffice

## Current State: Needs Alignment with nchantrs v0.3.0

### Project
| Attribute | Value |
|-----------|-------|
| **Name** | NchantdOffice |
| **Type** | PyQt5/PySide6 GUI Application |
| **Branch** | gamma (pulled from GitVein) |
| **Location** | `/home/solubrew/.orin/workspace/projects/nchantdoffice` |
| **Repository** | `file:///mnt/overse/SBST01/vein/GitVein/nchantdoffice.git` |
| **Last Updated** | 2026-03-04 |

### Purpose
NchantdOffice is a document-based productivity application (reference implementation of nchantrs) with tabs for various document types (TODOs, Notes, Calendar, Concerns, etc.).

---

## Critical Issues Found

### 🔴 P0 - CRITICAL

| Issue | Status | Description | File |
|-------|--------|-------------|------|
| **logma.off() causing dialog issues** | 🔴 OPEN | `logma.off()` is called in models.py line 67 - this causes dialogs to not appear (same bug fixed in nchantrs commit b5d5e92) | `nchantdoffice/models.py:67` |
| **Missing password dialog/auth** | 🔴 OPEN | No authentication dialog in NchantdOfficeCloak - nchantrs now requires auth via NchantdCape password dialog | `nchantdoffice/nchantdoffice.py` |
| **Missing theme directories** | 🔴 OPEN | No `_data_/themes/` or `_data_/icons/` directories - theme system not implemented | `nchantdoffice/_data_/` |
| **P0-1.4 Auth bypass vulnerability** | ⚠️ CHECK | users.py inherits from nchantrs User - may need to verify no insecure defaults | `nchantdoffice/utilities/users.py` |

### 🟡 P1 - HIGH

| Issue | Status | Description | File |
|-------|--------|-------------|------|
| **Checkable attribute bug** | ⚠️ CHECK | P0-1.1 in CHANGES.md - need to verify widgets don't have checkable issues | `widgets/` |
| **Missing initView() in NchantdOfficeCloak** | 🟡 TODO | Compare with nchantrs fix (commit 62f84c4) | `nchantdoffice/nchantdoffice.py` |
| **No GlainMixin integration** | 🟡 TODO | nchantrs added GlainMixin - not implemented here | models.py |

### 🟢 WORKING

| Component | Status | Notes |
|-----------|--------|-------|
| NchantdCloak inheritance | ✅ | Properly extends NchantdCloak |
| Model classes | ✅ | Uses NchantdCloakModel, NchantdTabSetModel |
| NchantdStore | ✅ | Extends NchantdStore correctly |
| Views | ✅ | Extends NchantdCloakView |
| Dialogs | ✅ | Uses NchantdCape, NchantdSigil |
| Widget imports | ✅ | Imports from nchantrs.widgets |

---

## Architecture Comparison

### nchantrs Pattern (Reference)
```
nchantrs/
├── models/           # NchantdStore, CloakModel, CapeModel
├── views/            # NchantdCloakView
├── dialogs/          # NchantdCape, NchantdSigil
├── widgets/          # NchantdWidget base
├── _data_/
│   ├── themes/      # QSS files
│   ├── themes.yaml   # Theme config
│   └── icons/        # Icon assets
└── utilities/        # users.py, policies.py
```

### NchantdOffice Current
```
nchantdoffice/
├── models.py         # NchantdOfficeCloakModel, Store
├── views.py          # NchantdOfficeCloakView  
├── dialogs/          # NchantdOfficeDocumentCape
├── widgets/          # Custom widgets using nchantrs
├── utilities/        # users.py, policies.py
└── _data_/
    ├── models.yaml   ✅
    └── nchantdoffice.yaml
    ❌ themes/
    ❌ icons/
```

---

## Alignment Status

### Implemented (Aligned with nchantrs)
- [x] Model layer using nchantrs base classes
- [x] View layer extending nchantrs views
- [x] Dialog classes extending NchantdCape/NchantdSigil
- [x] Widget imports from nchantrs.widgets
- [x] YAML configuration

### Not Implemented (Needs Work)
- [ ] **Authentication** - No password dialog, no requires_auth
- [ ] **Theme system** - Missing themes/, icons/, themes.yaml
- [ ] **GlainMixin** - Not integrated
- [ ] **logma.off() bug** - Must be removed (causes dialog issues)

---

## Required Actions

### Immediate (P0)
1. **Remove `logma.off()`** from `nchantdoffice/models.py:67`
2. **Add authentication** - Implement password dialog like nchantrs
3. **Add theme directories** - Create _data_/themes/, _data_/icons/
4. **Verify auth security** - Check for P0-1.4 vulnerabilities

### Short-term (P1)
5. Add initView() call in NchantdOfficeCloak.__init__
6. Integrate GlainMixin for agent memory
7. Verify checkable attribute handling in widgets

---

## Dependencies

| Package | Status |
|---------|--------|
| nchantrs | ✅ Required (imported) |
| condor | ✅ |
| ogma | ✅ (but logma.off() is the problem) |
| pyffice | ✅ |
| pycurity | ✅ |
| subtrix | ✅ |

---

## Testing

| Category | Status |
|----------|--------|
| Core tests | ⏳ Pending |
| Widget tests | ⏳ Pending |
| Integration tests | ⏳ Pending |
| Auth flow tests | ⏳ Pending |

---

## Files Analyzed

| File | Issues Found |
|------|--------------|
| `nchantdoffice/models.py` | 🔴 logma.off(), missing GlainMixin |
| `nchantdoffice/nchantdoffice.py` | 🔴 No auth, missing initView() |
| `nchantdoffice/views.py` | ✅ OK |
| `nchantdoffice/utilities/users.py` | ⚠️ Need security check |
| `nchantdoffice/utilities/policies.py` | ✅ OK |
| `nchantdoffice/dialogs/dialogs.py` | ✅ OK |
| `nchantdoffice/_data_/` | 🔴 Missing themes/, icons/ |

---

*Last updated: 2026-03-04*
*Review conducted using nchantrs STATE.md/CHANGES.md as reference*
