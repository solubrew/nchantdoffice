# TODAY is 2026-08-03:
- the following issues were found to existing testing the NchantdOffice Desktop Application with all its most updated internal dependencies.

## Document Changes:
- fix(models): seed app_user row on initial install (T-NEW-129) -- bootstrap_app_user + store_app_user + get_app_user wired from run_on_launch (7da0d1e)
- feat(toolbars): top-level new-node toolbar lands at pid=0 (T-NEW-130) -- NchantdNewDocumentSigil.top_level flag + launch_new_document_sigil signals the rootnode dispatch (ac448ad)
- feat(models): deny child-node creates under Home/Journal/Settings (T-NEW-131) -- is_locked_pid + is_locked_parent helpers, add_node/add_node_app refuse children of locked trees for all users (fc61c4e)
- feat(models): deny tab create/delete in Settings tree (T-NEW-132) -- is_locked_tab_parent helper, add_tab/delete_tab refuse Settings-tree tab ops for all users (87ace4d)
- feat(panes): sort buttons now sort the entire subtree (T-NEW-133) -- cmd_sort_children + _resolve_sort_direction + _sort_subtree helper, every descendant depth is reordered (asc/desc) and persisted (8857081)
- feat(toolbars): Get Pro button visibly green (T-NEW-134) -- _apply_bg_color helper on NchantdOfficeDocumentMixin sets background-color via setStyleSheet, paired with white text for contrast (558a4f3)
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
- 