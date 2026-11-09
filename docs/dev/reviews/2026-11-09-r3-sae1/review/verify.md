# verify — crit-sae1

## Verdicts

### EMIT-1 — HOLDS
Commands: `{B,S}/build/pcrec --features all -p rx -o D/rx.c --pattern P` then `grep 'define RX_REQ_RUN '`.
- `abc{0}de`: BASE "6465@0", SUBJECT "6465@0".
- `ab(?:c{0}){3}de`: BASE "6465@0", SUBJECT "61626465@1".
- p2probe "" on both patterns, subjects abde / abcde: `M 0 4` then `N` for both (same match sets).
- src/facts/req.c:674-678 (review tree): `rb_rep_width0(a,b){ (void)a; return b->runs.maxw == 0; }` -- reads the body's maxw (c: 1), never the repeat's {0}. Consequence: a missed refinement (answer-safe), SUBJECT stronger only when the body itself is width 0.

### EMIT-2 / SLOT-1 — HOLDS
Command: `S/build/pcrec --features all --emit-facts --pattern P | grep -E 'req_pieces|req_whole_run'` (fields: whole_run value / pieces why):
- `abcd(?:)*efgh`: whole_run 6162636465666768, pieces `decline:one-group`
- `ab(?:\b)*cd`: whole_run 61626364, pieces `decline:one-group`
- `abcd(?:)+efgh`, `abcd(?:){3}efgh`, `abcd(?:\b)+efgh`, `ab(?:\b)+cd`: whole_run joined (6162636465666768 / 61626364), pieces `decline:not-fixed-width`.
BASE for `abcd(?:)*efgh`, `abcd(?:)+efgh`, `ab(?:\b)*cd`, `ab(?:\b)+cd`: whole_run 65666768 / 6364 and pieces `decline:not-fixed-width` for all four. So `one-group` on the m=0 forms is new with SUBJECT; the reason differs between m=0 and m>=1 for identical joined runs.
Code (src/facts/req.c, review tree, rb_rep_unit_into ~656-663; rr_unit at :398-405 sets all=true):
```
    if (rmin == 0) rb_init(v);     /* rb_init: runs = rr_unit() -> all = true, maxw 0 */
    else *v = *b;
    v->runs.all = true;
    rb_cat_into(w, acc, v);
```
dump strings: src/dump/facts_dump.c:121 PF_WHY_PIECES_WALL -> "decline:not-fixed-width", :123 PF_WHY_PIECES_ONE -> "decline:one-group".

### CHECK-1 — HOLDS
src/core/compound.c:74 (review tree): `.facts = facts, .harness = NULL, .meas = meas };` inside the part-compile `PcrecEmitIn`.
H=SUBJECT build/pcrec-harness, `--features all -p rx`:
- `H --harness=restore=empty -o D1/rx.c --pattern '^a|abcd(?:\b)*efgh$'` vs same without lever (D2): `cmp D1/rx.c D2/rx.c` -> "IDENTICAL"; D1 has `RX_REQ_RUN "none"`, `RX_COMPOUND "split"`, `RX__Q_REQ_RUN "6162636465666768@1"` (part stamp, un-restored, line 207).
- `H --harness=restore=empty --pattern 'abcd(?:\b)*efgh$'` -> `RX_REQ_RUN "65666768@2"`; without lever `"6162636465666768@1"`.
- Half-restored compound: `--pattern 'abcd(?:\b)*efgh\A'` is RX_COMPOUND "split"; under the lever `RX_REQ_RUN "65666768@2"` but `RX__F_REQ_RUN "6162636465666768@1"` (cmp with no-lever: differ at line 10); no-lever has both `6162636465666768@1`. So the lever yields a mixed stamp set in a compound artifact.
- `'abcd(?:\b)*efgh$|^x'` under lever: byte-identical to no-lever (all part stamps stay 6162...@1).

