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

## [Unreleased] - UI Feature Implementation (2026-03-04)

### Implemented Features

#### Tab Drag-and-Drop
| Feature | Implementation | Status |
|---------|---------------|--------|
| Center app tab dragging | nchantrs `NchantdTabSet.start_drag()` | ✅ EXISTS |
| Tab reordering within tabset | `move_tab()` method | ✅ EXISTS |
| Tab dragging between panes | MIME data with source_widget | ✅ EXISTS |
| Drag visual feedback | `create_drag_pixmap()` | ✅ EXISTS |

#### Tree Drag-and-Drop
| Feature | Implementation | Status |
|---------|---------------|--------|
| Tree node drag-and-drop | QAbstractItemView.DragDrop mode | ✅ EXISTS |
| Tab-to-tree drag handler | `NchantdOfficeApplicationTree._handle_tab_drop()` | ✅ EXISTS |
| Node creation from dropped tab | `_create_node_from_tab()` | ✅ EXISTS |

#### Right Pane / Toolbox
| Feature | Implementation | Status |
|---------|---------------|--------|
| Right pane tabset | `panes["right"]` | ✅ EXISTS |
| Toolbox loading | `load_toolbox()` in tabset | ✅ EXISTS |
| Tab-specific toolbox | Per-tab `toolbox_config` | ✅ EXISTS |
| Search in documents | Document search widgets | ✅ EXISTS |

### Known Gaps Still Needing Implementation

| Priority | Feature | Status | Notes |
|----------|---------|--------|-------|
| P0 | Center app tab dragging | ✅ DONE | Already in nchantrs |
| P0 | Tree node drag-and-drop | ✅ DONE | Already in nchantrs |
| P0 | Cross-pane tab dragging | ✅ DONE | Already in nchantrs |
| P0 | Tab-to-tree drag-drop | ✅ DONE | Already in nchantdoffice |
| P1 | Right toolbox: Search implementation | 🟡 PARTIAL | Per-doc search exists |
| P1 | Right toolbox: Additional items | 🟡 PARTIAL | Calendar/Charts have drawers |
| P2 | Right-click context menus | 🔴 NOT DONE | Needs implementation |

### Action Items

- [ ] Implement right-click context menus throughout application
- [ ] Enhance right toolbox search functionality
- [ ] Add more toolbox drawer items

---

## [Previous Versions]

See git history for earlier changes.
