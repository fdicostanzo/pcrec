# [CTX-PREFILTER] joint-position measurement

Lane `ctxjoint` (sonnet), branch `lane/ctxjoint`, worktree `worktrees/ctxjoint`
off main `31979ed3`. MEASUREMENT lane: nothing under `src/`, `cli/`, `lib/`.
Answers the D77 trigger `docs/dev/ctx_prefilter_census.md` §5 named: STEP 0
estimated the tightening with an INDEPENDENCE MODEL; this measures the JOINT
quantity on real subjects. Study code and raw results:
`studies/ctx_prefilter_joint/` (own CLAUDE.md).

## 0. Headline

1. **The condition is sound and it rejects a lot where there is anything to
   reject.** Over 6 subjects x 99 patterns (594 cells), zero cells reject a
   true match start (`T ⊆ C1` everywhere) and zero break `C1 ⊆ C0`. On the
   live cells (the prefilter admits >= 1 candidate) the candidate-weighted
   rejection is 60-77% and the per-pattern median is 0.96-1.00; the removal
   share of the FALSE candidates is 96.5-100% pooled.
2. **The independence model got the population right and the patterns
   wrong.** Model median rejection 0.93-0.96 against measured 0.99-1.00, but
   the mean absolute per-pattern gap is 0.21-0.37 and the model is off by
   more than 5 points on about half the cells, in both directions (§4).
3. **Verdict (§6): the D77 build trigger is NOT met.** The rejection number
   clears the bar; the bar's other two legs do not. Of the six bench-derived
   patterns exactly one construct (`lka-pos`/`lka-verb`, one pattern in two
   spellings) has a sized condition that removes >= 50% of its false
   candidates at >= 1 per KB on the bench's own subject, and that cell's
   measured loss is per-byte VM stepping, not candidate work: the
   condition would sit downstream of `[OPT-HYB-RESEED]`, which is not built.
   Recommendation unchanged: do not build; re-open after RESEED lands and a
   lookaround cell still loses.

## 1. Method

**Derivation of candidate positions** (no compiler involved; the equivalence
is documented, not read off an artifact). Let `P` be the pattern text.

| set | definition |
|---|---|
| `B0` | `P` with every lookaround ERASED except single-character ones (shape a), which [UCP] U2's A_CTX hosts exactly in the DFA and which stay real |
| `C0` | `{ p : B0 matches (anchored) at p }`: the positions the lookaround-free superset admits as a match start, i.e. what the hybrid prefilter hands the VM |
| `E1` | `B0` with each POSITIVE multi-character lookaround (shape b/c/d, computable non-empty necessary set, no trailing quantifier) REPLACED IN PLACE by its one-character condition: `(?=abc)` -> `(?=[a])`, `(?<=xy)` -> `(?<=[y])` |
| `C1` | `{ p : E1 matches at p }` |
| `T` | `{ p : P matches at p }`, the true match starts |

`rejection = (|C0| - |C1|) / |C0|`; `false-removed = (|C0| - |C1|) /
(|C0| - |T|)`. Anchored-at-`p` membership is computed by libpcre2 itself
(exact PCRE semantics), by compiling `(?=(?:X))` and jumping between hits with
one unanchored search per hit. The necessary sets are step 0's own
(`lac_engine.body_first_set`/`body_last_set`, imported unchanged).
libpcre2 is the local 10.48 Homebrew build (not the 10.46 reference; these
positive-lookaround semantics are not version-sensitive). The built
`build/pcrec` (main `31979ed3`, pre-U2) is used only to read
`RX_VM_PREFILTER`/`RX_REQ_BYTE` stamps; the measurement never reads it.

**Population.** The 354 still-VM rows of [UCP] U2's route manifest
(`df93ecf5:tests/ucp/ctxnode_route.tsv`, copied to
`studies/ctx_prefilter_joint/population.tsv`; U2 is not on main). 145
patterns carry a positive multi-character lookaround by the step-0
classifier: step 0's 143 plus the 2 whose body its loose parser could not
resolve. **99 have at least one applicable condition.** The other 46: 27 have
a zero-width-possible body (no sound byte), 2 are the unresolved bodies, and
**17 have a trailing `*` on the lookaround** (min 0, so its body is not
necessary; step 0's census has no quantifier check and its 115 "sized"
occurrences include these, which is a small soundness finding against step 0).
Measured on the 99; the utf8-encoding rows are measured in BYTE mode because a
byte class in libpcre2's UTF mode reads as code points, and stay separable by
their `enc` column.

