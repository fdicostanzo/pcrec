# Lens 8 — error-path and cleanup consistency

Lane `lens8err` (opus, read-only over `src/`, `cli/`, `lib/`). Charter:
`docs/dev/reviews/code_review_criteria_draft.md` (RATIFIED 2026-09-17),
lens 8. Base: `main` @ `7d444f9e`. Nothing under `src/`, `cli/`, `lib/`
or `tests/` was written; no `make`, no build, no suite run. Failure
injection was reasoned, never executed.

**Headline: the K7 discipline is in far better shape than a tree-wide
audit usually finds — and it has exactly one live hole, which is K7's
own defect verbatim.** Two Job-owned `StrBuf`s added after K7's fix were
never wired to the `Ctx`, so an allocation failure in either calls
`abort()` and kills the caller's process. That is the outcome K7's entry
calls "the worst item on this list", reachable on an ordinary VM
compile. Everything else found is maintainability or check-design.

---

## Summary of findings

| # | finding | severity | effort | blast radius |
|---|---|---|---|---|
| F1 | `Job.scr_test`/`scr_desc` have no `Ctx` back-pointer → `abort()` on OOM | **CORRECTNESS-RISK** | MECHANICAL | 1 file, 1 line; 0 checks staled |
| F2 | `cli_parse`'s failure returns leak `libdirs` at both call sites | MAINTAINABILITY | MECHANICAL | 1 file, 2 sites |
| F3 | `emit_state_legend` silently changes the emitted artifact on OOM | MAINTAINABILITY | LOCAL | 1 file; interacts with D76/D94 |
| F4 | `rxt_source.c` runs two disciplines for one event (arena aborts, heap diagnoses) | MAINTAINABILITY | LOCAL | 1 file; couples to `[LIB]` |
| F5 | `write_file`/stdout path never observe a write error → exit 0 on ENOSPC | MAINTAINABILITY | MECHANICAL | 1 file, 3 sites |
| F6 | the discipline's only check is SKIPPED on darwin and can pass vacuously; 0 sabotage rows | MAINTAINABILITY | LOCAL | check tier |
| F7 | a target's `.c`/`.h` pair can be left half-written | POLISH | LOCAL | 1 file, 2 sites |

---

## Method and population

The audit question (1) was answered by enumerating every raw allocation
call site by grep and classifying each, not by sampling. Tree-wide,
`src/` + `cli/` + `lib/` (60,326 lines) contains **38 raw
`malloc`/`calloc`/`realloc`/`strdup` sites in 10 files**:

| file | sites | failure route |
|---|---|---|
| `src/core/arena.c` | 1 | `ctx_nomem` when `a->cx` set, else `abort` |
| `src/core/sb.c` | 2 | `ctx_nomem` when `sb->cx` set, else `abort` |
| `src/core/compile.c` | 1 | checked, returns −1 with a diagnostic |
| `src/ir/nfa.c` | 1 | `ctx_nomem` |
| `src/ir/dfa.c` | 3 | `ctx_nomem` |
| `src/opt/minimize.c` | 7 | hand-free then `ctx_nomem` |
| `src/opt/scanedge.c` | 10 | hand-free then `ctx_nomem` |
| `src/gen/emit_dfa.c` | 5 | **silent degradation** (F3) |
| `src/parse/rxt_source.c` | 2 | return NULL / `rxt_fail` (F4) |
| `cli/main.c` | 9 | `perror` + nonzero exit |

Per ADDENDUM 2 the census (`tools/review/out/function_census.tsv`, 860
rows) was worked length-ranked top-down. The top ten by length —
`pcrec_emit_vm` (3,037), `compile_driver` (1,234),
`pcrec_rxt_source_parse` (975), `emit_info_def` (813),
`pcrec_select_engine` (559), `vm_emit` (515), `main` (514),
`emit_attempt` (509), `vm_render_listing` (501), `cli_parse` (431) —
were each read for their failure and cleanup routes. **Where the sweep
stopped:** below rank 25 (`pcrec_build_dfa`, 232 lines) functions were
not read individually; they were covered by the tree-wide greps
instead (allocation sites, `free()` targets, `setjmp`/`Ctx`
construction, file handles, mutable statics), each of which is
exhaustive over the primary tier by construction. No function below
rank 25 holds a raw allocation or a `setjmp`, so the unreviewed
remainder cannot contain an instance of audit questions (1) or (2); it
could in principle contain one of (5), and that is the residual.

