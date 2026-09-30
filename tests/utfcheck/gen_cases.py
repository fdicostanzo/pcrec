#!/usr/bin/env python3
"""tests/utfcheck/gen_cases.py -- writes the QUESTION set the libpcre2 10.46
probe answers ([UTF-VALID], docs/design/utf_valid_design.md §7).

Deterministic (fixed seed, fixed lists): re-running it reproduces
questions.tsv byte for byte, so a transcript's questions can always be
regenerated and diffed. One TSV row per question:

    set  pattern  subject_hex  startpos  mode  qpos

`mode` is S (an unanchored search from qpos) or A (PCRE2_ANCHORED at qpos).
`startpos` is the position a pcrec CALLER passes; `qpos` is the position the
oracle is asked about. They differ only on `align` rows, where qpos is the
position -fstartpos-guard=align moves a mid-character startpos to (computed
HERE, from the byte rule alone -- not from pcrec). Sets:

  pinned  the design's §1 rows (10.46 transcripts utfcheck_10.46.txt,
          cases*.txt), reproduced exactly
  lb      every §1.4 LB pattern pcrec compiles, at startpos LB and LB + 1 on
          "\\xff" + 10 x 'z' (the design's own refuse/answer pair), both modes
  kinds   every ill-formed sequence kind embedded in ASCII at three depths
          (before, at and past the 8-byte fast path's first window), at
          startpos 0, just before, on and just after the bad sequence
  align   well-formed and ill-formed subjects with multi-byte characters,
          every startpos, asked at the aligned position
  random  a seeded differential over a fragment alphabet
"""
import random, sys

LB_PATTERNS = [
    "b", "(?<=a)b", "(?<=..)b", "(?<!a)b", "(?<=a|bc)d", r"\bb", r"\Bb",
    r"b\b", r"(?=\b)b", r"(?<=\ba)b", r"(?<=\b..)b", "(?<=(?<=..)a)b",
    "(?<=a(?<=..))b", "(?=(?<=..))b", "(?m)^b", "^b", r"\Ab", r"\Gb", "b$",
    r"b\Z", r"b\z", "(?(DEFINE)(?<x>(?<=...)))b", r"(?(DEFINE)(?<x>\b))b(?&x)",
    "(*naplb:..)b", r"(?<=\x{100})b", r"a\Kb", r"(?:\b|(?<=...))b", "b(?<=...)",
]

def unesc(s):
    out = bytearray(); i = 0
    while i < len(s):
        if s[i] == '\\' and s[i+1] == 'x':
            out.append(int(s[i+2:i+4], 16)); i += 4
        else:
            out.extend(s[i].encode()); i += 1
    return bytes(out)

def hx(b): return b.hex() if b else '-'

rows = []
def add(st, pat, subj, pos, mode, qpos=None):
    rows.append((st, pat, hx(subj), pos, mode, pos if qpos is None else qpos))

# ---- pinned: the design's §1 rows (pattern|subject|start) ----------------
PINNED = r"""a|a\xff|0
a|xa\xffz|0
a|\xffab|2
b|\xffab|2
(?<=a)b|\xffab|2
(?<=a)b|x\xffab|3
(?<=\xff)b|\xffab|2
a|ab\xe3\x80|0
a|ab\xc0\x80|0
a|ab\xed\xa0\x80|0
a|ab\xf4\x90\x80\x80|0
a|ab\x80|0
z|ab\xffcd|0
a|\xc3\xa9a|1
(?<=..)b|\xffab|2
(?<=...)b|\xffxab|3
(?<=a|bc)d|\xffbcd|3
(?<=(?<=..)a)b|\xffzab|3
(?<=(?<=..)a)b|\xffzab|2
(?<=\ba)b|\xffab|2
(?<=\b..)b|\xffzab|3
\Ab|\xffab|2
\Ab|\xffab|1
\Ab|\x80b|1
\Gb|\xffb|1
a|\xc3\xa9\xffa|1
a|\x80\xa9a|1
(?<=a)b|\xc3\xa9\xffb|1
a|\xa9a\xff|1
(?<=a)b|\x80\x80\x80b|3
(?<=a)b|a\x80\x80b|3
(?<=a)b|\xff\xc3\xa9\xa9b|4
a|a\xff|0
a|\xffa|2
(?<=a)b|\x80b|1
b|\x80b|0
a|a b\xff|0
a(?=..)|a b\xff|0
a|\xa9a\xff|5"""
for line in PINNED.splitlines():
    pat, subj, pos = line.rsplit('|', 2)
    for mode in "SA":
        add("pinned", pat, unesc(subj), int(pos), mode)

