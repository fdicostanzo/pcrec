# THE LEDGER — capability@0.1's [OPTLOOP] cycle 2 batch-2 AFTER at pcrec b1885a83 (abi 30)

Read-only extraction, no diagnosis, per inbox_from_pcrec.md I-95 (the
[B80] (b) ask), read alongside I-99/I-100/I-101 (Frank's class-pure-views
ruling) for context only — per I-99 (3)/I-100 (4), **this ledger ships in
the EXISTING single-roster shape**; the two class-pure views ([B82]) and
the standing cross-class query (I-101) are a FOLLOW-UP on these SAME
records, not redone here. Scores the AFTER window's per-cell numbers
against I-95 (a)'s named targets and the union-18 carve-out population,
per the D119 landing bar as I-87(a)/I-95 state it: **a TARGET cell must
improve by more than its IQR; every other cell must not regress by more
than its IQR.** Numbers only; the manager's interpretation and any
outbox item are not this lane's to write.

**BEFORE** = the four `pcrec_8d716693_*` records (2026-09-23T03:19-05:52Z
starts; abi 29) and `reports/2026-09-23-capability-0.1-budu-ryzen1600-after-8d716693.tsv`
— this is the SAME set of records that was the AFTER side of the prior
ledger (`2026-09-23-optloop1-batch1-after-8d716693.md`); it is the BEFORE
for this cycle.
**AFTER** = the four `pcrec_b1885a83_*` records (2026-09-23T11:47-14:14Z
starts; abi 30) and `reports/2026-09-23-capability-0.1-budu-ryzen1600-after-b1885a83.tsv`.
The AFTER report is a CROSS-PIN render (`reporter: v19`) carrying both
pins' four pcrec testees plus `oniguruma`/`rust`/`vectorscan`, with the
reporter's own `delta_verdict` column — used here only as a cross-check
(§0.2), never as the source of the D119 verdicts, which this ledger
computes independently from the records.

**Ratio/percentage convention: `(after − before) / before`, so a
positive `Δ%` is SLOWER (a regression) and a negative `Δ%` is FASTER (an
improvement), for every table in this ledger.**

---

## 0. SOURCES, SAMPLE SHAPE, HYGIENE — what was read, and how

### 0.1 The eight records

| side | testee | record file (`store/records/capability@0.1/...`) | trials | rows (compile/match) | subjects (thr/srch) |
|---|---|---|---|---|---|
| before | `pcrec_8d716693_auto-caps-simdna` | `...20260923T031941Z.jsonl` | 5 | 623 / 24,180 | 3 / 75 |
| before | `pcrec_8d716693_auto-nocaps-simdna` | `...20260923T035507Z.jsonl` | 5 | 627 / 24,570 | 3 / 75 |
| before | `pcrec_8d716693_vm-caps-simdna` | `...20260923T042632Z.jsonl` | 5 | 623 / 24,180 | 3 / 75 |
| before | `pcrec_8d716693_vm-in-caps-simdna` | `...20260923T050923Z.jsonl` | 5 | 623 / 24,180 | 3 / 75 |
| after | `pcrec_b1885a83_auto-caps-simdna` | `...20260923T114747Z.jsonl` | 5 | 623 / 24,180 | 3 / 75 |
| after | `pcrec_b1885a83_auto-nocaps-simdna` | `...20260923T122232Z.jsonl` | 5 | 627 / 24,570 | 3 / 75 |
| after | `pcrec_b1885a83_vm-caps-simdna` | `...20260923T125206Z.jsonl` | 5 | 623 / 24,180 | 3 / 75 |
| after | `pcrec_b1885a83_vm-in-caps-simdna` | `...20260923T133317Z.jsonl` | 5 | 623 / 24,180 | 3 / 75 |

