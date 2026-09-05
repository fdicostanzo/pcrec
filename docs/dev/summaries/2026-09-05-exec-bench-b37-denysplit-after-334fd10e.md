# Executive summary: the [B37] deny-flag AFTER, pin 334fd10e

Window 2026-09-05 03:48–07:22 EDT on ubuntubudu (the bench's own grant,
run in the gap before our battery slot). Ten records measured at pcrec
pin `334fd10e` (abi 22): `altwide@0.2` × {auto, noisland, nocaps, vm,
vm-in}, `loglines@0.1` × {auto, noedge}, `bounded@0.3` × {auto, vm,
auto-clang}. Baselines per finding: `1989c62` (abi 15, the 2026-09-02
full suite) and `288d505` (abi 17). Store grew to 144 records (134
measured). Hygiene was the cleanest window to date: 10/10 cells at
attempt 1, pre-flight drift 0.0–1.2% (mean 0.28%), and **0 disagreeing
answer rows out of 23,424 — a first**; zero wrong answers anywhere.
Sources: pcrec-bench ledger
`docs/dev/ledgers/2026-09-05-b37-denysplit-after-334fd10e.md` (961
lines, every number cited) and outbox O-17; our answers went back as
I-50 (bench inbox, e23b782).

## 1. The big win, explained: the VM alternation island

Between abi 15 and abi 22, six optimization rows landed. The one that
moved the board is **[ENG-ISL] STEP 1 — the VM alternation island**, a
trie dispatch that replaced the VM's serial-try lowering for wide
literal alternations, with the [CC-DIFF] entry-chain work (abi 21→22)
multiplying it on small programs.

**What it replaced.** `w-256` is a 256-branch alternation of random
lowercase words (`wordA|wordB|…`, 256 branches); `srt-256` is the SAME
256 words sorted. The old lowering tried branches one at a time at every
subject position: compare bytes against branch 1, fail, restore, branch
2, … — so a failing position could pay hundreds of partial comparisons,
re-reading the same subject bytes, and branch ORDER was a real cost
variable: the bench measured the unsorted spelling **×8.87 slower** than
the sorted one on identical language. Each branch also emitted its own
code chain — 341 KB for w-256.

**What it does now.** The whole alternation compiles into ONE shared
byte trie (`docs/design/alt_dispatch_study.md`, algorithm (e), Frank's
R1 ruling): at each position the VM walks the trie once — every subject
byte examined once — and a two-sided commit rule (commit only when
neither a deeper path nor an already-deferred shallower candidate can
beat this branch index) preserves PCRE2's leftmost-first preference
exactly while pushing AT MOST ONE resume frame per dispatch. The trie is
order-insensitive by construction: both spellings build the identical
machine.

**What that measured to, at the bench:**

| quantity | before (1989c62) | after (334fd10e) |
|---|---|---|
| `w-256 ÷ srt-256` throughput (the order effect) | **×8.87** | **×1.0007** (per subject 0.9994–1.0014) |
| the two artifacts | 341,111 vs 301,957 B | **byte-identical, 292,043 B** |
| `w-256` forced-VM throughput | 1,931 ms/set | **15.9 ms/set (×121.57 faster)** |
| island's effect over 54 VM cells | — | ×0.0014–0.91, **median ×0.026** (~40×) |
| VM beats PCRE2's JIT | **3 of 40** cells | **32 of 44** cells |
| VM compile-wall refusals (500 KB code cap) | 26 of 66 | **22 of 66** (`w-384` at 85.6% of cap, `pfx3-512` at 440,187 B both crossed) |

The JIT scoreboard row is the headline: PCRE2's JIT is the fastest
widely-deployed regex execution tier, and pcrec's VM route — plain
ahead-of-time gcc-compiled C, no runtime code generation, no
dependencies — now beats it on 32 of 44 wide-alternation cells, e.g.
`vm ÷ jit` **0.029** on `s-512` and **0.067** on `w-256` (i.e. ×15–35
faster), crossing below 1.0 by width 64. The bench's own prediction P11
("no crossing across the ladder") is refuted in our favour — the ratio
moved a factor of 70 across the ladder. The smaller code also moved the
walls: every VM refusal diagnostic shrank (`s-4096` 3.74 MB → 2.24 MB),
and two patterns (`w-384`, `pfx3-512` — the latter unpredicted) crossed
into compiling.

