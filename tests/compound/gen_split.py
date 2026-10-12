#!/usr/bin/env python3
"""tests/compound/gen_split.py -- [COMPOUND] G1: write tests/compound/split.rxt
FROM libpcre2's answers (docs/design/compound.md §E.3 G1). Oracle first:
every m/n/ms/ns/g/mc line is libpcre2 10.46's answer, never pcrec's.

  python3 -I gen_split.py ORACLE_BIN PCREC SCRATCH CASES > split.rxt

ORACLE_BIN is tests/fuzz/pcre2_oracle.c built against libpcre2-8 (it compiles
at options=0, so a `utf8` case's `encoding utf8` is carried into the pattern
text the oracle sees as a `(*UTF)` prefix). CASES is split_cases.tsv: the
twin's case list (every pin-only shape the split row admits and every shape
it must decline, by the reason it declines), the panel's witnesses and the
owed CMP-13 row. A case pcrec refuses at parse (a verb, an unbuilt
conditional: the decline witnesses whose control is the refusal itself,
compound.md §E.4) is written as a `perr` block. Each case gets the twin's subject alphabet (its own
literals, its non-ASCII bytes, space, newline), thinned to a fixed sample:
the panel's witness subjects verbatim, the empty subject, every 1- and
2-character string, and twelve longer seeded strings; each subject at
startpos 0 (m/n), and at 1 and at the end where those are character starts (ms/ns),
with every group slot (g), and its find-all count (mc, match_api.md §3.1's
loop driven through the oracle). A utf8 case's subjects are well-formed (the
harness's default startpos guard and no subject check; ill-formed subjects
and the other option arms are G2's, check_split_diff.py). verify_split.py
re-reads the written file and re-asks the oracle; it shares no code with
this generator.
"""
import itertools, os, random, re, subprocess, sys

SEEDS = {
    rb"\A\s+|\s+\z": [b" ", b"x  "],
    rb"a{0,4}\A": [b"aa", b"xaa"],
    rb"^x|a(?R)?b": [b"aabb", b"xaabb"],
    rb"(?>\Ga|ab)c": [b"abc", b"ac"],
    rb"(?:^(a)|b)(?1)": [b"xba", b"aa"],
    rb"^\s*\{|\}\s*$": [b"{  }", b"{ }\n", b" { } "],
}


def alphabet(p, utf):
    esc = re.findall(rb"\\([^A-Za-z0-9])", p)
    bare = re.sub(rb"\\x\{[^}]*\}|\\[pPgkN]\{[^}]*\}|\\.|\(\?(?:[a-zA-Z^-]*[:)]|[=!>|]|<[=!]|"
                  rb"P?<\w+>|'\w+')|\(\*[^)]*\)|\{\d*,?\d*\}", b"", p)
    keep = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789,;:'\"/#-=@&%!~`<>_{}"
    lits = list(dict.fromkeys([e for e in esc if 32 < e[0] < 127] +
                              [bytes([c]) for c in bare if 32 < c < 127 and chr(c) in keep]))[:4]
    alpha = lits + [b" ", b"\n"] + ([b"\t"] if b"\\s" in p else []) + \
        ([b"\xc3\xa9"] if utf else [])
    return list(dict.fromkeys(alpha))[:8]


def subjects(p, utf):
    a = alphabet(p, utf)
    out = [b""] + list(SEEDS.get(p, []))
    out += [x for x in a] + [x + y for x, y in itertools.product(a, repeat=2)][:24]
    rnd = random.Random(7)
    words = list(dict.fromkeys(re.findall(rb"[A-Za-z_]{3,}", re.sub(rb"\\[a-zA-Z]", b" ", p))))[:6]
    for _ in range(12):
        s = b"".join(rnd.choice(a) for _ in range(rnd.randint(3, 10)))
        if words and rnd.random() < 0.5:
            s = rnd.choice(words) + s + rnd.choice(words)
        out.append(s)
    return list(dict.fromkeys(out))


