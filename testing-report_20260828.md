# TODAY is 2026-08-28:
- the following issues were found to existing testing the NchantdOffice Desktop Application with all its most updated internal dependencies.


## Issues Found:
- on delete of node the interface should fall back to the previously selected node if it doesn't have one set it should fall back to the parent of the deleted node
- need to set a maximum width of NchantdImage to be the standard center space of the 3 pane layout
- if the left side and/or right side panels are hidden the image can expand into those areas but must respect the reclaim if they are shown and add resize the width and maintain ratio

## Bugs: