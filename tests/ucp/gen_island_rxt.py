#!/usr/bin/env python3
"""tests/ucp/gen_island_rxt.py -- [UCP] U3: GENERATES the character-stepped
DFA's two .rxt files from libpcre2 (ctypes), never from pcrec, and RE-CHECKS
them against libpcre2 (the ill-formed file's only oracle).

    gen_island_rxt.py WELL_OUT ILL_OUT [--diverge FILE]
    gen_island_rxt.py --verify FILE...

WELL_OUT (tests/ucp/island.rxt): well-formed subjects, oracle PCRE2_UTF|UCP,
plus `mg` find-all counts (rxt_format.md §1.7.1: PCRE2's own global loop,
NOTEMPTY_ATSTART|ANCHORED retry after an empty match, held against
`<prefix>_next`), which run the retry machine, and the
EDGE BLOCKS (review 2026-11-10 r4 ucpu3 checks-4): one single-character cell
at the first and last member of every interval of a set the machine steps,
and at the code point either side, so a segment lookup that is off by one at
any interval edge is red.
ILL_OUT (tests/utf8/island_illformed.rxt): subjects with ill-formed UTF-8,
oracle PCRE2_UTF|UCP|MATCH_INVALID_UTF (pcrec's ruled utf8 semantics), with
`mg` cells and hand cells that put an ill-formed byte at each place a walk
reads one (checks-2/6): the forward seed, a forward step, the reverse seed,
a reverse step, the retry.

THE DIVERGENCE (checks-3). An EMPTY match beside an ill-formed byte is where
pcrec's machines can differ from PCRE2 (match_api.md §9.5). Such a cell is
written like every other unless it is named in the `--diverge` file (one
`<pattern>\\t<cell line>` per row, taken from a harness run): those cells
alone are left out, and the file header COUNTS and NAMES them.

--verify re-checks every m/n/ms/ns/mg cell of each FILE against libpcre2
with the options its header declares (`# oracle-options: UTF|UCP[|MIU]`),
the only oracle the ill-formed file has (verify_ucp.py spells options as
in-pattern verbs, and MATCH_INVALID_UTF has none). Exit 0 = all agree;
SKIPS LOUDLY (exit 0) when libpcre2 cannot be loaded. A file with fewer
cells than its floor is red (a population is counted, K35).
"""
import ctypes
import os
import random
import re
import sys

UTF, UCP, MIU = 0x00080000, 0x00020000, 0x04000000
NOTEMPTY_ATSTART, ANCHORED = 0x00000008, 0x80000000
OPTS = {"UTF": UTF, "UCP": UCP, "MIU": MIU}
FLOOR = {"island.rxt": 3000, "island_illformed.rxt": 400}


def load_lib():
    """libpcre2-8: the resolved one's directory (PCRE2_LIBS -L) first."""
    names = []
    for tok in os.environ.get("PCRE2_LIBS", "").split():
        if tok.startswith("-L"):
            for n in ("libpcre2-8.so.0", "libpcre2-8.0.dylib", "libpcre2-8.dylib"):
                names.append(os.path.join(tok[2:], n))
    names += ["libpcre2-8.so.0", "libpcre2-8.0.dylib", "libpcre2-8.dylib"]
    for n in names:
        try:
            return ctypes.CDLL(n)
        except OSError:
            continue
    return None


lib = load_lib()
if lib is not None:
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
    MD = lib.pcre2_match_data_create_8(64, None)

# (comment, pattern, hand subjects). Every pattern carries (*UCP); the block
# says `encoding utf8`.
PATTERNS = [
    ("T4 row 1: UCP \\b around a literal", r"(*UCP)\bfoo\b",
     ["foo", "éfoo", "fooé", "a foo b", "·foo·", "_foo", "foó", "日foo"]),
    ("the headline: a Unicode word", r"(*UCP)\b\w+\b",
     ["héllo wörld", "日本語 テキスト", "áb c", "٣٤ x", "😀ab😀", "Ωmega", "__"]),
    ("\\B between word characters", r"(*UCP)\B\w\B",
     ["abc", "éàü", "ab", "日本語", "x"]),
    ("a wide consuming set beside \\b (one character edge)", r"(*UCP)\w+\b",
     ["αβγ δ", "ǅx", "a b"]),
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
    ("the retry machine SUCCEEDS: an empty first branch, then a word "
     "(checks-5)", r"(*UCP)\b(?:|\w+)",
     ["ab cd", "日本 語", "é", "a"]),
    ("the retry machine SUCCEEDS: a lazy word (checks-5)", r"(*UCP)\b\w*?",
     ["ab cd", "日本 語", "é x", "ab"]),
    ("a bare \\b", r"(*UCP)\b", ["ab", "é é", "", "·"]),
    ("a bare \\B", r"(*UCP)\B", ["ab", "é", "", " a"]),
    ("a lookbehind context set beside \\b (two context sets)", r"(*UCP)(?<=\$)\d+\b",
     ["$12", "$12é", "$12 ", "x12"]),
    ("a dot between boundaries", r"(*UCP).\b.", ["ab", "a b", "é ", " é", "日本"]),
    ("a negated wide set", r"(*UCP)\b\S+\b", ["héllo, wörld", "-x-"]),
]

