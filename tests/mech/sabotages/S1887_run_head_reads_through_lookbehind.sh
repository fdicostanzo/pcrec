# S1887 ([RUN-POS-SET] stages 2p/2b, lane altbuild; docs/design/alt_normal_form.md
# §3.5 r7 FIX-2, S-L) -- THE RUN READS THROUGH A LOOKBEHIND, the adjacency
# head's rule leaking into the run's column.
#
# The two heads have OPPOSITE rules on `A_LOOK`: the owner's adjacency head
# reads through it (it consumes nothing), the run CUTS there (a lookbehind's
# bytes sit before the match start). The plant gives the run walk the
# adjacency rule for a positive lookbehind: its body joins the run as if
# consumed in place, so `(?<=abc)x` reports the run `abcx` where the correct
# one is `x` alone (under the floor, no run). The pre-check then searches
# `abcx` from the start offset and rejects `ms 3 "abcx"`, which libpcre2
# matches (3,4) (tests/lookaround/startpos.rxt, a generated file whose every
# cell was read from libpcre2). Hand-derived in the design at `(?<=foo)bar`;
# the corpus's own `(?<=abc)x` is the same cell.
SAB_ID="S1887-run-head-reads-through-lookbehind"
SAB_FILE="src/facts/req.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/lookaround/startpos.rxt"
SAB_DESC="the necessary-run walk reads through a positive lookbehind as if its body were consumed, so (?<=abc)x carries the run abcx and a search from offset 3 rejects a subject libpcre2 matches"
SAB_DOC_FIGURE="PREDICTED: tests/lookaround/startpos.rxt red on ms 3 \"abcx\" 3 4 (NOMATCH), and on the other ms cells whose lookbehind body joins a run over the floor."
SAB_REACH='"$PCREC" --features all -e byte --emit-facts=byte --pattern "(?<=abc)x" | grep -P "\treq_whole_run\t" | grep -c "\tnone\t"'
SAB_REACH_EXPECT='1'
SAB_REACH_POP='tests/lookaround/startpos.rxt|^pattern \(\?<=abc\)x|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        case A_KRESET:
        case A_LOOK:
        /* The two deliberate declines'
SAB_AFTER='        case A_KRESET:
        case A_LOOK:
            if (a->k == A_LOOK && a->u.look.behind && !a->u.look.neg) {
                a = a->l;   /* SABOTAGE S1887: the run reads through the lookbehind */
                continue;
            }
        /* The two deliberate declines'
