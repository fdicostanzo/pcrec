#!/usr/bin/env python3
"""tests/encseam/findall_oracle.py — the python3 `re` oracle for the find-all
protocol of docs/spec/match_api.md §3.1.

Reads TAB-separated CLASS/PATTERN/SUBJECT cases on stdin (findall_cases.txt's
format, comments and blank lines skipped) and writes, per case, two answers:

    F <spans>   what `re.finditer` reports
    P <spans>   what §3.1's protocol reports

WHY TWO. The spec's find-all loop is NOT `re.finditer`: an artifact that
reports an empty match cannot be asked to retry the same position under
"empty match not permitted here" (PCRE2_NOTEMPTY_ATSTART), which is what
finditer's engine does, so for an empty-PREFERRING pattern the protocol is
knowingly LOSSY. Comparing pcrec against finditer alone would therefore
either fail the honest cases or force the check to accept any difference at
all. Two answers keep both halves checkable: pcrec must equal P exactly, and
the case's declared CLASS (exact / lossy) must hold between P and F.

WHAT MAKES `P` AN ORACLE RATHER THAN A COPY OF THE IMPLEMENTATION. The
matching is python's — `re.search(subject, pos)` is a completely independent
leftmost-first engine, and every span in P comes from it. What this file
shares with the artifact under test is the LOOP RULE, which is the spec text
being verified, not the code being verified. The C side reaches its advance
through the compiled `<prefix>_next_pos` residual; this side spells the same
rule as `+ 1`, and under the byte encoding those must agree — which is the
[M5-SEAM] claim.
"""
import re
import sys


def protocol(rx, s):
    """docs/spec/match_api.md §3.1's loop, with python `re` as the matcher."""
    out = []
    p = 0
    n = len(s)
    while p <= n:
        m = rx.search(s, p)
        if not m:
            break
        out.append((m.start(), m.end()))
        # The advance is off the MATCH's own start, not off the loop
        # variable: an empty match can be found later than the position
        # searched from.
        p = m.end() if m.end() > m.start() else m.start() + 1
    return out


def render(spans):
    return " ".join("%d,%d" % (a, b) for a, b in spans)


def main():
    for line in sys.stdin:
        line = line.rstrip("\n")
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) == 2:          # a case with an EMPTY subject
            parts.append("")
        if len(parts) != 3:
            sys.stderr.write("findall_oracle: malformed case: %r\n" % line)
            return 2
        cls, pat, subj = parts
        rx = re.compile(pat)
        print("F %s" % render([(m.start(), m.end()) for m in rx.finditer(subj)]))
        print("P %s" % render(protocol(rx, subj)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
