# Bench request DRAFT: R-17's set-FIND forms on real subjects (the gate before R17-b merges)

**Revision 2 (lane r17r23, 2026-10-12, the r5 light re-check, K3-4/K3-5):**
§2 item 3 drops "state-losing by construction"; §4's gate rule changes
(reproduce-on-rerun, F from the bench's spread or three layout-perturbed A/A
pairs, the absolute criterion on every cell, no 0.05 floor); §5 and Q3 ask
for uses per activation. Relayed to the bench as a corrigendum to I-148:
`setfind_bench_corrigendum_I148.md`.

Draft by the memfn kit (lane r17r22, 2026-10-12) for the pcrec manager to
relay to pcrec-bench (D78: main writes the bench's inbox; the kit never writes
to pcrec-bench). It is written to stand alone: the bench needs nothing else
to act on it. Design behind it: `docs/design/memfn/setfind.md` revision 2.2
(§9.2, §11.2a). Ruling that makes it a gate: D162 addendum 1 (Frank,
2026-10-12): the kit's stateful forms ADMIT by default, and "the bench relay
on real subjects is the gate before the routing event lands: a real cell
losing beyond the regression floor returns to the kit before merge."

## 1. What changes, in one paragraph

Today, when a pcrec artifact looks for the next position whose byte is in a
small set S (the DFA prefilter, the DFA hat, the VM hat), it walks a 256-entry
table one byte at a time. R17-b replaces that walk, wherever S is covered by
at most four simple terms, with a kit form that tests a whole word at once and
CARRIES the word's membership mask between candidates, so a second candidate
in the same word costs a bit-scan instead of a restart. Kit timings (Zen 4,
synthetic subjects, unofficial) show it 2-17x faster on sparse sets and about
0.86x of the walk on dense ones while the state carries, but up to about
1.65-1.83x SLOWER where every candidate is a true match (the state dies with
the call) at around 300k candidates per million bytes, on dense per-call
spans, and on clustered runs. The kit cannot tell from synthetic text how
often real subjects sit in those corners. The bench can.

## 2. Which cells

**Phase A (gates R17-b):**
1. **The R-17 named cells** (the bench cells whose losses opened R-17, each
   with the kit's twin name):

   | bench cell | kit cell | S | site |
   |---|---|---|---|
   | `utf8/alt-distinct-lead` | `adl` | {63,D0,E6} | DFA prefilter |
   | `utf8/ci-sigma` | `sig` | {CE,CF} | DFA prefilter |
   | `utf8/ci-kelvin` | `kel` | {4B,6B,E2} | DFA prefilter |
   | `utf8/ci-turkish-i` | `tki` | {49,69} | DFA prefilter |
   | `syntax/alt-nested`, `syntax/alt-two` | `alt2`, `alt2r` | {63,64} | DFA prefilter |
   | `capability/high-byte-run` | `hbr`, `hbrc` | 80..FF | DFA prefilter |
   | `capability/utf8-lead-no-cont` | `u8l` | C2..DF | DFA prefilter, bounded |
   | `capability/quoted-delim-match` | `qdm` | {22,27} | VM hat |
   | `syntax/bak-k-named` | `bkn` | {3C} | VM hat |
   | `capability/balanced-parens-rec` | `bpr` | {28} | VM hat |

2. **The dense controls** `lc` ([a-z]) and `dig` ([0-9]): the bench cells
   whose prefilter set is a lowercase or digit range and which do not lose
   today (question Q1 asks the bench to name them), plus any other cell the
   bench knows to be candidate-dense (most bytes in S).
3. **Every bench cell whose artifact moves at R17-b.** Main supplies this list
   from the pcrec-side mover census over the bench's own patterns (emitted C
   before and after R17-b, walk → kit form). It includes any VM-hybrid cell
   whose prefilter function moves. That site's state lives for one call of
   the prefilter function, which is entered once per VM re-seed; within one
   call, every candidate the prefilter's DFA rejects is another use of the
   same state. How many uses one call serves depends on the subject, so these
   cells must be read, with uses per activation reported where the bench can
   count it (§5).

