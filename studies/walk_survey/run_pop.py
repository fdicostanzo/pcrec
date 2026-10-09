#!/usr/bin/env python3
"""walk_survey: run the instrument over a population.

    PCREC=... PROBE=... python3 run_pop.py POP.tsv OUT.tsv [JOBS]

POP.tsv rows (pop_bench.py / pop_corpus.py): pid set enc icase pattern_hex
regime subjects. For every pid and CONFIG (default; nocaps = --no-captures)
one instrumented artifact is built (wsbuild.py) and every regime row's
subjects are run through wsdrv. Each OUT row = one (pid, config, regime,
subject) with the artifact's route stamps, the pattern facts, the probe's
widths, and wsdrv's per-phase columns. A refused compile is one row with
rc=REFUSED; a run over its time limit is rc=TIMEOUT (a FINDING, not a skip).
"""
import concurrent.futures as cf, hashlib, os, re, subprocess, sys

PCREC = os.environ["PCREC"]; PROBE = os.environ["PROBE"]
HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.environ.get("WORK", os.path.join(HERE, "work"))
TO = os.environ.get("TIMEOUT_BIN", "/usr/bin/gnutimeout")
CONFIGS = os.environ.get("CONFIGS", "default,nocaps").split(",")
STAMPS = ["ENGINE", "ENGINE_SEL", "DFA_SCAN", "DFA_PREFILTER", "DFA_START", "DFA_MATCH",
          "DFA_SCAN_EDGE", "REQ_BYTE", "REQ_RUN", "REQ_HANDOFF", "END_WINDOW",
          "VM_PREFILTER", "VM_START_SCAN", "MEMFN_LIBC"]
FACTS = ["start_anchor", "nullable", "end_window", "req_byte", "req_run"]


def stamps(c):
    d = {}
    for m in re.finditer(r'^#define RX_(\w+) ("?)([^"\n]*)\2\s*$', open(c, errors="replace").read(), re.M):
        d[m.group(1)] = m.group(3)
    return d


def facts(args):
    r = subprocess.run([PCREC, "--emit-facts"] + args, capture_output=True, timeout=300)
    d = {}
    for ln in r.stdout.decode("utf8", "replace").split("\n"):
        f = ln.split("\t")
        if len(f) >= 7 and f[1] in FACTS:
            d[f[1]] = f[6] if f[4] != "declined" else "declined:" + (f[7] if len(f) > 7 else "")
    return d


def probe(enc, pat):
    r = subprocess.run([PROBE], input=("0\t%s\t%s\n" % (enc, pat.hex())).encode(),
                       capture_output=True, timeout=120)
    f = r.stdout.decode().split("\n")[1].split("\t") if r.returncode == 0 else []
    if len(f) >= 8 and f[1] == "ok":
        return dict(view=f[2], cwmax=f[3], minw=f[4], lead_unb=f[5], gstart=f[6])
    return dict(view="?", cwmax="?", minw="?", lead_unb="?", gstart="?")


