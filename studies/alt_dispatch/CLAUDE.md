# studies/alt_dispatch/ — [ENG-ISL.S0] the alternation-dispatch study

Chartered by Frank 2026-09-03, lane altstudy. Compares five dispatch
algorithms for a wide literal alternation — today's serial try (`vm_alt`,
`src/gen/emit_vm.c`), first-byte grouping, a ported `src/ir/nfa.c:192`
M2.8 trie walk with priority-tagged accepts, a `[OPT-ALTHASH]` k-byte
block hash, and (added mid-study by ruling R1, Frank 2026-09-03) the
VM-native trie walk — for exactness (answer-identity against the serial
oracle, at every subject position) and cost (tries/verify-bytes per
subject byte, ns/byte and ns/call, construction time and table bytes; for
the VM-native walk also frames pushed and the deferred-list "mask width"),
on pcrec-bench's `bench/altwide/` patterns and subjects.
`studies/CLAUDE.md`'s standing rule: self-contained, own Makefile
(`gcc -O2`, C11), never built by pcrec's top-level `make`, never run by
`make test`; nothing here touches `src/` or `tests/`. See
`docs/design/alt_dispatch_study.md` for the method, the exactness
argument (including a correctness subtlety in the VM-native walk's commit
test that its own first draft missed, §3.2), the measured tables and the
recommendation; this file is the directory map.

## Files

- `README.md` — how to reproduce (`make inputs`/`check`, `make unit`,
  `make run`) and a one-line description of each of the five algorithms.
- `Makefile` — builds `altdispatch` (the harness binary) and
  `tests/unit_trie` from plain `gcc -O2`; `make run` writes `results/*.tsv`;
  `make check` re-derives `patterns/`/`subjects/` from pcrec-bench and
  diffs against the committed copies.
- `gen_inputs.py` — derives `patterns/*.branches` and `subjects/*.bin` from
  pcrec-bench's `bench/altwide/` (read-only source; provenance recorded in
  every derived file's header and in `subjects/PROVENANCE.md`). Its own
  header documents exactly what is a direct copy, what is derived by a
  stated rule with no new pool words (`srt-1024`/`srt-2048`/`ci-1024`/
  `ci-2048`), and what could not be built at all (`sh1`/`pfx3` beyond 512 —
  see docs/design/alt_dispatch_study.md §5).
- `src/common.h`/`.c` — shared types. A branch is a sequence of `ByteSet`s
  (256-bit class bitmaps), not a raw string — mirrors `src/ir/nfa.c`'s
  `TItem` deliberately, so a `(?i)` branch (each alphabetic position admits
  `{lower, upper}`) is a first-class input with no special-casing anywhere
  else in the harness. `bset_load`/`subject_load` read the `.branches`/
  `.bin` file formats `gen_inputs.py` writes.
- `src/algo_serial.c`/`.h` — (a), the oracle: `vm_alt`'s serial try, ported.
- `src/algo_firstbyte.c`/`.h` — (b): stable first-byte grouping.
- `src/algo_trie.c`/`.h` — (c) AND (e): the M2.8 trie (`src/ir/nfa.c:192`)
  ported to a query walk (`trie_dispatch`, (c)), plus a static per-node
  `subtree_min` annotation and `trie_dispatch_vm` (ruling R1, (e)), which
  walks the SAME trie but COMMITS (pushes one resumable frame, stops) or
  DEFERS (records into a small ascending list) at every end node — see the
  design doc §3.2 for the exactness argument, including why the commit
  test needs a second check (`best_deferred`) beyond what the ruling's own
  wording states. Rule 1 (a branch ending mid-trie) needs no special
  machinery for (c) (the walk collects every accept it passes and takes
  the min, order-independent by construction); rule 2 (overlapping non-
  identical classes) is vacuous for this study's literal/ci branch shapes
  and is handled defensively by DECLINING (a flat serial fallback for that
  subtree) rather than mis-ordering — see the design doc §3 for the
  argument and why this study's real inputs never reach that path.
- `src/algo_hash.c`/`.h` — (d): the `[OPT-ALTHASH]` k-byte (k=2,4) block
  hash, open-addressed with exact-key verification (NOT a true minimal
  perfect hash — design doc §5 item 3).
- `src/harness.c` — the driver: for every (pattern, subject) pair, builds
  all indices (timing construction; (e) shares (c)'s trie), checks
  (b)/(c)/(d)/(e) against (a) at every subject position, then times 11
  rounds per algorithm and writes
  `results/{identity,tries,timing,construction}.tsv`.
- `tests/unit_trie.c` — adversarial exactness checks for (c) AND (e): both
  of `nfa.c:192`'s own hazard counter-examples (rule 1: `abc|a|abd`; rule 2:
  `[ab]p|[bc]x|[ab]xy`, the latter hand-built in C since this study's
  literal/ci file format cannot express a genuinely overlapping class),
  each checked at every subject position against this study's own serial
  oracle AND against `nfa.c`'s own stated PCRE span. The rule-1 case is
  also (e)'s own regression test — it is the case that caught the
  best_deferred correctness gap, design doc §3.2.
- `patterns/*.branches` — one branch (a lowercase word) per line, `# MODE
  literal|ci` and `# PROVENANCE` header comments. Derived from
  pcrec-bench; see `gen_inputs.py`.
- `subjects/*.bin` — copied byte-for-byte from pcrec-bench (the 17 short
  field/hit/near-miss files plus the four `t-*` throughput prose files);
  `subjects/PROVENANCE.md` has the per-file source path and sha256.
- `analyze.py` — reads `results/*.tsv` and prints the summary tables the
  design doc's §4 cites (answer-identity totals, tries/ns per byte on the
  primary search subject, the `w`-vs-`srt` width-ladder ratio, construction
  cost/table bytes). Read-only over `results/`; writes nothing.
- `results/*.tsv` — this study's measured, committed output. See
  `harness.c`'s header for the four files' columns.

## Conventions

Every algorithm's cost is charged in two comparable units:
`tries` (branch attempts / trie steps / hash probes — one push/fail/pop-
shaped operation) and `verify_bytes` (byte-level class-membership tests).
Neither is charged for free anywhere; a "0 tries" row in `results/tries.tsv`
means the algorithm's own index structure ruled out every branch before
attempting one (e.g. first-byte grouping when the subject byte starts no
branch at all).

Maintenance: update this file when files are added/removed or their roles
change.