**Data sources (all read-only, all named).**

| subject | bytes | source | identity check |
|---|---:|---|---|
| `t-256k.bin`, `t-64k.bin` | 262144 / 65536 | pcrec-bench `bench/capability/throughput/` (mixed log+http+source+prose) | sha256 = `manifest_throughput.tsv` (`3cf7b248...`, `d2e4f134...`) |
| `syntax-t-256k.bin`, `syntax-t-64k.bin` | 262144 / 65536 | pcrec-bench `bench/syntax/censustext.py`, regenerated IN MEMORY by `gen_bench_subjects.py` (no bench write; bytecode off) | sha256 = `bench/syntax/manifest_throughput.tsv` (`8b7ca5c5...`, `2611159e...`), refused otherwise |
| `decisions.md` | 548428 | `docs/dev/decisions.md` at `31979ed3` | a real prose+identifier text with dense literals |
| `APPROACH.md` | ~21 KB | the subject step 0 used | for the model-vs-measured comparison on step 0's own subject |

The syntax subject is the one the bench's lookaround cells (`lka-*`, `lkb-pos`)
run on; the store's `t-256k` records for those cells are the same bytes.

## 2. Controls

`studies/ctx_prefilter_joint/results/controls.txt`, run before every
measurement (the script refuses to proceed if any fails):

| control | pattern / subject | expected | measured |
|---|---|---|---|
| positive, lookahead | `x(?=ab)` on `("xa"*1000)+("xb"*3000)` | 4000 cand, 1000 pass, rejection 0.75 | 4000 / 1000 / 0.7500 |
| positive, lookbehind | `(?<=xy)w` on `("yw"*1000)+("zw"*3000)` | 4000 / 1000 / 0.75 | 4000 / 1000 / 0.7500 |
| negative (must reject 0) | `x(?=ab)` on `"xa"*500` | 500 / 500 / 0.0 | 500 / 500 / 0.0000 |
| all-reject | `x(?=ab)` on `"xb"*500` | 500 / 0 / 1.0 | 500 / 0 / 1.0000 |

The soundness control is built into every cell: `T ⊆ C1 ⊆ C0` held in 594 of
594 cells. `T` is computed from the ORIGINAL pattern, so it does not share a
source with the condition it checks.

## 3. Results

All figures from `studies/ctx_prefilter_joint/results/analysis.txt`. A cell is
DORMANT when the prefilter admits no candidate on the subject (the pattern's
own literals never occur), LIVE otherwise.

| subject | cells | dormant | live | rejection min / p25 / med / p75 / max | pooled | false removed (pooled) |
|---|---:|---:|---:|---|---:|---:|
| `t-256k` (capability) | 99 | 64 | 35 | 0 / 0 / 1.00 / 1.00 / 1 | 0.770 | 1.000 |
| `t-64k` (capability) | 99 | 64 | 35 | 0 / 0 / 1.00 / 1.00 / 1 | 0.739 | 1.000 |
| `syntax-t-256k` | 99 | 21 | 78 | 0 / 0.82 / 1.00 / 1.00 / 1 | 0.704 | 0.975 |
| `syntax-t-64k` | 99 | 21 | 78 | 0 / 0.80 / 1.00 / 1.00 / 1 | 0.708 | 0.976 |
| `decisions.md` | 99 | 2 | 97 | 0 / 0.81 / 0.99 / 1.00 / 1 | 0.604 | 0.965 |
| `APPROACH.md` | 99 | 23 | 76 | 0 / 0.78 / 0.99 / 1.00 / 1 | 0.750 | 0.969 |

Distribution of rejection over live byte-encoding cells (share of cells):

