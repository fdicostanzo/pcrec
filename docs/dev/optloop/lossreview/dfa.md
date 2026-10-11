# [LOSS-REVIEW] phase 1, the DFA-route share (lane lrdfa, 2026-10-11)

Charter: `../lossreview_charter.md`. Population: every trailing cell of
`../gapreport_2026-10-11.md` whose shipped-default artifact is `RX_ENGINE
"dfa"`, utf8 and litrun excluded (lane lrmisc), VM/hybrid excluded (lane lrvm).
SIMD-only, rust-only and SCAN-SIMD cells are LISTED (§5), not attributed.

**Evidence tier: load-insensitive only.** The box was busy (a heavy chain plus a
kit slot), so no clock was read. Every ns figure is the bench's own (b8337c33,
set-grain sum over a regime's subjects, peers per `--peer-group`; drift bounds
are in the gap report's judgement). Everything else was counted on this lane's
worktree at main f2fcffb4. Main's `src/` equals e878687b, where the gap report
compiled its stamps. Main differs from the measured pin b8337c33 only by the
flag-accessor refactor and kit SIMD-layer changes, so the SIMD-off artifact is
unchanged.

- **Stamps.** `--features all`, the bench's pcrec-auto flags, read off the
  emitted C, `--emit-facts` and `--emit-ir`.
- **Per-phase subject loads.** These come from the walk_survey instrument
  (`studies/walk_survey/`, `wsdrv5.c`) at main.
- **Counted find-all work.** `dfa/facount.c` counts `rx_search` calls,
  matches, and `memchr` calls and bytes via `--wrap`.
- **Skip-block counts.** `dfa/twins/mk_count.py` + `stepcount.c` count
  skip-block entries, bytes skipped and forward DFA steps.

The counts run over the bench's own subjects, regenerated read-only from a
`git archive` copy of pcrec-bench at d359564f. All 31 throughput and 278 short
subjects match their committed manifests' sha256. All 290 throughput (pattern,
subject) match counts equal the bench's libpcre2-derived `expectations.tsv`.

## 0. Answers first

1. **The DFA route trails on 55 cells / 50 patterns** (vs jit, a scalar engine,
   or rust alone). Of those, **29 attributable cells (28 patterns) carry 51.2 ms
   of bench loss**, and 26 are listed (SCAN-SIMD 17, rust-only 9). On every
   trailing DFA cell where jit is the winner, pcre2-interp is 1.3-25x SLOWER
   than pcrec. So jit wins on code generation
   or SIMD, never on an algorithm pcrec lacks (D119). The algorithmic losses
   (where a SCALAR engine wins) are exactly four cells, all vs re2:
   concat-sqli, hex8-bounded, dbnames and json-constant. They are 42.1 of the
   51.2 ms.
2. **Top three causes by total loss, each with a fix-existing candidate:**

   | rank | cause | cells | ns lost (bench) | fix-existing candidate |
   |---|---|---|---|---|
   | 1 | **ATTEMPT-SHAPE**: one `^` arm sends concat-sqli to `ENG_ATTEMPT`, which re-walks from every start (3.145 loads per subject byte) | 1 | 28,869,442 (re2 x4.80) | **`[OPT-ATTEMPT-SPLIT]`** (ratified 2026-09-22, unbuilt). The exact twin is built and answer-identical. |
   | 2 | **DENSE-SKIP**: the start-skip block is entered every 2-10 bytes on a dense start set. Each entry pays a skip loop, a seed reload and a mispredicted exit. re2 steps every byte at ~1.6 ns/B with no skip. | 3 | 13,232,148 (re2 x1.14-x1.94) | **`[START-DENSE]`**, widened from K90/K91's hat-only disarm to every table-skip NEXT row: a density-priced choice between the skip and plain stepping. The twins are `plainloop` and the shipped `-fno-start-set` arm. |
   | 3 | **HIT-RESTART**: per-hit `memchr` return and restart at a 3-4% scan byte under dense find-all. lit-cat does 42,663 calls for 7,628 matches, about 10-17 ns per call. jit's SIMD first-unit search is inline. | 14 | 4,422,139 (jit x1.25-x2.75) | **memfn R4d**, the SWAR fused pair-filter scan+verify. Its trigger is already MET at SIMD-off (R-1: 1.95x on union-select, 2.7x on mod-i). It should be routed to the ofsskip FUNC's BODY as well as the pre-check. |

   Next: RUN-PICK 1.76 ms, PAIR-SKIP 1.36 ms, K101 0.92 ms, RANGE-SKIP 0.44 ms,
   REV-PASS 0.13 ms, ATTEMPT-STEP 0.04 ms (§2).
