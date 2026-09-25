# S3: attribution of the four losing WAF cells (plus the slack near-tie)

Lane `wafread`, 2026-09-25, branch `lane/wafread` from main `ea51a4b3`.
This is S3 of `docs/design/compare_stack.md` §6.1 (D122 + ADDENDUM + ADDENDUM 2).
It is a read. Nothing under `src/`, `cli/`, `lib/` or `tests/` changed. Nothing was
written in `/Users/fdicostanzo/pcrec-bench`, which was read only.
**No timing was taken on this box.** Every ns figure is the bench's Ryzen 1600
record (`budu-ryzen1600`, capability@0.1). Every other number is a count, a
stamp read from emitted C at `ea51a4b3`, or a prediction that is labelled as one.
Instruments are in `waf/` (see its `CLAUDE.md`), and `waf/waf_numbers.txt` is
the rendered output they produce.

**Units.** The `large-subject-throughput` regime is set-grain: one find-all
over each of `t-64k`, `t-256k` and `t-1m`, 1,376,256 bytes in all. `ns/B` below
is the set median divided by 1,376,256. **All five cells have zero matches on
all three subjects** (§1), so each cell is exactly one `rx_search` call per
subject. The scan therefore IS the whole cell, and there is no per-match or
per-call term to separate out.

---

## 0. Findings first

| cell (thr) | pcrec ns/B | algorithmic winner, ns/B | SIMD/JIT, not targets | ships (stamps at ea51a4b3) | CAUSE (compare_stack layer) | needs CASELESS? | lever (algorithmic?) |
|---|---|---|---|---|---|---|---|
| `942360-concat-sqli` 5.39× | 8.80 | re2 1.63 (lazy DFA, no prefix accel) | rust 1.79, vectorscan 0.64 | dfa / **attempt** / prefilter none / table none / edge none | **(1) L4 engine shape:** one `^` arm routes the whole pattern to `ENG_ATTEMPT`. This is MEASURED at ×3.51 (I-85 M5.b, 8.42→2.40). **(2) The residual 2.40 vs 1.63 is DFA transition cost** on a machine where every byte is a candidate: the split artifact's first set is ⊇ the word class, so L3 cannot filter it | **no** | `[OPT-ATTEMPT-SPLIT]` (exists, ratified), then the per-step question of §3.4. Both algorithmic |
| `942270-union-select` 2.27× vs re2 (3.55× vs rust) | 0.724 | re2 0.319 (scalar **ShiftDFA over the caseless prefix `union`**) | rust 0.204 (Teddy), JIT 0.044 | dfa / unanchored / **byte-class `{u,U}`** / premul / edge none; REQ none | **L3.** A byte-at-a-time table walk over a one-cube set. The walk itself is ~78-87% of the cell (§3.2). The pattern's three necessary runs (`union`, `select`, `from`) are all caseless, so `reqbyte.c` sees none of them. None of them occurs in the subject | **YES: the only S4 customer** | **S4(a):** a caseless necessary-run pre-check. The operand is a letter scanned by two leapfrogged libc `memchr` streams (one per case) plus a masked P4 verify. PREDICTED 0.12-0.27 ns/B from slack's measured per-hit rate (§3.2). Algorithmic, with libc's SIMD as the accepted baseline |
| `942160-sleep-benchmark` 3.49× vs rust | 0.989 | **none ahead: pcrec beats every scalar engine** (re2 1.627) | rust 0.283 (Teddy), JIT 0.764 (interp 4.86) | dfa / unanchored / byte-class `{s,S,b,B}` / premul / edge bitmap; REQ `)` emitted | L3 plus multi-literal. The only engines ahead are SIMD (rust) or excluded (JIT, per cycle-1 rule 1) | only as a caseless **multi**-literal, i.e. `[OPT-A]`/Teddy, which is held | **none now.** A SIMD-phase deferral, as cycle1_analysis §2.3(j) already records |
| `942140-dbnames` 1.82× | 2.967 | re2 1.629 (lazy DFA, no prefilter) | rust 1.78, JIT 3.93 | dfa / unanchored / **byte-class-bounded, 63 bytes** / premul / edge mixed; REQ none | **(1) L3:** the leading `\b` widens `can_begin_match` to the word class (77% of bytes), so the scan is 95% transition steps (`firstset_design.md` §3.1). This is `[OPT-FIRSTSET]`'s named cause. **(2) DFA transition cost:** ~3.2 ns per step against re2's ~1.6 per byte | **no.** The 14-byte true first set is a plain table set | `[OPT-FIRSTSET]` (+ the re-seed repair). Predicted 2.09 ns/B by the firstset model. Beyond that it is the per-step question (§3.4). Both algorithmic |
| `slack-webhook-url` 0.77× (**a WIN**) | 0.246 (nocaps) / 0.253 (caps) | pcrec is the fastest algorithmic engine (re2 0.319, rust 0.469) | JIT 0.037, vectorscan 0.081 | dfa (caps: vm+hybrid) / offset-set / REQ_RUN `://`@1 emitted | none: `://` is absent, so the REQ_RUN pre-check answers the whole call in one pass. 39,095 `/` hits at ~8.7 ns each | no | nothing. Its measured memchr+verify rate is the calibration §3.2 uses |