# The edge blocks (checks-4): (comment, pattern, set probe, subject former).
# Each probe is the set's own membership, asked of libpcre2 at every non-ASCII
# code point; the cells are the oracle's answers on the formed subjects.
EDGES = [
    ("EDGE: the word set, read AFTER a word character (the forward machine's "
     "context side)", r"(*UCP)x\b", r"(*UCP)^\w", lambda c: "x" + c),
    ("EDGE: the word set, read BEFORE a word character (the reverse machine's "
     "and the seed's side)", r"(*UCP)\bx", r"(*UCP)^\w", lambda c: c + "x"),
    ("EDGE: a narrow consuming set (\\d) beside \\b", r"(*UCP)\b\d", r"(*UCP)^\d",
     lambda c: c),
    ("EDGE: a property set (\\p{Greek}) beside \\b", r"(*UCP)\b\p{Greek}",
     r"(*UCP)^\p{Greek}", lambda c: c),
]

TOK = ["a", "b", "f", "o", "x", "_", "1", " ", "-", "\n", ".", "é", "ß", "α", "日",
       "😀", "́", "٣", "·", " ", "Ω", " ", "ǅ", "\U0001D7D8", "foo",
       "é foo", "$"]
BAD = [b"\x80", b"\xff", b"\xc3", b"\xe6\x97", b"\xc0\x80", b"\xed\xa0\x80",
       b"\xf4\x90\x80\x80", b"\xbf", b"\xf0\x9f", b"\xc2"]
# Hand ill-formed subjects (checks-6): a bad byte where each walk reads one --
# first (the forward seed at a startpos after it), mid-word (a forward step,
# a reverse step), last (the reverse seed), and doubled (the retry's step).
HAND_ILL = [b"\x80foo", b"foo\x80", b"\xffab cd\xc3", b"\xe6\x97foo\xe6\x97",
            b"ab\x80cd", b"\xc3\xa9\x80\xc3\xa9", b"\x80\x80", b"a\xbf\xbfb",
            b"\xce\xb1\xff\xce\xb2"]


def compile_(pat, opts):
    err, off = ctypes.c_int(), ctypes.c_size_t()
    b = pat.encode()
    code = lib.pcre2_compile_8(b, len(b), opts, ctypes.byref(err), ctypes.byref(off), None)
    if not code:
        raise SystemExit("pcre2 refused %r (%d)" % (pat, err.value))
    return code


def run(code, s, sp, flags=0):
    rc = lib.pcre2_match_8(code, s, len(s), sp, flags, MD, None)
    if rc == -1:
        return None
    if rc < 0:
        return "E"
    ov = lib.pcre2_get_ovector_pointer_8(MD)
    return (ov[0], ov[1])


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


def findall_count(code, s):
    """PCRE2's global loop (pcre2demo's): after an empty match retry
    NOTEMPTY_ATSTART|ANCHORED at the same offset, else advance one byte and
    past every 0x80-0xBF byte (pcre2demo's step, which is also match_api.md
    §3.1.1's normative advance over ill-formed UTF-8)."""
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


def unesc(t):
    out, i = bytearray(), 0
    while i < len(t):
        c = t[i]
        if c == "\\":
            n = t[i + 1]
            if n == "x":
                out.append(int(t[i + 2:i + 4], 16))
                i += 4
                continue
            out.append({"n": 0x0A, '"': 0x22, "\\": 0x5C}[n])
            i += 2
            continue
        out += c.encode()
        i += 1
    return bytes(out)


def starts(s):
    """startpos values a caller may pass: never at a continuation byte (a
    stray one included: match_api.md §9.3's guard refuses it)."""
    return [p for p in range(len(s) + 1) if p == len(s) or not 0x80 <= s[p] <= 0xBF]


def cell(code, s, sp):
    r = run(code, s, sp)
    if r == "E":
        return None, None
    if sp == 0:
        return r, ('m "%s" %d %d' % ((esc(s),) + r) if r else 'n "%s"' % esc(s))
    return r, ('ms %d "%s" %d %d' % ((sp, esc(s)) + r) if r
               else 'ns %d "%s"' % (sp, esc(s)))


