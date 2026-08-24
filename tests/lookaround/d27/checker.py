#!/usr/bin/env python3
"""checker.py -- [M6.6.3] D27's OWN, INDEPENDENT re-verification of every
.rxt file this author wrote under d27/. This is a fresh .rxt PARSER,
written directly from docs/testing.md's format description (never by
importing the generator scripts' Block/RxtFile writer machinery, and
never by reading any harness code under tests/, which this cell does not
have) -- so a bug shared between "how the file was written" and "how the
file is read back" cannot hide an error from this pass. It re-derives
every m/n/ms/ns/g expectation from the SAME two oracles the generators
used (la_oracle's libpcre2 10.46 binding, python3 `re`) and asserts the
file's text matches, independently of whatever the generator scripts
computed at write time.

For `perr` blocks: this checker confirms EXISTENCE of the refusal by
compiling the pattern with the prebuilt `build/pcrec` binary under the
block's declared `--features` list (exit code must be nonzero) -- per the
brief's RULES OF EVIDENCE, this is sanctioned ("you may compile a cell's
pattern to see whether it is REFUSED (existence)"); it never derives a
match/nomatch expectation from pcrec, and it does not touch pcrec for any
non-perr block.

Usage: python3 checker.py [file.rxt ...]   (default: every *.rxt in d27/)
"""
import glob
import os
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import common
from common import la

PCREC = os.path.normpath(os.path.join(_HERE, "..", "build", "pcrec"))

# perr existence checks need a real -o target (pcrec also writes a .h
# beside it); per the SCOPE MANDATE this goes under the session scratchpad,
# never /tmp directly and never inside the cell.
_SCRATCH = "/tmp/claude-1001/-home-duxevents-pcrec/3f43c5f0-1e9e-4215-a124-6a0d2eb941c2/scratchpad/la27"
os.makedirs(_SCRATCH, exist_ok=True)
_PERR_OUT = os.path.join(_SCRATCH, "checker_perr_probe.c")


# ---------------------------------------------------------------------------
# A from-scratch .rxt parser, per docs/testing.md's format section.
# ---------------------------------------------------------------------------
class ParseError(Exception):
    pass


ESCAPES = {'"': '"', '\\': '\\', 'n': '\n', 't': '\t', 'r': '\r',
           'f': '\f', 'v': '\v'}


def decode_subject(literal, filename, lineno):
    """literal is the text between the outer double quotes (quotes already
    stripped). Decode \\" \\\\ \\n \\t \\r \\f \\v \\xHH; anything else is a
    hard parse error, per docs/testing.md."""
    out = []
    i = 0
    n = len(literal)
    while i < n:
        c = literal[i]
        if c == '\\':
            if i + 1 >= n:
                raise ParseError("%s:%d: dangling backslash in subject"
                                  % (filename, lineno))
            e = literal[i + 1]
            if e == 'x':
                if i + 3 >= n + 1 or not all(
                        ch in '0123456789abcdefABCDEF'
                        for ch in literal[i + 2:i + 4]) or len(literal[i + 2:i + 4]) != 2:
                    raise ParseError("%s:%d: bad \\xHH escape" % (filename, lineno))
                out.append(chr(int(literal[i + 2:i + 4], 16)))
                i += 4
                continue
            if e in ESCAPES:
                out.append(ESCAPES[e])
                i += 2
                continue
            raise ParseError("%s:%d: unknown escape \\%s" % (filename, lineno, e))
        else:
            out.append(c)
            i += 1
    return "".join(out)


def split_quoted(rest, filename, lineno):
    """rest starts with a '"'; return (decoded_subject, remainder_after_closing_quote)."""
    if not rest.startswith('"'):
        raise ParseError("%s:%d: expected quoted subject" % (filename, lineno))
    i = 1
    n = len(rest)
    while i < n:
        if rest[i] == '\\':
            i += 2
            continue
        if rest[i] == '"':
            return decode_subject(rest[1:i], filename, lineno), rest[i + 1:]
        i += 1
    raise ParseError("%s:%d: unterminated quoted subject" % (filename, lineno))


class CaseM:
    def __init__(self, subject, start, end, startpos=0):
        self.subject = subject
        self.start = start
        self.end = end
        self.startpos = startpos
        self.groups = {}   # slot -> (start, end) or None


class CaseN:
    def __init__(self, subject, startpos=0):
        self.subject = subject
        self.startpos = startpos


class RxtBlock:
    def __init__(self, pattern, filename, lineno):
        self.pattern = pattern
        self.filename = filename
        self.lineno = lineno
        self.flags = ""
        self.features = ""
        self.is_perr = False
        self.cases = []   # list of CaseM/CaseN, in file order


