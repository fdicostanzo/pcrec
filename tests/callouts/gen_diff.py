#!/usr/bin/env python3
"""tests/callouts/gen_diff.py — the GENERATED callout differential
([INLINE-C] stage 1b; docs/spec/match_api.md §11).

WHAT IT CHECKS. A seeded population of random patterns carrying callout
sites, each compiled by pcrec and asked over random subjects; every answer
(match span and every group, or no match) is compared with libpcre2 10.46's
under the oracle flags of co_oracle.c (the answer-moving optimizations off,
§11.6¶2). The callees are behaviors.h's pure rows, bound on pcrec's side by
stubs.c and on libpcre2's by co_oracle.c. A `consume` site is a NAMED row
whose `pcre2_equiv` is spliced in its place for the oracle.

THE FIRING-CLASS BOUND rides the same runs: every site the artifact's own
`--emit-ir` listing classes `once-per-start` or `once-per-match` must fire at
most once per attempt start within one search call (§11.8), read off the
stubs' fire log. Fire COUNTS are never compared (§11.6¶1).

THE POPULATION IS COUNTED, NOT ASSUMED (learnings.md §3): a pattern pcrec or
libpcre2 refuses is skipped with its reason tallied, and the run fails when
fewer than --floor patterns were compiled AND compared, or fewer than
--floor/2 artifacts carry a once-class site whose bound the fire log checks.

Usage: gen_diff.py --pcrec BIN --work DIR [--n N] [--seed S] [--floor F]
Exit 0 green, 1 on any disagreement, a missed floor or a co_oracle.c that
does not build against a present libpcre2, 3 only when libpcre2 itself is
absent (the caller reports the skip; verify_callouts.build_oracle).
"""
import argparse
import os
import random
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from verify_callouts import build_oracle  # noqa: E402  (absent vs broken)

def read_rows():
    """behaviors.h's row table, the ONE list of behaviours: (name, is_consumer,
    pcre2_equiv) in row order, which is the id order stubs.c logs by."""
    import re as _re
    rows = []
    with open(os.path.join(HERE, "behaviors.h")) as f:
        for m in _re.finditer(r'\{ "(\w+)",\s*co_\w+,\s*(NULL|"((?:[^"\\]|\\.)*)")\s*\}', f.read()):
            rows.append((m.group(1), m.group(2) != "NULL",
                         m.group(3).replace("\\\\", "\\") if m.group(3) else None))
    return rows


ROWS = read_rows()
CHECKS = [n for n, c, _ in ROWS if not c]
NCHECK = len(CHECKS)
CONSUMER_ROWS = [n for n, c, _ in ROWS if c]
CONSUMERS = {n: e for n, c, e in ROWS if c}
ALPHA = "ab1x"


class Gen:
    def __init__(self, rng):
        self.r = rng
        self.next_num = 0
        self.ngroups = 0

    def site(self):
        r = self.r
        if r.random() < 0.15:
            name = r.choice(sorted(CONSUMERS))
            return '(?C"%s,consume")' % name, ("consume", name)
        if r.random() < 0.25:
            name = r.choice(CHECKS)
            return '(?C"%s")' % name, ("check", name)
        # a numbered check: unique number per site, behaviour n % NCHECK
        beh = r.randrange(NCHECK)
        n = beh + NCHECK * self.next_num
        self.next_num += 1
        if n > 255:
            return '(?C"pass")', ("check", "pass")
        return "(?C%d)" % n, ("check", CHECKS[beh])

    def atom(self, depth):
        r = self.r
        k = r.random()
        if depth < 2 and k < 0.3:
            kind = r.choice(["(", "(", "(?:", "(?>", "(?="])
            if kind == "(":
                self.ngroups += 1
            return kind + self.alt(depth + 1) + ")"
        if k < 0.45:
            return r.choice(["[ab]", "\\d", ".", "[^x]"])
        return r.choice(ALPHA)

    def quant(self, a):
        r = self.r
        if a.startswith("(?="):
            return a
        q = r.choice(["", "", "", "*", "+", "?", "{1,2}", "*?", "+?", "*+", "{2}"])
        return a + q

    def seq(self, depth):
        r = self.r
        items = []
        for _ in range(r.randint(1, 4)):
            if r.random() < 0.3:
                items.append(self.site()[0])
            else:
                items.append(self.quant(self.atom(depth)))
        return "".join(items)

    def alt(self, depth):
        return "|".join(self.seq(depth) for _ in range(self.r.randint(1, 2 if depth else 3)))

    def pattern(self):
        self.next_num = 0
        self.ngroups = 0
        p = self.alt(0)
        if "(?C" not in p:
            p = self.site()[0] + p
        r = self.r.random()
        if r < 0.1:
            p = "^" + p
        elif r < 0.2:
            p = p + "$"
        return p