| subject | 0 | (0,25%) | [25,50%) | [50,75%) | [75,100%) | 100% |
|---|---:|---:|---:|---:|---:|---:|
| `syntax-t-256k` | 5% | 17% | 0% | 3% | 5% | 70% |
| `decisions.md` | 8% | 14% | 2% | 0% | 33% | 43% |
| `APPROACH.md` | 5% | 16% | 0% | 1% | 29% | 48% |
| `t-256k` | 35% | 0% | 0% | 3% | 0% | 62% |

The distribution is bimodal: a condition either removes essentially every
candidate or nearly none. The NARROW-111 subset (every condition step-0
narrow) behaves like the whole (median 0.996-1.000 on the live cells; the
few wide rows are `pwd-strength-chain`, which has no candidates anywhere).

**A caveat that matters for reading the medians.** 58 of the 78 live cells on
`syntax-t-256k` have ZERO true match starts: most of the population is test
fixtures whose contrived literals never actually match real text, so a
rejection of 1.00 there means "the condition removed candidates that were
never going to match", which is correct and is also the easy case. The
pooled and false-removed columns are candidate-weighted and less flattered.

Absolute density (live cells, per KB of subject): removed candidates per KB
median 1.4-2.0 on the syntax/APPROACH subjects, 0.7 on `decisions.md`, 9-10
on the capability text; 22 of 77 syntax cells remove >= 3 per KB.

## 4. Model versus measured

Step 0's model: survival fraction = product of each necessary set's own
selectivity on the subject. Measured survival = `|C1| / |C0|`. Live byte
cells with a model value:

| subject | n | model rejection (median) | measured (median) | mean absolute gap | model too optimistic | too pessimistic | within 5 pts |
|---|---:|---:|---:|---:|---:|---:|---:|
| `APPROACH.md` (step 0's subject) | 75 | 0.952 | 0.997 | 0.208 | 25 | 13 | 37 |
| `decisions.md` | 96 | 0.947 | 0.996 | 0.244 | 33 | 24 | 39 |
| `syntax-t-256k` | 77 | 0.930 | 1.000 | 0.240 | 21 | 33 | 23 |
| `t-256k` | 34 | 0.963 | 1.000 | 0.368 | 13 | 5 | 16 |

The model's direction was right (the condition is strong) and its magnitude
per pattern is not usable: the gap is a quarter of the whole 0-1 range, in
both directions, which is the position-blindness step 0 named (a byte
conditional on the candidate's own literal is not distributed like the byte
in isolation). Model-only numbers should not be quoted per pattern.

## 5. The six bench-derived rows

Step 0's population has six patterns that are not pcrec's own fixtures. Their
rows on the bench's own syntax subject (`syntax-t-256k`, 262144 B):

| pattern | condition | candidates | true | rejection | false removed | removed / KB |
|---|---|---:|---:|---:|---:|---:|
| `syntax/lka-pos` `item(?= done)` | next in {` `} | 681 | 6 | 0.593 | 0.599 | 1.58 |
| `syntax/lka-verb` (same body) | same | 681 | 6 | 0.593 | 0.599 | 1.58 |
| `syntax/lkb-pos` `(?<=item )done` | prev in {` `} | 665 | 6 | 0.165 | 0.167 | 0.43 |
| `syntax/lka-nonatomic` | next in {`i`} | 681 | 681 | 0 | none false | 0 |
| `capability/pwd-strength-chain` | 4 x wide (255 bytes) | 0 | 0 | n/a | n/a | n/a |
| `utf8/asr-lb-varwidth` | prev in {`a`, `0xA9`} | 0 on this subject | | | | |

(`utf8/asr-lb-varwidth` reads 100% / 90% / 92% on the capability, prose and
APPROACH texts, byte mode, none of them its own subject; the utf8 bench
subjects are generated and not present.) On the four `syntax` patterns the
mechanism removes 59%, 59%, 17% and 0% of candidates; `pwd-strength-chain`'s
lookaheads begin `.*` and admit 255 of 256 bytes.

## 6. Verdict against a D77 trigger

**Threshold applied.** D77 is "build later, under a measured number" and D119
item 4 makes the number a measured gap on real cells. The condition mechanism's
work is fewer VM attempts, so a build trigger needs all three of:

- (T1) a REAL, non-fixture, VM-routed pattern whose sized condition removes
  >= 50% of its false candidates on a bench-class natural subject;
- (T2) at >= 1 removed candidate per KB, because at the scan floor
  (0.0168 ns/B, 17 ns/KB) one avoided VM attempt per KB is already the same
  order as the floor and fewer than that cannot clear a bench IQR;
- (T3) that cell's measured loss is candidate-bound, i.e. attributable to
  the attempts the condition would remove, not to a per-byte cost the
  condition does not touch.

**Result.** T1 and T2 are met, by one construct: `lka-pos`/`lka-verb`
(59.3% of candidates, 1.58 per KB removed). `lkb-pos` fails T1 (16.5%),
`lka-nonatomic` fails T1 (every candidate is a true start), `pwd-strength-chain`
fails both (wide, no candidates). **T3 fails for the one cell that passes
T1/T2.** Bench store, pin `751b9c6d`, `syntax@0.1`, `t-256k`, median of 5
trials, ns/byte (records under `store/records/syntax@0.1/`):

| cell | pcrec auto | pcrec forced-VM | libpcre2 JIT |
|---|---:|---:|---:|
| `lka-pos` | 1.2118 | 1.2096 | 0.1245 |
| `lka-verb` | 1.2115 | 1.2110 | 0.1242 |
| `lka-neg` (same 681 candidates) | 0.4088 | 3.4222 | 0.2276 |
| `lkb-pos` | 2.9486 | 2.9710 | 0.1523 |

`lka-pos` costs 318 us per 256 KB pass; if that were candidate work it
would be 467 ns for each of 681 candidates, which no VM attempt on `item(?= done)`
costs. Auto equals forced-VM to 0.2%, so the prefilter's candidate set buys
nothing today, and `lka-neg`, with the same candidates, is 3x cheaper. That
is the mechanism `docs/dev/utf8_attrib.md` (A) measured: a clamp-free hybrid
does not re-seed from the prefilter after a failed attempt and steps every
position (drafted as `[OPT-HYB-RESEED]`, plan.md, STATE:not-started). The
attribution is inferred from these numbers plus that memo, not from a profile
of `lka-pos` itself. Tightening the candidate set cannot move a cell whose
cost is independent of the candidate set.

**Therefore: the measured joint rejection meets T1/T2 on one bench construct
and fails T3; no D77 build trigger is met.** What would meet it: [OPT-HYB-RESEED]
lands, and a lookaround cell still loses with false-candidate density
>= 1/KB and a condition that removes >= half of them. The measurement that
would show it is the bench re-run of `lka-pos`/`lkb-pos` after RESEED, read
against this document's candidate counts (681 / 665 per 256 KB).

## 7. Limits

- `C0` is the set of positions where the erased pattern matches, an
  over-approximation of what the hybrid's forward+reverse DFA pair actually
  hands the VM (leftmost windows). It is the right upper set for "how many
  candidates the condition could reject"; the real prefilter may admit fewer,
  and today's VM does not restrict itself to it (§6).
- 58 of 78 live syntax cells have no true match on real text; see §3.
- The population is 99 patterns of which 6 are bench-derived; only 4 of the 6
  ran on their own bench subject here (`utf8/asr-lb-varwidth`'s subjects are
  generated and absent, `pwd-strength-chain` is a non-starter).
- The cost side of §6 (T3) rests on bench-store numbers and a prior
  measurement's mechanism; nothing in this lane was timed.
- Single machine (Mac, libpcre2 10.48); positions are not machine-dependent.

## 8. Reproducing

```
python3 studies/ctx_prefilter_joint/gen_bench_subjects.py $SCRATCH/subj   # needs /Users/fdicostanzo/pcrec-bench, read-only
python3 studies/ctx_prefilter_joint/joint.py build/pcrec $SCRATCH/out \
  /Users/fdicostanzo/pcrec-bench/bench/capability/throughput/t-256k.bin,$SCRATCH/subj/syntax-t-256k.bin,\
$SCRATCH/subj/syntax-t-64k.bin,docs/dev/decisions.md,APPROACH.md
python3 studies/ctx_prefilter_joint/analyze.py $SCRATCH/out/joint.tsv
```

`PCREC_PCRE2_PATH` overrides the libpcre2 path (default
`/opt/homebrew/lib/libpcre2-8.dylib`). About 8 s in total, one process.
