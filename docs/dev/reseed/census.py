#!/usr/bin/env python3
"""[OPT-HYB-RESEED] D77 census: which VM-hybrid artifacts does the retry
re-seed decision reach, split by the prefilter language's exactness.

For every corpus `pattern`/`pattern-esc` line (enumerated through
scripts/emit_sweep.py's own --list-source reader), compile with
`--features all -p rx` under each encoding named on the command line and
read the artifact's stamps. For a hybrid (`<P>_VM_PREFILTER "hybrid"`) the
exactness question is the three over-approximation sources the tree names
(src/ir/nfa.c: A_ATOMIC and A_LOOK erase, the count collapse): the kinds
come from `--emit-facts`' `kinds` row, the collapse from
`<P>_VM_PREFILTER_LANG`. `nclamp == 0` is `<P>_VM_PRUNE_CEILING "none"`.

With `--reseed` the artifact's own `<P>_VM_RESEED` stamp is also read and
cross-tabulated, so the same script is the post-build census.

Usage: census.py PCREC_BIN TREE_DIR OUT_TSV [--enc byte,utf8] [--jobs 2]
"""
import argparse, concurrent.futures, os, re, subprocess, sys, tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "scripts"))
import emit_sweep  # noqa: E402

STAMP = re.compile(rb'^#define RX_([A-Z_0-9]+) (.*)$', re.M)


def stamps(c_text):
    return {m.group(1).decode(): m.group(2).decode(errors="replace").strip()
            for m in STAMP.finditer(c_text)}


def one(pcrec, pat, enc, tmp):
    base = ["--features", "all"] + (["-e", enc] if enc != "byte" else [])
    r = subprocess.run([pcrec, "-p", "rx"] + base + ["-o", "-", "--pattern", pat],
                       capture_output=True, timeout=60)
    if r.returncode != 0:
        return None
    st = stamps(r.stdout)
    row = {"engine": st.get("ENGINE", "?").strip('"'),
           "pf": st.get("VM_PREFILTER", "-").strip('"'),
           "lang": st.get("VM_PREFILTER_LANG", "-").strip('"'),
           "ceiling": st.get("VM_PRUNE_CEILING", "-").strip('"'),
           "reseed": st.get("VM_RESEED", "-").strip('"'),
           "dfapf": st.get("DFA_PREFILTER", "-").strip('"'),
           "kinds": "-"}
    if row["pf"] == "hybrid":
        f = subprocess.run([pcrec] + base + ["--emit-facts", "--pattern", pat],
                           capture_output=True, timeout=60)
        for line in f.stdout.decode(errors="replace").splitlines():
            parts = line.split("\t")
            if len(parts) > 6 and parts[1] == "kinds":
                row["kinds"] = parts[6] or "none"
    return row


def exactness(row):
    if row["pf"] != "hybrid":
        return "no-hybrid"
    over = []
    k = row["kinds"]
    if "atomic" in k: over.append("atomic")
    if "lookaround" in k: over.append("look")
    if row["lang"] != "exact": over.append("collapsed")
    return "exact" if not over else "over:" + "+".join(over)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pcrec"); ap.add_argument("tree"); ap.add_argument("out")
    ap.add_argument("--enc", default="byte,utf8")
    ap.add_argument("--jobs", type=int, default=2)
    a = ap.parse_args()
    pats = emit_sweep.enumerate_corpus(a.pcrec, a.tree, 30)
    seen, uniq = set(), []
    for f, kind, p in pats:
        if p in seen: continue
        seen.add(p); uniq.append((f, p))
    work = [(f, p, e) for f, p in uniq for e in a.enc.split(",")]
    rows = []
    with tempfile.TemporaryDirectory() as tmp, \
         concurrent.futures.ThreadPoolExecutor(a.jobs) as ex:
        futs = {ex.submit(one, a.pcrec, p.decode("utf-8", "surrogateescape")
                          if isinstance(p, bytes) else p, e, tmp): (f, p, e)
                for f, p, e in work}
        for fu in concurrent.futures.as_completed(futs):
            f, p, e = futs[fu]
            try: r = fu.result()
            except Exception: r = None
            if r is None: continue
            rows.append((f, e, p, r))
    tab = {}
    with open(a.out, "w", encoding="utf-8", errors="surrogateescape") as o:
        o.write("file\tenc\tengine\tpf\tceiling\texactness\tdfapf\treseed\tpattern\n")
        for f, e, p, r in sorted(rows, key=lambda x: (x[0], x[1], str(x[2]))):
            ex_ = exactness(r)
            cl = "none" if r["ceiling"] == "none" else "clamp"
            ps = p if isinstance(p, str) else p.decode("utf-8", "surrogateescape")
            o.write(f"{f}\t{e}\t{r['engine']}\t{r['pf']}\t{r['ceiling']}\t{ex_}\t"
                    f"{r['dfapf']}\t{r['reseed']}\t{ps!r}\n")
            if r["pf"] == "hybrid":
                key = (e, cl, "exact" if ex_ == "exact" else "over", r["reseed"])
                tab[key] = tab.get(key, 0) + 1
    print(f"compiled rows: {len(rows)} (unique patterns {len(uniq)} x encodings)")
    print("hybrids by (encoding, nclamp, exactness, reseed-stamp):")
    for k in sorted(tab):
        print("  %-6s nclamp=%-5s %-6s reseed=%-18s %6d" % (k[0], k[1], k[2], k[3], tab[k]))


if __name__ == "__main__":
    main()
