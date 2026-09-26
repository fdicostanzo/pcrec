# S287 — [OPT-LITSCAN] S1 `OfsTest.maxk` NOT WIDENED FOR THE RUN
# (src/gen/emit_dfa.c, `ofs_test_of`): the run rows' `maxk` is left at
# `o->maxk` alone (the walk's own selection bound) instead of also covering
# the run's own last byte (`ro + rl - 1`), so the emitted candidate-start
# guard (`cand + maxk >= n`) admits a candidate too close to the subject's
# end for the run compare to read safely. litscan_s1.md §7.1 row (d).
#
# DETECTED BY ASAN, NOT BY AN ORDINARY ANSWER DIFFERENTIAL: on a subject
# ending exactly where the run's last byte would fall past the buffer, the
# guard passes when it should refuse, and `emit_exact_compare`'s `memcmp`
# reads past the subject — a heap-buffer-overflow READ, only visible under
# `make asan` (or a sanitizer-built harness), never a wrong `m`/`n` answer on
# a plain build reading adjacent heap bytes that happen to agree.
#
# MEASURED DIRECTLY (2026-09-25, s1build PART 2 triage), NOT THROUGH THIS
# MATRIX'S `harness` ARM: `tests/mech/run_sabotage_matrix.sh`'s `harness` arm
# invokes `tests/harness/run.sh`, whose own subject buffers ARE malloc'd
# exactly to length (`decode()`'s `malloc(srclen)`) -- but re-running this row
# solo with `GENCFLAGS` carrying `-fsanitize=address` exported into the
# matrix's own environment (so it threads through to `run.sh`'s generated-code
# compile) still reads `corpus:0fail/55pass` / UNDETECTED: the harness's
# per-case gcc invocation is not the one this repo's `make asan` uses to link
# the driver against the sanitizer runtime, so the instrumented `memcmp` call
# never actually traps here. CONFIRMED REAL by a hand-built reproduction
# instead: the artifact `tests/mech/run_sabotage_matrix.sh` itself would
# produce for `[ab]/user` (extracted from a scratch sabotaged tree, byte for
# byte), compiled `gcc-16 -O0 -g -fsanitize=address`, linked against a 6-line
# driver that `malloc(strlen(s))`s the subject "xxa/us" (exactly the corpus's
# own §5.10/`run_pinned.rxt` `n \"xxa/us\"` cell for this pattern) and calls
# `rx_search` directly -- AddressSanitizer: heap-buffer-overflow, READ of
# size 5, 0 bytes after a 6-byte region, in `rx_search`'s `memcmp` (the P4
# call `ofsk_emit_verify` emits), with the CLEAN (unsabotaged) artifact
# answering `rc=0` cleanly on the identical driver and subject. So the
# mechanism is real and the corpus already carries a subject that would
# reach it (`n \"xxa/us\"`, twice, in `tests/offsetskip/run_pinned.rxt`) --
# what is missing is a MECH-MATRIX ARM that actually links the harness's
# generated code against a sanitizer runtime, which no existing arm does
# (S155's `framebuffer` arm builds its OWN bespoke ASan driver rather than
# reusing `harness`, for the identical reason). Building that arm is
# check-design work outside this triage's scope; filed here with its
# reproduction rather than guessed at. `SAB_EXPECT=UNDETECTED` reflects what
# THIS matrix's arms can measure today, not a claim that the defect is safe.
SAB_ID="S287-ofstest-maxk-not-widened"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/offsetskip/run_pinned.rxt"
SAB_EXPECT=UNDETECTED
SAB_DESC="ofs_test_of leaves OfsTest.maxk at the walk's own o->maxk without widening it to cover the run's own last byte (ro + rl - 1), so the run-pinned candidate guard (cand + maxk >= n) under-covers the run compare and a subject ending just short of a full run causes a heap-buffer-overflow READ in emit_exact_compare's memcmp -- '[ab]/user' on a subject ending 'a/us' is the reach witness, confirmed by a direct ASan reproduction (see header) since no suite arm in this matrix links generated code against a sanitizer runtime"
SAB_DOC_FIGURE="Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S287 -- reads UNDETECTED, corpus:0fail/55pass, matching SAB_EXPECT (this matrix's harness arm does not build under a sanitizer). The real defect is confirmed by the hand ASan reproduction in this file's own header, not by this matrix run."
# [MECH-REACH] the router's run row emits a maxk that already covers the run
# (o->maxk vs ro+rl-1) on the clean tree; confirms the widened form is live.
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "[ab]/user" && grep -q "^#define RX_DFA_PREFILTER \"run-pinned\"" "$REACH_TMP/o.c" && echo REACH-RUN-PINNED-EMITTED'
SAB_REACH_EXPECT="REACH-RUN-PINNED-EMITTED"
SAB_COUNT=1
SAB_BEFORE='    t->maxk     = o->maxk > ro + rl - 1 ? o->maxk : ro + rl - 1;'
SAB_AFTER='    t->maxk     = o->maxk;   /* SABOTAGE S287: not widened for the run */'
