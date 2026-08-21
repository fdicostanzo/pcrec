#!/usr/bin/env python3
"""
D27 oracle verifier for tests/assertions/d27/*.rxt.

Re-parses each .rxt file per the grammar in docs/testing.md ("The `.rxt`
format") and re-checks EVERY expectation line -- m/n/ms/ns and any attached
g/gp -- against the real libpcre2 runtime (via lib_pcre2.py's ctypes
binding), at options=0 (or PCRE2_CASELESS for a `flags i` block, options=0
otherwise -- no other compile/match option is ever used, per the project
brief). perr blocks are checked against libpcre2's own compile verdict
UNLESS marked `# pcrec-gate-only` on the line immediately before `pattern`
-- those assert pcrec's OWN feature-gating refusal, which is not a PCRE2
concept (PCRE2 has no module system; it accepts \\A \\z \\Z \\b \\B \\G \\K
and (?m) unconditionally), so there is nothing for this oracle to check
there; they are counted separately and never silently skipped.

This script does NOT invoke pcrec or gcc. It answers exactly one question:
"is the EXPECTATION written in this .rxt file what real libpcre2 says?" --
independent of whatever pcrec's own test harness (tests/harness/run.sh)
finds when it later runs these files against the compiled artifact.

Usage:
    python3 oracle.py [file-or-dir ...]      # default: every *.rxt beside this script
    python3 oracle.py --verbose ...          # print every case, not just failures

Exit code 0 iff every non-excluded expectation matches libpcre2; 1 otherwise.
"""
import sys
import os
import glob

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib_pcre2 as P


class RxtError(Exception):
    pass


def decode_subject(raw: str, filename: str, lineno: int) -> bytes:
    """Decode the escapes defined in docs/testing.md's escape table."""
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
            raise RxtError(f"{filename}:{lineno}: trailing backslash in subject")
        e = raw[i + 1]
        if e == '"':
            out.append(0x22); i += 2
        elif e == '\\':
            out.append(0x5C); i += 2
        elif e == 'n':
            out.append(0x0A); i += 2
        elif e == 't':
            out.append(0x09); i += 2
        elif e == 'r':
            out.append(0x0D); i += 2
        elif e == 'f':
            out.append(0x0C); i += 2
        elif e == 'v':
            out.append(0x0B); i += 2
        elif e == 'x':
            if i + 3 >= n:
                raise RxtError(f"{filename}:{lineno}: truncated \\xHH escape")
            hx = raw[i + 2:i + 4]
            out.append(int(hx, 16))
            i += 4
        else:
            raise RxtError(f"{filename}:{lineno}: unknown escape \\{e}")
    return bytes(out)


def split_quoted(rest: str, filename: str, lineno: int):
    """Given text starting with a '\"...\"' subject (with possible escapes)
    followed by more fields, return (subject_text, remainder_after_quote)."""
    if not rest.startswith('"'):
        raise RxtError(f"{filename}:{lineno}: expected quoted subject")
    i = 1
    buf = []
    n = len(rest)
    while i < n:
        c = rest[i]
        if c == '\\':
            if i + 1 >= n:
                raise RxtError(f"{filename}:{lineno}: trailing backslash in subject")
            buf.append(rest[i:i + 2])
            i += 2
            continue
        if c == '"':
            return ''.join(buf), rest[i + 1:].strip()
        buf.append(c)
        i += 1
    raise RxtError(f"{filename}:{lineno}: unterminated quoted subject")


class Block:
    def __init__(self, pattern, lineno):
        self.pattern = pattern
        self.lineno = lineno
        self.flags_i = False
        self.features = None     # list[str] or None
        self.is_perr = False
        self.gate_only = False   # preceding-comment marker: not oracle-checkable
        self.exclude_reason = None  # preceding-comment marker: '# unverifiable: ...'
        self.cases = []          # list of dicts: kind, subject(bytes), startpos, start, end, lineno, gs (list of (slot,start,end))

    def caseless(self):
        return self.flags_i


def parse_rxt(path):
    blocks = []
    cur = None
    pending_gate_only = False
    pending_exclude = None
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for lineno, raw_line in enumerate(lines, start=1):
        line = raw_line.rstrip('\n')
        stripped = line.strip()
        if stripped == '':
            continue
        if stripped.startswith('#'):
            if stripped.startswith('# pcrec-gate-only'):
                pending_gate_only = True
            elif stripped.startswith('# unverifiable:'):
                pending_exclude = stripped[len('# unverifiable:'):].strip()
            continue
        if stripped.startswith('pattern '):
            pat = line[len('pattern '):]  # verbatim after first space, not stripped-of-content
            # 'pattern ' is 8 chars; take everything after the literal prefix
            pat = line.split(' ', 1)[1] if ' ' in line else ''
            cur = Block(pat, lineno)
            cur.gate_only = pending_gate_only
            cur.exclude_reason = pending_exclude
            pending_gate_only = False
            pending_exclude = None
            blocks.append(cur)
            continue
        if cur is None:
            raise RxtError(f"{path}:{lineno}: expectation line before any 'pattern'")
        if stripped == 'perr':
            cur.is_perr = True
            continue
        if stripped.startswith('flags '):
            letters = stripped[len('flags '):].strip()
            for c in letters:
                if c != 'i':
                    raise RxtError(f"{path}:{lineno}: unknown flag '{c}'")
            cur.flags_i = 'i' in letters
            continue
        if stripped.startswith('features '):
            feats = stripped[len('features '):].strip()
            cur.features = [x.strip() for x in feats.split(',') if x.strip()]
            continue
        if stripped.startswith('m ') or stripped.startswith('ms '):
            is_ms = stripped.startswith('ms ')
            rest = stripped[3:].strip() if is_ms else stripped[2:].strip()
            startpos = 0
            if is_ms:
                parts = rest.split(None, 1)
                startpos = int(parts[0])
                rest = parts[1]
            subj_text, remainder = split_quoted(rest, path, lineno)
            subject = decode_subject(subj_text, path, lineno)
            nums = remainder.split()
            if len(nums) != 2:
                raise RxtError(f"{path}:{lineno}: expected '<start> <end>' after subject")
            start, end = int(nums[0]), int(nums[1])
            cur.cases.append({'kind': 'm', 'subject': subject, 'startpos': startpos,
                               'start': start, 'end': end, 'lineno': lineno, 'gs': []})
            continue
        if stripped.startswith('n ') or stripped.startswith('ns '):
            is_ns = stripped.startswith('ns ')
            rest = stripped[3:].strip() if is_ns else stripped[2:].strip()
            startpos = 0
            if is_ns:
                parts = rest.split(None, 1)
                startpos = int(parts[0])
                rest = parts[1]
            subj_text, remainder = split_quoted(rest, path, lineno)
            if remainder.strip() != '':
                raise RxtError(f"{path}:{lineno}: trailing text after n/ns subject")
            subject = decode_subject(subj_text, path, lineno)
            cur.cases.append({'kind': 'n', 'subject': subject, 'startpos': startpos,
                               'lineno': lineno, 'gs': []})
            continue
        if stripped.startswith('g ') or stripped.startswith('gp '):
            is_gp = stripped.startswith('gp ')
            rest = stripped[3:].strip() if is_gp else stripped[2:].strip()
            nums = rest.split()
            if len(nums) != 3:
                raise RxtError(f"{path}:{lineno}: expected '<slot> <start> <end>'")
            slot, gstart, gend = int(nums[0]), int(nums[1]), int(nums[2])
            if (gstart == -1) != (gend == -1):
                raise RxtError(f"{path}:{lineno}: asymmetric RX_UNSET (-1 in one slot only)")
            if not cur.cases or cur.cases[-1]['kind'] != 'm':
                raise RxtError(f"{path}:{lineno}: g/gp with no preceding m/ms case")
            cur.cases[-1]['gs'].append({'slot': slot, 'start': gstart, 'end': gend,
                                         'pending': is_gp, 'lineno': lineno})
            continue
        raise RxtError(f"{path}:{lineno}: unparseable line: {line!r}")
    return blocks


def check_file(path, verbose=False):
    passed = 0
    failed = 0
    skipped_gate = 0
    skipped_unverifiable = 0
    fails = []
    try:
        blocks = parse_rxt(path)
    except RxtError as e:
        print(f"PARSE ERROR: {e}")
        return (0, 1, 0, 0, [str(e)])

    for b in blocks:
        pat_bytes = b.pattern.encode('utf-8')
        caseless = b.caseless()

        if b.is_perr:
            if b.gate_only:
                skipped_gate += 1
                if verbose:
                    print(f"{path}:{b.lineno}: [gate-only, not oracle-checkable] pattern {b.pattern!r}")
                continue
            if b.exclude_reason:
                skipped_unverifiable += 1
                if verbose:
                    print(f"{path}:{b.lineno}: [excluded: {b.exclude_reason}] pattern {b.pattern!r}")
                continue
            err = P.compile_error(pat_bytes, caseless)
            if err is None:
                failed += 1
                msg = f"{path}:{b.lineno}: perr pattern {b.pattern!r} -- expected libpcre2 REJECT, but it COMPILED"
                fails.append(msg)
                print("FAIL " + msg)
            else:
                passed += 1
                if verbose:
                    print(f"PASS {path}:{b.lineno}: perr pattern {b.pattern!r} -- libpcre2 rejects ({err[0]}): {err[2]}")
            continue

        if b.exclude_reason:
            skipped_unverifiable += len(b.cases) if b.cases else 1
            if verbose:
                print(f"{path}:{b.lineno}: [excluded: {b.exclude_reason}] pattern {b.pattern!r}")
            continue

        for c in b.cases:
            try:
                r = P.match(pat_bytes, c['subject'], c['startpos'], caseless)
            except P.Pcre2CompileError as e:
                failed += 1
                msg = f"{path}:{c['lineno']}: pattern {b.pattern!r} -- libpcre2 COMPILE ERROR: {e}"
                fails.append(msg)
                print("FAIL " + msg)
                continue

            if c['kind'] == 'n':
                if r is not None:
                    failed += 1
                    msg = (f"{path}:{c['lineno']}: pattern {b.pattern!r} subject {c['subject']!r} "
                           f"@{c['startpos']} -- expected NO MATCH, libpcre2 found {r[0]}")
                    fails.append(msg)
                    print("FAIL " + msg)
                else:
                    passed += 1
                    if verbose:
                        print(f"PASS {path}:{c['lineno']}: n {c['subject']!r} @{c['startpos']}")
                continue

            # kind == 'm'
            if r is None:
                failed += 1
                msg = (f"{path}:{c['lineno']}: pattern {b.pattern!r} subject {c['subject']!r} "
                       f"@{c['startpos']} -- expected match [{c['start']},{c['end']}), libpcre2 found NO MATCH")
                fails.append(msg)
                print("FAIL " + msg)
                continue
            got_s, got_e = r[0]
            if (got_s, got_e) != (c['start'], c['end']):
                failed += 1
                msg = (f"{path}:{c['lineno']}: pattern {b.pattern!r} subject {c['subject']!r} "
                       f"@{c['startpos']} -- expected [{c['start']},{c['end']}), libpcre2 gave [{got_s},{got_e})")
                fails.append(msg)
                print("FAIL " + msg)
            else:
                passed += 1
                if verbose:
                    print(f"PASS {path}:{c['lineno']}: m {c['subject']!r} @{c['startpos']} -> [{got_s},{got_e})")

            for g in c['gs']:
                slot = g['slot']
                if slot >= len(r):
                    failed += 1
                    msg = (f"{path}:{g['lineno']}: pattern {b.pattern!r} -- slot {slot} "
                           f"exceeds libpcre2's own group count ({len(r) - 1})")
                    fails.append(msg)
                    print("FAIL " + msg)
                    continue
                pair = r[slot]
                exp_unset = (g['start'] == -1)
                if exp_unset:
                    ok = pair is None
                else:
                    ok = (pair is not None and pair == (g['start'], g['end']))
                if not ok:
                    failed += 1
                    got_repr = "-1 -1" if pair is None else f"{pair[0]} {pair[1]}"
                    msg = (f"{path}:{g['lineno']}: pattern {b.pattern!r} subject {c['subject']!r} "
                           f"@{c['startpos']} slot {slot} -- expected {g['start']} {g['end']}, "
                           f"libpcre2 gave {got_repr}")
                    fails.append(msg)
                    print("FAIL " + msg)
                else:
                    passed += 1
                    if verbose:
                        print(f"PASS {path}:{g['lineno']}: g/gp slot {slot} -> {g['start']} {g['end']}")

    return (passed, failed, skipped_gate, skipped_unverifiable, fails)


def main(argv):
    verbose = False
    args = []
    for a in argv[1:]:
        if a == '--verbose':
            verbose = True
        else:
            args.append(a)
    if not args:
        args = [os.path.dirname(os.path.abspath(__file__))]

    files = []
    for a in args:
        if os.path.isdir(a):
            files.extend(sorted(glob.glob(os.path.join(a, '*.rxt'))))
        else:
            files.append(a)
    files = sorted(set(files))

    if not files:
        print("no .rxt files found")
        return 1

    total_pass = total_fail = total_gate = total_unver = 0
    all_fails = []
    for f in files:
        p, fl, g, u, fails = check_file(f, verbose=verbose)
        print(f"{f}: {p} passed, {fl} failed, {g} gate-only skipped, {u} unverifiable skipped")
        total_pass += p
        total_fail += fl
        total_gate += g
        total_unver += u
        all_fails.extend(fails)

    print("---")
    print(f"TOTAL: {total_pass} passed, {total_fail} failed, "
          f"{total_gate} gate-only (pcrec-policy, not oracle-checkable), "
          f"{total_unver} unverifiable (excluded, see file comments)")
    return 0 if total_fail == 0 else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))
