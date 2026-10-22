#!/usr/bin/env python3
# docs/design/kit_proof/measure/gen_subjects.py — [KIT-VERIFY] `measure`: the subjects and
# their EXPECTED answers.
#
# usage: python3 -I gen_subjects.py CELLS.TSV OUTDIR
#
# For each cell (cells.tsv: id TAB pattern) and each class it writes, deterministically
# (random.Random seeded from the cell id and class; no clock, no file read):
#   <cell>.<class>.raw     ~1 MiB of text, the `throughput` subject
#   <cell>.<class>.srec    1024 short records (u32 LE length + bytes), the `search_short` subject
#   <cell>.<class>.mrec    1024 short records, the `match` subject
#   <cell>.<class>.<regime>.expect   "ops N hits H hash X" computed by python `re` alone
# and subjects.tsv (cell, class, bytes, throughput matches, srec hits, mrec hits).
#
# CLASSES (stated, per cell):
#   real   lowercase prose (or the cell's natural text: a path listing, log lines) with the
#          match planted at a natural, SPARSE rate, plus near-misses that must not match
#   none   the same filler and near-misses, no match anywhere (asserted)
#   dense  matches packed back to back with one or two filler bytes between
# Short records: lengths 32..160 cut from the class's raw text. In `real`, a quarter of the
# records are cut to CONTAIN a match (search_short) or to START at one (match); `dense` records
# all contain / start at one; `none` records contain none.
#
# The expected answers use python's `re` on bytes with the same find-all loop as
# match_api.md section 3.1.3 (search from p, next p = end for a non-empty match), so they
# share no source with pcrec. Every pattern here matches only non-empty spans (asserted).
import os
import random
import re
import sys

FNV = 1099511628211
MASK = (1 << 64) - 1
BASIS = 14695981039346656037
RAW_BYTES = 1 << 20
NREC = 1024

WORDS = """the of and to in is that it was for on are with as his they at be this from have or by one
had not but what all were when we there can an your which their said if do will each about how up out
them then she many some so these would other into has more her two like him see time could no make than
first been its who now people my made over did down only way find use may water long little very after
words called just where most know get through back much before go good new write our used me man too any
day same right look think also around another came come work three word must because does part even
place well such here take why help put different away again off went old number great tell men say small
every found still between name should home big give air line set own under read last never us left end
along while might next sound below saw something thought both few those always show large often together
asked house don world going want school important until form food keep children feet land side without
boy once animal life enough took sometimes four head above kind began almost live page got earth need far
hand high year mother light country father let night picture being study second soon story since white
ever paper hard near sentence better best across during today however sure knew try told young sun thing
whole hear example heard several change answer room sea against top turned learn point city play toward
five himself usually money seen didn morning body upon family later turn move face door cut done""".split()
WORDS = [w for w in WORDS if w != "done"]   # `done` is the done-eol cell's own token


def seed_of(cell, cls):
    return random.Random("%s/%s" % (cell, cls)).getrandbits(64)


def prose(rng, n, near, near_p, plant, plant_p, newline_every=72):
    out = []
    size = 0
    col = 0
    while size < n:
        r = rng.random()
        if plant is not None and r < plant_p:
            w = plant(rng)
        elif near and r < plant_p + near_p:
            w = rng.choice(near)
        else:
            w = rng.choice(WORDS)
        out.append(w)
        size += len(w) + 1
        col += len(w) + 1
        if col >= newline_every:
            out.append("\n")
            col = 0
        else:
            out.append(" ")
    return "".join(out).encode("ascii")[:n]


def hexs(rng, k):
    return "".join(rng.choice("0123456789abcdef") for _ in range(k))


def digits(rng, k):
    return "".join(rng.choice("0123456789") for _ in range(k))


def dense_join(rng, n, token, seps):
    out = []
    size = 0
    while size < n:
        t = token(rng)
        out.append(t)
        s = rng.choice(seps)
        out.append(s)
        size += len(t) + len(s)
    return "".join(out).encode("ascii")[:n]


def lines_text(rng, n, line):
    out = []
    size = 0
    while size < n:
        l = line(rng) + "\n"
        out.append(l)
        size += len(l)
    return "".join(out).encode("ascii")[:n]


# ---- per-cell generators: gen(cls, rng) -> bytes ------------------------------------------

def g_lit(cls, rng):
    near = ["abcdefg", "abcdefgx", "bcdefgh", "abcdefg h", "xabcdefg"]
    if cls == "dense":
        return dense_join(rng, RAW_BYTES, lambda r: "abcdefgh", [" ", "\n", "x ", "-"])
    return prose(rng, RAW_BYTES, near, 1 / 150, (lambda r: "abcdefgh") if cls == "real" else None,
                 1 / 700)


