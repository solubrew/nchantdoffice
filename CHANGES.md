# CHANGES.md - NchantdOffice

All notable changes to the NchantdOffice project will be documented in this file.

---

## [Unreleased] - Post nchantrs Alignment

### Fixed (2026-03-04)

#### Critical (P0)
- ✅ **logma.off() bug**: Fixed in models.py line 48 - commented out to prevent dialog issues

### Issues Found During Review (2026-03-04)

#### Critical (P0)
- ~~**logma.off() bug**: Found `logma.off()` in models.py line 67 - this causes dialogs to not appear~~ ✅ FIXED
- **Missing authentication**: No password dialog or requires_auth implementation - nchantrs auth is a stub (not implemented)
- **Missing theme system**: No `_data_/themes/` or `_data_/icons/` directories - not present in nchantrs either
- **P0-1.4 security**: Verified users.py has no insecure defaults ✅

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
