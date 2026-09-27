# EXECUTIVE SUMMARY — pcrec-bench's `bench/utf8@0.1`, first sample (2026-09-27)

For Frank. pcrec-bench's new UTF-8 encoding set (I-90's charter, "any
functionality which might be affected by encoding") ran its full 11-testee
roster on 2026-09-26. Four ledgers scored it end to end: the parent ledger
(P1-P11, R0-R1, R8), an addendum closing R2-R5/R7, a second addendum closing
R6, and a control read settling one open item. Numbers below cite those four
files plus pcrec's own `docs/dev/plan.md`.

**The pin, stated once because it matters throughout.** Every number here
measures pcrec at `ce658cb7` (abi 33), sampled 2026-09-26 05:06-07:52 UTC.
Two pcrec-side changes landed on `main` or on an active lane **after** that
sample and are **not** reflected in anything below:
`[OPT-REQRUN-ENC]` stage 2 (the run-scan-byte fix, abi 38, merged to `main`
at `43039d4e`) and K68 (`rx_info.flags`' unmasked deny bits, abi 39, built on
lane `k68fix`, not yet merged). Both are named in `docs/dev/plan.md`'s
`[OPT-REQRUN-ENC]` row as travelling back to the bench as inbox item I-112
once K68 lands — that re-measure is still owed, not done.

## 1. FINDINGS

**Correctness: pcrec is exact.** 0 wrong of 33,810 / 33,810 / 32,830 / 32,830
match rows across all four `pcrec-*-utf8` configs (`auto`, `auto-nocaps`,
`vm`, `vm-in`) — the only roster members besides `pcre2-utf-interp`/`-jit`
with zero wrong answers anywhere
(`2026-09-26-utf8-0.1-first-ce658cb7.md` §1, §2.1 summary). Every other
engine's wrong answer is a documented semantics difference, not a defect:
rust/re2/onig/vectorscan read a bare `\p{Greek}`/`\p{Cyrillic}`/`\p{Latin}`/
`\p{Han}` as `Script` where PCRE2 (and pcrec) read `Script_Extensions`
(U10); Oniguruma folds ß↔SS under `(?i)` where PCRE2 folds simply (U9);
RE2 places an empty-width `\B` mid-character (U8); `pcre2-utf-dfa`'s
longest-match convention disagrees with leftmost-first on one lazy
quantifier (documented, not a finding).

**Compile time: two patterns dominate everything.** Every non-property
compile is gcc-bound (median 0.16-0.19 s, 98.7-99.0% in gcc, p90 ≤ 0.38 s)
except `\p{L}+`/`\P{L}+` on the DFA route, which hit the emitted-size
retry ladder and take **70.74 s / 106.41 s** (plain/whole-subject) and
**41.32 s / 62.27 s** respectively — 91-93% of the whole `auto` config's
total compile-time budget over 69 patterns (§6.1-6.2). `^\p{L}{4}$` refuses
outright on every config (>1 MB C-source or >500 KB code). This is exactly
the population `docs/dev/plan.md`'s `[OPT-RETRY-REUSE]` row already cites as
its own "BENCH REPRODUCTION" evidence (filed, not scheduled) — no new row
needed; see §4.

**Search-short regime (91 subjects, ≤512 B): pcrec is essentially flat.**
The one pair (`@é`/`é@`) that later turns into a ×39.6 throughput gap
differs by only ×1.12-1.14 at search-short grain (P1.a, REFUTED against its
own ×1.5 bar) — the mechanism needs enough subject bytes to accumulate a
cost per scanned occurrence; a short subject never accumulates it. This is
the numeric backing for "pcrec dominates outside of large-subject search":
on the short-subject regime, none of the mechanisms below move the needle.

