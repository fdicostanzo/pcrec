# rlhtwin — [REQ-HANDOFF-L1]: the one-byte K82 handoff, scope + twins

**Lane `rlhtwin`, 2026-10-11, opus. MEASUREMENT plus a design scope; nothing under `src/`
on `lane/rlhtwin` changes.** The twin's emitter is a SCRATCH src change on branch
`lane/rlhtwin-scratch` (`ceca117d`), **NOT FOR MERGE** (no abi bump, no spec hunk, no tests,
no deny-axis work). Pin: main `e4387b18` (abi as at that commit), Linux dev box (Ryzen
7700X, gcc 15.2 `-O2`, libpcre2-8 10.46). pcrec-bench at `d359564f`, read only (subjects
regenerated in a `git archive` copy; short and throughput manifests compared equal).
Instruments and raw outputs: `docs/dev/optloop/rlhtwin/` (own `CLAUDE.md`), re-using
et1twin's driver, oracle driver and reverse-inner twin by path. **Every number is SCRATCH
TIER.** The box was NOT quiet during timing (lane r14p's memfn plant builds ran
throughout; load1 recorded in `times.tsv`'s header and trailer); variants are interleaved
per subject on one pinned core, so the ratios are the reading, not the absolutes.

Charter: plan.md `[REQ-HANDOFF-L1]` as re-scoped by Frank 2026-10-11 — generalize the
EXISTING K82 handoff to a landmark of length 1..n at an inner match point, K = the
maximum offset of its first guaranteed occurrence from the match start, scan from c − K;
measure on loglines/ipv6 + ipv4 against today and the reverse-inner twin.

## 0. Answers first

1. **Why today's handoff does not reach ipv6/ipv4: a MISSING FACT first, an admission
   guard second, no emitter obstacle.** The run walk produces no run for either pattern
   (each branch's best run is the single byte `:`/`.`, below the 16-bit run floor, and
   `rr_alt` keeps only common heads/tails anyway); the byte survives only in the
   necessary SET, which carries no offset. So there is no K to hand off with. Every
   `len >= 2` test in the handoff path (`req_handoff_applies`, `req_site_define`'s byte
   arm, `pcrec_emit_req_byte_check`, the K readers) is a consequence of that, not an
   independent decision. The kit vocabulary already has `(ALL_PRESENT, ASSIGN, SET)`.
   §1.
2. **The smallest general change** (built as scratch, §1.3): a per-member maximum offset
   on the necessary-set walk (the run walk's own offset rules, applied to the set: CAT
   shifts the right factor by `maxw(left)` and takes the nearer bound for a byte in both;
   ALT takes the farther; a `{m>=1,}` repeat keeps the body's FIRST-iteration offset); a
   derived landmark K (the run window's where a run ships, else the picked byte's); the
   existing `handoff` row's `len >= 2` conjunct replaced by "the landmark's K is finite";
   the PRE site's byte gate ASSIGNs its position. Same row, same stamp (`RX_REQ_HANDOFF`
   = K), same deny (`-fno-req-handoff`): no new flag bit. **No first-iteration peel is
   needed for K**: the walk's repeat rule already reads the first iteration; the scratch
   fact gives ipv6 K = 4 and ipv4 K = 3 with no splice (the peel rincensus needs is for
   rev-inner's `P·L` split, not for a bound).
3. **Identity**: all five variants answer-identical to today and to libpcre2 10.46 on
   both cells (524 subjects each, find-all + every startpos: 287,464 / 271,336 searches),
   0 diffs. A planted bound of K = 0 is caught (381 / 364 differing subject lines); K − 1
   down to 1 is NOT, and that is equivalence, not blindness: on the reverse-pass DFA body
   any start inside the leading class run reaches the same leftmost end and the reverse
   pass restores the start (§2.2).
4. **Timing: the one-shot handoff captures 0-6% of reverse-inner's win; the handoff
   RE-ENTERED at the forward scan's restart point captures 109-120%** (ipv6 h2/today
   0.334 throughput / 0.319 short vs rev-inner 0.392 / 0.405; ipv4 0.196 / 0.278 vs
   0.261 / 0.399), and on sfx-64 0.068 vs rev-inner's 0.067. §3. The K82 handoff moves only the scan's ENTRY; on syslog text the first `:` is a
   timestamp a dozen bytes in, so the entry moves by a dozen bytes and the forward DFA then
   walks every later byte exactly as today. Re-entering the same gate wherever the
   unanchored machine is back in its start state with no accept pending (where it already
   skips to the next can-begin byte) keeps it on the landmark scan.
5. **VERDICT**: the generalized handoff as re-scoped (length 1..n, ENTRY only) captures
   0-6% of reverse-inner's saving on ipv6 and ipv4 — it does not clear the plan row's
   "build only if it captures much of the benefit". The same handoff RE-ENTERED captures
   109-120% (§3), is a smaller build than rev-inner (no reverse prefix machine, no G2, no
   anchored verify), and also serves the cells where the run handoff ALREADY ships
   (sfx-64: full capture; kv-quoted: none, +1.3%; §3.3). The recommended general change is therefore the landmark-K
   fact PLUS a NEXT-slot row with the handoff's own map (`CM_LOWERBOUND`), §4.

## 1. Scope

### 1.1 What the handoff is today

`handoff` is FIRST's row in `cand_rows[]` (`src/gen/emit_dfa.c:8700`, map
`CM_LOWERBOUND`, deny `-fno-req-handoff`); its predicate `req_handoff_applies`
(`emit_dfa.c:7608`) requires an emitted pre-check AND `pcrec_fact_req_run(cx)->len >= 2`,
a DFA scan, a finite `req_run_maxoff`, no count-collapsed prefilter, and the (d′) decline.
The gate (`req_site_define`, `emit_dfa.c:1524`) ASSIGNs the run window's position;
`emit_req_handoff_rest` subtracts K; the body starts at `handoff_position`
(`pcrec_emit_req_byte_check`). The fact is `ReqRun.maxoff`, the run walk's `RbRun.off`
plus the window's `at` (`src/facts/req.c`, litscan_k82h.md §1.3).

