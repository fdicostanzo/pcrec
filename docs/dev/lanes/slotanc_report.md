# slotanc report

## Summary
Rows t2 and k1 of slot/sabotage.sh re-anchored; both DETECTED with controls green (JMB/JMH). The FULL table did NOT complete:
its J4 control is RED on the unplanted tree at 99b41b3d4 (a code defect outside this lane's scope; STOP). arch-blind 17/0 and est selftest 68/0 pass.

## Re-anchored rows
- t2: anchor now `    sh(CC + ["-DSLOT_GATE_TU"] * gate + ["-c", "-DSYM=" + sym,` (link.py:591); the plant inserts `"-march=x86-64-v3"` before `"-c"`, keeping the gate-TU arg. Result: ISA MISMATCH kit.find_byte.mfind-swar: keyed target generic.
- k1: both anchor and replacement indent 31 -> 27 spaces (plan.py:461). Result: KEY-ARM MISMATCH ... dim reject: the key names 50, the Arm 0.
Commit 6e76748b2. No other edits.

## Full table
`sabotage.sh <scratch>` (no filter): "control J2/est/J3 green", then "sabotage: CONTROL red (the unplanted copy's J4 dry run)":
link.py:674 `timed_shape_check(a.name, o, sym, fc[0])` -> TypeError: 'NoneType' object is not subscriptable. `render()` returned fc None for an arm whose TU
contains SLOT_GATE_TU (a J4 arm, likely a base.null / verify arm). Log: /var/tmp/pcrec-pcrec/scratch/memfn/slotanc/full.log; control output full/control.J4.out.
The `run.py dry J4` crash is independent of the planted rows (unplanted copy), so no row after the controls ran: table result UNKNOWN beyond t2/k1.
Likely cause: the TIMED-SHAPE call added by mcfixa/mcfixb (de4413cbb) assumes fc is set for every SLOT_GATE_TU TU; some J4 arm kinds return None.

## STATE AT HANDOFF
Rulings applied: none (file empty). (needs a fix lane for the J4 `fc` None in link.py:674, then a re-run of the full table).
OWED: none