**The four headline answers the brief asks for:**

1. **Only one of the four losing cells needs a caseless mechanism,** and that is
   `union-select`. S4 has exactly one customer, worth 0.1831 of the losing
   matrix's ~10.284. The shape it needs is **S4(a)**: a caseless necessary run
   searched with memchr and verified with a mask. That shape is `reqbyte.c`'s
   known false negative (iii) closed. The other two S4 options do not reach it:
   - **S4(b), the cube scan on `{u,U}`, is ALREADY what ships.** The byte-class
     table walk is a one-cube membership test spelled as a table. A
     byte-at-a-time mask spelling of it buys nothing measurable.
   - **Only a SWAR or SIMD spelling of S4(b) changes the rate.** SWAR is
     register-width arithmetic, not a vector ISA. Whether it counts as "our own
     SIMD" under Frank's 2026-09-25 hold is **an open ruling (§5 Q1)**. S4(a)
     does not need that answer.
2. **`concat-sqli` and `dbnames` need no caseless mechanism and no L2 compare.**
   Their causes are already named rows:
   - `[OPT-ATTEMPT-SPLIT]` covers concat-sqli, and `[OPT-FIRSTSET]` covers dbnames.
   - They share a residual below those rows: DFA per-step cost on text where
     nearly every byte is a transition. The winner there is re2's plain lazy DFA
     with **no prefilter at all**. Rust cannot build one either, and lands at
     1.78-1.79.
   - compare_stack §6.3 said "(c) only" for dbnames and "(c)" for concat-sqli,
     where (c) is the multi-literal prefilter. **This read refutes that on the
     facts.** The algorithmic winner on both uses no multi-literal mechanism, and
     rust's multi-literal prefilter loses to re2 on both.
3. **`sleep-benchmark` is not an algorithmic loss.** pcrec already beats every
   scalar engine. It stays a SIMD-phase deferral. One unexplained drift is
   recorded and not attributed: 0.920 → 0.989 ns/B (+7.5%) between pin
   `25b1984f` and `6ef76820`+ (§3.3, Linux block L4).
4. **Every mechanism named here is algorithmic.** None depends on our own SIMD.
   The only SIMD-shaped options are S4(b)-SWAR and `[OPT-A]` Teddy. They are
   recorded as future SIMD rows, not proposed.

**Recommended next step.** Run the Linux block in §4. It is one executor
session, about 10 minutes of timed runs, with every twin answer-checked here
first. Then:

- **(i) If U1-U3 confirm:** open S4(a) scoped to `union-select`. Its first
  customer brings P2 (the byte cube) into `src/core/` (ADDENDUM 2 (2)), and it
  lands after S1 has extracted the kit, as a P5 form row.
- **(ii) Treat `[OPT-FIRSTSET]` (with its re-seed) as dbnames' S3 answer.** It
  already names dbnames in its landing bar. Carry the L2 block's dbnames rerun
  into its F3.
