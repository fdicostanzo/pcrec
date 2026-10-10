# Lane specnum — numbered sections and paragraphs, contents, citation checks (report)

Lane: specnum (sonnet), branch `lane/specnum` off `lane/specclean` (`c2c11fa4`),
2026-10-09. Finishes `[SPEC-CLEAN]` with the three things Frank asked for that
lane specclean did not apply: permanent section and paragraph numbers for
`docs/spec/match_api.md`, a generated table of contents, and the checks that
hold both and the citations of them.

## 1. Numbers

`match_api.md` now carries 54 numbered sections and 379 numbered paragraphs.

- A section's number is its heading's (`§3.1.3`), preceded by `<a id="s3-1-3"></a>`.
- A paragraph is a prose paragraph, a list item or a block quote, numbered from 1
  within its innermost section and written `§3.1.3¶4`; its first line reads
  `<a id="s3-1-3-p4"></a>[3.1.3¶4] …`. The preamble above §1 is section `0`. A
  fenced code block or a table belongs to the paragraph it follows (to its
  section when nothing precedes it), because a code block is an illustration of a
  paragraph and a table is its data (the `<!-- value-set: RX_NAME -->` markers the
  registry and fallback-table checks anchor on stay directly above their tables).
- **The paragraph separator is `¶`, not another dot — a deviation from the brief's
  `§3.2.4`.** The brief's form cannot be had without renumbering cited sections:
  §3.1 has a subsection `§3.1.1` (`_next_pos`, cited by the emitted comment) and
  also has paragraphs, and §6.3, §3, §5, §6, §8, §9 and §10 are the same
  (paragraphs and numbered subsections side by side). A dotted paragraph number
  would be `§3.1.1` for two different things. `¶` keeps the number a hierarchy
  (`§3.1¶1` is a paragraph of §3.1, `§3.1.1` a subsection), keeps every existing
  `§N.M.K` citation meaning what it meant, and costs nothing at a call site:
  `match_api.md §6.3.4¶11`. Insertions and retirements are as briefed: a section
  between §3.2 and §3.3 is `§3.2a` (its subsections `3.2a.1`, its first paragraph
  `§3.2a¶1`), a paragraph after ¶4 is `¶4a`, a removal leaves `[3.2¶4] — retired.`
  or the heading `### 3.2 — retired` (tested: such stubs keep the checks green and
  stay in the contents).
- **One heading had no number.** `#### Finding every match` (the find-all loop)
  took `§3.1.3`, the next free child of §3.1; it comes BEFORE §3.1.1 and §3.1.2 in
  the document, which is the stability rule working (their numbers are cited from
  emitted comments and could not move). `S3.1` — the emitted `next_pos` comment's
  form — still means the find-all loop: the loop is inside §3.1.
- The semantic `<a id>` anchors specclean added (151) were REPLACED by
  number-derived ones, not kept beside them: two anchors per paragraph would be two
  link targets to keep in step. `studies/specnum/anchor_map.tsv` maps each old id to
  its number and new anchor, for anyone holding a link; the 113 in-document links
  were re-pointed to the new ids, and the inventory table's links now read
  `[§6.3.4¶11](#s6-3-4-p11)`.
- The preamble paragraph `§0¶2` (the "Citing this document" paragraph) states the
  rule in the document itself; `docs/spec/CLAUDE.md` gained a "Numbering and
  citation" section so other spec documents adopt it (anchor and label syntax, the
  separator and why, the stability rule, the contents block, the checks, and the
  steps to adopt it).
- `studies/specnum/number.py` is the ONE-TIME labelling pass (it refuses an
  already-numbered file); the standing definition of "a paragraph" is
  `tests/spec_history/specdoc.py`, which the check applies on every `make test`.

## 2. Contents

`scripts/spec_toc.py [--init|--check] FILE…` rebuilds a block between
`<!-- spec-toc:begin -->` and `<!-- spec-toc:end -->` from the document's numbered
headings: number plus link, indented by depth, 54 entries for `match_api.md`, put
right under the `# ` title. It errors (rc 1) on a numbered heading with no
`<a id="sN">` line, on a repeated number, on a missing block (without `--init`) and
on a document with no numbered headings; `--check` writes nothing. Its failing-
direction control is `scripts/tests/spec_toc.py.test` (17 checks, run by
`make testscripts`; also in the chain below).

## 3. Citations

