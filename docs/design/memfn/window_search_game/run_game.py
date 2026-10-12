#!/usr/bin/env python3
"""run_game.py -- the population run (lane wingame). Counts only, no clock.

    run_game.py PCREC BENCHCOPY SUBJDIR PRIOR.tsv CORPUSROOT OUTDIR [NCORPUS]

For every pattern of the bench's capability/loglines/syntax sets and a
deterministic sample of NCORPUS (default 150) corpus `pattern` lines:
  1. derive D161's span list (spans.py) and check it against pcrec's own
     k-set walk (`kset_agree`: fixed-prefix class sizes vs the walk's sizes);
  2. read pcrec's facts and stamps (`--emit-facts`, one compile each) and map
     today's SHIPPED window search onto the same Form shape where it has one;
  3. run every kit policy (game.POLICIES, the shipped default prior) plus
     P5-dfa under the SUBJECT's own byte rates (the prior-mismatch control);
  4. simulate every chosen form over the set's throughput subjects (the
     corpus sample over capability's t-256k) and write the counts.
Outputs: spans.tsv, choices.tsv, sim.tsv, facts/<id>.facts.
"""
import glob
import hashlib
import os
import re
import signal
import subprocess
import sys

import numpy as np

import game as G
import spans as SP

SETS = {
    "capability": ["capability__t-256k"],
    "loglines": ["loglines__t-256k-fail", "loglines__t-256k-hit"],
    "syntax": ["syntax__t-256k"],
    "corpus": ["capability__t-256k"],
    "wit2": ["capability__t-256k", "loglines__t-256k-fail", "loglines__t-256k-hit",
             "syntax__t-256k"],
}

# [wingame2] two-span witnesses for P6 `refine`, appended to the population as
# their own set (summarize.py's census tables name the four original sets, so
# they stay as published). A = the digit span (no rare target), B = the rare
# one. `bounded` gaps give a region; `unbounded` ones are Frank's fallback.
WIT2 = [
    ("w01-bounded-4", rb"\d{3}.{0,4}#"),
    ("w02-bounded-0", rb"\d{3}#"),
    ("w03-bounded-12", rb"\d{2,4}.{0,12}#"),
    ("w04-bounded-x", rb"[0-9]{1,4} x{2}"),
    ("w05-bounded-at", rb"\d{3}.{0,8}@"),
    ("w06-loose-gap", rb".{0,6}\d.{0,3}#"),
    ("w07-unbounded-hash", rb"\d+.*#"),
    ("w08-unbounded-x", rb"[0-9]+ x{2}"),
    ("w09-unbounded-at", rb"\d+\w*@"),
    ("w10-unbounded-lit", rb"\d+.*timeout"),
    ("w11-A-semirare", rb"\d{3}-.{0,4}#"),
]

PF_START = {"memchr", "byte-class", "first-class", "first-memchr", "memchr-bounded",
            "byte-class-bounded", "first-class-bounded", "first-memchr-bounded"}


def population(bench, corpus_root, ncorpus):
    pop = []
    for s in ("capability", "loglines", "syntax"):
        for f in sorted(glob.glob(os.path.join(bench, s, "patterns", "*.rx"))):
            b = open(f, "rb").read()
            if b.endswith(b"\n"):
                b = b[:-1]
            pop.append((s, os.path.basename(f)[:-3], b))
    seen = set()
    cand = []
    for f in sorted(glob.glob(os.path.join(corpus_root, "*", "*.rxt"))):
        if "/bench/" in f or "/fuzz/" in f:
            continue
        for ln in open(f, "rb"):
            if ln.startswith(b"pattern "):
                p = ln[8:].rstrip(b"\n")
                if p and p not in seen and len(p) < 200:
                    seen.add(p)
                    cand.append(p)
    cand.sort(key=lambda p: hashlib.sha1(p).hexdigest())
    for i, p in enumerate(cand[:ncorpus]):
        pop.append(("corpus", "c%03d" % i, p))
    return pop


