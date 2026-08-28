# [OPT-2] STEP 2 — MEASUREMENT: is the `\z` form's cost the scan-to-end?

Lane `opt2m`, 2026-08-28. Measurement only: **nothing under `src/` or
`tests/` changed**. Follows `docs/dev/opt3_dfa_scan_measurement.md`'s method
and report shape.

## 0. The answer in four lines

1. **The stated hypothesis is REFUTED.** Comparing the SAME entry
   (`rx_match`, the anchored match-here call) on the plain `orig` DFA
   artifact against the `(?:orig)\z` DFA artifact, over the bench's 85
   compliance subjects, the `\z` form costs **3.7% more on the whole set,
   3.35% more on the 40 matching subjects** — not the 3.7x (now 2.15x at
   this pin) the plan row set out to explain. "Must scan to the end" is not
   what is happening: on a MATCHING subject the plain form already scans to
   the end too, because the subject IS the match end-to-end by construction
   of the `match` regime (`ANCHORED|ENDANCHORED`).
2. **The 2.13x DFA-vs-VM gap this lane reproduced in-tree (matching the
   bench's own 2.15x re-pin) is the REVERSE PASS**, not the `\z` mechanism.
   A cost-isolation patch that deletes the reverse scan from the `\z`
   artifact (scratch, answer-INCORRECT by construction, timing-only) cuts
   the DFA's cost on matching subjects **from 2.077x behind VM to 1.046x —
   essentially parity** (short matching subjects: 1.207x behind → **0.571x,
   i.e. AHEAD of VM by 1.75x**). The reverse pass is **~50% of DFA cost on
   every matching subject measured**, short or long, uniformly.
3. **The `\z` form's real per-byte cost is one predictable branch plus a
   restructured accept check** (§4): a `scan_position == subject_length`
   test guarded by `__builtin_expect(..., 0)`, taken exactly once per call
   (the last byte), plus computing `forward_view_state` as a copy of
   `forward_state` before the accept test instead of after. That is the
   entire mechanism the plan row's hypothesis pointed at, and it costs
   single-digit percent, matching OPT-3's own finding that predictable
   off-chain branches are close to free.
4. **The lever the numbers point at is [ENG-ABS]'s already-recorded
   direction**: an anchored match-here entry that runs the forward machine
   from `ctx->pos` only and skips the reverse pass entirely (the start is
   already known — it's the question being asked). Named with its number
   below (§6); not built, per the brief.

## 1. Method

Box: same as `opt3_dfa_scan_measurement.md` (AMD Ryzen 5 1600, `taskset -c
3`). `load1` before each trial series: 0.19–0.28 idle, rising to 0.51–0.75
mid-run from other session activity — noted per series below; nothing
observed above 1.0, and no number here turns on the difference (the whole
point of a calibrated per-subject iteration count, next paragraph, is that
each measurement is internally self-normalizing against transient load).

**Driver**: `adriver.c` (new, scratch, not committed — see §7), built
against each artifact's `gen.c`. Unlike `bdriver`/`fdriver` (which take a
fixed iteration count), `adriver` takes a `<id>\t<path>` LIST and
CALIBRATES each subject independently: start at 2,000 iterations of
`rx_match(ctx)`, and if the timed run is under 30 ms, scale the iteration
count up (targeting 30 ms) and re-time, repeating until the calibrated run
clears the floor. This matters here specifically because the 85 compliance
subjects range from 0 to 10,252 bytes and a fixed iteration count that is
enough for the 10 KB subject leaves the 5-byte ones at a handful of
iterations, all noise. Each subject's reported `ns_per_call` is one
calibrated measurement; **5 independent process invocations** (5 trials)
were run per artifact and the MEDIAN across trials taken per subject before
summing into set totals — this is what "matching short" spread 1.0006–1.0527
(whole) / 1.0024–1.2781 (plain) means in §3: per-subject spread across the 5
trials, not intra-run noise.

**Subjects and expectations**: `pcrec-bench`'s `bench/email/subjects/*.bin`
(85 files, read-only) and `expectations.tsv`'s `orig`/`match` rows (`expected
== "match"` vs `"nomatch"`), both read directly — no copy, no regeneration.
`manifest.tsv`'s `len` column gives the length split used in §3.3.

**Artifacts**: three, all `--features all` (harmless for `orig`: no named
groups), all at this worktree's HEAD (includes `[OPT-3]` STEP 1+2, the
premultiplied table):

| artifact | pcrec invocation | `RX_ENGINE` | `RX_DFA_PREFILTER` | `RX_DFA_TABLE` |
|---|---|---|---|---|
| `orig-plain` | `pcrec -p rx --features all -- '<orig.rx text>'` | `dfa` | `byte-class` | `premultiplied` |
| `orig-whole` | `pcrec -p rx --features all -- '(?:<orig.rx text>)\z'` | `dfa` | `byte-class-bounded` | `premultiplied` |
| `orig-whole-vm` | `pcrec -p rx --features all --engine=vm -- '(?:<orig.rx text>)\z'` | `vm` | — | — |

Confirmed by grepping each `gen.c`'s `#define RX_*` lines (reproduced
above verbatim from the actual build output, not transcribed from a report).
This matches `NOTES.md`'s documented mechanism exactly: `orig`'s `\z` form
still selects the DFA, and the prefilter narrows from `byte-class` to
`byte-class-bounded`.

