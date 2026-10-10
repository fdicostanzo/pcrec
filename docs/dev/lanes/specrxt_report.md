# Lane specrxt: rxt_format.md facts-only and numbered (report)

Lane specrxt (sonnet), branch `lane/specrxt` off main `eac53111`, 2026-10-10. Plan row `[SPEC-CLEAN]`, `docs/spec/rxt_format.md` (1,764 lines before, 8 marker lines). Method: the speclim, specreg and specsmall lanes. Not done here: docs/dev/plan.md (the manager's, at merge); full `make test`, mech, test-axes, san (box hold).

Citation note for readers of this report: numbered docs are cited below in words ("section 1.3 of rxt_format.md"), because the tree-wide citation scan reads a literal section-sign citation in any tracked file, this one included.

## 1. Survey, before and after

Counted by `tests/spec_history/spec_history.py` (marker lines outside fenced code; "before" = the three baseline rows removed).

| file | lines before | marker lines before (walkback/narrative/tagopen) | lines after | headings | paragraphs | marker lines after |
|---|---|---|---|---|---|---|
| rxt_format.md | 1,764 | 8 (4/1/3) | 1,776 | 32 | 224 | 0 |

No allowlist rows were needed. The document carries the generated contents block (`scripts/spec_toc.py --init`) and the numbering, produced by the unmodified `studies/specnum/number.py` over a hand-written draft (the draft is in the session scratchpad, not committed; the result is the document). The draft was a scripted edit of the old text: the old document was mostly facts already, so the job was numbering, removing build-step tags and correcting what the code disagrees with, not restructuring.

Numbering decisions. The old document had no numbers, so none are inherited; its section names are kept as headings.
- 1 the `.rxt` format: 1.1 the head, 1.2 the delivering call, 1.3 building from a source file, 1.4 the lexical rules (1.4.1 to 1.4.4 the line classes S0-S3, 1.4.5 the open subtree, 1.4.6 the schema layer, 1.4.7 values and whitespace), 1.5 the block's line kinds (1.5.1 the subject escapes), 1.6 named subjects, 1.7 `mc`, 1.8 `under`, 1.9 `provenance`, 1.10 `analysis`, 1.11 `variant`, 1.12 `ext`, 1.13 the schema and its surface (1.13.1 the clause spellings), 1.14 the example.
- 2 `--list-source` (2.1 the four `#section` blocks), 3 oracle verification (3.1 `oracle`), 4 how the harness evaluates a block, 5 the driver protocol, 6 organizing tests by component (6.1 adding a directory).
- Three headings are new because the old text hung their content under the wrong parent: 1.4.7 (the whitespace, tab, one-space and block-scalar rules sat as bullets under "The SCHEMA layer"), 1.5 (the whole block directive list sat as bullets under the same heading) and 1.5.1 (the subject escape table).
- The "Drift found and fixed by this document" section is removed (history, moved to the record).

## 2. History moved (frozen)

`docs/dev/history/rxt_format_record.md`: the COMPLETE old text, verbatim, under a short header. The same text is in git at `eac53111`. `docs/dev/history/CLAUDE.md`, `docs/dev/CLAUDE.md`, `docs/dev/lanes/CLAUDE.md`, `docs/spec/CLAUDE.md` (the rxt_format entry rewritten to current facts) and `tests/spec_history/CLAUDE.md` are updated.

Dropped as history or as build-step tags (all in the record): the bracketed step and wave tags on productions and paragraphs, "since [REL-1.10]/D118", "addendum (iv)", the r46sem finding notes (FIXED, "previously omitted"), the "once thought to be a gap" aside, the "EARLIER versions stated ... DELETED" sentence, the "behaviour has always shipped; this sentence makes it a promise" rationale, the K75/K73 lane-report pointer, the Drift section. Dropped as measurements: "every file in tests/ is of that shape today", "no file in tests/ is head-bearing / carries an include line", "the corpus contains three such blocks", "make test's eight scripts". The wave and phase names the tool itself prints (`wave`, `# wave-built:`) stay.

## 3. Code wins: disagreements resolved (each checked by running `build/pcrec`, `tests/harness/run.sh` or `tests/harness/verify_rxt.py` on a probe file, or by reading `src/parse/rxt_source.c`)

1. Block `description |` (block scalar): the old text said the block scalar is a head form only and that `|` in a block is "refused by name". Live: `pcrec`, `run.sh` and `verify_rxt.py` all accept `description |` with indented lines in a pattern block. Stated as a property of any prose kind that carries `children: prose`, in the head and a block alike (sections 1.4.7 and 1.5).
2. `budget`: the old text said a repeated FIELD is not legal. Live: `budget steps=5` then `budget steps=6` is accepted by `pcrec` (the dump shows 6) and `run.sh` (last assignment wins). Stated as last-wins (sections 1.4.6 and 1.5).
3. `features only`: the old text said it is "parsed and recorded in this build; it becomes operative when config composition lands". Live: composition is built and `features only` replaces the configs' list (`rxt_source.c`, and the old text's own section on building said so). Stated as operative, and as a block-only line (a `config` body refuses it).
4. Composition list: the old text named `flags`, `encoding`, `engine`, `budget` as more-specific-wins and `features` as a union, and omitted `tune`, `analysis` (config-only; later-wins across `from`/`with`) and the `pcrec` raw lines (joined in order). Added from `cfg_merge` (section 1.3).
5. `oracle` engine grammar: the old text said the ENGINE half is an identifier with no `-` and no `.`. Live: `pcrec` takes a `defname` (`oracle pcre2-dfa` is accepted); `run.sh` and `verify_rxt.py` take only an identifier on a BLOCK's `oracle` line and refuse `pcre2-dfa`. Stated both ways (section 3.1). Reader disagreement: open question 1.
6. `oracle none <reason>`: a second spelling that `pcrec` accepts (a reason is required) and the old text did not mention; `run.sh` and `verify_rxt.py` refuse it on a block's `oracle` line (run.sh accepts it at file level through the dump). Added (section 3.1).
7. Duplicate target prefix: the old text said writing one prefix twice is refused with the older "duplicate target prefix" sentence "from the side where naming both definitions would say nothing new". Live: that sentence is for the same prefix written twice for the SAME definition; two targets with one prefix and different definitions get the collision diagnostic that names both. Stated precisely (section 1.3).
8. The example: its last case (`m "byte \x41 then newline\n" 5 6` under `pattern colou?r`) FAILS in `run.sh` ("expected match 5 6, got nomatch") and in `verify_rxt.py`. It sat in the old text unrun. The example now gives that case its own `pattern A` block; the whole example passes both harnesses (9 cases, ALL CHECKS PASSED).
9. `var`: the old text states the name grammar and the quoted value. `run.sh` and `verify_rxt.py` enforce both (`var 1x "v"` is refused); `pcrec` reads the line as a qualified line and accepts `var 1x "v"` and `var a b`. Stated as who enforces it (section 1.5). Open question 1.
10. `verify_rxt.py` and the head: the old text called the format's readers "three". `verify_rxt.py` refuses any file-level declaration by name ("a head-bearing .rxt file is not verifiable by this script"). Stated (section 0 paragraph 2).
11. `g` and `gp` operand checks: the old text called them "parse-time" failures. They are failures of `run.sh` and `verify_rxt.py`; `pcrec` accepts `g 1 0` and `g 0 0 1` with no preceding `m` (it does not read case operands). Stated as the harness readers' (section 1.5). Likewise `gu internal` is refused by `run.sh` and `verify_rxt.py`, not by `pcrec`.
12. `lib` row: the old text said the `"path"` form is refused if it names no readable file. Live: the refusal comes when a target is BUILT (`pcrec -o`), not from `--list-source` (which accepts `lib "nonexist.rxt"`). Stated (section 1.1).
13. Driver: the old usage line omitted the trailing `[var...]` bindings (`NAME=<escaped value>` set, bare `NAME` unset), the `unset-var` word, and that `PCREC_ERR_STARTPOS` prints `giveup -7`. Added from `driver.c` and `outcome_word.h` (section 5). Exit codes: the old text said `run.sh` treats `>=124` as a timeout; for a test binary it is exactly 124 (timeout) and `>=126` (crash); corrected (section 5).
14. "`utf8` is refused until milestone M5" (encoding bullet): stale; `utf8` is built. Reworded to "an encoding pcrec refuses is heard from the compiler".
15. "`tests/assertions/` is the one directory whose oracle rule differs by design": false (`verify_vars.py`, `verify_ucp.py` and others are own oracles). Reworded to "carries" and a pointer to tests/CLAUDE.md.
16. "Organizing tests by component": the ASCII tree listed 10 of the 55 directories under tests/ and described `bench/` as non-`.rxt`; replaced by a statement of the rule and a pointer to tests/CLAUDE.md.
17. The environment-variable list in the RXTROUTE/RXTFLAGS paragraph (eight names, "manual-only, nothing in make test sets them") is dropped: `run.sh`'s header now lists many more (`RXTDUMP`, `HARNESS_BATCH`, `LINTGEN`, ...) and the "nothing in make test sets them" claim was not re-verified. Points at the header and docs/testing.md.
18. Items checked and unchanged (re-run live): eleven head declarations and `version` RESERVED (`--list-schema`: 75 rows, wave-built 23, wave-reserved 999); the ten schema columns and two sections; the seven constraint kinds and `functional-binding` having no row; indentation is spaces (tab refused by name); NUL byte refused with the line; `pattern-esc` escapes, `\x00` refused naming K9; one space before `pattern`; tab in a `with`/`from` list refused; a second file-level `description` and a second block `description` refused naming the earlier line; `flags` letters `i` and `u`, each once; `engine vm` only; `tune` value set and refusals; `name` grammar and block-name uniqueness; the target prefix derivation and collision refusal; the derived-identifier call (`(?&cls_up)` reaches `name cls-up`; the hyphen spelling is refused; two definitions deriving one identifier are refused naming both); delivering calls and their refusals (no export, undeclared export, encoding mismatch, a local group, a repeated site, a flat clash); the three libpcre2 refusals of the delivering spellings, re-run against the installed libpcre2 (all three refused, the plain call accepted); `vocabulary` (empty and duplicate refused), `under` (closed convention, duplicate refused), `oracle` shape (slash with no version refused), `variant` rules, `provenance` rules (url forbidden when authored, required otherwise, adaptation iff not verbatim), the `analysis` rules (lowercase, row key grammar, canonical count, ascending keys, at most one block per (query, encoding), `bigram` refused, `markov1` and `run-rarity` unusable); `--list-source` columns (20) and the four sections' columns, a `pattern-esc` block as a `pattern` row with `esc`; `--list-source` refuses `-o`; the `mc` counts (`(?=a)` over `xax` is 1, `a*?` over `aaa` is 4, and the four ill-formed UTF-8 counts); the harness summary lines and `[resolution]` class; the `include` refusals; the `@file:` and mode-`count` driver forms; `--engine=vm` disabling the prefilter (`no-engine-vm`).