def facts(pcrec, pat, path):
    if not os.path.exists(path):
        r = subprocess.run(["gnutimeout", "30", pcrec, "--features", "all", "--emit-facts",
                            "--pattern", pat], capture_output=True)
        open(path, "wb").write(r.stdout + b"#rc\t%d\n" % r.returncode + r.stderr)
    fa, st = {}, {}
    for ln in open(path, "rb").read().decode("latin-1").splitlines():
        f = ln.split("\t")
        if ln.startswith("#rc\t"):
            st["_rc"] = f[1]
        if ln.startswith("#") or len(f) < 3:
            continue
        if len(f) >= 7 and f[0] == "byte":
            fa[f[1]] = f[6]
        elif len(f) == 3 and f[0] == "byte":
            st[f[1]] = f[2].strip('"')
    return fa, st


def startset_mask(v):
    if ":" not in v:
        return None
    hx = v.split(":", 1)[1]
    m = 0
    for i in range(32):
        byte = int(hx[2 * i:2 * i + 2], 16)
        for k in range(8):
            if byte >> k & 1:
                m |= 1 << (8 * i + k)
    return m


def kset_list(v):
    out = []
    for t in v.split(","):
        t = t.strip()
        if not t:
            continue
        if t.startswith("["):
            out.append(("n", int(t[1:-1])))
        else:
            out.append(("b", int(t)))
    return out


def kset_agree(ext, fa):
    """(agree, disagree) over the fixed prefix span's positions."""
    if ext["status"] != "ok" or not ext["spans"] or "kset_walk" not in fa:
        return None
    s0 = ext["spans"][0]
    if s0["omin"] != 0 or s0["overshoot"] != 0:
        return None
    ks = kset_list(fa["kset_walk"])
    ag = dis = 0
    for j, c in enumerate(s0["classes"]):
        if j >= len(ks):
            break
        n = 1 if ks[j][0] == "b" else ks[j][1]
        if n == SP.popc(c):
            ag += 1
        else:
            dis += 1
    return ag, dis


def shipped(fa, st, ext, prior):
    """Today's choice as a Form, or a string naming why it has none."""
    if st.get("_rc", "0") != "0":
        return "ship:compile-refused"
    eng = st.get("RX_ENGINE", "?")
    pf = st.get("RX_DFA_PREFILTER", "-")
    if eng == "vm":
        if st.get("RX_VM_START_SCAN") == "first-class" and "start_set" in fa:
            m = startset_mask(fa["start_set"])
            return G.Form(-1, [0], [m], 0, 0, "ship:vm-first-class", prior)
        if st.get("RX_VM_PREFILTER") != "hybrid":
            return "ship:vm-" + st.get("RX_VM_PREFILTER", "-")
        # the hybrid's inlined DFA prefilter carries the scan: map it below
    if pf in PF_START and "start_set" in fa:
        m = startset_mask(fa["start_set"])
        if m is not None and SP.popc(m) < 256:
            return G.Form(-1, [0], [m], 0, 0, "ship:" + pf, prior)
        return "ship:" + pf + "(no-set)"
    if pf.startswith("offset-set") or pf.startswith("run-pinned"):
        offs = st.get("RX_DFA_PREFILTER_OFFSETS", "none")
        if offs == "none":
            return "ship:" + pf + "(no-offsets)"
        ks = kset_list(fa.get("kset_walk", ""))
        pre = None
        if ext["status"] == "ok" and ext["spans"] and ext["spans"][0]["omin"] == 0 \
                and ext["spans"][0]["overshoot"] == 0:
            pre = ext["spans"][0]["classes"]
        items = []
        for t in offs.split(","):
            items.append((int(t.rstrip("*")), t.endswith("*")))
        L = max(o for o, _ in items) + 1
        cl = [SP.ALL] * L
        scan = None
        for o, star in items:
            if o < len(ks) and ks[o][0] == "b":
                cl[o] = 1 << ks[o][1]
            elif pre is not None and o < len(pre) and (o >= len(ks) or SP.popc(pre[o]) == ks[o][1]):
                cl[o] = pre[o]
            else:
                return "ship:" + pf + "(class-unknown)"
            if star:
                scan = o
        return G.Form(-1, [scan if scan is not None else items[0][0]], cl, 0, 0, "ship:" + pf, prior)
    if pf == "handoff":
        rr = st.get("RX_REQ_RUN", "none")
        k = st.get("RX_REQ_HANDOFF", "none")
        rbs = st.get("RX_REQ_BYTE", "none")
        if (rr == "none" or "@" not in rr) and k.isdigit() and rbs.isdigit():
            # a one-byte landmark: the req byte, K back (no minimum offset is
            # carried, so the overshoot is K)
            return G.Form(-1, [0], [1 << int(rbs)], int(k), int(k), "ship:handoff-byte", prior)
        if rr == "none" or not k.isdigit() or "@" not in rr:
            return "ship:handoff(no-run)"
        win = bytes.fromhex(rr.split("@")[0])
        msk = bytes.fromhex(rr.split("/")[1]) if "/" in rr else b"\xff" * len(win)
        cl = [(1 << b) | (1 << (b ^ (~m & 0xFF))) for b, m in zip(win, msk)]
        rb = int(st.get("RX_REQ_BYTE", "-1")) if st.get("RX_REQ_BYTE", "none").isdigit() else win[0]
        a = win.index(rb) if rb in win else 0
        return G.Form(-1, [a], cl, int(k), int(k), "ship:handoff", prior)
    return "ship:dfa-" + pf


