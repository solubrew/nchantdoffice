# TODAY is 2026-08-03:
- the following issues were found to existing testing the NchantdOffice Desktop Application with all its most updated internal dependencies.

## Document Changes:
- removed Chart from initial release due to limiting matrix to .csv files due to time/complexity of debugging all the excel logic

## Issues Found:
- need to implement a file open filter on the dialog based on the active tab document type
- need to implement a file import filter on the dialog based on what file types can be imported (.ctd, .pyof, etc)
- implement autosave functionality on each action/focal-change of each document type
- import of .pyof is still broken, need to pull in the tables (doc_tree_node, doc_tab, doc_media, doc_media_content, app_media, app_media_content) grab the content data in each row and create a new row in the corresponding table of the current application database
-  
 


## Bugs: