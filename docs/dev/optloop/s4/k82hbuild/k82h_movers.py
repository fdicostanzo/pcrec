#!/usr/bin/env python3
"""[K82] (B) THE HANDOFF -- the MOVER MANIFEST and the DENY ARM
(docs/design/litscan_k82h.md §4.1).

  BASE=<pcrec at abi 60> NEW=<pcrec with the handoff> SCR=<scratch> \\
      [ABI_FROM=60 ABI_TO=61] [PROCS=4] python3 k82h_movers.py

Populations: `../c3_movers.py`'s own (imported): every pcrec-bench export x
{auto, vm} x {caps, nocaps}, and every corpus `pattern` row as written x
{auto, vm, --no-captures, --engine=vm -fprefilter} (the last two are the r1
panel's C-C9 arms: the forced hybrid is where the hybrid route's population
lives).

NORMALIZATION, by name and nothing else: BASE's abi digit ABI_FROM -> ABI_TO
at its sites, and NEW's one `#define RX_REQ_HANDOFF "<v>"` line removed (its
value recorded): Frank's Q3 ruling puts that line on EVERY artifact, so a
non-mover differs from BASE in exactly those two places. Then BYTE FOR BYTE.

  NEW  vs BASE  the PROGRAM moved <=> a PREDICTION recomputed here in Python
                from NEW's `--emit-facts` rows and stamps, never from the C:
                REQ_WHY "emitted", REQ_RUN not "none", a DFA scan in front
                (RX_ENGINE "dfa", or RX_VM_PREFILTER "hybrid"), req_run_maxoff
                finite, RX_VM_PREFILTER_LANG not "count-collapsed" (Q10), and
                not (d'): a hybrid whose prefilter carries a `\\G` dispatch and
                whose kinds hold neither atomic nor lookaround (its
                prefilter-window ceiling). On a predicted mover REQ_HANDOFF
                must equal req_run_maxoff; elsewhere it must read "none".
                Off-diagonal cells are failures.
  DENY vs BASE  NEW + -fno-req-handoff: IDENTICAL on every artifact after the
                same normalization, with DENY's REQ_HANDOFF reading "none"
                (bit 46 is in `strategy_denials`, so rx_info.flags does not
                move either).
  THE FACT      NEW's `req_whole_run` == BASE's on every artifact: the offset
                is an annotation and must not move the run CHOICE.

WHAT THIS IS NOT (litscan_k82h.md §4.1, [r1 C-C4]): the prediction and the
stamp both read `rb_walk`'s K, so this checks the plumbing (fact -> selection
-> text), never the fact. The fact's checks share no source with the walk:
the hand K pin table (tests/codegen/run_prechecks.sh §5.12), k82h_oracle.py
(invariant F against libpcre2) and the K-1 plant (k82h_answers.py).
"""
import collections, json, os, re, shutil, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import c3_movers as c3   # noqa: E402  (reads BASE/NEW/SCR itself)

BASE, NEW, SCR = c3.BASE, c3.NEW, c3.SCR
ABI_FROM, ABI_TO = os.environ.get("ABI_FROM", "60"), os.environ.get("ABI_TO", "61")
c3.CORPUS_CFG = {"auto": [], "vm": ["--engine=vm"], "nocaps": ["--no-captures"],
                 "vm-pf": ["--engine=vm", "-fprefilter"]}
HANDOFF_RE = re.compile(r'^#define RX_REQ_HANDOFF "([^"]*)"\n', re.M)


def norm_base(t):
    if ABI_FROM == ABI_TO:
        return t
    t = re.sub(r'(abi )%s\b' % ABI_FROM, r'\g<1>' + ABI_TO, t)
    t = re.sub(r'(PCREC_RX_ABI_H(?: \+ 0\))? (?:!= )?)%s\b' % ABI_FROM, r'\g<1>' + ABI_TO, t)
    return re.sub(r'(\.abi *= *)%s\b' % ABI_FROM, r'\g<1>' + ABI_TO, t)


SIZEWHY_RE = re.compile(r'^(#define RX_\w+_WHY "size cap retry, [^"]*?)(\d+)( > \d+")$', re.M)