---

## F1 — CORRECTNESS-RISK: two Job `StrBuf`s bypass `ctx_nomem` and abort the caller

**This is K7's own defect, live, in code written after K7 was closed.**

`compile_driver` attaches the error channel to the compile's allocators
at `src/core/compile.c:758-762`:

```c
cx.arena.cx = &cx;
cx.job = calloc(1, sizeof(Job));
if (cx.job) {
    cx.job->csb.cx = cx.job->hsb.cx = &cx;
    cx.job->vmsb.cx = cx.job->irsb.cx = &cx;
}
```

and its comment (`compile.c:755-757`) says *"the four Job buffers are
attached as soon as the Job exists."* **`Job` declares six `StrBuf`s,
not four.** `src/core/internal.h:2021` adds `scr_test` and `scr_desc`,
introduced by `[ART-SIZE]` well after K7's fix. They are never assigned
a `cx`, and `Job` is `calloc`'d, so both stay NULL for the whole
compile.

`sb_grow` (`src/core/sb.c:24-28`) is the consequence:

```c
char *np = realloc(sb->p, cap);
if (!np) {
    if (sb->cx) ctx_nomem(sb->cx);
    abort();   /* a detached buffer (syntax_dump.c) has no error channel */
}
```

So a `realloc` failure while appending to either scratch buffer takes
the `abort()` — **SIGABRT in the caller's process, no diagnostic** —
which `docs/dev/known_issues.md`'s K7 entry describes as *"the worst
item on this list"* and `src/core/CLAUDE.md` states as the rule the
back-pointer exists to enforce: *"pcrec is a LIBRARY, and aborting kills
the CALLER's process."* The `abort()`'s own comment names
`syntax_dump.c` as the one legitimate detached case, and it is now
wrong: these two buffers belong to a compile, have a `pcrec_error` to
report through, and are freed by `job_cleanup` (`compile.c:216-217`)
like every other Job buffer.

**Reachability is ordinary, not exotic.** `scr_test` is written by
`vm_cursor_rep` (`src/gen/emit_vm.c:4091`), the VM's **cursor rung** —
reached by any VM-engine pattern with a deterministic repeat over a
class sequence (`[a-z]{2,10}` and its family). The site appends in a
loop (`sb_puts(t, " && (")` and `vm_cls_test` per stride element), so it
genuinely grows. `scr_desc` (`emit_vm.c:8145`) is narrower —
`vm_render_listing`, i.e. `--emit-ir` only.

**Why no check saw it:** see F6. The discipline's only positive control
is `tests/resource/run_resource_tests.sh` section 2, which is skipped on
this box and whose four cells cannot steer an allocation failure to a
chosen call site.

**Secondary observation, benign today.** `sb_grow`'s `[ART-SIZE]`
early-abort is also `&& sb->cx`-gated (`sb.c:15`), so the size-term
ladder's scratch bound is inert for these two buffers as well. That half
is harmless — `compile.c:808-817` arms `abort_over` on `csb`/`vmsb`/`hsb`
only, and the scratch buffers are reset per use — but it is a second
behaviour riding the same missing pointer, so the fix closes both.

**Suggestion.** One line beside the existing four:
`cx.job->scr_test.cx = cx.job->scr_desc.cx = &cx;`, and correct
"the four Job buffers" to a form that cannot go stale again — the
comment's number is the thing that failed here, so prefer naming the
rule ("every `StrBuf` the Job owns") over recounting.

**A3 — checks bound to this code:** none. No sabotage row plants in
`sb.c`, `arena.c` or `compile.c`'s attachment block; no codegen text
grep reads it. The re-aim burden of the fix is zero, which is the same
fact as "nothing would have caught it".

---

## F2 — MAINTAINABILITY: `cli_parse` leaks `libdirs` on its own failure, at both call sites

`cli/main.c:1232-1240` states an invariant, and states it well:

> *"`--lib-path` is the only option in this CLI that ALLOCATES, so
> refusing it here is what makes "st.libdirs is non-NULL" true on
> exactly two paths — this one and the `--source` compile — both of
> which free it. **Every other exit from `main` provably has nothing to
> free**, which is why none of them carries a `free` that a reader would
> have to keep in step."*

