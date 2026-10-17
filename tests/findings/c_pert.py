#!/usr/bin/env python3
"""tests/findings/c_pert.py — C-PERT, the PERTURBATION check of the
`<PREFIX>_FINDINGS` stamp's honesty ([WINDOW-E1];
docs/design/memfn/window_contract.md rev 3.1 §3.7.7, from the prototype
window_contract_rev31/perturb_proto.py).

    c_pert.py TREE PCREC SCRATCH [--every K] [--jobs N]

The stamp claims "these are the kinds this artifact read". This check tests
the claim from OUTSIDE, by changing the data and watching the bytes: it reads
only the emitted bytes and the stamp text, never pcrec's ask record and never
the kit's `consulted` report, so a reader that reads and does not report
(learnings §3: a control sharing a source with what it controls) cannot hide.

THE METHOD. For each kind with a payload shape (a `find_queries[]` row of
version > 0 in src/core/findings.c; today `byte-rate`), every artifact of the
population is compiled three times, under the SAME analysis name and stop:

    BARE  no `-I`, no `--analysis`
    BASE  `-I SCRATCH/base --analysis default`, a verbatim copy of the store's
          default.rxt
    PERT  `-I SCRATCH/pert --analysis default`, the same file with the kind's
          data PERTURBED by its row of PERTURBERS below

Keeping the name and the stop means only the DATA differs, so the digest is
the only stamp text that can change.

THE VERDICTS, per artifact (STAMP = the two stamp lines, `#define
<P>_FINDINGS` and `.findings =`, masked before a byte compare):
    FAIL null      BASE differs from BARE anywhere, the whole file: the route
                   itself moved something, so no other verdict means anything
    FAIL moved     BASE's stamp omits the kind and the bytes outside STAMP
                   differ between BASE and PERT
    FAIL refusal   BASE's stamp omits the kind and exactly one side refuses
    FAIL stamp     BASE's stamp omits the kind and PERT's lists it
    otherwise legal: consulted-moved (the check's POWER: a dropped stamp item
    on such an artifact turns red), consulted-same, quiet, refused-both.

THE POWER FLOOR. consulted-moved per arm, held to FLOORS (literals measured at
landing, ~80% of the measured count, for the slice this runs at): a
perturbation too weak to move anything cannot read green.

THE STANDING EXCEPTION, F-5 (window_contract.md §3.7.6, D167 add. 3): the
stamp reports the FINAL attempt only, so a compile whose discarded attempt
read the kind stamps "" while its bytes move. Those artifacts are a NAMED
bucket, selected by an INDEPENDENT criterion — the artifact's own
`<P>_ENGINE_SEL` says a ladder retry shipped (`size-cap-retry`) — never by
the findings record; the bucket has an exact-membership pin (F5_PIN) and a
floor, so it cannot grow silently and goes red when F-5 is fixed (then the
pin is re-cut, with the union-over-attempts abi event). The pinned witnesses
are always ADDED to the population, so a slice cannot lose them.

THE KIND TABLE. A kind with a payload shape and no PERTURBERS row FAILS: a new
kind cannot ship unperturbed.
"""
import argparse
import collections
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor

ap = argparse.ArgumentParser()
ap.add_argument("tree")
ap.add_argument("pcrec")
ap.add_argument("scratch")
ap.add_argument("--every", type=int, default=1)
ap.add_argument("--jobs", type=int, default=4)
a = ap.parse_args()
sys.path.insert(0, os.path.join(a.tree, "scripts"))
import emit_sweep as es  # noqa: E402  (the corpus enumeration and one compile)

fails = 0


def ok(m):
    print("PASS: " + m)


def bad(m):
    global fails
    fails += 1
    print("FAIL: " + m)


