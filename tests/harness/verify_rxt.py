#!/usr/bin/env python3
"""Cross-verify .rxt corpus files against python's `re` module (the base-tier
oracle, decisions.md D4). Usage: verify_rxt.py [files-or-dirs...]; default is
<repo>/tests/base. A comment line `# pcre2-only` immediately before a
`pattern` line skips python verification for that block (used where python re
diverges from real PCRE, e.g. quantified anchors — see docs/testing.md).

[M4.5a] `g <slot> <start> <end>` / `gp <slot> <start> <end>` capture-group
expectation lines (attached to the most recent `m`/`ms` case) are checked
against python re's `match.span(slot)`, identically for 'g' (live) and 'gp'
(pending-VM) — pending-ness is a fact about what pcrec's CURRENT compiled
artifact can deliver (RX_NCAPS), which this oracle has no notion of and does
not need; it verifies the EXPECTATION itself, independent of whether
tests/harness/run.sh can check it yet. See docs/testing.md."""
import re
import sys
import glob
import os

BASE_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "base"))

def decode_subject(s):
    # s is the raw text between the outer quotes (quotes already stripped)
    out = []
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c == '\\':
            if i + 1 >= n:
                raise ValueError("trailing backslash in subject")
            nc = s[i+1]
            if nc == '"':
                out.append('"'); i += 2
            elif nc == '\\':
                out.append('\\'); i += 2
            elif nc == 'n':
                out.append('\n'); i += 2
            elif nc == 't':
                out.append('\t'); i += 2
            elif nc == 'r':
                out.append('\r'); i += 2
            elif nc == 'f':
                out.append('\f'); i += 2
            elif nc == 'v':
                out.append('\v'); i += 2
            elif nc == 'x':
                if i + 3 >= n:
                    raise ValueError("bad \\xHH escape")
                hexpart = s[i+2:i+4]
                out.append(chr(int(hexpart, 16)))
                i += 4
            else:
                raise ValueError(f"unknown subject escape \\{nc}")
        else:
            out.append(c)
            i += 1
    return ''.join(out)

def parse_quoted(line):
    """line starts with a double-quote; return (decoded_subject, rest_of_line_after_closing_quote)."""
    assert line[0] == '"'
    i = 1
    raw = []
    n = len(line)
    while i < n:
        c = line[i]
        if c == '\\':
            if i + 1 >= n:
                raise ValueError("trailing backslash before end of line in subject")
            raw.append(line[i:i+2])
            i += 2
        elif c == '"':
            # end of quoted subject
            rest = line[i+1:]
            return decode_subject(''.join(raw)), rest
        else:
            raw.append(c)
            i += 1
    raise ValueError("unterminated quoted subject: " + line)


def parse_startpos_tail(line, prefix):
    """line starts with `<prefix> ` (e.g. 'ms '); return (P, rest_of_line)
    where rest_of_line starts at the quoted subject."""
    rest = line[len(prefix):].lstrip()
    i = 0
    n = len(rest)
    while i < n and rest[i].isdigit():
        i += 1
    if i == 0:
        raise ValueError(f"missing startpos in {prefix!r} line: {line!r}")
    p = int(rest[:i])
    tail = rest[i:].lstrip()
    return p, tail


def parse_group_tail(line, prefix):
    """line starts with `<prefix> ` ('g ' or 'gp '); return (slot, start, end)
    from the remaining `<slot> <start> <end>` tail. RX_UNSET is '-1 -1' in
    BOTH slots — one -1 without the other is a hard parse error, matching
    tests/harness/run.sh's own check."""
    rest = line[len(prefix):].strip()
    parts = rest.split()
    if len(parts) != 3:
        raise ValueError(f"bad {prefix.strip()!r} line tail {rest!r}")
    slot, start, end = int(parts[0]), int(parts[1]), int(parts[2])
    if (start == -1) != (end == -1):
        raise ValueError(f"RX_UNSET must be -1 in BOTH slots, not one: {rest!r}")
    return slot, start, end


