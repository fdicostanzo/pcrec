# verify

## CON-1
Verdict: HOLDS. tests/codegen/run_recursion_identity.sh:1259 `FILEPIN="${RECURSION_IDENTITY_FILEPIN:-06699f615}"`; `git show`-equivalent `git grep -n 'define PCREC_ARTIFACT_ABI' 06699f615 -- src` -> src/gen/emit_dfa.c:55 `#define PCREC_ARTIFACT_ABI 103`; subject emit_dfa.c:55 = 105. `git diff --stat BASE SUBJECT | grep recursion_identity` -> empty (file untouched). Lines 1393-1396: `if [ "$ABI_SUBJ" != "$ABI_PIN" ]; then bad "the emitted scaffolding changed: bump ... re-pin comparison (B)..."; ...; exit 1` -> gate bails on mismatch (105 vs 103).

## CHK-4
Verdict: HOLDS (stamps run; red is by reasoning, no suite run).
Ran `nice -n 19 build/pcrec --features all -p rx -o - --pattern P` (no --engine; subject build) for `a+(xyz)\1`, `[^@ ]+@(x)\1`, `\w+(@)x\1`: all three print `#define RX_ENGINE "vm"`, `#define RX_VM_PREFILTER "none"`, `#define RX_REQ_HANDOFF "unbounded"`.
tests/codegen/run_prechecks.sh: l.1692 `if [ "$st" -gt 0 ]; then` (integer test on "unbounded" -> bash error, falls to else); l.1841-1844 `if grep -q '^ *attempt_position = handoff_position;$' "$a"; then [ "$k" != "unbounded" ] && [ "$st" -le "$k" ] || bad "[5.12b] ... attempt-loop REQ_HANDOFF ..."` ; l.1847-1850 `if [ "$k" = "unbounded" ] && [ "$(stamp "$a" REQ_WHY)" = "emitted" ]; then ... [ "$st" = "none" ] || bad "[5.12c] $pat: req_landmark_maxoff unbounded but REQ_HANDOFF \"$st\" (S467)"`.
Reasoning: an artifact in the population (handoff.rxt/reqcube.rxt/... via the loop at l.1851+) with unbounded landmark maxoff, REQ_WHY emitted and stamp "unbounded" fails the 5.12c `[ "$st" = "none" ]` test -> bad (red); and 5.12b l.1692 errors. Whether such a pattern is in the current seven-file population not checked (lane green suggests none today), so the red is latent.

## EMIT-1
Verdict: HOLDS (mechanism confirmed; as the finding itself says, no regression vs BASE).
Ran `nice -n 19 tools/rxrun.sh {base,subj} OUTDIR '(a|aa|b)+cxyz' SUBJ 0 --engine=vm --step-budget=3000`, SUBJ=`cxyz`+30a+`q`: base `none` / `err -2`; subj `"unbounded"` / `err -2`; tools/p2 `nomatch`. SUBJ=`bxcxyz`+30a+`q`: base `err -2`; subj `err -2`; p2 `nomatch`.
Emitted subj rx.c (verify/w/e1_subj/rx.c): l.364 `size_t landmark_position = handoff_position;` l.366 `attempt_position = handoff_position;` l.386 entry seek `while (attempt_position < subject_length && !rx_start_set[...]) attempt_position++;` with no landmark check after it; loop l.403-408: `attempt_position++; if (landmark_position < attempt_position) { landmark_position = rx_reqrun(...attempt_position); if (landmark_position >= subject_length) return 0; } while (... !rx_start_set ...) attempt_position++;` i.e. re-ask BEFORE the seek, and none after the entry seek.
Forbidden direction (answer -> give-up vs BASE): none seen; both cases give up in BASE too.

## CHK-1
Verdict: HOLDS.
Compiled `nice build/pcrec` via tools/rxrun.sh subj `[^@ ]+@x --engine=vm` (verify/w/c1/u/rx.c; re-ask at l.309-310 `landmark_position = rx_reqrun(subject, subject_length, attempt_position); if (landmark_position >= subject_length) return 0;`). Mutated copy (python str.replace, count 1) replaces those two lines with `{ size_t t_ = rx_reqrun(subject, subject_length, attempt_position); if (t_ >= subject_length) return 0; }`. gcc -O1 with tools/drv.c.
Subject " @x " + "a@y"*20000 + "a@x", start 0, single runs `/usr/bin/time -f %e`: unmutated `match 60003 60007` 0.00 s; mutated `match 60003 60007` 1.42 s; tools/p2 `match 60003 60007`. Same answer, ~quadratic time.

## CHK-2
Verdict: HOLDS (for the two claims I ran: the mutation changes the answer on this witness, and unmutated = p2; "all 770 cells pass" not re-run, no suite).
`tools/rxrun.sh subj OUT 'b*xx(?=q)' xxxq 0 --engine=vm --features all`: stamp "unbounded", `match 1 3`; `tools/p2 'b*xx(?=q)' xxxq 0` -> `match 1 3`. Mutated copy (emitted rx.c l.303 `landmark_position = rx_reqrun(subject, subject_length, attempt_position);` -> `... attempt_position + 1);`, gcc + tools/drv.c): `nomatch`.

