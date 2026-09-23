# b2ledger — reading the batch-2 ledger (O-49) against the D119 bar

Lane `b2ledger`, 2026-09-23, opus, branch `lane/b2ledger` from `3e58d700`.
Analysis + compile-side measurement only; nothing under `src/`/`cli`/`lib/`/
`tests/`, nothing written in pcrec-bench, **no clock read on this box**.

**Delivered.** `docs/dev/optloop/cycle2_batch2_reading.md` (813 lines,
§9 the exec-summary addendum at the 40-line bar),
`docs/dev/optloop/b2ledger/` (three instruments + committed JSON + its own
`CLAUDE.md`), `docs/dev/optloop/runs/2026-09-23-o49-b1885a83/` (the ledger,
O-49 and I-95 archived verbatim + a README), and the
`docs/dev/optloop/CLAUDE.md` entry. `plan.md` and the journal untouched, per
the brief.

**Verdicts.** `[OPT-FREQPICK]`'s target MEETS (`nested-comment-rec` 9.3 ms →
23.1 µs on 4/4, the cost model predicting its ABSOLUTE after-value to 0.2%)
and the mechanism carries one hazard its own design note classified as a
gain. `[OPT-REQPOS]` tier 2b's targets meet (−97.6%/−97.9% where the run is
absent) and the **carve-out clause FAILS**. Dispositions in §7.

**The 17 misses: A = 6, B = 6, C = 5**, each classified by compiling the
row's pattern under the ledger's exact config flags with a compiler built
from lane `admitimpl`'s parked fix (`cb437f26`, abi 31, NOT merged) and
diffing the stamps and the emitted pre-check — never by resemblance.

**Six things worth reading the file for.**

1. **The null control is larger this cycle and it is total**: 131 of 192
   capability artifact-configs are program-identical across the pin, and
   **34 of the 34 non-target regressions the ledger NAMES sit on one** — its
   §2.1 top-20 and all 14 of its §2.2, including the +41.09% cell it calls
   "the one genuine outlier". Banded by scale: +8.77% at µs-scale
   throughput, +11.16% at search, **+41.09% below 100 ns**. Only 2 of the
   17 misses lie outside it.
2. **The worst miss, counted exactly.** Tier 2b's emitted loop makes one
   `memchr` CALL per occurrence of its SCAN BYTE, not of the run:
   `router-prefix-order` goes 315 calls → **39,098** (124×), and the model
   reproduces its +80.83% with one free parameter carried from cycle 1
   (`c_call` = 7.72 ns). `reqpos_2b.md` §4.3 prices the loop per `memcmp`
   and is silent about the restart before each one — **97% of the
   regression**.
3. **O-49's largest movement had its sign predicted backwards.**
   `wild-validator-email-owasp`'s +27,010%..+52,757% floor jump is the pick
   moving to an ABSENT byte on a ONE-ATTEMPT artifact, predicted to inside
   the measured range by one full `memchr` pass — and
   `reqbyte_freq_pick.md` §7.1 lists that cell among the effects that "are
   gains". Its acceptance check ("no cell's picked byte goes from absent to
   present") is sound and its converse is missing, so the cell passes it and
   regresses 500×. Class (A): the fix removes it.
4. **The named falsifier cannot answer its own question.**
   `logparse-atomic` is `^`-anchored, so the fix deletes its whole
   pre-check — the cell chosen to falsify the no-decline-rule has no run
   check left to have a rate about — and its largest regression (+41.82% on
   a 49 ns baseline) is numerically indistinguishable from a
   program-identical null cell of the same size (`date-nested-plus`,
   +41.09% on 52 ns). The cell that CAN answer it, `keyword-prefix-order`
   (+59.7%, the ledger's largest carve-out regression), was never named.
5. **The fix's scoping inverts the cost ordering at one cell**, shown by
   compiling `/user|/users` with and without `-fno-req-run` under the fix's
   own compiler: `REQ_WHY` reads **`dominated`** (pre-check removed, 315
   calls) without the run and **`emitted`** (kept, 39,098 calls) with it.
   `admitimpl_report.md` §0 F3's reasoning is sound and is not challenged;
   its named trigger for widening now has a population and a number (§6).
6. **Two ask-vs-design discrepancies**, both inflating the miss count.
   I-95 promotes `tag-depth3-bound`/`tag-pair-match` to TARGETS where
   `reqpos_2b.md` §6.2 classifies them as CARVE-OUTS and predicts no
   improvement; their byte is absent at both pins, so all eight cells do
   identical work and the ledger's 3 MEETS and 2 MISSES are **one non-event
   read twice with opposite signs**. And I-95 calls `nested-comment-rec`
   "the pick's one losing cell" where its note names its two cells as THE
   TARGET CELLS; the phrase appears in neither design note.

**Instrument validation, before any of it was used.** The stamp census
reproduces the bench's §3.3 census **20 of 20 by value**, derived from
emitted `#define` lines rather than from `engine_metadata`. The three
throughput subjects were regenerated and **sha256-checked against
`manifest_throughput.tsv`, 3 of 3**. The design notes' own byte counts
(`/` 30,000, `r` 54,781, `.` 14,826) are reproduced **exactly** once it is
noticed they are `t-1m`-only. And the `REQ_WHY` `one-attempt` population is
**exactly the 9 patterns / 27 artifact-configs
`cycle1_ledger_reading.md` §6 G2 predicted by name**, measured against a
compiler built from the fix rather than from the prediction.

**The trap this lane walked into**, recorded in `b2ledger/CLAUDE.md`: the
cost model's "added cost" framing is valid only where the pre-check PASSES
THROUGH. Where the byte or run is ABSENT the pre-check answers the call and
everything below it never runs, so it REPLACES a pass rather than adding
one — the model over-predicted by **17×** on `wild-secrets-github-pat`'s
DFA route until the artifact was read. That is exactly the population the
mechanism exists to serve.

**Validation COMPLETE** (docs only; no suite applies, no `src/` change).
Three compilers built by `git archive` into the session scratchpad
(`8d716693`, `b1885a83`, `cb437f26`), `make -j2 CC=gcc-16`, all rc=0; no
live `build/` touched; `worktrees/admitimpl` never entered. Control:
`git diff b1885a83..main -- src/ cli/ lib/` is **empty**, so the compiler
read here is the one that was measured.

**Owed to the manager.** §8's three inbox asks are ready to append —
**I-102** (the admission fix's acceptance cells, extended by batch 2, with
`wild-validator-email-owasp` as the discriminating cell and the six meeting
targets as explicit no-move controls), **I-103** (one three-artifact timing
block that decides the run-form dominance rule; needs no new pcrec build,
both axes ship), **I-104** (carry a null-control band in the capability
report — a re-ask of I-91 block B with this lane's own population offered,
`b2ledger/nullctl.json`).
