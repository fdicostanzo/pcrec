#!/usr/bin/env python3
"""docs/design/dec_fallback/probes_b3.py -- decfb0's attempt-histogram probes
(`../decision_families/decfb0/build_ref.py`'s PATCHES) RE-ANCHORED on the
recovery point as B3 (lane decfbB3) left it: one `fit_walk` dispatch in
place of the five tests (dec_fallback.md §4.2 B3).

A python file defining PATCHES, the shape `attempt_hist.py --child-patches`
/ `--parent-patches` and `cross_record.py` read. Each probe prints THE SAME
LINE AT THE SAME EVENT as decfb0's:

  att    the attempt header -- anchor unchanged by B3, copied verbatim;
  fail   the arrival -- anchor unchanged by B3, copied verbatim;
  sel1   decfb0 printed `collapse=retry_collapse drop=retry_drop` whenever
         either held, on an arrival that was not the force loop's, a K60
         propagation or a size-term trial (the three tests ahead of it).
         B3 deleted those booleans; the probe RESTATES them from the same
         inputs (the arrival's `dfa_overflowed`, the engine, the flags and
         the state the attempt ran under) rather than reading the walk's
         row, so the probe stays independent of the decision it watches.
         The three earlier tests become "the walk did not take row 0-2";
  rung   decfb0 printed the size-cap switch's row on every arrival that got
         past the [SEL-1] block: here, every arrival whose row is none of
         rows 0-4.

Re-verified (decfbB3): the child built with these probes and the parent
built with decfb0's print identical probe sequences over decfb0's population
in every limit variant (`attempt_hist.py --ref <B2> --rev <B3>
--child-patches probes_b3.py`: ATTEMPT HISTOGRAM IDENTICAL).
"""
import os, runpy

_b = runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "../decision_families/decfb0/build_ref.py"))["PATCHES"]
# decfb0's own att/fail probes, whose anchors B3 did not touch
_ATT, _FAIL = _b[0], _b[1]
assert _ATT[0].startswith("        cx.pat = pattern;") and _FAIL[0] == "        if (setjmp(cx.jb)) {\n"

_WALK = "            const FitRung *rung = fit_walk(&fs, fit_labels(&cx));\n"
PATCHES = [
    _ATT,
    _FAIL,
    (_WALK,
     _WALK +
     "            {\n"
     "                const bool ovf_eligible = cx.dfa_overflowed &&\n"
     "                                          defo.engine == PCREC_ENGINE_AUTO &&\n"
     "                                          !(defo.flags & PCREC_FORCE_PREFILTER);\n"
     "                const bool retry_collapse =\n"
     "                    ovf_eligible && !dfa_disabled &&\n"
     "                    !(defo.flags & PCREC_NO_PREFILTER_COLLAPSE);\n"
     "                const bool retry_drop =\n"
     "                    ovf_eligible && !(dfa_disabled && collapse_reason != CR_SEL1);\n"
     "                const bool early = rung->act == FIT_FORCE_NEXT || rung->act == FIT_PROPAGATE ||\n"
     "                                   rung->act == FIT_TERM_NEXT;\n"
     "                if (!early && (retry_collapse || retry_drop))\n"
     "                    fprintf(stderr, \"DECFB sel1 collapse=%d drop=%d\\n\", (int)retry_collapse, (int)retry_drop);\n"
     "                if (!early && rung->act != FIT_SEL1_COLLAPSE && rung->act != FIT_SEL1_DROP)\n"
     "                    fprintf(stderr, \"DECFB rung=%s\\n\", rung->name);\n"
     "            }\n"),
]
