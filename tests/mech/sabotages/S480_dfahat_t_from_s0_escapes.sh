#!/usr/bin/env bash
# S480 ([START-SET] stage 3, D148 addendum 1; docs/design/startset.md §6.3,
# §6.4.3) -- THE DFA HAT'S SET IS r3's `T = S ∩ E`, with r3's admission: the
# intersection reads s0's escape set E instead of E* (every seed state's), so a
# start byte in S \ E is dropped, and the T == S build assertion (which r3 did
# not have) is disabled with it -- the review r4 sound-F1 BLOCKER, planted. (Re-anchored
# 2026-10-06, lane ssfix3: the shipped set is now T = S and the assertion is
# the re-seed's premise read off the machine, `dfa_reseed_exact`; the plant
# disables that guard, which would otherwise refuse the witnesses.)
#
# On every machine where S ⊆ E this is the identical table (§6.4.3 item 6), so
# its ONLY reach is the six sound-F1 witnesses, which the ruled admission
# DECLINES (S ⊄ E) and the plant ADMITS: `(?:(?<=a)z|w)` and its three
# siblings, `(?<=a)b|(?<=bc)d`, `(?m)(?<=\n)a|b$` -- tests/startset/dfahat.rxt's
# `W` blocks, where e.g. `(?:(?<=a)z|w)` on "aza" is (1,2) and the plant loses
# it (11,040-60,430 twin diffs each, §4.1a). Detector (arm dfahat, the
# ANSWER part since the ssfix3 split): those answer cells and the
# differential; [dfa-movers] and [dfa-wit] are the struct arm's.
SAB_ID='S480-dfahat-t-from-s0-escapes'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='dfahat'
SAB_DESC='the DFA hat intersects S with s0'\''s escape set E and admits T = S & E (r3'\''s set, sound-F1), with the re-seed premise guard off'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/ssbuild3_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S480.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern '\''(?:(?<=a)z|w)'\'' && grep -q '\''^#define RX_DFA_PREFILTER "byte-class-bounded"'\'' "$REACH_TMP/o.c" && echo REACH-SOUND-F1-WITNESS'
SAB_REACH_EXPECT='REACH-SOUND-F1-WITNESS'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    for (int b = 0; b < 256; b++) {
        tv[b] = (uint8_t)ss_has(ss, b);
        if (tv[b] && !u->cand.set[b]) return false;   /* T not within E: no narrowing */
        if (!tv[b] && u->cand.set[b]) proper = true;
    }
    if (nt == 0 || !proper) return false;
    if (!u->views)
        pcrec_ctx_fail(s->cx, 0, "internal error: a seeded machine without the "
                       "D11 bound reached the DFA hat (startset.md §6.4.3 item 3)");
    if (!dfa_reseed_exact(s->d, tv))'
SAB_AFTER='    for (int b = 0; b < 256; b++) {
        tv[b] = (uint8_t)(ss_has(ss, b) && u->cand.set[b]);   /* SABOTAGE S480: r3'\''s S & E */
        if (tv[b] && !u->cand.set[b]) return false;   /* T not within E: no narrowing */
        if (!tv[b] && u->cand.set[b]) proper = true;
    }
    if (nt == 0 || !proper) return false;
    if (!u->views)
        pcrec_ctx_fail(s->cx, 0, "internal error: a seeded machine without the "
                       "D11 bound reached the DFA hat (startset.md §6.4.3 item 3)");
    if (0 && !dfa_reseed_exact(s->d, tv))   /* SABOTAGE S480 */'
