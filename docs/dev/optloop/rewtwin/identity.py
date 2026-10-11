#!/usr/bin/env python3
"""rewtwin identity: the rev-end-width TWIN against today's artifact, the
-fno-rev-end artifact and libpcre2 (the box's 10.46), at EVERY start position.

usage: identity.py TODAY_PCREC TWIN_PCREC SUBJ_DIR WORK_DIR

For each (pattern, mode) row: three artifacts are compiled (today = main's
compiler, twin = lane/rewtwin-scratch's, base = main's under -fno-rev-end),
linked into one driver with libpcre2-8, and run over a subject pool (the
bench's published litrun short + throughput subjects, their edits, and an
exhaustive sweep over a small per-row alphabet). For every subject and every
start position (every character boundary under utf8) the driver compares each
artifact's search answer (rc, every capture pair) with pcre2_match at that
offset. Since find-all is a chain of searches from earlier answers' ends,
every-startpos subsumes it. Prints one line per row and a total; exit 1 on
any difference.
"""
import itertools, os, subprocess, sys

ROWS = []   # (name, pattern, mode flags, alphabet, utf8)
LIT = {
    "alt-foo-tails": "foo.x|foobar|foo.",
    "lit-l2": "ab", "lit-l3": "abc", "lit-l4": "abcd", "lit-l7": "abcdefg",
    "lit-l8": "abcdefgh", "lit-l10": "abcdefghij", "lit-l16": "abcdefghijklmnop",
    "lit-l31": "abcdefghijklmnopqrstuvwxyzABCDE",
    "lit-l40": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMN",
    "aws": r"\b((?:A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16})\b",
    "ghp": r"\b(github_pat_[0-9a-zA-Z_]{82})\b",
    "ctrl-abc-dollar": "abc$", "floor": "#",
}
for k, p in LIT.items():
    ROWS.append((k + "/whole", "(?:%s)\\z" % p, "abxfo\n"))
ROWS.append(("ctrl-abc-dollar/plain", "abc$", "abcx\n"))
# `$`/`\Z` seeds and the shapes the width fact must get right.
for name, p, alpha in [
    ("eol-lit4", "(?:abcd)$", "abcd\n"), ("eoz-Z", "abc\\Z", "abc\n"),
    ("eol-dot", "a.c$", "ac\n"), ("eol-space-nl", "(?:a\\s)$", "a \n"),
    ("eol-alt", "(?:ab|cd)$", "abcd\n"), ("eol-ci", "(?i)abc$", "aBC\n"),
    ("eol-wordb", "\\bab$", "abx \n"), ("eoz-lb", "(?<=x)ab\\z", "abx\n"),
    ("eol-nl", "(?:a\\n)$", "a\n"), ("eol-onlynl", "\\n$", "a\n"),
    ("eol-nlnl", "(?:\\n\\n)$", "a\n"), ("eoz-alt2", "(?:a|b)(?:c|d)\\Z", "abcd\n"),
    ("eol-la", "a(?=b)b$", "ab\n"), ("eol-mixed", "(?:x$|y\\z)", "xy\n"),
    ("eoz-class", "[a-c]{3}\\z", "abcd\n"), ("eol-wb2", "a\\b$", "a \n"),
]:
    ROWS.append((name, p, alpha))
UTF = [("u8-e-z", "é\\z", "aé\n"), ("u8-ab-z", "ab\\z", "abé\n"),
       ("u8-dot-eol", "(?:é.)$", "éa\n"), ("u8-e2-eol", "(?:éé)$", "éa\n")]

DRIVER = r'''
#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "t0.c"
#include "t1.c"
#include "t2.c"
static const unsigned char PAT[] = PATTERN_BYTES;
int main(int argc, char **argv)
{
    int err; PCRE2_SIZE eo;
    pcre2_code *re = pcre2_compile(PAT, sizeof PAT - 1, PCRE_OPTS, &err, &eo, NULL);
    if (!re) { printf("pcre2 compile error %d\n", err); return 2; }
    pcre2_match_data *md = pcre2_match_data_create_from_pattern(re, NULL);
    FILE *f = fopen(argv[1], "rb");
    unsigned long long cells = 0, diff[3] = {0, 0, 0};
    unsigned int len;
    static unsigned char s[1 << 20];
    int ncaps = T0_NCAPS;
    while (fread(&len, 4, 1, f) == 1) {
        if (fread(s, 1, len, f) != len) return 3;
        for (size_t sp = 0; sp <= len; sp++) {
            if (IS_UTF && sp < len && (s[sp] & 0xC0) == 0x80) continue;
            int prc = pcre2_match(re, s, len, sp, 0, md, NULL);
            PCRE2_SIZE *ov = pcre2_get_ovector_pointer(md);
            ptrdiff_t want[64][2];
            for (int g = 0; g < ncaps; g++) {
                want[g][0] = want[g][1] = PCREC_UNSET;
                if (prc > 0 && g < prc && ov[2*g] != PCRE2_UNSET) {
                    want[g][0] = (ptrdiff_t)ov[2*g]; want[g][1] = (ptrdiff_t)ov[2*g+1];
                }
            }
            int wrc = prc > 0 ? 1 : (prc == PCRE2_ERROR_NOMATCH ? 0 : -100);
            int (*fn[3])(const unsigned char *, size_t, size_t, ptrdiff_t (*)[2]) = { t0_search, t1_search, t2_search };
            for (int k = 0; k < 3; k++) {
                ptrdiff_t got[64][2];
                for (int g = 0; g < ncaps; g++) got[g][0] = got[g][1] = -7;
                int rc = fn[k](s, len, sp, got);
                int bad = rc != wrc;
                if (!bad && rc == 1)
                    for (int g = 0; g < ncaps; g++)
                        bad |= got[g][0] != want[g][0] || got[g][1] != want[g][1];
                if (bad && diff[k]++ < 3) {
                    printf("  DIFF art%d sp=%zu len=%u rc=%d want=%d g0=(%td,%td) want=(%td,%td) subj=", k, sp, len, rc, wrc,
                           got[0][0], got[0][1], want[0][0], want[0][1]);
                    for (unsigned i = 0; i < len && i < 60; i++) printf(s[i] >= 32 && s[i] < 127 ? "%c" : "\\x%02x", s[i]);
                    printf("\n");
                }
            }
            cells++;
        }
    }
    printf("cells=%llu diff_today=%llu diff_twin=%llu diff_base=%llu\n", cells, diff[0], diff[1], diff[2]);
    return (diff[0] || diff[1] || diff[2]) ? 1 : 0;
}
'''


