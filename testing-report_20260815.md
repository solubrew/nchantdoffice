# TODAY is 2026-08-15:
- the following issues were found to existing testing the NchantdOffice Desktop Application with all its most updated internal dependencies.

## Document Changes:
- fix(models): seed app_user row on initial install (T-NEW-129) -- bootstrap_app_user + store_app_user + get_app_user wired from run_on_launch (7da0d1e)
- feat(toolbars): top-level new-node toolbar lands at pid=0 (T-NEW-130) -- NchantdNewDocumentSigil.top_level flag + launch_new_document_sigil signals the rootnode dispatch (ac448ad)
- feat(models): deny child-node creates under Home/Journal/Settings (T-NEW-131) -- is_locked_pid + is_locked_parent helpers, add_node/add_node_app refuse children of locked trees for all users (fc61c4e)
- feat(models): deny tab create/delete in Settings tree (T-NEW-132) -- is_locked_tab_parent helper, add_tab/delete_tab refuse Settings-tree tab ops for all users (87ace4d)
- feat(panes): sort buttons now sort the entire subtree (T-NEW-133) -- cmd_sort_children + _resolve_sort_direction + _sort_subtree helper, every descendant depth is reordered (asc/desc) and persisted (8857081)
- feat(toolbars): Get Pro button visibly green (T-NEW-134) -- _apply_bg_color helper on NchantdOfficeDocumentMixin sets background-color via setStyleSheet, paired with white text for contrast (558a4f3)
- feat(models): 100-node cap redirects to Nchantd Account with reason param (T-NEW-135) -- fixed dead-code bug in _check_max_nodes_for_user, redirect_to_get_pro accepts reason, NchantdAccountSettings appends ?reason= to compare URL (5bf6f3d)
-

## Issues Found:
- total node limit of 100 for non-pro users needs to launch a popup warning with a Get Pro button when the user hits it not just silently deny
  8922              3767  0688d6e9-edd9-7af6-8000-9cae9e60d978           Wireless Internet     usernode  ...  2026-08-15T15:32:10.266384           0           0          1           doc
  8923                 2  067ce332-8864-7d0b-8000-bfd314a580cc                     Journal  displaynode  ...              20260814091023           0           0          1           app
  8924                 3  066a7cf6-5aca-79a2-8000-f4b5405a0427                    Settings  displaynode  ...              20260814091023           0           0          1           app

  [8925 rows x 26 columns]
  2026-08-15 18:16:14,014 - nchantdoffice.models                      257: WARNING  - [models] add_node rejected: max_nodes_per_user limit reached for user (ntype='usernode', name='1808e')
  2026-08-15 18:16:24,994 - nchantrs.widgets.widgets                  499: INFO     - Focus Out

- new_child_node button on NewDocument toolbar was broken between b8798a38 solubrew <solubrew@solutionsbrewer.com> on 8/15/26 at 12:51 PM and the current HEAD -- was the Pro lock, not a regression (T-NEW-056 deny path)
-

- Tab Delete button not working from document toolbar or from NchantdTabPane in the toolbox
- Ensure that .pyof import doesn't pull in DELETE_BIT=1 nodes or tabs
- need to redirect file_details in toolbox to internal data when the tab is an internal document
- need to work on saving the external file externally when it is an external location file so that it is not just a viewer but an editor
- connect ctrl+s to save button logic
- 

