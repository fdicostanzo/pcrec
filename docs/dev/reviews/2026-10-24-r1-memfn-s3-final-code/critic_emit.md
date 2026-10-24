# critic_emit.md — lens emitted-vs-replaced (opus), round memfn-s3-final

SUBJECT cc4f54eb2 (compiler /tmp/claude-1001/crit-memfn-s3-final/subj/pcrec), BASE 0d3765c87
(/tmp/claude-1001/crit-memfn-s3-final/base/pcrec). Scratch: /tmp/claude-1001/crit-memfn-s3-final/emit/.
Arms: BASE; SUBJ (default); OFF = SUBJ `--memfn=no-wf-find`. Library form, `--features all`, unless said.

## Findings

### EMIT-1  PAIR's two memchr streams start fresh on every rx_search call: find-all goes quadratic where BASE was linear
- status: CONFIRMED. Repro: `subj/pcrec -p rx -o ciw.subj.c --features all --pattern '(?i)xq'` (and the BASE
  compiler for the replaced artifact); driver `emit/cnt2.c` = find-all by repeated `rx_search(s,n,from)`, from
  = previous match end, over `"xq"+60 spaces` repeated to SIZE bytes; `perf stat -e instructions:u`.
  Instructions per subject byte, BASE vs SUBJ: 256 KiB 8.2 vs 202; 1 MiB 7.8 vs 796; 4 MiB 7.7 vs 3175
  (BASE linear, SUBJ grows with the subject: quadratic). Same shape for `x[Q%]y` (PAIR widened to two
  unrelated bytes) on `"x%y"+60 spaces` at 1 MiB: BASE 3.09, SUBJ 784 instr/byte.
- severity: speed      - effort: M      - blast radius: every `"cover"` artifact whose stop is PAIR (the E-find
  loop's two streams, window.c:2620, and the B-fn offset-skip function's fn-pair body, ofsskip.c:245/275)
  whenever one of the two bytes is absent or far: caseless 1-letter stops on lower-case text (`(?i)xq`, any
  `(?i)` literal whose rarest position is a letter), `[Q%]`-style stops; through rx_search, rx_search_in and
  the find-all iterator (rx_next/rx_next_n call rx_search).
- where: memfn/src/window.c:2620 (`_ha/_hb/_fr` are locals of one search), memfn/src/ofsskip.c:240-258
  (`ofs_pair_text`; header comment ofsskip.c:~19-27 "searching both streams fresh per call").
- detail: each call re-runs BOTH memchrs; the absent byte's memchr scans to `n` every time, so each call costs
  O(n - from) regardless of how near the match is, and a find-all costs O(n x matches). BASE's fn-pair arm had
  the same property (BASE `(?i)hello` already shows 762 instr/byte on a text with a match every 65 bytes, and
  SUBJ keeps it: 760), but BASE reached it only through the prefix offset-skip row; S3 widens PAIR to ANY
  two-byte stop and makes it the REPORT's search, so artifacts that were linear at BASE (`(?i)xq`: BASE
  "byte-class" prefilter; `x[Q%]y`: BASE "memchr") are now quadratic under the default build. Single-stream
  memchr stops are not affected (the memchr ends at the first hit, which is at most the next match). A
  stream that hit `n` stays a valid fact for any later call over the same subject; the cheapest repairs are
  to bound each stream's memchr by the other stream's hit (search b only in [at, ha)), or to fall back to a
  one-stream/walk form when one member's rate is far below the other's. Realistic shape
  (pre-existing at BASE, kept by SUBJ): `(?i)the` find-all over the 1.8 MB journal LOWER-CASED (`tr A-Z
  a-z`, so no `T`): 968 instr/byte BASE, 967 SUBJ, vs 5.2/4.2 on the original-case text; one fix serves
  both. The SIMD layer escapes it (`-fmemfn-simd` `(?i)xq`, same subject: 2.4 instr/byte SSE2 arm, 2.1 AVX2
  arm: its vrun rungs scan one masked stream), so the default (SIMD-off) build is the one exposed. Not a timing claim: instruction counts only.

### EMIT-2  D-hors drops what a failed verify learned: shift 1 after a mismatch, so a class window costs O(n*w) on runs of w-2..w-1 members
- status: CONFIRMED (instruction counts; adversarial only). Repro: `--pattern '[0-9a-f]{8}'` (D-hors; BASE
  "unanchored" + "byte-class"), find-all driver `emit/cnt.c` over UNIT repeated to 1 MiB, `perf stat -e
  instructions:u`, instr/byte BASE vs SUBJ: `aaaaa-` 17.95 vs 21.45; `aaaaaa-` 16.68 vs 24.61 (SUBJ 1.48x);
  all other shapes tried SUBJ is better (`a-` 37.1 vs 20.6, `aaaaaaa-` 15.5 vs 5.7) and on real text
  (docs/dev/dev_journal.md, 1.8 MB) SUBJ wins everywhere: `[a-z]{6}` 13.9 vs 6.1, `[A-Za-z0-9]{10}` 11.2 vs
  7.7, `[0-9a-f]{8}` 9.9 vs 2.2, `\b[0-9a-f]{8}\b` 12.4 vs 2.3, `[a-z]{3}` 22.2 vs 9.8.
