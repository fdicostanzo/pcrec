# Reading: uses per activation of R-17's set-FIND sites on the bench's own subjects

Lane r17upa, 2026-10-12, for the memfn kit manager. COUNTS ONLY, no timing.
The question came from the bench, through main: how many USES does one ACTIVATION
of a set-FIND site get on the bench's own subjects? This decides whether a stateful
form's carried state pays. The kit's break-even `B_EVEN` lies between 1 and 4
uses per state lifetime (setfind.md rev 2.3 §9.2; `mask8_swar` reads ~2-3 in
`reading_slot2.md`). Background: setfind.md §7.5 and §9.2, r5 K3-4, and
`setfind_bench_request.md` §2 and §5 (Q3).

Instrument, data and every table: `upa/` (own CLAUDE.md). Full generated tables:
`upa/out/tables.md`. Raw counts: `upa/out/counts.tsv.gz`.

## Headline

- **(a) Search-short (one `rx_search(s, n, 0)` per short subject): BELOW the
  break-even everywhere R-17 names.** On the named cells the median activation
  has 1 use (0 on `bkn`/`bpr`, where a pre-check rejects 95-96% of short
  subjects before the site is reached; 2 on `u8l`, whose bounded walk takes one
  more trivial use at the subject's last byte). Apart from `u8l`'s tail, at most 40% of
  activations reach 2 uses (`alt2`/`alt2r`; 16% on `adl`, ≤ 5% elsewhere), and
  none reaches 16. Bench-wide, 95 of 135 site-bearing cells are
  BELOW in this regime, 10 IN-BRACKET and 30 ABOVE. The ABOVE cells are altwide's
  512 B prose lines and loglines' 4 KiB chunks.
- **(b) Find-all, per `rx_search` call (the state's real lifetime): the named
  cells split by how many candidates the DFA rejects.** `adl` sits far ABOVE: the
  pooled median is 168 uses per call, and per subject the median runs from 31 to
  20,280. It passes 290-440 candidates per match on the mixed subjects and 38-52
  on the Latin and CJK ones. `alt2`/`alt2r` are ABOVE: median 6, 86%
  of calls take at least 2 uses and 65% at least 4. Seven cells sit at 1 use per
  call:
  - `sig` and `hbr` have no candidates at all in any find-all subject, so each
    call is one long miss scan;
  - in `kel`, `tki`, `qdm`, `bkn` and `bpr` nearly every candidate is a match
    (1.0-1.3 candidates per match).

  `u8l` reads 2 for the bounded-tail reason above, with zero candidates.
- **No named cell sits in the state-lost DENSE corner on the bench's subjects.**
  Every named cell at 1 use per call has a density of 0-56,870 ppm (the kit's
  `T_DENSE` bracket is ~300k). There, one use is one long scan, which a word-wide
  form wins on scan width whether or not state carries. The one dense named
  subject is `adl` on `t-64k-cyr` (309k ppm), and it carries 20,280 uses in its
  single activation.
- **The state-lost dense corner is real elsewhere on the bench, and it is the
  dense controls.** Two groups qualify: the `[0-9]` cells on the all-digit
  subjects, and the `[a-z]` cells on the all-letter subjects. Their density is
  1,000,000 ppm, and every call's first byte is a candidate that becomes the
  match. Together with `\w`/`.`/class cells on dense text, 138 find-all
  (cell, subject) rows over 46 cells sit at ≥ 300k ppm with median < 4 uses and a
  set of ≤ 4 terms (upper bound; §4). That corner is §9.2's (a) case, the
  `[FINDALL-NEXT]` residual.
- **(c) VM hybrids, per prefilter-function call: mostly 1 use per call at low
  density.** Of 16 hybrid cells, 12 have a median of 1 in find-all, and 2 are never
  entered there. Two exceptions
  carry state: `loglines/level-context` (31 per call in find-all, 6 in
  search-short) and `capability/wild-logparse-syslogbase-expanded` (7,669). Two
  hybrid subjects are in the dense corner, both on `t-mixed-runs-4k`:
  `wild-logparse-base10num-grok` (492k ppm) and
  `wild-semdiv-empty-alt-repeat-pcre2` (450k).

## 1. Method, and why this one

**A post-processed copy of the shipped compiler's emitted C, with counters at the
site.** It is answer-identical by test: the plain and the instrumented builds
give byte-identical answers on every subject of every cell. The steps:

1. **Compile each bench pattern exactly as the bench's pcrec testee does.** The
   argv is that of `testees/pcrec/adapter.py` at bench `1cb906f6`:
   `pcrec -p rx -fcomments --features all [--no-captures] [-e utf8] -o artifact.c
   --pattern <raw bytes>`. The compiler is `build/pcrec` of this tree, which is
   lane/memfn-r17 at `0409c204` with `src/` unchanged. Two configs are run, the
   testees `auto` (caps) and `nocaps` that the bench's utf8 reports use.
2. **Find every set-FIND site.** A site is a 256-entry table walk
   `while (P < N && !T[S[P]]) P++;`, and its bounded twin `P + 1 < N`. This is
   census.py's `WALK_RE`, so the population is the one census.py classifies. The
   role comes from the table name: DFA prefilter `can_begin_match`, DFA hat
   `start_bytes`, VM hat `start_set`. The holding function comes from the C:
   `rx_search` for DFA sites, `rx_search_run` for VM hats, `rx_prefilter` for a
   hybrid's prefilter.
3. **Instrument a copy.** `upa_act(F)` goes at the holding function's entry. One
   activation is one call of that function, which is the lifetime of the
   storage a stateful form declares there (setfind.md §7.5). Each walk statement
   becomes `{ <walk> upa_use(F, hit, pos); }`, so one use is one "next candidate
   at or after lo". The counter is test-only static state in the driver; no
   artifact text outside the copy changes.
4. **Drive both builds exactly as the bench's `timed.c` does (read, not
   copied).** search-short makes ONE `rx_search(s, n, 0)` per short subject.
   find-all runs the match_api.md §3.1 loop: advance off `caps[0][0]`, step a
   character on an empty match, and use the utf8 advance on the utf8 set (the
   harness sets `--utf8` from the set's encoding).
5. **Use the bench's own subjects and mapping.** Patterns and the regime-to-subject
   mapping come from the bench's loader (`pcrecbench.subbench`). Subjects are
   regenerated by the bench's own generators into a scratch `git archive` copy.
   Every set's `manifest.tsv` and `manifest_throughput.tsv` reproduced byte for
   byte. Nothing was written to the bench tree.

**Why not the filed `mfk-upa` (a kit trace rendering).** It would count the same
thing, but it needs R17-b's storage sites to exist in kit text. The site, its
holding function and the call pattern are all already in today's emitted C, and
a stateful form changes none of them. A post-processed copy therefore answers
the question for today's artifacts and for R17-b's alike, with no build change
and nothing in the default build. The text hook is kept as a probe script (D77:
`mfk-upa` stays filed).

**Levels.** The tables read the `fn:` level, one activation per call of the
holding function. Two other levels are recorded:
- `call`: one `rx_search`;
- `pass`: one whole find-all pass, the brief's activation (b) taken literally.

For DFA and prefilter-less VM sites, `fn` equals `call`, except that a FRAMES
give-up escalates to `rx_search_deep` and enters `rx_search_run` a second time,
with fresh storage. For hybrids, `fn` is one prefilter call, entered once per VM
re-seed (activation (c)). The `pass` level is NOT a state lifetime, because
storage dies with every `rx_search` return. It is reported only as the upper
bound a cross-call state (`state_by_caller`, §17) would see.

**Bands.** The brief brackets `B_EVEN` in (1, 4): the kit loses at 1 use and wins
at 4. A cell is:
- BELOW when its median activation has ≤ 1 use;
- ABOVE when the median is ≥ 4;
- IN-BRACKET for 2-3, where nothing has been timed.

The median is §9.2's proposed statistic.

## 2. Controls (all green)

| control | what it is checked against | result |
|---|---|---|
| answer identity | the plain artifact's answers (first span, match count, a hash of every span) on every subject | 270 cell × config pairs, identical on all |
| oracle | the bench's own `expectations.tsv` (libpcre2 10.46 differential, independent of pcrec) | every answer agrees except 18, all three `syntax/rec-{1,name,r-uc}` find-all subjects × 2 configs. Those are pcrec give-ups (`giveup=-3`), identical in the plain build, a known give-up cell |
| monotone positions | within one activation, successive candidate positions strictly rise (in the driver) | 0 violations |
| hit bound | a level's hits ≤ (bytes of the subject in S, counted from the parsed table) × activations | 0 violations |
| activation bound | calls ≤ activations of a site in `rx_search`/`_run` ≤ 2 × calls (deep tier) | 0 violations |
| PLANTED | `--plant`: the copy skips every candidate it finds | all 11 named cells fire: identity false, 85 oracle diffs (`upa/out/planted_controls.tsv`) |

Population (K35): 704 jobs = 352 bench patterns × 2 configs, over 8 sets. The
`sentinel` set is skipped as a byte copy of capability. Of the 704:
- 270 have at least one site;
- 387 have none (memchr, offset-skip, anchored, or no prefilter);
- 47 are refused by pcrec (module refusals and size caps, the bench's own refused cells).

## 3. The R-17 named cells (config auto; nocaps is identical on all 11)

Pooled over each regime's subjects. The find-all medians are per subject, with
density in S in parentheses. Search-short pools one activation per short subject
(at most 93 B in capability, syntax and utf8).

| cell | kit | site (role, fn, \|S\|, terms<=) | search-short: act, median [p10, p90] max, >=2 | find-all: act, median [p10, p90] max, >=2 / >=4 / >=16 | find-all medians per subject (density ppm) | band short / find-all |
|---|---|---|---|---|---|---|
| utf8/alt-distinct-lead | adl | dfa-pf, rx_search, 3, 3 | 91, 1 [1, 2] 8, 0.16 | 645, 168 [12, 653] 20280, 0.99 / 0.95 / 0.89 | t-64k 139 (124054), t-256k 287 (123390), t-1m 219 (122284), t-64k-lat 31 (24597), t-64k-cyr 20280 (309433), t-64k-cjk 46 (53070), t-64k-asc 2398 (37933) | BELOW / ABOVE |
| utf8/ci-sigma | sig | dfa-pf, rx_search, 2, 1 | 91, 1 [1, 1] 5, 0.05 | 7, 1 [1, 1] 1, 0.00 / 0.00 / 0.00 | t-64k 1 (0), t-256k 1 (0), t-1m 1 (0), t-64k-lat 1 (0), t-64k-cyr 1 (0), t-64k-cjk 1 (0), t-64k-asc 1 (0) | BELOW / BELOW |
| utf8/ci-kelvin | kel | dfa-pf, rx_search, 3, 2 | 91, 1 [1, 1] 1, 0.00 | 4765, 1 [1, 2] 97, 0.16 / 0.01 / 0.00 | t-64k 1 (3220), t-256k 1 (3548), t-1m 1 (3612), t-64k-lat 1 (2228), t-64k-cyr 97 (1465), t-64k-cjk 1 (3052), t-64k-asc 1 (7050) | BELOW / BELOW |
| utf8/ci-turkish-i | tki | dfa-pf, rx_search, 2, 1 | 91, 1 [1, 1] 1, 0.00 | 41545, 1 [1, 1] 1, 0.00 / 0.00 / 0.00 | t-64k 1 (25177), t-256k 1 (24807), t-1m 1 (25133), t-64k-lat 1 (46005), t-64k-cyr 1 (0), t-64k-cjk 1 (4410), t-64k-asc 1 (56870) | BELOW / BELOW |
| syntax/alt-nested | alt2 | dfa-pf, rx_search, 2, 1 | 42, 1 [1, 3] 8, 0.40 | 11395, 6 [1, 19] 78, 0.86 / 0.65 / 0.15 | t-64k 6 (70038), t-256k 6 (69405), t-1m 6 (69790) | BELOW / ABOVE |
| syntax/alt-two | alt2r | dfa-pf, rx_search, 2, 1 | 42, 1 [1, 3] 8, 0.40 | 11395, 6 [1, 19] 82, 0.86 / 0.65 / 0.16 | t-64k 6 (70038), t-256k 6 (69405), t-1m 6 (69790) | BELOW / ABOVE |
| capability/high-byte-run | hbr | dfa-pf, rx_search, 128, 1 | 75, 1 [1, 1] 2, 0.03 | 11, 1 [1, 1] 1, 0.00 / 0.00 / 0.00 | t-64k 1 (0), t-256k 1 (0), t-1m 1 (0), t-evil-match-60k 1 (0), t-evil-nearmiss-16k 1 (0), t-trim-match-60k 1 (0), t-trim-nearmiss-16k 1 (0), t-mixed-runs-4k 1 (0), t-tail-digits-1m 1 (0), t-tail-txt-1m 1 (0), t-tail-space-1m 1 (0) | BELOW / BELOW |
| capability/utf8-lead-no-cont | u8l | dfa-pf bounded, rx_search, 30, 1 | 75, 2 [2, 2] 2, 0.99 | 11, 2 [2, 2] 2, 1.00 / 0.00 / 0.00 | t-64k 2 (0), t-256k 2 (0), t-1m 2 (0), t-evil-match-60k 2 (0), t-evil-nearmiss-16k 2 (0), t-trim-match-60k 2 (0), t-trim-nearmiss-16k 2 (0), t-mixed-runs-4k 2 (0), t-tail-digits-1m 2 (0), t-tail-txt-1m 2 (0), t-tail-space-1m 2 (0) | IN-BRACKET / IN-BRACKET |
| capability/quoted-delim-match | qdm | vm-hat, rx_search_run, 2, 2 | 75, 1 [1, 1] 2, 0.01 | 3875, 1 [1, 1] 1, 0.00 / 0.00 / 0.00 | t-64k 1 (5432), t-256k 1 (5424), t-1m 1 (5674), t-evil-match-60k 1 (0), t-evil-nearmiss-16k 1 (0), t-trim-match-60k 1 (0), t-trim-nearmiss-16k 1 (0), t-mixed-runs-4k 1 (0), t-tail-digits-1m 1 (0), t-tail-txt-1m 1 (0), t-tail-space-1m 1 (0) | BELOW / BELOW |
| syntax/bak-k-named | bkn | vm-hat, rx_search_run, 1, 1 | 42, 0 [0, 0] 1, 0.00 | 5359, 1 [1, 3] 9, 0.13 / 0.02 / 0.00 | t-64k 1 (8484), t-256k 1 (8232), t-1m 1 (9165) | BELOW / BELOW |
| capability/balanced-parens-rec | bpr | vm-hat, rx_search_run, 1, 1 | 75, 0 [0, 0] 1, 0.00 | 7872, 1 [1, 1] 1, 0.00 / 0.00 / 0.00 | t-64k 1 (5234), t-256k 1 (5558), t-1m 1 (5780), t-evil-match-60k 0 (0), t-evil-nearmiss-16k 0 (0), t-trim-match-60k 0 (0), t-trim-nearmiss-16k 0 (0), t-mixed-runs-4k 0 (0), t-tail-digits-1m 0 (0), t-tail-txt-1m 0 (0), t-tail-space-1m 0 (0) | BELOW / BELOW |

Reading the bands against §9.2:

- **ABOVE (state pays): `adl` and `alt2`/`alt2r` in find-all.** `adl`'s DFA
  rejects 290-440 candidates per match on the mixed subjects and 38-52 on the
  Latin and CJK ones. On the match-free Cyrillic and ASCII subjects one call takes
  2,398-20,280 uses. `alt2`'s rejects about 8 per match at
  70k ppm. These are the cells where a carried mask turns every rejected candidate
  into a bit-scan.
- **BELOW, sparse (state cannot pay, the form still can): `sig`, `hbr`, `kel`,
  `tki`, `qdm`, `bkn`, `bpr`, and `u8l` (2, bounded tail).** Find-all density is
  0-56,870 ppm. One use is one long scan (on `sig` and `hbr`, the whole subject).
  §9.2's decline needs (D) AND (P), and these cells fail (D), so the stateful row
  ADMITS. Its gain here is scan width, not state.
- **Search-short is BELOW for every named cell.** The subjects are 1-93 B; the
  state lives for one call and is used once (or not at all: `bkn` and `bpr` are
  95-96% zero-use, behind a pre-check memchr). If R17-b's stateful row costs more
  than the walk at 1 use on a short span, this is the regime that would show it.
  §9.2(b), dense per-call, is the matching corner, and the per-call figure is the
  bench timing's to give.

Per-subject detail (find-all rows per subject, the state-lifetime level):
Appendix A.

## 4. Dense controls, and where the decline corner actually is

Q1 asks the bench to name its dense controls. From the census, the candidates are
the cells whose site set is exactly `[0-9]` (25 cells) or exactly `[a-z]` (14
cells): `upa/out/tables.md` §"Dense controls". They behave in two opposite ways:

- **State-lost dense, §9.2 corner (a).** The `bounded/` family runs on its
  uniform subjects (`t-digits-*`, `t-letters-*`, 1,000,000 ppm): `dig-exact-*`,
  `dig-upto-*`, `year4`, `nest*`, `hex32`, `cls-atleast-4096`, `nest2-letters-6`,
  `line-80`, `pw-8-64`. Every call's first byte is the candidate that becomes the
  match, so the median is 1, with 0% at ≥ 2. The same holds at 300k-1M ppm with
  1.0 candidates per match for:
  - `syntax/cls-w`, `syntax/mod-a`, `syntax/cls-posix` (`\w`/`[[:alpha:]]`, 694-764k);
  - `utf8/cls-dot`, `utf8/cls-neg-single`, `utf8/ci-neg-fold`, `utf8/cls-mixed` and the other wide utf8 classes (366k-1M).
- **Dense but state-carrying.** altwide's `[a-z]` prefilters (`s-*`, `w-*`,
  `srt-*`, `wb-*`, `clsa-*`, `clsd-*`) run at about 780k ppm with medians of 15 to
  59,215 per call, because the wide-alternation DFA rejects nearly every
  candidate. Density alone does not predict lost state; the reject rate does.

The full corner list (`summarize_upa.py out --corner 300000`) has 165 find-all
(cell, subject) rows at ≥ 300k ppm with median < 4. Of these, 138 rows over 46
cells have a set of at most 4 terms. That is an UPPER BOUND on terms: the fewest
of the set's maximal ranges, its complement's ranges and census.py's greedy cube
cover. The kit's `mf_set_terms` decides admission. Nine of the rows are
`dup-param-detect`, whose median is 0: the pre-check rejects before the hat, so
storage is declared and never used, and those rows are not a corner at all.

## 5. VM hybrids (activation (c): one prefilter call, entered once per VM re-seed)

16 hybrid cells hold a site in `rx_prefilter` (`upa/out/tables.md` §"VM hybrids").

| group | cells | find-all median per prefilter call |
|---|---|---|
| carries state | `loglines/level-context` (dfa-hat {3 bytes}) | 31 (23-4,446 per subject); search-short 6 |
| carries state | `capability/wild-logparse-syslogbase-expanded` (dfa-hat, 16) | 7,669 (269-120,666) |
| BELOW, low density | `bounded/ctx-*` (4), `syntax/rec-{back,fwd,g-angle,py}`, `utf8/asr-lb-class`, `wild-logparse-quotedstring-grok` | 1 (5k-155k ppm) |
| BELOW, one dense subject | `wild-logparse-base10num-grok`, `wild-semdiv-empty-alt-repeat-pcre2` | 1; `t-mixed-runs-4k` at 492k/450k ppm is in the corner |
| never entered in find-all | `wild-logparse-winpath-grok`, `wild-secrets-username-password-pair` | (pre-check rejects every throughput subject) |

The r5 K3-4 point is borne out. "Per retry" is a proxy, and two hybrids carry
tens to thousands of uses per prefilter call, where the DFA rejects candidates
inside one entry.

## 6. Answers to the bench's Q2/Q3 from this run (relay facts, read not timed)

- **Q2 (rescan, sizes).** `timed.c`'s find-all timed loop repeats the WHOLE pass
  `iters` times over the same buffer, so a sample rescans one subject. Find-all
  subject sizes per set:

  | set | sizes |
  |---|---|
  | syntax | 64 KiB, 256 KiB, 1 MiB |
  | utf8 | 64 KiB, 256 KiB, 1 MiB, plus four 64 KiB script corpora |
  | capability | 4 KiB-1 MiB, 11 subjects |
  | bounded | 4-64 KiB |
  | altwide | 128/512 KiB |
  | loglines | 16 KiB-1 MiB |

  The 64K caveat therefore applies to every 64 KiB subject the bench times.
- **Q3 (uses per activation).** Answered here from a pcrec-side copy, not from the
  harness. The bench need not count it. Density in S per subject is in
  `counts.tsv` (`density_ppm`). Candidates per match is `hits_per_match`; this is
  a cross-check figure, not the bench's own count, which the bench does not
  publish.

## 7. Summary for the bench (main relays)

For R-17's set-FIND sites we counted uses per activation on your own subjects.
The subjects were regenerated by your generators (manifests byte-identical), and
each artifact was driven exactly as `timed.c` drives it, with answers checked
against your expectations. Two caveats on the method: it was pcrec-side
instrumentation of a copy, and no timing was taken.

- **Short-subject search.** One `rx_search` per subject sits at 1 use per call
  (0 where a pre-check rejects first) on every named cell. That is below the
  kit's 1-4 break-even, so a stateful form cannot recover its setup there.
- **Find-all, state pays.** `utf8/alt-distinct-lead` (median 31-20,280 uses per
  call by subject) and `syntax/alt-nested`/`alt-two` (median 6) are well above
  the break-even.
- **Find-all, state does not pay, but the cells are sparse.** The other named
  cells take 1 use per call at 0-57k ppm, so the new form's win there, if any,
  is scan width.
- **The dense controls.** The corner the kit worries about (1 use per call at ≥
  300k ppm, every candidate a match) is not among the named cells. It is your
  dense controls: the `bounded/` `[0-9]`/`[a-z]` cells on the all-digit/all-letter
  subjects, plus `\w`/`.`/wide-class cells on dense text (46 cells with small
  sets). Those are the cells whose A0-vs-A1 reading decides the decline.
- **VM hybrids.** Mostly 1 use per prefilter call. `loglines/level-context` (31)
  and `wild-logparse-syslogbase-expanded` (7,669) carry state across rejected
  candidates.

Uses per activation is therefore known for every cell, and you need not count it.
Please report density alongside the timings as asked.

## 8. Standing questions (docs/design/CLAUDE.md)

1. **Regime.** These are counts, deterministic per (artifact, subject). The only
   regime split that matters is the one reported: per-call vs find-all, and the
   state level vs the pass. Box, compiler and libc do not move them, except that
   a give-up (frames, steps) can change where a find-all stops, and the bench's
   give-up cells are the same.
2. **Independent control.** The oracle is libpcre2 through the bench's
   expectations (independent of pcrec). The answer identity is plain vs
   instrumented. The monotone/hit/activation bounds are computed from the subject
   bytes and the parsed table, not from the counter's code. The planted copy
   fires on all 11 named cells. The population is counted (704 jobs, 270 with
   sites).
3. **What moves when data is regenerated.** Nothing emitted. A re-run at a newer
   pcrec or bench pin re-derives every table; the `abi`, the stamps and the
   artifacts are untouched.

## Appendix A: named cells, per subject (state-lifetime level)

| cell | kit | site | S | regime | subject | density (ppm) | matches | activations | uses/act p10 / median / p90 (max) | >=2 / >=4 / >=16 | zero | hits/match | band |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| utf8/alt-distinct-lead | adl | dfa-pf in rx_search | {63,D0,E6} | search-short | 91 short subjects (pooled) | - | - | 91 | 1 / 1 / 2 (8) | 0.16 / 0.08 / 0.00 | 0.00 | - | BELOW |
| utf8/alt-distinct-lead | adl | | | find-all | t-64k (65536 B) | 124054 | 24 | 25 | 22 / 139 / 729 (1180) | 1.00 / 1.00 / 0.96 | 0.00 | 336.708 | ABOVE; pass = 8082 uses |
| utf8/alt-distinct-lead | adl | | | find-all | t-256k (262144 B) | 123390 | 73 | 74 | 14 / 287 / 1046 (2111) | 0.96 / 0.92 / 0.89 | 0.00 | 440.274 | ABOVE; pass = 32141 uses |
| utf8/alt-distinct-lead | adl | | | find-all | t-1m (1048576 B) | 122284 | 434 | 435 | 21 / 219 / 628 (1815) | 0.99 / 0.96 / 0.91 | 0.00 | 293.560 | ABOVE; pass = 127406 uses |
| utf8/alt-distinct-lead | adl | | | find-all | t-64k-lat (65536 B) | 24597 | 42 | 43 | 9 / 31 / 69 (134) | 1.00 / 0.98 / 0.77 | 0.00 | 38.381 | ABOVE; pass = 1613 uses |
| utf8/alt-distinct-lead | adl | | | find-all | t-64k-cyr (65536 B) | 309433 | 0 | 1 | 20280 / 20280 / 20280 (20280) | 1.00 / 1.00 / 1.00 | 0.00 | - | ABOVE; pass = 20280 uses |
| utf8/alt-distinct-lead | adl | | | find-all | t-64k-cjk (65536 B) | 53070 | 65 | 66 | 6 / 46 / 110 (154) | 0.98 / 0.94 / 0.82 | 0.00 | 51.523 | ABOVE; pass = 3350 uses |
| utf8/alt-distinct-lead | adl | | | find-all | t-64k-asc (65536 B) | 37933 | 0 | 1 | 2398 / 2398 / 2398 (2398) | 1.00 / 1.00 / 1.00 | 0.00 | - | ABOVE; pass = 2398 uses |
| utf8/ci-sigma | sig | dfa-pf in rx_search | {CE,CF} | search-short | 91 short subjects (pooled) | - | - | 91 | 1 / 1 / 1 (5) | 0.05 / 0.03 / 0.00 | 0.00 | - | BELOW |
| utf8/ci-sigma | sig | | | find-all | t-64k (65536 B) | 0 | 0 | 1 | 1 / 1 / 1 (1) | 0.00 / 0.00 / 0.00 | 0.00 | - | BELOW; pass = 1 uses |
| utf8/ci-sigma | sig | | | find-all | t-256k (262144 B) | 0 | 0 | 1 | 1 / 1 / 1 (1) | 0.00 / 0.00 / 0.00 | 0.00 | - | BELOW; pass = 1 uses |
| utf8/ci-sigma | sig | | | find-all | t-1m (1048576 B) | 0 | 0 | 1 | 1 / 1 / 1 (1) | 0.00 / 0.00 / 0.00 | 0.00 | - | BELOW; pass = 1 uses |
| utf8/ci-sigma | sig | | | find-all | t-64k-lat (65536 B) | 0 | 0 | 1 | 1 / 1 / 1 (1) | 0.00 / 0.00 / 0.00 | 0.00 | - | BELOW; pass = 1 uses |
| utf8/ci-sigma | sig | | | find-all | t-64k-cyr (65536 B) | 0 | 0 | 1 | 1 / 1 / 1 (1) | 0.00 / 0.00 / 0.00 | 0.00 | - | BELOW; pass = 1 uses |
| utf8/ci-sigma | sig | | | find-all | t-64k-cjk (65536 B) | 0 | 0 | 1 | 1 / 1 / 1 (1) | 0.00 / 0.00 / 0.00 | 0.00 | - | BELOW; pass = 1 uses |
| utf8/ci-sigma | sig | | | find-all | t-64k-asc (65536 B) | 0 | 0 | 1 | 1 / 1 / 1 (1) | 0.00 / 0.00 / 0.00 | 0.00 | - | BELOW; pass = 1 uses |
| utf8/ci-kelvin | kel | dfa-pf in rx_search | {4B,6B,E2} | search-short | 91 short subjects (pooled) | - | - | 91 | 1 / 1 / 1 (1) | 0.00 / 0.00 / 0.00 | 0.00 | - | BELOW |
| utf8/ci-kelvin | kel | | | find-all | t-64k (65536 B) | 3220 | 164 | 165 | 1 / 1 / 2 (4) | 0.23 / 0.02 / 0.00 | 0.00 | 1.287 | BELOW; pass = 212 uses |
| utf8/ci-kelvin | kel | | | find-all | t-256k (262144 B) | 3548 | 755 | 756 | 1 / 1 / 2 (5) | 0.19 / 0.01 / 0.00 | 0.00 | 1.232 | BELOW; pass = 931 uses |
| utf8/ci-kelvin | kel | | | find-all | t-1m (1048576 B) | 3612 | 3031 | 3032 | 1 / 1 / 2 (6) | 0.20 / 0.01 / 0.00 | 0.00 | 1.249 | BELOW; pass = 3788 uses |
| utf8/ci-kelvin | kel | | | find-all | t-64k-lat (65536 B) | 2228 | 146 | 147 | 1 / 1 / 1 (1) | 0.00 / 0.00 / 0.00 | 0.00 | 1.000 | BELOW; pass = 147 uses |
| utf8/ci-kelvin | kel | | | find-all | t-64k-cyr (65536 B) | 1465 | 0 | 1 | 97 / 97 / 97 (97) | 1.00 / 1.00 / 1.00 | 0.00 | - | ABOVE; pass = 97 uses |
| utf8/ci-kelvin | kel | | | find-all | t-64k-cjk (65536 B) | 3052 | 200 | 201 | 1 / 1 / 1 (1) | 0.00 / 0.00 / 0.00 | 0.00 | 1.000 | BELOW; pass = 201 uses |
| utf8/ci-kelvin | kel | | | find-all | t-64k-asc (65536 B) | 7050 | 462 | 463 | 1 / 1 / 1 (1) | 0.00 / 0.00 / 0.00 | 0.00 | 1.000 | BELOW; pass = 463 uses |
| utf8/ci-turkish-i | tki | dfa-pf in rx_search | {49,69} | search-short | 91 short subjects (pooled) | - | - | 91 | 1 / 1 / 1 (1) | 0.00 / 0.00 / 0.00 | 0.00 | - | BELOW |
| utf8/ci-turkish-i | tki | | | find-all | t-64k (65536 B) | 25177 | 1650 | 1651 | 1 / 1 / 1 (1) | 0.00 / 0.00 / 0.00 | 0.00 | 1.000 | BELOW; pass = 1651 uses |
| utf8/ci-turkish-i | tki | | | find-all | t-256k (262144 B) | 24807 | 6503 | 6504 | 1 / 1 / 1 (1) | 0.00 / 0.00 / 0.00 | 0.00 | 1.000 | BELOW; pass = 6504 uses |
| utf8/ci-turkish-i | tki | | | find-all | t-1m (1048576 B) | 25133 | 26354 | 26355 | 1 / 1 / 1 (1) | 0.00 / 0.00 / 0.00 | 0.00 | 1.000 | BELOW; pass = 26355 uses |
| utf8/ci-turkish-i | tki | | | find-all | t-64k-lat (65536 B) | 46005 | 3015 | 3016 | 1 / 1 / 1 (1) | 0.00 / 0.00 / 0.00 | 0.00 | 1.000 | BELOW; pass = 3016 uses |
| utf8/ci-turkish-i | tki | | | find-all | t-64k-cyr (65536 B) | 0 | 0 | 1 | 1 / 1 / 1 (1) | 0.00 / 0.00 / 0.00 | 0.00 | - | BELOW; pass = 1 uses |
| utf8/ci-turkish-i | tki | | | find-all | t-64k-cjk (65536 B) | 4410 | 289 | 290 | 1 / 1 / 1 (1) | 0.00 / 0.00 / 0.00 | 0.00 | 1.000 | BELOW; pass = 290 uses |
| utf8/ci-turkish-i | tki | | | find-all | t-64k-asc (65536 B) | 56870 | 3727 | 3728 | 1 / 1 / 1 (1) | 0.00 / 0.00 / 0.00 | 0.00 | 1.000 | BELOW; pass = 3728 uses |
| syntax/alt-nested | alt2 | dfa-pf in rx_search | {63,64} | search-short | 42 short subjects (pooled) | - | - | 42 | 1 / 1 / 3 (8) | 0.40 / 0.07 / 0.00 | 0.00 | - | BELOW |
| syntax/alt-nested | alt2 | | | find-all | t-64k (65536 B) | 70038 | 521 | 522 | 1 / 6 / 20 (78) | 0.86 / 0.66 / 0.16 | 0.00 | 8.601 | ABOVE; pass = 4481 uses |
| syntax/alt-nested | alt2 | | | find-all | t-256k (262144 B) | 69405 | 2260 | 2261 | 1 / 6 / 17 (53) | 0.85 / 0.64 / 0.13 | 0.00 | 7.865 | ABOVE; pass = 17777 uses |
| syntax/alt-nested | alt2 | | | find-all | t-1m (1048576 B) | 69790 | 8611 | 8612 | 1 / 6 / 19 (70) | 0.86 / 0.65 / 0.15 | 0.00 | 8.283 | ABOVE; pass = 71325 uses |
| syntax/alt-two | alt2r | dfa-pf in rx_search | {63,64} | search-short | 42 short subjects (pooled) | - | - | 42 | 1 / 1 / 3 (8) | 0.40 / 0.07 / 0.00 | 0.00 | - | BELOW |
| syntax/alt-two | alt2r | | | find-all | t-64k (65536 B) | 70038 | 521 | 522 | 1 / 6 / 20 (82) | 0.86 / 0.67 / 0.17 | 0.00 | 8.810 | ABOVE; pass = 4590 uses |
| syntax/alt-two | alt2r | | | find-all | t-256k (262144 B) | 69405 | 2260 | 2261 | 1 / 6 / 18 (55) | 0.85 / 0.64 / 0.14 | 0.00 | 8.050 | ABOVE; pass = 18195 uses |
| syntax/alt-two | alt2r | | | find-all | t-1m (1048576 B) | 69790 | 8611 | 8612 | 1 / 6 / 20 (72) | 0.86 / 0.65 / 0.16 | 0.00 | 8.498 | ABOVE; pass = 73181 uses |
| capability/high-byte-run | hbr | dfa-pf in rx_search | {80..FF (128)} | search-short | 75 short subjects (pooled) | - | - | 75 | 1 / 1 / 1 (2) | 0.03 / 0.00 / 0.00 | 0.00 | - | BELOW |
| capability/high-byte-run | hbr | | | find-all | t-64k (65536 B) | 0 | 0 | 1 | 1 / 1 / 1 (1) | 0.00 / 0.00 / 0.00 | 0.00 | - | BELOW; pass = 1 uses |
| capability/high-byte-run | hbr | | | find-all | t-256k (262144 B) | 0 | 0 | 1 | 1 / 1 / 1 (1) | 0.00 / 0.00 / 0.00 | 0.00 | - | BELOW; pass = 1 uses |
| capability/high-byte-run | hbr | | | find-all | t-1m (1048576 B) | 0 | 0 | 1 | 1 / 1 / 1 (1) | 0.00 / 0.00 / 0.00 | 0.00 | - | BELOW; pass = 1 uses |
| capability/high-byte-run | hbr | | | find-all | t-evil-match-60k (61440 B) | 0 | 0 | 1 | 1 / 1 / 1 (1) | 0.00 / 0.00 / 0.00 | 0.00 | - | BELOW; pass = 1 uses |
| capability/high-byte-run | hbr | | | find-all | t-evil-nearmiss-16k (16385 B) | 0 | 0 | 1 | 1 / 1 / 1 (1) | 0.00 / 0.00 / 0.00 | 0.00 | - | BELOW; pass = 1 uses |
| capability/high-byte-run | hbr | | | find-all | t-trim-match-60k (61440 B) | 0 | 0 | 1 | 1 / 1 / 1 (1) | 0.00 / 0.00 / 0.00 | 0.00 | - | BELOW; pass = 1 uses |
| capability/high-byte-run | hbr | | | find-all | t-trim-nearmiss-16k (16385 B) | 0 | 0 | 1 | 1 / 1 / 1 (1) | 0.00 / 0.00 / 0.00 | 0.00 | - | BELOW; pass = 1 uses |
| capability/high-byte-run | hbr | | | find-all | t-mixed-runs-4k (4096 B) | 0 | 0 | 1 | 1 / 1 / 1 (1) | 0.00 / 0.00 / 0.00 | 0.00 | - | BELOW; pass = 1 uses |
| capability/high-byte-run | hbr | | | find-all | t-tail-digits-1m (1048522 B) | 0 | 0 | 1 | 1 / 1 / 1 (1) | 0.00 / 0.00 / 0.00 | 0.00 | - | BELOW; pass = 1 uses |
| capability/high-byte-run | hbr | | | find-all | t-tail-txt-1m (1048527 B) | 0 | 0 | 1 | 1 / 1 / 1 (1) | 0.00 / 0.00 / 0.00 | 0.00 | - | BELOW; pass = 1 uses |
| capability/high-byte-run | hbr | | | find-all | t-tail-space-1m (1048522 B) | 0 | 0 | 1 | 1 / 1 / 1 (1) | 0.00 / 0.00 / 0.00 | 0.00 | - | BELOW; pass = 1 uses |
| capability/utf8-lead-no-cont | u8l | dfa-pf bounded in rx_search | {C2..DF (30)} | search-short | 75 short subjects (pooled) | - | - | 75 | 2 / 2 / 2 (2) | 0.99 / 0.00 / 0.00 | 0.00 | - | IN-BRACKET |
| capability/utf8-lead-no-cont | u8l | | | find-all | t-64k (65536 B) | 0 | 0 | 1 | 2 / 2 / 2 (2) | 1.00 / 0.00 / 0.00 | 0.00 | - | IN-BRACKET; pass = 2 uses |
| capability/utf8-lead-no-cont | u8l | | | find-all | t-256k (262144 B) | 0 | 0 | 1 | 2 / 2 / 2 (2) | 1.00 / 0.00 / 0.00 | 0.00 | - | IN-BRACKET; pass = 2 uses |
| capability/utf8-lead-no-cont | u8l | | | find-all | t-1m (1048576 B) | 0 | 0 | 1 | 2 / 2 / 2 (2) | 1.00 / 0.00 / 0.00 | 0.00 | - | IN-BRACKET; pass = 2 uses |
| capability/utf8-lead-no-cont | u8l | | | find-all | t-evil-match-60k (61440 B) | 0 | 0 | 1 | 2 / 2 / 2 (2) | 1.00 / 0.00 / 0.00 | 0.00 | - | IN-BRACKET; pass = 2 uses |
| capability/utf8-lead-no-cont | u8l | | | find-all | t-evil-nearmiss-16k (16385 B) | 0 | 0 | 1 | 2 / 2 / 2 (2) | 1.00 / 0.00 / 0.00 | 0.00 | - | IN-BRACKET; pass = 2 uses |
| capability/utf8-lead-no-cont | u8l | | | find-all | t-trim-match-60k (61440 B) | 0 | 0 | 1 | 2 / 2 / 2 (2) | 1.00 / 0.00 / 0.00 | 0.00 | - | IN-BRACKET; pass = 2 uses |
| capability/utf8-lead-no-cont | u8l | | | find-all | t-trim-nearmiss-16k (16385 B) | 0 | 0 | 1 | 2 / 2 / 2 (2) | 1.00 / 0.00 / 0.00 | 0.00 | - | IN-BRACKET; pass = 2 uses |
| capability/utf8-lead-no-cont | u8l | | | find-all | t-mixed-runs-4k (4096 B) | 0 | 0 | 1 | 2 / 2 / 2 (2) | 1.00 / 0.00 / 0.00 | 0.00 | - | IN-BRACKET; pass = 2 uses |
| capability/utf8-lead-no-cont | u8l | | | find-all | t-tail-digits-1m (1048522 B) | 0 | 0 | 1 | 2 / 2 / 2 (2) | 1.00 / 0.00 / 0.00 | 0.00 | - | IN-BRACKET; pass = 2 uses |
| capability/utf8-lead-no-cont | u8l | | | find-all | t-tail-txt-1m (1048527 B) | 0 | 0 | 1 | 2 / 2 / 2 (2) | 1.00 / 0.00 / 0.00 | 0.00 | - | IN-BRACKET; pass = 2 uses |
| capability/utf8-lead-no-cont | u8l | | | find-all | t-tail-space-1m (1048522 B) | 0 | 0 | 1 | 2 / 2 / 2 (2) | 1.00 / 0.00 / 0.00 | 0.00 | - | IN-BRACKET; pass = 2 uses |
| capability/quoted-delim-match | qdm | vm-hat in rx_search_run | {22,27} | search-short | 75 short subjects (pooled) | - | - | 75 | 1 / 1 / 1 (2) | 0.01 / 0.00 / 0.00 | 0.00 | - | BELOW |
| capability/quoted-delim-match | qdm | | | find-all | t-64k (65536 B) | 5432 | 178 | 179 | 1 / 1 / 1 (1) | 0.00 / 0.00 / 0.00 | 0.00 | 1.000 | BELOW; pass = 179 uses |
| capability/quoted-delim-match | qdm | | | find-all | t-256k (262144 B) | 5424 | 711 | 712 | 1 / 1 / 1 (1) | 0.00 / 0.00 / 0.00 | 0.00 | 1.000 | BELOW; pass = 712 uses |
| capability/quoted-delim-match | qdm | | | find-all | t-1m (1048576 B) | 5674 | 2975 | 2976 | 1 / 1 / 1 (1) | 0.00 / 0.00 / 0.00 | 0.00 | 1.000 | BELOW; pass = 2976 uses |
| capability/quoted-delim-match | qdm | | | find-all | t-evil-match-60k (61440 B) | 0 | 0 | 1 | 1 / 1 / 1 (1) | 0.00 / 0.00 / 0.00 | 0.00 | - | BELOW; pass = 1 uses |
| capability/quoted-delim-match | qdm | | | find-all | t-evil-nearmiss-16k (16385 B) | 0 | 0 | 1 | 1 / 1 / 1 (1) | 0.00 / 0.00 / 0.00 | 0.00 | - | BELOW; pass = 1 uses |
| capability/quoted-delim-match | qdm | | | find-all | t-trim-match-60k (61440 B) | 0 | 0 | 1 | 1 / 1 / 1 (1) | 0.00 / 0.00 / 0.00 | 0.00 | - | BELOW; pass = 1 uses |
| capability/quoted-delim-match | qdm | | | find-all | t-trim-nearmiss-16k (16385 B) | 0 | 0 | 1 | 1 / 1 / 1 (1) | 0.00 / 0.00 / 0.00 | 0.00 | - | BELOW; pass = 1 uses |
| capability/quoted-delim-match | qdm | | | find-all | t-mixed-runs-4k (4096 B) | 0 | 0 | 1 | 1 / 1 / 1 (1) | 0.00 / 0.00 / 0.00 | 0.00 | - | BELOW; pass = 1 uses |
| capability/quoted-delim-match | qdm | | | find-all | t-tail-digits-1m (1048522 B) | 0 | 0 | 1 | 1 / 1 / 1 (1) | 0.00 / 0.00 / 0.00 | 0.00 | - | BELOW; pass = 1 uses |
| capability/quoted-delim-match | qdm | | | find-all | t-tail-txt-1m (1048527 B) | 0 | 0 | 1 | 1 / 1 / 1 (1) | 0.00 / 0.00 / 0.00 | 0.00 | - | BELOW; pass = 1 uses |
| capability/quoted-delim-match | qdm | | | find-all | t-tail-space-1m (1048522 B) | 0 | 0 | 1 | 1 / 1 / 1 (1) | 0.00 / 0.00 / 0.00 | 0.00 | - | BELOW; pass = 1 uses |
| syntax/bak-k-named | bkn | vm-hat in rx_search_run | {3C} | search-short | 42 short subjects (pooled) | - | - | 42 | 0 / 0 / 0 (1) | 0.00 / 0.00 / 0.00 | 0.95 | - | BELOW |
| syntax/bak-k-named | bkn | | | find-all | t-64k (65536 B) | 8484 | 250 | 251 | 1 / 1 / 1 (5) | 0.10 / 0.01 / 0.00 | 0.00 | 1.224 | BELOW; pass = 306 uses |
| syntax/bak-k-named | bkn | | | find-all | t-256k (262144 B) | 8232 | 941 | 942 | 1 / 1 / 3 (9) | 0.12 / 0.02 / 0.00 | 0.00 | 1.293 | BELOW; pass = 1217 uses |
| syntax/bak-k-named | bkn | | | find-all | t-1m (1048576 B) | 9165 | 4165 | 4166 | 1 / 1 / 3 (9) | 0.13 / 0.02 / 0.00 | 0.00 | 1.307 | BELOW; pass = 5445 uses |
| capability/balanced-parens-rec | bpr | vm-hat in rx_search_run | {28} | search-short | 75 short subjects (pooled) | - | - | 75 | 0 / 0 / 0 (1) | 0.00 / 0.00 / 0.00 | 0.96 | - | BELOW |
| capability/balanced-parens-rec | bpr | | | find-all | t-64k (65536 B) | 5234 | 343 | 344 | 1 / 1 / 1 (1) | 0.00 / 0.00 / 0.00 | 0.00 | 1.000 | BELOW; pass = 343 uses |
| capability/balanced-parens-rec | bpr | | | find-all | t-256k (262144 B) | 5558 | 1457 | 1458 | 1 / 1 / 1 (1) | 0.00 / 0.00 / 0.00 | 0.00 | 1.000 | BELOW; pass = 1457 uses |
| capability/balanced-parens-rec | bpr | | | find-all | t-1m (1048576 B) | 5780 | 6061 | 6062 | 1 / 1 / 1 (1) | 0.00 / 0.00 / 0.00 | 0.00 | 1.000 | BELOW; pass = 6061 uses |
| capability/balanced-parens-rec | bpr | | | find-all | t-evil-match-60k (61440 B) | 0 | 0 | 1 | 0 / 0 / 0 (0) | 0.00 / 0.00 / 0.00 | 1.00 | - | BELOW; pass = 0 uses |
| capability/balanced-parens-rec | bpr | | | find-all | t-evil-nearmiss-16k (16385 B) | 0 | 0 | 1 | 0 / 0 / 0 (0) | 0.00 / 0.00 / 0.00 | 1.00 | - | BELOW; pass = 0 uses |
| capability/balanced-parens-rec | bpr | | | find-all | t-trim-match-60k (61440 B) | 0 | 0 | 1 | 0 / 0 / 0 (0) | 0.00 / 0.00 / 0.00 | 1.00 | - | BELOW; pass = 0 uses |
| capability/balanced-parens-rec | bpr | | | find-all | t-trim-nearmiss-16k (16385 B) | 0 | 0 | 1 | 0 / 0 / 0 (0) | 0.00 / 0.00 / 0.00 | 1.00 | - | BELOW; pass = 0 uses |
| capability/balanced-parens-rec | bpr | | | find-all | t-mixed-runs-4k (4096 B) | 0 | 0 | 1 | 0 / 0 / 0 (0) | 0.00 / 0.00 / 0.00 | 1.00 | - | BELOW; pass = 0 uses |
| capability/balanced-parens-rec | bpr | | | find-all | t-tail-digits-1m (1048522 B) | 0 | 0 | 1 | 0 / 0 / 0 (0) | 0.00 / 0.00 / 0.00 | 1.00 | - | BELOW; pass = 0 uses |
| capability/balanced-parens-rec | bpr | | | find-all | t-tail-txt-1m (1048527 B) | 0 | 0 | 1 | 0 / 0 / 0 (0) | 0.00 / 0.00 / 0.00 | 1.00 | - | BELOW; pass = 0 uses |
| capability/balanced-parens-rec | bpr | | | find-all | t-tail-space-1m (1048522 B) | 0 | 0 | 1 | 0 / 0 / 0 (0) | 0.00 / 0.00 / 0.00 | 1.00 | - | BELOW; pass = 0 uses |