def perturb_byte_rate(src):
    """The 256 `freq` rows' values reversed by rank (rarest <-> commonest),
    plus one `cpfreq` block serving utf8 (under `-e utf8` pcrec's prior is
    prior-none, so data is ADDED there, not perturbed)."""
    lines = src.split("\n")
    rows = [(i, l) for i, l in enumerate(lines) if re.match(r"\s+row [0-9a-f]{2} \d+$", l)]
    vals = sorted(int(l.split()[2]) for _, l in rows)
    for (i, l), v in zip(sorted(rows, key=lambda r: int(r[1].split()[2])), reversed(vals)):
        lines[i] = l[:len(l) - len(l.lstrip())] + "row %s %d" % (l.split()[1], v)
    return "\n".join(lines).rstrip("\n") + """
    cpfreq
        question q
        reader r
        analyzer authored
        encoding utf8
        serves byte-rate when utf8 via encode-utf8
        row U+0061 50
        row U+0078 1
        row U+00E9 30
        row U+4E2D 20
        provenance
            source authored
            retrieved 2026-10-16
"""


PERTURBERS = {"byte-rate": perturb_byte_rate}
# The F-5 bucket's exact membership (file, pattern): the two corpus witnesses
# whose discarded attempt asked (window_contract.md §3.7.6 F-5).
F5_PIN = {("tests/uprops/size_ladder_prefilter_drop.rxt", r"(\p{Xwd})x", "noreqbyte/utf8"),
          ("tests/utf8/wclass_illformed.rxt", r"x(\p{Xwd})y", "noreqbyte/utf8")}
# Power floors per arm at --every 16 (measured at landing, ~80%); the full
# population (--every 1) is held to the prototype's own counts' ~80%.
FLOORS = {
    # measured 57 / 33 / 27 / 26 / 9 / 11 / 0 / 0 (e1build, 2026-10-17)
    16: {"default/byte": 45, "default/utf8": 26, "noreqbyte/byte": 21, "noreqbyte/utf8": 20,
         "noreq-pf/byte": 7, "noreq-pf/utf8": 8, "noreq-vm/byte": 0, "noreq-vm/utf8": 0},
    # measured 1,009 / 617 / 494 / 484 / 219 / 237 / 0 / 0 over 5,275 distinct
    # (file, pattern) pairs (the prototype's 1,161 / 707 / ... counted rows)
    1: {"default/byte": 807, "default/utf8": 493, "noreqbyte/byte": 395, "noreqbyte/utf8": 387,
        "noreq-pf/byte": 175, "noreq-pf/utf8": 189, "noreq-vm/byte": 0, "noreq-vm/utf8": 0},
}

# the kinds with a payload shape, read off the vocabulary's one home
fsrc = open(os.path.join(a.tree, "src/core/findings.c")).read()
shaped = [t for t, v in re.findall(r'\{\s*"([a-z-]+)",\s*(\d+),\s*PCREC_FIND_UNMEASURED_', fsrc)
          if int(v) > 0]
if not shaped:
    bad("the kind table: no find_queries[] row with a payload shape was found (lost population)")
for t in shaped:
    if t not in PERTURBERS:
        bad(f"the kind table: '{t}' has a payload shape and no perturber row")

B, P = os.path.join(a.scratch, "base"), os.path.join(a.scratch, "pert")
os.makedirs(B, exist_ok=True)
os.makedirs(P, exist_ok=True)
src = open(os.path.join(a.tree, "src/findings/default.rxt")).read()
open(os.path.join(B, "default.rxt"), "w").write(src)
pert = src
for t in shaped:
    if t in PERTURBERS:
        pert = PERTURBERS[t](pert)
open(os.path.join(P, "default.rxt"), "w").write(pert)

arms = [("default", []), ("noreqbyte", ["-fno-req-byte"]),
        ("noreq-pf", ["-fno-req-byte", "-fno-req-run", "-fno-prefilter"]),
        ("noreq-vm", ["--engine=vm", "-fno-req-byte", "-fno-req-run"])]
arms = [(n + "/" + e, (["-e", "utf8"] if e == "utf8" else []) + f)
        for n, f in arms for e in ("byte", "utf8")]
