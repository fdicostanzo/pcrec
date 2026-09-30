#!/usr/bin/env python3
"""[OPT-HYB-RESEED] answer identity at EVERY startpos: branch point (abi 46)
vs this change, over every artifact the change moves (identity_sweep.py's
`mover` rows).

Each mover pattern is compiled by both compilers (`--features all -p rx`,
its encoding), linked with one driver, and run on a deterministic subject
set built from the pattern's own characters plus fillers (valid UTF-8 under
utf8), at every startpos 0..n. The driver prints the full result per call —
the return code (1 / 0 / a give-up or refusal code) and caps[0] — so a
give-up that moves is a difference too. The two transcripts must be equal.
Usage: answer_diff.py BASE_PCREC NEW_PCREC IDSWEEP_TSV OUT_LOG [--jobs 2]
"""
import argparse, ast, concurrent.futures, os, random, subprocess, sys, tempfile

DRIVER = r'''
#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
extern int rx_search(const unsigned char *, size_t, size_t, ptrdiff_t (*)[2]);
int main(int argc, char **argv) {
    FILE *f = fopen(argv[1], "rb"); unsigned char buf[4096]; unsigned len;
    while (fread(&len, 4, 1, f) == 1) {
        if (len > sizeof buf || fread(buf, 1, len, f) != len) return 2;
        for (size_t sp = 0; sp <= len; sp++) {
            ptrdiff_t c[1][2] = {{-9, -9}};
            int r = rx_search(buf, len, sp, c);
            printf("%zu:%d:%td,%td ", sp, r, r == 1 ? c[0][0] : -1, r == 1 ? c[0][1] : -1);
        }
        putchar('\n');
    }
    return 0;
}
'''


def subjects(pat, enc, seed):
    rng = random.Random(seed)
    chars = sorted(set(c for c in pat if c.isprintable() and c not in "()[]{}?*+|^$\\"))
    if enc == "byte":
        chars = [c for c in chars if ord(c) < 128] + ["\xe9"]
    fill = ["x", "y", " ", "a", "\n"] + (["é", "日", "本"] if enc == "utf8" else [])
    alpha = chars + fill
    out = [""]
    for _ in range(40):
        n = rng.randint(1, 48)
        out.append("".join(rng.choice(alpha) for _ in range(n)))
    lit = "".join(chars)
    out += [lit, lit * 3, "y" * 20 + lit + "y" * 20, (lit + "x") * 5]
    enc_name = "utf-8" if enc == "utf8" else "latin-1"
    res = []
    for s in out:
        try: res.append(s.encode(enc_name))
        except UnicodeEncodeError: pass
    return res


def run_one(a, pat, enc, idx, tmp):
    d = os.path.join(tmp, f"p{idx}_{enc}")
    os.makedirs(d, exist_ok=True)
    subj = os.path.join(d, "subj.bin")
    with open(subj, "wb") as o:
        for s in subjects(pat, enc, idx):
            o.write(len(s).to_bytes(4, "little")); o.write(s)
    outs = []
    for tag, binp in (("base", a.base), ("new", a.new)):
        c = os.path.join(d, f"{tag}.c")
        argv = [binp, "--features", "all", "-p", "rx"] + (["-e", "utf8"] if enc == "utf8" else []) + ["-o", c, "--pattern", pat]
        if subprocess.run(argv, capture_output=True, timeout=120).returncode != 0:
            return ("COMPILE-FAIL", tag)
        exe = os.path.join(d, tag)
        r = subprocess.run(["gcc-16", "-O1", "-w", "-o", exe, c, os.path.join(tmp, "drv.c")], capture_output=True, timeout=300)
        if r.returncode != 0:
            return ("SKIP-LINK", tag)  # e.g. a vars artifact: its search takes the environment pair
        r = subprocess.run([exe, subj], capture_output=True, timeout=300)
        outs.append(r.stdout if r.returncode == 0 else b"RC%d" % r.returncode)
    return ("same" if outs[0] == outs[1] else "DIFF", outs[0].count(b":"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("base"); ap.add_argument("new"); ap.add_argument("tsv"); ap.add_argument("out")
    ap.add_argument("--jobs", type=int, default=2)
    a = ap.parse_args()
    work = []
    for line in open(a.tsv, encoding="utf-8", errors="surrogateescape").read().splitlines()[1:]:
        parts = line.split("\t")   # identity_sweep.py's columns; the pattern is always last
        enc, verdict, pat = parts[1], parts[2], parts[-1]
        if verdict == "mover":
            work.append((ast.literal_eval(pat), enc))
    tally, cells, diffs = {}, 0, []
    with tempfile.TemporaryDirectory() as tmp:
        open(os.path.join(tmp, "drv.c"), "w").write(DRIVER)
        with concurrent.futures.ThreadPoolExecutor(a.jobs) as ex:
            futs = {ex.submit(run_one, a, p, e, i, tmp): (p, e) for i, (p, e) in enumerate(work)}
            for fu in concurrent.futures.as_completed(futs):
                p, e = futs[fu]
                try: v = fu.result()
                except Exception as x: v = ("ERROR:" + type(x).__name__, 0)
                tally[v[0]] = tally.get(v[0], 0) + 1
                if v[0] == "same": cells += v[1]
                if v[0] not in ("same", "SKIP-LINK"): diffs.append((e, v, p))
    with open(a.out, "w", encoding="utf-8", errors="surrogateescape") as o:
        o.write(f"movers: {len(work)}\n")
        for k in sorted(tally): o.write(f"  {k}: {tally[k]}\n")
        o.write(f"identical (subject, startpos) cells: {cells}\n")
        for e, v, p in diffs: o.write(f"{e}\t{v}\t{p!r}\n")
    print(open(a.out).read())
    sys.exit(1 if diffs else 0)


if __name__ == "__main__":
    main()
