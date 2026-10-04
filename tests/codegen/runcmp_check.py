#!/usr/bin/env python3
"""tests/codegen/runcmp_check.py -- [OPT-LITSCAN] S4 C1's structural checks on
the RUN COMPARE (src/gen/runcmp.c; docs/design/litscan_s4.md §5.4;
docs/spec/tuning.md §2.38), run by run_codegen_tests.sh's [OPT-LITSCAN S4]
block. Prints one `PASS: ...` / `FAIL: ...` line per check.

    python3 runcmp_check.py PCREC WORKDIR CC

WHAT IT READS, AND WHY THE EXPECTATIONS COME FROM THE PATTERN. Each witness
names the run it must compare, written out from the PATTERN TEXT here, never
from the compiler. Every `<p>_w<W>(base + o) == <p>_w<W>("...")` chain the
artifact carries is decoded back into (offset, bytes) words, and the check
asks of each compare:

  1. EVERY WORD LIES INSIDE THE RUN and THE LAST WORD SITS AT EXACTLY L - W:
     `o + W <= L` with L the witness's own run length, the first word at 0,
     and no gap between words (the run's every byte is in some word).
  2. THE WORDS SPELL THE RUN: the bytes the words' constants decode to,
     placed at their offsets, are the witness's run byte for byte (an
     over-reading last word reads a byte the run does not have, a shifted
     one spells a different run).
  3. EVERY CONSTANT IS A STRING LITERAL, never an integer literal: an integer
     literal is a statement about the target's byte order.

Then, per artifact: the helpers are declared iff the artifact writes a word
compare, only the widths it uses, ahead of their first use; the
`<PREFIX>_RUN_WORDS` stamp equals the number of word compares in the text;
the pay-for-what-you-use directions (an L = 4, 8 or 16 run stays a `memcmp`);
under `-fno-run-overlap` no word compare and no helper remain, the stamp reads
0, and each word compare became exactly one `memcmp`; and every witness
compiles under the harness's own `-Wall -Wextra -Werror`.

Failing direction, recorded at the landing: sabotage rows S443 (last word at
L - W + 1) and S444 (at L - W - 1) each turn the offset/spelling checks red
on every overlap witness (docs/dev/lanes/s4build_report.md).
"""
import os
import re
import subprocess
import sys

PCREC, WORK, CC = sys.argv[1], sys.argv[2], sys.argv[3] or "cc"
npass = nfail = 0


def ok(msg):
    global npass
    npass += 1
    print("PASS: [OPT-LITSCAN S4] " + msg)


def bad(msg):
    global nfail
    nfail += 1
    print("FAIL: [OPT-LITSCAN S4] " + msg)


