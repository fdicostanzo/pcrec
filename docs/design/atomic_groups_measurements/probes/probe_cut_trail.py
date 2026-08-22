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
        outs = {}
        for arm, flags in (("ok", []), ("sab", ["-DCUT_REWINDS_TRAIL"])):
            exe = os.path.join(td, "cut_proto_" + arm)
            cc = subprocess.run(["gcc", "-O2", "-Wall", "-Wextra", "-std=gnu11"]
                                + flags + ["-o", exe, src],
                                capture_output=True, text=True)
            if cc.returncode != 0:
                print("COMPILE FAILED (%s arm) — this probe reports NOTHING "
                      "rather than zero:" % arm)
                print(cc.stderr)
                return 1
            if cc.stderr.strip():
                print("compiler diagnostics, %s arm (kept: a warning here is a "
                      "finding):" % arm)
                print(cc.stderr)
            outs[arm] = subprocess.run([exe], capture_output=True,
                                       text=True).stdout
        out = outs["ok"]
        sab = {}
        for line in outs["sab"].splitlines():
            if line.startswith("PROTO\t"):
                _, pat, subj, got = line.split("\t")
                sab[(pat, subj)] = got

    print("libpcre2:", P.version())
    print("gcc     :", subprocess.run(["gcc", "-dumpversion"],
                                      capture_output=True, text=True).stdout.strip())
    print()
    hdr = ("%-22s %-8s %-20s %-20s %-6s %-20s %-9s %s"
           % ("PATTERN", "SUBJECT", "PROTOTYPE", "LIBPCRE2 (oracle)", "AGREE",
              "UNCUT TWIN", "cut-vs-", "TRAIL-"))
    print(hdr)
    print("-" * len(hdr))
    print("%-22s %-8s %-20s %-20s %-6s %-20s %-9s %s"
          % ("", "", "", "", "", "(control)", "uncut", "REWIND"))
    rows = 0
    bad = 0
    vacuous = 0
    disc_trail = 0
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
        st = sab.get((pat, subj))
        trail_disc = (st is not None and st != got)
        if trail_disc:
            disc_trail += 1
        print("%-22s %-8s %-20s %-20s %-6s %-20s %-9s %s"
              % (pat, subj, got, want, "yes" if ok else "**NO**", u,
                 "yes" if differs else "no",
                 "**YES**" if trail_disc else "no"))
    print()
    print("rows: %d   disagreeing with libpcre2: %d" % (rows, bad))
    print("rows discriminating CUT-vs-UNCUT      : %d" % (rows - vacuous))
    print("rows discriminating THE TRAIL INVARIANT: %d  (built with "
          "-DCUT_REWINDS_TRAIL and diffed row by row)" % disc_trail)
    print()
    print("R31 C6: THESE ARE DIFFERENT AXES AND THE FIRST REVISION CONFLATED")
    print("THEM. A row can be 'vacuous' on the cut-vs-uncut axis and be the")
    print("only thing standing between CUT-INV and a silent capture loss. The")
    print("suite needs a non-zero count in BOTH columns, and reports both.")
    if rows == 0:
        print("VERDICT: the prototype produced NO rows. This probe reports "
              "nothing rather than success.")
        return 1
    if bad:
        print("VERDICT: the proposed lowering DIVERGES from PCRE2 on %d row(s)." % bad)
        return 1
    if vacuous == rows:
        print("VERDICT: every row is vacuous on the cut axis — this suite would "
              "pass with RX_CUT deleted and proves nothing.")
        return 1
    if disc_trail == 0:
        print("VERDICT: NO row discriminates the trail invariant — this suite "
              "would pass with a trail-rewinding cut, which is the exact thing "
              "CUT-INV claims is wrong. It proves nothing about §3.1.")
        return 1
    print("VERDICT: the proposed lowering reproduces PCRE2 on all %d rows; %d "
          "discriminate CUT-vs-UNCUT and %d discriminate the TRAIL INVARIANT, "
          "so both of §3's claims are load-bearing in this measurement."
          % (rows, rows - vacuous, disc_trail))
    return 0


sys.exit(main())
