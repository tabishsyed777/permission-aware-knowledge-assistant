# Local service

The transport is tested on Linux with SO_PEERCRED. It denies requests if kernel credentials are unavailable. The admin starts the service with the Unix user IDs permitted to retrieve staff entries.

Run this single-user example from the project directory. The temporary directory limits access to your account.

```sh
socket_dir=$(mktemp -d)
python3 service.py serve "$socket_dir/faq.sock" --staff-uid "$(id -u)" &
server_pid=$!
# Once the socket exists:
python3 service.py ask "$socket_dir/faq.sock" "staff parking"
kill "$server_pid"
```

In a multiuser setup, use an administrator-owned socket directory accessible to the intended Unix group, with no client write permission on the directory. The service creates a group-accessible socket. Restrict the data files separately. Restart the service to reload data or change the allowlist. The server handles requests sequentially. The concurrent retrieval benchmark in QA.md measures the underlying snapshot reader. The transport tests send authorized, denied and forged-role requests over actual sockets. Production throughput and external security review are pending.
