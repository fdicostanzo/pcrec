#!/usr/bin/env python3
"""gen_island_rxt.py -- [UCP] U3 lane ucpu3b: GENERATES the island's two .rxt
files from the resolved libpcre2 (ctypes), never from pcrec.

    gen_island_rxt.py WELL_OUT ILL_OUT

WELL_OUT (tests/ucp/island.rxt): well-formed subjects, oracle PCRE2_UTF|UCP
(verify_ucp.py re-checks every m/n/ms/ns cell on every make test-ucp), plus
`mc` find-all counts from PCRE2's own global loop (NOTEMPTY_ATSTART|ANCHORED
retry after an empty match), which exercise the island retry machine.
ILL_OUT (tests/utf8/island_illformed.rxt): subjects with ill-formed UTF-8,
oracle PCRE2_UTF|UCP|MATCH_INVALID_UTF (pcrec's ruled utf8 semantics). An
EMPTY match beside an ill-formed byte is match_api.md 9.5's documented
divergence of pcrec's byte machines, which the island inherits: such cells
are LEFT OUT (counted in the header), never written with pcrec's answer.
"""
import ctypes
import random
import sys

UTF, UCP, MIU = 0x00080000, 0x00020000, 0x04000000
NOTEMPTY_ATSTART, ANCHORED = 0x00000008, 0x80000000
lib = ctypes.CDLL("libpcre2-8.so.0")
lib.pcre2_compile_8.restype = ctypes.c_void_p
lib.pcre2_compile_8.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_uint32,
                                ctypes.POINTER(ctypes.c_int),
                                ctypes.POINTER(ctypes.c_size_t), ctypes.c_void_p]
lib.pcre2_match_data_create_8.restype = ctypes.c_void_p
lib.pcre2_match_data_create_8.argtypes = [ctypes.c_uint32, ctypes.c_void_p]
lib.pcre2_match_8.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t,
                              ctypes.c_size_t, ctypes.c_uint32, ctypes.c_void_p,
                              ctypes.c_void_p]
lib.pcre2_get_ovector_pointer_8.restype = ctypes.POINTER(ctypes.c_size_t)
lib.pcre2_get_ovector_pointer_8.argtypes = [ctypes.c_void_p]
lib.pcre2_config_8.argtypes = [ctypes.c_uint32, ctypes.c_void_p]

# (comment, pattern, hand subjects). Every pattern carries (*UCP); the block
# says `encoding utf8`.
PATTERNS = [
    ("T4 row 1: UCP \\b around a literal", r"(*UCP)\bfoo\b",
     ["foo", "éfoo", "fooé", "a foo b", "·foo·", "_foo", "foó", "日foo"]),
    ("the headline: a Unicode word", r"(*UCP)\b\w+\b",
     ["héllo wörld", "日本語 テキスト", "áb c", "٣٤ x", "😀ab😀", "Ωmega", "__"]),
    ("\\B between word characters", r"(*UCP)\B\w\B",
     ["abc", "éàü", "ab", "日本語", "x"]),
    ("a wide consuming set beside \\b (one character edge)", r"(*UCP)\w+\b",
     ["αβγ δ", "ǅx", "a b"]),
    ("a non-ASCII literal before \\b", r"(*UCP)é\b",
     ["é", "éa", "éé", "é ", "café"]),
    ("a narrow set (\\d) with \\b", r"(*UCP)\b\d+\b",
     ["12 34", "a12", "١٢٣", "x٣", "12é"]),
    ("trailing \\B", r"(*UCP)x\B",
     ["x", "xé", "x ", "xx"]),
    ("$ and \\z after \\b (the forward machine's position views)", r"(*UCP)\bfoo\b$",
     ["foo", "foo\n", "a foo", "foo\n\n", "éfoo"]),
    ("\\z", r"(*UCP)\bfoo\b\z", ["foo", "foo\n", "x foo"]),
    ("(?m)$ after \\b", r"(*UCP)(?m)\bfoo$", ["foo\nx", "afoo\n", "é foo\nb"]),
    ("alternation across \\b", r"(*UCP)(?:\bab|cd\b)", ["xab", "ab", "cdé", "cd"]),
    ("a property class between boundaries", r"(*UCP)\b\p{Greek}+\b",
     ["αβγ", "aαβ", "αβ δ", "Ωx"]),
    ("caseless", r"(*UCP)(?i)\bstra\w+e\b",
     ["STRAßE", "straße", "xstraße", "Strasse"]),
    ("nullable: the iterator's retry machine", r"(*UCP)\b\w*",
     ["ab cd", "é", "", " ", "日本 語"]),
    ("a bare \\b", r"(*UCP)\b", ["ab", "é é", "", "·"]),
    ("a bare \\B", r"(*UCP)\B", ["ab", "é", "", " a"]),
    ("a lookbehind context set beside \\b (two context sets)", r"(*UCP)(?<=\$)\d+\b",
     ["$12", "$12é", "$12 ", "x12"]),
    ("a dot between boundaries", r"(*UCP).\b.", ["ab", "a b", "é ", " é", "日本"]),
    ("a negated wide set", r"(*UCP)\b\S+\b", ["héllo, wörld", "-x-"]),
]

