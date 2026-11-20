"""One window per session: a second start finds the first and asks it to show itself."""

import os
import tempfile
import unittest

try:
    from PyQt5.QtCore import QCoreApplication
    from PyQt5.QtNetwork import QLocalServer  # noqa: F401
    HAVE_QT = True
except ImportError:  # the stubbed test runs have no real PyQt5
    HAVE_QT = False

import single_instance


class SocketPathTests(unittest.TestCase):
    def test_no_runtime_dir_means_no_single_instance(self):
        old = os.environ.pop("XDG_RUNTIME_DIR", None)
        try:
            self.assertIsNone(single_instance.socket_path())
            os.environ["XDG_RUNTIME_DIR"] = "relative/dir"
            self.assertIsNone(single_instance.socket_path())
        finally:
            if old is None:
                os.environ.pop("XDG_RUNTIME_DIR", None)
            else:
                os.environ["XDG_RUNTIME_DIR"] = old

    def test_socket_lives_in_the_runtime_dir(self):
        with tempfile.TemporaryDirectory() as d:
            old = os.environ.get("XDG_RUNTIME_DIR")
            os.environ["XDG_RUNTIME_DIR"] = d
            try:
                self.assertEqual(single_instance.socket_path(), os.path.join(d, "av-morning-star.socket"))
            finally:
                if old is None:
                    os.environ.pop("XDG_RUNTIME_DIR", None)
                else:
                    os.environ["XDG_RUNTIME_DIR"] = old


@unittest.skipUnless(HAVE_QT, "needs PyQt5.QtNetwork")
class ForwardTests(unittest.TestCase):
    def setUp(self):
        self.app = QCoreApplication.instance() or QCoreApplication([])
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "av-morning-star.socket")

    def tearDown(self):
        self.dir.cleanup()

    def pump(self):
        for _ in range(20):
            self.app.processEvents()

    def test_a_second_start_reaches_the_first(self):
        shown = []
        server = single_instance.listen(self.path, lambda: shown.append(1))
        self.assertIsNotNone(server)
        self.assertTrue(single_instance.forward_to_running(self.path))
        self.pump()
        self.assertEqual(shown, [1])
        server.close()

    def test_nobody_running_means_this_start_owns_the_window(self):
        self.assertFalse(single_instance.forward_to_running(self.path))

    def test_a_crashed_copys_socket_is_taken_over(self):
        open(self.path, "w").close()  # stale file where the socket should be
        server = single_instance.listen(self.path, lambda: None)
        self.assertIsNotNone(server)
        server.close()


if __name__ == "__main__":
    unittest.main()
