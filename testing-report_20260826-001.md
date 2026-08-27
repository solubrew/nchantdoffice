










Add a terminal as a Document type

Also add a terminal as toolbox drawer for the script document

terminal only avialble to pro users

There are several ways to embed a terminal in a PySide6 application, ranging from a simple command runner to a full VT100-compatible emulator.

1. Simple Interactive Terminal (QProcess + QPlainTextEdit)
This is the easiest cross-platform approach. It runs a shell (bash/cmd/powershell) and handles basic input/output. It works well for simple commands but has limited support for full-screen apps (vim, htop, etc.) or complex escape sequences.

import sys
import platform
from PySide6.QtCore import QProcess, Qt
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPlainTextEdit, QVBoxLayout, QWidget
)

class TerminalWidget(QPlainTextEdit):
    def init(self, parent=None):
        super().init(parent)
        self.setFont(QFont("Consolas" if platform.system() == "Windows" else "Monospace", 11))
        self.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4;")
        self.setReadOnly(False)

        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.handle_output)
        self.process.finished.connect(self.handle_finished)

Start the shell
        if platform.system() == "Windows":
            self.process.start("cmd.exe")
        else:
            self.process.start("/bin/bash", ["-i"])  # interactive bash

        self.appendPlainText("Terminal started...\n")

    def handle_output(self):
        data = self.process.readAllStandardOutput()
        text = bytes(data).decode("utf-8", errors="replace")
        self.moveCursor(QTextCursor.MoveOperation.End)
        self.insertPlainText(text)
        self.moveCursor(QTextCursor.MoveOperation.End)

    def handle_finished(self):
        self.appendPlainText("\n[Process finished]\n")

    def keyPressEvent(self, event):
Send key presses to the process
        if self.process.state() == QProcess.ProcessState.Running:
            key = event.text()
            if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
                self.process.write(b"\n")
            elif event.key() == Qt.Key.Key_Backspace:
                self.process.write(b"\x08")  # or \b
            elif key:
                self.process.write(key.encode())
            else:
                super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)

class MainWindow(QMainWindow):
    def init(self):
        super().init()
        self.setWindowTitle("PySide6 Terminal")
        self.resize(800, 500)

        central = QWidget()
        layout = QVBoxLayout(central)
        self.terminal = TerminalWidget()
        layout.addWidget(self.terminal)
        self.setCentralWidget(central)

if name == "main":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

Notes:
This is a basic implementation. Real terminals need better handling of cursor movement, history, colors, and special keys.
On Windows you may prefer powershell.exe.

2. Better Options – Dedicated Terminal Libraries

| Library                  | Pros                                      | Cons                          | Install                                      |
|--------------------------|-------------------------------------------|-------------------------------|----------------------------------------------|
| termqt              | Pure Python, supports PySide6, VT100     | Not 100% complete             | pip install termqt                        |
| qtpyTerminal        | Cross-platform, uses Pyte (good VT100)   | Installed from Git            | pip install qtpy pytepip install git+https://github.com/mguijarr/qtpyTerminal.git |
| pyside6-qtermwidget | Full-featured (based on LXQt QTermWidget)| Heavier, may need system libs | pip install pyside6-qtermwidget           |

Example with qtpyTerminal (recommended for most cases)

import sys
from qtpy.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from qtpyTerminal import qtpyTerminal

app = QApplication(sys.argv)
win = QMainWindow()
win.setWindowTitle("Embedded Terminal")
container = QWidget()
layout = QVBoxLayout(container)

term = qtpyTerminal()
Optional: term.set_cmd("python")  # start Python REPL instead of shell
term.set_cols(120)
term.set_rows(30)

layout.addWidget(term)
win.setCentralWidget(container)
win.resize(900, 500)
win.show()

Start the terminal
term.start()

sys.exit(app.exec())

Example with termqt
See the start.py example in the termqt repository. You create a Terminal widget and connect it to a TerminalExecIO (which runs bash or cmd).

3. Other Approaches

Python REPL only** (not a full system terminal): Use libraries like adeqt or qonsole.
Embed external terminal** (Linux only): Use xterm -into or urxvt -embed with the widget’s winId(). Fragile and not recommended for production.
Serial / custom protocol**: Qt’s official serial-port terminal example shows a good console-style QPlainTextEdit pattern that you can adapt.

Recommendation

Quick prototype / simple needs** → Use the QProcess + QPlainTextEdit example above.
Proper interactive terminal* → Start with *qtpyTerminal* or *termqt**.
Maximum compatibility / features** → Try pyside6-qtermwidget if the wheel installs cleanly on your platform.

Would you like a more complete version of any of these (with command history, colors, copy/paste, or a specific shell)?