Owed items: none.

## 4. Claims ledger

SUPERSEDED = not the live behaviour (section 3); HISTORY = a dated, step or finding statement moved to the record; N/A-DROP = a count or measurement not stated; POINTER = pointed at another doc. "new" is the new label in the doc (paragraph numbers are generated; the section is given).

| old section | claim | new |
|---|---|---|
| title, intro | scope; three readers; the reader wins on disagreement; battery composition is process record | 0 (the "see Drift" pointer HISTORY; verify_rxt head scope added) |
| The .rxt format | head and body; the head ends at the first block opener; no head; a head with no blocks is a distinct observable | 1 (the "every file in tests/" sentence N/A-DROP) |
| The head | the eleven declarations table | 1.1 (lib/target/include/analysis rows reworded; step tags HISTORY; `lib` refusal at build SUPERSEDED, item 12) |
| The head | config body lines; `analysis` resolved and later-wins; `pcrec` line rules | 1.1 para 3 |
| The head | NOT IN THIS BUILD derived list, withdrawn productions, `version` | 1.1 paras 4-5 and 1.13 (the two duplicate paragraphs folded into one pointer) |
| The delivering call | the four forms, the five bullets | 1.2 |
| Building from a source file | target definition, prefix, derivation, collision, no-target outcomes, union and more-specific-wins, harness control | 1.3 (composition list SUPERSEDED, item 4; duplicate-prefix sentence SUPERSEDED, item 7; the "has always shipped" rationale HISTORY) |
| Lexical rules | the two layers | 1.4 |
| S0-S3, open subtree | line classes, attachment, grouping, opaque regions, dedent, open subtree | 1.4.1-1.4.5 (the asymmetry-deleted sentence HISTORY) |
| The SCHEMA layer | kind-by-token, cardinality, seven constraint kinds, when answered | 1.4.6 (repeated budget field SUPERSEDED, item 2) |
| The SCHEMA layer (bullets) | trailing whitespace, tab in a list, one space, block scalar | 1.4.7 (finding notes HISTORY; block scalar SUPERSEDED, item 1) |
| (bullets) | comments, `pattern`, NUL | 1.5 |
| (bullets) | `pattern-esc`, K9, the dump-value seam | 1.5 |
| (bullets) | `flags`, `features`, `perr`, `m`/`n`/`ms`/`ns`, `g`/`gp`/`gu`, `var`/`var-unset`, `name` and its sub-rules, `description`, `encoding`, `export`, `features only`, `tune`, `engine`, `budget`, `frames-buffer=` | 1.5 (items 1, 2, 3, 9, 11, 14) |
| (bullets) | the seven more block lines; RXTROUTE/RXTFLAGS | 1.5 (list of env vars N/A-DROP, item 17) |
| (bullets) | the subject escape table | 1.5.1 |
| Named subjects | `@file:`, `as`, `sha256`, who checks | 1.6 |
| mc | the counting rule, empty-match advance, ill-formed UTF-8, the two stray-byte rules | 1.7 (K75/K73 tags and lane pointer HISTORY) |
| under | the second answer per convention | 1.8 |
| provenance | the eleven-field record, per-parent split | 1.9 |
| analysis | the bundle, data block, `serves`, `row` grammar | 1.10 (`bigram` sentence now a fact) |
| variant | the sub-block, rules | 1.11 |
| ext | the aux production, the graduation rule | 1.12 (the dangling "section 2.27" pointer dropped) |
| The schema and its surface | the dump, ten columns, `value` shape, `#section surface`, `version` | 1.13 ("SEVENTH registry surface" N/A-DROP; W23-S3 test name dropped) |
| clause spellings | `closed`, `closed per-key`, `required-if`/`forbidden-if`, `parent`, ` and ` | 1.13.1 |
| Example | the example | 1.14 (last case SUPERSEDED, item 8) |
| --list-source | the 20 columns, the added kinds, pattern-esc, what is reported, the four sections, validation, `kind`, `engine` column, escaped columns, AS WRITTEN, the sectionless main table | 2, 2.1 (the "once thought a gap" aside and the superseding narrative HISTORY; `--resolved` stated as a fact) |
| Oracle verification | python `re`, ASCII, `# pcre2-only`, own-oracle directories | 3 (item 15) |
| oracle | the declaration, engine-ref, version, skip, method | 3.1 (items 5, 6) |
| How the harness evaluates a block | the five steps, the head call, include and the accounting unit, the summary lines | 4 (two MEASURED sentences N/A-DROP) |
| The driver protocol | usage, `@path`, mode, steps 1-7, exit codes, bounds, the usage note | 5 (items 13, 14) |
| Organizing tests by component | the tree, the roster pointer, adding a directory | 6, 6.1 (item 16) |
| Drift found and fixed | three drift notes | HISTORY (the three facts they led to are already in 1.5 and 5) |