- **(iii) Put the per-step question (§3.4) to the plainloop twins** before
  anyone designs for it. If they close the gap to re2, the cause is the loop's
  skip/stay dispatch. That is a selection question for `dfa_scans[]`, not a new
  mechanism. If they do not, the cause is the step itself: the by-class accept
  view and the bounded check.

The measured order therefore does not move S2: `[OPT-VMLIT]` has no customer among
these cells. This supports ADDENDUM 2 (1)'s ordering: the S3 read found what S4
would have been built for, and it is one cell.

---

## 1. The subject: all five cells are zero-match scans, and the vocabulary matters

From `waf/waf_numbers.py` (§(2) of `waf_numbers.txt`):

- **Every keyword is absent,** case-insensitively, from all three subjects:
  `union`, `select`, `from`, `sleep`, `benchmark`, `information_schema`,
  `database`, `schema`, `://`, `hooks.slack`. python `re` finds zero matches for
  every pattern on every subject.
- **The grammar's vocabulary is narrow.** It has **zero** occurrences of the
  caseless bigrams `un`, `sl`, `be`, `fr`, `om`, `ct`, against 13,009 of `se`
  and 10,191 of `on`. So a PAIR scan on these subjects would read far better
  than it would on real text. **No prediction below uses a bigram rate for that
  reason.** Every candidate count is single-byte.
- **Densities of the shipped candidate sets:** `{u,U}` 3.09%, `{s,S,b,B}` 5.29%,
  the word class 77.27%, `)` 0.57%, `/` 2.84%, `:` 0.86%. The text averages
  5.69 bytes per word.

The cells therefore reward a filter that can prove absence in one pass. That is
the pre-check shape, and it is D119-honest here: benign WAF traffic also mostly
lacks `union`. The pick (§3.2) is where real traffic differs.

---

## 2. Who wins, and what the winner does

Figures are set-grain ns/B from `waf_numbers.txt` §(1). Latest pcrec
(`b1885a83`); competitors from `fullroster-25b1984f` or `after-b1885a83`,
whichever is newest.

**re2 (scalar; the algorithmic target on concat-sqli, union-select and dbnames).**
`re2/prog.cc` `Prog::ConfigurePrefixAccel` (fetched 2026-09-25, google/re2 main):

- A **case-folded required prefix** gets `PrefixAccel_ShiftDFA`. This is a
  branch-free scalar shift-DFA over at most `kShiftDFAFinal` = 9 prefix bytes,
  unrolled by eight. It checks for a match only at the end of each iteration.
- A case-sensitive multi-byte prefix gets `PrefixAccel_FrontAndBack` (memchr /
  AVX2). A single byte gets plain `memchr`.
- With no required prefix there is no accelerator, and re2 runs its lazy DFA one
  transition per byte.

What that means per cell:

- `(?i)union.*?select.*?from` has the folded prefix `union`, so it gets the
  ShiftDFA. **0.319 ns/B, about 1 cycle/byte, independent of candidate density.**
- `\b`-led alternations (dbnames, concat-sqli) have no required prefix, so they
  get the plain lazy DFA. **1.63 ns/B on both, and 1.62 on the unrelated
  `json-constant`.** That is re2's generic per-byte DFA rate.

**rust regex (SIMD literal prefilters; excluded as a target per cycle-1 rule 4).**
`regex-syntax/src/hir/literal.rs` (fetched 2026-09-25):

- `Extractor::new()` defaults are `limit_class: 10`, `limit_repeat: 10`,
  `limit_literal_len: 100`, `limit_total: 250`.
- `(?i-u)ab` extracts as `exact(["AB","Ab","aB","ab"])`: case-insensitivity is
  expanded into literal variants.
- `(?i)union` is 2⁵ = 32 variants, well inside Teddy's reach. That is 0.204 ns/B.
- `sleep|benchmark` is 32 + 512 variants, over the total limit, so the extractor
  trims them to prefixes (INFERRED from the documented limit behaviour, not
  traced). That is 0.283 ns/B.
