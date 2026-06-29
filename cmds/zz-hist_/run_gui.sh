#!/bin/bash
# Launch NchantdOffice GUI
# Sets up paths and launches the GUI

export PYTHONPATH="/home/solubrew/EDN/AGTs/gwenbot/workspace/projects/ogma:/home/solubrew/EDN/AGTs/gwenbot/workspace/projects/nchantrs:/home/solubrew/.orin/workspace/nchantdoffice:$PYTHONPATH"

cd /home/solubrew/.orin/workspace/nchantdoffice
python3 -m nchantdoffice.gui "$@"