def parse_rxt(path):
    """Yield (lineno, kind, data) tuples. kind in {'pattern','m','n','ms','ns','perr','g','gp'}."""
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    results = []
    pcre2_only_next = False
    for lineno, raw_line in enumerate(lines, 1):
        line = raw_line.rstrip('\n')
        if line.strip() == '# pcre2-only':
            pcre2_only_next = True
            continue
        if line == '' or line.startswith('#'):
            continue
        if line.startswith('pattern '):
            pat = line[len('pattern '):]
            results.append((lineno, 'pattern', (pat, pcre2_only_next)))
            pcre2_only_next = False
        elif line == 'perr':
            results.append((lineno, 'perr', None))
        elif line.startswith('flags '):
            results.append((lineno, 'flags', line[len('flags '):].strip()))
        elif line.startswith('features '):
            results.append((lineno, 'features', line[len('features '):].strip()))
        elif line.startswith('m "'):
            rest = line[2:]  # keep leading quote
            subj, tail = parse_quoted(rest)
            tail = tail.strip()
            parts = tail.split()
            if len(parts) != 2:
                raise ValueError(f"{path}:{lineno}: bad m line tail {tail!r}")
            start, end = int(parts[0]), int(parts[1])
            results.append((lineno, 'm', (subj, start, end)))
        elif line.startswith('n "'):
            rest = line[2:]
            subj, tail = parse_quoted(rest)
            tail = tail.strip()
            if tail != '':
                raise ValueError(f"{path}:{lineno}: unexpected trailing content on n line: {tail!r}")
            results.append((lineno, 'n', subj))
        elif line.startswith('ms '):
            p, rest = parse_startpos_tail(line, 'ms ')
            subj, tail = parse_quoted(rest)
            tail = tail.strip()
            parts = tail.split()
            if len(parts) != 2:
                raise ValueError(f"{path}:{lineno}: bad ms line tail {tail!r}")
            start, end = int(parts[0]), int(parts[1])
            results.append((lineno, 'ms', (p, subj, start, end)))
        elif line.startswith('ns '):
            p, rest = parse_startpos_tail(line, 'ns ')
            subj, tail = parse_quoted(rest)
            tail = tail.strip()
            if tail != '':
                raise ValueError(f"{path}:{lineno}: unexpected trailing content on ns line: {tail!r}")
            results.append((lineno, 'ns', (p, subj)))
        elif line.startswith('gp '):
            try:
                slot, start, end = parse_group_tail(line, 'gp ')
            except ValueError as e:
                raise ValueError(f"{path}:{lineno}: {e}")
            results.append((lineno, 'gp', (slot, start, end)))
        elif line.startswith('g '):
            try:
                slot, start, end = parse_group_tail(line, 'g ')
            except ValueError as e:
                raise ValueError(f"{path}:{lineno}: {e}")
            results.append((lineno, 'g', (slot, start, end)))
        else:
            raise ValueError(f"{path}:{lineno}: unrecognized line: {line!r}")
    return results


