# `[OPT-LITSCAN]` S1: a pinned literal run goes to the prefilter, and a dominated pre-check is elided

Lane `s1design`, 2026-09-25, branch `lane/s1design` from main `b5c1423b`
(abi 32). **Design only.** Nothing under `src/`, `cli/`, `lib/` or `tests/`
changed. No darwin clock was read: every number below is either a COUNT
taken off an artifact, or a Ryzen measurement from the bench's own records
(`capability@0.1`, reduced with `pcrecbench.reduce`, as in
`cycle2_admitfix_reading.md` §0.1). Predictions are labelled as predictions.
Instruments: `docs/dev/optloop/s1/` (its `CLAUDE.md` lists them).

Governing rulings: D122 and its ADDENDA 1-3. `compare_stack.md` §6.1 S1 is the
charter. The row is plan `[OPT-LITSCAN]`, which carries Frank's three-arm form
rule from `[OPT-REQPOS]`.

---

## 0. Findings first

1. **Router is (i) plus (ii). Keyword is (ii) alone.** Read off the
   artifacts at `b5c1423b`:
   - `router-prefix-order` (`/user|/users`) ships `RX_DFA_PREFILTER "memchr"`
     on `/`, and a separate `RX_REQ_RUN "2f75736572@0"` pre-check that also
     scans `/`. The run IS pinned. `prefix_k.c`'s walk proves offsets 0..4 are
     exactly `/`,`u`,`s`,`e`,`r`. The k-set model declines it anyway, because
     `/` is the rarest byte and the measured "scan must move" rule
     (`offset_k_skip.md` §7.4) refuses a scan at offset 0. So the prefilter
     never learns the run.
   - `keyword-prefix-order` (`in|instanceof`) ships `RX_DFA_PREFILTER
     "offset-set"` with `OFFSETS "0,1*"`: scan `n` at offset 1, verify `i` at
     offset 0. **That prefilter already carries the run `in`.** The pre-check
     (`RX_REQ_RUN "696e@1"`, scan `n`) is the same search a second time.
     G1 cannot see this, because `dfa_cand_scan_byte` returns −1 for every
     offset-set prefilter (`emit_dfa.c:5429`). Its comment says an
     offset-set "scans a membership table". That has been false since
     `[OPT-K]` required the scan offset to be a singleton.
2. **Both S1 after-programs are known, and both answer-check.**
   - Keyword's S1 program is main's `-fno-req-byte` artifact. That artifact
     is **program-identical to `25b1984f`'s** (the diff is only the header
     line, `.abi`, `.flags` and `rx_info`'s `vars` pair). So its predicted
     after-value is a measured number, not a model.
   - Router's S1 program exists as a hand twin (`s1/mk_twin.py`). It returns
     the same spans as the shipped artifact on all 78 bench subjects.
3. **Counted on the bench's own subjects (`s1/twin_counts.txt`),
   throughput set:**

   | arm | router `memchr` calls | router DFA steps | keyword `memchr` calls |
   |---|---|---|---|
   | (a) as shipped | 77,822 | 78,696 | 88,264 |
   | (c) = `25b1984f`'s program | 39,098 | 79,438 | 44,135 |
   | **(b) S1** | **39,098** | **1,872** | **44,135** |

   S1 removes the duplicate pass on both patterns: 38,724 and 44,129 library
   calls. On router it also removes 77,566 DFA steps. Those are the entries
   at the 38,783 `/` bytes that are not `/user`.
4. **Predicted after-values (§4):**

   | pattern | now | predicted after | vs `25b1984f` |
   |---|---|---|---|
   | router thr | 720.0k / 720.3k ns | **≈337k ns (range 330-394k)** | 0% to −16% |
   | keyword thr | 1,238.5k / 1,239.1k ns | **≈731k ns** | 0% |

   Both land inside or below `25b1984f`'s band on the DFA route. The four
   forced-VM cells are **no-move controls**: those artifacts have no DFA scan,
   and S1 does not touch them. What they are owed is §8's VM seed, not S1.
5. **The same double pass exists well beyond the two witnesses.** Census at
   `b5c1423b` (§6): **34 of 235 bench artifacts and 523 of 3,576 corpus
   artifacts** change program under S1. In every one of them, the same byte
   was being scanned twice. The seven bench cells S1 changes besides the
   witnesses (six capability patterns, §5) all share one property, which
   makes them the carve-out class the mechanism names: **the run is absent
   from the throughput subject**. So today the pre-check is the whole answer,
   and after S1 the prefilter must give that answer at no greater cost.
6. **k64fix interacts, favourably, by construction (§8.1).** The widened G1
   elides only where the prefilter's candidate test IMPLIES the run. So an
   elided pre-check's no-match proof survives in the prefilter. That is
   exactly the property K64 needs on a backtracking route.

---

## 1. The mechanism, as rows

S1 adds **one selection row, one admission conjunct and one extracted
primitive**. It adds no new emitted form and no new loop.

### 1.1 The k-set selection gains a row: `run-pinned`

Today `pcrec_prefix_ksets` (`src/opt/prefix_k.c:386`) is one cost model with
one answer. S1 makes its *decision* a DFA_SELECT-style list. The model is
still computed first, because it is an analysis. The rows then choose among
its answer, the run, and nothing:

| order | row | deny flag | applies | selection it publishes |
|---|---|---|---|---|
| 1 | `run-pinned` | **`PCREC_NO_RUN_PREFILTER`** (new, bit 32, a `#define` per `pcrec.h`'s >30 rule) | see the predicate below | the model's selection (or `{0*}` if it has none), **plus a RUN TERM** `(o, L)`. In-run singleton verifies become redundant and are dropped |
| 2 | `cost-model` | none of its own (`PCREC_NO_OFFSET_SKIP` sits on the `dfa_pfs[]` rows as today) | the model's material, moved scan (today's rule, unchanged) | today's |
| 3 | `none` | — | always | `nsel = 0` |

**The predicate for `run-pinned`:**
1. `Job.req_run.len ≥ 2`.
2. The run is PINNED. Some `o` exists with `o + L ≤ nwalk` such that
   `k[o+i]` is the singleton `req_run.bytes[i]` for every `i`. So the run
   sits at a fixed offset from every match's start, proved by the walk that
   already owns that fact. There is no second analysis.
3. **The scan is the same byte at the same offset: identity.** Call the
   pick's offset `s = o + req_run.idx`. Either the model's selection scans
   offset `s`, or the model selected nothing, `s == 0`, and the offset-0
   filter is the `memchr` form on exactly `req_run.bytes[idx]`.

Clause 3 is what makes S1 "the prefilter already scans the same byte; give
it the run". It never changes WHICH byte an artifact `memchr`s for. It reads
no prior, so it holds under every encoding.

Where the predicate fails, the pre-check stays exactly as today and is
recorded as outside S1 (§6, classes C2, D and V).

**Why a run TERM, not more offsets.** `PCREC_OFSK_MAX_SET` is 4, and router's
run alone needs 5 offsets. The model's greedy search is capped at 4 for its
own measured reason (`offset_k_skip.md` §4.5), and S1 leaves it alone. The
run term is one verify with its own bound, `L ≤ PCREC_MAX_REQ_RUN_EMIT = 8`.
It is also `compare_stack.md`'s P3 shape, "bytes plus offset from the
candidate start", recorded once in `PrefixKSets` beside the offsets it came
from.

**Where it lands.** The row is read through the existing `dfa_pfs[]`
entries `offset-set`/`offset-set-bounded` (`pf_ofs_applies_common` is
`nsel > 0`, which `{0*}` satisfies). No new `DfaPf` row and no new emitted
loop: `pf_block_ofs`'s `<p>_ofsskip` IS the search. Its `sc->k == 0` arm
already exists (`emit_dfa.c:5243`). Only the selection has never produced
it.