### 1.2 Why ipv6/ipv4 get `REQ_BYTE` and `REQ_HANDOFF "none"`

Read off `--emit-facts` at the pin:

| pattern | req_set | req_whole_run | req_run_maxoff | req_byte | REQ_WHY | REQ_HANDOFF |
|---|---|---|---|---|---|---|
| ipv6 `(?:(?:H:){4,7}H\|(?:H:){1,7}:H{0,4})` | 58 | none | none | 58 `:` | emitted | none |
| ipv4 `(?:(?:OCT)\.){3}(?:OCT)` | 46 | none | none | 46 `.` | emitted | none |

In causal order:

1. **The fact (the root cause).** The run walk never ships a run here. Each branch's best
   run is ONE byte (`:` at offset ≤ 4; `.` at offset ≤ 3), and a run ships only at
   `PCREC_MIN_REQ_RUN_BITS` = 16 (two exact bytes). Even a longer per-branch best would
   not survive the top-level alternation: `rr_alt` keeps the branches' common HEAD and
   common TAIL only, and ipv6's branches start with a repeat (`rr_none`, no head). The
   byte reaches `req_byte` through the SET (`rb_intersect` across the branches), and the
   set is a 256-bit membership with no offset. **There is no K for a byte.** This is
   litscan_k82h.md Q4's "needing per-byte offsets for the SET", confirmed as THE blocker.
2. **The admission guard (a consequence).** `req_handoff_applies` returns false at
   `->len < 2` before it reads K. With a byte K in hand it would still decline here.
3. **The emitter (one structural line, no obstacle).** `req_site_define`'s byte arm
   (`} else gate = b;`) never sets `handoff`, and `pcrec_emit_req_byte_check` reads the
   handoff only under `len >= 2`; both are the same guard spelled twice more. The kit's
   vocabulary already carries `(MF_OP_ALL_PRESENT, MF_H_ASSIGN, MF_TK_SET)`
   (`memfn/src/compose.c`'s `vocab[]`), so the byte gate can ASSIGN its position today.
   **One kit finding**: it renders that site with the GENERIC per-byte loop (a
   statement-expression scanning one byte per iteration; `RX_MEMFN_LIBC` flips from
   `"memchr"` to `"none"`), not `memchr`. On these cells it costs nothing measurable
   (h1 vs h1m in §3: the one-shot gate scans only to the first landmark), but under the
   re-entered form it is the hot scan, so a build needs a kit ASSIGN arm over one SET
   term that returns `memchr`'s position — a request the manager files (single-writer
   ledger).