def main():
    args = sys.argv[1:]
    if args:
        files = []
        for a in args:
            if os.path.isdir(a):
                files += sorted(glob.glob(os.path.join(a, "*.rxt")))
            else:
                files.append(a)
    else:
        files = sorted(glob.glob(os.path.join(BASE_DIR, "*.rxt")))
    if not files:
        print("No .rxt files found")
        sys.exit(1)

    total_pass = 0
    total_fail = 0
    per_file_counts = {}

    for path in files:
        fname = os.path.basename(path)
        entries = parse_rxt(path)
        cur_pattern = None
        cur_pattern_lineno = None
        compiled = None
        compile_error = None
        m_count = n_count = ms_count = ns_count = perr_count = 0
        g_count = gp_count = 0
        # [M4.5a] the most recent m/ms case in the CURRENT block, so a
        # following g/gp line knows what subject/startpos to re-search —
        # last_case_kind is 'm' (an m/ms case is live), 'n' (an n/ns case
        # came instead — g/gp after it is a hard error, no captures on a
        # no-match assertion), or None (no case yet in this block).
        last_case_kind = None
        last_case_subj = None
        last_case_pos = None
        skipped = 0
        cur_skip = False
        cur_reflags = 0
        file_failures = []

        for lineno, kind, data in entries:
            if kind == 'pattern':
                cur_pattern, cur_skip = data
                cur_pattern_lineno = lineno
                compile_error = None
                compiled = None
                cur_reflags = 0
                last_case_kind = None
                last_case_subj = None
                last_case_pos = None
                if not cur_skip:
                    try:
                        compiled = re.compile(cur_pattern)
                    except re.error as e:
                        compile_error = e
                continue

            if kind == 'features':
                # per-block enabled-module list (MOD-0.3c). The python oracle
                # is deliberately unaffected: python re has no module gate,
                # and every construct the gate can open either means the same
                # thing in python (\d \s \w and friends — verified as
                # usual) or cannot be expressed there at all, in which case
                # the block carries # pcre2-only exactly like any other
                # python-inexpressible pattern. An EMPTY list is a corpus
                # typo, refused like an unknown flag letter.
                if not data:
                    file_failures.append((lineno, "empty features list"))
                continue

            if kind == 'flags':
                # per-block compile options; re-compile the current block's
                # pattern under them. re.ASCII is not optional here: without it
                # python's IGNORECASE folds Unicode (K/Kelvin sign, long s),
                # which would make this oracle disagree with pcrec's
                # deliberately ASCII-only fold and silently mis-verify the
                # base tier. Unicode folding is DD-1/M5.
                if data != 'i':
                    file_failures.append((lineno, f"unknown flag letter(s) {data!r} (only 'i' is defined)"))
                    continue
                cur_reflags = re.IGNORECASE | re.ASCII
                if not cur_skip:
                    compile_error = None
                    compiled = None
                    try:
                        compiled = re.compile(cur_pattern, cur_reflags)
                    except re.error as e:
                        compile_error = e
                continue

            if cur_pattern is None:
                file_failures.append((lineno, f"{kind} line with no preceding pattern block"))
                continue

            if cur_skip:
                skipped += 1
                continue

            if kind == 'perr':
                perr_count += 1
                if compile_error is None:
                    file_failures.append((lineno, f"pattern {cur_pattern!r} (from line {cur_pattern_lineno}) was expected to fail to compile, but it compiled fine"))
                else:
                    total_pass += 1
                    continue
            elif kind == 'm':
                m_count += 1
                subj, start, end = data
                last_case_kind = 'm'
                last_case_subj = subj
                last_case_pos = 0
                if compiled is None:
                    file_failures.append((lineno, f"pattern {cur_pattern!r} failed to compile ({compile_error}), cannot check m line"))
                else:
                    mo = compiled.search(subj)
                    if mo is None:
                        file_failures.append((lineno, f"pattern {cur_pattern!r} subject {subj!r}: expected match [{start},{end}) but got no match"))
                    elif mo.span() != (start, end):
                        file_failures.append((lineno, f"pattern {cur_pattern!r} subject {subj!r}: expected span ({start},{end}) but got {mo.span()}"))
                    else:
                        total_pass += 1
                        continue
            elif kind == 'n':
                n_count += 1
                subj = data
                last_case_kind = 'n'
                last_case_subj = None
                last_case_pos = None
                if compiled is None:
                    file_failures.append((lineno, f"pattern {cur_pattern!r} failed to compile ({compile_error}), cannot check n line"))
                else:
                    mo = compiled.search(subj)
                    if mo is not None:
                        file_failures.append((lineno, f"pattern {cur_pattern!r} subject {subj!r}: expected no match but got {mo.span()}"))
                    else:
                        total_pass += 1
                        continue
            elif kind == 'ms':
                ms_count += 1
                p, subj, start, end = data
                last_case_kind = 'm'
                last_case_subj = subj
                last_case_pos = p
                if compiled is None:
                    file_failures.append((lineno, f"pattern {cur_pattern!r} failed to compile ({compile_error}), cannot check ms line"))
                else:
                    mo = compiled.search(subj, p)
                    if mo is None:
                        file_failures.append((lineno, f"pattern {cur_pattern!r} subject {subj!r} startpos {p}: expected match [{start},{end}) but got no match"))
                    elif mo.span() != (start, end):
                        file_failures.append((lineno, f"pattern {cur_pattern!r} subject {subj!r} startpos {p}: expected span ({start},{end}) but got {mo.span()}"))
                    else:
                        total_pass += 1
                        continue
            elif kind == 'ns':
                ns_count += 1
                p, subj = data
                last_case_kind = 'n'
                last_case_subj = None
                last_case_pos = None
                if compiled is None:
                    file_failures.append((lineno, f"pattern {cur_pattern!r} failed to compile ({compile_error}), cannot check ns line"))
                else:
                    mo = compiled.search(subj, p)
                    if mo is not None:
                        file_failures.append((lineno, f"pattern {cur_pattern!r} subject {subj!r} startpos {p}: expected no match but got {mo.span()}"))
                    else:
                        total_pass += 1
                        continue
            elif kind in ('g', 'gp'):
                # [M4.5a] capture-group expectation, oracle-verified against
                # python re's match.span(slot) regardless of the 'g'/'gp'
                # (live/pending-VM) distinction — pending-ness is a property
                # of what pcrec's CURRENT artifact can deliver (RX_NCAPS),
                # never of whether the expectation itself is correct, so this
                # oracle checks BOTH kinds identically.
                if kind == 'gp':
                    gp_count += 1
                else:
                    g_count += 1
                slot, start, end = data
                if last_case_kind != 'm':
                    file_failures.append((lineno, f"'{kind}' line with no preceding m/ms case in this block"))
                elif compiled is None:
                    file_failures.append((lineno, f"pattern {cur_pattern!r} failed to compile ({compile_error}), cannot check {kind} line"))
                else:
                    mo = compiled.search(last_case_subj, last_case_pos)
                    if mo is None:
                        file_failures.append((lineno, f"pattern {cur_pattern!r} subject {last_case_subj!r} startpos {last_case_pos}: preceding case implies a match but oracle found none, cannot check group slot {slot}"))
                    elif slot > compiled.groups:
                        file_failures.append((lineno, f"pattern {cur_pattern!r}: group slot {slot} exceeds pattern's group count ({compiled.groups})"))
                    else:
                        got = mo.span(slot)
                        if got != (start, end):
                            file_failures.append((lineno, f"pattern {cur_pattern!r} subject {last_case_subj!r} startpos {last_case_pos}: group slot {slot} expected ({start},{end}) but got {got}"))
                        else:
                            total_pass += 1
                            continue
            total_fail += 1

        per_file_counts[fname] = (m_count, n_count, ms_count, ns_count, perr_count, g_count, gp_count, len(file_failures))
        if skipped:
            print(f"  {fname}: {skipped} case(s) in '# pcre2-only' blocks skipped (not python-verifiable)")
        if file_failures:
            print(f"=== {fname}: {len(file_failures)} FAILURES ===")
            for lineno, msg in file_failures:
                print(f"  line {lineno}: {msg}")

    print()
    print("=== Summary ===")
    grand_m = grand_n = grand_ms = grand_ns = grand_p = grand_g = grand_gp = grand_f = 0
    for fname in sorted(per_file_counts):
        m_count, n_count, ms_count, ns_count, perr_count, g_count, gp_count, fails = per_file_counts[fname]
        grand_m += m_count; grand_n += n_count
        grand_ms += ms_count; grand_ns += ns_count
        grand_p += perr_count; grand_f += fails
        grand_g += g_count; grand_gp += gp_count
        total = m_count + n_count + ms_count + ns_count + perr_count + g_count + gp_count
        status = "OK" if fails == 0 else f"{fails} FAIL"
        print(f"  {fname:28s} m={m_count:3d} n={n_count:3d} ms={ms_count:3d} ns={ns_count:3d} perr={perr_count:3d} g={g_count:3d} gp={gp_count:3d} total={total:3d}  [{status}]")
    print()
    grand_total = grand_m + grand_n + grand_ms + grand_ns + grand_p + grand_g + grand_gp
    print(f"TOTAL: m={grand_m} n={grand_n} ms={grand_ms} ns={grand_ns} perr={grand_p} g={grand_g} gp={grand_gp} cases={grand_total}")
    print(f"PASS={total_pass} FAIL={total_fail}")
    if grand_f == 0:
        print("ALL CHECKS PASSED (100%)")
    else:
        print(f"{grand_f} FAILURES REMAIN")
        sys.exit(1)


if __name__ == '__main__':
    main()
