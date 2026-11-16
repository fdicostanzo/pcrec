# R-45 reply draft: window spans of up to 4095 positions ([COVER-CAP] stage 2)

Status: DRAFT for the kit manager (lane r45, 2026-11-16, design only; no code, no timing).
Tree read: main `ea83fbc01` (worktree `worktrees/r45`). The request is
`memfn/docs/requests.md` R-45; pcrec's side is `docs/design/cover_cap.md` §11 (rev 5.2),
reviews r13 (`docs/dev/reviews/2026-11-15-r13-covs2d.md`) and r15
(`docs/dev/reviews/2026-11-15-r15-covs2e.md`), and r9's EMITTED-2
(`docs/dev/reviews/2026-11-15-r9-covs1.md`). The kit's 2026-11-15 ideas entries (long exact
spans (1)-(4), the owner's direction verbatim, the EMITTED-2 fact) sit on the kit branch
`lane/memfn-k1108` (`git show lane/memfn-k1108:memfn/docs/ideas.md`, from line 797), not on main.

Sizes below come from one probe, compiled at this tree (gcc 15.2, x86-64, `-std=gnu11`): it
includes `memfn/src/window.c` so the kit's internal types are visible too, and prints
`sizeof`. The probe and its proposed-layout twin are lane scratch
(`/var/tmp/pcrec-pcrec/scratch/memfn/r45/sz.c`, `prop.c`). Today's figures: `mf_class`
2,932 B (`proven` 1,312 B); `mf_result` 3,000 B; `mf_wspan` 1,164 B; `mf_walt` 16 B;
`mf_wreply` 532 B; `mf_site` 2,968 B; `mf_pred` 2,808 B. Internal: `wf_pos` 76 B, `wf_alt`
6,064 B, `wf_dec` 12,568 B, `struct wf_plan` 3,424 B, `wf_legacy` 5,016 B.

## Goals

In priority order; a conflict goes to the higher one.
1. **A cover of up to 4095 positions passes the seam.** pcrec's three conjuncts and its
   `_Static_assert` hold at `k` = 4095. Who benefits: pcrec's stage 2.
   Measurable: `cc_fits` is true at 4095 on the combined branch.
2. **No holder of a seam struct grows.** pcrec's stack holders stay at or below today's
   23,456 B for 8 classes; no kit frame goes over 4 KB. Who benefits: every compile.
   Measurable: `sizeof`, and `run_link_checks.sh`.
3. **Zero movers at pcrec's default width (32).** Who benefits: users wanting stability.
   Measurable: the stage-2 sweep's mover count, 0.
4. **The three forms are decided by cards, not by a constant.** Who benefits: the owner's
   dial. Measurable: every `h` is labelled MEASURED, DERIVED or UNMEASURED.

Non-goals: no form design beyond naming the three forms; no near-miss form (ASK (4) asks a
reading only); no timing in this lane.

## 0. The answer in one paragraph

Yes. The kit carries spans of up to 4095 positions on EVERY window span, through one general
carrier with no per-site-kind bound. The span's per-position arrays move OUT of the
statement's struct into storage the host owns. The proof becomes a COUNTED range in the
caller's arena, sized by the site's own stated extent, under a build-time ceiling that
pcrec's `_Static_assert` can read. The kit's working state is sized by each site's extent,
never by the ceiling. `MF_MAX_TERM` and `MF_WMAX_SPAN` stay 32 and are DECOUPLED from the
span length. Because the per-position arrays leave the structs, every class and statement a
host holds gets SMALLER, not larger: `mf_class` goes from 2,932 B to 1,640 B, and
`mf_wspan` from 1,164 B to 32 B. This is one `MF_SITE_ABI` event (29 -> 30) that carries
`MF_CLASS_V` 10 -> 11, inside the one joint pcrec `abi` event. The three forms' cards are
specified in §3; their numbers need a box window and stay OPEN. Dense near misses (§4) are
a complexity-class question: O(n·k) against the engine's O(n). They are the one regime
where a long cover can lose by orders of magnitude.

## 1. ASK (1): can the statement and the reply carry 4095? The three bounds

**Answer: yes. The kit declares the three bounds below. Each applies to EVERY window span,
not only to a REPORT site's span 0. The proof range is a per-reply count under a build-time
ceiling.**

