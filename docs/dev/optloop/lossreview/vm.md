# [LOSS-REVIEW] phase 1 — the VM-route share (lane `lrvm`, 2026-10-11)

Charter: `../lossreview_charter.md`. Population: every trailing cell of
`../gapreport_2026-10-11.md` whose shipped-default artifact routes to the VM
(`RX_ENGINE "vm"`: hybrids, frameless and counter rungs included), except the
utf8 and litrun sets (lane `lrmisc`) and SIMD-only/rust-only cells (listed in
§1.3, not attributed). Siblings: `dfa.md` (lrdfa), `misc.md` (lrmisc).

**No timing was taken.** The box ran a heavy chain throughout. Every number
here is either the bench's (set-grain medians from the 10-11 instance's
`gap_rows.json`, `vm/cells.tsv`) or a load-insensitive count:

- **stamps** compiled at main `f2fcffb4` (abi 74) with the bench's
  `pcrec-auto` flags (`--features all`). No `src/` change since the gap
  report's `e878687b` census, so the routes agree with it.
- **gcov line counts**: each artifact is built `--coverage` and driven by the
  bench's find-all loop over the set's throughput subjects (`vm/gcovrun.sh`,
  `vm/fadrv.c`). `vm/gcov_counts.py` sums the emitted lines into events
  (`vm/gcov_counts.tsv`: attempts, seek iterations, DFA steps, memchr calls,
  trail undo iterations, PLT seam calls). The subjects were regenerated
  read-only from a `git archive` of pcrec-bench `d359564f` with its own
  generators. All 31 throughput and 278 short subjects sha256-match the
  manifests (`vm/regen_subjects.sh`).
- **walk_survey's per-phase subject loads** (`studies/walk_survey/results/`,
  abi 71) as a cross-check. Match counts agree with gcov on every cell.
- **gcc -S / objdump reads** of artifacts built the bench's way
  (`-O2 -fPIC -shared`).
- **20 hand twins** (`vm/twins/`), every one answer-identical to today's
  artifact over the set's throughput and short subjects plus discriminating
  extras. Their timing is OWED to a quiet slot (§5).

## 1. Route census

### 1.1 Attributed here (37 cells: 28 throughput, 9 short-subject)

All are VM-route at main under the bench's flags. Where the brief expected a
cell here and it is not, see §1.2.

### 1.2 Expected by the brief but DFA-route at main (not mine; lrdfa's)

`syntax/asr-wb`, `asr-nwb`, `loglines/stack-frame`, `syntax/mod-i`, `mod-r`
and `capability/wild-validator-email-owasp` all stamp `RX_ENGINE "dfa"`.
email-owasp shares cause C7 with moment-iso8601 (§2.7), so it is written up
there as a cross-route note.

### 1.3 Listed, not attributed

| cell | why | numbers |
|---|---|---|
| capability `wild-secrets-github-pat` thr | rust-only (jit is 0.81, ahead) | rust x1.10, 17,833 ns |
| loglines `level-context` thr / short | rust-only (jit 0.76 / 0.73, ahead) | rust x2.09 / x1.95; gcov: the DFA hat's table walk reads 4.04M of 4.18M bytes (rust: SIMD literal prefilter) |
| litrun `wild-secrets-aws-access-key-id` thr | VM hybrid, but the litrun set is lrmisc's | jit x2.59 |

## 2. Per-cell attribution

ns lost is the bench's set-grain median, auto minus the peer (throughput:
the sum over the set's subjects). "interp" says whether pcre2-interp is also
slower than pcrec. Where it is, the peer's advantage is code generation, not
a mechanism pcrec lacks (D119).

