"""Qt parent harness for NchantdOffice -- TDD step 1.

The plan (per the production-readiness review and the
T-NEW-044 / T-NEW-045 follow-up): drive live Qt defects via a
subprocess that boots a real ``QApplication``, exposes a
``QLocalServer`` so a test can issue commands, and reports
readiness on stdout.

This file is the **server** half: a standalone script that
boots a minimal Qt tree and runs the event loop while
processing JSON commands over a local socket.

Why a separate script: it has to run in a *child* process so
the test's main thread is not blocked on the Qt event loop.
The test process imports nothing from here -- it just
spawns this script via ``subprocess.Popen`` and talks to it
over the socket.

Why a QLocalServer and not a TCP socket: the local socket
path is unique per test, no firewall, no port-collision
risk, and lives in a tmpdir we can clean up. Sticking to
local sockets also keeps the harness in-process-only, which
matters because the production consumer is a desktop app.

Handshake protocol:

    1. Server boots, picks a unique socket path under /tmp,
       creates a QApplication, builds a QMainWindow with
       ``objectName="qt_parent_root"``, and starts a
       QLocalServer listening on that path.
    2. Server writes a single line to stdout:
       ``READY <socket-path>``
       and flushes. The test reads this line to know the
       server is ready.
    3. Test connects, sends a single JSON line per command,
       receives a single JSON line per response, and closes.
    4. On SIGTERM / SIGINT / EOF on the socket, the server
       quits its event loop and exits 0.

This is a TDD RED-shaped harness. The plan is to ship step
1, prove the handshake works with a real pytest, then in
step 2 plug a real NchantdOfficeCloak into the same boot
path. If step 1 fails, we have not lost any work because
nothing else builds on it.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path


def _build_root_window(qt):
    """Create a ``QMainWindow`` with a known ``objectName``.

    The ``objectName`` is the contract: the test process
    walks ``QWidget.findChild(QWidget, "qt_parent_root")``
    to confirm the right window is up. No real NchantdOffice
    work happens in this step -- only the boot and the
    event loop plumbing.
    """
    from PySide6.QtWidgets import QMainWindow, QLabel

    window = QMainWindow()
    window.setObjectName("qt_parent_root")
    window.setWindowTitle("qt_parent_server")
    label = QLabel("qt_parent ready")
    label.setObjectName("qt_parent_label")
    window.setCentralWidget(label)
    return window


def _install_signal_handlers(qt_app, server):
    """Hook SIGTERM and SIGINT to a clean Qt quit.

    Without this, ``subprocess.Popen.terminate()`` kills the
    process abruptly and the socket is leaked. The test
    fixture's teardown relies on a graceful exit so the
    socket file is removed before the next test.
    """
    import signal

    def _handler(signum, frame):
        server.close()
        qt_app.quit()

    signal.signal(signal.SIGTERM, _handler)
    signal.signal(signal.SIGINT, _handler)


def _make_command_processor(window):
    """Return a function that takes a JSON command dict and
    returns a JSON-serialisable result dict.

    Supported commands in this step:

      - ``{"cmd": "ping"}`` -> ``{"result": "pong", "ts": <float>}``
      - ``{"cmd": "find", "name": <objectName>}`` -> ``{"found": bool, "class": str}``
      - ``{"cmd": "sizes", "name": <objectName>}`` -> ``{"w": int, "h": int}``
      - ``{"cmd": "root"}`` -> ``{"objectName": <str>}``

    The processor never raises; bad commands return
    ``{"error": "..."}`` so the client gets a structured
    failure instead of a broken connection.
    """
    from PySide6.QtWidgets import QWidget

    def _process(cmd):
        try:
            name = cmd.get("cmd")
            if name == "ping":
                import time
                return {"result": "pong", "ts": time.time()}
            if name == "root":
                return {"objectName": window.objectName()}
            if name == "find":
                target = cmd.get("name", "")
                # findChild only walks descendants. If the
                # caller asks for the root itself, return
                # the root window.
                if target == window.objectName():
                    found = window
                else:
                    found = window.findChild(QWidget, target)
                if found is None:
                    return {"found": False}
                return {
                    "found": True,
                    "class": type(found).__name__,
                    "objectName": found.objectName(),
                }
            if name == "sizes":
                target = cmd.get("name", "")
                if target == window.objectName():
                    found = window
                else:
                    found = window.findChild(QWidget, target)
                if found is None:
                    return {"found": False, "w": 0, "h": 0}
                sz = found.size()
                return {"found": True, "w": sz.width(), "h": sz.height()}
            return {"error": f"unknown cmd: {name!r}"}
        except Exception as exc:
            return {"error": f"{type(exc).__name__}: {exc}"}

    return _process


def main() -> int:
    # 1. Force the offscreen QPA BEFORE we import any Qt
    #    modules. PySide6 reads QT_QPA_PLATFORM at QApplication
    #    construction time; if a real X server is reachable
    #    the import path will pick xcb and crash in this
    #    environment.
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    # 2. Pick a unique socket path. The /tmp file is unlinked
    #    on QLocalServer.close() so we never accumulate
    #    orphans from crashed test runs.
    sock_dir = Path(tempfile.mkdtemp(prefix="qt-parent-"))
    sock_path = str(sock_dir / "socket")

    # 3. Now import Qt -- the env is set.
    from PySide6.QtCore import QByteArray, QTimer
    from PySide6.QtNetwork import QLocalServer
    from PySide6.QtWidgets import QApplication

    qt_app = QApplication.instance() or QApplication(sys.argv)
    window = _build_root_window(qt_app)

    # 4. Start the QLocalServer and emit the READY line.
    server = QLocalServer()
    if not server.listen(sock_path):
        print(f"FAIL listen: {server.errorString()}", file=sys.stderr)
        return 2
    print(f"READY {sock_path}", flush=True)

    process_cmd = _make_command_processor(window)

    def _on_new_connection():
        # The server processes one client at a time. That
        # is sufficient for a single pytest; the test
        # sends one command, reads one response, and closes.
        sock = server.nextPendingConnection()
        if sock is None:
            return

        # Read until newline. Use a 1-second idle timeout
        # so a half-open client does not wedge the server.
        from PySide6.QtCore import QTextStream

        sock.readyRead.connect(lambda: _read_line(sock))
        sock.disconnected.connect(sock.deleteLater)

        def _read_line(s):
            # Drain available bytes; the test sends one
            # line per command, so we look for the first
            # newline and process whatever is on that line.
            while s.bytesAvailable() > 0:
                data = bytes(s.readAll()).decode("utf-8", errors="replace")
                # Multiple lines could pile up; split on
                # newline and process each.
                for line in data.splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        cmd = json.loads(line)
                    except json.JSONDecodeError as exc:
                        s.write(QByteArray(
                            (json.dumps({"error": f"bad json: {exc}"}) + "\n").encode()
                        ))
                        s.flush()
                        continue
                    result = process_cmd(cmd)
                    s.write(QByteArray(
                        (json.dumps(result) + "\n").encode()
                    ))
                    s.flush()

    server.newConnection.connect(_on_new_connection)
    _install_signal_handlers(qt_app, server)

    # 5. Show the window so the widget tree is alive and
    #    visible (visible widgets only - this matters for
    #    downstream NchantdOffice tests that look for
    #    actually-rendered widgets).
    window.show()

    # 6. Run the event loop. QLocalServer fires
    #    newConnection on the loop; the handlers above do
    #    the rest.
    return qt_app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
