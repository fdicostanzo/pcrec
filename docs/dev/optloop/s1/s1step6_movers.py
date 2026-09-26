#!/usr/bin/env python3
"""[OPT-LITSCAN] S1 step 6 — the Q1 conversion's movers, BY ID, and its residue.

litscan_s1.md §7.2 step 6 converts the floating-run pre-check's scan loop
(K66's `emit_run_scan_loop`, both callers) into calls of file-scope blocks
emitted by the offset-skip block's own emitter. The predicted population is
exactly the artifacts that emit the RUN pre-check: BASE stamps
`RX_REQ_WHY "emitted"` and an `RX_REQ_RUN` other than "none". This emits every
artifact of reqpos_census.py's populations (bench caps/nocaps, each also under
`--engine=vm`; corpus auto, `--engine=vm` and `-e utf8`; all `--features all`)
from BASE and NEW and checks, per artifact:

  1. changed iff predicted (after the abi-digit normalization);
  2. every `#define` stamp line identical (the conversion moves no stamp);
  3. THE RESIDUE: with BASE's run scan loop(s) and their empty-window line
     removed, and NEW's `rx_reqrun*` block(s) and call line(s) removed, the
     two texts are byte-identical — so nothing but the pre-check moved;
  4. the predicted count of blocks: NEW has one `rx_reqrun*` block per BASE
     `size_t rp_pos` loop, with the same run literal and scan byte.

  BASE=<pcrec> NEW=<pcrec> SCR=<scratch> BENCH=<pcrec-bench root>
  CORPUS=<tree whose tests/ is the corpus> PCREC=<pcrec for --list-source>
  [ABI_FROM=36 ABI_TO=37] [LIST=<file: one changed id per line>]
  python3 s1step6_movers.py

Exit 0 iff every artifact passes all four.
"""
import os, sys, re, subprocess, collections
from concurrent.futures import ThreadPoolExecutor
sys.dont_write_bytecode = True
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(here, "..", "c2"))
from reqpos_census import bench_pop, corpus_pop  # noqa: E402
E = os.environ
ABI_FROM, ABI_TO = E.get("ABI_FROM"), E.get("ABI_TO")


def norm(text):
    if not ABI_FROM:
        return text
    text = re.sub(rb'(abi )%s\b' % ABI_FROM.encode(), rb'\g<1>' + ABI_TO.encode(), text)
    text = re.sub(rb'(\.abi *= *)%s\b' % ABI_FROM.encode(), rb'\g<1>' + ABI_TO.encode(), text)
    return text


def emit(binp, pat, extra, d):
    os.makedirs(d, exist_ok=True)
    out = os.path.join(d, "a.c")
    try:
        r = subprocess.run([binp, "-p", "rx", "--features", "all", "-o", out] + extra
                           + ["--pattern", pat], capture_output=True, timeout=180)
    except subprocess.TimeoutExpired:
        return b"TIMEOUT"
    return open(out, "rb").read() if r.returncode == 0 else None


def stamp(text, name):
    m = re.search(rb'^#define RX_%s "([^"]*)"$' % name, text, re.M)
    return m.group(1).decode() if m else None


LOOP_OPEN = re.compile(rb'^(\s*)\{\n\s*size_t rp_pos = ')
BASE_CMP = re.compile(rb'!memcmp\(subject \+ rp_c[^,]*, "((?:[^"\\]|\\.)*)", (\d+)\)\) break;')
BASE_MEMCHR = re.compile(rb'memchr\(subject \+ rp_pos, (\d+),')
NEW_CMP = re.compile(rb'if \(!memcmp\(subject \+ cand, "((?:[^"\\]|\\.)*)", (\d+)\)\) return cand;')
NEW_MEMCHR = re.compile(rb'memchr\(subject \+ pos(?: \+ \d+)?, (\d+),')