**Honest frame.** This is the FORCED-VM axis — a comparability
instrument. Our default (`auto`) selects the DFA on all 34 compiled
altwide cells, and the DFA is still ahead of our own VM on every
compiled throughput cell (vm ÷ auto 3.8–8.0). But the island closed the
match-axis inversion too: whole-subject `match` on the VM route is now
BELOW the DFA's on every island form (0.75–0.86, was 19–376), and the
margin the DFA holds is no longer ×660 but single digits — the VM went
from a liability to a credible second engine, which is exactly what the
size/speed dial and the refusal-wall story need.

## 2. Findings (the rest)

- **[OPT-EDGE]'s dispatch rework paid off on its third sample.** The
  scan edge's cost on `iso-ts` (an ISO-timestamp matcher over log
  lines, the set's most edge-bearing artifact, 8 edges) fell from
  ×1.09/×1.07 (search/throughput) to **×1.016/×1.006**; the deny arm
  (`noedge`) is FLAT across all three pins (1,142,263 / 1,142,674 /
  1,142,842 ns/set) — a textbook control saying the pin moved nothing
  on loglines except the edge's dispatch. I-44's predicted 0.99–1.01
  band met on throughput, missed by 0.6% on search.
- **The DFA's whole-subject `match` entry got ×0.57–0.92 faster on
  every altwide cell** (`w-64` 880.4 → 503.2 ns/set; failing subjects
  ×0.29–0.79) — an unlooked-for win spanning abi 16–22. Prime suspect
  is [CC-DIFF]'s uniform-table fold (the only in-window change reaching
  edge-free artifacts, which also moved ×0.93); bisect probe owed.
- **The fold witnesses confirmed the mechanism transfers** (not the
  exact bytes): `cls-upto-4` timing ×0.627 on gcc with the .rodata
  section gone; `dig-upto-16` (`\d{1,16}`) throughput ×0.594.
- **The bounded ladder's digit rungs moved ×0.70** (5.05 → 3.55 ns/B) —
  our I-50 answer: mechanism-identical to iso-ts's 29→15-instruction
  generic path (same scan-edge dispatch commits). The whole-form
  customers did NOT move (2048÷1024 still 1.984; `d-01024` still
  ×39.1) — [OPT-VEDGE]'s BEFORE holds, its charter intact.
- **The tripwire we asked for FIRED**: forced-VM `floor` (the one-byte
  literal `:`) got **×2.0 slower** on throughput on both sets (0.296 →
  0.593 ns/B) — the ONLY `forward`-shaped artifact that got slower
  while its 645-byte siblings got ×0.50–0.70 faster. I-50 carries the
  mechanism read (floor is rung-free; its entire failing-path cost is
  the outer retry loop the entry-chain merge touched) and the
  one-cell discriminating probe for the quiet box.
- **`RX_VM_PROGRAM_BYTES` vs code-bytes reconciled and verified to the
  byte** (I-50 §1): different population AND different comment policy —
  program region only with comments vs whole file without; w-256
  reproduces the bench's 305,686 exactly.

## 3. Where we stand: ahead / behind

Against **PCRE2 JIT** (the hard opponent), at 334fd10e:

| axis | standing | numbers |
|---|---|---|
| wide alternations, forced VM | **AHEAD 32/44** | vm÷jit 0.029 (`s-512`) – 0.40 (`w-64`); was 3/40 |
| wide alternations, auto (DFA) | **AHEAD, flat under width** | `w-256` auto 2.90 ms vs jit 238.4 ms ≈ **×82**; auto flat 2.3–3.4 ms across the ladder where the JIT rises with width |
| narrow alternations | BEHIND | `w-8` vm÷jit 2.79; `sh1-64` 1.53; `nar4-64` 1.07 |
| caseless wide alternation | BEHIND | `ci-256` vm÷jit 7.9 — the island declines `(?i)` today; abi 23's cls-fold family is the adjacent lever |
| shared-prefix family | BEHIND | `pfx3-256` 8.25 (though `pfx3-512` newly compiles at 3.32) |
| tiny-literal forced VM | BEHIND (regression) | `floor` throughput 15.75 — the ×2.0 tripwire, chartered |
| compile coverage | MIXED | VM refuses 22/66, DFA 32/66 at the caps (JIT compiles all); but our refusals cost 0.8 s (VM) vs the DFA's 113.7 s per pass — the DFA-wall cost is the standing sore |

Against **PCRE2 interp**: ahead everywhere measured, one to three orders
(`w-384` vm 16.5 ms/set vs interp 3,492 ms — ×211).

## 4. Surprises

1. **The order effect vanished to four decimal places** (1.0007) —
   predicted "within 2 bytes", landed at 0 bytes: trie construction is
   order-insensitive, so "candidate 2 shipped" is confirmed and no sort
   pass will ever be needed.
2. **`pfx3-512` crossed the VM wall unpredicted** — our own wall
   statement was derived on the w-family; the island's 0.81 program
   shrink covers pfx3 too. The bench's size census §1 is stale by
   −18…−26% per rung on the VM route (named to [ENG-ISL] in I-50).
3. **The canary worked**: the forced-VM floor tripwire the bench set at
   our request fired at ×2.0 and isolated a real regression the whole
   green battery never saw — the deny-flag/tripwire discipline is
   earning its keep on their side as D27 does on ours.
4. **The I-37 cell can't be probed the way I-44 planned** — it is a DFA
   artifact; there is no `RX_VM_ENTRY_SHAPE` stamp on it. Where
   `forward` DOES stamp under auto, gcc caught clang (clang÷gcc 0.630 →
   0.930).
5. **The island costs +1.5% throughput on framed hybrids** (`ctx-*`)
   while the same programs' match cells gain ×0.65–0.68 — a
   which-budget-binds split, ask (iv), unprobed.
6. **One rung moved backwards in a faster ladder**: `cls-upto-32`
   letters ×1.14 slower while width 4 got ×0.59 faster — on artifacts
   we verified are stamp-identical apart from the embedded bound.

## 5. Impact

- The compile-to-C thesis now has its strongest external validation:
  ahead-of-time, dependency-free artifacts beating PCRE2's JIT on the
  workload class (wide alternations) where the JIT was ahead ×6–15 four
  days ago, with zero answer divergence across 23,424 rows.
- [ENG-ISL]'s open design question (sort pass?) is closed by
  measurement: never needed.
- The VM is now a credible fallback where the DFA refuses — the walls
  themselves moved, and every refusal diagnostic shrank.
- Chartered follow-ups got sharper, not more numerous: the floor
  regression (ask (i)) has a one-cell discriminating probe; the DFA
  `_match` movement (ask (vi)) has a two-suspect bisect; [OPT-VEDGE]'s
  customer population is confirmed untouched and waiting.
- The DFA refusal wall (32/66 altwide at the 1 MB source cap, 113.7 s
  of refusal cost per pass) is now the most visible gap on the board.

## 6. Next steps

1. Today's battery at 37f5ae02 (abi 23) on ubuntubudu — running as this
   is written (launched 11:45 EDT; box granted early) — including PC-3
   against the reference 10.46, the utf8-owed items, and the
   capability-probe verdict line for the bench.
2. After the battery, on the quiet box: the O-16 (iii) probe (plain
   `_match` vs `_in`), the floor entry-shape cell, the DFA-match bisect
   prep. Results to the bench inbox with DONE.
3. [B39] — the bench's abi-23 re-pin (the cls-fold AFTER) on Frank's
   go; their census re-derivation closes the staleness.
4. The `--vm-entry-shape` `--list-axes` row ([REG-SV]-class) and the
   rest of the admin queue (wake.md).
5. K49's fix and M5.0 stages 3–5 remain on Frank's word.
