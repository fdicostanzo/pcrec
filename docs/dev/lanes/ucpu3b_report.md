# ucpu3b — [UCP] U3, the island DFA as a capability route (D134)

Lane ucpu3b (opus), branch `lane/ucpu3b` off main 7d74499bc. Build GO quoted in the brief
(Frank 2026-11-10: "Let's surface these. Go."). Charter: D130, D134, ucp_design.md §0.1 (T3-T6),
§2.3-§3.8, §6 (the U3 row), u3_island_twin.md.

## 0. Build plan

### What exists, measured at the base (7d74499bc)

- `(*UCP)\b\w+\b`, `(*UCP)\bfoo\b`, `(*UCP)\Bx` under `-e utf8 --features all`: REFUSED at parse
  ("UCP \b is not built yet under encoding 'utf8' ... needs [UCP] U3/U4").
- `(*UCP)\w+` under utf8: REFUSED by U1's wide-set rule (930 intervals > `PCREC_UCP_NARROW_MAX_INTERVALS`).
  `\p{Xwd}+` (the same set) compiles today: all-byte DFA, 0.25 s, 612 KB of C.
- `(?<=[\x{100}-\x{2000}])x`: VM hybrid (T3 row 2, the lookaround lowering), as the twin measured.
- The DFA, the NFA and every NFA/DFA reader are byte-level. U2's context-set list and atoms
  (src/ir/dfa.c `ctx_collect`/`ctx_atoms`) are the machinery the island extends.

### The population U3 serves at this build (D134 items 1-2, CONSERVATIVE)

- **Row 1 of T4 (`island-forced`) only**: a machine whose context list holds a set that is not
  byte-expressible. Today that is UCP `\b`/`\B` under utf8 and nothing else reaches it, because:
- **Non-ASCII lookaround contexts stay on the VM.** They HAVE a route (the VM hybrid) and the twin's
  break-even is by TEXT CLASS (x1/x2: island 4-5x faster on ascii/latin1, 1.35-2.8x slower on
  mixed/cjk), which a compile-time row cannot read. The D134 row is built as a T3 row whose predicate
  is FALSE until a measurement rules it (OWED, see §M); "never selected except where the twin already
  proved a win" selects nothing, because no twin win is text-independent.
- Consuming wide sets with no context set (`(*UCP)\w+`, `\p{L}+`) keep the all-byte form (D134 item 1).
  U1's wide-set REFUSAL is lifted (ucp_design.md §6 U3 row: "U1's wide-set refusals lifted for the DFA
  route"): UCP `\w` is `\p{Xwd}` (D130, study §B) and takes `\p{Xwd}`'s routes as they are today.

### Units (each its own commit)

