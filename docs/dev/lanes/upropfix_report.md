# upropfix report: the uprops local arena (K155 class) on main 96b2587a8

STATE: stopped (the brief's own stop rule: the house-form fix raises peak memory above noise; a ruling is needed)

## Summary

Main is red on `tests/core/scratch_builder_check.py` because `uprops_produce` (src/parse/mod_uprops.c) decodes a property set into a private `Arena tmp = { .cx = cx }` and then calls `pcrec_ast_class_from_iv`, which allocates from the compile arena and can refuse. A refusal there longjmps with tmp's block live: a strand, K155's class.

I measured the house form the brief names first (decode straight into `cx->arena`, drop tmp). It fixes the strand but raises peak RSS at 4,000 `\p{L}` in a class from 77.4-77.7 MB to 99.8-100.1 MB (+29%, three runs each). That is the regression r97 IDENTITY-2 existed to remove and dpfix removed. Per the brief I STOPPED, reverted the trial edit and changed no code. The branch carries only this report.

## Class

- CLASS: a resource live across a refusal that nothing frees on the longjmp. Here the resource is a private arena's blocks: the decoded interval list, 8n bytes, at least one 64 KB block. It is K155's class. It is not K163's: tmp's `.cx` IS the running Ctx, so it fails into the right recovery point. That point just does not know about tmp.
- HOUSE RULE BROKEN: src/core/CLAUDE.md, "Builders that can be interrupted by `pcrec_ctx_fail` must be arena-backed: `pcrec_sb_scratch(&cx->arena)` ... (K155; gate `tests/core/scratch_builder_check.py`)". An Arena that is not the Ctx's own is a heap builder by that rule.
- THE WINDOW: `pcrec_ucd_find(&tmp, ...)` makes one allocation (ucd_tables.c `ucd_decode`), so if it fails on its own malloc nothing is stranded. Then `pcrec_ast_class_from_iv(cx, ...)` runs `node()`, `pcrec_cpset_add` and `cls_finish`, all on `cx->arena`. Any of their OOMs, or any refusal `cls_finish` raises, strands tmp's block.
- WHY THE TWO GREEN BRANCHES MADE A RED MAIN: K155's gate (merge d69bdc2af) and dpfix's local arena (merge 6c9342003, the IDENTITY-2 fix) never met before the merge.
- WHY A LOCAL ARENA WAS CHOSEN (dpcompact_report.md, dpfix_report.md, review r97 IDENTITY-2 and its RULED section): BASE handed out a static pointer into the table. dpcompact decoded every `\p` into the compile arena, on the probe passes too, and peak RSS rose 78.1 -> 99.9 MB (+5.5 KB per item). The ruling said "decode only when the result is wanted. Show peak RSS at 4,000 \p{L} within noise of BASE." dpfix met it two ways: `pcrec_ucd_exists` for the probe, and a scratch arena freed right after the class constructor copies the set. The scratch arena is the part that met the PEAK bar. Decoding only when the result is wanted is not enough alone: decoding into `cx->arena` on the result pass only measures 99.8-100.1 MB (below).
- SIBLINGS: every other `Arena <name> = ...`/`Arena <name>;` local on the compile path. `grep -nE '(^|[^\w*])Arena\s+[A-Za-z_]\w*\s*(=|;)' src/{core,enc,parse,ir,facts,opt,gen}/*.c` = 4 hits, this one plus 3 others, and the check allows each of the 3:
  - src/core/compile.c:252 `pcrec_subst_compile`, `Arena a = { 0 }`: ALLOW "a detached arena, freed on return, no Ctx". There is no Ctx, so nothing can longjmp. Safe.
  - src/gen/emit_subst.c:1210 `pcrec_emit_subst`, `Arena a = { 0 }`: ALLOW "a detached arena, no Ctx". Safe for the same reason.
  - src/gen/clskit.c:1126 `pcrec_clskit_emit_kit`, `Arena a = { .cx = c->cx }`: ALLOW under the `[ARENA-SCOPES] client` block, "a private arena never registered on the Ctx". It is a KNOWN strand, and K155 stays open for it until [ARENA-SCOPES] lands. It has exactly this site's shape.
  The Arena struct fields outside those: `Ctx.arena`, which job_cleanup frees, and `RxtSource.arena` (internal.h), which has no Ctx and errors by return. So this site is the second private arena with a live Ctx. clskit.c is the first, and it is allowlisted as a known strand, not as safe.
- DYNAMIC CONTROL: `tests/core/alloc_check.c` witness W3 is `\p{L}` under `-e utf8`, so it reaches this window. I did NOT run `make test-alloc`: the box lock was held by queue job 200-main-step0, and I did not idle-wait. Whether W3 goes red on main 96b2587a8 is OPEN. If it stays green, alloc_check does not see this strand, and that is a second finding for the follow-up.

## Fix

No fix is committed. I measured the forms below with the dpfix command:

```
/usr/bin/time -f "%M KB" build/pcrec -e utf8 --features classes,unicode-props -p p -o OUT.c \
    --pattern "$(cat $PCREC_TMPDIR/scratch/dpfix/pl.pat)"     # [ + \p{L} x 4000 + ]
```

| form | peak RSS, 3 runs | emitted C |
|---|---|---|
| main 96b2587a8 (local `Arena tmp`) | 77,564 / 77,652 / 77,380 KB | reference |
| house form: decode into `cx->arena`, tmp removed | 99,776 / 100,072 / 100,088 KB (+29%) | identical except the generated file's own `#include "<name>.h"` line |

dpfix measured BASE (before dpcompact) at 78.1 MB, so main today is at BASE and the house form is +22 MB. That is far above noise, so by the brief this is the stop case.

Options for the ruling. My recommendation comes first.

1. (recommended) ALLOW row now, real fix rides [ARENA-SCOPES]. Add `("src/parse/mod_uprops.c", "uprops_produce", "arena:tmp", "[ARENA-SCOPES] client: transient decode, freed on return; stranded on an OOM/refusal in pcrec_ast_class_from_iv")` to the check's existing `[ARENA-SCOPES] client` block. clskit.c's identical shape sits there today. Add the site to [ARENA-SCOPES]'s client list and one sibling line to K155. This is the general mechanism with a GO (architecture note accepted, design D-1..D-12 pending), and the site is a textbook scope client: a LIFO transient freed on return. Cost: main stays one known strand worse until the scopes build. The strand is at least 64 KB per refused compile, and only on an OOM or a refusal inside the class constructor. The brief excluded an ALLOW row whose reason is not "never live across a refusal", so this needs the manager's override. The precedent is the clskit row.
2. A Ctx-owned scratch arena (`Arena ucd_scratch` on `Ctx`, freed in job_cleanup's unconditional tail beside `cx->arena`, emptied after each use). Peak stays where it is today, because it frees per use like the current tmp. But the teardown has more sites than job_cleanup: src/dump/syntax_dump.c has three refusal handlers that free `cx.arena` by hand (around lines 881/952/978, 1210/1256 and 1725). One of them parses patterns that can reach `\p`. Each would need the second free, and the scan does not cover src/dump. That is a hand-kept parallel teardown, the thing [ARENA-SCOPES] exists to replace. I would not build it.
3. No transient array at all: a streaming decode. The class constructor would read the set through an iterator over ucd_tables' interval cursor (`UcdCur`), e.g. a `pcrec_ast_class_from_ucd` or an opaque cursor in ucd_tables.h. Peak would fall below today's, and no arena question would remain. Cost: an interface change in ucd_tables.h, plus the ucd wall check's needle, which flags `Ucd*` names outside the module, so the cursor would need an opaque public name. It also widens parse.c's constructor family. It is a real design change with its own review, not a red-main fix.
4. Accept the +22 MB with the house form. That reverses r97's IDENTITY-2 ruling, so it is the owner's call, and I do not recommend it.

## Checks

- `python3 -I tests/core/scratch_builder_check.py <worktree>` on the unchanged tree: rc 1, the brief's exact FAIL line (src/parse/mod_uprops.c:290). That reproduces the red.
- Trial (house form, reverted): `make -j16` rc 0. Peak and identity are in the table above.
- After the revert: `make -j16` rc 0, and the tree matches lane/upropfix HEAD (`git status` clean before this report).
- NOT RUN, because no fix was committed: `make test-registry`, the parse tier, `make strict`, the anchor check, the byte-identity sweep, `make test-alloc`, and the queued `upropfix-test`. No sabotage id was taken.

## STATE AT HANDOFF

- STOPPED for a ruling on the fix form (options 1-4 above; I recommend 1). No code change. The branch holds this report only.
- Rulings file `docs/dev/lanes/upropfix_rulings.md`: re-read before this report. It is empty, so no ruling was applied.
- OWED: `upropfix-test` (the deliver file's owed key). It is NOT queued, because there is no fix to test. A follow-up lane queues it after the ruled fix.
- OPEN for the follow-up: does `make test-alloc` (alloc_check W3 = `\p{L}`) go red on main 96b2587a8? See Class, "DYNAMIC CONTROL".
- Scratch: `$PCREC_TMPDIR/scratch/upropfix/` (p_cur.c, p_A.c, the original mod_uprops.c copy, build logs). No queue jobs from this lane.
