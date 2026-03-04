# CHANGES.md - NchantdOffice

All notable changes to the NchantdOffice project will be documented in this file.

---

## [Unreleased] - Post nchantrs Alignment

### Issues Found During Review (2026-03-04)

#### Critical (P0)
- **logma.off() bug**: Found `logma.off()` in models.py line 67 - this causes dialogs to not appear (same bug was fixed in nchantrs commit b5d5e92)
- **Missing authentication**: No password dialog or requires_auth implementation - nchantrs now enforces authentication
- **Missing theme system**: No `_data_/themes/` or `_data_/icons/` directories - theme system not implemented
- **P0-1.4 security**: Need to verify users.py has no insecure defaults (inherits from nchantrs User class)

#### High Priority (P1)
- **Checkable attribute bug**: P0-1.1 from nchantrs CHANGES - need to verify widgets don't have checkable issues
- **Missing initView()**: Compare with nchantrs fix (commit 62f84c4)
- **No GlainMixin**: nchantrs added GlainMixin - not integrated in NchantdOffice

### Architecture Alignment

The review compared NchantdOffice against nchantrs v0.3.0 patterns:

| Component | nchantrs | NchantdOffice | Status |
|-----------|----------|---------------|--------|
| Model classes | NchantdCloakModel | NchantdOfficeCloakModel | ✅ Aligned |
| Store | NchantdStore | NchantdOfficeStore | ✅ Aligned |
| Views | NchantdCloakView | NchantdOfficeCloakView | ✅ Aligned |
| Dialogs | NchantdCape | NchantdOfficeDocumentCape | ✅ Aligned |
| Auth | Password dialog | **Missing** | 🔴 Needs work |
| Themes | themes/, icons/ | **Missing** | 🔴 Needs work |
| GlainMixin | Implemented | **Missing** | 🟡 Needs work |

---

## [Previous Versions]

See git history for earlier changes.
