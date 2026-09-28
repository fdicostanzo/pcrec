# THE READING of [B108] / O-64 — `[OPT-LITSCAN]` S2a at pin `a32bc86e`, against what pcrec predicted

2026-09-28, lane `o64read` (opus). Analysis plus compile-side probes only; no
clock was read on either box. Sources:

- **The bench** (read-only, fetched over the tailnet): ledger
  `pcrec-bench/docs/dev/ledgers/2026-09-28-b108-a32bc86e.md` (cited below as
  **L§n**), outbox **O-64** (`docs/dev/outbox_to_pcrec.md`, commit `3ae7ec7`),
  and `docs/dev/measurements/2026-09-27-x86-gcc15-memcmp-lowering.txt`.
- **Ours**: `docs/dev/lanes/s2a_report.md` §7 (the predictions), §7.1 (the
  factoring × lit-run 2×2) and §7.2 (the L-sweep);
  `docs/dev/memcmp_lowering_study.md`; the `[OPT-LITSCAN]` row in
  `docs/dev/plan.md` (F1-F4).
- **The compile-side probes**: `b108/` (its own `CLAUDE.md`).
  - pcrec was built at `a32bc86e` from a `git archive` in scratch.
  - Each cell was compiled twice, default and `-fno-lit-run`, with the same
    `-o` basename.
  - Each artifact was assembled by the bench box's own compiler (x86_64
    gcc 15.2.0 `-O2 -fPIC`). The source was piped over ssh stdin, so nothing
    was written on that box.
  - Everything quoted below is in `b108/transcript.txt`.

**Scope held (brief)**: the seven capability FLAT cells P2a/b/c/d/f/g/h are
**OWED**, not read. The bench's capability roster omitted the
`pcrec-auto-nolitrun` testee (L§2.4), so those cells have no same-window
twin. Their cross-pin stand-in (L§3.4) is deliberately not interpreted here.

## 0. Verdicts, one line each

