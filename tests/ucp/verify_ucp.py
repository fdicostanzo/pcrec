#!/usr/bin/env python3
"""Cross-verify tests/ucp's `.rxt` corpus against LIBPCRE2 with the options
each block states — this directory's own oracle (docs/spec/rxt_format.md's
"a directory may name its own oracle"; tests/assertions/verify_pcre2.py is the
precedent this follows and REUSES).

    Usage: verify_ucp.py [files-or-dirs...]      (default: tests/ucp)

WHY IT EXISTS. python `re` has no PCRE2_UCP, so the default oracle cannot
check a single cell here (verify_rxt.py skips every `flags u` block and this
directory as a whole). The committed CLI oracle (tests/fuzz/pcre2_oracle.c)
compiles at options = 0 by a project-wide pin, so the block's options travel
INSIDE the pattern, as PCRE2's own start-of-pattern verbs: `(*UTF)` for
`encoding utf8`, `(*UCP)` for `flags u`, and `(?i)` for `flags i`, placed
AFTER the pattern's own leading verb run (a verb after `(?i)` is PCRE2 error
160). Nothing here decides a semantic of its own — the spellings are PCRE2's.

WHAT IT IS NOT: a check on pcrec. tests/harness/run.sh runs pcrec against the
same cells; keeping the two apart is the point (verify_pcre2.py's header).

`perr` blocks are COUNTED and not checked: they are pcrec's capability
refusals (refusals.rxt's header), and libpcre2 accepts most of them.

SKIPS LOUDLY when libpcre2 is absent (exit 0 with a skip line).
"""
import importlib.util
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))

_spec = importlib.util.spec_from_file_location(
    "verify_pcre2", os.path.join(ROOT, "assertions", "verify_pcre2.py"))
_vp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_vp)
parse_rxt = _vp.parse_rxt

_LEAD_VERBS = re.compile(r"^(?:\(\*[A-Z0-9_]+\))*")


def oracle_pattern(pattern, encoding, flags):
    """The block's pattern with its options spelled as PCRE2 verbs/letters."""
    lead = _LEAD_VERBS.match(pattern).group(0)
    rest = pattern[len(lead):]
    pre = ""
    if encoding == "utf8":
        pre += "(*UTF)"
    if "u" in flags:
        pre += "(*UCP)"
    return pre + lead + ("(?i)" if "i" in flags else "") + rest


def check_file(binpath, workdir, path):
    npass = nfail = nperr = 0
    pattern = None
    enc = flags = ""
    perr = False
    for lineno, kind, data in parse_rxt(path):
        if kind == "pattern":
            pattern, _ = data
            enc = flags = ""
            perr = False
            continue
        if kind == "encoding":
            enc = data
            continue
        if kind == "flags":
            flags = data
            continue
        if kind == "perr":
            perr = True
            nperr += 1
            continue
        if pattern is None or perr:
            continue
        if kind == "m":
            subj, start, end = data
            want, sp = (start, end), 0
        elif kind == "n":
            subj, want, sp = data, None, 0
        elif kind == "ms":
            sp, subj, start, end = data
            want = (start, end)
        elif kind == "ns":
            sp, subj = data
            want = None
        else:
            continue
        opat = oracle_pattern(pattern, enc, flags)
        got = _vp.oracle_run(binpath, workdir, opat, subj, sp)
        if got == want:
            npass += 1
        else:
            nfail += 1
            print("FAIL %s:%d: pattern %r (oracle %r) subject %r: file says "
                  "%s, libpcre2 says %s" % (path, lineno, pattern, opat, subj,
                                           want, got))
    return npass, nfail, nperr


def main(argv):
    targets = argv[1:] or [HERE]
    files = []
    for t in targets:
        if os.path.isdir(t):
            files += [os.path.join(t, n) for n in sorted(os.listdir(t))
                      if n.endswith(".rxt")]
        else:
            files.append(t)
    if not files:
        print("verify_ucp: no .rxt files found — refusing to report a pass "
              "over an empty corpus")
        return 1
    with tempfile.TemporaryDirectory() as workdir:
        binpath = _vp.build_oracle(workdir)
        if binpath is None:
            print("verify_ucp: SKIP — libpcre2-8 is not loadable on this box, "
                  "so the UCP expectations cannot be re-verified here.")
            return 0
        tp = tf = tperr = 0
        for path in files:
            p, f, pe = check_file(binpath, workdir, path)
            print("  %-36s %4d cells agree with libpcre2%s, %d perr counted"
                  % (os.path.relpath(path, os.path.dirname(ROOT)), p,
                     "" if f == 0 else ", %d DISAGREE" % f, pe))
            tp += p; tf += f; tperr += pe
    if tp == 0:
        print("verify_ucp: 0 cells checked — the corpus has no population")
        return 1
    print("verify_ucp: %d cells agree with libpcre2, %d disagree, %d perr "
          "blocks counted (pcrec capability refusals, not checked)"
          % (tp, tf, tperr))
    return 1 if tf else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
