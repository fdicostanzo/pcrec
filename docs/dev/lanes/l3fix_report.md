# l3fix — review r63's FIX-NOW, DOC and PLAN items for span_arms L3's remodels

## Summary

Lane l3fix applied the rulings of review r63 (docs/dev/reviews/2026-11-20-r63-l3remodel.md) on top of
lane/l3build @ c776d02f4. One byte-identical fix commit (bc07f24ed), the DOC records and three plan rows.
`make strict`, `make test-plan-lint` and `make test-claudemd-size` pass. The identity gate and `make test` are
queued (OWED, see Validation queued). CONFORM-1 is not done here (it goes to the L3 feature brief).

## The fix commit

bc07f24ed, in `src/gen/emit_dfa.c` unless noted:
- CONFORM-3: `req_landmark_admits` takes the `PfBound`. NONE and K <= 0 price at 0, UNBOUNDED at its saturated value
  (its comment says so). Both callers (`pf_handoff_applies`, `req_pick_shadow`) pass the bound, not `.v`.
- CONFORM-2: `head_max`'s writer spells the state: UNBOUNDED gives `MF_HEAD_MAX_UNBOUNDED`, BOUNDED its value, NONE
  keeps the initial 0 (D-7's table; unreachable, every HANDOFF row excludes NONE).
- CONFORM-5/HOUSE-8: `emit_req_handoff_rest`'s header no longer restates "c >= posvar always"; the premise lives only
  in `emit_req_move_open`. Register row 30's `where` (docs/dev/guide/architecture.md) now names `emit_req_move_open`.
- HOUSE-3/4/5: `rn_cmp` and `pcrec_lb_max` comments state the contract, with no plan or ledger ids; `Ctx.lb_max`
  names its writer and reader accessors; src/facts/CLAUDE.md, src/core/CLAUDE.md name `rn_cmp`,
  `pcrec_run_scan_index`, `pcrec_bound_of`, `pcrec_lb_max`. src/gen/CLAUDE.md is within 24 bytes of its 12 KB
  limit, so `emit_req_move_open` is recorded in register row 30 only (not repeated there).

## Identity

OWED: job `200-l3fix-ident` (clean-builds c776d02f4 as the reference and bc07f24ed, runs `scripts/emit_sweep.py`
over the SUBJECT population plus `sae1_evidence/bench_patterns.txt`, verdict by `ident_check.py` against an empty
census). Pass line: `== ident_check COMPLETE: 0 unexplained` (in its job.log). Script:
/var/tmp/pcrec-pcrec/scratch/l3fix/jobs/l3fix-ident; output /var/tmp/pcrec-pcrec/scratch/l3fix/ident/.

## Records and plan rows

- EMITTED-1: declared multiplicity change across f52b6d6aa, written in `scripts/trace_diff.py`'s docstring (where the
  default compare is described) and in docs/design/plan_row_bodies/REQ-LOOKAROUND.md under "L3 remodels".
- CONFORM-4/HOUSE-2's sentence: in `src/facts/facts.h` at `pcrec_bound_of` (third encoding; negative off is bounded).
- Plan rows (each with a trigger; `make test-plan-lint` clean): [BOUND-ENCODINGS], [CHECKBIND-HANDOFF-HARNESS]
  (S813/S814 shown red only through the prechecks), [CHECKMOVED-S901].

## Validation queued

| key | what | verdict line |
|---|---|---|
| `200-l3fix-ident` | identity of bc07f24ed vs c776d02f4 | `== ident_check COMPLETE: 0 unexplained` |
| `200-l3fix-test` | full `make test` via perfrun on this worktree | exec'd perfrun: the job's rc is the verdict; no `*** [... test-X] Error` line in its log |

l3build's own queued jobs were left alone. The box was held by a non-timing test (k146fix) when queued.

## STATE AT HANDOFF

Commit bc07f24ed plus this report. Rulings file: empty (no entries to apply). Both jobs OWED. Do not edit the
worktree's source while `200-l3fix-test` runs.
