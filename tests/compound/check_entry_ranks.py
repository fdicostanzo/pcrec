#!/usr/bin/env python3
"""tests/compound/check_entry_ranks.py -- E0's rank fixture check: the RANK
column of `entry_rows[]` against a hand fixture and against the emitted C
(docs/design/compound_entries.md §3.2, §3.6; a precondition of E1).

  check_entry_ranks.py DRIVE PCREC TREE WORKDIR [--every N]

DRIVE is tests/compound/compound_drive.c built; its `ranks` subcommand
compiles each pattern as the default build does, writes the artifact, and
prints the edge relation `entry_rows[]` derived for that artifact's shape
with each edge's rank.

  (1) THE FIXTURE (entry_ranks.tsv, hand-written from the emitted C): every
      witness row's edge exists with the fixture's rank, and the row's call
      site appears in the `from` function's body of the written artifact
      exactly `count` times, so a witness that stopped reaching its site
      fails rather than passing on a stale edge. Every rank R0..R3 has a
      witness row or an UNWITNESSED row (reported, never passed); neither is
      a failure, and so is both.
  (2) THE RE-SEED POPULATION: over every N-th distinct corpus pattern, each
      artifact whose `search_run` calls the hybrid's embedded search is R3
      exactly where that body holds a second `<p>_prefilter(` call site (the
      retry's re-seed), read from the text, never from the rank predicate's
      inputs. Floors on both sides (K35).

Exit 1 on any failure.
"""
import os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "startset"))
from startset_lib import corpus_blocks  # noqa: E402

RANKS = ("R0", "R1", "R2", "R3")
# Per-population floors at the Makefile's EVERY=8 (measured 2026-10-16 at
# EVERY=1: 910 R3, 449 R2 of 4,243 distinct patterns); scaled by EVERY.
FLOOR_R3, FLOOR_R2 = 910, 449


def fn_body(src, name):
    """The body of the function `name` defined in `src`: from its opening
    brace to the first closing brace in column 0, or None."""
    for m in re.finditer(r"(?m)^[A-Za-z][^;{]*?\b%s\(" % re.escape(name), src):
        j = m.end()
        while j < len(src) and src[j] not in "{;":
            j += 1
        if j < len(src) and src[j] == "{":
            k = src.find("\n}", j)
            return src[j:k] if k >= 0 else None
    return None


def c_name(entry):
    """The emitted function an entry name denotes at prefix `rx`."""
    return "main" if entry == "main" else "rx_" + entry


def drive_ranks(drive, outdir, cases):
    """{id: {(from, to): rank}} and the refused ids, from `drive ranks`."""
    os.makedirs(outdir, exist_ok=True)
    inp = "".join("%s\t%s\t%s\n" % (i, a, p.hex()) for i, a, p in cases)
    r = subprocess.run([drive, "ranks", outdir], input=inp.encode(),
                       capture_output=True, timeout=3600)
    if r.returncode:
        print("FAIL: compound_drive ranks exited %d: %s" % (r.returncode, r.stderr[:300]))
        return None, None
    edges, refused = {}, set()
    for ln in r.stdout.decode().splitlines():
        f = ln.split("\t")
        if len(f) == 2 and f[1] == "refused":
            refused.add(f[0])
        elif len(f) == 4:
            edges.setdefault(f[0], {})[(f[1], f[2])] = f[3]
    return edges, refused