**Large-subject-throughput regime: this is where pcrec loses.** Method
(the bench's own large-subject comparison, restated here so the tally
below is reproducible): per pattern, pcrec's best of its four configs
(`auto`, `auto-nocaps`, `vm`, `vm-in`) against the best FULL-GRAIN
competitor (libpcre2 dfa/interp/jit, oniguruma, re2, rust —
`vectorscan-block-nosom` is EXCLUDED throughout this document: it is
boolean-grain, stops at first match, and is never a legitimate "pcrec
loses" comparator, per the parent ledger §0.3). Over the 75-pattern set:
**6 are n/a** (the UCP family pcrec does not compile, P5.a), leaving 69
ranked. Of those, **42 pcrec wins outright, 5 lose by ≤×2, and 22
(31.9% of the ranked population) lose by more than ×2 — every one of
them a `large-subject-throughput` cell, none in `short_subject_search`**
(cross-checked directly against the report's own matrix TSV; matches the
parent ledger §2.3's coarser "22 of 138 auto-rankable cells" statement,
which pools both regimes: 138 = 69 + 69, and `short_subject_search`
contributes 68 wins / 1 loss-≤×2 / 0 losses->×2 to that pool). See §3 for
the dedicated reading of the 22, split by what is and is not attributed
to a known mechanism.

**The `pcre2-jit` band (R2, Frank's own rule) is a near-census, not a small
list**: 431 of 1,340 comparable cells (32.2%) trip "worse than ×2 or better
than ×20" against JIT. Almost all of it is unsurprising by construction
(every non-JIT interpreter is slower than JIT; `vectorscan`'s boolean-grain
fast path and `rust`'s early-exit are "faster than ×20" on patterns that
never match). pcrec's own "slower" cells (24 of 134 on the forced-VM route,
3 of 138 on `auto`) are the same `\p{*}` property family the compile-cliff
finding already names (`2026-09-26-...-addendum-r2r7.md` §3).

**`alt-cyr-64` (a 64-branch Cyrillic alternation) is NOT an encoding
defect.** It trips both the script band (R4, ×420/×228 on libpcre2) and the
compile-time cliff (R5) on every testee that has one — but a dedicated
control read against `bench/altwide@0.2`'s own branch-count ladder
(`2026-09-26-utf8-0.1-alt-cyr-64-control-read.md`) shows it compiles at or
below `w-64`'s own cost once branch/byte count is held constant, on the
identical DFA/byte-class-prefilter mechanism `altwide` already measures.
It is a within-corpus outlier (measured against the utf8 set's other 74
mostly-single-construct patterns), not a Cyrillic-specific cost. No pcrec
action item.

## 2. SURPRISES

**A. U11 — libpcre2's own Cyrillic "floor" cost is its UTF-8 subject
validation, not a pcrec-relevant finding, and not JIT-immune.** The pure
byte-safe control pattern `~` (matches nothing) costs ~3.05-3.13× more
ns/byte on `t-64k-cyr` than on `t-64k-asc`, identically on
`libpcre2-dfa`/`-interp`/`-jit`. A standalone C probe isolates the cause:
`PCRE2_NO_UTF_CHECK` collapses the ratio to ~1.00 on all three routes —
this IS libpcre2's built-in `pcre2_match()`/`pcre2_dfa_match()` UTF-8
validation pass, priced by script rather than by call count. It reaches
even the `pcre2-jit` testee because the real driver calls `pcre2_match()`
(which dispatches to JIT internally), never `pcre2_jit_match()` directly —
confirmed by the probe's own `jit_via_match` vs `jit_direct` split
(`docs/dev/upstream_findings.md` U11). Filed UNDERSTOOD, not reported
upstream, not ours to fix.

**B. The lead-byte scan-byte defect (O-60's own headline finding) is
already found, dispositioned, and fixed on `main` — but after this
sample.** On every artifact in the set that stamps `RX_REQ_RUN`, the run
was scanned at its **leftmost** byte — the UTF-8 lead byte — which is the
densest byte of the subject's own script (0xC3 on Latin, 0xD0 on Cyrillic,
0xE6 on CJK) or an ordinary ASCII letter (`u` of `user@…`), rather than a
genuinely rare byte. `docs/dev/plan.md`'s `[OPT-REQRUN-ENC]` row (STATE:done,
closed 2026-09-26, same day as this sample) traces it to
`src/opt/reqbyte.c`'s `rn_scan_index` returning index 0 whenever the
encoding is non-byte, and fixes it to scan the run's **rightmost** byte
instead — matching the sibling single-byte path `rb_pick`'s own rightmost
rule (`docs/design/reqpos_2b.md` §2.3). abi 37→38, merged to `main`.

