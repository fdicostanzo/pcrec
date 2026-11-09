# house findings

## Findings

### HOUSE-1 (SUSPECTED->CONFIRMED by reading; maintenance; effort S; blast: kit only)
Duplicated selector/level-block shape. vany.c `vany_selector` (picks top bit via `31u - __builtin_clz(levels)`, one call, else `__body`) and ofsskip.c `fn_selector` (top = `rung[0]`, one call, else `callee`) are the same decision written twice with two different ways of finding "the top admitted level". vany.c `vany_level` and ofsskip.c `fn_level_block` repeat the simd_open / `#include <header>` / head / body / `\n` / simd_close bracket (ofsskip adds the once-per-art include bit, vany does not, so vany re-includes per helper only if called twice). Shared abstraction: `kit_top_level(unsigned mask)` in levels.c (next to `kit_target_levels`) plus one `kit_level_open(art/sink, lv)` bracket helper; vrun.c renders only the body so it is not a third copy. Where: memfn/src/vany.c vany_selector/vany_level; memfn/src/ofsskip.c fn_selector/fn_level_block. Cost of leaving: the next level (w64, arm64) edits the "top admitted" rule in two places.

### HOUSE-2 (CONFIRMED by reading; maintenance; effort S; blast: pcrec+kit seam)
Dead parameter kept and fed a bare literal. `mf_art_begin(ma, prefix, 0, ...)` (src/gen/memfn_sites.c, pcrec_memfn_art) and formhash.c `fh_render` pass a literal `0` for a `policy` argument that memfn.h/kit.h now say is "stored, read by nothing" (`mf_art.policy`). Memory rule pcrec-no-silent-defaults: a field nothing reads should be removed from the call (an abi event, and this IS one) not zero-filled; leaving it invites the next author to set a bit that does nothing. Also the pcrec comment justifying `0` is at the call site only. Fix: drop the parameter in the same abi/MF_SITE_ABI event, or document `0` as a named constant.

### HOUSE-3 (CONFIRMED by reading; maintenance; effort S; blast: kit.h)
Transitional switch left in. kit.h `MF_TARGET_REQUIRED` is a `#ifndef ... #define 1` toggle whose comment still reads "0 until the U2+U3 joint merge, which sets it to 1 in this one line. At 0 an art that states no target renders the portable text ...". The merge is this diff, so the comment now narrates a past state and describes a mode (At 0) no caller can reach without a -D; compose.c `define_sel` tests `MF_TARGET_REQUIRED &&` twice, keeping both dead arms alive. Either delete the switch and the `&&`, or rewrite the comment to state the live rule (refuse unstated target / unnamed policy bit) and why the knob stays. Stale-comment class named in the brief.

### HOUSE-4 (CONFIRMED by reading; maintenance; effort S; blast: src/gen/memfn_targets.c)
`pcrec_memfn_target` is documented as "the ONE derivation every art, the artifact's guard and region and `<PREFIX>_TARGETS` read" but re-runs `resolve()` (token parse through the kit) on every call: once in `pcrec_memfn_art` and once each from `pcrec_memfn_targets_stamp`, `pcrec_emit_target_guard`, `_open`, `_close` (>=5 parses per artifact, more per size-ladder attempt), and each can `pcrec_ctx_fail` mid-emission. coding.md 1.x/altitude: derive once, store on the Job/Ctx (the way `job->mf` is), read the stored pointer. Also a getter with a failing side effect is the predicate-with-side-effect pattern; failure belongs at the one derivation point. Not an answer bug.

### HOUSE-5 (CONFIRMED by reading; maintenance; effort S; blast: emit_dfa.c / emit_vm.c)
Region pairing split across two files: `pcrec_emit_target_open` is called once, in the shared `pcrec_emit_prologue` (emit_dfa.c), but `pcrec_emit_target_close` is called from two engine-specific sites (emit_dfa.c end of the DFA emitter, emit_vm.c `vm_emit_epilogue`). Correct today (verified both engines reach exactly one close; parts emit nothing), but the invariant "open in prologue, close before main" lives in prose in NOTES.md; a third emitter path or an early `goto` (note DFA's `in_entries:` label) can unbalance it silently. A first-match/declared place (e.g. the epilogue shared helper, or a debug assert in `pcrec_emit_main`/artifact end that open==close) would own it. Emitted-text rule: any new emitted scaffolding is an abi event; this is covered (98).

### HOUSE-6 (CONFIRMED by reading; maintenance; effort XS; blast: kit)
Positional initializer growth. `gate_in` gained a 6th member `art`; six call sites were edited to `{ s, def, NULL, NULL, NULL, NULL }` / `..., art }` (compose.c x3, ofsskip.c x3). Positional NULL runs are exactly how a wrong-slot value (art in `wf` position) compiles silently; designated initializers (`.s=, .h=, .art=`) at these sites removes the class. Same for `gate_tctx` neighbours, left as-is.

### HOUSE-7 (CONFIRMED by reading; doc/style; effort XS; blast: kit)
Reflow damage: memfn/src/formhash.c ~l.262-268 comment: the edit merged a long clause into the line "...so the text mf_form_hash folds is the text a cell times. `row` is the kit row the facts must reach (the composer's arm for a" (127 cols; surrounding lines ~78). Cosmetic; rewrap. The entries[] table rows at 294-301 are 146 cols but pre-existing in shape (only the column name and values changed).

### HOUSE-8 (SUSPECTED; maintenance; effort S; blast: kit gate)
NO_<level> classes are positional arithmetic: `CM_NO_LEVEL(lv) = 1<<(CL_SIZE+1+lv)` and `MF_TARGET_CLASSES` rely on fields.def declaring the generated classes immediately after SIZE, guarded by a _Static_assert in gate.c. House-OK (the assert is the alarm), but it means any class added after SIZE in fields.def breaks the build rather than extending; a comment at the CL_SIZE definition site (fields.def l.~135) says so, but nothing at MF_CLASS(SIZE) itself does. Add "NO_<level> follow; do not insert below" there. Confirm by inserting a class after SIZE in a private copy (not done: budget).

### HOUSE-9 (CONFIRMED by reading; maintenance; effort XS; blast: levels.c)
`levels.c` hand-rolls comma-list scanning (`list_has` + the strcspn loop in `admits`), a token walk that the target parser in targets.c also needs (it parses and validates `features`/`needs`). One `kit_csv_next`-style iterator would serve both and the table check; today two loops with the same `p += n; if (*p) p++;` idiom. Low priority: only two uses.

## PROBED-AND-HELD
- Stale-name grep (MF_P_PORTABLE_ONLY, pcrec_memfn_policy) over src/ lib/ cli/ memfn/src memfn/include tests/memfn tests/cli docs/spec: only 3 hits (fields.def x2, memfn.h x1), all deliberate "RETIRED" statements. HELD.
- No `#if` CPU arms remain in vany.c/vrun.c/ofsskip.c renderers (read of the full diff). HELD.
- memfn_targets.c: selection `simd_rows` first-match table untouched; new put_target_text is a single shared writer for guard/open/close (no triplicated bracket code). HELD.
- stamp_kinds.c TARGETS row placed with the other SK_PATTERN artifact stamps; emitted via pcrec_sb_stamp_str (no hand-written #define). HELD.
- Spec/doc travel: lib/pcrec.h hunk present; NOTES.md/CLAUDE.md for src/gen updated. HELD. (0 compiles used.)
