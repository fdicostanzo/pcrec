# rlhbuild — [REQ-HANDOFF-L1] BUILT: the K82 handoff generalized to any landmark, entered and re-entered

**Lane `rlhbuild`, 2026-10-11, opus.** Branch `lane/rlhbuild` from main `48343196`
(abi 74). ONE merge, ONE abi event (74 -> 75). Charter: plan.md `[REQ-HANDOFF-L1]` as
ruled (Q1 build the row family, Q2 one deny, Q3 rev-inner held, Q4 R-15 filed;
Frank's K-admission ceiling; the two-landmark UNLOCK is NOT built), scoped by
`docs/dev/lanes/rlhtwin_report.md`, generalizing the EXISTING K82 handoff
(`docs/design/litscan_k82h.md`) rather than adding a parallel mechanism.
Measurement instruments: `docs/dev/optloop/rlhbuild/` (own `CLAUDE.md`).

## 0. Answers first (resume from here)

1. **Built as ruled, in the existing first-match table.** (1) The no-mover fact:
   per-member set offsets on the run walk's own rules (`RbSet.off`, core row
   `req_set_maxoff`) and the LANDMARK's K (`req_landmark_maxoff`: the run
   window's K where a run ships, else the `req_byte` member's). (2) ENTRY: FIRST's
   `handoff` row reads the landmark K for length 1..n; the one-byte gate ASSIGNs
   its position (same row, same `RX_REQ_HANDOFF` = K vocabulary, deny
   `-fno-req-handoff`). (3) RE-ENTRY: a NEXT-slot row `handoff` (identity
   `handoff-reentry`, map `CM_LOWERBOUND`, `CR_DFA`) between the exact-start rows
   (`run-pinned*`/`offset-set*`) and the start-byte rows; at each restart of the
   forward scan (start state, no accept pending) it re-asks the SAME pre-check
   site (a second `mf_use` of the PRE handle) from `scan_position`, reuses the
   kept hit while it is still ahead, answers NOMATCH on a miss, and moves to
   `c - K` where that is ahead, rounded up under utf8 and re-seeded where the
   machine seeds. Denied by the same `-fno-req-handoff` (listed on the
   `prefilter` axis with that deny). No new flag bit. (4) K ADMISSION, derived (§1.4).
2. **One structural finding the brief did not anticipate: the re-entry closes a
   cycle in the start table's selection reads** (NEXT reads FIRST, FIRST reads
   PRESENCE, PRESENCE's G1 reads NEXT). Resolved in the table's own vocabulary,
   not by a special case: a selection READ can be made UNDER deny bits
   (`CandNode.under`), and G1 asks NEXT for the scan the artifact carries
   WITHOUT the handoff (a row that re-uses the pre-check cannot dominate it);
   the slot that reads FIRST declares which rows read it (`CandNode.by`), and the
   self-check follows a read only where the gathered deny bits do not remove its
   readers. Fixed point: G1 dominated -> no pre-check -> no handoff -> NEXT takes
   the start-byte row G1 saw; not dominated -> the re-entry may apply. S810/S812
   are the mechanism's own sabotage rows. §1.3.
