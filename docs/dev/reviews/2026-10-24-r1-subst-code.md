# 2026-10-24 rN — subst (code): compiled substitution, lane/substland

DRAFT by the round coordinator; every disposition is PROPOSED, for the manager's ruling.

## Subject
- Branch lane/substland, SUBJECT 1222b31befc0df84074ce7f95febfd8bbea30f9c; BASE 6ec3a21088a315792bbbf4f9436c280e2aaadc8a
  (merge-base with main). 160 files, +16,794/-77, 52 commits. [M4-SUBST]: subst artifacts (template -> pieces),
  the R4 interface, module subst-extended, the case table, CLI `--subst`/`--subst-file`/`--emit-support`.
  Contract docs/spec/subst_api.md; design docs/design/replace_design.md §R4, subst_template_design.md.
- Review tree worktrees/crit-subst at SUBJECT, built once under boxlock; BASE built from `git archive` in scratch
  for the before/after diff. Critics ran the built compiler, gcc and their own drivers; no make, no suites.
- Profile: emitted C (new kind + touched emit_dfa/lower_enc/definitions/enc), a caller-facing contract, checks
  (50 sabotage rows, two sections, the d27 harness), plain C structure. No floor/pin re-pin in the diff, so no
  trade-audit lens.

## Lenses as run
| lens | model | question | why chosen |
|---|---|---|---|
| contract-template (TPL) | opus | does every admitted template form render what the spec and pcre2_substitute say, and every refused form refuse at its offset? | contract, answer tier; the template language is most of the contract |
| contract-interface (IFACE) + goals | opus | does the code do what §1, §3-§10 and the branch CLI spec sections for --subst and --emit-support say; do names describe behaviour; are §R4's goals ranked and served? | contract, interface tier; the contract is too large for one lens |
| emitted vs replaced (EMIT) + sibling + general form | opus | C/asm of the new path vs hand-written and pcre2; every pre-existing rx entry BASE vs SUBJECT | emitted C, and touched shared emitters |
| check adequacy (CHK) | sonnet | per new check: failing input, its chooser, a witness reaching the site, a counted population | 50 sabotage rows + sections + d27 |
| house rules (HOUSE) | sonnet | coding.md/style.md/architecture.md over the new and touched C | ~1,900 lines of new C |
| verifier | sonnet | re-run every CONFIRMED finding that would change code or design | skill §6 |

## Which lens caught what
- Answer-tier: TPL-1 (contract-template, by differential against libpcre2). EMIT-5 (emitted lens, from reading the
  emitted table) raises an answer-tier RULING question under today's D26 addendum.
- Speed: only the emitted lens (EMIT-1/2/3), with a pcre2 baseline. Size: EMIT-4, TPL-4.
- Interface design/naming: IFACE-4/5/6 (contract-interface). Doc drift: IFACE-1/2/3/7/9, TPL-2/3.
- Check defects: CHK-1 (two rows DETECTED by a -Werror compile failure, not their witness), CHK-6/7/8.
- Pre-existing rx artifacts: emitted lens, 0 bytes moved over 72 compiles + 6 flag variants + 58 diagnostic probes.
- Overlaps: EMIT-6 and HOUSE-7 are one emitted-text cleanup; IFACE-8 explains IFACE-4 (no ranked goals);
  IFACE-9's stale draft is where IFACE-1's "returns 0" came from; CHK-7 also seen by IFACE (probed held for 9 options;
  CHK found the default-valued spellings that slip through).

## Findings (verifier status in brackets)

### Answer tier
- **TPL-1** [HOLDS] `encoding = -1` (encoding-neutral) is decided from the template TEXT bytes only, so an all-ASCII
  subst-extended template with `\xe9`, `\x{100}`, `\o{351}`, `\N{U+41}` is accepted against an rx of the other
  encoding and renders bytes PCRE2 does not (byte rx: `\xc3\xa9` vs `\xe9`; `\x{100}`/`\N{U+41}` rendered where PCRE2
  refuses -57; reverse: a lone 0xE9 into UTF-8 output). §2¶5 promises refusal "before any output". emit_subst.c:1124-1133.
  **PROPOSED: FIX-NOW** — set the record's encoding from the parsed literal bytes (or any numeric escape); add the
  six cases as cells; amend §2¶5's "all-ASCII" sentence. Effort S.
