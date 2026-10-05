# Critic A, D6 light panel on integration.md rev 4.5: the contract against pcrec's emitters at abi 61

Basis: `git log f116cff5..main -- src cli lib` shows K86 only (cli, not an abi event). `build/pcrec` was built 14:18:29, the f116cff5 commit time, and its artifacts stamp "(abi 61)". The artifacts below are in $TMPDIR/critA/.

## A1 — BLOCKER: on the no-DFA route, the set-leads lead is REQUIRED, not OPTIONAL
- **Doc:** §14.5 "every predicate of a no-DFA-route pre-check (lead excepted)" (REQUIRED); §14.5 "`set-leads`' lead byte" is OPTIONAL; §15.3 "OPTIONAL when it is `set-leads`' lead"; §15.5 part 0 "OPTIONAL"; §14.10 bit 45 "the OPTIONAL lead predicate is not passed"; §R4.5.1 item 1 "Bit 45 still removes part 0".
- **Emitter:**
  - `emit_req_set_rest` (src/gen/emit_dfa.c:1283) has `if (req_lead_byte(cx) >= 0) done[req_lead_byte(cx)] = true;`, so the set rest omits the byte the lead tests.
  - `req_set_leads_applies` (:6716) has no DFA-route conjunct.
- **Artifact:** `--features all --pattern '(x?)([a-z]+)+Z.user\1'` gives RX_ENGINE "vm" and VM_PREFILTER "none". The emitted pre-check is the lead `!memchr(...,90,...)` plus `rx_reqrun`, with NO rq_set block. With `-fno-req-set-lead` the same pattern emits `rq_set[] = { 90 }`.
- **pcrec's own pins:** tests/codegen/run_prechecks.sh:1379 ("Z ... LEADS it ... so no member is left") and S459 (set_rest_retests_lead).
- **Wrong:**
  - On this route the lead is the only test of a member of the necessary set, so it is part of K65's linear no-match proof. An arm that drops the "OPTIONAL" lead turns NOMATCH into PCREC_ERR_STEPS (the `(x?)([a-z]+)+Z.@\1` give-up shape that emit_req_set_rest's header describes).
  - Bit 45 does not remove part 0 here. It moves the byte into part 3.
  - The "three set-leads lines" diff (gates_sync.sh (4)) holds on DFA routes only.
- **Fix:**
  - §14.5: lead need = OPTIONAL iff `pcrec_artifact_has_dfa_scan`, else REQUIRED. Delete "(lead excepted)".
  - Restate the per-route need in §15.3, §15.5 part 0 and §19 row 5.
  - §14.10 bit 45: "DFA routes: part 0 not passed. No-DFA routes: the lead byte joins part 3."
  - §R4.5.1's "run first (lead folded into the run's pass)" is sound only if the folded pass still proves the lead absent before it returns a miss. State that.

## A2 — MAJOR: `use` cannot be a static DELEG_SITES column
- **Doc:** §14.0 "`use` … DELEG_SITES' column (§14.5)"; §14.5 "`use` (DELEG_SITES' new column)"; §8.5 says DELEG_SITES is "a static table … one row per site"; §17.6 row "a POSITION site's row marked DISCARD | C10 | the PF/handoff rows exist".
- **Emitter:**
  - Whether the PRE result is read as a position is decided PER ARTIFACT by `req_uses[]` (emit_dfa.c:6867, `req_use`), through the return value of `pcrec_emit_req_byte_check` (:1391).
  - That result is read as `fwd.from` (:8365), as `first` (:8656), and as the VM hybrid's first prefilter start (emit_vm.c:13424).
  - The same PRE kind is DISCARD on union-select (RX_REQ_HANDOFF "none") and POSITION on cls-n-uc, userpass and mod-i.
  - The OFS emitter (`ofs_test_emit_fn`) serves PF (always POSITION) and PRE (either).
  - No "handoff row" exists.