def span_reps(sp, prior):
    """Per bounded span: its rarest single position and its best pair --
    the span-vs-span comparison Frank asked about."""
    out = []
    by = {}
    for f in G.forms_of(sp, prior, True):
        k = (f.si, f.kind)
        if k not in by or f.est_stop < by[k].est_stop:
            by[k] = f
    for k in sorted(by):
        out.append(by[k])
    return out


# shipped routes with no window search at all: the engine meets every byte
SCAN_ALL = re.compile(r"ship:(dfa-none|dfa--|vm-none|vm--|dfa-prefilter-none)$")

_ALARM = False


def _al(sig, frm):
    raise TimeoutError()


def pymatches(ext_py, buf):
    if ext_py is None:
        return "-"
    try:
        rx = re.compile(ext_py.encode("latin-1"))
    except Exception:
        return "-"
    signal.signal(signal.SIGALRM, _al)
    signal.alarm(3)
    try:
        n = sum(1 for _ in rx.finditer(buf))
    except TimeoutError:
        n = "timeout"
    finally:
        signal.alarm(0)
    return str(n)


def fmt_none(v):
    return "inf" if v is None else str(v)


def relcontrol(fk, s, name, ext):
    """The control for G.region_of: the relative distance of two bounded
    spans derived from (move-back, overshoot, length) alone against a DIRECT
    walk of the items between them."""
    sp = ext["spans"]
    for i in range(len(sp)):
        for j in range(i + 1, len(sp)):
            if sp[i]["move_back"] is None:
                continue
            lo, hi = SP.rel_from_items(ext["items"], sp, i, j)
            reg = G.region_of(sp[i], sp[j])      # start(A) - start(B), A = i
            if sp[j]["move_back"] is None:
                dl = dh = "-"
                ag = hi is None
            else:
                dl, dh = (-reg[1], -reg[0]) if reg else ("-", "-")
                ag = reg is not None and (dl, dh) == (lo, hi)
            fk.write("%s\t%s\t%d\t%d\t%s\t%s\t%s\t%s\t%d\n" % (
                s, name, i, j, lo, fmt_none(hi), dl, dh, ag))


