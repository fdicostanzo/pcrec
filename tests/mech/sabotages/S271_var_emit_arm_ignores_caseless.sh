# S271 — [VAR] THE EMIT ARM IGNORES `Ast.u.var.caseless` (src/gen/emit_vm.c,
# `vm_var`): every `${name}` reference routes through the CASE-SENSITIVE seam
# entry, whatever `(?i)` was in force at it.
#
# THIS IS D62 CONTROL 3's ACCEPTED RESIDUAL, PLANTED. `internal.h`'s comment on
# `Ast.u.var.caseless` says it in as many words: "ANY ANALYSIS THAT
# PATTERN-MATCHES `case A_VAR:` AND DOES NOT READ THIS FIELD reproduces
# possessify.c's pre-D62 bug, and no compiler diagnostic will say so." The
# backreference's own sibling row S106 plants exactly this one construct over,
# and this row is what makes that sentence checkable for the new kind rather
# than carried forward on the strength of the old one.
#
# IT IS ANSWER-DETECTABLE, unlike the two precheck-admission rows: a caseless
# variable bound to "abc" stops matching "ABC", which tests/vars/caseless.rxt's
# first block asserts directly. That is why this row's arm is `vars` and its
# figure is a real fail count rather than a structural-section report.
#
# THE PLANT FLIPS THE FIELD READ AND NOTHING ELSE: the seam call still goes
# through `pcrec_enc_entry_engine_callable`, the mask is still OR'd, the work
# charge is still emitted. The ONLY thing the suite sees is which of the two
# residual entries the artifact calls, which is the whole content of D18/D23's
# "an option compiles away" rule at this site.
SAB_ID="S271-var-emit-arm-ignores-caseless"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="vars harness"
SAB_HARNESS_TARGET="tests/vars/caseless.rxt"
SAB_DESC="vm_var stops reading Ast.u.var.caseless, so a caseless \${name} compiles to the CASE-SENSITIVE compare — D62 control 3's accepted residual for this kind, and S106's plant one construct over. A caseless variable bound to 'abc' stops matching 'ABC'"
SAB_DOC_FIGURE="PREDICTED: the 'vars' arm RED — tests/vars/caseless.rxt's caseless blocks fail on every subject carrying the other case (byte and utf8 both, including the KELVIN cell, where the value 'k' stops matching U+212A). The splice oracle inside that same section stays GREEN and that is the point: it splices the value and asks libpcre2 with PCRE2_CASELESS, so it says what the answer SHOULD be while the corpus says what the artifact gives. MEASURED 2026-09-23 at ba6a6c3b (lane varmvp, run solo): DETECTED, reach:ok(1/1), vars:1fail/1pass, corpus:18fail/7pass. The 'vars' arm's own 1fail is the CORPUS arm of that section; its ORACLE arm stays GREEN, which is the point -- the oracle splices the value and asks libpcre2 with PCRE2_CASELESS, so it says what the answer should be while the corpus says what the artifact gives. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S271."
# [MECH-REACH] THE PROBE says the SITE is reached at all: on the clean tree a
# caseless variable reference really does route through the CASELESS entry.
# Without this, a future change that stopped producing `A_VAR` under `(?i)` —
# or stopped emitting the caseless residual — would make this row UNDETECTED
# for a reason that has nothing to do with the field it plants.
#
# RE-POINTED 2026-09-26 (lane s265reach): the emitted caseless span-compare
# was `rx_var_match_caseless` when this probe was written (measured DETECTED
# at ba6a6c3b above) and has since been renamed/generalised to
# `rx_span_match_caseless`, shared with the backreference compare (see the
# 2026-09-23 anchor note below -- the SAME rename this row's own SAB_BEFORE/
# SAB_AFTER already tracks via the PCREC_ENCE_SPAN_CASELESS seam-entry
# constant, unrelated to [OPT-PRECHECK-ADMIT]). The MECHANISM stayed live
# (the emitted `vm_var` body for `(?i)${v}` still calls
# `rx_span_match_caseless`); only this probe's literal grep string was
# stale, and the old string reads `reach:MISSING(1/1)` on main as of
# `5803051b` -- UNREACHED. Verified with the reach command below run
# directly against the built binary.
SAB_REACH='"$PCREC" --features vars,modifiers -p rx -o "$REACH_TMP/o.c" --pattern "(?i)\${v}" && grep -q "rx_span_match_caseless" "$REACH_TMP/o.c" && echo REACH-VAR-CASELESS-ENTRY-EMITTED'
SAB_REACH_EXPECT="REACH-VAR-CASELESS-ENTRY-EMITTED"
SAB_COUNT=1
# [VAR ruling, 2026-09-23] ANCHOR RE-DERIVED FROM THE LIVE SOURCE: the bits
# are the GENERALISED span compare's, shared with the backreference, since the
# manager ruled the sibling entry out. The plant is UNCHANGED in meaning --
# `Ast.u.var.caseless` stops being read and every variable routes through the
# case-SENSITIVE compare.
# [K94] RE-ANCHORED, INTENT UNCHANGED: the caseless arm now names
# `vm_caseless_entry(v, a->u.var.ucp)` (the UCP/plain choice) instead of the
# bare constant; the plant still stops `u.var.caseless` being read.
SAB_BEFORE='    const unsigned seam_entry = a->u.var.caseless
        ? vm_caseless_entry(v, a->u.var.ucp) : PCREC_ENCE_SPAN;'
SAB_AFTER='    const unsigned seam_entry = PCREC_ENCE_SPAN;   /* SABOTAGE S271: the field is not read */'
