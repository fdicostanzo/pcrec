# pcrec's reading of pcrec-bench outbox O-97: [START-LANDING] state 3 (pin b8337c33, abi 74)

Written 2026-10-11 by lane o97read (read + summarize + triage; nothing under
`src/`, `tests/`, `docs/spec/` or `plan.md` touched, nothing timed, nothing
built), for the manager's record. Sources, all read-only:

- pcrec-bench outbox `docs/dev/outbox_to_pcrec.md` §O-97 (origin/master
  `59a6d6ef`, fetched into the local sibling checkout);
- the ledger `docs/dev/ledgers/2026-10-11-start-landing-state3-b8337c33.md`
  (lane b135read3; §4 verdict, §5 controls, §6 the [ENG-TACTICS] table, §7
  relay answers, §8 ranking);
- pcrec side: `docs/dev/plan.md` ([START-LANDING], [ENG-TACTICS],
  [OPT-REVEND], [REQ-HANDOFF-L1], [U8-PICK]), `docs/dev/known_issues.md`
  K103/K104, `docs/design/start_landing.md`, `docs/dev/lanes/slbuild_report.md`,
  `src/facts/kset.c`.

Numbers below are the bench's (medians of 5 trials; "ov" = trial ranges
overlap, "DISJ" = disjoint); this lane did no arithmetic of its own beyond
the sums noted. Window: 2026-10-10 20:21 to 2026-10-11 13:03 EDT, ABBA of
b8337c33 against 7388f1c0 (abi 73, repeated as the cross-window control),
every cell measured. Sentinels flat (pcrec 0.982-1.013 over 16 h; the
control column p5-p95 is 0.995-1.007 over 422 cells), so any effect under
about 0.7% is not an engine effect.

## 1. Verdict

[START-LANDING] did what the design said it would. The reading in one
paragraph:

- **Population.** 298/298 predicted movers reproduced by value (I-145's
  210 `end-minus-width` + 88 `landing`; 292 had a compile row the bench
  timed, the other 6 are altwide 2, sentinel 2, `ci-ucp-invariance` 2 with
  no pair).
- **Speed.** Beyond trial overlap (caps and nocaps pooled), 76% of the
  `end-minus-width` cells and 78% of the `landing` cells are faster, against
  a program-identical null of 2.6% faster / 1.8% slower (p5-p95 x0.990-1.008).
- **Where it does nothing.** The whole-subject form moved nothing (278
  cells, all program-identical); the tail family is flat (24 set cells all ov
  at x0.990-1.013, 132 per-subject cells 0 disjoint, `program_sha256`
  identical); nothing outside the flipped set moved in a way the null does
  not contain.
- **Cost.** One unpredicted population: utf8 search-short, 12 patterns,
  24 cells slower by +1.3% to +6.0% (ask 1 below). One compile-time
  outlier, `wild-datetime-datefinder-alternation` (ask 2).

### Per mover set

`B/A` is b8337c33 over 7388f1c0, window 3 both, caps and nocaps pooled.

| set | class | cells | better | worse | ov | median B/A | min-max |
|---|---|---|---|---|---|---|---|
| capability | end-minus-width | 32 | 15 | 4 | 13 | 0.995 | 0.791-1.007 |
| loglines | end-minus-width | 12 | 11 | 0 | 1 | 0.968 | 0.737-0.983 |
| email-specimen | end-minus-width | 4 | 4 | 0 | 0 | 0.846 | 0.744-0.944 |
| litrun | end-minus-width | 48 | 43 | 2 | 3 | 0.786 | 0.637-1.008 |
| syntax | end-minus-width | 168 | 149 | 4 | 15 | 0.951 | 0.850-1.012 |
| syntax | landing | 28 | 28 | 0 | 0 | 0.790 | 0.703-0.980 |
| utf8 | end-minus-width | 116 | 67 | 10 | 39 | 0.981 | 0.789-1.052 |
| utf8 | landing | 108 | 69 | 14 | 25 | 0.942 | 0.517-1.060 |
| bounded | end-minus-width | 28 | 22 | 1 | 5 | 0.934 | 0.691-1.015 |
| bounded | landing | 40 | 40 | 0 | 0 | 0.743 | 0.586-0.951 |
| all | end-minus-width | 408 | 311 (76%) | 21 (5%) | 76 | 0.956 | 0.637-1.052 |
| all | landing | 176 | 137 (78%) | 14 (8%) | 25 | 0.839 | 0.517-1.060 |
| null | program-identical | 852 | 22 (2.6%) | 15 (1.8%) | 815 | 1.000 | 0.753-1.063 |

Reading by set:

- **litrun** is where the fixed-width row pays most: `lit-l40` short x0.638,
  `lit-l16` short x0.655, `lit-l31` short x0.684 and throughput x0.664,
  `wild-secrets-github-pat` short x0.749 caps / x0.641 nocaps.
- **bounded** and **syntax `landing`** are the cleanest sets: 68 of 68 and
  28 of 28 not worse, medians x0.743 and x0.790.
- **loglines / email-specimen** `floor` short x0.737 / x0.744, `uuid` and
  `hex32-id` about x0.97.
- **capability** is the quietest set (median x0.995): its throughput subjects
  rarely match, so the start is rarely recovered. Short cells that win:
  `wild-secrets-github-pat` x0.840, `wild-validator-uuid-grok` x0.911,
  `hex8-bounded` x0.960.
- **By regime.** `end-minus-width`: throughput 143/204 better (median
  0.976), search 168/204 (median 0.925). `landing`: throughput 76/88
  (0.788), search 61/88 (0.886). The gain is mostly a search-regime gain.
- **utf8** is the mixed set: best `prp-l` throughput x0.517 / short x0.568,
  `cls-neg-cjk` x0.544; worst are the 12 patterns of ask 1.
- **FIT movers** (`prp-l`, `prp-notl`): confirmed by value on all four
  records (`ENGINE_SEL size-cap-retry > selected`, `landing`, emit 471,796 >
  894,613 and 490,248 > 874,155; they grow, as the note said) and faster by
  more than the other landing movers (x0.517 / x0.568 and x0.873 / x0.911).
  The bench did not split the size-rung change from START-LANDING; the
  `-fno-start-landing` arm would.
- **Sub-1% worse rows** (`wild-validator-uuid-grok` throughput +0.7%, aws
  nocaps throughput +0.6%, litrun `floor` short +0.8%) are inside the +-0.7%
  window drift.

Also settled by the window (no pcrec action):

- **grok +19% did not repeat.** `wild-logparse-quotedstring-grok` caps short:
  7388f1c0 window 1 2,525.2 ns, window 3 2,149.0, b8337c33 2,147.0; program-
  identical at all four records, emitted C differs in three lines (banner,
  header include name, `.abi`). The +19% was that record's, not the abi 72 > 73
  step's. The bench files nothing.
- **Vectorscan SOM reading** (relay ask 3, cross-window: the Vectorscan
  records are 1.5-2 days older, no same-window control, so only the order of
  magnitude counts): against `block-som` pcrec-nocaps wins every tail cell,
  `tail-word-eoz` 21,909 ns vs 22,253,652 (x1,016), `tail-space-eol` 21,971 vs
  18,044,599 (x821), the other three x31,700 to x164,000; on the two 61,440-byte
  matching bodies x6.1 faster (21,776 vs 133,476; 21,798 vs 133,332). The two
  losses (x55.6 and x21.7) exist only against the no-SOM arm, which reports a
  boolean and no span.

### Proposed disposition of plan row [START-LANDING] (a proposal; plan.md not edited)

The row's own text says "REMAINS: SL4 bench relay (I-145)". O-97 is that
relay's answer, and it matches the design's prediction on every axis the
design made one (population exact; twins' direction and rough size, -20 to
-42%; null clean). Propose:

1. **Flip to `STATE:completed`** with a closure note citing this file, O-97
   and the ledger, and archive it to `plan_completed.md` (the admin2 / closefold
   convention). Everything it chartered shipped: SL1-SL3 merged at sltri 14eda255
   (abi 74, bits 53/54), SL4 relayed and answered.
