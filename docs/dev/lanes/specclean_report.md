# Lane specclean — match_api.md facts-only rewrite (report)

Lane: specclean (opus), branch `lane/specclean` off main `aee1a570`,
2026-10-09. Plan row `[SPEC-CLEAN]`. Brief: survey history density across
docs/spec; rewrite `docs/spec/match_api.md` as a facts-only contract; move the
history to `docs/dev/history/`; a claims ledger as the safety net; re-point
every inbound citation; a cheap check against recurrence.

## 1. Survey: history density of every docs/spec/*.md (as found, at aee1a570)

Counted by `tests/spec_history/spec_history.py --survey` (lines carrying a
marker, outside fenced code; empty allowlist), plus raw word counts:

| file | lines | date | addendum | walkback | narrative | tagopen | marker lines | per 1k | raw `was` | raw RULED/ruling | raw `[TAG]` lines |
|---|---|---|---|---|---|---|---|---|---|---|---|
| match_api.md (old) | 5807 | 139 | 8 | 73 | 38 | 60 | 318 | 54.8 | 188 | 18 | 310 |
| registry.md | 720 | 24 | 0 | 11 | 23 | 5 | 63 | 87.5 | 24 | 13 | 50 |
| table_contract.md | 174 | 8 | 0 | 0 | 3 | 2 | 13 | 74.7 | 6 | 2 | 15 |
| limits.md | 1161 | 17 | 1 | 6 | 5 | 19 | 48 | 41.3 | 13 | 9 | 59 |
| cli.md | 1365 | 25 | 1 | 10 | 7 | 13 | 56 | 41.0 | 13 | 8 | 64 |
| facts_listing.md | 171 | 4 | 1 | 1 | 0 | 1 | 7 | 40.9 | 2 | 1 | 5 |
| ir_listing.md | 228 | 2 | 2 | 2 | 1 | 1 | 8 | 35.1 | 5 | 1 | 12 |
| tuning.md | 4336 | 53 | 5 | 34 | 24 | 30 | 146 | 33.7 | 56 | 30 | 171 |
| findings.md | 308 | 1 | 0 | 1 | 0 | 1 | 3 | 9.7 | 4 | 0 | 5 |
| rxt_format.md | 1764 | 0 | 0 | 4 | 1 | 3 | 8 | 4.5 | 16 | 2 | 23 |
| vars.md | 170 | 0 | 0 | 0 | 0 | 0 | 0 | 0.0 | 1 | 0 | 0 |
| **match_api.md (new)** | 3140 | 0 | 0 | 0 | 0 | 0 | **0** | **0.0** | 44 | 1 | 11 |

