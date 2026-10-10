# Lane specsmall: facts_listing.md, ir_listing.md, findings.md facts-only rewrite, `-i` help wording (report)

Lane specsmall (sonnet), branch `lane/specsmall` off main `736005f5`, 2026-10-10. Plan row `[SPEC-CLEAN]`, the next three docs in density order, plus two owed items. Method: the speclim and specreg lanes. Not done here: docs/dev/plan.md (the manager's, at merge); full `make test`, mech, test-axes, san (box hold; lane lfl0 owns the box).

Citation note for readers of this report: numbered docs are cited below in words ("section 4 of findings.md"), because the tree-wide citation scan reads a literal section-sign citation in any tracked file, this one included.

## 1. Survey, before and after

Counted by `tests/spec_history/spec_history.py` (marker lines outside fenced code; "before" = the baseline rows removed).

| file | lines before | marker lines before (date/addendum/walkback/narrative/tagopen) | lines after | headings | paragraphs | marker lines after |
|---|---|---|---|---|---|---|
| facts_listing.md | 171 | 7 (4/1/1/0/1) | 125 | 11 | 49 | 0 |
| ir_listing.md | 228 | 8 (2/2/2/1/1) | 159 | 13 | 33 | 0 |
| findings.md | 308 | 3 (1/0/1/0/1) | 229 | 15 | 54 | 0 |

No allowlist rows were needed. All three carry the generated contents block (`scripts/spec_toc.py --init`) and the numbering, produced by the unmodified `studies/specnum/number.py` over a hand-written draft (the drafts are in the session scratchpad, not committed; the result is the document).

Numbering decisions:
- findings.md keeps its old top-level numbers: sections 1 (terms), 2 (data), 3 (normalization), 3a (the code-point derivations, kept as section 3a because the frozen records and a design note cite it by that number), 4 (readers), 5 (stamp), 6 (shipped analyses and store), 7 (resolution), 8 (listings), 9 (library). The old section 3's test vectors are now 3.2, the normalization 3.1; the listings are 8.1-8.3. Old section 4 keeps both its tables (24 inbound citations of section 4 still name the readers).
- facts_listing.md and ir_listing.md had unnumbered headings, so numbers are new: facts_listing 1 what it is, 2 query, 3 framing, 4 sections (4.1 `facts` with 4.1.1 status, 4.1.2 value, 4.1.3 why; 4.2 `decisions`), 5 guarantees, 6 not promised. ir_listing 1 what it is, 2 framing, 3 sections (3.1 `summary` with 3.1.1 the `prefilter` vocabulary and 3.1.2 `prune-ceiling`; 3.2 `slots`; 3.3 `rungs`/`strategies`/`pruning`; 3.4 `program`; 3.5 `choicepoints`; 3.6 `islands`; 3.7 `callouts`), 4 consuming it.

## 2. History moved (frozen)

`docs/dev/history/facts_listing_record.md`, `ir_listing_record.md`, `findings_record.md`: the COMPLETE old text of each doc, verbatim, under a short header. The same text is in git at `736005f5`. `docs/dev/history/CLAUDE.md`, `docs/dev/CLAUDE.md`, `docs/dev/lanes/CLAUDE.md`, `docs/spec/CLAUDE.md` (the three entries rewritten to current facts) and `tests/spec_history/CLAUDE.md` are updated.

## 3. Code wins: disagreements resolved (each checked against a live `build/pcrec` of this branch or the source)

1. ir_listing: "one of the nine tokens" for `prefilter`, with eleven rows in the table beneath it. The source table (`src/opt/select_engine.c` admission rows plus the two `yes` arms in `src/gen/emit_vm.c`) has eleven tokens and tuning.md already says eleven. Stated as eleven (section 3.1.1).
2. ir_listing: the `prefilter` table order is not the emitter's test order. The emitter's order is backref, linked-call, var, nullable-exact, nullable-collapsed, overflow-drop, size-dropped, forced-on, forced-off, default. The spec states the rule (construct and analysis routes before the flag routes) and not a row order; the table is a vocabulary.
3. ir_listing: `rungs` and `strategies` summary values were not enumerated. Added from source (`cursor`, `frames-bounded`, `frames-unbounded`, `revdet`, `counter`; `possessive`, `backtracking`), an addition, not a disagreement.
4. ir_listing: "A DFA/prefilter listing section is future work; `--emit-dot` is unbuilt" is planning state; the facts (no such section, no `--emit-dot`; a DFA-engine pattern is refused naming `--engine=vm`) remain. Re-run live: the refusal text is unchanged. The "D77-gated real IR" paragraph is design direction and is not carried.
5. ir_listing: `prune-ceiling` `none` for `-fno-length-prune`, `possessify` EMPTY under `-fno-possessify`, `step-budget` EMPTY under `--fno-step-budget`: re-run live, all hold. The callouts section is empty on every artifact (live note: module `callouts` has no producer).
6. facts_listing: the section-name API said a `rate` section is "reserved for [FINDINGS] B1". Live prints `facts` and `decisions` only; stated as "no other section is printed". The reservation was planning state.
7. facts_listing: the `why` reason names `decline:not-end-anchored` and `decline:gstart` were absent from the doc; the source (`src/dump/facts_dump.c`) has them and they are listed (the doc already said reason names are advisory).
8. facts_listing: `--emit-facts` "composes with no other query mode" re-run live (`--emit-facts --emit-ir` is refused as separate queries; `-o` is refused). Stated for both listings.
9. facts_listing: value spellings re-read against `pcrec_fact_render` (`src/facts/facts.c`): kinds order, `start_set` as `nullable` or count plus 64 hex digits, `run_pin` `o` or `o:at+len`, `req_run_maxoff` `unbounded`. All match; the `since` and step-tag asides are dropped.
10. findings: the kinds table had a `built` column (B1/B4/B5) and the preamble said the document grows by step. Dropped as planning state. The code fact is that the `bigram` kind is in the vocabulary (`find_derivs[]`, `--list-analyses` column order) but the `.rxt` reader refuses a `bigram` block ("not an analysis-bundle directive"), so no `run-rarity` answer exists. Stated in section 2, and section 8's resolution rows show `run-rarity` as none (live).
11. findings: corpus byte counts for `weblog` (1,000,000) and `log` (999,960) are measurements of vendored data, not contract; dropped. The corpus identity, licence and "synthesized" fact stay (`--list-analyses` prints source, licence, retrieved).
12. findings: the three test-vector rows re-computed with an independent script (3,970 and 3,906 with R = 64; 999,490 and 2; 999,490 and 2 with R = -509): unchanged. The default's stamp `1822fb973b95a4da` re-read live: unchanged.
13. findings: the five limits (`PCREC_MAX_FIND_COUNT` 2^40, `PCREC_MAX_FIND_CPFREQ_ROWS` 65,536, `PCREC_FIND_FLOOR_PPM` 2, `PCREC_MAX_FIND_CHAIN` 8, `PCREC_MAX_FIND_BUNDLE_BYTES` 1 MiB) re-read from `--list-limits` (anchor 3.7): unchanged.
14. findings: a fact the old text did not state, added after a live run: `--analysis` with a compile query such as `--emit-facts` is refused ("applies to a compile ... or to --list-analysis FILE only"). Stated in section 7.
15. findings: resolution rules (name charset, the three stops, include-next, terminal by identity, the failure table) are exercised by `tests/findings/` (fixtures 1-22); not re-run here (the findings suite is multi-process). Re-read, not re-measured; `--analysis Foo` and `--analysis nosuch` refusals re-run live and match the table.

Owed items:
16. `-i` (owed item 1). `--help` said "(ASCII letters)". Verified by compiling and running matchers: `-i -e byte 'k'` matches `K` only as ASCII; `-i -e byte '\xe9'` does not match `\xc9`; with `--features all --ucp` it does (Latin-1 pairs); `-i -e utf8 'k'` matches U+212A (a 3-byte match). The `--help` entry in `cli/main.c` now says the fold follows the encoding (byte: ASCII letters, plus the Latin-1 pairs under `--ucp`; utf8: Unicode simple case folding). `cli.md` section 1.8's table gained a `byte` plus `--ucp` row and the `byte` row says "without `--ucp`". No test pins the help text (grepped tests/); `--help` is not emitted artifact text, so no `abi` event.
17. `tests/registry/CLAUDE.md` (owed item 2). The drift note said "138 ... 128 ... 100 at Q2/SR-9". What `registry_check.c` does: one exact `total != N` test (142 today) that moves with every added or removed row. The file now says that and states no number; the second place that said "iterates all 118 rows (100 when written ...)" now says "every registry row".

## 4. Claims ledger

SUPERSEDED = not the live behaviour (section 3); HISTORY = a dated, ruling or step statement moved to the record; N/A-DROP = a count or measurement not stated; POINTER = pointed at another doc, kept as a pointer. "new" is the new label in the doc.

### facts_listing.md

| old section | claim | new |
|---|---|---|
| header | step dates, rulings, the rows added by step | HISTORY |
| header | conforms to table_contract; cli.md is the flag entry; design is informational | 0 para 1 |
| What it IS | debug listing, status as ir_listing, no `abi` number | 1 para 1 |
| What it IS | what it prints; decision stamps are route decisions the record lacks | 1 para 2 |
| What it IS | reads the record, same renderer as the stamps, final attempt only | 1 para 3 |
| What it IS | not VM-only | 1 para 4 |
| The query | form, no `-o`, ordinary compile, options apply, `=ENC,...`, refusal | 2 paras 1-5 (composes with no other query mode: live) |
| Framing 1-6 | table contract, named sections, name set append-only, escaping, width, no trailing `#` line | 3 items 1-6 (the `rate` reservation SUPERSEDED, item 6 of section 3) |
| `facts` | one row per fact per encoding; forced asks after the artifact | 4.1 para 1 |
| `facts` | the column table (promised flags) | 4.1 table |
| `facts` | status vocabulary | 4.1.1 |
| `facts` | value spellings | 4.1.2 (the since-tags dropped, HISTORY) |
| `facts` | why grammar and tokens | 4.1.3 (two reasons added from source) |
| `facts` | "Facts emptied" lines checked by run_facts_checks.sh | 4.1.3 closing paragraph |
| `decisions` | one row per value stamp, machinery macros excluded | 4.2 |
| Guarantees | three guarantees | 5 items 1-3 |
| Not promised | names, spellings, reason names, note; resolve by name | 6 |

### ir_listing.md

| old section | claim | new |
|---|---|---|
| header | step date and ruling tags | HISTORY |
| IS and is not | debug listing; control structure complete, operands lossy | 1 para 1 |
| IS and is not | not an IR; byproduct of the emitter's walk; the real-IR paragraph | 1 para 2 (the real-IR / gated paragraph N/A-DROP, design direction) |
| IS and is not | VM-only, refusal naming `--engine=vm`; DFA listing and `--emit-dot` future | 1 para 3 (future-work wording SUPERSEDED to a fact) |
| IS and is not | derives from the VEvent stream | 1 para 4 |
| Framing 1-8 | contract applies; named sections incl. program; width; name set; escaping; multi-valued cells; no trailing `#`; preamble | 2 items 1-8 (nine section names listed from source) |
| summary | the fact/value table | 3.1 table (rungs and strategies vocabularies added) |
| summary | the prefilter vocabulary | 3.1.1 (nine tokens SUPERSEDED: eleven; row notes' tags dropped) |
| summary | prune-ceiling and the stamp | 3.1.2 |
| slots | layout, families, one row per family, group pair, revdet triple | 3.2 paras 1-5 |
| rungs, strategies, pruning | per-quantifier views, empty population, per emitted vs per source | 3.3 paras 1-4 |
| program | the op table, append-only op set, events in own sections only | 3.4 |
| choicepoints | one row per push, preference order | 3.5 |
| islands, callouts | counts, empty populations, no callouts producer | 3.6, 3.7 |
| Consuming it | `tests/lib/table.sh` functions; no fixed-position grep | 4 paras 1-2 (the D106 history sentence HISTORY) |
| History | first-version note | HISTORY |

### findings.md

| old section | claim | new |
|---|---|---|
| header | status line, steps B1/B2/B5, "where not built it says so", design record | HISTORY (design pointer kept, 0 para 1) |
| header | the one promise: speed, never answer or give-up | 0 para 2 |
| 1 Terms | the terms table | 1 |
| 2 The data | counts not rates, the kinds table (built column) | 2 table (built column HISTORY; bigram status from code, item 10 of section 3) |
| 2 The data | serves line is the whole selection rule; one block per (query, encoding); count ceiling | 2 paras 3-5 |
| 2 The data | the chain, `default` as terminal, the `utf8` NONE under default | 2 paras 6-7 |
| 3 unigram | the five normalization steps; integer arithmetic | 3.1 |
| 3 unigram | test vectors | 3.2 (re-computed, item 12) |
| 3a | `encode-utf8`, `encode-latin1`, the drop and the refusal, the row cap, why a code-point kind | 3a paras 1-6 |
| 4 | the three NONE-answer kinds and the reader table | 4 (the K65/K66 tags dropped, HISTORY; the since-tags dropped) |
| 5 | stamp grammar, digest bytes, `rx_info.findings`, disclosure, default change moves the digest | 5 |
| 6 | the shipped default and the store; gen-findings; the generated `log` and `weblog` | 6 (corpus byte counts N/A-DROP, item 11) |
| 7 | naming, fill-only, the three stops, include-next, terminal by identity, answering, eager | 7 (refusal with other query modes added, item 14) |
| 7 | failure table | 7 table |
| 8 | `--list-analyses` columns, rows digest | 8.1 |
| 8 | `--list-analysis NAME` sections | 8.2 |
| 8 | `--list-analysis FILE` sections | 8.3 |
| 9 | the three `pcrec_options` fields; the library parses | 9 |

## 5. Citations re-pointed and checks that read these docs

- Line-number citations of the old texts were re-pointed to section citations (12 sites in docs/design, docs/dev/reviews, docs/dev/lanes, one comment in tests/base/opt41_rung_nullable_decline.rxt). Cites in tuning.md, match_api.md, cli.md and table_contract.md that named these docs by file only now carry a section (a one-hunk spec change each).
- False positives of the scan (about 30): a bare word "findings" followed by a section sign in design notes, lane reports, tests/findings references, two sabotage rows' comment and `SAB_DOC_FIGURE` strings, two third_party PROVENANCE notes, src/findings/CLAUDE.md and tests/mech/CLAUDE.md. They name the findings DESIGN or the findings TEST SUITE sections, not findings.md. Each was reworded in place (the section sign became "sec."), as speclim did; a few (the decfbB3 and plan_completed sentences about five or four lane results) were reworded to "results". The sabotage scripts' edits touch comments and the `SAB_DOC_FIGURE` record only, not anchors or the planted text.
- Not edited: `memfn/docs/responses.md` and `requests.md` (append-only ledgers; the scan passes without edits).
- Checks that read these docs' literal text, found by grep: `tests/lib/spec_extract.sh` and the `value-set` markers belong to match_api.md only. `tests/codegen/run_ir_listing.sh` and `run_facts_checks.sh` parse the LISTINGS by header name through `tests/lib/table.sh`; they name the docs only in message strings and comments and read none of their text. `run_facts_checks.sh` reads tuning.md's "Facts emptied" lines, not facts_listing.md. `tests/findings/findings_ref.py` cites findings sections 3 and 5, which still hold the normalization and the stamp. Nothing needed re-pinning.
- `tests/spec_history/baseline.tsv`: the 12 rows of the three docs removed. `cite_floors.tsv`: facts_listing 4, ir_listing 3, findings 53 (about half of the 8, 7, 107 measured; the ir_listing and facts_listing counts are small because most readers cite them by file name; the file-only cites in the specs now carry sections).

## 6. Open questions (not resolvable by reading the code; not guessed)

1. `src/dump/findings_dump.c` prints `docs/spec/findings.md` section 6 in the `--list-analyses` header comment, and `cli/main.c` cites the same section for the two listings. The number resolves (section 6 is the store the listing lists) but the listings' own text is section 8. Left: it is listing output text (a pinned comment line in `tests/findings/` goldens is possible) and a comment in `cli/main.c`; whoever owns them can point it at section 8.
2. `src/core/findings.c` carries a comment "(`bigram`, B4) is still the spec-stated vocabulary"; the spec now states the vocabulary-only status, so the comment is accurate and left.
3. `docs/spec/CLAUDE.md`'s `tuning.md` and `rxt_format.md` entries still carry dated bracketed narrative (other docs' entries; baseline debt of those docs).
4. `--help`'s `-i` wording owner: the `--help` text is changed here under the lane's brief; if `README.md` or a guide quotes the old help line it was not found by grep (docs/guide/encodings-and-subjects.md already states the per-encoding fold).

## 7. Validation

Run LAST, after this report was written (the scan reads it). Verdict lines are quoted in the handback message and appended below by the lane.