### 1.2 G1 widened inside `req_admit`: one conjunct, not a second predicate

`req_admit` (`emit_dfa.c:5514`) keeps its order: NONE, then G2, then G1. G1
becomes:

```
dominated  ⇔  p = the artifact's candidate-scan byte (memchr OR offset-set scan)
              ∧ ( p == q                                     -- identity, any encoding
                  ∨ (L < 2 ∧ memchr form ∧ byte enc ∧ ppm(p) ≤ ppm(q)) )   -- today's clause, unchanged scope
              ∧ ( L < 2 ∨ the selection's verifies ⊇ the run at its pinned offsets )
```

- `dfa_cand_scan_byte` is widened to return the offset-set scan byte (it is
  a singleton by construction, so the −1 there is a stale claim). It gains
  a companion that answers "does the selection verify this run". Both are
  read off the SAME `dfa_pf_of` + `unanch_start` derivation the emitter
  uses, as today.
- **Identity only for runs, and for the offset-set one-byte case.** The
  prior's density clause stays scoped to the one-byte `memchr` form it was
  measured on (F3; D77).
- No axis bit, as §2.29 of `tuning.md` already rules for admission.
  `REQ_WHY`'s four-token set is unchanged, and `"dominated"` now reaches
  offset-set artifacts.

### 1.3 The extracted primitive: P4, the exact compare

`emit_req_run_check`'s `!memcmp(<base>, "<run>", L)` (`emit_dfa.c:723`)
becomes the kit's first primitive, one emitter function
(`compare_stack.md` P4, exact arm). There are two callers:

- **REQ_RUN**, re-emitted BYTE-IDENTICALLY through it. This is the
  implement-then-replace step, and its acceptance is the identity gate
  moving zero artifacts on the extraction commit alone.
- **`ofsk_emit_verify`'s run term.** The run term includes the scan byte,
  exactly as REQ_RUN's compare does. So the two callers pass the same
  `(base, bytes, L)` shape, and gcc sees the same constant-length `memcmp`.

Pay-for-what-you-use holds. There is no K/T mask (S1 is exact-only), no
SWAR, and no form choice beyond `memcmp`. The compare's own form list is
one row today, and a masked or SWAR row joins it at S4.

**P5, the search loop.** The run-pinned prefilter uses `<p>_ofsskip`, so no
second search is introduced. The FLOATING-run pre-check (class D, §6)
keeps its own loop. It is the same search, "next occurrence of the run with
the scan member at `idx`", spelled a second time, which is exactly what
D122 rules out. §9 Q1 asks whether S1 converts it (one more commit, text
change on every class-D/V artifact) or leaves it to the first form row that
would otherwise fork.

---

## 2. The emitted shape (router, as the twin carries it)

Before: the pre-check at the top of `rx_search`, then this prefilter:

```c
if (forward_state == 0 && last_accept_position == (size_t)-1) {
    if (scan_position >= subject_length) return 0;
    const void *q = memchr(subject + scan_position, 47, subject_length - scan_position);
    if (!q) return 0;
    scan_position = (size_t)((const unsigned char *)q - subject);
}
```

After: no pre-check (`RX_REQ_WHY "dominated"`), and the offset-set call it
already has on keyword:

```c
static inline size_t rx_ofsskip(const unsigned char *subject, size_t n, size_t pos)
{
    while (pos + 4 < n) {
        size_t cand;
        const void *q = memchr(subject + pos, 47, n - pos);
        if (!q) return n;
        cand = (size_t)((const unsigned char *)q - subject);
        if (cand + 4 >= n) return n;
        if (!memcmp(subject + cand, "/user", 5)) return cand;   /* P4 */
        pos = cand + 1;
    }
    return n;
}
```

