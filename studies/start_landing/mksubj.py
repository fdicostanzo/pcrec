#!/usr/bin/env python3
"""[START-LANDING] exhaustive short subjects for one artifact (STUDY).

    mksubj.py ART.c PREFIX ENC OUT.hex [MAXSUBJ]

The alphabet is one representative byte per byte class of the artifact's
FORWARD machine (`<p>_forward_byte_class[256]`, read from the emitted text).
Every string over the alphabet up to the longest length whose total stays
under MAXSUBJ (default 40000) is written, one hex line each: a
machine-derived, pattern-specific exhaustive pool (E9's shape).

REVISION 2 (lane landrev, SL-E4). Under utf8 the alphabet is three parts, and
only the first is ever thinned:
  1. the ASCII class representatives (at most 6, spread over the classes);
  2. ONE WELL-FORMED CHARACTER PER MULTIBYTE LEAD CLASS of the forward
     machine (the class's smallest well-formed lead, completed with the
     smallest continuation bytes Table 3-7 allows), so the pattern's OWN
     multibyte characters are in the pool (rev 1 used a fixed 2/3/4-byte
     triple that a class like `[\\x{400}-\\x{4FF}]` never contains), plus one
     character per continuation-byte class (the same lead, that class's
     representative as its last byte) where that is well-formed;
  3. THE ILL-FORMED TOKENS, ALWAYS KEPT (rev 1's thinning dropped the
     truncated lead past 9 tokens): a lone continuation, truncated 2/3/4-byte
     leads, 0xFF, an overlong lead (C0), overlong 3- and 4-byte forms, a
     surrogate (ED A0 80), a code point above U+10FFFF (F4 90 80 80), F5, and
     LEAD RUNS (C3 C3 C3 C3, E2 E2 E2, F0 F0) -- the shapes SL-E1's quadratic
     restart lived on.
Exhaustive to the length the cap allows (3 under utf8 with the full
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
    # 2. one well-formed character per multibyte lead class
    lead_cls = {}
    for lead in range(0xC2, 0xF5):
        c = cl[lead] if cl else lead
        if c not in lead_cls and wf_first(lead): lead_cls[c] = lead
    leads = sorted(lead_cls.values())
    while len(leads) > 8:                     # spread, first and last kept
        leads = leads[::2] + ([leads[-1]] if leads[-1] not in leads[::2] else [])
    mb_t = [wf_first(lead) for lead in leads]
    # and one per continuation class (at most 3): the last byte of a
    # multibyte form taken from that class
    if cl and mb_t:
        cont = {}
        for b in range(0x80, 0xC0):
            cont.setdefault(cl[b], b)
        nx = 0
        for c, b in sorted(cont.items(), key=lambda kv: kv[1]):
            for t in list(mb_t):
                cand = t[:-1] + bytes([b])
                if nx < 3 and wf(cand) and cand not in mb_t:
                    mb_t.append(cand); nx += 1; break
    if not mb_t:
        mb_t = [b"\xc3\xa9", b"\xe2\x82\xac", b"\xf0\x9f\x98\x80"]
    # 3. the ill-formed tokens: always kept
    bad_t = [b"\x80", b"\xc3", b"\xe2\x82", b"\xf0\x9f\x98", b"\xff", b"\xc0\x80",
             b"\xe0\x80\x80", b"\xf0\x80\x80\x80", b"\xed\xa0\x80", b"\xf4\x90\x80\x80",
             b"\xf5\x80", b"\xc3\xc3\xc3\xc3", b"\xe2\xe2\xe2", b"\xf0\xf0"]
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