- **`match_api.md#anchor` → `match_api.md §N¶K`** (`studies/specnum/repoint.py`,
  with its own dry run): 291 lines in 127 files rewritten (bare `#anchor` forms
  included when the line, or one of the three before it, names `match_api`; markdown
  link targets keep an anchor, `#s…`), `§5.4 (`#dup-name-algorithm`)`-style
  redundancy collapsed to `§5.4¶6`, plus five lines by hand where `match_api` sat
  more than three lines up. Rewritten files include `lib/pcrec.h`, `src/gen/emit_dfa.c`,
  `src/core/internal.h`, `src/parse/rxt_compose.c` and `docs/spec/{cli,rxt_format,tuning}.md`
  — comments only; none sits inside an emitted string (checked line by line against the
  dry run), so there is no `abi` event. `make` rebuilt clean afterwards. The three emitted
  `S3.1`/`S3.1.2` strings (`src/enc/enc_*.c`, `src/gen/emit_dfa.c:2337`) are untouched
  and still true.
- **`match_api.md:<line>`**: eleven living or historical prose uses reworded to
  "`match_api.md line N`" (dev_journal ×2, four reviews/reports, two design notes,
  and `docs/design/decision_families/stamp_inventory_raw.md`); two tool outputs that
  are `grep -n` over the old file (`docs/design/start_table/reader_grep.txt`,
  `docs/design/subroutines_measurements/out/premises.txt`) are excluded by name in
  `cite_exclude.tsv`, as are the specclean and specnum logs.
- **Dangling numbers found by the new check**, none by the earlier rewrite: three
  `match_api` citations of the OLD numbering (`§2.2` and `§6.0` in dev_journal
  carrying a "now §5.x" note — reworded as "`§2.2` of the old match_api"; `S9b` in
  a W1 review, which names a spec HUNK, not a section) and one `match_api §11.9`
  that is the DESIGN note `match_api_m4.md`'s section (a review of that note; now
  spelled `match_api_m4 §1/§11.9`). The tree holds 1,057 citations of `match_api`;
  all resolve.

## 4. Checks (`make test-spec-history`, 64 checks, was 55)

All run under the same section (it was already in `TEST_SECTIONS`, so the count of
sections is unchanged); the history-marker check is untouched. New, in
`tests/spec_history/spec_cites.py` over every `docs/spec/*.md` that carries the
contents block:

| check | what it asserts |
|---|---|
| numbering ×3 | every numbered heading has its `<a id>` line and a depth equal to level − 1 and no repeat; every paragraph opens with its label, which names its own section, with a number-derived anchor and no repeat; base numbers run 1..n in order, an inserted `4a` after its `4` |
| toc | `scripts/spec_toc.py --check` is clean |
| cites ×4 | the citation patterns read planted text correctly (control); a planted dangling section and paragraph are both reported (control); every `<doc>.md §N` / `§N¶K` / `SN` in the tracked tree (chains `§A, §B`, `§A and §B` included) names a heading or label that exists; no `<doc>.md:<line>` remains; at least `cite_floors.tsv`'s count were scanned (500 of the measured 1,057 — K35) |

The tree is `git ls-files` at the repository's top level, otherwise a walk (a mech
scratch tree is `git archive` output with no `.git`).

**Failing direction** (planted into a `git archive` copy of the tree, each vs a clean
run of 64/0): an unlabeled paragraph → the paragraph-label FAIL; a stale contents
line → the toc FAIL (with the diff); `match_api.md §9.9` → the dangling FAIL naming
the file and line; `match_api.md §3.1.3¶77` → the same; `docs/spec/match_api.md:1234` →
the line-number FAIL; a label changed `[3.2¶2]`→`[3.2¶9]` → label, anchor and order
FAILs; a deleted section heading → label, toc and dangling (a cited `§3.5`) FAILs.
A retired-section stub (`### 3.4 — retired`) with a retired paragraph passes.

**Sabotage.** S748 (id given in the brief) is landed as
`tests/mech/sabotages/S748_spec_history_marker.sh` (git mv of the pending row; id
replaced, header and figure updated). Simulated against a scratch tree as the matrix
does (`SAB_BEFORE`→`SAB_AFTER`, then the arm): 58 pass / 6 fail — the five marker
classes plus the numbering FAIL (the planted paragraph carries no number). It was NOT
run through `make mech` locally (the chain below does). **A second row is drafted and
needs an id:** `tests/spec_history/sabotage_row_cites.pending` plants
`match_api.md §9.9` into `docs/spec/vars.md`; against a scratch tree it gives exactly
one FAIL (the dangling-citation line), 63 pass. **Id requested: one.** Its header says
how to land it (replace `SXXX`, move to `tests/mech/sabotages/S<id>_spec_cite_dangling.sh`).