def parse_rxt(path):
    blocks = []
    cur = None
    pending_features = ""
    pending_flags = ""
    with open(path) as f:
        for lineno, raw in enumerate(f, start=1):
            line = raw.rstrip("\n")
            if not line.strip():
                continue
            if line.lstrip().startswith("#"):
                continue
            parts = line.split(" ", 1)
            kw = parts[0]
            rest = parts[1] if len(parts) > 1 else ""
            if kw == "features":
                pending_features = rest.strip()
                continue
            if kw == "flags":
                pending_flags = rest.strip()
                continue
            if kw == "pattern":
                cur = RxtBlock(rest, path, lineno)
                cur.features = pending_features
                cur.flags = pending_flags
                pending_features = ""
                pending_flags = ""
                blocks.append(cur)
                continue
            if cur is None:
                raise ParseError("%s:%d: %s line before any pattern"
                                  % (path, lineno, kw))
            if kw == "perr":
                cur.is_perr = True
                continue
            if kw == "m":
                subj, remainder = split_quoted(rest, path, lineno)
                nums = remainder.split()
                if len(nums) != 2:
                    raise ParseError("%s:%d: bad m line" % (path, lineno))
                cur.cases.append(CaseM(subj, int(nums[0]), int(nums[1])))
                continue
            if kw == "n":
                subj, remainder = split_quoted(rest, path, lineno)
                cur.cases.append(CaseN(subj))
                continue
            if kw == "ms":
                p_str, remainder = rest.split(" ", 1)
                subj, remainder2 = split_quoted(remainder, path, lineno)
                nums = remainder2.split()
                if len(nums) != 2:
                    raise ParseError("%s:%d: bad ms line" % (path, lineno))
                cur.cases.append(CaseM(subj, int(nums[0]), int(nums[1]),
                                        startpos=int(p_str)))
                continue
            if kw == "ns":
                p_str, remainder = rest.split(" ", 1)
                subj, remainder2 = split_quoted(remainder, path, lineno)
                cur.cases.append(CaseN(subj, startpos=int(p_str)))
                continue
            if kw == "g":
                nums = rest.split()
                if len(nums) != 3:
                    raise ParseError("%s:%d: bad g line" % (path, lineno))
                slot, gs, ge = int(nums[0]), int(nums[1]), int(nums[2])
                if not cur.cases or isinstance(cur.cases[-1], CaseN):
                    raise ParseError("%s:%d: g line with no preceding m/ms case"
                                      % (path, lineno))
                cur.cases[-1].groups[slot] = None if gs == -1 else (gs, ge)
                continue
            raise ParseError("%s:%d: unrecognized directive %r" % (path, lineno, kw))
    return blocks


# ---------------------------------------------------------------------------
# Re-verification against the oracles.
# ---------------------------------------------------------------------------
def oracle_for_block(block):
    """Decide which oracle(s) this block should be checked against, from
    the FILE TEXT alone (the '# pcre2-only' marker line immediately above
    'pattern', which this parser also has to notice -- re-scan for it)."""
    return None  # unused; marker handled in verify_file via raw text scan


def find_pcre2_only_markers(path):
    """Return the set of pattern-line line-numbers immediately preceded
    (ignoring blank lines) by a '# pcre2-only' comment line."""
    marked = set()
    pending = False
    with open(path) as f:
        for lineno, raw in enumerate(f, start=1):
            line = raw.rstrip("\n")
            if not line.strip():
                continue
            if line.strip() == "# pcre2-only":
                pending = True
                continue
            if line.lstrip().startswith("#"):
                continue
            if line.startswith("pattern "):
                if pending:
                    marked.add(lineno)
                pending = False
                continue
            if line.startswith("features ") or line.startswith("flags "):
                # these precede 'pattern' within the same block header;
                # the marker must survive across them.
                continue
            pending = False
    return marked


