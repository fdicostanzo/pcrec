"""x0fix (kit_proof rev 2.2): who the two reading defects R1/R2 reach, counted
over the kvcensus population with the fixed kvdfa: every census pattern at its
own flags, and every DFA-engine one again under -fno-rev-end (R).

R1: a machine whose EMITTED entry constant is not row 0 (kvdfa read row 0 as
the start before rev 2.2). Counted per machine (anchored, forward), seeded or
not, with or without a view table; a DEAD entry constant (a seeded machine
whose absent predecessor fails) is counted apart: the old `starts()` added
row 0 for it too.
R2: an anchored machine whose language from its entry gains a byte at some
depth only through the eol view's gated final '\\n' (kvdfa.lang's `view_d`),
i.e. where the plain walk under-stated S_d.

usage (repo root, build/pcrec built; > 50 compiles: under scripts/boxlock):
  PCREC=build/pcrec python3 -I docs/design/kit_proof/x0/exposure.py [-j N]
One line per count; one `e.g.` line per class with up to four patterns.
"""
import collections, gzip, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "dev", "kvcensus"))
import conj   # noqa: E402
import kvdfa  # noqa: E402

KV = os.path.join(HERE, "..", "..", "..", "dev", "kvcensus")


def one(a):
    fl, pat = a
    c = conj.compile_c(pat, fl)
    out = []
    if c is None:
        return out
    for m in ("anchored", "forward"):
        M = kvdfa.Machine(c, m)
        if not M.ok:
            continue
        row = dict(m=m, seeded=M.seeded, views=bool(M.views), read=M.entry_read,
                   entry=M.entry, dead=M.entry_read and M.entry is None,
                   ne0=M.entry_read and M.entry is not None and M.entry != 0)
        if m == "anchored" and M.entry_read:
            L = kvdfa.lang(M, M.starts())
            row["view_d"] = L["view_d"]
        out.append(row)
    if not any(r["m"] == "anchored" for r in out):
        # the census site reading's fallback (x0.py site_reading): a hybrid's
        # language machine, compiled --engine=dfa --no-captures
        c2 = compile_lang(pat, fl)
        M = kvdfa.Machine(c2, "anchored") if c2 else None
        if M is not None and M.ok and M.entry_read:
            out.append(dict(m="anchored-lang", seeded=M.seeded, views=bool(M.views), read=True,
                            entry=M.entry, dead=M.entry is None,
                            ne0=M.entry is not None and M.entry != 0,
                            view_d=kvdfa.lang(M, M.starts())["view_d"]))
    return out


def compile_lang(pat, fl):
    a = [conj.PCREC, "-p", "rx", "--features", "all", "-fno-scan-edge", "--engine=dfa", "--no-captures"]
    if "i" in fl: a.append("-i")
    if "u" in fl: a += ["-e", "utf8"]
    if "R" in fl: a.append("-fno-rev-end")
    argv = [os.fsencode(x) for x in ["nice", "-n", "19", "gnutimeout", "30"] + a + ["-o", "-", "--pattern"]]
    p = subprocess.run(argv + [pat.encode("latin-1")], capture_output=True)
    return p.stdout.decode("latin-1") if p.returncode == 0 else None


def main():
    j = int(sys.argv[sys.argv.index("-j") + 1]) if "-j" in sys.argv else 1
    pats = [json.loads(l) for l in gzip.open(os.path.join(KV, "patterns.tsv.gz"), "rt")]
    jobs = set()
    for p in pats:
        fl = ("i" if p.get("icase") else "") + ("u" if p.get("enc") == "utf8" else "")
        pat = bytes.fromhex(p["pat"]).decode("latin-1")
        jobs.add((fl or "-", pat))
        if p.get("engine") == "dfa":
            jobs.add((fl + "R", pat))
    jobs = sorted(jobs)
    if j > 1:
        from multiprocessing import Pool
        with Pool(j) as pool:
            res = pool.map(one, jobs, chunksize=16)
    else:
        res = [one(a) for a in jobs]
    h, ex = collections.Counter(), collections.defaultdict(list)
    for (fl, pat), rows in zip(jobs, res):
        arm = "R" if "R" in fl else "default"
        enc = "utf8" if "u" in fl else "native"
        h[("items", arm, enc)] += 1
        for r in rows:
            k = (r["m"], arm, enc, "seeded" if r["seeded"] else "unseeded",
                 "views" if r["views"] else "no-views")
            h[("machines",) + k] += 1
            if not r["read"]:
                h[("entry-unread",) + k] += 1
                if len(ex[("entry-unread", r["m"])]) < 4:
                    ex[("entry-unread", r["m"])].append(pat[:40])
            elif r["dead"]:
                # a DEAD entry constant (seeded: the absent predecessor fails,
                # `(?<=x)cat`); the old starts() added row 0 for it
                h[("entry dead",) + k] += 1
            elif r["ne0"]:
                h[("R1 entry!=0",) + k] += 1
                kk = ("R1 entry!=0", r["m"], k[3], k[4])
                if len(ex[kk]) < 4:
                    ex[kk].append(pat[:40])
            if r.get("view_d"):
                h[("R2 view-gated byte", arm, enc)] += 1
                if len(ex[("R2", arm)]) < 4:
                    ex[("R2", arm)].append(pat[:40])
    print("## x0fix exposure: kvcensus patterns at own flags (default); DFA ones also -fno-rev-end (R)")
    for k, v in sorted(h.items(), key=str):
        print(*k, v)
    for k, v in sorted(ex.items(), key=str):
        print("e.g.", *k, " ".join(repr(x) for x in v))
    print("== exposure COMPLETE: items=%d" % len(jobs))


if __name__ == "__main__":
    main()