2. **Carry the one residue** (ask 1, the utf8 search-short slowdown) as a
   named follow-up, not as an open [START-LANDING]: either a `K105`
   PERFORMANCE entry (ACCEPTED pending the bounded attribution of §2) or a
   one-line sub-row, the manager's choice of home. It is a performance
   residue, not a correctness one: answers are identical (checked at every
   startpos and against libpcre2 10.46 on ill-formed utf8).
3. **Rows to grep per the close-out rule** (done): only [ENG-TDFA]
   (names [START-LANDING] as the home of the exact-condition start half;
   unaffected, it was ruled "build lambda, not the exact condition"),
   [ENG-TACTICS] (§3 below) and [IFACE-PUSH] (flag-bit count, 55 of 64 used,
   unchanged) mention it. No row names it as a gate that this closing opens.
4. The bench's own request, `~/pcrec` on the bench box (a detached HEAD that
   predates b8337c33, so `tools/frontpage.py`'s `git describe` fails) is the
   manager's to action, see §5.

## 2. Triage of the three asks

Rule applied: the one-pass loss rule (residual losses only slightly above
noise get ONE bounded effort, then accept; large or reproducible losses get
fixed), plus the high-impact-focus rule (obscure items get a short answer,
not a measurement lane). "Noise" is the ledger's: the null p5-p95 is x0.990 to
x1.008 and the cross-window drift +-0.7%.

### Ask 1. Is the utf8 search-short slowdown expected (12 patterns, 24 cells)?

**Asked.** Is there a per-call cost in the utf8 landing / end-minus-width
path that a later pin removes? The cells: `prp-lu` x1.060, `ci-neg-fold`
x1.054, `asr-lb-neg` x1.052 (end-minus-width), `cls-dot` x1.051,
`cls-neg-single` x1.049, `lit-offset-at-tail` x1.028, `lit-offset-at-head`
x1.026, `floor` x1.020, `lit-1ch-2b` x1.018, `prp-greek` x1.016,
`alt-mixed-width` x1.016, `qnt-lazy-2b` x1.015; +10 to +92 ns on 770-1,870 ns
cells, DISJ in both configs; 10 of the 24 cells are `end-minus-width`, 14 are
`landing`. 56 utf8 patterns flipped and 48 have a faster cell; the bench
hypothesizes a per-call cost in the landing / ill-formed-step path.

**Pcrec-side facts.**

- Not predicted, and not explained by the cost pcrec measured. The design
  (`start_landing.md` §5.6 and the Q2 ruling's happy-path note) prices the
  post-loop guard at one well-predicted decode per REPORTED MATCH, nothing
  in the scan loop. slbuild measured it: `.` +0.13 ns per match, `\p{L}+`
  +1.2 ns, `[a-zé]+` +0.4 ns (find-all over 1 MiB, interleaved, scratch tier,
  `slbuild_report.md` Q2 (4)). The bench's +10 to +92 ns per call is one to
  two orders larger, so the guard decode alone is not the story.
- The design's "could another regime flip a decision" paragraph says a
  short-subject search shrinks the walk (the reverse pass is bounded by the
  match) and the rows "never add work on well-formed text"; the record store
  is one store per landing. That reasoning holds for the reverse walk saved,
  and does not cover the new rows' fixed entry (landing record, post-loop
  call, possibly a non-inlined decode helper), which is where a per-call term
  would live. This is a hypothesis from reading, not a measurement.
- Two of the 12 may be a different mechanism altogether. `lit-offset-at-head`
  and `lit-1ch-4b` are the [U8-PICK] pick defects (u8pick0_report: wrong
  necessary byte in BOTH encodings), and `floor`/`lit-1ch-2b` sit on cells
  whose absolute cost is a `memchr` floor; a layout or entry-term shift of
  +10 ns reads as +2% there. The bench's hypothesis is not exclusive of this.
- No scheduled pin removes it. [REQ-HANDOFF-L1] (built, not merged, waits on
  kit R-15) and the `rev-end-width` change (K103 fix (b)) both touch the
  `end-minus-width` row's shape, but rewtwin's twin DECLINES under utf8
  (n-W may land mid-character), so neither reaches these cells.