| cell | lost vs jit (best peer) | route stamps | dominant cost (gcov counts, find-all over the bench subjects) | why the peer is faster | existing opt meant to cover it, and why it did not | cause |
|---|---|---|---|---|---|---|
| syntax `mod-j-uc` thr | **9,449,388** (x1.59) | vm framed (FRAMES 2), START_SCAN first-class `\w`, VM_PREFILTER none (no-backreference), REQ_BYTE ' ' emitted | 1,017,146 attempts, each with a frame push/pop for the `(?:the|\w+)` choice (1,017,095 pops); 4,036,174 trail-reset + 2,046,520 trail-pop iterations; 727,369 `rx_span_match` calls, which are `call rx_span_match@PLT` under the bench's `-O2 -fPIC` (gcc may not inline an exported function: semantic interposition); 3,850,208 `\w+` span iterations | same backtracking algorithm; JIT keeps captures in registers/frame, compares inline. interp 7.9x slower | [CC-DIFF] always_inline covers the entry chain, not the seam entry the VM calls; [ART-TRAIL-ELIDE] filed, unscheduled; frames are the alternation's own | C1 |
| syntax `mod-j-uc` short | 3,574 (x1.55) | same | same mechanism, 42 short subjects | as above | as above | C1 |
| syntax `bak-2` thr | **5,518,938** (x1.55) | vm frameless (inline entry), START_SCAN first-class `\w` (63 members), no prefilter | 1,047,618 attempts (76% of all positions are `\w`); **6,785,297 trail-reset iterations (6.5 per attempt)** for 7 trailed `RX_SET` sites; 794,481 PLT seam calls; 1,375,704 hat-seek iterations | as above. interp 6.4x slower | trail: [ART-TRAIL-ELIDE]; PLT: none; hat: START-SET stage 2's `pf_vm_start_applies`, which has no density admission (`|S| < 256` is its "ONLY narrowness gate", an UNMEASURED DEFAULT, D149; MASS admission filed, Q-R5 / [START-DENSE]) | C1 |
| syntax `bak-2` short | 1,427 (x1.27) | same | same | as above | as above | C1 |
| syntax `bak-py`, `bak-g-rel`, `bak-1` thr | **3,541,265 / 3,483,601 / 3,453,927** (x1.27-1.28) | vm frameless (inline), START_SCAN first-class `\w`, REQ_BYTE ' ' emitted | 1,017,146 attempts; 3,850,412 `\w+` span iterations (each attempt inside a word rescans to its end); 4,036,174 trail-reset iterations; 726,049 PLT seam calls; **291,097 attempts fail at the ' ' test, which is independent of the start position within the word run** | as above. interp 6.0-6.1x slower | trail/PLT/hat as above; no opt skips the start-independent failures (PCRE2 does not either) | C1 |
| same three, short | 1,094-1,117 (x1.20-1.21) | same | same | as above | as above | C1 |
| capability `phone-palindrome-6` thr | **1,739,252** (x1.26) | vm frameless (inline), START_SCAN first-class `\d` | 4,681,579 hat-seek iterations (a table walk over every byte of 4.68 MB); 469,540 attempts; **3,806,544 trail-reset iterations (8.1 per attempt)** for 10 trailed `RX_SET` sites; 240,718 PLT seam calls | as above. interp 7.0x slower. The ratio moved x3.00 -> x1.26 since 10-05, but the subjects changed (capability 0.1 -> 0.2), so that is not a movement | trail, PLT as above | C1 |
| capability `quoted-delim-match` thr | **1,643,355** (x3.79) | vm framed (FRAMES 2048), START_SCAN first-class `{",'}`, no prefilter (no-backreference) | **4,641,424 hat-seek iterations: the 2-member table walk reads every byte**; only 44,024 attempts | JIT scans the two-byte first-code-unit set with a SIMD search; interp 3.0x slower | START-SET stage 2's `pf_vm_emit_first_class`: "Q-R5: the TABLE form only at stage 2, at any `|S|`". The `|S| = 1 -> memchr` cut-over is not taken (D149), and no 2-byte form exists for the VM hat | C2 |
| syntax `bak-k-named` thr | **528,346** (x2.14) | vm frameless, START_SCAN first-class `{<}`, REQ_RUN "</" emitted | 1,309,729 entry + 174,838 retry seek iterations (a 1-member table walk); 16,071 memchr (pre-check); 6,968 attempts | JIT: SIMD first-char search. interp 1.3x slower | as quoted-delim (table form at `|S| = 1`) | C2 |
| capability `balanced-parens-rec` thr | **411,833** (x1.53) | vm framed (linked call), START_SCAN first-class `{(}`, REQ_BYTE ')' emitted | 1,319,883 seek iterations (1-member table walk); 15,733 memchr; 23,583 frames | as above. interp 2.5x slower | as above | C2 |
| syntax `qnt-poss-quest` thr | **1,133,848** (x1.94) | vm hybrid, exact language, DFA prefilter memchr('a'), RESEED adaptive, frameless | **1,295,798 VM attempts: one at every byte** (`'a'` gaps sit under the 16 B crossover, so the adaptive retry steps); the prefilter itself takes 12,804 steps | JIT: SIMD skip to 'a', then a 2-byte check. The language of `a?+a` is exactly `aa`, so a DFA answers it with no VM at all. interp 1.9x slower | [OPT-HYB-RESEED]'s adaptive row: its step mode advances one byte, not to the next start-set byte (the VM hat is declined on a hybrid by V's ROUTE conjunct); [OPT-HYB-RESEED-POLICY] (folded into [START-DENSE]) measured this cell on the Mac | C4 |
| syntax `grp-atomic-alt` thr | **700,654** (x2.74) | vm hybrid, exact, DFA prefilter memchr('a'), RESEED adaptive | 101,815 memchr calls (one per `'a'`, 7% of bytes); 199,741 forward DFA steps; 5,858 matches. The VM's own share is small (walk_survey: 0.01 loads/B) | `(?>a|ab)c` is exactly `ac` (once `a` succeeds the atomic group never tries `ab`), and the language JIT scans is that pair. interp 7.1x slower | the atomic group forces the VM, and the hybrid's prefilter is the erased `(?:a|ab)c`, which has no fixed literal run for [OPT-LITSCAN] S1's run-pinned rows to pin | C4 (+C3) |
| syntax `lkb-pos` / `lkb-neg` thr | **372,614 / 340,268** (x2.85 / x2.00) | vm hybrid exact, DFA prefilter offset-set `"0,2*"` (memchr at the pinned byte) | 43,173 / 56,660 memchr calls, one per occurrence of the pinned byte; ~18.8K forward steps. The VM share is small | JIT: a SIMD char-PAIR search (two bytes at a fixed distance), so near-zero candidates and no per-hit call. interp 6.2x / 6.8x slower | [OPT-LITSCAN] S1 / the memfn kit's `fn-memchr` body: one memchr stream, restarted per hit. The scalar fused pair filter (R4d, SWAR) has its trigger MET at SIMD-off (integration.md §22) and is unbuilt; the SIMD pair rows (R-13 `vrun-w32/w16`) are behind `-fmemfn-simd`, OFF | C3 |
| syntax `lka-pos` / `lka-verb` thr | **323,123 / 323,157** (x2.98) | vm hybrid exact, run-pinned `item@3` (memchr 'm') | 30,349 memchr calls (one per 'm', 2.2% of bytes); 3,582 `item` hits; 36 matches | as lkb-*. interp 4.9x slower | as lkb-* | C3 |
| syntax `lka-neg` / `lka-nonatomic` thr | **223,038 / 187,990** (x1.75 / x1.62) | as lka-pos | 30,314 memchr; ~3,560 matches | as above | as above | C3 |
| capability `wild-secrets-slack-webhook-url` thr | **220,642** (x2.25) | vm hybrid exact frameless, REQ_RUN `RVICES/T@6` with fold mask, REQ_HANDOFF 26 | 39,130 memchr('/') calls in the run pre-check, each followed by a masked 8-byte compare; 0 matches | JIT: SIMD char-pair search. interp 4.6x slower | as lkb-*. The gap report groups this cell under CI, but its scan byte `/` is case-invariant, so no caseless mechanism is involved | C3 |
| capability `pwd-strength-chain` thr / short | **263,045 / 3,766** (x1.97 / x1.45) | vm hybrid exact (DFA attempt, anchored), VM framed (FRAMES 9) | 81,922 frames popped: each lookahead's `.*` greedy span, then one resume per position backwards; 163,842 span iterations. Lives on t-evil-* (60K / 16K letters with no newline) | same algorithm, cheaper per step. interp 2.3x slower | the cursor rung pushes one resume frame per retreated position even when the follow atom is a one-byte test | C6 |
| bounded `ctx-lazy-64` / `-256` / `-1024` / `ctx-greedy-256` thr | **63,746 / 64,310 / 64,178 / 63,311** (x1.6; rust x7.6, 146K each) | vm, ENGINE_SEL collapsed-prefilter, DFA hat first-class-bounded `{a,f,p}`, REQ_BYTE 'a' | on the letters subjects (86 KB of the set's 106 KB), **85,988 forward DFA steps out of 85,988 letter bytes, all in state 22**, the `\b` word-wait state (self-loops on the 63 word bytes, exits on non-word). The hat's skip runs 31 iterations; it skips only in state 0. The digit subjects are dismissed by the REQ_BYTE pre-check | rust: a SIMD literal prefilter over `fail|abort|panic` finds no candidate in random letters. JIT: a cheaper per-byte loop. interp 3.3x slower | M2.1's `pick_skip_states` admits a stay loop only on states that stay put on **>= 192 of 256 bytes**. State 22 stays on 63, so no stay loop. K91 (I1) also counts the hat's seek on these cells, +4-6% | C5 |
| bounded `ctx-lazy-64` short | 1,185 (x1.22) | same | short log lines, mixed | as above | as above | C5 |
| capability `wild-datetime-moment-iso8601` thr | **62,659** (x10.7 jit; x39.8 re2, 67,392) | vm hybrid exact, DFA attempt (anchored, one attempt), **REQ_BYTE '-' REQ_WHY "one-attempt"** | 77,838 attempt steps, all on two hazard subjects: `t-trim-match-60k` (61,440 bytes, every byte read) and `t-trim-nearmiss-16k` (16,385). `^\s*` consumes the whole whitespace run, then fails. The other nine subjects fail within 1-5 bytes | re2/JIT answer from the required byte: `'-'` is absent, so they never walk the run. **interp is SLOWER than jit but FASTER than pcrec (x1.45)**: this is algorithmic | [OPT-PRECHECK-ADMIT] G2 (`req_route_one_attempt`) declines the pre-check on a linear one-attempt route. G2's premise, "the attempt reads at most the window the check would scan", holds in bytes but not in cost: a DFA step (~0.8 ns/B) against memchr (~0.05 ns/B) over an unbounded leading run | C7 |
| syntax `grp-cap` / `grp-named` / `grp-named-quote` thr | 136,748 / 139,548 / 137,728 (x1.25-1.26) | vm hybrid exact frameless, run-pinned `cat` | 42,663 memchr, 7,628 matches. **nocaps is 663-664K: the same cost as the DFA route's `lit-cat` (663K, DENSE, lrdfa)**. The VM's capture assignment is the ~20K difference | as DENSE (lrdfa). interp 5.5x slower | DENSE's own (lrdfa). The VM-specific share is 3% | C8 |

### 2.1 The brief's specific questions

**ANCH-ATTEMPT: which subjects, and why.** The losses sit on the two `t-trim`
subjects for moment-iso8601 (`^\s*` reads the whole whitespace run) and on
`t-evil-match-60k` / `t-evil-nearmiss-16k` for email-owasp (`[a-zA-Z0-9_+&*-]+`
reads 60K / 16K letters looking for `@`, which is absent; walk_survey's
per-subject loads are exactly 61,440 and 16,385 there and 1-9 bytes on every
other subject). Both are G2 declines of a necessary byte that the subject does
not contain (C7, §3). The capability@0.1 subjects did not expose it because
every 0.1 subject fails these anchored patterns within a few bytes.

**bak-2, the only grower since 10-05: what moved it.** The bench's pcrec side
went 13,173,354 -> 15,484,565 ns (+17.5%). I diffed the artifact emitted by a
compiler built at the 10-05 pin `c4c70f2c` against main's, comments
stripped. The **only program change is START-SET stage 2's VM hat**
(`ssbuild2`, abi 62): a 256-entry `rx_start_set` table for `\w` and the seek
loop at the entry and at every retry. On syntax text `\w` covers 76% of
positions. So the seek skips the 24% of attempts that were already cheap (each
fails at the program's first `\w` test, the same bitmap) and puts a table
load, a compare and a data-dependent loop exit in front of each of the 1.05M
attempts that remain. gcov: the deny build (`-fno-start-set`) takes 1,375,704
attempts and no seek, against 1,047,618 attempts plus 1,375,704 seek
iterations at main. bak-1, bak-g-rel and bak-py carry the same hat and grew
3-4%: their attempts are costlier (a `\w+` span, a pre-check), so the seek is
a smaller fraction. The emitter's own comment at `pf_vm_start_applies` names
this regime: "a dense S (a `\w`-led pattern, |S| = 63) still seeks; ... a MASS
admission is filed behind them (Q-R5)". Twin `bak2-no-start-set` (a flag
build, answer-identical) settles it in a quiet slot.

**BACKTRACK: is pcre2-interp also slower?** Yes, on every BACKTRACK cell (6-8x
slower: `vm/cells.tsv`'s `interp_ns`). These cells are not algorithmic losses
in D119's sense: PCRE2 runs the same backtracking search and the JIT wins on
code generation. The same holds for every VM-route cell in §2 except
moment-iso8601, where interp beats pcrec. That does not make the backtrack
losses unfixable. The counts point at three pcrec-specific per-attempt costs
the JIT does not pay, and two of them already have rows (C1, §3).

## 3. Per-cause roll-up, ranked by total loss

Totals are the sum of ns lost vs pcre2-jit over the cause's cells
(throughput + short-subject, both caps classes as the gap report scored
them). The figure vs the best non-vectorscan peer is given where it differs.

| rank | cause | cells | total lost vs jit (ns) | vs best peer | algorithmic (scalar peer or interp also wins)? |
|---|---|---|---|---|---|
| 1 | **C1 BACKREF-ATTEMPT**: per-attempt overhead in backreference programs. (a) The seam compare `<prefix>_span_match` is an exported function, called through the PLT under `-fPIC`. (b) A frameless program trails every slot write and undoes 4-8 trail entries per failed attempt. (c) START-SET's VM hat seeks on a dense `\w` set. (d) Attempts inside a possessive word run fail at a start-independent test and are rescanned | mod-j-uc, bak-2, bak-py, bak-g-rel, bak-1, phone-palindrome-6 (x2 regimes) | **27,193,673** | same | no (interp 6-8x slower) |
| 2 | **C2 VM-HAT TABLE FORM**: the VM hat's seek walks a 256-entry table byte by byte even where `|S|` is 1 or 2 and sparse | quoted-delim, bak-k-named, balanced-parens | **2,583,534** | same | no |
| 3 | **C3 ONE-BYTE MEMCHR RESTART**: a literal-run prefilter or pre-check scans one byte with memchr and restarts the call per hit; JIT scans a char PAIR with SIMD | lkb-pos, lkb-neg, lka-pos, lka-verb, lka-neg, lka-nonatomic, slack | **1,990,060** (+ grp-atomic-alt's scan, counted in C4) | same | no |
| 4 | **C4 VM-FORCED REGULAR LANGUAGE**: a possessive / atomic construct forces the VM where the language is a plain literal, and the hybrid's adaptive retry steps every byte | qnt-poss-quest, grp-atomic-alt | **1,834,502** | same | no |
| 5 | **C8 DENSE (route-independent)**: lrdfa's DENSE cause under a VM hybrid; the VM's capture share is 3% | grp-cap, grp-named, grp-named-quote | 414,024 | same | no |
| 6 | **C6 CURSOR-RUNG REWIND**: a greedy span retreats one resume frame per position even when the follow atom is a one-byte test | pwd-strength-chain (x2 regimes) | 266,811 | same | no |
| 7 | **C5 WORD-WAIT STAY THRESHOLD**: M2.1's 192-of-256-byte stay rule declines the `\b` word-wait state, so the DFA steps every byte of a word | ctx-lazy-64/256/1024, ctx-greedy-256 (+ the short cell) | 256,730 | **584,735** vs rust | rust only (SIMD literal prefilter) |
| 8 | **C7 G2 REACH-BLIND DECLINE**: G2 declines the necessary-byte pre-check on a one-attempt route even when the attempt can read an unbounded run before reaching that byte | moment-iso8601 (+ email-owasp, DFA route, 39,731) | 62,659 | 67,392 vs re2 | **yes** (re2 x39.8, interp x1.45) |

Total VM-route loss vs jit: **34,643,515 ns**. C1 is 78% of it.

## 4. Phase-2 seeds (fix-existing first)

Each seed names the mechanism, its existing home, the population it moves,
the remodel overlap, and what in phase 1 supports it. No gain is claimed
before the twins are timed.

### 4.1 Fix-existing

1. **C1a: emit the encoding seam's hot entries with internal linkage.**
   `<prefix>_span_match` (backreferences) and `<prefix>_back_step`
   (lookbehind) are exported functions. Under the bench's
   `gcc -O2 -fPIC -shared` (a stranger's shared library builds the same way)
   gcc may not inline them, because a default-visibility symbol can be
   interposed. Every call is a `call ...@PLT` in the attempt loop: 12 sites in
   bak-2's `.text`, 18 in phone-palindrome-6, 6 `back_step` sites in lkb-pos.
   The fix is to emit a `static inline` body that the VM calls and keep the
   exported name as a one-line wrapper. [CC-DIFF] STEP 1 put `always_inline`
   on the entry chain's statics for the same class of cost; the seam entries
   were outside its set because they are public. Population: every
   backreference and lookbehind artifact. It is an abi event (emitted text),
   with byte-identical answers. Static evidence: bak-2 `.text` goes
   4,161 -> 3,156 bytes. Twins: `bak2-static-seam`, `bak1-static-seam`,
   `modj-static-seam`. Remodel overlap: memfn owns the N7 span compare's
   LOOP (M7, `memfn/src/mismatch.c`), and the entry's signature and linkage
   are the backend's (`src/enc/`, D58 addendum 2). This seed touches only the
   linkage.
2. **C1b: [ART-TRAIL-ELIDE] has a sub-case that needs no dataflow fact.** In
   a FRAMELESS program the trail's only reader is
   `rx_reset_for_next_attempt`. Every attempt starts with every slot UNSET.
   So an untrailed `RX_SET` plus a reset of the program's own written slots to
   `PCREC_UNSET` is equivalent by construction. The row's dominance fact is
   needed only for framed programs. Population (from the row): 27 bench /
   623 corpus frameless artifacts with `RX_SET`. The frameless trail
   `FRAMES` give-up disappears, a one-way change that needs the limits.md
   hunk the row already names. Evidence: bak-2 undoes 6.5 trail entries per
   failed attempt (6.79M iterations) and phone-palindrome-6 8.1 (3.81M).
   bak-2 `.text` 4,161 -> 3,123 bytes, and both C1a+C1b give 2,036. Twins:
   `bak2-trail-free`, `bak2-both`, `bak1-both`, `phone-both`. Remodel
   overlap: none (the row says so).
3. **C1c + C2: give the VM hat a form row and a density admission
   (Q-R5 / [START-DENSE]).** Two halves of one table. (i) A dense `S` (bak-2's
   `\w`, 76% of positions) should decline: the seek costs more than the
   attempts it removes. The MASS primitive (`pcrec_dfa_cand_ppm`, the prior's
   mass over the scanned set) already prices the DFA hat's re-seed. (ii) A
   sparse `S` of one or two bytes should seek with memchr or a two-stream
   leapfrog, not a table walk. The kit already has `pf_memchr`, and the K82
   pair leapfrog exists as `fn-pair`. That is D157's shape: pcrec states
   `|S|` and the rate, and the kit picks the form. Population: 176 auto
   corpus / 17 bench VM-hat movers (ssbuild2's manifest). The deny build and
   twins are measured below. Twins: `bak2-no-start-set`,
   `phone-no-start-set` (a 10-member digit set at low density, the control
   that should NOT regress), `quoted-seek`, `parens-seek`, `kname-seek`.
   Remodel overlap: [START-DENSE] is gated on C7 (done); the FIND text is
   memfn's (R4g PF).
4. **C5: price M2.1's stay threshold by MASS, not by byte count.**
   `pick_skip_states` admits a state that stays on >= 192 of 256 bytes. The
   `\b` word-wait state stays on 63 bytes that carry ~80% of text mass, and on
   the bench's letters subject 100%. A threshold read off the prior (the same
   MASS primitive) would emit a stay loop there. The loop-carried value
   becomes the cursor rather than a dependent table load. M2.10's measured
   regression was a REVERSE-machine skip, and the forward machine is untested
   (the function's own comment). This is also a "suspect tuning constant".
   Population: every leading-`\b` DFA scan, hybrid prefilters included. The
   same gcov run counts 1.46M / 2.56M / 3.23M forward steps on lrdfa's
   json-constant / dbnames / hex32-id (an FYI went to lrdfa). Twin:
   `ctx64-stay22` (85,988 -> 6 forward steps on the letters subjects).
   Remodel overlap: the STAY site's text is memfn's (R4h); the DECISION
   (`pick_skip_states`) is pcrec's.
5. **C4 (retry half): step through the start set, not every byte.** When
   [OPT-HYB-RESEED]'s adaptive row steps, it advances one byte. The VM hat's
   `S` is declined on a hybrid by its ROUTE conjunct. A stepping retry that
   seeks the next byte of `S` makes qnt-poss-quest's attempts go from
   1,295,798 to 95,957 (twin `possq-stepset`). This is the retry slot's row
   ([START-DENSE] folds [OPT-HYB-RESEED-POLICY], which measured this cell).
   Twin `possq-no-reseed` gives the fixed retry for reference.
6. **C6: let the cursor rung seek its follow byte when it retreats.** When
   the atom after a greedy span begins with a one-byte test, the retreat
   could scan down for the next position passing that test and push one
   frame there. Today it pushes and pops one frame per position.
   pwd-strength-chain goes from 81,922 frames popped to 0 (twin
   `pwd-rewind`). It needs a give-up statement: fewer steps are consumed, so
   a `STEPS` give-up can become an answer and never the reverse. Population:
   not counted here. The STEP 0 would be a census of cursor rungs whose
   follow starts with a one-byte test.
7. **C3: build R4d (the scalar SWAR pair filter).** integration.md §22: its
   trigger is MET at SIMD-off (union-select 1.4-2.0x, mod-i's sweep 2.7x on
   the Linux box). Every C3 cell pays one memchr restart per hit of a 2-4%
   byte: 30-57K calls per 1.37 MB, at a derived ~10-16 ns per call. JIT
   avoids this with a SIMD pair search, and R-13's `vrun-w32/w16` rows are
   the SIMD form (OFF by default; SIMD-attributable). Remodel overlap: memfn
   (kit rows). This is shared with lrdfa's SCAN-SIMD/SEL-LIT cells.
8. **C7: make G2 reach-aware.** G2 should decline only where the one attempt
   cannot read further than a bound before it reaches the necessary byte.
   That needs the byte's max offset from the attempt start, which is the
   landmark-offset fact [REQ-HANDOFF-L1] introduces (main has
   `req_run_maxoff` for runs only). moment-iso8601 and email-owasp both have
   the byte behind an unbounded leading run. **There is a trade, and it is
   the reason G2 exists**: the batch-1 G2 cells were whole-subject matches
   where the extra memchr is pure overhead (+18.7-38.5% at ns scale). Here
   the hazard cells lose ~60 µs per set pass. Ranked by total loss the
   admission wins. The decision belongs to [PRIOR-COST-UNIFY], the one
   expected-cost primitive, and should not be another hand-set rule. Twin
   `moment-precheck` (77,838 attempt steps -> 8).

### 4.2 New mechanisms (after the fix-existing items)

- **C1d: start-independent failure skip.** When an attempt's first atom is a
  possessive class run `C+` and the attempt fails at a test that reads only
  positions at or past the run's end (bak-1's ' ' test), every start inside
  that run fails identically, so the loop can skip to the run's end. 29% of
  bak-1's attempts are in this class (291,097 of 1,017,146). PCRE2 does not
  do this, so it would be a lead over the JIT on this family. It needs its
  own D77 census.
- **C4 (language half): rewrite possessive/atomic constructs whose language
  is regular.** `C?+C` is `CC`, `C*+` is `C*(?!C)`, and an atomic
  alternation whose first branch is a prefix of a later one has a dead later
  branch. Each rewrite turns a VM-forced pattern into a DFA one. The
  one-character negative lookahead it produces is [ENG-LOOK] shape (a). Twin
  ceilings: `possq-aa`, `atomicalt-ac` (pattern twins, answer-identical).
  Population: not counted.

## 5. Owed twins (timing in a quiet slot; scratch tier)

All 20 are built and answer-checked (`vm/twins/twins.tsv`, which lists the
question each one answers and its answer-check count). Reproduce:

    W=worktrees/lrvm; export LR=$W/build/lr PCREC=$W/build/pcrec BENCHCOPY=$LR/bc
    $W/docs/dev/optloop/lossreview/vm/regen_subjects.sh $BENCHCOPY   # expect 309 OK
    $W/docs/dev/optloop/lossreview/vm/twins/run_all_twins.sh          # 20 x ANSWERS IDENTICAL
    for t in $LR/twins/*/; do "$t/time.sh" > "$t/time.log"; done        # QUIET SLOT ONLY

Each `time.sh` runs 9 interleaved rounds, base then twin, pinned to one core
(`taskset -c 14`). Each driver is built the bench's way (`-O2 -fPIC -shared`
artifact, driver linked against it) and reports best-of-5 per subject plus
the set total. A twin is a candidate's CEILING on its own cell, never its
landing number: the landing still needs the bench's own run (D144 add. 4).

Priority, by the loss each twin could explain: `bak2-both` and `bak1-both`
(C1, 27M), `bak2-no-start-set` (the grower), `modj-static-seam`,
`quoted-seek-seam` (C2), `possq-stepset`, `ctx64-stay22`, `pwd-rewind`,
`moment-precheck`.

## 6. Files

`vm/` holds this attribution's instruments and data. See `CLAUDE.md`.