Stamps become `RX_DFA_PREFILTER "offset-set"` and
`RX_DFA_PREFILTER_OFFSETS "0*,1,2,3,4"`. The existing vocabulary covers
this: the run's offsets are listed, and `*` marks the scan. `0*` is a new
VALUE in that domain, since today's selection can never scan offset 0. It
gets a spec sentence (§7).

---

## 3. Answer identity

A prefilter may only skip positions that cannot start a match. A pre-check
may only answer NOMATCH where no match exists. S1 touches one of each.

**The run-pinned skip refuses exactly the positions that cannot start a
match.** Every refusal is one of two tests failing:
- the scan byte at `cand + s`, or
- one byte of the run at `cand + o .. cand + o + L − 1`.

Each of those bytes is a singleton set of `prefix_k.c`'s walk at its
offset. The walk's soundness argument (its header, "WHY IT IS SOUND") is
universally quantified over the candidate start and the preceding byte.
The walk passes assertions as though they held, which can only widen a
set. So a failed byte is a proof that no match begins at `cand`. Three
facts complete the argument, and all three are inherited unchanged from
`[OPT-K]`:
- the landing state (reseeded where the machine seeds, `pf_emit_ofs_reseed`);
- the D11 bounded variant (a miss clamps to n−1, with no early return);
- the `pos + maxk < n` loop guard. It also closes K27's
  `memchr(NULL, c, 0)`: `n > 0` is implied.

The only new element is a scan at offset 0. That offset is `k0`'s own
single `memchr` byte, by clause 3. So the landing byte is one the step
provably leaves the start state on, which is the invariant that
"offset 0 is always a member" exists to keep (`prefix_k.c`, the
comment above the verify selection).

**The elision is a check not run.** It can only remove a NOMATCH the engine
below returns anyway (§2.29 of `tuning.md`). The stronger property G1' adds
is that the elided NOMATCH is still reached WITHOUT an attempt:
- The window lacks the run, so no candidate passes the prefilter's run
  term. Any candidate `c ≥ pos` with `c + maxk < n` would put the run at
  `c + o`, inside `[pos, n)`.
- The first skip therefore returns `n`, and the entry returns 0 (or clamps
  to n−1 under a view).

This is why §8.1's K64 interaction is safe.

**Verification the implementation owes:**
- `make test-axes AXES="-fno-run-prefilter -fno-offset-skip -fno-req-run -fno-req-byte"`
  must be answer-identical over the corpus.
- A corpus `.rxt` witness file, oracle-verified by python3 `re`, covering:
  a run at subject start and end, `cand + maxk == n − 1`, a failed run at
  every scan hit, a run straddling `startpos`, the empty and NULL subject,
  and a `$`-bearing bounded form.
- `make ubsan`/`make asan` on both axes, for the new offset-0 `memchr`.

---

## 4. Cost model and predicted after-values

**Method.** `cycle2_batch2_reading.md` §4.1's method: counts off the
artifact times the constants the cycle-2 readings solved on the bench box.
- `c_call` = 7.72 ns per `memchr` call.
- 0.016794 ns per scanned byte.
- The per-step constant is solved here from router's arm (c), whose program
  `25b1984f` measured: 393,757 ns.

**Router, arm (c) decomposed.**
- 39,098 × 7.72 = 301.8k ns for the calls.
- ~1.37M B × 0.0168 = 23.1k ns for the bytes.
- That leaves 68.8k ns over 79,438 DFA steps: **≤ 0.87 ns per step**. It is
  an upper bound, because per-call and reverse-pass costs are in the
  residual too.

**Cross-check against arm (a), the shipped artifact.** The model predicts
(a) − (c) = 38,724 × 7.72 + 23.1k + the in-loop `memcmp`s = 322k ns. The
bench measured 326.2k ns. That leaves ~4k ns for 38,724 inlined `memcmp`s,
**≈ 0.1 ns each**. The model reproduces the shipped cost.

**Router, arm (b), S1.**
- The same 39,098 calls and bytes as (c).
- 77,566 fewer steps.
- ~38,786 failed run compares at ~0.1 ns each.

