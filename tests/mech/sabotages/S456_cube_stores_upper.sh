#!/usr/bin/env bash
# S456 ([OPT-LITSCAN] S4 C3, lane c3build) -- THE HULL STORES THE UPPER MEMBER.
#
# A run position is canonical: T is the LOWER member, every free bit clear
# (litscan_s4.md §2.3.1, r2 R2-S3), because the pair scan's second stream is
# T | ~K and the masked compare tests (s & K) == T. This plant stores the
# upper member in the alternation's common head. The walk's one position
# constructor (rn_put) refuses it as an internal error on the first hull it
# meets, so `frank|fred` stops compiling. Detector: the harness on
# reqcube.rxt's `frank|fred` block (a refused compile fails its cells); were
# the refusal removed too, reqcube_check.py's canonical-form sweep.
# (Design's provisional S455.)
SAB_ID="S456-cube-stores-upper"
SAB_FILE="src/facts/req.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/litscan/reqcube.rxt"
SAB_DESC="the alternation's common head stores each hull position's upper member instead of the lower, a non-canonical position the walk's constructor refuses as an internal error"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/c3build_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S456."
# RE-AIMED 2026-11-13 (lane s2tri, [RUN-POS-SET] flip 2 -> 128): the
# witness is unchanged (reqcube.rxt's frank|fred block, the harness detector)
# and still reaches the plant's site (rn_common_head's join loop, row 2:
# the branches differ in width); only its spelling moved. With set positions
# up to 128 members the common head no longer stops at the cube hull fr[ae]
# (`667261@0/fffffb`) but runs on through the n/d position: measured on the
# tip `6672[6165][646e]@0`. The plant's intersection is empty at the third
# position as before, so the constructor still refuses it.
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "frank|fred" && grep -qF "#define RX_REQ_RUN \"6672[6165][646e]@0\"" "$REACH_TMP/o.c" && echo REACH-HULL-CANON'
SAB_REACH_EXPECT="REACH-HULL-CANON"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (!rn_admits(w, u)) break;
        rn_put(w, &o, u);'
SAB_AFTER='        if (!rn_admits(w, u)) break;
        { unsigned char *x_ = pcrec_arena_alloc(&w->cx->arena, 32); for (int i_ = 0; i_ < 32; i_++) x_[i_] = a.pos[o.n][i_] & b.pos[o.n][i_]; rn_put(w, &o, x_); }   /* SABOTAGE S456: the intersection */'
# RE-ANCHORED 2026-11-13 (lane rps3, [RUN-POS-SET] stage 3): positions are sets, so no
# member is "canonical"; the constructor now refuses a set outside the walk's domain (the
# empty set among it). The plant stores the branches' INTERSECTION, empty wherever they
# differ (`frank|fred`'s third position), which the constructor refuses loudly, as the
# upper member was.