- **EMIT-5** [HOLDS, plus a fifth row U+00B5 -> U+03BC] the case table copies libpcre2 10.46's \U results that are not
  Unicode Simple_Uppercase_Mapping (U+03B9->U+0345 a combining mark, U+03BC->U+00B5, U+01C5->U+01C6 lowercase,
  U+03D0->U+03B2 lowercase, U+00B5->U+03BC; UCD 16.0 says 0399, 039C, 01C4, 0392, 039C). §2¶14 pins "the code point
  libpcre2 10.46 maps it to", ruled at BASE; the D26 addendum (e04e9f61a, today) says follow the standard where PCRE2
  has a bug and record the upstream issue. **PROPOSED: FIX-NOW, subject to the manager's ruling** — leaning: these
  are a PCRE2 bug (\U yielding a lowercase letter or a combining mark), so the table becomes UCD simple mappings,
  §9 gains a difference row, upstream_issues.md gains the entry, and the `same` cells covering these code points
  become pcrec-only. Cheapest before landing (the table and its cells are new). Effort M.

### Speed / size
- **EMIT-1** [HOLDS: 110.9M vs pcre2+JIT 95.9M instr, +15.7%] UTF-8 case forcing is the one subst row slower than
  pcre2_substitute+JIT: two full passes (sizing then writing), no ASCII fast path (every a-z through a ~11-step bsearch
  over 1,466 pairs), uncased tail inside the region. §R4.11 marked the two passes UNMEASURED with trigger "a user's hot
  \U template". **PROPOSED: PLAN** — a new row with this measurement as its evidence; ASCII fast path + skip sizing
  when §4¶22's 1.5x bound fits. Not a landing blocker (answers right; plain and byte-case templates beat pcre2+JIT).
- **EMIT-2** [HOLDS: 354 vs 110 instr/match overhead over bare find-all, 3.2x] replace-all's `rx_subst_append_`
  re-checks overflow/fit through pointers per piece; `rx_subst_flatten` already has the batch shape. Still 22% under
  pcre2+JIT. **PROPOSED: PLAN** (headroom, S).
- **EMIT-3** (not verified; analysis) slot calls not inlined, case state not constant-folded, constants case-mapped per
  match. **PROPOSED: NOTED**, fold into EMIT-1's row.
- **EMIT-4** [HOLDS: 41,532 B vs 14,537 B text; 23,056 B of tables] the IMPLEMENTATION support unit links the case
  tables into programs with no case template. **PROPOSED: PLAN**, as a member of the [DATA-PLAN]/D179 table-format
  family (run/delta encoding) plus a way for non-case programs not to link them.
- **TPL-4** [HOLDS: ~157 B RSS per template byte; no length row in limits.def] **PROPOSED: PLAN** (a template length
  / piece-count limit row; low priority, outputs correct).

### Interface / design
- **IFACE-4** [HOLDS; verifier: §10¶7 DOES state both cases as MISMATCH] replace-all answers MISMATCH (no `need`) for
  `o->cap < P` and for > RX_SUBST_BATCH_PAIRS (256) groups, where the element answers the same shortfall NOSPACE+need.
  An argument against a stated rule, not an undocumented defect. **PROPOSED: FIX-NOW for cap < P** (NOSPACE + need = P:
  one code per shortfall across entry points, S, pre-release); **PLAN for > 256 groups** (a fallback through o->pc or
  its own code; a pattern class with >255 groups cannot use replace-all today).