def read_fixture(path):
    rows, unw = [], {}
    with open(path, encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.rstrip("\n")
            if not ln or ln.startswith("#"):
                continue
            f = ln.split("\t")
            if len(f) >= 2 and f[1] == "UNWITNESSED":
                unw[f[0]] = f[2] if len(f) > 2 else ""
            elif len(f) == 8:
                rows.append(dict(zip(("rank", "id", "arms", "pattern", "from",
                                      "to", "site", "count"), f)))
            else:
                print("FAIL: fixture: malformed row: %r" % ln)
                return None, None
    return rows, unw


def check_fixture(drive, work):
    rows, unw = read_fixture(os.path.join(HERE, "entry_ranks.tsv"))
    if rows is None:
        return 1
    fails = 0
    for r in rows:
        if r["rank"] not in RANKS:
            print("FAIL: fixture %s: rank %r" % (r["id"], r["rank"])); fails += 1
    for rk in RANKS:
        wit = [r for r in rows if r["rank"] == rk]
        if wit and rk in unw:
            print("FAIL: %s is both witnessed and UNWITNESSED" % rk); fails += 1
        elif not wit and rk not in unw:
            print("FAIL: %s has no witness and no UNWITNESSED row" % rk); fails += 1
        elif not wit:
            print("UNWITNESSED: %s (%s)" % (rk, unw[rk]))
    cases = [(r["id"], r["arms"], r["pattern"].encode()) for r in rows]
    out = os.path.join(work, "fixture")
    edges, refused = drive_ranks(drive, out, cases)
    if edges is None:
        return fails + 1
    for r in rows:
        tag = "fixture %s (%s %s -> %s)" % (r["id"], r["pattern"], r["from"], r["to"])
        if r["id"] in refused:
            print("FAIL: %s: the witness does not compile" % tag); fails += 1; continue
        got = edges.get(r["id"], {}).get((r["from"], r["to"]))
        if got != r["rank"]:
            print("FAIL: %s: entry_rows[] says %s, the fixture %s" % (tag, got, r["rank"]))
            fails += 1
        with open(os.path.join(out, r["id"] + ".c"), encoding="latin-1") as fh:
            body = fn_body(fh.read(), c_name(r["from"]))
        n = body.count(r["site"]) if body is not None else -1
        if n != int(r["count"]):
            print("FAIL: %s: %r occurs %d times in %s's body, the fixture says %s"
                  % (tag, r["site"], n, c_name(r["from"]), r["count"]))
            fails += 1
    print("fixture: %d witness rows over %d ranks, %d failures"
          % (len(rows), len({r["rank"] for r in rows}), fails))
    return fails


def check_reseed_population(drive, pcrec, tree, work, every):
    blocks, _ = corpus_blocks(pcrec, tree)
    seen, pats = set(), []
    for b in blocks:
        if b["pattern"] not in seen:
            seen.add(b["pattern"]); pats.append(b["pattern"])
    sample = pats[::every]
    cases = [("p%d" % i, "-", p) for i, p in enumerate(sample)]
    out = os.path.join(work, "pop")
    edges, _ = drive_ranks(drive, out, cases)
    if edges is None:
        return 1
    fails, n = 0, {"R2": 0, "R3": 0}
    for cid, es in sorted(edges.items()):
        rk = es.get(("search_run", "prefilter"))
        if rk is None:
            continue
        with open(os.path.join(out, cid + ".c"), encoding="latin-1") as fh:
            body = fn_body(fh.read(), "rx_search_run")
        sites = body.count("rx_prefilter(") if body is not None else 0
        want = "R3" if sites >= 2 else "R2"
        if rk != want or sites < 1:
            print("FAIL: %r: search_run -> prefilter is %s, its body holds %d call sites"
                  % (sample[int(cid[1:])], rk, sites))
            fails += 1
        if rk in n:
            n[rk] += 1
    floors = {"R3": FLOOR_R3 // every // 2, "R2": FLOOR_R2 // every // 2}
    for rk, fl in floors.items():
        if n[rk] < fl:
            print("FAIL: re-seed population: %d %s edges, floor %d" % (n[rk], rk, fl))
            fails += 1
    print("re-seed population: %d patterns, R3 %d, R2 %d, %d failures"
          % (len(sample), n["R3"], n["R2"], fails))
    return fails


def main():
    args = sys.argv[1:]
    every = 1
    if "--every" in args:
        i = args.index("--every"); every = int(args[i + 1]); del args[i:i + 2]
    if len(args) != 4:
        print(__doc__); return 2
    drive, pcrec, tree, work = args
    fails = check_fixture(drive, work)
    fails += check_reseed_population(drive, pcrec, tree, work, every)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