- On the `\b` keyword alternations rust lands at 1.78-1.79, **slower than re2**.
  That is consistent with no usable prefilter (BELIEVED: we did not trace rust's
  choice).

**pcre2-jit (excluded, cycle-1 rule 1: the interpreter must also win, and it does
not on any of these rows).**

- It is fastest on union-select (0.044) and slack (0.037), with `pcre2-interp` at
  2.06 and 1.69 respectively.
- That pattern is a SIMD start-up scan in JIT code. It is not a pattern-level
  start-up optimization the interpreter shares.
- BELIEVED, from the rates: the JIT's `fast_forward_char_pair` SIMD path. Not
  traced here.

---

## 3. Per cell

### 3.1 `942360-concat-sqli`: engine shape first, transition cost second

**Ships.** The stamps are `RX_DFA_SCAN "attempt"`, `RX_DFA_PREFILTER "none"`,
`RX_DFA_TABLE "none"` and `RX_DFA_SCAN_EDGE "none"`. The artifact is 388,580 B
(caps) and 388,582 B (nocaps). This read reproduced cycle1_analysis M5's stamps
at `ea51a4b3`.

**Cost chain** (Linux, I-85, `t-1m`):

| stage | ns/B |
|---|---|
| base | 8.42 |
| arm-deletion upper bound (M5.b, `split.rx`: 5→4 arms, 1,460→291 B) | 2.396 |
| **re2** | **1.63** |

So cause (1), the `ENG_ATTEMPT` shape, is **measured**: ×3.51. That is
`[OPT-ATTEMPT-SPLIT]`, ratified.

**Cause (2), the residual 2.40 → 1.63 (×1.47), is not L3.**

- The split artifact stamps `byte-class-bounded`, with a first set ⊇ the word
  class. Its fourth arm starts with `["'0-9A-Z_-z]`, and the `\b` arm widens to
  the word class.
- No truer first set is narrow, and there is no necessary run shared by all
  arms. So FIRSTSET cannot help.
- What is left is per-transition cost. It is the same residual as dbnames (§3.4).

**Caseless:** none needed. **L2:** no compare site exists on this route
(compare_stack §1 refinement (c)). §6.3's "first find out why the prefilter is
`none`" is answered: `ENG_ATTEMPT` has no prefilter machinery at all
(`emit_dfa.c:13-17`).

**Short-subject (srch, 1.53× vs rust, 0.77× vs best scalar)** is a SIMD
deferral already (cycle1 §2.3(j)).

### 3.2 `942270-union-select`: the S4(a) customer

**Ships.** `byte-class` over `can_begin_match = {u,U}`, with REQ none. The forward
loop is:

```c
while (scan_position < subject_length && !rx_can_begin_match[subject[scan_position]]) scan_position++;
```

It then steps the DFA at each hit: 42,563 hits, 3.09%.

**Where the 0.724 goes (a MODEL, not a measurement).**
`firstset_design.md` §3.1 gives an identity:

```
cost/B = (L·b + w·a + c)/(L + w),   L = (1−d)/d
```

It carries a measured `a` = 3.21 ns/step. At d = 3.09%, L = 31.3. With w = 1-2
steps per entry and c ≥ 0, the measured 0.724 solves to b = 0.57-0.65 ns per
skipped byte. So **the byte-at-a-time table walk is ~78-87% of the cell.** The
candidates' DFA re-entries are the minority. Two consequences follow:

- a sparser 1-byte set would buy little;
- a mask spelling of the same walk (S4(b), scalar) would buy nothing.

What moves the rate is replacing the walk with `memchr`, which runs at libc's
SIMD rate, about 0.02-0.05 ns/B across the bench's floor cells.

**Why pcrec has no such scan today.** The three necessary runs `union`, `select`
and `from` are all caseless. `reqbyte.c`'s literal members are
`pcrec_cls_single` singletons only (compare_stack §2.5), so `RX_REQ_BYTE "none"`.
There is also no case-invariant necessary byte anywhere: `.*?` separates the runs.

