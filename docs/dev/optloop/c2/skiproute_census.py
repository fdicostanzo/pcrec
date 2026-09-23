#!/usr/bin/env python3
"""[OPT-FIRSTSET] §4.5 — THE SKIP-ROUTE CENSUS (lane fsreconcile, 2026-09-22).

Answers ONE question, corpus-wide: does any shipped artifact run a
candidate-start SKIP whose result is NOT confirmed by a reverse pass?

`firstset_design.md` §4's soundness finding is about a skip loop that
jumps over bytes carrying the start state's CONTEXT.  Lane `linuxask`
then measured the real two-pass `rx_search` VETOING the spurious forward
accept on §4.1's own witness, which raises the general question this
census answers by COUNTING rather than by argument: the veto exists only
where a reverse pass exists.  Three routes could lack one —

  (a) `RX_DFA_START "pinned"`     the reverse machine is NOT EMITTED
                                  ([OPT-5] STEP 2's elision), so a
                                  forward accept is the answer;
  (b) the VM route's own prefilter (`RX_VM_PREFILTER`), which has no
                                  reverse pass of its own;
  (c) `rx_match`, the anchored entry, which has no skip at all today
                                  (`tests/codegen/run_anchored_match.sh`
                                  §2 already asserts that).

So the census cross-tabs, per compiled artifact: RX_ENGINE ×
RX_DFA_PREFILTER × RX_DFA_START × RX_VM_PREFILTER, plus whether the
emitted text actually CONTAINS a reverse walk and a skip.  It reads the
emitted `.c` — never the pattern, never a claim about what the pass
would do.

Populations: every `pattern`/`pattern-esc` line of every shipped `.rxt`,
via `pcrec --list-source`, decoded through `pcrec_sb_field`'s escape
vocabulary (`reqpos_census.py`'s own `dec_field`, the recorded trap).

Environment
  PCREC   the pcrec build to compile with
  CORPUS  pcrec root (its tests/ tree is walked)
  OUT     output directory (TSV + summary written here)
  JOBS    parallel compiles (default 8)
  FEATURES  --features value (default "all")
"""
import os, sys, subprocess, tempfile, json, collections
import concurrent.futures as cf

E = os.environ
OUT = E.get("OUT", ".")
JOBS = int(E.get("JOBS", "8"))
FEATURES = E.get("FEATURES", "all")

def dec_field(b: bytes) -> bytes:
    """`pcrec_sb_field`'s escape vocabulary, inverted (src/core/sb.c)."""
    out = bytearray(); i = 0
    while i < len(b):
        c = b[i]
        if c == 0x5c and i + 1 < len(b):
            n = b[i+1]
            if n == 0x5c: out.append(0x5c); i += 2; continue
            if n == 0x74: out.append(9);    i += 2; continue
            if n == 0x6e: out.append(10);   i += 2; continue
            if n == 0x72: out.append(13);   i += 2; continue
            if n == 0x78 and i + 3 < len(b):
                try: out.append(int(b[i+2:i+4], 16)); i += 4; continue
                except ValueError: pass
        out.append(c); i += 1
    return bytes(out)

def corpus_pop():
    rows, files = [], []
    for root, _d, fs in os.walk(os.path.join(E["CORPUS"], "tests")):
        for f in fs:
            if f.endswith(".rxt"): files.append(os.path.join(root, f))
    for f in sorted(files):
        r = subprocess.run([E["PCREC"], "--list-source", f],
                           capture_output=True, timeout=120)
        if r.returncode != 0: continue
        rel = os.path.relpath(f, E["CORPUS"])
        for ln in r.stdout.split(b"\n"):
            if not ln or ln.startswith(b"#"): continue
            fl = ln.split(b"\t")
            if len(fl) < 5: continue
            if fl[0] not in (b"pattern", b"pattern-esc"): continue
            pat = dec_field(fl[4])
            if not pat or b"\x00" in pat: continue
            rows.append(("%s:%s" % (rel, fl[1].decode()), pat))
    return rows

STAMPS = ("RX_ENGINE", "RX_DFA_PREFILTER", "RX_DFA_START", "RX_VM_PREFILTER",
          "RX_DFA_SCAN", "RX_ENGINE_SEL")

