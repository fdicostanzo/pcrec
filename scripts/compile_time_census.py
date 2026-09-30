#!/usr/bin/env python3
"""scripts/compile_time_census.py -- [OPT-CLOSURE-CTX]/[OPT-RETRY-REUSE]'s
compile-TIME census (lane k67, 2026-09-29).

WHAT IT MEASURES. The CPU time (user+sys, the child's own rusage -- never
wall, which a loaded box inflates) pcrec spends compiling every corpus
`pattern`/`pattern-esc` line under `-p rx --features all -o -`, once per
encoding in --encodings (default `byte,utf8`: most corpus blocks are written
under `byte`, and K67's whole population is the wide-class `utf8` lowering).
With two binaries it runs both on every row, INTERLEAVED per row, so a load
change on the box moves both columns together rather than one.

It also reads two stamps off each emitted artifact, because the retry
ladders are what [OPT-RETRY-REUSE] is about and the artifact is the only
place that says a ladder ran:
  <P>_ENGINE_SEL    `size-cap-retry` = the DFA drop ladder fired
  <P>_UNROLL_K_WHY  anything but `default`/`option`/`denied` = the VM
                    size-term ladder ran
Each row's `ladder` column is the union ("-" when neither fired).

The population comes from the tree's own `--list-source` (scripts/
emit_sweep.py's enumerate_corpus, never a hand list), and a population
under --floor is a FAILURE (K35: a census over nothing reads as "fast").

USAGE
  # one binary
  python3 scripts/compile_time_census.py --bin build/pcrec --out /tmp/a.tsv
  # before/after, the reference built from a revision
  python3 scripts/compile_time_census.py --ref <rev> --bin build/pcrec \\
      --out /tmp/ab.tsv --top 20
  # re-summarise a TSV this script wrote
  python3 scripts/compile_time_census.py --summarise /tmp/ab.tsv --top 20

OUTPUT. A TSV (one row per (pattern, encoding): file, enc, ladder, rc and
cpu seconds per binary, the pattern escaped) and a summary on stderr: total
CPU per binary, the rows over --timeout, the ladder population and its CPU
share, and the worst --top rows by the FIRST binary's time.

EXIT 0 iff the population meets --floor and no row timed out on the LAST
binary (a candidate that hangs is a finding; a reference that hangs is the
defect being measured)."""
import argparse
import concurrent.futures
import os
import re
import subprocess
import sys
import tempfile
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
import emit_sweep as es  # noqa: E402

DEFAULT_TREE = os.path.dirname(SCRIPT_DIR)
LADDER_WHY_QUIET = {"default", "option", "denied", ""}
STAMP_RE = re.compile(rb'^#define [A-Z0-9_]*_(ENGINE_SEL|UNROLL_K_WHY) "([^"]*)"',
                      re.M)


def log(msg):
    print(msg, file=sys.stderr, flush=True)


def one_compile(bin_path, pat, enc, timeout):
    """(rc, cpu_seconds, ladder). rc None = timed out (cpu = the timeout)."""
    argv = [bin_path, "-p", "rx", "--features", "all", "-e", enc, "-o", "-"]
    argv += (["--pattern", pat] if es.pcrec_speaks_pattern_flag(bin_path)
             else ["--", pat])
    with tempfile.TemporaryFile() as out:
        p = subprocess.Popen(argv, stdout=out, stderr=subprocess.DEVNULL)
        t0 = time.monotonic()
        while True:
            pid, status, ru = os.wait4(p.pid, os.WNOHANG)
            if pid:
                break
            if time.monotonic() - t0 > timeout:
                p.kill()
                os.wait4(p.pid, 0)
                return None, float(timeout), "-"
            time.sleep(0.002)
        p.returncode = os.waitstatus_to_exitcode(status)
        cpu = ru.ru_utime + ru.ru_stime
        out.seek(0)
        text = out.read()
    stamps = dict((k.decode(), v.decode()) for k, v in STAMP_RE.findall(text))
    lad = []
    if stamps.get("ENGINE_SEL") == "size-cap-retry":
        lad.append("drop")
    if stamps.get("UNROLL_K_WHY", "") not in LADDER_WHY_QUIET:
        lad.append("unroll")
    return p.returncode, cpu, "+".join(lad) or "-"


def esc(s):
    """The pattern as one printable TSV cell (bytes or str in)."""
    if isinstance(s, str):
        s = s.encode("utf-8", "surrogateescape")
    return s.decode("latin-1").encode("unicode_escape").decode("ascii")


