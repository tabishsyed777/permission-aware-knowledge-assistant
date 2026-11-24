"""Unix socket transport. Caller roles come exclusively from kernel credentials."""
import argparse
import json
import os
import socket
import socketserver
import struct
import sys
from pathlib import Path

import core
import domain


def peer_uid(connection):
    if hasattr(socket, "SO_PEERCRED"):
        raw = connection.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize("3i"))
        return struct.unpack("3i", raw)[1]
    if hasattr(connection, "getpeereid"):
        return connection.getpeereid()[0]
    raise RuntimeError("Kernel peer credentials unavailable")


class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        self.connection.settimeout(3)
        try:
            uid = peer_uid(self.connection)
            raw = self.rfile.readline(8193)
            core.require(raw.endswith(b"\n") and len(raw) <= 8192, "invalid frame")
            obj = json.loads(raw)
            core.require(isinstance(obj, dict) and set(obj) == {"question"}, "invalid fields")
            q = obj["question"]
            core.require(isinstance(q,str) and 0 < len(q.strip()) <= 1000,"invalid query")
            scopes = {"public", "staff"} if uid in self.server.staff else {"public"}
            match = domain.lookup(self.server.rows, core.norm(q), scopes)
            reply = {"status":"insufficient_evidence","answer":None,"citations":[]}
            if match:
                value, evidence, method = match
                reply = {"status":"answered","answer":value,"method":method,
                         "citations":[{"id":r["id"],"source":r["source"]} for r in evidence]}
        except (OSError, RuntimeError, TypeError, ValueError):
            reply = {"status":"invalid_request"}
        self.wfile.write(json.dumps(reply).encode()+b"\n")


class Server(socketserver.UnixStreamServer):
    def __init__(self, path, rows, staff):
        self.rows = rows
        self.staff = frozenset(staff)
        super().__init__(str(path), Handler)


def request(path, payload):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.settimeout(5)
        sock.connect(str(path))
        sock.sendall(json.dumps(payload).encode()+b"\n")
        with sock.makefile("rb") as stream:
            return json.loads(stream.readline())


def main():
    parser = argparse.ArgumentParser()
    actions = parser.add_subparsers(dest="cmd", required=True)
    serve = actions.add_parser("serve")
    serve.add_argument("socket")
    serve.add_argument("--source", type=Path, default=core.DEFAULT)
    serve.add_argument("--staff-uid", action="append", type=int, default=[])
    ask = actions.add_parser("ask")
    ask.add_argument("socket")
    ask.add_argument("question")
    args = parser.parse_args()
    if args.cmd=="ask":
        print(json.dumps(request(args.socket, {"question":args.question}), indent=2))
        return
    rows = core.validate(core.read(args.source))
    os.umask(0o117)
    with Server(args.socket, rows, args.staff_uid) as server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            Path(args.socket).unlink(missing_ok=True)


if __name__=="__main__":
    main()