- **Wrong:**
  - A static PRE=DISCARD lets an arm return "any occurrence" on handoff artifacts. That is exactly S464's miscompile (litscan_k82h §1.1a).
  - A static PRE=POSITION makes DISCARD unreachable.
- **Fix:**
  - `mf_site.use` becomes a per-instance fact derived from `req_use(cx)`, the same call that sets `ret_pred`. DELEG_SITES holds at most a ceiling ("may be DISCARD").
  - C10 checks per instance: POSITION iff the result is read (pcrec_emit_req_byte_check returned something other than posvar), or the site is PF/OFS.
  - Reword the §17.6 row.

## A3 — MAJOR: pcrec text and stamps describe the kit's plan, and a non-baseline arm can falsify them (touches Q55)
- **Doc:** §14.9 plan_hint/plan_pos "Every other arm may ignore them"; §15.5 "The notes are pcrec's per part: … [OPT-REQPOS]"; §19 row 3 says plan_pos stays at M1.
- **Emitter and spec:**
  - `<PREFIX>_REQ_RUN`'s `@idx` is defined by docs/spec/findings.md:128 as "which position of the run the scan tests (one memchr for a byte, two streams for a pair)".
  - On the run route `<PREFIX>_REQ_BYTE` is the scan member. emit_dfa.c:1374 says the stamp "and the emitted memchr cannot disagree".
  - The entry-side [OPT-REQPOS] note (emit_req_run_check :1185-1196) reads "the scan is on byte %d at offset %d of the run" or "the scan is on position %d". That is a FORM statement, so by §14.2's own rule it belongs to the arm, not to pcrec's notes.
- **Wrong:** R4d's fused run filter, or any arm that ignores plan_pos, moves bytes while pcrec still stamps and comments the old scan position. MEMFN_FORMS reads "none" at SIMD-off (Q55), so nothing flags it.
- **Fix:**
  - Before R4d, re-spec `@idx` and the run-route REQ_BYTE in docs/spec/ as pcrec's rarity PICK (a fact), not "the position the scan tests".
  - Split the [OPT-REQPOS] note into a fact half (pcrec's `note`) and a form half (the arm's).
  - Or name both explicitly as R4d's D80 spec hunk. Cross-reference Q55.

## A4 — MAJOR: about 28 existing sabotage rows are anchored inside M1 emitters, and nothing re-points them
- **Doc:** §17.6 adds new rows only. §16 item 3 and §22 R4c name src/gen/CLAUDE.md, not the mech rows.
- **Evidence:** `grep -l 'SAB_FILE=.*emit_dfa.c'` intersected with the M1 emitter texts finds 28 rows, including:
  - S185, S265, S267, S277, S278, S279, S293;
  - S447, S448, S449, S452, S455;
  - S459, S460, S463, S464, S471, S472.
- **Split emitter:** S464's SAB_BEFORE is emit_req_handoff's declaration printf. §15.5 moves that line to the kit (part 1 ASSIGN), while the subtraction (S463, S471, S472) stays pcrec's. So emit_req_handoff is split across the boundary.
- **Wrong:** the REPLACE commit deletes the anchored text. Each row misses its target and reports UNREACHED ([MECH-REACH]).
- **Fix:** §16 and §22 R4c: every mech row whose SAB_BEFORE lives in a migrated emitter is re-pointed into memfn/ (or onto the remaining pcrec half) in the REPLACE commit, with the count stated. Name the emit_req_handoff rows.

## A5 — MAJOR: a site-level `empty` cannot describe the composite, and reordering breaks EXCLUDED
- **Doc:** §14.3 "Any other arm may reorder them"; §15.4 empty EXCLUDED ("the first half has already returned on an empty window"); §15.5 gives no `empty` for the composite.
- **Emitter:** part 0's `<=` test (:1322) and part 1's loop guard are what make part 3's bare `memchr(subject + search_from, …, subject_length - search_from)` (:1298) safe on a NULL/0 subject. That is K27, cited at :1252 ("no memchr here can see a NULL subject").
- **Wrong:** an arm that reorders the set rest first, or drops a guarding predicate, emits memchr(NULL, c, 0).
- **Fix:** the composite's site-level `empty` = MISS. EXCLUDED is a property of a predicate placed after a guarding predicate, and the kit re-derives it whenever it reorders.

