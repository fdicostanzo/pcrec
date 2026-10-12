# docs/design/compound/twin/ — the split twin ([COMPOUND] design lanes mscomp and mscomp2, 2026-10-12)

Hand-composed compounds built from UNCHANGED `build/pcrec` compiles plus a
hand-written controller: the evidence behind `../../compound.md` §B and §E.2.
Light measurement only (counted loads, an every-startpos differential); no clock.
Scratch output goes under the worktree's `build/` (never committed). Revision 1
(lane mscomp, as [COMPOSITE]) and revision 2 (lane mscomp2) files sit side by
side; revision 2's are the ones the note cites.

Revision 2 (cited by the note):
- `twin2.py` — per case: Q DERIVED the way the build derives it (a small
  parser: kill `\G` always, `^`/`\A` outside lookbehinds and when no `(?m)`, to
  an EMPTY CLASS; prune bottom-up; a never arm holding a capture group kept,
  logged `keepcap`), F = P compiled guards-off with its attempt bound patched
  to `start_max = search_from` (`bound_floor`; P's `_match_caps` when there is
  no DFA attempt loop), today's artifact compiled per option arm (byte; utf8 x
  {refuse, none, align} x {`-futf-check` off, on}), the controller from
  `ctrl2.c.in`, linked with `diff.c` and run over generated subjects carrying
  the pattern's witness bytes (asserted) and the panel's witness subjects.
  `--plant N` builds a failing-direction controller (1: Q from `from`; 2: the
  utf check with Q's reach; 3: no prologue).
- `ctrl2.c.in` — the revision-2 controller: one prologue from P, the bounded F,
  Q from `next_pos(f)`, `QNEVER` for the floor-only form, the plants.
- `cost2.py` — counted subject loads of a whole find-all, today vs the compound
  (derived Q, bounded F), pin-only cells including matching subjects.
- `probes2.py` — the generators revision 1 lacked: `sizes` (linked bytes,
  today vs compound) and `one-tu` (the one-translation-unit `-Werror` probe).
- `results/cases2.tsv` (revision 1's 94 cases + 18 panel witnesses),
  `split_differential2.tsv` (177 case-arms, 2,170,123 cells, 0 differences),
  `plants.tsv`, `split_loads2.tsv`, `sizes2.tsv`, `one_tu_probe2.txt`.

Revision 1 (history): `twin.py` (textual kill to `(?!)`, Q mostly VM),
`ctrl.c.in`, `cost.py` (also the shared `count`/`CFLAGS` that `cost2.py`
imports), `diff.c` (shared by both revisions), `sqli_p.txt`/`sqli_np.txt`
(empty in the tree; `cost.py`'s sqli cells read them), `results/cases.tsv`,
`split_differential.tsv`, `split_differential_literal.tsv`,
`split_loads.tsv`, `sizes.tsv`, `one_tu_probe.txt` (hand-run; superseded by
`probes2.py`).

Reproduce revision 2 from the worktree root (TMPDIR inside the worktree; about
4 min each on 4 cores for the differential, split the case list 4 ways):
`python3 docs/design/compound/twin/twin2.py build/pcrec docs/design/compound/twin/results/cases2.tsv build/sc/t2`
`python3 docs/design/compound/twin/twin2.py build/pcrec CASES build/sc/pl --plant N`
`python3 docs/design/compound/twin/cost2.py build/pcrec build/sc/cost2`
`python3 docs/design/compound/twin/probes2.py build/pcrec build/sc/pr sizes|one-tu`
