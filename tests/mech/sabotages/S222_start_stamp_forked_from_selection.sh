# S222 ([OPT-5] STEP 2) — THE `RX_DFA_START` STAMP IS FORKED FROM THE
# SELECTION: a SECOND predicate at the stamp site.
#
# WHAT IT BREAKS. This file's standing rule is ONE DERIVATION, MANY READERS:
# `dfa_search_start_of` is called by the emitter's dispatch, by the
# `<PREFIX>_DFA_START` macro, by `rx_info.search_form` and by the two stamp
# folds, so none of them can name a form the body did not take. The
# cautionary tale is `unanch_start`'s own — "M2.7 forked a second copy, and
# the fork is exactly how the prefilter and skip loops went missing from the
# `$` path for a whole milestone". This plant writes the fork.
#
# THE FAILURE MODE IS A STAMP THAT LIES ABOUT THE ARTIFACT. Every ANSWER is
# unchanged — the body is still emitted from the real selection — so no
# corpus cell, no oracle, no differential and no answer-identity sweep can be
# red. What moves is a fact the bench BUCKETS ON and a consumer reads through
# `rx_info.search_form` to know which form of `<prefix>_search` it linked.
#
# ================== NON-VACUITY IS DEMONSTRATED, NOT ASSERTED ==============
#
# A stamp-fork sabotage can pass VACUOUSLY: if the forked predicate happens to
# agree with the real one on every corpus artifact, the row is green and
# certifies nothing. So the fork is not an arbitrary second predicate.
#
# AND THE OBVIOUS FORK — the widened `state_acc_any` read alone — IS
# VACUOUS, MEASURED. The lane planted exactly that in the SELECTION and swept
# the corpus: 224 pinned artifacts, the same 224 the clean tree produces,
# because `state_acc_any` ORs over the CLASS-CONTEXT views while the
# discriminating `(?m)…$` family accepts only under the POSITION view, which
# that bit does not see, and any state the two spellings DO disagree on is
# refused by P2 anyway. A stamp forked to it would agree with the selection
# everywhere and certify nothing — which is this row's own stated hazard,
# arriving through the repair for it.
#
# SO THE FORK DROPS P2 AS WELL, which is the same two-hunk shape S218 had to
# take for the same measured reason (S108's defence-in-depth pair). With both
# halves forked at the STAMP SITE, the stamp disagrees with the selection on
# the 19 artifacts the coordinated plant moves — MEASURED: the selection
# holds 224 while a stamp built this way answers for 243 — and every one of
# those 19 stamps `"pinned"` on an artifact whose body still emits
# `rewind_position`, which is precisely what check §2's stamp-vs-body third
# term reports.
#
# ITS DISJOINTNESS FROM S218 IS ARGUED, since it reuses S218's discriminating
# population. The two sabotage DIFFERENT SITES: S218 edits the SELECTION, so
# the body changes and the answers move; S222 edits the STAMP, so the body is
# untouched and no answer moves. Check §2 (stamp == body) is what distinguishes
# them — it is the row that fires here and cannot fire for S218, whose stamp
# and body still agree with each other while both being wrong.
SAB_ID="S222-start-stamp-forked-from-selection"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="searchpinned"
SAB_DESC="RX_DFA_START and rx_info.search_form are written from a SECOND predicate rather than from the axis-J selection the body was emitted through, so on the (?m)...\$ family the artifact stamps \"pinned\" while still carrying its reverse machine. No answer moves at all -- the stamp simply describes a different artifact from the one in the file, which is what a bench bucketing on it and a dlopen consumer reading the mirror would both act on"
SAB_DOC_FIGURE="PREDICTED: searchpinned RED in §2's stamp-vs-body third term and in its mirror leg, on the 19 artifacts the coordinated fork moves (the canonical DETECTED figure is owed from the manager's matrix run). NON-VACUITY IS MEASURED, not asserted: the widened read ALONE agrees with the selection on all 224 pinned artifacts, so the fork drops the invariance clause too -- see the header. The corpus arm is deliberately not assigned: no answer moves, and assigning it would invite a reader to score its green as a half-detection."
# [MECH-REACH] THE PROBE says the stamp site still exists and still answers
# from the selection: on the clean tree `(?m)a*$` stamps "reverse-pass" AND
# carries a rewind_position, i.e. the stamp and the body agree. The floor is
# the manifest's own population, since that is what makes the fork disagree.
SAB_REACH='"$PCREC" --features all -p rx --no-captures -o "$REACH_TMP/o.c" -- "(?m)a*$" && grep -q "RX_DFA_START \"reverse-pass\"" "$REACH_TMP/o.c" && grep -q "size_t rewind_position" "$REACH_TMP/o.c" && echo REACH-STAMP-AGREES-WITH-BODY'
SAB_REACH_EXPECT="REACH-STAMP-AGREES-WITH-BODY"
SAB_REACH_POP="docs/dev/opt5m2_m2_changed_patterns.txt|^\(\?m|12"
SAB_COUNT=1
SAB_BEFORE='static const char *dfa_search_start_name(Ctx *cx)
{ return dfa_search_start_of(cx)->c.name; }'
SAB_AFTER='/* SABOTAGE S222: the stamp is a SECOND predicate, forked from the selection
 * the body was emitted through. It reads the WIDENED accept bit AND omits
 * the invariance clause -- both halves, because the widened read ALONE is
 * MEASURED to agree with the selection everywhere (see this file header). */
static const char *dfa_search_start_name(Ctx *cx)
{
    if (cx->job->engine != PCREC_ENG_UNANCH || dfa_engine_is_empty(cx))
        return "reverse-pass";
    const Dfa *fd = &cx->job->dfa;
    int fs = fd->s0;
    if (fs < 0 || fs >= fd->n) return "reverse-pass";
    if (!state_acc_any(&fd->st[fs])) return "reverse-pass";
    if (dfa_needs_seed(fd)) {
        for (int u = 0; u < UPC_N; u++) {
            if (!upc_emit_live(u)) continue;
            int su = fd->s1u[u];
            if (su < 0 || su >= fd->n) return "reverse-pass";
            if (!state_acc_any(&fd->st[su])) return "reverse-pass";
        }
    }
    return "pinned";
}'
