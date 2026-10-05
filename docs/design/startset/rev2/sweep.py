#!/usr/bin/env python3
"""[START-SET] rev 2: the DFA hat's seeded-machine sweep (review r4 sound-F1,
sound-F2, checks-F2).  For every census row whose auto artifact is a SEEDED
DFA or hybrid machine with a byte-class skip (the only skip form a new row can
replace with a narrower table; memchr rows have |E| = 1 and cannot narrow), it
compiles the artifact, reads E / E* / Tdfa off its tables (estar.py), builds
four narrowed+re-seeded twins (patch.py):

  cur  T = S & E      (the r3 note's §2 F -- the defect)
  a    T = S & E*     (option a)
  b    T = S          (option b)
  dfa  T = Tdfa       (the machine's own floor; a control, not an option)

and runs drv5.c over every subject on a per-row alphabet up to a per-row
length, every startpos, the full capture vector, with local libpcre2 (10.48,
NOT the 10.46 reference) as a third arm and the START-BYTE ORACLE.

It reports, per row: the sets' sizes, the STATIC check Tdfa <= T per option,
the ORACLE check (every byte that begins a non-empty match under base or
libpcre2 is in T) per option, the differential diffs per option, and each
option's admission (mover) verdict.

    sweep.py CENSUS_TSV OUT_TSV [ROW_FILTER_SUBSTRING ...]
Env: PCREC (the compiler), W (scratch dir), JOBS (default 4), PCRE2 (prefix,
default /opt/homebrew), and ALPHA/MAXLEN to override the per-row alphabet
(comma-separated hex) and length for a single filtered row.
"""
import csv, itertools, json, os, subprocess, sys, concurrent.futures as cf

HERE = os.path.dirname(os.path.abspath(__file__))
PCREC = os.environ["PCREC"]; W = os.environ["W"]; JOBS = int(os.environ.get("JOBS", "4"))
P2 = os.environ.get("PCRE2", "/opt/homebrew")

def bits(h):
    b = bytes.fromhex(h); return {i for i in range(256) if b[i >> 3] >> (i & 7) & 1}

def alphabet(st, S, pat):
    E, cls = set(st["E"]), st["fwd_class"]
    pick = []
    def add(b):
        if b not in pick and len(pick) < 7: pick.append(b)
    pref = lambda xs: sorted(xs, key=lambda b: (not (0x20 < b < 0x7f), b != 10, b))
    for b in pref(S - E)[:2]: add(b)
    seen = {cls[b] for b in pick}
    for b in pref(S & E) + pref(set(range(256)) - S):
        if cls[b] not in seen: add(b); seen.add(cls[b])
    for b in pat:
        if 0x20 < b < 0x7f and chr(b).isalnum(): add(b)
    return pick

def esc(t):
    return "".join(chr(c) if 0x20 <= c < 0x7f and c != 0x5c else "\\x%02x" % c for c in t)

