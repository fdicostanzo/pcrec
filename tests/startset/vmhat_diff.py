#!/usr/bin/env python3
"""tests/startset/vmhat_diff.py -- [START-SET] stage 2: THE VM HAT's
EVERY-STARTPOS ANSWER DIFFERENTIAL and START-BYTE ORACLE (D148;
docs/design/startset.md §6.2 rows "answer identity" (2) and "start-byte
oracle"; review r4 checks-F2 (b), checks-F3; the k82hbuild precedent).

POPULATION: the stage-2 mover manifest's corpus rows (`manifests/
manifest_s2_vm_auto.tsv`, MANIFEST= to choose another, e.g. the forced one)
x three CONFIGS: the block's own options (`auto`), `--engine=vm`, and
`--no-captures` (which may route a mover to the DFA, where the pair must
simply agree). For each (mover, config) the pattern is built twice by ONE
compiler -- `-fno-start-set` (`pa`, today's emitter: the reference, which
never reads the start set) and the default (`pb`, the hat) -- linked into one
TU with vmhat_driver.c, and asked at EVERY startpos of every subject:
answers and capture vectors equal, except that a deny-arm GIVE-UP may become
the hat's answer (docs/spec/match_api.md §3.1, never the reverse); and every
non-empty deny-arm match must start on a byte of the `start_set` fact.

SUBJECTS: the block's own `.rxt` subjects (and each behind 1..3 bytes outside
S, so a seek has something to skip), an exhaustive sweep over a small
per-pattern alphabet (members of S first, then the pattern's own bytes, then
one byte outside S), seeded random strings over that alphabet plus newline
and UTF-8 bytes, and under `-e utf8` stray continuation bytes, a truncated
lead and an overlong lead around each own subject.

`SAN=1` builds the driver and both artifacts with
`-fsanitize=address,undefined` (each subject is already in an exactly-sized
heap block). `SHARD=i/n` runs every n-th (mover, config) from the i-th.
FLOOR (K35): the (mover, config) pairs run, below which a collapsed
population fails rather than reading clean.

STAGE 3, THE DFA HAT (`HAT=dfa`): the same differential over the stage-3
manifest's corpus rows (`manifest_s3_dfa.tsv`) x {own options,
`--no-captures` (a hybrid mover's own DFA build), `-fprefilter-collapse` (a
hybrid mover's COUNT-COLLAPSED prefilter, sound-F5(d)'s population), and on a
utf8 mover `-futf-check` (D133: the deny arm's PCREC_ERR_UTF, which
tests/utfcheck pins to libpcre2, must survive the hat -- the skip runs after
the entry prologue's `rx_valid_upto`, sabotage S504)}; its
sweep alphabet also carries up to two bytes of the deny arm's `E` outside S
(read off `pa`'s emitted tables, startset_lib.machine_sets): the bytes a skip
passes that MOVE the left context, which is what the re-seed exists for.
The start-byte oracle is the same: every deny-arm match starts on a byte of
the fact, and the fact is the DFA hat's `T` (Q-R1's T == S).

Env: PCREC, CC, TMPDIR, JOBS, SAN, SHARD, HAT, MANIFEST, FLOOR.
Prints PASS:/FAIL: and the trailers.
"""
import concurrent.futures as cf, os, random, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TREE = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import startset_lib as L

PCREC = os.environ.get("PCREC", os.path.join(TREE, "build", "pcrec"))
CC = os.environ.get("CC") or shutil.which("gcc-16") or "gcc"
SAN = os.environ.get("SAN") == "1"
CFLAGS = (["-O1", "-g", "-fsanitize=address,undefined", "-fno-omit-frame-pointer"]
          if SAN else ["-O1"]) + ["-std=gnu11", "-w"]
JOBS = int(os.environ.get("JOBS", "6"))
HAT = os.environ.get("HAT", "vm")
MANIFEST = os.environ.get("MANIFEST", os.path.join(
    HERE, "manifests", "manifest_s3_dfa.tsv" if HAT == "dfa" else "manifest_s2_vm_auto.tsv"))
# K35 floor: half the (mover, config) pairs measured at landing (lane
# ssbuild2, docs/dev/lanes/ssbuild2_report.md §4: 528 pairs; lane ssbuild3,
# docs/dev/lanes/ssbuild3_report.md: the DFA hat's figure).
FLOOR = int(os.environ.get("FLOOR", "105" if HAT == "dfa" else "264"))   # 210 / 528 pairs at landing
TMO = 600