TOK = ["a", "b", "f", "o", "x", "_", "1", " ", "-", "\n", ".", "é", "ß", "α", "日",
       "😀", "́", "٣", "·", " ", "Ω", " ", "ǅ", "\U0001D7D8", "foo",
       "é foo", "$"]
BAD = [b"\x80", b"\xff", b"\xc3", b"\xe6\x97", b"\xc0\x80", b"\xed\xa0\x80",
       b"\xf4\x90\x80\x80", b"\xbf", b"\xf0\x9f", b"\xc2"]


def compile_(pat, opts):
    err, off = ctypes.c_int(), ctypes.c_size_t()
    b = pat.encode()
    code = lib.pcre2_compile_8(b, len(b), opts, ctypes.byref(err), ctypes.byref(off), None)
    if not code:
        raise SystemExit("pcre2 refused %r (%d)" % (pat, err.value))
    return code


MD = lib.pcre2_match_data_create_8(64, None)


def run(code, s, sp, flags=0):
    rc = lib.pcre2_match_8(code, s, len(s), sp, flags, MD, None)
    if rc == -1:
        return None
    if rc < 0:
        return "E"
    ov = lib.pcre2_get_ovector_pointer_8(MD)
    return (ov[0], ov[1])


def findall_count(code, s):
    """PCRE2's global loop (pcre2demo's): after an empty match retry
    NOTEMPTY_ATSTART|ANCHORED at the same offset, else advance one character."""
    pos, n = 0, 0
    while pos <= len(s):
        r = run(code, s, pos)
        if r is None or r == "E":
            return n if r is None else None
        n += 1
        if r[0] == r[1]:
            r2 = run(code, s, r[1], NOTEMPTY_ATSTART | ANCHORED)
            if r2 not in (None, "E"):
                n += 1
                pos = r2[1]
                continue
            pos = r[1] + 1
            while pos < len(s) and 0x80 <= s[pos] <= 0xBF:
                pos += 1
        else:
            pos = r[1]
    return n


def bad_mask(s):
    bad = [False] * len(s)
    i = 0
    while i < len(s):
        b0 = s[i]
        ln = (1 if b0 < 0x80 else 2 if b0 & 0xE0 == 0xC0 else 3 if b0 & 0xF0 == 0xE0
              else 4 if b0 & 0xF8 == 0xF0 else 0)
        ok = False
        if ln and i + ln <= len(s):
            try:
                ok = len(s[i:i + ln].decode("utf-8")) == 1
            except UnicodeDecodeError:
                ok = False
        if ok:
            i += ln
        else:
            bad[i] = True
            i += 1
    return bad


def esc(s):
    out = []
    for c in s:
        if c == 0x22:
            out.append('\\"')
        elif c == 0x5C:
            out.append("\\\\")
        elif c == 0x0A:
            out.append("\\n")
        elif 0x20 <= c < 0x7F:
            out.append(chr(c))
        else:
            out.append("\\x%02x" % c)
    return "".join(out)


def starts(s):
    """startpos values a caller may pass: never at a continuation byte."""
    return [p for p in range(len(s) + 1) if p == len(s) or not 0x80 <= s[p] <= 0xBF]