The invariant holds for all ~45 returns **below** that comment. It fails
for the one **above** it:

- `cli/main.c:1228` — `if (cli_parse(argc - 1, argv + 1, &st, "command line") != 0) return 1;`

`libdir_push` (`main.c:362-374`) reallocs into `st->libdirs` inside the
same argument loop that has ~30 later failure returns, so
`pcrec --lib-path /x --bogus` allocates and then returns 1 without
freeing. On `main` the OS reclaims it, so this is a LeakSanitizer
finding rather than a user-visible one — but it falsifies the stated
invariant, which is the part that will cost the next reader.

**The second call site is the sharper one, because it is not a process
exit.** `apply_target` (`main.c:890-935`):

```c
int rc = cli_parse(n, v, &ts, where);
free(v); free(buf);
if (rc != 0) return 1;            /* :914 — ts.libdirs not freed */
...
if (!cli_extras_clean(&ts)) {
    free(ts.libdirs);             /* :929 — the only free of it in the file */
```

`grep -n "ts.libdirs" cli/main.c` returns exactly one line (929). A
`.rxt` `config` block spelling `pcrec --lib-path /x --bogus` therefore
leaks per target, inside a loop, returning to `compile_source` rather
than to the OS.

**The success path is safe, and structurally so** — see H10 below; that
is worth preserving in whatever fix lands.

**Suggestion.** Make `cli_parse` free what it allocated on its own
failure paths (it owns `libdir_push`), or add a one-line
`cli_state_free(&st)` used at both sites. The former keeps the
invariant's sentence true as written.

**A3:** no sabotage row or check binds to either site.

---

## F3 — MAINTAINABILITY: `emit_state_legend` silently changes the emitted artifact on allocation failure

`src/gen/emit_dfa.c:3602-3618` and `:3647-3648` are the only allocation
sites on the compile path that neither diagnose nor abort:

```c
int *dist = malloc(...); ... int *queue = malloc(...);
if (!dist || !from || !via || !queue) {
    free(dist); free(from); free(via); free(queue);
    return;                    /* a legend is never worth failing a compile over */
}
...
path = malloc((size_t)(maxd + 1) * sizeof(int));
if (!path) { free(dist); free(from); free(via); free(queue); return; }
```

The stated reason is right on its own terms — refusing a compile over a
comment would be worse. The consequence the comment does not state is
that **pcrec can emit two different artifacts for one input, exit 0
both times, with allocator state the only difference.** The legend is
emitted scaffolding, and D76/D94 make emitted scaffolding an `abi`
event precisely because readers pin it: the `.abi` stamp, the identity
gate's (B) pin, `tests/codegen/run_cpset_structure.sh`'s
`EMITTED_BYTES` manifest, and `docs/dev/artifact_size_log.tsv`'s
per-artifact byte counts all read a number this path can move without
saying so. `battriage_report.md` already records that the manifest's
rows *"never cite an abi digit at all but whose byte-count VALUES move
anyway"* — this is a third way for that class of reader to be moved,
and unlike the other two it is not deterministic.

This is a very low-probability path (four small `malloc`s of
`d->n * sizeof(int)`), which is exactly why it should be cheap to make
honest rather than cheap to leave.

**Suggestion.** Two options, both small. Either route it through
`ctx_nomem` like every other compile-path allocation — the legend runs
before the artifact is published, so the refusal is clean — or keep the
degradation and **emit a one-line comment saying the legend was
omitted**, so the artifact states what it is and a byte-count mover has
a visible cause. The second preserves the stated intent; the first is
consistent with the rest of the tree. Prefer the first unless someone
can name a caller who wants a legend-less artifact more than a refusal.

**A3:** `tests/codegen/run_cpset_structure.sh` CHECK 3's `EMITTED_BYTES`
manifest and `tests/size/`'s tripwire both read bytes this path can
move; neither can attribute a move to it.

---

## F4 — MAINTAINABILITY: `rxt_source.c` runs two disciplines for one event

Within one file, an out-of-memory has two different outcomes depending
on which allocator hit it:

- `src/parse/rxt_source.c:2101-2103` — `calloc` checked, returns NULL;
  and then, explicitly, `src->arena.cx = NULL;`. Every subsequent
  `arena_alloc` from that arena therefore reaches `arena.c:20-23` with
  no `cx` and **aborts**.