def g_year(cls, rng):
    if cls == "dense":
        return dense_join(rng, RAW_BYTES, lambda r: digits(r, r.randint(5, 9)), [" ", " ", "\n"])
    return _year_prose(rng, cls == "real")


def _year_prose(rng, real):
    out = []
    size = 0
    col = 0
    while size < RAW_BYTES:
        r = rng.random()
        if r < 0.10:
            w = digits(rng, rng.randint(1, 3))
        elif real and r < 0.14:
            w = digits(rng, rng.choice([4, 4, 4, 5, 6]))
        else:
            w = rng.choice(WORDS)
        out.append(w)
        size += len(w) + 1
        col += len(w) + 1
        if col >= 72:
            out.append("\n")
            col = 0
        else:
            out.append(" ")
    return "".join(out).encode("ascii")[:RAW_BYTES]


def g_ext(cls, rng):
    dirs = WORDS[:60]
    names = WORDS[60:120] + ["guitar", "star", "target", "tarpit"]
    exts = [".txt", ".c", ".h", ".py", ".gz", ".zip", ".tgz", ".ta", ".tr", ".tag", ".rar", ".md",
            ".gzip", ".tx"]
    def path(r, ext):
        return "/" + "/".join(r.choice(dirs) for _ in range(r.randint(2, 3))) + "/" + \
               r.choice(names) + ext
    if cls == "dense":
        return lines_text(rng, RAW_BYTES,
                          lambda r: path(r, r.choice([".tar.gz", ".tar.gz", ".tar"])))
    def line(r):
        if cls == "real" and r.random() < 1 / 25:
            return path(r, r.choice([".tar", ".tar.gz"]))
        return path(r, r.choice(exts))
    return lines_text(rng, RAW_BYTES, line)


def g_hex(cls, rng):
    if cls == "dense":
        return dense_join(rng, RAW_BYTES, lambda r: hexs(r, 8), [" ", " ", "\n"])
    def near(r):
        k = r.randint(0, 3)
        if k == 0:
            return hexs(r, r.randint(5, 7))
        if k == 1:
            return hexs(r, r.randint(9, 12))
        if k == 2:
            return "0x" + hexs(r, 8)
        return hexs(r, 8) + "g"
    out = []
    size = 0
    col = 0
    while size < RAW_BYTES:
        r = rng.random()
        if cls == "real" and r < 1 / 40:
            w = hexs(rng, 8)
        elif r < 1 / 40 + 1 / 20:
            w = near(rng)
        else:
            w = rng.choice(WORDS)
        out.append(w)
        size += len(w) + 1
        col += len(w) + 1
        if col >= 72:
            out.append("\n")
            col = 0
        else:
            out.append(" ")
    return "".join(out).encode("ascii")[:RAW_BYTES]


def g_foobar(cls, rng):
    near = ["fooba", "oobar", "foobaz", "foo bar", "fobar", "foobbar", "foo"]
    if cls == "dense":
        return dense_join(rng, RAW_BYTES, lambda r: "foobar", [" ", "\n", "x ", "-"])
    return prose(rng, RAW_BYTES, near, 1 / 100, (lambda r: "foobar") if cls == "real" else None,
                 1 / 700)


def g_cat(cls, rng):
    near = ["cats", "concat", "catalog", "bobcat", "scatter", "category", "cat_", "_cat", "cat1",
            "Cat", "ca t"]
    plants = ["cat", "cat", "cat", "cat,", "cat.", "(cat)"]
    if cls == "dense":
        return dense_join(rng, RAW_BYTES, lambda r: r.choice(plants), [" ", " ", "\n"])
    return prose(rng, RAW_BYTES, near, 1 / 30, (lambda r: r.choice(plants)) if cls == "real" else None,
                 1 / 60)


def g_done(cls, rng):
    stat = ["running", "pending", "failed", "donezo", "doner", "dones", "queued", "skipped"]
    def line(r):
        w = r.choice(WORDS)
        if cls == "dense":
            return "step %s done" % w[:3] if r.random() < 0.9 else "step %s" % w
        if cls == "real" and r.random() < 1 / 12:
            return "task %s done" % w
        if r.random() < 0.15:
            return "task %s done deal" % w
        return "task %s %s" % (w, r.choice(stat))
    return lines_text(rng, RAW_BYTES, line)