def strip_base(text):
    """BASE minus its run scan loops and the empty-window line before the first."""
    lines = text.split(b"\n")
    out, loops, i = [], [], 0
    while i < len(lines):
        ln = lines[i]
        if (re.match(rb'^\s*if \(subject_length <= search_from\) return 0;$', ln)
                and i + 2 < len(lines) and lines[i + 2].lstrip().startswith(b"size_t rp_pos")):
            i += 1
            continue
        m = re.match(rb'^(\s*)\{$', ln)
        if m and i + 1 < len(lines) and lines[i + 1].lstrip().startswith(b"size_t rp_pos"):
            ind = m.group(1)
            j = i + 1
            while lines[j] != ind + b"}":
                j += 1
            body = b"\n".join(lines[i:j + 1])
            loops.append((BASE_CMP.search(body).groups(), BASE_MEMCHR.search(body).group(1)))
            i = j + 1
            continue
        out.append(ln)
        i += 1
    return b"\n".join(out), loops


def strip_new(text):
    """NEW minus its rx_reqrun* blocks (and the blank line after) and calls."""
    lines = text.split(b"\n")
    out, blocks, i = [], [], 0
    while i < len(lines):
        ln = lines[i]
        if re.match(rb'^static inline size_t rx_reqrun(_whole)?\(', ln):
            j = i
            while lines[j] != b"}":
                j += 1
            body = b"\n".join(lines[i:j + 1])
            blocks.append((NEW_CMP.search(body).groups(), NEW_MEMCHR.search(body).group(1)))
            i = j + 1
            if i < len(lines) and lines[i] == b"":
                i += 1
            continue
        if re.match(rb'^\s*if \(rx_reqrun(_whole)?\(subject, subject_length, search_from\) '
                    rb'>= subject_length\) return 0;$', ln):
            i += 1
            continue
        out.append(ln)
        i += 1
    return b"\n".join(out), blocks


def one(job):
    i, key, pat, extra = job
    b = emit(E["BASE"], pat, extra, f"{E['SCR']}/m/{i}/b")
    a = emit(E["NEW"], pat, extra, f"{E['SCR']}/m/{i}/a")
    if b is None and a is None:
        return key, "refused", []
    if b is None or a is None or b"TIMEOUT" in (a, b):
        return key, "odd", ["refusal/timeout mismatch"]
    b = norm(b)
    pred = stamp(b, b"REQ_WHY") == "emitted" and stamp(b, b"REQ_RUN") not in (None, "none")
    changed = b != a
    errs = []
    if changed != pred:
        errs.append("changed=%s predicted=%s" % (changed, pred))
    sb = [ln for ln in b.split(b"\n") if ln.startswith(b"#define RX_")]
    sa = [ln for ln in a.split(b"\n") if ln.startswith(b"#define RX_")]
    if sb != sa:
        errs.append("stamps moved")
    rb, loops = strip_base(b)
    ra, blocks = strip_new(a)
    if rb != ra:
        errs.append("residue differs")
    if loops != blocks:
        errs.append("loops %r != blocks %r" % (loops, blocks))
    return key, ("changed" if changed else "identical"), errs


def main():
    jobs, n = [], 0
    for pname, rows, cfgs in (
            ("bench", bench_pop(), [("caps", []), ("nocaps", ["--no-captures"]),
                                    ("vm-caps", ["--engine=vm"]),
                                    ("vm-nocaps", ["--engine=vm", "--no-captures"])]),
            ("corpus", corpus_pop(), [("auto", []), ("vm", ["--engine=vm"]),
                                      ("utf8", ["-e", "utf8"])])):
        for rid, pat in rows:
            for cname, extra in cfgs:
                n += 1
                jobs.append((n, (pname, rid, cname), pat, extra))
    tally = collections.Counter()
    bad, movers = [], []
    with ThreadPoolExecutor(max_workers=int(E.get("JOBS", "8"))) as ex:
        for key, verdict, errs in ex.map(one, jobs):
            tally[(key[0], verdict)] += 1
            if errs:
                bad.append((key, errs))
            if verdict == "changed":
                movers.append("\t".join(key))
    if E.get("LIST"):
        with open(E["LIST"], "w") as f:
            f.write("".join(m + "\n" for m in movers))
    for k in sorted(tally):
        print("%s\t%s\t%d" % (k[0], k[1], tally[k]))
    for key, errs in bad:
        print("BAD\t%s\t%s\t%s\t%s" % (key[0], key[1], key[2], "; ".join(errs)))
    print("TOTAL %d artifact-configs, %d bad" % (len(jobs), len(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
