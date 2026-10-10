# docs/spec/ — spec documents

Spec documents detail how the tool and its surfaces actually work and how to
use them. They are deliverables like code: actively maintained (not
append-only), carry no build history, and may reference docs/design/
documents for the reasoning behind a design without repeating it.

Build history is NOT part of the spec (Frank, 2026-08-14), and
`make test-spec-history` (`tests/spec_history/`) flags it mechanically, with
the other docs' current history counted as known debt: how a surface
came to be — panel outcomes, refuted predictions, rulings, the design
process — stays in docs/design/ and docs/dev/. A spec may refer to design
documents but only INFORMATIONALLY: such references are background for the
curious reader, never normative. The spec alone states the contract; if a
spec and a design doc disagree, the spec is what the tool promises.

## Numbering and citation (Frank, 2026-10-09; lane specnum)

A spec is cited like a legal code: by NUMBER, which never changes. `match_api.md`
is the first document to carry it; every other spec adopts it when it is
rewritten facts-only (`tests/spec_history/cite_floors.tsv` has a row per
adopter, and the checks below run on any `docs/spec/*.md` that carries the
contents block).

- **Sections.** Every heading below the `# ` title begins with its dotted
  number (`## 3.`, `### 3.1`, `#### 3.1.3`; depth = heading level - 1) and is
  preceded by a line `<a id="s3-1-3"></a>` (`s` + the number, dots to dashes).
- **Paragraphs.** Every prose paragraph, list item and block quote begins
  `<a id="s3-1-3-p4"></a>[3.1.3¶4] ` -- the section's number, `¶`, the
  paragraph's number: 1, 2, 3 ... in document order within its innermost
  section (the preamble above the first heading is section `0`). A fenced
  code block or a table belongs to the paragraph it follows, or to its
  section when nothing precedes it. `¶`, not another dot, because a section
  can hold both subsections and paragraphs: `§3.1.1` is a subsection of
  §3.1, `§3.1¶1` a paragraph of it.
- **The citation form** is `match_api.md §3.1.3` or `match_api.md §3.1.3¶4`
  (a human may add the topic). Never a line number, never an anchor name. A
  shell or emitted string may use `S3.1`, the form the emitted
  `<prefix>_next_pos` comment already has.
- **Stability.** A number is never reused and never changes. An addition takes
  a letter after its predecessor: a section between §3.2 and §3.3 is `§3.2a`
  (its subsections `3.2a.1`, its paragraphs `§3.2a¶1`), a paragraph after ¶4
  is `¶4a`. A removal leaves a one-line stub under the same number -- the
  heading `### 3.2 — retired` or the paragraph `[3.2¶4] — retired.`, optionally
  naming where the text went (`— retired (moved to §7¶2)`). Moving text to
  another section is a removal plus an addition.
- **Contents.** A block between `<!-- spec-toc:begin -->` and
  `<!-- spec-toc:end -->` right under the title lists every numbered heading,
  number and link, and is GENERATED: `python3 scripts/spec_toc.py FILE` (add
  `--init` the first time) rewrites it; never edit between the markers.
- **Checks** (`make test-spec-history`, `tests/spec_history/spec_cites.py`):
  the numbering is well-formed (anchors, labels, order); the contents are
  current; every `<doc>.md §N` / `§N¶K` / `SN` cited anywhere in the tree
  names a number that exists (a retired stub exists); no `<doc>.md:<line>`
  citation remains. What no check can see is a RENUMBERING that leaves every
  cited number resolvable (a paragraph deleted and its successors shifted
  up): review the diff of a spec edit for a changed label.
- **Adopting it in another spec**: number the headings, give each its anchor
  line, label the paragraphs (`studies/specnum/number.py` is the one-time pass
  that labelled `match_api.md`; adapt it, it refuses a numbered file), run
  `scripts/spec_toc.py --init`, add the doc's row to `cite_floors.tsv`,
  and re-point the tree's citations of it (`studies/specnum/repoint.py` did
  that for the anchor form).

## Files

