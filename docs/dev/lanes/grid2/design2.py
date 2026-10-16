#!/usr/bin/env python3
"""grid2: the zen4-grid2 slot's DESIGN, its SUBJECTS and its ORACLE (libpcre2).

  python3 -I design2.py design OUT [--dry]   arms.tsv, arms_f2.tsv, subjects.tsv,
                                             groups2.tsv, fit_map.tsv, ext/ob/arms.tsv,
                                             ext/trig/arms.tsv
  python3 -I design2.py gen OUT [-j N]       OUT/subj/<name>/ (streamed directories +
                                             .manifest.tsv), OUT/subj_facts.tsv
  python3 -I design2.py oracles OUT [-j N]   OUT/oracle.tsv: the answer line of every
                                             (own cell, subject, mode) from libpcre2
                                             through tests/oracle/'s local adapter
                                             (the gate's leg O; NOT python re)
  python3 -I design2.py count OUT [--dry]    groups, arms and launches per item

It reuses grid1's grid.py (CELLS, blocks(), gen_buffer, sname) and extends its CELLS
table with the cells grid2 adds; grid1 itself is not touched. Design changes are table
edits (CELLS2, the ITEM_* tables), never branches.

THE ITEMS (r17b_prime.md §5.4; one row of the table each):
  1  the 149 grid1 fit groups (F1 141 + F3 8) re-timed STREAMED, every pickable arm at
     both layers (walk; SIMD-off V1; SIMD-on S1, A1; the iterator's A3 in find-all);
     base copies walk#b and walk#c are the harness's (BASE_COPIES=3). Groups that map
     to the same streamed subject (D1's repeated and D2's streamed twin) are ONE group
     here; fit_map.tsv maps every grid1 group to its grid2 group.
  2  dispatch TWINS ride item 1's groups (the interleave is within a group, so a
     twin and its single form are timed together): arms tw0/tw1/tw2 (the WALK+V1+W64
     scaffold with f forced to WALK / V1 / A1) on 20 dense F1 groups, on the member-free
     points (F3's 8 + the n = 48..128 points + new n = 8, 32), and sc0 (the walk moved
     into the scaffold's helper, no dispatch) on the R0-shaped member-free groups
     (hex-run, word-eq, \\w).
  3  one-byte arms at five kinds (o-fwd o-bnd o-hat o-hyb o-back): walk (the table
     walk at |S| = 1; o-back: the hand walk), libc (the artifact as the compiler emits
     it), v1 (one-term SWAR), loop (the generic byte loop); 6 gaps find-all streamed
     + 4 member-free lengths.
  4  NONE (arm `none`: the use's FIND statement deleted, the consumer walks) rides
     item 3's six gap groups of every kind.
  6  F2 perf on {walk, V1, A1} of every item-1 group (arms_f2.tsv, F2 rows);
  7  F2 streamed perf: hex-run, bounded, dfa-hat x 4 arms x prose/docs/code streamed;
  8  the pre-scan trigger probe: trig-dig / trig-word, keep (base) vs drop
     (-fno-req-byte -fno-req-run), early/late/absent x g.
"""
import hashlib, os, re, sys
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
G1 = os.path.normpath(os.path.join(HERE, "..", "grid1"))
sys.path.insert(0, G1)
sys.path.insert(0, HERE)
import grid                      # noqa: E402  (grid1's design module)
import streamgen as sg           # noqa: E402

INF = grid.INF
PUNCT = grid.PUNCT
SPIKE_SUBJ = os.environ.get("SPIKE", "/home/pcrec/projects/pcrec/worktrees/memfn-slot/spike1") + "/subj"

