# subtri — what in the search costs the time on bench O-109's three slow substitution cases

Lane subtri (opus), 2026-10-27. Measurement and report only: nothing under
`src/`, `cli/`, `lib/` or `tests/` changed (NO BUILD GO). Every number is a
user-space INSTRUCTION count (exact, repeatable to <0.01%) or a CYCLE count
used only as a ratio; the box was not in a timing window (queue jobs
620/621/622-ic2 were running), so no wall-clock figure here is evidence.

## Summary

Premise checked: O-109 and the ledger
`pcrec-bench/docs/dev/ledgers/2026-10-27-subst-0.1-first-9ae59f5d4.md` name the
three patterns and numbers the brief quotes (5b 453 vs rust 143 ms; 7 203 vs
JIT 52; 2 128 vs JIT 48). All three cases REPRODUCE: the regenerated
`acc-main` subject matches the bench manifest byte for byte (sha256
`a9b0a4cc…`, 361,986,301 B), and the match counts are the bench's (80,123 /
23,986 / 160).

The search IS the cost: a plain find-all is 98.7-99.5% of the substitution's
instructions on all three cases (render + copy is ~30M instructions and
~0.1-0.15G cycles, mostly the 362 MB copy). Nothing between 9ae59f5d4 and
main bdc2cb2e5 moved any case (2 and 7: emitted C identical except the abi
digit; 5b: a second reverse scan-edge run, -0.04% instructions).

One named cause per case, each confirmed by a span-identical hand prototype
of the generated artifact (scratch only, not pcrec code):

| case | the cause | where the instructions go (find-all, main) | prototype | instr | cycles |
|---|---|---|---|---|---|
| 5b mask-email | the start mechanism is the LEADING CLASS: the byte-class prefilter is true on 92.8% of bytes, so the forward DFA steps 336.0M of 362.0M bytes and restarts 53.6M times for 80,123 matches; `@` (exactly 80,123 occurrences) is only a whole-window memchr pre-check | forward DFA 98.8% (16.1 instr/byte), `@` pre-check 0.75%, reverse 0.4% | drive from memchr(`@`), move back over the class run, anchored DFA forward | 5.477G -> 0.073G (x75) | x45 |
| 7 url-tld-fix | the required run's FOUND POSITION IS DISCARDED: two req-run pre-checks locate `https://www.` (memchr `/`) and return yes/no, then the start is re-derived by a scalar one-byte table loop over `h` and 3.57M VM attempts | start-set table loop 66%, the two pre-checks 23% (re-run from search_from on each of 23,987 calls), failing VM attempts 6.5%, the VM's real work (51,041 attempts at `https://www.`, lookahead + backref included) 2.9% | the run search drives every attempt (exact: the pattern opens with the run); then also key it on `h` | 3.267G -> 0.894G (x3.7) -> 0.304G (x10.7) | x2.0 -> x4.9 |
| 2 rare | the candidate filter between matches is the hybrid's DFA prefilter, keyed on `/` (the pattern's first byte, 20.0M in the subject); the `admin/` run is consulted once per call and then handed off, never re-entered (the L1 re-entry excludes VM hybrids by design), and its memchr is ALSO on `/` | DFA prefilter 99.6% (18.46M memchr calls of ~18 B + 41.1M DFA steps); req run 0.4%; VM 21k instructions total | the run drives every candidate; then key it on `d` (2.06M) | 1.257G -> 0.767G (x1.6) -> 0.137G (x9.2) | x1.2 -> x4.8 |

Bench hypotheses: **5b RIGHT** (drive from `@`; the prototype is x75 fewer
instructions). **7 WRONG on the mechanism**: it is not per-attempt VM cost
(the backreference/lookahead work is 2.9%); it is the start scan between
candidates and the discarded req-run position ("candidate count" is half
right: 3.57M attempts, but they cost 46 instructions each; the scan between
them costs the time). **2 PARTLY right**: a rarer landmark is the larger lever,
but `admin/` is already the landmark — it is keyed on its `/` byte (the
default byte prior rates `/` 7x rarer than `d`; on this access log `/` is 10x
more common) and it drives only the first hop of each call.

