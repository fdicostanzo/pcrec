# S1470 (K128, lane corefix) -- THE STAR'S ENTRY TEST IS NOT EMITTED.
#
# THE CLAIM: PCRE2's empty-iteration rule covers an unbounded repeat's LAST
# MANDATORY iteration, because `X{m,}` compiles to m-1 plain copies and ONE
# repeating bracket. vm_star carries it as one emitted line at the loop's
# entry: the last mandatory copy recorded where it began in the star's guard,
# and `pos == guard` there means it consumed nothing, so the loop runs no
# iteration and takes the exit. Without the line the loop iterates after an
# empty iteration m, and a group the empty iteration set survives the later
# one (iterd27 F4: `(?:()|a)+?b` over "ab", group 1 (0,0) where libpcre2
# leaves it unset).
SAB_ID="S1470-star-entry-empty-test-dropped"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/captures/empty_iteration.rxt"
SAB_DESC="vm_star stops emitting its entry test (pos == the last mandatory iteration's start goes to the exit), so after an EMPTY last mandatory iteration the loop iterates again and the empty iteration's group writes survive: (?:()|a)+?b over 'ab' reports group 1 (0,0) where libpcre2 leaves it unset"
SAB_DOC_FIGURE="PREDICTED: tests/captures/empty_iteration.rxt RED on every lazy {1,}/{2,}/counter row (the twelve # pcre2-only blocks, both routes), the controls green -- the same 76 failures the pre-fix tree (a53296894) measured on this file by hand (lane corefix). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1470."
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "(?:()|a)+?b" && grep -c "scan_position == slot_values" "$REACH_TMP/o.c" && echo REACH-STAR-ENTRY-TEST'
SAB_REACH_EXPECT='REACH-STAR-ENTRY-TEST'
SAB_REACH_POP='tests/captures/empty_iteration.rxt|^pattern \(\?:\(\)\|a\)\+\?b$|2'
SAB_COUNT=1
SAB_BEFORE='        pcrec_sb_printf(v->b, "    if ((ptrdiff_t)scan_position == slot_values[%d]) goto %s_L%d;\n",
                  gslot, v->p, exit);'
SAB_AFTER='        (void)exit;   /* SABOTAGE S1470: the entry test is not emitted */'