The new doc's remaining raw `was`/`[TAG]` hits are present-tense prose ("was
attempted", "was REFUSED" in the quoted emitted block) and verbatim emitted
text or plan-row/test-section pointers; its two marker hits ("walk back to the
run's first row", "D47 second addendum") are allowlisted with reasons.
Follow-ups (filed, not done here): registry.md, table_contract.md, limits.md,
cli.md, facts_listing.md, ir_listing.md and tuning.md each want the same
treatment, in that order of density; `docs/spec/CLAUDE.md`'s other entries
also carry revision narratives (it is an index, not scanned by the check).

## 2. The rewrite

`docs/spec/match_api.md`: 5,807 → 3,140 lines, organized by topic, each topic
in one place, 151 explicit `<a id>` anchors (every section and every stamp).
Top-level numbering is kept where the topic stayed, so most `§N` citations
still resolve: §1 namespaces, §2 ABI types (re-quoted verbatim from a fresh
abi-71 build), §3 entries (§3.1 search + the find-all loop — the emitted
`<prefix>_next_pos` comment cites "match_api.md S3.1", so it must stay there —
§3.1.1 next_pos, §3.1.2 valid_upto, §3.2/§3.3/§3.4, §3.5 give-ups across
entries, §3.6 the `(?:P)\z` idiom), §4 give-up and refusal codes (with a
limits cross-reference block), §5 captures and groups (§5.3 concurrency incl.
old §10.5's clause, §5.4 named groups incl. old §6.0, §5.5 composition), §6
`rx_info` field by field (a 28-row table with mirrors) + the `abi` rule +
flags, §6.1 placement, §6.3 stamps (scoping rules, a 51-row inventory table,
one anchored entry per stamp, every value set a table), §7 NUL, §8 library,
**§9 encodings and character positions (new: the startpos/K50/align/offset-0/
-futf-check/engine-positions material that was spread through old §3.1 and
§8.2)**, §10 the `_in` entries and the tiered default (old §3's [OPT-1] cost
model merged into §10.9). Old §9 (provenance/pre-v1) is now the preamble's
`#pre-v1`; old §6.2 is `#rx-info-counts`; old §3.5's history went to the record.

Cite by anchor: `docs/spec/match_api.md#find-all`. The preamble says so
(`#citing`) and docs/spec/CLAUDE.md repeats it.

## 3. History

- `docs/dev/history/match_api_record.md` (frozen, 1,951 lines): 134 blocks of
  the old text, verbatim and in order, each tagged `[old §X, lines a-b]` —
  every paragraph the check's markers flag, plus the header's revision notes,
  old §3.5, old §9 and old §10's status box; plus docs/spec/CLAUDE.md's old
  `match_api.md` entry. Full old text: `git show aee1a570:docs/spec/match_api.md`.
- `docs/dev/history/abi_changelog.md` (LIVING): the `abi` change log, old
  lines 2309-3553 verbatim. **RULING ASKED** (message to team-lead): D76
  addendum [REVW.A1] named match_api.md §6 its only home; I moved it and
  re-pointed the readers that name its home (`src/gen/emit_dfa.c`'s comment,
  `src/gen/CLAUDE.md` ×2, `tests/codegen/run_codegen_tests.sh`'s comment). The
  spec keeps the current number (`#abi`, "71"), the guard text and the bump
  rule. decisions.md is untouched: if ruled, D76 wants an addendum-2 line
  ("the log moved to docs/dev/history/abi_changelog.md; a bump adds its entry
  there and updates the spec's number sentence"). If ruled the other way, the
  log goes back as a marked non-normative appendix and the check needs an
  allowlist block.
- `docs/dev/history/CLAUDE.md` new; docs/dev/CLAUDE.md lists `history/`.

## 4. Claims ledger — `studies/specclean/claims.tsv`

2,187 normative claims extracted from the old text BEFORE the rewrite (seven
sonnet extractors by line range; kinds N 1,649 / M 154 measured / H 384
current facts found inside history blocks), each mapped against the new doc by
eight sonnet mappers, then every UNMAPPED/SUPERSEDED row resolved by me
(`resolutions.tsv`; `build_ledger.py` assembles and fails on any unmapped row
or unfound locator; draft line numbers carried to the final doc by a difflib
alignment, spot-checked).

| status | rows | meaning |
|---|---|---|
| MAPPED | 1,989 | the new doc states it (line + anchor) |
| POINTED | 67 | the new doc defers it, at that line, to another spec doc that states it |
| SUPERSEDED | 37 | the old claim is not the live behaviour; the new line states the live one, with evidence |
| HISTORY | 49 | on re-reading, a past-state statement, not a current fact |
| INTERNAL | 26 | true but an internal emitted-code detail; mapped to §1's new internals clause |
| ELSEWHERE | 19 | a fact owned by another spec doc (tuning.md, ir_listing.md, vars.md, cli.md, findings.md, facts_listing.md), with its file:line |
| **UNMAPPED** | **0** | |

## 5. Doc defects found (old text vs code — the code won; each verified by probe or src)

1. §2's "verbatim" ABI block lacked `rx_var` and `rx_ctx.vars`/`nvars` (abi 32),
   and §1 counted SIX fixed-literal types; there are seven.
2. §3: "five entries" / "eight is what an artifact exports" — nine per-artifact
   symbols (`<prefix>_valid_upto` was never counted).
3. §4/§6.3 named `<PREFIX>_BT_FRAMES` as a live macro / `frame_capacity`'s
   mirror; nothing emits it — it is `<PREFIX>_RESUME_FRAMES`.
4. §6.3 quoted `RX_SIMD_GUARDED_BYTES 0ULL`; the emitter writes
   `0x0000000000000000ULL`.
5. §6.3: ".h carries nineteen `#define`s, VM .c twenty-six" — 29 in the .h.
6. §6.3: "six of rx_info's fifteen fields have a macro" — the struct has 28.
7. §3.4/§6.1: "104-byte object, exactly two relocations" — 200 bytes, seven
   (one per non-NULL pointer member).
8. §8.2: "all nineteen members" listed twenty; `pcrec_options` has 25
   (`analysis`, `analysis_dirs`, `analysis_source`, `analysis_source_len`,
   `memfn` missing). Now quoted and glossed.
9. §6: `prefilter` "one of the nine" DFA values / a hybrid's "same five" —
   eleven.
10. §6: the emitted `.engine` comment "reads `PCREC_ENGINE_DFA=1 /
    PCREC_ENGINE_VM=2`" — it reads `/* PCREC_ENGINE_VM */`.
11. §6.3 `_VM_PREFILTER_LANG`: "count-collapsed ⇒ subject-end, the same
    consequence an atomic group or lookaround already has" — false for those:
    `xy(a+)(?>b+)c` reads `"prefilter-window"`, `xy(a)(?=b)bc` `"none"`.
12. §6.3 `_FAST_FRAMES`: "a consumer distinguishes the single-tier causes via
    rx_info.flags" — `-fno-tiered-entry` is masked out of flags.
13. §6.3 `_ENGINE_SEL "size-cap-retry"` row named non-existent stamps
    (`<PREFIX>_PREFILTER_LANG_WHY "count-collapsed"` beside `_DFA_PREFILTER`);
    the live fact is `RX_VM_PREFILTER_LANG "count-collapsed"`.
14. §6.3 `_VM_CLS_FOLDS`: "the DFA route never consults the byte-fold row" —
    a DFA scan edge does at `--tune=-2/-1` (`RX_DFA_SCAN_EDGE "fold"`).
15. §6.3: "(b) VM-only ... and the frame/trail sizes" and "everything but
    RX_ENGINE is VM-only" — the sizing macros and ~20 stamps are on every
    artifact.
16. §6: `nnames` = "the PRIMARY pattern's rows" — on a composed artifact it
    counts caller-scope rows including flat imports (probe: ngroups 1, nnames 2).
17. §6.3 `_VM_FRAMELESS 1` ⇒ "the eight statics carry always_inline" — only
    under the `inline`/`forward` entry shapes (`shared`: seven; `plain`: none).
18. §6.3 `_RUN_WORDS` counted "the overlap row" only — also the `words` row.
19. The abi log's S4 C1 entry: run compare in `src/gen/runcmp.c` — it is
    `memfn/src/runcmp.c`.
20. UNDOCUMENTED exported, header-declared symbols: `<prefix>_span_match`,
    `<prefix>_span_match_caseless`, `<prefix>_var_valid` (now listed in §3 as
    non-entry residual helpers). Stamps never described in old §6.3's body:
    `<PREFIX>_TUNE`, `_VM_PRUNE_CEILING`'s value set (`none`/
    `prefilter-window`/`subject-end`, from `src/gen/emit_vm.c:11618`),
    `_VM_ROOT_MINW` and `_VM_CALL_*`'s scopes (conditional; from code).
21. Stale header notes ("abi is 27", "byte is the only encoding").
22. 10.6's table: 800 KB row 0.056 s / 88 MB vs the re-measure 0.057 / 90 MB
    the same section quoted; the new table carries the re-measure (a mapper
    re-ran it: ru_maxrss 89.6 MB).

NOT fixed here (outside a doc-only lane; filed as follow-ups):
- **Emitted-comment staleness** (fixing it is an `abi` event): the emitted
  `rx_info` member comments say `prefilter` is "the DFA's five values" and
  `nentries` "equal on every artifact pcrec emits today" (false on composed
  artifacts); the `rx_matchfn` comment carries history (`[DD-14] wave A commit
  2`). The new spec says the emitted member comments are glosses and the table
  in §6 is the contract.
- **`lib/pcrec.h` comments**: `frame_capacity` still names `<PREFIX>_BT_FRAMES`;
  `step_budget`/`work_budget` name `<PREFIX>_ERR_STEPS`/`_ERR_WORK` (pre-[ABI-NS]).

Measured numbers carried from the old text were NOT all re-measured: those in
the defects list were, and the mappers probed the rows they marked SUPERSEDED
or CHECK (e.g. -O2 frame sizes 3,184 / 131,216 / 144, the mmap RSS). The
claims ledger's notes name each probe.

## 6. Inbound citations

1,356 citation occurrences in 341 files (forms `match_api.md:N`, `§N`, `SN`,
`SSN`, `` `…` §N ``) were each logged by seven sonnet re-pointers
(`studies/specclean/cites_1..7.tsv`): **429 REPOINTED** (in 160 files),
891 VALID (the §-number still means the same topic), 24 LEFT-GENERATED (tool
outputs: tools/review/out, design `out/` dirs, a census `.tsv`, a `reader_grep.txt`),
5 LEFT-EMITTED (`src/enc/enc_byte.c:30,268`, `src/enc/enc_utf8.c:40,421`,
`src/gen/emit_dfa.c:2337` — emitted comment strings citing `S3.1`/`S3.1.2`,
both still valid; touching them is an abi event), 7 LEFT-UNRESOLVED (historical
records whose line citation predates aee1a570 and whose topic is not
determinable: stamp_inventory_raw.md ×2, r4e0b_report.md:75, w5_facts.md:162,
r1-k82-handoff.md:21, lens9:424, testing.md:3539). Every `match_api.md:N` line
citation in a living file is now an anchor; historical records kept a
"(was match_api.md:N)" note where the agent re-pointed them. Every old `§9`
citation (now encodings) was re-pointed to `#pre-v1`. Emitted-artifact identity
verified unchanged: main's `build/pcrec` and this branch's emit byte-identical
C for 4 patterns × 4 flag sets.

**How a citer should cite**: `docs/spec/match_api.md#<anchor>`
(`studies/specclean/ANCHORS.txt` lists all 151 at landing); a `§N` beside it
is fine for a human, never a line number.

**Readers of spec text kept working**:
- `tests/registry/axes_registry_check.sh` and `tests/codegen/
  run_fallback_table.sh` extracted value sets by phrase anchors (one of them a
  DATE, "2026-08-26: a THIRD"). Every value set is now a table under a
  `<!-- value-set: RX_NAME -->` marker and both scripts anchor on it; the
  line/prose extractors (`extract_line_values`, `extract_prose_values`) lost
  their last callers and were removed from `tests/lib/spec_extract.sh`.
  Sabotage: a removed marker extracts empty, which `check_value_set` reports
  as every dump value undocumented (red).
- abi-number readers (D94): the spec's two readers (the guard block and the
  `#abi` sentence) both read 71; no test reads the spec's number.

## 7. Prevention: `make test-spec-history` (`tests/spec_history/`)

`spec_history.py` scans docs/spec/*.md (not CLAUDE.md), per line outside code
fences, for five markers: `date` (ISO date), `addendum`, `walkback` (used to,
no longer, now reads, corrected, superseded, formerly, previously, this
revision, before this date, re-quoted, walk back, until/since `[TAG]`, since
abi N), `narrative` (panel, critic, RULED, ruling, Frank, lane NAME), `tagopen`
(a paragraph/bullet/heading opening with `[ROW-TAG]`). `allowlist.tsv` (2 rows,
both match_api.md, with reasons); `baseline.tsv` = the other ten docs'
per-marker counts as KNOWN DEBT, held EXACTLY (a rise is new history, a fall
says "lower the baseline"). match_api.md has no baseline row. Joined
`TEST_SECTIONS` (the section count moves +1). Hand sabotage, against a scratch
copy of the tree: a planted `**[XYZ-1], 2026-10-09 — ADDENDUM:** this used to
read otherwise (panel R99).` line → 5 FAIL (all five markers), checks
failed 5; a baseline raised to 999 → 1 FAIL ("debt was paid: lower ... to 25").
The mech arm `spechistory` is registered in `tests/mech/run_sabotage_matrix.sh`;
the row is `tests/spec_history/sabotage_row.pending`, **id left blank (`SXXX`)
for the manager to allocate** (its header says how to land it; it is kept out
of `tests/mech/sabotages/` because the matrix parses the id from the filename).
learnings §3 notes: the control (the baseline) is a separate file from the
docs it counts; the check fails closed on an empty docs/spec, an unknown marker
id, or a baseline naming a missing file; what it cannot see (history phrased
with none of the markers) is stated in its CLAUDE.md.

## 8. Validation

- `make test-registry` (after the marker switch): `checks failed: 0`, every
  value-set leg PASS both directions (log was scratch).
- `make test-spec-history`: 55 passed / 0 failed.
- `make test-codegen`, `make test-rxtsource`, `make test-registry` (re-run
  after the citation edits): see the handback message for the numbers.

## 9. Files

New: `docs/dev/history/{CLAUDE.md,match_api_record.md,abi_changelog.md}`,
`tests/spec_history/{CLAUDE.md,spec_history.py,run_spec_history.sh,
allowlist.tsv,baseline.tsv,sabotage_row.pending}`, `studies/specclean/`
(ledger + inputs + briefs + citation logs; its own CLAUDE.md), this report.
Changed: `docs/spec/match_api.md` (rewritten), `docs/spec/CLAUDE.md`,
`docs/dev/CLAUDE.md`, `tests/CLAUDE.md`, `tests/lib/{spec_extract.sh,
CLAUDE.md}`, `tests/registry/{axes_registry_check.sh,CLAUDE.md}`,
`tests/codegen/{run_fallback_table.sh,run_codegen_tests.sh}`, `Makefile`,
`tests/mech/run_sabotage_matrix.sh`, `src/gen/{emit_dfa.c,CLAUDE.md}`
(comments only), and 160 files' citations.

Owed to the manager: the abi-changelog ruling (§3), the S-id for the sabotage
row, the D76 addendum line if ruled, plan.md `[SPEC-CLEAN]` STATE, and filing
the follow-ups (other spec docs' debt in density order; emitted-comment
staleness as an abi event; lib/pcrec.h comments).
