# S155 ([DD-14] wave B+C, design SS9.3 S-SR8, REWRITTEN UNDER D71.1) -- THE
# DEPTH CAPACITY FIRES, AND IT FIRES AS `PCREC_ERR_FRAMES`.
#
# THE ROW'S PREMISE CHANGED UNDER IT AND THIS HEADER IS THE RECORD. SS9.3's
# S-SR8 sabotages "return `RX_R_FRAMES` instead of `RX_R_RECURSE`", which
# assumes a SECOND counter -- `call_depth` against `RX_CALL_DEPTH` -- answering
# its own code. **D71 item 1 removed that counter from the default artifact**:
# `PCREC_ERR_RECURSE` is reserved as an ABI fact and the `ERR_FLOOR` renumber
# lands, but the recursion-depth COUNTER is a [V-H] DIAGNOSTIC GENERATION AXIS
# emitted only when asked for. A call therefore consumes ORDINARY FRAMES and a
# deep one answers `PCREC_ERR_FRAMES`; "rebuild with the diagnostic axis to
# learn which bound" is the documented story.
#
# SO THERE IS NO CODE TO SWAP, and the claim that survives the ruling is the
# half SS3.3 rests on: **the depth capacity is the ONLY guard**. No
# compile-time left-recursion refusal (PCRE2 has none -- error 140 is "invalid
# escape sequence in (*VERB) name", a different construct, and every
# left-recursive shape compiles), and no same-position runtime check, because
# SS3.3 MEASURED that one would be a MISCOMPILE: `^(a|(?1)a)$` performs 199
# nested recursions ALL ENTERED AT OFFSET 0 and MATCHES.
#
# THE SABOTAGE IS THEREFORE THE CAPACITY TEST ITSELF, which is the line that
# makes the guard exist. Without it a runaway recursion writes past the end of
# `resume_stack` -- K27's class in emitted code -- where the artifact owes a
# typed, bounded refusal.
#
# ITS POPULATION WAS THE `gu frames` CELLS, which exist because SS10.3 found a
# HARNESS GAP and wave A closed it: `.rxt`'s vocabulary could not say "this
# pattern gives up" at all, so `PCREC_ERR_RECURSE`'s whole observable surface
# was unassertable. The `gu <code> "<subject>"` directive is what lets this row
# have a detector rather than a description.
#
# **AND THAT POPULATION IS NO LONGER A DETECTOR. RE-MEASURED 2026-08-25** after
# the full matrix scored this row UNDETECTED on a tree whose SABOTAGE APPLIES
# CORRECTLY. Two INDEPENDENT causes, both measured on a scratch tree carrying
# this row's own edit, and the second is the one that matters:
#
#   1. `SAB_HARNESS_TARGET` pointed at `tests/recursion/leftrec.rxt`, which
#      HAS HELD ZERO `gu` CELLS SINCE [DD-14.EMPTY] (wave E). All three of its
#      give-up cells became `n`: the artifact now stamps `RX_VM_ROOT_MINW` and
#      `<prefix>_search` answers NOMATCH before the first frame is pushed.
#      MEASURED: the sabotaged compiler emits `#define RX_VM_ROOT_MINW
#      1099511627776ULL` for `^((?1)a)$` and returns 0 without reaching an
#      `RX_CALL`. `grep -c '^gu ' tests/recursion/leftrec.rxt` is 0. The row was
#      scoped to a file that cannot reach the sabotaged macro at all.
#
#   2. **NO ANSWER-CHECKING CELL ANYWHERE IN THE TREE CAN SEE THIS EDIT**, and
#      the reason is defence in depth rather than a thin population. The line
#      deleted here is ONE OF THREE BYTE-IDENTICAL CAPACITY TESTS emitted from
#      the same function -- `RX_TRAIL` (src/gen/emit_vm.c:8384), `RX_PUSH`
#      (:8393) and `RX_CALL` (:8483) -- and ALL THREE RETURN THE SAME
#      `RX_R_FRAMES`. Design SS4 measures 2.000 resume frames and 8.982 trail
#      entries PER NESTING LEVEL, so on every runaway shape that survives
#      [DD-14.EMPTY] a `RX_PUSH` or a `RX_TRAIL` sits between two `RX_CALL`s
#      and stops the runaway ONE FRAME LATER WITH THE IDENTICAL TYPED ANSWER.
#      The sabotage therefore changes NO ANSWER; it changes a WRITE. MEASURED
#      under the sabotage: framebuffer.rxt 16/0, quantified.rxt 57/0 (its
#      `^(?R)*$` `gu frames` cell included), leftrec.rxt 7/0, and the
#      `recursion` arm 10/0 -- including its own explicit check that
#      `^(a(?1)?b)$` "answers 'frames' at n=343". This is S108's lesson in a
#      new place: A ONE-HUNK MUTATION CANNOT FALSIFY A DEFENCE-IN-DEPTH TRIO,
#      and the corpus asserts the ANSWER, which the other two still produce.
#
# SO THE DETECTOR HAS TO READ THE WRITE, WHICH IS WHY THIS ROW NOW CARRIES THE
# `framebuffer` ARM. `tests/recursion/run_frame_buffer.sh` SS2 builds
# `fb_exact_driver.c` under `-fsanitize=address,undefined` on buffers with NO
# SLACK -- and a one-frame-short frames buffer with a generous trail is the
# ONLY population in this tree where `RX_CALL`'s test is the guard that binds
# FIRST. MEASURED 2026-08-25 on the sabotaged tree: `AddressSanitizer:
# heap-buffer-overflow ... WRITE of size 8 ... 0 bytes after 27160-byte region`
# in `rx_match_anchored`, i.e. exactly one resume frame past the end of the
# caller's array -- SAB_DESC's own sentence, observed.
#
# THE COST, AND FRANK'S RULING ON IT (2026-08-25). The detector is
# CONDITIONAL: SS2's ASan build is a PREFLIGHT, and on a box whose `$CC` cannot
# build with `-fsanitize=address,undefined` the section runs its two
# `one-short` arms WITHOUT the sanitizer, where the sabotaged build still
# answers `-3` and still PASSES. Left alone, this row would then have read
# `UNDETECTED` on such a box -- **which is a statement about the CODE, and it
# would be FALSE.** RULED: the row stays expected-DETECTED, and the MATRIX must
# not be able to print that reading. So `tests/mech/run_sabotage_matrix.sh`'s
# `framebuffer` arm runs the script with `REQUIRE_ASAN=1`, a failed preflight
# exits 3, the arm records `framebuf:UNMEASURED-no-asan`, and the verdict block
# prints **ANOMALY (an assigned arm could not perform its measurement)**. The
# opt-in `make test-frame-buffer` route passes no flag and is unchanged.
#
# THIS IS `SKIP-IS-NOT-A-PASS` APPLIED TO AN INSTRUMENT RATHER THAN AN ORACLE,
# which is the general form: `pc3`'s missing libpcre2 has been scored this way
# since MOD-0.8c, and a missing SANITIZER is the same absence for the same
# reason. `any_fail` OUTRANKS it, so a row another arm did catch still reads
# DETECTED, and the arm scrapes the `checks failed:` total BEFORE it consults
# the exit status -- a red SS1 or SS3 on an ASan-less box is still a red.
# VALIDATED IN THE FAILING DIRECTION with a `cc` wrapper that rejects
# `-fsanitize=`: `checks passed: 6, checks failed: 0` -- the exact green that
# would have been read as UNDETECTED -- and exit 3.
#
# THE `harness` AND `recursion` ARMS ARE KEPT, RE-POINTED, AND ARE THE CONTROL
# HALF. `SAB_HARNESS_TARGET` now names `tests/recursion/framebuffer.rxt` -- the
# file that still holds four `gu frames` cells and the caller-supplied
# capacities -- precisely so the row records that the ANSWER does not move.
# A future edit that ALSO broke the give-up code would go red there instead,
# and the two arms reading 0fail is then the measurement rather than a gap.
SAB_ID="S155-depth-capacity-untyped"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness recursion framebuffer"
SAB_HARNESS_TARGET="tests/recursion/framebuffer.rxt"
SAB_DESC="RX_CALL stops testing the resume-frame capacity, so a runaway recursion runs off the end of the frame array instead of returning a typed give-up -- an out-of-bounds write in emitted code where the artifact owes an honest PCREC_ERR_FRAMES"
SAB_DOC_FIGURE="RE-MEASURED 2026-08-25, and the figure is a PAIR because one half of this row detects and the other half deliberately does not. SABOTAGED: the 'framebuffer' arm reads 5pass/1FAIL -- run_frame_buffer.sh S2's exact-fit driver aborts under -fsanitize=address,undefined with heap-buffer-overflow, WRITE of size 8, 0 bytes after the 27160-byte frames region, in rx_match_anchored. CLEAN (control, same commit, no edit): 'framebuffer' reads 6pass/0fail, S2 green under the same sanitizer. THE ANSWER-CHECKING ARMS DO NOT MOVE AND ARE NOT EXPECTED TO: sabotaged 'harness' (framebuffer.rxt) 16cases/0fail and 'recursion' 10checks/0fail, identical to clean, because RX_TRAIL and RX_PUSH keep byte-identical capacity tests returning the same RX_R_FRAMES one frame later. SUPERSEDES the wave B+C figure, which named leftrec.rxt's give-up cells and quantified.rxt's ^(?R)*$ cell as the population: [DD-14.EMPTY] (wave E) turned all three leftrec cells into constant-time NOMATCH via RX_VM_ROOT_MINW, leaving that file with zero 'gu' cells, and quantified.rxt's cell was measured 57cases/0fail under the sabotage. CONDITIONAL, AND THE MATRIX NOW SAYS SO RATHER THAN LYING (Frank's ruling, 2026-08-25): the framebuffer arm runs with REQUIRE_ASAN=1, so on a box whose CC cannot build -fsanitize=address,undefined the script exits 3, the cell reads 'framebuf:UNMEASURED-no-asan' and the row is scored ANOMALY -- never UNDETECTED, which would be a false claim about the code. Validated with a cc wrapper that rejects -fsanitize=: 6pass/0fail and exit 3, i.e. the exact green that used to read as a finding."
SAB_COUNT=1
SAB_BEFORE='                "        if (run->resume_depth >= run->resume_cap) return %s_R_FRAMES; \\\n"
                "        run->resume_stack[run->resume_depth].resume_label = &&%s_fail;   \\\n"
                "        run->resume_stack[run->resume_depth].resume_position = (p_);     \\\n"
                "        run->resume_stack[run->resume_depth].trail_mark = run->trail_depth; \\\n"
                "        run->resume_stack[run->resume_depth].call_top = run->call_top;   \\\n"
                "        run->resume_stack[run->resume_depth].call_ret = (ret_);          \\\n"
                "        run->call_top = run->resume_depth;                               \\\n"
                "        run->resume_depth++;                                             \\\n"
                "    } while (0)\n\n",
                v.up, v.up, v.p);'
SAB_AFTER='                /* SABOTAGE S155: the capacity test is gone */
                "        run->resume_stack[run->resume_depth].resume_label = &&%s_fail;   \\\n"
                "        run->resume_stack[run->resume_depth].resume_position = (p_);     \\\n"
                "        run->resume_stack[run->resume_depth].trail_mark = run->trail_depth; \\\n"
                "        run->resume_stack[run->resume_depth].call_top = run->call_top;   \\\n"
                "        run->resume_stack[run->resume_depth].call_ret = (ret_);          \\\n"
                "        run->call_top = run->resume_depth;                               \\\n"
                "        run->resume_depth++;                                             \\\n"
                "    } while (0)\n\n",
                v.up, v.p);'
