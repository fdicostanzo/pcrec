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
5. **Timing and the R-15 delta**: §5 (OWED at this commit if the section says
   so; the numbers are scratch tier).
6. **Validation**: the full chain is ARMED, not run, at hand-back (§6): make,
   make strict, FULL make test, make test-axes, mech S805-S814 (+ the re-aimed
   rows), emit_sweep start-arm floors, make test-spec-history. The sections I
   ran solo while fixing are listed in §6 with their verdicts.
7. **A cost the kit row R-15 removes**: every byte-landmark artifact's ENTRY gate
   is now the kit's GENERIC ASSIGN loop (a byte-at-a-time statement expression)
   where it was a discard `memchr`; `RX_MEMFN_LIBC` drops `memchr` on the
   movers whose only memchr it was (bench: dotted4, ipv4, ipv6,
   qnt-poss-brace), and the code grows ~570 B per gate (the size-term rescue
   witness, §2.3). The re-entered gate is the same text. §5 measures it.

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
(Measured with the first-cut admission; the later comparative admission only
narrows which artifacts re-enter, and every artifact is held by the suites below.)

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

## 5. Timing — SEE §5 BELOW (filled after the run)

## 6. Validation

## 7. Open items, filed rather than built

## 8. BENCH RELAY DRAFT