- severity: speed      - effort: S      - blast radius: D-hors cover sites (`[a-z]{6}`, `[0-9a-f]{8}`,
  `[A-Za-z0-9]{10}`, `[0-9a-f]{4}[g-z]{4}` all take it).
- where: memfn/src/window.c (D-hors renderer, `wf_dtable` row; emitted text `... rx_mf1_c += rx_mf1_sh[rx_mf1_b];`
  after the verify).
- detail: the verify tests positions c..c+w-2 left to right and, on failure, shifts by sh[b] (= 1 for a member
  b), so a non-member at c+j is re-discovered by the next j windows (period-7 `aaaaaa-` ~3.5 range tests per
  byte). For a window whose positions share one class (hex8, `[a-z]{6}`), verifying RIGHT to left and, on a
  non-member at c+j, advancing to c+j+1 is safe and makes the loop linear in bytes. Second, smaller: in the
  `!member(b)` branch the emitted `sh[b]` is the constant w for every uniform-class window (table census:
  `[a-z]{6}` = 26x1, 230x6; `[0-9a-f]{8}` = 22x1, 234x8), and after a failed verify it is the constant 1, so
  the 256-byte `rx_mf1_sh` table and its indexed load buy nothing there (the table only carries information
  for mixed windows such as `[0-9a-f]{4}[g-z]{4}`: 20x1, 16x4, 220x8). Real-text counts say D-hors is a net
  win as shipped; this is a worst-case/size note, not a regression on ordinary text.

