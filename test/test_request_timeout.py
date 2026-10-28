"""Request timeout regression test; no Spotify credentials or network required."""

import socket
import tempfile
import threading
import unittest
from unittest.mock import patch

from urllib3 import Timeout
from urllib3.exceptions import MaxRetryError, ReadTimeoutError

from spotifywebapipython import spotifyclient
from spotifywebapipython.spotifyclient import SpotifyClient


class RequestTimeoutTest(unittest.TestCase):

    def setUp(self):
        # a server that never answers: the kernel completes the connection and
        # takes the request, but nothing ever accepts or reads it.
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addCleanup(self.server.close)
        self.server.bind(("127.0.0.1", 0))
        self.server.listen(16)

        # keep the client's timeouts, with a finite read shortened to fractions of a second.
        timeout = patch.object(
            spotifyclient, "Timeout",
            lambda connect=None, read=None: Timeout(connect=connect, read=None if read is None else 0.2),
        )
        timeout.start()
        self.addCleanup(timeout.stop)

        storage = tempfile.TemporaryDirectory()
        self.addCleanup(storage.cleanup)
        self.client = SpotifyClient(tokenStorageDir=storage.name, spotifyConnectDirectoryEnabled=False)

    def test_stalled_reply_raises_instead_of_blocking(self):
        errors = []

        def request():
            try:
                self.client._Manager.request("GET", "http://127.0.0.1:%d/" % self.server.getsockname()[1])
            except Exception as ex:
                errors.append(ex)

        caller = threading.Thread(target=request, daemon=True)
        caller.start()
        caller.join(10)

        self.assertFalse(caller.is_alive(), "the request is still waiting for a reply that never comes")
        self.assertIsInstance(errors[0], MaxRetryError)
        self.assertIsInstance(errors[0].reason, ReadTimeoutError)


if __name__ == "__main__":
    unittest.main()
