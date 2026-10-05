#!/usr/bin/env python3
"""[START-SET] rev 2: the start-byte oracle over the VM hat's populations
(review r4 checks-F2 (b): an expectation from OUTSIDE the walk that reaches
the VM-only arms -- A_BREF, A_CALL, A_VAR, the zero-width set).

For every census row the V predicate admits (unanchored, S non-nullable,
|S| < 256) on the given route (`auto`: the vm-none artifacts; `vm`: under
--engine=vm), it compiles the artifact, runs every subject over a per-row
alphabet (S's members first, then the pattern's own alnum bytes, then one
byte outside S) up to a per-row length at every startpos, and checks that
every byte that begins a non-empty match under the artifact or local
libpcre2 (10.48) is in S.  A pattern carrying \\K is skipped (its reported
start is not its attempt start).

    vmoracle.py CENSUS_TSV OUT_TSV auto|vm        Env: PCREC, W, JOBS, PCRE2
"""
import csv, itertools, os, subprocess, sys, concurrent.futures as cf
HERE = os.path.dirname(os.path.abspath(__file__))
PCREC = os.environ["PCREC"]; W = os.environ["W"]; JOBS = int(os.environ.get("JOBS", "6")); P2 = os.environ.get("PCRE2", "/opt/homebrew")

def bits(h):
    b = bytes.fromhex(h); return {i for i in range(256) if b[i >> 3] >> (i & 7) & 1}
def esc(t): return "".join(chr(c) if 0x20 <= c < 0x7f and c != 0x5c else "\\x%02x" % c for c in t)

def run(job):
    i, r, route = job
    d = os.path.join(W, "v%d" % i); os.makedirs(d, exist_ok=True)
    pat = bytes.fromhex(r["pat_hex"]); S = bits(r["fs_set"])
    extra = (["-e", "utf8"] if r["set"] == "utf8" else []) + (["--engine=vm"] if route == "vm" else [])
    o = {"kind": r["kind"], "name": r["name"], "S": len(S)}
    if b"\\K" in pat: o["status"] = "skip-K"; return o
    if subprocess.run([PCREC, "--features", "all", *extra, "-p", "rx", "-o", os.path.join(d, "rx.c"), "--pattern", pat], capture_output=True).returncode:
        o["status"] = "refused"; return o
    alpha = []
    for b in sorted(S, key=lambda b: (not (0x20 < b < 0x7f), b))[:3] + list(pat) + [b for b in (0x20, 0x0a, 0x7e, 0x01) if b not in S][:1]:
        if b not in alpha and len(alpha) < 6 and (b in S or (0x20 < b < 0x7f and chr(b).isalnum()) or b in (0x20, 0x0a, 0x7e, 0x01)): alpha.append(b)
    L = 7 if len(alpha) <= 4 else 6 if len(alpha) <= 5 else 5
    cc = ["gcc-16", "-O1", "-w", "-I" + d, "-o", os.path.join(d, "drv"), os.path.join(HERE, "drv_obs.c"), os.path.join(d, "rx.c")]
    if subprocess.run(cc[:-2] + ["-DWITH_PCRE2", "-I" + P2 + "/include"] + cc[-2:] + ["-L" + P2 + "/lib", "-lpcre2-8"], capture_output=True).returncode:
        subprocess.run(cc, check=True)
    subj = "".join(esc(bytes(t)) + "\n" for n in range(L + 1) for t in itertools.product(alpha, repeat=n))
    res = subprocess.run([os.path.join(d, "drv"), pat, "utf8" if r["set"] == "utf8" else "byte"], input=subj, capture_output=True, text=True, timeout=600)
    last = res.stdout.strip().splitlines()[-1]
    if "pcre2 compile fail" in last:
        subprocess.run(cc, check=True); last = subprocess.run([os.path.join(d, "drv")], input=subj, capture_output=True, text=True, timeout=600).stdout.strip().splitlines()[-1]
    kv = dict(x.split("=", 1) for x in last.split())
    ob, pob = bits(kv["obs"]), bits(kv["pobs"])
    o.update(status="ok", alpha=",".join("%02x" % b for b in alpha), L=L, cases=kv["cases"], matches=kv["matches"], giveups=kv["giveups"],
             pcre2_vs_base=kv["pcre2_vs_base"], obs=len(ob | pob), viol_base=",".join("%02x" % b for b in sorted(ob - S)),
             viol_pcre2=",".join("%02x" % b for b in sorted(pob - S)))
    for f in ("rx.c", "rx.h", "drv"):
        try: os.remove(os.path.join(d, f))
        except OSError: pass
    return o

def main():
    census, outp, route = sys.argv[1:4]
    rows = [r for r in csv.DictReader((l for l in open(census) if not l.startswith("# ")), delimiter="\t")]
    eng, pf = ("a_RX_ENGINE", "a_RX_VM_PREFILTER") if route == "auto" else ("v_RX_ENGINE", "v_RX_VM_PREFILTER")
    pop = [r for r in rows if r["status"] == "ok" and r[eng] == "vm" and r[pf] != "hybrid" and r["start_anchor"] in ("unanchored", "")
           and r["fs_nullable"] == "0" and r["fs_set"] and len(bits(r["fs_set"])) < 256]
    with cf.ThreadPoolExecutor(JOBS) as ex: res = list(ex.map(run, [(i, r, route) for i, r in enumerate(pop)]))
    keys = ["kind", "name", "status", "S", "alpha", "L", "cases", "matches", "giveups", "pcre2_vs_base", "obs", "viol_base", "viol_pcre2"]
    with open(outp, "w") as f:
        f.write("# [START-SET] rev 2 vmoracle.py route=%s\n" % route + "\t".join(keys) + "\n")
        for o in res: f.write("\t".join(str(o.get(k, "")) for k in keys) + "\n")
    ok = [o for o in res if o.get("status") == "ok"]
    print("route=%s rows=%d ok=%d skipped=%s cells=%d matches=%d rows_reaching_a_match=%d start_byte_violations(base)=%d (pcre2)=%d pcre2_vs_base_rows=%d" % (
        route, len(res), len(ok), dict(__import__("collections").Counter(o["status"] for o in res if o.get("status") != "ok")),
        sum(int(o["cases"]) for o in ok), sum(int(o["matches"]) for o in ok), sum(int(o["matches"]) > 0 for o in ok),
        sum(bool(o["viol_base"]) for o in ok), sum(bool(o["viol_pcre2"]) for o in ok), sum(o["pcre2_vs_base"] != "0" for o in ok)))

main()
