#!/usr/bin/env python3
r"""tests/ucp/build_ucp_store.py — CAPTURE libpcre2 10.46's UCP sets into the
committed store (docs/design/ucp_design.md §1.6, D130 Q9): the `membership`
kind under a UCP OracleId (`oracle_store/libpcre2-<ver>-ucp/`), over
`ucp_sets.py`'s population — every construct under `byte` and `utf8`, and
every spelling under `utf8` (a spelling like `\x{ff10}` does not compile
under byte).

The reference is the Linux box, over the tailnet, as ONE light ssh-stdin run
set (tests/oracle/remote_adapter.py; nothing is written remotely). An
IDEMPOTENT regeneration of the whole file, never an append (§7.1a).

    python3 tests/ucp/build_ucp_store.py [--host duxevents@100.69.121.107]
"""
import datetime
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.normpath(os.path.join(_HERE, "..", ".."))
sys.path.insert(0, os.path.join(_ROOT, "tests", "oracle"))
sys.path.insert(0, _HERE)

import oracle_store as os_  # noqa: E402
from remote_adapter import RemoteAdapter  # noqa: E402
from ucp_sets import SETS  # noqa: E402


def questions():
    out = []
    for cons, spell, _ in SETS:
        out.append({"property": cons, "encoding": "byte"})
        out.append({"property": cons, "encoding": "utf8"})
        q = {"property": spell, "encoding": "utf8"}
        if q not in out:
            out.append(q)
    return out


def main(argv):
    host = "duxevents@100.69.121.107"
    if "--host" in argv:
        host = argv[argv.index("--host") + 1]
    a = RemoteAdapter(host, ucp=True)
    a.MAX_BATCH = 24
    qs = questions()
    answers = a.answer([("membership", q) for q in qs])
    oid = a.oracle_id()
    rows = list(zip(qs, answers))
    path = os_.store_path(os.path.join(_ROOT, "oracle_store"), oid,
                          "membership")
    n = os_.write_store(
        path, oid, "membership", rows,
        datetime.datetime.now(datetime.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"),
        host, "python3 tests/ucp/build_ucp_store.py --host %s" % host)
    print("wrote %s (%d rows) from %s" % (path, n, oid))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
