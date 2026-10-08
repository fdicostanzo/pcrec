#!/usr/bin/env python3
"""[DEC-FALLBACK] rev 2: build the row-reach PROTOTYPE compilers.

The design's B1 row_reach instrument reads the B1 trace; that trace does not
exist before B1, so this prototype reads probes instead, decfb0's method
(../../decision_families/decfb0/build_ref.py) widened. It copies src/ lib/
cli/ memfn/ into SCRATCH/tree, patches ONLY the copy's compile.c and
select_engine.c with stderr `DECFB` probes, and builds one compiler per
limit variant. Probes:

  att    attempt header: dd, CR, SDR, st_phase
  fail   one arrival: the labels (ovf, scr, nomem), pf.forcing, st_phase,
         and the refused attempt's fit (pcoll, pf, chosen)
  forcing / nomem / trial   which of the three tests ahead of the ladder took it
  sel1   the [SEL-1] block's verdict
  rung   the size-cap walk's row (`refuse` included, whatever the label)
  adm    the prefilter admission's inputs and its verdict, every attempt
  gate   the collapse gate's verdict and PFLW, every attempt that reaches it

Probes write stderr only; reach.py asserts the plain variant's stdout and rc
identical to the unprobed build/pcrec. Nothing under src/ is modified.
usage: build_reach.py SCRATCH_DIR [VARIANT...]   (default: every variant)
"""
import os, shutil, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
VARIANTS = {
    "plain":   [],
    "lowsize": ["-DPCREC_MAX_VM_EMIT_CODE_BYTES=30000", "-DPCREC_MAX_EMIT_BYTES=60000",
                "-DPCREC_SIZE_TERM_THRESHOLD=10000"],
    "lowdfa":  ["-DPCREC_MAX_AUTO_DFA_ELEMS=3000"],
    "lowboth": ["-DPCREC_MAX_VM_EMIT_CODE_BYTES=30000", "-DPCREC_MAX_EMIT_BYTES=60000",
                "-DPCREC_SIZE_TERM_THRESHOLD=10000", "-DPCREC_MAX_AUTO_DFA_ELEMS=3000"],
    # the size term's threshold only (run_size_term.sh §7's reference
    # compiler): the one variant `capacity-declined` has a population in
    "lowthr":  ["-DPCREC_SIZE_TERM_THRESHOLD=1000"],
}

CP = "src/core/compile.c"
SE = "src/opt/select_engine.c"
PATCHES = [
    (CP, "        cx.pat = pattern;\n        cx.patlen = pattern ? strlen(pattern) : 0;\n",
     "        cx.pat = pattern;\n        cx.patlen = pattern ? strlen(pattern) : 0;\n"
     "        fprintf(stderr, \"DECFB att=%d dd=%d cr=%d sdr=%d stph=%d\\n\", (int)attempt,\n"
     "                (int)dfa_disabled, (int)collapse_reason, (int)size_drop_rung, (int)st_phase);\n"),
    (CP, "        if (setjmp(cx.jb)) {\n",
     "        if (setjmp(cx.jb)) {\n"
     "            fprintf(stderr, \"DECFB fail ovf=%d scr=%d nomem=%d forcing=%d stph=%d pcoll=%d pf=%d chosen=%d\\n\",\n"
     "                    (int)cx.dfa_overflowed, (int)cx.size_cap_refused, (int)cx.failed_nomem,\n"
     "                    (cx.job && cx.job->pf.forcing) ? 1 : 0, (int)st_phase,\n"
     "                    cx.job ? (int)cx.job->fit.prefilter_collapsed : -1,\n"
     "                    cx.job ? (int)cx.job->fit.prefilter : -1,\n"
     "                    cx.job ? (int)cx.job->fit.chosen : -1);\n"),
    (CP, "            if (cx.job && cx.job->pf.forcing) {\n",
     "            if (cx.job && cx.job->pf.forcing) {\n"
     "                fprintf(stderr, \"DECFB forcing\\n\");\n"),
    (CP, "            if (cx.failed_nomem) {\n",
     "            if (cx.failed_nomem) {\n"
     "                fprintf(stderr, \"DECFB nomem\\n\");\n"),
    (CP, "            if (st_phase == ST_LADDER) {\n                int final_k",
     "            if (st_phase == ST_LADDER) {\n"
     "                fprintf(stderr, \"DECFB trial\\n\");\n"
     "                int final_k"),
    (CP, "            if (retry_collapse || retry_drop) {\n",
     "            if (retry_collapse || retry_drop)\n"
     "                fprintf(stderr, \"DECFB sel1 collapse=%d drop=%d\\n\", (int)retry_collapse, (int)retry_drop);\n"
     "            if (retry_collapse || retry_drop) {\n"),
    (CP, "            bool restart_term = false;\n            switch (rung->act) {\n",
     "            bool restart_term = false;\n"
     "            fprintf(stderr, \"DECFB rung=%s\\n\", rung->name);\n"
     "            switch (rung->act) {\n"),
    (CP, "            cx.job->fit.prefilter_collapsed = collapse;\n",
     "            cx.job->fit.prefilter_collapsed = collapse;\n"
     "            fprintf(stderr, \"DECFB gate wanted=%d collapse=%d pflw=%d rep=%d nul=%d force=%d\\n\",\n"
     "                    (int)pfc_wanted, (int)collapse, (int)cx.job->fit.prefilter_lang_why,\n"
     "                    (int)pfc_rep, (int)pcrec_fact_nullable(&cx), (int)pfc_force);\n"),
    (SE, "                   : would_prefilter;\n}\n",
     "                   : would_prefilter;\n"
     "    fprintf(stderr, \"DECFB adm bref=%d call=%d var=%d dd=%d cr=%d nul=%d ea=%d crep=%d fon=%d foff=%d wp=%d pf=%d dnd=%d dn=%d\\n\",\n"
     "            (int)has_bref, (int)has_call, (int)has_var, (int)cx->dfa_disabled, (int)cx->collapse_reason,\n"
     "            (int)pcrec_fact_nullable(cx), (int)pcrec_fact_empty_admits(cx), (int)collapsible_rep,\n"
     "            (int)force_on, (int)force_off, (int)would_prefilter, (int)fit->prefilter,\n"
     "            (int)fit->prefilter_declined_nullable_default, (int)fit->prefilter_declined_nullable);\n"
     "}\n"),
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
    for f, a, r in PATCHES:
        p = os.path.join(tree, f)
        s = open(p).read()
        assert s.count(a) == 1, "anchor drifted (%s): %r" % (f, a[:60])
        open(p, "w").write(s.replace(a, r))
    se = os.path.join(tree, SE)
    s = open(se).read()
    if "#include <stdio.h>" not in s:
        open(se, "w").write("#include <stdio.h>\n" + s)
    srcs = subprocess.check_output(
        "find %s/src %s/memfn/src -name '*.c' 2>/dev/null | LC_ALL=C sort" % (tree, tree),
        shell=True, text=True).split()
    want = sys.argv[2:] or list(VARIANTS)
    for name, defs in VARIANTS.items():
        if name not in want:
            continue
        out = os.path.join(scratch, "pcrec_" + name)
        cmd = ["gcc", "-O1", "-std=gnu11", "-I" + tree + "/lib", "-I" + tree + "/src"] + defs + \
              ["-o", out, tree + "/cli/main.c"] + srcs
        subprocess.check_call(cmd)
        print("built", out)

main()
