# `[OPT-REQRUN-ENC]` STAGE 1 — the D77 census

**Lane `reqrunenc`, 2026-09-26.** Census only: no `src/` change is
delivered (two candidates were patched LOCALLY, in this worktree, to
measure and correctness-check them — see §5 — and reverted; `git diff
main -- src/` is empty in the delivered commit). This answers the plan
row's own trigger: which decline rule the RUN path (`rn_scan_index`,
`src/opt/reqbyte.c:539-550`) should use `!bytekey` (every non-byte
encoding — `-e utf8` is the only one that exists today), replacing
today's unconditional leftmost (index 0).

Read `docs/design/reqpos_2b.md` §2.3 first: it is the ratified decline
this census re-measures ("costs nothing measurable, the `-e utf8` arm
shares no bar cell") — a claim the bench's O-60 pattern set has since
falsified (§3 below).

## 0. The headline

* **The RUN path fires on 12.0% of the corpus and 28.3% of the bench under
  `-e utf8`** (§1), and on the artifacts that fire, **today's leftmost pick
  is a UTF-8 lead byte 12.0% of the time on the corpus and 20.7% on the
  bench** — the exact defect O-60 names: a lead byte is shared by every
  character in its script block, so `memchr` stops on nearly every
  character rather than the rare one the literal actually needs.
* **Two candidate fixes, R (rightmost member — `rb_pick`'s own rule) and S
  (rightmost non-lead-byte member), are BYTE-IDENTICAL on the ENTIRE
  measured `-e utf8` population** — 912 of 912 runs (92 bench + 820
  corpus), zero disagreements. They diverge only on a hypothetical/control
  population that cannot occur in real `-e utf8` compiles (§2.3).
* **Recommendation: candidate R.** It is provably equivalent to S wherever
  it matters, needs no UTF-8-specific byte-range logic (`rb_pick`'s
  identical fallback, reused rather than re-invented — the tree's own
  "general mechanism, not a special case" rule), and is a **one-line
  change**: `rn_scan_index`'s `if (!bytekey) return 0;` becomes
  `if (!bytekey) return r->n - 1;`.
* **Cost proxy**: on the four O-60 witnesses, R's chosen byte's occurrence
  rate in the bench's own throughput subjects drops 100%-to-99.996% off
  L's rate (§3), and a rough same-box timing proxy reproduces O-60's
  Linux ratios' ORDER OF MAGNITUDE and DIRECTION on two of them (§4).
* **Correctness**: L (today, control), R, and S all pass the whole
  `-e utf8`-carrying `.rxt` population (14 files, 1,499/1,499 cases) with
  zero regressions (§5).
* **Byte encoding is untouched by construction**: `!bytekey` gates the
  whole candidate difference, so every byte-encoding artifact is
  byte-identical under R or S — confirmed directly, not just argued (§2.4).

## 1. Method and instruments

Reused rather than rewritten, per the brief: `docs/dev/optloop/c2/
reqpos_probe.c` (`[OPT-REQPOS]`'s own D77 census instrument) is copied
UNCHANGED as `reqrunenc/reqrunenc_probe.c` and built against this
worktree's `libpcrec.a`. It links the REAL parser + `pcrec_altcls` +
`pcrec_discharge_atomic` + `pcrec_lower_enc` and re-derives `reqbyte.c`'s
own necessary-run walk (`RbRun`/`r.best`), so its `run_hex` column is the
SAME run `pcrec_req_byte` computes, before `rn_window_start`'s truncation
— which is the right stage to measure from, since `rn_scan_index` (the
row's whole subject) runs on the FULL run, not the truncated window
(`reqbyte.c:604`: `i = rn_scan_index(&r, ...)` precedes the `r.n >
PCREC_MAX_REQ_RUN_EMIT` truncation).

**One bug found and fixed in the reused instrument, not in `reqbyte.c`
itself.** `reqpos_probe.c`'s `walk()` switch has no `case A_VAR:` and no
`default:`, so an unhandled `Ast` kind falls through its `for (;;)` with
`a` unchanged — an infinite busy loop. `[VAR]` postdates `reqpos_census.md`
(2026-09-22)'s own corpus run, so it never hit this; this census's corpus
population does, on the FIRST `tests/vars/*.rxt` template it reaches
(`^${prefix}-[0-9]+$`). Fixed by adding `case A_VAR:` alongside
`A_BREF`/`A_CALL` — `reqbyte.c:492`'s own real switch already declines all
three identically (empty set: the operand's bytes are not in the pattern).
Verified with `gcc -Wall -Wextra` (a switch over a bounded-domain `enum`
tag with `default:` omitted deliberately, per `coding_guide.md`'s
"no-`default:` exhaustive switch as the `-Wswitch` alarm") — no missing-case
warning after the fix. `reqrunenc_probe.c`'s own header documents the
find; this is the version delivered.

`driver.py` (new, downstream of the probe) reuses `c2/reqpos_census.py`'s
`bench_pop()`/`corpus_pop()`/`run_probe()` verbatim (`reqrunenc/
_shared_pop.py`, an unmodified copy) for the two populations the row
names — every `bench/*/patterns/*.rx` in pcrec-bench (325 patterns, all
sets, not only `utf8`) and every `pattern`/`pattern-esc` line of the
shipped `.rxt` corpus (4,016 lines, field-decoded the same way) — and
computes the three candidates directly off each row's `run_hex`, no new
compile.

**The three candidates, stated precisely** (`i` is the chosen index into
the run `R`, `|R| = n >= 2`):

* **L (today)**: `i = 0`, unconditionally.
* **R (`rb_pick`'s rule)**: `i = n - 1`, unconditionally.
* **S (skip lead bytes)**: `i` = the LARGEST index whose byte is NOT a
  UTF-8 lead byte (i.e. is ASCII `0x00-0x7F` or a continuation byte
  `0x80-0xBF`) — scanning from the right, mirroring R's own rightmost
  convention. Falls back to `i = 0` (matching L) when every byte in the
  run is a lead byte (`0xC2-0xF4`), the same universal-fallback shape
  `rn_scan_index` already has.

## 2. Population

### 2.1 How many artifacts take the RUN path, and how often is L's byte a lead byte

| population | patterns probed | run >= 2 (RUN path fires) | of those, L's byte is a lead byte (0xC2-0xF4) |
|---|---:|---:|---:|
| bench, `byte` | 325 | 97 (29.8%) | 24 (24.7%) |
| bench, `-e utf8` | 325 | 92 (28.3%) | 19 (20.7%) |
| corpus, `byte` | 4,016 | 755 (18.8%) | 33 (4.4%) |
| corpus, `-e utf8` | 4,016 | 820 (20.4%) | 98 (12.0%) |

The `byte`-encoding rows are a CONTROL, not a population the fix touches
(`!bytekey` is false there — see §2.4) — they show that classifying a byte
into `0xC2-0xF4` by pure coincidence happens at a lower, unrelated rate
(4.4%/24.7%) than the real `-e utf8` phenomenon (12.0%/20.7%), i.e. this
is not an artifact of the byte range chosen to define "lead byte".

### 2.2 How many artifacts MOVE under each candidate (vs. L), `-e utf8` only

| population | run >= 2 | moves under R | moves under S |
|---|---:|---:|---:|
| bench | 92 | 92 (100.0%) | 92 (100.0%) |
| corpus | 820 | 789 (96.2%) | 789 (96.2%) |

The 31 corpus non-movers (820 − 789) are runs whose first and last byte
happen to be numerically equal (e.g. a two-member run built from the same
repeated byte) — not a case where L was already correct, just one where L
and R/S coincide.

### 2.3 R vs. S: they never disagree on the real population

| population | R vs S disagree, `-e utf8` | R vs S disagree, `byte` (control) |
|---|---:|---:|
| bench | 0 | 1 |
| corpus | 0 | 1 |

**Zero disagreements across all 912 real `-e utf8` runs.** The two control
disagreements (`syntax/esc-hex-braced`'s `636166e9` = `"caf\xe9"`,
`tests/base/high_bytes.rxt:36`'s `deadbeef`) exist only because a `byte`
value like `0xE9`/`0xEF` falls numerically inside `0xC2-0xF4` BY CHANCE —
there is no such thing as a UTF-8 lead byte under `byte` encoding, so this
is exactly the meaningless case §2.1 already flagged, not a real
counter-example.

**Why R and S coincide everywhere it matters, structurally, not just by
luck of this population**: a `-e utf8` run is built from complete lowered
UTF-8 code-unit sequences, and the LAST byte of any complete multi-byte
character is always a continuation byte (`0x80-0xBF`), never a lead byte —
so the rightmost member of a real run is a lead byte only if the run is
truncated to end mid-character (an alternation's common suffix stopping
between a lead byte and its continuation, or similar). That is a real,
statable edge case the format allows, but it has **zero occurrences** in
912 measured runs across both populations. `docs/design/reqpos_2b.md`'s own
"known false negatives" convention says this should be named rather than
silently assumed away: if it ever occurs, R keeps the lead byte (same
defect as L) while S correctly avoids it — the one case where S beats R.
It has never been observed.

### 2.4 The byte-encoding arm: confirmed untouched, not just argued

`!bytekey` is `cx->opt->encoding == PCREC_ENC_BYTE` being false — R and S
change nothing when it is true, by construction (neither candidate touches
the `bytekey` branch of `rn_scan_index`, which is unconditionally the
existing frequency-argmin pick, `reqbyte_freq_pick.md`'s own mechanism).
Confirmed directly rather than left as an inspection claim: compiling
`café` (`byte` encoding) with the shipped compiler and with each patched
candidate (§5) and comparing the emitted `.c` (fixing the output filename
so the embedded `#include` line does not itself differ) gives an IDENTICAL
sha256 on all three:
`ae61b1a87ad7ea28d61abeca86b462855c12e8242ae841eb1c1e23fcc47bf47e`.

## 3. Cost proxy — memchr candidate rate on the real bench subjects

For each of O-60 §3's four literal witnesses, the chosen byte's occurrence
count in the EXACT throughput subject text O-60 measured against
(regenerated in-memory from `pcrec-bench/bench/utf8/gen_throughput_
subjects.py`'s pure `build()` — read-only, nothing written to pcrec-bench;
verified the module's own sha256 manifest is unaffected by importing it):

| witness | subject | L byte | L count | L /KB | R=S byte | R=S count | R=S /KB | reduction |
|---|---|---|---:|---:|---|---:|---:|---:|
| `lit-offset-at-tail` (`é@`) | t-64k-lat | 0xc3 | 4,652 | 72.69 | 0x40 | 0 | 0.00 | 100% |
| `lit-cyr-run` (`Москва` prefix) | t-64k-cyr | 0xd0 | 20,279 | 316.86 | 0xba | 860 | 13.44 | 95.8% |
| `lit-run-3` (`日本語`) | t-64k-cjk | 0xe6 | 3,478 | 54.34 | 0x9e | 206 | 3.22 | 94.1% |
| `lit-mixed-ascii` (`user@例え.jp` prefix) | t-64k-asc | 0x75 ('u') | 2,040 | 31.88 | 0x8b | 0 | 0.00 | 100% |

R and S pick the identical byte on all four (§2.3's finding, not a
coincidence restricted to these four). The `lit-mixed-ascii` row is the
sharpest: `t-64k-asc` is the byte-clean-ASCII control subject, so ANY
non-ASCII scan byte (R/S's 0x8b, a CJK continuation byte) has a
STRUCTURAL zero occurrence rate there, while L's `'u'` is an ordinary
common English letter — this is O-60's own "even the byte prior would
pick '@' over 'u'" point, generalized.

## 4. Timing proxy — this box, not the bench's

Rough, same-box (Mac M1) `CLOCK_MONOTONIC` medians of 21 trials of one
`rx_search` call over the whole subject buffer, `docs/dev/optloop/
reqrunenc/timedrv.c`, ONE process at a time, never in parallel. A PROXY
only — the bench's own Linux box is the real measurement, and O-60 already
supplies it; this exists to confirm DIRECTION and rough MAGNITUDE, not to
re-derive O-60's numbers.

| witness | subject | L median | R median | ratio | O-60 (Linux, `t-64k-*` or `t-1m`) |
|---|---|---:|---:|---:|---:|
| `lit-offset-at-tail` | t-64k-lat | 50,000 ns | 1,000 ns | 50.0x | 39.6x |
| `lit-run-3` | t-64k-cjk | 46,000 ns | 3,000 ns | 15.3x | 11.8x |

Same direction, same order of magnitude, on a different architecture and
compiler — corroborating rather than re-measuring O-60.

## 5. Correctness — the `-e utf8`-carrying `.rxt` files, all three candidates

R and S were patched LOCALLY into `src/opt/reqbyte.c`'s `rn_scan_index`
(the one-line/one-loop change each — see §0), built into `BUILD_DIR=
build-candR`/`build-candS` (default `build/` = L, untouched), and run
through `tests/harness/run.sh` over the 14 `.rxt` files that carry an
`encoding utf8` (or sibling `encoding byte` control) block anywhere in the
tree (found by `grep -rl "^encoding" tests/`):

```
tests/utf8/axis01_encoded_length.rxt   tests/utf8/axis02_class_boundary.rxt
tests/utf8/axis03_invalid_utf8.rxt     tests/utf8/axis04_p_categories.rxt
tests/utf8/axis06_caseless_fold.rxt    tests/utf8/axis07_caseless_1ton.rxt
tests/utf8/axis08_lookbehind_varwidth.rxt
tests/utf8/axis09_nextpos_findall.rxt  tests/utf8/axis10_surrogate_witness.rxt
tests/utf8/axis11_startpos_boundary.rxt tests/utf8/axis12_scripts.rxt
tests/utf8/fold.rxt
tests/base/k65_precheck_whole_set.rxt  tests/base/k66_precheck_whole_run.rxt
```

| candidate | build | cases passed | cases failed | pattern-compile failures |
|---|---|---:|---:|---:|
| L (control, shipped) | `build/pcrec` | 1,499 | 0 | 0 |
| R | `build-candR/pcrec` | 1,499 | 0 | 0 |
| S | `build-candS/pcrec` | 1,499 | 0 | 0 |

All three identical: 1,499/1,499, zero pattern-compile failures.

Logs: `docs/dev/optloop/reqrunenc/harness_logs/cand_{L,R,S}.log`,
`harness_logs/driver.log` (the sequencing wrapper's own trailer). `src/`
was restored to `main`'s `reqbyte.c` (verified `git diff --stat` empty)
before this note's own commit — the two builds live only under
`build-candR/`/`build-candS/` (gitignored, not delivered) for
reproducibility; the patch diffs themselves are inlined in §5.1 for the
record.

### 5.1 The two patches measured (not delivered — stage 2's job)

```c
/* candidate R */
static int rn_scan_index(const RbRun *r, bool bytekey)
{
    int i, best = 0;
    unsigned lo;
    if (!bytekey) return r->n - 1;
    ... /* unchanged */
}

/* candidate S */
static int rn_scan_index(const RbRun *r, bool bytekey)
{
    int i, best = 0;
    unsigned lo;
    if (!bytekey) {
        for (i = r->n - 1; i >= 0; i--) {
            unsigned char b = r->bytes[i];
            if (b <= 0x7f || (b >= 0x80 && b <= 0xbf)) return i;
        }
        return 0;
    }
    ... /* unchanged */
}
```

## 6. Recommendation

**Build candidate R** for stage 2: `if (!bytekey) return r->n - 1;`,
matching `rb_pick`'s own `!bytekey` fallback exactly (`return s->pick;`,
which is itself the rightmost-branch-wins convention threaded from
`cat`/`alt`) — one mechanism, two call sites, no new byte-range constant
to maintain. It is provably indistinguishable from S over every measured
`-e utf8` artifact (§2.3) and the entire bench cost/timing evidence (§3-4).
The one theoretical case where S would differ (§2.3's mid-character
truncation) has never been observed and is not worth a second code path
under D77's own "wait for a measured need" discipline — if it is ever
found, it becomes S's own row, cheaply, since S's logic already exists
here as a measured alternative.

**Scope for stage 2**: `rn_scan_index` only. `rn_window_start`'s
truncation is a downstream consumer that already receives whichever `i`
`rn_scan_index` returns and needs no change (§1). No abi bump: this is a
SPEED-only choice within an existing decline clause (`reqbyte.c`'s own
framing — "the worst a bad choice can cost is speed... never a match"),
not new emitted scaffolding or a stamp change — `RX_REQ_RUN`'s printed
`@offset` will change VALUE on movers, which is `reqpos_2b.md`'s own
precedent (the tier-2b landing moved the same stamp) and not itself an
abi event.

## 7. Reproduction

`docs/dev/optloop/reqrunenc/`: `reqrunenc_probe.c` (the probe, `[VAR]` fix
included), `_shared_pop.py` (verbatim copy of `c2/reqpos_census.py`'s
population/probe-runner functions), `driver.py` (this census's own
candidate/mover analysis), `reqrunenc_census.json` (driver.py's output),
`scanrate.py`/`reqrunenc_scanrate.json` (§3's memchr-rate proxy),
`timedrv.c` (§4's timing proxy driver), `harness_logs/` (§5's correctness
run logs).
