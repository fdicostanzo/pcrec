#!/usr/bin/env python3
"""tests/compound/check_parts.py -- [COMPOUND] B1's unit drive: part mode and
the parts' options (docs/design/compound.md §A.1, §A.5; §F row B1).

  check_parts.py DRIVE WORKDIR

DRIVE is tests/compound/compound_drive.c built. For each WITNESS (the split
client's pin-only shapes, each with its Q written out by hand: B2 derives
Q, B1 only renders it), each ARM (the parent's encoding and contract
options) and each PREFIX (`kz`, and a legal 60-byte one):

  (1) the parts compile: F = P bounded to one attempt, Q, both DFA and
      guards-off, through `pcrec_compile_part` (`compound_drive parts`);
  (2) ONE translation unit -- the plain artifact of P at prefix `pp` (it
      brings the shared ABI block, which no part carries), F, Q, a HAND
      CONTROLLER (the split combinator with the prologue computed from P,
      compound.md §B.2/§A.6) and a driver main -- compiles under the
      harness's `-O1 -std=gnu11 -Wall -Wextra -Werror`;
  (3) no part symbol is global (`nm -g` has no `__f_`/`__q_` name), the
      parts carry none of the shared blocks (no ABI guard, no feature macro,
      no `rx_info`, no `main`), and F's attempt loop is bounded at
      `search_from` (the BOUND the part option selects; an unbounded F
      answers the same, so only the text can show it);
  (4) the linked program answers exactly what the plain artifact answers,
      every subject at every startpos 0..n+1 (verdict and caps[0]): the
      positive control that F really is P's one attempt and the parts work;
  (5) K79: each part's text at the 60-byte prefix is its text at `kz` with
      only the prefix's spelling changed;
  (6) the BOUND is a general emission option (B4's soft item, §A.5): P
      compiled as an ORDINARY artifact (prefix `nb`, no part mode) under a
      one-attempt request answers, at every character start 0..n, exactly
      the plain artifact's match-here (`pp_match_caps` at that position):
      one attempt at `from` is P's own priority answer there.

Also runs `compound_drive selfcheck` (the table-build self-check refuses
every unstated or inconsistent field). Exit 1 on any failure.
"""
import itertools, os, random, subprocess, sys

CC = os.environ.get("CC", "gcc")
GENCFLAGS = ["-O1", "-std=gnu11", "-Wall", "-Wextra", "-Werror"]
L60 = "lp" * 30
# (id, P, Q or None for the floor-only form, HAS_G): compound.md §B.4's
# pin-only shapes, Q by §B.1's kill and prune done by hand.
WITNESSES = [
    ("trim", rb"^\s+|\s+$", rb"\s+$", 0),
    ("wrapper", rb"^\s*\{|\}\s*$", rb"\}\s*$", 0),
    ("flooronly", rb"a{0,4}\A", None, 0),
    ("gend", rb"\Ga$|b$", rb"b$", 1),
    ("tie", rb"^q|a$|a\n$", rb"a$|a\n$", 0),
    ("semmf1", rb"\A\s+|\s+\z", rb"\s+\z", 0),
]
# (name, drive args, UTF, GUARD (0 none, 1 refuse, 2 align), UCHECK)
ARMS = [
    ("byte", [], 0, 0, 0),
    ("utf8", ["--enc", "utf8"], 1, 1, 0),
    ("utf8-check", ["--enc", "utf8", "--utf-check"], 1, 1, 1),
    ("utf8-align-check", ["--enc", "utf8", "--guard", "align", "--utf-check"], 1, 2, 1),
    ("utf8-none", ["--enc", "utf8", "--guard", "none"], 1, 0, 0),
]
CONTROLLER = r"""
/* the hand controller: split = first-nonzero(F @ f, Q @ next_pos(f)),
 * one prologue computed from P (compound.md §B.2, §A.6) */
int @P_search(const unsigned char *s, size_t n, size_t from, ptrdiff_t (*caps)[2])
{
#if UTF && GUARD == 1
    if (!(from == 0 || from >= n || (s[from] & 0xC0) != 0x80)) return PCREC_ERR_STARTPOS;
#elif UTF && GUARD == 2
    if (!(from == 0 || from >= n || (s[from] & 0xC0) != 0x80))
        do from++; while (!(from >= n || (s[from] & 0xC0) != 0x80));
#endif
#if UTF && UCHECK
    if (@P__f_valid_upto(s, n, from) != n) return PCREC_ERR_UTF;
#endif
    if (from > n) return 0;
    size_t qf = from;
    if (from == 0 || HAS_G) {
        int r = @P__f_search(s, n, from, caps);
        if (r != 0) return r;
        qf = @P__f_next_pos(s, n, from);
    }
#if QNEVER
    (void)qf;
    return 0;
#else
    return @P__q_search(s, n, qf, caps);
#endif
}

#include <stdio.h>
#include <stdlib.h>
/* reads hex subjects on stdin; compares @P_search with pp_search at every
 * startpos 0..n+1 */
int main(void)
{
    static char line[4096];
    unsigned char subj[2048];
    long cells = 0, matches = 0, diffs = 0;
    while (fgets(line, sizeof line, stdin)) {
        size_t n = 0;
        for (char *h = line; h[0] && h[1] && h[0] != '\n'; h += 2) {
            unsigned v; sscanf(h, "%2x", &v); subj[n++] = (unsigned char)v;
        }
        for (size_t from = 0; from <= n + 1; from++) {
            ptrdiff_t a[PP_NCAPS][2] = {{0}}, b[PP_NCAPS][2] = {{0}};
            int ra = @P_search(subj, n, from, a), rb = pp_search(subj, n, from, b);
            cells++;
            if (rb == 1) matches++;
            if (ra != rb || (ra == 1 && (a[0][0] != b[0][0] || a[0][1] != b[0][1]))) {
                if (diffs++ < 5)
                    printf("DIFF from=%zu n=%zu compound=%d(%td,%td) plain=%d(%td,%td)\n",
                           from, n, ra, a[0][0], a[0][1], rb, b[0][0], b[0][1]);
            }
        }
    }
    printf("cells=%ld matches=%ld diffs=%ld\n", cells, matches, diffs);
    return diffs ? 1 : 0;
}
"""


