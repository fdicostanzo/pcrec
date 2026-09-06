# S233 — [K50] THE `byte` BACKEND GROWS A CHARACTER-START RESTRICTION.
#
# Under `byte` every position IS a character boundary, so `PcrecEnc`'s
# `start_cls`/`start_guard` are NULL and nothing is emitted: no IR gate, no
# `ENG_ATTEMPT` continue, no entry guard, and the flag is masked out of
# `rx_info.flags` because it could not have acted. That is what makes "the
# encoding with no defect pays nothing for K50's fix" a construction rather
# than a comparison. Give the backend a guard and the claim collapses.
#
# THE PLANTED GUARD IS DELIBERATELY ONE THAT IS ALMOST ALWAYS TRUE (`the byte
# is not NUL`), because a guard that refused often would fail the corpus and
# be caught by anything. This one refuses on a subject containing a NUL —
# which `docs/spec/match_api.md` 3.1 promises is an ORDINARY byte — so it is
# the shape a plausible mistake takes: correct on nearly every subject, and a
# silent contract violation on the one class that says so.
#
# WHAT SEES IT: `tests/utf8/run_startbnd_diff.sh` 4, THREE independent ways on
# the same artifact — the two flag settings stop being byte-identical (the
# mask no longer applies), a `return PCREC_ERR_STARTPOS;` appears in a byte
# artifact, and `<PREFIX>_STARTPOS_GUARD` stops reading `"permissive"`. Three
# because they fail for three different reasons: the first is about the mask,
# the second about the emitter, the third about the stamp, and a fix that
# repaired one would leave the other two red.
SAB_ID="S233-startpos-guard-leaks-byte"
SAB_FILE="src/gen/enc/enc_byte.c"
SAB_SUITES="startbnd"
SAB_DESC="the byte backend declares a character-start guard, so a byte artifact grows a startpos check for an encoding in which every position is a valid start — the leak K50's fix must not have, planted in the almost-always-true shape a real mistake would take"
SAB_DOC_FIGURE="src/gen/enc/enc.h's start_cls/start_guard field comment; src/gen/enc/enc_byte.c's own NULL-is-the-answer paragraph; docs/spec/tuning.md 2.23's inert-under-byte row"
SAB_COUNT=1
SAB_REACH='"$PCREC" -p rx --features assertions -o - -- "\\B" | grep -o "_STARTPOS_GUARD \"permissive\"" | head -1'
SAB_REACH_EXPECT='_STARTPOS_GUARD "permissive"'
SAB_BEFORE='    NULL, NULL   /* [K50] start_cls / start_guard: every position is a start */'
SAB_AFTER='    NULL, "@P >= @N || @S[@P] != 0"   /* SABOTAGE S233 */'