3. **19 answer-checked twin artifacts** (§4) are listed with their exact build,
   check and timing commands.
   - **Composition:** 14 hand twins, 4 shipped compiler arms (`-fno-start-set`
     ×3, `-fno-req-run-fold`) and 1 reconstruction control. Every one gives the
     same spans as its base AND as libpcre2 10.46, on 45-87 subjects each.
   - **Planted control:** a planted twin (the rare stream never searched) is
     caught as DIFF on 6 of 45 subjects.
   - **Timing:** owed, for a quiet slot (`dfa/twins/time_twins.sh`, never run).
4. **Two findings change the obvious fix.**
   - **K101's bounded-stream fix shape does not obviously win on the bench's own
     mod-i cell.** It cuts `memchr` bytes from 5.04 to 1.96 per subject byte, but
     raises `memchr` calls from 53,301 to 88,333 (+66%). R4d is the stronger
     candidate there. The bounded shape stays the off-bench cliff fix.
   - **G2's decline on email-owasp is RIGHT in total and wrong on two subjects.**
     The G2-off twin makes `memchr` read every byte of all 11 subjects (1.000
     per subject byte), against today's attempt reading 0.017. A DEFERRED
     pre-check (test `@` once, only after the attempt has walked 64 bytes alive)
     reads 0.017 with 2 calls. That is a refinement of G2's predicate, not its
     removal.

## 1. Per-cell table

Ns lost = auto-caps minus the best non-SIMD comparator (jit or a scalar
engine). For cells where only rust is ahead, it is rust (listed). Ns are the
bench set-grain sums: per pass over all of a regime's subjects. The bucket
columns are per subject byte, over the throughput subjects. The full TSV is
`dfa/cells.tsv`; the cause rules are `dfa/causes_dfa.tsv`; the generator is
`dfa/rollup.py`.

