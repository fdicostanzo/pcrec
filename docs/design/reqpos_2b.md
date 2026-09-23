# `[OPT-REQPOS]` tier 2b — the necessary literal RUN as a whole-window pre-check

**`[OPTLOOP.2]` cycle-2 design note, lane `c2design`, 2026-09-22.** Design
only: nothing under `src/`, `cli/`, `lib/` or `tests/` changed in the delivery
that carries this note, no mechanism is built, and no clock was read anywhere.
Every number is a COUNT taken from committed artifacts
(`docs/dev/optloop/c2/reqpos_census.tsv`, `run_selectivity.txt`,
`subject_freq.json`) or from one `gcc-16 -O2 -S` compilation of a four-line
probe (§3.2, the only thing this note compiled). Ratification and a D6 panel
are owed before any implementation lane opens.

---

## 0. Read this first — the verdict, and three findings that reshape the row

**VERDICT: tier 2b CLEARS D119's bar and should be built — but it is not the
mechanism the row describes.** It is not a start bound, it needs no position
relative to the match start, and it does not depend on tier 2. It is
`[OPT-REQBYTE]` **widened from a 1-byte necessary fact to an L-byte one**, and
today's mechanism is its `L = 1` case exactly.

1. **THE ROW'S OWN FRAMING — "the position as a start bound" — IS NOT WHAT 2b
   NEEDS, AND THE CENSUS ALREADY SAID SO.** `reqpos_census.md` §1 records that
   "tier 2b is ORTHOGONAL to 1/2/3: a run is a statement about two bytes'
   RELATIVE positions and says nothing about either one's offset from the
   start." Read forward, that means the census's `dmin`/`dmax`/`run_pmin`/
   `run_pmax` columns — everything tier 2 would consume — **are not read by
   this mechanism at all.** Four of the fourteen `capability` runs have
   `run_pmax = -1` (an UNBOUNDED offset from the match start) and are served
   perfectly, because the delta the compare uses is internal to the run. So
   the row's tier 2 (declined by the census on population) is not a
   precondition, and `src/opt/prefix_k.c`'s fixed-offset tier 1 is a different
   mechanism serving a different question (a candidate START on the DFA route).
2. **THE DECLINE RULE CANNOT COME FROM A BYTE-FREQUENCY PRIOR, AND THAT IS
   ARITHMETIC RATHER THAN OPINION.** A run's density is a JOINT property and
   `freq` is a MARGINAL distribution. Predicting a run's rate as the product
   of its members' ppm over-predicts the measured gain by 5×, 8× and 3,257× on
   the three `capability` rows where a gain is finite (§4.2) — a 650× spread
   across three rows, so no calibration constant and no threshold over an
   independence product separates the 1.00× row from the 119× row. Either the
   mechanism ships with no decline rule (recommended, §4.3) or a SECOND named
   `freq`-family analysis value carries run rates, which D83's addendum
   explicitly permits and which nothing measured yet asks for.
3. **`memcmp` WITH A COMPILE-TIME-CONSTANT LENGTH IS A BETTER EMITTED FORM
   THAN THE ROW'S OWN `memcpy`-INTO-`uint64` SKETCH, MEASURED** (§3.2).
   `gcc-16 -O2` lowers `memcmp(p, "abcd", 4)` to one 32-bit load and one
   compare and `memcmp(p, "github_p", 8)` to one 64-bit load and one compare,
   with no call — Frank's "ONE unaligned word load compared against a
   constant" exactly — while reading only the L bytes the run occupies. So
   there is no over-read to bound, no endianness question, no alignment UB,
   and the `[WORD-FOLD]` row's own page-boundary worry never arises. The
   masked (small-CLASS) form is the one that genuinely needs a hand-rolled
   load, and it is gated on `[WORD-FOLD]` and is NOT in this note's event.

**And one dependency, stated up front**: `reqbyte_freq_pick.md` is a
PRECONDITION for this mechanism's cost story, not a companion. The run form's
per-candidate cost is bounded by the density of the byte it `memchr`s, and on
`logparse-atomic` today's pick is the SPACE at 121,963 hits per MiB where the
prior picks the COLON at 9,070 — a 13.4× difference in exactly the cell where
this mechanism's own gain is 1.00×.

---

## 1. The measured need

### 1.1 The population

`reqpos_census.md` §2, over a probe that drives the real parser, `altcls`,
`discharge_atomic` and `lower_enc`, cross-checked against batch 1's landed
`RX_REQ_BYTE` stamp (63 of 64 bench patterns, 0 disagreements):

| | bench (249) | corpus (3,944) | corpus `-e utf8` |
|---|---|---|---|
| **run ≥ 2 (tier 2b)** | **68 — 27.3%** | **734 — 18.6%** | 799 — 20.3% |
| run ≥ 4 | 29 — 11.6% | 90 — 2.3% | 100 — 2.5% |
| run ≥ 8 | 6 — 2.4% | 25 — 0.6% | 26 — 0.7% |
| tier 2 (bounded `dmax`) — the row's own headline tier | 21 — 8.4% | 238 — 6.0% | 255 — 6.5% |

Run LENGTH distribution, derived here from the census's `run_len` column:

| L | 2 | 3 | 4 | 5 | 6 | 7 | 8 | ≥ 9 |
|---|---|---|---|---|---|---|---|---|
| corpus (734) | 460 | 184 | 33 | 20 | 6 | 6 | 4 | 21 |
| bench (68) | 18 | 21 | 21 | 2 | 0 | 0 | 1 | 5 |

**62.7% of the corpus population is L = 2**, which is one 16-bit load and one
compare, and only 5.0% is L ≥ 5. The mechanism's median case is the cheapest
case, which is the opposite of what a "word compare" sounds like.