- `match_api.md` — the match-API contract, FACTS ONLY (rewritten by lane
  specclean, 2026-10-09): §1 symbols and namespaces (the shared ABI block and
  its `abi`-valued guard), §2 the fixed ABI types verbatim, §3 the entry points
  (`<prefix>_search` with the find-all loop at §3.1 — the emitted
  `<prefix>_next_pos` comment cites "match_api.md S3.1", so the loop stays
  there — `_next_pos`, `_valid_upto`, `_match`, `_match_caps`, `_info`,
  give-ups across entries, the `(?:P)\z` idiom), §4 the give-up and refusal
  codes, §5 captures and groups (slot rules, concurrency at §5.3, named groups,
  composition), §6 `rx_info` field by field and the `abi` rule, §6.3 every
  stamp macro (an inventory table, then one anchored entry per stamp), §7 the
  NUL-terminated compile entry, §8 the library structures, §9 encodings and
  character positions, §10 the `_in` entries and the tiered default. **Cite it
  by number** (`match_api.md §3.1.3`, or one paragraph, `§3.1.3¶4`), never
  by line or anchor name; the numbering rule above applies, its contents
  block is generated by `scripts/spec_toc.py`, and a §6.3 stamp is a numbered
  paragraph of §6.3.x (the inventory table at §6.3.2¶1 gives each one). Every §6.3 value set is a table directly under a
  `<!-- value-set: RX_NAME -->` marker, which `tests/registry/
  axes_registry_check.sh` and `tests/codegen/run_fallback_table.sh` anchor on:
  keep the marker with its table. Its history (revision notes, rulings,
  walkbacks) is `docs/dev/history/match_api_record.md`, its `abi` change log
  `docs/dev/history/abi_changelog.md`; `make test-spec-history`
  (`tests/spec_history/`) keeps history out. `studies/specclean/claims.tsv`
  maps every claim of the pre-rewrite text to its new home.

- `table_contract.md` — the wire format of every command that outputs a DATA
  TABLE, FACTS ONLY and numbered (rewritten by lane specreg): §1 scope (a table
  of every conforming producer and its shape, anonymous or sectioned), §2 the
  producer rules (`#` comments, a header row naming all columns, append-only
  columns, no TAB in a field), §3 the consumer rules (resolve by header name,
  trailing-safe, field count only as header equality), §4 sections (`#section
  NAME`, the leading anonymous table), §5 the two checks (header truthfulness,
  generator agreement). A new table surface adopts it at birth and gets a row in
  §1. Cite by number (`table_contract.md §2¶4`). History:
  `docs/dev/history/table_contract_record.md`.

- `facts_listing.md` — `--emit-facts`' output format, FACTS ONLY and numbered
  (rewritten by lane specsmall): §1 what the listing is (a debug listing, reads
  the record and never recomputes it), §2 the query, §3 framing, §4 the two
  `#section` blocks (§4.1 `facts` with its CLOSED `status` and `used`
  vocabularies, the `value` spellings at §4.1.2 and the `why` token grammar at
  §4.1.3; §4.2 `decisions`), §5 the three guarantees, §6 what is NOT promised.
  The per-flag "Facts emptied" lines it points at live in `tuning.md` §2 and
  are what `tests/codegen/run_facts_checks.sh` checks the listing against.
  Cite by number (`facts_listing.md §4.1.3`). History:
  `docs/dev/history/facts_listing_record.md`.

