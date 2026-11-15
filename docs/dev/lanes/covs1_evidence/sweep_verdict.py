"""covs1-sweep's exit contract (lane covs1w): the sweep is the instrument, predict.py the judge.
usage: sweep_verdict.py REPORT MOVERS.tsv SWEEP_RC
Exit 0 iff the instrument ran to completion and its only complaint, if any, is movers in the
two streams a gained cover touches (c-default, facts). It reads emit_sweep's own report; it
never decides WHICH patterns may move (predict.py does, from the baseline build)."""
import os, re, sys

report, movers, rc = sys.argv[1], sys.argv[2], int(sys.argv[3])
txt = open(report, errors="replace").read()
real = txt.split("===== REAL RUN", 1)[1] if "===== REAL RUN" in txt else ""
bad = []
if "SELF-CHECK PASSED" not in txt:
    bad.append("self-check did not pass")
if "emit_sweep: DONE" not in txt:
    bad.append("no DONE line (the sweep did not run to completion)")
if not real:
    bad.append("no REAL RUN section")
if "DELIVER witness: OK" not in txt:
    bad.append("DELIVER witness not OK")
if not os.path.exists(movers):
    bad.append("movers file not written")
for ln in real.splitlines():
    if ln.strip().startswith("tag floors:") and "all held" not in ln:
        bad.append("tag floor: " + ln.strip())
stream, allowed = None, {"c-default", "facts"}
nstreams = 0
for ln in real.splitlines():
    m = re.match(r"-- stream: (.*) --$", ln)
    if m:
        stream = m.group(1)
        continue
    m = re.search(r"movers=(\d+) asymmetric=(\d+)", ln)
    if m and stream:
        nstreams += 1
        mv, asym = int(m.group(1)), int(m.group(2))
        if asym:
            bad.append("stream %s: asymmetric=%d" % (stream, asym))
        if mv and stream not in allowed:
            bad.append("stream %s: movers=%d (only c-default/facts may move)" % (stream, mv))
if nstreams < 11:
    bad.append("only %d streams reported in the real run (11 expected)" % nstreams)
if os.path.exists(movers):
    for ln in open(movers):
        if ln.startswith("#") or not ln.strip():
            continue
        s, cls, _ = ln.split("\t", 2)
        if cls != "mover" or s not in allowed:
            bad.append("movers file row outside the allowed shape: %s %s" % (s, cls))
for b in bad:
    print("sweep_verdict: RED: " + b)
print("sweep_verdict: emit_sweep rc=%d; instrument %s; movers are predict.py's to judge" % (rc, "RED" if bad else "ok"))
sys.exit(1 if bad else 0)