# ---- lb: every LB pattern at startpos LB and LB + 1 ----------------------
# LB itself is the oracle's answer (PCRE2_INFO_MAXLOOKBEHIND), so the
# question set covers startpos 0..4 (every LB in the list is <= 3) and the
# checker picks the pair it needs; the subject is lb.c's own.
lbsubj = b"\xff" + b"z" * 10
for pat in LB_PATTERNS:
    for pos in range(0, 5):
        for mode in "SA":
            add("lb", pat, lbsubj, pos, mode)
    # and a subject the pattern can MATCH on, so an answer is not only -1
    for subj in (b"\xffab", b"\xffxab", b"\xffbcd", b"\xffzzab"):
        for pos in range(0, len(subj) + 1):
            add("lb", pat, subj, pos, "S")

# ---- kinds: every ill-formed kind at three depths ------------------------
KINDS = [
    b"\xff", b"\xfe", b"\xf5\x80\x80\x80", b"\xf8\x88\x80\x80\x80",
    b"\x80", b"\xbf", b"\x80\x80",                       # stray continuations
    b"\xc3", b"\xe2\x82", b"\xf0\x9f\x98",               # truncated, then 'x'
    b"\xc0\x80", b"\xc1\xbf", b"\xe0\x80\x80", b"\xe0\x9f\xbf",
    b"\xf0\x80\x80\x80", b"\xf0\x8f\xbf\xbf",            # overlong
    b"\xed\xa0\x80", b"\xed\xbf\xbf",                    # surrogates
    b"\xf4\x90\x80\x80", b"\xf7\xbf\xbf\xbf",            # > U+10FFFF
    b"\xc3\x28", b"\xe2\x28\xa1", b"\xe2\x82\x28",       # bad continuation
]
for pat in ("a", "(?<=a)b", r"\bb", "(a)"):
    for depth in (1, 7, 17):
        for kind in KINDS:
            subj = b"a" * depth + kind + b"xab"
            bad = depth
            for pos in sorted({0, bad - 1, bad, bad + 1, len(subj)}):
                if 0 <= pos <= len(subj):
                    add("kinds", pat, subj, pos, "S")
                    add("kinds", pat, subj, pos, "A")
    # a truncated sequence at the very END (no byte after it)
    for kind in (b"\xc3", b"\xe2\x82", b"\xf0\x9f\x98"):
        subj = b"ab" + kind
        for pos in range(0, len(subj) + 1):
            add("kinds", pat, subj, pos, "S")
# the fast path's own windows: one bad byte after k ASCII bytes, k = 0..24,
# and a valid two-byte character after k ASCII bytes (no error at all)
for k in range(0, 25):
    add("kinds", "a", b"b" * k + b"\xff" + b"a", 0, "S")
    add("kinds", "a", b"b" * k + b"\xc3\xa9" + b"a", 0, "S")
    add("kinds", "a", b"b" * k + b"\xe6\x97\xa5" * 3 + b"\x80a", 0, "S")

# ---- align: every startpos of subjects with multi-byte characters --------
def aligned(subj, pos):
    """-fstartpos-guard=align's rule, from bytes alone: a position > 0
    inside the subject on a continuation byte (0x80-0xBF) moves forward to
    the first byte that is not one, or to n. Offset 0 never moves."""
    if pos == 0 or pos >= len(subj):
        return pos
    while pos < len(subj) and (subj[pos] & 0xC0) == 0x80:
        pos += 1
    return pos
ALIGN_SUBJ = [
    "éaéb".encode(), "日本ab日b".encode(),
    "x\U0001d11eab".encode(), "aééabé".encode(),
    b"\xc3\xa9a\xff", b"\xe6\x97\xa5a\xffb", b"\xffa\xc3\xa9b",
]
for pat in ("a", "b", "(?<=a)b", "(?<=.)b", r"\bb", r"\Gb", "x*", "(a)",
            "(?<=..)a", ".b"):
    for subj in ALIGN_SUBJ:
        for pos in range(0, len(subj) + 2):
            for mode in "SA":
                add("align", pat, subj, pos, mode, aligned(subj, pos))

# ---- random: a seeded differential --------------------------------------
rng = random.Random(20260930)
FRAG = [b"a", b"b", b"z", b" ", "é".encode(), "日".encode(),
        "\U0001d11e".encode(), b"\xff", b"\x80", b"\xc3", b"\xe2\x82",
        b"\xed\xa0\x80", b"\xc0\x80"]
RPAT = ["a", "b", "(?<=a)b", r"\bb", "(?<=..)b", "x*", "(a|é)+", "a.b",
        r"\Ab|z", "(?<=é)b"]
for _ in range(1500):
    pat = rng.choice(RPAT)
    subj = b"".join(rng.choice(FRAG) for _ in range(rng.randint(0, 8)))
    pos = rng.randint(0, len(subj) + 1)
    add("random", pat, subj, pos, rng.choice("SA"))

out = sys.stdout
out.write("# set\tpattern\tsubject_hex\tstartpos\tmode\tqpos\n")
for r in rows:
    out.write("\t".join(str(x) for x in r) + "\n")