def emit(tag, pat, *flags):
    out = os.path.join(WORK, "rc_" + tag + ".c")
    r = subprocess.run([PCREC, "--features", "all", "-p", "rx", *flags,
                        "-o", out, "--pattern", pat],
                       capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        return None
    with open(out, encoding="latin-1") as f:
        return out, f.read()


def cdecode(lit):
    """The bytes of a C string literal body as pcrec_sb_cstr writes it."""
    b, i = bytearray(), 0
    while i < len(lit):
        ch = lit[i]
        if ch == "\\":
            nx = lit[i + 1]
            if nx in "01234567":
                b.append(int(lit[i + 1:i + 4], 8))
                i += 4
                continue
            b.append({"n": 10, "t": 9, "r": 13}.get(nx, ord(nx)))
            i += 2
            continue
        b.append(ord(ch))
        i += 1
    return bytes(b)


WORD = re.compile(r'rx_w([248])\(([^()]*?)\) == rx_w\1\("((?:[^"\\]|\\.)*)"\)')
INTLIT = re.compile(r'rx_w[248]\([^()]*\) == (?:0x|[0-9])')


def chains(text):
    """Every word compare in `text`: a list of (base, [(off, W, bytes)])."""
    out = []
    for line in text.splitlines():
        cur = None
        for m in WORD.finditer(line):
            w, arg, lit = int(m.group(1)), m.group(2), m.group(3)
            mo = re.match(r"^(.*?)(?: \+ (\d+))?$", arg)
            base, off = mo.group(1), int(mo.group(2) or 0)
            if cur is not None and cur[0] == base and line[cur[2]:m.start()] == " && ":
                cur[1].append((off, w, cdecode(lit)))
                cur[2] = m.end()
            else:
                cur = [base, [(off, w, cdecode(lit))], m.end()]
                out.append(cur)
    return [(c[0], c[1]) for c in out]


def check_compare(label, words, run, base_off):
    L = len(run)
    w = words[0][1]
    offs = [o - base_off for o, _, _ in words]
    if any(x[1] != w for x in words):
        bad(f"{label}: the words of one compare have mixed widths {[x[1] for x in words]}")
        return
    if offs[0] != 0 or offs[-1] != L - w or any(o + w > L for o in offs) \
            or any(b > a + w for a, b in zip(offs, offs[1:])):
        bad(f"{label}: word offsets {offs} (W={w}) for a {L}-byte run -- the first must be 0, "
            f"the last exactly L - W = {L - w}, every word inside the run and no byte uncovered")
        return
    spelled = bytearray(L)
    for o, _, bts in zip(offs, words, [x[2] for x in words]):
        spelled[o:o + w] = bts
    if bytes(spelled) != run:
        bad(f"{label}: the words spell {bytes(spelled)!r}, the run is {run!r}")
        return
    ok(f"{label}: {len(words)} words of {w} at offsets {offs} cover the {L}-byte run "
       f"{run!r} exactly, the last at L - W")


# (tag, pattern, flags, [(run, base, offset of the run at that base)])
WITNESSES = [
    ("router", "/user|/users", (), [(b"/user", "subject + cand", 0)]),
    ("foob", r"foo\b", (), [(b"foo", "subject + cand", 0)]),
    ("abuser", "[ab]/user", (), [(b"/user", "subject + cand", 1)]),
    ("aeqb", "a=b", ("-fno-offset-skip",), [(b"a=b", "subject + cand", 0)]),
    ("quote", 'a"b', ("-fno-offset-skip",), [(b'a"b', "subject + cand", 0)]),
    ("cmt", r"\*/x", ("-fno-offset-skip",), [(b"*/x", "subject + cand", 0)]),
    ("island", "foo(?:username|password|passphrase)bar", ("--engine=vm",), None),
]
POOL = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghij"
for L in (3, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15):
    WITNESSES.append((f"vm{L}", POOL[:L].decode(), ("--engine=vm",),
                      [(POOL[:L], "subject + scan_position", 0)]))

for tag, pat, flags, runs in WITNESSES:
    got = emit(tag, pat, *flags)
    if got is None:
        bad(f"'{pat}' {' '.join(flags)}: refused")
        continue
    path, text = got
    cs = chains(text)
    stamp = re.search(r"^#define RX_RUN_WORDS (\d+)$", text, re.M)
    nwords = int(stamp.group(1)) if stamp else -1
    if nwords != len(cs):
        bad(f"'{pat}': RX_RUN_WORDS reads {nwords}, the text carries {len(cs)} word compares")
    else:
        ok(f"'{pat}': RX_RUN_WORDS {nwords} equals the word compares in the text")
    if INTLIT.search(text):
        bad(f"'{pat}': a word is compared against an INTEGER literal -- a byte-order assumption")
    if runs is None:          # the island: every compare must still check out internally
        if not cs:
            bad(f"'{pat}': the island's single-child chains took no overlap row")
        for base, words in cs:
            o0 = words[0][0]
            L = words[-1][0] + words[-1][1] - o0
            run = bytearray(L)
            for o, w, b in words:
                run[o - o0:o - o0 + w] = b
            check_compare(f"'{pat}' island chain at {base} + {o0}", words, bytes(run), o0)
    else:
        for run, base, off in runs:
            mine = [wd for b, wd in cs if b == base and wd[0][0] == off]
            if not mine:
                bad(f"'{pat}': no word compare of {run!r} at {base} + {off}")
                continue
            for wd in mine:
                check_compare(f"'{pat}' at {base} + {off}", wd, run, off)
    used = sorted({w for _, wd in cs for _, w, _ in wd})
    decl = sorted(int(m) for m in re.findall(r"^static inline uint\d+_t rx_w([248])\(const void \*p\)", text, re.M))
    if decl != used:
        bad(f"'{pat}': helpers declared for widths {decl}, the compares use {used}")
    elif cs and text.index("static inline uint%d_t rx_w%d(" % (8 * used[0], used[0])) > text.index("rx_w%d(subject" % used[0]):
        bad(f"'{pat}': the rx_w{used[0]} helper is declared after its first use")
    else:
        ok(f"'{pat}': helpers declared for exactly the widths used ({used}), ahead of use")
    r = subprocess.run([CC, "-O1", "-Wall", "-Wextra", "-Werror", "-c", "-o", path + ".o", path],
                       capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        bad(f"'{pat}': does not compile under -Wall -Wextra -Werror: {r.stderr.strip()[:300]}")
    else:
        ok(f"'{pat}': compiles under -Wall -Wextra -Werror")
    den = emit(tag + "_deny", pat, *flags, "-fno-run-overlap")
    if den is None:
        bad(f"'{pat}' -fno-run-overlap: refused")
        continue
    dtext = den[1]
    dstamp = re.search(r"^#define RX_RUN_WORDS (\d+)$", dtext, re.M)
    nm_def, nm_den = text.count("!memcmp("), dtext.count("!memcmp(")
    if chains(dtext) or "rx_w2(" in dtext or "rx_w4(" in dtext or "rx_w8(" in dtext \
            or not dstamp or dstamp.group(1) != "0":
        bad(f"'{pat}' -fno-run-overlap: a word compare, a helper or a non-zero RX_RUN_WORDS survives the deny")
    elif nm_den != nm_def + len(cs):
        bad(f"'{pat}' -fno-run-overlap: {nm_den} memcmp compares, expected {nm_def} + {len(cs)} "
            "(each word compare restored to exactly one memcmp)")
    else:
        ok(f"'{pat}' -fno-run-overlap: no word compare, RX_RUN_WORDS 0, and the {len(cs)} word "
           f"compare(s) restored to memcmp ({nm_den} in all)")

# PAY FOR WHAT YOU USE: the lengths gcc already lowers to one load (or a vector
# compare) stay a memcmp, and an artifact with no overlap compare carries no
# helper.
for L in (4, 8, 16):
    got = emit(f"keep{L}", POOL[:L].decode(), "--engine=vm")
    if got is None:
        bad(f"L = {L} witness refused")
        continue
    text = got[1]
    want = '!memcmp(subject + scan_position, "%s", %d)' % (POOL[:L].decode(), L)
    if want in text and not chains(text) and "rx_w" + "4(const" not in text \
            and re.search(r"^#define RX_RUN_WORDS 0$", text, re.M):
        ok(f"L = {L}: the run stays one memcmp, no helper, RX_RUN_WORDS 0")
    else:
        bad(f"L = {L}: expected the run as one memcmp with no word compare and no helper")

print(f"runcmp_check: {npass} passed, {nfail} failed")
sys.exit(1 if nfail else 0)
