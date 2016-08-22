# label-cmd
Dynamically control torrent downloads with labels

**Features**

* Dynamically execute binaries based on label.
* Argument support.
* Create/translate in text variables.

**Installation**

1. pip install deluge-client
2. git clone https://github.com/Vauxite/label-cmd.git /opt/label-cmd
3. Deluge/Preferences/Execute
4. Event: Torrent Complete.
5. Command: /opt/label-cmd/label_cmd.py