## CHK-5
Verdict: HOLDS (compile + grep facts; the "would pass if conjunct dropped" part is reasoning, I did not build a plant).
`build/pcrec --features all -p rx -o - --pattern '([^@ ]+)@x'` (default engine): `RX_REQ_HANDOFF "none"`, `RX_ENGINE "vm"`, `RX_VM_PREFILTER "hybrid"`.
src/gen/emit_dfa.c:8959 `if (pcrec_artifact_has_dfa_scan(cx) || !(cand_path_members(cx) & CAND_MVM))` inside `req_handoff_vm_run` (8952) is the declining conjunct.
`grep -ln 'CAND_MVM))'` and `grep -l '!(cand_path_members'` over tests/mech/sabotages/*.sh: no hits. The only has_dfa_scan sabotages (S739, S779, S494, S504) matched `has_dfa_scan` elsewhere; S494 plants the definition (`return cx->job->fit.chosen == ENGM_DFA || cx->job->fit.prefilter;`, emit_dfa.c:399 area), not the 8959 conjunct. tests/memfn/run_handoff_reach.sh: no `pcrec_artifact_has_dfa_scan`; hybrid section (l.43-90) is a reach list; the only unbounded pattern in the file is the engine-vm row at l.163 `[^@ ]+@x byte unbounded re -`. No hybrid unbounded decline pin found.

## TH-5
Verdict: HOLDS (sentinel passed as head_max; reaches only the PCREC_CAND_TRACE shadow, so no answer/choice moves).
src/gen/emit_dfa.c:1658 `s->head_max = handoff ? (uint64_t)req_handoff_k(cx) : 0;`; req_handoff_k (9066-9070) returns `pcrec_fact_req_whole_run(cx)->whole_maxoff` when req_use_whole, which for the unbounded row is >= PCREC_W_UNBOUNDED (stamp code at 9233 `if (req_handoff_k(cx) >= PCREC_W_UNBOUNDED) return "unbounded";`; internal.h:2590 comment: 1LL<<40).
memfn/src/presence.c:245 `unsigned long long h = 1000000u, m = 1000000u, k = s->head_max;` ... :258 `else if (k * h >= 1000000u) out->landmark = 0;` :259 `else out->landmark = ...`.
Consumer: grep of `->landmark|.landmark` over src/gen/*.c memfn/src/*.c: only presence.c (writes) and src/gen/emit_dfa.c:11416 `int kl = k.landmark < 0 ? 0 : k.landmark;` inside `req_pick_shadow` (def l.11306; its decl l.340-344 and call l.1578/1660 are under `#ifdef PCREC_CAND_TRACE`), emitted to stderr via MFPICK records. No other reader. Not run under a trace build (not built).

## EMIT-3
Verdict: HOLDS.
src/core/compile.c:1225-1228 `static bool fit_handoff_applies(const FitSel *s) { return s->cx->job && s->cx->job->req_handoff_vm; }` (rung "drop-handoff", l.1453-1454, note l.1458-1461 still names only the bounded-rows cost).
Setter: src/gen/emit_dfa.c:1204 (in emit_req_handoff_rest) `if (whole) cx->job->req_handoff_vm = true;` (before the `if (k >= PCREC_W_UNBOUNDED)` branch at 1205); the unbounded row emit_dfa.c:10606 `.u.use = { REQ_USE_HANDOFF, .whole = true, .reenter = true }` (row at 10602). So the unbounded row sets the bit.
`nice build/pcrec -p rx --engine=vm -o a.c --pattern 'a+xyz'` -> RX_REQ_HANDOFF "unbounded", 19638 bytes; with `-fno-req-handoff` -> "none", 19284 bytes (wc -c): delta +354, matching the finding's figure. Cap-ladder repro not run (cap raise-only; needs ~1 MB artifact).

## EMIT-4
Verdict: HOLDS (maintenance/size only; no behaviour effect).
Emitted subj rx.c (verify/w/e1_subj/rx.c) l.362-366, `grep -n handoff_position` shows no other use: `size_t handoff_position = rx_reqrun(subject, subject_length, search_from); if (handoff_position >= subject_length) return 0; size_t landmark_position = handoff_position; handoff_position = search_from; attempt_position = handoff_position;` -> the store of handoff_position at 365 is only copied on (dead intermediate).
src/gen/emit_dfa.c:1192-1195 (emit_req_handoff_rest) `StrBuf round = { 0 }; round.cx = cx; pcrec_emit_start_zero(cx, &round, ..., PCREC_START0_ROUNDUP);` built before `if (k >= PCREC_W_UNBOUNDED) {` (l.1205) whose branch emits only `handoff_position = %s;` and never uses round. emit_req_landmark_move 7852-7859: `StrBuf round = {0}; ... pcrec_emit_start_zero(... &round ...)` then `if (k >= PCREC_W_UNBOUNDED) { pcrec_sb_free(&round); return; }` -> built then explicitly freed unused (not a leak).

## CON-2
Verdict: HOLDS (doc staleness).
docs/spec/tuning.md:956 (SUBJECT worktree) [2.41¶9b]: "retries an artifact over a cap without the attempt-loop rows (¶8b) and the hybrid prefilter's re-entry (¶8a)" -- ¶8c not named, though req_handoff_vm_run (emit_dfa.c:8956 `if (cx->req_handoff_dropped) return false;`) drops the new row too.

## CON-4
Verdict: HOLDS (tag still not-started at SUBJECT; quoted below: the tag is STATE:not-started; the "status ... BUILT" line was not printed per the instruction).
277:- [REQ-PAST-LAST] STATE:not-started — stop the search loop once attempts pass the LAST occurrence of a required run (unbounded handoff)
VERIFY COMPLETE
