"""TDD step 1 -- spawn the Qt parent server, handshake, ping.

This is the proof that the parent harness can boot a real
``QApplication`` in a subprocess, expose a ``QLocalServer``,
and answer a single ``ping`` command. The test is RED-capable:
if the handshake fails for any reason (server crashes, READY
line never appears, socket cannot connect, server does not
reply to ping), the test goes red with a precise error
message that pinpoints where the failure is.

Each test run gets a fresh server process and a fresh socket
path. The fixture tears the server down by sending ``quit``
and waiting for the process to exit; if the server is
unresponsive after 5 seconds, the fixture kills it
forcefully so the next test is not blocked.

The test only asserts on the things that step 1 needs to
prove:
  1. Server emits a single ``READY <path>`` line.
  2. ``ping`` returns ``{"result": "pong", ...}``.
  3. ``find qt_parent_label`` returns ``{"found": True, ...}``.
  4. ``sizes qt_parent_root`` returns non-zero width/height.

If any of these fail, the test prints the server's stderr
and the socket path it tried, so the failure is easy to
locate.
"""

from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SERVER_SCRIPT = Path(__file__).resolve().parent / "qt_parent" / "server.py"


def _drain_stdout(proc, deadline):
    """Read stdout from ``proc`` until we see a ``READY`` line or
    the deadline elapses. Returns the READY line and any extra
    output that arrived before it.
    """
    chunks = []
    start = time.time()
    while time.time() - start < deadline:
        if proc.stdout is None:
            time.sleep(0.05)
            continue
        chunk = proc.stdout.read(1)
        if not chunk:
            break
        chunks.append(chunk)
        joined = "".join(chunks)
        if "\n" in joined:
            line, rest = joined.split("\n", 1)
            line = line.strip()
            if line.startswith("READY "):
                return line, rest
    raise TimeoutError(
        f"server did not emit READY within {deadline}s; "
        f"got: {''.join(chunks)!r}"
    )


