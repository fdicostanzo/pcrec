# o51read — reading O-51 against I-103/I-103a, the cycle-3 ask

2026-09-23, lane `o51read`, sonnet. Docs-only, nothing under
`src/`/`cli`/`lib/`/`tests/`, no timing, pcrec-bench touched only per D78's
single-writer file (`inbox_from_pcrec.md`, this lane's last act).

## What was delivered

1. **`docs/dev/optloop/cycle2_i103_reading.md`** (133 lines) — O-51's four
   answers checked against I-103/I-103a's own EXPECT lines and against
   `cycle2_batch2_reading.md` §4.1/§6 and the `[OPT-REQPOS]` three-arm
   form rule recorded on `plan.md`. Verdicts, briefly:
   - Router `(b)−(c) ≈ 0` matches I-103's EXPECT exactly (all four
     configs within IQR) — the run form is the whole cost, confirming
     §4.1's 124× call-amplification finding by direct measurement.
   - Keyword's `(b)−(c)` delta is positive and same-order across two
     independent sessions (39.5k-48.3k ns) but the IQR-crossing bar
     itself flips (one session's own IQR widened 40× between runs) —
     read as a decision-RULE robustness finding, not smoothed into
     either branch.
   - memchr-run beats the inline scalar hand-twin on all six measured
     cells, both patterns, confirming I-103a's EXPECT at both 2.8% and
     3.2% — the rule's common-tier (inline) mechanism correctly does not
     fire below its ~8% crossover.
   - The crossover constant does not condition on two points 0.36
     percentage points apart (both mechanisms' fitted byte terms go
     unphysically negative) — shown and stopped, per the ruling's own
     instruction, not forced.
   Section 3 states ESTABLISHED / NOT ESTABLISHED explicitly. Section 3
   also records a `learnings.md` §3 CANDIDATE (not applied): a hand-twin
   template written from one witness's own byte-offset generalizes wrong
   to a second witness at a different offset — O-51's own §0 deviation 4
   incident (keyword's arm (d) needed the manager's ruling to correct).

2. **The cycle-3 ask, designed not built** (reading §4). Counted every
   run-carrying capability pattern's scan-byte hit frequency (14 of 64
   patterns, via `docs/dev/optloop/b2ledger/stampdiff.json`'s fix-side
   `RX_REQ_RUN` against the regenerated `bench/capability/throughput/
   {t-64k,t-256k,t-1m}.bin` — sha256-verified byte-identical to O-51's own
   cited hashes). Widest real spread: `wild-semdiv-dollar-trailing-
   newline-pcre2` at **0.4773%** (clears <0.5%) to `keyword-prefix-order`
   at **3.2067%** — **no candidate in the bench's own set clears 6%**.
   Verified the byte-pick mechanism (argmin over the run's own bytes'
   `pcrec_byte_freq_ppm`) against all 14 real cases from source
   (`src/opt/prefix_k.c`'s shipped table): **14/14 exact**, including two
   non-trivial ties (`://`'s two `/`s; keyword's `in` picking `n` over
   `i`). Used that verified mechanism to design a synthetic witness: a
   run built only from `e`/space bytes forces `'e'` as the pick (the
   table's two highest-ppm entries), and `'e'` already occurs in the
   EXISTING throughput subjects at 8.5212% — no new subject text
   required, only a new pattern (a nested-comment-rec-shaped delimiter
   pair). Draft I-105 ask text is in the reading and in the inbox entry
   below.

3. **Archive**: `docs/dev/optloop/runs/2026-09-23-o51-i103/` — the O-51
   outbox entry, the I-103/I-103a asks, and the full 495-line
   `b83runform_report.md`, each copied verbatim at read time; own
   README.md. `docs/dev/optloop/CLAUDE.md` entry added.

4. **Last act**: pcrec-bench inbox entry I-105 ("I-103 logs fetched"),
   releasing `/tmp/optloop5`, stating the reading's established/not lines
   and the cycle-3 ask, per D78's single-writer-file ritual.

## Verdicts (one line each)

- Router: the run FORM is the whole cost — CONFIRMED exactly.
- Keyword: direction positive, same order across sessions — decision-rule
  robustness issue, not resolved by this window (I-104 is the fix).
- Inline vs memchr: memchr-run wins everywhere measured — CONFIRMED.
- Crossover constant: does not condition on 0.36pp-apart points — shown,
  not forced.
- Cycle-3 pair chosen: `wild-semdiv-dollar-trailing-newline-pcre2`
  (0.4773%) + `keyword-prefix-order` (3.2067%, best real high end, reuses
  an already-built arm) OR the proposed synthetic `e`/space-run witness
  once the bench builds and verifies it (no real candidate clears 6%).
- Could not compute: the exact emitted stamp (`RX_REQ_BYTE`/`RX_REQ_RUN`)
  a real compile of the proposed synthetic pattern would produce — the
  argmin mechanism predicts `'e'` with 14/14 confirmed accuracy on real
  cases, but this is a design proposal, not a build (D77).

## Rulings received

None mid-flight; the brief itself (team-lead message) carries the full
task and this lane worked it without a rulings-file poll.