**The mechanism: S4(a).** Widen `RbSet` to cubes (P2). A caseless run's letter
position is a K=0xDF cube. P5 searches one letter as **two leapfrogged `memchr`
streams**, the lower and upper case. This is the classic caseless first-unit
scan (BELIEVED to be what PCRE2's interpreter does for a caseless first code
unit; not traced). At each hit, P4 does a masked compare of the run:
`(c[i]|0x20)==run[i]`, which is exact for ASCII letters. This is where the K/T
mask first enters P4, as compare_stack §6.1 S4 anticipates.

**Cost model (PREDICTED from a measured rate, same bench, same subjects).**

- Slack's REQ_RUN pre-check is the same shape (memchr + verify, restart per hit):
  0.246 ns/B × 1,376,256 B / 39,095 hits = **8.66 ns per hit, all-in**.
- Scaled by each letter's two-case hit count:

| run (letter) | hits (lower + upper) | predicted ns/B | vs re2 0.319 | vs rust 0.204 |
|---|---|---|---|---|
| `from` (`m`) | 17,978 + 306 | **0.115** | 2.8× ahead | ahead |
| `from` (`f`), **the prior's argmin** | 24,889 + 2,285 | **0.171** | 1.9× ahead | ahead |
| `select` (`c`) | 29,365 + 962 | 0.191 | 1.7× ahead | ≈ |
| `union` (`u`) | 38,400 + 4,163 | 0.268 | 1.2× ahead | behind |

The prior (`pcrec_byte_freq_ppm`, lower + upper ppm) ranks the letters
f 16,266 < m 17,545 < u 20,195 < c 20,286, so an argmin pick lands on `from`/`f`.

**A caveat to carry into S4's design:** `from` is the right pick on the bench and
the WRONG one on real traffic. Prose contains "from" constantly; benign requests
rarely contain "union". A letter's rarity is a marginal fact and a run's rarity
is a joint one. This is `reqpos_2b.md`'s own finding: an independence product
mis-predicts run density by 5× to 3,257×. **The run choice needs a run-level
prior or a findings value, not the letter argmin.** A design that inherits the
letter argmin will look excellent on this cell and be poor in deployment.