def c_bytes(b):
    return '"' + "".join("\\x%02x" % c for c in b) + '"'


def pool(subj_dir, alpha, utf8):
    out = []
    for sub in ("subjects", "throughput"):
        d = os.path.join(subj_dir, sub)
        for fn in sorted(os.listdir(d)):
            b = open(os.path.join(d, fn), "rb").read()
            if sub == "throughput":   # every-startpos over 64 KiB: keep the tail
                b = b[-200:]
            for e in (b, b + b"\n", b"x" + b, b[:-1], b + b"\n\n", b[:-1] + b"\n"):
                out.append(e)
    syms = [c.encode("utf-8") for c in alpha]
    for n in range(0, 7 if len(syms) <= 5 else 6):
        for t in itertools.product(syms, repeat=n):
            out.append(b"".join(t))
    return out


def main():
    today, twin, subj_dir, work = sys.argv[1:5]
    os.makedirs(work, exist_ok=True)
    total_bad = 0
    rows = [(n, p, "", a, False) for n, p, a in ROWS]
    rows += [(n + "/nocaps", p, "--no-captures", a, False) for n, p, a in ROWS]
    rows += [(n, p, "", a, True) for n, p, a in UTF]
    rows += [(n + "/nocaps", p, "--no-captures", a, True) for n, p, a in UTF]
    for name, pat, mode, alpha, utf8 in rows:
        wd = os.path.join(work, name.replace("/", "_"))
        os.makedirs(wd, exist_ok=True)
        enc = ["-e", "utf8"] if utf8 else []
        stamps = []
        for tag, comp, extra in (("t0", today, []), ("t1", twin, []), ("t2", today, ["-fno-rev-end"])):
            cmd = [comp, "--features", "all", "-p", tag] + enc + ([mode] if mode else []) + extra + \
                  ["-o", os.path.join(wd, tag + ".c"), "--pattern", pat]
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if r.returncode:
                print("%-28s COMPILE FAIL %s: %s" % (name, tag, r.stderr.strip())); total_bad += 1; break
            txt = open(os.path.join(wd, tag + ".c"), encoding="latin-1").read()
            scan = [l.split('"')[1] for l in txt.splitlines() if l.startswith("#define %s_DFA_SCAN " % tag.upper())]
            stamps.append(scan[0] if scan else "-")
        else:
            same = open(os.path.join(wd, "t0.c"), "rb").read().replace(b"t0", b"tX").replace(b"T0", b"TX") == \
                   open(os.path.join(wd, "t1.c"), "rb").read().replace(b"t1", b"tX").replace(b"T1", b"TX")
            src = DRIVER.replace("PATTERN_BYTES", c_bytes(pat.encode("utf-8"))) \
                        .replace("PCRE_OPTS", "PCRE2_UTF" if utf8 else "0") \
                        .replace("IS_UTF", "1" if utf8 else "0")
            open(os.path.join(wd, "drv.c"), "w").write(src)
            r = subprocess.run(["gcc", "-O2", "-w", "-I", wd, "-o", os.path.join(wd, "drv"),
                                os.path.join(wd, "drv.c"), "-lpcre2-8"], capture_output=True, text=True, timeout=300)
            if r.returncode:
                print("%-28s BUILD FAIL: %s" % (name, r.stderr[:400])); total_bad += 1; continue
            with open(os.path.join(wd, "subj.bin"), "wb") as f:
                for b in pool(subj_dir, alpha, utf8):
                    f.write(len(b).to_bytes(4, "little")); f.write(b)
            r = subprocess.run([os.path.join(wd, "drv"), os.path.join(wd, "subj.bin")],
                               capture_output=True, text=True, timeout=600)
            print("%-28s scan=%s twin=%s %s" % (name, stamps[0], "identical-text" if same else "TWIN",
                                                r.stdout.strip().replace("\n", "\n    ")))
            total_bad += r.returncode != 0
    print("ROWS WITH A DIFFERENCE OR FAILURE: %d" % total_bad)
    sys.exit(1 if total_bad else 0)


main()