def vm_args(args):
    return [a for a in args if not a.startswith("--engine=")] + ["--engine=vm"]


def esc(b):
    return "".join(chr(c) if 0x21 <= c < 0x7f and c != 0x5c else "\\x%02x" % c for c in b)


def rxt_unesc(t):
    out, i = bytearray(), 0
    while i < len(t):
        c = t[i]
        if c == 0x5c and i + 1 < len(t):
            n = t[i + 1]
            if n == ord("x") and i + 3 < len(t):
                try:
                    out.append(int(t[i + 2:i + 4], 16)); i += 4; continue
                except ValueError:
                    pass
            out.append({ord("t"): 9, ord("n"): 10, ord("r"): 13}.get(n, n)); i += 2; continue
        out.append(c); i += 1
    return bytes(out)


CASE = re.compile(rb'^(?:m|n|ms|ns|mc)\s+(?:-?\d+\s+)?"((?:[^"\\]|\\.)*)"')


def own_subjects(bid):
    path, line = bid.rsplit(":", 1)
    out = []
    with open(os.path.join(TREE, path), "rb") as f:
        lines = f.read().split(b"\n")
    for ln in lines[int(line):]:
        if ln.startswith(b"pattern ") or ln.startswith(b"pattern-esc "):
            break
        m = CASE.match(ln)
        if m:
            out.append(rxt_unesc(m.group(1)))
    return out


