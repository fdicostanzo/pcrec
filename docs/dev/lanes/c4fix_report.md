# c4fix report: r58 FIX-NOWs on the C4 data-scope rule

STATE: complete (validation owed: one queued `make test`, key below)

## Summary
`mask_rxt` / `mask_tsv` in tests/memfn/arch_blind_check.py now follow the .rxt grammar
instead of keying on a line's first word. Commit 97b4d6b64 (fixes), 094a17b19 (skill
sentence, separate commit). `bash tests/memfn/run_arch_blind.sh` 32 pass / 0 fail;
`make test-memfn-arch` green; `make strict` clean. Allowlist unchanged (103 hits / 53 groups, floor 26).

## Fixes per finding
- IDENT-2: manifest comment in tests/codegen/run_dfa_stamps.sh now says "never-match under the byte
  encoding this census compiles at", names the two entries that match under UTF and that the last has no
  zero-width assertion. Pins untouched.
- SCOPE-1: prose regions (§1.4.4: kinds description, vocabulary, license-note, adaptation, attribution,
  note, value exactly `|` after trimming, to the first line indented <= opener, blank or comment) and `ext`
  subtrees (§1.4.5) are not data: their lines are unmasked whatever their first word. The kind lists are the
  `--list-schema` rows with value=prose AND children=prose / children=tree (hardcoded; the check runs no pcrec).
- SCOPE-2: the `pattern |` region clause and its comment are deleted.
- SCOPE-3: TSV header = the first line among the leading `#` lines and the first content line that has
  >= 2 tab cells, one exactly a declared column (`pattern`, `subject`, `oracle_subject_spans`,
  `oracle_matches(subject=>spans)`). A `#` line with such cells counts (the `# id<TAB>...<TAB>pattern`
  header style of tests/subst/d27 and ~20 others); a prose comment never does (arms_reach.tsv's
  "# REACH: ... subject ..." no longer masks column 0). Substring match removed. `#` rows after the header stay in scope.
- SCOPE-4: controls rewritten (`data_scope_files`): every plant is `a <word> b` (class 1 needs the
  boundaries); one line per data keyword, an indented directive, every prose-kind opener, a pattern ending
  `|`, each closer (indent, blank, comment, whitespace-only inert), trailing-space `|`, an `ext` subtree,
  TSVs with comment first line / comment header / late header / one-word comment / no header, and `src/`
  .rxt/.tsv that must hit. Plus direct asserts that `mask_rxt` keeps the keyword and line numbers and
  `mask_data` applies only to tests .rxt/.tsv.
- SCOPE-5: `var` stays masked; named in the scope sentences of docs/design/memfn/integration.md (C4 row,
  whose sentence was also cut off mid-clause: completed) and docs/testing.md.

## Mutation gate
Harness: scratch mut2.py, adapted from the critic's mut.py (its string anchors named code now deleted), 53 mutants:
deleting each keyword of the data, prose, tree and TSV-column sets, each region/closer clause, the comment test,
lstrip, whole-line blanking, scope guards, the mask_data call, header/column rules. 50 killed, 3 survivors, all
equivalent:
- `comment does not close` and `comment test off`: a column-1 `#` line has indent 0, never > the opener's
  indent, so the indent test closes the region anyway; and its first token is `#...`, never a data keyword.
- `tsv substring match` (detection only): with exact column selection unchanged, a header found via a
  substring cell masks no column; the column-selection variant (`tsv col substring`) is killed.
The critic's original mut.py was not re-run as written (its anchors no longer exist after SCOPE-2 deleted the clause).

## Reader diff
Scratch readerdiff.py: `build/pcrec --list-source` over the 337 listable tests/**/*.rxt (5 golden files
unlistable, skipped, as in r58). Reader data lines = `pattern` rows + `#section cases` rows other than g/gp:
98,114. Masked lines excluding `var`: 98,114. Missed 0, over-masked 0; 39 `var` lines masked (the reader does not
dump `var`; ruled data, SCOPE-5). The old mask gives the same counts (no prose line in today's corpus starts with
a data keyword), so SCOPE-1 differs only in the controls today. TSV has no reader; the whole-tree scan
(103 hits / 53 groups) is identical.

## Validation
- `bash tests/memfn/run_arch_blind.sh`: 32 passed, 0 failed.
- `make test-memfn-arch`: green. `make strict`: clean.
- OWED: `make test` via boxqueue, key `300-c4fix-b202611191818222429986.test` (perfrun, cap 3996). It is held by a
  lift file and will not start until the manager creates
  `/home/pcrec/projects/pcrec/worktrees/c4fix/.lift` (after 07:00 on 2026-11-20; it cannot end before 20:00 tonight).

## STATE AT HANDOFF
Branch lane/c4fix: commits 97b4d6b64, 094a17b19, this report. Rulings file docs/dev/lanes/c4fix_rulings.md:
absent, nothing applied. Owed: the key above (needs the lift file).