## 5. What the checks do not catch

A RENUMBERING that leaves every cited number resolvable — delete ¶2 and let its
successors shift up: every label still exists, the order still runs 1..n, and only a
citation of the LAST number dangles. Stability is a review duty (a spec diff that
changes a label is the signal). The mechanical form is an identity manifest (each
label plus a hash of the paragraph's first words, held exactly); not built (D77: no
renumbering has happened), and it would make every first-sentence edit a manifest
edit. Filed as a possible follow-up, not a row.

## 6. Notes for the manager

- **`¶` vs the brief's dotted form** is the one judgement call (above). If Frank wants
  the dotted form anyway, it needs the cited subsections renumbered (`§3.1.1`,
  `§3.1.2`, all of `§6.3.N`, …) — a far larger rewrite of the tree's citations.
- **Other spec docs** adopt the rule by number-labelling (adapt `number.py`), an
  anchor line per heading, `spec_toc.py --init`, a `cite_floors.tsv` row.
  `docs/spec/CLAUDE.md` says so. Their history debt (baseline.tsv) is untouched.
- **`docs/dev/lanes/specclean_report.md` and `studies/specclean/` are unchanged**
  (historical): they describe the anchor-citation form this lane replaced;
  `ANCHORS.txt` there lists the old ids and `studies/specnum/anchor_map.tsv` carries
  them to numbers.
- The ruling asked by specclean (the abi change log's home) is not touched here.

## 7. Validation

Light, this box, one at a time, `TMPDIR` a 20-character path:

Run at `6e93a73b`+S748 (the doc, the checks and the citation rewrite were
final; later commits touch only CLAUDE.md files, the report, the self-test and
the pending row), log files in the lane's scratchpad:

| target | result |
|---|---|
| `make -j16` | rc 0 (comment-only `src/`/`lib/` edits rebuilt clean) |
| `make test-spec-history` | 64 passed / 0 failed (was 55/0) |
| `make test-registry` | 37/0 and 79/0 |
| `make test-rxtsource` | 279/0 |
| `make test-fallback-table` | 143/0 |
| `make test-tune-dial` | 113/0 |
| `make test-memfn-rows` | 137/0 |
| `make test-codegen` | rc 0, run_group 15/15 scripts |
| `make strict` | clean (`-Werror -Wshadow`, whole tree) |
| `scripts/tests/spec_toc.py.test` | 17/0 |
| `scripts/m6read_check_sab_anchors.py` | all anchors resolve (590 sabotages) |

`TMPDIR` was a 20-character path. The S748 row was simulated, not run through
`make mech`, and the planted-tree runs of §4 were against `git archive` copies.

Heavy chain (armed detached, waiting for `worktrees/specnum/.lift`; one waiter):
`worktrees/specnum/build/land/{waiter.sh,chain.sh}`, trailer
`worktrees/specnum/build/land/trailer.log`. Stages: `make -j8`; `make test` via
`scripts/perfrun --label specnum` (verdict:
`grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-' build/land/test.log` empty, read with
`test.log.perfrun`); `make strict`; `scripts/tests/spec_toc.py.test`;
`mech VALIDATE_ONLY`; `make mech` for S748 alone (`mech.log`, its
`== mech run COMPLETE` trailer). **OWED**; chain done = trailer line `== CHAIN DONE`.

## 8. Files

New: `scripts/spec_toc.py`, `scripts/tests/spec_toc.py.test`,
`tests/spec_history/{specdoc.py,spec_cites.py,cite_floors.tsv,cite_exclude.tsv,sabotage_row_cites.pending}`,
`tests/mech/sabotages/S748_spec_history_marker.sh` (moved from
`tests/spec_history/sabotage_row.pending`),
`studies/specnum/{CLAUDE.md,number.py,repoint.py,anchor_map.tsv}`, this report.
Changed: `docs/spec/match_api.md` (numbered, contents block, preamble), `docs/spec/CLAUDE.md`,
`tests/spec_history/{spec_history.py,CLAUDE.md}`, `tests/mech/run_sabotage_matrix.sh`
(a comment), the CLAUDE.md of `scripts/`, `scripts/tests/`, `tests/`, `studies/`,
`docs/dev/lanes/`, and the citations in 127 files (§3).
