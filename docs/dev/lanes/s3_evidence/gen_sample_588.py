#!/usr/bin/env python3
# docs/dev/lanes/s3_evidence/gen_sample_588.py — job 588's MOVER SAMPLE subjects (lane s3, the S3
# review's item E): the subjects and expected answers for the sample_588.tsv patterns, in the 650
# harness's file formats (docs/design/kit_proof/measure/gen_subjects.py, whose filler, record cutter
# and expected-answer loops it imports, so both share one implementation of the answers).
#
# usage: python3 -I gen_sample_588.py SAMPLE.TSV OUTDIR
#
# For each sample row (id, pattern) and class, deterministically (random.Random seeded from the id
# and class; no clock):
#   <id>.<class>.raw / .srec / .<regime>.expect    regimes throughput and search_short
# and classes.tsv: id, class, and either the subject's match counts or `skip WHY`.
#
# CLASSES (stated for every pattern; the 650 harness's per-cell texts do not exist for these):
#   real    gen_subjects' English prose with a GENERATED match of the pattern planted as a word
#           at 1/200 (`match_of`, below; each plant verified by python `re` in the class's count)
#   none    the same prose, no plant; SKIPPED where the prose itself matches (the class would not
#           be a no-match class)
#   random  uniform bytes over printable ASCII and '\n' (always generatable; its matches counted)
# The expected answers are python `re` on bytes alone (no pcrec source).
import importlib.util
import os
import random
import re
import re._constants as C
import re._parser as P
import sys

here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "gs", os.path.join(here, "../../../design/kit_proof/measure/gen_subjects.py"))
gs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gs)

CLASSES = ("real", "none", "random")
ALPHA = [c for c in range(0x20, 0x7F)] + [0x0A]
CATS = {
    C.CATEGORY_DIGIT: lambda c: 48 <= c <= 57,
    C.CATEGORY_NOT_DIGIT: lambda c: not 48 <= c <= 57,
    C.CATEGORY_SPACE: lambda c: c in b" \t\n\r\f\v",
    C.CATEGORY_NOT_SPACE: lambda c: c not in b" \t\n\r\f\v",
    C.CATEGORY_WORD: lambda c: chr(c).isalnum() or c == 95,
    C.CATEGORY_NOT_WORD: lambda c: not (chr(c).isalnum() or c == 95),
}


def _members(items):
    """The ASCII bytes an IN class admits (ALPHA only: the filler's alphabet)."""
    neg = any(op is C.NEGATE for op, _ in items)
    def has(c):
        for op, av in items:
            if op is C.LITERAL and av == c:
                return True
            if op is C.RANGE and av[0] <= c <= av[1]:
                return True
            if op is C.CATEGORY and CATS.get(av, lambda _c: False)(c):
                return True
        return False
    return [c for c in ALPHA if has(c) != neg]


def _gen(seq, rng, out):
    """One random string of the parsed sequence `seq` into `out`; False where unsupported."""
    for op, av in seq:
        if op is C.LITERAL:
            out.append(av)
        elif op is C.NOT_LITERAL:
            out.append(rng.choice([c for c in ALPHA if c != av]))
        elif op is C.ANY:
            out.append(rng.choice([c for c in ALPHA if c != 0x0A]))
        elif op is C.IN:
            m = _members(av)
            if not m:
                return False
            out.append(rng.choice(m))
        elif op in (C.MAX_REPEAT, C.MIN_REPEAT, C.POSSESSIVE_REPEAT):
            lo, hi, sub = av
            hi = min(hi, lo + 3)
            for _ in range(rng.randint(lo, hi)):
                if not _gen(sub, rng, out):
                    return False
        elif op is C.SUBPATTERN:
            if not _gen(av[-1], rng, out):
                return False
        elif op is C.ATOMIC_GROUP:
            if not _gen(av, rng, out):
                return False
        elif op is C.BRANCH:
            if not _gen(rng.choice(av[1]), rng, out):
                return False
        elif op in (C.AT, C.ASSERT, C.ASSERT_NOT):
            continue                        # zero-width: the plant's verification decides
        else:
            return False                    # a back-reference, a conditional: not generated
    return True


