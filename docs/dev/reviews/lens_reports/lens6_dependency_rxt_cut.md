# Lens 6 — organization / dependency hierarchy / the rxt cut

Lane `lens6dep` (opus, read-only to `src/`/`cli/`/`lib/`/`tests/`), 2026-09-17.
Charter: `docs/dev/reviews/code_review_criteria_draft.md` lens 6 (Frank #6),
RATIFIED with addenda A1-A5. Base: `main` at `7d444f9e`.
Metric artifacts cited as `tools/review/out/...` (read from
`worktrees/revtools/tools/review/out/`), generated at `998af066` /
`1edd6c5e`.

Everything below that carries a number was measured in this worktree. The
build used for the link experiment is the charter's one permitted
`make -j4 CC=gcc-16`; no suite was run.

---

## 0. Summary — six findings, ranked

| # | Finding | Severity | Effort | Blast radius |
|---|---|---|---|---|
| **R1** | **The rxt cut FAILS today.** A matcher-only consumer links all three rxt objects; the drag is exactly ONE symbol from ONE call site. | MAINTAINABILITY | LOCAL | 2 files, 0 checks |
| **L1** | `src/gen/enc/` is misfiled. All 6 include back-edges are this one directory, and every one of them reads only the seam's DATA half — never its emission half. | MAINTAINABILITY | LOCAL | ~12 source files, 34 doc/check citations, 6 sabotage `SAB_FILE` rows |
| **L2** | **The include graph understates cross-layer coupling by 6.5x.** 6 include back-edges; 39 call-level back-edge references, 33 of which no include edge can see, because `core/internal.h` declares them all. | MAINTAINABILITY | (diagnosis; no move proposed) | — |
| **L3** | `core/` is TWO layers wearing one name: the shared bottom (types, arena, sb) and the pipeline DRIVER, which sits above `gen/`. 20 of L2's 39 back-edges are this one conflation. | MAINTAINABILITY | DESIGN-EVENT | naming/layer-model only, or a file move |
| **L4** | The four `*_dump.c` CLI surfaces (2,773 lines) live in `src/parse/` and reach into `src/gen/` and `src/opt/`. They are already link-clean; only the filing is wrong. | POLISH | MECHANICAL | 4 files, Makefile wildcard already covers |
| **L5** | `src/core/internal.h` IS a god-header: 5,522 lines, 225 function declarations of which **32 (14.2%) are defined in `src/core/`**; included by 52 of the tree's ~55 `.c` files; #2 churn hotspot at 171 touches. | MAINTAINABILITY | CROSS-CUTTING | 52 TUs recompile per touch; 1 sabotage anchor |

Nothing here is CORRECTNESS-RISK. The tree's layering is *sound* — no
cycle miscompiles anything — and the two genuinely load-bearing rulings
(D58/DD-12 (7)'s sealed backends; `limits.def` as the config home) are
untouched by every proposal below. What is wrong is that the **stated**
architecture (`APPROACH.md`'s `core → parse → ir → opt → gen` pipeline,
restated in `src/CLAUDE.md`) and the **linkable** architecture disagree,
and the instrument the review started from (the include graph) cannot see
the disagreement.

---

## 1. THE RXT CUT — the verified deliverable

### 1.1 The question, and the answer

> Can a matcher-only consumer link `build/libpcrec.a` without
> `rxt_source`/`rxt_compose`/`rxt_schema` objects today?

**NO.** All three are pulled into a consumer that does nothing but
`pcrec_default_options` → `pcrec_compile` → `pcrec_output_free`, and the
whole drag is a single symbol reference.

### 1.2 The experiment — transcript

The consumer is `docs/spec/match_api.md` §8.0's calling sequence, kept to
the three functions `lib/pcrec.h` actually exports (`pcrec_default_options`,
`pcrec_compile`, `pcrec_output_free` — the header declares no others):

```c
#include <stdio.h>
#include <string.h>
#include "pcrec.h"

int main(void)
{
    pcrec_options opt;  pcrec_output out;  pcrec_error err;
    pcrec_default_options(&opt);
    opt.header_name = NULL;                 /* self-contained .c */
    if (pcrec_compile("a(b|c)+d", &opt, &out, &err) != 0) {
        fprintf(stderr, "pcrec: %s (at byte %zu)\n", err.msg, err.pos);
        return 1;
    }
    printf("emitted %zu bytes of C\n", strlen(out.c_src));
    pcrec_output_free(&out);
    return 0;
}
```

**Arm 1 — link against the archive as built, with a link map:**

```
$ gcc-16 -O2 -Wall -Wextra -Werror -I<w>/lib -o consumer consumer.c \
      <w>/build/libpcrec.a -Wl,-map,map.txt
$ ./consumer
emitted 47649 bytes of C
$ grep -oE 'libpcrec\.a\(([a-z_0-9]+\.o)\)' map.txt | sort -u | wc -l
44
```

**44 of the archive's 48 members are selected**, and the four absentees are
exactly the four `*_dump.o`:

```
$ comm -23 <(ar t libpcrec.a | grep -v SYMDEF | sort) <(pulled members, sorted)
axes_dump.o
limits_dump.o
schema_dump.o
syntax_dump.o
```

(see L4 — the dump tier is already link-clean, and that is the contrast
that makes R1 worth fixing.) **`rxt_compose.o`, `rxt_schema.o` and
`rxt_source.o` are all three in the pulled set.**

**Arm 2 — delete the rxt objects from a copy of the archive and relink:**

```
$ cp <w>/build/libpcrec.a libpcrec_cut.a
$ ar d libpcrec_cut.a rxt_source.o rxt_compose.o rxt_schema.o schema_dump.o
$ gcc-16 -O2 -I<w>/lib -o consumer_cut consumer.c libpcrec_cut.a
Undefined symbols for architecture arm64:
  "_pcrec_rxt_compose", referenced from:
      _compile_driver in libpcrec_cut.a[3](compile.o)
ld: symbol(s) not found for architecture arm64
```

**ONE undefined symbol.** The whole rxt tier hangs off it.
(`schema_dump.o` was deleted in the same `ar d` for symmetry with the
dump-tier question; it produced no undefined symbol, which is arm 1's
"already link-clean" result confirmed from the other direction.)

**Arm 3 — the undefined-symbol chain** (`nm -u` on the three objects,
filtered to rxt/schema names):

```
rxt_compose.o  →  _pcrec_rxt_prefix_from_name                 (in rxt_source.o)
rxt_source.o   →  _pcrec_rxt_schema_{row,rows,nrows,opener,
                   child_scope,group_scope,open_subtree,
                   prose_region}, _pcrec_rxt_constraint_next,
                   _pcrec_rxt_scope_{name,noun,context},
                   _pcrec_rxt_value_name                      (in rxt_schema.o)
rxt_schema.o   →  (nothing in the tier)
```

So the chain is a clean three-link ladder:

```
core/compile.o :: compile_driver
      └─ pcrec_rxt_compose            (parse/rxt_compose.c:718)
             └─ pcrec_rxt_prefix_from_name   (parse/rxt_source.c)
                    └─ 13 schema accessors    (parse/rxt_schema.c)
```

`pcrec_rxt_prefix_from_name` is [DD-13b.W23]'s derived-identifier lookup
(`w233_report.md` §2.22, `w23design_report.md`'s §4.5-item-4 repair) — the
composer asks `rxt_source.c` to turn a target name into a symbol prefix,
and that file's own `#include` of the schema drags `rxt_schema.o` behind it.

**Arm 4 — verify the cut works and is answer-identical.** A stub standing
in for the minimal cut of §1.4:

```c
#include "core/internal.h"
Ast *pcrec_rxt_compose(Ctx *cx, Ast *root) { (void)cx; return root; }
```

```
$ gcc-16 -O2 -I<w>/lib -o consumer_cut consumer.c stub.o libpcrec_cut.a
$ ./consumer_cut
emitted 47649 bytes of C      # byte-identical to arm 1
```

The stub is legitimate *because the composer already early-returns*:
`src/core/compile.c:715-724` states it, in the tree's own words —
`cx.defs` is *"NULL on every entry but `pcrec_compile_defs`, so
`pcrec_rxt_compose` below is one pointer test and every artifact a
non-`--source` compile emits is byte-identical to before the composer
existed."* The design intent is already "inert on the matcher path"; only
the **link graph** does not reflect it.

### 1.3 What the cut is actually worth — and the correction it forces

The naive framing ("the cut saves the rxt tier's 365 KB of object code")
is wrong, and measuring four arms rather than two is what shows it.
`-dead_strip` (ld64's equivalent of `--gc-sections`) is available with **no
source change at all**:

| arm | source change | `-dead_strip` | file bytes | `__text` | `__cstring` | rxt syms |
|---|---|---|---|---|---|---|
| baseline (how the Makefile links today) | — | no | 767,528 | 243,964 | 152,989 | **32** |
| dead-strip only | — | yes | 687,480 | 199,996 | 141,365 | **2** |
| source cut only | yes | no | 694,784 | 199,516 | 140,909 | **0** |
| source cut + dead-strip | yes | yes | 688,512 | 194,428 | 140,261 | **0** |

Read the table this way:

1. **The three rxt objects contribute 44,448 bytes of `__text`
   (18.2% of the matcher-only binary's code) and 12,080 bytes of
   `__cstring` today**, because nothing strips them (baseline − source-cut).
2. **`-dead_strip` alone recovers 43,968 of those 44,448 bytes** with no
   source change, leaving **480 bytes and exactly two live symbols**:
   ```
   $ nm consumer_ds | grep -i rxt
   000000010000ccc0 T _pcrec_rxt_compose
   000000010000db4c T _pcrec_rxt_prefix_from_name
   ```
   The 13 schema accessors and all 4,037 lines of the `.rxt` parser are
   unreachable from the composer's early-return path and vanish.
3. **The source cut's marginal size win over a link flag is therefore
   ~480 bytes of code and two symbols — not 365 KB.**

So the honest verdict is a split one, and I am stating it against my own
lens's interest:

> **The rxt cut's SIZE case is already discharged by a link flag nobody
> has to be told about.** What the source cut buys that `-dead_strip`
> cannot is (a) **archive-member selection** — the three objects are
> *selected* into the link regardless of stripping, which is what an SBOM,
> an attack-surface audit, a `--whole-archive` consumer, or a shared-library
> build with default visibility actually sees; (b) **dependency honesty** —
> today `core/` statically references `parse/`'s newest and largest
> subsystem on the path every consumer takes; and (c) **a real
> `-Werror`-grade guarantee** rather than an optimisation the consumer may
> or may not enable.

This also produces the cheapest possible interim recommendation, which is
not a refactor at all: **`docs/spec/match_api.md` §8.0's worked example
should link with `-Wl,-dead_strip` (or `-Wl,--gc-sections` on GNU ld) and
say why.** That is a doc hunk, MECHANICAL, and it moves 43,968 bytes for
every consumer who copies the example — which is the whole point of a
worked example. (D80: a caller-observable recommendation carries its spec
hunk; this is that hunk.)

### 1.4 The minimal cut

The reference must be removable at LINK time, so a runtime `if
(cx.defs)` around the call does not help — a static call reference exists
whether or not it is taken. Three facts make the cut small:

- `pcrec_compile_defs` (the only entry that ever sets `cx.defs`) is
  declared at `src/core/internal.h:4913` and has **exactly one caller in
  the whole tree**: `cli/main.c:1196`.
- `pcrec_compile_defs` and `pcrec_compile` are defined in the SAME object
  (`nm -g build/obj/core/compile.o`: both `T` in `compile.o`), which is
  why the linker cannot separate them.
- The composer's *position* in the pipeline is ruled (`[DD-13b.W1.3]`,
  `w1_impl` §2.1: after `pcrec_parse`, before `pcrec_callgraph_build`,
  before `pcrec_altcls`) — and none of the proposals below moves it.

**THE CUT (smallest form):** give `compile_driver` an optional composer
hook and move the `--source` entry into its own translation unit.

1. `compile_driver` takes (or `Ctx` carries) one added field,
   `Ast *(*compose)(Ctx *, Ast *)`, and line 1157 becomes
   `if (cx.compose) root = cx.compose(&cx, root);` at the identical
   position. The `cx.ncap_primary = cx.ncap;` seed on line 1156 stays
   where it is — its own comment says it is seeded outside the composer
   precisely so it is right on every compile.
2. `pcrec_compile` leaves the hook NULL. `compile.o` then names no rxt
   symbol.
3. `pcrec_compile_defs` moves to a new TU (`src/core/compile_defs.c`, ~15
   lines: it is a thin wrapper today) which sets the hook to
   `pcrec_rxt_compose`. Only *that* object names the rxt tier, and only
   `cli/main.c` pulls it.

Blast radius: **2 files edited, 1 file added, 0 emitted bytes moved** (the
composer runs at the same point on the same inputs; a non-`--source`
compile already took the early return). Not an `abi` event — nothing in
the emitted scaffolding changes, so D76/D94 do not fire. The `-Werror`
requirement on the new TU is ordinary.

**The one-line alternative, rejected:** make `pcrec_rxt_compose` a weak
symbol. It removes the undefined-symbol error without removing the archive
member, does not work portably (ld64 vs GNU ld differ), and replaces a
structural fact with a linker trick — the shape
`pcrec-general-mechanisms-not-special-cases` and D77 both argue against.

### 1.5 Check-coupling for the cut (A3)

Population by grep, not by judgement:

```
$ grep -rn "rxt_compose" tests/                    →  0 hits
$ grep -rn 'SAB_FILE="src/core/compile.c"' tests/mech/sabotages/  →  10 rows
      S166 S169 S178 S189 S191 S192 S193 S237 S252 S253
```

**Zero checks anchor on the composer call or on `rxt_compose.c` at all.**
The ten `compile.c` sabotage rows anchor on the *drop ladder*, the
*size-term bar*, *callgraph binding order*, *postresolve*, *root discharge*
and the *premul drop rung* — every one of them elsewhere in the file. Two
are worth naming because they sit nearest the edit:

- **S166 `callgraph_binds_early`** anchors the ordering constraint the
  composer's own comment cites in the opposite direction (the composer
  must run *before* `pcrec_callgraph_build`). A cut that keeps the call
  site's position leaves S166 intact; a cut that moves it does not.
- **S178 `root_discharge_dropped`** anchors on `root = ...` assignment
  publication a few lines below. Anchors are copied from
  `git show HEAD:<path>` per BOILERPLATE; a re-anchor here is line-shift
  only, and only if the wave's diff perturbs its context window.

So the cut's re-aim burden is: **nothing on the sabotage side, nothing on
the codegen side, and one `src/core/CLAUDE.md` file-list line** for the new
TU (the Conventions rule: update the owning directory's CLAUDE.md on a file
add).

### 1.6 A1 — the ruled record

No D-row or plan row rules that `pcrec_compile` and `pcrec_compile_defs`
share a translation unit, nor that the composer is called unconditionally.
`[DD-13b.W1.3]` rules the composer's POSITION (preserved) and
`w13_report.md` §1/D89 rule its group-numbering behaviour (untouched). The
tree's own comment at `compile.c:715-724` states the inertness property the
cut makes structural. **The cut contradicts no ruled record.**

---

## 2. LAYERING

### 2.1 L1 — `src/gen/enc/` is misfiled

`tools/review/out/include_backedges.tsv` (6 rows, all of them):

```
src/core/compile.c      :14   gen/enc/enc.h   core  → gen
src/ir/dfa.c            :111  gen/enc/enc.h   ir    → gen
src/ir/nfa.c            :35   gen/enc/enc.h   ir    → gen
src/opt/lower_enc.c     :134  gen/enc/enc.h   opt   → gen
src/parse/parse.c       :36   gen/enc/enc.h   parse → gen
src/parse/rxt_compose.c :75   gen/enc/enc.h   parse → gen
```

`tools/review/out/include_layer_matrix.tsv` confirms the shape: `core→gen`
1, `parse→gen` 2, `ir→gen` 2, `opt→gen` 1, and **every other below-diagonal
cell is 0**.

**The judgement the charter asks for: `enc/` is misplaced, not the
includes.** The evidence is that the six back-edges and the emitter read
*disjoint halves of one struct*. Measured — every consumer's lookup site
and the fields it reads:

| file:line | layer | reads from `PcrecEnc` |
|---|---|---|
| `core/compile.c:1122` | core | `pcrec_enc_by_id`, `pcrec_enc_ready`, `->name`, `pcrec_enc_names` (the `-e utf8` refusal) |
| `parse/parse.c:395,713` | parse | `->max_cp` (complement universe), `->fold` (`cls_casefold`), `->name` |
| `parse/rxt_compose.c:471` | parse | `->name` (a composed target's declared-encoding check) |
| `ir/nfa.c:1089` | ir | `->start_cls` ×4 (the K50 gate) |
| `ir/dfa.c:1312` | ir | `->start_cls`, `pcrec_enc_start_cls_ok`, `->name` |
| `opt/lower_enc.c:615` | opt | `->max_cp` ×5 |
| `gen/emit_dfa.c` | gen | `->advance` ×5, `->start_guard`, `pcrec_enc_start_guard`, `pcrec_enc_emit_decls/defs`, `PCREC_ENCE_NEXT_POS` |
| `gen/emit_vm.c` | gen | `PCREC_ENCE_BREF{,_CASELESS}`, `PCREC_ENCE_BACK_STEP`, `pcrec_enc_advance`, `pcrec_enc_entry_engine_callable` |

**Not one of the six back-edges touches a text field** (`entries`,
`decls`, `defs`, `advance`, `start_guard`). The split is exact:

- **the DATA half** — `id`, `name`, `max_cp`, `fold`, `start_cls`, plus
  the lookups and `pcrec_enc_start_cls_ok` — is read by core, parse, ir
  and opt. It is a *registry of facts about an encoding*.
- **the TEXT half** — `entries`, `advance`, `start_guard`, and the three
  emit functions — is read by `gen/` alone. It is *residual text an
  artifact embeds*.

And the history explains why the filing drifted rather than being wrong
from the start. The seam was chartered as emission-only — `[M5-SEAM]`
(plan_completed.md:2591) scopes it as *"the DD-12 residual-header embed
mechanism"*, which is purely `gen/` work. The data half arrived later, in
four separately-recorded seam events, each of which `src/gen/enc/CLAUDE.md`
dutifully logs as *"`PcrecEnc` GAINED A SCALAR … a D58 SEAM EVENT"*:
`max_cp` ([M5.0] stage 1, read by `parse`), `fold` (stage 4, read by
`parse`), `advance` ([K49], `gen`), `start_cls`/`start_guard` ([K50], read
by `ir`). **Three of the four added a reader OUTSIDE `gen/`, and the
directory's filing was never revisited.** D58's own revisit clause asked
for interface changes to be recorded against the entry — they were, one at
a time, and no one summed them.

**Proposal (LOCAL):** move `src/gen/enc/` → `src/enc/`, and insert `enc`
into the layer model between `core` and `parse`:
`lib → core → enc → parse → ir → opt → gen → cli`. That is the correct
position by construction — `enc.h`'s only core dependency is `StrBuf` and
`PcrecFold` from `core/internal.h` (`enc.h:35`, the header's own comment
says so), and `enc_byte.c`/`enc_utf8.c`/`enc.c` include nothing but
`gen/enc/enc.h`, `<string.h>` and a generated `.inc`. **The move takes all
six back-edges to zero with no code change at all — only `#include`
spellings.**

**A1 check.** No D-row and no plan row names the directory PATH: `grep -rn
"src/gen/enc" docs/dev/decisions.md` returns **nothing**. D58 and DD-12 (7)
rule the seam's *semantics* — sealed backends, no encoding conditionals,
the third-encoding recipe — none of which a move touches. But the move
**does** falsify two prose sentences that must travel in the same change,
and they are the ones a future backend author reads:

- `src/gen/enc/enc.h:27-31` — *"Nothing in src/core, src/gen, cli/ or
  lib/ is touched"* in the third-encoding recipe.
- `src/gen/enc/CLAUDE.md` — the same recipe, spelled *"`src/gen` outside
  this directory"*.

Both become simpler after the move (the directory is no longer *inside*
`src/gen`), which is a small argument in the move's favour: the recipe
currently has to carve an exception out of its own parent.

**A note the move does NOT fix, recorded because it is the deeper half.**
`enc.o` calls `pcrec_cls_newline` and `pcrec_cls_word_esc`, both defined in
`parse/mod_classes.o` (see §2.2's detail table) — an `enc → parse` call
edge that survives any relocation. That is [K50]'s `UPC_NOSTART`
disjointness check reaching for the D64 newline and word-byte definitions,
which live in a feature module. It is a genuine layering question (a
*definition of a byte class* arguably belongs below both), and I am filing
it as an observation rather than a proposal because fixing it means moving
class definitions out of a module, which is module-architecture territory
this lens has no mandate over.

**Check-coupling for the enc move (A3).** `grep -rn "gen/enc" tests/
scripts/ Makefile` → **34 citation sites**. Load-bearing (a move breaks
them):

| kind | sites |
|---|---|
| sabotage `SAB_FILE=` | **6**: `S-U5`, `S-U6`, `S-U9`, `S116`, `S229`, `S233` (all `enc_byte.c`/`enc_utf8.c`) |
| test C `#include "gen/enc/enc.h"` | **2**: `tests/utf8/startbnd_backend_check.c:52`, `tests/mrl/cwmax_check.c:121` |
| structural greps on a path | **4**: `tests/codegen/run_cpset_structure.sh:153,271,395,412` |
| Makefile | **2**: `:110` (source wildcard), `:157` (`utf8_fold_pairs.inc` prerequisite) |
| prose/`SAB_DOC_FIGURE` citations | **20** (cosmetic, but a stale path in a sabotage's doc figure is the class `w23implfix_report.md` calls citation-provenance rot) |

Six scripts carry a comment reading *"the source list is FOUND, not
globbed at a fixed depth — `src/gen/enc/` is two levels deep"*
(`run_endvar_identity.sh:73`, `run_trie_identity.sh:81`,
`run_wordctx_identity.sh:73`, `run_mlinectx_identity.sh:94`,
`run_gstart_identity.sh:80`, `tests/thread/run_thread_tests.sh:160`).
Those were written to survive exactly this; **the code survives and the
comments go stale** — they must be edited in the same change or the next
reader trusts a sentence about a directory that no longer exists.

### 2.2 L2 — the include graph understates coupling by 6.5x

This is the lens's methodological finding, and it qualifies every number
in §2.1.

I built the **call-level** layer matrix the way the include graph cannot:
`nm -g` over all 47 objects for definitions, `nm -u` for references, joined
on symbol, bucketed by the defining object's directory (with `gen/enc` split
out as its own `enc` tier to match §2.1's proposal).

```
CALL-LEVEL cross-layer edges (rows = caller layer, cols = callee layer)
from\to   core   enc  parse    ir    opt    gen
core         0     2      3     4      8      3
enc          4     0      2     0      0      0
parse       42     2      0     0      6     10
ir           7     3      2     0      1      0
opt         27     1      4     0      0      0
gen         14     7      6     0     15      0
```

**39 back-edge symbol references** (earlier layer → later layer), against
the include graph's **6**:

```
parse → gen : 10      core → gen   : 3      enc → parse : 2
core  → opt :  8      core → parse : 3      ir  → opt   : 1
parse → opt :  6      core → enc   : 2
core  → ir  :  4
```

Only the 8 references in the `→ enc` column correspond to the include
graph's 6 rows. **The other 31 are invisible to any include-based
instrument**, and the reason is a single file: `src/core/internal.h`
declares every one of them, and 52 of the tree's ~55 `.c` files include it,
so a cross-layer *call* generates no cross-layer *include*.

The full detail, since A5 asks for rows rather than a claim:

| caller object | symbol | defining object |
|---|---|---|
| `core/compile.o` | `nfa_has_bot`, `nfa_wrap_unanchored`, `pcrec_build_nfa` | `ir/nfa.o` |
| `core/compile.o` | `pcrec_build_dfa` | `ir/dfa.o` |
| `core/compile.o` | `pcrec_altcls` | `opt/altcls.o` |
| `core/compile.o` | `pcrec_callgraph_build` | `opt/callgraph.o` |
| `core/compile.o` | `pcrec_discharge_atomic` | `opt/atomic.o` |
| `core/compile.o` | `pcrec_lower_enc` | `opt/lower_enc.o` |
| `core/compile.o` | `pcrec_minimize_dfa` | `opt/minimize.o` |
| `core/compile.o` | `pcrec_postresolve` | `opt/postresolve.o` |
| `core/compile.o` | `pcrec_scanedge_dfa` | `opt/scanedge.o` |
| `core/compile.o` | `pcrec_select_engine` | `opt/select_engine.o` |
| `core/compile.o` | `pcrec_emit_dfa`, `pcrec_dfa_scan_state_written` | `gen/emit_dfa.o` |
| `core/compile.o` | `pcrec_emit_vm` | `gen/emit_vm.o` |
| `core/compile.o` | `pcrec_enc_by_id`, `pcrec_enc_names` | `gen/enc/enc.o` |
| `core/compile.o` | `pcrec_parse`, `pcrec_parse_mods_init` | `parse/parse.o` |
| `core/compile.o` | **`pcrec_rxt_compose`** | `parse/rxt_compose.o` ← **R1** |
| `gen/enc/enc.o` | `pcrec_cls_newline`, `pcrec_cls_word_esc` | `parse/mod_classes.o` |
| `ir/nfa.o` | `pcrec_callgraph_ntargets` | `opt/callgraph.o` |
| `parse/axes_dump.o` | `pcrec_dfa_axis_*_cands` ×10 | `gen/emit_dfa.o` ← **L4** |
| `parse/mod_backrefs.o` | `pcrec_bref_mark` | `opt/atomic.o` |
| `parse/mod_lookaround.o` | `pcrec_cwmax`, `pcrec_cwmin`, `pcrec_has_call` | `opt/mrl.o`, `opt/atomic.o` |
| `parse/parse.o` | `pcrec_pat_char` | `opt/lower_enc.o` |
| `parse/syntax_dump.o` | `pcrec_ast_stamped_by` | `opt/atomic.o` ← **L4** |

**The transferable form**, and the reason this belongs in the synthesis
rather than only in this report: *an include graph measures what a file
had to be TOLD to see; when one header tells everybody everything, it
measures nothing.* The review's own metric artifact
(`include_backedges.tsv`, 6 rows) reads as a near-clean bill of health, and
the tree has 39. This is `pcrec-check-design-lessons`' shape — **a control
sharing a source with what it controls** — at the instrument level: the
instrument and the architecture both route through `internal.h`, so the
instrument cannot see `internal.h`'s effect.

**No move is proposed for L2.** It is a diagnosis, and its two actionable
consequences are L3 and L5 below.

### 2.3 L3 — `core/` is two layers wearing one name

Twenty of the 39 back-edges are `core/compile.o` alone, and **they are not
a defect** — they are the pipeline driver calling each stage in order,
which is exactly what `src/CLAUDE.md` says `compile.c` is
(*"pipeline driver is `pcrec_compile()` in core/compile.c"*). The defect is
in the **layer model**, which files the driver in the bottom layer.

`src/core/` holds two unrelated things:

- **a bottom tier** — `arena.c`, `sb.c`, `cpset.c`, `fold.c`, `tune.c`,
  and the type definitions in `internal.h`. Everything depends on it; it
  depends on nothing. Correctly placed.
- **a top tier** — `compile.c` (1,892 lines), the driver, which by
  definition sits ABOVE `gen/`. Every one of its 20 "back-edges" is a
  forward edge once it is filed at the top.

Filing them together is what makes `core → gen` read as a violation when
it is the pipeline working. The cheapest fix is **not a file move**: it is
to teach `tools/review/include_graph.py` (and `src/CLAUDE.md`'s prose) that
the order is `core(base) → enc → parse → ir → opt → gen → driver → cli`,
with `compile.c` in `driver`. That reclassifies 20 of 39 back-edges as
forward edges *truthfully*, and leaves a residue of 19 that are worth
looking at — which is the number a refactor wave should actually be aimed
at.

If a file move is wanted later, `src/core/compile.c` → `src/driver/compile.c`
is mechanical; its cost is the 10 sabotage `SAB_FILE="src/core/compile.c"`
rows listed in §1.5 plus whatever greps a path. I am **not** proposing it:
D77 says wait for a measured need, and the measured need here is served by
fixing the model, which costs a tool constant and a paragraph.

### 2.4 L4 — the dump tier is filed under `parse/`

Four files in `src/parse/` are not parser code:

| file | lines | what it is |
|---|---|---|
| `src/parse/syntax_dump.c` | 1,770 | `--list-syntax`, `--explain`, `--probe-ask` |
| `src/parse/axes_dump.c` | 731 | `--list-axes` |
| `src/parse/schema_dump.c` | 183 | `--list-schema` |
| `src/parse/limits_dump.c` | 89 | `--list-limits` |
| **total** | **2,773** | |

They are CLI registry-dump surfaces. Their symbols
(`pcrec_syntax_tsv`, `pcrec_axes_tsv`, `pcrec_limits_tsv`,
`pcrec_rxt_schema_tsv`, `pcrec_probe_ask`, `pcrec_definitions_tsv`,
`pcrec_syntax_explain`, `pcrec_syntax_families`, `pcrec_syntax_verbs`,
`pcrec_construct_built_status`, `pcrec_flavour_by_name`) are named by
`cli/main.c` and by nothing else in `src/`. Filing them under `parse/` is
what produces the largest single `parse → gen` cell in §2.2's matrix
(`axes_dump.o` reaching 10 `pcrec_dfa_axis_*_cands` enumerators inside
`gen/emit_dfa.c`) and one `parse → opt` edge (`syntax_dump.o` →
`pcrec_ast_stamped_by`).

**They are already link-clean** — this is the contrast that makes R1 worth
fixing. All four `*_dump.o` are the ONLY archive members a matcher-only
consumer does not select (§1.2, arm 1), for a structural reason: no
`src/` object names them, so nothing but `cli/main.c` can pull them in.
**That is the property R1 asks for the rxt tier, achieved by construction
rather than by care**, and the mechanism is identical — the tier's entries
are named only from the surface that needs them.

**Proposal (MECHANICAL, POLISH):** move the four to `src/dump/` (or
`cli/dump/`) and give it its own tier at the top of the layer order beside
the driver. The Makefile already globs per directory; a new directory needs
one wildcard line and its own `CLAUDE.md` per Conventions. Blast radius:
4 files, 1 Makefile line, 1 new CLAUDE.md, plus `src/parse/CLAUDE.md`'s
file list. Check-coupling: `grep -rn "syntax_dump\.c\|axes_dump\.c" tests/`
should be run by the wave (not run here — it is outside the enc/rxt
populations this lane priced).

---

## 3. L5 — header hygiene: `internal.h` IS a god-header

The census the charter asked for, measured rather than asserted. Method:
strip block and line comments from `src/core/internal.h` (5,522 lines,
overwhelmingly prose), take every top-level declaration ending `);`, join
each name against the `nm -g` definition table:

```
internal.h FUNCTION DECLARATIONS (comments stripped): 225 distinct
by defining layer:
  parse  122      (54.2%)
  opt     38      (16.9%)
  core    32      (14.2%)   ← the only ones this header's DIRECTORY owns
  gen     28      (12.4%)
  ir       5       (2.2%)
  unresolved: 0
```

**32 of 225 (14.2%) of the declarations in `src/core/internal.h` are
defined in `src/core/`.** The top defining objects are
`gen/emit_dfa.o` (27), `parse/rxt_schema.o` (19), `parse/parse.o` (13),
`core/cpset.o` (12), `parse/registry.o` (12), `parse/definitions.o` (11),
`opt/atomic.o` (10).

Scale and cost:

- **5,522 lines**, included by **52** of the tree's ~55 `.c` files.
- `tools/review/out/churn_hotspots.tsv` row 2: **171 touches, 7,380 total
  churn, hotspot score 944,262** — #2 behind `emit_vm.c` and ahead of
  `emit_dfa.c`. Every one of those 171 touches invalidates all 52 TUs.
- It is simultaneously the reason L2's 31 hidden back-edges are hidden.

**The finding is NOT "split it into 6 headers."** That is the shape lens 11's
own anti-perversion clause warns about, and this header earns much of its
length honestly: a large share of those 5,522 lines is the tree's densest
*why* documentation (the `UPC_NOSTART` partition argument, the
`cwmin`/`cwmax` polarity rules, the D70 payload contract), which is
genuinely shared and correctly co-located with the types it describes.

The finding is the **split it already implies and does not make**:

> `internal.h` is two documents in one file — the **shared TYPE and
> CONTRACT tier** (`Ctx`, `Ast`, `StrBuf`, `Arena`, `CpSet`, the class-axis
> partition, the D70 payload rules, `ctx_fail`/`ctx_nomem`), which every
> layer legitimately needs, and a **cross-layer FUNCTION DIRECTORY** (193
> declarations of functions defined in four other directories), which is
> the thing that launders the dependency graph.

The second half is what a per-layer header would carry: `parse/parse.h`,
`opt/opt.h`, `gen/gen.h`, `ir/ir.h`. The payoff is not tidiness — it is
that **the include graph would then measure something**, and every finding
in §2 would have been visible to the metric artifact that was supposed to
find it.

**Effort: CROSS-CUTTING, and I am not proposing it for this round.** It
touches 52 TUs, and its check-coupling is a single sabotage row
(`grep -rn 'SAB_FILE=.*internal\.h' tests/mech/sabotages/` → **1**), which
is deceptively cheap — the real cost is 52 `#include` edits and the risk of
moving a comment away from the type it documents. The cheap first step, and
the one I do recommend, is **ordering-only**: group `internal.h`'s
declaration block by defining layer with a header comment per group, so the
193-vs-32 split is visible in the file. That is MECHANICAL, moves no code,
and makes the eventual split a cut rather than a survey.

---

## 4. PROBED-AND-HELD

Negative results with the evidence behind them, so the same ground is not
re-covered.

1. **No include cycle exists.** `include_edges.tsv` (198 rows under its
   header; `include_layer_matrix.tsv`'s header reads `local_edges=94`)
   plus the layer matrix: the only below-diagonal cells are the six
   `→ gen/enc/enc.h` rows. With `enc` filed between `core` and `parse`
   (§2.1) the include DAG is acyclic and strictly ordered. **HELD.**

2. **`lib/pcrec.h` does not leak the rxt tier.** The public header
   declares exactly three functions — `pcrec_default_options`,
   `pcrec_compile`, `pcrec_output_free` (`grep -nE` over 1,072 lines). The
   rxt drag is entirely internal; no consumer can be blamed for it, and
   fixing it breaks no published contract. **HELD.** (`pcrec_compile_defs`
   and `pcrec_emit_ir` are `internal.h` entries reached by `cli/main.c`
   through `-Isrc` — a public-surface observation belonging to lens 9,
   noted here because it is what makes the cut cheap.)

3. **The dump tier needs no cut.** All four `*_dump.o` are already outside
   a matcher-only consumer's link (§1.2). **HELD** — L4 is a filing
   finding, not a linkage one.

4. **`enc.h`'s dependency on `core/internal.h` is not a problem for the
   move.** It reads `StrBuf` and `PcrecFold` only (`enc.h:35`,
   `internal.h:60`, `internal.h:3278`), both bottom-tier types; an `enc`
   tier above `core` keeps that edge forward. **HELD.**

5. **The composer's ruled POSITION is not in tension with the cut.** The
   `[DD-13b.W1.3]` ordering constraints (after `pcrec_parse`, before
   `pcrec_callgraph_build` and `pcrec_altcls`) are satisfied identically by
   a hook call at line 1157. **HELD.**

6. **No sabotage row or codegen check anchors on `rxt_compose`.**
   `grep -rn "rxt_compose" tests/` → 0 hits. **HELD.**

7. **The enc back-edges are not a `PcrecEnc`-is-too-fat problem.** Every
   consumer reads 1-4 fields and each has exactly ONE `pcrec_enc_by_id`
   lookup site (six sites, six files). Splitting the struct would buy
   nothing the directory move does not; splitting the HEADER (data half
   low, text half in `gen/`) is a live alternative to the move but costs a
   second file and an extra seam for a backend author to learn — **not
   recommended**, and recorded so the wave does not re-derive it.

8. **The 44,448-byte figure for the rxt tier's `__text` contribution is
   not the cut's value.** Four-arm measurement (§1.3); the source cut's
   marginal win over `-Wl,-dead_strip` is ~480 bytes and two symbols.
   Stated against the lens's own interest. **HELD.**

---

## 5. What a refactor wave should take, in order

1. **`match_api.md` §8.0 gains `-Wl,-dead_strip`** with the reason.
   MECHANICAL, doc-only, 43,968 bytes for every consumer who copies the
   example. (D80 hunk; no code.)
2. **L4, the dump tier move.** MECHANICAL, no check-coupling found in the
   enc/rxt greps, and it demonstrates the tier pattern R1 wants.
3. **L1, `src/gen/enc/` → `src/enc/`** plus the layer-model row. LOCAL;
   6 sabotage `SAB_FILE` re-aims, 2 test `#include`s, 4 structural greps,
   2 Makefile lines, 6 stale depth comments, 2 recipe sentences.
   Takes `include_backedges.tsv` to zero rows.
4. **R1, the rxt cut.** LOCAL; 2 files edited, 1 added, 0 checks staled,
   0 emitted bytes moved, no `abi` event.
5. **L3, the layer model** (tool constant + `src/CLAUDE.md` prose).
   MECHANICAL; reclassifies 20 of 39 back-edges truthfully and leaves the
   19 that are worth attention.
6. **L5, `internal.h` grouped by defining layer.** MECHANICAL first step;
   the real split is CROSS-CUTTING and belongs to a later round with its
   own 52-TU budget.

Steps 3 and 5 should land together, or `include_backedges.tsv` reads zero
while §2.2's 39 call edges are still unmeasured — which is precisely the
false clean bill this lens was written to catch.