### 1.3 The smallest general change (scratch: `lane/rlhtwin-scratch` `ceca117d`)

| layer | change | general because |
|---|---|---|
| core fact | `RbSet` gains `off[256]`: per member, the largest byte offset from the attempt start at which SOME guaranteed occurrence begins. `rb_union(l, r, maxw(l))`: a byte only in `r` is at `maxw(l) + off_r`; in both, `min(off_l, maxw(l) + off_r)` (either occurrence satisfies invariant F, so the nearer bound holds). `rb_intersect`: `max`. Every arm that puts width to the LEFT of `acc` shifts it (multi-member class 1, `{0,n}` repeat its max width, backref/call unbounded). `{m>=1,}`: the body's offsets (the first iteration starts where the repeat does). Stored in `ReqSet.off` | it is the run walk's offset table (litscan_k82h.md §1.3) applied to the other accumulator on the same walk; no new walk, no re-spelling |
| derived fact | `req_byte_maxoff` = `off[req_byte]`; `req_landmark_maxoff` = the run window's K where a run ships, else the byte's | the landmark is "the gate's needle", whatever its length |
| row predicate | `handoff`'s `len >= 2` conjunct removed; K read from the landmark fact | one predicate for 1..n |
| emitter | the byte gate becomes the site's `ret_pred` when FIRST is `handoff`; the "one window predicate" internal check counts the landmark predicate; `emit_req_handoff_rest`/the stamp read the landmark K | the K82 text is unchanged; only which predicate is kept |
| stamp | `RX_REQ_HANDOFF` = K, as today | the stamp already names K, not the run |
| deny | `-fno-req-handoff`, reused | same row, same decision (where the body starts); one deny per row; no flag bit spent ([IFACE-PUSH]'s ≤ 4-bit trigger) |

Scratch K values: ipv6 4, ipv4 3, kv-quoted 32 (unchanged), dotted4 3.

What a build owes that the scratch omits: an `--emit-facts` row for the byte K (E2,
derived, `depends req_set`, owner `req.c`); `--emit-facts`' `req_set` value text must NOT
move (it renders a stamp reader; put the offsets on a new core fact row, the run's
`whole_maxoff` precedent); the fact's own independent check (litscan_k82h.md §4.2a's
shape, a byte-K probe against matched spans); the utf8 round-up is already in
`emit_req_handoff_rest`; abi event + spec hunk for `RX_REQ_HANDOFF`'s description and
`req-use`; sabotage rows (the K-plant must use K = 0 or a later occurrence, §2.2; K − 1 is
equivalent on reverse-pass bodies); the RbSet frame growth (2 KB per walk frame as
scratch-spelled; a saturating 16-bit offset, or offsets only for members, is the build's
choice).

### 1.4 What else the generalized ENTRY handoff newly serves

Compile-only census, every bench pattern (`census.sh` → `census.tsv`; 367 patterns, 27
refused by both compilers at `--features all`): **5 move**.

