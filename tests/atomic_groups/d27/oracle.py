#!/usr/bin/env python3
"""oracle.py -- an INDEPENDENT re-checker for tests/atomic_groups/d27/*.rxt.

This script does NOT import, or otherwise trust, whatever process wrote the
.rxt files. It re-implements the .rxt grammar directly from docs/testing.md
(the format spec, read fresh for this script) and re-queries libpcre2 10.46
via docs/design/eng_brep_measurements/probes/pcre2_ctypes.py -- the oracle
of record per GOAL_FACTS B.2 -- for every m/n/ms/ns/g/gp expectation in
every file in this directory, plus the perr direction for the two files
that carry it. Run it last, after the .rxt files are written, and read its
per-file pass/fail counts as the corpus's own self-check.

Usage:
    python3 oracle.py                 # check every *.rxt in this directory
    python3 oracle.py FILE.rxt ...    # check specific files

Exit code is 0 iff every case in every checked file agrees with libpcre2 (or,
for syntax_errors.rxt / gating.rxt, agrees with the expected accept/reject
direction described below); nonzero otherwise, so this can be wired into a
CI-style check later without modification.
"""
import sys
import os
import re as _pyre

HERE = os.path.dirname(os.path.abspath(__file__))
PROBE_DIR = os.path.join(
    HERE, "..", "..", "..",
    "docs", "design", "eng_brep_measurements", "probes")
sys.path.insert(0, os.path.abspath(PROBE_DIR))
import pcre2_ctypes as p2  # noqa: E402

import ctypes  # noqa: E402
_lib = p2._lib
_lib.pcre2_pattern_info_8.restype = ctypes.c_int
_lib.pcre2_pattern_info_8.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_void_p]
PCRE2_INFO_CAPTURECOUNT = 4
PCRE2_CASELESS = 0x00000008


def capcount(compiled):
    n = ctypes.c_uint32(0)
    rc = _lib.pcre2_pattern_info_8(compiled._code, PCRE2_INFO_CAPTURECOUNT, ctypes.byref(n))
    if rc != 0:
        raise RuntimeError("pcre2_pattern_info CAPTURECOUNT failed: rc=%d" % rc)
    return n.value


# --- .rxt grammar (docs/testing.md, read directly for this re-implementation) ---

_ESCAPES = {
    '"': '"', '\\': '\\', 'n': '\n', 't': '\t', 'r': '\r', 'f': '\f', 'v': '\v',
}


class RxtError(Exception):
    pass


def decode_subject(raw):
    """raw is the text between the opening and closing double quotes,
    exactly as it appeared in the file (quotes already stripped)."""
    out = bytearray()
    i = 0
    n = len(raw)
    while i < n:
        c = raw[i]
        if c != '\\':
            out.append(ord(c))
            i += 1
            continue
        if i + 1 >= n:
            raise RxtError("trailing backslash in subject")
        nc = raw[i + 1]
        if nc == 'x':
            if i + 4 > n:
                raise RxtError("truncated \\xHH escape")
            hx = raw[i + 2:i + 4]
            out.append(int(hx, 16))
            i += 4
            continue
        if nc not in _ESCAPES:
            raise RxtError("unknown escape \\%s" % nc)
        out.append(ord(_ESCAPES[nc]))
        i += 2
    return bytes(out)


def parse_quoted(line):
    """Extract the double-quoted subject from a line like:
    'm "abc\\n" 0 3' or 'ms 1 "abc" 0 3'. Returns (raw_inside_quotes, rest)."""
    assert line[0] == '"'
    i = 1
    buf = []
    n = len(line)
    while i < n:
        c = line[i]
        if c == '\\':
            if i + 1 >= n:
                raise RxtError("trailing backslash in quoted subject")
            buf.append(c)
            buf.append(line[i + 1])
            i += 2
            continue
        if c == '"':
            return ''.join(buf), line[i + 1:]
        buf.append(c)
        i += 1
    raise RxtError("unterminated quoted subject")


