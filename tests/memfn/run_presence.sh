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
#     present (K35). Read off the emitted text, not off the emitter. The
#     same order on the DFA's ATTEMPT route (`(?m)^`, `RX_DFA_SCAN
#     "attempt"`, b3brev finding 7): in `rx_search`, the verdict before the
#     first `for (start = `. A NEGATIVE CONTROL plants the reorder into a
#     copy of each witness's text (the pre-check statement moved after the
#     attempt's marker) and requires the same check to report it, so the
#     order test is shown able to fail (b3brev finding 7).
#  C. THE DENIES' ANSWERS (b3brev finding 2): B3b removed req_site_define's
#     internal-error guard against a handoff pre-check with a part after its
#     landmark, because `--memfn=no-fd-pres-pick` (P9) now puts such parts on
#     handoff sites, and argued their soundness in its header. The harness runs
#     tests/litscan/presence_deny.rxt (the argument's witnesses, oracle-written
#     by gen_presence_deny.py) and K65/K66's files under each of the three new
#     denies, and handoff.rxt under P9, the one that moves handoff sites; all
#     must pass. Its REACH (K35): at least 8 of presence_deny.rxt's patterns
#     must MOVE under P9 (9 at the lane), or the file stops witnessing the
#     parts it is about.
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
# (D172 S3: the fixed-width witnesses `é{2}cat` and `a{3}(?i:cat)` became
# `cover`, which runs no pre-check; a variable count keeps their route)
WIT = [([], "é{2,3}cat"), (["--engine=vm"], "é{2,3}cat"), (["-e", "utf8"], "a{3,4}(?i:cat)"),
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
def order_reason(t, kind):
    """None where the presence verdict precedes the first attempt; else why
    not. In the search function's own body (to its closing `}` at column 0),
    EVERY line of the entry's verdict comes before the first attempt: "vm",
    each `memchr(subject + search_from` before the first `ctx.pos = `; "dfa",
    each verdict (the byte's memchr, the run's `_reqrun(...search_from)`)
    before the first `for (start = `. Every occurrence, not the first one: a
    verdict split around the attempt is the defect too (the negative control
    moves ONE line)."""
    if kind == "vm":
        if '#define RX_VM_PREFILTER "none"' not in t:
            return "not a no-DFA VM artifact"
        run = t.find("_search_run(const unsigned char")
        pres, att = ["memchr(subject + search_from"], "ctx.pos = "
    else:
        if '#define RX_DFA_SCAN "attempt"' not in t:
            return "not a DFA attempt-route artifact"
        run = t.find("int rx_search(const unsigned char")
        pres, att = ["memchr(subject + search_from", "_reqrun(subject, subject_length, search_from)"], "for (start = "
    if run < 0:
        return "no search body"
    end = t.find("\n}\n", run)
    body = t[run:end if end >= 0 else len(t)]
    hits = [i for p in pres for i in range(len(body)) if body.startswith(p, i)]
    a = body.find(att)
    if not hits or a < 0:
        return "no pre-check or no attempt (K35)"
    if max(hits) > a:
        return "ORDER: a part of the presence verdict follows the first attempt"
    return None

def plant(t, kind):
    """The negative control's text: the pre-check's first statement line moved
    to just after the attempt marker's line (a reordered artifact)."""
    lines = t.split("\n")
    run = next(i for i, l in enumerate(lines) if ("_search_run(const unsigned char" if kind == "vm"
                                                  else "int rx_search(const unsigned char") in l)
    pi = next(i for i in range(run, len(lines)) if "memchr(subject + search_from" in lines[i]
              or "_reqrun(subject, subject_length, search_from)" in lines[i])
    ai = next(i for i in range(run, len(lines)) if ("ctx.pos = " if kind == "vm" else "for (start = ") in lines[i])
    moved = lines.pop(pi)
    if ai > pi:
        ai -= 1
    lines.insert(ai + 1, moved)
    return "\n".join(lines)

PR8 = [("vm", [], "(x?)([a-z]+)+Z.@\\1"), ("vm", [], "(?m)^(x?)([a-z]+)+Z.@\\1"),
       ("vm", ["-e", "utf8"], "(?m)^(x?)([a-z]+)+Z.@\\1"),
       ("dfa", [], "(?m)^ab[a-z]*@"), ("dfa", ["-e", "utf8"], "(?m)^ab[a-z]*@"),
       ("dfa", [], "(?m)^x{2,5}(?i:cat)")]
nb = nneg = 0
for i, (kind, fl, pat) in enumerate(PR8):
    t = art("p%d" % i, fl, pat)
    if t is None:
        fail("[pr8] %s %s: refused" % (" ".join(fl), pat)); continue
    t = t.decode("utf-8", "replace")
    why = order_reason(t, kind)
    if why:
        fail("[pr8] %s %s %s: %s" % (kind, " ".join(fl), pat, why))
        continue
    nb += 1
    good("[pr8] %s %s %s: the verdict precedes the first attempt" % (kind, " ".join(fl), pat))
    nw = order_reason(plant(t, kind), kind)
    if nw and nw.startswith("ORDER"):
        nneg += 1
        good("[pr8-negative] %s %s %s: a planted reorder is reported" % (kind, " ".join(fl), pat))
    else:
        fail("[pr8-negative] %s %s %s: a planted reorder is NOT reported (%s)"
             % (kind, " ".join(fl), pat, nw))
(good if nb == len(PR8) else fail)("[pr8-population] %d of %d witnesses" % (nb, len(PR8)))
(good if nneg == len(PR8) else fail)("[pr8-negative-population] %d of %d planted reorders reported"
                                     % (nneg, len(PR8)))

# C
harness = os.path.join(tree, "tests", "harness", "run.sh")
base = [os.path.join(tree, "tests", f) for f in
        ("litscan/presence_deny.rxt", "base/k65_precheck_whole_set.rxt", "base/k66_precheck_whole_run.rxt")]
for deny in ("no-fd-pres-pick", "no-fd-pres-g1", "no-pres-set-lead"):
    files = base + ([os.path.join(tree, "tests", "litscan", "handoff.rxt")] if deny == "no-fd-pres-pick" else [])
    r = subprocess.run(["bash", harness] + files, capture_output=True, text=True, timeout=1800,
                       env=dict(os.environ, PCREC=pcrec, RXTFLAGS="--memfn=" + deny))
    out = r.stdout + r.stderr
    def num(k):
        m = [l for l in out.splitlines() if l.startswith("cases %s:" % k)]
        return int(m[-1].split(":")[1]) if m else -1
    p, f = num("passed"), num("failed")
    if r.returncode or f != 0 or p <= 0:
        fail("[deny-answers] --memfn=%s: rc %d, cases passed %d failed %d" % (deny, r.returncode, p, f))
        for l in [l for l in out.splitlines() if "FAIL" in l][:10]:
            print("    " + l)
    else:
        good("[deny-answers] --memfn=%s: %d cases over %d files, 0 failed" % (deny, p, len(files)))
pats = []
for l in open(base[0], encoding="utf-8", errors="surrogateescape"):
    if l.startswith("pattern "):
        pats.append([l[8:].rstrip("\n"), "byte"])
    elif l.startswith("encoding ") and pats:
        pats[-1][1] = l.split()[1]
nmove = 0
for i, (pat, enc) in enumerate(pats):
    d = art("cd%d" % i, ["-e", enc], pat.encode("utf-8", "surrogateescape"))
    q = art("cq%d" % i, ["-e", enc, "--memfn=no-fd-pres-pick"], pat.encode("utf-8", "surrogateescape"))
    nmove += d is not None and q is not None and d != q
(good if nmove >= 8 else fail)("[deny-answers-reach] %d of %d presence_deny.rxt patterns move under P9 (floor 8)"
                               % (nmove, len(pats)))
print("checks passed: %d" % ok)
print("checks failed: %d" % bad)
sys.exit(1 if bad else 0)
PY
