"""adasim/common.py -- loaders shared by fit.py / sim.py: per-stretch features, measured ns tables."""
import re, glob, os
import numpy as np

W = "/home/pcrec/projects/pcrec/worktrees/flat"
MDIR = W + "/build/adasim/m"
E8 = "/home/pcrec/projects/pcrec/worktrees/e8min/build/e8slot_r2"
REPORT = W + "/docs/dev/lanes/flat_report.md"
M1 = np.uint64(0x7fffffffffffffff)


def popcnt(a):
    a = a.astype(np.uint64)
    a = a - ((a >> np.uint64(1)) & np.uint64(0x5555555555555555))
    a = (a & np.uint64(0x3333333333333333)) + ((a >> np.uint64(2)) & np.uint64(0x3333333333333333))
    a = (a + (a >> np.uint64(4))) & np.uint64(0x0f0f0f0f0f0f0f0f)
    return ((a * np.uint64(0x0101010101010101)) >> np.uint64(56)).astype(np.int32)


def stretch_feats(cell, subj):
    m = np.load(f"{MDIR}/{cell}__{subj}.npy")
    fid = np.load(f"{MDIR}/{cell}__{subj}.fid.npy")
    k = popcnt(m)
    t = popcnt((m ^ (m >> np.uint64(1))) & M1)
    return m, k, t, fid


def flat_table():
    """{(cell, subject_fullname): dict(walk, V1, M64, F8, F64 as ns)} from flat_report.md section 2."""
    out = {}
    for l in open(REPORT):
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        if len(c) == 8 and re.match(r"(j1-|an-)", c[0]) and re.match(r"^\d+$", c[2]):
            w = float(c[2])
            pct = lambda s: float(s.split()[0])
            out[(c[0], c[1])] = dict(walk=w, V1=w * (1 + pct(c[4]) / 100), F8=w * (1 + pct(c[5]) / 100),
                                     F64=w * (1 + pct(c[6]) / 100), M64=w * (1 + pct(c[7]) / 100), floor=float(c[3]))
    return out


def e8_table():
    out = {}
    for l in open(E8 + "/e8_cells.tsv").read().splitlines()[1:]:
        f = l.split("\t")
        if f[0] == "J1":
            out[(f[1], f[3])] = dict(walk=float(f[6]), V1=float(f[7]), floor=float(f[8]), matches=int(f[13]))
    return out


def full_name(cell, short, have):
    for (c, s) in have:
        if c == cell and (s == short or s.endswith("__" + short)):
            return s
    raise KeyError((cell, short))


def qproxy(m, order=6):
    """per-stretch count of bits the subject's ideal static order-`order` context predictor gets wrong (the e8why
    Q numerator: the walk's exit branch is predictable iff the member bit is predictable from the last bits)."""
    n = len(m)
    bits = np.unpackbits(m.astype("<u8").view(np.uint8).reshape(n, 8), axis=1, bitorder="little").reshape(-1)
    ctx = np.zeros(len(bits), np.int32)
    for j in range(1, order + 1):
        ctx[j:] |= bits[:-j].astype(np.int32) << (j - 1)
    cnt = np.zeros((1 << order, 2), np.int64)
    np.add.at(cnt, (ctx, bits), 1) if len(bits) < 1 else None
    cnt[:, 0] = np.bincount(ctx[bits == 0], minlength=1 << order)
    cnt[:, 1] = np.bincount(ctx[bits == 1], minlength=1 << order)
    maj = (cnt[:, 1] > cnt[:, 0]).astype(np.uint8)
    wrong = (bits != maj[ctx]).astype(np.int32)
    return wrong.reshape(n, 64).sum(axis=1)


FDIR = W + "/build/adasim/f"


def subjects():
    """[(cell, subject_fullname)] for every feature file."""
    out = []
    for p in sorted(glob.glob(MDIR + "/*.npy")):
        b = os.path.basename(p)
        if b.endswith(".fid.npy"):
            continue
        c, s = b[:-4].split("__", 1)
        out.append((c, s))
    return out


def feats(cell, subj):
    """(k, t, q) int32 arrays per whole 64-byte stretch, cached; k = members, t = transitions, q = Q-proxy misses."""
    os.makedirs(FDIR, exist_ok=True)
    f = f"{FDIR}/{cell}__{subj}.npz"
    if os.path.exists(f):
        z = np.load(f)
        return z["k"], z["t"], z["q"]
    m, k, t, _ = stretch_feats(cell, subj)
    q = qproxy(m)
    np.savez(f, k=k, t=t, q=q)
    return k, t, q


def resolve(have, cell, short):
    """the feature-file subject name matching a table's (possibly short) subject name."""
    for c, s in have:
        if c == cell and (s == short or s.endswith("__" + short)):
            return s
    raise KeyError((cell, short))