| cell | reg | tier | ns lost (vs, ratio) | route: scan / prefilter / start / REQ_WHY | measured bucket (per subject byte; find-all calls) | cause |
|---|---|---|---|---|---|---|
| capability/wild-waf-crs-942360-concat-sqli | thr | A | 28,869,442 (re2 x4.8) | attempt / none / attempt-start / none | loads 3.145 (all fwd); calls 11 | ATTEMPT-SHAPE |
| capability/wild-validator-email-owasp | thr | B | 39,731 (jit x7.22) | attempt / none / attempt-start / **one-attempt** | loads 0.017 (fwd): 77,825 B on the two evil subjects, 1-9 B elsewhere | ATTEMPT-STEP |
| capability/hex8-bounded | thr | A | 7,294,385 (re2 x1.94) | unanchored / first-class-bounded / end-minus-width / none | loads 1.243 (fwd 0.843, skip 0.400); skip entries 0.146/B, mean skip **1.75 B**, steps 0.746/B | DENSE-SKIP |
| capability/wild-waf-crs-942140-dbnames | thr | A | 4,905,636 (re2L x1.65) | unanchored / first-class-bounded / reverse-pass / none | loads 1.160 (fwd 0.613, skip 0.547); entries 0.095/B, mean skip 4.75 B, steps 0.548/B | DENSE-SKIP |
| capability/wild-codegrammar-json-constant | thr | A | 1,032,127 (re2 x1.14; rust x9.04) | unanchored / first-class-bounded / reverse-pass / none | loads 1.127 (fwd 0.371, skip 0.756); entries 0.067/B, mean skip 10.4 B, steps 0.311/B | DENSE-SKIP |
| capability/keyword-prefix-order | thr | A | 848,258 (jit x1.59) | unanchored / offset-set / reverse-pass / dominated | loads 1.061; calls 24,541; memchr **164,806** (= every `n`) | HIT-RESTART |
| loglines/stack-frame | thr | A | 832,488 (jit x2.75) | unanchored / offset-set-bounded / reverse-pass / emitted (set-leads `)`) | loads 1.098 (pre 1.068); calls 906; memchr **90,225** (the run gate on `a`) | HIT-RESTART |
| syntax/asr-nwb | thr | A | 551,101 (jit x2.50) | unanchored / offset-set-bounded / end-minus-width / emitted | loads 1.089; calls 2,054; memchr 79,737 | HIT-RESTART |
| syntax/asr-wb | thr | A | 532,978 (jit x2.36) | unanchored / offset-set-bounded / end-minus-width / emitted | loads 1.088; calls 1,862; memchr 81,011 | HIT-RESTART |
| syntax/cls-fold-pair | thr | A | 299,109 (jit x1.68) | unanchored / memchr / end-minus-width / emitted (handoff 0) | loads 1.094; calls 7,631; memchr 50,291 | HIT-RESTART |
| syntax/cls-dot | thr | A | 285,717 (jit x1.64) | unanchored / memchr / end-minus-width / — | loads 1.037; calls 7,631; memchr 42,663 | HIT-RESTART |
| syntax/mod-reset | thr | A | 214,210 (jit x1.29) | unanchored / run-pinned / end-minus-width / — | loads 1.096; calls 8,065; memchr 93,897 | HIT-RESTART |
| syntax/mod-unset | thr | A | 210,837 (jit x1.28) | same | loads 1.096; calls 8,065; memchr 93,897 | HIT-RESTART |
| syntax/mod-x | thr | A | 149,995 (jit x1.29) | unanchored / run-pinned / end-minus-width / dominated | loads 1.089; calls 7,631; memchr 42,663 | HIT-RESTART |
| syntax/esc-hex | thr | A | 149,514 (jit x1.29) | same | same | HIT-RESTART |
| syntax/lit-cat | thr | A | 148,349 (jit x1.29) | same | same | HIT-RESTART |
| syntax/mod-n | thr | A | 141,216 (jit x1.27) | same | same | HIT-RESTART |
| syntax/grp-noncap | thr | A | 42,544 (jit x1.26) | unanchored / offset-set / reverse-pass / — | loads 1.015; calls 1,983; memchr 10,924 | HIT-RESTART |
| loglines/stack-frame | srch | B | 15,823 (jit x1.90) | as thr | (short subjects, not counted) | HIT-RESTART |
| capability/wild-waf-crs-942270-union-select | thr | A | 1,758,450 (jit x9.49; **re2 x1.33**) | unanchored / byte-class / reverse-pass / emitted (run `SELECT`@4, fold) | loads 2.115 (pre 2.115: two streams); calls 11; memchr **134,706** (= every `c`/`C`) | RUN-PICK |
| syntax/alt-nested | thr | A | 756,021 (jit x1.63) | unanchored / byte-class `{c,d}` / end-minus-width / none | loads 1.076 (skip 0.906, fwd 0.171); calls 11,395; no memchr (table walk) | PAIR-SKIP |
| syntax/alt-two | thr | A | 606,753 (jit x1.52) | same | loads 1.078; calls 11,395 | PAIR-SKIP |
| syntax/mod-i | thr | A | 459,074 (jit x1.81) | unanchored / byte-class / end-minus-width / emitted (fold, handoff 0) | loads **5.149** (pre 5.120); memchr 53,301, **5.038 memchr B/B** | K101 |
| syntax/mod-r | thr | A | 457,293 (jit x1.81) | same | same | K101 |
| capability/high-byte-run | thr | A | 257,378 (jit x1.19) | unanchored / byte-class `[\x80-\xff]` / reverse-pass / none | loads 1.000 (skip 1.000), 0 matches | RANGE-SKIP |
| capability/utf8-lead-no-cont | thr | A | 185,627 (jit x1.13) | unanchored / byte-class-bounded `[\xc2-\xdf]` / end-minus-width / none | loads 1.000 (skip), 0 matches | RANGE-SKIP |
| bounded/pw-8-64 | thr | A | 62,985 (jit x1.49) | unanchored / byte-class / reverse-pass / none | loads 2.031 (fwd 1.016, **rev 1.000**); calls 1,669 | REV-PASS |
| bounded/line-80 | thr | A | 43,221 (jit x2.34) | unanchored / byte-class / reverse-pass / none | loads 2.000 (fwd 1.000, **rev 1.000**); calls 10 | REV-PASS |
| bounded/cls-atleast-4096 | thr | A | 28,046 (jit x1.47) | unanchored / byte-class / reverse-pass / none | loads 1.808 (fwd 0.808, **rev 0.808**); calls 8 | REV-PASS |

(`—` = `REQ_WHY none`. Listed cells: §5.)

## 2. Per cause: mechanism, the existing opt meant to cover it, why it did not

### 2.1 ATTEMPT-SHAPE — 28.87 ms, 1 cell (concat-sqli), algorithmic (re2 x4.80; pcrec leads jit x33)