# ---- CELLS2: grid1's CELLS (read-only) plus grid2's. Same columns as grid.CELLS:
# pattern (bytes regex = the python-side description; the ORACLE is libpcre2 on it),
# filler, landing members, match tokens, REQ, SET.
LOW = b"abcdefghijklmnopqrstuvw0123456789 .,;-"             # no x y z
NONWORD = b" .,;:-()="
CELLS2 = {
    "wcls":      (rb"\w+=", PUNCT, b"", [], b"=", rb"\w"),   # R0's third scaffold cell (4 RANGE terms)
    # item 3/4 one-byte cells. The landing is the one member byte; a landing's attempt
    # dies within 1-2 bytes. REQ is "" because these cells are emitted with
    # -fno-req-byte -fno-req-run (the whole-window pre-check would answer a member-free
    # subject before the site ran; ext_ob/build.sh says so)
    "o-fwd":     (rb"xy+z", LOW, b"x", [b"xyz"], b"", rb"x"),
    "o-bnd":     (rb"xy+(?=z)", LOW, b"x", [b"xyz"], b"", rb"x"),
    "o-hat":     (rb"\bx[a-z]+\b", NONWORD, b"x", [b" xab ", b" xyz "], b"", rb"x"),
    "o-hyb":     (rb"xy+z", LOW, b"x", [b"xyz"], b"", rb"x"),
    "o-back":    (rb"(?m)^xy+z", LOW, b"\n", [b"\nxyz"], b"", rb"\n"),
    # item 8: grid1's dig / word-eq with their REQ byte present (the pre-check exists)
    "trig-dig":  (rb"[0-9]+x", grid.CELLS["dig"][1], b"0123456789", [], b"x", rb"[0-9]"),
    "trig-word": (rb"[A-Za-z_]+=", PUNCT, b"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_", [], b"=", rb"[A-Za-z_]"),
}
grid.CELLS.update(CELLS2)       # fork()ed workers inherit the extended table

# EMIT: how build.sh/ext builds emit each cell's artifacts (see build.sh, ext_*/build.sh)
GAPS = [2, 8, 32, 256, 4096, INF]          # item 3 gaps (INF = 0 = absent)
OB_LENS = [8, 32, 64, 1 << 20]             # item 3 member-free lengths
OB_N = 65536                               # item 3/4 find-all buffer size
OB_L = 65536                               # one planted match per buffer: a find-all pass is two calls

PICK_ALL = ["walk", "V1", "S1", "A1", "A3"]
PICK_FIRST = ["walk", "V1", "S1", "A1"]
TW = ["tw0", "tw1", "tw2"]
K_ARMS = ["walk", "V1", "A1"]

# item 2 selection (tables, not branches)
DENSE20 = ([("dig", g, L) for g in (2, 8, 32) for L in (32, 1024, 65536)] +
           [("dfa-hat", g, L) for g in (2, 8, 32) for L in (1024, 65536)] +
           [("bounded", 2, 8), ("bounded", 2, 1024), ("bounded", 8, 32), ("bounded", 32, 8), ("bounded", 32, 1024)])
EXTRA_POINTS = [8, 32]                     # new member-free dig points (M12's N = 8, 32)
SC0_CELLS = ("f3-hex-run", "f3-word-eq", "f3-wcls")

# the DRY subset (2-3 groups per item): substrings of the grid2 subject names
DRY_ITEM1 = [("dig", "g2-dig-n64k-g8-L1k-u-S", "all"), ("dfa-hat", "g2-dfa-hat-n64k-g8-L1k-u-S", "all"),
             ("dig", "g2-dig-n64k-g8-L32-u-S", "first"), ("f3-dig", "g2-f3-dig-n64k-ginf-Lnone-S", "first"),
             ("f3-hex-run", "g2-f3-hex-run-n64k-ginf-Lnone-S", "first")]
DRY_OB = [("o-fwd", 8), ("o-hat", 8), ("o-back", 8)]
DRY_OBLEN = [("o-fwd", 64)]
DRY_TRIG = [("trig-dig", "early", 8), ("trig-dig", "late", 8), ("trig-dig", "absent", 8)]

# ---- subject naming
def sname2(fam, n, g, L, shape, reuse="S"):
    return "g2-" + grid.sname(fam, n, g, L, shape, reuse)[3:]

def tag(v):
    return "inf" if v == 0 else (f"{v >> 20}m" if v >= 1 << 20 and v % (1 << 20) == 0 else
                                 f"{v >> 10}k" if v >= 1024 and v % 1024 == 0 else str(v))

def trig_name(cell, pos, g, n=OB_N):
    return f"g2-{cell}-n{tag(n)}-g{tag(g)}-{pos}-S"

def ob_name(cell, n, g, L):
    return f"ob_{cell}-n{tag(n)}-g{tag(g)}-L{'none' if L == 0 else tag(L)}-S"

