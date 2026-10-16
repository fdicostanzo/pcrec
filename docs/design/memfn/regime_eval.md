# [REGIME-EVAL] — the replay evaluator for the knowledge-filtered regime table (rev 2.4)

Status: **REV 2.4, PROPOSED, design only** (lane `regeval7`, 2026-10-14, branch
`lane/memfn-regeval7` cut from the kit branch `lane/memfn-r17`). Rev 2.4 = rev 2.3 plus ONE
ruling (Frank, 2026-10-14, via the pcrec manager): the evaluator parameter table is not a
private table but one more [KNOW-SRC] KIND, `evaluator-params` (§3.0a). Docs only, plus the
one data file `regime_eval/regime-eval.evaluator-params.tsv`; no build, no timing.

**Change log, rev 2.3 -> rev 2.4** (every change marked `[r2.4 KNOW-SRC]`; §R.6 maps them):

1. **`[r2.4 KNOW-SRC]` The parameter table is a [KNOW-SRC] kind** (`evaluator-params`):
   written in the canonical `#section` shape from day one in
   `regime_eval/regime-eval.evaluator-params.tsv`, which is the source of truth; §3.0a's
   markdown table mirrors its `params` section.
2. **`[r2.4 KNOW-SRC]` The prereg hash IS the kind's digest** (`regime-eval@1:<digest16>`,
   replacing `params_sha256`); the report's diff against prereg IS the census tool's diff
   (`knowledge_census.sh evaluator-params OLD NEW`); the table is listed through
   `--list-evaluator-params`, its canonical view a loadable input (round trip).
3. **`[r2.4 KNOW-SRC]` The placement rule applied to all 72 rows:** 62 stay as harness
   thresholds; EP14 (r-in), EP16 (w-call), EP30 (nu) and EP58 (bucket-edges) are DERIVED
   from timing and MOVE to the measurement set (ids kept; the file's `bindings` section
   names the key each is read from); EP67-EP72 leave the kind (plan arithmetic, script
   literals). Overrides are restated as overrides of a kind's values, unchanged in spirit.
4. **`[r2.4 KNOW-SRC]` `regime_eval/CLAUDE.md`, `memfn/CLAUDE.md` and §10 updated.**

Rev 2.3 status follows. Status: **REV 2.3, PROPOSED, design only** (lane `regeval6`, 2026-10-14, branch
`lane/memfn-regeval6` cut from `lane/memfn-r17`). Rev 2.3 = rev 2.2 plus Frank's three
rulings (2026-10-14, via the pcrec manager): Q-REVAL-12 (the LEAN plan is THE plan),
Q-REVAL-16 (rev 2's constants plus both loosenings) and Q-REVAL-17 (k = 3, WITH A CONDITION:
k is a declared, visible parameter). Rev 2.3 generalises the condition to EVERY chosen
constant that can change a verdict: one evaluator parameter table (§3.0a), pinned by the
prereg, printed at the top of every report, overridable by option, with an overridden run
non-gating. Docs only; no timing, no build, nothing under `src/`.

Rev 2.2: **PROPOSED, design only** (lane `regeval5`, 2026-10-14, branch
`lane/memfn-regeval5` cut from `lane/memfn-r17`). Rev 2.2 = rev 2.1 plus the REAL J1
population ([REGIME-CORPUS] steps 1-2, done on main) and a LEAN plan that leads. Nothing
was timed, nothing was compiled, no `make` ran. Two scripts count the corpus bytes and
the 177 questions (`regime_eval/rev22_population.py`) and recompute the wall and the
power (`regime_eval/rev22_arith.py`). Rev 2.1's status follows.

Rev 2.1: **PROPOSED, design only** (rev 2.1 = rev 2 plus three rulings that landed after it: D166 addendum 1, D166 addendum 1.1 and regime_tables rev 0.4; lane `regeval4`, branch `lane/memfn-regeval4` cut from `lane/memfn-r17`). Rev 2 status follows.

Rev 2: **PROPOSED, design only** (rev 0 lane `regeval`, 2026-10-13, branch
`lane/memfn-regeval` cut from `lane/memfn-r17` at efcc3cd20; rev 1 lane `regeval2`,
2026-10-14, branch `lane/memfn-regeval2`, applies main's review; rev 2 lane `regeval3`,
2026-10-14, branch `lane/memfn-regeval3` cut from `lane/memfn-r17`, applies the D6 panel
r1, `docs/dev/reviews/2026-10-14-r1-memfn-regime-eval.md` §D, all 33 ids). Nothing under
`src/`, `memfn/src/`, `tests/` or `lib/` changed, nothing was timed, and no `make` ran.
The cheap prototype of the replay still runs on the grid1 slot's EXISTING logs
(`regime_eval/replay_proto.py`, §8). Rev 2 adds `regime_eval/rev2_arith.py`, which
recomputes two pieces of arithmetic this revision quotes from finished files (§2.4,
§2.7). The bars change, so E5's pre-registration waits for the zen4-grid2 fit cells
(§2.1, §7).

Every rev 2 change is marked in place `[r1 <id>]`, where the id is the panel's finding
id (M-n, I-n, B-n, or `*-unlock`). §R maps each id to the sections it changed.

**Change log, rev 2.2 -> rev 2.3** (docs only; every change is marked in place `[r2.3]`;
§R.5 maps them by section):

1. **`[r2.3]` ONE evaluator parameter table** (§3.0a, 72 rows: 66 read by the judge, 6 plan
   arithmetic only), each with name, value, unit, what it gates, provenance (CHOSEN /
   DERIVED from <data> / RULED by <who, date>), the override option and where it is
   printed. Every chosen constant of the note moved into it; the prose now refers to it as
   EPnn and does not restate the numbers (§1.2, §2.4, §2.6-§2.9, §3.0-§3.4, §4.2-§4.3,
   §5.3).
2. **`[r2.3]` The override semantics** (§3.0a). Overrides are allowed for exploration. A
   run whose effective parameters differ from the pre-registered ones is NON-GATING and
   labelled "advisory: parameters differ from prereg <hash>", lists every differing
   parameter, and `--final` refuses any override. The prereg file pins the whole table
   and hashes it with the bars (§3.4). Every report begins with the table, the prereg
   value and the diff.
3. **`[r2.3]` Q-REVAL-12/16/17 RESOLVED** (§9, Frank 2026-10-14), and §9.2's entries
   replaced by pointers. The lean plan is THE plan (§2.4, §7 E7, §0); rev 2.1's plan is a
   documented alternative only. cap(LINER) = R_in + 2 and the pooled final reading for a
   sealed regime below G0 are RULED (§2.4, §2.8, §3.1). k = 3 carries its condition: it is
   EP21, printed beside the k = 2 / 4 counts, overridable by `--cb-k=`, with provenance.
4. **`[r2.3]` §10's checklist is extended**, and `docs/design/memfn/CLAUDE.md` and
   `regime_eval/CLAUDE.md` updated. The arithmetic scripts are unchanged: their constants
   are the table's plan-only rows (EP67-EP72) and the LINER cap of the +1 reading they
   price beside +2.

**Change log, rev 2.1 -> rev 2.2** (docs only; two new scripts in `regime_eval/`; every
change is marked in place `[r2.2]`; §R.4 maps them by section):

1. **`[r2.2]` The real J1 population replaces the assumed one** (~140 blinded patterns,
   20 per class, ~70 of them RT; `rev2_arith.py`'s `N_PAT`) (§2.3a). There
   are 177 blinded questions over 7 classes (on main: `docs/dev/lanes/rwquest/`). Without a
   compile, their EXPECTED placement is 54 RT (31%), 116 OTHER, 2 UNREACHED, 1 NOSITE,
   4 GATE-EXCLUDED (`short-pool`) and 0 REFUSE, with 5 `ucp` questions at REFUSE risk.
   **About two thirds of what users asked is led by one literal byte (92) or by `(?m)^`
   (24)**, so its search site is the kit's `pf_memchr` or MLINE, which the table does not
   cover yet. This is the
   §2.3 "first finding", ahead of any regret: P-RT (≥ 40%) is expected to be REFUTED, and
   G0's weight (0.31 against w_min 0.25) is expected to clear by a small margin. Gated cells
   per class × regime are tabulated (§2.3a). The wall is recomputed: rev 2.1's plan costs
   ~309 min on the real population, not ~407 (§2.4).
2. **`[r2.2]` The corpus author's caveats are applied.**
   - (a) Line endings are recorded per subject, and cells carry `eol` and `eol-sensitive`
     labels. ALL prose and non-English files are CRLF, and so are `logs/hadoop.log` and
     `logs/zookeeper.log`, which the corpus report did not flag (§2.3b).
   - (b) Streamed buffers are drawn by a stratified, salt-derived window rule across the
     WHOLE file (and its same-family pool), never from heads. One exemplar reserve is taken
     per pool, and a 1 MiB floor applies (§2.4, §2.8).
   - (c) pg8186, pg8453 and pg20175 are MISLABELLED: they are reported separately, never
     gate, and are never drawn into a pool or an exemplar (§2.3b).
   - (d) The gazetteer's fixed-width rows and the tars' NUL padding get subject-shape labels
     (§2.3b).
   - (e) The blinded author's spawn-time disclosure is a row of §5.1, with the
     primed-intent split as its mitigation.
3. **`[r2.2]` A LEAN plan leads; rev 2.1's plan is the ALTERNATIVE** (§2.4). The lean plan
   is **~131 min in TWO quiet-box windows (~69 + ~62 min)**, with grid2's ~56 min
   separately. It is built from six cuts, and each cut's cost in POWER is stated: cells and
   patterns per layer × regime, gates that fall to UNDERPOWERED/UNREACHED, and controls
   that become unscorable. Five levers were not taken, also with their costs. The power
   table is in §2.4. The gate formulas are unchanged. One looser constant is PROPOSED with
   its arithmetic (cap(LINER) = R_in + 2, Q-REVAL-16), and so is a pooled final reading
   for a sealed regime below G0.
4. **`[r2.2]` J2a's fallback is the default path** (§2.10). Main arranges a byte transfer
   of the bench's 11 subjects of ≥ 1 MiB, each sha-checked against the bench manifest. The
   import-with-kit-seeds route becomes the alternative if the bench says yes (Q-REVAL-15,
   relayed as I-152, no answer yet).
5. **`[r2.2]` Q-REVAL-12 (lean vs full, leaning lean), Q-REVAL-16 (the constants) and
   Q-REVAL-17 (k = 3) are rewritten** so they can be sent to Frank (§9.2). §10's checklist
   is extended. The two rev 2.1 findings bound for the kit manager are left as they stand.

**Change log, rev 2 -> rev 2.1** (docs only; `regime_eval/rev2_arith.py` gains parts 1b
and the without/with-perf wall; nothing timed, no make, nothing under `src/`). Each
change is marked in place `[D166a1]`, `[D166a1.1]` or `[rt0.4]`.

1. **`[D166a1]` No measurement set, method, gate, pre-registered bar, control or tool
   may REQUIRE perf counters** (Frank, binding: "not everyone has the paranoia set to
   2"). A perf pass is an OPTIONAL diagnostic: with counters unavailable it skips loudly,
   the skip is recorded in its own output and in the set's provenance, and nothing
   downstream fails or changes. Sets are producible from timing alone.
   - The consumer-bound class (§2.7) is decided from TIMING ALONE: walk − best ≤ NULL_c;
     the ns spread over K = {walk, V1, A1} ≤ **k·NULL_c with k = 3** (CHOSEN, from the
     F2 cells and gridread's A/A, `rev2_arith_out.txt` part 1b); pick − best ≤ NULL_c
     (condition 3b, kept). The misses test is an UNGATED corroboration column (agree /
     disagree / unavailable) with its own count.
   - Every bar, control, G0-G4 leg, prereg field and refusal rule was audited (§2.7,
     "Audit"); each is ungated or diagnostic. P-PRED's misses figure is optional.
   - Every perf pass assigned to zen4-grid2 or to a judge slot is OPTIONAL. The slot
     arithmetic is shown both ways: **~407 min required (five slots of 75-87 min), ~431
     min with the optional passes** (§2.4); grid2's required wall is ~56 min, its optional
     perf ~6 min (§2.1).
2. **`[D166a1.1]` Suggest, never act.** When counters are unavailable every measuring
   script (grid harness, `time.sh`, the F2 pass) prints a SUGGESTION and never acts on
   it: the current `kernel.perf_event_paranoid`, that 2 or lower enables the optional
   counter pass, what the pass adds, and the one-off and persistent commands. Scripts
   never change system settings. Harness requirements: §1.2.
3. **`[rt0.4]` Re-cited against regime_tables rev 0.4** (main @ a866eae51). A = the
   measurement SET id and a separate key I = ISA availability; this note's own ISA field
   is now that key (§1.1). The amended-D2 row is **R8** (needs P, N, M, A), citing replay
   F-2: every `RD2` is now R8 (§4.1, §4.4, §5.4, §7, §9.2). Q-REVAL-13 (the id) and
   Q-REVAL-14 (the A/I split) are RESOLVED by rev 0.4. [MEASURE-SET]'s trigger is the
   kit's E3 commit (main's design lane `msetdes` is in flight); the general judge is
   main's plan row [TABLE-JUDGE] (§5.5).
4. §10's checklist is extended; §9.2 gains Q-REVAL-17 (k).

**Change log, rev 1 -> rev 2** (kept; D6 panel r1, 20 themes, 33 ids, all ACCEPTED):

1. **An independent pick oracle** (T1, §5.4): a D27-blinded author in a cell writes
   ~60 (knowledge → expected row) cases and a second small evaluator from regime_tables'
   prose rows only. `regime_pick` must match every case, and the condition plants must
   fail some.
2. **UNSCORABLE rows and controls are declared** (T2, §3.3, §4.1-§4.2, §4.4): R3a, R3b,
   R4 (every H-keyed row) and C2 are twin-owned, excluded from G4 and never counted as
   passed. C3 is per moved cell, with a quadrature noise rule and a minimum moved count.
   The pending amended-D2 row gets an id (`RD2`, proposed; `[rt0.4]` it is **R8** in regime_tables rev 0.4). H rows are exempt from the
   witness rule.
3. **Every bar is a stated formula in walk-cost units, with its noise rule, power floor
   and the sealed holdout** (T4/T5/T6/T9, §3.0-§3.1). The noise rule is quadrature over
   independent timing groups. The G2 caps come from a STREAMED in-sample replay of fit
   cells that run in zen4-grid2, so E5 waits for grid2. G3 is a per-pass test. A thin
   bar reads UNDERPOWERED, and a thin population reads UNREACHED (G0).
4. **The consumer-bound class leaves the denominator only** (T7, §2.7). Condition 3b
   (pick − best ≤ NULL) keeps pick losses in G3. The spread uses the fixed arm set
   K = {walk, V1, A1}. F2's quote is corrected from `gridread/f2_counts.txt` (B-7).
5. **Winner's curse and A/A** (T8, §1.3, §4.3): cross-fit regret (the best is chosen on
   the other launches and scored on the held one), a split-half C7, a third walk arm
   `walk#c` as an independent A/A and drift anchor, a null-mutation control C8, and
   per-arm A/A where it exists.
6. **Contamination and sealing** (T9, §2.8): a sha256 disjointness proof, J2a ∩
   ALPHA/spike/costmodel inputs counted and non-gating, ~30% of J1 sealed as a
   final-only holdout, J1b written now and committed unopened, every prereg version
   listed, and main's slot request as the ordering authority.
7. **Populations counted** (T10, §2.3, §2.6, §3.1): a sixth class GATE-EXCLUDED, RT
   per timed group, partial cells counted and capped, G0's RT floor, and an RT-share
   weight floor.
8. **Evaluator plants** (T11, §5.3): a second independent parser, an oracle-policy
   control, a planted E-leak, the evaluator's blob shas in `prereg.tsv`, main's journal
   as the time authority, and a rollback trigger on a PROVISIONAL PASS.
9. **Slots** (T12, §2.4): recomputed with four `lines` buckets, WITNESS cells, `walk#c`
   and a rerun budget. That is 785 groups, ~431 min in five slots of 79-92 min (rev 1
   had ~226 min). It adds a load1-breach abort rule.
10. **Wrong-box sets** (T13, §2.9, §1.1): refused unless the run is a declared C6; a
    per-slot FIT anchor replay reads SET-MISMATCH; the knowledge record gains an ISA
    key `I`.
11. **The bench boundary** (T15, §2.10): J2a imports only the bench's text libraries,
    from a `git archive` extract of a pinned bench commit, with kit seeds and a kit
    output dir. The fallback is condition W on the bench's existing ≥ 1 MiB subjects.
    The relay question is Q-REVAL-15.
12. **Smaller items**: shadow trace at E3 (T3); report-only inherited CB on Zen 1
    (T14); controls through `regime_pick` until [MEASURE-SET], with E3 owing the deny
    rows' D80 hunk (T16); `--diff` renamed an advisory pick census (T17); the interim
    set and E labelled, with the ownership words (T18); re-cited against regime_tables
    rev 0.3 (T19; `[rt0.4]` now rev 0.4); the `picks.tsv` + `arm_ns.tsv` interface and nothing more general
    (T20); memfn/CLAUDE.md's boundary table (side).
13. New open questions Q-REVAL-12..16 (§9.2). §9 "Questions — resolved" is unchanged.

**Change log, rev 0 -> rev 1** (main's review, 2026-10-14; kept):

1. **Judge cells are STREAMED** (§2.4, §3.4 `prereg.tsv`, §2.6). F2 measured the walk's
   branch misses far lower on repeated 64 KiB buffers than on fresh 1 MiB text (rev 2
   corrects the quoted range, §2.4 [r1 B-7]), so a repeated judge flatters the walk
   where the table picks forms. Repeated 64 KiB survives only as a labelled, UNGATED
   column that reports the predictor-training effect (P-PRED).
2. **Consumer-bound cells are a COUNTED class** (§2.7).
3. **New reported quantity P-MOVE** (§3.2).
4. **§9 is now "Questions — resolved"** (main, 2026-10-14).
5. **§8** notes that regime_tables corrections 1-4 were accepted and applied by main.
6. §10's charter-vs-committed checklist is extended.

Owner (Frank, 2026-10-13): the kit owns the rows, this evaluator and the twin
([REGIME-TWIN]). pcrec owns the knowledge plumbing ([REGIME-LANDINGS]), the iterator
([FINDALL-NEXT], D165), the measurement sets ([MEASURE-SET], D166), the engine arms,
and comments on the kit's work. **`[r1 B-8]` For the measurement sets the split is:
pcrec owns the set FORMAT, LOADER, STORE and STAMP; the kit owns the VALUES and the
METHOD that measures them.**

Inputs read: **`[rt0.4]` main's `docs/design/regime_tables.md` rev 0.4 (main @
a866eae51, read via `git show main:`; rev 2 read rev 0.3 at aad0199d9, `[r1 B-6]`)**; D27, D144 (+ add. 1, 4), D147, D161 add. 11-12, D162
(+ add. 1-4), D165 (+ add. 1), D166; plan rows [REGIME] and children; `costmodel_report.md`,
`gridread_report.md` (+ `gridread/`, including `f2_counts.txt`), `grid1_report.md` +
`grid1/README.md`, `vecspike_reading.md`; `memfn/docs/responses.md` through the D161 add.
11 notice; the D6 panel r1 review file. **`[r1 B-1]` pcrec-bench read READ-ONLY at
db629a54** (`git show` only): `bench/bounded/gen_throughput_subjects.py`,
`bench/bounded/boundedtext.py`, `bench/loglines/logtext.py`, the headers of
`captext.py`/`censustext.py`/`utf8text.py`, and every `manifest_throughput.tsv`.
Nothing was run inside the bench tree. **`[r2.2]` Rev 2.2 also read, from main via `git
show`, `docs/dev/lanes/rwcorpus/` (manifest.tsv: 88 rows, 7 classes; CLAUDE.md,
PROVENANCE.md), `rwcorpus_report.md`, `docs/dev/lanes/rwquest/` (questions.tsv: 177
questions; CLAUDE.md) and `rwquest_report.md`, plus the corpus BYTES in
`worktrees/.corpus/` (read-only, counted by `python3 -I`, nothing executed).**

Vocabulary: a **cell** is one (pattern/site, subject slice, mode, call shape). A
**group** is one timed harness group (one cell's arms, timed together; a cell at both
layers is one group). A **form** is a kit search form (WALK, V1 = SWAR W=8, S1/A1 =
SSE2/AVX2 W=64, V3/S3/A3 = the same with state kept across calls). **Regret** =
measured ns of the table's pick − measured ns of the fastest form the layer offers on
that cell (rev 2: cross-fit, §1.3). **The walk** is the scalar table walk, the D147
floor every percentage is quoted against. **Walk-cost units** `[r1 B-9]`: a quantity
divided by the walk's ns on the same cells, so a bar reads the same on any box.

## R. Panel r1 disposition (by id)

The binding table is the review's §D. This table maps each id to the section(s) it
changed, so completeness is checked by id: 11 M + 9 I + 10 B + 3 unlocks = 33, plus the
"side" row.

| id | theme | what changed | section(s) |
|---|---|---|---|
| M-1 | T4 | G2 caps from a STREAMED in-sample replay (zen4-grid2 fit cells), in walk-cost units; a rep64k cap check printed beside | §2.1, §3.1 (G2), §3.4, §7 (E4b, E5) |
| M-2 | T5 | G3 is a per-pass test; per call only for `first`/`lines`; the Σ ≤ 0 clause defined | §3.1 (G3) |
| M-3 | T6 | quadrature noise over independent groups; power floors read UNDERPOWERED | §3.0, §3.1, §4.2 |
| M-4 | T7 | CB leaves the denominator only; spread over K = {walk, V1, A1}; F2 streamed perf pass in grid2 | §2.7, §3.1, §2.1, §7 |
| M-5 | T8 | cross-fit regret; `walk#c` as independent A/A and drift anchor | §1.2, §1.3, §4.3, §2.9 |
| M-6 | T9 | sha256 disjointness proof; J2a ∩ ALPHA/spike contaminated; ~30% of J1 sealed; every prereg version listed | §2.2, §2.8, §3.4 |
| M-7 | T12 | wall recomputed (length buckets, WITNESS, `walk#c`, reruns); five slots; load1-breach abort rule | §2.4 |
| M-8 | T13 | refuse set.box ≠ run box unless C6; per-slot FIT anchor replay; SET-MISMATCH | §2.9, §3.4, §4.1 (C6) |
| M-9 | T12 | +2 launches for a group whose A/A disagrees by more than NULL (pre-registered) | §1.2, §2.4, §3.4 |
| M-10 | T14 | inherited CB labels on Zen 1 are report-only, never gate | §2.7, §2.4 (J4) |
| M-11 | T11 | blob shas of the evaluator, `regime_pick` and the CB classifier in `prereg.tsv`; main's journal is the time authority; rollback trigger on PROVISIONAL PASS | §3.3, §3.4 |
| M-also | T4/T12 | populations, classes and pattern medians printed separately; regret against walk − EXT consumer; neither streamed condition is DRAM-bound | §6.1, §2.4 |
| M-unlock | T20 | a table-agnostic replay harness: the interface only | §5.5 |
| I-1 | T1 | the blinded pick oracle (D27 cell): cases + a prose-row evaluator; plants must fail cases | §5.3, §5.4, §7 (E3b) |
| I-2 | T2 | UNSCORABLE rows and controls; C3 per moved cell with a minimum moved count | §3.3, §4.1, §4.2, §4.4 |
| I-3 | T7 | condition 3b; CB-with-pick-loss cells stay in G3; with-class gates printed | §2.7, §3.1 |
| I-4 | T8 | split-half C7; null-mutation control C8; per-arm A/A | §4.1, §4.3 |
| I-5 | T10 | GATE-EXCLUDED class with per-arm counts; partial cells counted and capped; G0 RT floor; RT per timed group; RT-share weight floor | §2.3, §2.6, §3.1 (G0), §6.1 |
| I-6 | T9 | J2a ∩ ALPHA/spike/costmodel non-gating; J1b now, hash unopened; (W) byte-range check; prereg sha in main's slot request | §2.2, §2.8, §3.4 |
| I-7 | T11 | second independent parser; oracle-policy control; planted E-leak | §5.3 |
| I-8 | T19 | `lines` bucket edges from the set under test (and the control sets); no edge inside a bucket | §1.3, §2.4 |
| I-9 | T4 | G2 caps and G3 constants labelled not independent; headline = held-out − in-sample | §3.1, §6.1 |
| I-unlock | T20 | a decision-table evaluator for pcrec's tables: the input side kept pluggable, nothing built | §5.5 |
| B-1 | T15 | J2a reads the bench's text libraries only, read-only, kit seeds and output dir; fallback W; relay | §2.2, §2.10, §9.2 (Q-REVAL-15) |
| B-2 | T16 | C1/C5/C6 through `regime_pick` until [MEASURE-SET]; E3 owes the deny rows' D80 hunk and registry floor pin; [MEASURE-SET]'s trigger is E3 | §5.2, §7 (E3), §R.2 |
| B-3 | T3, T2 | E3 carries a trace-only shadow call; witness rule exempts H rows; pending row id | §5.3, §4.4, §7 (E3) |
| B-4 | T17 | `--diff` is an advisory pick census; D166's mover census is pcrec's | §6.1, §9.1 |
| B-5 | T13 | ISA key `I` in the knowledge record; the D157 note on the range-term count | §1.1, §R.2 |
| B-6 | T19 | re-cited rev 0.3; C3 row list, §8 header, §4.4 fixed; F-1 → F-2 relayed | header, §4.1, §4.4, §8, §R.2 |
| B-7 | T7 | F2's numbers corrected; P-PRED expects no change on bounded | §2.4, §2.7, §3.2 |
| B-8 | T18 | interim set labelled, converter and zero-mover `--diff` at [MEASURE-SET]; ownership words; surrogate-E agreement check and fresh S1/S3 prereg at [REGIME-LANDINGS] | header (Owner), §1.1, §5.2, §7 |
| B-9 | T4 | G3's floor and NULL's ratio in walk-cost units / re-derived per slot; CB constants marked Zen 4 | §1.3, §2.7, §3.1 |
| B-10 | T9 | J2a ∩ ALPHA disjointness counted (K35) | §2.2, §2.8 |
| B-unlock | T20 | the CONTRACT is table-agnostic at the cost of an interface: `picks.tsv` + `arm_ns.tsv` | §5.5, §6.1 |
| side | — | memfn/CLAUDE.md's boundary table gains the regime table, the evaluator and measurement sets | `memfn/CLAUDE.md` (this branch) |

### R.1 What changed in the bars, at a glance

| bar | rev 1 | rev 2 |
|---|---|---|
| G0 | — | NEW: RT floor per layer × regime × filter; below it the gate reads UNREACHED |
| G1 | Σ regret ≤ Σ regret(P) + Σ NULL over differing cells (linear) | the same, with quadrature noise over groups, cross-fit regret and a power floor |
| G2 | % caps = repeated in-sample + headroom; CB cells out of numerator and denominator | caps = f(STREAMED in-sample from grid2), walk-cost units; CB out of the denominator only; noise allowance; power floor |
| G3 | per call: > 50 ns AND > 25% of walk | per pass (and per call for `first`/`lines`), floor 3 × the set's walk per-call cost; Σ ≤ 0 defined |
| G4 | every control WORSE; C3 summed against a 1-point floor | scorable controls only; C3 per moved cell; UNSCORABLE twin-owned; C7 split-half; C8 null mutation; evaluator plants |

### R.2 Relayed to main (from the review's §D, and new from this revision)

1. regime_tables §2's key A ("ISA + tuning class") conflicted with D166 item 3. This note
   split it: A = the measurement set id, and I = the ISA level (§1.1). (B-5)
   `[rt0.4]` RESOLVED: rev 0.4 has A = the set id and a separate key I = ISA
   availability (Q-REVAL-14).
2. regime_tables §3's pending row cited "replay F-1" for the 6.0% S3-on DINGHY figure;
   it is **F-2** (§8). (B-6) `[rt0.4]` RESOLVED: row R8 cites F-2.
3. [MEASURE-SET]'s trigger is E3: E3 creates the row denies and needs set files the
   compiler can read (§5.2, §7). (B-2) `[rt0.4]` Stated for main's design lane
   `msetdes` (in flight): the trigger is the kit's E3 commit.
4. A table-agnostic judge INTERFACE is filed (§5.5): `picks.tsv` + `arm_ns.tsv`, no
   general judge built (D77). `[rt0.4]` The general judge is main's plan row
   [TABLE-JUDGE]. Trigger: a second first-match table with a measured
   threshold that needs a verdict (candidates: the reseed rows, [PRIOR-COST-UNIFY],
   [SEL-COST]). (T20)
5. zen4-grid2 carries the evaluator's owed cells (§2.1): the streamed in-sample fit
   cells, the FIT anchor subset, and `walk#c`. E5 waits for them. (T4/T7) `[D166a1]`
   The F2 streamed perf pass and the perf pass on the fit cells are OPTIONAL there and
   no longer gate E5.
6. NEW: the pending amended-D2 row needed an id; the kit proposed `RD2` (Q-REVAL-13).
   `[rt0.4]` RESOLVED: it is R8 in rev 0.4. One observation for main: R8's condition
   reads g ("g >= ~4 B", an E fact) while its `needs` column lists P, N, M, A. Under S0
   (no E) the g clause cannot be evaluated. The kit's pick function reads `needs` as
   written until main says otherwise; the blinded oracle (§5.4) will see the same text.
7. NEW: the J2a subject question for the bench dev (Q-REVAL-15). `[r2.2]` Relayed as
   I-152. The byte-transfer fallback is now the default (§2.10).
8. `[r2.2]` NEW for main:
   - (a) J1b is owed. rwquest delivered one list, and its author should get a brief
     without the lanes index (§5.1).
   - (b) The coverage finding (§2.3a): about two thirds of the blinded questions are
     led by one literal byte or by `(?m)^`, so their site family is OTHER. This is
     input to D161 addendum 11's widening, and it is not a regime-table defect.
   - (c) `logs/hadoop.log` and `logs/zookeeper.log` are CRLF, which rwcorpus's report
     does not record.

### R.3 Rev 2.1: the three rulings, by section

| ruling | what changed | sections |
|---|---|---|
| D166 add. 1 (`[D166a1]`) | CB decided from timing alone (k = 3, CHOSEN); perf misses an ungated corroboration column; the audit table; P-PRED/P-CB/prereg/E4b/J4 made optional or timing-based; perf passes in grid2 and the judge slots optional; the slot wall shown with and without them (~407 / ~431 min) | §1.2, §2.1, §2.4, §2.7, §3.2, §3.4, §7, §9.1, §9.2 (Q-REVAL-17) |
| D166 add. 1.1 (`[D166a1.1]`) | the counter-unavailable SUGGESTION, never an action; the harness requirement and its check | §1.2, §7 (E4) |
| regime_tables rev 0.4 (`[rt0.4]`) | A = set id and key I = ISA; R8 replaces RD2; Q-REVAL-13 and -14 RESOLVED; [MEASURE-SET]'s trigger is E3 (`msetdes` in flight); [TABLE-JUDGE] | header, §R.2, §1.1, §4.1, §4.4, §5.2, §5.4, §5.5, §7, §8, §9.2, §10 |

### R.4 Rev 2.2: the real population and the lean plan, by section `[r2.2]`

| item | what changed | sections |
|---|---|---|
| real J1 population | 177 questions placed without a compile (ESTIMATE): 54 RT / 116 OTHER / 2 UNREACHED / 1 NOSITE / 4 GATE-EXCLUDED / 0 REFUSE (5 ucp at risk); cells per class × regime under two bracketing readings; question mode → call shape; one subject pool per question | §2.2, §2.3, §2.3a, §3.2 (P-RT) |
| caveat (a) CRLF | `eol` per subject (crlf / lf / one-line / binary), `eol-sensitive` cells, `lines` split at LF with the CR kept in N | §2.3b, §2.4 |
| caveat (b) heads | stratified salt-derived 64 KiB windows across the whole file and its same-family pool; one exemplar reserve per pool; a 16-window (1 MiB) floor, `short-pool` below it | §2.4, §2.8, §2.3 (exemplar) |
| caveat (c) mislabelled | pg8186, pg8453, pg20175 reported apart, never gate, never pooled | §2.3b |
| caveat (d) shapes | `periodic-200` (gazetteer), `nul-padded` (tars), `compressed` labels; per-cell landing-gap quantiles printed | §2.3b, §6.1 |
| caveat (e) disclosure | a §5.1 row; the J1 headline printed overall, primed-only and unprimed-only | §5.1, §6.1 |
| lean plan | ~131 min in two windows; six cuts and three levers each priced in power; rev 2.1's plan re-costed at ~309 min as the alternative | §2.4, §7 (E7) |
| power | G0-G4 status per plan, both readings; cap(LINER) + 2 and a pooled final reading for an underpowered sealed regime PROPOSED | §2.4, §3.1, §2.8, §9.2 |
| J2a | the byte-transfer fallback is the default; import is the alternative | §2.10, §9.2 (Q-REVAL-15) |
| questions | Q-REVAL-12, -16, -17 rewritten for Frank | §9.2 |

### R.5 Rev 2.3: the parameter table and the rulings, by section `[r2.3]`

| item | what changed | sections |
|---|---|---|
| parameter table | 72 rows, one place; prose refers by EP id (rev 2.4: now a [KNOW-SRC] kind, §R.6) | §3.0a, §1.2, §2.4, §2.6-§2.9, §3.0-§3.4, §4.2, §4.3, §5.3 |
| override semantics | exploration allowed; differing run is advisory and non-gating; `--final` refuses any override; the prereg pins and hashes the table; report-top block with the diff | §3.0a, §3.4 |
| Q-REVAL-12 | lean plan is THE plan; rev 2.1's is a documented alternative | §0, §2.4, §7 (E7), §9 |
| Q-REVAL-16 | constants agreed; cap(LINER) = R_in + 2 and the pooled final reading RULED | §2.4, §2.8, §3.1, §9 |
| Q-REVAL-17 | k = 3, a declared visible parameter (condition) | §2.7, §3.0a (EP21, EP22), §3.2, §9 |
| checklist | rev 2.3 rows | §10 |

### R.6 Rev 2.4: the parameter table is a [KNOW-SRC] kind, by section `[r2.4 KNOW-SRC]`

| item | what changed | sections |
|---|---|---|
| kind and file | `evaluator-params`; `regime-eval.evaluator-params.tsv` in canonical `#section` shape (`header`, `params`, `bindings`) is the source of truth; the markdown mirrors it | §3.0a, the file |
| prereg hash | the kind's digest (`regime-eval@1:<digest16>`), replacing `params_sha256`; plus the measurement-set stamp the moved rows read from | §3.0a, §3.4 |
| report diff | `knowledge_census.sh evaluator-params OLD NEW`; the report prints the kind, digest and moved rows' set | §3.0a (What every report prints) |
| listing | `--list-evaluator-params`; the canonical view is a loadable input; `params.tsv` of a run is that view | §3.0a |
| placement rule | 62 rows stay; EP14, EP16, EP30, EP58 move to the measurement set (`bindings`); EP67-EP72 leave (plan arithmetic); EP56/EP57/EP47 kept with reasons | §3.0a |
| overrides | unchanged in spirit, restated as overrides of a kind's values; moved rows overridden by literal or FILE (a set) | §3.0a (Override semantics) |
| checklist | rev 2.4 rows | §10 |

## 0. Summary

1. **Replay, not modelling.** The evaluator asks the BUILT table what it picks for each
   cell's knowledge record and looks up that form's measured ns. The best form is the
   fastest TIMED arm, never a prediction, and `[r1 M-5]` it is chosen and scored on
   different launches (cross-fit), so the minimum over noisy arms does not bias regret.
   It cannot see dispatch cost; [REGIME-TWIN] owns that term (§1.4).
2. **Fit on grids, judge on held-out text, judged STREAMED.** Thresholds come only from
   synthetic grids, published as a measurement set (D166). `[r1 M-1]` The bars' in-sample
   reference is a STREAMED replay of the fit cells, which zen4-grid2 times (§2.1). The
   judge populations are the [REGIME-CORPUS] subjects × the blinded user patterns (with
   ~30% SEALED until the final reading, `[r1 M-6]`), the bench's population (its
   ALPHA/spike overlap counted and non-gating, `[r1 B-10]`), and later Zen 1.
   `[r2.2]` The real J1 is 177 questions; about 54 of them reach the table (estimate,
   §2.3a). The plan is the lean one (RULED, Q-REVAL-12), ~131 min in two quiet-box windows (§2.4); rev 2.1's plan stays as a documented alternative only.
