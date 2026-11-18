# formsfixm report: review r45 (FORMS8-1..5) on the span forms' cards (R-45 plan A)

Lane formsfixm (kit lane, opus), branch `lane/memfn-formsfixm`, cut from `lane/memfn-formsfixl` @ 3fd31c86d.
Review: `docs/dev/reviews/2026-11-18-r45-memfn-forms8.md` (+ dir: the critic's drill scripts, logs and
the scratch patch they ran against). Design text: `docs/design/memfn/r45_reply.md` rev 13.1
("Changes in rev 13.1"). Script: `memfn/tests/span_forms/cards.py`.

## STATE AT HANDOFF

STATE: delivered. Every RULING applied in its primary form; the FORMS8-1 FALLBACK (record-only) was
NOT needed: (a)+(c) passed in `selftest --rev12` at ~06:07, before the 08:30 cut-off. Rulings file
`docs/dev/lanes/formsfixm_rulings.md`: empty at every poll (last read before the full selftest);
no entry applied. Validation: complete (full selftest 222 / 0 failed, make strict, doc checks; numbers below).
Owed: none. Files outside the brief's three: `docs/dev/reviews/CLAUDE.md` (the review's line, as the
brief asked), the review's evidence dir, and the lanes history index line (lanes/CLAUDE.md N-1 rule).

## FIXES BY ID

Fail-before lines: `scratch/memfn/formsfixm/failbefore.log` (the new gated rows read with
`INTER_PE_PER_TEXT` off, which is 3fd31c86d's `text_interaction` branch verbatim, every other part of
the rule as in this lane) and the critic's c1.py against 3fd31c86d. Pass-after lines:
`scratch/memfn/formsfixm/rev12.log` (`selftest --rev12`) and the full selftest.

- **FORMS8-1 (a)** The lack of fit is read against each TEXT's OWN pure error, never the per-regime
  pool over the night's texts. The pool now gives only the noise's SHAPE across a text's regimes
  (rows weighed by their regime variance). The line is an F with Satterthwaite effective df on each
  side, both shrunk by 1 / (1 + kappa / 2), where kappa is the night's excess kurtosis of the
  standardized pure-error deviations. Launches are first winsorized at `INTER_CLIP` = 4 robust sigmas
  (`_clipped`). Why not the robust median form: per-text df suffice (~12 pure-error df on a head
  text). The per-text F alone fixed the 2x-text row: 1 of 100 flagged, against the critic's 100. It
  left t(5) at 21 of 300 nights flagged. Clipping closed that while keeping the F statistic. The
  sweep that set `INTER_CLIP` (labelled MEASURED in place, on synthetic models only), at clip
  none / 5 / 4 / 3.5 / 3:
  - t(5) nights flagged: 21 / 9 / 11 / 10 / 10 of 300;
  - r44 A heads τ 3 %: 0.010 / 0.013 / 0.023 / 0.030 / 0.053.
  `INTER_MIN_PE_DF` = 4 is an UNMEASURED DEFAULT.
- **FORMS8-1 (c)** New gated rows (layout "phase" 1 %, one 5 % H(8) win in hit-dense):
  - before: `FAIL (r45 FORMS8-1) no interaction, t(5) launches     nights flagged 166 of 300 (accept <= 0.05); h* = 8 in 92 with the void, 201 without (accept >= 0.9 x)`
  - before: `FAIL (r45 FORMS8-1) no interaction, one pattern's (hex24) head arms at 2x sigma nights flagged 300 of 300 (accept <= 0.05); h* = 8 in 0 with the void, 174 without (accept >= 0.9 x)`
  - after: `ok   (r45 FORMS8-1) no interaction, t(5) launches     nights flagged 11 of 300 (accept <= 0.05); h* = 8 in 203 with the void, 201 without (accept >= 0.9 x)`
  - after: `ok   (r45 FORMS8-1) no interaction, one pattern's (hex24) head arms at 2x sigma nights flagged 6 of 300 (accept <= 0.05); h* = 8 in 175 with the void, 174 without (accept >= 0.9 x)`
  - controls (in the selftest): `ok   (r45 FORMS8-1) control: t(5) launches, r44's pooled pure error nights flagged 166 of 300 (the drill sees the defect: accept > 0.05)`; 2x: `nights flagged 300 of 300`.
