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

**Large-subject-throughput regime: this is where pcrec loses.** Of 138
auto-rankable cells, 116 tie or beat the best full-grain competitor within
×2; the other **22 (16%) lose by more than ×2, and every one of them is a
`large-subject-throughput` cell** — none in `search_short`
(§2.3). Seven are literals sharing one mechanism (§3, below); the rest are
lookbehinds (VM route, ×2.85-×8.15 vs `pcre2-utf-jit`), one byte-class
alternation, and several folds/anchors at ×2.2-×5.0. See §3 for the
dedicated reading.

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

## 3. LARGE-SUBJECT SEARCH — the one regime where pcrec loses, in detail

**Which patterns, which engines, how big.** Seven literal patterns carry
the seven worst of the 22 outlier cells against `rust-default` (the
strongest competitor on this population):

| pattern | subject | scanned byte (this sample) | ratio vs rust |
|---|---|---|---|
| `lit-cyr-run` (Москва) | `t-64k-cyr` | 0xD0 (Cyrillic lead, shared by ~half the alphabet) | ×16.13 |
| `lit-nfc-pair` (café) | `t-64k-lat` | `c` (an ordinary French/German/Spanish letter) | ×7.21 |
| `lit-offset-at-tail` (é@) | `t-64k-lat` | 0xC3 (all of Latin-1 Supplement's lead byte) | ×6.38 (×39.6 head-vs-tail at subject grain) |
| `lit-1ch-3b` (日) | `t-64k-cjk` | 0xE6 (a common CJK lead byte) | ×5.00 |
| `lit-mixed-ascii` (user@例え.jp) | `t-64k-asc` | `u` (an ordinary English letter) | ×4.57 |
| `lit-run-3` (日本語) | `t-64k-cjk` | 0xE6 | ×4.46 (×25.5 vs `pcre2-utf-interp` at ×3.28, P2) |
| `lit-sharp-s` (Straße) | `t-64k-lat` | `S` | ×4.38 |

Every one of these seven has the identical mechanism: `RX_REQ_RUN`'s
scanned member sits at index `@0` (§2.1-2.3 of the parent ledger). rust is
flat across the offset-skip order pair (×1.013-1.018 tail/head, vs pcrec's
×7.30-×39.61 depending on subject) — the strongest evidence the gap is a
pick, not an engine-speed gap.

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
population ranks strictly ahead of anything SIMD, and correctly so — it is
already fixed without SIMD.

**Is `[OPT-REQRUN-ENC]`'s fix expected to close this?** Yes, for six of the
seven — `docs/dev/plan.md`'s own `[OPT-REQRUN-ENC]` row cites these *exact*
witnesses (é@, user@例え.jp, Москва, 日本語) by name as the population its
rightmost-scan fix reaches. Scanning rightmost instead of leftmost moves
the scanned byte from the shared lead byte/common letter to whichever byte
sits at the run's tail — for `é@`, that is already `@` (matching
`lit-offset-at-head`'s own byte, closing the ×39.6 asymmetry outright); for
`日本語`/`Москва`/`user@例え.jp`, it moves to a UTF-8 *continuation* byte,
which is markedly rarer in running prose than a lead byte or an ASCII
letter. `lit-nfc-pair` (café) and `lit-sharp-s` (Straße) are plausibly the
same mechanism (their runs are also scanned at index 0 today) but are not
named explicitly in the plan row's witness list, so treat those two as
likely-but-unconfirmed until the re-measure. `lit-1ch-4b` (😀, the R7
high-side outlier at ×1.95-2.45) is a single 4-byte character whose whole
run is one lead byte shared by every emoji/4-byte character — plausibly the
same family, also unconfirmed. **None of this is measured yet**: the fix
landed on `main` (abi 38) the same day as this sample but after it was
taken; K68 (abi 39) is still on an unmerged lane. The re-measure is the
literal next step, not a prediction to bank on without it.

**The bench's own attribution.** All of §2.1-2.3, §3's addendum reading,
and the R6 census agree: no cause beyond the stamps is asserted by the
bench itself (parent ledger §7: "no cause is asserted for pcrec's scan-byte
choice beyond the stamps... the link is for pcrec to confirm"). pcrec's own
plan.md is what supplies the mechanism and the fix.

## 4. IMPACT

- **Zero correctness risk found.** pcrec is the only compiled-C testee with
  0 wrong answers on all four configs; the fix in flight touches only which
  byte a prefilter scans, never an answer.
- **The headline throughput gap (7 literals, ×4.4-×16 vs rust) already has
  a landed, root-caused fix** (`[OPT-REQRUN-ENC]`, abi 38) — this is a
  same-day finding-to-fix turnaround, not a new backlog item.
- **The compile-time gap (`\p{L}+`/`\P{L}+`, up to 106 s) has a filed,
  evidenced, not-yet-scheduled row** (`[OPT-RETRY-REUSE]`) whose own
  "measured need" section already cites this sample's numbers.
- **One census item (`alt-cyr-64`) is fully dispositioned as a
  non-defect** by a dedicated control read against `altwide`'s existing
  branch-count ladder — no work item.
- **One upstream finding (U11)** is understood, not actionable, and not
  ours to fix.

## 5. NEXT STEPS

| item | state | owner |
|---|---|---|
| Merge lane `k68fix` (K68, abi 39) | built, pending merge | pcrec manager |
| Send inbox I-112 (the utf8 re-measure at abi 39, both fixes present) | owed once K68 merges | pcrec manager → bench |
| `[OPT-REQRUN-ENC]` | STATE:done, merged `main` (abi 38) | closed |
| `[OPT-RETRY-REUSE]` | filed, not scheduled — owns the `\p{L}+`/`\P{L}+` compile-time gap; this sample's numbers are already its cited evidence | queued, D125 sequencing |
| `[OPT-LITSCAN]` | STATE:started (S1 steps 1-5 built) — the general literal-search kit that eventually owns a *proper* UTF-8-frequency-aware pick (an "encoding-keyed prior") replacing `[OPT-REQRUN-ENC]`'s rightmost stopgap; plan.md states this explicitly | in flight, cycle-3 row |
| `lit-nfc-pair`/`lit-sharp-s`/`lit-1ch-4b` — confirm same mechanism | unconfirmed, named in §3 | fold into the I-112 re-measure reading |
| `alt-cyr-64` | dispositioned (non-defect); recommend citing `altwide`'s curve in `bench/utf8/NOTES.md`'s R5 writeup per the control read's own suggestion | bench-side, no pcrec action |

No new plan row is proposed: every finding in this sample lands on an
existing row (`[OPT-REQRUN-ENC]`, closed same-day; `[OPT-RETRY-REUSE]`,
already evidenced by this exact data; `[OPT-LITSCAN]`, the eventual
general-prior owner) or is dispositioned as a non-defect (`alt-cyr-64`) or
an upstream, non-actionable finding (U11).
