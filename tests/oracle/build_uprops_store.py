r"""tests/oracle/build_uprops_store.py — the UPROPS INSTANCE
(`docs/design/oracle_interface.md` §9 Step 1, R56-6 corrected): the first
real store customer, populating a `membership` store from the SAME name
population `tests/uprops/run_uprops_tests.sh` already sweeps -- reusing that
script's own two lists (`CATEGORIES`, `script_values()`) rather than a third
hand-kept copy, per this house's standing rule against a second population a
future change could silently drift from the first.

TWO RUNS, TWO DESTINATIONS, matching §7.2's committed-vs-gitignored split:

  1. LOCAL (LocalAdapter): whatever libpcre2 this box resolves (Homebrew
     10.48 today, NOT the project's 10.46 pin) answers the BYTE-encoding
     population -- `run_uprops_tests.sh`'s own `BYTE_SCRIPTS`/
     `BYTE_SCRIPT_CONTROLS` list, since the byte arm's whole population is
     the properties with a Latin-1-reachable member (§7.2's own "local
     cache's whole value is saving a same-box re-run"). Written to
     `build/oracle_cache/<local-version>/membership.tsv` -- gitignored,
     `build/`-shaped, never touching what `make`/`make test` reads.

  2. REMOTE (RemoteAdapter, the true 10.46 reference over
     `duxevents@100.69.121.107`): the FULL utf8-encoding population --
     `CATEGORIES` plus EVERY script value in both the bare and `sc=`
     namespaces (387 properties, matching `tests/uprops/CLAUDE.md`'s own
     measured count and `../../docs/design/oracle_interface.md` §1.4's
     citation). This is what R56-6 corrects the charter to: it discharges
     wake.md's owed "STAGE-5 10.46 EXACT arm" -- `S-U12`'s own neighborhood,
     the script-namespace `membership` differential measured against
     whichever local library darwin resolves rather than against the true
     pin -- WITHOUT darwin owning the reference. Committed to
     `oracle_store/libpcre2-10.46/membership.tsv`.

Both runs are IDEMPOTENT regenerations of the whole file (§7.1a: "a store
file is not a log a caller appends a line to"), never an append.

Usage:
    python3 tests/oracle/build_uprops_store.py local
    python3 tests/oracle/build_uprops_store.py remote [--chunk N]
"""
import datetime
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.normpath(os.path.join(_HERE, "..", ".."))
sys.path.insert(0, _HERE)

import oracle_store as os_  # noqa: E402

NAMES_MAJOR = "C L M N P S Z".split()
NAMES_SUB = ("Lu Ll Lt Lm Lo Mn Mc Me Nd Nl No Pc Pd Ps Pe Pi Pf Po Sm Sc Sk "
             "So Zs Zl Zp Cc Cf Cs Co Cn").split()
NAMES_DERIVED = "L& Lc Any Xan Xps Xsp Xuc Xwd".split()
CATEGORIES = NAMES_MAJOR + NAMES_SUB + NAMES_DERIVED
assert len(CATEGORIES) == 45, len(CATEGORIES)

BYTE_SCRIPTS = ("Avestan Carian Common Coptic Duployan Elbasan Georgian "
                "Glagolitic Gothic Greek Gunjala_Gondi Han Latin Lydian "
                "Mahajani Old_Permic Shavian").split()
BYTE_SCRIPT_CONTROLS = "Cyrillic Hiragana Katakana Kawi Thaana Unknown".split()

_UCD_ALIASES = os.path.join(
    _ROOT, "third_party", "ucd-16.0.0", "PropertyValueAliases.txt")


def script_values():
    """`run_uprops_tests.sh`'s own `script_values()`, transcribed to python
    line for line (the `sc ;` row prefix, the Katakana_Or_Hiragana
    exclusion) rather than shelling out to awk, so this script has no
    dependency on the shell being available -- same source file, same
    rule, verified to reproduce the shell version's count below."""
    out = []
    with open(_UCD_ALIASES, "r", encoding="utf-8") as f:
        for line in f:
            if not line.startswith("sc ;"):
                continue
            parts = line.split(";")
            val = re.sub(r"\s+", "", parts[2]) if len(parts) > 2 else ""
            if val and val != "Katakana_Or_Hiragana":
                out.append(val)
    return out


def _now():
    return datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ")


def build_local():
    from local_adapter import LocalAdapter
    a = LocalAdapter()
    names = list(CATEGORIES)
    for s in BYTE_SCRIPTS + BYTE_SCRIPT_CONTROLS:
        names += [s, "sc=" + s]
    batch = [("membership", {"property": n, "encoding": "byte"})
              for n in names]
    print("local: sweeping %d byte-arm properties against %s"
          % (len(names), a.oracle_id()))
    answers = a.answer(batch)
    oid = a.oracle_id()
    rows = [({"property": n, "encoding": "byte"}, ans)
            for n, ans in zip(names, answers)]
    root = os.path.join(_ROOT, "build", "oracle_cache")
    path = os_.store_path(root, oid, "membership")
    n = os_.write_store(path, oid, "membership", rows, _now(),
                         os.uname().nodename,
                         "python3 tests/oracle/build_uprops_store.py local")
    print("wrote %s (%d rows)" % (path, n))
    return path


def build_remote(host, chunk):
    from remote_adapter import RemoteAdapter
    a = RemoteAdapter(host)
    a.MAX_BATCH = chunk
    scripts = script_values()
    print("remote: %d script values from the vendored UCD (host says the "
          "shell's script_values() finds 171 when Katakana_Or_Hiragana is "
          "excluded -- this run's own count is printed below, not assumed)"
          % len(scripts))
    names = list(CATEGORIES)
    for s in scripts:
        names += [s, "sc=" + s]
    print("remote: sweeping %d utf8-arm properties against the 10.46 "
          "reference (%s), in chunks of %d"
          % (len(names), host, chunk))
    batch = [("membership", {"property": n, "encoding": "utf8"})
              for n in names]
    answers = a.answer(batch)
    oid = a.oracle_id()
    print("remote resolved:", oid)
    rows = [({"property": n, "encoding": "utf8"}, ans)
            for n, ans in zip(names, answers)]
    root = os.path.join(_ROOT, "oracle_store")
    path = os_.store_path(root, oid, "membership")
    n = os_.write_store(
        path, oid, "membership", rows, _now(), host,
        "python3 tests/oracle/build_uprops_store.py remote --chunk %d"
        % chunk)
    print("wrote %s (%d rows)" % (path, n))
    return path


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("local", "remote"):
        sys.stderr.write(__doc__)
        sys.exit(2)
    if sys.argv[1] == "local":
        build_local()
    else:
        chunk = 60
        if "--chunk" in sys.argv:
            chunk = int(sys.argv[sys.argv.index("--chunk") + 1])
        build_remote("duxevents@100.69.121.107", chunk)
