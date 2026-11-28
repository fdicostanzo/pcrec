# docs/dev/lanes/predfold1127_evidence/ — lane predfold1127's evidence

Evidence for docs/dev/lanes/predfold1127_report.md. The lane folds two owner rulings into the predicate documents:
gate-beside-label ("error") and one-path ("yes all five"; record docs/design/plan_row_bodies/COND-FAMILY.md,
2026-11-27). This is design evidence only. Nothing here rules, and no check under `make` reads it.

## Files

- `predfold1127_model.py` is a STANDALONE python3 model, the successor of
  `../predfix111_evidence/predfix111_model.py`.
  - It LOADS predfix111's model unchanged, up to its checks (`# ==== CHECKS (a probe loads the model up to this
    line)`). The older models load through it.
  - WALK1127 is the one-path walker, written from the ruled statement: a step may be skipped only when exactly one
    label of that name is visible from the start. It counts per spot, within one match (two branches of one `|`
    are one each); a wall hides what is under it, a gate (a part or call used alone) does not and is never
    skipped (line 2); the array form is exempt (line 3); "more than once" is counted under the start (line 5).
    A read that skips nothing keeps the label flow. Nodes between are labels, groups, gates, list aliases and an
    argument's place.
  - `X1127[0]` off is predfix111's walker WALK111: the control of CANARY1127, CENSUS1127 and SWEEP1127.
  - Switches (READ1127): `array` (reading (d): `error` printed, `exempt` the other), `direct` (a target reached
    directly beside a skipped one: `error` printed, `wins` the other).
  - The checks, by name: CANARY1127; RULE1127 (29 reads, hand verdicts each citing its ruled line, legal reads
    against hand regexes); READINGS1127 (the manager's readings); READ_D1127 (reading (d), both sides); CENSUS1127
    (every dotted read at the starting commit, control against now, every move declared, every unparsed read
    categorised); TABLE1127; SWEEP1127 (every printed three-mode line; the start commit 637a5e79c under the
    control; declarations GONE1127); ERRSWEEP1127 (MSG111 plus MSG1127); SPECLINES1127; STALE1127; QUOTES1127
    (the record at the PINNED start commit); MECH1127 (MECH111's mechanically built regexes against the engine);
    SUCCESSOR1127.
  - SUCCESSOR1127 runs predfix111 in full (its SUCCESSOR111 re-runs the eighteen before it and dumps their outputs)
    and keys every red of all nineteen with predfix90's `red_key10`, declared in `predfold1127_succ_decl.tsv`.
    A traceback is never declarable.
  - Its verdict is its last line, `predfold1127_model: N checks, F failed`. It exits non-zero iff that line
    reports a failure.
  - Run: `timeout 6000 python3 -I -B <this dir>/predfold1127_model.py`, with `PREDFOLD1127_SUCCDIR=DIR` (an
    existing scratch directory for the successor outputs).
    - `PREDFOLD1127_LIGHT=1` skips SUCCESSOR1127. `PREDFOLD1127_READDUMP=1` reads DIR instead of re-running.
    - `PREDFOLD1127_WRITEDECL=F` writes the seen reds as a declaration draft.
  - `PREDFOLD1127_SABOTAGE=sN` plants one wrong rule, fact or text per check (PLANTS1127, s1..s15). `=all` runs
    every plant, one LIGHT subprocess each; s15 reads DIR.
- `predfold1127_model.out`, `predfold1127_sabotage.out`: the committed runs at the delivered tip.
- `predfold1127_succ_decl.tsv`: SUCCESSOR1127's declarations (model, red check, class, reason, key).

## Known limits

- predfix111's limits hold for every read WALK1127 does not parse (38 printed dotted reads; CENSUS1127 lists
  each with its category).
- The full-path search in a message tries subsets of the nodes between, the walker judging each.
- MECH1127 covers six reads with a single-digit condition on a named target.

Lane files are historical after merge; never edited then.
