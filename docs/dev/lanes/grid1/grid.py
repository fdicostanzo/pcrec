#!/usr/bin/env python3
"""grid1: the slot's DESIGN (declared tables), its SUBJECTS and their ORACLE.

  python3 -I grid.py design OUT     writes OUT/arms.tsv (F1 + F3 cells),
                                    OUT/arms_f2.tsv (F2's perf cells, never
                                    timed by time.sh) and OUT/subjects.tsv
  python3 -I grid.py gen OUT [-j N]  writes every subject in subjects.tsv to
                                    OUT/subj/<name> (a file, or a directory of
                                    distinct buffers for a STREAMED subject),
                                    its facts to OUT/subj_facts.tsv
  python3 -I grid.py oracle OUT CELL SUBJ MODE   one oracle line (any subject,
                                    the real ones included)
  python3 -I grid.py oracles OUT [-j N]  OUT/oracle.tsv: the oracle line of
                                    every (own cell, subject, mode) the arm
                                    tables (timed + f2) name; python `re`
                                    over the bytes, never pcrec
  python3 -I grid.py count OUT       the design's row/launch counts per block

Everything here is a declared table: CELLS (pattern + token alphabet per
cell), BLOCKS (which subjects x modes x arms each part of the design times).
Change the design by editing a row, never by adding a branch.

SUBJECT MODEL (costmodel_report.md §0; the brief's "landing"):
  - a LANDING is a byte in the site's scanned set that does NOT start a match
    (one member byte, filler on both sides: the attempt that follows fails
    within 1-2 bytes, a MINIMAL-VERIFY landing; near-hit depth is not an axis);
  - a MATCH token is planted at the end of every L-byte window (L = 0: none;
    L >= n: one match at the end of the subject), so a find-all call spans
    ~L bytes and a `first` call is ONE call of span ~L;
  - landings are planted with mean gap g (g = 0: none) and a SHAPE:
      reg    exactly every g bytes;
      u      i.i.d. gaps uniform in [max(2, g - g//2), g + g//2] (mean g;
             the default: real text's gaps vary, and a period-g stream is one
             the walk's exit branch learns);
      burst  bursts of 8 landings 2 bytes apart, then one gap closing the
             8g period (mean g);
    a landing never touches a match token or another landing (a one-byte
    guard each side); a landing that would is DROPPED, so the planted count
    is a fact recorded in facts.tsv, never assumed;
  - reuse: `rep` = one buffer of n bytes (the timed loop repeats it);
    `S` (streamed) = STREAM_TOTAL / n distinct buffers of the same (g, L,
    shape), each from its own seed, cycled by the driver.
"""
import hashlib, os, re, sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

MASK = (1 << 64) - 1
STREAM_TOTAL = 64 << 20          # §F: "streamed distinct buffers totalling 64 MiB"
N_DEFAULT = 65536
INF = 0                          # g = 0: no landings; L = 0: no match

# ---- CELLS: name | pattern (bytes regex, the oracle) | filler | landing members | match
# tokens | REQ | SET. REQ = the cell's required byte(s) outside its set: a subject with
# NO member (no landing, no match) carries them in its filler, or the artifact's
# whole-window pre-check answers before the site runs (the site would be UNREACHED
# and the row would time the pre-check). SET = the site's scanned set, the
# generator's no-member self-check for those subjects.
# dfa-hat's filler is NON-WORD bytes: the DFA hat is the scan the DFA's START
# state runs, and in a word the DFA itself walks the letters (with letter
# filler the site counted 2 uses per call at every g: check.sh leg G). So a
# dfa-hat landing is a word-initial near hit (" t." : \b holds, `t` then a
# non-word byte fails), the prose case.
# Every cell's art comes from slot25c ALPHA except `quad`, which build.sh emits
# with this worktree's compiler (the only 4-term cover there is: `[0-9A-Fa-f_]+=`).
PUNCT = b" !\"#$%&'()*+,-./:;<>?@[\\]^`{|}~"   # none of 0-9 A-Z a-z _ =
CELLS = {
    # cell      pattern                       filler                             landing                         match tokens                     REQ    SET
    "dig":     (rb"[0-9]+x",                  b"abcdefghijklmnopqrstuvwyz .,;-", b"0123456789",                  [b"%dx"],                        b"x", rb"[0-9]"),
    "bounded": (rb"[a-z]+\b",                 b"0123456789_",                    b"abcdefghijklmnopqrstuvwxyz",  [b"%c "],                        b"",  rb"[a-z]"),
    "dfa-hat": (rb"\b(?:true|false|null)\b",  b" .,;:-()=",                      b"fnt",                         [b" true ", b" null ", b" false "], b"", rb"[fnt]"),
    "hex-run": (rb"[a-f0-9]+",                PUNCT, b"", [], b"",  rb"[a-f0-9]"),
    "word-eq": (rb"[A-Za-z_]+=",              PUNCT, b"", [], b"=", rb"[A-Za-z_]"),
    "quad":    (rb"[0-9A-Fa-f_]+=",           PUNCT, b"", [], b"=", rb"[0-9A-Fa-f_]"),
}
# F3's subjects are per cell (family "f3-<cell>"): PUNCT plus the cell's REQ, no member

