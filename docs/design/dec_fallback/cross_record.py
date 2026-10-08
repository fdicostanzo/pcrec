#!/usr/bin/env python3
"""docs/design/dec_fallback/cross_record.py -- [DEC-FALLBACK] B1's CROSS-RECORD
(dec_fallback.md §4.2 B1): before the fallback trace may serve as B2-B5's
gate, its per-compile fallback sequences must equal two instruments that
share no source with it, on B1's own base, in all five limit variants.

  (a) decfb0's PROBED COPY (`../decision_families/decfb0/build_ref.py`'s
      PATCHES as `probes_b3.py` re-anchors them on B3's one dispatch, the
      attempt histogram's probes; built here by
      `attempt_hist.build_side`), run by decfb0's own `census.py` over its own
      population and argv. From its probes: the row each arrival took
      (`sel1 collapse=`, `rung=`; an arrival with neither is the size term's
      trial catch when its attempt header says `stph=1`), the arrival labels
      (`fail ovf= scr=`) and the state the NEXT attempt starts from (its
      `att=` header: dd, cr, sdr, stph).
  (b) the rev-2 row-reach PROTOTYPE (`reach/build_reach.py`'s probes, run by
      `reach/reach.py` over its population x 14 arms), read with the
      prototype's OWN analysis (`reach/analyse.py`'s parse/labels/t2_row/
      t3_row): the same per-arrival rows, labels and next-attempt state, and
      beyond the brief two more slots the prototype probes: every attempt's
      T2 row and verdict (its `adm` probe through `t2_row`, against the
      trace's `admit` records) and every gate's T3 row (`t3_row` against the
      trace's `gate` records); and the final `attrib` token against the
      artifact's own `RX_ENGINE_SEL` stamp.

The trace side is B1's trace build: (a) compiles decfb0's argv with the
trace compiler `row_reach.py` built (`--trace-dir`, its OUT), (b) reads
`row_reach.py`'s records files for the same variant x arm, so (b) costs no
extra trace compile. Both sides must have run on the same tree.

The state compare: a trace `fallback` record's post-row (dd, cr, sdr) must
equal the next attempt header's, and `restart=1` must be followed by
`stph=0` (the size term reset). An arrival that ends the compile (refuse,
nomem) has no next header and compares rows and labels only. `forcing` is
not in either prototype's label set; a trace arrival carrying it is a
mismatch (none in either population: no corpus compile fails in the force
loop).

usage: cross_record.py --trace-dir RR_OUT --out DIR [--variants a,b]
                       [--arms a,b] [--jobs N] [--stride N] [--skip-a] [--skip-b]
Exit 0 every compile agrees, 1 a mismatch or a K35 floor, 2 bad input.
"""
import argparse, ast, collections, json, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "../../.."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import attempt_hist                      # noqa: E402  build_side, census, build_ref
import row_reach                         # noqa: E402  reach (the prototype's population/argv)
import emit_sweep                        # noqa: E402  VARIANTS
import runpy                             # noqa: E402
# HEAD is post-B3: decfb0's probes re-anchored on the one dispatch (probes_b3.py)
PROBES_B3 = runpy.run_path(os.path.join(HERE, "probes_b3.py"))["PATCHES"]

reach = row_reach.reach
# the prototype's own analysis; analyse.py ends in an unguarded `main()`
_an = {}
exec(compile(open(os.path.join(HERE, "reach/analyse.py")).read().rsplit("\nmain()", 1)[0],
             "reach/analyse.py", "exec"), _an)
STAMP_SEL = re.compile(r'^#define RX_ENGINE_SEL "([^"]*)"', re.M)


def log(m):
    print(m, file=sys.stderr, flush=True)


def kv(s):
    return {a: int(b) for a, b in re.findall(r"(\w+)=(-?\d+)", s)}


def trace_fallbacks(recs):
    """[(row, labels, state-dict)] from the trace's fallback records."""
    out = []
    for slot, route, rowf, _ in recs:
        if slot == "fallback":
            w = rowf.split(" ")
            out.append((w[0], route, kv(" ".join(x for x in w[1:] if not x.startswith("ovw=")))))
    return out


def compare_seq(want, trace, nexthdr):
    """want: [(row, labels)]; nexthdr: [hdr dict or None] per arrival (the
    attempt that followed it). -> None or a difference string."""
    got = [(r, l) for r, l, _ in trace]
    if got != want:
        return f"rows {got} != {want}"
    for i, (r, l, st) in enumerate(trace):
        h = nexthdr[i]
        if h is None:
            continue
        for f in ("dd", "cr", "sdr"):
            if st.get(f) != h.get(f):
                return f"arrival {i} ({r}): post-row {f}={st.get(f)} but the next attempt starts {f}={h.get(f)}"
        if st.get("restart") == 1 and h.get("stph") != 0:
            return f"arrival {i} ({r}): restart=1 but the next attempt has stph={h.get('stph')}"
    return None


# ---- (a) decfb0 -------------------------------------------------------------