**Twins built and answer-checked here** (no timing): `ciprecheck union u`,
`from f`, `from m` and `select c`. All are SAME on `t-64k`/`t-1m` (0 matches) and
on `match.bin` (9 matches, equal to python `re`'s count). A deliberately wrong
run (`unions`) DIFFs (9 → 0), so the check can fail. Linux block U1-U3 (§4)
times them.

**S4(b) and S4(c):**

- S4(b) scalar is today's walk (above). S4(b)-SWAR, testing 8 positions per word
  under P8, is the one form that could beat the walk without memchr. It is held
  pending §5 Q1.
- S4(c) Teddy is held (ADDENDUM 2 (4)).

**Short-subject (srch):** pcrec wins (0.54×).

### 3.3 `942160-sleep-benchmark`: not an algorithmic loss

**Ships.** `byte-class {s,S,b,B}` (5.29%), `RX_REQ_BYTE "41"` (`)`, present 7,861
times, so the pre-check passes after a short scan), and a bitmap scan edge in
the reverse pass.

**Standing:** pcrec at 0.989 beats re2 (1.627), pcre2-dfa and interp. Only rust
(Teddy over the trimmed case variants of `sleep`/`benchmark`) and the excluded
JIT are faster. Under D119's rules this is the SIMD-phase deferral cycle 1 already
recorded.

**Caseless relevance:** only as a caseless MULTI-literal (two runs, neither
necessary alone). That is `[OPT-A]`/Teddy, held. A scalar form exists, four
leapfrogged memchr streams (two letters × two cases), but it has no customer:
the cell is not losing to any algorithmic engine.

**Unattributed drift, recorded:** pcrec went 0.920 → 0.989 ns/B (+7.5%) between
the pin (`25b1984f`/`cf0962e3`) and every later build (`6ef76820`, `8d716693`,
`b1885a83`). The other four cells did not move (≤ 0.5%). Candidates:

- the batch-1 REQ_BYTE pre-check `)`, which is a whole-window `memchr` that
  passes, so it should cost well under 1%;
- code layout.

Not attributed here. Linux block L4 is an A/B with `-fno-req-byte`.

### 3.4 `942140-dbnames`: FIRSTSET's cell, then the per-step question

**Ships.**

- `byte-class-bounded`, with `can_begin_match` = the 63-byte word class (the
  leading `\b`; cycle1 §2.3(d)).
- Two stay loops, the by-class accept view, and a mixed scan edge.
- Forward table: 4,872 entries.

**The cost is structural, not pattern-specific.** The four artifacts
cycle1_analysis §2.3(d) lists as carrying the 63-byte word-class set land
within 5% of each other:

| artifact | ns/B |
|---|---|
| aws-access-key-id | 2.894 |
| syslogbase-expanded (VM route, DFA hybrid prefilter) | 2.898 |
| dbnames | 2.966 |
| json-constant | 3.050 |

These are four unrelated automata (`waf/stamp_join.sh` → `waf/stamp_join.txt`).
The only other `byte-class-bounded` artifact, `currency-lookbehind-fixed` at
8.1, is VM-routed, with backtracking work on top.
`firstset_design.md` §3.1 already has the mechanism: at d = 77% the loop is
94.8% transition steps at a = 3.21 ns/step.

**Cause (1), L3 set width.** This is `[OPT-FIRSTSET]`, whose landing bar already
names this cell.

- The true first set is 14 bytes (7 letters × 2 cases, 22.2%).
- The firstset model predicts 2,190,072 ns on `t-1m`, **≈ 2.09 ns/B**.
- The I-85 M3.c twin measured 2.74. `firstset_design.md` §3.4 flags that +31% as
  unexplained.
- O-46 later found the companion `json-constant` twin's M3.c number did not
  reproduce: 1.52-1.66 on reruns vs 3.41. **So the dbnames twin number is suspect
  too, and a rerun is owed** (L2).
- Note that the narrowing **must carry the re-seed**. As ratified it deletes
  matches (`firstset_design.md` §4; O-46 F2).

**Cause (2), the per-step residual.** Even at FIRSTSET's predicted 2.09, dbnames
stays ~1.3× behind re2's 1.63. The same shape is concat-sqli's post-split
residual (2.40 vs 1.63), where no set can be narrowed.

- pcrec's step here costs ~3.2 ns. OPT-3 STEP 2's premultiplied plain loop ran
  ~1.80 ns/B on t-b/t-c, and re2 runs ~1.6.
- The difference is what this loop carries per iteration that the plain loop
  does not:
  - the three-way state dispatch (`forward_state == 0 / 2755 / 3190`) with its
    skip/stay loop entries and exits every ~5.7 bytes (a word);
  - the by-class accept probe (the `\b` view);
  - the bounded `scan_position + 1 < subject_length` guard.
- OPT-3 (plan row, STEP 3 candidate (b)) predicted exactly this. It said a stay
  loop generalized to every self-looping state is "a net LOSS on non-periodic
  text unless predicted", at one data-dependent exit per 2-6 bytes. Stay loops
  have since shipped (`dir_fwd_skip`).

**The `plainloop` twin discriminates.** It deletes the dispatch chain and every
skip/stay loop, and steps the DFA on every byte (re2's shape). It keeps the view
probe and the bounded guard.

- **If it lands near re2 (≤ ~1.8):** the stay/skip dispatch is a net cost on this
  text. The fix is a SELECTION: a density- or run-length-gated row in
  `dfa_scans[]`/`dfa_pfs[]`, reading P6. It is table-driven per ADDENDUM 2 (4),
  exact-only, and needs no mask.
- **If it stays near 2.9:** the view probe/guard is the cost. That is a different
  row (the `\b` by-class accept, `[OPT-FIRSTSET]`'s neighbourhood).

**Caseless:** none. The 14-byte set is an ordinary table set. It is two cubes per
letter pair, but a 256-byte table spells it no worse, and at 22% density no
memchr form applies.

**Short-subject (srch):** pcrec wins (0.61×).

### 3.5 `slack-webhook-url`: a win, and the calibration point

**Ships** (nocaps): DFA, `offset-set`, `REQ_BYTE 47` (`/`), `REQ_RUN "3a2f2f@1"`
(the run `://`, scanned on `/`). Caps is the VM hybrid with the same pre-check.

- `://` never occurs, so the whole call is one memchr('/') pass with a failed
  compare at each of 39,095 hits.
- 0.246 ns/B beats re2 (0.319) and rust (0.469). Only JIT and vectorscan are
  ahead.
- **No customer.**

One recorded observation, not a proposal:

- The static prior ranks `/` (4,154 ppm) rarer than `:` (6,646).
- On this log-heavy subject `:` is 3.3× rarer (11,812 hits), which would predict
  ~0.074 ns/B.
- This is the subject-blind-prior hazard `reqbyte_freq_pick.md` names. It is a
  `[ENG-PGO]` `freq` concern, not an S4 one.
- compare_stack §6.2 called slack "already a near-tie". It is a win. The census's
  "near-tie" wording (`wordfold_census.md` §0/§5) reads 0.77× as close-behind,
  but the ratio is pcrec over the target, so pcrec is ahead.

---

## 4. Linux measurement request (executor text; darwin timing is never citable)

**Prerequisites.**

- Pcrec at `lane/wafread` (or main after merge), built with the box's gcc.
- cycle1_analysis.md §0.1-0.5 re-run first: `$OPT1`, the three subjects
  sha256-checked, `clock.c`, `findall.c`.
- One heavy thing at a time. load1 < 0.5 before any timed phase.

```sh
# 0. inputs + artifacts
W="$OPT1/pcrec/docs/dev/optloop/waf"; PAT=/home/duxevents/pcrec-bench/bench/capability/patterns
python3 "$W/mk_inputs.py" "$OPT1"            # writes $OPT1/match.bin, $OPT1/split.rx
for P in wild-waf-crs-942140-dbnames wild-waf-crs-942270-union-select wild-waf-crs-942160-sleep-benchmark; do
  "$OPT1/pcrec/build/pcrec" --features all --no-captures -p rx -o "$OPT1/$P.c" --pattern "$(cat $PAT/$P.rx)"
done
"$OPT1/pcrec/build/pcrec" --features all --no-captures -p rx -o "$OPT1/split.c" --pattern "$(cat $OPT1/split.rx)"
"$OPT1/pcrec/build/pcrec" --features all --no-captures -fno-req-byte -p rx \
    -o "$OPT1/sleepnrb.c" --pattern "$(cat $PAT/wild-waf-crs-942160-sleep-benchmark.rx)"
grep -h -E '^#define RX_(DFA_SCAN|DFA_PREFILTER|REQ_BYTE) ' "$OPT1"/*.c

# 1. twins (each must print SAME on every line; STOP on any DIFF)
cd "$OPT1"
for P in wild-waf-crs-942140-dbnames split wild-waf-crs-942270-union-select wild-waf-crs-942160-sleep-benchmark; do
  python3 "$W/mk_twin.py" plainloop $P.c ${P}_plain.c
  "$W/check.sh" $P.c ${P}_plain.c subj/t-64k.bin subj/t-1m.bin match.bin
done
U=wild-waf-crs-942270-union-select
for RL in "union u" "from f" "from m" "select c"; do set -- $RL
  python3 "$W/mk_twin.py" ciprecheck $U.c ${U}_ci_$1$2.c $1 $2
  "$W/check.sh" $U.c ${U}_ci_$1$2.c subj/t-64k.bin subj/t-1m.bin match.bin
done
# EXPECT matches: 0 on t-*; match.bin dbnames 7, split 10, union 9, sleep 6

# 2. timing: base vs each twin, three sizes, 5 iterations (findall.c's best-of)
t() { cp "$OPT1/$2.h" "$OPT1/art.h"; gcc -O2 -I"$OPT1" -o "$OPT1/bin_$1" "$OPT1/findall.c" "$OPT1/$1.c"
      for S in t-64k t-256k t-1m; do "$OPT1/bin_$1" "$OPT1/subj/$S.bin" 5; done; }
uptime
t wild-waf-crs-942140-dbnames wild-waf-crs-942140-dbnames;       t wild-waf-crs-942140-dbnames_plain wild-waf-crs-942140-dbnames
t split split;                                                   t split_plain split
t $U $U; t ${U}_plain $U
for V in unionu fromf fromm selectc; do t ${U}_ci_$V $U; done
t wild-waf-crs-942160-sleep-benchmark wild-waf-crs-942160-sleep-benchmark
t wild-waf-crs-942160-sleep-benchmark_plain wild-waf-crs-942160-sleep-benchmark
t sleepnrb sleepnrb
uptime
```

**Expectations and what refutes them** (all ns/B at `t-1m`):

- **U1 (the S4 claim).** `ci_fromm` ≈ 0.12, `ci_fromf` ≈ 0.17, `ci_selectc` ≈
  0.19, `ci_unionu` ≈ 0.27. They should be **ordered by hit count** and all below
  re2's 0.319.
  - Refuted if any is ≥ base 0.72.
  - The per-hit model is refuted if the order does not follow the hits (18k <
    27k < 30k < 43k). The two-stream leapfrog may cost more per hit than slack's
    one stream. A uniform upward shift with the order intact still confirms the
    mechanism.
- **U2 (the walk-dominance model, control).** `union-select_plain` is **slower**
  than base. It steps every byte at ~1.8-3.2 ns. If it is faster, §3.2's b-solve
  is wrong.
- **U3 (control).** `sleep_plain` is slower than base (5.3% density; the same
  logic).
- **L1 (the per-step question).** `dbnames_plain` and `split_plain` ≤ ~1.8
  (near re2 1.63) means the skip/stay dispatch is a net cost. ≈ base (2.9 /
  2.4) means the dispatch is free and the cost is the step (view probe + guard).
  Either answer names the row. **In between is also informative:** report the
  fraction.
- **L2 (FIRSTSET's owed rerun, riding the same session if the executor has
  `firstset_design.md` §7's F-blocks staged).** Run the dbnames 14-byte twin with
  the re-seed, 5 trials. The firstset model predicts 2.09. The rerun decides
  whether M3.c's 2.74 was the json-style outlier.
- **L4 (sleep drift).** `sleepnrb` vs base. A difference below 1% clears the
  REQ_BYTE pre-check and leaves layout as the suspect. Record, don't chase.

---

## 5. Open questions for Frank

1. **Does SWAR count as "our own SIMD" under the 2026-09-25 hold?**
   compare_stack §6.1 S4(b) lists "SWAR under P8" as a caseless option. It is
   scalar-register arithmetic (8 positions per 64-bit word, a has-zero-byte
   trick) and needs no ISA capability, but it is data-parallel. S4(a) does not
   need the answer: union-select's predicted win uses libc `memchr` only. The
   answer decides whether S4(b) is a row or a future SIMD row.
2. **S4(a)'s run choice.** On the bench, `from` wins (§3.2), and on real WAF
   traffic `union` does. The letter-argmin prior picks `from`. Should S4(a)'s pick
   read a run-level value (a `freq`-family findings entry, D83's addendum
   permits it), or should the static rule prefer the run that is rarest as a run
   (by length, or by a run table), accepting a worse bench number? Recommendation:
   the run-level rule. Winning the cell with the pick that loses in deployment is
   the D119 carve-out's own warning case.

---

## 6. What this read did not do

- **No timing.** Every prediction above is labelled PREDICTED/MODEL and is owed
  §4's block.
- **Rust's and the JIT's internal choices are INFERRED** from documented
  behaviour (the extractor limits, ShiftDFA) and from their rates. They were not
  traced in either engine.
- **The caps arm was not read separately** beyond the stamps. For all four WAF
  cells auto-caps equals auto-nocaps within 0.5%: every one routes DFA, and a
  capture-free pattern needs no VM.
- **The short-subject cells were only placed, not attributed.** Every one is
  either a pcrec win or an existing SIMD deferral.