def summarise(rows, names, top):
    for i, nm in enumerate(names):
        tot = sum(r["cpu"][i] for r in rows)
        to = sum(1 for r in rows if r["rc"][i] is None)
        log(f"[census] {nm}: total cpu {tot:.2f} s over {len(rows)} rows, "
            f"{to} timed out")
        lad = [r for r in rows if r["ladder"][i] != "-"]
        ltot = sum(r["cpu"][i] for r in lad)
        log(f"[census] {nm}: ladder population {len(lad)} rows, "
            f"{ltot:.2f} s ({(100.0 * ltot / tot) if tot else 0:.1f}% of total)")
    log(f"[census] worst {top} by {names[0]}:")
    for r in sorted(rows, key=lambda r: -r["cpu"][0])[:top]:
        cols = "  ".join(f"{r['cpu'][i]:8.3f}" for i in range(len(names)))
        log(f"  {cols}  {r['enc']:5s} {r['ladder'][0]:11s} {r['file']}  "
            f"{r.get('pat_esc') or esc(r['pat'])[:60]}")


def read_tsv(path):
    rows, names = [], []
    with open(path, encoding="utf-8", errors="surrogateescape") as f:
        head = f.readline().rstrip("\n").split("\t")
        names = [h[len("cpu_"):] for h in head if h.startswith("cpu_")]
        for line in f:
            v = line.rstrip("\n").split("\t")
            d = dict(zip(head, v))
            rows.append({
                "file": d["file"], "enc": d["enc"], "pat": None,
                "pat_esc": d["pattern"][:60],
                "ladder": [d["ladder_" + n] for n in names],
                "rc": [None if d["rc_" + n] == "timeout" else int(d["rc_" + n])
                       for n in names],
                "cpu": [float(d["cpu_" + n]) for n in names]})
    return rows, names


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--bin", action="append", default=[],
                    help="a pcrec binary (repeatable; order = column order)")
    ap.add_argument("--ref", help="git rev to build as the FIRST binary")
    ap.add_argument("--tree", default=DEFAULT_TREE)
    ap.add_argument("--encodings", default="byte,utf8")
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--floor", type=int, default=3000,
                    help="minimum distinct corpus pattern lines (K35)")
    ap.add_argument("--limit", type=int, default=0,
                    help="smoke: first N pattern lines only (floor waived)")
    ap.add_argument("--out", help="TSV to write")
    ap.add_argument("--summarise", help="re-summarise an existing TSV")
    a = ap.parse_args()

    if a.summarise:
        rows, names = read_tsv(a.summarise)
        summarise(rows, names, a.top)
        return 0

    bins = []
    if a.ref:
        scratch = tempfile.mkdtemp(prefix="ctcensus_")
        b, _ = es.build_from_rev(a.tree, a.ref, scratch, es.resolve_cc(a.tree),
                                 "ref")
        bins.append(("ref", b))
    for i, b in enumerate(a.bin):
        bins.append(("bin%d" % i if len(a.bin) > 1 or not a.ref else "cand",
                     os.path.abspath(b)))
    if not bins:
        ap.error("need --bin and/or --ref")
    names = [n for n, _ in bins]

    corpus = es.enumerate_corpus(bins[-1][1], a.tree, 60)
    seen, pats = set(), []
    for f, _kind, pat in corpus:
        if pat not in seen:
            seen.add(pat)
            pats.append((f, pat))
    log(f"[census] {len(pats)} distinct corpus pattern lines "
        f"(floor {a.floor}), encodings {a.encodings}, binaries {names}")
    if a.limit:
        pats = pats[:a.limit]
    elif len(pats) < a.floor:
        log("[census] FAIL: population under the floor -- the extractor "
            "broke, not the compiler got faster (K35)")
        return 1
    work = [(f, p, e) for f, p in pats for e in a.encodings.split(",")]

    def run_row(item):
        f, p, e = item
        res = [one_compile(b, p, e, a.timeout) for _, b in bins]
        return {"file": f, "pat": p, "enc": e,
                "rc": [r[0] for r in res], "cpu": [r[1] for r in res],
                "ladder": [r[2] for r in res]}

    rows = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        for i, r in enumerate(ex.map(run_row, work)):
            rows.append(r)
            if (i + 1) % 1000 == 0:
                log(f"[census] {i + 1}/{len(work)}")
    rows = [r for r in rows if r]

    if a.out:
        with open(a.out, "w", encoding="utf-8", errors="surrogateescape") as f:
            head = ["file", "enc"]
            for n in names:
                head += ["ladder_" + n, "rc_" + n, "cpu_" + n]
            f.write("\t".join(head + ["pattern"]) + "\n")
            for r in rows:
                v = [r["file"], r["enc"]]
                for i in range(len(names)):
                    v += [r["ladder"][i],
                          "timeout" if r["rc"][i] is None else str(r["rc"][i]),
                          "%.4f" % r["cpu"][i]]
                f.write("\t".join(v + [esc(r["pat"])]) + "\n")
    summarise(rows, names, a.top)
    return 1 if any(r["rc"][-1] is None for r in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
