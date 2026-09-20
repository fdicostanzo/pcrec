# Lane hdrgen — [HDR-1] purpose headers for `src/gen/emit_vm.c` and `src/gen/emit_dfa.c`

Branch `lane/hdrgen`, from main `c007e9d2`. Charter (Frank, 2026-09-20):
"it would be helpful if the functions had a header comment that indicated
their purpose. e.g. from the name, it isn't clear what `vm_ev` is about."

## Population, before and after

Counted with `tools/review/function_census.py` plus the brief's rule: a
function is HEADED iff the nearest non-blank line above its signature closes
a comment that is not a section banner. Banner = a comment block carrying a
run of 4+ dashes/equals whose text is a short region label.

| file | functions | headed before | unheaded before | unheaded after |
|---|---|---|---|---|
| `src/gen/emit_vm.c` | 124 | 98 | 26 | 1 |
| `src/gen/emit_dfa.c` | 204 | 99 | 105 | 1 |
| both | 328 | 197 | 131 | 2 |

**131, not the brief's 137.** The brief quoted the committed census
(`docs/dev/hdr1_census_2026-09-20.txt`: emit_dfa 109, emit_vm 28). That file
records no method, so the 6-function gap is a banner-classification
difference between two independent readings of the same rule, not a missed
population: every function in both files was classified here, and the two
readings I wrote (one line-based, one comment-block-based) agreed at 131.
Every unheaded function now has a header except the two below.

## The two residual rows — a census artifact, NOT an UNCLEAR

`emit_vm.c:779 vm_rolef` and `emit_dfa.c:682 dfa_fragf` are both spelled as a
forward declaration carrying `__attribute__((format(printf, 2, 3)))` followed
immediately by the definition. Each already HAS a full purpose header — it
sits above the declaration — so the nearest non-blank line above the
DEFINITION is that `__attribute__` line and the mechanical rule scores it
unheaded. A second header between the two spellings would be a duplicate of
the one three lines up. Left alone deliberately.

## UNCLEAR list

**Empty.** No function in either file needed a `/* HDR-1 UNCLEAR: ... */`
header. Every one was legible from its body, its neighbouring object
(`DfaRepr`/`DfaPf`/`DfaDir`/`DfaForm`, the slot-layout comment, the `CapOff`
and `VmSnap` typedefs) and its call sites.

## What the headers say

Sized to the function, per `docs/dev/coding_guide.md` §4.2 / L4-C1.

- One line for an axis predicate (`pf_memchr_applies`, `seed_applies`), a
  name builder (`match_entry_name`), a cell derivation (`cell_premul`).
- The three-part form — what it produces, what it reads that is not a
  parameter, the one invariant a caller must not break — for the long ones:
  `unanch_start`, `emit_search_head`, `dfa_form_derive`, `emit_machine_tables`,
  `emit_unanchored`, `emit_header`, `token_premul`, `pcrec_emit_dfa`,
  `vm_alt`, `vm_cap_offsets`, `vm_isl_node`.
- Where emitted C is involved the header says what the GENERATED code will
  DO, since that is the reader's real question (`vm_fail`, `pf_emit_memchr`,
  `dir_rev_bound_accept`, `view_emit_end_and_eol`).
- Text was HOISTED, not composed: the K24 `noclone` argument, the
  `fit.chosen == ENGM_DFA` two-customers rule, the 558-artifact identity-gate
  incident, the `\b`/`\B` lost-match site, the CUT-before-charge ordering,
  and the `vm_isl_node` reallocation hazard all already existed in the body
  or at a neighbouring site.

`vm_ev` — the charter's own example — now reads: appends one event to the
VM's listing stream (label/goto/fail/push/set/cut/note) with its operands and
the same `role` text the emitted `// ...` comment carries, arena-backed and
doubled.

## Anchors touched

**None.** `scripts/m6read_check_sab_anchors.py` after both commits:

```
sabotages checked: 269 (285 anchor sites)
all anchors resolve
```

285/285, the branch-point figure. No sabotage row needed re-aiming.

## Validation

`make -j4 CC=gcc-16` clean; `make strict CC=gcc-16`:

```
strict: whole tree compiles clean with -Werror -Wshadow
```

`python3 scripts/emit_sweep.py --ref c007e9d2` — **OWED**, running in the
background behind the box's one-heavy-suite rule.

The main tree's darwin battery gate (`build/battery_gate_11ff5f51/`) was
still in its `test` stage at 12:58, so the sweep could not start. A waiter
was launched instead (PID 7367 at launch): it polls that gate's
`trailer.log` for `== BATTERY DONE` at one-minute intervals, then runs the
sweep in this worktree.

- log: `worktrees/hdrgen/build/hdrgen_sweep.log`
- completion line to grep for: `== HDRGEN SWEEP DONE rc=`
- `rc=0` is the accept (five streams byte-identical, 0 movers); any other rc
  is a finding and the sweep's own output above that line names the stream.
- the waiter gives up after 4h with `rc=timeout` and the sweep NOT run; if
  that fires, or if the process did not survive the session, the sweep is
  one command from this worktree:
  `python3 scripts/emit_sweep.py --ref c007e9d2`

Nothing about the delivery depends on the sweep's mechanics — it is the
measurement that turns "comments cannot move a byte" from an assumption into
a fact, which is why it is run rather than argued.

## Commits

- `7db51538` emit_vm.c, 25 headers, +114 lines
- `f59259f1` emit_dfa.c, 104 headers, +419 lines

Comments only: no code, no string literal, no emitted text, no declaration
and no blank-line layout inside any function was changed. Not an abi event —
and the byte-neutrality is MEASURED by the sweep, not assumed.