def g_wd(cls, rng):
    if cls == "dense":
        return dense_join(rng, RAW_BYTES,
                          lambda r: "".join(r.choice("abcdefghijklmnopqrstuvwxyz") + r.choice("0123456789")
                                            for _ in range(r.randint(1, 4))), [" ", " ", "\n"])
    near = ["snake_case", "_x", "x_", "a-b", "(x)", "[y]", "z."]
    def plant(r):
        return r.choice(WORDS)[:r.randint(1, 5)] + digits(r, r.randint(1, 3))
    return prose(rng, RAW_BYTES, near, 1 / 20, plant if cls == "real" else None, 1 / 25)


GEN = {"lit-l8": g_lit, "year4": g_year, "file-ext-order": g_ext, "hex8-bounded": g_hex,
       "foobar": g_foobar, "cat-bounded": g_cat, "done-eol": g_done, "word-digit": g_wd}


# ---- the expected answers ------------------------------------------------------------------

def mix(h, v):
    return ((h ^ (v & MASK)) * FNV) & MASK


def expect_throughput(rx, buf):
    h, k, p, n = BASIS, 0, 0, len(buf)
    while p <= n:
        m = rx.search(buf, p)
        if m is None:
            break
        a, b = m.span()
        assert b > a, "empty match: the loop below would need the NOTEMPTY retry"
        k += 1
        h = mix(mix(h, a), b)
        p = b
    return 1, k, h


def expect_search_short(rx, recs):
    h, k = BASIS, 0
    for r in recs:
        m = rx.search(r)
        if m:
            k += 1
            h = mix(mix(h, m.start()), m.end())
        else:
            h = mix(h, MASK)
    return len(recs), k, h


def expect_match(rx, recs):
    h, k = BASIS, 0
    for r in recs:
        m = rx.match(r)
        if m:
            k += 1
            h = mix(h, m.end())
        else:
            h = mix(h, MASK)
    return len(recs), k, h


def make_records(rng, rx, buf, cls, contain):
    starts = [m.start() for m in rx.finditer(buf)]
    recs = []
    for _ in range(NREC):
        ln = rng.randint(32, 160)
        want = starts and ((cls == "dense") or (cls == "real" and rng.random() < 0.25))
        if want:
            s = rng.choice(starts)
            if contain:
                off = rng.randint(0, 20)   # the match sits a few bytes in
                off = min(off, s)
                a = s - off
            else:
                a = s                       # the record starts AT the match
        else:
            a = rng.randint(0, len(buf) - ln)
            while cls == "none" and rx.search(buf[a:a + ln]):   # a cut can CREATE a match
                a = rng.randint(0, len(buf) - ln)
        recs.append(buf[a:a + ln])
    return recs


def pack(recs):
    return b"".join(len(r).to_bytes(4, "little") + r for r in recs)


def main():
    cells, outdir = sys.argv[1], sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    rows = []
    for line in open(cells):
        line = line.rstrip("\n")
        if not line or line.startswith("#"):
            continue
        cell, pat = line.split("\t")
        rx = re.compile(pat.encode("ascii"))
        for cls in ("real", "none", "dense"):
            rng = random.Random(seed_of(cell, cls))
            buf = GEN[cell](cls, rng)
            assert len(buf) == RAW_BYTES, (cell, cls, len(buf))
            nm = sum(1 for _ in rx.finditer(buf))
            if cls == "none":
                assert nm == 0, "%s/none contains %d matches" % (cell, nm)
            elif cls == "real":
                assert 20 <= nm <= 20000, "%s/real has %d matches (want a sparse, non-empty rate)" % (cell, nm)
            else:
                assert nm >= 20000, "%s/dense has only %d matches" % (cell, nm)
            srec = make_records(rng, rx, buf, cls, True)
            mrec = make_records(rng, rx, buf, cls, False)
            base = os.path.join(outdir, "%s.%s" % (cell, cls))
            open(base + ".raw", "wb").write(buf)
            open(base + ".srec", "wb").write(pack(srec))
            open(base + ".mrec", "wb").write(pack(mrec))
            e_t = expect_throughput(rx, buf)
            e_s = expect_search_short(rx, srec)
            e_m = expect_match(rx, mrec)
            for reg, e in (("throughput", e_t), ("search_short", e_s), ("match", e_m)):
                open("%s.%s.expect" % (base, reg), "w").write("ops %d hits %d hash %016x\n" % e)
            rows.append((cell, cls, len(buf), e_t[1], e_s[1], e_m[1]))
    with open(os.path.join(outdir, "subjects.tsv"), "w") as f:
        f.write("cell\tclass\tbytes\tthroughput_matches\tsearch_short_hits\tmatch_hits\n")
        for r in rows:
            f.write("%s\t%s\t%d\t%d\t%d\t%d\n" % r)
    print("gen_subjects: %d cells x 3 classes, %d subject sets" % (len(rows) // 3, len(rows)))


if __name__ == "__main__":
    main()