def refine_rows(fr, s, name, sid, sp, prior, S, chosen):
    """[wingame2] One block of variant rows per (consumer) for the patterns
    where Frank's setting exists (refine_pair) or a P6 policy picked a plan."""
    pair = G.refine_pair(sp, prior)
    picked = any(isinstance(chosen.get(p), G.Plan) for p in ("P6-dfa", "P6-vm"))
    if pair is None and not picked:
        return
    n = len(S)

    def row(cons, variant, gap, reg, f, c, w):
        fr.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%.0f\t%s\n" % (
            s, name, sid, cons, variant, gap, reg, f.desc() if f is not None else "-",
            c.get("stops", n), c.get("bsurv", "-"), c.get("local_pos", "-"), c.get("surv", n),
            c.get("win_bytes", n), c.get("starts", n), w,
            "%.3g" % ((f.width + 1) * f.fA.est_surv) if isinstance(f, G.Plan) else "-"))

    gap = "-"
    if pair is not None:
        ia, ib = pair
        gap = "bounded" if G.region_of(sp[ia], sp[ib]) is not None else "unbounded"
    for cons in ("dfa", "vm"):
        base = G.baseline_cost(cons) * n
        row(cons, "nosearch", gap, "-", None, {}, base)
        for pn in ("P5", "P6"):
            f = chosen["%s-%s" % (pn, cons)]
            if isinstance(f, (G.Form, G.Plan)):
                c = G.simulate_any(f, S)
                row(cons, pn, gap, ("%d" % f.width) if isinstance(f, G.Plan) else "-", f, c,
                    G.work_any(c, f, cons, n))
            else:
                row(cons, pn, gap, "-", None, {}, base)
        if pair is None:
            continue
        ia, ib = pair
        for loose in (False, True):
            ps = [p for p in G.plans_of(sp, prior, loose) if p.ia == ia and p.ib == ib]
            if not ps:
                continue
            p = ps[0]
            c = G.simulate_plan(p, S)
            row(cons, "local-loose" if loose else "local", gap, "%d" % p.width, p, c,
                G.work_any(c, p, cons, n))
            if not loose:
                cm = dict(c, surv=c["mcand"], win_bytes=c["mbytes"], starts=c["mstarts"])
                row(cons, "local-merge", gap, "%d" % p.width, p, cm, G.work_merge(c, p, cons, n))
        f = G.best_form_of(sp, ia, prior, cons)
        if f is None:
            continue
        c = G.simulate(f, S)
        row(cons, "fwd", gap, "-", f, c, G.work(c, f, cons, n))
        sa, sb = sp[ia], sp[ib]
        gr, k = G.rare_pos(sb, prior)
        gm = sb["classes"][k]
        if sb["omin"] >= sa["omin"] + len(sa["classes"]):      # B after A
            goff = sb["omin"] - sa["omin"] + k
        else:                                  # sound for any order: B is at or after
            goff = k + sb["omin"] - sa["move_back"]    # the window's beginning
        cg = G.simulate_gate(f, S, gm, goff)
        gp = G.scan_price(G.Form(0, [0], [gm], 0, 0, "one", prior))
        row(cons, "fwd-gate", gap, "gate:%s@%d,rate=%.3g,last=%d" % (SP.fmt_class(gm), goff, gr, cg["last"]), f, cg,
            G.work_gate(cg, f, cons, gp))
        # the consumer meeting every byte up to the last B, behind the same gate
        cb = G.baseline_cost(cons)
        row(cons, "nosearch-gate", gap, "gate:%s@%d" % (SP.fmt_class(gm), goff), None,
            {"stops": cg["last"] + 1}, gp * n + cb * max(0, cg["last"] + 1 - goff))
        # TAIL form of the gate: ONE reverse scan from the end for the last B
        # (cost = the tail beyond it), and the forward search ends there. It
        # pays the gate only for the bytes it can save.
        tail = n - cg["last"] - 1 if cg["last"] >= 0 else n
        ct = dict(cg, gate_n=tail)
        row(cons, "fwd-tail", gap, "tail:%s@%d,bytes=%d" % (SP.fmt_class(gm), goff, tail), f, ct,
            G.work_gate(ct, f, cons, gp))
        row(cons, "nosearch-tail", gap, "tail:%s@%d" % (SP.fmt_class(gm), goff), None,
            {"stops": cg["last"] + 1}, gp * tail + cb * max(0, cg["last"] + 1 - goff))


