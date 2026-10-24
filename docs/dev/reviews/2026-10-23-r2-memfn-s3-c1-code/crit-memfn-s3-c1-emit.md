# crit-memfn-s3-c1 — emitted vs replaced (S3: cover/E-find vs `--memfn=no-wf-find`)

Critic: opus, read-only, lens "emitted code vs what it replaces". Review tree
worktrees/crit-memfn-s3-c1 @ ae83da9d4 (BASE c3ea619c3). Compiler: that tree's build/pcrec.
Every artifact: `pcrec -p rx --features all [-fmemfn-simd] [--memfn=no-wf-find] -o F --pattern P`.
Scratch: /tmp/claude-1001/crit-memfn-s3-c1/{probe.sh,stmt.sh,out/}. No timing was run (box shared;
a heavy queue job held the lock throughout); per-byte effects are read from C/asm and from a
counted-operations model (model.py, no clock), labelled as such.
Denylist: none of the denied files was opened. The diffstat listing (git diff --stat BASE..SUBJECT)
showed the NAMES docs/dev/lanes/s3_report.md and docs/dev/lanes/s3_evidence/* — names only, not opened.

## Findings (F1-F4); status at the end

## F1 — CONFIRMED (emitted structure + counted ops), severity SPEED: uniform-set windows `X{k}` lose the replaced artifact's run-count scan edge; E-find re-tests every run byte up to k-1 times (O(r·k) per run of r members, was O(r))

Class: every fixed-width window whose positions share ONE set (or nearly), `\d{k}`, `[0-9]{k}`, `[A-Z]{k}`,
`\w{k}`, `[a-z]{k}`, `[0-9a-f]{k}`, `.{k}`, `[^\n]{k}`, `[\x80-\xff]{k}`, k = 2..24 (the admission cap: k=24
is `cover`, 25 is not, probed with literals W24/W25). In the replaced artifact EVERY one of these carried
the `[SCAN-EDGE]` run counter (`scan_run_length`, `_DFA_SCAN_EDGE "range"`/`"bitmap"`): one read per
subject byte, never re-read (19 of 19 probed uniform windows incl. the literal runs `a{8}`, ` {8}`, `\x00{8}`; the two non-uniform controls `\b\w\w\w\b`, `[ab][cd]` carry none). E-find renders them two ways,
both re-reading:
- set mass BELOW HORS_MIN (`\d{k}`, `[0-9]{k}`, `[A-Z]{k}`, `[\x80-\xff]{k}`, `\d\d`): Table B's WALK at offset 0
  (A-mass's TIE_LOWER puts the stop at the window's first position), C-yes left to right, D-one `c + 1`.
  On a failed verify at position j the next candidate is c+1, whose positions 0..j-1 were just tested.
- set mass AT/ABOVE HORS_MIN (`\w{k}`, `[a-z]{k}`, `[0-9a-f]{k}`, `.{k}`, `[^\n]{k}`): D-hors. Every set is
  the same, so `sh[b] = 1` for EVERY member byte (the table is 1 on the set, k off it, e.g. hx8's
  `rx_mf1_sh` = 8,..,1 on 0-9/a-f); a member at the last position always advances by one and the
  left-to-right verify re-reads the run.

Repro: `pcrec -p rx --features all -o new.c --pattern '\d{16}'` vs the same with `--memfn=no-wf-find`
(`out/Wd16_{new,old}_off.c`, asm `gcc -O2 -S`, `out/Wd16_*.s`). Side by side (asm, gcc 15.2 -O2):

```
NEW (E-find: walk@0 + 15-test verify + c+1)      OLD (forward scan, [SCAN-EDGE] run count)
.L15: movzbl (%rdi,%rax),%ecx                    .L16: movzbl (%rdi,%rax),%edx
      leal -48(%rcx),%edx                              subl $48,%edx
      cmpb $9,%dl ; jbe .L4                            cmpl $9,%edx ; ja .L13      # run ends
      leaq 1(%rax),%rcx                                addq $1,%rax ; addq $1,%rcx
.L6:  movq %rcx,%rax                                   cmpq %rsi,%rax ; jb .L59
.L3:  cmpq %rsi,%rax ; jb .L15                   .L59: cmpq $16,%rcx ; je .L17      # 16 counted = match
.L4:  ... movzbl 1(%rdi,%rax),%edx ; subl $48 ; cmpb $9 ; ja .L6   (x15, offsets 1..15,
      each failure -> .L6: c = c+1, back into the walk, which re-tests c+1 .. )
```
(OLD: each digit is read once by `.L16` and the run length is carried in %rcx; a short run returns to
the DFA's start state at the separator. NEW: a run of r < 16 digits is entered r times and the verify
walks the rest of the run from each entry.)

Counted byte tests per subject byte (model.py / model_worst.py, NO clock; old ≤ 1.0 by construction,
the run counter reads each byte once):

| pattern | E-find form | APPROACH.md | window.c (C) | artifact_size_log.tsv | synthetic digit runs 1..15 | worst shape (runs of k-1) |
|---|---|---|---|---|---|---|
| `\d{8}` | walk@0 + D-one | 1.01 | 1.01 | 1.63 | 2.25 | 4.50 |
| `\d{16}` | walk@0 + D-one | 1.01 | 1.01 | 1.63 | 6.02 | 8.50 |
| `\d{24}` | walk@0 + D-one | 1.01 | 1.01 | 1.63 | 6.02 | 12.50 |
| `[0-9a-f]{8}` | D-hors | 0.20 | 0.17 | 0.43 | 1.50 | 2.43 (period k-1) |
| `[0-9a-f]{24}` | D-hors | 0.07 | 0.06 | 0.12 | 1.47 | 6.48 (period k-1) |
| `\w{20}` | D-hors | 0.65 | 0.41 | 0.67 | 1.77 | — |
| `[a-z]{12}` | D-hors | 0.80 | 0.42 | 0.61 | 0.08 | — |

Reading: on prose and code the new loops are at or below one test per byte (D-hors's non-member
shift of k pays for the re-reads: the measured hex8/year4 wins live here). On subjects DENSE IN THE
SET WITH RUNS SHORTER THAN k (numeric logs, IDs, timestamps, CSV, hex dumps of words like
"deadbeef cafe"), the per-byte work grows with k: ~6x the replaced loop's reads at k=16 on digit runs
of 1..15, k/2 in the worst shape. A test is cheaper than a DFA step (independent loads vs the step's
dependent load chain), so the wall-clock ratio is SMALLER than the read ratio and is UNMEASURED here;
the one mispredicted exit per candidate is the likely dominant cost. Name: "uniform-set window on
set-dense, match-free subjects". Suggested witness: `\d{16}` and `[0-9a-f]{24}` over 1 MB of
`random-length digit/hex runs, 1..k-1`, both layers, DEF vs `no-wf-find`, in the `none` regime.

Severity speed; effort small-medium (see G1, the general form); blast radius: every uniform window in
cover (Table C's verify order + Table D's resume; no answer risk).

## F2 — CONFIRMED (form lost), severity SPEED at the SIMD layer only: a caseless literal run with ANY position outside the run (`\b`, a lookahead byte, a class before/after) loses `vrun@w32+w16` under `-fmemfn-simd`; E-find renders B-pair (two scalar `memchr` streams) at both layers

Class: `(?i)` literal runs of 2+ letters plus a context or class position. Probed 9, 7 lose vrun:
`(?i)\bthe\b`, `(?i)\bhello\b`, `(?i)\bthe`, `(?i)the\b`, `(?i)abc(?=d)`, `(?i)[0-9]hello`, `(?i)abc[xy]` all read
`_MEMFN_FORMS "vrun@w32+w16"` on the replaced artifact at `-fmemfn-simd` and `"none"` on the new one;
the new `-fmemfn-simd` statement is byte-identical to the new SIMD-off one. Controls: `(?i)hello`,
`(?i)the`, `(?i)xyzzy`, `(?i)foobar` (pure runs) keep vrun through B-fn; `(?i)ab\d`, `(?i)http:` had no vrun
in either arm. Cause, from the design text (window_site.md rev 3.3 §2.2's renderers): B-fn holds only
when "the plan IS the offset-skip function's predicate (one RUN term holding the stop's cube)"; a plan
with one more position (a `\b` context byte, a class) fails it and falls to B-pair, which has no SIMD row.

Repro: `pcrec -p rx --features all -fmemfn-simd -o N.c --pattern '(?i)\bhello\b'` vs `... --memfn=no-wf-find`
(`out/c1_{new,old}_on.c`). Side by side (C, scalar names shortened):

```
NEW, -fmemfn-simd (== SIMD-off)                    OLD, -fmemfn-simd (rx_reqrun__w32, then DFA)
if (fr || ha < c+3) ha = memchr(s+c+3,'L',..)      m = movemask( cmpeq(and(load(s+i+3),0xDF),'L')
if (fr || hb < c+3) hb = memchr(s+c+3,'l',..)               & cmpeq(and(load(s+i+2),0xDF),'L') );
c = min(ha,hb) - 3;                                while (m) { cand = i+ctz(m);
if (\b at c-1 && (w4(s+c)&0xDFDFDFDF)=="HELL"          if ((w8(s+cand) & pk) == pt) return cand; ...}
    && ... && \b at c+5) found; else c++;          i += 32;
```
Per byte (counted on APPROACH.md, lowercased; no clock): the new loop wakes once per `l`/`L`
(0.0250 per byte, every ~40 bytes, each wake a libc return + a ≥4-test verify); the replaced 32-byte
block filters on TWO positions (`ll`, 0.00145 per byte, ~17x fewer candidates) and runs no call.
For `(?i)\bthe\b`: wakes on `h` 0.0201/byte vs the replaced `th` filter 0.0106/byte. SIMD-off is
unchanged in method (both arms use the same two memchr streams; the new arm drops the DFA tail).
UNMEASURED wall-clock; both arms' memchr are glibc's vectorized ones, so the loss is the wake rate
(~2x-17x more candidates and calls), not the scan rate.

Severity speed (SIMD layer; the layer is opt-in, OFF by default, so the default build is not
affected); effort: small if B-fn's predicate test admits "the run term + extra verify positions"
(the vrun rows already verify `pk/pt` masks, they can carry the extra tests in the post-filter) or a
B-pair SIMD row; blast radius: every caseless word with a boundary, the commonest caseless REPORT
shape. This is the same family as the r1 29x caseless finding (the PAIR/SIMD rows unreachable), now
narrowed to plans that are not exactly one run.

## F3 — CONFIRMED (form), SUSPECTED magnitude, severity SPEED: a low-mass MULTI-member set is chosen as the stop over a single rare byte, so a vectorized `memchr` becomes a scalar byte walk

Class: a window holding one rare literal byte AND a set of 2+ members whose rate-table mass is lower
still: high-byte sets (`[\x80-\xff]`, `[^\x00-\x7f]`), control ranges (`[\x00-\x08]`). Probed:
`[\x80-\xff]q`, `[\x80-\xff]x`, `[\x80-\xff]j`, `[^\x00-\x7f]e`, `[\x00-\x08]z` all take Table B's WALK on the set
at offset 0; the replaced artifacts took `memchr` on the literal (offset-set / ofsskip). Controls that
keep memchr on the literal: `[A-Z]x`, `[0-9]x`, `[^ -~]x`, `\dz`, `[XYZ]q` (5).

Repro: `pcrec -p rx --features all -o N.c --pattern '[\x80-\xff]q'` vs `--memfn=no-wf-find`
(`out/m6_{new,old}_off.{c,s}`), asm gcc -O2:
```
NEW (walk on s[c] >= 0x80, one byte per iteration)   OLD (ofsskip: glibc memchr on 'q' at offset 1)
.L14: cmpb $0,-1(%rdi,%rax) ; js .L4                 q = memchr(subject+pos+1, 113, n-pos-1);
.L5:  movq %rax,%rdx                                 cand = q - subject - 1;
.L3:  leaq 1(%rdx),%rax ; cmpq %rsi,%rdx ; jb .L14   if (rx_ofs_k0[subject[cand]]) return cand;
.L4:  cmpb $113,(%rdi,%rax) ; jne .L5   # verify 'q'  pos = cand + 1;  (then the DFA, 2 bytes)
```
The new loop is NOT vectorized by gcc 15.2 -O2 (one compare-and-branch per byte). Subject facts (no
clock): APPROACH.md has 2.76% high bytes and 0.145% `q` — the walk stops every ~36 bytes on a
candidate the verify rejects, the memchr every ~690; on build/pcrec (ELF) 15.9% high bytes, 46% bytes
0x00-0x08 (`[\x00-\x08]z` walks stop on nearly every other byte). On pure ASCII the walk never stops
but still costs one compare per byte against glibc's vector memchr. Either way the new loop does
more work per byte; the size of the loss is UNMEASURED (expected large on the no-hit regime: a byte
loop vs a vector scan).

Cause: A-mass ranks stops by mass alone (window_site.md §2.1; T_MASS_SET) and Table B then has to
WALK a multi-member set; the mass of the set is low, but the FIND METHOD's per-byte price (walk vs
memchr) does not enter the stop choice. The replaced selector (prefix_k / offset-set) did price it.
This is the stop-ranking question; D176 is on this critic's denylist, so this finding does not know
whether D176 ruled the mass-only ranking for S3 — if it did, this is that ruling's measured
consequence for the class above and should be read against D176, not as new.

Severity speed; effort: the A/B coupling (price a stop by its B pick, "find cost per byte x
candidate rate", the kit addendum's measurement-card rule); blast radius: windows mixing a rare byte
with a high-byte or control-byte set (utf8-adjacent and binary-format patterns).

**F3 addendum — the same shape for NON-CASE two-member sets.** Table B's PAIR is held to a two-member
CUBE (a case pair); any other two-member set (`[qj]`, `[qx]`) that wins the stop is WALKED. Probed:
`the[qx]` (old: memchr `h`@1, run-pinned; new: byte walk on `[qx]`@3), `ab[qj]cd` (old memchr `b`@1;
new walk `[qj]`@2), `ee[qj]ee` (old memchr `e`; new walk), `e[qj]e` (old memchr `e`@2; new walk). On
ASCII prose the replaced memchr wakes every ~50 bytes (`h`) / ~65 (`b`); the new walk is one
compare-and-branch per byte everywhere. B-pair's text (two `memchr` streams, the nearer hit) does not
need a cube: it would serve any two-member stop. Controls with no move: `[qj]`, `[qj][qj]`, `[qQ]`
(byte-class walk in both arms). So F3's class is "the chosen stop is a set of 2+ members that is not
a case pair, beside a single literal byte": 9 of 9 such probes moved from memchr to a walk.
(Of the 9, the replaced memchr was on `e` — ~10% of prose bytes — for `[^\x00-\x7f]e`, `e[qj]e`, `ee[qj]ee`,
where a walk is plausibly competitive; the clear losses are `[\x80-\xff]q`, `[\x80-\xff]j`, `[\x80-\xff]x`,
`[\x00-\x08]z`, `ab[qj]cd`, `the[qx]`.)

## F4 — SUSPECTED, severity SPEED (small): literal-run windows (`\x00{8}`, `a{8}`, ` {8}`) call `memchr` once per member byte inside a short run

E-find: `memchr(stop byte @ k-1)`, 8-byte compare, `c + 1` — inside a run of r < k members every
`c + 1` re-enters `memchr`, which returns at once. The replaced artifact found the pair and COUNTED the
run (`scan_run_length`), one call per run. Counted on build/pcrec (ELF): `\x00{8}` 0.255 memchr
calls per byte new vs ~0.111 zero-runs per byte (≈ the replaced call rate), ~2.3x the calls; on C
source ` {8}` 0.216 vs ~0.14-0.24 (the replaced pair search also calls once per lone space): near
parity. Per-call cost of a memchr that returns at once is libc call overhead, UNMEASURED. Same root
as F1 (no failure-position resume); F1's general form fixes it too (a failed compare at j resumes
past the first non-member, read right to left). Effort: with G1; blast radius: literal-run windows
(`X{k}` of one byte) on subjects with many short runs of that byte (binaries, indented code).

## Pattern-class table (old form -> new form -> per-byte effect)

`old` = `--memfn=no-wf-find` (pre-S3 artifact), `new` = default. Layer SIMD-off unless stated. Counts are probes.

| class (probes) | old form | new form | per subject byte |
|---|---|---|---|
| single byte `a` `\x00` `\xff` (3) | memchr prefilter + DFA | B-memchr, `if (1)` verify | same scan, DFA tail gone: better |
| single case pair / 2-set `(?i)a` `[aA]` `(?i)k` `[xq]` `[qQ]` (5) | byte-class table walk + DFA | B-walk `s[c]==A\|\|s[c]==a` | same (both scalar byte loops; gcc folds to 1-2 cmp) |
| plain literals `ab` `xyz` `foobar` `\x00\x00` `\xff\xfe` `a\x00b`, W8..W24 (12) | run-pinned / offset-set / handoff memchr + DFA | B-memchr on the same rare byte + inline w2/w4/memcmp verify | same find; DFA re-walk gone: better. Stop byte identical in 10 of 12; W20/W24 drop the old second memchr stream (`j`) and keep `q` |
| caseless literal runs `(?i)ab` `(?i)foobar` `(?i)hello` `(?i)the` `(?i)qu` `[aA][bB]` (10) | handoff/pair streams, or byte-class walk | B-fn (offset-skip fn, pair streams) | same or better; SIMD-on GAINS vrun on 8 that had none (see HELD) |
| caseless run + context/class position `(?i)\bthe\b` etc. (9) | pair streams; SIMD-on vrun@w32+w16 | B-pair, no SIMD row | SIMD-off same; **SIMD-on loses vrun (F2)**: 2x-17x more candidates |
| two-value / range / negated beside a rare literal `[ab]x` `[aA]bc` `[ax]yz` `q[uv]` `[a-f]x` `[^a]bc` `x[^a]y` `[A-Z]x` `[0-9]x` `\dz` `[XYZ]q` `[^ -~]x` (12) | offset-set / run-pinned memchr | B-memchr on the literal | same find, cheaper tail: better |
| low-mass multi-member set beside a literal (`[\x80-\xff]q`, `[\x00-\x08]z`, `the[qx]`, `ab[qj]cd` ...) (9) | memchr on the literal | **B-walk on the set (F3)** | vector memchr -> scalar byte loop |
| uniform dense window, mass >= HORS_MIN (`\w{k}` `[a-z]{k}` `[0-9a-f]{k}` `.{k}` `[^\n]{k}`) (9) | DFA + [SCAN-EDGE] run count, 1 read/byte | D-hors, `sh = 1` on every member | prose/code: 0.07-0.99 tests/byte (better on sparse members); set-dense short runs: up to ~6.5/byte (**F1**) |
| uniform window, mass < HORS_MIN (`\d{k}` `[0-9]{k}` `[A-Z]{k}` `[\x80-\xff]{2}` `\d\d`) (7) | DFA + run count | B-walk@0 + C-yes l-to-r + D-one | prose: ~1.0; digit-dense: 1.6-12.5 tests/byte (**F1**) |
| literal runs `a{8}` ` {8}` `\x00{8}` (3+1) | pair memchr + run count | memchr@k-1 + 8-byte compare + c+1 | up to ~2.3x memchr calls on binaries (F4) |
| lookbehind/lookahead `(?<=a)b` `a(?=b)` `(?<!x)foo` `(?<=\d)px` `(?<=q)ee` `(?<=z)e` `(?<=x)\d\d` (7) | handoff / memchr-bounded + DFA | B-memchr (context stop: D1c, `c-1`) + context test | same find, better tail |
| `\b` words `\bfoo\b` `\bx` `\Bing\b` `\bee` `(?<![a-z])ee` (5) | offset-set/first-memchr-bounded + DFA | B-memchr + inline word-class tests | same find, better tail |
| `\b\w\w\w\b` (1) | byte-class-bounded DFA (no run count) | D-hors over `\w` | prose: <1 test/byte |
| dates/times/IP `\d{4}-\d{2}-\d{2}` `\d\d:\d\d` `\d\d\d\.\d\d\d...` (3) | offset-set memchr `-`/`:`/`.` | B-memchr on the same punctuation | same (the stop moves from the first `-` to the second; same byte) |
| utf8 `€` `é` `(?i)é` `\x{1F600}` (4 cover) | offset-set memchr | B-memchr (same bytes, or a subset) | same |
| declined, unchanged (W25+, `(?i)k`/`(?i)σ`/`[α-ω]x`/`a.c`/`[^a]b` utf8, `foo(?!bar)`, `(?<=[qz])ee`, `(?i)(?<=x)abc`) (13) | — | byte-identical scan (`unanchored`) | none |

## PROBED-AND-HELD

- Other entries: `rx_match`, `rx_match_caps`, `rx_search_in`, `rx_match_in`, `rx_match_caps_in`, `rx_next_pos`,
  `rx_valid_upto` byte-identical between arms on 7 artifacts (l6, wb2, Wd16, c1, hb3, u1, la1); only
  `rx_search` and its helpers move (r2 lesson 2 asked for this diff).
- Answers: 2,849 subject x pattern runs, new vs old `--emit-main` binaries, 7 patterns covering every
  new form (D-hors, D1c context stop, B-walk@0, B-pair+`\b`, high-byte walk), random 0-40 byte subjects
  over a 18-symbol alphabet incl. utf8 bytes: 0 differences.
- Size: text+rodata of 20 artifacts, all SMALLER new (-256 B to -2,432 B; the DFA tables go). D-hors adds
  a 256-byte `sh` table per site, inside that.
- `memcmp` in the new verify (2..24 bytes): inlined by gcc 15.2 -O2 in all 10 probed artifacts (0 calls).
- Walk compare chains for multi-range sets (`[[:punct:]]`, `\w`): gcc folds to a range + 64-bit bitmask
  test, one load per byte, as cheap as the replaced 256-byte table lookup.
- SIMD-on: no artifact where the replaced one had a SIMD form and the new one has none, EXCEPT F2's class
  (7 of 9 caseless+context probes). 8 gains (`(?i)ab`, `[aA][bB]`, `(?i)ss`, `(?i)qu`, `(?i)zz`, `(?i)ea`, `(?i)et`, `(?i)ta`), 7 keep vrun in both arms, 117 `none` in both (139 total).
- Literal stops: the memchr byte is the same as the replaced artifact's in 10 of 12 literal windows; the
  two others keep the rarer of the replaced two streams.
- D1c context stop (`(?<=q)ee`): forward memchr from `c-1` with the `c < 1` clamp; reads the byte
  before `search_from` only as a context test, as the pattern requires.
- Frequent-letter caseless pairs `(?i)ea` `(?i)et` `(?i)ta` (3): byte-class walk -> B-fn two memchr streams
  on `a`/`t` (~6-9% of prose bytes, a wake every ~11-15 bytes). Plausibly neutral either way; the
  walk-vs-memchr density crossover is the finder's D1 `UNMEASURED DEFAULT` in both arms. Not a finding.
- Admission cap: 24-byte literal is `cover`, 25 is not (W24/W25/W26/W27/W28/W31 probed).

Population: 139 patterns, 4 arms each (new/old x SIMD off/on), 556 compiles in batches under 50
(the box lock was held by a queued heavy job throughout; no timing was run). 49 gcc -O2 -S/-c builds.

## Standing question 1 — sibling of a family

- **D-hors's `holds` (mass >= HORS_MIN, window >= 2)** is a member of the "how to advance over a DENSE
  set" family, which already has three other members: pcrec's `[SCAN-EDGE]` run count in the forward
  scan (`emit_dfa.c`, the form F1 says was lost), the finder's measured crossovers R3a/R3b and D1's
  walk-vs-memchr basis (finder.c), and vrun's density guard (S288 `density_memchr_guard`). Each decides
  the same question ("the stop set is dense: what replaces one-step-per-hit?") from its own threshold.
  HORS_MIN is PROVISIONAL from ONE winning cell (plan_cost.def; window_site.md §2.5 says E[sh] decides
  later). Recommend that the E[sh] reading becomes the family's ONE row: expected advance per probe,
  from the rate table, against the scan-edge run count's 1 byte per read.
- **B-fn's predicate** ("the plan IS the offset-skip function's predicate") is the composer's
  translate test again (E-stmt's). Its all-or-nothing shape is F2's cause: one extra verify position
  drops the plan from the SIMD-carrying row to a row with no SIMD form.
- **PAIR's cube restriction** (finder.c) is a sibling of ofsskip's `fn-pair` admission; on E-find's text
  B-pair's two streams need no cube (F3 addendum).

## Standing question 2 — general form and unlocks

- **G1 (F1, F4): a FAILURE-POSITION resume as Table D's general row.** On a failed test at window offset
  j with byte b, resume at `c + shift_j[b]`, `shift_j[b]` = least t >= 1 with b in the tested set at
  offset j - t, else j + 1; Table C then orders the verify RIGHT TO LEFT inside the window on D-fail's
  sites. D-hors is the j = last case; D-one is `shift = 1`. For a uniform window the table collapses to
  `j + 1` (no table). Counted (model.py, right-to-left + skip-past-failure): `\d{8}/{16}/{24}` 0.81 /
  0.38 / 0.34 tests per byte on digit runs 1..15 (new today: 2.25 / 6.02 / 6.02; replaced <= 1.0); on
  the tsv 0.22 / 0.12 / 0.07. Unlocks: removes the reason for a HORS_MIN threshold on uniform windows
  (the skip is never worse than 1 and is sublinear on dense-but-short runs), and gives the scan-edge
  run count's O(n) without a DFA. Trigger: F1's witness (`\d{16}`, `[0-9a-f]{24}` over set-dense short
  runs, `none` regime) showing a loss vs `no-wf-find` beyond floor at either layer.
- **G2 (F3): price the stop by its FIND, not by mass alone.** A's choice over positions takes B's pick
  price per byte (memchr's scan rate vs a walk's, times the stop's candidate rate) — the measurement
  card rule of the kit addendum. Unlocks: a rare literal beats a rarer-but-walked set; non-cube
  two-member stops can be priced as B-pair. Trigger: a witness on `[\x80-\xff]q` / `the[qx]` over ASCII
  prose. (Read against D176, which this critic was denied.)
- **G3 (F2): B-fn carries extra verify positions.** vrun's candidate loop already verifies an 8-byte
  `pk/pt` mask; the extra positions (a `\b` byte test, a class) go into that post-filter, so a plan that
  is "one run + k more tests" keeps the SIMD row. Unlocks: every caseless word with a boundary at the
  SIMD layer. Trigger: the default flip of `-fmemfn-simd` (R4f), or a SIMD-layer witness on
  `(?i)\bthe\b` over prose.

## Status: COMPLETE