**Above noise?** Yes for the 1.5%-and-over cells (reproducible, DISJ in both
configs, null band under 1%); slightly above for the 1.3-1.5% ones. In
absolute terms it is small beside the same set's gains (utf8 `end-minus-width`
67 better vs 10 worse; `landing` 69 vs 14; the set's reporter row reads 70
improve / 14 regress). That is exactly the one-pass rule's case.

**Proposed disposition: ONE bounded read-only lane, then accept.** Do not
build anything. Cheapest next action, no timing needed for the first half:
for `prp-lu`, `cls-dot` and `lit-offset-at-tail` (one per mechanism guess),
compile at 7388f1c0 and b8337c33 with `-p rx -e utf8`, diff the emitted C and
`--emit-facts`, and name the new text on the short-call path (record store,
guard call, whether the decode helper is inlined). The measurement half is a
scratch-tier twin on the dev box: default vs `-fno-start-landing
-fno-start-width` vs a guard-deleted copy, over the bench's published utf8
subjects; the deny pair restores the reverse pass, so the answer is "landing
rows vs reverse pass" exactly. If the delta is the guard or an un-inlined
decode, one decline or inline predicate survey (the rule's single allowed
effort); if it is layout, accept and note it in the pin checklist. A sonnet
lane fits; no `make test`.