class Block:
    def __init__(self, pattern, lineno):
        self.pattern = pattern
        self.lineno = lineno
        self.flags = ''
        self.features = None
        self.is_perr = False
        self.cases = []   # list of dict: kind, subject(bytes), startpos, start, end
        self.gcases = []  # list of (case_index, slot, start, end) attached to last m/ms


def parse_rxt(path):
    blocks = []
    cur = None
    with open(path, 'r', encoding='utf-8') as f:
        for lineno, line in enumerate(f, 1):
            line = line.rstrip('\n')
            if line.strip() == '' or line.lstrip().startswith('#'):
                continue
            if line.startswith('pattern '):
                cur = Block(line[len('pattern '):], lineno)
                blocks.append(cur)
                continue
            if cur is None:
                raise RxtError("%s:%d: directive before any 'pattern' line" % (path, lineno))
            if line.startswith('flags '):
                cur.flags = line[len('flags '):].strip()
                continue
            if line.startswith('features '):
                cur.features = line[len('features '):].strip()
                continue
            if line.strip() == 'perr':
                cur.is_perr = True
                continue
            if line.startswith('m ') or line.startswith('n ') or \
               line.startswith('ms ') or line.startswith('ns '):
                kind, rest = line.split(' ', 1)
                rest = rest.strip()
                startpos = 0
                if kind in ('ms', 'ns'):
                    sp_str, rest = rest.split(' ', 1)
                    startpos = int(sp_str)
                    rest = rest.strip()
                raw_subj, rest = parse_quoted(rest)
                subject = decode_subject(raw_subj)
                rest = rest.strip()
                if kind in ('m', 'ms'):
                    s_str, e_str = rest.split()
                    cur.cases.append({
                        'kind': kind, 'subject': subject, 'startpos': startpos,
                        'start': int(s_str), 'end': int(e_str), 'lineno': lineno,
                    })
                else:
                    if rest != '':
                        raise RxtError("%s:%d: %s case has trailing text" % (path, lineno, kind))
                    cur.cases.append({
                        'kind': kind, 'subject': subject, 'startpos': startpos,
                        'lineno': lineno,
                    })
                continue
            if line.startswith('g ') or line.startswith('gp '):
                kind, rest = line.split(' ', 1)
                slot_str, s_str, e_str = rest.split()
                if not cur.cases:
                    raise RxtError("%s:%d: %s line with no preceding m/ms case" % (path, lineno, kind))
                cur.gcases.append({
                    'case_index': len(cur.cases) - 1,
                    'slot': int(slot_str), 'start': int(s_str), 'end': int(e_str),
                    'lineno': lineno,
                })
                continue
            raise RxtError("%s:%d: unparseable line: %r" % (path, lineno, line))
    return blocks


# --- checking ---

