# [OPTLOOP.1] — READING THE BATCH-1 LEDGER (O-45) AGAINST THE D119 BAR

Lane `b1ledger`, 2026-09-23, branch `lane/b1ledger` from `467a08f3`.
Analysis + compile-side measurement only: nothing under `src/`, `cli/`,
`lib/` or `tests/`; nothing written in `/Users/fdicostanzo/pcrec-bench`
(read-only reference). **No clock was read on this box.** Every number
below is either the bench's Ryzen 1600 measurement, or a structural fact
read off emitted C, or an exact arithmetic count (subject bytes, find-all
call counts, `memchr` scan distances, object symbol sets).

**The bench REPORTS and does not diagnose (D78 / I-57). This file is the
diagnosis.**

**Sources.** `pcrec-bench/docs/dev/outbox_to_pcrec.md` O-45; the ledger
`pcrec-bench/docs/dev/ledgers/2026-09-23-optloop1-batch1-after-8d716693.md`
(660 lines, §1 the D119 table, §2 the out-of-bar cells, §3 the stamp
census, §4 the ranked findings); the report group
`pcrec-bench/reports/2026-09-23-capability-0.1-budu-ryzen1600-after-8d716693.*`.
BEFORE = pcrec `25b1984f` (abi 27), AFTER = pcrec `8d716693` (abi 29).
Δ% convention throughout is the ledger's: **positive is SLOWER.**

**The compiler this lane read.** `git diff 8d716693..467a08f3 -- src/ cli/
lib/` is one `CLAUDE.md` line, so this worktree's `build/pcrec` emits what
the measured pin emitted. The BEFORE compiler is `git archive 25b1984f`
built in the session scratchpad; every artifact pair below was emitted to
the **same `-o` basename** in two directories (the `-o`-basename trap,
this house's fifth recorded instance — it fired once in this lane's own
first identity census and was caught by the census reading 0 identical).

Reproduction pieces: `docs/dev/optloop/b1ledger/` (its own `CLAUDE.md`).

---

## 0. THE SUBJECT ARITHMETIC EVERY NUMBER BELOW RESTS ON

`bench/capability`'s `large-subject-throughput` regime has **three**
subjects — `t-64k` 65,536 B, `t-256k` 262,144 B, `t-1m` 1,048,576 B,
**1,376,256 bytes in total** — and a set-grain cell is the SUM over the
three. All three were regenerated here from `captext.text(n, seed)` and
their **sha256 checked against the committed `manifest_throughput.tsv`:
3 of 3 match**, so the byte censuses below are the bench's own subjects
and not a lookalike.

