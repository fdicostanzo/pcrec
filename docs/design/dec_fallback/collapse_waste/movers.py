#!/usr/bin/env python3
"""docs/design/dec_fallback/collapse_waste/movers.py -- the MOVER MANIFEST of
lane decattr ([DEC-VAR-ATTRIB] + [DEC-COLLAPSE-WASTE], 2026-10-09).

Compiles emit_sweep's corpus population (every `pattern`/`pattern-esc` line
of tests/**/*.rxt, decoded, `--features all`, `-o -`) with compiler A and
compiler B on the streams the two rows can move, and CLASSIFIES every changed
line against the declared mover shapes:

  c       `.c` at the default engine (base byte, and `-e utf8`)
          esel:<old>-><new>   the <P>_ENGINE_SEL line          (F1)
          pfwhy:<old>-><new>  the <P>_VM_PREFILTER_WHY line    (waste, form (a))
  ir      `--emit-ir` at the default engine, arms "", -fno-prefilter,
          -fno-prefilter-collapse (`-fprefilter` cannot reach a moved row)
          tok:<old>-><new>    the `prefilter` row's value      (F1/F-B1/§4.5)
  irvm    `--emit-ir --engine=vm`, the same `prefilter` row
  facts   `--emit-facts=byte,utf8`
          used:<fact>:<old>-><new>  a fact's `used` column     (the up-front ask)
          stamp:<name>:<old>-><new> the listing's copy of a stamp above

A changed line outside those shapes is UNDECLARED and fails the run (exit 1).
Writes the TSV of every mover to stdout (kind, stream, arm, file, pattern,
class) and a summary to stderr. A is the parent, B the child; the abi digits
are NOT normalized, so compare two binaries of ONE abi (the lane compares
3b43b33d against d4c2b5cb, both abi 68).

usage: movers.py BIN_A BIN_B [--jobs N] [--streams c,ir,irvm,facts]
                 [--bases byte,utf8]
"""
import argparse, collections, os, re, sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "../../../.."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import emit_sweep as es    # noqa: E402  the population and the argv builders

DEF = re.compile(rb'^#define RX_(ENGINE_SEL|VM_PREFILTER_WHY) "(.*)"$')


def lines(b):
    return b.splitlines() if b else []


def c_class(a, b):
    la, lb = lines(a), lines(b)
    if len(la) != len(lb):
        return None
    out = []
    for x, y in zip(la, lb):
        if x == y:
            continue
        mx, my = DEF.match(x), DEF.match(y)
        if not (mx and my and mx.group(1) == my.group(1)):
            return None
        tag = "esel" if mx.group(1) == b"ENGINE_SEL" else "pfwhy"
        out.append(f"{tag}:{mx.group(2).decode()}->{my.group(2).decode()}")
    return out


def ir_tok(b):
    for ln in lines(b):
        f = ln.split(b"\t")
        if len(f) >= 2 and f[0] == b"prefilter":
            return f[1].decode()
    return None


def ir_class(a, b):
    la, lb = lines(a), lines(b)
    if len(la) != len(lb):
        return None
    for x, y in zip(la, lb):
        if x != y and not (x.startswith(b"prefilter\t") and y.startswith(b"prefilter\t")):
            return None
    return [f"tok:{ir_tok(a)}->{ir_tok(b)}"]


def facts_class(a, b):
    la, lb = lines(a), lines(b)
    if len(la) != len(lb):
        return None
    out = []
    for x, y in zip(la, lb):
        if x == y:
            continue
        fx, fy = x.split(b"\t"), y.split(b"\t")
        if (len(fx) == len(fy) == 3 and fx[:2] == fy[:2]
                and fx[1] in (b"RX_ENGINE_SEL", b"RX_VM_PREFILTER_WHY")):
            out.append(f"stamp:{fx[1].decode()[3:]}:{fx[2].decode()}->{fy[2].decode()}")
            continue
        if len(fx) != len(fy) or len(fx) < 6:
            return None
        diff = [i for i in range(len(fx)) if fx[i] != fy[i]]
        if diff != [5]:         # the `used` column only
            return None
        out.append(f"used:{fx[1].decode()}:{fx[5].decode()}->{fy[5].decode()}")
    return out