| unit | what | files |
|---|---|---|
| A admission | UCP `\b \B` under utf8 builds `A_CTX` over its cpset (the byte image keeps the ASCII part); the U1 wide-set refusal row lifted; the parse-time refusal moves to SELECTION: a pattern with a non-byte-expressible context set is DFA-only (no VM route until U4), so captures requested or a VM-only construct refuses by name ("needs [UCP] U4") | src/parse/mod_assertions.c, mod_ucp.c, ctxnode.c, src/opt/select_engine.c (one `analyses[]` row), src/core/internal.h |
| B NFA | island mode, decided per pattern from the AST (T4 row 1's fact): `A_WCLASS` lowers to its ASCII part as `N_CLASS` plus one character-level edge `N_WCHAR` over its non-ASCII set; `N_CTX` carries its non-ASCII set; the unanchored wrap consumes a character (or one ill-formed byte, the ⊥ rule) per step; reverse NFA likewise | src/ir/nfa.c, src/core/internal.h |
| C DFA | T4 as a data table; character atoms (the non-ASCII universe refined by every `N_WCHAR` set and every context set, plus ⊥ split by "may start a character"); context atoms extended by the character atoms' projections; one island column table per machine (`Dfa.isl`: target and accept per (state, char atom)); T5 per state (`dead` / `self-loop` / `island`) as data; the non-ASCII byte column carries `PCREC_DFA_ISLAND` on island states. Minimization SKIPS island machines (listed shortcut: correctness first; the design's atom-column minimization is a follow-up) | src/ir/dfa.c, src/opt/dfamemo.c, minimize.c |
| D emission | island tokens above the scan-edge heads in the reserved top range (H5, counted); the island block (decode, vector, accept, target) in the forward unanchored, reverse and anchored walks; seeds and the reverse termination boundary through `back_step` + decode (§3.2); H7 (the NA accept column is 0 on island states and never read as an answer); every optional form that assumes byte-stepping (unroll, landmark walk, kset facts, offset-k, end-window, memfn kit sites, the D164 end mark) DECLINES on an island machine through its own selector's applicability, stamped. ENG_ATTEMPT (patterns with `^ \A \G (?m)^` beside UCP `\b`) declines the island at this build: refused by name, follow-up unit | src/gen/emit_dfa.c, src/opt/scanedge.c, src/core/compile.c |
| E surface | stamps (`RX_DFA_ISLAND`: the T4 row that fired, island state count, char atoms); `--list` of T4/T5; `limits.def` row for the character-atom cap (H4) with T4 `decline` above it; D80 spec hunks: pattern_language.md §7.1¶2, §7.8, §9¶2; cli.md §1.9; limits.md §3.8; match_api.md (the new stamp) | src/gen/stamp_kinds.c, src/core/limits.def, docs/spec/* |
| F tests | tests/ucp/island.rxt (oracle-verified against libpcre2 10.46 UTF\|UCP\|MATCH_INVALID_UTF; the ill-formed matrix of §6: truncated/overlong/surrogate/>U+10FFFF/stray continuation/0xFF × forward, reverse, seed); the twin's 31,168-case correctness set re-run against the real build (studies/u3_island_twin harness pointed at build/pcrec); sabotage rows for §6's five U3 shapes | tests/ucp/, tests/mech/sabotages/ |

### abi

No existing artifact is meant to move: every machine outside T4 row 1 is built exactly as today, and
island artifacts are NEW (previously refused). So the plan is NO abi bump, verified by the identity
gates (recursion identity, codegen identity, `run_wordctx_identity.sh`). If any non-island artifact
moves, that is a defect of this change, not an abi event.

### Sabotage shapes (ucp_design.md §6 U3 row)

The decoder accepting `C0 80`; ⊥ read as a word character; the reverse island skipping a whole
truncated run; an island state given a scan edge (H2); the H7 accept column read on a non-ASCII byte
(structural). Ids from a range checked against main + worktrees + memfn's reserved ranges at the time.

### Measurement card and the OWED measurement (§M)

The island is a new scan method: its card goes in the measurement script in the same change (memory:
a new method adds its card). The D134 row's predicate needs the island-vs-hybrid break-even on the
competing population (non-ASCII lookaround contexts, x1/x2 shapes) by prefilter strength; text class
is not a compile-time fact, so the row can only fire on a compile-time proxy (the prefilter's kind) or
on a caller's declared domain ([FINDINGS] `byte-rate`). That choice is for the ruling after the
measurement; until then the row is false.

### Design question check

None blocks the build. Two choices this plan takes inside the charter, stated so they can be
overruled: (1) the conservative D134 row (false) because text class is not a compile-time fact;
(2) lifting U1's wide-set refusal (ucp_design.md §6 U3 row), which makes `(*UCP)\w+` compile as
`\p{Xwd}+` does today.

## STATE AT HANDOFF (2026-11-10)

### Units done (commits on lane/ucpu3b)

| commit | unit |
|---|---|
| 2ad63a918 | step 0: this plan |
| 1063f86d2 | B+C: island NFA (`N_WCHAR`, `pcrec_build_nfa_island`, decided by `pcrec_island_needed`) and DFA (character atoms over `iset[]`, `tr[]` = `ncls + nchr` cells, segment table, T5 kinds as data); byte-path readers (kset, width, land_char, span) DECLINE island NFAs (`decline:island-nfa`); the memo keys on `island`; minimization SKIPS island machines |
| f5adcb004 | A+D: admission (UCP `\b`/`\B` under utf8 builds; U1's wide-set refusal lifted, `(*UCP)\w` builds as `\p{Xwd}`), the selection row `island` (last row of `analyses[]`, ENGM_DFA only) with refusals by name where the VM is needed (captures, `\K`, VM lookaround, `--engine=vm`) and for start anchors (ENG_ATTEMPT island not built); emitter: forward walk, reverse walk from the end, retry machine for nullable patterns, LOCATE row `island` first in `cand_rows[]`; `RX_DFA_SCAN "island"` |
| 4089a059f | F: `tests/ucp/island.rxt` + `tests/utf8/island_illformed.rxt` (libpcre2 10.46, 933 cells, harness 933/933); refusals.rxt / reject table / ucp_compare moved; twin set re-run |
| 4155cfb90 | E: spec hunks (cli §1.9¶7, limits §3.8/§3.9¶3a-c, pattern_language §7.1¶2/§7.8¶2, match_api `"island"` value + scan-table row, facts_listing `decline:island-nfa`); limits rows `PCREC_MAX_ISL_SETS`/`_ATOMS`; registry 41->43 checks, 82->84 rows; `PCREC_DFA_ISLAND` on the sentinel allowlist |

### Correctness (measured, local libpcre2 10.46, UTF|UCP|MATCH_INVALID_UTF)

- The twin's correctness set re-run against the REAL build, every twin case (`ucpu3b_evidence/twin_rerun.py`, result `twin_rerun_10.46.tsv`): 9 cases x 31,168 = 280,512 cells, **0 differing**, 0 §9.5 cells. x3/x3b take `"island"`; the seven others keep their all-byte route (D134 item 1, the island never competes).
- Differential (scratch `diff.py`): ~60 patterns x 1,500-1,700 cases (views `$ \z \Z (?m)$`, nullable, lookbehind beside `\b`, caseless, wide/narrow/property sets, ill-formed subjects): 0 differing outside match_api.md §9.5's documented empty-match-beside-ill-formed family, which `(?aW)\b`'s byte machines share.
- Local: `make strict` clean; reject table 669/0 (coverage 290/127/0/115); registry suite rc 0; ucp_compare 42/0 (32 sets compared, 9 wide).

### abi

98, NO bump. Identity probe main vs lane (60 patterns, same output names): 58 same, 2 differ — `(*UCP)\bfoo\b` and `(*UCP)\w+` under utf8, both previously REFUSED (the intended new compiles). No non-island artifact moved.

### Gates queued (OWED; DO-THEN-FINISH)

| job key | what | done line to read |
|---|---|---|
| 430-main-ucpu3b-maketest | make test via perfrun, log `$PCREC_TMPDIR/scratch/ucpu3b/maketest.log` | `scripts/boxqueue state 430-main-ucpu3b-maketest`; `scripts/verdict` on the log |
| 431-main-ucpu3b-axes | make test-axes | `scripts/boxqueue state 431-main-ucpu3b-axes` |
| 432-main-ucpu3b-ubsan | make ubsan (both axes) | `scripts/boxqueue state 432-main-ucpu3b-ubsan` |
| 433-main-ucpu3b-asan | make asan (both axes) | `scripts/boxqueue state 433-main-ucpu3b-asan` |

No `--ready` chain on another key; they run after the full suite in priority order.

### OWED (not built by this lane)

- **D134 row measurement**: island vs VM hybrid break-even by text class and prefilter strength on the COMPETING population (non-ASCII lookaround contexts, twin x1/x2). Not queued: the competing route is not built (those patterns stay on the VM hybrid), so there is nothing to time yet; the row is CONSERVATIVE = the island fires only where no byte form and no other DFA exists (T4 row 1).
- **Measurement card** for the island scan method (memory: a new method adds its card): not written; it is visibly UNMEASURED.
- **mech sabotage rows** (plan §: decoder accepting `C0 80`; ⊥ read as word; reverse skipping a truncated run; H7 accept): not written; no mech job queued for them.
- Follow-ups: T5 fast path (DEAD/SELF/ISLAND kinds computed, unused by the walk); prefilter/skip/scan edges on island machines; minimization of island machines; ENG_ATTEMPT island (start anchors refused by name); captures (U4) and the VM reading wide sets (U4); a dedicated `RX_DFA_ISLAND` stamp was NOT added (the island is read from `RX_DFA_SCAN "island"`; the other DFA stamps take their absence values on it).

### For the kit

Nothing. No memfn/ edit and no kit-side change needed: the island emits its own walk and declines every kit site.
