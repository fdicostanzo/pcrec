#!/usr/bin/env python3
"""rulepilot: build the timing slot (compile only, no clock; writes ONLY under OUT).

The slot is grid1's EXT-ARM-SET shape (docs/dev/lanes/grid1/README.md "The arm contract"), the
shape the E8 and flat slots used: OUT/ext/rp/arms.tsv declares one cell per site, `rp-<ID>`,
whose arms are the site's FORCEABLE default-route arms from the committed inventory
(inventory/census.jsonl: the census arms plus the pick-only arms), `a0` = the default compile =
the cell's base; OUT/bin/rp-<ID>/<arm>/run is grid1's gdrv.c linked with the arm's artifact;
OUT/subj/rp_<ID>_{m,d}<L>-S/ are the site's streamed subjects (gen_subj.py). Every arm is
re-emitted by THIS compiler and must be byte-identical to the inventory's arm (the census rule:
the `.c` minus its one `#include` line); a mismatch means the compiler moved and FAILS the build.

usage: slot_build.py OUT [--sites ID,ID..] [--jobs 4]       env PCREC (default: this worktree's)
"""
import argparse, concurrent.futures as cf, csv, hashlib, json, os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
G1 = os.path.join(W, "docs", "dev", "lanes", "grid1")
PCREC = os.environ.get("PCREC", os.path.join(W, "build", "pcrec"))
CORPUS = os.environ.get("CORPUS", "/home/pcrec/projects/pcrec/worktrees/.corpus")
INV = os.environ.get("RP_INV", os.path.join(HERE, "inventory"))

def excluded_ids():
    """The declared pre-timing exclusions (inventory/exclusions.tsv: id, date, reason), read by
    slot_build, mkjobs, read_slot (and, through the dataset, search's split)."""
    p = os.path.join(INV, "exclusions.tsv")
    if not os.path.exists(p):
        return set()
    return {r["id"] for r in csv.DictReader(open(p, encoding="utf-8"), delimiter="	", quoting=csv.QUOTE_NONE)}

def sh(argv, **kw):
    return subprocess.run(argv, capture_output=True, **kw)

def plan(only=None):
    files = {r["id"]: r["files"].split(";")[0] for r in csv.DictReader(
        open(os.path.join(W, "docs/dev/lanes/rwquest/questions.tsv"), encoding="utf-8"),
        delimiter="\t", quoting=csv.QUOTE_NONE)}
    out, skip = [], excluded_ids()
    for line in open(os.path.join(INV, "census.jsonl")):
        r = json.loads(line)
        if r["refused"] or len(r["arms"]) < 2 or r["id"] in skip or (only and r["id"] not in only):
            continue
        if files[r["id"]].startswith("sealed"):
            raise SystemExit(f"slot_build: {r['id']} names a sealed file")
        r["src"] = os.path.join(CORPUS, files[r["id"]])
        out.append(r)
    return out

def body_sha(c_path, inc):
    lines = open(c_path, "rb").read().splitlines()
    return hashlib.sha256(b"\n".join(l for l in lines if not l.startswith(inc))).hexdigest()[:16]

