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
# ITS POPULATION IS THE `gu frames` CELLS, which exist because SS10.3 found a
# HARNESS GAP and wave A closed it: `.rxt`'s vocabulary could not say "this
# pattern gives up" at all, so `PCREC_ERR_RECURSE`'s whole observable surface
# was unassertable. The `gu <code> "<subject>"` directive is what lets this row
# have a detector rather than a description.
SAB_ID="S155-depth-capacity-untyped"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness recursion"
SAB_HARNESS_TARGET="tests/recursion/leftrec.rxt"
SAB_DESC="RX_CALL stops testing the resume-frame capacity, so a runaway recursion runs off the end of the frame array instead of returning a typed give-up -- an out-of-bounds write in emitted code where the artifact owes an honest PCREC_ERR_FRAMES"
SAB_DOC_FIGURE="REWRITTEN UNDER D71.1, and the rewrite is the point. Design 9.3's S-SR8 assumed a SECOND counter (call_depth against RX_CALL_DEPTH) answering PCREC_ERR_RECURSE, and sabotaged the CODE it returned; D71.1 removed that counter from the default artifact entirely, so the sabotage has nothing to swap. The claim that survives is \"THE DEPTH CAPACITY FIRES, AND THE gu frames CELLS SEE IT\": leftrec.rxt's give-up cells and quantified.rxt's ^(?R)*\$ cell are the population, and each asserts a TYPED give-up rather than a crash."
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
