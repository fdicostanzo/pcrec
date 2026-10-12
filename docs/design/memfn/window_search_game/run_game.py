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
}

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
    eng = st.get("RX_ENGINE", "?")
    pf = st.get("RX_DFA_PREFILTER", "-")
    if eng == "vm":
        if st.get("RX_VM_START_SCAN") == "first-class" and "start_set" in fa:
            m = startset_mask(fa["start_set"])
            return G.Form(-1, [0], [m], 0, 0, "ship:vm-first-class", prior)
        return "ship:vm-" + st.get("RX_VM_PREFILTER", "-")
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
        if rr == "none" or not k.isdigit() or "@" not in rr:
            return "ship:handoff(no-run)"
        win = bytes.fromhex(rr.split("@")[0])
        rb = int(st.get("RX_REQ_BYTE", "-1")) if st.get("RX_REQ_BYTE", "none").isdigit() else win[0]
        a = win.index(rb) if rb in win else 0
        return G.Form(-1, [a], [1 << b for b in win], int(k), int(k), "ship:handoff", prior)
    return "ship:dfa-" + pf


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
    fs = open(os.path.join(out, "spans.tsv"), "w")
    fc = open(os.path.join(out, "choices.tsv"), "w")
    fm = open(os.path.join(out, "sim.tsv"), "w")
    fs.write("set\tname\tstatus\tnotes\tanch_start\tnspans\tnbounded\tkset_agree\tengine\t"
             "prefilter\toffsets\treq_run\thandoff\tspans\n")
    fc.write("set\tname\tpolicy\tform\test_stop\test_surv\texp_cost_none\texp_cost_dfa\texp_cost_vm\n")
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
        chosen = []
        if ext["status"] == "ok" and not ext.get("anch_start"):
            for pname, pol in G.POLICIES:
                chosen.append((pname, pol(sp, prior)))
        sh = shipped(fa, st, ext, prior)
        chosen.append(("SHIPPED", sh))
        for pname, f in chosen:
            if isinstance(f, G.Form):
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
            for pname, f in chosen + extra:
                if not isinstance(f, G.Form):
                    fm.write("%s\t%s\t%s\t%s\t%s\t-\t-\t-\t-\t-\t-\t-\t%s\n" % (
                        s, name, sid, pname, f or "no-bounded-span", pm))
                    continue
                c = G.simulate(f, S)
                fm.write("%s\t%s\t%s\t%s\t%s\t%d\t%d\t%d\t%d\t%d\t%.0f\t%.0f\t%s\n" % (
                    s, name, sid, pname, f.desc(), c["stops"], c["surv"], c["win_bytes"],
                    c["win_union"], c["starts"], G.work(c, f, "dfa", len(S)),
                    G.work(c, f, "vm", len(S)), pm))
        print(fid, ext["status"], len(sp), file=sys.stderr)
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    sys.exit(main(*a[:6], int(a[6]) if len(a) > 6 else 150))
