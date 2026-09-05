# [M5.0] STAGE 2 — the UTF-8 backend: lane `utf8s2` report

Branch `lane/utf8s2`, worktree `worktrees/utf8s2`, base `1772fe41`
("journal part 2 (close)"; stage 1 merged at `f22b65c4`). Design of record:
`docs/design/utf8_design.md` — §2 (the lowering), §2.1.2 as corrected by R2
(splice-in-place), §5.2 / §5.2.1 (`back_step`), §5.6 (the width chain), §8.5
(the ASCII differential), §9.2 stage 2 (the acceptance list).

**NOT MERGED, NOT PUSHED.** All commits on `lane/utf8s2`; the manager reviews
and merges. Do NOT run full `make test` on this box (Frank's rule); full
validation is the Linux slot's.

---

## 0. WHAT LANDED, against §9.2's stage-2 list

| §9.2 obligation | status | evidence |
|---|---|---|
| the utf8 backend (four residual bodies incl. `back_step` per §5.2.1) | **DONE** | `src/gen/enc/enc_utf8.c`; `-e utf8` compiles ASCII, α, `\x{3b1}{2}`, wide ranges, 4-byte chars; surrogates rejected as subjects |
| the genuinely-rebuilding byte-sequence lowering at `compile.c:1000`, splice-in-place | **DONE** | `src/opt/lower_enc.c` — a `LowerOps` table, utf8 row does §2.3's decomposition; group-root-address check (`cap_sig`) asserts no `A_CAP` moves |
| `-e utf8` starts compiling; `\x{>FF}` compiles under utf8, refuses under byte | **DONE** | `enc.c` row swapped to `&pcrec_enc_backend_utf8`; `\x{}` is base grammar range-checked per encoding (§2.7.3) |
| the `u.rep.revbody` resolution (413 classes) — loud, never silent | **DONE** | `lower_walk`'s `A_REP` arm clears `revbody` for any body the lowering would change; the 413 ASCII classes are below `identity_max`, so their reverse machines are kept and consistent by IDENTITY — §8.5 exercises them at 0 divergences |
| `pcrec_cwmin`/`pcrec_cwmax` at BOTH timings; `pcrec_maxw` chain RETIRES | **DONE** | `mrl.c` (`pcrec_maxw`→`pcrec_cwmax` chars, `pcrec_cwmin` new), `callgraph.c` third fixpoint, `la_widths` (one function, both timings), `internal.h` memo fields; test side re-aimed (`cwmax_check.c`, `run_mrl_tests.sh §8`, S136/S171 re-pointed, S-U10 new) |
| byte-axis identity gate 100% (expect 14/14) | **PASS 14/14** | `run_encoding_identity.sh`, all four axes, `differing=0 refusal-mismatch=0`; `.abi = 22` unchanged (no bump) |
| the group-root-address check | **DONE** | in the COMPILER (`cap_sig`), stronger than a corpus sweep |
| DD-12(7)(a)'s two M5-time structural checks | **DONE** | `run_encoding_checks.sh` DD12a(i) hot-loop shape identity (object bytes), DD12a(ii) second-backend seam-signature validation |
| §8.5's ASCII differential, 31-block exclusion asserted | **DONE (local slice; full sweep owed to Linux slot)** | `run_encoding_checks.sh §8.5`: 150-block local slice, 0 divergences; census ASCII=2932 excl(subject)=30 (the decode-not-text-scan control) |
| §8.1.1 check 3 (stamp census) as a diff | **DONE** | `run_encoding_checks.sh` CHK3: ASCII utf8 stamps == byte stamps |
| sabotage rows S-U4..S-U10 written and DETECTED | **DONE** | all demonstrated in the failing direction (§3 below) |
| specs in the same change (D80) | **DONE** | `cli.md` (`-e utf8` accepted + ill-formed/startpos contract), `match_api.md §8.2/§3.1`, `registry.md` (`\x{}`) |
| directory CLAUDE.md updates | **DONE** | `src/gen/enc`, `src/opt` (lower_enc/mrl/callgraph), `tests/codegen`, `tests/mrl` |
| NO abi bump (byte axis byte-identical) | **CONFIRMED** | new utf8 artifacts are new outputs; byte artifacts unmoved (`.abi = 22`) |

---

## 1. THE LOWERING, and the two designs the revbody rule ruled out

`pcrec_lower_enc` is a `LowerOps` table selected once by encoding id — one
sealed instance per encoding, no `if (enc == UTF8)` anywhere (DD-12 (7) in the
pass). The utf8 `lower_class` splits each code-point interval at the UTF-8
length boundaries and the surrogate gap, then emits an `A_ALT` of `A_CAT`s of
byte-range classes ([Cox07]/[Ragel]; §2.3) — all existing IR vocabulary, so
`nfa.c`/`emit_vm.c` meet no new node kind.

**Two findings while building it, both recorded at the code:**

1. **An `A_ALT` replacement is sealed in `A_CAT(A_EMPTY, alt)`.** The spliced
   node sits in the leaf's old slot, and a slot at the top of a structure whose
   owner walks its own spine — `vm_look_behind`'s per-branch chain over
   `u.look.nbranch` parse-time branches — would read a bare alternation AS more
   spine. `(?<=[a\x{3b1}])x` compiled to "alternation spine longer than branch
   count" before the wrapper; the two extra epsilon nodes cost nothing and keep
   every enclosing arity what the parse said.

2. **`u.rep.revbody` and lowering do not commute.** The reversed body is
   reversed at the CODE-POINT level; the backward walk reads subject bytes
   right-to-left, so lowering the reversed copy would emit `CE B1` where the
   walk needs `B1 CE`. "Lower revbody too" is a silent wrong-order miscompile,
   not an option. The rule: a body the lowering WOULD CHANGE loses the
   reverse-deterministic rung (`revbody` cleared), decided by
   `subtree_is_identity` on `identity_max`. Under `byte` unreachable; under
   `utf8` the 413 corpus revdet classes are ASCII (kept, consistent by
   identity); only genuinely non-ASCII revdet bodies drop the rung, trading
   throughput for correctness (§2.5.1's decline discipline).

**The group-root-address check (R2's owed stage-2 check) is in the COMPILER,
not the test suite.** `cap_sig` hashes the count and addresses of every `A_CAP`
before and after the pass and `ctx_fail`s if either moves — stronger than a
corpus sweep, and it runs on every compile.

---

## 2. THE WIDTH CHAIN RE-AIMED INTO CHARACTERS

`pcrec_maxw` (bytes) retired; `pcrec_cwmax` (characters) and `pcrec_cwmin` are
the lookbehind width rule's consumers. The `A_CLASS` arm answers exactly 1 in
every encoding (a class is one character by definition), which is what makes
§5.6's whole measured population — `.`, `[^a]`, `\w`, `[a\x{3b1}]`, all
fixed-one-character and variable-byte-width — compile as fixed-width
lookbehinds. `callgraph.c` runs three fixpoints now (`minw` bytes, `cwmin`,
`cwmax`); `la_widths` is one function read at both timings (parse hook +
`postresolve`), so §5.6.4's "both timings move together" is structural.
`internal.h`'s `u.call` fields are `minw` / `cwmin` / `cwmax` / `cwmax_known`.

Test side re-aimed in the same change: `maxw_check.c` → `cwmax_check.c`
(`PCREC_MAXW_SABOTAGE` → `PCREC_CWMAX_SABOTAGE`), `run_mrl_tests.sh §8`,
S136 (prose) and S171 (`S171_cwmax_fixpoint_one_round.sh`, anchors re-pointed to
`cg_cwmax_publish`). `run_mrl_tests.sh` is **27/0** locally.

---

## 3. THE SEVEN SABOTAGE ROWS, all DEMONSTRATED DETECTED

Each applied to the live source (forced rebuild), symptom observed, reverted.

| row | claim | clean → sabotaged |
|---|---|---|
| S-U4 | `pcrec_cwmax`'s A_CLASS arm is the definitional 1, not the max code-unit length | `(?<=a)x` -e utf8: compiles → REFUSED |
| S-U5 | utf8 `back_step` walks characters | `(?<=α)x` on `CE B1 78`: match(2,3) → nomatch |
| S-U6 | utf8 `next_pos` finds a boundary | find-all over `αβ`: 0,2,4 → 0,1,2,3,4 |
| S-U7 | surrogate range excluded from every lowered set | `^.$` on `ED A0 80`: reject → match(0,3) |
| S-U8 | the MRL clamp stride is the encoded length | `(a)(?:\x{3b1}){0,3}x`: clamp stride 2 present → absent |
| S-U9 | `back_step` validates each run's declared length | `(?<!.)x` on `C2 80 80 78`: match(3,4) → giveup -6 (the RX_R_INTERNAL abort) |
| S-U10 | the `cwmin` fixpoint runs to settlement | two-hop acyclic chain lookbehind: compiles → REFUSED |

S-U4 and S-U8 are re-aimed AS BUILT and say so in their own headers: the
design's forms of both are no-ops against the shipped code (S-U4's byte-width
function retired; S-U8's per-class `minw` arm was never built — §5.6.1's
exactness arrives through the lowering, not a `minw` arm). S-U4's sabotage is
the `[M5.0]` cross-note's own refuted cure, so it detects the wrong-turn a
reader of that uncorrected row would take.

---

## 4. LOCAL VALIDATION RUN (Frank's light-testing rule)

| instrument | result |
|---|---|
| `run_encoding_identity.sh` (byte axis, 4 axes, CC=gcc-16 PROCS=4) | **14/14, 0 differing, .abi=22 unchanged** |
| `run_encoding_checks.sh` (ENC_MAX_BLOCKS=150) | **7/7** — §8.5 0 divergences, CHK3 0, DD12a(i)/(ii) clean, S-U8 present |
| `run_mrl_tests.sh` | **27/0** (cwmax section + the K23/counter/lattice cells) |
| `make strict CC=gcc-16` | **clean** (`-Werror -Wshadow`) |
| `make test-recursion` | **10/0** |
| `make test-lookaround` (`run_lookaround_diff.sh` §1-4) | **green**; `run_expansion_diff.sh` structural §0-1 green |
| `make test-reject` | **598/0** (counts updated for `\x{}` base grammar: 286 rej / 104 acc) |
| the seven S-U rows | **all DETECTED** in the failing direction |

**`make test-rungselect test-possessify test-corpus`** (CC=gcc-16 PROCS=4,
one run, MAKE-EXIT=0) — the revbody clear's byte-path proof, measured rather
than argued from the identity gate:

- rungselect **24/0**; rungdiff **205 patterns / 395,757 cells / 0 diverged**,
  106 patterns on the reverse-deterministic rung (the rung population is
  intact — the clear is unreachable under `byte`), 985 rung-free
  byte-identical, DFA-routed byte-identical (704).
- possessify **16/0**; possdiff **155 patterns / 0 diverged**, 351 positive
  verdicts, 680 verdict-free byte-identical.
- corpus **27,045 cases passed / 0 failed**, 0 pattern-compile failures,
  size tripwire OK (2,962 rows; worst size and gcc-CPU pins untouched).
  The size log regenerated by the run's own compile pass is committed with
  this report (stage 1's precedent — droppable if the manager prefers it
  regenerated at merge).

---

## 5. DEVIATIONS AND WHAT I OWE

- **§8.5's full 3,319-block sweep is owed to the Linux slot.** Locally it ran a
  150-block slice at 0 divergences; `ENC_MAX_BLOCKS=0 make test-encoding-checks`
  is the whole corpus. The census (2932 ASCII blocks / 30 subject-exclusions)
  and its decode-not-text-scan control ran in full and pass.

- **`run_expansion_diff.sh`'s three-way libpcre2 differential** ran only its
  structural §0-1 arms locally; the whole three-way against this Mac's
  non-reference libpcre2 (10.48, not 10.46) is a Linux/slot concern by the
  same rule the design's oracle-host note gives. I FIXED a **pre-existing
  darwin harness bug** in that script while there: `-o "$d/b"` collided with
  the include dir `$d/B` on the case-insensitive macOS filesystem
  (`ld: ... Is a directory`), reproduced identically on base 1772fe41 (10×);
  renamed the binaries `runa`/`runb`. Flagged so the macport lane knows.

- **`run_mrl_tests.sh` carried two BSD-portability bugs** I fixed (both
  pre-existing since the Mac move, both silently making the whole section read
  "cc-fail"): `xargs -a` (GNU-only → `xargs < file`) and `sed -i` without a
  suffix (BSD reads the next arg as the extension → `sed -i.bak … && rm`).

- **`test-codegen` has 5 residual failures on this box** — OS-0b (two-engine
  ABI-block compile), K24 (accessor-count desugar), the inline-capability `nm`
  read, and SABANCHOR's one stale anchor **S199** (a macport rewrite of
  `tests/harness/run.sh`, a file I never touched). **All verified identical on
  base 1772fe41** (built and run there): my stage-2 work added ZERO codegen
  failures. S199 is the macport lane's to re-aim; the OS-0b/K24/nm cluster is
  darwin+gcc-16 and clears on Linux.

- **`docs/pcre2_compliance.md`'s `\x{...}` row** still reads "requires module
  'unicode-props'" — that page is regenerated by the `compliance-refresh`
  skill, not hand-edited, so I left it and flag it: `\x{}` is now base grammar.

---

## 6. RULINGS RECEIVED

`docs/dev/lanes/utf8s2_rulings.md` was polled at every stage boundary and never
present during the lane. R2 (stage 1's splice-in-place ruling) was already in
the design/code I inherited and is consumed as such.

---

## 7. DISCLOSURE

Every file written is inside `worktrees/utf8s2/`. Scratch is
`/private/tmp/.../scratchpad/utf8s2/`, not committed. Nothing outside the pcrec
repository was created, modified or deleted; pcrec-bench was not touched; no
ssh to any other machine. `gcc-16` throughout (bare gcc is Apple clang). Every
long validation ran in the background with a polled log. Spawn-time injections
beyond the brief: the session-root `CLAUDE.md`, the per-directory `CLAUDE.md`
files auto-injected on reads, and the memory index.