| config | now | predicted (b) | vs now | vs `25b1984f` |
|---|---|---|---|---|
| router thr auto-caps | 719,995.6 | **337k** (330k if the whole residual is step cost; **393.8k floor case** if the saved steps were free) | −53% | −14% (floor 0%) |
| router thr auto-nocaps | 720,273.3 | **337k** (same range) | −53% | −14% |
| keyword thr auto-caps | 1,238,485.2 | **731,121** (`25b1984f`'s measured value: the SAME program) | −41% | 0 |
| keyword thr auto-nocaps | 1,239,078.3 | **731,390** | −41% | 0 |
| router srch auto ×2 | 711.9 / 712.7 | ≤ now: 94 → 77 calls over 76 calls | ≤ 0 | — |
| keyword srch auto ×2 | 733.6 / 732.5 | 733-774, **inside the srch band (−3.8..+11.9%)** | ≤ +5.6% | 0 |
| router/keyword thr+srch **vm-caps, vm-in-caps** (8 cells) | 4.44-4.64M thr | **unchanged**: no DFA scan, `REQ_WHY "emitted"`, program-identical save the abi line | 0 | +9.2..10.7% (owned by §8.2) |

On keyword srch: the program equals `25b1984f`'s, and the counts say 9
FEWER calls. The 774 → 733 difference between those pins is therefore
drift, not the pre-check. The prediction is "within band".

**The one real uncertainty is router's (i) share, 0 to −14%.** It is the
`bignum` question (`offset_k_skip.md` §7.4): does a verify that removes loop
ENTRIES buy anything measurable when the scan byte is unchanged? On
`bignum` it did not. Router differs in two ways:
- the scan is already `memchr` on a 1-in-35 byte, not a table walk over
  80% of the bytes;
- the saved work is 77,566 steps against 39,098 calls, not steps interleaved
  with every byte.

The acceptance keeps the two apart (§5): (ii) is the hard bar and (i) is
the measured question. Arm (b) − (c) answers it directly.

---

## 5. Acceptance cells, and the carve-outs named from the mechanism

**Targets** (D119 rule 4: median gain > IQR, then the band):
- router thr, auto-caps and auto-nocaps: must land at or below `25b1984f`'s
  393.8k plus the band (+6.75%). (ii)'s bar.
- keyword thr, auto ×2: the same bar, predicted at 731k.
- **(i)'s question**, router (b) against (c): reported as a number, not as a
  bar.

**No-move controls.** These artifacts are program-identical save the abi
line (the census and the stamps confirm it before the window):
- router/keyword vm-caps and vm-in-caps, thr and srch;
- `nested-comment-rec` ×4 (class V);
- `wild-secrets-github-pat` vm ×2 (V).

**Carve-outs, derived from what the mechanism does.** S1 does three things:
it moves a whole-window dismissal from the pre-check into the prefilter, it
adds a verify per scan hit, and it drops a pass. Each hazard follows from
one of those, and each is named here with the members it has:

| hazard, from the mechanism | who has it (bench, both auto configs) | today thr / srch (auto-caps) | predicted |
|---|---|---|---|
| **H1. The pre-check WAS the whole answer** (the run is absent from the subject), and the prefilter must now dismiss at the same cost. Same byte and same stream by clause 3; the verify replaces the pre-check's own `memcmp` | `wild-secrets-slack-webhook-url` (C1, **a 0.77× WIN**); `wild-secrets-github-pat` (C1); `file-ext-order` (B); `wild-semdiv-altorder-foo-foobar-rustregex` (B); `wild-semdiv-dollar-trailing-newline-pcre2` (C1). Run occurrences in the throughput set: **0 for all five**; scan hits 39,095 / 7,861 / 19,436 / 24,889 / 6,569 | 347.7k / 1,201; 129.3k / 1,091; 260.6k / 683; 358.3k / 647; 26.1 / 629 | = now ± band. Per hit, the verify is one `memcmp` either way. C1 adds the model's offset-0 test ahead of it, which fails first on most hits |
| **H2. A run-dense subject**: every scan hit starts the run, so the verify saves nothing and costs ~0.1 ns per hit | none in the bench (router 0.8%, keyword 21% of hits) | — | a corpus-only hazard. Its size bound is hits × 0.1 ns |
| **H3. A one-byte pre-check dropped from an offset-set artifact** (class E): one `memchr` call per `rx_search` removed | `wild-validator-uuid-grok` | 82.4k / 776 | ≤ now (the `json-array-begin` −24.7% shape, scaled by its call count) |

**Not a carve-out, and why.** The WAF cells are not affected:
- `942270`, `942160`, `942140` and `942360` are either `byte-class`
  prefilters with no run (`REQ_RUN none`) or have no prefilter at all, so
  none of them is in classes A, B, C1 or E;
- `942500-comment-obfuscation` is class D (its run is floating) and is
  unchanged.

S1 absorbs nothing of S3/S4. `union-select`'s caseless run is invisible to
`reqbyte.c` and stays S4(a)'s (`waf_attribution.md` §0).

---

## 6. Census: which artifacts change

`s1/census.py` drives a probe build (`s1/probe_patch.py`, scratch only). The
probe prints, per compile, the facts §1's predicates read, off the emitter's
own derivations. Populations are the reqpos census's:
- the bench's 235 compilable patterns (14 refused), under `--features all` and
  `--no-captures` (identical counts);
- the corpus's 3,576 compilable `.rxt` rows, `--features all`, with row
  options not applied (a prediction, not the gate).

Output: `s1/census.tsv` and `census_summary.txt`.

| class | what S1 does | bench (per auto config) | corpus |
|---|---|---|---|
| A: run pre-check; the selection already verifies the pinned run (keyword) | elide | 3 | 79 |
| B: run pinned; no k-set; scan@0 == the `memchr` byte (router) | run-pinned `{0*}` + run term; elide | 12 | 71 (+3 whose pick is not the `memchr` byte, excluded by clause 3) |
| C1: run pinned; the k-set scans the pick's offset | add the run term; elide | 15 | 120 |
| E: one-byte pre-check; offset-set scanning the same byte | elide | 4 | 253 |
| **program changes** | | **34** | **523** (14.6%) |
| C2: run pinned; the k-set scans a different run member (the "scan must move" rule pushed it off the offset-0 pick) | unchanged, recorded | 12 | 35 |
| D: floating run | unchanged | 14 | 32 |
| V: no DFA scan (VM without hybrid) | unchanged | 13 | 71 |

Every artifact moves in the whole-file pin anyway, through the abi bump.
The "program changes" row is what the D76 program-region comparison and
the Linux window see. C2 is S1's honest residual: the same double pass, on a
DIFFERENT byte of the same run. Resolving it needs a density judgement
between two run members, and nothing has measured one (§9 Q2).

---

## 7. Stamps, abi, spec, sabotage (D76/D80/D94)

- **abi: ONE bump**, to the next number after main's at landing. k64fix
  already takes 33, so this is probably 34. The site list is every reader
  of the number, found by grep (D94): the `PCREC_ARTIFACT_ABI` constant,
  the spec's change logs, `tests/resource/run_resource_tests.sh`'s pin and
  the identity gate's (B) pin. Then run registry, codegen and rxtsource,
  as the D94 addendum requires.
- **Axis:** `PCREC_NO_RUN_PREFILTER` (bit 32, `#define`), `-fno-run-prefilter`.
  - Masked out of `rx_info.flags` via `strategy_denials`, for
    `PCREC_NO_OFFSET_SKIP`'s reason (it changes no answer).
  - It joins `tests/registry/axes_registry_check.sh` and
    `tests/axes/run_axes.sh`, which grep `PCREC_BIT(` shapes; bit 32 is
    the first `#define`d bit they meet after 31.
  - The denied build of a B artifact is TODAY's artifact, pre-check
    included, which makes it a D82 control rather than a third variant.
    C1/A/E elisions are not denied by it. They are admission, which has no
    axis (§2.29).
- **Spec hunks (D80), in `docs/spec/tuning.md`:**
  - §2.29 G1's paragraph becomes §1.2's rule;
  - the `[OPT-K]` section gains "the scan may be offset 0 when a pinned run
    selects it, and the run is verified as one term outside the k-set cap
    of 4";
  - `OFFSETS`' value domain gains `0*`;
  - a new §2.30 for the flag;
  - `match_api.md` §6.3 carries the OFFSETS sentence if it restates the
    domain.
- **Sabotage** (numbered after the highest S-id on main at landing, S274 if
  k64fix is in):
  - (a) the run term compared at `cand + o + 1`: answer-detectable,
    lost matches;
  - (b) the run term one byte longer than proved: answer-detectable, the
    S268 mirror;
  - (c) G1's implication conjunct dropped: structural, a class-C2/D witness
    whose `REQ_WHY` must read `"emitted"` (`run_prechecks.sh` §6).
  - Each row carries a reach witness ([MECH-REACH]).
- **Existing anchors that move:** S267/S268 anchor in `emit_req_run_check`.
  The P4 extraction moves their source lines, so re-anchor them from
  `git show HEAD:` and re-verify intent. S269/S270 (G1/G2) anchor in
  `req_admit`, which S1 and k64fix both edit.
- **`compare_stack.md` updates in the same change:**
  - §2.3's `emit_req_run_check` and `ofsk_emit_verify` rows name P4;
  - §2.5's G1 row loses "blind to an offset-set scan";
  - §5's "sites that keep their own form" gains the floating pre-check
    loop, with the reason, unless §9 Q1 converts it.

---

## 8. Interactions

### 8.1 k64fix (unmerged, abi 33)

k64fix narrows G2's VM arm (`req_route_one_attempt`): a VM artifact now
declines only where its one attempt is LINEAR (an exact hybrid, or
frameless). The pre-checks it hands back fall through to G1. S1's G1 fires
only where a DFA scan exists AND its candidate test implies the run. By §3,
the elided pre-check's NOMATCH is then reached with zero attempts, which is
the no-match proof K64 exists to keep.

**One pre-existing gap sits beside this.** Today's one-byte density clause
(`p ≠ q`, `ppm(p) ≤ ppm(q)`) elides WITHOUT implication. On a VM hybrid
whose prefilter is count-collapsed (not exact), that could reopen K64's
give-up on an unanchored pattern where `q` is absent and `p` is present.
S1 does not widen that clause. It is reported here for k64fix / Frank, and
it is not verified with a witness (§9 Q4).

**Textual:** both lanes edit `req_admit`'s neighbourhood and re-anchor
S269. Whichever lands second rebases.

### 8.2 The forced-VM residual is a different mechanism: the VM seed

The four forced-VM cells (+9.2..10.7% over `25b1984f`) and
`json-array-begin`'s forced-VM pair (+15/+16%) have no DFA scan, so there is
nothing for the pre-check to be dominated by. Their lever is D122 item 3:
the pre-check's hit bounds the leftmost match start from below.
- The first run occurrence is at `r ≥ search_from`, and the run is pinned
  at `o`. So `attempt_position = max(search_from, r − o)`.
- That is sound, because no match can start before `r − o`.

On router, one attempt per call would replace every attempt from
`search_from`. A rough prediction is the pre-check's own ~330k ns, against
4.46M today. But it needs the pinned offset ON THE VM ROUTE, where
`prefix_k.c`'s walk is not run today, and it is `[OPT-REQPOS]`'s declined
tier 2 re-opened. **Not S1.** It is named as the next row, with this
paragraph as its trigger (§9 Q3).

### 8.3 What S1 must not absorb

- No caseless, no K/T mask, no cube: S4.
- No SWAR form row: S1 adds no form at all.
- No change to the model's constants or its "scan must move" rule for
  patterns without a pinned run.
- No multi-literal. D class stays.

---

## 9. Open questions for Frank

1. **Convert the floating-run pre-check (class D, and the V artifacts) to a
   `<p>_ofsskip`-shaped call of the one search block, IN S1?**
   - For: after S1 it is the only second spelling of the same search, which
     is D122's named failure.
   - Against: its text changes on ~100 corpus artifacts and on the V
     no-move controls (`nested-comment-rec`, the forced-VM witnesses), for
     no measured gain. The controls would stop being program-identical.
   - **Recommendation:** yes, as S1's LAST commit, inside the same abi
     event, with those controls re-scored as "changed program, predicted
     equal". If you prefer the controls kept clean, defer it to S2, the
     first row that would otherwise fork the loop.
2. **Class C2** (12 bench, 35 corpus): the same double pass, but the
   prefilter scans a different run member than the pick. Leave it (S1 is
   identity-only; D77), or let the run-pinned row re-point the scan to the
   pick? The second choice overrides the measured "scan must move" rule on
   these patterns, and nothing has measured that.
3. **The VM seed (§8.2):** open it as its own row (tier 2's re-opening,
   with the forced-VM residual as its measured need)? Or is the forced-VM
   testee not a population you want optimized?
4. **The one-byte density clause without implication (§8.1):** should
   k64fix's lane, or a probe, try to build a K64-sibling witness on a
   collapsed VM hybrid before S1 lands?

---

## 10. The Linux measurement request (ready to append to the bench inbox; the manager sends it)

> **I-1xx ([OPT-LITSCAN] S1 acceptance, after the lane lands).** Pin: the S1
> merge. Testees auto-caps, auto-nocaps, vm-caps, vm-in-caps;
> `capability@0.1`, both regimes. **Arms:** (a) the base pin (`b5c1423b`, or
> k64fix's if it has merged); (b) the S1 pin; (c) the S1 pin with
> `-fno-run-prefilter -fno-req-run`. That is router's `25b1984f` program:
> arm (c) was verified program-identical at `b5c1423b`, and the lane
> re-verifies it at S1. **Targets:** router and keyword thr, auto ×2. Bar:
> (b) ≤ `25b1984f` + band. Predicted router 337k (range 330-394k), keyword
> 731k. **(i)'s question:** router (b) against (c), reported as a number.
> **Carve-outs (H1/H3):** slack-webhook-url, github-pat, file-ext-order,
> foo-foobar, semdiv-dollar, uuid-grok, auto ×2, both regimes. Bar: within
> the band of (a). **No-move controls** (program-identical, verify the
> stamps first): router/keyword/github-pat/nested-comment-rec on
> vm-caps/vm-in-caps. Answer-check every arm before timing (the O-51
> precedent). The lane's twin (`s1/mk_twin.py`) matched the shipped spans
> on 78/78 subjects.

A PRE-implementation twin run is NOT requested. Keyword's after-program has
already been measured (it is `25b1984f`'s), and router's arm (b) comes free
with the landed build. D77: the landing is the measurement.

---

## 11. The four lenses

| lens | reading |
|---|---|
| specific vs general | General: every pinned run with identity (523 corpus artifacts), not a router clause. The one special-shaped piece is the run TERM, and it is P3's general record |
| core vs derived | Derived from existing facts only (the walk's singletons, `Job.req_run`, axis B's selection). No new analysis |
| applicable vs assumption-changing | One assumption relaxed, "the scan never sits at offset 0", and only where a pinned run selects it. That is what the §7.4 rule's own reason ("a verify only removes entries") does not cover: a whole duplicate pass is also removed |
| fits the architecture vs refactor | Fits: a row in the selection, a conjunct in `req_admit`, and one emitter function extracted with byte-identical re-emission |