### CHECK-2 — HOLDS (with a caveat)
tests/axes/run_axes.sh (review tree):
- 1683-1688: `# [REQ-EMPTYCAT] span_arms E1 (§3.7): --harness=restore=empty runs ... its answers must equal the default's.` / `INTERNAL_ARMS=("--harness=no-compound" "--harness=pres-window" "--harness=restore=empty")`
- 1701: `[ "$arm" = "--harness=no-compound" ] && lever_ran=1` -- only no-compound sets lever_ran.
- 2325-2329: `if [ "$lever_ran" = 1 ]; then ... python3 "$ROOT_DIR/tests/compound/check_lever.py" ...` -- the only after-loop property check.
So the restore=empty arm in test-axes gets answer-identity only, no check that it changed anything (pres-window is likewise un-checked; precedent). Caveat: the movement is pinned elsewhere, tests/codegen/run_facts_checks.sh:660-662 `[facts-arm] under --harness=restore=empty the walk runs T2 row 1's old form and its facts name the arm` (not in the axes arm itself).

### CHECK-3 — HOLDS (the "drop the line" half by reading; no rebuild allowed)
- `ab(?:\B){3}cd`, `--features all -p rx`, grep RX_REQ_RUN: BASE "6364@0"; SUBJECT "61626364@1".
- Reading: src/facts/req.c:659-661 `if (rmin == 0) rb_init(v); else *v = *b; v->runs.all = true;`; rb_init (req.c:515-520) sets `acc->runs = rr_unit()` and rr_unit (398-405) has `r.all = true`, so the forced `all = true` is a no-op at m=0. At m>=1 `*v = *b` copies the body's runs; `\b`/`\B` is A_CTX which req.c:~836-841 sends to `rr_none` (409-415: `r.all = false`), so there the forced line is what makes the join (nothing else sets all). Hence dropping it changes only m>=1. (Not confirmed by a mutant build; I may not rebuild.)
- Pins: tests/codegen/run_facts_checks.sh [facts-arm] (lines ~625-662) uses only AP='abcd(?:\b)*efgh' (m=0); its cells are req_whole_run/req_run/req_byte/req_pieces/req_set, no m>=1 pattern. tests/litscan/spanarms.rxt has the m>=1 witness `abcd(?:\b)+efgh` (line 84) with only `n` (no-match) answers; `grep 'req_run|req_whole_run|@[0-9]'` on it finds nothing. So no test pins an m>=1 RUN value.

### CONTRACT-1 — HOLDS
`S/build/pcrec --features all -p rx --pattern 'abcd(?:\b)*efgh'` -> `RX_REQ_RUN "6162636465666768@1"` (joined across a zero-iteration-admitting repeat).
docs/spec/tuning.md:670 [2.28¶3] (review tree), verbatim in part: "...nothing is joined across a repeat's iterations (`(?:ab){2,}` reports `ab`); a quantifier admitting zero iterations breaks contiguity (the opposite would delete a match where the repeat takes none); and everything that breaks the byte analysis breaks the run. Each of these is a missed opportunity, never an unsound claim."
tuning.md is not touched by BASE..SUBJECT (git diff --stat empty), so the sentence is stale only with respect to width-0 bodies; for non-zero-width bodies it still holds (BASE `(?:ab)*` etc.).

### CONTRACT-2 — HOLDS
Frozen design (`git show 791e592d3:docs/design/span_arms.md`):
- §3.7 table row "restored arms" (line 425): "harness arms `alt`, `empty` (2a), `rep` (T2 -> today's best-only REP), `zero` (T3 E-4 -> today's cut; E-5 stays E2's plain unit), `look` (...)" -- `empty` is annotated (2a); no arm is listed for E1's T2 row 1 (unit rows: `rep` is "T2 -> best-only REP", not the width-0 row).
- §8 row E1 (line 987) gate: "...`make test`, `make test-axes` with the `empty` arm; S-g, W-R4".
- src/facts/walk_arms.def:24-27 (review tree): "`empty` is span_arms unit E1's (T2 row 1, a repeat of a width-0 body: today's min-0 gap and best-only copy); stage 2a of alt_normal_form restores its EMPTY unit under the same name." Line 28: `WALK_ARM(EMPTY, "empty", (1u << PF_REQ_WHOLE_RUN) | (1u << PF_REQ_PIECES))`.
So the design's table gives `empty` to 2a while §8 gives it to E1 and the code names E1's row `empty` with 2a sharing the name; the §3.7 row is internally inconsistent with §8, and the code's resolution (one name, shared) is stated only in walk_arms.def.

