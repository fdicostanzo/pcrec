# [ARTREV] S0 selection -- DRAFT, PILOT ROWS PINNED (lanes artharness 2026-10-05, artprep 2026-10-06)

`selection.tsv` is the selector's draft: 16 cells, each one the bench already
times, stratified by ROUTE (read from the artifact's own stamps, not guessed) and
by bench STANDING. It is a draft because the artifacts are regenerated at the
post-START-SET-stage-2 pin (abi 62) and the routes below are re-read there
(`studies/artrev/gen_selection.py --pcrec BIN --pin SHA --all`); a row whose route
or standing moved is re-judged, not carried.

## How it was built (and what it is not)

- **Standing** = pcrec `auto-caps` median ns / libpcre2 `jit-caps` median ns, regime
  `large-subject-throughput`, read from the bench's published reports
  `pcrec-bench/reports/2026-10-02-*-fc719ca4.tsv` (the `rank` rows, read-only): losing
  > 1.15, near-tie 0.90-1.15, winning < 0.90 (300 paired cells; 71 losing, 8 near-tie,
  221 winning). The 2026-10-05 round1 reports are not in the Mac checkout; the losing
  rows were cross-checked against `gapreport_2026-10-05.md` (stack-frame x4.83 vs its
  x4.85, level-context x3.82 vs x3.83, the aws key x44.04 vs x43.9) and the cause group
  column is that report's `gapreport/rank.json` membership. Ratios are therefore one pin
  older than the gap report; they stratify, they are not results.
- **Route** = the stamps of the artifact compiled by the CURRENT main binary (abi 61) with
  the bench's flags (`--features all`, plus `-e utf8` on the utf8 set): `dfa-scan`
  (`RX_ENGINE dfa`, `RX_DFA_SCAN unanchored`), `dfa-attempt` (`RX_DFA_SCAN attempt`),
  `vm` (`RX_VM_PREFILTER none`), `hybrid` (`RX_VM_PREFILTER hybrid`), `utf8-*` the same
  under `-e utf8`. "Captures" = `RX_NCAPS` (a group-bearing pattern is forced VM/hybrid by
  default; `--no-captures`, the bench's `auto-nocaps` testee, recovers the DFA).
- Pattern text is the bench's `bench/<set>/patterns/<name>.rx` verbatim.

## Coverage

| route | losing | near-tie | winning |
|---|---|---|---|
| DFA scan | A01 stack-frame (pilot), A02 union-select, A13 grp-cap (no-caps) | A03 cls-i-class | A04 kv-quoted |
| DFA attempt | A05 anc-m-caret | - | A06 email-owasp |
| VM (captures) | A07 doubled-word (pilot) | - | A08 nested-comment-rec |
| hybrid | A09 level-context (pilot), A10 aws-key, A12 grp-cap | - | A11 ipv4-owasp |
| utf8 | - | A14 asr-lb-class (hybrid), A15 cls-neg-cjk (DFA) | A16 cls-high-range |

Captures vs none: with captures A07 A08 A10 A11 A12; no captures in the pattern A01-A06,
A09, A14-A16; forced no-captures A13 (the same pattern as A12, so the pair measures what
the capture machinery costs on one artifact pair).

Gaps, stated rather than filled: no VM or hybrid cell sits in the near-tie band in the
10-02 data (they are either clearly losing or clearly winning); a utf8 LOSING cell does not
exist against the JIT (the utf8 set's losses are against rust, group U8-PICK, which this
stratification does not use). Both would need a different peer to populate.

## The pilot (charter 5)

- **A01 loglines/stack-frame** -- DFA find-all on a LOSING cell (x4.83, group FS-DFA/START-SET).
  Caution: START-SET stage 2/3 touch DFA start seeding, so this artifact may move at the
  new pin; that is the reason the pilot is regenerated, and a lead that is "START-SET
  again" is the generalizer's known-vs-new signal, not a defect of the selection.
- **A07 capability/doubled-word** -- VM with captures (`\b(\w+)\b\s+\1\b`, a backreference,
  `RX_VM_PREFILTER none`), LOSING x1.93; the hybrid-free VM path.
- **A09 loglines/level-context** -- hybrid (DFA gate + VM), LOSING x3.82, group CTX
  (not START-SET, so the pilot's hybrid lead is independent of the in-flight stage).

Chosen over the alternatives (A02, A10) for review size (A01 919 emitted lines, A07 438,
A09 1185) and so that no two pilot artifacts share a cause group.

## Notes a reviewer's brief needs

- **Cell subjects**: `large-subject-throughput` cells are the find-all over the set's
  `throughput/t-64k, t-256k, t-1m` (`bytes` in the report is their sum, 1,376,256 on
  capability); only `bench/capability/throughput/*.bin` is in the Mac checkout, the other
  sets' subjects come from the bench's `gen_throughput_subjects.py` or the Linux box via the
  manager. `dfa-attempt` cells (A05, A06, A11) are anchored validators whose throughput
  cell is ns/call; their regime is `short-subject-search` (`manifest.tsv` ids), so the
  timing subject is a short subject, not a megabyte file.
- **Dense and sparse variants** (S4) are the confirmer's to construct from the cell's subject.
- **A04 kv-quoted** is a winner against the JIT that loses to rust (INNER-LIT): it is in the
  set because "a winning artifact can still waste work" (charter 4).
- `selection.tsv` columns: `id, name` (the artifact directory), `bench_set, bench_pattern,
  pcrec_flags_extra, route, captures, engine_stamps_main_abi61, standing,
  ratio_auto_vs_jit, gapreport_group, pilot, bench_regime, bench_subject, note`.

## PILOT PINNED at main 57db5152 (abi 62) -- lane artprep, 2026-10-06

The three pilot artifacts (A01, A07, A09) were regenerated with a `build/pcrec` built from main
57db5152 (START-SET stage 2 landed; `make CC=gcc-16`, binary sha256 `67cca146...`, the full hash is in each
artifact's `GENERATION.txt`) by `gen_selection.py --pilot --force --pcrec <that binary> --pin 57db5152`, gcc-16
(Homebrew 16.2.0). Columns `pinned_at` and `pin_stamps_abi62` of `selection.tsv` carry the pin and the re-read
stamps. A row's route did NOT move for any pilot artifact; what moved versus the ca7bdb11 (abi 61) dry run, from
a `diff` of the two `artifact.c` per artifact:

| artifact | route at the pin | moved vs ca7bdb11? |
|---|---|---|
| A01 loglines/stack-frame | dfa / unanchored (stamp `RX_VM_START_SCAN "none"`) | NO: 5 changed lines, all abi-62 bookkeeping (the `Generated by ... (abi N)` header, `.abi = 62`, one new stamp line `RX_VM_START_SCAN "none"`). The DFA hat of START-SET is not built (stage 3), so the artifact is the abi-61 one. 919 -> 920 lines. |
| A07 capability/doubled-word | vm / no prefilter (stamp `RX_VM_START_SCAN "first-class"`) | YES, and it is the START-SET stage-2 VM hat showing: +23 lines net (25 added, 2 bookkeeping lines changed), a 256-entry `rx_start_set[]` table (word bytes plus `_` `0-9`) and two `while (attempt_position < subject_length && !rx_start_set[subject[attempt_position]]) attempt_position++;` skip loops with their `>= subject_length` early return, at the search entry and in the retry. Reviewers of A07 therefore start from the post-stage-2 shape; the DFA/hybrid pilots do not. 438 -> 461 lines (selection's emitted-line counts). |
| A09 loglines/level-context | vm / hybrid (stamp `RX_VM_START_SCAN "none"`, `RX_ENGINE_SEL "collapsed-prefilter"`) | NO: the same 5 bookkeeping lines as A01. 1185 -> 1186 lines. |

The A07 hat is the one pilot lead a reviewer cannot rediscover as "new": the generalizer's known-vs-new check
(START-SET stage 2) will name it; the reviewer is blind and will simply meet it as emitted code.

### Cell subjects (corrected)

The draft `bench_subject` text above was written for the capability set (`t-64k/t-256k/t-1m`, n=3, sum
1,376,256 B) and wrongly repeated for the other sets. Corrected for the pilot rows only (the other rows' text is
still the draft and is re-read when they are pinned): the loglines `large-subject-throughput` cell is the TWELVE
subjects `t-{016k,064k,256k,1024k}-{fail,syslog,hit}` (the bench report's `n` is 12 for stack-frame and for
level-context, the cell metric is the median over them), not three. `docs/dev/optloop/artrev/pilot_setup.md`
carries the subjects, their provenance and hashes.
