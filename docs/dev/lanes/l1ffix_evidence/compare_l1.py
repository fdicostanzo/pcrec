#!/usr/bin/env python3
"""span_arms unit L1's TWO-SIDED COMPARE at the feature's gate (span_arms.md
rev 3.2 §14.4 "Common to every unit" (1), L1 "Census (first)", RULING-4).

REVISED by lane l1ffix (review r55 H, the landing check under D191 add. 1 (b)),
from l1feat_evidence/compare_l1.py: (1) it JUDGES `run_pin` and
`req_landmark_maxoff` (a route-level mover is a mover, r55 lesson 2): a
pattern whose BASE pin is lost or shortened is a PIN-LOST disagreement
(r55 B's landing condition: none), a raised landmark offset is a
LANDMARK-LOOSER one; pin gains and tighter landmarks are listed for
explain_l1.py; (2) a text with a positive lookaround in ANOTHER spelling
(`(?*`, `(*pla:`, the alpha names) is labelled so, not "outside the model's
scope" (r55 TABLE-7: 34 such rows).

the OBSERVED movers (the base build's facts against the feature build's, the
facts stream's own vocabulary) against the census MODEL's predicted movers
(l1build_evidence/census_l1.py, reused unedited), in both directions.

  OBSERVED  every distinct pattern text of the population (every `.rxt` under
            TREE/tests and the bench file, census_l1.py's `population`), each
            compiled by both builds with `--emit-facts=byte,utf8` (the facts
            stream's encodings, scripts/emit_sweep.py stream 6); a fact moved
            where its status, value or why differs. ALL texts, not only those
            with a positive lookaround: the empty-class leaf (W-D8) and the TOP
            set step reach any pattern, so a mover outside the model's scope
            must show up here, not be assumed away.
  MODEL     census_l1.py's `one()` on every text it reads (byte only, its one
            alphabet): `dead`, and the run/set/byte/set_maxoff its spelling
            predicts.

The compare, on the BYTE encoding (the model's): a pattern is a model mover iff
it is an observed mover, and where both, the same facts moved and (for a
narrowing) the observed values are the model's predicted ones. Every
disagreement is listed with its pattern. utf8-only movers are listed apart
(the model reads no utf8). Also writes OUT/observed.tsv in
sae1_evidence/ident_check.py's census format (src, escaped pattern, moved
facts), so the identity gate can read the observed movers.

usage: compare_l1.py BASE_PCREC WORK_PCREC TREE BENCH_FILE OUT_DIR [--jobs N]
rc: 0 when the compare has no disagreement, 1 otherwise.
"""
import concurrent.futures as cf
import importlib.util
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "census_l1", os.path.join(HERE, "../l1build_evidence/census_l1.py"))
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)

WATCH = ("req_whole_run", "req_set", "req_set_maxoff", "req_byte")
ROUTE = ("run_pin", "req_landmark_maxoff")
# every positive-lookaround spelling the parser takes, rewritten to the two
# the model reads (atomicity moves no byte the walk reads)
REWRITE = [(b"(*non_atomic_positive_lookahead:", b"(?="), (b"(*non_atomic_positive_lookbehind:", b"(?<="),
           (b"(*positive_lookahead:", b"(?="), (b"(*positive_lookbehind:", b"(?<="),
           (b"(*napla:", b"(?="), (b"(*naplb:", b"(?<="), (b"(*pla:", b"(?="), (b"(*plb:", b"(?<="),
           (b"(?<*", b"(?<="), (b"(?*", b"(?=")]


def rewrite(p):
    for o, n in REWRITE:
        p = p.replace(o, n)
    return p


def pin_len(v):
    """The pinned stretch's length from a `run_pin` value (`o:at+len`, or a
    bare offset when the stretch is the whole window); 0 for none."""
    if v in ("", "none", None):
        return 0
    return int(v.split("+")[1]) if "+" in v else 10 ** 6


def offnum(v):
    return 1 << 62 if v == "unbounded" else int(v) if v.lstrip("-").isdigit() else None