**Bench-only questions to relay (not answerable from pcrec's side):**

1. In the 24 cells, is the slowdown a flat per-subject term (every one of the
   75-112 subjects +x ns) or concentrated on subjects that match near the
   end / carry a multibyte character at the landing? The bench's subject-grain
   slices answer it without a new run. Flat means an entry term; concentrated
   means the guard or the decode.
2. Would the bench run a `-fno-start-landing -fno-start-width` arm of
   b8337c33 on those 12 utf8 patterns (search-short only), as a scratch
   control? It attributes the loss exactly but costs a window slot; ask only
   if the pcrec-side diff does not settle it.

### Ask 2. emit-c x2.53 on `wild-datetime-datefinder-alternation` (173 > 437 ms)?

**Asked.** Is it the new start-recovery analysis on a very wide DFA? The
cell: nocaps, 891,859 B emit, program-identical; the gcc phase unchanged;
the other 119 emit-c cells over 10 ms move at most x1.18 (the trend page's
total compile time x1.53 nocaps / x1.83 caps, the caps side being a refusal
at both pins).

**Pcrec-side facts.**

- The only compile-time work START-LANDING added is the SL1 facts: `width`
  (`pcrec_width_walk`, a union-frontier walk that can step more than 255
  times and was made to reset its generation stamp on wrap for that reason)
  and `land_char` (`pcrec_land_char`, `src/facts/kset.c`), which is an EXACT
  per-byte walk: for each of 256 bytes, the successors of every live
  frontier state, closed with `wclose`, plus a memoized mid-character descent
  under utf8. Cost is on the order of 256 x frontier x closure per frontier,
  and the datefinder alternation (month, weekday and zone names) has a very
  wide start frontier. So the bench's reading is plausible by construction.
  It is NOT measured: no compile-time census was run on SL1 (slbuild's
  report carries no compile-CPU figure), and the `k67` census instrument
  `scripts/compile_time_census.py` exists but was not re-run.
- Both facts are asked by the new RECOVER rows, so they run whenever a DFA
  artifact reaches the RECOVER slot, including when the answer is a decline.
  A decline early in the walk is cheap; a pattern whose walk runs long before
  declining (or holding) pays it all.
- Not the same item as the 2026-09-30 witness filed on [OPT-LITSCAN]
  (the same pattern's VM program bytes 508,413 > 605,083 under D127's floor
  of 3). That one is size at `--engine=vm`; this is compile time at auto.

**Above noise?** The ratio is large and the cell is one of 120; the absolute
is +264 ms on a compile whose gcc phase (the larger half) is unchanged and
whose budget (D45, 10 s) it is nowhere near. By the high-impact-focus rule
this is a short answer, not a lane.

**Proposed disposition: answer from existing facts, with a one-command
check, then accept or file.** Cheapest next action (manager, about a minute,
run it as a paired compile, not a benchmark): compile the pattern with
default flags and with `-fno-start-landing -fno-start-width` (bits 53/54 deny
both rows, so the facts are never asked) and compare `pcrec`'s own wall; the
bench's emit-c phase is exactly that wall. If the deny pair restores about 173
ms, the answer to the bench is "yes, SL1's facts on a wide frontier", and a
BOONIES row filed on the facts walk (a `land_char`/`width` work bound as a
DECLINE, not a tuned constant, per the suspect-constants rule) is enough;
nothing is scheduled. If it does not restore it, it is a different cause
(e.g. the T1/T2 ladder retry) and the check names it. I did not run it (the
brief forbids timing).

### Ask 3. Does K103's trigger count the litrun whole rows (unchanged at state 3)?

**Asked.** The litrun `(?:P)\z` whole-subject rows read 0.997-1.006 across
state 3: START-LANDING neither adds to nor removes the [OPT-REVEND] price.

**Pcrec-side facts.**

- K103 already contains these rows: its witness list is O-96 (c)2, the
  litrun whole forms (`alt-foo-tails` x1.077, `lit-l4` x1.034, `lit-l2`
  x1.032; `lit-l8` x1.022; `lit-l31`/`lit-l40` WIN by 2%). So they are the
  evidence, not a new trigger. State 3 only confirms they stand where REVEND
  left them (the ledger's §7.1 gives the exact texts and ratios, relayed
  as I-146 asked).
- K103's trigger (D77) is "a short-subject cell where the entry floor is the
  cost at rank". Those rows are 3-8% on 264-405 ns whole-subject calls, i.e.
  +9 to +21 ns each; they are not at rank in any weighted list, and K103
  stays ACCEPTED / UNSCHEDULED.
- The one bounded effort the rule allows was already spent: lane rewtwin
  (2026-10-11, scratch, Zen 4) measured fix (b). The floor did NOT reproduce
  on the dev box (today's rev-end is 1.7-2.6x faster than `-fno-rev-end`
  on every (c)2 cell except github-pat, K104). The twin with the verify
  INLINED wins `abc$` -21%, `lit-l31` -24%, `lit-l40` -31%, aws nocaps -44%,
  github-pat nocaps -72%, but is +1 to +8% on W <= 4 literals (and a CALLED
  verify loses 27-35%). Its own open relay question is whether the +2 to 8%
  is the Zen 1 box or the a15fb77b pin.
- The [OPT-REVEND] `rev-end-width` trigger text is "a bench end-pinned
  fixed-width cell where the walk exceeds 10% of the cell (a CHOSEN
  threshold, unmeasured)". This ledger gives per-call medians (263.7-404.9 ns)
  but no walk share, so it cannot answer that either way.

**Above noise?** The whole rows are +2 to +8% at REVEND, reproducible,
both configs, but unmoved since; they are known, filed and measured once.

**Proposed disposition: answer from existing facts; accept.** No. The litrun
whole rows are K103's witnesses, not a trigger; state 3 adds nothing to K103
and nothing to the `rev-end-width` row. No lane. The one open item is the
bench-only relay already queued in K103's text: a `-fno-rev-end` (bit 52)
arm of the litrun whole rows on the bench box (Zen 1), to separate "the box
has an entry floor the dev box lacks" from "the pin does". Ask it only if the
bench has a spare slot; it is not needed to hold K103.

## 3. The [ENG-TACTICS] table (ledger §6)

Set-grain medians at b8337c33, window 3, 5 trials, ns. `T` is
`large-subject-throughput`, `S` is `short-subject-search`, `W` is
`match-compliance` whole-subject (`(?:...)\z`). Start / prefilter is the
stamp (caps and nocaps identical). Min-max ranges are in the ledger.

### loglines (plain form; every row `dfa / unanchored` except `level-context`, `vm`)

| pattern | regime | caps | nocaps | start / prefilter |
|---|---|---|---|---|
| `bignum` | T | 7,289,045.9 | 7,261,136.4 | reverse-pass / first-class-bounded |
| `bignum` | S | 237,285.8 | 237,399.7 | reverse-pass / first-class-bounded |
| `floor` | T | 2,842,707.3 | 2,841,138.2 | end-minus-width / memchr |
| `floor` | S | 1,512.2 | 1,511.8 | end-minus-width / memchr |
| `hex32-id` | T | 11,052,363.4 | 11,057,040.6 | end-minus-width / first-class-bounded |
| `hex32-id` | S | 297,968.6 | 297,938.2 | end-minus-width / first-class-bounded |
| `http-5xx` | T | 280,071.5 | 280,542.3 | reverse-pass / memchr-bounded |
| `http-5xx` | S | 4,944.6 | 5,153.8 | reverse-pass / memchr-bounded |
| `ipv4` | T | 6,938,840.7 | 6,946,944.0 | reverse-pass / byte-class |
| `ipv4` | S | 207,712.9 | 207,664.9 | reverse-pass / byte-class |
| `ipv6` | T | 10,616,540.5 | 10,622,994.8 | reverse-pass / byte-class |
| `ipv6` | S | 260,510.0 | 259,378.0 | reverse-pass / byte-class |
| `iso-ts` | T | 1,152,508.5 | 1,152,760.2 | reverse-pass / offset-set |
| `iso-ts` | S | 20,564.2 | 20,552.4 | reverse-pass / offset-set |
| `kv-quoted` | T | 202,809.9 | 202,819.1 | reverse-pass / first-class-bounded |
| `kv-quoted` | S | 5,700.0 | 5,699.5 | reverse-pass / first-class-bounded |
| `level-context` | T | 2,290,791.2 | 2,291,346.3 | reverse-pass / first-class-bounded |
| `level-context` | S | 83,955.6 | 83,889.7 | reverse-pass / first-class-bounded |
| `stack-frame` | T | 1,307,579.0 | 1,308,074.1 | reverse-pass / offset-set-bounded |
| `stack-frame` | S | 33,358.7 | 33,323.2 | reverse-pass / offset-set-bounded |
| `uuid` | T | 1,060,907.6 | 1,061,509.7 | end-minus-width / offset-set-bounded |
| `uuid` | S | 20,372.4 | 20,331.1 | end-minus-width / offset-set-bounded |

(`http-5xx` nocaps short is the ledger's only "non-mover that moved":
4,949.0 > 5,153.8, x1.041, one config, one regime, not repeated in caps.)

### altwide sfx-* (b8337c33 only; `dfa`, prefilter `byte-class` on T and S, `none` on W)

| pattern | regime | caps | nocaps | scan / start |
|---|---|---|---|---|
| `sfx-64` | T | 2,803,525.6 | 2,801,848.2 | unanchored / reverse-pass |
| `sfx-64` | W | 423.4 | 424.9 | rev-end / reverse-pass |
| `sfx-64` | S | 1,016.6 | 1,021.2 | unanchored / reverse-pass |
| `sfx-256` | T | 2,618,112.9 | 2,621,032.6 | unanchored / reverse-pass |
| `sfx-256` | W | 428.0 | 429.4 | rev-end / reverse-pass |
| `sfx-256` | S | 1,016.4 | 1,019.2 | unanchored / reverse-pass |
| `sfx-512` | T | 1,865,818.8 | 1,866,491.6 | unanchored / reverse-pass |
| `sfx-512` | W | 447.0 | 447.2 | rev-end / reverse-pass |
| `sfx-512` | S | 1,017.9 | 1,018.2 | unanchored / reverse-pass |

### Reading against plan row [ENG-TACTICS]'s HELD triggers

[ENG-TACTICS] holds `rev-inner` (Frank, 2026-10-11, "a bit of a house of
cards") on a re-worded trigger: a weighted cell where the RE-ENTERED handoff
([REQ-HANDOFF-L1]) leaves a measured gap, or an unbounded prefix it cannot
serve. [OPT-REVEND] holds `rev-end-width` on "a bench end-pinned fixed-width
cell where the walk exceeds 10% of the cell". This table is the baseline for
the first and says nothing new for the second, and neither trigger fires on
it.

- **START-LANDING did not touch the rev-inner population.** `ipv6`
  (10.62 ms T, 260.5 us S; walk_survey's 5.83 ms of the K12 total), `ipv4`,
  `kv-quoted`, `bignum`, `iso-ts`, `stack-frame`, `level-context` and all
  three `sfx-*` stay `reverse-pass`: their starts are not a one-character
  landing nor a fixed width, so the new rows decline and they sit where
  7388f1c0 left them. The only loglines patterns that flipped (`floor`,
  `hex32-id`, `uuid`) are not rev-inner candidates. So state 3 neither
  retires nor shrinks the ~14 ms upper estimate (rincensus: ipv6, sfx-*, six
  small patterns) behind the HELD row.
- **The first trigger cannot be read yet.** It is conditioned on
  [REQ-HANDOFF-L1], which is built (lane/rlhbuild 39684936, abi 74 > 75) but
  NOT merged (it waits on kit R-15; an integration lane is owed). rlhtwin's
  scratch result is the only handoff-gap evidence so far: ENTRY-only
  generalisation captures 0-6% of reverse-inner's win, the re-entered handoff
  109-120% on ipv6/ipv4 and reaches sfx-64's -93% without G2, and `kv-quoted`
  gains nothing. The table's `ipv6` T (10.6 ms), `sfx-64` T (2.80 ms) and the
  `kv-quoted` cells are the "before" figures the bench's next window reads
  that merge against; `sfx-*` short cells are flat at about 1.02 us across
  all three, a floor, not a gap.
- **The second trigger (rev-end-width) gets no new evidence here.** The
  `sfx-*` whole forms (423-447 ns, `rev-end / reverse-pass`) are variable-width
  suffix patterns, not the fixed-width case the row names; the fixed-width
  evidence is the litrun whole rows (ask 3), unchanged at state 3, and the
  ledger carries no walk-share per call. The 10% test stays unmeasured by this
  window; rewtwin's twin is the measurement on file.
- **Net.** Both rows stay HELD. Nothing in state 3 raises or lowers their
  priority; the one actionable consequence is that when [REQ-HANDOFF-L1]
  merges, this table's rows `ipv6`, `ipv4`, `kv-quoted`, `sfx-64/256/512` are
  the cells whose ratio decides the first trigger, and b8337c33 is their pin.

## 4. Findings on the bench's reporting

- The reporter's D119 bar and the ledger's overlap test are different cuts
  (ledger §0 item 1): capability's `short >= 1us` stratum sets its null band at
  +-24.69% from one noisy program-identical cell (`phone-palindrome-6`
  nocaps), so the reporter reads capability's 16 caps movers as "1 improve,
  15 within the bar" where the overlap test reads 8 better / 1 worse / 7 ov.
  Quote the cut with the number.
- The cross-window control is clean to +-0.7% over 422 cells, with four tails
  (all capability): grok caps short 0.851 (window 1's slow reading), 
  `bracket-array-define` throughput 1.158 (a mixed-state record), and
  `phone-palindrome-6` nocaps short 1.118 and throughput 0.910 (the set's
  loudest cell).
- `ci-ucp-invariance` is in the compile census but unsupported by declaration
  on `pcrec-*-utf8`, so the bench's 56 utf8 movers read against the census's 57.

## 5. Open items for the manager

- Ask 1: authorize (or decline) the one bounded attribution lane; relay the
  two bench-only questions.
- Ask 2: the one-command paired compile (§2); a BOONIES row only if the deny
  pair restores the time.
- Ask 3: nothing owed; the K103 relay (a `-fno-rev-end` bench arm) is optional.
- The bench's request: `~/pcrec` on ubuntubudu (`/home/duxevents/pcrec`)
  needs `git fetch` so `git describe` finds b8337c33. It is in the pcrec
  mandate but is a light op on the bench's box and outside this lane.
- The reply (I-147 or its successor) to the bench: confirm the verdict, answer
  (f) as "not predicted; attribution pending, no pin scheduled to remove it",
  (g) as "probably SL1's facts on a wide frontier, check pending", (h) as "K103's
  witnesses, not a trigger". Written by the manager to
  `inbox_from_pcrec.md` as a single-file `[inbox]` commit.
