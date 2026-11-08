#!/usr/bin/env python3
"""tests/memfn/target_text.py -- THE TARGET'S OWN TEXT in an artifact, the
one reader of it the SIMD checks share (target seam, units U2+U3; lane
u3floor). Since the seam a `-fmemfn-simd=T` artifact carries scaffolding no
SIMD form put there: `<P>_TARGETS "FAMILY:T"`, T's family GUARD
(`mf_family_c_of`) and T's REGION open/close (`mf_target_c_of`), all counted
in `<P>_SIMD_GUARDED_BYTES` (match_api.md §6.3.10¶8-¶15; tuning.md
§2.43¶4: "its target's own text aside").

The spellings are the kit's declared text, read from the dumper
(tests/memfn/simd_levels.c), never a copy typed here. Readers:
simd_floor_check.py (C18: placement and exclusivity, then the cut) and
libc_census.py (C11's movers half: an ON artifact equals the default, its
target's own text aside, exactly where FORMS reads "none").
"""
import re
import subprocess

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
    """`text` with its target's own text set aside: the pieces cut and the
    TARGETS / SIMD_GUARDED_BYTES stamp lines dropped. None when the TARGETS
    stamp names no row."""
    t = target_of(text, targets)
    if t is None:
        return None
    return TARGET_STAMPS.sub('', cut(text, t))