**The regime is FIND-ALL** (`adapter.py:3696-3698` appends `--find-all`
when `regime == "throughput"`, over and above `REGIME_MODE`'s `search`),
so `<prefix>_search` is called once per match plus once to fail, and a
per-call pre-check is paid once per match. This is load-bearing: the
first cost model this lane wrote assumed one call per subject and was
wrong by four orders of magnitude on the cells with many matches.

**The floor rate.** `floor-byte` (`~`) at the AFTER pin reads 23,113.3 ns
on `auto-caps` for those 1,376,256 bytes = **0.016795 ns/byte, 59.6 GB/s**
— one `memchr`-class linear pass over the whole throughput subject set.
Every "≈23,100 ns" in the ledger is that one number.

---

## 1. THE NULL CONTROL — 16 REGRESSING CELLS WHOSE PROGRAM DID NOT CHANGE

This was not asked for and it re-reads everything that follows, so it is
first.

All 64 `capability` patterns were compiled at both pins in all three of
the bench's flag sets (`auto`, `--no-captures`, `--engine=vm`) and the two
artifacts compared line by line, ignoring only the generated-by comment,
the three NEW `#define`s (`RX_REQ_BYTE`, `RX_END_WINDOW`, `RX_VM_START`),
`#include <string.h>` and the `.abi` integer:

| outcome | artifact-configs |
|---|---|
| **program-identical across the pin** | **56** |
| changed — required-byte pre-check | 85 |
| changed — VM anchor bound only | 20 |
| changed — pre-check + anchor bound | 11 |
| changed — pre-check + end window | 8 |
| changed — all three | 4 |
| changed — end window (+/- anchor bound) | 3 |
| refused at both pins | 5 |

16 patterns are program-identical on all three configs. For four of them
the `__text` section of the compiled object was compared byte for byte
(gcc-16 `-O2 -fPIC`, arm64): **identical md5, identical size, on all
four** (`phone-palindrome-6` 3,355 B, `quoted-delim-match` 4,123 B,
`wild-codegrammar-json-constant` 3,911 B,
`wild-logparse-quotedstring-noatomic` 10,997 B).

Joining that census against the ledger's §2.1 table:

**16 of the 64 non-named cells the ledger scores as regressing beyond
their IQR sit on an artifact whose executable text did not change**, at
Δ% from **+0.04% to +8.46%**, median +0.52%. The worst of them is

| cell | before (ns) | after (ns) | Δ% | before IQR | Δ ÷ IQR |
|---|---|---|---|---|---|
| `phone-palindrome-6` / thr / `auto-caps` | 6,585,253.9 | 7,142,399.5 | **+8.46%** | 15,787.5 | **35.3×** |

Nothing in that artifact moved but three unreferenced macros and one
integer field in `rx_info`.

**What this measures.** The D119 bar's noise model is the cell's own
within-window IQR over 5 trials. The comparison it is applied to spans
two windows a day apart (2026-09-22T02:11Z and 2026-09-23T03:19Z). The
IQR cannot see the between-window component — box state, frequency, page
and address layout — and the null population says that component reaches
at least **8.46%** of a throughput cell's median on this box. The eight
records are all X13 `agree`, attempt 1, other-core busy ≤6.06%: the
hygiene gate is clean and this is not a hygiene failure. It is the wrong
noise model, and the instrument that measures the right one was already
sitting in the data for free.

**Applied to the ledger's §2.1 population of 64 regressing cells:**

| class | cells |
|---|---|
| program-identical artifact (null controls) | 16 |
| changed artifact, Δ% ≤ the null band's observed max (8.46%) | 34 |
| changed artifact, Δ% **above** the null band | **14** |

So "a 64-cell population of everyday patterns picks up real regressions"
(ledger finding 6) is **14 cells**, not 64. The 14 are named in §4.3.

**This does not dissolve the named findings.** `nested-comment-rec`
(+18.8% to +25.0% on four separately-compiled artifacts),
`uuid-near-miss`/`ipv4-near-miss` (+18.7% to +38.5% on eight cells) and
the 1,150× floor cells (§5) are all well outside the band and are
reproduced by an independent cost model below. It does dissolve
`router-prefix-order`'s two misses (§3) and 34 of the §2.1 rows.

---

## 2. THE D119 VERDICT, PER MECHANISM

D119 rule 4: *a mechanism lands only if its target cells' median
improvement exceeds their IQR AND no carve-out cell regresses by more
than its IQR.* The ledger computes the bar per CELL; the bar is stated
per MECHANISM, so the 41 target rows and 32 carve-out rows are
attributed to their mechanism here using I-87's own mapping and the
ledger's §3.2 stamp census.

### 2.1 [OPT-ANCHOR-VM] — the VM's attempt-loop start bound

| | rows | result |
|---|---|---|
| targets | 13 (`bracket-array-define` thr ×4 + srch ×4, `evil-alt-nested` thr ×4, `trim-nested-star` thr `auto-caps`) | **13/13 improve ≫ IQR** (−9.36% to −99.9986%) |
| attributable regressions | 0 outside the null band | — |

The four patterns ledger finding 6 attributes to this mechanism
(`date-nested-plus`, `phone-list-nested-plus`, `numeric-id-nested-plus`,
`base10num-near-miss`, regressing 1.0-4.7%) all sit **inside** the null
band, and the finding needs one correction: on `auto-nocaps` those
patterns take the DFA route, where no `RX_VM_START` is emitted at all —
`date-nested-plus`/srch/`auto-nocaps` (+4.68%) is on a
**program-identical** artifact.

Where the mechanism can be read alone, it is a clean win:
`email-nested-plus`'s VM artifact gains `const size_t attempt_max =
search_from;` and one changed loop exit, which is the whole of
[OPT-ANCHOR-VM] in two lines.

**VERDICT: MEETS THE BAR.**

### 2.2 [OPT-ENDWIN] — the end-anchor start window

| | rows | result |
|---|---|---|
| targets | 4 (`wild-semdiv-dollar-trailing-newline-pcre2` thr ×4) | **4/4 improve** (−99.968% to −99.998%) |
| carve-outs charged to it | `uuid-near-miss`, `ipv4-near-miss` (16 rows) | 8 regress — but **not this mechanism's cost**, §4.2 |

The clamp is pure arithmetic — two compares and a subtraction
(`emit_dfa.c`'s `pcrec_emit_end_window_clamp`). Isolated with the deny
flags on `uuid-near-miss`, `-fno-req-byte` leaves the clamp alone and
`-fno-end-window` leaves the `memchr` alone; the measured cost lives in
the second. The clamp in fact **rescues** the pre-check on those two
patterns: without it the `memchr` window would be the whole subject
(23 µs a call) instead of 37 bytes (≈3 ns a call).

**VERDICT: MEETS THE BAR** — contingent on the axis-isolated re-measure
(§8, block B) confirming the clamp alone costs nothing.

### 2.3 [OPT-REQBYTE] — the necessary-byte whole-window pre-check

| | rows | result |
|---|---|---|
| targets | 20 (5 patterns × 4 configs) | **20/20 improve 98.20-99.885%** |
| target, reclassified | 4 (`router-prefix-order`) | 2 improve, **2 miss** (+1.19%, +1.21% — inside the null band, §3) |
| carve-out `floor-byte` | 8 | 7 improve/flat, 1 at +0.12% (28.5 ns) |
| carve-out `nested-comment-rec` | 8 | 4 improve 70.9-75.4%, **4 regress 18.8-25.0%** |
| carve-out `uuid`/`ipv4` DFA route | 8 | **8 regress 18.7-38.5%** (this mechanism's cost, §4.2) |

Twelve carve-out cells regress by far more than their IQR and by more
than the null band. D119's second clause is not satisfied.

**VERDICT: TARGETS MEET, CARVE-OUT CLAUSE FAILS.** The mechanism is worth
what the targets say it is worth — it is the largest win in the batch by
a wide margin — and as emitted it also carries three defects, each with a
general fix (§6).

---

## 3. THE TWO MISSES — `router-prefix-order`, DFA route, throughput

`/user|/users`. `RX_REQ_BYTE "114"` (`r`), confirmed by value. The
regression is +1.1850% (`auto-caps`, 393,757.0 → 398,422.8 ns, +4,665.8)
and +1.2066% (`auto-nocaps`, +4,754.0), each about 10× a very tight
before-IQR of 431/1,399 ns. The same pattern's forced-VM throughput and
all four configs' short-search improve.

**What the artifact does there.** Compiled and read:

```
 line  17:  #define RX_DFA_PREFILTER "memchr"
 line  49:      !memchr(subject + search_from, 114, subject_length - search_from))   <- the pre-check
 line 115:          const void *q = memchr(subject + scan_position, 47, ...);        <- the prefilter
