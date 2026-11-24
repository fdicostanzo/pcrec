#!/usr/bin/env python3
"""clsets.py — the STUDY POPULATIONS, read out of the tree's own generated data.

Three populations, each a list of (name, intervals) where `intervals` is the
sorted, disjoint, non-adjacent code-point interval list pcrec's own
`src/core/cpset.c` invariant maintains:

  * `uprops()`   — the 312 DISTINCT sets behind module `unicode-props`' 717
                   name rows, read out of the Unicode tables through
                   `tests/uprops/ucd_dump.c` (the module's own interface).
                   Never re-derived from the UCD: the study measures the sets
                   pcrec ACTUALLY builds, the same discipline
                   `studies/form_char_twins` used when it parsed byte sets off
                   the emitted artifact rather than off the pattern.
  * `k53()`      — the six sets K53 named (docs/dev/known_issues.md), each
                   paired with its complement, since a refusing spelling's
                   polarity is half the population.
  * `byteclasses()` — byte-class sample: the 32-byte class bitmaps parsed out
                   of emitted artifacts (see extract_byteclasses.py, which
                   writes results/byteclasses.tsv).

No pcrec source is imported and nothing is written outside this directory.
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))

MAX_CP = 0x10FFFF


# ---------------------------------------------------------------- parsing

def _parse_inc(path=None):
    """Return (intervals, rows). intervals: list of (lo,hi). rows: list of
    (name, ns, off, n, ci_off, ci_n).

    [DATA-PLAN] A1: the table's storage format belongs to ONE module
    (`src/parse/ucd_tables.c`), so this no longer parses the generated file.
    It reads the TSV `tests/uprops/ucd_dump.c` writes through the module's
    interface: `$UCD_DUMP` names the file, or `build/ucd_dump` (a binary built
    from that source against `build/libpcrec.a`) is run.  Each row's two sets
    are appended to one pool, so `off`/`n` index it as before."""
    import subprocess
    path = path or os.environ.get("UCD_DUMP")
    if path:
        text = open(path, encoding="utf-8").read()
    else:
        exe = os.path.join(REPO, "build", "ucd_dump")
        if not os.path.exists(exe):
            raise SystemExit("clsets: set UCD_DUMP to the output of "
                             "tests/uprops/ucd_dump.c (or build it to %s)"
                             % exe)
        text = subprocess.run([exe], check=True, capture_output=True,
                              text=True).stdout
    def parse_set(s):
        if s == "-":
            return []
        return [(int(a, 16), int(b, 16))
                for a, b in (p.split("-") for p in s.split(","))]
    ivs, rows = [], []
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        name, ns, cs, ci = line.split("\t")
        off = len(ivs)
        ivs.extend(parse_set(cs))
        n = len(ivs) - off
        cio = len(ivs)
        ivs.extend(parse_set(ci))
        rows.append((name, int(ns), off, n, cio, len(ivs) - cio))
    return ivs, rows


def _slice(ivs, off, n):
    return tuple(ivs[off:off + n])


def uprops():
    """The DISTINCT sets, each named by the SHORTEST name that denotes it
    (with the namespace mask appended when a name answers in more than the
    bare namespace, so a name here is reproducible).  Sorted by interval
    count descending, so the worst real sets lead."""
    ivs, rows = _parse_inc()
    seen = {}
    for name, ns, off, n, cio, cin in rows:
        for o, c in ((off, n), (cio, cin)):
            key = _slice(ivs, o, c)
            if not key:
                continue
            label = name if c == n or o == off else name + "/ci"
            prev = seen.get(key)
            if prev is None or len(label) < len(prev):
                seen[key] = label
    out = [(lab, list(key)) for key, lab in seen.items()]
    out.sort(key=lambda kv: (-len(kv[1]), kv[0]))
    return out


def _complement(iv, max_cp=MAX_CP):
    out, pos = [], 0
    for lo, hi in iv:
        if lo > pos:
            out.append((pos, lo - 1))
        pos = hi + 1
    if pos <= max_cp:
        out.append((pos, max_cp))
    return out


def k53():
    """The six sets K53 named, each with its complement.

    docs/dev/known_issues.md K53 lists `\\p{L}`, `\\p{C}`, `\\p{Cn}` (the three
    that refused at filing), `\\p{Xan}`/`\\p{Xwd}` ("the same shape (measured)")
    and, from [M5.0] stage 5, the `Unknown` script set (`Zzzz`) — six sets,
    twelve spellings once both polarities are counted, which is the list the
    entry's own "all fourteen spellings compile" line enumerates.
    """
    ivs, rows = _parse_inc()
    want = {"L": "L", "C": "C", "CN": "Cn", "XAN": "Xan", "XWD": "Xwd",
            "ZZZZ": "Unknown(Zzzz)"}
    got = {}
    for name, ns, off, n, cio, cin in rows:
        if name in want and want[name] not in got:
            got[want[name]] = _slice(ivs, off, n)
    missing = [v for v in want.values() if v not in got]
    if missing:
        raise SystemExit("clsets: K53 names missing from the table: %s"
                         % ", ".join(missing))
    out = []
    for label in ("L", "C", "Cn", "Xan", "Xwd", "Unknown(Zzzz)"):
        iv = list(got[label])
        out.append((label, iv))
        out.append(("^" + label, _complement(iv)))
    return out


def byteclasses(path=None):
    """The byte-class sample, read from results/byteclasses.tsv (written by
    extract_byteclasses.py from EMITTED artifacts).  Each row is a 64-hex-digit
    256-bit membership word plus a provenance label."""
    path = path or os.path.join(HERE, "results", "byteclasses.tsv")
    if not os.path.exists(path):
        raise SystemExit("clsets: %s missing — run `make byteclasses` first"
                         % path)
    out = []
    for line in open(path, encoding="utf-8"):
        if line.startswith("#") or not line.strip():
            continue
        f = line.rstrip("\n").split("\t")
        bits = int(f[0], 16)
        members = [b for b in range(256) if (bits >> b) & 1]
        out.append((f[1], members_to_intervals(members)))
    return out


def members_to_intervals(members):
    out = []
    for m in sorted(members):
        if out and m == out[-1][1] + 1:
            out[-1] = (out[-1][0], m)
        else:
            out.append((m, m))
    return out


def population(which):
    return {"uprops": uprops, "k53": k53, "byteclasses": byteclasses}[which]()


def dump_iv(which, outdir):
    """Write one `lo hi` hex interval file per set — discover.c's input."""
    os.makedirs(outdir, exist_ok=True)
    names = []
    for name, iv in population(which):
        tag = "".join(c if c.isalnum() else "_" for c in name)
        with open(os.path.join(outdir, tag + ".iv"), "w") as f:
            for l, h in iv:
                f.write("%x %x\n" % (l, h))
        names.append((name, tag))
    with open(os.path.join(outdir, "INDEX.tsv"), "w") as f:
        for name, tag in names:
            f.write("%s\t%s\n" % (name, tag))
    return names


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--dump-iv":
        for w in sys.argv[2:]:
            ns = dump_iv(w, os.path.join(HERE, "build", "iv", w))
            print("dumped %d sets for %s" % (len(ns), w))
        sys.exit(0)
    which = sys.argv[1] if len(sys.argv) > 1 else "uprops"
    pop = population(which)
    tot = sum(len(iv) for _, iv in pop)
    print("# population=%s sets=%d intervals=%d" % (which, len(pop), tot))
    for name, iv in pop[:20]:
        span = iv[-1][1] - iv[0][0] + 1
        card = sum(h - l + 1 for l, h in iv)
        print("%-28s intervals=%-6d members=%-9d span=%d"
              % (name, len(iv), card, span))
