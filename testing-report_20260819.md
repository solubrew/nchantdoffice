# TODAY is 2026-08-19:
- the following issues were found to existing testing the NchantdOffice Desktop Application with all its most updated internal dependencies.


## Issues Found:
- all tabs are being rendered on node selection we need to have fully lazy with the ability to be moved to a background process to load the non-focus tabs of the node
- matrix document tabs are slow in loading each cell....we need to lazy/background load the cells that are outside the viewport upon scroll/calculate
- on document open the toolbar save button needs to flip it already flips on tab reload but we need to flip it on file open
- 


## Bugs: