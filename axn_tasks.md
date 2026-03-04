# AXN Tasks - NchantdOffice Deep Dive Review

## 📋 Executive Summary
- **Total TODOs Found**: 40+
- **Critical Issues**: 8
- **Security Issues**: 3
- **Performance Issues**: 4
- **Feature Enhancements**: 12

---

## 🚨 CRITICAL ISSUES (P0)

### P0-1: logma.off() Bug - Multiple Instances
**Files**: 
- `updates/db.py:29`
- `widgets/documents/analytics/charts.py:43`
- `widgets/documents/atnrg/browsers/browsers.py:48`
- `widgets/items/items.py:36`
- `widgets/catalogs.py:40`
- `widgets/panes/new.py:38`
- `widgets/controls/toolboxes.py:36`

**Issue**: `logma.off()` causes dialog issues (same bug fixed in nchantrs)
**Fix**: Comment out or remove all `logma.off()` calls
**Status**: TODO

### P0-2: Missing initView() Call
**File**: `nchantdoffice.py`
**Issue**: NchantdOfficeCloak.__init__ doesn't call initView() after creating view
**Status**: TODO

### P0-3: GlainMixin Not Integrated
**File**: `nchantdoffice.py`
**Issue**: Parent nchantrs has GlainMixin, but NchantdOfficeCloak doesn't integrate it
**Status**: TODO

---

## 🔒 SECURITY ISSUES

### S-1: Hardcoded API URL
**File**: `utilities/links.py:39`
```
API_URL = "https://nchantdoffice.com/api/affiliate/"
```
**Issue**: Hardcoded URL with no env-based configuration
**Status**: TODO - Make configurable

### S-2: No Authentication Implementation
**File**: `nchantdoffice.py`
**Issue**: No password dialog or auth system (matches nchantrs stub)
**Status**: TODO - Need proper implementation

### S-3: Credential Storage
**File**: `widgets/panes/sources.py:336-342`
**Issue**: Uses `secure_stored_key` - verify pycurity integration is proper
**Status**: TODO - Audit

---

## ⚡ PERFORMANCE ISSUES

### PERF-1: Virtual Table Creation Commented
**File**: `models.py:1100`
```python
# self.store.create_virtual_table() #TODO: relocat
```
**Issue**: Vector search table not being created
**Status**: TODO

### PERF-2: RSS Feed Processing
**File**: `models.py:964`
```python
# df = df[df["published_dttm"] == dt.datetime.now().date() - 3]#TODO convert to correct formats
```
**Issue**: Inefficient date filtering
**Status**: TODO

### PERF-3: Large Document Splitting
**File**: `models.py:1345`
```python
# TODO: increment version
```
**Issue**: No proper versioning for large documents
**Status**: TODO

### PERF-4: Duplicate View Creation
**File**: `models.py:1895`
```python
# TODO:  create child node and split off tabsdata
```
**Issue**: Tab overflow not handled - >31 tabs causes issues
**Status**: TODO

---

## ✅ TODOs - FEATURE ENHANCEMENTS

### FEAT-1: Import Functionality
- **File**: `models.py:1255` - Import from Notion, Evernote
- **File**: `dialogs/documents.py:241,245` - Various format integrations
- **File**: `widgets/documents/media/forms.py:141` - Excel to Google Forms

### FEAT-2: Document Features
- **File**: `widgets/documents/documents.py:125,134` - Icon flipping for pane toggles
- **File**: `widgets/documents/media/scripts.py:120` - Change plaintext to richtext
- **File**: `widgets/documents/workbooks/matricies.py:493,512,543` - Readonly/fill data, thumbnails

### FEAT-3: Widget Improvements
- **File**: `widgets/documents/atnrg/browsers/browsers.py:678-708` - Address Input widget
- **File**: `widgets/panes/new.py:198` - Widget_code override

### FEAT-4: Settings & Configuration
- **File**: `widgets/config/settings.py:270,286,288` - Default tab, toolbox dropdown, sequence control
- **File**: `widgets/config/accounts.py:121` - Connect to service

### FEAT-5: Data & Analytics
- **File**: `widgets/documents/analytics/sources.py:131` - Get table fields
- **File**: `widgets/panes/search.py:122` - Tag tracking
- **File**: `widgets/panes/documents.py:121` - Tag tracking

### FEAT-6: Application Features
- **File**: `widgets/controls/toolbars.py:152` - Switch to MultiInstance
- **File**: `widgets/controls/toolbars.py:182` - Cleanup add_tab signatures
- **File**: `widgets/controls/toolbars.py:223` - Multiple notes position increment
- **File**: `widgets/controls/toolboxes.py:177,229` - Load new NchantdOffice instance

### FEAT-7: API & Services
- **File**: `widgets/documents/atnrg/browsers/browsers.py:309` - Web scraping functions
- **File**: `widgets/documents/atnrg/prompts.py:421` - User/NchantdService configurations
- **File**: `widgets/documents/atnrg/surveys.py:159` - Form selection from various sources

### FEAT-8: Wizard & Setup
- **File**: `dialogs/documents.py:260` - Launch form builder wizard
- **File**: `dialogs/documents.py:292` - Handle .csv, .xlsx, .xls, .tab formats
- **File**: `widgets/panes/new.py:410` - Default pane handlers for root node

### FEAT-9: Database & Storage
- **File**: `models.py:1559` - Version handling for links
- **File**: `models.py:1731` - Create datasource table in document database

---

## 📝 GENERAL TODOs (No Priority)

### G-1: Version Upgrades
- **File**: `z-work_/nchantdtodo/dstruct.py:138` - Upgrade UUID to 7 or 8

### G-2: Documentation
- Multiple files need docs

---

## 🔄 Actions Needed

1. **Fix logma.off()** - Comment out in all 7 files
2. **Add initView()** - In NchantdOfficeCloak
3. **Integrate GlainMixin** - In NchantdOfficeCloak
4. **Make API URL configurable** - In utilities/links.py
5. **Audit credential storage** - In widgets/panes/sources.py

---

*Generated: 2026-03-04*
*Review Type: Systematic Code Deep Dive*
*Coverage: All modules analyzed*