def route_verdicts(rec):
    """r55 H: the byte `run_pin` and `req_landmark_maxoff` of BASE vs SUBJECT,
    as (kind, text) pairs: PIN-LOST / LANDMARK-LOOSER are disagreements,
    PIN-GAIN / PIN-MOVED / LANDMARK-TIGHTER are movers to explain."""
    a, b = rec.get("base"), rec.get("work")
    out = []
    if not a or not b:
        return out
    pa = a.get(("byte", "run_pin"), ("", "none", ""))[1]
    pb = b.get(("byte", "run_pin"), ("", "none", ""))[1]
    if pa != pb:
        la, lb = pin_len(pa), pin_len(pb)
        kind = "PIN-LOST" if lb < la else "PIN-GAIN" if la == 0 else "PIN-MOVED"
        out.append((kind, "run_pin base [%s] subject [%s]" % (pa, pb)))
    ma = a.get(("byte", "req_landmark_maxoff"), ("", "", ""))[1]
    mb = b.get(("byte", "req_landmark_maxoff"), ("", "", ""))[1]
    if ma != mb:
        x, y = offnum(ma), offnum(mb)
        kind = "LANDMARK-LOOSER" if x is None or y is None or y > x else "LANDMARK-TIGHTER"
        out.append((kind, "req_landmark_maxoff base [%s] subject [%s]" % (ma, mb)))
    return out


def listing(pcrec, pat):
    try:
        r = subprocess.run([pcrec, "--features", "all", "--emit-facts=byte,utf8",
                            "--pattern", pat], capture_output=True, timeout=C.TIMEOUT)
    except subprocess.TimeoutExpired:
        return None
    if r.returncode != 0:
        return None
    rows = {}; sec = None
    for line in r.stdout.decode("utf-8", "surrogateescape").splitlines():
        if line.startswith("#section "):
            sec = line.split()[1]; continue
        if line.startswith("#") or sec != "facts":
            continue
        x = line.split("\t")
        rows[(x[0], x[1])] = (x[4], x[6], x[7])   # status, value, why
    return rows


def observe(args):
    base, work, src, pat = args
    a, b = listing(base, pat), listing(work, pat)
    rec = {"src": src, "pat": pat}
    if a is None or b is None:
        rec["asym"] = (a is None) != (b is None)
        rec["moved"] = {}
        return rec
    moved = {}
    for k in sorted(set(a) | set(b)):
        if a.get(k) != b.get(k):
            moved.setdefault(k[0], []).append(k[1])
    rec["moved"] = moved
    rec["work"] = b
    rec["base"] = a
    return rec


def obs_byte_set(rec):
    """The observed byte movers in the model's vocabulary."""
    out = set()
    b = rec.get("work"); a = rec.get("base")
    if not b:
        return out
    if b.get(("byte", "req_whole_run"), ("", "", ""))[2] == "dead" and \
       a.get(("byte", "req_whole_run"), ("", "", ""))[2] != "dead":
        out.add("dead")
    for f in WATCH:
        if a.get(("byte", f), (None,))[1:2] != b.get(("byte", f), (None,))[1:2]:
            out.add(f)
    return out


