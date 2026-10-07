# [MEMFN-ROWCON] Row contracts: the K96 generalization (design, rev 4.1, narrowed)

Status: rev 4.1, 2026-10-07. It answers the light re-check
(`docs/dev/reviews/2026-10-07-r4-memfn-rowcon-light.md`: B1, M1-M3, and
the S1-S8 table). After these edits N1 builds with no further panel.
Earlier: rev 4, Frank narrowed the item (via the pcrec manager):
"I don't want this to turn into a solution without problem scenario."
This revision builds ONLY the K96 generalization. Everything else is
HELD in §6, with its trigger.

The history (revs 1-3.1, three panels) is in git and in:
- `docs/dev/reviews/2026-10-07-r1-memfn-rowcon.md`;
- `docs/dev/reviews/2026-10-07-r2-memfn-rowcon.md`;
- `docs/dev/reviews/2026-10-07-r3-memfn-rowcon-spotcheck.md`.

Evidence is in `probes/rowcon/`.

## 0. The problem scenario (the only one this solves)

K96: R4c's ofsskip arm was chosen for a site whose `miss` it did not
honour (it returns `n`) and whose `floor` it did not read. That gave
wrong answers and under-reads. pcrec never sent such a site, so it stayed
latent until G2 reached it.

The r1 audit (`probes/rowcon/audit_kit_rows.md`) found the same SHAPE in
8 more cells of the kit's rows, and 13 cells where rows disagree on a
field. All of them are unreachable from pcrec today. **The defect class:
a kit row can be selected for a site it does not serve, because nothing
forces its selection test to cover every field its output depends on.**

## 1. Rules (ruled)

- **R1, use only what is stated.** A row may USE only a value the caller
  STATED; it never presumes one. Fields a row does not use are
  wildcards. Not everything must be stated (Frank, Q-ROW-1 as clarified).
- **R2, a stated value is a requirement.** A row that does not serve a
  stated value DECLINES, even if it never reads the field. That is K96's
  `floor` half.

## 2. The mechanism (kit-internal; the kit's two existing tables)

The kit's two tables are the composer arms (`compose.c` `arms[]`) and
runcmp's rows (`rc_row`). Each row gains two declarations:
- **`uses`:** the fields its output reads.
- **`serves`:** for each field, the value CLASSES it handles. The token
  `ANY` means "irrelevant to this row's output", and is declared, never
  assumed. A field absent from `serves` serves nothing.

**Value classes** come from ONE classify function per field, kept in one
small table (`memfn/src/fields.def`). Each class set is closed and
includes `OTHER`. A value nobody classified lands in `OTHER`. Examples:
- `miss` ∈ {`MISS_N`, `OTHER`}, where `MISS_N` is a miss value that IS the
  site's own `n`: the public token `MF_MISS_N` (memfn.h, compared by
  address; what "unstated" lacked at N2's three would-decline cells), or
  the very text of the `n` hook;
- `floor` ∈ {`ZERO`, `OTHER`};
- **the text-shape classes [r4, S2-S7]:**
  - `s`/`n`/`lo` ∈ {`IDENT`, `OTHER`}, where `IDENT` means a bare C
    identifier, checked lexically;
  - `on_miss`/`on_cand` ∈ {`JUMP` (one `return`/`goto` statement),
    `BRACED`, `OTHER`}.

  A row that pastes text raw serves only `IDENT`/`JUMP`. Generic, which
  parenthesizes and braces, serves `OTHER`. So a non-identifier hook can
  never reach a raw-pasting row: it falls to generic. That makes the
  in-situ hazard IMPOSSIBLE at selection, with no snapshot and no byte
  moved (the hook census shows pcrec passes only identifiers and `return
  0;`). The contract (memfn.h) gains one sentence per class.

**The gate, at BOTH phases [r4 B1].** Most hooks are USE-time (`s`, `n`,
`lo`, `miss`, `on_miss`, the call-time `floor`), so a define-only gate
would miss them.
- **Define:** the gate runs in the existing `select_arm` walk (and the
  runcmp walk), before each row's own predicate, over the define-time
  fields.
- **Use:** the gate RE-CHECKS the chosen row against the use hooks. A use
  the chosen row does not serve is REFUSED, naming the fields. It cannot
  re-select, because the definition is already written. This makes the
  call-time half of K96's fix (`ofsskip.c` use refusals) general,
  instead of deleting it.

In each phase it applies per field the first rule that matches:
1. **used and unstated:** DECLINE (R1).
2. **stated, class not served:** DECLINE (R2).
3. **otherwise:** pass.

A row added later, or a field added to the contract later, is DECLINED
until someone declares it, so it fails toward the generic row or a loud
refusal, never toward a wrong answer. If NO row serves a site, the kit
refuses and names the fields.

**Generic** serves every class of every field it uses. A value it cannot
serve is a contract refusal, checked by G2. That includes a FUNC
`floor` that differs between define and use (S8): generic refuses
the disagreement.

