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

- `facts_listing.md` — **[PATFACTS] step 3.0, 2026-09-26 (D126, ruled Q8).**
  `--emit-facts`' output format: its two `#section` blocks (`facts`,
  `decisions`) and their columns, the CLOSED `status` (`derived`/`denied`/
  `declined`/`absent`) and `used` vocabularies, the `why` token grammar
  (`deny:<flag>`/`decline:<reason>`/`rate:<source>`), the three guarantees
  (never refuses a compile that succeeded; never changes the compile; one
  spelling per value, shared with the fact-valued stamps), and what is NOT
  promised (fact names, reason names, prose). A DEBUG listing with
  `ir_listing.md`'s status — no `abi` number. The per-flag "Facts emptied"
  lines it points at live in `tuning.md` §2.25-§2.28 and are what
  `tests/codegen/run_facts_checks.sh` checks the listing against.

- `ir_listing.md` — **[DD-8], 2026-09-19.** `--emit-ir`'s output format:
  its nine `#section` blocks (`summary`, `slots`, `rungs`, `strategies`,
  `pruning`, `program`, `choicepoints`, `islands`, `callouts`) and their
  columns, the `prefilter` value vocabulary and the `program` `op`
  vocabulary, the multi-valued-cell and escaping rules, and the three
  things the listing is NOT — not an IR anything consumes, not lossless
  (lossy on operands, by ruling), not a DFA listing. Sits UNDER
  `table_contract.md` (it conforms to it and adds only what is specific
  to this listing) and beside `cli.md` §2 (the flag's reference entry).
  The producer-side rule that an empty population is a ROW rather than a
  comment lives here, because it follows from the table contract's own
  header rule rather than from taste. Read it before changing anything
  `vm_render_listing` prints.

- `limits.md` — the resource-bound contract, FACTS ONLY and numbered (rewritten
  by lane speclim): §1 the guarantee (a give-up is never a false answer), §2 the
  give-up codes, §3 the numbers (§3.1 step and work budgets, §3.2 frame and
  trail capacities and the tiered entry's cost, §3.3 the compile-time ceilings,
  their raise-only overrides and the DFA-side exceptions, §3.4a
  `pcrec_limits_tsv`, §3.5 the `.rxt` source parser's caps, §3.6 `vars`, §3.7
  findings, §3.8 `ucp`, §3.9 the DFA context sets), §4 the worked example, §5
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

- `tuning.md` — **[SPEC-1.3], 2026-08-25.** The `-f`/`-fno-` tuning-axis
  contract: what a tuning flag is (a generation-time choice, D18/D46/D47.3),
  one section per axis (every `-f`/`-fno-` flag, `--unroll=K`,
  `--engine=`'s tuning-adjacent role) stating what each denies/forces, its
  default, its emitted stamp (verified by an artifact diff), whether it is
  ANSWER-IDENTITY-preserving or ENGINE-SELECTING, and the differential that
  validates it with a measured population count. Also states the DFA side's
  own stamps (§3 — the `[DD-13]` gap this document once recorded was closed
  by `[DD-13]`/`[DD-13c]`, and `[OPT-3]` added `RX_DFA_TABLE` on 2026-08-26
  with its own axis at §2.13) and a
  `pcrec_options`-field-to-flag mirror table. Found and flagged one drift in
  the process: `lib/pcrec.h`'s own comment names the splice/linkage stamp
  `<PREFIX>_VM_CALLS`; the shipped emitter (`src/gen/emit_vm.c`) actually
  emits two macros, `RX_VM_CALL_SPLICED`/`RX_VM_CALL_LINKED` — this document
  states the as-built name; `lib/pcrec.h`'s comment was corrected at 40d9f79.

  **2026-09-29 (D131 item 1, lane adm131 applying clsfit's verbatim diff):**
  §2's λ (class-matcher kit) row moves off `reservation` for the first
  time — it states the RULED policy (one kit constant λ=4 plus a
  first-match rule over the whole-set tables, `docs/design/
  opt_dial_design.md` §4) — but is still a design-stage entry: `[CLS-TREE]`
  is unbuilt, so the row documents what the mechanism will read the day it
  lands, not a shipped behaviour.

- `rxt_format.md` — **[SPEC-1.6], 2026-08-25.** The `.rxt` test-corpus
  format and the harness driver protocol, extracted from `docs/testing.md`
  (lines ~124-467 there): the full directive grammar (`pattern`/`flags`/
  `features`/`perr`/`m`/`n`/`ms`/`ns`/`g`/`gp`/`gu`/`engine`/`budget`/
  `frames-buffer=`), the subject escape table, the oracle-verification
  requirement (the default python-`re` oracle, the `# pcre2-only`
  exclusion convention, per-directory oracle overrides), how `run.sh`
  scores a block, `tests/harness/driver.c`'s CLI/exit-code contract
  (including the `_in`-entry anchored cross-check's exit `4`, previously
  undocumented in prose anywhere), the D45 budget policy stated as policy
  rather than measurement, and how to add a new component test directory.
  Every claim verified against `tests/harness/run.sh`/`driver.c` at this
  worktree's branch point (`d39ce94`); `docs/testing.md` keeps the process
  record (runtimes, battery composition, sanitizer/lint measurements,
  TT-* notes, the living oracle-exclusion catalog) and gained a header
  note plus a one-paragraph pointer where the moved sections stood.


  **[DD-13b.W1.2], 2026-08-31**: the head table's `target` row stops
  reading "Parsed, not yet built" and its `lib` row stops reading
  "Recorded, not yet resolved"; a new "Building from a source file"
  section states what belongs to the FORMAT rather than to the CLI — a
  definition is a block's `name` in the FILE namespace, the
  no-target-plus-one-unnamed-block compatibility default, the
  library-builds-nothing outcome, the `features` UNION and the
  more-specific-wins table, and the harness's per-target agreement control.

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

- `findings.md` — **[FINDINGS] B1, 2026-09-27 (D122/D123/D126).** The
  findings contract: the terms, the `freq` kind and its row grammar, the
  closed query/derivation vocabularies, the `unigram` normalization with its
  test vectors, the per-question-KIND NONE answers and each reader's kind and
  guarantee, the `<PREFIX>_FINDINGS` stamp grammar with the digest's byte
  layout and the name-disclosure statement, and the shipped default and store.
  It grows by step (resolution and the CLI at B2, the analyzer at B3/B6,
  `run-rarity` at B4, `cpfreq` at B5), and says at each section what is not
  built yet.
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