```

Two `memchr` passes per call, on two different bytes, in one function.

**The cost, counted exactly.** Running the real artifact's find-all loop
over the three subjects: **312 matches, 315 calls**, and the pre-check's
`memchr` scans **18,260 bytes in total** (the distance from each match end
to the next `r`). At the floor rate that scan is 307 ns; the remaining
cost is the call itself, 315 of them. At a realistic glibc `memchr` call
cost of ~12 ns for a ~58-byte scan, 315 calls come to 3,780 ns, and
307 + 3,780 = **4,087 ns against a measured 4,666 ns — 88% of the
regression, from the pre-check's own per-call overhead.**

**Ranked hypotheses.**

1. **The pre-check is strictly DOMINATED on this artifact** (confidence:
   high; the arithmetic above plus the byte census). Counted in the
   bench's own throughput subjects, the pre-check's byte `r` has density
   5.2564% and the prefilter's byte `/` has density 2.8407% — the
   pre-check tests a byte **1.85× COMMONER** than the byte the artifact
   already filters on, so it can never dismiss a window the prefilter's
   own pass would not dismiss sooner. Every one of its 315 calls is pure
   cost. Discriminating measurement: §8 block A (`-fno-req-byte` on this
   pattern must recover the BEFORE number; the axis exists).
2. **The pick is the wrong member of the set** (confidence: high, same
   census). The necessary set for `/user|/users` is `{/, u, s, e, r}`
   with densities `/` 2.84%, `u` 2.79%, `s` 4.38%, `e` 8.52%, `r` 5.26%.
   PCRE2's rightmost rule picks the second-commonest. This is
   `c2design`'s F1 finding with a measured cost attached, and
   [OPT-FREQPICK] (lane `optimpl2`, parked at abi 30) is the fix already
   designed and built.
3. **Code-generation perturbation** (confidence: low here, high
   elsewhere — §4.3). Residual after 1: ~580 ns, i.e. 0.15% of the cell.

**Disposition.** Both misses are +1.19%/+1.21% on a cell whose null-band
sibling moved +8.46% with no code change at all. **They are not
distinguishable from the between-window band and should not, on this
evidence, block the mechanism.** They are nevertheless a real
cost-of-mechanism cell, they are fully explained, and both of the two
fixes that remove them are already designed.

---

## 4. THE CARVE-OUT REGRESSIONS

### 4.1 `nested-comment-rec` — +18.8% to +25.0% on all four configs

**Hypothesis 1 below is REFUTED on x86_64 — see §9(C).**

`(/\*(?:[^*/]|\*(?!/)|/(?!\*)|(?1))*\*/)`. Route `vm` under BOTH auto
configs (so the four testees are four VM measurements, not a DFA/VM
split), `RX_VM_PREFILTER "none"`, `RX_VM_START "unanchored"`,
`RX_REQ_BYTE "47"`.

**The diff across the pin is four lines**, and the whole of it is:

```c
 static int rx_search_run(const unsigned char *subject, size_t subject_length,
        size_t search_from, ptrdiff_t (*capture_spans)[2], rx_run_state *run)
 {
     ...
     if (search_from > subject_length) return 0;
+    if (subject_length <= search_from ||
+        !memchr(subject + search_from, 47, subject_length - search_from))
+        return 0;
     attempt_position = search_from;
```

plus `#include <string.h>` and three `#define`s. `RX_VM_ENTRY_SHAPE`
("plain"), `RX_VM_RUNGS` (`0x4u`) and `RX_VM_PROGRAM_BYTES` (10432) are
unchanged, so no rung, route or engine decision moved.

**The `memchr` cannot be the cost, and the margin is five orders of
magnitude.** Counted on the real artifact: the pattern has **0 matches**
in all three subjects, so find-all makes **3 calls**, and `/` first
occurs at offset 875 / 89 / 84 — the pre-check reads **1,051 bytes in
total**, ≈25 ns. The measured regression is **+1,528,965 ns**
(`auto-caps`, 7,798,115.1 → 9,327,080.3). **Ratio 60,674×.**

Per byte: the engine walk is 5.666 ns/byte before and 6.777 ns/byte
after, so the added cost is **1.111 ns per byte of subject** — a
PER-ATTEMPT cost, on a mechanism whose only emitted code runs once per
call.

**Ranked hypotheses.**

1. **The pre-check's PLACEMENT changed gcc's compilation of the function
   that carries the attempt loop.** `rx_search_run` is that function: the
   `for (;;)` over `attempt_position` calling `rx_match_anchored` lives
   in it, and the pre-check was emitted INTO it. Measured here on
   arm64/gcc-16 `-O2`: at the BEFORE pin the object exports
   `_rx_search_run.part.0` — gcc's partial-inlining split — and at the
   AFTER pin it exports a whole `_rx_search_run` with no split. Across
   all 62 compiling forced-VM artifacts, **24 lose that split at the AFTER
   pin, and in all 24 the pre-check is the thing that was added**
   (12 more carry the pre-check without flipping, so the pre-check is
   necessary and not sufficient). The three biggest unexplained VM-route
   regressions in the ledger — this one, `float-literal-bound`,
   `file-ext-order` — are all in the flipping 24. `rx_match_anchored`
   itself is 716 asm lines in both builds and out of line in both, so the
   hot body's INSTRUCTIONS did not change; its ADDRESS did (object
   `__text` 5,651 → 5,483 bytes).
2. **An x86_64/gcc-15.2-specific inline decision that reaches the
   per-attempt path.** [CC-DIFF] STEP 0 already measured, at this exact
   seam, gcc stopping at a call boundary where clang inlined, costing a
   152-byte frame and a `-fstack-protector-strong` canary per entry. If
   on the bench's toolchain `rx_match_anchored` stops being inlined into
   `rx_search_run`, or the frame grows, the cost is per ATTEMPT and
   1.111 ns/byte is exactly the right size for it. Not observable on
   arm64 (out of line in both builds) — this is why §8 block C exists.
3. **Pure alignment**: the hot loop is byte-identical and moved. Weak
   support: the AFTER-side trial IQR blows up from 1,926.8 to 597,173.7 ns
   (310×) on this cell, and per-process ASLR is the ordinary source of
   run-to-run front-end variance. Weak counter-argument: four
   independently compiled artifacts all regressing 18.8-25.0% is not what
   four independent alignment accidents look like.
4. **REFUTED — the scan cost**: 25 ns measured against 1.53 ms.
5. **REFUTED — cache pollution by the pre-check's pass**: it touches
   ≤875 bytes, 14 cache lines, per call.
6. **REFUTED — a route/rung/engine change**: every stamp identical but
   the three new ones.

### 4.2 `uuid-near-miss` / `ipv4-near-miss` — the DFA route, both regimes

`^[0-9a-fA-F]{8}-…{12}$` and `^(?:(?:25[0-5]|…)\.){3}(?:…)$`. Both
`RX_ENGINE "dfa"`, `RX_DFA_PREFILTER "none"`, and both gained an end
window (37 and 16 bytes, exact) and a required byte (`-` and `.`).