**Mechanism.** One `^` arm, the 5th and last of five top-level arms, routes the
whole pattern to `ENG_ATTEMPT`: `RX_DFA_SCAN "attempt"`, no prefilter, no
table, no edge. An attempt is started at every position and re-walks the
following bytes. The count is **3.145 loads per subject byte**, all forward
(walk_survey `m_gap` = 3.145).

**Existing opt.** `[OPT-ATTEMPT-SPLIT]` (plan.md; ratified 2026-09-22, batch 2
or later, unbuilt) and `[ENG-ABS-CARET]` (not-started). The decline is the
route rule `emit_dfa.c:13-17`, "the slow shape is ^ on only SOME branches". No
predicate fires; the mechanism simply does not exist yet.

**Twin.** `dfa/twins/mk_split.py` + `split_rx.c` is EXACT, not the
arm-deletion upper bound (waf M5.b: x3.51):
- it compiles the four `^`-free arms unanchored (`byte-class-bounded` /
  `reverse-pass`) and the `^` arm as its own anchored attempt;
- the `^` arm is last, so it has the lowest priority, and it can start only
  at 0 (no `(?m)`);
- so the answer is the unanchored match unless that one has none at 0 and the
  `^` arm matches at 0.

The twin is answer-identical to base and libpcre2 on 87 subjects (12 matches).

**After it.** The residual is the split artifact's per-step cost: its first set
contains the word class. That is §2.2's cause, so the two compose.

### 2.2 DENSE-SKIP — 13.23 ms, 3 cells, algorithmic (re2 x1.14-x1.94; jit is behind pcrec on all three)

**Mechanism.** The forward loop enters its start-skip block (`forward_state
== 0 && last_accept == -1`: a table walk over `rx_start_bytes`, then a seed
reload `rx_forward_seed_state[byte_class[s[pos-1]]]`) at every return to state
0. On these start sets the skip is SHORT:

| cell | skip entries per byte | mean skip | forward steps per byte | bench ns/B | re2 ns/B |
|---|---|---|---|---|---|
| hex8-bounded `\b[0-9a-f]{8}\b` | 0.146 | **1.75 B** | 0.746 | 3.224 | 1.666 |
| dbnames | 0.095 | 4.75 B | 0.548 | 2.670 | 1.622 |
| json-constant `\b(?:true\|false\|null)\b` | 0.067 | 10.4 B | 0.311 | 1.841 | 1.614 |

So hex8-bounded pays a loop entry, a seed reload and a data-dependent exit
every ~7 bytes to skip 1.75 of them. re2's lazy DFA steps every byte with no
skip, at ~1.6 ns/B. pcrec's own premultiplied step runs at OPT-3's ~1.3-1.8
ns/step (`opt3_dfa_scan_measurement.md`); pcrec is at 3.2 ns/B. This is
waf_attribution.md §3.4's per-step question, now with counts. That section
named the `plainloop` twin as the discriminator, and it was never timed.

**Existing opt.** The DFA hat (START-SET stage 3, `first-class-bounded`)
admits `T = S ∩ E*` iff T ⊊ E, with NO density term. The pre-hat `byte-class`
/ `byte-class-bounded` skip rows had none either. **K91** (known_issues.md)
already names this regime: the hat loses at d_T 12-31%. Its candidate fix is
"the density-adaptive disarm ... on the unified start table". **`[START-DENSE]`**
(D153; K90+K91+K83 folded, gated on C7, and C7 is done) is that row.

**Why it did not cover these cells.** `[START-DENSE]` is unbuilt. As filed it
is scoped to the hat's disarm, while hex8's skip loop would be just as short
under `-fno-start-set` (that arm is twinned).

**Fix-existing widening.** One density-priced NEXT selection: plain stepping
vs the table skip. It reads the prior density of the skip set, so E[skip] =
1/d − 1 against an entry cost that is MEASURED, never guessed (memory
pcrec-suspect-tuning-constants).

### 2.3 HIT-RESTART — 4.42 ms, 14 cells / 13 patterns, jit-only (interp 3-25x slower than pcrec)

**Mechanism.** In a dense find-all, every hit of the scan byte returns from
`memchr`, is verified, fails, and calls `memchr` again. The scan byte is a
3-4% one:

| cell | scan byte |
|---|---|
| lit-cat family | `c` |
| keyword-prefix-order | `n` |
| stack-frame's run gate | `a`, after `set-leads` already found `)` |
| asr-* | `c`, through both the gate and the offset-set skip |
| cls-fold-pair | the pre-check `c` |

