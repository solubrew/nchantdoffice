# TODAY is 2026-08-03:
- the following issues were found to existing testing the NchantdOffice Desktop Application with all its most updated internal dependencies.

## Document Changes:
- 


## Issues Found:
- Block from creating new Nodes at the top level 
- block from creating any nodes in the Settings and Journal trees
- block from creating/deleting tabs in Settings node tree
- node sort buttons in not actuallying sorting the subtree of selected node
- change color of get pro button to a green button
- total node limit of 100 for non-pro users needs to launch a popup warning with a Get Pro button when the user hits it not just silently deny
  8922              3767  0688d6e9-edd9-7af6-8000-9cae9e60d978           Wireless Internet     usernode  ...  2026-08-15T15:32:10.266384           0           0          1           doc
  8923                 2  067ce332-8864-7d0b-8000-bfd314a580cc                     Journal  displaynode  ...              20260814091023           0           0          1           app
  8924                 3  066a7cf6-5aca-79a2-8000-f4b5405a0427                    Settings  displaynode  ...              20260814091023           0           0          1           app

  [8925 rows x 26 columns]
  2026-08-15 18:16:14,014 - nchantdoffice.models                      257: WARNING  - [models] add_node rejected: max_nodes_per_user limit reached for user (ntype='usernode', name='1808e')
  2026-08-15 18:16:24,994 - nchantrs.widgets.widgets                  499: INFO     - Focus Out

- app_instance entry is not being made on new install/creation of initial instance
- new_child_node button on NewDocument toolbar was broken between b8798a38 solubrew <solubrew@solutionsbrewer.com> on 8/15/26 at 12:51 PM and the current HEAD
- 


## Bugs:
- 