# ---- the design
class Group:
    def __init__(self, item, cell, subj, mode, arms, off=None, spec=None, g1=None):
        self.item, self.cell, self.subj, self.mode, self.arms = item, cell, subj, mode, list(arms)
        self.off, self.spec, self.g1 = off, spec, g1 or []
    @property
    def tok(self):
        return self.subj + ("" if self.off is None else f"@{self.off}")

def build(dry):
    """-> (groups list, subjects dict name -> spec)"""
    groups, subjects, byk = [], {}, {}
    def add(g):
        k = (g.cell, g.tok, g.mode)
        if k in byk:                       # the same streamed group from two grid1 groups
            h = byk[k]
            h.g1 += g.g1
            for a in g.arms:
                if a not in h.arms: h.arms.append(a)
            return h
        byk[k] = g; groups.append(g)
        subjects[g.subj] = g.spec
        return g
    # item 1 (+ the item-2 twin arms that ride its groups)
    dense = {(c, sname2(c, 65536, g, L, "u" if g != 2 else "reg")) for c, g, L in DENSE20}
    for block, cell, arms, mode, subs, offs in grid.blocks():
        for s in subs:
            fam, n, g, L, shape, reuse = s
            spec = (fam, n, g, L, shape, "S")
            for o in offs:
                nm = sname2(*spec)
                pick = PICK_ALL if mode == "all" else PICK_FIRST
                if cell.startswith("f3-") or cell in ("dig", "dfa-hat", "bounded"):
                    pass
                a = list(pick)
                if cell.startswith("f3-") and mode == "first":
                    a = list(PICK_FIRST)
                gr = Group(1, cell, nm, mode, a, o, spec, [(block, cell, grid.sname(*s) + ("" if o is None else f"@{o}"), mode)])
                add(gr)
    # item 2 riders
    for g in groups:
        base_cell = g.cell[3:] if g.cell.startswith("f3-") else g.cell
        fam, n, gg, L, shape, _ = g.spec
        memfree = gg == 0 and L == 0
        if (base_cell, g.subj) in dense and g.mode == "all":
            g.arms += TW; g.item = 12
        elif memfree and g.mode == "first" and g.off is None and (g.cell.startswith("f3-") or (g.cell == "dig" and n in (48, 63, 64, 65, 128))):
            g.arms += TW; g.item = 12
        if g.cell in SC0_CELLS and memfree:
            g.arms += ["sc0"]; g.item = 12
    # item 2 new groups: dig member-free n = 8, 32 (first); f3-wcls 64 KiB / 1 MiB (R0's \w cell)
    for n in EXTRA_POINTS:
        spec = ("dig", n, INF, 0, "u", "S")
        add(Group(2, "dig", sname2(*spec), "first", PICK_FIRST + TW, None, spec))
    for n in (65536, 1 << 20):
        spec = ("f3-wcls", n, INF, 0, "u", "S")
        add(Group(2, "f3-wcls", sname2(*spec), "first", PICK_FIRST + ["sc0"], None, spec))
    # item 3/4 (ext set "ob"): own subjects ob_*
    ob, trig = [], []
    for cell in ("o-fwd", "o-bnd", "o-hat", "o-hyb", "o-back"):
        back = cell == "o-back"
        for g in GAPS:
            spec = (cell, OB_N, g, OB_L, "u", "S")
            arms = ["walk", "libc", "none"] if back else ["walk", "libc", "v1", "loop", "none"]
            ob.append(Group(34, cell, ob_name(cell, OB_N, g, OB_L), "all", arms, None, spec))
        for n in OB_LENS:
            spec = (cell, n, INF, 0, "u", "S")
            arms = ["walk", "libc"] if back else ["walk", "libc", "v1", "loop"]
            ob.append(Group(3, cell, ob_name(cell, n, INF, 0), "first", arms, None, spec))
    # item 8 (ext set "trig")
    for cell in ("trig-dig", "trig-word"):
        for pos in ("early", "late", "absent"):
            for g in (8, 32):
                spec = (cell, OB_N, g, 0, pos, "S")
                trig.append(Group(8, cell, trig_name(cell, pos, g), "first", ["keep", "drop"], None, spec))
    if dry:
        keep = set()
        sel = []
        for c, s, m in DRY_ITEM1:
            sel += [g for g in groups if g.cell == c and g.subj == s and g.mode == m and g.off is None]
        for g in groups:
            if g.item == 2 and g.cell in ("f3-wcls",) and g.spec[1] == 65536: sel.append(g)
            if g.item == 2 and g.cell == "dig" and g.spec[1] == 8: sel.append(g)
        groups = sel
        ob = [g for g in ob if (g.item == 34 and (g.cell, g.spec[2]) in DRY_OB) or (g.item == 3 and (g.cell, g.spec[1]) in DRY_OBLEN)]
        trig = [g for g in trig if (g.cell, g.spec[4], g.spec[2]) in DRY_TRIG]
        subjects = {g.subj: g.spec for g in groups}
    for g in ob + trig:
        subjects[g.subj] = g.spec
    return groups, ob, trig, subjects