### EMIT-3  A stop below the candidate re-clamps and re-tests `c >= 1` on every candidate; gcc keeps both
- status: CONFIRMED. Repro: `subj/pcrec -p rx -o lb.subj.c --features all --pattern '(?<=x)foo'`; emitted loop
  `for (;;) { if (rx_mf1_c < 1) rx_mf1_c = 1; { memchr(s + c - 1, 'x', ...); c = hit + 1; } if (!(c + 2 < n))
  break; if (rx_mf1_c >= 1 && rx_w2(...) ...` . `objdump -d` of `gcc -O2` keeps a `test/cmovne/sub/cmovb`
  clamp per iteration and an `add $1; je` wrap test for `c >= 1` (c = hit+1 can only be 0 by wraparound, so
  gcc cannot drop it). Hand-edited copy (`emit/lbx/lbx.c`: clamp hoisted above the loop, `c >= 1 &&`
  deleted) vs SUBJ, find-all instr/byte (`emit/cnt.c`, 1 MiB): `xfox` 31.88 -> 27.88, `xxxx` 53.9 -> 45.9,
  `x foo bar baz` 6.12 -> 5.50 (10-15% of the search's instructions on candidate-dense text).
- severity: speed      - effort: S      - blast radius: every E-find loop whose stop lies below the candidate
  (lookbehind context byte, `\b`-adjacent stops, D1c-served stops).
- where: memfn/src/window.c, E-find loop renderer (the `if (C < k) C = k;` prologue and the `C >= k &&`
  guard in the verify conjunction).
- detail: after the first iteration the candidate is always `hit + k >= k` (and on a miss it only grows), so
  the clamp is needed once, before the loop, and the verify's `C >= k` is implied by the stop's own
  arithmetic; both are emitted inside the loop. Answers unaffected (0 diffs, see PROBED-AND-HELD). Also seen,
  negligible: every E-find text ends `f ? c : n` followed by the entry's `if (scan_position == n) return 0;`,
  a second compare on the success path that the found flag already decided.

### EMIT-4  Set stops route to the byte-at-a-time walk even beside a one-byte memchr stop: real-text losses up to 27x vs BASE
- status: CONFIRMED (instruction counts). Repro: BASE and SUBJ compilers, `--features all`, library form;
  find-all driver `emit/cnt3.c` (repeated rx_search from the previous match end) over the 1.8 MB
  docs/dev/dev_journal.md (`emit/text.txt`); `perf stat -e instructions:u`, instr/byte BASE -> SUBJ:
  `[<>&]x` 0.41 -> 11.07 (27x); `[QXZ]{2}` 6.08 -> 11.07; `[.,;]\d` 6.69 -> 11.20; `[qQ%][jX][k#]` 6.09 ->
  10.07; `[A-Z][a-z]` 7.16 -> 8.52; `[xyz][0-9]` 6.35 -> 8.14. Walk wins only where its set is dense
  (`[A-Z]{3}` 8.67 -> 7.53, `\d{3}` 7.99 -> 7.40). Same answers (match counts equal). The OFF arm is BASE.
- severity: speed      - effort: M      - blast radius: every `"cover"` REPORT site whose least-mass core
  position is a 3+-member set (finder row R7w, the walk), i.e. most class-led short windows; through
  rx_search / rx_search_in / the iterator.
- where: emitted `for (;;) { while (c < n && !(s[c] == 38 || s[c] == 60 || s[c] == 62)) c++; ...`
  (`[<>&]x`); Table A's A-mass row (window_site.md §1, "over the core positions, the least mass") feeding
  Table B's R7w row (memfn/src/finder.c, `FF_WALK`).
- detail: Table A picks the stop by byte mass alone, then Table B renders whatever it got. On `[<>&]x` the
  set {<,>,&} has 503 ppm on this text against `x`'s 4304 ppm, so A picks the set; but the walk spends ~11
  instructions on EVERY byte while BASE's memchr on `x` (BASE `RX_DFA_PREFILTER "offset-set"`, memchr(...,
  120, ...)) spends ~0.4. The design names this as a non-goal ("pricing the stop by its find method ...
  `[MEMFN-PAIRSTOP]`: today Table A ranks by mass alone", window_site.md Non-goals), but Goal 2 ("Not slower
  than DEF beyond the floor (users of the default build)") is ranked above it and S3 makes the cover the
  DEFAULT; §6's bar measures the 581 cells (hex8, file-ext-order, foobar) and job 588's 24 movers, none of
  which (as named) is a set-led REPORT window, so this population is not counted by the bar. Minimum
  repair inside S3's scope: let A-mass decline a multi-member position in favour of a one-member one whose
  mass is within a fixed factor (the memchr/walk per-byte cost ratio), or keep such sites on the OFF arm
  until [MEMFN-PAIRSTOP] lands. Also: these artifacts stamp `RX_REQ_WHY "dominated"` (spec: "the artifact's
  own candidate-start memchr ... already scans a byte at least as rare") while containing no memchr at all
  (the `[<>&]x` SUBJ artifact: `grep -c memchr` = 0, and it stamps `RX_MEMFN_LIBC "none"`) — the
  stamp describes a scan the artifact does not run (§6.3.1¶5a), see EMIT-5.

### EMIT-5  `RX_REQ_WHY "dominated"` (and `_REQ_RUN`'s `@idx`) on cover artifacts name a memchr the artifact does not run
- status: CONFIRMED. Repro: `subj/pcrec -p rx -o t.c --features all --pattern '[<>&]x'`: stamps
  `RX_REQ_BYTE "120"`, `RX_REQ_WHY "dominated"`, `RX_MEMFN_LIBC "none"`; the artifact contains no memchr
  (`grep -c memchr t.c` = 0): its search is the walk over {&,<,>} (EMIT-4). BASE's same artifact did run
  `memchr(..., 120, ...)`. Second shape: `(?<=x)foo` stamps `RX_REQ_RUN "666f6f@0"` (`@0` = `f`) while its
  only memchr scans 120 (`x`, the context byte at -1).
- severity: doc      - effort: S      - blast radius: cover artifacts whose stop is a walk set (REQ_WHY) or
  lies outside the necessary run (REQ_RUN `@idx`); consumers bucketing on REQ_WHY (match_api §6.3.7¶8-9).
- where: docs/spec/match_api.md §6.3.7¶8 value table (`"dominated"`: "the artifact's own candidate-start
  `memchr` (or run-pinned test) already scans a byte at least as rare, or its locator decides presence
  itself (`rev-end`/`empty`)"), ¶7 (`@idx` = "the member the emitted `memchr` scans for"), §6.3.1¶5a ("the
  others never describe a pass the artifact does not run"); producer: the REQ_WHY decision in
  src/gen/emit_dfa.c on the cover path.
- detail: the decline is right (a pre-check in front of a full-subject walk adds work only if the byte is
  absent), but the stated reason is false for a walk stop, and ¶7's `@idx` claim is false once the window
  stop leaves the run. Either widen the `"dominated"` row to "the artifact's own window search (`"cover"`)
  decides presence itself" — the same argument the row already makes for `rev-end`/`empty` — or stamp the
  cover's own reason; and say in ¶7 that on `"cover"` `@idx` is the analysis pick, not a scanned member.

## PROBED-AND-HELD

- **Answers, byte mode, SUBJ vs libpcre2** (driver `emit/drv.c`: every `search_from` 0..n per subject,
  subject in an exact-size malloc under ASan, compare rc + `[start,end)`): 16 hand shapes (literal, caseless,
  `ab[xy]cd`, `q[0-9]z`, `[qQ%][jX][k#]` walk, `x[Q%]y` PAIR widened, `(?<=x)foo`, `\bfoo\b`, `\bfoo`,
  `\b[0-9a-f]{8}\b` and `[0-9a-f]{8}` D-hors, `[abc]xyz[def]`, `[a-c]z[a-c]`, `a.c`, `a\nb`, `(?i)xq`) x 3000
  random subjects = 616k cases, plus 7 planted-alphabet reruns (372k cases, 165k matches): 0 differences, 0
  ASan reports. 90 random fixed-width patterns with `\b`/`\B`/lookbehind/lookahead/`^`/`$`/`(?i)` context
  (61 admitted to `"cover"`), 1.06M cases: 0 differences, 0 ASan reports (no read past `n` or before 0).
- **utf8** (`-e utf8`, oracle PCRE2_UTF): `héllo`, `(?i)héllo`, `\bfoo\b`, `\b[0-9a-f]{8}\b`, `[ñü]z`
  (cover) and `a.c`, `(?<=é)foo`, `x[éa]y`, `(?i)k` (not admitted), BASE and SUBJ, 172k cases per arm: 0 differences.
  The K50 start-position guard text is identical BASE/SUBJ. (My first utf8 run used PCRE2_UCP and showed
  BASE==SUBJ diffs on `\b`; `-e utf8` keeps `\w` ASCII without `(*UCP)` and pcrec rejects UCP `\b` with a
  clean message — driver error, not a finding.)
- **-fmemfn-simd**: SIMD-on minus SIMD-off over the 16 shapes = only `#if`-guarded `__w16`/`__w32` rungs
  and their selector plus the FORMS/GUARDED stamps (ci, ciw); the other 14 identical but for the header
  name. SIMD artifacts `(?i)hello`, `(?i)xq` at SSE2 and `-mavx2`: 493k cases, 0 differences.
- **OFF arm == BASE but abi digits**: `--memfn=no-wf-find` vs BASE, normalised for the abi number and the
  header name, 21 hand shapes + 50 random + 12 shapes x {`-e utf8`, `-fmemfn-simd`, `--emit-main`}: 0
  differing lines.
- **Native (non-REPORT) offset-skip sites have zero byte moves**: SUBJ vs BASE normalised on every
  non-cover artifact (`(?<=ab)cd`, `(foo|bar)baz`, `(ab)(cd)`, `foo(?=bar)`, `[0-9]+abc` + 10 random, 9 of
  them carrying `rx_ofsskip`): identical.
- **Pre-existing entries**: rx_match, rx_match_caps, rx_search_in, rx_match_in, rx_match_caps_in, the
  iterator (rx__enter/rx__step/rx_next/rx_next_n), rx_next_pos, rx_valid_upto, rx_info's other fields:
  byte-identical BASE vs SUBJ on all 21 cover artifacts (only rx_search/rx__find and the scan stamps move).
- **Stamps on cover artifacts vs their contents**: `_DFA_SCAN "cover"`, `_DFA_START`/`.search_form
  "attempt-start"`, `_DFA_PREFILTER(_OFFSETS) "none"`, `_DFA_TABLE` (lb's mixed -> indexed = the anchored
  machine alone, §6.3.4¶8), `_DFA_UNIFORM_FOLDS` (hexr 1 = the anchored next_state fold), `_DFA_SCAN_EDGE`
  (non-"none" exactly where rx_match carries a run view), `_MEMFN_LIBC` (memchr/memcmp inventory),
  `_RUN_WORDS` (counts the overlap/words runs emitted; walk3's 2-byte `memcmp` not counted) — all consistent
  with the spec except EMIT-5.
- **Size**: `gcc -O2` text+rodata smaller on every one of 21 cover artifacts (e.g. lit 3351 -> 2577, uci
  5450 -> 3454, hex8 3112 -> 3074), C text smaller on all.
- **Real-text instruction counts** (1.8 MB journal, find-all): SUBJ <= BASE on 31 of 38 cover patterns
  tried (hex8 9.9 -> 2.2, `\bfoo\b` 1.51 -> 0.86, `(?i)xq` 6.17 -> 0.32, `[a-z]{3}` 22.2 -> 9.8); the
  losses are EMIT-4's walk sites and `\bS3\b` (0.37 -> 0.40, noise-level).
- **Extra work / redundant tests checked and held**: one-stream memchr loops resume at the stop's next
  position (no re-scan), the stop byte is not re-tested in class verifies (walk3, dot, hex8's `c+7`), the
  D-hors probe byte is not re-verified, bounds are tested once per candidate.
- Denylist: no denied file opened. window_site.md rev 3.3 lines 16-18 name review files; not followed.
