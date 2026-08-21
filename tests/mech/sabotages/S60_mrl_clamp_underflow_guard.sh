# S60 — [M4.6d] THE CLAMP'S UNDERFLOW GUARD MADE VACUOUS.
#
# READ THIS ROW'S HISTORY BEFORE CHANGING IT: its first form removed the
# clamp's LATTICE ROUNDING (R26 E1's defect, restored) and came back
# UNDETECTED — mrldiff 0 fail / 146 pass, mrl 0 fail / 19 pass. That was not a
# thin population. It is a structural property of the emitted form, and it is
# a strengthening of the design's own claim:
#
#   THE SHIPPED CURSOR RUNG CANNOT EXPRESS R26 E1'S DEFECT. §4.1 rounds because
#   the clamp ASSIGNS a cursor value, and an assigned value must be a position
#   the loop could occupy. This emitter never assigns one — it FOLDS the cap
#   into the scan's own bound (§4.6), `while (cur + W <= lim_ ...)`, and `cur`
#   only ever moves by `W` from `scan_position`. So the largest `cur` the loop reaches is
#   `scan_position + W*floor((lim_ - scan_position)/W)` whether or not `lim_` was pre-rounded: the
#   loop bound is SELF-ROUNDING, and an off-lattice cursor has no spelling.
#   MEASURED by hand on `((?:ab){10,20}){10,50}` at subject_length = 198..201, rounded and
#   unrounded, answers identical.
#
# The rounding STAYS in `<PREFIX>_MRL_CAP` anyway, and deliberately: it makes
# the emitted cap the exact bound independently of how a caller consumes it,
# so a future site that does assign from it is correct by construction rather
# than by remembering this paragraph. What it does not do is carry weight
# today, and a sabotage row that pretends otherwise would be a green check
# nobody could interpret.
#
# WHAT IS ACTUALLY LOAD-BEARING at that site is the GUARD IN FRONT OF IT.
# `<PREFIX>_MRL_SHORT` is what establishes that `ceil - minrest - scan_position` does not
# underflow; §4.1 writes it as `if (CEIL < MINREST_q || CEIL - MINREST_q < scan_position)
# goto fail;` for exactly that reason. Vacuous, the subtraction wraps, `lim_`
# becomes an enormous `size_t`, and the scan's ONLY bound on the subject is
# gone — the loop reads past the end of the subject while the body keeps
# matching.
#
# MEASURED: `(a{2,4}){3,9}bcdefghij` under `--engine=vm` over an all-'a'
# subject on an exact-size heap allocation — AddressSanitizer
# heap-buffer-overflow at subject_length = 8 and subject_length = 12, against a clean `r=0` on the
# shipped build. A subject whose tail does NOT match the body fails the byte
# test inside the buffer and hides it, which is why the witness family is
# "all body bytes, no follow".
SAB_ID="S60-mrl-clamp-underflow-guard"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="mrldiff mrl"
SAB_DESC="the clamp's underflow guard made vacuous, so ceil - minrest - scan_position wraps and the folded scan bound becomes enormous: the span loop reads past the end of the subject (ASAN heap-buffer-overflow) while the body keeps matching"
SAB_DOC_FIGURE="docs/design/k23_impl/k23_design.md §4.1's guard; §14.3's self-rounding note"
SAB_COUNT=1
SAB_BEFORE='            "    ((%s_window_end) < (size_t)(mr_) || (%s_window_end) - (size_t)(mr_) < (p_))\n"'
# The two %s are KEPT (harmlessly, inside a comment) so the sb_printf's
# argument count still matches its format and the sabotaged tree does not
# build with a -Wformat-extra-args warning that would read as the sabotage
# being malformed.
SAB_AFTER='            "    (0)  /* SABOTAGE S60: %s/%s underflow guard removed */\n"'
