# reqpast — the VM attempt loop stops past the last occurrence of an unbounded required run ([REQ-PAST-LAST])

Lane reqpast (opus), 2026-11-12, branch `lane/reqpast` from main db0d874aa (abi
103). Build go: Frank 2026-11-12 "ok proceed with S1" (S1 includes
[REQ-PAST-LAST]); manager ruling 2026-11-12: pcrec-only, lazy re-find when
attempts pass the last hit, no kit request.

## STATE AT HANDOFF

DELIVERED on `lane/reqpast` (abi 105), awaiting the cloud `make test` verdict
and the manager's axes run. Rulings file: one entry, R1 (keep the row under
`-fno-req-handoff`, record the dense-hit loss and the tail win), APPLIED
(tuning.md §2.41¶8c, F6). The brief's flag stop rule fired (the stop can be
slower on dense hits); I asked, and R1 answered it before delivery. Local
sections, all on the final tree, each a box-queue job of batch
b20261112165923319091: strict, codegen, registry, candoracle, memfnreach,
prechecks, prefilter, startset, compound, partlayout, resource, cpsetstruct,
rxtsource, litscan: all 14 GREEN (litscan 8,325 cases, 0 failed; rxtsource 300 checks). startset and rxtsource went red first on the regenerated
`handoff_vm.rxt` (line-keyed pins); re-pinned (CHANGES), then green.

## FINDINGS

**F1. The premise held.** `build/pcrec --emit-facts -p rx --pattern 'a.*foo'`
on main db0d874aa: `req_run 666f6f@0`, `req_run_maxoff unbounded
(decline:unbounded)`, `RX_REQ_HANDOFF "none"`. Under `--engine=vm` the attempt
loop gated once at the entry and never again.

**F2. The stop IS `handoff-attempts` with K unbounded; one row family.** The
new `req-use` row `handoff-attempts-unbounded` (src/gen/emit_dfa.c, the FIRST
rows of `cand_rows[]`, listing order 4) shares every conjunct of the bounded
attempt-loop rows (`req_handoff_vm_run`, factored out of
`req_handoff_entry_applies`: admission emitted, VM with no DFA scan, more than
one attempt, whole run of 2+ positions) and the linearity conjunct
`req_parts_in_whole`; it differs only in K being unbounded, so the three rows
are disjoint. Its `CandUse` is the bounded row's (`whole`, `reenter`), and the
emitters degenerate by arithmetic, not by a parallel path: the entry's move
block becomes `handoff_position = search_from;` (the hit is kept in
`landmark_position`), and `emit_req_landmark_move` emits the re-entry (re-ask
once the attempt position passes the kept hit, a miss is NOMATCH) and returns
before the move, which is never ahead for an infinite K. Same deny
(`-fno-req-handoff`), same size-cap rung (`drop-handoff`), same give-up
direction (tuning.md §2.41¶9a). There is no unbounded `-entry` row: an
entry-only form would be the plain gate.

