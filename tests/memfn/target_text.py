#!/usr/bin/env python3
"""tests/memfn/target_text.py -- THE TARGET'S OWN TEXT in an artifact, the
one reader of it the SIMD checks share (target seam, units U2+U3; lane
u3floor). Since the seam a `-fmemfn-simd=T` artifact carries scaffolding no
SIMD form put there: `<P>_TARGETS "FAMILY:T"`, T's family GUARD
(`mf_family_c_of`), T's REGION open/close (`mf_target_c_of`) and the HEADER
lines placed at file scope just ahead of the open (the kit's header facts and
a compound part's own <string.h>), all counted in `<P>_SIMD_GUARDED_BYTES`
(match_api.md §6.3.10¶8-¶15; tuning.md §2.43¶4: "its target's own text
aside").

The spellings are the kit's declared text, read from the dumper
(tests/memfn/simd_levels.c), never a copy typed here. Readers:
simd_floor_check.py (C18: placement and exclusivity, then the cut) and
libc_census.py (C11's movers half: an ON artifact equals the default, its
target's own text aside, exactly where FORMS reads "none").
"""
import os
import re
import subprocess
import tempfile

# the stamps that carry the target's own text (a compound's parts' lines
# carry `__`; match_api.md §3.7¶1)
TARGET_STAMPS = re.compile(r'^#define (?:(?!__)\w)+_(TARGETS|SIMD_GUARDED_BYTES) .*\n?', re.M)
TARGETS = re.compile(r'^#define (?:(?!__)\w)+_TARGETS "([^"]*)"$', re.M)
PIECES = ('guard', 'open', 'close')


def read_table(levels_bin):
    """(levels, targets) from the dumper's `level` and `target` rows."""
    levels, targets = [], []
    out = subprocess.run([levels_bin], capture_output=True, text=True, check=True).stdout
    for row in out.splitlines():
        f = row.split('\t')
        if f[0] == 'level':
            levels.append({'token': f[1], 'family': f[2], 'needs': f[3], 'header': f[4],
                           'vw': f[5], 'march': f[6], 'stamp': f[7]})
        elif f[0] == 'target':
            text = [bytes.fromhex(x).decode('utf-8') for x in f[4:7]]
            targets.append({'name': f[1], 'family': f[2], 'features': f[3],
                            'open': text[0], 'close': text[1], 'guard': text[2]})
    return levels, targets


def tokens(s):
    return set(t for t in s.split(',') if t)


def admitted(t, levels):
    """The levels t admits, by the table's facts (target_seam_units.md §2)."""
    return [l for l in levels if l['family'] == t['family'] and tokens(l['needs']) <= tokens(t['features'])]


def cut(text, t):
    """`text` with each of t's guard, region open and region close removed
    where it occurs exactly once (a missing or doubled piece is left for the
    caller's placement check to name)."""
    for what in PIECES:
        if t[what] and text.count(t[what]) == 1:
            text = text.replace(t[what], '', 1)
    return text


HEADER_LINE = re.compile(r'#include <([^>]*)>\n')


def header_run(text, t):
    """The (start, end) span of the `#include <h>` lines directly ahead of t's
    region open (the target's header lines, match_api.md §6.3.10¶15), and
    their header names; (None, None, []) when the open is not there once."""
    if not t['open'] or text.count(t['open']) != 1:
        return None, None, []
    end = start = text.index(t['open'])
    names = []
    while True:
        line_at = text.rfind('\n', 0, start - 1) + 1 if start else 0
        m = HEADER_LINE.fullmatch(text, line_at, start)
        if not start or not m:
            break
        names.insert(0, m.group(1))
        start = line_at
    return start, end, names


def moved_headers_aside(ton, toff, t):
    """`ton` without the header lines ahead of t's region whose `#include <h>`
    the SIMD-off text `toff` also carries (a compound part's own <string.h>,
    first included there so the region never reads it first): a placement
    move, not new text. The other header lines (a level's vector header) stay
    for the caller's lint."""
    start, end, names = header_run(ton, t)
    if start is None:
        return ton
    keep = ''.join('#include <%s>\n' % h for h in names
                   if '#include <%s>\n' % h not in toff)
    return ton[:start] + keep + ton[end:]


def moved_out(toff, ton, t):
    """`toff` without the `#include <h>` lines the ON text `ton` moved out of
    its region (lane u3d27, F1: a compound part's own header lines are not
    repeated inside the region; match_api.md §6.3.10¶15): each OFF line the
    ON text lacks (a line diff) that includes a header ON includes ahead of
    t's region open. `toff` unchanged where ON has no open."""
    if not t['open'] or ton.count(t['open']) != 1:
        return toff
    ahead = set(HEADER_LINE.findall(ton[:ton.index(t['open'])]))
    if not ahead:
        return toff
    with tempfile.NamedTemporaryFile('w', delete=False, encoding='utf-8', errors='surrogateescape') as fa, \
         tempfile.NamedTemporaryFile('w', delete=False, encoding='utf-8', errors='surrogateescape') as fb:
        fa.write(toff)
        fb.write(ton)
    r = subprocess.run(['diff', '--unchanged-line-format= %L', '--old-line-format=-%L',
                        '--new-line-format=', fa.name, fb.name], capture_output=True)
    os.unlink(fa.name)
    os.unlink(fb.name)
    out = []
    for l in r.stdout.decode('utf-8', 'surrogateescape').splitlines(True):
        m = HEADER_LINE.fullmatch(l[1:])
        if l[0] == '-' and m and m.group(1) in ahead:
            continue
        out.append(l[1:])
    return ''.join(out)


def target_of(text, targets):
    """The row the artifact's TARGETS stamp names, or None."""
    m = TARGETS.findall(text)
    if len(m) != 1:
        return None
    for t in targets:
        if '%s:%s' % ('none' if t['family'] == '-' else t['family'], t['name']) == m[0]:
            return t
    return None


def aside(text, targets):
    """`text` with its target's own text set aside: the header lines ahead of
    the region and the pieces cut, the TARGETS / SIMD_GUARDED_BYTES stamp
    lines dropped. None when the TARGETS stamp names no row."""
    t = target_of(text, targets)
    if t is None:
        return None
    start, end, _ = header_run(text, t)
    if start is not None:
        text = text[:start] + text[end:]
    return TARGET_STAMPS.sub('', cut(text, t))
