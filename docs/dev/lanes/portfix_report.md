# portfix — the emitted-code portability fix (2026-09-14, lane portfix, sonnet)

Charter: `docs/dev/lanes/anchtriage_report.md` §1 (the diagnostic) and §4
disposition (a) — the label-immediately-followed-by-declaration shape in the
DFA reverse-pass/anchored-form scan-edge emission, plus the abi 24 -> 25
event that rides it. Branch `lane/portfix`, worktree `worktrees/portfix`,
parked on the branch per the brief (a battery is in flight on this box;
the manager merges).

## 1. The defect, and where it actually lives

The triage report's reproduction named one line (`on.c:283`) and one label
(`on_reverse_scan_views:`), but warned the emission is templated through the
Forward/Reverse/Anchored `DfaDir` fold and asked for a grep of the fold's
consumers rather than trust in one line number.

**The templated site is `emit_scan_loop` in `src/gen/emit_dfa.c`**, the one
function `emit_unanchored`/`emit_attempt` call TWICE (once per `DfaForm`, so
once per direction — Forward, Reverse, and, since `[ENG-ABS]`, Anchored — all
three route through this one body). It emits two labels:

- `lv`, the `scan_views` label (`scan_label(lv, sizeof lv, f, "views")`),
  printed whenever the machine carries a scan edge (`if (edges) ...`,
  `emit_dfa.c` around the pre-fix line 5888). Immediately after it,
  `f->view->emit(c, f)` runs for any machine with a position view
  (`end`/`eol`/`end+eol` — the `none` view's `emit` is `NULL`), and every one
  of the three real view-emit functions (`view_emit_eol_only`,
  `view_emit_end_only`, `view_emit_end_and_eol`) opens by calling
  `view_decl`, whose FIRST line is the declaration
  `<dir>_view_state = <dir>_state;`. That is the label-then-declaration
  shape gcc accepts as a `-std=gnu11` extension and clang 21 rejects under
  `-Werror` as `-Wc23-extensions`.
- `le`, the `scan_edge` label, printed whenever the entry seed can land on a
  head (`if (seedhead) ...`). Nothing declares immediately after it TODAY
  (`f->acc->emit_top` is an `if`-statement when present; `f->pf->emit`'s
  first line is always a `//` comment), so it was not part of the
  reproduced failure — but it is emitted by the SAME templated function, and
  a future view or accessor form that starts with a local would reopen the
  identical hazard there silently.

Both labels are per-MACHINE (Forward/Reverse/Anchored), not per-artifact, so
the fix at this one site covers all three directions the fold spans —
exactly the "grep the fold's consumers" instruction, discharged by finding
there is only one consumer function, not three.

## 2. The fix

`src/gen/emit_dfa.c`, `emit_scan_loop`: both label emissions gain a trailing
`;` (an empty statement) after the colon —
`"%s  %s:\n"` -> `"%s  %s:;\n"` at both the `lv` and `le` sites. Mechanical,
as the charter predicted: an empty statement is a no-op on every compiler,
costs one byte on every scan-edge-bearing machine (whether or not it also
carries a view), and closes the hazard class at its one source rather than
patching the one reproduced spelling.

Commit `05c27b43` (`[PORTFIX] fix: gcc-16-vs-clang21 label-then-declaration
in the DFA scan-edge emission`).

## 3. Witness measurement, before AND after, independently reproduced

`docs/dev/lanes/anchtriage_report.md` §1 already carries one before/after
pair for `(a+)$`; this lane took a fresh independent measurement rather than
trusting the transcript, by `git stash`-ing the fix, rebuilding, and
re-running the same commands:

```
$ cc -O1 -std=gnu11 -Wall -Wextra -Werror -I. -o drv_clang_before \
      anchdiff_driver.c on_before.c off_before.c
on_before.c:283:13: error: label followed by a declaration is a C23
  extension [-Werror,-Wc23-extensions]
  283 |             on_reverse_state reverse_view_state = reverse_state;
      |             ^
off_before.c:283:13: error: ...(same, off_reverse_state)
clang exit: 1

$ gcc-16 -O1 -std=gnu11 -Wall -Wextra -Werror -I. -o drv_gcc_before \
      anchdiff_driver.c on_before.c off_before.c
gcc exit: 0
```

Fix restored, rebuilt, then all **six** patterns the triage report named
(`(a+)$`, `(?m)ERROR$`, `([^c]{1,3})$`, `(a{0,4}c$)`, `(a{1,3}?$)`, `ERROR$`)
compiled with `-p on`/`-p off --no-captures --features all
[-fno-anchored-dfa]`, linked against `tests/anchored/anchdiff_driver.c`
under `-O1 -std=gnu11 -Wall -Wextra -Werror`:

| pattern | clang (`cc`) before | clang after | gcc-16 before | gcc-16 after |
|---|---|---|---|---|
| `(a+)$` | error (Wc23-extensions) | clean | clean | clean |
| `(?m)ERROR$` | error | clean | clean | clean |
| `([^c]{1,3})$` | error | clean | clean | clean |
| `(a{0,4}c$)` | error | clean | clean | clean |
| `(a{1,3}?$)` | error | clean | clean | clean |
| `ERROR$` | error | clean | clean | clean |

All six: clang goes error -> clean, gcc-16 stays clean throughout — exactly
the disposition the charter predicted. Scratch reproduction under
`/private/tmp/claude-501/.../scratchpad/portfix_witness/` (session
scratchpad, not committed, per the scope mandate).

## 4. The abi ritual (abi 24 -> 25)

Emitted-scaffolding change per D76/D94, so it is an abi bump + identity-gate
re-pin in the same change. **The reader list was found by grep, not
hand-enumerated** (this file's own D94 citation warns a hand list missed a
fifth reader in `match_api.md` once):

```
grep -rn '\.abi = 24\|ABI_EXPECT=24\|rx_info\.abi.*is.*24\|is `24`' \
     --include='*.c' --include='*.h' --include='*.sh' --include='*.md' .
```

Four LIVE readers found (a fifth, `docs/spec/tuning.md`, was checked and
carries no bare abi-number claim to move):

| site | change |
|---|---|
| `src/gen/emit_dfa.c` (`.abi = 24,` emission) | `.abi = 25,` + a new `[PORTFIX]` bump-history comment block, same per-artifact-kind shape (r37 A12's lesson) every prior bump carries |
| `tests/codegen/run_codegen_tests.sh` (`ABI_EXPECT=24`) | `ABI_EXPECT=25`, event appended to the `[DD-14.FB]` bump-history `bad` message |
| `tests/codegen/run_recursion_identity.sh` (comparison (B) `FILEPIN`) | new comment block for the event; **`FILEPIN` value itself LEFT UNSET** (still `8e0fe77f`) — see §5 |
| `docs/spec/match_api.md` (TWO live occurrences: the caller-facing abi paragraph near the top, and the §6.3 reflection-facts entry) | both updated `24` -> `25`, the new event prepended to each chain, old `24`-was-`[K50]` text kept as the next link |

Everything else the grep matched is historical narration (lane reports,
`docs/dev/decisions.md`'s D97 entry, `docs/dev/plan.md`'s archived
`[K50-BNDSTART]` row, design-doc landing notes) and is untouched per
`docs/dev/lanes/CLAUDE.md`'s own rule — those record what was true when
written, never a live claim about today's abi.

**Comparison (A) is untouched, structurally, not by exception.** Both
labels live inside `pcrec_emit_dfa_engine` — for a hybrid, called from
`emit_vm.c`'s prefilter block ABOVE the `goto <p>_L0;` marker
`run_recursion_identity.sh`'s `prog_region()` extracts; for a non-hybrid DFA
artifact, reached with no such marker in the file at all. `prog_region()`
returns empty either way, `[OPT-EDGE]` STEP 1's own abi-18-19 precedent
exactly. No new deny-axis IFF was needed on (A).

### The (B) pin is deliberately left UNSET, owed to the manager

Per `opt5i_report.md`'s and `ccdiff1_report.md`'s precedent (cited directly
in the brief): a pin must name a commit reachable AFTER the merge, and a
lane branch's own commit is not one yet. `RECURSION_IDENTITY_FILEPIN`
default stays `8e0fe77f` in this branch's `tests/codegen/
run_recursion_identity.sh`. **Owed at merge**: re-pin to the merge commit
(the one that lands this branch's src changes on main), matching every
prior lane's own abi-bump handoff.

## 5. Validation status

- **`make -j4 CC=gcc-16`**: clean, twice (once for the mechanical fix alone,
  once after the abi-comment commit).
- **`make strict CC=gcc-16`**: **GREEN** — `strict: whole tree compiles
  clean with -Werror -Wshadow`.
- **The direct witness pair (§3)**: **COMPLETE**, six patterns, both
  compilers, before and after, all as predicted.
- **`make test-codegen CC=gcc-16`**: **NUMBERS OWED, RUNNING IN
  BACKGROUND.** A first foreground attempt hit the tool's own 2-minute
  wall and was killed before `run_codegen_tests.sh`'s own group even
  reported a line — this box has a full battery (`build/
  battery_20260914_021456`, stages `test strict axes san lint mech`)
  running concurrently in its `mech` stage per the brief's box constraint,
  and codegen's own corpus sweeps are slow under that contention.
  Relaunched: `nohup bash -c 'timeout 1800 make test-codegen CC=gcc-16' >
  /tmp/portfix_test_codegen2.log 2>&1 &`, background pid `72301`
  (`run_codegen_tests.sh`'s own `ABI_EXPECT=25` check is inside this
  group). **A fresh agent or the manager should tail
  `/tmp/portfix_test_codegen2.log` for its `checks passed`/`checks failed`
  trailer** (a session-scratch path per the scope mandate, not a committed
  artifact — if the process has since exited on session end, re-run the
  same command fresh).
- **`bash tests/anchored/run_anchored_diff.sh` (the section the whole
  triage chain started from)**: **NUMBERS OWED, RUNNING IN BACKGROUND** for
  the same box-contention reason. Launched with `CC` unset (the plain
  `make test` condition the triage's own §2/§5 cared about):
  `nohup bash -c 'timeout 1800 bash tests/anchored/run_anchored_diff.sh' >
  /tmp/portfix_anchored_diff.log 2>&1 &`, background pid `69927`.
  **Expected**: 7 passed / 0 failed (matching `anchtriage_report.md` §2's
  rxtnul numbers under `CC=gcc-16`) now that clang is no longer forced
  down a red path by `cc_resolve.sh`'s own resolution to `gcc-16` on this
  box AND (independently, per this lane's own fix) the emitted C is
  clean under clang too. A fresh agent or the manager should tail
  `/tmp/portfix_anchored_diff.log` for its `checks passed`/`checks failed`
  line.
- **Full `make test`**: deliberately NOT run (the brief's box constraint;
  the manager runs it at merge).

## 6. Rulings received

None — no mid-flight questions arose; the charter's disposition (a) and the
BOILERPLATE's abi ritual were sufficient to execute the brief without a
ruling.

## Summary for the manager

Fix is mechanical, landed, and independently re-measured before/after on
all six named witnesses (clang error -> clean, gcc unaffected). The abi
ritual is complete except the (B) `FILEPIN` value itself, which is
deliberately owed per house precedent. `make strict` is green.
`make test-codegen` and `tests/anchored/run_anchored_diff.sh` (CC unset)
are both running in the background under box contention from the
concurrent battery and their pass/fail trailers are owed — log paths above.
Nothing else is outstanding. Branch parks on `lane/portfix`; do not merge.