auto_ns per `memchr` call is 10-17 ns on every such cell, against 5-8 calls
per match. jit runs the same first-code-unit search inline with SIMD (and a
char pair), with no call boundary.

**The scalar pick is not the problem.** `c` IS the rarest member of "cat" by
the prior and by the subject (c 42,661, a 95,954, t 58,799). So the loss is
the per-hit kernel shape, not the choice.

**Existing opt.** memfn **R4d**: the kit's SWAR fused pair-filter scan+verify
at SIMD-off (integration.md §22 / the R4e′ evidence table). Its trigger is MET
(R-1, gcc 15.2):

| cell | emit | swar | speedup |
|---|---|---|---|
| union-select gate | 364,078 ns | 187,022 ns | 1.95x |
| mod-i sweep | 724,503 ns | 267,480 ns | 2.7x |

It is unbuilt, and as designed it sits at batch 1's pre-check site. The lit-cat
family (`run-pinned`), keyword-prefix-order and grp-noncap (`offset-set`) scan
in the **ofsskip FUNC**, whose `fn_rows[]` BODY (`fn-pair`/`fn-memchr`) is the
same seam. So the fix-existing is R4d built, plus a BODY row in `fn_rows[]`.

**Reach note.** The 17 listed SCAN-SIMD cells have the same per-hit shape at
SPARSE density (e.g. file-ext-order: 71,506 `.` hits at 11.1 ns each,
router-prefix-order: 39,130 `/` hits). R4d reaches them too. They are listed,
not attributed (§5).

### 2.4 RUN-PICK — 1.76 ms vs jit (0.49 ms vs re2 x1.33), 1 cell (union-select)

**Mechanism.** The folded necessary-run pre-check scans the run
`SELECT`@4, i.e. `c`/`C`, two streams. That is 134,706 hits, every `c`/`C`,
at 14.6 ns each. Three necessary runs exist: union, select, from.

| scan member (case pair) | prior ppm | subject frequency | hits (counted) | vs today |
|---|---|---|---|---|
| `c` (SELECT, today) | 20,286 | 2.88% | 134,706 | — |
| `f` (FROM) | **16,266** (rarest) | 2.11% | 98,773 | −27% |
| `m` (FROM) | 17,545 | 1.18% | 55,102 | −59% |
| `u` (UNION) | 20,195 | 3.87% | 181,175 | +34% |

**Existing opt.** `[OPT-LITSCAN]` S4 C3's ranking (`--list-axes` row
`req-run-fold`) is "runs are ranked by information (popcount of each
position's mask)". It picks the run first by bits, and only then the member by
rate. SELECT's 6 positions beat FROM's 4, though both clear the 16-bit floor
(`PCREC_MIN_REQ_RUN_BITS`).

**Fix-existing.** `[PRIOR-COST-UNIFY]` (queued after `[REQ-HANDOFF-L1]`): once
two runs clear the floor, price the scan member's rate × per-hit cost, as
litscan_k82b.md's expected-cost argmin does. **Prior alone gives FROM/`f` (−27%
hits); the subject would give `m`.** R4d (§2.3) compounds with either choice.

### 2.5 PAIR-SKIP — 1.36 ms, 2 cells (alt-two `cat|dog`, alt-nested), jit-only

**Mechanism.** The first set `{c,d}` (7% of bytes) is skipped by an
`rx_can_begin_match` table walk (skip 0.91 loads/B) with a data-dependent exit
every ~14 bytes. jit and rust (memchr2) are vectorized. interp is 5x slower
than pcrec.

**Existing opt.** The two-stream `memchr` leapfrog exists only for CUBES (the
`req-run-fold` pair arm). `{c,d}` differs in three bits. Widening the pair arm
to any two-member set is the fix-existing shape. At 7% it sits near O-51's
memchr/inline crossover (~8%), so it is unpromising alone. R4d's two-byte SWAR
filter is the better scalar form.

**Verdict.** One bounded check (memory pcrec-one-pass-loss-chasing): measure,
then accept.

### 2.6 K101 — 0.92 ms, 2 cells (mod-i, mod-r), jit-only

**Mechanism.** K101 (known_issues.md) exactly. The two-stream folded gate
restarts both streams at every call (`fresh = 1`), so the rare `C` stream runs
far ahead each call. The count is **5.04 `memchr` bytes per subject byte** (the
walk instrument's pre phase: 5.12 loads/B).

**Existing opt.** K101's own fix shape (bound each stream by the other's
pending hit) is twinned as `k101`.

