# [OPT-K] — the OFFSET-k candidate-start skip

Lane `optk`, 2026-08-28. Written BEFORE the emitter, on
`docs/design/premultiplied_dfa_table.md`'s and `docs/design/emitter_form.md`'s
model: the derivation, the cost model and the emitted form are fixed here with
measurements, and the code is then written against this document. The plan row
`- [OPT-K]` in `docs/dev/plan.md` is the charter; Frank ruled the shape on
2026-08-28 (the pair from the start; the general mechanism, one row).

## 0. The answer in eight lines

1. pcrec's candidate-start filter looks only at **offset 0**, and on log text
   the three patterns pcrec is furthest behind PCRE2-JIT on all begin with a
   byte that is in every line — so the filter passes almost every position to a
   transition loop that costs 10.7 cycles/byte.
2. The general fact is a **set of (offset k, byte-set) tests every match must
   satisfy**, of which today's filter is the k = 0 member.
3. The k ≥ 1 members cannot come from the DFA (§2.2 — an ENG_UNANCH DFA state
   merges the threads from every subject position, which destroys offset
   selectivity by construction). They come from a walk of the pattern's own
   **NFA from `Nfa.anch_start`** (§3).
4. Which offsets to test is a **selection over a cost model** under a static
   byte-frequency prior, with the offset-0 filter that ships today as the
   baseline and a **2× materiality bar** (§4). Offset 0 is always in the set.
5. The emitted form is one `memchr` at the chosen offset k\*, a verify chain
   over the other offsets, and a resume from the failed candidate — scalar, no
   SIMD (§5).
6. It is an `[ENG-FORM]` **selection**, not a second mechanism: axis B gains two
   candidates at the head of its list and the k = 0 forms stay exactly as they
   are, byte for byte, for every pattern the selection declines (§5.1).
7. It is **answer-identical by construction** — the skip refuses only starts the
   scan would refuse — and the gate is `make test-axes` under
   `-fno-offset-skip` (§6).
8. Measured selections, before any timing: `uuid` 807,006 → 20 ppm predicted
   candidate rate, `iso-ts` 74,760 → 372, `stack-frame` 807,006 → 6,037; and
   `ipv4`, `hex32-id`, `http-5xx`, `ipv6`, `kv-quoted` and **both email
   patterns** are declined and do not move (§4.7).

---

## 1. The measured need

`pcrec-bench`'s `loglines@0.1` at pin `35e1ab1`, search band, ns per subject
set, `pcrec-auto` against `pcre2-jit`:

| row | pcrec ns/set | jit ns/set | pcrec vs jit |
|---|---|---|---|
| `stack-frame` | 558,756 | 17,574 | **31.8× behind** |
| `uuid` | 434,798 | 35,766 | **12.2× behind** |
| `iso-ts` | 213,267 | 21,013 | **10.1× behind** |
| `kv-quoted` | — | — | 1.50× behind |
| `bignum` | — | — | 1.07× behind |
| `hex32-id` | — | — | 1.14× **ahead** |
| `ipv4` | — | — | 3.56× ahead |
| `ipv6` | — | — | 4.39× ahead |
| `http-5xx` | — | — | 15.0× ahead |

The JIT runs 0.08–0.15 ns/byte on the three it wins: a SIMD scan of the
fixed-length prefix for its most selective byte-position **pair**. pcrec's
transition loop is measured at **10.7 cycles/byte**
(`docs/dev/opt3_dfa_scan_measurement.md` §6), so the whole question is how
often the loop is entered at all.

**What every one of the three has in common:** the byte at offset 0 is not
selective on log text.

| pattern | offset-0 candidate set | mass under §4.1's prior |
|---|---|---|
| `\b[0-9a-f]{8}-…` (uuid) | 63 bytes (every word character) | 80.7% |
| `\d{4}-\d{2}-…` (iso-ts) | 10 digits | 7.5% |
| `\bat (?:…)` (stack-frame) | 63 bytes (every word character) | 80.7% |

The 63-byte sets are not a bug in the derivation and §2.1 explains why they are
correct. They are the reason the filter buys nothing.

---

## 2. What ships today, and exactly where it stops

### 2.1 The offset-0 filter is derived from the DFA start state

`src/gen/emit_dfa.c`'s `cand_from_escapes` (D63's shared derivation) computes
the bytes on which the forward DFA's start state does **not** stay put:

```c
set[b] = (d->st[fs].tr[d->clsmap[b]] != fs);
```

A run of bytes outside that set leaves the machine parked in `fs`, so the scan
may jump over it — one `memchr` when the set is a singleton (`DFA_PF_MEMCHR`),
a 256-entry bitmap walk otherwise (`DFA_PF_BYTE_CLASS`), each in a `-bounded`
variant under `views` (D11).

**Why a `\b`-leading pattern gets 63 bytes there, and why that is right.**
`\b`'s truth reads the byte to the LEFT, and the DFA carries that in the state
IDENTITY (`src/core/internal.h`, `Dfa.s1u`'s note). So the start state escapes
on every word character — not because a match can begin there, but because the
machine must REMEMBER that the previous byte was a word character. Narrowing
that set would be a miscompile: on `\b[0-9]{2}` against `"ab12"` a filter that
skipped the letters would land at `'1'` in the no-context start state, evaluate
`\b` as true, and match `"12"`, which PCRE2 does not.

**This is load-bearing for §5.4 and it is why offset 0 keeps its own
derivation.** The k ≥ 1 analysis below never re-derives offset 0.

### 2.2 Why the same walk cannot simply be continued past offset 0

The obvious generalisation — from the start state, follow the escape
transitions k steps and union the escapes of the states you land in — is
**correct and useless**, and it is worth stating because it is the first thing
anyone will try.

An ENG_UNANCH DFA state is the merge of the threads from **every** subject
position (`nfa_wrap_unanchored`'s lowest-priority self-loop). Four bytes into
`\d{4}-`, the state carries threads at 4, 3, 2, 1 and 0 digits. "A byte that
does not return the machine to the start state" at offset 4 is therefore
`[0-9-]`, not `-`: the thread at 3 digits is advanced by a digit, so a digit
keeps the state alive. The selectivity the row exists for is gone before the
walk begins. Measured on a scratch build of exactly that walk: `\d{4}-\d{2}-`
yields a set of 11 bytes at offset 4.

The thread whose bytes we want to constrain is the one from the candidate start
**alone**, and the only place it exists on its own is the pattern's own NFA.

---

## 3. The derivation

`src/opt/prefix_k.c`, `pcrec_prefix_ksets`.

### 3.1 The walk

`Nfa.anch_start` is a new field (§3.5). The walk maintains `frontier[j]`, the
set of NFA states a thread from the candidate start can occupy after consuming
exactly `j` bytes, closed over epsilon:

```
frontier[0] = closure({anch_start})
S[j]        = union of the classes of the N_CLASS states in frontier[j]
frontier[j+1] = closure({ st.t1 : st in frontier[j], st is N_CLASS })
```

The closure passes `N_SPLIT` down both edges, `N_EPS` down `t1`, and **every
assertion node** (`N_BOT`, `N_EOL`, `N_END`, `N_BOT_M`, `N_EOL_M`, `N_WORDB`,
`N_NWORDB`, `N_GSTART`) down `t1` as though it held. The switch has no
`default:` arm on purpose: a new `NKind` must be classified here, and a new
CONSUMING kind silently treated as an assertion is this file's one unsound
direction.

### 3.2 Soundness

**Claim.** If a match begins at subject position `p` and the walk published
`S[j]`, then `s[p+j] ∈ S[j]`.

**Proof.** A match beginning at `p` runs a thread from `anch_start`. After `j`
consumed bytes that thread sits in some NFA state; that state is in
`frontier[j]`, because `frontier` is closed over epsilon and over every
assertion (an assertion that HOLDS is a subset of "an assertion passed
unconditionally"). The thread's next byte is consumed by an `N_CLASS` state of
that set, whose class is a subset of `S[j]`. ∎

Every failure mode of the analysis widens some `S[j]`. A pattern the walk
cannot model precisely gets a bigger set, the cost model declines it, and the
artifact keeps the filter it has. **There is no direction in which this
analysis can refuse a start the scan would have accepted.**

### 3.3 Where the walk stops

Four stop conditions, in the order they are asked:

1. **`N_ACCEPT` is in the frontier.** The match may already be over, so
   `s[p+j]` need not exist and no constraint at offset `j` is sound. This is
   the condition that makes `min_length` implicit rather than a second
   analysis: the walk simply stops at the pattern's minimum width.
2. **The frontier has no consuming state.** Same thing by another route.
3. **`S[j]` is the whole alphabet.** Every later offset is at least as wide
   (the frontier only fans out), so the walk has nothing left to say.
4. **`j == PCREC_PREFIX_K_MAX` (24).** A walk bound, not a tuning knob: past
   two dozen bytes a still-narrow prefix is vanishingly rare on the corpus (the
   largest useful offset any corpus pattern produces is 13, `uuid`'s second
   hyphen).

### 3.4 The domain, stated as what widens the sets

The plan row asks for "which prefix shapes yield fixed offsets, and where it
stops". The honest answer is that **nothing is refused categorically** — the
walk runs on every pattern and the selection declines the ones it cannot
exploit. What is worth stating is which shapes stay narrow:

| shape | what the walk yields | worked example |
|---|---|---|
| literal bytes | singletons | `ERROR.*failed` → `{E}{R}{R}{O}{R}` at 0–4 |
| a class | that class | `\d{4}-` → 10 digits at 0–3, `{-}` at 4 |
| exact counts `{n}` | the class, `n` times | `[0-9a-f]{8}-` → `{-}` at 8 |
| case-folded literals | the fold pair, from the parser's own bitmap | `(?i)needle` → `{Nn}{Ee}{Ee}{Dd}{Ll}{Ee}` |
| alternation of EQUAL width | the union, offset by offset | `(?:ab\|cd)ef` → `{ac}{bd}{e}{f}` |
| a leading assertion | passed; offsets are measured from the candidate start, unmoved | `\bat ` → `{a}{t}{ }` |
| a lookbehind | **invisible** — `src/ir/nfa.c` lowers `A_LOOK` to an epsilon | `(?<=foo)bar` → `{b}{a}{r}`, the `foo` contributes nothing (§10) |
| alternation of UNEQUAL width | the union of what each branch has at that offset — correct, and usually wide | `ab\|abc` → `{a}{b}`, then accept |
| `.` / a negated class | ~255 bytes: the walk continues but the offset is useless | `x.{3}y` → `{x}`, 255, 255, 255, `{y}` |
| a variable-width atom (`*`, `+`, `?`, `{n,m}`) | the sets SMEAR across offsets | `colou?r-code` → `{c}{o}{l}{o}{ru}{-r}{-c}{co}{do}{de}` |
| an unbounded repeat before the selective byte | the smear reaches the alphabet and the walk stops | `[^ ]+@` → nothing past offset 0 |

The last two rows are the derivation's real boundary and they are why the two
**email** patterns are untouched (§4.7): both open with `[a-z0-9!#$%&'*+/=?^_\`{|}~-]+`,
whose `+` smears every later offset, and `@` sits at a variable offset. The
walk publishes 5 offsets for them, all of them ~76% of the alphabet, and the
selection declines.

### 3.5 `Nfa.anch_start` — a field, not a shape test

`nfa_wrap_unanchored` moves `Nfa.start` to a `N_SPLIT` whose `t1` is the
pattern and whose `t2` is an all-bytes `N_CLASS` looping back. The walk needs
`t1`. Sniffing that shape at the walk would be a second statement of the wrap's
construction that a change to the wrap could silently invalidate, so
`pcrec_build_nfa` publishes `anch_start = f.start` and `nfa_wrap_unanchored`
deliberately leaves it alone. An unwrapped machine — ENG_ATTEMPT's, and the
reverse machine — answers correctly with nobody having to remember to.

---

## 4. The selection

### 4.1 The prior

A static 256-entry table in parts per million, `pcrec_byte_freq_ppm`.

**Where it comes from, and where it deliberately does not.** The obvious source
for a log-text prior is the comparative bench's own log lines. Using them would
be exactly the failure `docs/dev/learnings.md` §3 catalogues — a control that
shares a source with the thing it controls — and every measurement in §7 would
then be a measurement of a table fitted to those subjects. So the mass is
assigned from two independent, citable priors: the classical English
letter-frequency ordering (scaled to 52% of the mass for lower case, upper case
at a tenth of its lower-case twin), space at 15% and newline at 1.2%; and the
structural punctuation of machine-written lines (`.` `:` `-` `/` `=` `"` `,`
`_` and the brackets) raised well above their prose frequencies, with digits at
0.9% each. Every remaining byte, the whole 0x80–0xff half included, gets a
floor of 2 ppm rather than zero — a zero would let the model believe a byte is
IMPOSSIBLE and choose a skip on a certainty it does not have. The assignment is
then normalised to sum to exactly 1,000,000, which
`pcrec_byte_freq_total_ppm()` returns and the structural check asserts.

**D83's hook, named and not built.** D83 rules that the real prior is a
file-general findings file measured off the deployment's own exemplar. The
selection reads `pcrec_byte_freq_ppm` and nothing else, so adopting a findings
file is a second implementation of that one function and touches nothing else
in this row. It is not built (D77). **The measurement that would trigger it:**
a bench row where the shipped table's ordering picks a different k\* from the
one the exemplar's own byte frequencies pick, AND the difference is outside the
timing spread. None exists today — on the ten `loglines` patterns the shipped
table and the subjects' own measured frequencies agree on every k\*.

**The prior orders bytes; it does not predict a subject.** Everything
downstream of it is answer-identity-preserving, so a badly-fitted prior costs
speed on some input and can never cost a match.

### 4.2 The cost model

Units are hundredths of a cycle per subject byte.

| constant | value | source |
|---|---|---|
| `C_MEMCHR` | 6 (0.055 c/B) | MEASURED, `opt3_dfa_scan_measurement.md` §4 CONTROL 1 (glibc AVX2 memchr) |
| `C_BITMAP` | 116 (1.16 c/B) | MEASURED, same table, row 1 (the 256-entry `can_begin_match` walk) |
| `C_VERIFY` | 250 (2.5 c) | one load + one table probe, per CANDIDATE |
| `C_ENTER` | 2000 (20 c) | [OPT-3]'s measured 10.7 c/B × the ~2 bytes a false start survives |
| `C_MISPRED` | 1500 (15 c) | a mispredicted branch on this box |

```
verify_cost(p) = C_VERIFY + C_MISPRED * min(p, 1-p)
cost(scan, V)  = scan_cost + p_scan * Σ_{v∈V} verify_cost(p_v)
                           + p_scan * Π_{v∈V} p_v * C_ENTER
```

**`C_MISPRED` is not a refinement — it is what separates the outliers from the
controls.** A verify is a conditional branch on the candidate path, so its cost
is not a probe but a probe plus what the predictor loses; a test that passes a
third of the time is a coin flip. Without the term the model recommends
verifying a sixteen-byte hex class at offsets 1 and 2 of `\b[0-9a-f]{32}\b` — a
pair of coin-flip branches on 80% of all positions — predicts a 2.56× win, and
would in truth put two mispredicting branches on the hot path of a pattern
pcrec is already 1.14× AHEAD of the JIT on. With the term that pattern's
predicted gain falls to 1.29×, below §4.5's bar, and the artifact does not move.

### 4.3 How sensitive the model is — MEASURED, and the claim is narrowed

`C_ENTER` is the constant with real spread, so it was swept over 8, 12, 20, 30,
40 and 60 cycles and the selection compared, over **1,352 distinct corpus
patterns** and the bench's own eleven.

- **The three patterns this row exists for select the identical k-set at every
  value from 8 to 60 cycles.** So do both email patterns (nothing) and
  `kv-quoted`, `ipv6` and `floor` (nothing).
- **The corpus's margin does move**: 11 of 1,352 patterns change their k-set
  between 12 and 20 cycles, 33 between 20 and 30, and 120 between 8 and 20.
- **The three log CONTROLS sit on the bar**: `ipv4` and `http-5xx` are declined
  at 20 cycles and selected at 30; `hex32-id` is declined at 30 and selected at
  40.

**The draft of this note claimed the model was insensitive over that range and
the sweep refuted it; the claim is corrected rather than the sweep repeated
until it agreed.** What is true is narrower and is the thing that matters: the
selection is stable where the gap is 10×–30× and unstable where it is 1.2×–1.6×,
which is the right way round for a model this rough. It also means the controls'
exclusion is a consequence of a MEASURED constant and not of a chosen one, and
that §7's timing — not the model — is the acceptance.

### 4.4 The rule

For each candidate scan offset:

- **A scan offset past 0 must be a singleton.** A multi-byte set at k > 0 would
  need a bitmap WALK at that offset — emitted code no measured pattern reaches,
  since a set wide enough to need one is never selective enough to be chosen.
  This is `attempt_cand`'s scope line in `src/gen/emit_dfa.c` for the same
  reason: shipping an untested emitted loop is worse than shipping none. Offset
  0 keeps both forms, because both already ship.
- **Verifies are added greedily, most selective first.** Greedy is exact here
  and not an approximation: each verify multiplies the entry rate by its own
  mass independently of the others, so the best `n` offsets are the `n` with the
  lowest mass and no exchange improves a set of that size.
- **Offset 0 is always in the set** — as the scan, or as a mandatory verify.
  §5.4 is why.

### 4.5 The materiality bar

An offset-k form is adopted only when the model predicts it at least **2×**
cheaper than the offset-0 filter that ships today.

It is not a safety margin — the change is answer-identical either way. It is
what keeps an artifact from MOVING for a predicted gain nobody can measure: a
moved artifact is a re-pinned identity gate, a changed objdump and a changed
byte count, and buying those for a predicted 1.5× that is inside the model's own
error bars (§4.3) is a bad trade. The three patterns this row exists for predict
19×, 31× and 3,600×.

### 4.6 The caps

`PCREC_OFSK_MAX_SET` is **4** — the scan plus at most three verifies. On every
corpus pattern the third and fourth verify are already below the model's noise,
and each one is emitted text and a branch on the candidate path.
`PCREC_PREFIX_K_MAX` is **24** (§3.3 condition 4). Neither is a `limits.h`
budget: exceeding them declines an optimization, it never refuses a pattern, so
there is nothing for `docs/spec/limits.md` to promise.

### 4.7 What the rule selects — MEASURED, before any timing

On the bench's own patterns, `--features all --no-captures`:

| pattern | offset-0 mass | selected k-set (`*` = the scan) | predicted rate | ratio |
|---|---|---|---|---|
| `uuid` | 807,006 ppm | `k=0`, **`k=8*`** (`-`), `k=13` (`-`) | 20 ppm | 40,350× |
| `iso-ts` | 74,760 ppm | `k=0` (digits), **`k=4*`** (`-`) | 372 ppm | 201× |
| `stack-frame` | 807,006 ppm | `k=0`, **`k=1*`** (`t`), `k=2` (` `) | 6,037 ppm | 134× |
| `bignum` | 807,006 ppm | **`k=0*`** (bitmap), `k=1` (digits) | 60,331 ppm | 13× |
| `ipv4` | 74,760 ppm | — declined | — | — |
| `hex32-id` | 807,006 ppm | — declined | — | — |
| `http-5xx` | 3,323 ppm | — declined | — | — |
| `ipv6` | 284,434 ppm | — declined | — | — |
| `kv-quoted` | 807,006 ppm | — declined | — | — |
| `floor` (`:`) | 6,646 ppm | — declined | — | — |
| **email `orig`** | 763,093 ppm | — **declined** | — | — |
| **email `factored`** | 763,093 ppm | — **declined** | — | — |

The two email patterns are the **derivation-domain control** and they come out
right for the structural reason §3.4 gives, not by a threshold accident: their
`+`-smeared prefix means no offset past 0 is narrow at any value of any
constant in the model.

**`iso-ts` selects `{digit}@0 ∧ {-}@4`, not the JIT's `{-}@4 ∧ {-}@7`.** The
plan row's "the selectivity is the CONJUNCTION" holds — it is a pair either way
— but the model prefers the cheaper partner: `-`@4 alone leaves 4,984 ppm, and
one predictable digit probe cuts that to 372, which is already 30× below the
loop's cost. Adding `-`@7 as a third member costs more (one more branch on every
candidate) than the 350 ppm of loop entries it removes. The model's arithmetic
for both options is in `prefix_k.c`'s `model_cost`.

**`bignum` is a new beneficiary the row did not predict**, and it is the
mechanism generalising rather than a special case: `\b[0-9]{10,19}\b` has the
useless 63-byte offset-0 set of every `\b`-leading pattern, and one digit probe
at offset 1 cuts its loop-entry rate 13×.

---

## 5. The emitted form

### 5.1 It is an `[ENG-FORM]` selection, and the k = 0 forms do not move

`docs/design/emitter_form.md` §3's **axis B** (the prefilter, forward only)
gains two candidates at the head of its five-entry preference list:

| # | object | applies when | deny |
|---|---|---|---|
| 1 | `offset-set-bounded` | forward && `ofsk.nsel > 0` && `views` | `PCREC_NO_OFFSET_SKIP` |
| 2 | `offset-set` | forward && `ofsk.nsel > 0` | `PCREC_NO_OFFSET_SKIP` |
| 3 | `memchr-bounded` | forward && `kind == MEMCHR` && `views` | — |
| 4 | `memchr` | forward && `kind == MEMCHR` | — |
| 5 | `byte-class-bounded` | forward && `kind == BYTE_CLASS` && `views` | — |
| 6 | `byte-class` | forward && `kind == BYTE_CLASS` | — |
| 7 | `none` | always | — |

Three consequences, and they are the reason this is the shape:

- **`<PREFIX>_DFA_PREFILTER` keeps being `obj->c.name`.** Two new values, no
  `stamp()` method, no second derivation.
- **`-fno-offset-skip` is a `deny` field on two candidates**, which is D82's
  "the deny flag = a filter on the candidate list". Under it the list is exactly
  today's and the artifact matches the pre-row one to the line, apart from the
  single `_DFA_PREFILTER_OFFSETS` stamp every `abi` 9 artifact carries — which
  is what makes the flag a valid control rather than a fourth variant.
- **The k = 0 skip BECOMES the |set| = 1, k = 0 case** in the sense the plan row
  asks for: `ofsk.nsel > 0` is false for every pattern where the k-set is
  `{0}` alone, so `memchr`/`byte-class` are literally what that case selects,
  and the mechanism is one preference list rather than two mechanisms.

The `-bounded` split is inherited unchanged and for D11's reason: under `views`
the skip may not pass `n-1` and loses its `return 0` early-out, which is a
different emitted body, not a label.

### 5.2 The accessor block

Layer 2, one `static inline` per machine per form, emitted at file scope beside
the state-token block (`emit_token`'s neighbour), so the VM hybrid's inlined
`static <prefix>_prefilter` gets it by construction:

```c
/* Offset-k candidate-start skip. Every match of this pattern carries
 *   '-' at offset 8   and   '-' at offset 13   and   [0-9A-Za-z_] at offset 0
 * from its own start, so a position failing any of them cannot begin one.
 * Returns the first position >= pos that satisfies all three, or n. */
static inline size_t rx_forward_ofsskip(const unsigned char *subject,
                                        size_t n, size_t pos)
{
    while (pos + 13 < n) {
        const void *q = memchr(subject + pos + 8, 45, n - pos - 8);
        if (!q) return n;
        size_t cand = (size_t)((const unsigned char *)q - subject) - 8;
        if (cand + 13 >= n) return n;
        if (rx_can_begin_match[subject[cand]] && subject[cand + 13] == 45)
            return cand;
        pos = cand + 1;
    }
    return n;
}
```

- `pos + maxk < n` is the loop's guard and it does three jobs at once: it is the
  "no room for a match" early-out (§3.3 condition 1 proved the match is at least
  `maxk+1` bytes long); it makes `pos + kstar < n` so `memchr` gets a non-NULL
  pointer and a non-zero length, which is [K27]'s hazard closed by construction;
  and it bounds the loop.
- `cand = hit − k*` is the **mapping back to the forward scan start**. It cannot
  underflow: the search began at `pos + k*`, so `hit ≥ pos + k*`.
- `pos = cand + 1` is the **resume from the failed candidate** — the next
  `memchr` starts at `hit + 1`, so no candidate is examined twice and none is
  skipped.
- The verify chain is emitted in ASCENDING OFFSET order so a reader of the
  artifact sees the pattern's own order, and each member is a byte comparison
  when its set is a singleton and a `<prefix>_can_begin_match`-style bitmap
  probe otherwise. Offset 0 reuses the **existing** `can_begin_match` table
  rather than emitting a second copy of it.

### 5.3 The loop integration

The entry condition is `pf_open`'s, unchanged — still parked in the start state
with nothing found:

```c
if (forward_state == S0 && last_accept_position == (size_t)-1) {
    size_t cand = rx_forward_ofsskip(subject, subject_length, scan_position);
    if (cand >= subject_length) return 0;              /* unbounded form */
    scan_position = cand;
    <reseed>
}
```

and the `-bounded` form replaces the early-out with the clamp the other bounded
forms use:

```c
    if (cand < subject_length) { scan_position = cand; <reseed> }
    else if (scan_position + 1 < subject_length) scan_position = subject_length - 1;
```

The skip sits where `pf->emit` already sits in `emit_scan_loop`'s skeleton —
after the `scalar-plain` accept probe, before the stay-skips, the view selector
and the step — so the evaluation ORDER D11 fixed is untouched.

### 5.4 The reseed, and why offset 0 is mandatory

Today's skip jumps over bytes that leave the machine **in** the start state, so
the state after the jump is trivially still the start state. **This skip jumps
over bytes that leave it**, and two things follow.

**(a) The machine must be re-seeded on landing.** For a machine with
`dfa_needs_seed` — every `\b` pattern, which is three of the four beneficiaries
— the start state carries the class of the byte to the left, and the bytes we
jumped over are how that class was being carried (§2.1). So the landing state is
`s1u[upc(s[cand-1])]`, which is exactly what the search's own initializer
computes at `search_from`; the emitted reseed is the same expression through the
same `<M>_seed_state` table:

```c
    forward_state = scan_position ? rx_forward_seed_state[rx_forward_byte_class[subject[scan_position - 1]]]
                                  : S0;
```

For a machine without a seed there is one start state and no context to carry,
so nothing is emitted and the landing state is `S0` — which it already is.

**(b) Offset 0 must be verified.** After the landing the loop falls through to
the step. If the landing byte did not escape the start state the machine would
still be parked there next iteration and the skip would run again — terminating,
because the step advances the position, but re-searching from every parked
position for a candidate it has already rejected. Verifying offset 0 makes the
landing byte one the step provably leaves the start state on, which is exactly
the invariant today's offset-0 filter has.

### 5.5 The reverse machine is unaffected — the argument, not the assertion

The forward scan finds where a match ENDS; the reverse machine then walks back
from `last_accept_position` to find where the leftmost one BEGINS, bounded by
`search_from` — **not** by the skip's landing position. So it is entitled to
report a start earlier than anything the forward skip landed on, and the claim
"the reverse machine is unaffected" has to be earned.

It is. The reverse machine's answer is the leftmost `y` with `s[y..last]` a
match. `y ≥ search_from` by its own bound. `y ≥ p`, the position the skip
started from, because the forward scan was in the start state at `p` with
`last == -1`, which is precisely "no thread from before `p` is alive".
`y ∉ [p, cand)` because §3.2 proves every position there fails a test every
match start satisfies. So `y ≥ cand`, which is where the forward scan resumed.

The same argument covers the **threads discarded by the reseed**. A thread from
`y ∈ [p, cand)` might still be alive at `cand` in a full scan, so the true DFA
state there is a superset of the reseeded one. It does not matter: any accept of
that thread would BE a match starting at `y`, which §3.2 excludes, so it can
never accept, and a thread that can never accept contributes nothing to any
later answer. It cannot affect D3's priority pruning either — pruning is
triggered BY an accept, and this thread has none.

### 5.6 Empty matches, views, and the two positions at the end

The mechanism inherits its whole zero-width argument from `unanch_start`, and
that is why the k-set is derived **only** when `kind != DFA_PF_NONE`:
`!start_acc` (which ORs in the seeded start states under `fseed`) is what says
the machine cannot accept while parked, so no position the skip passes can be an
empty match. A k-set selected independently of that verdict would be a second,
weaker version of an argument the function already makes — the fork D63's header
forbids.

An EOL/END view accept applies only at `n-1` and `n`, which the `-bounded`
form's clamp never passes.

### 5.7 Find-all and restart: O(n) per subject, not per restart

The skip is inside the search function and the search function is called once
per restart, so a naive reading is that a find-all loop re-scans from each match
end and the memchr work is O(matches × n). It is not, and for the same reason
today's memchr form is not: each call's `memchr` starts at `search_from + k*`
and the whole scan is monotone in `search_from`, so the union of all calls'
memchr ranges over one find-all sweep is `[0, n)` traversed once, plus at most
`k*` bytes of re-read per restart. The k-set adds nothing to that: `maxk` is
bounded by `PCREC_PREFIX_K_MAX`, so the re-read is at most 24 bytes per match.
The verify chain runs per CANDIDATE, and candidates are a subset of positions,
so it is bounded by the same sweep.

### 5.8 What is NOT built

- **SIMD.** The scan is one `memchr`, which is already glibc's AVX2 routine. A
  vectorised scan of the PAIR — checking both offsets in one register pass — is
  `[OPT-SIMD]`'s territory and is measured only if the scalar form leaves a gap
  (D77). §7 is the measurement that would say so.
- **ENG_ATTEMPT.** `attempt_cand`'s derivation is a different question (which
  PREDECESSOR bytes leave an attempt alive) and its skip advances BETWEEN
  attempts. The same k-set would apply — offsets measured from the attempt
  position — but no ENG_ATTEMPT pattern in the corpus or the bench shows the
  shape, so it is named and not built (D77). **The measurement that would
  trigger it:** an anchored-family bench row whose attempt loop dominates.
- **A bitmap walk at k > 0** — §4.4.
- **The D83 findings-file prior** — §4.1.

---

## 6. Identity

### 6.1 The argument

The skip refuses only starts the scan would refuse (§3.2), it lands the machine
in the state the scan would have been in (§5.4a), it discards only threads that
can never accept (§5.5), and it never passes a position at which the machine
could accept (§5.6). So every artifact's answer — span, capture slots, failure
surface — is unchanged on every subject.

### 6.2 The gate

`-fno-offset-skip` removes the two candidates, and the denied build's output
**differs from the pre-row compiler's by exactly one line** — the
`_DFA_PREFILTER_OFFSETS` stamp every `abi` 9 artifact carries — for every
pattern. That
makes the axis a member of `make test-axes`'s family with no special handling:
`tests/axes/run_axes.sh` derives its registry from `lib/pcrec.h`'s `1u << N`
constants and `cli/main.c`'s flag loop, so bit 16 joins by construction, and the
sweep compares the whole `.rxt` corpus case by case, by ANSWER, against the
default build.

`docs/spec/tuning.md` §2's "(bit 16)" heading is what that script cross-checks
the derivation against, which is why §2.14 exists and why §2's count moves from
thirteen to fourteen.

---

## 7. Measurement

### 7.1 The plan

1. **Bench, `loglines` search band + the 1 MB throughput sweep**: before/after
   on the three exercising rows and the three controls, ≥ 5 trials, the
   per-trial method of `opt3_dfa_scan_measurement.md` §2.
2. **Bench, `email` orig + factored**: must be UNTOUCHED — same artifact bytes,
   same time. This is the derivation-domain control.
3. **objdump of the hot loop** for an artifact where the skip is NOT selected:
   instruction-for-instruction identical to before (D82 bound 1).
4. **Artifact size and gcc time** deltas, on a selected and a declined artifact.
5. **`make test` and `make test-axes`**, asynchronously.

### 7.2 Measured — filled in at the end of the lane

*(see §7.3 and the lane's final report)*

### 7.3 Measured — the model's own corrections

Two claims in the draft of this note were refuted by measurement and are
recorded here rather than quietly fixed:

- **"The model is insensitive to `C_ENTER` over 8–40 cycles."** False; §4.3
  carries the sweep and the narrowed claim.
- **"A verify costs a probe."** False for a coin-flip verify; §4.2's
  `C_MISPRED` term exists because without it the model moves `hex32-id`, a
  control pcrec is already ahead on.

---

## 8. The five things every axis gets ([CHK-2]'s convention)

| # | thing | this row's |
|---|---|---|
| 1 | stamp | `<PREFIX>_DFA_PREFILTER` values `"offset-set"` / `"offset-set-bounded"`, plus the sibling `<PREFIX>_DFA_PREFILTER_OFFSETS` naming the chosen k-set (`"0,8*,13"`; `"none"` when no offset skip) |
| 2 | deny flag | `-fno-offset-skip` / `PCREC_NO_OFFSET_SKIP` (bit 16), `docs/spec/tuning.md` §2.14 in §2.13's deny-only shape |
| 3 | identity gate | `make test-axes` bit 16, by construction (§6.2) |
| 4 | structural check | `tests/codegen/run_offset_skip.sh` — reads the ARTIFACT (the emitted `memchr` offset, the verify chain, the reseed, the prior's sum), never the stamp |
| 5 | sabotage row | `tests/mech/` — the verify chain deleted; the resume set to `cand + 1 + k*` instead of `cand + 1`; the reseed dropped |

The sibling stamp carries a per-pattern VALUE, which is why it is a second
stamp rather than a widening of `DFA_PREFILTER`: `[ENG-FORM]`'s rule is that
`DFA_PREFILTER` is the chosen object's `name`, a static string, and a stamp
whose value is computed from the machine is a different kind of fact.

## 9. The abi bump — FOUR sites, one change (D76)

`rx_info.abi` moves **8 → 9**: the emitted text gains a file-scope accessor
block, a changed prefilter body, a reseed and a new stamp line.

| # | site |
|---|---|
| 1 | `src/gen/emit_dfa.c` — `.abi = 9` |
| 2 | `tests/codegen/run_codegen_tests.sh` — `ABI_EXPECT=9` and its `[DD-14.FB]` §10.4 message |
| 3 | `docs/spec/match_api.md` §6 — the "`rx_info.abi` is `9`" sentences |
| 4 | `tests/codegen/run_recursion_identity.sh` — comparison (B)'s `FILEPIN`, re-pinned to this change's last `src` commit |

## 10. Does one walk serve [DD-11]/D66's leading fixed lookbehind? — ANSWERED

**Yes, and the enabling change is not in this walk.**

D66 item (2) names "candidate-start derivation from a leading fixed lookbehind
(memchr its anchor byte; `\A` → position 0)" as the same optimizer this row
builds. Structurally it is the same walk read from the other side: a leading
`(?<=X)` of fixed width `w` constrains bytes at offsets `−w … −1` from the
candidate start, exactly as the prefix constrains offsets `0 … k`. Everything
downstream is already indifferent to the sign — `PrefixK.k` is an `int`, the
cost model reads only `ppm`, the greedy is over masses, and the emitted chain
would gain a `cand >= -mink` guard where it has `cand + maxk < n`.

**What blocks it is upstream and is not this row's to move.** `src/ir/nfa.c`
lowers `A_LOOK` to an epsilon on the DFA path, so a lookbehind's bytes are not
in the machine the walk reads at all — measured: `(?<=foo)bar` publishes
`{b}{a}{r}` at offsets 0–2 and nothing at −3…−1, and that is SOUND (an
assertion passed unconditionally, §3.1) rather than wrong. Making those bytes
visible means giving the NFA a representation of a fixed-width lookbehind,
which is [DD-11]'s core-reduction work and [M6.6]'s dependency, exactly as D66
sequences it.

**So: no code for it here, and none needed later beyond a second seeder.** When
the representation exists, the change is one function that seeds the walk from
the lookbehind's own reversed body and publishes negative `k`. This note's §3
is written with `anch_start` as *the* seed so that the second seeder is an
addition and not a rewrite.