- **IFACE-5** [HOLDS] the default prefix `rx` emits the record `rx_subst_info` (and `-p pcrec` -> `pcrec_subst_info`),
  inside the reserved `rx_subst_*` family and spelled as its own struct tag. **PROPOSED: FIX-NOW** (pre-release rename of
  the record's suffix so the default prefix stays usable; a subst emitted-text change, so before the subst kind's bytes
  are pinned). Manager's call on the spelling (D174).
- **IFACE-6** (read) `pcrec_subst_check`/`pcrec_subst_map_names` beside `rx_subst_ctx_init`/`rx_subst_flatten`/
  `rx_subst_replace_all`: no stated rule for the two prefixes. **PROPOSED: FIX-NOW with IFACE-5** as one rename +
  a §1¶2 sentence stating the rule; after release it is an API break. grep the sabotage anchors before moving names.
- **IFACE-8** (read) §R4 has no ranked, checkable goals; R4.0 items 4/5 are amended by R9/R11/R13 without a marker.
  The five implied goals were each tested and held. **PROPOSED: DOC** (ranked goal table + amended markers).

### Doc
- **IFACE-1** §10¶10 says replace-all "returns 0"; it returns the count (§10¶7). **DOC (FIX-NOW, one clause).**
- **IFACE-2** §8¶1's table omits replace-all from BADSPAN/UNSET/UNSET_VAR/ERR_ITER and says "context helper". **DOC.**
- **IFACE-3** §4¶11 omits the no-map MISMATCH (k >= ncap, or a named ref with no map). **DOC.**
- **IFACE-7** [HOLDS] a BOUND iterator's consumed matches are copied unreplaced and uncounted; §10¶7's "0 = subject
  unchanged" assumes a fresh iterator. **DOC.**
- **IFACE-9** [HOLDS] docs/design/subst_api_r4_draft.md survived the build (its header says it is replaced at build
  time), diverges from the spec in ~275 lines and names RX_FOREACH_PAIRS (dropped, D175); replace_design.md
  §R4.2/§R4.16/§R4.17 likewise. **DOC (FIX-NOW: retire the draft to a pointer, mark superseded sentences).**
- **TPL-2** §2¶14a: "begins a well-formed character" is judged per source piece, not over the output stream. **DOC.**
- **TPL-3** §2¶4's "template offset" is the construct start for some refusals and the fault point for others. **DOC**
  (state "the offset of the refused construct").

### Checks
- **CHK-1** [HOLDS] S1354 and S1374's plants fail the emitted code's -Werror compile (unused-parameter,
  type-limits), so the matrix scores DETECTED at "driver build" without any cell running. **PROPOSED: FIX-NOW**
  (warning-clean plants; consider a "plant compiles" assertion in the matrix — the general form, see lessons).
- **CHK-6** [HOLDS] the room arm prints `need` but run_subst_tests.py:329-332 never reads it; the support-id clause
  and sneed overflow have no mech row. **PROPOSED: FIX-NOW** for reading `need` (S); PLAN for the two rows.
- **CHK-7** [HOLDS] `--engine=auto`, `--tune=0`, `--size-cap=degrade` accepted with `--subst` (refusal is a compare
  against defaults), against the branch CLI spec (--subst section) "every pattern-compile option is refused". **PROPOSED: FIX-NOW** (refuse by
  presence, S; derive the test loop from the option table).
- **CHK-8** [HOLDS] REACH token S1352 still in REACH_NEED though S1352 is now an equivalent mutant; shared tokens let a
  row's only witness vanish (S1357/duprun3). **PROPOSED: FIX-NOW** for the stale token (S); NOTED for sharing.
- **CHK-4** [HOLDS] d27's ref_pcre2.py:15 dlopens the bare soname, bypassing tests/lib/resolve_pcre2.sh (D98).
  **PROPOSED: FIX-NOW** (S).
- **CHK-3** [PARTLY: d27/cli/cli.sh:69 does refuse-test `$65536`] the 65535/65536 boundary is not pinned in
  tests/subst's own cells. **PROPOSED: NOTED** (covered by d27; add to cells only with another edit there).
