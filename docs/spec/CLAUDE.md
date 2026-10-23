# docs/spec/ -- spec documents

Spec documents detail how the tool and its surfaces actually work and how to
use them. They are deliverables like code: actively maintained (not
append-only), carry no build history, and may reference docs/design/
documents for the reasoning behind a design without repeating it.

## Standing rules

- **The spec carries no build history** (Frank, 2026-08-14). How a surface
  came to be -- panel outcomes, refuted predictions, rulings, the design
  process -- stays in docs/design/ and docs/dev/. `make test-spec-history`
  (`tests/spec_history/`) flags build history mechanically, with the other
  docs' current history counted as known debt. A spec may refer to design
  documents but only INFORMATIONALLY: such references are background for the
  curious reader, never normative. The spec alone states the contract; if a
  spec and a design doc disagree, the spec is what the tool promises.
- A change to anything a caller can observe updates the spec in the SAME
  change (D80; root CLAUDE.md); a reviewer rejects a contract change without
  its spec hunk.
- Each spec's history lives in `docs/dev/history/<doc>_record.md` (match_api:
  `match_api_record.md` and `abi_changelog.md`), never in the spec.
- Keep the literal shapes that scripts read (see the Files list).
- **Caller-facing names describe behaviour, never architecture** (D174, Frank
  2026-10-22): no "kit"/"memfn"/"proof"/family letters in a new flag, stamp,
  field, option or spec sentence a caller reads. Not retroactive.
- `docs/pcre2_compliance.md` is SPEC-TIER IN PLACE ([SPEC-1.9]): it meets this
  tier through its own three-component annotated-derivation discipline
  (`.claude/skills/compliance-refresh/SKILL.md`) and stays at its path because
  `tests/registry/compliance_section.py` and the annotation store are
  path-keyed.
- Maintenance: update this file when files are added/removed or roles change.

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

## Files (all FACTS ONLY and numbered unless noted; cite by number)

- `match_api.md` -- match-API contract: symbols/namespaces, fixed ABI types,
  entry points (the find-all loop at §3.1: the emitted `<prefix>_next_pos`
  comment cites "match_api.md S3.1", so the loop stays there), give-up/refusal
  codes (§4), captures (§5), `rx_info` and the `abi` rule (§6), every stamp
  macro (§6.3; each §6.3 value set is a table directly under a
  `<!-- value-set: RX_NAME -->` marker that `tests/registry/axes_registry_check.sh`
  and `tests/codegen/run_fallback_table.sh` anchor on: keep the marker with
  its table), compile entry (§7), library structures (§8), encodings (§9),
  `_in` entries (§10). `studies/specclean/claims.tsv` maps the pre-rewrite
  claims to new homes.
- `table_contract.md` -- wire format of every DATA TABLE command; §1 has a row
  per conforming producer (a new table surface adopts it at birth and gets a
  row); producer/consumer rules, sections, the two checks.
- `facts_listing.md` -- `--emit-facts` format. Per-flag "Facts emptied" lines
  live in `tuning.md` §2 and are what `tests/codegen/run_facts_checks.sh`
  checks the listing against.
- `ir_listing.md` -- `--emit-ir` format (VM-only, nine `#section` blocks); read
  before changing anything `vm_render_listing` prints.
- `limits.md` -- resource-bound contract. `pcrec --list-limits` names each
  number's section in its `anchor` column (3.1-3.9 and 8), and
  `tests/registry/limits_check.sh` finds each anchored value, comma-grouped,
  inside that section's text: keep a number's literal in its section.
- `cli.md` -- the `pcrec` command-line reference (§1 flags, §2 listing/query
  surfaces, §3 diagnostics, §4 non-features).
- `tuning.md` -- tuning-axis contract. Readers of its literal text, keep their
  shapes: `tests/axes/run_axes.sh` and `tests/registry/axes_registry_check.sh`
  take the `(bit N)` set between `## 2.` and `## 3.` (every axis bit, nothing
  else; a `--list-axes`-checked `(bit N)` in every flag heading);
  `tests/codegen/run_facts_checks.sh` reads each `-fno-` section's
  `**Facts emptied**` paragraph; `tests/codegen/run_tune_dial.sh` reads §5.4's
  table rows by their first cell (`-fno-premul-table`, `ladder — bar`,
  `ladder — threshold`: no earlier table may start a row with those);
  `tests/memfn/rows_check.py` reads §2.38's row table. Every pre-rewrite
  section number was kept.
- `rxt_format.md` -- the `.rxt` format and harness driver protocol; says which
  of the three readers (`pcrec`, `run.sh`, `verify_rxt.py`) enforces each
  rule. No test reads its literal text.
- `registry.md` -- TSV column contract of the registry listings
  (`--list-syntax`, `--list-verbs`, `--list-families`, `--list-axes`,
  `--list-definitions`). `tests/registry/axes_registry_check.sh` reads the
  `memfn` floor literal from §6¶8, so that paragraph keeps its form.
- `findings.md` -- findings contract (data, normalization, stamp, listings).
- `measures.md` -- measurement-set contract ([MEASURE-SET] M0), numbered from
  birth.
- `pattern_language.md` -- the PATTERN LANGUAGE: every accepted construct, its meaning
  (match semantics, captures, preference order), module gate and refusal
  shape, per encoding and option; pcrec's own definition, of which
  `docs/pcre2_compliance.md` is the delta. Numbered from birth. §10 is the
  construct index, one line per `--list-syntax` row (syntax, module,
  section) in a `| syntax | module | section |` table under the heading
  `10. Construct index`: `tests/registry/syntax_index_check.py` (in
  `make test-registry`) reads that table and the heading numbers, so keep
  both shapes. A new registry row needs its §10 line in the same change.
- `vars.md` -- module `vars` ([VAR]) caller-observable contract (`${name}`,
  `rx_var`, `PCREC_ERR_UNSET_VAR`); not yet in the numbered-facts form
  described above.

## Pointers

`tests/spec_history/` (`spec_cites.py`, `cite_floors.tsv`),
`scripts/spec_toc.py`, `studies/specnum/`, `docs/dev/history/*_record.md`,
D80 in `docs/dev/decisions.md`, `docs/guide/` (human tier, points here).

History (long narrative, dated notes, measurements, per-lane records; not auto-injected): docs/dev/history/claude_md/docs__spec.md
