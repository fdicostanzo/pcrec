#!/usr/bin/env python3
"""docs/design/memfn/r17b_prime/b3a/pr11_census.py -- PR-11's CENSUS over
the COLLAPSED HYBRIDS (lane b3a; r17b_prime.md rev 3 §3.1 row B3a, §4.6).

    pr11_census.py --pcrec PCREC [--bench-dir DIR] [--jobs J] [--tmp DIR]

Every pattern of the corpus, bench and rwquest populations that holds a
counted repeat is compiled under the default arm and `-e utf8`; the artifacts
whose VM hybrid prefilter is COUNT-COLLAPSED are the population (counted per
population and arm, K35). For each, the claims are the req walk's (necessary
set members and whole run, `--emit-facts`) and the evidence is the EMITTED
front run over the pattern's MATCHING corpus subjects (the `.rxt` `m`/`ms`
cases of its block, under the block's own encoding) with each claim deleted
(tests/memfn/pr11_front.py). A collapsed artifact with no matching corpus
case takes subjects harvested from the real-world corpus texts, else a
HAND-WRITTEN one (HAND_SUBJECTS, each checked to match by python `re`); one
with none of the three is UNCHECKED, never a pass, and fails the census
(lane b3afix). The `ok` (checked) count per population is floored
(pr11_floors.tsv, floor(0.9 x measured)). Exit 1 on any `enforcement` or
`vacuous` result, an unchecked artifact or a floor miss.
"""
import argparse
import collections
import concurrent.futures
import glob
import os
import re
import subprocess
import sys

TREE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../.."))
sys.path.insert(0, os.path.join(TREE, "tests/memfn"))
import pr11_front as pf  # noqa: E402

COUNTED = re.compile(r"\{\d+(,\d*)?\}")


def unq(s):
    """A `--list-source` subject field ("..." in the .rxt subject escapes)."""
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        s = s[1:-1]
    out, i = bytearray(), 0
    while i < len(s):
        if s[i] == "\\" and i + 1 < len(s):
            c = s[i + 1]
            if c == "x":
                out.append(int(s[i + 2:i + 4], 16)); i += 4; continue
            m = {"t": b"\t", "n": b"\n", "r": b"\r", "\\": b"\\", '"': b'"', "0": b"\0"}.get(c)
            if m is not None:
                out += m; i += 2; continue
        out += s[i].encode("utf-8", "surrogateescape"); i += 1
    return bytes(out)


def corpus(pcrec):
    """(flags, pattern, [matching subjects]) per corpus pattern block."""
    out = []
    for f in sorted(glob.glob(os.path.join(TREE, "tests", "**", "*.rxt"), recursive=True)):
        r = subprocess.run([pcrec, "--list-source", f], capture_output=True, timeout=120)
        if r.returncode != 0:
            continue
        blocks, cases, sect = {}, collections.defaultdict(list), None
        for ln in r.stdout.decode("utf-8", "surrogateescape").splitlines():
            if ln.startswith("#section"):
                sect = ln.split()[1]
                continue
            if ln.startswith("#"):
                continue
            c = ln.split("\t")
            if sect is None and c[0] in ("pattern", "pattern-esc") and len(c) > 8:
                pat = pf_decode(c[4])
                enc = c[8]
                blocks[c[1]] = (["-e", enc] if enc and enc != "byte" else [], pat)
            elif sect == "cases" and len(c) > 7 and c[3] in ("m", "ms", "mc") and c[6] == "inline":
                cases[c[1]].append(unq(c[7]))
        for bl, (fl, pat) in blocks.items():
            out.append((fl, pat, cases.get(bl, [])))
    return out


def pf_decode(s):
    """The `pattern` column's escapes (\\t \\n \\r \\\\ \\xNN) back to text."""
    return unq('"%s"' % s).decode("utf-8", "surrogateescape")


def bench(bench_dir):
    out = []
    for f in sorted(glob.glob(os.path.join(bench_dir, "bench", "*", "patterns", "*.rx"))):
        b = open(f, "rb").read()
        if b.endswith(b"\n"):
            b = b[:-1]
        out.append(([], os.fsdecode(b), []))
    return out


def rwquest():
    out = []
    with open(os.path.join(TREE, "docs/dev/lanes/rwquest/questions.tsv"), encoding="utf-8",
              errors="surrogateescape") as fh:
        hdr = fh.readline().rstrip("\n").split("\t")
        ip, iflag = hdr.index("pattern"), hdr.index("flags")
        for ln in fh:
            c = ln.rstrip("\n").split("\t")
            if len(c) <= max(ip, iflag):
                continue
            pat, flags = c[ip], [] if c[iflag] in ("", "-") else c[iflag].split(",")
            ims = "".join(x for x in flags if x in "ims")
            full = ("(?%s)" % ims if ims else "") + pat
            ifile = hdr.index("files")
            if len(c) > ifile and c[ifile]:
                _RWFILE[full] = c[ifile].split(";")[0]
            out.append(((["-e", "utf8"] if "utf" in flags else []) + (["--ucp"] if "ucp" in flags else []),
                        full, []))
    return out


def _corpus_dir():
    """[REGIME-CORPUS]'s gitignored texts, `worktrees/.corpus/` of the MAIN
    checkout (a lane worktree has none of its own), read only."""
    try:
        common = subprocess.run(["git", "-C", TREE, "rev-parse", "--path-format=absolute",
                                 "--git-common-dir"], capture_output=True, text=True).stdout.strip()
        return os.path.join(os.path.dirname(common), "worktrees", ".corpus")
    except OSError:
        return os.path.join(TREE, "worktrees", ".corpus")