def oracle_text(pat):
    """The pattern libpcre2 is asked: each consume site spliced to its
    equivalent, wrapped so a quantifier or alternation applies to the whole."""
    for name, eq in CONSUMERS.items():
        pat = pat.replace('(?C"%s,consume")' % name, "(?:%s)" % eq)
    return pat


def hexs(b):
    return b.hex()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pcrec", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--n", type=int, default=1200)
    ap.add_argument("--seed", type=int, default=20261026)
    ap.add_argument("--floor", type=int, default=1000)
    ap.add_argument("--batch", type=int, default=60)
    ap.add_argument("--cc", default=os.environ.get("CC", "gcc"))
    ap.add_argument("--cflags", default=os.environ.get("GENCFLAGS", "-O1"))
    a = ap.parse_args()
    os.makedirs(a.work, exist_ok=True)

    oracle = os.path.join(a.work, "co_oracle")
    rc, why = build_oracle(a.cc, oracle)
    if rc:
        sys.stderr.write("gen_diff: %s\n" % why)
        if rc == 1:
            print("FAIL: gen_diff: %s" % why)
        return rc

    rng = random.Random(a.seed)
    g = Gen(rng)
    skips = {}
    arts = []   # (prefix, pattern, ngroups-of-pcrec, once_ids, subjects)
    seen = set()
    tries = 0
    while len(arts) < a.n and tries < a.n * 4:
        tries += 1
        pat = g.pattern()
        if pat in seen:
            continue
        seen.add(pat)
        px = "g%d" % len(arts)
        cpath = os.path.join(a.work, px + ".c")
        r = subprocess.run([a.pcrec, "-p", px, "--features", "all", "-o", cpath,
                            "--pattern", pat], capture_output=True, text=True)
        if r.returncode != 0:
            why = r.stderr.strip().split(" (pattern offset")[0]
            why = why.split(": ", 1)[-1][:70]
            skips[why] = skips.get(why, 0) + 1
            continue
        ir = subprocess.run([a.pcrec, "--features", "all", "--emit-ir",
                             "--pattern", pat], capture_output=True, text=True)
        # The fire log keys on the BINDING, so the bound is checked only for
        # a binding that names exactly one site (two sites sharing one
        # binding fire it twice per start legitimately).
        sites = {}
        insec = False
        for line in ir.stdout.splitlines():
            if line.startswith("#section"):
                insec = line.strip() == "#section callouts"
                continue
            if not insec or line.startswith("#"):
                continue
            f = line.split("\t")
            if len(f) >= 5:
                sites.setdefault(f[2][len("rx_callout_"):], []).append(f[4])
        once = set()
        for b, classes in sites.items():
            if len(classes) != 1 or classes[0] not in ("once-per-start", "once-per-match"):
                continue
            if b.isdigit():
                once.add(int(b))
            elif b in CHECKS:
                once.add(256 + CHECKS.index(b))
            elif b in CONSUMER_ROWS:
                once.add(256 + NCHECK + CONSUMER_ROWS.index(b))
        ncaps = None
        with open(os.path.join(a.work, px + ".h")) as h:
            for line in h:
                if line.startswith("#define %s_NCAPS " % px.upper()):
                    ncaps = int(line.split()[2])
        subs = set()
        while len(subs) < 6:
            subs.add("".join(rng.choice(ALPHA) for _ in range(rng.randint(0, 7))))
        arts.append((px, pat, ncaps, sorted(once), sorted(subs)))

    # ---- pcrec side: batched drivers --------------------------------------
    stubs_hdr = None
    got = {}
    for b0 in range(0, len(arts), a.batch):
        chunk = arts[b0:b0 + a.batch]
        d = os.path.join(a.work, "drv%d.c" % b0)
        with open(d, "w") as f:
            f.write("#include <stdio.h>\n#include <string.h>\n")
            for px, *_ in chunk:
                f.write('#include "%s.h"\n' % px)
            f.write("extern int co_log_n; extern int co_log_id[]; extern ptrdiff_t co_log_start[];\n")
            f.write("static void ask(const char *tag, int (*fn)(const unsigned char *, size_t, size_t, ptrdiff_t (*)[2]),\n"
                    "                int ncaps, const int *once, int nonce, const char *s)\n{\n"
                    "    ptrdiff_t caps[64][2];\n    size_t n = strlen(s);\n    co_log_n = 0;\n"
                    "    int r = fn((const unsigned char *)s, n, 0, caps);\n"
                    "    printf(\"%s\\t%s\\t\", tag, s);\n"
                    "    if (r == 1) { printf(\"match\"); for (int g = 0; g < ncaps; g++) printf(\" %td %td\", caps[g][0], caps[g][1]); }\n"
                    "    else if (r == 0) printf(\"nomatch\");\n    else printf(\"code %d\", r);\n"
                    "    for (int i = 0; i < co_log_n; i++) for (int j = i + 1; j < co_log_n; j++)\n"
                    "        for (int k = 0; k < nonce; k++)\n"
                    "            if (co_log_id[i] == once[k] && co_log_id[j] == once[k] && co_log_start[i] == co_log_start[j]) {\n"
                    "                printf(\"\\tclassviol %d %td\", once[k], co_log_start[i]); goto done; }\n"
                    "done:\n    putchar('\\n');\n}\n")
            f.write("int main(void)\n{\n")
            for px, pat, ncaps, once, subs in chunk:
                f.write("    { static const int once[] = { %s }; (void)once;\n"
                        % (", ".join(str(x) for x in once) if once else "-1"))
                for s in subs:
                    f.write('      ask("%s", %s_search, %d, once, %d, "%s");\n'
                            % (px, px, ncaps, len(once), s))
                f.write("    }\n")
            f.write("    return 0;\n}\n")
        exe = os.path.join(a.work, "drv%d" % b0)
        srcs = [d] + [os.path.join(a.work, px + ".c") for px, *_ in chunk]
        cmd = [a.cc] + a.cflags.split() + ["-I", a.work, "-o", exe] + srcs + \
              ["-include", os.path.join(a.work, chunk[0][0] + ".h"),
               os.path.join(HERE, "stubs.c")]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            sys.stderr.write("gen_diff: driver build failed:\n%s\n" % r.stderr[:2000])
            return 1
        r = subprocess.run([exe], capture_output=True, text=True, timeout=600)
        for line in r.stdout.splitlines():
            f = line.split("\t")
            got[(f[0], f[1])] = f[2:]

    # ---- the oracle -------------------------------------------------------
    qs = []
    for px, pat, ncaps, once, subs in arts:
        for s in subs:
            qs.append((px, s, "%s\t%s\t0" % (hexs(oracle_text(pat).encode()), hexs(s.encode()))))
    r = subprocess.run([oracle], input="\n".join(q for *_, q in qs) + "\n",
                       capture_output=True, text=True, timeout=600)
    ans = r.stdout.splitlines()
    if len(ans) != len(qs):
        sys.stderr.write("gen_diff: oracle answered %d of %d questions\n" % (len(ans), len(qs)))
        return 1

    pats = {px: (pat, ncaps) for px, pat, ncaps, *_ in arts}
    bad = 0
    viol = 0
    compared = set()
    oracle_err = 0
    for (px, s, _), o in zip(qs, ans):
        pat, ncaps = pats[px]
        mine = got.get((px, s))
        if mine is None:
            print("FAIL: %s %r on %r: no pcrec answer" % (px, pat, s))
            bad += 1
            continue
        if o.startswith("error"):
            oracle_err += 1
            continue
        compared.add(px)
        mine_ans = mine[0]
        if len(mine) > 1 and mine[1].startswith("classviol"):
            viol += 1
            if viol <= 20:
                print("FAIL: %s %r on %r: firing-class bound broken (%s)" % (px, pat, s, mine[1]))
        if o.startswith("match"):
            want = o.split()[1:1 + 2 * ncaps]
            o_cmp = "match " + " ".join(want)
        else:
            o_cmp = o
        if mine_ans.strip() != o_cmp.strip():
            bad += 1
            if bad <= 40:
                print("FAIL: %s %r on %r: pcrec '%s' libpcre2 '%s'" % (px, pat, s, mine_ans, o))
    ncase = sum(len(x[4]) for x in arts)
    nbound = sum(1 for x in arts if x[3])
    print("gen_diff: %d patterns generated (%d tries), %d compiled, %d compared, "
          "%d cases, %d disagreements, %d class-bound violations, %d oracle errors, "
          "%d artifacts with a checked firing-class bound"
          % (len(arts) + sum(skips.values()), tries, len(arts), len(compared),
             ncase, bad, viol, oracle_err, nbound))
    print("gen_diff: %d of %d compiled artifacts (%.0f%%) carry a once-class "
          "site the fire log checks" % (nbound, len(arts),
                                         100.0 * nbound / max(1, len(arts))))
    for why, n in sorted(skips.items(), key=lambda x: -x[1]):
        print("gen_diff: skipped %d: %s" % (n, why))
    if len(compared) < a.floor:
        print("FAIL: gen_diff: %d patterns compared, below the floor of %d"
              % (len(compared), a.floor))
        return 1
    # The firing-class bound is checked only on artifacts that carry a
    # once-class site (K35): its population has its own floor, half the
    # compared floor (measured 890 of 1,200 at lane ic1bfix, 2026-10-26).
    if nbound < a.floor // 2:
        print("FAIL: gen_diff: %d artifacts carry a checked firing-class "
              "bound, below the floor of %d" % (nbound, a.floor // 2))
        return 1
    return 1 if bad or viol else 0


if __name__ == "__main__":
    sys.exit(main())
