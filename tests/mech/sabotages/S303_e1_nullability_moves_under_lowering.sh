# S303 — [PATFACTS] step 3.2 NULLABILITY MOVES UNDER THE ENCODING LOWERING
# (src/opt/lower_enc.c, `lower_class_utf8`): a non-empty class above U+007F
# lowers to `A_EMPTY` instead of its byte sequences — the one lowering that
# would break design §3's argument that nullability is invariant ("a
# non-empty class lowers to a non-empty byte sequence").
#
# On a pattern whose only consuming node is that class (`\x{3b1}`), the
# structural tree is not nullable and the lowered one is, so the E1 fact
# sealed before the lowering and a re-derivation after it disagree. The E2
# seal's cross-check (`src/facts/facts.c` `pf_check_e1`) refuses the compile
# with an internal error, and `tests/codegen/run_facts_checks.sh` [facts-e1]
# surfaces that refusal on its non-nullable lowering-rewritten witnesses.
# THE CROSS-CHECK IS THE FIRST DETECTOR, NOT THE ONLY ONE, and that was
# measured rather than assumed (lane pf32, by hand): with this plant AND the
# cross-check's call removed, [facts-e1] is still red, because the start
# gate's machine-level self-check (`src/ir/nfa.c` `cstart_check_omission`,
# [K50-NULLGATE]) then refuses the same witnesses — the gate was omitted on
# the E1 answer "not nullable" and the lowered machine accepts without
# consuming. That is two independent derivations meeting, as that check's
# header says; it covers the DFA-unanchored route only, where the E2
# cross-check covers every route and fires first. MEASURED PER WITNESS
# (lane pf32, scratch tree): with the cross-check, four witnesses are refused
# by '[PATFACTS] nullability sealed at E1 (no) disagrees...' —
# `\x{3b1}`, `[\x{3b1}-\x{3c9}]`, `(\x{3b1})\1`, `\x{3b1}{2,5}`; with it
# removed, THREE are refused by [K50-NULLGATE] and `(\x{3b1})\1` (a VM route,
# where no start gate is built) PASSES. So the backreference witness is the
# one only the cross-check sees. THE MATRIX CANNOT ATTRIBUTE: the `facts` arm
# scores run_facts_checks.sh's failed-CHECK count and [facts-e1] is one check,
# red under either detector — a removed cross-check would still read
# DETECTED here. The attribution lives in this header and the lane report. The listing alone cannot
# see the drift: every E1 reader keeps the value sealed before the lowering.
# (The plant is not answer-neutral — the class stops consuming — so the
# corpus would also go red on patterns neither check refuses.)
# RE-ANCHORED at [CLS-TREE] S3 (2026-09-29, lane s3build): the non-empty
# return became `return wclass_of(lc, a, res);`. The AFTER is unchanged: the
# class still lowers to a bare A_EMPTY, and the E1/E2 cross-check refuses it.
SAB_ID="S303-e1-nullability-moves-under-lowering"
SAB_FILE="src/opt/lower_enc.c"
SAB_SUITES="facts"
SAB_DESC="the utf8 encoding lowering turns a non-empty class above U+007F into A_EMPTY, so a pattern whose only consuming node is that class is nullable on the lowered tree and not on the structural one the E1 seal recorded — the drift the E1 invariance cross-check exists to refuse"
SAB_DOC_FIGURE="facts:1fail/6pass expected — [facts-e1] reports the non-nullable lowering-rewritten utf8 witnesses refused with 'internal error: [PATFACTS] nullability sealed at E1 (no) disagrees with the lowered tree's (yes)'; every other facts check stays green. With the cross-check disabled by hand the same witnesses are refused by [K50-NULLGATE]'s 'omitted the character-boundary gate on a pattern that can ACCEPT without consuming' instead (defence in depth; the cross-check fires first). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S303."
# [MECH-REACH] the site answers: under -e utf8 a class above U+007F IS
# rewritten by the lowering (its two-byte run exists only on the lowered tree).
SAB_REACH='"$PCREC" -e utf8 -p rx -o "$REACH_TMP/o.c" --pattern "\\x{3b1}" && grep -q "^#define RX_REQ_RUN \"ceb1@1\"" "$REACH_TMP/o.c" && echo REACH-UTF8-LOWERING-REWRITES'
SAB_REACH_EXPECT="REACH-UTF8-LOWERING-REWRITES"
SAB_REACH_POP="tests/codegen/run_facts_checks.sh|^    'E1W[[:space:]]utf8[[:space:]].*[[:space:]]no'|4"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                res = seal;
            }
            return wclass_of(lc, a, res);'
SAB_AFTER='                res = seal;
            }
            return pcrec_ast_node(lc->cx, A_EMPTY);   /* SABOTAGE S303: a non-empty class lowers to A_EMPTY */'