**And every count above is a FLOOR**, for reasons the census names: at an
`A_ALT` the run analysis keeps only the branches' common prefix and suffix
(`(?:xabcy|zabcw)` reports no run where `abc` is one), runs are not merged
across a repeat's iterations, and a class with more than one member contributes
nothing — which is every caselessly folded literal, since D23 folds `(?i)a` to
`[aA]` at parse time. So **every `(?i)` pattern's run figure is zero or short
until the masked form lands**, and that is `[WORD-FOLD]`'s own population
arriving from this side.

### 1.2 The bar cells, and they are real

`reqpos_census.md` §4 and §0: **five `capability` patterns have the single
necessary byte PRESENT in the throughput subject and the RUN ABSENT**, so a
byte-grain whole-window pre-check cannot fire at all and a run-grain one
answers the entire find-all call in one pass. Four of the five are cycle-1
LOSING cells:

| pattern | run | L | rarest member's hits in `t-1m` | run hits | rank | score |
|---|---|---|---|---|---|---|
| `wild-semdiv-dollar-trailing-newline-pcre2` | `abc` | 3 | 4,973 | **0** | 4 | 0.8710 |
| `file-ext-order` | `.tar` | 4 | 14,826 | **0** | 13 | 0.2213 |
| `wild-semdiv-altorder-foo-foobar-rustregex` | `foo` | 3 | 18,853 | **0** | 14 | 0.1931 |
| `wild-secrets-github-pat` | `github_pat_` | 11 | 4,973 | **0** | 16 | 0.1763 |
| `wild-secrets-slack-webhook-url` | `://` | 3 | 9,070 | **0** | — | (wins today) |

**1.4617 of the losing matrix's 10.284**, in four throughput cells, every one
of which the mechanism converts from a full attempt loop into one
`memchr`-class pass at the 0.0168 ns/byte floor `cycle1_analysis.md` §2.2
shows three engines share and pcrec's own `floor-byte` control already
reaches. That is a STEP change, not a percentage, and it is why the verdict is
BUILD rather than DECLINE.

### 1.3 The honest reading of "60 of 68 runs never occur"

`run_selectivity.txt`: of the 68 bench patterns with a run, **60 have a run
that never occurs in `t-1m` at all.** That is the mechanism's BEST case and
not its worst — a run that never occurs is a whole-call answer. The brief's
framing reads it as a weakness; it is the opposite, and the note says so.

**The real weakness is the eight rows with a FINITE gain**, whose median is
4.24× and whose minimum is 1.00× — and the 1.00× rows are where the word
compare is pure added cost per candidate:

| pattern | run | L | rarest member's hits | run hits | gain |
|---|---|---|---|---|---|
| `capability/logparse-atomic` | `": "` | 2 | 9,070 | 9,070 | **1.00×** |
| `capability/logparse-atomic-removed` | `": "` | 2 | 9,070 | 9,070 | **1.00×** |
| `loglines/http-5xx` | `" HTTP/1."` | **8** | 6,236 | 6,000 | **1.00×** |
| `syntax/mod-reset`, `syntax/mod-unset` | `"at"` | 2 | 30,306 | 3,230 | 9.4× |
| `capability/keyword-prefix-order` | `"in"` | 2 | 30,683 | 7,243 | 4.2× |
| `capability/router-prefix-order` | `"/user"` | 5 | 29,144 | 245 | **119.0×** |

**The longest finite-gain run in the whole population, `" HTTP/1."` at eight
bytes, has a gain of 1.00×.** So a run's gain is not a function of its length
in either direction, and any decline rule keyed on L would decline
`router-prefix-order`'s five bytes at 119× while accepting eight bytes at
1.00×. This is the single most useful row in the table and §4 is built on it.

### 1.4 The honest caveat on generalization

The bench's throughput texts are `captext.text()` output — a synthetic
line-structured text at three sizes and three seeds, whose grammar interleaves
words, punctuation and digits and was never constructed around these literals.
So "the run is absent" is REALISTIC for the secrets and WAF families (a
scanner over text that contains no secret is the deployed case) and ARBITRARY
for the semantics-divergence families (`foo|foobar` over text with no `foo`).
The bar cells are scored on the subbench as it is measured, and the
generalization claim this note does NOT make is that 60-of-68 absence is a
property of real subjects.

---

## 2. The analysis that produces the run

### 2.1 What it must produce, and what it must not

For each pattern, ONE tuple: **the run's bytes `R[0..L-1]`, and the index `i`
of the member the emitted scan will `memchr`.** Nothing else. Not an offset
from the match start, not a `dmin`/`dmax`, not a second run.

The soundness statement is one sentence and it is `[OPT-REQBYTE]`'s own
sentence at word grain: *every match of this pattern contains `R` as a
contiguous substring; every byte of every match lies in
`[search_from, subject_length)`; so if `R` does not occur in that window, no
match exists in it.*

### 2.2 The walk

It is `reqbyte.c`'s existing bottom-up walk with a second accumulator, and the
node arms are the same arms. `RbSet` gains a companion — a `RUN` value
carrying the longest guaranteed-contiguous literal byte sequence of the
subtree, plus its own head and tail runs so a concatenation can join them:

| node | run |
|---|---|
| `A_CLASS` singleton (after `pcrec_lower_enc`, so exactly one BYTE) | the 1-byte run `{b}` |
| `A_CLASS` multi-member | EMPTY — the decline that costs every `(?i)` literal, §1.1 |
| `A_CAT` | join: left's TAIL run concatenated with right's HEAD run is a candidate; the best of {left's best, right's best, the join} wins |
| `A_CAP`, `A_ATOMIC` | transparent — `reqbyte.c`'s own argument, unchanged |
| `A_REP` with `rmin >= 1` | the body's best run; **the head and tail runs do NOT survive a repeat** unless `rmin >= 2` would let them join across iterations, which this note declines (§2.4 item 4) |
| `A_REP` with `rmin == 0` | EMPTY, `reqbyte.c`'s one arm where forgetting the minimum deletes a match |
| `A_ALT` | the branches' longest COMMON prefix and common suffix only — the census's own stated false negative, kept because the alternative is a set of runs and the emitted form tests one |
| `A_EMPTY`, `A_BOL`, `A_EOL`, `A_END`, `A_WORDB`, `A_NWORDB`, `A_GSTART`, `A_KRESET`, `A_LOOK`, `A_BREF`, `A_CALL` | EMPTY — identical to `reqbyte.c`'s arms, including the LOOKBEHIND correctness decline |

The switch stays exhaustive with no `default:` arm, `src/opt/mrl.c:38-46`'s
rule and `reqbyte.c`'s own: a node kind added later must be a COMPILE ERROR
here, because a new kind inheriting "the empty run" is sound and is therefore
exactly the silent loss worth an alarm.