# HAND-WRITTEN matching subjects (lane b3afix, review MINOR-3) for the
# collapsed artifacts no corpus case and no harvest reaches; each is checked
# to MATCH by python `re` before it is used (`hand_subjects`), and the front
# must pass it (pr11_front.check's positive control).
HAND_SUBJECTS = {
    r"\b(?:ERROR|FATAL|CRIT)\b.{0,200}?\b(?:timeout|timed out|refused|denied|unreachable)\b": [
        b"2026-10-17T03:12:44Z ERROR db pool: connection to 10.0.0.7 timed out after 30s\n",
        b"FATAL upstream api.internal: connection refused"],
    r"(?s)PK\x03\x04[\s\S]{26}(BILLS-[\w.-]+\.xml)": [
        b"PK\x03\x04\x14\x00\x00\x00\x08\x00abcdefghijklmnopqrstBILLS-118hr1234ih.xml"],
}


def hand_subjects(pat):
    subs = HAND_SUBJECTS.get(pat, [])
    for s in subs:
        if not re.search(pat.encode("utf-8", "surrogateescape"), s):
            raise SystemExit("HAND_SUBJECTS: %r does not match %r (python re)" % (s, pat))
    return subs


CORPUS_DIR = os.environ.get("PR11_CORPUS") or _corpus_dir()
ALL_TEXTS = sorted(glob.glob(os.path.join(CORPUS_DIR, "*", "*.*")))
_RWFILE = {}


def texts_for(pat):
    """The rwquest question's own first file, when `pat` is one."""
    return [os.path.join(CORPUS_DIR, _RWFILE[pat])] if pat in _RWFILE else []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pcrec", default=os.path.join(TREE, "build/pcrec"))
    ap.add_argument("--bench-dir", default="/home/pcrec/projects/pcrec-bench")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--tmp", default=os.environ.get("TMPDIR", "/tmp"))
    ap.add_argument("--floors", default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                     "pr11_floors.tsv"))
    a = ap.parse_args()
    pops = {"corpus": corpus(a.pcrec), "bench": bench(a.bench_dir), "rwquest": rwquest()}
    jobs = []
    for pop, items in pops.items():
        for fl, pat, subs in items:
            if not COUNTED.search(pat):
                continue
            arms = [fl] if fl else [[], ["-e", "utf8"]]
            for arm in arms:
                jobs.append((pop, arm, pat, subs))
    res = collections.Counter()
    bad = []
    unchecked = []

    def one(k, job):
        pop, arm, pat, subs = job
        w = os.path.join(a.tmp, "pr11c%d" % k)   # one directory per job: a slow compile is never overwritten
        if not pf.compile_front(a.pcrec, arm, pat, w):
            return pop, arm, pat, "not-collapsed", {}
        if not subs:
            # no matching corpus case: harvest matches from the real-world
            # corpus texts (rwquest's own file first, then every class)
            texts = [t for t in (texts_for(pat) + ALL_TEXTS) if os.path.isfile(t)]
            subs = pf.harvest(os.path.join(w, "a.c"), texts, w)
        if not subs:
            subs = hand_subjects(pat)
        if not subs:
            return pop, arm, pat, "unchecked-no-subject", {}
        st, det = pf.check(a.pcrec, arm, pat, subs, w)
        return pop, arm, pat, st, det

    with concurrent.futures.ThreadPoolExecutor(a.jobs) as ex:
        for pop, arm, pat, st, det in ex.map(lambda kj: one(*kj), enumerate(jobs)):
            if st == "not-collapsed":
                continue
            res[(pop, " ".join(arm) or "-", st)] += 1
            res[(pop, " ".join(arm) or "-", "derived")] += det.get("derived", 0)
            if st in ("enforcement", "vacuous", "driver"):
                bad.append("%s [%s] %s: %s %s" % (pop, " ".join(arm), pat, st, det))
            if st == "unchecked-no-subject":
                unchecked.append("%s [%s] %s" % (pop, " ".join(arm) or "-", pat))
    print("# PR-11 census: counted-repeat patterns compiled per population x arm; "
          "rows are the COUNT-COLLAPSED hybrids")
    print("pop\tarm\tstate\tcount")
    for k in sorted(res):
        print("%s\t%s\t%s\t%d" % (k + (res[k],)))
    for u in sorted(unchecked):
        bad.append("unchecked (no matching subject; give it one in HAND_SUBJECTS): " + u)
    # the `ok` count per population, floored ([rev3 D10]'s shape: floor(0.9 x
    # measured), lane b3afix): a population whose checked artifacts FALL is a
    # control that stopped reaching its population
    if a.floors and os.path.isfile(a.floors):
        for ln in open(a.floors):
            if ln.startswith("#") or not ln.strip():
                continue
            pop, fl = ln.rstrip("\n").split("\t")[:2]
            got = sum(v for k, v in res.items() if k[0] == pop and k[2] == "ok")
            if got < int(fl):
                bad.append("floor %s ok %d < %s" % (pop, got, fl))
            else:
                print("PASS: floor %s ok %d >= %s" % (pop, got, fl))
    for b in bad:
        print("FAIL: " + b)
    collapsed = sum(v for k, v in res.items() if k[2] != "derived")
    if not collapsed:
        print("FAIL: no collapsed hybrid in any population (K35)")
    print("PR11_CENSUS_DONE collapsed=%d fails=%d" % (collapsed, len(bad) + (0 if collapsed else 1)))
    return 1 if bad or not collapsed else 0


if __name__ == "__main__":
    sys.exit(main())