`rx_match` is called with `ctx->pos = 0`, `ctx->ncap = 0`, `ctx->caps =
NULL` — the self-contained form the spec requires every `rx_matchfn` to
accept (`docs/spec/match_api.md` §2, the comment on the typedef).

## 2. Reproducing the DFA-vs-VM gap, in-tree

Before attributing anything, the number itself was reproduced independently
of the bench's own report (which is at the SAME pin, `35e1ab1`, but the
lane's brief asked for a number this lane owns):

| split | n | DFA (`\z`) set ns | VM (`\z`) set ns | ratio DFA/VM |
|---|---|---|---|---|
| ALL 85 | 85 | 133,183.3 | 62,436.9 | **2.133x** |
| MATCHING | 40 | 97,166.3 | 46,780.9 | 2.077x |
| NON-MATCHING | 45 | 36,017.0 | 15,656.0 | 2.301x |

Against `pcrec-bench`'s `reports/2026-08-28-email-specimen-0.2-...-35e1ab1.md`
(`orig`/`match-compliance`): `pcrec_auto` (DFA) 133,799.6 / `pcrec_vm-in`
62,129.7 = **2.153x**. This lane's `orig-whole-vm` is `--engine=vm` under
default prefilter selection, not literally the bench's `pcrec-vm-in` build
config, so exact equality isn't expected — 2.133x vs 2.153x (0.9% apart) is
agreement, not coincidence, and confirms the earlier 3.7x (pin `692c2e8`,
before `[OPT-3]` STEP 2 landed) has already been roughly HALVED by the
premultiplied-table change alone, before this lane's own lever fires at all.

## 3. The `\z` overhead, isolated: plain-DFA vs `\z`-DFA, same call

This is the plan row's actual question: does `\z` cost more than plain on
the SAME engine, for the SAME call (`rx_match`)? 5 trials each, median per
subject, `load1` 0.19–0.75 across the two series (rising mid-series from
other session activity, bounded — see §1).

| split | n | plain set ns | `\z` (whole) set ns | ratio (`\z`/plain) |
|---|---|---|---|---|
| ALL 85 | 85 | 128,387.7 | 133,183.3 | **1.037x** |
| MATCHING | 40 | 94,015.8 | 97,166.3 | 1.033x |
| NON-MATCHING | 45 | 34,371.9 | 36,017.0 | 1.048x |

**3.7% on the whole set, 3.3% on matching subjects. Not 3.7x.** The
per-subject table (85 rows, both directions) is in the raw analysis output;
the pattern is uniform — every matching subject's ratio is 1.03–1.17x, with
no outlier suggesting a qualitatively different code path kicking in at any
particular length. The two `s-029`/`s-081` non-matching rows with ratio
`<1` (`\z` faster) are within calibration noise at ~5–70 ns absolute — noted,
not chased; they are not large enough to matter to any total here.