def tokens_for(cell, rng, room):
    """one match token for CELL that fits in ROOM bytes"""
    toks = CELLS[cell][3]
    out = []
    for t in toks:
        if b"%d" in t: t = t.replace(b"%d", bytes([0x30 + int(rng.integers(10))]))
        if b"%c" in t: t = t.replace(b"%c", bytes([0x61 + int(rng.integers(26))]))
        if len(t) + 1 <= room: out.append(t)
    return out[int(rng.integers(len(out)))] if out else None

# ---- the forms (arm names; `walk` is every own cell's base)
F9 = ["walk", "V1", "S1", "A1", "V3", "S3", "A3", "Sn", "An"]   # §F's forms
F6 = ["walk", "V1", "S1", "A1", "Sn", "An"]                     # `first` mode: §F's forms less the kept
                                                                # twins (one call keeps nothing; CUT, report §2)
F4 = ["walk", "V1", "A1", "A3"]                                 # §F's span-axis forms
FALIGN = ["walk", "S1", "S2", "A1", "A2"]                       # the prologue arms
FF3 = ["walk", "V1", "V2", "S1", "S2", "A1", "A2", "Sn", "An"]  # F3: first mode, no kept twins
G8 = [2, 4, 8, 16, 32, 64, 256, INF]

def sname(fam, n, g, L, shape, reuse):
    def k(v): return "inf" if v == 0 else (f"{v >> 20}m" if v >= 1 << 20 and v % (1 << 20) == 0 else
                                           f"{v >> 10}k" if v >= 1024 and v % 1024 == 0 else str(v))
    s = f"g1-{fam}-n{k(n)}-g{k(g)}-L{'none' if L == 0 else k(L)}"
    if g not in (0, 2): s += f"-{shape}"
    return s + ("-S" if reuse == "S" else "")

