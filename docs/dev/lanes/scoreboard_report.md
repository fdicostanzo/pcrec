# scoreboard report: what PCRE2 does that pcrec does not (lane scoreboard, 2026-11-05, sonnet)

Facts only; no design, no recommendation beyond the ranking. Branch `lane/scoreboard`
from main `0e811ff4c`. Full per-gap data: `docs/dev/lanes/scoreboard_evidence/gaps.tsv`.
PCRE2 side: the committed `docs/pcre2_compliance.md` plus the installed libpcre2 10.46 used
as a LIBRARY to confirm a construct is real. The pinned PCRE2 reference copy (D181) was not touched.

## For the owner, in plain words

1. There are 16 real syntax gaps (constructs libpcre2 10.46 accepts and pcrec refuses, even with every module on), two groups ruled out of scope, one utf8-only limit (`(?r)`) and the size caps (rows 17-20). Nothing found in the other direction: no pattern pcrec accepts that libpcre2 rejects, and 43 match comparisons on edge constructs agreed with libpcre2 exactly.
2. Real-world frequency is 0 for every gap that can be measured. There is NO real-world pattern harvest in the tree ([UTF-RW] is `not-started`). The nearest populations are the 32 imported "wild" bench patterns (all compile, none uses a gap construct) and 40 hand-written "realistic" patterns (none uses one). So the ranking below rests on corpus and bench counts plus the documented outside demand in `utf_wants_2026-10-24.md`, and says so.
3. The only gap with a double-digit count anywhere is variable-width lookbehind: 37 of pcrec's 6,304 corpus patterns compile under libpcre2 and are refused by pcrec, plus 1 bench pattern. It has no plan row.
4. Next are conditionals `(?(1)..)` (5 corpus patterns, 1 bench probe) and then single-digit or one-off constructs: `\X`, `(?[..])` class set operations, `\R`, `(*ACCEPT)`, `(*FAIL)`, `\C`, `\cX`, `\o{}`, `\N{U+..}`, `(?#..)`, `(?|..)`, `[[:<:]]`.
5. Of the constructs the owner's lists name, `\X` ([GRAPHEME]) and class set operations ([CLASS-SETOPS]) are the only ones with outside-demand evidence behind them (utf_wants ranks them 1st and 3rd); in this tree their own counts are 0 to 1.
6. Prominent: a bare `pcrec` (default feature set `std1` = classes + modifiers) refuses 150 of the 392 bench patterns with "requires module X" (assertions 58, lookaround 21, unicode-props 14, atomic-groups 11, others fewer). Those are BUILT modules, not gaps, but a stranger's default compile does not see them. With `--features all` the same 392 compile except 20.
7. Six places where documents disagree with the compiler (stale rows), listed in "Disagreements" below, per the stop rule; not resolved here. Premise test: `\X` and `(?[[a-z]&&[aeiou]])` both refuse cleanly ("not implemented yet", module named); neither miscompiles. `[a-z&&[aeiou]]` (PCRE2's non-set-operation spelling) compiles and agrees with libpcre2.
8. PCRE2's options and match-time flags are covered by a separate document, `docs/pcre2_options.md` (80 flags, each with a ruled disposition). Partial matching and streaming are the one clearly open capability there (no spec support yet); the newline and BSR conventions ride the same unbuilt `verbs` module as gap 9.

## Ranking

Sort rule: real-world frequency first (0 everywhere, so all tie), then measured corpus count, then bench count, then outside-demand evidence. "corp" = patterns in `tests/**/*.rxt` that libpcre2 accepts and pcrec refuses under `--features all` (measured by compiling all 6,304). "bench" = pcrec-bench `bench/*/patterns/*.rx` (392 files) lexical hit, with the refusal confirmed by compile. Wild = the 32 bench patterns that carry a `source_url`; realistic = `eng_brep_measurements/probes/realistic_patterns.txt` (40). Every wild/realistic cell is 0 for every gap below.

| # | gap | PCRE2 | pcrec status (exact refusal in gaps.tsv) | corp | bench | demand (utf_wants) | owning row | size |
|---|---|---|---|---|---|---|---|---|
| 1 | variable-width lookbehind, e.g. `(?<=a{1,3})b`, `(?<=(a\|bc))b`, `(*plb:(a\|bc))x` | real; unbounded `(?<=a+)` rejected by both | refused: "variable-length lookbehind is not implemented" (module `lookaround` otherwise built; doc: OK-LIMITED, becomes PLANNED) | 37 | 1 (capability/negation-scope-lookbehind-var) | not graded | no row; `lookaround_design.md` names a follow-on | unknown |
| 2 | conditionals `(?(1)a\|b)`, `(?(<n>)..)`, `(?(R)..)`, `(?(?=a)..)` | real | refused: module `conditionals` "not implemented yet" (doc: PLANNED-HARD; `(R)` and assertion forms: no becomes; `VERSION`: out of scope) | 5 | 1 (syntax probe) | not graded | no row | unknown |
| 3 | `\X` grapheme cluster | real | refused: module `misc` "not implemented yet" (PLANNED-HARD) | 0 | 1 (syntax probe) | rank 1: spec RL2.2, multi-engine, asks | [GRAPHEME] not-started; needs UAX #29 data vendored | unknown; new dataset |
| 4 | `(?[ ])` class set operations | real | refused: module `extended-classes` "not implemented yet" (PLANNED) | 1 | 1 (syntax probe) | rank 3: spec RL1.3, near-universal | [CLASS-SETOPS] not-started | utf_wants: compile-time interval algebra, no engine change (unmeasured) |
| 5 | `\R` | real | refused: `misc` (PLANNED) | 0 | 1 | utf_wants #14 "trivial" | no row | unknown |
| 6 | `(*ACCEPT)` | real | refused: `verbs` (PLANNED-HARD) | 0 | 1 | none | no row | unknown |
| 7 | `(*FAIL)` `(*F)` | real | refused: `verbs` (PLANNED) | 0 | 0 | none | no row | unknown |
| 8 | `(*atomic:..)` `(*script_run:..)` `(*sr:)` `(*asr:)` | real | refused: `verbs` (atomic: PLANNED naming gap; script_run: no becomes) | 0 | 0 | script runs: narrow | no row | unknown |
| 9 | `(*CR)` `(*LF)` `(*CRLF)` `(*ANYCRLF)` `(*ANY)` `(*NUL)` `(*BSR_*)` `(*NOTEMPTY)` `(*NOTEMPTY_ATSTART)` | real | refused: `verbs` (PLANNED) | 0 | 0 | BSR_UNICODE mentioned | no row | unknown |
| 10 | `\C` | real (byte mode) | refused: `misc` (PLANNED) | 0 | 1 | none | no row | unknown |
| 11 | `\cX` | real | refused: `misc` (no becomes in doc; registry says planned) | 0 | 1 | none | no row | unknown |
| 12 | `\o{ddd}` | real | refused: `misc` (as above) | 0 | 1 | none | no row | unknown |
| 13 | `\N{U+hhhh}` | real in UTF mode | refused: `unicode-props` "not implemented yet" | 0 | 0 | #12, readability only | no row | unknown |
| 14 | `(?#..)` comment | real | refused: `comments` (PLANNED) | 0 | 1 | none | no row | unknown |
| 15 | `(?\|..)` branch reset | real | refused: `branch-reset` (registry planned; absent from the doc's survey tables) | 0 | 1 | none | no row | unknown |
| 16 | `[[:<:]]` `[[:>:]]` | real | refused: "requires module 'assertions'" even with `assertions` enabled (PLANNED) | 1 | 0 | none | no row | unknown |
| 17 | `(*COMMIT)` `(*PRUNE)` `(*SKIP)` `(*THEN)` `(*MARK)` | real | refused: "outside pcrec's scope and no module will implement it" (OUT-OF-SCOPE) | 1 | 1 | none | none (ruled out) | n/a |
| 18 | `(*LIMIT_*)` `(*NO_*)` `(*CASELESS_RESTRICT)` `(*TURKISH_CASING)` `(*scan_substring:)` `(?(VERSION>=)` | real | refused: out of scope | 0 | 0 | TURKISH_CASING out of scope | none (ruled out) | n/a |
| 19 | `(?r)` under `-e utf8` | real | refused: "not implemented under -e utf8" (OK-LIMITED, K70) | 1 | 0 | none | K70 in known_issues.md | unknown |
| 20 | size / state caps (emit bytes over 1,000,000 or 500,000; NFA over 131,072 states) | libpcre2 has no such cap on these patterns | refused: "pattern too large" (OK-LIMITED for `a{0,65535}`, PLANNED) | 1 | 7 (5 altwide + 1 bounded synthetic, 1 wild datefinder) | none | no row found | unknown |

Not gaps (checked): `\p{Assigned}` and `\p{InGreek}` are rejected by libpcre2 10.46 too; `(?R(1))` likewise; `(?(R&n)..)` with no such group likewise. Properties, scripts, `Bidi_Class`, the 53 binary properties, `\p{Xan}` etc. compile (plan row [UPROP-MORE] landed part B). `(?C..)` callouts compile under `--features all` (see Disagreements). 24 corpus patterns embedding `(?C`c: ..`)` are refused only because `--allow-code=c` was not passed; by design, not a gap.

## Accepted by pcrec but answered differently from libpcre2

None found. Compile-level: 272 probe patterns (217 + 55) were compiled by both; there is no pattern pcrec accepts and libpcre2 rejects. Match-level: 43 (pattern, subject) pairs on the constructs most likely to differ (`a{,3}`, `a{ 1, 3 }`, `(?xx)`, `\<`, `\N+`, `[a-z&&[aeiou]]`, `(?aT)[[:alpha:]]`, `(?U)`, `(?n)`, empty and nested-star cases, `\e`, `[\b]`) gave 0 differences in match / no-match / start / end. This is a small probe, not a sweep; the registry-vs-libpcre2 check (PC-3), the fuzzer and the oracle-verified corpus remain the real defences and were not re-run.

## Disagreements between sources (stop rule: both recorded, not resolved)

| # | construct | one source says | measured compile |
|---|---|---|---|
| 1 | `\v` | compliance "Character types" table: `REJECTED`, becomes `PLANNED`; registry index: `built` | `\v` compiles under the default feature set |
| 2 | `\p{..}` `\P{..}` | same table: `REJECTED`, becomes none; the "Unicode properties" section: `OK-GATED`; registry `built` | `\p{L}` refused "requires module 'unicode-props'" by default, compiles with `--features all` |
| 3 | `(?C..)` callouts | plan.md [M4-CALLOUTS] `not-started` (step 2 behaviour); compliance Callouts: `OK-GATED`; registry `built` | `(?C1)a` refused "requires module 'callouts'" by default, compiles with `--features all` |
| 4 | `\cX` `\o{}` `\N{U+..}` `(*script_run:)` `(?(R)` | compliance survey tables: `REJECTED`, becomes none (`—`); registry roadmap `planned` | refused in all cases (registry reading and doc reading agree on the refusal, differ on the roadmap) |
| 5 | `(*atomic:..)` | compliance: PLANNED, "naming gap"; registry: module `verbs`, unbuilt | refused "requires module 'verbs'" even with all modules on |
| 6 | `(?\|..)` | registry index lists it (`unbuilt`, planned); the compliance survey tables carry no row for it | refused, "not implemented yet" |

Also: the registry index reads `REJECTED` in its status column for rows that compile fine under the default set (`\d`, `\s`, `(?i)`): that column is the base-grammar status, and `built` plus the module name is what answers "does it work"; recorded because a reader of only the index can misread it.

## Options and match-time features

Not an unknown after all: `docs/pcre2_options.md` ([PC-5], ruled D38 2026-08-14) is an option-by-option survey of 80 flags and values against libpcre2 10.46 (3 shared bits, 28 compile bits, 17 `EXTRA_*` bits, 5 JIT, 19 match/DFA/substitute, 6 NEWLINE and 2 BSR values). I did not re-survey it; I only read the dispositions and grepped `docs/spec` for the most visible ones. Each flag carries a ruled disposition, not a build state:

- `NEVER` (ruled out; 15 or so rows): `NO_AUTO_POSSESS`, `NO_DOTSTAR_ANCHOR`, `NO_START_OPTIMIZE`, all five JIT options, `NO_JIT`, `COPY_MATCHED_SUBJECT`, `DFA_RESTART`, `DISABLE_RECURSELOOP_CHECK`, `ALT_VERBNAMES`.
- `LATER` (no customer, no row): `ALT_BSUX` and `EXTRA_ALT_BSUX`, `NEVER_BACKSLASH_C`, `EXTRA_MATCH_WORD`, `EXTRA_MATCH_LINE`, `EXTRA_PYTHON_OCTAL`, `EXTRA_NO_BS0`, `DFA_SHORTEST`.
- `RIDES(owner)` (arrives with a module or row): the newline family (`DOLLAR_ENDONLY`, `FIRSTLINE`, `EXTRA_ESCAPED_CR_IS_LF`, NEWLINE and BSR) rides DD-11, which is the same gap as row 9 above; partial matching (`PARTIAL_SOFT`, `PARTIAL_HARD`) rides OS-3 / streaming (spec `match_api.md` 5.2 paragraph 6: "No partial-match or streaming window state"; plan [M3.0], [M3.1] `not-started`); the `EXTRA_ASCII_*` flags are `(?a..)` and are built.
- `API-PARAM` / `GENERATION-AXIS` / `EMITTED-LOOP`: `NOTBOL`, `NOTEOL`, `USE_OFFSET_LIMIT`, `ANCHORED`, `ENDANCHORED`, `LITERAL`, `NOTEMPTY`, `NOTEMPTY_ATSTART`. A grep of `docs/spec` finds no `NOTBOL`/`NOTEOL`/`OFFSET_LIMIT` entry; the spec does carry an internal `notempty` machine. Whether each is built today I did not establish (the options doc records the ruling, not the state).
- `pcre2_pattern_convert()` (glob / POSIX to pattern) is explicitly excluded by that survey (section 7). Serialisation of compiled patterns and `pcre2_callout_enumerate` are not in either document; no pcrec counterpart was found; absence not confirmed.
- JIT is not applicable to an ahead-of-time compiler.

Two other differences that are caller-visible and already recorded elsewhere: pcrec's own substitution artifact (spec `subst_api.md` section 9 lists its differences from `pcre2_substitute`), and the oracle being pinned at `options = 0` (so none of the above is differentially verified).

## Method

- Constructs: the registry index of `docs/pcre2_compliance.md` (144 rows, `built`/`unbuilt` column) and its per-section survey tables; confirmed by compiling a minimal pattern per construct with `build/pcrec --features all -p rx -o scratch --pattern ..` (217 + 55 probes, exact first refusal line recorded in gaps.tsv). `--features all` is used because the default set (`std1`) refuses every built module by name; the default-set refusals are reported separately (summary point 6).
- libpcre2 confirmation: a 10-line C harness (scratch) calling `pcre2_compile` from libpcre2-8 10.46, byte and UTF modes; used only to say "this construct is accepted/rejected".
- Corpus: `build/pcrec --list-source` over the 312 `.rxt` files, `pattern` rows, 6,304 patterns (the 6,174 quoted by the rwsurvey lane in October has grown). Each compiled with `--features all` (byte, then utf8 on failure): 5,864 compile, 440 refuse (most are the deliberate error tests); the 440 were then run through libpcre2, and "libpcre2 accepts" is the corp column. Head directives (`features`, `flags`, `engine`) were not applied, so a few patterns that only compile under their file's flags show as refused or accepted by the wrong route; the libpcre2 cross-check removes most of this noise. `tests/reject/` (a shell table, not `.rxt`) is not counted.
- Lexical counts (bench, corpus, wild, realistic): a small escape- and class-aware scanner in scratch, not a parser, so they are hits not proofs. They count a pattern once per construct kind.
- Bench: 392 pattern files under `bench/*/patterns/*.rx` of pcrec-bench (read only); "wild" = those whose `provenance.tsv` row has a `source_url` (32, in `capability` and `unusual`); the 12 `syntax` bench rows are one probe per construct, so they show one hit per construct by design and do not measure frequency.
- Plan rows: `grep` of plan.md, each checked against the registry result rather than its title.
- Raw data (not committed): `$PCREC_TMPDIR/scratch/scoreboard/` (probe results, counts, corpus and bench compile TSVs, refusals-vs-libpcre2 table).

## Measured vs inferred

Measured on this box: every refusal line; libpcre2 acceptance of each probe; corpus compile results (6,304) and the libpcre2 cross-check of the 440 refusals; bench compile results at `--features all` and at the default set; the 43 match comparisons; the 150-of-392 default-set figure (first stderr line contains "requires module"; a few of the 242 others may be other errors).

Read from documents, not re-measured: `docs/pcre2_options.md` dispositions; the compliance statuses and `becomes` values; plan.md STATE tags and row text; the utf_wants demand grades ("external demand" is that lane's evidence, I did not check it); the size notes ("unknown" wherever no row or design gave one; I estimated none).

Inferred or limited: lexical counts; the corpus is pcrec-authored, so a 0 there says little about outside use; "real-world frequency 0" means nothing in this tree, not nothing in the world, because no outside harvest exists yet ([UTF-RW] not started); libpcre2 version-of-introduction per construct is not stated in the compliance doc and was not looked up, except the `{,n}` quantifier (10.43+, the doc says so); the options section reports dispositions from `pcre2_options.md`, not build state.