**C. R6 (engine-selection surprises) reads clean — nothing pcrec chose is
wrong.** A full stamp-level check (the two-lead-byte class `[α-ω]+`, every
compiling control-twin pair, the corpus-wide declined-prefilter census)
finds no engine-route inconsistency anywhere: the DFA route correctly picks
`byte-class` over `memchr` for a two-lead-byte class exactly as
`utf8_design.md` §6.3 predicts, and every one of the four patterns with a
declined prefilter is fully anchored or zero-width-everywhere, never a
missed lead-byte opportunity (`...-addendum-r6.md` §7). The forced-VM
route's blanket `prefilter=none` is that testee's own documented identity,
not a per-pattern decline.

## 3. LARGE-SUBJECT SEARCH — the 22 losses, split ATTRIBUTED / UNATTRIBUTED

**Only the literal scan-byte class has evidence tying it to a named
mechanism.** Of the 22 `large-subject-throughput` cells losing by more
than ×2 (§1, verified directly against the report's matrix TSV), the
bench's own ATTRIBUTION is narrow: "only the literal scan byte has
evidence [O-60 §3's stamps]... EVERYTHING ELSE IS UNATTRIBUTED." Splitting
the 22 accordingly:

### 3.1 ATTRIBUTED — the literal/run scan-byte class (10 of 22)

| pattern | scanned byte (this sample) | ratio | winner | witness named by plan.md's `[OPT-REQRUN-ENC]` row? |
|---|---|---|---|---|
| `lit-cyr-run` (Москва) | 0xD0 (Cyrillic lead, shared by ~half the alphabet) | ×16.13 | rust | yes |
| `lit-nfc-pair` (café) | `c` (an ordinary French/German/Spanish letter) | ×7.21 | rust | no — plausible, unconfirmed |
| `lit-offset-at-tail` (é@) | 0xC3 (all of Latin-1 Supplement's lead byte) | ×6.38 (×39.6 head-vs-tail at subject grain) | rust | yes |
| `lit-1ch-3b` (日) | 0xE6 (a common CJK lead byte) | ×5.00 | rust | no — plausible, unconfirmed |
| `qnt-counted-3b` | (3-byte counted literal, same run mechanism) | ×4.58 | rust | no — plausible, unconfirmed |
| `lit-mixed-ascii` (user@例え.jp) | `u` (an ordinary English letter) | ×4.55 | rust | yes |
| `lit-run-3` (日本語) | 0xE6 | ×4.46 (×25.5 vs `pcre2-utf-interp` at ×3.28, P2) | rust | yes |
| `lit-nearmiss-run` | (literal run, same mechanism) | ×4.45 | rust | no — plausible, unconfirmed |
| `lit-sharp-s` (Straße) | `S` | ×4.38 | rust | no — plausible, unconfirmed |
| `lit-1ch-4b` (😀) | one lead byte shared by every 4-byte character | ×2.06 | re2 | no — plausible, unconfirmed |

Every one of these ten stamps `RX_REQ_RUN` scanned at index `@0` (§2.1-2.3
of the parent ledger: "Every stamped `RX_REQ_RUN` in this list is scanned
at index `@0`"). rust is flat across the offset-skip order pair
(×1.013-1.018 tail/head, vs pcrec's ×7.30-×39.61 depending on subject) —
the strongest evidence the gap is a pick, not an engine-speed gap. Of the
ten, **only four are named explicitly** as the population
`[OPT-REQRUN-ENC]`'s fix reaches (é@, user@例え.jp, Москва, 日本語); the
other six (café, Straße, 日, the two `nearmiss`/`counted` literals, 😀)
share the identical `@0`-scanned-run stamp but are not individually cited
in the plan row's witness list — carried here as **likely-but-unconfirmed**,
not as closed.

**Diagnosis: algorithmic, not memchr/SIMD-bound.** The underlying scan
primitive (a `memchr`-class pass) is not the problem — pcrec's own
byte-mode floor cell reads 17,611 ns/MiB against libpcre2's 17,693 and
rust's 17,817 (`cycle1_analysis.md`, cited for the general fact that
pcrec's scan loop already reaches memchr-class throughput). The entire gap
above is which byte gets handed to that scan: scanning the shared lead byte
of a whole script block, or an ordinary-frequency ASCII letter, instead of
a genuinely rare byte. That is a pure pick/heuristic defect. Per the
standing sequencing rule (memory `pcrec-post-spine-direction`: "get what we
can algorithmically and generally first... SIMD at the end"), this
population ranks strictly ahead of anything SIMD — **and rust's own
throughput here is plausibly a SIMD literal prefilter, but that reading is
UNVERIFIED**, not a measured fact; nothing here confirms what rust's
matcher is doing internally.

**Is `[OPT-REQRUN-ENC]`'s fix expected to close this?** Yes, for the four
named witnesses, and plausibly for the other six in this bucket — but
**none of it is measured yet**: the fix landed on `main` (abi 38) the same
day as this sample but after it was taken; K68 (abi 39) is still on an
unmerged lane. Scanning rightmost instead of leftmost moves the scanned
byte from the shared lead byte/common letter to whichever byte sits at the
run's tail — for `é@`, that is already `@` (matching `lit-offset-at-head`'s
own byte, closing the ×39.6 asymmetry outright); for
`日本語`/`Москва`/`user@例え.jp`, it moves to a UTF-8 *continuation* byte,
markedly rarer in running prose than a lead byte or an ASCII letter. The
re-measure (I-112) is the literal next step, not a prediction to bank on
without it. **The fix does not touch, and is not claimed to touch, the
other 12 of the 22 losses below.**

### 3.2 UNATTRIBUTED — no mechanism identified (12 of 22)

| family | patterns | ratio | winner |
|---|---|---|---|
| caseless | `ci-ascii-control` | ×4.69 | rust |
| | `ci-sigma` | ×3.43 | rust |
| | `ci-strasse` | ×2.85 | rust |
| | `ci-moskva` | ×2.70 | rust |
| alternation | `alt-distinct-lead` | ×7.33 | rust |
| | `alt-nearmiss` | ×4.00 | rust |
| assertions (non-lookbehind) | `asr-b-ascii` | ×4.97 | rust |
| | `asr-dollar-ml` | ×3.12 | rust |
| lookbehind | `asr-lb-varwidth` | ×8.15 | `pcre2-utf-jit` |
| | `asr-lb-neg` | ×3.38 | oniguruma |
| | `asr-lb-fixed` | ×2.85 | `pcre2-utf-jit` |
| other | `cls-dot-rep` | ×2.21 (~92.9 vs ~42.0 ns — noise-scale absolute cost) | rust |

**No plan.md row, design note, or bench ledger asserts a cause for any row
in this table.** R6 (Surprise C, §2 above) checked engine-selection specifically and
found nothing wrong with pcrec's own choices on the population it could
reach; it did not, and could not, explain WHY the chosen mechanism costs
what it costs against rust/pcre2-jit/oniguruma on these twelve. The
lookbehind trio is VM-route (Surprise C, §2 above: `auto` gives all four lookbehind
patterns — including the two here — a real hybrid prefilter,
`vm_prefilter_lang=exact`, and still loses ×2.85-8.15). Treat this whole
table as OPEN, not as a queued fix — §5 proposes a read (not a fix) to
narrow it.

**The bench's own attribution discipline, stated once for both tables.**
All of §2.1-2.3, the addenda's own reading, and the R6 census agree: no
cause beyond the stamps is asserted by the bench itself for even the
ATTRIBUTED table (parent ledger §7: "no cause is asserted for pcrec's
scan-byte choice beyond the stamps... the link is for pcrec to confirm").
pcrec's own plan.md is what supplies the mechanism and the fix for §3.1;
nothing in either repository supplies one yet for §3.2.

## 4. IMPACT

- **Zero correctness risk found.** pcrec is the only compiled-C testee with
  0 wrong answers on all four configs; the fix in flight touches only which
  byte a prefilter scans, never an answer.
- **The ATTRIBUTED throughput gap (10 literal-run patterns, ×2.1-×16 vs
  rust/re2) already has a landed, root-caused fix for its named subset**
  (`[OPT-REQRUN-ENC]`, abi 38) — a same-day finding-to-fix
  turnaround for 4 of 10, plausible-but-unconfirmed for the other 6, not
  measured against any of them yet.
- **The UNATTRIBUTED throughput gap (12 patterns: caseless, alternation,
  two non-lookbehind assertions, the lookbehind trio, `cls-dot-rep`) has
  no mechanism and no fix in flight.** This is more than half of the 22
  losses and is not to be read as "closing soon" — it needs its own
  attribution read (§5) before any fix is proposed.
- **The compile-time gap (`\p{L}+`/`\P{L}+`, up to 106 s) has two filed,
  evidenced, not-yet-scheduled rows** — `[OPT-RETRY-REUSE]` (the retry
  ladder's per-rung rebuild, K67's witness) and `[OPT-CLOSURE-CTX]` (the
  loop-context closure path K67 also names) — whose own "measured need"
  sections already cite this sample's numbers.
- **One census item (`alt-cyr-64`) is fully dispositioned as a
  non-defect** by a dedicated control read against `altwide`'s existing
  branch-count ladder — no work item.
- **One upstream finding (U11)** is understood, not actionable, and not
  ours to fix.

## 5. NEXT STEPS

| item | state | owner |
|---|---|---|
| (i) Merge lane `k68fix` (K68, abi 39) | built, pending merge | pcrec manager |
| (i) Send inbox I-112 (the utf8 re-measure at abi 39, both fixes present — the acceptance surface for §3.1's 4 named witnesses AND the 6 unconfirmed) | owed once K68 merges | pcrec manager → bench |
| `[OPT-REQRUN-ENC]` | STATE:done, merged `main` (abi 38) | closed |
| `[OPT-RETRY-REUSE]` / `[OPT-CLOSURE-CTX]` | filed, not scheduled — own the `\p{L}+`/`\P{L}+` compile-time gap (K67); this sample's numbers are already their cited evidence | queued, D125 sequencing |
| `[OPT-LITSCAN]` | STATE:started (S1 steps 1-5 built) — the general literal-search kit that eventually owns a *proper* UTF-8-frequency-aware pick (an "encoding-keyed prior") replacing `[OPT-REQRUN-ENC]`'s rightmost stopgap; S4 (caseless) is the sequenced step that would eventually reach the `ci-*` rows in §3.2, once it opens | in flight, cycle-3 row |
| (ii) An ATTRIBUTION READ of the 12 unattributed rows (§3.2) at current `main`: per-pattern mechanism stamps (`engine`, `engine_sel`, `dfa_prefilter`/VM `prefilter`, `req_byte`/`req_run`) plus `--emit-facts` where it applies, read in the bench's own look-first order (lookbehind trio first among these twelve, since it is the largest non-scan-byte loss cluster; then the caseless/alternation/assertion rows). **Proposed, not run** — a read-only lane, no `src/` change, mirroring the addenda's own no-measurement-no-report discipline. | proposed | pcrec, next lane |
| (iii) Owners for a future fix, found by grepping `plan.md` (facts, not commitments): `[OPT-LITSCAN]` S4 for the caseless (`ci-*`) rows once its sequence reaches caseless; `[OPT-A]` (STATE:not-started, the rarest-byte/pair-scan/multi-literal survey) is the closest existing row for a multi-literal or alternation-prefix mechanism (`alt-distinct-lead`/`alt-nearmiss`); **no existing row targets lookbehind throughput specifically** — `[ENG-LOOK]` (STATE:not-started, lookaround-by-product-construction in the DFA engine) is the nearest general mechanism that could remove the VM-forced route the lookbehind trio sits on today, but it is not scoped as a throughput fix and nobody has proposed it as one. | proposed for filing, not filed | Frank / pcrec manager |
| `lit-nfc-pair`/`lit-sharp-s`/`lit-1ch-3b`/`lit-nearmiss-run`/`qnt-counted-3b`/`lit-1ch-4b` — confirm same `[OPT-REQRUN-ENC]` mechanism | unconfirmed, named in §3.1 | fold into the I-112 re-measure reading |
| `alt-cyr-64` | dispositioned (non-defect); recommend citing `altwide`'s curve in `bench/utf8/NOTES.md`'s R5 writeup per the control read's own suggestion | bench-side, no pcrec action |

No new plan row is proposed for the ATTRIBUTED population: every finding
there lands on an existing row (`[OPT-REQRUN-ENC]`, closed same-day;
`[OPT-RETRY-REUSE]`/`[OPT-CLOSURE-CTX]`, already evidenced by this exact
data; `[OPT-LITSCAN]`, the eventual general-prior owner) or is
dispositioned as a non-defect (`alt-cyr-64`) or an upstream,
non-actionable finding (U11). The UNATTRIBUTED population (§3.2) is NOT
closed by any of this — item (ii) above is what would turn it into
proposable rows, and it is not run here.

---

## Revision (utf8sum2, against the bench's own committed reports)

This revises the prior draft (lane `utf8sum`) against
`pcrec-bench`'s reports/ledgers/O-60 directly (see header list), plus an
independent recomputation of the large-subject tally from the report's own
`matrix.tsv` (per-pattern best-of-4-pcrec-configs vs. best-of-6-full-grain-
competitors, `vectorscan` excluded) to cross-check the bench's numbers
rather than merely transcribe them. Corrections and additions:

1. **Added the full tally** (42 win / 5 lose ≤×2 / 22 lose >×2 / 6 n/a on
   `large-subject-throughput`; 68 win / 1 lose ≤×2 / 0 lose >×2 on
   `short_subject_search`) — the prior draft stated only the pooled
   "22 of 138" figure. Independently recomputed from `matrix.tsv` and
   found to match Frank's team-lead brief exactly, including all 22
   pattern names and their winners.
2. **Split the 22 large-subject losses into ATTRIBUTED (§3.1, 10 rows,
   the literal/run scan-byte class) and UNATTRIBUTED (§3.2, 12 rows:
   caseless, alternation, two assertions, the lookbehind trio,
   `cls-dot-rep`)** — the prior draft named only the 7 worst literals and
   left the other 15 as a one-line list inside §1, which could be read as
   implying the landed fix bears on all 22. It does not; §3.1's closing
   line states this explicitly now.
3. **Corrected the literal count from 7 to 10**: `qnt-counted-3b`,
   `lit-nearmiss-run`, and `lit-1ch-4b` were previously omitted from the
   detailed table (they were named only via O-58/O-60's shorter list or
   the R7 addendum) despite carrying the identical `@0`-scanned-run stamp
   and belonging in the same attributed bucket.
4. **Kept, and sharpened, the SIMD-honesty framing**: added an explicit
   line that rust's own throughput on the attributed rows is "plausibly a
   SIMD literal prefilter, but that reading is UNVERIFIED" — the prior
   draft's "SIMD later" framing did not carry this caveat as explicitly.
5. **Added `[OPT-CLOSURE-CTX]` and K67** alongside `[OPT-RETRY-REUSE]` in
   the compile-time gap's IMPACT/NEXT-STEPS entries — both are cited by
   `plan.md` as owning K67's witness (`\p{L}+ -e utf8`) jointly with
   `[OPT-RETRY-REUSE]`; the prior draft named only the latter.
6. **NEXT STEPS**: added (i) the I-112 re-measure (carried over, sharpened
   to name it as the acceptance surface for both the confirmed and
   unconfirmed attributed witnesses), (ii) a PROPOSED (not run)
   attribution-read plan for the 12 unattributed rows, and (iii) owners
   for a future fix found by grepping `plan.md` — `[OPT-LITSCAN]` S4 for
   caseless, `[OPT-A]` for multi-literal/alternation, and the finding that
   **no existing plan row targets lookbehind throughput**; `[ENG-LOOK]` is
   the nearest general mechanism but is not scoped as a throughput fix.
   None of (ii)/(iii) is run or filed here — proposals only, per brief.
7. No number in the prior draft's §1/§2/§4 (correctness, compile times,
   U11, `alt-cyr-64`) was found to disagree with the bench's committed
   reports on independent re-check; those sections are carried forward
   unchanged in substance.