# ---- BLOCKS: block | cell | arms | mode | subjects (fam, n, g, L, shape, reuse) | offsets
def blocks():
    B = []
    def add(block, cell, arms, mode, subs, offs=(None,)):
        B.append((block, cell, arms, mode, subs, offs))
    def sub(cell, g, L, n=N_DEFAULT, shape="u", reuse="rep"):
        return (cell, n, g, L, "reg" if g == 2 else shape, reuse)
    # dig: the PF 1-term set, the primary cell (every axis)
    add("D1-core-rep", "dig", F9, "all", [sub("dig", g, L) for g in G8 for L in (32, 1024, 65536)])
    add("D2-core-stream", "dig", F9, "all", [sub("dig", g, L, reuse="S") for g in (2, 8, 32, 256) for L in (32, 1024, 65536)])
    add("D3-span", "dig", F4, "all", [sub("dig", g, L) for g in (4, 64) for L in (8, 128)])
    add("D4-first", "dig", F6, "first", [sub("dig", g, L) for g in (2, 8, INF) for L in (8, 32, 128)])
    add("D5-len-sparse", "dig", F6, "first", [sub("dig", INF, 0, n=n) for n in (48, 63, 64, 65, 128)])
    add("D5-len-dense", "dig", F9, "all", [sub("dig", 8, 32, n=n) for n in (48, 63, 64, 65, 128)])
    add("D6-align-first", "dig", FALIGN, "first", [sub("dig", INF, 65536), sub("dig", INF, 0, n=65)], offs=(0, 7, 31))
    add("D6-align-all", "dig", FALIGN, "all", [sub("dig", 8, 1024)], offs=(0, 7, 31))
    add("D7-shape", "dig", F9, "all", [sub("dig", g, 1024, shape=sh, reuse=r) for g in (8, 32) for sh in ("reg", "burst") for r in ("rep", "S")])
    # dfa-hat: the DFA hat, 2 terms
    add("H1-core-rep", "dfa-hat", F9, "all", [sub("dfa-hat", g, L) for g in G8 for L in (32, 1024, 65536)])
    add("H2-core-stream", "dfa-hat", F9, "all", [sub("dfa-hat", g, L, reuse="S") for g in (2, 8, 32, 256) for L in (1024, 65536)])
    add("H3-span", "dfa-hat", F4, "all", [sub("dfa-hat", g, L) for g in (4, 64) for L in (8, 128)])
    add("H4-first", "dfa-hat", F6, "first", [sub("dfa-hat", g, L) for g in (2, 8, INF) for L in (8, 32, 128)])
    # bounded: the PF run-consuming set ([a-z], the dense-prose loser)
    add("B1-core-rep", "bounded", F9, "all", [sub("bounded", g, L) for g in (2, 8, 32, INF) for L in (8, 32, 1024, 65536)])
    add("B2-core-stream", "bounded", F9, "all", [sub("bounded", g, L, reuse="S") for g in (2, 32) for L in (8, 1024)])
    # F3: 1-4 term sets on subjects with NO member (the per-byte rate beta per width)
    for c in ("dig", "hex-run", "word-eq", "quad"):
        add("F3-sparse", "f3-" + c, FF3, "first", [("f3-" + c, n, INF, 0, "u", "rep") for n in (65536, 1 << 20)])
    return B

F2_CELLS = ["hex-run", "bounded", "dfa-hat"]
F2_SUBJ = ["prose1m", "docs1m", "code1m", "prose64k", "docs64k", "code64k"]
F2_ARMS = F4

def design(out):
    rows = {}            # (cell, arm) -> {mode: [subject tokens]}
    subjects = {}
    order = []
    for block, cell, arms, mode, subs, offs in blocks():
        for s in subs:
            subjects[sname(s[0], *s[1:])] = s
        toks = [sname(s[0], *s[1:]) + ("" if o is None else f"@{o}") for s in subs for o in offs]
        for a in arms:
            key = (cell, a)
            if key not in rows: rows[key] = {}; order.append(key)
            rows[key].setdefault(mode, [])
            rows[key][mode] += [t for t in toks if t not in rows[key][mode]]
    with open(os.path.join(out, "arms.tsv"), "w") as f:
        f.write("# grid1 own arms (F1 + F3). cell\tarm\trole\tsubjects\tmodes -- see README.md\n")
        for cell, a in order:
            for mode, toks in rows[(cell, a)].items():
                f.write(f"{cell}\t{a}\t{'base' if a == 'walk' else 'arm'}\t{','.join(toks)}\t{mode}\n")
    with open(os.path.join(out, "arms_f2.tsv"), "w") as f:
        f.write("# grid1 F2 (perf branch-miss pass; never timed by time.sh). Same columns.\n")
        for c in F2_CELLS:
            for a in F2_ARMS:
                f.write(f"{c}\t{a}\t{'base' if a == 'walk' else 'arm'}\t{','.join(F2_SUBJ)}\tall\n")
    with open(os.path.join(out, "subjects.tsv"), "w") as f:
        f.write("name\tfamily\tn\tg\tL\tshape\treuse\n")
        for nm, s in sorted(subjects.items()):
            f.write(f"{nm}\t{s[0]}\t{s[1]}\t{s[2]}\t{s[3]}\t{s[4]}\t{s[5]}\n")

