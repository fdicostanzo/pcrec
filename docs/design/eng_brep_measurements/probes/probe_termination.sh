#!/bin/sh
# probe_termination.sh — R21 E-2's ruling, checked two ways.
#
# The ruling: a BOUNDED repeat takes NO empty-iteration guard; only `rmax ==
# -1` does. The design note's S6 argues that a counter loop keeps this safe
# because the counter's increase, not the byte consumed, is what bounds the
# iteration count. Two things are checked here, and they are different claims:
#
#   (1) the emitter really does omit the guard for bounded repeats and really
#       does emit one for the unbounded nullable case -- read out of
#       `--emit-ir`'s SLOTS section, which is written by the emitter's own
#       walk;
#   (2) the SEMANTICS of an empty-capable bounded body agree with python3
#       `re`, which is what makes the omission correct rather than merely
#       intentional.
#
# (2) is a BASE-TIER oracle check, not the three-way sweep S5 specifies.
set -u
BIN=${BREP_BIN:-build/pcrec}

BOUNDED='(a?){0,4}b (a*){0,3}b ((?:a|)){2,4}b (b*){1,3}c (|a){0,3}b ((a)|){0,2}b'
UNBOUNDED='(a?)*b (a*)*b ((?:a|))*b (|a)*b'

echo "=== (1) guard slots, from --emit-ir's own SLOTS section ==="
printf 'pattern\tbound\tguard_present\n'   # 0, or a nonzero line count: presence, not a slot count
for p in $BOUNDED; do
    g=$("$BIN" --emit-ir --engine=vm -- "$p" 2>&1 |
        grep -c 'empty-iteration guard slot' || true)
    n=$("$BIN" --emit-ir --engine=vm -- "$p" 2>&1 |
        grep -c 'no empty-iteration guard slots' || true)
    printf '%s\tbounded\t%s\n' "$p" "$([ "$n" -gt 0 ] && echo 0 || echo "$g")"
done
for p in $UNBOUNDED; do
    n=$("$BIN" --emit-ir --engine=vm -- "$p" 2>&1 |
        grep -c 'no empty-iteration guard slots' || true)
    g=$("$BIN" --emit-ir --engine=vm -- "$p" 2>&1 |
        grep -c 'guard' || true)
    printf '%s\tunbounded\t%s\n' "$p" "$([ "$n" -gt 0 ] && echo 0 || echo "$g")"
done

echo
echo "=== (2) the same patterns against python3 re ==="
python3 - "$BOUNDED" "$UNBOUNDED" <<'PY'
import re, subprocess, sys, os, tempfile
pats = (sys.argv[1] + " " + sys.argv[2]).split()
subs = ["", "b", "ab", "aab", "aaab", "aaaab", "aaaaab", "ba", "c", "bc",
        "bbc", "abc", "xaab", "aaaaaaaab"]
bad = 0
tmp = tempfile.mkdtemp()
BIN = os.environ.get("BREP_BIN", "build/pcrec")
for p in pats:
    src = os.path.join(tmp, "m.c")
    r = subprocess.run([BIN, "-p", "rx", "--emit-main", "--engine=vm",
                        "-o", src, "--", p], capture_output=True, text=True)
    if r.returncode != 0:
        print("REFUSED\t%s\t%s" % (p, r.stderr.strip()[:80])); bad += 1; continue
    b = os.path.join(tmp, "m")
    c = subprocess.run(["gcc", "-O1", "-w", "-std=gnu11", "-o", b, src],
                       capture_output=True, text=True, timeout=120)
    if c.returncode != 0:
        print("CCFAIL\t%s" % p); bad += 1; continue
    rx = re.compile(p)
    for s in subs:
        m = rx.search(s)
        want = "no match" if m is None else "%d %d" % m.span()
        got = subprocess.run([b, s], capture_output=True, text=True,
                             timeout=30).stdout.strip()
        # the emitted main prints its own wording; compare the span numbers
        nums = [t for t in got.replace(",", " ").split() if t.lstrip("-").isdigit()]
        gotspan = " ".join(nums[:2]) if nums else "no match"
        if want != gotspan:
            print("DIVERGE\t%r\tsubject=%r\tpython=%r\tpcrec=%r"
                  % (p, s, want, got)); bad += 1
print("# divergences: %d over %d patterns x %d subjects"
      % (bad, len(pats), len(subs)))
PY
