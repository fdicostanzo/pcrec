#!/usr/bin/env python3
"""tests/callouts/advice_check.py — the `once` ADVICE, checked against what
the patterns actually match ([INLINE-C] 1b advice; docs/spec/match_api.md
§11.8¶3).

A `once` refusal names the live construct, its fix, and a VERDICT on that
fix: it does not change what the pattern matches (PROVEN SAME), it loses a
match on a subject the refusal prints (PROVEN CHANGES), or it may (UNPROVEN).
A lazy quantifier is offered no seal at all. pcrec derives the verdict; this
program checks it against libpcre2 10.46 (co_oracle.c, the answer-moving
optimizations off), which shares no code with pcrec's analysis. Per row:

  1. the refusal names the construct and the row's verdict (and a lazy row
     names none), and the `--emit-ir` note of the site without `once` is
     inside the refusal;
  2. every fix compiles with `once`, and no ATTEMPT (rx_match anchored at
     each start) fires its site more than once (advice_drv.c);
  3. the fix's matches against the pattern as written, callouts removed,
     searched from every start of every subject over the row's alphabet up
     to length 5 (4 for four letters), plus any witness: EQUAL when the row
     pins `same`, DIFFERENT somewhere when it pins `differs`. Every
     relation pinned here was read off libpcre2, for every verdict,
     UNPROVEN rows included, so an UNPROVEN row whose fix is in fact
     harmless is visible as such;
  4. PROVEN CHANGES: the printed subject is a real witness: as written, the
     search from offset 0 matches AT 0; with the fix it does not.

`@` in a row is the site: `(?C"x,once")` for pcrec, `(?C"x")` for the
listing, nothing for libpcre2.

Usage: advice_check.py --pcrec PCREC --work DIR [--cc CC]
Exit 0 green, 1 on any failure (or an empty population), 3 only when
libpcre2 itself is absent (`build_oracle`'s rule).
"""
import argparse
import itertools
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from verify_callouts import build_oracle  # noqa: E402

VERDICT = {
    "same": "that does not change what it matches",
    "changes": "that loses a match",
    "unproven": "that may change what it matches",
}
DEF = "(?(DEFINE)(?<w>a+))"

# pattern, construct, verdict (or `noseal`), alphabet, [(fix, relation)]
ROWS = [
    # the quantifier
    ("a+@ab", "the quantifier", "changes", "ab",
     [("a++@ab", "differs"), ("(?>a+)@ab", "differs")]),
    ("a+@b", "the quantifier", "same", "abc",
     [("a++@b", "same"), ("(?>a+)@b", "same")]),
    ("a+@a*b", "the quantifier", "unproven", "ab", [("a++@a*b", "same")]),
    ("x(a*)@ab", "the quantifier", "changes", "xab", [("x(a*+)@ab", "differs")]),
    ("a{2,5}@ab", "the quantifier", "changes", "ab", [("a{2,5}+@ab", "differs")]),
    ("(?:ab)+@abc", "the quantifier", "changes", "abc",
     [("(?:ab)++@abc", "differs")]),
    ("[a-c]+@b", "the quantifier", "changes", "abc", [("[a-c]++@b", "differs")]),
    ("\\w+@", "the quantifier", "same", "a-", [("\\w++@", "same")]),
    ("(\\d+)@x", "the quantifier", "same", "1x", [("(\\d++)@x", "same")]),
    # the lazy quantifier: no seal is offered
    ("a+?@b", "the lazy quantifier", "noseal", "ab",
     [("(?>a+?)@b", "differs"), ("a++@b", "same")]),
    ("a*?@ab", "the lazy quantifier", "noseal", "ab",
     [("a*+@ab", "differs"), ("(?>a*?)@ab", "differs")]),
    # the alternation
    ("(?:a|ab)@c", "the alternation", "changes", "abc",
     [("(?>a|ab)@c", "differs")]),
    ("(?:a|b)@c", "the alternation", "same", "abc", [("(?>a|b)@c", "same")]),
    ("(?:a|ab|abc)@d", "the alternation", "changes", "abcd",
     [("(?>a|ab|abc)@d", "differs")]),
    ("^(?:ab|a)@bc\\z", "the alternation", "changes", "abc",
     [("^(?>ab|a)@bc\\z", "differs")]),
    ("(?:a|ab)@b*c", "the alternation", "unproven", "abc",
     [("(?>a|ab)@b*c", "same")]),
    # the subroutine call: the survey does not model a call, so never SAME
    (DEF + "(?&w)@ab", "the subroutine call", "changes", "ab",
     [(DEF + "(?>(?&w))@ab", "differs")]),
    (DEF + "(?&w)@b", "the subroutine call", "unproven", "ab",
     [(DEF + "(?>(?&w))@b", "same")]),
    # the non-atomic lookaround: no proof models it, so always UNPROVEN
    ("(?*(a+))@\\1ab", "the non-atomic lookaround", "unproven", "ab",
     [("(?=(a+))@\\1ab", "differs"), ("(?>(?*(a+)))@\\1ab", "differs")]),
    ("(?*a+)@a+c", "the non-atomic lookaround", "unproven", "ac",
     [("(?=a+)@a+c", "same"), ("(?>(?*a+))@a+c", "same")]),
    ("(?<*a|b)@c", "the non-atomic lookaround", "unproven", "abc",
     [("(?<=a|b)@c", "same"), ("(?>(?<*a|b))@c", "same")]),
]