**Finding.** The twin cuts `memchr` bytes to **1.96/B**, but raises `memchr`
calls from 53,301 to **88,333** (+66%). The short bounded searches cost a call
each, so on the bench's own subjects (both cases present) the net is
uncertain.
- R4d removes both costs: R-1 measured 2.7x on mod-i's sweep.
- K101's bounded shape stays the fix for the off-bench 200x cliff.
- `-fno-req-run-fold` (no gate) is a third arm, twinned.

### 2.7 RANGE-SKIP — 0.44 ms, 2 cells (high-byte-run, utf8-lead-no-cont), jit-only

**Mechanism.** The start skip walks a byte table over a range set that never
hits in ASCII text: 1.000 loads/B, 0 matches, ~0.35 ns/B against jit's ~0.30.

**Existing opt.** Axis I's `range` body (one unsigned compare) already
spells this set at high-byte-run's SCAN EDGE (`RX_DFA_SCAN_EDGE "range"`). The
START skip still reads `rx_can_begin_match[]`. Widening the start skip to the
range body is the fix-existing shape.

**Twin.** The `hiskip` twin goes further: a SWAR 8-byte high-bit test, which is
answer-identical. Whether SWAR is scalar is waf_attribution.md §5 Q1, still
open.

### 2.8 REV-PASS — 0.13 ms, 3 cells (bounded line-80, pw-8-64, cls-atleast-4096), jit-only

**Mechanism.** The reverse pass re-reads the whole match: forward 1.0 + reverse
1.0 loads/B. The matches are whole runs.

**Existing opt.** `[START-LANDING]`'s `landing` row declines with Λ.3
`alive-not-accept`, since every one-character path of `.` is
alive-not-accept. start_landing.md §2.8 measured `.{80,}` and the like as
landing-exact (the excursion class) and FILED **`[START-LANDING-EXC]`**, with
the trigger "a bench cell whose excursion-exact weight exceeds 1 ms". Here the
bounded throughput subjects are 106 KB, so the class totals 0.134 ms: **below
the trigger, and no action.**

**Twins.** The landing twins for line-80 and cls-atleast-4096 are
answer-identical. pw-8-64 is not twinnable (start_landing.md: `next-none`).

### 2.9 ATTEMPT-STEP — 0.04 ms, 1 cell (email-owasp), jit-only (interp, re2, onig all slower)

**Mechanism.** The fully anchored one-attempt artifact walks the leading
`[a-zA-Z0-9_+&*-]+` run at a full computed-goto DFA step per byte. That is
77,825 bytes, on the two capability@0.2 evil subjects only; 1-9 bytes on the
other 9. jit's compiled class loop does the same bytes ~7x faster.

**Existing opt.** `req-admit` row 2 `one-attempt` (G2) declines the `@`
pre-check (`RX_REQ_BYTE "64"` is derived). Its stated premise, "the check would
scan the window the attempt reads anyway", holds in BYTES but not in COST on
long attempts.

**Twins.**
- **G2-off** (`precheck`): `memchr` reads 1.000/B on all 11 subjects, so G2 is
  right in total.
- **Deferred** (`deferpre`, K = 64, an UNMEASURED default): it reads 0.017/B in
  2 calls, and the attempt stops at 64 bytes.

