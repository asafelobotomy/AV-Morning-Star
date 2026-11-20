"""One window per session.

A second start (the menu entry clicked while the app is already open) asks the
running copy to bring its window forward and then exits, so two copies never
download into the same folder at once.

The running copy listens on a local socket in ``$XDG_RUNTIME_DIR``, which only
this user can reach. Without that directory every start gets its own window,
as before.
"""

import os

SOCKET_NAME = "av-morning-star.socket"


def socket_path():
    """The session's socket path, or None when there is no usable runtime dir."""
    runtime = os.environ.get("XDG_RUNTIME_DIR", "")
    if not runtime or not os.path.isabs(runtime) or not os.path.isdir(runtime):
        return None
    return os.path.join(runtime, SOCKET_NAME)


def forward_to_running(path):
    """Ask a running copy to show itself. True if one answered."""
    from PyQt5.QtNetwork import QLocalSocket  # imported here so main.py imports without QtNetwork (tests stub PyQt5)

    probe = QLocalSocket()
    probe.connectToServer(path)
    if not probe.waitForConnected(1000):
        return False
    probe.write(b"show\n")
    probe.waitForBytesWritten(1000)
    probe.disconnectFromServer()
    return True


def listen(path, on_show, parent=None):
    """Own the session's socket and call ``on_show`` whenever another start
    asks. A socket left by a copy that crashed is taken over. Returns the
    server, or None if it couldn't listen (then a second start opens a second
    window)."""
    from PyQt5.QtNetwork import QLocalServer

    server = QLocalServer(parent)
    server.setSocketOptions(QLocalServer.UserAccessOption)
    if not server.listen(path):
        QLocalServer.removeServer(path)
        if not server.listen(path):
            print(f"av-morning-star: can't listen on {path} ({server.errorString()}); "
                  "a second start will open a second window")
            return None

    def accept():
        while True:
            peer = server.nextPendingConnection()
            if peer is None:
                break
            peer.disconnected.connect(peer.deleteLater)
            on_show()

    server.newConnection.connect(accept)
    return server


def claim(app, get_window):
    """Run once the QApplication exists, before any window. Returns True when
    another copy is already open (it has been asked to come forward, so this
    start should exit). Otherwise this copy now owns the session and brings
    ``get_window()`` forward when a later start asks."""
    path = socket_path()
    if path is None:
        return False
    if forward_to_running(path):
        return True

    def show():
        window = get_window()
        if window is None:  # still on the splash screen; it shows the window itself
            return
        if window.isMinimized():
            window.showNormal()
        window.show()
        window.raise_()
        window.activateWindow()

    server = listen(path, show, app)
    if server is not None:
        app.aboutToQuit.connect(server.close)
        app._single_instance_server = server  # keep it alive with the app
    return False
