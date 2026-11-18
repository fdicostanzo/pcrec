# docs/dev/lanes/predspec27_evidence/ — rev 27 of predicates_draft.md (one type; backref-label = capture), its evidence

Lane predspec27 (2026-11-18), DESIGN EVIDENCE: the owner's 2026-11-18 afternoon rulings (backref-label capture;
value-hole yes; match-is-rx; read-is-constant) run in every mode, and every MANAGER'S READING of those entries that a
run can decide. Rules nothing. Historical after merge; never edited after. `../predspec261_evidence/` stays as
committed (the helpers here are copies, not imports).

## Files

- `predspec27_model.py` — STANDALONE. PARTS BL (backref-label: the ruled witness, m1-m3), VD (the value-hole
  discussion: case at the hole; the narrowed `${$y}` / `\k<y>` control), UT (one type: `$x & <5`; his `if` under the
  ruled `when`, three test readings; `\d + 1` lifted at compile time and its order; `$y + 1` at run time; `|`, `&`,
  `.` on a read), TT (the type table as RULE-AS-CODE). Controls: libpcre2-8 10.46 through
  `../rxmodel_evidence/pcre2h.py` (run, never read: D181), python `re`, direct semantic functions.
- `predspec27_model.out` — forward run: CHECKS 20 of 20 OK.
- `predspec27_sabotage.out` — all 8 sabotages at once: 12 of 20. `predspec27_sabotage_each.out` — each alone; every
  one fails at least one check.

## Run (one process; no make; nothing under /tmp)

    (cd $PCREC_TMPDIR/scratch/predspec27 && timeout 900 python3 -I -B \
        <worktree>/docs/dev/lanes/predspec27_evidence/predspec27_model.py > fwd.out)

Seconds. `PREDSPEC27_SABOTAGE=1` or `s1,..`; the list is the script's header.

## RULE-AS-CODE (consistency checks, never independent controls)

| predicate | draft sentence (rev 27) |
|---|---|
| `status(op, kind)` | R.1.16 THE TYPE TABLE (BUILT NOW / UNDER CONSTRUCTION) |

LIMITS: the label is predspec261's marker model; the conditional's warning is not runnable (no parser).