def f2_rows(groups, dry):
    """items 6 and 7: arms_f2.tsv rows (cell, arm, role, subjects, modes)"""
    rows = []
    for g in groups:
        if g.item in (1, 12) and g.cell != "f3-wcls":
            rows.append((g.cell, g.mode, g.tok, [a for a in K_ARMS if a in g.arms]))
    real = [] if dry else [(c, s) for c in ("hex-run", "bounded", "dfa-hat") for s in ("prose", "docs", "code")]
    if dry: real = [("hex-run", "prose")]
    for c, s in real:
        rows.append((c, "all", f"g2-real-{s}-S", grid.F4))
    return rows

def write_tables(out, dry):
    groups, ob, trig, subjects = build(dry)
    def rows_of(gs):
        order, per = [], {}
        for g in gs:
            for a in g.arms:
                k = (g.cell, a)
                if k not in per: per[k] = []; order.append(k)
                per[k].append(g)
        return order, per
    def write_arms(path, gs, base_of, title):
        order, per = rows_of(gs)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(f"# {title}. cell\tarm\trole\tsubjects\tmodes -- grid1/README.md\n")
            for cell, a in order:
                for mode in ("first", "all"):
                    toks = [g.tok for g in per[(cell, a)] if g.mode == mode]
                    if toks:
                        f.write(f"{cell}\t{a}\t{'base' if a == base_of(cell) else 'arm'}\t{','.join(dict.fromkeys(toks))}\t{mode}\n")
    write_arms(os.path.join(out, "arms.tsv"), groups, lambda c: "walk", "grid2 own arms (items 1, 2)")
    write_arms(os.path.join(out, "ext", "ob", "arms.tsv"), ob, lambda c: "walk", "grid2 ext ob (items 3, 4)")
    write_arms(os.path.join(out, "ext", "trig", "arms.tsv"), trig, lambda c: "keep", "grid2 ext trig (item 8)")
    with open(os.path.join(out, "arms_f2.tsv"), "w") as f:
        f.write("# grid2 F2 rows (items 6, 7; perf; never timed by time.sh). Same columns.\n")
        for cell, mode, tok, arms in f2_rows(groups, dry):
            for a in arms:
                f.write(f"{cell}\t{a}\t{'base' if a == 'walk' else 'arm'}\t{tok}\t{mode}\n")
    with open(os.path.join(out, "subjects.tsv"), "w") as f:
        f.write("name\tfamily\tn\tg\tL\tshape\treuse\tnbuf\n")
        for nm, s in sorted(subjects.items()):
            f.write(f"{nm}\t{s[0]}\t{s[1]}\t{s[2]}\t{s[3]}\t{s[4]}\t{s[5]}\t{sg.nbuf_for(s[1])}\n")
    with open(os.path.join(out, "groups2.tsv"), "w") as f:
        f.write("item\tcell\tsubject\tmode\tarms\n")
        for g in groups + ob + trig:
            f.write(f"{g.item}\t{g.cell}\t{g.tok}\t{g.mode}\t{','.join(g.arms)}\n")
    with open(os.path.join(out, "fit_map.tsv"), "w") as f:
        f.write("grid1_block\tgrid1_cell\tgrid1_subject\tmode\tgrid2_cell\tgrid2_subject\n")
        for g in groups:
            for blk, c, s1, m in g.g1:
                f.write(f"{blk}\t{c}\t{s1}\t{m}\t{g.cell}\t{g.tok}\n")
    print(f"design: {len(groups)} own groups, {len(ob)} ob groups, {len(trig)} trig groups, {len(subjects)} subjects" + (" (DRY)" if dry else ""))

