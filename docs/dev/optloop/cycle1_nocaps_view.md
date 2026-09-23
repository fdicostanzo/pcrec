# [OPTLOOP.1-NOCAPSVIEW] — the nocaps-vs-nocaps re-ranking of cycle 1

Lane `nocapsview`, 2026-09-23, branch `lane/nocapsview` from `603bc035`.
Docs only: nothing under `src/`, `cli/`, `lib/` or `tests/`; nothing
written in `/Users/fdicostanzo/pcrec-bench` (read-only reference). **REVISED
after two follow-up messages** (both dated 2026-09-23, after this memo's
first draft landed): the manager forwarding pcrec-bench's own authoritative,
run-derived classification table (I-99 ack `e8c5a12`; I-100 rulings
`5435ac6`/`e8d6109`) with the instruction to use it as Step 1's authority
in place of this lane's own `configs.toml` read; and Frank adding a
standing cross-class anomaly query (I-101, `7f440dd`) as a new §6. **The
authoritative table moves `rust-default` from the caps class into the
nocaps class** (I-100 ruling 2) — this changes every number in §0/§2/§3/§4
from the first draft, since `rust` is now a NOCAPS scored competitor
alongside `pcre2-dfa`, not merely a §6 curiosity.

**The ask.** Frank, 2026-09-23 (D119 addendum, "THE POPULATION IS TWO
CLASS-PURE LEDGERS", `docs/dev/decisions.md`): *"I meant that we should
compare capturing vs capturing and non-capturing vs non-capturing engine
runs."* `cycle1_caps_view.md` rendered the caps-vs-caps half (84/123).
This memo renders the OTHER half, plus (§6) Frank's sanity check that no
capturing competitor is beating pcrec's own non-capturing artifact.

**Sources.** `cycle1_rows.tsv` (the 125-row ranked-cell population and its
class weights, reused unchanged). pcrec-bench's OWN classification table
(`docs/dev/inbox_from_pcrec.md`, commits `e8c5a12`/`5435ac6`/`e8d6109` —
Step 1 cites it verbatim). Two bench reports: the BEFORE report
(`reports/2026-09-20-...-fullroster-25b1984f.*`, the only one that ever
measured `libpcre2_10.46_dfa-nocaps-simdna`, and the only one carrying
`pcre2-interp`/`pcre2-jit`/`re2`/`re2-longest`/`tre`) and the AFTER report
(`reports/2026-09-23-...-after-8d716693.*`, both pcrec pins together in
one window, but narrowed to `oniguruma`/`rust`/`vectorscan` as its only
non-pcrec testees).

**Reproduction.** `docs/dev/optloop/nocapsview/build_nocaps_view.py` reads
the sources above with no recompilation and no re-measurement, and writes
`nocaps_rows.json`/`nocaps_rows.tsv`.

---

## 0. Headline

| view | scorable cells | win/tie | loss | no-data |
|---|---|---|---|---|
| BEFORE (pin `25b1984f`) | 113 | **87 (77.0%)** | 26 | 12 |
| AFTER (pin `8d716693`) | 113 | **92 (81.4%)** | 21 | 12 |

Total weighted losing score fell **7.6062 → 4.0091** (−47%). These numbers
are materially different from — and worse than — the first draft's
110-cell/100-win table: adding `rust-default` as a scored NOCAPS
competitor (I-100's ruling, not this lane's own choice) both scores 3
previously no-data cells — `router-prefix-order`/srch, `file-ext-order`/
srch, `keyword-prefix-order`/srch, all three where `pcre2-dfa` reads
`wrong` (per `cycle1_caps_view.md` §2's own foot-table) but `rust`
measures cleanly; the other 12 no-data cells (backreference/recursion
patterns) stay no-data because `rust`'s own `regex` crate has no
backreference support either, so `pcre2-dfa`'s `unsup` population is
untouched — and, far more consequentially, `rust` is the
FASTEST engine on the whole roster on many of these rows (it dominated
`cycle1_analysis.md`'s original mixed ranking too) — so 17 of BEFORE's
26 losses and 18 of AFTER's 21 losses are against `rust`, not `pcre2-dfa`.

**Batch 1's own effect is still a real, large win**: six BEFORE losses
flip to win/tie (§2), and the losing score still fell 47%. But two cells
flip the OTHER way — `winpath-near-miss`/thr and `email-nested-plus`/thr
— and against a `rust`-inclusive competitor set their loss ratios are
even starker (256× and 215×, up from 87×/9× when `pcre2-dfa` alone was
the competitor) because `rust` answers these two patterns even faster
than `pcre2-dfa` does. Read §3.

**§6's headline, up front**: 40 of 125 cells (BEFORE) and 29 of 125
(AFTER) show SOME capturing (YES-class) competitor beating pcrec's own
non-capturing artifact — but 30/40 and 25/29 of those are `pcre2-jit`,
which `cycle1_analysis.md` §0 rule 1 already excludes from "algorithmic"
for exactly this reason (JIT codegen is not an algorithmic advantage).
The genuinely surprising population — a non-JIT capturing competitor
beating our non-capturing artifact — is **10 cells BEFORE, 4 cells AFTER**,
all real and clearing the within-window noise floor. Read §6.

---

## 1. Step 1 — the roster classified by capture mode (pcrec-bench's own table, authoritative)

**This table supersedes the first draft's `configs.toml` read**, per the
manager's instruction: pcrec-bench's own driver-code-derived
classification (`docs/dev/inbox_from_pcrec.md` in pcrec-bench, ack `e8c5a12`
2026-09-23, frozen by `e8d6109` after Frank's ruling `5435ac6`/I-100) is
the authority; this lane's earlier `configs.toml` read is kept as a
CROSS-CHECK column, with the one disagreement stated in full rather than
silently resolved.

| config | class (frozen) | pcrec-bench's own evidence | this lane's earlier `configs.toml` read | agreement? |
|---|---|---|---|---|
| `pcrec-auto` / `pcrec-vm` / `pcrec-vm-in` (`-caps` ids) | **YES** | `--no-captures` absent | `captures = "on"` | agree |
| `pcrec-nocaps` (`auto-nocaps`) | **NO** | `--no-captures` | `captures = "off"` | agree |
| `pcre2-interp` / `pcre2-jit` | **YES** | `pcre2_match`, ovector assigned every call | `captures = "on"` | agree |
| `pcre2-dfa` | **NO** | `pcre2_dfa_match` cannot assign per-group captures (driver.c's own header) | `captures = "off"` | agree |
| `re2-default` / `re2-longest` | **YES** | `driver.cc`: `Match(..., submatch.data(), nsub)` with `nsub>0` on EVERY call | `captures = "on"` | agree |
| `oniguruma-default` | **YES** | `onig_search` called with a region | `captures = "on"` | agree |
| `tre-default` | **YES** | `tre_regnexecb` called with `pmatch`; `emit_caps` | `captures = "on"` | agree |
| `vectorscan-block-nosom` | **NO** (SIMD-excluded from any scored set regardless) | boolean grain by charter | `captures = "off"` | agree |
| `rust-default` | **NO, RULED — the one disagreement** | I-100 ruling 2: the timed loop is `find_at`-driven (`src/main.rs:255`) with exactly **ONE `captures_at` call on the FIRST match per driver call** (`:263`), not one per match — Frank's principle applied by the manager: this counts as NO for the class-pure views, with the single `captures_at` **declared as a fixed per-call cost** | `captures = "on"` (declared field; this lane's earlier read also confirmed the driver DOES call `.captures_at()`/`.captures()`, just did not know it fires once per call rather than once per match) | **DISAGREE with this lane's earlier table** — not a factual error (both agree the driver calls a captures API), a RULING about which class a single-call-per-driver-invocation captures cost belongs to |

**The captures_at caveat, stated precisely** (I-100 point 2): because
`rust`'s `captures_at` fires once per `find_at`-loop CALL rather than once
per MATCH, its cost is effectively AMORTIZED across every match the
`large-subject-throughput` (find-all) regime's one call finds — negligible
on `thr` cells with hundreds or thousands of matches — but UNAMORTIZED on
`short-subject-search` cells, where the call finds at most one match and
the `captures_at` cost is the whole extra cost, paid in full on every one
of the regime's 75 short subjects. This memo does not have an isolated
measurement of that per-call cost (no builds, no timing per this lane's
brief); the qualitative direction is stated here as pcrec-bench's own
finding, not re-derived.

**`testee_id`s are NOT renamed** (I-100 point 3): `rust`'s store id stays
`rust_1.13.1_default-caps-simdna` — the literal string still says `caps`
— while the classification TABLE above, not the id, is this memo's
authority throughout. Every `rust` reference in §2–§6 below uses that id
verbatim; read its class from this table, never from the id text.

**Growth named but not built**: `re2-nosub` (a pure NO re2 arm — today's
`re2-default`/`re2-longest` are both YES, so the NO class has no re2
representative until this lands) and `rust-find`/`rust-captures` (the pure
split that retires `rust-default` from these views). Until then, **the NO
class's algorithmic-scalar competitor set is exactly two configs**:
`pcre2-dfa` and `rust-default` (with its stated caveat) — thinner than the
YES class's five (`pcre2-interp`, `pcre2-jit`, `re2-default`,
`re2-longest`, `oniguruma`, `tre` — six counting `pcre2-jit`, five
algorithmic). Every conclusion below is bounded by that thinness: a NOCAPS
row `pcrec` loses says "loses to the best of two engines, one of them
carrying a declared impurity", not "loses to the class".

---

## 2. Step 2 — the nocaps-vs-nocaps ranking, BEFORE and AFTER

Same rule as `cycle1_analysis.md` §0 (reused unchanged): weight by pattern
family, `score = weight × log2(ratio)` clamped to 0 at ratio ≤ 1, ratio =
pcrec `auto-nocaps` median ÷ **best of {`pcre2-dfa`, `rust-default`}**
median (the `best_of` selection `cycle1_caps_view.md`'s own CAPS table
already uses for its multi-engine competitor set, applied here to the
NOCAPS class's two-engine set). 12 of the 125 ranked cells carry no
`pcre2-dfa` AND no `rust` number at all (both `unsup`/refused on
backreference/recursion patterns neither engine implements) — down from
the first draft's 15 no-data cells, since `rust` measures cleanly on 3
patterns where only `pcre2-dfa` was `unsup`.

### BEFORE (pin `25b1984f`)

Losing cells, ranked by score (26 rows; `pcre2-dfa` is the winning
competitor on 9 of them — six `cap-recursion` rows plus
`wild-secrets-username-password-pair`/thr, `wild-logparse-winpath-grok`/thr
and `currency-lookbehind-fixed`/thr, where `pcre2-dfa` simply reads faster
than `rust` on that specific row, not because of any construct `rust`
cannot attempt; `rust` is the winning competitor on the other 17, mostly
ordinary DFA-route rows where `rust`'s literal-prefilter start beats
`pcre2-dfa`'s NFA-simulation scan):

| pattern | regime | score | ratio | competitor |
|---|---|---|---|---|
| `bracket-array-define` | thr | 1.7422 | 15691.17× | `pcre2-dfa` |
| `tag-depth3-bound` | thr | 0.9569 | 201.61× | `pcre2-dfa` |
| `wild-semdiv-dollar-trailing-newline-pcre2` | thr | 0.8708 | 1402.11× | `rust` |
| `wild-secrets-username-password-pair` | thr | 0.7233 | 55.21× | `pcre2-dfa` |
| `wild-secrets-aws-access-key-id` | thr | 0.6196 | 31.06× | `rust` |
| `wild-logparse-winpath-grok` | thr | 0.3608 | 148.63× | `pcre2-dfa` |
| `wild-codegrammar-json-constant` | thr | 0.2787 | 14.97× | `rust` |
| `nested-comment-rec` | thr | 0.2364 | 3.71× | `pcre2-dfa` |
| `wild-waf-crs-942360-concat-sqli` | thr | 0.2318 | 4.99× | `rust` |
| `router-prefix-order` | thr | 0.2258 | 6.54× | `rust` |
| `file-ext-order` | thr | 0.2212 | 6.30× | `rust` |
| `wild-semdiv-altorder-foo-foobar-rustregex` | thr | 0.1933 | 5.00× | `rust` |
| `wild-waf-crs-942270-union-select` | thr | 0.1831 | 3.56× | `rust` |
| `wild-secrets-github-pat` | thr | 0.1763 | 2.66× | `rust` |
| `wild-waf-crs-942160-sleep-benchmark` | thr | 0.1711 | 3.28× | `rust` |
| `keyword-prefix-order` | thr | 0.0831 | 2.00× | `rust` |
| `wild-waf-crs-942140-dbnames` | thr | 0.0745 | 1.68× | `rust` |
| `balanced-parens-rec` | srch | 0.0628 | 1.42× | `pcre2-dfa` |
| `wild-waf-crs-942360-concat-sqli` | srch | 0.0624 | 1.54× | `rust` |
| `nested-comment-rec` | srch | 0.0530 | 1.34× | `pcre2-dfa` |
| `balanced-parens-rec` | thr | 0.0275 | 1.17× | `pcre2-dfa` |
| `wild-secrets-aws-access-key-id` | srch | 0.0255 | 1.15× | `rust` |
| `uuid-near-miss` | thr | 0.0119 | 1.10× | `rust` |
| `wild-validator-ipv4-owasp` | thr | 0.0051 | 1.04× | `rust` |
| `currency-lookbehind-fixed` | thr | 0.0051 | 1.04× | `pcre2-dfa` |
| `ipv4-near-miss` | thr | 0.0039 | 1.03× | `rust` |

Total losing score **7.6062**.

### AFTER (pin `8d716693`)

Losing cells (21 rows; `rust` is RE-MEASURED in the after report for this
pin — only `pcre2-dfa` is reused from BEFORE, see §0's methodology note
below):

| pattern | regime | score | ratio | competitor |
|---|---|---|---|---|
| `email-nested-plus` | thr | 0.6454 | 215.00× | `rust` |
| `wild-secrets-aws-access-key-id` | thr | 0.6100 | 29.45× | `rust` |
| `winpath-near-miss` | thr | 0.4000 | 256.13× | `rust` |
| `wild-codegrammar-json-constant` | thr | 0.2787 | 14.97× | `rust` |
| `nested-comment-rec` | thr | 0.2674 | 4.41× | `pcre2-dfa` |
| `wild-waf-crs-942360-concat-sqli` | thr | 0.2305 | 4.94× | `rust` |
| `router-prefix-order` | thr | 0.2267 | 6.59× | `rust` |
| `file-ext-order` | thr | 0.2211 | 6.30× | `rust` |
| `wild-semdiv-altorder-foo-foobar-rustregex` | thr | 0.1942 | 5.03× | `rust` |
| `wild-waf-crs-942270-union-select` | thr | 0.1835 | 3.57× | `rust` |
| `wild-waf-crs-942160-sleep-benchmark` | thr | 0.1807 | 3.50× | `rust` |
| `wild-secrets-github-pat` | thr | 0.1770 | 2.67× | `rust` |
| `keyword-prefix-order` | thr | 0.0940 | 2.19× | `rust` |
| `wild-waf-crs-942140-dbnames` | thr | 0.0738 | 1.67× | `rust` |
| `wild-waf-crs-942360-concat-sqli` | srch | 0.0619 | 1.54× | `rust` |
| `uuid-near-miss` | thr | 0.0492 | 1.51× | `rust` |
| `ipv4-near-miss` | thr | 0.0393 | 1.39× | `rust` |
| `wild-validator-ipv4-owasp` | thr | 0.0380 | 1.37× | `rust` |
| `balanced-parens-rec` | thr | 0.0194 | 1.11× | `pcre2-dfa` |
| `wild-codegrammar-json-array-begin` | thr | 0.0134 | 1.14× | `rust` |
| `currency-lookbehind-fixed` | thr | 0.0047 | 1.03× | `pcre2-dfa` |

Total losing score **4.0091**.

**What moved.** Six BEFORE losses flip to win/tie: `bracket-array-define`/
thr (`[OPT-ANCHOR-VM]`), `tag-depth3-bound`/thr, `wild-secrets-username-
password-pair`/thr, `wild-logparse-winpath-grok`/thr (all three
`[OPT-REQBYTE]`), `wild-semdiv-dollar-trailing-newline-pcre2`/thr
(`[OPT-ENDWIN]`), `nested-comment-rec`/srch and `balanced-parens-rec`/srch
(`[OPT-ANCHOR-VM]`), and `wild-secrets-aws-access-key-id`/srch — eight
flips in total (one more than the first draft found, since
`wild-semdiv-dollar-trailing-newline-pcre2`/thr was a LOSS against `rust`
before batch 1 even though it was already a win against `pcre2-dfa` alone).
Three flip the other way: `wild-codegrammar-json-array-begin`/thr (a small,
band-clearing move, ratio 0.86× → 1.14×) and the two floor-entry
catastrophes, §3.

**Batch 1's mechanism reach, cross-referenced against
`docs/dev/optloop/b1ledger/artifact_identity.tsv`'s per-config census**
(which of the three mechanisms changed the `nocaps` pcrec ARTIFACT for
each pattern — unaffected by which competitor set the artifact is scored
against): `[OPT-ANCHOR-VM]` reaches `bracket-array-define`,
`email-local-nodup`, `logparse-atomic`, `pwd-strength-chain`;
`[OPT-ENDWIN]` reaches `wild-validator-us-zip-owasp`,
`wild-validator-ipv4-owasp`, `uuid-near-miss`,
`wild-semdiv-dollar-trailing-newline-pcre2`; `[OPT-REQBYTE]` reaches the
majority of "changed:reqbyte*" rows. This is unchanged from the first
draft — the mechanism's REACH into the nocaps artifact is a property of
the artifact, not of which competitor it is scored against; only the
SCORE each reached cell earns changes with the wider competitor set.

---

## 3. The two new losses — a regression this view finds that the caps view could not

`winpath-near-miss`/thr and `email-nested-plus`/thr are `[OPT-REQBYTE]`'s
carve-out cost landing on a pattern whose required byte is **absent from
the throughput subjects** (`artifact_identity.tsv`'s
`absent_in_thr_subjects` column reads `True` for both) — the exact
mechanism `cycle1_ledger_reading.md` §5 names and prices at 23,120.8 ns
predicted.

| pattern | before ns | after ns | measured Δns | vs. `pcre2-dfa` (265/2,522 ns) | vs. `rust` (also ~fast) |
|---|---|---|---|---|---|
| `winpath-near-miss` | 20.38 | 23,119.74 | +23,099.4 | 87.2× loss | **256.1× loss** |
| `email-nested-plus` | 31.98 | 23,138.80 | +23,106.8 | 9.17× loss | **215.0× loss** |

**`rust` makes the loss look even worse than `pcre2-dfa` alone did**,
because `rust`'s own literal-prefilter start is even faster than
`pcre2-dfa`'s NFA-simulation scan on these two rows — the same mechanism
the first draft found, restated on the wider, authoritative competitor
set. These two cells are ALSO §6's newest non-JIT cross-class anomalies
(§6.4 makes the connection explicit): the floor-entry cost is not merely
a nocaps-vs-nocaps loss, it is bad enough that even a YES-class
(capturing) interpreted competitor — `oniguruma` on `winpath-near-miss`,
`re2-default` on `email-nested-plus` — now beats pcrec's non-capturing
artifact too.

**Cause bucket (D81 convention):** `[OPT-REQBYTE]` engine-selection cost,
sub-bucket "required byte present in the pattern but absent from the
measured subject" — a known, named, already-priced mechanism; a genuinely
new LOSS this class-pure, `rust`-inclusive view surfaces more sharply
than the first draft did.

**Smaller carve-out cluster** (`uuid-near-miss`, `wild-validator-ipv4-owasp`,
`ipv4-near-miss` — `[OPT-ENDWIN]` carve-out, now scored against `rust`
too, 1.04–1.51× here rather than the first draft's larger dfa-only
percentages, since `rust` was ALREADY beating pcrec on these rows before
batch 1 and stays close after; `nested-comment-rec`/thr — `[OPT-REQBYTE]`
carve-out, +18.80% on the paired same-pin Δ%, G3-unattributed per
`cycle1_ledger_reading.md` §9(C)) is unchanged in mechanism attribution
from the first draft, only in its scored ratio against the wider
competitor set.

---

## 4. Step 3 — the honest comparison

| view | scorable cells | pcrec win/tie | win/tie rate | one-sentence reason it differs |
|---|---|---|---|---|
| Mixed best-variant (`cycle1_analysis.md` §1) | 125 | 91 | 72.8% | picks whichever of pcrec's four bench configs is fastest per row |
| Caps-vs-caps (`cycle1_caps_view.md` §1/§5) | 123 | 84 | 68.3% | `auto-caps` against every YES-class competitor (`rust` included there too — that memo predates this ruling and has not been revised; see the note below) |
| Nocaps-vs-nocaps, BEFORE (this memo §2, revised) | 113 | 87 | 77.0% | `auto-nocaps` against the best of `pcre2-dfa`/`rust-default`, per the frozen I-100 classification |
| Nocaps-vs-nocaps, AFTER (this memo §2, revised) | 113 | 92 | 81.4% | same competitor set, batch 1's mechanisms landed |

**Open item for the manager**: `cycle1_caps_view.md` §1's CAPS table still
scores `auto-caps` against a competitor set that includes `rust` (its own
§0 text: `"rust", "tre"` in `CAPS_ENGINES`) — under I-100's ruling `rust`
is NOT a YES-class config for the class-pure views. That memo was written
and merged BEFORE the classification froze and has not been revised here
(out of this lane's scope — its own lane, `capsview`, owns that file); its
84/123 stays the number of record until a `capsview`-lane follow-up
re-scores the CAPS table with `rust` removed from the CAPS competitor set
(and, per this memo's §1, added instead to a WIDENED nocaps competitor set
— which would also change `cycle1_caps_view.md` §2's own NOCAPS table,
since that one used `pcre2-dfa` alone). **Flagged as §5 question 4.**

---

## 5. Questions for the bench / Frank

1. **Should the AFTER report re-measure `pcre2-dfa` at the new pin?** This
   memo's AFTER ranking still reuses `pcre2-dfa`'s BEFORE-window number
   (§2's methodology) — `rust` is now re-measured in the AFTER report, so
   this reuse is narrower than the first draft's (which also had to reuse
   `pcre2-interp`/`jit`/`re2`×2/`tre` for §6; see question 2), but it is
   still the one open assumption in the main §0–§4 ranking.
2. **§6's AFTER anomaly check reuses FIVE testees from the BEFORE window**
   (`pcre2-interp`, `pcre2-jit`, `re2-default`, `re2-longest`, `tre` — only
   `oniguruma` and `rust` are re-measured in the after report). This is a
   much larger reuse than §0's single `pcre2-dfa` row and weakens §6's
   AFTER numbers proportionally more — worth a standing policy for which
   testees a capability AFTER comparison carries, not just `pcre2-dfa`.
3. **`nested-comment-rec`/thr's +18.80% carve-out regression has no
   confirmed mechanism** as of `cycle1_ledger_reading.md` §9(C)/(D) — this
   memo reproduces it again, independently, on the `rust`-inclusive
   nocaps-vs-nocaps view.
4. **`cycle1_caps_view.md`'s CAPS table needs a re-score once `rust`
   leaves the CAPS competitor set** (§4's open item) — not this lane's
   file to touch, flagged for the manager to route.
5. **§6's non-JIT anomaly population (10 BEFORE, 4 AFTER — §6.3) is a
   standing, real finding**: `wild-waf-crs-942140-dbnames`/thr and
   `wild-waf-crs-942360-concat-sqli`/thr lose to `re2` (non-JIT,
   capturing) on BOTH pins, unrelated to batch 1 — worth a cycle-2 cause
   read.
6. **`re2-nosub` and `rust-find`/`rust-captures` are named as roster
   growth but not scheduled** — until they land, the NO class has exactly
   two algorithmic competitors, one of them ruled rather than pure. Is
   there a target cycle for that growth?

---

## 6. Cross-class anomaly query (Frank's nuance, I-101)

*"It's possible a capturing competitive engine is faster than our
non-capturing. That would be surprising. We should validate that this
isn't true."* pcrec-bench's own inbox (I-101, `7f440dd`) frames this as a
STANDING query `[B82]`'s reporter will own going forward; this section is
the one-time pcrec-side rendering off the same two reports §0–§4 use, per
Frank's own text ("A pcrec lane renders it once from O-45's report
meanwhile; the standing query is yours").

### 6.1 Method

For every one of the 125 ranked cells, compare pcrec `auto-nocaps`'s
median against the BEST (lowest-median) of every YES-class config
(`pcre2-interp`, `pcre2-jit`, `re2-default`, `re2-longest`, `oniguruma`,
`tre` — §1's frozen table; `rust` excluded here since it is ruled NO, see
the informational footnote in §6.5). A cell is an ANOMALY if that best
YES-class median is LOWER than `auto-nocaps`'s. Two clearance checks, since
this is a WITHIN-report comparison (not the cross-window Δ% §2/§3 use):
whether the competitor's own `max_ns` sits below `auto-nocaps`'s own
`min_ns` over the report's 3–5 trials (a non-overlapping-range check, the
closest signal these reduced reports carry to a formal IQR) — every
anomaly cell below clears this. `pcre2-jit` is flagged separately: it is
excluded from "algorithmic" everywhere else in this cycle
(`cycle1_analysis.md` §0 rule 1) for exactly the reason this section
would otherwise misreport as surprising — a JIT beating an AOT-compiled
DFA on start-up-optimization-bound rows is expected, not an anomaly by
D119's own definition of "algorithmic advantage". **AFTER methodology
caveat**: only `oniguruma` (of the six YES-class configs) is re-measured
in the after report; `pcre2-interp`/`pcre2-jit`/`re2-default`/
`re2-longest`/`tre` are reused from the BEFORE window (§5 question 2).

### 6.2 Counts

| | total anomaly cells | of which `pcre2-jit` (excluded elsewhere as non-algorithmic) | non-JIT — genuinely surprising by Frank's framing |
|---|---|---|---|
| BEFORE | 40 | 30 | **10** |
| AFTER | 29 | 25 | **4** |

All 10 BEFORE and all 4 AFTER non-JIT anomalies clear the within-window
range check (competitor's max below `auto-nocaps`'s min).

### 6.3 The non-JIT anomaly table — the real finding

BEFORE:

| pattern | regime | `auto-nocaps` ns | competitor | competitor ns | ratio |
|---|---|---|---|---|---|
| `bracket-array-define` | thr | 4,880,173.5 | `oniguruma` | 93.6 | 52131.71× |
| `wild-semdiv-dollar-trailing-newline-pcre2` | thr | 109,772.6 | `oniguruma` | 151.3 | 725.62× |
| `dup-param-detect` | thr | 13,395,576.0 | `pcre2-interp` | 23,240.8 | 576.38× |
| `tag-depth3-bound` | thr | 4,687,857.3 | `pcre2-interp` | 23,238.0 | 201.73× |
| `tag-pair-match` | thr | 4,634,280.3 | `pcre2-interp` | 23,229.8 | 199.50× |
| `wild-logparse-winpath-grok` | thr | 3,468,809.9 | `pcre2-interp` | 23,249.3 | 149.20× |
| `wild-secrets-username-password-pair` | thr | 1,287,801.1 | `pcre2-interp` | 23,276.3 | 55.33× |
| `wild-waf-crs-942360-concat-sqli` | thr | 12,239,876.9 | `re2-longest` | 2,246,279.2 | 5.45× |
| `bracket-array-define` | srch | 6,882.1 | `oniguruma` | 2,915.5 | 2.36× |
| `wild-waf-crs-942140-dbnames` | thr | 4,099,500.9 | `re2-default` | 2,241,475.2 | 1.83× |

AFTER:

| pattern | regime | `auto-nocaps` ns | competitor | competitor ns | ratio |
|---|---|---|---|---|---|
| `winpath-near-miss` | thr | 23,119.7 | `oniguruma` (RE-MEASURED) | 93.3 | 247.81× |
| `email-nested-plus` | thr | 23,138.8 | `re2-default` (reused BEFORE) | 341.4 | 67.78× |
| `wild-waf-crs-942360-concat-sqli` | thr | 12,137,118.1 | `re2-longest` (reused BEFORE) | 2,246,279.2 | 5.40× |
| `wild-waf-crs-942140-dbnames` | thr | 4,082,823.2 | `re2-default` (reused BEFORE) | 2,241,475.2 | 1.82× |

### 6.4 The connection to §3

`winpath-near-miss`/thr and `email-nested-plus`/thr are §3's own
floor-entry regressions AND new AFTER non-JIT anomalies — the SAME
mechanism produces both symptoms. Before batch 1 neither pattern was
close to any competitor (`auto-nocaps` answered in 20–32 ns); after batch
1 the pre-check's fixed ~23,100 ns floor cost is now slow enough that even
an INTERPRETED, capturing competitor beats it. `wild-waf-crs-942140-
dbnames` and `wild-waf-crs-942360-concat-sqli` are the two persistent,
batch-1-UNRELATED non-JIT anomalies (present on both pins, unchanged
mechanism) — `re2`'s own automaton engine outpacing pcrec's DFA on these
two WAF-pattern rows regardless of captures, worth a cycle-2 cause read
(§5 question 5).

### 6.5 Rust — informational only, footnoted per Frank's literal text

Frank's own request text named `"rust-default under its caveat"` among the
YES-class configs to check; I-100/I-101's frozen table rules `rust-default`
NO for the class-pure views (§1), so it is **excluded from §6.2–6.4's
scored anomaly table** to stay consistent with §1's authority. Purely as
the literal-request footnote: `rust` already appears as a NOCAPS
competitor in §2 (it wins outright on many rows), so by construction there
is no separate "rust anomaly" population to report beyond what §2 already
tables — every row where `rust` beats `auto-nocaps` is already one of §2's
own scored losses (17 BEFORE, 18 AFTER), not a hidden, unscored anomaly.

### 6.6 The mirror — one line

Cells where pcrec's CAPTURING default (`auto-caps`) beats every
non-capturing competitor (`pcre2-dfa`, `rust`; `vectorscan` excluded):
**80 of 111 scorable cells BEFORE, 87 of 111 AFTER** — expected, and not
itself a finding (a captures-on artifact routinely does more work and
still often wins on rows the DFA-route engines lose for unrelated
reasons); recorded here only because Frank's own framing asked for the
mirror explicitly.

---

**Deliverables list.** This memo; `docs/dev/optloop/nocapsview/`
(`build_nocaps_view.py`, `nocaps_rows.json`, `nocaps_rows.tsv`, own
`CLAUDE.md`); a `docs/dev/optloop/CLAUDE.md` entry; `docs/dev/lanes/
nocapsview_report.md`; a `docs/dev/lanes/CLAUDE.md` line.
