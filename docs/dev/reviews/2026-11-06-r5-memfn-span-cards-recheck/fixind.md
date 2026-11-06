# fixind findings — memfn-span-cards-r1 (lens: fix-induced)

Subject: span_cards.md rev 1 @ b06c7447f. Code traced at the review worktree (main 9f5f082de).
W = /home/pcrec/projects/pcrec/worktrees/crit-memfn-span-cards-r1.

## Findings

### fixind-1 — the S2c cell-text check (k) compares a WINDOW-site text with the CANONICAL-instance hash: red on today's `walk`/`libc` by construction
- CONFIRMED (by reading; no render run). FIX-INDUCED (PREMISE-2 builders + PREMISE-3 entry table + COST-5 (10)). Severity: check/design. Effort: small (text). Blast: S2c witness, sabotage (k), every kit-grid@3 key.
- §3.2: cells come from `g2_win_gen.c --cards` on "a window FIND site, stop at the candidate", "wrapped as a `static` function the driver's loop calls"; the witness compares the cell text's hash with `mf_form_hash(<the key's form token>)`, a mismatch red. Same §: the entry-table rows `walk`, `libc` stay "today's, byte for byte".
- Today's canonical instance (W/memfn/src/formhash.c:237-277, header :11-16): a STMT/FIND/ASSIGN site, the walk over the set `[0-9]` through a named table (`table_ref = 1`, table body in the file sink, which is hashed), libc on the byte `x`, `on_miss "return 0;"`. The normalization renames identifiers only; "an operator, a constant, a statement or a call moves the hash" (:26-29). A window site with a one-member stop (D1w/D1) has different constants and statements, plus the wrapper.
- So (k) is red on every `walk`/`libc` cell unless the builder renders exactly the canonical site, which contradicts §3.2's builder table. Not stated: which text the cell hash covers (the form body alone? the wrapper?) and which site the entry table's `stated facts` fix for `pair`/`walk-set`/`rc-*` so cell and canon coincide.

### fixind-2 — SLOT-4's check C guard never sees a kit-grid@3 key: CONTRACT-1 keeps format 2 out of the only directory check C reads
- CONFIRMED. FIX-INDUCED (SLOT-4 crossed with CONTRACT-1). Severity: check. Effort: small-medium. Blast: Goal 3/R-MS3 staleness of zen4-grid3's `deps`.
- check C is the per-ROW loop of `check_sets` (W/tests/memfn/finder_check.py:341-397). It iterates `os.listdir(memfn/data/sets)` only, and resolves a form only from a row key (`parts[2]`, :393-397). §3.8/§5 place no format-2 file there, and sabotage (o) enforces that. zen4-grid3 lives in `measure_store/`.
- `git grep 'kit:form\|form_hash'` over tests/ scripts/: no other check resolves a `measure_store` set's `kit:form.*` deps. arm_fixtures `--hash` (:1655) hashes ids, not set rows.
- Result: the §2.4 half "every key's form token must resolve to a canon id with a hash" has population ZERO for stage 2, at S2c (no keys exist yet) and after S2e (keys outside the read dir). The S2c witness "check C resolves every new dep" reads green with nothing resolved. That is SLOT-4's original defect, moved one directory over. Only the card-level half (a `kit:form.` dep with no `form` dim) can fire, and it fires on cards, not keys.

### fixind-3 — the `cells` section is homed for per-launch medians, but its columns' meanings do not fit, and Goal 3's exact recompute cannot be run from them
- CONFIRMED (text vs spec). FIX-INDUCED (SLOT-1 + MEAS-5 + MEAS-6 + MEAS-7 + MEAS-14). Severity: design (Goal 3). Effort: medium (spec text). Blast: S2c spec §3.4, S2e recompute check, measure_sets §7.2's off-card check.
- Definition of the home: measures.md §2.2¶1 `cells` = `cell group arm length launch round ns_e6`; measure_sets.md:329 "the raw per-launch cells every `fitted` row and every `measured` row of a NULL-rule decision reads"; measure_sets.md:1229-1230 "The checker refuses a row OFF ITS CARD ... whose cells' lengths or subject are not the card's".
- (a) `length` gets two meanings. §3.4 step 2 says "E = the subject's event count per call ..., written in the cell's `length` field". The same step indexes `c(a, LEN, l)` with LEN = 1048576 from the card (`delta base.<form> 1048576 per-hit`). A delta arm's cell cannot carry both. With E in `length`, the lookup by LEN finds nothing, and §7.2's "cells' lengths are the card's" refuses the row.
- (b) `round` is unstated. A cell is the MEDIAN over R rounds (§3.4 step 1), and §3.8 keeps the rounds out of the set. What the round column holds (`-`? 0?) is not said.
- (c) group to job. u_l is "the job's control" (step 3), and drift is per JOB (§3.5), but no cell column names the job. Arm `ctl` repeats once per job, told apart only by `group`, whose naming is unstated. So the recompute cannot pair a row with its u_l or its job's drift verdict.
- (d) Arm names. The unit row's cells are found "by arm = its key" (§4.4 ¶2.2¶5), but in J2 the unit IS the control (§3.3), so they would be arm `ctl` or arm `kit.find_byte.walk`? Is the key spelled with its `kit.` owner? For walk's find_hit base, §3.7 says "the walk's miss base is the control's 1 Mi point", while the card says `base.<form>`, so `base.walk` does not exist.
- (e) Contradiction inside the subject. §2.3 [MEAS-6] says "each density is one row measured inside ONE group against a miss-only base in the same launch", and §3.4 step 2 says "The base is in the SAME group and launch". §3.7's J3 count (3 + 3 + 4 x 12 = 54) puts the 3 bases OUTSIDE the 4 hit groups, one per form, shared by all four. J4 does the same ("2 `null` bases").

### fixind-4 — "the `partial` verdict ... recomputed EXACTLY from cells" (Goal 3) rests on data the set does not hold
- CONFIRMED (text). FIX-INDUCED (SLOT-1, MEAS-7, the Goal 3 restatement). Severity: design/check. Effort: small (state the domain). Blast: S2e recompute check, sabotage (p)/(q).
- §3.5: a group passes iff its cost rows pass, the quiet gate held ("the producer's record, NOT recomputable") and its job is not drift-refused. §3.5 PARTIAL: "the set holds only passing groups' rows". Nothing says whether a refused group's CELLS stay.
- If they go, the recompute cannot show a refused group failed, nor recompute FRG ("the p90 ... over EVERY twinned arm", §3.5).
- If they stay, those are cells no row reads, against §1.5 as amended. The quiet-gate input cannot be recomputed in any case.
- J1's cells (widths, `128#b`, its control) are in the same position: they feed FRG ("every twinned arm"?) and J1's drift, but J1 writes no row. Unstated: the FRG population, and which job/group records the set carries.