## A6 — MINOR: part and predicate indices are inconsistent
- **Doc, two numberings:**
  - §14.2 note_tag: window "(index 0)" → [OPT-REQPOS], whole "(index 1)" → [K66]. This matches today's `i ? "[K66]" : "[OPT-REQPOS]"` at :1067.
  - §15.3 note(0) = [OPT-REQBYTE]; §15.4 note(3) = [K65]; §15.5 numbers lead 0, window 1, whole 2, rest 3, with `ret_pred = 1`.
- **Wrong:**
  - note_tag(1) is [K66] in one numbering and the window in the other, which breaks byte identity under -fcomments.
  - `ret_pred = 1` is wrong when part 0 is absent and preds[] is dense. mod-i is such a cell: handoff, no lead (gates_d4d9ed90/mi_use.txt).
  - Nothing says that mf_site.handoff is ASSIGN iff ret_pred != 0xFF, while the other parts behave as ON_MISS.
- **Fix:**
  - One numbering: part = the index in preds[].
  - State whether absent parts are omitted (then ret_pred = the window's index, 0 or 1) or reserved.
  - Map note_tag onto the same index.
  - State the ASSIGN/ON_MISS rule.

## A7 — MINOR: the VM hybrid handoff route is not enumerated
- **Doc:** §15.5 lists "On the DFA route … and the handoff" and "On the no-DFA route (no handoff …)".
- **Emitter:** `req_handoff_applies` (:6834) admits ENGM_VM with fit.prefilter (minus Q10 and d'). emit_vm.c:13413-13424 feeds `first` (handoff_position) to the first prefn call. has_dfa_scan is true there, so there is no part 2 or 3.
- **Fix:** add a third listing: VM hybrid, define at emit_vm.c:13118 (unconditional), use at :13189, consumer = the prefilter's first call (POSITION), parts 0 and 1 only.
- **Caveat:** this is from code reading only. I found no witness artifact; my candidates were count-collapsed or had VM_PREFILTER "none".

## A8 — MINOR: every line citation in §14-§16 is pre-handoff (read at 1c2ba975), under a heading that says "abi 61"; some now point at a different function

| what | doc cites | actual |
|---|---|---|
| ofs_test_emit_fn | :6180 (now pf_block_ofs's brace) | :6295 |
| ofs_test_emit_pair | :6139 (now ofsk_emit_verify) | :6243 |
| emit_req_one_byte | :1235 | :1312 |
| emit_req_set_rest | :1181 | :1258 |
| req_run_tests | :1017 | :1026 |
| req_set_leads_applies | :6601 | :6716 |
| DFA unanchored define / clamp / use | :8113 / :8128 / :8132 | :8343 / :8358 / :8365 |
| DFA anchored define / clamp / use | :8406 / :8416 / :8417 | :8641 / :8655 / :8656 |
| VM define / clamp / use | emit_vm.c:13105 / :13157 / :13172 | :13118 / :13170 / :13189 |
| §16 memchr list (M1 six) | :1221, :1247, :6153, :6157, :6216, :6218 | :1298, :1324, :6257, :6261, :6331, :6333 |
| §16 memchr list (remaining three) | :5679, :5703, :8762 | :5783, :5807, :9001 |

The 9 → 3 count is correct. **Fix:** cite function names, or re-read at f116cff5.

## A9 — MINOR: the pair arm's locals and the form comment's literals are incomplete
- **Doc:** §15.1 lists the manifest locals as "subject, n, pos, cand, q", and the block comment's denies as "-fno-offset-skip/-fno-run-prefilter/-fno-req-run".
- **Emitter:**
  - ofs_test_emit_pair (:6252-6253) declares `ha`, `hb`, `fresh`. This is the gate on us, up and mi, 3 of the 4 R-1 cells.
  - The masked comment (pcrec_emit_req_run_blocks :1080-1086) spells -fno-req-run-fold and -fno-req-byte, and "two memchr streams for its bytes %d and %d".
- **Fix:** add the three locals, and list all deny literals and the two-stream wording as frozen form text.

## A10 — MINOR: pcrec-side checks pin the lead order, which rev 4.5 made the kit's
- **Doc:** §R4.5.3 item 3 / §R4.5.5 item 3 make the lead order part of R4d's kit form.
- **Evidence:** tests/codegen/run_prechecks.sh §5.11 (the lead is the first `!memchr` above the first `rx_reqrun(`) and S460 (lead_after_run) assert lead-first in pcrec's own suite.
- **Fix:** name §5.11 and S460 in R4d's design. When run-first lands, they become kit-form checks to re-home (G2/C5) or relax.

## A11 — NOTE: the comment escaper is stateful
- **Doc:** §14.2 gives the sink escaper `comment_byte` (emit_comment_safe_byte).
- **Emitter:** the real signature is `(StrBuf*, int *prevp, unsigned char, bool (*extra_escape)(unsigned char))` (emit_dfa.c:93). It threads `prev` across calls to catch `*/` and `/*`.
- **Fix:** the sink op carries the prev state and the predicate, or the doc states that no kit-written comment uses it at M1 (today only pcrec's notes do).

## A12 — NOTE: §15.7's "shown complete" omits PF byte-class
- pf_emit_bcls and its -bounded twin (:5822: `while (... !can_begin_match[...]) pos++; if (pos >= n) return 0;`) are not sketched. union-select's PF is "byte-class".
- **Fix:** add a bullet: STMT/FIND/ASSIGN, a SET term via table_ref, empty MISS (NOP for -bounded).

## Q53-Q55
Only A3 touches a question (**Q55**). Nothing touches Q53 or Q54.

## Checked and clean
- **ofs_test_emit_fn's memchr form:** the `while (pos + maxk < n)` guard; the offset and no-offset memchr; `cand + maxk >= n`; the ascending verify chain via `pcrec_emit_run_compare(cx, c, "subject + cand", t->run_o, …)`; the pair arm taken first when the mask byte at plan_pos is not 0xFF (:6305).
- **Handoff text** (emit_req_handoff :1125-1145): the declaration and miss test match §15.5 part 1's format. The [K82] comment, the K subtraction and the UTF-8 round-up are pcrec's text after the site. The block is absent at K=0 under byte (verified with -e utf8 '[0-9]{1,3}user').
- **Pre-check formats:**
  - the one-byte gate (:1321-1327) matches §15.3;
  - the rq_set block (:1291-1303) matches §15.4;
  - the ON_MISS call line (:1225) matches §15.5.
- **Define and use on all three routes:** define precedes use and both test the same condition (ENGM_DFA on DFA, unconditional on VM). req_run_tests and pcrec_emit_req_byte_check share their early-outs, so a block is never defined without being called.
- **Helper placement:** the rx_wN helper is written before the block comment (pcrec_runcmp_prepare :1064).
- **§15.2:** the call-site texts (pf_emit_ofs[_bounded] :6400-6445).
- **§15.7:** the PF memchr and memchr-bounded shapes (end_back 1, miss subject_length - 1 behind `scan_position + 1 < subject_length`) and N3's `break;`.
- **Deny bits** 44, 45, 46 (lib/pcrec.h:1076/1085/1096, axes.def:203-209). The bit-46 row is correct.
- **gates_d4d9ed90 snapshots:** us agrees with abi-61 emission. up, mi and cn were read from the snapshots only (the bench patterns are off-limits).
