"""probe_cut_trail.py — PROTOTYPE, checked against libpcre2.

[M6.4.1] §3. Compiles and runs `cut_proto.c` — five atomic patterns hand-
lowered onto the EMITTED VM's own frame/trail machinery, the macros copied
verbatim from a real artifact — and checks every row against libpcre2 10.46.

WHAT A GREEN RUN MEANS, stated narrowly. It means the lowering SHAPE the
design proposes (mark before the first push; ordinary backtracking inside the
body; one RX_CUT at the body's exit; NO trail rewind at the cut) computes
PCRE2's answers for these cells, INCLUDING the two the whole no-trail-rewind
question turns on:

  - `(?>(a)|ab)` on "ab"        -> group 1 RETAINED across the cut, (0,1)
  - `((?>(a)|ab))c|(abc)` on "abc" -> the cut succeeded, the CONTINUATION then
    failed, and an OUTER frame BELOW the mark had to undo the body's group
    writes. If the cut had rewound the trail, or if the outer frame's trail
    mark had been taken after the body ran, group 1 or group 3 would be wrong.

It does NOT mean the module is correct; nothing here is pcrec's code. See
cut_proto.c's header for the exclusions.

THE NEGATIVE CONTROL IS NOT OPTIONAL and is built in: the probe also runs the
five patterns' UNCUT twins through libpcre2 and reports, per row, whether the
cut actually CHANGED the answer. A row where cut and uncut agree proves
nothing about the cut, and a suite made only of those rows would pass with
RX_CUT deleted — which is the failure mode docs/design/assertions_measurements/
CLAUDE.md records for probe_startpos_context.py's own first draft.
"""
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "eng_brep_measurements", "probes"))
import pcre2_ctypes as P  # noqa: E402


def uncut(pat):
    """The twin: `(?>` -> `(?:`, a two-byte edit that touches nothing else."""
    return pat.replace("(?>", "(?:")


def pc(pat, subj, ncap):
    rx = P.compile(pat)
    r = rx.search(subj, 0)
    if r is None:
        return "nomatch"
    span, groups = r
    groups = tuple(groups) + (None,) * max(0, ncap - len(groups))
    s = "(%d,%d)" % span
    for g in groups[:ncap]:
        s += " -" if g is None else " (%d,%d)" % g
    return s


def main():
    src = os.path.join(HERE, "cut_proto.c")
    with tempfile.TemporaryDirectory() as td:
        exe = os.path.join(td, "cut_proto")
        cc = subprocess.run(["gcc", "-O2", "-Wall", "-Wextra", "-std=gnu11",
                             "-o", exe, src], capture_output=True, text=True)
        if cc.returncode != 0:
            print("COMPILE FAILED — this probe reports NOTHING rather than zero:")
            print(cc.stderr)
            return 1
        if cc.stderr.strip():
            print("compiler diagnostics (kept: a warning here is a finding):")
            print(cc.stderr)
        out = subprocess.run([exe], capture_output=True, text=True).stdout

    print("libpcre2:", P.version())
    print("gcc     :", subprocess.run(["gcc", "-dumpversion"],
                                      capture_output=True, text=True).stdout.strip())
    print()
    hdr = ("%-22s %-8s %-22s %-22s %-8s  %-22s %s"
           % ("PATTERN", "SUBJECT", "PROTOTYPE", "LIBPCRE2 (oracle)", "AGREE",
              "UNCUT TWIN (control)", "CUT MATTERS HERE"))
    print(hdr)
    print("-" * len(hdr))
    rows = 0
    bad = 0
    vacuous = 0
    for line in out.splitlines():
        if not line.startswith("PROTO\t"):
            continue
        _, pat, subj, got = line.split("\t")
        rows += 1
        ncap = len(re.findall(r"\((?!\?)", pat))
        want = pc(pat, subj, ncap)
        u = pc(uncut(pat), subj, ncap)
        ok = got == want
        differs = u != want
        if not ok:
            bad += 1
        if not differs:
            vacuous += 1
        print("%-22s %-8s %-22s %-22s %-8s  %-22s %s"
              % (pat, subj, got, want, "yes" if ok else "**NO**", u,
                 "yes" if differs else "no (vacuous row)"))
    print()
    print("rows: %d   disagreeing with libpcre2: %d   "
          "rows where the cut changes nothing (vacuous): %d"
          % (rows, bad, vacuous))
    if rows == 0:
        print("VERDICT: the prototype produced NO rows. This probe reports "
              "nothing rather than success.")
        return 1
    if bad:
        print("VERDICT: the proposed lowering DIVERGES from PCRE2 on %d row(s)." % bad)
        return 1
    if vacuous == rows:
        print("VERDICT: every row is vacuous — this suite would pass with "
              "RX_CUT deleted and proves nothing.")
        return 1
    print("VERDICT: the proposed lowering reproduces PCRE2 on all %d rows, "
          "and %d of them are NON-VACUOUS (the uncut twin gives a different "
          "answer), so RX_CUT is load-bearing in this measurement."
          % (rows, rows - vacuous))
    return 0


sys.exit(main())