- **CHK-2** (suspected) d27 families have no PASS floor; PCREC_REFUSED is uncounted. **PROPOSED: PLAN.**
- **CHK-5** (suspected) cells hard-code 10.46 answers without a version gate or label. **PROPOSED: PLAN** (print the
  version at least; ties to EMIT-5's ruling).

### House rules
- **HOUSE-1** [HOLDS] the template parser's group-name grammar is a private copy of mod_named_groups.c's, whose own
  comment forbids a second copy; subst_template.c:20-27 says it "UNIFIES WITH IT AT MERGE". **PROPOSED: FIX-NOW**
  (this is the merge; S).
- **HOUSE-3** [HOLDS] pcrec_prefix_acceptable and compile_driver spell the same two checks and messages twice.
  **PROPOSED: FIX-NOW** (S, one call site).
- **HOUSE-7 + EMIT-6** [HOLDS] three non-ASCII `§`/`¶` comments in emitted subst artifacts (rx artifacts and the support
  unit are ASCII); a blanket `(void)` list and a dead `sl` in every case region. **PROPOSED: FIX-NOW** as one emitted-text
  cleanup, before the subst kind's bytes are pinned (same timing argument as IFACE-5).
- **HOUSE-8** [HOLDS] case_state_tables' row scan has no bound (relies on a final unconditional row); literals 9/3.
  **PROPOSED: FIX-NOW for the bound (fail loudly, no silent default)**; PLAN for the rest.
- **HOUSE-2** (CLI output tail 3-4 copies), **HOUSE-4** [HOLDS: the two item walks] (span table shared by the two
  emitters), **HOUSE-5** (fixed scratch buffers, coding.md 2.2), **HOUSE-6** (arena strndup copy), **HOUSE-9**
  [(1) HOLDS] (st_seq stop predicate twice; st_push; extract st_dollar/st_run, not a table), **HOUSE-10** [HOLDS]
  (support unit built to read its id), **HOUSE-11** (small items). **PROPOSED: PLAN** — one subst-cleanup row; each S,
  none changes an answer; grep sabotage anchors (coding.md 3.5) before moving lines.

## PROBED-AND-HELD (summary; full lists in review/*.md)
- TPL: ~320 differential cases vs pcre2_substitute 10.46 (core 66, extended 100, case forcing 80, a FULL Unicode
  sweep of every scalar 1..0x10FFFF under \U\L\u\l: identical), CLI escaping of hostile template bytes.
- IFACE: 47 CLI lines, reserved prefixes both paths, check 15 cases, by-name helper 8, element 22, replace-all paths,
  header coexistence, support unit STATIC/IMPLEMENTATION/two-TU link, identical bytes.
- EMIT: pre-existing rx artifacts byte-identical BASE vs SUBJECT (72 compiles, 6 flag variants, 58 diagnostic probes);
  abi stays 84, no bump owed; plain templates 23% fewer instructions than pcre2+JIT; byte case 15% fewer.
- CHK: SAB_BEFORE counts 50/50; S1352 equivalence held; ~25 emitted-text plants compile clean; pcre2 skip is loud.
- HOUSE: allocation exception documented; refactored escape decoders behaviour-equal; declared tables extended by rows.

## By-id completeness
TPL-1..4; IFACE-1..9; EMIT-1..6; CHK-1..8; HOUSE-1..11 — 38 ids, each dispositioned above.
Proposed FIX-NOW: TPL-1, EMIT-5 (after ruling), IFACE-1, IFACE-4 (cap<P part), IFACE-5, IFACE-6, IFACE-9, CHK-1,
CHK-4, CHK-6 (need), CHK-7, CHK-8 (token), HOUSE-1, HOUSE-3, HOUSE-7+EMIT-6, HOUSE-8 (bound). Other DOC items ride
the same spec hunk.

## Not covered
`${!name}` variables against an oracle; scratch-size exactness as a bound (§4¶22); per-match/batch/no-gaps recipes
beyond replace-all (TPL); real abi skew and real two-support-id programs (simulated); thread use (§7¶5); map-ful render
cost; >85-group batch shrink; non-ASCII subjects on the UTF-8 case path timing; .rxt/-o DIR pooled compiles for the rx
byte-identity check; parse-side/CLI sabotage rows judged by reading only (needed a sabotaged compiler); tools/review
censuses predate the new files. No D27 spec-first author was part of this round (a d27 harness ships in the diff).

## Lessons for the guide (proposed)
1. **A sabotage row can be DETECTED by the plant failing to compile** (CHK-1): with -Werror on emitted code, a plant
   that leaves a parameter unused or a comparison vacuous scores DETECTED at "driver build". Rule for check-adequacy:
   transplant each emitted-text plant onto a real artifact and compile it; a sabotage row needs a "plant compiles" gate.
2. **Encoding-neutrality decided from source text, not from what the source denotes** (TPL-1) is a recurring shape
   (the text is ASCII, the value is not); a contract lens should probe every escape that produces a byte.
3. **"Bug-compatible with version X" in a spec is a ruling that can be overtaken the same day** (EMIT-5 vs the D26
   addendum): a round should check spec sentences that pin an upstream version against the current D-rows.

## Rulings (manager, 2026-10-24)

Every proposed disposition is accepted except where stated.

- **EMIT-5: FIX-NOW, a PCRE2 bug.** Under the D26 addendum (Frank, 2026-10-24: compatible with PCRE2 unless it is a bug), an uppercasing that yields a lowercase letter or a combining mark contradicts Unicode's own UnicodeData.txt simple mappings, which is the evidence the addendum asks for. The case table becomes the UCD 16.0.0 simple mappings; §2¶14 is restated ("the code point Unicode's simple case mapping gives"); §9 gains a difference row; docs/dev/upstream_issues.md gains the five code points; the `same` cells over them become pcrec-only with the difference recorded.
- **IFACE-5 + IFACE-6: FIX-NOW, one rule.** Every support-unit symbol moves to `pcrec_subst_*` (inside pcrec's reserved internal prefix, cli §1.6¶2 row 3), so no caller prefix can spell one, and the artifact's own names stay `<prefix>_subst_*`. §1¶2 states the rule: artifact names carry the caller's prefix, support-unit names carry `pcrec_subst_`. Grep the sabotage anchors before moving names.
- **IFACE-4:** FIX-NOW for cap < P (NOSPACE + need = P, one code per shortfall); PLAN for > RX_SUBST_BATCH_PAIRS groups.
- **CHK-1:** FIX-NOW (warning-clean plants for S1354/S1374) and the general form too: the sabotage matrix asserts that an emitted-text plant COMPILES before it can score DETECTED (a check that scored a compile failure as a catch is a check that could not fail).
- **PLAN rows filed:** [SUBST-SPEED] (EMIT-1, EMIT-2, EMIT-3); [SUBST-CLEANUP] (HOUSE-2/4/5/6/9/10/11, HOUSE-8 rest, TPL-4, IFACE-4 > 256 groups, CHK-2, CHK-5, CHK-6's two rows, CHK-8 sharing); EMIT-4 joins [DATA-PLAN] (the support unit's case tables: D179 format, and programs with no case template do not link them).
- **DOC items** (IFACE-1/2/3/7/8/9, TPL-2/3) ride the fix lane's spec hunk.
- **Process changes accepted:** skill §6.4 removes the review worktree with `scripts/wtprune --apply --force --quiet-min 1 crit-<topic>`; critics are launched unnamed (a teammate cannot name agents). Lessons 1-3 go to docs/dev/guide/critics.md.
- **D27 spec-first author:** not run in this round; the subst d27 harness on the branch predates R4's extended forms. Recommended before release, not a landing gate.
