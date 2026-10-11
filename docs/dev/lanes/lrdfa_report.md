# lrdfa — [LOSS-REVIEW] phase 1, the DFA-route share (2026-10-11, opus)

Brief: the manager's lrdfa brief; charter `docs/dev/optloop/lossreview_charter.md`.
Deliverable: `docs/dev/optloop/lossreview/dfa.md` (+ `dfa/` instruments/data,
`lossreview/CLAUDE.md`). Branch `lane/lrdfa` from main f2fcffb4. Nothing under
`src/`, `tests/`, `docs/spec/`; no timing (box busy); nothing written in pcrec-bench.

## Summary (resume from here)

- **Population.** 55 trailing DFA-route cells (50 patterns, utf8 and litrun
  excluded): 29 are attributed (51.2 ms of bench loss) and 26 are listed
  (SCAN-SIMD 17, rust-only 9). On every DFA cell where jit is the winner,
  pcre2-interp is slower than pcrec. The scalar (D119) losses are 4 cells,
  all vs re2: concat-sqli, hex8-bounded, dbnames, json-constant (42.1 ms).
- **Top causes and their fix-existing candidates:**

  | cause | loss | fix-existing candidate |
  |---|---|---|
  | ATTEMPT-SHAPE | 28.9 ms | `[OPT-ATTEMPT-SPLIT]`; an exact twin is built |
  | DENSE-SKIP | 13.2 ms | `[START-DENSE]` widened to every table-skip NEXT row; the hex8 skip averages 1.75 B per entry |
  | HIT-RESTART | 4.4 ms | memfn R4d (SWAR fused scan+verify, trigger met) plus an ofsskip `fn_rows[]` BODY row |

  Then RUN-PICK 1.76 (`[PRIOR-COST-UNIFY]`), PAIR-SKIP 1.36, K101 0.92,
  RANGE-SKIP 0.44, REV-PASS 0.13 (`[START-LANDING-EXC]`, below trigger),
  ATTEMPT-STEP 0.04 (a deferred G2 pre-check).
- **Twins.** 19 artifacts are answer-checked (base = twin = libpcre2 10.46),
  plus a planted control that the check catches. Timing is OWED:
  `dfa/twins/time_twins.sh`.
- **Findings.**
  - K101's bounded-stream shape raises `memchr` calls +66% on the bench's own
    mod-i subjects (bytes 5.04 → 1.96/B), so R4d is preferred there.
  - G2 is right in total on email-owasp: its G2-off twin reads 1.0 B/B on
    every subject, while a deferred check reads 0.017 B/B.
  - stack-frame is not a `[REQ-HANDOFF-L1]` mover (its census): its loss is
    the run gate's 90,225 `a` restarts after `set-leads` found `)`.

## Validation

- Subjects: 31 throughput + 278 short files, sha256 = the bench's committed
  manifests (copy at pcrec-bench d359564f).
- Base answers: 290/290 throughput match counts = the bench's expectations.tsv.
- Twins: `dfa/data/check_twins.log`, all SAME. The control (`k101plant`) gives
  DIFF on 6 of 45 subjects.
- Owed: the quiet-slot timing (`time_twins.sh`, 23 binaries, `DRYRUN=1`
  verified). No `make test` is needed: no code was changed.

## Deviation

- One empty file was written to `/tmp/x` during setup and deleted at once.
  It is disclosed in dfa.md §7.
- An early `cd` into the worktree was used before switching to absolute paths.
