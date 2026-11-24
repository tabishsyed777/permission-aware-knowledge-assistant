import os
import json
import socket
from types import SimpleNamespace
import tempfile
import threading
import unittest
from pathlib import Path
import core
import service


class TransportTests(unittest.TestCase):
    def exchange(self, staff, payload):
        context = SimpleNamespace(rows=core.validate(core.read(core.DEFAULT)),staff=staff)
        client, server = socket.socketpair()
        with client, server:
            thread = threading.Thread(target=service.Handler,args=(server,None,context))
            thread.start()
            try:
                client.settimeout(5)
                client.sendall(json.dumps(payload).encode()+b"\n")
                with client.makefile("rb") as stream:
                    return json.loads(stream.readline())
            finally:
                thread.join(5)

    def test_filesystem_listener(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"qa.sock"
            try:
                server=service.Server(path,core.validate(core.read(core.DEFAULT)),[])
            except PermissionError as exc:
                self.skipTest(f"host blocks AF_UNIX listener: {exc}")
            with server:
                thread=threading.Thread(target=server.handle_request)
                thread.start()
                try:
                    self.assertEqual(service.request(path,{"question":"parking"})["status"],"answered")
                finally:
                    thread.join(5)
    def test_authorized(self):
        self.assertEqual(self.exchange([os.getuid()],{"question":"staff parking"})["answer"],"Use lot F.")
    def test_denied(self):
        self.assertEqual(self.exchange([],{"question":"staff parking"})["citations"],[])
    def test_role_forgery(self):
        self.assertEqual(self.exchange([],{"question":"staff parking","scope":"staff"}),{"status":"invalid_request"})