## Method

- Subject: `bench/subst/gen_subjects.py` run IN PLACE (before ruling R1
  arrived; see STATE AT HANDOFF) with `python3 -B` (no bytecode) and
  `--out`, `--manifest`, `--planted` all in `/tmp/claude-1001/subtri/subj/`
  (read first: with those three flags it writes nothing inside pcrec-bench;
  afterwards `git -C pcrec-bench status` clean and no file under
  `bench/subst/` or `pcrecbench/` newer than the run, `__pycache__`
  included). The generated manifest is byte-identical to the committed
  `bench/subst/manifest.tsv`; acc-main sha256
  `a9b0a4cc17e65d3ab1fb415c1adf14ec929e3a1e90c8798b7aecddaac7b1ad77`, R1's
  value.
- Artifacts: exactly the bench's compile (`testees/pcrec/configs.toml`
  pcrec-auto: `--features all`, `-p rx`; template via `--subst-file`,
  rendered to the pcrec dialect by `pcrecbench/subst_template.py`;
  `--features subst-extended` for case 7; `--emit-support`), from two builds:
  9ae59f5d4 (`git archive` into scratch, `make -j16`) and main bdc2cb2e5 (this
  worktree). gcc 15.2 `-O2`.
- Driver `/tmp/claude-1001/subtri/drv.c`: the subst_api.md §6¶9 `sub_all`
  wrapper verbatim in shape (the bench's `subst_shim.c` shape) and a plain
  `rx_next_n` find-all (batch 64), with `instructions:u`/`cycles:u` read by
  `perf_event_open` around the call only; `taskset -c 7`; 2-3 repeats
  (instructions agree to within ~1,000 of 10^9). `HASH=1` hashes every
  capture span of every match: every prototype below is span-identical to
  the shipped artifact. `OUTFILE=` writes the substitution output: for the
  shipped artifacts, every prototype and the `--analysis=weblog` builds, its
  sha256 equals the bench's `bench/subst/expectations.tsv` acc-main row
  (2 `0b9c3be4…`, 5b `4b66e137…`, 7 `80c1df04…`).
- Counters: instrumented copies of each generated `rx.c` (candidate entries,
  bytes skipped, DFA steps, memchr calls and bytes, VM attempts) and
  attribution copies that bracket each search stage with `rdpmc` (perf mmap
  page, seqlock read; probe overhead ~20 instructions measured and
  subtracted). `perf record -e instructions:u` + `perf annotate` named the hot
  loops. Instruments (committed copies and the per-artifact diffs:
  `docs/dev/lanes/subtri_evidence/`): `/tmp/claude-1001/subtri/{drv.c,drv_attr.c,pmc.h}`,
  `instr/`, `attr/`, `proto/`; full table `/tmp/claude-1001/subtri/table.txt`.
- Competitor structure is from public documentation only, labelled as such.

Search share (instructions; cycles in brackets, ratio only):

| case | subst | find-all | find share |
|---|---|---|---|
| 5b | 5,506.5M (2.41G) | 5,477.3M (2.32G) | 99.5% |
| 7 | 3,295.1M (1.08G) | 3,266.7M (0.99G) | 99.1% |
| 2 | 1,273.9M (0.70G) | 1,256.9M (0.56G) | 98.7% |

9ae59f5d4 vs main: 5b 5,478.8M vs 5,477.3M find; 7 3,266.5M vs 3,266.7M; 2
1,256.88M vs 1,256.88M. Nothing since moved them.

## Case 5b mask-email

Artifact: DFA, `RX_DFA_PREFILTER "byte-class"`, `RX_REQ_BYTE "64"`,
`RX_DFA_START "reverse-pass"`. `rx_search` = (1) `memchr(subject+from, '@',
rest)` as a yes/no pre-check, (2) a forward unanchored DFA whose skip loop
(`rx_can_begin_match`) is the leading class `[%+-.0-9A-Z_a-z]`, (3) a reverse
DFA from the match end.

Counters (find-all, main): 80,124 calls; the `@` pre-check walks 360.9M bytes
(once over the subject, 0.75% of instructions); the skip loop skips only
26.1M bytes (7.2%); the forward DFA STEPS 336.0M bytes (92.8%) and re-enters
its start state 53.6M times (every token boundary) — 669 starts per match;
reverse DFA 1.16M steps (0.4%). rdpmc attribution: forward DFA 5,412M
instructions = 98.8%.

Hot loop (`perf annotate`, gcc output of the emitted loop): 14 instructions
per byte while in a non-start state (bound check, byte load, class load,
add, transition load, dead check, accept load, cmov of last-accept, state-zero
test) plus a 4-instruction skip test on each return to state 0; the
transition load is a loop-carried load, ~7 cycles/byte measured (2.32G cycles
/ 336M steps). Tightening the loop cannot fix this: even a perfect DFA step
is bounded by that load latency; the waste is stepping 336M bytes at all.

Candidate counts: `@` occurs exactly 80,123 times in `acc-main`, one per
match; the leading class is true on ~93% of bytes.

Prototype (`/tmp/claude-1001/subtri/proto/5b/rx.c`): memchr(`@`) from
`search_from`; move back over the leading class run (bounded by
`search_from`); if the run is non-empty, the artifact's own anchored
`rx_match` from the run start; on a miss, the next `@`. Exact here because the
leading class excludes `@` (an earlier start cannot pair with a later `@`;
where_to_start.md §2.3's first sufficient condition) and the prefix has no
backreference, atomic or possessive (G1), and the suffix no backreference
(G4). Result: find 5,477.3M -> 73.1M instructions (x75), 2.32G -> 0.052G
cycles (x45); subst 5,506.5M -> 102.4M instructions, 2.41G -> 0.18G cycles
(the copy now dominates); spans identical.

Counter evidence checked: the `@` pre-check's whole-window memchr is not the
cost (0.75%); the reverse pass is not (0.4%); the renderer is not (0.5%).

Competitor (public docs, labelled): rust `regex-automata`'s meta engine
documents a "reverse inner" strategy (find a required inner literal with a
prefilter, run a reverse DFA back to the start, then forward) — the shape the
prototype has; consistent with rust's x3.16. libpcre2 JIT (286 ms) runs an
attempt per start position with a required-code-unit check; pcrec's DFA is
slower than that here because it steps every byte.

ONE cause: the start mechanism is the broad leading class; the rare required
interior byte does not drive candidates. Share of the gap: all of it (the
prototype closes the instruction count by x75; the bench's 3.16x).

## Case 7 url-tld-fix

Artifact: VM only (backreference in a negative lookahead), no prefilter,
`RX_VM_START_SCAN "first-class"` with the set `{h}`, `RX_REQ_RUN
"s://www."@3`, plus a whole-run check `https://www.`. `rx_search_run`: (1)
`rx_reqrun` and (2) `rx_reqrun_whole` — both memchr `/` and compare, both
return only "present or not" (`>= n` -> no match), (3) a scalar
`while (!rx_start_set[s[p]]) p++` loop from `search_from`, (4) a VM attempt
at each `h`, re-running (3) after each failure.

Counters (find-all, main): 23,987 calls; each pre-check walks 168.7M bytes in
total (9.40M memchr calls each, ~18 B per call) and its found position is
dropped; the start-set loop walks 357.5M bytes; 3,568,519 VM attempts, of
which 51,041 pass the `https://www.` literal and 23,986 match.

rdpmc attribution (instructions, net of probe):

| stage | count | instructions | share | per |
|---|---|---|---|---|
| start-set table loop (`h`) | 3.57M entries | 2,159M | 66% | 6.0 per byte |
| req-run pre-check `s://www.` | 23,987 | 379M | 11.6% | 15.8k per call |
| whole-run pre-check `https://www.` | 23,986 | 379M | 11.6% | 15.8k per call |
| VM attempts at non-URL `h` (+ reset) | 3.52M | 162M + 48M | 6.5% | 46 + 14 |
| VM attempts at `https://www.` (the real matching: alternation, lookahead, `\2\b`) | 51,041 | 96M | 2.9% | 1,874 |

(Cycle attribution through rdpmc is distorted by the probe; read roughly it
puts the start loop and the two pre-checks at ~45% each, the VM at ~8%.)

Prototypes (all span-identical), instructions / cycles of the find-all:

| variant | instr | cycles | vs shipped |
|---|---|---|---|
| shipped | 3,266.7M | 0.99G | 1 |
| `--analysis=weblog` (pre-checks re-keyed to `w`; nothing else moves) | 2,728.7M | 0.70G | x1.2 / x1.4 |
| 7d: seed ONCE per call at the run's first hit ([OPT-VMSEED]'s stated form) | 2,141.3M | 0.76G | x1.5 / x1.3 |
| 7c: start-set loop as memchr(`h`) only (startset.md's `first-memchr` VM form, Q-R5) | 1,306.2M | 0.68G | x2.5 / x1.5 |
| 7a: the run search DRIVES every attempt (re-entered after each failure; exact, the run is at offset 0) | 894.3M | 0.50G | x3.7 / x2.0 |
| 7b: 7a with the run found by memchr(`h`) + one 12-byte compare | 304.4M | 0.20G | x10.7 / x4.9 |

Counter evidence: the bench's "per-attempt VM cost" reading is refuted — the
lookahead/backreference matching is 96M instructions (2.9%); auto ≈ vm
because neither has anything but the VM's start scan in front.

Competitor (public docs, labelled): libpcre2 JIT documents a first-code-unit
search and a required-code-unit check; a SIMD first-character scan over `h`
(1% of bytes) plus a fast-failing attempt is consistent with its 52 ms.

ONE cause: the required run's found position is presence-only; the start is
re-derived by a byte-at-a-time first-class loop and 3.57M attempts. Ranked
share of the recovered cycles (shipped 0.99G -> 7b 0.20G): driving from the
run 62% (-0.49G, 7a), the run's memchr byte (`/` -> `h`) 38% (-0.30G).

## Case 2 rare

Artifact: VM hybrid, `RX_VM_PREFILTER "hybrid"`, `RX_DFA_PREFILTER "memchr"`
on `/`, `RX_REQ_RUN "admin/"@5`, `RX_REQ_HANDOFF "6"`. `rx_search_run`: (1)
`rx_reqrun` finds the first `admin/` (memchr on `/`, its last byte) — ONCE per
call; (2) hands off to the DFA prefilter at hit − 6; (3) the prefilter
(memchr `/` + DFA steps) scans forward until it finds a real match window,
however far; (4) the VM verifies the window.

Counters (find-all, main): 161 calls; the req run walks 2.38M bytes (0.7%,
130,866 memchr calls); the prefilter walks 336.9M bytes (93%) with 18.46M
memchr(`/`) calls (~18 B each) and 41.1M DFA steps (2.2 per `/`); 3,538
reverse steps; 160 VM attempts, all succeeding. rdpmc attribution: prefilter
1,251.8M = 99.6%, req run 5.0M, VM 21k. Inside the prefilter
(annotate + loop length): ~15 instructions per DFA step, ~14 of call glue per
memchr, ~8 inside glibc's `__memchr_evex` per short call.

Candidate counts: `/` 19,985,023; `d` 2,062,325; `admin/` 42,280;
`/phpmyadmin/` 89 + `/wp-admin/` 71 = 160. The default byte-rate prior
(`src/core/findings_table.inc`) gives `/` 4,154 vs `d` 28,161 — it ranks `/`
as 7x rarer; on this subject it is 10x more common. `--analysis=weblog` (a
shipped bundle) re-keys the req run to `d` (`"admin/"@1`, req byte 100) — but
the req run is 0.4% of the work, so it moves 0.3%: the prefilter still
memchr's `/`.

Prototypes (span-identical), the 2x2 of the two levers:

| | memchr `/` | memchr `d` |
|---|---|---|
| run used once, prefilter drives (shipped / weblog) | 1,256.9M instr, 0.56G cyc | 1,252.8M, 0.56G |
| the run drives every candidate (2b / 2a) | 766.8M, 0.46G | 136.5M, 0.12G |

The driver form (`/tmp/claude-1001/subtri/proto/2a/rx.c`): each `admin/` hit
`c` fixes the only possible start (`c−6` if `/phpmy` precedes, `c−4` if
`/wp-`; mutually exclusive on byte `c−1`, increasing in `c` because
`admin/` cannot overlap itself), one anchored VM attempt there.

ONE cause: the run that is rare enough to drive candidates never drives
them; the DFA prefilter's `/` does, between every pair of matches. Neither
lever alone is enough (the byte alone: 0.3%; the driver alone: x1.2 cycles);
together x4.8 cycles / x9.2 instructions. Ranked share of the recovered
cycles (0.56G -> 0.12G): the byte choice inside a driving run 79%, the
driving itself 21% — but the byte only pays once the run drives.

Competitor (public docs, labelled): rust's regex documents literal-set
prefilters (Teddy, SIMD multi-substring) for an alternation of literal
prefixes like `/phpmyadmin/|/wp-admin/`; PCRE2's ChangeLog records SIMD
character-pair fast-forward searching in the JIT (two characters at fixed
offsets). Both search for rarer evidence than a single `/`.

## Cross-case

- All three are the SAME family: a landmark that pcrec has already DERIVED
  (`@` req byte, `s://www.` req run, `admin/` req run) is used as presence-only
  evidence or for one hop, and the bytes between candidates are walked by a
  weaker mechanism (a broad class DFA, a one-byte table loop, a `/` memchr +
  DFA). where_to_start.md §0 names exactly this ("the one mapping pcrec does
  NOT have is an EXACT start for a landmark behind an UNBOUNDED prefix — today
  such a landmark is presence-only"); cases 7 and 2 show the bounded/offset-0
  versions of it on the VM-only and VM-hybrid routes, which the K82/L1
  handoff does not serve (`pf_handoff_applies`: `cand_finish_of != VM`,
  rlhbuild_report.md §1.3).
- Two of the three (2, 7) ALSO have a memchr byte chosen by the default prior
  that is wrong for access logs (`/`); `--analysis=weblog` fixes the pick but
  not the structure, so it buys 0.3% / 16%.
- None is per-attempt matcher cost; none is render/copy cost; none moved
  since 9ae59f5d4.

## Proposed rows

Not scheduled; the manager files. Each names the existing row it belongs to
and the measurement that would verify a fix (instructions:u of the find-all
on `acc-main`, span-identical to today, then the bench's subst cell).

1. **5b -> [ENG-TACTICS] rev-inner (HELD).** Its re-worded trigger reads "a
   weighted cell where the re-entered handoff leaves a measured gap, or an
   UNBOUNDED prefix it cannot serve": 5b is that cell (unbounded leading
   class, ×3.16 to the best library, x75 instructions in a span-identical
   hand twin). It is the easy end of rev-inner: G2 holds by rust's first
   condition (the prefix class cannot contain `@`), G1/G4 hold, and the
   reverse walk is a single class run (a D161 "move-back" span, not a reverse
   DFA). Witness for Frank's "house of cards" concern: the twin is the
   narrowest admitted form (single-byte landmark the prefix excludes).
   Verify: find ≤ 0.1G instructions (from 5.48G), spans identical; bench 5b
   cell. Lens: the population of "broad leading class + required byte the
   class excludes" (`\S+@\S+`-like, the K7 class in walk_survey) is the
   census to count first.
2. **7 -> [OPT-VMSEED] (not started), re-scoped to the RE-ENTERED form.** Its
   text is the seed-once form (7d: x1.3 cycles only); the measured win needs
   the run search to drive every attempt (7a x2.0) and, for a run at offset 0,
   the run position IS the candidate (EXACT, where_to_start.md's run-pinned
   row on the VM route). Population: VM-only-at-auto with a required run, as
   the row says. Verify: case 7 find ≤ 0.9G instructions at the shipped
   byte, span-identical. Sibling: startset.md Q-R5's VM `first-memchr` form
   (7c, x1.5 cycles on its own) — one of the two, not both, per the
   general-mechanisms rule.
3. **2 -> [REQ-HANDOFF-L1]'s re-entry extended to the VM hybrid** (NEW row
   draft, a widening of a completed row: today `pf_handoff_applies` declines
   `cand_finish_of == VM`). Draft: "the hybrid's req run re-enters after a
   false hit instead of handing the rest of the call to the first-byte
   prefilter; each hit maps to a start bound (here an exact start per arm)".
   Verify: case 2 find ≤ 0.8G instructions with today's byte (2b),
   span-identical; K88's back-to-back shape as the control.
4. **2 and 7 (byte choice) -> [PRIOR-COST-UNIFY] (blocked) / [OPT-LITSCAN]'s
   frequency-prior form, plus [MEMFN-PAIRSTOP].** The default prior ranks `/`
   7x rarer than `d`/`h`; on access logs it is 5.5% of bytes. A shipped
   analysis already fixes the pick (`--analysis=weblog`). Two readings for the
   manager: (a) the bench's pcrec-auto runs without an analysis, so this is
   the default prior's blind spot for URL-heavy text, or (b) a two-byte
   (pair) search robust to the prior. Verify: the 2a/7b twins (x4.8 / x4.9
   cycles once rows 2/3 exist).
5. (For the record, no row) The DFA step loop's 14 instructions/byte (5b) is
   load-latency bound; making it tighter is not where 5b's gap is.

## Questions for the bench

1. Do the libpcre2-JIT and rust arms of 5b/7/2 have strategy stamps (rust's
   meta strategy chosen; JIT's start-of-match optimizations) to confirm the
   structural readings above, which are from public docs only?
2. Would the bench add a pcrec-auto arm compiled with `--analysis=weblog` on
   the subst set (the subject is an access log), so the prior's share is a
   bench number rather than a lane's instruction count?
3. Is the 7 case's subject density (51,041 `https://www.` of which 23,986
   match) intended, or should a variant with fewer near-misses exist? It
   sets how much the re-entered form beats seed-once.

## STATE AT HANDOFF

STATE: done. All three cases reproduced and attributed; no build, nothing
owed. Rulings file `docs/dev/lanes/subtri_rulings.md` re-read before this
report; last entry applied: R1 (bench facts + subject procedure). R1's
numbers match the ones used here. R1's procedure (copy `bench/subst/` to
scratch, run the copy with `python3 -I`) arrived after the subject was
already generated by running the script in place with all outputs
redirected to scratch and `-B`; I did not regenerate, because the result is
the same file (sha256 equal to R1's value) and the in-place run wrote
nothing in pcrec-bench (checked: git status clean, no newer file under
`bench/subst/` or `pcrecbench/`, `__pycache__` included). The deviation is
reported here rather than hidden. The 362 MB `subj/acc-main.log` is deleted
at handoff as R1 asks. Instruments and data stay
in `/tmp/claude-1001/subtri/` (scratch, uncommitted): `drv.c`, `drv_attr.c`,
`pmc.h`, `instr/`, `attr/`, `proto/{5b,2a,2b,7a,7b,7c,7d}/rx.c`, `wl-art/`,
`table.txt` (copies in `docs/dev/lanes/subtri_evidence/`); `subj/acc-main.log`
deleted at handoff.