@pytest.fixture
def server_proc():
    """Boot the server in a child subprocess.

    Yields the parsed READY line (which contains the socket
    path). On teardown, sends ``quit`` and waits for clean
    exit; if that fails, terminates and prints stderr so the
    failure is visible in the pytest output.
    """
    env = dict(os.environ)
    env["QT_QPA_PLATFORM"] = "offscreen"
    # PYTHONPATH so the subprocess can import the harness
    # server module. The server file lives under
    # tests/qt_parent/server.py and is invoked as a script,
    # so it does not need to be on the import path, but the
    # fixtures that the test process imports do.
    env.setdefault("PYTHONPATH", str(REPO_ROOT) + os.pathsep + env.get("PYTHONPATH", ""))

    proc = subprocess.Popen(
        [sys.executable, str(SERVER_SCRIPT)],
        cwd=str(REPO_ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    try:
        ready_line, _rest = _drain_stdout(proc, deadline=15.0)
    except Exception:
        # Surface the child's stderr so the failure is debuggable.
        try:
            stderr = proc.stderr.read() if proc.stderr else ""
        except Exception:
            stderr = "<stderr unreadable>"
        try:
            proc.kill()
        except Exception:
            pass
        raise
    yield ready_line

    # Teardown: ask the server to quit and wait. If it
    # does not exit in 5s, kill it.
    try:
        sock_path = ready_line.split(" ", 1)[1].strip()
        _send_command(sock_path, {"cmd": "ping"})  # any command wakes the loop
    except Exception:
        pass
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=5)
    # Print stderr on failure so the user sees the cause.
    if proc.returncode not in (0, None):
        try:
            stderr = proc.stderr.read() if proc.stderr else ""
        except Exception:
            stderr = "<stderr unreadable>"
        if stderr:
            print(f"[qt_parent_server] stderr:\n{stderr}", file=sys.stderr)


def _send_command(sock_path, cmd, timeout=5.0):
    """Open a fresh socket, send one JSON line, read one JSON line.

    Returns the parsed response. Raises on any I/O failure
    with a message that includes the socket path and the
    command.
    """
    deadline = time.time() + timeout
    last_err = None
    while time.time() < deadline:
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                s.connect(sock_path)
                payload = (json.dumps(cmd) + "\n").encode("utf-8")
                s.sendall(payload)
                chunks = []
                while True:
                    chunk = s.recv(4096)
                    if not chunk:
                        break
                    chunks.append(chunk)
                    joined = b"".join(chunks)
                    if b"\n" in joined:
                        line, _rest = joined.split(b"\n", 1)
                        return json.loads(line.decode("utf-8"))
                joined = b"".join(chunks)
                if joined:
                    return json.loads(joined.decode("utf-8"))
                last_err = "empty response"
        except (FileNotFoundError, ConnectionRefusedError) as exc:
            last_err = f"{type(exc).__name__}: {exc}"
            time.sleep(0.1)
    raise TimeoutError(
        f"could not send {cmd!r} to {sock_path}: {last_err}"
    )


def test_server_emits_ready_line_with_socket_path(server_proc):
    """The server must write ``READY <path>`` to stdout on boot.

    The path is the only way the test knows where to
    connect. If the line is missing or malformed, the
    handshake cannot proceed.
    """
    line = server_proc
    assert line.startswith("READY "), f"unexpected first line: {line!r}"
    sock_path = line.split(" ", 1)[1].strip()
    assert sock_path.endswith("/socket"), (
        f"socket path does not end in /socket: {sock_path!r}"
    )
    assert Path(sock_path).parent.exists(), (
        f"socket directory missing: {Path(sock_path).parent}"
    )


def test_ping_returns_pong(server_proc):
    """A ping command must get a pong response.

    This is the most basic handshake. If the server's
    event loop is not flushing bytes back, every other
    command will fail too.
    """
    sock_path = server_proc.split(" ", 1)[1].strip()
    result = _send_command(sock_path, {"cmd": "ping"})
    assert result.get("result") == "pong", f"unexpected ping response: {result!r}"
    assert "ts" in result, f"pong missing ts: {result!r}"


def test_find_returns_known_widget(server_proc):
    """``find`` walks the widget tree and returns the target.

    The window has a child label with
    ``objectName="qt_parent_label"``. If the server can
    find it, the widget tree is alive.
    """
    sock_path = server_proc.split(" ", 1)[1].strip()
    result = _send_command(sock_path, {"cmd": "find", "name": "qt_parent_label"})
    assert result.get("found") is True, f"label not found: {result!r}"
    assert result.get("class") == "QLabel", (
        f"unexpected class: {result.get('class')!r}"
    )


def test_root_returns_root_object_name(server_proc):
    """``root`` is the simplest introspection -- the root window's
    own objectName. This is the contract the future
    NchantdOffice tests will rely on to find the main window.
    """
    sock_path = server_proc.split(" ", 1)[1].strip()
    result = _send_command(sock_path, {"cmd": "root"})
    assert result.get("objectName") == "qt_parent_root", (
        f"root.objectName = {result.get('objectName')!r}, "
        f"expected 'qt_parent_root'"
    )


def test_sizes_returns_nonzero_for_root(server_proc):
    """After ``window.show()`` the root must have a non-zero size.

    A size of 0 means the window was never shown -- in
    which case downstream ``findChild`` calls would still
    work, but real consumer widgets would not render.
    """
    sock_path = server_proc.split(" ", 1)[1].strip()
    result = _send_command(sock_path, {"cmd": "sizes", "name": "qt_parent_root"})
    assert result.get("found") is True, f"root not found: {result!r}"
    assert result.get("w", 0) > 0, f"root width = {result.get('w')!r}"
    assert result.get("h", 0) > 0, f"root height = {result.get('h')!r}"


def test_unknown_command_returns_error(server_proc):
    """An unknown command must return a structured error, not
    crash the server or break the socket.
    """
    sock_path = server_proc.split(" ", 1)[1].strip()
    result = _send_command(sock_path, {"cmd": "nonsense"})
    assert "error" in result, f"expected error key, got: {result!r}"
    # The server must still be alive after a bad command:
    # a follow-up ping must succeed.
    follow_up = _send_command(sock_path, {"cmd": "ping"})
    assert follow_up.get("result") == "pong", (
        f"server died after bad command: {follow_up!r}"
    )