def match_of(pat, rx, rng, tries=60):
    """A string python `re` finds as a match of `pat` when planted as a word (spaces around it),
    or None. Generated from re's own parse of the pattern, then VERIFIED by `rx`."""
    try:
        tree = P.parse(pat.decode("ascii"), 0)
    except Exception:
        return None
    for _ in range(tries):
        out = []
        if _gen(list(tree), rng, out) and out:
            cand = bytes(out)
            m = rx.search(b" " + cand + b" ")
            if m and m.end() > m.start():
                return cand
    return None


def compiles(pat):
    """The bytes regex python `re` reads `pat` as, or None (not ASCII, unparsed, or a construct
    whose meaning differs from PCRE's: `\\Z`, `\\z`)."""
    if not pat.isascii() or b"\\Z" in pat or b"\\z" in pat:
        return None
    try:
        return re.compile(pat)
    except Exception:
        return None


def subjects(sid, pat, outdir):
    """Writes the classes' subjects for one sample row; returns its classes.tsv rows."""
    rx = compiles(pat)
    rows = []
    for cls in CLASSES:
        rng = random.Random("s3-588/%s/%s" % (sid, cls))
        if rx is None:
            rows.append((sid, cls, "skip python re cannot read the pattern"))
            continue
        if cls == "real":
            pool = [match_of(pat, rx, rng) for _ in range(40)]
            pool = [p for p in pool if p]
            if not pool:
                rows.append((sid, cls, "skip no generated match"))
                continue
            buf = gs.prose(rng, gs.RAW_BYTES, None, 0, lambda r: r.choice(pool).decode("latin-1"), 1 / 200)
        elif cls == "none":
            buf = gs.prose(rng, gs.RAW_BYTES, None, 0, None, 0)
        else:
            buf = bytes(rng.choice(ALPHA) for _ in range(gs.RAW_BYTES))
        nm = sum(1 for _ in rx.finditer(buf))
        if cls == "none" and nm:
            rows.append((sid, cls, "skip the prose itself matches (%d)" % nm))
            continue
        if cls == "real" and not nm:
            rows.append((sid, cls, "skip no planted match survived"))
            continue
        srec = gs.make_records(rng, rx, buf, cls, True)
        base = os.path.join(outdir, "%s.%s" % (sid, cls))
        open(base + ".raw", "wb").write(buf)
        open(base + ".srec", "wb").write(gs.pack(srec))
        e_t = gs.expect_throughput(rx, buf)
        e_s = gs.expect_search_short(rx, srec)
        for reg, e in (("throughput", e_t), ("search_short", e_s)):
            open("%s.%s.expect" % (base, reg), "w").write("ops %d hits %d hash %016x\n" % e)
        rows.append((sid, cls, "ok matches %d srec_hits %d" % (e_t[1], e_s[1])))
    return rows


def read_sample(path):
    """sample_588.tsv's rows: (id, stratum, pattern bytes)."""
    sys.path.insert(0, os.path.join(here, "../../../../scripts"))
    import emit_sweep  # noqa: E402  (the --list-source escape vocabulary, one implementation)
    out = []
    for line in open(path, encoding="utf-8"):
        if line.startswith("#") or not line.strip():
            continue
        f = line.rstrip("\n").split("\t")
        out.append((f[0], f[1], bytes(emit_sweep.decode_escape(f[2]))))
    return out


def main():
    sample, outdir = sys.argv[1], sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    rows = []
    for sid, _stratum, pat in read_sample(sample):
        rows += subjects(sid, pat, outdir)
    with open(os.path.join(outdir, "classes.tsv"), "w") as f:
        for r in rows:
            f.write("\t".join(r) + "\n")
    ok = sum(1 for r in rows if r[2].startswith("ok"))
    print("gen_sample_588: %d patterns, %d of %d class subjects generated"
          % (len(rows) // len(CLASSES), ok, len(rows)))


if __name__ == "__main__":
    main()