- **FORMS8-1 (b)** The scope is unchanged (one void cell = no pick that night). It is now STATED in
  three places: rev 13.1 (table row and the §3 interaction paragraph), the cards.py comment at
  `INTER_SHARE`, and `rule`'s interaction line ("ONE flagged text voids the night's pick (r1 step 5)").
- **FORMS8-2** `pool_size_refusal` + `main`: a POOL_SIZE other than 4 is refused at start (exit 2).
  - before (critic's c1.py on 3fd31c86d, `POOL_SIZE=8`): `refusal: variants 1 and 5 of one relative layout share the 32-B phases (7,); variants 0 and 4 of one relative layout share the 32-B phases (8,); 4 distinct built layouts of 8 variants (text_var charges sL2 / 8)`. That is every pool refused, and there is no start-time refusal (no such function on 3fd31c86d, so the row cannot run there).
  - after: `ok   (r45 FORMS8-2) POOL_SIZE other than 4 refused at start refused: 2, 3, 8; \`POOL_SIZE=8 cards.py plan\` exit 2, cards: REFUSED: POOL_SIZE=8: ...`
- **FORMS8-3** DOC: rev 13.1 and the cards.py comment now say that `INTER_SHARE` is an index, not the
  variance share, and does not bind today. PLAN stated in both: an effect-size floor, trigger = the
  first real night that flags a text. RECORD rows:
  - `REC  (r45 FORMS8-3) interaction 0.5 % x main 1 %      nights flagged 10 of 300; h* = 8 in 280 with the void, 291 without`
  - `REC  (r45 FORMS8-3) interaction 0.5 % x main 0 %      nights flagged 13 of 300; h* = 8 in 264 with the void, 286 without`
  - The critic read these on rev 13: flagged ~27 % of nights, power 144 / 193 and 132 / 189 of 200.
- **FORMS8-4** DOC: the coupling is stated in rev 13.1 (table row and §3) and in the cards.py
  comment. RECORD rows (the new line and the per-head floor together):
  - onereg hit-dense τ 3 %: 0.013 (288 flagged) vs 0.200 with the void off;
  - onereg τ 5 %: 0.010 (300) vs 0.220;
  - mix 3 % x 1.5 %: 0.023 (268) vs 0.183.
  - The 0.5 % rows above are the "interaction just below the line".
- **FORMS8-5** DOC: the `SIGMA_READ_BIAS` comment and rev 13.1 now read "MEASURED on the drill's
  SYNTHETIC model (r44 V11), not on night data; on a real night an UNMEASURED correction".

Earlier rows that MOVED (none loosened; both readings):
- `(r44 A)` heads τ 2 %: 0.000 -> 0.003. τ 3 %: 0.000 -> 0.023 (accept <= 0.05). The first-void
  RECORD went 0.920 / 0.937 -> 0.110 / 0.873. Rev 13's line voided ~80 texts a night under this
  model, which left the agreement gate's estimators few cells. The new line voids 10-23 texts, the
  head texts.
- `(r44 B)` power beside a noisy loser: 281 -> 275 of 300 (accept >= 270).
- `POWER_RECORD` pins (r44 L) went red on the first `--rev12` run and were re-pinned:
  - τ 1 %: (204, 296, 179) -> (203, 296, 183);
  - τ 2 %: (25, 271, 18) -> (25, 267, 18). The 10 % winner at 2 % now reads below rev 11's line
    270 (a RECORD row).
- RECORD rows that moved: rho 0.8 τ 2/3 % 0.277/0.350 -> 0.253/0.317; rho 0.95 0.110/0.577/0.627
  -> 0.120/0.583/0.637. Phase τ 1 % interaction voids: 5 -> 4.

## CHECKS RUN

- **selftest --rev12** (copy of WIP 33e15ccc0, `rev12.log`): `selftest --rev12: 33 checks, 2 failed`.
  The two failures were the POWER_RECORD pins, re-pinned in be2994675.
- **selftest (full)**: run on be2994675's cards.py (copy `scratch/memfn/formsfixm/cards_full_be2994675.py`;
  HEAD's cards.py differs only by 3 comment/docstring lines, the provenance header; PCREC_TREE = this
  worktree), `python3 -I -u`, nice, log `scratch/memfn/formsfixm/selftest_full.log`:
  `selftest: 222 checks, 0 failed`, EXIT 0 (07:38-09:08). formsfixl's run read 217; the 5 new checks
  are this lane's. F2 0.000 / 0.000. Worst class-drill arm row `(r38) noise at arm: H(8), every cell, tau 2 %
  P(h* != 64) = 0.017`. FINDING: the first attempt (timeout 5400, block-buffered) hit its bound with
  no output (`selftest_full_timeout1.log`, EXIT 124). The selftest now takes ~90 min, where
  formsfixl's took 65: the interaction test is ~30 % of `analyse` on a layout night. Of that,
  `f_lower` is 1.24 s of 1.95 s per 20 nights (the bisection on float Satterthwaite df, which the
  lru_cache never hits) and `_clipped` 0.64 s (cProfile, `prof.out`). Caching on df rounded to 0.01
  would recover most of it. That is not done here: it would need a re-validation. Bound the night's
  selftest at >= 7200 s.
- **make strict** (-j8): rc 0, "strict: whole tree compiles clean with -Werror -Wshadow; the kit's
  target table check passes" (`strict.log`).
- **doc checks** `make test-claudemd-size test-spec-history test-doc-lint test-plan-lint`: rc 0
  (187 / 11 / 15 / 2 passed, 0 failed; `docchk.log`). `grep -E 'plan\.md:[0-9]'` over the review
  files and r45_reply.md: none.
- Drill scripts: `scratch/memfn/formsfixm/dr.py`, `dr1.py`, `dr2.py` (the clip sweep), `fb.py`
  (fail-before), `fv.py` (first-void cause). Their logs are `*_v2.log`, `*_v3.log`, `c*_*.log`.

## FOR THE MANAGER

- Power and flagged-night rates, void ON vs OFF, for every new row (300 nights each):
  - t(5) + phase 1 % + 5 % win: flagged 11 (on) / — (off: nothing voided); power 203 vs 201. On
    3fd31c86d: flagged 166, power 92 vs 201.
  - hex24 head arms 2x + phase 1 % + 5 % win: flagged 6; power 175 vs 174. On 3fd31c86d: 300
    flagged, power 0 vs 174.
  - mix 0.5 % x 1 % + win: flagged 10; power 280 vs 291.
  - mix 0.5 % x 0 + win: flagged 13; power 264 vs 286. That is -7.7 %, inside the 10 % line but
    the largest cost.
  - onereg 3 % / 5 %, mix 3 x 1.5 (no win), P(h* != 64) on vs off: 0.013 / 0.200, 0.010 / 0.220,
    0.023 / 0.183.
  - "Flagged" counts the test's flags with the void on. With the void off the test still runs and
    prints, but voids nothing.
- Heterogeneous noise the ruling did not gate, read in drills (100-300 nights, seed 900):
  - one regime 3x (not-warm) + phase 1 %: 0 of 300 flagged (critic, rev 13: 56 of 100);
  - every head arm 1.5x: 1 of 100.
- Margins: r44 A's τ 3 % row now reads 0.023 against 0.05 (it was 0.000). Clipping below 4 sigmas
  takes it to 0.053, so INTER_CLIP must not go lower without a new reading.
- Sensitivity: `INTER_CLIP`, `INTER_ALPHA` and the kurtosis shrink all decide the false-flag rate
  together. Each is measured on synthetic launch models only. The first real night's printed line
  shows the kurtosis read and the shrink factor.
- `rule`'s interaction line text changed (it is record output, not a contract). No `docs/spec/` reader.