BOUNDED = r"""
#include <stdio.h>
/* (6): the one-attempt request on an ordinary artifact against the plain
 * artifact's match-here, at every character start 0..n */
int main(void)
{
    static char line[4096];
    unsigned char subj[2048];
    long cells = 0, diffs = 0;
    while (fgets(line, sizeof line, stdin)) {
        size_t n = 0;
        for (char *h = line; h[0] && h[1] && h[0] != '\n'; h += 2) {
            unsigned v; sscanf(h, "%2x", &v); subj[n++] = (unsigned char)v;
        }
        for (size_t from = 0; from <= n; from++) {
            if (UTF && from < n && (subj[from] & 0xC0) == 0x80) continue;
            ptrdiff_t a[NB_NCAPS][2] = {{0}}, b[PP_NCAPS][2] = {{0}};
            int ra = nb_search(subj, n, from, a);
            rx_ctx c = { .subject = subj, .len = n, .pos = from };
            ptrdiff_t rb = pp_match_caps(&c, b);
            cells++;
            int same = ra == 1 ? rb >= 0 && a[0][0] == (ptrdiff_t)from && a[0][1] == b[0][1]
                     : ra == 0 ? rb == -1 : (ptrdiff_t)ra == rb;
            if (!same && diffs++ < 5)
                printf("DIFF from=%zu n=%zu bounded=%d(%td,%td) match_caps=%td\n",
                       from, n, ra, a[0][0], a[0][1], rb);
        }
    }
    printf("cells=%ld diffs=%ld\n", cells, diffs);
    return diffs ? 1 : 0;
}
"""


def subjects(utf):
    alpha = [b" ", b"\t", b"\n", b"a", b"b", b"q", b"{", b"}", b"x"]
    alpha += [b"\xc3\xa9", b"\x80", b"\xc3", b"\xff"] if utf else [b"\xe9", b"\xff"]
    out = [b""]
    for L in (1, 2, 3):
        out += [b"".join(t) for t in itertools.product(alpha, repeat=L)]
    rnd = random.Random(1)
    out += [b"".join(rnd.choice(alpha) for _ in range(rnd.randint(4, 14))) for _ in range(300)]
    return b"".join(s.hex().encode() + b"\n" for s in out)


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, timeout=600, **kw)


