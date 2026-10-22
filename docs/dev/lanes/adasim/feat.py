"""adasim/feat.py -- per-stretch member masks for every subject flat and e8 timed (count-only, no clock).
usage: feat.py OUTDIR   -> OUTDIR/<cell>__<subject>.npy (uint64 member mask per whole 64-byte stretch, files
concatenated; .fid.npy = file index per stretch). The member set is read from the cell's V1 artifact (__member())."""
import os, re, sys, glob
import numpy as np

E8 = "/home/pcrec/projects/pcrec/worktrees/e8min/build/e8slot_r2"
SUBJ = E8 + "/subj"
G2 = "/home/pcrec/projects/pcrec/worktrees/memfn-slot/grid2/subj"
FLAT = "/home/pcrec/projects/pcrec/worktrees/flat/docs/dev/lanes/flat/stretch_counts.tsv"
MEMBER_RE = re.compile(r"__member\(unsigned char x\)\s*\{\s*return (.*?);\s*\}", re.S)


def member_table(cell):
    src = open(f"{E8}/bin/{cell}/V1/art.c").read() if os.path.exists(f"{E8}/bin/{cell}/V1/art.c") else \
        open(f"/home/pcrec/projects/pcrec/worktrees/flat/build/flat/slot/bin/{cell}/V1/art.c").read()
    m = MEMBER_RE.search(src)
    if not m:
        raise SystemExit(f"{cell}: no __member")
    expr = m.group(1).replace("(unsigned char)", "u8")
    u8 = lambda v: v & 255
    t = np.zeros(256, np.uint8)
    for x in range(256):
        t[x] = 1 if eval(expr, {"u8": u8, "x": x}) else 0
    return t, expr


def masks(path, tab):
    files = sorted(glob.glob(path + "/b*")) if os.path.isdir(path) else [path]
    out, fid = [], []
    for i, f in enumerate(files):
        b = np.fromfile(f, np.uint8)
        n = len(b) // 64
        if n == 0:
            continue
        bits = tab[b[: n * 64]].reshape(n, 64)
        m = np.packbits(bits, axis=1, bitorder="little").view("<u8").reshape(n)
        out.append(m); fid.append(np.full(n, i, np.int32))
    return np.concatenate(out), np.concatenate(fid)


if __name__ == "__main__":
    od = sys.argv[1]; os.makedirs(od, exist_ok=True)
    rows = [l.split("\t") for l in open(E8 + "/groups2.tsv").read().splitlines()[1:]]
    jobs = {(r[1], r[2]): f"{SUBJ}/{r[2]}" for r in rows}
    for l in open(E8 + "/e8_cells.tsv").read().splitlines()[1:]:
        f = l.split("\t")
        if f[0] == "J1":
            jobs[(f[1], f[3])] = f"{SUBJ}/{f[3]}"
    for l in open(FLAT).read().splitlines()[1:]:
        c, s = l.split("\t")[:2]
        if not c.startswith("an-"):
            jobs[(c, s)] = f"{SUBJ}/{s}"
    jobs[("an-dig", "g2-dig-n64k-g8-L1k-reg-S")] = G2 + "/g2-dig-n64k-g8-L1k-reg-S"
    jobs[("an-dfa-hat", "g2-dfa-hat-n64k-ginf-L32-S")] = G2 + "/g2-dfa-hat-n64k-ginf-L32-S"
    for (c, s), p in sorted(jobs.items()):
        tab, expr = member_table(c)
        m, fid = masks(p, tab)
        np.save(f"{od}/{c}__{s}.npy", m); np.save(f"{od}/{c}__{s}.fid.npy", fid)
        print(c, s, len(m), expr, flush=True)
