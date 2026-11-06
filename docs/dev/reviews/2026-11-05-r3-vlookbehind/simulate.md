# SIM lens findings (crit-simulate), design `docs/design/vlookbehind.md` rev 0 @ 9f3aaaee1

Harness: `simulate/sim.c` (gcc -lpcre2-8). It implements §5.1 FROM THE TEXT: per top-level branch in written
order, candidate starts farthest first over [lo,hi] clamped at subject start 0 (UTF: by characters), the branch body
run forward at each candidate with libpcre2 as the forward VM, `(?:BODY)(?C1)` PCRE2_ANCHORED over the FULL
subject, callout fails unless position == cursor (the end-check, backtracking into the body); atomic arm takes the
first path, non-atomic arm evaluates the FOLLOW inside the callout (so it retries into the body and then shorter
candidates); negative arm = no branch/candidate ends at the cursor. Output compared with libpcre2 on the whole pattern
`(?<=LB)F` / `(?<!LB)x` / `(?<*LB)F`, F = `x` or `\1`: match span AND every group. Also checks accept/refuse verdict
(model rule: refuse iff some branch lo<hi and some hi>255) and `max_lookbehind` vs the model's hi.
CAN model: all of the above, positive/negative/non-atomic, start offsets 1..5, byte and UTF-8, captures, retry into
body. CANNOT model: the follow beyond `x`/`\1` (non-atomic retry is exercised only through those), backrefs INSIDE
the body (stage 2), calls in the body, lookbehind inside a larger pattern with a non-empty prefix (every match
starts at the cursor), global iteration (first match only per subject/offset), the real emitted C.
Self-check (the harness can fail): `SAB=1` (candidates shortest first) -> 96962 diffs of 962760 cases.

## Findings

### SIM-1 (doc / gate, CONFIRMED, small effort): gate 1's "0 differences" is not reachable over UTF x startpos>0 x varying bodies that contain `\b` or a nested lookbehind
- Design §6 stage 1 gate 1 ("0 differences", cells include `startpos > 0`, byte and UTF-8) and §2's "Context before the
  start is read" / "Before startpos" rows.
- Repro (libpcre2 10.46, `simulate/sp`): `sp '(?<=\ba{1,2})x' baax 3 u` -> `[3-4]`; the same with byte mode, or from offset 0,
  -> `nomatch`. Fixed-width twin (already the case today): `sp '(?<=\ba)x' bax 2 u` -> `[2-3]`, byte -> nomatch.
  Nested: `sp '(?<=(?<=a)b{1,2})x' abbx 3 u` -> nomatch, byte -> `[3-4]`.
- Cause (documented, not a new fact): `docs/design/utf_valid_design.md` (@9f077685a, the "[uvbuild, 2026-09-30, MEASURED]" paragraph):
  under PCRE2_UTF the backward reads stop at `startpos - max_lookbehind`, so a `\b` or inner lookbehind at the edge of
  the window sees no earlier character; pcrec reads the real bytes. The simulation reproduces the SPEC rule and
  therefore disagrees with libpcre2 exactly there: 7776 diffs / 19.7M cases at offset 3, 5012 at offset 4, 0 at offset >=5 (and 0 at offsets 1,2,3 in byte mode); every
  differing pattern contains `\b` or a nested `(?<`; no other class differs.
- Why it matters for THIS design: a varying body widens the exposed set (the window edge is hit by any candidate
  at distance hi whose `\b` reads hi+1), and gate 1 as written would either fail or be quietly narrowed. The design does not
  name the class.
- Suggest: gate 1 names the exclusion (UTF x startpos>0 x {`\b`, `\B`, `\A`-like context, nested lookbehind} cells are
  recorded as the D133 known divergence, citing utf_valid_design.md), and keeps those cells in the population as
  expected-divergent so the count stays honest. Severity: doc. Blast radius: the build lane's gate.