3. **The K admission is derived, with no constant of its own**: the re-entry's
   expected jump `1/h - K` (h the landmark's hit rate under the byte-rate prior;
   a run's is the product of its positions') against the displaced start-byte
   row's expected skip `1/m` (m the mass of the set it scans; 1 where it scans
   nothing): admit iff `1/h - K > 1/m`. With no start-byte row this is `K*h < 1`,
   the mean gap clearing K. A first cut admitted on `K*h < 1` alone and
   displaced the DFA hat on its own witnesses (`(?:\b|xy)a`, `\b(?:true|false)\b`:
   'a'/'e' are common); the comparison against the row it replaces is the same
   prior's reading and keeps them. That the mean-gap point is where the jump
   stops PAYING in time is UNMEASURED (bench). It is the FOURTH member of the
   prior-cost family (G1's `req_byte_dominated_by`, `set-leads`'s
   `pcrec_find_pick`, R4's `cand_rs_dense_applies`): a unification candidate
   (memory `pcrec-forest-for-trees`), filed in §7, not built.
4. **Identity**: 0 differing lines against main, against `-fno-req-handoff` and
   against libpcre2-8 10.46 on all eight cells (ipv6, ipv4, dotted4, sfx-64,
   kv-quoted and the three K-admission cells; find-all + every startpos, 3,882
   subjects, 1.15M startpos searches); `tests/litscan/handoff.rxt` grows 24
   oracled blocks (python3 `re` AND libpcre2 must agree on byte blocks) and
   passes under the lane's build. §3.
5. **Timing and the R-15 delta (§5, scratch tier): DO NOT MERGE AHEAD OF
   R-15.** With the byte gate as a `memchr` ASSIGN (the scratch twin `newm`,
   what R-15's row renders) the build reproduces rlhtwin's win: throughput
   ipv6 x0.305, ipv4 x0.196, sfx-64 x0.068, kv-quoted x1.007, dotted4 and the
   landmark-absent subjects at parity. Through TODAY's generic kit loop (the
   build as committed) the same re-entry gives most of it back (ipv6 x0.571,
   ipv4 x0.877 with six of twelve subjects up to x1.43 SLOWER than main), and
   every landmark-ABSENT subject regresses x35-x53 against main's one discard
   `memchr` (dotted4 over its own throughput texts; hcolon/hcolon_in over z
   text). The R-15 delta (generic over memchr): x1.87 / x4.48 / x46 on
   ipv6 / ipv4 / dotted4 throughput.
6. **Validation**: the full chain is ARMED, not run, at hand-back (§6): make,
   make strict, FULL make test, make test-axes, mech S805-S814 (+ the re-aimed
   rows), emit_sweep start-arm floors, make test-spec-history. The sections I
   ran solo while fixing are listed in §6 with their verdicts.
7. **A cost the kit row R-15 removes**: every byte-landmark artifact's ENTRY gate
   is now the kit's GENERIC ASSIGN loop (a byte-at-a-time statement expression)
   where it was a discard `memchr`; `RX_MEMFN_LIBC` drops `memchr` on the
   movers whose only memchr it was (bench: dotted4, ipv4, ipv6,
   qnt-poss-brace), and the code grows ~570 B per gate (the size-term rescue
   witness, §2.3). The re-entered gate is the same text. §5 measures it, and
   answer 5 is what it costs.

## 1. Design as built

### 1.1 The fact (no mover; its own checks)

`src/facts/req.c`: `RbSet` gains `uint32_t off[256]` (32-bit, saturating at
`RB_OFF_UNBOUNDED`, published as `PCREC_W_UNBOUNDED`; 1 KiB per set rather than
`long long`'s 2 KiB because the walk recurses per paren level, depth 250). The
run walk's offset rules, applied to the set: `rb_union(l, r, maxw(l))` stores a
member only `r` carries at `maxw(l) + off_r` and keeps the NEARER of two
occurrences for a member both carry; `rb_intersect` keeps the FARTHER branch;
every width-only arm (a multi-member class, a min-0 repeat, a backreference/
variable/call) is a pure shift through `rb_union(rb_empty(), acc, w)`; a
`{m>=1,}` repeat keeps the body's FIRST-iteration offsets. Published as:

| fact | kind | value | owner |
|---|---|---|---|
| `req_set_maxoff` | E2 core, deny `-fno-req-byte` | `byte:K` per member, ascending (`byte:unbounded`) | req.c |
| `req_landmark_maxoff` | E2 derived, depends `req_set_maxoff req_run_maxoff req_byte` | the run window's K where a run shipped, else the byte's; `unbounded`/`none` | req.c |

`req_set`'s own value text is unchanged (it renders a stamp reader). Checks that
share no source with the walk: run_prechecks.sh §5.12a's HAND K table gains seven
byte-landmark rows derived from the pattern text (dotted4 3, ipv6-shaped 4,
`a.?b` 2, `(?:ab|c):` 2 from the wider branch, utf8 `.{1,3}:` 12, `\w+:`
unbounded, `[a-y]\d{0,150}:` 151), and the answer cells of handoff.rxt (an
understated K moves answers there at K = 0). spec: `facts_listing.md` §4.1.2¶8a/¶8b;
`tuning.md` §2.27¶5 (the fact deny's "facts emptied" line).

### 1.2 The ENTRY (FIRST's `handoff`, generalized)

`req_handoff_applies` drops `len >= 2` and reads `req_landmark_maxoff`; the
pre-check site's byte arm (`req_site_define`) keeps its position (`ret_pred` the
byte's predicate, `MF_H_ASSIGN`) whenever FIRST is `handoff`; the internal check
reads `nrun > 1 || nrest != 0`; `pcrec_emit_req_byte_check`'s start site reads
the handoff for either needle; `emit_req_handoff_rest` subtracts the landmark's
K (its comment names "run window" for a run, "landmark byte" for a byte, so no
run artifact's comment moves). `RX_REQ_HANDOFF` carries K as before. Bench
movers of the entry stamp: 6 (dotted4, ipv4, ipv6, grp-atomic-alt, qnt-poss-brace,
utf8/cls-s-ucp), §2.

### 1.3 The RE-ENTRY (NEXT's `handoff`) and the selection cycle

The row (`cand_rows[]`, after `offset-set`):
`{ "handoff-reentry", PCREC_NO_REQ_HANDOFF, pf_handoff_applies }`, slot NEXT,
routes `CR_DFA`, tok `handoff`, map `CM_LOWERBOUND`, hands `CT_LOWER`, listed as
`prefilter` order 5 (the start-byte rows move 5..12 -> 6..13), payload
`{ .emit = pf_emit_handoff, .reseeds = true, .scan = PF_SCAN_LANDMARK }`
(a new `PfScan` value: a lower bound, never a candidate byte, so no reader
prices it as one). VERIFIER's `accepts` gains `CT_LOWER` (the forward machine is
an unanchored scan; a lower bound is a valid entry).

Predicate `pf_handoff_applies`, cheapest first: the forward machine of the
caller-facing body (`cand_finish_of != VM`: never inside a VM hybrid's
prefilter, whose retries are RETRY's), FIRST's selection READ (`req_use_read`,
through `cand_read` with FIRST's site) is `handoff` (so the pre-check is emitted,
its site keeps the position, K is finite: FIRST's conjuncts are read, never
restated), and the K admission (§1.4).

Emission (`pf_emit_handoff`, inside the shared `pf_open`/`pf_close` so the
`landing` record works unchanged):

```c
        if (forward_state == S0 && last_accept_position == (size_t)-1) {
            if (landmark_position < scan_position) {
                landmark_position = <the PRE site's text, lo = scan_position>;   /* kit; miss: return 0; */
            }
            if (landmark_position - scan_position > K) {
                scan_position = landmark_position - K;
                <utf8 only: round up to a character start>
                <seeded only: forward_state = scan_position ? seed[class[s[pos-1]]] : s0;>
            }
        }
```

and the entry keeps the hit before its subtraction
(`size_t landmark_position = handoff_position;`, emitted only where the re-entry
is selected, `req_reentered`). The kit's second use is `emit_req_reentry_use`
(same handle, hooks `lo = scan_position`, `result = landmark_position`, no
declaration, `on_miss` `return 0;`) — R-15's Q-R15-1 option (a): one fact, one
site.

SOUNDNESS (the entry's proof re-applied): the block runs only at the start
state with no accept pending. On an UNSEEDED machine that is literally a fresh
call from `scan_position` (the initializer gives the start state at any
startpos), so Claims 1-3 of litscan_k82h.md §1.2 apply with `f = scan_position`;
the reverse pass keeps its `search_from` floor, which is sound for the reason
§1.2's last note gives. On a SEEDED machine the start state can carry an
in-flight thread whose future it subsumes (`(?:\b|xy)a`); every completion of
such a thread is in the start state's future, every string of which holds the
landmark within K of some suffix's start, so a completion whose suffix starts AT
`scan_position` (the fake-context case) has its landmark in
`[scan_position, scan_position + K]`, the jump test `c - scan_position > K` is
false, and nothing moves; a completion whose suffix starts later is a real match
starting at or after `c - K` (Claim 1). The move re-seeds from the byte before
the landing (the jumped bytes begin no match), only where it moved. The scan
position never decreases, so the work is linear for every K.

THE CYCLE (finding 2): the predicate reads FIRST; FIRST reads PRESENCE; G1
(PRESENCE `dominated`) reads NEXT. Unbroken, every selection of NEXT recursed.
`CandNode` gains `under[slot]` (deny bits a read is made under; `cand_read`
ORs them in) and `by[slot]` (deny bits every row making the read carries).
PRESENCE `.under[NEXT] = PCREC_NO_REQ_HANDOFF`; NEXT `.reads[FIRST] = CR_DFA`,
`.by[FIRST] = PCREC_NO_REQ_HANDOFF`. The trace build's cycle check is now a
bounded DFS carrying the gathered bits (`cand_read_reaches`). The admission's
own read of "the row below me" is the same deny used on its own slot
(`cand_select(NEXT, s, flags | PCREC_NO_REQ_HANDOFF)`), not a cross-slot read.

### 1.4 The K admission (`req_landmark_admits`)

`h = req_landmark_hit_ppm` (the byte's mass, or the product over a run window's
positions, ceil at each step), `m = pcrec_find_set_mass` of the set the row
below scans (`PF_SCAN_BYTE`/`SET`, via `pf_scan_set_of`; 1,000,000 where that
row is `none`). Admit iff `h == 0`, or `K*h < 10^6` and
`(10^6 - K*h) * m > 10^6 * h` (i.e. `1/h - K > 1/m`). Under no byte-rate (utf8)
the masses are cardinality's, inside the primitive. Hand cells (run_prechecks
§5.12m): `[a-y]\d{0,100}:` re-enters, `[a-y]\d{0,150}:` does not (its ENTRY still
hands off at 151), Frank's `a.{1,50000}z` takes no handoff at all (a
count-collapsed hybrid, Q10) and keeps its memchr. A DFA-route hostile cell where
the admission itself declines is `[a-y]\d{0,150}:` over colon-dense text.

### 1.5 What else moved, by grep, and why

| reader | change |
|---|---|
| `PCREC_ARTIFACT_ABI` 74 -> 75 | `src/gen/emit_dfa.c:54`; `match_api.md` §1 (guard block x3), §6¶17, the `abi` row of §6's table; `run_codegen_tests.sh` `ABI_EXPECT` + ledger; `abi_changelog.md` new top entry; S693 re-aimed; the identity gate's (B) FILEPIN self-pinned (§6) |
| `RX_DFA_PREFILTER` value `"handoff"` | `match_api.md` §6.3.4's value table; `run_dfa_stamps.sh` `PF_VALUES`, the text marker and a witness |
| `RX_REQ_HANDOFF` for a byte | `match_api.md` §6.3.7¶10-11; `tuning.md` §2.41¶1/¶3/¶5/¶8a/¶9 and its inventory row |
| start-set rank | `tuning.md` §2.42¶4 names the re-entry above the hat rows |
| `--list-axes` | `prefilter` gains `handoff` (order 5) with the handoff's deny: axes registry check 226 -> 229 |
| the start-set suites | `dfahat_checks.py` and `census_s1.py` deny the handoff on BOTH arms (the hat is measured against today's plain row exactly as before; the interplay is §5.12l-q's); manifests re-pinned (only handoff.rxt rows moved) |

## 2. Movers

### 2.1 Bench (compile-only, `census.sh` -> `census.tsv`; 367 patterns, 24 refused by main)

16 artifacts move: 14 re-enter (`RX_DFA_PREFILTER "handoff"`) and 6 change
`RX_REQ_HANDOFF` (2 of them only that):

| pattern | handoff base -> new | prefilter base -> new | libc base -> new |
|---|---|---|---|
| loglines/ipv6 | none -> 4 | byte-class -> handoff | memchr -> none |
| loglines/ipv4 | none -> 3 | byte-class -> handoff | memchr -> none |
| bounded/dotted4 | none -> 3 | byte-class -> handoff | memchr -> none |
| syntax/qnt-poss-brace | none -> 2 | memchr -> handoff | memchr -> none |
| syntax/grp-atomic-alt (VM hybrid) | none -> 2 | memchr (prefilter body, unchanged) | memchr |
| utf8/cls-s-ucp | none -> 4 | memchr (unchanged) | memchr |
| altwide/sfx-64, -256, -512 | 9 | byte-class -> handoff | memchr |
| loglines/kv-quoted | 32 | first-class-bounded -> handoff | memchr,memcmp |
| syntax/cls-fold-pair, cls-pair-ctl | 0 | memchr -> handoff | memchr |
| syntax/mod-i, mod-r | 0 | byte-class -> handoff | memchr |
| utf8/ci-ascii-control, ci-strasse | 0 / 2 | byte-class -> handoff | memchr |

### 2.2 Corpus

run_prechecks §5.12 (its population, 168 patterns): 67 handoff movers (39 with
K > 0); §5.12l (its population, 8 files): 28 re-entering, floor 22. The DFA
stamp census (`run_dfa_stamps.sh`) agrees stamp-to-text on every artifact.

### 2.3 Size

The byte gate's generic ASSIGN text is ~570 B larger than the discard memchr
(measured on the size-term rescue witness `(?:aa|a){8,12}+b`, a VM hybrid whose
`b` is now a handed-off byte landmark: +571 B at every unroll K; its reference
cap re-calibrated 32,300 -> 33,200 with the arithmetic in the script). R-15's
`memchr` ASSIGN row removes this.

## 3. Identity

`ident.sh` -> `ident.txt` (etdrv `ident`: one find-all pass + a search from every
startpos per subject, hashed; base = main 48343196):

| cell | subjects | find-all matches | startpos hits/searches | base vs new | vs deny | vs newm | vs libpcre2 |
|---|---|---|---|---|---|---|---|
| ipv6 | 524 | 3,193 | 88,701/287,464 | 0 | 0 | 0 | 0 |
| ipv4 | 524 | 2,716 | 72,851/271,336 | 0 | 0 | 0 | 0 |
| dotted4 | 454 | 2,334 | 50,028/84,120 | 0 | 0 | 0 | 0 |
| sfx64 | 444 | 1,490 | 32,327/48,110 | 0 | 0 | 0 | 0 |
| kvq | 524 | 1,632 | 45,919/250,279 | 0 | 0 | 0 | 0 |
| hostile `a.{1,50000}z` | 204 | 103 | 23,263/47,376 | 0 | 0 | 0 | 0 |
| hcolon `[a-y]\d{0,150}:` | 204 | 10,766 | 22,773/47,376 | 0 | 0 | 0 | 0 |
| hcolon_in `[a-y]\d{0,100}:` | 204 | 10,766 | 22,773/47,376 | 0 | 0 | 0 | 0 |

Subjects: each cell's bench short + throughput subjects (regenerated in a
`git archive` copy of pcrec-bench d359564f) + 400 adversarial (rlhtwin's
generator for ipv6/ipv4/dotted4, et1twin's for kvq/sfx64) or gen_hostile.py's.
(Measured on the first-cut admission's build; the final compiler emits these
eight artifacts identical but for the two abi digits, diffed, so the result
stands for the final build.)

handoff.rxt: 48 cases x 2 routes, `gen_handoff.py --check-pcrec` 0 mismatches;
the harness on it reads `cases failed: 0`. The answer-identity sweep over the
whole corpus against `-fno-req-handoff` is `make test-axes`'s (OWED, §6).

## 4. Sabotage

S805-S814 (allocated), all anchors count 1 and every REACH probe reaching on the
lane's build; verdicts OWED from the chain's mech run (§6):

| row | plant | detector |
|---|---|---|
| S805 | the set offsets lose the left factor's width (K = 0 on dotted4) | handoff.rxt answers; §5.12a |
| S806 | an alternation's member keeps the NEARER branch | §5.12a (`(?:ab|c):` 2 -> 1; K-1 is equivalent on answers) |
| S807 | a min-0 repeat does not shift the set | §5.12a (`a.?b` 2 -> 1) |
| S808 | the re-entry re-asks from `scan_position + 1` (a LATER occurrence) | handoff.rxt |
| S809 | the re-entry jumps to the landmark itself (K = 0) | handoff.rxt |
| S810 | `cand_read` ignores `under`: G1 re-enters FIRST/PRESENCE (unbounded recursion) | prechecks (every compile with a pre-check) |
| S811 | the K admission always admits (THE ADMISSION CEILING) | §5.12m |
| S812 | the self-check ignores `by` (`table-read-cycle`) | candoracle |
| S813 | the re-entry does not re-seed (THE RE-ENTRY SEEDING) | handoff.rxt `\b\d{1,3}\.\d` on "1.x 1234.5 1.2"; §5.12n |
| S814 | the re-entry does not round up under utf8 | §5.12o; handoff.rxt utf8 |

Re-aimed (intent re-verified): S446, S460, S463, S606, S693. Reach re-pointed:
S265 (`a.*?b`), S280, S282, S283, S610. Every row's reach probe was re-run on
the lane's build against main's: no row stops reaching.

## 5. Timing, and the R-15 delta (SCRATCH TIER)

`time.sh` (et1twin's/rlhtwin's method): `taskset -c 7`, the four C variants
interleaved per subject, 3 rounds, each line etdrv's median of 5 batches of
>= 40 ms, the table the median over rounds; raw `times.tsv` (throughput) and
`times_short.tsv` (search_short), reading `times_summary.txt` /
`times_short_summary.txt`. load1 ~0.5-1.0 throughout (no other heavy run of
mine; the box was otherwise idle by `/proc/loadavg`). Every variant's match
count equals base's on every subject line. `base` = main 48343196; `new` =
the lane as built (the byte gate is the kit's GENERIC loop at the entry AND the
re-entry); `deny` = the lane under `-fno-req-handoff`; `newm` = `new` with both
byte-gate sites hand-edited to a libc `memchr` ASSIGN (`mkmemchr.py`, SCRATCH,
NOT the lane's text: what R-15's row would render). Run landmarks (sfx64, kvq)
have no generic loop, so `newm` = `new` there.

### 5.1 Throughput (find-all over each cell's throughput subjects)

| cell | n | new/base | newm/base | deny/base | **new/newm (the R-15 delta)** | per-subject new/base | per-subject newm/base |
|---|---|---|---|---|---|---|---|
| loglines/ipv6 | 12 | 0.571 | **0.305** | 1.000 | **1.87** | 0.551-0.730 | 0.260-0.345 |
| loglines/ipv4 | 12 | 0.877 | **0.196** | 0.996 | **4.48** | 0.685-**1.429** | 0.060-0.342 |
| bounded/dotted4 | 5 | **46.4** | 1.003 | 1.000 | **46.3** | 35.4-52.8 | 1.000-1.005 |
| altwide/sfx-64 | 4 | **0.068** | 0.068 | 1.166 | 1.00 | 0.059-0.120 | same |
| loglines/kv-quoted | 12 | 1.012 | 1.007 | **13.78** | 1.00 | 0.998-1.015 | same |
| hostile `a.{1,50000}z` | 6 | 1.000 | 1.001 | 1.001 | 1.00 | 0.996-1.002 | same |
| hcolon `[a-y]\d{0,150}:` (re-entry declined) | 6 | 1.217 | 1.134 | 1.002 | 1.07 | 1.07-1.14 colon / **35-46** z | 1.13-1.25 colon / 1.00 z |
| hcolon_in `[a-y]\d{0,100}:` (re-entry admitted) | 6 | 1.537 | 1.501 | 1.000 | 1.02 | 1.26-1.49 colon / **35-46** z | 1.47-1.52 colon / 1.00 z |

Reading, in order of consequence:

1. **The re-entry delivers rlhtwin's win when the gate is memchr, and gives
   most of it back through the generic loop.** ipv6 0.305 (rlhtwin's h2: 0.334),
   ipv4 0.196 (h2: 0.196), sfx-64 0.068 (h2: 0.068, a run landmark, no generic
   loop). Through today's generic ASSIGN loop: ipv6 0.571, ipv4 0.877 with SIX
   of twelve subjects slower than main (up to x1.43 on the syslog subjects,
   whose `.` landmarks are dense and dead), because the re-entry re-asks the
   gate once per restart and each ask is a byte-at-a-time loop.
2. **A LANDMARK-ABSENT subject is a regression of x35-x53 through the generic
   loop**: dotted4 over letters/digits text (no `.`), and hcolon/hcolon_in over
   z text (no `:`). Main rejected these calls with ONE discard `memchr`
   (~0.02 ns/B); the build's entry gate is the generic loop over the whole
   window (~1 B/cycle). `newm` is at parity (1.000-1.006). This is not the
   re-entry's cost: hcolon declines the re-entry and pays it at the ENTRY.
   **The build must not land on main ahead of R-15's memchr ASSIGN row** (or an
   equivalent kit rendering of the one-member ASSIGN gate), or every
   byte-landmark artifact (bench: dotted4, ipv4, ipv6, qnt-poss-brace,
   grp-atomic-alt, cls-s-ucp) regresses on landmark-sparse subjects. R-15's
   own §4 sequencing (the kit row first at zero movers, L1's merge the one abi
   event) is exactly the order that avoids it.
3. **kv-quoted: the re-entry costs +1.2%** (rlhtwin measured +1.3%), and the
   entry handoff it keeps is worth x11-x19 on the hit subjects (`deny`/base:
   `-fno-req-handoff` now removes the entry too, so the deny arm is the
   no-handoff artifact, slower than main on exactly the subjects K82 cured).
4. **The K admission behaves as derived and the hostile cells stay linear.**
   Frank's `a.{1,50000}z` takes no handoff at all (a count-collapsed hybrid,
   Q10) and is unchanged (1.000 on z-dense text, 4 KiB-1 MiB, ns/B flat).
   `[a-y]\d{0,150}:` declines the re-entry; `[a-y]\d{0,100}:` admits it, and
   over COLON-DENSE text (which contradicts the prior that admitted it) it
   costs x1.47-1.52 against main, flat in n (linear: the scan never moves
   back). That is the prior being wrong about the subject, not a K blow-up;
   the admission's job is K against the prior's gap, and the bench's text is
   the test of whether the prior's gap is right.
5. hcolon's ENTRY-only handoff costs +13% even through memchr on colon-dense
   text (1.13-1.25): a find-all call per match pays the ASSIGN gate, the
   compare and the clamp where main paid a discard `memchr`; small and
   UNEXPLAINED beyond that (no attribution run).

### 5.2 search_short (one `rx_search` from 0, short subjects <= 4 KiB)

| cell | n | new/base | newm/base | deny/base | new/newm | worst new/base | slower than main by >3% |
|---|---|---|---|---|---|---|---|
| loglines/ipv6 | 112 | 0.576 | **0.325** | 1.000 | 1.77 | 0.801 | 0 of 112 |
| loglines/ipv4 | 112 | 1.104 | **0.315** | 0.998 | 3.51 | 2.341 (s-008) | 83 of 112 (generic build) |
| bounded/dotted4 | 49 | 1.830 | **0.841** | 1.000 | 2.18 | 12.894 (d-01024) | 33 of 49 (generic build) |

ipv6 short calls: rlhtwin's h2 read 0.319; the memchr build reads 0.325, the
generic build 0.576, every one of the 112 calls faster than main either way.
ipv4 and dotted4 (filled at integration from `docs/dev/optloop/rlhbuild/
times_short_summary.txt`, 3 rounds x 5 reps, 273 subject lines, match counts
equal across all four variants on every line): `new` is the build with the
GENERIC gate loop, `newm` the scratch memchr ASSIGN (what R-15 now renders).
With memchr both cells beat main on the summed short calls (ipv4 x0.315,
dotted4 x0.841); through the generic loop ipv4 is x1.104 and dotted4 x1.830
(landmark-absent subjects up to x12.9 per call), the regression §5.1 item 2
and §5.3 record. The deny reproduces main (x0.998 / x1.000).

### 5.3 The R-15 delta, stated for the kit (R-15's D77 reading)

On ipv6 / ipv4 / dotted4 the built re-entry with today's GENERIC gate loop
against the scratch memchr ASSIGN at both sites, pinned and interleaved:
**throughput x1.87 / x4.48 / x46 slower through the generic loop** (per
subject x1.60-2.38 / x2.73-16.8 / x35-53); search_short in §5.2. R-15's
Q-R15-2 asked exactly this ("Build only if S1 beats h2g on the three cells");
it does, by a wide margin on every cell, and the dotted4 / landmark-absent
cases show the generic loop is also a regression against MAIN (§5.1 item 2),
not only a missed win.



## 6. Validation

**Run by this lane, on the lane's tree (Linux dev box, solo, nothing else of
mine running):**

| check | verdict |
|---|---|
| `make -j16`, `make strict` | clean (gcc 15.2, `-Werror -Wshadow`) |
| `make test-codegen` | 16/16 scripts, 743 PASS |
| `make test-vm` | 3/3 (after SEL-1 re-pin 2 -> 3: the hostile cell, a corpus event) |
| `make test-prechecks` (`run_prechecks.sh`) | green, 392+ PASS (5.12a/b/c/e/l-q included) |
| `make test-startset` | green (the hat suites deny the handoff on both arms; manifests re-pinned) |
| `make test-registry`, `test-cpset-structure`, `test-rxtsource` | green after the re-pins in §1.5 (axes 229, the `(?i)HeLLo` manifest row, census +24 blocks) |
| `make test-encoding-checks` | 11/0 (DD12a(i) excises the byte gate and the re-entry move; prior-keyed `handoff` form); main's own run 11/0 |
| `make test-memfn-rows`, `test-memfn-reach` | 4/0 and 3/3 |
| `make test-cand-oracle` (trace build, both walks' successor) | 91/0, the self-check's state-based cycle test included |
| `tests/harness/run.sh tests/litscan/handoff.rxt` | 4,824+/0 (regenerated after; `gen_handoff.py --check-pcrec` 0 mismatches) |
| identity (§3) | 0 diffs, 8 cells, vs main / deny / libpcre2 10.46 |
| sabotage anchors (every row's `SAB_BEFORE` count) | all match; every REACH probe reaches as on main |

**OWED — armed, NOT run** (the BOILERPLATE's never-idle-wait rule: the chain is
detached behind a `.lift` waiter, ONE waiter in this worktree):

```
nohup setsid bash /home/pcrec/projects/pcrec/worktrees/rlhbuild/build/land/chain.sh &   # armed by the lane
touch /home/pcrec/projects/pcrec/worktrees/rlhbuild/.lift                               # the manager lifts
```

It runs, logging one line per step to `build/land/chain.log` (completion
trailer `== rlhbuild chain COMPLETE`): `make`, `make strict`, the FULL
`make test` through `scripts/perfrun --label rlhbuild` (`build/land/test.log`;
verdict `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'`), `make test-axes`
(`axes.log`), `make test-recursion-identity` (`recid.log`; FILEPIN self-pinned
to `a6dfa071`, this lane's last src commit), `scripts/emit_sweep.py --ref HEAD
--arms start` (`sweep.log`: the start-arm DIFFER floors; `-fno-req-handoff`'s
differ count RISES with the byte landmarks, a floor is a minimum, and
`-fno-start-set`'s may FALL where the re-entry now outranks a hat, which would
be a reviewed re-pin), `make test-spec-history` (`spechist.log`), and the mech
rows S805-S814 plus every re-aimed/re-pointed row (S265 S280 S282 S283 S446
S460 S463 S606 S610 S693), each `mech_SNNN.log`.

Expected reds a fresh agent should read before calling anything a regression:
the start-arm floors above; any rxtsource/startset manifest the full suite
pins that this lane's section runs did not reach.

## 7. Open items, filed rather than built

1. **R-15 is a precondition of the merge, not a follow-up** (§5.1 item 2,
   §5.3): through the generic loop the build regresses landmark-absent and
   landmark-dense byte cells against main by x35-53 and up to x1.43. Main files
   R-15's step 2 against this lane's measurement; the kit's row lands first at
   zero movers, then this branch.
2. **The prior-cost family has four members now** (memory
   `pcrec-forest-for-trees`): G1's `req_byte_dominated_by` (a COMPARE),
   `set-leads`' `pcrec_find_pick` (a PICK), R4's `cand_rs_dense_applies` (a
   density threshold) and the re-entry's `req_landmark_admits` (an expected
   jump against an expected skip). All four read `pcrec_find_byte_rate`
   through findings.c's primitives and decide "which scan pays" between a
   landmark and a start-byte set. A unifying PRIMITIVE ("expected advance per
   stop of scan X", `1/mass`) would make G1, set-leads and this admission one
   comparison; proposed, not built (no measured disagreement among them yet).
3. **The admission reads the prior only.** hcolon_in shows a prior-admitted
   re-entry costing x1.5 on text that contradicts the prior (linear). Whether
   the bench's text contradicts the default prior on any real cell is the
   bench's question (§8, Q2).
4. **ENTRY-only +13% on hcolon's colon-dense find-all, through memchr**
   (§5.1 item 5): unexplained; small; a placement/attribution question for the
   bench's numbers before anyone builds on it.
5. **The re-entry only fires at the start state s0.** On a seeded machine
   (`\b...`) the restart often sits in a seed state that is not s0 (the
   `seed[nonword]` cell), so the re-entry fires less there than on unseeded
   machines; the existing start-set rows share the same condition (`pf_open`).
   Not measured beyond the corpus answers.
6. **Two-landmark window (Frank's UNLOCK)**: not built, as ruled.
7. **VM hybrids get the ENTRY generalization only** (grp-atomic-alt, K 2):
   their retries are RETRY's; no re-entry inside the prefilter function.

## 8. BENCH RELAY DRAFT (for main to send; not sent)

> **[REQ-HANDOFF-L1] built on lane/rlhbuild (pcrec abi 74 -> 75).** Stamp and
> vocabulary changes a bench reader sees:
>
> - `<PREFIX>_REQ_HANDOFF` (unchanged vocabulary: a decimal K or `"none"`) now
>   also carries a K for a ONE-BYTE landmark: K is the maximum byte offset of
>   the pre-check's needle (the run window where `REQ_RUN` is not `"none"`,
>   else the byte `REQ_BYTE`) from the match start. New values on bench
>   patterns: loglines/ipv6 `"4"`, loglines/ipv4 `"3"`, bounded/dotted4 `"3"`,
>   syntax/qnt-poss-brace `"2"`, syntax/grp-atomic-alt `"2"`, utf8/cls-s-ucp `"4"`.
> - `<PREFIX>_DFA_PREFILTER` gains the value **`"handoff"`**: the forward scan
>   RE-ENTERS the handoff at each restart (re-finds the landmark, moves to
>   hit - K when ahead). Bench patterns moving to it: loglines/ipv6, ipv4,
>   kv-quoted; bounded/dotted4; altwide/sfx-64, sfx-256, sfx-512;
>   syntax/cls-fold-pair, cls-pair-ctl, mod-i, mod-r, qnt-poss-brace;
>   utf8/ci-ascii-control, ci-strasse (14).
> - `<PREFIX>_MEMFN_LIBC` drops `"memchr"` on dotted4, ipv4, ipv6 and
>   qnt-poss-brace (their one-byte gate renders through the kit's generic loop
>   until R-15's row lands).
> - `--emit-facts` gains `req_set_maxoff` and `req_landmark_maxoff`.
> - Deny: `-fno-req-handoff` removes BOTH the entry handoff and the re-entry
>   (no new flag bit). `--list-axes` lists `handoff` on the `prefilter` axis
>   with that deny.
>
> Asks:
> 1. When R-15's memchr row has landed with it, time BASE (abi 74) vs NEW vs
>    `-fno-req-handoff` on loglines/ipv6, ipv4, kv-quoted, bounded/dotted4
>    (throughput + search_short) and altwide/sfx-64 (throughput). Scratch
>    predictions (Linux dev box, memchr gate): ipv6 x0.31 / ipv4 x0.20 /
>    dotted4 x1.00 (its throughput text has no `.`) / sfx-64 x0.07 /
>    kv-quoted x1.01 throughput; search_short in the lane report §5.2.
> 2. Does any bench cell's subject carry a byte-landmark DENSER than the
>    default byte prior predicts (the case where an admitted re-entry costs
>    up to x1.5, linearly)? The candidates are the 14 movers above.
> 3. A cell where the re-entered handoff leaves a measured gap to rev-inner
>    (the re-worded [ENG-TACTICS] trigger): kv-quoted's -8.7% stays the
>    standing candidate.

## 9. Integration addendum (lane rlhland, 2026-10-11)

- Merged main (677762be, kit R-15) into lane/rlhbuild; `git merge` alone.
  Conflicts (3, all append-only text): docs/dev/lanes/CLAUDE.md and
  tests/mech/CLAUDE.md kept both sides; docs/dev/plan.md kept main's new
  [PRIOR-COST-UNIFY] row and the lane's [REQ-HANDOFF-L1] row plus main's
  REFINEMENT sentence and the hcolon_in file-at-merge note. `make strict`
  clean before the merge commit.
- Movers re-pinned (abi stays 75; test-codegen's abi readers were already
  green): tests/codegen/run_prechecks.sh `[5.12l]` (28 re-entering artifacts)
  accepts the memchr ASSIGN rendering of the re-entry gate (it was red on all
  28). tests/memfn/site_manifest.tsv PRE row gained `emit_req_reentry_use`
  (no new row).
- R-15's three stale items flipped: the cli case now asserts the deny
  reproduces the generic gate loop on dotted4 (both simd settings) and still
  moves nothing on `(ab)c?userpass`; the registry.md / tuning.md sentences;
  rows.tsv `precheck_assign_byte` reach `pcrec` (witness dotted4, cflags the
  deny, control `=`). Its pcrec_floor is PLACEHOLDER (legal): the N2 census
  that reads it is OWED, a slot.
- Variants sweep: 13 tag floors (26 FLOOR lines) in scripts/emit_sweep.py
  VARIANT_PINS lowered to slot22's measured values. NOT done: the two thin-tag
  MANIFEST reds in the same log (`(\p{Xwd})`, `((a)+)+` no longer carry
  no-size-cap / stderr-default) need a tree-measured `--emit-pins` run; this
  branch's own variants sweep is OWED to the manager.
- §5.2 ipv4/dotted4 rows filled.
- Quick checks green on the branch: strict, test-codegen, test-cli,
  test-prechecks, test-memfn-{manifest,rows,reach,stamps,arms,deleg,g2},
  test-registry, test-startset, test-entry-shape-identity,
  test-rxtsource, test-spec-history. `make test-spec` fails here on
  `pcre2_compile_8` link errors (environment: it is not part of the chain's
  evidence; not investigated).
- Chain: build/land/chain.sh, PID 2287504, SID 2287504 (the lane shell's SID
  differs), log build/land/chain.log, trailer `== rlhbuild chain COMPLETE`.
  `.lift` created at the end of this lane.
