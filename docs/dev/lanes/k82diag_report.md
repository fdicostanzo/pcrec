# k82diag — K82 diagnosis: [OPT-LITSCAN] S4 C3's movers and short-call term (2026-10-04, lane k82diag, opus)

DIAGNOSIS ONLY. No `src/` change. Branch `lane/k82diag` from main `2c344793`
(abi 59). The Mac numbers below are DIRECTIONAL ONLY (D144 add. 1): they are
gcc-16 -O2 on the M1, calibrated loops of at least 50 ms
(`alpha_c3.sh`'s own `drv.c`), median of 3 launches x 5 passes, with no
taskset and no floor arm. Linux numbers are r1alpha's (`r1read_report.md` §3),
and the per-call rows were read off `scratch_lx/r1alpha/c3.out` by one
read-only `ssh grep`. Instruments and transcripts are in
`docs/dev/optloop/s4/k82diag/`.

## 0. Summary

K82 has **three causes, not one**. None of them is in the masked compare.

| cause | movers | mechanism (measured by an instrumented twin, §1) | cure (§4) |
|---|---|---|---|
| **A. The run pre-check REPLACES a rarer byte pre-check** | `userpass` | BASE ran `memchr('=')`, and `=` is absent from the cap subjects, so it rejected in one pass. NEW runs only the `USER` run block. The masked run matches `user`, which occurs 187-212 times per 64 KiB, so **the gate PASSES on 100% of calls** after about 900 B, and the hybrid's DFA prefilter then scans the whole subject (0.0168 -> 0.95 ns/B). | row R3: the set pick leads when it is rarer than the run's scan member. Twin T1 restores BASE exactly |
| **B. A low-information run's pre-check passes on match-dense text and doubles the scan** | `mod-i`, `mod-r`, `cls-fold-pair`, `cls-pair-ctl`, `ci-strasse` | The gate passes on 99.7-100% of calls. Its candidate is DISCARDED (`if (rx_reqrun(...) >= n) return 0;`), so the engine rescans the same span. The pair arm also re-searches both streams fresh on every call, so the rare stream's lookahead is thrown away: on `mod-i` the gate's `memchr`s read **4.8x the subject** per find-all. | row R4: the run pre-check needs about 16 bits of information UNDER THE RATE. These runs carry 12.5-13.9 bits under the builtin prior, the customers 16.2-25.9. Under NONE, `ci-strasse` cannot be told apart from `ci-ascii-ctl` (§4.4) |
| **C. Under NONE the PICK lands on a pair of UTF-8 LEAD bytes** | `alt-shared` | `e697a5e4@3/fffffffd`: the NONE answer "rightmost" scans `{0xE4, 0xE6}`, which are CJK lead bytes (1.5% of u8 text), instead of BASE's exact continuation byte 0xA5 (0.37%). That costs 13x the `memchr` calls (518 against 40 per find-all). | the PICK primitive's NONE answer becomes the uniform-mass argmin, with ties still going to `rightmost`. Twin T2 recovers most of it, with a residual of about +0.02 ns/B on the Mac |

The suspected cause ("a scan that stops on every `u`") is **half right for
`userpass`**. The pick did drop the rare `=` guard, which is cause A. But the
cost does not come from per-`u` hits: the gate made 2 compares per call. The
cost is that the gate stops REJECTING and the full engine runs. It is
**wrong for the other six**, which are causes B and C.

**The short per-call term** (§2) is the pair arm's floor: two fresh `memchr`
calls per call, which is a flat ~10.06 ns on Linux glibc. It costs +2.4..+4.4
ns where BASE's DFA rejected a 6-11 B subject in 6.5-7.7 ns, about +4.4 ns per
failed candidate, and +6.6..+11 ns on the four subjects that contain `select`
(there the gate passes, so its cost is purely added). Net over 73 cells on
Linux: **-127 ns** (39 WIN, -264; 34 REGRESSION, +136).

**Recommendation (§5):** keep C3 default-on IF the R3/R4 fix is round 2's
first build. Otherwise flip it off.

## 1. The seven movers, grouped by cause

Delta = `-fno-req-run-fold` (DENY == BASE, abi 58's program) against default
(NEW), at `--features all -p rx`, with the cells' own flags. Gate counters come
from `mk.sh` (each `memchr` inside `rx_reqrun` is counted, along with each
masked compare and each gate pass/fail), normalized per find-all run.

### 1.A `userpass` (`(?:username|USERNAME|user|USER)[ \t]*=…`, VM engine with a DFA prefilter)

- **Emitted delta.** BASE: `if (... !memchr(subject + search_from, 61, ...)) return 0;`.
  NEW: that line is GONE. In its place is `rx_reqrun` (the pair arm on
  `U`/`u`, then `(rx_w4(s+cand) & rx_w4("\337\337\337\337")) == rx_w4("USER")`),
  and then the unchanged `rx_prefilter` (DFA) and VM.
- **Facts.** `req_set {61}`, `req_whole_run 55534552/dfdfdfdf` (28 popcount
  bits, the `user|USER` hull), `req_byte 61`. `REQ_BYTE "61"` still names `=`,
  but on this route no emitted code tests it. That is litscan_s4.md
  §2.3.3 case (ii).
- **Counters (cap t-64k, per call):** 1 gate call, **1 pass**, 3 `memchr`
  calls, 904 B scanned, 2 compares. The text has 0 `=`, 212 caseless `user`
  and 0 `USER`.
- **Cause A.** The rejection power is lost. The gate is cheap, but it says
  "maybe", and the full DFA prefilter pass follows.
- **Twin T1** (NEW with BASE's `memchr('=')` placed in front of the run
  block), Mac:

  | subject | deny | new | T1 |
  |---|---|---|---|
  | cap t-64k | 0.01999 | 0.6227 | **0.01998** |
  | cap t-1m | 0.02312 | 0.7326 | **0.02312** |

  T1 equals BASE to four digits.
- **The design named this.** litscan_s4.md §2.3.3 lists, as "Not built", "a
  one-byte `memchr` of the set pick in front of the run block on DFA routes …
  Its trigger is a DFA-route pair-scan mover whose set pick is rare and absent
  on a measured subject." `userpass` IS that trigger: the hybrid route, a pair
  scan, and `=` rare and absent.

### 1.B `mod-i`, `mod-r` (`(?i)cat`), `cls-fold-pair` (`c[aA]t`), `cls-pair-ctl` (`c[ac]t`), `ci-strasse` (`(?i)straße`, utf8)

- **Emitted delta.** A NEW `rx_reqrun` gate appears in front of an UNCHANGED
  DFA:
  - `mod-*`: there was no pre-check before. The gate is the pair arm on
    `C`/`c` with two overlapping masked `rx_w2` compares, and it sits in front
    of the byte-class scan loop.
  - `cls-*`: BASE was `REQ_WHY "dominated"` (the DFA's own `memchr('c')`
    prefilter). The masked run carries more than that prefilter verifies, so
    G1 no longer dominates and a one-stream `memchr('c')` run block is added
    in front of the same `memchr('c')` prefilter. This is the `a[bc]de` G1
    move of §2.3.5, which the design accepted with "if its cost shows on a
    measured cell, bit 44 is the interim kill switch".
  - `ci-strasse`: the pair arm on `A`/`a` at k* = 2 (`TRA`), in front of the
    byte-class DFA.
- **Counters (per find-all run, 64 KiB subject):**

  | cell | matches | gate pass rate | `memchr` calls | bytes `memchr` read | compares |
  |---|---|---|---|---|---|
  | mod-i | 400 | 99.75% | 2,634 | 317 KiB (**4.8x the subject**) | 2,232 |
  | mod-r | 400 | 99.75% | 2,630 | 317 KiB | 2,228 |
  | cls-fold-pair | 377 | 99.7% | 2,096 | 64.8 KiB (1.0x) | 2,095 |
  | cls-pair-ctl | 377 | 99.7% | 2,096 | 64.8 KiB | 2,095 |
  | ci-strasse | 11 | 100% | 526 | 54.7 KiB | 514 |

- **Cause B.** On these subjects the run is PRESENT, densely (syn: one `cat`
  per ~163 B). A pre-check only pays when it rejects. Here it never does, so
  every call pays the gate's span and then the engine's scan of the same span:
  - The gate's candidate is not handed on. The emitted gate is
    `>= subject_length` only.
  - `mod-*` pays a second, emission-level cost. `fresh = 1` re-searches BOTH
    streams on every call, so the rare `C` stream (0.2%) runs ~500 B ahead
    past the next match and is thrown away. The next call reads the same
    bytes again, which makes 4.8x.
  - `cls-*` scans one stream, so it is "only" a doubled `memchr('c')` (1.0x
    plus the prefilter's own 1.0x).
- **Mac directional** (ns/B, deny -> new): mod-i 64k 0.747 -> 1.504, 1m 0.837
  -> 1.648; mod-r 64k 0.748 -> 1.503; cls-fold-pair 64k 0.581 -> 1.182, 1m
  0.771 -> 1.348; cls-pair-ctl 64k 0.575 -> 1.210; ci-strasse 64k 0.526 ->
  0.610, 1m 0.593 -> 0.786. Same direction and order as Linux.
- **The masked compare is not the cost.** `cls-*`'s one-stream arm loses as
  much per byte as `mod-*`'s two-stream arm minus the overshoot. The term is
  the per-candidate `memchr` restart plus the compare, about 8-11 ns per scan
  hit. Note also that the r2 census counted G1 moves for class C only (1, in
  the corpus). The two `cls-*` G1 moves are class A1, so that count missed
  them.

### 1.C `alt-shared` (`日本|日曜|日付`, utf8)

- **Emitted delta.**
  - BASE: exact run `e697a5@2`, one-stream `memchr(0xA5)` at k* = 2.
  - NEW: `e697a5e4@3/fffffffd` (日 plus the next character's lead byte,
    `{E4, E6}` folded by bit 1). It is the pair arm on 0xE4/0xE6 at k* = 3.
  - `REQ_BYTE` moves `165` -> `230`.
- **Fact.** `req_run ... rate:none(utf8)->rightmost`. Under `-e utf8` the
  default analysis serves no byte-rate (D123-4/5, findings design §2.4,
  reqbyte_freq_pick.md §3), so PICK answers the positional rightmost, which
  is the pair.
- **Counters (u8 t-64k, per find-all run):**

  | arm | gate pass rate | `memchr` calls | bytes read | compares |
  |---|---|---|---|---|
  | BASE | 100% | 40 | 12.5 KiB | 40 |
  | NEW | 94% | **518** | 71 KiB | 499 |

  Lead bytes 0xE6 + 0xE4 are 1.50% of the text, against 0xA5 at 0.37%.
- **Cause C.** The scan member moves from an exact continuation byte to a pair
  of lead bytes.
- **The design named this one too.** §2.3.3 "Accepted, stated: `bar(?i:x)`
  under `-e utf8` (NONE)", with the trigger "a measured utf8 cell where the
  pair scan loses to an adjacent exact byte". `alt-shared` is that cell.
- **Twin T2** (NEW's run and masked 4-byte verify, but the scan on the exact
  0xA5 at k* = 2, one stream), Mac, ns/B:

  | subject | deny | new | T2 |
  |---|---|---|---|
  | u8 64k | 0.0684 | 0.1525 | **0.0853** |
  | 256k | 0.0744 | 0.2138 | **0.0980** |
  | 1m | 0.1062 | 0.2467 | **0.1285** |

  T2 recovers 80-84%. The residual +0.017..+0.024 is cause B in small form:
  the longer run is found later, and the DFA rescans the span.

## 2. The short per-call cells' fixed entry term (union-srch, 75 subjects)

`union-select`'s run is `SELECT@4/dfdf…` (k* = 4, the pair arm on `C`/`c`),
and its set is empty. BASE has no pre-check at all. Gate counters (Mac,
deterministic) are joined to Linux's `c3.out` rows in `corr.py`, with its
output in `lx_union_srch.txt` plus `pc_mac.out`:

| gate work per call | cells | Linux NEW ns/call | Linux delta | REG / WIN |
|---|---|---|---|---|
| 0 `memchr` (n <= MAXK = 5: the loop never runs) | 15 | 3.3-8.1 | -0.9..-6.0 | 0 / 15 |
| 2 `memchr`, 0 compares (no `c`/`C`: both streams miss) | 43 | **10.04-10.11** on 39 of them | -44.0..+6.7 | 22 / 20 |
| 3 `memchr`, 1 compare (one failed candidate) | 5 | 14.5-14.95 | -1.9..+7.4 | 4 / 1 |
| 4-6 `memchr`, 2-4 compares | 6 | 19.5-34.4 | -17.5..+7.9 | 3 / 2 |
| gate PASSES (the subject holds `select`) | 4 (waf-concat, waf-comment-obfuscation, waf-union, waf-dbnames) | 18-80 | **+6.6..+11.0** | 4 / 0 |

- **The entry term is two fresh `memchr` calls.** It is not the masked
  compare's setup, and it is not an extra pass. On Linux glibc a rejecting
  gate costs a flat ~10.06 ns against ~3.3 ns with no loop at all, so the two
  calls cost ~6.8 ns together. BASE's DFA rejects a 6-11 B subject in
  6.2-7.7 ns, which gives the +2.4..+3.9 cluster.
- **Each failed candidate adds ~4.4 ns** (one `memchr` re-search plus a
  compare).
- **Where the gate passes, its cost is purely added**, and the DFA runs after
  it. That gives the four worst cells (+6.6..+11.0), each with a gate pass
  rate of 1.00.
- **The wins** are rejections of longer subjects that BASE's DFA scanned
  byte by byte (sec-github-pat 55.9 -> 11.9).
- **Mac does not reproduce the term.** Its BASE entry costs ~2x Linux's, and
  its libc `memchr` call is cheaper, so on the Mac nearly every rejecting cell
  WINS. Only the gate-pass and multi-candidate cells regress (+1.3..+5.3). The
  term is a glibc-call-cost fact; read it on Linux.
- **Two Linux cells are not explained.** `v-us-zip-plus4` (+5.8) and
  `la-email-dotdot` (+6.7) take 2 `memchr` calls, never pass, and read 22-25
  ns where their siblings read 10.06. Their BASE is also high (16-18 ns
  against ~7 for their length), so it is something about the subject on that
  box, perhaps a glibc page-cross path. It needs a light Linux probe; it is
  not diagnosed here.
- **The fix below does not move this term.** `union-select` keeps its run
  (25.9 prior bits, empty set: row R2). A remedy would be its own row, for
  example a subject-length knee in front of the pair arm or searching the
  rarer stream first. D77 applies: its trigger is a ruling that the net
  -127 ns is not enough.

## 3. Mac directional confirmation (all cells, ns/B, deny -> new)

| cell | subject | deny | new | Linux sign |
|---|---|---|---|---|
| userpass | cap 64k / 1m | 0.0198 / 0.0229 | 0.639 / 0.725 | REG (same) |
| mod-i / mod-r | syn 64k | 0.747 / 0.748 | 1.504 / 1.503 | REG |
| cls-fold-pair / cls-pair-ctl | syn 64k | 0.581 / 0.575 | 1.182 / 1.210 | REG |
| ci-strasse | u8 64k | 0.526 | 0.610 | REG |
| alt-shared | u8 64k | 0.0681 | 0.1518 | REG |
| union-caps (customer) | cap 64k / 1m | 0.564 / 0.599 | 0.268 / 0.423 | WIN (same) |
| ci-ascii-ctl (customer) | u8 64k | 0.525 | 0.211 | WIN |

All nine signs agree with Linux. The twins T1 and T2 are in §1.

## 4. Fix proposal (for a later build lane, after Frank's ruling)

### 4.1 Where it lives

The regressions are an EMISSION decision, the pre-check's. They are not a
fact defect.
- The run FACT is right: `USER`, `CAT` and `cAt` are necessary.
- The fact has other consumers: the pin, `dfa_pfs[]`'s `run-pinned` rows, and
  G1. A uniform rate-priced floor on the fact would decline 26 EXACT bench
  runs, mostly `run-pinned` prefilters (`lit-cat`, `mod-n`, `grp-*`,
  `esc-hex`; `census.out`), which is a regression waiting to happen.

So the fix goes in `req_admit` (P7, `src/gen/emit_dfa.c:6548`). That is
[OPT-PRECHECK-ADMIT]'s cost-admission derivation, and it is today an if-chain
of three declines. It becomes a first-match predicate-row table (`DFA_SELECT`
shape, `dfa_pfs[]` idiom). Each row says WHICH pre-check is emitted, or why
none is. The fact, the stamps `REQ_BYTE`/`REQ_RUN` and the pin are unchanged.

### 4.2 The table

| # | row | predicate | pre-check emitted | `REQ_WHY` |
|---|---|---|---|---|
| 1 | `none` | no byte and no run | none | `none` |
| 2 | `one-attempt` | G2 (unchanged) | none | `one-attempt` |
| 3 | `run-common` (NEW) | a run shipped, and its information UNDER THE RATE is `< PCREC_MIN_REQ_RUN_BITS`. That information is `Σ -log2(cube_mass(T_i, K_i))`, MASS's per-position cube mass, the same member sum the pick uses | the run block is declined. The candidate becomes the SET pick's one-byte `memchr`, which goes through rows 5-6 (or none if the set is empty) | `common` (NEW token) when nothing is emitted, otherwise per rows 5-6 |
| 4 | `set-leads` (NEW) | a run is admitted, the set is non-empty, and the set pick's mass is `<` the run's scan-member cube mass | `memchr(set pick)` and THEN the run block, cheapest first | `emitted` |
| 5 | `dominated` | G1 (unchanged) over the selected candidate | none | `dominated` |
| 6 | `emitted` | always | the candidate | `emitted` |

Rows 3 and 4 are numbered for exposition. The build lane places them before
G1 so that G1 asks about the candidate they select. The order is the answer,
as in `dfa_pfs[]`.

**Row 3 is general, not masked-only, and its unit is not new.**
- It asks "is this run expected to be ABSENT from a 64 KiB window". 16 bits
  of rate-priced information is an occurrence rate of 2^-16 per byte.
  Rejection is the only way a pre-check pays (§1.B).
- **Under NONE it reproduces today exactly.** The uniform mass of a
  2^(8-p)-member cube is `2^(8-p)/256`, so `-log2` is `p = popcount(K)`. That
  is today's number, and NONE compiles (every `-e utf8` artifact) stay
  byte-identical.
- It reuses the existing knee `PCREC_MIN_REQ_RUN_BITS` (16, "bits"). No new
  constant enters (D141).
- It applies to EXACT runs too, and it should:
  - Row 3 moves only artifacts that are `emitted` today. A `dominated` or
    `one-attempt` exact run keeps its program, because its fallback byte is
    the same or is dominated.
  - Measured on the Mac with the gate deleted, against the gate kept,
    exact-run pre-checks with low prior information cost today what C3's
    movers cost:
    - `stack-frame` (`at `, 11.3 bits): log 64k-fail 0.347 -> 0.252,
      1024k-hit 1.197 -> 0.646 ns/B.
    - `asr-nwb` (`cat`, 14.0 bits): syn 64k 0.994 -> 0.844.
    - `cls-s-lc` and `qnt-plus-ctl`: null.
  - With row 3's real fallback (`memchr('(')`, the set pick), `stack-frame`
    lands on the no-gate number (0.256 / 0.458 / 0.651).
  - So K82 is partly a pre-existing exact-run defect that C3 widened, not a
    C3-only one.

**Row 4 is the "not built" item of §2.3.3, now triggered.**
- Under NONE: the set pick's mass is 1/256 and an exact scan member's is also
  1/256, so an exact run never moves. A pair (2/256) with a non-empty set
  moves to set-leads.
- Under `byte`: it moves wherever the set holds a byte rarer than the run's
  scan byte.

**Cause C's cure is in the PICK primitive, not in the table.**
`pcrec_find_pick`'s NONE answer changes from "`rightmost`, whatever the
candidates' sizes" to "argmin of the UNIFORM mass (cardinality), ties to
`rightmost`".
- This is MASS's own NONE answer (cardinality), applied inside the primitive.
  No reader tests the rate, so D126 Q4's ban on reader-side NONE rules holds.
- It keeps "ties to rightmost", which was D126 Q4's actual objection to a
  uniform table (`cand[0]` = leftmost).
- Every all-exact candidate list ties, so it is unchanged (set pick, pin).
- It does reverse §2.3.3's "accepted, stated" sentence, and that is Frank's
  call.

### 4.3 Predicted movers (bench compile-facts census, `census.py`, Mac; the corpus census is OWED to the build lane)

| row | bench artifacts that move | predicted direction |
|---|---|---|
| 3, masked | mod-i, mod-r, cls-fold-pair, cls-pair-ctl | **back to BASE's program.** `mod-*`: the set is empty, so no pre-check, as DENY. `cls-*`: the fallback `memchr('c')` is G1-dominated by the prefilter, as BASE. DENY's measured timings are the prediction (Linux: -0.32..-0.70 ns/B) |
| 3, exact `emitted` | sfx-64/256/512, stack-frame, asr-nwb, asr-wb, cls-n-uc, cls-s-lc, qnt-plus-ctl, qnt-poss-plus (10) | favourable or null on the four measured (above). The other six need alpha cells. `stack-frame` was C3's CONTROL, so the build lane needs a new control |
| 4 | userpass (masked); stack-frame, cls-h, cls-n-uc, cls-s-lc, cls-v, mod-s (exact, `byte` rate: set pick rarer than the run's scan byte; stack-frame/cls-n-uc/cls-s-lc also hit row 3 first) | userpass **= BASE** (T1, -0.6..-0.7 ns/B Mac, -0.92 Linux predicted). Exact: a bounded-cost `memchr` in front, unmeasured |
| PICK NONE | alt-shared (of the 3 bench NONE masked runs; ci-ascii-ctl and ci-strasse have all-pair windows, so they tie and stay on the rightmost) | T2: -0.07..-0.12 ns/B Mac, a residual of +0.02 against BASE |
| none | **ci-strasse stays a mover** (+0.08..+0.10 ns/B Linux) | see 4.4 |

### 4.4 What it does to C3's customers

| customer | rate-priced information | set | row | change |
|---|---|---|---|---|
| union-select | 25.9 bits | empty | 6 | unchanged, the win is kept |
| slack-webhook | 72.7 bits | non-empty, but the run's scan member is rarer | 6 | unchanged |
| http-5xx | 81.3 bits | non-empty, but the run's scan member is rarer | 6 | unchanged |
| ci-ascii-ctl | NONE: 21 popcount bits (16.2 if it were priced) | - | 6 | unchanged |

- Union-select's short per-call term (§2) is untouched.
- **The margin on the low side is thin.** Priced by the rate, the movers sit at
  12.5-13.9 bits and ci-ascii-ctl at 16.2. The knee was ruled in popcount
  units, so reusing it in rate units is a claim the alpha must check.
- **`ci-strasse` and `ci-ascii-ctl` are the same shape under NONE** (three
  caseless ASCII letters, 21 bits). No rule without a rate can separate a run
  that is present in the text from one that is absent. `ci-strasse` therefore
  stays a small mover, by construction, unless `-e utf8` gets a byte-rate.
  That is D123-4/5's ruled byte-only default, and it is not proposed here.

### 4.5 abi

**Yes, this is an abi event (59 -> 60).** It moves the emitted PROGRAM TEXT
and `REQ_WHY` stamp values on a population, which is [OPT-PRECHECK-ADMIT]'s
own abi-31 precedent ("moves a STAMP VALUE … and the emitted PROGRAM TEXT").
Row 3 also adds a fifth token to `REQ_WHY`'s closed four-token set. That is a
contract hunk in `match_api.md` §6.3 (the token table) and `tuning.md` §2.29,
plus a re-pin of every reader found by grep (D76/D94). The PICK NONE change
moves `REQ_RUN`'s `@idx` and `REQ_BYTE` on NONE masked runs (`alt-shared`:
`@3/…` -> `@2/…`, `230` -> `165`). Deny: bit 44 still restores abi 58's
program. Whether rows 3 and 4 get their own deny bit is the build lane's
D144/house call.

## 5. Keep C3 on, or flip it off? (facts for Frank's ruling)

- **Size in absolute ns/B (Linux):**
  - Losses: userpass +0.93, mod-i/mod-r +0.65 each, cls-* +0.37 each,
    alt-shared +0.10, ci-strasse +0.09. That is about 3.2 summed.
  - Wins: union-nocaps/caps -0.45 each, ci-ascii-ctl -0.47, slack/http
    -0.001..-0.004. That is about 1.4 summed.
  - Per call: a net -127 ns over 73 short cells.
- **Shape:** union-select is a production WAF rule. userpass is a production
  secrets rule. Four of the seven losers are synthetic syntax probes over
  match-dense text.
- **Cure cost:** userpass's +0.93 is removed by one row (T1 = BASE to four
  digits). The four syn losers return to BASE's program under row 3. Flipping
  bit 44 off by default would also forfeit the two customer wins.

**One line:** keep C3 default-on if the R3/R4 fix is round 2's FIRST build
(the worst loss has a measured one-row cure); flip it off if that build is
not next, because userpass's +0.93 ns/B on a production-shaped pattern
outweighs union-select's -0.45.

## 6. Instruments and reproduction (`docs/dev/optloop/s4/k82diag/`)

- `gen.py` is `alpha_c3.sh`'s subject generator, lifted verbatim. It wrote
  into a scratch dir, and every subject was sha256-OK against the bench
  manifests. pcrec-bench was read only.
- `cnt_pre.h` and `mk.sh` build the gate-counting twin of an artifact
  (`art/<cell>/{new,deny}` -> `cnt`/`cntd`).
- `tm.sh` runs the 3-launch median timer over arms.
- `pc.sh` and `corr.py` produce the per-call table. Their transcripts are
  `pc_mac.out` and `lx_union_srch.txt` (Linux `c3.out`'s union-srch rows,
  copied by one read-only `ssh grep`).
- `census.py` and `census.out` are the rate-priced information census and the
  row-4 census over the 345 bench exports (`PCREC`, `BENCH` from the
  environment).
- The twins T1 and T2, and the `nogate`/`fb` arms, are one-line `sed`/python
  edits of the NEW artifact, as described in §1 and §4.2. Scratch artifacts
  were not committed.

Owed (to the build lane, not this one): the corpus census of rows 3, 4 and
PICK-NONE; Linux alpha cells for the 10 exact row-3 movers and the 6 row-4
exact movers; a new byte-identical control in place of `stack-frame`; the two
unexplained Linux per-call cells.
