# simlit (crit-vlb2, lens simulate-literal) -- findings

Sources in this dir: `simlit.c` (interpreter + libpcre2 10.46 differential; build `gcc -O2 -o simlit simlit.c -lpcre2-8`),
raw outputs `out_{b,u}_{0..4}.txt` (b = byte, u = UTF-8; the digit is the sabotage id, 0 = the design as written).
Command used: `simlit b|u SAB maxlen tstride` (byte: maxlen 6, UTF: maxlen 5, tstride 4); `simlit W ...` evaluates one lookbehind at one cursor and prints the work charge.

## The interpreter (what "literal" means here)
Explicit frame stack (`PUSH` saves target pc, cursor, trail depth; `rx_fail` pops the top frame, rewinds the trail to the
frame's mark, restores cursor and pc). Explicit trail: every `SET` (VK_SET) of a slot, group open/close and the `POS`,
`MARK`, `D_i` slots records the old value. Ops are exactly §5.1's lines: `BLT lo` guard (not emitted at lo==0),
`D_i = min(hi, scan_position)`, `PUSH L_adv` BEFORE the back-step, `CHARGE D_i`, `back_step(D_i)` with sentinel -> `rx_fail`,
body, end-check, `L_adv`: `if D_i==lo goto next` / `D_i--` / `goto L_try`. `one-length` row per the §5.1b table (no slot,
guard `< k`, push of `L_b(i+1)` skipped on the last branch, `RX_R_INTERNAL` on the negative arm's end-check, decline on positive).
Body engine: a backtracking VM compiled from a regex AST (literals, classes, `.`, `\b`, alternation, capture/non-capture groups,
`?`, `{n,m}`, lazy `{n,m}?`), counted loops unrolled into PUSH chains. UTF mode decodes 2-byte `é` for matching and back-stepping.

Wiring the design leaves unstated, and where I took it from (all `src/gen/emit_vm.c` in the review tree, `vm_look` ~7425 and
`vm_look_behind_branch` ~7117):
- Entry: `SET MARK = resume_depth` only for atomic or negative; `SET POS = scan_position` always; negative pushes `negok` AFTER the
  mark and BEFORE the first branch, so it sits BELOW every `L_adv` frame. (vm_look)
- Branch exhaustion of the LAST branch = `rx_fail`, which for the negative arm pops `negok` = assertion holds. (header, "THE LAST BRANCH")
- Common `L_ok`: negative = `CUT MARK; rx_fail`; atomic positive = `CUT MARK; RESTORE POS`; non-atomic = `RESTORE POS` only. (vm_look okl blocks)
- The sentinel exit goes to `rx_fail` (pops the frame just pushed). (note 2)
- One-length branch: guard, push `L_b(i+1)` (non-last), charge k, back-step, sentinel, body, end-check. (vm_look_behind_branch)
- `CUT` is an assignment of the frame count to the mark and does not rewind the trail. (note 2/vm_cut)

## Findings

SIMLIT-1 -- NO divergence found; the design's §5.1 / §5.1b, read literally, matches libpcre2 10.46 on the whole population. (CONFIRMED absence)
- Severity: none. Bears on owner Q1 A and B: the `range` row alone (B) was exercised on every branch whose width varies, and the
  `one-length` row (A) on every fixed branch in the same patterns (the pool mixes them in every order, 1-3 branches).
- Population (byte): 8,592 patterns accepted (0 rejected by libpcre2) of which 8,466 have >= 1 varying branch, x 1,093 subjects
  (alphabet a,b,c, length 0-6, exhaustive) x start offsets 0-3 = 37,409,568 cases, 16,140,897 of them matches. DIFFS = 0.
- Population (UTF-8): same patterns, alphabet a,b,c,é (2-byte), length 0-5 (1,365 subjects, exhaustive), start offsets 0-3 at character
  boundaries = 39,274,032 cases, 14,250,964 matches. DIFFS excluding D142's class = 0. The sentinel/pop path fired 17,129,347 times
  (and 0 times in byte mode, matching §5.1's "dead under byte").
- Pattern shape: 14 branch templates (`a`, `ab`, empty, `a{1,2}`, `a{0,2}` (lo=0 varying), `b?`, `(a|ab)`, `(a{1,2})b`, `.{1,2}`,
  `[ab]{2,3}?`, `(b{1,2})`, `\ba{1,2}`, `a{1,2}?b`, `(a|aa|aaa)`): all 14 singles, all 196 ordered pairs, every 4th of the 2,744 ordered
  triples (686); forms `(?<=`, `(?<!`, `(?<*`; follows ``, `c`, `\1`, `c\1` (the `\1` follows only where group 1 exists: they force
  the non-atomic retry and the atomic non-retry). Retry-forcing cases are real: e.g. `(?<*(a|aa|aaa))\1` is in the population.
- Not covered (honest limits): nested lookarounds in the body, atomic/possessive body parts, recursion/subroutine calls into the
  lookbehind, max width > 4 characters, more than 3 top-level branches, `^`/`$` in a body, the 255/65535 caps. Body engine is mine, so a
  body-engine bug would show as a diff (none did), not hide one.

SIMLIT-2 -- §5.1 does not state the negative-arm / atomic / non-atomic wiring; a literal implementer must import it from the emitter. (CONFIRMED, doc)
- Severity: doc. Effort: one sentence in §5.1. Blast radius: the build lane. Both Q1 answers.
- Evidence: §5.1's listing ends at `L_ok`; frame order (negative `negok` pushed below all `L_adv`), the `CUT MARK` placement and the
  non-atomic "no cut" are only in `vm_look`. I imported them (list above) and got 0 diffs, so the existing wiring is sufficient;
  the design just does not say so. Suggest: "the negative arm's `negok` frame is pushed once at entry, below every `L_adv`;
  `L_ok` cuts to the mark (atomic and negative) exactly as `vm_look` does today; exhaustion of the last branch is `rx_fail`".

SIMLIT-3 -- §5.3's predicate (hard `RX_R_INTERNAL` only on `one-length`, decline on `range`) is load-bearing and tested. (CONFIRMED hold; see sabotage S3)
- If the range row kept today's negative-arm hard return, 8,586,600 byte cases (and 7,578,419 UTF, non-D142) return INTERNAL. No
  action; recorded as the sabotage that proves the test can see it.

## Sabotage self-check (every one MUST produce diffs; all do). Counts exclude D142; same 8,592 patterns, 37.4M byte / 39.3M UTF cases.
| id | change | byte diffs | UTF diffs (+D142 line) | smallest repro |
|---|---|---|---|---|
| S1 | retry frame saves the CANDIDATE (push after back-step) | 11,788,896 | 9,429,913 (+1,126,083) | `(?<=b?)c` on `ac`: sim nomatch, pcre2 [1-2] |
| S2 | shortest-first candidate order | 428,133 | 164,269 (+22,065) | `(?<=(a{1,2})b)` on `aab`: sim g1=(1,2), pcre2 g1=(0,2) |
| S3 | negative-arm end-check on the range row hard-returns (rev-0 rule) | 8,586,600 | 7,578,419 (+716,600) | `(?<!b?)` on `a`: sim INTERNAL, pcre2 nomatch |
| S4 | branch exhaustion goes to `rx_fail` instead of the next branch (the previous round's bug) | 6,158,214 | 4,778,858 (+814,624) | `(?<=a{1,2}|)` on `b` at 1: sim nomatch, pcre2 [1-1] |

## D142 class (UTF startpos, §6 gate 1) -- counted on its own line, excluded from diffs
UTF, start offset > 0, pattern containing `\b`: 3,714 cases differ with the design as written (interpreter does not clip backward reads
at startpos; libpcre2 does). Repro: `(?<=\ba{1,2})` on `aaa`, start 3: sim nomatch, pcre2 [3-3]. All 3,714 involve `\b` and start > 0;
none in byte mode (0), as §2 states. Classes: `(?<=` missed 570 / wrong-span 855 / false 105; `(?<!` false 192 / wrong 588; `(?<*` missed 570 / wrong 834.

## §5.5 recomputation
Design formula: per branch, per evaluation, charge <= sum of d for d=lo..hi = (hi+lo)(hi-lo+1)/2. One-length: k.
| quoted | formula | interpreter (`simlit W`, subject `b`x300+`x`, cursor 300, all candidates fail) | agree |
|---|---|---|---|
| 32,640 (`{1,255}`) | 256*255/2 = 32,640 | 32,640 (positive) and 32,640 (negative) | yes |
| 1,320 (4..51) | 55*48/2 = 1,320 | 1,320 | yes |
| 30,600 evaluations | 1,000,000,000/32,640 = 30,637.7, so 30,637 fit, "at least 30,600" true | n/a (arithmetic) | yes (floor is 37 loose) |
| per-branch formula, 3 branches `a{1,3}\|a{2,4}\|bbbbb` | 6 + 9 + 5 = 20 | 20 | yes |
| lo=0 `a{0,5}` | 5*6/2 = 15 | 15 | yes |
| clamp, `{1,255}` at cursor 10 | sum 1..10 = 55 | 55 | yes |
| UTF sentinel candidate charged D_i | `a{1,3}` on `éa`, cursor 3 (2 chars precede): 3+2+1 = 6 | 6 | yes |
| one-length `aaa` | 3 | 3 | yes |
Caveats: the 30,600 figure counts only the back-step charge; the body's own work charge is separate and not in this number (the design
says "worst-case {1,255} evaluations ... before PCREC_ERR_WORK" -- true only if nothing else is charged; not an error, a scope note).

## PROBED-AND-HELD
- Literal §5.1 and §5.1b vs libpcre2 10.46: 37,409,568 byte cases and 39,274,032 UTF-8 cases, 0 diffs (details in SIMLIT-1).
- Trail/frame discipline (D_i set before push, decremented after pop, outer pop rewinds it): held in every non-atomic retry case with a
  `\1` follow (the `(?<*(a|aa|aaa))\1`-shaped patterns), byte and UTF.
- §5.1c cells 1-3 and cell 4 shapes: cells' patterns are inside the population shape (`a{1,2}|b`, `a{2,3}|b`, `a{1,2}|bc` via `bc`-free
  analogues `a{1,2}|ab`; cell 4 is `(?<*(a|aa|aaa))\1`-style); all agree.
- Sentinel-dead-under-byte claim: 0 pops in 37.4M byte cases; 17.1M pops under UTF-8, all answer-correct.
- §5.5 numbers: all agree (table above).
