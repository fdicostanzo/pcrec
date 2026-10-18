# u1rev — [KIT-VERIFY] U1 design note, revision 2 (lane report)

Lane `u1rev` (opus), 2026-10-18, branch `lane/u1rev` from main `542b0cecb`. DESIGN ONLY
under the box rule: nothing under `src/`, `memfn/`, `tests/` changed; no `make test`, no
timing, no sweep. The only CPU work was a worktree `make build/pcrec` and about 7,000
single-pattern compiles under `nice -n 19` (the recount, about 30 s total).

## Delivered

- `docs/design/kit_proof.md` **revision 2**: every finding of the D6 panel
  `docs/dev/reviews/2026-10-18-r3-kit-proof-u1.md` dispositioned. A new **§R2** maps
  every finding id to the section that discharges it (k3-family B1, M1-M7, m1-m6,
  Q1/Q3, UL-0..UL-8; k3-contract B1-B2, M3-M5, readers, bits, staging, sabotage, R-26
  details, unlocks; k3-sound B1, M1-M4, m1-m5, unlocks). Changed text is marked
  `[r3 <id>]` (62 marks).
- `docs/design/kit_proof/conj.py` (new): the `cover_conj[]` table written as code over the
  emitted anchored machine (kvdfa's reader), with three modes (`census`, `rarm`,
  `witnesses`). `conj.txt` holds its output and `witnesses.txt` its witness list.
  `kit_proof/CLAUDE.md` and `docs/design/CLAUDE.md`'s entry are updated.

## What changed, in one paragraph per theme

- **Definition.** Whole-cover is now `cover_conj[]`, C1-C14, a listed first-match
  conjunct table on `split_conj[]`'s shape. The machine conjuncts close sound B1 (no
  accept below `k` in any form, no eol view at `k`, only the class accept and the end
  view at `k`), M1 (`e(⊥)` is the emitted entry constant, trace-asserted), M2 (C1 on the
  FINISHER route) and m3 (`\G` as conjunct C3). The table also asserts an unmarked A
  (fam-m4). Stage 1 is `CR_DFA` only (ATTEMPT dropped).
- **Producer.** `S_d`, `exact_len` and the hull are `span_facts`' first slice
  (`src/facts/spans.c`, priority-free, UL-0 inside U1). Only the end at `k` and the
  context sets read A. C8 is the two-producer control. `exact_len` is stated over the
  SENT sets. `MkLang` (pattern) / `MkEnd` (machine) / `MkKnown` (subject, a reference to
  the kit's class).
- **R-26.** The carrier is `mf_site.ctx[]`/`nctx`, and the note names the refusals it
  lifts and the per-predicate term cap (`MF_MAX_CTX`, derived). `read_floor` is a new
  enum. REPORT is REQUIRED-all with a DEFAULT-build class check (`pcrec_ctx_fail`). Every
  new field has an UNSTATED zero or is a refused-if-stated wildcard. `kit_class` copies
  `proven0`/`proven_prev`. The K96 readers are named (`fields.def`, `gate.c`, eight
  arms' `[FLD_x]` tables, g2). `MF_MAX_AHEAD` is 1. Completeness is in the bar. R-26.6 is
  the kit's UNROUTED REPORT row.
- **Staging.** Z0 → B3b → Z1 → Zk (the REPORT row unrouted) → X0 → Z2 (harness lever
  `build/pcrec-harness --harness=kit-proof` only; C17 `pending`; `.list` at B1) →
  measure → B4 lockdown → B1.
- **Checks.** X0 is an independent per-position, per-byte libpcre2 oracle, set-equal and
  with full-alphabet subjects, run BEFORE Z2. X5 is byte identity. K35 gets a getwidth
  denominator, `selected ⊆ engine dfa`, and a `why` split `no-row`/`kit-denied`/
  `kit-none`. Sabotage S1130-S1148 is PROPOSED, the six missing plants and sound's three
  included.
- **Family / Frank.** Rows are distinct by walk, and the fact and the finisher are
  source-neutral. `-fno-kit-proof` is a FACT deny (bit 57; 7 free → 6). `compound.c:199`
  and `:235` become typed field reads. Q1 is RULED (→ [CAPS-KNOWN]). Q2-Q4 carry the
  panel's answers, PENDING FRANK'S RULING.

## Populations, recounted (`kit_proof/conj.txt`)

| quantity | bench native / utf8 | corpus native / utf8 |
|---|---:|---:|
| stage-1 sites (`CR_DFA`, origin start, whole) | 66 / 46 | 560 / 413 |
| patterns `cover_conj[]` C1-C12 admits | 66 / 46 | 558 / 413 |
| context joins admitted (start-origin site) | 6 / 3 | 68 / 56 |
| context joins the machine admits, no start-origin site (U-ctxorigin) | 0 / 0 | 12 / 9 |
| stage-1 sites whose sent span 0 is shorter than `k` | 33 / 33 | 129 / 160 |
| end-anchored bodies declining at `no-eol-view` under `-fno-rev-end` | 8 / 7 | 75 / 69 |

These reproduce the panel's numbers: 66 / 560 and 46 / 413 (k3-sound M2), and 80 / 65
corpus context joins before the origin conjunct (k3-sound M4).

## Findings of this lane

- **Instrument defect (own, fixed).** `conj.py`'s first run passed the pattern to argv as
  a Python `str`. Python re-encodes that as UTF-8, so 8 utf8-born corpus patterns
  compiled as different bytes and read `exact`. The pattern now goes to argv as its own
  bytes. The same defect class appears in the startset census record.
- **Revision 1's `DFA_HAT 6` stage-1 row was wrong**: every DFA_HAT whole-cover site sits
  on a VM-engine artifact (a hybrid), so it is a VM-finisher site.
- **`(?m)^` leaves stage 1** with `CR_ATTEMPT`: `(?m)^` bodies take the attempt route
  (C1). Revision 1 listed it as expressible in stage 1. It is now U-bisim's.
- **Under `-fno-rev-end`, `\z` bodies become `cover` artifacts** (1 bench / 10 corpus,
  e.g. `done\z`). That is correct (an end view, empty `C_k`, absent SATISFIES) and is
  U-z's population.

## Could NOT discharge (with reasons)

1. **X0 itself was not run.** It is the per-byte libpcre2 oracle plus the full-alphabet
   differential over the admitted population: a heavy differential, outside this lane's
   box rule (design only, no sweeps). It is designed (§6.4) and placed before Z2 (§7).
   The k3-sound critic's run (4.0M + 0.5M cells, 0 differences) is its precursor on the
   critic's instrument.
2. **The getwidth K35 denominator's number** is designed, not counted (same rule). It is
   a python `sre_parse` pass over the corpus and bench, cheap, owed at Z2.
3. **The per-field `serves`/`uses` cells of every kit arm** for the new fields are named
   (§4.3) but not written: they are the kit's at Z1 (K96, the kit's tables).
4. **Whether `cand_rows[]`'s self-check admits a row with no `.list` at Z2** was not
   verified in code. The note gives both outcomes: no `.list` until B1, or a declared
   `--list-axes` delta at Z2.
5. **B1 after B4** is a proposal: the order is stated and argued (§7), and the kit
   session must agree, since B4's lockdown is theirs.

## Validation

None owed beyond the design: this lane ships no code. `conj.py`'s three modes ran to
completion (`conj.txt`, 143 lines). The witnesses read as §1.1 states.
