# Permission-Aware Knowledge Assistant

Filter evidence by authorized scope before topic retrieval. The offline CLI answers public questions. A local Unix socket service supports authenticated staff queries using operating-system peer identities.

## Quick start

From this directory, run these commands with Python 3.12 or 3.13. The example corpus is fictional and runs offline with the standard library.

```sh
python3 core.py ask 'onboarding'
python3 core.py build data/source.json snapshot.json
python3 core.py ask 'Tell me about onboarding' --snapshot snapshot.json
python3 -m unittest discover -v
python3 evaluate.py
```

## Asking questions

Use “Tell me about parking” for the public policy. The service also accepts “staff parking” for UIDs on its administrator-configured allowlist.

## Using your own sources

Use the records in `data/source.json` as a schema example. Supply unique citation IDs and usable source locators. Build a new snapshot after additions, edits, or deletions. A successful build atomically replaces the previous snapshot. Results contain the answer, retrieval method and source locators. Unsupported queries return `insufficient_evidence`.

For multiuser deployment, keep source, snapshots and UID policy readable only by the service administrator. Use a dedicated service account and expose only the socket to clients. The sample corpus is fictional. See SERVICE.md.

See [QA.md](QA.md) for measured results, review status and release limits.