### CONTRACT-3 / SLOT-2 — HOLDS
Frozen design 791e592d3:docs/design/span_arms.md:
- line 482, §4.1 row E-4: "... a negative lookaround ..., and `X{m,n}`, m >= 1, of such a body (`(?:\b)+`, `pcrec_wrap_bare_anchor`'s `<anchor EMPTY>` under a quantifier) | the unit ... | cut | unit (joins consumed contiguity)" (E2's unit per line 545 "(3) E-4 a census, unit E2").
- line 520, §4.4 table: "`abcd(?:\b)+efgh` (E-4; never matches) | 4 | 8 (sound: ...)".
Probes (SUBJECT, `--features all`):
- `pcrec -p rx --pattern 'abcd(?:\b)+efgh'` -> RX_REQ_RUN "6162636465666768@1" (8 bytes); `pcrec ... 'abcd\befgh'` -> "65666768@2" (4 bytes).
- `pcrec --emit-facts` on `abcd(?:\b)+efgh`: req_whole_run 6162636465666768 (no why).
- `pcrec-harness --harness=restore=empty --emit-facts` same pattern: req_whole_run 65666768, why `harness:empty`.
So the E-4 m>=1 mover is already joined and the `empty` arm restores it, consistent with the manager's ruling (consequence: the design's §4.4 E-4 row moves under E1, while the plain `\b` form stays E2's).

### CONTRACT-4 — HOLDS (as a literal contradiction; severity is doc-only)
`H --features all -fno-req-run --harness=restore=empty --emit-facts --pattern 'abcd(?:\b)*efgh'` (fact / status / value / why):
req_whole_run denied none `deny:-fno-req-run`; req_pieces denied none `deny:-fno-req-run`; req_run denied none `deny:-fno-req-run`; req_run_maxoff derived none (empty why); req_byte derived 98 `rate:builtin-prior`; req_landmark_maxoff derived 1 (empty). No `harness:` token anywhere. (Without -fno-req-run the same lever gives `harness:empty` on all six of req_whole_run/req_pieces/req_run/req_run_maxoff/req_byte/req_landmark_maxoff; the default build under -fno-req-run alone lists the same deny:/rate: whys, so the lever is invisible.)
docs/spec/facts_listing.md (review tree):
- 4.1.3¶1 (line 107): "`why` is empty for a plain derivation, else exactly one of the tokens below; where more than one applies, the first in this order is written: `harness:` (¶4a), then `deny:`, `decline:` and `rate:`."
- 4.1.3¶4a (line 112): "... It sits on every fact the restored arm can change (`req_whole_run` and `req_pieces` for the arm `empty`) and on every fact derived from one of them (`req_run`, `req_run_maxoff`, `req_byte`, `req_landmark_maxoff`, `run_pin`) ..."
req_whole_run and req_pieces are named facts the arm can change, and they list `deny:` not `harness:`, against ¶1's order. (One could argue the denied value cannot change, but the spec text says "can change", not "did change".)

### CONTRACT-5 — HOLDS
`H --features all --harness=restore=bogus+empty --emit-facts --pattern abc` -> `pcrec: --harness=restore= wants walk arm names joined by '+' (no arm 'bogus+empty')` (names the whole list, not the bad arm `bogus`).
`H --features all --harness=restore=empty++empty --emit-facts --pattern abc` -> `... (no arm '+empty')` (the empty middle name is reported as '+empty').
(The pcrec_walk_arms_parse contract in src/facts/facts.h:358 returns "the first unknown name's offset in `list`"; the message prints the list from that offset to its end, not the one name.) Harness-only, diagnostics wording: D26 tier.

Note for CONTRACT-4: the frozen design §3.7 (line 437) says "(A `deny:` fact is empty, `pf_enter`, so neither value arises on it.)", i.e. the design intends no `harness:` on a denied fact; the shipped spec ¶1/¶4a wording ("first in this order... `harness:` then `deny:`", "every fact the restored arm can change") does not carry that exception.

### SLOT-3 — HOLDS
Frozen design (791e592d3:docs/design/span_arms.md): line 434-437 "It is a WHY VALUE like the others: the listing keeps 'exactly one why' per run, and ... `harness:` join `deny:`, `decline:` and `rate:` under one first-match order ... there is no second field." Line 442 "`pf_done_why` (`facts.c:169-182`) takes `dead` and `harness:` out of its `decl` list". Line 103 (READY-5): "no second field".
SUBJECT: src/facts/facts.h:427-437 `PfWhy { status; code; deny; ... unsigned char arms; }` with comment "It names the listing's `why` ahead of `code` ... and leaves `status` to `code`"; src/facts/facts.h:521 `unsigned  arms_seen;` (in PatFacts); src/dump/facts_dump.c:95-98 in `fd_why`: `if (w->arms) return pcrec_sb_fragf(&cx->arena, "harness:%s", pcrec_walk_arms_text(...));` ahead of `switch ((PfWhyCode)w->code)`. So the arm set is a second field beside `code`, not a value of `code`; the printed listing still has one why column (contract on the wire holds), and the spec (facts_listing ¶4a) says status is "the derivation's own". The design's own wording is violated at the data-structure level.

### SLOT-4 — HOLDS
src/facts/req.c (review tree):
- 697-704: `rb_rep_rows[] = { { rb_rep_width0, RB_REP_UNIT, PCREC_WALK_ARM(EMPTY) }, { rb_rep_min1, RB_REP_BEST, 0 }, { rb_rep_any, RB_REP_GAP, 0 } };`  rb_rep_any (686-692) `return true`.
- 708-714: `size_t i = 0; while ((rb_rep_rows[i].arm & w->restored) || !rb_rep_rows[i].when(a, b)) i++; return rb_rep_rows[i].row;` -- no bound check on `i`; termination rests on the last row having arm 0 and an always-true `when`. No static_assert/_Static_assert in req.c (grep empty). Sound today for any `restored` value (the last row's arm is 0), so a latent-invariant finding only.

### SLOT-5 — HOLDS
src/facts/req.c:870-880: `pcrec_req_walk(Ctx *cx, const Ast *root, const ReqWalkParams *p, ...)` { `w->pos_set = p->pos_set; w->restored = p->restored; w->pd = (PdCfg){ &rb_pd_bytes, p->max_pieces, PCREC_MAX_REQ_RUN_SCAN };` } -- the record is unpacked field by field into RbWalk and PdCfg (the walk keeps no pointer to `p`).

### SLOT-6 — HOLDS
`git show 6a7fd9b04:docs/dev/plan.md | grep -n '^- \[HARNESS-LEVERS\]'` -> line 807: "- [HARNESS-LEVERS] STATE:not-started — the cli/main.c `--harness=` lever if-chain as rows of the facts.def-deny harness-source family". (The title says "facts.def-deny harness-source family"; the frozen design replaced that family per its table line 1095: "replaces rev 1's 'harness source in `facts.def`'s deny'".)

### SLOT-7 — HOLDS (nothing reads the list)
`grep -rln 'movers-out|movers_out'` over the review tree (excluding docs/dev/lanes, build, .git, journal.md, responses.md): scripts/emit_sweep.py (definition: option at :3321, writer at :3659-3669 "[REQ-EMPTYCAT] span_arms E1's identity gate: EVERY mover and asymmetric key per stream ... for a comparison against a census's mover list" writing `#stream\tclass\tkey` TSV), docs/design/memfn/probes/vmlazy/lazy_census.py (an unrelated, older option of the same name), docs/design/memfn/probes/CLAUDE.md. No script, test, make target or queue job reads the emitted file or compares a census list to observed movers; the "census list = observed movers (two-sided)" gate (design §8 row E1) has the producer only, no committed comparator. (Other 'movers' users, tests/memfn/stamp_mover_census.py etc., are separate memfn tools that do not take this file.)

VERIFY COMPLETE