**The brief's framing needs one correction before the answer.**
[OPT-ENDWIN] on the DFA route is **not a reverse pass**. It is a start
clamp, two compares and a subtraction:

```c
    if (subject_length > 37ULL && search_from < subject_length - 37ULL)
        search_from = subject_length - 37ULL;
```

There is no per-attempt window cost to measure.

**What the cost is.** With the clamp in place the pre-check's `memchr`
runs over the last 37 (16) bytes only. Counted on the real artifacts:
3 calls, **98 bytes** (`uuid`) and **48 bytes** (`ipv4`) scanned in
total. Predicted added cost ≈ 3 `memchr` calls ≈ 9.1 / 8.3 ns. Measured:
**+7.6 ns** (19.930 → 27.576) and **+6.2 ns** (18.791 → 24.961). In the
search regime, 75 calls: +1.40 ns and +1.80 ns per call. **The model
predicts these cells to within a nanosecond.**

So the +38.5% is a true percentage of a very small number: ~2.5 ns of
`memchr` call overhead added to a route whose entire answer took ~6.6 ns.

**And the artifact already knows it did not need the check.** In the
emitted C:

```
 line 35:      search_from = subject_length - 37ULL;      <- the end-window clamp
 line 37:      !memchr(subject + search_from, 45, ...)    <- the pre-check, a call
 line 96:  const size_t start_max = 0 /* fully ^-anchored */;
 line 97:  for (start = search_from; start <= start_max; start++) {
```

For any subject longer than 37 bytes the clamp makes `search_from >
start_max`, so the loop body never runs and the function returns 0 — by
arithmetic, at zero cost. **The free check that decides the call is
emitted 59 lines below the `memchr` call that cannot.** The forced-VM
route improves 81-100% on the same patterns because there the attempt
loop was real.

### 4.3 The 14 non-named cells above the null band

| Δ% | cell | class |
|---|---|---|
| +34.06 | `logparse-atomic-removed` srch `auto-nocaps` | one-start (§6 G2) |
| +32.60 / +32.50 | `wild-codegrammar-json-array-begin` thr `auto-nocaps`/`auto-caps` | duplicated pass (G1) |
| +25.64 | `wild-validator-ipv4-owasp` srch `auto-nocaps` | one-start (G2) |
| +22.63 | `wild-secrets-github-pat` thr `vm-in-caps` | perturbation (G3) |
| +17.18 / +15.96 | `float-literal-bound` thr `vm-caps`/`vm-in-caps` | perturbation (G3) |
| +17.07 / +17.00 | `winpath-near-miss` srch `auto-caps`/`auto-nocaps` | one-start (G2) |
| +15.45 / +14.39 | `wild-codegrammar-json-array-begin` thr `vm-in-caps`/`vm-caps` | duplicated pass (G1) |
| +10.81 / +10.68 | `file-ext-order` thr `vm-caps`/`vm-in-caps` | perturbation (G3) |
| +10.07 | `wild-validator-uuid-grok` srch `auto-nocaps` | pre-check call cost |

**`wild-codegrammar-json-array-begin` is `\[` — a single literal.** Its
artifact emits `memchr(..., 91, ...)` at line 49 as the pre-check and
`memchr(..., 91, ...)` at line 107 as the candidate-start prefilter:
**the same byte, twice, every call.** Counted: 7,816 matches, 7,819
calls, and the pre-check scans exactly 1,376,256 bytes in total (one full
pass — every match IS a `[`). Predicted added cost 23,118 ns of scan plus
7,819 `memchr` calls; measured +85,950 ns, which the model reproduces
within ~10% at a 7 ns call cost. `floor-byte` is the control for the same
shape with the byte ABSENT: the pre-check returns 0 and the prefilter's
pass never runs, so one pass either way — measured −29.4 ns, flat.

**The perturbation class, counted:**

| cell | pre-check's own measured work | measured Δ | ratio |
|---|---|---|---|
| `nested-comment-rec` thr `auto-caps` | 1,051 B / 3 calls ≈ 25 ns | +1,528,965 ns | 60,674× |
| `wild-secrets-github-pat` thr `vm-in` | 617 B / 3 calls ≈ 18 ns | +1,080,891 ns | 60,400× |
| `file-ext-order` thr `vm-caps` | 107 B / 3 calls ≈ 9 ns | +416,636 ns | 44,814× |
| `float-literal-bound` thr `vm-caps` | 571,928 B / 7,822 calls ≈ 29 µs | +3,245,030 ns | 111× |

All four are VM-route cells whose pre-check went into `rx_search_run`.
Three of the four are in the partial-inlining-flip 24;
`wild-secrets-github-pat` is not, and it regresses +22.63% through
`rx_search_in` while the SAME artifact regresses +3.03% through
`rx_search` — one artifact, two entries, two answers, which is a layout
signature and not a mechanism cost.

---

## 5. THE ~23,100 ns FLOOR, ENTERED FROM BELOW

O-45 item 3 and ledger finding 2: eight of the nine named-target rows
land in a 23,088-23,190 ns band from millions of ns above, and two
previously near-zero DFA-route cells RISE into it. The rise is now
explained exactly.

