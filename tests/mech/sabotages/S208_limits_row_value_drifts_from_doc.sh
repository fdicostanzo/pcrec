# S208 (D90/[LIM-1]) — A TABLE ROW'S VALUE IS EDITED AND docs/spec/limits.md
# IS NOT, AND THE DERIVATION CHECK IS THE ONLY THING THAT NOTICES.
#
# WHAT IT BREAKS. `src/core/limits.def`'s `PCREC_MAX_VM_EMIT_CODE_BYTES` row
# moves 500000 -> 400000. Nothing else in the tree names this number by
# hand — `src/core/limits.h` GENERATES its `#ifndef`-guarded default from
# this exact row (the [LIM-1] refactor's whole point), and every call site
# that used to read the literal `500000` now reads the generated symbol —
# so the COMPILER agrees with itself: `pcrec --list-limits` faithfully
# reports 400000, and the artifact-size cap the compiler actually ENFORCES
# moves with it. The one thing that goes silently wrong is
# `docs/spec/limits.md` §8, which still says "500,000" (the CALLER-FACING
# PROMISE): a caller reading the spec is now told a number the shipped
# compiler does not honour.
#
# WHY NOTHING ELSE IN THE TREE CAN SEE IT. The corpus, `make test-axes`,
# every identity gate and every differential all compile against WHATEVER
# `PCREC_MAX_VM_EMIT_CODE_BYTES` currently is — a lower cap can only refuse
# MORE, and nothing in the standing corpus sits within 100x of either
# 400000 or 500000 (docs/spec/limits.md §8's own "measured empty band"
# paragraph), so `tests/codegen/run_size_term.sh`'s cells, which probe the
# cap directly with a `-D`-lowered REFERENCE compiler, never notice the
# SHIPPED default moved — they build their own reference regardless of
# what limits.def says. This is a purely TEXTUAL drift between two
# documents (the table and the doc), and `tests/registry/limits_check.sh`
# part 2 (dump vs. docs/spec/limits.md §3/§8, forward direction) is the one
# instrument in the tree that reads both.
#
# THE PLANT IS THE ROW'S VALUE ONLY, never limits.md — the whole point is
# that limits.md is left EXACTLY as a correctly-landed [LIM-1] would leave
# it (matching the value the table had before this row existed), so the
# check's job is to notice that the two no longer agree, not to notice that
# either one individually looks wrong.
SAB_ID="S208-limits-row-value-drifts-from-doc"
SAB_FILE="src/core/limits.def"
SAB_SUITES="limits"
SAB_DESC="src/core/limits.def's PCREC_MAX_VM_EMIT_CODE_BYTES row is edited from 500000 to 400000 with docs/spec/limits.md left unchanged (still '500,000') -- the compiler, --list-limits and every runtime check agree with the NEW number by construction (one derivation), so only a doc-vs-table check can see the two documents disagree"
SAB_DOC_FIGURE="PREDICTED: limits:1fail (part 2's PCREC_MAX_VM_EMIT_CODE_BYTES row: 'value 400000 (400,000) NOT found in limits.md section 8'). Every other suite this row could plausibly touch (harness, codegen, sizeterm, registry) is expected 0fail -- see this row's own header for why. CANONICAL RUN 2026-09-19 ([REVW.4] wave 4, solo, at d0c8b4c2): limits:1fail/23pass -- DETECTED, unexpected: 0, anomalies: 0. The one red cell is exactly the predicted part-2 row: \"[doc] PCREC_MAX_VM_EMIT_CODE_BYTES = 400000 (400,000) NOT found in limits.md \u00a78 -- the table and the doc have drifted\". The pass denominator is 23 rather than 21 because [REVW.4] item 1 added a limits.def row (+1 manifest check is not a PASS line, but the anchored-row doc loop is unchanged) and item 2's D107 inversion split part 3 into three arms; the row's verdict and its one-instrument claim are unchanged."
SAB_COUNT=1
SAB_BEFORE='PCREC_LIMIT(PCREC_MAX_VM_EMIT_CODE_BYTES, 500000, "bytes", "size cap", BUILD_D, "8", "[ART-SIZE]/D84: emitted C bytes OUTSIDE table initializers; --max-emit-code-bytes ALSO raises it per-compile (raise-only); -D moves the built-in default (run_size_term.sh'"'"'s reference-compiler consumer)", LIMITS_H)'
SAB_AFTER='PCREC_LIMIT(PCREC_MAX_VM_EMIT_CODE_BYTES, 400000, "bytes", "size cap", BUILD_D, "8", "[ART-SIZE]/D84: emitted C bytes OUTSIDE table initializers; --max-emit-code-bytes ALSO raises it per-compile (raise-only); -D moves the built-in default (run_size_term.sh'"'"'s reference-compiler consumer)", LIMITS_H)  /* SABOTAGE S208 */'