- `src/parse/rxt_source.c:3477-3480` — `realloc` checked, and the file
  raises a real diagnostic: `rxt_fail(..., "out of memory reading 'lib %s'")`.

The file's author clearly intended OOM to be a diagnosed refusal — they
wrote the diagnostic — and the arena half silently does the opposite.
`arena_strndup`/`arena_strdup` (`rxt_source.c:339-350`) take a bare
`Arena *` rather than a `Ctx *`, which is what makes the arena path
unable to diagnose; the three sibling helpers elsewhere in the tree
(`br_strndup`, `rc_strndup`, `ng_arena_strndup` — lens 1's X4 cluster,
cited not duplicated) all take `Ctx *` and route correctly.

**Severity is bounded today and the bound is worth stating precisely:**
`lib/pcrec.h` declares none of the `pcrec_rxt_source_*` surface, so the
only caller is the CLI, where an abort is a defensible exit. It stops
being defensible the moment lens 6's `[LIB]` linkable-library cut
exposes any of it — and `pcrec_compile_defs` already carries an
`RxtDefs` closure into the compile pipeline, so the seam is adjacent.

**Suggestion.** Either give `RxtP`/`RxtSource` a `Ctx`-shaped error
channel so the arena can diagnose, or state the abort as a deliberate
CLI-tier decision at `:2103` with the `[LIB]` condition that would
retire it. The current bare `src->arena.cx = NULL;` reads as an
oversight and is one line from being one.

---

## F5 — MAINTAINABILITY: a failed write is never observed

`cli/main.c:292-299`:

```c
static int write_file(const char *path, const char *text)
{
    FILE *f = fopen(path, "w");
    if (!f) { perror(path); return -1; }
    fputs(text, f);                              /* return unchecked */
    if (fclose(f) != 0) { perror(path); return -1; }
    return 0;
}
```

`fclose` catches the common ENOSPC case (the data is still buffered),
so this is mostly covered — but `fputs`'s return and `ferror(f)` are
both unread, and for a write large enough to flush mid-call the error
indicator is what carries the failure.

**The stdout path has no coverage at all.** `main.c:1209` and
`main.c:1726` both do a bare `fputs(out.c_src, stdout)` and then return
0, with no `fflush`/`ferror` before returning. `pcrec -p rx -o - 'a+' >
/full/disk` therefore **exits 0 having written nothing** — and `-o -`
exists for exactly the build-pipeline use where an unnoticed empty
output is worst.

**Suggestion.** Add `if (fflush(stdout) != 0 || ferror(stdout))` before
the `return 0` on both stdout paths, and `ferror(f)` to `write_file`
alongside the existing `fclose` check. MECHANICAL.

---

## F6 — MAINTAINABILITY (check design): the discipline's only check is skipped here and can pass vacuously

This is the reason F1 survived, so it is filed as a finding rather than
as context.

**There are zero sabotage rows on the error-path discipline.** Over 262
rows in `tests/mech/sabotages/`, none plants in `arena.c`, `sb.c`,
`minimize.c`'s cleanup blocks, `scanedge.c`'s cleanup blocks, or
`compile.c`'s attachment block. (`S213`/`S215` name `scanedge.c` but aim
at scan-edge *selection*, not its cleanup.) The single detector is
`tests/resource/run_resource_tests.sh` section 2, whose own header
states the claim under audit:

> *"Every allocation on the compile path reports through `ctx_nomem()`
> instead of `abort()` (`src/core/{arena,sb,compile}.c`,
> `src/ir/{nfa,dfa}.c`, `src/opt/minimize.c`)"*

Three problems, in increasing order of importance:

1. **The file list is stale.** It names six files; the tree now has ten
   with raw allocations. `scanedge.c` joined and is correctly routed;
   `emit_dfa.c` joined and is not (F3). A claim enumerated by a
   hand-written file list goes stale exactly the way `dialimpl`'s
   §5.3a manifest and `w23implfix`'s five-token withdrawal check did —
   this is the same class, third instance.

