#!/usr/bin/env python3
"""Cross-verify a `.rxt` corpus against LIBPCRE2 — the oracle module
`assertions` has to use, because the base-tier one is WRONG here.

    Usage: verify_pcre2.py [files-or-dirs...]     (default: tests/assertions)

WHY THIS EXISTS AT ALL. CLAUDE.md's standing rule is that expectations are
oracle-verified with python3 `re`, and tests/harness/verify_rxt.py is that
oracle. For `\\Z` that rule produces WRONG expectations, silently:

    pattern   subject     PCRE2      python 3.14
    b\\Z       'ab\\n'      (1, 2)     None          <- python says NO MATCH
    a*\\Z      'aaa\\n'     (0, 3)     (4, 4)        <- and here, a wrong SPAN

**python's `\\Z` IS PCRE2's `\\z`.** python has no single escape for PCRE2's
`\\Z` at all — the only spelling is `(?=\\n?\\Z)`, which needs lookahead (a
module that does not exist yet). Both divergences are in the dangerous
direction, so a `\\Z` cell written from python would encode `\\z` and this
suite would go green on a miscompile. Measured in assertions_design.md
§3.2.1 and reproduced by this lane; every `\\Z` block in tests/assertions/
therefore carries `# pcre2-only` (which makes verify_rxt.py skip it) and is
verified HERE instead.

WHAT IT IS AND IS NOT. It is a check on the CORPUS — do these expectations
describe PCRE2? — exactly as verify_rxt.py is, with a different oracle. It is
NOT a check on pcrec: tests/harness/run.sh is what runs pcrec against these
same cells. Keeping the two apart is the point; a single script that both
generated an expectation and checked it would be a control sharing a source
with what it controls.

REUSE, deliberately: the `.rxt` parser is IMPORTED from
tests/harness/verify_rxt.py rather than copied, so there is exactly one
implementation of the file format, and the libpcre2 oracle is
tests/fuzz/pcre2_oracle.c — the committed CLI oracle PC-3 and the fuzzer
already share — rather than a third ctypes binding. This box has the PCRE2
8-bit runtime but not the -dev package, which is why that oracle dlopens a
hand-declared ABI; see tests/fuzz/pcre2_abi.h.

SKIPS LOUDLY when libpcre2 is absent (PC-3's own pattern): exit 0 with a
skip line on stdout, never a silent pass.
"""
import importlib.util
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
ORACLE_SRC = os.path.join(ROOT, "fuzz", "pcre2_oracle.c")
DEFAULT_DIR = HERE

_spec = importlib.util.spec_from_file_location(
    "verify_rxt", os.path.join(ROOT, "harness", "verify_rxt.py"))
_vr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_vr)
parse_rxt = _vr.parse_rxt


def build_oracle(workdir):
    """Build tests/fuzz/pcre2_oracle. Returns the path, or None if the
    build fails for want of libpcre2 (the SKIP case)."""
    binpath = os.path.join(workdir, "pcre2_oracle")
    cc = os.environ.get("CC", "gcc")
    r = subprocess.run([cc, "-O1", "-std=gnu11", "-Wall", "-Wextra", "-Werror",
                        "-o", binpath, ORACLE_SRC, "-ldl"],
                       capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        sys.exit("verify_pcre2: could not build the oracle:\n" + r.stderr)
    # The oracle dlopens libpcre2 at RUN time, so a successful build proves
    # nothing about availability — probe it.
    subj = os.path.join(workdir, "probe_subject")
    with open(subj, "wb") as f:
        f.write(b"a")
    r = subprocess.run([binpath, "a", subj], capture_output=True, text=True,
                       timeout=60)
    if r.returncode != 0 or not r.stdout.startswith("match"):
        return None
    return binpath


def oracle_run(binpath, workdir, pattern, subject, startpos):
    subj = os.path.join(workdir, "subject")
    with open(subj, "wb") as f:
        f.write(subject.encode("latin-1"))
    r = subprocess.run([binpath, pattern, subj, str(startpos)],
                       capture_output=True, text=True, timeout=60)
    out = r.stdout.strip()
    if out.startswith("match"):
        parts = out.split()
        return (int(parts[1]), int(parts[2]))
    if out == "nomatch":
        return None
    return "ORACLE:" + (out or r.stderr.strip() or "empty")


def check_file(binpath, workdir, path):
    npass = nfail = nflag = 0
    pattern = None
    perr = False
    flagged = False
    for lineno, kind, data in parse_rxt(path):
        if kind == "pattern":
            pattern, _ = data
            perr = False
            flagged = False
            continue
        if kind == "perr":
            perr = True
            continue
        if kind == "flags":
            # A `flags` directive puts the block OUTSIDE this oracle's domain:
            # tests/fuzz/pcre2_oracle.c compiles at options=0 by deliberate
            # project-wide pin (adopting any flag is a re-measurement event),
            # so verifying a flagged block here would compare a with-flags
            # expectation against a without-flags oracle — wrong in the silent
            # direction. Skip the block LOUDLY (counted below), the same shape
            # as verify_rxt.py's `# pcre2-only` skip. Found at the [M6.2] d27
            # merge review, where a `flags i` cell was mis-scored a
            # disagreement. Spell per-block caselessness inline ((?i)...) to
            # keep a cell verifiable here.
            if data:
                flagged = True
            continue
        if kind in ("features", "g", "gp"):
            continue
        if perr or pattern is None:
            continue
        if flagged:
            if kind in ("m", "n", "ms", "ns"):
                nflag += 1
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
        got = oracle_run(binpath, workdir, pattern, subj, sp)
        if got == want:
            npass += 1
        else:
            nfail += 1
            print("FAIL %s:%d: pattern %r subject %r startpos %d: "
                  "file says %s, libpcre2 says %s"
                  % (path, lineno, pattern, subj, sp, want, got))
    return npass, nfail, nflag


def main(argv):
    targets = argv[1:] or [DEFAULT_DIR]
    files = []
    for t in targets:
        if os.path.isdir(t):
            for dirpath, _, names in os.walk(t):
                files += [os.path.join(dirpath, n) for n in sorted(names)
                          if n.endswith(".rxt")]
        else:
            files.append(t)
    files = sorted(set(files))
    if not files:
        print("verify_pcre2: no .rxt files found — refusing to report a pass "
              "over an empty corpus")
        return 1

    with tempfile.TemporaryDirectory() as workdir:
        binpath = build_oracle(workdir)
        if binpath is None:
            print("verify_pcre2: SKIP — libpcre2-8 is not loadable on this "
                  "box, so the \\Z expectations cannot be re-verified here. "
                  "Install libpcre2-8-0 to run this check.")
            return 0
        total_p = total_f = total_fl = 0
        for path in files:
            p, f, fl = check_file(binpath, workdir, path)
            print("  %-44s %4d cells verified against libpcre2%s%s"
                  % (os.path.relpath(path, ROOT), p,
                     "" if f == 0 else ", %d DISAGREE" % f,
                     "" if fl == 0 else
                     ", %d in `flags` blocks skipped (options=0 pin)" % fl))
            total_p += p
            total_f += f
            total_fl += fl
    if total_p == 0:
        print("verify_pcre2: 0 cells checked — the corpus has no population")
        return 1
    print("verify_pcre2: %d cells agree with libpcre2, %d disagree%s"
          % (total_p, total_f,
             "" if total_fl == 0 else
             ", %d skipped in `flags` blocks (outside the options=0 oracle)"
             % total_fl))
    return 1 if total_f else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
