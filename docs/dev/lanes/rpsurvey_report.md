# rpsurvey — [RUN-POS-SET] survey: do caseless UTF-8 positions cut required runs?

Lane rpsurvey (sonnet), 2026-11-05, worktree `worktrees/rpsurvey` cut from main b04160586. Facts only; no source edits. Rulings file `rpsurvey_rulings.md` did not exist at any commit/report point (no later rulings). Evidence under `docs/dev/lanes/rpsurvey_evidence/` (scripts, two TSVs); raw sweeps stayed in scratch.

## Verdict on the row's trigger ("the survey finds runs cut on real bench cells")

**FIRES.** The one bench sub-bench that measures pcrec under `-e utf8` is `bench/utf8` (8 pcrec `*-utf8` testees in its roster, 76 pattern files). In it, 5 of the 12 `ci-*` patterns have a required run cut or lost today by a caseless position: `ci-strasse` (run 3 of 7 positions), and `ci-moskva`, `ci-greek-run`, `ci-e-acute`, `ci-sigma` (run lost entirely, 0, where the caseless-free literal has 12 / 6 / 2 / 2). Two more, `ci-kelvin` and `ci-long-s`, are the row's named k/s letters but are single-position patterns: no run exists to cut, and their search choice still differs from the `(?i)q` twin (Q3). Scoping caveats: (a) the k/s letters named in the row cut only ONE bench cell's run (`ci-strasse`, by 1 position); the larger bench loss is non-ASCII caseless letters, which the row's title ("caseless UTF-8 letters") covers but its body does not name. (b) The bench's other caseless patterns (`capability/wild-secrets-slack-webhook-url`, `wild-waf-crs-942270-union-select`, WAF/`ci-256` families) are cut too under `-e utf8` but are measured under byte only, so they are not utf8 cells.

## Premise test (first, as briefed)

`(?i)ok` vs `(?i)oq`, `-e utf8 --emit-facts`: `req_run`/`req_whole_run` are `none` for both (2 positions is below the run floor, so no run to compare), but everything downstream differs: `RX_DFA_SCAN` unanchored vs cover, `RX_DFA_PREFILTER` byte-class vs none, `width` [2,4] vs [2,2], `kset_walk` `[2],[3]` vs `[2],[2]`. With enough letters the run itself is cut: `(?i)abcdefghijk` utf8 whole run 10 positions (`abcdefghij`; the trailing k is the gap) vs 11 for the `q` twin; `(?i)abcdkefghij` utf8 whole run `efghij` (6) vs 11 for `(?i)abcdqefghij`; `(?i)abk` has no run under utf8, `(?i)abq` has 3 positions. Under `-e byte` k is not cut (`(?i)abcdkefghij` byte whole run 11, k included). Premise confirmed: req.c keeps one cube per position, and k/s cut it under utf8 only.

## Q1 — which letters / shapes cut

Source: `third_party/ucd-16.0.0/CaseFolding.txt`, statuses C and S (simple folds, what `-e utf8 (?i)` uses; the 104 F entries and 2 T entries are excluded — those belong to [FULL-CASEFOLD]). Grouping by fold target gives **1454 fold classes** (1427 two-member, 24 three-member, 3 four-member).

| class shape | classes | what it is |
|---|---|---|
| all members one byte | 24 | the ASCII letters other than k, s (a-z minus k, s) — always one cube, never cut |
| **ASCII letter + multi-byte member** | **2** | **k / K / U+212A (4B 6B E2 84 AA) and s / S / U+017F (53 73 C5 BF)** — the only ASCII letters that cut |
| same length 2 | 425 | non-ASCII; position-wise hulls: 317 have every position's hull within 2 members, 108 do not |
| same length 3 | 686 | 426 hull within 2 members, 260 not |
| same length 4 | 282 | 131 hull within 2, 151 not |
| mixed length (e.g. 2 vs 3 bytes) | 35 | ß/U+1E9E, å/Å/U+212B and the like |