def count(out, dry):
    groups, ob, trig, subjects = build(dry)
    def line(name, gs, extra_copies=2):
        launches = sum(len(g.arms) + extra_copies for g in gs)       # per round: arms + walk#b + walk#c
        print(f"{name:34} groups={len(gs):4} launches/round={launches:5}")
        return launches
    it1 = [g for g in groups if g.item in (1, 12)]
    print(f"item 1 fit groups (grid1 149 -> {len({tuple(x[1:4]) for g in groups for x in g.g1})} distinct grid1 groups, {len(it1)} grid2 groups)")
    t = 0
    base_arms = lambda g: [a for a in g.arms if not a.startswith(("tw", "sc"))]
    l1 = sum(len(base_arms(g)) + 2 for g in groups)
    l2 = sum(len(g.arms) - len(base_arms(g)) for g in groups)
    print(f"{'item 1 (pickable arms + #b #c)':34} groups={len(groups):4} launches/round={l1:5}")
    print(f"{'item 2 (twin/scaffold arms)':34} groups={sum(1 for g in groups if len(g.arms) != len(base_arms(g))):4} launches/round={l2:5}")
    l3 = sum(len([a for a in g.arms if a != 'none']) + 2 for g in ob)
    l4 = sum(1 for g in ob if 'none' in g.arms)
    print(f"{'item 3 (one-byte arms + #b #c)':34} groups={len(ob):4} launches/round={l3:5}")
    print(f"{'item 4 (none arms)':34} groups={l4:4} launches/round={l4:5}")
    l8 = sum(len(g.arms) + 2 for g in trig)
    print(f"{'item 8 (trigger probe, optional)':34} groups={len(trig):4} launches/round={l8:5}")

# ---- generation
def gen_trig(cell, n, g, pos, seed):
    """trig cells: landings at mean gap g, ONE match token (early / late) or none (absent)"""
    buf, _, nland = grid.gen_buffer(cell, n, g, 0, "u", seed)
    s = bytearray(buf)
    tok = {"trig-dig": b"7x", "trig-word": b"a="}[cell]
    if pos == "early": s[64:64 + len(tok)] = tok
    elif pos == "late": s[n - 64:n - 64 + len(tok)] = tok
    return bytes(s), (0 if pos == "absent" else 1), nland

def gen_one(a):
    out, name, fam, n, g, L, shape, reuse, nbuf = a
    path = os.path.join(out, "subj", name)
    tm = tl = 0
    def mk(seed):
        nonlocal tm, tl
        if fam.startswith("trig-"): b, m, l = gen_trig(fam, n, g, shape, seed)
        else: b, m, l = grid.gen_buffer(fam, n, g, L, shape if not fam.startswith(("o-",)) or shape in ("reg", "u", "burst") else "u", seed)
        # the planted-count self-check against python re (the generator's, as grid1's): the planted
        # matches are what the pattern finds, and a no-member subject holds no member byte
        cell = fam[3:] if fam.startswith("f3-") else fam
        k, _ = grid.oracle_of(cell, b, "all")
        if k != m: raise SystemExit(f"GEN SELF-CHECK FAILED {name}: planted {m} matches, python re finds {k}")
        if m == 0 and l == 0 and not fam.startswith("trig-"):
            if re.search(grid.CELLS[cell][5], b): raise SystemExit(f"GEN SELF-CHECK FAILED {name}: a no-member subject holds a member byte")
        tm += m; tl += l
        return (b,)
    sg.synthetic_stream(path, lambda seed: mk(seed), name, nbuf)
    return f"{name}\t{fam}\t{n}\t{g}\t{L}\t{shape}\t{reuse}\t{nbuf}\t{tm}\t{tl}"

def gen_real(out):
    """item 7's streamed real-text subjects: 16 x 64 KiB windows of each spike1 1 MiB file"""
    for s in ("prose", "docs", "code"):
        src = os.path.join(SPIKE_SUBJ, f"{s}1m")
        dst = os.path.join(out, "subj", f"g2-real-{s}-S")
        if not os.path.exists(src): print(f"gen: no {src}; item 7 subject {s} skipped"); continue
        if not (os.path.isdir(dst) and os.path.exists(os.path.join(dst, sg.MANIFEST))):
            sg.window_stream(dst, src, 65536, 16, f"g2-real-{s}")

