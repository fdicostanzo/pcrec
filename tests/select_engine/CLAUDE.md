# tests/select_engine — the [M4.7a] SR-8 socket, proven internally

Guards `src/opt/select_engine.c`'s `forces_registry_engines` analysis and the
`Ctx.vmonly_seen`/`vmonly_pos`/`vmonly_why` fields it reads (`src/core/
internal.h`) — the lowering-time mechanism [SR-8]'s flip built for consulting
the registry's `engines` column outside the parser. See `docs/dev/plan.md`'s
`[SR-8]`/`[M4.7a]` rows and `select_engine.c`'s own header for the charter.

## Why this cannot be a `.rxt` corpus or a CLI probe

No pattern reaches the mechanism today. Every `VM_ONLY` registry row
(`src/parse/registry.c`) is gated by a module with no producer — confirmed at
M4.7a by reading every file in `src/parse/` — so nothing the shipped parser
builds ever sets `vmonly_seen`. That is [SR-8]'s own charter statement ("zero
currently-refused constructs become compilable"), not a gap this suite is
covering up: there is genuinely no real construct to write a `.rxt` case for
yet.

So this directory takes `tests/registry/registry_check.c`'s shape instead:
link `build/libpcrec.a`, `#include "core/internal.h"`, and drive the real
functions — `pcrec_parse`, `pcrec_select_engine` — inside one process, with a
hand-built `Ctx` standing in for the producer no module has written. That is
not a weaker check than a `.rxt` corpus would be; it is the only check
available for an internal fact with no external surface yet, the same
argument `tests/registry/CLAUDE.md` makes for its own internal linkage.

## Files

- **`select_engine_check.c`** — three checks against a `Ctx` seeded the way
  `src/core/compile.c`'s `compile_driver` seeds one (same field values, so
  this is not a fabricated shape `select_engine.c` has never seen), parsing
  the real pattern `"abc"` (capture-free, so `forces_captures` is inert and
  the only variable is `vmonly_*`):
  1. **baseline** — `vmonly_seen` left unset (matching every shipped build
     today) leaves engine selection on the DFA, proving the new analysis is
     inert when unpopulated rather than merely asserting it in a comment;
  2. **the socket fires** — stamping `vmonly_seen`/`vmonly_pos`/`vmonly_why`
     exactly as a future producer would forces `ENGM_VM` under `auto`, with
     `why`/`why_pos` threaded through to `EngineFit` unchanged (checked
     against `why_text()`'s exact `"%s at pattern offset %zu"` format);
  3. **the refusal is SHARED, not reinvented** — `--engine=dfa` against a
     `vmonly_seen`-forced pattern hits the identical `ctx_fail` call
     `forces_captures`'s own conflict already uses ("requires the VM engine,
     which --engine=dfa excludes"), naming the socket's own reason text and
     firing at the socket's own position. This is the proof that the two
     analyses genuinely share one refusal mechanism (`pcrec_select_engine`'s
     generic `analyses[]` aggregation loop and the `§5.6` override switch)
     rather than each analysis needing its own diagnostic path.
- **`run_select_engine_tests.sh`** — builds and runs the check, same
  `LIBPCREC`/`SANFLAGS` override shape as
  `tests/registry/run_registry_tests.sh` (so `make ubsan`/`make asan` can
  point it at the sanitizer-built library); carries an exact PASS count (3)
  plus a manifest of the three checks by name, the `tests/registry/` /
  `tests/reject/` convention for making a silently-deleted check visible in
  a diff and FAIL rather than merely show up in one.

Part of `make test` as `make test-select-engine`, and in the `make
ubsan`/`make asan` both-axes batteries alongside `tests/registry/`'s own
entry.

## What this directory does NOT establish

**Not a claim about any real PCRE construct.** There is no backreference,
lookaround, or atomic-group producer to test yet — `vmonly_seen` is stamped
by hand here, standing in for code that does not exist. When the first
VM_ONLY module lands a producer, IT inherits the obligation to prove its own
`vmonly_*` stamping is correct (right row, right position, right engine mask)
against real patterns — this suite only proves the READING half, the socket
itself, works.

Maintenance: update this file when files are added/removed or its role
changes.
