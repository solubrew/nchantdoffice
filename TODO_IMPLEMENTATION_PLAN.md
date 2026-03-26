# NchantdOffice TODO.md Implementation Plan

## Status: IN PROGRESS

### ✅ Items 1 & 2 - Already Implemented (nchantrs base)
- [x] Default to Home node after install
- [x] Restore last selected node on relaunch

### 🔴 Item 3 - Toolbar Missing
**Problem**: Main Document Toolbar completely missing from PDF, Image, and other document types

**Root Cause**: `init_toolbar()` method not being called or toolbar widgets not being built

**Fix Plan**:
1. Check if `NchantdOfficeDocumentMixin.init_toolbar()` is being called for all document types
2. Ensure toolbar data exists in database (nchantd_menu/nchantd_menu_item tables)
3. Add toolbar to all document type classes that inherit from NchantdOfficeDocumentMixin

### 🔴 Item 4 - No Right Click Context Menu
**Problem**: No right-click functionality at all

**Root Cause**: 
- Warning: "No app model available for context menu" - widget doesn't have proper app reference
- `contextMenuEvent` not properly connected

**Fix Plan**:
1. Ensure all document widgets have proper `app` reference set
2. Fix `NchantdWidgetMixin.contextMenuEvent` to load menus from database
3. Verify `NchantdMenu` build system is working
4. Test that right-click triggers menu display

### ⚠️ Tab Duplication Issue - INVESTIGATION NEEDED
**Problem**: When creating new tabs, old views are duplicated instead of replaced

**Investigation**:
1. Check `updateTabs()` in nodes.py - verify it clears before building
2. Check `buildTabSet()` - ensure it's replacing not appending
3. Verify model/instance references are unique per tab