3. **Pre-registered, loose acceptance** (§3; `[r2.3]` every constant a visible row of the parameter table, §3.0a, an overridden run advisory): five gate bars per layer and shipped
   filter (G0 population floor, G1 aggregate dominance, G2 per-regime caps, G3 outlier
   budget, G4 evaluator validity), each `[r1 M-3]` a stated formula in walk-cost units
   with a quadrature noise rule and a power floor. Predictions and reported quantities
   never gate. The bars file pins the evaluator's own blob shas, and main's journal and
   slot request order it before any judge timing (`[r1 M-11]`, `[r1 I-6]`).
4. **Failing-direction controls** (§4), expressed through set files and row denies
   only. `[r1 I-2]` Controls on H-keyed rows cannot be scored by replay and are handed
   to the twin, listed and never counted as passed. Row deletion is judged per moved
   cell. `[r1 I-4]` A null-mutation control shows the evaluator does not call
   everything WORSE.
5. **The table is checked against something that is not itself** `[r1 I-1]`: a
   D27-blinded author writes cases from the prose rows, and `regime_pick` must match them
   (§5.4).
6. **The prototype already pays.** Replaying rev 0.2 on the grid it was fitted from
   reproduces §3's S0 row exactly. It also found the four corrections main applied as
   regime_tables rev 0.3 (§8, F-1..F-8). `[rt0.4]` Rev 0.4 adds R8 and the A/I split.

## 1. The replay: inputs and output

### 1.1 The cell and its knowledge record

A cell is `(site, subject, mode, call)`:

| field | values | source |
|---|---|---|
| site | pattern id + kit site index (an artifact may hold several; D165 add. 1 says one stateful FIND per search entry today) | the compile; the kit's MF_TRACE site list |
| subject | corpus file id + slice (offset, length) + sha256 of the slice bytes | the [REGIME-CORPUS] manifest; slices at fixed offsets |
| mode | `first` (one call from 0), `all` (find-all through `_search`, match_api.md §3.1), `iter` (find-all through the iterator; emulated by grid1's keep arm until D165 builds, §3.3) | the timing row |
| call | `whole` (the slice is the subject) or `lines` (one call per line, the grep shape; a new harness mode, §2.4) | the timing row |

Each cell has one KNOWLEDGE record, keyed as in regime_tables §2 (`[rt0.4]` rev 0.4). A filter
S0-S3 masks it:

| key | value in a cell | where it comes from | filters |
|---|---|---|---|
| P | site kind (PF scan / DFA hat / VM hat / MLINE), term count, RANGE-term count, layer (SIMD on/off) | the compile: the kit's site description in the MF_TRACE build (the same dump `n2_census.py` reads). `[r1 B-5]` D157 note: the RANGE-term count is KIT-DERIVED from the site's byte set (`set[32]`); pcrec sends no such field | all |
| N | `n − startpos` at call entry | the call shape: whole → slice length; lines → each line's length (the replay uses the per-call distribution, §1.3) | all |
| M | one-shot or iterator | the mode | all |
| E | landing gap g per candidate stop | **before [REGIME-LANDINGS]**: the evaluator derives g from an EXEMPLAR file of the same class, never the timed slice, using pcrec-analyze's unigram and bigram counts. `[r1 B-8]` This is a SURROGATE producer, labelled `E=exemplar-bigram(kit)` on every figure. **After**: the analysis object's landings kind (`E=analysis(landings)`, D162 provenance); the switch is gated by an agreement check and a fresh S1/S3 pre-registration (§7, E13). An ORACLE arm (`E=oracle`, counted on the timed slice) is reported as an upper bound and never gates. | S1, S3 |
| H | the previous step's span; candidates per block | the counting twin (`cnt`, never timed): activation span ADV/A per call; per-block popcounts from the `blocks`/`uses` counters | S2, S3 |
| A | WHICH MEASUREMENT SET (D166 item 3; `[rt0.4]` regime_tables rev 0.4's key A) | a set file: id, box, run, method version, values relative to the walk's per-byte cost, with absolute ns as provenance only. `[r1 B-8]` Until [MEASURE-SET] exists the kit writes the set in its own TSV, LABELLED in its header `kit-private interim set (pre-[MEASURE-SET]); format owner pcrec`. The evaluator reads the set by id and records its sha256. | all |
| **I** `[rt0.4]` (rev 0.4's key I, ISA availability) | the ISA level the artifact may use: none (SIMD-off) or a `memfn/src/levels.def` level (today `LV_X86_W16`, SSE2, and `LV_X86_W32`, AVX2 / x86-64-v3) | the run's declared arm (`-fmemfn-simd` plus the target level). It selects between the SSE2 forms (S1/S3) and the AVX2 forms (A1/A3), which regime_tables rev 0.4 §3 calls DISTINCT arms with their own thresholds. On Zen 4 the default arm is `LV_X86_W32` (A1); an S-row judgement is a declared `LV_X86_W16` arm. | all (SIMD-on) |

`[r1 B-5]` `[rt0.4]` Rev 2 found regime_tables §2 defining A as "ISA + tuning class"
(pre-D166) and split it in this note. Rev 0.4 adopts the split: **A = the measurement
SET id, I = ISA availability, two separate keys.** This note's own ISA field IS key I
and nothing here carries a second spelling (§R.2, Q-REVAL-14 RESOLVED). The tuning class
is a property of the set (its box), not a key.

### 1.2 The measured ns of every candidate form

The measured ns come from the grid1 harness, the kit's standing instrument
(`docs/dev/lanes/grid1/README.md` is the arm contract):

- **Base arm (`walk`).** The kit-branch compile of the pattern with
  `--memfn=no-pf-terms-mask`.
- **A/A arms `[r1 M-5]`.** `walk#b` (as in grid1) and NEW `walk#c`: the same
  artifact as `walk`, three times. `walk`/`walk#b` give the cell's A/A floor (NULL,
  §1.3). `walk#c` is held out of NULL: it is C7's independent A/A (§4.3) and the slot's
  noise-ratio source ν (§1.3). Where the harness repeats another arm (`V1#b`), that
  arm's own A/A is used for differences involving it (per-arm A/A, `[r1 I-4]`).
- **V1 arm.** The default compile (R17-b's `pf_terms_mask`).
- **S1/A1, S3/A3/V3, Sn/An arms.** `mkvar.py` builds these from the V1 artifact. It
  edits only the site's struct and its `next_candidate`. `build.sh` proves that
  `gen(w8,0,0)` assembles identically to V1. Once the SIMD rows are BUILT (R17-b″),
  real kit renderings replace the hand edits for those forms, and the hand edits
  stay only as twins.
- **Both layers in every cell (Frank, 2026-10-13: "this entire effort is BECAUSE of
  simd").** The SIMD-off layer offers {walk, V1}; the SIMD-on layer adds {S1, A1}
  (selected by I, §1.1). The iterator variants add the kept forms. Each layer's best is
  taken over its own arms.
- **pcrec's engine arms (grid1's EXT arms, lane slotarms).** They hold the CONSUMER
  fixed. The evaluator reads EXT rows only to report the consumer's share of a cell's
  time, and `[r1 M-also]` to report regret against (walk − EXT consumer ns), the
  scan-attributable time (§6.1). It does NOT judge pcrec's own route table
  (`cand_rows[]`), which is pcrec's.
- **Correctness gate first** (`check.sh`, legs R, L and C). Every arm's answer line
  and match list equals the base's. The base equals the reference oracle (libpcre2
  10.46 through `tests/oracle/`'s local adapter). A cell that fails the gate is
  GATE-EXCLUDED and counted per failing arm (§2.3, `[r1 I-5]`), never timed. An
  answer failure of a PICKABLE arm is a hard FAIL of the run: that is a wrong kit form,
  not a timing question.
- **Measurement.** As grid1: `taskset` CPU 14, governor `performance`, the quiet gate
  (load1 < 1.5, checked at every group boundary, with the abort rule of §2.4), rotated
  interleaving, LAUNCHES launches of 7 rounds, the per-launch median. **The subject
  condition is part of the measurement (§2.4):** judge groups run STREAMED or on a
  whole subject ≥ 1 MiB.
- **Reruns `[r1 M-9]`.** A group whose `walk` vs `walk#b` A/A, per launch, disagrees by
  more than its NULL in any launch gets EP29 more launches (EP27 → EP27 + EP29), decided by the harness at the end of the group from that rule alone (pre-registered in `prereg.tsv`). The wall budget assumes the EP69 share of groups rerun (§2.4); the share actually rerun is reported.
- **Branch-miss pass (perf): OPTIONAL `[D166a1]`.** `perf_event_paranoid` is 2 on this
  box, so user-space events work here; nothing in this note requires that anywhere. A
  slot or grid MAY run F2's pass (`grid1/f2perf.sh`:
  `cycles:u,instructions:u,branches:u,branch-misses:u`, 3 launches) on a group, `[r1 M-4]`
  on the fixed arm set K = {walk, V1, A1} only (§2.7). It feeds only the ungated CB
  corroboration column and P-PRED's misses figure (§2.7, §3.2). When counters are
  unavailable it SKIPS LOUDLY: `f2perf.sh` already writes a named `F2_SKIPPED` line and
  exits 0; the skip is also recorded in the pass's output and in the set's provenance
  (`perf: ran | skipped (paranoid=N)`), and nothing downstream fails or changes. A set is
  producible, and a pre-registration valid, with `perf: skipped`.
- **Harness requirements: counter suggestions `[D166a1.1]`.** Every measuring script
  (the grid harness `slot.sh`/`time.sh`, `f2perf.sh`, and any later pass) must, when the
  counters are unavailable, print a SUGGESTION (to its log and to the pass's status file)
  and NEVER act on it. The suggestion states:
  1. the current `kernel.perf_event_paranoid` value (read from
     `/proc/sys/kernel/perf_event_paranoid`; `?` if unreadable);
  2. that a value of 2 or lower enables the optional counter pass;
  3. what the pass adds: branch misses and the predictability diagnosis (the ungated CB
     corroboration, P-PRED's misses figure);
  4. the commands: one-off `sudo sysctl kernel.perf_event_paranoid=2`; persistent, a file
     `/etc/sysctl.d/99-perf.conf` containing the line `kernel.perf_event_paranoid = 2`.
  The scripts never run `sysctl`, never write under `/etc`, never use `sudo`, and never
  change any system setting. E4 (§7) owes the change to `slot.sh`/`time.sh`/`f2perf.sh`
  and a check that the suggestion text appears when the probe is forced to fail, that
  the skip reaches the provenance, and that no `sysctl`/`sudo` appears in the scripts.

### 1.3 The output

For every (cell, layer, filter):

- **the pick**: the row that fired and the form it chose (`picks.tsv`, §5.5);
- **the best, cross-fit `[r1 M-5]`**: for each launch l of the cell's L launches, the
  arm that is fastest on the median of the OTHER launches, b(−l), is scored by its ns
  on launch l. The pick and the walk are also read on launch l. Then
  `regret = mean over l of (ns_l(pick) − ns_l(b(−l)))`. The arm chosen and the
  arm scored never share a launch, so the minimum over noisy arms does not bias regret
  upward. The panel's fold ("best on launches 1-2, scored on launch 3") is the l = 3
  term of this mean; rotating over all l uses every launch. Cross-fit regret can be
  negative, and sums keep the sign;
- **regret** is in absolute ns per pass, and also normalised per call and per MiB
  (a DINGHY cell is ~16 ns and a LINER MiB is ~0.27 ms, gridread §5.2), and in
  walk-cost units (§3.0);
- **the cell's NULL threshold `[r1 B-9]`**: `NULL_c = max(AA_c, ν · ns_walk(c))`.
  AA_c is the cell's A/A floor from `walk`/`walk#b` (or the per-arm A/A for an arm
  with a `#b`). ν is the SLOT's own aggregate A/A ratio, `median over the slot's
  groups of |ns(walk) − ns(walk#c)| / ns(walk)`, recorded per slot. It replaces the
  fixed 3.09% (gridread's Zen 4 grid1 figure), so J4 on Zen 1 derives its own ν. A
  launch-sign check is kept;
- **the walk's ns**, for walk-cost units.

Per regime (DINGHY / TUG / LINER, §2.5), each figure is summed:

- the absolute regret;
- regret in walk-cost units (§3.0), both denominators of §2.7;
- the same for every fixed-form policy (always walk / V1 / A1 / A3);
- the quadrature noise N (§3.0).

On `lines` cells N is per call, so the knowledge record, and hence the pick, can
differ per line. The replay prices a per-line pick by the per-call ns of each form.
The counting twin reports the per-call span histogram, and the harness reports ns per
pass = Σ over lines. **The replay therefore needs per-form ns for the lines that fall
in each N band.** These come from separate groups whose subject is the slice's lines
bucketed by length; each bucket is one streamed subject.

**`[r1 I-8]` Bucket edges come from the sets under test, not the table's code.** The
edges are the union of every N-boundary in the ACTIVE set and in every CONTROL set
(§4.1) named in `prereg.tsv`. With rev 0.3's values (rev 0.4 adds none yet) that is {32, 64} from R1/R2 plus
{14, 32} from C1's swapped spans, so four buckets: `< 14`, `14-31`, `32-63`, `≥ 64`.
`[rt0.4]` Rev 0.4's R8 lists N in its `needs` and carries a threshold "L ≥ ~16-32 B",
which would fall strictly inside `14-31` if it is an N-boundary. Its number is not yet a
set value, so the buckets above stand; once R8's L is declared, the check below either
refuses or adds a bucket, and that is a finding for main, not a silent re-bucketing.
The evaluator checks before any timing that no N-boundary of any pre-registered set
falls strictly inside a bucket, and refuses otherwise. A later set whose boundary
falls inside a bucket cannot be priced on `lines` cells; its `lines` cells read
UNPRICEABLE and are counted (never silently priced at a bucket mean).

### 1.4 What replay cannot see: the dispatch

The prototype makes the gap concrete: an artifact built from the table carries every
reachable form behind run-time compares. regime_tables §1 says it emits "the union of
the picks over the rows reachable under the knowledge it can ever have", and N, M and
H rows become emitted compares (the kit's D161 add. 11 notice, item 1). Replay prices
the pick as if the artifact held only that form. It misses:

1. the compare per call (N, M) or per block (H, R4);
2. code size and its layout effects (two or more forms per site);
3. R4 altogether. R4 switches form INSIDE a call per block, so no per-pass median of a
   single-form arm prices it. The prototype declares it NOT REPLAYABLE.

These go to [REGIME-TWIN]. Its hand-built table arm (real emitted compares) is timed in
one grid slot against the fixed forms and against the per-row best on the same cells.
It yields a dispatch term per (row set, site kind, A) as a SET VALUE. The evaluator then
re-runs §3's bars with that term added to every pick whose cell can reach more than one
form. `[r1 I-2]` R4, and every H-keyed row, is UNSCORABLE by replay (§3.3): the twin
scores them, and until it does the bars state that they exclude dispatch.

## 2. Populations, the fit/judge split, and placement

### 2.1 FIT (thresholds come only from here)

- **grid1 F1 and F3** (Zen 4, 2026-10-13): 141 + 8 groups. These give the constants
  regime_tables rev 0.3 (and `[rt0.4]` rev 0.4, whose row R8 reads gridread's D2) reads.
- **zen4-grid2, the kit's next grid slot `[r1 M-1]` `[r1 M-4]`.** It carries, for this
  evaluator:
  1. a STREAMED re-time of the F1/F3 fit cells (the PICKABLE population, every arm
     the table can pick, both layers, plus `walk#b` and `walk#c`). These are the
     in-sample cells the G2 caps are derived from (§3.1). They are FIT cells, not judge
     cells, so reading them changes nothing held out;
  2. `[D166a1]` OPTIONAL: the F2 perf pass on the K arms of every such cell, so the
     ungated corroboration column exists on streamed data. In-sample CB labels do NOT
     need it: they come from the timing rule (§2.7);
  3. `[D166a1]` **OPTIONAL: the F2 streamed perf pass** (T7): F2's 3 cells (hex-run,
     bounded, dfa-hat) × 4 arms on a STREAMED subject per class (prose, docs, code), the
     measurement the panel asked for (F2 never perf-measured the streamed condition).
     Rev 2 made E5 wait for it; rev 2.1 does not, because no bar reads it;
  4. the FIT ANCHOR SUBSET (§2.9): 30 of those groups, chosen at E4b to cover every
     scorable row's fit evidence, whose per-form ratios become the set's anchor values.
  Estimated wall for the REQUIRED items: 149 groups × ~7 arms × 3.4 launches × 0.95 s ≈
  56 min. `[D166a1]` The OPTIONAL passes add perf ≈ 5 min and the F2 streamed pass
  < 1 min (36 rows × 0.6 s), ~6 min in all; with them ~62 min. E5 waits for grid2's
  timing logs (§7), not for the perf output.
- **Later grids**:
  - F4 and F7, through D165's real iterator (R3, R4, A3);
  - F5, Zen 1, through a bench window (every W=64 row moves);
  - the missing axes regime_tables §5 lists: near-hit depth, bytes against landings,
    multi-position filters, and real text's predictability mix *as a synthetic axis*.
- **Fit subject condition.** Every set row carries the subject condition its constant
  was fit on (`repeated64k`, `streamed`, `whole1m`). grid1 F1/F3 are mostly
  `repeated64k`, which flatters the walk's predictor on some cells (F2, §2.4), so their
  constants are labelled `fit-repeated`. F4/F5/F7 run STREAMED. A streamed re-FIT of
  the F1/F3 constants stays FILED with its D77 trigger: P-PRED (§3.2) showing that the
  repeated-to-streamed change moves any row's pick on the judge cells. (grid2's
  streamed re-TIME above is not a re-fit: no constant is read from it, only the caps'
  in-sample reference.)
- **Output.** A fit produces ONE measurement set (D166): one box, one run, one method
  version. Its id names the grid run (for example `zen4-grid1-v1`). The kit owns its
  values and method; a fit that changes a row's constant is a ruled row diff
  (regime_tables §6 item 3).
- **WITNESS cells** (§4.4). Synthetic cells built so that every SCORABLE row has
  cells that reach it: R0 needs a ≥2-RANGE-term site; R1 needs a one-shot call with
  n < 32. They are not FIT data; nothing is fitted on them. `[r1 I-2]` Each scorable
  row has at least m_min = 5 witness cells, so its C3 control is powered (§4.2).

### 2.2 JUDGE, held out

| id | population | status | gates? |
|---|---|---|---|
| J1-open | [REGIME-CORPUS] subjects × the blinded user patterns, the ~70% NOT sealed | `[r2.2]` COLLECTED on main: rwcorpus (88 manifest rows, 7 classes) + rwquest (177 questions); ~54 RT expected, ~37 of them open (§2.3a) | YES |
| J1-sealed `[r1 M-6]` | the other ~30% of J1's patterns, chosen at pre-registration (§2.8), timed in the same slots, logs sealed unread | `[r2.2]` ~17 RT patterns expected | YES, ONCE, at the final reading (§2.8; `[r2.2]` a regime below G0 there reads on the pooled population, RULED, Q-REVAL-16, EP46) |
| J1b `[r1 I-6]` | a SECOND blinded pattern list the user agent writes NOW; its hash is committed unopened | `[r2.2]` NOT written: rwquest delivered one list. OWED by main's lane before E5 | only after a FAIL, as the fresh population for the next pre-registration |
| J2a | the bench's published patterns, timed by the grid1 harness at the kit tier on subjects made under §2.10's boundary rule | `[r2.2]` default path: the bench's ≥ 1 MiB subjects by byte transfer (§2.10) | YES, except the contaminated subset |
| J2a-contam `[r1 I-6]` `[r1 B-10]` | J2a cells whose pattern or subject is in ALPHA (slot25c), the spike, or any costmodel input (§2.8) | counted (K35) | NO: reported, labelled contaminated |
| J2b | the bench's own run of a table build on targeted hardware (D144 add. 4), via main | after the build | the OFFICIAL verdict; not a replay |
| J3 | ALPHA (slot25c) and spike cells | seen by costmodel (its regimes, 3.42 ns/use) | NO: reported as "semi-held-out" |
| J4 | Zen 1: J1-open + J2a subset re-timed on ubuntubudu via a bench slot request through main | after F5 | YES for the Zen 1 set; also the wrong-box control (§4.1 C6) |

- **Isolation.** No judge cell's timing is read before the pre-registration (§3.4).
  Judge results never feed a threshold. When a judge reading moves a row, the new
  constant is FIT on a new grid, and the old judge population becomes FIT-contaminated
  for that row. It is listed as such in the next run's manifest.
- **Iteration `[r1 M-6]` `[r1 I-6]`.** Re-registering against the same J1 after a FAIL
  tunes on the judge. After a FAIL the next pre-registration judges on J1b (opened
  then) plus J2a; J1 is listed as contaminated for every row its reading moved.
  J1-sealed stays sealed until the final reading of whichever table version is
  submitted for PASS.
- **The bench rule.** Bench-only questions go to main for relay (memory: ask the
  bench dev). The evaluator never reads the bench's ledgers. It uses only published
  pattern and subject definitions, through §2.10, and the bench's own reports for J2b.

### 2.3 J1: from blinded questions to cells

- **The user agent.** It is D27-blinded: no `src/`, no `tests/`, no bench patterns,
  no regime documents. It writes questions in natural language and the PCRE pattern
  for each, per corpus class. Main owns that lane and commits the pattern list with
  its sha256, and `[r1 I-6]` the J1b list's sha256 in the same commit, with J1b's
  file kept out of the evaluator's reach until opened (it lives in main's scratch, or
  is committed encrypted; main's call).
- **Freezing.** The evaluator freezes the list by hash at pre-registration (§3.4). A
  pattern added later belongs to the next run.
- **Site mapping, no clock.** Each pattern is compiled with the kit branch at both
  layers (`-fno-memfn-simd` and `-fmemfn-simd`) with the N2 census tooling
  (`tests/memfn/n2_census.py`'s pool, which records row selections per site through
  the MF_TRACE build).
- **`[r1 I-5]` Classification is PER TIMED GROUP, not per pattern.** A pattern can
  reach the table on one subject and not another (the required-byte pre-check answers
  first on one file, grid1 §5). Each (pattern, subject, mode, call) group lands in
  exactly one class:

| class | meaning | in the replay? |
|---|---|---|
| REFUSE | pcrec refuses the pattern (a module not built, a limit) | no; counted with its diagnostic |
| NOSITE | compiles, no kit FIND site on any search path (anchored whole-match, pure DFA with no set prefilter, ...) | no; counted |
| OTHER | a kit site whose form family the regime table does not cover yet (`pf_memchr`, the `vrun` pre-check, MLINE, ADVANCE) | no; counted per family. D161 add. 11 grows the table over (stop, form), and these become in scope then |
| UNREACHED | a regime-table site that never runs on this group's subject (counter leg U zero) | no; counted per subject |
| GATE-EXCLUDED `[r1 I-5]` | a regime-table site that runs, but the group is not gateable: an arm failed the correctness gate, a subject failed the streamed condition (`REPEATED-ONLY`), the group was discarded by the load rule (§2.4), or its `lines` buckets are UNPRICEABLE (§1.3) | no; counted with a reason and, for answer failures, PER ARM. A pickable arm's answer failure is a hard FAIL (§1.2) |
| RT | a regime-table site that runs, gateable | YES |

- **Completeness (K35).** For every frozen pattern the class counts over its groups sum
  to its group count, and over all patterns to the frozen group total. The evaluator
  fails closed if they do not. Every non-RT group is LISTED with its class and reason,
  never dropped silently. A pattern's own class (for P-RT) is RT if any of its groups
  is RT.
- **The RT share leads the summary**, per pattern and per group. If the blinded
  population mostly misses the table, that is the first finding, before any regret.
  `[r1 I-5]` It is also the gates' WEIGHT (§3.1, G0).
- **Subjects per pattern.** ~~Each RT pattern is timed on two timed files of its OWN
  class and on one file of a FOREIGN class (fixed by a rotation declared at
  pre-registration). A third file of its own class is the E exemplar (§1.1) and is
  never timed.~~ `[r2.2]` Each real question names the file it was written for, and a
  class is not one population: the structured class holds a fixed-width TSV, a quoted
  CSV, two kinds of GeoJSON and an XML dump, and the non-English class holds six
  scripts. So each RT pattern is timed on its own question's file, extended to a
  same-family POOL when that file is too small (§2.4). The E exemplar is the pool's
  reserved byte range, never timed (§2.8). The foreign-class subject stays the optional,
  ungated J-c.
- **`[r2.2]` Question mode → call shape.** `find-all` and `count` → `all` (a count is a
  find-all whose matches are not reported); `first` → `first`; `line` (grep) → `lines`.
  The question's own mode is recorded on every cell (`qmode`). The plan (§2.4) times
  shapes beyond the own mode where they buy power, and says which.

### 2.3a The real J1 population: an ESTIMATE without a compile `[r2.2]` (new)

The 177 questions (rwquest, main) are placed into §2.3's classes as far as can be done
without pcrec. `regime_eval/rev22_population.py` takes each pattern (or rwquest's python
equivalent, for `\p{..}`/`\x{..}`) through python's own sre parse. It erases the
zero-width items, takes the first-byte set S (UTF-8 lead bytes for code points; case
variants under `i`), and applies this first-match table:

| # | condition | expected class |
|---|---|---|
| 1 | anchored at the subject start (`^`/`\A` without `(?m)`), or a `line`-mode question that starts `^` | NOSITE |
| 2 | starts with `(?m)^` | OTHER (MLINE) |
| 3 | S nullable, or \|S\| ≥ 250 | NOSITE (no narrowing first byte) |
| 4 | \|S\| = 1 | OTHER (`pf_memchr`: one first byte) |
| 5 | zero python hits AND the required run absent from the file | UNREACHED |
| 6 | otherwise (2 ≤ \|S\| ≤ 249) | RT |
| after | an RT question on a MISLABELLED file, or on a pool below the 16-window floor (§2.4) | GATE-EXCLUDED |

**Every class here is an ESTIMATE, labelled `est`.** REFUSE, NOSITE, OTHER, UNREACHED and RT
are pcrec's answers, and E6's site-mapping census (no clock) replaces this table. What the
estimate cannot see is named so that E6 can be checked against it:

- which prefilter row pcrec picks. An offset-k pick or a required-run pre-check can move a
  literal-led pattern's stop, but its site family stays OTHER;
- per-window UNREACHED, where a window lacks the required run;
- whether a broad set such as `\w` (|S| = 63) is admitted by the start-set rows (counted RT
  here);
- REFUSE. The five `ucp` questions (N06, N11, N12, N13, N25) are at risk until [UCP]'s
  route is complete. Only N12 is estimated RT.

| class | n | REFUSE | NOSITE | OTHER | UNREACHED | GATE-EXCL. | RT (est) |
|---|---|---|---|---|---|---|---|
| logs | 28 | 0 | 1 | 16 | 1 | 0 | 10 |
| code | 27 | 0 | 0 | 19 | 0 | 0 | 8 |
| prose | 27 | 0 | 0 | 11 | 0 | 0 | 16 |
| structured | 24 | 0 | 0 | 22 | 0 | 0 | 2 |
| markup | 24 | 0 | 0 | 21 | 0 | 0 | 3 |
| nonenglish | 25 | 0 | 0 | 10 | 1 | 4 (`short-pool`) | 10 |
| binary | 22 | 0 | 0 | 17 | 0 | 0 | 5 |
| **all** | **177** | **0** | **1** | **116** (92 `pf_memchr`, 24 MLINE) | **2** (L25, N11) | **4** (N08, N09, N10, N22) | **54** |

**The first finding (§2.3), before any regret.** About a third of what users asked reaches
the table (54 of 177, 30.5%; the RT share is the gates' WEIGHT, §3.1 G0). The remainder is
OTHER: 92 questions are led by one literal byte (`\bERROR\b`, `"GET `, `<sponsor`,
`\x89PNG`), and 24 by `(?m)^`. In structured data and markup almost nothing reaches it (2
and 3 of 24). So:

- P-RT (≥ 40%) is expected to read REFUTED;
- G0's weight floor (w_min = 0.25) is expected to clear, but only by 0.06;
- the widening D161 addendum 11 describes (the table over (stop, form), `pf_memchr` and
  MLINE as families) is where this population's search time lives.

The kit reports this to main as the first line of E8's summary. It is not a reason to delay
the judge: the gates judge the table on what it covers, and the weight says how much that is.

**Regime placement is bracketed, not counted.** The counting twin's L = ADV/A is not
available without a compile. g_est = 1 / rate(S) over the file's windows (§2.4's rule,
stand-in salt). Two readings bracket the counted placement:

- LOWER: one activation per landing, L = g. TUG cannot occur under this reading.
- UPPER: one activation per match, L = bytes per python match.

`lines` cells are capped by the line length (L ≤ N), so buckets below 64 B are DINGHY by
construction.

| RT patterns, own shape | n | DINGHY lo / up | TUG lo / up | LINER lo / up |
|---|---|---|---|---|
| logs | 10 | 8 / 0 | 0 / 7 | 2 / 3 |
| code | 8 | 6 / 0 | 0 / 5 | 2 / 3 |
| prose | 16 | 13 / 0 | 0 / 7 | 3 / 9 |
| structured | 2 | 2 / 0 | 0 / 2 | 0 / 0 |
| markup | 3 | 2 / 0 | 0 / 1 | 1 / 2 |
| nonenglish | 10 | 9 / 4 | 0 / 5 | 1 / 1 |
| binary | 5 | 4 / 1 | 0 / 2 | 1 / 2 |
| **all** | **54** | **44 / 5** | **0 / 29** | **10 / 20** |

Gated cells per class × regime (one layer × filter, J1 open + sealed; the plans are in
§2.4; `rev22_arith_out.txt` §1b):

| class | LEAN cells | DINGHY lo / up | TUG lo / up | LINER lo / up | FULL cells | DINGHY lo / up | TUG lo / up | LINER lo / up |
|---|---|---|---|---|---|---|---|---|
| logs | 36 | 30 / 6 | 0 / 21 | 6 / 9 | 56 | 46 / 6 | 0 / 35 | 10 / 15 |
| code | 48 | 42 / 24 | 0 / 15 | 6 / 9 | 64 | 54 / 24 | 0 / 25 | 10 / 15 |
| prose | 81 | 72 / 33 | 0 / 21 | 9 / 27 | 101 | 88 / 33 | 0 / 29 | 13 / 39 |
| structured | 6 | 6 / 0 | 0 / 6 | 0 / 0 | 10 | 10 / 0 | 0 / 10 | 0 / 0 |
| markup | 18 | 15 / 9 | 0 / 3 | 3 / 6 | 24 | 19 / 9 | 0 / 5 | 5 / 10 |
| nonenglish | 42 | 39 / 24 | 0 / 15 | 3 / 3 | 52 | 48 / 28 | 0 / 20 | 4 / 4 |
| binary | 24 | 21 / 12 | 0 / 6 | 3 / 6 | 33 | 28 / 14 | 0 / 9 | 5 / 10 |
| **all** | **255** | **225 / 108** | **0 / 87** | **30 / 60** | **340** | **293 / 114** | **0 / 133** | **47 / 93** |

What this says for power before any plan is chosen:

- DINGHY is plentiful under both readings;
- TUG exists only if one activation spans several landings, so the counted placement
  decides whether G0's TUG reads UNREACHED;
- LINER is thin: 10 to 20 patterns;
- structured and markup cannot support per-class figures (printed, UNREACHED).

Also counted: the own mode of the 54 RT patterns is `all` for 51 and `lines` for 3, never
`first`. 28 of the 54 are on CRLF subjects. The stand-in salt seals 17 of them (§2.8).

### 2.3b Subject facts and labels `[r2.2]` (new; the corpus author's caveats a, c, d)

**(a) Line endings, recorded per subject.** `rev22_population_out.txt` part 1 has one
class per derived manifest row:

| corpus class | crlf | lf | one-line | binary |
|---|---|---|---|---|
| prose | 12 | — | — | — |
| nonenglish | 29 | — | — | — |
| logs | 2 (`hadoop.log`, `zookeeper.log`) | 5 | — | — |
| code | — | 6 | — | — |
| markup | — | 3 | — | — |
| structured | — | 4 | 1 (Natural Earth GeoJSON, 13 MB) | — |
| binary | — | — | — | 5 |

Two of the CRLF files are logs, which the corpus report did not say. PCRE2's default
newline is LF, so on a CRLF subject:

- `$` and `(?m)$` match only before the LF, i.e. after the CR;
- `.` and `\s` consume the CR;
- `^$` finds almost no blank lines (P21 finds 1 where `^\s*$` finds 3,388).

The answers come from the oracle (libpcre2 10.46 at its default newline), so the semantics
are exact by construction, and nothing about them is re-decided here. What the labels add is
VISIBILITY:

- `cells.tsv` carries `eol` (`crlf`, `lf`, `one-line`, `binary`) and `eol_sensitive`. A cell
  is eol-sensitive when the subject is CRLF and the pattern has `$`, a leading `^` under
  `(?m)`, or `(?m)`. That is 8 questions, 2 of them RT (P19, P27);
- `summary.txt` prints every gate figure split by `eol` as well, reported and not gating,
  so a CRLF effect cannot hide inside a pooled sum;
- `lines` subjects split at LF, and the CR stays in the line. So N counts the CR: a
  31-character CRLF line is a call with N = 32 and falls in the 32-63 bucket. The bucket
  is the call's real N; nothing strips the CR.

**(c) Mislabelled files: reported apart, never gate.** pg8186 and pg8453 are French with
the accents stripped (99.98% ASCII). pg20175 is Greek stored as Latin-1-looking mojibake.

- Every cell on these files is labelled `mislabelled` and printed in its own summary
  column. It is never in a gate population, never in a subject POOL and never an
  exemplar (§2.4).
- The K35 completeness count lists them. The questions on them are N11 (pg8186, UNREACHED
  est) and N20 (pg20175, OTHER est), so neither would have gated anyway.
- "Fix or drop" is main's plan-row item. A re-fetched, correctly accented file is a new
  manifest version, and so belongs to the next pre-registration, never to this one.

**(d) Subject shapes that distort landing statistics.** Each gets a `shape` label. Every
cell also carries its landing-gap quantiles (`gap_p10`, `gap_p50`, `gap_p90`, from the
counting twin's per-call span histogram), because a mean g misleads on all three shapes.
Labelled cells print as their own rows in the per-class summary. Nothing gates on a label.

- `periodic-200`, the census gazetteer. Every row is space-padded to 200 bytes, and
  58.5% of the file is spaces. A lead set containing a space lands in each row's padding
  run, at a 200-byte period. Periodic landings can be learnt by the walk's predictor even
  on streamed buffers, so P-PRED there is not representative of text. The water-area
  columns read `0.`, which is a question-writing trap rather than an engine fact.
- `nul-padded`, the uncompressed tars. NUL is 13.4% of `django-5.0.tar` and 6.1% of
  `libpng-1.6.43.tar`, in 512-byte block padding.
  - A lead set without NUL crosses long landing-free runs, which are perfectly
    predictable for the walk.
  - A lead set with NUL (B04, B12) lands densely inside them.
  - Either way the gaps are bimodal.
  - Members do not start a line, so `(?m)^` reaches member bodies only (B14 finds
    nothing).
- `compressed`: `.tar.gz`, `.tar.bz2` and `.zip`, with ~42% invalid UTF-8 and near-uniform
  bytes. Landings are geometric and maximally unpredictable, the opposite extreme from
  `nul-padded`.

### 2.4 Timing the held-out cells: STREAMED condition, shape, count, slot wall

**The streamed condition (pre-registered; §3.4 puts it in `prereg.tsv`).** Why, with
`[r1 B-7]` F2's numbers as `gridread/f2_counts.txt` gives them: the walk's branch
misses on fresh 1 MiB text (F2, an optional diagnostic that was available on that box)
are 145-251 per KiB in every cell (hex-run 201-250,
bounded 145-251, dfa-hat 156-194). On a REPEATED 64 KiB buffer they are 0.4-0.9
(dfa-hat), 22 / 150 / 4.7 (hex-run prose / docs / code) and 95-168 (bounded). So a
repeated judge lets the walk's predictor learn the subject, and flatters the walk, on
dfa-hat and on hex-run prose and code. It does NOT on hex-run docs or on bounded, whose
repeated walk already misses at fresh-text rates. The streamed rationale therefore holds
where the table picks forms against a trained walk, and P-PRED (§3.2) is expected to
read ≈ 1 on bounded. Rev 0 timed most judge cells repeated; rev 1 and rev 2 do not.
Every JUDGE cell, including the J2a and WITNESS cells and the `lines` buckets, runs on
one of:

- **(S) a streamed subject**: a directory of 64 DISTINCT 64 KiB buffers (4 MiB in all)
  cut from the pattern's class corpus at distinct offsets (`[r2.2]` from the question's
  POOL by the drawing rule below; 16 to 64 buffers), disjoint from the E exemplar
  and from every FIT buffer (§2.8), every buffer's sha256 in the manifest. grid1's
  cursor never resets, so consecutive passes see distinct data (`grid1/README.md` item
  5; check leg C rejects a driver that does not cycle). `ns/pass` is per buffer, and
  the regret sums are per MiB;
- **(W) a whole subject of at least 1 MiB** (the size F2 counted), `[r1 I-6]` whose
  byte range does not overlap the exemplar's or any FIT buffer's (§2.8).

`[r1 M-also]` Neither condition is DRAM-bound: (S)'s 4 MiB working set and (W)'s
1 MiB fit the 7700X's 32 MiB L3 (and a Zen 1 CCX's 8 MiB L3 for J4). The judge measures
cache-resident text, as the fit did; a DRAM-streaming regime is out of scope and would
be its own condition.

A cell timed ONLY on a repeated subject is `REPEATED-ONLY` (GATE-EXCLUDED, §2.3) and
never enters a gate. Total size is at least 4× the largest fresh size F2 measured. The
size is pre-registered and is not fitted. ~~The class corpus must supply 4 MiB outside
the exemplar and the FIT buffers; a class that cannot is served by (W) alone and listed.~~
`[r2.2]` Replaced by the drawing rule below.

**`[r2.2]` The buffer-drawing rule (caveat b: across WHOLE files, never from heads).**
Head samples mislead on this corpus. `^TX\t` (S02) finds 0 in the gazetteer's first 4 MiB
and 1,863 in the whole file, because the file is sorted by state; `ERROR` (L01) finds 6
against 539. Seven questions find nothing in the head and something in the file. So every
streamed subject is drawn by a deterministic, stratified rule whose only free input is
`prereg_salt` (§2.8). Everything below is pre-registered, and `h(...)` is
sha256(`prereg_salt` ‖ ...) read as an integer.

Every size, count and floor in this rule (the 64 KiB window, the 64-window ceiling, the 16-window floor, the 1/8 reserve, the 64 KiB reserve minimum, the 1 MiB (W) minimum, the 64 KiB bucket minimum) is a row of §3.0a (EP48-EP54); where the text below gives a number, the table wins `[r2.3]`.

1. **The pool.** It is the question's own file, followed by the other files of the SAME
   FAMILY in manifest order:
   - prose: all twelve English books;
   - non-English: the same script (CJK 6 files, Kana 5, Cyrillic 7, Greek 3, Hebrew 2,
     Latin-extended 2, transliteration 1);
   - code: the same language, which is one file per language here;
   - logs: the same source;
   - markup: the same format;
   - structured and binary: the file alone.

   Pools never cross a family, because a question written for C code has no meaning on
   Java. A MISLABELLED file is never in a pool.
2. **One exemplar reserve per pool.** R = max(64 KiB, ⌊pool bytes / 8⌋) contiguous bytes,
   aligned to line starts, taken from the pool file chosen by h(pool, `E`) among the files
   at least R long, at offset h(pool, `E`, file) mod (F − R + 1). The reserve is the
   pool's E exemplar (§1.1, §2.8). It is never timed and never inside a window.
3. **Windows.** The pool minus its reserve is one USABLE stream (files concatenated in
   pool order), U bytes long. M = min(64, ⌊U / 64 KiB⌋) windows, one per equal stratum
   [jU/M, (j+1)U/M). Window j starts at the stratum start plus h(pool, `W`, j) mod
   (U/M − 64 KiB + 1).
   - A window that crosses a file boundary or the reserve continues after it, so it never
     reads reserved bytes.
   - In a text class, a window is then trimmed to whole lines: it starts after its first
     LF and ends at its last LF. Binary-class windows, and windows that hold no LF (the
     13 MB one-line GeoJSON), are not trimmed.
   - Every window's (file, offset, length) and sha256 go into the manifest.
   - The strata cover the whole stream, so a sorted or concatenated file is sampled
     everywhere.
4. **The floor: 16 windows (1 MiB, F2's fresh size).** A pool with M < 16 cannot stream:
   its RT cells are GATE-EXCLUDED, reason `short-pool`, and counted. The estimate finds 4
   such questions: N08 and N22 on the Greek pool (0.6 MB) and N09 and N10 on the Hebrew
   pool (0.4 MB). Every other RT question's pool reaches 16. The `go.src` and
   `jquery_md.md` pools are also short, but none of their questions is RT. The prose
   pool, and the logs, code and structured files above 4 MiB, reach 64.
5. **(W)** is one contiguous slice of at least 1 MiB of the question's own file, outside
   the reserve, at a salt offset, line-aligned. It exists for 31 of the 54 RT questions
   (est); the prose books under ~1.2 MB and every non-English file have none.
6. **`rep64k`** repeats window 0 of the same pool.
7. **`lines`** subjects are the lines of the (S) windows, bucketed by N (§1.3; LF split, CR
   kept, §2.3b). A bucket that holds less than one 64 KiB buffer of such lines in the
   pattern's subject has no group. Its lines are excluded from the `lines` cell and their
   share is printed. Logs and structured files have almost no lines under 64 B, so their
   `lines` cells are usually one bucket.

`rev22_population.py` implements rules 2 to 5 with a stand-in salt to size the population.
Its histogram estimate uses a per-file reserve, a simplification that is labelled in the
script. The kit's E4 generator implements the rule exactly, and the E6 disjointness proof
checks its output (§2.8).

**Cell shapes per RT pattern (own class), all gated:** `first`/S, `all`/S, `all`/W
(1 MiB), `all`/lines (S, four buckets, §1.3), `iter`/S. That is `[r1 M-7]` 8 groups per
RT pattern (rev 1 counted `lines` as one group). The foreign-class group and the second
own-class file are the optional J-c (below). `[r2.2]` That is the ALTERNATIVE plan's
shape set. The plan (the lean one, Q-REVAL-12) times `first`/S, `all`/S and `lines`/S in every
bucket that exists for the pattern (one to four; 147 bucket groups over the 54 RT
patterns, est). It drops `all`/W and `iter`/S for J1 (below).

**The repeated column (UNGATED, labelled `rep64k`).** One extra group per RT pattern:
`all` on a single REPEATED 64 KiB own-class buffer, all arms. It measures the
PREDICTOR-TRAINING EFFECT (P-PRED, §3.2) and gives the like-for-like column against the
`fit-repeated` figures of §8, and `[r1 M-1]` the rep64k cap check of §3.1. It never
feeds a bar, a control, or a pick. `[r2.2]` In the lean plan it covers a 2-per-class
subsample of 14 patterns, drawn by h(`rep`, id) among each class's RT patterns.

**Harness extension H1 (kit, small):** a `lines` subject = a manifest of line buffers,
one pass = one call per line through the existing streamed-cursor code (README item 5).
The extension is a manifest generator that splits the slice into per-bucket line
buffers. The driver is unchanged. Check leg C already proves the cursor cycles.

**`[r2.2]` `[r2.3]` THE PLAN: the LEAN plan (RULED by Frank, 2026-10-14, Q-REVAL-12).** Frank asked for "looser and leaner". The target is
two quiet-box windows (about 2 × 85 min of judge timing), with grid2's required ~56 min
separately. The arithmetic is `regime_eval/rev22_arith.py`, output `rev22_arith_out.txt`,
on §2.3a's ESTIMATED population. The inputs are rev 2.1's: SEC 0.95 s (0.65 repeated),
L = EP27 (WITNESS EP28), f_rerun EP69 and EP70 per group (the plan inputs are the plan-arithmetic constants EP67-EP72, which are not part of the evaluator-params kind (§3.0a), and only the wall arithmetic reads them). Every group times FIVE arms:
`walk`, `walk#b`, `walk#c`, V1, A1.

| unit | groups | arms | min |
|---|---|---|---|
| J1 `all`/S | 54 | 5 | 18.1 |
| J1 `first`/S | 54 | 5 | 18.1 |
| J1 `lines`/S, the buckets that exist per pattern (§2.4 rule 7) | 147 | 5 | 49.4 |
| J2a, (W) on the transferred bench subjects (§2.10) | 20 | 5 | 6.7 |
| WITNESS (7 scorable rows × 5, L = 5) | 35 | 5 | 16.2 |
| `rep64k` (ungated, 2 per class) | 14 | 5 | 3.2 |
| anchors: the full replay (10) and end drift (3) in window 1; drift anchors at the start and end of window 2 (3 + 3) | — | — | 19.0 |
| **total** | **324** | | **130.8** |

| window | contents, in order | min |
|---|---|---|
| W1 | full FIT anchor replay; check + counting (no clock); J1 `all`/S; J1 `first`/S; WITNESS; `rep64k`; end drift | 68.7 |
| W2 | drift anchors (walk + best on 10 anchors); check + counting; J1 `lines`/S; J2a; end drift | 62.1 |
| **total** | plus zen4-grid2, required ~56 min, separately (§2.1) | **130.8** |

That leaves about 39 min of the two-window envelope unused, and it is held on purpose: it
is the BREACH-resume margin. Under the load rule below, a resumed slot re-runs its anchors.
The headroom lets one discarded group run, or window 2's fallback to a full replay
(cut 6), finish without a third window. Three add-backs fit inside it. None is in the lean
plan, and each states what it buys:

- the S1 arm, +18.0 min: the declared `LV_X86_W16` layer is judged;
- J1 `all`/W, +10.4 min: the W-vs-S agreement, and 4 more open LINER cells (L13, L19,
  C21, B20);
- J1 `iter`/S, +23.9 min: reported S2/S3 figures only.

**The cut ladder, each cut priced in power.** Cumulative from rev 2.1's plan on the REAL
population. "Cells" are gated cells per layer × filter on J1-open; "lo/up" are §2.3a's
two readings.

| step | wall | Δ | what it costs in power |
|---|---|---|---|
| ALTERNATIVE: rev 2.1's shapes, real population (5 slots) | 308.7 | — | the reference: 231 cells; every gate powered except TUG (lo: UNREACHED) and G2-LINER at central noise (below) |
| cut 1: J1 `iter`/S out | 281.9 | −26.9 | −37 cells (one per open pattern, the `all`/S regime split). The always-A3 policy (iter only) leaves G1: UNREACHED. No control lost: C2 and C3 for R3a/R3b/R4 are already twin-owned. The reported S2/S3 figures are gone (they never gated, Q-REVAL-7) |
| cut 2: J1 `all`/W out | 266.5 | −15.4 | −21 cells, 4 of them LINER (lo). No status changes, but G0-LINER (lo) ends at 21, one cell over the floor. Lost: the W-vs-S agreement and the 1 MiB like-for-like against F2's fresh-text figures, both diagnostic. W stays for J2a |
| cut 3: arms 8/6 → 5 (drop S1 = `LV_X86_W16`, and V3/A3) | 219.5 | −47.0 | no cells lost at I = `LV_X86_W32` (A1, Zen 4's default). For a declared W16 arm, every gate reads UNREACHED (not run), and the S-forms' own thresholds go unjudged at the kit tier on Zen 4. V3/A3 only served `iter` (cut 1). C1 swaps the SIMD-on and SIMD-off g* (A1 against V1), so it is unaffected |
| cut 4: J2a 40 × 3 → 20 × 1 | 185.9 | −33.6 | J2a cells 120 → 20. Their regime is unknown before E6, so the power table counts J1-open alone and no status changes. J2a-only summaries read UNDERPOWERED in every regime. J2a-contam counting is unchanged |
| cut 5: `rep64k` 54 → 14 (2 per class) | 176.8 | −9.2 | ungated only: P-PRED, P-BND and the rep64k cap check rest on 14 patterns, which per class is a pair, not a distribution |
| cut 6: two windows; full anchor replay in W1, drift anchors in W2 | **130.8** | −46.0 | no gate moves. SET-MISMATCH is read in W1. W2 inherits it if its 10 drift anchors (walk + best) stay within EP37·AA of W1's ratios on at least EP39 of EP36 (the drift rule's own rows); otherwise W2 runs the full replay (+10 min, inside the headroom). A W2 failure's attribution rests on those 10 anchors, not 30 |

Levers NOT taken, with what they would cost:

- **`lines` buckets 4 → 3**, dropping C1's 14 edge: −3.4 min only, because lines under
  14 B are 1-5% of text. It would cost:
  - the judge-population C1 at S0 near the 14 edge, which reads UNPRICEABLE (§1.3; C1
    stays scorable on WITNESS);
  - P-R1's < 14 / 14-31 split;
  - |D(always-A1)| at SIMD-on S0, which falls from 62 to 55.
- **`first`/S only where the question's own mode is `first`**: −18.1 min. No RT question
  has `first` as its own mode, so the shape would vanish. Its cost:
  - G0-LINER (lo) would fall from 21 to 14 cells and read UNREACHED in all four gate
    populations;
  - G3 would fall from 144 to 113 non-CB cells (still powered), and its per-call leg would
    lose every `first` cell;
  - |D(always-walk)| at SIMD-off S1 would fall from 35 to 28.
- **LAUNCHES 3 → 2**: about −33 min. Q-REVAL-8 ruled 3, and the cost is real:
  - cross-fit would score each launch against a best chosen on ONE other launch;
  - NULL would come from 2 launches, so per-cell noise grows by about √1.5;
  - every G2 floor's required n grows 1.5× (LINER at r = 1%: 26 → 40 cells).
- **Patterns per class capped**: not needed. The real RT population (54) is smaller than
  rev 2.1's assumed 70.
- **`lines` on a subset of classes**: the gates can least do without this unit. Without
  `lines` at all (an illustration in `rev22_arith_out.txt`):
  - |D(always-A1)| at SIMD-on S0 = 0, so G1 is vacuous;
  - G3 has 31 non-CB cells and reads UNDERPOWERED;
  - under the upper reading every regime is UNREACHED.

  R1 and R2 fire only on short N, which is to say on `lines` cells.

**The power table** (J1-open: 37 patterns est; per layer × shipped filter; J2a not counted).
"ok" means the gate is powered: it can read PASS or FAIL. Noise is r = per-group NULL /
walk as an RMS, at 1.0 / 1.5 / 3.09%; F1's A/A has median 0.20% and p90 3.37%. n_eff is
n/2, from the unequal walk weights. The caps take §8's PICKABLE fit-repeated figures as
R_in proxies until E4b reads grid2. The CB share is 1/6, from F2.

| gate | ALTERNATIVE, 308.7 min: lo / up | LEAN, 130.8 min: lo / up |
|---|---|---|
| gated cells per layer × filter | 231 | 173 |
| G0 DINGHY (cells / patterns) | 199/36 ok · 79/33 ok | 152/36 ok · 74/33 ok |
| G0 TUG | 0 UNREACHED · 88/19 ok | 0 UNREACHED · 57/19 ok |
| G0 LINER | 32/7 ok · 64/14 ok | 21/7 ok · 42/14 ok |
| G1, \|D(P)\| (floor 10): off S0 walk, V1 | 86, 145 ok | 62, 111 ok |
| G1: off S1 walk, V1 | 45, 186 ok | 35, 138 ok |
| G1: on S0 walk, V1, A1 | 202, 198, 62 ok | 144, 140, 62 ok |
| G1: on S1 walk, V1, A1 | 138, 198, 126 ok | 102, 140, 104 ok |
| G2 DINGHY | ok at every r | ok at every r |
| G2 TUG | UNREACHED · ok | UNREACHED · ok (on S1: UNDER at 3.09%) |
| G2 LINER, cap = R_in + 1 (superseded) | ok only at r = 1% · off ok to 1.5%, on ok at 1% | UNDER at every r · off ok at 1%, on UNDER |
| G2 LINER, cap = R_in + 2 (RULED) | — | ok at r ≤ 1.5% (needs 16-18 cells) · same; UNDER at 3.09% (needs 69-76) |
| G3 non-CB cells (floor 40) | 192 ok | 144 ok |
| G4 | scorable: C1, C3 for R0 R1 R2 R5 R6 R7 (on WITNESS; R8 once declared), C4, C5, C7, C8. UNSCORABLE (twin-owned): C2, C3 for R3a R3b R4. UNREACHED: C6 (needs J4, E11) | the same |
| J1-sealed alone at the final reading (17 patterns) | LINER 15/3 UNREACHED · all ok | LINER 9/3 UNREACHED · LINER 18/6 UNREACHED |

Reading it:

1. The lean plan has about 25% fewer cells. At central noise no gate changes status
   between the plans, except G2-LINER (lo) and the sealed LINER (up).
2. Two weaknesses are NOT the plan's. TUG under the lower reading is a population fact:
   it exists only if activations span several landings. G2-LINER at central noise is a
   noise fact: rev 2.1's plan does not buy it either.
3. **Justified loosening: cap(LINER) = R_in + 2 points (RULED, Q-REVAL-16).**
   - With +1, the power floor holds the noise allowance 2N/W under 0.5 point. That takes
     n_eff ≥ (4r / 1.1)², about 30 LINER cells at r = 1.5%. The real population has 7 to
     14 LINER patterns per layer × filter, so no affordable plan gives that many cells.
   - With +2, the floor is 16 to 18 cells, which both plans meet under both readings.
   - +2 still means something: LINER's R_in is 0.0-0.1%, so held-out LINER regret above
     2% of the walk would still say the default is wrong where it lives. The DINGHY and
     TUG caps are already at least +2.
   - RULED (Frank, 2026-10-14, Q-REVAL-16): +2 is EP13. A G2-LINER reading of UNDERPOWERED still makes the run INCONCLUSIVE, never FAIL (§3.0).
4. **The sealed holdout cannot reach G0 in LINER**, at 3 to 6 patterns, nor in TUG under
   the lower reading. This holds in either plan. RULED (Q-REVAL-16, EP46): at the final reading, a sealed regime below G0 is judged on the pooled population (J1-open ∪
   J1-sealed), labelled `pooled (sealed underpowered)`, with the sealed-only figure
   printed beside it. Without this, the final reading is INCONCLUSIVE in those regimes by
   construction.

**The ALTERNATIVE: rev 2.1's plan (documented only; not scheduled `[r2.3]`).** On the real population, `rev22_arith.py` re-costs it
at **~309 min** in five slots: 340 J1 groups (54 RT patterns; `all`/W for 31 of them),
J2a 120, WITNESS 35, `rep64k` 54, 5 × 13 min fixed. It would become the plan only on a NEW ruling by Frank (Q-REVAL-12 chose the lean plan). Its own arithmetic at the assumed 70 RT patterns is kept below for the
record.

**Estimate `[r1 M-7]` `[r1 M-9]`** (`[r2.2]` rev 2.1's, at the ASSUMED 70 RT patterns; the
formula, so that main can rescale; the arithmetic is `regime_eval/rev2_arith.py`, output
`rev2_arith_out.txt`):

```
inputs
  SEC        0.95 s per launch, streamed or >= 1 MiB; 0.65 s repeated 64 KiB (grid1 §3)
  L          3 launches per judge group; 5 per WITNESS group (Q-REVAL-8)
  f_rerun    0.20: budget share of judge groups that get +2 launches (M-9; an estimate,
             the realised share is reported)
  arms       8 on all/iter groups, 6 on first/lines (rev 1's 7 and 5, + walk#c);
             6 on WITNESS
  perf       OPTIONAL `[D166a1]`: 0.6 s per arm row, on K = {walk, V1, A1} only (F2: 72
             rows in 43 s). Counted only in the "with optional perf" column below
  check      4.0 s per group (check.sh + counting, no clock; rev 1's 3 x 12 min over its
             540 groups, scaled per group)
  per slot   13 min fixed: FIT anchor replay ~10 min (M-8) + end-of-slot drift
             re-time ~3 min (§2.9)

per unit:  groups x arms x (L + 2 f_rerun) x SEC  +  groups x 4.0 s
           [+ groups x 3 x 0.6 s, the OPTIONAL perf pass]

unit             groups  timed  check  REQUIRED  | perf   with optional perf
J1 first/S           70   22.6    4.7     27.3    |  2.1   29.4
J1 all/S             70   30.1    4.7     34.8    |  2.1   36.9
J1 all/W             70   30.1    4.7     34.8    |  2.1   36.9
J1 iter/S            70   30.1    4.7     34.8    |  2.1   36.9
J1 lines/S x 4      280   90.4   18.7    109.1    |  8.4   117.6   (4 buckets, I-8)
J2a                 120   51.7    8.0     59.7    |  3.6   63.3   (40 patterns x 3 groups)
rep64k column       70   18.2    4.7     22.9    |  2.1   25.0   (ungated; no reruns)
WITNESS              35   16.6    2.3     19.0    |  1.1   20.0   (7 scorable rows x 5; L = 5)
SUM                 785  290.0   52.3    342.3    | 23.6   365.9
+ 5 slots x 13 min fixed                   65.0                   65.0
total                                    ~407 min (6.8 h)       ~431 min (7.2 h)   [rev 1: ~226 min]
```

`[D166a1]` The required path is the left column: **~407 min**. The optional counter
passes add ~24 min (~431 min, rev 2's figure) on a box where counters work. Nothing
else changes between the columns; no bar reads the perf column.

The increase over rev 1 (rev 2's figures, with the perf column; +205 min, +91%): J1 and
J2a timed +99 (three more `lines` buckets +68; `walk#c` and the rerun budget +31),
WITNESS timed in its own right +17, the rep64k column +2, perf +6 and check +16 (more
groups; perf is cheaper per group because it runs on K only), and the per-slot anchor
and drift re-time +65. Without the optional perf the increase over rev 1 is +181 min. J1-sealed costs nothing extra: it is ~30%
of the same 70 patterns.

**The fit into slots `[r1 M-7]` `[D166a1]`** (`[r2.2]` the ALTERNATIVE's slots, at rev
2.1's assumed population; the lean plan's two windows are above). Five slots, each ≤ ~87
min on the required path (≤ ~92 min with the optional perf passes):

| slot | contents | required min | with optional perf |
|---|---|---|---|
| J-a1 | J1 `all`/S + `all`/W | 82.6 | 86.8 |
| J-a2 | J1 `iter`/S + `first`/S | 75.1 | 79.3 |
| J-a3 | J1 `lines` buckets 1-2 + WITNESS | 86.5 | 91.8 |
| J-a4 | J1 `lines` buckets 3-4 + half the rep64k column | 79.0 | 84.2 |
| J-b | J2a + the other half of the rep64k column | 84.1 | 88.8 |
| J-c | optional, ungated, unscheduled: foreign class + second own-class file (rev 1: ~140 min; more at rev 2's arms and buckets, not re-estimated) | — | — |
| total (J-a1 to J-b) | | 407.3 | 430.9 |

Each slot runs, in order: the FIT anchor replay (§2.9), `check.sh` and the counting
pass on its own groups (no clock), its timed groups, `[D166a1]` the OPTIONAL perf pass
on its own groups (run only where counters are available, else skipped loudly with the
§1.2 suggestion; the slot's verdict and every bar are identical either way), and the
end-of-slot drift re-time. One heavy run at a time, through main's slot channel.
If main must cut, the first lever is J1 `iter`/S (−37 min): its cells are emulated
(Q-REVAL-7), so its S2/S3 never gate, and under S0/S1 the M = iterator key only
disables R1/R2, which `all`/S already covers (Q-REVAL-12). `[r2.2]` The ladder above
takes that lever first and prices every later one. The lean plan's windows run in the
same order: anchors, check and counting, timed groups, optional perf, end drift.

**The load1-breach abort rule `[r1 M-7]` (pre-registered).** The harness samples load1
before and after every group. A group with load1 ≥ EP40 at either sample is discarded
(GATE-EXCLUDED, reason `load`) and re-queued once at the end of the slot. If EP41 consecutive groups are discarded, or load1 ≥ EP40 persists for EP42 min, the slot ABORTS:
the groups already timed with clean samples are kept, the slot is marked BREACH in its
log, and the remaining groups go to a resumed slot that first re-runs the anchor
replay. A group re-queued twice (EP43) is GATE-EXCLUDED for good and counted. (EP40-EP43 are rows of §3.0a; the wording above gives their names, not a second copy of the numbers.)

On Zen 1, the J4 subset is J-a1's cells only: about 2.2× the wall on ubuntubudu's slower
core, so ~3.2 h with its anchor replay. `[r2.2]` Under the lean plan, J4 is window 1's J1
groups (`all`/S + `first`/S, 108 groups): about 2.2 × 36 min plus the anchor replay, so
~1.6 h. J4 runs no perf pass (`[D166a1]` it need not; the box's
paranoia setting is irrelevant to it). `[r1 M-10]` `[D166a1]` Its consumer-bound labels
are computed from J4's OWN timing by the §2.7 rule (rev 2 could only inherit Zen 4's);
the Zen 4 label of the same cell id is printed beside it as `inherited`, report only.

### 2.5 Regime placement

A cell's regime comes from the COUNTED facts of its own counting twin, never from
timings or the table:

- L = bytes advanced per activation (ADV/A);
- g = bytes per use (ADV/U).

Placement uses costmodel's rule: DINGHY if L < 64, else TUG if g < 18.5, else LINER.
This is the rule regime_tables §3's regret table is reported in, so judge figures
compare to the fit's one for one.

The rule is pre-registered as a REPORTING bucket only, and it never decides a pick.
`[r2.2]` Before E6 there is no counting twin. §2.3a's placement of the real population is
therefore an ESTIMATE, bracketed by two readings (L = g, and L = bytes per match). The
gated placement is this counted rule, unchanged.
A second column re-buckets with gridread's W=64 boundaries (L ≥ 8-32, g ≥ 4) for
reference and is not gated.

Real text adds one axis the grid controlled: landing PREDICTABILITY (gridread §5.3:
+4-7 ns per unpredictable landing on the walk). The counting twin cannot see it; F2's
branch-miss count can. The per-cell file carries a `pred` column: the walk's ns per use
on the cell, divided by its grid value at the same g. It is a derived observation,
reported only.

### 2.6 The prototype's population lesson

Requiring every arm timed (gridread §6.2's 101 groups) silently drops grid1's L = 8
groups, because those time only walk/V1/A1/A3. The kit's R3 correction (A3 loses at
L ≈ 8) rests on exactly those groups.

The evaluator's population rule is therefore: **every form the table can PICK in that
layer is timed; the best is the minimum over the arms that were.** Cells missing a
non-pickable arm are kept and flagged `partial`. A population rule is part of the
pre-registration, never chosen after the reading.

`[r1 I-5]` **Partial cells are counted and capped.** A partial cell's best may be too
slow (the missing arm might have won), so its regret is biased LOW. Partial cells are
therefore kept OUT of the G2 and G3 numerators and, so they do not dilute the
percentages either, out of the G2 denominator and the G3 cell count. They stay in G1
(the comparison against a fixed policy is fair on the arms timed). Their count per
layer × regime × filter is printed. If partial cells exceed EP20 of the RT cells of a gate population, that gate reads UNREACHED for that population (the population is
not what was pre-registered).

The rule has a second clause, **the subject condition**: a cell enters a gate only if
its judge timing is STREAMED or ≥ 1 MiB (§2.4). A `rep64k` cell is reported in its own
labelled column and never gates.

### 2.7 The consumer-bound class: a COUNTED class, out of the denominator only

F2 showed that on bounded prose every form misses about the same as the walk, 145-160
per KiB at 1 MiB. Those misses belong to the CONSUMER (the `[a-z]+\b` run verify), not
to the scan. Such a cell inflates the "% of walk" denominators without the table being
able to turn it.

**Definition `[D166a1]` (timing only, pre-registered).** A (cell, layer, filter) is
CONSUMER-BOUND (`cb = 1`) iff all three hold, each read from the group's TIMED rows
(cross-fit, §1.3), with no counter of any kind:

1. **Nothing to gain:** ns(walk) − ns(best) ≤ NULL_c (§1.3). A form that wins is not
   consumer-bound.
2. **All forms tie `[r1 M-4]` `[D166a1]`:** over the FIXED arm set K = {walk, V1, A1},
   the ns spread `max(ns) − min(ns) ≤ k · NULL_c`, with **k = EP21 (a visible parameter: RULED and CHOSEN, see below)**.
   K is the walk plus the arms every gated cell times at both layers; a fixed K makes
   the label a property of the cell's mechanism and not of how many variants were timed
   (rev 1 took the spread over every timed arm, so it grew with the arm count). The
   spread is taken over K's ns whatever the layer, since K is timed in every group.
3. **No pick loss `[r1 I-3]` (condition 3b):** ns(pick) − ns(best) ≤ NULL_c. A cell
   where the table's pick loses to the best is never consumer-bound; it stays in G3 and
   in every denominator. Because the pick depends on the filter, `cb` is per (cell,
   layer, filter).

Rev 2 had four conditions: material misses (≥ 50/KiB), equal misses over K (≤ 20%), and
conditions 1 and 3 above. The two miss conditions required perf counters, which D166
addendum 1 forbids as a requirement ("not everyone has the paranoia set to 2"). They
become the optional corroboration column below.

**What the timing rule means, honestly.** Rev 2's equal-misses test named a MECHANISM
(the consumer owns the misses). The timing rule names the OUTCOME: the cell is a tie,
nothing the scan does moves it, and the table's pick costs nothing. It cannot tell a
consumer-owned cell from a scan-owned cell where the forms simply tie, and does not try:
either way the table has no regret to remove there, and removing such a cell from the
DENOMINATOR (only) makes the percentage gates stricter. The cause is a separate fact
(the corroboration column, and the origin matter below). The class keeps its name `cb`
for continuity with the gate arithmetic; the report calls it "tie/consumer-bound".

**Choosing k `[D166a1]` (CHOSEN, not fitted; D149).** The evidence is the finished F2
cells (`gridread/f2_counts.txt`, cycles/pass as the ns proxy, NULL taken at gridread's
3.09% of the walk, the grid's own p90 A/A; a cell's NULL_c is at least that) and the
A/A figures in `gridread_report.md` §1.1 (F1 A/A median 0.20%, p90 3.37%; F3 p90 0.17%;
EXT p90 0.38%). `regime_eval/rev2_arith.py` part 1b prints, for each of the 18 F2
cells, the K spread in NULL units (`rev2_arith_out.txt`):

| reading | spread over K, in NULL_c |
|---|---|
| cells where the forms tie (walk best or within NULL, pick within NULL) | 1.4-2.1 (bounded docs1m 1.4, code1m 1.7, code64k 2.1; hex-run docs1m 1.6, code1m 2.1, prose1m 2.1) |
| the next cell up | 2.2 (bounded docs64k, repeated; its pick loses +6.9%) |
| hex-run docs64k (repeated; the walk loses 9.4% to the best) | 3.0 |
| every other cell | 4.8-9.6 (dfa-hat 4.8-8.2; bounded prose 6.2-6.8; hex-run code64k, prose64k 9.6, 7.9) |

- A spread is a difference of two arms, each with its own A/A: two independent arms at
  the p90 A/A is about √2 ≈ 1.4 NULL, so k must exceed √2; k = 2 sits on the tie
  cluster's edge (2.1 vs 2.0 drops three of the six tie rows to noise).
- **k = 3** sits between the tie cluster (at most 2.1, then 2.2) and the first
  scan-owned cell (4.8): 1.4× headroom above the cluster and 1.6× clearance below the
  scan-owned cells. The one reading at 3.0 (hex-run docs64k, repeated) fails condition 1
  regardless, because its walk loses 9.4%.
- The F2 cells with the equal-miss mechanism were bounded prose (spread 6.2-6.8 NULL: the
  SWAR and AVX2 forms are 19-21% slower than the walk at equal misses). Under the timing
  rule they are NOT consumer-bound at any k < 6.2: the cost of that mechanism now shows
  in the time, where it belongs, and those cells stay in every denominator. That is a
  stricter reading than rev 2's perf reading (gates only get harder to pass).
- **k is a declared, visible parameter `[r2.3]`** (Frank, Q-REVAL-17: "a configuration lever that shouldn't be hidden"). It is EP21 in §3.0a: named in the prereg bars file, printed in the header block of every report AND, in the CB block, beside the counts at EP22 (k = 2 and k = 4), overridable by `--cb-k=`, and listed with its provenance (CHOSEN, RULED by Frank 2026-10-14, re-read on grid2's streamed data before E5). A run at any other k is advisory (§3.0a).
- The evidence is thin (6 of 36 (cell, layer) rows read tie at k = 3, 0 of 36 read
  consumer-bound by rev 2's perf rule under S0). The report prints the CB count at
  k = 2 and k = 4 beside k = 3 (ungated, replacing rev 2's 10%/35% tolerances), so a
  boundary effect shows. On the F2 cells k = 3 and k = 4 agree; k = 2 loses three rows.
- The label is a property of the box's NULL and timing: marked Zen 4 only (`[r1 B-9]`).
  On Zen 1 the rule is evaluated from Zen 1's own timing and NULL (§2.4, J4).
  grid2's streamed timing (§2.1) re-reads this table on streamed subjects before E5;
  if the gap closes there, k (EP21) re-opens before the prereg, not after (Q-REVAL-17, RULED: k = 3 with that condition). The threshold is fixed in `prereg.tsv` before the judge slot (§3.4).

**What the class does `[r1 M-4]`.** A CB cell leaves the DENOMINATOR only. Its regret
stays in every numerator (by condition 3 it is at most NULL_c per cell, but it is
summed, never dropped). In rev 1 a CB cell left G2 and G3 altogether; with the
walk-vs-best condition alone, a cell whose pick lost +16% was classed CB and its loss
vanished from the gates. The panel's example (bounded prose1m, pick +15.8% / +19.0% of
walk under S0, `rev2_arith_out.txt`) fails condition 3 under S0, and under the timing
rule it fails condition 2 as well (spread 6.2 NULL).

**The optional corroboration column `[D166a1]` (UNGATED).** Where counters are available,
the perf pass's misses/KiB give rev 2's mechanism test (walk misses ≥ 50/KiB and the K
spread of misses/KiB ≤ 20% of the walk's, constants CHOSEN, Zen 4 only, with conditions
1 and 3 above). `cells.tsv` carries `cb_perf` = `agree` (both readings say CB or both
say not), `disagree`, or `unavailable` (no counters on this slot/box), and `summary.txt`
prints the three counts and the `disagree` cells. Nothing reads the column: no bar, no
control, no refusal, and `unavailable` is a normal value that fails nothing. On the F2
cells under S0 the perf reading is CB on none of the 36 rows (rev 2's 0.9% spread passes
only where the pick is the walk) and the timing rule reads six tie rows, so `disagree` is
expected to be nonzero, and is information about WHY a tie cell ties, not an error.

**Audit `[D166a1]`: nothing is gated on a counter.** Every bar, control, leg, prereg
field and refusal rule of this note was read for a dependence on perf counts:

| item | reads a counter? | state in rev 2.1 |
|---|---|---|
| G0 (floors; non-CB cell count) | through `cb` only | `cb` is timing-only: ungated by perf |
| G1, G2 (caps, W_exCB), G3 (outlier budget, non-CB cells) | through `cb` only | the same |
| G4 and C1-C8, the plants, the oracle (§4, §5.3, §5.4) | no | unchanged |
| NULL, ν, the A/A controls, cross-fit (§1.3, §4.3) | no (timing) | unchanged |
| the anchor replay, SET-MISMATCH, drift (§2.9) | no (timing) | unchanged |
| P-PRED | the walk's misses/KiB figure | that figure is OPTIONAL (`unavailable` is printed); the timing ratios stay |
| P-CB | the count at 10% / 35% tolerances (misses) | now the count at k = 2, 3, 4 (timing); the perf corroboration counts are extra |
| E4b's "CB re-read on streamed data" | grid2 perf | timing re-read; perf optional |
| `prereg.tsv` "perf event list" | yes | the rule's k and the denominator rule are fields; the event list is recorded ONLY if the pass ran, with `perf: ran / skipped` |
| refusal rules (§3.4) | no | none reads `perf` |
| J4 (Zen 1) CB labels | rev 2 inherited Zen 4's | computed from J4's own timing |
| set provenance | n/a | records `perf: ran | skipped (paranoid=N)`; a set with `skipped` is as valid |

**Reporting.** CB cells are LISTED, not hidden inside regime sums:

- `cells.tsv` carries `cb` (0, 1; `[D166a1]` never `unknown`, the rule needs timing
  only), `cb_spread_k` (the K spread in NULL_c units) and `cb_perf` (`agree`,
  `disagree`, `unavailable`; ungated);
- `summary.txt` has a CB block: count and share of RT cells per layer × regime × site
  kind, and the patterns whose cells are ALL consumer-bound;
- every denominator is given both ways:

  | quantity | WITH the class | WITHOUT the class |
  |---|---|---|
  | Σ walk ns per layer × filter × regime | W_all | W_exCB |
  | regret as walk-cost units | R / W_all | R / W_exCB (R includes CB cells' regret) |
  | outlier share (G3) | outliers / RT cells | outliers / non-CB RT cells |

- **What gates `[r1 I-3]`:** G2's caps and G3's rate gate on the WITHOUT-the-class
  DENOMINATOR (the stricter percentage), with every numerator complete. The with-class
  figures are printed beside every gated one, as gates in their own right that are
  reported and not gating ("with-class G2/G3"). G1 sums nanoseconds and is unaffected.
- E4b derives the in-sample figures of §3.1's caps from grid2's streamed fit cells with
  this definition, so the caps and the judge use one rule. `[D166a1]` It needs only
  grid2's TIMING rows.

A CB cell's cause is a pcrec/origin matter ([FIND-BOUNDARY-SIDE], origsurvey's
BYTE-ONLY 53%), not a table matter. The report says so beside the count.

### 2.8 Contamination and sealing `[r1 M-6]` `[r1 I-6]` `[r1 B-10]` (new)

**The disjointness proof (run at E6, before any judge timing; its output is committed
with the prereg's population files).**

1. Every judge buffer (each (S) buffer, each (W) subject, each `lines` bucket file,
   each WITNESS subject) is hashed in 4 KiB-aligned chunks (sha256 per chunk).
2. The same is done for every FIT buffer (grid1's and grid2's subjects, including
   their `prose1m`/`docs1m`/`code1m`), every E exemplar, and the findings corpora
   (`docs/dev/findings_measure/`'s inputs and the shipped analysis bundles' sources).
3. A judge buffer with ANY chunk hash in the FIT, exemplar or findings set is
   contaminated. It is replaced (a different offset) before the prereg, or, if the class
   corpus cannot supply a disjoint buffer, the class is served by (W) alone (§2.4), and
   the replacement is listed.
4. (W) subjects are also checked by BYTE RANGE: a (W) slice of a corpus file must not
   overlap the exemplar's or a FIT buffer's (file id, offset, length) range in the same
   file. That catches overlaps that are not 4 KiB-aligned. `[r2.2]` The exemplar is now
   the pool's RESERVE, a byte range inside one pool file (§2.4 rule 2), so every (S)
   window is checked by byte range against it too. A window that crosses the reserve
   continues after it by construction, and the check proves that.
4a. `[r2.2]` **Mislabelled files and pools.** No window, exemplar or (W) slice may come
   from a MISLABELLED file (§2.3b) or from outside the question's family pool. The proof
   lists each pool with its files, its reserve and its window count, and it lists every
   `short-pool` question.
5. **J2a ∩ ALPHA / spike / costmodel inputs.** A J2a cell is contaminated if its
   pattern (by text sha) or its subject (by sha, chunked as above) appears in ALPHA
   (slot25c), the spike's cells, or any input `costmodel_report.md` names. Those cells
   form J2a-contam: counted (K35), reported with their labels, and never gating.
   ALPHA's and the spike's pattern lists are kit artifacts, so this needs no bench read.

The proof's counts (buffers checked, contaminated, replaced, J2a-contam cells) lead the
manifest. A zero is printed as a zero.

**The sealed holdout.** At pre-registration the RT patterns of J1 are ranked by
`sha256(prereg_salt || pattern_sha)`, and the bottom EP44 share (rounded up, at least EP45 patterns per class where the class has 15 or more) form J1-sealed. `[r2.2]` On the real
population that is about 17 of 54 RT patterns; only prose (16 RT, est) reaches the
15-pattern clause. A sealed regime below G0 at the final reading is judged on the pooled
population, labelled, with its sealed-only figure beside it (EP46, RULED, Q-REVAL-16; §2.4 power table item 4). `prereg_salt` is a
random value committed IN `prereg.tsv`, so the split is fixed before any timing and is
not the kit's choice. J1-sealed groups are timed in the same slots, interleaved, under
the same conditions. Their raw logs are moved, unparsed, to a `sealed/` directory in the
slot scratch, and the sha256 of each sealed log goes into the manifest. Judge mode never
parses `sealed/` unless run as `--final` with an UNSEAL line in main's journal that
names the prereg version and the table listing sha it judges. After unsealing, J1-sealed
is contaminated for every later version. `summary.txt` prints J1-open and J1-sealed
separately and pooled.

**J1b.** Written now by the blinded user agent (main's lane); its sha256 goes into
`prereg.tsv` unopened. It is opened only for the pre-registration that follows a FAIL
(§2.2).

**Every prereg version is listed.** `regime_eval/prereg_versions.tsv`: version, blob
sha, main's journal entry hash that recorded it, the populations it was judged on, the
verdict, and what it contaminated. A run's manifest names the version it read.

### 2.9 The wrong-box set and the per-slot anchors `[r1 M-8]` `[r1 M-5]` (new)

A set's constants are true of the box, compiler and state it was fit on. A judge failure
caused by a wrong or stale set must not be blamed on the table.

- **Refusal.** The set file's `box` (CPU model string + host id) and the slot log's
  must match. A mismatch is a hard refusal unless `prereg.tsv` declares the run as C6
  (§4.1), the wrong-box control.
- **The FIT anchor replay.** Each judge slot starts by re-timing the set's FIT ANCHOR
  SUBSET (EP33 groups from grid2's streamed fit cells, chosen at E4b to cover every
  scorable row's fit evidence; listed in the set). For each anchor and each form the
  evaluator computes the walk-relative ratio ns(form)/ns(walk) and compares it with the
  set's recorded ratio. An anchor DEVIATES if any form's ratio differs by more than EP34·NULL_c/ns(walk), or if its best form differs beyond NULL. If more than EP35 of anchors deviate, the slot reads **SET-MISMATCH**: its judge figures are reported, but
  a gate failure in that slot is attributed to the set (box, compiler or state), not to
  the table, and the judge must be re-run on a matching set. Otherwise a judge failure
  goes to the table. (Every constant here is a row of §3.0a: EP33-EP39.)
- **The drift check.** The slot ends by re-timing EP36 of the anchors (walk and their best
  arm). If the walk's ns moved by more than EP37·AA between start and end on more than EP38 of the EP36, the slot reads DRIFT and its gated cells are flagged; G1-G3 are reported
  with and without the DRIFT slot, and a gate that passes only with it reads
  INCONCLUSIVE.
- `walk#c` (§1.2) is the within-group drift and A/A check; the anchors are the
  between-slot one.

### 2.10 J2a and the bench boundary `[r1 B-1]` (new)

Rev 1 said a published bench subject under 1 MiB is replaced by "a STREAMED set
generated from the bench's published generator at distinct seeds". Read on the bench at
db629a54: `bench/bounded/gen_throughput_subjects.py` hard-codes `SEED = 20260830` and
`OUT = <its own dir>/throughput`, and its `main()` writes there and rewrites
`manifest_throughput.tsv`. Running it would write into pcrec-bench, which is a mandate
breach. The bench's other throughput generators (capability, email, syntax, utf8,
loglines, altwide, litrun) have the same shape: a hard-coded `OUT` under the bench tree.

What CAN be imported without writing anything:

| library | sub-bench | what it offers | module-level side effects (read at db629a54) |
|---|---|---|---|
| `bench/bounded/boundedtext.py` | bounded | `Rng(seed)` (on `random.Random(seed).getrandbits(32)` only), `prose(rng, nbytes)`, `letters`, `digits`, the shape generators (`year4`, `hex32`, `dotted4`, `csv5`, ...) | none: it inserts the bench root into `sys.path` and imports `pcrecbench.periodic`; no file opened |
| `bench/loglines/logtext.py` | loglines | `Rng(seed)`, `background(rng)` log lines, `syslog_only`, `feature_line(rng, feature)` | none: the same `sys.path` insert and import |
| `captext.py`, `censustext.py`, `utf8text.py` | capability, syntax, utf8 | line and sentence generators on their own `Rng` | headers read only; `utf8text` OPENS a data file for reading. Not confirmed for use: in the relay question |

**`[r2.2]` The DEFAULT path: a byte transfer of the bench's existing ≥ 1 MiB subjects.**
Q-REVAL-15 was relayed as I-152 and has no answer yet. So the path that needs nothing
from the bench beyond bytes it already has becomes the default. It was item 4 below.

- Main arranges a byte transfer of the 11 subjects to a kit-readable scratch location,
  through its own channel with the bench dev (D78). The kit never reads the bench
  checkout's untracked files and never writes there.
- Each file must match the sha256 in the committed `manifest_throughput.tsv` at a pinned
  bench commit C, which the kit reads with `git show`. A mismatch is not used, and it is
  listed.
- The prereg records C, each manifest row and each received file's sha256.
- J2a's lean draw is 20 patterns, chosen by h(`j2a`, pattern sha) from the sub-benches
  that have a subject (capability, email, loglines, syntax, utf8). Each runs on one of its
  sub-bench's W subjects, chosen by h(`j2aW`, pattern sha).
- bounded, altwide, litrun and sentinel have no subject on this path: their patterns are
  J2a-NOSUBJECT, counted.
- Until the bytes arrive, every J2a cell is J2a-NOSUBJECT and J2a's gate weight prints 0.
  The gates then rest on J1-open alone, which is what the §2.4 power table assumes
  anyway.

The import route (items 1-3 below, with kit seeds, from a `git archive` extract) becomes
the ALTERNATIVE. It is taken only if the bench answers I-152 (a) yes. It would add (S)
subjects for bounded and loglines, but it changes no gate's power.

**The rule** (`[r2.2]` the ALTERNATIVE route, items 1-3; item 4 is now the default above).

1. The kit takes a pinned bench commit C and extracts ONLY the library files plus
   `pcrecbench/periodic.py` into kit scratch:
   `git -C pcrec-bench archive C bench/bounded/boundedtext.py bench/loglines/logtext.py pcrecbench/periodic.py | tar -x -C $SCRATCH/benchlib`.
   Nothing is ever imported from the live bench checkout, so no `__pycache__` or other
   file can appear there.
2. A kit script (in the kit's tree) imports the libraries from `$SCRATCH/benchlib` under
   `python3 -I -B`, with KIT seeds (recorded in the manifest, distinct from every bench
   `SEED`), and writes (S)/(W) subjects only to the kit's slot scratch.
3. The prereg records C, the sha256 of each extracted file, the kit seeds, and the
   generated subjects' shas. J2a cells of sub-benches without a confirmed library are
   served by step 4 or counted as J2a-NOSUBJECT.
4. **Fallback, condition W on the bench's EXISTING subjects.** The bench's committed
   `manifest_throughput.tsv` files list 11 subjects of at least 1 MiB (capability
   `t-1m`; email `t-a`..`t-e`, five; loglines `t-1024k-fail`/`-syslog`/`-hit`; syntax
   `t-1m`; utf8 `t-1m`). Their bytes are gitignored and are NOT present in this box's
   checkout. They may be used only if obtained without writing to the bench: provided by
   the bench dev to a kit-readable location, or reproduced by calling the generator's
   pure `build()` from a `git archive` extract in kit scratch, with no `main()`. Either
   way, each must match the committed manifest's sha256 byte for byte, or it is not
   used. Whether the second route is acceptable is the bench dev's call (Q-REVAL-15).
   bounded, altwide, litrun and sentinel have no ≥ 1 MiB subject, so their patterns are
   J2a-NOSUBJECT under the fallback, unless (S) from `boundedtext` serves bounded.
5. **The relay question** goes to the bench dev via main before E6 (Q-REVAL-15). ~~Until it
   is answered, J2a runs on (S) from `boundedtext` and `logtext` only, and every other
   J2a cell is counted J2a-NOSUBJECT.~~ `[r2.2]` It was relayed as I-152. Until it is
   answered, J2a follows the default path above. J2a's gate weight is printed (§3.1, G0).

## 3. Pre-registered acceptance (loose, per Frank)

Frank (2026-10-13): looser bars are fine. Outliers and some regression are accepted for
a cleaner, clearer design. What is not loose is WHEN the bars are fixed, and `[r1 M-3]`
what each bar can and cannot see.

### 3.0a The evaluator parameter table: a [KNOW-SRC] kind `[r2.3]` `[r2.4 KNOW-SRC]`

Frank (2026-10-14, Q-REVAL-17): "a configuration lever that shouldn't be hidden." Every
harness constant in this note that can change a verdict, a label (PASS, FAIL, UNDERPOWERED,
UNREACHED, CONFIRMED, REFUTED, `short-pool`, DRIFT, SET-MISMATCH), a population or a
sealed split is a DECLARED, VISIBLE parameter, one row of the table below, and nowhere
else. The prose of this note refers to a row as "EPnn" or by name and does not restate
the number; where a number still appears in prose it is an example, and the table wins.
No script holds one as a buried literal (the six plan-arithmetic constants are the one
stated exception, below).

**`[r2.4 KNOW-SRC]` The table is not a private table.** Frank's ruling (2026-10-14, via the
pcrec manager): the evaluator parameter table is ONE MORE [KNOW-SRC] KIND, named
**`evaluator-params`** (plan row [KNOW-SRC]; `docs/design/measure_sets.md` §9; D166). It
is a member of the family of §9.1 beside the analysis object, measurement sets and
[TABLE-JUDGE]'s picks. Four consequences:

1. **The FILE is the source of truth, and the table below mirrors it.**
   `docs/design/memfn/regime_eval/regime-eval.evaluator-params.tsv` is a `table_contract.md`
   `#section` file in the shape `measure_sets.md` §1.2 and §9 fix, with sections `header`,
   `params` and `bindings`. The file name follows the kind's `<name><suffix>` pattern (§9.2:
   the analysis `.rxt`, the sets' `.measures.tsv`, the picks' `.picks.tsv`), so the suffix
   is `.evaluator-params.tsv` and the kind name is `evaluator-params`. The markdown table
   below is that file's `params` section, one row per line, with the `class` folded into
   the provenance column and the `printed` column dropped (it reads "header block" for every
   row except EP21 and EP22, which are also printed beside the k = 2 / 4 counts, below).
   A disagreement between the two is a defect of the note, never of the file.
2. **The prereg hash IS the kind's DIGEST.** `prereg.tsv` carries the kind's stamp item,
   `regime-eval@1:<digest16>` (`id@rev:digest`, §9.5's measures spelling), in place of rev
   2.3's separate `params_sha256`. The digest is [KNOW-SRC]'s `ks_digest` (§9.2 part 5):
   FNV-1a-64 with the domain prefix `pcrec-eparm-1`, 16 hex, over the `params` rows `id`,
   `name`, `value` in id order. The design-time value is in the file's header
   (`values_digest`), computed by that recipe by hand; the loader recomputes it, and the
   first R-check (R1, below) is where a disagreement is found. FNV is not collision-hard,
   and it is not asked to be: the prereg file is ALSO covered by its own blob sha (§3.4),
   which covers the provenance text and the `bindings` section the digest leaves out.
3. **The report's "diff against prereg" IS the census tool's diff.** The DIFF block below
   is `scripts/knowledge_census.sh evaluator-params OLD NEW`'s output for the kind (§9.3),
   OLD = the prereg's pinned file, NEW = the effective table (the file with the overrides
   applied). The tool compares rows by id and reports each differing value with the
   override that set it. For this kind no compile population is involved: the "movers" are
   the differing rows themselves, and the attribution (which gates read the row) is the
   `gates` column.
4. **The table is listed through `--list-evaluator-params`.** The four views of §9.2 part 6:
   the index (`--list-evaluator-params`, bare: one row per reachable item, here the file
   and any `-I`/FILE item), the CANONICAL view (`--list-evaluator-params NAME|FILE
   --view=canonical`, which IS a loadable input of the kind: ROUND-TRIP identity, §9.6), a
   derived view (`--view=gates`: per gate, the rows it reads, from the `gates` column) and
   the per-target view (not applicable: the kind shapes no artifact, so no stamp lands in
   generated code). The kind row: suffix `.evaluator-params.tsv`; stops FILE and `-I` only
   (no embedded store: the evaluator is a harness, and the committed file is its default);
   `cli_flag` none (the evaluator's own `--param`, below); digest domain `pcrec-eparm-1`;
   derived sections the loader rejects: `gates`. Until [KNOW-SRC] is built, the file is
   written in this canonical shape from day one (as the kit's interim measurement set is),
   the evaluator reads it with a small `#section` reader of its own, and the K-steps replace
   that reader by the module at zero movers.

**Placement rule, applied to every row (Frank, 2026-10-14).** Compiler numbers go to
`limits.def`; measured decision numbers go to measurement sets; harness thresholds go to a
[KNOW-SRC] kind. Rev 2.3's 72 rows were checked one at a time against it:

- **62 rows stay** as harness thresholds (below): a count, a share, a multiplier, a size or
  a switch the evaluator CHOOSES or that was RULED; none is a measurement of the box. No
  row is a compiler number: nothing here becomes an emitted byte or a compile-time limit.
- **4 rows MOVE to the measurement set** (the sub-table "Rows moved out"): they are
  numbers DERIVED from timing, so they are measured decision numbers by the rule, and they
  are re-derived per slot or per box, which a harness-threshold file cannot carry without
  a hand-injected value. The ids are kept (so prose that says EP14, EP16, EP30 or EP58
  stays correct); the `bindings` section of the file records, per moved id, the
  measurement key and source it is read from, and the `params` section carries no value.
- **6 rows LEAVE the kind** (EP67-EP72, "Plan arithmetic"): they never change a verdict
  and the judge never reads them; EP67, EP68 and EP72 are measurements (grid1's seconds per
  launch and F2's perf pass) that belong to grid1's logs as provenance, and EP69-EP71 are
  the plan-arithmetic scripts' own estimates. They stay as the scripts' header literals,
  printed in their output, as rev 2.3's `regime_eval/CLAUDE.md` already said.

Two borderline rows STAY, with the reason, so a later reader can overturn them:

1. **EP56 `regime-L` and EP57 `regime-g`** are the edges of the REPORTING buckets (DINGHY /
   TUG / LINER; never a pick), RULED by main (Q-REVAL-9). They look like crossovers but are
   definitions of a label. If regime_tables later DERIVES `g` from a set's crossover, EP57
   moves to the set in the same change.
2. **EP47 `prereg-salt`** is drawn once at E5 from a random source and then fixed. It is a
   harness constant (no measurement), `unset` in the design copy; a GATING run refuses
   `unset`, and E5's freeze is a new rev of the file.

The rows are of two kinds, named in the provenance column (rev 2.3's DERIVED kind is gone
from this kind: those rows moved, above):

- **CHOSEN**: picked by the kit, justified in the section that uses it, not fitted to a
  reading (D149). "List RULED (Q-REVAL-16)" means Frank agreed the list on 2026-10-14 (rev 2's
  constants plus both loosenings).
- **RULED by <who, date>**: set by a ruling. A ruled value that is also a judgement call
  (k = 3) says so.

**What each column means.** `name` is the key in the prereg file; `override` is the
long option on `regime_eval.py` (`--<name>=VALUE`, and the generic `--param NAME=VALUE`);
`printed` (a file column) is where the value shows up beyond the header block that lists
every row. A list value is `;`-joined (EP22, EP24, EP64).

#### Override semantics (restated as overrides of a [KNOW-SRC] kind's values) `[r2.4 KNOW-SRC]`

The semantics are rev 2.3's and are unchanged in spirit; they are now stated against the
kind. An override replaces a row's value for one run. It is never an edit of the file, and
the evaluator writes nothing back to it.

1. **Overrides are allowed, for exploration.** Any row can be set on the command line, for
   `--check`, replays, what-if runs and the controls. The evaluator never refuses an
   override as such. `--param NAME=VALUE` is the kind's generic override; the per-row
   `--<name>=` spellings are its aliases. A moved row (EP14, EP16, EP30, EP58) is
   overridden the same way, by a literal, or by `FILE` naming another measurement set (the
   override then names that set's `id@rev:digest`).
2. **A run whose effective table differs from the pre-registered one is NON-GATING.** The
   evaluator compares the effective table with the prereg's pinned digest and, row by row,
   with the pinned file (the census diff, consequence 3). If ANY row differs, the run:
   - labels its status line `advisory: parameters differ from prereg <blob sha8>`;
   - prints every gate, control and prediction reading with the prefix `ADVISORY` and
     never as a bare PASS/FAIL; a shell exit code 3 (distinct from the exit codes of PASS,
     FAIL and refusal) tells scripts it was not a gate;
   - writes its results under an `advisory/` directory and does not append to
     `prereg_versions.tsv`, so it can neither pass a table nor fail one;
   - lists every differing parameter, with the pre-registered value, the effective value
     and the override that set it.
3. **Judge mode (§3.4) is stricter.** `--judge` and `--final` still refuse to start on any
   prereg mismatch, and `--final` additionally refuses ANY override: the unsealing never
   happens on an advisory run. A judge run with an override is an advisory run, not a
   judge run. A MOVED row's value is read from the measurement set the prereg names (its
   `id@rev:digest` is a prereg field) and recomputed from that set's rows; a hand-injected
   value is an override.
4. **Changing a pre-registered value after a reading** is the §3.4 rule (a new
   pre-registration, a new population, a new slot). The override option is the way to see
   what a change would do before one is made; it is not the way to make one. A change to a
   row of the file is a new `rev` of the file and so a new digest.

#### What every report prints at its top

`summary.txt`, and the standard output of every mode, begin with the same block, before any
gate line:

```
PARAMETERS  evaluator-params regime-eval@1  digest <16hex> (prereg) / <16hex> (effective)   prereg <blob sha8> (version N)
STATUS      GATING | advisory: parameters differ from prereg <blob sha8>
id    name              value      prereg value   provenance
EP01  noise-factor      2          2              CHOSEN; carried by Q-REVAL-16 (...)
...                                                (all params rows, in id order)
EP14  r-in              (measurement set <id@rev:digest>, shas of its source logs)
...                                                (the four moved rows, from the set)
DIFF        none | n parameter(s) differ:        (knowledge_census.sh evaluator-params OLD NEW)
            EP21 cb-k        3 -> 2   (--cb-k=2)
```

- The block lists EVERY row, not only the differing ones, with its provenance, so a reader
  never has to look up what was in force. The four moved rows print the value used and the
  set and source sha it came from.
- The DIFF block is last, one line per differing row, and is empty only on a GATING run.
- `manifest.tsv` carries the same table (so a diff of two runs shows a parameter change as
  a data change), and `params.tsv` is the effective table in the kind's CANONICAL view (so
  it is itself a loadable input: a run can be replayed by feeding its `params.tsv` back).
- **k is printed twice.** The header block shows `cb-k` (EP21), and the CB block (§2.7) and
  P-CB print the CB count at `cb-k-report` (EP22: k = 2 and 4) beside the count at the gated
  k, labelled with their values, so a boundary effect is always on the page.

**The table (the `params` section of `regime-eval.evaluator-params.tsv`; 62 rows)**

| id | name | value | unit | what it gates | provenance | override | placement |
|---|---|---|---|---|---|---|---|
| EP01 | noise-factor | 2 | × N(S) | every bar's noise allowance (G1, G2, controls' WORSE test, C7 a) | CHOSEN (about two standard errors); list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--noise-factor=` | harness |
| EP02 | g1-min-cells | 10 | cells | G1 UNDERPOWERED: fewer differing cells than this | CHOSEN; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--g1-min-cells=` | harness |
| EP03 | g1-min-visible | 0.05 | of W(D(P)) | G1 UNDERPOWERED: 2·N above this share of walk cost | CHOSEN; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--g1-min-visible=` | harness |
| EP04 | g2-power-frac | 0.5 | of cap | G2 UNDERPOWERED: 2·N/W_exCB above this share of the cap | CHOSEN; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--g2-power-frac=` | harness |
| EP05 | g3-min-cells | 40 | non-CB RT cells | G3 UNDERPOWERED below this | CHOSEN; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--g3-min-cells=` | harness |
| EP06 | m-min | 5 | moved cells | a control's UNDERPOWERED line; witness cells per scorable row (§2.1, §4.4) | CHOSEN; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--m-min=` | harness |
| EP07 | g0-min-cells | 20 | RT cells per layer × regime × filter | G0 UNREACHED below this | CHOSEN; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--g0-min-cells=` | harness |
| EP08 | g0-min-patterns | 5 | patterns | G0 UNREACHED below this | CHOSEN; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--g0-min-patterns=` | harness |
| EP09 | w-min | 0.25 | RT share of J1 patterns | G0 weight: below it every PASS reads LOW-WEIGHT PASS | CHOSEN; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--w-min=` | harness |
| EP10 | cap-mult | 1.25 | × R_in(r) | cap(DINGHY), cap(TUG) | CHOSEN; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--cap-mult=` | harness |
| EP11 | cap-add | 2 | points of walk | cap(DINGHY), cap(TUG) | CHOSEN; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--cap-add=` | harness |
| EP12 | cap-mult-liner | 1.0 | × R_in(LINER) | cap(LINER) | CHOSEN; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--cap-mult-liner=` | harness |
| EP13 | cap-add-liner | 2 | points of walk | cap(LINER); was 1 before the ruling (LINER cap R_in + 2) | RULED by Frank, 2026-10-14 (Q-REVAL-16), loosening 1 | `--cap-add-liner=` | harness |
| EP15 | g3-floor-calls | 3 | × w_call | the per-call floor F = 3·w_call of an outlier | CHOSEN; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--g3-floor-calls=` | harness |
| EP17 | g3-walk-frac | 0.25 | × ns_walk | an outlier's per-pass threshold max(F, this·ns_walk) | CHOSEN; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--g3-walk-frac=` | harness |
| EP18 | g3-rate | 0.05 | of non-CB RT cells | G3 (a): outlier share allowed | CHOSEN; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--g3-rate=` | harness |
| EP19 | g3-budget-frac | 0.25 | of the table's summed saving | G3 (b): summed outlier excess allowed | CHOSEN; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--g3-budget-frac=` | harness |
| EP20 | partial-cap | 0.10 | of a gate population's RT cells | a gate reads UNREACHED above this share of partial cells | CHOSEN; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--partial-cap=` | harness |
| EP21 | cb-k | 3 | × NULL_c | consumer-bound condition 2: the ns spread over K at most k·NULL_c | RULED by Frank, 2026-10-14 (Q-REVAL-17); value CHOSEN; re-read on grid2's streamed data before E5 | `--cb-k=` | harness; condition-bearing (Q-REVAL-17) |
| EP22 | cb-k-report | 2;4 | × NULL_c | reported only: the CB count at each, beside the gated k (P-CB) | CHOSEN; printed beside k by Q-REVAL-17 condition | `--cb-k-report=` | harness |
| EP23 | cb-null-mult | 1 | × NULL_c | CB conditions 1 and 3 (walk − best, pick − best) | CHOSEN; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--cb-null-mult=` | harness |
| EP24 | cb-arms | walk;V1;A1 | arm set K | the arms the CB spread is taken over | CHOSEN; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--cb-arms=` | harness |
| EP25 | cb-perf-misses | 50 | misses/KiB | OPTIONAL, ungated corroboration only (cb_perf column) | CHOSEN; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--cb-perf-misses=` | harness |
| EP26 | cb-perf-spread | 0.20 | of the walk's misses | OPTIONAL, ungated corroboration only (cb_perf column) | CHOSEN; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--cb-perf-spread=` | harness |
| EP27 | launches | 3 | per judge group | cross-fit and NULL (the paired-sign rule) | RULED by main, 2026-10-14 (Q-REVAL-8) | `--launches=` | harness |
| EP28 | launches-witness | 5 | per WITNESS group | witness power | RULED by main, 2026-10-14 (Q-REVAL-8) | `--launches-witness=` | harness |
| EP29 | rerun-extra | 2 | launches added | a group whose walk vs walk#b disagrees beyond NULL in any launch | CHOSEN; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--rerun-extra=` | harness |
| EP31 | noisy-factor | 2 | × grid2's ν | a slot reads NOISY (flagged like DRIFT) above this | CHOSEN; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--noisy-factor=` | harness |
| EP32 | c7-best-disagree | 0.05 | of cells with top-two arms differing beyond NULL_c | C7 (b), the split-half best-arm disagreement | CHOSEN; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--c7-best-disagree=` | harness |
| EP33 | anchor-n | 30 | FIT anchor groups | the per-slot anchor replay (chosen at E4b) | CHOSEN; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--anchor-n=` | harness |
| EP34 | anchor-dev-factor | 2 | × NULL_c/ns_walk | an anchor DEVIATES when a form's walk-relative ratio differs by more | CHOSEN; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--anchor-dev-factor=` | harness |
| EP35 | setmismatch-frac | 0.20 | of anchors | SET-MISMATCH when more than this share deviate | CHOSEN; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--setmismatch-frac=` | harness |
| EP36 | drift-n | 10 | anchors re-timed | the end-of-slot drift check | CHOSEN; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--drift-n=` | harness |
| EP37 | drift-factor | 2 | × AA | an anchor's walk ns moved by more than this | CHOSEN; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--drift-factor=` | harness |
| EP38 | drift-max | 3 | anchors of drift-n | DRIFT when more than this many moved | CHOSEN; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--drift-max=` | harness |
| EP39 | w2-drift-agree | 7 | of 10 anchors within 2·AA | LEAN plan: W2 inherits W1's SET-MISMATCH reading (else a full replay) | CHOSEN; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--w2-drift-agree=` | harness |
| EP40 | load1-max | 1.5 | load1 | a group at or above it at either sample is discarded (reason load) | CHOSEN, inherited from grid1's quiet gate; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--load1-max=` | harness |
| EP41 | load-consecutive | 3 | discarded groups in a row | slot ABORTS (BREACH) | CHOSEN; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--load-consecutive=` | harness |
| EP42 | load-persist | 5 | minutes | slot ABORTS (BREACH) | CHOSEN; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--load-persist=` | harness |
| EP43 | load-requeue | 1 | re-queues | a twice-discarded group is GATE-EXCLUDED for good | CHOSEN; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--load-requeue=` | harness |
| EP44 | sealed-share | 0.30 | of RT patterns, rounded up | J1-sealed size | CHOSEN; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--sealed-share=` | harness |
| EP45 | sealed-min-class | 5 | patterns per class of 15 or more | J1-sealed size | CHOSEN; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--sealed-min-class=` | harness |
| EP46 | sealed-pooled-final | on | flag | the final reading judges a sealed regime below G0 on the pooled population, sealed-only figure beside it | RULED by Frank, 2026-10-14 (Q-REVAL-16), loosening 2 | `--sealed-pooled-final=` | harness |
| EP47 | prereg-salt | unset | bytes | the sealed split, the window draws, the second parser's cells | CHOSEN once, at random, committed in prereg.tsv | `--prereg-salt=` | harness; value drawn once at E5 (note 2) |
| EP48 | window-bytes | 65536 | bytes | size of one streamed (S) buffer | CHOSEN; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--window-bytes=` | harness |
| EP49 | windows-max | 64 | windows (4 MiB) | most windows per streamed subject | CHOSEN; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--windows-max=` | harness |
| EP50 | window-floor | 16 | windows (1 MiB) | below it a pool cannot stream: short-pool, GATE-EXCLUDED | CHOSEN (F2's fresh size); list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--window-floor=` | harness |
| EP51 | reserve-frac | 0.125 | of the pool | the exemplar reserve R = max(reserve-min, this·pool) | CHOSEN; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--reserve-frac=` | harness |
| EP52 | reserve-min | 65536 | bytes | the exemplar reserve R | CHOSEN; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--reserve-min=` | harness |
| EP53 | w-subject-min | 1048576 | bytes | a (W) subject's minimum size (F2's fresh size) | CHOSEN; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--w-subject-min=` | harness |
| EP54 | bucket-min-bytes | 65536 | bytes of lines | a lines bucket below it has no group | CHOSEN; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--bucket-min-bytes=` | harness |
| EP55 | rep64k-per-class | 2 | patterns | the ungated rep64k column (LEAN) | CHOSEN; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--rep64k-per-class=` | harness |
| EP56 | regime-L | 64 | bytes per activation | DINGHY if L below it (a REPORTING bucket; never a pick) | RULED by main, 2026-10-14 (Q-REVAL-9) | `--regime-L=` | harness; reporting-bucket edge ruled by main, not a measurement (note 1) |
| EP57 | regime-g | 18.5 | bytes per use | TUG if g below it, else LINER (reporting only) | RULED by main, 2026-10-14 (Q-REVAL-9) | `--regime-g=` | harness; reporting-bucket edge ruled by main, not a measurement (note 1) |
| EP59 | p-r1 | 0.80 of lines cells with N < 32 | share | P-R1 CONFIRMED / REFUTED | CHOSEN; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--p-r1=` | harness |
| EP60 | p-r5 | 0.5 | of SIMD-on DINGHY regret | P-R5 | CHOSEN; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--p-r5=` | harness |
| EP61 | p-e | 2 | points of walk | P-E | CHOSEN; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--p-e=` | harness |
| EP62 | p-rt | 0.40 | of J1 patterns | P-RT (written before any reading; not moved by §2.3a) | CHOSEN; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--p-rt=` | harness |
| EP63 | p-bnd | 1 | × NULL_c | P-BND | CHOSEN; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--p-bnd=` | harness |
| EP64 | pmove-top | 5;10;25 | percent of cells | P-MOVE's concentration shares (reported) | CHOSEN; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--pmove-top=` | harness |
| EP65 | row-unexercised | 10 | RT cells | Q-REVAL-2's deletion proposal and the unexercised label (§4.2) | RULED by main, 2026-10-14 (Q-REVAL-2) | `--row-unexercised=` | harness |
| EP66 | second-parser-cells | 30 | cells | the second parser's spot check (§5.3) | CHOSEN; list RULED by Frank 2026-10-14 (Q-REVAL-16) | `--second-parser-cells=` | harness |

**Rows moved out to the measurement set (EP14, EP16, EP30, EP58)**

| id | name | value | unit | read from (the file's `bindings` section) | override |
|---|---|---|---|---|---|
| EP14 | r-in | per layer × regime × filter | points of walk | key `kit.reval_r_in.<layer>.<regime>.<filter>`: the in-sample reference of every cap and of the HEADLINE, DERIVED from zen4-grid2's streamed fit cells (E4b), with the grid2 log shas | `--r-in=VALUE, or FILE` |
| EP16 | w-call | about 16 on Zen 4 | ns per DINGHY call | key `kit.reval_w_call`: F's unit, the active set's own walk cost per DINGHY call | `--w-call=VALUE, or FILE` |
| EP30 | nu | per slot, median of abs(walk − walk#c)/walk | ratio | key `kit.reval_nu.<slot>`: NULL_c = max(AA_c, ν·ns_walk) and so every N; DERIVED from the slot's walk#c groups; grid2's value is the NOISY reference (EP31) | `--nu=VALUE, or FILE` |
| EP58 | bucket-edges | every N-boundary of the active and control sets (today 14, 32, 64) | bytes | a DERIVED VIEW of the sets named in prereg.tsv, computed from their rows each run; no key | `--bucket-edges=VALUE, or FILE` |

The keys are PROPOSED: the owner is `kit` (the evaluator is the kit's harness; D157 keeps
pcrec out of the kit's vocabulary), the quantity names are the kit's to confirm, and a
method card (`measure_sets.md` §7.2) must exist for each before the first set carries one.
`r-in` (points of walk) and `nu` (a ratio) are dimensionless, as D166 wants; `w-call` is an
absolute ns and is carried as its row's walk-relative `value_e6` with the absolute in
`abs_ns_e6` as provenance, not as a free-standing absolute.

**Plan arithmetic (not a kind; EP67-EP72)**

| id | name | value | unit | provenance | where |
|---|---|---|---|---|---|
| EP67 | sec-stream | 0.95 | s per launch | measured in grid1 §3 (grid1's provenance, not a decision) | `rev2_arith.py`, `rev22_arith.py` header |
| EP68 | sec-rep | 0.65 | s per launch | measured in grid1 §3 | the same |
| EP69 | f-rerun | 0.20 | of groups | CHOSEN (an estimate; the realised share is reported) | the same |
| EP70 | check-s | 4.0 | s per group | CHOSEN (rev 1's figure, scaled) | the same |
| EP71 | slot-fixed | 13 | min per slot | CHOSEN | the same |
| EP72 | perf-s-row | 0.6 | s per perf row | measured in F2 (72 rows in 43 s) | the same |

Not parameters of the evaluator, and so not rows: the harness contracts it inherits from
grid1 (rounds per launch, CPU pinning, governor), which are recorded in the set's
provenance and checked by the correctness gate; and the formulas themselves (quadrature
over groups, the cross-fit rule, the placement and CB rule structure), which are code
pinned by the evaluator blob shas of §3.4. A change to a formula is a change to the
evaluator and is caught there, not here.

**Checks of the kind.** They ride [KNOW-SRC]'s `make test-knowledge` (§9.6) when it exists;
until then the evaluator's `--check` runs the same four on this one file: R1 load → list →
load keeps the digest; R2 list → load → list is byte-identical; R3 the independent python
parser agrees on every section and column; R4 the committed file IS its canonical view.
Plus two checks of this kind alone: every `params` row's `override` equals the long option
the prose names (grep of this note), and every EPnn in the prose resolves to a `params`,
`bindings` or plan row (no orphan id).


### 3.0 Units and the noise rule `[r1 M-3]` `[r1 B-9]` (new)

**Walk-cost units.** For a set S of cells, `W(S) = Σ_{c∈S} ns_walk(c)` (the walk's ns,
cross-fit launch-mean, §1.3). A regret sum R(S) in walk-cost units is `R(S)/W(S)`.
Ratios of ns on the same cells cancel the box's clock, so a bar stated this way means
the same on Zen 4 and Zen 1. Absolute constants that remain are tied to the SET (G3's
per-call floor) or re-derived per slot (ν).

**The noise rule: quadrature over independent timing groups.** For a set S of cells,

```
N(S) = sqrt( Σ_{g ∈ groups(S)} ( Σ_{c ∈ S ∩ g} NULL_c )² )
```

The cells inside one group (its layers and filters) share launches, so their noise is
added LINEARLY within the group (conservative: fully correlated). Different groups are
timed in different, rotated windows, so their noise is independent and adds in
QUADRATURE. Every bar's noise allowance is EP01·N(S) (EP01 = 2 today, about two standard errors when NULL_c is a one-sided ~1σ-to-2σ floor; the factor is pre-registered, not fitted).

**Why quadrature and not a cell bootstrap.** The quantity to bound is MEASUREMENT noise
in the difference between two policies on the same cells. NULL_c is already a per-cell
measured bound on that noise (A/A floor or ν·walk). The groups are independent by
construction (rotated, separated in time), which is exactly the condition for quadrature.
The rule is closed-form and deterministic, so `--check` reproduces it bit for bit and
the prereg can pin it without an RNG seed. A bootstrap over CELLS estimates a different
quantity: how the population SAMPLE varies, which is a generalization question. That
question is answered here by the held-out design itself: J1-open vs J1-sealed vs J2a,
reported separately. A bootstrap over LAUNCHES would need more than 3-5 launches per
group to be stable. Rev 1's linear sum over-allowed by about √(number of groups): on the
prototype's 132 groups it was 2-3× the aggregate A/A, so G1 was vacuous when the table
and a policy differ on few cells (M-3).

**Power floors.** A bar is UNDERPOWERED, which is never PASS, when it cannot see the
difference it exists to see:

| bar | UNDERPOWERED when |
|---|---|
| G1 vs policy P | the differing set D(P) has fewer than EP02 cells, or EP01·N(D(P)) > EP03·W(D(P)) (it cannot see a EP03 share of walk difference where the table and P differ) |
| G2, per regime | EP01·N(regime) / W_exCB(regime) > EP04·cap (the noise allowance would be more than that share of the cap) |
| G3 | fewer than EP05 non-CB RT cells (the outlier rate EP18 would then be fewer than 2 outliers) |
| a control (§4.2) | fewer than m_min (EP06) moved cells |

A gate's verdict is the worst over its comparisons, in the order FAIL > UNDERPOWERED >
UNREACHED > PASS. A run whose gates are all PASS except some UNDERPOWERED reads
INCONCLUSIVE, naming them. That is not a FAIL that sends the table back; it asks for
more cells or launches. All constants in this section are rows EP01-EP06 of §3.0a, CHOSEN, labelled, and pinned in `prereg.tsv`.

### 3.1 Gate bars

Each bar is evaluated per layer (SIMD-off, SIMD-on) × per SHIPPED filter, on J1-open ∪
J2a (non-contaminated) pooled, and separately on J1-sealed at the final reading (§2.8),
over STREAMED or ≥ 1 MiB RT cells only (§2.4), with cross-fit regret (§1.3). Partial
cells are handled as in §2.6. Every figure is also printed per population (J1-open,
J1-sealed, J2a), per corpus class and as pattern medians (`[r1 M-also]`, §6.1).

- R17-b′ ships S0, and S1 where E arrives.
- R17-b″ ships S2 and S3.

Notation: RT(r) = the RT cells of regime r for this layer × filter; D(P) = the cells
where the table's pick and policy P's differ; R_T(S), R_P(S) = summed cross-fit regret
of the table and of P over S; W, W_exCB, N as in §2.7 and §3.0.

| bar | formula (all in walk-cost units or counts) | constants |
|---|---|---|
| **G0 population floor** `[r1 I-5]` | each layer × regime × filter has `n_RT ≥ EP07` cells from `≥ EP08` patterns, else every gate reads UNREACHED there (never PASS). WEIGHT: the RT share of the blinded J1 patterns (§2.3) must be `≥ w_min` (EP09); below it, every PASS reads LOW-WEIGHT PASS and the coverage finding leads the summary | EP07, EP08, EP09 |
| **G1 aggregate dominance** | for every fixed-form policy P ∈ {always walk, always V1, always A1, always A3 (iter only)}: `R_T(D(P)) − R_P(D(P)) ≤ 2·N(D(P))`, i.e. in walk-cost units `(R_T − R_P)/W(D(P)) ≤ 2·N(D(P))/W(D(P))` (the 2 is EP01). Power floor §3.0 | EP01 |
| **G2 regime caps** `[r1 M-1]` | for each regime r: `R_T(RT(r)) / W_exCB(r) − 2·N(RT(r))/W_exCB(r) ≤ cap(r)`, where the numerator includes CB cells' regret (§2.7). `cap(r) = EP10·R_in(r) + EP11` points for DINGHY and TUG, `cap(LINER) = EP12·R_in(LINER) + EP13` points (`[r2.3]` EP13 = 2, RULED, Q-REVAL-16; it was 1, and the power arithmetic of §2.4 is why), and `R_in(r)` is the STREAMED IN-SAMPLE figure: the same formula's left-hand term computed by E4b on grid2's streamed fit cells (PICKABLE population, §2.1), with this rev's CB rule. Power floor §3.0. Printed beside it, ungated: the rep64k cap check (the same formula on the `rep64k` column against the `fit-repeated` §8 figures) | EP10-EP13; R_in = EP14 (from grid2) |
| **G3 outlier budget** `[r1 M-2]` | a cell is an OUTLIER iff, PER PASS, `ns_pick − ns_walk > max(F, EP17·ns_walk)`, or, for `first` and `lines` cells only, the same holds PER CALL (lines: per call in each bucket). `F = EP15·w_call`, where `w_call` (EP16) is the active set's walk cost per DINGHY call (≈ 16 ns on Zen 4, so F ≈ 50 ns; on another box the set's own value). Then: (a) outliers ≤ EP18 of non-CB RT cells; (b) `Σ_outliers (ns_pick − ns_walk) ≤ EP19 · max(0, Σ_RT (ns_walk − ns_pick))`. When the table's summed saving over the walk is ≤ 0, (b)'s budget is 0, so ANY outlier fails (b). Power floor §3.0 | EP15-EP19 |
| **G4 evaluator validity** `[r1 I-2]` | every SCORABLE control in §4.1 reads WORSE under §4.2 (on the judge population where reached and powered, else on WITNESS cells); C7 and C8 read as §4.3 requires; the evaluator's own checks (§5.3, §5.4) pass. UNSCORABLE controls are listed as twin-owned and do not count toward G4 in either direction; G4's line reads "PASS (k of k scorable; u twin-owned)" | as stated |

`[r1 I-9]` **Independence labels.** The G2 caps are IN-SAMPLE plus headroom: they are
not independent of the table's fit, and the summary labels them so. G3's constants and
the power-floor constants are chosen, not derived. **The headline figure is held-out
minus in-sample**: per regime, `R_held(r) − R_in(r)` in walk-cost units, with 2·N, for
J1-open, J1-sealed and J2a separately. A gate PASS is reported under that headline, not
in place of it.

Why these numbers, briefly:

- **G2's headroom.** "Loose" means a held-out population a little worse than the fit
  still passes. Rev 1's caps were the `fit-repeated` §8 figures plus headroom. A streamed
  walk is slower where the predictor was trained, so "% of walk" shrinks and the caps
  would pass by construction (M-1: F-4's SIMD-on DINGHY loss of 11-14% already sat
  inside rev 1's 15%). The caps are now the STREAMED in-sample figure times EP10 plus EP11 points, which reproduces rev 1's spacing on the repeated numbers (e.g. SIMD-off DINGHY:
  1.25·20.2 + 2 = 27.3 against rev 1's 25) without fixing a number before grid2 reads.
- **LINER is tight on purpose.** It is where the table's default lives, and a LINER regret more than EP13 points above in-sample would mean the default is wrong (`[r2.3]` EP13 is 2 points after Q-REVAL-16, from 1; the power arithmetic is in §2.4).
- **SIMD-off TUG is wide on purpose.** Frank ruled LINER (V1) as the default with no
  data. gridread §6.2 shows always-V1 regrets 16.6% in TUG in-sample, and the ruling
  rests on X2 ("real text leans LINER"). The cap is not where that bet is judged;
  prediction X2 below judges it.
- **G3's floor** is three DINGHY calls of the set's own walk. It catches a per-call
  disaster on `first`/`lines` cells, where one call is the pass. Per pass on a 64 KiB
  or 1 MiB buffer, the 25%-of-walk term dominates: that is what M-2 asked for, since a
  per-call floor loosens as calls per pass grow (10k calls at 40 ns per call excess is
  +400 µs, +150%, and still under a 50 ns per call floor).

A failed gate sends the TABLE back to the kit, unless the slot read SET-MISMATCH
(§2.9). It does not send the forms back. The failure report names the regime and the
row that fired in the cells carrying the excess.

### 3.2 Predictions (reported, never gating)

Each prediction is written down now and reported CONFIRMED / REFUTED / UNREACHED. Every threshold in the table below is a row of §3.0a (EP59-EP63; P-MOVE's shares are EP64); the table there wins `[r2.3]`, and a run that changes one is advisory:

| id | prediction | if refuted |
|---|---|---|
| X2 | On J1 STREAMED, SIMD-off S0's TUG regret (W_exCB) is at most the STREAMED in-sample figure R_in(TUG) from grid2 (real text leans LINER). The `fit-repeated` 16.6% is printed beside it with the `rep64k` column as its like-for-like. A streamed figure ABOVE R_in(TUG) is the refutation | re-open the SIMD-off default (D162 totality is unaffected: WALK becomes the SIMD-off default) |
| P-R1 | R1 picks the walk on at least 80% of J1's `lines` cells with N < 32, and the walk is the best there | R1's crossover moves (kit's note: with landings in the call the crossover passes 32 B) |
| P-R5 | on J1 at S1, R5's per-site g* cuts SIMD-on DINGHY regret vs S0 by at least half | the per-site g* is a grid artifact |
| P-E | the gap between E=exemplar and E=oracle regret is at most 2 points of the walk in every regime | the exemplar is a poor proxy; [REGIME-LANDINGS] carries real landings, or E is not worth shipping |
| P-RT | at least 40% of the blinded patterns are RT (`[r2.2]` written before any reading; §2.3a's no-compile ESTIMATE is 54 of 177, 31%, so REFUTED is expected and E6 confirms or corrects it; the prediction's 40% is not moved) | the regime table covers too little of real use for its cost; widen it (D161 add. 11) before tuning it |
| P-BND `[r1 B-7]` | on bounded cells, P-PRED's walk ratio ns(walk, rep64k) ÷ ns(walk, streamed) is within NULL of 1 (the bounded walk already misses at fresh-text rates when repeated) | the bounded consumer's predictability differs between conditions; the streamed rationale needs a bounded-specific note |

Reported quantities (no bar, no refutation row; the numbers are printed and read by main):

| id | quantity | why it is reported |
|---|---|---|
| P-MOVE | the share of RT cells whose BEST form differs from the walk at all, i.e. some timed arm beats the walk by more than NULL_c (cross-fit), per layer × regime × filter, with and without the CB class. Also the CONCENTRATION: the share of Σ(walk − best) carried by the top 5%, 10% and 25% of cells, the same for the table's realised saving Σ(walk − pick), and the number of patterns with at least one mover cell | Frank wants to see whether the table's value lives in few cells |
| P-PRED | the predictor-training effect: per cell, ns(walk, rep64k) ÷ ns(walk, streamed), the same for each form, and `[D166a1]` OPTIONALLY the walk's misses/KiB in both conditions (the optional perf pass; printed `unavailable` where there are no counters, and nothing reads it). Plus the count of picks that CHANGE between the repeated and the streamed condition. `[r1 B-7]` Expected ≈ 1 on bounded and on hex-run docs, > 1 on dfa-hat and hex-run prose/code | names what the repeated column measures; says whether a streamed re-fit of the `fit-repeated` rows is due (§2.1 trigger) |
| P-CB | the consumer-bound cells (§2.7): count, share of RT cells per layer × regime × site kind, `[D166a1]` the count at the EP22 values (k = 2 and 4) beside the gated k (EP21, 3), labelled with their values, and the optional `cb_perf` agree / disagree / unavailable counts | makes the class visible instead of hiding it in sums |

### 3.3 Scope statements that are part of the bars

- Replay bars exclude dispatch until [REGIME-TWIN] reads (§1.4). After the twin, G1-G3
  are re-run with its term added. Passing without the twin is a PROVISIONAL PASS, and
  the status line says so.
- **`[r1 I-2]` UNSCORABLE by replay, handed to the twin.** The rows R3a, R3b and R4, that
  is every H-keyed row, and the control C2 (the old R3 error, an H-keyed set value) are
  UNSCORABLE: replay prices a per-pass pick, these rows act per step or per block, and
  per-pass H is the wrong quantity (F-5, F-7). In rev 1, C2 already read NOT-WORSE in
  sample, so G4 could not pass. They are excluded from G4, LISTED in `controls.tsv` with
  verdict `UNSCORABLE (twin-owned)`, and never counted as passed. They are gated by the
  twin, by F4 and F7, and by D165's dense-tiny-match parity gate (regime_tables §5).
  The C3 instances for R3a, R3b and R4 are UNSCORABLE for the same reason.
- `iter` cells are emulated by the keep hand-edit until D165 builds. S2 and S3 bars on
  emulated cells are reported but do not gate (Q-REVAL-7).
- Answers are not part of acceptance. Every form is answer-identical. Answer identity
  is the correctness gate (§1.2) and a wrong answer GATE-EXCLUDES a cell (and fails the
  run for a pickable arm).
- **`[r1 M-11]` The rollback trigger.** A PROVISIONAL PASS authorizes R17-b′'s ROUTING
  commit (Q-REVAL-11). It carries a rollback trigger, recorded in the kit's responses
  notice and in main's journal with the PASS: if [REGIME-TWIN]'s dispatch-inclusive
  re-run of G1-G3 reads FAIL, or J2b's official bench run refutes the table on its
  targeted hardware, the kit flips R17-b′'s routing off (its deny becomes the default)
  in the next kit change, as the abi event it is. The PROVISIONAL PASS is not converted
  to PASS until the twin's re-run reads PASS.

### 3.4 Fixing the bars before the reading

- **The pre-registration file.** `docs/design/memfn/regime_eval/prereg.tsv` holds,
  machine-read by the evaluator:
  - **`[r2.3]` `[r2.4 KNOW-SRC]` THE EVALUATOR-PARAMS KIND (§3.0a): the pinned `regime-eval.evaluator-params.tsv` (a copy, or its blob sha) and its stamp item `regime-eval@1:<digest16>`, which IS the prereg hash of the table (it replaces `params_sha256`); plus the `id@rev:digest` of the measurement set the four moved rows (EP14, EP16, EP30, EP58) are read from. Every constant below is a row of one or the other, and the file is hashed with the bars;**
  - every bar and prediction above, as its FORMULA's constants (§3.0-§3.2), plus the
    `R_in(r)` values E4b computed from grid2 and the grid2 log shas they came from
    `[r1 M-1]`;
  - the noise rule (quadrature over groups; the factor is EP01) and every power-floor and G0 constant (EP02-EP09) `[r1 M-3]` `[r1 I-5]`;
  - the cross-fit rule and the rerun rule (+2 launches on an A/A disagreement beyond
    NULL) `[r1 M-5]` `[r1 M-9]`;
  - the population rule (§2.6) including partial-cell handling, and the **STREAMED
    CONDITION**: judge cell is (S) 64 distinct 64 KiB buffers, 4 MiB in all, disjoint
    from the exemplar and FIT buffers, or (W) a whole subject ≥ 1 MiB with the
    byte-range check; a repeated 64 KiB cell is `rep64k` and never gates; the buffer
    count, buffer size and the minimum total size are values in the file;
  - the **consumer-bound definition** (§2.7): `[D166a1]` the three timing conditions, K (EP24), k (EP21) and the denominator rule. The optional corroboration's constants and perf
    event list are recorded only if that pass ran, with a `perf: ran | skipped (paranoid=N)`
    field. No refusal rule reads it, and a prereg with `perf: skipped` is valid;
  - the placement rule (§2.5) and the `lines` bucket edges with the sets they came
    from (§1.3);
  - the frozen pattern list's sha256, `[r1 I-6]` J1b's sha256 (unopened), the corpus
    manifest's sha256, the slice offsets, `[r1 M-6]` `prereg_salt` and the resulting
    J1-sealed list's sha256;
  - the disjointness proof's sha256 (§2.8) and the J2a-contam list;
  - `[r1 B-1]` the bench commit read for J2a, the extracted files' shas, the kit seeds;
  - the foreign-class rotation;
  - the E source per filter;
  - the control list with each control's target regimes and whether it is SCORABLE;
  - the LAUNCHES count and the load-abort rule (EP27, EP28, EP40-EP43);
  - the measurement set id, its sha256, its `box`, and whether the run is a declared C6
    `[r1 M-8]`; the anchor subset and the SET-MISMATCH and drift constants (EP33-EP39);
  - the table listing's sha256 (§5.2);
  - **`[r1 M-11]` the blob shas of `regime_eval.py`, `regime_pick` (source and the
    built binary's sha), the CB classifier, the second parser (§5.3) and the oracle
    cases (§5.4)**, so the evaluator that reads the judge is the one registered.
- **Commit and announce.** It is committed ALONE as `[regime-eval] pre-registration`.
  Its blob sha256 is posted to main in a responses notice. `[r2.3]` The parameter table is part of that blob, so the same sha pins every constant. **`[r1 M-11]` Main's journal
  entry recording that sha is the TIME authority** (committer dates are forgeable), and
  **`[r1 I-6]` main's slot request carries the prereg sha** and is the ORDERING
  authority: a judge slot is requested by main only after its journal records the
  sha. The version is appended to `prereg_versions.tsv` (§2.8).
- **The evaluator's judge mode refuses to run unless all hold:**
  1. `prereg.tsv` at HEAD has the same blob as at the pre-registration commit, and that
     blob sha is the one main's slot request named;
  2. `[r1 M-11]` each judge slot's `SLOT_START` line carries the prereg sha passed in
     main's slot request (the harness writes the line from the request), and main's
     journal entry for that sha exists and precedes the request;
  3. the slot's `arms.tsv` and subject manifest hash to the values the prereg names,
     and every gated group's subject satisfies the streamed condition and the
     disjointness proof;
  4. the table listing and the set it reads match the prereg's hashes, and `[r1 M-8]`
     the set's `box` matches the slot's, unless the run is the declared C6;
  5. `[r1 M-11]` the blob shas of the evaluator's own files and of `regime_pick` match
     the prereg's.
  Any mismatch is a hard refusal that names the field. `[r2.3]` An OVERRIDDEN parameter (§3.0a) is not a prereg mismatch of this kind: the run is not refused, it is ADVISORY and non-gating, labelled "advisory: parameters differ from prereg <hash>" with every differing parameter listed, and `--final` refuses any override.
- **Changing a bar after a reading** means a NEW pre-registration, a NEW judge
  population (J1b after a FAIL, §2.2) and a new slot. Both results are reported side by
  side, and both versions are in `prereg_versions.tsv`.
- **Outliers are LISTED, not excused.** Every G3 outlier appears in the results with
  its cell, regime, the row that fired, pick, best, walk and excess. Any note beside
  one is labelled INTERPRETATION (gridread's convention). An outlier is never removed
  from a sum.

## 4. Failing-direction controls

The evaluator must show it FAILS when the table is wrong. Each control mutates the
table or set through the build's own knobs (§5.2), re-runs the replay on the same cells
and timings (no new timing), and must score VISIBLY WORSE. `[r1 I-4]` One control (C8)
must score exactly NOT-WORSE with zero moved cells, so the evaluator is also shown not
to call every change WORSE.

### 4.1 The controls

| id | control | how expressed (until [MEASURE-SET], all through `regime_pick`, §5.2) | target regimes | scorable by replay? |
|---|---|---|---|---|
| C1 | swapped thresholds: SIMD-on g* ↔ SIMD-off g*; and R1/R2's spans ↔ R3's spans | an alternate set file | all | yes |
| C2 | the old R3 short-span error: A3 for H < 32 (no R3a) | set value `h_r3a = 0` | DINGHY | **NO: UNSCORABLE, twin-owned** `[r1 I-2]` |
| C3 | each row deleted, one at a time, `[r1 B-6]` over regime_tables `[rt0.4]` rev 0.4's rows: R0, R1, R2, R3a, R3b, **R8** (the amended-D2 row, needs P, N, M, A; replay F-2), R4, R5, R6, R7 | a row deny (`--memfn=no-<row>`, created at E3; until then `regime_pick`'s deny list) | the regimes the row fires in | R0, R1, R2, R8, R5, R6, R7: yes (R8 `[rt0.4]` once its condition is a set value; until then listed `pending`). R3a, R3b, R4: **NO, UNSCORABLE, twin-owned** `[r1 I-2]` |
| C4 | R0 removed: V1 on ≥ 2 RANGE terms (C3's R0 instance, named separately because its evidence is the F3 grid) | deny R0 | all (it is P-keyed) | yes |
| C5 | per-site g* replaced by the PF figure (4.5 SIMD-on, 14 SIMD-off for every site kind) | an alternate set file | DINGHY, TUG | yes |
| C6 | the set from the wrong box: Zen 4's set applied to Zen 1's timings, and Zen 1's set applied to Zen 4's | the other box's set file, in a run DECLARED C6 in `prereg.tsv` (the only run where §2.9's box refusal is lifted) `[r1 M-8]` | all (once J4 exists) | yes |
| C7 | A/A, split-half `[r1 I-4]` | the whole replay on odd-round vs even-round medians (§4.3) | must read inside its bound | yes |
| C8 | null mutation `[r1 I-4]` (new) | (a) an ALIAS of the active set: value-identical, new id, different file sha; (b) the deny of a row, applied only to cells where that row's knowledge says it cannot fire (an alias-row deny: e.g. R1 on cells with N ≥ 64) | all | must read NOT-WORSE with exactly 0 moved cells and Δ = 0 |

### 4.2 "Visibly worse", declared now `[r1 I-2]` `[r1 M-3]`

For a control C on a population Π (judge, or WITNESS), let `M_C` be the cells whose pick
C MOVED, and, per regime r, `M_C(r) = M_C ∩ RT(r)`.

- `|M_C| = 0`: **UNREACHED**, never PASS.
- `0 < |M_C| < m_min` (m_min = 5): **UNDERPOWERED**, never PASS. The control is then
  scored on the WITNESS population, whose cells are built to move it (§4.4).
- Otherwise, with cross-fit regrets,
  `Δ_C(S) = Σ_{c∈S} (regret_C(c) − regret_table(c))` and `N(S)` from §3.0:
  - **C3 and C4 (row deletion), PER MOVED CELL SET:** WORSE iff
    `Δ_C(M_C) > 2·N(M_C)`, pooled over every regime the moved cells fall in;
  - **C1, C5, C6 (broad set changes):** WORSE iff `Δ_C(M_C(r)) > 2·N(M_C(r))` in at
    least one target regime r with `|M_C(r)| ≥ m_min`.
- Rev 1's second term, "1.0 point of the regime's summed walk", is DELETED. A row that
  fires on a few cells can never move a regime sum by one point, so C3 passed
  vacuously as NOT-WORSE for every rare row (I-2). Noise only matters where the pick
  changed, and the quadrature rule prices exactly that.
- **Reported per moved cell.** `controls.tsv` has one row per (control, layer, filter,
  regime) with |M|, Δ, N and the verdict, and `controls_cells.tsv` has one row per
  (control, moved cell): the row that fired under the table and under C, both picks, the
  cell's Δ_c and NULL_c, and its regime.

Each control reports one of:

- **WORSE**: the evaluator detects this error;
- **NOT-WORSE where reached**: the evaluator cannot tell this table from the true
  one on this population;
- **UNDERPOWERED** or **UNREACHED**;
- **UNSCORABLE (twin-owned)** (§3.3).

A NOT-WORSE is a G4 failure for C1, C5 and C6 (scorable). For C3 a row deletion that is
NOT-WORSE has a different meaning. Either the row is worth nothing on real use (a
candidate for deletion under Frank's "cleaner, clearer design", Q-REVAL-2), or the
population cannot exercise it. The report says which, by the row's reach count. A row
that fires on fewer than EP65 RT cells reads as "unexercised", not "worthless". For G4,
C3 must read WORSE on the WITNESS population for every scorable row (that is what the
witnesses are for); its judge-population reading is the Q-REVAL-2 evidence.

### 4.3 The A/A controls and the noise rule

- **C7, split-half `[r1 I-4]`.** Rev 1's C7 was "always walk#b" against "always walk",
  scored against a floor built from the same two arms, a tautology. Rev 2 splits each
  launch's 7 rounds into odd (1, 3, 5, 7) and even (2, 4, 6) rounds and runs the WHOLE
  replay on each half independently (cross-fit, NULL and ν from that half). C7 PASSES
  iff (a) for every layer × regime × filter, `|R_T,odd − R_T,even| ≤ 2·N` over the RT
  cells, and (b) the best arm disagrees between halves on at most EP32 of the cells
  whose top two arms differ by more than NULL_c (every such disagreement is listed).
  The halves share no round, so a pass is evidence the regret figure is stable, not a
  restatement of the floor.
- **`walk#c` `[r1 M-5]`.** The independent A/A arm: ν (§1.3) comes from walk vs walk#c,
  which NULL_c's own A/A (walk vs walk#b) never reads. Its per-slot ν and its
  distribution are printed; a slot whose ν exceeds EP31× grid2's ν reads NOISY and is
  flagged like DRIFT (§2.9).
- **C8, the null mutation `[r1 I-4]`.** Both legs must give 0 moved cells and Δ = 0
  exactly (Δ is computed, not assumed). Anything else is an evaluator bug and fails G4.
- **Per-arm A/A `[r1 I-4]`.** Where the harness repeats an arm (an arm#b), NULL_c for a
  difference involving that arm uses its own A/A. The list of arms with their own A/A
  is printed.
- **Winner's curse `[r1 M-5]`.** Rev 1 accepted the upward bias of raw regret (best =
  the minimum over noisy arms, larger with 7 arms than with 2). Rev 2 removes it by
  cross-fitting (§1.3). The raw (non-cross-fit) regret is still printed, and the
  difference between the two is reported as the bias estimate.
- **Per-cell verdicts** (WIN, LOSS or NULL against the walk, listed per cell) use
  gridread's rule: |Δ| ≤ NULL_c, or the paired launch deltas disagree in sign.

### 4.4 Reach of the controls ([MECH-REACH])

Every control's report carries the count of moved cells. The prototype shows the
problem on the fit grid: R0 and R1 are UNREACHED (the grid has no ≥2-range-term site
and no one-shot n < 32 call). The WITNESS population (§2.1) exists for these.

Rule: every SCORABLE row (`[r1 B-6]` `[rt0.4]` over rev 0.4: R0, R1, R2, R8, R5, R6, R7) has at
least m_min = 5 WITNESS cells that the row fires on and where deleting the row changes
the pick. The evaluator checks this with `regime_pick` (§5.2) before any timing, and it
fails closed on a scorable row without them.

`[r1 B-3]` **Exemptions.** The H-keyed rows R3a, R3b and R4 are EXEMPT from the witness
rule: replay cannot score them (§3.3), and the twin is their witness. In rev 1 the rule
failed closed on them, and on the pending row because it had no id. **The amended-D2
row** `[rt0.4]` has its id, **R8** (regime_tables rev 0.4, needs P, N, M, A; Q-REVAL-13
RESOLVED), and enters the rule when its condition (L ≥ ~16-32 B and g ≥ ~4 B) is declared
as set values in the kit's table (E3); until then it is listed as
`pending (no condition)` and is neither a witness failure nor a scored row.

WITNESS cells are timed in the judge slot (J-a3, §2.4) but reported apart. They gate
only G4.

## 5. Independence

### 5.1 Sources, and what each must not share

Everything below follows docs/dev/learnings.md §3 and memory pcrec-check-design-lessons.

| judged thing | judged against | must not share |
|---|---|---|
| the table's pick | the fastest TIMED arm on the cell, cross-fit `[r1 M-5]` | the cost model. The best is never `costmodel.py --price` or gridread's fit. The prototype imports grload's loaders and refuses gridread.py, which holds the fit (§8). It also must not share LAUNCHES with its own selection (cross-fit) |
| `[r1 I-1]` the table's ROW SEMANTICS (order, conditions, boundaries) | the blinded oracle's cases and its prose-row evaluator (§5.4) | the kit's selection function, its source, and its set values' code path. The rev 1 agreement and plant checks compared the kit's one function with itself |
| the thresholds | judge populations the fit never saw | the fit data: thresholds from FIT only; the judge isolation of §2.2; ALPHA/spike non-gating; `[r1 M-6]` J1-sealed read once; J1b after a FAIL |
| the G2 caps | `[r1 M-1]` grid2's STREAMED in-sample replay | **not independent** (in-sample plus headroom), labelled so; the headline is held-out minus in-sample `[r1 I-9]` |
| the patterns | a D27-blinded author | the kit's or pcrec's alphabet: the user agent never sees src/, tests/, the bench patterns or the regime documents |
| the patterns' INTENTS `[r2.2]` | the same author's own disclosure (`rwquest_report.md`) | the injected spawn-time context. The author received the session-root CLAUDE.md, `docs/CLAUDE.md`, `docs/dev/CLAUDE.md` and the LANES INDEX, which describes engine internals (required-byte and required-run pre-checks, start sets, reverse-end walks, `memchr` kernels). Slight priming toward rare-literal and anchor cases cannot be ruled out, and the author says so. MITIGATION: questions are tagged mechanically (`rare-literal`: guessed rare with a literal run ≥ 3; `anchor`: `^`, `$`, `\A`, `\z`; `backref`; `keyword-alt`: ≥ 4 alternatives). That is 63 of 177 questions and 18 of the 54 RT (est). The J1 HEADLINE is printed overall, primed-only and unprimed-only, and a gate PASS that holds only with the primed cells is reported as such. The sealed holdout and J1b stay: J1b is written by a fresh author whose brief carries no lanes index |
| E (the exemplar gap) | the timed slice | the timed bytes: the exemplar is a different file of the same class, checked by chunk hash and byte range (§2.8); the planted E-leak control proves the check fires (§5.3) `[r1 I-7]`. E=oracle is the only exception and never gates |
| the regime bucket | counted facts from the counting twin | timings and the table's own conditions |
| the population | a completeness sum over SIX classes, per timed group `[r1 I-5]` | the evaluator's own filter: K35, every pattern and group listed |
| the evaluator's arithmetic | `[r1 I-7]` a second independent parser (30 random raw cells), the oracle-policy control | the evaluator's own parser and join |
| the evaluator | its failing-direction controls, witnesses, and the null mutation C8 | its own success: §4 |
| a judge failure's cause | `[r1 M-8]` the per-slot FIT anchor replay (§2.9) | the judge cells themselves |

### 5.2 One declared table, read by both

The table the build compiles is the kit's declared row data. D161 add. 11 makes the
kit's copy the source of truth, and regime_tables §0 mirrors it. The evaluator must
judge THAT table, not a transcription.

Design, which adds no parallel mechanism:

- **The pick harness `regime_pick` (kit, tests only).** A small C program linked
  against the kit's own selection function. It reads knowledge records as TSV (one
  per cell × layer × filter, with the filter masking unknown keys) plus a measurement
  set file and an optional deny list (`--memfn=` syntax). It writes `picks.tsv` (§5.5).
  - Python never evaluates a row condition. It only joins picks to timings and does
    arithmetic.
  - The harness is the same code path the compiler runs at define time for {P, E, A, I}
    rows.
  - For {N, M, H} rows it calls the same condition function that the emitted dispatch
    is generated from. The kit table's `needs` column decides which (the kit's D161
    add. 11 notice: "one table, two evaluation times").
- **Controls go through the build's knobs only, and `[r1 B-2]` until [MEASURE-SET],
  through `regime_pick`.** A control is an alternate SET FILE or a ROW DENY. No control
  edits the table.
  - C2 (the old R3) is a set value.
  - C3 and C4 are denies.
  - C1, C5, C6 and C8(a) are set files.
  - **Until [MEASURE-SET] the compiler cannot read a set file** (the `--measures`
    channel is not started), so C1/C5/C6/C8 are applied by `regime_pick` reading the
    alternate set TSV. That is the same selection function on different data, so it is
    still not a second table.
  - **The row denies `--memfn=no-<row>` do not exist yet.** E3 creates them as rows of
    `memfn/src/options.def`, so **E3 owes, in the same commit, the D80 spec hunk for
    the new `--memfn=` options and the raise of the spec-pinned `memfn` section
    member-count floor** (the r15b precedent). Until E3 lands, `regime_pick`'s deny list
    stands in.
  - If a control cannot be expressed this way, that is a finding against the table's
    declaredness, not a reason for a second table.
- **The set's ownership and its interim form `[r1 B-8]`.** pcrec owns the set FORMAT,
  LOADER, STORE and STAMP ([MEASURE-SET], D166); the kit owns the VALUES and the
  METHOD. The kit's interim TSV is labelled as such in its header (§1.1).
  `[rt0.4]` [MEASURE-SET]'s trigger is the kit's E3 commit (the first consumer of a set
  file the compiler must read); main's design lane `msetdes` is in flight on its format.
  When [MEASURE-SET] lands, the kit supplies a converter (`set_to_measures.py`, interim TSV
  → pcrec's format), and the evaluator's advisory pick census (§6.1) between the
  interim-set run and the converted-set run must show ZERO pick movers. Because the set
  file's hash changes, that forces a NEW pre-registration; the judge populations already
  read are unaffected (the picks did not move).
- **The table's identity is recorded.** The evaluator records the sha256 of the kit's
  table LISTING ([LIST-TABLES]: `--list-axes`' `memfn` section, or the kit's own table
  dump), as printed by the binary that built the timed artifacts. The same listing
  hash goes into the pre-registration. A results file whose listing hash differs from
  the artifacts' build is refused.
- **Before R17-b′.** The prototype carries the rows in Python (`replay_proto.py`'s
  `ROWS`), labelled as a mirror of regime_tables rev 0.2. That is exactly the parallel
  mechanism the design forbids. It is allowed only in the prototype, and it expires at
  R17-b′'s first commit (E3, Q-REVAL-11).
- **Sequencing.** R17-b′'s first commit is the table data plus its pick function at
  ZERO MOVERS: not routed, no emitted byte. It precedes the evaluator's build, so the
  harness links real rows from day one.

### 5.3 What the harness proves about itself

Each check below is built so that it can fail.

- **Agreement `[r1 B-3]`.** E3 is unrouted, so an MF_TRACE build of an E3 artifact
  would record no pick. E3 therefore carries a **trace-only SHADOW call** (r4ccore's I1
  implement-then-replace pattern): under the MF_TRACE build only, at define time, the
  kit calls its selection function on each FIND site's knowledge and writes (site, row,
  form) to the trace, emitting ZERO bytes. At E4, on every FIT cell, `regime_pick`'s
  pick must equal the shadow's for that cell's pattern with the cell's P/E/A/I. For
  run-time rows (N, M) the shadow records the condition the dispatch would emit, and
  the check evaluates it at the cell's N. **What agreement proves, and what it does not
  `[r1 I-1]`:** both sides call the kit's one selection function, so agreement checks
  the PLUMBING (knowledge records, set loading, filter masks, the trace join), not the
  table's semantics. A wrong condition (`<` for `<=`) or a wrong row order agrees with
  itself. The table's semantics are checked against the blinded oracle (§5.4).
- **Plants (on the oracle, not on itself) `[r1 I-1]`.** Three plants, applied in a test
  build of the kit's table: (i) a set value off by one (`h_r3a + 1`, and an N-boundary
  `+1`); (ii) one row's comparison flipped (`<` → `<=`); (iii) two adjacent rows
  swapped. Each must make `regime_pick` FAIL at least one oracle case (§5.4). The cases
  were written before the plants, by an author who never saw the code, so the plant is
  checked against an independent expectation. The rev 1 plant ("a planted off-by-one
  must move picks on WITNESS cells") moved both sides of the comparison at once.
- **The second parser `[r1 I-7]`.** A separate script (awk over the raw `time_*.log`,
  sharing no code with `regime_eval.py`'s loaders) re-reads EP66 cells chosen by
  `sha256(prereg_salt || cell_id)` and recomputes, for each, every arm's per-launch
  median ns, the cross-fit regret of the table's pick, ADV/A, ADV/U and the regime.
  Every value must equal `cells.tsv`'s exactly (integers) or to 1e-9 relative (floats).
  This catches a wrong pick→ns join, the wrong cell's ADV/A, or E read from the timed
  slice in the join.
- **The oracle-policy control `[r1 I-7]`.** Two synthetic `picks.tsv` files go through
  the full evaluator: pick = the cross-fit best on every cell must give regret exactly
  0 everywhere (by construction of §1.3, the arm chosen on the other launches is the
  one scored); pick = the slowest timed arm must give the maximum regret, equal to an
  independent computation by the second parser. Either failing is an evaluator bug.
- **The planted E-leak `[r1 I-7]`.** A test run sets the E exemplar of a few cells to
  their own timed slice. The evaluator must REFUSE (`E-LEAK`, naming the cells) from
  the chunk-hash check of §2.8, before any arithmetic.

### 5.4 The blinded pick oracle `[r1 I-1]` (new; a D27 cell task)

The panel's blocker: everything in rev 1 that checked the table's picks compared the
kit's selection function with itself. The fix is an expectation written from the
table's PROSE by an author who never sees the kit's code.

**Who.** A D27-blinded author, created by the kit with `scripts/mk_d27_cell.sh
regoracle` (a worktree plus the allowlist-filtered cell `worktrees/regoracle-cell/`).
The kit's non-blind lanes may triage the author's output but never edit a case.

**What the author receives (the cell's whole allowlist, besides the boilerplate).**

1. `regime_rows_extract.md`, cut by the kit from main's `docs/design/regime_tables.md`
   at rev 0.4 or later (`[rt0.4]` main @ a866eae51 or a later commit, named in the extract's
   header with the file's blob sha). It contains, verbatim: §1 (Shape: one table,
   first-match, knowledge filters, default last); §2's knowledge table (the key
   vocabulary P, N, M, E, H, A, and the filters S0-S3); and §3's row table with the
   **id, needs, condition and pick columns only**. The evidence and "refuted by" columns,
   the regret tables, §4-§6, and every measured number that is not part of a row's
   condition are cut, because they come from the fits.
2. A one-page brief: the case format, the deliverables below, and the rule that every
   threshold the prose gives only approximately (`~14 B`, `g*(site kind)`) is a
   NAMED SYMBOL, not a number.

Nothing else: no `memfn/`, no `src/`, no `tests/`, no set file, no regime_eval.md, no
gridread. The disclosure of the spawn-time injections (session-root CLAUDE.md, the
memory index) stays in the brief.

**What the author delivers.**

1. `oracle_cases.tsv`, about 60 cases. Each case is (case id, filter S0-S3, layer
   SIMD on/off, I where the prose distinguishes S/A forms, a knowledge record whose
   numeric fields are either literals or a NAMED threshold plus an offset, e.g.
   `N = 32`, `N = 31`, `g = gstar(pf) - 1`, `H = L_R3a`; unknown keys marked absent)
   → (expected row id, expected pick). Coverage the author must state and meet: every
   row fired at least once; every condition's boundary at T − 1, T and T + 1 for each
   threshold T; every filter masking at least one key that would otherwise fire a row;
   both layers; the `if emitted` clause of R2; the default row reached under every
   filter.
2. `prose_eval.py`, the author's own small first-match evaluator of the prose rows (a
   second implementation, from the same prose, independent of the kit's code).
3. `NOTES.md`: every ambiguity the prose left (for example "~14", "if emitted", whether
   a boundary is inclusive), how each case resolved it, and which cases depend on the
   resolution.

**How `regime_pick` is checked against it (E4, and on every later table change).**

1. The kit instantiates every named symbol from the ACTIVE set's values (a symbol table
   printed into the results, so a reader sees `gstar(pf) = 4.5` beside the case).
2. `regime_pick` must give the expected row id and pick on EVERY case. A mismatch is a
   finding, triaged as one of: (a) a prose ambiguity (recorded in `NOTES.md`; the prose
   is fixed by main on its mirror and by the kit in its table, the extract is re-cut,
   and the author re-writes the affected cases blind); (b) a kit bug (fixed in the
   kit's table, never by editing the case).
3. `prose_eval.py` must agree with the cases (the author's self-consistency), and with
   `regime_pick` on 100,000 knowledge records sampled uniformly over each field's range,
   boundaries over-sampled. A disagreement is triaged the same way.
4. The three plants of §5.3 must each fail at least one case.
5. The H rows (R3a, R3b, R4) ARE in the oracle: their selection semantics is checkable
   even though their timing is not (§3.3). R8 `[rt0.4]` enters when its condition is declared (its `needs` P, N, M, A put it among the oracle's {P, N, M} rows plus the set key A).

The cases, `prose_eval.py` and the extract's blob sha go into `prereg.tsv` (§3.4).
Main's regime_tables is the source of the prose because it is the joint contract
(regime_tables §0); the kit's table is the thing judged.

### 5.5 The judge interface `[r1 M-unlock]` `[r1 I-unlock]` `[r1 B-unlock]` (new; the interface only)

All three critics converged on the same unlock: make the evaluator's CONTRACT
table-agnostic, so pcrec's own first-match tables (`cand_rows[]`, `fit_rungs[]`, the
reseed rows, `req_admits[]`) could later be judged through the same judge. The
disposition accepts the INTERFACE only.

The evaluator reads exactly two judged-input files, and `regime_pick` is one producer of
the first:

`picks.tsv` (one row per cell × layer × filter, sorted by cell_id, layer, filter):

| column | meaning |
|---|---|
| `cell_id` | the stable cell id of §6.1 |
| `layer` | `off` / `on` |
| `filter` | the knowledge filter (S0-S3 here; any string for another table) |
| `producer` | the producer and its blob sha, e.g. `regime_pick@<sha>` |
| `set_id`, `set_sha` | the measurement set the producer read (empty if none) |
| `row_id` | the row that fired |
| `form_id` | the form it chose; must name an arm of `arm_ns.tsv` |

`arm_ns.tsv` (one row per group × cell × arm × launch × half):

| column | meaning |
|---|---|
| `group_id`, `cell_id`, `layer` | the timed group, the cell, the layer |
| `arm_id` | the harness arm (`walk`, `walk#b`, `walk#c`, `V1`, `A1`, ...) |
| `form_id` | the form the arm renders (`walk#b` → `walk`), for the join with `picks.tsv` |
| `launch`, `half` | the launch index; `all`, `odd` or `even` rounds (C7) |
| `ns_pass`, `calls_per_pass`, `bytes_per_pass` | the per-launch median and the pass's call and byte counts |
| `subj_cond` | `S`, `W`, `rep64k` |

Knowledge records (`knowledge.tsv`) and counts are the PRODUCER's inputs, not the
evaluator's. A control is just another `picks.tsv` (the producer run with a different
set or deny). Regret, NULL, the controls' rule, the gates and the prereg checks read only
these two files plus the regime placement.

**Nothing more general is built (D77).** No table registry, no second producer, no
generic judge command, no plug-in mechanism. The trigger for more: a second first-match
table with a MEASURED threshold that needs a verdict (candidates: the reseed rows,
[PRIOR-COST-UNIFY], [SEL-COST]); at about three such tables the forest-for-the-trees
rule applies. Filed with main (§R.2). `[rt0.4]` The general judge is main's plan row
[TABLE-JUDGE]; this interface (`picks.tsv` + `arm_ns.tsv`) is what it would read.

## 6. Outputs and where they live

### 6.1 Results files

Results are committed under `docs/design/memfn/regime_eval/results/<run-id>/`, where
`<run-id>` = `<date>-<box>-<set-id>-<listing-sha8>`:

| file | contents |
|---|---|
| `manifest.tsv` | the run's inputs, one per row: the prereg blob sha and version, the set id and sha, the listing sha, the corpus manifest sha, the pattern list sha, the disjointness proof's counts `[r1 M-6]`, the bench commit and extracted shas `[r1 B-1]`, the sealed logs' shas, and the sha256 of every slot log read (time_*.log, raw, counts, subj_facts; gridread's SHA256SUMS shape), plus box, gcc, CPU, LAUNCHES, ν per slot and the SLOT_START lines. `--check` re-verifies them. |
| `picks.tsv`, `arm_ns.tsv` | the judge interface (§5.5) |
| `cells.tsv` | one row per (cell, layer, filter), sorted by a stable cell id (pattern id, subject id@sha8, slice, mode, call), with no timestamps in rows. Columns: `cell layer filter population class site_kind terms range_terms regime L g pred E_src I rows_fired pick best ns_pick ns_best ns_walk regret_xfit regret_raw regret_per_call null_cell aa_floor nu launches reruns verdict_vs_walk partial outlier subj_cond cb cb_spread_k mv_best_vs_walk slot_flags`; `[r2.2]` plus `qmode pool eol eol_sensitive shape gap_p10 gap_p50 gap_p90 primed mislabelled` (§2.3, §2.3b, §5.1) |
| `population.tsv` | every frozen pattern and every timed group with its class (REFUSE / NOSITE / OTHER / UNREACHED / GATE-EXCLUDED / RT), reason, per-arm exclusion counts, and site family `[r1 I-5]`. The completeness sums are in the header. |
| `controls.tsv`, `controls_cells.tsv` | one row per (control, layer, filter, regime): moved cells, Δ, N, the verdict (incl. UNSCORABLE, UNDERPOWERED); and one row per (control, moved cell) `[r1 I-2]` |
| `summary.txt` | per layer × filter × regime: table regret, every fixed policy, the gate bars with PASS / FAIL / UNDERPOWERED / UNREACHED and their inputs, the HEADLINE (held-out − in-sample, `[r1 I-9]`), the predictions, the reported quantities, the CB block, every denominator both ways, the with-class G2/G3, the outlier list in full, the slot flags (SET-MISMATCH, DRIFT, NOISY, BREACH), and the status line (PASS / PROVISIONAL PASS (no twin) / INCONCLUSIVE / FAIL, with LOW-WEIGHT where G0's weight floor applies). `[r1 M-also]` Every figure is printed per POPULATION (J1-open, J1-sealed, J2a, J2a-contam, WITNESS), per corpus CLASS and as the PATTERN MEDIAN, not only ns-pooled; and regret is also printed against (walk − EXT consumer ns), the scan-attributable time. `[r2.2]` The coverage line leads: the share of the 177 questions per class (§2.3), and per site family OTHER is split into (`pf_memchr`, MLINE, ...). The J1 headline is printed three ways: overall, primed-only and unprimed-only (§5.1). Every gate figure is also split by `eol` and by `shape`, and the `mislabelled` and `short-pool` cells get their own block. All of these are reported and not gating |
| `oracle.tsv` | the §5.4 cases with the instantiated symbols, `regime_pick`'s answer and the verdict per case; the plant results |
| `checks.txt` | the second parser's 30 cells, the oracle-policy control, the E-leak plant, C7 and C8 |

Everything is plain sorted TSV with fixed column order, so `diff` across runs,
measurement sets or boxes shows only what moved. A companion
`regime_eval.py --diff RUN_A RUN_B` joins `cells.tsv` on the cell id and prints pick
changes and regret moves. **`[r1 B-4]` That is an ADVISORY PICK CENSUS over judge cells,
not D166's mover census.** D166 item 1's mover census is pcrec's: it is emit_sweep-shaped
(emitted artifact bytes over the corpus and the bench, including the emitted N/M/H
dispatch) and pcrec owns it. `--diff` may optionally ingest an emit_sweep run to show
which artifacts' bytes moved beside which picks moved, but it never stands in for it.

### 6.2 What stays out of the tree

These stay in scratch, uncommitted:

- the slot directory and every raw log (their sha256s are in the manifest), including
  `sealed/` until unsealed;
- the corpus BYTES. Licensing: only ids and sha256s are committed, and the bytes live
  in `worktrees/.corpus/`;
- the bench library extract and the J2a subjects (§2.10).

The prototype's outputs, and `rev2_arith_out.txt`, are committed because they are small
and in-sample, and they cite their input files.

## 7. The plan

| step | what | owner | gates on | slot? |
|---|---|---|---|---|
| E0 | this note → main's comments → D6 panel r1 → **rev 2 (this)** → main's comments on rev 2 | kit | — | no |
| E1 | [REGIME-CORPUS] collection report (manifest, PROVENANCE, sha256s) `[r2.2]` DONE on main (rwcorpus) | main | — | no |
| E2 | blinded user-agent lane: questions + patterns per class, frozen list committed, `[r1 I-6]` J1b written and its hash committed unopened. `[r2.2]` Questions DONE (rwquest, 177). **J1b is OWED**: one list was delivered. Its author's brief should carry no lanes index (§5.1) | main | E1 | no |
| E3 | R17-b′ first commit: table data + pick function, zero movers (§5.2). It FIRST retires the Python mirror (Q-REVAL-11). `[r1 B-3]` It carries the trace-only SHADOW call (§5.3) and `[rt0.4]` row R8 with its declared condition. `[r1 B-2]` It creates the row denies `--memfn=no-<row>` WITH their D80 spec hunk and the raised `memfn` member-count floor pin. Main: [MEASURE-SET]'s trigger is E3 `[rt0.4]` (the kit's E3 commit; main's design lane `msetdes` is in flight) | kit | E0 | no |
| E3b `[r1 I-1]` | the blinded pick oracle (§5.4): the kit cuts the extract from main's regime_tables (`[rt0.4]` rev ≥ 0.4), creates the `regoracle` cell, the author delivers cases + `prose_eval.py` + NOTES | kit (cell lane) | E0 (runs beside E3) | no |
| E4 | evaluator build: `[D166a1.1]` the counter-unavailable SUGGESTION in `slot.sh`/`time.sh`/`f2perf.sh` (§1.2) with its check (text appears when the probe fails; skip reaches the provenance; no `sysctl`/`sudo` in the scripts), `regime_pick`, `regime_eval.py` (replay with cross-fit, controls with the moved-cell rule, judge gate, the advisory census, `--check`), harness H1 (`lines`, four buckets) and the streamed-subject generator (§2.4), the CB classifier on K and the P-MOVE/P-PRED/P-CB reports (§2.7, §3.2), WITNESS cells, `walk#c` and the rerun rule in the harness, the anchor replay and drift check (§2.9), the disjointness proof (§2.8), the bench-library extract script (§2.10), the second parser and the self-checks (§5.3). Validated IN-SAMPLE on grid1 (must reproduce the prototype within the same arithmetic) with every control, the agreement check, the oracle cases and the plants | kit | E3, E3b | no |
| E4b `[r1 M-1]` | in-sample STREAMED replay on zen4-grid2's fit cells: `R_in(r)` per layer × regime × filter, the CB re-read on streamed data from grid2's timing (§2.7), the anchor subset and its set values (§2.9), grid2's ν | kit | E4 and zen4-grid2's logs | no (grid2 is the kit's own slot) |
| E5 | pre-registration commit (with `R_in`, the oracle and evaluator shas, J1-sealed's list, the bench commit) + hash posted to main; main's journal records it | kit, main | E2, E4b | no |
| E6 | site-mapping census (no clock), counting pass, correctness gate on J1 + J2a + WITNESS; the disjointness proof; population.tsv. `[r2.2]` It also prints its class counts beside §2.3a's ESTIMATE, question by question, so the estimate's misses are visible (e.g. a literal-led pattern pcrec routes to a set FIND) | kit | E5 | light (no clock; ~15 min, -j) |
| E7 | `[r2.3]` THE PLAN (lean, RULED Q-REVAL-12): windows W1 and W2 on Zen 4 (§2.4), every cell streamed or ≥ 1 MiB, with the anchor replay in W1, drift anchors in W2, the OPTIONAL perf pass (`[D166a1]`) and the drift checks; main's slot request carries the prereg sha. DOCUMENTED ALTERNATIVE ONLY, not scheduled: rev 2.1's judge slots J-a1, J-a2, J-a3, J-a4, J-b (J-c optional, ungated, not scheduled) | kit, scheduled by main | E6 | YES. LEAN: ~69 + ~62 min (~131 min). ALTERNATIVE on the real population: ~309 min in five slots (rev 2.1's own figure, at the assumed 70 patterns: ~407 required, ~431 with optional perf) |
| E8 | replay of J1-open + J2a → results committed → summary to main | kit | E7 | no |
| E9 | D6 panel on the RESULTS (rows, outliers, controls, predictions) | kit launches, main comments | E8 | no |
| E10 | [REGIME-TWIN]: the hand-built table arm timed against fixed forms and the per-row best on FIT + a J-a1 subset; dispatch term as a set value; bars re-run with dispatch; the UNSCORABLE rows and C2 scored | kit | E8 (design with E0) | YES: one grid slot, ~60 min |
| E10b `[r1 M-6]` | the FINAL reading: J1-sealed unsealed once (main's UNSEAL line), the bars re-run on it with the twin's term | kit, main | E10 | no |
| E11 | F5: J4 on ubuntubudu via a bench request through main; the Zen 1 set; C6 | main schedules the bench box | E8 | bench window |
| E12 | R17-b″ evidence: F4/F7 through D165's iterator; S2/S3 bars become gating | kit + pcrec | D165 build | YES |
| E13 `[r1 B-8]` | when [REGIME-LANDINGS] lands: an agreement check between the surrogate `E=exemplar-bigram(kit)` and `E=analysis(landings)` on the FIT and J1 exemplars (the distribution of the g difference and the pick changes it causes), then a FRESH S1/S3 pre-registration (new version, J1b or a new population for the S1/S3 rows) | kit | [REGIME-LANDINGS] | light |
| E14 `[r1 B-8]` | when [MEASURE-SET] lands: the converter, the zero-mover advisory census between the interim and converted sets, and a new pre-registration (the set hash moved) | kit | [MEASURE-SET] | no |

The [REGIME] umbrella's official verdict (D144 add. 4) remains the bench run on
targeted hardware (J2b). This evaluator is the kit-tier gate before it.

Slots needed, via main: zen4-grid2 (the kit's own next grid slot, now carrying §2.1's
owed cells), E6 (light), E7 (five; `[r2.2]` lean: TWO windows), E10 (one), E11 (a bench window).

What [REGIME-TWIN] adds:

- the dispatch term (per row set and site kind);
- the only score for R3a, R3b, R4 and C2 (`[r1 I-2]`);
- code-size movement per artifact (pcrec's observable, `artifact_size_log`), which
  replay cannot see;
- the conversion of PROVISIONAL PASS into PASS, and the rollback trigger's test
  (`[r1 M-11]`).

## 8. The prototype: what the replay already shows (in sample)

`regime_eval/replay_proto.py` on grid1's slot (inputs sha-matched to
`gridread/SHA256SUMS`). It imports grload's loaders only. Its knowledge records come
from planted facts plus the `site(G1)` counters. `[r1 B-6]` Its rows are regime_tables
**rev 0.2's conditions** (with the kit's rev 0.1 corrections), held in Python as a
labelled mirror (§5.2). Rev 0.3 (main @ aad0199d9) did not change any replayed
condition: it relabelled the S1-off/S2/S3 regret figures as model policies, marked
R3a/R3b PROVISIONAL and R3b SIMD-on only (as the prototype already reads it, F-3), and
added the pending amended-D2 row, which has no declared condition and is not replayed.
`[rt0.4]` Rev 0.4 (main @ a866eae51) names that row **R8** (needs P, N, M, A; cites F-2)
and changes no other row; the prototype still does not replay it (E4 does, once the kit's
table declares its condition).
The figures below are therefore unchanged, and are rev 1's cross-launch medians, not
rev 2's cross-fit regret (E4 re-derives them both ways).

| filter, layer | STRICT population (101 groups) | regime_tables §3 claims | PICKABLE population (132 / 109) |
|---|---|---|---|
| S0 SIMD-on | 11.1 / 1.2 / 0.0 | 11.1 / 1.2 / 0.0 | 13.7 / 1.3 / 0.0 |
| S0 SIMD-off | 18.8 / 16.6 / 0.1 | 18.8 / 16.6 / 0.1 | 20.2 / 16.2 / 0.1 |
| S1 SIMD-on | 5.6 / 0.1 / 0.0 | 6.6 / 0.1 / 0.0 | 8.9 / 0.1 / 0.0 |
| S1 SIMD-off | 3.5 / 2.1 / 0.1 | 2.7 / 0.4 / 0.1 | 6.3 / 2.0 / 0.1 |
| S2 SIMD-on (iter) | 6.0 / 1.2 / 0.0 | 5.6 / 1.2 / 0.0 | 4.9 / 1.3 / 0.0 |
| S2 SIMD-off (iter) | 10.5 / 16.6 / 1.0 | — | 8.3 / 16.2 / 0.9 |
| S3 SIMD-on (iter) | 6.0 / 0.1 / 0.0 | 0.5 / 0.1 / 0.1 | 4.9 / 0.1 / 0.0 |
| S3 SIMD-off (iter) | 3.5 / 2.1 / 1.0 | 1.5 / 0.4 / 0.1 | 2.8 / 2.0 / 0.9 |

All values are DINGHY / TUG / LINER regret as % of the walk.

Controls on STRICT (`proto_out_strict.txt`), under rev 1's rules:

- C1 swapped g*: WORSE in all three configurations.
- C5 PF-only g*: WORSE in both.
- C3: deleting R3a or R6 is WORSE; deleting R5 is WORSE at S1 and NOT-WORSE at S3.
  Deleting R2 is NOT-WORSE (|Δ| ≈ 0 on 2-4 moved cells). Deleting R3b is NOT-WORSE,
  and its Δ is negative: −5.2 µs at S2 and −39.9 µs at S3. `[r1 I-2]` Under rev 2, R3a
  and R3b are UNSCORABLE (their C3 rows read twin-owned), and R2's 2-4 moved cells are
  UNDERPOWERED (< m_min), so it goes to its WITNESS cells.
- R0 and R1 are UNREACHED.
- C2, the old R3, is NOT-WORSE: −6.0 µs on STRICT; +35.1 µs on PICKABLE, under the
  moved-cell threshold. `[r1 I-2]` Under rev 2, UNSCORABLE (twin-owned).
- C7 (A/A, rev 1's form): 1.25% of the walk. Rev 2's split-half C7 is built at E4.

Findings (MEASURED replay arithmetic over the slot's timings; interpretations labelled):

- **F-1.** The evaluator's arithmetic reproduces regime_tables §3's S0 row exactly on
  gridread's own population. The replay and the source agree where they should, so
  the instrument starts calibrated.
- **F-2.** The S1-SIMD-off, S2-SIMD-on and S3 figures in regime_tables §3 are not what
  the declared ROWS achieve. They are gridread §6.2's model rows ("gap", "hint",
  "gap+span" with oracle facts). The rows regret S3 SIMD-on DINGHY 6.0% against the
  claimed 0.5%. INTERPRETATION: the rows have no DINGHY row for "L ≥ ~16-32 and
  g ≥ ~4 → W=64" (gridread §6.3 D2's amended rule), and R4 is not replayable. This is
  why the evaluator replays rows and never quotes a model. (`[r1 B-6]` regime_tables
  rev 0.3's pending row cites this as "replay F-1"; it is F-2. Relayed, §R.2.)
- **F-3.** S2 SIMD-off regrets 10.5% in DINGHY against always-walk's 2.4%: the table
  loses to a fixed form, a G1 failure. R3b's condition requires SIMD-on, so a span of
  14-32 B with SIMD off falls through to R7's V1. INTERPRETATION: R3 needs a SIMD-off
  arm (WALK, by rule D1) or a statement that S2 is SIMD-on only (rev 0.3 took the
  latter).
- **F-4.** With no iterator, SIMD-on DINGHY regret (11.1-13.7%) is worse than
  always-walk (7.2-9.1%). This is regime_tables' own note: find-all through `_search`
  makes N the remaining subject, so DINGHY is invisible at call time. G1 is aggregate
  and the table still dominates overall (LINER), which is why G2 caps DINGHY
  separately and loosely.
- **F-5.** The population rule decides C2. STRICT drops the L = 8 groups the kit's
  R3 correction rests on, and C2 there reads −6.0 µs (the old row looks better).
  PICKABLE keeps them and C2 reads +35.1 µs, but under the moved-cell noise threshold.
  The R3 correction is therefore NOT visibly supported by the replay of this grid.
  INTERPRETATION: H here is the per-pass mean activation span, and R3 is a per-step
  row; per-step H needs the iterator (F4) or [REGIME-TWIN]. (`[r1 I-2]` This is why
  rev 2 declares the H rows and C2 UNSCORABLE by replay.)
- **F-6.** R0 and R1 are unreachable on the fit grid (no ≥2-range-term F1 cell; no
  one-shot n < 32 call), hence the WITNESS population (§2.1, §4.4).
- **F-7.** Deleting R3b IMPROVES in-sample regret (−39.9 µs at S3). INTERPRETATION:
  A3 at activation spans 14-32 B loses to R7's A1 on these cells. This conflicts with
  gridread §4.2's L* 14-19 B, which is a per-call-span crossover at fixed g, again
  the per-step vs per-pass H gap.
- **F-8.** The TUG A/A floor (38 µs) is dominated by the walk's bimodality (gridread
  §1.1). A regime-summed noise rule hides real controls there. §4.2's moved-cell rule
  is the fix, now with quadrature (§3.0).

None of these is a judge result. They are statements about the table against its own
fit data, which is the evaluator's first job (E4 must reproduce them). The §8 figures
are `fit-repeated` (§2.1) and WITH the consumer-bound class; `[r1 M-1]` the caps no
longer derive from them (E4b derives `R_in` from grid2's streamed cells), and they stay
the like-for-like reference for the `rep64k` column and its cap check.

**Disposition of regime_tables corrections 1-4** (the kit's notice of 2026-10-14 asked
for them; each below is the finding behind F-2, F-3, F-5/F-7 and F-6). All four are in
regime_tables rev 0.3 (main @ aad0199d9):

1. S1-off / S2 / S3 figures are gridread's model rows, not the declared rows: accepted;
   applied by main on its mirror.
2. R3b has no SIMD-off arm (F-3): accepted; applied by main on its mirror.
3. The R3a/R3b split is not supported by the grid's per-pass H (F-5, F-7): accepted;
   applied by main on its mirror (R3a/R3b PROVISIONAL until per-step H exists).
4. R0 and R1 are unreachable on the fit grid (F-6): accepted; applied by main on its
   mirror (the WITNESS cells of §2.1, §4.4 carry the reach).

## 9. Questions — resolved (main and Frank, 2026-10-14)

Main accepted all of Q-REVAL-1..11 as recommended, with the riders below.

- **Q-REVAL-1, the bar values (§3.1): RULED, adopt as proposed, with the streamed
  condition.** The values are loose by design. LINER is the only tight cap, and it is
  tight because the default lives there. The bars apply only to STREAMED or ≥ 1 MiB
  cells (§2.4), and G2/G3 gate without the consumer-bound class (§2.7).
- **Q-REVAL-2, may a held-out row deletion argue for removing the row?: RULED yes, but
  a deletion becomes a PROPOSAL to Frank.** When C3 reads NOT-WORSE on the judge
  population AND the row fires on at least EP65 RT cells, the report files a per-row
  proposal to Frank under "cleaner design". It is never automatic and never a kit
  decision. On the fit grid this already names R2 (|Δ| ≈ 0) and R3b (negative Δ) for a
  look.
- **Q-REVAL-3, E before [REGIME-LANDINGS]: RULED as recommended, exemplar-bigram,
  labelled, until [REGIME-LANDINGS].** The evaluator derives g from a same-class
  EXEMPLAR through pcrec-analyze's unigram and bigram counts, labelled
  `E=exemplar-bigram(kit)`, and also reports E=oracle. Every figure that uses it carries
  the label until [REGIME-LANDINGS] delivers the analysis object's landings kind.
- **Q-REVAL-4, harness extension H1 (`lines`): RULED as recommended.** A manifest
  generator in the grid1 harness, no driver change. It is the only shape where N at
  call entry is small on real text, so it is the only place R1 and R2 are judged on use.
- **Q-REVAL-5, ALPHA and spike cells (J3): RULED as recommended.** Reported, never
  gating.
- **Q-REVAL-6, J2a: RULED yes, published definitions only.** The bench's published
  patterns and subjects, timed at the kit tier. The evaluator never reads the ledgers,
  and bench-only questions go to main for relay.
- **Q-REVAL-7, emulated iterator cells: RULED as recommended.** S2 and S3 on keep-edit
  cells are reported and do not gate until F4 measures the real iterator.
- **Q-REVAL-8, LAUNCHES for judge slots: RULED as recommended.** 3 for J-a1, J-a2, J-b
  (and J-c if run), with gridread's paired-sign rule; 5 for WITNESS cells. The estimate
  of §2.4 uses 3.
- **Q-REVAL-9, the reporting buckets: RULED as recommended.** costmodel's (64, 18.5) as
  the gated buckets; gridread's W=64 boundaries as an ungated second column.
- **Q-REVAL-10, the measurement set before [MEASURE-SET]: RULED as recommended.** The
  kit writes its set as a TSV in D166's shape (relative to the walk's per-byte cost,
  absolute ns as provenance, id, box, run, method version and, new in rev 1, the
  subject condition per row, §2.1), replaced by pcrec's format when [MEASURE-SET] lands.
- **Q-REVAL-11, order relative to R17-b′: RULED as recommended, with the E3 zero-mover
  table first, which retires the Python mirror.** E3 (the table data plus its pick
  function at zero movers) comes first and retires `replay_proto.py`'s `ROWS` mirror
  (§5.2); then the evaluator (E4), then the judge (E7), then R17-b′'s ROUTING commit
  only after a PASS or PROVISIONAL PASS.

- **Q-REVAL-12, the judge plan: RULED (Frank, 2026-10-14, via the pcrec manager): the
  LEAN plan.** About 131 min in two quiet-box windows (~69 + ~62), plus grid2's ~56
  separately, and ~39 min of the two-window envelope held as the BREACH-resume margin
  (§2.4). It is THE plan (§0, §2.4, §7 E7). Rev 2.1's plan (~309 min on the real
  population, five slots) is a documented alternative only: it becomes the plan only on a
  new ruling. The three add-backs (W16 arm, J1 `all`/W, `iter`/S) stay available inside the
  margin on Frank's word, and none is in the plan. `lines`, `walk#c` and the rerun budget
  are kept.
- **Q-REVAL-16, the chosen constants: RULED (Frank, 2026-10-14): rev 2's constants plus
  BOTH loosenings.** The constants are the rows of §3.0a with provenance "list RULED by
  Frank 2026-10-14 (Q-REVAL-16)". The loosenings: (1) the LINER cap is R_in + 2 points
  (EP13, was +1); (2) at the final reading, a sealed regime below G0 is judged on the
  pooled population, labelled, with its sealed-only figure beside it (EP46). The
  power arithmetic that justified them is in §2.4.
- **Q-REVAL-17, the consumer-bound tolerance: RULED (Frank, 2026-10-14): k = 3, WITH A
  CONDITION.** Frank: "q-reval-17 is a configuration lever that shouldn't be hidden." So k
  is a DECLARED, VISIBLE parameter (EP21), not a constant in a script:
  - named in the prereg bars file (the pinned evaluator-params file and its digest, §3.0a, §3.4);
  - printed in every report beside the k = 2 and k = 4 counts (EP22; the header block, the
    CB block, P-CB);
  - overridable by option (`--cb-k=`), an overridden run being advisory (§3.0a);
  - listed with its provenance: chosen (not fitted), RULED, and re-read on grid2's
    streamed data before E5 (§2.7).

  Frank extended the condition to EVERY chosen constant that can change a verdict, which
  is §3.0a: the noise factor, m_min, G0's floors, the power fractions, the cap formula's
  multipliers and additions, G3's constants, the partial-cell cap, the SET-MISMATCH and
  drift thresholds, the rerun budget, the sealed share, ν, the subject-window sizes and
  floors, k, and the rest.

### 9.1 The standing design questions (docs/design/CLAUDE.md)

1. **Measurement regime: RELEVANT.**
   - Every judge timing is Zen 4 7700X, CPU 14, governor `performance`, gcc 15.2
     -O2, kit tier, unofficial (D144 add. 4), under the quiet gate, with `first`,
     find-all, `lines` and emulated-iterator call patterns.
   - Real text differs from the grid in landing predictability, and that moves g*
     2-4× (gridread §5.3). The judge populations exist to see exactly that.
   - `[r2.2]` The real corpus adds three regime facts, each a label rather than a gate:
     - line endings: every prose and non-English file is CRLF, and so are two log files,
       and N in a `lines` call counts the CR;
     - the subject shapes `periodic-200`, `nul-padded` and `compressed`, which make a
       mean g mislead, so gap quantiles are printed;
     - sorted or concatenated files, which make head samples mislead, so windows are
       stratified across the whole pool (§2.3b, §2.4).
     A plan cut changes power, never the regime of a cell (§2.4's ladder).
   - The SUBJECT CONDITION flips the walk's cost on some cells: `[r1 B-7]` on a
     repeated 64 KiB buffer the walk misses 0.4-0.9 per KiB on dfa-hat and 4.7-22 on
     hex-run prose/code, against 145-251 on fresh 1 MiB in every cell; bounded and
     hex-run docs already miss at fresh-text rates when repeated (F2). That is why every
     judge cell is streamed or ≥ 1 MiB (§2.4), the repeated column is ungated, the F1/F3
     constants are labelled `fit-repeated` (§2.1), and `[r1 M-1]` the caps' in-sample
     reference is STREAMED (grid2).
   - Neither streamed condition is DRAM-bound (§2.4) `[r1 M-also]`.
   - `[D166a1]` A TIE across the fixed arm set K in TIME (spread ≤ 3·NULL_c, walk and
     pick within NULL_c of the best) marks a consumer-bound / tie cell (§2.7). It is a
     counted class that leaves only the denominators. Branch misses are an optional,
     ungated corroboration, never a requirement.
   - Zen 1 (AVX2 as 2×128) is expected to move every W=64 row. J4 and C6 measure it,
     with ν and NULL re-derived on that box `[r1 B-9]` and a per-slot anchor replay
     against the set (§2.9).
   - Dispatch is unmeasured by replay. [REGIME-TWIN] supplies it, and passes before
     it are PROVISIONAL.
   - A different call pattern (an iterator against `_search` find-all) flips DINGHY
     picks. M is a knowledge key, and the emulated cells do not gate.
2. **Independent control: RELEVANT.** §5.1's table:
   - the best comes from timed arms, never the model, cross-fit so choosing and scoring
     never share a launch;
   - `[r1 I-1]` the table's row semantics are checked against a blinded author's
     cases and second evaluator, not against the kit's own function;
   - thresholds come from FIT only, the judge is held out and pre-registered, ~30% is
     sealed to the final reading, and J1b waits for a FAIL;
   - the G2 caps are in-sample and labelled not independent; the headline is
     held-out minus in-sample;
   - patterns come from a D27-blinded author;
   - E comes from a different file than the timed one, proved by chunk hash, with a
     planted leak that the check must catch;
   - the population is counted to completeness over six classes per timed group (K35);
   - every scorable control is failing-direction, with witnesses that reach their rows
     ([MECH-REACH]), and C8 shows the evaluator can read NOT-WORSE; the unscorable ones
     are named and handed to the twin;
   - the evaluator's arithmetic is re-read by a second parser and an oracle-policy
     control;
   - the table under test is the built table, through its own pick function and
     knobs, with its listing hash recorded;
   - `[r2.2]` the blinded author's spawn-time disclosure is a §5.1 row. The headline is
     printed primed-only and unprimed-only. §2.3a's placement is an ESTIMATE that E6
     replaces, and E6 prints both side by side, so the estimate cannot stand in for the
     census;
   - the consumer-bound criterion is measured `[D166a1]` from TIMING alone (walk − best,
     the K spread in NULL units, the pick's loss), with the chosen k labelled and the
     F2 gap that bounds it shown (§2.7); perf misses are an optional, ungated
     corroboration, and no control, bar or refusal needs counters.
3. **What moves when the data is regenerated: RELEVANT, NO pcrec byte.**
   - The evaluator is analysis. A new measurement set or a re-fit grid changes picks
     and therefore regret. The results are versioned by (set id, listing sha,
     population sha). `[r1 B-4]` `--diff` is an ADVISORY pick census over judge cells;
     D166's mover census (artifact bytes) is pcrec's and is emit_sweep-shaped.
   - Re-fitting a threshold the judge has already read contaminates that judge
     population for that row (§2.2).
   - Changing `prereg.tsv` after a reading invalidates the judge run (§3.4), and the
     version list records it.
   - `[r1 B-8]` Converting the interim set to [MEASURE-SET]'s format moves no pick
     (checked by the census) but moves the set hash, so it forces a new
     pre-registration.
   - No abi event, no stamp, no spec hunk from the evaluator: nothing here is
     caller-observable. `[r1 B-2]` E3's row denies ARE caller-visible `--memfn=`
     options, so E3 carries their D80 hunk and the floor pin; that is E3's, not the
     evaluator's.
   - `[r2.2]` A new corpus manifest version (re-fetched mislabelled files, a volatile USGS
     row) or a new question list moves pools, windows, exemplars and the frozen pattern
     hash. That is a new pre-registration and never an edit of a running one. The window
     rule is a function of the manifest and `prereg_salt` only, so the same inputs redraw
     the same windows byte for byte.
   - The table itself, when routed (R17-b′), is the kit's abi event, not this
     evaluator's.

### 9.2 Open questions (new in rev 2), with recommendations

- **Q-REVAL-12, the judge plan: RESOLVED `[r2.3]`** (Frank, 2026-10-14: the LEAN plan; §9). The rev 2.2 discussion (problem, forces, leaning) is in that revision's git history.
- **Q-REVAL-13, the pending amended-D2 row's id: RESOLVED `[rt0.4]`.** Rev 2
  recommended the kit name it `RD2`; regime_tables rev 0.4 (main @ a866eae51) names it
  **R8** (needs P, N, M, A; cites replay F-2). The kit's table uses R8. The row carries
  its declared condition (L ≥ ~16-32 B and g ≥ ~4 B, the thresholds as set values) at
  E3; until then it is listed `pending` and neither scored nor a witness failure.
- **Q-REVAL-14, key A vs ISA (relayed, B-5): RESOLVED `[rt0.4]`.** Rev 2
  recommended splitting A into A = the measurement set id (D166 item 3) and I = the ISA
  level, the tuning class a property of the SET (its box), not a key. Regime_tables rev
  0.4 adopts exactly that: A = the set id, I = ISA availability (SSE2/AVX2/AVX-512/NEON),
  two separate keys. This note's ISA field is key I (§1.1).
- **Q-REVAL-15, J2a subjects (for the bench dev, via main; B-1).** `[r2.2]` RELAYED as
  I-152, no answer yet. Three questions:
  (a) may the kit import `boundedtext.py` and `logtext.py` from a `git archive` extract
  of a pinned bench commit, with kit seeds and kit output dirs (§2.10)? (b) may it do
  the same with `captext.py`, `censustext.py` and `utf8text.py` (the last opens a data
  file, which would need to be in the extract)? (c) for condition W, may the kit
  reproduce the bench's existing ≥ 1 MiB throughput subjects by calling each
  generator's pure `build()` from an extract (no `main()`), verified byte for byte
  against the committed manifest, or would the bench dev rather provide the bytes?
  ~~Recommendation: ask all three; proceed with (a) only until answered, counting the
  rest as J2a-NOSUBJECT.~~ `[r2.2]` Until the bench answers, the DEFAULT is (c)'s second
  half: main arranges a byte transfer of the 11 subjects, each sha-checked against the
  bench manifest at a pinned commit (§2.10). A yes to (a) or (b) makes the import route
  available as the alternative. It adds (S) subjects for bounded and loglines and changes
  no gate's power.
- **Q-REVAL-16, the chosen constants: RESOLVED `[r2.3]`** (Frank, 2026-10-14: rev 2's constants plus both loosenings; §9, §3.0a).
- **Q-REVAL-17, the consumer-bound tolerance k: RESOLVED `[r2.3]`** (Frank, 2026-10-14: k = 3, as a declared visible parameter; §9, §3.0a EP21/EP22, §2.7).

## 10. Charter vs committed

| charter item | committed |
|---|---|
| 1. Replay inputs (cell; knowledge P/N/M/E/H/A under S0-S3; measured ns of every form, both layers) and output (pick, regret, absolute + relative per regime); sources named; the dispatch gap handed to [REGIME-TWIN] | §1.1-§1.4 |
| 2. FIT/JUDGE split (grid1 F1/F3 + future grids → a D166 set; J1 corpus × blinded, J2 bench via main, J3 ALPHA/spike, J4 Zen 1); held-out timing via grid1 over corpus subjects with cell and slot estimates; regime placement from counted L/g; pattern→site mapping with every non-reaching pattern counted (K35) | §2.1-§2.6 (estimate §2.4; mapping and completeness §2.3) |
| 3. Pre-registered loose acceptance per layer and regime; total-regret caps, outlier rule, dominance over fixed forms; committed and hashed before the run; outliers listed | §3.0-§3.4 |
| 4. Failing-direction controls (swapped thresholds, old R3, each row deleted, R0 removed, per-site g* → PF, wrong-box set), "visibly" defined beforehand; A/A control; the noise rule | §4.1-§4.4, §3.0; the prototype runs C1-C5 and C7 (§8) |
| 5. Independence (no shared source; fit vs judge; best from timed arms; one declared table read by both, no parallel mechanism) | §5.1-§5.5 |
| 6. Outputs: per-cell table, per-regime and per-filter summaries, control scores; diffable; committed vs scratch | §6.1-§6.2 |
| 7. The plan: run order, gates, slots via main, what the twin adds | §7 |
| 8. Open questions Q-REVAL-n with recommendations + the standing design questions | §9 (resolved), §9.1, §9.2 (new) |
| Rev 1, item 1: every judge cell streamed or ≥ 1 MiB; repeated 64 KiB only as a labelled UNGATED column naming the predictor-training effect; wall recomputed and fitted; the condition in §2.4 AND in `prereg.tsv`; populations rule and X2 updated | §2.1, §2.4, §2.6, §3.2 (X2, P-PRED), §3.4 |
| Rev 1, item 2: consumer-bound cells as a COUNTED class with a measured, pre-registered criterion; denominators with and without the class | §2.7, §3.1, §3.4, §6.1 |
| Rev 1, item 3: P-MOVE (non-gating) | §3.2 |
| Rev 1, item 4: Q-REVAL-1..11 resolved with main's rulings and riders | §9 |
| Rev 1, item 5: regime_tables corrections 1-4 noted as accepted and applied by main | §8 |
| **Rev 2: every one of the panel's 33 ids applied and marked `[r1 <id>]`, with a by-id map** | §R (and the marks in place) |
| Rev 2, T1: the blinded pick oracle as a D27 cell task (what the author receives, delivers, how `regime_pick` is checked); no cases written by the kit | §5.4, §5.3, §7 (E3b) |
| Rev 2, T2: UNSCORABLE rows and controls listed; the per-moved-cell C3 rule exactly; H rows witness-exempt; pending row id | §3.3, §4.1, §4.2, §4.4, Q-REVAL-13 |
| Rev 2, T4/T5/T6/T9: every bar a stated formula in walk-cost units with its noise rule (quadrature, justified against a bootstrap), power floor and the sealed holdout; caps from a STREAMED in-sample replay in zen4-grid2, E5 waits | §3.0, §3.1, §2.8, §2.1, §7 (E4b, E5) |
| Rev 2, T7: §2.7 with condition 3b, the denominator-only rule, the spread over walk + common arms; the F2 streamed pass in grid2's owed list; B-7's corrected F2 numbers | §2.7, §2.1, §2.4, `regime_eval/rev2_arith.py` |
| Rev 2, T12: wall recomputed with length buckets and WITNESS cells, slots re-split, arithmetic shown | §2.4, `rev2_arith_out.txt` |
| Rev 2, T13: SET-MISMATCH anchor replay; ISA field in the knowledge record | §2.9, §1.1 |
| Rev 2, T15: J2a against the bench boundary, generators read read-only, fallback W, relay question | §2.10, Q-REVAL-15 |
| Rev 2, T19: re-cited regime_tables rev 0.3; C3's row list, §8's header, §4.4 fixed | header, §4.1, §8, §4.4 |
| Rev 2, T20: the `picks.tsv` and arm-timing interface columns; nothing more general | §5.5 |
| Rev 2, side: memfn/CLAUDE.md's boundary table (regime table, evaluator, measurement sets; owner split per T18) | `memfn/CLAUDE.md` |
| Rev 2: change log, status line, new questions Q-REVAL-12..16, "Questions — resolved" kept intact | header, §9.2, §9 |
| **Rev 2.1: three late rulings applied, each marked `[D166a1]`, `[D166a1.1]` or `[rt0.4]`, with a change-log line** | header, §R.3 |
| Rev 2.1, D166 add. 1 (a): CB decidable from timing alone; k chosen and justified from gridread's A/A and the F2 cells; perf-misses an optional ungated corroboration column with its own count | §2.7, `rev2_arith.py` part 1b, Q-REVAL-17 |
| Rev 2.1, D166 add. 1 (b): every bar, control, G0-G4 leg, prereg field and refusal rule audited for perf dependence; P-PRED's misses figure optional | §2.7 (Audit), §3.2, §3.4 |
| Rev 2.1, D166 add. 1 (c): every perf pass in grid2 and the judge slots optional; slot arithmetic with and without | §2.1, §2.4, `rev2_arith_out.txt` |
| Rev 2.1, D166 add. 1.1: scripts print the paranoid value, "2 or lower enables the optional pass", what it adds, and the one-off and persistent commands; never act | §1.2 (Harness requirements), §7 (E4) |
| Rev 2.1, rt0.4: A/I as separate keys; R8 for RD2 everywhere; rev 0.4 re-cited; Q-REVAL-13 and -14 RESOLVED; C3's row list, witness list and §8 checked for R8; [MEASURE-SET] trigger E3 / `msetdes`; [TABLE-JUDGE] | header, §1.1, §4.1, §4.4, §5.4, §5.5, §7, §8, §9.2 |
| **Rev 2.2, part 1: the real J1 population folded in; each change marked `[r2.2]`, with a change-log line and a by-section map** | header, §R.4 |
| Rev 2.2, subjects and questions read from main (rwcorpus manifest, 88 rows / 7 classes; rwquest, 177 questions); the python counts are not treated as an oracle | header (Inputs), §2.3a |
| Rev 2.2, caveat (a): line-ending class per subject; how cells are labelled (`eol`, `eol_sensitive`); `lines` N counts the CR | §2.3b, §2.4 rule 7, §6.1 |
| Rev 2.2, caveat (b): the buffer-drawing rule across whole files (stratified, salt-derived, pool families, one reserve per pool, 16-window floor) | §2.4 rules 1-7, §2.8 items 4-4a |
| Rev 2.2, caveat (c): pg8186, pg8453, pg20175 reported apart, never gate, never pooled | §2.3b, §2.8 item 4a |
| Rev 2.2, caveat (d): gazetteer fixed-width and tar NUL padding, with their effect on landing statistics and the `shape` labels and gap quantiles | §2.3b, §6.1 |
| Rev 2.2, caveat (e): the disclosure row in §5.1, with its mitigation (headline overall, primed-only, unprimed-only; sealed holdout and J1b stay) | §5.1, §6.1, §7 (E2) |
| Rev 2.2: the 177 questions through the five-class placement WITHOUT a compile, marked ESTIMATE; cells per class × regime; the wall recomputed | §2.3a, §2.4, `rev22_population.py`, `rev22_arith.py` |
| **Rev 2.2, part 2: a LEAN plan leads (about two quiet-box windows plus grid2's ~56 min); rev 2.1's plan is the alternative** | §2.4 (LEAN PLAN), §7 (E7) |
| Rev 2.2: the lean plan built from the cut levers, each cut's cost in POWER (cells and patterns per layer × regime, gates to UNDERPOWERED/UNREACHED, unscorable controls), the levers not taken and their costs | §2.4 (the cut ladder, levers not taken) |
| Rev 2.2: gate formulas kept; one looser constant and one pooled final reading PROPOSED with their arithmetic | §2.4 (power table, items 3-4), §3.1 (G2), Q-REVAL-16 |
| Rev 2.2: plan → wall → per-gate power table | §2.4 (the power table) |
| Rev 2.2: J2a's fallback (byte transfer, sha-checked against the bench manifest) is the default; the import is the alternative | §2.10, Q-REVAL-15 |
| Rev 2.2: Q-REVAL-12 (lean vs full, leaning lean), Q-REVAL-16 (constants) and Q-REVAL-17 (k = 3) ready to send to Frank (`[r2.3]` now RESOLVED) | §9 |
| Rev 2.2: the two rev 2.1 findings for the kit manager left as they stand | — (not in this note) |
| **Rev 2.3: three rulings applied, each change marked `[r2.3]`, with a change-log line and a by-section map** | header, §R.5 |
| Rev 2.3, Frank's condition on Q-REVAL-17 and its extension: ONE evaluator parameter table, every chosen constant a row with name, value, unit, what it gates, provenance (CHOSEN / DERIVED / RULED), override option and where printed; prose refers by EP id | §3.0a, and the references in §1.2, §2.4, §2.6-§2.9, §3.0-§3.4, §4.2-§4.3, §5.3 |
| Rev 2.3: override semantics. Overrides allowed; a run whose parameters differ from the pre-registered values is NON-GATING, labelled "advisory: parameters differ from prereg <hash>", lists every differing parameter; `--final` refuses any override; the prereg pins and hashes the whole table; the top of every report prints the table and its diff | §3.0a (Override semantics, What every report prints), §3.4 |
| Rev 2.3: k (EP21) named in the bars file, printed beside the k = 2 / 4 counts in every report, overridable by `--cb-k=`, listed with provenance | §3.0a, §2.7, §3.2 (P-CB), §3.4 |
| Rev 2.3: Q-REVAL-12/16/17 RESOLVED in §9; the lean plan is THE plan, rev 2.1's plan a documented alternative only; the two loosenings RULED | §0, §2.4, §2.8, §3.1, §7 (E7), §9 |
| Rev 2.3: the arithmetic scripts keep their constants as the table's plan-only rows; nothing timed, built or under `src/` | EP67-EP72; `regime_eval/CLAUDE.md` |
| **Rev 2.4: Frank's [KNOW-SRC] ruling applied, each change marked `[r2.4 KNOW-SRC]`, with a change-log line and a by-section map** | header, §R.6 |
| Rev 2.4: the parameter table is the `evaluator-params` kind; the file `regime_eval/regime-eval.evaluator-params.tsv` (canonical `#section` shape, loads unchanged when [KNOW-SRC] lands) is the source of truth and §3.0a mirrors it | §3.0a, the file |
| Rev 2.4: the prereg hash is the kind's DIGEST; the report's diff against prereg is the census tool's diff; the table is listed through `--list-evaluator-params` | §3.0a, §3.4 |
| Rev 2.4: the placement rule checked against every EP row; derived rows (EP14, EP16, EP30, EP58) moved to the measurement set with their keys named; EP67-EP72 out of the kind; borderline EP56/EP57/EP47 argued | §3.0a |
| Rev 2.4: overrides unchanged in spirit, restated as overrides of a [KNOW-SRC] kind's values | §3.0a |
| Rev 2.4: the new data file is described in `regime_eval/CLAUDE.md`; the `memfn/CLAUDE.md` line carries rev 2.4; no `src/`, build or timing | `regime_eval/CLAUDE.md`; `docs/design/memfn/CLAUDE.md` |
| CLAUDE.md lines | `docs/design/memfn/CLAUDE.md`; `regime_eval/CLAUDE.md` |
| No timing, no make test, nothing under src/, memfn/src/, tests/, lib/ | held: Python arithmetic over finished files only; pcrec-bench read with `git show` only; `[r2.2]` the corpus bytes in `worktrees/.corpus/` read and counted by `python3 -I`, nothing executed, nothing compiled |