def intervals(code):
    """The set's non-ASCII members as intervals, asked of libpcre2."""
    out, lo = [], None
    for cp in range(0x80, 0x110000):
        if 0xD800 <= cp <= 0xDFFF:
            continue
        b = chr(cp).encode()
        inn = run(code, b, 0) not in (None, "E")
        if inn and lo is None:
            lo = cp
        if not inn and lo is not None:
            out.append((lo, prev))
            lo = None
        prev = cp
    if lo is not None:
        out.append((lo, prev))
    return out


def edge_block(comment, pat, probe, form):
    cw = compile_(pat, UTF | UCP)
    ivs = intervals(compile_(probe, UTF | UCP))
    cps = set()
    for lo, hi in ivs:
        for cp in (lo - 1, lo, hi, hi + 1):
            if 0x80 <= cp <= 0x10FFFF and not 0xD800 <= cp <= 0xDFFF:
                cps.add(cp)
    lines = []
    for cp in sorted(cps):
        _, ln = cell(cw, form(chr(cp)).encode(), 0)
        lines.append(ln)
    return ("# %s: %d intervals, %d edge cells\n# pcre2-only\npattern %s\n"
            "encoding utf8\nfeatures all\n%s\n" % (comment, len(ivs), len(lines), pat,
                                                   "\n".join(lines)))


def read_diverge(path):
    out = set()
    if path:
        with open(path) as f:
            for ln in f:
                ln = ln.rstrip("\n")
                if ln and not ln.startswith("#"):
                    out.add(tuple(ln.split("\t", 1)))
    return out


def generate(well_out, ill_out, diverge):
    buf = ctypes.create_string_buffer(64)
    lib.pcre2_config_8(11, buf)
    ver = buf.value.decode()
    rnd = random.Random(20261110)
    well, ill, left_out = [], [], []
    for comment, pat, hand in PATTERNS:
        cw = compile_(pat, UTF | UCP)
        cm = compile_(pat, UTF | UCP | MIU)
        subs = [h.encode() for h in hand]
        for _ in range(6):
            subs.append("".join(rnd.choice(TOK) for _ in range(rnd.randint(1, 6))).encode())
        lines = []
        for s in subs:
            lines.append(cell(cw, s, 0)[1])
            sp = rnd.choice(starts(s)[1:] or [0])
            if sp:
                lines.append(cell(cw, s, sp)[1])
        for s in subs[:4]:
            c = findall_count(cw, s)
            if c is not None:
                lines.append('mg "%s" %d' % (esc(s), c))
        well.append("# %s\n# pcre2-only\npattern %s\nencoding utf8\nfeatures all\n%s\n"
                    % (comment, pat, "\n".join(lines)))
        lines = []
        subs = list(HAND_ILL)
        for _ in range(10):
            parts = [rnd.choice(TOK).encode() if rnd.random() > 0.3 else rnd.choice(BAD)
                     for _ in range(rnd.randint(1, 6))]
            subs.append(b"".join(parts))
        for i, s in enumerate(subs):
            sps = {0}
            if i < len(HAND_ILL):
                bad = bad_mask(s)
                sps |= {p + 1 for p in range(len(s)) if bad[p]} & set(starts(s))
            else:
                sps |= set(rnd.sample(starts(s), min(2, len(starts(s)))))
            for sp in sorted(sps):
                r, ln = cell(cm, s, sp)
                if ln is None:
                    continue
                if (pat, ln) in diverge:
                    left_out.append((pat, ln))
                    continue
                lines.append(ln)
            c = findall_count(cm, s)
            if c is not None:
                ln = 'mg "%s" %d' % (esc(s), c)
                if (pat, ln) in diverge:
                    left_out.append((pat, ln))
                else:
                    lines.append(ln)
        ill.append("# %s\n# pcre2-only\npattern %s\nencoding utf8\nfeatures all\n%s\n"
                   % (comment, pat, "\n".join(lines)))
    for e in EDGES:
        well.append(edge_block(*e))
    stale = diverge - set(left_out)
    if stale:
        raise SystemExit("gen_island_rxt: --diverge rows no generated cell matches "
                         "(a stale list): %r" % sorted(stale)[:5])
    with open(well_out, "w") as f:
        f.write(
            "# [UCP] U3 -- THE CHARACTER-STEPPED DFA (ucp_design.md §3, D134 item 1).\n"
            "# Every pattern here holds a context set this encoding cannot express\n"
            "# byte by byte (UCP \\b/\\B under utf8), so it takes the character-stepped\n"
            "# DFA (RX_DFA_SCAN \"char-step\"; run_ucp_tests.sh §5 pins the route):\n"
            "# ASCII bytes step the table, a non-ASCII character steps as its\n"
            "# character atom. Cells: wide and narrow consuming sets beside \\b, the\n"
            "# forward machine's position views ($, \\z, (?m)$), two context sets on\n"
            "# one machine, startpos seeds (the character before search_from), `mg`\n"
            "# find-all counts whose empty matches run the retry machine (two\n"
            "# patterns where it SUCCEEDS), and the EDGE blocks: every interval edge\n"
            "# of the sets the machines step, one cell each.\n"
            "#\n"
            "# oracle-options: UTF|UCP\n"
            "# ORACLE: libpcre2 %s (`mg`: PCRE2's own global loop), GENERATED by\n"
            "# tests/ucp/gen_island_rxt.py, never from pcrec; its --verify mode and\n"
            "# verify_ucp.py re-check the cells. Ill-formed subjects:\n"
            "# tests/utf8/island_illformed.rxt.\n\n" % ver)
        f.write("\n".join(well))
    with open(ill_out, "w") as f:
        f.write(
            "# [UCP] U3 -- THE CHARACTER-STEPPED DFA over ILL-FORMED UTF-8\n"
            "# (ucp_design.md §3.5): a byte that does not decode is one ill-formed\n"
            "# character, in no set and not a word character, forward, in the\n"
            "# reverse walk's step back, in the seeds and in the retry. Same patterns\n"
            "# as tests/ucp/island.rxt; subjects mix well-formed characters with stray\n"
            "# continuations, truncated leads, 0xFF, overlongs, surrogates and\n"
            "# > U+10FFFF, plus hand subjects with a bad byte where each walk reads\n"
            "# one, every startpos just after a bad byte, and `mg` counts.\n"
            "#\n"
            "# oracle-options: UTF|UCP|MIU\n"
            "# ORACLE: libpcre2 %s under PCRE2_UTF|PCRE2_UCP|PCRE2_MATCH_INVALID_UTF\n"
            "# (pcrec's ruled `-e utf8` semantics), GENERATED by\n"
            "# tests/ucp/gen_island_rxt.py, re-checked by its --verify mode\n"
            "# (run_ucp_tests.sh §5).\n"
            "#\n"
            "# LEFT OUT: %d cell(s) where pcrec's answer DIFFERS from PCRE2's, each an\n"
            "# empty match beside an ill-formed byte (match_api.md §9.5's documented\n"
            "# divergence, inherited from the byte machines; known_issues.md). Every\n"
            "# other such cell is written, since it agrees:\n%s\n\n"
            % (ver, len(left_out),
               "\n".join("#   %s   %s" % (p, ln) for p, ln in left_out) or "#   (none)"))
        f.write("\n".join(ill))
    print("wrote %s (%d blocks), %s (%d blocks, %d diverging cells left out), oracle %s"
          % (well_out, len(well), ill_out, len(ill), len(left_out), ver))