**F3. Soundness.** Every match holds the whole run at or after its attempt
start (src/facts/req.c: lookaround bodies are not descended into, so no run
byte lies before a match's start; `\K` moves the reported start, not the
attempt start). So once the attempt position passes the run's last occurrence
no attempt can match. Witnesses in tests/litscan/handoff_vm.rxt: `a+\Kxyz`
(\K), `(?<=xyz)a+xyz` (a lookbehind holding the run's own bytes), utf8
`[^@ ]+@x` (the advance is one character; the re-ask starts at the attempt
position, a character start), `a+xyz`, `[^@ ]+@x`, and a give-up witness.
Oracle: gen_handoff_vm.py's python3 `re` + libpcre2 cells; `--check-pcrec`
0 mismatches.

**F4. Reach is narrower than reqlast's 250, by construction.** Census over the
same 5,484 corpus lines (5,023 compile; script
`$PCREC_TMPDIR/scratch/reqpast/census.py`, output `census.tsv`): the row fires
on **8** patterns at the default engine and **155** under `--engine=vm`. The
reqlast count of 250 counted RX_ENGINE "vm" including VM HYBRIDS (which have a
DFA prefilter and are excluded, as for the bounded row) and the 147 one-byte
landmarks (excluded: the attempt-loop rows need a whole run of 2+ positions;
widening the family to a one-byte landmark would move the bounded rows too and
was not built). The remaining declines are patterns whose necessary set holds
a byte the run does not (`a.*foo`: `a` is a set-rest member outside `foo`, so a
re-ask could rescan to the next `a` each time: the same linearity conjunct as
the bounded row). So the premise test's own pattern `a.*foo` stays "none".
Tail, listed, not built: (a) the VM hybrid's prefilter and the DFA routes
(below); (b) one-byte landmarks; (c) set-rest bytes outside the run (would need
the re-ask to cover only the run, a second site shape); (d) the re-entry sits
before the start-set seek, so the first attempt the seek lands on past the
last hit still runs once (one wasted attempt per search, the bounded row's
placement).

**F5. The DFA route is left out: not the same row's form there.** On a DFA
artifact the handoff re-entry is NEXT's `handoff` prefilter row, which REPLACES
the start-byte skip and is admitted by the K margin (`1/h - K > 1/m`), never
true for an infinite K; and the forward scan reaches the subject's end in one
pass with no per-position attempts, so a stop could only save the scan's tail
bytes, and only from start-state restarts (in `a.*foo` the scan never returns
to the start state after an `a`). A DFA form would be a new composition, not
this row's degenerate form. reqlast counted 45 DFA patterns.

**F6. The flag: the existing family deny, no new bit.** The row sits under
`-fno-req-handoff` (`PCREC_NO_REQ_HANDOFF`, bit 46), the deny of every
`req-use` handoff row, so no new public bit and no harness lever. Cost: one
compare per failed attempt while the kept hit is ahead; a re-ask only when an
attempt passes the hit, each re-ask starting past the previous hit, so the
re-asks together read each byte a bounded number of times (the bounded row's
own amortization, `req_parts_in_whole`). On DENSE hits (one passed occurrence
per failed attempt) it is one presence-site call per attempt, which is more
than one compare, so it CAN be slower; that is exactly the bounded
`handoff-attempts` row's cost profile, which shipped under the same public
deny. Measured (queue job 200-reqpast-bench, single process, best of 7, gcc -O2,
`$PCREC_TMPDIR/scratch/reqpast/bench/`): `[^@ ]+@x` under `--engine=vm`, 1 MB
of ` @x` (dense: every failed attempt passes a hit) 1.38 ms per search
against 0.81 ms denied (two runs: 1.284/0.849, 1.380/0.805, 1.427/0.840); the
bounded `handoff-attempts` row on `[^@ ]{1,5}@x` over the same subject 1.56
against 0.71 ms, so the family already carried this profile; the tail case
(` @x` then `ab ` to 1 MB) 0.009 ms against 1.47 ms. Ruled R1 (manager,
2026-11-12): keep it under `-fno-req-handoff`, record loss and win in the spec
hunk (tuning.md §2.41¶8c) and here. A remedy for the dense case (re-ask
after the start-set seek, or one reverse find of the last occurrence, a kit
method) is listed, not built. If the manager wants the unbounded row on a separate switch,
it is one column of its table row (deny 0 plus a `--harness=` lever).

**F7. Measurement card: not a choosable method.** As minw's F5: the stop is not
priced against another method (no set or argmin reads it; the re-ask is the
existing presence site, the kit's text unchanged). What would show its
benefit is the plan row's D77 trigger cell (a long subject with a no-match
tail past the run's last occurrence on the VM attempt loop), not a card.

**F8. Sabotage id range.** S1960-S1964 of the brief's S1955-S1964 already exist
on main (lane `lb_*` rows). This lane used S1955-S1957 only.

## CHANGES

Commits on `lane/reqpast`: 5d849fecb, f2cc280b2, bf048c1d4, 11e692ba3 (WIP) and the final one.

- `src/gen/emit_dfa.c`: `req_handoff_vm_run` (shared conjuncts, factored out
  of `req_handoff_entry_applies`, which keeps the finite-K bound);
  `req_handoff_unbounded_applies`; the row `handoff-attempts-unbounded` in
  `cand_rows[]` (listing order 4, `scan-from-startpos` -> 5; deny
  `PCREC_NO_REQ_HANDOFF`; `whole`, `reenter`); `emit_req_handoff_rest`'s
  unbounded branch (`handoff_position = posvar;`, the hit kept in
  `landmark_position`); `emit_req_landmark_move` returns before the move for
  an unbounded K; the re-entry's comment; `req_handoff_stamp` "unbounded".
  `PCREC_ARTIFACT_ABI` 103 -> 105 (104 reserved for K38-2; re-pin at landing
  if the order differs).
- abi readers (by grep for 103): `docs/spec/match_api.md` (the ABI_H block,
  the `rx_info` table, §6¶17's sentence), `tests/codegen/run_codegen_tests.sh`
  ABI_EXPECT, S693 re-aimed, `docs/dev/history/abi_changelog.md` entry.
- Spec: `tuning.md` §2.41¶8c (new: the contract sentence, the row, its cost,
  measured loss and win), ¶9 (stamp value "unbounded"), ¶9a (¶8c added);
  `match_api.md` §3.1¶15a, §6.3.7¶10-11 (the "unbounded" value);
  `facts_listing.md` §4.1.2¶8 (the fact as a contract sentence: a necessary
  run occurs inside every match at or after the attempt start whatever
  `req_run_maxoff` is; lookbehind and `\K`), ¶8/¶8b ("unbounded" on the VM
  rows); `limits.md` §8.4 rung 4a (¶8c).
- Tests: `tests/litscan/gen_handoff_vm.py` + regenerated `handoff_vm.rxt`
  (six unbounded blocks incl. utf8, `\K`, lookbehind and a give-up witness;
  `a+xyz` relabelled from decline; oracle-checked, `--check-pcrec` 0
  mismatches; header line count kept so the GIVEUP1 keys 20-27 hold);
  `tests/axes/run_axes.sh` GIVEUP1 entries for line 490 (`-fno-req-handoff`,
  `-fno-req-byte`, `-fno-req-run`) and 491-504 (`-fno-req-byte`), measured by
  a sweep of every `--list-axes` deny flag over that file (queue job
  200-reqpast-sweep; only those three flags moved a new line);
  `tests/memfn/run_handoff_reach.sh` (`a+xyz`, `[^@ ]+@x` pinned "unbounded"
  re-entered, floor 4 -> 6, reached 7); `tests/startset/vmhat_checks.py`
  accepts "unbounded"; `tests/registry/run_registry_tests.sh` axes checks
  245 -> 248; `tests/codegen/cand_oracle_witnesses.tsv` witness `a+xyz`;
  `tests/litscan/CLAUDE.md`.
- Sabotage: new S1955 (unbounded entry starts at the hit; detector
  handoff_vm.rxt), S1956 (unbounded row admits a part outside the run;
  memfnreach), S1957 (stamp "none"; memfnreach). Re-aimed S1704 (reach floor
  7 >= 6), S1706 (the bound moved into `req_handoff_entry_applies`' return;
  detector now `(a)\1xyz`'s decline pin), S693 (abi). Anchors of all 192 rows
  on the touched files match their SAB_COUNT
  (`$PCREC_TMPDIR/scratch/reqpast/anchors.sh`).
- Differential (queue job 200-reqpast-diff, `$PCREC_TMPDIR/scratch/reqpast/diff/`):
  default vs `-fno-req-handoff` over every corpus pattern whose artifact takes
  the row (163 artifacts: 155 `--engine=vm` + 8 auto), 46 subjects each
  (random over the pattern's bytes and the run, the run placed 0-3 times), every
  startpos: 152,817 calls, 0 differences, 0 give-up moves; 8 artifacts of 4
  callout patterns did not link with the plain driver (no callout bodies) and
  were not run.
- Line-keyed pins moved by the regenerated `handoff_vm.rxt`:
  `tests/startset/manifests/manifest_s2_vm_{auto,forced}.tsv` (the file's VM
  hat movers re-pinned under their new ids: rows 485/509/550 (and forced 711)
  removed, 485/549/596/648/674/706/749/790 (and forced 951) added; the mover
  diff read in full, then `vm-movers` green on both arms);
  `tests/rxtsource/run_rxtsource_tests.sh` census 7032/98198 -> 7037/98405,
  C3 PASS +162, VERIFIABLE +162, SKIP +45 (= pcre2-only +45).
- docs/dev/plan.md status line; lanes history index entry.

## OWED

- The cloud `make test` (`scripts/cloudrun --owner main --kind test --name
  reqpast`, dispatched as this lane's last act); its verdict reaches main via
  queuewatch/monread.
- `make test-axes` (the manager dispatches it): the GIVEUP1 entries for line
  490/491-504 were measured by the per-flag sweep over `handoff_vm.rxt` only
  (not the whole axes run); the `--engine=vm` reach of the new row (155
  corpus patterns) is covered there for the first time.
- Landing: the abi number. This branch says 105 with 104 reserved for K38-2;
  if K38-2 lands first, the 103 readers in this diff become 104 readers at
  merge (abi_changelog "was" line, S693's AFTER, match_api).
- Proposed ids (none taken): a K row for F4's tail (c), the set-rest bytes
  outside the run (`a.*foo` itself stays declined); a BOONIES row for the
  dense-hit remedy (re-ask after the start-set seek, or a one-time reverse
  find of the last occurrence, a kit request).