def main():
    a = sys.argv[1:]
    jobs = 8
    if "--jobs" in a:
        k = a.index("--jobs"); jobs = int(a[k + 1]); del a[k:k + 2]
    base, work, tree, bench, out = a
    t0 = time.time()
    os.makedirs(out, exist_ok=True)
    pop = C.population(base, tree, bench)
    seen = {}
    for src, pat in pop:
        seen.setdefault(pat, src)
    with cf.ThreadPoolExecutor(jobs) as ex:
        obs = list(ex.map(observe, [(base, work, s, p) for p, s in seen.items()]))
        mod = list(ex.map(C.one, [(base, s, p, True) for p, s in seen.items() if C.has_pos_look(p)]))
    model = {r["pat"]: r for r in mod}
    lines = []; bad = 0
    asym = [r for r in obs if r.get("asym")]
    for r in asym:
        lines.append("  ASYMMETRIC %s %s" % (r["src"], C.esc(r["pat"]))); bad += 1
    obs_mov = {r["pat"]: r for r in obs if r["moved"]}
    byte_mov = {p: r for p, r in obs_mov.items() if "byte" in r["moved"]}
    utf8_only = {p: r for p, r in obs_mov.items() if "byte" not in r["moved"]}
    mod_mov = {p: r for p, r in model.items() if r.get("moved")}
    # (1) model mover, not observed
    for p in sorted(set(mod_mov) - set(byte_mov)):
        r = mod_mov[p]
        lines.append("  MODEL-ONLY %s %s model=%s" % (r["src"], C.esc(p), ",".join(r["moved"]))); bad += 1
    # (2) observed, not a model mover
    for p in sorted(set(byte_mov) - set(mod_mov)):
        r = byte_mov[p]; m = model.get(p)
        why = "abstained: " + m["abstain"] if m and "abstain" in m else \
              "a positive lookaround in another spelling (the model reads (?= and (?<= only)" \
              if not C.has_pos_look(p) and C.has_pos_look(rewrite(p)) else \
              "outside the model's scope (no positive lookaround)" if not C.has_pos_look(p) else \
              "the model predicts no move"
        lines.append("  OBSERVED-ONLY %s %s observed=%s byte-facts=%s (%s)" % (
            r["src"], C.esc(p), ",".join(sorted(obs_byte_set(r))), ",".join(r["moved"]["byte"]), why)); bad += 1
    # (3) both: the same facts, the same values
    agree = 0
    for p in sorted(set(byte_mov) & set(mod_mov)):
        r = byte_mov[p]; m = mod_mov[p]
        ob = obs_byte_set(r); mb = set(m["moved"])
        vals = []
        if m.get("pred"):
            w = r["work"]
            for f, mf in (("req_whole_run", "req_whole_run"), ("req_set", "req_set_step"),
                          ("req_byte", "req_byte"), ("req_set_maxoff", "req_set_maxoff")):
                got = w.get(("byte", f), ("", "", ""))[1]
                want = m["pred"][mf]
                if f == "req_set":
                    same = C.set_members(got) == C.set_members(want)
                elif f == "req_set_maxoff" and "req_set_maxoff" not in mb:
                    continue
                else:
                    same = got == want
                if not same:
                    vals.append("%s observed [%s] model [%s]" % (f, got, want))
        if ob != mb or vals:
            lines.append("  DIFFER %s %s observed=%s model=%s %s" % (
                r["src"], C.esc(p), ",".join(sorted(ob)), ",".join(sorted(mb)), "; ".join(vals))); bad += 1
        else:
            agree += 1
    # (4) r55 H: the route facts, judged on every observed mover
    route = {"PIN-LOST": 0, "PIN-GAIN": 0, "PIN-MOVED": 0, "LANDMARK-LOOSER": 0, "LANDMARK-TIGHTER": 0}
    for p in sorted(obs_mov):
        for kind, text in route_verdicts(obs_mov[p]):
            route[kind] += 1
            lines.append("  %s %s %s %s" % (kind, obs_mov[p]["src"], C.esc(p), text))
            if kind in ("PIN-LOST", "LANDMARK-LOOSER"):
                bad += 1
    for p in sorted(utf8_only):
        r = utf8_only[p]
        lines.append("  UTF8-ONLY %s %s utf8-facts=%s" % (r["src"], C.esc(p), ",".join(r["moved"]["utf8"])))
    with open(os.path.join(out, "observed.tsv"), "w") as h:
        h.write("#src\tpattern\tmoved_facts\n")
        for p, r in sorted(obs_mov.items(), key=lambda kv: kv[1]["src"]):
            h.write("%s\t%s\t%s\n" % (r["src"], C.esc(p), ";".join(
                "%s:%s" % (e, ",".join(fs)) for e, fs in sorted(r["moved"].items()))))
    def where(ps):
        return "%d (corpus %d, bench %d)" % (len(ps), sum(1 for p in ps if seen[p].startswith("corpus:")),
                                             sum(1 for p in ps if seen[p].startswith("bench:")))
    head = [
        "population: %d rows, %d distinct texts; model read %d positive-lookaround texts (%d abstained)"
        % (len(pop), len(seen), sum(1 for r in mod if "abstain" not in r), sum(1 for r in mod if "abstain" in r)),
        "OBSERVED movers (any encoding): %s; byte: %s; utf8 only: %s" % (where(obs_mov), where(byte_mov), where(utf8_only)),
        "MODEL movers: %s" % where(mod_mov),
        "both, agreeing (facts and values): %d" % agree,
        "route facts (byte): " + ", ".join("%s %d" % kv for kv in route.items()),
        "observed facts moved, byte, by fact: " + ", ".join(
            "%s %d" % (f, sum(1 for r in byte_mov.values() if f in obs_byte_set(r))) for f in ("dead",) + WATCH),
    ]
    lines = head + lines
    lines.append("== compare COMPLETE: %d disagreements, %.0f s" % (bad, time.time() - t0))
    with open(os.path.join(out, "compare.txt"), "w") as h:
        h.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