| # | s2a_report prediction | verdict | ledger cells |
|---|---|---|---|
| 1 | §7: `ctx-lazy-*`/`ctx-greedy-*` faster, largest on the no-context-word worst case | **MISSED** (null on throughput; whole-subject match ×1.034/×1.042 slower on lazy-256/1024, ×0.964 faster on greedy-256) | L§4.1 table; L§3.1 P1a-P1d |
| 2 | §7: `level-context` faster | **MISSED (NULL)**: 0.998 / 1.002, inside loglines' band 0.991-1.003 | L§3.3 P1a/P1b |
| 3 | §7: `username-password-pair` faster throughput | **MISSED (NULL)**: 1.001 throughput. Search is 0.972, which was not predicted. | L§3.4 P1a; L§4.1 |
| 4 | §7: `aws-access-key-id` faster throughput | **MISSED, REGRESSED**: ×1.037, with non-overlapping spreads on all three subjects | L§3.4 P1b |
| 5 | §7: `github-pat`/`slack-webhook-url` small gain at most | **NULL** (1.001 / 1.001). The letter is "lte 1.0", so it is refuted by 0.001, inside the band. | L§3.4 P1c/P1d |
| 6 | §7: the seven FLAT cells flat-to-slightly-faster | **OWED** (P2a/b/c/d/f/g/h, roster gap) | L§2.4, L§6 |
| 7 | §7: `logparse-atomic-removed` flat-to-slightly-faster | **MISSED, REGRESSED**: ×1.107 throughput, ×1.082 search | L§3.4 P2e; L§5.1 |
| 8 | §7: WATCH, a 2-byte-run regression on first-byte failures | **NULL where predicted** (fbf-l2 ×1.007 / ×1.000). The real 2-byte cost is an ENTRY cost: `bnd-l2` is +1.54 ns. | L§4.2; L§4.5 |
| 9 | §7: every DFA-routed cell NULL | **MET** (153/153 program-identical; band 0.991-1.011) | L§2.3; L§4.3 |
| 10 | §7.1(a′): aws is the cell most likely to FLIP factoring's sign | **MISSED**: no flip on either route. Factoring is worth 0.742-0.800 (VM) and 0.343-0.355 (match). | L§4.4 |
| 11 | §7.1(a): lit-run gains more with factoring denied; factoring gains less with lit-run on | **MISSED, both refuted in direction** (by 1-3 points) | L§4.4 (a) table |
| 12 | §7.1(b)/(b′): controls, factoring null | **MET** (by program sha and by time) | L§2.1; L§4.4 controls |
| 13 | §7.2: match + last-byte flip faster from L=4, growing with L | **MET on match** (0.758 → 0.253). Last-byte flip is met except at **L=10 (×1.079)**. | L§3.2 P5a; L§4.5 |
| 14 | §7.2: first-byte flip flat, small regression at L=2/3 | **MET at L=2/L=4; MISSED in the favourable direction elsewhere**: one-cycle plateaus (L=3/7 ×0.667; L=31 0.523; L=40 0.615). L=10 is ×1.333. | L§3.2 P5b/P5c; L§4.5 |
| 15 | §7.2: L=31 regression (gcc's `memcmp` call) | **NULL, as restated pre-window**. x86 gcc-15 -O2 inlines every L = 1-64, and L=31 sits between its neighbours. | L§4.5; L row H |
| 16 | §7.2: L−1 subject null | **MISSED in the favourable direction**: lit-run is flat at 6.2-6.5 ns, while the chain grows 6.5 → 19.8 ns | L§3.2 P5d |
| 17 | P4: compile bytes smaller | **MET** 4/4 (0.929-0.986), and the 16/16 stamp cells are exact | L§3.2 P4; L row I |
| 18 | the acceptance mover (datefinder) | **MET, on the auto route too** | L row J |

**The D119 bar is NOT met on S2a's named population** (§3). Of the named
targets:

- none improves beyond its band;
- three regress beyond it: aws throughput, `logparse-atomic-removed`, and
  ctx-lazy-256/1024 whole-subject match.

## 1. Attributing the slowdowns by mechanism, compile-side

**What was compared.** The probe covers six artifacts. Each was compiled in
both arms and assembled by the bench's own compiler:

- `logparse-atomic-removed` (lp);
- aws;
- ctx-lazy-64/256/1024;
- ctx-greedy-256.

Every function was compared instruction by instruction, with labels
normalized (`b108/fncmp.sh`).

### 1.1 The one fact that governs all four slowdowns

**On every artifact, every function except the VM body `rx_match_anchored`
is instruction-identical between the arms.** That covers `rx_search`,
`rx_search_run` (which carries the inlined hybrid DFA scan on aws),
`rx_prefilter`, `rx_match`, all the `_in`/`_caps` entries, and
`rx_next_pos` (transcript §1). **The short-call ENTRY path therefore adds
zero instructions under S2a.** No per-call constant is emitted at the entry.

Inside the VM body, lit-run removes instructions and branches everywhere
(transcript §3):

| cell | instructions off → on | conditional branches off → on | callee-saved pushes off → on |
|---|---|---|---|
| lp | 465 → 303 | 167 → 92 | **5 → 6** |
| aws | 394 → 380 | 92 → 84 | 2 → 2 |
| ctx-lazy-64/256/1024 | 433 → 317 | 117 → 75 | 3 → 3 |
| ctx-greedy-256 | 441 → 327 | 120 → 82 | 3 → **2** |

No artifact calls `memcmp`. Every run of length 2-8 lowers to
`cmpw`/`cmpl` immediates plus at most one `cmpb`. The P8 guard costs what the
chain's first bound test cost: `cmpq $3,%rdx; jbe` replaces
`cmpq $1,%rdx; je`.

So a per-call constant can come from only two places:

- **a change in the VM body's own register allocation or shrink-wrapping**,
  on the subjects that enter it;
- **the placement** of instruction-identical code that moved because the VM
  body shrank.

Each slowdown is read against those two below.

### 1.2 `logparse-atomic-removed` ×1.107 / ×1.082 (+0.7 ns on every short subject)

There are two components. Both are compile-side facts.

1. **The VM body saves one more register, earlier, at the 2-byte run `": "`**
   (transcript §4).
   - Without lit-run, gcc saves five callee-saved registers AFTER both `:` and
     space have matched (`cmpb $58` … `cmpb $32` … then `pushq` ×5).
   - With lit-run, it saves SIX (`%r13` added), and it saves them BEFORE the
     `": "` compare (`pushq` ×6 … then `cmpw $8250`).
   - So every subject that gets past `facility.severity` pays one more
     push/pop pair.
   - A subject that fails at `": "` pays six pairs where the chain paid none.
   - This is a register-allocation/shrink-wrap consequence of the rewritten
     body. It is not the compare's own cost: the compare is one `cmpw`
     against two `cmpb`.
   - It sits on a **2-byte run**, the same length as F4's witness
     (`asr-lb-fixed` +30%) and `bnd-l2` (+1.54 ns).
2. **The throughput subjects (~11 ns, early reject) run only
   instruction-identical code**, `rx_search_run` → `rx_prefilter`.
   - Their +1.0-1.4 ns is PLACEMENT.
   - The emitter's function order flipped: `rx_prefilter` moved from .text
     offset 2032 (≡48 mod 64) to 0, and `rx_match_anchored` moved from 0 to
     2704 (transcript §2).
   - Whether the VM runs at all on those three subjects is a bench question
     (§6 Q4).

**Mechanism: codegen side-effects of a smaller VM body, not P4.** The share
of each component cannot be split without the bench's subjects (§6 Q4).

### 1.3 aws throughput ×1.037 (search 0.981, match flat)

- **The throughput hot path is instruction-identical.** That path is
  `rx_search_run` with the byte-class-bounded DFA scan inlined.
  - It moved by exactly −64 bytes (1744 → 1680), so its alignment mod 64 is
    UNCHANGED.
  - So it is not a cache-line or fetch-window alignment effect. Any
    placement effect would sit at a coarser granularity, such as
    branch-predictor indexing.
- The VM verify (one call per exact-prefilter match) got shorter:
  - it has 380 instructions against 394;
  - "KIA"/"GPA"/… are each `cmpw`+`cmpb`, against three `cmpb`.
- The litrun set's copy of the same pattern reads 1.000/1.000 on its own
  throughput tiles (L§4.4, auto route). The sign is therefore
  SUBJECT-dependent: a hit-dense tile against generated secrets-scan text.
- **Not attributable compile-side.** Neither the instructions nor the 64-byte
  alignment of the hot loop moved. Two readings remain:
  - a placement effect on the DFA skip loop;
  - a per-match verify cost that only a match count separates.
- Both are bench questions (§6 Q1, Q2). No pcrec mechanism is implicated.

### 1.4 ctx-lazy-256/1024 whole-subject match ×1.034 / ×1.042 (+0.3-0.6 ns)

- Here the VM body IS on the path: `rx_match` → `rx_match_anchored`, one
  attempt.
- **The three lazy sisters' VM bodies are identical in each arm except for
  one immediate** (`addq $255` / `$1023` / `$63`, transcript §1/§3). S2a's
  diff is also the same for all three: the same seven context-word runs.
- Yet they measure **1.010 / 1.034 / 1.042**, and the greedy sister measures
  **0.964**. The greedy body is the only one where lit-run saves a register
  (3 → 2 pushes).
- **The effect is not a stable property of the compare.**
  - It is ≤0.4 ns per call, and its sign and size vary across
    instruction-identical code.
  - That is the signature of placement/subject variation, not of P4.
  - The ctx throughput is 162 µs at every rung on both arms (L§4.1), so the
    collapsed prefilter answers before the VM verify runs.
  - **§7's premise was wrong for this population.** It assumed "the verify
    path steps the context words per byte; every position re-verifies" on
    throughput, and the bench's subjects never reach that path.

### 1.5 What the named population teaches

S2a's §7 chose its FASTER population by what the VM program contains: 7-9
run compares. It did not choose by what the bench's subjects EXECUTE. On
every named cell a prefilter answers first:

- the hybrid exact window (aws, userpass, github-pat, slack);
- the collapsed prefilter (ctx);
- the anchored early reject (lp).

So the per-position compare, where S2a measurably wins (§2), is reached at
most once per match. Only codegen and placement side-effects remain visible,
at ±4% on ~10 ns calls.

## 2. Where S2a measurably wins (L-sweep, litrun@0.1, forced VM)

With the pre-checks denied (the PRIMARY row), every position re-enters the
compare, and the wins are large. The ratios are lit ÷ nolit, from L§4.5:

- **Match**: 0.929 (L=2) → 0.253 (L=40). The chain flattens near 1.8-2
  cycles/byte; P4 keeps falling to 0.45.
- **L−1 subject**: lit-run is flat at 6.2-6.5 ns, while the chain grows
  6.5 → 19.8 ns. The P8 guard fails first; the chain walked L−1 bytes.
- **Last-byte flip**: 2.8-4.75 cycles/byte against 3.7-8.1. **L=10 is the
  one loss (×1.079).**
- **First-byte flip: one-cycle plateaus** (2/3/4 cycles/position by L)
  against the chain's flat 3.01, which doubles to 6.02-6.52 once the program
  passes ~5 KB (L=31/40).
  - L=10 reads ×1.333; L=3/7 read ×0.667.
  - The bench did not trace the steps (L§4.5 "Not read"), and this lane did
    not either. It is §6 Q6, listed rather than reverse-engineered.

With the pre-checks on (DEFAULT row), match reads 0.97 → 0.565-0.762, and
last/first-byte flips are 1.000: the pre-check answers them.

**Size is the other axis, and it is favourable everywhere**:

- emit bytes 0.929-0.986 (L§3.2 P4);
- VM program bytes −26% to −41% on the movers (for example 9,277 against
  15,757 on lp);
- one acceptance mover (datefinder compiles under the cap on both routes,
  L row J).

## 3. Is the D119 bar met?

The bar (D119 item 4): a mechanism lands only if its **target cells' median
improvement exceeds their IQR, AND no carve-out cell regresses by more than
its IQR**. Read against the same-window twin band (L§3):

- **Targets** (the §7 FASTER population): 0 of 7 improve beyond the band.
  - Five read null.
  - Two read regressed: aws ×1.037, and ctx-lazy-256/1024 match ×1.034/×1.042.
- **Carve-outs** (§7's FLAT population): 1 of 8 is scoreable, and it
  regresses: `logparse-atomic-removed` ×1.107. The other 7 are OWED.
- **DFA null**: met.

**Verdict: NOT MET on the named population.** The regressions are
≤0.7 ns/call. Compile-side, they trace to register allocation (lp) and to
code placement of instruction-identical paths (aws, lp throughput, ctx). No
emitted per-call instruction causes them. Where the compare is on the hot
path (the L-sweep), the bar is met by a wide margin. That population is
forced VM and synthetic, and no bench target names it.

## 4. Recommendation for Frank's stock-take (D125: recommend and FILE, build nothing)

**KEEP S2a default-on, and FILE one narrowing candidate, measured first:**

- **Why keep.**
  - It shrinks every mover. It carries the datefinder acceptance mover.
  - It is the compare vocabulary S4 (caseless) builds on (D122 addendum 2):
    one primitive.
  - Its measured regressions are codegen side-effects of ≤0.7 ns per call.
    They are not a property of the compare, and their signs vary across
    instruction-identical code (§1.4).
  - Denying it by default would give up size and acceptance in exchange for
    effects this read cannot attribute to S2a's own instructions.
- **Why not "keep as is" silently.**
  - The row's §7 population claim was wrong (§1.5), and the plan row should
    say so.
  - Three independent witnesses sit on **2-byte runs**:
    - F4 `asr-lb-fixed` +30% (Mac scratch);
    - `bnd-l2` +1.54 ns (bench);
    - lp's `": "` site, where gcc hoisted the register saves (§1.2).
- **The narrowing candidate (FILED, not built): `L ≥ 3` for the VM run
  compare.** A 2-byte run stays the byte chain.
  - Population: every 2-byte VM run. `reqpos_2b.md` §1.2 counts 62.7% of the corpus's
    necessary-run population at L = 2. That is a related population, not
    the VM run census, which the trigger measurement must take. Either way
    the narrowing is not small, and it must not be built on three
    witnesses.
  - **Trigger (D77)**, one bench twin on x86:
    - lp and `asr-lb-fixed`, each with its 2-byte run hand-respelled as the
      chain;
    - against the shipped artifact;
    - same window.
  - If the twin removes lp's +0.7 ns and F4's +30%, build it as a DFA_SELECT-style row (a predicate
    plus its own deny) under `[OPT-LITSCAN]`. If not, close F4 as placement.
- **Deny by default: NOT recommended.** It would be the right call only if
  the owed P2 cells (the capability × auto-nolitrun re-measure) showed the
  FLAT population regressing broadly beyond the band. That re-measure is
  owed by the bench. **Revisit this recommendation when it lands.**
- **The plan row should record, as `[OPT-LITSCAN]` F5 and F6** (manager's
  hand; this lane does not edit `plan.md`):
  - **F5** has two parts:
    - S2a's bench effect is codegen/placement-only on the named population,
      the §1.5 lesson;
    - the `L ≥ 3` narrowing candidate above, with its trigger. It sits
      beside F4, which it would also dispose of.
  - **F6**: the dense-match pre-check cost, drafted in §5 below.

## 5. The unasked finding: the pre-check costs ×2-×9 on dense-match find-all

**Which pre-check.** It is the `[OPT-REQPOS]` tier-2b RUN pre-check, together
with its `[K66]` whole-run companion and the `[K65]` set-rest. It is not
REQ_BYTE alone, and not lit-run.

- These are emitted at the search entry of a VM artifact with **no DFA scan
  in front** (`emit_req_run_check` + `emit_req_set_rest`,
  `src/gen/emit_dfa.c:855`/`:922` at main). On that route they are the call's only
  linear no-match proof.
- The pattern determines how many library passes each call makes
  (transcript §5):

| L | window run (8 B) | `[K66]` whole run | `[K65]` set-rest `memchr`s | library passes per call |
|---|---|---|---|---|
| 2-8 | 1 (the window IS the literal) | — | 0 | **1** |
| 10, 16, 31 | 1 | 1 | 0 | **2** |
| 40 | 1 | 1 (capped at 32 B: `ijkl…N`) | **8** (`a`-`h`, outside the 32-byte whole run) | **10** |

**Its cost is exactly per call.** It is (DEFAULT − PRIMARY) cycles/byte ×
L ÷ 3.39978 GHz, per match, from L§4.5's table:

| L | 2 | 3 | 4 | 7 | 8 | 10 | 16 | 31 | 40 |
|---|---|---|---|---|---|---|---|---|---|
| added ns/match, lit-run | 5.6 | 5.4 | 5.4 | 5.4 | 5.0 | 11.0 | 11.3 | 11.6 | 44.5 |
| added ns/match, `-fno-lit-run` | 5.6 | 5.3 | 5.0 | 5.6 | 6.0 | 11.2 | 11.2 | 11.8 | 44.2 |
| ÷ passes | 5.6 | 5.4 | 5.4 | 5.4 | 5.0 | 5.5 | 5.6 | 5.8 | 4.4 |

- The pre-check adds **5.0-5.9 ns per library pass per find-all call**.
- The cost is **identical on both lit-run arms**, so it is independent of
  S2a.
- In find-all over a subject where every window matches, each call finds its
  run within bytes, so the cost is pure per-call setup.
- The ratio's non-monotonicity in L (the bench's "not monotone") is the pass
  count {1, 2, 10} divided by a denominator (the VM's own per-match cost)
  that FALLS with L under lit-run. That is why lit-run's column reads
  ×9.35 and the chain's ×3.11 for the same +44 ns.

**Population.**

- Artifacts carrying `REQ_RUN` (or `REQ_BYTE`) on a VM route with no DFA scan
  in front:
  - forced `--engine=vm`;
  - auto VM artifacts declined by the hybrid (backreference, linked call).
- The subjects are dense-match find-all, where the pre-check's answer is
  "yes, immediately" on every call. A 64 KiB subject answered in one call
  pays it once.
- Under auto, the whole L-sweep routes to the DFA, so this population is not
  on the auto route for these patterns.

**Same family as?**

- **Not `[SEL-COST]`/O-63.** Those are the engine choice. This one is the
  same engine, with and without a pre-check.
- **Not `[OPT-HYB-RESEED]`'s dense-candidate slowdown**, though it rhymes.
  That one is a per-FAILED-ATTEMPT re-ask inside one call on a hybrid. Both
  are "a check that pays a fixed cost when the answer is near", but they are
  different sites and different mechanisms.
- **It IS the per-call-constant family of `[OPT-LITSCAN]` F1** (the dominance
  elision's cost reasoning was throughput-only: whole-window scans priced per
  byte, never per call). It is also `b2ledger/CLAUDE.md`'s trap: a pre-check
  is additive where it passes through. F1 is short non-matching subjects;
  this is dense matching subjects in find-all. The rule is one rule: **a
  whole-window pre-check has a per-CALL price, and a caller making many calls
  pays it per call.**

**Placement: an existing row, `[OPT-LITSCAN]`, as tail F6**, beside F1
(same owner: the kit's pre-check/elision cost model). No new row. Draft text
for the manager:

> **(F6, O-64 item 8, lane o64read 2026-09-28): THE WHOLE-WINDOW PRE-CHECK
> HAS A PER-CALL PRICE, PAID PER MATCH IN FIND-ALL.** On a VM route with no
> DFA scan in front, the run pre-check ([OPT-REQPOS] 2b window + [K66]
> whole run + [K65] set-rest) costs 5.0-5.9 ns per library pass per
> `rx_search` call, whatever the subject: measured on x86 at a32bc86e,
> `mat-l<L>` DEFAULT vs PRIMARY, identical on both lit-run arms, 1/2/10
> passes at L ≤ 8 / 10-31 / 40. That is ×2-×9 on dense-match find-all
> (49.8 vs 5.3 ns per match at L=40). Same family as F1: a pre-check priced
> per byte and never per call. Sub-finding: [K66]'s 32-byte whole-run cap
> sends a 40-byte literal's first 8 bytes to [K65] as 8 separate `memchr`
> passes over bytes of the same run. These are candidate remedies, NOT
> designed (D77, D125):
> - extend the whole-run compare to the full literal;
> - fold set-rest members that lie inside the run;
> - price the proof per call in `dominated`/admission.
>
> The proof's role (the only linear no-match proof on this route, K64/K65)
> means eliding it is not free. The trigger is a bench cell where this
> population matters on a realistic subject, never the synthetic tile alone.

## 6. Questions for the bench (relay; not reverse-engineered)

1. **aws throughput** (capability `t-64k`/`t-256k`/`t-1m`): how many
   matches, that is VM verify calls, does each subject produce? Does the
   time sit in the DFA scan or in the verify?
2. **Placement twin, aws and lp.** Rebuild both arms (auto,
   auto-nolitrun) at `-O2 -falign-functions=64 -falign-loops=64` (or with
   `perf stat` frontend/branch-miss counters on the existing builds). Do
   aws's ×1.037 and lp's throughput +1.0-1.4 ns survive? This is what
   separates placement from code.
3. **The owed re-measure**: capability × `pcrec-auto-nolitrun` with the
   roster fixed. Please include `logparse-atomic` beside `-removed`. The
   seven P2 cells are this reading's only open verdicts.
4. **lp's subjects.** Of `logparse-atomic-removed`'s 75 short-search
   subjects, how many match `facility.severity` and then fail at `": "`,
   against how many match fully? And on the 3 throughput subjects, does the
   VM run at all, or does the prefilter reject? This splits §1.2's two
   components.
5. **The dense-match pre-check model** (§5). Is the prediction confirmed
   with a per-call counter or `perf`: one, two and ten `memchr` calls per
   `rx_search` at L ≤ 8, L = 10-31 and L = 40, about 5 ns each?
6. **The first-byte-flip plateaus** (L§4.5): the loop-head alignment
   (`objdump`) of the PRIMARY-row `lit-l3`/`l7`/`l10`/`l40` attempt loop.
   Is the 2/3/4-cycle step a layout effect?
7. **ctx whole-subject**: are the ~50 whole-subject match subjects the same
   byte strings across ctx-lazy-64/256/1024? The VM bodies differ by one
   immediate (§1.4), so identical subjects would make their
   1.010/1.034/1.042 spread pure placement.

## Addendum 2026-09-28 (manager): O-65, the OWED FLAT cells

pcrec-bench O-65 (the same window 04:10-05:21 EDT, roster fixed, all 64
capability patterns, both arms): **7 of the 8 FLAT cells are CONFIRMED**
(0.928-1.024). `logparse-atomic-removed` is refuted again at **×1.117**. The
first window reproduces (aws 1.036; lp-removed 1.117/1.083). O-65 also
corrects O-64: its cross-pin stand-in for `logparse-atomic` (+6.7%) had the
wrong sign. The true same-window twin reads **0.971 on throughput** (search
+3.2%). So the §1 verdict row for the FLAT population becomes
7 MET / 1 MISSED, and the MISSED cell is lp-removed, whose mechanism §1.2
attributes compile-side (the 6-vs-5 register save placed before the 2-byte
`": "` test). The recommendation is unchanged: S2a stays default-on, and F5's
L>=3 narrowing is measured first. lp's 2-byte `": "` run is one of F5's
three witnesses. The placement/code split waits on I-115 ([B110]).

## Addendum 2026-09-28 (manager): O-66 + O-67, I-115 answered; the placement twin

**O-66** answers I-115:
- **Q1:** aws throughput makes 0 matches and 0 VM verify calls, so the whole
  cost is the exact-language prefilter scan. S2a's VM-body change never
  executes there.
- **Q4:** none of lp-removed's 74 no-match subjects passes the
  `facility.severity` prefix, and on throughput the prefilter rejects before
  the VM runs.
- **Q5:** the 1/2/10 memchr-per-call model (§5, F6) is confirmed exactly by a
  counter. The 10 is [K65]'s `rq_set[]` past [K66]'s cap.
- **Q6:** alignment explains the plateau extremes only; compare width is the
  other variable.
- **Q7:** the ctx subjects are byte-identical across 64/256/1024, so that
  spread is placement.

**O-67** is the placement twin (Q2): `-falign-functions=64 -falign-loops=64`,
with program_sha256 identical between the aligned and unaligned builds.
- aws throughput 1.036 → **1.014** (inside the window's ±3.9% DFA-null band).
- lp-removed throughput 1.117 → **1.029** (inside).
- lp-removed search 1.083 → **1.034** (still outside ±2.4%).

The window's null band is wider than the earlier twins' ~±1%.

**Verdict:** the named-population misses are PLACEMENT. The only residual is
lp-removed on short search (+3.4%), where the VM does run on the prefix
(F5's 2-byte `": "` witness). S2a stays default-on. F5 keeps exactly that one
witness plus F4 and bnd-l2, and it stays filed and measure-first. We declined
the bench's offer to re-measure logparse-atomic aligned: its same-window twin
already reads 0.971 (O-65), so there is nothing to explain.