def strip_handoff(t):
    """NEW's text with its REQ_HANDOFF line removed, the stamp's value, and
    -- the one other place the line shows -- each size-cap retry reason's
    emitted-byte count lowered by the line's own length (a `_WHY` stamp
    that quotes the attempted artifact's size counts that line too)."""
    m = HANDOFF_RE.search(t)
    if not m:
        return t, None
    n = len(m.group(0))
    t = SIZEWHY_RE.sub(lambda w: w.group(1) + str(int(w.group(2)) - n) + w.group(3), t)
    return HANDOFF_RE.sub("", t, count=1), m.group(1)


def facts(binp, pat, args):
    """--emit-facts: (fact rows {name: value}, decision stamps {name: value})."""
    try:
        r = subprocess.run([binp.encode(), b"--features", b"all", b"--emit-facts",
                            *[a.encode() for a in args], b"--pattern", pat],
                           capture_output=True, timeout=300)
    except subprocess.TimeoutExpired:
        return None, None
    fr, st, sec = {}, {}, None
    for ln in r.stdout.decode("latin-1").split("\n"):
        if ln.startswith("#section"):
            sec = ln.split()[1]
            continue
        if not ln or ln.startswith("#"):
            continue
        f = ln.split("\t")
        if sec == "facts" and len(f) >= 7:
            fr[f[1]] = f[6]
        elif sec == "decisions" and len(f) >= 3:
            st[f[1]] = f[2].strip('"')
    return fr, st


def gstart_prefilter(text):
    """The hybrid's static prefilter carries a `\\G` dispatch: its attempt
    loop compares `start` with its own third argument (ENG_ATTEMPT's shape)."""
    m = re.search(r'^static [^\n]*rx_prefilter\(.*?^}\n', text, re.S | re.M)
    return bool(m and "(start == search_from)" in m.group(0))


def predict(fr, st, text):
    """(mover?, K or None) from the facts/stamps alone."""
    if st.get("RX_REQ_WHY") != "emitted" or st.get("RX_REQ_RUN", "none") == "none":
        return False, None
    scan = st.get("RX_ENGINE") == "dfa" or st.get("RX_VM_PREFILTER") == "hybrid"
    k = fr.get("req_run_maxoff", "none")
    if not scan or not k.isdigit():
        return False, None
    if st.get("RX_VM_PREFILTER_LANG") == "count-collapsed":
        return False, None
    if st.get("RX_VM_PREFILTER") == "hybrid" and gstart_prefilter(text):
        kinds = fr.get("kinds", "")
        if "atomic" not in kinds and "lookaround" not in kinds:
            return False, None
    return True, int(k)


def one(job):
    i, pop, pat, args, cfg = job
    d = tempfile.mkdtemp(dir=SCR)
    try:
        for x in ("b", "a", "d"):
            os.makedirs(os.path.join(d, x))
        b = c3.emit(BASE, pat, args, d + "/b")
        a = c3.emit(NEW, pat, args, d + "/a")
        dn = c3.emit(NEW, pat, args + ["-fno-req-handoff"], d + "/d")
    finally:
        shutil.rmtree(d, ignore_errors=True)
    rec = {"i": i, "pop": pop, "cfg": cfg, "pat": pat.decode("latin-1"), "args": args}
    if any(x == "TIMEOUT" for x in (a, b, dn)):
        rec["id"] = "timeout"; return rec
    if b is None or a is None or dn is None:
        rec["id"] = "refused" if (b is None and a is None and dn is None) else "refusal-mismatch"
        return rec
    nb = norm_base(b)
    na, ka = strip_handoff(a)
    nd, kd = strip_handoff(dn)
    fr, st = facts(NEW, pat, args)
    frb, _stb = facts(BASE, pat, args)
    if fr is None or frb is None:
        rec["id"] = "timeout"; return rec
    mover, k = predict(fr, st, a)
    rec.update(id="moved" if na != nb else "identical", stamp=ka, deny_stamp=kd,
               predicted=mover, k=k, maxoff=fr.get("req_run_maxoff"),
               route=("hybrid" if st.get("RX_VM_PREFILTER") == "hybrid" else
                      "attempt" if "for (start = handoff_position" in a else
                      "unanchored" if "scan_position = handoff_position" in a else "-"),
               deny="identical" if nd == nb and kd == "none" else "moved",
               whole=(frb.get("req_whole_run"), fr.get("req_whole_run")),
               lang=st.get("RX_VM_PREFILTER_LANG"))
    return rec


