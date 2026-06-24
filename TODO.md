# nchantdoffice TODO List

## ✅ Completed Items

| ID | Description | Status | Commit |
|----|-------------|--------|--------|
| 1 | Node selection after install - default to Home node | ✅ Complete | `1d28cd8f` |
| 2 | Restore last selected node on successive runs, fallback to Home | ✅ Complete | `1d28cd8f` |
| 3 | Fix main document toolbar for all document types | ✅ Complete | `710cf01` |
| 4 | Implement context menu using NchantdMenu build system | ✅ Complete | `710cf01` |
| 5 | Add drag and drop system for tree nodes | ✅ Complete | `8f484ec` |

---

## 🔴 Critical Priority (Bugs/Issues)

| ID | Priority | Location | Description |
|----|----------|----------|-------------|
| C1 | 🔴 P1 | `nchantdoffice/widgets/trees.py:88` | TODO #2 selection issue - node selection not working correctly in certain situations |
| C2 | 🔴 P1 | `nchantdoffice/widgets/trees.py:207` | Sibling creation issue in certain situations - cannot create siblings properly |
| C3 | 🔴 P1 | `nchantdoffice/nchantdoffice.py:839` | Widget database registration refactor needed |
| C4 | 🔴 P1 | `nchantdoffice/nchantdoffice.py:973` | Tree routing issue |
| C5 | 🔴 P2 | `nchantdoffice/nchantdoffice.py:1316` | Document object not available |
| C6 | 🔴 P2 | `nchantrs/widgets/controls/nchantdprompt.py:161` | Nchantd Prompt override issue |
| C7 | 🔴 P2 | `nchantrs/nodes.py:250` | Initial loading data duplicates - data loaded multiple times |
| C8 | 🔴 P2 | `nchantrs/nodes.py:123` | Tag tracking issue across multiple nchantd*.py files |

---

## 🟠 High Priority (Core Features)

| ID | Location | Description |
|----|----------|-------------|
| H1 | `nchantdoffice/nchantdoffice.py` | Implement document creation |
| H2 | `nchantdoffice/nchantdoffice.py` | Implement document opening |
| H3 | `nchantdoffice/nchantdoffice.py` | Implement export functionality |
| H4 | `nchantdoffice/nchantdoffice.py` | Implement save functionality |
| H5 | `nchantdoffice/nchantdoffice.py` | Implement list functionality |
| H6 | `nchantdoffice/nchantdoffice.py` | Implement info display |
| H7 | `nchantdoffice/nchantdoffice.py` | Implement search functionality |
| H8 | `nchantdoffice/nchantdoffice.py` | Implement validation |
| H9 | `nchantdoffice/nchantdoffice.py` | Implement repair functionality |
| H10 | `nchantdoffice/nchantdoffice.py:1144` | Virtual table relocation |
| H11 | `nchantdoffice/nchantdoffice.py:1891` | Lazy loading - move to nchantrs base |
| H12 | `nchantrs/nodes.py:410` | Default pane handlers for root node |

---

## 🟡 Medium Priority (Enhancements)

| ID | Location | Description |
|----|----------|-------------|
| M1 | `nchantdoffice/nchantdoffice.py:245` | Google Drive integration dialog |
| M2 | `nchantdoffice/nchantdoffice.py:260` | Form builder wizard - currently commented out |
| M3 | `nchantdoffice/nchantdoffice.py:545` | App tables relocation |
| M4 | `nchantdoffice/nchantdoffice.py:606` | PID definition/argument handling |
| M5 | `nchantdoffice/nchantdoffice.py:1005` | Date format conversion |
| M6 | `nchantdoffice/nchantdoffice.py:1324` | External notifications approval |
| M7 | `nchantdoffice/nchantdoffice.py:1386` | Version increment logic |
| M8 | `nchantdoffice/nchantdoffice.py:1599` | Version handling |
| M9 | `nchantdoffice/nchantdwidget.py:77` | Widget database lookup |
| M10 | `nchantdoffice/nchantdimage.py:677,687,697,707` | Address input widget |
| M11 | `nchantdoffice/nchantdchat.py:105,217` | Automation rules |
| M12 | `nchantdoffice/widgets/trees.py` | Tab duplication issue in nodes.py |

---

## 🟢 Low Priority (Nice to Have)

| ID | Location | Description |
|----|----------|-------------|
| L1 | `nchantdoffice/nchantdoffice.py:292` | CSV/XLSX/TAB file handling |
| L2 | `nchantdoffice/nchantdoffice.py` | Additional file format support |
| L3 | | Performance optimization opportunities |
| L4 | | UI/UX polish and improvements |

---

## 📊 Summary by Category

| Category | Count |
|----------|-------|
| ✅ Completed | 5 |
| 🔴 Critical Bugs | 8 |
| 🟠 High Priority Features | 12 |
| 🟡 Medium Priority | 12 |
| 🟢 Low Priority | 4 |
| **Total** | **41** |

---

## 🎯 Recommended Next Actions

1. **Immediate:** Fix C1 (TODO #2 selection issue in trees.py:88)
2. **Immediate:** Fix C2 (Sibling creation issue in trees.py:207)
3. **Soon:** Implement H1-H9 (Core document operations)
4. **Later:** Address M1-M12 (Enhancements)

---

*Last Updated: 2026-06-24*