def subjects(pat, S, own, utf8, ctx=()):
    outside = [b for b in (0x20, 0x7e, 0x01, 0x0a, 0x5f, 0x2d) if b not in S][:1]
    alpha = []
    for b in sorted(S, key=lambda b: (not (0x20 < b < 0x7f), b))[:3] + list(ctx) + list(pat) + outside:
        if b not in alpha and len(alpha) < 5 and (b in S or b in outside or 0x20 < b < 0x7f):
            alpha.append(b)
    out = {b""}
    frontier = [b""]
    for ln in range(1, 6 if len(alpha) <= 4 else 5):
        frontier = [f + bytes([c]) for f in frontier for c in alpha]
        out.update(frontier)
    for o in own:
        out.add(o)
        for j in range(1, 4):
            out.add(bytes(outside or [0x20]) * j + o)
            out.add(o + bytes(outside or [0x20]) * j + o)
        if utf8:
            for st in (b"\x80", b"\x80\x80\x80"):
                out.update({st + o, o[:len(o) // 2] + st + o[len(o) // 2:], o + st})
            out.update({o + b"\xe2\x82", o + b"\xc3", b"\xc0\xaf" + o})
    rnd = random.Random(0x5527)
    pool = alpha + [0x0a, 0xc3, 0xa9, 0xe2, 0x84, 0xaa, 0x80]
    for _ in range(60):
        out.add(bytes(rnd.choice(pool) for _ in range(rnd.randint(1, 40))))
    return sorted(out)


def fact_set(pat, args):
    r = subprocess.run([PCREC, *args, "--emit-facts", "--pattern", pat], capture_output=True, timeout=TMO)
    fct, _ = L.facts(r.stdout.decode("utf-8", "replace"))
    nul, S = L.set_of(fct["start_set"]["value"])
    return None if nul else S


def run(job):
    bid, pat, args, cfg, td = job
    d = tempfile.mkdtemp(dir=td)
    for pfx, extra in (("pa", ["-fno-start-set"]), ("pb", [])):
        r = subprocess.run([PCREC, *extra, *args, "-p", pfx, "-o", os.path.join(d, pfx + ".c"),
                            "--pattern", pat], capture_output=True, timeout=TMO)
        if r.returncode:
            return {"status": "refused", "cfg": cfg}
    S = fact_set(pat, args)
    arg1 = "-" if (S is None or b"\\K" in pat) else bytes(
        sum(1 << (b & 7) for b in S if b >> 3 == i) for i in range(32)).hex()
    cc = subprocess.run([CC, *CFLAGS, "-I", d, "-o", os.path.join(d, "t"),
                         os.path.join(HERE, "vmhat_driver.c"), os.path.join(d, "pa.c"),
                         os.path.join(d, "pb.c")], capture_output=True, timeout=TMO)
    if cc.returncode:
        return {"status": "build", "cfg": cfg, "err": cc.stderr.decode("latin-1")[:300]}
    ctx = ()
    if HAT == "dfa" and S is not None:
        m = L.machine_sets(open(os.path.join(d, "pa.c"), encoding="latin-1").read(), "pa")
        if m.get("status") == "ok":
            ctx = sorted(m["E"] - S, key=lambda b: (not (0x20 < b < 0x7f), b))[:2]
    subj = subjects(pat, S or set(), own_subjects(bid), "utf8" in " ".join(args), ctx)
    env = dict(os.environ, ASAN_OPTIONS="detect_leaks=0:abort_on_error=0")
    try:
        r = subprocess.run([os.path.join(d, "t"), arg1],
                           input=("\n".join(esc(s) for s in subj) + "\n").encode("latin-1"),
                           capture_output=True, timeout=TMO, env=env)
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "cfg": cfg}
    m = re.search(rb"cells (\d+) same (\d+) allow (\d+) defect (\d+) matches (\d+) startbyte_viol (\d+)", r.stdout)
    rec = {"status": "ok" if (r.returncode == 0 and m) else "defect", "cfg": cfg,
           "err": r.stderr.decode("latin-1")[:600], "checked": arg1 != "-"}
    if m:
        rec.update(dict(zip(("cells", "same", "allow", "defect", "matches", "sbv"), map(int, m.groups()))))
    return rec


def main():
    want = set()
    for ln in open(MANIFEST, encoding="utf-8"):
        if ln.startswith("#") or not ln.strip() or ln.startswith("bench/"):
            continue
        i, o, _h = ln.rstrip("\n").split("\t")
        want.add((i, o))
    blocks, _ = L.corpus_blocks(PCREC, TREE)
    jobs = []
    with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as td:
        for b in blocks:
            if (b["id"], " ".join(b["args"])) not in want:
                continue
            if HAT == "dfa":
                cfgs = [("auto", b["args"]), ("nocaps", b["args"] + ["--no-captures"]),
                        ("collapse", b["args"] + ["-fprefilter-collapse"])]
                if "--encoding=utf8" in b["args"]:
                    cfgs.append(("utfcheck", b["args"] + ["-futf-check"]))
            else:
                cfgs = [("auto", b["args"]), ("vm", vm_args(b["args"])),
                        ("nocaps", b["args"] + ["--no-captures"])]
            for cfg, args in cfgs:
                jobs.append((b["id"], b["pattern"], args, cfg, td))
        if os.environ.get("SHARD"):
            i, n = map(int, os.environ["SHARD"].split("/"))
            jobs = jobs[i::n]
        with cf.ThreadPoolExecutor(JOBS) as ex:
            res = list(ex.map(run, jobs))
    passed = failed = 0
    tot = {"cells": 0, "same": 0, "allow": 0, "matches": 0, "pairs": 0, "checked": 0}
    per = {}
    for (bid, pat, args, cfg, _), r in zip(jobs, res):
        per.setdefault(cfg, {"ok": 0, "refused": 0, "bad": 0})
        if r["status"] == "refused":
            per[cfg]["refused"] += 1
            continue
        if r["status"] != "ok":
            per[cfg]["bad"] += 1
            failed += 1
            print("FAIL: %s [%s] %s: %s %s" % (bid, " ".join(args), cfg, r["status"], r.get("err", "")))
            continue
        per[cfg]["ok"] += 1
        tot["pairs"] += 1
        tot["checked"] += r["checked"]
        for k in ("cells", "same", "allow", "matches"):
            tot[k] += r[k]
    print("REACH: %d (mover, config) pairs run of %d (per config %s); %d cells, %d same, %d deny-give-up -> hat-answer, %d matches start-byte-checked on %d pairs (floor %d pairs)"
          % (tot["pairs"], len(jobs), per, tot["cells"], tot["same"], tot["allow"], tot["matches"], tot["checked"], FLOOR))
    if tot["pairs"] < FLOOR:
        failed += 1
        print("FAIL: [%s-diff] %d pairs ran, below the floor %d" % (HAT, tot["pairs"], FLOOR))
    if not failed:
        passed += 1
        print("PASS: [%s-diff] every startpos of every subject answers as the deny arm does (a give-up may become the answer), and every deny-arm match starts on a byte of the start set%s"
              % (HAT, " (ASan/UBSan)" if SAN else ""))
    print("checks passed: %d" % passed)
    print("checks failed: %d" % failed)
    sys.exit(1 if failed else 0)


main()