def decfb0_seq(probes):
    """decfb0's probes -> ([(row, labels)], [next header or None])."""
    atts, cur = [], None
    for p in probes:
        if p.startswith("att="):
            cur = {"hdr": kv(p), "fail": None, "take": None}
            atts.append(cur)
        elif cur is None:
            continue
        elif p.startswith("fail "):
            cur["fail"] = kv(p)
        elif p.startswith("sel1 "):
            cur["take"] = "sel1-collapse" if kv(p)["collapse"] else "sel1-drop"
        elif p.startswith("rung="):
            cur["take"] = p[5:]
    want, nxt = [], []
    for i, a in enumerate(atts):
        f = a["fail"]
        if f is None:
            continue
        take = a["take"] or ("size-term-trial" if a["hdr"]["stph"] == 1 else "?unprobed")
        lab = "|".join(x for x, b in (("overflow", f["ovf"]), ("size", f["scr"])) if b) or "other"
        want.append((take, lab))
        nxt.append(atts[i + 1]["hdr"] if i + 1 < len(atts) else None)
    return want, nxt


def census_argv(comp, key):
    """decfb0's census.py argv, spelled as it spells it (census.py is a
    script, not a module)."""
    pat, flags, feats, enc, eng = key
    cmd = [comp, "-p", "rx", "--pattern-esc", "-o", "-"]
    if "i" in flags: cmd.append("-i")
    if "u" in flags: cmd.append("--ucp")
    if feats: cmd += ["--features", feats]
    if enc: cmd += ["-e", enc]
    if eng: cmd += ["--engine=" + eng]
    return cmd + ["--pattern", "\"" + pat.replace("\"", "\\\"") + "\""]


def trace_compile(cmd):
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=120)
    except subprocess.TimeoutExpired:
        return "TIMEOUT", [], b""
    recs = [tuple(ln.split("\t")[1:5]) for ln in r.stderr.decode("utf-8", "replace").split("\n")
            if ln.startswith("CANDTRACE\t") and ln.split("\t")[1] in row_reach.SLOTS]
    return ("ok" if r.returncode == 0 else "refused"), recs, r.stdout


def run_a(variants, trace_dir, out, jobs, stride):
    side = os.path.join(out, "decfb0")
    log("[cross_record] (a) building decfb0's probed copies of HEAD ...")
    tree, probe = attempt_hist.build_side("HEAD", side, PROBES_B3, variants, jobs)
    ok, lines = True, []
    for v in variants:
        tbin = os.path.join(trace_dir, f"src_ref-trace-{v}", "build", "pcrec")
        if not os.path.exists(tbin):
            sys.exit(f"cross_record: no trace compiler {tbin} (run row_reach.py first)")
        log(f"[cross_record] (a) {v}: decfb0 census ...")
        rows = attempt_hist.census(tree, probe, v, stride)
        keys = sorted(rows)
        log(f"[cross_record] (a) {v}: {len(keys)} trace compiles ...")
        with ThreadPoolExecutor(max_workers=jobs) as ex:
            res = list(ex.map(lambda k: trace_compile(census_argv(tbin, ast.literal_eval(k))), keys))
        n = diff = arrivals = multi = 0
        for k, (st, recs, _) in zip(keys, res):
            dst, probes = rows[k]
            want, nxt = decfb0_seq(probes)
            tr = trace_fallbacks(recs)
            n += 1; arrivals += len(tr); multi += len(tr) > 0
            why = (f"status {dst} vs trace {st}" if dst != st else compare_seq(want, tr, nxt))
            if why:
                diff += 1
                if diff <= 5:
                    lines.append(f"(a) {v} {k[:100]}: {why}")
        good = diff == 0 and (stride > 1 or n >= attempt_hist.POPULATION_FLOOR) and multi > 0
        print(f"(a) decfb0 {v}: {n} compiles, {arrivals} arrivals over {multi} compiles, "
              f"{diff} differ -> {'AGREE' if good else 'FAIL'}")
        ok = ok and good
    return ok, lines


# ---- (b) the rev-2 prototype ------------------------------------------------

