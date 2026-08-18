#!/usr/bin/env python3
"""D27 oracle for the pcrec `named-groups` module acceptance corpus.

Independently re-derives every match/capture expectation in this
directory's *.rxt files against python3's `re` module, and reports
which cases it could and could not verify.

WHY A CUSTOM SCRIPT: this D27 cell was given docs/testing.md and
docs/spec/match_api.md only, not the project's own
tests/harness/verify_rxt.py (that script lives under tests/, outside
this cell's allowlist). This script re-implements just enough of the
.rxt grammar (documented in docs/testing.md, "The .rxt format") to
parse the four files in this directory and check them.

TRANSLATION: python3's `re` only accepts the (?P<name>...) spelling.
Every (?<name>...) / (?'name'...) pattern is translated to its
(?P<name>...) equivalent before being handed to `re.compile`. The
translation is a plain textual substitution (see `translate`), safe
here because this corpus never contains a lookbehind `(?<=`/`(?<!`,
which is the one construct that could be confused with `(?<name>`.

PCRE2-ONLY MARKING: a `# pcre2-only` comment line immediately above a
`pattern` line (docs/testing.md's own convention) marks a block this
script does NOT hold to python agreement -- python's `re` diverges from
PCRE2 on group-name length capping and on which characters are
"alphanumeric" (unicode identifiers vs. PCRE2's ASCII-only rule). Such
a block is reported separately, with what python actually did, never
silently skipped.

Usage: python3 oracle.py [file-or-dir ...]   (default: this directory)
"""
import re
import sys
import os
import glob

# ---------------------------------------------------------------------
# .rxt parsing (subset of docs/testing.md's grammar: pattern, features,
# flags, perr, m, n, ms, ns, g -- gp is not used by this corpus)
# ---------------------------------------------------------------------

ESCAPES = {
    '"': '"', '\\': '\\', 'n': '\n', 't': '\t',
    'r': '\r', 'f': '\f', 'v': '\v',
}


def decode_subject(raw):
    """Decode the escape vocabulary docs/testing.md defines for a
    quoted subject: \\" \\\\ \\n \\t \\r \\f \\v \\xHH."""
    out = bytearray()
    i = 0
    n = len(raw)
    while i < n:
        c = raw[i]
        if c == '\\':
            if i + 1 >= n:
                raise ValueError(f"trailing backslash in subject {raw!r}")
            nx = raw[i + 1]
            if nx == 'x':
                hexpair = raw[i + 2:i + 4]
                if len(hexpair) != 2:
                    raise ValueError(f"bad \\x escape in {raw!r}")
                out.append(int(hexpair, 16))
                i += 4
                continue
            if nx not in ESCAPES:
                raise ValueError(f"unknown escape \\{nx} in {raw!r}")
            out.extend(ESCAPES[nx].encode('latin-1'))
            i += 2
            continue
        out.extend(c.encode('utf-8'))
        i += 1
    # Decode as latin-1 back to a str usable by python re against a str
    # subject (this corpus's subjects are all ASCII/near-ASCII test
    # fixtures, not the byte-level probes docs/spec/match_api.md S3.1
    # describes -- those are out of scope for a named-groups corpus).
    return bytes(out).decode('latin-1')


def split_quoted(rest):
    """Parse a leading double-quoted, escape-aware string off `rest`;
    return (raw_inside_quotes, remainder_after_closing_quote)."""
    assert rest[0] == '"'
    i = 1
    buf = []
    while True:
        if i >= len(rest):
            raise ValueError(f"unterminated subject: {rest!r}")
        c = rest[i]
        if c == '\\':
            buf.append(rest[i:i + 2])
            i += 2
            continue
        if c == '"':
            i += 1
            break
        buf.append(c)
        i += 1
    return ''.join(buf), rest[i:].strip()


class Block:
    def __init__(self, pattern, features, flags, pcre2_only, lineno):
        self.pattern = pattern
        self.features = features
        self.flags = flags
        self.pcre2_only = pcre2_only
        self.lineno = lineno
        self.is_perr = False
        self.cases = []   # list of dicts: kind, subject, startpos, start, end
        self.gcases = []  # list of (case_index, slot, start, end)


def parse_rxt(path):
    blocks = []
    cur = None
    pending_pcre2_only = False
    with open(path, encoding='utf-8') as f:
        for lineno, line in enumerate(f, 1):
            line = line.rstrip('\n')
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith('#'):
                if stripped == '# pcre2-only':
                    pending_pcre2_only = True
                continue
            if stripped.startswith('pattern '):
                pat = line[len('pattern '):]
                cur = Block(pat, [], None, pending_pcre2_only, lineno)
                pending_pcre2_only = False
                blocks.append(cur)
                continue
            if cur is None:
                raise ValueError(f"{path}:{lineno}: line outside any block: {line!r}")
            if stripped.startswith('features '):
                cur.features = [s.strip() for s in stripped[len('features '):].split(',')]
                continue
            if stripped.startswith('flags '):
                cur.flags = stripped[len('flags '):].strip()
                continue
            if stripped == 'perr':
                cur.is_perr = True
                continue
            if stripped.startswith('g '):
                _, rest = stripped.split(' ', 1)
                slot_s, start_s, end_s = rest.split()
                idx = len(cur.cases) - 1
                cur.gcases.append((idx, int(slot_s), int(start_s), int(end_s)))
                continue
            if stripped.startswith('m '):
                rest = stripped[2:].strip()
                subj_raw, rest2 = split_quoted(rest)
                start_s, end_s = rest2.split()
                cur.cases.append(dict(kind='m', subj_raw=subj_raw, startpos=0,
                                       start=int(start_s), end=int(end_s)))
                continue
            if stripped.startswith('n '):
                rest = stripped[2:].strip()
                subj_raw, _ = split_quoted(rest)
                cur.cases.append(dict(kind='n', subj_raw=subj_raw, startpos=0))
                continue
            raise ValueError(f"{path}:{lineno}: unrecognized line: {line!r}")
    return blocks