- `ir_listing.md` — `--emit-ir`'s output format, FACTS ONLY and numbered
  (rewritten by lane specsmall): §1 what the listing is (a debug listing,
  VM-only, derived from the emitter's own walk), §2 framing, §3 the nine
  `#section` blocks (§3.1 `summary` with the `prefilter` token vocabulary at
  §3.1.1 and `prune-ceiling` at §3.1.2; §3.2 `slots`; §3.3 `rungs`/`strategies`/
  `pruning`; §3.4 `program` and its `op` vocabulary; §3.5 `choicepoints`; §3.6
  `islands`; §3.7 `callouts`), §4 consuming it. Sits under `table_contract.md`
  and beside `cli.md` §2. Read it before changing anything `vm_render_listing`
  prints. Cite by number (`ir_listing.md §3.1.1`). History:
  `docs/dev/history/ir_listing_record.md`.

- `limits.md` — the resource-bound contract, FACTS ONLY and numbered (rewritten
  by lane speclim): §1 the guarantee (a give-up is never a false answer), §2 the
  give-up codes, §3 the numbers (§3.1 step and work budgets, §3.2 frame and
  trail capacities and the tiered entry's cost, §3.3 the compile-time ceilings,
  their raise-only overrides and the DFA-side exceptions, §3.4a
  `pcrec_limits_tsv`, §3.5 the `.rxt` source parser's caps, §3.6 `vars`, §3.7
  findings data, §3.8 `ucp`, §3.9 the DFA context sets), §4 the worked example, §5
  the C stack, §6 left recursion, §7 what is not limited, §8 emitted artifact
  size (§8.4 the size-cap ladder, §8.7 the warning) with §8a and §8b.
  `pcrec --list-limits` names the section of each number in its `anchor`
  column (3.1-3.9 and 8), and `tests/registry/limits_check.sh` finds each
  anchored value, comma-grouped, inside that section's text: keep a number's
  literal in its section. Cite by number (`limits.md §8.4`). History:
  `docs/dev/history/limits_record.md`.

- `cli.md` — the `pcrec` command-line reference, FACTS ONLY and numbered
  (rewritten by lane speclim): §1 compiling a pattern (§1.1 a file operand and
  how a target's options compose, §1.2 `-o`, then one section per flag or flag
  group through §1.18), §2 the listing and query surfaces (one section each),
  §3 diagnostics (exit codes, the class tag, the compatibility tiers), §4 what
  the CLI does not do. Cite by number (`cli.md §1.1.4`). History:
  `docs/dev/history/cli_record.md`.

- `tuning.md` — the tuning-axis contract, FACTS ONLY and numbered (rewritten
  by lane spectune): §1 what a tuning flag is (the four classes: answer-
  identical, engine-selecting, contract, rendering; the answer-identity rule;
  the dial default and explicit-beats-dial), §2 the axes — §2¶3 the
  `rx_info.flags` mask rule, §2¶4 the inventory table, then one section per
  axis, §2.1-§2.45 (a `--list-axes`-checked `(bit N)` in every flag heading;
  §2.10 `--unroll`, §2.11 `--engine`, §2.21 `--vm-entry-shape`, §2.29 the
  pre-check admission table, which has no flag), §3 the DFA scan's stamps
  with §3.1 the hybrid and §3.2 the `rx_info` mirrors, §4 the
  `pcrec_options` mirror (exhaustive over `flags`), §5 the `--tune` dial
  (§5.4 the pinned policy table). Every pre-rewrite section number was kept.
  Readers of its literal text, so keep their shapes: `tests/axes/run_axes.sh`
  and `tests/registry/axes_registry_check.sh` take the `(bit N)` set between
  `## 2.` and `## 3.` (every axis bit, nothing else); `tests/codegen/
  run_facts_checks.sh` reads each `-fno-` section's `**Facts emptied**`
  paragraph; `tests/codegen/run_tune_dial.sh` reads §5.4's table rows by
  their first cell (`-fno-premul-table`, `ladder — bar`, `ladder —
  threshold`: no earlier table may start a row with those); `tests/memfn/
  rows_check.py` reads §2.38's row table. Cite by number (`tuning.md
  §2.17`). History: `docs/dev/history/tuning_record.md`.

- `rxt_format.md` — the `.rxt` test-corpus format and the harness driver
  protocol, FACTS ONLY and numbered (rewritten by lane specrxt): §1 the
  format (§1.1 the head and its eleven declarations, §1.2 the delivering
  call `(?&site=name)`, §1.3 building from a source file, §1.4 the lexical
  rules in two layers — §1.4.1-§1.4.5 the structure layer S0-S3 and the open
  subtree, §1.4.6 the schema layer, §1.4.7 values and whitespace — §1.5 the
  block's line kinds with the subject escapes at §1.5.1, §1.6 named subjects
  `@file:`, §1.7 `mc`, §1.8 `under`, §1.9 `provenance`, §1.10 `analysis`
  bundles, §1.11 `variant`, §1.12 `ext` and its graduation rule, §1.13 the
  schema and `--list-schema` with the constraint clause spellings at §1.13.1,
  §1.14 an example that `run.sh` and `verify_rxt.py` pass), §2
  `--list-source` (§2.1 the four `#section` blocks), §3 oracle verification
  (§3.1 `oracle`), §4 how `run.sh` evaluates a block, §5 the driver protocol
  and exit codes, §6 organizing tests by component. It says which of the
  three readers (`pcrec`, `run.sh`, `verify_rxt.py`) enforces each rule.
  Cite by number (`rxt_format.md §1.5`). No test reads its literal text.
  History: `docs/dev/history/rxt_format_record.md`.

- `registry.md` — the TSV column contract of the registry listings, FACTS ONLY
  and numbered (rewritten by lane specreg): §1 the append-only, resolve-by-name
  promise, §2 `--list-syntax` (17 columns, each with its value set and whether
  it is a closed vocabulary or free text), §3 `built` versus `status`/`roadmap`,
  §4 `--list-verbs`, §5 `--list-families` (the grouping rule and `built`'s
  direction), §6 `--list-axes` (12 columns, the source boundary, the one-row-per-
  value rule, the kit's `memfn` section and its pinned floor), §7 what the
  registry tests pin and what they do not, §8 retired, §9 `--list-definitions`,
  §10 where every table surface is documented. Cite by number (`registry.md
  §6¶4`). `tests/registry/axes_registry_check.sh` reads the `memfn` floor
  literal from §6¶8, so that paragraph keeps its form (see it). History:
  `docs/dev/history/registry_record.md`.

- `findings.md` — the findings contract, FACTS ONLY and numbered (rewritten by
  lane specsmall): §1 terms, §2 the data (`freq`, `cpfreq`; `bigram` is
  vocabulary only), §3 the `unigram` normalization with its test vectors, §3a
  the `encode-utf8`/`encode-latin1` derivations, §4 the per-question-KIND NONE
  answers and each reader, §5 the `<PREFIX>_FINDINGS` stamp and its digest, §6
  the shipped analyses and the store, §7 resolution of a name, §8 the two
  listings, §9 the `pcrec_options` fields. Cite by number (`findings.md §4`).
  History: `docs/dev/history/findings_record.md`.
- `vars.md` — **module `vars`' caller-observable contract** ([VAR], 2026-09-23):
  `${name}` in a pattern, whose bytes the caller supplies per call. The
  spelling and its five bash-shaped operators, the `rx_var` type and the
  BY-NAME rule (an index is meaningless across separately compiled
  artifacts), where the array is passed (`rx_ctx` for the `rx_matchfn`-shaped
  entries, a trailing pair for `<prefix>_search` and its `_in` siblings),
  `PCREC_ERR_UNSET_VAR`'s below-the-floor refusal class and why an unset
  variable is loud rather than empty, every refusal the module can raise, and
  the engine/caseless facts. The ABI surface itself is `match_api.md` §2 and
  §6's `abi` 32 entry; the numbers are `limits.md` §3.6. Design:
  `docs/design/variables_common.md` / `variables_pattern.md`.

**`docs/pcre2_compliance.md` is SPEC-TIER IN PLACE** ([SPEC-1.9], manager
ruling, 2026-08-25): it meets this tier's bar through its own
three-component annotated-derivation discipline (generated facts +
independent PCRE2-side survey + keyed hand-written annotations, held in
checked tension — `.claude/skills/compliance-refresh/SKILL.md`) rather
than by moving under `docs/spec/`; it stays at its current path because
its tooling (`tests/registry/compliance_section.py`, the annotation
store) is path-keyed.

Maintenance: update this file when files are added/removed or their roles
change.
