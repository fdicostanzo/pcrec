#!/usr/bin/env python3
"""tests/axes/utfcheck_arm.py -- `-futf-check`'s OWN ARM of `make test-axes`
([UTF-VALID], docs/spec/tuning.md §2.36; utf_valid_design.md §4.1/§7).

`-futf-check` is a CONTRACT axis: it gives a different answer on purpose
wherever a cell's checked range is ill-formed, and the corpus carries such
cells (tests/utf8/k73_startskip.rxt and the ill-formed axes). So run_axes.sh
EXCLUDES it from the identity sweep by name and runs this instead, over the
same two RXTDUMPs (the default build's and the `RXTFLAGS=-futf-check` one):

  byte block   the flag is INERT: the answer must be the default's, exactly
  utf8 block   the answer must be the default's iff the cell's checked range
               [startpos - LB, n) is well-formed, and otherwise `utf <off>`
               (tests/harness/driver.c's word for PCREC_ERR_UTF) with <off>
               the first ill-formed sequence's first byte

THE ORACLE IS NOT PCREC. Well-formedness and the offset are python's strict
`bytes.decode('utf-8')` over the range the design's §1.3 walk defines
(transcribed from the design, not from the C); LB is libpcre2's own
PCRE2_INFO_MAXLOOKBEHIND for the block's pattern (the borrowed
pcre2_ctypes binding). A cell whose LB cannot be had (no libpcre2, or a
pattern libpcre2 does not compile) is checked only where LB cannot matter
(startpos 0), and counted, never dropped. A mid-character startpos > 0 is
the K50 guard's, which runs FIRST: both builds answer it identically.

Usage: utfcheck_arm.py BASE_DUMP UTF_DUMP ROOT_DIR
"""
import ctypes, os, re, sys

base_dump, utf_dump, root = sys.argv[1:4]
sys.path.insert(0, os.path.join(root, "docs/design/eng_brep_measurements/probes"))
try:
    import pcre2_ctypes as P
    P._lib.pcre2_pattern_info_8.restype = ctypes.c_int
    P._lib.pcre2_pattern_info_8.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_void_p]
    HAVE_PCRE2 = True
except Exception as e:                      # noqa: BLE001 - reported, not hidden
    print(f"utfcheck arm: libpcre2 unavailable ({e}); LB-dependent cells are counted unchecked")
    HAVE_PCRE2 = False
PCRE2_UTF, INFO_MAXLOOKBEHIND = 0x00080000, 15

_lb_cache = {}
def lb_of(pat):
    if not HAVE_PCRE2:
        return None
    if pat not in _lb_cache:
        try:
            c = P.Compiled(pat.encode("utf-8", "surrogateescape"), PCRE2_UTF)
            v = ctypes.c_uint32(0)
            rc = P._lib.pcre2_pattern_info_8(c._code, INFO_MAXLOOKBEHIND, ctypes.byref(v))
            _lb_cache[pat] = v.value if rc == 0 else None
        except P.Pcre2Error:
            _lb_cache[pat] = None
    return _lb_cache[pat]

def stepback(s, pos, lb):
    for _ in range(lb):
        if pos == 0: break
        pos -= 1
        while pos > 0 and (s[pos] & 0xC0) == 0x80:
            pos -= 1
    return pos

def py_offset(s, pos, lb):
    f = stepback(s, pos, lb)
    try:
        s[f:].decode("utf-8"); return len(s)
    except UnicodeDecodeError as e:
        return f + e.start

ESC = {'"': 0x22, '\\': 0x5C, 'n': 10, 't': 9, 'r': 13, 'f': 12, 'v': 11}
def unquote(text):
    """The .rxt subject vocabulary (docs/spec/rxt_format.md): returns the
    bytes and the rest of the line after the closing quote."""
    assert text[0] == '"'
    out = bytearray(); i = 1
    while i < len(text):
        c = text[i]
        if c == '"':
            return bytes(out), text[i+1:]
        if c == '\\':
            d = text[i+1]
            if d == 'x':
                out.append(int(text[i+2:i+4], 16)); i += 4; continue
            out.append(ESC[d]); i += 2; continue
        out.extend(c.encode("utf-8", "surrogateescape")); i += 1
    raise ValueError("unterminated subject")

_files = {}
def cell(path, line):
    """(encoding, pattern, subject, startpos) for the case at path:line, from
    the file itself: the block is the nearest `pattern` line above it, and its
    `encoding` line (block-scoped) if any. None for a line this reader cannot
    place (a named `@file:` subject, a pattern-esc block)."""
    if path not in _files:
        with open(path, encoding="utf-8", errors="surrogateescape") as f:
            _files[path] = f.read().split("\n")
    lines = _files[path]
    enc, pat = "byte", None
    for i in range(line - 1, -1, -1):
        l = lines[i].strip()
        if l.startswith("encoding ") and pat is None:
            enc = l.split()[1]
        if l.startswith("pattern-esc "):
            return None
        if l.startswith("pattern "):
            pat = lines[i].lstrip()[len("pattern "):]
            break
    if pat is None:
        return None
    l = lines[line - 1].strip()
    m = re.match(r'^(?:under\s+\S+\s+)?(m|n|ms|ns|mc|gu)\s+(?:(\d+)\s+|\S+\s+)?(".*)$', l)
    if not m:
        return None
    kind, pos, rest = m.group(1), m.group(2), m.group(3)
    if kind == "gu":
        pos = None
    try:
        subj, _ = unquote(rest)
    except (ValueError, KeyError, IndexError):
        return None
    return enc, pat, subj, int(pos) if pos and kind in ("ms", "ns") else 0

def load(p):
    d = {}
    with open(p, encoding="utf-8", errors="surrogateescape") as f:
        for ln in f:
            c = ln.rstrip("\n").split("\t")
            if len(c) >= 6:
                d[(c[0], int(c[1]))] = (c[2], c[3], c[4], c[5])
    return d

base, utf = load(base_dump), load(utf_dump)
n = dict(byte=0, utf8=0, refused=0, agree=0, unplaced=0, lb_unchecked=0,
         guard=0, fail=0, lost=0, gained=0)
fails = []
for key, b in base.items():
    u = utf.get(key)
    if u is None:
        n["lost"] += 1; fails.append(f"LOST {key[0]}:{key[1]}"); continue
    path = key[0] if os.path.isabs(key[0]) else os.path.join(root, key[0])
    c = cell(path, key[1]) if b[2] != "REFUSED" else None
    if c is None or c[0] != "utf8":
        # byte (inert), a compile refusal, or a line this reader cannot place
        if c is None and b[2] != "REFUSED": n["unplaced"] += 1
        else: n["byte"] += 1
        if u != b:
            n["fail"] += 1
            fails.append(f"{key[0]}:{key[1]}: -futf-check moved an answer it cannot act on: {b} -> {u}")
        continue
    enc, pat, subj, pos = c
    n["utf8"] += 1
    if 0 < pos < len(subj) and (subj[pos] & 0xC0) == 0x80:
        n["guard"] += 1              # K50 first: both builds refuse (-7)
        want = b
    else:
        lb = lb_of(pat) if pos > 0 else 0
        if lb is None:
            n["lb_unchecked"] += 1
            continue
        off = py_offset(subj, pos, lb) if pos <= len(subj) else len(subj)
        if off == len(subj):
            want = b
        else:
            want = (b[0], b[1], "3", f"utf {off}")
            n["refused"] += 1
    if u != want:
        n["fail"] += 1
        fails.append(f"{key[0]}:{key[1]}: want {want}, got {u} (pattern {pat!r}, subject {subj!r} @ {pos})")
    else:
        n["agree"] += 1
for key in utf:
    if key not in base:
        n["gained"] += 1; fails.append(f"GAINED {key[0]}:{key[1]}")

print("utfcheck arm: " + " ".join(f"{k}={v}" for k, v in n.items()))
for f in fails[:40]:
    print("  " + f)
# K35: the arm must REACH ill-formed utf8 cells, or it certifies nothing.
# Floors measured on the first full run and rounded down; a smaller corpus
# run (run_axes.sh FILE...) reports its own counts and is floored only at 1.
full = len(base) > 10000
floors = dict(utf8=900, refused=80) if full else dict(utf8=1, refused=1)
for k, fl in floors.items():
    if n[k] < fl:
        fails.append(f"population {k}={n[k]} below floor {fl}")
        print(f"  population {k}={n[k]} below floor {fl}")
sys.exit(1 if fails else 0)