The `A_CAT` spine and the `A_ALT` spine are walked ITERATIVELY, for
`reqbyte.c`'s own recorded reason ("this project has segfaulted its own
compiler on a 20,000-byte literal for want of exactly that") — and the census
probe's own build recorded the same lesson independently
(`c2prep_report.md` F5: "a census walk must fold the `A_CAT` spine
iteratively; the first draft died on the corpus").

### 2.3 Choosing `i` — and why `reqbyte_freq_pick.md` is a precondition

`i` is the index of the run member the scan `memchr`s. The per-candidate cost
of the whole mechanism is exactly the number of occurrences of `R[i]` in the
window, so **`i` is chosen as the ARGMIN of `pcrec_byte_freq_ppm` over the
run's members**, ties to the leftmost. Two consequences:

* It is the same rule, the same accessor and the same shipped table as
  `reqbyte_freq_pick.md` §3.1, applied to a smaller set. Not a second
  mechanism; one call.
* **Without the pick rule, this mechanism inherits the rightmost accident.**
  The census reports `pick_in_run` as a boolean — is today's picked byte a
  member of the run — and it is 0 on **7 of 68 bench** and **12 of 734 corpus**
  patterns, including `tag-depth3-bound` and `tag-pair-match`, whose picked `>`
  is not in their run `</` at all. On those the scan byte must be re-chosen
  from the run regardless, so the pick question cannot be deferred.

**The census does not carry `i`.** Its `run_hex` gives `R` and `pick_in_run`
gives a boolean; the index is owed as a one-column census extension (§7 item
1) before an implementation lane can pin a fixture's expected emitted text.

**THE SAME ENCODING DEPENDENCE APPLIES HERE, AND IT BINDS THIS ROW TOO**
(Frank's consideration of 2026-09-22 evening, worked in full at
`reqbyte_freq_pick.md` §3). A byte-frequency value is a fact about a subject
corpus UNDER an encoding — a UTF-8 corpus's histogram is a different value
from a latin1 corpus's over the same text — and this mechanism's `i` is
chosen by exactly that value over exactly the same lowered byte tree, so it
inherits the hazard whole: the shipped `byte_freq_ppm_tbl`'s entire 0x80–0xFF
half sits at the table's 2 ppm floor, which under `-e utf8` calls the bytes a
Latin corpus uses most the rarest bytes there are, and picking a UTF-8 lead
byte as the `memchr` target is the worst available choice for the scan cost
§3.3 prices. **So `i`'s frequency-informed choice carries
`reqbyte_freq_pick.md` §3.3's rule unchanged: it applies under `byte` and
DECLINES under every other encoding, falling back to the run's LEFTMOST
member** — which needs no prior, is what the plan row already specifies for
the no-findings-file case ("with an `[ENG-PGO]` findings value it picks the
RAREST pair, without one the leftmost"), and costs nothing measurable, since
the census's `-e utf8` arm shares no bar cell with §6.1. The RUN itself is
encoding-sound by construction for `reqbyte.c`'s own reason — it is built
from post-`lower_enc` singleton byte classes, and §2.4 item 7 already records
that `-e utf8` RAISES the population rather than complicating it. And when a
run-rate analysis is eventually written (§4.3's named trigger), it is a
findings value like any other and is keyed by encoding the same way — one
`DATA`-scope row, `[DD-13b]`'s to write, spelled out at
`reqbyte_freq_pick.md` §3.4.

### 2.4 What the mechanism declines, stated as a list

1. **Any pattern with no run of length ≥ 2** — 81.4% of the corpus. It keeps
   `[OPT-REQBYTE]`'s `L = 1` behaviour unchanged, which is the same artifact
   it has today.
2. **Every caselessly folded literal**, because D23 makes `(?i)abc` three
   two-member classes and a multi-member class contributes no byte. This is
   the largest decline by population and its remedy is `[WORD-FOLD]`'s masked
   compare, a separate row (§3.4).
3. **Runs longer than a cap.** The emitted compare is priced at L ≤ 8: the
   run is TRUNCATED to its best 8-byte window around `i`, never split into two
   compares. **"Best" RULED by Frank (2026-09-22 evening): the 8-byte window
   containing `i` whose members sum to the LOWEST `pcrec_byte_freq_ppm`,
   ties to the leftmost — the same prior and accessor as `i`'s own choice,
   under the same encoding rule (byte only; elsewhere the leftmost window
   containing `i`). "That is precisely the sort of precompiling analysis
   that gives this project its advantage."** `github_pat_`'s eleven bytes become eight, which is already a
   whole-call answer on this subject. A second compare would be a second
   mechanism with its own cost question and no measured need (D77).
4. **Runs joined across a repeat's iterations.** `(?:ab){2,}` guarantees
   `abab`, and this note does not claim it: the census's own false-negative
   list already excludes it, the population is unmeasured, and a join across
   an iteration boundary is the kind of reasoning that wants its own witness
   family. Declined with the reason, not forgotten.
5. **Runs across an alternation's non-common interior** (`(?:xabcy|zabcw)`).
   Same census false negative; a set of runs needs a multi-compare emitted
   form.
6. **Everything `reqbyte.c` already declines** — a zero-admitting quantifier,
   a backreference, a linked call, every assertion, and a lookaround's body,
   which stays un-descended for the LOOKBEHIND correctness reason and not for
   convenience.
7. **Nothing on account of encoding.** After `pcrec_lower_enc` a run is a run
   of BYTES under either encoding, and a run spanning a character boundary is
   as sound as one inside a character. `-e utf8` raises the population
   (734 → 799) because a multi-byte character lowers to a fixed-width `A_CAT`
   of singleton byte classes, which is more contiguous literal, not less.

---

## 3. The emitted C

### 3.1 The shape

Written ONCE and emitted by both engines' search entries, inside
`pcrec_emit_req_byte_check` (`src/gen/emit_dfa.c:660`) rather than beside it —
so the two routes cannot test the run in two different shapes, which is that
function's own stated reason for existing. At `L == 1` the emitted text is
byte-for-byte what it is today. At `L >= 2`, with `A = R[i]`:

```c
/* [OPT-REQPOS] every match of this pattern contains the 4 bytes
 * ".tar", so a window without them holds no match at all. */
if (subject_length <= search_from) return 0;
{
    size_t rp_pos = search_from;
    for (;;) {
        const void *rp_q = memchr(subject + rp_pos, 46,
                                  subject_length - rp_pos);
        size_t rp_c;
        if (!rp_q) return 0;
        rp_c = (size_t)((const unsigned char *)rp_q - subject);
        if (rp_c + 4 <= subject_length
            && !memcmp(subject + rp_c, ".tar", 4)) break;
        rp_pos = rp_c + 1;
        if (rp_pos >= subject_length) return 0;
    }
}
```

(The example is `file-ext-order` with `i = 0`; a non-zero `i` subtracts `i`
from `rp_c` in both the guard and the `memcmp` base, which is how the run
OVERLAPS `A` in Frank's `https://` example — `memchr` the `:`, compare eight
bytes at `p − 5`.)

Six things about it, each one a rule this tree already holds:

* **The `<=` guard above the loop is the same two-obligations-in-one-test
  `pcrec_emit_req_byte_check` already writes** and its comment already
  explains: `memchr(NULL, c, 0)` is undefined behaviour and `match_api.md`
  §3.1 permits a legal empty subject with a NULL pointer (UBSan reads the
  emitted artifact, so this is a report and not a theory), and an empty window
  cannot hold the run anyway. Unchanged, reused.
* **The window guard is `rp_c - search_from >= i` and `rp_c - i + L <=
  subject_length`**, both necessary and neither defensive: the run must lie
  ENTIRELY inside `[search_from, subject_length)` because every byte of every
  match does, so a hit too near either end cannot be the run's own `A` and the
  scan advances. **At `i == 0` the first conjunct must be OMITTED, not emitted
  as `>= 0u`** — an always-true unsigned comparison is a `-Wtype-limits`
  report under the harness's own `-Wall -Wextra -Werror` `GENCFLAGS`, which is
  the exact defect class `edge1_report.md` recorded (`(unsigned)s >= 0u` on a
  machine all of whose states are heads: a `-Werror` failure in emitted code
  that no answer check can see). The example above is `i == 0` and shows the
  one-conjunct form.
* **`memcmp` with a LITERAL length, never a variable and never `memmem`.**
  `memmem` is a GNU extension and pcrec emits portable C; a variable length
  defeats the lowering §3.2 measures; and a hand-rolled `memcpy` into a
  `uint64_t` reads bytes the run does not occupy, which is the over-read
  `[WORD-FOLD]`'s own row already refuses ("pcrec does not own the buffer —
  the page-boundary trick real engines use fails the both-axes ASan/UBSan
  discipline").
* **The run is a STRING LITERAL and therefore every byte of it must be
  escaped.** The run comes from pattern text, so `emit_comment_safe_byte`'s
  sibling discipline applies at the string position: a `"`, a `\`, a NUL and
  every non-printable byte need an escape, and a `\?` trigraph-adjacent
  sequence needs care. The tree has no emitted-C-string-literal escaper today
  (the comment escaper is `emit_dfa.c:80`), so **this is one new emission-kit
  primitive**, `sb_cstr` or the like, belonging beside `sb_text`/`sb_field`
  in `src/core/sb.c` per wave 1's own two-vocabularies-one-implementation
  shape (`w1kit_report.md` §0). Alternative considered and declined: emit a
  `static const unsigned char` array and `memcmp` against it — it defeats
  gcc's constant folding (§3.2 measures the literal form producing an
  immediate; an array is a second load) and it adds a `.rodata` object to
  every artifact in the population.
* **The comment carries pattern-derived bytes and must go through the comment
  escaper**, threading `*prevp` across calls, for `-Wcomment` under the
  harness's own `-Werror` `GENCFLAGS` (coding_guide §3.2, lane `cmtfix`'s two
  hazards `*/` AND `/*`). A run of `*/` is `nested-comment-rec`'s actual run,
  so this is not hypothetical: the row's own witness would break the build.
* **Columns are kept near a sabotage anchor** (coding_guide §3.4): S265's
  anchor sits in this function's emitted text, `replace.py` matches
  `SAB_BEFORE` as a whole-file line-agnostic substring, and re-indenting the
  existing `L == 1` lines to share a block with the new loop would break it.
  So **the `L == 1` path emits its existing text at its existing indent**,
  unchanged and un-nested, and the run path is a sibling branch — which is
  also why the example above opens its own `{ }` scope rather than hoisting
  `rp_pos` beside the existing declarations.

### 3.2 The lowering, measured on this box

`gcc-16 -O2 -S` on constant-length `memcmp` (the probe and its output are in
this lane's scratch, reproduced in one command in §7 item 3):

| L | lowering | call? |
|---|---|---|
| 4 | `ldr w1,[x0]` + one immediate + `cmp` | no |
| 8 | `ldr x1,[x0]` + one immediate + `cmp` | no |
| 3 | `ldrh` + `ldrb`, two compares | no |
| 11 | `ldr x2,[x0]` + `cmp`, then the 3-byte tail | no |

So Frank's "a 2-byte pair and an 8-byte run cost the same instruction pair" is
true for L ∈ {2, 4, 8} and the odd lengths decompose into two loads rather
than calling out of line. **62.7% of the corpus population is L = 2**, one
16-bit load. The lowering is the compiler's and pcrec does not hand-roll it,
which is also why this form survives a toolchain that lowers differently —
`[CC-DIFF]`'s standing lesson.

### 3.3 The cost, stated against today's shape rather than against zero

This is the part a reviewer should attack. Today's `L = 1` check is ONE
`memchr` that stops at the FIRST hit. The run form loops until the run is
found or the window is exhausted, so:

* **Run ABSENT**: today's check falls through after one hit and the attempt
  loop runs the whole window. The run form makes one full `memchr` pass over
  the window plus one `memcmp` per `A` occurrence, and RETURNS 0. This is the
  win, and it is the 60-of-68 case.
* **Run PRESENT and `A` common**: today's check falls through at the first
  `A`; the run form scans to the first RUN occurrence, paying one `memcmp` per
  intervening `A`. **This is a real added cost and it is bounded by `A`'s
  density** — which is §2.3's whole reason for choosing `A` by the prior, and
  why `logparse-atomic`'s cost is 9,070 compares per MiB rather than 121,963.
* **The 1.00× rows are pure cost**, by construction: `": "` at gain 1.00× pays
  one `memcmp` per colon and learns nothing. §4 is about whether that is
  acceptable.

The mechanism therefore stays inside one `memchr`-class pass in the
`cycle1_analysis.md` §2.2 sense — O(n) with one sequential pass — but with a
per-`A`-hit constant that today's form does not have.

### 3.4 What is NOT in this event

**The masked / small-CLASS compare.** Frank's ruling includes "where the run
is small CLASSES rather than exact bytes, the same compare works as load +
AND-mask + compare — `[WORD-FOLD]`'s cube compare, so the two rows SHARE that
primitive." `[WORD-FOLD]` is `STATE:not-started` and its own D77 gate is an
unrun census, so **this note does not build on it and does not instruct its
use**, per coding_guide §2's rule against reaching for an unbuilt primitive.
The masked form is event 2, gated on `[WORD-FOLD]` landing, and it is the
event that unlocks the `(?i)` population §2.4 item 2 declines. Nothing in
event 1 forecloses it: the analysis produces a run of singleton classes today
and a run of one-cube classes later, and the emitted form goes from `memcmp`
to load+and+compare at the same call site.

---

## 4. The decline rule

### 4.1 Why one is needed here and was not needed for `[OPT-FIRSTSET]`

`firstset_design.md` §3.3 finds that narrowing a candidate-start SET is
monotonically non-harmful at the byte grain, so its model declines nothing.
This mechanism is different in kind: §3.3 above shows it adds a per-candidate
`memcmp` that buys nothing on the 1.00× rows. A decline rule is therefore a
real question and not a formality.

### 4.2 The prior cannot answer it, and here is the arithmetic

Predicting a run's occurrence rate as the product of its members' ppm under
independence, against the measured gain:

| pattern | run | members' ppm | rarest | independence rate | predicted gain | **measured** | over by |
|---|---|---|---|---|---|---|---|
| `logparse-atomic` | `": "` | 6,646 / 124,561 | 6,646 | 828 ppm | 8.0× | **1.00×** | **8×** |
| `keyword-prefix-order` | `"in"` | 46,105 / 44,776 | 44,776 | 2,064 ppm | 21.7× | **4.20×** | **5×** |
| `router-prefix-order` | `"/user"` | 4,154 / 18,359 / 42,034 / 84,235 / 39,708 | 4,154 | 0.0107 ppm | 387,418× | **118.96×** | **3,257×** |

**The over-prediction spans 650× across three rows.** Bytes in real text are
not independent — that is what a run IS — so `freq`, a marginal distribution,
is structurally the wrong statistic and no constant fitted to it helps. This
is the same class of result as `cls_tree_study.md` §8's "a cost model that
prices a form without building it is only safe if something independently
builds and checks", arriving from the data side.

### 4.3 The recommendation: ship with NO decline rule, and say what it costs

Three reasons, and the third is the decisive one:

1. **The mechanism's own structure already bounds the damage.** With `A`
   chosen by §2.3, the added cost is one constant-length `memcmp` per
   occurrence of the RAREST member under the prior — the cheapest scan the
   analysis can produce. On the worst measured row that is 9,070 two-byte
   compares per MiB, ~0.9% of subject bytes touched twice.
2. **A decline rule needs a statistic nobody has measured**, and D77 forbids
   building it now. If the bench shows a real regression on a 1.00× row, the
   trigger is named: a second `freq`-family named analysis value carrying RUN
   rates (D83 addendum item 1 permits exactly this — "a later analysis … is a
   new named value in the same file, never a new mechanism"), whose first
   consumer would be this decline — and which is KEYED BY ENCODING for §2.3's
   reason, since a run's rate is as much a fact about an encoded corpus as a
   byte's is.
3. **The axis IS the decline rule for now.** `-fno-req-run` (or the value form
   §5 recommends) lets a caller who has measured a regression turn it off,
   which is what a tuning axis is for and what `tuning.md` §1 says it is for.
   A guessed threshold in the compiler is worse than a flag a measurement can
   set.

**What this costs, stated plainly**: a caller whose subject makes the run as
common as its rarest byte pays ~1% of a pass for nothing, silently, until they
measure it. That is the trade, it is on the speed axis only, and it can never
cost a match.

---

## 5. `abi`, stamp, axis, sabotage

### 5.1 `abi`

**Yes — one bump, and it is a scaffolding change and not only a value
change.** A new stamp line appears on EVERY artifact (§5.2) and the emitted
pre-check gains lines on the population, so this is `abi` **29 → 30** (or
30 → 31 if `reqbyte_freq_pick.md` lands first; the two SHOULD land as one
event, §7 item 5, because their populations overlap and two bumps re-pin the
same manifests twice). The full D76/D94 ritual, with the three reader classes
this house has now recorded:

1. **text that cites the number** — found by grepping the current digit;
2. **a manifest whose rows hold byte COUNTS that move without citing any
   digit** (`battriage_report.md`, `evtriage3_report.md`, `optimpl1_report.md`
   §0) — `run_cpset_structure.sh` CHECK 3's twelve `EMITTED_BYTES` rows and
   `run_resource_tests.sh`'s rescue pin, **re-measured by recompiling the
   witnesses to the check's OWN `-o` basename**, this house's four-times-recorded
   trap;
3. **a check that COUNTS rather than cites** — `run_registry_tests.sh`'s
   axes-coverage pin, which batch 1 moved 108 → 120 and which moves again
   here if a new axis lands.

**One correction owed to the documents, found while writing this note.**
`docs/dev/coding_guide.md` §3.1 and `src/gen/CLAUDE.md:25` both say the
current `abi` value is `PCREC_ARTIFACT_ABI` in `src/core/limits.def`. It is
**`src/gen/emit_dfa.c:51`**; `limits.def` contains no such row. A writer
following the ritual's own citation opens the wrong file. Not fixed here
(docs-only lane, and it is a one-line edit in two files that belongs with the
next bump).

### 5.2 The stamp

`<PREFIX>_REQ_BYTE` **keeps its meaning exactly**: the byte the emitted
`memchr` tests. That is the fact `run_prechecks.sh` §3 already reads and the
one a reader most wants, and re-defining it would stale a gate for nothing.

**`<PREFIX>_REQ_RUN` is added**, on every artifact of both engines, beside it
and in the same shape: a string with a `"none"` member, for `REQ_BYTE`'s and
`END_WINDOW`'s own recorded reason (0 is a legal byte value, so no number is
free to mean "declined"). Its value when present is the run's bytes as
lowercase hex plus `A`'s index — `2e746172@0` for `.tar` — which is machine-
readable, escape-free, and carries the one fact a check cannot otherwise
derive. `"none"` at `L < 2`, so the vast majority of artifacts carry the stamp
and declare the empty population, which is the shape D108/`dd8_report.md` §2.1
argues for: an absent population is a ROW with empty cells, never an absent
row, because a check cannot distinguish "no run" from "the stamp stopped being
emitted".

### 5.3 The axis

**This note recommends `-fno-req-run` / `PCREC_NO_REQ_RUN` as its OWN bit**,
which is the opposite of `reqbyte_freq_pick.md` §5.1's recommendation for the
pick, and the difference is the point:

* the pick changes WHICH member an existing mechanism tests — a value;
* the run changes WHAT is tested, adds emitted code, adds a stamp and has its
  own cost profile and its own decline question (§4) — a mechanism, and D119
  rule 5 is categorical about mechanisms.

**And it must be independently revertible from `-fno-req-byte`**, because
their populations differ and a bench carve-out will want exactly one of them
off. Denying `-fno-req-byte` must also deny the run (there is no run check
without a necessary byte to `memchr`); denying `-fno-req-run` must leave the
`L = 1` check standing, byte-identical to today. That asymmetry is a
`tuning.md` sentence and a `run_axes.sh` pair, not an implicit.

**Cost, recorded because it is real.** This is bit 31, the LAST bit spellable
as `1u << N` in `lib/pcrec.h`'s flags enum (`PCREC_NO_REQ_BYTE = 1u << 30` is
today's last member; `1u << 32` is undefined behaviour). The storage is fine —
`pcrec_options.flags` is `uint64_t` — but the next axis after this one forces
the enum to `1ull <<`, which reaches
`tests/registry/axes_registry_check.sh`, whose bit table is DERIVED by
grepping the header's `PCREC_(NO|FORCE)_` spellings. **So an implementation
lane must either take bit 31 knowingly or do the `1ull` widening in the same
change**, and that is Frank's call (§8 question 4) rather than a lane's.

### 5.4 Answer identity and the sabotage row

**Answer identity is preserved in batch 1's strongest sense**: the pre-check
returns NOMATCH only where every attempt would have failed, because the run is
necessary. `make test-axes` on `-fno-req-run` must be answer-identical over
the whole corpus (on darwin: `AXES="-fno-req-run"` alone, verified against
`run_axes.sh`'s own spelling first — the full table is multi-hour).

**The sabotage row (next free id on main at the time) inverts the `memcmp`
sense**, S265's own shape one grain over, and it is ANSWER-DETECTABLE: a
matching subject becomes NOMATCH. That matters because `optimpl1_report.md`
§0 records that two of batch 1's three mechanisms have NO answer-level
detector anywhere in the tree — this one does, and for the same reason S265
does.

**A second row is needed and it is the interesting one**: plant a run one byte
LONGER than the analysis proved (take `.tar` to `.tarz`). The pre-check then
refuses windows that do contain a match, so it is also answer-detectable — but
only on a subject that contains the short run and not the long one, which no
existing corpus file has a reason to carry. **So the row needs its own witness
and that witness must be written with the row**, or it ships UNREACHED. That
is `[MECH-REACH]`'s eighth instance arriving before the fact instead of after,
and the note flags it so a lane writes the fixture rather than discovering the
gap at `make mech`.

### 5.5 The gate

`tests/codegen/run_prechecks.sh` gains a §4, built on §3's own design
(assert the artifact's EMITTED TEXT, and assert the `memcmp` SENSE separately
from its ARGUMENT, because the two sabotage rows corrupt them separately).
Three arms, each with its both-directions population:

1. **the run's presence and shape** — a fixture set whose expected
   `REQ_RUN` value is a LITERAL in the check, hand-derived, never recomputed
   from the analysis;
2. **`L == 1` byte identity** — a fixture with a singleton run whose artifact
   must be byte-identical to `-fno-req-run`'s, which is the arm that makes
   "81.4% of the corpus is untouched" a checked fact rather than a claim;
3. **the window guard's presence** — an absence assertion needs a positive
   control (`evtriage_report.md`'s lesson: an absence reads green when its
   needle dies), so the arm counts the guard in a fixture with `i > 0` and
   asserts its absence in one with `i == 0`.

---

## 6. The landing bar and its cells

### 6.1 Improve (D119 rule 4: median gain > IQR on these cells)

| cell | rank | score | ratio to algorithmic target | mechanism's effect |
|---|---|---|---|---|
| `wild-semdiv-dollar-trailing-newline-pcre2`, throughput | 4 | 0.8710 | 1401.2251 vs `rust` | run `abc` absent → whole call in one pass |
| `file-ext-order`, throughput | 13 | 0.2213 | 6.2993 vs `rust` | run `.tar` absent → whole call in one pass |
| `wild-semdiv-altorder-foo-foobar-rustregex`, throughput | 14 | 0.1931 | 4.9835 vs `rust` | run `foo` absent → whole call in one pass |
| `wild-secrets-github-pat`, throughput | 16 | 0.1763 | 2.6587 vs `rust` | run `github_pat_` (truncated to 8) absent → whole call in one pass |

**1.4617 weighted, 14.2% of the losing matrix's 10.284**, and the largest
single tranche any cycle-2 candidate has. Every one is a throughput
(find-all) cell, which is where a whole-window pre-check pays most.

Note the target is `rust` on all four, and `rust`'s advantage here is a
literal prefilter with a SIMD implementation — `cycle1_analysis.md` §0 rule 4
separates those, so the honest claim is that this mechanism closes the
ALGORITHMIC half of the gap and the scalar column is what it must be scored
against. A cell that reaches the best SCALAR engine and stays behind `rust`
alone becomes a SIMD-phase deferral, which is a result.

### 6.2 Do not regress

| cell | why |
|---|---|
| `capability/logparse-atomic`, `logparse-atomic-removed`, both regimes | **THE CELLS THIS MECHANISM CAN HURT.** Gain 1.00×: one `memcmp` per colon, 9,070 per MiB, buying nothing. If either regresses beyond its IQR, §4.3's no-decline-rule recommendation is refuted and the trigger in §4.3 item 2 fires |
| `loglines/http-5xx`, throughput | the third 1.00× row, and the one with the LONGEST run (8 bytes) — it is in a different subbench, so D119's 2026-09-22 addendum applies (the subbench follows the question) and this cell is measured in `loglines` |
| `capability/keyword-prefix-order`, throughput | gain 4.2×: a real but modest win, and the row where a small gain must still exceed the added compare's cost |
| `floor-byte`, throughput and search | the floor control. Single literal `~`, `L = 1`, must be byte-identical |
| batch 1's five improve cells | **TWO of the five have a run** — `tag-depth3-bound` and `tag-pair-match`, both `</`, both with `pick_in_run == 0`, so on those two the scan byte MOVES off `>` and their emitted text changes. Both bytes of `</` are ABSENT from `t-1m`, so their whole-call answer is already won at `L = 1` and the run form must not make them slower by scanning further. The other three (`dup-param-detect` `=`, `wild-secrets-username-password-pair` `=`, `wild-logparse-winpath-grok` `\`) are `L = 1` and must be byte-identical under §5.5 arm 2 |
| `router-prefix-order`, throughput | rank 12. Gain 119.0× — the best finite gain in the population, and a row that already lost its byte-identity control status at batch 1 |

### 6.3 Size

Non-zero and small: the population's artifacts gain a loop of roughly ten
emitted lines plus a string literal of L bytes, and every artifact gains one
stamp line. At 18.6% of the corpus that is a real `artifact_size_log.tsv`
movement — read it with `scripts/size_diff` and expect the unpinned-max guard
to be untroubled, since the largest artifacts in the corpus are DFA tables
measured in hundreds of kilobytes. D119 rule 4's size clause ("a speedup that
grows artifacts materially takes a `--tune` position, not the default") is not
triggered by tens of bytes, and the note says so rather than leaving it to a
reader.

---

## 7. The D77 measurements this note's landing rests on

1. **The census extension: `i`, the scan member's index within the run**
   (darwin, free, hours). `c2/reqpos_probe.c` gains one column. Without it no
   fixture's expected emitted text can be pinned and §5.5 arm 1 cannot be
   written. ACCEPTANCE: the column is present for all 734 corpus and 68 bench
   run-bearing rows, and `pcrec_byte_freq_ppm`-argmin agrees with a
   hand-derived value on the fourteen `capability` runs.
2. **The absent/present sweep per subbench, with each set against its OWN
   subjects** (darwin, free). `reqpos_census.md` §7 records that §4's `syntax`
   and `altwide` gains were measured against `capability`'s text and are not
   citable; this sweep fixes that and produces the real 1.00×-row list across
   all six sets. ACCEPTANCE: the finite-gain population is enumerated with its
   own subjects, so §6.2's carve-out list is complete rather than
   `capability`-shaped.
3. **The lowering check, re-run on the Linux reference toolchain** (light, via
   the executor; gcc-15.2 there against gcc-16 here). `§3.2`'s table decides
   the emitted form, and `[CC-DIFF]` is this tree's standing evidence that one
   toolchain's lowering is not another's. Command:
   `printf '#include <string.h>\nint f(const unsigned char*p){return memcmp(p,".tar",4)==0;}\n' | gcc -O2 -S -x c - -o -`.
   ACCEPTANCE: no `call` to `memcmp` at L ∈ {2,4,8}. A call there does not kill
   the mechanism but moves the decline question, so it must be known first.
4. **The bench cells, on Linux, through the executor** (D119's landing bar).
   §6.1's four improve cells and every §6.2 carve-out, at the shipped default
   `auto-caps` and at `cycle1_caps_view.md`'s variants. ACCEPTANCE: median
   gain on the four exceeds their IQR; no carve-out regresses beyond its IQR.
   **The two `logparse-atomic` cells are the ones to read first** — they are
   where §4.3's recommendation is falsifiable.
5. **NOT a measurement, a sequencing recommendation**: land
   `reqbyte_freq_pick.md` and this row as ONE `abi` event. Their emitted-byte
   populations overlap (every run-bearing pattern's scan byte is chosen by the
   pick rule), and two bumps re-pin the same three reader classes twice for no
   reviewer benefit.

---

## 8. The four design lenses

**Specific vs general.** General, and it is the general form of a mechanism
the tree already has: `[OPT-REQBYTE]` becomes the `L = 1` case of "the
necessary literal run", with one emitter, one analysis and one soundness
argument covering both. That is what `reqbyte.c`'s own header predicted when
it chose the rightmost rule so "a later multi-byte form is a WIDENING of this
mechanism and not a different one" — this note is that widening, and it
arrives as a wider fact rather than as a second mechanism beside the first
(memory `pcrec-general-mechanisms-not-special-cases`). The two things it
DECLINES to generalize — multiple runs, and runs joined across iterations —
are declined in writing with their reasons (§2.4 items 4 and 5), not folded in
as special cases.

**Core vs derived.** It adds a genuine CORE fact: the longest guaranteed
contiguous literal run, which no pass in the tree computes today. That is real
new analysis in `src/opt/`, sharing a walk and a switch with `reqbyte.c` but
carrying a second accumulator with its own join rule at `A_CAT`. Everything
downstream — the scan byte, the emitted compare, the stamp — is derived from
it. The honest reading is that this is the more expensive of the two cycle-2
notes by a wide margin, and §6.1's 1.4617 weighted score is what buys that.

**Applicable vs assumption-changing.** Applicable on the answer axis: identity
is preserved by construction, every existing decline stands, and the window
argument is `[OPT-REQBYTE]`'s own sentence at a wider grain. It DOES change
two assumptions and both are named. (a) On the cost axis it introduces a
per-candidate compare that today's shape does not have, which is a real
regression risk on the 1.00× rows and is a measured carve-out rather than an
argued one (§4, §6.2). (b) In the emitted text it introduces **the first
multi-byte read at a computed offset and the first emitted C string literal**,
which is why §3.1 owes an escaper primitive and why the window guard is two
conjuncts rather than one. Neither reaches an unbuilt primitive: the masked
form that would is event 2 (§3.4).

**Fits the architecture vs needs a refactor.** Fits, with one addition. The
analysis extends an existing file's existing walk; the emitter extends the one
function both engines already share; the stamp joins two siblings in the same
block; the axis joins a table. The addition is the emitted-C-string escaper,
which belongs in `src/core/sb.c` beside wave 1's text layer and is a
primitive the tree will want again the first time anything else emits
pattern-derived bytes outside a comment — so it is a missing library function,
`coding_guide` §4.1's "common extracts FIRST", rather than this row's private
helper.

---

## 9. Open questions for Frank

1. **Is the verdict accepted — tier 2b BUILD, tier 2 DECLINED?** (The census
   already recommends declining tier 2; this note adds that tier 2 is not even
   a precondition for 2b, so the two are fully separable.)
2. **Ship with NO decline rule (§4.3), accepting ~1% of a pass wasted on the
   1.00× rows until a run-rate analysis exists?** (Recommend yes: the prior
   structurally cannot price a run, §4.2, and a guessed threshold is worse
   than the axis.)
3. **RULED 2026-09-22 (Frank): truncate, and the window is the LOWEST-frequency 8-byte window containing `i` (§2.4 item 3).** Original question — is truncating a run to 8 bytes right, or should a long run emit two
   compares? (Recommend truncate: `github_pat_`'s eight bytes are already a
   whole-call answer, and 25 of 734 corpus patterns have L ≥ 8 at all.)
4. **Bit 31 is the last `1u <<` bit in the flags enum. Take it, or do the
   `1ull` widening in this change?** (Recommend the widening, in this change:
   it reaches `axes_registry_check.sh`'s derived bit table, and doing it under
   an `abi` bump that is already re-pinning three reader classes is cheaper
   than doing it alone later.)
5. **Land this and `reqbyte_freq_pick.md` as ONE `abi` event, or two?**
   (Recommend one, §7 item 5.)
6. **Does the `(?i)` population wait for `[WORD-FOLD]`, or does `[WORD-FOLD]`
   get pulled forward by this row's own decline list?** (Recommend waiting:
   `[WORD-FOLD]`'s D77 gate is an unrun census whose own charter records
   Frank's caution that the shipped corpus may contain no example, and this
   row's event 1 pays without it.)