## 5. Citations re-pointed and checks that read this doc

- Line-number citations of the old text (61 sites outside `studies/specclean/`, which the cite scan skips) were re-pointed to section citations by quote: docs/design/dd13_format (bench_rxt_needs_v1.md 33, CLAUDE.md 3, w23_impl.md 3), docs/design/encoding_data_layout.md, docs/design/findings/design.md, docs/dev/lanes/CLAUDE.md and four lane reports, docs/dev/reviews (r46 11 sites, r56), and one comment in tests/rxtsource/run_rxtsource_tests.sh. Because those sites cited a snapshot of the doc from August and September, each was re-pointed to the section that now holds the statement it quoted (the mapping was by the quoted text), not by arithmetic. One site (findings design, the B0 hunks) was reworded so the scan does not read "design section 14" as a section of rxt_format.md. Four sites wrote the line form with a colon outside the backticks (`rxt_format.md`:458-474 in oracle_interface.md, design/CLAUDE.md, the oraiface report and a docstring in `tests/oracle/oracle_store.py`) and the scan does not see that form; they were re-pointed too (section 2.1).
- File-only and quoted-title cites in the spec tier now carry sections: registry.md, cli.md (four sites), findings.md (two), limits.md, match_api.md (two), table_contract.md (two). One hunk each.
- Not edited: `memfn/docs/responses.md` and `requests.md` (append-only ledgers; the scan passes without edits). Not edited, by design: lane reports and design notes that quote a section by its old TITLE (for example "The head" or "the .rxt format") rather than by number (the titles still exist as headings); the `SAB_DOC_FIGURE` strings in S241, S244, S290 and S291 (they name sections by title, which still match); comments in `tests/harness/verify_rxt.py`, `tests/quoting/d27/checker.py` and a rxtsource fixture that quote "Blank lines are ignored" and similar sentences; and `src/dump/schema_dump.c:74`, which is `--list-schema`'s own output text (a pinned surface row) and names the file without a section.
- Checks that read this doc's literal text, found by grep over tests/, scripts/, Makefile and docs/testing.md: none. `tests/lib/spec_extract.sh` and the `value-set` markers belong to match_api.md only. The rxtsource suite, the schema-surface checks (`--list-schema` against the compiled table) and the mech rows S241/S244/S290/S291 read `pcrec`, the fixtures and the schema, never the markdown; the only mentions of the doc in those scripts are comments and `SAB_DOC_FIGURE` strings. The reads that DO exist are `tests/spec_history/` (markers, numbering, contents, citations), which this lane ran.
- `tests/spec_history/baseline.tsv`: the three rxt_format rows removed. `cite_floors.tsv`: rxt_format 34 (half of 69 measured); the header comment records the 69.

## 6. Open questions (not resolvable by reading the code; not guessed)

1. Reader disagreements the schema says should not exist. `oracle` engine grammar (item 5 of section 3) and `var` (item 9) differ between `pcrec` and the two harness readers; `oracle none <reason>` (item 6) is accepted by `pcrec` and refused by `run.sh` and `verify_rxt.py` on a block's line. The schema rows say `oracle`: validated_by `pcrec` (so no cross-reader claim) but `var` and `var-unset`: `all-readers`, whose fixture evidently does not cover `var 1x "v"`. The spec states what each reader does; whoever owns the readers should decide which side moves.
2. `src/dump/schema_dump.c` and the `--list-source` header comment in `src/parse/rxt_source.c` cite `format_design.md` section 2.27 and similar design-note numbers in their output text. Listing output text, left.
3. `docs/spec/CLAUDE.md`'s `tuning.md` entry still carries dated bracketed narrative (the sibling lane spectune owns it).

## 7. Validation

Run LAST, after this report was written (the scan reads it). Verdict lines are appended below by the lane.