def gen(out, jobs):
    os.makedirs(os.path.join(out, "subj"), exist_ok=True)
    rows = [l.rstrip("\n").split("\t") for l in open(os.path.join(out, "subjects.tsv")).readlines()[1:]]
    args = [(out, r[0], r[1], int(r[2]), int(r[3]), int(r[4]), r[5], r[6], int(r[7])) for r in rows]
    with ProcessPoolExecutor(jobs) as ex:
        facts = list(ex.map(gen_one, args))
    gen_real(out)
    with open(os.path.join(out, "subj_facts.tsv"), "w") as f:
        f.write("name\tfamily\tn\tg\tL\tshape\treuse\tnbuf\tplanted_matches\tplanted_landings\n")
        f.write("\n".join(facts) + "\n")
    print(f"gen: {len(facts)} subjects")

# ---- the oracle: libpcre2 through tests/oracle/'s local adapter
_AD = None
def adapter():
    global _AD
    if _AD is None:
        root = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
        sys.path.insert(0, os.path.join(root, "tests", "oracle"))
        os.chdir(root) if False else None
        import local_adapter
        _AD = local_adapter.LocalAdapter()
    return _AD

def oracle_version():
    return adapter().oracle_id().version

def pc_of(cell, buf, mode, rx):
    n = len(buf)
    if mode == "first":
        r = rx.search(buf, 0)
        if r is None: return 1, 7
        (s, e), _ = r
        return 1, (s * 31 + e) & grid.MASK
    h = k = p = 0
    while p <= n:
        r = rx.search(buf, p)
        if r is None: break
        (s, e), _ = r
        k += 1; h = (h * 131 + s * 31 + e) & grid.MASK
        if e == s and e >= n: break
        p = e if e > s else e + 1
    return k, h

def oracle_job(a):
    out, cell, s, m = a
    cellp = cell[3:] if cell.startswith("f3-") else cell
    pat = grid.CELLS[cellp][0]
    rx = adapter()._br.pcre2.compile(pat)
    path = os.path.join(out, "subj", s)
    bufs = [open(os.path.join(path, f), "rb").read() for f in sorted(os.listdir(path)) if not f.startswith(".")] \
        if os.path.isdir(path) else [open(path, "rb").read()]
    M = H = 0
    for b in bufs:
        k, h = pc_of(cell, b, m, rx)
        M += k; H = (H * 1099511628211 + h) & grid.MASK
    return f"{cell}\t{s}\t{m}\tmatches={M} hash={H:x}"

def oracles(out, jobs):
    import subprocess
    ver = oracle_version()
    want = os.environ.get("ORACLE_VERSION", "10.46")
    if ver != want:
        raise SystemExit(f"ORACLE: libpcre2 {ver}, want {want} (set ORACLE_VERSION to accept another)")
    keys = set()
    for line in subprocess.run([sys.executable, "-I", os.path.join(G1, "arms.py"), out, "items", "all"],
                               capture_output=True, text=True, check=True).stdout.splitlines():
        c, a, r, s, m = line.split("\t")
        cp = c[3:] if c.startswith("f3-") else c
        if cp in grid.CELLS and not s.startswith("g2-real-"): keys.add((c, s.split("@")[0], m))
    with ProcessPoolExecutor(jobs) as ex:
        res = list(ex.map(oracle_job, [(out, c, s, m) for c, s, m in sorted(keys)]))
    with open(os.path.join(out, "oracle.tsv"), "w") as f:
        f.write("\n".join(res) + "\n")
    print(f"oracles: {len(res)} (cell, subject, mode) lines from libpcre2 {ver}")

if __name__ == "__main__":
    cmd, out = sys.argv[1], sys.argv[2]
    dry = "--dry" in sys.argv
    jobs = int(sys.argv[sys.argv.index("-j") + 1]) if "-j" in sys.argv else 4
    if cmd == "design": write_tables(out, dry)
    elif cmd == "gen": gen(out, jobs)
    elif cmd == "oracles": oracles(out, jobs)
    elif cmd == "count": count(out, dry)
    else: raise SystemExit(__doc__)
