#!/usr/bin/env python3
"""l3feat2 R-2: for each pattern x {BASE, L3 without the decline, L3 with it}: DFA_PREFILTER, what the
default route's forward scan searches for, and whether that comes from the lookbehind.
Reads the emitted C (default route, --features all, byte):
  prefilter scan  = the rx_prefilter body: 'calls rx_reqrun' (the handoff row) or its memchr byte(s);
  entry           = whether rx_search_run asks rx_reqrun once before the first attempt (the entry move);
  run scan        = rx_reqrun__body's memchr byte and the run position it is (REQ_RUN's @idx);
  verify          = rx_reqrun__body's memcmp text.
A run position i is a LOOKBEHIND byte iff K < 0 and i < -K.
usage: r2_measure.py PATFILE OUT.tsv BASEBIN NODECBIN DECBIN"""
import os, re, subprocess, sys, tempfile

def emit(b, pat, td):
    o = os.path.join(td, "o.c")
    r = subprocess.run([b, "--features", "all", "-p", "rx", "-o", o, "--pattern", pat], capture_output=True)
    if r.returncode:
        return None
    return open(o, "rb").read().decode("latin-1")

def body(t, name):
    m = re.search(r"^static[^\n]*\b%s\(" % name, t, re.M)
    if not m:
        return None
    e = t.find("\n}\n", m.start())
    return t[m.start():e]

def stamp(t, k):
    m = re.search(r'#define RX_%s "([^"]*)"' % k, t)
    return m.group(1) if m else "-"

def run_positions(run):
    h = run.split("@")[0].split("/")[0]
    return re.findall(r"\[[0-9a-f]+\]|[0-9a-f]{2}", h)

def one(b, pat, td):
    t = emit(b, pat, td)
    if t is None:
        return dict(pf="REFUSED")
    pf, run, k = stamp(t, "DFA_PREFILTER"), stamp(t, "REQ_RUN"), stamp(t, "REQ_HANDOFF")
    kv = int(k) if re.fullmatch(r"-?\d+", k) else None
    lb = -kv if kv is not None and kv < 0 else 0
    pb = body(t, "rx_prefilter") or ""
    if "rx_reqrun(" in pb:
        pscan = "run finder (rx_reqrun)"
    else:
        bs = re.findall(r"memchr\(subject \+ [^,]*, (\d+),", pb)
        pscan = ("memchr " + ",".join(sorted(set(chr(int(x)) if 32 < int(x) < 127 else "\\x%02x" % int(x) for x in bs)))) if bs else "table/other (" + pf + ")"
    sr = body(t, "rx_search_run") or body(t, "rx_search") or ""
    entry = "handoff_position = rx_reqrun(" in sr
    rb = body(t, "rx_reqrun__body") or ""
    m = re.search(r"memchr\(subject \+ pos[^,]*, (\d+),", rb)
    sbyte = chr(int(m.group(1))) if m and 32 < int(m.group(1)) < 127 else (("\\x%02x" % int(m.group(1))) if m else "-")
    mi = re.search(r"@(\d+)", run); idx = int(mi.group(1)) if mi else None
    vm = re.search(r'memcmp\(subject \+ [^,]*, "((?:[^"\\]|\\.)*)", (\d+)\)', rb)
    ws = re.findall(r'rx_w\d+\("((?:[^"\\]|\\.)*)"\)', rb)
    verify = vm.group(1) if vm else ("+".join(ws) if ws else "-")
    src = "-"
    if idx is not None and rb:
        src = "LOOKBEHIND" if idx < lb else "consumed"
    pscan_src = ("scan byte " + src) if pscan.startswith("run finder") else "match start (consumed)"
    return dict(pf=pf, run=run, k=k, pscan=pscan, pscan_src=pscan_src, entry="entry asks run finder" if entry else "no entry ask",
                rscan=("%s @%s %s" % (sbyte, idx, src)) if rb else "-", verify=verify,
                verify_lb=("yes (%d lookbehind bytes)" % lb) if rb and lb and verify != "-" else "no")

def main():
    patf, out, base, nod, dec = sys.argv[1:]
    pats = [l.rstrip("\n") for l in open(patf, encoding="latin-1") if l.strip()]
    with tempfile.TemporaryDirectory(dir=os.environ.get("PCREC_TMPDIR", "/var/tmp/pcrec-%s" % os.environ.get("USER", "u"))) as td, open(out, "w") as f:
        cols = ("pf", "k", "run", "pscan", "pscan_src", "entry", "rscan", "verify", "verify_lb")
        f.write("pattern\tbuild\t" + "\t".join(cols) + "\n")
        for p in pats:
            pb = p.encode("latin-1").decode("unicode_escape").encode("latin-1")
            for name, b in (("BASE", base), ("L3-nodecline", nod), ("L3-decline", dec)):
                r = one(b, pb, td)
                f.write("%s\t%s\t%s\n" % (p, name, "\t".join(str(r.get(c, "")) for c in cols)))

if __name__ == "__main__":
    main()