## Bugs:
- 2026-08-15 22:19:02,101 - squirl.orgnql.sonql                       257: WARNING  - Table app_tab
2026-08-15 22:19:02,101 - squirl.orgnql.sonql                       257: WARNING  - Data [['Journal', 'nchantrs.widgets.calendars.days.NchantdDayJournal', '{}', '06a811e1-60bb-79b0-8000-793884599fdd', '06a811e1-6152-7159-8000-e208190c8b5b', 1, 'day', 'center', 0, 1, 1, 1, '06a811e1-619a-7b18-8000-8f7f4aca49dd', 0, '20260815221902', 0, '20260815221902', 0, 0, 1]]
2026-08-15 22:19:02,109 - nchantdoffice.models                      257: WARNING  - [models] get_app_user failed: 'NchantdOfficeCloakModel' object has no attribute 'get_table'
2026-08-15 22:19:02,109 - nchantdoffice.models                      257: WARNING  - [models] bootstrap_app_user failed: cannot pickle 'generator' object
Traceback (most recent call last):
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/models.py", line 2127, in bootstrap_app_user
    self.store_app_user(user, db="db")
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/models.py", line 3507, in store_app_user
    store.store_app_user(payload, db=db)
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/models.py", line 4220, in store_app_user
    self._store("app_user", [payload], db)
  File "/mnt/iverse/SB/3_Functions/Projects/MicroMole/3_Work/1_DELTA/micromole/micromole/storage.py", line 930, in _store
    return self._store_impl(table, payload, db, columns)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Projects/MicroMole/3_Work/1_DELTA/micromole/micromole/storage.py", line 947, in _store_impl
    return self.docs[db].write(cfg)
           ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskSQuiRL/1_DELTA/squirl/squirl/orgnql/sonql.py", line 1018, in write
    self.dikt = sanitizeRecords(self._configure_data(data))
                                ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskSQuiRL/1_DELTA/squirl/squirl/orgnql/sonql.py", line 1377, in _configure_data
    return deepcopy(transform_data)
           ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/copy.py", line 136, in deepcopy
    y = copier(x, memo)
        ^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/copy.py", line 221, in _deepcopy_dict
    y[deepcopy(key, memo)] = deepcopy(value, memo)
                             ^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/copy.py", line 136, in deepcopy
    y = copier(x, memo)
        ^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/copy.py", line 221, in _deepcopy_dict
    y[deepcopy(key, memo)] = deepcopy(value, memo)
                             ^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/copy.py", line 136, in deepcopy
    y = copier(x, memo)
        ^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/copy.py", line 196, in _deepcopy_list
    append(deepcopy(a, memo))
           ^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/copy.py", line 136, in deepcopy
    y = copier(x, memo)
        ^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/copy.py", line 221, in _deepcopy_dict
    y[deepcopy(key, memo)] = deepcopy(value, memo)
                             ^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/copy.py", line 151, in deepcopy
    rv = reductor(4)
         ^^^^^^^^^^^
TypeError: cannot pickle 'generator' object
2026-08-15 22:19:02,110 - nchantdoffice.updates.db                   79: INFO     - Updating pyffice document
- 2026-08-15 22:19:07,129 - nchantdoffice.updates.checker             257: WARNING  - [update_checker] GET api/check-update failed: HTTPSConnectionPool(host='nchantdoffice.com', port=443): Max retries exceeded with url: /api/check-update?current_version=0.0.1&os=qt6-linux (Caused by ConnectTimeoutError(<HTTPSConnection(host='nchantdoffice.com', por
- 2026-08-15 22:19:07,143 - nchantdoffice.updates.checker             257: WARNING  - [update_checker] check-update timed out (expected on a dev/offline box); falling back to local-only mode.

## Filed from this report (2026-08-16 sweep)

The "Issues Found" section above maps to the following T-NEW
cards in `TODOs.md` (filed 2026-08-16, gamma `5b6397e`):

| Issue | T-NEW card | Status |
|-------|-----------|--------|
| 1. 100-node cap popup | (none — popup superseded by T-NEW-135 redirect per user direction 2026-08-16) | closed |
| 2. Tab Delete broken from document toolbar + NchantdTabPane | **T-NEW-142** | open |
| 3. .pyof import pulls DELETE_BIT=1 nodes | **T-NEW-143** | open |
| 4. file_details toolbox should redirect to internal data for internal docs | **T-NEW-144a** | open |
| 5. External file should be editor, not viewer | **T-NEW-144b** | open |
| 6. ctrl+s should call save button | **T-NEW-145** | open |

The traceback block above (timestamps 22:19:02.10 → 22:19:07.12)
also surfaced two regressions in the **T-NEW-129** wiring
(`bootstrap_app_user` / `get_app_user`):

| Traceback | T-NEW card | Status |
|-----------|-----------|--------|
| `get_app_user failed: 'NchantdOfficeCloakModel' object has no attribute 'get_table'` | **T-NEW-147** | open |
| `bootstrap_app_user failed: cannot pickle 'generator' object` | **T-NEW-146** | open |

Both regressions should be considered **lead candidates** for
the next sprint — they break first-boot behaviour for every
new install (T-NEW-129 was supposed to fix first-boot, not
break it).