**Fields whose 0 is a real value** (`comment_tier`, `reverse`,
`guard_by_caller`, `on_miss_leaves`, `end_back`, `fn_ref`, `table_ref`)
are per-kind OBLIGATIONS: every builder of that site kind sets them, so 0
is a stated value, not an absence. They carry a WRITTEN exemption in
`fields.def` (r3 M7's list). The rev-3.1 `UNSTATED`/tri-state layout bump
is CUT [r4 M3]: no scenario needs it.

## 3. Visibility: decline reasons in the kit's own trace

Under the kit compile-time switch `MF_TRACE` (off by default), each
selection prints one block to stderr, tagged `MFTRACE`. It gives each row
evaluated with its verdict:
- DENIED (by which deny);
- DECLINED (the mask of every failing field, by name);
- PRED_FALSE;
- CHOSEN.

The line format is documented in `memfn/docs/trace_format.md`. pcrec's
census turns it on through `scripts/emit_sweep.py --trace` (`KITFLAGS`
inherit `CFLAGS`), so there is NO pcrec source change. Nothing reaches an
artifact, and no public struct changes for it. G2 prints the same records
on its failures.

## 4. Reach floors

Under `MF_TRACE`, kit-private counters count CHOSEN per row, and per
(row, used field, class). They are printed at exit and summed by the
census. The independent controls, none derived from `fields.def`:
- **`tests/memfn/rows.tsv`:** a hand-maintained name manifest, one line
  per row, with its reach reason and witness. Rows unreached from pcrec
  take a closed reason: `total-fallback`, `pending-site:<trigger>` or
  `contract-reach:<G2 family>`. Anything else is deleted (D77).
- **A text signature per row,** checked in its witness's artifact.
- **G2:** byte-loop agreement on every reached cell, and a per-row CHOSEN
  floor over G2 (fed by lane g2x's families). Two differentials:
  - the POISON differential: every field a row does not use is set to
    junk, and the render must be identical or the row must decline. It
    catches a row that READS an undeclared field.
  - the SEMANTIC differential [r4 M1]: for every field a row declares
    `ANY`, or serves at more than one class, G2 VARIES that field across
    its classes and checks ANSWERS against the byte loop. It catches a
    row that IGNORES a field it should read, which is K96's actual shape
    (ofsskip ignored `miss` and `floor`).
- **Literal floors in `docs/spec/`:** rows per table, and witnessed rows.

## 5. Steps (each its own commit; gate vs main; always green)

| step | content | pcrec artifact movers |
|---|---|---|
| N1 | `fields.def` + classify (including the text-shape classes); `uses`/`serves` on both tables; the gate in WARN mode at define AND use (verdicts recorded, selection unchanged); `MF_TRACE` + `trace_format.md`; the obligation exemptions | none |
| N2 | the WARN census over the whole corpus × every axis (via `emit_sweep --trace`). **It must show ZERO would-decline verdicts on pcrec sites**; each one found is fixed in `uses`/`serves`, or becomes an R-6 entry | none |
| R-6 | pcrec states what N2 shows its chosen rows use (expected: `MF_MISS_N` at the ofsskip site, define and call, plus any enum N2 names) | none (a pcrec lane) |
| G2u | the blinded G2 update: explicit values, refusal expectations, the poison differential, per-row floors | none |
| N3 | the gate ENFORCES at both phases: precheck serves a stated `miss`; a shape-dependent row is split; ofsskip's ad hoc K96 checks become the general gate (the define AND use halves). ENTRY [r4 M2]: N2's census RE-RUN after R-6, both phases, still zero would-decline; plus the identity gate over the row split | none (census = 0, gate) |
| N4 | `rows.tsv`, signatures, the census floors, the `docs/spec/` literals | none |

The arm names are already in the trace. Listing the composer arms in
`--list-axes` is NOT in scope (no problem scenario asks for it).

## 6. HELD, filed with triggers (do not design further, do not build)

- **H1, the general first-match table engine** (Q-ROW-4: the charter
  widening stays RULED). TRIGGER: a real table, kit or pcrec, wants to
  adopt it. Evidence that §2 does not paint us into a corner:
  - Appendix A of rev 3.1 (in git, `e5f5c0c0..55804fdd`) maps stc2's
    `cand_rows[]` onto an engine head with no special cases;
  - `probes/rowcon/customers.md` lists pcrec's tables.

  §2's `uses`/`serves` gate is the engine's "profile" layer, so it would
  move under an engine unchanged.
- **H2, the hook SNAPSHOT** (Q-ROW-1(c) option B, and Q-ROW-6, ruled).
  TRIGGER: a MEASURED hazard. A census of the hook texts pcrec actually
  passes at every delegated site (`probes/rowcon/hook_census.md`) decides
  it:
  - no risky text → SNAPSHOT stays filed, with that census as its "not
    yet" evidence, and builds when a migration introduces such a hook.
    **RESULT (2026-10-07): NO RISKY HOOK.** Every value hook is a bare
    identifier, `on_miss` is `return 0;`, and the prefix-derived names are
    identifiers. SNAPSHOT stays FILED. Re-run the census at every
    migration step that adds or changes a hook;
  - a risky text → that case goes to Frank.

  Rev 3.1's §5 placement table (in git) is the design to resume.
- **H3, rev 3's T2b** (arm names in `--list-axes`). TRIGGER: someone
  needs the listing.