### 3.1 Why the hypothesis's mechanism doesn't produce a large number

The plan row's framing ("the plain form exits at its last accept while the
`\z` form must scan to the end") assumes there is a matching subject where
the plain form stops SHORT of the subject's end. There isn't one in this
regime: `match` means `ANCHORED|ENDANCHORED` — the subject's bytes ARE the
match, end to end, by the compliance regime's own definition
(`NOTES.md` "Regime coverage": `match` = `PCRE2_ANCHORED|PCRE2_ENDANCHORED`
at 0). So the plain form's forward loop ALSO runs every byte of a matching
subject — there is no earlier dead state to hit, because nothing after the
match's last byte exists to diverge on. Both forms scan to the same place;
the `\z` form just does slightly more work getting there (§4).

### 3.2 Non-matching subjects: still no large gap

Non-matching subjects are where a genuine "\z form can't bail out where
plain form would" story would have to live (a subject with a valid-looking
prefix and garbage after it): 4.8% average, same order as matching. The
dead-state break (`if (rx_forward_is_dead(forward_state)) break;`) is
UNCHANGED between the two artifacts — same test, same position in the loop,
same effect — so a subject whose garbage triggers a fast dead-state exit in
the plain form triggers the identical exit in the `\z` form. There is no
subject class where dead-state detection differs between the two.

### 3.3 The matching split is DOMINATED by 5 pathological subjects

Worth stating before anyone reads the 97,166 ns matching-set number as "40
short valid emails": 5 of the 40 matching subjects (`s-057` 10,252 B,
`s-059` 5,134 B, `s-064` 4,110 B, `s-058` 4,011 B, `s-061` 2,008 B) are
25,515 of the matching set's 26,120 total BYTES (97.7%) and **94,880 of its
97,166 ns (97.6%)**. Split:

| split | n | bytes | plain ns | `\z` ns | `\z`/plain | DFA/VM | DFA-NOREV/VM |
|---|---|---|---|---|---|---|---|
| matching, short (<256 B) | 35 | 605 | 2,127.9 | 2,285.4 | 1.074x | 1.207x | **0.571x** |
| matching, long (≥256 B, pathological) | 5 | 25,515 | 91,887.9 | 94,880.9 | 1.033x | 2.114x | 1.066x |

(`DFA-NOREV` is §5's cost-isolation patch — introduced here because the
row is more legible beside its own split.) The 35 ordinary short valid
emails carry almost none of the matching set's absolute time; the reported
"matching" totals in §2–3 are, in practice, a measurement of pcrec's cost
on the bench's OWN pathological long subjects (deep dot-atom chains, long
quoted strings — the same subjects `[OS-4]`/`NOTES.md` flag as the
`exponential-backtracking` hazard-class witnesses), not of the typical case.
Both splits tell the same qualitative story (§5), so this does not change
the lever recommendation, but it changes what "the matching-subject number"
means if quoted alone.

## 4. What the emitted C says

`rx_match` itself is **byte-identical** between the two artifacts —
confirmed by direct comparison, not inference:

```c
/* orig-plain/gen.c:1031-1039, orig-whole/gen.c:1153-1161 -- IDENTICAL */
ptrdiff_t rx_match(const rx_ctx *ctx)
{
    /* Initialized: gcc -O1 false maybe-uninitialized (pcrec K28). */
    ptrdiff_t capture_spans[RX_NCAPS][2] = {{0}};
    int found = rx_search(ctx->subject, ctx->len, ctx->pos, capture_spans);
    if (found < 0) return (ptrdiff_t)found;
    if (found != 1 || (size_t)capture_spans[0][0] != ctx->pos) return -1;
    return capture_spans[0][1] - capture_spans[0][0];
}
```

This is `docs/spec/match_api.md` §3.5's documented body, verbatim, in both
artifacts. **All of the difference is inside `rx_search`.** Forward loop,
`orig-plain/gen.c:990-1005`:

```c
for (;;) {
    if (rx_forward_accepts(rx_forward_is_accepting, forward_state)) last_accept_position = scan_position;
    if (forward_state == 0 && last_accept_position == (size_t)-1) {
        while (scan_position < subject_length && !rx_can_begin_match[subject[scan_position]]) scan_position++;
        if (scan_position >= subject_length) return 0;
    }
    if (scan_position >= subject_length) break;
    forward_state = rx_forward_step(rx_forward_next_state, forward_state, rx_forward_byte_class[subject[scan_position++]]);
    if (rx_forward_is_dead(forward_state)) break;
}
```

Same loop, `orig-whole/gen.c:1109-1123`:

```c
for (;;) {
    if (forward_state == 0 && last_accept_position == (size_t)-1) {
        while (scan_position + 1 < subject_length && !rx_can_begin_match[subject[scan_position]]) scan_position++;
    }
    rx_forward_state forward_view_state = forward_state;
    if (__builtin_expect(scan_position == subject_length, 0) &&
        rx_forward_view_live(rx_forward_end_view, rx_forward_row(forward_state)))
        forward_view_state = rx_forward_view_take(rx_forward_end_view, rx_forward_row(forward_state));
    if (rx_forward_accepts(rx_forward_is_accepting, forward_view_state)) last_accept_position = scan_position;
    if (scan_position >= subject_length) break;
    forward_state = rx_forward_step(rx_forward_next_state, forward_view_state, rx_forward_byte_class[subject[scan_position++]]);
    if (rx_forward_is_dead(forward_state)) break;
}
```

Three differences, all per-byte cost, none of them "scan further":

1. The prefilter's skip-loop bound changes from `scan_position <
   subject_length` to `scan_position + 1 < subject_length` — this is
   `RX_DFA_PREFILTER`'s `-bounded` variant (`docs/spec/tuning.md` §3): the
   skip can't blindly consume the LAST byte, because that byte might need
   the end-view lookup. It never fires on these subjects anyway (§3 of
   `opt3_dfa_scan_measurement.md`: the skip loop only pays on long
   non-candidate runs, which this pattern's subjects don't have).
2. Every iteration computes `forward_view_state` (a copy of
   `forward_state`) and tests `scan_position == subject_length` before the
   accept check, instead of testing `forward_state` directly at the top of
   the loop. The branch is `__builtin_expect`-hinted false and is true on
   exactly ONE iteration per call (the last byte) — this is the
   "predictable branch, near-free" case `opt3_dfa_scan_measurement.md` §5
   already established (0.05 cycles/byte for the analogous accept/prefilter
   tests there).
3. On the one iteration where it IS taken, `rx_forward_row` (an integer
   divide by the class stride, 18) and a table lookup (`rx_forward_view_*`)
   run once — a single-shot cost, not a per-byte one.

The reverse loop (`orig-plain/gen.c:1013-1020`, `orig-whole/gen.c:1131-1139`)
carries the identical three differences, mirrored. **Nothing here scans
FURTHER than the plain form** — same subject bytes, same loop bound
(`subject_length`), same dead-state break. The `\z` form does marginally
MORE PER BYTE (one extra predictable branch, one extra register), not more
bytes.

## 5. The reverse pass: what actually costs 2x

A cost-isolation patch (`orig-whole-norev/gen.c`, scratch, **NOT
answer-correct**, timing-only — see caveat below) deletes the reverse loop
entirely and sets `match_start_position = search_from` unconditionally,
in the shape of `opt3_dfa_scan_measurement.md`'s `v0b`/`v1b` variants (a
hand-patched artifact timed to attribute cost, never built into the
compiler, never used to decide an answer):

```c
/* orig-whole-norev/gen.c -- COST ISOLATION ONLY, not a working mechanism */
if (last_accept_position == (size_t)-1) return 0;
{
    size_t match_end_position = last_accept_position;
    size_t match_start_position = search_from;   /* reverse pass deleted */
    if (capture_spans) { capture_spans[0][0] = (ptrdiff_t)match_start_position; capture_spans[0][1] = (ptrdiff_t)match_end_position; }
    return 1;
}
```

This is deliberately wrong wherever the true match start differs from
`search_from` (i.e. genuinely for an UNANCHORED search) — it exists only to
subtract the reverse pass's wall-clock cost, exactly as `search_from ==
ctx->pos` for every call this lane's driver makes (`rx_match` always calls
`rx_search` with `search_from = ctx->pos`), so its returned SPAN's start is
accidentally always right for these particular calls; its `found` outcome
(0 vs 1) is unaffected, since that still comes from the forward pass alone,
which was not touched.

| split | n | `\z` (whole) ns | `\z` NOREV ns | reverse-pass share | vs VM (whole) | vs VM (NOREV) |
|---|---|---|---|---|---|---|
| ALL 85 | 85 | 133,183.3 | 79,970.3 | 40.0% | 2.133x | 1.281x |
| MATCHING | 40 | 97,166.3 | 48,953.5 | **49.6%** | 2.077x | **1.046x** |
| NON-MATCHING | 45 | 36,017.0 | 31,016.8 | 13.9% | 2.301x | 1.981x |
| matching, short (<256 B) | 35 | 2,285.4 | 1,082.1 | 52.7% | 1.207x | **0.571x** |
| matching, long (≥256 B) | 5 | 94,880.9 | 47,871.4 | 49.5% | 2.114x | 1.066x |

**On every matching-subject split — short or long — the reverse pass is
~50% of the DFA's cost**, and removing it (in this cost-isolation form)
takes the DFA from 2.08x behind VM to parity (1.046x), and on the 35
ordinary short valid emails, to **43% AHEAD of VM** (0.571x). This is the
mechanism: a matching subject's forward pass walks every byte once; the
reverse pass then walks (up to) the same bytes AGAIN, back to front, to
recover the match start — for `rx_match`, a value the caller does not need
to compute at all, because `rx_match`'s own contract only asks "does the
pattern match starting exactly at `ctx->pos`", and `ctx->pos` IS the start.
On non-matching subjects the reverse pass barely runs (13.9%): most either
never set `last_accept_position` (no accept anywhere, forward-only return 0)
or set it briefly near a short prefix, so there is little to walk back
over — consistent with `NOTES.md`'s "80 of 170 cells match" and this lane's
own 40/45 split.

## 6. Lever candidates (named, not built)

### (a) Anchored match-here via the unwrapped forward DFA — RECOMMENDED, already chartered

This is `[ENG-ABS]`'s recorded "SECOND MECHANISM" (`docs/dev/plan.md`,
2026-08-18 design thread), and §5 above is its missing measurement: emit
the pattern's UNWRAPPED forward DFA (no start-anywhere self-loop — a
distinct table from today's search table, same trust model, same IR) and
run it from `ctx->pos` directly for `rx_match`/`rx_match_caps`, with NO
reverse pass (the start is `ctx->pos` by construction) and NO candidate-hunt
skip loop (there is nothing to hunt — the caller already named the start).
**The number it would have to beat**: §5's NOREV isolation is not this
mechanism (it still runs the full unanchored forward scan with its
self-loop and skip machinery, just skips the walk-back), so it UNDERSTATES
the available gain — the true unwrapped-forward form additionally drops
the prefilter's per-iteration `forward_state == 0` test and the `-bounded`
skip-loop bound entirely, since an anchored attempt never re-enters state 0
hunting for a later candidate. §5's 1.046x-parity number is therefore a
CEILING on the remaining gap, not a floor: the real mechanism should land
DFA at or below VM on the matching set, and comfortably ahead on short
subjects (§5's short-subject NOREV row, 0.571x, is the closer analogue,
since short subjects rarely engage the skip loop's steady-state cost
either way). Answer-identity argument: for `rx_match`/`rx_match_caps`
specifically (never `rx_search`), "match starting at `ctx->pos`" is decided
entirely by the forward machine from `ctx->pos` — the existing unanchored
`rx_search` is provably a superset computation (it additionally asks "is
there a match ANYWHERE", which the anchored caller doesn't need answered),
so the two must agree on every subject where both terminate; the identity
gate is comparing `rx_match`'s old and new bodies over the corpus + the
compliance subjects, not a new semantic to design. GATE UNCHANGED from
`[ENG-ABS]`'s own charter: `[BENCH-1]` measuring a `^`-on-some-branches loss
was the ORIGINAL gate reason; this lane's §5 is a SECOND, independent
forcing function (the compliance regime's own numbers) that the charter did
not have when written 2026-08-18.

### (b) Fold the `\z` view cost into the general fold — NOT worth its own charter

§4's 3–5% is real but small next to (a)'s ~50%. `[DD-13]`(b)'s own
end-view fold (referenced in the `[OPT-2]` plan row's STEP 1 note) is the
place this belongs if it is ever chased — but §3–4 here show there is very
little left to fold once (a) exists, because (a) removes the reverse-pass
view lookup entirely (no reverse pass, no reverse-view test) and only the
forward-pass's single-iteration view check would remain, already measured
near-free. **Number it would have to beat**: the 3.7% whole-set /3.3%
matching-set overhead in §3 — small enough that `[OPT-2]`'s finding is
better read as "the `\z` mechanism was never the cost" than as "here is a
second lever."

### (c) Dead-state early-exit on the reverse pass — NOT separately needed

Considered and set aside: the reverse loop already has the identical
dead-state break the forward loop has
(`if (rx_reverse_is_dead(reverse_state)) break;`,
`orig-whole/gen.c:1139`), so there is no missing early-exit to add here —
the reverse pass's cost is not "it fails to bail out early", it is "it
exists at all for a call that already knows the answer it's computing."
(a) obsoletes this candidate rather than complementing it.

## 7. What was NOT measured

- **No cycle-level attribution.** `perf` is unavailable on this box for the
  same reason `opt3_dfa_scan_measurement.md` §1 records (`perf_event_paranoid
  = 4`); this lane stayed in wall-clock ns throughout, which is sufficient
  at this question's scale (percent-level vs the plan's assumed x-level).
- **No factored.rx run.** The brief named `orig` as the exercising pattern
  and `factored` tracks it per `opt3_dfa_scan_measurement.md` §2's own
  precedent ("factored is the same measurement, not a second one" —
  same 18-class stride DFA, same `byte-class`/`byte-class-bounded`
  prefilter pair). Not reproduced here; it would be a second data point on
  the same mechanism, not a different one.
- **The unwrapped-forward-DFA mechanism itself was NOT built**, per the
  brief. §5's cost-isolation patch is a measurement device that returns
  wrong answers by construction on any subject where the true start isn't
  `ctx->pos`; it must not be read as a prototype, and nothing here is a
  drop-in for `[ENG-ABS]`'s charter — only its missing number.
- **The 45 non-matching subjects' individual step counts were not
  instrumented** (no forward/reverse counters compiled in, unlike
  `opt3_dfa_scan_measurement.md` §3's approach) — the 13.9% reverse-pass
  share for that split is read from wall-clock totals only. A counter-based
  breakdown would sharpen `§5`'s NON-MATCHING row but is unlikely to change
  its qualitative reading (small reverse-pass share because few subjects
  in that split ever set `last_accept_position`).
- **`make test` / `make strict` were not run** by this lane (another lane
  may own the heavy slot; this lane's own change is docs-only). Nothing
  under `src/` or `tests/` changed.

## 8. Artifacts of this lane

- `adriver.c` — the calibrated anchored-match-here timing driver (scratch,
  not committed; reconstructible from §1's description — takes an
  `<id>\t<path>` list, per-subject iteration calibration to a 30 ms floor,
  5-trial invocation convention).
- `orig-plain/`, `orig-whole/`, `orig-whole-vm/` — the three built
  artifacts (§1's table), each a `pcrec` invocation away from
  reproduction; not committed.
- `orig-whole-norev/` — the §5 cost-isolation patch, a mechanical two-line
  edit of `orig-whole/gen.c`'s reverse-pass block (documented in §5,
  reproducible from the diff shown there); not committed, not
  answer-correct, not a prototype.
- `analyze.py` — the post-processing script (median-of-5 per subject,
  matching/non-matching split against `expectations.tsv`, set sums); not
  committed.
- Session scratchpad only, per the lane's scope mandate; nothing here
  touches `/home/duxevents/pcrec-bench`.
