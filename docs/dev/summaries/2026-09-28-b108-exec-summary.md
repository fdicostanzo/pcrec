# EXECUTIVE SUMMARY — [B108]: `[OPT-LITSCAN]` S2a on the bench at pin `a32bc86e` (2026-09-28)

For Frank. pcrec-bench measured S2a (the VM's exact literal run as one
compare, abi 41) in one window on 2026-09-27/28 (x86_64, gcc 15.2.0, -O2).
It used a same-window twin (`auto` against `auto -fno-lit-run`) plus a new
set, `litrun@0.1`, built from s2a_report §7.1/§7.2.

Sources:
- pcrec-bench's ledger `docs/dev/ledgers/2026-09-28-b108-a32bc86e.md`;
- outbox O-64;
- my reading `docs/dev/optloop/b108_reading.md`, which holds every
  derivation, the per-prediction verdict table and the compile-side
  probes.

## 1. FINDINGS

- **Correctness: 0 answer changes** on all 17 records.
- **The DFA-null prediction holds exactly**: 153 of 153 DFA artifacts are
  byte-identical between the arms, and their timing is the band itself.
- **S2a's named FASTER population is not faster on x86.**
  - Five of the seven named cells are null: ctx throughput, `level-context`,
    userpass, github-pat, slack.
  - Two are slower beyond the twin's ±1% band:
    - aws throughput ×1.037;
    - ctx-lazy-256/1024 whole-subject match ×1.034/×1.042.
  - The one scoreable FLAT cell, `logparse-atomic-removed`, is ×1.107
    slower.
  - The other seven FLAT cells are **OWED**: the bench's roster omitted the
    deny testee, and they are re-measuring.
- **Where the compare actually runs per position, S2a wins big.** On the
  forced-VM L-sweep with pre-checks denied:
  - match costs 0.93× → 0.25× as L grows from 2 to 40;
  - the L−1 subject is flat at ~6.3 ns, against a chain growing to 19.8 ns.
- **Size wins everywhere**: VM programs 26-41% smaller on the movers, and
  the datefinder acceptance mover is confirmed on the auto route too.
- **Factoring × lit-run (§7.1)**: no sign flip on either route. Factoring
  stays worth ×1.25-×2.9 on aws.
- **The x86 memcmp column is closed.** gcc-15 inlines every length 1-64 at
  -O2, so the arm64 L=31 cliff does not exist there. It is added to
  `memcmp_lowering_study.md` §12.
- **The D119 bar is NOT met on the named population.** No target improves
  beyond its band, and three regress.

## 2. SURPRISES

- **The slowdowns are not in S2a's instructions** (reading §1).
  - I assembled six of the affected artifacts with the bench's own compiler,
    in both arms.
  - On every one, **every function except the VM body is
    instruction-identical**. The entry path gains zero instructions.
  - The VM body only shrinks: 5-35% fewer instructions, and 9-45% fewer
    branches.
  - What remains:
    - `logparse-atomic-removed`: gcc now saves one more register, and saves
      them all *before* the 2-byte `": "` test instead of after it;
    - aws's hot scan loop: byte-identical, and moved by exactly 64 bytes;
    - the three ctx-lazy sisters: identical VM bodies except one constant,
      yet they read 1.010 / 1.034 / 1.042.
  - These are codegen and placement effects of ≤0.7 ns per call, not a
    property of the compare.
- **The prediction chose its population by what the program contains, not
  by what the subjects execute.** On every named cell a prefilter answers
  first, so the VM compare runs at most once per match. That is why the
  wins S2a does have (the L-sweep) never showed on the named cells.
- **Unasked, and bigger than S2a: the VM route's pre-check costs ~5.5 ns per
  `memchr` pass per `rx_search` call.**
  - On dense-match find-all it is paid per match: ×2-×9, and 49.8 against
    5.3 ns per match at L=40.
  - The pass count is 1, 2 or 10 by literal length. The ten passes at L=40
    are partly [K66]'s 32-byte whole-run cap, which sends eight bytes of the
    same literal to eight separate `memchr` scans.
  - It is independent of lit-run.
  - It is the same per-call family as LITSCAN F1: a pre-check priced per
    byte and never per call.

## 3. IMPACT

- **No correctness risk.** Answers are identical; the DFA route is
  untouched.
- **S2a's speed claim for the bench population is withdrawn. Its size claim
  and the acceptance mover stand.** It remains the compare primitive S4
  (caseless) builds on.
- **The 2-byte-run question now has three independent witnesses**, all
  per-call costs:
  - F4's `asr-lb-fixed` +30% (Mac scratch);
  - `bnd-l2` +1.54 ns;
  - `logparse-atomic-removed`'s register saves at `": "`.
  That makes a narrowing (`L ≥ 3`) worth measuring. It is not yet worth
  building.
- **The pre-check finding touches every forced-VM or hybrid-declined
  artifact that has a necessary run and is called in find-all**, not just
  S2a's. It belongs with the kit's pre-check cost model (F1's owner).

## 4. NEXT STEPS (D125: the next optimization cycle is HELD; recommend and file)

| item | recommendation | owner |
|---|---|---|
| S2a default | **KEEP default-on.** Record in the plan row that the bench effect on the named population is codegen/placement-only (reading §1.5). | Frank rules; manager records |
| 2-byte narrowing (`L ≥ 3`) | **FILE as `[OPT-LITSCAN]` tail F5, measured first.** Trigger: a bench x86 twin of lp and `asr-lb-fixed` with the 2-byte run respelled as the chain. Build only if it removes their cost. | stock-take |
| dense-match pre-check | **FILE as `[OPT-LITSCAN]` tail F6** (draft text in reading §5), beside F1. It is not a new row, and not `[SEL-COST]` or `[OPT-HYB-RESEED]`. | stock-take |
| deny by default | **Not recommended now.** Revisit when the owed capability × auto-nolitrun re-measure lands, and only if the seven FLAT cells regress broadly. | after the bench's re-measure |
| bench questions | Seven, in reading §6: the aws match count, a placement twin, the owed re-measure, lp's subject composition, the pre-check call count, the first-byte-flip loop alignment, ctx subject identity. | relay via pcrecdev2 |