pats = es.enumerate_corpus(a.pcrec, a.tree, 60)
keyed = sorted(set((f, p) for f, _k, p in pats))
pop = [x for i, x in enumerate(keyed) if i % a.every == 0]
pinned = {(f, p.encode()) for f, p, _ in F5_PIN}
pop = sorted(set(pop) | {x for x in keyed if (x[0], x[1]) in pinned})
ST = re.compile(rb'^#define [A-Z0-9_]+_FINDINGS "(.*)"$', re.M)
MASK = re.compile(rb'^(#define [A-Z0-9_]+_FINDINGS .*|    \.findings = .*)$', re.M)
SEL = re.compile(rb'^#define [A-Z0-9_]+_ENGINE_SEL "(.*)"$', re.M)


def lists(stamp, tag):
    return any(it.split(b"=")[0] == tag.encode() for it in stamp.split(b";") if it)


def one(item):
    arm, extra, (f, p) = item
    okn, on, _ = es.compile_stream_c(a.pcrec, p, 60, extra=extra)
    okb, ob, _ = es.compile_stream_c(a.pcrec, p, 60, extra=extra + ["-I", B, "--analysis", "default"])
    okp, op, _ = es.compile_stream_c(a.pcrec, p, 60, extra=extra + ["-I", P, "--analysis", "default"])
    if okn != okb or (okn and on != ob):
        return arm, "FAIL-null", f, p, None
    if not okb:
        return arm, ("refused-both" if not okp else "FAIL-refusal"), f, p, None
    sb = ST.findall(ob)[0]
    sel = (SEL.findall(ob) or [b""])[0]
    omits = [t for t in shaped if not lists(sb, t)]
    if not omits:
        if not okp:
            return arm, "consulted-refusal", f, p, sel
        same = MASK.sub(b"", ob) == MASK.sub(b"", op)
        return arm, ("consulted-same" if same else "consulted-moved"), f, p, sel
    if not okp:
        return arm, "FAIL-refusal", f, p, sel
    sp = ST.findall(op)[0]
    if any(lists(sp, t) for t in omits):
        return arm, "FAIL-stamp", f, p, sel
    if MASK.sub(b"", ob) != MASK.sub(b"", op):
        return arm, "FAIL-moved", f, p, sel
    return arm, "quiet", f, p, sel


items = [(arm, extra, x) for arm, extra in arms for x in pop]
c = collections.Counter()
f5 = set()
with ThreadPoolExecutor(a.jobs) as ex:
    for arm, v, f, p, sel in ex.map(one, items):
        key = (f, p.decode("utf-8", "replace"), arm)
        if v == "FAIL-moved" and sel == b"size-cap-retry":
            f5.add(key)              # F-5's bucket, by the artifact's own stamp
            v = "f5-bucket"
        c[(arm, v)] += 1
        if v.startswith("FAIL"):
            bad(f"C-PERT {arm} {v[5:]}: {f}: {p.decode('utf-8', 'replace')}")
print(f"C-PERT population: {len(pop)} patterns x {len(arms)} arms (every {a.every})")
for (arm, v), n in sorted(c.items()):
    print(f"  {arm}\t{v}\t{n}")
floors = FLOORS.get(a.every)
nfloor = 0
for arm, _ in arms:
    power = c[(arm, "consulted-moved")]
    if floors is None:
        print(f"INFO: {arm} power {power} (no floor at --every {a.every})")
    elif power < floors[arm]:
        nfloor += 1
        bad(f"C-PERT {arm}: power {power} consulted-moved artifact(s), under the floor {floors[arm]}")
nf = sum(1 for (arm, v) in c if v.startswith("FAIL"))
if not nf and not nfloor and floors is not None:
    ok(f"C-PERT no artifact's bytes, refusal or stamp moves with data its stamp omits "
       f"({len(items)} artifacts x 3 compiles; power floors held in all {len(arms)} arms)")
if f5 == F5_PIN:
    ok(f"C-PERT the F-5 bucket (an earlier attempt's ask, stamp \"\") is exactly its "
       f"{len(F5_PIN)} pinned witnesses (window_contract.md §3.7.6; D167 add. 3 fixes it)")
else:
    bad(f"C-PERT the F-5 bucket is {sorted(f5)}, pinned {sorted(F5_PIN)}: re-cut the pin only "
        "with the union-over-attempts event")
sys.exit(1 if fails else 0)