| bound | name | value | kind | applies to |
|---|---|---|---|---|
| positions per span | `MF_WSPAN_POS` | 4095 | SHAPE BOUND, CHOSEN: the widest span pcrec states (the cover's `k`, its anchored ceiling less one). TRIGGER: a statement past it, refused naming `len` | every window span |
| reach | `MF_WREACH` | `MF_WSPAN_POS + 1` = 4096 | SHAPE BOUND, DERIVED: the longest span plus its after-context position, which is the widest statement pcrec makes. TRIGGER as today: a statement past it, refused naming `start` | every window span |
| proof range forward (ceiling) | `MF_MAX_FWD` | `MF_WREACH` = 4096 | SHAPE BOUND, DERIVED: every offset a site may state lies below it | every reply |
| proof range forward (per reply) | `mf_class.proof_n` | `stated_end - MF_PROOF_LO`, where `stated_end` = 1 + the largest offset the site states (the after-context included), with `stated_end >= 1` | a COUNT, per reply | every reply |

What this means for pcrec's three conjuncts and its seam assertion:
- At `k` = 4095, `cc_fits` (`src/gen/known.c:336`) holds: `4095 <= 4095`,
  `4096 <= 4096`, `4095 < 4096`.
- B2's `_Static_assert` reads the three names above, so a `-D` raise of the ceiling fails
  the build. That is cover_cap.md §11.1 B2 as written.

**Why every span, not REPORT-only (the general form; memory
`pcrec-general-mechanisms-not-special-cases`).**
- The 32 and 64 are not facts about non-cover sites. They are the CARRIER's sizes
  (`memfn.h:650-667`), DERIVED from pcrec's own truncation bound `PCREC_MAX_REQ_RUN_SCAN`.
  Once the carrier holds 4095, a second, smaller name for "other sites" would be a parallel
  bound with no measured or derived source.
- The bound pcrec actually relies on for its own non-cover sites is pcrec's own
  construction. pcrec already asserts it against its own constants:
  `_Static_assert(PCREC_MAX_REQ_RUN_SCAN <= MF_WSPAN_POS, ...)` (`emit_dfa.c:1446`, still
  true at 4095). Its prefix walk is bounded by `PCREC_PREFIX_K_MAX` (24).
- So r15 FIND-11's worry ("every non-cover site's bound silently becomes 4095") is the
  intended reading. `window_bounds_check` (`src/gen/memfn_sites.c:590-600`) asks whether a
  statement fits the KIT, and every statement up to 4095 now does. pcrec's B4 does not need
  to thread a site kind in. B4 shrinks to re-reading the same three names.
- If pcrec wants to keep its non-cover sites at 32 as a pcrec invariant, that is a pcrec
  assertion on pcrec's constants at its own writers. It is not a kit bound. This is OPEN Q1.

**What the kit owes on its side, for a general carrier (K96: each row checks its own
contract).** Some kit paths keep a 32-shaped limit internally. Each one becomes a ROW
CONTRACT that declines, or a site refusal that names the field. None of them is a seam
bound, and pcrec states none of them longer today:
- E-func and E-stmt translate the plan into an old-field site, and `legacy_ok` already
  declines more than `MF_MAX_TERM` compares (`window.c:1463`).
  - `wf_legacy`'s run and mask buffers are sized `[MF_MAX_TERM][MF_WSPAN_POS]`
    (`window.c:1440-1441`). At 4095 they would be 262,080 B per prepare, so they get their
    own legacy bound (32, the translated rows' contract), and `legacy_ok` declines a run
    longer than it.
  - The translated ranking stays under `MF_RANK_MAX` 32 (`memfn.h:286`). A longer R
    declines the legacy rows and reaches E-find or the floor.
- The pre-check's run part: `mf_run_reply`'s `scan`, `ver_lo` and `ver_len` are `uint8_t`
  (`memfn.h:1280-1285`), so they widen to `uint16_t` (§5). `run_part_terms` allocates by
  the run's length rather than `2 * MF_WSPAN_POS` (`window.c:3013`).
- D-hors's shift table is `uint8_t`, held by `_Static_assert(MF_MAX_SPAN_POS < 256, ...)`
  (`window.c:1850`). The shift becomes `uint16_t`. That is a 512 B table, built once per
  plan.
- C-run's grouping caps groups at `MF_MAX_TERM` (`window.c:1786`; `int8_t grp`,
  `window.c:1354`, `:1772`). Past the cap, positions stay lone tests, which is correct and
  silent. That cap is decided by the forms of §3 (a run of one set becomes ONE loop, not 32
  compares), and the grouping index widens with them.

**The proof range: a count, under a ceiling.**
- **Why a count.** A constant range of 4,104 rows on every reply would be 131,328 B per
  class: on pcrec's stack 8 times (cover_cap.md §11.1), in `mf_result`, and once per class
  answer for EVERY site, short ones included. That breaks pcrec's 442,368 B stack budget
  and the kit's 4 KB frame bar (`memfn/CLAUDE.md`, "Compile-time stack").
- **What the count promises.** The kit's text tests no offset outside the site's stated
  extent. E-find and the floor test plan offsets only (`window.c:3287-3313`), and plan
  offsets are stated positions. So "nothing proven outside the range" is TRUE BY
  CONSTRUCTION, not a truncation. For a cover, `proof_n = k + 1 + MF_MAX_BACK`: the range
  always reaches offset `k`, the after-context.
- **pcrec's check.** pcrec's B5 comparison then reads `[MF_PROOF_LO, MF_PROOF_LO +
  proof_n)` and treats every offset outside it as all ones. Its want past `k` is all ones
  too.
- **The short-range internal error** ("the kit's proof range ends at offset %d, before the
  cover's after-context at %d") stays as pcrec's defence. The kit checks the same promise
  before it returns, as its own refusal: `proof_n` must cover the stated extent. Its
  control is a kit-tree plant that cuts `proof_n` below `k + 1`. That is cover_cap.md B5's
  per-reply-count branch, filed with §11.6.3's rows.
- **Old-field (non-window) FIND sites.** Their range ends at their terms' extent,
  clipped to `MF_MAX_FWD`, as `term_prove` already clips (`compose.c:406`).

**What retires: `MF_MAX_SPAN_POS` and `MF_MAX_AHEAD`.**
- They exist only to define `MF_MAX_FWD` (`memfn.h:302-315`). `MF_MAX_AHEAD`'s one
  position (the after-context) is now a stated span, so the stated extent covers it.
- Their readers are `memfn.h:653` (`MF_WSPAN_POS`), `window.c:1850` (re-spelled above), and
  pcrec's `known.c:347-351` and `known.h:27`. cover_cap.md A1 removes the pcrec ones
  (`MkEnd` stops copying), plus S1131's plant.
- If A1 has not landed when the kit branch merges, `MF_MAX_SPAN_POS` stays one more release
  as `32`, with a comment naming its last reader. This is OPEN Q4, and its answer is an
  ordering choice.

## 2. ASK (2): do `MF_MAX_SPAN_POS`, `MF_WMAX_SPAN` and `MF_MAX_TERM` stay equal?

**Answer: no. They decouple. `MF_MAX_TERM` stays 32, `MF_WMAX_SPAN` stays 32 under its own
derivation, `MF_WSPAN_POS` becomes 4095, and `MF_MAX_SPAN_POS` retires (§1).**

- **`MF_MAX_TERM` 32** (`memfn.h:277`): the number of terms in one conjunction. Its source
  is pcrec's VM stride and the strided ADVANCE (Q-R10-3), and both are unrelated to span
  length. Its readers are unchanged: pcrec's three (VM stride, term count, ADVANCE stride)
  and the kit's (`ofsskip.c:115`, `gate.c:314,532`, `compose.c:470`, `generic.c:180`).
  `mf_pred.term[MF_MAX_TERM]` (`memfn.h:722`) stays 2,560 B. Raising it to 4095 would make
  `mf_pred` about 330 KB and `mf_site` larger still, on every holder.
- **`MF_WMAX_SPAN` 32** (`memfn.h:658`): spans per alternative, a COUNT of spans, not of
  positions. It is re-derived on its own line, keeping today's derivation text: pcrec's
  widest alternative is the reseed one, at most `PCREC_PREFIX_K_MAX` (24) walked offsets
  plus R, so 25 or fewer. Spelled `32` with that derivation, its value is unchanged, and
  `mf_walt.nspan` stays `uint8_t` (`memfn.h:689`).
- **`MF_WSPAN_POS` 4095**: its own literal, derived as in §1.

**What moves on pcrec's side** (each from cover_cap.md §11.1's lists):
- `form_checks.py` still parses a literal `#define MF_MAX_TERM 32`: no change.
- Mech row S526 loses its premise. It lowers `MF_MAX_TERM` and expects a refusal THROUGH
  `MF_WSPAN_POS`'s derivation, and that derivation no longer exists. Its REACH greps
  `#define MF_WSPAN_POS MF_MAX_SPAN_POS`. Re-aim: plant `MF_WSPAN_POS` 4095 -> 4094 and
  expect BUILD-REFUSED through B2's assertion. That is a new unique witness for the seam
  assertion, and B2 needs one anyway.
- `PM_NPROOF 41` (`tests/memfn/proof_meta.h`) and its `_Static_assert(PM_NPROOF ==
  MF_MAX_FWD - MF_PROOF_LO)` go. The range is now a per-reply count, so the check reads
  `proof_n` against the site it built.
- `G2W_NPROOF 41` (`memfn/tests/g2/g2_win.h:23`), the kit's twin of that pin, goes the same
  way.

## 3. ASK (3): the three forms' cards, per the owner's direction

The forms, read from the owner's words (quoted in R-45; he names them, the kit owns them):
- **I, all inline.** Today's text: one membership test per position in one `&&` chain
  (`window.c:3287-3313`). A stretch of one-member or cube positions is ONE run compare
  (C-run, `window.c:1773-1825`, runcmp's rows).
- **L, all loops.** The span is split into maximal SUB-SPANS of one repeated set, each
  rendered as a loop over its positions against that set; a sub-span of length 1 is its
  one test. For example, `hex{8}-hex{4}-hex{4}-hex{4}-hex{12}` is 5 loops and 4 one-byte
  tests.
- **H(h), inline head, then loops.** The first `h` positions are inline, and the rest
  follow L. `H(0)` is L. `H(h >= k)` is I.

"Repeated sub-spans" with a period above 1 (for example `(ab){500}`) is NOT in the stated
population (mostly runs of one class), so the cards measure period 1 only. Period > 1 is an
UNMEASURED extension: TRIGGER, a census row with a periodic span of 36 or more. D77.

The head `h` is a tuning constant (D149): the cards' OUTPUT, never a guess. The cards are
built to tell two readings apart:
- **(a) death depth.** `h` near the expected depth at which candidates die under the art's
  byte rate, `E[D] = sum_i prod_{j<i} mass(S_j)`, which is about 1-2 for a hex or digit
  class on plain text.
- **(b) code size.** `h` near the length below which the inline chain's size costs
  nothing measurable, about 32 by the owner's 15:00 prediction ("most all rx ... will
  inline due to being under the inline head portion").

If the measured knee tracks (a), `h` is DERIVED from the byte rate and needs no constant.
Otherwise it is MEASURED, labelled with its card.

**The cards** (rows for `memfn/data/cards/kit-synthetic.tsv` and the kit's measurement
script, each added in the build that adds its form; memory
`pcrec-new-method-needs-measurement-card`):

| card | forms | k (shape) | subjects (regimes) | layers | what decides |
|---|---|---|---|---|---|
| C1 crossover | I, L, H(h) for h in {2, 4, 8, 16, 32} | 24, 32 (`[0-9a-f]{k}`, `\d{k}`: stage-1 movers and twins) | hit-dense (all members); DENSE NEAR-MISS (`k-1` members then a non-member, repeated: EMITTED-2's shape); miss-heavy (plain text, death at depth 0-1); uniform random bytes | SIMD-off, and SIMD-on where a level admits it | whether any H/L beats I at k <= 32. If none does, the default leaves today's covers byte-identical |
| C2 population | I, L, H(h), h as C1 | 36 (uuid: `hex{8}-hex{4}-hex{4}-hex{4}-hex{12}`), 40 (`lit-l40`, a literal: the run-compare control), 49, 60 (the census rows' own patterns) | as C1 | both | the knee of `h`; is L/H slower than I in any regime at the population's lengths |
| C3 long | I, L, H(h at C2's knee) | 500, 1000 (`[0-9a-f]{k}`, `a{k}`) | as C1 | both | whether I is ever faster at length (the dial cell's evidence, unlock 2); NOT-WARM where the bench supplies the method (D198 (f)) |
| C4 size | I, L, H | 32, 500, 1000, 4095 (`[0-9a-f]{k}`, `a{k}`) | none (compile only) | both | emitted C bytes against 250,000 / 1,000,000 (the size-cap ladder's silent cliff, R-45 FACT cost), `gcc -O2 -c` time, RSS and `.text`. Recorded, no timing |
| C5 engine reference | none: pcrec's engine route on the same subjects (`--memfn=no-window-search`) | as C1-C3 | as C1 | n/a | the floor every cover form is read against in the near-miss regime (§4) |

**The procedure** (kit timing, unofficial, per `memfn/CLAUDE.md` standing question 1):
- Linux, `taskset`-pinned, calibrated loops, at least 5 launches, median, with A/A
  controls (`lit-l16`) for the noise floor.
- Answers are identical across the forms by construction. G2 checks each form against the
  byte loop over the generated space, and that check is a precondition, not a card.
- **Decision rule, first match, per card:**
  1. A form's answers differ: the form is defective, and nothing is set.
  2. I is faster than every L/H beyond the floor in some regime at some k: report that
     (k, regime) as the dial cell's evidence (unlock 2).
  3. Otherwise: default = H(h), with h the C2 knee.

**Interim default, until the cards run: `h` = 32, labelled in place `UNMEASURED
DEFAULT:`.**
- It is chosen to equal pcrec's width default, so that the joint landing moves NO artifact
  at the default width: every span pcrec states at its default is 32 or shorter, so it is
  all inline, which is today's text.
- Only `--window-search-width` above 32 reaches L. This matches the owner's 15:00
  prediction. It is OPEN Q2: it is a default that gets used, so it must be named rather
  than silent.

**The kit option and the dial.**
- The forms get one `options.def` PAIR row per the D144 item 4 rule. The working name is
  `span-loop` (kit-owned, arch-blind): `no-span-loop` gives all inline (I), and `span-loop`
  forces L/H.
- pcrec's `--tune=N` can carry it as a cell once a card shows I faster (cover_cap.md §11.3,
  unlock 2). The kit never reads the dial.

**What a card needs from the box: OPEN.**
- C1-C3 and C5 are timing runs: a kit window request on the combined branch (cover_cap.md
  §11.4: "not part of this night unless the kit asks for a slot").
- C4 is a non-timing job: boxqueue, no window (memory `pcrec-kit-nontiming-runs-no-ask`).

## 4. ASK (4): the dense near-miss regime (no form asked)

**Reading: it is a complexity class, not a constant factor.** The cover's stream RESTARTs
one byte past a failed candidate (`mf_wstream` RESTART, `memfn.h:1666-1667`; EMITTED-2:
"resumes one byte later"). On a subject where every byte is a candidate and candidates die
deep, each byte is re-tested about `k/2` times:
- **The arithmetic at k = 32.** On EMITTED-2's subject (31 digits + `g`, period 32), the
  candidate at period offset `i` tests `31 - i` positions before it meets `g`. That is 496
  tests per 32 bytes, about 15.5 per byte, against the engine's one transition per byte.
  The x6.65 in instructions (230.7 M vs 1,534.8 M) fits that.
- **Extrapolated.** The cost per byte grows linearly in `k`: about 2,047 tests per byte at
  `k` = 4095. Scaling EMITTED-2's ratio by `4095/32`, that is roughly x850 against the
  engine (UNMEASURED, an extrapolation for scale only).
- **The consequence.** Under `--window-search-width` near the ceiling, a dense near-miss
  subject is the one regime where a long cover can lose by orders of magnitude. The
  stage-2 timing's near-miss cells (cover_cap.md §11.4 B) will see it at 36-60, and C1-C3
  above see it per form.

**What the statement already allows (facts, D157).**
- The kit has every position's set. On a failure at offset `j` with byte `x`, no candidate
  `c + u` with `0 < u <= j` can hold, unless `x` lies in `S_{j-u}`. That is the
  bad-character rule over sets, the same reasoning as D-hors's shift table, which today is
  evaluated only at the window's last offset (`window.c:1846-1862`).
- For a run of one class `S` with `x` not in `S`, the next viable candidate is `c + j + 1`.
  Each byte is then tested about once, which is linear, the engine's class.
- **Coupling with §3.** An L or H loop over a sub-span ends AT the failing offset, so the
  skip's input costs nothing extra in those forms. In form I the failing offset is not
  known: the `&&` chain short-circuits without naming it.
- **This is a reading, not a form.** It belongs in the kit's ideas log as an unevaluated
  entry. Its TRIGGER is C1/C2's near-miss reading of L/H slower than C5 (the engine) at any
  k of 36 or more. OPEN Q3 asks whether a skip after the failing position must ride with
  the first build that admits k > 32 under the option.

## 5. ASK (5): how the statement and the reply carry the longer span, and the abi events

**Design: the per-position arrays leave every seam struct. Statement arrays are HOST-owned.
Reply arrays live in the CALLER's arena (`mf_arena`, already pcrec's: "memory lives until
pcrec's arena dies", `memfn.h:1005-1012`). Each array is a counted list, so the seam still
serializes as text (a pointer to data plus its count is a list; no callbacks).**

| type | today | proposed | storage owner | size today -> proposed |
|---|---|---|---|---|
| `mf_wspan` (`memfn.h:669-685`) | `uint8_t len, core_lo, core_len`; `set[MF_WSPAN_POS][32]`; `table_ref[MF_WSPAN_POS]` inline | `uint16_t len, core_lo, core_len`; `const uint8_t (*set)[32]` and `const uint32_t *table_ref`, each `len` entries | HOST (pcrec's arena; cover_cap.md A1 already points the cover record's sets at arena storage) | 1,164 B -> 32 B per span; the host's arrays are 36 B per position: 1,152 B at k=32, 18,000 B at 500, 147,420 B at 4095 |
| `mf_class` (`memfn.h:1288-1343`) | `proven[41][32]` inline (1,312 B); `mf_run_reply` of `uint8_t` | `proven[]` REMOVED; appended LAST: `uint32_t proof_n; const uint8_t (*proof)[32];` (rows for offsets `MF_PROOF_LO .. MF_PROOF_LO + proof_n - 1`); `mf_run_reply` fields widen to `uint16_t`; `proven0`/`proven_prev` stay by value, COPIED from rows 0 and -1 as today | KIT writes, into the CALLER's arena, during `mf_ask`/`mf_defined`; rows are immutable after return; a by-value copy of the class shares them | 2,932 B -> 1,640 B; arena rows `proof_n x 32`: 1,312 B at k=32 (as today), 16,288 B at 500, 131,328 B at 4095 (cover site only; a short site's rows are fewer than today's 41) |
| `mf_result` (`memfn.h:1346-1372`) | holds `mf_class` | unchanged, holds the smaller class | — | 3,000 B -> 1,712 B |
| `mf_wreply` (`memfn.h:1695-1719`) | `uint8_t nplan`; `plan[72]`, `plan_term[72]`, `plan_test[72]` inline; `uint8_t run_len` | `uint16_t nplan`; `const int32_t *plan`, `const uint16_t *plan_term`, `const uint8_t *plan_test` (`nplan` entries); `uint16_t run_len` | KIT writes into the CALLER's arena (a FRAMED or NONE ask alike) | 532 B -> 136 B; arena 8 B per plan entry: 256 B at k=32, about 32 KB at 4095 |
| `mf_walt`, `mf_pred`, `mf_term`, `mf_site` | — | unchanged (`MF_MAX_TERM` 32, `MF_WMAX_SPAN` 32) | — | unchanged |

**Stack and arena consequences for pcrec** (its holders, from R-45's FACT):
- **The 8 by-value `mf_class` stack holders** take 13,120 B, down from 23,456 B.
- **The 3 `mf_wreply` stack locals** (`emit_dfa.c:4670, 7757, 16318`) take 408 B, down
  from 1,596 B. The cover's REPORT site needs no stack growth anywhere.
- **The arena** gains `proof_n x 32` B per class answer of a long site. At k = 4095 that is
  131 KB per answer of the cover site, for the attempt's life, and the size ladder repeats
  it per attempt.
- **For comparison, an inline layout at 4095** would make the class 132,948 B: 8 x that is
  1.06 MB on the stack, against the 442,368 B budget. A by-value layout is therefore not
  viable.
- **A sparse or run-length proof is designed, not built.** It would list `(lo, len, set)`
  runs, which is about 40 B for a run of one class and 9 runs for a uuid. Its worst case is
  no better than dense (a 4095-position literal of alternating bytes is 4095 runs), so dense
  is the simple form now. TRIGGER: pcrec's stage-2 compile-cost record (cover_cap.md §11.1,
  `covcost2` on `a{4095}` and `[0-9a-f]{1000}`) shows the arena's share of max RSS material
  against pcrec's compile memory. D77.

**The kit's own working state** (internal, no seam event, but it is most of the build):
- Every array sized by `WF_NPOS` / `MF_WPLAN_MAX` becomes sized by the alternative's
  stated extent, allocated per decision:
  - `wf_alt.p[]` (`window.c:183`);
  - `wf_dec.poff[]`/`pterm[]` (`:219-220`);
  - `struct wf_plan`'s `off`/`set`/`core`/`table`/`grp` (`:1323-1354`);
  - `wf_fpart.plan_test` (`:2556`);
  - the stack `int key[WF_NPOS]` in `find_groups` (`:1775`).
- These are allocated through the existing paths: the art arena at `:2475`, and `calloc`
  at `:2768` and `:2816`.
- **Why per extent.** Merely raising the constants would make `wf_dec` about 644 KB
  (`wf_pos` 76 B x 4,104 x 2 alternatives, plus the plan arrays), calloc'd and zeroed on
  EVERY window decision, short sites included. It would also make `find_groups`' stack
  array 16,416 B, against the 4 KB bar.
- `wf_legacy` keeps its own 32-bound (§1).
- No new frame over 4 KB. `run_link_checks.sh` holds that, and the peak line in
  `memfn/CLAUDE.md` is re-read at the build.

**abi events.**
- **`MF_SITE_ABI` 29 -> 30**, which carries:
  - `mf_wspan`'s and `mf_wreply`'s layouts;
  - the new values of `MF_WSPAN_POS`, `MF_WREACH`, `MF_MAX_FWD` and `MF_WPLAN_MAX`;
  - the retirement of `MF_MAX_SPAN_POS` and `MF_MAX_AHEAD`;
  - `MF_WMAX_SPAN`'s own spelling.
- **`MF_CLASS_V` 10 -> 11**, inside it: `proven[]` replaced by `proof_n`/`proof`, and
  `mf_run_reply` widened.
- **`MF_VOCAB` unchanged**: no op, handoff or term kind.
- **pcrec's `abi`.**
  - At the default width the interim `h` = 32 (§3) moves no kit byte, so the seam change
    by itself moves no artifact.
  - The JOINT landing is still ONE pcrec `abi` event, because pcrec's own stage 2 moves
    emitted text (cover_cap.md §11.1 "abi events").
  - If C1 sets `h` below 32, the stage-1 covers' bytes move in the same commit. That is a
    kit byte move, which is a pcrec abi event in the same commit (`memfn/CLAUDE.md`), with
    its `options.def` deny row.
- **Stamps.** L and H at SIMD-off are scalar forms, so `<PREFIX>_MEMFN_FORMS` reads `none`
  at SIMD-off as today (integration.md §18.1). A SIMD-on loop is a carried level like any
  vrun row.

## 6. The three standing questions (docs/design/CLAUDE.md)

1. **Measurement regime: relevant.** The cards of §3 name theirs: throughput on Linux,
   `taskset`-pinned, the four subject regimes, both layers, compiler gcc 15.2. A choice
   must hold in every regime its site can be in (K-1), which is why near-miss is a column
   of every card and never a separate study. Every number in this draft is either a
   `sizeof` (compile-only) or a cited fact. None is a timing.
2. **Independent control: relevant.**
   - The forms' answers are controlled by G2 against the byte loop over a GENERATED span
     space (lengths 1..64, plus 500 and 4095 as fixed long cases), never by the kit's own
     plan.
   - The proof is controlled by pcrec's B5 comparison against its OWN statement, plus the
     kit's own `proof_n` check and its plant (§1). The two share no source: pcrec reads its
     statement, and the kit reads the text it tests.
   - Timing is controlled by pcrec's G1 (its deny, `no-span-loop`) and by the engine-route
     reference C5.
3. **What moves when data is regenerated: not relevant today.** The forms read no measured
   data. `h` is a constant now (UNMEASURED DEFAULT), and if C2 shows the death-depth
   reading (a), it becomes a derivation from the art's byte rate. That rate is pcrec's
   analysis object, already an input. A rate change could then move a kit byte, which is
   an abi event (integration.md §21.3). It is named here so the build's card says it.

## 7. OPEN questions (for main / Frank), each with a recommendation

- **Q1 (main).** Should pcrec keep its non-cover window sites at 32 positions and reach 64
  as a PCREC assertion at its own writers, now that the kit's bounds are general?
  RECOMMEND: yes, as one `_Static_assert` per construction bound it already owns
  (`PCREC_MAX_REQ_RUN_SCAN`, `PCREC_PREFIX_K_MAX`), not as a site kind threaded into
  `window_bounds_check`. B4 then needs no site kind.
- **Q2 (Frank, via main).** Should the interim head `h` be 32, labelled `UNMEASURED
  DEFAULT`, until the cards run? It keeps the joint landing zero-mover at the default width
  and matches his 15:00 prediction. RECOMMEND: yes. The alternative, landing L as the
  default with no measured head, moves the stage-1 covers with no card behind it.
- **Q3 (Frank, via main).** Should the first build that admits k > 32 (under the option)
  also carry a skip after the failing position (§4)? Without it, a dense near-miss subject
  at k near 4095 may run hundreds of times slower than the engine (UNMEASURED,
  extrapolated). RECOMMEND: carry it IN the L/H loop as its stream (the loop's exit offset
  is the skip's input, at no extra cost), measured on the same cards with C5 as the
  reference, and keep form I's RESTART as it is. If Frank prefers D77 strictly: land
  without it, and state in the option's spec hunk that dense near-miss subjects are the
  option's known slow regime.
- **Q4 (main, ordering).** Should `MF_MAX_SPAN_POS` retire in this kit delivery?
  RECOMMEND: yes, if pcrec's A1 (`MkEnd` stops copying) is on the combined branch first;
  otherwise keep it as `32` one more release with a comment naming its last reader. It is
  an interim order and the end state is the same, so it is the manager's call (memory
  `pcrec-plain-words-not-ids`).
- **Q5 (main).** Should a timing slot be requested for C1-C3 and C5? They are kit timing
  and need a cleared night window (not 20:00-01:00). RECOMMEND: ask for it beside
  cover_cap.md §11.4's night, on the same combined-branch binary, so C5 and pcrec's B
  cells share a noise floor. C4 (compile and size only) is a plain boxqueue job.
- **Q6 (main).** The proof rows live in pcrec's arena for the attempt's life: 131 KB per
  class answer of a 4095 cover. Is that acceptable until the stage-2 cost record says
  otherwise? RECOMMEND: yes. The run-length form is designed (§5) and filed with its
  trigger.

## 8. responses.md-ready block (for the kit manager to post; facts only, D157)

```
## R-45 reply (2026-11-16, kit) — window spans of up to 4095 positions
- (1) YES. Bounds, EVERY window span (one general carrier; no site kind):
  MF_WSPAN_POS 4095 (CHOSEN: pcrec's widest statement); MF_WREACH = MF_WSPAN_POS + 1 =
  4096 (DERIVED: span + after-context); MF_MAX_FWD = MF_WREACH (build-time ceiling, for
  your _Static_assert). The reply's proof range is a PER-REPLY COUNT, mf_class.proof_n:
  [MF_PROOF_LO, stated_end), stated_end = 1 + the site's largest stated offset; nothing is
  proven outside it BY CONSTRUCTION (the text tests stated offsets only). For a cover it
  always reaches offset k. The kit refuses its own reply if proof_n misses the stated
  extent; your short-range error stays as defence, its control a kit-tree plant.
  pcrec's own 32/64 for non-cover sites are pcrec construction bounds (assert them on
  PCREC_MAX_REQ_RUN_SCAN / PCREC_PREFIX_K_MAX), not kit bounds.
- (2) NO, they decouple. MF_MAX_TERM 32 (terms; VM/ADVANCE stride) and MF_WMAX_SPAN 32
  (spans per alternative, own derivation: PCREC_PREFIX_K_MAX + R) stay; MF_WSPAN_POS 4095;
  MF_MAX_SPAN_POS and MF_MAX_AHEAD retire (MF_MAX_FWD no longer needs them). S526's
  premise ends; re-aim it at MF_WSPAN_POS 4095 -> 4094, BUILD-REFUSED via your seam
  assert. PM_NPROOF 41 goes (the range is a count).
- (3) Forms: I all inline (today), L loops over maximal runs of one set, H(h) inline
  head then L. Cards: C1 k=24,32; C2 k=36 (uuid),40 (lit-l40),49,60; C3 k=500,1000;
  C4 compile/size k=32..4095; C5 your engine route as reference. Subjects: hit-dense,
  dense near-miss (k-1 members + miss), miss-heavy, random; both layers. h is the cards'
  output (death-depth vs code-size knee). Interim h = 32, UNMEASURED DEFAULT: zero
  movers at your default width. One PAIR row (working name span-loop) for the dial.
  Card numbers OWED: a kit timing window (C1-C3, C5); C4 a boxqueue job.
- (4) Dense near miss is O(n*k) vs the engine's O(n): ~k/2 re-tests per byte (15.5 at
  k=32, fits x6.65; ~x850 at 4095, UNMEASURED extrapolation). The statement already
  gives what a skip past the failing position needs (bad-character over sets); an L/H
  loop yields the failing offset for free. Logged as an idea; see the open question.
- (5) Arrays leave the seam structs. mf_wspan: uint16 len/core_lo/core_len, set and
  table_ref point at HOST-owned arrays (1,164 -> 32 B). mf_class: proven[41][32] removed;
  proof_n + proof rows in YOUR arena (mf_arena), immutable, shared by copies; run reply
  uint16 (2,932 -> 1,640 B; mf_result 3,000 -> 1,712 B). mf_wreply: nplan uint16, plan/
  plan_term/plan_test in your arena (532 -> 136 B). Arena rows at k=4095: 131,328 B per
  class answer of the cover site. Your 8 stack classes: 23,456 -> 13,120 B. Kit internals
  sized per site extent (never the ceiling). MF_SITE_ABI 29 -> 30 carrying MF_CLASS_V
  10 -> 11; MF_VOCAB unchanged; no kit byte moves at default width (h = 32).
- Questions for you: non-cover 32/64 as pcrec asserts? interim h = 32? fail-skip in the
  first >32 build? MF_MAX_SPAN_POS retire order (after A1)? card window beside 11.4's?
```