def main():
    well_out, ill_out = sys.argv[1], sys.argv[2]
    buf = ctypes.create_string_buffer(64)
    lib.pcre2_config_8(11, buf)
    ver = buf.value.decode()
    rnd = random.Random(20261110)
    well, ill = [], []
    nill_exempt = 0
    for comment, pat, hand in PATTERNS:
        cw = compile_(pat, UTF | UCP)
        cm = compile_(pat, UTF | UCP | MIU)
        subs = [h.encode() for h in hand]
        for _ in range(6):
            subs.append("".join(rnd.choice(TOK) for _ in range(rnd.randint(1, 6))).encode())
        lines = []
        for s in subs:
            r = run(cw, s, 0)
            lines.append('m "%s" %d %d' % ((esc(s),) + r) if r else 'n "%s"' % esc(s))
            sp = rnd.choice(starts(s)[1:] or [0])
            if sp:
                r = run(cw, s, sp)
                lines.append('ms %d "%s" %d %d' % ((sp, esc(s)) + r) if r
                             else 'ns %d "%s"' % (sp, esc(s)))
        for s in subs[:4]:
            c = findall_count(cw, s)
            if c is not None:
                lines.append('mc "%s" %d' % (esc(s), c))
        well.append("# %s\n# pcre2-only\npattern %s\nencoding utf8\nfeatures all\n%s\n"
                    % (comment, pat, "\n".join(lines)))
        lines = []
        for _ in range(10):
            parts = [rnd.choice(TOK).encode() if rnd.random() > 0.3 else rnd.choice(BAD)
                     for _ in range(rnd.randint(1, 6))]
            s = b"".join(parts)
            for sp in sorted(set(rnd.sample(starts(s), min(2, len(starts(s)))) + [0])):
                r = run(cm, s, sp)
                if r == "E":
                    continue
                if r and r[0] == r[1]:
                    bad = bad_mask(s)
                    p = r[0]
                    if (p < len(s) and bad[p]) or (p > 0 and bad[p - 1]):
                        nill_exempt += 1
                        continue
                if sp == 0:
                    lines.append('m "%s" %d %d' % ((esc(s),) + r) if r else 'n "%s"' % esc(s))
                else:
                    lines.append('ms %d "%s" %d %d' % ((sp, esc(s)) + r) if r
                                 else 'ns %d "%s"' % (sp, esc(s)))
        ill.append("# %s\n# pcre2-only\npattern %s\nencoding utf8\nfeatures all\n%s\n"
                   % (comment, pat, "\n".join(lines)))
    with open(well_out, "w") as f:
        f.write(
            "# [UCP] U3 -- THE ISLAND: the character-stepped DFA (ucp_design.md §3,\n"
            "# D134 item 1). Every pattern here holds a context set this encoding\n"
            "# cannot express byte by byte (UCP \\b/\\B under utf8: T4 row 1), so it\n"
            "# takes the `island` LOCATE row (RX_DFA_SCAN \"island\"): ASCII bytes step\n"
            "# the table, a non-ASCII character steps as its character atom. Cells:\n"
            "# wide and narrow consuming sets beside \\b, the forward machine's\n"
            "# position views ($, \\z, (?m)$), two context sets on one machine,\n"
            "# startpos seeds (the character before search_from), and `mc` find-all\n"
            "# counts, whose empty matches run the island retry machine.\n"
            "#\n"
            "# ORACLE: libpcre2 %s, PCRE2_UTF|PCRE2_UCP (`mc`: PCRE2's own global loop),\n"
            "# GENERATED by docs/dev/lanes/ucpu3b_evidence/gen_island_rxt.py, never\n"
            "# from pcrec. verify_ucp.py re-checks the m/n/ms/ns cells; the harness\n"
            "# runs pcrec on all of them. Ill-formed subjects: tests/utf8/\n"
            "# island_illformed.rxt.\n\n" % ver)
        f.write("\n".join(well))
    with open(ill_out, "w") as f:
        f.write(
            "# [UCP] U3 -- THE ISLAND over ILL-FORMED UTF-8 (ucp_design.md §3.5): a\n"
            "# byte that does not decode is ⊥, one byte in no set and not a word\n"
            "# character, forward, in the reverse walk's step back, and in the seeds.\n"
            "# Same patterns as tests/ucp/island.rxt, subjects mixing well-formed\n"
            "# characters with stray continuations, truncated leads, 0xFF, overlongs,\n"
            "# surrogates and > U+10FFFF.\n"
            "#\n"
            "# ORACLE: libpcre2 %s under PCRE2_UTF|PCRE2_UCP|PCRE2_MATCH_INVALID_UTF\n"
            "# (pcrec's ruled `-e utf8` semantics), GENERATED by docs/dev/lanes/\n"
            "# ucpu3b_evidence/gen_island_rxt.py. %d cells whose answer is an EMPTY\n"
            "# match beside an ill-formed byte are left out: match_api.md §9.5's\n"
            "# documented divergence of pcrec's byte machines, which the island\n"
            "# inherits. verify_ucp.py cannot check this file (it spells the options\n"
            "# as in-pattern verbs, and plain PCRE2_UTF refuses these subjects), which\n"
            "# is why it lives here, beside axis13_ctx_illformed.rxt.\n\n"
            % (ver, nill_exempt))
        f.write("\n".join(ill))
    print("wrote %s (%d blocks), %s (%d blocks, %d exempt cells left out), oracle %s"
          % (well_out, len(well), ill_out, len(ill), nill_exempt, ver))


main()