2. **The section is SKIPPED on darwin** (`run_resource_tests.sh:705-706`),
   because RLIMIT_AS is not enforceable on macOS. The skip is loud,
   named and correct — Frank's own interim disposition — but its
   consequence is that since the 2026-09-04 Mac move **the only positive
   control for the `ctx_nomem` discipline has not run on the development
   box at all.** Combined with K54 (the `san` stage was silently broken
   on darwin until 2026-09-14), the entire memory-error tier is
   Linux-only, and F1 was introduced and shipped in that window.

3. **A cell can pass without ever reaching an allocator.** The verdict
   arm (`:659`) accepts any of three diagnostics:
   `grep -q 'out of memory\|too complex\|too large'`. Only the first is
   an allocation failure; the other two are the *budget* refusals
   section 1 tests. So a cell whose `ulimit` stopped binding — because a
   cap was retuned, or an optimization pass cut the pattern's
   footprint, which `[OPT-4]` has already done once to this exact
   section (`:686-694`) — passes on the wrong mechanism. The `0)` arm
   correctly scores "it compiled" as a failure; there is no arm for "it
   refused for the other reason". That is `learnings.md` §3's
   controls-share-a-source shape at the *verdict* rather than at the
   population.

Even repaired, the section could not have found F1: an address-space
limit makes *whichever* allocation crosses the line fail, and nothing
steers it to a chosen call site. The header's claim that four patterns
put the failure in four named allocators (`:679-683`) is asserted, not
measured — no cell verifies which site failed.