**Phase B (the SIMD arms' acceptance, later, per box):** the same cells, when
the SIMD arms `mask64_sse2` / `mask64_avx2` land (D144 addendum 4, D147: they
must beat the current scalar form on the hardware each one targets).

## 3. Which arms

All arms are ONE pinned pcrec commit (the R17-b branch); they differ only by
flags, so a difference between arms is the form and nothing else.

| arm | flags | what it is |
|---|---|---|
| A1 FLOOR | `--memfn=no-pf-terms-mask` | today's table walk |
| A0 NEW | (none) | SIMD-off: `mask8_swar`, the recommended portable form |
| A1′ A/A | `--memfn=no-pf-terms-mask`, a second testee build with a DIFFERENT CODE LAYOUT (e.g. built with another `-falign-functions` value, or with padding) | the same program as A1, laid out differently, to measure the floor including layout noise (§4) |
| B0 (phase B) | `-fmemfn-simd` | SIMD-on: `mask64_sse2` or `mask64_avx2`, the kit's per-box choice |
| B1 (phase B) | `-fmemfn-simd --memfn=no-pf-terms-mask` | the walk at SIMD-on |

In phase A the SIMD-on layer's artifacts are byte-identical to SIMD-off at
these sites (no SIMD arm exists yet), so phase A reads SIMD-off only and says
so. Phase B adds B0 against both B1 and A0 (D147: SIMD must beat the current
scalar).

**Boxes.** Phase A on ubuntubudu (Zen 1, the bench's home box) AND on the
Linux dev box (Zen 4, where the kit measured), because the portable form must
not lose on either. Phase B per width on the boxes that run it: SSE2 on both,
AVX2 on the dev box (native) and on ubuntubudu (2x128 µops) as a separate
reading. Main schedules the boxes (one heavy run at a time).

## 4. What "loses beyond the regression floor" means (PROPOSED)

> **SUPERSEDED (2026-10-12, kit manager):** the operative gate rule is the ONE
> merged rule in `setfind_bench_corrigendum_I148.md` §1. It combines the kit's
> review fixes with the bench's O-98 additions: disjoint trial ranges, subject
> grain, and the 0.05 floor KEPT. A1′ is the align64 placement twin, one per
> set. The text below is the revision-2 draft, kept for history.

The kit proposes the following; main and the bench should replace any part
with the bench's existing comparison rule where one applies, and say so in
the result.

A cell (one bench cell, one regime, one box) **LOSES** iff ALL of:
1. both arms' records are pinned and their trials AGREE (no
   `inconclusive-spread`; such a cell is reported, re-run once, and if still
   inconclusive is listed as UNJUDGED, not as a pass);
2. **ratio:** median(A0) / median(A1) > 1 + F, where F is:
   - the bench's STANDING per-cell spread figure for that cell, regime and
     box, where the bench has one (Q6);
   - otherwise the largest |median(A1′) / median(A1) - 1| over AT LEAST THREE
     A/A pairs from the same window, each pair LAYOUT-PERTURBED: A1′ is the
     same program as A1 built with a different code layout (a different
     `-falign-functions` value, or a padded build), so F covers placement
     effects as well as run-to-run noise. A same-binary pair cannot see
     layout, and pcrec has measured 1.33x from code placement alone (K24);
3. **absolute, on EVERY cell:** median(A0) - median(A1) also exceeds the
   absolute A/A delta from the same source as F (the bench's standing
   absolute spread, or the largest absolute delta of the A/A pairs);
4. **reproduced:** a cell that meets 1-3 is re-run IMMEDIATELY (same window,
   same binaries), and LOSES only if the re-run meets 1-3 too. A loss that does
   not reproduce is reported as a TIE marked "not reproduced", with both
   readings.

The kit's earlier 0.05 floor on F is withdrawn: it was the kit's own noise
band, measured on synthetic subjects in the kit's driver, not the bench's.

A cell **WINS** symmetrically (ratio < 1 - F and the absolute delta beyond
the A/A delta); a win needs no re-run, because the gate reads losses only.
Anything else is a TIE.

**The gate.** Phase A PASSES iff no cell LOSES on either box. A losing cell
returns R17-b to the kit with the cell, its regime, its box, both medians and
the subject facts of §5; the kit decides (setfind.md §11.2a: a state-lost
dense cell is [FINDALL-NEXT]'s residual and main rules whether it blocks; or
the kit narrows the admission by a stated, measured predicate; or R17-b
waits). Wins and ties are reported too: the gate is about losses, the
decision record needs all three.

## 5. Which regimes, and the subject facts to report beside each cell

**Regimes:** the bench's own, on its own subjects:
- **find-all** (the driver's loop of searches over one subject, each call
  starting after the previous match);
- **per-call** (one search per subject, the bench's short-subject regime),
  where the cell has one.

**Beside each cell, per subject** (the kit supplies S per cell in §2; the
bench measures from its subject):
- **candidate density:** the fraction of subject bytes in S, in ppm;
- **run profile:** the mean length of runs of consecutive bytes in S, and the
  mean gap between them;
- **if the harness can count it, either of:** candidates per true match (how
  many set hits the search passes per match it reports, find-all), or uses
  per activation (how many times one search call, or one call of a hybrid's
  prefilter function, asks the set search for the next candidate). This is
  the state's lifetime. The kit's break-even lies between 1 and 4 uses per
  lifetime (it loses at 1 and wins at 4; nothing between was timed);
- **subject size, and whether the timed loop rescans the same subject** (see
  below).

**Why real subjects matter (the 64K caveat).** The kit's harness rescans one
synthetic subject per sample. At 64 KiB the table walk ran at 0.65 ns/byte at
300k density, against 1.91 ns/byte at 1 MiB, with 0.038 branch misses per
call: consistent with the branch predictor having LEARNED the repeated stream.
That makes the kit's 64K dense numbers the hardest case for the new form, and
its 1 MiB numbers the easiest. A real subject, with a consumer's work between
calls, lies somewhere between, and the kit cannot tell where. That is why the
gate is the bench's reading, not the kit's.

## 6. Questions for the bench

- **Q1.** Which bench cells are the dense controls: the patterns whose
  prefilter set is [a-z] or [0-9] (the kit's `lc`/`dig`), or the most
  candidate-dense set sites the bench has?
- **Q2.** In the find-all regime, does a timed sample rescan the same subject,
  and how large are the subjects? (The 64K caveat above depends on it.)
- **Q3.** Can the bench report density, run profile, and candidates per match
  or uses per activation, per subject (S given per cell), or should main
  compute them read-only from the bench's subjects? (If neither count is
  possible, the kit can count uses per activation in a pcrec trace build
  instead; say so.)
- **Q4.** Can the pcrec testee adapter pass `--memfn=no-pf-terms-mask` and
  `-fmemfn-simd` through to pcrec, or must main hand the bench separately
  built testees per arm?
- **Q5.** Does the bench already have a comparison rule for "a regression"
  between two pcrec arms? If so, the kit asks the bench to use it in place of
  §4 and to state it.
- **Q6.** Does the bench have a standing per-cell spread figure to use as F?
  If not, are at least three layout-perturbed A/A pairs per cell feasible in
  one window (§4)?
- **Q7.** Phase A needs both boxes. Is a dev-box (Zen 4) run of the bench
  available in the same window shape as ubuntubudu's, or does it need its own
  slot request?

## 7. What the kit sends back to main after the reading

A verdict table per box: cell × regime × arm, the medians, F, WIN/TIE/LOSS,
and the subject facts; the gate's PASS/RETURN; and, for every LOSS, which of
setfind.md §9.2's corners it sits in ((a) state-lost dense, (b) dense
per-call, (c) clustered runs) or "none" (a new finding).