def run_row(job):
    i, r, alpha_over, L_over = job
    d = os.path.join(W, "row%d" % i); os.makedirs(d, exist_ok=True)
    pat = bytes.fromhex(r["pat_hex"]); extra = ["-e", "utf8"] if r["set"] == "utf8" else []
    out = {"kind": r["kind"], "name": r["name"], "route": "hybrid" if r["a_RX_VM_PREFILTER"] == "hybrid" else r["a_RX_ENGINE"]}
    for p in ("rx", "c_", "a_", "b_", "d_"):
        c = subprocess.run([PCREC, "--features", "all", *extra, "-p", p, "-o", os.path.join(d, p + ".c"), "--pattern", pat], capture_output=True)
        if c.returncode: out["status"] = "refused"; return out
    st = json.loads(subprocess.run([sys.executable, os.path.join(HERE, "estar.py"), os.path.join(d, "rx.c"), "rx", r["fs_set"]], capture_output=True, text=True, check=True).stdout)
    if st["status"] != "ok": out["status"] = st["status"]; return out
    assert st["cbm_agrees"], "can_begin_match != state 0's escape set"
    S, E, Es, Td = set(st["S"]), set(st["E"]), set(st["Estar"]), set(st["Tdfa"])
    T = {"cur": S & E, "a": S & Es, "b": S, "dfa": Td}
    for p, k in (("c_", "cur"), ("a_", "a"), ("b_", "b"), ("d_", "dfa")):
        subprocess.run([sys.executable, os.path.join(HERE, "patch.py"), os.path.join(d, p + ".c"), p, ",".join(map(str, sorted(T[k])))], check=True)
    alpha = [int(x, 16) for x in alpha_over.split(",")] if alpha_over else alphabet(st, S, pat)
    L = int(L_over) if L_over else (7 if len(alpha) <= 4 else 6 if len(alpha) <= 6 else 5)
    srcs = [os.path.join(d, p + ".c") for p in ("rx", "c_", "a_", "b_", "d_")]
    cc = ["gcc-16", "-O1", "-w", "-I" + d, "-o", os.path.join(d, "drv"), os.path.join(HERE, "drv5.c"), *srcs]
    p2 = subprocess.run(cc[:-6] + ["-DWITH_PCRE2", "-I" + P2 + "/include"] + cc[-6:] + ["-L" + P2 + "/lib", "-lpcre2-8"], capture_output=True)
    if p2.returncode: subprocess.run(cc, check=True)
    subj = "".join(esc(bytes(t)) + "\n" for n in range(L + 1) for t in itertools.product(alpha, repeat=n))
    mode = "utf8" if extra else "byte"
    res = subprocess.run([os.path.join(d, "drv"), pat, mode], input=subj, capture_output=True, text=True)
    last = res.stdout.strip().splitlines()[-1] if res.stdout.strip() else ""
    if "pcre2 compile fail" in last:     # pcrec-only syntax: rebuild without the libpcre2 arm
        subprocess.run(cc, check=True); res = subprocess.run([os.path.join(d, "drv")], input=subj, capture_output=True, text=True)
        last = res.stdout.strip().splitlines()[-1]
    kv = dict(x.split("=", 1) for x in last.split())
    obs = bits(kv["obs"]) | bits(kv["pobs"])
    out.update(status="ok", alpha=",".join("%02x" % b for b in alpha), L=L, cases=int(kv["cases"]), matches=int(kv["matches"]),
               pcre2_vs_base=kv.get("pcre2_vs_base", "n/a"), E=len(E), S=len(S), Estar=len(Es), Tdfa=len(Td), S_minus_E=len(S - E),
               obs=len(obs), witness=" | ".join(l.strip() for l in res.stdout.splitlines()[:-1][:4]))
    for k in ("cur", "a", "b", "dfa"):
        out["T_" + k] = len(T[k]); out["diffs_" + k] = int(kv[k + "_diffs"])
        out["static_ok_" + k] = int(Td <= T[k]); out["oracle_ok_" + k] = int(obs <= T[k])
    # admission (mover) verdicts; S is a necessary condition on every row here (fs_nullable 0, |S| < 256)
    out["mover_cur"] = int(bool(T["cur"]) and T["cur"] < E)                 # the r3 note's F
    out["mover_a_sub"] = int(bool(T["a"]) and T["a"] < E)                   # (a), admitted only as a proper subset of E
    out["mover_a_card"] = int(bool(T["a"]) and len(T["a"]) < len(E))        # (a), admitted on |T| < |E|
    out["mover_b_sub"] = int(bool(S) and S < E)                             # (b), proper subset
    out["mover_b_card"] = int(bool(S) and len(S) < len(E))                  # (b), |S| < |E|
    out["mover_c"] = int(S <= E and bool(S & E) and (S & E) < E)            # (c): decline when S not <= E
    return out

def main():
    census, outp, filt = sys.argv[1], sys.argv[2], sys.argv[3:]
    rows = [r for r in csv.DictReader((l for l in open(census) if not l.startswith("# ")), delimiter="\t")]
    pop = [r for r in rows if r["status"] == "ok" and r["seeded"] == "1" and r["a_RX_DFA_PREFILTER"] in ("byte-class", "byte-class-bounded")
           and r["fs_nullable"] == "0" and r["fs_set"] and len(bits(r["fs_set"])) < 256]
    if filt: pop = [r for r in pop if any(f in r["name"] for f in filt)]
    jobs = [(i, r, os.environ.get("ALPHA"), os.environ.get("MAXLEN")) for i, r in enumerate(pop)]
    with cf.ThreadPoolExecutor(JOBS) as ex: res = list(ex.map(run_row, jobs))
    keys = []
    for o in res:
        for k in o:
            if k not in keys: keys.append(k)
    with open(outp, "w") as f:
        f.write("\t".join(keys) + "\n")
        for o in res: f.write("\t".join(str(o.get(k, "")) for k in keys) + "\n")
    print("rows", len(res), "ok", sum(o.get("status") == "ok" for o in res))

main()
