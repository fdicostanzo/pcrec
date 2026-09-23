# Cycle 2 — reading O-51 against I-103/I-103a's EXPECTs and the [OPT-REQPOS] form rule

2026-09-23, lane `o51read`. Reads pcrec-bench's O-51
(`runs/2026-09-23-o51-i103/`, full raw report `b83runform_report.md`, 495
lines — read in full) against the two asks it answers and against
`cycle2_batch2_reading.md` §4.1/§6 and `plan.md`'s `[OPT-REQPOS]` row
three-arm form rule (Frank 2026-09-23 ~12:5x). No clock read here; every
number below is O-51's own or arithmetic on it.

## 1. The four answers against I-103/I-103a's EXPECT

1. **Router: `(b)−(c) ≈ 0` — EXACT match to I-103's EXPECT.** All four
   configs read within IQR (margins 1.3%-73%; report §8). I-103 stated
   this as the discriminator: "if (b) is within IQR of (c) ... the run
   form is the whole cost." It is.
2. **Keyword: EXPECT was `(a)-(c) ~ +560-590k`, `(b)-(c)` unstated
   directionally.** Measured `(b)-(c)` is positive both configs
   (39,506.9 / 45,236.2 ns) — order of magnitude smaller than router's
   run-form cost but not indistinguishable from zero either session. The
   IQR-crossing bar itself flips between two independently-run sessions
   on `auto-nocaps` (report §8: IQR 1,583.1 ns first session, 65,093.6 ns
   this one) while the delta stays 39.5k-48.3k ns both times — the
   **direction is robust, the bar's verdict at this sample size is not**.
3. **Inline vs memchr: EXPECT was "memchr-run should still beat the
   inline scalar loop" at 2.8-3.2%.** Confirmed on all six measured
   cells, both patterns, margins +8.5% to +52.5%, every one outside IQR
   (report §9) — not router-specific, since keyword's arm (d) is now
   built (offset-corrected, see §4 below).
4. **Crossover constant: EXPECT (stated, not claimed provable) was that
   two points 0.36pp apart might not condition the two-parameter
   solve.** Confirmed — both mechanisms' fitted byte terms go negative
   (memchr −0.689, inline −1.414 ns/B, report §10), shown and stopped
   rather than forced, exactly as the ruling instructed.

## 2. Against the three-arm form rule and §4.1/§6

