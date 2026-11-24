"""Permission-Aware Knowledge Assistant domain retrieval and answer rules."""
NAME = '11-permission-aware-knowledge-assistant'

from common import norm,require
FIELDS=("topic","scope","text")

def validate(rows):
    seen=set()
    for r in rows:
        key=norm(r["topic"]),r["scope"]
        require(r["scope"] in {"public","staff"} and key not in seen,"invalid visibility or duplicate topic")
        seen.add(key)

def lookup(rows,q,allowed):
    # The transport sets allowed from the authenticated peer. Query text never grants access.
    visible=[r for r in rows if r["scope"] in allowed]
    q=q.rstrip("?")
    if q.startswith("tell me about "): q=q[len("tell me about "):]
    scope="public"
    for label in ("public","staff"):
        if q.startswith(label+" "):
            scope=label
            q=q[len(label)+1:]
            break
    hits=[r for r in visible if norm(r["topic"])==q and r["scope"]==scope]
    if hits: return hits[0]["text"],hits,"scope-filtered lookup"

def solve(rows,q):
    return lookup(rows,q,{"public"})