def verify_block(block, pcre2_only, results):
    fname = os.path.basename(block.filename)
    if block.is_perr:
        feats = block.features or ""
        cmd = [PCREC, "--features", feats, "-p", "rx", "-o", _PERR_OUT,
               "--", block.pattern] if feats else \
              [PCREC, "-p", "rx", "-o", _PERR_OUT, "--", block.pattern]
        try:
            proc = subprocess.run(cmd, capture_output=True, timeout=10)
        except Exception as e:                                # noqa: BLE001
            results.fail(fname, block.lineno, block.pattern,
                         "perr: pcrec invocation raised %r" % (e,))
            return
        if proc.returncode == 0:
            results.fail(fname, block.lineno, block.pattern,
                         "perr: pcrec ACCEPTED this pattern (expected refusal)")
        else:
            results.ok()
        return

    for case in block.cases:
        if isinstance(case, CaseM):
            expect = (case.start, case.end)
        else:
            expect = None
        p2 = common.pcre2_search(block.pattern, case.subject, case.startpos)
        if p2 == "ERR":
            results.fail(fname, block.lineno, block.pattern,
                         "libpcre2 could not compile this pattern at all "
                         "(re-check should never reach here for a non-perr "
                         "block)")
            continue
        got_span = p2[0] if p2 is not None else None
        got_groups = p2[1] if p2 is not None else None
        if got_span != expect:
            results.fail(fname, block.lineno, block.pattern,
                         "libpcre2: subject %r startpos=%d expected %r got %r"
                         % (case.subject, case.startpos, expect, got_span))
            continue
        if isinstance(case, CaseM):
            for slot, want in case.groups.items():
                got = None
                if got_groups and slot - 1 < len(got_groups):
                    got = got_groups[slot - 1]
                if got != want:
                    results.fail(fname, block.lineno, block.pattern,
                                 "libpcre2: subject %r slot %d expected %r got %r"
                                 % (case.subject, slot, want, got))
                    continue
        results.ok()

        if pcre2_only:
            continue
        py = common.py_search(block.pattern, case.subject, case.startpos)
        if py == "ERR":
            results.fail(fname, block.lineno, block.pattern,
                         "marked python-verifiable but python re cannot "
                         "compile this pattern at all")
            continue
        py_span = py[0] if py is not None else None
        py_groups = py[1] if py is not None else None
        if py_span != expect:
            results.fail(fname, block.lineno, block.pattern,
                         "python: subject %r startpos=%d expected %r got %r"
                         % (case.subject, case.startpos, expect, py_span))
            continue
        if isinstance(case, CaseM):
            for slot, want in case.groups.items():
                got = None
                if py_groups and slot - 1 < len(py_groups):
                    got = py_groups[slot - 1]
                if got != want:
                    results.fail(fname, block.lineno, block.pattern,
                                 "python: subject %r slot %d expected %r got %r"
                                 % (case.subject, slot, want, got))
                    continue
        results.ok()


class Results:
    def __init__(self):
        self.n_ok = 0
        self.n_fail = 0
        self.failures = []

    def ok(self):
        self.n_ok += 1

    def fail(self, fname, lineno, pattern, msg):
        self.n_fail += 1
        self.failures.append("%s:%d: pattern %r: %s" % (fname, lineno, pattern, msg))


def verify_file(path, results):
    blocks = parse_rxt(path)
    marked_lines = find_pcre2_only_markers(path)
    n_perr = sum(1 for b in blocks if b.is_perr)
    n_ok_blocks = len(blocks) - n_perr
    for b in blocks:
        if not b.features:
            results.fail(os.path.basename(path), b.lineno, b.pattern,
                         "block has no 'features' line (default feature "
                         "set does not include lookaround -- a cell that "
                         "forgets this is refused and passes vacuously)")
            continue
        if "lookaround" not in b.features.split(","):
            results.fail(os.path.basename(path), b.lineno, b.pattern,
                         "block's features line %r does not include "
                         "'lookaround'" % (b.features,))
            continue
        pcre2_only = b.lineno in marked_lines
        verify_block(b, pcre2_only, results)
    return len(blocks), n_perr


def main():
    args = sys.argv[1:]
    if args:
        files = args
    else:
        files = sorted(glob.glob(os.path.join(_HERE, "*.rxt")))
    if not os.path.exists(PCREC):
        print("FATAL: prebuilt pcrec not found at %s" % (PCREC,), file=sys.stderr)
        sys.exit(2)

    results = Results()
    total_blocks = 0
    total_perr = 0
    for path in files:
        try:
            nb, npe = verify_file(path, results)
        except ParseError as e:
            results.fail(os.path.basename(path), 0, "<parse>", str(e))
            continue
        total_blocks += nb
        total_perr += npe
        print("%-24s %4d blocks (%3d perr)" % (os.path.basename(path), nb, npe))

    print()
    print("TOTAL: %d blocks (%d perr) across %d files" %
          (total_blocks, total_perr, len(files)))
    print("assertions checked ok: %d   FAILED: %d" % (results.n_ok, results.n_fail))
    if results.failures:
        print()
        print("FAILURES:")
        for f in results.failures[:200]:
            print("  " + f)
        if len(results.failures) > 200:
            print("  ... and %d more" % (len(results.failures) - 200,))
    sys.exit(1 if results.n_fail else 0)


if __name__ == "__main__":
    main()