### fixind-5 — `lengths` and `aa_rule` are re-purposed in the card table without amending their definition; the estimator grammar adds placeholders the format promises not to have
- CONFIRMED (text). FIX-INDUCED (MEAS-5's "`lengths` names the row's ESTIMATOR"; MEAS-1/4's `twin-per-arm;bimodal-unit`). Severity: maintenance/design. Effort: small (two more hunks). Blast: measure_sets §7.2, measures.md §2.3¶2, kit-grid.tsv header.
- The homes' definitions (measure_sets.md:1221-1223): `lengths` = "the call lengths measured"; `aa_rule` = "the A/A design (`pair-per-group`, `pair-per-launch`, `bimodal-test` for the unit, §1.4)". Rev 1 writes `slope 65536,...` / `delta base.<form> 1048576 per-hit` into `lengths`, and `twin-per-arm;bimodal-unit` into `aa_rule`: a new token, and a rename of `bimodal-test`. §4.4 and §10.2 amend measure_sets §1.4/§1.5/§4.1/:490-494/§3.6/§7.3/§7.4, but never §7.2. kit-grid.tsv's column comment (W/memfn/data/cards/kit-grid.tsv:10-22) is not listed either.
- measures.md §2.3¶2: "The format defines no placeholder token and reads no owner's vocabulary." The new spec §3.4 interprets `base.<form>`, `base.null.<cls>` and `base.fail.<kind>.<entry>` by substituting key tokens by DIM NAME (`form`, `cls`, `kind`, `entry`: owner vocabulary). Until now `deps`' `kit:form.<form>` was provenance text the format never interprets. Rev 1 does not say whether ¶2.3¶2 is amended or the grammar is spelled without placeholders.

### fixind-6 — CONTRACT-3's named detector cannot see a ksgen omission at S2a: CONTRACT-7 removed the field from the view it compares
- CONFIRMED (by reading). FIX-INDUCED (CONTRACT-3 x CONTRACT-7). Severity: check. Effort: small (a sabotage row + a format-2 store fixture, or a raw-field compare). Blast: S2a.
- §4.5 claims that without the ksgen change "the pre-parse holds 0 where a fresh parse holds KS_MEAS_EMPTY and `meas_store_check.c` (pre vs fresh, :72-80) goes red". meas_store_check compares DECODED views (W/tests/knowledge/meas_store_check.c:78, `decode_to(... "pre"...)` vs `"fresh"`). CONTRACT-7: format 1's decoded view gains NO noise field.
- At S2a the only committed set is grid1 (format 1). zen4-grid3 arrives at S2e. A ksgen that leaves the appended field out writes C zero (W/scripts/ksgen.c:347-358, positional initializer), and nothing at S2a sees it.
- If the fill (§4.2) keys MEASURED on the field and not on `format`, grid1 rows are then handed "MEASURED 0" from the pre-parse path only. S2a's sabotage list (a)-(h) has no ksgen row.

### fixind-7 — the loader's noise bound must be a COPIED literal: ks_measures.c may not read MF_MEASURE_MAX, contrary to K138's prescribed form; and that bound's definition does not fit noise
- CONFIRMED. FIX-INDUCED (CONTRACT-5 noise half). Severity: maintenance/design. Effort: small. Blast: S2a spec §2.2¶3a, ks_measures.c, the K138 fix, row 1's band.
- §4.1/§4.4: "pcrec's loader refuses a noise past 10^15", and the spec spells "at most 10^15"; "its noise row reads the same bound so the two refusals agree".
- ks_measures.c DEPENDENCY RULE (W/src/core/ks_measures.c:8-12: "libc and `core/ksrc.h`/`core/ks_measures.h` only") is enforced by tests/core/ksrc_deps_check.sh (a')/(b') (:51-59, :91-99; S1242). It cannot include memfn.h, so the bound is a second home of MF_MEASURE_MAX.
- K138 (W/docs/dev/known_issues.md:22) prescribes "a §7 refusal row for value_e6 above MF_MEASURE_MAX (read from the seam, not copied)". Rev 1 neither says how "reads the same bound" is met nor amends K138's form.
- The definition of the bound being reused (memfn.h:1220-1225): "A SHAPE BOUND ... the finder's comparisons add at most four values ..., which stays inside int64". Noise is used SQUARED in a quadrature sum (§6; span_pick.md:231). 10^15 squared is 10^30, past int64, so the bound's own rationale does not cover the new field. Rev 1 states no bound derivation for noise, and leaves no arithmetic note for row 1.

### fixind-8 — the MFMEAS triple digest: its domain is unstated against the hand rule, and the record's positional reader is unlisted
- SUSPECTED (would be confirmed by S2a's text). FIX-INDUCED (CONTRACT-8). Severity: check/doc. Effort: small. Blast: S2a witness, tests/compound.
- `memfn_measures` hands only `kit.` rows with a value: null rows are skipped (W/src/gen/memfn_sites.c:86-87; memfn.h:1213-1215). §4.2 says ks_ref.py computes the same digest "from the FILE by the format rule". The format rule (MEASURED/UNMEASURED) does not say "skip null and non-`kit.` rows". zen4-grid3 has `null` delta rows by design (§3.5). An implementer following the text digests a different line set, so the witness is red on a correct fill, or both sides get fitted to each other.
- MFMEAS gains two fields, at a position not given. tests/compound/run_part_measures.sh:67-88 reads the record POSITIONALLY ($2 role, $3 stamp, $4/$5 the addresses). It is not in §4.2/§5/§8.2's reader lists (§5 lists that script only for "a synthetic header's text").

### fixind-9 — the per-launch `cells` go into the EMBED, which nobody sized beyond its text; this contradicts the sizing the embed-every-rev ruling rests on
- SUSPECTED (sizes estimated; S2e measures). FIX-INDUCED (SLOT-1). Severity: size. Effort: small (state it, or an embed rule now). Blast: libpcrec.a, every linked binary, the committed .inc files.
- §3.8 "Size" counts ~96 KB of set TEXT only. ksgen also writes every cell into the PRE-PARSE (W/scripts/ksgen.c:344-345, `put_tab(... "cells" ...)`): 7 string literals plus 7 pointers (56 B) per cell. That is about 1,370 x (56 B + the strings again), roughly 77 KB of pointers alone plus relocations. measures_store.inc spells text one byte per line: grid1's 9,562-byte set is 57,708 B of .inc (6x), so about 0.58 MB of committed source for grid3's text.
- Today libpcrec.a's size(1) total is 1,827,353 B, so the add is plausibly 10-15 %.
- The embed-every-rev decision (measure_sets.md:625-628) rests on "47 rows is about 6 KB ... the cells and cards add about 4 KB. Ten committed sets stay below one `fold_tables.inc`". The cells part rests on §1.5 (:430-431): "The cells are few: ... not grid1's 6,725 launches. Cells no row reads are not committed." Rev 1 amends §1.5's sentence but not :625-628's sizing.

### fixind-10 — the manager's `[rev1 D188a1]` edit left rev 1 text standing that contradicts it
- CONFIRMED (grep). FIX-INDUCED (D188a1). Severity: doc. Effort: trivial. Blast: §0, §2.5, §2.7, §9, §10, handoff.
- D188a1 (§2.7 :273-284; header :8; §10 :889) says the model is RULED and J6 is "HELD until [XARCH-DEV]'s go". Still standing:
  - §0 row 8 (:79) "HELD until the SIMD model is ruled";
  - §2.5 table (:217) "HELD until the SIMD model is ruled (§2.7)";
  - §2.5 :240 "until the SIMD model is ruled";
  - §9 S2g (:881) "once the SIMD model is ruled";
  - §10 item 5 (:901-903) "once the model is ruled. Relay to Frank with the model question if useful": there is no model question now;
  - STATE AT HANDOFF (:966) "S2g HELD on the owner's SIMD model".
- The facts are also read two ways. :261-266 read them "Per SIMD level (memfn's `levels.def`)", with (b) "read off that artifact's `MEMFN_FORMS` stamp". D188a1 (:277-284) reads them "PER DECLARED TARGET", with (b) "read off the artifact's declared-target list". :289 and :297 ("per level") keep the level reading. D188 add. 1 says "read per variant's target".
- Also: D188 says "a measurement SET records three facts", but :287-289 homes fact (b) for zen4-grid3 in PROVENANCE.md. That file is outside set.tsv, so outside its sha-256 in index.tsv and outside the digest.

### fixind-11 — §10 cross-references went stale when the DEFAULTS question was ruled out of the list
- CONFIRMED (rev 0 vs rev 1 diff). FIX-INDUCED (PREMISE-4 ruling). Severity: doc. Effort: trivial.
- Rev 0's §10 list was 1 memchr-back, 2 DEFAULTS, 3 bundle noise, 4 match_api. Rev 1's is 1 memchr-back, 2 bundle noise, 3 match_api, 4 scalar row 1, 5 D188 (b), 6 harness retirement.
- Still rev 0's numbering: §4.6 (:700) "For main (§10.3)" should be item 2, and §4.4 (:670) "For main (§10.4)" should be item 3.
- "§10.3" is also now the HEADING "Row 1's design items" (:918), which §2.3 (:165) and §2.5 cite, so the same reference means two things.
- §0 row 9 (:80) says "five items for main"; §10 lists six.

### fixind-12 — DEFAULTS (B): the new and old `index.tsv` rows' `supersedes`/`status` values are not stated
- CONFIRMED (text). FIX-INDUCED (PREMISE-4 (B)). Severity: doc. Effort: trivial. Blast: measure_store/index.tsv, measure_store/CLAUDE.md.
- index.tsv has `supersedes` and `status` (grid1: `current`) (W/measure_store/index.tsv:1-2). measure_sets.md:597 says "Supersession is recorded in `index.tsv` (`supersedes`)". §8.2/§8.3 list "+ `index.tsv` row" only.
- Rev 1 does not say whether zen4-grid3 supersedes zen4-grid1, a different method@ver that §2.1 says is "not compared", or whether grid1 stays `current`. No code reads either column (git grep), so this is a text decision to state.

## PROBED-AND-HELD

- PREMISE-9: three positional `mf_measure` constructors. `git grep '(mf_measure)'` over src/ cli/ memfn/ tests/ finds exactly cli/main.c:160, src/gen/memfn_sites.c:89 and tests/memfn/arm_fixtures.c:1562.
- MF_MEASURE_MAX = 1000000000000000 (memfn.h:1220), so "10^15" matches. The kit's check is at compose.c:891-905 as cited.
- No kit row reads a set key today: the only `fd_value` caller is finder.c:492 (templated keys), and `"kit.` literals in memfn/src are only the owner prefix check. Goal 1's "every stamp `""`" premise holds.
- `--list-measurements` (no value) today prints one row: zen4-grid1 with `default_for idk`. Goal 1's "exactly two rows move at S2e" fits the listing's columns.
- S1229's SAB_BEFORE is `    { "idk", "zen4-grid1", 1u },` as §8.2 quotes. S1244's anchor is `KS_DOMAIN("pcrec-meas-1"), KS_SUB_NONE, meas_fold` (ks_measures.c:245), so "the first's line kept byte for byte" keeps it.
- KsKind `.item`/`.stamp`: no generic reader. `git grep '(->|\.)(item|stamp)\b'` hits only the declarations at ks_measures.c:724-725 and ks_analysis.c:351-352. §4.5's "recorded so a future one reads the right role" is honest.
- The shadow rule (measures.c:131-145) compares `digest`, so under format 2 a FILE set re-using `zen4-grid3@1` with other noise is refused. The format closes the hole as claimed.
- The test levers skip the `cells` section: the harness reader (cli/main.c:105-107, sect 0) and fd_load_set (arm_fixtures.c:1540). The new cells cannot break them, and their line buffers (8192/4096) fit format-2 rows.
- finder_check's card-row shape check (13 kit columns, a §3.1 unit; :337-339) passes the four kit-grid@3 rows. Every grid1 card with a `kit:form.` dep has `form` as its first dim (kit-grid.tsv rows 1-10), so the new deps guard does not fire on existing cards.
- mfixtures.py:177 `("format", hdr("format", "2"), "format 2")` exists as cited. The base fixture already carries numeric noise text (`1730`, :109), which supports sabotage (c).
- K138 exists (known_issues.md:20) as §4.1 cites it.
- D188 add. 1 text vs §2.7: "generic plus 1-2 SIMD" and "each variant's entry exposed" are not in decisions.md's addendum, but they are in [XARCH-DEV]'s RULED line (plan.md@592ed6da3 :1747). Held.
- [KIT-POLICY-TABLE] row exists. Its status line says COVER_Z_E3 is "in plan_cost.def" today, but `git grep COVER_Z` finds nothing. That is the plan row's own stale wording, not the subject's (§6 homes z at row 1). Noted, not a subject finding.
- ks_measures.c:305 (format refusal), ksgen.c:347-358, meas_store_check.c:72-80, memfn_sites.c:406, finder.c:440-451 and finder_check.py:395-399 hold as cited (the last at :393-397, off by two).