def one(arg):
    """Compile one pattern; read its stamps and two TEXT facts off the .c."""
    ident, pat = arg
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "a.c")
        r = subprocess.run([E["PCREC"], "--features", FEATURES, "-p", "rx",
                            "-o", out, "--pattern", pat.decode("latin-1")],
                           capture_output=True, timeout=120)
        if r.returncode != 0 or not os.path.exists(out):
            return {"id": ident, "status": "refused"}
        src = open(out, "r", errors="replace").read()
    rec = {"id": ident, "status": "ok"}
    for s in STAMPS:
        v = ""
        for ln in src.split("\n"):
            if ln.startswith("#define %s " % s):
                v = ln.split(" ", 2)[2].strip().strip('"'); break
        rec[s] = v
    # TEXT facts, read off the emitted artifact rather than inferred:
    rec["has_skip"] = int(("_can_begin_match[subject[scan_position]]" in src)
                          or ("memchr(subject + scan_position" in src)
                          or ("_ofsskip(" in src))
    # `match_start_position` ALONE is the reverse walk's own variable.  An
    # earlier draft also required `_reverse_next_state`, which is a FALSE
    # NEGATIVE on any artifact whose reverse transition table is uniform and
    # folded away ([CC-DIFF] STEP 1's `RX_DFA_UNIFORM_FOLDS`) -- 84 corpus
    # rows read "skip without reverse" for that reason and every one of them
    # stamped `RX_DFA_START "reverse-pass"`.
    rec["has_reverse"] = int("match_start_position" in src)
    # A SEEDED start state is what the skip can lose: the machine tracks the
    # class of the byte to its left, so `<p>_forward_seed_state[` is emitted
    # (`dfa_needs_seed`).  This is the population `[OPT-FIRSTSET]`'s narrowing
    # would actually change the answer of.
    rec["has_seed"] = int("_forward_seed_state[" in src)
    rec["has_reseed"] = int("_ofsskip(" in src and "_seed_state[" in src)
    return rec

def main():
    rows = corpus_pop()
    sys.stderr.write("corpus pattern lines: %d\n" % len(rows))
    recs = []
    with cf.ThreadPoolExecutor(max_workers=JOBS) as ex:
        for i, rec in enumerate(ex.map(one, rows)):
            recs.append(rec)
            if i % 250 == 0: sys.stderr.write("  %d\n" % i)
    cols = ["id", "status"] + list(STAMPS) + ["has_skip", "has_reverse", "has_seed", "has_reseed"]
    with open(os.path.join(OUT, "skiproute_census.tsv"), "w") as f:
        f.write("# [OPT-FIRSTSET] §4.5 skip-route census, lane fsreconcile.\n")
        f.write("# One row per shipped .rxt pattern line compiled at --features %s, -p rx.\n" % FEATURES)
        f.write("# has_skip/has_reverse/has_reseed are read off the EMITTED .c text.\n")
        f.write("\t".join(cols) + "\n")
        for r in recs:
            f.write("\t".join(str(r.get(c, "")) for c in cols) + "\n")
    ok = [r for r in recs if r["status"] == "ok"]
    summ = {
        "pattern_lines": len(rows),
        "compiled": len(ok),
        "refused": len(recs) - len(ok),
        "skip_and_no_reverse": sum(1 for r in ok if r["has_skip"] and not r["has_reverse"]),
        "skip_total": sum(1 for r in ok if r["has_skip"]),
        "reverse_total": sum(1 for r in ok if r["has_reverse"]),
        "by_start_x_prefilter": collections.Counter(
            "%s|%s|%s" % (r["RX_ENGINE"], r["RX_DFA_PREFILTER"], r["RX_DFA_START"]) for r in ok),
        "skip_no_reverse_rows": [r["id"] for r in ok if r["has_skip"] and not r["has_reverse"]][:50],
        "vm_prefilter_values": collections.Counter(r["RX_VM_PREFILTER"] for r in ok),
        # THE REACH: a skip loop over a SEEDED machine is exactly where the
        # narrowing changes an answer.  Split by whether the consumer is the
        # plain DFA search or a VM hybrid's inlined prefilter.
        "skip_and_seed": sum(1 for r in ok if r["has_skip"] and r["has_seed"]),
        "skip_and_seed_dfa": sum(1 for r in ok if r["has_skip"] and r["has_seed"]
                                 and r["RX_ENGINE"] == "dfa"),
        "skip_and_seed_vm_hybrid": sum(1 for r in ok if r["has_skip"] and r["has_seed"]
                                       and r["RX_VM_PREFILTER"] == "hybrid"),
        "pinned_with_prefilter": sum(1 for r in ok if r["RX_DFA_START"] == "pinned"
                                     and r["RX_DFA_PREFILTER"] not in ("none", "")),
        "pinned_total": sum(1 for r in ok if r["RX_DFA_START"] == "pinned"),
    }
    summ["by_start_x_prefilter"] = dict(summ["by_start_x_prefilter"])
    summ["vm_prefilter_values"] = dict(summ["vm_prefilter_values"])
    json.dump(summ, open(os.path.join(OUT, "skiproute_summary.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in summ.items() if k != "skip_no_reverse_rows"}, indent=1))
    print("skip-without-reverse sample:", summ["skip_no_reverse_rows"][:10])

main()
