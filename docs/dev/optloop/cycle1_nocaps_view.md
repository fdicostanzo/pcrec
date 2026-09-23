# [OPTLOOP.1-NOCAPSVIEW] — the nocaps-vs-nocaps re-ranking of cycle 1

Lane `nocapsview`, 2026-09-23, branch `lane/nocapsview` from `603bc035`.
Docs only: nothing under `src/`, `cli/`, `lib/` or `tests/`; nothing
written in `/Users/fdicostanzo/pcrec-bench` (read-only reference).

**The ask.** Frank, 2026-09-23 (D119 addendum, "THE POPULATION IS TWO
CLASS-PURE LEDGERS", `docs/dev/decisions.md`): *"I meant that we should
compare capturing vs capturing and non-capturing vs non-capturing engine
runs. If an engine is run non-capturing on a pattern, then we can't
compare that to a capturing engine run — they are almost completely
different things with different objectives."* `cycle1_caps_view.md`
rendered the caps-vs-caps half (84/123). This memo renders the OTHER
half: pcrec's `auto-nocaps` testee against every competitor config that
runs non-capturing — over the same population, BEFORE batch 1 (pin
`25b1984f`) and AFTER it (pin `8d716693`).

**Sources.** `cycle1_rows.tsv` (the 125-row ranked-cell population and its
class weights, reused unchanged, not recomputed — same discipline
`cycle1_caps_view.md` used). `pcrec-bench`'s testee declarations
(`testees/*/configs.toml`, cross-checked against `tools/selfcheck.py`'s
own assertions) for Step 1's classification. Two bench reports:
`reports/2026-09-20-capability-0.1-budu-ryzen1600-fullroster-25b1984f.*`
(the BEFORE report `cycle1_caps_view.md`'s own NOCAPS table used — the
only report in the roster's history that measured `libpcre2_10.46_dfa-
nocaps-simdna` at all) and
`reports/2026-09-23-capability-0.1-budu-ryzen1600-after-8d716693.*` (the
AFTER report, `pcrec-bench` outbox O-45/O-47, both pcrec pins measured
together in one window). **The AFTER report's own roster does not include
`pcre2-dfa`** (narrowed to oniguruma/rust/vectorscan spot-checks plus
pcrec's four configs at both pins) — see §0's methodology note on how
this memo handles that gap.

**Reproduction.** `docs/dev/optloop/nocapsview/build_nocaps_view.py`
reads the three sources above with no recompilation and no re-measurement,
and writes `nocaps_rows.json`/`nocaps_rows.tsv` — the single source every
number below is read from.

---

## 0. Headline

| view | scorable cells | win/tie | loss | no-data |
|---|---|---|---|---|
| BEFORE (pin `25b1984f`) | 110 | **100 (90.9%)** | 10 | 15 |
| AFTER (pin `8d716693`) | 110 | **104 (94.5%)** | 6 | 15 |

Total weighted losing score fell **4.7066 → 1.4094** (−70%). Batch 1's
three mechanisms reach the nocaps testee too (not only the caps testee the
ledger's own headline table describes) and six of BEFORE's ten losing
cells flip to win/tie, four by 98–100×. **But two cells flip the other
way, from a clean win to a catastrophic loss** — `winpath-near-miss`/thr
(+113,334%) and `email-nested-plus`/thr (+72,253%) — the exact
required-byte-absent floor-entry mechanism `cycle1_ledger_reading.md` §5
already named, independently reproduced here to within a few nanoseconds
of its own predicted value, on the nocaps testee specifically. Read §3.

**Methodology note on the missing `pcre2-dfa` row.** The AFTER report was
built to compare pcrec's own two pins, plus three fixed spot-check
competitors; it does not re-measure `pcre2-dfa` at either pin. Since
`pcre2-dfa` is a third-party binary (libpcre2 10.46, direct-linked,
identical build both times) wholly unaffected by any pcrec commit, this
memo uses the BEFORE report's `pcre2-dfa` numbers as the competitor
reference for BOTH the BEFORE and the AFTER ranking — an assumption, not a
measurement, and the same cross-window shape `cycle1_ledger_reading.md`
§1 already found introduces up to ±8.46%/−5.74% of pure between-window
noise on a program-IDENTICAL artifact. `pcre2-dfa`'s own binary and
pattern compile are even MORE stable than a pcrec artifact across two
days (no compiler, no pin, nothing pcrec's batch 1 touches), so the
assumption is far safer for it than it would be for a pcrec cell — but it
is still unverified and is asked of the bench in §5.

---

## 1. Step 1 — the roster classified by capture mode

Read directly from `testees/*/configs.toml`'s `captures` field
(`record_schema.md 6.4`'s own derivation source: `engine_name,
engine_version, engine_mode, captures, simd` — literally the field that
becomes the `-caps-`/`-nocaps-` component of the derived `testee_id`),
never guessed from a testee name. Two cross-checks used where the config
alone was not conclusive: `pcrec-bench/tools/selfcheck.py:9858` directly
asserts `"pcre2-dfa declares captures=off"`; `testees/rust/src/main.rs:255-
284` was read to confirm the driver actually CALLS `captures_at`/
`captures` at the match position (not only declares the field), and
`testees/re2/adapter.py:183` likewise declares the field explicitly.

| config | class | evidence |
|---|---|---|
| `pcrec-auto` (`auto-caps`) | **caps** | `testees/pcrec/configs.toml`: `captures = "on"` |
| `pcrec-nocaps` (`auto-nocaps`) | **nocaps** | `testees/pcrec/configs.toml`: `captures = "off"` |
| `pcrec-vm` (`vm-caps`) | **caps** | `captures = "on"` |
| `pcrec-vm-in` (`vm-in-caps`) | **caps** | `captures = "on"` |
| `pcre2-interp` | **caps** | `testees/pcre2/configs.toml`: `captures = "on"` |
| `pcre2-jit` | **caps** | `captures = "on"` (excluded from either scored set anyway — cycle1_analysis.md §0 rule 1: JIT codegen is never itself the algorithmic target) |
| `pcre2-dfa` | **nocaps** | `testees/pcre2/configs.toml`: `captures = "off"`; confirmed by `tools/selfcheck.py:9858` (`"pcre2-dfa declares captures=off"`) — `pcre2_dfa_match` reports no per-group captures by construction (NFA-simulation breadth-first scan) |
| `oniguruma-default` | **caps** | `testees/onig/configs.toml`: `captures = "on"` |
| `re2-default` / `re2-longest` | **caps** | `testees/re2/adapter.py:183`: `"captures": "on"` |
| `tre-default` | **caps** | `testees/tre/configs.toml`: `captures = "on"` |
| `rust-default` | **caps** | `testees/rust/adapter.py`: `"captures": "on"`; driver-confirmed — `testees/rust/src/main.rs:255-284` calls `.find_at()`/`.find()` to locate the match THEN `.captures_at()`/`.captures()` at that position to populate submatches |
| `vectorscan-block-nosom` | **nocaps** | `testees/vectorscan/adapter.py:163`: `"captures": "off"  # Hyperscan has NO capturing groups at all"` — excluded from the nocaps-vs-nocaps scored set anyway per `cycle1_analysis.md` §0 rule 2 (SIMD-first, boolean-grain, no scalar mechanism to mine) |

**No UNKNOWN configs.** Every roster entry the bench has ever measured on
`capability@0.1` resolves cleanly from its own `configs.toml` declaration,
cross-checked in the two cases (`rust`, `pcre2-dfa`) where a second,
independent source was available. The nocaps-vs-nocaps scored set is
therefore exactly what `cycle1_caps_view.md` §2 already used: `pcrec-
nocaps` against `pcre2-dfa` alone — the only algorithmic nocaps competitor
on the whole roster.

---

## 2. Step 2 — the nocaps-vs-nocaps ranking, BEFORE and AFTER

Same rule as `cycle1_analysis.md` §0 (reused unchanged): weight by pattern
family (`1 / rows of that family in the 125-row population`), `score =
weight × log2(ratio)` clamped to 0 at ratio ≤ 1, ratio = pcrec `auto-
nocaps` median ÷ `pcre2-dfa` median, compared within a row only. 15 of the
125 ranked cells carry no `pcre2-dfa` number at all — `cycle1_caps_view.md`
§2's own foot-table (10 `unsup` on backreference/recursion patterns `pcre2
-dfa` cannot run, 4 `wrong`, 1 `gave-up`) — leaving 110 scorable.

### BEFORE (pin `25b1984f`)

Reproduces `cycle1_caps_view.md` §2's own totals exactly (100/110,
10 losses, 15 no-data) — a direct cross-check that this lane's independent
re-parse of the same report agrees with the earlier lane's.

Losing cells, ranked by score:

| pattern | regime | score | ratio | `auto-nocaps` ns | `pcre2-dfa` ns |
|---|---|---|---|---|---|
| `bracket-array-define` | thr | 1.7422 | 15691.17× | 4,880,173.5 | 311.0 |
| `tag-depth3-bound` | thr | 0.9569 | 201.61× | 4,687,857.3 | 23,252.3 |
| `wild-secrets-username-password-pair` | thr | 0.7233 | 55.21× | 1,287,801.1 | 23,326.7 |
| `wild-secrets-aws-access-key-id` | thr | 0.5387 | 19.83× | 4,201,042.8 | 211,881.9 |
| `wild-logparse-winpath-grok` | thr | 0.3608 | 148.63× | 3,468,809.9 | 23,338.3 |
| `nested-comment-rec` | thr | 0.2364 | 3.71× | 7,809,454.0 | 2,105,602.6 |
| `balanced-parens-rec` | srch | 0.0628 | 1.42× | 6,494.0 | 4,585.5 |
| `nested-comment-rec` | srch | 0.0530 | 1.34× | 9,306.4 | 6,937.2 |
| `balanced-parens-rec` | thr | 0.0275 | 1.17× | 5,481,441.1 | 4,705,332.8 |
| `currency-lookbehind-fixed` | thr | 0.0051 | 1.04× | 11,205,442.3 | 10,819,260.4 |

Total losing score **4.7066**.

### AFTER (pin `8d716693`)

| pattern | regime | score | ratio | `auto-nocaps` ns | `pcre2-dfa` ns (reused, see §0) |
|---|---|---|---|---|---|
| `wild-secrets-aws-access-key-id` | thr | 0.5292 | 18.82× | 3,986,630.0 | 211,881.9 |
| `winpath-near-miss` | thr | 0.3223 | 87.22× | 23,119.7 | 265.1 |
| `nested-comment-rec` | thr | 0.2674 | 4.41× | 9,275,952.3 | 2,105,602.6 |
| `email-nested-plus` | thr | 0.2664 | 9.17× | 23,138.8 | 2,522.1 |
| `balanced-parens-rec` | thr | 0.0194 | 1.11× | 5,239,095.5 | 4,705,332.8 |
| `currency-lookbehind-fixed` | thr | 0.0047 | 1.03× | 11,175,118.7 | 10,819,260.4 |

Total losing score **1.4094**.

**What moved.** Six BEFORE losses flip to win/tie: `bracket-array-define`/
thr (−99.9985%, `[OPT-ANCHOR-VM]`), `tag-depth3-bound`/thr (−99.51%,
`[OPT-REQBYTE]`), `wild-secrets-username-password-pair`/thr (−98.19%,
`[OPT-REQBYTE]`), `wild-logparse-winpath-grok`/thr (−99.33%,
`[OPT-REQBYTE]`), `nested-comment-rec`/srch (−71.40%, `[OPT-ANCHOR-VM]`)
and `balanced-parens-rec`/srch (−84.99%, `[OPT-ANCHOR-VM]`) — every one of
these Δ%s is far outside the O-48 null band (−5.74%/+8.46%), a genuine
measured win, not noise. Two flip the other way (§3). The two BEFORE
losses that stayed losses (`wild-secrets-aws-access-key-id`/thr −5.09%,
`balanced-parens-rec`/thr −4.43%, `currency-lookbehind-fixed`/thr +0.03%)
all sit INSIDE the null band — flat, not a real move either direction, and
`nested-comment-rec`/thr's own persistent loss (+18.80%, outside the band)
is the batch's own unattributed carve-out regression (`cycle1_ledger_
reading.md` §4.1/§9(C): real, +18.8–25.0%, but G3's placement hypothesis
is refuted on the box that measures it and no mechanism is confirmed as
of this writing).

**Batch 1's target cells and carve-outs, as they land on the nocaps
testee.** Cross-referenced against `docs/dev/optloop/b1ledger/
artifact_identity.tsv`'s own per-config census (which of the three
mechanisms changed the `nocaps` artifact for each pattern, independently
of whether that pattern is scored above):

| mechanism | patterns reaching the `auto-nocaps` artifact | cells in THIS view's 125-row population | result here |
|---|---|---|---|
| `[OPT-ANCHOR-VM]` | `bracket-array-define`, `email-local-nodup`, `logparse-atomic`, `pwd-strength-chain` | `bracket-array-define` thr/srch (2 of its 13 named targets reach nocaps — `evil-alt-nested`/`trim-nested-star` do NOT: their `nocaps` artifact is `program-identical`, confirming `f2_rescue_split.md`'s finding that these two never route to VM under `--no-captures`) | both improve far outside the band (−99.9985%, and srch not separately named above but the SAME mechanism) |
| `[OPT-ENDWIN]` | `wild-validator-us-zip-owasp`, `wild-validator-ipv4-owasp`, `uuid-near-miss`, `wild-semdiv-dollar-trailing-newline-pcre2` | `wild-semdiv-dollar-trailing-newline-pcre2`/thr was already a scored WIN before batch 1 (ratio 0.042×) and improves further to −99.97% (0.0000134×) — a target that was never a loss here, unlike in the caps view where `auto-caps` starts from a genuine loss on this row; carve-outs `uuid-near-miss`, `wild-validator-ipv4-owasp` regress 18.75–38.54%, exactly reproducing the ledger's own 18.7–38.5% carve-out range, independently, on the nocaps testee alone |
| `[OPT-REQBYTE]` | the majority of "changed:reqbyte*" rows in the identity census | multiple named targets improve 98–99.98%; the carve-out set includes BOTH the floor-entry catastrophes (§3) and `nested-comment-rec`'s unattributed +18.80% | targets meet the bar; carve-out clause still fails, on this testee too |

The D119 bar (`|Δ| > max(IQR, null band)`; this lane has no per-cell
within-window IQR, so it applies the O-48 null band uniformly — the
CORRECTED noise model `cycle1_ledger_reading.md` §1 itself recommends for
any cross-window comparison, which every number in this memo is) is
**MET for the named targets on the nocaps testee** and **FAILS for the
carve-out clause**, the same verdict the ledger reached for the caps
testee — with one addition (§3) the ledger's own headline table does not
carry, because it was computed on `auto`/the mixed population, not on
`auto-nocaps` in isolation against `pcre2-dfa`.

---

## 3. The two new losses — a regression this view finds that the caps view could not

`winpath-near-miss`/thr and `email-nested-plus`/thr are `[OPT-REQBYTE]`'s
carve-out cost landing on a pattern whose required byte is **absent from
the throughput subjects** (`artifact_identity.tsv`'s
`absent_in_thr_subjects` column reads `True` for both) — the exact
mechanism `cycle1_ledger_reading.md` §5 names and prices at 23,120.8 ns
predicted. Measured here, independently, on the `auto-nocaps` testee
alone:

| pattern | before ns | after ns | measured Δns | §5's prediction |
|---|---|---|---|---|
| `winpath-near-miss` | 20.38 | 23,119.74 | +23,099.4 | +23,120.8 (§5: measured elsewhere +23,103.5) |
| `email-nested-plus` | 31.98 | 23,138.80 | +23,106.8 | +23,120.8 (§5: measured elsewhere +23,059.6) |

Both land within 25 ns of §5's own predicted value — as clean an
independent confirmation as this kind of arithmetic gets.

**Why this shows up here and not as prominently in the caps view.** On
`winpath-near-miss`, `pcre2-dfa` was already answering in 265 ns before
batch 1 — `pcrec`'s own pre-check now COSTS more than eleven times that
competitor's *entire* run, turning an 0.08× win into an 87× loss. The
caps-view competitor set (`pcre2-interp`, `onig`, `re2`, `re2-longest`,
`rust`, `tre`) has no engine anywhere near that fast on these two cells —
`winpath-near-miss` doesn't even appear as a named row in
`cycle1_caps_view.md`'s CAPS-table loss population, because `auto-caps`'s
own artifact for this pattern is a different (VM) machine that the
`[OPT-REQBYTE]` pre-check reaches differently. The floor-entry cost is
real and mechanism-general (§5 already knew it), but its CONSEQUENCE — a
clean win flipping to a two-order-of-magnitude loss — is a nocaps-vs-
nocaps-specific finding: `pcre2-dfa`'s near-instant reject on a
required-byte-absent subject is the one competitor fast enough for the
new floor cost to matter this much.

**Cause bucket (off the D81 stamps convention `cycle1_analysis.md` §0
uses):** `[OPT-REQBYTE]` engine-selection cost, sub-bucket "required byte
present in the pattern but absent from the measured subject" — already a
known, named, and priced mechanism; not a new defect, but a genuinely new
LOSS this class-pure view surfaces that the caps view's own competitor set
could not.

**Cause bucket, the smaller cluster (10–90% relative, single-digit-to-
low-triple-digit-ns absolute, within `[OPT-ENDWIN]`/`[OPT-REQBYTE]`'s
already-named carve-out populations):** `uuid-near-miss`,
`wild-validator-ipv4-owasp`, `ipv4-near-miss` (`[OPT-ENDWIN]` carve-out,
18.75–38.54% here, matching the ledger's 18.7–38.5% range exactly),
`nested-comment-rec`/thr (`[OPT-REQBYTE]` carve-out, +18.80%, matching the
ledger's 18.8–25.0% range, G3-unattributed). Four further cells
(`logparse-atomic`, `logparse-atomic-removed` both regimes,
`wild-codegrammar-json-array-begin`, `wild-datetime-moment-iso8601`,
`wild-validator-email-owasp`, `wild-validator-uuid-grok`) regress
10–60% beyond the null band on the nocaps testee and are **not named in
any of the ledger's §2/§4 tables** — new findings for this view, all
small in absolute ns (tens of ns to tens of thousands, one exception:
`wild-codegrammar-json-array-begin`/thr moves 263,616 → 349,567 ns,
+32.6%, real and unexplained). None are scored losses (they stay wins
against `pcre2-dfa`'s own absolute numbers) but they are real, band-
clearing regressions on the nocaps artifact this view is the first to
tabulate against a fixed external competitor.

---

## 4. Step 3 — the honest comparison

| view | scorable cells | pcrec win/tie | win/tie rate | one-sentence reason it differs |
|---|---|---|---|---|
| Mixed best-variant (`cycle1_analysis.md` §1) | 125 | 91 | 72.8% | picks whichever of pcrec's four bench configs is fastest per row, so a captures-off engine (`pcre2-dfa`) can be beaten by pcrec's OWN captures-off variant even on a row the shipped default loses |
| Caps-vs-caps (`cycle1_caps_view.md` §1/§5) | 123 | 84 | 68.3% | the shipped default (`auto-caps`) against capture-BEARING competitors only — the class D119's addendum requires for a captures-on artifact, and the harder comparison since every competitor here is doing MORE work per match |
| Nocaps-vs-nocaps, BEFORE (this memo §2) | 110 | 100 | 90.9% | `auto-nocaps` against the ONE algorithmic nocaps competitor (`pcre2-dfa`), which is itself often the fastest thing on the whole roster on these rows (no submatch bookkeeping, breadth-first NFA simulation) — the highest win rate of the three because `pcre2-dfa` is a comparably lean opponent, not because pcrec is doing less here |
| Nocaps-vs-nocaps, AFTER (this memo §2) | 110 | 104 | 94.5% | batch 1's three mechanisms land on the nocaps testee too (named targets improve 98–100%), moving the rate up four points despite two new floor-entry losses that did not exist BEFORE |

The **mixed 91/125 and the caps 84/123 are not directly comparable to the
nocaps 100/110 or 104/110 rate** — different denominators (a 125-cell
population minus the compile failures/no-`pcre2-dfa` rows each view's own
population excludes), and the D119 addendum's whole point is that they
answer different questions: whether pcrec's BEST configuration can do a
job at all (mixed), whether the SHIPPED captures-on default keeps pace
with other captures-on engines (caps), and whether the captures-off
generation axis keeps pace with the one other captures-off engine that
exists (nocaps). All three are true simultaneously and none supersedes
the others.

---

## 5. Questions for the bench / Frank

1. **Should the AFTER report re-measure `pcre2-dfa` at the new pin, or is
   reusing its BEFORE-window number the intended shape for a competitor
   this bench does not build?** This memo's AFTER ranking rests entirely
   on that reuse (§0's methodology note). `pcre2-dfa` is a fixed
   third-party binary unaffected by any pcrec commit, so the risk is
   small, but it is untested — nothing in this memo's data confirms
   `pcre2-dfa`'s own numbers are stable across the same two windows the
   16-cell null control (`cycle1_ledger_reading.md` §1) measured for
   pcrec's own program-identical artifacts. A cheap discriminator: the
   bench already has BOTH windows' `oniguruma`/`rust`/`vectorscan` numbers
   in the after report (they ARE re-measured there) — comparing those
   against their own BEFORE-report numbers would bound the between-window
   drift for a THIRD-PARTY, unchanging binary directly, without needing a
   fresh `pcre2-dfa` run at all.
2. **Should future capability reports carry `pcre2-dfa` on every AFTER
   comparison as standing policy**, given it is the ONLY algorithmic
   nocaps competitor on the whole roster and every future nocaps-vs-nocaps
   cycle depends on it? The D119 addendum names this memo and "every
   capability report hereafter" (inbox I-99) as the trigger; this is the
   first data point saying the gap is a real cost, not a hypothetical one.
3. **`nested-comment-rec`/thr's +18.80% carve-out regression on the nocaps
   testee has no confirmed mechanism as of `cycle1_ledger_reading.md`
   §9(C)/(D)** (G3 placement refuted on x86_64, the hand-twin instrument
   inconclusive). This memo reproduces the same regression, independently,
   on a different testee (`auto-nocaps` rather than `auto`/`auto-caps`) —
   one more data point that whatever is happening is not specific to the
   captures-on artifact.
4. **The four newly-surfaced small regressions** (`logparse-atomic`,
   `logparse-atomic-removed`, `wild-codegrammar-json-array-begin`,
   `wild-datetime-moment-iso8601`, `wild-validator-email-owasp`,
   `wild-validator-uuid-grok`) are not in any named batch-1 target or
   carve-out list. None flips a scored win to a loss, so none is urgent,
   but `wild-codegrammar-json-array-begin`/thr's absolute +85,950 ns move
   is large enough (32.6%, well outside the null band) that it may be
   worth a cause-bucket read in cycle 2's own analysis pass rather than
   left here as an aside.

---

**Deliverables list.** This memo; `docs/dev/optloop/nocapsview/`
(`build_nocaps_view.py`, `nocaps_rows.json`, `nocaps_rows.tsv`, own
`CLAUDE.md`); a `docs/dev/optloop/CLAUDE.md` entry; `docs/dev/lanes/
nocapsview_report.md`; a `docs/dev/lanes/CLAUDE.md` line.
