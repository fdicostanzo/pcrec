# substr4 — compiled substitution, design revision 4 (Frank's interface rework)

Lane substr4 (opus, 2026-10-22), worktree `worktrees/subst`, branch
`lane/subst` (base c09063494). DESIGN ONLY: no build go, so nothing under
`src/`, `cli/`, `lib/`, `tests/` or `docs/spec/` was touched. No abi.

## STATE AT HANDOFF

- Everything is committed on `lane/subst` (this report's commit is the tip).
  The tree is clean except `docs/dev/artifact_size_log.tsv`, which was dirty
  before the lane and is left as it was.
- Rulings file `docs/dev/lanes/subst_rulings.md`: entries R4-R8 applied, **R8
  last**. R5-R8 arrived while the lane was working, and were found at the
  pre-commit re-read.
- Deliverables:
  - `docs/design/replace_design.md` §R4 (READ FIRST; §R4.0-§R4.14), with
    `[R4: ...]` markers on §R3.1-§R3.5, §R3.7, §R3.9-§R3.13, §R3.16, §R2.5
    rule 4 and §R2.6;
  - `docs/design/subst_api_r4_draft.md`, the draft of the new
    `docs/spec/subst_api.md`: numbered, 10 sections, 86 paragraphs, contents
    block generated, numbering check clean;
  - `docs/design/subst_measurements/r4_probe_ext{,2,3}.py` and
    `r4_transcript.txt`: 97 libpcre2 10.46 cells, answers only.
- Validation: `make test-spec-history` has one red, the known one
  (`tests/compound/CLAUDE.md:125` cites paragraph 8 of section 5 of `measures.md`, as substfix
  reported; it resolves at merge). Every other check passes, including the
  citations this lane wrote. The draft passes `spec_cites.check_numbering`
  and `spec_toc`. No other suite applies to a docs-only change.

## Premise test

Confirmed. Today the element and the glue each take an `rx_subst_binding`
that only `pcrec_subst_bind` can make BOUND (`subst_api.md` §4¶4, §6¶1), so
the bind is mandatory.

## STOP RULE

Did not fire. Every accepted form, `subst-extended` included, is a piece into
one of four places:

- the artifact's constant data (literals, escapes and default text);
- the subject;
- a caller variable;
- the caller's scratch, for case forcing only, sized exactly before any
  write.

## What R4 proposes (summary a fresh agent can resume from)

- **Independence.** The template is compiled without the regex. It publishes
  a REFERENCE LIST in first-appearance order, and the element takes an
  OPTIONAL MAP:
  - NULL means the numbers are the slots;
  - `{slot[]}` is a hand renumbering;
  - `{slot[], run[]}` adds duplicate names (the first participating wins);
  - `RX_SUBST_NOGROUP` is a deliberate "no group".

  The brief's `(first group, count)` entry was argued against: it cannot index
  numbers (duplicate groups are not contiguous) or rows (unnamed groups have
  none). See §R4.3.
- **One check**, `pcrec_subst_check`, which every element call runs first.
  Helper (C), `pcrec_subst_map_names`, resolves by name, can mark an absent
  reference NOGROUP, and ends with the check.
- **Pieces.** `{const unsigned char *p; size_t len}`, at a fixed stride of
  `k * P` per call (empty and padding pieces kept), with `p` never NULL.
  NOSPACE is decided before any write, an error commits the matches before
  it, and nothing is ever searched twice.
- **Unset.** Blank by default, with an `RX_SUBST_STRICT` flag (R6). A
  conditional's test and NOGROUP never error.
- **`subst-extended`** (R5) is designed from measurement. It covers `${n:-t}`
  (unset only), `${n:+s:u}`, escapes, `\Q..\E`, `\1`-`\9` and case forcing.
  Case forcing becomes ONE scratch piece per match, running from the first
  case escape to the end of the template. It is rendered in two passes (size,
  then write), because case state follows output order through branches.
  `\NN` is refused (it depends on the pattern's group count) and `$*MARK`
  stays refused.
- **No glue.** Rulings 4 and 5 remove the glue. Draft §6 carries the
  recipes for `_next`, `_next_n`, `RX_FOREACH` and replacements-only.
- **The support unit** (R7 and R8) is ONE file from `pcrec --emit-support
  [-o FILE]`, standalone, with an implementation guard. It holds the check,
  helper (C), `rx_group_run`, `rx_subst_ctx_init`, `rx_subst_flatten` (KEPT,
  R8) and the UTF-8 case map. Its names carry the abi, so a mismatch fails
  to link. Subst headers then hold types and declarations only.

## Open questions for Frank (§R4.9)

1. The piece pointer type: `unsigned char` (leaning) or `char`.
2. The support file: written by the compiler (leaning) or a fixed file in the
   tree.
3. Every template-using program links the support file once, because the
   render calls its one check (leaning yes), or each template carries a
   private copy of the check.
4. `\10`-style escapes are refused, since they depend on the pattern's group
   count (leaning refuse).
5. Confirm that the generic "substitute into my buffer" loop goes too.

## Findings

- **F-R4-1: the brief's `(first group, count)` entry does not work** for
  either meaning of "group" (§R4.3). R4 replaces it with a slot list plus
  optional runs.
- **F-R4-2: PCRE2's `\NN` replacement escape depends on the pattern's group
  count.** `\10` is the byte 0x08 with one group and group 10 with twelve
  (transcript). A template compiled independently cannot honour it, so the
  draft refuses it and names `${10}` and `\o{10}`.
- **F-R4-3: case state outlives conditional branches** (`${2:-\Ux}y` → `XY`).
  Case regions therefore cannot be fixed at compile time, and the design uses
  one dynamic region per template. PCRE2's single-character combinations are
  irregular (`\L\u` acts as `\U`); the draft reproduces them as measured.
- **F-R4-4: UTF case mapping changes byte length** (`ß` → `ẞ`, 2 → 3 bytes)
  and leaves some characters alone (`ı` under `\U`; U+212A and U+0130 under
  `\L`). The table is a NEW DATA SET. Its proposed home is a table derived
  from `third_party/` UCD, controlled by libpcre2's per-code-point answers in
  `oracle_store/` (§R4.12).
- **F-R4-5: R7 does not delete everything the rulings file expected.** It
  deletes every function body from subst headers (about 250 lines each) and
  the `rx_shape` reserved spelling. It does NOT delete MF1's guard rule or the
  `rx_subst`, `pcrec_subst` and `rx_group` reservations: types, flags and
  support names still use those spellings. What goes is the class "two
  headers define the same function text" (§R4.14).

## Owed at build (none now)

- The build itself, which needs Frank's go. §R4.10 sizes it at about two
  lanes: the interface first, then `subst-extended` and the case data.
- A fresh D27 round for the new surfaces.
- Sabotage ids from a manager-named range: 25 kept, 6 re-aimed, 6 retired,
  about 15 new.
- The per-code-point case-mapping control in `oracle_store/`.
- The cli.md §1.19 hunk (its text is in §R4.14).
