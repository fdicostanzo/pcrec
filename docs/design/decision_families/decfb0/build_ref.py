#!/usr/bin/env python3
"""[DEC-FALLBACK] STEP 0: build the scratch census compilers.

Copies src/ lib/ cli/ memfn/ into SCRATCH/tree, patches ONLY the copy's
src/core/compile.c with stderr `DECFB` probes (attempt header, failure
arrival, rung taken), then builds one compiler per variant:

  plain  shipped limits (probes only)
  <name> -D lowered limits, variants in VARIANTS below

The probes write stderr only; the emitted bytes are asserted identical to the
unprobed build/pcrec by census.py's --check-bytes. Nothing under src/ is
modified. usage: build_ref.py SCRATCH_DIR
"""
import os, shutil, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
VARIANTS = {
    "plain": [],
    # emitted-size caps lowered (run_size_term.sh's shape): size-cap ladder
    "lowsize": ["-DPCREC_MAX_VM_EMIT_CODE_BYTES=30000", "-DPCREC_MAX_EMIT_BYTES=60000",
                "-DPCREC_SIZE_TERM_THRESHOLD=10000"],
    # DFA work budget lowered (run_n1_budget.sh's shape): [SEL-1] overflow ladder
    "lowdfa": ["-DPCREC_MAX_AUTO_DFA_ELEMS=3000"],
    # both
    "lowboth": ["-DPCREC_MAX_VM_EMIT_CODE_BYTES=30000", "-DPCREC_MAX_EMIT_BYTES=60000",
                "-DPCREC_SIZE_TERM_THRESHOLD=10000", "-DPCREC_MAX_AUTO_DFA_ELEMS=3000"],
}

PATCHES = [
    # (anchor, replacement-with-anchor)
    ("        cx.pat = pattern;\n        cx.patlen = pattern ? strlen(pattern) : 0;\n",
     "        cx.pat = pattern;\n        cx.patlen = pattern ? strlen(pattern) : 0;\n"
     "        fprintf(stderr, \"DECFB att=%d dd=%d cr=%d sdr=%d stph=%d\\n\", (int)attempt,\n"
     "                (int)dfa_disabled, (int)collapse_reason, (int)size_drop_rung, (int)st_phase);\n"),
    ("        if (setjmp(cx.jb)) {\n",
     "        if (setjmp(cx.jb)) {\n"
     "            fprintf(stderr, \"DECFB fail ovf=%d scr=%d pcoll=%d pf=%d chosen=%d\\n\",\n"
     "                    (int)cx.dfa_overflowed, (int)cx.size_cap_refused,\n"
     "                    cx.job ? (int)cx.job->fit.prefilter_collapsed : -1,\n"
     "                    cx.job ? (int)cx.job->fit.prefilter : -1,\n"
     "                    cx.job ? (int)cx.job->fit.chosen : -1);\n"),
    ("            if (retry_collapse || retry_drop) {\n",
     "            if (retry_collapse || retry_drop)\n"
     "                fprintf(stderr, \"DECFB sel1 collapse=%d drop=%d\\n\", (int)retry_collapse, (int)retry_drop);\n"
     "            if (retry_collapse || retry_drop) {\n"),
    ("            bool restart_term = false;\n            switch (rung->act) {\n",
     "            bool restart_term = false;\n"
     "            fprintf(stderr, \"DECFB rung=%s\\n\", rung->name);\n"
     "            switch (rung->act) {\n"),
]

def main():
    scratch = os.path.abspath(sys.argv[1])
    tree = os.path.join(scratch, "tree")
    if os.path.exists(tree):
        shutil.rmtree(tree)
    os.makedirs(tree)
    for d in ("src", "lib", "cli", "memfn"):
        shutil.copytree(os.path.join(ROOT, d), os.path.join(tree, d),
                        ignore=shutil.ignore_patterns("*.o"))
    cp = os.path.join(tree, "src/core/compile.c")
    s = open(cp).read()
    for a, r in PATCHES:
        assert s.count(a) == 1, "anchor drifted: " + a[:50]
        s = s.replace(a, r)
    open(cp, "w").write(s)
    srcs = subprocess.check_output(
        "find %s/src %s/memfn/src -name '*.c' 2>/dev/null | LC_ALL=C sort" % (tree, tree),
        shell=True, text=True).split()
    for name, defs in VARIANTS.items():
        out = os.path.join(scratch, "pcrec_" + name)
        cmd = ["gcc", "-O1", "-std=gnu11", "-I" + tree + "/lib", "-I" + tree + "/src"] + defs + \
              ["-o", out, tree + "/cli/main.c"] + srcs
        subprocess.check_call(cmd)
        print("built", out)

if __name__ == "__main__":   # dec_fallback/attempt_hist.py imports PATCHES
    main()