def run_b(variants, arms, trace_dir, out, jobs, stride):
    proto = os.path.join(out, "proto")
    log("[cross_record] (b) building the prototype's probed compilers ...")
    subprocess.check_call([sys.executable, os.path.join(HERE, "reach/build_reach.py"), proto]
                          + variants, stdout=subprocess.DEVNULL)
    ok, lines = True, []
    tot = collections.Counter()
    for v in variants:
        for arm in arms:
            if v == "lowthr" and arm not in row_reach.LOWTHR_ARMS:
                continue
            tpath = os.path.join(trace_dir, f"records_ref_{v}_{arm}.jsonl")
            if not os.path.exists(tpath):
                sys.exit(f"cross_record: no trace records {tpath} (run row_reach.py first)")
            log(f"[cross_record] (b) {v} {arm}: prototype ...")
            subprocess.check_call([sys.executable, os.path.join(HERE, "reach/reach.py"), ROOT,
                                   proto, v, arm, "--jobs", str(jobs), "--stride", str(stride)], stdout=subprocess.DEVNULL)
            P = {(r["src"], tuple(r["key"])): r
                 for r in map(json.loads, open(os.path.join(proto, f"reach_{v}_{arm}.jsonl")))}
            T = {(r["src"], tuple(r["key"])): r for r in map(json.loads, open(tpath))}
            c = collections.Counter()
            if set(P) != set(T):
                c["population"] += 1
            for k in sorted(set(P) & set(T)):
                p, t = P[k], T[k]
                c["compiles"] += 1
                why = None
                if p["status"] != t["status"]:
                    why = f"status {p['status']} vs trace {t['status']}"
                else:
                    atts = _an["parse"](p["pr"])
                    want, nxt = [], []
                    for i, a in enumerate(atts):
                        if a["fail"] is None:
                            continue
                        lab = _an["labels"](a["fail"])
                        if a["fail"]["forcing"]:
                            lab = "forcing" + ("|" + lab if lab != "other" else "")
                        want.append((a["take"] or "?unprobed", lab))
                        nxt.append(atts[i + 1]["hdr"] if i + 1 < len(atts) else None)
                    recs = [tuple(x) for x in t["rec"]]
                    tr = trace_fallbacks(recs)
                    c["arrivals"] += len(tr)
                    why = compare_seq(want, tr, nxt)
                    # admit: one T2 row + verdict per attempt that reached it
                    if not why:
                        pa = [(_an["t2_row"](a["adm"], 0)[0], a["adm"]["pf"]) for a in atts
                              if a["adm"] is not None]
                        ta = []
                        for slot, route, rowf, _ in recs:
                            if slot == "admit":
                                w = rowf.split(" ")
                                r_ = w[0]
                                if r_ == "default":
                                    r_ = "default-on" if "pf=1" in w else "default-off"
                                ta.append((r_, int(w[1].split("=")[1])))
                        c["admits"] += len(ta)
                        if pa != ta:
                            why = f"admit {ta} != prototype t2_row {pa}"
                    if not why:
                        pg = [_an["t3_row"](a["gate"], a["hdr"]["cr"], arm == "pf")[0]
                              for a in atts if a["gate"] is not None]
                        tg = []
                        for slot, route, rowf, _ in recs:
                            if slot == "gate":
                                w = rowf.split(" ")
                                tg.append("rung-" + w[1].split("=")[1] if w[0] == "rung" else w[0])
                        c["gates"] += len(tg)
                        if pg != tg:
                            why = f"gate {tg} != prototype t3_row {pg}"
                    if not why and p["status"] == "ok" and p["st"].get("ENGINE_SEL"):
                        at = [rowf.split(" ")[0] for slot, _, rowf, _ in recs if slot == "attrib"]
                        c["attribs"] += 1
                        if not at or at[-1] != p["st"]["ENGINE_SEL"]:
                            why = f"final attrib {at[-1:] } != stamp {p['st']['ENGINE_SEL']}"
                if why:
                    c["differ"] += 1
                    if c["differ"] <= 3:
                        lines.append(f"(b) {v} {arm} {k[0]} {k[1][0][:80]!r}: {why}")
            tot.update(c)
            good = not c["differ"] and not c["population"]
            ok = ok and good
            print(f"(b) prototype {v} {arm}: {c['compiles']} compiles, {c['arrivals']} arrivals, "
                  f"{c['admits']} admits, {c['gates']} gates, {c['attribs']} final stamps, "
                  f"{c['differ']} differ{' POPULATION DIFFERS' if c['population'] else ''}"
                  f" -> {'AGREE' if good else 'FAIL'}")
    if tot["arrivals"] == 0 or tot["admits"] == 0 or tot["gates"] == 0:
        ok = False
        lines.append("K35: (b) compared no arrival / admit / gate at all")
    print(f"(b) total: " + " ".join(f"{k}={tot[k]}" for k in sorted(tot)))
    return ok, lines


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--trace-dir", required=True)
    ap.add_argument("--out", default=os.path.join(ROOT, "build/cross_record"))
    ap.add_argument("--variants", default=",".join(emit_sweep.VARIANTS))
    ap.add_argument("--arms", default=",".join(reach.ARMS))
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--stride", type=int, default=1, help="a SAMPLE (must match row_reach.py's; floors not applied)")
    ap.add_argument("--skip-a", action="store_true")
    ap.add_argument("--skip-b", action="store_true")
    a = ap.parse_args()
    variants, arms = a.variants.split(","), a.arms.split(",")
    os.makedirs(a.out, exist_ok=True)
    ok, lines = True, []
    if not a.skip_a:
        o, l = run_a(variants, os.path.abspath(a.trace_dir), a.out, a.jobs, a.stride); ok &= o; lines += l
    if not a.skip_b:
        o, l = run_b(variants, arms, os.path.abspath(a.trace_dir), a.out, a.jobs, a.stride); ok &= o; lines += l
    for ln in lines:
        print("  " + ln)
    print("CROSS-RECORD: " + ("AGREE" if ok else "FAIL"))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