Read in full (all eight `kind: setup`/`compile`/`match` rows); these are
the ONLY files this ledger's numbers come from. The two `.subject-grain.tsv`
files (~53.6 MB each, `after-8d716693`/`after-b1885a83`) were **not
opened** — every number here is reconstructed from the records themselves,
which carry the identical raw rows the subject-grain TSV renders from. The
`.md`/`.matrix.html`/`.matrix.tsv` renders and both `.interpretation.md`
sidecars were **not read** (the sidecars are STALE against this window's
own records per `b80repin`'s `make check` report — see §4).

### 0.2 Arithmetic used — the SAME module the reporter imports

Medians, IQRs and verdicts below are computed by importing
`pcrecbench.reduce` directly (`read_record`, `cells_from_record`,
`reduce_set_cell`, `reduce_match_cell`), the exact functions `report.py`
calls for `--grain set`, not a re-implementation.

**IQR method (unchanged from the prior ledger): Type-7 / Hyndman-Fan
linear interpolation, Q1 = 25th percentile, Q3 = 75th percentile.** For
exactly 5 sorted per-trial sums `x0<=x1<=x2<=x3<=x4`, Q1 = x1, Q3 = x3, so
**IQR = x3 − x1** (the spread of the three central trials).

**Cross-check against the committed cross-pin TSV** (not the source of
the verdicts, a confirmation of them): every one of the three named-target
patterns this ledger flags as a regression (`router-prefix-order`,
`logparse-atomic`, `wild-secrets-github-pat`) matches the AFTER report's
own `rank` rows to the printed digit and its `delta_verdict` column agrees
in DIRECTION on every row checked — e.g. `router-prefix-order` /
`large-subject-throughput`: this ledger's before/after medians for
`auto-caps` (398,422.848062 / 720,485.587744) match the report's
`median_ns` column exactly, and the report's own `delta_verdict` reads
`slower ×1.81` (720485.59/398422.85 = 1.8083, i.e. +80.83%, matching this
ledger's independently-computed +80.83%). `wild-secrets-github-pat` /
`large-subject-throughput` / `vm-caps`: report `faster ×41.72`, this
ledger's Δ% = −97.60%, `129145.43/5387513.31 = 0.02397` → `1/0.02397 =
41.72` — the same arithmetic read twice.

### 0.3 Window provenance (BEFORE and AFTER)

Both windows: 5 trials, **X13 (v1.4 pre-flight + trial agreement) `agree`
on ALL EIGHT records, 0 `groups_disagreeing` on every one**, attempt 1
throughout (no `inconclusive-spread` re-measure on either side).

| side | testee | load1 (before→after) | occupancy target% (before→after) | occupancy max-other% (before→after, 5s avg) | trial-agreement | rows_disagreeing / rows_judged |
|---|---|---|---|---|---|---|
| before | auto-caps | 0.01 → 1.00 | 0.0 → 0.0 | 1.6 → 1.6 | agree | 6 / 4834 |
| before | auto-nocaps | 0.73 → 1.03 | 0.0 → 0.0 | 1.4 → 1.8 | agree | 6 / 4912 |
| before | vm-caps | 0.75 → 1.06 | 0.2 → 1.0 | 0.8 → 1.4 | agree | 4 / 4834 |
| before | vm-in-caps | 0.76 → 1.00 | 0.8 → 0.8 | 0.4 → 1.4 | agree | 7 / 4834 |
| after | auto-caps | 0.40 → 1.00 | 7.01 → 0.0 | 2.2 → 1.6 | agree | 7 / 4834 |
| after | auto-nocaps | 0.73 → 1.01 | 0.0 → 0.0 | 0.4 → 1.8 | agree | 4 / 4912 |
| after | vm-caps | 0.74 → 1.01 | 0.0 → 0.0 | 2.0 → 1.0 | agree | 2 / 4834 |
| after | vm-in-caps | 0.73 → 1.07 | 0.4 → 0.0 | 1.8 → 0.8 | agree | 7 / 4834 |

All eight `occupancy.*.verdict` read `pass` on both before/after samples
(load limit 2.0, occupancy limit 10.0%); the highest gate-scope reading
anywhere in either window is 7.01% (AFTER auto-caps' own BEFORE-sample
target-core reading), still under the 10% pre-flight bar. `worst_group`
on every one of the eight records is `phone-palindrome-6` /
`short-subject-search` (`d` 2-7 of `n`=75), consistent across both pins.

**BEFORE window ran 2026-09-23T03:19:36Z → 05:51:45Z** (the SAME wall
range as the prior ledger's AFTER window — these are the same eight
files, read from the other side of the pin boundary this time).
**AFTER window ran 2026-09-23T11:47:42Z → 14:13:52Z** (≈2h26m; 07:47:42 →
10:13:52 EDT — matching the brief's stated 07:47-10:14 EDT).

**The report header's `worst_other_core_busy: 62.5%
(pcrec_8d716693_auto-caps-simdna / date-nested-plus /
large-subject-throughput)` line is, this time, INSIDE this ledger's own
BEFORE population** (unlike the prior ledger, where the header's spike
named an excluded older record): read directly from
`pcrec_8d716693_auto-caps-simdna`'s own `occupancy.timeline`, it is one
87 ms group's single-second peak (`max_other_cpu` 8), not a 5-second
average — the record's own `occupancy.before/after.max_busy_pct` (5s
average) for that same testee is 1.6/1.6%, both `pass`. Every
per-group timeline peak across the 8×~124-126 groups stays under 63% on
either pin (before: 62.5/22.22/15.38/11.76; after: 38.89/28.57/21.05/31.82,
all on different tens-to-low-hundreds-ms groups) — no group's peak
threatened its own `pass` verdict.

**KB-27 standing check (per the brief's ask, unchanged rule):**
`evil-alt-nested` × `{rd-evil-alt-near-miss, sd-empty-alt-hit}` under
`short-subject-search`, read at the per-subject `reduce_match_cell` level
on all four AFTER (and all four BEFORE) testees: **`auto-caps`/`vm-caps`/
`vm-in-caps` read `outcome_counts={'gave-up': 5}` (`n_wrong=0`,
`n_no_expectation=0`) on both subjects, on BOTH pins** — a genuine engine
give-up, unchanged from the prior ledger. **`auto-nocaps` reads
`outcome_counts={'did-not-match-as-expected': 5}` with `n_no_expectation=5`
on both subjects, on BOTH pins** — the no-expectation case KB-27 already
carves out of `n_wrong`, also unchanged. Neither reading moved across
this pin boundary.

---

## 1. THE D119 TABLE — I-95 (a)'s named targets and the union-18 carve-outs

**Population, discovered directly from the AFTER `auto-caps` record's
own compile rows (independent of the repin lane's own census — see §3):
126 (pattern, regime) pairs, `plain` form, present on both pins.** 7 are
I-95 (a)'s literal named-target cells; 29 fall into the union-18
carve-out population outside the 7 target cells; 90 are neither.

### 1.1 TARGET CELLS (I-95 (a)) — 28 rows, 7 (pattern, regime) × 4 testees

I-95 (a) names REGIMES explicitly for each pattern: `logparse-atomic`
BOTH (thr + srch); `router-prefix-order`, `wild-secrets-github-pat`,
`tag-depth3-bound`, `tag-pair-match`, `nested-comment-rec` — THROUGHPUT
ONLY. Each of these five patterns also has a `short-subject-search`
regime in the corpus; those cells are NOT named targets and are scored
under §1.2 (they are all in the union-18 carve-out set).

| pattern | regime | testee | before med (ns) | before IQR | after med (ns) | after IQR | Δ% | verdict (before-IQR) |
|---|---|---|---|---|---|---|---|---|
| logparse-atomic | large-subject-throughput | auto-caps | 41.518 | 0.042 | 44.433 | 0.158 | +7.0197% | **regress** |
| logparse-atomic | large-subject-throughput | auto-nocaps | 40.344 | 0.068 | 43.222 | 0.136 | +7.1342% | **regress** |
| logparse-atomic | large-subject-throughput | vm-caps | 43.586 | 0.047 | 58.879 | 0.318 | +35.0885% | **regress** |
| logparse-atomic | large-subject-throughput | vm-in-caps | 49.179 | 0.059 | 69.745 | 0.112 | +41.8186% | **regress** |
| logparse-atomic | short-subject-search | auto-caps | 876.424 | 0.857 | 830.505 | 1.529 | −5.2394% | improve |
| logparse-atomic | short-subject-search | auto-nocaps | 859.859 | 2.028 | 815.742 | 6.974 | −5.1308% | improve |
| logparse-atomic | short-subject-search | vm-caps | 836.829 | 9.164 | 861.230 | 11.033 | +2.9159% | **regress** |
| logparse-atomic | short-subject-search | vm-in-caps | 951.001 | 2.446 | 950.012 | 1.281 | −0.1040% | within-bar |
| router-prefix-order | large-subject-throughput | auto-caps | 398,422.8 | 174.809 | 720,485.6 | 170.058 | **+80.8344%** | **regress** |
| router-prefix-order | large-subject-throughput | auto-nocaps | 398,752.2 | 395.217 | 720,106.1 | 780.199 | **+80.5899%** | **regress** |
| router-prefix-order | large-subject-throughput | vm-caps | 4,050,506.2 | 3,154.734 | 4,451,241.0 | 6,312.448 | +9.8935% | **regress** |
| router-prefix-order | large-subject-throughput | vm-in-caps | 4,049,652.5 | 2,640.938 | 4,441,972.6 | 6,396.492 | +9.6877% | **regress** |
| wild-secrets-github-pat | large-subject-throughput | auto-caps | 124,604.5 | 60.883 | 129,396.6 | 231.349 | +3.8459% | **regress** |
| wild-secrets-github-pat | large-subject-throughput | auto-nocaps | 124,798.7 | 95.782 | 128,959.2 | 179.769 | +3.3338% | **regress** |
| wild-secrets-github-pat | large-subject-throughput | vm-caps | 5,387,513.3 | 12,000.469 | 129,145.4 | 248.879 | −97.6029% | improve |
| wild-secrets-github-pat | large-subject-throughput | vm-in-caps | 5,857,018.1 | 6,899.356 | 125,586.1 | 85.842 | −97.8558% | improve |
| tag-depth3-bound | large-subject-throughput | auto-caps | 23,141.027 | 11.221 | 23,112.369 | 8.634 | −0.1238% | improve |
| tag-depth3-bound | large-subject-throughput | auto-nocaps | 23,159.742 | 27.846 | 23,093.660 | 43.266 | −0.2853% | improve |
| tag-depth3-bound | large-subject-throughput | vm-caps | 23,177.114 | 5.647 | 23,126.166 | 6.555 | −0.2198% | improve |
| tag-depth3-bound | large-subject-throughput | vm-in-caps | 23,113.890 | 31.768 | 23,112.968 | 5.657 | −0.0040% | within-bar |
| tag-pair-match | large-subject-throughput | auto-caps | 23,128.123 | 23.374 | 23,159.620 | 1.234 | +0.1362% | **regress** |
| tag-pair-match | large-subject-throughput | auto-nocaps | 23,159.616 | 9.003 | 23,168.559 | 11.695 | +0.0386% | within-bar |
| tag-pair-match | large-subject-throughput | vm-caps | 23,116.516 | 29.330 | 23,195.351 | 76.380 | +0.3410% | **regress** |
| tag-pair-match | large-subject-throughput | vm-in-caps | 23,144.063 | 19.676 | 23,135.145 | 22.037 | −0.0385% | within-bar |
| nested-comment-rec | large-subject-throughput | auto-caps | 9,327,080.3 | 597,173.7 | 23,118.463 | 13.452 | −99.7521% | improve |
| nested-comment-rec | large-subject-throughput | auto-nocaps | 9,275,952.3 | 366,365.7 | 23,134.727 | 13.439 | −99.7506% | improve |
| nested-comment-rec | large-subject-throughput | vm-caps | 9,350,863.1 | 116,823.1 | 23,152.517 | 28.184 | −99.7524% | improve |
| nested-comment-rec | large-subject-throughput | vm-in-caps | 9,746,259.5 | 31,549.444 | 23,149.292 | 40.077 | −99.7625% | improve |

**11 of 28 target rows MEET the bar; 17 of 28 MISS.** The verdict is
IDENTICAL whichever cell's IQR is used (before-IQR or after-IQR) on all
28 rows — no reading flip anywhere in this table (unlike the prior
ledger's one flip).

**By pattern:**
- `nested-comment-rec` (the one regime I-95 predicted as "the pick's one
  losing cell"): 4/4 MEET, the largest margin in the table (−99.75% to
  −99.76%, IQRs in the tens-to-hundreds-of-thousands of ns against a
  9.3-9.7 MILLION ns baseline).
- `wild-secrets-github-pat`: 2/4 MEET (`vm-caps`/`vm-in-caps`, −97.6%/
  −97.9%, millions of ns collapsing to ~125-129K ns) and 2/4 MISS
  (`auto-caps`/`auto-nocaps`, +3.3%/+3.8% — these two testees were
  ALREADY at ~124-125K ns before this pin, not millions).
- `tag-depth3-bound`: 3/4 MEET (small improvements, −0.12% to −0.29%,
  against IQRs of 5.6-31.8 ns), 1/4 within-bar (`vm-in-caps`, −0.004%).
  Already at the ~23,100 ns floor on all four testees before this pin.
- `tag-pair-match`: 0/4 MEET — 2/4 MISS (auto-caps +0.14%, vm-caps
  +0.34%, both tiny absolute moves against tight IQRs at the ~23,100 ns
  floor), 2/4 within-bar. `tag-depth3-bound` and `tag-pair-match` share
  the identical `req_run` stamp (`"</"@0`, §3) but diverge on this
  verdict.
- **`logparse-atomic` — I-95's own "no-decline-rule falsifier" — MISSES
  on 5 of 8 rows, including its named-first throughput regime on ALL
  FOUR testees** (+7.0% to +41.8%; the `vm-caps`/`vm-in-caps` regressions
  are the largest percentage moves in the whole target table apart from
  `router-prefix-order`'s DFA route). Its search regime meets the bar on
  `auto-caps`/`auto-nocaps` (−5.2%/−5.1%) but MISSES on `vm-caps`
  (+2.9%) and reads within-bar on `vm-in-caps`. The repin lane's own
  finding — that `logparse-atomic` now carries a REAL 2-byte run
  `": "@0` (byte 0x3a 0x20) rather than a bare pick move — is CONFIRMED
  by this ledger's own census (§3); the run did not prevent the
  regression I-95 asked to check for; if anything the regression is
  LARGEST on the two testees where the run is most exclusively
  responsible for the search path (`vm-caps`/`vm-in-caps` throughput,
  +35.1%/+41.8%).
- **`router-prefix-order` — I-95's "freq pick's live case" — is the
  single worst-missing target: +80.83%/+80.59% on the DFA route
  (`auto-caps`/`auto-nocaps`)**, an order of magnitude past its own
  (tight, 175-780 ns) before-IQR, against a ~398→720 μs baseline. Its
  VM route also misses, more mildly (+9.7%/+9.9%).

### 1.2 CARVE-OUTS — two subsections per the brief, populations from §3's independently-derived census

Every union-18 pattern's cell OUTSIDE the 7 named-target cells above.
`nested-comment-rec`/`router-prefix-order`/`tag-depth3-bound`/
`tag-pair-match`/`wild-secrets-github-pat`'s `short-subject-search` rows
land here (their thr rows are already scored in §1.1); `logparse-atomic`
contributes NOTHING here (both its regimes are §1.1 targets).

#### 1.2.1 REQ_RUN-stamping cells (14 patterns; §3's independently-derived
run-stamping population), minus §1.1's rows — 84 cells (10 patterns ×
2 regimes × 4 testees, minus `wild-secrets-github-pat`'s thr row already
scored)

**Aggregate (before-IQR): 57 improve, 23 regress, 4 within-bar.**

Regressing cells (23): `keyword-prefix-order`/thr on all four testees
(+8.0% to +59.7% — the DFA route's +59.6%/+59.7% is the largest
percentage regression in this whole ledger outside the floor-conversion
population in §2.2); `logparse-atomic-removed` on 6 of 8 cells (+1.7% to
+31.5%, one improving cell each on thr `auto-nocaps` is absent — all
four thr cells regress; only srch `auto-nocaps` improves −1.6%);
`wild-secrets-github-pat`/srch/`auto-caps` (+3.8%, its 3 sibling testees
improve −2.5% to −13.3%); `wild-secrets-slack-webhook-url`/thr/DFA route
(+1.7%/+3.4%, its VM route improves −92.9% each collapsing from millions
of ns); `wild-secrets-slack-webhook-url`/srch/`auto-nocaps` (+0.09%,
within its own before-IQR under the after-IQR reading — one of nine
flips in the union population); `wild-semdiv-dollar-trailing-newline-pcre2`/
srch/VM route (+2.5%/+3.7%, its DFA route and thr regime all improve);
`wild-waf-crs-942500-comment-obfuscation`/thr/`auto-caps` (+0.017%, a
floor-level move — see §2.2's shape); `winpath-near-miss`/thr/DFA route
(+0.09%/+0.11%, floor-level) and `winpath-near-miss`/srch on ALL FOUR
testees (+4.9% to +10.3%, the DFA route worst).

Improving cells (57) are dominated by two shapes: the forced-VM route's
own multi-million-ns collapses (`file-ext-order`/thr `vm-caps`/`vm-in-caps`
−93.9% each; `wild-secrets-slack-webhook-url`/thr `vm-caps`/`vm-in-caps`
−92.9% each; `wild-semdiv-altorder-foo-foobar-rustregex`/thr `vm-caps`/
`vm-in-caps` −91.0% each; `wild-waf-crs-942500-comment-obfuscation`/thr
`vm-caps`/`vm-in-caps` −99.43% each), and the search-regime improvements
that ride along on every one of these ten patterns' `keyword-prefix-order`,
`file-ext-order`, `tag-depth3-bound`/`tag-pair-match`, `router-prefix-order`,
`nested-comment-rec` VM-route srch cells (−38.9% to −68.1%).

#### 1.2.2 REQ_BYTE-moved cells (14 patterns; §3's census), minus §1.1's
rows — 88 cells (11 patterns × 2 regimes × 4 testees, minus
`router-prefix-order`/`tag-depth3-bound`/`tag-pair-match`/
`nested-comment-rec`'s thr rows already scored)

**Aggregate (before-IQR): 64 improve, 21 regress, 3 within-bar.**

Ten of the fourteen REQ_BYTE-moved patterns are ALSO REQ_RUN-stamping
patterns (§3's "both" population), so their rows repeat between §1.2.1
and §1.2.2 by construction (`nested-comment-rec`, `router-prefix-order`,
`tag-depth3-bound`, `tag-pair-match`, `file-ext-order`,
`logparse-atomic-removed`, `wild-semdiv-altorder-foo-foobar-rustregex`,
`wild-semdiv-dollar-trailing-newline-pcre2`, `wild-waf-crs-942500-comment-obfuscation`
— all already counted in §1.2.1). The four patterns UNIQUE to this
subsection (pure `req_byte` pick moves, NO run at all — §3): `codegrammar-flat`,
`codegrammar-xflag`, `dup-param-detect`, `wild-validator-email-owasp`.

**`codegrammar-flat`/`codegrammar-xflag`** (byte moved 58→34, `'`;` →
`'`\"`'`;` no, decoded: 0x3a=':'→0x22='"'... byte 34 is ASCII `"`): both
patterns move identically — thr regime mixed (auto-caps improves −1.9%
to −2.9%, auto-nocaps/vm-caps regress +1.0% to +3.4%, vm-in-caps flat),
srch regime regresses on the DFA route (+3.0% to +4.9%) and improves on
the VM route (−13.0% to −16.5%).

**`dup-param-detect`** (byte moved 61→38, `=`→`&`): thr regime is at the
~23,100 ns floor on all four testees (within noise, −0.14% to +0.39%);
srch regime improves cleanly on all four (−24.7% to −26.5%).

**`wild-validator-email-owasp`** (byte moved 46→64, `.`→`@`) — **the
single largest percentage movement in this entire ledger**: thr regime
regresses **+27,009.85% to +52,757.09%** on all four testees, moving
from 43.7-85.3 ns (already near-instant) to 23,118.8-23,200.5 ns — the
SAME ~23,100 ns floor the named targets collapse DOWN onto in §1.1, here
reached from BELOW (see §2.2/§5 finding 2, the floor-convergence
phenomenon this pattern newly joins). Its srch regime improves cleanly
on all four testees (−15.3% to −19.7%).

---

## 2. CELLS OUTSIDE THE BAR EITHER WAY (non-named, 90 patterns × 2 regimes × 4 testees = 360 cells)

**Under the before-IQR reading: 82 improve, 96 regress, 172 within-bar.
Under the after-IQR reading: 90 improve, 94 regress, 166 within-bar.**
61 of 360 improve under BOTH readings; 72 of 360 regress under BOTH
readings; 96 of 360 flip between readings (concentrated at small,
sub-2% Δ% on cells whose IQR is comparable in size to the movement
itself — a wider flip population than the prior ledger's 63/492, because
this population (unlike §1's named cells) carries no large forced
mechanism change to dominate the noise floor).

**Context only, NOT this pin-pair's own control: I-97/O-48's same-pin
interleaved-window null band is −5.74%..+8.46% (median −0.08%), measured
at the PRIOR pin pair (8d716693's own predecessor) as five interleaved
same-pin trials' spread — cited here only as a rough scale for "is this
movement bigger than same-pin noise typically is," never as this
pin-pair's own control (no same-pin repeat was run this window).**

### 2.1 Non-named REGRESSIONS with before-median ≥ 100 ns (82 cells,
before-IQR reading), largest 20 by |Δ%|

| pattern | regime | testee | before (ns) | after (ns) | Δ% | verdict (a) |
|---|---|---|---|---|---|---|
| ipv4-near-miss | short-subject-search | vm-in-caps | 1,021.419 | 1,135.363 | +11.16% | regress |
| phone-palindrome-6 | large-subject-throughput | vm-caps | 6,586,599.6 | 7,164,447.0 | +8.77% | regress |
| wild-codegrammar-json-number-extended | short-subject-search | auto-caps | 1,393.273 | 1,499.272 | +7.61% | regress |
| wild-codegrammar-json-number-extended | short-subject-search | auto-nocaps | 1,393.819 | 1,498.732 | +7.53% | regress |
| wild-semdiv-empty-alt-repeat-pcre2 | short-subject-search | auto-caps | 2,880.862 | 3,097.294 | +7.51% | regress |
| phone-palindrome-6 | short-subject-search | auto-caps | 7,031.463 | 7,495.260 | +6.60% | regress |
| phone-palindrome-6 | large-subject-throughput | vm-in-caps | 7,039,078.0 | 7,366,060.2 | +4.65% | within-bar (after-IQR) |
| wild-datetime-datefinder-alternation | short-subject-search | auto-nocaps | 1,949.612 | 2,021.152 | +3.67% | regress |
| high-byte-run | short-subject-search | auto-caps | 1,095.893 | 1,133.969 | +3.47% | regress |
| wild-codegrammar-json-object-begin | short-subject-search | vm-caps | 657.021 | 679.688 | +3.45% | regress |
| wild-secrets-aws-access-key-id | short-subject-search | auto-caps | 1,167.806 | 1,207.473 | +3.40% | regress |
| wild-codegrammar-json-array-begin | short-subject-search | vm-caps | 684.842 | 707.105 | +3.25% | regress |
| wild-secrets-aws-access-key-id | short-subject-search | auto-nocaps | 982.327 | 1,012.533 | +3.07% | regress |
| floor-byte | short-subject-search | vm-caps | 664.143 | 684.437 | +3.06% | regress |
| numeric-id-nested-plus | short-subject-search | auto-caps | 824.603 | 847.448 | +2.77% | regress |
| base10num-near-miss | short-subject-search | vm-caps | 998.994 | 1,026.115 | +2.71% | regress |
| evil-alt-nested | large-subject-throughput | vm-in-caps | 12,009.904 | 12,333.527 | +2.69% | regress |
| wild-validator-ipv4-owasp | short-subject-search | vm-caps | 888.607 | 909.018 | +2.30% | regress |
| mojibake-curly-quote | short-subject-search | vm-caps | 669.326 | 684.472 | +2.26% | regress |
| wild-validator-us-zip-owasp | short-subject-search | auto-caps | 751.794 | 767.388 | +2.07% | regress |

62 more cells regress by less than 2%, down to +0.04%; full population
in the extraction script's own output. `floor-byte`/`wild-waf-crs-942500-
comment-obfuscation`/`winpath-near-miss` (all three named/carve-out
patterns already covered in §1) contribute floor-level regressing rows
into the <2% band; none of the 82 rows above is a named target or
carve-out pattern.

### 2.2 Non-named REGRESSIONS with before-median < 100 ns — the
floor-conversion cells (14 cells)

Every one of these is a DFA-route-only (`auto-caps`/`auto-nocaps`) or
mixed cell already near-instant (12-52 ns) before this pin, now moved to
either a still-small value or, on `date-nested-plus`/`vm-caps`, a much
larger one:

| pattern | regime | testee | before (ns) | after (ns) | Δ% |
|---|---|---|---|---|---|
| date-nested-plus | large-subject-throughput | vm-caps | 52.214 | 73.670 | +41.09% |
| wild-validator-us-zip-owasp | large-subject-throughput | auto-nocaps | 12.461 | 13.341 | +7.06% |
| wild-validator-us-zip-owasp | large-subject-throughput | vm-in-caps | 37.619 | 39.061 | +3.83% |
| wild-validator-us-zip-owasp | large-subject-throughput | auto-caps | 25.782 | 26.734 | +3.69% |
| phone-list-nested-plus | large-subject-throughput | vm-caps | 39.083 | 40.435 | +3.46% |
| uuid-near-miss | large-subject-throughput | vm-caps | 33.759 | 35.174 | +4.19% |
| numeric-id-nested-plus | large-subject-throughput | vm-caps | 39.117 | 40.060 | +2.41% |
| wild-validator-ipv4-owasp | large-subject-throughput | vm-in-caps | 34.242 | 34.647 | +1.18% |
| wild-datetime-moment-iso8601 | large-subject-throughput | auto-caps | 48.674 | 49.178 | +1.03% |
| numeric-id-nested-plus | large-subject-throughput | auto-caps | 27.664 | 27.806 | +0.51% |
| phone-list-nested-plus | large-subject-throughput | auto-nocaps | 14.276 | 14.325 | +0.35% |
| base10num-near-miss | large-subject-throughput | auto-caps | 16.022 | 16.084 | +0.39% |
| wild-validator-ipv4-owasp | large-subject-throughput | auto-caps | 31.092 | 31.147 | +0.18% |
| trim-nested-star | large-subject-throughput | auto-nocaps | 14.237 | 14.250 | +0.09% |

`date-nested-plus`/`vm-caps` is the one genuine outlier here (+41.1%, a
real ~21.5 ns move on an already-tiny baseline); the other 13 are
picosecond-scale IQR technicalities, the same shape §2.2 of the prior
ledger described.

### 2.3 The floor-CONVERGENCE population — both directions (non-named,
extending §1.2.2's `wild-validator-email-owasp` finding)

No non-named `large-subject-throughput` cell in this population COLLAPSED
from millions of ns to the ~23,100 ns floor the way the §1.1 targets did
(the biggest non-named improvement, `float-literal-bound`/`auto-caps`,
moved 1,939,786.6 → 1,890,624.0 ns, −2.53% — a real but modest move, not a
collapse); the floor-convergence-FROM-ABOVE mechanism this pin exercises
stays confined to the 6 named §1.1 targets plus the two §1.2 carve-out
patterns that already collapsed under the PRIOR pin (`wild-secrets-
slack-webhook-url`, `wild-semdiv-altorder-foo-foobar-rustregex`,
`wild-waf-crs-942500-comment-obfuscation`'s VM route). The
floor-convergence-FROM-BELOW direction (§1.2.2's `wild-validator-email-owasp`)
is likewise NOT matched by any non-named cell in this ledger's own
population — no other previously-near-instant pattern jumped onto the
~23,100 ns floor this cycle.

### 2.4 MISSING cells (10 rows, unchanged population from the prior ledger)

| pattern | regime | testee | before | after |
|---|---|---|---|---|
| evil-alt-nested | short-subject-search | auto-caps | expectation-failing (gave-up) | expectation-failing (gave-up) |
| evil-alt-nested | short-subject-search | auto-nocaps | expectation-failing (no-expectation) | expectation-failing (no-expectation) |
| evil-alt-nested | short-subject-search | vm-caps | expectation-failing (gave-up) | expectation-failing (gave-up) |
| evil-alt-nested | short-subject-search | vm-in-caps | expectation-failing (gave-up) | expectation-failing (gave-up) |
| wild-datetime-datefinder-alternation | large-subject-throughput | auto-caps | ABSENT (did-not-compile) | ABSENT (did-not-compile) |
| wild-datetime-datefinder-alternation | large-subject-throughput | vm-caps | ABSENT (did-not-compile) | ABSENT (did-not-compile) |
| wild-datetime-datefinder-alternation | large-subject-throughput | vm-in-caps | ABSENT (did-not-compile) | ABSENT (did-not-compile) |
| wild-datetime-datefinder-alternation | short-subject-search | auto-caps | ABSENT (did-not-compile) | ABSENT (did-not-compile) |
| wild-datetime-datefinder-alternation | short-subject-search | vm-caps | ABSENT (did-not-compile) | ABSENT (did-not-compile) |
| wild-datetime-datefinder-alternation | short-subject-search | vm-in-caps | ABSENT (did-not-compile) | ABSENT (did-not-compile) |

Exactly the same 10 cells as the prior ledger, unchanged in shape on both
sides of this pin (`wild-datetime-datefinder-alternation`'s
`auto-nocaps` compile — the only route that succeeds — still reads
`dfa`, `670274`/`665222`-byte-class diagnostics unchanged in cause);
NOT interpolated, no Δ computed, no NEW refusal appears on either side
of this pin boundary.

---

## 3. THE STAMP CENSUS (from the AFTER records, independently derived)

Computed by grouping all four AFTER records' `plain`-form compile rows
by `pattern_id` and reading `engine_metadata.{req_byte,req_run,
end_window,vm_start}` directly — no reliance on the repin lane's own
count. `req_byte`/`req_run`/`end_window` are pattern-level: checked
identical across all four AFTER testees wherever the pattern compiles on
more than one; the ONE pattern where they diverge,
`wild-datetime-datefinder-alternation`, diverges only because THREE of
its four testees fail to compile at all (unrelated to this pin's own
change — see §2.4) while `auto-nocaps` (the one route that compiles it)
stamps `none`/`none`/`none` cleanly.

### 3.1 Census counts (I-95 (a)'s ask)

**14 of 62 compiled patterns stamp a non-`none` `RX_REQ_RUN`** (2 of the
64-pattern corpus refuse for unrelated reasons:
`negation-scope-lookbehind-var` is `unsupported-by-declaration`,
`wild-datetime-datefinder-alternation` refuses on 3 of 4 routes as
above). **Independently reproduces the repin lane's own item-7 census
exactly: 14 run-stamping, 14 byte-moved, union 18 (4 run-only + 4
moved-only + 10 both) — no disagreement between this ledger's own
compile-row read and `docs/dev/lanes/b80repin_report.md`'s.**

**Run-length distribution (I-95 (a)'s explicit ask), hex-decoded:**

| length (bytes) | count | patterns |
|---|---|---|
| 2 | 8 | `keyword-prefix-order` ("in"@1), `logparse-atomic`/`logparse-atomic-removed` (": "@0), `nested-comment-rec`/`wild-waf-crs-942500-comment-obfuscation` ("*/"@0), `tag-depth3-bound`/`tag-pair-match` ("</"@0), `winpath-near-miss` (":\\"@1) |
| 3 | 3 | `wild-secrets-slack-webhook-url` ("://"@1), `wild-semdiv-altorder-foo-foobar-rustregex` ("foo"@0), `wild-semdiv-dollar-trailing-newline-pcre2` ("abc"@1) |
| 4 | 1 | `file-ext-order` (".tar"@0) |
| 5 | 1 | `router-prefix-order` ("/user"@0) |
| 8 | 1 | `wild-secrets-github-pat` ("hub_pat_"@3 — truncated from an 11-byte literal to `PCREC_MAX_REQ_RUN_EMIT`) |

Two identical run pairs by construction, both confirmed: `tag-depth3-bound`/
`tag-pair-match` both stamp `"</"@0`; `nested-comment-rec`/
`wild-waf-crs-942500-comment-obfuscation` both stamp `"*/"@0`.

### 3.2 Named expectations (I-95 (a)), checked by value

| pattern | expectation | measured (AFTER, all applicable testees identical) | match? |
|---|---|---|---|
| `wild-secrets-github-pat` | `REQ_RUN "hub_pat_"` scan index 3 | `req_run="6875625f7061745f@3"` → hex-decodes to `"hub_pat_"@3`; `req_byte="95"` (`_`, byte index 3 of the run) | **MATCH, exact** |
| `logparse-atomic` | `REQ_BYTE 58 (':')` | `req_byte="58"` | **MATCH, exact**; ALSO stamps `req_run="3a20@0"` → `": "@0`, unasked for by name but flagged in I-95's own prose as the falsifier-relevant fact |
| `router-prefix-order` | moved FROM 114; report new value | `req_byte="47"` (`/`), with `req_run="2f75736572@0"` → `"/user"@0` | **MATCH** |

### 3.3 Full per-pattern census (AFTER, `plain` form, 64 patterns)

`route(auto-X)` reads the ENGINE `auto-X` actually selected; `vm_start`
is read off the forced-VM (`vm-caps`) artifact. Routes are UNCHANGED from
the prior (8d716693) census on every one of the 62 compiling patterns —
[OPT-FREQPICK]/[OPT-REQPOS] moves byte encodings, not engine selection.

| pattern | req_byte | req_run | end_window | route(auto-caps) | route(auto-nocaps) | vm_start |
|---|---|---|---|---|---|---|
| balanced-parens-rec | 41 | none | none | vm | vm | unanchored |
| base10num-near-miss | none | none | none | dfa | dfa | anchored |
| bracket-array-define | none | none | none | vm | vm | anchored |
| codegrammar-flat | 34 | none | none | vm | dfa | unanchored |
| codegrammar-xflag | 34 | none | none | vm | dfa | unanchored |
| currency-lookbehind-fixed | none | none | none | vm | vm | unanchored |
| date-nested-plus | none | none | none | vm | dfa | anchored |
| doubled-word | none | none | none | vm | vm | unanchored |
| dup-param-detect | 38 | none | none | vm | vm | unanchored |
| email-local-nodup | none | none | none | vm | vm | anchored |
| email-nested-plus | 64 | none | none | vm | dfa | anchored |
| evil-alt-nested | none | none | none | vm | dfa | anchored |
| file-ext-order | 46 | ".tar"@0 | none | dfa | dfa | unanchored |
| float-literal-bound | 46 | none | none | vm | vm | unanchored |
| floor-byte | 126 | none | none | dfa | dfa | unanchored |
| high-byte-run | none | none | none | dfa | dfa | unanchored |
| ipv4-near-miss | 46 | none | 16 | dfa | dfa | anchored |
| keyword-prefix-order | 110 | "in"@1 | none | dfa | dfa | unanchored |
| logparse-atomic | 58 | ": "@0 | none | vm | vm | anchored |
| logparse-atomic-removed | 58 | ": "@0 | none | vm | dfa | anchored |
| mojibake-curly-quote | 148 | none | none | dfa | dfa | unanchored |
| negation-scope-lookbehind-var | n/a | n/a | n/a | unsupported-by-declaration | unsupported-by-declaration | n/a |
| nested-comment-rec | 42 | "*/"@0 | none | vm | vm | unanchored |
| numeric-id-nested-plus | none | none | none | vm | dfa | anchored |
| phone-list-nested-plus | none | none | none | vm | dfa | anchored |
| phone-palindrome-6 | none | none | none | vm | vm | unanchored |
| pwd-strength-chain | none | none | none | vm | vm | anchored |
| quoted-delim-match | none | none | none | vm | vm | unanchored |
| router-prefix-order | 47 | "/user"@0 | none | dfa | dfa | unanchored |
| tag-depth3-bound | 60 | "</"@0 | none | vm | vm | unanchored |
| tag-pair-match | 60 | "</"@0 | none | vm | vm | unanchored |
| trim-nested-star | none | none | none | vm | dfa | anchored |
| utf8-lead-no-cont | none | none | none | vm | vm | unanchored |
| uuid-near-miss | 45 | none | 37 | dfa | dfa | anchored |
| wild-codegrammar-json-array-begin | 91 | none | none | dfa | dfa | unanchored |
| wild-codegrammar-json-constant | none | none | none | dfa | dfa | unanchored |
| wild-codegrammar-json-number-extended | none | none | none | dfa | dfa | unanchored |
| wild-codegrammar-json-object-begin | 123 | none | none | dfa | dfa | unanchored |
| wild-codegrammar-json-stringcontent-escape | 92 | none | none | dfa | dfa | unanchored |
| wild-datetime-datefinder-alternation | none | none | none | did-not-compile | dfa | n/a |
| wild-datetime-moment-iso8601 | 45 | none | none | vm | dfa | anchored |
| wild-logparse-base10num-grok | none | none | none | vm | vm | unanchored |
| wild-logparse-base10num-noatomic | none | none | none | vm | vm | unanchored |
| wild-logparse-quotedstring-grok | none | none | none | vm | vm | unanchored |
| wild-logparse-quotedstring-noatomic | none | none | none | vm | vm | unanchored |
| wild-logparse-syslogbase-expanded | 58 | none | none | vm | vm | unanchored |
| wild-logparse-winpath-grok | 92 | none | none | vm | vm | unanchored |
| wild-secrets-aws-access-key-id | 65 | none | none | vm | dfa | unanchored |
| wild-secrets-github-pat | 95 | "hub_pat_"@3 | none | vm | dfa | unanchored |
| wild-secrets-slack-webhook-url | 47 | "://"@1 | none | vm | dfa | unanchored |
| wild-secrets-username-password-pair | 61 | none | none | vm | dfa | unanchored |
| wild-semdiv-altorder-foo-foobar-rustregex | 102 | "foo"@0 | none | dfa | dfa | unanchored |
| wild-semdiv-dollar-trailing-newline-pcre2 | 98 | "abc"@1 | 4 | dfa | dfa | unanchored |
| wild-semdiv-empty-alt-repeat-pcre2 | none | none | none | vm | dfa | unanchored |
| wild-validator-email-owasp | 64 | none | none | dfa | dfa | anchored |
| wild-validator-ipv4-owasp | 46 | none | 16 | vm | dfa | anchored |
| wild-validator-us-zip-owasp | none | none | 11 | vm | dfa | anchored |
| wild-validator-uuid-grok | 45 | none | none | dfa | dfa | unanchored |
| wild-waf-crs-942140-dbnames | none | none | none | dfa | dfa | unanchored |
| wild-waf-crs-942160-sleep-benchmark | 41 | none | none | dfa | dfa | unanchored |
| wild-waf-crs-942270-union-select | none | none | none | dfa | dfa | unanchored |
| wild-waf-crs-942360-concat-sqli | none | none | none | dfa | dfa | unanchored |
| wild-waf-crs-942500-comment-obfuscation | 42 | "*/"@0 | none | dfa | dfa | unanchored |
| winpath-near-miss | 92 | ":\\"@1 | none | dfa | dfa | anchored |

**REQ_BYTE VALUES moved on 14 patterns** (compared against the BEFORE
records' own compile rows): `codegrammar-flat`/`codegrammar-xflag`
58→34, `dup-param-detect` 61→38, `file-ext-order` 114→46,
`logparse-atomic`/`logparse-atomic-removed` 32→58, `nested-comment-rec`
47→42, `router-prefix-order` 114→47, `tag-depth3-bound`/`tag-pair-match`
62→60, `wild-semdiv-altorder-foo-foobar-rustregex` 111→102,
`wild-semdiv-dollar-trailing-newline-pcre2` 99→98,
`wild-validator-email-owasp` 46→64, `wild-waf-crs-942500-comment-obfuscation`
47→42. No pattern in the 64-pattern corpus lost a previously-present
`req_byte`/`end_window` entirely, and none gained `end_window` newly at
this pin (the three `end_window`-carrying patterns —
`ipv4-near-miss`/`uuid-near-miss`/`wild-semdiv-dollar-trailing-newline-pcre2`,
plus `wild-validator-ipv4-owasp`/`wild-validator-us-zip-owasp` — are
unchanged from the prior pin's own values, 16/37/4/16/11 respectively).

---

## 4. PROVENANCE

Window: **BEFORE 2026-09-23T03:19:36Z → 05:51:45Z; AFTER 2026-09-23T11:47:42Z
→ 14:13:52Z (07:47:42 → 10:13:52 EDT), 4/4 cells attempt-1 on each side**,
X13 `agree` on all 8 records with 0 `groups_disagreeing`, trial-agreement
worst group `phone-palindrome-6`/`short-subject-search` on every one
(§0.3). Worst gate-scope reading either window: 7.01% target-core busy
(AFTER auto-caps' pre-sample), well under the 10% pre-flight bar; worst
5-second non-target average 2.2% (same record); worst single-group
instantaneous spike 62.5% (BEFORE auto-caps, an 87 ms `date-nested-plus`
group — see §0.3 for why this is the same figure the report header
names, and why it did not move that record's own `pass` verdict).
Queries: this ledger's own extraction script (`pcrecbench.reduce`
imported directly against the 8 `.jsonl` files by path, §0.2); the
cross-check query against `reports/2026-09-23-capability-0.1-budu-ryzen1600-after-b1885a83.tsv`
was `grep '^rank\s+<pattern>\s+(set)\s+<regime>' <file> | grep median_ns`.

**What was read:** all 8 records' `setup`/`compile`/`match` rows in
full; the AFTER cross-pin report TSV's header and the specific `rank`
rows named in §0.2's cross-check; `docs/dev/lanes/b80repin_report.md`
in full (for its item-7 census, cross-checked and reproduced independently
in §3, and for its `make check` numbers); I-95's full text and I-99/
I-100/I-101 in full (`docs/dev/inbox_from_pcrec.md`).

**What was NOT read:** both `.subject-grain.tsv` files (~53.6 MB each);
both `.md`/`.matrix.html`/`.matrix.tsv` renders; both
`.interpretation.md` sidecars. Per the brief's own note and `b80repin`'s
own `make check` finding (163 passed / 28 FAILED, all 28 in
check-interpret §3 "sidecar freshness," pre-existing and unrelated to
this pin's own change): **the `2026-09-23-capability-0.1-...-after-8d716693.interpretation.md`
sidecar is ALREADY STALE against records committed since its last
regeneration, and no sidecar exists yet for `after-b1885a83` at all** —
this ledger's findings are read from the records and report directly,
never from an interpreter pass, consistent with I-99 (3)/I-100 (4)'s
ruling that tonight's ledger ships in the existing single-roster shape
and the class-pure views/cross-class query ([B82]) are a follow-up on
these SAME records, not a re-run.

---

## 5. RANKED FINDINGS (facts only)

1. **Of I-95 (a)'s 7 named target cells (28 rows across 4 testees), only
   11 of 28 MEET the D119 bar; 17 MISS it, including the named
   throughput regime of BOTH `logparse-atomic` (I-95's own
   "no-decline-rule falsifier") and `router-prefix-order` (I-95's "freq
   pick's live case") on ALL FOUR testees or worse.** `router-prefix-order`/
   `large-subject-throughput`/`auto-caps`/`auto-nocaps` regresses
   **+80.83%/+80.59%**, roughly 10× its own before-IQR, moving
   398→720 μs — the single largest regression on any named target cell
   in either this or the prior ledger. `logparse-atomic`/
   `large-subject-throughput` regresses on all four testees (+7.0% to
   +41.8%), confirming the stamp census's independent finding (§3.1/3.2)
   that this pattern now carries a real 2-byte run (`": "@0`) rather
   than only a pick move — the run's presence did not prevent, and on
   the VM route coincides with the largest, regression.

2. **`wild-validator-email-owasp`/`large-subject-throughput` regresses
   +27,009.85% to +52,757.09% on all four testees**, moving from
   43.7-85.3 ns (near-instant) to 23,118.8-23,200.5 ns — landing on the
   SAME ~23,100 ns floor that eight of §1.1's named targets collapse
   DOWN onto from millions of ns. This is the floor-convergence
   phenomenon the prior ledger's finding 2 first named, now confirmed
   reached from BELOW by a NEW pattern this cycle (the prior ledger's
   two below-floor joiners were `winpath-near-miss`/`email-nested-plus`;
   no non-named cell in this ledger's own population joins it, per §2.3).

3. **`wild-secrets-github-pat`, `nested-comment-rec`, and `tag-depth3-bound`
   are the three named-target patterns that meet or mostly meet the
   bar**, each with the same shape: `nested-comment-rec` meets cleanly
   on all four testees (−99.75% to −99.76%, millions of ns collapsing to
   the ~23,100 ns floor); `wild-secrets-github-pat` meets ONLY on its
   forced-VM route (−97.6%/−97.9%, millions of ns collapsing to
   ~125-129 μs) while its DFA route — already at ~124-125 μs before this
   pin, not millions — regresses +3.3%/+3.8%; `tag-depth3-bound`
   improves marginally on 3 of 4 testees at the already-reached
   ~23,100 ns floor. `tag-pair-match`, which shares `tag-depth3-bound`'s
   identical `req_run` stamp (`"</"@0"`), instead regresses on 2 of 4
   testees and reads within-bar on the other 2 — the two "identical
   run" patterns diverge on their D119 verdict.

4. **The union-18 carve-out population is net-improving but not
   uniformly so**: §1.2.1's 14 REQ_RUN-stamping patterns read 57
   improve / 23 regress / 4 within-bar (before-IQR); §1.2.2's 14
   REQ_BYTE-moved patterns read 64 improve / 21 regress / 3 within-bar.
   `keyword-prefix-order`/`large-subject-throughput` is the largest
   carve-out regression (+59.6%/+59.7% on the DFA route, +8.0%/+8.3% on
   the VM route) — none of I-95's own prose named this pattern as a
   target, but its `req_run` stamps (`"in"@1`) place it in the union-18
   population by construction. `logparse-atomic-removed` regresses on 6
   of its 8 cells (+1.7% to +31.5%), the DFA route worst.

5. **The non-named (90-pattern) population shows no large collapse
   either direction this cycle** — unlike the prior ledger, whose
   non-named population included 44 cells collapsing from millions of ns
   to near-zero. The largest non-named regression by percentage,
   `ipv4-near-miss`/`short-subject-search`/`vm-in-caps` (+11.16%), and
   the largest by absolute IQR-relative margin, `phone-palindrome-6`/
   `large-subject-throughput`/`vm-caps` (+8.77%, IQR 549,497 ns wide but
   still cleared), sit far below the named-target population's movements
   in scale. 82 of 360 non-named cells regress at or above their
   before-IQR with a before-median ≥ 100 ns (§2.1); 14 more are
   floor-level (<100 ns) technicalities (§2.2), one of which
   (`date-nested-plus`/`vm-caps`, +41.1%) is a real move on a tiny
   baseline rather than a picosecond artifact.

6. **Measurement quality is clean on both sides of the comparison**: all
   eight records attempt-1, X13 `agree` with 0 disagreeing groups on
   every one, box quiet throughout (worst gate-scope reading 7.01%,
   worst 5-second non-target average 2.2%, both well under the 10%
   pre-flight limit; one 62.5% single-group instantaneous spike traced
   to an 87 ms group that did not move its record's own `pass`
   verdict), no `inconclusive-spread` re-measure on either side (§0.3) —
   no measurement-quality caveat qualifies any number in §1 or §2. The
   D119 verdict is IDENTICAL under the before-IQR and after-IQR readings
   on every one of §1.1's 28 target rows (no flip), unlike the prior
   ledger's one flip.

7. **KB-27's fix reproduces clean across this pin boundary**:
   `rd-evil-alt-near-miss`/`sd-empty-alt-hit` under `evil-alt-nested`/
   `short-subject-search` read identically on BOTH pins on all four
   testees — `gave-up`×5 on `auto-caps`/`vm-caps`/`vm-in-caps`,
   `did-not-match-as-expected` with `n_no_expectation=5` on
   `auto-nocaps` — unchanged in shape by this re-pin, independent of
   anything I-95 asked about.