def task(args):
    stream, arm, base, rec, a_bin, b_bin, timeout = args
    f, kind, pat = rec
    extra = ([("-e", "utf8")] if base == "utf8" else [])
    extra = [x for t in extra for x in t] + ([arm] if arm else [])
    if stream == "c":
        ra = es.compile_stream_c(a_bin, pat, timeout, extra=extra, want_err=True)
        rb = es.compile_stream_c(b_bin, pat, timeout, extra=extra, want_err=True)
        if not ra[0] and not rb[0]:
            return None
        if ra[0] != rb[0]:
            return (stream, arm or base, f, pat, "ASYMMETRIC")
        if ra[1] == rb[1]:
            return None
        cls = c_class(ra[1], rb[1])
    elif stream in ("ir", "irvm"):
        if stream == "ir":
            ra = es.compile_stream_ir_auto(a_bin, pat, timeout, extra=extra)
            rb = es.compile_stream_ir_auto(b_bin, pat, timeout, extra=extra)
        else:
            ra = es.compile_stream_ir(a_bin, pat, timeout, extra=extra)
            rb = es.compile_stream_ir(b_bin, pat, timeout, extra=extra)
        if ra[1] == rb[1]:
            return None
        cls = ir_class(ra[1], rb[1]) if (ra[1] and rb[1]) else None
    else:
        ra = es.compile_stream_facts(a_bin, pat, timeout)
        rb = es.compile_stream_facts(b_bin, pat, timeout)
        if ra[1] == rb[1]:
            return None
        cls = facts_class(ra[1], rb[1]) if (ra[1] and rb[1]) else None
    return (stream, arm or base, f, pat, " ; ".join(cls) if cls else "UNDECLARED")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bin_a"); ap.add_argument("bin_b")
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--streams", default="c,ir,irvm,facts")
    ap.add_argument("--bases", default="byte,utf8")
    ap.add_argument("--timeout", type=int, default=60)
    a = ap.parse_args()
    pats = es.enumerate_corpus(a.bin_b, ROOT, a.timeout)
    seen, pop = set(), []
    for rec in pats:
        if rec[2] not in seen:
            seen.add(rec[2]); pop.append(rec)
    jobs = []
    for s in a.streams.split(","):
        if s == "c":
            plan = [("c", "", b) for b in a.bases.split(",")]
        elif s == "ir":
            plan = [("ir", arm, "byte") for arm in ("", "-fno-prefilter", "-fno-prefilter-collapse")] \
                 + [("ir", "", "utf8")]
        elif s == "irvm":
            plan = [("irvm", "", "byte")]
        else:
            plan = [("facts", "", "byte")]
        for st, arm, base in plan:
            jobs += [(st, arm, base, rec, a.bin_a, a.bin_b, a.timeout) for rec in pop]
    with ThreadPoolExecutor(a.jobs) as ex:
        res = [r for r in ex.map(task, jobs) if r]
    tally = collections.Counter()
    bad = 0
    print("stream\tcell\tfile\tpattern\tclass")
    for st, cell, f, pat, cls in sorted(res, key=lambda r: r[:3]):
        print(f"{st}\t{cell}\t{f}\t{es.encode_escape(pat if isinstance(pat, bytes) else pat.encode("utf-8", "surrogateescape"))}\t{cls}")
        for c in cls.split(" ; "):
            tally[(st, cell, c)] += 1
        bad += cls in ("UNDECLARED", "ASYMMETRIC")
    print(f"population {len(pop)} distinct patterns; movers {len(res)}", file=sys.stderr)
    for k, n in sorted(tally.items()):
        print(f"  {k[0]:5} {k[1]:24} {n:5}  {k[2]}", file=sys.stderr)
    print("MOVERS: " + ("ALL DECLARED SHAPES" if not bad else f"{bad} UNDECLARED/ASYMMETRIC"),
          file=sys.stderr)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
