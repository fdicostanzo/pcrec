# scope

## Findings


### SCOPE-1 (CONFIRMED, maintenance/answer-hole; effort S; blast: C4 only) prose region lines and `ext` trees whose first word is a data keyword are masked
mask_rxt keys on the first token of EVERY line (any indent) and has no notion of the prose regions (`description |`, `vocabulary`, `license-note`, `adaptation`, `note`, any `children: prose` kind) or the open `ext` subtree (rxt_format.md 1.4.4/1.4.5). The ruling says description/other directives stay in scope.
Repro (scope/craft.py, tests/ rxt text, planted `avx512`): `description |\n  m avx512 here`, `  n ...`, `  pattern avx512`, `  var avx512`, `  under avx512`, also under `vocabulary x |`, `provenance/license-note |`, and `ext foo\n  m avx512` -> all PASS-UNSEEN (old checker hit them). "pattern" or "n"/"m" as the first word of a prose line is ordinary English. 
Fix shape: track region state for every prose-opener (from --list-schema value=prose AND children=prose) and only mask a data keyword at column 0 or under an `under` line; do not mask inside prose/ext regions.
mask_rxt.py:277-297 (arch_blind_check.py).

### SCOPE-2 (CONFIRMED, answer-hole + design; effort S) `pattern |` / `pattern-esc ... |` region has no basis in the spec and the keyword mask lacks the trailing-text tail it implies
rxt_format.md 1.4.4p1: only kinds with value:prose AND children:prose open a region; `pattern`/`pattern-esc` are value:raw children:none (a pattern `|` is the regex). The code opens a region at `pattern ...|` or `pattern-esc "x" |` and blanks following more-indented lines. In valid files those lines cannot exist (indent under a pattern is refused), so this masks only invalid input, but in an invalid/ draft file it blanks arbitrary prose. Zero over-masking in the real corpus (see counts below), so severity low. Also a region closes on a whitespace-only line (spec: bytes inside region) - over-scans only (conservative). Mutants of all region clauses survive (SCOPE-4), consistent with the clause being dead.

