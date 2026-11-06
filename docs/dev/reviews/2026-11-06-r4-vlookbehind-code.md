# Review 2026-11-06 r4 — vlookbehind stage 1 CODE (lane/vlbbuild 48606e036)

## RULING (manager, 2026-11-06)

No answer- or speed-level finding (about 1,100 cells against libpcre2 10.46; the limits and the STEPS figures are exact; abi 96 at every reader). Every PROPOSED FIX-NOW is ACCEPTED: F1, F3, F6-F11, F15, F17. F16 is FIX-NOW too: key DD12a(i)'s symbols by (backend, symbol) so the check stops reading the table it polices; it is small and general. F1: a lookbehind holding a backreference, var or consume callout gets the shape-5 "not built" refusal the spec and D189 promise (stage 2's backrefs), never "unbounded"; the call sweep scores over-refusal as a failure. F15: the lblow totals guard is BUILT (a planted off-by-one must refuse at compile, never hang). Sabotage rows S1963, S1964, S133 and S1980 are each fixed to fail for the RIGHT reason with a plant that moves an answer or a compile verdict; W3/W3b/W10 get plants or a stated reason each. F11's floors are raised to the measured counts minus a stated margin. SEAM-5/6/7 (the fourth spelling of the boundary rule, facts coded in enc.c, symbols parsed from C text) are PLAN: one rule per encoding, triggered by a third encoding. Validation re-runs after the fixes; the manager cancelled the queued mech/reach/axes jobs (204-208) that the fixes invalidate. Process change adopted: the round's plant.sh helper becomes a standing critic tool (the fix lane commits it under tools/review/ with a CLAUDE.md line).

## Subject

- Branch `lane/vlbbuild`, SUBJECT `48606e0360f1ece6da48cf9192e7c3346ae2efb3`, BASE (merge-base with
  main) `fb22c62a68562ad1bbdcf88a009b673d16e733d2`. 19 commits, 93 files (+3168/-739) outside the lane
  reports. Bounded variable-width lookbehind per `docs/design/vlookbehind.md` rev 4 + erratum r3-1106,
  K137's fix, abi 95 -> 96, D189.
- Rulings frozen at main `ad4ead990`. FREEZE DRIFT at hand-back: main moved to `468afbb0a`; plan.md only
  ([REQ-LOOKAROUND] ordering note, [A-REV] GO "after lookbehind stage 1 + alternation land",
  [KIT-POLICY-TABLE] retitle, new [SCAN-MULTIEXIT]). None bears on a finding below.
