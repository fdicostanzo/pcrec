# l1ftri — triage of the RED identity job on lane/l1feat

## Summary
Class (a): a JOB defect. The job `200-l1feat-b20261119140703424787.ident` was RED only because
`scripts/verdict` read the trailer `emit_sweep: DONE rc=1` that the job's grep copied into job.log.
emit_sweep exits 1 whenever base and feature differ at all, and this gate has expected movers. The real
judge, `ident_check.py`, printed `== ident_check COMPLETE: 0 unexplained`. No unexplained emitted-code mover.
Fix: the grep no longer copies the trailer (`l1ftri_evidence/ident.sh`, also applied to
`scratch/l1feat/ident.sh` so the retry of the queued job reads green).

## What the identity job compared
Base 07c840368 build (`scratch/l1feat/trees/base`) against the feature build (`scratch/l1feat/bin/pcrec`,
built at 1e2a4f5db; the later commits to 40e2e8626 change no file under src/cli/lib/memfn, only
src/facts/CLAUDE.md), over the 11 emit_sweep streams, then ident_check.py against the compare's observed
movers (`compare/observed.tsv`, 306 rows). Streams: c-default 10 movers, c-vm 10, facts 378 (306 census texts
plus utf8/bench keys), all other streams 0; asymmetric 0 everywhere.

## Each mover and its class
All 10 c-default movers are the same 10 patterns as c-vm; each is a census mover (req_set / req_byte /
req_set_maxoff facts moved). Every .c hunk is the content the moved fact feeds, never scaffolding (no
comment, declaration or layout change; the only non-content line is the `#include "b.h"`/`"f.h"` name
difference from my diff outputs):
- `[a-z]+(?<=a)@x`: `RX_REQ_RUN` `[61-7a]4078` -> `614078` (rep-copy class).
- `\w*(?=a)\w`, `\w+(?<=a)`, `\w+?(?<=a)`, `A*(?=a)\w`, `\w+(?<=a)b?`: `RX_REQ_BYTE` none -> 97, `RX_REQ_WHY` none -> dominated.
- `(?=a(b)?)\w\1?`: REQ_BYTE 97, WHY emitted, a `memchr` early-out in search, `RX_MEMFN_LIBC` gains memchr.
- `\b(?=a)\w+\b`, `[a-]{1,3}(?<=a|bc)\b`: REQ_BYTE 97, handoff emitted, prefilter/search code follows.
- `\w{1,3}(?<=a)b`: `RX_REQ_RUN` 6162@1, handoff 3 -> 2, a `rx_reqrun__body` helper.
Class: expected (design span_arms §14.4 L1: the facts layer moves on purpose and the search code that reads
the facts follows). Not an abi event: no scaffolding moved, and no non-mover moved.
The 378 facts movers are the 306 census movers plus per-source/utf8 duplicates; ident_check equates them.

## Fixes
`l1ftri_evidence/ident.sh`: drop `emit_sweep: DONE` from the grep and comment why. Retry:
`boxqueue retry l1feat-b20261119140703424787.ident`.

## STATE AT HANDOFF
Rulings file: none present. RERUN of the fixed script by hand: ident_check "0 unexplained", rc=0, scripts/verdict GREEN (log scratch/l1ftri/rerun.log). Not yet re-queued: main runs `boxqueue retry`.