# ---------------------------------------------------------------------
# PCRE-spelling -> python spelling translation
# ---------------------------------------------------------------------

# (?<name>...)  -> (?P<name>...), but NOT (?<= or (?<! (lookbehind)
_ANGLE_NAME = re.compile(r"\(\?<(?![=!])([^>]*)>")
# (?'name'...)  -> (?P<name>...)
_QUOTE_NAME = re.compile(r"\(\?'([^']*)'")


def translate(pattern):
    p = _ANGLE_NAME.sub(r"(?P<\1>", pattern)
    p = _QUOTE_NAME.sub(r"(?P<\1>", p)
    return p


# ---------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------

def verify_block(block, path):
    py_pattern = translate(block.pattern)
    flags = re.ASCII if block.flags and 'i' in block.flags else 0
    if block.flags and 'i' in block.flags:
        flags |= re.IGNORECASE

    if block.is_perr:
        try:
            re.compile(py_pattern, flags)
            py_result = ('OK', None)
        except re.error as e:
            py_result = ('ERR', str(e))
        if block.pcre2_only:
            return dict(status='DIVERGENCE-DOCUMENTED', detail=py_result)
        if py_result[0] == 'OK':
            return dict(status='FAIL',
                        detail=f"expected perr, but python compiled {py_pattern!r} without error "
                               f"(this block is not marked '# pcre2-only' -- either the rejection "
                               f"reason is not shared with python and the marker is missing, or "
                               f"the expectation is wrong)")
        return dict(status='PASS', detail=py_result)

    if block.pcre2_only:
        return dict(status='SKIP-UNVERIFIABLE',
                    detail="pcre2-only block carries m/g expectations; oracle.py does not "
                           "cross-check these against python (see README)")

    try:
        compiled = re.compile(py_pattern, flags)
    except re.error as e:
        return dict(status='FAIL', detail=f"python could not compile {py_pattern!r}: {e}")

    problems = []
    spans = []  # per-case computed spans, for g-line lookup
    for case in block.cases:
        subject = decode_subject(case['subj_raw'])
        m = compiled.search(subject, case['startpos'])
        if case['kind'] == 'n':
            if m is not None:
                problems.append(f"case {case!r}: expected no match, python found {m.span()}")
            spans.append(None)
            continue
        # kind == 'm'
        if m is None:
            problems.append(f"case {case!r}: expected match [{case['start']},{case['end']}), python found none")
            spans.append(None)
            continue
        if m.span() != (case['start'], case['end']):
            problems.append(f"case {case!r}: expected span [{case['start']},{case['end']}), "
                            f"python gives {m.span()}")
        spans.append(m)

    for (idx, slot, exp_start, exp_end) in block.gcases:
        m = spans[idx] if idx < len(spans) else None
        if m is None:
            problems.append(f"g slot {slot} for case #{idx}: no python match object to check against")
            continue
        try:
            got = m.span(slot)
        except IndexError:
            problems.append(f"g slot {slot} for case #{idx}: python pattern has no group {slot}")
            continue
        if got != (exp_start, exp_end):
            problems.append(f"g slot {slot} for case #{idx}: expected [{exp_start},{exp_end}), "
                            f"python gives {got}")

    if problems:
        return dict(status='FAIL', detail='; '.join(problems))
    return dict(status='PASS', detail=None)


def main(argv):
    targets = argv[1:] or [os.path.dirname(os.path.abspath(__file__))]
    files = []
    for t in targets:
        if os.path.isdir(t):
            files.extend(sorted(glob.glob(os.path.join(t, '*.rxt'))))
        else:
            files.append(t)

    counts = dict(PASS=0, FAIL=0, **{'DIVERGENCE-DOCUMENTED': 0, 'SKIP-UNVERIFIABLE': 0})
    failures = []

    for path in files:
        blocks = parse_rxt(path)
        for block in blocks:
            result = verify_block(block, path)
            counts[result['status']] = counts.get(result['status'], 0) + 1
            tag = result['status']
            print(f"{os.path.basename(path)}:{block.lineno}: {tag}: {block.pattern!r}"
                  + (f" -- {result['detail']}" if result['detail'] else ""))
            if tag == 'FAIL':
                failures.append((path, block.lineno, block.pattern, result['detail']))

    print()
    print("Summary:", ', '.join(f"{k}={v}" for k, v in counts.items()))
    if failures:
        print()
        print(f"{len(failures)} FAILURE(S):")
        for path, lineno, pattern, detail in failures:
            print(f"  {os.path.basename(path)}:{lineno}: {pattern!r}: {detail}")
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