### SIM-2 (test coverage, SUSPECTED, small effort): the end-check witnesses never exercise a greedy QUANTIFIER at the body's tail
- §7 W2/W3 and §5.3. W3's witness backtracks into an alternation only.
- Hazard found while building the harness: libpcre2 itself auto-possessified `(a{1,2})` before my end-check callout and the
  simulation went wrong (96k false diffs) until `PCRE2_NO_AUTO_POSSESS`. Any pcrec pass or emitter rung that treats
  "the body ends" as "the pattern ends" (possessify, counted/optional-phase rungs "follow cannot fit ends the loop
  without a frame", emit_vm.c ~5449) would do the same to a varying body's trailing quantifier. `src/opt/possessify.c`
  does NOT enter `A_LOOK` (its comment at the `case A_LOOK` arm near line 1856, "possessify cannot narrow ANY lookaround body"), so that pass holds; the emitter's rungs were not
  traced by me.
- Witnesses that need backtracking into a greedy quantifier (oracle, `oracle_probe m`): `(?<=a{1,2})a` on `aaa` -> (1,2) then (2,3);
  `(?<!a{1,2})a` on `aaa` -> (0,1); `(?<=(?:ab){1,2})a` on `ababa` -> (2,3),(4,5). A body that does not backtrack
  into the quantifier gives (2,3) first. W3's alternation witness would stay green under a sabotage that only
  possessifies the tail quantifier. Suggest adding the first row as W3b. Severity: test coverage.

## PROBED-AND-HELD

- Rule simulation vs libpcre2, WHOLE answers (span + every group), byte mode and UTF-8: the 59-body pool (literal alternation of different
  lengths, bounded `a{m,n}`, nested quantifier, capture groups incl. nested/duplicated-by-branch numbering, atomic
  `(?>..)`/possessive `{..}+`/`?+`, nested lookahead `(?=..)(?!..)`, nested lookbehind, `\b`/`^` inside, empty alternation,
  2-byte character bodies with byte widths vs character widths). Populations (patterns x subjects = cases; subjects
  are all strings over {a,b,x,space} up to length 5/6 plus all over {a,b,x,e-acute} up to length 4/5):
  - run_byte.out / run_utf.out: 9422 patterns x 1706 subjects = 16,073,932 cases each mode, 0 diffs.
  - run2_b.out / run2_u.out: 34,422 patterns x 6826 subjects = 234,964,572 cases each mode, 0 diffs.
  - start offsets 1,2,3 each mode (12,266 patterns x 1706): byte 0 diffs (20.9M, 20.8M, 20.5M cases); UTF 0 diffs at offsets 1 and 2, 7776 at 3, 5012 at 4, 0 at 5 (all SIM-1 class).
  - Total about 570M comparisons. Forms: 1 branch (every pool body, 59), 2 branches (random pairs), 3 branches (random triples);
    polarities `(?<=`, `(?<!`, non-atomic `(?<*`; follow `x` and `\1` (when the pool body has group 1). Mispicks: none. Branch order,
    farthest-first, clamp at 0, end-check with body backtracking, non-atomic retry (shorter candidates and body paths), neg-arm
    unset captures all agree with libpcre2.
- Accept/refuse verdicts over the same populations (34,422 + 9,422 + 12,266 patterns x modes): 0 patterns refused by libpcre2 and accepted by the rule, none the other way
  (population is within 255). `max_lookbehind` equals the model's widest hi in all but the pure-`\b` bodies
  (libpcre2 reports 1 for a body that is only `\b`; spec match_api 9.4 P2 already says `\b` counts 1, and nesting is a max, so held).
- Cap boundary, fine sweep (280 patterns x byte and UTF-8 compiles, `cap_byte.out`, `cap_utf.out`): n in 253..257 for `a{1,n}`,
  `a{n}|b{1,2}`, `a{n}|b`, `b{1,2}|a{1,n}`, `a{n}|b{300}`, `a{n}a`, `a{1,n-1}a`, `a{n-1}a?`, `(a|b){n}` (fixed, accepted at 256/257),
  `(?:a?){n}` (varying, refused at 256), nested `(?:a{2}){1,n/2}`, `(?:ab){1,n/2}`, `(?:a|bb){1,n/2}`, `é` forms in both encodings. Rule holds:
  refuse (err 200) iff some branch varies and some branch maximum > 255; `a{255}|b{1,2}` accepted, `a{256}|b{1,2}` refused,
  `a{254}b{1,2}` refused (hi 256), `a{1,254}b` accepted, `a{1,255}b` refused, `a{256}|b` and `a{300}|(?:b|c)` accepted (all fixed),
  `a{300}|(?:b|cc)` refused. Same under `(?<!` and `(?<*`. Unit is bytes in byte mode, characters under UTF: `(?:é){1,127}` accepted
  in both, `(?:é){1,128}` refused in byte mode (256 bytes), accepted in UTF (to 255, refused at 256). So the "characters, per encoding" wording in §5.2 holds; the
  utf8-encoding cap is characters, which pcrec must compute with cwmax in characters.
- Quoted numbers recomputed: bench pattern is `(?<!\bnot\s{1,3}(?:\w{1,12}\s{1,3}){0,3})\bavailable\b` (pcrec-bench `bench/capability/patterns.rxt:1272`):
  lo = 3+1 = 4, hi = 3+3+3*(12+3) = 51, libpcre2 `maxlookbehind=51` in both encodings; candidates 51-4+1 = 48 ("up to 48") ok; the "143967 fixed-width
  branches" text in bench_expansion.txt: 3 + 36 + 36^2 + 36^3... = 1+36+1296+46656 = 47989 and x3 = 143967 ok.
- §8 counts from `population.tsv`: rows sum 37, 27 distinct lines, 1 false positive (`(?<=${v})x`) so 36 real; B-loop yes 30 rows/22 distinct + "deferred path" 2/2 = 32 rows/24 distinct (stage 1),
  + needs-bref-width 4 rows/2 distinct = 36 rows/26 distinct (stage 2); matches population_coverage.txt. ok.
- libpcre2 answers quoted in §2 and §7, 32 rows re-run through `oracle_probe m` (atomic `abbx`, `a{1,2}+a`, `\ba{1,2}` x3, `^a{0,2}` x2, `(?=xy)` x2, `(?<*(a|aaa))c\1`,
  `(?<=(ab)|(b{1,2}))c`, `(?<=(a)|(aa))c`, startpos-free versions, `é{1,2}` UTF, W1-W6, S136 re-aim rows `(?<=bc|d)x`/`(?<!bc|d)x` on `abcx`/`bcax`, W8/W9 compile verdicts):
  all equal the quoted answers.
- §5.5 formula: per position, per branch, (hi-lo+1) candidates, each body run costs at most hi steps -> n * sum (hi-lo+1)*hi; consistent with the harness's own work (no counter-example).

## Questions for a pcre2-reader
None.