Observed on the compiler (`(?i)abcd<X>efgh` per class, one compile per class, `req_whole_run` position count vs the 8+width a cut-free run would have): **513 classes keep the whole run (24 ASCII + 210 + 279), 941 are cut** (215 of the 2-byte, 407 of the 3-byte, all 282 of the 4-byte, all 35 mixed, both ASCII k/s). Of the same-length classes (1393) a per-position hull of at most 2 members (a cube, representable by the existing form) holds for 874, so at least 385 same-length classes are cut today although each position is already a cube; the other 519 need a position of more than 2 members (`pos_set` is 2, `PCREC_MAX_REQ_RUN_POS_SET`).

Other non-cube shapes that cut a run, independent of caseless: a class that is not one cube or has more than `pos_set` members (`rb_class_into`'s gap: `[0-9]`, `\w`, `.`, `[a-z]`...); a class with a member above 0xFF (`pcrec_cls_cube` false); and any UTF-8 lowered non-singleton class, which lowers to an alternation of byte sequences, which `rr_alt` reduces to its common cube-hull head and tail only (`src/facts/req.c` 470-480, 349-380). That mechanism, not the byte-cube representation, is why e.g. `(?i)москва` loses its run: each letter is a 2-branch alternation `d0 9c | d0 bc`; per-position hulls are cubes of 2 but alternation's `all` is false so only the adjacent join survives and the 12-position run falls below the floor (`req_whole_run` none). Under `-e byte`, a caseless ASCII letter is one 2-member cube and cuts nothing; non-ASCII letters are not folded without `--ucp`.

## Q2 — corpus and bench counts

Population (existing enumerator: `pcrec --list-source` over `tests/**/*.rxt`, the method of `scripts/emit_sweep.py list_source_patterns`, plus `pcrec-bench/bench/*/patterns/*.rx`, read-only): 6686 rows, **5449 unique** (5057 corpus (pattern, flags) pairs, 392 bench files). Observable used: `--emit-facts` (`req_whole_run`, the stamps in `docs/spec/facts_listing.md`), not re-derived. `.rxt` head `config`/`with`/`from`/`features` cascades are not applied (flags column `i`/`u` only; `--features all`), the `.rxt`'s own encoding column is ignored (every pattern is compiled under both `-e utf8` and `-e byte`). 4650 corpus + 367 bench = 5017 compile under utf8 (4621 + 366 under byte); the rest are pcrec's own refusals (size caps, UCP `\w`, missing modules) and are excluded, not counted as affected.

| measure | corpus | bench | total |
|---|---|---|---|
| unique patterns compiled under utf8 | 4650 | 367 | 5017 |
| caseless scope (`-i` flag or `(?i`/`(?i:` in text), compiled | 363 | 27 | 390 |
| caseless AND a literal k/s/K/S outside classes/escapes (twin k→q, s→t exists) | 39 | 11 | 50 |
| of those, run (`req_whole_run` or `req_run`) differs from the twin | 15 | 3 | **18** (15 of 39 corpus, 3 of 11 bench) |
| of those, search-choice stamps differ from the twin | — | — | 31 (see Q3 caveat) |
| caseless AND a non-ASCII letter in the text | 13 | 7 | 20 (12 have `req_whole_run` 0 under utf8) |
| utf8 whole run SHORTER than the byte run (both compile) | — | — | 31 (29 caseless; the 2 others are `(?x)` with a ZWSP-class char) |

The 18 run-cut patterns, run today vs twin (positions): corpus `litscan/handoff.rxt:1012 (?i)straße` 3/4, `:1101 (?i)stra(ße)` 3/4, `:2395 a.*?(?i:select)` 5/6, `handoff_vm.rxt:400 (?i)stra` 3/4, `reqcube.rxt:29/48/67/86` (`S(?i:ab)`/`sab` alternations) 0/3, `:164 (?i:select)\d+x` 5/6, `:181 (?i)select` 5/6, `:242` 10/12, `:377 (?i)information_schema` 12/18 (run 8/8), `:396 (?i)union.*?select.*?from` 5/6, `:434` 5/6, `:480` 2/3; bench `capability/wild-secrets-slack-webhook-url` 6/14, `capability/wild-waf-crs-942270-union-select` 5/6, `utf8/ci-strasse` 3/4. Full rows: `rpsurvey_evidence/twin_affected.tsv` (37 rows: the 18 plus 19 strategy-only).

What a byte SET per position would keep (derived from the rule, since the existing observable can only show today's run):
- **k, s (ASCII+multi-byte, variable width).** After a k/s the offsets of what follows are not fixed (1 byte vs 2-3), so a run cannot continue THROUGH the letter. A set per position would keep the letter's first byte `{4B,6B,E2}` (`{53,73,C5}` for s) as the last position of the run on its left, and its last byte `{4B,6B,AA}` (`{53,73,BF}`) as the first position of the run on its right: **+1 position on each side**. E.g. `(?i)select`: today 5 (`elect`); the tail-side set run is `{53,73,BF}` then `elect` = 6, the twin `(?i)qelect`-style comparator also 6 — the k/s gain is 1 position, never a through-run. `(?i)stra` 3 → 4. `(?i)information_schema` (several s) has whole run 12 today vs 18 for its s→t twin; what sets recover there is each cut side's +1, not the 18 (derived, not measured).
- **Same-length non-ASCII classes (1393 of the 1428).** Every position carries its set and offsets align, so the whole run survives: `(?i)москва` 0 → 12 positions (`d0 {9c,bc} d0 {9e,be} ...`; each position hull is a 2-member cube), `(?i)αβγ` 0 → 6, `(?i)é` 0 → 2 (below the floor alone; the 8+2 form is kept by neighbours: `(?i)abcdéefgh` keeps `é` and its right neighbours today).
- **Mixed-length classes (35, incl. ß).** Like k/s: +1 position on each side (first-byte set `{C3,E1}` / last-byte set `{9F,9E}` for ß/U+1E9E); `(?i)straße` 3 → at most 4–5.

## Q3 — affected bench cells (pattern x encoding actually measured)

Only `bench/utf8` runs pcrec under `-e utf8` (roster: `pcrec-auto-utf8`, `pcrec-auto-nohybreseed-utf8`, `pcrec-auto-clang-utf8`, `pcrec-auto-clang-nohybreseed-utf8`, `pcrec-auto-utf8-noreqhandoff`, `pcrec-nocaps-utf8`, `pcrec-vm-utf8`, `pcrec-vm-in-utf8`; 8 pcrec testees). Table over the 12 `ci-*` patterns (whole run positions today, utf8; literal comparator = the same text without `(?i)`; strategy = engine/scan/prefilter/handoff offset):

| cell (pattern) | utf8 run today | caseless-free literal's run | strategy today | strategy of the comparator |
|---|---|---|---|---|
| `ci-strasse` `(?i)straße` | 3 | 7 (`straße`) | dfa/unanchored/handoff/h2 | twin `(?i)traße`: handoff/h0 (same class, other offset) |
| `ci-moskva` `(?i)москва` | **0** | 12 | dfa/unanchored/memchr | `москва`: dfa/cover/none, run 12 |
| `ci-greek-run` `(?i)αβγ` | **0** | 6 | dfa/unanchored/offset-set | `αβγ`: cover/none, run 6 |
| `ci-e-acute` `(?i)é` | 0 | 2 | dfa/cover/none | `é`: cover/none (same) |
| `ci-sigma` `(?i)σ` | 0 | 2 | dfa/unanchored/byte-class | `σ`: cover/none |
| `ci-kelvin` `(?i)k` | 0 (single position) | n/a | dfa/unanchored/byte-class | `(?i)q`: dfa/cover/none |
| `ci-long-s` `(?i)s` | 0 (single position) | n/a | dfa/unanchored/byte-class | `(?i)t`: dfa/cover/none |
| `ci-ascii-control` `(?i)abc`, `ci-class-range`, `ci-neg-fold`, `ci-turkish-i`, `ci-ucp-invariance` | 3 / 0 / 0 / 0 / 0 | — | not run-bearing (control or class) | — |

So the search pcrec picks does change on affected cells, with the caveat that a twin differs in more than the run (the k/s twin's width is fixed [w,w] vs variable [w,w+2], and its start set is one byte class, so cover-vs-unanchored cannot be attributed to the run alone; on `ci-kelvin`/`ci-long-s` there is no run in either, so those two are NOT run effects). Run-attributable on bench: `ci-moskva` and `ci-greek-run` (run lost; scan goes from cover/no-prefilter to unanchored with a memchr/offset-set prefilter), and `ci-strasse` (3 vs 4, prefilter class unchanged). Cells = up to 5 patterns x 8 testees = 40 run-affected, 2 x 8 = 16 k/s strategy-affected (roster-level; which cells ran in a window is the bench's ledger, not read). Other `bench/utf8` patterns: byte and utf8 runs are equal on every pattern that compiles (literal and anchored families), `qnt-*` differ the other way (utf8 run longer). Table: `rpsurvey_evidence/bench_utf8_runs.tsv`.

## Q4 — the k-set path

`src/facts/kset.c` walks the pattern's NFA (after lowering, so over BYTE classes), `frontier[j]` = the N_CLASS states a thread from the candidate start can occupy after j bytes; position j's set is the union of those states' byte classes (`kset.c` lines 33-37, 77-118). A caseless UTF-8 letter therefore reaches it as full byte sets, not cubes: `(?i)ok` stamps `kset_walk [2],[3]`, `span_facts 2:[2],[3]`, `width [2,4]` (the `[3]` is the 3-byte set `{4B,6B,E2}`, sizes from the listing's `[N]` spelling; the byte values themselves are not printed for wider positions, so identity is inferred from the three NFA arms k, K, E2 84 AA, not read off). `(?i)oq` is `[2],[2]`, `[2,2]`. Past a variable-width letter the frontier merges threads of different widths, so later sets are unions (`(?i)hello world kitchen`: `...,[3],[3],[3],[4],[4],[4],[4]`), no longer exact products. So kset already keeps `{4B,6B,E2}` at k's offset and the kit receives it; req.c's run does not.

## Method (rerunnable)

```
W=/home/pcrec/projects/pcrec/worktrees/rpsurvey; E=$W/docs/dev/lanes/rpsurvey_evidence; S=$PCREC_TMPDIR/scratch/rpsurvey
make -C $W -j4
python3 -I $E/folds.py $W/third_party/ucd-16.0.0/CaseFolding.txt $S/fold_classes.tsv      # Q1: 1454 classes, shapes
scripts/boxlock run --label rpsurvey-sweep -- nice python3 -I $E/sweep.py $W /home/pcrec/projects/pcrec-bench $S/sweep_full.tsv   # Q2/Q3: ~11000 compiles, k/s twins
python3 -I $E/an.py $S/sweep_full.tsv $S/affected.tsv                                      # twin-affected rows
scripts/boxlock run --label rpsurvey-fold -- nice python3 -I $E/foldsweep.py $W $S/fold_classes.tsv $S/foldsweep.tsv   # 1454 compiles, per-class run
build/pcrec -e utf8 --emit-facts --pattern '(?i)ok'                                        # single-pattern premise tests
```

The sweeps ran under the box lock (sweep and fold waited on three queued mechfix2 jobs for ~10 minutes). No timing runs. `fold_classes.tsv` and the raw sweeps are in scratch, not committed (regenerate with the commands above).

## Limits of this survey

- Corpus rows: `.rxt` heads, `with`/`from` cascades, per-pattern features/encoding columns are not applied; flags column `i`/`u` only. 432 (utf8) / 462 (byte) of 5449 do not compile in this harness (pcrec refusals) and are not counted.
- The twin changes the pattern text (k→q, s→t outside escapes/classes/group heads); counts of "twin differs" are for patterns with a literal k/s only. Caseless patterns whose k/s sit in a class (`[a-z]`, `[[:lower:]k]`) are in the strategy column of `twin_affected.tsv` where a twin existed and otherwise uncounted.
- "Run" = `req_whole_run` position count (and `req_run`); the run FLOOR (information-based; `(?i)ab` and `(?i)abk` utf8 have no run, `(?i)abq` has one) means a per-position set run that is longer than today's may still be below the floor; I did not model it.
- Q2's per-position-set numbers are derived from the rule (cube hull, fixed offsets) not measured; Q1's cut counts and every "today" number are measured.
- No design proposed; whether per-position sets or an alternation-as-product reading of same-length folds is the right shape is the row's later step.

STATE AT HANDOFF: report + evidence committed on `lane/rpsurvey`; no source touched; no owed runs.
