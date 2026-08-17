# R28 — D6 landing panel on [M4.6d] MRL pruning (2026-08-17)

Panel on the delivered lane/mrl branch (handback at eaf6049), three
read-only critics with distinct lenses: r28sound (opus,
engine-soundness; permitted to compile individual artifacts in
scratchpad), r28instr (sonnet, instruments/checks — this project's
vacuous-green specialty), r28claims (sonnet, claims-vs-artifacts).
Design-note relitigation was out of scope (R26 owns that). Compiled by
the manager; change requests executed by the mrl lane in the same
session (delta report referenced at the bottom). Frank's accept-as-is
ruling on the +8% shape (D51 addendum) was taken in parallel and is
NOT a panel item.

## Verdicts

- r28sound: **SOUND TO MERGE** — no soundness hole; all six attacked
  claims survived; ~285k-cell independent differential battery, zero
  real divergences.
- r28instr: not clean as delivered — two MAJORS (both closed by the
  lane before merge, below).
- r28claims: handback **faithful** — every headline number traces to a
  real on-branch artifact; independent 10,168-count reconciliation.

## What SURVIVED attack (risk retired, recorded on purpose)

- pcrec_minw a true lower bound at every AKind (exhaustive switch, no
  live default; saturation errs safe twice; nullability agrees
  arm-for-arm with vm_nullable).
- Lattice rounding direction correct at strides 2/3, exact-minimum and
  off-lattice; underflow closed by construction (MRL_SHORT ordering).
- Vm.fdyn: never negative (trip guard bounds the trailed slot), never
  double-counted (fmin=F not cf when the runtime term is in force —
  verified in emitted text on nested-counter shapes); instrumented
  abort-on-negative builds, zero firings.
- The revdet negative answer to prediction 6 could not be refuted; the
  shortl-not-fulll trap is real and correctly handled, lazy extension's
  rx_fail stop justified at the site.
- Possessive arm confirmed TEST-not-clamp in source and emitted C; MRL
  soundness does not couple to possessify's.
- Obligations (a)/(b): ceil_ assigned at exactly two sites, both from a
  fresh window; parameter-not-member means forgetting is a compile
  error; the stamp and the emitted form derive from one fact and cannot
  disagree.
- §1b's stv[N]))) grep hand-traced non-vacuous (only the fdyn path
  emits that suffix, all four stv emission sites checked).
- The three harness fixes and the D45 third-fix disposition; the
  floor-with-window is a fixed 64-byte literal, cannot silently widen.
- All archives non-empty with D35 headers; gate arithmetic (floor×0.9)
  verified; the 10,168 count reconciled independently (+191 mrl cases
  counting g/gp lines per run.sh's accounting, +2 from the resident's
  move into the counted tree).
- r28sound's window-ceiling isolator: every flagged row was the v1
  ceiling ANSWERING CORRECTLY where subject-end exhausted budget — D51
  ruling 2 working as designed on the unsound-direction axis.

## Findings and dispositions

**R28-1 — MAJOR (r28instr): MRL had ZERO sabotage coverage** while
every sibling rung has 3-5 (S45-S57). DISPOSITION: FIX-BEFORE-MERGE —
lane authored S58-S62 and validated each fires; S60 independently
surfaced the self-rounding property (see R28-3).

**R28-2 — MAJOR (r28instr): the DIFF_A_MAY_ANSWER_MORE exemption was
untracked and stale** — the driver silently excused with no counter,
and the "2 cells" figure predated the corpus growing to 202,458.
DISPOSITION: FIX-BEFORE-MERGE — driver prints "excused: N",
run_mrldiff.sh asserts against a pinned value; the re-measure moved
the number 2 → 22 at the shipping corpus, vindicating the finding.
Direction logic itself was traced sound by both r28instr and r28sound
(answer-vs-answer mismatch can never be excused).

**R28-3 — MINOR, the panel's best (r28sound): the lattice rounding is
behaviorally DEAD in the delivered form and its named regression guard
could not fail.** The fold of the clamp into the scan's loop guard is
what makes R26 E1 inexpressible (floor∘floor identity); proven by a
sabotaged MRL_CAP with rounding removed — byte-identical answers over
1,240 subjects at strides 2/3. Cell 2's structural half grepped the
stride ARGUMENT, not the division — a check that cannot fail; and the
emitter comment credited the rounding with the safety the fold
provides. Rounding KEPT as defence-in-depth (it becomes load-bearing
if the clamp is ever un-folded). DISPOSITION: FIX-BEFORE-MERGE —
comment re-attributed to the fold; cell 2 greps the division so
removing the rounding is loud. This is the control-shares-source
family, caught by the panel in the landing's own guard.

**R28-4 — MINOR (r28sound): the 22 excused cells are exactly the
highest-MRL-work shapes, previously taken on trust.** DISPOSITION:
FIX-BEFORE-MERGE — third-arm referee added for excused cells only:
--no-captures selects the pure DFA engine (MRL-free, terminating where
python hangs); the excused span is re-derived and asserted.

**R28-5 — MINOR (r28sound): the primary differential shares the
emitter across both arms.** The critic built the missing
independent-engine arm and ran it clean (74×1,305, 0 span
divergences). DISPOSITION: adopt dfadiff.py into
docs/design/mrl_impl/probes/ as an ages-freely archived instrument
with provenance; NOT battery-wired.

**R28-6 — MINOR (r28claims): plan.md's "16/16" stale vs the final
19/19** (the counter-rung fix added three checks after that prose).
DISPOSITION: FIX-BEFORE-MERGE with the count reconciliation below.

**R28-7 — MINOR (r28instr + r28claims): three contradictory cell
totals in committed files** (174,486 / 176,276 / 202,458).
DISPOSITION: FIX-BEFORE-MERGE — all reconciled to the re-measured
final figure.

**R28-8 — NIT (r28sound): two riders written down rather than
discovered later** — the retry-recompute path is structurally
unexercised (and the two arms run different search loops if it ever
fires, so the differential has no ground truth for it); vm_dyn_add's
VM_MRL_DYN_MAX retreat (>240 chars) under-estimates safely but
UNSTAMPED. DISPOSITION: documented in the design note §14; disclosure
counter added if trivial, else recorded residual.

## Reflection

The panel earned its cost twice over. First: the sabotage-coverage gap
(R28-1) and the dead-check finding (R28-3) are both instances of the
project's oldest lesson — a green board proves nothing until something
demonstrates it can go red — found in the landing of the very lane
that had itself caught a vacuous control (D45's third) days into the
same arc. Nobody is exempt, including the careful. Second: the
exemption re-measure (2 → 22) shows why counts must be re-run numbers,
not copied ones. Process note for briefs: three lanes today wrote
final reports as plain assistant text that never reached the manager —
every brief's deliverable line must say "report via SendMessage"
explicitly.