def count(out):
    tot_g = tot_l = 0
    print(f"{'block':18} {'cell':12} {'mode':5} {'groups':>6} {'arms':>4} {'launch/round':>12}")
    for block, cell, arms, mode, subs, offs in blocks():
        g = len(subs) * len(offs); per = len(arms) + 1     # +1: the base's A/A twin
        tot_g += g; tot_l += g * per
        print(f"{block:18} {cell:12} {mode:5} {g:6} {len(arms):4} {g * per:12}")
    print(f"TOTAL groups={tot_g} launches/round={tot_l} (before same_first skips)")

# ---- generation
def gen_buffer(fam, n, g, L, shape, seed):
    rng = np.random.default_rng(seed)
    cell = fam[3:] if fam.startswith("f3-") else fam
    f3 = fam != cell
    nomember = f3 or (g == 0 and L == 0)
    filler = np.frombuffer((PUNCT if f3 else CELLS[cell][1]) + (CELLS[cell][4] if nomember else b""), np.uint8)
    s = filler[rng.integers(len(filler), size=n)].copy()
    kind = np.zeros(n + 2, np.uint8)          # 1 token byte, 2 guard (index + 1)
    nmatch = 0
    if not f3 and L:
        wins = [(0, n)] if L >= n else [(k * L, (k + 1) * L) for k in range(n // L)]
        for lo, hi in wins:
            t = tokens_for(cell, rng, hi - lo)
            if t is None: raise SystemExit(f"no match token fits L={L} for {fam}")
            st = hi - 1 - len(t)
            if st < 0: continue
            s[st:st + len(t)] = np.frombuffer(t, np.uint8)
            kind[st + 1:st + 1 + len(t)] = 1
            kind[st] = max(kind[st], 2); kind[st + 1 + len(t)] = max(kind[st + 1 + len(t)], 2)
            nmatch += 1
    nland = 0
    if not f3 and g:
        if shape == "reg" or g <= 2:
            pos = np.arange(g // 2, n, g)
        elif shape == "u":
            lo, hi = max(2, g - g // 2), g + g // 2
            gaps = rng.integers(lo, hi + 1, size=n // lo + 2)
            pos = np.cumsum(gaps) - gaps[0] + g // 2
        elif shape == "burst":
            per = 8 * g
            starts = np.arange(per // 2, n, per)
            pos = (starts[:, None] + 2 * np.arange(8)[None, :]).ravel()
        else:
            raise SystemExit("shape " + shape)
        pos = pos[(pos >= 1) & (pos < n - 1)]
        ok = (kind[pos + 1] == 0) & (kind[pos] != 1) & (kind[pos + 2] != 1)
        pos = pos[ok]
        mem = np.frombuffer(CELLS[cell][2], np.uint8)
        s[pos] = mem[rng.integers(len(mem), size=len(pos))]
        nland = len(pos)
    return s.tobytes(), nmatch, nland

def oracle_of(cell, buf, mode):
    rx = re.compile(CELLS[cell[3:] if cell.startswith("f3-") else cell][0])
    if mode == "first":
        m = rx.search(buf)
        return 1, ((m.start() * 31 + m.end()) & MASK) if m else 7
    h = 0; k = 0
    for m in rx.finditer(buf):
        k += 1; h = (h * 131 + m.start() * 31 + m.end()) & MASK
    return k, h

def oracle_line(cell, path, mode):
    bufs = [open(os.path.join(path, f), "rb").read() for f in sorted(os.listdir(path)) if not f.startswith(".")] \
        if os.path.isdir(path) else [open(path, "rb").read()]
    M = H = 0
    for b in bufs:
        m, h = oracle_of(cell, b, mode)
        M += m; H = (H * 1099511628211 + h) & MASK
    return f"matches={M} hash={H:x}"

def gen_one(args):
    out, name, fam, n, g, L, shape, reuse = args
    path = os.path.join(out, "subj", name)
    seed0 = int.from_bytes(hashlib.sha256(name.encode()).digest()[:8], "little")
    nbuf = STREAM_TOTAL // n if reuse == "S" else 1
    if reuse == "S": os.makedirs(path, exist_ok=True)
    tm = tl = 0; digests = set()
    for i in range(nbuf):
        b, m, l = gen_buffer(fam, n, g, L, shape, seed0 + i)
        tm += m; tl += l
        digests.add(hashlib.sha256(b).digest())
        # the planted-count self-check: the oracle must find exactly the planted matches
        cell = fam[3:] if fam.startswith("f3-") else fam
        k, _ = oracle_of(cell, b, "all")
        if k != m: raise SystemExit(f"GEN SELF-CHECK FAILED {name} buf {i}: planted {m} matches, oracle finds {k}")
        if m == 0 and l == 0:
            if re.search(CELLS[cell][5], b): raise SystemExit(f"GEN SELF-CHECK FAILED {name}: a no-member subject holds a member byte")
            if CELLS[cell][4] and CELLS[cell][4][:1] not in b: raise SystemExit(f"GEN SELF-CHECK FAILED {name}: no required byte")
        open(os.path.join(path, f"b{i:05d}") if reuse == "S" else path, "wb").write(b)
    if len(digests) != nbuf: raise SystemExit(f"GEN SELF-CHECK FAILED {name}: {nbuf - len(digests)} repeated buffers")
    return f"{name}\t{fam}\t{n}\t{g}\t{L}\t{shape}\t{reuse}\t{nbuf}\t{tm}\t{tl}\t{tm / (n * nbuf):.6g}\t{tl / (n * nbuf):.6g}"

def gen(out, jobs):
    os.makedirs(os.path.join(out, "subj"), exist_ok=True)
    rows = [l.rstrip("\n").split("\t") for l in open(os.path.join(out, "subjects.tsv")).readlines()[1:]]
    args = [(out, r[0], r[1], int(r[2]), int(r[3]), int(r[4]), r[5], r[6]) for r in rows]
    with ProcessPoolExecutor(jobs) as ex:
        facts = list(ex.map(gen_one, args))
    with open(os.path.join(out, "subj_facts.tsv"), "w") as f:
        f.write("name\tfamily\tn\tg\tL\tshape\treuse\tnbuf\tplanted_matches\tplanted_landings\tmatches_per_byte\tlandings_per_byte\n")
        f.write("\n".join(facts) + "\n")
    print(f"gen: {len(facts)} subjects")

def own_cell(cell):
    c = cell[3:] if cell.startswith("f3-") else cell
    return c in CELLS

def oracle_job(a):
    out, cell, s, m = a
    return f"{cell}\t{s}\t{m}\t{oracle_line(cell, os.path.join(out, 'subj', s), m)}"

def oracles(out, jobs):
    import subprocess
    here = os.path.dirname(os.path.abspath(__file__))
    keys = set()
    for line in subprocess.run([sys.executable, "-I", os.path.join(here, "arms.py"), out, "items", "all"],
                               capture_output=True, text=True, check=True).stdout.splitlines():
        c, a, r, s, m = line.split("\t")
        if own_cell(c): keys.add((c, s.split("@")[0], m))
    with ProcessPoolExecutor(jobs) as ex:
        res = list(ex.map(oracle_job, [(out, c, s, m) for c, s, m in sorted(keys)]))
    with open(os.path.join(out, "oracle.tsv"), "w") as f:
        f.write("\n".join(res) + "\n")
    print(f"oracles: {len(res)} (cell, subject, mode) lines")

if __name__ == "__main__":
    cmd, out = sys.argv[1], sys.argv[2]
    if cmd == "design": design(out)
    elif cmd == "gen": gen(out, int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[3] == "-j" else 4)
    elif cmd == "oracle": print(oracle_line(sys.argv[3], os.path.join(out, "subj", sys.argv[4]), sys.argv[5]))
    elif cmd == "oracles": oracles(out, int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[3] == "-j" else 4)
    elif cmd == "count": count(out)
    else: raise SystemExit(__doc__)
