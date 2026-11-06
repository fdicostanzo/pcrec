# READY findings (RELAYED by message; the critic's Write was refused by the harness; transcribed by the coordinator verbatim in substance)

Verdict: ready with listed text fixes. Freeze check: 2ef0d1818..80341284e touches only tests/memfn and S1079; no cited code moved.

## Findings
- READY-1 (CONFIRMED, maintenance). S133's SAB_BEFORE (S133_backstep_inlined.sh:41-46) is a 6-line block: the seek, the "ENCODING SEAM's back-step, %d character%s" note, and the sentinel branch to pcrec_vm_tgt_fail(). S134 (:36-37) anchors the same branch with the fail target. On a non-last branch the range row's lo_i sentinel goes to L_n_i (§5.1, W11b), and its note differs (§5.1b text 4). So the "one shared line" plan cannot keep S133 at SAB_COUNT=1 unchanged or keep S134 covering both rows. U8 must list re-cutting S133/S134's SAB_BEFORE/AFTER and SAB_DOC_FIGUREs.
- READY-2 (CONFIRMED). run_codegen_tests.sh:1599 exact guard `resid_backdecl -ne 7`; residlbrange + utf8 twin make it 9 -> red by construction. Header :1583-1597 says "one per top-level branch", broken by a range branch. By :1126's precedent fwd_step needs its own exact guard (=2). Not in U6.
- READY-3 (CONFIRMED by run). pcre2_ctypes.py:142 encodes str patterns latin-1; `Compiled('(?<=é|bc)x', PCRE2_UTF)` fails "UTF-8 error: byte 2 top bits not 0x80". Every non-ASCII UTF cell makes bref_oracle exit 2. Precedent fix utfcheck_arm.py:48. No PCRE2_MATCH_INVALID_UTF constant, no compile context (gate 3's max_varlookbehind=0 unaskable). Not in U6; tests/backrefs/CLAUDE.md:33 unlisted.
- READY-4. Owed items in no unit: W-low asan compilee confirmation + --work-budget compile; gate 3's accept-set/classification harness and gate 4's budget cell; DD12a(i) re-validation plants (§5.6 item 5); W-low's codegen detector and K49 member floor (implied, not named).
- READY-5 (doc). Gate 6 says `make test-codegen`; run_encoding_checks.sh runs under `test-encoding-checks` (Makefile:835-837).
- READY-6 (doc). Totals step is in vm_plan (emit_vm.c:10600), not pcrec_emit_vm; VmFrame built in vm_emit_search_body (:13056-13061), not pcrec_emit_vm; back_step mask OR is in vm_look_behind (:7392-7397), not vm_look.
- READY-7. U1 omits the stored widths change, `const int *widths` (internal.h:1858, comment :1834-1870); readers la_lb_raise (mod_lookaround.c:395), the hook and fix_widths (:446-452, :589-633), emit_vm.c:7122; vm_count_slots_look and vm_cost_look must read it. LA_MSG_MAX's comment unassigned.
- READY-8. A corpus flip moves exact guard NPO=69 in run_lookaround_diff.sh:270; flipped refused.rxt cells (:104/220/228) are python-refused, becoming `# pcre2-only` blocks. S136's DOC_FIGURE moves. Text fix.
- READY-9 (doc). arev.md:341 "today's four" VmSeek members (five after); K49 header (run_encoding_checks.sh:2094-2110) says "spelled TWICE" and a "linked next_pos".
- READY-10 (SUSPECTED). If fwd_step's utf8 body is built from next_pos's string/macro or calls it, K49's tie compares a source with itself; design should state the row is its own literal.
- READY-11 (SUSPECTED). No witness covers a vm_slot_lblow off-by-one or slot collision; lblow vm_w_range has no S150-S153 twin, argued answer-neutral; §5.1b should say so.

Per-unit: U1 cites hold (limits_check:179 -eq 78), witness yes, not separable, incomplete (R7); U2 hold/yes/no/partial (R4); U3 hold except fn name (R6)/weak (R11)/no/yes; U4 hold (six b_seek sites 4731,5073,5223,5894,7198,7510), producer misnamed/yes (W13,W6)/no/no (R9); U5 hold (bit 8 free; 2628 both encodings)/yes (W14 i/ii)/no/yes; U6 hold (SIG_RE :455, INLINE_RESID :1220, PCRE2_UTF :36)/yes/no/no (R2,R3,R5); U7 hold (FILEPIN :1252, ABASEPIN :1265)/yes/no/partial (R8); U8 S123 holds, S133/S134 do not/yes/no/no (R1,R4); U9 hold/weak/no/yes.

Standing: siblings (a) per-entry exact guards in [M5-SEAM]; (b) enc_entry_name/enc_is_twinned (enc.c:195-222) derive symbols from decls ("" for inline) -> build on pcrec_enc_entry_symbols; (c) S150-S153 rows. General form: every hand list naming seam entries from the reader (SIG_RE, TWINNED, sigs_of, residual_names exclusions, startbnd_backend_check); unlocks: third backend passes checks unedited (trigger: next entry/backend); reader table as [VMREC] (c) helper registry seam half (trigger: (c) design).

## PROBED-AND-HELD
VK_SEEK/LSET read only by renderers; no enc_mask number emitted; sentinel count holds for range (3); sigs_of matches fwd_step; uniform_fold `_step(` matcher no collision; --work-budget, VALIDATE_ONLY, REACH_ONLY exist. ~60 greps, 2 compiles, 1 python probe.
