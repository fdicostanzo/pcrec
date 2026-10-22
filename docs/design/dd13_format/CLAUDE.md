# docs/design/dd13_format/ — the [DD-13] unified file format design

Design material for plan row [DD-13]: the unified pattern-source / test
file format (compilation manifest + test carrier + pcrec-bench set
format). Staged: [DD-13a] requirements, [DD-13b] design (waves W1, W23),
[DD-13c] adversarial panel; the original rule was that no parser is written
before (c) closes (D6 panel gate). The format is a DIALECT: existing `.rxt`
files stay valid and unchanged (R-COMPAT-1).

## Standing rules

- `frank_inputs.md` is append-only and dated (Frank's requirements, rulings-in-direction, OD-n ledger).
- `bench_rxt_needs_v1.md` is a verbatim received input: never edit its verbatim half; re-fetch from pcrec-bench and diff on any doubt. The [DD-13b.W23] revision builds against this copy.
- Design notes are revisioned documents with a finding-by-finding revision record (format_design.md §0.x, w1_impl.md §0.4, w23_impl.md §0.5) for each panel round (reviews under `docs/dev/reviews/`); read a note's newest revision record first. Claim kinds: MEASURED / CITED / ARGUED / DECIDED.
- Panel rounds are D6 panels; rulings by Frank (D87, D99, F-Q1, F-Q2) bind the design: D99 = the `.rxt` file's purpose is DEFINING RX, primarily for pcrec (bench use must not distract); aux production `ext <consumer>` is parsed structurally but never interpreted (graduation rule: once pcrec must ACT on aux content it graduates to a real production).
- Any grammar/semantic change updates the matching spec (`docs/spec/rxt_format.md`, D80) in the same change; a ratification ask to Frank must state which underlying needs are tentative.

## Files

- `frank_inputs.md` — Frank's dated requirements/rulings/OD-n ledger feeding [DD-13a].
- `requirements.md` — [DD-13a] requirements note (R-RXT-*, R-VE-*, R-VF-*, R-VG-*, R-BENCH-*, R-GEN-*, R-SUBST-*; OD-1..5, tensions, anti-requirements); paneled R27.
- `format_design.md` — [DD-13b] design note (grammar, semantics, schema, migration, seams, attack list, worked files); current revision 3.4.2 (D99 narrowing, aux production `ext`, structure layer S0-S3, `.def` schema table).
- `w1_impl.md` — [DD-13b.W1] implementation note (wave 1: composer, checks, sabotage plan, D80 spec deltas, four steps); rev 2.4, paneled r45; design phase complete.
- `w23_impl.md` — [DD-13b.W23] implementation note (rev 1.1, r59 fix round; staging, spec deltas, checks, per-step checklist).
- `usecases_and_outline.md` — manager's position paper for Frank (use cases U1-U11, line-kind outline in three waves, six rulings).
- `bench_rxt_needs_v1.md` — pcrec-bench's `rxt_needs_v1.md` verbatim ([B42] needs N-1..N-53, 41-check acceptance list) with Frank's F-Q1/F-Q2 rulings.

## Pointers

docs/dev/plan.md [DD-13], docs/dev/decisions.md D87 / D99 / D80, docs/spec/rxt_format.md, docs/dev/reviews/ (r27, r44, r45, r57, r58, r59), docs/dev/known_issues.md K57, docs/design/subst_template_design.md.

Maintenance: update this file when files are added/removed or change roles.

History (long narrative, dated notes, measurements, per-lane records; not auto-injected): docs/dev/history/claude_md/docs__design__dd13_format.md