CELL = re.compile(r'^(m|n|ms|ns|mg) (?:(\d+) )?"((?:[^"\\]|\\.)*)"(?: (\d+))?(?: (\d+))?$')


def verify(paths):
    if lib is None:
        print("gen_island_rxt --verify: SKIPPED -- libpcre2-8 cannot be loaded "
              "(the ill-formed file has no other oracle)")
        return 0
    rc = 0
    for path in paths:
        opts, code, pat = None, None, None
        npass = nfail = 0
        with open(path) as f:
            for ln in f:
                ln = ln.rstrip("\n")
                m = re.match(r"^# oracle-options: ([A-Z|]+)$", ln)
                if m:
                    opts = 0
                    for o in m.group(1).split("|"):
                        opts |= OPTS[o]
                    continue
                if ln.startswith("pattern "):
                    if opts is None:
                        raise SystemExit("%s: no `# oracle-options:` header" % path)
                    pat = ln[len("pattern "):]
                    code = compile_(pat, opts)
                    continue
                m = CELL.match(ln)
                if not m or code is None:
                    continue
                kind, sp, subj, a, b = m.groups()
                s = unesc(subj)
                if kind == "mg":
                    got = findall_count(code, s)
                    ok = got == int(a)
                else:
                    r = run(code, s, int(sp) if sp else 0)
                    ok = (r is None if kind in ("n", "ns")
                          else r not in (None, "E") and r == (int(a), int(b)))
                if ok:
                    npass += 1
                else:
                    nfail += 1
                    print("FAIL: %s: pattern %s: %s (libpcre2 disagrees)" % (path, pat, ln))
        floor = FLOOR.get(os.path.basename(path), 1)
        if npass + nfail < floor:
            print("FAIL: %s: only %d cells (floor %d) -- the file lost its population"
                  % (path, npass + nfail, floor))
            nfail += 1
        print("%s: %d cells agree with libpcre2, %d disagree" % (path, npass, nfail))
        rc |= 1 if nfail else 0
    return rc


def main(argv):
    if argv[1:2] == ["--verify"]:
        return verify(argv[2:])
    if lib is None:
        raise SystemExit("gen_island_rxt: libpcre2-8 cannot be loaded")
    div = None
    if "--diverge" in argv:
        div = argv[argv.index("--diverge") + 1]
    generate(argv[1], argv[2], read_diverge(div))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
