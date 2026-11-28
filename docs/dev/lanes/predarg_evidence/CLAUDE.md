# docs/dev/lanes/predarg_evidence/ — lane predarg's evidence

Evidence for docs/dev/lanes/predarg_report.md: a STUDY of the owner's strong lean no-path-through-argument ("a path
never goes through an argument's place ..."; record docs/design/plan_row_bodies/COND-FAMILY.md, 2026-11-27). Design
evidence only: nothing here rules, nothing asserts, and no check under `make` reads it. The documents read are those
at the lane's start commit 88cda0d38.

## Files

- `load.py` loads lane predfold1127's model (`../predfold1127_evidence/predfold1127_model.py`, the in-force walker
  WALK1127) up to its checks, as its probes do, plus its sweep definitions. Imported by the rest.
- `cand.py` puts the candidate into the walker as modes of `_between`: `now`, `A` (the carve-out as a door: a place
  passes only where it is listed), `A0` (A, strictly the place's own parent), `A2` (A, any list above the place in
  the body), `B` (A, and the listed labels count as the body's own: not steps). Every mode applies body-own-name
  and array-gate.
- `rxbuild.py` builds a python `re` regex mechanically from a program's text and bindings, each group and written
  label uniquely named, so a READING names the target; the target's `\d` is narrowed by the condition.
- `census.py` / `census.out`: every printed program of core.md, library.md, parked.md that reads through a macro or
  into an argument, classed by route, with the walker's verdict in now, A and B.
- `probes.py` / `probes.out`: the adversarial programs, walker verdicts in five modes, each reading RUN; a CONTROL
  first (five printed lines answered by rxbuild, compared to the printed answers).
- `moves.py` / `moves.out`: each printed line that moves, its re-spelling RUN against the printed answers, and the
  reads reading B turns legal.

## Run

`timeout 600 python3 -I -B <this dir>/census.py` (likewise probes.py, moves.py); each prints and exits 0. Each runs
in under a second here.

## Known limits

- The walker does not parse label parameters, named lists `[(=h) = ..]`, `occurrences`, `rx.digits` or a start
  written inside an argument: those verdicts are by hand in the report, marked.
- rxbuild handles no loops and no `&` between patterns; the `hits` and `list_of` runs are hand-written regexes or
  rely on python's last-iteration capture, said where used.

Lane files are historical after merge; never edited then.