def oracle(binp, scratch, pat, utf, subj, sp):
    f = os.path.join(scratch, "subj")
    with open(f, "wb") as h:
        h.write(subj)
    r = subprocess.run([binp, (b"(*UTF)" if utf else b"") + pat, f, str(sp)],
                       capture_output=True, timeout=60)
    ans = r.stdout.decode().split()
    if not ans or ans[0] not in ("match", "nomatch"):
        sys.exit("oracle: %r on %r @%d: %s" % (pat, subj, sp, ans))
    return None if ans[0] == "nomatch" else list(map(int, ans[1:]))


def starts(subj, utf):
    return [i for i in range(len(subj) + 1)
            if not utf or i == len(subj) or (subj[i] & 0xC0) != 0x80]


def next_pos(subj, utf, p):
    p += 1
    while utf and p < len(subj) and (subj[p] & 0xC0) == 0x80:
        p += 1
    return p


def findall(binp, scratch, pat, utf, subj):
    """match_api.md §3.1's loop: resume at a non-empty match's end, off an
    empty one at next_pos(its start)."""
    n, pos, count = len(subj), 0, 0
    while pos <= n:
        v = oracle(binp, scratch, pat, utf, subj, pos)
        if v is None:
            break
        count += 1
        pos = v[1] if v[1] > v[0] else next_pos(subj, utf, v[0])
    return count


def esc(b):
    out = []
    for c in b:
        ch = chr(c)
        if ch == "\n": out.append("\\n")
        elif ch == "\t": out.append("\\t")
        elif ch == "\r": out.append("\\r")
        elif ch == '"': out.append('\\"')
        elif ch == "\\": out.append("\\\\")
        elif 32 <= c < 127: out.append(ch)
        else: out.append("\\x%02x" % c)
    return "".join(out)


HEADER = """# [COMPOUND] G1: the split compound's answer net (docs/design/compound.md
# §E.3 G1; build step B4). Written by tests/compound/gen_split.py FROM
# libpcre2 10.46's answers, never pcrec's; tests/compound/verify_split.py
# re-reads this file and re-asks the oracle. Every block is `# pcre2-only`
# (the cases carry \\G, \\Z, \\z and possessive or atomic forms python `re`
# answers differently or not at all).
#
# The cases are tests/compound/split_cases.tsv: every pin-only shape the
# `split` row admits (a ^/\\A/\\G floor arm beside end-pinned arms, the
# floor-only form, the wrapper and trim idioms, the tie and interior-$
# cells) and the shapes it must decline. The default build compiles the
# admitted ones to compounds, so this corpus is their answer check under
# every axis and sanitizer arm the corpus rides; the option arms the corpus
# cannot express (the startpos guards, -futf-check) are G2's.
"""


def main():
    binp, pcrec, scratch, cases = sys.argv[1:5]
    os.makedirs(scratch, exist_ok=True)
    print(HEADER.rstrip("\n"))
    done = set()
    for ln in open(cases, encoding="ascii"):
        f = ln.rstrip("\n").split("\t")
        if len(f) < 3:
            continue
        cid, enc, pat = f[0], f[1], bytes.fromhex(f[2])
        utf = enc == "utf8"
        if (pat, utf) in done:
            continue
        done.add((pat, utf))
        print()
        print("# " + cid)
        print("# pcre2-only")
        print("pattern " + pat.decode("ascii"))
        if utf:
            print("encoding utf8")
        print("features all")
        refused = subprocess.run([pcrec, "--features", "all", "-o", os.path.join(scratch, "p.c")] +
                                 (["-e", "utf8"] if utf else []) + ["--pattern", pat],
                                 capture_output=True, timeout=300).returncode != 0
        if refused:
            print("perr")
            continue
        for s in subjects(pat, utf):
            for sp in sorted(set(starts(s, utf)) & {0, 1, len(s)}):
                v = oracle(binp, scratch, pat, utf, s, sp)
                kw, pre = ("m", "") if sp == 0 else ("ms", "%d " % sp)
                if v is None:
                    print('%s %s"%s"' % ("n" if sp == 0 else "ns", pre, esc(s)))
                    continue
                print('%s %s"%s" %d %d' % (kw, pre, esc(s), v[0], v[1]))
                for k in range(1, len(v) // 2):
                    print("g %d %d %d" % (k, v[2 * k], v[2 * k + 1]))
            print('mc "%s" %d' % (esc(s), findall(binp, scratch, pat, utf, s)))


main()