def main():
    js = c3.jobs()
    wt = {j[0]: w for j, w in js}
    print("jobs:", len(js), file=sys.stderr, flush=True)
    with ThreadPoolExecutor(max_workers=int(os.environ.get("PROCS", "4"))) as ex:
        res = list(ex.map(one, [j for j, _w in js]))
    for r in res:
        r["w"] = wt[r["i"]]
    json.dump(res, open(f"{SCR}/k82h_movers.json", "w"), indent=0)
    bad = 0
    for pop in ("bench", "corpus"):
        rs = [r for r in res if r["pop"] == pop]
        cfgs = c3.BENCH_CFG if pop == "bench" else c3.CORPUS_CFG
        print(f"== {pop}: {len(rs)} distinct artifact-configs ({sum(r['w'] for r in rs)} rows)")
        print("  ids:", dict(collections.Counter(r["id"] for r in rs)))
        ok = [r for r in rs if r["id"] in ("identical", "moved")]
        tab = collections.Counter((r["id"], r["predicted"]) for r in ok)
        print(f"  moved & predicted {tab[('moved', True)]:6d}   moved & not {tab[('moved', False)]:6d}")
        print(f"  ident & predicted {tab[('identical', True)]:6d}   ident & not {tab[('identical', False)]:6d}")
        bad += tab[("moved", False)] + tab[("identical", True)]
        for r in ok:
            if (r["id"] == "moved") != r["predicted"]:
                print(f"   OFF-DIAGONAL {r['id']} predicted={r['predicted']} {r['cfg']} {r['pat'][:70]!r} {r['args']}")
            want = str(r["k"]) if r["predicted"] else "none"
            if r["stamp"] != want:
                bad += 1
                print(f"   STAMP {r['stamp']!r} != {want!r} {r['cfg']} {r['pat'][:70]!r} {r['args']}")
            if r["whole"][0] != r["whole"][1]:
                bad += 1
                print(f"   RUN-CHOICE {r['whole'][0]} -> {r['whole'][1]} {r['cfg']} {r['pat'][:70]!r}")
        for cfg in cfgs:
            mv = [r for r in ok if r["cfg"] == cfg and r["id"] == "moved"]
            ks = collections.Counter(r["k"] for r in mv)
            rt = collections.Counter(r["route"] for r in mv)
            unb = [r for r in ok if r["cfg"] == cfg and r["maxoff"] == "unbounded"]
            print(f"  {cfg}: movers {len(mv)} distinct ({sum(r['w'] for r in mv)} rows); "
                  f"K>0 {sum(1 for r in mv if r['k'])}; routes {dict(rt)}; "
                  f"unbounded-run artifacts {len(unb)}; K histogram {dict(sorted(ks.items(), key=lambda kv: str(kv[0])))}")
            langs = collections.Counter(r["lang"] for r in mv if r["route"] == "hybrid")
            if langs:
                print(f"    hybrid movers' RX_VM_PREFILTER_LANG {dict(langs)}")
        dmov = [r for r in ok if r["deny"] != "identical"]
        print(f"  deny arm: {len(ok) - len(dmov)} identical to BASE, {len(dmov)} not")
        bad += len(dmov)
        for r in dmov[:20]:
            print(f"   DENY-MOVED {r['cfg']} {r['pat'][:70]!r} {r['args']}")
        for r in rs:
            if r["id"] in ("timeout", "refusal-mismatch"):
                print(f"   {r['id'].upper()} {r['cfg']} {r['pat'][:70]!r}")
                bad += r["id"] == "refusal-mismatch"
        if not any(r["id"] == "moved" for r in ok):
            print("   EMPTY mover population (K35)"); bad += 1
    print(f"k82h_movers: {'PASS' if bad == 0 else 'FAIL'} ({bad} off-diagonal, stamp, run-choice, deny or refusal failures)")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
