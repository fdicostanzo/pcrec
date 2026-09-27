# [UTF8-ATTRIB] — attribution of the twelve unattributed utf8@0.1 large-subject losses, and the F3 answer

Lane `utf8attrib`, 2026-09-27, opus, READ-ONLY (nothing under `src/` or
`tests/` changes). Charter: plan.md `[UTF8-ATTRIB]`. The inputs are bench
outbox O-63 (the re-measure at pcrec pin `751b9c6d`, abi 39), the bench's
committed utf8 reports at that pin
(`reports/2026-09-27-utf8-0.1-budu-ryzen1600-fullroster-751b9c6d.{matrix,subject-grain}.tsv`),
`docs/dev/summaries/2026-09-27-utf8-bench-exec-summary.md` §3.2 and
`[OPT-LITSCAN]`'s F3 note.

**Method.** Three compilers were built from `git archive` in the scratchpad,
never by a checkout: `ce658cb7` (the bench's previous utf8 pin), `751b9c6d`
(the re-measure pin) and current main `02db9c1b` (abi 41). Each of the 17
patterns involved (the 12 rows plus the 5 lit-* rows O-63 names) was
compiled with `--features all -e utf8`, which is the bench adapter's
configuration. Choices were read off the stamps, off `--emit-facts` (main
only) and off the emitted `memchr(...)` arguments, which name the scanned
byte and its offset exactly. The bench's own throughput subjects
(`bench/utf8/throughput/*.bin`) were read over ssh, and per-subject byte and
literal counts were taken from those files.

**Timings are SCRATCH TIER.** They come from a Mac M1 with gcc-16 `-O2`, a
find-all driver (`rx_search` from the end of each match), and the median of
15 repetitions on a box that was not quiet. They confirm mechanisms and
ratios only. None of them is a bench number. Hand-twins are the emitted C
with ONE named edit. Each twin's answers (match count and a span hash) were
checked equal to the base artifact's on all seven throughput subjects, and
the lookbehind twin was also checked on a match-dense synthetic subject.

---

## (B) THE BENCH'S ASK (a) — written to be relayed verbatim

**Short answer.** No: `lit-sharp-s`'s ×2.84 regression is NOT F3's mechanism.
The pre-check itself caused it. `[OPT-REQRUN-ENC]`'s rightmost rule moved
the whole-window pre-check's scan byte from `S` to `e`, and `e` is the most
common letter in Latin text. `lit-cyr-run`'s flatness IS F3's mechanism, and
the rightmost rule is what exposes it. The rule chooses a byte by POSITION,
not by rarity. In UTF-8 it avoids lead bytes, but it can land on a common
ASCII letter (`Straße`) or on a continuation byte. A continuation byte occurs
in every non-ASCII script, so a literal from one script now costs scan stops
on text in another script. Both flip-to-slow cells are that case.

**The byte choices, read from the emitted C at each pin.** "pre-check" is
the whole-window run/byte check (`rx_reqrun` at 751b9c6d). "prefilter" is
the DFA candidate-start scan (`memchr` or `rx_ofsskip`). `@k` is the byte's
offset in the literal.

| pattern | pre-check @ ce658cb7 | pre-check @ 751b9c6d | prefilter @ 751b9c6d (same at ce658cb7) | prefilter @ main (abi 41) |
|---|---|---|---|---|
| `lit-sharp-s` `Straße` | run `Straße`, scan `S` 0x53 @0 | run `Straße`, scan **`e` 0x65 @6** | offset-set: memchr **0xC3 @4**, verify `S` @0 | offset-set: memchr `t` 0x74 @1, verify `S` @0 |
| `lit-cyr-run` `Москва` | 8-byte window `Моск`, scan 0xD0 @0 | 8-byte window **`сква`** (d181d0bad0b2d0b0), scan **0xB0 @7** | memchr **0xD0 @0** | offset-set: memchr 0x9C @1, verify 0xD0 @0 |
| `lit-mixed-ascii` `user@例え.jp` | window `user@例`, scan `u` @0 | window `r@例え`, scan 0x88 @7 | offset-set: memchr `@` @4, verify `u` @0 | offset-set: memchr `s` @1 |
| `lit-run-3` `日本語` | window from 0, scan 0xE6 @0 | window 97a5…aa9e, scan 0x9E @7 | memchr 0xE6 @0 | offset-set: memchr 0x97 @1 |
| `lit-offset-at-head` `@é` | run `@é`, scan `@` @0 | run `@é`, scan **0xA9 @2** | memchr `@` @0 | offset-set: memchr **0xC3 @1** |

**Each cell's mechanism.** The occurrence counts are from the bench's own
subjects.

- **`lit-sharp-s` ×2.84 slower (t-1m).** `Straße` occurs 19 times in t-1m,
  so the pre-check does not reject the subject. Each find-all call re-runs
  the pre-check up to the next occurrence, and each `e` is a memchr restart
  plus a 7-byte compare. There are 52,650 `e` in t-1m against 1,298 `S`.
  - Scratch hand-twin: the 751b9c6d artifact with ONLY the pre-check's scan
    byte changed back to `S`@0 runs in 304 µs, against 1,085 µs for the
    unmodified artifact and 308 µs for ce658cb7. On t-64k-asc it is 2.5 µs
    against 90.6 µs. **All of the regression is the pre-check byte.**
  - F3's lead byte is a SEPARATE, residual cost. A second twin that also
    moves the prefilter from 0xC3@4 to 0x9F@5 gives t-64k-lat 62 µs → 5.7 µs
    and t-1m 304 µs → 169 µs.
- **`lit-mixed-ascii` resolved.** The literal is in no subject, so the
  pre-check rejects everywhere and the prefilter never runs. The rightmost
  member 0x88 happened to be rarer than the old leftmost `u` (2,363 against
  13,581 in t-1m).
- **`lit-run-3` resolved** by the same effect: 0x9E against the shared CJK
  lead byte 0xE6, 206 against 3,478 in t-64k-cjk.
- **`lit-cyr-run` flat (t-1m ×1.12).** The run is 12 bytes, and on the DFA
  route only an 8-byte WINDOW is compared. The rightmost scan index forces
  that window to the tail, `сква`. Lowercase `москва` occurs 189 times in
  t-1m and 43 times in t-64k-cyr, so the pre-check PASSES. The DFA prefilter
  then memchrs the lead byte 0xD0 (100,202 in t-1m) over the rest of the
  subject, which is F3 exactly.
  - At ce658cb7 the pre-check itself scanned 0xD0 and rejected. So both
    pins pay one full pass of 0xD0 stops, and the time is flat.
  - Scratch: 1,086 µs at ce658cb7 against 1,068 µs at 751b9c6d.
- **Flip-to-slow `lit-offset-at-head`/t-64k-lat ×17.6.** The old pre-check
  byte `@` is absent from the Latin subject, so one memchr pass rejected it.
  The new byte 0xA9 is `é`'s continuation byte, with 1,922 stops.
  - Scratch: 1.33 µs → 26.5 µs.
- **Flip-to-slow `lit-cyr-run`/t-64k-cjk ×3.24.** The old byte 0xD0 is a
  Cyrillic lead byte and absent from CJK text. The new byte 0xB0 is a
  continuation byte, and it occurs 377 times in the CJK subject.
  - Scratch: 1.33 µs → 4.6 µs.

**What current main would choose instead (the [PATFACTS]/B1 NONE rules, D126
Q4).** Under `-e utf8` the byte-rate is NONE (`RX_FINDINGS
"byte-rate=none"`).
- **Pre-check: unchanged.** PICK's NONE answer is the positional rightmost
  (`pcrec_find_run_scan_index`), so every pre-check byte in the table is
  identical at abi 41.
- **DFA prefilter: moved, but only by a tie.** MASS's NONE answer is set
  cardinality, so every singleton offset ties at 3,906 ppm. `prefix_k.c`'s
  model then always prefers a scan at k ≥ 1 with offset 0 as a verify, and
  the strict `<` keeps the first k it tries. The result is that **the scan
  byte is the literal's SECOND byte**: `t`, 0x9C, `s`, 0x97, 0xC3.
- Scratch consequences:
  - `lit-cyr-run` is fixed by luck. 0x9C is capital `М`'s continuation
    byte, which occurs 0 times in t-64k-cyr. t-1m goes 1,068 µs → 83 µs and
    t-64k-cyr 198 µs → 2.1 µs.
  - `alt-nearmiss` narrows about ×2.6 (see (A)).
  - `lit-sharp-s` gets slightly worse, t-1m 1,085 µs → 1,264 µs (`t` has
    27,122 stops against 0xC3's 16,522).
  - `lit-offset-at-head` (scan now the shared Latin lead byte 0xC3) and
    `lit-mixed-ascii` (scan now `s`) are LATENT regressions. They are masked
    on the bench's subjects because the pre-check rejects first.
- **The fix is a rate, not a better position rule.** Neither NONE answer is
  a rarity rule. No positional rule can be right across scripts: a lead byte
  is script-specific (rare off-script, dense on-script), and a continuation
  byte is the reverse. What fixes this is a real byte rate under `utf8`, the
  "encoding-keyed prior" that `[FINDINGS]`/`[OPT-LITSCAN]` already name.

**Bench-only questions to relay** (memory `pcrec-ask-bench-dev`):
1. The x86 bench box has not confirmed any scratch number here. The
   lookbehind re-seed twin in (A) is the one worth a bench cell, and its C
   transform is one block, described in (A).
2. Confirm that the large-subject-throughput regime's find-all advances with
   `pos = max(end, pos+1)` on these non-empty patterns. The scratch driver
   assumes it.

---

## (A) THE TWELVE ROWS, in the bench's look-first order

Ratios are pooled over the seven throughput subjects: pcrec's best config
against the best competitor, with vectorscan excluded. They come from the
751b9c6d fullroster matrix. "Worst cells" are per subject, from the
subject-grain report, `auto-caps` against the best competitor.

| # | row | ×@751b9c6d (winner) | where the loss lives | mechanism (pcrec's choice, from the stamps) | algorithmic vs scan-speed | owner | main (abi 41) changes it? |
|---|---|---|---|---|---|---|---|
| 1 | `asr-lb-varwidth` `(?<=a\|é)x` | **8.17** (pcre2-jit) | every subject containing `x` (asc ×23, lat ×12, t-1m ×8.5); cjk/cyr WIN ×0.01 | VM hybrid (`RX_VM_PREFILTER "hybrid"`, prefilter memchr `x`). The prefilter erases the lookbehind, so it OVER-approximates: it finds the first `x`, the VM attempt there fails, and the attempt loop then steps **every character boundary to the subject's end** without asking the prefilter again. The re-seed (`retry_win`, `src/gen/emit_vm.c:12793-12808`) is emitted only when an MRL clamp exists (`v->nclamp > 0`). Cost is O(n) VM attempts once one `x` exists, and 0 matches in every subject. | **ALGORITHMIC.** Scratch twin (main's artifact + the re-seed block after the retry advance): t-1m 7,603 µs → 61 µs (×124), t-64k-asc 645 µs → 8.3 µs; answers identical. | **NEW row, drafted: `[OPT-HYB-RESEED]`** (below). `[ENG-LOOK]` is NOT the lever here. | No. Main is +3-9% (S2a's 2-byte `é` compare on the per-position path). |
| 2 | `alt-distinct-lead` `日本\|Москва\|café` | **7.30** (rust) | all subjects; cyr ×16, t-1m ×7.4, asc ×4.2 | DFA with a `byte-class` prefilter over the first-byte set {`c`, 0xD0, 0xE6}. It is a bytewise bitmap loop (~0.33 ns/B scratch). 0xD0 is about every other byte of Cyrillic text and `c` is common in Latin/ASCII, so the DFA is entered constantly. No required byte (alternation), so no pre-check. | **Both.** Algorithmic: each branch has a rarer byte at a non-zero offset (`М`'s 0x9C @1, `é`'s 0xA9 @4, `日`'s 0x97 @1). A multi-literal candidate test at per-branch offsets would stop only on those, but `prefix_k.c` scans only a SINGLETON at k > 0. The interleaved-memchr twin LOSES here (cyr ×100 slower): the members are frequent. The remainder is scan speed (rust: Teddy, SIMD). | `[OPT-A]` (multi-literal / Teddy lead) | No (scratch identical). |
| 3 | `ci-ascii-control` `(?i)abc` | 4.70 (rust) | asc ×7.3, lat ×6.0, t-1m ×4.8; cyr ×2.4 | DFA `byte-class` {A, a}, a bytewise loop. `a` is the most frequent member of the pattern. `REQ_BYTE "none"` (caseless sets have no single byte). | Mostly scan speed: loop cost alone is ×2.4 on cyr, where no `a` exists. There is an algorithmic part: scanning the rarest FOLD PAIR (`b`/`B` or `c`/`C` at k=1/2) would cut entries, but k > 0 must be a singleton today. The two-memchr twin LOSES (×3.3 slower, frequent members). | `[OPT-LITSCAN]` S4 (caseless) | No. |
| 4 | `ci-sigma` `(?i)σ` | 3.43 (rust) | UNIFORM ×3.42 on every subject, including those with no Greek | DFA `byte-class` {0xCE, 0xCF} (the three case forms' lead bytes). Both are absent from every subject, so the whole cost is the bytewise class loop's speed. | **Algorithmic at this population:** two interleaved `memchr` (libc, the tier pcrec already uses) instead of the bitmap loop: scratch t-1m 341 µs → 45.5 µs (×7.5). It is NOT generally safe: on the rows above, where a member is frequent, the same twin is 3-100× SLOWER. So it is a FORM choice that needs a rate, which under `utf8` is NONE. | `[OPT-A]` (its memchr2/memchr3 lead) as an `[OPT-LITSCAN]` form row; gated on the utf8 prior | No. |
| 5 | `ci-strasse` `(?i)straße` | 2.82 (rust) | asc ×4.0, lat ×3.0, t-1m ×2.8 | DFA `byte-class` {S, s, 0xC5 (ſ)}. `s` is common, so the loop is entered constantly. On subjects with no `s` it pays the ×1.7-2.0 loop floor. | Scan speed plus the fold-pair choice (as row 3). The two-memchr twin loses (×2.8). | `[OPT-LITSCAN]` S4 | No. |
| 6 | `ci-moskva` `(?i)москва` | 2.70 (rust) | cyr ×4.9, t-1m ×2.8; asc/lat/cjk WIN ×0.08 | DFA `memchr` on **0xD0**, the Cyrillic LEAD byte (`REQ_WHY "dominated"`). On Cyrillic text it stops about every other byte. This is F3's lead-byte class under caseless. | **Algorithmic:** the rarer anchor is a continuation byte, but under `(?i)` each position is a 2-byte fold set {0x9C, 0xBC} and k > 0 must be a singleton. It needs S4's caseless vocabulary plus F3's prefilter-selection fix. | `[OPT-LITSCAN]` (F3 prefilter selection + S4) | No. |
| 7 | `alt-nearmiss` `日本語\|日本国` | 4.04 (rust) | t-1m ×4.3, cjk ×8.4; asc/cyr/lat ≈ tie | Pre-check run is the common prefix `日本` (scan 0xAC). `日本` occurs 242 times in t-1m while neither full branch occurs, so the pre-check passes. The DFA prefilter at 751b9c6d is memchr 0xE6 (CJK lead: 11,964 in t-1m). The distinguishing tail (`語`/`国`) is in no necessary fact. | Algorithmic. (a) The lead-byte scan (F3). (b) A necessary SET after the run (third character ∈ {語, 国}) is not derived. | F3 → `[OPT-LITSCAN]`; the post-run set → `[OPT-A]` (multi-literal) | **Partly.** Main scans 0x97 @1 (3,563 stops): scratch t-1m 258 µs → 100 µs, cjk 56 µs → 14 µs. The pre-check-passes part remains. |
| 8 | `asr-b-ascii` `\bcat\b` | 5.06 (rust) | lat ×6.4, asc ×5.7, t-1m ×5.2; cjk/cyr WIN | DFA `offset-set-bounded`: memchr `a` @1, verify `c` @0; pre-check run `cat` scan `t` @2. `cat` occurs 91 times in t-64k-asc and `\bcat\b` never (0 matches), so the pre-check passes and the prefilter restarts on every `a` (4,103 per 64 KB). | Mostly scan speed. Every byte of `cat` is 4-7% of ASCII text. A `-e byte` compile (FREQPICK picks `c`) times the SAME on the ASCII subject (53.9 µs against 55.3 µs), so the byte pick is not the lever. What would help is a PAIR/memmem scan. | `[OPT-A]` (pair scan: the `\bat ` O-8 witness is this shape) | No. |
| 9 | `asr-dollar-ml` `(?m)語$` | **0.80, NOW A WIN** | only t-64k-cjk ×1.23 remains | Pre-check scan moved from 0xE8 (`語`'s lead) to 0x9E (`[OPT-REQRUN-ENC]`). | resolved at the re-measure | `[OPT-REQRUN-ENC]` (closed) | Main moves the prefilter to 0xAA @1. Not timed. |
| 10 | `asr-lb-neg` `(?<!日)本` | 3.21 (oniguruma) | t-1m ×3.9, cjk ×3.2, t-64k ×3.0; others WIN | As row 1. The hybrid prefilter erases `(?<!日)`, so after every `本` preceded by `日` (a failed attempt) the loop steps every position until the next real match. | **ALGORITHMIC.** Re-seed twin: t-1m 3,508 µs → 141 µs (×25), cjk 146 µs → 23 µs; 237/57 matches identical. | `[OPT-HYB-RESEED]` (drafted) | No (the prefilter moved to 0x9C @1; +6% scratch). |
| 11 | `asr-lb-fixed` `(?<=é)x` | 2.85 (pcre2-jit) | asc ×6.1, lat ×3.8, t-1m ×3.1; cjk/cyr WIN | As row 1. | **ALGORITHMIC.** Re-seed twin: t-1m 3,011 µs → 63 µs (×48). | `[OPT-HYB-RESEED]` (drafted) | **Slower at main: +30% scratch** (t-1m 2.29 ms → 3.01 ms, reproduced twice). The only program change is S2a's `memcmp(…, "\303\251", 2)` replacing two byte compares in the lookbehind body, on the path that runs once per position (see the finding below). |
| 12 | `cls-dot-rep` `^.{5}$` | 2.22 (rust) | noise-scale absolute (pcrec 10-19 ns, rust 6 ns) | DFA anchored, `search-filter`. `RX_END_WINDOW "none"` because the end window DECLINES under `utf8` (`--emit-facts`: `decline:enc-multibyte`), whereas `-e byte` stamps `6`. An anchored-both-ends pattern whose width is bounded could reject `n − pos > 4·cwmax + 1` in O(1). | Algorithmic, but per-call and nanosecond-scale. | `[OPT-ENDWIN]` (closed) residual. Drafted `[OPT-ENDWIN-ENC]`, recommended HELD under D77. | No. |

**Totals.** Of the twelve rows, one is already resolved at 751b9c6d
(`asr-dollar-ml`). Three rows (the lookbehind trio) are one ALGORITHMIC
defect with a measured ×25-×124 scratch fix and a drafted row. Three rows
are F3/prefilter-selection defects that need a `utf8` rate
(`ci-moskva`, `alt-nearmiss`, and `ci-sigma`'s form choice). Four rows are
mostly scan speed with algorithmic side levers owned by `[OPT-A]` or
`[OPT-LITSCAN]` S4 (`alt-distinct-lead`, `ci-ascii-control`, `ci-strasse`,
`asr-b-ascii`). One row is noise-scale (`cls-dot-rep`).

### Finding: the hybrid's retry never re-seeds without an MRL clamp (rows 1, 10, 11)

`vm_emit_search_body`'s comment (`src/gen/emit_vm.c:12818-12848`) argues
that the retry "cannot fire" because the hybrid's prefilter is the
capture-ERASED machine and so accepts exactly the pattern's language. It
emits the re-seeding recompute only where a clamp exists, and it says the
recompute "costs nothing on a path the argument above says is dead."

LOOKAROUND ERASURE breaks the argument. The prefilter for `(?<=a|é)x`
accepts `x`, so the retry fires on every non-matching candidate. With no
clamp, the loop then walks `attempt_position++` over the rest of the subject.

The spelling that fixes it already exists: the same three lines as the
entry call, which the comment calls sound (H2: the prefilter answers for
`[start, n)`). Emitting them unconditionally whenever `prefn` exists is the
whole change.

**Drafted row (FILED, not scheduled, D125):**

> `[OPT-HYB-RESEED]` STATE:not-started (DRAFTED 2026-09-27 by lane
> utf8attrib, docs/dev/utf8_attrib.md (A)) (SIZE S; abi event: emitted text
> changes) — THE VM HYBRID'S ATTEMPT LOOP RE-SEEDS FROM THE PREFILTER AFTER
> EVERY FAILED ATTEMPT, not only when an MRL clamp exists
> (`src/gen/emit_vm.c:12793-12808`'s `retry_win`, today gated on
> `v->nclamp > 0`). Today a failed attempt on a clamp-free hybrid steps
> every character boundary to the subject end. The prefilter OVER-approximates
> whenever the VM route's reason is erased from the DFA (lookbehind,
> lookahead; census the others), so the "retry cannot fire" argument
> (`:12818-12848`) does not hold there.
> MEASURED NEED (scratch, Mac, hand-twin of main's artifact, answers
> identical): utf8@0.1 `asr-lb-varwidth` t-1m ×124, `asr-lb-fixed` ×48,
> `asr-lb-neg` ×25. At the bench these are the ×8.17/×2.85/×3.21 losses to
> pcre2-jit/oniguruma.
> D77 FIRST: census the VM-hybrid artifacts with `nclamp == 0` across the
> corpus plus the bench sets, split by whether the prefilter language is
> exact (retry never fires; re-seed costs nothing) or over-approximate. Then
> answer-identity over the corpus × every startpos, the identity gates, and
> a sabotage row that removes the re-seed on a lookbehind witness (answer-
> INVISIBLE, so the detector is structural or a step/time budget; S269's
> precedent).
> Interacts with `[OPT-VMSEED]` (no-DFA-front seed) only by sharing the
> "ask the candidate finder again" spelling.

### Finding: S2a's 2-byte compare on a per-position failing path (row 11)

`asr-lb-fixed` at main is +30% (scratch, reproduced twice) against
751b9c6d. The program diff is exactly one change. The lookbehind body's
`é`, two single-byte compare-and-branch steps, becomes
`scan_position + 2 <= n && !memcmp(subject + scan_position, "\303\251", 2)`.
On this artifact the body runs once per subject POSITION (the re-seed
defect above) and fails on its first byte about 99% of the time, so the
early-exit byte compare was cheaper.

This is a note for S2a's owed D77 bench pass, not a row. It disappears
once `[OPT-HYB-RESEED]` lands, because the attempts drop by roughly 1,000×.
It does name a shape where one P4 compare with L=2 is not free: a run
whose first byte rarely matches, on a hot failing path.

### Drafted row (recommended HELD): `[OPT-ENDWIN-ENC]`

> `[OPT-ENDWIN-ENC]` STATE:not-started (DRAFTED 2026-09-27, lane
> utf8attrib; RECOMMENDED HELD, D77 — the one witness is nanosecond-scale)
> — `[OPT-ENDWIN]`'s end window under a multi-byte encoding. It declines
> today (`src/facts/endwin.c` decline (2): a byte clamp can land
> mid-character). A sound byte bound is `4 · cwmax` for utf8, rounded to a
> character boundary. For a pattern anchored at BOTH ends it reduces to an
> O(1) length reject. Witness `cls-dot-rep` `^.{5}$`: pcrec 10-19 ns
> against rust 6 ns. Trigger: a measured end-anchored utf8 cell above
> noise.

No other new row is drafted. Every other lever lands on an existing row:
- `[OPT-A]`: the multi-literal / Teddy lead, the memchr2/3 lead and the
  pair-scan lead.
- `[OPT-LITSCAN]`: S4 caseless, F3's prefilter selection and the
  three-arm FORM rule.
- `[FINDINGS]`/`[OPT-LITSCAN]`: the `utf8` byte rate, the "encoding-keyed
  prior". It is the dependency under rows 4, 6, 7 and all of (B).

---

## Reproduction (scratch, not committed)

- Compilers: `git archive <pin> | tar -x` for ce658cb7 and 751b9c6d
  (`make -j4 CC=gcc-16`), and the worktree build for main.
- Compile: `pcrec --features all -p rx -e utf8 -o OUT.c --pattern "$(cat bench/utf8/patterns/NAME.rx)"`.
- Driver: `rx_search(s, n, pos, caps)` in a loop, `pos = end` (or `end+1` on
  an empty match), median of 15 runs by `clock_gettime_nsec_np(CLOCK_UPTIME_RAW)`,
  `gcc-16 -O2 OUT.c drv.c`.
- Twins, one edit each:
  - `lit-sharp-s`: `rx_reqrun`'s memchr set to `(subject + pos, 83, …)`
    with `cand = q − subject`.
  - Its second twin: `rx_ofsskip` scans 159 @5.
  - The lookbehind trio: the block
    `{ ptrdiff_t window[1][2]; if (rx_prefilter(subject, subject_length, attempt_position, window) != 1) return 0; attempt_position = (size_t)window[0][0]; }`
    inserted after the retry's continuation-skip loop in `rx_search_run`.
  - `ci-*`/`alt-distinct-lead`: the `rx_can_begin_match` loop replaced by
    one `memchr` per class member, taking the minimum.
