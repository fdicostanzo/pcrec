#!/usr/bin/env python3
r"""[START-LANDING] exhaustive short subjects for one artifact (STUDY).

    mksubj.py ART.c PREFIX ENC OUT.hex [MAXSUBJ]

The alphabet is one representative byte per byte class of the artifact's
FORWARD machine (`<p>_forward_byte_class[256]`, read from the emitted text).
Every string over the alphabet up to the longest length whose total stays
under MAXSUBJ (default 40000) is written, one hex line each: a
machine-derived, pattern-specific exhaustive pool (E9's shape).

REVISION 2 (lane landrev, SL-E4). Under utf8 the alphabet is three parts, and
only the first is ever thinned:
  1. the ASCII class representatives (at most 6, spread over the classes);
  2. CLASS-OWN MULTIBYTE CHARACTERS: per multibyte lead class of the
     forward machine (at most 8, the smallest classes first), every
     combination of continuation-class representatives, the well-formed ones
     ranked by the summed size of the classes they use, the 3 most specific
     kept -- so the pattern's OWN characters are in the pool (rev 1 used a
     fixed 2/3/4-byte triple that a class like `[\x{400}-\x{4FF}]` never
     contains; run 2's smallest-continuation choice left 24 of 274 rows'
     pools without one matching subject);
  3. THE ILL-FORMED TOKENS, ALWAYS KEPT (rev 1's thinning dropped the
     truncated lead past 9 tokens): each chosen lead class TRUNCATED (the
     lead alone; a 3/4-byte lead also with its first continuation), a lone
     continuation, truncated 2/3/4-byte
     leads, 0xFF, an overlong lead (C0), overlong 3- and 4-byte forms, a
     surrogate (ED A0 80), a code point above U+10FFFF (F4 90 80 80), F5, and
     LEAD RUNS (C3 C3 C3 C3, E2 E2 E2, F0 F0) -- the shapes SL-E1's quadratic
     restart lived on.
Exhaustive to the length the cap allows (2 or 3 under utf8 with the full
alphabet), then a seeded random tail of longer strings (4-12 tokens) to fill
the cap, so every token also appears in runs and mixed contexts.
"""
import itertools, random, re, sys

art, P, enc, out = sys.argv[1:5]
cap = int(sys.argv[5]) if len(sys.argv) > 5 else 40000
src = open(art).read()
m = re.search(r"%s_forward_byte_class\[256\] = \{([^}]*)\}" % re.escape(P), src)
cl = None
if m:
    cl = [int(x) for x in m.group(1).replace("\n", " ").split(",") if x.strip()]


def wf_first(lead):
    """The smallest well-formed character with this lead byte, or None."""
    if 0xC2 <= lead <= 0xDF: return bytes([lead, 0x80])
    if lead == 0xE0: return bytes([lead, 0xA0, 0x80])
    if 0xE1 <= lead <= 0xEF and lead != 0xED: return bytes([lead, 0x80, 0x80])
    if lead == 0xED: return bytes([lead, 0x80, 0x80])
    if lead == 0xF0: return bytes([lead, 0x90, 0x80, 0x80])
    if 0xF1 <= lead <= 0xF3: return bytes([lead, 0x80, 0x80, 0x80])
    if lead == 0xF4: return bytes([lead, 0x80, 0x80, 0x80])
    return None


def wf(b):
    try:
        b.decode("utf8"); return True
    except UnicodeDecodeError:
        return False


ascii_t, mb_t, bad_t = [], [], []
if cl:
    seen = {}
    for b, c in enumerate(cl):
        if c not in seen: seen[c] = b
    for c in list(seen):                      # printable reps where a class has one
        for b in range(0x20, 0x7f):
            if cl[b] == c: seen[c] = b; break
    reps = sorted(seen.values())
    ascii_t = [bytes([b]) for b in reps if b < 0x80 or enc != "utf8"]
else:
    ascii_t = [bytes([b]) for b in b"a1 _\n"]
if enc == "utf8":
    # 2. CLASS-OWN multibyte characters (rev 2 run 3: run 2's "smallest
    # continuation" choice paired a continuation class with the FIRST lead
    # only, so `é(?:x$)?`'s pool never held C3 A9, and 24 of 274 rows' ex
    # pools held no matching subject at all). Per lead class (the smallest
    # classes first: the pattern's own), every combination of continuation
    # CLASS representatives at each position is tried; the well-formed ones
    # are ranked by specificity (the summed size of the classes they use,
    # smallest first) and the best 3 per lead class are kept.
    size = {}
    for b in range(256):
        c = cl[b] if cl else b
        size[c] = size.get(c, 0) + 1
    lead_cls = {}
    for lead in range(0xC2, 0xF5):
        c = cl[lead] if cl else lead
        if c not in lead_cls and wf_first(lead): lead_cls[c] = lead
    leads = sorted(lead_cls.values(), key=lambda b: (size[cl[b] if cl else b], b))[:8]
    cont = {}
    for b in range(0x80, 0xC0):
        cont.setdefault(cl[b] if cl else b, b)
    creps = sorted(cont.values())
    for lead in leads:
        k = len(wf_first(lead)) - 1
        cands = []
        for tail in itertools.islice(itertools.product(creps, repeat=k), 512):
            ch = bytes([lead]) + bytes(tail)
            if wf(ch):
                cands.append((sum(size[cl[b] if cl else b] for b in ch), ch))
        cands.sort()
        mb_t += [ch for _, ch in cands[:3]]
    mb_t = list(dict.fromkeys(mb_t))
    if not mb_t:
        mb_t = [b"\xc3\xa9", b"\xe2\x82\xac", b"\xf0\x9f\x98\x80"]
    # 3. the ill-formed tokens: always kept. First the CLASS-OWN TRUNCATIONS
    # (rev 2 run 2: the fixed C3/E2/F0 set below never truncates a lead the
    # pattern itself starts with -- `(?i)s`'s C5, `[α-ω]`'s CE -- and the
    # no-guard control passed on exactly those rows): every chosen lead
    # alone, and for a 3- or 4-byte lead its first continuation too.
    trunc_t = []
    for lead in leads:
        f = wf_first(lead)
        trunc_t.append(bytes([lead]))
        if len(f) >= 3: trunc_t.append(f[:2])
    bad_t = trunc_t + [b"\x80", b"\xc3", b"\xe2\x82", b"\xf0\x9f\x98", b"\xff", b"\xc0\x80",
             b"\xe0\x80\x80", b"\xf0\x80\x80\x80", b"\xed\xa0\x80", b"\xf4\x90\x80\x80",
             b"\xf5\x80", b"\xc3\xc3\xc3\xc3", b"\xe2\xe2\xe2", b"\xf0\xf0"]
    bad_t = list(dict.fromkeys(bad_t))
    # thin ONLY the ASCII part, keeping the first and last class and a spread
    while len(ascii_t) > 6:
        ascii_t = ascii_t[::2] + ([ascii_t[-1]] if ascii_t[-1] not in ascii_t[::2] else [])
else:
    while len(ascii_t) > 9:
        ascii_t = ascii_t[::2]
toks = ascii_t + mb_t + bad_t
L, tot = 0, 1
while tot + len(toks) ** (L + 1) <= cap:
    L += 1; tot += len(toks) ** L
rnd = random.Random(0x1A9D)
extra = max(0, cap - tot) if enc == "utf8" else 0
with open(out, "w") as f:
    for n in range(L + 1):
        for w in itertools.product(toks, repeat=n):
            f.write(b"".join(w).hex() + "\n")
    for _ in range(extra):
        f.write(b"".join(rnd.choice(toks) for _ in range(rnd.randint(L + 1, 12))).hex() + "\n")
print("%d tokens (%d ascii, %d multibyte, %d ill-formed), exhaustive length <= %d, %d subjects"
      % (len(toks), len(ascii_t), len(mb_t), len(bad_t), L, tot + extra))
