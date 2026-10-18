#!/usr/bin/env bash
# tests/memfn/run_presence.sh — [MEMFN] R17-b' B3b's light checks on the
# ROUTED presence decision, at the pcrec level (lane b3b; docs/design/memfn/
# r17b_prime.md rev 3 §3.1 row B3b). Run by run_finder.sh as part `presence`.
#
#  A. THE ALIAS (Q-R17P-19; the kit manager's Q-19, binding: PCREC_NO_REQ_SET_LEAD
#     stays a WORKING alias of the kit's deny, never a silent no-op). For each
#     witness, the artifact under `-fno-req-set-lead` (the CLI spelling of bit
#     45, which the library rewrites) is BYTE-IDENTICAL to the one under
#     `--memfn=no-pres-set-lead`, and both DIFFER from the default (the deny
#     acts there: K35); and the alias composes with another kit option
#     (`--memfn=no-fd-d1` beside it equals `--memfn=no-fd-d1,no-pres-set-lead`).
#     The expectation is the kit deny's own artifact, never the alias's code.
#  B. PR-8 (§4.4, window_contract §2.4): on the route with no DFA scan (a
#     backreference declines the hybrid; W1, and W2 under `(?m)^`), the
#     presence verdict precedes the first attempt: in the artifact's
#     `_search_run`, the pre-check's first `memchr(subject + search_from`
#     line comes before the first `ctx.pos =` (the attempt's start), both
#     present (K35). Read off the emitted text, not off the emitter.
#
# Usage: bash tests/memfn/run_presence.sh [TREE]   (needs TREE/build/pcrec)
set -u
export LC_ALL=C
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TREE="$(cd "${1:-$SCRIPT_DIR/../..}" && pwd)"
WORK="$(mktemp -d "${TMPDIR:-/tmp}/presence.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT
python3 -I - "$TREE" "$WORK" <<'PY'
import os, subprocess, sys
tree, work = sys.argv[1:3]
pcrec = os.path.join(tree, "build", "pcrec")
ok = bad = 0

def good(m):
    global ok
    ok += 1
    print("PASS: " + m)

def fail(m):
    global bad
    bad += 1
    print("FAIL: " + m)

def art(tag, flags, pat):
    d = os.path.join(work, tag)
    os.makedirs(d, exist_ok=True)
    o = os.path.join(d, "o.c")
    r = subprocess.run([pcrec, "-p", "rx", "--features", "all"] + flags + ["-o", o, "--pattern", pat],
                       capture_output=True, timeout=60)
    if r.returncode:
        return None
    return open(o, "rb").read()

# A
WIT = [([], "é{2}cat"), (["--engine=vm"], "é{2}cat"), (["-e", "utf8"], "a{3}(?i:cat)"),
       ([], "(?:user|USER)[ \\t]*="), (["-e", "byte"], "(x?)([a-z]+)+Z.@#\\1")]
na = 0
for i, (fl, pat) in enumerate(WIT):
    a = art("a%d" % i, fl + ["-fno-req-set-lead"], pat)
    b = art("b%d" % i, fl + ["--memfn=no-pres-set-lead"], pat)
    d = art("d%d" % i, fl, pat)
    c1 = art("c%d" % i, fl + ["--memfn=no-fd-d1", "-fno-req-set-lead"], pat)
    c2 = art("e%d" % i, fl + ["--memfn=no-fd-d1,no-pres-set-lead"], pat)
    if None in (a, b, d, c1, c2):
        fail("[alias] %s %s: a compile was refused" % (" ".join(fl), pat)); continue
    if a != b:
        fail("[alias] %s %s: -fno-req-set-lead's artifact is not --memfn=no-pres-set-lead's"
             % (" ".join(fl), pat))
    elif a == d:
        fail("[alias] %s %s: the deny moves nothing here (not a witness: K35)" % (" ".join(fl), pat))
    elif c1 != c2:
        fail("[alias] %s %s: the alias beside another kit option is not the joined deny"
             % (" ".join(fl), pat))
    else:
        na += 1
        good("[alias] %s %s: -fno-req-set-lead == --memfn=no-pres-set-lead != default, and composes"
             % (" ".join(fl), pat))
(good if na >= 4 else fail)("[alias-population] %d alias witnesses (floor 4)" % na)

# B
PR8 = [([], "(x?)([a-z]+)+Z.@\\1"), ([], "(?m)^(x?)([a-z]+)+Z.@\\1"),
       (["-e", "utf8"], "(?m)^(x?)([a-z]+)+Z.@\\1")]
nb = 0
for i, (fl, pat) in enumerate(PR8):
    t = art("p%d" % i, fl, pat)
    if t is None:
        fail("[pr8] %s %s: refused" % (" ".join(fl), pat)); continue
    t = t.decode("utf-8", "replace")
    run = t.find("_search_run(const unsigned char")
    body = t[run:] if run >= 0 else ""
    pre = body.find("memchr(subject + search_from")
    att = body.find("ctx.pos = ")
    if '#define RX_VM_PREFILTER "none"' not in t or run < 0 or pre < 0 or att < 0:
        fail("[pr8] %s %s: not a no-DFA VM artifact with a pre-check and an attempt (K35)"
             % (" ".join(fl), pat))
    elif pre > att:
        fail("[pr8] %s %s: the first attempt precedes the presence verdict (PR-8)"
             % (" ".join(fl), pat))
    else:
        nb += 1
        good("[pr8] %s %s: the verdict precedes the first attempt" % (" ".join(fl), pat))
(good if nb == len(PR8) else fail)("[pr8-population] %d of %d witnesses" % (nb, len(PR8)))
print("checks passed: %d" % ok)
print("checks failed: %d" % bad)
sys.exit(1 if bad else 0)
PY