# Every (construct, verdict) the rows must reach: each verdict for each row
# kind that can reach it. A call is never PROVEN SAME and a lookaround is
# only UNPROVEN (neither proof models them; match_api.md §11.8¶3).
REACH = {
    ("the quantifier", "same"), ("the quantifier", "changes"),
    ("the quantifier", "unproven"), ("the lazy quantifier", "noseal"),
    ("the alternation", "same"), ("the alternation", "changes"),
    ("the alternation", "unproven"), ("the subroutine call", "changes"),
    ("the subroutine call", "unproven"),
    ("the non-atomic lookaround", "unproven"),
}

WITNESS = re.compile(r'\(offset 0 of "((?:[^"\\]|\\x\{[0-9a-f]+\})*)"\)')


def site(p, how):
    return p.replace("@", {"once": '(?C"x,once")', "plain": '(?C"x")',
                           "none": ""}[how])


def unwit(s):
    return re.sub(r"\\x\{([0-9a-f]+)\}", lambda m: chr(int(m.group(1), 16)), s)


def subjects(alpha):
    top = 4 if len(alpha) > 3 else 5
    for n in range(top + 1):
        for t in itertools.product(alpha, repeat=n):
            yield "".join(t)


def searches(oracle, pat, subs):
    """libpcre2's search from every start of every subject: a list of
    (subject, start, answer) with answer the group-0 span or None."""
    q = []
    ph = pat.encode("latin-1").hex()
    for s in subs:
        for st in range(len(s) + 1):
            q.append((s, st))
    inp = "".join("%s\t%s\t%d\n" % (ph, s.encode("latin-1").hex(), st)
                  for s, st in q)
    out = subprocess.run([oracle], input=inp, capture_output=True, text=True,
                         timeout=600).stdout.splitlines()
    if len(out) != len(q):
        raise RuntimeError("co_oracle answered %d of %d" % (len(out), len(q)))
    res = []
    for (s, st), line in zip(q, out):
        f = line.split()
        if f[0] == "error":
            raise RuntimeError("co_oracle: %s on %r" % (line, pat))
        res.append((s, st, (int(f[1]), int(f[2])) if f[0] == "match" else None))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pcrec", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--cc", default=os.environ.get("CC", "gcc"))
    a = ap.parse_args()
    os.makedirs(a.work, exist_ok=True)
    oracle = os.path.join(a.work, "co_oracle")
    rc, why = build_oracle(a.cc, oracle)
    if rc:
        print("%s: advice_check: %s" % ("FAIL" if rc == 1 else "SKIP", why))
        return rc

    npass = nfail = 0
    seen = set()

    def ok(m):
        nonlocal npass
        npass += 1
        print("PASS: " + m)

    def bad(m):
        nonlocal nfail
        nfail += 1
        print("FAIL: " + m)

    def pcrec(*args):
        return subprocess.run([a.pcrec, "--features", "all"] + list(args),
                              capture_output=True, text=True, timeout=60)

    for i, (pat, what, verdict, alpha, fixes) in enumerate(ROWS):
        seen.add((what, verdict))
        # 1. the refusal and the listing note
        r = pcrec("-o", os.path.join(a.work, "r.c"), "--pattern", site(pat, "once"))
        msg = r.stderr.strip()
        if r.returncode == 0 or not re.search(re.escape(what) + r" at offset \d+", msg):
            bad("%s: want a refusal naming %s, got rc %d: %s" % (pat, what, r.returncode, msg))
            continue
        named = [v for v, t in VERDICT.items() if t in msg]
        want = [] if verdict == "noseal" else [verdict]
        if named != want:
            bad("%s: want verdict %s, the refusal says %s: %s" % (pat, want or "none", named or "none", msg))
        else:
            ok("%s: the refusal names %s and %s" % (pat, what, verdict))
        ir = pcrec("--emit-ir", "--pattern", site(pat, "plain"))
        note = None
        sec = False
        for line in ir.stdout.splitlines():
            if line.startswith("#section"):
                sec = line == "#section callouts"
            elif sec and not line.startswith("#"):
                note = line.split("\t")[6]
                break
        if note and note in msg:
            ok("%s: the listing note is the refusal's text" % pat)
        else:
            bad("%s: the listing note %r is not inside the refusal %r" % (pat, note, msg))
        wit = None
        if verdict == "changes":
            m = WITNESS.search(msg)
            if not m:
                bad("%s: PROVEN CHANGES with no witness subject: %s" % (pat, msg))
                continue
            wit = unwit(m.group(1))
        subs = list(subjects(alpha)) + ([wit] if wit is not None else [])
        try:
            base = searches(oracle, site(pat, "none"), subs)
        except RuntimeError as e:
            bad("%s: %s" % (pat, e))
            continue
        for j, (fix, rel) in enumerate(fixes):
            # 2. the fix compiles with `once` and fires at most once per attempt
            d = os.path.join(a.work, "f%d_%d" % (i, j))
            os.makedirs(d, exist_ok=True)
            r = pcrec("-p", "rx", "-o", os.path.join(d, "a.c"), "--pattern", site(fix, "once"))
            if r.returncode != 0:
                bad("%s: the fix %s is refused: %s" % (pat, fix, r.stderr.strip()))
                continue
            b = subprocess.run([a.cc, "-O1", "-std=gnu11", "-w", "-I", d, "-o",
                                os.path.join(d, "m"), os.path.join(HERE, "advice_drv.c"),
                                os.path.join(d, "a.c")], capture_output=True, text=True)
            if b.returncode != 0:
                bad("%s: the fix %s did not build: %s" % (pat, fix, b.stderr[:300]))
                continue
            runs = subprocess.run([os.path.join(d, "m")], capture_output=True, text=True,
                                  timeout=120, input="".join(
                                      s.encode("latin-1").hex() + "\n" for s in subs))
            most = [int(x.split()[1]) for x in runs.stdout.splitlines()]
            if len(most) != len(subs) or max(most) > 1:
                bad("%s: the fix %s fired %s times in one attempt (%d of %d subjects read)" % (
                    pat, fix, max(most) if most else "?", len(most), len(subs)))
            else:
                ok("%s: the fix %s compiles and fires at most once per attempt over %d subjects" % (pat, fix, len(subs)))
            # 3. the fix's matches against the pattern as written
            got = searches(oracle, site(fix, "none"), subs)
            diff = [(x[0], x[1], x[2], y[2]) for x, y in zip(base, got)
                    if x[2] != y[2]]
            if (rel == "same") == (not diff):
                ok("%s: the fix %s matches %s over %d searches%s" % (
                    pat, fix, "the same" if rel == "same" else "differently",
                    len(base), "" if not diff else " (first: %r from %d: %s vs %s)" % diff[0]))
            else:
                bad("%s: the fix %s pinned %s, libpcre2 reads %s%s" % (
                    pat, fix, rel, "differs" if diff else "same",
                    "" if not diff else ": %r from %d: %s vs %s" % diff[0]))
            # 4. the witness is real
            if wit is not None:
                w0 = [x[2] for x in base if x[0] == wit and x[1] == 0][0]
                f0 = [x[2] for x in got if x[0] == wit and x[1] == 0][0]
                if w0 and w0[0] == 0 and not (f0 and f0[0] == 0):
                    ok("%s: the witness %r matches at 0 as written (%s) and not with %s (%s)" % (pat, wit, w0, fix, f0))
                else:
                    bad("%s: the witness %r is not one for %s: as written %s, fixed %s" % (pat, wit, fix, w0, f0))
    print("verdicts reached: %s" % ", ".join("%s/%s" % k for k in sorted(seen)))
    if seen != REACH:
        bad("the rows reach %s, the declared set is %s" % (
            sorted(seen - REACH) or "nothing extra", sorted(REACH - seen) or "all"))
    print("advice checks passed: %d, failed: %d" % (npass, nfail))
    if npass == 0:
        print("FAIL: advice_check: nothing was checked")
        return 1
    return 1 if nfail else 0


if __name__ == "__main__":
    sys.exit(main())