### SCOPE-3 (CONFIRMED, design/maintenance; effort S) mask_tsv takes line 0 as the header even when it is a `#` comment
Of 92 tests/**/*.tsv, ~75 begin with a `#` comment line and the true header (if any) comes later. mask_tsv tests only lines[0]; a comment that contains the word "subject" blanks column 0 of EVERY later row. Today: tests/possessify/arms_reach.tsv (comment "...witness subject...", col 0 = pattern text, 18 lines) and tests/ucp/latin1_fold_10.46.tsv (comment "...all 256 subjects", col 0 = hex byte, 114 rows) are masked this way, by accident of wording; harmless now, but a later edit of a comment, and any TSV with a note column named e.g. `subject_notes`, silently exempts data from C4. Conversely a real `pattern`/`subject` header BELOW comment lines (e.g. tests/memfn/d27_region/cases/patterns.tsv, d3_census) is not masked (conservative: the lane's ruling is half-applied, not unsafe).
Genuine masked TSVs: tests/lookaround/d27_l1/l1d27_listing.tsv (pattern; oracle_matches(subject=>spans): data), tests/subst/d27/corpus/d_{big,bsk,byte,empty,grp,lim,name,nogap,tpl,utf}.tsv (pattern, subject: data). No prose column is blanked (the "finding"/"why" columns stay in scope).
Fix: skip leading `#` lines to find the header, or require the header line to be non-comment.

### SCOPE-4 (CONFIRMED, test-adequacy; effort S) scratch controls are vacuous for the pattern line, the region, and several keywords: 26 of 40 mutants survive per-clause
The data-scope control plants the word as `a<W>b` (pattern lines 3, region line 8, TSV `a<W>b` cell). CLASS 1 requires a non-alphanumeric boundary (L/R lookarounds, arch_blind_check.py:75-76), so those plants never hit even with NO masking. Only the `m "W"`, `ms 1 "W"`, TSV subject cell `W=>0-3` rows prove anything.
Mutation run (scope/mut.py, copy of checker, scope/mut.out; FAIL lines with TMPDIR under scope/tmp, baseline 22 PASS, 0 FAIL):
 SURVIVED (rc=0): delete kw `pattern`, `pattern-esc`, `mg`, `gu`, `var`, `under`; region never opens; region opens for `pattern` only; region opens without trailing `|`; region body not blanked; region `>` -> `>=` and -> always-true; region not closed by blank; not closed by `#`; comment test removed; lstrip removed (indented data keyword unmasked); `tests` scope guard on .rxt dropped / on .tsv dropped (an .rxt under docs/ or src/ is masked); TSV `pattern` column not masked; TSV header row masked too (incl. substring `pattern` match `'pattern' in h`).
 KILLED: delete kw m/n/ms/ns/mc (n, ns, mc killed only by the real-corpus allowlist STALE/NEW rows, not by the scratch control: scopectl=0), rxt/tsv mask noop, mask_data call removed, tsv subject col, all/no cols.
 Surviving mutants mean e.g. the `pattern` keyword, the whole `pattern |` region path, indented keywords and the scope guards are untested; the corpus-level allowlist would catch some by new hits only if a real file regresses. Fix: plant with boundaries (`a W b`), add `mg/gu/var/under/pattern-esc` lines, an indented `under` child, a non-tests .rxt/.tsv plant that must hit, and a header-masking/pattern-substring TSV row.
Allowlist edits (read-only run of the checker at the review tree): 103 hits in 53 groups, allowlist 53 rows / 103 allowed, 0 STALE, 0 NEW, floor check passes (floor literal 26 in run_arch_blind.sh, unchanged). Each deleted/lowered row (lookbehind_variable.rxt 4->2 etc.) equals the new scanner's count. OK.

### SCOPE-5 (CONFIRMED, minor, answer-hole by design; effort XS) data-keyword mask blanks the whole tail incl. trailing comment form and `var` values; `g`/`gp` are not keywords
`m "a" 0 1 # avx512` -> blanked (a trailing `#` is data per 1.4.1, so correct). `var NAME "..."`: masked, but 39 corpus lines (tests/vars/*.rxt) are not in --list-source's pattern/case set (var is a pattern-fragment value: arguably data, but it is a disagreement the ruling's "pattern/case lines" did not name; keep or document). `g`/`gp` (numeric slot spans) not masked: harmless (no strings). Directive lines carrying `\t` after keyword are masked (split on any whitespace), also pattern with tab (a hard error in pcrec) - immaterial.

## PROBED-AND-HELD

- mask_rxt vs `pcrec --list-source` over EVERY tests/**/*.rxt (342 files; 337 listable, 5 tests/findings/golden/*.rxt are not parseable by the built compiler so uncompared): truth lines (pattern/pattern-esc blocks + cases except g/gp) = 98114, mask blanks 98153; MISSED data lines 0; OVER-masked 39, all `var` lines (tests/vars/{basic,caseless,startset,unset}.rxt); no non-data line other than var swallowed in the real corpus. scope/cmp.py, scope/cmp.out.
- Data directives vs --list-schema block kinds: pattern, pattern-esc, m, n, ms, ns, mc, mg, gu, under, var all in KW; unmasked case/value kinds g, gp (numeric), var-unset, callout, variant `text`, are not subject data in the ruling's sense (callout/var-unset/text could carry pattern text: `variant ... text <regex>` is raw pattern text and stays in scope; conservative).
- Indented `#` (col 2+) and `# comment after region`, region end by blank/dedent/comment, CRLF, `pattern-x` prefix, name/var-unset/callout/variant lines: all stay visible (craft.py, 'seen').
- Allowlist counts match the new scan exactly (above).
- Cases checked: 29 crafted inputs, 40 mutants, 337+92 real files. Probes finished before 19:45.

CRITIC COMPLETE