def build_site(out, r):
    msgs = []
    for a in r["arms"]:
        d = os.path.join(out, "bin", "rp-" + r["id"], a["arm"]); os.makedirs(d, exist_ok=True)
        argv = ["gnutimeout", "60", PCREC, "-p", "rx", "--features", "all", "-o", os.path.join(d, "art.c")] \
            + r["popts"] + a["how"] + ["--pattern", r["pattern"]]
        p = sh(argv)
        if p.returncode:
            return f"FAIL {r['id']} {a['arm']}: emit rc={p.returncode} {p.stderr[-200:]!r}"
        if body_sha(os.path.join(d, "art.c"), b'#include "art.h"') != a["sha"]:
            return f"FAIL {r['id']} {a['arm']}: re-emitted bytes differ from the inventory (the compiler moved)"
        L = os.path.join(out, "lib")
        for cmd in (["gcc", "-O2", "-I" + d, "-I" + L, "-c", os.path.join(d, "art.c"), "-o", os.path.join(d, "art.o")],
                    ["gcc", "-O2", "-I" + d, "-I" + L, "-c", os.path.join(L, "gdrv.c"), "-o", os.path.join(d, "gdrv.o")],
                    ["gcc", "-o", os.path.join(d, "run"), os.path.join(d, "gdrv.o"), os.path.join(d, "art.o")]):
            p = sh(cmd)
            if p.returncode:
                return f"FAIL {r['id']} {a['arm']}: {' '.join(cmd[:2])} {p.stderr[-200:]!r}"
        if a["arm"] == "a0":
            p = sh(["gcc", "-O2", "-I" + d, "-I" + L, "-o", os.path.join(d, "chk"), os.path.join(L, "gchk.c"), os.path.join(d, "art.o")])
            if p.returncode:
                return f"FAIL {r['id']} a0: chk link {p.stderr[-200:]!r}"
    chk = os.path.join(out, "bin", "rp-" + r["id"], "a0", "chk")
    p = sh(["python3", "-I", os.path.join(HERE, "gen_subj.py"), out, r["id"], r["src"], chk], text=True)
    if p.returncode:
        return f"FAIL {r['id']}: gen_subj {p.stderr[-300:]}"
    return "OK " + p.stdout.strip()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out"); ap.add_argument("--sites"); ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args()
    out = a.out
    for sub in ("tmp", "subj", "lib", "bin", "ext/rp", "res", "ans", "time"):
        os.makedirs(os.path.join(out, sub), exist_ok=True)
    for f in ("gdrv.c", "gchk.c", "gload.h", "keep.h"):
        shutil.copy(os.path.join(G1, f), os.path.join(out, "lib", f))
    open(os.path.join(out, "arms.tsv"), "w").write("# no own cells: rulepilot is an ext arm set\n")
    shutil.copy(os.path.join(out, "arms.tsv"), os.path.join(out, "arms_f2.tsv"))
    open(os.path.join(out, "subj_facts.tsv"), "w").write(
        "name\tfamily\tn\tg\tL\tshape\treuse\tnbuf\tplanted_matches\tplanted_landings\n")
    open(os.path.join(out, "oracle.tsv"), "w").close()
    open(os.path.join(out, "subj_rp.tsv"), "w").write("id\tregime\tlen\tnbuf\tbytes\tmatches\n")
    sha = sh(["sha256sum", PCREC], text=True).stdout.split()[0]
    commit = sh(["git", "-C", W, "rev-parse", "HEAD"], text=True).stdout.strip()
    open(os.path.join(out, "provenance.txt"), "w").write(
        f"pcrec={PCREC}\npcrec_sha256={sha}\nworktree_commit={commit}\n"
        f"gcc={sh(['gcc', '--version'], text=True).stdout.splitlines()[0]}\n")
    sites = plan(set(a.sites.split(",")) if a.sites else None)
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        res = list(ex.map(lambda r: build_site(out, r), sites))
    bad = [x for x in res if not x.startswith("OK")]
    open(os.path.join(out, "tmp", "build.log"), "w").write("\n".join(res) + "\n")
    if bad:
        print("\n".join(bad[:20])); raise SystemExit(f"slot_build: FAILED ({len(bad)} sites)")
    subj = {}
    for row in open(os.path.join(out, "subj_rp.tsv")).read().splitlines()[1:]:
        i, reg, L = row.split("\t")[:3]
        subj.setdefault(i, []).append(f"rp_{i}_{reg[0]}{L}-S")
    with open(os.path.join(out, "ext", "rp", "arms.tsv"), "w") as f:
        f.write("# rulepilot's ext arm table: cell arm role subjects modes\n")
        for r in sites:
            for arm in r["arms"]:
                f.write(f"rp-{r['id']}\t{arm['arm']}\t{'base' if arm['arm'] == 'a0' else 'arm'}\t"
                        f"{','.join(sorted(subj[r['id']]))}\tall\n")
    p = sh(["python3", "-I", os.path.join(G1, "arms.py"), out, "validate", "all"], text=True)
    print(p.stdout.strip().splitlines()[-1])
    if p.returncode:
        print(p.stdout[-2000:]); raise SystemExit("slot_build: arm tables invalid")
    print(f"slot_build: done sites={len(sites)} arms={sum(len(r['arms']) for r in sites)} "
          f"groups={sum(len(v) for v in subj.values())}")

if __name__ == "__main__":
    main()