def one(job):
    pid, enc, icase, pat, rows = job
    out = []
    pr = probe(enc, (b"(?i)" + pat) if icase else pat)
    cfgs = list(CONFIGS)
    if any(r == "match" for r, _ in rows):
        cfgs.append("anch")
    for cfg in cfgs:
        args = ["--features", "all"]
        if enc == "utf8": args += ["-e", "utf8"]
        if icase: args.append("-i")
        if cfg == "nocaps": args.append("--no-captures")
        # anch: the ANCHORED-ATTEMPT REFERENCE for the match regime -- the
        # pattern wrapped as \A(?:P), searched at 0; its machine phases'
        # unique bytes are what an anchored attempt at 0 reads
        ptxt = (b"\\A(?:" + pat + b")") if cfg == "anch" else pat
        args += ["--pattern-esc", "--pattern", "\"" + esc(ptxt) + "\""]
        h = hashlib.sha1((cfg + enc + str(icase)).encode() + pat).hexdigest()[:16]
        myrows = [(r, x) for r, x in rows if r == "match"] if cfg == "anch" else rows
        art = os.path.join(WORK, "art", h)
        b = subprocess.run([sys.executable, os.path.join(HERE, "wsbuild.py"), PCREC, art] + args,
                           capture_output=True, timeout=1800)
        base = dict(pid=pid, config=cfg, enc=enc)
        base.update(pr)
        if b.returncode != 0:
            base["rc"] = "REFUSED" if b.returncode == 3 else "BUILDFAIL"
            base["note"] = b.stdout.decode("utf8", "replace").strip().replace("\t", " ")[:160]
            out.append(base); continue
        st = stamps(os.path.join(art, "rx.c"))
        base.update({k: st.get(k, "") for k in STAMPS})
        base.update(facts(args))
        for regime, subs in myrows:
            mode = "search" if cfg == "anch" else {"match": "match", "search_short": "search", "throughput": "findall",
                    "search": "search", "findall": "findall"}[regime]
            lim = "600" if regime in ("throughput", "findall") else "120"
            res = run(art, mode, enc, subs, lim)
            if res is None:   # batch timed out: per subject
                res = []
                for s in subs:
                    r1 = run(art, mode, enc, [s], lim)
                    res += r1 if r1 else [dict(subject=os.path.basename(s), rc="TIMEOUT")]
            for r in res:
                row = dict(base); row.update(r); row["regime"] = regime
                out.append(row)
    return out


def esc(b):
    o = []
    for c in b:
        if c == 0x5c: o.append("\\\\")
        elif c == 0x22: o.append('\\"')
        elif 0x20 <= c < 0x7f: o.append(chr(c))
        else: o.append("\\x%02x" % c)
    return "".join(o)


def run(art, mode, enc, subs, lim):
    p = subprocess.run([TO, "-s", "KILL", lim, os.path.join(art, "bin"), os.path.join(art, "map"),
                        mode, "1" if enc == "utf8" else "0"] + subs, capture_output=True)
    if p.returncode != 0:
        return None
    lines = p.stdout.decode().rstrip("\n").split("\n")
    hdr = lines[0].split("\t")
    return [dict(zip(hdr, l.split("\t"))) for l in lines[1:]]


def main():
    pop, outp = sys.argv[1], sys.argv[2]
    jobs = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    groups = {}
    for ln in open(pop).read().split("\n")[1:]:
        f = ln.split("\t")
        if len(f) < 7: continue
        g = groups.setdefault(f[0], [f[0], f[2], f[3] == "1", bytes.fromhex(f[4]), []])
        g[4].append((f[5], f[6].split(",")))
    cols = None
    with open(outp, "w") as fo, cf.ProcessPoolExecutor(jobs) as ex:
        for i, res in enumerate(ex.map(one, groups.values(), chunksize=1)):
            for r in res:
                if cols is None:
                    cols = ["pid", "config", "regime", "enc", "rc", "note", "view", "cwmax", "minw",
                            "lead_unb", "gstart"] + STAMPS + FACTS + \
                           ["subject", "n", "s", "e", "calls", "nmatch", "T", "U", "U_before",
                            "U_span", "U_after", "mult2", "multmax", "unk_pcs", "T_scan", "ahead", "span_sum", "land_rev", "land_calls", "ovl"] + \
                           ["%s_%s" % (a, p) for p in ["pre", "skip", "fwd", "rev", "anc", "vm", "endw", "misc", "unk"]
                            for a in ("T", "U", "lo", "hi", "A")]
                    fo.write("\t".join(cols) + "\n")
                fo.write("\t".join(str(r.get(c, "")) for c in cols) + "\n")
            fo.flush()
            if i % 50 == 0:
                print("done", i, "of", len(groups), flush=True)


if __name__ == "__main__":
    main()