- Review tree built once, unlocked (`nice make -j2`, EXIT 0); BASE built as a git-archive export.
  Planted compilers via a round helper (`plant.sh`, the matrix's own `replace.py` applier, no make).

## Lenses as run

| lens | model | its one question | why chosen |
|---|---|---|---|
| EMIT (emitted vs replaced) | opus | the range loop's and `$_fwd_step`'s emitted C vs the one-length path; BASE vs SUBJECT bytes of pre-existing artifacts; answers vs libpcre2 on adversarial witnesses; storage sizing; G4's bound | emitted C (profile) |
| CONTRACT | opus | does the compiler do exactly what the spec hunks say (accept set, 255 cap, 65535 ceiling, STEPS class, abi readers), do names describe behaviour; + ruling check (D189 vs [DD-14.LB]) | caller-facing contract; rulings relied on |
| CHECKS (check adequacy) | sonnet | per new/changed sabotage row and guard: what makes it fail, does a witness reach the site, is the population counted | 21 new sabotage rows, re-cut anchors, moved guards |
| SEAM (seam round trip + slot tracing + house rules + goals + the two standing questions) | opus | is the grown encoding seam a seam, and are the checks that read it (DD12a(i)/(ii), K49) derived honestly; one table per slot; coding.md; goals order; sibling family; general form + unlocks | a back-end seam; tables/slots; plain C structure |
| CORPUS (corpus provenance) | sonnet | did every flipped/added expectation come from libpcre2 10.46, never pcrec, and is it right | the D27 and non-D27 corpus flips (launcher's profile item) |
| verifier | sonnet | re-ran the 10 CONFIRMED code/design-changing findings | — |

## Which lens caught what

- EMIT and CONTRACT independently: the backreference-in-lookbehind refusal (F1).
- CONTRACT alone: the STEPS-bound sentence (F2), stale [DD-14.LB] text + the call sweep's classifier (F3), wording corners (F4).
- EMIT alone: G2's unnamed second byte mover (F5).
- CHECKS alone: four broken/mis-aimed sabotage rows (F6-F9), witnesses with no plant (F10), loose K35 floors (F11), wrong DOC_FIGUREs (F12).
- CORPUS: no wrong expectation over 727 cells (every cell of 9 files, not a sample); two low items (F13, F14).
- SEAM alone (relayed by message; its file Write was refused by tool policy, coordinator wrote seam/findings.md from the relay): the missing lblow guard (F15), self-sourced DD12a(i) rules (F16), the witness gap (F17), the if-chain row (F18), the boundary family (F19), row facts as code (F20).

## Findings (PROPOSED dispositions)

### F1 (EMIT-1 + CONTRACT-1) — a backreference inside a lookbehind is refused as "unbounded" (shape 7), not as the shape-5 capability refusal the spec and D189 promise — FIX-NOW
- `(a)(?<=\1)x` (also `(?<=(a)\1)x`, `(a)(?<=b|\1)x`, `(?<=${x})a`): "every alternative of a lookbehind must have a bounded length (this one is unbounded)". libpcre2 10.46 ACCEPTS all of them. Spec pattern_language.md (the lookbehind paragraph, at the subject) (§2.4 shape 5 names "a backreference inside a lookbehind") and :480 (§7.4¶5 "`(a)(?<=\1)`, shape 5"); D189 "stays refused until stage 2". Code: `src/parse/mod_lookaround.c:365-373` and `:589-591` ("EVERY ARM IS A REFUSAL PCRE2 MAKES TOO") are false for this arm, reached via `pcrec_cwmax`'s saturating A_BREF answer (`:312`).
- No answer moves, but the caller is told a false fact about PCRE2 (D26's exact tier: whether a construct is real / who owns it). BASE worded it as "not implemented". Verifier: HOLDS.
- Reason: the spec is right and the code contradicts it; a small arm (a has-backref test ahead of the width walk, a capability sentence) fixes it. tests/reject rows naming the text move with it.

### F2 (CONTRACT-2) — limits.md §3.1 (fifth paragraph, at the subject)'s "about K² steps per position" holds only for a one-repeat body — DOC
- The three quoted figures are exact (7,889 -> 0, 7,890 -> STEPS for `(?<=a{1,254}b)`, etc.). But `(?<=(a{1,120}){1,2}b)` gives STEPS from ~500 bytes (K² predicts ~8,700); libpcre2 answers no-match. Per-position cost is K x (body's own backtracking). Still inside §9¶3's give-up allowance; never FRAMES, never wrong. Verifier: HOLDS.
- Reason: one qualifying sentence in the spec hunk the subject adds.

### F3 (CONTRACT-3) — stale [DD-14.LB] text on caller-facing pages, and the call sweep scores an over-refusal as EXPECTED — FIX-NOW (sweep) / DOC (compliance page)
- `docs/pcre2_compliance.md:1452-1470` and `:166-168` still say variable lookbehind is "DESIGNED, NOT BUILT" and `(?<=(a|bc))x` is REFUSED; the build accepts and answers it.
- `tests/recursion/run_lookbehind_call_sweep.py:29-48`, `:199-205`, `:244-245` (+ Makefile's `test-recursion-lbsweep` comment): a width refusal of a pattern libpcre2 compiles still scores PCREC-REFUSES and passes. Under D189 that is now the defect class (an over-refusal of a bounded call body), and this is the one sweep over call-bearing lookbehind bodies. Verifier: HOLDS.
- Reason: the sweep's classifier encodes the superseded ruling and is blind to the regression class this change opens; the compliance page may be owned by the compliance-refresh skill at landing (launcher's call).

### F4 (CONTRACT-4) — three width-refusal wording corners — PLAN (or NOTED)
- (a) a saturating BOUNDED width `(?<=(?:(?:a{65535}){65535}){65535})x` is called "unbounded" (libpcre2 err 187 "too long"); (b) a varying alternative over the ceiling says "has N" where the cap arm says "can match up to"; (c) alternatives are checked last-to-first, libpcre2 reports the first. Offsets agree. D26 tier 3 except (a), which states a false fact. Verifier: HOLDS.
- Reason: courtesy tier; (a) could ride F1's fix since it is the same saturation conflation (`mod_lookaround.c:312`).

### F5 (EMIT-2) — design G2 names one byte-mover exception (the ceiling); K137's fix moves every default `-e utf8` VM artifact with a retry loop — DOC
- 105 of 220 BASE/SUBJECT pairs differ beyond the abi stamp; all `-e utf8`, every moved hunk exactly the 5-line `[K49] The retry advance` comment; 0 byte artifacts, 0 `-fcomments`, 0 IR listings moved. This is the RULED K137 fix (known_issues.md:14-18), but vlookbehind.md G2 / the erratum never mention K137 (grep = 0).
- Reason: an identity-gate reader holding G2 will read the movers as a breach; one sentence.

### F6 (checks-1) — S1963 (W5, non-atomic retry) is a no-op plant: UNDETECTED by construction — FIX-NOW
- The plant makes `vm_look_needs_mark` return true, but the cut at body success is `if (atomic) vm_cut(...)` (`src/gen/emit_vm.c:7711`), so the mark is written and never read. Witness file 54/0 under the plant; also 0 fails over nonatomic_behind/ahead + lookbehind_variable (108 cases). Verifier: HOLDS (54/0).
- Reason: the row's whole purpose (W5) is unprotected; re-plant on the cut condition.

### F7 (checks-2) — S1964 (far sentinel taken) moves no answer; only a sanitizer sees it, and the row lists no sanitizer arm — FIX-NOW
- Plant: harness 54/0; vlb_one on 10 utf8/utf8-invalid patterns PASS. Under `-fsanitize=address,undefined` the W6 cell `(?<=(é{0,2}))x` reads `subject[SIZE_MAX]` and fails. codegen's sentinel count keeps the token, so it is blind too. Verifier: HOLDS.
- Reason: an out-of-bounds read in shipped matcher code would be undetected by the row as declared; add an asan arm or re-aim.

### F8 (checks-3) — S133 (re-cut) now fails to COMPILE emitted code on every range cell and so scores ANOMALY (matrix exit 1 at ceiling 0) — FIX-NOW
- SAB_FILE2 still drops `v->enc_mask |= PCREC_ENCE_BACK_STEP`; the range loop's far step calls back_step: `rx_BACK_STEP_NONE undeclared`. No `SAB_EXPECT=COMPILE-CATCH`; `run_sabotage_matrix.sh` ~3646 scores it ANOMALY. SAB_DESC still says "the ANSWERS ARE IDENTICAL". Verifier: HOLDS (matrix itself not re-run).
- Reason: the queued mech job will go red on it.

### F9 (checks-4) — S1980 (W12(a)) detects for the wrong reason — FIX-NOW
- The plant writes `LO_i = scan_position` (the candidate) at L_try, so failures are 22 x "expected match got nomatch" (a moving exhaustion bound), never the trail overrun the row describes. A faithful plant (re-write LO_i with its own value at L_try) gives 18 x GAVE UP (frames), already at two candidates, so W12(a)'s "nine candidates" is not what discriminates; the W12(a) cells are sound. Verifier: HOLDS (own-plant figure not re-run).
- Reason: a row whose detection does not exercise its stated mechanism protects nothing it names.

### F10 (checks-6) — witnesses W3, W3b, W10 (and W5 after F6) have no faithful plant — FIX-NOW (rows) or PLAN
- Design §7 (vlookbehind.md ~1834, ~1842) names sabotages for W3 (end-check without backtracking into the body), W3b (tail possessified), W10 (longest over all branches); no S1960-S1980 row plants them; W3b and W10's cells go red under none of the 21 rows. S1975's DOC_FIGURE claims "W3b red": measured false (line 31 passes). Verifier: HOLDS.
- Reason: the design's own witness table is the build's contract; three witnesses are unguarded.

### F11 (checks-7) — K35 cell floors in run_lookaround_diff.sh §5 sit ~60% of the measured figure while the comment says "floored at its measured figure" — FIX-NOW (small)
- Floors 30000/9000/2000/150 vs ~48,900/15,100/2,060/252 (extrapolated from constant per-pattern cell counts). ~40% of byte/utf8 subjects can vanish green; the subject set is unpinned, only the pattern counts. Verifier: HOLDS (extrapolated, said so).
- Reason: a population check that cannot see a 40% loss is not counting the population (K35).

### F12 (checks-5) — S1977/S1978/S1979 DOC_FIGUREs predict harness cells red that stay green — DOC
- Each row's detection rests on one net (codegen per-site counts for S1977/S1979, K49(b) for S1978); the figures should say so. All three are marked owed, so the matrix run would correct them; S1965/S1966 fail identical cells (indistinguishable by the corpus) — NOTED.

### F13 (corpus-1) — D27 generators are not runnable in-tree (pre-existing cell layout) — NOTED
- `tests/lookaround/d27/common.py:19-21` resolves a path that exists only in the author's cell mirror; in a mirror the flipped rows reproduce. Pre-existing, not introduced.

### F14 (corpus-2) — three flipped `spellings.rxt` blocks have only vacuous no-match subjects — NOTED
- `tests/lookaround/d27/spellings.rxt:140-165`: subjects lack `c`; the discriminating twins are at :233+. The D27 author's own subjects.

### F15 (SEAM-1) — READY-11's "emitter check that the count pass's sub-totals equal the emitter's own" does not exist; an lblow off-by-one compiles silently and hangs a matcher — FIX-NOW
- `src/gen/emit_vm.c:7285` takes `vm_slot_lblow(v, v->nlblow++)` with no bound and no post-emission compare against `nlblow_total` (the nsplice sibling has one, `:8558`). Plant (vm_slot_lblow +j+1): 5/5 SILENT-MOVE (rc 0, gcc 0), the write lands on another slot; `(?<=a{1,2})x` then does not finish. Coordinator spot-check: grep confirms no compare after `:10841`'s reset. (Relayed; not independently re-run.)
- Reason: the erratum states a guard the code lacks; the K27-family guard is a few lines.

### F16 (SEAM-2) — DD12a(i)'s derived rules read the table they police — FIX-NOW (or PLAN, launcher's call)
- ONE_SIDED and the row floor come from the seam reader's own table. Deleting byte's fwd_step or UCP row stays green except through the hand constant `erows -lt 15` (`run_encoding_checks.sh:1969`); an invented symbol, a wrong stands-for, and a compiler plant deleting `enc.c:407` (the side-table symbol) all stay GREEN, because SYM2KEY is one map across both backends. Coordinator spot-check: `:469-479` and `:1969` read as described. (Relayed.)
- Reason: learnings §3's first failure shape (a control sharing a source with what it controls); fix is to key by (backend, symbol).

### F17 (SEAM-3) — the default DD12a run cannot see a splice in the non-last / negative range path — FIX-NOW (tiny)
- The only varying witness `(?<=a{1,2})x` is one-branch positive (`run_encoding_checks.sh:1592`); a bypass splice in the `L_n_i` block is green; the far-path control is red. Add `(?<=a{1,2}|b)x` and `(?<!a{1,2}|b)x`.

### F18 (SEAM-4) — §5.1b's "declared emission row" ships as 13 `range` conditionals in `vm_look_behind_branch` (emit_vm.c:7271-7410) — PLAN
- One shared predicate (`vm_lb_varies`) keys them, so it is not two mechanisms, but it is the if-chain the decisions-as-tables rule names. A two-row const table. Remodel overlap: [VMREC].

### F19 (SEAM-5) — the boundary rule now has four spellings per backend; fwd_step's body is next_pos's — PLAN (sibling of a family, general form + unlock)
- `enc_utf8.c` fwd_step (:369+) repeats next_pos's (:62-68) three lines; with advance (:597) and start_guard that is four. General form: one boundary datum per backend rendered by the seam (enc_render_advance precedent). Unlock: a new encoding states the rule once. Trigger: a third encoding or a fifth spelling. Tension with READY-10 (K49's tie wants two sources): a design question, not a defect.

### F20 (SEAM-6) — stands-for and the side table are code, not row fields (principle 9) — PLAN
- `enc.c:144` enc_row_side_table, `enc.c:405` pcrec_enc_entry_stands_for (no backend argument though it is a fact about byte's row). Fold into [ENC-SIDE-EMIT] as its sibling.

### F21 (SEAM-7, SEAM-8) — symbol facts parsed from C text (enc.c:371-392, silent 63-char truncation, #define never listed); K49(b) compile-red prints an empty reason — NOTED

## PROBED-AND-HELD (summary; full lists in review/)

- EMIT: 255 BASE/SUBJECT pairs (510 compiles) of pre-existing lookbehinds, every spelling x 5 variants: 115 SAME, 105 K137-only (F5), 26 refused identically, 9 the intended new acceptances; 6 IR listings identical. 103 adversarial cells vs libpcre2 (multi-branch, non-atomic retry incl. W-low's shape, re-entry in repeats, nested both polarities, failed-candidate captures, lazy/possessive/atomic, anchors and `\b`/`\G` in bodies, calls, utf8, utf8-invalid incl. 5 under asan): 0 differ; 13 more by own ctypes. Storage: 21 patterns under asan/ubsan, 0 FRAMES, 0 reports; every new slot/trail/frame charged by `vm_count_slots_look`/`vm_cost_look`; give-ups only above the stamped subject ceiling. G4: +17 lines/branch, +5-line `$_fwd_step` once, one local, one slot: within bound. Emitted text matches §5.1's sketch line for line.
- CONTRACT: ~330 compiles vs own ctypes libpcre2; newly accepted constructs (unequal alternations, bounded/nested/lazy/possessive quantifiers, nested lookaround, atomic, calls, anchors, `\N`/`.`/`\h`/`\p{L}`, caseless incl. Kelvin/long s, utf8 classes, every polarity): 0 diffs; 310 random patterns: 0 accept/refuse mismatches (3 raw divergences triaged as libpcre2's: upstream U9 and -47). Accept beyond libpcre2: only the stated §9¶2a zero-width class. 255 cap: 60 cells, 10 routes x byte/utf8 x 254/255/256, identical to libpcre2. 65535 ceiling: 36 cells identical (except literal runs libpcre2 refuses as code size, err 120). STEPS: three spec figures exact; never FRAMES, never a hang, never wrong over 15 shapes x 3 sizes. abi 96: every reader moved, none left at 95. Names: D174-clean.
- CHECKS: anchor tripwire 1123 rows / 1165 sites resolve; all 21 plants build; 15 rows detected faithfully by their declared arm (S1960-62, S1965-76); S-U4, S136, S170, S134, S-U6, S693 hold; W-low's codegen detector reaches (setLO 1->0, rawLO 0->1).
- SEAM: masking on 3 artifacts; READY-10 literal; K49(b) 5 table plants all red; DD12a(i) 15/15 reached; count/emit replication; ~90 compiles.
- CORPUS: 727 cells across 9 files (every cell) vs own libpcre2 driver: 0 mismatches; mutation control 3/3; gen_corpus.py and both .gen.py reproduce their files byte for byte; no generator answer path reads pcrec; bref_oracle change correct per mode and moves no existing answer; D27 README/extract notes say who, why and the source.

## By-id completeness

| id | lens | verified | disposition |
|---|---|---|---|
| EMIT-1 | EMIT | HOLDS | F1 FIX-NOW |
| EMIT-2 | EMIT | (doc, quoted) | F5 DOC |
| CONTRACT-1 | CONTRACT | HOLDS | F1 FIX-NOW |
| CONTRACT-2 | CONTRACT | HOLDS | F2 DOC |
| CONTRACT-3 | CONTRACT | HOLDS | F3 FIX-NOW / DOC |
| CONTRACT-4 | CONTRACT | HOLDS | F4 PLAN |
| checks-1 | CHECKS | HOLDS | F6 FIX-NOW |
| checks-2 | CHECKS | HOLDS | F7 FIX-NOW |
| checks-3 | CHECKS | HOLDS | F8 FIX-NOW |
| checks-4 | CHECKS | HOLDS | F9 FIX-NOW |
| checks-5 | CHECKS | (doc) | F12 DOC |
| checks-6 | CHECKS | HOLDS | F10 FIX-NOW |
| checks-7 | CHECKS | HOLDS | F11 FIX-NOW |
| checks-8 | CHECKS | — | held (reasoned) |
| corpus-1 | CORPUS | — | F13 NOTED |
| corpus-2 | CORPUS | — | F14 NOTED |
| SEAM-1 | SEAM (relayed) | coordinator grep | F15 FIX-NOW |
| SEAM-2 | SEAM (relayed) | coordinator grep | F16 FIX-NOW/PLAN |
| SEAM-3 | SEAM (relayed) | — | F17 FIX-NOW |
| SEAM-4 | SEAM (relayed) | text | F18 PLAN |
| SEAM-5 | SEAM (relayed) | text | F19 PLAN |
| SEAM-6 | SEAM (relayed) | text | F20 PLAN |
| SEAM-7 | SEAM (relayed) | — | F21 NOTED |
| SEAM-8 | SEAM (relayed) | — | F21 NOTED |

## Recommendation

A D27 spec-first author is not recommended for this round: the D27 corpus already exists and was re-derived
cell by cell from libpcre2 (0 mismatches); F1 is a spec-vs-code contradiction a spec-first author would
find only by testing refusal wording.

## Lessons for the guide (proposed)

1. **A check lens re-derives every NEW sabotage row's plant against the emitted text it claims to break**, not the
   row's prose: 4 of 21 new rows (F6-F9) were a no-op, answer-invisible, a compile-ANOMALY or the wrong mechanism, all
   with confident DOC_FIGUREs written before the matrix ran ("owed"). A round on a branch whose mech run is still owed
   should treat every PREDICTED figure as unmeasured.
2. **A design's witness table is checked against the row list one-to-one** (F10): three named witnesses had no row.
4. **A critic whose findings-file Write is refused relays in one message, and the coordinator writes the file** (SEAM, this round: the critic correctly would not route around the refusal; lanecheck could not pass without the file).
3. **A refusal whose comment says "every arm is one PCRE2 makes too" gets one probe per construct that reaches the arm
   through a saturating fact** (F1, F4a: A_BREF and triple nesting both saturate to "unbounded").
