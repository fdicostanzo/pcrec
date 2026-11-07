# [VMREC] — the record vocabulary step (c)'s analysis must model

Written directly as a body (the `BOXQUEUE.md` / `CAP-SPAN.md` precedent) by
the [VLOOKBEHIND] stage-1 build (lane vlbbuild, 2026-11-06), under ruling 7
of review 2026-11-06 r2 (`docs/design/vlookbehind.md` §5.6 `[r2-1106 F7]`):
new members of the closed lists `VmSeek` and `VmLocalKind` are row
additions that do not wait for [VMREC], and [VMREC] lists them here. The
plan.md row is the status of record; this file is the member list.

## Members added after step (a), with the declared effect (c) will read

From [VLOOKBEHIND] stage 1 (`src/gen/vm_stmt.h`, `vm_look_behind_branch`
in `src/gen/emit_vm.c`):

- `VSK_STEP_CHAR` (a `VmSeek` member): writes the subject cursor; reads the
  cursor, one slot (`POS`) and the subject; calls the seam entry
  `$_fwd_step`.
- `VL_LB_COUNT` (a `VmLocalKind` member): an untrailed local, one per
  artifact (`<p>_lb_count`), live only between a `range` branch's guard and
  its first push.
- The `VSK_BACKSTEP` local count operand (`byloc`, `x`, built only by
  `pcrec_vm_b_seek_local`): reads that local.
- Two operands that read the local through TEXT rather than as a record
  field: the decrement's src and the far `VK_WORK` count. Existing `rv`
  locals have the same shape, so (c)'s rule "every analysed operand is
  printed by its renderer or carried as a record field" lists them with the
  `rv` reads rather than as new.

No new `VmKind` was added.

Maintenance: a later row that adds a member to a closed record list appends
it here, with its effect.