**Suggestion, in priority order.** (a) One sabotage row that reverts a
`ctx_nomem` to `abort()` and asserts section 2 reddens — the row K7's
own fix note describes having run manually ("reverting `ctx_nomem` to
`abort()` fails 4 checks") but never committed. (b) Split the verdict
arm so `out of memory` is its own cell outcome, distinct from a budget
refusal. (c) Replace the hand-written file list with something derived
— a grep-based census of raw allocation sites and their failure routes,
asserted against a pinned count, would have failed the day `emit_dfa.c`
and `scr_test` arrived. (d) A build-time `-D` allocation-failure
injector would reach a *chosen* site and is the only instrument that
finds an F1 directly; it is a DESIGN-EVENT and should wait for (a)-(c).

---

## F7 — POLISH: a target's `.c`/`.h` pair can be half-written

`cli/main.c:1210-1211` and `:1728-1729`:

```c
} else if (write_file(cpath, out.c_src) != 0 ||
           write_file(hpath, out.h_src) != 0) {
```

Short-circuit means a `.c` written successfully followed by a failed
`.h` leaves the `.c` on disk, referencing a header that is absent or
stale. In the multi-target `--source` loop, targets `0..i-1` are already
written when target `i` fails. A consumer's `make` then sees a fresh
`.c` and an old `.h` — the one combination that miscompiles quietly.

This is ordinary CLI behaviour and may well be the intended trade; it is
filed so the decision is recorded rather than defaulted. The cheap
mitigation is to `remove(cpath)` when the `.h` write fails, which makes
the pair atomic enough for `make` without a temp-file dance.

---

## PROBED-AND-HELD

Negative results with the evidence behind them, so this ground is not
re-covered. **The discipline holding is the main result of this lens.**

- **H1 — every `setjmp` has its `Ctx`, and nothing that can fail
  allocates before it.** Five `Ctx` constructions tree-wide
  (`compile.c:692`, `:1851`; `syntax_dump.c:731`, `:1027`, `:1522`) and
  five `setjmp` sites (`compile.c:822`, `:1874`; `syntax_dump.c:760`,
  `:1038`, `:1547`) — a 1:1 pairing. Each pre-`setjmp` window was
  grepped for `arena_alloc`, `sb_*`, `ctx_fail`, `arena_strdup` and
  `pcrec_parse`: **zero hits in code** across all five (the two textual
  hits in `compile.c`'s window are inside comments). R20's tier-1 class
  — a hand-built `Ctx` reaching `ctx_fail` with an unarmed `jmp_buf` —
  is structurally closed.

- **H2 — the `volatile` discipline across `setjmp` is complete and
  mechanically backed.** `compile_driver` declares eleven scalars that
  cross the boundary (`dfa_disabled`, `collapse_reason`,
  `size_drop_rung`, `dropped_anchored`, `dropped_premul`,
  `size_cap_bytes`, `size_cap_limit`, `dfa_was_engine`,
  `budget_fallback`, `st_phase`, `st_idx`) and every one is `volatile`,
  with the arrays (`overflow_why`, `st_k`/`st_ok`/`st_code`/`st_total`)
  correctly exempt. A scan of the function's remaining locals found no
  unmarked non-array scalar. The discipline is not prose: `-Wclobbered`
  rides `-Wextra` in `WARN` (`Makefile:16`), which `make strict` promotes
  to `-Werror` (`Makefile:1173`). **One caveat worth recording:**
  `-Wclobbered` is only meaningful with optimization on, and
  `ALLFLAGS = $(CFLAGS) ...` with `CFLAGS ?= -O2` (`Makefile:15,17`) — a
  `make strict CFLAGS=-O0` is a silently vacuous gate. Not a finding
  (nobody does this), recorded because the gate's power depends on an
  overridable variable.

- **H3 — no `free()` of an arena-backed pointer anywhere.** All 76
  `free()` call sites in the primary tier were classified by target;
  every one is a heap pointer. The arena/heap boundary is respected in
  both directions, including the subtle cases (`minimize.c:188`'s
  rebuilt states take their `tr` from `arena_alloc` while the `DState`
  array itself is `calloc`'d and freed; `scanedge.c:673`'s permuted rows
  carry arena `tr` pointers through a heap scratch array).

- **H4 — `tab_grow`'s apparent double-free is not one.**
  `src/ir/dfa.c:879-883` reads `free(d->tab); d->tab = malloc(...); if
  (!d->tab) { d->tabcap = 0; ctx_nomem(cx); }`, and the comment claims
  *"`d->tab` is already NULL here"* over a `free` that does not null it.
  The claim is nonetheless true — `malloc`'s NULL return is assigned into
  `d->tab` on the line between — so `job_cleanup`'s later
  `free(cx->job->dfa.tab)` frees NULL. Held; the comment's wording is
  the only thing that invites a second look.

- **H5 — `minimize.c`'s seven heap tables are correct on all three
  exits.** Both failure blocks (`:87-90`, `:165-169`) free every table
  live at that point before `ctx_nomem`, and the success path frees all
  seven (`:216-217`, `:220-224`). This is K7's named hand-cleanup exception and it
  has stayed correct through two subsequent edits ([M6.2] wave B's accept
  bits, the `has_end` signature narrowing).

- **H6 — `scanedge.c`'s ten heap tables are correct on all four exits.**
  Failure (`:518-521`), the `nfound == 0` early return (`:532-534`), the
  inner `ns` failure (`:654-659`) and the success path (`:688-689`) each
  free the full set. The nine-way free block appearing four times is a
  lens 1 extraction candidate, not an error-path defect — cited, not
  duplicated.

- **H7 — library re-entry is clean.** `grep` over `src/` and `cli/` finds
  **zero function-local statics** and exactly two file-scope mutable
  objects, both in `src/parse/enabled.c` (`g_enabled_label`,
  `g_enabled_modules`, plus `g_enabled_features`). All three are
  write-once at spec-parse time, before any compile, documented as such
  at that file's head, and relied on by the thread suite. A second
  `pcrec_compile` in one process inherits no poisoned state from a
  failed first one: `job_cleanup` (`compile.c:197-229`) frees all six
  `StrBuf`s, all eight machine arrays, the three taken-but-unpublished
  strings and the `Job` itself, then `arena_free`s. The `Ctx` is a fresh
  stack local per call.

- **H8 — allocation is architecturally confined.** `src/gen/emit_vm.c`
  is the largest file (11,575 lines) and holds the tree's longest
  function (`pcrec_emit_vm`, 3,037 lines) — and it contains **zero raw
  allocations**. So do `src/parse/parse.c`, every `mod_*.c`, and every
  `opt/` pass except `scanedge.c` and `minimize.c`. The emitters allocate
  only from the arena and the Job's buffers. This is why F1 is the only
  hole: there are very few places for one to be.

- **H9 — the three `Ctx`-taking `strndup` helpers all route correctly.**
  `br_strndup` (`mod_backrefs.c:141`), `rc_strndup`
  (`mod_recursion.c:99`) and `ng_arena_strndup`
  (`mod_named_groups.c:76`) each call `arena_alloc(&cx->arena, ...)`, so
  a failure reaches `ctx_nomem` through the attached back-pointer. Only
  `rxt_source.c`'s bare-`Arena` pair diverges (F4).

- **H10 — `apply_target`'s success path cannot leak `ts.libdirs`, and
  the reason is structural.** `cli_extras_clean` (`main.c:354-360`)
  tests that the entire tail of `CliState` past `opt` is all-zero, and
  `libdirs` lives in that tail — so a non-NULL `libdirs` *forces* the
  `:929` branch that frees it. The success path provably has nothing to
  free. Worth preserving explicitly when F2 is fixed: it is a real
  invariant that a naive "free it everywhere" patch would obscure.

- **H11 — K11's returned-claims epilogue is intact.** The four doorways
  still return `ExtResult`; `noreturn` survives only where it belongs
  (`ctx_fail`, `ctx_nomem` — `internal.h:2531`, `:2541`) and on no
  doorway; and all four call sites end in internal-error walls
  (`parse.c:830`, `:903`, `:1323`, `:1345`, plus `ext.c:108`'s
  unconsumed-outcome wall). The UB this entry recorded remains
  structurally unrepresentable.

- **H12 — file handles are balanced.** Three `fopen` sites tree-wide
  (`cli/main.c:294`, `src/parse/rxt_source.c:552`). Every error route in
  `rxt_source`'s reader closes before failing (`:555`, `:557`, `:561`,
  `:562` — four exits, four `fclose`es). No `tmpfile`, `mkstemp`,
  `unlink` or `remove` anywhere in the primary tier, so there is no
  temp-file cleanup obligation to get wrong.

- **H13 — the `-o` path writes nothing before the compile succeeds.**
  Both output routes (`main.c:1208-1216`, `:1725-1733`) compile fully
  into memory and only then write, so a refused pattern cannot truncate
  or partially overwrite a previous artifact. The only partial state is
  the `.c`/`.h` pair (F7).

---

## Admissibility notes

- **A1 (ruled record).** No finding here contradicts a D-row or a ruled
  section. F3 and F4 both *cite* rulings that constrain the fix rather
  than oppose it: D76/D94 (emitted scaffolding is an `abi` event) makes
  F3 worth closing, and F4's severity bound rests on `lib/pcrec.h`'s
  current surface, which lens 6's `[LIB]` work may move. F6(d)'s
  allocation-failure injector is named as a DESIGN-EVENT and deferred
  under D77 — no measurement today triggers it; F6(a)-(c) are the cheap
  instruments that would.
- **A2 (abstraction bar).** Only one duplication is touched, and it is
  deferred to lens 1 with the abstraction named: `scanedge.c`'s nine-way
  free block appears four times (`:518`, `:532`, `:656`, `:688`) and
  wants a single `se_free(...)` or a small owned-table struct. Filed as
  H6, not as a lens 8 finding.
- **A3 (check coupling).** Stated per finding. The aggregate: **the
  fixes proposed here stale zero existing checks**, because zero
  existing checks bind to the code they touch. That is F6.
- **A4 (severity/effort/blast).** In the summary table; F1 is the only
  CORRECTNESS-RISK and carries its reaching call sequence (a VM-route
  pattern taking the cursor rung → `vm_cursor_rep` → `sb_puts` on
  `scr_test` → `sb_grow` → `realloc` returns NULL → `abort()`).
- **A5 (evidence).** Population counts are from tree-wide greps stated
  in the Method section; the length ranking and the stopping point are
  from `tools/review/out/function_census.tsv`; lens 1's X4 strndup
  cluster is cited to
  `worktrees/lens1dup/docs/dev/reviews/lens_reports/lens1_semantic_duplication.md`
  rather than re-derived.

---

## Ranked for the synthesis

1. **F1** — MECHANICAL, one line, closes a live caller-abort. Do this
   first regardless of wave ordering; it does not wait on a refactor.
2. **F6(a)+(b)** — the sabotage row and the verdict split, so F1's class
   cannot recur silently. (c) follows when someone is in that file.
3. **F2**, **F5** — MECHANICAL, CLI-local, independent of everything.
4. **F3** — LOCAL, wants a one-line ruling (refuse vs. announce) before
   the edit.
5. **F4** — LOCAL, but the right moment is whenever lens 6's `[LIB]` cut
   touches the `rxt_source` surface.
6. **F7** — POLISH, a recorded decision more than a fix.