def main():
    drive, work = sys.argv[1:3]
    fails = []
    r = run([drive, "selfcheck"])
    print(r.stdout.decode(), end="")
    if r.returncode:
        fails.append("selfcheck: a part with an unstated field was accepted")
    listing = "".join("%s\t%s\t%s\n" % (w, p.hex(), q.hex() if q else "-")
                      for w, p, q, _g in WITNESSES).encode()
    cells = matches = bcells = 0
    for arm, args, utf, guard, ucheck in ARMS:
        texts = {}
        for pfx in ("kz", L60):
            d = os.path.join(work, arm, pfx[:2] + str(len(pfx)))
            os.makedirs(d, exist_ok=True)
            r = run([drive, "parts", d, pfx] + args, input=listing)
            if r.returncode:
                fails.append("[%s] compound_drive parts exited %d: %s" % (arm, r.returncode, r.stderr.decode()[:300]))
                continue
            rows = [ln.split("\t") for ln in r.stdout.decode().splitlines()]
            for row in rows:
                if row[2] != "ok":
                    fails.append("[%s %s] %s %s refused: %s" % (arm, pfx[:2], row[0], row[1], row[3]))
            for w, p, q, hasg in WITNESSES:
                parts = [os.path.join(d, "%s.%s.c" % (w, t)) for t in ("f", "q") if t == "f" or q]
                if not all(os.path.exists(x) for x in parts):
                    continue
                for x in parts:
                    t = open(x).read()
                    texts[(pfx, w, os.path.basename(x))] = t
                    for shared in ("PCREC_RX_ABI_H", "PCREC_FEATURE_SET", "struct rx_info ",
                                   "int main(", "#include <stdint.h>"):
                        if shared in t:
                            fails.append("[%s] %s part %s carries a shared block (%s)" % (arm, w, x, shared))
                    bounded = "const size_t start_max = search_from" in t
                    if bounded != x.endswith(".f.c"):
                        fails.append("[%s] %s part %s: one-attempt bound %s" % (
                            arm, w, x, "present on Q" if bounded else "missing on F"))
                nb = os.path.join(d, w + ".nb.c")
                if pfx == "kz" and os.path.exists(nb):
                    ntu = os.path.join(d, w + ".nbtu.c")
                    with open(ntu, "w") as f:
                        f.write("#define UTF %d\n" % utf)
                        f.write(open(os.path.join(d, w + ".plain.c")).read())
                        f.write(open(nb).read())
                        f.write(BOUNDED)
                    nexe = os.path.join(d, w + ".nbexe")
                    b = run([CC] + GENCFLAGS + ["-o", nexe, ntu])
                    if b.returncode:
                        fails.append("[%s] %s: the bounded ordinary artifact did not build: %s"
                                     % (arm, w, b.stderr.decode()[:400]))
                    else:
                        o = run([nexe], input=subjects(utf))
                        out = o.stdout.decode().strip().splitlines()
                        if o.returncode:
                            fails.append("[%s] %s: the one-attempt request differs from "
                                         "match-here: %s" % (arm, w, " | ".join(out[-6:])))
                        else:
                            bcells += int(out[-1].split()[0].split("=")[1])
                tu = os.path.join(d, w + ".tu.c")
                with open(tu, "w") as f:
                    f.write("#define UTF %d\n#define GUARD %d\n#define UCHECK %d\n#define HAS_G %d\n"
                            "#define QNEVER %d\n" % (utf, guard, ucheck, hasg, 0 if q else 1))
                    f.write(open(os.path.join(d, w + ".plain.c")).read())
                    for x in parts:
                        f.write(open(x).read())
                    f.write(CONTROLLER.replace("@P", pfx))
                exe = os.path.join(d, w + ".exe")
                b = run([CC] + GENCFLAGS + ["-o", exe, tu])
                if b.returncode:
                    fails.append("[%s %s] %s: the one-TU -Werror build failed: %s"
                                 % (arm, pfx[:2], w, b.stderr.decode()[:400]))
                    continue
                g = run(["nm", "-g", "--defined-only", exe]).stdout.decode()
                leaked = [ln.split()[-1] for ln in g.splitlines() if "__f_" in ln or "__q_" in ln]
                if leaked:
                    fails.append("[%s] %s: part symbols are global: %s" % (arm, w, leaked))
                o = run([exe], input=subjects(utf))
                out = o.stdout.decode().strip().splitlines()
                tally = out[-1] if out else ""
                if o.returncode:
                    fails.append("[%s %s] %s: compound differs from the plain artifact: %s"
                                 % (arm, pfx[:2], w, " | ".join(out[-6:])))
                elif pfx == "kz":
                    kv = dict(x.split("=") for x in tally.split())
                    cells += int(kv["cells"]); matches += int(kv["matches"])
        # K79: the long-prefix text is the short one respelled.
        for (pfx, w, name), t in texts.items():
            if pfx != "kz" or (L60, w, name) not in texts:
                continue
            want = t.replace("kz__", L60 + "__").replace("KZ__", L60.upper() + "__")
            if want != texts[(L60, w, name)]:
                fails.append("[%s] K79: %s %s differs at the 60-byte prefix beyond the spelling"
                             % (arm, w, name))
    for f in fails[:40]:
        print("FAIL: " + f)
    floor_ok = cells >= 100000 and matches >= 5000 and bcells >= 20000
    print("%s: B1 parts: %d witnesses x %d arms x 2 prefixes; %d cells, %d matches "
          "against the plain artifact; %d bounded-request cells; %d failures"
          % ("PASS" if not fails and floor_ok else "FAIL", len(WITNESSES), len(ARMS),
             cells, matches, bcells, len(fails)))
    if not floor_ok:
        print("FAIL: below the population floor (100000 cells, 5000 matches, "
              "20000 bounded-request cells)")
    return 1 if fails or not floor_ok else 0


if __name__ == "__main__":
    sys.exit(main())