Router and keyword sit at 2.8433%/3.2067% scan-byte frequency —
comfortably inside the rule's **moderate** tier (well under the ~8%
crossover), where the rule says: use the run check only where its
restarts cost less than what they dismiss, else fall back to the byte
form; the inline (**common**-tier) mechanism is not supposed to fire
here at all. O-51 confirms both halves directly: the inline arm loses
badly on both patterns (finding 3 above) — the common-tier mechanism is
correctly inapplicable at this frequency, independent of any
crossover-value dispute — and router's `(b)−(c)≈0` is the measured
instance of "restarts cost more than what they dismiss, so the byte form
is free relative to no check at all," which is exactly `cycle2_batch2_
reading.md` §4.1's finding restated as a decision (its 124× call
amplification, 39,098 vs 315 calls, is why the run form costs +322,063
ns while the byte form costs nothing extra) and exactly what §6's
candidate rule (admit the run only where its scan-byte's own `memchr`
count is strictly lower than the prefilter's) would correctly decline on
`router-prefix-order` (both scan byte 47, identical counts — the rule's
own worked example). Keyword weakens one assumption behind that rule:
the byte form is not exactly free there either (finding 2), so "falls
back to the byte form" is directionally right but "the byte form costs
what the prefilter alone costs" is not exact on every pattern — a
refinement for whoever builds the rule, not a refutation of it.

## 3. Established / not established

**ESTABLISHED**: (i) memchr-run beats the scalar inline loop at both
2.8% and 3.2% scan-byte frequency, on every configuration measured (VM
and DFA route, captures on/off) — the common-tier inline mechanism does
not apply below ~8% and O-51 is direct evidence, not an extrapolation.
(ii) Router's pre-check cost is entirely the run form, not the byte
lookup — the dominance-rule decision the run-form-widening candidate in
`cycle2_batch2_reading.md` §6 needs for its own worked example is
settled by measurement, not argument.

**NOT ESTABLISHED**: (i) Keyword's IQR-crossing verdict — the decision
RULE needs a null-control band (I-104's own ask) before "does (b) clear
(c)" can be answered without depending on which 5-trial session ran.
(ii) The crossover constant itself — two points 0.36pp apart cannot
solve a two-parameter system; a well-separated pair is needed (§5).

**Process finding** (candidate for `learnings.md` §3, not applied here):
*a hand-twin instrument template written from ONE witness's own offset
generalizes wrong to a second witness whose scan byte sits at a
different position within its run — a per-witness placement check, not
substitution, is what an offset-bearing template needs.*

## 4. The cycle-3 ask, designed not built

**Population.** From `b2ledger/stampdiff.json`'s fix-side `RX_REQ_RUN`
(14 of 64 capability patterns carry a run), counted the run's own scan
byte against the regenerated `bench/capability/throughput/{t-64k,
t-256k,t-1m}.bin` (sha256 `d2e4f134…`/`3cf7b248…`/`ccbdf7eb…`, matching
`b83runform_report.md` §1 exactly — the same subjects O-51 measured on):

| pattern | byte | hits | freq |
|---|---:|---:|---:|
| wild-semdiv-dollar-trailing-newline-pcre2 | 98 `b` | 6,569 | **0.4773%** |
| wild-secrets-github-pat | 95 `_` | 7,861 | 0.5712% |
| logparse-atomic(-removed) | 58 `:` | 11,812 | 0.8583% |
| file-ext-order | 46 `.` | 19,436 | 1.4122% |
| wild-semdiv-altorder-foo-foobar-rustregex | 102 `f` | 24,889 | 1.8085% |
| router-prefix-order | 47 `/` | 39,095 | 2.8407% |
| wild-secrets-slack-webhook-url | 47 `/` | 39,095 | 2.8407% |
| keyword-prefix-order | 110 `n` | 44,132 | **3.2067%** |

(5 more read 0 hits — their scan byte never occurs in these subjects at
all; excluded as uninformative for a rate measurement.) **No candidate in
the bench's own capability set clears 6%** — the widest real spread is
`wild-semdiv-dollar-trailing-newline-pcre2` (0.4773%, clears <0.5%) vs
`keyword-prefix-order` (3.2067%, already measured by O-51), a 6.7×
spread that still falls short of the requested split.

**Proposed synthetic witness** (designed, not built — D77). Checked the
argmin mechanism against all 14 real cases above using the shipped
`pcrec_byte_freq_ppm` table (`src/opt/prefix_k.c`): the picked scan byte
is, on 14/14, the argmin over the run's OWN bytes' ppm values (e.g.
router's `/user` picks `/` at 4,154 ppm over `u`/`s`/`e`/`r`'s higher
values; keyword's `in` picks `n` at 44,776 over `i`'s 46,105) — a fully
verified predictor, not a guess. Under that table, `' '`=124,561 ppm and
`'e'`=84,235 ppm are the two highest entries in the whole table, so a
run built ONLY from `e`/space bytes forces `'e'` as the argmin pick
regardless of tie-break details. `'e'` already occurs in the EXISTING
throughput subjects at **8.5212%** (117,274 hits/1,376,256 B) — no new
subject text is required, only a new PATTERN whose necessary run
consists solely of `e`/space bytes, e.g. a nested-comment-rec-shaped
delimiter pair using `"e "`/`" e"` in place of `"*/"`. This is a
proposal for the bench to build and verify by compile, not a claim about
what pcrec would emit.

**I-105's ask** (rides after `[B84]`'s I-102 window, per BOILERPLATE):
the same I-103a block — default / `-fno-req-run` / `-fno-req-byte` /
inline hand-twin (offset-corrected per pattern, O-51's own lesson) — on
`wild-semdiv-dollar-trailing-newline-pcre2` (0.4773%) paired against
EITHER `keyword-prefix-order` (3.2067%, already built, reuses O-51's own
arms with no new build) as the best REAL spread, OR the proposed
synthetic `e`/space-run witness above once the bench builds and verifies
it compiles with the expected stamps — SLOT ASKED NOT ASSUMED.