def check_file(path):
    fname = os.path.basename(path)
    blocks = parse_rxt(path)
    n_pass = 0
    n_fail = 0
    fails = []

    # These two files' perr blocks test pcrec's own --features CLI gate over
    # patterns that are independently EXPECTED TO BE VALID PCRE2 syntax
    # (gating.rxt), vs genuinely malformed PCRE2 syntax (syntax_errors.rxt).
    # oracle.py cannot invoke pcrec itself (out of this cell's allowlist, and
    # not this script's job -- gating and rejection are re-checked at merge
    # review against the real implementation); what it CAN independently
    # re-verify is the PCRE2-side half of that claim.
    expect_pcre2_reject = (fname == 'syntax_errors.rxt')
    expect_pcre2_accept = (fname == 'gating.rxt')

    for b in blocks:
        options = PCRE2_CASELESS if 'i' in b.flags else 0
        try:
            compiled = p2.Compiled(b.pattern, options)
            compile_err = None
        except p2.Pcre2Error as e:
            compiled = None
            compile_err = e

        if b.is_perr:
            if expect_pcre2_reject:
                ok = compiled is None
                label = "syntax_errors.rxt perr: pattern must be a genuine PCRE2 rejection"
            elif expect_pcre2_accept:
                ok = compiled is not None
                label = "gating.rxt perr: pattern must be VALID PCRE2 syntax (refusal is pcrec's module gate, not a PCRE2 syntax error)"
            else:
                ok = True
                label = "perr (not independently PCRE2-checked by this oracle)"
            if ok:
                n_pass += 1
            else:
                n_fail += 1
                fails.append("%s:%d: pattern %r -- %s -- FAILED (compiled=%s)" %
                              (fname, b.lineno, b.pattern, label, compiled is not None))
            continue

        if compiled is None:
            n_fail += 1
            fails.append("%s:%d: pattern %r -- unexpectedly FAILS to compile under libpcre2: %s" %
                          (fname, b.lineno, b.pattern, compile_err))
            continue

        ng = capcount(compiled)
        gmap = {}
        for g in b.gcases:
            gmap.setdefault(g['case_index'], []).append(g)

        for ci, case in enumerate(b.cases):
            r = compiled.search(case['subject'], case['startpos'])
            kind = case['kind']
            if kind in ('n', 'ns'):
                ok = (r is None)
                if ok:
                    n_pass += 1
                else:
                    n_fail += 1
                    fails.append("%s:%d: pattern %r subject %r startpos %d -- expected NO MATCH, libpcre2 gives %r" %
                                 (fname, case['lineno'], b.pattern, case['subject'], case['startpos'], r))
                continue
            # m / ms
            if r is None:
                n_fail += 1
                fails.append("%s:%d: pattern %r subject %r startpos %d -- expected match (%d,%d), libpcre2 gives NO MATCH" %
                             (fname, case['lineno'], b.pattern, case['subject'], case['startpos'],
                              case['start'], case['end']))
                continue
            span, groups = r
            ok = (span == (case['start'], case['end']))
            if ok:
                n_pass += 1
            else:
                n_fail += 1
                fails.append("%s:%d: pattern %r subject %r startpos %d -- expected (%d,%d), libpcre2 gives %r" %
                             (fname, case['lineno'], b.pattern, case['subject'], case['startpos'],
                              case['start'], case['end'], span))
            # check attached g/gp lines
            padded = list(groups) + [None] * (ng - len(groups))
            for g in gmap.get(ci, []):
                slot = g['slot']
                if slot < 1 or slot > ng:
                    n_fail += 1
                    fails.append("%s:%d: g/gp slot %d out of range (ngroups=%d) for pattern %r" %
                                 (fname, g['lineno'], slot, ng, b.pattern))
                    continue
                gv = padded[slot - 1]
                expect_unset = (g['start'] == -1 and g['end'] == -1)
                if expect_unset:
                    gok = (gv is None)
                    got = 'unset' if gv is None else gv
                else:
                    gok = (gv is not None and gv == (g['start'], g['end']))
                    got = gv
                if gok:
                    n_pass += 1
                else:
                    n_fail += 1
                    fails.append("%s:%d: pattern %r subject %r slot %d -- expected %s, libpcre2 gives %r" %
                                 (fname, g['lineno'], b.pattern, case['subject'], slot,
                                  ('unset' if expect_unset else (g['start'], g['end'])), got))

    return n_pass, n_fail, fails


def main():
    args = sys.argv[1:]
    if args:
        paths = args
    else:
        paths = sorted(
            os.path.join(HERE, f) for f in os.listdir(HERE) if f.endswith('.rxt')
        )
    total_pass = total_fail = 0
    print("libpcre2:", p2.version())
    for path in paths:
        n_pass, n_fail, fails = check_file(path)
        total_pass += n_pass
        total_fail += n_fail
        status = "OK" if n_fail == 0 else "FAIL"
        print("%-28s %-4s  pass=%-4d fail=%-4d" % (os.path.basename(path), status, n_pass, n_fail))
        for line in fails:
            print("    " + line)
    print()
    print("TOTAL: pass=%d fail=%d" % (total_pass, total_fail))
    sys.exit(0 if total_fail == 0 else 1)


if __name__ == '__main__':
    main()