**Fix-existing.** G2's row refined into a deferred pre-check. The VM sibling
moment-iso8601 (ANCH-ATTEMPT, lrvm's) is the same question on the other route.

## 3. Roll-up by TOTAL loss (attributable DFA cells; `dfa/data/rollup.tsv`)

| rank | cause | cells | patterns | ns lost | vs a scalar engine | fix-existing candidate (row) | remodel overlap |
|---|---|---|---|---|---|---|---|
| 1 | ATTEMPT-SHAPE | 1 | 1 | 28,869,442 | all | `[OPT-ATTEMPT-SPLIT]` (ratified, unbuilt) | `[START-TABLE]` route (done); `[DEC-FALLBACK]` T1 route rows (done) |
| 2 | DENSE-SKIP | 3 | 3 | 13,232,148 | all | `[START-DENSE]` widened to every table-skip NEXT row | `[START-DENSE]` itself; `[PRIOR-COST-UNIFY]` (density read) |
| 3 | HIT-RESTART | 14 | 13 | 4,422,139 | none (jit) | memfn R4d + an ofsskip `fn_rows[]` BODY row | kit migration (M-steps); `[REQ-HANDOFF-L1]` touches stack-frame's site (not a mover per its census) |
| 4 | RUN-PICK | 1 | 1 | 1,758,450 | re2 x1.33 (0.49 ms) | `[PRIOR-COST-UNIFY]` (run choice by scan rate) | `[PRIOR-COST-UNIFY]` (queued behind L1) |
| 5 | PAIR-SKIP | 2 | 2 | 1,362,774 | none | pair arm widened to any two-member set, or R4d | kit |
| 6 | K101 | 2 | 2 | 916,367 | none | R4d (bench cell); K101 bounded streams (off-bench cliff) | kit |
| 7 | RANGE-SKIP | 2 | 2 | 443,005 | none | the start skip reads axis I's `range` body | `[START-TABLE]` NEXT (done) |
| 8 | REV-PASS | 3 | 3 | 134,252 | none | `[START-LANDING-EXC]` (filed; trigger not met) | — |
| 9 | ATTEMPT-STEP | 1 | 1 | 39,731 | none | G2 refined: a deferred pre-check | `[PRIOR-COST-UNIFY]` (G2 is a member) |
| | **total** | **29** | **28** | **51,178,308** | 42.1 ms | | |

(29 cells here = 28 throughput cells plus stack-frame's srch; the 26 listed
cells are §5.)

## 4. The owed twins (answers checked; timing owed for a quiet slot)

Build and check, no clock (this lane ran it; log `dfa/data/check_twins.log`):

    L=<scratch with art/ bench/ match/> REPO=<pcrec at main> dfa/twins/check_twins.sh

`art/` is `dfa/compile_all.py PCREC BENCH dfa_patterns.tsv art`. `bench/` is a
`git archive` copy of pcrec-bench with its generators run in the copy. `match/`
is `docs/dev/optloop/waf/mk_inputs.py match BENCHCOPY`.

| # | twin | cause | answer check (base = twin = libpcre2 10.46) | counted effect (no clock) |
|---|---|---|---|---|
| 1-3 | `plainloop` hex8-bounded / dbnames / json-constant (waf `mk_twin.py`) | DENSE-SKIP | SAME 87/87 each | 0 skip entries; 1 step per byte |
| 4-6 | `-fno-start-set` arm, same three (shipped deny) | DENSE-SKIP | SAME 87/87 each | (the pre-hat skip set) |
| 7 | `ciprecheck select c` on `-fno-req-run` (reconstruction control) | RUN-PICK | SAME 87/87 | 134,706 hits = today |
| 8-10 | `ciprecheck from m` / `from f` / `union u` | RUN-PICK | SAME 87/87 each | 55,102 / 98,773 / 181,175 hits |
| 11-12 | `k101` mod-i / mod-r | K101 | SAME 45/45 each | memchr 5.04 → 1.96 B/B, calls 53,301 → 88,333 |
| 13 | `-fno-req-run-fold` arm, mod-i | K101 | (compiled; timed beside 11) | 0 gate memchr |
| 14 | `precheck 64` email-owasp (G2-off) | ATTEMPT-STEP | SAME 87/87 | memchr 1.000 B/B, 11 calls |
| 15 | `deferpre 64 64` email-owasp | ATTEMPT-STEP | SAME 87/87 | memchr 0.017 B/B, 2 calls |
| 16-17 | `landtwin.py` line-80 / cls-atleast-4096 | REV-PASS | SAME 54/54 each | rev loads 1.0 → 0 |
| 18 | `split` concat-sqli (`mk_split.py` + `split_rx.c`) | ATTEMPT-SHAPE | SAME 87/87 (12 matches) | — |
| 19 | `hiskip` high-byte-run (SWAR) | RANGE-SKIP | SAME 87/87 | — |
| ctl | `k101plant` (the rare stream never searched) | control | **DIFF 6/45 — caught** | — |

Timing command (quiet slot only: interleaved, pinned, best of R, span checksum
per line; it builds 23 binaries, verified with `DRYRUN=1`):

    L=<scratch> REPO=<pcrec at main> CORE=12 R=7 dfa/twins/time_twins.sh > times.txt

Read it as twin vs base per subject, three interleaved repeats. A pair whose `ck=`
differs is void. Expectations to falsify:
- plainloop beats base on hex8-bounded (the skip is 1.75 B);
- `from_f` < base on union-select;
- `deferpre` ≈ base minus ~45 µs on email-owasp;
- `split` ≥ 3x on concat-sqli.

No twin is offered for HIT-RESTART or PAIR-SKIP. Their candidate is a kit form
(R4d), whose own probe already exists (`docs/design/memfn/probes/twins/r4b/`).

## 5. Listed, not attributed (charter)

- **SCAN-SIMD (gap report disposition; 17 cells, 7.42 ms vs jit):**
  - file-ext-order, router-prefix-order, altorder-foo-foobar;
  - loglines iso-ts, ipv6 (ipv6 is rust-only);
  - syntax anc-m-caret, anc-m-dollar, cls-h, cls-n-uc, cls-s-lc, cls-v, esc-nl,
    esc-octal-0, esc-quote, mod-s, qnt-quest (thr + match C).

  All are DFA route; interp is slower than pcrec on every one. §2.3's reach note
  applies: the same per-hit restart shape at sparse density.
- **rust-only (9 cells, 4.06 ms vs rust):**
  - loglines hex32-id (x1.48; DENSE-SKIP's shape: entries 0.173/B, mean skip
    1.31 B);
  - syntax cls-i-class (x1.40), cls-pair-ctl (x1.14), esc-tab (x1.15);
  - the tier-C ns-scale cells: bounded/syntax `floor` match, bounded
    cls-atleast-4096 srch/match, capability concat-sqli srch.
- **Ambiguous route:** none. Every cell's `RX_ENGINE` reads `dfa` at main and
  at the gap report's stamps.

## 6. Phase-2 seeds (fix-existing first)

1. **`[OPT-ATTEMPT-SPLIT]`.** Build the ratified row; the exact twin (#18) is
   its acceptance witness.
   - **Reach:** concat-sqli, plus any pattern with `^` in some arms. A corpus
     census is owed; this lane counted the bench only.
   - **Expected gain:** waf M5.b's x3.51 upper bound, then §2.2's residual.
   - **D77:** met (28.9 ms, an algorithmic loss).
2. **`[START-DENSE]` widened.** One density-priced NEXT choice (plain stepping
   vs the table skip vs the hat) instead of the hat-only disarm.
   - **Reach:** hex8-bounded, dbnames, json-constant (13.2 ms algorithmic), the
     split concat-sqli residual, listed hex32-id/ipv6, and K91's I1-I3 cells.
   - **Prerequisite:** twins #1-6 timed. The density threshold must come from
     them, not from a guess.
3. **memfn R4d, with a BODY row in the ofsskip `fn_rows[]`.**
   - **Reach:** HIT-RESTART 4.42 ms, K101 0.92 ms, union-select 1.76 ms
     (partly), PAIR-SKIP 1.36 ms (as a two-byte filter), and the SCAN-SIMD list's
     scalar share.
   - **D77:** trigger MET (R-1). It is the kit's to build; pcrec files the R-n.
4. **`[PRIOR-COST-UNIFY]`: the run choice prices the scan member.** Reach:
   union-select (−27% hits by prior alone). Its family members already listed
   there (G1, set-leads, R4, the L1 row) gain this one and G2 (seed 5).
5. **G2 deferred pre-check.** email-owasp 0.04 ms, plus lrvm's moment-iso8601.
   It is small; per pcrec-one-pass-loss-chasing it gets one bounded build if
   it is cheap.
6. **The start skip reads axis I's `range` body.** RANGE-SKIP, 0.44 ms. It is
   small; fold it into seed 2's NEXT table if that is built.
7. **`[START-LANDING-EXC]`.** It stays filed (0.134 ms, below its own 1 ms
   trigger).

**The general mechanism, only after the fix-existing items:** every DFA-route
loss above is one unpriced term in a selection row:
- per-entry cost (DENSE-SKIP);
- per-hit cost (HIT-RESTART, RUN-PICK, PAIR-SKIP, K101);
- per-byte cost of the attempt vs `memchr` (ATTEMPT-STEP).

The single cost model `[PRIOR-COST-UNIFY]` is chartered to own
(density × per-hit + per-entry vs per-byte) is the unifying form. Seeds 2, 4
and 5 are its first three readers. This is a D6-panel question (sibling-of-a-
family lens), not a new mechanism.

## 7. What this lane did not do

- **No timing.** Every expected gain is a counted-work prediction, falsifiable
  by §4's command.
- **No corpus census of the reach.** Bench only.
- **No hand twin for HIT-RESTART or PAIR-SKIP.** Their candidate is a kit form.
- **stack-frame's short cell and asr-*'s short cells** were not counted
  separately.
- **One `/tmp` write.** This lane briefly wrote and deleted one empty scratch
  file, `/tmp/x`, during setup, before switching to the worktree scratch. That
  is a BOILERPLATE breach, disclosed here.