| pattern | K | route | note |
|---|---|---|---|
| loglines/ipv6 | 4 | DFA | the cell |
| loglines/ipv4 | 3 | DFA | the cell |
| bounded/dotted4 `(?:\d{1,3}\.){3}\d{1,3}` | 3 | DFA | ipv4's sibling |
| syntax/grp-atomic-alt `(?>a\|ab)c` | 2 | VM hybrid | the VM consumer (prefilter's first call) |
| syntax/qnt-poss-brace `a{1,2}+b` | 2 | DFA | |

80 bench patterns carry a byte-only pre-check; 30 of them `emitted` (the rest
`dominated`/`one-attempt`, where nothing is handed off), and of those 30 the five above are
the ones with a finite byte K on a route the row admits. The rest are unbounded
(`\S+@\S+`, email: the byte sits after an unbounded class run) or VM routes without a DFA
scan. **The population of the ENTRY generalization is small and its gain is ~0 (§3); the
row's value is in the re-entered form.**

### 1.5 The re-entered handoff (the general form the twin found)

The handoff's soundness (litscan_k82h.md §1.2, Claims 1-3) is a statement about a fresh
search from a startpos `f`: no match starts in `[f, c − K)`. The forward unanchored body
reaches a fresh search from `scan_position` every time its machine is back in its start
state with no accept pending — the exact point where it already skips to the next
can-begin byte (the NEXT slot's site). So the same gate applies there with `f =
scan_position`: find the landmark's least occurrence `c ≥ scan_position` (none: NOMATCH,
since no thread is alive and no match is pending), jump to `max(scan_position, c − K)`.
A landmark found earlier and still `≥ scan_position` is reused (it is still the least).
On a seeded machine the jump re-seeds from the byte before the landing, as the
offset-set/first-set rows already do (`pf_emit_ofs_reseed`); kv-quoted's twin re-uses
its artifact's own re-seed line.

In the start table this is a NEXT-slot row with FIRST `handoff`'s map, `CM_LOWERBOUND`,
ranked below the exact-start rows (`run-pinned*`, `offset-set*`) and above the
start-byte rows (`first-*`, `memchr*`, `byte-class*`), on `CR_DFA`; its predicate is
`handoff`'s (the landmark K finite) plus the DFA-scan premise; the landmark scan is the
gate's FIND site re-used (`rx_reqrun` for a run; `memchr` for a byte). The entry
instance stays FIRST's (it is also what the attempt and VM-hybrid bodies read). Deny:
the brief asked whether to reuse `-fno-req-handoff`. For the ENTRY generalization, yes.
For the re-entered row, the recommendation is also yes (§5 Q2): one fact, one proof, and
no measured use for the entry without the re-entry. A separate bit (the usual house shape
for a NEXT row) is the alternative if Frank wants the two ablated apart.

## 2. Identity

### 2.1 The check (`ident.sh` → `ident.txt`)

et1twin's method: per subject, the bench's find-all loop and single searches from every
startpos (stride 1 to 4 KiB, then every 4099th byte), hashed over `(pos, rc, s, e)`;
subjects = the loglines short (112) + throughput (12) subjects regenerated and
manifest-checked + 400 adversarial subjects per cell (`gen_adv.py`: the landmark at
exactly K and K+1 after a start-set run, landmark-dense runs, start-set runs longer than
K, many dead landmarks between matches for the re-entry).

| cell | subjects | find-all matches | startpos searches (hits) | o/h1 | o/h1m | o/h2 | o/r | o/p2 |
|---|---|---|---|---|---|---|---|---|
| ipv6 | 524 | 3,193 | 287,464 (88,701) | 0 | 0 | 0 | 0 | 0 |
| ipv4 | 524 | 2,716 | 271,336 (72,851) | 0 | 0 | 0 | 0 | 0 |

`o` today; `h1` the scratch emitter's artifact unmodified; `h1m` h1 with the gate as
memchr; `h2` h1m re-entered; `r` et1twin's reverse-inner twin (ipv4's donor
`(?:OCT)\.\z`, built here the same way; `.` ∉ digits, G2's literal arm); `p2` libpcre2-8
10.46.

### 2.2 The failing-direction control (`plant.sh` → `plant.txt`)

h2 with its bound replaced at the entry AND the re-entry:

| cell | K | planted | subject lines differing from today (of 512) |
|---|---|---|---|
| ipv6 | 4 | 3 | 0 |
| ipv6 | 4 | 1 | 0 |
| ipv6 | 4 | 0 | **381** |
| ipv4 | 3 | 2 | 0 |
| ipv4 | 3 | 1 | 0 |
| ipv4 | 3 | 0 | **364** |

K = 0 (start AT the landmark) is caught on both. K − 1 down to 1 is equivalent, by the
body's shape rather than by luck: P here is a class run (`[0-9a-f]{1,4}`, `[0-9]{1,3}`
alternatives), any suffix of a P-string before the landmark that is still non-empty is a
P-string, so a start anywhere inside the run reaches the same leftmost-longest END, and
the reverse pass (floored at `search_from`, not at the handoff) restores the leftmost
start. The handoff's K is exact for the PROOF (Claim 1) and loose for these bodies. Two
consequences: a build's K-sabotage row must plant K = 0 or a later-occurrence gate
(litscan_k82h.md S464's shape), never K − 1, on reverse-pass cells; and an attempt-route
or VM witness is what makes K − 1 visible.

## 3. Timing

`time.sh` (et1twin's method): `taskset -c 7`, the five variants interleaved per subject,
3 rounds, each reading the median of 7 batches of ≥ 40 ms, the table the median over
rounds; `throughput` = one find-all pass per throughput subject (12), `search_short` =
one `rx_search` from 0 per short subject (112, all ≤ 4096 B). load1 2.55 at start
(lane r14p's builds), 1.43 at end. Every variant's match count equals today's on all 248
subject lines. Raw `times.tsv`, reading `times_summary.txt`. CAPTURE =
`(today − variant) / (today − rev-inner)`, the fraction of the reverse-inner twin's
saving the variant achieves.

### 3.1 ipv6 and ipv4

| cell | regime | today Σ ns | h1 /today | h1m /today | **h2 /today** | rev-inner /today | capture h1 | capture h1m | **capture h2** |
|---|---|---|---|---|---|---|---|---|---|
| ipv6 | throughput | 3,951,722 | 0.991 | 1.003 | **0.334** | 0.392 | 0.02 | −0.00 | **1.09** |
| ipv6 | search_short | 122,346 | 0.991 | 0.993 | **0.319** | 0.405 | 0.02 | 0.01 | **1.14** |
| ipv4 | throughput | 3,099,195 | 0.967 | 0.993 | **0.196** | 0.261 | 0.04 | 0.01 | **1.09** |
| ipv4 | search_short | 77,069 | 0.981 | 0.966 | **0.278** | 0.399 | 0.03 | 0.06 | **1.20** |

Per subject:

- **ipv6**: h2/today 0.258-0.372 on every throughput subject and 0.245-0.674 on every short
  subject (all 112 faster). h2 against rev-inner: 0.67-1.01 throughput (tie on
  `1024k-syslog`), 0.62-1.23 short (slower than rev-inner beyond 2% on 5 of 112).
- **ipv4**: h2/today 0.074-0.302 throughput; short 0.166-1.103, with **2 of 112 short
  subjects slower than today** (`s-010` 45.5 → 48.3 ns, `s-027` 40.9 → 45.1 ns: the
  re-entry's per-restart test on a call that matches early). Against rev-inner h2 wins on
  the fail/hit subjects (0.64-0.75) and LOSES on the four `syslog` subjects (1.5-1.7×:
  0.074 vs 0.044 of today on 1 MiB). Those subjects carry no `.`-landmark that starts a
  match, and rev-inner's reverse walk rejects each `.` in ≤ 3 bytes, where h2 re-runs the
  forward DFA over up to K + a few bytes per `.`. Both are far under today on them.
- **h1 ≈ h1m ≈ today** (within ~3%, mostly noise; h1's slight edge on ipv4 throughput
  is not reproduced by h1m and is placement-sized): the one-shot handoff moves only the
  entry, and the first landmark is a dozen bytes in. The generic kit loop costs nothing
  measurable here because it scans only to that first landmark.

### 3.2 Why the entry form cannot capture it

Today's unanchored forward scan walks every byte from the entry to the first match end
(it skips only non-can-begin bytes while in the start state, and hex digits / digits are
can-begin). The entry handoff removes the prefix before the first landmark of each call,
and on syslog text that is the timestamp's `:`/`.`. Reverse-inner wins by staying on the
landmark scan; so does h2, by re-asking the gate at each fresh-start point.

### 3.3 The re-entry on the cells where the run handoff already ships (`extra.sh`)

| cell | K | identity (o/h2, o/p2) | throughput h2/today | et1twin rev-inner/today |
|---|---|---|---|---|
| altwide/sfx-64 | 9 | 0 / 0 (444 subjects) | **0.068** (0.059-0.121) | 0.067 |
| loglines/kv-quoted | 32 | 0 / 0 (524 subjects) | 1.013 (0.996-1.019) | 0.913 |

(Identity over the set's short + throughput subjects + et1twin's own 400 adversarial
subjects per cell; timing one pass of 3 rounds, `extra_times.tsv`; et1twin's numbers are
its own run, same subjects, same box, an earlier day.)

- **sfx-64**: the re-entered run handoff matches reverse-inner's −93% exactly. That is
  et1twin's own diagnosis ("the K82 handoff is single-shot") confirmed by the fix, with
  NO factor-free G2 arm needed (the handoff's soundness has no G2).
- **kv-quoted**: no gain, +1.3% (each restart's `rx_reqrun` re-call on a seeded machine
  that rarely returns to the start state between `="` hits). Rev-inner's −8.7% here is
  EXACT start over the K = 32 window, which no handoff gives. So the re-entry needs no
  admission rule to be safe here, but a build re-times this cell (§5 bench Q1).

## 4. Verdict and the proposed general change

**Per cell, fraction of reverse-inner's saving captured (Σ over the regime's subjects):**

| cell | regime | generalized handoff as re-scoped (ENTRY, h1) | + memchr gate (h1m) | **RE-ENTERED (h2)** |
|---|---|---|---|---|
| loglines/ipv6 | throughput | 2% | 0% | **109%** |
| loglines/ipv6 | search_short | 2% | 1% | **114%** |
| loglines/ipv4 | throughput | 4% | 1% | **109%** |
| loglines/ipv4 | search_short | 3% | 6% | **120%** |
| altwide/sfx-64 (run, K = 9) | throughput | today already ships the entry | — | **~100%** (0.068 vs 0.067) |
| loglines/kv-quoted (run, K = 32) | throughput | today already ships the entry | — | **~0%** (1.013 vs 0.913) |

**VERDICT.** The handoff generalized to a one-byte landmark at the ENTRY only, which is
the row as re-scoped, captures **~0-6%** of reverse-inner's win on ipv6 and ipv4 and
does not clear "build only if it captures much of the benefit". The same handoff
**re-entered at the forward scan's restart point captures all of it (109-120%) on ipv6
and ipv4 and on sfx-64**. It needs no G2, no factor-free arm, no peel, no reverse
prefix machine and no anchored verify. It loses to reverse-inner where exactness inside
the window matters (kv-quoted; ipv4's syslog subjects, though still 13× under today
there), and it costs a few ns on 2 of 224 short calls.

**The proposed general change** (three commits, in order):

1. **Fact (no mover).** `RbSet.off[]`: the per-member maximum first-occurrence offset
   on the necessary-set walk, using the run walk's own offset rules (§1.3). It gets its
   own core facts row, so `req_set`'s value text does not move. The derived
   `req_landmark_maxoff` is the run window's K, or else the picked byte's K. The
   independent check is a byte-K probe against matched spans.
2. **The entry generalization (abi event).** `handoff`'s `len >= 2` conjunct reads "the
   landmark's K is finite". The byte gate ASSIGNs its position. `RX_REQ_HANDOFF` is K.
   The deny stays `-fno-req-handoff`. Movers: the five in §1.4.
3. **The re-entry (abi event).** A NEXT-slot row on `CR_DFA` with `handoff`'s map
   `CM_LOWERBOUND`, ranked below `run-pinned*`/`offset-set*` and above the start-byte
   rows. Its predicate is the landmark K finite plus a DFA scan. At the unanchored body's
   restart point (start state, no accept pending), the gate's FIND is re-asked from
   `scan_position`: no hit means NOMATCH, else jump to `max(scan_position, c − K)`, with
   the reseed of `pf_emit_ofs_reseed` on a seeded machine and the found position reused
   while it is still ahead. It is denied by the same `-fno-req-handoff` (Q2). It needs
   the kit's memchr ASSIGN arm for a byte landmark (Q4). Its movers are every DFA
   artifact whose FIRST row is `handoff` (bench: today's 47 run handoffs + the five
   above), each timed on the bench.

## 5. Questions (with recommendations) and bench-only questions

**For Frank (each with a recommendation):**

- **Q1. Build the generalized handoff as the ENTRY row alone (the row as re-scoped), or
  with the re-entry?** The entry alone captures ~0% on both cells (§3) and moves 5 bench
  patterns; the re-entry is where the benefit is. *Recommendation: build both as one
  row family, the landmark-K fact first (a no-mover fact commit, its own checks), then
  the ENTRY generalization (`handoff` reads the landmark K; movers = §1.4's five), then
  the NEXT-slot re-entry row (`CM_LOWERBOUND` on `CR_DFA`), each its own abi event.
  Do NOT build the entry generalization alone and stop.*
- **Q2. One deny for entry and re-entry?** Both use one fact (the landmark's K) under
  one proof (Claim 1 at a fresh-search point); entry-without-re-entry has no measured
  use (it is ~0 here). Flag bits are scarce ([FLAG-ACCESS]/[IFACE-PUSH]'s ≤ 4-bit
  trigger). *Recommendation: reuse `-fno-req-handoff` for both (it denies every use of
  the landmark's position); list the re-entry row under the same axis. A separate bit
  only if a measurement ever wants the entry without the re-entry.*
- **Q3. Rev-inner is HELD on a trigger (D151 add. 7). Does this change it?** On
  ipv6/ipv4 the re-entered handoff matches or beats the reverse-inner twin (§3) with no
  reverse prefix machine, no G2/composition gate, no peel and no anchored verify, and
  it also re-scans on kv-quoted/sfx-64 where rev-inner needed the factor-free arm.
  *Recommendation: keep rev-inner HELD and re-word its trigger to "a cell where the
  re-entered handoff leaves a measured gap": exact start (rev-inner) buys only what the
  forward DFA spends inside the K window, which is what et1twin's kv-quoted control
  measured at −8.7%.*
- **Q4. The kit request.** The byte gate's ASSIGN renders through the generic per-byte
  loop. Under the re-entry it is the hot scan. *Recommendation: file R-n for an ASSIGN
  arm over one SET term (facts only: the site, its one byte term, ASSIGN, the
  position kept); main files it, not this lane.*

**Bench-only questions for relay:**

1. Official verdicts are bench runs on the targeted box (D144 add. 4). When the row is
   built, can loglines/ipv6, loglines/ipv4 and bounded/dotted4 (throughput +
   search_short) and altwide/sfx-64 + loglines/kv-quoted (throughput) be timed BASE vs
   NEW vs `-fno-req-handoff`?
2. Is there a loglines/altwide median at a post-[START-LANDING] pin to weight the
   population (walk_survey's weights are old-pin)?

## 6. Reproduction

```
make -j16                                    # today's build/pcrec (lane/rlhtwin)
git checkout lane/rlhtwin-scratch && make -j16 && cp build/pcrec build/rlh/pcrec_scratch && git checkout lane/rlhtwin && make -j16
B=/home/pcrec/projects/pcrec-bench; W=build/rlh/bc; mkdir -p $W
git -C $B archive HEAD bench pcrecbench | tar -x -C $W
(cd $W/bench/loglines && python3 -I gen_subjects.py && python3 -I gen_throughput_subjects.py)
(cd $W/bench/altwide  && python3 -I gen_subjects.py && python3 -I gen_throughput_subjects.py)
D=docs/dev/optloop/rlhtwin
PCREC=$PWD/build/pcrec SCRATCH=$PWD/build/rlh/pcrec_scratch BENCH=$B OUT=$PWD/build/rlh/cells $D/build.sh
OUT=$PWD/build/rlh/cells BENCHCOPY=$PWD/$W $D/ident.sh            # -> ident.txt
OUT=$PWD/build/rlh/cells BENCHCOPY=$PWD/$W PLANTS="K-1 1 0" $D/plant.sh   # -> plant.txt
PCREC=$PWD/build/pcrec SCRATCH=$PWD/build/rlh/pcrec_scratch BENCH=$B TMPD=$PWD/build/rlh/census $D/census.sh > $D/census.tsv
OUT=$PWD/build/rlh/cells BENCHCOPY=$PWD/$W $D/time.sh > $D/times.tsv
python3 $D/summarize.py $D/times.tsv > $D/times_summary.txt
for m in build ident time; do PCREC=$PWD/build/pcrec BENCH=$B BENCHCOPY=$PWD/$W OUT=$PWD/build/rlh/extra $D/extra.sh $m; done
```

## 7. Validation

`make test-spec-history` on this branch: 145 passed / 0 failed (log
`build/rlh/spec_history.log`). Nothing under `src/` moves on `lane/rlhtwin`, so no other
suite is owed. The scratch branch `lane/rlhtwin-scratch` (`ceca117d`) was built and used
only for the twin; it has no suite run and is NOT FOR MERGE. `extra_ident.txt` is
`extra.sh ident`'s output.
