#!/usr/bin/env python3
"""rpunion's mover census (window_contract.md rev 3.1 §3.7.3a, D167 add. 3).

    census.py TREE REF_PCREC NEW_PCREC [--jobs N] [--every K] [--mask-abi]

Compiles emit_sweep's corpus argv population (`-p rx --features all -o -`)
with both binaries in nine arms (default, -fno-req-byte, the deny-pf arm and
the VM deny arm, each at byte and utf8, plus --engine=vm) and reports every
artifact whose bytes differ, with the differing lines, and every refusal
asymmetry. --mask-abi first rewrites the abi number (78/79) on lines that
name the abi, so the census lists what moves BEYOND the digit; each mover is
tagged by whether only the two knowledge-stamp lines moved, and by whether
the artifact is a compound (`<P>_COMPOUND` not "none") or shipped from a
retry (`<P>_ENGINE_SEL`). Reads emitted bytes only.
"""
import argparse, collections, os, re, sys
from concurrent.futures import ThreadPoolExecutor

ap = argparse.ArgumentParser()
ap.add_argument("tree"); ap.add_argument("ref"); ap.add_argument("new")
ap.add_argument("--jobs", type=int, default=4)
ap.add_argument("--every", type=int, default=1)
ap.add_argument("--mask-abi", action="store_true")
a = ap.parse_args()
sys.path.insert(0, os.path.join(a.tree, "scripts"))
import emit_sweep as es  # noqa: E402

ARMS = [("default", []), ("noreqbyte", ["-fno-req-byte"]),
        ("noreq-pf", ["-fno-req-byte", "-fno-req-run", "-fno-prefilter"]),
        ("noreq-vm", ["--engine=vm", "-fno-req-byte", "-fno-req-run"])]
ARMS = [(n + "/" + e, (["-e", "utf8"] if e == "utf8" else []) + f)
        for n, f in ARMS for e in ("byte", "utf8")] + [("vm/byte", ["--engine=vm"])]
STAMP = re.compile(rb'^(#define [A-Z0-9_]+_FINDINGS .*|    \.findings = .*)$')
SEL = re.compile(rb'^#define [A-Z0-9_]+_ENGINE_SEL "(.*)"$', re.M)
COMP = re.compile(rb'^#define [A-Z0-9_]+_COMPOUND "(.*)"$', re.M)
FIND = re.compile(rb'^#define [A-Z0-9_]+_FINDINGS "(.*)"$', re.M)


def mask(b):
    if not a.mask_abi:
        return b.split(b"\n")
    return [re.sub(rb'\b7[89]\b', b'NN', l) if re.search(rb'abi|ABI', l) else l
            for l in b.split(b"\n")]


pats = es.enumerate_corpus(a.new, a.tree, 60)
keyed = sorted(set((f, p) for f, _k, p in pats))
pop = [x for i, x in enumerate(keyed) if i % a.every == 0]


def one(item):
    arm, extra, (f, p) = item
    okr, orr, _ = es.compile_stream_c(a.ref, p, 60, extra=extra)
    okn, on, _ = es.compile_stream_c(a.new, p, 60, extra=extra)
    if okr != okn:
        return arm, "asymmetric", f, p, None
    if not okr:
        return arm, "refused-both", f, p, None
    lr, ln = mask(orr), mask(on)
    if lr == ln:
        return arm, "same", f, p, None
    import difflib
    d = [l for l in difflib.diff_bytes(difflib.unified_diff, lr, ln, lineterm=b"", n=0)
         if not l.startswith((b"---", b"+++", b"@@"))]
    only_stamp = all(STAMP.match(l[1:]) for l in d)
    sel = (SEL.findall(on) or [b""])[0].decode()
    comp = (COMP.findall(on) or [b""])[0].decode()
    fr = (FIND.findall(orr) or [b"?"])[0].decode()
    fn = (FIND.findall(on) or [b"?"])[0].decode()
    return arm, ("mover-stamp" if only_stamp else "mover-other"), f, p, (sel, comp, fr, fn, d[:8])


items = [(arm, ex, x) for arm, ex in ARMS for x in pop]
c = collections.Counter()
movers = []
with ThreadPoolExecutor(a.jobs) as ex:
    for arm, v, f, p, info in ex.map(one, items):
        c[(arm, v)] += 1
        if v.startswith("mover") or v == "asymmetric":
            movers.append((arm, v, f, p, info))
print(f"census: {len(pop)} patterns x {len(ARMS)} arms (every {a.every}), mask-abi={a.mask_abi}")
for (arm, v), n in sorted(c.items()):
    print(f"  {arm}\t{v}\t{n}")
print(f"movers+asymmetric: {len(movers)}")
for arm, v, f, p, info in movers:
    print(f"MOVER\t{arm}\t{v}\t{f}\t{p.decode('utf-8', 'replace')}")
    if info:
        sel, comp, fr, fn, d = info
        print(f"  ENGINE_SEL={sel} COMPOUND={comp} FINDINGS {fr!r} -> {fn!r}")
        for l in d:
            print("  | " + l.decode("utf-8", "replace")[:200])
print("== census COMPLETE")
