"""covs1-sweep's exit contract (lane covs1w, fixed by covs1g after review r11 ADQ-3): the sweep is the
instrument, predict.py the judge.
usage: sweep_verdict.py REPORT MOVERS.tsv SWEEP_RC     |     sweep_verdict.py --selftest
Exit 0 iff the instrument POSITIVELY ran to completion and its only complaint, if any, is movers in the
two streams a gained cover touches (c-default, facts). Default is RED: every state not recognised as
"completed, all floors held" is red. It reads emit_sweep's own report; it never decides WHICH patterns
may move (predict.py does, from the baseline build)."""
import os, re, subprocess, sys, tempfile

# emit_sweep's failure vocabulary (scripts/emit_sweep.py: report_tally, the stream report, the floors,
# the DELIVER witness, completion_trailer). Each is printed only on a failure.
FAIL_RE = re.compile(r"VIOLATION|FAILURE|TAG FLOOR side|MANIFEST side|NO TAG FLOORS PINNED|"
                     r"CENSUS OFF-DIAGONAL|INVALID|uncaught exception|Traceback \(most recent|"
                     r"tag floors: NOT APPLIED|COMPOSITION FLOORS: NOT APPLIED|SELF-CHECK FAILED")


def judge(txt, movers_text, rc):
    """-> list of red reasons (empty = the instrument completed and is in the expected shape)."""
    bad = []
    real = txt.split("===== REAL RUN", 1)[1] if "===== REAL RUN" in txt else ""
    if "SELF-CHECK PASSED" not in txt:
        bad.append("self-check did not pass")
    m = re.findall(r"^emit_sweep: DONE rc=(\d+)\s*$", txt, re.M)
    if not m:
        bad.append("no clean DONE line (the sweep did not run to completion, or it died with an exception)")
    elif int(m[-1]) != rc:
        bad.append("DONE rc=%s disagrees with the sweep rc %d" % (m[-1], rc))
    if rc not in (0, 1):
        bad.append("sweep rc=%d (only 0, or 1 with movers, is a completed sweep)" % rc)
    if not real:
        bad.append("no REAL RUN section")
    if "DELIVER witness: OK" not in txt:
        bad.append("DELIVER witness not OK")
    for ln in txt.splitlines():
        if FAIL_RE.search(ln):
            bad.append("emit_sweep failure line: " + ln.strip()[:160])
    ntags = len(re.findall(r"^\s*tags \(side a / side b\):", real, re.M))
    nheld = len(re.findall(r"^\s*tag floors: \d+ pinned, all held\s*$", real, re.M))
    if ntags == 0:
        bad.append("no tallied stream reported tags")
    if nheld != ntags:
        bad.append("tag floors held for %d of %d tallied streams" % (nheld, ntags))
    if movers_text is None:
        bad.append("movers file not written")
    stream, allowed = None, {"c-default", "facts"}
    nstreams = nmov = 0
    for ln in real.splitlines():
        m = re.match(r"-- stream: (.*) --$", ln)
        if m:
            stream = m.group(1)
            continue
        m = re.search(r"movers=(\d+) asymmetric=(\d+)", ln)
        if m and stream:
            nstreams += 1
            mv, asym = int(m.group(1)), int(m.group(2))
            nmov += mv
            if asym:
                bad.append("stream %s: asymmetric=%d" % (stream, asym))
            if mv and stream not in allowed:
                bad.append("stream %s: movers=%d (only c-default/facts may move)" % (stream, mv))
    if nstreams < 11:
        bad.append("only %d streams reported in the real run (11 expected)" % nstreams)
    if rc == 1 and not nmov:
        bad.append("sweep rc=1 with no mover in any stream (an exit that is not 'movers exist')")
    for ln in (movers_text or "").splitlines():
        if ln.startswith("#") or not ln.strip():
            continue
        s, cls, _ = ln.split("\t", 2)
        if cls != "mover" or s not in allowed:
            bad.append("movers file row outside the allowed shape: %s %s" % (s, cls))
    return bad


def selftest():
    streams = ["c-default", "facts"] + ["s%d" % i for i in range(9)]
    body = "".join("-- stream: %s --\n  movers=0 asymmetric=0\n  tags (side a / side b): x=1/1\n"
                   "  tag floors: 3 pinned, all held\n" % s for s in streams)
    clean = ("SELF-CHECK PASSED: all-identical\n===== REAL RUN: a vs b =====\n" + body +
             "DELIVER witness: OK (x)\nemit_sweep: DONE rc=0\n")
    cases = [  # (name, report, movers, rc, expect_red)
        ("clean", clean, "", 0, False),
        ("movers in c-default", clean.replace("c-default --\n  movers=0", "c-default --\n  movers=4").replace("rc=0", "rc=1"),
         "c-default\tmover\tp\n", 1, False),
        ("tag floor failed", clean.replace("  tag floors: 3 pinned, all held\n",
         "  TAG FLOOR side a: x 1 < 9\n", 1), "", 1, True),
        ("floor line missing (no vocabulary)", clean.replace("  tag floors: 3 pinned, all held\n", "", 1), "", 0, True),
        ("reach floor", clean.replace("DELIVER witness", "  REACH FLOOR VIOLATION: 1 < 9\nDELIVER witness"), "", 0, True),
        ("uncaught exception", clean.replace("emit_sweep: DONE rc=0",
         "emit_sweep: DONE rc=1 (uncaught exception, traceback follows)"), "", 1, True),
        ("deliver failure", clean.replace("DELIVER witness: OK", "DELIVER WITNESS FAILURE: x\nDELIVER witness: OK"), "", 1, True),
        ("no DONE", clean.replace("emit_sweep: DONE rc=0\n", ""), "", 0, True),
        ("rc 2", clean.replace("DONE rc=0", "DONE rc=2"), "", 2, True),
        ("rc 1 without movers", clean.replace("DONE rc=0", "DONE rc=1"), "", 1, True),
        ("missing movers file", clean, None, 0, True),
        ("asymmetric", clean.replace("movers=0 asymmetric=0", "movers=0 asymmetric=2", 1), "", 0, True),
        ("mover in c-vm", clean.replace("s0 --\n  movers=0", "s0 --\n  movers=1").replace("rc=0", "rc=1"), "", 1, True),
        ("empty report", "", "", 0, True),
    ]
    fails = 0
    for name, rep, mv, rc, red in cases:
        got = bool(judge(rep, mv, rc))
        print("selftest %-36s expect %s got %s %s" % (name, "RED" if red else "ok", "RED" if got else "ok",
              "" if got == red else "WRONG"))
        fails += got != red
    print("sweep_verdict selftest: %s" % ("FAILED %d" % fails if fails else "all %d cases right" % len(cases)))
    sys.exit(1 if fails else 0)


if sys.argv[1:2] == ["--selftest"]:
    selftest()
report, movers, rc = sys.argv[1], sys.argv[2], int(sys.argv[3])
txt = open(report, errors="replace").read()
bad = judge(txt, open(movers).read() if os.path.exists(movers) else None, rc)
for b in bad:
    print("sweep_verdict: RED: " + b)
print("sweep_verdict: emit_sweep rc=%d; instrument %s; movers are predict.py's to judge" % (rc, "RED" if bad else "ok"))
sys.exit(1 if bad else 0)