def main(pcrec, bench, subjdir, prior_path, corpus_root, out, ncorpus=150):
    os.makedirs(os.path.join(out, "facts"), exist_ok=True)
    prior = G.load_prior(prior_path)
    subj = {}
    for s, ids in SETS.items():
        for sid in ids:
            if sid not in subj:
                buf = open(os.path.join(subjdir, sid + ".bin"), "rb").read()
                subj[sid] = (buf, np.frombuffer(buf, np.uint8), G.prior_from_subject(buf))
    pop = population(bench, corpus_root, ncorpus)
    pop += [("wit2", n, p) for n, p in WIT2]
    if os.environ.get("WINGAME_ONLY"):
        pop = [x for x in pop if x[0] == os.environ["WINGAME_ONLY"]]
    if os.environ.get("WINGAME_LIMIT"):          # smoke runs during a box hold
        pop = pop[::max(1, len(pop) // int(os.environ["WINGAME_LIMIT"]))]
    fs = open(os.path.join(out, "spans.tsv"), "w")
    fc = open(os.path.join(out, "choices.tsv"), "w")
    fm = open(os.path.join(out, "sim.tsv"), "w")
    fs.write("set\tname\tstatus\tnotes\tanch_start\tnspans\tnbounded\tkset_agree\tengine\t"
             "prefilter\toffsets\treq_run\thandoff\tspans\n")
    fc.write("set\tname\tpolicy\tform\test_stop\test_surv\texp_cost_none\texp_cost_dfa\texp_cost_vm\n")
    fi = open(os.path.join(out, "spaninfo.tsv"), "w")
    fi.write("set\tname\tspan\tL\tomin\tmb\tov\tmin_pos_rate\tjoint_rate\tspan\n")
    fp = open(os.path.join(out, "spanforms.tsv"), "w")
    fp.write("set\tname\tsubject\tspan\tkind\tform\tL\tmb\tov\test_stop\test_surv\t"
             "stops\tsurv\twin_bytes\tstarts\twork_scan\twork_dfa\twork_vm\n")
    fr = open(os.path.join(out, "refine.tsv"), "w")
    fr.write("set\tname\tsubject\tconsumer\tvariant\tgap\tregion\tform\tstops\tbsurv\tlocal_pos\t"
             "surv\twin_bytes\tstarts\twork\test_hits\n")
    fk = open(os.path.join(out, "relcontrol.tsv"), "w")
    fk.write("set\tname\ti\tj\titems_lo\titems_hi\tderived_lo\tderived_hi\tagree\n")
    fm.write("set\tname\tsubject\tpolicy\tform\tstops\tsurv\twin_bytes\twin_union\tstarts\t"
             "work_dfa\twork_vm\tpy_matches\n")
    for s, name, pat in pop:
        ext = SP.extract(pat)
        ext_py = None
        if ext["status"] == "ok":
            try:
                ext_py = SP.pcre_to_py(pat.decode("latin-1"))[0]
            except ValueError:
                ext_py = None
        fid = "%s__%s" % (s, name)
        fa, st = facts(pcrec, pat, os.path.join(out, "facts", fid + ".facts"))
        ka = kset_agree(ext, fa)
        sp = ext["spans"]
        fs.write("\t".join([s, name, ext["status"] if ext["status"] == "ok" else "unparsed:" + ext["why"],
                            ",".join(sorted(ext["notes"])) or "-",
                            str(ext.get("anch_start", "-")), str(len(sp)),
                            str(len(G.bounded_spans(sp))),
                            "-" if ka is None else "%d/%d" % ka,
                            st.get("RX_ENGINE", "?"), st.get("RX_DFA_PREFILTER", "-"),
                            st.get("RX_DFA_PREFILTER_OFFSETS", "-"), st.get("RX_REQ_RUN", "-"),
                            st.get("RX_REQ_HANDOFF", "-"),
                            " ".join(SP.fmt_span(x) for x in sp)]) + "\n")
        for i, x in enumerate(sp):
            rates = [G.pc(prior, c) for c in x["classes"]]
            fi.write("%s\t%s\t%d\t%d\t%d\t%s\t%s\t%.3g\t%.3g\t%s\n" % (
                s, name, i, len(x["classes"]), x["omin"], fmt_none(x["move_back"]),
                fmt_none(x["overshoot"]), min(rates), float(np.prod(rates)), SP.fmt_span(x)))
        chosen = []
        if ext["status"] == "ok" and not ext.get("anch_start"):
            for pname, pol in G.POLICIES:
                chosen.append((pname, pol(sp, prior)))
        if ext["status"] == "ok":
            relcontrol(fk, s, name, ext)
        sh = shipped(fa, st, ext, prior)
        chosen.append(("SHIPPED", sh))
        for pname, f in chosen:
            if isinstance(f, (G.Form, G.Plan)):
                fc.write("%s\t%s\t%s\t%s\t%.3g\t%.3g\t%.4g\t%.4g\t%.4g\n" % (
                    s, name, pname, f.desc(), f.est_stop, f.est_surv,
                    G.expected_cost(f, "none"), G.expected_cost(f, "dfa"), G.expected_cost(f, "vm")))
            else:
                fc.write("%s\t%s\t%s\t%s\t-\t-\t-\t-\t-\n" % (s, name, pname, f or "no-bounded-span"))
        for sid in SETS[s]:
            buf, S, sprior = subj[sid]
            extra = []
            if ext["status"] == "ok" and not ext.get("anch_start"):
                extra.append(("P5-dfa-subjprior", G.pol_window("dfa")(sp, sprior)))
            pm = pymatches(ext_py, buf)
            if ext["status"] == "ok" and not ext.get("anch_start"):
                for f in span_reps(sp, prior):
                    c = G.simulate(f, S)
                    fp.write("%s\t%s\t%s\t%d\t%s\t%s\t%d\t%d\t%d\t%.3g\t%.3g\t%d\t%d\t%d\t%d\t%.0f\t%.0f\t%.0f\n" % (
                        s, name, sid, f.si, f.kind, f.desc(), f.L, f.mb, f.ov, f.est_stop,
                        f.est_surv, c["stops"], c["surv"], c["win_bytes"], c["starts"],
                        G.work(c, f, "none", len(S)), G.work(c, f, "dfa", len(S)),
                        G.work(c, f, "vm", len(S))))
            for pname, f in chosen + extra:
                if f == "decline" or (isinstance(f, str) and SCAN_ALL.match(f)):
                    n = len(S)
                    fm.write("%s\t%s\t%s\t%s\t%s\t%d\t%d\t%d\t%d\t%d\t%.0f\t%.0f\t%s\n" % (
                        s, name, sid, pname, f + "(consumer-meets-every-byte)", n, n, n, n, n,
                        G.baseline_cost("dfa") * n, G.baseline_cost("vm") * n, pm))
                    continue
                if not isinstance(f, (G.Form, G.Plan)):
                    fm.write("%s\t%s\t%s\t%s\t%s\t-\t-\t-\t-\t-\t-\t-\t%s\n" % (
                        s, name, sid, pname, f or "no-bounded-span", pm))
                    continue
                c = G.simulate_any(f, S)
                fm.write("%s\t%s\t%s\t%s\t%s\t%d\t%d\t%d\t%d\t%d\t%.0f\t%.0f\t%s\n" % (
                    s, name, sid, pname, f.desc(), c["stops"], c["surv"], c["win_bytes"],
                    c["win_union"], c["starts"], G.work_any(c, f, "dfa", len(S)),
                    G.work_any(c, f, "vm", len(S)), pm))
            if ext["status"] == "ok" and not ext.get("anch_start"):
                refine_rows(fr, s, name, sid, sp, prior, S, dict(chosen))
        print(fid, ext["status"], len(sp), file=sys.stderr)
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    sys.exit(main(*a[:6], int(a[6]) if len(a) > 6 else 150))
