# Lane `revrev` — [OPT-REVEND] design revision 2 + the deciding timing (2026-10-09)

Branch `lane/revrev` off main `9e431f6d` (abi 71). Opus, design + hand-twin; nothing under
`src/`, `cli/`, `lib/` or `tests/`, no plan or journal edits.

**Deliverables:**
- `docs/design/revend.md` REVISION 2: form C (walk-only) primary, forms A and B recorded;
  §R2 dispositions X1-X13 by id with `[r2 Xn]` edits in place; §7 predictions; §10
  questions.
- `studies/revend_twin/`: `mktwin.py` `TWIN_FORM=walk` + head placement (X7) + dead-seed
  skip (X1) + controls `nodead`/`tien`/`tien1`; `r2_patterns.tsv`, `controls_r2.tsv`,
  `run_r2_check.sh`, `mksubj_r2.py`, `timedrv4.c`, `run_r2_timing.sh`, `r2_table.py`;
  verbatim `results/r2_*`; CLAUDE.md updated.
- this report.

## Summary (resume from here)

- **Form C (Frank's point) holds and is the primary design.** `<p>_search` on an admitted
  artifact is only the reverse walk from `n` (and `n-1` before a final newline under
  `$`/`\Z`), recording which seed reaches the smallest accepting position `s*`. One seed:
  the answer is `(s*, seed)`. Both seeds (a TIE): one anchored run from `s*` decides
  `n` vs `n-1`. None: NOMATCH. No forward pass.
- **The tie arm is a three-row table** (§2.4): `no-tie` (one seed under `\z`, or the fact
  `nl_last` false: the reverse machine's seed state, after the end view, dies on `'\n'`; 4 of
  the bench's 5 patterns), `anchored` (`DFA_MATCH "unwrapped"`), `body` (`"search-filter"`:
  calling `_match` would recurse, so `s*` goes to the body as `LOWER`).
- **Handoff (X2):** the row hands `START`+end or `VERDICT` to the CALLER over a new
  declared edge E13 (WINDOW → CALLER); `LOWER` only on the `body` tie arm (E2). Checked
  against `cand_rows_selfcheck`: CALLER accepts `START|VERDICT`, so adding
  `CN(CAND_NODE_CALLER)` to WINDOW's `succ` is the whole change.
- **Q1 collapses:** C beats W1 on all 47 bounded cells (C/W1 0.004-0.89). **Q2 becomes the
  downstream-stamp question** (form C does not run PRESENCE/FIRST/NEXT/RECOVER on movers).
- Filed new: the forward-machine-free admission (form C needs only the reverse machine;
  `[a-z]{0,8192}\z` and wider fall back to the VM today).

## Validation (complete; scratch tier)

| run | result |
|---|---|
| identity, form C, 74 patterns (43 + 18 new X1/tie/wide + revq1's 13) | **0 twin diffs / 1,393,750 cells**; find-all 0 / 78,341; vs libpcre2 10.46 0 / 1,233,468 except K74's 55 cells on `\B\w*\z` (artifact identical) |
| identity, form A (73; refuses `[a-z]{0,4096}\z`, `_match` is search-filter) | 0 / 1,372,523; find-all 0 / 76,962 |
| identity, form B, 74 | 0 / 1,393,750; find-all 0 / 78,341 |
| identity, form C on `-fno-anchored-dfa` artifacts (tie → body), 16 | 0 / 339,632; find-all 0 / 18,277; libpcre2 0 / 301,680 |
| controls (form C, 9 patterns) | all red with witnesses: `noeol` (`\d+$` 10+70, `a*$` 552+355, `a\Z(?=\n)` 24), `firstseed` (`a*$`/`.*$`/`\s*?$`), `tien` (`\s*?$` 552+355), `tien1` (`\s+$` 36+140, `\s*$`), `nodead` (ASan SEGV in `<p>_reverse_view_live` on all three X1 shapes) |
| timing | 7 passes x 71 cells x 4 arms, 0 ANSWER-DIFF; core 2 (sibling 10 busy > 0.1 on 14 of 497 cell-runs); load1 per pass 2.98 (pass 1, after the 5-minute wait cap) then 1.35-2.05 |

`results/r2_identity.txt`, `r2_controls.txt`, `r2_timing.tsv`, `r2_table.md`,
`r2_meta.txt`, `r2_tiearm.txt`.

## Timing headline (ns per call, median of 7 pass medians)

| cell | today | **C** | A | B |
|---|---:|---:|---:|---:|
| `\d+$` t-tail-digits-1m (match) | 527,865 | **6.4** | 11.8 | 18.5 |
| `\w+\z` t-tail-txt-1m (match) | 1,540,533 | **3.5** | 6.4 | 7.8 |
| `\s+$` t-tail-space-1m (match) | 1,400,650 | **4.9** | 7.7 | 10.3 |
| `[a-z]+\.txt$` t-tail-txt-1m (match) | 2,147,087 | **9.6** | 23.1 | 37.4 |
| `.*\.txt$` t-tail-txt-1m (match) | 187,493 | **11.8** | 18.8 | 24.8 |
| `\s+$` t-tail-spacenl-1m (TIE) | 1,448,480 | 11.7 | **10.9** | 14.8 |
| bounded `done$` long (W1 today) | 13.7 | **5.7** | 11.6 | 21.5 |
| bounded `(?:[a-z]{0,1024})\z` 1 KB (W1) | 682.0 | **301.4** | 1,394 | 994.8 |
| `[a-z]{0,4096}\z` ~1 KB (W1) | 2,066 | **301.9** | — | 994.7 |
| `[a-z]{0,4096}\z` none (W1) | 1,926 | **2.0** | — | 3.8 |

- Form C leads on every matching cell bar the tie (A by 0.8 ns: the seed record).
- The two `.txt` cells, re-timed with the walk at the head and no early `.txt` (X7): C
  9.6 / 11.8 ns, where revision 1's form B read 68.6 / 32.6.
- On non-matching tails C is within -0.4..+0.6 ns of B. The positive part is the unused
  tie arm: `results/r2_tiearm.txt` shows `\d+$` (cannot tie, so T1 emits nothing) at
  3.3 → 2.6 ns without it.
- `[a-z]{0,60000}\z` is VM-routed (REVEND declines); W1 on the VM is 130 us / 34 us /
  130 us (1 KB / 50 KB / none), context only. The 50 KB match cell asked for in the brief
  is not available on the DFA route: 4,096 is the widest bound that stays DFA.

## Predictions table, ready to relay (bench O-91 ask 2)

Ryzen 1600 bench box, auto-caps, fixed driver ([B133]). Point = Linux form-C median x 1.6 +
5 ns (both UNMEASURED transfer terms; x 1.3 for the one ~1 KB walk), rounded to 5; range
[Linux min, 2.5 x point]. **Falsifiable claims: every acceptance cell <= 100 ns (<= 150 ns
on the grown driver), and size independence.**

| cell | t-tail-digits-1m | t-tail-txt-1m | t-tail-space-1m |
|---|---:|---:|---:|
| tail-digits-eol `\d+$` | 15 ns (6-38), match | 10 (3-25) | 10 (3-25) |
| tail-word-eoz `\w+\z` | 10 (4-25), match | 10 (3-25), match | 10 (2-25) |
| tail-space-eol `\s+$` | 10 (3-25) | 10 (3-25) | 15 (5-38), match |
| tail-ext-lower-txt `[a-z]+\.txt$` | 10 (3-25) | 20 (9-50), match | 10 (3-25) |
| tail-dotstar-txt `.*\.txt$` | 10 (3-25) | 25 (9-62), match | 10 (3-25) |

Plus `\s+$` x t-trim-nearmiss-16k **10 ns** (3-25); `\d+$` x t-1m **15 ns** (6-38).
Class B cells now predicted to IMPROVE: `anc-dollar` 15, `anc-z-lc` 10, `anc-z-uc` 15,
`ctrl-abc-dollar` / `wild-semdiv-dollar-trailing-newline-pcre2` 15,
`letters-bounded-tail-z` 395 (~1 KB tail) or 10 (short tail).

## Open questions for Frank (discussion; full text in revend.md §10)

1. **Q1 (REVEND before W1) collapses by the numbers:** C is faster than W1 on all 47 bounded
   cells. Leaning: REVEND first, unless there is a non-speed reason.
2. **Q2 (new): the downstream search stamps on admitted artifacts.** C does not emit the
   forward pass, prefilter, pre-check or reverse pass, so `RX_DFA_SCAN`/`_PREFILTER`/
   `_START`/`RX_REQ_*` would name absent passes. Leaning: their existing `"none"` values,
   with `RX_DFA_START`/`RX_REQ_WHY`/`rx_info.search_form` reading `"rev-end"` (the `[OPT-5]`
   precedent), in the S2 abi event. Cost: the readers in §5.3 (d).
3. **Q3: the tie arm table** (no-tie / anchored / body). Leaning: as designed.
4. **Q4: stage 2 (captures) and the forward-machine-free admission** stay filed (D77).

## For the manager

- **Sabotage ids NEEDED: 16** (revend.md §9.2: 10 answer-level, 6 structural), plus
  re-aims of S264 (its reach probe to `(abc)$`, X8), S693 (the abi constant) and every §5.3
  (d) row whose witness becomes a mover.
- **The full reader list** is revend.md §5.3: (a) abi-number readers with file:line, (b)
  byte-count readers, (c) the `END_WINDOW` stamp-VALUE readers (37 files by grep; the value
  readers named), (d) the downstream slot-stamp readers by count (`DFA_START` 19,
  `DFA_SCAN` 33, `DFA_PREFILTER` 54, `_OFFSETS` 15, `REQ_*` 90 files).
- **Bench-only questions** (revend.md §11): fixed driver; a 64 KiB variant; whether the
  bench's `t-tail-txt-1m` body contains an early `.txt`; keep the class B cells in the
  window; a tie cell (`\s+$` on a body ending `"   \n"`) does not exist in the family yet.
- **Manager-level spelling:** the stamp/listing token `rev-end` (X10), the tie sub-axis's
  row names, the `"none"`/`"rev-end"` downstream values.
- `start_table.md` §1.6 gains E13 and §4.4's REVEND line (`hands CAND`) needs correcting
  at merge.
- **Process notes.** The box was not quiet: load1 3.7-4.5 for 15 minutes from the kit's
  `g2simd` run and the desktop. I stopped two earlier timing launches (scripts/safekill) and
  moved the load wait from per-cell to per-pass (up to 5 minutes), recording load1 and the
  SMT sibling's busy fraction per cell; pass 1 ran at 2.98 after the cap. I also wrote one
  stray file to `/tmp/null` (a `make` redirect) at the start and deleted it at once.
- No live finding against main. The one oracle divergence is K74 (known).