| pattern | required byte | occurrences in the 3 subjects | before (ns) | after (ns) | predicted added | measured added |
|---|---|---|---|---|---|---|
| `winpath-near-miss` thr `auto-caps` | 92 `\` | **0** | 20.088 | 23,123.6 | 23,120.8 | 23,103.5 |
| `email-nested-plus` thr `auto-caps` | 64 `@` | **0** | 47.279 | 23,106.9 | 23,120.8 | 23,059.6 |
| `floor-byte` thr `auto-caps` (control) | 126 `~` | **0** | 23,142.7 | 23,113.3 | 23,120.8 | −29.4 |

The model is exact to 0.08% and 0.27%. The required byte is absent from
every throughput subject, so the `memchr` reads all 1,376,256 bytes and
returns NULL — the correct answer, at 1,150× and 488× the cost of the
answer the artifact gave before.

**Why they were ~20 ns before.** Read off the BEFORE artifact:

```c
    const size_t start_max = 0 /* fully ^-anchored */;
    for (start = search_from; start <= start_max; start++) {
```

One start position, a handful of bytes into the state machine, dead. An
O(1) exit. `email-nested-plus` is the same on the VM route, where the
AFTER build additionally emits `const size_t attempt_max = search_from;`
— [OPT-ANCHOR-VM] correctly reducing it to one attempt — **below** the
`memchr` that scans a megabyte.

**Why `floor-byte` is the control and not a counter-example.** It carries
the same byte in the pre-check and in its own candidate-start prefilter.
Absent, the pre-check returns 0 and the prefilter never runs: one pass
before, one pass after. The pre-check REPLACED a pass rather than adding
one, which is the only shape in which a whole-window pre-check is free.

---

## 6. THE GENERAL FINDING, AND THE MECHANISM IT PROPOSES

Stated once: **a pre-check must be admitted by comparing its cost class
against the route it guards, and it must not be emitted inside the
function that carries the loop it is trying to avoid.** The batch shipped
three violations of that, each with a general form.

### G1 — DOMINANCE. Do not emit a pass the artifact already runs.

`pcrec_emit_req_byte_check`'s own header says the mechanism "EXTENDS THE
PREFILTER PRIMITIVE RATHER THAN PARALLELING IT". On a DFA artifact that
already emits `RX_DFA_PREFILTER "memchr"` for byte `p`, a necessary-byte
pre-check for byte `q` parallels it exactly, and is worth emitting only
if `q` is strictly rarer than `p`. Measured: all three DFA artifacts in
this population have `q == p` (`floor-byte`, `wild-codegrammar-json-
array-begin`) or `q` commoner than `p` (`router-prefix-order`, 1.85×) —
and the two where the byte is present are the two worst DFA-route
regressions in the ledger.

**Rule:** where the artifact emits a candidate-start `memchr` for `p`,
emit the necessary-byte pre-check only for a `q` with a strictly lower
`pcrec_byte_freq_ppm`; otherwise decline. The value is already in the
tree (`src/opt/prefix_k.c:91`) and [OPT-FREQPICK] is already its third
reader.

### G2 — ADMISSION. Do not precede an exit cheaper than the pre-check.

`attempt_cand` (`src/gen/emit_dfa.c:2999`) already carries the rule, for
the prefilter:

> *A fully-anchored pattern already runs ONE attempt (`start_max` is the
> literal 0), so there is nothing between attempts to skip.*

The candidate-start prefilter declines itself on those artifacts — which
is exactly why `winpath`/`uuid`/`ipv4` read `RX_DFA_PREFILTER "none"` —
and the pre-check, emitted one level above, did not inherit the decline.
This is D120's own shape: a fact computed in one file and not reached by
a later consumer.

**Rule:** decline the whole-window pre-check when the artifact's
candidate-start set is a single position — `start_max` a literal 0 on the
DFA route, `RX_VM_START "anchored"`/`"gstart"` on the VM route. Measured
population: **9 patterns, 27 artifact-configs, 29 regressing ledger
cells** (8 carve-out rows, 8 of §2.1, 13 of §2.2) — `email-nested-plus`,
`ipv4-near-miss`, `logparse-atomic`, `logparse-atomic-removed`,
`uuid-near-miss`, `wild-datetime-moment-iso8601`,
`wild-validator-email-owasp`, `wild-validator-ipv4-owasp`,
`winpath-near-miss`. Zero named target rows are in that population (every
met target is unanchored, or is a `RX_VM_START "anchored"` row carrying
NO required byte), so the decline costs the batch nothing it won.

The stronger form of the same rule, free once the bound is read: when the
end-window clamp and the start bound INTERSECT EMPTY — `search_from >
start_max` — return 0 before any check at all. On `uuid`/`ipv4` that is
every subject longer than 37/16 bytes.

### G3 — PLACEMENT. Do not compile the pre-check into the hot function.

**REFUTED on x86_64, see §9.** The arm64/gcc-16 `.part.0`-loss mechanism
below does not reproduce on the bench's own gcc-15.2/x86_64 box; G3's
rule may still stand as a byte-identity discipline (its own acceptance
criterion), but not yet as a demonstrated performance win on the box that
measures.

On the VM route the check is emitted inside `rx_search_run`, the function
holding the attempt loop. Measured consequence: 24 of 62 forced-VM
artifacts lose gcc's partial-inlining split of that function, and the
four cells whose regression the cost model misses by 111×-60,674× are all
VM-route cells. On the DFA route, where the check sits in `rx_search`
above the tables, the cost model reproduces every cell within a factor of
1.0-2.0.

**Rule:** emit the pre-check in the ENTRY wrappers (`<prefix>_search`,
`_search_in`, `_search_deep`) rather than in `<prefix>_search_run`, with
an acceptance criterion a gate can check: **`rx_search_run`'s compiled
bytes must be identical between the `-freq-byte` and `-fno-req-byte`
builds of the same pattern.** That is a byte-identity assertion over one
function, in the shape the tree's four `.c` identity gates already use.

### Through the four lenses (memory `pcrec-design-evaluation-lenses`)

- **Specific vs general.** All three are general: none names a pattern,
  a bench cell or a byte. G1 is a comparison between two densities the
  tree already computes; G2 is one predicate two emitters already have;
  G3 is where text is written, not what it says.
- **Core vs derived.** Core. G2 restores an invariant the prefilter
  already obeys; G1 states the "extends, not parallels" claim the
  mechanism's own header makes; G3 is the emitted-text discipline
  (`coding_guide.md` §3) applied to a new site.
- **Applicable vs assumption-changing.** Applicable. No engine, rung,
  stamp or ABI assumption moves; G1/G2 change WHETHER text is emitted
  (already an axis, `-fno-req-byte`), G3 changes WHERE. G3 is an
  emitted-scaffolding change, so it IS an `abi` bump and identity re-pin
  in the same change (D76/D94).
- **Fits the architecture vs needs a refactor.** Fits. G1 and G2 are
  predicates in `pcrec_emit_req_byte_check`'s two DFA call sites and the
  VM's one; G3 moves three emitted lines up one call level. No new pass,
  no new field, no second mechanism.

### As a cycle-2 plan row

```
- [OPT-PRECHECK-ADMIT] STATE:not-started (SIZE S-M) (PROPOSED 2026-09-23 by
  [OPTLOOP.1] ledger reading, docs/dev/optloop/cycle1_ledger_reading.md §6)
  — ADMIT AND PLACE THE PRE-CHECKS BY COST, not unconditionally. Three
  predicates on one emitted construct: (G1) decline the necessary-byte
  pre-check where the artifact already emits a candidate-start memchr for a
  byte at least as rare (pcrec_byte_freq_ppm, src/opt/prefix_k.c:91);
  (G2) decline it where the candidate-start set is a single position
  (start_max a literal 0; RX_VM_START "anchored"/"gstart") — the rule
  emit_dfa.c:2999 already applies to the prefilter — and return 0 with no
  check at all where the end-window clamp and the start bound intersect
  empty; (G3) emit the VM's check in the three entry wrappers, not in
  <prefix>_search_run, so the function carrying the attempt loop compiles
  identically to the -fno-req-byte build. Rides the existing -fno-req-byte
  axis (no new bit); G3 is an abi event with the D94 grep ritual. LANDING
  BAR — improve: (winpath-near-miss, thr), (email-nested-plus, thr),
  (uuid-near-miss, thr+srch), (ipv4-near-miss, thr+srch),
  (wild-codegrammar-json-array-begin, thr), (nested-comment-rec, thr).
  Do not regress: the five [OPT-REQBYTE] target rows, (floor-byte, thr+srch).
```

---

## 7. RECOMMENDED DISPOSITIONS — Frank rules default-on vs `--tune`

| mechanism | recommendation | the number that decides it |
|---|---|---|
| **[OPT-ANCHOR-VM]** | **DEFAULT-ON, as shipped** | 13 of 13 target rows improve (−9.36% to −99.9986%); zero attributable regressions outside the null band. |
| **[OPT-ENDWIN]** | **DEFAULT-ON, as shipped** | 4 of 4 target rows improve ≥99.968%; its own emitted code is three arithmetic operations, and isolating it with `-fno-req-byte` leaves nothing that can cost a nanosecond. |
| **[OPT-REQBYTE]** | **DEFAULT-ON WITH THE ADMISSION FIX** ([OPT-PRECHECK-ADMIT] G1+G2 first, G3 with batch 3) | Targets collapse 98.20-99.885% — a `--tune` position would forfeit the largest win the loop has produced. Against that, 29 regressing cells come from ONE declinable predicate and 4 more from a duplicated pass; the two named misses (+1.19%/+1.21%) are inside a null band measured at +8.46%. |

A `--tune` position is the wrong instrument for [OPT-REQBYTE]: its losses
are not a size/speed trade (D119's second axis) but an admission defect
with a measured population of 29 cells and a one-predicate fix. If Frank
prefers to ship before the fix, G2 alone is a few lines and removes 29 of
the 33 attributable regressing cells.

**Size axis** (D119 rule 4's second axis): the pre-check costs +200 to
+334 emitted bytes per artifact on the seven patterns measured here
(`nested-comment-rec` 23,614 → 23,865; `floor-byte` 11,706 → 11,906). No
`--tune` consequence.

---

## 8. OWED LINUX MEASUREMENTS — ready to append to the bench inbox

```
## I-91 (2026-09-23, [OPTLOOP.1] ledger reading) — the executor blocks that
   discriminate the batch-1 regressions

All blocks: ubuntubudu, quiet box, the bench's own build shape
($CC -O2 -fPIC on the emitted .c). BEFORE = pcrec 25b1984f, AFTER = pcrec
8d716693. Patterns are bench/capability/patterns/<name>.rx; subjects are
bench/capability/throughput/t-{64k,256k,1m}.bin. Every timing block is
5 trials, median, interleaved A/B/A/B.

BLOCK A — the axis isolation (timing; answers §3 and §2.2 at once)
  For each of {router-prefix-order (auto, --no-captures),
  uuid-near-miss (auto), ipv4-near-miss (auto),
  wild-codegrammar-json-array-begin (auto)}: build FOUR artifacts at the
  AFTER pin — default, -fno-req-byte, -fno-end-window,
  "-fno-req-byte -fno-end-window" — and time the throughput find-all loop.
  EXPECT: -fno-req-byte recovers the BEFORE number on all four;
  -fno-end-window leaves uuid/ipv4 WORSE than default (the clamp is what
  keeps the memchr window at 37/16 bytes); router's -fno-req-byte number
  is within its IQR of 393,757 ns.

BLOCK B — the null-control band (no new runs needed if the AFTER records
  are kept; otherwise 5 trials each)
  Re-report the per-cell Δ% for the 16 program-identical cells named in
  §1, and ALSO their improving siblings (the ledger lists regressions
  only, so the band is currently one-sided). EXPECT: a symmetric band.
  ASK: carry a NULL-CONTROL BAND in future capability reports, computed
  from the program-identical population, and state D119's bar as
  |Δ| > max(IQR, null band).

BLOCK C — the VM placement mechanism (NO clock; disassembly only)
  For {nested-comment-rec, float-literal-bound (--engine=vm),
  file-ext-order (--engine=vm), wild-secrets-github-pat (--engine=vm)},
  both pins, gcc-15.2 -O2:
    (i)   nm -g <obj> | grep rx_search_run      -> is there a .part.0?
    (ii)  objdump -d, function rx_search_run    -> does it CALL
          rx_match_anchored, or is the body inlined? instruction count?
    (iii) frame size and any __stack_chk in rx_search_run (CC-DIFF STEP 0)
    (iv)  byte offset and 64-byte alignment of the top of the hot loop
  EXPECT (from arm64/gcc-16, which must be replicated or refuted):
  .part.0 present at 25b1984f and ABSENT at 8d716693 on the first three;
  rx_match_anchored out of line in both; its own size unchanged.

BLOCK D — the placement hand-twin (timing; this is also the FIX's
  acceptance test)
  nested-comment-rec, AFTER pin, four builds of the SAME emitted C:
    (a) as-is
    (b) the three pre-check lines DELETED by hand
    (c) the three pre-check lines MOVED from rx_search_run into
        rx_search / rx_search_in / rx_search_deep (the proposed G3)
    (d) as-is, compiled with -fno-partial-inlining
  EXPECT: (b) reproduces the BEFORE median 7,798,115 ns within its IQR —
  if it does NOT, the pre-check is not the cause at all and §4.1 is wrong.
  (c) is the fix: EXPECT it within IQR of (b). (d) separates the
  partial-inlining route from plain layout.

BLOCK E — instructions vs cycles (perf is unavailable at
  perf_event_paranoid=4; run only if that is lifted)
  perf stat -e instructions,cycles,stalled-cycles-frontend,branch-misses
  on nested-comment-rec builds (a) and (b) of block D. EXPECT: instruction
  counts within 0.1% and cycles differing by ~19% => a front-end/placement
  effect, not added work.
```

---

## 9. Reconciliation against O-48 (2026-09-23, lane g3rec)

O-48 (`pcrec-bench/docs/dev/outbox_to_pcrec.md`, [B78], full transcript
`pcrec-bench/docs/dev/lanes/b78blocks_report.md`) is the bench's answer to
§8's I-91 block, forwarded as inbox item I-93, executed on ubuntubudu
(gcc 15.2.0, x86_64) — the box that measures the after-ledger this whole
file reads. Raw transcripts archived at
`docs/dev/optloop/runs/2026-09-23-i93-8d716693/` (README there names what
was and was not archived, and why).

### (A) — EXPECT directions vs the instrument gap

Every direction held: `-fno-req-byte` reads faster than default on all
four Block A patterns (−8.58% to −25.29%); `-fno-end-window` leaves
`uuid-near-miss`/`ipv4-near-miss` WORSE than default (+14.29%, +4.76%),
consistent with §4.2's arithmetic above. **The ABSOLUTE recovery clauses
are unverifiable on this instrument**: every `-fno-req-byte` median reads
**2×-10× the cited BEFORE value** (O-48 Block A's own stated gap; e.g.
router 793,050 ns measured vs. 393,757-393,998 ns cited, uuid 190 ns vs.
19.9-20.4 ns) — the `findall.c` hand-rolled driver (I-89 §0.4) reads
systematically higher than the bench's own committed `store` numbers, on
every cell, trivial and real-match alike (b78blocks_report.md §0 item 3).
Direction is trustworthy here; absolute magnitude is not.

### (B) — the null band is now two-sided, and the bar's numbers stand

`docs/dev/optloop/runs/2026-09-23-i93-8d716693/blockB_output_twosided.txt`.
120 cells (15 patterns × 2 regimes × 4 testees): **min −5.7393%, max
+8.4605%, median −0.0806%, mean −0.4488%; 41 regressing / 79 improving.**
This §1's own reading was already one-sided in the direction that matters
(regressions) and cites the identical worst cell to four significant
figures — `phone-palindrome-6`/thr/`auto-caps`, +8.4605% here against
+8.46% there — so **the reading's own bar, `|Δ| > max(IQR, null band)`,
is UNCHANGED for every regression verdict already drawn** (§1's +8.46%
ceiling and O-48's +8.4605% ceiling are the same measurement read twice).
What is new is the OTHER side: an artifact whose program did not move can
also read up to **−5.74%** "faster" between two windows a day apart, so a
claimed IMPROVEMENT under roughly that magnitude is equally inside the
band and not, on its own, evidence of a real speedup. No verdict in §2-§5
turns on an improvement smaller than 5.74% (every named target row
improves by double digits or more), so this widens the bar's definition
without moving any of this file's own conclusions.

**The 15-vs-16 pattern-identity population differs by exactly one
pattern**, and the two identity criteria differ in KIND, not just count.
Ours (§1, `docs/dev/optloop/b1ledger/artifact_identity.tsv`) is a
near-full **artifact TEXT diff** — the two emitted `.c`/`.h` files
compared line by line, ignoring only the generated-by comment, the three
new `#define`s, `#include <string.h>`, and the `.abi` integer. Theirs
(O-48 Block B) is a **record STAMP-EQUALITY test** — no compiled-object
diff at all, since the committed JSONL record carries no emitted text or
hash of it, so identity is decided by comparing the record's own
`engine_metadata` KEYS (excluding `abi`/`emit_bytes`/`emit_code_bytes`,
requiring the three new stamps read their neutral value). Diffing our
16-pattern list (§1's TSV) against O-48's named 15 finds the populations
agree on 15 of 16; the one pattern in ours and not in theirs is
**`wild-waf-crs-942360-concat-sqli`**. Per O-48's own discipline
("stated as fact, not chased further per I-57 terms") this lane did not
root-cause the single-pattern gap beyond confirming it is real and
isolated to one row — a metadata-key comparison and a source-text
comparison are different instruments and are not guaranteed to agree on
every row even when they agree on 15 of 16.

### (C) — G3 PLACEMENT IS REFUTED ON x86_64

`docs/dev/optloop/runs/2026-09-23-i93-8d716693/blockC_disasm_search_run.txt`.
`nm -g | grep rx_search_run` on gcc-15.2/x86_64 finds **no `.part.0`
symbol at either pin, on any of the three patterns that have a
`rx_search_run` symbol at all** — `nested-comment-rec`, `float-literal-
bound`, `file-ext-order`. The arm64/gcc-16 reading §4.1 hypothesis 1
measured (24 of 62 forced-VM artifacts lose the partial-inlining split at
the AFTER pin) **does not transfer to the box that measures the ledger
this file reads.** The bench's own committed `capability@0.1` records are
built on `gcc-15.2.0`/Ryzen — the box O-48 ran on IS the box the ledger's
numbers come from, so this is not a cross-architecture caveat on a
side finding; it is a refutation of the mechanism on the record's own
compiler.

**`nested-comment-rec`'s +18.8% to +25.0% regression (§4.1) is therefore
UNATTRIBUTED as of now.** Block C's own disassembly tests hypothesis 1's
sibling, hypothesis 2 ("An x86_64/gcc-15.2-specific inline decision that
reaches the per-attempt path", [CC-DIFF] STEP 0's frame/canary mechanism,
explicitly named in §4.1 as "why §8 block C exists"), and **does not
confirm it either**: `rx_match_anchored` is called out-of-line by
`rx_search_run` at BOTH pins (it was never inlined, so it cannot "stop"
being inlined), `__stack_chk_fail` is present at BOTH pins (not an
AFTER-only canary addition), and the total stack footprint is a FLAT
104 B at both pins on all three patterns — none of hypothesis 2's two
named preconditions (an inlining state change, a frame that grows) is
observed. **The second hypothesis §4.1's own list ranks after the now-
refuted first — hypothesis 2 — is therefore the reading's nominal new
lead by elimination, but it survives only in a weakened form**: what
Block C(ii)/(iv) actually finds is the new `memchr` call itself (+9 to
+17 disassembled instructions per pattern) and the hot-loop's absolute
address shifting by exactly 64 bytes (same mod-64 residue before/after,
so alignment CLASS is unchanged, only the address) — closer to §4.1's
hypothesis 3 (pure layout) than to hypothesis 2 as literally stated. No
witness in hand yet distinguishes "the new instructions cost something
real on this box" from "this is more of the between-window noise (B)
already measures at up to 8.46%" — that is exactly what Block D was
chartered to resolve and did not (below).

**`wild-secrets-github-pat` has no `rx_search_run` symbol at either
pin — resolved here, not investigated by O-48 (its own text: "not
investigated further, out of scope").** Compiled in this worktree at
`8d716693`'s successor tip (`--engine=vm --features all --emit-main`,
`build/pcrec -p rx`): the emitted artifact stamps `RX_VM_FRAMELESS 1` and
`RX_VM_ENTRY_SHAPE "inline"`, and at that entry shape `rx_search_run` is
declared `static inline __attribute__((always_inline))`
(`worktrees/g3rec` build, verified in the emitted `.c`). A frameless VM
artifact's entry chain is unconditionally always-inlined into its three
callers under this rung ([CC-DIFF] STEP 1, `ccdiff1_report.md`, gated on
the same `has_push`-derived bool `RX_VM_START`/frameless test) — so
`rx_search_run` has no independent existence to be a linkable symbol at
all, on any compiler, at any pin. This is a **[CC-DIFF] STEP 1 fact,
landed 2026-09-03, wholly unrelated to batch 1 or [OPT-REQBYTE]** — not,
as the brief's own working guess had it, a pinned-start/anchored route
with no search loop (the artifact's own `RX_VM_START` stamp reads
`"unanchored"`; there is a search loop, it is simply folded entirely into
its own three call sites and leaves no symbol of its own).

### (D) — the hand-twin did not resolve; the next measurement, and the second-ranked hypothesis

`docs/dev/optloop/runs/2026-09-23-i93-8d716693/blockD_time_output_iters{5,25}.txt`.
All four EXPECT clauses failed to resolve: every measured Δ (variants
(a)/(b)/(c)/(d) against each other) sits inside the per-variant IQR
(300K-1.5M ns on an 8.4M-9.9M ns median, roughly 3-17%), and variant
(b)'s sign flips between the two internal-iters settings tried (+9.86% at
iters=5, −4.45% at iters=25). O-48's own read matches this file's §4.1
framing exactly: the pre-check's own measured work is ≈25 ns against a
claimed ~1.53M ns delta (a 60,674× ratio), so a probe built to separate
"the partial-inlining split" from "plain layout" is, on this box, asking
a question its own compiler does not structurally raise the way arm64's
does — Block C(i) already confirmed there is no split to separate.

**Ready-to-append executor block (I-98 candidate):**

```
## I-98 (2026-09-23, [OPTLOOP.1] ledger reading §9) — Block D re-run under
   the bench's own driver, and the second-hypothesis discriminator

Motivation: O-48/[B78] Block D's findall.c instrument could not resolve
the nested-comment-rec hand-twin -- every measured delta sat inside the
per-variant IQR (300K-1.5M ns, ~3-17% of an 8.4M-9.9M ns median), and
variant (b)'s sign flipped between the two internal-iters settings tried.
O-48 names its own fix: "it needs either the bench's own driver as the
instrument ... or a subject/iters shape whose delta clears this
pattern's own noise." This block is that re-run, using the SAME four
builds Block D already produced (or rebuilt from the report's verbatim
3-line diff, its own BLOCK D section):
  (a) as-is
  (b) the three pre-check lines deleted by hand
  (c) the three pre-check lines moved to the entry wrappers
      (<prefix>_search / _search_in / _search_deep) -- the shape
      [OPT-PRECHECK-ADMIT] G3 proposes
  (d) as-is, -fno-partial-inlining
Method: time all four with the bench's OWN capability@0.1 shim/driver and
record protocol (store/records/..., large-subject-throughput regime, the
same 3 subjects, the store's own trial count and X13 hygiene gate) --
NOT findall.c. Answer-check matches=[0,0,0] on all three subjects, all
four variants, before timing (as O-48 already did).

EXPECT: if (b) reads below (a) by a delta that clears the null-control
band (O-48 Block B: up to +8.46%/-5.74% BETWEEN interleaved windows;
tighter within one run of this block's own 5 interleaved trials), the
pre-check costs something real on this box and hypothesis 2 -- WEAKENED,
per this file's own §9(C): not an inlining-state or frame-size change
(Block C already measured neither moves), but the added instructions
and the hot-loop's shifted address -- is the surviving candidate; go on
to ask whether (c) is within the band of (b), which is G3's literal
acceptance test. If (b) does NOT clear the band even under the store's
own driver, hypothesis 2 is refuted too, nested-comment-rec's regression
has no confirmed x86_64 mechanism, and G3's placement rule should be kept
only as the byte-identity DISCIPLINE its own §6 acceptance criterion
states (`rx_search_run` compiled identical between -freq-byte and
-fno-req-byte builds) -- a correctness/hygiene rule, not a claimed
performance win, absent a new witness.
```

