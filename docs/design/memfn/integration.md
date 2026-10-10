# memory-functions: R1d, THE INTEGRATION MAP AND THE COMPOSITION MODEL

**REVISION 4.9 (lane `r9d`, 2026-10-08, from kit branch `lane/memfn-r9`
at main 5ddd2f04, design only): THE SIMD LAYER'S DESIGN PASS, request R-9
under D147 addendum 11 (SIMD is a parallel path; each form beats the
CURRENT scalar layer at its sites or names a benefit), REVISED AFTER THE
D6 PANEL r9 (`../../dev/reviews/2026-10-08-r9-memfn-simd.md`, 43 findings)
and D144 addendum 4. It overrides anything below that conflicts.** Read
§R4.9 first. In short:
- `[r9 F-1]` A zero-mover kit step, R4e′.0, first makes the FUNC part
  PRE and OFS share a selected first-match table, `fn_rows[]`, with a
  BODY slot (the scalar loops) and a PREFIX slot (born empty). **`[R4e′.0]` BUILT**
  (lane r4e0, 2026-10-09). SIMD rows
  are PREFIX rows; no decorator over the floor.
- `SCAN_ROWS` is the kit's form tables (`arms[]`, `rc_row`, `fn_rows[]`)
  under ONE shared walk and ONE deny carrier (`--memfn=`). SIMD forms are
  rows with a layer, an ISA level (`memfn/src/levels.def`) and their own
  deny; `policy`/`budget` are row-contract fields.
- THE FLOOR RULE: a SIMD-on rendering is the SIMD-off rendering plus
  guarded text (check C18, four legs (a)-(d) `[D155]`; on-target one
  replaced call per SIMD FUNC; source-level insertion-only at every
  target). SIMD bytes are neutral to every
  pcrec length decision by construction (RQ-3); D84's caps are Q-R9-9.
- Short spans fall to the next rung by a derived reach, `VW + T`, T
  defined once. The run-time cascade is a separate, filed row.
- `[r9 M-1]` Two tiers (D144 addendum 4): kit and lane timings anywhere
  are UNOFFICIAL; an OFFICIAL verdict is a pcrec-bench run on each box a
  level targets (ubuntubudu Zen 1, the dev box Zen 4, the Mac). Bench
  testees come before acceptance, through the pcrec manager.
- First batch: rows `vrun-w32`/`vrun-w16` for a FUNC part whose
  predicate is one RUN term and its site's only predicate (PRE window
  with no lead; OFS run-pinned by its own cell). SSE first. Everything
  else is filed with the cell it lacks.
- ~~Q-R9-1 is RESOLVED; Q-R9-2..9 are for Frank~~ `[D155]` **Q-R9-1..9
  are RULED (D155, Frank 2026-10-08; §R4.9.10).** Requests RQ-0..6 are for
  main (§R4.9.11). §R4.9.12 is the 43-id completeness table, plus D155's
  rows.
- `[D155]` **A function that does work never contains `#if`** (Q-R9-6's
  amendment, as restated by Q-R9-10 shape (c), D155 addendum 1;
  §R4.9.2.5). The level choice is made at FILE SCOPE: the FUNC's scalar
  loop becomes a helper `<fn>__body`, each rendered level adds a guarded
  helper `<fn>__w<VW>`, and the FUNC, written ONCE, is a SELECTOR whose
  whole body is the `#if`/`#elif`/`#else` chain, one plain call per arm.
  SIMD-off routes through `<fn>__body` too: a one-time byte move (+139 B
  per FUNC, measured) and a pcrec abi event, step R4e′.0b, measured as G1
  (§R4.9.2.6). **`[R4e′.0b]` BUILT** (lane r4e0b, 2026-10-09, abi 69 -> 70). Runtime dispatch stays FILED (`[MEMFN-RTDISPATCH]`);
  §R4.9.3.1 shows the same helpers serve it. Q-R9-10 and Q-R9-11 are
  RULED (D155 addendum 1).

Changed passages carry `[rev4.9]` in place; the panel revision's edits
carry `[r9 <id>]`. This revision keeps the number 4.9. `[r9b]` `[M7]`
marks merged, text at 4.9 (F-9 is closed: main is merged in). The r9b
light re-check pass (`../../dev/reviews/2026-10-09-r9b-memfn-simd.md`,
2 critics) applied its findings in place, each marked `[r9b]`.

**REVISION 4.8 (lane `m1b`, 2026-10-07, from kit branch `lane/memfn-m1b`
at main 993f8c1d): M1b's CONTRACT, request R-5 (runcmp migrates, zero
movers). They override anything below that conflicts.** Read §R4.8
first. The kit manager ruled Q-M1b-1..8 before the lane (§R4.8.0). In
short:
- §14.8's RUN_WORDS sentence was WRONG: pcrec's `stamp` sink op QUOTES
  its value, so the line would read `RX_RUN_WORDS "0"` on every artifact.
  The sink gains an UNQUOTED op, `stamp_int`, appended at the end;
- `mf_hooks.run_cmp` is retired and `note` stops carrying the word-load
  helpers: the kit compares runs and declares its helpers itself;
- all three in ONE `MF_SITE_ABI` 3 → 4 bump; `MF_VOCAB` stays 2;
- bit 43 crosses through ONE pcrec map table, into every site's
  `denies` AND `mf_art_begin`'s, and the kit asserts they agree;
- the run-compare rows are the kit's, read by `--list-axes` through an
  accessor.
No emitted byte moves and there is no pcrec abi event. Changed passages
carry `[rev4.8]` in place.

**REVISION 4.7 (lane `memfnfix`, 2026-10-05, from kit branch
`lane/memfn-r4a` at 99130d75): THE KIT'S CONTRACT AFTER G2, AND D147
ADDENDUM 10 FOLDED. They override anything below that conflicts.** Read
§R4.7 first. G2, the blinded kit tests, found three defects (F1-F3) and
asked seventeen contract questions (Q-G2-1..17). The kit session ruled
each one under D146, and §R4.7.0 maps every ruling to where it lives.
In short:
- VERIFY honours its range `[lo, n − end_back)`;
- `lo > n` is a legal EMPTY range;
- ON_CAND renders `empty = NOP`;
- out-of-enum fields and seven shapes outside the vocabulary are REFUSED
  loudly;
- an unsatisfiable run byte stays IN the vocabulary and renders as a
  term that never holds;
- five caller obligations are stated.

Q-G2-5 stays OPEN. **Q53-Q55 are RULED** (D147 addendum 10): the libc
record's refined form (§R4.3.3) and N7's scope (§R4.3.4) are now the
design of record, no longer proposals. **No open question for Frank
remains in §23.** Changed passages carry `[rev4.7]` in place.

**REVISION 4.6 (lane `memfnr46`, 2026-10-05, from kit branch
`lane/memfn-r45` at df041954, design only): THE r5 PANEL'S 23 FINDINGS
APPLIED (`../../dev/reviews/2026-10-05-r5-memfn-rev45.md`, A1-A12 and
B1-B11, all ACCEPTED by the kit session). They override anything below
that conflicts.** Read §R4.6 first. The blocker (A1): `set-leads`' lead
is OPTIONAL on DFA-scan routes and REQUIRED on no-DFA routes, where it
is part of K65's no-match proof (§14.5). `use` is a per-instance fact
(§14.5), the composite site's `empty` is MISS (§14.4), and `preds[]`
has one dense numbering (§15.5). Line citations in §14-§16 are now
function names. **This revision rules nothing: Q53-Q55 stay open, with
refined text (§23).** Changed passages carry `[rev4.6]` in place.
**`[rev4.7]` Q53-Q55 are now RULED (D147 addendum 10; §R4.7).**

**REVISION 4.5 (lane `memfnr45`, 2026-10-05, from kit branch
`lane/memfn-r45` at main 08caf4a3, design only): R-1'S LINUX VERDICT AND
D149 FOLDED. They override anything below that conflicts.** Read §R4.5
first. R4b is DONE and R4d's trigger is MET at SIMD-off on union-select
(§22). The LEAD ORDER is part of the composite site's form, a kit
per-site choice that defaults to lead first (§15.5). D149 binds every
kit form: each unroll width, block size and cut-over is measured,
derived or left to the compiler, or labelled in place as an unmeasured
default (§8.6 K-7). **This revision rules nothing: the open questions are
still Q53-Q55 only.** Changed passages carry `[rev4.5]` in place.

**REVISION 4.4 (lane `memfnr44`, 2026-10-05, from main 3b04f1ef, design
only): D147 ADDENDA 8-9 FOLDED. They override anything below that
conflicts.** Read §R4.4 first. Q43 is ruled (aarch64 SIMD-on forms wait
for a verdict-grade box). Q44, Q45, Q46, Q48 and Q49 are ruled as
recommended. **Q47 is refined: pcrec keeps ONE axis, `-fmemfn-simd`. The
kit's per-form switches live in the kit's OWN option namespace,
`--memfn=<opt>[,<opt>…]`, defined by a registry inside `memfn/` and
passed through uninterpreted. `--list-axes` prints a `memfn` section
from that registry, and a spec-pinned floor on the section's member
count is the independent control.** Everywhere an earlier passage spelled
a kit switch as an `axes.def` row, a generated axis, `mf_switches()` or
`--memfn-deny=`, read it through §R4.4.1. Changed passages carry
`[rev4.4]` in place. The open questions are now Q53-Q55 only.

**REVISION 4.3 (lane `memfnr43`, 2026-10-05, from main 7f94b0cd, design
only): FRANK'S 2026-10-05 RULINGS FOLDED — D146, D147 and D147 addenda
1-7. They override anything below that conflicts.** Read §R4.3 first.
Its table (§R4.3.0) maps each ruling to where it now lives. The
three-profile wording (`baseline` / `portable` / `native`) and the
`memfn-native` axis are replaced by ONE SIMD switch, spelled
`-fmemfn-simd` / `-fno-memfn-simd` and OFF by default (§R4.3.1).
Cascading ISA levels are a kit form (§R4.3.2). The stamp is Q39 as
ruled, plus addendum 6's libc record (§R4.3.3). EVERY search site
migrates, under a checked site manifest (§R4.3.4). The planner moves
live at M5 (§R4.3.5). Q51 and Q52 are rejected (§R4.3.6). §22's build
order and §23's question list are rebuilt. Changed passages carry
`[rev4.3]` in place. Where an earlier passage that carries no
`[rev4.3]` mark still says `memfn-native`, `-fmemfn-native`,
`-fno-memfn-native`, `portable` (as a profile) or `native` (as a
profile), read it through §R4.3.1's spelling table.

**REVISION 4.2 (lane `memfnsetup`, 2026-10-05, from main 06ec65c8,
design only): D147 APPLIED — the scalar algorithm stays live and
improvable forever, SIMD is a layer, each layer must be the best it can
be on its own, and every acceptance reading reports SIMD-off and
SIMD-on.** Read §L first: it defines the two layers over this design,
demotes the frozen baseline to a per-step comparator, gives every kit
change its own deny as its OFF arm, and lists every passage that
conflicted. Changed passages carry `[rev4.2]` in place. Frank's Q35 and
Q36 rulings are recorded in §23. The kit's in-tree home is now set up
(`memfn/`, lane memfnsetup).

**REVISION 4 (lane `memfndel4`, 2026-10-05, from main 1c2ba975, design
only): THE CONTRACT REWORKED FROM THE EMITTERS' ACTUAL SHAPES, per the
r3 light panel (`../../dev/reviews/2026-10-05-r3-memfn-delegation.md`,
F1-F13 and G-F1..G-F14, every finding ACCEPTED). Read §R4 first: it
names the seven standing rulings this revision honours and maps every
finding to its section. The new material is §14-§23. Revision 3's §8-§13
stand where §R4 does not override them; the overridden passages carry a
`[rev4]` annotation in place.** D146 is unchanged: pcrec describes a
search site and the kit returns its code.

**REVISION 3 (lane `memfndel`, 2026-10-05, from main 90d396fd, design
only): THE DELEGATION MODEL, per D146 (Frank, 2026-10-05). Read §R3
first. Every changed passage is marked `[rev3]`, and the new material is
§8-§13. Revision 2's K0 capability-and-price query (§7) is SUPERSEDED:
no price crosses the boundary, and pcrec does no cost comparison.** The
project is named **pcrec-memory-functions** ("the kit" below, as
before). Revisions 1 and 2 are kept below and annotated where rev 3
overrides them (house style: refutations inline, not edited away).

**REVISION 2 (lane `memfnk0`, 2026-10-05, from main 68acba37, design
only): the K0 capability-and-price query layer, per Frank's ruling on
Q12. Read §R2 first; every changed passage is marked `[rev2]`, and the
new layer is §7.** Revision 1's text below is kept where it still holds
and annotated in place where it does not (house style: refutations
inline, not edited away).

Owner row: `[MEMFN]` (docs/dev/plan.md), step R1d. Lane `memfnmap`,
2026-10-04, written from main at 8a41efd2 (abi 59), reading `lane/k82fix`
(abi 60, unmerged) for `req_admits[]`. DESIGN ONLY: nothing under `src/`,
`cli/`, `lib/` or `tests/` changes, and no emitted byte moves (D91). Every
table row, stamp, option and emitted text below is DESIGNED, not built.
Building any of it is an `abi` event plus a `docs/spec/` hunk (D76/D94,
D80), behind the trigger its plan step names (§6).

Frank (2026-10-04): *"Don't get too caught up with 'separate project'. We
need to integrate. We use decision tables to organize variants. SIMD
variants might slot into those tables cleanly if given the chance. What
does that mean? Separate projects may mean a product that can be used to
generate the code selected in the decision tables. Or if that doesn't
work, some things are in the remote project and some are local. That
said, a project that allows you to create bespoke high-speed memory
functions stands on its own."* And earlier: is there benefit in
constructing functions TAILORED to the need rather than a fixed set?

Inputs: `requirements.md` (R1: F1-F13, B1a/B1b/B2/B3, RB-*, N-*),
`isa_selection.md` (R1b), `isa_evaluation.md` (R1c), `survey.md` (R2),
`docs/design/compare_stack.md` (the L0-L4 layers, §2's site inventory),
D82 (the form slot), D91 (scalar first, two budgets), D119, D122 and its
addenda 2-3 (every form choice a `DFA_SELECT`-style row; SIMD later = one
row; SWAR admitted now), D139 (one class-form table, sites as bits), D144
item 4 (every optimization its own deny), D145 (generated-output licence
exception), and the tables themselves (§1).

---

## R4.9. Revision 4.9: the SIMD layer's design pass (R-9) `[rev4.9]`, revised after panel r9 `[r9]`

(Top-level, like §R4.8. It sits first because it replaces §22 R4e′,
extends §R4.3.2 and §8.6 K-6/K-7, and realizes §2.2's `SCAN_ROWS`
inside the kit.)

**The input.** Request R-9 (`memfn/docs/requests.md`): the R4e′ design
pass under D147 addendum 11. SIMD is an independent optimization path
because it switches on and off (`-fmemfn-simd`, default OFF). Each SIMD
form must be measurably FASTER than the CURRENT scalar layer at its
sites, or show a named benefit, because SIMD imposes restrictions (an ISA
requirement, no portability promise). Default-ON is its own ruled event
(R4f). Capacity is 2:1 migration:SIMD until M5′. This revision is DESIGN
ONLY: no source, no emitted byte, no timed run. It was written from kit
branch `lane/memfn-r9` at main 5ddd2f04 (lane r9d). The facts it states
about the box were read with `lscpu`, `/proc/cpuinfo` and sysfs on
2026-10-08, and the macro sets with `gcc -dM -E`.

**`[r9]` The panel revision.** The D6 panel r9
(`../../dev/reviews/2026-10-08-r9-memfn-simd.md`, three critics, 43
findings: C-1..C-12, M-1..M-16, F-1..F-15) and the rulings that postdate
the first draft (D144 addendum 4, D147 addenda 11-13, M6 = VMSTRIDE at
`MF_SITE_ABI` 8) are applied here by the same lane, every edit marked
`[r9 <id>]` in place. The completeness table is §R4.9.12. Where the first
draft's text is superseded it is replaced, and the mark says by what. The
kit facts below are read READ-ONLY at the kit tip (`lane/memfn-m7`:
M4 and M7 landed, `MF_SITE_ABI` 7, `MF_VOCAB` 3, 11 rows in `arms[]`,
`options.def` still EMPTY). This revision stays numbered 4.9. `[r9b]` `[M7]` marks merged, text at 4.9.

**What it decides, in short:**
- `[r9 F-1]` **A zero-mover SEAM comes first.** The FUNC part that PRE and
  OFS share (`ofs_fn_define`) has no row walk today. Step R4e′.0 makes its
  body a selected first-match table, `fn_rows[]`, with a SLOT column (BODY,
  PREFIX). The scalar bodies are its BODY rows; PREFIX is born empty. SIMD
  rows are PREFIX rows; they never call or wrap the floor row (§R4.9.2.1).
  `[D155]` They never wrap or splice it. A level helper's entry test
  CALLS the floor's helper `<fn>__body` by name, as its fall-through
  (§R4.9.2.5).
- `SCAN_ROWS` is the kit's form tables: `arms[]`, `rc_row` and now
  `fn_rows[]`, all walked by ONE shared walk (`[r9 F-3]`). SIMD forms are
  rows, each declaring a layer, an ISA level, its instruction classes and
  its own `--memfn=no-<row>` deny through the ONE deny carrier
  (`[r9 F-2]`). No parallel table.
- THE FLOOR RULE, unchanged in substance: a SIMD-on rendering is the
  SIMD-off rendering plus text that sits only inside level guards,
  PREPROCESSED-EQUAL off-target; on-target, insertion plus one replaced
  call per SIMD FUNC (raw text: insertion-only) (C18, four legs (a)-(d),
  `[r9 C-6]`, `[r9b]`). `[D155]` Ruled with an amendment: the guarded text
  is whole file-scope helper definitions plus a selector FUNC, and no
  function that does work holds a directive (a selector's whole body may
  be the `#if` chain, one call per arm, and nothing else). On-target, C18's leg (b) now allows
  exactly ONE replaced line per SIMD FUNC: the selected call
  (§R4.9.2.5, §R4.9.8).
- `[r9 C-3]` SIMD bytes are neutral to every pcrec selection BY
  CONSTRUCTION: the kit brackets guarded text and pcrec's length readers
  read the SIMD-off length (RQ-3, now a prerequisite). Whether D84's
  refusal cap counts guarded bytes is Q-R9-9.
- Short spans fall to the next rung by a DERIVED reach, `VW + T`, with T
  defined once (`[r9 C-1]`). A run-time cascade is a separate, filed row.
- `[r9 M-1]` **Verdicts are two-tier (D144 addendum 4).** Kit and lane
  timings anywhere are UNOFFICIAL and directional. An OFFICIAL verdict is
  a pcrec-bench run on each piece of hardware a row's level targets:
  ubuntubudu (Zen 1), the dev box (Zen 4, AVX2 and AVX-512), the Mac
  (aarch64, addendum 8). Bench testees come BEFORE acceptance. Acceptance
  requests go to the pcrec manager, who carries them to the bench inbox.
- The first batch is ONE site shape at two levels: a FUNC part whose
  predicate is one RUN term and is its site's only predicate, at 16-byte
  and 32-byte width. SSE (w16) first, by D144 addendum 4. Everything else
  is filed with the cell it lacks (§R4.9.7).
- `[r9fu]` **The scalar twin at every batch-1 site already calls glibc
  `memchr`** (measured, §R4.9.7.1): both BODY rows are glibc-backed. So
  batch 1's rows sit over `fn-pair` ONLY, where R-1 timed them against
  that glibc-backed body. `vrun` over `fn-memchr` is filed with its cell.
  That takes OFS run-pinned (always exact, so always `fn-memchr`) and the
  exact-window bin out of batch 1. No part of §R4.9 assumes a
  function-entry setup point (`[MEMFN-ENTRYSINK]`). The one form whose
  assembly shows per-call setup re-done inside a pcrec-owned outer loop is
  the filed `vrun` over OFS run-pinned (§R4.9.7.2).

### R4.9.0 Each input, and where it now lives

| input | what it says | where it lives now |
|---|---|---|
| `[D155]` D155 (main 3b1fd77c, Frank 2026-10-08) | Q-R9-1..9 ruled; Q-R9-6 amended (no `#if` in a function body (restated by add. 1 / Q-R9-10: a selector's whole body may be the `#if` chain); file-scope per-level helpers; SIMD-off routes through the helper as a measured abi event); `[MEMFN-RTDISPATCH]` filed with its terms (frequency class per site, per-level copies by target attribute selected once, a non-cascading level set, per-arch artifacts already served) | §R4.9.2.5 (the shape); §R4.9.2.6 (the abi event); §R4.9.3.1 (runtime dispatch, filed); §R4.9.8 (C18); §R4.9.10 (each Q marked RULED); §R4.9.12 (D155 rows) |
| D147 addendum 11 | SIMD is a parallel path; each form beats the CURRENT scalar layer at its sites or names a benefit; default-ON is ruled separately; 2:1 capacity until M5′ | §R4.9.6 (the bar); §22 R4e′ `[rev4.9]` (trigger, capacity) |
| `[r9 M-1]` D144 addendum 4 (main 04733583) | SIMD verdicts are pcrec-bench runs on the hardware each form targets; the manager coordinates the boxes; SSE first, the AVX2/AVX-512 order argued on evidence; AVX-512 is NOT filed for lack of hardware | §R4.9.5 (two tiers); §R4.9.5.1 (the submission); §R4.9.7 (the order) |
| `[r9]` D147 addendum 13 (main 26297b6c, PRELIMINARY) | "faster" = same-host, same-window pcrec-bench run against the scalar twin; target cells' median whole-call time beyond the noise band; no other cell regresses past the floor; per instruction-set tier; net of costs | §R4.9.6 (the bar is written in its terms; its "revisit when R-9's panel proposes a better regime" is answered there) |
| `[r9 F-7]` D147 addendum 12 (main eb2ca801) | N6 is RETIRED: it was an engine step, not a search site | §R4.9.7 filed list (N6 struck) |
| `[r9 F-6]` M6 = VMSTRIDE (R-10), `MF_SITE_ABI` 8 | multi-term ADVANCE, `MF_MAX_TERM` 32, `span_hi` as an iteration count; carries NO SIMD ADVANCE bound (manager, D77) | §R4.9.7 filed list |
| D147, addenda 2, 6, 7 | layers; cascades case by case; ONE switch; OFF by default | §R4.9.2 (the layer column); §R4.9.3 (cascades) |
| D147 addendum 8 (Q43) | aarch64 SIMD-on forms are not accepted without a verdict-grade box | §R4.9.5 item 9; §R4.9.7 filed list |
| D144 + addenda 1 and 3 | absolute deltas against a floor; ≥ ~50 ms loops; ASan/UBSan over movers when memory reads change; batch gates | §R4.9.5 |
| D149 | every unroll width, block size and cut-over measured, derived or left to the compiler, or labelled | §R4.9.5 item 10 (split correctness vs performance, `[r9 M-9]`) |
| D77 | build under a measured need | §R4.9.7 (the batch is evidence-only; the rest is filed) |
| D146, row contracts | the kit owns forms; a row declares `uses`/`serves` | §R4.9.2 |
| D84 | the emitted-size caps are not deniable and are overridable upward | §R4.9.2.4, Q-R9-9 |
| R-1 / R4b (`memfnr4b_report.md` §9; `probes/out/twins/r4b/linux/`) | `ffl` vs `swar` vs `emit`, Zen 1, gcc 15.2 | §R4.9.1 F1-F3; §R4.9.7 |
| `linux_results.md` | glibc's call term, the AVX2 knee, dispatch costs, T-A, the survey's x86 bars | §R4.9.3; §R4.9.7 filed list |
| `opt3_dfa_scan_measurement.md` §3-§4 | the DFA candidate skip skips 0 bytes per entry on English text | §R4.9.7 filed list (PF set) |
| `isa_selection.md`, `isa_evaluation.md`, `requirements.md` N-4/RB-3/RB-4/RB-7 | compile-time selection by predefined macros; no mutable static; a loop-free short path per tier | §R4.9.2, §R4.9.3 |
| `[r9]` the kit tip, read-only (`lane/memfn-m7`) | M4 (MLINE, `pf_memchr_back`, `MF_SITE_ABI` 6), M7 (MISMATCH, `mismatch_inplace`, N7 delegated, N7U pending (since retired, D147 add. 14), `MF_SITE_ABI` 7, `MF_VOCAB` 3); `ofs_fn_define` called directly by `precheck_define` and the OFS arm; `options.def` 0 rows | §R4.9.2.1 (the seam); §R4.9.7 |

### R4.9.1 Findings in the prior measurements, read before designing

**F-R9-1. R-1's 16-byte column measured the SCALAR path, at both widths.**
`f_ffl` (`probes/twins/tb_r4b.c`) returns `f_swar(...)` whenever
`n − pos < VW + T` (T = run length − 1). At pc16 (n = 16, pos = 0) that
holds for EVERY cell at BOTH widths: union-select 16 < 21 (w16) and
< 37 (w32), userpass 16 < 19 / 35, mod-i 16 < 18 / 34, cls-n-uc 16 < 17 /
33. So in every pc16 row, `ffl` and `swar` ran the same scalar algorithm
with the same constants. The rows still differ, consistently across
three launches:

| pc16, ns (ffl − swar, same build) | union-select | userpass | mod-i | cls-n-uc |
|---|---|---|---|---|
| SSE2 build, launch 1 | 4.63 − 6.32 = **−1.69** | 6.06 − 6.67 = **−0.61** | 5.41 − 7.08 = **−1.67** | 5.12 − 6.05 = **−0.93** |
| AVX2 build, median of 3 | 5.78 − 6.34 = **−0.56** | 7.31 − 6.63 = **+0.68** | 6.77 − 7.12 = **−0.35** | 6.42 − 6.01 = **+0.42** |

`[r9 M-13]` The first draft called this "per-binary code generation and
placement of one scalar loop". That is an INFERENCE: the control that
would show it was not run, and it may as well be the dispatch prefix
changing how gcc compiles the fall-through (inlining, register
allocation). What IS established is TEXT identity of the scalar path, so:
- **R-1's advice still holds, by construction.** "Short spans belong
  to the scalar form" is enforced by the derived reach (§R4.9.3). A row
  never runs its vector body below the span its body needs.
- **The floor rule is a TEXT claim.** C18 proves the scalar path's text
  is unchanged, never its machine code. Batch 1's submission therefore
  REPORTS an objdump comparison of the scalar fall-through region, OFF vs
  ON, as a fact (§R4.9.5.1), and the null population (§R4.9.5 item 6)
  decides how a below-reach per-call cell reads.

**F-R9-2. R-1's SIMD-on reading crossed `-march`.** The table's header
reads "SIMD-on = ffl − swar(sse2)": the AVX2 `ffl` was subtracted from
`swar` built WITHOUT `-mavx2`. linux_results.md §5 shows that `-march`
alone moves a scalar artifact by up to 5.7%, and by +34.5% on
`paren-rec`. So a SIMD-on reading compares builds at the SAME `-march`
(§R4.9.5 item 4). The cross-build w32-versus-w16 deltas in R-1 are trigger
evidence only.

**F-R9-3. R-1's SIMD-on comparator was not the current scalar layer at
every cell.** R-1 compared `ffl` against `swar`. The CURRENT scalar layer
at main is `emit` (R4d is unbuilt), and on a cell with a lead, R4d's
designed form is lead first (`swlf`, §15.5). Against those comparators:
- **userpass (the lead `=` rejects):** every vector form is NULL on
  throughput (gate 1m: emit 17,610, `ffl` SSE2 17,622, `ffllf` AVX2
  17,609; floor 23). Every vector form LOSES per call (`ffl` SSE2 vs emit:
  pc16 +2.16, pc256 +11.76, pc1024 +17.55; `ffllf` AVX2 vs emit: pc16
  +1.75, pc256 +0.72, pc1024 +0.23; floors 0.01-0.03).
- **cls-n-uc (the lead `m` never rejects):** `ffl` wins against both emit
  and swlf (gate 256k: 33.94 vs 76.53 and 108; pc1024: 22.61 vs 72.51 and
  59.12).
- **union-select and mod-i (no lead):** `ffl` wins against emit, swar and
  (vacuously) any lead order, in every throughput row and at pc64 and
  above.

The kit cannot tell userpass from cls-n-uc: the difference is the
subject, not the site. By K-1, the lead shape is not in the first batch
(§R4.9.7).

**F-R9-4. `[r9 M-1, M-12]` R-1 is UNOFFICIAL trigger evidence on an
official CPU class.** R-1 ran on ubuntubudu (Ryzen 5 1600, Zen 1:
x86-64-v3 at most, AVX2 executed as two 128-bit halves, slow microcoded
PDEP/PEXT, no AVX-512, governor `schedutil`) in a co-linked probe
harness pinned with `taskset`. Under D144 addendum 4 that box is one of
the bench's OFFICIAL boxes, and the harness is the UNOFFICIAL tier. So
the first draft's reason ("the box differs") was backwards: the CPU is an
official class, the instrument is not. R-1 STRENGTHENS the case for w16
on that CPU (w16 beats emit AND swar on every throughput row and every
per-call row above reach, e.g. union-select gate 1m 364,078 → 48,844 ns
against a floor of 1,073) and leaves w32's case as it was (a throughput
win over w16, per-call mixed on the same CPU). It does not repair the
gaps: no exact (unmasked) window cell, no VM-hybrid cell, pc16 ran the
scalar path, R-1 crossed `-march` (F-R9-2). The dev box
(`pcrec@192.168.1.17`, Ryzen 7 7700X, Zen 4, 8 cores / 16 threads,
`avx2`, `avx512f/bw/vl/vbmi`, `gfni`, `vpclmulqdq`, governor
`performance`, glibc 2.43, gcc 15.2.0, no clang; read 2026-10-08 at load
average 7.9) is ALSO an official bench box under addendum 4, the only one
that executes AVX-512.

**F-R9-5. SIMD-on text is LONGER, and pcrec reads emitted length.** A
SIMD rendering is the scalar rendering plus guarded text (§R4.9.2).
pcrec has selections that compare emitted LENGTH against a threshold:
- the VM entry-shape knee (`job->vmsb` through `pcrec_sb_len_uncut`,
  4,096 bytes);
- the size-cap ladder (`fit_rungs[]`, `PCREC_MAX_EMIT_BYTES`), whose
  measured size includes the stamp lines (`match_api.md` §6);
- and D84's two REFUSAL caps (code bytes 500,000, total 1,000,000).

`[r9 C-3]` The first draft proposed to MEASURE this (C-SEL) and build a
fix only if the census moved something. The panel showed that cannot
work: stamps that quote measured sizes (`VM_PREFILTER_WHY "size cap retry,
hybrid 1026588 > 1000000"`, the K-ladder's `%zu nodes %zu/%zu bytes`)
differ ON vs OFF on exactly the near-cap witnesses C-SEL names, and a
census over corpus + bench + witnesses cannot show that no user pattern
sits within the SIMD delta of a threshold. So neutrality is made true BY
CONSTRUCTION (§R4.9.2.4, RQ-3 now a prerequisite), C-SEL becomes its
check, and the refusal cap is a separate question (Q-R9-9).

**F-R9-6. pcrec does not carry `--memfn=` yet.** `--list-axes` prints the
`memfn` section (`src/dump/axes_dump.c`), but no CLI flag, config
directive or library field carries the string, so `mf_site.opts` is
always NULL (`memfn_sites.c` sets it). `[r9 F-8]` No kit row has a
PCREC-REACHABLE OFF arm until pcrec carries it (G2's generated sites
already set `opts`, so the kit's own tests reach it). That covers R4d's
row and every SIMD row (request RQ-1).

**F-R9-7. A vector skip at the DFA's candidate start has negative
evidence.** `opt3_dfa_scan_measurement.md` §3-§4: on English text the
candidate-start skip is entered 190,651 times per MiB and skips 0 bytes,
because non-candidate runs have length 1. A 7x faster pshufb skip made
all three bench subjects SLOWER, with a crossover at ~32-byte runs.
T-A's 4-15x set-classifier wins (linux_results.md §6.1) are on a MISS
over a whole 64 KiB span, which is the opposite regime.

**F-R9-8 `[r9fu]`. Every batch-1 FUNC body already calls glibc `memchr`,
and R-1 timed the vector form against that body for `fn-pair` only.**
Measured on witness patterns at the kit tip (§R4.9.7.1). Both BODY rows
call `memchr` (one stream for `fn-memchr`, two for `fn-pair`), the run
verify is inline word loads (no `memcmp`), and `nm -u` on every artifact
lists `memchr`. R-1's `emit` column is byte-identical to today's
`fn-pair` FUNC text for union-select and mod-i. So for `fn-pair` R-1
already compared against the glibc-backed twin, and the SIMD-on verdict
column it printed (`ffl − swar`) understates the margin. R-1 has no cell
where the vector form and the glibc-backed `fn-memchr` body compute the
same function. glibc's ifunc picks its `memchr` by CPU at load time, not
by the consumer's `-march`, so at the default recipe a w16 (SSE2) row
competes there with a scalar twin whose `memchr` already runs at the
CPU's top tier.

### R4.9.2 `SCAN_ROWS`: the FUNC-body seam, and SIMD forms as rows

**What `SCAN_ROWS` is now.** Revision 1 (§2.2) designed `SCAN_ROWS` as a
pcrec table. Revision 3 moved every form choice into the kit (D146).
Revision 4.9 realizes `SCAN_ROWS` as the kit's first-match form tables:
- the composer's `arms[]` (`memfn/src/compose.c`). `[r9 F-7]` At the kit
  tip it has 11 rows (`ofsskip`, `precheck`, `precheck_assign`, `runcmp`,
  `pf_memchr`, `pf_memchr_bounded`, `pf_walk`, `pf_walk_bounded`,
  `pf_memchr_back`, `mismatch_inplace`, `generic`) over the ops FIND,
  SKIP (with the ADVANCE handoff), VERIFY, ALL_PRESENT and MISMATCH;
- `rc_row` (`memfn/src/runcmp.c`) for the compare of one run;
- `[r9 F-1]` NEW, `fn_rows[]` (`memfn/src/ofsskip.c`), the body of the
  FUNC part that the PRE and OFS sites share (§R4.9.2.1).

One table answers "which text renders this", whatever layer the text
belongs to, and one walk serves all three (§R4.9.2.3). That follows
memory `pcrec-decisions-as-first-match-tables`, and it is why §2.6's
"rows, not a parallel mechanism" holds.

#### R4.9.2.1 THE SEAM: the FUNC body as a selected row table `[r9 F-1, C-2]`

**The problem (F-1, verified at the kit tip).** The text batch 1 changes
is the body of the scanning FUNCTION (`static inline size_t <name>(const
unsigned char *subject, size_t n, size_t pos …)`). That function is
rendered by `ofs_fn_define` (`memfn/src/ofsskip.c`), which no row walk
reaches:
- `precheck_define` (`memfn/src/precheck.c`, the PRE composite) calls
  `ofs_fn_define` directly, once per predicate holding an `fn_ref`;
- the OFS arm's define calls the SAME `ofs_fn_define`;
- inside it, an inline `if (b >= 0) return pair_body(…)` already chooses
  between two scalar bodies (two `memchr` streams when the scanned
  position is a two-member cube, one `memchr` otherwise). That is a
  selection with no row, no deny and no trace.

So a SIMD row in `arms[]` keyed on "the PRE composite" cannot be evaluated
where the text is rendered, and a row keyed on the FUNC predicate alone
silently reaches OFS too. The first draft's "continue the walk and
collect" was a decorator over the floor row, which the house rule forbids.

**The seam: step R4e′.0, kit-only, ZERO MOVERS, before any SIMD row.**
1. `ofs_fn_define` gains the calling SITE as an input:
   `ofs_fn_define(art, h, s, p, fn, o)`. Both callers pass the site they
   render (`precheck_define` its composite, the OFS arm its FIND site).
   This is a kit-internal signature; no `mf_site` field changes and there
   is no `MF_SITE_ABI` bump.
2. Its body becomes ONE first-match table, `fn_rows[]`, walked by the
   shared kit walk (§R4.9.2.3) with input `(site, pred, hooks)`, the same
   triple `gate_in` already carries. Each row has a SLOT column, the
   question it answers (D151 addendum 3's shape: one table, rows tagged by
   slot, the walk takes a slot):
   - **BODY:** which scalar loop is the function's body. Rows at birth:
     `fn-pair` (applies: the scanned position is a two-member cube, i.e.
     today's `b >= 0`) and `fn-memchr` (applies: otherwise). These two rows
     ARE today's inline branch, moved into the table text-for-text. Both
     are scalar, undeniable (no options.def row: they move no byte), and
     carry `ofs_fn`'s current row contract.
   - **PREFIX:** ~~what goes in front of the body: helper definitions at
     file scope above the function, and dispatch rungs at the top of its
     body.~~ `[D155]` which guarded per-level helper DEFINITIONS sit at
     file scope beside the body helper. A PREFIX row renders whole
     `static inline` function definitions only, never a line inside
     another function. Born EMPTY, the way `options.def` was born empty.
     An empty PREFIX slot renders zero bytes.
3. **Assembly, fixed order, by the seam:** ~~the chosen PREFIX row's file-
   scope part; the function head (`ofs_fn_define`'s existing text); the
   chosen PREFIX row's dispatch rungs; the chosen BODY row's loop.~~
   `[D155]` the chosen BODY row's loop as the helper `<fn>__body`; the
   chosen PREFIX row's helpers and its named rungs' helpers, one guarded
   block per level; then the FUNC itself, written once. With a PREFIX
   row, the FUNC's whole body is the selector chain, one call per arm.
   §R4.9.2.5 gives the shape. At R4e′.0 itself (zero movers) the BODY row still renders
   inside the FUNC as today: the move to `<fn>__body` is the separate
   step R4e′.0b (§R4.9.2.6). The
   walk asks BODY FIRST, so the floor is computed before any SIMD row is
   asked (`[r9 C-2]`), and the PREFIX walk receives the chosen BODY row's
   id. Neither row calls, wraps or splices the other: the seam owns the
   order, and each row writes only its own slot (a PREFIX row's render
   function has no access to the body). `[D155]` A PREFIX row's helper
   does CALL its fall-through by NAME (`<fn>__body` or the next rung's
   helper). The seam hands it that name; the row never sees the body's
   text.
4. **The gate for the step** (I1's shape): every `emit_sweep` stream
   byte-identical against the parent at both comment tiers and every axis;
   `arms.tsv` pins unchanged; G2 quick unchanged; the trace gains a table
   name `fn` and its two rows, read by `rows_check` (each row's witness: a
   two-member-cube scan, e.g. a caseless pinned run, for `fn-pair`; an
   exact scan for `fn-memchr`; floors in `row_floors.tsv`).
5. **What is pcrec's:** nothing. The kit owns the renderer, so the seam is
   kit-side end to end. pcrec's identity gates are its control.

> **`[R4e′.0]` BUILT** (lane r4e0, 2026-10-09, request R-11;
> `docs/dev/lanes/r4e0_report.md`). Kit-only, zero movers, no options.def
> row, no `MF_SITE_ABI` bump, no abi event. As built:
> - `fn_rows[]` (`memfn/src/ofsskip.c`) holds `fn-pair` and `fn-memchr`
>   in the BODY slot; the PREFIX slot is empty. The two bodies are
>   today's text moved verbatim into `pair_body`/`memchr_body`. `fn-memchr`
>   is the slot's FLOOR: its predicate always holds, and first-match order
>   keeps it off a cube (its text is right only where the scanned position
>   is one byte). Sabotage S686 (the two rows swapped) holds that order.
> - `ofs_fn_define(art, handle, h, p, fn, o)`: the calling site goes in as
>   its HANDLE, not an `mf_site *`. The handle gives the site
>   (`art->sites[handle - 1]`) and numbers the trace record.
> - Text order: the PREFIX row's helpers (none), the FUNC head, the BODY
>   loop. That is §R4.9.2.5's order without `<fn>__body`, which R4e′.0b
>   adds. The PREFIX walk is handed the chosen BODY row (`fn_in.body`).
> - Contracts `fn_pair_ct`/`fn_memchr_ct`. They read `denies`
>   (NONE|RUN_OVERLAP), `table_ref` (NONE|REF), `reverse` (NO) and no
>   `floor`. Every other field is the calling arm's, which the arms walk
>   checked first, so they serve MF_ANY there. That includes `pred`/
>   `preds`: the walk's predicate is one of them, and ofs_fn_applies holds
>   it.
> - Trace table `fn`, phase `define`, site = the calling site's handle.
>   The gate's reach registry went from 16 to 32 rows, because 17 rows
>   would have overflowed it (`REACH_DROPPED`).
> - The gate's witnesses are in `tests/memfn/rows.tsv` (`fn-pair`:
>   `(?i)cat`, control `-fno-req-run-fold`; `fn-memchr`: `abc[0-9]+xyz`,
>   control `-fno-req-run -fno-offset-skip`). G2 floors are measured
>   (`row_floors.tsv`). The pcrec floors are the slot census's.

**The sites the seam reaches.** Every `ofs_fn_define` call, i.e. every
emitted FUNC part. They have three pcrec customers (names from
`emit_dfa.c`):

| FUNC part (pcrec's name) | delegated site | handoff | pcrec route (stamps) | reached by batch 1's rows? |
|---|---|---|---|---|
| `<p>_reqrun` (`fn_ref` 1, the window run) | PRE composite | ASSIGN on a DFA-scan route; ON_MISS on a no-DFA route; the VM-hybrid handoff route (rev 4.6) | DFA-scan, no-DFA, VM hybrid | YES when the window run is the site's ONLY predicate (no lead, no set rest, no whole run) AND `[r9fu]` its BODY row is `fn-pair` (the scanned position is a two-member cube); a window whose scanned position is one byte (every exact run; a masked run whose pick is a non-letter, e.g. `(?i)\d+ab/cd` scans `/`) is `fn-memchr`, NO in batch 1 (§R4.9.7.1) |
| `<p>_reqrun_whole` (`fn_ref` 2, [K66]'s whole run) | PRE composite, no-DFA routes only | ON_MISS | no-DFA | NO: such a site also holds the window predicate, so the run is never the site's only predicate |
| `<p>_ofsskip` | OFS (FIND/RETURN), selected by `cand_rows[]`' `offset-set`, `offset-set-bounded`, `run-pinned`, `run-pinned-bounded` rows | RETURN | DFA prefilter | `run-pinned[-bounded]`: YES when the pinned k-set is the run alone. `[r9fu]` NO in batch 1: the run-pin is exact-only, so every such FUNC's BODY is `fn-memchr` (witness `/user\|/users`, the bench's `router-prefix-order`); it moves to the filed `vrun` over `fn-memchr` row (§R4.9.7.1). `offset-set[-bounded]`: NO (set terms only, no run) |

**OFS run-pinned, which R-1 never timed.** `[r9fu]` Under §R4.9.7.1 this
bin is no longer batch 1's: every run-pinned FUNC is `fn-memchr`, and
batch 1's rows sit over `fn-pair` only. What follows now binds the filed
`vrun` over `fn-memchr` row, unchanged, and that row's trigger cell
includes this bin. R-1's cells are PRE sites. The
shape-keyed predicate reaches OFS run-pinned sites whose k-set is the run
alone, and the panel ruled that those need their own cell or a structural
exclusion before a SIMD row may apply to them. The design takes the CELL:
- The seam step's census (an `MF_TRACE` build over corpus + bench,
  counting `fn` walks by customer, slot verdict and predicate shape)
  enumerates the OFS run-pinned sites the predicate reaches, by id, with a
  K35 floor. The bench has run-pinned prefilter artifacts (S1's census:
  27 bench caps artifacts selected the `run-pinned` pair at its pin;
  `router-prefix-order`'s `/user` is the named exact witness), so the
  census names bench patterns for the bin, or the bin gets a synthetic
  witness from the capability subbench (§R4.9.5.1).
- The OFS bin is a separate bin of the pre-registered population
  (§R4.9.6). Until it has an official reading the row may land as a
  CANDIDATE but is not ACCEPTED (§R4.9.6 lifecycle).
- FALLBACK, if the bench cannot schedule the cell: a structural exclusion
  that is an ordinary APPLIES conjunct on a stated site field
  (`s->op != MF_OP_FIND`), not a special case, recorded in the row's
  record and lifted by the cell.
- The same applies to the VM-hybrid route of the PRE window (§R4.9.6 bins,
  `[r9 C-11]`).

#### R4.9.2.2 The SIMD row's declaration, and `levels.def`

**The row declaration.** A row of any of the three tables may carry ONE
declaration struct. A scalar row's is NULL (the scalar default: layer
SCALAR, no level, budget from its contract).

```c
/* memfn/src/kit.h (DESIGNED, R4e′ batch 1) */
typedef struct mf_formdecl {
    const char *opt;       /* [r9 F-2] its options.def row name: the ONE deny
                              carrier (`--memfn=no-<opt>`). Layer and budget are
                              READ from that row through the name, never
                              restated here (one source)                        */
    uint8_t     level;     /* a levels.def token: the ISA level its text needs  */
    const char *const *over;   /* [r9 C-2] the BODY rows it may sit over         */
    const char *const *rungs;  /* the narrower SAME-FORM rows its dispatch names,
                              top-down: the ladder is DATA, never a walk-on     */
    uint32_t    insn;      /* [r9 M-11] the instruction classes the text uses
                              (MF_I_* bits: cmpeq, movemask, ctz, shuffle, ...) */
    uint32_t  (*reach)(const mf_site *s, const mf_pred *p);
                           /* the derived span its vector body needs, VW + T
                              (§R4.9.3); the correctness bound, never a tuning */
    uint32_t    guarded_max; /* [r9 C-3] an upper bound on the guarded bytes one
                              rendering writes, stated by the kit and checked by
                              G2 (Q-R9-9's per-row bound)                       */
} mf_formdecl;
```

**The level registry: `memfn/src/levels.def`** (kit-private, born with
batch 1; pcrec never includes it, so C4 is unaffected). It is an X-macro
in `options.def`'s idiom:

```
/* MF_LEVEL(token, family, guard, vw, test_march, forbid, stamp)
 *   token       kit-private id
 *   family      the architecture family (x86-64 | aarch64)
 *   guard       the preprocessor condition the level's text sits under:
 *               predefined macros ONLY (RB-3), never a probe or a run-time
 *               test. [r9 C-8] It names the architecture and excludes the
 *               ILP32 ABIs (i686 -msse2 and x32 -mx32 both define __SSE2__;
 *               x32 also defines __x86_64__ — gcc -dM -E, 2026-10-08)
 *   vw          the register width in bytes, the DERIVED vector width
 *   test_march  [r9 F-13] the -march the harness compiles this level at
 *               (tests read it through mf_levels(); no -march name reaches
 *               pcrec's src/, C4)
 *   forbid      [r9 M-11] instruction classes a row at this level may NOT
 *               use until a pcrec-bench run on Zen 1 shows no loss:
 *               PDEP/PEXT (BMI2, microcoded on Zen 1) and gathers
 *   stamp       the level's token in MEMFN_FORMS (opaque, arch-blind)     */
MF_LEVEL(LV_X86_W16, x86_64,
         "defined(__x86_64__) && !defined(__ILP32__) && defined(__SSE2__)",
         16, "x86-64",    MF_I_PDEP_PEXT | MF_I_GATHER, "w16")
MF_LEVEL(LV_X86_W32, x86_64,
         "defined(__x86_64__) && !defined(__ILP32__) && defined(__AVX2__)",
         32, "x86-64-v3", MF_I_PDEP_PEXT | MF_I_GATHER, "w32")
```

`[r9 F-13]` The kit exports `mf_levels()` beside `mf_options()`, and the
harness reads the level list (and each level's `test_march`) from it, with
a literal floor on its count in the tests (K35). Rows reference a level by
token; they never spell a guard. A 64-byte (AVX-512) level and every
aarch64 level are NOT in batch 1 (§R4.9.7); each is born with its first
row, and an aarch64 row also needs addendum 8's acceptance.

**How the vector ops are spelled** (`[r9 F-10, C-7]`). The helpers use the
compiler's x86 intrinsics (`<emmintrin.h>` at w16, `<immintrin.h>` at
w32): the one spelling gcc and clang both accept, and a compiler header
rather than a libc one, so the artifact stays self-contained. The kit
writes the `#include` INSIDE the level guard at file scope, immediately
before the first helper at that level (once per artifact per level; the
`mf_art` remembers). There is no new `MF_INC_` bit: pcrec writes the
`MF_INC_*` includes unguarded at the top, which would put 3,291
(`emmintrin`) or 45,912 (`immintrin`) preprocessed lines into the
`-mgeneral-regs-only` text and turn C18 red on every mover, and pcrec
writing the guard itself would break C4. No level guard ever appears in
the `.h` (`[r9 C-9]`): a guard there would be evaluated under the
CONSUMER TU's flags. Batch 1's FUNC parts are `static inline` in the
`.c`. `MEMFN_LIBC`'s finishing pass scans emitted text, not preprocessed
text, so an intrinsics header is never read as a libc call.

#### R4.9.2.3 The walk: one shared walk, row contracts, one deny carrier `[r9 F-2, F-3, F-12]`

**One walk.** `select_arm` (`compose.c`) and `rc_row_of` (`runcmp.c`) are
today two near-identical walks (deny, gate, predicate, trace). R4e′.0
extracts their shared prefix ONCE, `kit_walk(table, slot, in, gphases,
trace)`, and all three tables use it (`fn_rows[]` takes a slot; the other
two have one). The extraction is part of the zero-mover seam step (its
text effect is nil; the trace names are unchanged).

> **`[R4e′.0]` BUILT** as `kit_walk(table, slot, in, gphases, denies, x,
> tc, why)` (`memfn/src/compose.c`). A table is a `kit_table` of accessors
> (`ct`, `slot`, `deny`, `holds`). `select_arm`, `rc_row_of` and
> `fn_select` call it. Only tests 1, 2 and 5 are built:
> - test 1 reads the one `MF_D_*` bit;
> - test 3 (REACH) and test 4 (OVER) arrive with batch 1's first SIMD row,
>   since no row reads them today (D77);
> - reading `--memfn=` in test 1 is RQ-1's.
>
> A slot holding no row is not a selection, and records nothing in the
> trace. **Open for batch 1:** a PREFIX walk that asks rows and chooses
> none is not a refusal, but today's `END chosen=-` spells a refusal
> (`trace_format.md`). The trace needs a word for it before the first
> PREFIX row lands. Sabotage S689 shows the census reads such an END as
> a refusal.

**The walk, first match, per row in table order:**

| # | test | verdict when it fails |
|---|---|---|
| 1 | DENY: the row's options.def name is named `no-<opt>` in the site's `opts`; or, for the one legacy row, its `MF_D_*` bit is in the art's `denies` | `DENIED` (existing word) |
| 2 | CONTRACT: the row's `uses`/`serves` gate (row_contracts.md R1, R2), now including the stated fields `policy` and `budget` | `DECLINED` + the field mask (existing) |
| 3 | REACH (SIMD rows only, a row predicate): `span_hi ≥ reach(site, pred)`. A site pcrec PROVES shorter than the vector body's reach never gets the rung | `PRED_FALSE` |
| 4 | OVER (PREFIX rows only): the chosen BODY row is in the row's `over` list | `PRED_FALSE` |
| 5 | APPLIES: the row's own predicate over `(site, pred, hooks)` | `PRED_FALSE` |
| 6 | all pass | `CHOSEN` |

**Policy and budget are FIELDS, not new walk tests** (`[r9 F-3]`). The
first draft bolted a layer test, a size test and a budget test onto the
arms walk with new trace words (`INERT:PORTABLE`, `INERT:SIZE`). They are
withdrawn. `policy` (already a stated `mf_site` field, read by no kit row
today) and the site's budget enter `fields.def` as stated-bit VALUE
fields: a row serves a stated value iff it serves every class bit the
value carries (R2). Classes: `PORTABLE` (`MF_P_PORTABLE_ONLY`),
`INLOOP` (`MF_P_INLOOP`), `SIZE` (`MF_P_SIZE_LEANING`). Scalar rows serve
every class. A SIMD row serves neither `PORTABLE` nor `INLOOP` unless its
options.def budget is `MF_B_LOOP` (none in batch 1). So the existing
`DECLINED` verdict, N2's would-decline census and `rows_check` see a SIMD
row's policy decline with no new vocabulary.

**`SIZE` is NOT decided here** (`[r9 F-12]`). Q44 rules the dial
interaction at R4d as a D103 diff. Until that diff, SIMD rows SERVE
`SIZE`: an explicit `-fmemfn-simd` under `--tune -2/-1` renders its SIMD
rows rather than going silently inert. The SIMD × tune cell is put into
R4d's D103 diff. `MF_P_SIZE_LEANING` is set by nothing at the kit tip, so
the population of the cell is empty today.

**One deny carrier** (`[r9 F-2]`). Every NEW kit deny is an options.def
row reached through `mf_site.opts` (`--memfn=`), named in the row's
declaration and nowhere else. The one existing `MF_D_*` bit,
`MF_D_RUN_OVERLAP` (pcrec axis bit 43, `-fno-run-overlap`, tuning.md
§2.38, crossed into the kit by one map table at M1b), STAYS as the legacy
exception, for a stated reason: it is a caller-observable pcrec flag that
predates the kit namespace, listed as an axis by `--list-axes`. Retiring
it into `--memfn=no-run-overlap` is a CLI and spec change (D80) with no
problem scenario. Rules: no new `MF_D_*` bit; walk test 1 reads both
through one function; the bit's retirement is filed with "a second legacy
bit appears" as its trigger. **Order:** DENY is test 1, so a
`--memfn=no-vrun-w32` at `-fno-memfn-simd` reads `DENIED` (it is accepted
and inert, `[r9 F-8]`); a separate DENY arm at SIMD-off is untestable and
needs no test, since both verdicts render the floor.

**Row contracts.** A SIMD (PREFIX) row declares `uses`/`serves` like any
row. Because the body under it is the BODY row's text, it must SERVE every
hook class that BODY row serves at that site, or it DECLINES (R2) and the
FUNC renders the floor alone. A SIMD row never widens a site's contract.
Its in-block verify goes through the BODY's own verify chain, i.e.
`runcmp`'s `rc_row` (`[r9 C-12]`): one run compare, so the `denies` class
(bit 43) reaches the vector text exactly as it reaches the floor, and the
SIMD row's `serves` for `denies` equals its BODY row's.

**The ladder: what a chosen PREFIX row renders** (`[r9 C-2, F-1]`). The
PREFIX walk is first match: ONE row is chosen, the TOP rung. The ladder
below it is not a walk-on and not a collect: it is the rows its
declaration NAMES in `rungs` (same form stem by construction, top-down),
each re-asked tests 1-5 by the same walk. A named rung that fails is
skipped and traced; the floor is the BODY row, always present. So the
stamp can never name another form's row (the first draft's `vfoo-w16`
hole is closed by data, not by a stem comparison). `[D155]` Each rendered
rung is ONE guarded helper definition. Its fall-through, the next
rendered rung's helper or `<fn>__body`, is written by the seam from this
same `rungs` list, as the helper's entry test (§R4.9.2.5). A skipped rung
therefore just drops out of the chain: the rung above it falls through to
the one below.

> **THE FLOOR RULE** (`[D155]` RULED, Q-R9-6, with Frank's amendment).
> The SIMD-on rendering of an artifact is its SIMD-off rendering,
> unchanged, with text INSERTED, and every inserted byte sits inside a
> level-guard block. The amendment adds: no preprocessor directive ever
> sits inside a function body. The level choice is made at FILE SCOPE,
> and every function that does work is directive-free; a selector's
> whole body may be the `#if` chain, one call per arm, and nothing else
> (§R4.9.2.5, Q-R9-10 shape (c)).
> Stated as the properties C18 checks (§R4.9.8):
> (a) PREPROCESSED-EQUAL off-target: with no ISA macro defined
> (`-mgeneral-regs-only`, `-mno-sse2`), the SIMD-on and SIMD-off
> artifacts preprocess to the same text. This is the exact form of "the
> SIMD-on artifact compiled without the features IS the SIMD-off
> artifact". Measured on the probes: EQUAL, 12 of 12 (§R4.9.2.5; `[r9b]` taken on the superseded file-scope-definitions rendering).
> (b) `[D155]` ONE REPLACED CALL PER FUNC on-target: at each live level
> L, the SIMD-on preprocessed text is the SIMD-off preprocessed text with
> lines INSERTED, plus, for each FUNC that carries a SIMD row, exactly
> ONE changed line: the selected definition's call
> `return <fn>__body(<args>);` becomes `return <fn>__w<VW>(<args>);`.
> Nothing else may change or be removed. ~~(b) INSERTION-ONLY on-target~~:
> the r9 leg (C-6) assumed rungs INSIDE the FUNC body. Under file-scope
> selection the FUNC's one call necessarily names a different helper
> on-target, so pure insertion is impossible by construction. The
> replaced-call count is checked against the mover census (one per SIMD
> FUNC), so the leg is no weaker. It still catches guarded text that
> changes the floor: a guarded `#define memchr my_memchr` rewrites
> `<fn>__body`'s preprocessed lines and shows as extra changed lines.
> (c) `[D155]` SOURCE-LEVEL INSERTION-ONLY at every target: the raw
> SIMD-on text is the raw SIMD-off text with lines inserted and none
> removed. The scalar `#else` arm IS the SIMD-off FUNC, byte for byte.
> Measured: 0 deleted lines on 4 of 4 probe renderings (`[r9b]` taken on the superseded rendering; re-measured by G1). This is what
> makes RQ-3's `len − simd_guarded` exact (§R4.9.2.4).
> (d) `[D155]` NO DIRECTIVE IN A BODY EXCEPT THE SELECTOR'S: a `#` line
> may occur between a function's opening `{` and its matching `}` in the
> SIMD-on text ONLY in the selector shape, where the function's whole
> body is the `#if`/`#elif`/`#else`/`#endif` chain, one call per arm, and
> nothing else. Any other `#` line in a function body is a C18 failure.
> This is a lint on the raw text.

`[D155]` The r9 FUNC shape that stood here put two `#if` rungs at the top
of the FUNC body (`if (pos < n && n − pos ≥ <reach>) return
rx_reqrun_w32(…)` under the w32 guard, then the w16 rung, then the BODY's
loop inline). The amendment WITHDRAWS it. The shape is now §R4.9.2.5's:
the loop is a helper, each level is a helper, and the FUNC is one call.

The STMT use lines are UNCHANGED: they still call `rx_reqrun`. A
STMT-only site (a later batch) uses the same slots. ~~its PREFIX is an
`#if <guard> <vector text> #else` around a BODY it does not write~~
`[D155]` A STMT has no function body of its own to keep directive-free.
If its text sits inside an emitted function (pcrec's `rx_search`), a
`#if` around it would put a directive inside that body, which the
amendment forbids. So a STMT-only site takes SIMD only by becoming a
call to a file-scope helper (a FUNC part). Designing that is that
batch's.

What the rule buys:
- **One scalar spelling.** The floor of every ladder IS the BODY row the
  site gets at SIMD-off. `[D155]` It is rendered ONCE per artifact, as
  `<fn>__body`, and every level's helper falls through to it by name.
- **Every SIMD-on artifact compiles and runs on any target** (at scalar
  speed off its levels). Addendum 6 does not require this. It costs
  source bytes only, and it is what makes C18 possible (Q-R9-6).
- **An independent check, C18** (§R4.9.8): the preprocessor, with gcc's
  own macro set, decides which text survives. `-mgeneral-regs-only` was
  verified on this box to empty the x86 vector macros (it keeps only
  `__x86_64__`), even with `-march=x86-64-v3` added. `[D155]` So does
  `-mno-sse2`, and `-mavx2 -mno-sse2` keeps neither `__SSE2__` nor
  `__AVX2__`: the w32 guard implies the w16 guard under gcc 15.2
  (`gcc -dM -E`, 2026-10-08).
- `[D155]` **Function bodies are the same text at every level.** Only
  WHICH definition of the FUNC is compiled changes. That is what lets
  runtime dispatch reuse the helpers unchanged (§R4.9.3.1).

**The deny, per row.** Each SIMD row has its own options.def row,
`MF_OPT("<form>-w<VW>", MF_OPT_DENY, <budget>, MF_L_SIMD, "...")`. Batch 1
has two: `vrun-w16` and `vrun-w32`. A width is not an ISA name, so the
names stay arch-blind, as options.def requires. Denying the wider row
leaves the narrower row as the site's top rung, which is exactly the
DISPLACED comparison (§R4.9.6). The layer switch `-fno-memfn-simd`
declines every SIMD row at once through `policy`, so there is no per-form
umbrella row (Q-R9-7).

**The stamp** (`[r9 C-9, F-15]`). A chosen SIMD row writes
`<id>@<level>+<level>…` in `MEMFN_FORMS` (§R4.3.3's grammar), with the
levels top-down: `vrun@w32+w16`. The stamp names the RENDERED levels,
never the live one: at the bench's default recipe `vrun@w32+w16` names a
w32 rung that is compiled out, and on a target with no level (the Mac at
batch 1) the stamp is non-`none` while nothing vector runs. That is
consistent with addendum 3 (`none` iff byte-identical to the SIMD-off
compile) and the `match_api.md` §6.3 hunk says it. Consumers still bucket
on `none`/not-`none` only. `[D155]` Under file-scope selection the stamp
still lists the RENDERED levels: one token per guarded helper block, top
to bottom of the selector chain. The scalar arm is never listed, because
every FUNC has it. At SIMD-off, and after R4e′.0b with no SIMD row, the
value is `none`. R4e′.0b moves no `MEMFN_FORMS` value. `vrun@w32+w16`
says the selector has a w32 arm and a w16 arm above `#else`, whatever
the consumer's `-march` compiles.

#### R4.9.2.4 Selection neutrality by construction `[r9 C-3]`

pcrec already has the mechanism: `pcrec_sb_len_uncut` (`src/core/sb.c`)
returns a buffer's length AS IF comments were on, by adding back the
bytes the comment gate dropped, and every length-based decision reads it
([EMIT-VERB] §3a). SIMD gets the mirror image:
- **Kit side** (batch 1's commit, folded into its one `MF_SITE_ABI` bump):
  two sink ops appended to `mf_sink`, `simd_open(u, level)` and
  `simd_close(u)`. The kit brackets every byte it writes inside a level
  guard with them, and writes the guard lines themselves inside the
  bracket. `[D155]` Guarded bytes are now WHOLE HELPER DEFINITIONS plus
  directives. Bracketed: each level's helper block, from its `#if` line
  through its `#endif` (the intrinsics `#include` included), and the
  selector's guarded parts inside the FUNC's body, from `#if <top guard>`
  through the `#else` line, plus the closing `#endif`. NOT bracketed: the
  FUNC's head and braces and the `#else` arm's one call, because they ARE
  the SIMD-off FUNC byte for byte. Because the
  SIMD-on source is the SIMD-off source with lines inserted (floor rule
  (c)), `len(ON) − simd_guarded = len(OFF)` holds exactly, not
  approximately. Measured on the probes, in the file-scope-definitions
  rendering that shape (c) superseded: 84 lines inserted, 0 deleted, for
  each of `(?i)cat` and `/user|/users` (§R4.9.2.5; (c) is re-counted by
  the first SIMD batch's C18).
- **pcrec side (RQ-3):** pcrec's sink counts bracketed bytes into the
  buffer's `simd_guarded`, and every length DECISION reads
  `len_uncut − simd_guarded`: the VM entry-shape knee, the `fit_rungs[]`
  size measurement, the size-quoting stamps. So `-fmemfn-simd` moves no
  rung, no ladder step and no stamp value by construction.
- **D84's refusal caps are a separate question** (Q-R9-9). Their purpose
  is the compile budget, and at `-march=L` the guarded text IS compiled.
  The recommendation is to EXCLUDE guarded bytes, so SIMD-on can never
  change a refusal, and to hold the compile bound instead by a per-row
  CONSTANT bound on guarded text (`mf_formdecl.guarded_max`, stated by
  the kit, checked by G2 over the generated site space): at most
  `nsites × max guarded_max` bytes ride beyond the cap. `[D155]` **RULED
  (a)** (D155 item 9). Under file-scope selection a row's `guarded_max`
  bounds its whole guarded footprint per FUNC: its helper definition, its
  level's `#include` line (written once per artifact per level, so it is
  at most once per FUNC), its selector arm (the chain's `#if`/`#elif` line plus one call),
  and its share of the directives. The seam's directive bytes per level
  are a constant the seam states; the row's bound includes that constant.
  The guarded bytes are now always whole helper definitions plus
  directives, never fragments inside the scalar text.
- **`RUN_WORDS` and `MEMFN_LIBC` under ON, declared:** the kit counts
  `RUN_WORDS` over UNBRACKETED text only, so it is equal ON vs OFF (the
  helpers reuse the floor's run compare row). `MEMFN_LIBC` scans the whole
  artifact; ON ⊇ OFF, and ON − OFF ⊆ the chosen rows' declared libc sets,
  which is ∅ for batch 1 (the helpers call no libc; their verify uses the
  same `rc_row` the floor uses, so a `memcmp` row there is already in
  OFF).
- C18 also detects a moved selection on every mover, since a moved rung
  changes UNGUARDED text.

**Batch 1's rows, in `fn_rows[]` order** (rows 1-2 new; 3-4 born at
R4e′.0):

| # | row | slot / layer / level | APPLIES (over `(site, pred, hooks)`) | reach | over | rungs | deny |
|---|---|---|---|---|---|---|---|
| 1 | `vrun-w32` | PREFIX / SIMD / w32 | `pred` is ONE term, a RUN of length ≥ 2 holding the scanned position, any mask; `pred` is the site's ONLY predicate (no lead, no set rest, no whole run); any handoff | `32 + T` | `fn-pair` `[r9fu]` | `vrun-w16` | `--memfn=no-vrun-w32` |
| 2 | `vrun-w16` | PREFIX / SIMD / w16 | the same | `16 + T` | `fn-pair` `[r9fu]` | — | `--memfn=no-vrun-w16` |
| 3 | `fn-pair` | BODY / SCALAR | the scanned position is a two-member cube (today's `b >= 0`); TWO glibc `memchr` streams | — | — | — | none (moves no byte) |
| 4 | `fn-memchr` | BODY / SCALAR | otherwise; ONE glibc `memchr` stream | — | — | — | none |

`[r9fu]` **Why `over` is `fn-pair` alone.** Both BODY rows are glibc-backed
(§R4.9.7.1), so each row's bar is "beat glibc's `memchr` plus the call"
(D147 addendum 13's trap). R-1 cleared that bar for `fn-pair` (its `emit`
column IS today's `fn-pair` text) and has no cell for `fn-memchr`. A
`fn-memchr` site therefore falls through walk test 4 (OVER, `PRED_FALSE`)
and renders as today. The first draft's `over` list named both rows. The
second row is filed with its cell (§R4.9.7's filed list); adding it later
is a one-cell `over` edit, not a new row.

A FUNC no PREFIX row takes renders exactly as today. `[D155]` After
R4e′.0b, that means the SIMD-off shape: `<fn>__body` plus the FUNC's one
call, with no directive (§R4.9.2.6). A site whose
predicate `ofs_fn_applies` declines (e.g. a scanned position that is a
four-member cube) has no FUNC part at all (the generic row renders it), so
the seam and its SIMD rows are never reached: the first draft's
"`kit_fail` or a shape outside C18" hole (`[r9 C-2]`) cannot occur.

#### R4.9.2.5 `[D155]` File-scope selection: the shape

Frank's amendment to Q-R9-6 (D155 item 6): *"no `#if`/`#ifdef` inside
function bodies. The SIMD choice lives at FILE SCOPE (per-level `static
inline` helpers selected by `#if`), and the body makes one plain call.
The SIMD-off artifact routes through the helper too — a one-time,
measured byte move and abi event — so the floor rule stays exact."*
Q-R9-10 RULED shape (c) (D155 addendum 1) restates the rule as *"a
function that does work never contains `#if`; a selector function's
whole body may be the `#if` chain, one call per arm, and nothing else."*

**SIMD-off, from step R4e′.0b on** (§R4.9.2.6). The BODY row's loop
becomes a helper, and the FUNC becomes one call:

```c
static inline size_t rx_reqrun__body(const unsigned char *subject, size_t n, size_t pos)
{
    <the BODY row's loop, byte for byte as today>
}

static inline size_t rx_reqrun(const unsigned char *subject, size_t n, size_t pos)
{
    return rx_reqrun__body(subject, n, pos);
}
```

**SIMD-on, batch 1** (`vrun-w32` chosen, rung `vrun-w16`; comments
elided; guards abbreviated to their `levels.def` tokens):

```c
<rx_reqrun__body, exactly as above>
#if <w16 guard>
#include <emmintrin.h>
static inline size_t rx_reqrun__w16(const unsigned char *subject, size_t n, size_t pos)
{
    if (pos >= n || n - pos < <reach w16>) return rx_reqrun__body(subject, n, pos);
    <the w16 block loop>
}
#endif
#if <w32 guard>
#include <immintrin.h>
static inline size_t rx_reqrun__w32(const unsigned char *subject, size_t n, size_t pos)
{
    if (pos >= n || n - pos < <reach w32>) return rx_reqrun__w16(subject, n, pos);
    <the w32 block loop>
}
#endif
static inline size_t rx_reqrun(const unsigned char *subject, size_t n, size_t pos)
{
#if <w32 guard>
    return rx_reqrun__w32(subject, n, pos);
#elif <w16 guard>
    return rx_reqrun__w16(subject, n, pos);
#else
    return rx_reqrun__body(subject, n, pos);
#endif
}
```

**The three pieces.**
1. **`<fn>__body`**, the scalar helper. It is the chosen BODY row's text
   (`fn-pair` or `fn-memchr`), byte for byte, under a renamed head. It is
   unguarded and always present, and it is the ONE scalar spelling in the
   artifact.
2. **`<fn>__w<VW>`**, one per RENDERED rung, inside that level's guard.
   Its text is the PREFIX row's. Its first statement is the entry test:
   the derived reach (§R4.9.3, a correctness bound) falls through to the
   next rendered rung's helper, or to `<fn>__body`. The seam hands the row
   that name, taken from the `rungs` data. So the ladder w32 → w16 →
   scalar is a chain of plain calls in the helpers' entry tests, with no
   directive, and no vector body ever runs a partial block. Blocks are
   written in ASCENDING level order, so each helper is defined before the
   one that falls to it (w32 falls to w16, which is defined above it),
   and the selector FUNC follows all of them.
3. **The selector: the FUNC `<fn>` itself, written ONCE** (`[D155]`
   Q-R9-10 RULED, shape (c)). Its head and braces are the SIMD-off FUNC's,
   and its WHOLE BODY is ONE `#if`/`#elif`/`#else`/`#endif` chain with
   exactly one plain call per arm, to that level's helper, and nothing
   else. The SEAM writes the chain from `levels.def`'s guard strings, top
   level first (the preprocessor's first match is the table's first
   match). A row never spells a guard. The `#else` arm's call is the
   SIMD-off FUNC's own line, byte for byte, which is what makes floor rule
   (c) hold. With no PREFIX row chosen there is no chain, only the
   SIMD-off FUNC's one call. This is the only place a function body holds
   a directive: a function that does work never contains `#if`.

Every helper has the FUNC's own parameter list, table parameters
included (`table_params`), so every call forwards the same argument list
and the STMT use lines do not change. The w32 guard implies the w16 guard
(gcc 15.2: `-mno-sse2` also removes `__AVX2__`), so w32's fall-through to
w16 always names a defined function. A rung skipped by the walk (denied,
or failing its reach at selection) is not rendered: the rung above it
falls through to the next rendered one, and the selector has no arm for
it.

**Ruled shape (c), and what it superseded.** Q-R9-10 asked how "the body
makes one plain call" is spelled. D155 addendum 1 RULED shape (c): the
FUNC is written once and its whole body is the chain (above). An
intermediate shape (b), a file-scope level macro, was ruled and then
superseded the same day by (c); it is not the rule. The probe measurements recorded
in this section (the 139 B, the identical `-O2` assembly, the 84 lines
inserted and 0 deleted) were taken on the file-scope-definitions rendering
that (c) replaces; (c) leaves SIMD-off byte-identical to it (the FUNC is
one call), so the +139 B stands, but the on-target equal-assembly and
insertion counts are re-measured by R4e′.0b's G1 and the first SIMD
batch's C18, not claimed here.

**Where the pieces sit, relative to `fn_rows[]` and the sinks.** The seam
(`ofs_fn_define`, §R4.9.2.1 item 3) writes all three pieces contiguously,
at the FUNC's current place: the same file-scope define sink
(`mf_define`) it writes the FUNC to today, in the order body, helper
blocks, selector. No new sink is needed, and nothing else in the
artifact moves relative to the FUNC. The BODY slot supplies piece 1's
text and the PREFIX slot supplies piece 2's helper texts (the chosen row,
then its named rungs, each re-walked). The seam writes the heads, the
entry tests' names, all directives and piece 3. `simd_open`/`simd_close`
bracket pieces 2 and 3's guarded parts (§R4.9.2.4).

**Several FUNCs in one artifact.** Nothing is shared between FUNCs: each
FUNC gets its own `<fn>__body`, its own helpers and its own selector,
because the helper texts carry that FUNC's constants (run bytes, masks,
offsets, table parameters). Two FUNCs at the same levels repeat the same
guard strings in their own chains.
- **Names** are the FUNC's own name plus a fixed suffix: `__body`, or
  `__` followed by the level's stamp token from `levels.def` (`__w16`,
  `__w32`; one source for the token).
- **The names are unique.** Every FUNC name is unique in its artifact
  and ends in one of pcrec's fixed FUNC suffixes (`_reqrun`,
  `_reqrun_whole`, `_ofsskip`). So no helper name can equal a FUNC name
  or another FUNC's helper name.
- **The double underscore** inside an identifier is legal in C, which
  reserves a leading `__` only. The helpers never reach the `.h`
  (`[r9 C-9]`), so a C++ includer never sees them.
- **Includes.** An intrinsics `#include` is written once per level per
  artifact, inside the first guarded block at that level (the `mf_art`
  remembers it, `[r9 C-7]`).

**The stamp.** It reports rendered levels, as before (§R4.9.2.3). One
token is listed per arm above `#else`, top-down.

**Probe evidence** (scratch, this lane, `gcc 15.2.0`, glibc 2.43, the dev
box, `taskset -c 12-15`. The transcript is `../../dev/lanes/r9d_report.md`
"revision D155". The inputs are the kit tip's own emitted witnesses from
r9fu, re-rendered by a script in each shape. The vector helpers are
r9fu's hand twin, not kit renders. No timing was taken.)
- **SIMD-off costs nothing at `-O2`/`-O3`.**
  - Inputs: twelve witness artifacts, every r9fu artifact with a FUNC
    (eleven PRE `rx_reqrun`, one OFS `rx_ofsskip`).
  - Method: each compiled `-S` as today and as both new shapes. The
    whole-file assembly was compared after renumbering gcc's
    `.LFB`/`.LFE` per-function counters (one more function shifts every
    later index).
  - Result: `-O2` 12/12 IDENTICAL and `-O3` 12/12 IDENTICAL, in both
    shapes. No `__body` symbol survives.
  - `-Os`: 9/12 identical.
    - `(a|b)+xyzzy` and `(?i)(a|b)+cat` differ only in a NAME. At `-Os`
      gcc already keeps today's FUNC out of line at its two call sites,
      and that out-of-line copy is now called `rx_reqrun__body`.
    - `(?i)union.*?select.*?from --engine=vm` differs in one register
      choice across two instructions.
  - `-O0`: one more call per FUNC call (1 → 2). `-O0` inlines nothing
    today either.
- **Every level combination compiles clean.**
  - 144 compiles: two witnesses × (two shapes + two controls) × nine
    flag sets × `-O0`/`-O2`.
  - Flag sets: `-mgeneral-regs-only`, default x86-64, `x86-64-v2`,
    `sandybridge`, `x86-64-v3`, `x86-64-v4`, `-mno-sse2`,
    `-mavx2 -mno-sse2`, `-mgeneral-regs-only -march=x86-64-v3`. All
    with `-Wall -Wextra`.
  - Result: 0 errors, and 0 warnings outside one control.
  - The controls cover the unused-helper case. In the first, w32 falls
    straight to `__body`, so the w16 helper is defined and UNUSED at
    v3/v4. As `static inline`, gcc says nothing. In the second, the same
    helper is declared plain `static`, and it draws `-Wunused-function`
    at v3 and v4 (8 of 8 such compiles). So the warning is live, and
    `static inline` on every helper is what keeps a skipped arm silent.
- `[r9b]` **All figures below were taken on the file-scope-definitions
  rendering that (c) superseded, unless marked.** This covers the 144
  compiles, the `-O2` inlining, the instruction counts (336/418,
  279/363) and the 15,884,000-call differential.
- **C18 on the new shape.** `[D155]` Measured on the file-scope-definitions
  rendering that Q-R9-10's shape (c) superseded; (c) changes where the
  chain sits (inside the FUNC's body), not the helpers, and is re-measured
  by R4e′.0b's G1 and the first batch's C18.
  - (a) EQUAL, 12 of 12 (two witnesses × two shapes × three flag sets).
  - (b) At default, v3 and v4: exactly ONE deleted line per comparison,
    the selected call `return <fn>__body(subject, n, pos);`. Inserted:
    3,236 lines at default (`<emmintrin.h>`), about 45,800 at v3/v4.
  - (c) The source diff deletes 0 lines (4 of 4).
- **On-target code.**
  - At `-O2`, every helper inlines into `rx_search` at every level (no
    helper symbol remains).
  - Instruction counts: `(?i)cat` default/v3 336/418, `/user|/users`
    279/363. r9fu's twin of the WITHDRAWN shape (rungs inside the body)
    counted 337/423 and 276/356. So the counts are close but not
    identical: a code-generation difference to keep in mind for F-R9-1's
    objdump report.
- **Answers.**
  - A differential over 15,884,000 calls per build: random subjects of
    length 0..130 over each pattern's alphabet, every `pos`.
  - Builds: today, both OFF shapes and both ON shapes, at default, v3, v4
    and `-mgeneral-regs-only`.
  - Result: ONE result hash per witness across every build.

#### R4.9.2.6 `[D155]` Step R4e′.0b: the routing byte move, an abi event, and its G1 measurement

**What moves.** Every artifact with a FUNC part, i.e. every
`ofs_fn_define` call: PRE `<p>_reqrun`, `<p>_reqrun_whole` and OFS
`<p>_ofsskip`.
- Each FUNC's loop moves, unchanged, under the head `<fn>__body`, and the
  FUNC becomes one call (§R4.9.2.5's SIMD-off shape).
- Nothing else moves, and no comment line is added.
- Measured on the twelve witnesses (`[r9b]` the pre-(c) rendering; re-measured by G1): +139 B per FUNC (+141 for
  `rx_ofsskip`, whose name is two bytes longer).

**Why a step of its own**, between the seam R4e′.0 and batch 1:
- R4e′.0 stays ZERO-MOVER. The table refactor is checked by identity,
  and that check is only meaningful while nothing moves.
- R4e′.0b is the one byte move, checked by its own census.
- Batch 1 then adds only guarded text (floor rule (c)).

So there is one event per commit, implement-then-replace.

**It is a pcrec abi event, in the kit's commit.**
- A kit byte move is a pcrec abi event (root CLAUDE.md, D76/D94).
  pcrec's abi takes "the next number at landing", never a literal.
- Every reader of the number is found BY GREP, the identity gates are
  re-pinned, and `make test-codegen` plus the suites that count are run.
  This is RQ-6.
- It is not an `MF_SITE_ABI` event: no contract field changes. No
  `MEMFN_FORMS`, `RUN_WORDS` or `MEMFN_LIBC` value moves.
- The FUNC and its helper are `static`, so no entry a caller links
  against changes. D80's spec obligation is the abi number's own spec
  readers, found by the same grep.
- **Q49 is amended for this step only.** "No abi bump at SIMD-off, no
  default byte moves" still holds for batch 1 and every later SIMD row.
  R4e′.0b is the single exception, the one D155 ordered.

**The measurement plan (G1, both layers).** "`static inline` must cost
nothing, so measure it":
1. **The mover census** comes from pcrec, not the kit.
   - `emit_sweep`'s streams are compared with the parent's.
   - The movers must be exactly the artifacts with a FUNC part, by id,
     counted against the seam's `fn` census by customer (K35 floor).
   - Each mover's text diff must be exactly the routing. A script checks
     this: rename `<fn>__body` back and drop the forwarder, and the
     result equals the parent byte for byte. Any other moved byte is red.
2. **Object identity** is the "costs nothing" claim, stated as a fact.
   - Every mover is compiled at the bench recipe (`-O2`, default
     `-march`) and at `-O2 -march=x86-64-v3`.
   - Its assembly is compared with the parent's, with gcc's function
     counters renumbered and the helper symbol name normalized.
   - The probes predict IDENTICAL on every mover at `-O2`. Each
     non-identical mover is listed with its diff.
   - `-Os` and `-O0` are reported but do not gate (the probes show one
     register difference in 12 at `-Os`, and one more call at `-O0`; `[r9b]` safe:
     the SIMD-off text is identical in shapes (b) and (c);
     [GUIDE-OPT-LEVEL] recommends `-O2`).
3. **Timing applies only where item 2 is not identical.**
   - A mover with identical code at a recipe runs the same instructions,
     so the report says so and does not time identical binaries.
   - Each non-identical mover gets a tier-U pair (RQ-4's slot): parent vs
     routed, both regimes (§R4.9.5). The identical movers are its null
     population, and they must read null (that is the control).
   - A non-null cell goes to the bench (the RQ-5 path) and lands only as
     a recorded, accepted cost.
4. **Both layers.**
   - The reading is taken at `-fno-memfn-simd` and at `-fmemfn-simd`.
   - At R4e′.0b no SIMD row exists, so the two artifacts are
     byte-identical (C11's identity half), and the SIMD-on reading IS
     that identity.
   - From batch 1 on, the SIMD-on layer is judged against this routed
     SIMD-off (§R4.9.6), never against the pre-routing text.

> **`[R4e′.0b]` BUILT** (lane r4e0b, 2026-10-09, request R-11;
> `docs/dev/lanes/r4e0b_report.md`). pcrec abi 69 -> 70 (the pcrec manager
> assigned 70; 69 is another lane's event). As built:
> - The seam `ofs_fn_define` writes the BODY row's loop under `fn_head`'s
>   head as `<fn>__body`, then the PREFIX row's helpers (none), then
>   `fn_selector`'s `<fn>`: `return <fn>__body(subject, n, pos[, tables]);`.
>   The PREFIX walk is handed the helper's name (`fn_in.body_fn`). A later
>   PREFIX row adds `#if` arms above that call without touching the BODY
>   text. No options.def deny: the routing is the floor shape D155 ordered,
>   measured once against its parent (this section), not an arm with an OFF.
> - **G1, measured** (`probes/r4e0b/`, every corpus row and composition
>   file, four `.c` streams, gcc 15.2, the dev box): 0 OTHER and 0
>   ASYMMETRIC; every FUNC-bearing artifact un-routes to the parent byte for
>   byte, and the movers are exactly the parent artifacts holding a FUNC
>   (3,334 artifact-streams; the `--emit-ir` listings identical, headers abi
>   digits only). The delta per FUNC is 121 + 2 x len(name) plus its tables
>   (rx_reqrun +139, rx_ofsskip +141, rx_reqrun_whole +151; 203 table-bearing
>   ofsskips +184), as predicted on every mover.
> - **Assembly is NOT identical on every mover**, against the prediction:
>   2,126 of 2,452 movers identical at `-O2` and at `-O2 -march=x86-64-v3`;
>   326 differ at both, 11 `byte` ones by block order alone (the same
>   instructions), 315 `-e utf8` ones by the K50 guard's error return taking
>   its own epilogue (typically +7 instructions on the cold `startpos`
>   path), 0 VM-forced. `-Os` (sampled) 4 of 127 differ; `-O0` all differ
>   (one more call).
> - **Timing, only for those** (tier U, one core, 7 alternated runs,
>   find-all on 64 KiB and 64-byte calls): all 227 distinct patterns read
>   null, every ratio inside its own run-to-run spread (utf8 medians 1.000
>   thr / 1.001 call); identical-assembly controls read the same.

### R4.9.3 Cascades and the short-span path

**Three ways a level is picked.**

| mode | where the pick happens | text | when |
|---|---|---|---|
| compile-time ladder | the consumer's compiler, from predefined macros (`-march`) | ~~§R4.9.2's dispatch prefix~~ `[D155]` §R4.9.2.5's file-scope selector, plus the helpers' entry tests | the DEFAULT for every SIMD row; batch 1 |
| run-time cascade (K-6) | the artifact at each call, `__builtin_cpu_supports` | a separate row (below); `[D155]` now `[MEMFN-RTDISPATCH]`'s shape, §R4.9.3.1 | only on its own trigger; FILED |
| none | — | the floor alone | SIMD off; or no SIMD row applies |

The ladder needs no state, holds no static and costs one compare per
rung per call. `[D155]` That compare is now each helper's ENTRY TEST, so
a call that falls through pays one compare per rendered rung and one
call per rung (inlined at `-O2`, measured on the superseded rendering, §R4.9.2.5). The consumer's `-march` decides what runs: at the
bench's recipe (`-O2`, no `-march`), x86-64 defines `__SSE2__` and no
wider predefined ISA macro (measured with `gcc -dM -E`), so batch 1's w16 row is
the live arm and w32 is compiled out. At `-march=x86-64-v3`, w32 is live
and w16 is its short path. This is why `-march` is a dimension of the
measurement regime (§R4.9.5 item 4) and of the bench recipe (Q-R9-2).

**The short-span path is the next rung, by a DERIVED reach.**
- `[r9 C-1]` **T is defined ONCE**: T = `max_reach(pred)`, the highest
  byte offset the predicate reads relative to the candidate, the same
  derivation the BODY's own loop guard (`pos + maxk < n`) already uses
  (`memfn/src/ofsskip.c`). For a run at offset 0, T = L − 1. The first
  draft's second definition ("the run term's extent beyond the scanned
  byte", which reads as L − 1 − KA) is WITHDRAWN: on union-select it gave
  a w16 reach of 17 instead of 21 and an over-read of up to 4 bytes past
  `n`.
- **reach = VW + T, derived from the HIGHEST READ.** A vector block at
  base `i` covers candidates `i..i+VW−1`. The pair filter's second load
  reads `[i+KB, i+KB+VW)` with `KB ≤ T`, and the in-block verify of lane
  VW−1 reads up to `i+VW−1+T`. Both need `n − i ≥ VW + T`, so that is the
  smallest span the body reads one full block of. It is a CORRECTNESS
  bound (D149: DERIVED), not a performance cut-over (`[r9 M-9]`).
- **Static decline.** Where pcrec's facts prove `span_hi < reach`, the
  row declines at selection (walk test 3) and the FUNC carries no rung.
  `MF_SPAN_UNBOUNDED` passes, so an unbounded site is never falsely
  declined.
- **Dynamic.** At run time, `n − pos < reach` falls through ~~the prefix~~
  `[D155]` the helper's entry test to the next rung's helper, and finally
  to `<fn>__body`. So w32 → w16 → scalar, and
  no vector body ever runs a partial block.
- **R-1's 16 B finding re-read (F-R9-1).** At 16 B every row falls to
  the BODY by construction. What remains is the ~~prefix's~~ `[D155]`
  entry tests' compare-and-branch plus any code-generation effect, read against the null
  population (§R4.9.5 item 6).
- **Performance cut-overs ABOVE the reach are tuning constants**
  (`[r9 M-9]`). Two are swept, not one: w32-over-w16 AND w16-over-scalar,
  each at `{reach, 2·reach, 4·reach}`, at the level where the pair
  meets. They are picked in the UNOFFICIAL tier (§R4.9.5), labelled
  `MEASURED-UNOFFICIAL (<CPU class>)` in place, and become MEASURED only
  on an official bench reading. Until then the derived minimum ships and
  no other number is written (D149).
- **The loop-free tier below the narrowest vector width** (RB-4) is a
  SCALAR-layer form. The BODY provides it if the scalar row has it. A SIMD
  row carries no private scalar short path (the floor rule).

**The run-time cascade (K-6), designed and FILED.** Its one purpose is to
let a binary built at a LOW `-march` (the bench's recipe, most
consumers') use a wider level on a CPU that has it. `[D155]` Its SHAPE
below (a prefix rung inside the FUNC body) is WITHDRAWN by the amendment.
Its guard, its cost, its libgcc dependency (Q-R9-8, RULED) and its bar
stand, as inputs to `[MEMFN-RTDISPATCH]`, whose terms D155 states and
whose shape §R4.9.3.1 shows. The text below is kept as the r9 record.
- `[r9 C-4]` **A separate PREFIX row**, e.g. `vrun-rt`, placed ABOVE
  `vrun-w32` in `fn_rows[]`, naming rungs `vrun-w32`, `vrun-w16`, so it
  renders ABOVE the FULL compile-time ladder: cascade, w32, w16, floor.
  Its text lives in one guard, `defined(__x86_64__) && !defined(__ILP32__)
  && defined(__SSE2__) && defined(__linux__) && defined(__GNUC__) &&
  !defined(__AVX2__)`:
  - a helper defined with `__attribute__((target("avx2")))`;
  - a prefix rung `if (n − pos ≥ reach && __builtin_cpu_supports("avx2"))
    return helper(...)`.

  The `defined(__SSE2__)` conjunct is load-bearing: without it the guard
  is TRUE under `-mgeneral-regs-only`, `-mno-sse`, `-mno-sse2` and
  `-mno-avx` (the panel's probe compiled under all four), C18 is red on
  every cascade mover, and a kernel or freestanding build runs an AVX2
  helper that clobbers ymm state. "The compile-time top level is absent"
  is the guard's `!defined(__AVX2__)`, a property of the consumer's
  compile, never a kit fact (the kit is arch-blind at render time): the
  cascade's place in the table is a row-ORDER fact. At `-march=x86-64-v3`
  the cascade compiles out and w32 is live; the stamp lists rendered
  rungs, `vrun-rt@w32+w16` (C-9).
- **Its cost, named in its regime** (K-6): detection 0.44-0.59 ns; per
  call +0 under gcc and +0.9-1.3 ns under clang over a direct call
  (linux_results.md §2, Zen 1, unofficial). Darwin is excluded by the
  guard: `__builtin_cpu_supports` answers 0 for every feature on
  Darwin/AArch64 (isa_selection.md §0 item 3). Reading a cached word in
  the artifact is forbidden (`match_api.md` §5.3).
- **Its dependency** (`[r9 C-4]`, Q-R9-8). `__builtin_cpu_supports` reads
  libgcc's `__cpu_model` (initialized by a libgcc constructor). A
  cascade artifact therefore needs libgcc at LINK time (static
  `libgcc.a` or `libgcc_s`): a `-nostdlib` or freestanding link fails
  with an undefined `__cpu_model`. requirements.md N-4 forbids that for
  the portable forms; under SIMD-on it is Q-R9-8, and the spec states it.
  A call before the constructor reads a zero model and falls to w16 or
  the floor, which is safe.
- **Its bar.** It must beat the single-level row it displaces (w16 at
  default `-march`) on the official boxes, in both regimes. It must also
  beat the current scalar layer (transitively, through w16's acceptance).
- **Its trigger (D77).** An unofficial probe cell: R-1's harness with a
  `cas` variant, built at the bench's recipe, beating `ffl` SSE2 past the
  null band in both regimes at a batch-1 cell. Batch 1's lane MAY run
  this probe as measurement only. A met trigger is a later batch's row.

#### R4.9.3.1 `[D155]` Runtime dispatch (`[MEMFN-RTDISPATCH]`, FILED): what the same helpers already serve

D155 FILES runtime dispatch (plan row `[MEMFN-RTDISPATCH]`, not
scheduled). Its trigger (D77): more than one architecture selected for
runtime support AND a hot-loop SIMD form exists. No dispatcher is
designed here. This subsection shows that §R4.9.2.5's shape does not
preclude the row's terms, and where each term would land.

**1. Each site states a frequency class.**
- An INFREQUENT site (about once per search call) may choose its level
  at run time.
- A FREQUENT site (inside a pcrec-owned loop) never pays a hardware
  check. It takes a STATIC choice: the lowest common denominator of the
  selected set, or a named level.
- The class is a SITE fact, and pcrec states it, because only pcrec knows
  where it calls the FUNC (D146).
- **Finding: the class is NOT `MF_P_INLOOP`.**
  - C10 sets `MF_P_INLOOP` only from D91's budget column, which puts OFS
    in budget 1, i.e. not in-loop. A budget says how long ONE call may
    run (an OFS call is a scan).
  - r9fu measured that the OFS FUNC is CALLED inside the DFA scan loop,
    on every re-seed (§R4.9.7.2).
  - So frequency is a second fact, not a reading of the first. That is
    Q-R9-11, RULED (D155 addendum 1): a `freq` column in `DELEG_SITES`,
    built only when `[MEMFN-RTDISPATCH]` triggers, kit-decided.

The first-batch sites, and the filed one, from r9fu's artifact lines:

| site (FUNC) | where pcrec calls it | frequency class | under runtime dispatch |
|---|---|---|---|
| PRE window `<p>_reqrun`, DFA route, ASSIGN (batch 1) | once, at `rx_search` entry (`(?i)cat` l.79) | INFREQUENT | may choose its level at run time |
| PRE window, DFA without handoff, and no-DFA ON_MISS (batch 1) | once (`\d+xyzzy` l.70; `(?i)union…` `--engine=vm` l.312) | INFREQUENT | the same |
| PRE window, VM hybrid (batch 1) | once, before the prefilter and the attempt loop (`(a\|b)+xyzzy` l.387). The hybrid's re-seed calls `rx_prefilter`, not the FUNC | INFREQUENT | the same |
| filed `vrun` over `fn-memchr`: OFS `<p>_ofsskip`, run-pinned | INSIDE `rx_search`'s DFA scan `for (;;)`, on every re-seed (`/user\|/users` l.132) | FREQUENT | static choice only |

**2. Per-level copies by target attribute, chosen once.**
- A level ABOVE the consumer's compile-time level gets a second copy of
  the SAME helper text. The copy sits under a dispatch guard (the level's
  macro ABSENT, plus `__SSE2__`, `__x86_64__`, not ILP32, Linux, GNUC:
  C-4's guard) and carries `__attribute__((target("<level>")))` on its
  head.
- The FUNC's selector gains one arm under that guard, for an INFREQUENT
  site only. The arm's body is still ONE plain call, to a per-FUNC
  dispatcher helper (`<fn>__rt`, NOT designed here). That helper chooses
  once, D155's "selected once", and calls a level helper.
- A FREQUENT site gets no runtime arm. Its selector stays the static
  chain.

Probe (scratch, `(?i)cat`; `[r9b]` ran in the same probe set as the
static probes, on the superseded file-scope-definitions rendering, per
r9d_report.md "Probes"; not re-run on shape (c)):
- The w32 helper under the static guard and its copy under the dispatch
  guard are the same text except for the attribute.
- With a stand-in arm (`__builtin_cpu_supports("avx2") ? w32 : w16`,
  used for the compile only, not the design), the file compiles clean
  under `-Wall -Wextra` at default, `x86-64-v3` and
  `-mgeneral-regs-only`.
- The answers match at default and v3: the same hash as every static
  build over 15,884,000 calls.
- At default, gcc does NOT inline the target-attributed helpers into the
  default-target caller. `rx_reqrun__w16` and `rx_reqrun__w32` stay out of
  line, so a dispatched site pays a real call per FUNC call. That is
  acceptable only where the FUNC is called about once per search, which
  is D155's frequency rule reached from the other side.
- The floor rule holds for the runtime block, which is guarded text:
  (a) is EQUAL at `-mgeneral-regs-only` and at `-mno-sse2`, and the
  source diff deletes 0 lines.

**3. A compile-time level set that need not cascade.**
- The set is DATA: the rendered rungs, i.e. the chosen row's `rungs`
  filtered by the walk.
- Each helper's entry test names the next RENDERED rung, or `<fn>__body`.
  So "AVX-512 or scalar" renders one wide helper that falls straight to
  `__body`, with no w32 or w16 between.
- Probe: the control in which w32 falls straight to `__body` compiles
  clean at all nine flag sets. The skipped helper is silent because it
  is `static inline` (§R4.9.2.5).
- A FREQUENT site's static choice is the same mechanism:
  - "The lowest common denominator" is the selector compiled at the set's
    lowest `-march` (the usual runtime-dispatch recipe).
  - "A named level" is a selector arm that calls that level's helper with
    no check.
  - Either one only changes which helper the FUNC's one call names.
    Choosing between them is the row's ruling, not this design's.

**4. Per-architecture separate artifacts already work.** Compile the same
SIMD-on artifact once per `-march` (one `lib.so` per `-march`, chosen at
load): the selector takes the matching arm in each compile, and pcrec
needs nothing.
- Measured (`[r9b]` superseded rendering): the same source at default, v3 and v4 compiles to three
  different arms (`pcmpeqb` 4/8/8, `ymm` 0/18/18 for `(?i)cat`).
- The answers are identical.

**What the row inherits from this design, unchanged:**
- the helper names and texts;
- the floor rule and C18 (a runtime block is a guarded block);
- RQ-3's bracket accounting;
- Q-R9-8's libgcc dependency, RULED (D155 item 8).

What it must design:
- the dispatcher helper;
- its once-only choice, without a mutable static in the artifact
  (`match_api.md` §5.3: TS-1 forbids one, so "chosen once" has to be a
  resolver the loader runs, or a caller-held choice;
  `isa_evaluation.md`'s hoisted pick);
- the frequency-class fact (Q-R9-11, RULED: the `freq` column of
  `DELEG_SITES`, built here at the trigger).

The mutable-static constraint is RECORDED here as the one hard problem
the row has. It is not solved here.

### R4.9.4 The `-fmemfn-simd` axis: BUILT and inert; what pcrec owes

**Built** (R4c lane AXIS, 2026-10-06; read at main 5ddd2f04):
- `src/core/axes.def` has `PCREC_AXIS(PCREC_NO_MEMFN_SIMD,
  "-fno-memfn-simd", PCREC_FORCE_MEMFN_SIMD, "-fmemfn-simd",
  PCREC_AXIS_DEFAULT_OFF)` (bits 48/49).
- Both bits are masked out of `rx_info.flags` (`strategy_denials`).
- `pcrec_memfn_policy(flags)` (`src/gen/memfn_stamps.c`) sets
  `MF_P_PORTABLE_ONLY` iff the force bit is not in force, and every
  site's `policy` reads it (`src/gen/memfn_sites.c`).
- `docs/spec/tuning.md` §2.43 states the meaning and "INERT before
  R4e′".
- C11's identity half prints "identical (no SIMD form)".
- `--list-axes` prints the `memfn` section from `mf_options()`.

pcrec needs NO new axis, no `--isa=`, no `-march` knob and no ISA fact for
the SIMD layer. The seam (R4e′.0) lands entirely in `memfn/` and
`tests/memfn/`. Batch 1 lands in `memfn/`, `tests/memfn/` and
`docs/spec/`, plus RQ-3's pcrec-side length readers (Q49: no abi bump at
SIMD-off, no default byte moves). `[D155]` One exception precedes batch 1:
step R4e′.0b, the routing byte move. It is a pcrec abi event at SIMD-off,
carried by RQ-6 (§R4.9.2.6).

**Owed by pcrec, as later requests** (named here, not designed;
§R4.9.11):
- RQ-1, the `--memfn=` carrier (F-R9-6). A prerequisite of batch 1 (its
  two denies) and of R4d.
- RQ-2, a second filter position as a pcrec fact (Q-R9-3 (a)).
- RQ-3, SIMD bytes neutral to pcrec's length decisions (`[r9 C-3]`: now a
  PREREQUISITE of batch 1, no longer conditional on a census).
- RQ-4, the dev box's slot for the UNOFFICIAL tier (`[r9 M-1]` demoted).
- RQ-5, the bench SUBMISSION for batch 1's official verdicts
  (`[r9 M-1, M-4]`: before acceptance, not at landing).
- `[D155]` RQ-6, R4e′.0b's abi event on pcrec's side: the bump, the
  readers found by grep, the identity re-pin, and the G1 object-identity
  census (§R4.9.2.6).

### R4.9.5 The measurement regime: two tiers `[r9 M-1]`

Every SIMD reading belongs to exactly one TIER, and says which (D144
addendum 4). The first draft made the dev box the "verdict box" (its
Q-R9-1 (a)). That is withdrawn: the dev box is a bench box, and a verdict
is a bench run, on every box the form's level targets.

**Tier U, UNOFFICIAL (directional).** Any harness, any box: the kit's
probes (R-1's co-linked shape), a lane's alpha script, a dev-box
`taskset` run, a Mac scratch run. A reading names its sub-class: U-Mac
(aarch64; floor text only at batch 1), U-dev (7700X, Zen 4), U-budu
(ubuntubudu through a manager slot with the kit's harness: the SAME CPU
as the bench, NOT the bench's harness). Tier U decides:
- D77 TRIGGERS (a cell justifies building) and which rows to SUBMIT;
- the CONSTANTS to submit: the reach, unroll and KB sweeps run here first
  to cut the bench's arm count;
- a VETO on submission: a U-dev or U-budu loss past its null band means
  do not spend a bench slot, unless a stated Zen 1 / Zen 4 hypothesis says
  otherwise.
Tier U NEVER grants acceptance, never labels a constant MEASURED (only
MEASURED-UNOFFICIAL), never sets a default, and is never quoted as a
verdict (D144 addendum 1's "directional" rule, extended past the Mac).

**Correctness is CPU-independent and decisive in any tier**: the answer
sweep per level, G2 per level, ASan/UBSan, I2 zero movers, C9-x86, C18
and C-SEL. They run wherever they run; the dev box OWNS AVX-512
correctness (the only box that executes it).

**Tier O, OFFICIAL (the verdict).** A planned pcrec-bench run, built from
a pcrec commit the bench pins, on EACH box that executes the row's
level, pre-registered (§R4.9.5.1). The kit never writes to pcrec-bench:
a batch's acceptance comes to the pcrec manager as a bench request (the
kit's `responses.md` notice), and main carries it to the bench inbox
(`inbox_from_pcrec.md`, one `[inbox]` commit, D78) and schedules the
boxes (on the dev box through main's slot channel, one heavy run at a
time; D144 addendum 4).

| level | official boxes (D144 addendum 4) | why |
|---|---|---|
| w16 (SSE2) | ubuntubudu (Zen 1) AND the dev box (Zen 4) | the widest reach: every x86-64 consumer, the bench's default recipe |
| w32 (AVX2) | ubuntubudu AND the dev box | Zen 1's 2×128 execution is exactly what the bench must show; Zen 4 is native |
| w64 (AVX-512, filed) | the dev box | the only box that executes it; judged there alone (not "unofficial-only": the dev box is a bench box) |
| aarch64 (filed) | the Mac | under addendum 8 only: Mac verdicts admitted, or an aarch64 Linux box |

The protocol items below apply to EVERY reading; where tier O differs it
says so.

1. **The boxes and the header.** Each transcript header records the CPU
   model and class (`zen1` / `zen4` / `m1`), governor, boost, glibc, gcc,
   pcrec and kit commits (and the bench commit in tier O), `-march` and
   `-mtune`, and load1 at start and before each launch (wait for < 0.5).
   `[r9 F-14]` The governor at launch is recorded because bench O-69
   traced a per-process split to it (the [EMIT-ALIGN] row, NOT TRIGGERED,
   names that cause rather than layout).
2. **Pinning (tier U on the dev box; tier O is the bench's discipline,
   asked of the bench dev, `[r9 M-14]`).** `taskset -c C` on one logical
   CPU, its SMT sibling read from `/sys/devices/system/cpu/cpuC/topology/
   thread_siblings_list` (never a `C ± 8` rule: the bench box is 6c/12t)
   and held idle. Per launch the transcript records the sibling's busy%
   (from `/proc/stat` deltas) and the pinned CPU's effective frequency,
   and a launch above a stated sibling-busy figure (`UNMEASURED DEFAULT:`
   5%) is discarded. Main's quiet slot (RQ-4) is a noise reducer, not a
   guarantee.
3. **Programs.** Each arm is its OWN binary built from the pcrec-emitted
   artifact (the `alpha_k82.sh` shape). Variants are never co-linked in
   one binary for a verdict. R-1's co-linked harness stays a tier-U probe
   and trigger instrument.
4. **Arms, at each `-march` level L the row is live at** (batch 1: L ∈
   {default x86-64, x86-64-v3}; v4 is a tier-U report until a w64 row
   exists):
   - OFF = the `-fno-memfn-simd` artifact built at L (the CURRENT scalar
     layer at that commit and that `-march`, F-R9-2);
   - ON = `-fmemfn-simd` at L;
   - DENY = `-fmemfn-simd --memfn=no-<row>` at L. For a lone row its text
     is asserted byte-identical to OFF before any timing; it is a
     same-text pair on the very mover cells;
   - DISPLACED, for a row that displaces a SIMD row (w32 over w16) =
     `-fmemfn-simd --memfn=no-vrun-w32` at L.
   - `[r9 M-4]` Every recipe is `-O2 -march=<named level> -mtune=generic`,
     NEVER `-march=native`: native on Zen 1 and Zen 4 are different
     binaries with different macro sets, so the two CPUs would not run the
     same bytes. A named level lets one build run on both.
   - Arms are INTERLEAVED (ABAB) inside each launch (`[r9 M-5]`): boost on
     Zen 4 depends on the active core count, so un-interleaved drift falls
     on one arm.
5. **The floor and the noise band are the NULL POPULATION** (`[r9 M-5,
   M-6]`). Every non-mover artifact in the submitted set is byte-identical
   OFF vs ON (the floor rule). Its ON − OFF delta distribution, per regime
   and per CPU class, measured in the same run and the same binary set, IS
   the placement-plus-noise band (b1ledger's null control: 56 of 187
   program-identical artifacts, with regressions up to +8.46% on identical
   `__text`). The FLOOR is a high quantile of it (`UNMEASURED DEFAULT:` the
   maximum over the null cells, per regime and CPU class, until the null
   distribution itself supports a quantile). `|DENY − OFF|` on the movers
   is reported beside it as a second same-text reading, never as the
   threshold.
6. **No alignment-flag band** (`[r9 M-6]`). The first draft's relink with
   `-falign-functions=64 -falign-loops=32` is WITHDRAWN: one alternative
   layout is a single draw, the flags re-align the whole binary including
   the harness, and 64/32 were unlabelled constants. Its job (separating
   placement from a real per-call cost) is the null population's. A
   below-reach per-call cell measures the dispatch prefix (`[D155]` now the
   selector's call plus the helpers' entry tests); a median shift
   outside the null band there is a LOSS even if each launch alone sits
   inside it (K81 and K85's +1..+9 ns entry terms were real).
7. **Regimes** (both, every cell; §21.1):
   - THROUGHPUT: gate (one call from 0) and sweep (find-all), at 64 KiB
     and 1 MiB, on subjects hit-sparse and hit-dense for the cell;
   - PER-CALL: `short75` and pc16/pc64/pc256/pc1024, each marked BELOW or
     ABOVE the row's reach. `[r9 M-4]` The bench has no per-call span
     cells today, so the submission REQUESTS a span-ladder subbench
     (§R4.9.5.1); until it exists the per-call leg is tier U and labelled
     so;
   - `[r9 M-10]` DENSITY: a hit-spacing ladder (8, 16, 32, 64, 128, 256 B
     between hits) as a synthetic witness cell in BOTH tiers. Batch 1's
     density bound is what that ladder covers; a loss past the floor at a
     spacing on an official box blocks or narrows the row (§R4.9.6).
8. **Loops and statistic.** Each timed loop ≥ ~50 ms, min of 3 loops per
   launch, median of 3 launches (`UNMEASURED DEFAULT:` 3 × 3, R-1's). Each
   reading reports the NUMBER of cells tested, so the multiple-comparison
   exposure is visible (`[r9 M-5]`). Absolute ns; a ratio only for
   throughput cells well above the timer floor (D144 addendum 1).
9. **Both layers** (D147).
   - The SIMD-OFF reading of a SIMD batch is ZERO MOVERS: I2 at
     `-fno-memfn-simd` against the parent commit, every axis and both
     comment tiers (§17.1). A SIMD-off mover in a SIMD batch is a defect,
     not a reading.
   - The SIMD-ON reading is the verdict (§R4.9.6).
   - aarch64 (addendum 8): batch 1 has no aarch64 level, so a Mac build
     of a SIMD-on artifact compiles to the floor. Mac runs check SIMD-off
     text answers only; its "movers" are TEXT movers (the stamp), F-15.
   - clang: compile correctness where installed (ubuntubudu, the Mac);
     never a timing verdict. The dev box has no clang.
10. **D149: every constant in batch 1's form, split by kind** (`[r9 M-9]`).

| constant | kind | status in batch 1 |
|---|---|---|
| vector width VW | correctness bound | DERIVED: the level's register width (`levels.def`) |
| T | correctness bound | DERIVED: `max_reach(pred)` (C-1), L − 1 for a run at offset 0 |
| reach (the short path) | correctness bound | DERIVED: `VW + T`, the smallest span the body reads one full block of |
| w16-over-scalar cut-over above reach | performance | SWEPT in tier U at `{reach, 2·reach, 4·reach}`; MEASURED-UNOFFICIAL until tier O; the derived reach ships until then |
| w32-over-w16 cut-over above reach | performance | the same, at `-march=x86-64-v3` |
| main-loop unroll | performance | SWEPT in tier U at 1×, 2×, 4× per level, or the plain 1× loop shipped and labelled `UNMEASURED DEFAULT:`. "Left to the compiler" is not available for an intrinsic loop (`[r9 M-9]`). Never 2× silently |
| scan position KA | site fact | DERIVED: `plan_hint`/`plan_pos` (§14.9), pcrec's fact |
| second filter position KB | site fact | pcrec's fact under Q-R9-3 (a) (`mf_pred.plan_pos2`, RQ-2) |
| lead order | — | not applicable: batch 1 has no lead |
| density bound | performance | the spacing ladder's covered range (item 7); no density decision is made in the text |
| null-band quantile, sibling-busy cut, loops × launches, load1 < 0.5 | regime | `UNMEASURED DEFAULT:` each, labelled in place (`[r9 M-9]`) |

#### R4.9.5.1 The bench submission (tier O) `[r9 M-4]`

A batch's official verdict is requested by ONE submission: the kit writes
it as a `responses.md` notice to main; main writes it into the bench inbox
(`inbox_from_pcrec.md`, a single-file `[inbox]` commit, D78) and schedules
the boxes. It is written and committed BEFORE the run and carries:
1. **Pins.** The pcrec commit and kit commit the bench builds; the bench
   commit; the compiler, glibc and governor as each bench box actually
   has them, ASKED of the bench dev (pcrecdev2, memory
   `pcrec-ask-bench-dev`), never assumed; the bench's pinning/idling
   discipline, asked the same way (`[r9 M-14]`).
2. **Testees,** per row and per live level L, each a separate binary:
   OFF@L, ON@L, DENY@L (text asserted identical to OFF before submitting)
   and DISPLACED@L for w32. Recipes `-O2 -march=<level> -mtune=generic`,
   recording the `--memfn=` string and `-march` (Q55's ruled attribution
   route, §R4.3.3).
3. **Cells:** the FULL mover set of the pre-registered population (not
   proposer-chosen evidence cells), the two evidence cells (union-select,
   mod-i), one cell per bin (§R4.9.6), the no-DFA (ON_MISS) bin and the
   VM-hybrid bin (bench patterns where the census finds them, else
   synthetic witnesses from the capability subbench, the
   capability-subbench-first rule; `(?i)\d+cat` at `--engine=vm` and
   `(?i)(a|b)+cat` are this lane's measured `fn-pair` witnesses for the
   two), the density ladder, and the NON-MOVER artifacts as the null
   population. `[r9fu]` The exact-window bin and the OFS run-pinned bin
   left batch 1 with `fn-memchr` (§R4.9.7.1). The submission MAY carry
   them as the filed `vrun` over `fn-memchr` row's trigger cells (that
   row's cell list is in §R4.9.7.1). If it does, they are marked
   non-target and the row is not accepted from them.
4. **A span-ladder subbench request**: the same patterns at 16/32/64/256/
   1024-byte subjects, so the per-call regime has an official instrument.
5. **The pre-registration** (the house prediction-table shape): predicted
   deltas per cell, the bar's thresholds, which cells are controls, the
   bins, the sweeps in. Written and committed before the run, at
   `docs/design/memfn/probes/simd/<batch>/prereg.md`; the reading is read
   against it.
6. **Arm budget:** the reach, unroll and KB sweeps run in tier U first;
   the bench gets the chosen candidate plus the incumbent, never the full
   cross product.
7. **Reported facts beside the verdict:** the objdump comparison of the
   scalar fall-through region, OFF vs ON (`[r9 M-13]`); the instruction
   classes each row declares (`mf_formdecl.insn`, `[r9 M-11]`), so the
   reading can be read against Zen 1's slow classes.
8. **Acceptance latency, stated:** a tier-O reading lands in the bench's
   window, so no SIMD delivery can claim an official re-measure "in the
   same delivery" (`[r9 M-8]`).

`[r9 F-4]` **`<PREFIX>_MEMFN_OPTS`** (rev 4.6 Q55: FILED, trigger "a bench
consumer asks") is now PLAUSIBLY triggered: the bench must tell DENY and
DISPLACED arms from ON. The recipe already records the `--memfn=` string,
so the submission ASKS the bench whether recipe recording suffices; the
stamp line is built only if it says no.

### R4.9.6 The acceptance bar per row, the record, and what re-opens it

**The bar** (D147 addenda 11 and 13, `[r9 M-3, M-5]`). A SIMD row is
ACCEPTED at level L iff, in a tier-O reading on EVERY official box that
executes L (§R4.9.5's table), the pre-registered bar holds:
1. **against OFF at L** (the CURRENT scalar layer, same `-march`).
   `[r9fu]` At every site a FUNC PREFIX row reaches, OFF is a
   GLIBC-BACKED body: the BODY row the PREFIX sits over calls `memchr`
   (§R4.9.7.1). glibc picks that `memchr` by CPU, not by `-march`, so
   "same `-march`" fixes the row's level and never the twin's. The twin
   runs at the CPU's own tier on every box. The pre-registration names
   the twin as "`<BODY row>` + glibc `memchr` (the box's reported glibc)",
   never as "scalar".
   - the row's TARGET cells (named in the pre-registration) improve their
     median whole-call time beyond the null band, by at least a stated
     minimum effect (`UNMEASURED DEFAULT:` an absolute ns or ns/B figure
     per regime, until the null distribution gives it), on AT LEAST ONE
     official box running L;
   - NO cell in the pre-registered population regresses past the floor
     on ANY official box running L (throughput and per-call alike; below
     reach included, where the loss is the prefix's own cost (`[D155]`: the
     entry tests'), see item 6
     of §R4.9.5). A NULL on one box with a win on another is accepted and
     recorded (Zen 1's 2×128 may null w32 per call);
2. **against DISPLACED at L**, where it displaces a SIMD row: the same
   tests. A wider level must not lose to the narrower one it pre-empts,
   on any box running both (first-match's meaning: a row must beat the
   row it displaces);
3. **the population is PRE-REGISTERED and binned by CAUSE** (`[r9 M-7,
   C-11]`). The movers are the pcrec-side text diff `-fmemfn-simd` vs
   `-fno-memfn-simd` over the corpus and the bench's patterns, counted as
   DISTINCT SITE SHAPES (not patterns), printed with their count and a K35
   floor. Bins are what the cost model reads: (FUNC customer, handoff,
   pcrec route from the stamps, the `rc_row` the verify uses, masked or
   exact, and `[r9fu]` the BODY row the PREFIX sits over, which names the
   glibc-backed twin). There is no "fewer than 8 movers" exclusion: every bin the row
   reaches needs at least one official cell (a bench pattern, or a
   synthetic witness), fixed in the pre-registration before the numbers
   exist. A bin with no cell is UNREACHED; the UNREACHED list is printed
   with its counts at every G1 run, and a bin crossing from UNREACHED to
   reached flips the affected records to STALE (K35, the excluded side).
   The route is NOT a site fact the kit can read, so a losing route bin
   cannot be narrowed by the row's APPLIES: it blocks the row's level, or
   it needs a pcrec-stated fact (a request), and the record says which;
4. **correctness** (CPU-independent, any tier):
   - `make test` green;
   - the answer sweep at `-fmemfn-simd`, at every level (`GENCFLAGS`
     carrying `-march=L`), with a planted wrong arm red at its own level
     and green where it is compiled out; it is a SMOKE check, and G2
     carries the contract (`[r9 C-5]`);
   - ASan/UBSan over the movers at each level (D144 addendum 3);
   - G2 at each level (§R4.9.7), with per-path execution floors.

**When a box disagrees** (`[r9 M-3]`). A loss on ANY official box that
executes L blocks ACCEPTED at L. The kit cannot key on the box (both
boxes compile the same bytes for one `-march`), so the remedy is per
LEVEL: the losing level is removed from the row's rungs (w32 not
accepted, w16 still), or the row's APPLIES narrows by a stated site fact,
or the row is REJECTED. A level only one box executes (w64 on the dev
box) is judged on that box, and that judgement is official.

**The named-benefit alternative** (D147 addendum 11, `[r9 M-16]`). A row
that is not faster may be accepted on a SPECIFIC measured benefit. For a
SIMD row of THIS design, CODE SPACE is never such a benefit: its text is
the floor plus guarded text, so it is always longer. The path is open
only to a row that REPLACES scalar text (none in batch 1), and nobody
counts it as a second route into acceptance. A row whose benefit is
measured but which loses time past the floor is a TRADE, ruled by Frank
per row (Q-R9-4). `INERT:SIZE` is withdrawn (§R4.9.2.3). `[D155]` **RULED
"fastest wins"** (D155 item 4). For a SIMD row the bar is measurably
FASTER only, and code space is never a named benefit. The named-benefit
path and the TRADE route above are CLOSED for SIMD rows, and this
paragraph is kept as the record of the recommendation.

**The acceptance record and its lifecycle** (`[r9 M-2, F-11, M-8]`). Each
SIMD row × level × CPU class is one line of `tests/memfn/simd_accept.tsv`,
born with batch 1. Columns:
- `row`, `level`, `cpu_class` (`zen1` / `zen4` / `m1`);
- `state`: CANDIDATE, ACCEPTED, STALE or REJECTED;
- `tier`: `unofficial` or `bench`;
- the bins it was judged on, and the pre-registration path;
- for a bench line: `bench_run_id`, the bench commit, and the box's gcc
  and glibc AS THE BENCH REPORTED THEM;
- the pcrec and kit commits;
- the COMPARATOR digest: the BODY rows' `arms.tsv` digests for the row's
  fixtures PLUS a digest of the real site population (the mover manifest,
  by id);
- `transcript_comparator_digest`, copied from the transcript header at
  timing time;
- the regimes, `-march`/`-mtune`, null band and floor, the deltas, the
  verdict, the transcript path.

States:
- **CANDIDATE.** The row has landed behind the default-OFF switch with
  tier-U evidence only. It renders under `-fmemfn-simd` (opt-in: a
  CANDIDATE that turns out slow is an opt-in speed loss, not a disaster),
  and it is the state a bench testee pins. A row lands ONLY with a
  CANDIDATE line per level (`run_rows.sh` checks the row set, F-5).
- **ACCEPTED.** A tier-O reading met the bar on every official box
  running the level. Only ACCEPTED feeds R4f, the spec's or docs'
  "faster" wording and D147 addendum 11's claim.
- **STALE.** The comparator moved (below). It reads as CANDIDATE until
  re-measured; STALE lines queue a bench re-measure in the next
  submission.
- **REJECTED.** A tier-O loss. The level is removed from the row's rungs
  or the row's predicate narrowed in the kit's follow-up; the line stays
  as the record of why.

**What re-opens a comparison**, and how each is caught:

| event | why it re-opens | how it is caught |
|---|---|---|
| a scalar-layer change at the row's sites (D147: "a scalar improvement re-opens the comparison") | the comparator moved | **C19**: a line whose comparator digest no longer equals the current one (fixtures OR site population) reads STALE. Never red (Q-R9-5); the change lands on its SIMD-off reading |
| the comparator moves without moving a fixture (pcrec's pick, prior or findings bundle changing operands; `cand_rows[]` routing) | the site population moved | the population half of the digest (`[r9 M-8]`) |
| R4d landing (the first scalar mover at batch 1's site) | the same | C19, as above; R4d's alpha includes the `-fmemfn-simd` arms in tier U |
| a kit change to the SIMD row's own text | its own G1 | its own tier-U alpha, then its own submission |
| an UNREACHED bin becomes reached | the population grew | the G1 recount, STALE |
| the bench box's gcc or glibc major version changes | the scalar layer's libc calls (`memchr`) and both layers' code generation move | the record holds the versions the bench REPORTED; the next submission compares them with what the bench reports then |
| a box is added to a level's official list | a new verdict box | that box's lines are CANDIDATE until read |
| a WRONG ANSWER anywhere | correctness never waits | a DISASTER (D144 item 3): the row is removed from the table or its predicate emptied at once, in the kit, with its own commit |

**C19's states are computed, never edited by hand.** C19 checks
record digest == `transcript_comparator_digest` == current digest. A line
whose stored digest equals the transcript's but not the current one is
STALE, printed as such; C19 does not go red for it, and every READER of
`state` (R4f's gate, the submission queue, any docs claim) reads C19's
EFFECTIVE state, never the column alone. C19 IS red when a line's digest
was edited without a transcript that carries it (the plant: re-pin the
record's digest without a transcript), and when a SIMD row × level has
no line at all.

**A re-opened comparison never blocks the scalar change** (Q-R9-5). The
scalar layer is accepted on SIMD-off measurements alone (D147). If the
re-read SIMD row then loses past the floor, the scalar change still
lands, the line goes STALE, an issue row is filed (D144 item 3) and the
kit narrows or removes the row in a follow-up.

### R4.9.7 The first batch, with its evidence, and the filed list

**Step R4e′.0 (the seam) precedes batch 1** and is its own kit request:
§R4.9.2.1, zero movers, no options.def row, no `MF_SITE_ABI` bump. **`[R4e′.0]` BUILT** (lane r4e0, 2026-10-09).
`[D155]` **Step R4e′.0b (the routing) follows it, also before batch 1**:
§R4.9.2.6. **`[R4e′.0b]` BUILT** (lane r4e0b, 2026-10-09, abi 69 -> 70). It moves every FUNC's loop into `<fn>__body` and makes the FUNC
one call. It is a pcrec abi event (RQ-6), it has no options.def row, and
it is measured as G1. Batch 1 then adds only guarded text.

**Batch 1: the FUNC part whose predicate is one RUN term and is its
site's only predicate; rows `vrun-w32` and `vrun-w16` in `fn_rows[]`.**
The site population is §R4.9.2.1's table: PRE `<p>_reqrun` with no lead,
set rest or whole run, on every route, whose BODY row is `fn-pair`
(`[r9fu]`, §R4.9.7.1). The first draft also listed OFS `<p>_ofsskip`
run-pinned sites whose k-set is the run alone. They are all `fn-memchr`,
so they moved to the filed list. The form is R-1's `ffl`, a fused
pair-filter scan with an in-block verify that goes through the BODY's
`rc_row` (C-12). Only the FUNC's PREFIX slot is new; the use lines are
untouched. `[D155]` What the PREFIX slot renders is now the guarded helper
blocks and, through the seam, the selector arms (§R4.9.2.5).

**The level order, argued (D144 addendum 4: SSE first; the AVX2/AVX-512
order on evidence).**
- **w16 first.** It has the widest reach: every x86-64 consumer at the
  default recipe, both official x86 boxes. R-1 (tier U, Zen 1) shows it
  beating emit and swar on every throughput row and every per-call row
  above reach at both cells.
- **w32 second, in the same batch, as a CANDIDATE.** Its tier-U trigger is
  met on throughput even on Zen 1's 2×128 (union-select gate 1m −9,856 ns
  and mod-i sweep 1m −14,344 ns over w16), and its per-call reading is
  mixed on that CPU (mod-i pc64 +0.97, `short75` +0.99, union-select pc64
  −0.29). Zen 1 is where it is most likely to null, Zen 4 where it is most
  likely to win; its official verdict needs both (§R4.9.6).
- **w64 third, filed.** AVX-512 is NOT filed for lack of hardware (the
  dev box runs it natively). It is filed for lack of a CELL: its trigger is
  a tier-U dev-box probe at `-march=x86-64-v4` showing a w64 rung beating
  w32 past the null band at a batch-1 cell. The hypothesis such a probe
  tests (a masked final block with `k`-mask loads instead of the
  overlapped block) is stated as a hypothesis, not a claim.

**Evidence** (R-1, `readings.gcc.md`; ubuntubudu, Zen 1, gcc 15.2,
`taskset -c 2`; ns; TIER U on an official CPU class, F-R9-4):

| cell (route, handoff) | regime | emit (current scalar) | swar (R4d's candidate) | ffl SSE2 (w16) | ffl AVX2 (w32) | floor |
|---|---|---|---|---|---|---|
| union-select (`SELECT`, masked, L = 6; no-DFA, ON_MISS) | gate 1m | 364,078 | 187,022 | 48,844 | 38,988 | 1,073 |
| | sweep 64k | 16,580 | 11,422 | 3,037 | 2,421 | 106 |
| | pc64 / pc256 / pc1024 | 26.58 / 78.66 / 272 | 15.39 / 49.53 / 195 | 4.75 / 13.62 / 57.05 | 4.46 / 11.12 / 39.76 | 0.38 / 1.83 / 6.30 |
| mod-i (`CAT`, masked, L = 3; DFA, ASSIGN) | sweep 1m (6,030 hits) | 724,503 | 267,480 | 142,800 | 128,456 | 5,989 |
| | gate 1m (hit at 404) / 64k (hit at 90) | 73.35 / 46.24 | 75.75 / 20.25 | 21.84 / 7.09 | 17.41 / 7.08 | 0.52 / 0.35 |
| | pc64 / pc256 / pc1024 | 33.20 / 61.73 / 63.85 | 15.46 / 31.56 / 38.71 | 6.98 / 10.07 / 11.33 | 7.95 / 8.57 / 9.89 | 1.19 / 1.20 / 2.16 |

- Whichever scalar layer is current at landing (emit, or R4d's form if it
  lands first), the w16 trigger holds.
- `[r9fu]` **The `emit` column IS the glibc-backed `fn-pair` twin.** It is
  byte-identical to today's FUNC text for both cells, with two `memchr`
  streams, re-checked at the kit tip (§R4.9.7.1). So the trap of D147
  addendum 13 was already priced at these cells: `ffl` SSE2 beats glibc's
  `memchr` plus its restart churn in every row, by 3-7x on throughput.
  The SIMD-on verdict column R-1 PRINTED (`ffl − swar`) used a pure-SWAR
  comparator, so it is the weaker statement. The table above restates it
  against `emit`. Both cells are tier U on Zen 1 only, and Zen 4's glibc
  `memchr` is a different ifunc arm, so the dev-box cell is still owed in
  tier O (§R4.9.5's table).
- `[r9 M-10]` mod-i's 6,030 hits per MiB is one hit per ~174 bytes:
  SPARSE for a vector restart regime, not dense. The first draft's "it
  wins on mod-i's dense sweep" is withdrawn; the density ladder (§R4.9.5
  item 7) is what bounds batch 1's density claim.
- **Not in the evidence**, each with its handling: `[r9fu]` an EXACT
  (unmasked) window and OFS run-pinned are both `fn-memchr`, so they are
  out of batch 1 and filed with their cells (§R4.9.7.1; the first draft
  added the exact bin's cell to batch 1's submission); the VM-hybrid
  route's window (its own bin; `handoff.rxt`'s hybrid witnesses from R4c
  are the synthetic cell if the bench reaches none).

**Prerequisites:**
- R4e′.0 (the seam) landed;
- RQ-1 (`--memfn=`) landed, for the two denies;
- RQ-2 (Q-R9-3 (a)) landed, for KB;
- RQ-3 (neutrality) landed;
- the tier-U slot (RQ-4) for the sweeps; the bench submission (RQ-5) is
  sent BEFORE any line moves past CANDIDATE.

R4d is NOT a prerequisite. Whichever lands second re-reads the other's
layer (C19, §R4.9.6).

**G1, both layers** (tier U for timing; correctness decisive):
- the pcrec-side mover census, by distinct site shape and bin, with its
  count, a K35 floor and the UNREACHED list;
- the reach, cut-over and unroll sweeps (§R4.9.5 item 10);
- the null population and per-bin timing of OFF, ON, DENY, DISPLACED;
- the SIMD-off zero-mover I2; C-SEL; C18 both legs;
- the answer sweep per level; ASan/UBSan per level.

The reading goes to the pcrec manager as two tables, SIMD-off and SIMD-on,
marked TIER U, with the UNREACHED list, and with the bench submission
(§R4.9.5.1) for tier O.

**G2, the kit's own** (blinded as before, D27; `[r9 C-5, C-10, C-1]`).
The generated site space for the batch-1 shape is rendered with the
policy word lacking `MF_P_PORTABLE_ONLY`:
- masks, run lengths 2..8, run offsets, both handoffs, `use` both ways,
  both BODY rows under each PREFIX row. `[r9fu]` A PREFIX row renders over
  `fn-pair` only, and the `fn-memchr` sites in the space are the OVER
  test's negative control: their text is byte-identical to the SIMD-off
  rendering, and a plant that puts `fn-memchr` back in `over` is red
  there;
- compiled at every `mf_levels()` level's `test_march` plus
  `-mgeneral-regs-only` (w16's compiled-out level) and `-march=x86-64-v4`
  (the dev box executes all of them);
- subjects: lengths 0 to `2·(2·32 + 7) + 16`, alignments 0..31, a hit
  at every offset and none, MULTIPLE hits (two or more in one block,
  across m0/m1, and in the final block's already-covered lanes),
  NEAR-MISSES (the pair filter passes at KA and KB, the run fails, the
  loop continues; R-1's own `--check` used near-miss filler), and a `pos`
  sweep (restart at hit + 1);
- the oracle relation is EXACT RETURNED-POSITION equality with the scalar
  byte loop (which shares no code with the kit);
- guard pages at both ends, AND `[buf, s)` and `[s+n, end)` poisoned per
  case with `ASAN_POISON_MEMORY_REGION`, under ASan/UBSan: an aligned-down
  load below `s` is otherwise invisible (malloc is 16-aligned and
  `[buf, s)` is addressable). The corpus sweep's ASan does NOT cover reads
  past `n` (its subjects sit in larger buffers with a NUL at `s[n]`); only
  G2's end guard and poisoning do, and the design says so;
- plants per path, per level, each red where its path is live: the final
  block off by one (R-1's PLANT 1); the lane mask off by one; m0/m1 order
  swapped; the pair filter accepting a near-miss without the verify; the
  reach one short (C-1), red against the end guard page;
- per-path EXECUTION floors: a `--coverage` build of the rendered sites
  counts the entry tests (`[D155]`, formerly the prefix rungs), the 2× loop, the 1× loop, the overlapped final
  block and the in-block verify, each against a floor in
  `row_floors.tsv` (the [MECH-REACH] proof that the space reaches every
  path);
- `guarded_max` checked: no rendering writes more guarded bytes than its
  row declares (Q-R9-9);
- the declared instruction classes checked against the object
  (`objdump -d` of each level's helper: no PDEP/PEXT, no gather,
  `[r9 M-11]`);
- per-row CHOSEN floors in `tests/memfn/row_floors.tsv`.

**Born in batch 1's commit** (Q49: no abi bump; no default byte moves;
`[D155]` the routing abi event is R4e′.0b's, before this commit):
- rows `vrun-w32`/`vrun-w16` in `fn_rows[]` and options.def; the `memfn`
  section's spec floor raised by 2 (born at 2 if R4d has not landed);
- `levels.def` and `mf_levels()`;
- the `simd_open`/`simd_close` sink ops and `mf_pred.plan_pos2` (Q-R9-3),
  in ONE `MF_SITE_ABI` bump ("the next number at landing", never a
  literal: M6 takes 8);
- the `rows.tsv` lines (witness compiled with `-fmemfn-simd`, control
  with `-fno-memfn-simd`, signature absent);
- `arms.tsv` pins for the new fixtures;
- `simd_accept.tsv` with CANDIDATE lines per level and CPU class;
- the `simd` sweep arm with its projections, C18's four legs (a)-(d) `[r9b]`, C9-x86,
  C-SEL, C19, and C11's FORMS half made LIVE (§R4.9.8);
- the spec hunks (D80):
  - `tuning.md` §2.43 loses "INERT", states what the switch renders,
    that `-march` picks the live level and that `--memfn=` is a no-op at
    `-fno-memfn-simd`;
  - `match_api.md` §6.3: the carried-levels grammar, and that the levels
    are RENDERED, not live (C-9, F-15);
  - `limits.md`: whether D84's caps count guarded bytes (Q-R9-9's
    ruling);
  - §10.6's limits name the official boxes, their CPU classes, and
    aarch64 as unmeasured;
- the bench submission (RQ-5).

**FILED, each needing a cell** (do not build, D77; `[r9 F-7, F-6]`
re-read against the kit tip):

| site / form | why not batch 1 | the cell or fact that would trigger it |
|---|---|---|
| PRE composite WITH a lead (userpass, cls-n-uc) | F-R9-3: vector forms lose per call where the lead rejects (userpass) and win where it never rejects (cls-n-uc); the kit cannot tell which | the filed "lead can reject" fact (§15.5 item 2), OR a lead-first vector form measured NULL-or-better than the current scalar at userpass-like cells in both regimes |
| `[r9fu]` `vrun` over `fn-memchr`: every exact window, a masked window whose pick is a non-letter, and OFS run-pinned | the twin is ONE glibc `memchr` stream, which glibc's ifunc runs at the CPU's own tier. R-1 has no same-function cell (§R4.9.7.1). pcrec's pick favours a RARE byte, which is glibc's best regime | §R4.9.7.1's five cells, on both official x86 boxes, at the same `-march`, both regimes. Landing = add `fn-memchr` to the two rows' `over` |
| PRE composite with a whole run or set rest (`<p>_reqrun_whole`) | no cell | a timed mover in that bin |
| OFS `offset-set[-bounded]` (set terms only) | no cell; a set-only k-set is a different vector body (no run verify) | an offset-set cell with a fused form beating its current scalar arm |
| PF one byte (`pf_memchr`, `pf_memchr_bounded`) and MLINE (`pf_memchr_back`, delegated at M4) | glibc's AVX2 `memchr` is the x86 bar (55 ns at 4 KiB, ~60 B/ns); nothing surveyed beats it (linux_results.md §7). The scalar layer already calls it. D147 addendum 13's trap names exactly this | a cell where an inline form beats glibc in its regime (short per-call spans below n*, 64-256 B, are the only candidates; F = 3.24 ns) |
| PF byte set (`pf_walk`, `pf_walk_bounded`) | T-A wins only on a MISS over a whole span (4-15x); the DFA candidate skip skips 0 bytes per entry on real text and a 7x faster skip made bench subjects slower (F-R9-7); find-first vector forms lose on dense text | an artifact cell whose non-candidate runs are long (≥ ~32 B, the measured crossover) with the dense regime answered |
| SETREST fused ALL_PRESENT | no cell | §22's filed fused N4 arm's trigger |
| STAY, EDGE, VMSPAN (budget 2, ADVANCE) and VMSTRIDE (M6, building at `MF_SITE_ABI` 8: multi-term ADVANCE, `MF_MAX_TERM` 32) | in-loop, short spans; AVX2 without a 16 B tier costs 8-16 ns at 16 B (§6.1). `[r9 F-6]` A SIMD ADVANCE form needs a NUMERIC loop limit and stride the kit can read; ADVANCE carries `more` as a text expression and `span_hi` as an iteration cap. DECIDED (manager, D77): M6's `MF_SITE_ABI` 8 does NOT carry that bound; it comes in its own bump with the first SIMD ADVANCE cell. This answers R-10's Q-R10-10 (main relays it to `responses.md`) | U-3, a Linux cell dominated by class runs (§22 R4h's mover trigger), AND the bound's own bump |
| VERIFY / VMRUN masked run (`vec-masked`, L ≥ 16) | no cell; gcc already lowers a constant exact `memcmp` at L ≥ 16 to a vector compare in portable C | a run-compare-bound cell; the row would sit in `rc_row` and take the same `mf_formdecl` |
| N7, MISMATCH (delegated at M7: `mismatch_inplace` and the generic row) | no cell; a span compare's bound is a run-time operand pair | a MISMATCH-bound cell |
| ~~N7U~~ (per-character decode compare) | RETIRED (D147 addendum 14): the encoding's character walk, not a kit site | — |
| the lazy cursor rung's rmin prefix loop | migrated (R-12, VMSTRIDE/VMSPAN's instance) | — |
| ~~N6~~ | RETIRED (D147 addendum 12): an engine step, not a search site. No SIMD row will ever exist for it | — |
| a 64-byte level (AVX-512) | no CELL (the hardware exists: the dev box) | a tier-U probe at `-march=x86-64-v4` showing a w64 rung beats w32 past the null band at a batch-1 cell |
| aarch64 levels (NEON) | addendum 8 | Frank admits Mac verdicts for the cells, or an aarch64 Linux box exists |
| the run-time cascade `vrun-rt` | no cascade cell | §R4.9.3's probe |

#### R4.9.7.1 `[r9fu]` The glibc-inside trap, per site

D147 addendum 13 names the trap: a scalar site that calls glibc's
`memchr` is already SIMD inside. The first revision stated it only for
the PF/MLINE sites. This subsection settles it for every site class batch
1 reaches and for both BODY rows a SIMD row may sit over, BY MEASUREMENT.

**Method.** The kit tip's binary (`lane/memfn-m7` 01772107,
`build/pcrec`) emitted witness artifacts
(`pcrec -p rx -o wN.c --pattern P [--engine=vm]`). Each FUNC's body was
cut out of the `.c`, the artifact compiled `gcc -O2 -c` (gcc 15.2.0,
glibc 2.43, dev box) and read with `nm -u`, and the `.s` was read with
`gcc -O2 -S`. The full transcript is `../../dev/lanes/r9d_report.md`
"follow-up r9fu".

| witness | site class (stamps) | BODY row | `memchr` streams in the FUNC | `nm -u` | R-1 cell against this twin? |
|---|---|---|---|---|---|
| `(?i)cat` | PRE window, masked; DFA, ASSIGN (`REQ_HANDOFF "0"`) | `fn-pair` | 2 | `memchr` | YES: mod-i, `emit` byte-identical to this FUNC |
| `(?i)union.*?select.*?from` (and at `--engine=vm`: no-DFA, `VM_PREFILTER "none"`) | PRE window, masked | `fn-pair` | 2 | `memchr` (`__stack_chk_fail` on the VM arm) | YES: union-select, `emit` byte-identical |
| `(?i)\d+cat` `--engine=vm` | PRE window, masked; no-DFA, ON_MISS | `fn-pair` | 2 | `memchr` | no (the bin's witness) |
| `(?i)(a\|b)+cat` | PRE window, masked; VM hybrid | `fn-pair` | 2 | `memchr`, `__stack_chk_fail` | no (the VM-hybrid bin's witness) |
| `xyzzy`, `\d+xyzzy`, `[a-z]*select[a-z]*` | PRE window, exact; DFA (ASSIGN and none) | `fn-memchr` | 1 | `memchr` | NO |
| `\d+xyzzy` `--engine=vm`; `(a\|b)+xyzzy` | PRE window, exact; no-DFA; VM hybrid | `fn-memchr` | 1 | `memchr` | NO |
| `(?i)\d+ab/cd`, `(?i)\d+qz#x` | PRE window, MASKED, pick a non-letter (`/`, `#`) | `fn-memchr` | 1 | `memchr` | NO |
| `/user\|/users` (`router-prefix-order`) | OFS `run-pinned`, DFA prefilter, RETURN | `fn-memchr` | 1 | `memchr` | NO |

Every FUNC verifies its run with inline word loads (`rx_w2`/`rx_w4`
through `memcpy`), with no `memcmp`, `memrchr` or `strlen`. Its only libc
call on the hot path is `memchr`, one call per candidate restart (per
stream). **Verdict: at every batch-1 site class, the scalar twin is
glibc-backed.** The twin for a PREFIX row is "its BODY row + glibc
`memchr`", and the bar (§R4.9.6 item 1) says so. glibc chooses its
`memchr` arm at load time from the CPU (its multiarch ifunc; the arm was
not identified on this box), whatever the consumer's `-march` is.

**`fn-pair`: R-1 compared against the glibc twin.** The `emit` column of
R-1's table IS today's `fn-pair` text, so batch 1's evidence stands as
tier U against the right twin. Its regime is narrower than the table
suggests: both cells pick `C`/`c`, a DENSE letter, and the twin's cost
there is restart churn. R-1 has no `fn-pair` cell whose two picked bytes
are RARE. A rough calculation from the cited numbers (no new timing)
leaves the sign open there. Two glibc streams with almost no restarts run
at about half glibc's ~60 B/ns (linux_results.md §7), so about 30 B/ns.
R-1's w16 rate on union-select is about 21 B/ns (1 MiB in 48,844 ns,
with verify work included). So **the bench run must add a sparse-pick
`fn-pair` cell** (a caseless run whose prior-picked letter pair is rare,
e.g. a `(?i)…zq…`-shaped bench or synthetic pattern) as a TARGET-or-floor
cell. The pre-registration bins `fn-pair` movers by the pick's band in
pcrec's prior. A loss there blocks the level (§R4.9.6 item 3: the kit
cannot see density, so the fix is a pcrec-stated fact, a request).

**`fn-memchr`: no same-function cell, so the evidence is trigger-grade.**
R-1's only glibc-backed `fn-memchr` text is cls-n-uc's `nosl` arm (the
`-fno-req-set-lead` gate: `memchr('i')` plus the run compare). The table
shows `ffl` AVX2 under it (gate 1m 4.72 vs 10.34 ns, sweep 1m 97,527 vs
403,594, pc1024 13.88 vs 72.79). But that `ffl` computes the LEAD
function, the comparison is AVX2 only, and `i` is a dense letter. pcrec's
pick prefers the RAREST byte (`xyzzy` scans `z` at offset 3, `/user`
scans `/`). That is glibc's best regime, and at the default recipe it
pits a w16 (SSE2) row against a glibc arm at the CPU's top tier.

**Decision: `over` excludes `fn-memchr` in batch 1** (§R4.9.2.4's row
table). The alternative was to keep it and require a win over glibc
there. It is rejected because no cell exists to judge it, and D77 files
a form until its cell does. Batch 1 is then the `fn-pair` PRE window on
every route. The exact-window and OFS run-pinned bins leave batch 1, and
with them the OFS cell obligation of §R4.9.2.1 and the only
ENTRYSINK-candidate site (§R4.9.7.2).

**The filed row's trigger cells** (tier U first, then the bench, same
`-march` per arm, both official x86 boxes, both regimes; the twin is
`fn-memchr` + the box's glibc):
1. an exact window with a RARE pick (`\d+xyzzy`-shaped);
2. an exact window with a DENSE pick (cls-n-uc's `it` under
   `-fno-req-set-lead`);
3. OFS run-pinned (`router-prefix-order`, `/user|/users`);
4. a masked window with a non-letter pick (`(?i)\d+ab/cd`);
5. the exact VM-hybrid window (`(a|b)+xyzzy`).

The likely outcome to test is a win at (2) and a null or loss at (1) and
(3). If so, the row needs pcrec's pick-frequency band as a site fact,
like the filed lead fact. That is a request, not a kit guess.

#### R4.9.7.2 `[r9fu]` [MEMFN-ENTRYSINK]: nothing assumes an entry point; the candidates

Frank's rule for `[MEMFN-ENTRYSINK]` (plan.md, filed): build SIMD forms
WITHOUT a function-entry setup point, then measure.

**Nothing in §R4.9 assumes one.** It was checked section by section:
- the PREFIX row's file-scope part lives at file scope (`mf_define`);
- its rungs sit at the top of the FUNC body, which is reached from the
  use point; `[D155]` now each rung is its own helper's entry test, and the
  FUNC is one call (§R4.9.2.5). That is still no entry-point setup: the
  helpers inline into `rx_search` at `-O2` (measured on the superseded
  rendering, `[r9b]`), and the broadcast
  counts equal r9fu's twin of the withdrawn shape (`/user|/users`:
  `pshufd` 4 at default, `vpbroadcast` 8 at v3, in both);
- the ladder "holds no static" (§R4.9.3);
- the cascade reads no cached word.

How the vector constants are made was never stated, so it is stated
here, as measured.

**How a w16/w32 form makes its broadcast constants (measured).** A hand
twin was built in the rendering order §R4.9.2.1 fixes:
- the file-scope helpers `rfx_w16`/`rfx_w32`, under level guards: R-1's
  `ffl` block loop without the lead, with constants as literals;
- the rungs at the top of the FUNC;
- spliced into the kit tip's emitted artifacts for `/user|/users` (OFS
  run-pinned) and `(?i)cat` (PRE, ASSIGN).

It was compiled with `gcc -O2 -S` and with `-O2 -march=x86-64-v3 -S`.
- gcc inlines the helper and the FUNC into `rx_search`.
- Each `set1` of a literal becomes `mov $imm32; movd; pshufd $0` (SSE2) or
  `vmovd; vpbroadcastd` (v3). gcc emits these at the rung's entry, after
  the reach compare, and emits them AGAIN for the overlapped final block.
- gcc never uses a `.rodata` load and never hoists these out of an
  enclosing loop.
- A file-scope `static const` vector is the only other scope the kit
  has, and gcc constant-propagates it back to the same immediates (8 such
  instructions remain in `rx_search` at SSE2, 16 at v3).
- The scalar invariants (`n − T − VW`, the reach compare) are likewise
  recomputed at each entry.

So the plan row's "pattern-constant setup needs neither: gcc hoists it or
it is a constant" does NOT hold for gcc 15.2 here. The setup is about 3
instructions per vector constant, done at each entry. Whether that costs
anything measurable is the trigger's hand-twin question. No timing was
taken.

**Per form, against the trigger's assembly test** (per-call setup re-done
inside a pcrec-OWNED outer loop):

| form / site | where the FUNC is called (artifact line) | candidate? |
|---|---|---|
| `vrun-w16`/`-w32` over `fn-pair`, PRE window, DFA ASSIGN | once, at `rx_search` entry, before the scan (`(?i)cat` l.79) | NO: the setup runs once per matcher call; the only outer loop is the CALLER's find-all |
| the same, DFA no handoff / no-DFA ON_MISS | once (`if (rx_reqrun(…) >= n) return 0;`, `\d+xyzzy` l.70, `(?i)union…` `--engine=vm` l.312) | NO, same reason |
| the same, VM hybrid | once, before the prefilter and the attempt loop (`(a\|b)+xyzzy` l.387); the hybrid's re-seed calls `rx_prefilter`, not the FUNC | NO |
| filed `vrun` over `fn-memchr`, OFS run-pinned (`<p>_ofsskip`) | INSIDE `rx_search`'s DFA scan `for (;;)`, on every re-seed (`forward_state == 0`, no accept; `/user\|/users` l.132); the assembly shows the broadcasts on that path | **YES: the one CANDIDATE.** It is out of batch 1 (§R4.9.7.1), so it is the filed row's to measure |

**Batch 1 therefore has no ENTRYSINK candidate.** The design does not
change for the row: no sink is designed here, and none is assumed.

### R4.9.8 Checks, their independence, and the sibling family

**One paired compile, many projections** (`[r9 F-5]`). G1's mover census,
C-SEL, C11's FORMS half, C18 and I2 are all projections of the SAME
paired compile over the same population. They are built as ONE
`emit_sweep` arm, `simd`, compiling each corpus and bench pattern at
`-fmemfn-simd`, `-fno-memfn-simd` and each DENY arm, with ONE mover census
(counted once, one K35 floor) feeding named projections: `text` (G1
movers), `stamps` (C-SEL), `forms` (C11), `pp` (C18), `parent` (I2 against
the parent commit). No new script per check. "The answer sweep per level"
and "the `test-axes` arm per level" in the first draft are ONE thing: the
answer sweep IS the `test-axes` arm per level.

| check | checked against | independent because | population (K35) | witness reaches its site ([MECH-REACH]) |
|---|---|---|---|---|
| **C18, the floor rule**, two legs (`[r9 C-6, M-15]`; `[r9b]` SUPERSEDED by the next row: four legs) | (a) `gcc -E -P -mgeneral-regs-only` of ON vs OFF: preprocessed-EQUAL; ~~(b) `gcc -E -P -march=L` of ON vs OFF at each live level: an INSERTION-ONLY diff;~~ `[r9b]` struck, see the next row; plus a lint that every `#if` line in the ON − OFF text diff is a `levels.def` guard string from `mf_levels()` | the PREPROCESSOR, with gcc's own macro set, decides which text survives; the kit's ladder cannot assert it | movers compared, printed, floor = the census count | three plants: one byte of the floor text edited inside a SIMD rendering (red at (a)); a guarded `#define` that changes the floor (green at (a), red at (b)); an UNGUARDED byte added outside the stamp filter (the NEGATIVE control). The comparison's one named filter is the stamp lines (`#define <PREFIX>_…`), which vanish in `-E` anyway |
| `[D155]` **C18 as amended** (supersedes the row above in legs (b) and adds (c), (d)) | (a) unchanged: `gcc -E -P` at `-mgeneral-regs-only` AND `-mno-sse2`, ON vs OFF, byte-EQUAL; (b) at each live level, `gcc -E -P -march=L`, ON vs OFF: the DELETED lines are exactly one per SIMD FUNC and each matches `^    return <fn>__body\(<args>\);$`, and nothing else is deleted; (c) the RAW ON text vs the RAW OFF text: 0 deleted lines, and every inserted line lies inside a kit bracket (§R4.9.2.4); (d) a brace-depth scan of the raw ON text: a `#` line between a function's `{` and its matching `}` is allowed ONLY in the selector shape, i.e. the function's whole body is the `#if`/`#elif`/`#else`/`#endif` chain with one call per arm and nothing else; any other `#` line in a function body is a C18 failure; plus the guard lint (every `#if`/`#elif` line in ON − OFF is a `levels.def` guard string from `mf_levels()`) | (a) and (b): the PREPROCESSOR decides which text survives. (c) and (d) read the kit's own output, so they are structural lints, not independent; the census they are counted against is pcrec's | (b)'s replaced-line count = the SIMD-FUNC count from the mover census (K35); (c) and (d) over every SIMD-on mover | the three r9 plants, plus: a `#if` placed inside `<fn>__body` (red at (d)); a selector arm holding anything beyond its one call, e.g. a second statement (red at (d)); a SECOND changed line in the selector arm, e.g. the call's arguments reordered (red at (b)); the `#else` arm's FUNC text edited by one byte (red at (a) AND (c)); a rung arm left unbracketed (red at C-SEL through `simd_guarded`) |
| **C9-x86** (§17.3 on this box, `[r9 C-8]`) | every mover compiled with the harness `GENCFLAGS` `-Werror` at `x86-64`, `x86-64-v2`, `sandybridge` (AVX without AVX2), `x86-64-v3`, `x86-64-v4` and `-mgeneral-regs-only`; the live-arm count per level from `nm` of an `-O0` object | the compiler, at six macro sets that include each level minus its top feature; the kit-reported count is a second reading only | arms per level against a per-level COLUMN of `row_floors.tsv` (`[r9 F-5]`: no separate `c9_floor` pin file) | a plant guarding the w32 arm with an AVX-only guard compiles at v3 and fails at `sandybridge`; a plant guarding it with the w16 guard fails at `x86-64` |
| **C-SEL, selection neutrality** (`[r9 C-3, M-15]`) | every stamp except `MEMFN_FORMS`, compared as KEYS with byte and node counts normalised; `RUN_WORDS` exactly; `MEMFN_LIBC` as ON ⊇ OFF with the difference inside the chosen rows' declared sets; the refusal set as keys, never counts; ON vs OFF over the corpus, the bench and the near-cap size witnesses | pcrec's own stamps and its own compile results | artifacts and refusals compared, printed; a LITERAL floor in the script | the near-cap witnesses by NAME (`tests/resource`'s size rows and `tests/utf8/axis12_scripts.rxt`'s 999,925-byte artifact); a plant that drops `simd_guarded` from one length reader is red |
| **C19, the acceptance record** (`[r9 M-8, F-5]`) | `simd_accept.tsv`'s digests vs each line's transcript header vs the current fixtures + site-population digest | the transcript is written by the timing run, not by the record; the population digest comes from pcrec's mover manifest | `run_rows.sh` checks the record's row set against `rows.tsv`'s `MF_L_SIMD` rows (every SIMD row × level has a line) | a plant editing a line's digest without a transcript is red; a plant moving a fixture flips the line to STALE (printed, not red) |
| C11 FORMS half (§18.2), made LIVE | the `forms` projection: non-`none` exactly on the movers | the kit's `moved` is not read | non-`none` count = the mover count | `MEMFN_FORMS` forced `none` on a mover is red (§17.6's row, now reachable) |
| the answer sweep per level (= the `test-axes` arm per level) | the corpus oracles at `-fmemfn-simd`, `GENCFLAGS -march=L` | the oracles are python `re`/libpcre2 | cases per level printed; per-path `--coverage` counts against floors | a planted wrong w32 arm is red at v3 and green at x86-64; a planted wrong w16 arm is red at x86-64 and green at `-mgeneral-regs-only` (`[r9 C-5]`) |
| G2 per level (the kit's) | the scalar byte loop over a generated space, exact returned position | never another kit output (§4.5) | CHOSEN per row and per-path execution floors in `row_floors.tsv` | the guard-page, poisoning and per-path plants (§R4.9.7) |
| I2 at `-fno-memfn-simd` (the `parent` projection) | the parent commit's compile | a different commit | movers by id: must be 0 | a plant rendering a SIMD row under `MF_P_PORTABLE_ONLY` is red |
| the seam's gate (R4e′.0) | every `emit_sweep` stream vs the parent | a different commit | the `fn` census by customer, floors | a plant swapping `fn-pair`/`fn-memchr` order is red on every two-cube FUNC |
| `[D155]` the routing's gate (R4e′.0b, G1) | every `emit_sweep` stream vs the parent; the text diff un-done (rename `<fn>__body` back, drop the forwarder) must equal the parent byte for byte; the assembly at `-O2` (default and v3) vs the parent's, function counters renumbered | a different commit; the compiler | movers by id = the `fn` census (every FUNC part), floor | a plant that also edits one byte of the loop is red at the un-done diff; the assembly leg's witness is `__attribute__((noinline))` on `<fn>__body` (measured: 349 changed assembly lines on `(?i)cat`). Making `<fn>__body` plain `static` is NOT a witness, because gcc still inlines the single caller (measured: assembly identical), so that plant reads green by design |

**Sabotage rows** (ids at build from the kit manager's range; mech arms
in `tests/memfn/`): one per check above, plus §17.6's two SIMD rows (the
stamp row and "a SIMD arm emitting one intrinsic under default"), which
become reachable at batch 1. Each row states its `SAB_REACH` as the mover
census being non-empty.

**The sibling family** (the forest lens, memory
`pcrec-forest-for-trees`): every first-match table near this decision,
and where SIMD does or does not go.

| sibling table | question it answers | SIMD rows? | why |
|---|---|---|---|
| kit `fn_rows[]` (`ofsskip.c`, NEW at R4e′.0) | which loop is a FUNC's body, and ~~what goes in front of it~~ `[D155]` which guarded level helpers sit beside it | YES: batch 1, PREFIX slot | the text batch 1 changes is rendered here and nowhere else (F-1) |
| kit `arms[]` (`compose.c`) | which text renders this site | not in batch 1 | STMT-only and non-FUNC sites; a later batch's PREFIX-style slot |
| kit `rc_row` (`runcmp.c`) | which text compares this run | later (filed) | takes the SAME `mf_formdecl` when its first SIMD row lands; already shares the ONE walk |
| kit `options.def` | which kit rows can be denied/forced | one row per SIMD row | THE ONE deny carrier (D144 item 4 inside the kit's namespace); `MF_D_RUN_OVERLAP` the named legacy exception |
| kit `levels.def` (new) | which ISA levels exist, how they are guarded, what the tests compile them at | n/a | the one place a level is named; enumerated by `mf_levels()` |
| kit `fields.def` | which stated fields a row must serve | gains `policy`, `budget` | a SIMD row's policy decline is an ordinary `DECLINED` |
| pcrec `cand_rows[]` ([START-TABLE]) | WHERE and WHAT to search | NO | D146: pcrec decides what is searched; the kit decides how |
| pcrec clskit `ROWS`/`TAB_ROWS` (D131/D139) | one-position class membership; table storage | NO | one position is not a search |
| pcrec `fit_rungs[]` ([DEC-FALLBACK]) | the size-cap ladder | NO, and it no longer SEES SIMD bytes | §R4.9.2.4 (RQ-3) |
| pcrec `req_admits[]`/`req_uses[]` (now in `cand_rows[]`) | whether a pre-check exists, how its answer is used | NO | admission is a placement fact (§2.3 T2) |
| option_sets.md family `memfn` (`auto`/`simd`/`no-simd`) | which switch value a set names | n/a | unchanged; `--memfn=` stays one opaque value (§R4.4.1) |

No sibling answers the same question as a SIMD row. The shared STRUCTURES
(one declaration for all three kit tables, one walk, one deny carrier)
are unified from the start. `[r9 F-3]` **The H1 trigger** (row_contracts.md
§6: "a real table, kit or pcrec, wants to adopt the general first-match
engine") is NOT met by batch 1: `fn_rows[]` is a third KIT table using
the kit's own shared walk, which is H1's kernel built for the kit's three
customers; H1's engine is what a table OUTSIDE that walk would adopt. If a
pcrec table asks, the kernel exists.

### R4.9.9 The three standing design questions

1. **The measurement regime: RELEVANT.** It is this revision's core,
   §R4.9.5. Every number above names its box and tier (`[r9 M-1]`: R-1 is
   tier U on Zen 1), compiler (gcc 15.2), libc (glibc 2.43 on the dev box),
   pinning and regime. Things that can flip a verdict, each now an
   explicit dimension:
   - the consumer's `-march` (F-R9-2) and `-mtune` (named, never native);
   - the span against the row's reach (F-R9-1);
   - whether a lead rejects (F-R9-3: K-1 keeps the lead shape out);
   - the CPU class (Zen 1's 2×128 and slow PDEP/PEXT, Zen 4's native
     AVX2/AVX-512): a verdict per official box;
   - the hit density (the spacing ladder, `[r9 M-10]`);
   - glibc's `memchr`, which is part of the scalar layer;
   - the governor at launch (`[r9 F-14]`).
2. **The independent control: RELEVANT.** See the §R4.9.8 table.
   - Its controls share no source with the kit: the preprocessor (C18),
     pcrec's stamps and compile results (C-SEL), the compiler at six
     macro sets (C9-x86), the oracles (the sweep), the scalar byte loop
     (G2), the bench's own run (tier O), and the null population as its
     own noise control.
   - Populations come from ONE pcrec-side census with a floor, counted by
     distinct site shape (K35), with the UNREACHED bins recounted every
     run. Each witness is proven to reach its path by per-path coverage
     floors and plants red only where the path is live.
   - C19 shares a committed-file source with `arms.tsv`; it is a staleness
     detector, and its transcript binding is what stops a hand-edited
     digest.
3. **What moves when data is regenerated: RELEVANT.**
   - **R4e′.0 (the seam):** nothing emitted moves (its gate). The trace
     gains a table and two rows; `rows.tsv`, `row_floors.tsv` and the
     sabotage anchors in `ofsskip.c` move with the text.
   - `[D155]` **R4e′.0b (the routing):** every artifact with a FUNC part
     moves (+139 B per FUNC). It is a pcrec ABI EVENT: the abi number's
     readers are found by grep, the identity gates are re-pinned, and the
     kit's `arms.tsv` FUNC fixtures re-pin. The assembly is predicted
     unchanged at `-O2` (§R4.9.2.6). Its `simd_accept.tsv` effect is
     nil, since no record exists yet.
   - **`levels.def` or a SIMD row's text:** only `-fmemfn-simd` artifacts
     move. Under Q49 there is no abi bump and no default byte moves.
     `[D155]` A `levels.def` GUARD string moves the selector lines of
     every SIMD-on mover, and still nothing at SIMD-off, because the
     scalar arm carries no guard. Its
     own pins move (`arms.tsv` SIMD fixtures, the per-level column of
     `row_floors.tsv`), `MEMFN_FORMS` values move on SIMD-on artifacts,
     and every `simd_accept.tsv` line whose comparator or row moved reads
     STALE.
   - **The `MF_SITE_ABI` bump at batch 1** (sink ops, `plan_pos2`): a kit
     contract event; pcrec's call sites re-pin with it; no emitted byte
     moves.
   - **RQ-3:** no default byte moves (SIMD-off has no guarded bytes); the
     length readers' spec sentences move (D80), and Q-R9-9's ruling moves
     `limits.md`.
   - **`simd_accept.tsv`:** no emitted byte moves. Lines change state by
     C19's computation or by a reading.
   - **An `options.def` row:** the `memfn` section, its spec floor and
     the arm counts move (§21.3's last row).
   - **The spec:** batch 1 changes `tuning.md` §2.43, `match_api.md`
     §6.3 and `limits.md` (D80). R4f, the default flip, is the abi event
     (§22).

### R4.9.10 Questions for Frank (Q-R9-n), each with a recommendation

`[D155]` **Q-R9-1..11 are RULED** (Q-R9-1..9: D155, Frank 2026-10-08,
recorded on main 3b1fd77c; Q-R9-10 and Q-R9-11: D155 addendum 1, same
day). Each item below keeps its recommendation as the record, with its
ruling marked.

- **Q-R9-1. Which box gives SIMD verdicts?** `[r9 M-1]` **RESOLVED by
  D144 addendum 4:** an official verdict is a pcrec-bench run on the
  hardware each form targets (ubuntubudu Zen 1, the dev box Zen 4, the Mac
  under addendum 8); every other timing is directional. The first draft's
  recommendation (a), "the dev box is the verdict box", is WITHDRAWN.
  Nothing to rule. `[D155]` **RULED (item 1): resolved by D144 addendum 4.**
- **Q-R9-2. Acceptance levels, and how two boxes combine.** `[r9 M-3]`
  REVISED.
  - **Recommend:** each row is judged at EACH level it targets (w16 at
    the default x86-64, w32 at x86-64-v3), always against SIMD-off at the
    same `-march`, on EVERY bench box that executes that level. A loss
    past the floor on any of them blocks the level; a win is needed on at
    least one, and a null elsewhere is accepted and recorded. A level only
    one box executes (AVX-512) is judged on that box.
  - The bench gets the testees of §R4.9.5.1 at `-O2 -march=<level>
    -mtune=generic`: the default recipe exercises only w16, so a v3
    recipe is required for any w32 verdict.
  - And a row may LAND behind the default-OFF switch as a CANDIDATE before
    its bench reading, so the bench pins a main commit. **Recommend yes**:
    it is opt-in, D144's alpha-merge logic, and only ACCEPTED feeds R4f or
    a "faster" claim.
  - This reads D147 addendum 13 ("holds on each instruction-set tier") as
    "on each official box running the tier, no loss; on at least one, a
    win". Addendum 13 is preliminary; this is the panel's proposal for its
    revisit.
  - `[r9fu]` **Refined, same recommendation.** "Against SIMD-off at the
    same `-march`" fixes the ROW's tier, never the twin's. At every
    batch-1 site the twin is glibc-backed, and glibc picks its `memchr`
    arm by CPU (§R4.9.7.1). So "per instruction-set tier" means the row's
    level against a twin running the box's own glibc tier. The
    pre-registration names the twin as "BODY row + glibc", with the
    glibc each box reports. The follow-up changed one recommendation
    elsewhere, as a D77 filing and not a question: batch 1's `over`
    narrows to `fn-pair` (§R4.9.2.4, §R4.9.7.1). The ENTRYSINK check
    changed none. No new Q.
  - `[D155]` **RULED as recommended (item 2):** a level is judged on
    EVERY bench box that runs it. A loss anywhere blocks the level, and a
    win somewhere is required. Rows may land first as CANDIDATE behind
    the OFF switch. This is now the reading of D147 addendum 13.
- **Q-R9-3. Who picks the fused filter's SECOND position (KB)?**
  - (a) pcrec states it as a fact: `pcrec_find_pick2`, the PICK reader
    §2.3 T7 already named, carried as `mf_pred.plan_pos2`. That is a kit
    `MF_SITE_ABI` bump (folded into batch 1's one bump) and zero pcrec
    movers;
  - (b) the kit carries its own byte-rank table;
  - (c) a fixed positional rule, labelled `UNMEASURED DEFAULT`.

  **Recommend (a)** (the panel agreed). Rarity is pcrec's fact (D146's
  boundary), the prior stays ONE table, and R4d's SWAR pair filter needs
  the same fact, so one request serves both layers.
  `[D155]` **RULED (a) (item 3):** pcrec states `plan_pos2` (RQ-2).
- **Q-R9-4. A row that is smaller but not faster.** `[r9 M-16]` REVISED.
  - **Recommend:** a measured named benefit with every timing cell NULL
    or better is ACCEPTED; a benefit with a timing loss past the floor is
    a TRADE that comes to you per row.
  - For SIMD rows of this design the benefit can never be CODE SPACE:
    the floor rule makes their text always longer. The path is open only
    to rows that replace scalar text (none in batch 1).
  - `[D155]` **RULED "fastest wins" (item 4):** code space is never a
    SIMD named benefit, and the bar is measurably faster only. The
    named-benefit and TRADE routes are closed for SIMD rows (§R4.9.6).
- **Q-R9-5. Does a re-opened SIMD comparison ever block a scalar
  change?**
  - **Recommend NO.** The scalar change lands on its SIMD-off reading
    (D147). C19 flips the affected records to STALE and is never red for
    it (`[r9 M-8]`); the next bench submission re-measures them.
  - The SIMD row's new loss is filed as an issue row (D144 item 3), and
    the kit narrows or removes the row afterwards.
  - Only a wrong answer is a disaster.
  - `[D155]` **RULED NO (item 5):** a later SIMD loss never blocks a
    scalar change.
- **Q-R9-6. The floor rule.** Every SIMD-on rendering is its SIMD-off
  rendering plus text inside level guards, so a SIMD-on artifact still
  compiles and runs (at scalar speed) on any target.
  - **Recommend YES.** It costs only source bytes, gives one scalar
    spelling, and makes C18 possible: an independent check needing no
    timing, now with an on-target leg (C-6).
  - The alternative, SIMD-on text with no scalar fallback, is smaller
    but untestable off-target. Addendum 6 permits it but does not
    require it.
  - `[D155]` **RULED YES, AMENDED (item 6):** no `#if`/`#ifdef` inside a
    function body (restated by add. 1 / Q-R9-10: a selector's whole body
    may be the `#if` chain, one call per arm). The choice is made at file scope, by per-level
    `static inline` helpers and a selector, and the body makes one plain
    call. SIMD-off routes through the helper too, as a one-time measured
    byte move and abi event. Applied in §R4.9.2.3 (the rule restated),
    §R4.9.2.5 (the shape), §R4.9.2.6 (R4e′.0b) and §R4.9.8 (C18).
- **Q-R9-7. Deny granularity.**
  - **Recommend ONE deny per (form, width) row** (`vrun-w16`,
    `vrun-w32`), through the ONE carrier (`--memfn=`, options.def;
    `[r9 F-2]`), and no per-form umbrella row, because the layer switch
    is the umbrella.
  - Per-width denies are what let the w32 rung be measured against the
    w16 rung it displaces at the same `-march`.
  - `[D155]` **RULED as recommended (item 7):** one deny per (form,
    width), carried by one `--memfn=` flag (RQ-1).
- **Q-R9-8. The cascade's dependency, decided before its trigger fires.**
  A run-time cascade reads libgcc's `__cpu_model` through
  `__builtin_cpu_supports`, so a cascade artifact needs libgcc at LINK
  time (`-nostdlib`/freestanding links fail). requirements.md N-4 forbids
  that for the portable forms.
  - **Recommend:** ADMIT it under SIMD-on only, x86-64 Linux/ELF only,
    under C-4's guard (which includes `__SSE2__`, so `-mgeneral-regs-only`
    and `-mno-sse` builds, the kernel and freestanding ones, get the
    floor), with the spec stating the link dependency.
  - The cascade itself stays filed until its probe cell exists.
  - `[D155]` **RULED (item 8):** the libgcc ISA-cascade dependency is
    allowed, guarded and stated in the spec. The cascade itself is now
    `[MEMFN-RTDISPATCH]` (§R4.9.3.1), filed.
- **Q-R9-9. Do D84's emitted-size caps count guarded SIMD bytes?**
  `[r9 C-3]` Selection readers ignore guarded bytes by construction
  (§R4.9.2.4). The two REFUSAL caps (code bytes 500,000, total 1,000,000)
  are a different question: they protect the consumer's COMPILE budget
  (D45), and at `-march=L` the guarded text is compiled.
  - (a) EXCLUDE guarded bytes from both caps, and hold the compile bound
    by a per-row CONSTANT bound on guarded text (`guarded_max`), stated
    by the kit and checked by G2;
  - (b) INCLUDE them: a pattern near a cap compiles at SIMD-off and is
    refused at SIMD-on.

  **Recommend (a)**: SIMD-on then never changes a refusal (C-SEL holds
  for the refusal set too), and the extra compile cost is bounded by
  `nsites × max guarded_max` instead of being unbounded and unchecked.
  `limits.md` states the rule either way.
  `[D155]` **RULED (a) (item 9):** the D84 caps exclude guarded SIMD
  bytes, and each row carries its own bound (`guarded_max`, §R4.9.2.4).
- `[D155]` **Q-R9-10. Which file-scope shape does "the body makes one plain
  call" mean?** **RULED shape (c)** (D155 addendum 1, Frank 2026-10-08,
  confirmed to the manager). The FUNC is written ONCE, and its WHOLE BODY
  is the `#if`/`#elif`/`#else` chain with exactly one helper call per arm
  (§R4.9.2.5). The rule, verbatim: *"a function
  that does work never contains `#if`; a selector function's whole body
  may be the `#if` chain, one call per arm, and nothing else."* This
  amends item 6's "no `#if` inside function bodies". An intermediate shape
  (b), a file-scope level macro, was ruled and then superseded the same
  day by (c) (D155 addendum 1). SIMD-off costs +139 B per FUNC (the FUNC
  and `<fn>__body`; `[r9b]` measured on the pre-(c) rendering, re-measured
  by G1), and C18 sees exactly one replaced line per SIMD FUNC.
  C18's leg (d) allows ONLY the selector shape (§R4.9.8).
- `[D155]` **Q-R9-11. Where does a site's FREQUENCY CLASS live?** **RULED**
  (D155 addendum 1; kit-decided): a `freq` column in `DELEG_SITES`, built
  only when `[MEMFN-RTDISPATCH]` triggers, and NOT an `MF_P_INLOOP` policy
  flag. `[MEMFN-RTDISPATCH]` needs a per-site INFREQUENT/FREQUENT fact. It
  is not `MF_P_INLOOP`: that bit comes only from D91's budget, which puts
  OFS in budget 1, while OFS's FUNC is called on every re-seed inside the
  DFA scan loop (§R4.9.3.1), and a SIMD row DECLINES an `INLOOP` site
  through `policy` (§R4.9.2.3), so overloading it would silently remove
  OFS from every SIMD row. The column is set only there and checked like
  C10; it is crossed into `mf_site` as a stated field in the
  `MF_SITE_ABI` bump of the row that first reads it. Build nothing now
  (D77: the field is born with `[MEMFN-RTDISPATCH]`'s first design, at its
  trigger). Until then this revision RECORDS each first-batch site's class
  (§R4.9.3.1's table).

### R4.9.11 pcrec-side requests for main (each filed later as its own request; not designed here)

| id | what | why | movers | when |
|---|---|---|---|---|
| RQ-0 | **none for the seam.** R4e′.0 is kit-side end to end: the kit owns `ofs_fn_define` and its callers. pcrec's role is its identity gates as the control | `[r9 F-1]` | 0 | — |
| RQ-1 | **the `--memfn=` carrier**: a CLI flag, a config directive and a `pcrec_options` field carrying one opaque string, validated once per compile by `mf_opts_check` (its refusal text shown unchanged, D26), and copied into every site's `opts` (§R4.4.1). `[r9 F-8]` It changes a PUBLIC struct, so it carries the `lib/pcrec.h` hunk and spec hunks in `cli.md` and `registry.md` §6; its cross-source composition rule is stated (a string axis: silent file-wins, option_sets.md §2.5a); at `-fno-memfn-simd` it is accepted and inert, and the spec says so | no kit row has a pcrec-reachable OFF arm today (F-R9-6) | 0 | before batch 1 AND before R4d |
| RQ-2 | `[D155]` (Q-R9-3 RULED (a)) **the second pick** (Q-R9-3 (a)): `pcrec_find_pick2` as §2.3 T7's PICK reader, set by the PRE/OFS builders into `mf_pred.plan_pos2`. **SUPERSEDED by D157 and BUILT** (lane rq2, 2026-10-09, `docs/dev/lanes/rq2_report.md`): pcrec states the FACT, `mf_pred.rank_n`/`rank_pos`/`rank_ppm` (the run term's positions ordered by pcrec's prior rate, each with its rate, and a count; `MF_RANK_MAX` 32), filled by the PRE/OFS builder through `pcrec_find_run_rank`; `MF_SITE_ABI` 8 -> 9 off main | the fused filter's KB (§R4.9.5 item 10) | 0 | before batch 1's tier-U sweeps |
| RQ-3 | **SIMD bytes neutral to every length DECISION** (`[r9 C-3]`, now unconditional): pcrec's sink implements `simd_open`/`simd_close` by counting bracketed bytes into the buffer's `simd_guarded`, and every reader that today reads `pcrec_sb_len_uncut` for a decision (the VM entry-shape knee, the `fit_rungs[]` size measurement, the size-quoting stamps) reads `len_uncut − simd_guarded` through one helper. D84's caps follow Q-R9-9's ruling, with its `limits.md` hunk | F-R9-5: SIMD-on must not move a rung, a ladder step or a stamp value | 0 at SIMD-off | before batch 1 |
| RQ-4 | **a tier-U timing slot on the dev box** (`[r9 M-1]`, demoted from "the verdict box's slot"): one logical CPU named by main, its sibling idle per `thread_siblings_list`, load1 < 0.5 | §R4.9.5 items 1-2: the sweeps and the veto | 0 | before batch 1's tier-U sweeps |
| RQ-5 | **the bench submission** (`[r9 M-1, M-4]`): §R4.9.5.1's contents, carried by main to `inbox_from_pcrec.md` (D78), with the bench box facts asked of the bench dev and the span-ladder subbench request; main schedules each box (the dev box through its slot channel) | official verdicts; bench testees BEFORE acceptance | 0 | after batch 1 lands as CANDIDATE; before any line becomes ACCEPTED |
| RQ-6 | `[D155]` **R4e′.0b's abi event on pcrec's side**: in the kit's routing commit, bump pcrec's abi ("the next number at landing"), find every reader by grep (D94: the `.abi` stamp, test expectations, spec sentences, the gate's pins), re-pin the identity gates, run `make test-codegen` and the suites that count; run the G1 census of §R4.9.2.6: movers by id against the `fn` census, the un-done text diff, assembly identity at `-O2` default and v3, and timing ONLY for a non-identical mover | D155 item 6: SIMD-off routes through the helper, so every FUNC's text moves once | every artifact with a FUNC part (+139 B per FUNC); predicted 0 assembly movers at `-O2` | with R4e′.0b, after R4e′.0 and before batch 1 |

### R4.9.12 Disposition completeness: every panel id, and where it is applied `[r9]`

All 43 finding ids of `../../dev/reviews/2026-10-08-r9-memfn-simd.md`.
"Applied" names the section that carries the `[r9 <id>]` mark.

| id | severity | disposition | applied in |
|---|---|---|---|
| C-1 | MAJOR | ACCEPTED: T defined once (`max_reach`), reach from the highest read; G2 plant "reach one short" | §R4.9.3; §R4.9.5 item 10; §R4.9.7 G2 |
| C-2 | MAJOR | ACCEPTED, folded into the F-1 seam: BODY first, `over` column, the ladder = named same-form `rungs` | §R4.9.2.1; §R4.9.2.2; §R4.9.2.3 |
| C-3 | MAJOR | ACCEPTED in part: stamps as keys, sizes normalised; neutrality by construction (`simd_open`/`simd_close`, RQ-3); RUN_WORDS/MEMFN_LIBC declared; D84 cap → Q-R9-9 | §R4.9.1 F-R9-5; §R4.9.2.4; §R4.9.8 C-SEL; §R4.9.10 Q-R9-9; §R4.9.11 RQ-3 |
| C-4 | MAJOR | ACCEPTED: `__SSE2__` and `__x86_64__` in the cascade guard; cascade above the full ladder; applies as a row-order fact; libgcc link dependency in Q-R9-8 | §R4.9.3; §R4.9.10 Q-R9-8 |
| C-5 | MAJOR | ACCEPTED: G2 multi-hit, near-miss, `pos` sweep, exact returned position; plants per path; per-path coverage floors; `-mgeneral-regs-only` as w16's compiled-out level; the sweep is a smoke check | §R4.9.6 item 4; §R4.9.7 G2; §R4.9.8 |
| C-6 | MINOR | ACCEPTED (`[D155]` leg amended to one replaced call per SIMD FUNC, §R4.9.8): C18's insertion-only leg per live level; the `#if` guard lint; "preprocessed-equal" | §R4.9.2.3 (floor rule); §R4.9.8 C18 |
| C-7 | MINOR | ACCEPTED: the intrinsic `#include` inside the level guard at file scope, before the helper; no `MF_INC_` bit | §R4.9.2.2 |
| C-8 | MINOR | ACCEPTED: guards name `__x86_64__` and exclude ILP32; C9-x86 adds x86-64-v2 and sandybridge | §R4.9.2.2 (`levels.def`); §R4.9.8 C9-x86 |
| C-9 | MINOR | ACCEPTED: the stamp names rendered levels; no level guard in the `.h`; §6.3 hunk | §R4.9.2.3 (stamp); §R4.9.2.2; §R4.9.7 spec hunks |
| C-10 | MINOR | ACCEPTED: G2 poisons `[buf, s)` and `[s+n, end)`; the sweep's ASan gap stated | §R4.9.7 G2 |
| C-11 | MINOR | ACCEPTED as "drop the claim": the route is a pcrec-side bin key, not a kit fact; a losing route bin blocks or needs a stated fact | §R4.9.2.1; §R4.9.6 item 3 |
| C-12 | MINOR | ACCEPTED: the in-block verify goes through the BODY's `rc_row`; RUN_WORDS declared; `denies` served as the BODY's | §R4.9.2.3 (row contracts); §R4.9.2.4 |
| M-1 | BLOCKER | ACCEPTED as REFRAMED by D144 addendum 4: two tiers; official = bench on each targeted box; testees before acceptance; requests via main | §R4.9 intro; §R4.9.0; §R4.9.1 F-R9-4; §R4.9.5; §R4.9.5.1; §R4.9.10 Q-R9-1; §R4.9.11 RQ-4, RQ-5 |
| M-2 | MAJOR | ACCEPTED: `state`, `tier`, `cpu_class`, bench and toolchain pins in `simd_accept.tsv` | §R4.9.6 (record) |
| M-3 | MAJOR | ACCEPTED as reframed: judged on every bench box running the level; a loss on any blocks the level; one-box levels judged there | §R4.9.5 (table); §R4.9.6 (bar, disagreement); §R4.9.10 Q-R9-2 |
| M-4 | MAJOR | ACCEPTED: the bench submission spec; `-march=<level> -mtune=generic`, never native | §R4.9.5 item 4; §R4.9.5.1 |
| M-5 | MAJOR | ACCEPTED: minimum effect, pre-registered bins and cells, interleaved arms, repeats, cell count reported, floor from the null population | §R4.9.5 items 4, 5, 8; §R4.9.6 (bar) |
| M-6 | MAJOR | ACCEPTED: the alignment-flag band withdrawn; the null population is the band | §R4.9.5 items 5, 6 |
| M-7 | MAJOR | ACCEPTED: no "< 8 movers" exclusion; bins by cause, distinct shapes, recounted each reading; synthetic witnesses | §R4.9.6 item 3 |
| M-8 | MAJOR | ACCEPTED: C19 flips to STALE, never red for it; population digest; transcript binding; bench versions in the record | §R4.9.6 (record, C19); §R4.9.8 C19 |
| M-9 | MAJOR | ACCEPTED: reach is a correctness bound; both cut-overs swept in tier U; every regime constant labelled; MEASURED-UNOFFICIAL | §R4.9.3; §R4.9.5 item 10 |
| M-10 | MAJOR | ACCEPTED: the hit-spacing ladder in both tiers; "dense" claim withdrawn | §R4.9.5 item 7; §R4.9.7 |
| M-11 | MAJOR | ACCEPTED: `levels.def` `forbid` column (PDEP/PEXT, gathers); `mf_formdecl.insn`; G2/C9 list them; the submission names them | §R4.9.2.2; §R4.9.5.1 item 7; §R4.9.7 G2 |
| M-12 | MINOR | ACCEPTED: R-1 relabelled tier-U evidence on an official CPU class | §R4.9.1 F-R9-4; §R4.9.7 |
| M-13 | MINOR | ACCEPTED: F-R9-1 stated as text identity; the objdump comparison reported | §R4.9.1 F-R9-1; §R4.9.5.1 item 7 |
| M-14 | MINOR | ACCEPTED: the sibling from `thread_siblings_list`; sibling busy% and frequency recorded; bench discipline asked | §R4.9.5 item 2; §R4.9.5.1 item 1 |
| M-15 | MINOR | ACCEPTED: C18's named filter and negative control; C-SEL's literal floor | §R4.9.8 |
| M-16 | MINOR | ACCEPTED: the named-benefit path is size-free for SIMD rows; Q-R9-4 revised | §R4.9.6; §R4.9.10 Q-R9-4 |
| F-1 | BLOCKER | ACCEPTED: the zero-mover FUNC-body seam `fn_rows[]` (BODY/PREFIX slots), no decorator; reach enumerated, OFS run-pinned by its own cell or a structural exclusion | §R4.9.2.1; §R4.9.7; §R4.9.11 RQ-0 |
| F-2 | MAJOR | ACCEPTED: ONE deny carrier (`--memfn=`); `MF_D_RUN_OVERLAP` the named legacy exception; layer/budget read through options.def | §R4.9.2.2; §R4.9.2.3; §R4.9.8 siblings |
| F-3 | MAJOR | ACCEPTED: `policy`/`budget` as `fields.def` fields with `DECLINED`; ONE shared walk; H1 answered (not met) | §R4.9.2.3; §R4.9.8 |
| F-4 | MAJOR | ACCEPTED, covered by M-1; `MEMFN_OPTS` flagged plausibly triggered | §R4.9.5.1 |
| F-5 | MAJOR | ACCEPTED: one `simd` sweep arm with named projections; `c9_floor` folded into `row_floors.tsv`; `run_rows.sh` checks the record's row set; sweep = `test-axes` arm | §R4.9.8; §R4.9.6 (record) |
| F-6 | MAJOR | DECIDED NO by the manager: M6's `MF_SITE_ABI` 8 carries no SIMD ADVANCE bound; filed with its trigger; Q-R10-10 answered | §R4.9.0; §R4.9.7 filed list |
| F-7 | MINOR | ACCEPTED: the filed list and the `arms[]` facts re-read against the kit tip (N6 retired, N7 delegated, N7U pending, VMSTRIDE M6, MLINE M4, the rmin loop) | §R4.9.2; §R4.9.7 filed list |
| F-8 | MINOR | ACCEPTED: "pcrec-reachable"; composition rule; inert at SIMD-off; public-struct hunks | §R4.9.1 F-R9-6; §R4.9.2.3; §R4.9.11 RQ-1 |
| F-9 | MINOR | ACCEPTED: rev stays 4.9; the manager reconciles with the kit tip's 4.8; M6 claims no rev; `docs/design/CLAUDE.md` updated | §R4.9 intro; the header; `docs/design/CLAUDE.md` |
| F-10 | MINOR | ACCEPTED: intrinsics, inside the guard; self-contained; `MEMFN_LIBC` unaffected | §R4.9.2.2 |
| F-11 | MINOR | ACCEPTED: the lifecycle (CANDIDATE, ACCEPTED, STALE, REJECTED); a row lands with CANDIDATE lines and renders | §R4.9.6 |
| F-12 | MINOR | ACCEPTED: `INERT:SIZE` withdrawn; the SIMD × tune cell goes into R4d's D103 diff | §R4.9.2.3 |
| F-13 | MINOR | ACCEPTED: `mf_levels()` with `test_march`, a literal floor | §R4.9.2.2; §R4.9.8 |
| F-14 | MINOR | ACCEPTED: [EMIT-ALIGN] and O-69 cited; the governor at launch recorded | §R4.9.5 item 1 |
| F-15 | MINOR | ACCEPTED: the stamp reports text; the spec hunk says so; Mac movers are text movers | §R4.9.2.3 (stamp); §R4.9.5 item 9 |

`[D155]` **D155's items** (Frank's rulings on Q-R9-1..9, main 3b1fd77c, and
Q-R9-10/11, D155 addendum 1; not panel ids, and not counted in the 43):

| D155 item | ruling | applied in |
|---|---|---|
| 1 (Q-R9-1) | resolved by D144 addendum 4 | §R4.9.10 |
| 2 (Q-R9-2) | every box running a level: a loss anywhere blocks, a win somewhere is required; CANDIDATE first | §R4.9.10 |
| 3 (Q-R9-3) | pcrec states `plan_pos2` | §R4.9.10; §R4.9.11 RQ-2 |
| 4 (Q-R9-4) | "fastest wins": code space is never a SIMD named benefit | §R4.9.6; §R4.9.10 |
| 5 (Q-R9-5) | a later SIMD loss never blocks a scalar change | §R4.9.10 |
| 6 (Q-R9-6) | floor rule YES, AMENDED: no `#if` in a function body (restated by add. 1 / Q-R9-10: a selector's whole body may be the `#if` chain); file-scope helpers; SIMD-off routes through the helper, as a measured abi event | the summary; §R4.9 short list; §R4.9.2.1 (slots, assembly); §R4.9.2.3 (the rule restated, the withdrawn shape, the STMT note, the stamp); §R4.9.2.4 (whole-definition accounting); §R4.9.2.5 (the shape, probes); §R4.9.2.6 (R4e′.0b, G1); §R4.9.3 (entry tests); §R4.9.4; §R4.9.7; §R4.9.7.2; §R4.9.8 (C18 amended, the routing gate); §R4.9.9; §R4.9.10; §R4.9.11 RQ-6; §22 |
| 7 (Q-R9-7) | one deny per (form, width) through `--memfn=` | §R4.9.10 |
| 8 (Q-R9-8) | the libgcc cascade dependency is allowed, guarded and spec-stated | §R4.9.3; §R4.9.10 |
| 9 (Q-R9-9) | the D84 caps exclude guarded SIMD bytes; per-row bound | §R4.9.2.4; §R4.9.10 |
| add. 1 (Q-R9-10) | shape (c): the FUNC written once, its whole body the `#if` chain, one call per arm; "a function that does work never contains `#if`; a selector function's whole body may be the `#if` chain, one call per arm, and nothing else" | the summary; §R4.9 short list; §R4.9.2.1; §R4.9.2.3; §R4.9.2.4; §R4.9.2.5; §R4.9.8 (C18 leg (d)); §R4.9.10 |
| add. 1 (Q-R9-11) | a `freq` column in `DELEG_SITES`, built only when `[MEMFN-RTDISPATCH]` triggers; not `MF_P_INLOOP`; kit-decided | §R4.9.3.1; §R4.9.10 |
| filed `[MEMFN-RTDISPATCH]` | runtime dispatch, with its terms (frequency class, target-attribute copies chosen once, a non-cascading set, per-arch artifacts already served) | §R4.9.3; §R4.9.3.1; §R4.9.10 Q-R9-11 |
| facts recorded with D155 | batch 1 narrowed to `fn-pair`; `set1` broadcasts are rebuilt at each entry (r9fu) | already in §R4.9.7.1, §R4.9.7.2 |

Totals: 43 ids (2 BLOCKER, 20 MAJOR, 21 MINOR); 42 applied as
dispositioned, 1 (F-6) decided NO and applied as that decision. None
could not be applied.

**Follow-up rows `[r9fu]`** (the manager's two narrow gaps after the
revision; not panel ids, and not counted in the 43):

| id | gap | disposition | applied in |
|---|---|---|---|
| r9fu-1 | the glibc-inside trap (D147 addendum 13), stated only for PF/MLINE; is each batch-1 site's scalar twin glibc-backed, and did R-1 compare against it? | MEASURED: every batch-1 site class's FUNC calls glibc `memchr` (`fn-pair` 2 streams, `fn-memchr` 1), with no other libc call on the hot path. R-1's `emit` IS the glibc-backed `fn-pair` twin, so the evidence stands at tier U for dense picks. A sparse-pick `fn-pair` cell is owed to the bench. `fn-memchr` has no same-function cell, so it is trigger-grade. `over` narrows to `fn-pair`, and `vrun` over `fn-memchr` is filed with five cells. OFS run-pinned and the exact bin leave batch 1. The bar names the twin as "BODY + glibc". Q-R9-2 is refined | §R4.9 summary; §R4.9.1 F-R9-8; §R4.9.2.1 (table, OFS para); §R4.9.2.4 (row table); §R4.9.5.1 item 3; §R4.9.6 items 1, 3; §R4.9.7 (population, evidence, G2, filed list); §R4.9.7.1; §R4.9.10 Q-R9-2 |
| r9fu-2 | `[MEMFN-ENTRYSINK]`: does §R4.9 assume a function-entry setup point, and which first-batch form is a trigger candidate? | CHECKED: nothing assumes one. MEASURED (hand twin, gcc 15.2): literal broadcasts are rematerialized from immediates at each rung entry and never hoisted, and a file-scope `static const` does not change that. So the plan row's "gcc hoists it or it is a constant" fails here; plan.md's row text is the manager's to correct. Candidates: none in batch 1 (every PRE FUNC is called once per matcher call). The filed `vrun` over OFS run-pinned is the one candidate (its FUNC runs inside the DFA scan loop on every re-seed). No sink designed | §R4.9 summary; §R4.9.7.2 |

---

## R4.8. Revision 4.8: M1b's contract (R-5) `[rev4.8]`

(Top-level, like §R4.7. It sits first because it corrects §14.8, extends
§14.0's sink and hooks, and rules how bit 43 crosses (§14.10).)

**The input.** Request R-5 (`memfn/docs/requests.md`): M1b, runcmp
migrates, zero movers. The scope pass (`worktrees/m1bscope-scratch/
m1b_scope.md`, read-only, written at main 54c42e36) found one HIDDEN
BYTE MOVE in §14.8 as written and one contract gap (`--list-axes`). The
kit manager ruled Q-M1b-1..8 before the lane was briefed. They are kit
contract decisions under D146, plus Q-M1b-6, which is main's.

### R4.8.0 Each ruling, and where it now lives

| id | the question | ruling | where it lives |
|---|---|---|---|
| Q-M1b-1 | fill `mf_art_begin`'s `denies` too? | **Yes, from the SAME PCREC-bit → `MF_D_*` map table** that fills every site's `denies`, and the kit ASSERTS `site.denies == art.denies` at `mf_define` (a loud refusal). Flags are per compile, so the art-level helper and stamp decisions cannot disagree with a site's | §14.10 `[rev4.8]`; `memfn.h` `mf_art_begin`; `compose.c` `mf_define`; pcrec's map table (`src/gen/memfn_sites.c`) |
| Q-M1b-2 | the unquoted stamp channel | **(i) a NEW sink op `stamp_int(u, name, long long)`, APPENDED at the END of `mf_sink`**, because G2's and other sink initializers are positional; every initializer is updated | §14.0, §14.2, §14.8 `[rev4.8]`; `memfn.h` `mf_sink`; pcrec's stamp sink (`memfn_stamps.c`) |
| Q-M1b-3 | the run-compare rows for `--list-axes` | **A kit accessor** (the `mf_options()` precedent). pcrec's `run-overlap` section reads it and maps `MF_D_RUN_OVERLAP` back to bit 43 through the same map table, so stream 5 and the registry stay byte-identical | §14.10 `[rev4.8]`; `memfn.h` `mf_run_rows`; `src/dump/axes_dump.c` |
| Q-M1b-4 | S285's home | **KIT-side**, on the renderer's read of `run_len` (its intent: the compare tests `run_len + 1` bytes) | §R4.8.1 item 6; `tests/mech/sabotages/S285_*` |
| Q-M1b-5 | a VMRUN site's `empty` | **EXCLUDED** (pcrec's guard precedes the EXPR, `guard_by_caller`) | §15.6 `[rev4.8]`; `emit_vm.c`'s VMRUN builder |
| Q-M1b-6 (main) | VERIFY as a DELEG_SITES row? | **No.** VERIFY is carried as a TERM of the OFS and PRE sites (the SETREST precedent). VMRUN DOES get a DELEG_SITES row (D91 budget 2) and a `site_census` door. The manifest's VERIFY and VMRUN rows flip to `delegated` | §R4.8.1 item 4; `src/gen/memfn_sites.def`; `tests/memfn/site_manifest.tsv`; `site_census.DOORS` |
| Q-M1b-7 | `run_cmp` and `note`'s helper role | **Retire `mf_hooks.run_cmp` outright, and end `note`'s helper-carrying role, in ONE `MF_SITE_ABI` 3 → 4 bump with `stamp_int`.** `MF_VOCAB` stays 2 (VERIFY/BOOL over RUN is already in the vocabulary). Kit-internal: no pcrec abi bump, no artifact byte | §14.0 `[rev4.8]`; `memfn.h` |
| Q-M1b-8 | sabotage ids | **S570-S579 only**; more needs a ruling | the lane report |

8 rulings, 8 placed.

### R4.8.1 What changed in the design

1. **§14.8's RUN_WORDS sentence is corrected (Q-M1b-2).** It said the kit
   writes `RUN_WORDS` through the sink's `stamp` op and the bytes are
   unchanged. They are not: pcrec's `stamp` (`sink_stamp` →
   `pcrec_sb_stamp_str`) writes `"\"%s\""`, so `#define RX_RUN_WORDS 0`
   would become `#define RX_RUN_WORDS "0"` on 100% of the corpus, and its
   C type would change from integer to string (a consumer's
   `#if RX_RUN_WORDS > 0` breaks). The kit writes it through `stamp_int`,
   which pcrec renders as `pcrec_sb_stampf(…, "%lld", …)`, the call
   `pcrec_emit_runcmp_stamp` made. `mf_stamps` writes THREE lines in
   order: `RUN_WORDS`, `MEMFN_FORMS`, `MEMFN_LIBC`. pcrec deletes its two
   `pcrec_emit_runcmp_stamp` calls, so the memfn mark sits exactly where
   the `RUN_WORDS` line was. The count is identical: `mf_art` is per Job
   attempt as `Job.rc_words` was, and the stamp pass runs before the size
   measurement.
2. **The helpers are the kit's (§14.8).** `mf_art` records the word widths
   used and declared (bit W for width W) and the words-form count. A FUNC
   definition's arm declares, where pcrec's file-scope `note` did, the
   widths its run terms take (the art-level "flush ALL pending widths"
   semantics of `pcrec_emit_runcmp_helpers`, never per site); an EXPR site
   only records them; `mf_flush_helpers` at pcrec's prologue writes
   whatever is pending. The VM body is written before the prologue, so
   its widths reach the prologue's flush. The helpers' comment opens
   through `cmt_open(MF_CMT_NONESSENTIAL)` (no hook carries a tier at the
   prologue; `MF_CMT_NONESSENTIAL` equals pcrec's `PCREC_CMT_NONESSENTIAL`,
   asserted on pcrec's side). CHOSEN by the lane.
3. **Bit 43 crosses (§14.10, Q-M1b-1).** ONE pcrec table maps bit 43 to
   `MF_D_RUN_OVERLAP`. `pcrec_memfn_site` fills every site's `denies` from
   it (OFS, PRE, VMRUN: the OFS/PRE run term honours bit 43 too), and the
   attempt's `mf_art_begin` takes the same value. Every kit arm that
   renders a run compare honours it: exact compares fall to `memcmp`,
   masked ones to `bytes`.
4. **VERIFY is a term, VMRUN a site (Q-M1b-6).** The OFS/PRE run term is
   rendered by the verify chain with the kit's own compare. The VM's two
   callers (`vm_lit`, `vm_isl_emit`) describe one VMRUN site each through
   a new door, `pcrec_memfn_emit` (→ `mf_emit`): VERIFY / EXPR / BOOL, one
   REQUIRED RUN term at the node's depth (or 0), `guard_by_caller` 1,
   `empty` EXCLUDED, use DISCARD, policy INLOOP from the row. pcrec keeps
   its guard and its `goto` tail.
5. **The kit's runcmp arm.** `memfn/src/runcmp.c` holds the four rows
   (`words`, `overlap`, `bytes`, `memcmp`), their writers and the arm
   (VERIFY / EXPR / BOOL, one RUN term, `guard_by_caller`, every run byte
   within its mask) above the generic row. An unsatisfiable run byte
   (Q-G2-13) is left to the generic row, because `bytes` would spell a
   constant `(b & K) == T` that `-Wtautological-compare` flags. The
   overlap lengths and the width rule are DERIVED (D149): gcc's lowering
   of a constant `memcmp` (`docs/dev/memcmp_lowering_study.md` §3).
6. **S285 is kit-side (Q-M1b-4)**, on the renderer's read of `run_len`.

### R4.8.2 The three standing design questions, for this revision

1. **Measurement regime: NOT RELEVANT.** No timing is read or produced;
   zero movers by construction (the identity gate, I1 at IMPLEMENT).
2. **Independent control: RELEVANT.** I1 compares the kit's text with
   pcrec's own runcmp at every call of the IMPLEMENT commit (each
   compare, each define's span, the prologue's helpers, the RUN_WORDS
   line); the identity gate compares artifacts with main 993f8c1d over
   the corpus and every axis at both comment tiers. Neither reads the
   kit's own record of what it did.
3. **What moves when data is regenerated: NOT RELEVANT.** No data file
   or emitted byte moves. C5's run-bearing fixture pins move (the
   fixtures' stand-in `run_cmp` hook is gone and the kit compares runs
   itself): a change-detector re-pin under `tests/` (§17.4), no artifact.

---

## R4.7. Revision 4.7: the kit's contract after G2 `[rev4.7]`

(Top-level, like §R4.6. It sits first because it rules on §14.3's
operations, §14.4's empty range, §14.6's shape bounds and §14.7's caller
guard, and because it closes Q53-Q55.)

**The inputs.**
- G2, the kit's own tests, written D27-blinded by lane memfng2
  (`docs/dev/lanes/memfng2_report.md`: §4.3 has the findings, §7 the
  questions). It found:
  - **F1**, an answer defect: VERIFY ignored its empty range, and at
    `lo > n` it read past `n`;
  - **F2**, a totality gap: ON_CAND refused `empty = NOP`;
  - **F3**, a loudness gap: an out-of-enum `empty` or `need` rendered
    code.
- The kit session's rulings on F1-F3 and Q-G2-1..17. They are kit
  contract decisions under D146: the kit owns its own vocabulary.
- D147 addendum 10 (`docs/dev/decisions.md`): Frank ruled Q53-Q55 as
  the kit recommended.

**What was built** (lane memfnfix, `docs/dev/lanes/memfnfix_report.md`):
- the three fixes;
- the refusals, in `memfn/src/compose.c` (`site_check`, `pred_kinds`);
- every RULED statement, in `memfn/include/memfn.h`;
- `make test-memfn-g2`, G2's quick tier as a `make test` section;
- `make test-memfn-g2-full`, opt-in.

No emitter calls the kit, so no artifact byte moved (the identity proof
is in the report).

### R4.7.0 Each ruling, and where it now lives

| id | what G2 found or asked | ruling | where it lives |
|---|---|---|---|
| F1 | VERIFY never tested its range. At `end_back = 1, lo = n − 1`, or `lo ≥ n` with negative offsets, it answered "holds". At `lo > n` it read past `n` | **FIX.** VERIFY honours `[lo, n − end_back)`. An empty range gives the site's `empty` outcome, and the text never reads outside `[floor, n)`. The exception is `guard_by_caller`, where the caller asserts the range | §14.3, §14.4 `[rev4.7]`; `generic.c` `core` (VERIFY); `memfn.h` `MF_OP_VERIFY` |
| F2 | ON_CAND with `empty = NOP` refused | **FIX.** It renders, with no visit on an empty range. Totality | §14.4 `[rev4.7]`; `generic.c` `stmt_on_cand`; `site_check` (refusal deleted) |
| F3 | `empty = 9` and `need = 5` rendered code | **FIX.** Refused loudly, like every other out-of-enum field. The same check now covers `form`, `use`, `consumer` and a predicate's `need` | §14.6 `[rev4.7]`; `site_check`, `pred_kinds` |
| Q-G2-1 | may `lo` exceed `n`? | **Yes.** It is legal and means EMPTY | §14.4 `[rev4.7]`; `memfn.h` `lo` |
| Q-G2-2 | ON_CAND with NOP: in the vocabulary? | **Yes** (= F2) | as F2 |
| Q-G2-3 | EXPR/FUNC with `empty = NOP` | **REFUSED** (already refused at R4a) | §14.4 `[rev4.7]`; `site_check` |
| Q-G2-4 | ADVANCE with `empty = MISS` | **REFUSED** | §14.4 `[rev4.7]`; `site_check` |
| Q-G2-5 | reverse ADVANCE at `lo == n`: the hooks or §14.4's empty rule? | **OPEN.** No customer before M3. No code change | §14.4 `[rev4.7]`; `memfn.h` ADVANCE hooks |
| Q-G2-6 | `on_cand` below `floor` when `floor > lo` | **`floor <= lo` is the CALLER's precondition** | §14.7 `[rev4.7]`; `memfn.h` `floor` |
| Q-G2-7 | the lifetime of hook-returned strings | **They live until `mf_art_end`** | §14.2 `[rev4.7]`; `memfn.h` `mf_hooks` |
| Q-G2-8 | a conditional `on_cand` token that falls through | **It REJECTS, and scanning continues** (the R4a text already did this) | §14.7 `[rev4.7]`; `memfn.h` `on_cand`; `stmt_on_cand` comment |
| Q-G2-9 | SKIP with a SET term at offset ≠ 0 | **REFUSED** | §14.3 `[rev4.7]`; `site_check` |
| Q-G2-10 | `nterm = 0` | **REFUSED** | §14.6 `[rev4.7]`; `pred_kinds` |
| Q-G2-11 | RUN with `run_len = 0` | **REFUSED** | §14.6 `[rev4.7]`; `pred_kinds` |
| Q-G2-12 | ALL_PRESENT with `reverse = 1` | **REFUSED** | §14.3 `[rev4.7]`; `site_check` |
| Q-G2-13 | a run byte with bits outside its mask | **IN the vocabulary, literal formula; constant-false rendering allowed.** The term never holds. The kit may render that byte as `0`, with no masked compare, provided the answer is unchanged, and it NEVER normalises the byte into the mask. (First ruled REFUSED; REVISED, because G2's generated space exercises the shape and §14.6's totality says a well-defined site renders, §R4.7.2) | §14.6 `[rev4.7]`; `generic.c` `pred_test`; `memfn.h` `mf_term.run` |
| Q-G2-14 | a NULL `cursor` on ADVANCE | **Accepted.** Only `more`, `peek` and `step` are used | §14.3 `[rev4.7]`; `memfn.h` ADVANCE hooks |
| Q-G2-15 | `guard_by_caller` with negative offsets, or off EXPR VERIFY | **REFUSED** unless EXPR VERIFY with every offset ≥ 0 | §14.7 `[rev4.7]`; `site_check` |
| Q-G2-16 | does `cmt_open` write the comment opener? | **Yes.** The sink's `cmt_open` writes the opener and the sink writes the closer | §14.2 `[rev4.7]`; `memfn.h` `mf_sink` |
| Q-G2-17 | does `[lo, n − end_back)` apply to VERIFY? | **Yes** (= F1) | as F1 |
| Q-G2-18 | (R4c, lane CORE's F2) the pre-check arm is right only where `on_miss` LEAVES the site; may the kit read that from the hook's text? | **No: hooks are opaque. pcrec STATES it** in a new site field, `on_miss_leaves` (ON_MISS/ASSIGN; 0 = may fall through). An arm that needs it carries a `miss_leaves` predicate column in K2's first-match table; where it is 0 the generic row renders. `MF_SITE_ABI` 2 → 3; `MF_VOCAB` unchanged. CHOSEN by the kit manager 2026-10-06 | `memfn.h` `mf_site.on_miss_leaves`; `kit.h` `arm.miss_leaves`; `compose.c` `select_arm`, `site_check`; `precheck.c` (CORE's interim text sniff deleted) |
| Q53 | the libc record | **RULED YES** (addendum 10). The refined form is the design of record | §R4.3.3 `[rev4.7]`; §23 Q53 |
| Q54 | N7 under completeness | **RULED YES** (addendum 10), with the three corrections | §R4.3.4 `[rev4.7]`; §22 M7; §23 Q54 |
| Q55 | the kit's plan at SIMD-off | **ACCEPTED** (addendum 10). `<PREFIX>_MEMFN_OPTS` is FILED, not built | §23 Q55 |

F1-F3 and Q-G2-1..18 are 21 rows, all placed. Q53-Q55 are 3 of 3.

### R4.7.1 What changed in the design

1. **The range is the site's, on every op (F1, Q-G2-1, Q-G2-17).** The
   range is empty iff `lo + end_back >= n`, and `lo > n` is included.
   VERIFY was the one op whose text did not test it. Now every op
   reads nothing on an empty range and gives the site's `empty`
   outcome. `guard_by_caller` is the one place the CALLER asserts the
   range instead.
2. **Totality reaches ON_CAND's NOP (F2).** On an empty range the whole
   ON_CAND statement is skipped: no result write, no visit, no
   `on_miss`.
3. **The vocabulary's edge is loud (F3, Q-G2-3/4/9-12/15).** Each shape
   below is now refused by `mf_define`, where R4a rendered or misread
   it:
   - out-of-enum fields;
   - empty conjunctions;
   - zero-length runs;
   - an offset SKIP;
   - a reversed ALL_PRESENT;
   - an ADVANCE that misses;
   - a widened caller guard.
4. **An unsatisfiable run byte renders as constant false (Q-G2-13).**
   The site's answer is unchanged, and no tautological compare is left
   for `-Wall`/`-Werror` to flag.
5. **The caller's obligations are written down (Q-G2-6/7/8/14/16),
   and the art's error is stated STICKY.** None of them changes code.
6. **Q-G2-5 is recorded OPEN.**
7. **Q53-Q55 are RULED.** §R4.3.3's refined libc record and §R4.3.4's
   N7 scope are promoted from "proposal" to the design of record.
8. **Q-G2-18 (R4c; CHOSEN by the kit manager 2026-10-06).** Whether an
   ON_MISS/ASSIGN site's `on_miss` transfers control out of the site is a
   FACT pcrec states (`mf_site.on_miss_leaves`), never something the kit
   reads off the statement's text. The pre-check arm (§15.5) tests its
   predicates in sequence and leaves the set rest without an empty test,
   both right only where a miss leaves; its row in K2's table carries the
   `miss_leaves` predicate column, so a site that does not state it falls
   to the generic row. `site_check` refuses a value other than 0/1 and a
   nonzero value off ON_MISS/ASSIGN. This one ruling moves `MF_SITE_ABI`
   2 → 3 (it supersedes §14.0's `2`); `MF_VOCAB` stays 2. No emitted byte
   moves: pcrec's pre-check states 1 (its miss is `return 0;`).

Items 1-7: `MF_SITE_ABI` and `MF_VOCAB` do not move. No caller exists yet, the
(op, handoff, term kinds) table is unchanged, and every newly refused
shape was either never sent or never meaningful.

### R4.7.2 The ruling the control revised (Q-G2-13)

Q-G2-13 was first ruled REFUSED. G2 generates unsatisfiable runs on
purpose: a run byte with one bit its mask clears. The generator
(`g2_gen.c`, `unsat` in the RUN term cells) does this for 36 sites:
offsets −3..8 × lengths 5, 16 and 27 × one free bit. G2 expects them to
render under the literal formula, and the refusal made every G2 run read
36 generator failures, plus 17 missing RUN cells and the RUN-cell floor
line per compiler.

The kit session REVISED the ruling: the control is right. Under the
literal formula an unsatisfiable run term is well defined (it never
holds). §14.6's totality says a well-defined site renders, and refusing
it would only turn a correct answer into an error. So:
- the shape is IN the vocabulary;
- the kit renders the byte as `0`, the same answer with no
  `-Wtautological-compare` (36 lines per compiler under the literal
  `(b & m) == r` text, memfng2 §4.5);
- the byte is never normalised into its mask, which would be wrong
  under the formula.

G2 needed no change, and it now reads 0 failed.

### R4.7.3 The three standing design questions, for this revision

1. **Measurement regime: NOT RELEVANT.** No timing is read or produced.
   No emitter calls the kit, so the fixes move no artifact byte, and the
   identity proof shows 0 movers.
2. **Independent control: RELEVANT.**
   - G2 is the control, and it was not edited.
   - `run_g2.sh --quick` changes only the population and the schedule:
     - the gcc answer run keeps every site at the quick subject tier;
     - ASan and the witnesses run on every third batch, concurrently;
     - every judgement is the full run's own code;
     - the floors that scale are new literals (`QUICK_*`).
   - G2 generates none of these refused shapes: `nterm` 0, `run_len` 0,
     ALL_PRESENT `reverse`, an offset SKIP, ADVANCE MISS, and a
     `guard_by_caller` outside EXPR VERIFY or at a negative offset. Its
     refusal table does not cover them either, so they are UNTESTED by
     G2. A blinded author owes those cases, and the kit session files
     that (lane report §3).
3. **What moves when data is regenerated: NOT RELEVANT.** No data file,
   pin or emitted byte moves.

---

## R4.6. Revision 4.6: the r5 panel applied `[rev4.6]`

(Top-level, like §R4.5. It sits first because it overrides §14.5's
OPTIONAL lead, §14.0's static `use` column and §15.5's part numbering.)

**The input.** Request R-2 (`memfn/docs/requests.md`), after its panel:
the light D6 panel on rev 4.5
(`docs/dev/reviews/2026-10-05-r5-memfn-rev45.md`, with the critics' full
texts beside it). Critic A read the contract against pcrec's emitters at
abi 61 (the handoff, f116cff5). Critic B read the stamps, Q53-Q55 and
the docs' staleness. One BLOCKER, nine MAJOR. All 23 findings were
ACCEPTED by the kit session, and its disposition column is this
revision's instruction list. **This revision rules nothing.** No
emitted byte moves and nothing is built. R-1's verdicts are unaffected:
all four R-1 cells are DFA-route sites.

### R4.6.0 Each finding, and where it now lives

| id | sev | finding (short) | where it now lives |
|---|---|---|---|
| A1 | BLOCKER | `set-leads`' lead called OPTIONAL everywhere. On the no-DFA route `emit_req_set_rest` leaves the lead's byte out of the set rest, so the lead is part of K65's proof | §14.5 (new "per route" block; "lead excepted" deleted); §14.0 `need` comment; §14.3; §14.10 bit 45; §15.3; §15.5 part 0, `[rev4.6]` note on bit 45, item 6; §19 row 5; §R4.5.1 item 1; §R4.5.5 item 3; §22 R4d; probes `gates_sync.sh`, `tb_r4b.c` (comments only) |
| A2 | MAJOR | `use` cannot be a static `DELEG_SITES` column | §14.0 `use` comment; §14.5 `[rev4.6]` block; §17.6 row reworded; §22 R4c |
| A3 | MAJOR | `REQ_RUN`'s `@idx`, the run-route `REQ_BYTE` and the `[OPT-REQPOS]` note describe the scan form | §14.9 item 1; §19 row 3; §22 R4d; §R4.3.5; Q55 |
| A4 | MAJOR | ~28 mech rows anchored in M1 emitters; `emit_req_handoff` split | §16 item 4 (new); §22 R4c |
| A5 | MAJOR | no site-level `empty` for the composite; a reorder breaks EXCLUDED | §14.3; §14.4 `[rev4.6]` block; §15.4 `empty` row; §15.5 numbering block |
| A6 | MINOR | two part numberings; `ret_pred = 1` wrong without a lead; ASSIGN/ON_MISS rule unstated | §14.0 `ret_pred` comment; §14.2 note; §15.4 `note` row; §15.5 numbering block and item 4 |
| A7 | MINOR | the VM hybrid handoff route is not listed | §15.5 (third listing, witness OWED at R4c); §22 R4c |
| A8 | MINOR | line citations in §14-§16 are pre-handoff | §14 head (note) and every former line citation in §14-§16, now a function name; the 9 → 3 count kept (§16) |
| A9 | MINOR | pair arm's locals and the comment's deny literals incomplete | §15.1 (two `[rev4.6]` notes) |
| A10 | MINOR | `run_prechecks.sh` §5.11 and S460 pin lead-first in pcrec's suite | §15.5 item 7; §22 R4d |
| A11 | NOTE | the comment escaper is stateful | §14.2 sink bullet |
| A12 | NOTE | §15.7 omits PF byte-class | §15.7 (new bullet) |
| B1 | MAJOR | `MEMFN_FORMS` is constant `none` on every default artifact until R4f | §R4.3.5 `[rev4.6]` note; Q55 |
| B2 | MAJOR | nothing tells same-abi artifacts apart by `--memfn=` | §R4.4.1 (new block); §R4.3.5; §22 R4a′ and "Filed"; Q55 |
| B3 | MAJOR | C11's FORMS half vacuous until a SIMD-on form; its sabotage row unreachable | §10.5 `[rev4.6]` note; §17.6; §18.2; §21.2 C11 row; §22 R4d; Q55 |
| B4 | MAJOR | Q53's control list does not match the record's definition | §R4.3.3 (refined form, proposed); §10.5; §17.6 (`memcmp`, `memcpy` rows); §21.2 libc row; Q53 |
| B5 | MAJOR | recording idiom `memcpy` makes the line mislead | §R4.3.3; §22 R4a′; Q53 |
| B6 | MAJOR | Q54's cite (D23) and scope wrong; N7 outside C17's scan; M7 lacks `MF_VOCAB` bump | §R4.3.4 (definition, cite, C17 item 1); §8.5 N7 row; §22 M7; Q54 |
| B7 | MINOR | R4a′ "Trigger: MET" though the libc line waits on Q53 | §22 R4a′ |
| B8 | MINOR | a literal abi number beside "never a literal" | §R4.3.3 "Its event"; §22 R4a′ |
| B9 | MINOR | wait 2's status had two owners | §16 `[rev4.5]` note (points to §R4.5.5 item 1) |
| B10 | MINOR | stale rev lines | `memfn/CLAUDE.md`; `docs/design/memfn/CLAUDE.md`. (`memfn/docs/wake.md` is the kit session's, at its pause) |
| B11 | NOTE | M5′'s offsets show in `<PREFIX>_DFA_PREFILTER_OFFSETS` | §R4.3.5; Q55 |

23 findings, 23 placed. A1-A12: 12 of 12. B1-B11: 11 of 11.

### R4.6.1 What changed in the design

1. **The lead's need is per route (A1, the blocker).** OPTIONAL iff
   `pcrec_artifact_has_dfa_scan`, else REQUIRED. On a no-DFA route the
   lead is the only test of a necessary-set member, because
   `emit_req_set_rest` marks its byte done. Bit 45 removes part 0 on
   DFA-scan routes and moves the byte into part 3 on no-DFA routes. A
   run-first arm that folds the lead must still decide it over the
   whole window before any miss, and never return a hit with a
   REQUIRED lead untested. Verified by this lane at abi 61:
   `(x?)([a-z]+)+Z.user\1` is VM with no prefilter, emits the lead and
   no `rq_set`, and under `-fno-req-set-lead` emits `rq_set[] = { 90 }`.
2. **`use` is per instance (A2).** It comes from `req_use(cx)`, the same
   call that sets `ret_pred`. `DELEG_SITES` holds at most a ceiling,
   and C10 checks per instance.
3. **The composite's `empty` is MISS (A5).** EXCLUDED belongs to a
   predicate in its place after a guard, and the kit re-derives it on
   any reorder.
4. **One numbering (A6).** `preds[]` is dense; `ret_pred` is the
   window's index (0 or 1); `note`/`note_tag` share the index; the
   handoff is ASSIGN iff `ret_pred != 0xFF`.
5. **The VM hybrid handoff route is listed (A7).** Its witness is OWED
   at R4c.
6. **pcrec's form-describing stamps are named for R4d's spec hunk
   (A3), and pcrec's lead-first pins are named for R4d's design (A10).**
7. **The REPLACE commit re-points the mech rows (A4).** S464 goes
   kit-side; S463, S470, S471 and S472 stay pcrec-side.
8. **The stamps (B1-B5, B7, B8, B11).** C11's FORMS half is UNREACHED
   until R4e′. The bench attributes kit state by its recorded build
   recipe, and `<PREFIX>_MEMFN_OPTS` is filed. The libc record's refined
   form (whole artifact, source-level inventory, idiom loads excluded,
   names from the compile) is PROPOSED as Q53's recommendation. R4a′'s
   trigger is MET for the stamp only. No abi literal is written.
   **`[rev4.7]`** Q53 RULED: the refined form is the design of record
   (§R4.3.3).
9. **N7 (B6).** The owner is D58/DD-12. The site definition is "search
   or span-compare". C17's static scope gains `src/enc/` and M7 an
   `MF_VOCAB` bump, should Q54 rule yes. **`[rev4.7]`** Q54 RULED YES
   (§R4.3.4).
10. **Text only (A8, A9, A11, A12, B9, B10).** Function names for line
    numbers, the pair arm's locals and frozen literals, the stateful
    escaper, the byte-class sketch, one owner for the waits' status, and
    current rev lines.

### R4.6.2 Spellings this revision chose

1. The route test is spelled by its function,
   `pcrec_artifact_has_dfa_scan`: "DFA-scan route" when it is true (the
   DFA routes and the VM hybrid), "no-DFA route" when it is false.
2. `ret_pred` and `note(i)`/`note_tag(i)` index the dense `preds[]`.
   The `[K65]` note sits on the first set-rest predicate's index.
3. The bench-attribution line is `<PREFIX>_MEMFN_OPTS`, filed only.
4. The libc control's compile is `-O0 -fno-builtin -c` and `nm -u`, and
   "constant-size idiom load" is a `memcpy` of a constant 1-8 bytes.
5. Citations name the function, or the struct or table for a non-code
   anchor (`struct DfaDir`'s `peek`, `CandScan.run_verified`,
   `runcmp.c`'s header comment).

### R4.6.3 The three standing design questions, for this revision

1. **Measurement regime: NOT RELEVANT.** This revision reads and
   produces no measured number. R-1's numbers stand as §R4.5.4 states
   them. Its cells are DFA-route sites, so A1 does not touch them.
2. **Independent control: RELEVANT.** Three controls change.
   - C10 checks `use` per instance against the emitter's own use of the
     result (`pcrec_emit_req_byte_check`'s return), a structural fact of
     pcrec's text (A2).
   - C11's FORMS half is declared UNREACHED (K35) until a SIMD-on form
     exists, rather than counted as a pass (B3).
   - The libc record's proposed control takes names from the compile's
     symbol table, which shares no source with the kit's list, pcrec's
     list or the shim (B4). Its sabotage rows reach `memcmp` and
     `memcpy` (the second declared UNREACHED if the corpus has no
     non-constant `memcpy`).
   - The VM hybrid route's witness is OWED at R4c ([MECH-REACH]), and
     the mech rows anchored in M1 emitters are re-pointed at REPLACE
     (A4).
3. **What moves when data is regenerated: NOT RELEVANT.** No data file,
   pin or emitted byte moves. The design moves three future readers:
   R4d's spec hunk (A3), R4a′'s spec hunk and inbox note (B2, B5), and
   the REPLACE commit's mech re-pointing (A4). Each is named at its
   step.

---

## R4.5. Revision 4.5: R-1's Linux verdict and D149 folded `[rev4.5]`

(Top-level, like §R4.4. It sits first because it overrides §15.5's
description of the composite site's order and §22's R4b and R4d rows.)

**The inputs.** Request R-2 item 1 (`memfn/docs/requests.md`). Three:
R-1's findings (`docs/dev/lanes/memfnr4b_report.md` §9, the Linux
verdict, and §6, the §15.5 proposal), D149 (`docs/dev/decisions.md`),
and the stale facts rev 4.4 left (the abi number, wait 2's status).
**This revision rules nothing.** Q53-Q55 stay open. Where the report
says "must" or "default" about a kit form, it is the kit's own choice
under D146, recorded here, not a pcrec ruling.

### R4.5.0 Each input, and where it now lives

| input | what it says | where it now lives |
|---|---|---|
| R-1 §9, lead order | The lead order (lead first, or run first) is part of the composite site's form. userpass: run-first `swar` LOSES everywhere (the lead rejects first), lead-first `swlf` is null | §15.5 (new subsection, the closing paragraph rewritten); §R4.5.1 |
| R-1 §9, a future fact | A pcrec "lead can reject" density fact would let the kit choose run-first. Not built | §15.5; §R4.5.1; §22 "Filed, not scheduled" |
| R-1 §9, regime boundary | The portable fused form scans at ~0.18 ns/B and loses where `emit` pays few stops: mod-i gate 1m (+2.41 ns, floor 0.52), cls-n-uc gate 64k/256k | §15.5 (new subsection); §R4.5.1 |
| R-1 §9, R4b | DONE. Main 08caf4a3, merge 348c0a49, Linux `R4B-DONE status=0` | §22 R4b (both blocks), §21.1, §16 |
| R-1 §9, R4d's trigger | MET at SIMD-off on union-select: `swar` beats `emit` past the floor in both regimes, 1.4-2.0x | §22 R4d (both blocks); §R4.5.2 |
| R-1 §9, R4e′ | At AVX2, `ffl` loses to `swar` by +0.36/+0.64 ns at 16 B (userpass pc16, cls-n-uc pc16). Short spans belong to the scalar form inside the SIMD-on cascade or short path | §22 R4e′; §8.6 K-6 |
| R-1 §9, K85 | The fused forms remove the find-all dense-text loss and beat the `-fno-req-set-lead` floor (1m: `swlf` -160,932 ns, `ffl` AVX2 -306,068 ns, against nosl). Single gate calls on dense text still lose at SIMD-off | §15.5; §16 item 2; §19 row 5; §21.1; §22 R4d; §R4.5.1 |
| D149 | Every unroll width, block size, cut-over and threshold in a kit form is MEASURED, DERIVED or LEFT TO THE COMPILER, or labelled in place as an unmeasured default | §8.6 (K-7); §22 R4d; `memfn/CLAUDE.md` "The layers"; §R4.5.3 |
| stale abi | "the next number at landing (61 at main 7f94b0cd)" | §R4.3.3 and §22 R4a′ (annotated); §R4.5.2 |

### R4.5.1 What changed in the design

**1. The lead order is part of the composite site's form (§15.5).**
- The order was a hint pcrec's baseline honours and a non-baseline arm
  "may revise (lead and window fused into one pass)". That sentence
  made fusing the lead into the run pass sound like K85's general
  answer. R-1 measured otherwise.
- Where the lead rejects first (userpass: `=` is absent from the
  capability text), the run-first fused form loses at every length.
  Lead-first is null there.
- Where the lead never rejects (cls-n-uc on dense text), the cure for
  K85 comes from the fused RUN filter, not from fusing the lead.
- So the kit's per-site choice has two parts: the form of the run pass,
  and the lead order. The default is lead first when a lead is present.
  Run-first is chosen only on evidence the site carries.
- The evidence would be a pcrec "lead can reject" density fact (K85's
  suspected cause, `memfnr4b_report.md` §6 item 2). It is a possible
  future fact. It is NOT built (D77). Its trigger is a measured cell
  where run-first wins and lead-first does not.
- Bit 45 still removes part 0, so a site with no lead has no order.
- **`[rev4.6]`** (r5 A1) The last bullet holds on DFA-scan routes. On a
  no-DFA route the lead is REQUIRED (K65) and bit 45 moves its byte
  into the set rest. A run-first form ("the lead folded into the run's
  pass") is sound only if the folded pass still proves the lead absent
  before it returns a miss for it, and never returns a hit with a
  REQUIRED lead untested (§15.5 item 6). All four R-1 cells are
  DFA-route sites, so the measurements above stand.

**2. The portable fused form has a regime boundary (§15.5).**
- Its raw scan rate is ~0.18 ns/B (union-select 1m, no stops).
  `ffl`'s is ~0.04. glibc AVX2 `memchr` scans faster than `swar`.
- It wins where the emitted gate pays per-stop costs: union-select's
  1,431 `c` stops per 64 KiB, and the find-all sweeps of mod-i and K85.
- It loses where a short distance to the first hit gives `emit` few
  stops: mod-i gate 1m (+2.41 ns against a 0.52 floor, first hit at
  404) and cls-n-uc gate 64k/256k (`swar` 147 ns vs 76.5 at 256k;
  `swlf` 108).
- That is the portable form's regime boundary, not a defect. The SIMD-off
  form must not be selected for early-hit single gate calls on dense
  text without the future fact above. R4d's design carries the boundary.

**3. K85 (R-1 §9).** Both fused forms remove the find-all dense-text
loss and beat the no-gate floor. The single-call gate on dense text
still loses at SIMD-off. The general answer is the fused RUN filter with
the lead tested first.

**4. R4b is measured; R4d's trigger is MET at SIMD-off (§22).** One
cell meets it: union-select wins every row in both regimes (gate 1m
364,078 -> 187,022 ns; sweep 64k 16,580 -> 11,422; short 11.50 -> 5.83;
pc1024 272 -> 195). mod-i misses it by one throughput row (gate 1m).
R4d's form carries the lead order (item 1) and starts from the plain
loop (item 5).

**5. D149 binds every kit form (§8.6 K-7).** Every unroll width, block
size, short-span cut-over and density or size threshold in a kit form
is measured (its regime named), derived (from a stated quantity), or
left to the compiler. Otherwise it is labelled in place as an
unmeasured default: a comment where it lives, plus a line in the
design note. The first label is R-1's `swar` 2x (16-byte) unroll
(`docs/design/memfn/probes/twins/tb_r4b.c`, inherited from `ffl`'s 2xVW
shape and not measured against 1x or 4x). R4d's form therefore starts
from the plain loop, and its unroll is measured or compiler-chosen. No
retroactive sweep: a label is a measurement's trigger, not a build
order (D77).

**6. The 16 B note for R4e′ (§22).** At AVX2, `ffl` loses to `swar`
at 16 B by +0.64 ns (userpass pc16) and +0.36 ns (cls-n-uc pc16). Short
spans belong to the scalar form, inside the SIMD-on cascade or short
path (K-6). It is a form detail, not a verdict against the SIMD layer.
At every other cell, at SSE2 and AVX2, `ffl` wins.

### R4.5.2 Every passage this revision changed

| section | revision 4.4 said | revision 4.5 |
|---|---|---|
| title block | rev 4.4 current; open Q53-Q55 | rev 4.5 current; Q53-Q55 still open; rules nothing |
| §8.6 | K-1..K-6 | K-7 added: D149 |
| §15.5, "Why ONE site" | the order is a hint a non-baseline arm may revise; fusing lead and window is K85's general answer | annotated; replaced by "The lead order and the regime boundary" subsection |
| §16 item 2 and the `[rev4.3]` status | K85's re-measure OWED | annotated: measured, `k82halpha_report.md` §3 (K85 persists at +0.023..+0.036 ns/B); R-1 measured the fused forms. Wait 2 is MET (§R4.5.5 item 1) |
| §19 row 5 | the composite site's order | annotated: lead order is the kit's per-site choice |
| §21.1 R4b bullet | R4b measured on the post-handoff build, as a plan | marked measured, with the report pointer and the regime verdicts |
| §R4.3.3 "Its event" | abi "the next number at landing (61 at main 7f94b0cd)" | annotated: main is at abi 61 (the handoff, f116cff5), so 62 if nothing lands first; never a literal |
| §22 (rev 4.3 block) R4a′ | "62 if nothing lands first" | marked `[rev4.5]`: current as of main 08caf4a3; never a literal |
| §22 R4b | probe only, trigger MET, Linux alpha OWED | DONE (R-1) |
| §22 R4d | trigger: R4b's cell | trigger MET at SIMD-off on union-select; form carries the lead order; D149 |
| §22 R4e′ | the kit's SIMD forms, any cascade | plus the 16 B short-path note |
| §R4.4.0 Q48 row | the trigger is a K85-shaped cell the fused arm does not cure | annotated: R-1 found the single early-hit gate call on dense text still loses |
| §22 "Filed, not scheduled" | (no entry) | the pcrec "lead can reject" density fact, filed |
| §22 older blocks (rev 3, rev 4 lists, rev 4.2 block), §23 | R4b pending | history, annotated once at §22's head; not rewritten |
| `memfn/CLAUDE.md` | no D149 line | "kit forms obey D149" under "The layers" |
| `docs/design/memfn/CLAUDE.md` | integration.md at rev 4.4 | rev 4.5, one line |
| `docs/dev/lanes/CLAUDE.md` | no `memfnr45_report.md` | entry added |

Passages with a `[rev4.5]` mark are changed in place. Earlier text that
says R4b is owed, R4d's trigger is unmet, or K85 is open is history,
annotated and not rewritten.

### R4.5.3 Spellings this revision chose

1. The D149 rule is **K-7** in §8.6, after K-6. It is the kit's rule
   and applies to pcrec's emitters through D149 itself.
2. The unmeasured-default label is the text `UNMEASURED DEFAULT:` at the
   constant, as in `tb_r4b.c`. Panels grep for it.
3. The lead order is spelled "lead first" / "run first". It has no
   option name of its own: it is part of R4d's one form and rides R4d's
   one registry row (§R4.5.5 item 3). Run-first, when its fact exists,
   gets its own row.
4. The future density fact is spelled "lead can reject". It carries no
   `MF_P_*` name and no shape. It is filed, not designed.

### R4.5.4 The three standing design questions, for this revision

1. **Measurement regime: RELEVANT.** Every number above is R-1's: Linux
   (ubuntubudu, gcc 15.2, AMD Ryzen 5 1600, `taskset -c 2`), 3
   launches, floor = max |emit - emit2|, throughput and per-call
   regimes, SIMD-off and SIMD-on both reported. clang and the Mac form
   no verdict. The lead-order result holds in the capability-text and
   dense-text regimes R-1 measured and no other.
2. **Independent control: RELEVANT.** The verdict's control is R-1's
   correctness run (0 wrong, 10 of 10 planted caught, five builds) and
   its emit-vs-emit floor. R4d's G1 stays pcrec's timing against the
   kit's own deny, population from a pcrec-side artifact diff (§17.2).
3. **What moves when data is regenerated: NOT RELEVANT.** This revision
   adds no data file and moves no emitted byte.

### R4.5.5 The kit session's answers to the fold's open points

The fold (lane memfnr45) left four points open. They are the kit
session's to settle (D146: the form is the kit's; the status of pcrec's
waits is a fact, read from merged reports). None is a pcrec ruling.

1. **Wait 2 and the handoff's Linux alpha are MET.** The pcrec manager
   accepted the handoff's alpha (`requests.md` R-1, "Confirmed
   2026-10-05": cause (B) cured, DENY==BASE on every cell), and K85 was
   re-measured on the post-handoff build (`k82halpha_report.md` §3,
   `docs/dev/optloop/s4/k85alpha_lx.txt`, merged ad16111b). R4c's
   prerequisite "K85 re-measured (OWED)" is therefore MET. R4c's
   remaining prerequisite is R4a′.
2. **The early-hit single gate call is a CANDIDATE for Q48's cell, not
   yet its trigger.** Q48's trigger is "a K85-shaped cell that the R4d
   fused arm does not already cure". The R4d arm does not exist yet.
   R-1's `swar`/`swlf` are probes of it. The cell (cls-n-uc gate at
   64k/256k; mod-i gate at 1m) is judged at R4d's G1 alpha, against
   R4d's own deny row, at both layers. If it still loses past the floor
   there, Q48's trigger is met and the optional site is filed as a
   request.
3. **The lead order is part of R4d's ONE form**, not a separate kit
   form. R4d ships lead-first wherever a lead is present (the only
   order R-1 supports without a density fact), under R4d's single
   `--memfn=no-NAME` row. Run-first enters only with the "lead can
   reject" fact, as its own change, with its own trigger and its own
   registry row (D144 item 4). §R4.5.3 item 3 reads accordingly.
   **`[rev4.6]`** (r5 A1) The lead's NEED is per route, apart from its
   order: OPTIONAL on DFA-scan routes, REQUIRED on no-DFA routes (§14.5).
   R4d's design states both, and the run-first obligation (§15.5 item
   6).
4. **The older §22/§23 blocks stay as history** under §22's head note.
   They are not rewritten (the R4.4/R4.3 convention).

---

## R4.4. Revision 4.4: D147 addenda 8-9 folded `[rev4.4]`

(Top-level, like §R4.3. It sits first because it overrides §R4.3 in one
place: the kit's per-form switches.)

**The rulings.** D147 addendum 8 rules Q43. Addendum 9 rules Q44, Q45,
Q46, Q48 and Q49 as recommended and REFINES Q47. Revision 4.4 adds
nothing the rulings do not require. The few spellings the rulings left
open are listed in §R4.4.3. After this revision the open questions are
Q53-Q55 only.

### R4.4.0 Each ruling, and where it now lives

| Q | ruling | where it now lives |
|---|---|---|
| Q43 | RULED YES (addendum 8). SIMD-on forms tuned for aarch64 are not ACCEPTED until Frank admits Mac measurements as verdict-grade for those cells, or an aarch64 Linux box exists. x86 Linux gives the verdicts. The SIMD-off (portable) layer is unaffected | §17.2 and §10.1 annotated; §23 |
| Q44 | RULED YES (addendum 9). The dial interaction is ruled at R4d as a D103 diff: `--tune` -2/-1 send `MF_P_SIZE_LEANING`, with the movers census at those positions | §22 R4d; §23 |
| Q45 | RULED YES. The spec states whose libc was measured (glibc and libSystem; musl inherits), as §10.6's second limit, at R4d | §10.6; §22 R4d; §23 |
| Q46 | RULED YES. Two single-writer files. As built: `memfn/docs/requests.md` (manager only) and `memfn/docs/responses.md` (kit only) | §20.1; `memfn/CLAUDE.md`; §23 |
| Q47 | REFINED (addendum 9): the kit's OWN option namespace, `--memfn=`, from a kit-owned registry, listed by `--list-axes` as a `memfn` section | §R4.4.1; §14.10, §17.1 rewritten |
| Q48 | RULED YES. Optional sites: file, don't build. The D77 trigger is a K85-shaped cell that the R4d fused arm does not already cure (`[rev4.5]`: R-1 found one class, the single early-hit gate call on dense text at SIMD-off, which the fused form still loses; whether that is the Q48 cell is the kit session's call) | §19 row 11; §22 "Filed, not scheduled"; §23 |
| Q49 | RULED YES. An opt-in-only kit arm (R4e′, `-fmemfn-simd`) needs no abi bump at landing. Its pins, its `test-axes` arm and C9's floor are born in that commit, and its spec hunk lands there. The R4f flip is the abi event (`[D155]` except R4e′.0b, §R4.9.2.6) | §22 R4e′; §23 |
| D144 item 4 | met inside the kit's namespace: each kit change's own deny is a registry row | §R4.4.1; §L.3 |

### R4.4.1 The kit's own option space (Q47 refined)

**What pcrec keeps.** Exactly ONE axis for this: the layer switch
`-fno-memfn-simd` / `-fmemfn-simd` (§R4.3.1). `axes.def` gets no row for
a kit form, `flags` gets no bit for one, and `strategy_denials` has no
entry for one. A kit option is not a flag bit, so it cannot move
`rx_info.flags` (reqpos's 5-byte finding does not arise), and it spends
none of the 64 bits (Q15's budget).

**What the kit owns.** `--memfn=<opt>[,<opt>…]`:
- pcrec carries the value as ONE opaque string (CLI, config, library
  field) and hands it to the kit in `mf_site.opts` (the field §8.2 called
  `deny`). It never splits, sorts or looks up an option.
- Validation is the kit's. pcrec calls `mf_opts_check(str, err, n)` once
  per compile and shows the kit's refusal text unchanged (D26: the
  wording is the kit's).
- Spelling: `no-NAME` denies row NAME; a bare `NAME` forces it, accepted
  only for a row declared `MF_OPT_PAIR`.

**The registry: `memfn/src/options.def`.** An X-macro in `axes.def`'s and
`limits.def`'s idiom (D111), but the file is the kit's. pcrec's build
never reads it, and pcrec's sources never include it.

```
/* MF_OPT(name, kind, budget, layer, doc)
 *   name    kit-owned id, [a-z0-9-], arch-blind (C4)
 *   kind    MF_OPT_DENY | MF_OPT_PAIR    which --memfn= spellings it takes
 *   budget  MF_B_SCAN | MF_B_LOOP | MF_B_ANY       D91, as §8.5's INLOOP
 *   layer   MF_L_SCALAR | MF_L_SIMD      which acceptance reading owns it
 *           (§L.4); an MF_L_SIMD row is inert at -fno-memfn-simd
 *   doc     one line                                                      */
MF_OPT("cube",     MF_OPT_DENY, MF_B_SCAN, MF_L_SCALAR, "the cube set classifier (C1)")
MF_OPT("unrolled", MF_OPT_DENY, MF_B_LOOP, MF_L_SCALAR, "the unrolled scan loop (C2)")
```

- The kit includes it three times: the table, the accessor
  `mf_options(size_t *n)` (which replaces `mf_switches()`), and the
  parser behind `mf_opts_check`. What is printed and what is parsed are
  one table.
- A kit change that moves a byte adds its row in the same commit
  (D144 item 4). The row IS the change's OFF arm (§L.3), reached as
  `--memfn=no-NAME`.

**One enumeration point.** `--list-axes` prints pcrec's axis table and
then a `memfn` section (`#section memfn`, `table_contract.md`
§Sections), one row per `mf_options()` entry: `name`, `kind`, `budget`,
`layer`, the accepted spelling(s) and `doc`. pcrec's dump code prints
what the accessor returns and names no row. `test-axes`, the identity
gates (I2, G1's movers) and the registry check each read THIS section
and keep no name list of their own. `test-axes` sweeps each row's
spelling for answer identity, and I2 sweeps it for byte identity against
its pin once it has movers.

**The independent control: a spec-pinned floor.** The `memfn` section's
member count has a floor, a hand-written literal in `docs/spec/`
(`registry.md`, beside §6's axes pin). The registry check compares the
section's row count to it. The floor shares no source with
`options.def`, `mf_options()` or the section, so a stale or truncated
kit registry cannot also lower its own bar. It is raised only in the
change that adds a row. It is BORN at the first landing that adds a row
(R4d, the first mover, with its own deny). Before that the section is
empty, and the check is declared UNREACHED (K35), not set to 0.

**Consequences, each a reader to find BY GREP at the landing** (D76/D94
shape):
- `--list-axes` gains a section, so by `table_contract.md` rule 4 every
  consumer of the stream must select its section: `tests/axes/`,
  `tests/registry/`, anything that parses `--list-axes`. If rule 2 does
  not already say how a consumer selects the leading anonymous table,
  the landing carries that hunk to `table_contract.md`.
- `registry.md` §6's "N rows / M axes" pin counts the main table only
  (above the section line). The kit section has its own count and
  floor.
- `--memfn-deny=`, `mf_switches()` and "pcrec generates axis rows from
  the kit's table at build time" (§14.10) are withdrawn. C4's class 7
  (pcrec never spells a kit row name in `src/`) holds structurally,
  because pcrec holds a string.
- option_sets.md treats `--memfn=` as one opaque value (D93 precedence as
  for any value option). It does not decompose into per-element axes,
  and no set carries a kit option. If a set ever needs one, that is a
  new ruling (D77).

**`[rev4.6]` How the bench tells kit states apart (r5 B2).** Two
same-abi artifacts that differ only by `--memfn=` carry nothing in the
artifact that says which kit state ran: `MEMFN_FORMS` reads `none` at
SIMD-off (§R4.3.5), and D81 forbids a stamp that appears only when an
option is given. The rule: **the bench attributes kit state by the
build recipe it records** (abi, pcrec commit, argv). R4a′'s spec hunk
and its bench inbox note state this. An always-present
`<PREFIX>_MEMFN_OPTS` line (`none`, or the `--memfn=` string) is FILED,
trigger "a bench consumer asks" (D77). It is offered to Frank in Q55;
if he wants attribution in the artifact now, it rides R4a′ for free.

**The three standing questions** (`docs/design/CLAUDE.md`):
1. Measurement regime: not relevant. The registry changes no emitted
   byte by itself. The regime of a row's own effect is its change's G1
   (§17.2).
2. Independent control: relevant. The spec-pinned floor, above.
3. What moves when data is regenerated: relevant. A row added or
   removed moves the `--list-axes` section, the floor and the arm counts
   (§21.3's last row).

### R4.4.2 Every other place the rulings touch

| section | revision 4.3 said | revision 4.4 |
|---|---|---|
| §8.2 `mf_site.deny` | `--memfn-deny=`, passed through unparsed | `opts`, the `--memfn=` string, passed through unparsed |
| §8.6, §9.5, §10.1, §10.5, §L.3, §L.5, §L.6 | a kit change's OFF arm is `--memfn-deny=NAME` | `--memfn=no-NAME`, a registry row |
| §10.6 | the `-fno-memfn-*` bits and `--memfn-deny=` | `-fno-memfn-simd`/`-fmemfn-simd` and `--memfn=` |
| §11.4, §12.1 | option family `memfn`: three bits and `--memfn-deny=` | one axis, plus `--memfn=` |
| §14.10 | generated axis rows from `mf_switches()` | the kit's registry and `--list-axes`' `memfn` section (§R4.4.1) |
| §17.1 | arms over `axes.def` rows, the kit's published switches "once they have movers" | plus one arm per `memfn` section row; the arm-count floor adds the section's floor |
| §17.2, §10.1 | no verdict-grade armv8 guard, K-4 | plus Q43's acceptance rule |
| §17.6 | row: a change's `--memfn-deny=NAME` no longer reproduces its parent | `--memfn=no-NAME` |
| §20.2 | the kit's generated `--memfn-deny=NAME` rows | the kit's `--memfn=` registry |
| §21.3 | the kit's switch table (`mf_switches()`) | the kit's registry (`options.def`) and the spec floor |
| §22 R4d | its own `--memfn-deny=NAME` | its own `--memfn=no-NAME` row; Q44 and Q45 ruled here |
| §23 | Q43-Q49 open | Q43-Q49 RULED; Q47 REFINED; Q53-Q55 are the only open questions |
| `option_sets.md` | `--memfn-deny=` a list option decomposing into axes | cross-note added: one opaque value (§R4.4.1) |
| `memfn/CLAUDE.md`, `memfn/include/`, `memfn/src/` | `mf_switches()`, `--memfn-deny=NAME` | `mf_options()`, `--memfn=`, `src/options.def` |

Passages that carry a `[rev4.4]` mark are changed in place. Revisions 1-3
passages that still say `--memfn-deny=`, `--kit-deny=` or `mf_switches()`
(Q15, §R2's table, §12.1's rev 3 table, R4.1's G-F2 row) are history,
annotated and not rewritten.

### R4.4.3 Spellings this revision chose (the rulings left them open)

1. `--memfn=` tokens are `no-NAME` / `NAME`, and rows carry a `kind`.
2. The registry file is `memfn/src/options.def`, with the five columns
   above.
3. The accessor is `mf_options()` and the check is `mf_opts_check()`.
4. The `--list-axes` section's columns, and the main-table-only pin in
   `registry.md`.
5. The floor is born at the first row (R4d); UNREACHED before.
6. `--memfn=` is one opaque value in option_sets.md.
7. Q43 is stated as ruled (an acceptance rule). §17.2's "the kit does
   not select a SIMD-on form on aarch64" is kept as its consequence, not
   as the ruling.

---

## R4.3. Revision 4.3: Frank's 2026-10-05 rulings folded `[rev4.3]`

(This is a top-level section, not a fourth subsection of §R4. §R4's
subsections end at R4.2.)

**The rulings.** D146 (delegation) and D147 (layers) stand as §R3 and
§L apply them. Frank ruled every remaining revision-4 question the same
day, in D147's seven addenda (`docs/dev/decisions.md`). Two of those
addenda REPLACE earlier rulings: addendum 6 replaces addendum 2's three
profiles with one switch, and addendum 5 reverses Q42. Addendum 7 makes
the switch OFF by default and rejects Q51 and Q52. Revision 4.3 adds
no mechanism the rulings do not require. Where a ruling left a spelling
or a seam open, this section picks one and says so, and the three
genuinely new choices go to Frank as Q53-Q55 (§23).

### R4.3.0 Each ruling, and where it now lives

| ruling | source | what it rules | where it lives now |
|---|---|---|---|
| D146 | decisions.md | the kit is a DELEGATE: pcrec describes a site, the kit returns its code; no price crosses | §R3, §8, §14 (unchanged) |
| D147 | decisions.md | the scalar algorithm stays live forever; SIMD is a layer that must beat the CURRENT scalar; every reading reports both layers | §L (spelling updated by §R4.3.1) |
| Q35 contract YES | D147 | §8 as extended by §14 is the design of record, revised by panels as migration finds gaps | §8, §14; §23 Q35 RULED |
| Q36 in-tree YES | D147 | the kit is `memfn/`, `pcrec_mf_*`, two-file ledger; extraction waits for a stable API across several steps AND a real second consumer | `memfn/`, `memfn/CLAUDE.md`; §20; §23 Q36 RULED |
| Q37 0BSD YES | addendum 1 | the kit's own text is 0BSD; translated Rust `memchr` files carry per-file Unlicense provenance | §20.3; `memfn/LICENSE`; §23 Q37 RULED |
| Q38 | addendum 2, REPLACED by addendum 6 | addendum 2's off / portable / native profiles are replaced by ONE switch with a meaning | §R4.3.1; §8.5, §14.10, §20.2 annotated; §23 Q38 RULED |
| the switch's meaning | addendum 6 | OFF = portable C (plain C, SWAR, libc; runs anywhere). ON = hardware-optimized for a specific CPU, may or may not execute elsewhere. What sits inside ON is the kit's per-site choice | §R4.3.1; §8.5; §10.6 |
| default OFF | addendum 7 | SIMD is off by default until the SIMD hold (D91/D119) lifts (`[r9b]` `[rev4.9]` the hold is superseded by D147 add. 11; the flip is R4f); turning it on is its own ruled event (D112 shape) | §R4.3.1; §22 R4f |
| Q39 stamp YES | addendum 3 (+ addendum 6) | `<PREFIX>_MEMFN_FORMS` on every artifact; `none` iff identical to the SIMD-off compile; carried levels if a site cascades; no kit version; its own abi event R4a′; libc-call use recorded | §R4.3.3; §18 annotated; §22 R4a′; §23 Q39 RULED |
| Q40 YES | addendum 4 | at M5 the planner moves LIVE into the kit; pcrec keeps one semantic row; the reseed becomes unconditional; an abi event | §R4.3.5; §14.9, §19 annotated; §22 R4j/M5′; §23 Q40 RULED |
| Q41 YES | addendum 5 | M1 = the composite PRE site + the offset-skip trio; runcmp is M1b; M1 after the handoff merge and K85's re-measure; afterwards the migrated emitters are kit work | §16 (unchanged); §22 R4c; §23 Q41 RULED |
| Q42 REVERSED | addendum 5 | migrate EVERY search site, M4 included, with no performance customer (a ruled exception to D77: the trigger is completeness); a CHECKED SITE MANIFEST; the `memchr` ratchet ends at 0 outside the kit | §R4.3.4; §9.4, §9.5, §15.7 annotated; §22; §23 Q42 RULED |
| cascading capabilities | addendum 2 | one artifact MAY carry several ISA levels with a run-time pick, case by case, decided and measured by the kit; the cascade must beat the single-level form | §R4.3.2; §8.6 K-6; §R4.3.3's grammar |
| Q50 YES | addendum 6 | SWAR and libc calls are in the scalar layer | §R4.3.1; §L.1 annotated; §23 Q50 RULED |
| Q51 REJECTED | addendum 7 | the SIMD-off arm is not withdrawn; D147's both-layers reading stands | §R4.3.6; §23 Q51 |
| Q52 REJECTED | addendum 7 | the stamp is not re-keyed; Q39 as ruled stands | §R4.3.3, §R4.3.6; §23 Q52 |

### R4.3.1 The one SIMD switch (addenda 6 and 7; Q38, Q50)

**What it means.**

- **SIMD OFF.** The artifact is PORTABLE C. Its search code is the
  scalar layer: plain C, SWAR on ordinary integers, libc calls (libc does
  its own dispatch), and loop-free short-span forms. It compiles and runs
  on any target. Q50 is ruled: SWAR and libc are scalar layer.
- **SIMD ON.** The artifact, as compiled, is optimized through hardware
  for a specific CPU architecture. It MAY OR MAY NOT EXECUTE ELSEWHERE.
  pcrec makes no portability promise for it, and the spec says so (§10.6).
- **What sits inside ON is the kit's choice, per site:** which forms,
  which ISA levels, any cascade (§R4.3.2), and any fallback arm.
  Whether a narrower "baseline-ISA" SIMD-on form exists (for example,
  SSE2-only on x86-64) is a kit FORM question, not a pcrec profile.
  pcrec has exactly one bit of SIMD policy: the switch.
- **Default OFF** until the SIMD hold (D91, D119) lifts (`[r9b]` `[rev4.9]` superseded by D147 add. 11; the flip is R4f). Callers opt in
  with the switch. Turning it on by default is its own ruled abi event
  (R4f, D112 shape). After the flip, the DEFAULT artifact no longer
  promises portability, which is why the flip is Frank's ruling rather
  than a measurement's side effect.

**The spelling.** House convention for a capability that ships OFF is
a deny/force PAIR, OFF by default, enabled by its `-fX` spelling.
`-fcomments` (D112, `axes.def:219-220` at main 7f94b0cd) and `-futf-check` (`:183`) are
the precedents, and r3 G-F12 already applied that rule to this axis.
The axis is named for what addendum 6 rules (THE SIMD switch).
Addendum 2 had already spelled its off side `-fno-memfn-simd`, while
"native" named a profile that addendum 6 dissolves. So:

```
PCREC_AXIS(PCREC_NO_MEMFN_SIMD, "-fno-memfn-simd",
           PCREC_FORCE_MEMFN_SIMD, "-fmemfn-simd", PCREC_AXIS_DEFAULT_OFF)
```

- Both spellings exist from birth (R4c). R4f changes ONLY
  `default_state`.
- Both bits join `strategy_denials` (§14.10), so the switch never moves
  `rx_info.flags` on an artifact it cannot act on.
- **The policy bit the kit receives** is the existing
  `MF_P_PORTABLE_ONLY`, set when the switch is not forced. Its name
  already states addendum 6's meaning, so it is kept.

| earlier spelling | read as (rev 4.3) |
|---|---|
| axis `memfn-native` | axis `memfn-simd` |
| `-fmemfn-native`; profile `native`; "native arm(s)" | `-fmemfn-simd`; SIMD ON; "SIMD form(s)" (the kit's forms rendered only when the switch is on) |
| `-fno-memfn-native`; profile `portable`; "portable arm" | `-fno-memfn-simd` (or the switch not forced); SIMD OFF; "the scalar layer's form" |
| `PCREC_NO_MEMFN_NATIVE` / `PCREC_FORCE_MEMFN_NATIVE` | `PCREC_NO_MEMFN_SIMD` / `PCREC_FORCE_MEMFN_SIMD` |
| profile `baseline`; `-fno-memfn-scan`; `-fno-memfn-loop`; set `memfn-off` | withdrawn (§L.2-§L.3; D147 consequence 1); see §R4.3.6 |
| "the native default flip" (R4f) | "the SIMD default flip" (R4f) |
| option_sets.md family `memfn` | `auto` (∅), `simd` (`memfn-simd := force`), `no-simd` (`memfn-simd := deny`). Until R4f, `auto` and `no-simd` render the same text |
| R4i, declared tokens (`--isa=`) | NOT a pcrec axis. A target level is a kit form question (addendum 6). Re-opened only by a ruling |

**The layers over this switch (D147).** The scalar layer is everything
rendered with the switch off. The SIMD layer is whatever the kit adds
when it is on. G1's two readings are `-fno-memfn-simd` and
`-fmemfn-simd` on both arms (§L.4). The bench testee is `pcrec[simd]`
beside the default from R4e′. After R4f it becomes `pcrec[no-simd]`.

### R4.3.2 Cascading capabilities (addendum 2)

One artifact MAY carry several ISA levels, with a run-time pick between
them. This is decided CASE BY CASE, where the dispatch is cheap enough
for the site.

- **SIMD ON only.** A run-time pick among ISA levels is ISA text, and
  the SIMD-off artifact is portable C with none. libc's own internal
  dispatch is libc's, not the artifact's.
- **The facts on file.**
  - Linux x86: `__builtin_cpu_supports` costs 0.4-0.6 ns per call
    (`linux_results.md`). A cached word is free, but it is illegal as an
    artifact static (`match_api.md` §5.3; `isa_selection.md` §2).
  - Darwin: `__builtin_cpu_supports` answers 0 for every feature, so a
    cascade keyed on it silently runs its lowest level there.
  - aarch64: NEON is always present. SVE needs `getauxval`.
- **Likely first home:** D91 budget-1 sites (prefilters), where the
  dispatch is noise beside the scan. x86 first.
- **The kit decides and measures it as one of its own forms** (K-6,
  §8.6), under the layer rule:
  - the cascade must beat the single-level form at that site;
  - as a SIMD-layer form, it must also beat the CURRENT scalar layer
    (§L.4).
- pcrec stays arch-blind. No level name reaches `src/` (C4), and the
  only place a level is visible is the stamp's carried levels (§R4.3.3).

**`[rev4.9]`** §R4.9.3 extends this section. A cascade is a SEPARATE
row of the kit's form table, placed above the compile-time ladder's rows
and guarded to x86-64 Linux/ELF with GNU C, where the compile-time top
level is absent. `[r9 C-4]` Its guard also requires `__SSE2__` (so
`-mgeneral-regs-only`/`-mno-sse` builds get the floor), and it names the
FULL compile-time ladder as its rungs (cascade, w32, w16, floor). It must
beat the single-level row it displaces at the same `-march`, in both
regimes, on the official boxes. Its libgcc `__cpu_model` link dependency
is Q-R9-8. The compile-time LADDER (levels picked by predefined macros, no
run-time test, no state) is the default way a SIMD row carries several
levels. The first cascade is FILED with a probe as its trigger.

### R4.3.3 The stamp: Q39 as ruled, plus the libc record (addenda 3 and 6)

**`<PREFIX>_MEMFN_FORMS`, on every artifact of both engines.**

- Its value is `"none"` iff the artifact is byte-identical, with the
  stamp lines normalised out, to its own SIMD-off compile
  (`-fno-memfn-simd`) of the same build.
- Otherwise the value is the forms the artifact uses (addendum 3's
  words): every delegated site's form id, comma-joined, in site order.
  A cascading site's entry carries its levels in pick order, as
  `ID@LEVEL+LEVEL`.
- Form ids and level names are opaque. Consumers bucket on
  `none`/not-`none` and never parse an id. The spec says so.
- No kit version and no `MF_VOCAB` (§18.1, unchanged).
- Because SIMD is off by default, every DEFAULT artifact reads `none`
  until R4f. Only `-fmemfn-simd` artifacts carry ids. M1 and every
  migration step remain zero stamp movers, as §18.3 intended.
- **`[rev4.9]`** A compile-time ladder carries levels too, written the
  same way and top-down (`vrun@w32+w16`, §R4.9.2). A ladder and a
  cascade differ by form id (`vrun` vs `vrun-rt`), never by grammar.
  Level tokens are the kit's `levels.def` stamp column: `w16`, `w32`,
  widths rather than ISA names. `[r9 C-9, F-15]` The levels are the
  RENDERED ones, never the live one: the consumer's `-march` picks the live
  rung, and on a target with no level the value is non-`none` while
  nothing vector runs. No level guard appears in the `.h`.

**`<PREFIX>_MEMFN_LIBC`, the libc record (addendum 6), on every
artifact.**

- Its value is `"none"`, or the sorted, comma-joined names of the libc
  functions the artifact's search code calls (`memchr`, `memcmp`,
  `memmem`, …). The names are recorded as written in the text, whether
  or not gcc later inlines a constant-length call. The spec says so.
- It is what tells a reader that a SIMD-off artifact delegates to
  libc's own dispatch.
- **Why a second line rather than a field in `MEMFN_FORMS`:** a SIMD-off
  artifact that calls `memchr` must still read `MEMFN_FORMS "none"`.
  Folding the libc record into that value would break the ruled
  `none`-iff-identical rule. It would also make one check (C11)
  compare one value against two different references. **Q53** asks
  Frank to confirm this spelling.
- **Coverage.** The record covers ALL search code, so it is true from
  its birth. A delegated site's libc use is recorded by the kit through
  `mf_art`. A site the manifest still lists as PENDING (§R4.3.4)
  records its libc names into the same `mf_art` through one pcrec-side
  call, `mf_art_note_libc`. That call is deleted when the manifest's
  pending count reaches 0.
- **C11 gains a second assertion.** The value equals a pcrec-side scan
  of the artifact's text for calls to the functions the C9 header shim
  declares (§17.3). That list shares no source with the kit.

**`[rev4.6]` The libc record's refined form (r5 B4, B5; Q53, still
OPEN).** The record above has two defects. This is the form proposed to
Frank as Q53's recommendation (§23). It is not ruled.

> **`[rev4.7]` RULED (D147 addendum 10, Q53 YES).** The refined form
> below is the DESIGN OF RECORD, no longer a proposal. Where the rev 4.3
> bullets above it conflict ("search code" scope, a text scan for the
> C9 shim's names as the control, idiom `memcpy` recorded), this form
> wins:
> - a separate `<PREFIX>_MEMFN_LIBC` line;
> - a source-level inventory of the WHOLE artifact's libc calls,
>   excluding constant-size idiom `memcpy` loads;
> - its control: names from the compile (`nm -u` of an
>   `-O0 -fno-builtin` object), sharing no source with the line;
> - born in R4a′.
- **Its scope does not match its control (B4).** The record says
  "search code", but no pcrec-side check can delimit search code. The
  control scans for the shim's three names, yet `memcpy` appears
  outside search code (capture copies, the API) and as the SWAR load
  idiom inside it, `memmem`/`memrchr` are not in the shim, and comments
  contain `memchr(` text. Refined: the record lists the libc functions
  the WHOLE artifact's code calls, comments and strings excluded.
- **Its control derives names from the compile.** `nm -u` of a
  `-O0 -fno-builtin -c` object of the artifact gives the undefined
  libc names, minus the same constant-size rule below. It shares no
  source with the kit's list, pcrec's list or the shim. Sabotage rows
  cover `memcmp` and `memcpy`, not only `memchr` (§17.6).
- **It is a SOURCE-LEVEL INVENTORY, not a promise of a dispatched call
  (B5).** gcc lowers a fixed-size `memcpy` to a register load, and a
  constant small `memcmp`/`memchr` may be folded. The spec says so.
- **Constant-size idiom loads are EXCLUDED** (`memcpy` of a constant 1-8
  bytes): they are register loads, not calls. Without this rule R4d
  (`swar` removes `memchr`, adds `memcpy` loads) would read
  `memchr` → `memcpy`, the opposite of what happened.
- The "Coverage" bullet's `mf_art_note_libc` stays as the WRITER's
  mechanism. The control above is the independent check on it.

**Its event.** Both lines are born together in R4a′ (§18.3's event and
reader list, plus the second line). The abi digit is "the next number
at landing" (61 at main 7f94b0cd), never a literal.
**`[rev4.5]`, corrected `[rev4.6]`** (r5 B8) Main's abi is the
handoff's (f116cff5). The digit R4a′ takes is the number current at
landing. No literal is written here.

### R4.3.4 Completeness: every search site migrates, under a checked manifest (Q42 reversed)

**The ruling.** Every emitted search site migrates into the kit, the
`(?m)^` newline `memchr` (M4) included, without waiting for a
performance customer. Frank's reasons:

1. A half-migrated tree makes everyone remember which sites are which.
2. Having every search in one place exposes cross-site (set)
   opportunities that a scattered tree hides.

This is a ruled exception to D77's measured-need trigger. **The
exception covers MIGRATION only**, where each step stays byte-identical
(zero movers). A kit change that MOVES bytes still needs its measured
trigger and its G1 alpha (D77, D144). So in §22 every migration step's
trigger is "completeness: its prerequisites landed", and every mover
step keeps a measured cell.

**The search sites.** These are §8.5's rows whose operation is a
search over a byte span (**`[rev4.6]`**, r5 B6: "a search or
span-compare site", so that N7, a two-operand compare of a run-time
span returning a prefix count, is covered by the definition):

- PF, PRE, OFS and SETREST;
- VERIFY and VMRUN;
- STAY, the scan edge's loop, and VMSPAN at stride 1;
- MLINE (N3);
- ~~`vm_rev_emit`'s backward walk (N6)~~ **RETIRED (D147 add. 12):** not a search site, a mirrored one-position VM step;
- the VM span at stride > 1;
- the encoding seam's span compare (N7).

The last three were "not now"/"no" under the customer rule (§8.5). They
are now pending, with steps M6 and M7 (§22). They need vocabulary (a
backward walk with captures in flight, a strided SKIP). N7's place
under D23 is asked as **Q54**.
**`[rev4.6]`** (r5 B6) The cite is wrong. D23 is the ASCII case-fold
decision. The seam's owner is D58 and DD-12 (the encoding seam, and
the backreference compare through it). N7 lives in `src/enc/`
(`enc_byte.c`'s `$_span_match[_caseless]`), outside C17's `src/gen/`
static scan, and it is a hand-written `for` loop. So, should Q54 rule
yes: C17's static scope adds `src/enc/`, with a vocabulary line for the
`s[at + i] != ref[i]` loop, and M7 carries an `MF_VOCAB` bump for a
run-time-operand `mismatch` with a prefix-count return.

> **`[rev4.7]` RULED (D147 addendum 10, Q54 YES).** N7 is listed
> `pending` in the site manifest, and B6's three corrections are the
> design of record:
> - the cite is D58/DD-12;
> - the definition is "search or span-compare site";
> - C17 scans `src/enc/`.
>
> M7 bumps `MF_VOCAB`. Every "should Q54 rule yes" / "if Q54 rules yes"
> in this revision now reads as ruled.
>
> **`[M7]` As built (2026-10-08):** N7 is `delegated` for the byte-wise
> compares and its `s[at + i]` ceilings are gone from C12; utf8's caseless
> decode walk is its own `pending` row N7U (Q-R8-1), still spelling the
> `span-decode` vocabulary line (§15.8). (Retired, D147 add. 14: not a kit
> site; row and line deleted.)

These are NOT search sites, and are not listed:

- T4 one-position membership (one position, the `member` hook's
  source);
- any DFA or VM step, and T8/T9 (the engine);
- **`[M6]`** (Q-R10-11, kit ruling 2026-10-08) the encoding seam's utf8
  `$_back_step` / `next_pos` loops: bounded per-character decode steps
  (at most 4 bytes), the seam's analogue of T4, not searches.
- **`[R-12]`** (Q-R12-3, D147 addendum 14, Frank 2026-10-09) the encoding
  seam's utf8 CASELESS span compare (`u8_defs_bref_ci`, once manifest row
  N7U): a walk whose unit is the encoding's CHARACTER (a decode on either
  operand), not a byte window. **The rule:** such a walk belongs to the
  encoding, not the kit; its byte-domain sub-loops are kit sites; the kit
  is encoding-blind. N7U is RETIRED: its row, the `span-decode` vocabulary
  line and its C12 row are deleted (C17 13 rows, C12 1 row).

> **`[M6]` As built (2026-10-08):** VMSTRIDE is `delegated` (the VM span
> loop at stride > 1, §15.9) and its `walk-open` ceiling is gone from C12;
> the cursor rung's LAZY rmin prefix, a counted verify of rmin span blocks
> that no vocabulary line saw, is its own `pending` row VMLAZY (Q-R10-7),
> spelling the new `span-count` line. **`[R-12]` BUILT (lane vmlazy,
> 2026-10-09):** NORMALIZE (pcrec abi 70 -> 72) re-spelled the prefix as the
> span scan capped at rmin plus the rung's reach test; REPLACE (zero movers)
> routes it through VMSPAN/VMSTRIDE and DELETES the VMLAZY row (Q-R12-2);
> `span-count` stays at C12 ceiling 0 (Q-R12-6); `$_valid_upto`'s ASCII SWAR
> skip is listed `pending` as VALID (Q-R12-5). N6 stayed `pending` pending Frank's
> Q-R10-1 ruling; **N6 RETIRED (D147 add. 12):** not a search site (a
> mirrored one-position VM step, §R4.3.4's exclusion); its manifest row, the
> `walk-back` vocabulary line and its C12 ceiling row are deleted.

**The CHECKED SITE MANIFEST.** `tests/memfn/site_manifest.tsv` has one
row per search site: site id, emitter function(s), op/handoff, D91
budget, migration step, and status, which is exactly one of
`delegated` or `pending` (the ruled vocabulary, with no third state).
A new check, **C17**, fails on any of the following:

1. **An unlisted site, static half.** An emitter under `src/gen/`
   (**`[rev4.6]`** and `src/enc/`, for N7, if Q54 rules yes)
   spells a C12-vocabulary search form (emitted-text libc search calls,
   table-walk loop texts, runcmp row texts) in a function no `pending`
   row names.
2. **An unlisted site, dynamic half.** A site reaches `mf_emit_site`
   with no `delegated` row for it. The site id comes from the call,
   counted over the corpus compile pass.
3. **A delegated row whose emitter still spells a form.** This is two
   spellings of one search, D122.
4. **A pending row whose emitter spells nothing.** The row is stale and
   must move to `delegated` in its step's REPLACE commit.

- **Counts.** It prints its row counts (delegated / pending, with a K35
  floor equal to the committed row count) and the dynamic half's
  site-call count.
- **Born at R4a with every row `pending`.** Each migration step's
  REPLACE commit flips its rows.
- **Its stated limit:** the static half finds what C12's vocabulary can
  see. A new search spelled in an unrecognised way, such as a hand-written
  byte loop, escapes it until the vocabulary learns the shape. A
  sabotage row plants one recognised form in an unlisted function
  (§17.6).

**The ratchet's end state.** C12's `memchr(` count outside the kit is
9 at 90d396fd. It reads 3 after M1, 1 after M2 and **0** after M4.
Every other C12 vocabulary class likewise ends at 0 in `src/gen/`.
The end state of §9.5 is "pcrec spells no search", not "one
`memchr('\n')` remains".

### R4.3.5 The planner moves live at M5 (Q40, addendum 4)

- At M5, prefix_k's scan model moves into the kit as LIVE scalar-layer
  code. A frozen copy serves only as M5's byte-identity comparator.
- pcrec keeps one SEMANTIC row: a necessary byte set exists beyond
  offset 0.
- The kit plans the scan, and the reseed becomes unconditional on that
  row.
- `<PREFIX>_DFA_PREFILTER` reports pcrec's row. `MEMFN_FORMS` shows the
  kit's plan.
- It is an abi event with a movers census and a bench inbox note.

§22 splits this into **M5** (the model migrates, zero movers, by the
comparator) and **M5′** (the ruled adoption event: one semantic row,
the kit's plan, the unconditional reseed). M5′'s acceptance is G1's
alpha at both layers.

**One tension, stated.** "`MEMFN_FORMS` shows the kit's plan" (addendum
4) meets "`none` iff identical to the SIMD-off compile" (addendum 3).
At SIMD-off, which is the default, a scalar-layer plan change reads
`none`. So the plan is visible in the stamp only on `-fmemfn-simd`
artifacts. At SIMD-off it is attributed by M5′'s movers census and its
switch name. **Q55** asks whether that suffices.

**`[rev4.6]`** (r5 B1, B2, B11) The tension is sharper than stated
above. Until R4f the stamp is constant `none` on every default
artifact. Plan attribution at the default build rests on B2's rule:
the bench attributes kit state by the build recipe it records (abi,
pcrec commit, argv; §R4.4.1). M5′'s chosen offset set is already
visible in `<PREFIX>_DFA_PREFILTER_OFFSETS` (`match_api.md`), which
narrows what a bench consumer misses. Q55 carries the refined
recommendation (§23).

### R4.3.6 Q51 and Q52 rejected: what stands (addendum 7)

- **Q51 REJECTED.** The SIMD-off arm is NOT withdrawn. It is the
  switch's OFF state (`-fno-memfn-simd`): permanent, selectable, and the
  reading every scalar-layer change is accepted on. D147's both-layers
  reading stands: every acceptance reading for a change that touches
  searching reports SIMD-off and SIMD-on.

  **Reading, stated for checking.** Rev 4.2's Q51 bundled a second
  thing: the `-fno-memfn-scan`/`-fno-memfn-loop` bits, the `memfn-off`
  set, `off.tsv` and the `pcrec[memfn-off]` testee. Those selected the
  FROZEN baseline. D147 consequence 1 retires a frozen baseline
  independently of Q51, so they stay withdrawn. Their one role, an OFF
  arm for G1, is D144 item 4's per-change deny (`--memfn-deny=NAME`;
  **`[rev4.4]`** now `--memfn=no-NAME`, a kit registry row, §R4.4.1),
  which is ruled on its own (Q47). If the rejection was meant to bring those bits back, the
  change is this paragraph plus §20.2's two rows.
- **Q52 REJECTED.** The stamp is not re-derived. Q39 as ruled
  (§R4.3.3) stands: the reference is the SIMD-off compile, and the
  value is never keyed on a flag. §L.5 is superseded by §R4.3.3.

### R4.3.7 Every other place the rulings touch

| section | revision 4.2 said | revision 4.3 |
|---|---|---|
| §L.1 | `-fno-memfn-native` / `-fmemfn-native`; libc's place asked as Q50 | `-fno-memfn-simd` / `-fmemfn-simd`; Q50 RULED (SWAR and libc are scalar) |
| §L.3 | the `memfn-off` bits withdrawn (Q51) | they stay withdrawn, by D147 consequence 1; Q51 itself is rejected (§R4.3.6) |
| §L.4 | both layers at `-fno-memfn-native` / `-fmemfn-native` | the same, with the switch spelled `memfn-simd` |
| §L.5 | the stamp re-derived as Q52 | superseded by §R4.3.3 |
| §8.5 profile table | two rows, `portable` / `native` | the SIMD switch: off (`MF_P_PORTABLE_ONLY`) or on |
| §8.6 | K-1..K-5 | K-6 added: cascades (§R4.3.2) |
| §9.4 | customer first (D77) | migration by completeness; customers trigger MOVERS only (§R4.3.4) |
| §9.5 | ratchet reads 1 (N3) or 0 | 0, every class (§R4.3.4) |
| §10.5 | C5's vocabulary half at `-fno-memfn-native`; C9 at `-fmemfn-native`; C11 one line | `-fno-memfn-simd`; `-fmemfn-simd`; C11 checks both lines; C17 new |
| §10.6 | the two layers as profile semantics | adds: a SIMD-on artifact carries no portability promise; the libc record |
| §14.10 | profile row `memfn-native` | the `memfn-simd` pair, both bits in `strategy_denials` |
| §15.7 | "Q42 still says not to move it" | M4 migrates (§R4.3.4) |
| §16 | trigger: R4b's cell | prerequisites only (completeness); `lane/k82hbuild` is merged (f116cff5); K85's re-measure is owed (`[rev4.5]`: it exists, `k82halpha_report.md` §3; see §16's note) |
| §17.2/§17.3 | native over portable; C9 at `-fmemfn-native` | SIMD form over the scalar form; C9 at `-fmemfn-simd` |
| §17.6 | sabotage rows | three rows added (C17's two halves, the libc record) |
| §18 | value re-derived per §L.5 | §R4.3.3 |
| §19 rows 1, 4 | adoption asked as Q40 | Q40 RULED (§R4.3.5) |
| §20.2 | one pair, `memfn-native` | one pair, `memfn-simd` (§R4.3.1) |
| §21.3 | the stamp row | plus the `MEMFN_LIBC` line |
| §22 | rev 4 / rev 4.2 order | rebuilt (`[rev4.3]` block at its head) |
| §23 | Q35/Q36 ruled; Q37-Q52 open | Q35-Q42 and Q50 RULED; Q51/Q52 REJECTED; Q43-Q49 open; Q53-Q55 new |
| `option_sets.md` | family `memfn` over `memfn-native` | over `memfn-simd`; cross-note added |

**What the rulings do not change:**

- the contract (§8, §14) and the site shapes (§15);
- M1's scope and sequence (§16);
- the per-change deny as G1's OFF arm (§L.3);
- the symbol and provenance policy (§20.3);
- the measurement protocol (§21.1).

---

## L. Revision 4.2: D147's layers `[rev4.2]`

**What D147 rules** (Frank, 2026-10-05). pcrec continues scalar
ALGORITHMIC improvement indefinitely. SIMD is a LAYER on top of the
scalar algorithm, never a substitute for it. The scalar layer must be
the best it can be with SIMD off, and its improvements are accepted on
SIMD-off measurements. The SIMD layer must beat the CURRENT best scalar
layer, never an old or frozen one. Every acceptance reading for a change
that touches searching reports both layers. For this design: the kit's
scalar arms ARE the scalar layer, live and improvable; the frozen
pre-migration baseline exists only as a per-migration-step byte-identity
COMPARATOR; the SIMD-off profile runs the CURRENT scalar layer; kit work
and pcrec scalar work proceed in parallel.

Revision 4 had built the opposite in one place: a `baseline` PROFILE,
frozen forever, selected by `-fno-memfn-scan`/`-fno-memfn-loop`, serving
as G1's OFF arm, C5's pin, the stamp's reference and the bench's
`pcrec[memfn-off]` testee (Q38: "keep the baseline forever"). Revision
4.2 removes that role and re-founds each dependent on D147.

### L.1 The two layers, over this design

| layer | what it is here | how a build selects it | the reading |
|---|---|---|---|
| **scalar** | pcrec's algorithm (which facts form the predicate, the plan while pcrec holds it, handoffs, fusion requests) plus every kit arm rendered when `memfn-native` is NOT taken: scalar, SWAR, libc calls, loop-free short-span forms (§8.5 row 2, `portable`) | `-fno-memfn-native` (family `memfn`'s `no-simd`), which is also the DEFAULT until R4f | **SIMD-off** |
| **SIMD** | the kit's native arms (ISA text: §8.5 row 3, `native`) on top of the same algorithm | `-fmemfn-native` (`simd`); the default after R4f | **SIMD-on** |

- The layer line is §8.5's existing policy line: "no text that names an
  ISA". SWAR is in the scalar layer (D122 addendum 3). A libc call is in
  the scalar layer even though glibc's `memchr` is itself vectorized;
  whether that is the line D147 means is asked as **Q50**.
- Before R4e′ there is no native arm, so the SIMD-on reading renders
  the same text as SIMD-off. It is still REPORTED, as "identical (no
  native arm)", so that every reading has both columns from the first.

> **`[rev4.3]`** (addenda 6-7, §R4.3.1) One SIMD switch,
> `-fno-memfn-simd` / `-fmemfn-simd`, default OFF until the SIMD hold (`[r9b]` superseded, D147 add. 11)
> lifts. Read the table's `-fno-memfn-native` as `-fno-memfn-simd` and
> `-fmemfn-native` as `-fmemfn-simd`. Q50 is RULED as the policy line
> above: SWAR and libc are scalar layer. "Native arms" are the kit's
> SIMD forms, whose contents (levels, cascade, fallback) are its own
> per-site choice.

### L.2 The baseline becomes a per-step comparator

What a migration step keeps, unchanged: the IMPLEMENT/REPLACE pair
(§9.1); I1, the shadow comparator against pcrec's own emitter; I2,
movers by ID against the step's parent; I3, the standing identity gates
with no re-pin; `tests/memfn/pins/arms.tsv` RECORDED at the step from
pcrec's pre-migration emitter (§17.4). Together these prove that the
kit's arm, at birth, is pcrec's text byte for byte.

What goes:

- **The `baseline` PROFILE** (§8.5 row 1) as a permanent, selectable
  arm. After the REPLACE commit, the as-born arm IS the site's scalar
  arm: live kit code, edited by kit lanes, improved on SIMD-off
  acceptance, with the abi ritual when it moves a byte (§10.3). The
  pre-migration text is reachable afterwards only in history.
- **"FROZEN"** (§9.2), "changed only by a ruled abi event" (§16 item 3,
  Q27, Q38) and "keep the baseline forever" (Q27/Q38's recommendation).
- **`arms.tsv` as a freeze.** It stays as a CHANGE DETECTOR: it pins
  the CURRENT scalar arms' digests over their fixtures. Every kit change
  that moves an arm's text re-pins its rows in the same commit as its
  abi event, so it is one of that event's readers (D94's grep must find
  it). The sabotage row "one arm edited by one byte, no re-pin" still
  turns it red (§17.6).

Terminology: in §9-§18, "the baseline arm" now reads "the scalar arm
as born at its migration step". Where those sections reproduce bytes
(§15), they describe the step's comparator, which is unchanged.

### L.3 The OFF arm is each change's own deny

With no permanent baseline, `-fno-memfn-scan` and `-fno-memfn-loop`
have nothing to select that is not already the scalar layer or a
change's own deny. **They are withdrawn (Q51), and with them family
`memfn`'s `memfn-off` set, `tests/memfn/pins/off.tsv`, and the bench's
`pcrec[memfn-off]` testee.**

- **Every kit change that moves a byte carries its own deny** (D144
  item 4): **`[rev4.4]`** a row of the kit's own option registry
  (`memfn/src/options.def`), reached as `--memfn=no-NAME` (Q47 refined,
  §R4.4.1). That deny renders the site as it
  was before the change. This is how every pcrec optimization is
  already controlled; the kit gets no special mechanism.
- **The per-change comparator.** At the change's own commit, the corpus
  and bench patterns compiled with that deny are byte-identical, by ID,
  to the parent commit's default (§9.3 I2's tool, applied to the
  change). It is checked at that commit and never pinned afterwards: it
  is what makes "default vs deny" a parent-vs-change timing, which is
  D147's comparator generalised from migration steps to every change.
- `DELEG_SITES` keeps its budget column (it sets `MF_P_INLOOP`, C10)
  and loses its deny-bit column. §8.5's profile table is two rows:
  `portable` when `memfn-native` is not taken, `native` when it is.
  pcrec's own shipped denies on migrating sites (§14.10: bits 16, 30-33,
  43-46, `-fno-offset-skip` …) are unaffected.

### L.4 G1 under D147: both layers, against the current state

- **ON** is the default; **OFF** is the change's own deny (L.3). The
  population is the pcrec-side diff of those two compiles (still never
  the kit's `moved`, r3 G-F5). Regimes, the floor, pooled bins with
  their floor of 8, the cadence (every memfn abi event) and the armv8
  statement are §17.2's and §21.1's, unchanged.
- **Both layers, every time.** The ON/OFF pair is timed at SIMD-off
  (`-fno-memfn-native` on both arms) AND at SIMD-on (`-fmemfn-native` on
  both arms). Each is reported.
- **Which reading accepts what.**
  - A SCALAR-LAYER change (a scalar or SWAR arm, a plan, a fused scalar
    composite, or a pcrec algorithmic change to a delegated site's
    description) is accepted on its SIMD-off reading. Its SIMD-on
    reading is reported, and it re-opens every native arm on its
    movers (next bullet).
  - A SIMD-LAYER change (a native arm) is accepted on SIMD-on against
    the CURRENT scalar layer of the same build: its movers timed at
    `-fmemfn-native` against `-fno-memfn-native`. Beating the arm it
    replaced is not enough.
  - **After any scalar-layer change**, the native arms on its movers
    are re-read against the improved scalar (D147 consequence 3). A
    native arm that no longer beats it past the floor is a `D-n`
    defect (§20.1). The kit's interim answer is its own deny for that
    arm, or a selection row that stops choosing it.
- **D146's revisit-when** ("a delegated site's kit code is measured
  worse than pcrec's pre-migration form") is read per D147 as: worse
  than the scalar layer it replaced, i.e. its own deny, in either
  layer's reading.
- **The bench's batch-gate testees** become the two layers:
  `pcrec[simd]` beside the default from R4e′ (when the default is
  SIMD-off), and `pcrec[no-simd]` after R4f's flip. Each is requested
  through the bench inbox (D78) when it first has movers.

### L.5 The stamp reports the SIMD layer (Q39, re-derived as Q52)

> **`[rev4.3]`** SUPERSEDED. Q52 is REJECTED and Q39 as ruled stands
> (addenda 3, 7). The stamp is §R4.3.3: `none` iff identical to the
> SIMD-off compile, else the forms used (with carried levels), plus the
> `MEMFN_LIBC` record. The consequence below ("M1 and every scalar-layer
> change leave the stamp `none`") still holds, because SIMD is off by
> default.

Revision 4's `<PREFIX>_MEMFN_FORMS` was `none` iff the artifact equalled
its own `memfn-off` compile. That reference is gone. Revision 4.2
re-points it at the layer line, the fact D147 makes every reading
report:

- **`none` iff the artifact is byte-identical to its own
  `-fno-memfn-native` compile** of the same build (no native arm was
  rendered); otherwise the comma-joined NATIVE form ids, in site order.
  Every artifact carries it (Frank's Q3, D81), and it is born in its own
  abi event R4a′ exactly as §18.3 says.
- **C11's reference compile** becomes `-fno-memfn-native`: a pcrec-side
  diff of two CURRENT compiles, sharing no source with the kit's
  `moved`. Its assertions are §18.2's with `memfn-off` read as
  `-fno-memfn-native`.
- **Consequence:** M1 and every scalar-layer change leave the stamp
  `none`, so M1 stays zero-mover. Before R4f every default artifact
  reads `none`; after it, the stamp says which artifacts ran SIMD.
- **Cost, stated:** scalar-layer kit forms are not bucketed by the
  stamp. They are attributed by their abi event's movers census and
  their switch names, and a bench triage flips `--memfn=no-NAME`
  (`[rev4.4]`; was `--memfn-deny=NAME`). A
  scalar-form id list is not built until a bench consumer asks for it
  (D77).

### L.6 Every other place D147 touches

| section | revision 4 said | revision 4.2 |
|---|---|---|
| §8.5 profile table, row 1 | `baseline` under the budget deny bits, the guard's off arm | withdrawn (L.2, L.3); two rows remain |
| §8.6 K-5 | the kit's timed control against the scalar byte loop and the baseline arm | against the scalar byte loop and the CURRENT scalar arm; a native arm is selected only past the floor over it |
| §9.2 | "pcrec's last spelling, frozen" | the as-born scalar arm; frozen only as the step's comparator (L.2) |
| §9.5 | "the baseline profile holds everything pcrec used to spell, frozen" | the scalar layer holds it, live |
| §10.1, §17.2 G1 | ON vs `memfn-off` | ON vs the change's own deny, both layers (L.4) |
| §10.5 C5 | `memfn-off` byte-identical to the baseline pin | that half is replaced by the per-change comparator (L.3); the `-fno-memfn-native` vocabulary half stays |
| §10.5 C11, §18 | `none` against `memfn-off` | `none` against `-fno-memfn-native` (L.5) |
| §10.6 | "the baseline is pcrec's pre-migration text" | the spec states the two layers and the per-change denies |
| §14.6 | a new shape's `baseline` is the generic row; G1 UNREACHED for it | a new shape's change carries its deny like any other, which renders what the site had before; G1 reaches it |
| §14.9, R4j, Q40 | the model moves as "the baseline's frozen planner" | the model moves as the SCALAR LAYER's planner: byte-identical at M5 by the comparator, live after it |
| §16 item 2 | waiting so K85's text does not become the guard's OFF arm | the wait stands for byte identity (nobody edits the text under comparison; R4b is measured post-handoff); K85's cure is a scalar-layer change accepted on its own, before or after M1 |
| §16 item 3 | "a baseline change is a ruled abi event" | every scalar-arm change is an ordinary kit change: SIMD-off acceptance, the abi ritual when it moves a byte |
| §17.4 | `arms.tsv` frozen; `off.tsv` | `arms.tsv` a change detector re-pinned by each arm change; `off.tsv` withdrawn |
| §20.1 | `inbox_from_pcrec.md` / `outbox_to_pcrec.md` | as built: `memfn/docs/requests.md` (manager only, `[requests]` commits) and `memfn/docs/responses.md` (kit only, `[responses]` commits); roles unchanged |
| §20.2, option_sets.md | three axes; family `memfn` = auto / simd / no-simd / memfn-off | one deny/force pair `memfn-native` (default OFF) plus the kit's generated `--memfn-deny=` rows (**`[rev4.4]`** not axes: the kit's own `--memfn=` registry, §R4.4.1); family `memfn` = auto / simd / no-simd |
| §21.2, §21.3 | the G1 OFF arm is `memfn-off`; the baseline arms change only by ruling | rows rewritten in place (`[rev4.2]`) |
| §22 | R4b/R4c/R4d/R4j as written | annotated in place: R4b reports both layers, R4c lands one axis, R4d's testee is `pcrec[simd]`'s precursor, R4j moves the scalar planner |
| §23 Q38 | keep the baseline forever | revised: a per-step comparator only |

### L.7 What D147 does not change

The delegation contract (§8, §14), the site shapes (§15), M1's scope
and sequence (§16), the symbol policy and provenance (§20.3), the
measurement protocol (§21.1) and the build order's prerequisites and
triggers (§22) stand. Three questions are new (Q50-Q52); Q35 and Q36
are ruled (§23).

---

## R4. Revision 4: the contract from the emitters' actual shapes `[rev4]`

**What the r3 panel found.** The delegation architecture held, and no
finding is a blocker. But byte-identical, zero-mover migration was not
reachable through rev 3's hooks. Those hooks were written from ideal
sites, and today's sites have shapes the contract could not express. A
site returns on a miss, breaks, or is a whole function. It is an
expression inside pcrec's own `if (guard && EXPR) goto`. It reads a run
counter after the loop, emits helpers lazily, or is tallied into a
stamp. Two errors also repeated earlier ones: the stamp rule
contradicted Frank's Q3, and the shipped deny flags on the migrating
sites were not named. Revision 4 rebuilds the contract by reading each
M1 emitter at main `1c2ba975` (and the handoff on `lane/k82hbuild`,
`9bb97c7c`, abi 61). For every M1 site shape, §15 shows the `mf_site`
and hooks that reproduce today's text byte for byte.

### R4.0 The standing rulings this revision honours

| # | ruling | where it binds here |
|---|---|---|
| 1 | Frank's **Q3** on `litscan_k82h.md`: a stamp goes on EVERY artifact of its family, `none` where it does not apply. Presence never varies within a family (D81) | §18. The stamp is born with its own every-artifact abi event, BEFORE M1's replace commit. It carries no kit version. C11 checks the value, not presence |
| 2 | **D144 item 4**: every optimization keeps its own deny, and every shipped deny on a migrating site keeps working and is swept by the byte-identity gate | §14.10 gives each shipped deny's fate (bits 16, 30, 31, 32, 33, 43, 44, 45, 46, `-fno-offset-skip` …). The kit's per-form switches become real axes (**`[rev4.4]`** refined: rows of the kit's own registry, listed by `--list-axes`' `memfn` section, §R4.4.1). I2 sweeps every `axes.def` axis and every comment tier (§17.1) |
| 3 | **D146**: pcrec carries no arch knowledge and does no cost comparison | §19 lists every remaining place pcrec prices kit-owned search code, with its fate |
| 4 | **D76/D94**: abi changes follow the ritual. Readers are found by grep, including the byte-count reader class | §18.3 (the stamp's own event), §17.4 (per-arm pins, not whole-artifact pins) |
| 5 | Measured terms are OK; tuned cutoffs are not | §19 classifies every pcrec number on a delegated site as a measured term, a ruled semantic bound or a tuned cutoff. Only measured terms and ruled bounds survive in pcrec |
| 6 | **D145**: injected text must carry 0BSD, CC0, Unlicense, or a licence with its own output exception | §20.3: per-file provenance, the translated Rust `memchr` under its Unlicense arm, the kit under 0BSD |
| 7 | **D78**: single writer each way | §20.1: two files from day one. The manager is the sole writer of requests |

### R4.1 Every finding, and where it is answered

| id | finding (short) | disposition in rev 4 | section |
|---|---|---|---|
| F1 | hooks only write values; real sites return/break on a miss, are whole functions, or are expressions inside pcrec's `if` | Three site FORMS (expression, statement, function). An `on_miss` statement hook, an `indent` hook, and a `fn_name` hook plus the parameter list. **`[rev4.1]`** There is no opening-keyword hook: pcrec writes `kw (state == K) {` and its braces itself (§15.7) | §14.1, §14.2 |
| F2 | ADVANCE returns only the cursor; the scan edge's post-loop reads the kit's run counter; `scan_test` reads through `dir->peek` | ADVANCE gains a `count` lvalue with a declared start, a bound-reached contract, and a `peek` hook | §14.3 |
| F3 | in-emitter denies (`-fno-run-overlap`) have no channel to the kit; I2 cannot see them silently die | `mf_site.denies` carries every in-emitter deny. I2 sweeps every `axes.def` axis and every comment tier | §14.10, §17.1 |
| F4 | pcrec tallies emitted forms (`RUN_WORDS`, lazy helpers, the row name returned); helper placement moves | **`[rev4.1]`** A per-artifact `mf_art` (no `mf_plan`): `mf_stamps` writes the tallies through the sink, sites record helper needs and `mf_flush_helpers` writes them, `mf_includes` reports the headers. Helpers go "before first use" at the two points pcrec uses today | §14.8, §15.6 |
| F5 | empty and wrapped ranges undefined | `hi` is spelled `n − end_back`, never as a wrapping expression. Every site declares its EMPTY outcome: MISS, NOP or EXCLUDED | §14.4 |
| F6 | the K82 gate is ONE site (lead byte + run + whole run + rest of set); ALL_PRESENT has no position; set-leads' order is pcrec's rarity choice; ON_CAND has no order | ALL_PRESENT gains `ret_pred`, the predicate whose leftmost position it RETURNS. ON_CAND visits in ascending order (descending if reversed). `DELEG_SITES` marks the sites whose result is used as a POSITION | §14.3, §14.5, §15.5 |
| F7 | rule 3 (every term holds) contradicts `consumer` and M5 (dropping terms) | REQUIRED vs OPTIONAL terms. RETURN promises `c` ≤ the true leftmost, with every REQUIRED term holding at `c` | §14.5 |
| F8 | totality needs a generic scalar row; a new shape has no baseline; shape bounds unchecked | Every kit table ends in a generic scalar row, tested over a generated predicate space. A new shape's baseline is the portable scalar arm, declared, and is UNREACHED for G1. Shape bounds are `_Static_assert`ed against pcrec's own derivation caps | §14.6 |
| F9 | `plan_hint` "transitional", but the frozen baseline needs it forever | `plan_hint` is permanent while pcrec computes it. At M5 the MODEL itself moves into the kit as the baseline's frozen planner (implement-then-replace, byte-identical), and only then does pcrec stop computing it | §14.9 |
| F10 | `on_cand` text may be copied; labels, statics or control flow out of the loop break that | `on_cand` must be duplicable. A structural check C13 holds it | §14.7 |
| F11 | no lower read guard (N3 reads `s[start−k]`, the reseed reads `s[from−1]`) | Negative term offsets with a `floor` hook. The kit never reads below `floor` | §14.7 |
| F12 | the whole-artifact baseline pin forces re-pins on unrelated abi changes; baseline arms duplicate pcrec helpers | C5 checks a per-ARM digest pinned under `tests/`. The sink adapter exposes pcrec's escapers, so the kit never copies them | §17.4, §14.2 |
| F13 | pcrec still prices kit-owned search code | The list, each with its fate | §19 |
| G-F1 | the movers-only stamp contradicts Q3 | Stamp every artifact. **`[rev4.1]`** No kit version and no `MF_VOCAB` in the stamp; its value is `none` or opaque form ids. Its own every-artifact abi event, before M1's replace. C11 checks the value | §18 |
| G-F2 | the shipped denies on the migrating sites are unnamed and unswept; per-form switches are not axes | The fate table, I2 over every axis, and per-form switches as `axes.def` rows (**`[rev4.4]`** superseded: the kit's own registry, §R4.4.1) | §14.10, §17.1 |
| G-F3 | C9 fails on the Mac and is vacuous under `portable` | A header shim, a native-enabled config, and a K35 floor on arms compiled | §17.3 |
| G-F4 | armv8 has no verdict-grade guard | Stated plainly, in the spec too | §17.2 |
| G-F5 | G1's population came from the kit's own `moved`; thin bins; undeclared regime | Movers come from a pcrec-side default-vs-`memfn-off` artifact diff. The regime is declared, and bins are pooled with a floor | §17.2, §21.1 |
| G-F6 | G1's cadence misses kit re-tunes | G1 runs on the movers of EVERY memfn abi event | §17.2 |
| G-F7 | C4's held-out plant is overclaimed and box-dependent | Its scope is stated honestly, the plant count is printed per box, and matching is case-insensitive | §17.5 |
| G-F8 | sabotage rows may not be mech-runnable; the baseline digest lives in the kit | Per-pattern and per-arm pin digests under `tests/memfn/pins/`, an in-tree C11 census, and `SAB_REACH` on every row | §17.4, §17.6 |
| G-F9 | the standing design questions are unanswered | Three sections | §21 |
| G-F10 | freezing the baseline now would freeze K85's open regression and collide with live edits; the handoff is unmerged | M1 is sequenced after `lane/k82hbuild` merges and after K85's re-measure. After migration, edits to delegated emitters are kit-lane work | §16 |
| G-F11 | M1's scope exceeds its trigger; R4a/R4f are circular | M1 is narrowed to the triggering site class's closure under "all callers". R4f's circularity is broken by the opt-in `-fmemfn-native` | §16, §22 |
| G-F12 | `-fno-memfn-native` polarity inverted against house convention | Axis `memfn-native`, default OFF, enabled by `-fmemfn-native` (D112's shape). R4f is the flip | §20.2, §22 |
| G-F13 | one shared request file breaks D78 | Two files from day one | §20.1 |
| G-F14 | analyze/ is the inverse precedent; `mf_*` exported unprefixed from libpcrec; Rust memchr provenance | A symbol policy (`pcrec_mf_*` at link, hidden visibility), and per-file Unlicense provenance | §20.3 |

**Count:** 27 findings (F1-F13, G-F1..G-F14), all answered. One answer
departs from the options the panel offered: for F9 the MODEL migrates at
M5, so neither a permanent pcrec cost model nor a baseline re-pin is
needed (§14.9). Its open sub-question, adoption, goes to Frank as Q40.

### R4.2 What revision 4 overrides in revision 3

- §8.2's `mf_site`/`mf_result` and §8.3's hooks are EXTENDED, not
  replaced (§14). Rule 2 gains a caller-guard declaration for
  expression-form VERIFY sites (§14.7). Rule 3 is restated over
  REQUIRED and OPTIONAL terms (§14.5).
- §8.5's profile table: `-fno-memfn-native` "DEFAULT ON" becomes axis
  `memfn-native`, default OFF, enabled by `-fmemfn-native` (§20.2).
  Rows 1-3 are otherwise unchanged.
- §9.4's M1 is narrowed and re-sequenced (§16). M5 now carries the model
  (§14.9).
- §10.1's population and cadence (§17.2). §10.3's stamp (§18). §10.4's
  plant claim (§17.5). §10.5's C5 and C9 (§17.3, §17.4). §10.7's rows
  (§17.6).
- §11.3's single ledger becomes two files (§20.1). §11.1 gains the
  symbol policy (§20.3).
- §12.2's R4a-R4j are replaced by §22. §13's questions are superseded by
  §23 (Q35-Q49). Q24-Q34 are re-derived there, not merely renumbered.

---

## R3. Revision 3: delegation, not a price market `[rev3]`

**The ruling (D146, Frank, 2026-10-05).** pcrec hands a search SITE to
the kit as a description: the operation, its operands, pcrec's proven
facts (span bounds, anchoring, a density hint) and fusion hooks. The kit
returns the code for that site and owns every choice inside it: SIMD
forms compiled per ISA, the always-present scalar fallback, short-span
loop-free paths, libc calls. pcrec does no cost comparison and carries no
architecture knowledge. pcrec's existing scalar forms for delegated sites
migrate into the kit as its scalar arms, implement-then-replace,
byte-identical first. The two projects are tightly coupled, like
pcrec-bench: when pcrec needs compound work ("this check followed by
this check", a scan fused with a verify or a handoff), the kit provides
it. The guard is pcrec's own bench/alpha timing with the kit on vs off.
Revisit when a delegated site's kit code is measured worse than pcrec's
pre-migration form and the kit cannot fix it.

**Why it replaces rev 2.** The r2 panel
(`../../dev/reviews/2026-10-05-r2-memfn-k0.md`) found that the
architecture held and the price layer did not: the regime flips verdicts,
"corners prove dominance" is a model, pcrec's rows were priced from the
kit's own loops, and a recalibration moves bytes with no abi event. Every
one of those is a property of putting MEASURED NUMBERS ON THE BOUNDARY.
Delegation takes the numbers off it. The kit may still measure and
compare, but behind its own tests, and pcrec never reads the result
except as code.

**What rev 3 is, in one paragraph.** pcrec describes a site as an
`mf_site` (§8.2): an operation over a PREDICATE (a conjunction of
position terms: byte sets and masked runs at offsets from the candidate),
the proven span, anchoring, density hints, a policy word and a handoff.
The kit writes the site's code into pcrec's sink through text hooks
(§8.3): subject, read limit, bounds, result variable, cursor, and an
optional per-candidate verify. Compound work is the predicate algebra
plus a vocabulary pcrec extends by request (§8.4). pcrec's only
decisions are WHICH SITES ARE DELEGATED, by operation type, and which
PROFILE each asks for: `baseline` (pcrec's frozen pre-migration text,
the guard's "off" arm), `portable`, or `native` (§8.5). The kit decides
everything else with its own first-match tables and its own measured
data and tests (§8.6). pcrec's scalar forms migrate in customer order,
each byte-identical under the identity gates (§9). The guards are the
kit-on/kit-off timing, the kit's exhaustive tests, the abi ritual for
any kit change that moves a byte, the arch-blindness detector and a
cross-target syntax check (§10). The kit lives in-tree first as
`memfn/`, with a request ledger on D78's shape (§11). option_sets.md's
`vector` family becomes a `memfn` family of three deny bits, and the
first mover is K82's fused scan+verify after the handoff lands (§12).
Questions Q24-Q34 (§13).

### R3.1 What survives from revisions 1 and 2

- **The table inventory** (§1: T1-T9, N1-N7) and the seven sites that do
  not slot cleanly as built (§2.4). They are now the migration's work
  list (§9).
- **`SCAN_ROWS`' site set** (PF, PRE, OFS, STAY, EDGE, VMSPAN, SETREST),
  D139's sites-as-bits shape. The sites stay; the per-site ROWS do not
  (§8.5).
- **The hook idea** (§3.3), narrowed to text hooks with a written
  contract (§8.3). The `fallback` hook dissolves: the scalar fallback is
  the kit's.
- **K1/K2/K3** (§3.3) as the kit's INTERNAL layering: primitives,
  composition generator, stand-alone CLI and reference functions. pcrec
  calls only K2's site entry. K0 is withdrawn.
- **The composition model** (§4: primitive families, C1 classifier and
  C2 shape tables, the fixed library as generic-parameter outputs, the
  scalar byte loop as the only test reference). It is wholly the kit's.
- **The zero-mover stub idea** (rev 2 R4c). It becomes stronger: the
  first migration step routes real sites through the kit at ZERO movers,
  so the delegation path is live code from its first commit (§9.1), not a
  stub.
- **The fixed `portable` default** for `--isa` (§R2 finding 3, Q18):
  never detected from the build box. It is carried as an opaque
  pass-through (§8.2), and it stays HELD with R4h.
- **The deny-bit budget argument** (Q15): bits per BUDGET and kernel
  CLASS, never per ISA (§8.5).

### R3.2 The r2 panel's findings under delegation

Each finding is **carried** (still binds pcrec, answered in the section
named), **moved inside the kit** (still binds, but as an obligation of
the kit's own design and tests, listed in §8.6), or **dissolved** (its
premise was the price boundary, which no longer exists).

| id | sev | finding (short) | disposition | where, and why |
|---|---|---|---|---|
| P1 | HIGH | the price regime is unspecified and flips verdicts | moved inside the kit | the kit's choices among its arms still face chained vs isolated, hit vs miss. pcrec reads no price, so a regime error can no longer flip a pcrec selection. §8.6 obligation K-1 |
| P2 | MED | the crossover depends on min/median as lo/hi | moved inside the kit | a statistic of the kit's protocol (§8.6 K-2) |
| P3 | HIGH | bilinear corner dominance is a model | dissolved | pcrec has no dominance test. If the kit uses one, it is the kit's model with its own tests (K-1) |
| P4 | MED | "compare on r alone" is false for FIND_PAIR / ALL_PRESENT | moved inside the kit | K-1 |
| P5 / B3 | HIGH | pcrec's rows priced from the kit's own loops (shared source) | dissolved | pcrec's rows are not priced. The guard's "off" arm is pcrec's pre-migration text, pinned byte for byte by pcrec's identity gates (§10.1), and the timing is pcrec's own bench. Neither is computed by the kit |
| B2 | HIGH | `prefix_k.c:65-68` already holds measured machine constants | carried, staged | those constants choose WHICH term the offset-k skip scans and whether to adopt it: a scan PLAN, which D146 puts in the kit. §9.4 stages the move (pcrec's pick travels as a plan hint first), Q29 |
| P6 / B4 | MED | "every arm" vs `any_win`; arm provenance; three more contradictions | dissolved (pcrec) / moved (provenance) | pcrec has no arm notion. Which libc and compiler the kit's data came from is the kit's provenance (K-3) |
| K2 | HIGH | costs depend on the compiler (×2.4, gcc vs clang) | moved inside the kit, plus one spec sentence | the kit keys its data by compiler class and may ladder on compiler macros (K-3). pcrec's spec states that the kit's choices are measured under gcc, pcrec's target compiler (D2), §10.6 |
| P7 / K4 | MED | knobs in disguise: statistic, segment cap, extrapolation, ladder | moved inside the kit | K-2: protocol constants with a decision record in the kit, and a generator that fails rather than truncates |
| P8 | MED | per_hit unpriced; shape-inherited prices; unflagged in-loop sites; STALE granularity | moved inside the kit, plus one pcrec check | the in-loop half binds pcrec: a site's D91 budget is a FIELD of pcrec's delegation table and the request's `MF_P_INLOOP` bit comes only from it (§10.5 C10). The rest is K-1/K-2 |
| K1 / D1 | HIGH | new data moves emitted bytes with no abi event; no stamp | carried | ANY kit change that moves any byte pcrec emits is a pcrec abi event in the same commit, found by D94's grep, with the movers-by-ID census and the every-artifact stamp (§10.3; **`[rev4.1]`** §18, not movers only). In-tree, the kit change and the bump are one commit (§11.1) |
| P9 / C-a / C-b | HIGH | the timed control has no home, no long subjects, no armv8 arm | carried | it is now D146's guard: alpha per mover step on Linux, the batch gate's `memfn-off` bench testee, long subjects, a mover population with a floor, and a directional Mac arm (§10.1, Q31) |
| B1 | HIGH | the arch-blindness regex misses most vocabulary; weak plant | carried | rebuilt: seven vocabulary classes, one positive control each, a plant held out from the regex's source, wider scopes, plus two delegation classes (§10.4 C4) |
| B5 | MED | the other architecture's `#if` arms are never compiled | carried, on both sides | the kit cross-compiles every arm it can emit; pcrec runs `-fsyntax-only` per arm over its own artifacts, with an arm count (§10.5 C9) |
| K3 | MED | `mf_pricelist` ~28 KB on emitter stacks | carried, smaller | the request and result are small (§8.2) and come from pcrec's arena. C10 forbids `mf_*` request/result structs as automatics under `src/` |
| K5 / L1 | MED/LOW | kit text reaches artifacts against `third_party/`'s rule; licence; intrinsic headers | carried | §11.2 and Q26: 0BSD for the whole kit, the `third_party/` sentence updated at extraction, compiler-provided headers named in the spec |
| C-c | MED | the price verifier's midpoints were empty below 64 B | moved inside the kit | K-2 |
| C-d | MED | sabotage rows named timed detectors mech cannot run | carried | deterministic detectors only (§10.7) |
| C-e | MED | no `--check` for the price table; the R4c stub made the row's logic dead code | dissolved (pcrec) / moved (`--check`) | the migration routes real sites through the kit at zero movers, so pcrec's delegation code is never dead (§9.1). The kit's own data needs its own `--check` (K-2) |
| R1 | MED | the native default flip had no ruling designed | carried | `-fno-memfn-native` is ON by default during the SIMD hold, and the flip is its own ruled event (§12.2 R4f, Q28) |
| R2 | MED | R4c′'s trigger vs the handoff's likely removal of those cells | carried | the first mover's trigger is restated after the handoff lands and is measured on the post-handoff build (§12.2 R4d) |
| R3 | LOW | circular R4b/R4c triggers | carried | every step separates its PREREQUISITE (a step) from its TRIGGER (a measured cell or a ruling) (§12.2) |
| P10 / P11 | LOW | published spreads were min..max of 3; "a slow box moves nothing" | dissolved | no spread or scaling claim crosses the boundary |

**Count:** of 23 rows, 11 are carried (B2 staged), 7 move inside the
kit (P8 keeps one pcrec-side check), 3 dissolve outright, and 2 split
(dissolved for pcrec, moved for the kit: P6/B4 and C-e). Every HIGH that
was about MEASUREMENT (P1, P3, P5) leaves pcrec. Every HIGH that was
about the ARTIFACT or the CHECK (K1, P9, B1) stays.

### R3.3 What rev 3 removes from revisions 1 and 2

- §7 entire: the token-priced K0 query, `mf_pricelist`, `mf_dominates`,
  the reference terms `LIBC_*`/`LOOP_*`/`CMP_WORD8`, `memfn/cal/` as
  pcrec-visible data, and checks C2, C3, C7 and C8 as pcrec checks. C1,
  C4, C5 (reshaped) and C6 survive in §10.
- The `kit` ROW with a price predicate (§2.2 rev 2, §7.5), and pcrec's
  per-row price-formula fields.
- §2.5's `fallback` hook and its invariant's reason. The invariant
  itself (one scalar spelling per search) now holds because pcrec has
  NO scalar spelling of a delegated search after its migration step.
- Questions Q16, Q20 and Q23 (dissolved), Q12 (ruled, then superseded
  by D146), and Q19 (replaced by Q31). §13.1 maps every old question.

---

## R2. Revision 2: what changed and why `[rev2]`

**The ruling (Frank, 2026-10-05, on Q12).** He agreed with the K1/K2/K3
split, with one major refinement: *"I'd like pcrec as much as possible to
not know about the architecture details. I don't want pcrec to have
parallel knowledge in its decision tables to e.g. 'use avx2 here' if we
can avoid it. Perhaps it can query the library, given an opaque arch
token, metrics, various measures it can use to determine when to request
code injection."* And: *"That might remove the need for arch sub-panels
then."*

**The agreed shape, designed out in §7.** The kit gains a fourth layer,
**K0, CAPABILITY AND PRICE QUERY**:

- pcrec holds an OPAQUE token, from `--isa` or the fixed default
  `portable` (§7.2). pcrec never branches on it. It only passes it to the
  kit and prints it into a stamp. The C type makes this structural: pcrec
  holds an `mf_token *` with no accessor except its printable name.
- pcrec asks an ARCHITECTURE-NEUTRAL question. The question is an
  operation descriptor (find-in-set, skip-in-set, pinned pair, verify a
  run, all-present) plus the site's proven facts (span bounds, density
  interval, handoff) and the token (§7.3).
- The kit answers with a PRICE LIST. It lists the kernels it can generate
  for that token, each with piecewise-affine costs in one common unit
  (fixed picoseconds per call, picoseconds per byte, picoseconds per hit,
  each with its measured spread), its injected code bytes, and its
  arch-neutral site obligations. Whether a kernel is AVX2, SSE2, NEON or
  SWAR stays inside the kit.
- pcrec's decision table gets ONE arch-blind row, `kit` (§7.5). It
  selects the first kit quote that DOMINATES the price of the table's next
  applicable row over the whole box of the site's proven span and density,
  on every architecture arm, at the pessimistic end of both spreads. pcrec
  prices its own scalar rows in the same unit, from reference terms the
  same calibration run measured. Injection is requested only when that row
  wins.
- The prices are measured calibration tables, one per token, shipped as
  DATA in the kit and generated by a calibration probe through a
  `generate.py`. This is `third_party/`'s "a data source compiles to
  generated tables" rule (§7.7). A token no house box can measure (x86-64
  v4, SVE, SVE2) answers UNPRICED, and an UNPRICED token never selects a
  kit kernel.

**What this removes from pcrec** (§7.9 has the list):

- revision 1's four vector rows (`loopfree`, `vec-verify`, `vec`, `swar`)
  and T6's `vec-masked`. They become one `kit` row per table;
- the `BASE`/`DECLARED(L)` predicate vocabulary (§2.1);
- the vector width `V` that leaked into row 1's predicate;
- the `#if` ladder as a pcrec decision (§2.5). The ladder becomes kit
  text, and the fallback hook stays pcrec's;
- [OPT-SETS]'s `isa` poset, the `isa-route` axis and constraint rows 6-8.
  The `vector` family's four ISA-shaped bits are replaced by three bits
  named for D91's budgets and the kernel class. The "arch sub-panels"
  Frank named are those, and they go.

**What it adds:**

- one opaque value axis (`isa`, the token);
- three deny bits (`-fno-kit-scan`, `-fno-kit-loop`, `-fno-kit-native`),
  where revision 1 had four;
- one pass-through list option (`--kit-deny=`);
- the arch-blindness detector (§7.8 C4). This is a check that `src/`,
  `cli/` and `lib/` name no ISA, which turns Frank's "as much as possible"
  into a red test. Measured at this pin, the tree is ALREADY arch-blind:
  the C4 regex finds exactly ONE hit in `src/`, `cli/` and `lib/`, a
  comment at `src/opt/prefix_k.c:45` citing a glibc AVX2 measurement. So
  the allowlist is born with one entry. K0 is what keeps that number at
  one while kernels arrive.

**What did NOT change.** The table inventory (§1) and the seven sites that
do not slot cleanly (§2.4) still hold. So do the boundary's K1/K2/K3 split
and its hooks (§3.3), the composition model (§4) and the scalar-byte-loop
test reference (§4.5). [MEMFN]'s Linux run (`linux_results.md`) confirmed
T-C on x86 under gcc and clang: a `static const` descriptor through one
header kernel IS the hand kernel. That is the evidence the K2 boundary
rests on, and K0 does not touch it.

**Three findings this revision produced** (each in §7):

1. **No cutoff survives, and none is needed.** The Linux numbers already
   contain a crossover that revision 1 would have had to encode as a
   threshold. A fused SSE2 pass beats two glibc calls up to 64 B and
   loses from about 512 B. Under the dominance rule (§7.5) that crossover
   is a property of the two price lists, so it is never written in pcrec:
   - a proven span of 64 B or less selects the fused kernel;
   - an unproven (rest-of-subject) span does not, because the dominance
     check runs to infinity on the last segment's slope.

   The rule needs no assumed call span W, and W is the term
   `litscan_k82b.md` found decisive and could not source. The rule is
   `sel_cost.md` §3's admission rule ("the sign holds in every regime")
   made exact over a box. Pairwise price differences are bilinear in
   (span, density) on each segment, so checking the box's corners is a
   proof, not a sample.
2. **Density needs no prior at the default.** For the RETURN and ADVANCE
   handoffs, both rows read the same bytes up to the first hit, so the
   comparison is over read length alone (§7.6). Only VERIFY-THEN-CONTINUE
   reads density, and its default is the FULL feasible interval, which
   assumes nothing. A findings bundle may narrow the interval and is never
   required. This keeps K0 inside Frank's K82 ruling: the expected-cost
   model and its rates stay parked.
3. **The default token must be fixed, never detected.** If the default
   were "the build box's architecture", the emitted program would depend
   on the machine that ran `make`. [XARCH] measured 0 movers over 2,925
   rows across two boxes, and `litscan_k82b.md` §1.3 rejected a build-time
   probe on the same ground. So the default is `portable`, a composite
   token whose answer is one quote block per owned baseline ARM (x86-64-v1
   from ubuntubudu, armv8-a from the Mac). The `kit` row must win on every
   arm (§7.6).

---

## 0. Findings first

1. **SIMD slots into pcrec's tables as rows, but into the RIGHT table,
   and the right table does not exist yet.** The inventory (§1) has nine
   entries that touch scanning, verifying or classifying (T1-T9; T7 is a
   primitive, T8 a group of six machine tables). Today every
   L3 table row fuses WHAT is scanned (one byte, a set, an offset set, a
   pinned run) with HOW the scan is spelled (`memchr`, a table walk, two
   leapfrogged `memchr` streams). Adding SIMD as rows of those tables
   would double them: `dfa_pfs[]` already doubles every form for its
   `-bounded` twin, and a vector twin of each would make it four times
   its WHAT count. The clean slot is a NEW nested table, **the scan-form
   table `SCAN_ROWS`** (§2.2). Every L3 emitter asks it "find the first
   position in `[pos, lim)` whose byte is in S". The vector rows, the SWAR
   rows that D122 addendum 3 admits now, and today's scalar spellings are
   all rows of it. This is compare_stack.md P5's "form chosen at compile
   time", built as a table. The in-loop skips (the stay skip, the scan
   edge's run loop, the VM's span scan) are the same table at other SITES,
   in the D139 shape: one table, sites as bits.

2. **Seven sites do not slot cleanly today, each for a stated reason
   (§2.4):**
   - (a) `ofs_test_emit_fn`'s scan arm is an `if`, not a table.
   - (b) the stay skip has no form selection, and its set bypasses the
     class table that D139 made the scan edge use.
   - (c) the scan edge's LOOP form is a named, unbuilt slot. Axis I picks
     the test, not the loop.
   - (d) `vm_emit_span_scan` has one loop text.
   - (e) two readers classify the prefilter by `strcmp` on row NAMES
     (`emit_dfa.c:6417`, `:6450`). A vector row with a new name would
     silently fall out of G1's elision and out of the re-seed density
     price.
   - (f) `emit_req_set_rest` spells k one-needle passes, with no form
     choice.
   - (g) structural, not a defect: **pcrec does not know the target
     architecture when it emits.** Its output is architecture-neutral C.
     So a pcrec-time predicate can only say "a vector form exists at
     every supported architecture's baseline" or "at the DECLARED level"
     (route A, `--isa`). The per-architecture spelling resolves at gcc
     time, inside preprocessor-selected text. That fact draws the
     boundary in item 3.

     **[rev2]** The structural fact stands. What changes is who reads the
     two values. pcrec no longer has a `BASE`/`DECLARED` predicate. It
     passes an opaque token, and the kit decides whether its kernel text
     is a gcc-time ladder (composite token `portable`) or one spelling (a
     declared token). §7.2.

   Each of (a)-(f) is fixed by implement-then-replace (byte-identical)
   when its first non-scalar row lands, never ahead of it (D77).

3. **The boundary that works is a split (option c), drawn where the
   knowledge changes hands (§3).** The kit owns:
   - the per-ISA PRIMITIVES (load, classify, mask, first/last), as
     injectable text selected by predefined macros;
   - the COMPOSITION generator (descriptor in, C text out). It owns the
     loop skeleton, the short path, unrolling, the classifier per set
     shape per ISA, and the fixed reference functions.

   pcrec owns:
   - SELECTION: its tables, predicates over pattern facts, deny flags and
     stamps;
   - the OPERANDS, from its single sources (P2 cube, P3 run, P6 prior,
     minw/maxw);
   - FUSION, through hooks: the verify text at a hit, the DFA reseed and
     view bounds, the scalar fallback. The fallback is always pcrec's own
     next row, so there is never a second scalar spelling of one search
     (D122).

   The kit's internal tables answer only questions pcrec's tables do not
   ask (§3.4), so the result is two layers of one idiom, not two
   selectors. Option (a), a pure generator, is the same split with the
   primitives inlined into its output. Option (b), a header-only library
   with constant descriptors, is right for the stand-alone product and
   wrong as pcrec's only path. Gcc's constant propagation is not a
   guarantee (studies/simd1 §8), and a header the user must have breaks
   self-containment unless pcrec injects it.

   **[rev2]** RULED (Frank, 2026-10-05): the split stands, with a fourth
   kit layer **K0**, the capability-and-price query. pcrec's SELECTION
   shrinks to one arch-blind row per table. That row compares the kit's
   quoted prices against pcrec's own next row in one unit. The kit now
   also owns everything an ISA name appears in: which kernels exist for a
   token, what they cost, the target attribute and route text, the
   loader marker, and the CPU check. pcrec keeps the operands, the hook
   text and the WHAT/WHERE tables. §7.

4. **"Tailored, not fixed" is the composition model, and the fixed library
   falls out of it (§4).** A kernel is a composition of six primitive
   families, chosen by a first-match table keyed on:
   - set shape (which classifier);
   - span bounds (loop-free, one block, or a loop);
   - run/offset (one filter or a pinned pair);
   - density prior (unroll factor, and whether to iterate hits or restart
     per hit);
   - ISA capability.

   F1, F2, F3, F4, F5, F6, F9 and F13 are that composition at GENERIC
   parameters: a run-time operand, an unbounded span, an unknown density,
   the baseline ISA. The independent reference stays the scalar byte loop
   (N-6), NEVER the generic composition. A specialization checked against
   output of its own generator is a control that shares a source with
   what it controls (learnings.md §3, memory
   `pcrec-check-design-lessons`).

5. **Budgets that bind the design before any row is built (§5 Q14-Q16):**
   - **Deny bits:** 45 of the 64 `pcrec_options.flags` bits are taken
     (k82fix's `-fno-req-set-lead` is bit 45). One bit per vector row
     would exhaust them, so the recommendation is one bit per FAMILY plus
     the ISA level as a value option.
   - **Emitted-size caps (D84):** an un-declared build emits a two-arm
     `#if` ladder per vector site, which adds source bytes.
   - **The `abi` ritual:** any change to the kit's text moves emitted
     bytes, so every kit version bump is a pcrec `abi` event (D76/D94).

   **[rev2]** The deny-bit budget shrinks from four family bits to three
   (§7.9, Q15). The emitted-size cost of a ladder is now inside the
   quote's `code_bytes`, so D84's caps and the dial's size gate see it
   without a pcrec rule (Q16). One new event joins the abi ritual: a
   RECALIBRATION. It moves selections without moving any kit text, and it
   is governed by Q20.

---

## 1. The table inventory

Every first-match table in the tree that selects, or sits directly above,
a scan / verify / classify form. "Walk" names the selection function.
Line numbers are main at 8a41efd2 unless marked k82fix.

### 1.1 The walk itself

`DFA_SELECT` (`src/gen/emit_dfa.c:4943`) over `dfa_select` (`:4931`): the
first entry whose `deny & flags` is clear and whose `applies(const DfaSel *)`
holds. `DfaCand` (`:3315`) is `{name, deny, applies}`, and every object
struct begins with one. `DfaSel` (`:3298`) carries `cx`, the machine `d`,
the `UnanchStart`, `forward` and a per-state `st`. Every list ends with
`cand_always`. clskit.c and runcmp.c spell the same idiom with their own
row structs (a predicate TAG plus an exhaustive `switch`), because their
inputs are a set and a run, not a `DfaSel`.

### 1.2 The tables

| # | table | file:line | selects | rows, in order (deny) | predicates read | each row's emitter emits today |
|---|---|---|---|---|---|---|
| T1 | `dfa_pfs[]`, AXIS B | `emit_dfa.c:6304`; walk `dfa_pf_of` `:6323` | the forward scan's CANDIDATE-START skip: what it scans and how | `run-pinned-bounded`, `run-pinned` (`NO_OFFSET_SKIP`\|`NO_RUN_PREFILTER`); `offset-set-bounded`, `offset-set` (`NO_OFFSET_SKIP`); `memchr-bounded`, `memchr`; `byte-class-bounded`, `byte-class`; `none` | `us->kind` (`DFA_PF_MEMCHR` iff `cand.use_memchr`, decided in `unanch_start` `:4150`); `us->views` (the D11 bound); `ofsk.nsel`; the run pin (`pf_run_applies_common` `:5767`) | `pf_emit_memchr` `:5627`: rest-of-subject libc `memchr`, no verify. `pf_emit_bcls` `:5676`: `while (!can_begin_match[s[pos]]) pos++`. The offset/run rows call the file-scope `<p>_ofsskip` (`pf_block_ofs` `:6038` → `ofs_test_emit_fn` `:6143`), and their scan ARM is an `if`: the leapfrog over two `memchr` streams (`ofs_test_emit_pair` `:6102`) where the scan position is a two-member cube, else one `memchr` at k*. Then the `ofsk_emit_verify` chain (`:5990`), whose run term is the run compare (T7). The `-bounded` twins clamp to n−1 |
| T2 | `req_admits[]` (k82fix) | `lane/k82fix:emit_dfa.c:6638`; walk `req_admit` `:6660` | whether the whole-window PRE-CHECK is emitted, and in which shape | `none`; `one-attempt` (G2); `dominated` (G1); `set-leads` (`NO_REQ_SET_LEAD`); `emitted` | the `req_byte`/`req_run`/`req_set` facts; `req_route_one_attempt`; `dfa_cand_scan` (`:6392`) + `req_byte_dominated_by` (G1's density clause reads `cs->memchr_form`); `pcrec_find_pick` | ADMISSION only. The admitted shape is emitted by `pcrec_emit_req_byte_check` (`:1247`): one `memchr` for a byte; the `<p>_reqrun[_whole]` blocks (the same `ofs_test_emit_fn` as T1) for a run; `set-leads` adds the set pick's `memchr` in front; `emit_req_set_rest` (`:1170`) adds one `memchr` per remaining necessary-set member on the no-DFA-scan route |
| T3 | `dfa_edges[]`, AXIS H | `emit_dfa.c:7237`; walk `dfa_edge_of` `:7332` | per STATE: does it emit an [OPT-5] scan edge at all | `scan-edge` (`NO_SCAN_EDGE`); `table-walk` | the pass's own annotation `scan_span` (`edge_applies` `:7232`) | `emit_scan_edge` `:7407`: a peeled guard, then `while (more && TEST) advance;` (unbounded) or the counted `scan_run_length < span` loop. ONE loop form. Its own comment names the SIMD slot as a LOOP form "selected ahead of the scalar loop", unbuilt |
| T4 | `ROWS`, the class-form table | `src/gen/clskit.c:562`; walk `pcrec_clskit_select` `:693` | how ONE byte's membership is spelled, per set, per `--tune` position, per SITE (`CLSS_VM`, `CLSS_SCAN`) | `byte-range`; `byte-fold` (`CLSD_BYTE_FOLD`); `byte-fold-default` (VM only, held D138 Q1); `byte-kit` (`CLSD_BYTE_KIT`, size positions, only if smaller, D139 item 1); `byte-table`; `size-page3`; `speed-page2`; `speed-bitmap1`; `mid-page3`; `kit` | the set alone (one interval, the ASCII fold pair, byte-ness), model bytes, the call count, the `--tune` position, the site | inline `==c` / `(unsigned)(c-lo)<=span` / `(c\|0x20)==x` (`pcrec_clskit_emit_inline`), a kit matcher call, or a table read (`pcrec_clskit_read`). Readers: `vm_cls_test` (`emit_vm.c:1656`) and the scan edge's `scan_test` (`emit_dfa.c:7386`, axis I, D139 item 2) |
| T5 | `TAB_ROWS` | `clskit.c:754`; walk `pcrec_clskit_select_tables` `:777` | the TABLE representation for the classes T4 sent to a table, per artifact | `atom` (VM, `CLSTD_ATOM`); `scan-table` (scan site); `site` | the count of table-read classes, the atom partition's fit | the shared 256-byte byte→atom table plus a 64-bit mask per class; one 256-byte table per edge; or a 32-byte bitmap per class |
| T6 | `pcrec_runcmp_rows` | `src/gen/runcmp.c:64`; walk `rc_row_of` `:195` | the L2 RUN COMPARE (a verify), both engines | `words` (`NO_RUN_OVERLAP`, masked, L ≥ 2); `overlap` (`NO_RUN_OVERLAP`, exact, L ∈ {3, 5-7, 9-15}); `bytes` (masked fallback); `memcmp` (exact fallback) | the run alone (`rc_holds(pred, r)`: masked or not, its length) | memcpy-loaded word compares (`<p>_w<W>(base+o) & w("K")) == w("T")`, joined by `&&`); per-byte `(b & K) == T`; or `!memcmp(base, "t", L)`, which gcc fuses (one load at L ∈ {1,2,4,8}, a vector compare at L ≥ 16) |
| T7 | `pcrec_find_pick` (a primitive, not a table) | `src/core/findings.c:426` | the OPERAND: which candidate byte or cube is rarest | — (argmin over `cube_mass`; NONE answers by cardinality, k82fix (C)) | the byte-rate (static prior or a `--findings` bundle, D83/D123) | nothing; its readers (`pcrec_find_set_pick`, the run's scan member, `req_set_leads_applies`) feed T1/T2's operands |
| T8 | `dfa_reprs`, `dfa_views`, `dfa_seeds`, `dfa_accs`, `dfa_matches`, `dfa_search_starts` | `emit_dfa.c:5270`, `:5388`, `:5462`, `:5552`, `:6857`, `:7072` | the state token, the position views, the entry seed, the accept probe, the match entry, the search start | — | — | the DFA's representation. **Excluded from SIMD:** none of them scans. Membership IS the transition table (compare_stack.md §5's record) |
| T9 | `vm_ctx_forms[]` | `emit_vm.c:8229` | the VM's `\b`/lookaround context test | six truth-function rows | the node's function | a guarded one-position test through T4. **Excluded:** one or two positions, no scan |

### 1.3 The scan sites that have NO table (each a single emitted form today)

| # | site | file:line | what it is in requirements.md's menu | current form |
|---|---|---|---|---|
| N1 | the stay skip, forward and reverse (axis F's direction methods) | `emit_dfa.c:6627` `dir_fwd_skip`, `:6655` `dir_rev_skip` | F5 / F6 `skip_in_set`, IN-LOOP (D91 budget 2) | `while (pos < n && <p>_<m>_stay<K>[s[pos]]) pos++`. The stay set is a raw 256-byte table and is NOT asked through T4, unlike the scan edge since D139 item 2 |
| N2 | the VM span scan (`vm_cursor_rep`'s two arms) | `emit_vm.c:4613` `vm_emit_span_scan` | F5 at stride 1 (a class run); a stride-k sequence otherwise | `while (cur + stride <= lim && it_ < rmax && TEST) cur += stride`, with TEST being T4's spelling per position |
| N3 | `emit_attempt`'s `(?m)^` skip | `emit_dfa.c:8649` | F1, rest of subject | one libc `memchr('\n')`, candidate = hit + 1. Keeps its own form (compare_stack.md §5), provisionally |
| N4 | `emit_req_set_rest` | `emit_dfa.c:1170` | k × F1 presence tests (no current menu item: "all of S present") | a `for` over a `static const` member list, one `memchr` each |
| N5 | the ofsskip scan ARM | `emit_dfa.c:6143` `ofs_test_emit_fn` | F1 at offset k* plus a verify (F9's shape); F2/F3 for the cube (the K82 pair arm) | an `if`: pair arm (two `memchr` streams), else one `memchr` |
| N6 **RETIRED (D147 add. 12: not a search site)** | `vm_rev_emit`'s backward walk | `emit_vm.c` (compare_stack.md §2.3) | F6 reverse, per byte | a per-byte L1 test with `cur--`. Keeps its own form (compare_stack.md §5) |
| N7 | `$_span_match[_caseless]` | `src/enc/enc_byte.c:153/184` | F8 `mismatch`, a run-time operand | a byte loop returning a prefix count. Gated on a cell (compare_stack.md S6) |
| VMSTART | [START-SET] stage 2's VM hat: the prefilter-less VM attempt loop's entry and retry seek (`docs/design/startset.md` §5; built lane ssbuild2, 2026-10-05, abi 62) | `emit_dfa.c` `pf_vm_emit_first_class`, through `pcrec_emit_find` (T1 PF's own one statement) | F5 over the start set `S`, IN-LOOP per failed attempt (D91 budget 2, UNMEASURED, D149) | `while (pos < n && !<p>_start_set[s[pos]]) pos++` after a 256-entry table; the table form only at stage 2 (Q-R5). **The C17 site manifest (`tests/memfn/site_manifest.tsv`) does not exist at this pin, so the row is recorded here, `pending`, migrating with T1 PF's step** |

---

## 2. Slot-in: where SIMD joins, as rows

### 2.1 The rule this section answers to

A vector form is admissible only as a ROW: `{name, deny, applies,
emitter}`, walked by the table's existing first-match walk, with its name
being what the stamp prints and what `--list-axes` lists. The total
fallback stays last. An ISA fact is a PREDICATE INPUT, never a branch in
an emitter outside the row. That is D122 addendum 2 item 4 ("a SIMD form
later drops in as ONE ROW whose predicate includes the arch capability,
and its deny flag gives it an answer-identity axis for free"), D82, and
memory `pcrec-general-mechanisms-not-special-cases`.

**What "the arch capability" can mean at pcrec time** (finding 2g). pcrec
emits architecture-neutral C, and `Ctx` holds no target. So an ISA
predicate has exactly two readable values:

- `BASE`: a vector form of this composition exists at the baseline of
  EVERY architecture the kit supports (x86-64 SSE2, AArch64 ASIMD). The
  emitted text is then a preprocessor ladder whose `#else` arm is the
  next row's own scalar text (§2.5).
- `DECLARED(L)`: the caller passed `--isa=L` (isa_selection.md §1.2
  route A, designed, not built). The row may then emit only level L's
  spelling, with no ladder.

Route M (a consumer `-march` that raises the predefined macros) needs no
pcrec predicate. The kit's ladder sees the macros at gcc time.

**[rev2] SUPERSEDED.** pcrec reads neither value. The "arch capability"
in D122 addendum 2 item 4's sentence becomes a PRICED kit answer for an
opaque token (§7.2, §7.5). `BASE` is the kit's own behaviour for the
composite token `portable`. `DECLARED(L)` is its behaviour for a declared
token. The rule above still holds word for word: a vector form is
admissible only as a row, the fallback stays last, and no ISA fact
branches an emitter. The difference is that the row's predicate now
reads the kit's prices, not an ISA fact.

### 2.2 The new nested table: `SCAN_ROWS`, the scan-form table (P5's form slot)

**The question it answers.** "Spell the search for the first position `i`
in `[pos, lim)` whose byte is in S (or whose bytes satisfy a pinned
filter), with this handoff at a hit." It does not answer what S is, where
the search runs, or whether it runs at all. Those stay T1/T2/T3's.

**Its sites** (bits, D139's shape): `PF` (the T1 candidate-start skip),
`PRE` (the T2 pre-check's blocks), `OFS` (the ofsskip block's scan arm,
shared by T1's offset/run rows and T2's run blocks, which already share
`ofs_test_emit_fn`), `STAY` (N1), `EDGE` (T3's loop), `VMSPAN` (N2 at
stride 1), and `SETREST` (N4).

**Its input**, a `ScanSpec` (designed):

- **S, as an operand:** one byte; a two-member cube `(K, T)`; a T4
  `ClsChoice` (the set plus its scalar spelling); or a pinned pair (the
  scan byte at k* plus one more filter term at another offset). The
  pinned pair is Study A's and F9's packed pair, with the second position
  chosen by `pcrec_find_pick`.
- polarity: find-in (prefilters) or find-not-in (skips).
- direction.
- **the bound kind:** rest of subject; view-bounded `n − 1` (the D11
  twins); or counted, with `maxw` or the edge's `span`.
- **the site budget:** D91 1, the prefilter, or D91 2, in-loop.
- **the density prior:** `pcrec_find_set_ppm` / `pcrec_dfa_cand_ppm`.
- **the handoff:**
  - RETURN the index (PF, PRE);
  - VERIFY-THEN-CONTINUE, carrying the `ofsk_emit_verify` text with
    `cand` bound (OFS);
  - ADVANCE the cursor variable in place (STAY, EDGE, VMSPAN);
  - ALL-PRESENT (SETREST).
- the prefix placeholder (D143) and the comment tier.

**Its rows (first match).** The order is the design's. Placements marked
OWED are measured placements, not guesses (§6).

| # | row | sites | predicate | deny | emitter |
|---|---|---|---|---|---|
| 1 | `loopfree` | all | the bound is counted and `≤ V`, the kit's short-path width (from `maxw`, a `{0,n}` edge span, or a `W` from [FINDINGS.B4]) AND the kit composes S (§4) | `-fno-vec-scan` | kit K2: the loop-free overlapping-load short path, no loop and no call (RB-4) |
| 2 | `vec-verify` | OFS | the handoff is VERIFY-THEN-CONTINUE AND the kit composes S at `BASE` or `DECLARED` | `-fno-vec-scan` | kit K2 with the on-hit hook: iterate the hit mask's set bits, emit pcrec's verify text for each, and continue the vector loop on failure. That removes k82cost's per-hit re-entry `s`, the "find, verify, restart" cost |
| 3 | `vec` | PF, PRE, SETREST; STAY, EDGE, VMSPAN at `BASE` only unless `DECLARED` (isa_selection.md §2 row 4) | the kit composes S | `-fno-vec-scan` (in-loop sites: `-fno-vec-skip`) | kit K2: the composed scan (§4), with the `#else` arm being the first scalar row below that applies |
| 4 | `libc-memchr` | PF, PRE, OFS, SETREST | S is one byte AND the bound is rest-of-subject. OWED placement against row 3: requirements.md §2.3 row 5 keeps libc on a single rest-of-subject stream unless the Linux `n*` (U-1) says inline matches its long-span `beta` | none (today's default) | today's `memchr(...)` text, byte for byte (`pf_emit_memchr`, the ofsskip memchr arm, the pre-check, N4) |
| 5 | `leapfrog` | OFS, PRE | S is a two-member cube, single-byte scans | none | today's `ofs_test_emit_pair` text |
| 6 | `swar` | all | S is one byte, a cube, or ≤ 3 bytes, with no vector row taken. Portable `uint64_t` SWAR (has-zero-byte), admitted NOW by D122 addendum 3 as an ordinary row (no ISA predicate) | `-fno-swar-scan` | pcrec- or kit-emitted SWAR, P8's subject-end guard (word loads only where `pos + 8 ≤ n`, memcpy loads, a short epilogue) |
| 7 | `table-walk` | PF, STAY, EDGE, VMSPAN | always (the total fallback) | none | today's loop: `can_begin_match` / `stay<K>` / T4's scan test / T4's VM test, byte for byte |

**[rev2] The rows, revision 2.** Rows 1, 2, 3 and 6 above collapse into
ONE arch-blind row. The table becomes:

| # | row | sites | predicate | deny | emitter |
|---|---|---|---|---|---|
| 1 | `kit` | all | `kit_applies` (§7.5): the kit PRICES the query for the token, and its first quote (in the kit's order) whose obligations the site meets DOMINATES the next applicable row's price over the site's proven (span × density) box. It must do so on at least one arm, at the pessimistic end of both spreads. At the size-leaning `--tune` positions the kit's bytes must also not exceed the next row's | `-fno-kit-scan` (budget-1 sites: PF, PRE, OFS, SETREST) / `-fno-kit-loop` (budget-2 sites: STAY, EDGE, VMSPAN). `-fno-kit-native` restricts the quotes to portable-class kernels | `mf_emit` (§7.3) with pcrec's hooks: the verify text, the next row's text as every `#else`, the bound expression, the prefix |
| 2 | `libc-memchr` | PF, PRE, OFS, SETREST | S is one byte AND the bound is rest-of-subject | none | today's text. Price: `LIBC_MEMCHR` (+ `LIBC_RESTART` per hit) |
| 3 | `leapfrog` | OFS, PRE | S is a two-member cube | none | today's `ofs_test_emit_pair`. Price: `LIBC_PAIR` |
| 4 | `table-walk` | PF, STAY, EDGE, VMSPAN | always | none | today's loop. Price: `LOOP_TABLE` or `LOOP_EQ` by T4's spelling |

Revision 1's `loopfree`, `vec-verify`, `vec` and `swar` all survive as KIT
KERNELS. pcrec cannot tell them apart and does not need to. **[rev3]** The
`kit` row's price predicate is withdrawn. Under delegation pcrec keeps
no form ROWS for a delegated site at all: rows 2-4 (`libc-memchr`,
`leapfrog`, `table-walk`) migrate into the kit as its BASELINE arms
(§9), and pcrec's only per-site selection is the profile (§8.5). Row 4's "OWED
placement" against `vec` is gone, because it is a price comparison now.
SWAR's early admission (D122 addendum 3) survives as kernel CLASS: under
the SIMD hold, pcrec's query carries `MF_Q_PORTABLE_ONLY`, a policy flag
that names no architecture (§7.9).

Two notes on the rows (revision 1's numbering):

- **Rows 4, 5 and 7 are today's text.** Promoting the seven sites to ask
  `SCAN_ROWS` moves no byte while rows 1-3 and 6 are denied or absent.
  That is the implement-then-replace step each first non-scalar row
  carries (§6 R4c).
- **Row 6 is the one non-SIMD row.** It is buildable before the SIMD hold
  lifts (D122 addendum 3: "SWAR is fine"). It is also the first honest
  customer of the table, so the table is not built ahead of need (D77). A
  SWAR row needs a measured cell, like any optimization (D119).

**`[rev4.9]`** Under delegation `SCAN_ROWS` is the kit's own form
tables, `arms[]` and `rc_row`, and `[r9 F-1]` `fn_rows[]`, the FUNC-body
table the seam step R4e′.0 creates, all walked by one shared kit walk.
SIMD forms are rows there, beside the scalar arms they displace. Each declares its layer, its ISA level
(`memfn/src/levels.def`) and its own `--memfn=no-<row>` deny (§R4.9.2).
pcrec keeps no form row for a delegated site (rev 3), so none of the
rows above are pcrec's. Revision 1's `vec-verify` is batch 1's `vrun`
rows (§R4.9.7). §2.5's "the fallback is the next row" survives as
§R4.9.2's FLOOR RULE.

### 2.3 Per table: what joins, where, and what its emitter needs

| table | the SIMD (or SWAR) rows that join | position | predicate | deny | what the row's emitter needs | slots cleanly? |
|---|---|---|---|---|---|---|
| T1 `dfa_pfs[]` | **none of its own.** Its rows keep choosing WHAT and WHERE (memchr = one byte, byte-class = the set, offset/run = k-set or pin, and the `-bounded` twins). Each row's emitter asks `SCAN_ROWS` at site `PF` (or `OFS` through the block) for HOW | — | — | — | each emitter builds a `ScanSpec` from what it already holds: `f->cand` (byte or set), `us->views` → the bound kind, `f->ofs` → `OFS` with the verify hook | **yes, once (e) is fixed.** `reseeds` is unchanged: a vector skip over a parked-state set leaves the state parked, the same argument as `byte-class` |
| T2 `req_admits[]` | none (admission is a placement fact; D122 item 2 and P7 keep it the one admission derivation) | — | — | — | — | **yes, with one change:** G1's density clause reads `cs->memchr_form`, which `dfa_cand_scan` sets by `strcmp(pf->c.name, "memchr")` (`:6417`). It must read a property of the SCAN FORM (§2.4 e). The premise "a one-byte scan's per-hit cost" changes under `vec-verify` |
| T3 `dfa_edges[]` | none. Axis H stays "edge or not". The edge's LOOP asks `SCAN_ROWS` at site `EDGE` (the slot its own comment names) | — | — | — | the edge's class set from `scan_choice` (`:7287`), the span (counted or not), the direction's cursor and bound (`f->dir->posv`, `scan_more`), the accept recording, the `ADVANCE` handoff | **no, as built (c)**: the loop text is inline in `emit_scan_edge`. Promote the loop to the table first |
| T4 `ROWS` | **none.** T4 is ONE-POSITION membership and stays scalar. The VECTOR classifier is a different question (16-64 lanes at once) asked of the same set. It belongs to the kit's composition table (§4.3), which T4's set feeds | — | — | — | — | **yes**, as an input. Its `ClsChoice` is the scalar `#else` spelling of a vector row, so one set has one scalar spelling |
| T5 `TAB_ROWS` | none. A vector classifier's constants (nibble tables, range immediates) are the kit's own literals | — | — | — | — | **n/a** |
| T6 `pcrec_runcmp_rows` | **`vec-masked`**: a masked run of L ∈ [16, 2V], one or two overlapping vector loads, `(v & K) == T` as a lane mask, all-ones test | before `words` | masked AND L ≥ 16 AND the kit composes a vector compare at `BASE`/`DECLARED` | `-fno-vec-run` | kit K1's load/and/cmpeq/all-lanes primitives. The caller's P8 guard for L bytes is already emitted | **yes, with a signature change:** `rc_holds(pred, r)` sees only the run. An ISA predicate needs `cx` (`rc_holds(cx, pred, r)`). Exact runs get NO vector row: gcc already lowers constant `memcmp` at L ≥ 16 to a vector compare (D122 addendum: pay for what you use; this record is the reason) |
| T6, **[rev2]** | `vec-masked` is replaced by the arch-blind `kit` row (op VERIFY_RUN, §7.10). Its comparison side is `words`, priced as `ceil(L/8)·CMP_WORD8` | before `words` | `kit_applies` | the site's budget bit | `mf_emit` | **yes**: `rc_holds` still needs `cx`, now for the token and the prices, not for an ISA |
| T7 `pcrec_find_pick` | none (a primitive). The packed-pair operand needs a SECOND pick (the rarest other position, with a distance rule): a new reader, `pcrec_find_pick2`, of the same MASS/PICK kinds | — | — | — | — | **yes** (a reader, not a mechanism; D126 Q4's NONE rule holds inside the primitive) |
| T8, T9 | excluded (§1.2) | — | — | — | — | — |
| N1-N4 | rows of `SCAN_ROWS` at sites `STAY`, `VMSPAN`, `PF`, `SETREST` | — | — | — | as T3's | **no, as built (b), (d), (f)**. N3 stays `libc-memchr` (row 4) with no change |
| N5 | `SCAN_ROWS` site `OFS`: rows 2 (`vec-verify`, which subsumes the K82 pair arm as one fused cube pass, F3), 3, 4, 5, 6 | — | — | — | the verify hook, `maxk`, the guard | **no, as built (a)** |
| N6, N7 | none planned. N6 (RETIRED, D147 add. 12) keeps its own form (compare_stack.md §5). N7's F8 is a run-time operand row of its own when S6's cell exists | — | — | — | — | — |

### 2.4 Where SIMD does NOT slot cleanly, and the fix for each

| # | site | why not | the fix, implement-then-replace, when its first non-scalar row lands |
|---|---|---|---|
| (a) | `ofs_test_emit_fn`'s scan arm (`emit_dfa.c:6143-6185`) | a hard-coded `if (masked scan position) pair-arm else memchr-arm`. The comment explains the ORDER is load-bearing (r2 R2-S2), which is exactly what a row table encodes | the arm becomes `SCAN_ROWS` at site `OFS`. Rows 5 (`leapfrog`) and 4 (`libc-memchr`) are today's two arms, in today's order |
| (b) | the stay skip (`dir_fwd_skip`/`dir_rev_skip`) | no form selection, and the stay set is a raw `stay<K>` table, never asked through T4. That is the same shape D139 item 2 removed from the scan edge ("why can't it use the same structure the table recommends?") | first ask T4 at a scan-type site for the stay set (a D139-shaped cleanup, byte-identical where T4 answers `byte-table`), then ask `SCAN_ROWS` at `STAY`. An unbounded scan edge (`span < 0`) and a stay skip are the SAME loop, "advance while the byte keeps this state", so one site bit may serve both |
| (c) | the scan edge's loop (`emit_scan_edge`) | axis I selects the TEST. The loop is inline text | the loop becomes `SCAN_ROWS` at `EDGE`. The peeled first-iteration guard (the measured t-digits fix) stays the edge's own, around the table's loop |
| (d) | `vm_emit_span_scan` | one text, at any stride | stride 1 asks `SCAN_ROWS` at `VMSPAN`. A stride > 1 keeps its loop (a vector form of a k-periodic sequence is a different composition, unneeded until measured) |
| (e) | `dfa_cand_scan` (`:6417`) and `pcrec_dfa_cand_ppm` (`:6450`) classify T1's selection by `strcmp` on row NAMES | a row added under any other name changes G1's verdict and the re-seed price silently. The same file already holds the better shape: `DfaPf.reseeds` and `run_term` are FIELDS "so a seventh form cannot be added without answering it" | add a `DfaPf` field naming the scan's operand class (`SCAN_BYTE` / `SCAN_SET` / `SCAN_OFS`), and have both readers read it. G1's `memchr_form` premise ("one byte, per-hit restart") becomes a property of the chosen `SCAN_ROWS` row. This fix is owed with the first new T1-adjacent row whatever its kind, SIMD or not |
| (f) | `emit_req_set_rest` (N4) | one form (D82 bound 3: one form gets no table) | a fused ALL-PRESENT kernel (one pass, an OR-accumulated "found" mask per needle, early exit when all are found) is the second form that would earn the site a row. Site `SETREST` |
| (g) | every vector row, structurally | pcrec cannot know the architecture | §2.1 `BASE`/`DECLARED` plus §2.5's ladder. **Not a defect:** it is why the boundary is where §3 puts it |

### 2.5 The scalar fallback inside a ladder is the NEXT ROW

Under `BASE`, a vector row's emitted text is:

```c
#if <PREFIX>_MF_VEC_SSE2 || <PREFIX>_MF_VEC_NEON   /* the kit's capability macros */
    <kit K2 composition for S, at V = 16>
#else
    <the text of the first scalar row of SCAN_ROWS below this one that applies>
#endif
```

The `#else` is NOT the kit's own scalar loop. If it were, an x86 build with
no `__SSE2__` (impossible on x86-64, but the shape holds for an unknown
architecture) would run a second scalar spelling of the same search, which
is D122's one forbidden failure. The kit's own scalar or SWAR forms serve
the kit's stand-alone users and its reference functions. Inside pcrec, the
fallback is pcrec's next row. This requires K2's API to take the fallback
TEXT as a hook (§3.3).

**[rev2]** The ladder's macros, its arms and whether it exists at all are
now the kit's: pcrec passes a token and a kernel per arm (§7.3 `mf_emit`,
a NULL entry meaning "this arm falls back"). The invariant this section
states is kept, and it is now enforced at the API: the only scalar text
inside a kit emission is the `fallback` hook's, which is pcrec's next row.
An arm the kit cannot price is a fallback arm, so a ladder never gains a
scalar spelling of the kit's own.

**[rev3]** The `fallback` hook is withdrawn. After a site's migration
step pcrec has no scalar text to offer, so every `#else` is the kit's own
portable arm, and the invariant (one scalar spelling per search) holds
because the kit holds the only one (§8.3, §9).

### 2.6 Why this is rows, not a parallel mechanism

- **One walk, one idiom:** `SCAN_ROWS` is a `DfaCand` list (or clskit's
  tag-and-switch shape, whichever its inputs fit) walked first-match, total
  fallback last, deny bits in `pcrec_options.flags`, names on `--list-axes`
  ([LIST-TABLES]).
- **One table per question:** WHAT and WHERE (T1/T2/T3), HOW to scan
  (`SCAN_ROWS`), one-position spelling (T4), table storage (T5), verify
  (T6), the vector classifier (the kit's §4.3). No two answer the same
  question. A question asked by two tables would be the parallel mechanism.
- **Answer identity per deny, per architecture:** every vector row is
  speed-only. `make test-axes` with `-fno-vec-scan` and friends must be
  answer-identical on each architecture: the Mac (NEON), the Linux box
  (SSE2; AVX2 under route M), and x86 correctness under Rosetta 2 on the
  Mac (survey.md §1.2 ran SSE4.2/AVX2 there). Arch-specific testing is
  contained by the rows, which is D122 addendum 2 item 4's stated reason.
- **The stamp is the chosen row's name** (D82 rule 2, D46). A new stamp,
  `<PREFIX>_SCAN_FORM` per site class (designed), carries HOW, so the
  existing closed `<PREFIX>_DFA_PREFILTER` value set (WHAT; pcrec-bench's
  adapter enumerates it) does not split. That is the k82fix precedent of
  keeping `<PREFIX>_REQ_WHY`'s four tokens.

**[rev2]** Three of these four points hold unchanged. The changes:

- The answer-identity sweep's per-architecture arms become three deny
  arms per box (`-fno-kit-scan`, `-fno-kit-loop`, `-fno-kit-native`) over
  that box's PRICED tokens, plus option_sets.md §3.5a's compile-only arms
  per token.
- `<PREFIX>_SCAN_FORM` carries the kit's opaque `kernel_id` per arm, and
  it is emitted only where `kit` was selected.
- A new check, C4 (§7.8), keeps the rows arch-blind: no ISA word may
  appear in `src/`, `cli/` or `lib/`.

---

## 3. The boundary: what is the kit's and what is pcrec's

### 3.1 The candidates

The word "kit" means the memory-functions project here, whatever repository
it lives in (Q13).

- **(a) A GENERATOR library.** pcrec calls it at emit time through a C API:
  a descriptor goes in, emitted C text comes out, per ISA. The kit owns
  primitives, composition and spelling. pcrec owns selection and operands.
- **(b) Header-only `always_inline` primitives with CONSTANT descriptors.**
  pcrec's emitted text calls them, for example
  `mf_find_set(s, n, MF_SET_RANGES2('a','z','0','9'))`, and gcc's constant
  propagation does the specialization. The kit is a header. pcrec emits
  calls into it.
- **(c) A split.** The per-ISA primitives are the kit's injectable text, and
  composition is the kit's generator, each in its own layer. pcrec keeps
  selection, operands and FUSION through hooks. The variant the brief names
  ("primitives remote, composition/fusion local") is (c′), with pcrec
  owning composition too.

### 3.2 Evaluation

| criterion | (a) generator | (b) header + constant descriptors | (c) split: K1 primitives + K2 generator in the kit; selection and fusion hooks in pcrec | (c′) primitives remote, composition local |
|---|---|---|---|---|
| **self-contained output** (CLAUDE.md, top) | yes: text is emitted | **only if pcrec INJECTS the header text.** A user `#include` breaks the rule. Injected, it is (a)'s text without (a)'s specialization guarantee | yes. K2's text, plus the K1 subset it uses, is emitted. The runcmp precedent: `<p>_w<W>` helpers are emitted on demand (`pcrec_emit_runcmp_helpers`, `runcmp.c:248`) | yes |
| **D145 licence** | the kit's OUTPUT must carry no notice. The kit needs a generated-output exception of its own (Bison's shape), or a licence in D145's list | the header TEXT is copied into artifacts, so the header itself must be 0BSD / CC0 / Unlicense, or carry an exception | both (a) and (b) apply. Recommend 0BSD for K1 text and the same output exception for K2 (Q14). A memchr translation is Unlicense-derived and clean either way (survey.md §2) | as (c) for K1. Composition is pcrec's own text, already covered by D145 |
| **specialization guarantee** | **guaranteed:** literals are written by the generator (simd1 §8's "fix 1, the plan of record") | **NOT guaranteed.** simd1 §8 measured gcc 15 failing const-prop through a pointer array (half the throughput). Holds only for flat scalar or array descriptors, verified per compiler by objdump (N-8; D82 bound 1) | guaranteed. K2 passes immediates to K1, never a descriptor struct | guaranteed |
| **ISA resolution with no `--isa`** (§2.1) | the generator must emit a `#if` ladder per tier, or pcrec must call it once per tier and wrap the results | **natural:** the header's own `#if __SSE2__ / __ARM_NEON` selects at gcc time | natural. K1 resolves per-ISA spelling by predefined macros at gcc time. K2's composition is ISA-NEUTRAL except where the classifier RANKING differs per ISA (§4.3), and only there does it emit a two-arm ladder | as (c) |
| **testability: exhaustive per primitive** (N-6) | per generated output: possible, over a descriptor population | per primitive: direct, the header is the unit | **per K1 primitive directly, plus per K2 composition** over a descriptor population | per K1. Composition is tested inside pcrec only (answer identity), so it loses the kit's exhaustive length × alignment × position sweep |
| **testability: composition identity vs the reference** | generated vs the scalar byte loop (NOT the generic outputs; finding 4) | constant instantiations vs the scalar loop | as (a). Plus pcrec's answer identity per deny, per architecture (§2.6) | answer identity only. Weaker: the corpus never sweeps alignment or span end |
| **stand-alone value** ("bespoke high-speed memory functions stands on its own") | **high:** a CLI front-end (`memfn-gen 'find any of [a-z0-9_] in span, n ≤ 64'`) emits a tailored header. Nobody has this (survey.md §9 gap 1) | high as a LIBRARY (a better StringZilla: SSE2 tier, fused F2, short path), but a fixed set: the "tailored" half is only as good as const-prop | **highest:** both the library (K1 + reference functions) and the generator (K2 + CLI) | low: the library is a primitives header; the tailoring that is the product's point lives in pcrec |
| **what the bench / oracle can verify** | the oracle: answers only, unchanged (the rows are speed-only). The bench: pcrec cells, with stamps saying which composition ran. The kit needs its own bench (N-7) | same | same, plus the kit's own N-7 bench over its CLI-generated kernels, which is the stand-alone product's evidence | the bench sees pcrec only |
| **churn into pcrec** | every kit release that moves output is a pcrec `abi` event (D76/D94) | every header text change is an `abi` event (injected) | same as (a). Pinned vendor copy (N-10); the bump is deliberate, a ritual and not avoided (memory `pcrec-abi-changes-pre-release`) | primitive changes are `abi` events; composition changes are pcrec's own |
| **fusion with pcrec's verify / reseed / views** | needs hooks: K2 must accept caller text at the hit and the fallback | **hard.** A header function cannot contain the caller's verify unless it takes a callback (an indirect call per hit, or a macro-template, simd1 §8's risk again) | hooks (§3.3) | natural: pcrec writes the loop around primitives |
| **"two implementations of the same search"** (D122) | avoided by §2.5's next-row fallback | **at risk:** the header's scalar fallback is a second scalar spelling inside every artifact | avoided by §2.5 | avoided |

### 3.3 The recommendation: (c), with the hook contract as the uncertain part

**The kit** (one project; its home is Q13):

- **[rev2] K0, the capability-and-price query.** It takes a token and an
  arch-neutral query, and returns a price list: the kernels that exist
  for the token, their measured costs in one unit, their code bytes and
  their site obligations. It also returns the generic reference terms
  pcrec prices its own rows from, and the per-token opaque texts
  (attribute, CPU check, level stamp, loader marker). Its data is the
  calibration tables (§7.7). The full design is §7. **[rev3] Withdrawn by
  D146.** The kit's entry is `mf_emit_site` (§8.2); its measurements are
  internal (§8.6).
- **K1, the primitive layer.** Injectable C text, `static inline
  __attribute__((always_inline))`, every name behind the prefix macro
  (RB-2). It is selected per ISA by predefined macros (RB-3), with every
  wide tier also target-attributed for baseline TUs (RB-10). It has
  capability macros (`MF_VEC_BYTES`, `MF_HAS_LUT16`, `MF_HAS_MOVEMASK`)
  that compositions branch on at gcc time. Its scalar/SWAR fallback is
  for the kit's own users. K1 takes only scalar immediates and pointers,
  never descriptor structs.
- **K2, the composition generator.** A C library with no I/O. Descriptor
  in (§4.1), text out, written against K1's names. It holds the
  composition tables (§4.3-§4.4) as first-match row data with their own
  deny mask, and returns the CHOSEN ROWS' NAMES so a caller can stamp them
  (D46). Its hooks:
  - `on_hit(cand_expr)`: caller text inside the hit iteration;
  - `fallback()`: caller text for the `#else`;
  - `bound`: an expression, not a constant, so pcrec's `lim_` / `n − 1` /
    counted spans pass through;
  - `prefix`: pcrec passes its D143 placeholder `\x01q`, so its
    render-onto-finished-text step names everything.
- **K3, the stand-alone product.** A CLI over K2 that writes a header of
  named, tailored functions from a small spec. The FIXED REFERENCE
  FUNCTIONS (F1-F6, F9, F13 at generic parameters, §4.5) are K3's
  committed output, with direct per-tier names (RB-13) and optional
  out-of-line dispatch (RB-8/A2; legal in the kit's own library, never in
  pcrec's text).
- **The kit's own tests:** N-6 exhaustive per K1 primitive and per K2
  composition over a descriptor population, against the SCALAR BYTE LOOP;
  guard pages; ASan/UBSan; both architectures (Rosetta for x86
  correctness on the Mac, the Linux box for x86 timing). Its N-7 bench.
  N-8 disassembly checks.

**pcrec:**

- the tables (§2): which site gets a vector form, the deny bits, the
  stamps, the `--tune` positions (vector rows are denied at the
  size-leaning positions `-2`/`-1` unless measured smaller, D139 item 1's
  rule);
  **[rev2]** narrowed to ONE arch-blind `kit` row per table. pcrec
  decides WHETHER to ask the kit (the site, its operands, its proven
  facts) and whether the kit's best quote beats pcrec's own next row in
  the common unit. It never decides WHICH kernel or WHICH ISA. The
  `--tune` rule becomes the row's own bytes clause (§7.5);
- **[rev2]** the price FORMULAS of its own scalar rows, over generic
  terms the kit measured (§7.5);
- **[rev2]** the token, held opaque, passed and stamped (§7.2);
- the operands, from the single sources:
  - P2 `pcrec_cls_cube` for cubes;
  - T4's set intervals;
  - P3 for runs and pins;
  - P6 / `pcrec_find_*` for density and the second anchor pick;
  - minw/maxw and the edge span for bounds;
- the hooks' text: `ofsk_emit_verify`, the reseed, view clamps, and the
  next scalar row's text;
- the injection: the K1 subset a K2 output names, emitted once per
  artifact, as runcmp's helpers are;
- the vendored copy: pinned, with PROVENANCE naming the derived artifacts.
  This is the second instance of `third_party/`-derived text reaching an
  artifact, after `utf8_fold_pairs.inc` (third_party/README.md), so the
  README's "almost nothing reaches a generated artifact" sentence gains a
  second row.

**Why (c) and not (a).** They differ in one thing: whether K1 exists as a
separately testable, separately usable layer. Folding it into the generator
loses the kit's library product and its per-primitive exhaustive tests,
and saves nothing, because the generator must still emit the same
primitive text. **Why not (b) as pcrec's path:** specialization is not
guaranteed (simd1 §8), fusion needs callbacks, and the header's scalar
fallback is a second spelling of pcrec's searches. (b) survives as the
kit's LIBRARY face (K1 plus the reference functions), which is where its
stand-alone value is. **Why not (c′):** the composition (unroll, short
path, classifier per set shape) is exactly the "bespoke" knowledge Frank
says stands on its own. Leaving it in pcrec gives the kit nothing to stand
on, and pcrec's composition would be untestable outside answer identity.

**What is honestly uncertain:**

1. **The hook contract is the design's riskiest surface.** Text holes in a
   generator are easy to write and easy to misuse: hygiene of the names
   the hook text may reference, and a hook that reads past the guard the
   composition established. P8's subject-end rule must hold across the
   hole. The first build (§6 R4c) is sized to find out on ONE site (OFS's
   verify hook) before a second customer.
2. **Whether ISA-neutral composition holds for F4/F5.** The classifier
   RANKING differs by ISA (NEON `tbl` at baseline; x86 SSE2 has no
   `pshufb`), so K2 emits a ladder for the classifier only. If unroll or
   short-path choices also differ by ISA (U-8: AVX2's wider vector raises
   the short-path threshold), more of the composition becomes per-tier
   text, and (c) drifts toward (a)'s N-tier output. The size cost of that
   is unmeasured (§5 Q16).
   **[rev2]** This is now the KIT's uncertainty and is priced: a ladder
   or per-tier text shows up as `code_bytes` in the quote (§7.4), and
   linux_results.md Q16 (an AVX2 row keeps the SSE2 16-B tier) is a
   kit-internal composition rule.
3. **gcc-time capability macros are not pcrec-observable.** A stamp cannot
   say which arm compiled unless the artifact computes it from the same
   macros (`isa_selection.md`'s `<PREFIX>_ISA_LEVEL`, RB-12). The stamp
   then names the ROW. The ARM is a preprocessor fact the caller reads
   from the level macro. D46 is satisfied for selection. FORCING an arm is
   the consumer's `-m` flags (route M), not a pcrec flag.
4. **A second repository's churn pre-1.0.** Two-repo coordination costs
   more than it saves until K1's API settles. That is why Q13 recommends
   building the kit in-tree first, as a zero-dependency subtree like
   `analyze/`, and extracting it at its own 0.1.

### 3.4 Why the kit's tables are not a second selector

pcrec's tables ask questions only pcrec can answer:

- is this site worth a vector form at all;
- what is S, from which analysis;
- which budget, which bound, which handoff.

The kit's tables ask questions only a set and an ISA can answer:

- which classifier spells S;
- how many vectors per iteration at this density hint;
- loop-free or loop at this bound.

The rule that keeps them apart is written into the API: K2 receives
FACTS, never site names, and returns a composition or NONE. pcrec never
names a classifier. If pcrec ever wanted to override a classifier, the
override would be a K2 deny bit passed through, never a pcrec-side
re-derivation. **[rev2]** K0 makes this rule two-way. The kit receives
facts and never site names. pcrec receives prices and kernel IDs, and
never ISA names. The override path is `--kit-deny=` and `--kit-force=`,
both opaque pass-throughs. clskit is the in-tree precedent: `TAB_ROWS` (artifact-level)
and `ROWS` (per-set) are nested first-match tables answering different
questions, and the scan edge's axis I asks `ROWS` rather than holding a
mapping of its own (D139 item 2).

**One duplication risk this boundary creates, named with its control.**
The kit must analyse a set's SHAPE for its own users: is it one cube, how
many ranges, are its nibble buckets distinct. pcrec already owns P2
(`pcrec_cube_of`, `src/core/cpset.c`). Two derivations of "is this set one
cube" is compare_stack.md D2's class exactly. The control is an agreement
check, D2's prescribed one: the 256-point exact membership check, run over
every class the corpus produces, K2's verdict against `pcrec_cls_cube`'s.
In pcrec's calls, K2 additionally RECEIVES the cube as a hint, and must
refuse a hint its own analysis contradicts (a loud internal error, never
a silent preference).

---

## 4. The composition model

### 4.1 The descriptor (what K2 receives)

```c
typedef struct {
    /* the operand S */
    int            kind;        /* MF_S_BYTE, MF_S_CUBE, MF_S_SET, MF_S_PAIR */
    unsigned char  byte, K, T;  /* MF_S_BYTE / MF_S_CUBE */
    const uint64_t *set;        /* MF_S_SET: 256-bit membership; intervals beside it */
    int            j1, j2;      /* MF_S_PAIR: two offsets (scan, filter), j2 - j1 = d */
    unsigned char  b1, b2;      /*   and their bytes (or cubes) */
    int            negate;      /* skip (find first NOT in S) */
    int            reverse;
    /* the span */
    long           maxw;        /* -1 unbounded; else a proven bound on n */
    const char    *bound_expr;  /* the caller's bound, text */
    /* the priors */
    unsigned       density_ppm; /* expected hits per million bytes (P6/MASS); 0 = unknown */
    unsigned       run_p99;     /* skip: p99 run length if a findings value exists; 0 = unknown */
    /* the ISA */
    int            isa;         /* MF_ISA_BASE (ladder over every arch's baseline) or a declared level */
    unsigned       deny;        /* the caller's K2 row denies */
    /* hooks */
    void (*on_hit)(void *u, StrBuf *c, const char *cand_expr);   /* NULL: return the index */
    void (*fallback)(void *u, StrBuf *c);                        /* the #else arm's text */
    void *u;
} MfScanDesc;
```

(A sketch. The real API's shape is R4b's to fix. `StrBuf` would be the
kit's own sink type, not pcrec's.)

**[rev2]** Superseded by §7.3. K0's `mf_query` is this descriptor, made
arch-neutral:

- `isa` leaves the struct and becomes the token argument;
- `density_ppm` becomes an interval;
- `maxw` becomes a proven `[span_lo, span_hi]`;
- `run_p99` is dropped until a findings value exists to fill it (D77);
- the hooks move to `mf_hooks`, which K2 receives together with the
  kernel pcrec chose per arm. The price question and the generation call
  share one query, so K2 generates exactly what K0 priced.

### 4.2 The primitive set (K1)

| family | primitives | per-ISA notes (from survey.md §7) |
|---|---|---|
| **P-L load and safe tail** | `vload(p)` (unaligned, memcpy-based); `vload_last(s, n)` (the block ending exactly at `s + n`, overlapped); the sub-vector loads for `n < V`: two overlapping 8-byte words for 8..15, two 4-byte for 4..7, probes for 1..3 (RB-4); never a read outside `s[0..n)` (S-2; no aligned-down over-read, survey.md §0 item 4) | SSE2 `_mm_loadu_si128`; NEON `vld1q_u8`; SWAR `uint64_t` memcpy |
| **P-C classifiers** (a block in, a lane mask vector out) | `eq1(b)`; `eqN(b1..bk)` (OR-chain, k ≤ 3 by default); `cube(K, T)` (`(x & K) == T`, which covers every ASCII case pair at K = 0xDF); `rangeR(lo1, hi1, …)` (R ≤ 4: SSE2 `paddb` + signed `pcmpgtb`, PCRE2's idiom; NEON `vcleq` after a subtract); `lut16(lo_tbl, hi_tbl)` (nibble shufti: NEON `tbl` baseline, x86 SSSE3+ `pshufb`); `bitset32(tbl)` (NEON two `tbl` + `vtst`; x86 truffle at SSSE3+); `not(m)`; `and(m1, m2)` / `or(m1, m2)` (the pinned pair: `cls1(vload(p + j1)) & cls2(vload(p + j2))`, Study A) | the RANKING differs by ISA. That is the one place a composition holds a ladder (§4.3) |
| **P-M mask → position** | `any(m)` (NEON `umaxp` lane 0; x86 `movemask != 0`); `first(m)` (x86 `ctz(movemask)`; NEON `shrn #4` + `ctz >> 2`); `last(m)` (the `clz` forms, for F6); `count(m)` (popcount, F13); `next(m)` (clear lowest: bit iteration for VERIFY-THEN-CONTINUE) | `shrn #4` is settled practice (survey.md §9 item 8) |
| **P-S skeletons** | forward / reverse; the overlapped first block, an aligned middle, the overlapped last block (memchr's shape, no scalar head or tail at n ≥ V); unroll ×U with one OR-reduce per U vectors (RB-7); a size-tiered entry (`n < V` short path, `V ≤ n < U·V` single-vector loop, else unrolled: studies/simd1 §13's haystack tiering per call) | ISA-neutral, written over P-L/P-C/P-M |
| **P-SP loop-free short path** | for a PROVEN bound `maxw ≤ V`: no loop, no call. One or two overlapping loads, classify, mask, first. For a counted run (the scan edge's span): the mask clipped at the bound | the D91 corollary made vector-shaped; requirements.md §0 item 3 measured the scalar byte loop losing from 2-4 B |
| **P-F fusion and handoff** | RETURN (index or `n`); VERIFY-THEN-CONTINUE (for each set bit in hit order: run the `on_hit` text; on its success return `cand`; on all failing continue the vector loop: no re-entry and no rescan); ADVANCE (the cursor variable written in place: skip forms); ALL-PRESENT (OR-accumulate a per-needle "seen" bitmask across blocks, exit when full: N4); COUNT | the hooks are the boundary (§3.3). P8 holds: the hook text sees only `cand` with `cand + maxk < n` already established by the skeleton |

### 4.3 The composition tables (K2's, first match)

**C1, the CLASSIFIER table** (keyed on set shape × ISA capability). The
first applicable row whose capability holds on the arch wins. Under
`MF_ISA_BASE` the composition emits `#if <cap>` / `#else` (next row) only
where the arches' first rows differ.

| # | row | applies | capability | notes |
|---|---|---|---|---|
| 1 | `eq1` | S is one byte | any vector | the F1 shape |
| 2 | `cube` | S is one cube `(K, T)` with ≤ 4 members (a case pair; `[0-3]`-like) | any vector | one AND + one compare: F3; the K82 pair arm in ONE pass |
| 3 | `eqN` | 2 ≤ \|S\| ≤ 3, not one cube | any vector | F2's fused `Two`/`Three` |
| 4 | `range` | S is ≤ R intervals (R = 4 at SSE2 and NEON baseline; PCRE2's `X86_START_BITS_MAX_RANGES`) | any vector | the SSE2-baseline set form (survey.md §9 gap 2) |
| 5 | `lut16` | S ⊆ ASCII, ≤ 8 nibble buckets (shufti) | `MF_HAS_LUT16` (NEON base; x86 SSSE3+) | where x86 SSE2 and NEON first DIFFER: the ladder site |
| 6 | `bitset32` | any S | `MF_HAS_LUT16` | StringZilla's NEON form; truffle on x86 SSSE3+ |
| 7 | NONE | otherwise | — | K2 declines; pcrec's row predicate fails; the scalar row runs (no vector form exists for S on this tier) |

**C2, the SHAPE table** (keyed on span bound × density × handoff × ISA
width V):

| # | row | applies | composition |
|---|---|---|---|
| 1 | `short` | `0 ≤ maxw ≤ V` | P-SP: loop-free |
| 2 | `one-block` | `V < maxw ≤ 2V` | first block + overlapped last block, no loop |
| 3 | `iterate` | handoff is VERIFY-THEN-CONTINUE AND `density_ppm` is HIGH (≥ about one hit per V bytes; the threshold is owed, §6) | ×1 loop, bit-iterate every hit (dense: unrolling only delays the first hit) |
| 4 | `skip-width` | `negate` (a skip) AND `run_p99` known | a vector width whose window covers p99 of runs (simd1 §15's measured rule: predictability first). ×1, no unroll |
| 5 | `unrolled` | `density_ppm` LOW or unknown AND `maxw` unbounded or > 4V | the size-tiered entry: short / ×1 / ×4 OR-reduce (RB-7: matches libc's long-span `beta`) |
| 6 | `loop` | always | ×1 loop with the overlapped last block |

Every C1/C2 row has a K2 deny bit, and K2 reports `C1-row/C2-row` names
(for example `cube/unrolled`) for pcrec's `<PREFIX>_SCAN_FORM` stamp.

### 4.4 What "tailored" buys, case by case (the answer to Frank's earlier question)

| need (a pcrec site) | the fixed-library answer | the tailored composition | why it wins (measured or cited) |
|---|---|---|---|
| K82 pair arm, `(?i)` scan member | two `memchr` streams, leapfrogged (two calls, two passes, overshoot) | `cube` × `iterate`/`unrolled` with the run verify as `on_hit` | requirements.md §0 item 2: fused 0.96-1.46 ns against 3.27 ns at n ≤ 16; 1.6-1.8× at 4 KiB; no per-hit re-entry |
| `(?i)union…` byte-class prefilter over `{u, U}` | a 256-byte table walk, one load per byte | `cube` (K = 0xDF) × `unrolled` | survey.md §0 item 3: NEON `tbl` bitset 6.7-7.6× a table loop; a cube is cheaper still |
| scan edge `[a-z]{0,8}` | a byte loop with the T4 test per byte | `range` × `short` (maxw 8 ≤ V): one load, one classify, `first(not(m))`, clipped at 8 | requirements.md §0 item 3: a short span's form is loop-free |
| VM `[a-z.]+` before `@` (a class run) | the stride-1 span loop | `range`/`lut16` × `skip-width` | simd1 §15: classify + clz, 2-3× over a scalar table loop on mixed run lengths |
| REQ_RUN `/user` in a 1 MiB subject | `memchr('/')` + `memcmp` per hit, restarting | `pair` (the two rarest positions by `pcrec_find_pick2`) × `iterate`, with the run compare as `on_hit` | Study A (simd1 §12): pinned rare-position filters, adopted. The ofsskip and pre-check share one block, so one composition serves both |
| N4: three set members all present | three `memchr` passes | `eqN` × ALL-PRESENT, one pass | requirements.md §2.2 item 2 (k streams cost k F's and k passes) |

### 4.5 The fixed library as the generic-parameter outputs

The kit's reference functions are K2 at generic parameters: S a run-time
operand (no constant folding of needles, so K1 takes a broadcast register),
`maxw = -1`, `density_ppm = 0`, `isa = BASE`, `on_hit = NULL`.

| function | the composition |
|---|---|
| F1 `find_byte` | `eq1` × `unrolled`, RETURN |
| F2 `find_any2/3` | `eqN` × `unrolled`, RETURN |
| F3 `find_cube` | `cube` × `unrolled`, RETURN |
| F4 `find_in_set` | C1 rows 4-6 (a run-time set: `bitset32` on NEON; on SSE2 the scalar bitmap: C1 row 7 is honest here) × `unrolled` |
| F5 `skip_in_set` | F4 with `negate` |
| F6 `rfind_byte`, `rskip_in_set` | F1/F5 with `reverse`, P-M `last` |
| F9 `find_literal`, anchored | `pair` × `iterate`, with the kit's own literal compare as `on_hit` |
| F13 `count_byte` | `eq1` × COUNT (aligned 4× loop, scalar tail, never overlapped: an overlap double-counts) |
| F7 run compare | not a scan: K1's vector compare (T6's `vec-masked` row) |
| F8 `mismatch` | a two-operand variant (`cmpeq(a, b)` negated, `first`); a C1 row over two streams, not built until S6's cell |
| F10 Teddy, F11 UTF-8, F12 find-all | not compositions of this model; their own kernels (survey.md §8) |

**The reference for testing is never this table.** A specialization (say
`cube/short` at maxw 8) is checked against the scalar byte loop, which
shares no source with K2. Checking it against F3 (`cube/unrolled`, the
same generator) would let a K2 defect in `cube` pass both
(learnings.md §3). The generic outputs are the PRODUCT, not the control.

---

## 5. Questions for Frank

**[rev3]** The open questions are now §13 (Q24-Q34); §13.1 maps every
question below to its rev 3 status.

Numbering continues from isa_evaluation.md's Q7-Q11.

12. **Q12, the boundary.** Should §3.3's split be the design of record?
    - The kit owns K1 (per-ISA primitives, injectable text), K2 (the
      composition generator, with its own first-match tables and hooks)
      and K3 (the CLI and fixed reference functions).
    - pcrec owns selection (its tables, plus the new `SCAN_ROWS`),
      operands, fusion text and injection.

    **Recommendation:** yes. It is the only option under which the kit
    stands on its own as BOTH a library and a "bespoke functions"
    generator, pcrec's output stays self-contained and specialized, and
    no search gets a second scalar spelling.

    **[rev2] RULED (Frank, 2026-10-05): yes, with K0.** The kit owns
    K0-K3. pcrec owns selection through ONE arch-blind row per table,
    plus operands, hook text, its own rows' price formulas and the opaque
    token. Linux confirmed the K2 premise (linux_results.md §6.3: T-C's
    descriptor kernel is the hand kernel on x86 under gcc and clang).
    **Recommendation for what remains:** adopt §7 as the design of record
    for K0.
13. **Q13, where the kit lives first.** **Recommendation:** in-tree, as a
    zero-dependency top-level subtree (`memfn/`, on `analyze/`'s
    precedent: it links nothing from `src/`, and `src/` reads it only
    through its public header and API). Extract it to its own repository
    at its 0.1, when K1's API has a second consumer. That respects "don't
    get too caught up with separate project" and keeps the scope mandate
    unextended until then. pcrec's emitter then reads the in-tree copy.
    After extraction it reads a pinned vendor copy under `third_party/`,
    with PROVENANCE naming the derived artifacts.

    **[rev2]** Unchanged, plus the calibration data: `memfn/cal/` in-tree
    (§7.7). After extraction, the vendored copy carries `prices.inc` and
    each arm's PROVENANCE.md. A recalibration then arrives as a vendor
    bump (Q20).
14. **Q14, the kit's licence.** **Recommendation:** K1's injectable text
    under 0BSD, and K2/K3 under MIT with D145's generated-output exception
    (or all of it 0BSD). Either way its text and its output reach users'
    artifacts with no notice, under D145's list. A translated memchr is
    Unlicense-derived and compatible with both.

    **[rev2]** Unchanged. The calibration data never reaches an artifact.
    Only the chosen kernel's text and its opaque `kernel_id` stamp do. So
    the data takes the kit's own licence and needs no output exception.
15. **Q15, the deny-bit budget.** 45 of 64 bits are taken. **Recommendation:**
    - one pcrec bit per FAMILY: `-fno-vec-scan` (`SCAN_ROWS` rows 1-3 at
      PF/PRE/OFS/SETREST), `-fno-vec-skip` (the same rows at the in-loop
      sites, so D91's budget 2 has its own kill switch), `-fno-vec-run`
      (T6's `vec-masked`) and `-fno-swar-scan` (row 6): four bits;
    - K2's internal rows (C1/C2) denied through ONE value option
      (`--memfn-deny=cube,unrolled,…`), not flag bits;
    - the ISA level as the value option `--isa=L` (route A; already
      designed, isa_selection.md Q4).

    D144 item 4 ("every optimization its own deny") is met at the
    granularity the batch-gate triage uses: a family flips, then the
    value option bisects within it.

    **[rev2] Revised: three bits, named for budgets and kernel class,
    never for an ISA.**
    - `-fno-kit-scan` covers the `kit` row at budget-1 sites (PF, PRE,
      OFS, SETREST, and T6 where it verifies for a prefilter).
    - `-fno-kit-loop` covers the `kit` row at budget-2 sites (STAY, EDGE,
      VMSPAN, and T6 inside the match).
    - `-fno-kit-native` limits quotes to portable-class kernels. That is
      SWAR's D122 addendum 3 line and the bench's SIMD-off testee.

    The first two are three-valued (deny/auto/force, option_sets.md
    §2.4a), which gives D46's forceable half. `--kit-deny=` (rev 1's
    `--memfn-deny=`) and `--kit-force=` pass kernel IDs through unparsed.
    `--isa=TOKEN` is the one value axis. Bits used: 46 of 64 at this pin
    (0-45), with k82hand's design taking 46. **Recommendation:** the three
    bits.
> **`[rev4.4]`** Q15's `--memfn-deny=` / `--kit-deny=` spellings are
> history. The kit's per-form denies are `--memfn=no-NAME`, rows of the
> kit's own registry (§R4.4.1), and spend no pcrec flag bit.

16. **Q16, ladders in un-declared builds.** Without `--isa`, a vector row
    emits a two-arm `#if` (vector / pcrec's next scalar row). That adds
    source bytes under D84's caps and the dial's size term. **Recommendation:**
    accept it. The ladder covers only the classifier (C1 row 5's NEON/x86
    split) and the outer vector-or-scalar choice, not whole loops.
    Measure the added bytes over the corpus at R4c (the emitted-size log
    already exists, `[ART-SIZE.1b]`), and make "vector rows only under a
    declared `--isa`" a row predicate if the cost proves material. The
    rows absorb either answer.

    **[rev2] Dissolved.** A ladder's bytes are in the quote's exact
    `code_bytes` (§7.4). So D84's caps, the dial's size-leaning positions
    (the row's bytes clause, §7.5) and the size log all see them with no
    pcrec rule and no `--isa`-only predicate. Linux's one finding for
    this question (an AVX2 row must keep the SSE2 16-B tier, else 8-16 ns
    against 2-4 ns at 16 B) is a K2 composition rule, and it shows up in
    the AVX2 quote's own price. **Recommendation:** close Q16. The
    corpus-bytes measurement at R4c stays, as a census.
17. **Q17, promoting the seven non-table sites (§2.4).** **Recommendation:**
    each site is promoted to ask `SCAN_ROWS` only when its first
    non-scalar row lands, byte-identically (implement-then-replace), never
    as a standalone refactor (D77). Two exceptions, owed now regardless of
    SIMD:
    - §2.4(e), the `strcmp` name readers, is a latent defect against ANY
      new T1 row. Recommend it rides the next T1 change of any kind.
    - §2.4(b)'s first half, the stay set through T4, is D139's own
      argument one site over. Recommend filing it as a `[CLS-TREE]`
      follow-up row.

    **[rev2]** Unchanged. One addition: §2.4(e)'s fix should read the
    chosen `SCAN_ROWS` row's price CLASS (does a hit restart a call?),
    not its name. The `kit` row's per-hit price makes that class a
    property of the quote.

18. **[rev2] Q18, the default token.** Should the default be `portable`,
    fixed, never detected from the build box? Its answer is one quote
    block per owned baseline arm (x86-64-v1, armv8-a), and the kit text
    is a ladder whose `#else` is pcrec's next row. **Recommendation:**
    yes. Detection would make the emitted program depend on the machine
    that ran `make`. [XARCH] measured 0 movers over 2,925 rows on two
    boxes, and `litscan_k82b.md` §1.3 already declined build-time
    calibration on the same ground.
19. **[rev2] Q19, the Mac as the armv8-a calibration box.** D144
    addendum 1 calls Mac timings directional. **Recommendation:** admit
    the Mac as armv8-a's calibration box, under three conditions:
    - calibration's own protocol: N ≥ 5 loops of ≥ 50 ms, min and
      median, the harness's loop subtracted, in a quiet window;
    - pcrec reads only the pessimistic ends of the spreads (kit median
      against reference min), so noise makes the row decline, never
      wrongly select;
    - C7's ratio-invariance check passes on that arm.

    The verdict-making timings of D144 addendum 1 stay Linux-only. A
    calibration is not a verdict: C3 on the Mac would be. Without this
    ruling, armv8-a is UNPRICED and `portable` prices its x86 arm alone.
20. **[rev2] Q20, recalibration governance.** A new calibration run
    moves no kit text and no layout, so it is not an `abi` event. It can
    still move selections. **Recommendation:** a recalibration lands as
    one change containing:
    - the raw transcript;
    - the regenerated `prices.tsv`/`prices.inc` (`generate.py --check`
      green);
    - a SELECTION-DIFF census: every corpus and bench site whose chosen
      row or kernel moves, by ID (the movers-by-ID discipline every
      recent abi landing used);
    - C3 on the movers.

    It is accepted like an alpha (D144). Prices are never hand-edited.
    D103's ruled-diff governance does not apply: it governs a pinned
    policy table, and these are measurements.
21. **[rev2] Q21, the route folded into the token.** **Recommendation:**
    yes, and withdraw the designed `--isa-route` axis. The kit's token
    grammar spells both routes (`x86-64-v3` for route A, `x86-64-v3+cc`
    for route M with the `#error` floor; the spelling is the kit's). This
    removes option_sets.md constraint row 6 with it.
22. **[rev2] Q22, whose libc prices pcrec's libc rows.** `LIBC_*` is the
    calibration box's libc (glibc 2.43 for x86 arms; libSystem for
    armv8-a). A consumer on musl inherits decisions priced on glibc.
    **Recommendation:** accept and document it in `docs/spec/` at R4c. A
    platform-qualified token (`x86-64-v1/musl`) is the general form, to be
    built only for a measured customer (D77).
23. **[rev2] Q23, K0 against the K82 ruling.** Frank parked K82's
    expected-cost model for simplicity. K0 is also a cost comparison, but
    it needs no rates: no call span W, no density prior and no bundle.
    It needs only proven bounds and measured machine terms. The dominance
    rule reads the sign over the whole box, so it can only decline where
    a modelled expectation might have admitted. **Recommendation:** K0
    never requires a findings bundle. A bundle may only NARROW the
    density interval. If K82's model is ever unparked, its `ps` terms
    read `mf_ref` instead of adding `limits.def` rows, so the house
    keeps one calibration source.

---

## 6. Plan-row text for the manager (`[MEMFN]` R1d → R4)

**[rev3]** Both build orders below are superseded by §12.2 (R4a-R4j),
whose plan-row text replaces them.

Paste under `[MEMFN]`. Each step carries its D77 trigger. Steps that touch
pcrec's emission open only under `[OPT-SIMD]`'s sequencing (SIMD last,
D119/D91; `[rev4.9]` superseded: SIMD is a parallel path, D147 add. 11), except the SWAR row (D122 addendum 3).

> **R1d DELIVERED 2026-10-04 (lane memfnmap): `docs/design/memfn/integration.md`** — the integration map. Nine inventory entries (T1-T9) plus seven table-less scan sites (N1-N7); SIMD joins as rows of ONE new nested scan-form table `SCAN_ROWS` (sites PF/PRE/OFS/STAY/EDGE/VMSPAN/SETREST, D139's shape) rather than as vector twins of every `dfa_pfs[]` row; T6 runcmp gains one `vec-masked` row; T4 ROWS stays scalar and feeds the kit's classifier table. Seven sites do not slot cleanly as built (the ofsskip scan arm's `if`, the stay skip, the scan-edge loop, the VM span scan, two `strcmp`-on-row-name readers, N4's k-memchr loop, and pcrec's architecture-blindness at emit time), each with its implement-then-replace fix. Boundary = (c): kit K1 per-ISA primitives (injectable text) + K2 composition generator (descriptor in, text out, hooks for pcrec's verify and fallback) + K3 CLI/reference functions; pcrec keeps selection, operands, fusion text, injection. Q12-Q17 open to Frank.
> - **R3** (findings to Frank, rulings Q1-Q17): trigger = this delivery. Owed beside it: `probes/linux_run.sh` (U-1, U-8..U-12), the survey's Linux timing.
> - **R4a, kit K1 + reference functions, in-tree `memfn/` (per Q13):** P-L, P-C (`eq1`, `eqN`, `cube`, `range`), P-M and P-S for SSE2 + NEON + scalar/SWAR; F1/F2/F3/F5/F6 as committed K3 output; N-6 exhaustive + guard pages + ASan/UBSan on both architectures (Rosetta for x86 correctness on the Mac); the N-7 bench. **Trigger:** Frank's R3 ruling (the kit stands on its own, so its own trigger is the charter; no pcrec cell is needed for code that changes no emitted byte).
> - **R4b, K2 composition generator + K3 CLI:** C1/C2 tables with deny and row names; the four hooks; the descriptor; the agreement check of K2's cube analysis against `pcrec_cls_cube` (the 256-point exact check, every corpus class). **Trigger:** R4a green on both architectures, plus a named first pcrec customer (R4c).
> - **R4c, the first pcrec row, at site OFS:** promote `ofs_test_emit_fn`'s scan arm to `SCAN_ROWS` (rows 4/5 = today's text, byte-identical, the identity gate), then add `vec-verify` (`cube` × `iterate`/`unrolled`, the run verify as `on_hit`) under `-fno-vec-scan`. Fix §2.4(e) in the same change. abi bump, `docs/spec/` hunk, `<PREFIX>_SCAN_FORM` stamp, sabotage rows (vector row reached; hook guard; fallback arm). **Trigger:** `[OPT-SIMD]` opened (D119 sequencing) AND the K82 pair-arm cells measured on Linux above the D144 addendum-1 noise floor AND U-1's fused-vs-two-call margin holding on x86.
> - **R4c′, the SWAR row (`SCAN_ROWS` row 6), may precede R4c:** a portable SWAR `eq1`/`cube` scan at PF/OFS, admitted now by D122 addendum 3. **Trigger:** a measured cell whose time is in a one-byte or cube scan with short spans (the bench's per-call 6-11 B cells, k82diag §2), alpha-accepted per D144.
> - **R4d, `vec` at site PF (the byte-class prefilter):** C1 rows 2-6 over `can_begin_match`'s set; promote `pf_emit_bcls[_bounded]` to `SCAN_ROWS` first. **Trigger:** the bench class-shape census (U-2, relayed to pcrecdev2) AND a Linux cell whose time is in `pf_emit_bcls` (the WAF `byte-class` cells, compare_stack.md §6.3).
> - **R4e, in-loop skips (sites STAY, EDGE, VMSPAN):** promote the three loops (§2.4 b-d), then `vec`/`loopfree` at `BASE` only (isa_selection.md §2 row 4). **Trigger:** U-3 (an in-loop dispatch probe at a real emitted site, D91 budget 2 re-measured, never inherited) AND a Linux cell dominated by class runs (simd1 §15's shape; `t-digits`-type cells).
> - **R4f, T6 `vec-masked`:** **Trigger:** a census of masked runs with L ≥ 16 at verify sites, plus a cell.
> - **R4g, declared-ISA rows (`DECLARED(L)`):** wide tiers at prefilter sites. **Trigger:** isa_evaluation.md §3.3 L-1/L-2 (a measured level gain on ubuntubudu) and Q4's ruling.
> - **Filed, not scheduled:** the stay set through T4 (a `[CLS-TREE]` follow-up, §2.4 b, D139's argument); N4 ALL-PRESENT (trigger: a cell on the K65 no-DFA-scan route whose time is in `emit_req_set_rest`).


**[rev2] The build order, revision 2.** It replaces R4a-R4g above. The
triggers carry over unless stated. The K0 layer adds two steps (R4a′, and
the stub half of R4c). It turns revision 1's per-family pcrec rows into one
row per table.

> **R1d REVISION 2 DELIVERED 2026-10-05 (lane memfnk0): `docs/design/memfn/integration.md` rev 2** — Frank's Q12 ruling (boundary (c) plus K0) designed out. The kit gains K0, a CAPABILITY-AND-PRICE QUERY (§7): pcrec holds an OPAQUE token (`--isa`, default `portable`, fixed and never detected), asks an arch-neutral query, and gets a price list back (piecewise-affine ps costs with measured spreads, exact code bytes, arch-neutral site needs). pcrec's tables get ONE arch-blind row, `kit`, chosen iff a kit quote DOMINATES the next row's price over the site's proven span × density box on some arm. pcrec prices its own rows from kit-measured generic terms. Calibration is data in `memfn/cal/<arm>/` (raw transcript → `generate.py` → `prices.tsv`), owned per box; x86-64-v4/SVE/SVE2 are UNPRICED. Removes revision 1's four vector rows, `BASE`/`DECLARED`, `V`, the pcrec-side ladder, [OPT-SETS]'s `isa` poset/`isa-route`/constraint rows 6-8 and three of the `vector` family's four bits. Adds three deny bits (`-fno-kit-scan`/`-loop`/`-native`) and the arch-blindness detector C4. Q12 ruled; Q13-Q17 updated; Q18-Q23 new.
> - **R3** (rulings): Q13-Q23. Owed beside it: nothing new on Linux. linux_results.md already answers U-1/U-8..U-12/L-2/L-4/T-C.
> - **R4a, kit K1 + reference functions, in-tree `memfn/`** (unchanged from revision 1, plus the SWAR primitives as a PORTABLE kernel class). **Trigger:** Frank's R3 ruling.
> - **R4a′, K0 + the calibration pipeline** (new): `memfn/k0.h`; `mf_price` over `prices.inc`; `memfn/cal/calibrate.c` + `run_calibrate.sh` + per-arm `generate.py`; the first priced arms `x86-64-v1` (ubuntubudu, through the executor channel) and, on Q19, `armv8-a` (the Mac); C2 (price vs measurement, with the staleness count), C7 and C8 as the kit's own tests. **Trigger:** R4a green. No pcrec cell is needed, because it changes no emitted byte.
> - **R4b, K2 composition generator + K3 CLI** (unchanged), with `mf_emit` taking a kernel per arm and the fallback hook. **Trigger:** R4a′ green on one priced arm, plus a named first pcrec customer.
> - **R4c, pcrec's K0 consumer, byte-identical first:** `--isa=TOKEN` as an opaque value axis (default `portable`), `SCAN_ROWS` promoted at site OFS (rows `libc-memchr`/`leapfrog` = today's text, each with its price-formula field), the `kit` row against a K0 STUB that answers UNPRICED for every token, so ZERO movers is the identity gate. C4 (the arch-blindness detector, with its allowlist counted at birth) and C5 land here, and §2.4(e) is fixed in the same change. No abi event while the stub answers. **Trigger:** R4b green.
> - **R4c′, the first movers: portable-class kernels (SWAR) at OFS/PF under `MF_Q_PORTABLE_ONLY`**: the stub is replaced by the real K0, `-fno-kit-scan`/`-fno-kit-native` exist, and there are an abi bump, `<PREFIX>_SCAN_FORM` on movers, the `docs/spec/` hunk, C3 on the movers, sabotage rows and the selection-diff census. This is the first end-to-end K0 customer, and it is admissible under the SIMD hold (D122 addendum 3). **Trigger:** a measured cell whose time is in a one-byte or cube scan with short proven spans (k82diag §2's 6-11 B cells), alpha-accepted per D144.
> - **R4d, native-class kernels at OFS (`vec-verify`'s successor):** `MF_Q_PORTABLE_ONLY` is lifted for budget-1 sites. **Trigger:** `[OPT-SIMD]` opened (D119 sequencing) AND the K82 pair-arm cells above the D144 addendum-1 floor on Linux. U-1's margin is ANSWERED (fusion wins at ≤ 64 B, loses from ~512 B). Under K0 that is no longer a gate but the prices themselves.
> - **R4e, PF byte-class:** `pf_emit_bcls[_bounded]` promoted to `SCAN_ROWS`. **Trigger:** unchanged (U-2's class-shape census plus a Linux `pf_emit_bcls` cell).
> - **R4f, in-loop sites (STAY, EDGE, VMSPAN) and the in-loop calibration column:** the three loops promoted (§2.4 b-d), `-fno-kit-loop`, and `calibrate.c`'s `MF_Q_INLOOP` column. Until then, in-loop queries answer UNPRICED. **Trigger:** U-3 (an in-loop probe at a real emitted site) AND a Linux cell dominated by class runs.
> - **R4g, T6's `kit` row (VERIFY_RUN):** **Trigger:** unchanged (a census of masked runs with L ≥ 16 at verify sites, plus a cell).
> - **R4h, declared tokens beyond `portable`** (`x86-64-v3`, …: attribute, CPU-check and level-stamp texts from the kit, `rx_info.isa_token`, an abi event). **Trigger:** isa_evaluation.md L-1/L-2. L-2 is answered as "no customer now" (linux_results.md §5), so this stays HELD.
> - **Filed, not scheduled** (unchanged): the stay set through T4; N4 ALL-PRESENT. New: the platform-qualified token (Q22), built for a measured customer only; an emulator CORRECTNESS arm for v4/SVE (never a price).
---

## 7. K0, THE CAPABILITY-AND-PRICE QUERY `[rev2]`

**[rev3] SUPERSEDED ENTIRE by D146 (§R3, §8).** No price, token-priced
quote, dominance test or reference term crosses the boundary any more,
and pcrec does no cost comparison. The section is kept as the record of
the design the r2 panel reviewed. What survives of it: the opacity
principle (§7.1's last paragraph: the kit never learns a site name,
pcrec never an ISA name), the fixed `portable` default (§7.2, HELD with
R4i), the UNOWNED-arm rule as the kit's K-4 (§8.6), and checks C1, C4,
C5 and C6, rebuilt in §10.

### 7.1 The principle: one fact crosses the boundary, and it is a price

Revision 1's boundary already kept classifiers, unrolling and the short
path inside the kit (§3.4). But it left pcrec reading three facts that only
an architecture can answer:

- whether a vector form exists here (`BASE`/`DECLARED`);
- how wide a vector is (`V`, in row 1's predicate);
- whether the vector form is worth it. This was left to "OWED placements"
  in pcrec's row order, which would have become measured thresholds in
  pcrec's tables.

K0 replaces all three with one question and one answer:

| pcrec knows | the kit knows |
|---|---|
| WHAT is scanned (S as a 256-bit set, a pinned pair, a run) and WHERE (the site, its budget, its handoff) | which kernels exist for a token, and for which set shapes |
| the proven span interval and, if any, a density interval | what each kernel costs, per call, per byte and per hit, on the token's calibration box |
| the cost SHAPE of its own scalar rows (one `memchr` stream, two leapfrogged streams, a table walk), as formulas | the measured value of every generic machine term those formulas read (a libc `memchr` call, a table-walk byte step, a restart) |
| the hook text (verify, fallback, bound, prefix) | the target-attribute, route, CPU-check and loader-marker text for a token |
| the decision: one comparison in one unit | nothing about pcrec's sites |

The kit never learns a pcrec site name (§3.4's rule, kept). pcrec never
learns an ISA name. The row that compares them is arch-blind by
construction, because both sides of the comparison come back from the kit
in the same unit.

### 7.2 The token

- **The grammar is the kit's.** pcrec's `--isa=TOKEN` (the `.rxt` `isa`
  config line; `pcrec_options.isa`, a string) is handed to
  `mf_token_parse`. An unknown token is refused with the kit's reason and
  its list (`pcrec --list-isas` prints `mf_tokens()`). pcrec holds the
  result as `const mf_token *`, an incomplete type whose only accessor
  pcrec may call is `mf_token_name()` (for the stamp). It cannot compare
  tokens, and the compiler enforces that.
- **The default is `portable`, fixed, never detected** (§R2 finding 3,
  Q18). `portable` is a COMPOSITE token. Its price list has one ARM per
  owned baseline: `x86-64-v1` (ubuntubudu) and `armv8-a` (the Mac). Its
  kernel text is the kit's gcc-time ladder over those arms. Its `#else`
  is pcrec's next row (§2.5, unchanged in substance). An unknown
  architecture compiles the `#else` and costs exactly the next row.
- **A declared token** (`x86-64-v3`, `armv8-a`, …) has one arm. Its
  kernels are one spelling inside a target-attributed matcher. Revision
  1's ROUTE (target attribute A, or the consumer's `-march` with an
  `#error` floor M, isa_selection.md §1.2.2) is folded into the token:
  `x86-64-v3` is route A, and `x86-64-v3+cc` (spelling Q21's) is route M.
  The kit owns the route's text. pcrec's designed `--isa-route` axis is
  withdrawn.
- **What pcrec does with the token, completely:**
  1. it passes the token to `mf_price` and `mf_emit` (§7.3);
  2. it stamps `<PREFIX>_ISA "<name>"` when the token is not the default
     (D46's "what was asked"; a default artifact is byte-identical);
  3. it injects the kit's opaque per-token text at four fixed places: the
     matcher's attribute (`mf_text_attr`), the `<prefix>_cpu_ok()` body
     (`mf_text_cpu_ok`), the level stamp ladder (`mf_text_level_stamp`)
     and, under `--isa-marker`, the loader note (`mf_text_marker`, or the
     kit's refusal). Each is a byte string pcrec does not parse.

  pcrec never branches on the token. §7.8 C4 checks that.

### 7.3 The API

`memfn/k0.h` (the kit's in-tree header, Q13). The shapes below are the
contract to build at R4a′. The field lists are complete for the
operations of §2.2. Names are PROPOSED.

```c
#define MF_K0_ABI 1                 /* bumped on any layout change below */

typedef struct mf_token mf_token;   /* opaque; pcrec cannot see inside */

/* -- tokens --------------------------------------------------------- */
int          mf_token_parse(const char *spelling, const mf_token **out,
                            char *why, size_t whylen);   /* 0 or MF_ERR_TOKEN */
const char  *mf_token_name(const mf_token *t);           /* stamp text only  */
size_t       mf_tokens(const char **names, size_t cap);  /* --list-isas      */
const mf_token *mf_token_default(void);                  /* "portable"       */

/* -- the question (architecture-neutral) ---------------------------- */
typedef enum {
    MF_OP_FIND_IN,      /* first i in [lo,hi) with s[i] in S                     */
    MF_OP_SKIP_IN,      /* first i in [lo,hi) with s[i] NOT in S                 */
    MF_OP_FIND_PAIR,    /* first i: s[i] in S1 and s[i+delta] in S2              */
    MF_OP_VERIFY_RUN,   /* (s[i+j] & mask[j]) == run[j] for j < len, one place   */
    MF_OP_ALL_PRESENT   /* every one of k sets has a member in [lo,hi)           */
} mf_op;

typedef enum {
    MF_H_RETURN,        /* stop at the first hit; return its index (or the bound) */
    MF_H_VERIFY_NEXT,   /* run the caller's verify per hit; continue on failure   */
    MF_H_ADVANCE,       /* write the cursor in place (skip forms)                 */
    MF_H_ALL_PRESENT    /* OR-accumulate seen sets; stop when all are seen        */
} mf_handoff;

#define MF_SPAN_UNBOUNDED UINT64_MAX
#define MF_PPM_FULL       1000000u   /* density interval default: [0, 1e6] */

typedef struct {
    uint32_t       abi;             /* MF_K0_ABI                                   */
    mf_op          op;
    mf_handoff     handoff;
    uint8_t        reverse;
    uint8_t        set[32];         /* S (FIND_IN/SKIP_IN/FIND_PAIR's S1)          */
    uint8_t        set2[32];        /* FIND_PAIR's S2                               */
    int32_t        delta;           /* FIND_PAIR: S2's offset from S1               */
    const uint8_t *run, *mask;      /* VERIFY_RUN                                   */
    uint32_t       run_len;
    const uint8_t (*sets)[32];      /* ALL_PRESENT: k sets                          */
    uint32_t       nsets;
    uint64_t       span_lo, span_hi;/* PROVEN bytes the operation may read;        */
                                    /*   span_hi = MF_SPAN_UNBOUNDED if none       */
    uint32_t       dens_lo, dens_hi;/* candidates per 1e6 bytes; default 0..FULL   */
    uint32_t       flags;           /* MF_Q_INLOOP (D91 budget 2);                  */
                                    /* MF_Q_PORTABLE_ONLY (no native kernels:      */
                                    /*   D122 add. 3's line, -fno-kit-native)      */
    const char    *deny;            /* --kit-deny's list, passed through unparsed  */
} mf_query;

/* -- the answer: a price list ---------------------------------------- */
typedef struct { int64_t lo, hi; } mf_ps;   /* picoseconds: min and median of N loops */

typedef struct {                    /* cost(r) = at_r0 + per_byte*(r - r0)/1000,    */
    uint64_t r0, r1;                /*   for r in [r0, r1); r1 = MF_SPAN_UNBOUNDED  */
    mf_ps    at_r0;                 /*   on the last segment. at_r0: ps per call    */
    mf_ps    per_byte;              /*   per_byte: fs per byte (ps x 1000), so a    */
} mf_seg;                           /*   0.020 ns/B slope is 20,000, not 20         */

#define MF_MAX_SEG 16
typedef struct {
    mf_ps    per_hit;               /* ps per candidate handled (VERIFY_NEXT only)  */
    uint32_t nseg;
    mf_seg   seg[MF_MAX_SEG];
} mf_curve;

typedef struct {
    char     kernel_id[48];         /* opaque; stamped; passed back to mf_emit      */
    mf_curve cost;
    uint32_t code_bytes;            /* exact source bytes of the injected call site */
    uint32_t helper_bytes;          /* shared text emitted once per artifact        */
    uint32_t needs;                 /* MF_NEED_BOUND_EXPR, MF_NEED_SCRATCH_LOCAL,   */
                                    /* MF_NEED_HELPER_ONCE: arch-neutral site       */
                                    /* obligations pcrec must be able to meet       */
} mf_quote;

#define MF_MAX_QUOTE 8
typedef struct {                    /* one architecture arm of the token           */
    char     arm_id[24];            /* opaque (e.g. a digest); never a branch input */
    int      status;                /* MF_PRICED / MF_UNPRICED / MF_STALE           */
    uint32_t nquote;
    mf_quote quote[MF_MAX_QUOTE];   /* in the KIT's preference order (C1 x C2)      */
    const struct mf_refterms *ref;  /* this arm's generic terms (§7.5)             */
    char     cal_id[24];            /* digest of the calibration rows read          */
} mf_arm;

#define MF_MAX_ARM 4
typedef struct {
    uint32_t abi;
    int      status;                /* MF_PRICED if any arm is; else MF_UNPRICED   */
    uint32_t narm;
    mf_arm   arm[MF_MAX_ARM];
    char     kit_version[16];
} mf_pricelist;

int mf_price(const mf_token *t, const mf_query *q, mf_pricelist *out);

/* the generic terms pcrec's own rows are priced from (§7.5) */
typedef enum {
    MF_REF_LIBC_MEMCHR,   /* one libc memchr call reading r bytes                 */
    MF_REF_LIBC_PAIR,     /* two leapfrogged libc memchr streams (today's pair arm)*/
    MF_REF_LIBC_RESTART,  /* re-entering memchr after a discarded hit             */
    MF_REF_LOOP_TABLE,    /* a byte loop testing a 256-entry table per byte       */
    MF_REF_LOOP_EQ,       /* a byte loop testing == per byte                      */
    MF_REF_CMP_WORD8,     /* one 8-byte masked word compare (runcmp's `words`)     */
    MF_REF_NTERMS
} mf_refterm;
const mf_curve *mf_ref(const struct mf_refterms *r, mf_refterm which);

/* -- generation (K2, unchanged in substance from §3.3) ---------------- */
typedef struct {
    void (*on_hit)(void *u, mf_sink *c, const char *cand_expr);
    void (*fallback)(void *u, mf_sink *c);   /* the next row's text: every #else */
    const char *bound_expr;
    const char *prefix;                      /* pcrec's D143 placeholder          */
    void *u;
} mf_hooks;

int mf_emit(const mf_token *t, const mf_query *q,
            const char *const *kernel_per_arm,   /* NULL entry = fallback on that arm */
            const mf_hooks *h, mf_sink *out, char *names, size_t nameslen);

/* -- per-token opaque text (§7.2 item 3) ----------------------------- */
int mf_text_attr(const mf_token *t, mf_sink *out);
int mf_text_cpu_ok(const mf_token *t, const char *prefix, mf_sink *out);
int mf_text_level_stamp(const mf_token *t, const char *prefix, mf_sink *out);
int mf_text_marker(const mf_token *t, mf_sink *out, char *why, size_t whylen);
```

**Versioning.**

- `MF_K0_ABI` covers the structs' layout and the meaning of every field.
  Every struct carries it first. pcrec checks it at build time
  (`_Static_assert(MF_K0_ABI == PCREC_K0_ABI_EXPECTED)`), because the kit
  is in-tree (Q13). After extraction to a vendored copy, the same assert
  pins the vendored version.
- `kit_version` names the kit's text. Any change to kernel text moves
  emitted bytes, so it is a pcrec `abi` event (D76/D94, unchanged from
  revision 1).
- `cal_id` names the calibration rows an arm's prices came from. A
  recalibration moves no kit text and no layout, but it can move
  SELECTIONS. Its governance is Q20.
- **Staleness is impossible by construction, not by discipline.** Every
  calibration row records the digest of the kernel TEXT it timed. When
  the kit's current text for a kernel differs from that digest, `mf_price`
  marks the arm `MF_STALE` and returns no quote for that kernel. A
  stale arm behaves like an UNPRICED one (§7.6), and C2 (§7.8) counts the
  stale kernels, which must be 0 at a release.

### 7.4 The common unit, and the shape of a price

- **The unit is integer picoseconds per call on the arm's calibration
  box.** It is the unit `litscan_k82b.md` §1.3 proposed for its cost
  terms (`limits.def` rows in `ps`), for the same reasons: integer and
  bit-exact. Revision 1 had no unit at all, because it had no comparison. Slopes are
  carried in femtoseconds per byte, so that `memchr`'s 0.020 ns/B is 20,000
  rather than a rounded 20.
- **The variable is `r`, the bytes the operation reads before it hands
  off.** For RETURN, `r` is the distance to the first hit, capped at the
  bound. For ADVANCE it is the run length. For VERIFY_NEXT it is the whole
  bound, and the hits along it cost `per_hit` each. For ALL_PRESENT it is
  the distance to the last first-occurrence. Both sides of a comparison
  read the same `r`, because both implement the same search with the same
  semantics.
- **The curve is piecewise affine with MEASURED breakpoints.** The
  calibration measures each kernel at a fixed ladder of read lengths:
  every length 1 to 64, then 128, 256, 512, 1 KiB, 4 KiB, 64 KiB and
  1 MiB. Between two measured lengths the price is linear interpolation.
  Beyond the largest, the slope is the one measured between 64 KiB and
  1 MiB. There are no fitted parameters and no smoothing. The dense
  1-64 ladder is there because block quantization makes the cost
  non-affine below twice any vector width (§7.11 item 2). Its breakpoints
  are merged into at most `MF_MAX_SEG` segments by dropping a point only
  when interpolating across it stays inside both neighbours' spreads.
- **Every value is a pair (lo, hi) = (min, median) of N ≥ 5 loops**, each
  loop ≥ 50 ms. That is D144 addendum 1's protocol and the bench's
  Contract 3 reporting. The harness's own loop cost (callcost's `loop`
  row, 0.30 ns on Linux) is measured in the same run and subtracted.
- **`code_bytes` is exact, not modelled.** The kit dry-runs K2 for the
  query and counts the source bytes it would inject (D84's unit). So a
  ladder's bytes, revision 1's Q16 worry, are inside the quote.
- **`needs` is arch-neutral.** It says what the site must provide: a
  bound expression, a scratch local, a once-per-artifact helper. pcrec
  drops any quote whose needs the site cannot meet, without knowing why
  the kernel needs them.

### 7.5 The arch-blind row, and how pcrec prices its own rows

**pcrec's own rows carry PRICE FORMULAS over generic terms.** A row knows
the shape of the text it emits, which is pcrec knowledge, arch-neutral.
It reads the VALUES of the generic machine terms from the same arm's
calibration (`mf_ref`), so both sides of every comparison were measured in
one run on one box.

| `SCAN_ROWS` row (§2.2 `[rev2]`) | handoff | price formula (curves add pointwise) |
|---|---|---|
| `libc-memchr` | RETURN | `LIBC_MEMCHR(r)` |
| `libc-memchr` | VERIFY_NEXT | `LIBC_MEMCHR(W)`, plus `LIBC_RESTART` per hit |
| `leapfrog` | RETURN / VERIFY_NEXT | `LIBC_PAIR(r)`, plus `LIBC_RESTART` per hit (the measured two-stream form, overshoot included: it is what `pair_libc` timed) |
| `table-walk` | RETURN / ADVANCE | `LOOP_TABLE(r)` |
| `table-walk`, T4 spelled `==` or a range | RETURN / ADVANCE | `LOOP_EQ(r)` |
| T6 `words` | (a verify) | `ceil(L/8) * CMP_WORD8` |

A structural check makes the price formula a required FIELD of every row
that can sit below `kit`. This follows `DfaPf.reseeds`' precedent ("so a
seventh form cannot be added without answering it"). A row with no
formula cannot be the comparison's other side, and the build fails rather
than the row being silently skipped.

**The row** (`SCAN_ROWS` row 1, and T6's row before `words`):

```c
/* pcrec side. Reads no ISA fact: every number comes back from the kit. */
static bool kit_applies(const ScanSel *s, KitPick *pick)
{
    const ScanRow *next = scan_next_applicable(s, &ROW_KIT); /* structural walk */
    mf_query q;  scan_query_of(s, &q);       /* operands + proven facts, §7.6    */
    mf_pricelist pl;
    if (mf_price(s->cx->isa, &q, &pl) != MF_PRICED) return false;

    bool any_win = false;
    for (uint32_t a = 0; a < pl.narm; a++) {
        pick->kernel[a] = NULL;                       /* NULL: this arm falls back */
        if (pl.arm[a].status != MF_PRICED) continue;  /* fallback = a tie          */
        mf_curve mine;  next->price(s, pl.arm[a].ref, &mine);
        for (uint32_t k = 0; k < pl.arm[a].nquote; k++) {   /* the KIT's order     */
            const mf_quote *qt = &pl.arm[a].quote[k];
            if (!site_meets(s, qt->needs)) continue;
            if (!mf_dominates(&qt->cost, &mine, &q)) continue;
            pick->kernel[a] = qt->kernel_id;  any_win = true;  break;
        }
    }
    if (!any_win) return false;
    if (tune_size_leaning(s->cx) && kit_bytes(pick) > next->bytes(s))
        return false;                       /* D139 item 1: only if smaller */
    return true;
}
```

**Dominance, exactly.** `mf_dominates(K, N, q)` holds iff three things
are true:

1. **(i)** `K.hi(r, d) <= N.lo(r, d)` at every corner. The corners are the
   points `(r, d)` with `r` in the union of both curves' breakpoints
   inside `[span_lo, span_hi]` plus the two ends, and `d` in
   `{dens_lo, dens_hi}`.
2. **(ii)** If `span_hi` is unbounded, the same inequality also holds for
   the last segment's slope plus `d · per_hit`, at both values of `d`.
3. **(iii)** At least one corner is strict.

The `per_hit` term counts only under VERIFY_NEXT. With
`hits = d · r / 10^6`, the difference `K − N` on any segment has the form
`a + b·r + c·d·r`. That is bilinear, so its maximum over a rectangle is
at a corner, and the corner check is a PROOF over the whole box, not a
sample. The arithmetic is in `__int128`, exact. Test vectors ship with the
function, as `L(x)`'s do (findb4).

**Why this is not a tuned cutoff (D119, D144, the K82 ruling).**

- There is no threshold anywhere in pcrec. Every number is a measured
  machine quantity, regenerated by a pattern-blind, bench-blind probe.
- The verdict reads only the SIGN of a difference, so uniform scaling of
  an arm's prices moves nothing. §7.8 C7 tests that.
- The only modelled step is interpolation between measured lengths, and
  C2 checks it.

**The worked example (Linux, `linux_results.md` §1).** Take the K82 pair
arm (`leapfrog`, RETURN) against a fused two-needle kernel on the
`x86-64-v1` arm. The kernel reads 1.48-3.29 ns up to 64 B. `LIBC_PAIR`
reads 7.08-8.26 ns there. At 4 KiB the kernel reads 157.8 ns and
`LIBC_PAIR` 110.2.

- At an OFS site whose run window proves a span of 64 B or less, the
  kernel dominates and is selected.
- At a rest-of-subject site, (ii) fails on the last segment's slope, so
  the row does not apply and `leapfrog` stays.
- At the same site under a declared `x86-64-v3` token, a quote for an
  AVX2 unrolled body (RB-7) would be priced separately. It wins iff its
  own measured slope beats `LIBC_PAIR`'s.

pcrec reads none of those facts. The crossover revision 1 would have
encoded as "OWED placement" (§2.2 row 4) is a consequence of two price
lists.

### 7.6 The defaults: unpriced tokens, unproven spans, unknown density

| situation | the kit's answer | what pcrec does |
|---|---|---|
| the token's only arm is unowned (`x86-64-v4`, `armv8-a+sve`, `+sve2`) | `MF_UNPRICED`, no quotes | the row does not apply. The artifact is byte-identical to its `-fno-kit-*` twin except the `<PREFIX>_ISA` stamp. An unpriced token is never selected, by construction |
| a composite token with one arm unpriced (e.g. `portable` before Q19's armv8-a ruling) | that arm `MF_UNPRICED`; the others priced | the unpriced arm falls back (its `#else` is the next row, a tie). The row can still apply on the priced arms' wins |
| a kit kernel's text changed since calibration | that arm `MF_STALE` for that kernel | as UNPRICED for that kernel |
| no kit in the tree yet (before R4a′), or a stub K0 | `MF_UNPRICED` for every token | the row never applies, so zero movers. The stub is R4c's implement-then-replace starting point |
| an arm has quotes but none dominates | `MF_PRICED`, quotes returned | that arm falls back. The row applies only if some other arm wins strictly |
| no proven upper bound on the span (rest of subject) | — | `span_hi = MF_SPAN_UNBOUNDED`; dominance must hold on the last segment's slope (§7.5 (ii)) |
| a proven bound (`maxw`, a counted edge's span, the D11 `n − 1` view, a run window) | — | `span_hi` = that bound. A loop-free kernel the kit quotes only when `span_hi` fits it, so pcrec never sees `V` |
| density unknown (the default) | — | `[dens_lo, dens_hi] = [0, MF_PPM_FULL]`. Only VERIFY_NEXT and ALL_PRESENT read it; RETURN and ADVANCE compare on `r` alone (§R2 finding 2) |
| density known from a findings bundle | — | the interval narrows to the bundle's rate bounds. Never required; K82's parked expected-cost model is not a dependency (Q23) |
| an in-loop site (D91 budget 2) | quotes priced from the IN-LOOP calibration (`MF_Q_INLOOP`): the kernel entered hot, back to back, at the site's re-entry pattern | deny bit `-fno-kit-loop`. Until U-3 measures a real emitted in-loop site, the in-loop calibration is unbuilt, so in-loop queries answer UNPRICED |

So the kit's default is **no assumption**: the full density interval, an
unbounded span when nothing is proven, and no price where no house box
measured one.

### 7.7 The calibration data: provenance, format, regeneration, ownership

**Layout** (in-tree under the kit, Q13; `third_party/`'s shape applied to
data derived by MEASURING, as `oracle_store/` applies it to data derived
by RUNNING a library):

```
memfn/cal/
  CLAUDE.md
  calibrate.c          the probe: times K2-EMITTED kernel text and the
                       generic reference forms, per arm, on the box it runs on
  run_calibrate.sh     pinning (taskset on Linux), quiet-box checks (load1
                       before/after, recorded), N >= 5 loops >= 50 ms each
  <arm>/               one directory per ARM (x86-64-v1, x86-64-v3, armv8-a)
    PROVENANCE.md      box, CPU, OS, libc, compiler + flags, governor, date,
                       commit, probe digest, and WHAT DERIVES FROM IT
    raw/<run-id>.txt   the probe transcript, verbatim, with its header
    generate.py        raw -> prices.tsv; interpolation and segment merge only
    prices.tsv         the derived table (table-contract TSV)
  prices.inc           every arm's prices.tsv as C data; generated, committed
```

**`prices.tsv`** has three `#section` blocks (`docs/spec/table_contract.md`):

- `arm`: one row per arm. The columns are `arm  owner_box  status
  cal_id  run_id`, where status is `PRICED`, or `UNPRICED` with a reason.
- `kernels`: one row per (kernel, query class, segment). The columns are
  `kernel_id  text_digest  op  handoff  shape  inloop  r0  r1
  at_r0_lo  at_r0_hi  per_byte_lo  per_byte_hi  per_hit_lo  per_hit_hi`.
  The `shape` column holds the kit's C1 row name. That keeps it opaque to
  pcrec, and it is how the kit maps a query's set onto its rows.
- `reference`: one row per (term, segment), with the same cost columns.

**Regeneration.** `make -C memfn gen-cal` iterates `cal/*/generate.py`
and names no arm (`make gen-tables`' general rule). `generate.py --check`
regenerates into memory and fails on any difference. It runs in the
kit's own `make test`, so a hand-edited `prices.tsv` goes red. The raw
transcript is the only measured artifact. Everything downstream is
derived and checked.

**Ownership** (option_sets.md §3.5a's table, now a CALIBRATION table):

| arm | owner box | runs the calibration | status |
|---|---|---|---|
| `x86-64-v1`, `-v2`, `-v3` | ubuntubudu (Zen 1, glibc 2.43) | the manager, through pcrecdev2's executor channel (heavy Linux runs), on a quiet box | PRICED once measured |
| `x86-64-v4` | none (no AVX-512 box) | — | **UNPRICED** |
| `armv8-a` | the Mac (M1 Max, libSystem) | a lane, in a quiet Mac window | PRICED on Q19's ruling, else UNPRICED |
| `armv8-a+sve`, `+sve2` | none | — | **UNPRICED** |
| `portable` | composite: `x86-64-v1` + `armv8-a` | — | priced per arm |

An emulator (Intel SDE, `qemu-user`) can prove CORRECTNESS for an
unowned arm (option_sets.md R6). It can never price one: emulated time
is not the target's time. So v4/SVE stay UNPRICED until a real box
exists, and an unpriced arm can never select a kernel. That is the safe
direction.

**Relation to D141 ([EST-REGISTRY]).** The kit's `prices.tsv` is an
estimates registry for one domain, built in the shape D141 asks for (a
value, a unit, a kind that is FITTED, and provenance). pcrec gains NO
estimation constant from K0: its side of the comparison is formulas over
kit-supplied terms. D141's census, when scheduled, finds nothing new in
`src/` for this mechanism.

### 7.8 Testability

| # | check | what it proves | shares a source with the calibration? |
|---|---|---|---|
| C1 | every kit kernel against the SCALAR BYTE LOOP, exhaustive per length × alignment × position, guard pages, ASan/UBSan (§4.5, N-6) | answers | no |
| C2 | **price against measurement**: `memfn/cal/verify` times the kernels with its OWN driver, at read lengths the calibration ladder did NOT use (midpoints of every segment). Each measured value must lie inside the quote's (lo, hi), widened by the verifier's own measured spread. It also counts `MF_STALE` kernels (must be 0 at a release) | the interpolation rule and the data's currency | partly: it shares the kernel text and the box, but not the driver, the lengths or the loop code. It is the kit's own check, not the control |
| C3 | **THE CONTROL: decision order end to end.** On the owner box, over the population of every corpus site where `kit` is selected, plus every site where an arm was priced and lost, build each artifact default and with `-fno-kit-*`, and time both with the harness's find-all driver on corpus subjects (D144 add. 1 loops; the floor is base vs base). Where the prices predict a win beyond both spreads, the measured kit arm must not be slower than the deny arm past the floor. Where they predict a loss, the forced arm (`kit-scan=force`, below) must not be faster past the floor | that pcrec selects only where it wins, which is the claim the row makes | **no**: the subjects are different (corpus text, not synthetic spans), the driver is different (generated artifacts through the shipped API, not `calibrate.c`), and so are the code paths (the kernel inside a real matcher with pcrec's hooks, not isolated). It shares only the box, which is unavoidable and named |
| C4 | **arch-blindness detector**: `src/`, `cli/`, `lib/` contain no ISA vocabulary outside a committed allowlist counted at birth (D107's shape), and no `strcmp`/`==` on `mf_token_name(`. A new hit fails. The vocabulary is `grep -rniE '\b(sse[0-9.]*\|ssse3\|avx[0-9a-z]*\|neon\|sve2?\|x86-64-v[1-4]\|armv8[a-z.+-]*\|aarch64\|__x86_64__\|__arm_neon\|__avx2__\|pshufb\|x86_64\|arm64)\b'`. At 68acba37 it finds ONE hit (`src/opt/prefix_k.c:45`, a comment citing glibc's AVX2 `memchr` measurement), so the allowlist is born with one row | Frank's "as much as possible" as a red test | n/a |
| C5 | **unpriced never selects**: the corpus compiled at `--isa=x86-64-v4` and `--isa=armv8-a+sve` carries no `kit` selection, and is byte-identical to `-fno-kit-scan -fno-kit-loop` except the `<PREFIX>_ISA` stamp | §7.6's first row | no |
| C6 | answer identity per deny, per box: `make test-axes` arms for the three bits; option_sets.md §3.5a's compile-only arms per token | correctness under every selection | no |
| C7 | **ratio invariance**: scaling every price in one arm by 2, or by 1/2, flips 0 selections over the corpus census (k82b §1.4's shape) | the decision depends on the SIGN of a difference only, so a uniformly mis-scaled arm (a whole box running slow) moves nothing. A NON-uniform slip (one term in the wrong unit) is not this check's: C2 and C8 catch it, because their measured and fixture numbers stay in the true unit | n/a |
| C8 | the dominance unit test, on the committed Linux numbers as a fixture: the fused pair kernel against `LIBC_PAIR` SELECTS at `span_hi = 64` and does NOT select at `MF_SPAN_UNBOUNDED`. Plus a crossing pair that differs only at an interior breakpoint, which a two-endpoint check would pass | the corner proof, including the interior breakpoints and the slope arm | uses calibration numbers as fixtures by design |

**Forcing (D46's controllability half).** `kit-scan` and `kit-loop` are
three-valued axes (option_sets.md §2.4a): deny, auto and force. Under
force, the row takes the kit's first quote whose `needs` the site meets,
regardless of price. If the kit returns no quote (an UNPRICED token, or
an unsupported shape), the force cannot be honoured. The compile is then
refused, with the kit's reason. That refusal replaces option_sets.md's
constraint row 8 (`forced-row-below-level`) and is arch-blind: pcrec
refuses because the answer was empty, not because it knows a level.
`--kit-force=KERNEL_ID` (opaque, kit-validated) pins one kernel for C3's
loss arm and for the kit's bench.

**Sabotage rows** (ids taken at build, highest S on main + 1):

- one kernel's prices ×0.1 in `prices.inc` (C3 fires; C2 fires);
- an ISA word added to `src/gen/emit_dfa.c` (C4);
- `mf_price` returning PRICED for an unowned arm (C5);
- a kernel's text edited without recalibration, with the staleness
  digest check removed (C2's stale count);
- `mf_dominates` checking only the two ends of the span interval (C8's
  interior-crossing vector);
- one arm's `per_byte` read as ps instead of fs (C2: the verifier's
  measured midpoints leave the quote; C8: the committed fixture's
  selection flips at `span_hi = 64`).

### 7.9 What K0 removes

**From §2 (pcrec's per-site vector rows):**

| revision 1 | revision 2 |
|---|---|
| `SCAN_ROWS` rows 1-3 (`loopfree`, `vec-verify`, `vec`) and row 6 (`swar`) | ONE row, `kit`. The short path, the verify fusion, the vector scan and SWAR are all kit kernels. SWAR is a kernel of the PORTABLE class (`-fno-kit-native` keeps it) |
| row 1's predicate on `V`, the kit's short-path width | gone. The kit quotes a loop-free kernel only when `span_hi` fits it |
| row 4's OWED placement of `libc-memchr` against `vec` | gone. It is a price comparison, decided by data (§7.5's example) |
| the `BASE`/`DECLARED(L)` predicate vocabulary (§2.1) | gone. The token is passed, never read |
| the §2.5 ladder as a pcrec emission | kit text. The `fallback` hook (pcrec's next row) is unchanged |
| T6's `vec-masked` with an `rc_holds(cx, …)` ISA predicate | T6 gains the same `kit` row with `MF_OP_VERIFY_RUN`. `rc_holds` still needs `cx`, for the token and the prices, not for an ISA |
| `<PREFIX>_SCAN_FORM` = a C1/C2 row-name pair | `<PREFIX>_SCAN_FORM` = the kit's opaque `kernel_id` per arm, emitted only where `kit` was selected (**`[rev4.1]`** on every artifact, `none` where no `kit` arm was selected: §18, Frank's Q3 (a)) |

**From [OPT-SETS] (`docs/design/option_sets.md`)**: the "arch
sub-panels".

| option_sets.md item | revision 2 |
|---|---|
| §1.2 vector-row denies: `-fno-vec-scan`, `-fno-vec-skip`, `-fno-vec-run`, `-fno-swar-scan` (four bits) | three bits: `-fno-kit-scan` (D91 budget-1 sites, T6 included where it is a prefilter verify), `-fno-kit-loop` (budget-2 sites), `-fno-kit-native` (portable-class kernels only: D122 addendum 3's line, the bench's SIMD-off testee). They are named for budgets and kernel class, never for an ISA |
| §1.2 `--memfn-deny=cube,unrolled,…` | `--kit-deny=`, the same list, passed through UNPARSED (`mf_query.deny`). pcrec cannot spell a classifier |
| §1.2 / §4.3 the `isa` family: an 8-member POSET pcrec holds | one opaque value axis whose domain is `mf_tokens()`. The order, the chains and the members live in the kit. `--list-sets` lists `isa` members from the kit |
| §1.2 `isa-route` (`--isa-route=macro`) | withdrawn; folded into the token (Q21) |
| §1.2 `-fisa-check=entry`, `-fisa-dispatch=cpu-supports` | the CPU-check text is `mf_text_cpu_ok`. A dispatched kernel (isa_selection.md row 5, H2) is a kit kernel quoted with its measured dispatch term inside its price, under a token that names it. It stays HELD (Q11) |
| §1.2 `--isa-marker` | stays a pcrec boolean (explicit-only, §2.8). Its validity is the kit's answer (`mf_text_marker` refuses with a reason) |
| §2.7 constraint row 6 `isa-route-orphan` | removed (no route axis) |
| §2.7 constraint row 7 `isa-marker-orphan` ("not on the x86 chain") | removed. The kit's refusal replaces it, and pcrec no longer knows what an x86 chain is |
| §2.7 constraint row 8 `forced-row-below-level` | removed. The arch-blind "force with an empty quote list" refusal (§7.8) covers it, for every token |
| §4.2 the `vector` family's four members over four bits | `auto`; `no-simd` = `-fno-kit-native`; `scalar` = `-fno-kit-scan -fno-kit-loop`. A two-bit set at most. option_sets.md §0 item 8's "first consumer is [MEMFN] R4's vector rows" mostly evaporates: trigger 1 (one name over two or more vector-family bits) is met only by `scalar` |
| §4.2's `vector` × `isa` interaction table | gone. Both axes are inputs to one kit query, and the kit's answer is the whole table |
| §3.5's `vector` × `isa` sweep (4 × 8 = 32 corpus runs, floored) | three deny arms × each box's own priced tokens. The compile-only arms per token stay (§3.5a) |
| §3.5a ISA ownership | unchanged in substance, now the calibration ownership table (§7.7) |

**From isa_selection.md §2's first-match table** (pcrec-side ISA
selection): rows 1 (below the knee: baseline), 4 (in-loop: baseline only)
and 6 become price OUTCOMES. A wide kernel that cannot pay on the site's
span loses dominance. Row 3 (declared) is the token. Row 5 (H2 dispatch)
is a kit kernel. Row 2 (libc) is the reference terms. The table moves
into K0 entire. pcrec keeps no ISA selection table.

### 7.10 How pcrec's existing tables change

| table | change under revision 2 |
|---|---|
| T1 `dfa_pfs[]` | none of its own (as revision 1). Its emitters ask `SCAN_ROWS` at PF/OFS. §2.4(e) is still owed: G1's `memchr_form` premise becomes a property of the chosen `SCAN_ROWS` row, and that row may now be `kit` |
| T2 `req_admits[]` | none. G1's density clause must read the SCAN form's per-hit price class, not `strcmp` on a name (§2.4 e) |
| T3 `dfa_edges[]` | none. The edge's loop asks `SCAN_ROWS` at EDGE; ADVANCE handoff, budget 2 |
| T4 `ROWS` | none. The scalar spelling feeds `table-walk` and `LOOP_EQ`/`LOOP_TABLE`'s choice of formula, and S becomes `mf_query.set` |
| T5 `TAB_ROWS` | none |
| T6 `pcrec_runcmp_rows` | gains `kit` (op VERIFY_RUN) before `words`. Its next row's formula is `ceil(L/8)·CMP_WORD8`. Exact runs still get no row (gcc's `memcmp`, revision 1's reason) |
| T7 `pcrec_find_pick` | none. It may supply the density interval, optionally |
| T8, T9 | excluded (as revision 1) |
| `SCAN_ROWS` (new, §2.2) | four rows instead of seven: `kit`, `libc-memchr`, `leapfrog`, `table-walk`. Each non-`kit` row carries a price formula field |
| N1-N7 | as revision 1's §2.3/§2.4, with `kit` in place of rows 1-3 and 6 |
| the dial (`src/core/tune.c`) | two new axes join the pinned table: `kit-scan` and `kit-loop`, `auto` at every position. The size-leaning positions get D139's "only if smaller" through the row's own bytes clause (§7.5), not through a cell |
| `limits.def` | none from K0. If [K82]'s parked model is ever built, its `ps` terms would read `mf_ref` rather than adding rows (Q23) |

### 7.11 What is honestly uncertain

1. **Microbenchmark prices against in-situ cost.** A kernel inside a
   matcher pays alignment, register pressure and the hook's verify. The
   calibration times K2-emitted text inside a generated function, which
   is closer than K1 primitives, but it is not the matcher. C3 is what
   would show a systematic in-situ penalty. If it does, the remedy is an
   in-situ calibration column, never a correction factor.
2. **Interpolation below twice the vector width.** Block quantization
   makes cost a step function there. Hence the dense 1-64 B ladder and
   C2's midpoint samples. A kernel whose curve steps between ladder
   points would fail C2 rather than mis-select silently.
3. **The libc is the calibration box's.** `LIBC_*` prices glibc 2.43 on
   ubuntubudu and libSystem on the Mac. A consumer on musl inherits
   those decisions (Q22).
4. **`portable`'s conjunction.** A composite token needs a win on at
   least one arm, and the losing arms fall back. That is safe, but it
   doubles calibration and makes the ladder's bytes count against every
   arm's size gate.
5. **Compile-time cost.** One `mf_price` per candidate site is table
   lookups plus a dry-run K2 for `code_bytes`. That is unmeasured: R4c
   measures it under D45 before the row ships.
6. **The K82 ruling's spirit.** Frank parked K82's expected-cost model
   for simplicity. K0 is a cost comparison too. It differs in needing no
   rates (no W, no density prior, no bundle), only proven bounds. That
   is argued in §R2 and is Q23's to confirm.

---

## 8. THE DELEGATION CONTRACT `[rev3]`

### 8.1 The principle: a site crosses the boundary, and code comes back

| pcrec knows, and says | the kit knows, and decides |
|---|---|
| WHAT is searched: a predicate over positions (byte sets and masked runs at offsets from a candidate), from pcrec's single sources (P2 cube, T4 sets, P3 runs, the k-set derivation) | HOW: which term to scan and which to verify, the classifier per set shape, unrolling, the loop-free short path, a libc call vs inline vs injected text, the ISA ladder, SWAR vs vector, the always-present scalar arm |
| WHERE and under what PROOF: the site's D91 budget, its bound expressions, its proven span `[span_lo, span_hi]`, anchoring, the read limit | what those proofs buy: a span short enough for a loop-free path, an anchored site needing no loop at all |
| a density HINT per term and per predicate (pcrec's prior, encoding-gated) | what density does to its choice (iterate in place vs restart per hit, unroll factor) |
| the HANDOFF: what happens at a result (return it, advance a cursor in place, run pcrec's verify per candidate and continue on failure, or answer a presence boolean) | how the handoff is fused into its loop |
| the PROFILE asked for (§8.5): `baseline`, `portable` or `native`, and the opaque pass-throughs (`--memfn=` **`[rev4.4]`**; `--isa=` is withdrawn, §R4.3.1) | what each profile means in code, and every measurement behind its choices |

Neither side crosses into the other's column. The kit never learns a
pcrec site name or engine (§3.4's rule, kept). pcrec never learns an ISA,
never reads a cost, and never inspects the code it gets back: the text
goes from the kit's sink into pcrec's artifact unread.

### 8.2 The site description (C shapes, versioning)

`memfn/include/memfn.h`, the kit's ONLY public header (§11.1). Names
are PROPOSED; the shapes are the contract R4a builds. Every field is
architecture-neutral.

```c
#define MF_SITE_ABI 1   /* layout and meaning of every struct below           */
#define MF_VOCAB    1   /* the operation vocabulary: op x handoff x term kinds */

typedef enum {
    MF_OP_FIND,         /* first cand in [lo,hi) satisfying the predicate (last, if reverse)  */
    MF_OP_SKIP,         /* first cand in [lo,hi) whose byte is NOT in the one SET term       */
    MF_OP_VERIFY,       /* does the predicate hold at cand == lo (an anchored site)          */
    MF_OP_ALL_PRESENT   /* does EVERY one of npred predicates hold somewhere in [lo,hi)      */
} mf_op;

typedef enum {
    MF_H_RETURN,        /* write the result (or the miss value) to `result`                  */
    MF_H_ADVANCE,       /* move `cursor` in place with pcrec's own step text (skip forms)    */
    MF_H_ON_CAND,       /* per candidate, run pcrec's verify; continue on reject             */
    MF_H_BOOL           /* write 1/0 to `result` (VERIFY, ALL_PRESENT)                       */
} mf_handoff;

typedef enum { MF_T_SET, MF_T_RUN } mf_term_kind;

typedef struct {                    /* one position term, relative to cand          */
    mf_term_kind   kind;
    int32_t        offset;          /* bytes from cand; the term reads s[cand+offset..] */
    uint8_t        set[32];         /* MF_T_SET: 256-bit membership                    */
    uint32_t       table_ref;       /* MF_T_SET: pcrec's table-name hook id, or 0 (§8.3) */
    const uint8_t *run, *mask;      /* MF_T_RUN: (s[cand+offset+j] & mask[j]) == run[j] */
    uint32_t       run_len;
    uint32_t       ppm_lo, ppm_hi;  /* density hint: matches per 1e6 subject bytes;
                                       0..MF_PPM_FULL when unknown (the default)   */
} mf_term;

#define MF_MAX_TERM 8          /* [M6] 32 since MF_SITE_ABI 8 (Q-R10-3) */
typedef struct mf_pred {            /* a CONJUNCTION of terms                        */
    uint8_t  nterm;
    mf_term  term[MF_MAX_TERM];
    uint8_t  plan_hint;             /* TRANSITIONAL (§9.4): the term pcrec's model
                                       scans today; 0xFF = none                     */
} mf_pred;

typedef struct {
    uint32_t        abi;            /* MF_SITE_ABI                                   */
    mf_op           op;
    mf_handoff      handoff;
    uint8_t         reverse;
    mf_pred         pred;           /* FIND / SKIP / VERIFY                           */
    uint8_t         npred;          /* ALL_PRESENT                                    */
    const mf_pred  *preds;
    /* pcrec's proven facts */
    uint64_t        span_lo, span_hi;   /* proven bytes in [lo,hi); MF_SPAN_UNBOUNDED  */
    uint32_t        cand_ppm_lo, cand_ppm_hi;  /* the whole predicate's hint           */
    uint8_t         consumer;       /* MF_C_RESULT / MF_C_ENGINE: is a false candidate
                                       handed to a matcher that then rejects it?
                                       named, never priced (§9.4)                     */
    /* policy (§8.5): every bit arch-neutral */
    uint32_t        policy;         /* MF_P_BASELINE | MF_P_PORTABLE_ONLY |
                                       MF_P_INLOOP | MF_P_SIZE_LEANING               */
    const char     *opts;           /* [rev4.4] --memfn=, passed through unparsed    */
    const char     *token;          /* --isa=, passed through unparsed; NULL = the
                                       fixed default (§R2 finding 3), HELD (R4h)     */
} mf_site;

typedef struct {
    char     form_id[48];           /* opaque; stamped on every artifact (§18)         */
    uint32_t helpers;               /* once-per-artifact helpers the text names        */
    uint8_t  moved;                 /* 1 iff the text differs from this site's
                                       BASELINE text (computed by the kit; §10.5 C11) */
} mf_result;

int mf_emit_site(const mf_site *s, const mf_hooks *h, mf_sink *out,
                 mf_result *res, mf_arena *a);          /* 0, or a LOUD internal error */
int mf_emit_helpers(uint32_t helpers, const char *prefix, mf_sink *out);
int mf_vocab_has(mf_op op, mf_handoff h, uint32_t term_kinds); /* compile-time constant */
const char *mf_kit_version(void);                       /* "pcrec-memory-functions X.Y.Z" */
```

> **`[rev4]`** These shapes are EXTENDED by §14.0 (r3 F1-F11): three
> site forms, `end_back`/`empty`, `floor`, REQUIRED/OPTIONAL terms,
> ALL_PRESENT's `ret_pred`, `denies`, and a plan/render split whose
> `mf_art` carries form tallies, helpers and includes (`mf_plan` was never built; §14.8). `plan_hint` is NOT
> transitional (§14.9). `mf_result.form_id` is no longer stamped with a
> kit version (§18).

**Size (K3).** An `mf_site` is about 0.6 KB at `MF_MAX_TERM` 8 (32-byte
sets dominate; **`[M6]`** 2,696 bytes at 32, measured on x86_64, arena-backed). `preds` and runs are pointers into pcrec's arena. The kit
allocates nothing on the caller's stack beyond its frame and takes
scratch from `mf_arena`, which pcrec backs with its own arena. C10
(§10.5) forbids an `mf_site` or `mf_result` as an automatic variable
under `src/`.

**Versioning.** Three numbers, three meanings:

- `MF_SITE_ABI` covers layout and field meaning. pcrec asserts it at
  build (`_Static_assert(MF_SITE_ABI == PCREC_MF_SITE_ABI)`). In-tree
  (§11.1) the assert can only fail inside one commit.
- `MF_VOCAB` grows when an operation, handoff or term kind is ADDED
  (§8.4's request path). pcrec's delegation table (§8.5) is checked
  against `mf_vocab_has` at build: a site whose op the kit's vocabulary
  lacks is a build failure, never a silent pcrec fallback.
- `mf_kit_version()` names the kit's TEXT. A kit change that moves any
  byte pcrec emits is a pcrec `abi` event (§10.3). A kit change that
  moves no pcrec byte (a new op nobody requests yet, a K3 CLI feature, a
  test) is not.

**Totality.** For every request inside its vocabulary, the kit MUST
return code. A decline is a kit defect and pcrec fails loudly
(`pcrec_ctx_fail`, the house's internal-error tier). There is no "kit
declined, pcrec spells it itself" path: after a site's migration step
pcrec HAS no spelling of its own (§9), and keeping one would be the
second scalar spelling D122 forbids.

### 8.3 The hook contract

pcrec owns the names, the bounds and the code AROUND a site. It passes
them as TEXT, never as callbacks into the generated program. The kit
renders them into the site's code.

```c
typedef struct {
    /* the subject and its bounds: side-effect-free C expressions */
    const char *s;          /* the subject pointer                                    */
    const char *n;          /* the READ LIMIT: no byte at or past it is ever read        */
    const char *lo, *hi;    /* search start, exclusive end (D11's n-1 views pass here)   */
    /* RETURN / BOOL */
    const char *result;     /* the lvalue written                                       */
    const char *miss;       /* the value written when no cand exists (each site's own:
                               n, hi, -1 …; baseline arms need it byte for byte)         */
    /* ADVANCE */
    const char *cursor;     /* the cursor lvalue                                        */
    const char *step;       /* pcrec's step statement (`pos++`, `pos--`, …)              */
    const char *more;       /* pcrec's continue condition (its direction's scan_more)    */
    /* ON_CAND: pcrec's per-candidate verify */
    void (*on_cand)(void *u, mf_sink *c, const char *cand);
    uint32_t on_cand_reach; /* bytes on_cand reads at or after cand                      */
    /* one-position membership: T4 stays pcrec's */
    const char *(*member)(void *u, uint32_t term, const char *byte_expr);
    const char *(*table_name)(void *u, uint32_t table_ref);
    /* rendering */
    const char *prefix;     /* pcrec's D143 placeholder, rendered after emission         */
    int comment_tier;       /* PCREC_CMT_* passes through                                */
    void *u;
} mf_hooks;
```

**The rules, each with the check that holds it** (§10):

1. **Expressions are pure.** `s`, `n`, `lo`, `hi`, `more` and the member
   text may be evaluated any number of times, in any order. Only `step`
   has an effect. A kit arm that hoists `n` into a local is legal; a pcrec
   hook with a side effect in `hi` is a pcrec defect.
2. **The read guard is the kit's.** The kit never reads `s[k]` for
   `k >= n` or `k < 0`, for any term offset, any vector width, any tail
   (P8's rule, S-2: no aligned-down over-read). When `on_cand` runs, the
   kit has ALREADY established `cand + on_cand_reach <= n`. Held by the
   kit's guard-page tests (§10.2) with synthetic hooks that read exactly
   `on_cand_reach` bytes.
3. **The RETURN contract.** `result` = the LEFTMOST `cand` in `[lo, hi)`
   (the rightmost, if `reverse`) at which every term holds and every term
   read is below `n`, else `miss`. This is litscan_k82h.md §1.1a's
   written gate contract ("leftmost occurrence ≥ `search_from`") made
   the kit's, so the K82 handoff's soundness argument (`lo = max(f,
   c − K)`, that note's §1.2) reads the kit's result unchanged.
   > **`[rev4]`** Restated over REQUIRED and OPTIONAL terms (§14.5,
   > r3 F7): `c` is at most the true leftmost, and every REQUIRED term
   > holds at `c`. Rule 2 gains the expression-form caller guard and the
   > lower `floor` (§14.7).
4. **ON_CAND.** `on_cand`'s text ends in exactly one of two kit-rendered
   tokens, `\x01mfA` (accept) or `\x01mfR` (reject). Accept writes `cand`
   as the result. Reject resumes the search at `cand + 1` (`cand − 1`
   reversed): no candidate is skipped and none is revisited. The hook may
   name only `cand`, the hook expressions above, and pcrec's own locals
   declared OUTSIDE the site. The kit's own locals are block-scoped and
   carry the prefix placeholder, except inside BASELINE arms, which
   reproduce pcrec's pre-migration names exactly and declare them in the
   kit's baseline manifest (§9.2).
5. **ADVANCE.** The kit's loop is `while (more && member(byte at cursor))
   step;` in meaning. The text may differ (a vector body, a counted span),
   but the cursor ends at the first non-member position, or where `more`
   fails, and every `step` effect is the one pcrec gave. A counted span
   (the scan edge's `{0,n}`) is a proven `span_hi`, not a hook.
6. **Membership has ONE owner per granularity.** A ONE-POSITION test of a
   set is T4's (`member`), unchanged: the kit's scalar loop arms call
   back for it, so a set has one scalar spelling in the artifact. A
   MANY-LANE classifier of the same set is the kit's own (§4.3's C1).
   The `set[32]` bits are the truth both must agree with (§10.2's
   agreement check).
7. **Tables stay pcrec's.** A SET term may carry `table_ref`, naming a
   256-byte table pcrec already emits (`can_begin_match`, `stay<K>`,
   `scan<N>`). Baseline arms read it by name. Other arms may ignore it.
   The kit never emits a second copy of a table pcrec emits.
8. **The handoff into the DFA is pcrec's text AFTER the site.** The kit
   returns `c`; pcrec writes `lo = max(search_from, c − K)` and enters
   the engine. Nothing in the kit knows an engine exists. `consumer`
   tells the kit only whether a false candidate costs a later matcher
   anything, so it can weigh verifying harder (§9.4).

**What dissolves.** Revision 1's `fallback` hook (§2.5): the `#else` of
any ladder is the kit's own portable arm, and pcrec, after migration,
has no scalar text to offer. Revision 1's risk item 1 (§3.3, "the hook
contract is the riskiest surface") stands, now with rules 1-5 and their
checks. The first mover (§12.2 R4d) uses only RETURN, so ON_CAND's first
customer is a later step.

### 8.4 Compound work: "this check followed by this check"

D146: when pcrec needs compound work, the kit provides it. Rev 3 gives
compound work three spellings, all inside one request, and one way to
add a fourth.

| pcrec's need | spelled as | what the kit may do with it (its choice) | today's site |
|---|---|---|---|
| **a scan fused with a verify** ("find `c`/`C` at 4 where `SELECT` folds at 0") | ONE `MF_OP_FIND` whose predicate is a conjunction: a SET term and a RUN term at their offsets | scan the rarest term, filter on a second, verify the run from the mask bits, unroll: twins.md T-B's `ffl`, ~7x on the K82 gate | the ofsskip block (`ofs_test_emit_fn`: scan arm + `ofsk_emit_verify` chain + run term), the `<p>_reqrun[_whole]` blocks |
| **a check followed by a check** (presence, in any order) | `MF_OP_ALL_PRESENT` over predicates, in pcrec's ORDER as a hint | run them in order, reorder by density, or one fused pass with a per-predicate "seen" mask (F-ALL-PRESENT, §4.2 P-F) | the REQ_BYTE pre-check then `set-leads`; `emit_req_set_rest`'s k `memchr` passes (N4) |
| **a scan whose candidate pcrec must judge** (a verify the predicate cannot say) | `MF_H_ON_CAND` with pcrec's text | iterate the hit mask in place; never restart a call per hit | none today. It is the shape twins.md T-A's "iterate in place" lever names |
| **a scan handed to the engine** | RETURN, then pcrec's text (rule 8) | — | the K82 handoff |
| **a new composition** (an ORDERED pair: find P1, then P2 at or after P1's result + d; a COUNT; a mismatch over two streams, F8) | a REQUEST through §11.3's ledger, then an `MF_VOCAB` bump | the kit designs, builds and tests it in its own lane; pcrec's site joins the delegation table in the same change as its first use | none: filed when a customer has a measured cell (D77) |

So "this check followed by this check" is never pcrec emitting two kit
calls and gluing them. One site, one request, and the kit owns the
sequencing. It may emit two calls, if that is what wins.

### 8.5 What pcrec still decides, and the two tables it decides with

**Delegability is by SEMANTIC OPERATION, never by cost.** A site is
delegated when its operation is one of the kit's vocabulary and its
migration step has landed (§9). It is never delegated because something
measured faster. Some sites are NEVER delegated, each for a semantic
reason:

| site | delegated? | why |
|---|---|---|
| T1 PF (`memchr`, `byte-class`, `offset-set`, `run-pinned` and their `-bounded` twins) | yes | FIND over a predicate (one byte, a set, or the k-set conjunction) |
| T2 PRE (the REQ_BYTE / REQ_RUN pre-check blocks, `set-leads`) | yes | FIND / ALL_PRESENT |
| OFS (the ofsskip block, N5; shared by T1's offset/run rows and T2's run blocks) | yes | FIND over a conjunction |
| SETREST (N4) | yes | ALL_PRESENT |
| VERIFY and VMRUN (T6 `pcrec_runcmp_rows`: `words`, `overlap`, `bytes`, `memcmp`) | yes, as TWO site bits: VERIFY at budget 1 (the run term of a prefilter or pre-check, `emit_dfa.c:6039`) and VMRUN at budget 2 (inside the VM's match, `emit_vm.c:4483`, `:8628`) | VERIFY of one RUN term at a known position. One emitter, two budgets: runcmp's callers already split that way, which is why rev 2 put T6 under both of its loop and scan bits |
| STAY (N1), EDGE's loop (T3), VMSPAN (N2 at stride 1) | yes, at D91 budget 2 | SKIP with ADVANCE. Only the LOOP; the scan edge's peeled guard, its accept stores and state writes stay pcrec's (§9.3) |
| MLINE (N3, `(?m)^`'s `memchr('\n')`) | yes, last | FIND of one byte. No customer, so it migrates only for uniformity, and only if Q30 says so |
| N6 (`vm_rev_emit`'s backward walk) **RETIRED, D147 add. 12** | not now | a per-byte L1 test with captures in flight; compare_stack.md §5 keeps its form. Filed |
| N7 (`$_span_match[_caseless]`) | no | the encoding seam's residual entry; the encoding owns it (D23; **`[rev4.6]`** r5 B6: the owner is D58/DD-12, not D23, §R4.3.4). F8 `mismatch` is a later vocabulary item if S6's cell exists |
| VM span at stride > 1 | no | not a byte-set search (§2.4 d) |
| T4 one-position membership | never | one position, not a search; it is the `member` hook's source (§8.3 rule 6) |
| T8 DFA tables, T9 VM context tests, any DFA or VM step | never | the engine, not a memory function |

This is a static table in pcrec (`DELEG_SITES`, sites as bits on D139's
shape), one row per site with its op, handoff, D91 budget and deny bit.
Its op column is checked against `mf_vocab_has` at build (§8.2), and its
budget column against D91's site classification (C10).

**The profile, per site: pcrec's ONE first-match selection** (the house
idiom, memory `pcrec-decisions-as-first-match-tables`):

| # | profile | applies when | policy bits sent | what the kit does |
|---|---|---|---|---|
| 1 | `baseline` | the site's budget deny bit is set: `-fno-memfn-scan` (budget 1: PF, PRE, OFS, SETREST, VERIFY, MLINE) or `-fno-memfn-loop` (budget 2: STAY, EDGE, VMSPAN, VMRUN) | `MF_P_BASELINE` | emits the site's FROZEN pre-migration text: pcrec's own last spelling of this search, byte for byte (§9.2). The guard's "off" arm |
| 2 | `portable` | `-fno-memfn-native` is set. **DEFAULT ON during the SIMD hold** (D91, D119, D122 addendum 3; §12.2 R4f, Q28). **`[rev4]`** Now: axis `memfn-native` is NOT forced (default OFF; enabled by `-fmemfn-native`, D112's shape; §20.2) | `MF_P_PORTABLE_ONLY` | its best text with no architecture-specific code: scalar, SWAR, libc, short-span loop-free forms |
| 3 | `native` | always (**`[rev4]`**: `-fmemfn-native` given, or after R4f's flip) | — | its best text, ISA arms included (a gcc-time `#if` ladder under the fixed default token, or one spelling under a declared token, HELD) |

> **`[rev4.2]`** Row 1 is WITHDRAWN (D147, §L.2-§L.3): there is no
> permanent `baseline` profile and no `-fno-memfn-scan`/`-fno-memfn-loop`.
> Two rows remain: `portable` (the SCALAR layer, the SIMD-off reading)
> and `native` (the SIMD layer). `DELEG_SITES` keeps its budget column
> for `MF_P_INLOOP` and loses its deny-bit column. A kit change's OFF arm
> is its own `--memfn-deny=NAME` (**`[rev4.4]`** now `--memfn=no-NAME`).

> **`[rev4.3]`** (addenda 6-7, §R4.3.1) The profile is ONE switch, and
> the table is now:
>
> | # | SIMD | applies when | policy bits sent | what the kit does |
> |---|---|---|---|---|
> | 1 | off | `memfn-simd` not forced (the DEFAULT until R4f, or `-fno-memfn-simd`) | `MF_P_PORTABLE_ONLY` | portable C: plain C, SWAR, libc calls, loop-free short-span forms (Q50); runs on any target |
> | 2 | on | `-fmemfn-simd` (or the default after R4f's ruled flip) | — | hardware-optimized text for a specific CPU, which may or may not run elsewhere. Forms, levels, cascades (§R4.3.2) and fallback are its per-site choice |
>
> "Policy class, not architecture" below still holds. pcrec sends one
> bit and never learns what SIMD-on renders.

`MF_P_INLOOP` is set from the site row's budget (D91 budget 2), never
from a per-call decision. `MF_P_SIZE_LEANING` is set at `--tune` -2/-1,
so D139 item 1's "only if smaller" becomes the kit's rule under that bit
(adding it to the dial is a D103 ruled diff at the first mover, Q32).

The profile names a POLICY CLASS, not an architecture: `portable` means
"no text that names an ISA", which is D122 addendum 3's line ("SWAR is
fine"). pcrec cannot tell what the `native` profile emits on any machine,
and does not need to.

### 8.6 What the kit decides, and how (its internal concern, with its own tests)

The kit's choices are first-match tables of its own (§4.3's C1
classifier and C2 shape tables, requirements.md §2.3's binding-form
table, isa_selection.md §2's ISA table, a plan table over a
predicate's terms), each row with a name and a deny that `--memfn=`
reaches (**`[rev4.4]`**: a row of `memfn/src/options.def`, §R4.4.1).
Where its rows are ordered by MEASUREMENT, the measurement is
the kit's data, generated from transcripts by a `generate.py` beside it
(`third_party/`'s rule, applied inside the kit), with its own `--check`.

The r2 panel's measurement findings are now the kit's charter
obligations, carried into the kit's own design note at R4a:

- **K-1, regime and model.** Every measured comparison names its regime
  (chained vs isolated, hit vs miss, density), and a decision must hold
  in every regime its site can be in (P1, P4). Where a choice rests on a
  model (corner dominance, interpolation), the kit's note names it as one
  and tests it with a fixture that would fail if it were wrong (P3).
- **K-2, protocol constants.** The statistic, the length ladder, segment
  caps and extrapolation are constants in a kit decision record. A
  generator FAILS on capacity overflow and never truncates. A verifier
  samples at alignments and hit offsets the calibration held fixed (P2,
  P7, C-c, C-e).
- **K-3, provenance per arm.** Each measured arm names its box, libc,
  compiler class and flags. The kit's data may be keyed by compiler
  class, and its text may ladder on compiler macros (K2, P6/B4).
- **K-4, verdict-grade boxes.** A native arm whose architecture has no
  verdict-grade timing box (D144 addendum 1: Linux, `taskset`, quiet) is
  not SELECTED over the portable arm on that architecture until one
  exists or Frank admits the Mac (Q31). This is the kit's own rule, so
  pcrec still learns no arch fact.
- **K-5, the kit's own timed control.** The kit's selection among its
  arms is checked by its own timed suite against the scalar byte loop
  and the baseline arm, at its cadence. It is not pcrec's guard, which
  is §10.1 and shares no source with it. **`[rev4.2]`** Against the
  CURRENT scalar arm, not a baseline (D147): a native arm is selected
  only where it beats the current scalar arm past the floor, and is
  re-checked whenever that scalar arm improves.
- **K-6, cascades `[rev4.3]`** (D147 addendum 2, §R4.3.2). A SIMD-on
  site MAY carry several ISA levels with a run-time pick. The kit
  measures the cascade as one of its forms, and selects it only where
  it beats the single-level form at that site (and, as SIMD, the
  current scalar layer). It must name the pick's cost in its regime:
  `__builtin_cpu_supports` costs 0.4-0.6 ns per call on Linux x86, and
  it is wrong on Darwin, where it answers 0 for every feature. A cached
  word cannot be an artifact static (`match_api.md` §5.3). The likely
  first home is budget-1 prefilter sites, x86 first. The carried levels
  appear in the stamp (§R4.3.3).

- **K-7, tuning constants `[rev4.5]`** (D149, §R4.5.1 item 5). Every
  unroll width, block size, short-span cut-over and density or size
  threshold in a kit form is MEASURED (its regime named, K-1), DERIVED
  (from a stated quantity), or LEFT TO THE COMPILER. One that is none
  of these is labelled in place as an unmeasured default (the text
  `UNMEASURED DEFAULT:` at the constant, plus a line in the design
  note). A form that needs a width starts from the plain loop. The
  first label is R-1's `swar` 2x (16-byte) unroll, inherited from
  `ffl`'s 2xVW shape and not measured against 1x or 4x
  (`probes/twins/tb_r4b.c`). A label is a measurement's trigger, not a
  build order (D77).

- **`[rev4.9]` K-6 and K-7, made concrete for the SIMD layer** (§R4.9).
  - K-6: a cascade is a separate row, filed, with its trigger probe
    (§R4.9.3).
  - K-4/K-5: `[r9 M-1]` a SIMD row's acceptance is a pcrec-bench run
    (tier O) on every box that executes its level, at each live `-march`,
    against the SIMD-off compile at the same `-march` AND against the row
    it displaces (§R4.9.5-§R4.9.6); pcrec's G1 in tier U picks what to
    submit. Each row × level × CPU class is recorded in
    `tests/memfn/simd_accept.tsv` with a state, and C19 turns a scalar
    change into STALE lines, never a red.
  - K-7: a SIMD form's vector width and short-path reach are DERIVED
    (`levels.def`, `VW + T`, T = `max_reach`). Its unroll and any cut-over
    above the reach are swept in tier U and labelled MEASURED-UNOFFICIAL
    until a bench reading (§R4.9.5 item 10, `[r9 M-9]`).

None of this reaches pcrec. pcrec's view of all of it is: the code came
back, and its identity gates and bench say what changed.

---

## 9. THE MIGRATION: pcrec's scalar forms become the kit's scalar arms `[rev3]`

### 9.1 The unit, the two commits, and why the kit is live from the first

**The unit of migration is a pcrec EMITTER FUNCTION with every one of its
callers.** No emitter is ever half-delegated, because a form spelled by
the kit at one call site and by pcrec at another is two owners of one
search (D122; memory `pcrec-general-mechanisms-not-special-cases`).
`pcrec_emit_run_compare` has callers in both engines
(`emit_dfa.c:6039`, `emit_vm.c:4483`, `emit_vm.c:8628`), so it moves
with all three.

**Each step is two commits, implement then replace:**

1. **IMPLEMENT.** The kit gains the step's BASELINE arms: a transcription
   of pcrec's text for those emitters, byte for byte, including pcrec's
   local names (each declared in the baseline manifest, §9.2). In this
   commit every PROFILE of those ops answers with the baseline arm,
   because the kit adds no other arm in a migration step. pcrec's
   emitters build the `mf_site` and hooks and call `mf_emit_site`, AND
   still run their own text into a shadow buffer. A SHADOW COMPARATOR
   (an internal check, compiled into this commit only) fails the compile
   loudly if the two differ, on every compile the suite makes.
2. **REPLACE.** pcrec's own text for those emitters and the shadow
   comparator are deleted. pcrec now has no spelling of those searches.

**Zero movers, by construction and by gate.** Because no non-baseline
arm exists yet, the default build emits exactly what it did. That is
what makes the delegation path LIVE at zero movers: unlike revision 2's
R4c stub, whose `kit_applies` logic could never run while every token
answered UNPRICED (r2 C-e), here every delegated site's code really comes
from `mf_emit_site` from the first replace commit on.

### 9.2 The baseline profile: pcrec's last spelling, frozen

> **`[rev4.2]`** Not frozen, and not a profile (D147, §L.2). The arms
> described here are the kit's SCALAR ARMS AS BORN at the step: the
> manifest, the transcription and the pins prove them byte-identical to
> pcrec's pre-migration text AT THAT STEP (the comparator role, kept).
> From the REPLACE commit on they are the live scalar layer, improved by
> kit lanes on SIMD-off acceptance. The "FROZEN" bullet below and the
> "off arm" reading are withdrawn; the pin-not-source independence
> argument now applies per step, and per change through each change's
> own deny (§L.3).

The baseline arms are the kit's record of pcrec's pre-migration text,
one per migrated (emitter, op, handoff) shape. `memfn/baseline/
MANIFEST.tsv` lists, per arm: the pcrec function it was transcribed
from, the commit, the local names it declares (`scan_position`,
`scan_run_length`, `rq_i`, `q` …) and the digest of its rendered text
over a fixed request fixture.

- **It is FROZEN.** A baseline arm changes only by a ruled pcrec abi
  event (Q27). It is the guard's "off" arm (§10.1) and D146's
  revisit-when witness ("measured worse than pcrec's pre-migration
  form"), and both need the pre-migration form to stay reachable and
  unchanged.
- **Its independence is by PIN, not by source.** The baseline text
  lives in the kit, but pcrec's identity gates pin it to the bytes pcrec
  emitted at the step's parent commit (§9.3 I2/I3). A kit edit that moves
  a baseline byte turns them red. So the "off" arm is not computed by the
  thing it controls: it is pcrec's own old output, held in place by
  pcrec's own pins.

### 9.3 The identity gates every step passes

| # | gate | what it proves | shares a source with the kit? |
|---|---|---|---|
| I1 | the SHADOW COMPARATOR (§9.1 commit 1), on every compile of `make test` | kit text == pcrec text for every site the suite reaches, every option, both encodings | no: pcrec's original emitter is the other side |
| I2 | **movers by ID**: every corpus and bench pattern emitted at the step's parent and at the step, diffed byte for byte, at the default, at each `-fno-memfn-*` deny, at every `--tune` position and under `-e utf8`. ZERO movers, by ID (the census discipline every recent abi landing used) | the replace commit moved nothing, including on sites the suite's runs never execute | no |
| I3 | the standing identity gates (the four `.c`-artifact gates, recursion's two-comparison gate, the IR-listing baseline) pass with NO re-pin | the same, through the gates mech already sabotages | no |
| I4 | `PCREC_ARTIFACT_ABI` (`src/gen/emit_dfa.c:52`, 60 at 90d396fd) is unchanged in both commits | a migration is not an abi event; a commit that needs one is not a migration | n/a |
| I5 | the EMITTED-FORM RATCHET (C12, §10.5): pcrec's emitters spell no form the delegation table says is delegated. Born counting the emitted-text `memchr(` calls in `emit_dfa.c`: **9** at 90d396fd (lines 1221, 1247, 5679, 5703, 6153, 6157, 6216, 6218, 8762; comment text excluded), 0 in `emit_vm.c` | a replaced emitter cannot quietly come back as a second spelling | no |

### 9.4 The order: customer first (D77), and what each step moves

> **`[rev4]`** M1 is NARROWED to the closure of its triggering site
> class and SEQUENCED after `lane/k82hbuild` merges and K85's re-measure
> (§16, r3 G-F10/G-F11). M5 moves the MODEL, not a hint (§14.9).

> **`[rev4.3]`** (Q42 REVERSED, D147 addendum 5; §R4.3.4) The paragraph
> below is WITHDRAWN for migration. EVERY search site migrates, M4
> included, with completeness as the trigger: a ruled exception to D77,
> safe because each step is zero-mover. The table's "customer" column
> now names the trigger of the step's first MOVERS, which do still need
> a measured cell. Its `memchr(` column ends at 0 after M4, and M6/M7
> (the strided VM span, N7; N6 RETIRED, D147 add. 12) join it (§22). A CHECKED SITE MANIFEST
> (C17) lists every site as `delegated` or `pending`.

A step is taken when a CUSTOMER needs its sites in the kit (the
customer's trigger is in §12.2), never as a stand-alone refactor. That is
revision 1's Q17 rule, kept.

| step | pcrec emitters that move (all callers) | sites | ops / handoffs | §2.4 fix it carries | customer (trigger, §12.2) | `memchr(` ratchet after |
|---|---|---|---|---|---|---|
| **M1** | `ofs_test_emit_fn`, `ofs_test_emit_pair`, `ofsk_emit_verify` (the ofsskip blocks, T1's offset/run rows AND T2's `<p>_reqrun[_whole]`); `pcrec_emit_run_compare` and `pcrec_emit_runcmp_helpers` (runcmp.c entire: `words`, `overlap`, `bytes`, `memcmp`, all three callers); `pcrec_emit_req_byte_check` with `emit_req_set_rest` (REQ_BYTE, `set-leads`, N4) | OFS, PRE, SETREST, VERIFY, VMRUN | FIND over a conjunction (SET + RUN terms), RETURN; ALL_PRESENT, BOOL; VERIFY, BOOL | (a) the ofsskip `if` becomes the kit's plan (its load-bearing ORDER, r2 R2-S2, is the baseline arm's), (f) N4 | R4d: K82's fused scan+verify | 9 → 3 |
| **M2** | `pf_emit_memchr`, `pf_emit_bcls` and their `-bounded` twins | PF | FIND (one byte; a SET with `table_ref` = `can_begin_match`), RETURN | (e) `dfa_cand_scan` (`emit_dfa.c:6454`) and `pcrec_dfa_cand_ppm` (`:6487`) stop classifying by `strcmp` on row names and read a `DfaPf` field. Owed by ANY new T1-adjacent change, so it rides M2 even if M2 were not a kit step | R4g: PF byte-class | 3 → 1 |
| **M3** | `dir_fwd_skip`, `dir_rev_skip`; `emit_scan_edge`'s LOOP (the `while (more && TEST) advance;` and the counted `scan_run_length` loop; the peeled guard, the accept stores and the state writes stay pcrec's); `vm_emit_span_scan` at stride 1 | STAY, EDGE, VMSPAN (D91 budget 2) | SKIP, ADVANCE, with `member` = T4's spelling and `table_ref` = `stay<K>` / `scan<N>` | (b) and (c); (d) at stride 1 | R4h: in-loop | 1 |
| **M4** | `emit_attempt`'s `(?m)^` skip (N3) | MLINE | FIND one byte, RETURN | — | none. Q30 recommends NOT migrating it until one exists: a lone `memchr('\n')` in pcrec is not architecture knowledge | 1 → 0 if taken |
| **M5** | prefix_k's scan-PLAN selection (below) | OFS, PF | the plan moves; the predicate does not | — | the first mover whose best kit plan differs from `plan_hint` (measured) | — |

**The scan edge ("scan-edge?").** Only its LOOP is a memory function.
The peeled first iteration (the measured t-digits fix, `emit_dfa.c`'s
comment at `emit_scan_edge`), the accept-recording stores and the
fall-through state write are the DFA's own transition semantics. They
stay pcrec's text around the kit's ADVANCE site. A counted span (`{0,n}`)
is passed as a proven `span_hi`, not as a hook.

**prefix_k's measured constants (r2 B2), staged as M5.** `src/opt/
prefix_k.c` does two things:

- it DERIVES the necessary `(offset, byte-set)` facts and the pinned run.
  That is pcrec's semantic knowledge, and it stays (PATFACTS' territory);
- it SELECTS among them, with a cost model over `C_MEMCHR` 6, `C_BITMAP`
  116, `C_VERIFY` 250, `C_ENTER` 2000 (`:65-68`), `C_MISPRED` 1500 and
  the 2x materiality bar: which offset to scan, which to verify, and
  whether the skip is adopted over the offset-0 filter at all. Three of
  those constants are box-measured machine terms (`C_MEMCHR` is glibc's
  AVX2 `memchr`, the C4 allowlist's one code hit at `:45`). That is a
  SCAN PLAN, which D146 puts in the kit.

M1 and M2 move the TEXT only. The plan pcrec's model chose travels as
`mf_pred.plan_hint` plus the conjunction it chose, and the baseline arm
honours it byte for byte. M5, its own step with its own trigger, moves
the PLAN: pcrec passes the FULL necessary conjunction (offset 0
included) with per-term density hints and `consumer = MF_C_ENGINE`, and
the kit's plan table chooses. The five constants and the materiality bar
move into that table as the kit's measured data. `C_ENTER` (what a false
candidate costs the engine) becomes the kit's per-`consumer` term,
measured by the kit's timed suite over pcrec-emitted harness artifacts,
which the tight coupling permits. T1's rows still choose WHAT (which
facts form the predicate), so `RX_DFA_PREFILTER`'s closed value set
(which the bench adapter enumerates) does not split. M5 moves selections,
so it is an abi event with a movers census. At M5 the allowlist's last
code hit leaves `src/` (Q29).

### 9.5 The end state

After M1-M3 (and M5), pcrec's emitters build predicates and hooks, and
`src/gen/runcmp.c` is gone. pcrec spells no libc call, no table walk, no
leapfrog and no masked word compare for a delegated site. The
`memchr(` ratchet reads 1 (N3) or 0. The baseline profile holds
everything pcrec used to spell, frozen. The `-fno-memfn-*` bits reach it
from every site.

> **`[rev4.2]`** The end state per D147: the kit's scalar arms hold
> everything pcrec used to spell, as LIVE code that keeps improving; the
> native arms are a layer on top. No frozen profile exists, and the only
> `memfn` axis is `memfn-native` plus the kit's per-change
> `--memfn-deny=` rows (§L.3). **`[rev4.4]`** Read: `--memfn=no-NAME`
> registry rows (§R4.4.1).

> **`[rev4.3]`** After M1-M7 (and M5/M5′), pcrec spells NO search: C12
> reads 0 in every vocabulary class outside the kit, `(?m)^`'s
> `memchr('\n')` included, and C17's manifest reads 0 pending
> (§R4.3.4). The axis is `memfn-simd` (§R4.3.1).

---

## 10. GUARDS `[rev3]`

Seven guards. G1 is D146's own, independent of the kit. G2 is the
kit's. G3-G7 are pcrec's deterministic checks, and only they carry
sabotage rows (r2 C-d).

### 10.1 G1, D146's guard: pcrec's timing with the kit on vs off

> **`[rev4]`** The population below came from the kit's own `moved`.
> It is replaced by a pcrec-side default-vs-`memfn-off` artifact diff,
> with a declared regime, pooled bins, and a cadence of every memfn abi
> event (§17.2, r3 G-F5/G-F6). armv8 has NO verdict-grade guard (§17.2,
> G-F4).
>
> **`[rev4.2]`** The OFF arm is no longer the baseline profile: it is
> each change's own deny, and every reading is taken in BOTH layers,
> SIMD-off and SIMD-on (D147, §L.4). The bench testee is
> `pcrec[simd]`/`pcrec[no-simd]`, not `pcrec[memfn-off]`.

- **The two arms.** ON is the default profile (`portable` during the
  SIMD hold, `native` after R4f). OFF is `-fno-memfn-scan
  -fno-memfn-loop`, the BASELINE profile: pcrec's own pre-migration
  text, pinned byte for byte (§9.2). Neither arm is computed from the
  kit's data, and the timing is pcrec's own instrument. This is the
  control that shares no source with the kit (D146 "Guard").
- **Alpha, per mover step (D144 item 1).** Every step that adds
  movers (R4d, R4f, R4g, R4h, R4j) times its witness cells ON vs OFF on
  ubuntubudu: `taskset`-pinned, calibrated loops of at least ~50 ms,
  absolute deltas against a base-vs-base floor measured the same way
  (D144 addendum 1). The floor is ON vs ON and OFF vs OFF. A delta inside
  it is NULL.
- **Long subjects and a population (r2 P9, C-a, C-b).** The population
  is EVERY corpus and bench site where `mf_result.moved == 1`, written as
  a manifest by a compile pass and never filtered by an outcome. Its
  subjects are the bench's throughput subjects (at least 1 MiB,
  read-only from pcrec-bench, sha-verified), cut at 16 B, 64 B, 256 B,
  1 KiB, 64 KiB and 1 MiB so the short/long crossover linux_results.md
  found (fusion wins at 64 B and below and loses from about 512 B at
  SSE2 width) is crossed on both sides. Each bin (step, op, length
  decade) that holds a mover needs at least 8 sites, or it prints
  UNREACHED (K35: counted and printed). A mover in an UNREACHED bin is
  reported unverified.
- **Its home.** Alpha: `tests/memfn/guard/run_guard.sh` (opt-in, heavy,
  never in `make test`, run through pcrecdev2's executor channel per
  memory `pcrec-cross-platform-verification`). Batch gate: a pcrec-bench
  TESTEE `pcrec[memfn-off]` beside the default, requested through the
  inbox (D78) at R4d. That request is also option_sets.md §6.1 trigger 3
  (§12.1).
- **The aarch64 arm.** The Mac runs the same script, directional only
  (D144 addendum 1). Since the kit does not select a native arm on an
  architecture without a verdict-grade box (§8.6 K-4), aarch64's ON arm
  under `native` is the portable text until Q31 is ruled. The Mac run is
  then a check that it did not regress, not a verdict that native wins.
  **`[rev4.4]`** Q43 is ruled (D147 addendum 8): SIMD-on forms tuned for
  aarch64 are not ACCEPTED until Frank admits Mac measurements as
  verdict-grade for those cells, or an aarch64 Linux box exists. x86
  Linux gives the verdicts, and the SIMD-off layer is unaffected.
- **The verdict.** A mover whose ON arm is slower than OFF past the
  floor is a D146 revisit-when event. It is filed to the kit's request
  ledger (§11.3) as a defect against the kit's choice. While it is open
  the kit's own deny for that arm (`--memfn=no-NAME`, `[rev4.4]`), or pcrec's budget
  bit, is the interim kill switch (D144 item 4).

### 10.2 G2, the kit's own tests (the kit's business; pcrec only requires that they exist and gate the kit)

- **Exhaustive answers per arm** against the SCALAR BYTE LOOP (never
  against another output of the kit's own generator, §4.5): every
  length 0..256 plus the ladder to 1 MiB, every alignment mod 64, the hit
  at every offset in a block and at none, guard pages on both sides, ASan
  and UBSan. Both architectures: natively, Rosetta 2 for x86 correctness
  on the Mac, and ubuntubudu.
- **The baseline arms** against their manifest digests (§9.2), plus a
  `moved` property test: `moved == 0` iff the rendered text equals the
  baseline arm's for the same request (C11 relies on it).
- **The hook contract** (§8.3): synthetic hooks that read exactly
  `on_cand_reach` bytes at a guard page; impure-expression detection by
  rendering each hook expression as a counter-increment macro and
  asserting nothing depends on its evaluation count.
- **The agreement check** (§3.4, kept): the kit's own set-shape analysis
  against `pcrec_cls_cube`'s over every class the corpus produces, by the
  256-point exact membership check, and against T4's `member` spelling
  per set.
- **Cross-target syntax of every arm it can emit** (r2 B5, kit side):
  each arm compiled `-fsyntax-only` per target it names (gcc and clang
  natively, clang `--target=` for the other architecture with its own
  headers).
- **The kit's timed suite** (§8.6 K-5) and its data's `--check` (K-2), at
  the kit's cadence.

`make test` runs the kit's QUICK tier (correctness, a bounded length
range); the exhaustive tier is `make -C memfn test-full`, part of the
batch gate.

- **`[rev4.1]` Arm-differs property** (r3 addendum C3-2). For every
  non-baseline arm, on its own fixture sites, the arm's rendered text
  differs from the baseline arm's. It is what lets §18.2 assert only
  `none` ⇒ identical and still trust a non-`none` stamp as naming a
  rendered non-baseline arm.

### 10.3 G3, the abi ritual for kit versions (r2 K1/D1, carried)

- **Any kit change that moves ANY byte pcrec emits is a pcrec `abi`
  event in the SAME commit**: `PCREC_ARTIFACT_ABI` bumped, every reader
  found by D94's grep, the identity gates re-pinned, a `docs/spec/`
  hunk (D80), and the movers-by-ID census (§9.3 I2's tool) attached.
  In-tree (§11.1) this is one commit by construction. After an
  extraction it is the vendor-bump commit.
- **Detected without trusting the kit**: the standing identity gates
  compare pcrec's output against pinned bytes, so a kit edit that moves
  pcrec bytes with no bump turns them red. The kit's version string is
  not what is checked; the bytes are.
- **`[rev4]` WITHDRAWN, the next bullet.** It contradicts Frank's Q3
  ruling on `litscan_k82h.md` and D81 (r3 G-F1). The stamp now goes on
  EVERY artifact, `none` where no site is delegated, and carries no kit
  version. It is born in its own abi event (§18).
- **The stamp, on movers only** (k82hrev Q3's precedent): an artifact
  with at least one site whose `mf_result.moved == 1` carries
  `<PREFIX>_MEMFN "<kit version>"` and `<PREFIX>_MEMFN_FORMS
  "<form_id>,…"` in site order. An artifact with none carries neither, so
  the zero-mover migration adds no byte. Re-measuring or re-tuning
  inside the kit that moves a selection moves text, so it is covered by
  the same rule. There is no separate "recalibration" event (rev 2's
  Q20 dissolves).
- **`rx_info` is unchanged** until a consumer asks for the kit version in
  the struct (D77).

### 10.4 G4, the arch-blindness detector, rebuilt (C4; r2 B1)

> **`[rev4]`** The plant's "held out" claim is narrowed to what it can
> support, and matching is case-insensitive (§17.5, r3 G-F7).

pcrec carries no architecture knowledge (Q12's refinement, D146). C4
makes that a red test, with the r2 panel's rebuild:

- **Seven vocabulary classes, one pattern each, with explicit
  boundaries** (`\b` fails between `_` and a letter, so `MF_VEC_SSE2`
  slipped past rev 2's regex): (1) ISA names and levels; (2) predefined
  arch macros (`__SSE*__`, `__AVX*__`, `__aarch64__`, `__ARM_NEON*`,
  `__ARM_FEATURE_*`, `__x86_64__`, `_M_X64` …); (3) intrinsics and
  vector types (`_mm*_`, `__m128*`, `vld1q_*`, `vqtbl*`,
  `__builtin_ia32_*` …); (4) intrinsic headers (`*intrin.h`,
  `arm_neon.h`, `arm_sve.h`, `cpuid.h`); (5) targeting (`target("…")`,
  `-march=`, `__builtin_cpu_supports`, `getauxval`, `HWCAP`,
  `hw.optional`, `cpuid`); (6) arch nouns (`x86_64`, `amd64`,
  `aarch64`, `arm64`, `pshufb`, `movemask`, microarchitecture names);
  (7) kit-identity compares: `strcmp`/`strncmp`/`memcmp`/`==` with an
  operand naming `form_id`, `mf_kit_version(` or the `--isa=` token.
- **Two delegation classes, new in rev 3.** (8) pcrec reading kit
  OUTPUT: any `mf_sink` read-back, or a string search over a buffer the
  kit wrote, under `src/`. (9) the include graph: `src/`, `cli/` and
  `lib/` include only `memfn/include/memfn.h` from the kit, never an
  internal kit header (the precedent is `analyze/`'s link-nothing rule,
  inverted).
- **Positive controls, one per class**, planted in a scratch copy and
  required to hit. The plant vocabulary is HELD OUT from the regex's
  source: derived at check time from the compiler's own installation
  (`cc -dM -E` under each owned target, intrinsic names scraped from its
  headers). That list was never chosen by the regex's author
  (learnings.md §3, R8's lesson).
- **A negative control** for the one known false-positive class: hex
  escapes (`\x86` in `.rxt` subjects), excluded by rule.
- **Scopes**: the code of `src/`, `cli/` and `lib/` (allowlist counted at
  birth, D107's shape); the CLAUDE.md files inside them (allowlisted
  rows); `tests/` (its own allowlist, so a NEW test that branches on an
  architecture is visible). `memfn/` is EXEMPT: it is where architecture
  knowledge is supposed to live.
- **Born counts.** An unmerged and superseded lane (`memfnk0r3`)
  measured these classes at b7542fbe: code 1 hit (`src/opt/prefix_k.c:45`,
  "AVX2" in a measurement comment), `src/` docs 1 (`src/gen/CLAUDE.md`,
  "an x86 slot", in the sentence stating the ISA-neutral rule), `tests/`
  15 hits in 10 files (box descriptions, the `R_X86_64_*` relocation
  names `tests/codegen/run_scan_edge_dispatch.sh` parses, a Linux library
  path). C4's build lane re-takes the census and commits it as the
  allowlist; M5 removes the code hit.

### 10.5 G5-G7, pcrec's other deterministic checks

> **`[rev4]`** C5 pins per-ARM digests under `tests/memfn/pins/`
> instead of whole artifacts at the parent (§17.4, r3 F12/G-F8). C9 gains
> a header shim, a native-enabled configuration and a K35 floor (§17.3,
> G-F3). C11 checks the stamp's VALUE on every artifact (§18). C13 (on_cand
> duplicability) and C14 (shape bounds) are new (§14.6, §14.7).
>
> **`[rev4.2]`** C5's first half (`memfn-off` identical to the baseline
> pin) is replaced by the PER-CHANGE COMPARATOR: at a kit change's own
> commit, the corpus at that change's `--memfn=no-NAME` (`[rev4.4]`) is identical
> by ID to the parent's default (§L.3). C5's second half (no ISA
> vocabulary at `-fno-memfn-native`) stays. C11's reference compile is
> `-fno-memfn-native` (§L.5). C6's arms are `memfn-native`'s two
> spellings plus the kit's published switches.
>
> **`[rev4.3]`** Read `memfn-native` as `memfn-simd` throughout
> (§R4.3.1). C9 runs at `-fmemfn-simd`. C11 checks both stamp lines
> (§R4.3.3): `MEMFN_FORMS` against the `-fno-memfn-simd` compile, and
> `MEMFN_LIBC` against a pcrec-side text scan for the C9 shim's
> declared functions. C12's ceiling descends to 0 (§R4.3.4). **C17 is
> new: the checked site manifest** (`tests/memfn/site_manifest.tsv`).
> It fails on an emitter spelling a C12-vocabulary search form in a
> function no `pending` row names, on an `mf_emit_site` site with no
> `delegated` row, on a delegated row whose emitter still spells a
> form, and on a pending row whose emitter spells nothing. Its counts
> are printed under a K35 floor. It shares no source with the kit:
> the manifest and the vocabulary are pcrec's.
>
> **`[rev4.6]`** (r5 B3, B4) C11's row below says "the movers by ID
> are non-`none`". That holds for the SIMD-ON population only. At the
> default build (SIMD off until R4f) the artifact IS its SIMD-off
> compile, so the diff is empty and every value is `none`, R4d's
> SIMD-off movers included. So C11's FORMS half is declared UNREACHED
> (K35), not passed, until the first SIMD-on form exists (R4e′), as
> the registry floor is until R4d. Its presence half and its `none`
> implies identical half run from R4a′. C11's `MEMFN_LIBC` half takes
> Q53's refined control (§R4.3.3): names from the compile, not from the
> shim's list.

| # | check | what it proves | shares a source with the kit? |
|---|---|---|---|
| C5 | **profile identity**: the corpus at `-fno-memfn-scan -fno-memfn-loop` is byte-identical to the BASELINE pin (the step parent's output); at `-fno-memfn-native` it carries no text the C4 classes 1-4 match (a scan of the EMITTED artifacts, the one place pcrec may grep generated code for vocabulary, because it is checking the kit's promise, not branching on it) | the off arm is what G1 says it is; `portable` is portable | no |
| C6 | answer identity per deny, per box: `make test-axes` arms for the three bits, plus option_sets.md §3.5a's compile-only arms per declared token when R4i builds tokens | correctness under every profile | no |
| C9 | **cross-target syntax, pcrec side** (r2 B5): every corpus artifact with at least one mover, each `#if` arm compiled `-fsyntax-only` per the arm's target (Mac: gcc-16 natively, clang `--target=x86_64-linux-gnu`; ubuntubudu: gcc and clang natively, clang `--target=aarch64-linux-gnu`). The number of arms compiled per artifact is printed and must equal the count the kit reports in `mf_result` (K35). A Rosetta 2 run executes the x86 arm under C6 | the arms no box compiles natively at least parse and type-check, inside real artifacts | no |
| C10 | **site table and stack**: `DELEG_SITES`' budget column matches D91's classification (budget 1: PF, PRE, OFS, SETREST, VERIFY, MLINE; budget 2: STAY, EDGE, VMSPAN, VMRUN); `MF_P_INLOOP` is set only from that column; its op column passes `mf_vocab_has`; no `mf_site`, `mf_pred` or `mf_result` is an automatic variable under `src/` (r2 K3) | an in-loop site cannot ask for an out-of-loop arm; no large request on an emitter stack | n/a (structural) |
| C11 | **stamp census** `[rev4.1]`: every artifact carries `<PREFIX>_MEMFN_FORMS`; `none` implies identical to `memfn-off` (§18.2), the movers by ID (§9.3 I2's tool) are non-`none`, and every form id is one the kit's `moved` reported | **`[rev4.1]`** a `none` on a mover, or a non-`none` id naming no rendered non-baseline arm (§18.2) | partly: `moved` is the kit's, so G2's `moved` property test is the other half |
| C12 | **the emitted-form ratchet** (§9.3 I5): emitted-text `memchr(` calls, table-walk loop texts and runcmp row texts in pcrec's emitters, counted against a committed ceiling that only descends | no replaced form comes back as a second spelling | no |

### 10.6 The spec states the limits (D80)

At R4d's mover, `docs/spec/` gains the kit's contract as a caller sees
it: the `-fno-memfn-*` bits and `--memfn-deny=`, the stamps, the
profile semantics (the baseline is pcrec's pre-migration text), and
three limits. (1) The kit's choices are measured under gcc, pcrec's
target compiler; another compiler gets correct code whose speed was not
the one measured (r2 K2). (2) Where the kit calls libc, its choice was
measured against glibc and libSystem; musl inherits it (rev 2's Q22, now
Q33). (3) Injected intrinsics headers are compiler-provided (r2 L1).

> **`[rev4.2]`** The profile semantics the spec states are D147's two
> layers (`-fno-memfn-native`: the scalar layer, no ISA text;
> `-fmemfn-native`: the SIMD layer on top) and the per-change
> `--memfn-deny=` switches, not a baseline.

> **`[rev4.3]`** (addenda 6-7) The spec states the switch's MEANING:
> - `-fno-memfn-simd`, the default until a ruled flip, gives portable C
>   that runs on any target (plain C, SWAR, libc calls);
> - `-fmemfn-simd` gives text optimized for a specific CPU that MAY NOT
>   EXECUTE ELSEWHERE, with no portability promise.
>
> It also states both stamp lines' grammar, including `MEMFN_LIBC` as
> the record of libc's own dispatch. The SIMD-on half lands at R4e′
> (D80), the stamp half at R4a′.

> **`[rev4.4]`** (addenda 8-9) The spec also states:
> - the kit's option namespace: `--memfn=` is passed through
>   uninterpreted, the kit validates it, and `--list-axes` lists its rows
>   as the `memfn` section, whose member-count floor the spec pins
>   (§R4.4.1);
> - Q45's second limit, in the spec as ruled: the kit's libc choices
>   were measured against glibc and libSystem, and musl inherits them;
> - Q43: SIMD-on forms tuned for aarch64 are unmeasured at verdict
>   grade and not accepted (§17.2).

### 10.7 Sabotage rows (deterministic detectors only; ids at build, highest S on main + 1)

> **`[rev4]`** Replaced by §17.6. Every row is mech-runnable from a
> `git archive` (no history), its detector reads pins under `tests/`, and
> each carries `SAB_REACH` (r3 G-F8).

| sabotage | detector |
|---|---|
| one baseline arm edited by one byte | I3 / C5 (the baseline pin) |
| a kit text change that moves a pcrec byte, with no abi bump | the standing identity gates (G3) |
| an ISA word added to `src/gen/emit_dfa.c`, one row per C4 class, drawn from the held-out list | C4 |
| `#include "memfn/src/…"` (an internal kit header) in `src/` | C4 class 9 |
| a `strcmp` on `form_id` in `src/` | C4 class 7 |
| a site's INLOOP bit dropped from `DELEG_SITES` | C10 |
| `moved` forced to 0 on a mover | C11 (the stamp census disagrees with the byte census) |
| a replaced `memchr(` text re-added to an emitter | C12 |
| the kit's guard established one byte short (`cand + reach < n` off by one) | G2's guard-page hook test (the kit's own mech row) |
| a `-fno-memfn-native` arm emitting one intrinsic | C5 |

---

## 11. COUPLING LIKE THE BENCH: home, licence, requests, name `[rev3]`

### 11.1 Where the code lives first: in-tree `memfn/` (recommended, Q25)

> **`[rev4]`** `analyze/` is the INVERSE precedent (a leaf binary that
> links nothing). The kit links INTO libpcrec, so its symbols ship in
> `libpcrec.a`. §20.3 adds the symbol policy and per-file provenance
> (r3 G-F14).

- **A top-level, zero-dependency subtree, on `analyze/`'s precedent**:
  `memfn/` with its own Makefile, tests, CLAUDE.md, LICENSE and README.
  It links nothing from `src/`, `cli/` or `lib/`. pcrec's compiler links
  the kit (it is an emit-time library), and pcrec's sources reach it only
  through `memfn/include/memfn.h` (C4 class 9). Generated artifacts never
  depend on it: what reaches them is TEXT, so self-containment holds.
- **Why in-tree first.** Three reasons, the third decisive:
  1. The API is unsettled until M1 has run; two repositories double the
     cost of every change to it (revision 1's §3.3 item 4, kept).
  2. The scope mandate needs no extension: `memfn/` is inside the pcrec
     repository.
  3. **Atomicity.** A kit change that moves pcrec bytes MUST land with
     its abi bump and re-pins (§10.3). In one repository that is one
     commit and the identity gates see both halves at once. Across two
     it is a vendor bump that can be split, delayed or reverted out of
     step.
- **Extraction** to its own repository `pcrec-memory-functions` happens
  when a second consumer appears (a K3 CLI user, another project) or
  Frank rules it. **`[rev4.2]`** Q36 RULED a narrower, MEASURED
  trigger: a stable API across several migration steps AND a real
  second consumer (§23). It needs a SCOPE-MANDATE EXTENSION: the root
  CLAUDE.md's MANDATE names exactly two repositories, and pcrec-bench
  joined it by Frank's ruling (2026-08-17). After extraction pcrec reads
  a pinned vendored copy, `third_party/pcrec-memory-functions-<ver>/`,
  with a PROVENANCE.md naming what derives from it (every delegated site
  of every artifact), and `third_party/README.md`'s "nothing here
  reaches a generated artifact" sentence gains the kit's row beside
  `utf8_fold_pairs.inc` (r2 K5).

### 11.2 Licence (Q26)

The kit's text is injected into users' artifacts, so D145's
consequence binds it: 0BSD, CC0 or Unlicense, or a licence with its own
output exception. **Recommended: 0BSD for the whole kit**, the simplest
licence on D145's list. The planned translation of Rust `memchr`
(Unlicense OR MIT, survey.md) is clean under it. Compiler-provided
intrinsics headers are #included by injected text, never copied into it,
and the spec says so (§10.6).

### 11.3 How pcrec asks for new kit work (Q34)

> **`[rev4]`** One shared file breaks D78's single-writer rule (r3
> G-F13). Two files from day one, with the manager the sole writer of
> requests (§20.1).

**Now (in-tree): a request LEDGER, `memfn/docs/requests.md`.** Numbered
items, never deleted, on D78's shape:

- pcrec's side (the manager, or a pcrec lane through the manager) files
  `R-n`: the customer row, the measured cell that is the D77 trigger, and
  the SEMANTIC operation wanted (a new op, handoff or term kind, or a
  compound shape from §8.4's last row). It never names an ISA or a
  kernel.
- the kit's side (a kit lane) appends `ack:` with its plan, then
  `done:` with the `MF_VOCAB` value that carries it and the kit commit.
- a G1 revisit-when event (§10.1) is filed the same way, as `D-n`
  (defect against a kit choice), with its timing transcript.

It is a FILE rather than messages because kit lanes run asynchronously
and a request must survive a session boundary (memory
`pcrec-lane-hold-lift-artifact`). It is ONE file while both sides share
one repository and one manager. **At extraction** it splits into D78's
pair in the kit's repository (`inbox_from_pcrec.md`, written only by
pcrec's manager; `outbox_to_pcrec.md`, written only by the kit's), single
writer each way, live coordination interprocess. That is exactly the
pcrec-bench arrangement, and the reason for waiting is that until there
are two sessions there is nobody to be the second writer.

**Lanes.** Kit work is ordinary lane work (D86's feature type), briefed
with the scope mandate. A kit lane whose change moves pcrec bytes
carries the pcrec abi ritual in its own delivery (§10.3). The kit's
priorities are pcrec's requests first (it exists to serve them, as the
bench does), its stand-alone K3 product second.

### 11.4 The name

- Project, README, repository-to-be and `mf_kit_version()`'s string:
  **pcrec-memory-functions**.
- Directory `memfn/` (short, and already the design record's name,
  `docs/design/memfn/`). C prefix `mf_` / `MF_`. pcrec's option family
  `memfn`: `-fno-memfn-scan`, `-fno-memfn-loop`, `-fno-memfn-native`,
  `--memfn-deny=`. Revisions 1-2's `kit` flag spellings are withdrawn,
  because "kit" also names D122's compare-stack kit and clskit.
- In prose, "the kit" stays.

> **`[rev4.4]`** The option family is ONE pcrec axis, `-fmemfn-simd`,
> plus the kit's own `--memfn=` (§R4.4.1). The three bits named above
> are history (§R4.3.1, §R4.3.6).

---

## 12. option_sets.md, the build order, and the plan-row text `[rev3]`

> **`[rev4.2]`** §12.1's three deny bits and the `memfn-off` set are
> withdrawn (D147, §L.3, §20.2's annotation): family `memfn` is `auto` /
> `simd` / `no-simd`, and §6.1's first trigger is the bench's
> `pcrec[simd]` testee at R4e′, not a kit-off testee.

### 12.1 What rev 3 changes in option_sets.md

| option_sets.md item | revision 3 |
|---|---|
| §1.2 vector-row denies (`-fno-vec-scan`, `-fno-vec-skip`, `-fno-vec-run`, `-fno-swar-scan`); rev 2's `-fno-kit-scan/-loop/-native` | **three bits**: `-fno-memfn-scan` (budget-1 sites to the baseline profile), `-fno-memfn-loop` (budget-2 sites to baseline), `-fno-memfn-native` (the portable profile; DEFAULT ON during the SIMD hold). Named for D91's budgets and a policy class, never an ISA. Bit numbers are taken at landing (the next free; 47-49 if k82hand's bit 46 has landed) |
| §1.2 `--memfn-deny=` | kept, passed through UNPARSED: pcrec cannot spell a kit row (**`[rev4.4]`** now `--memfn=`, the kit's own registry, §R4.4.1) |
| §1.2/§4.3 the `isa` family (poset), `isa-route`, `-fisa-check`, `-fisa-dispatch`, `--isa-marker` | as rev 2's cross-note: ONE opaque value axis (`--isa=`, passed through), the route folded into the token, constraint rows 6-8 removed. All of it HELD with R4i |
| §4.2 the `vector` family (`auto` / `simd` / `no-simd` / `scalar`) | **family `memfn`**: `auto` (∅: the defaults), `simd` (`memfn-native := allow`: a caller's opt-in to native arms before the R4f flip; a conflict with a set that denies it is refused by name, as before), `no-simd` (`-fno-memfn-native`), `memfn-off` (`-fno-memfn-scan -fno-memfn-loop`: the D146 guard's off arm and the bench's off testee). `scalar` dissolves: "one byte at a time" is not a profile any more; the nearest thing is `memfn-off`, pcrec's old forms, which already include libc `memchr` |
| §4.2's `vector` × `isa` interaction table | gone: both are inputs of one kit request, and the kit's code is the whole answer |
| §3.5's sweep | three deny arms per box (C6); compile-only arms per declared token only at R4i |
| §6.1 trigger 1 (one name over two or more bits, plus a consumer) | met by `memfn-off` (two bits) the day pcrec-bench takes the `pcrec[memfn-off]` testee (§10.1). That request is ALSO trigger 3. So the first option-sets build is likely this one |
| §6.1 trigger 2's predicted first disagreement (rev 1's Q16: a size position denying `vec-scan`) | dissolves: a size-leaning `--tune` position sends `MF_P_SIZE_LEANING` to the kit (§8.5) rather than denying anything, so no set disagreement arises (Q32) |

The cross-note at the top of option_sets.md is updated in this lane's
delivery to point here.

### 12.2 The build order, revision 3

> **`[rev4]` SUPERSEDED by §22** (r3 G-F10/G-F11/G-F12): R4a-R4j are
> re-derived with the stamp's own event, M1 narrowed and sequenced, and
> R4f's circularity broken.

It replaces rev 2's R4a-R4h. Each step names its PREREQUISITE (a step
that must have landed) separately from its TRIGGER (a measured cell or a
ruling, never a step's mere completion; r2 R3). Nothing that moves an
emitted byte opens before its trigger (D77), and native text stays under
the SIMD hold until R4f (D91, D119).

> **R1d REVISION 3 DELIVERED 2026-10-05 (lane memfndel): `docs/design/memfn/integration.md` rev 3** — D146's DELEGATION model designed out: pcrec describes a SITE (`mf_site`: an op over a conjunctive predicate of byte-set/masked-run terms at offsets, proven span, anchoring, density hints, a policy word) and the kit writes its code through TEXT hooks (subject, read limit, bounds, result, cursor/step, per-candidate verify, T4's one-position spelling, pcrec's table names). pcrec decides only WHICH SITES are delegated (by op type: `DELEG_SITES`) and WHICH PROFILE each gets (first match: `baseline` under `-fno-memfn-scan`/`-loop` = pcrec's frozen pre-migration text, `portable` under `-fno-memfn-native` = default during the SIMD hold, `native`). Compound work = the predicate algebra + ALL_PRESENT + ON_CAND + a request ledger. Migration M1-M5 by customer, each implement (shadow comparator) then replace, zero movers by ID, a `memchr(` ratchet born at 9. Guards: D146's on/off timing (alpha + a `pcrec[memfn-off]` bench testee), the kit's exhaustive tests, the abi ritual for any kit byte move (stamp on movers), C4 rebuilt (7+2 classes, held-out plant), C9 cross-target syntax, C5-C12. In-tree `memfn/` first, 0BSD, name pcrec-memory-functions. r2 findings: 11 carried, 7 moved inside the kit, 3 dissolved, 2 split. Q24-Q34 open.
> - **R3** (rulings): Q24-Q34. Nothing owed on Linux beyond R4b's probe.
> - **R4a, the kit's skeleton in-tree** (`memfn/`): `memfn.h` with `MF_SITE_ABI`/`MF_VOCAB`, `mf_emit_site` over an EMPTY baseline set, K1 primitives and F1/F2/F3/F5/F6 reference functions with G2's exhaustive tests on both architectures, LICENSE (0BSD), CLAUDE.md, `docs/requests.md`. pcrec links it and calls nothing. No emitted byte moves. **Prerequisite:** none. **Trigger:** Frank's Q24/Q25 ruling.
> - **R4b, the first customer's measurement** (probe only, `probes/twins/`): twins.md T-B re-run on Linux ON THE POST-HANDOFF BUILD, with a PORTABLE (SWAR) fused pair-filter variant beside `emit` and the vector `ffl`, on the K82 cells (union-select, userpass, mod-i; gate, sweep, short). **Prerequisite:** none. **Trigger:** the K82 handoff (`lane/k82hbuild`, litscan_k82h.md) merged and alpha-accepted, because the handoff removes the second scan and T-B's twin must be measured against what remains (r2 R2).
> - **R4c, M1: OFS / PRE / SETREST / VERIFY migrate, zero movers** (§9.4): the ofsskip blocks, runcmp entire, the pre-check and N4, implement then replace, I1-I5 green; the three deny bits land (baseline == default, so C5 is live and vacuous-by-identity); `DELEG_SITES`, C4, C10, C12. **Prerequisite:** R4a. **Trigger:** R4b shows the PORTABLE fused form beating `emit` past the D144 floor on at least one K82 cell. If only the vector form wins, M1 waits for R4f's trigger instead.
> - **R4d, the first movers: the kit's portable fused conjunction arm at OFS/PRE**: abi bump, `<PREFIX>_MEMFN[_FORMS]` on movers, the `docs/spec/` hunk with §10.6's limits, C5/C6/C9/C11 live, sabotage §10.7, G1's alpha on the K82 cells; the bench `pcrec[memfn-off]` testee requested (D78 inbox). `MF_P_SIZE_LEANING` on the dial if Q32 rules it. **Prerequisite:** R4c. **Trigger:** R4b's cell (the same measurement: the step that moves bytes is the one it justified).
> - **R4e, ON_CAND's first customer** (a verify the predicate cannot express, iterated in place): **Trigger:** a measured cell where a candidate's verify is not a byte-set/run conjunction and the restart per hit dominates (twins.md T-A's "iterate in place" lever on a real site). Filed until then.
> - **R4f, the native default flip** (`-fno-memfn-native` default OFF): its OWN ruled event (r2 R1, Q28), never a side effect of a kit release. **Prerequisite:** R4d. **Trigger:** `[OPT-SIMD]` opened (D119: SIMD last; `[rev4.9]` superseded, D147 add. 11) AND a Linux alpha where the native arm beats the portable arm past the floor on a mover cell.
> - **R4g, M2: PF migrates, then PF movers** (`pf_emit_memchr`, `pf_emit_bcls`, the `-bounded` twins; §2.4 e's `strcmp` readers fixed in the M2 commit). **Prerequisite:** R4c. **Trigger:** U-2 (the bench class-shape census, relayed to pcrecdev2) AND a Linux cell whose time is in `pf_emit_bcls` (the WAF `byte-class` cells, compare_stack.md §6.3).
> - **R4h, M3: in-loop sites migrate, then in-loop movers** (STAY, the scan edge's loop, VMSPAN at stride 1; `MF_P_INLOOP`). **Prerequisite:** R4c. **Trigger:** U-3 (an in-loop probe at a real emitted site, D91 budget 2 re-measured, never inherited) AND a Linux cell dominated by class runs.
> - **R4i, declared tokens (`--isa=`):** HELD. **Trigger:** isa_evaluation.md L-1/L-2, answered "no customer now" by linux_results.md §5.
> - **R4j, M5: the scan PLAN moves into the kit** (prefix_k's selection and constants; §9.4): an abi event with a movers census; the C4 code hit leaves. **Prerequisite:** R4c (and R4g for PF). **Trigger:** a mover whose kit plan differs from `plan_hint` and whose G1 alpha beats the hinted plan past the floor (Q29).
> - **Filed, not scheduled:** M4 MLINE (Q30); a fused ALL_PRESENT arm for N4 (a cell on the K65 no-DFA-scan route whose time is in `emit_req_set_rest`); an ordered FIND_SEQ op and F8 `mismatch` (each by request with a cell, §11.3); N6; the stay set through T4 (a `[CLS-TREE]` follow-up, §2.4 b); extraction (§11.1).

---

## 13. Questions for Frank `[rev3]`

> **`[rev4]` SUPERSEDED by §23** (Q35-Q49). Q24-Q34 are re-derived
> there; §23.1 maps each.

Renumbered from Q24 (rev 2 ended at Q23; the unmerged price-model draft
`memfnk0r3`'s Q24-Q30 were never delivered and are void). Each has a
recommendation.

24. **Q24, the contract.** Adopt §8 as the design of record: `mf_site`
    (an op over a conjunctive predicate plus proven facts and a policy
    word), the text-hook contract with its eight rules, compound work as
    the predicate algebra plus ALL_PRESENT and ON_CAND, totality (a kit
    decline is a kit defect), and pcrec's two tables (`DELEG_SITES` by op
    type; the profile first-match). **Recommendation:** yes.
25. **Q25, where the kit lives.** In-tree `memfn/`, zero-dependency,
    extracted to `pcrec-memory-functions` when a second consumer appears
    or you rule it (a scope-mandate extension then). **Recommendation:**
    in-tree; the decisive reason is that a kit change and its pcrec abi
    bump must be one commit (§11.1).
26. **Q26, the licence.** **Recommendation:** 0BSD for the whole kit
    (D145's list), replacing rev 1's split recommendation (0BSD for K1,
    MIT plus exception for K2/K3).
27. **Q27, the deny bits and the baseline.** Three bits
    (`-fno-memfn-scan`, `-fno-memfn-loop`, `-fno-memfn-native`), with the
    budget bits selecting the BASELINE profile: pcrec's own pre-migration
    text, held by the kit and FROZEN, changed only by a ruled abi event.
    **Recommendation:** yes, and keep the baseline forever: it is D146's
    guard's off arm and the revisit-when witness, and it costs only the
    text it already is. **`[rev4.2]`** Superseded twice: by Q38, and
    then by D147, under which the baseline is a per-step comparator
    only (§L.2).
28. **Q28, the default during the SIMD hold.** `-fno-memfn-native` is ON
    by default, so the default profile is `portable` (scalar, SWAR, libc,
    loop-free short paths: D122 addendum 3's line). The flip to `native`
    is R4f, its own ruled event. **Recommendation:** yes.
29. **Q29, prefix_k's measured constants (r2 B2).** The k-set
    DERIVATION stays pcrec's; the scan PLAN (which term to scan, which to
    verify, whether to adopt the skip) and its five constants move into
    the kit at R4j, behind a measured trigger. Until then pcrec's pick
    travels as `plan_hint` and the baseline honours it. **Recommendation:**
    yes. Alternative: rule the plan pcrec's forever, which keeps
    box-measured terms (and the C4 allowlist's code hit) in `src/`.
30. **Q30, migrate without a customer?** M4 (the `(?m)^` `memchr('\n')`,
    N3) has no customer. **Recommendation:** no; leave it until one
    exists. A lone libc call in pcrec is not architecture knowledge, and
    the ratchet (C12) keeps it at one.
31. **Q31, the aarch64 verdict box.** D144 addendum 1 makes Mac timings
    directional, and no house aarch64 box gives verdict-grade numbers.
    **Recommendation:** the kit does not SELECT a native arm over its
    portable arm on an architecture with no verdict-grade box (§8.6 K-4),
    so aarch64 runs portable text under `native` until you either admit
    the Mac per cell (quiet window, D144's loop protocol, the kit's own
    timed suite) or a Linux aarch64 box exists. pcrec still learns no
    arch fact: the rule is the kit's.
32. **Q32, the dial.** `--tune` -2/-1 send `MF_P_SIZE_LEANING`, and the
    kit applies D139 item 1's "only if smaller" under it. That changes
    what two pinned positions mean, so it is a D103 ruled diff.
    **Recommendation:** rule it at R4d, with the movers census showing
    what it moves at those positions.
33. **Q33, the libc the kit measured (rev 2's Q22).** Where the kit
    chooses a libc call, it measured glibc and libSystem; musl inherits
    the choice. **Recommendation:** accept and state it in `docs/spec/`
    at R4d (§10.6). A libc-qualified request is the general form, built
    only for a measured customer.
34. **Q34, the request channel.** A numbered ledger in-tree
    (`memfn/docs/requests.md`) now; D78's single-writer inbox/outbox pair
    at extraction. **Recommendation:** yes.

### 13.1 Every earlier question, mapped

| old | status under rev 3 |
|---|---|
| Q12 (the boundary) | RULED (rev 2, with K0), then superseded by D146. K1-K3 survive as the kit's internal layering |
| Q13 (home) | becomes Q25 |
| Q14 (licence) | becomes Q26 |
| Q15 (deny bits) | becomes Q27 |
| Q16 (ladder bytes) | DISSOLVED: code bytes are the kit's concern, and `MF_P_SIZE_LEANING` hands it the dial's intent (Q32) |
| Q17 (promoting the seven sites) | kept as a RULE, not a question: promotion rides a customer (§9.4); §2.4(e) rides M2 regardless; §2.4(b)'s first half stays filed as a `[CLS-TREE]` follow-up |
| Q18 (the fixed `portable` default token) | carried unchanged; HELD with R4i |
| Q19 (the Mac as a calibration box) | replaced by Q31 (no calibration crosses the boundary; the question is now which box gives the kit verdicts) |
| Q20 (recalibration governance) | DISSOLVED: any kit change that moves a pcrec byte is an abi event (§10.3); there is no separate recalibration event |
| Q21 (the route in the token) | carried unchanged; HELD with R4i |
| Q22 (whose libc) | becomes Q33 |
| Q23 (K0 against the K82 ruling) | DISSOLVED: pcrec does no cost comparison at all |
| requirements.md Q1-Q3, isa_selection.md Q4-Q6, isa_evaluation.md Q7-Q11 | unchanged by rev 3, except that every dispatch or ISA choice they discuss (Q5's hybrids, Q4/Q7's levels) is now made INSIDE the kit; pcrec's only ISA surface is the held, opaque `--isa=` |

---

## 14. THE CONTRACT, REVISION 4: shapes read off the emitters `[rev4]`

Revision 3's §8 stands as the PRINCIPLE: pcrec says what is searched,
where and under what proof, and the kit decides how. This section
extends the SHAPES so that every site `src/gen/` writes today can be
described in them, and so that a baseline arm can reproduce that site
byte for byte (§15 does it for every M1 shape). Sources, read at main
`1c2ba975`: in `emit_dfa.c`, the pre-check (`emit_req_run_check`,
`emit_req_set_rest`, `emit_req_one_byte`, `pcrec_emit_req_byte_check`),
the run blocks (`req_run_tests`, `pcrec_emit_req_run_blocks`), the
offset-skip trio (`ofsk_emit_verify`, `ofsk_emit_params`,
`ofs_test_emit_pair`, `ofs_test_emit_fn`, with `pf_tables_ofs` and
`pf_block_ofs`), the PF forms (`pf_emit_memchr[_bounded]`,
`pf_emit_bcls[_bounded]`, `pf_emit_ofs[_bounded]`), the stay skips
(`dir_fwd_skip`, `dir_rev_skip`), the scan edge (`scan_test`,
`emit_scan_edge`), the `(?m)^` skip (in `emit_attempt`) and the
prologue (`pcrec_emit_prologue`); `runcmp.c` entire; in `emit_vm.c`,
`vm_isl_emit`, `vm_lit`, `vm_plan_entry`, `vm_plan_reseed`,
`vm_emit_search_body`, `vm_emit_epilogue` and `pcrec_emit_vm`. The
handoff was read on `lane/k82hbuild` `9bb97c7c`: `emit_req_handoff`,
`req_uses[]`, and `pcrec_emit_req_byte_check`'s new `const char *`
return.

> **`[rev4.6]`** (r5 A8) Every line-number citation in §14-§16 is
> replaced by the function (or table) it pointed into at `1c2ba975`.
> Function names survive the edits that moved every line after the
> handoff (f116cff5). The facts cited are unchanged, and each name was
> checked to exist at the rev 4.6 base.

### 14.0 The C shapes, revision 4 (additions to §8.2 and §8.3)

```c
#define MF_SITE_ABI 2   /* [rev4] forms, ranges, floor, need, ret_pred, denies */
#define MF_VOCAB    2   /* [rev4] ALL_PRESENT's ret_pred; ASSIGN/ON_MISS handoffs */

typedef enum {              /* [rev4] r3 F1: what the kit's text IS          */
    MF_FORM_EXPR,           /* ONE C expression; pcrec's text surrounds it    */
    MF_FORM_STMT,           /* statements at `indent`; pcrec's text before/after */
    MF_FORM_FUNC            /* a file-scope `static inline` function (its
                               DEFINITION) plus, wherever pcrec asks, its CALL
                               expression (mf_call)                           */
} mf_form;

typedef enum {              /* rev 3's four, plus two [rev4]                  */
    MF_H_RETURN,            /* EXPR / FUNC call: the VALUE is the result or `miss` */
    MF_H_ASSIGN,            /* [rev4] STMT: `result_decl result = …;` then, on a
                               miss, pcrec's `on_miss`                         */
    MF_H_ON_MISS,           /* [rev4] STMT: a presence gate. On no candidate,
                               run `on_miss`; on a hit, write nothing          */
    MF_H_ADVANCE,           /* STMT: move `cursor`; maintain `count` (§14.3)   */
    MF_H_ON_CAND,           /* STMT: per candidate, ascending (§14.3)          */
    MF_H_BOOL               /* EXPR: true iff the predicate holds              */
} mf_handoff;

typedef enum {              /* [rev4] r3 F5: an EMPTY range's outcome          */
    MF_EMPTY_MISS,          /* as a miss: `miss` written / `on_miss` run       */
    MF_EMPTY_NOP,           /* nothing written, nothing run                    */
    MF_EMPTY_EXCLUDED       /* pcrec's text has already proven lo < hi; the
                               kit emits no empty test at all                  */
} mf_empty;

typedef enum { MF_REQUIRED, MF_OPTIONAL } mf_need;   /* [rev4] r3 F7 */

/* mf_term gains:                                                            */
/*   int32_t  offset;   may be NEGATIVE ([rev4] r3 F11), >= -MF_MAX_BACK      */
/*   mf_need  need;                                                          */
/* mf_pred gains:                                                            */
/*   mf_need  need;      a whole predicate may be OPTIONAL (set-leads' lead,
                         on a DFA-scan route only: [rev4.6] §14.5)            */
/*   uint8_t  plan_hint; PERMANENT while pcrec computes it (§14.9)            */
/*   uint16_t plan_pos;  [rev4] the position INSIDE a RUN term the plan scans  */
/*   uint32_t fn_ref;    [rev4] FUNC: pcrec's name hook id (0 = none)         */
/* mf_site gains:                                                            */
/*   mf_form   form;                                                         */
/*   mf_empty  empty;                                                        */
/*   uint8_t   end_back;       hi = n - end_back, 0 or 1 (D11's bound), §14.4 */
/*   uint8_t   ret_pred;       ALL_PRESENT: RETURN/ASSIGN the leftmost hit of
                               preds[ret_pred]; 0xFF = none (§14.3). [rev4.6]
                               preds[] is DENSE: an absent part takes no index,
                               so the window's index is 0 or 1 (§15.5)      */
/*   uint8_t   guard_by_caller; EXPR VERIFY only: pcrec's text has established
                               lo + reach <= n before the expression runs     */
/*   uint8_t   use;            MF_USE_DISCARD (the result is only compared
                               with `miss`) or MF_USE_POSITION (read as a
                               position); [rev4.6] a PER-INSTANCE fact from
                               req_use(cx), not a DELEG_SITES column (§14.5) */
/*   uint16_t  npred;          was uint8_t: N4's set may hold 255 bytes       */
/*   uint64_t  denies;         MF_D_* in-emitter denies (§14.10)              */
```

The hooks gain these members and lose none:

```c
/* mf_hooks, [rev4] additions */
    const char *indent;      /* STMT / FUNC body: the indent pcrec's text is at   */
    const char *on_miss;     /* ON_MISS, ASSIGN, MISS-empty: pcrec's statement
                                ("return 0;", "break;"); never an expression    */
    const char *result_decl; /* ASSIGN: a declaration prefix ("size_t ") or NULL */
    const char *count;       /* ADVANCE: the run counter's name, or NULL (§14.3)  */
    long        count_start; /* its value at the kit's first statement            */
    const char *peek;        /* ADVANCE: the byte at the cursor, not consumed      */
    const char *floor;       /* the LOWER read limit (§14.7); "0" when NULL       */
    const char *(*fn_name)(void *u, uint32_t fn_ref);       /* FUNC: its name     */
    void (*note)(void *u, mf_sink *c, uint32_t part);       /* §14.2              */
    const char *(*note_tag)(void *u, uint32_t part);        /* [rev4.1] §14.2: pcrec's provenance tag, e.g. "[K66]" */
    /* UNTIL M1b (§16): pcrec's run compare for RUN term `term`, as an EXPR at
       `base + off` (rule 6's twin for whole runs: one spelling, pcrec's, while
       runcmp.c has callers the kit does not own); NULL after M1b             */
    void (*run_cmp)(void *u, mf_sink *c, const char *base, int32_t off, uint32_t term);
```

> **`[rev4.8]`** (Q-M1b-2, Q-M1b-7; §R4.8) `MF_SITE_ABI` is **4**:
> - `run_cmp` is RETIRED: the kit compares runs itself (`memfn/src/
>   runcmp.c`), and a FUNC definition declares its own word-load helpers
>   where pcrec's file-scope `note` wrote them. `note` keeps its §14.2
>   role (pcrec's FACT comment) and no longer carries helpers;
> - `mf_sink` gains `void (*stamp_int)(void *u, const char *name, long
>   long value)`, APPENDED after `legend_byte`: an UNQUOTED stamp line
>   (`stamp` quotes its value);
> - `mf_stamps` writes three lines, `RUN_WORDS` (through `stamp_int`),
>   `MEMFN_FORMS`, `MEMFN_LIBC`;
> - `mf_define` refuses a site whose `denies` differ from the art's.
> `MF_VOCAB` stays 2.

And the per-artifact state replaces rev 3's single `mf_emit_site` call:

```c
typedef struct mf_art mf_art;   /* one per Job ATTEMPT (the size ladder re-emits) */
mf_art  *mf_art_begin(mf_arena *a, const char *prefix, uint32_t policy, uint64_t denies);
int      mf_emit (mf_art *, const mf_site *, const mf_hooks *,
                  mf_sink *body, mf_sink *file_scope, mf_result *res);
int      mf_call (mf_art *, uint32_t handle, const mf_hooks *, mf_sink *body);
int      mf_flush_helpers(mf_art *, mf_sink *file_scope);
uint32_t mf_includes(const mf_art *);          /* MF_INC_STRING_H, …            */
int      mf_stamps(const mf_art *, mf_sink *); /* the kit's stamps, via sink->stamp */
```

`mf_result` keeps `form_id` and gains `handle` (a FUNC site's id for
`mf_call`). It keeps `moved` only for G2's property test. `moved` is no
longer an input to any pcrec guard (§17.2, §18).

**`[rev4.1]` The define/use split, part of `mf_emit`'s contract (r3
addendum C1-1).** A composite site has FUNC parts that belong at file
scope and STMT parts that belong in an entry's body, and pcrec writes the
two at different points of one buffer (§15.5). So `mf_emit` is two calls
that share one site:

```c
int mf_define(mf_art *, const mf_site *, const mf_hooks *def,
              mf_sink *file_scope, uint32_t *handle);      /* FUNC parts, once   */
int mf_use   (mf_art *, uint32_t handle, const mf_hooks *use,
              mf_sink *body, mf_result *res);              /* STMT/EXPR parts    */
/* mf_emit(art, site, hooks, body, file_scope, res) = mf_define + mf_use in one
   call: the form for a site whose parts all sit at ONE point               */
```

1. **Order.** pcrec calls `mf_define` at the file-scope point and
   `mf_use` at the entry, and the define point precedes the use point in
   the buffer on every route (§15.5's table). The kit asserts a defined
   handle at `mf_use` and an unused handle at artifact end (an internal
   error, so a condition that differs between the two points cannot
   drift).
2. **One description.** The site (`mf_site`) is passed ONCE, at define.
   `def` carries only what file-scope text needs (`fn_name`, `note`,
   `note_tag`, `run_cmp`, `legend_byte`). `use` carries what the entry
   text needs (`indent`, `on_miss`, `result_decl`, `result`, the subject
   and bound names). A hook is read at the call that writes the part it
   serves, never earlier.
3. **Names cross by the handle.** The STMT refers to the FUNC's name and
   parameter list through the handle, so the CALL's arguments are the
   definition's parameters, in the same order (§15.2).
4. **The kit alone chooses the arm**, once, at `mf_define`. The use call
   renders that arm's entry part, so a non-baseline arm that fuses lead
   and window into one function (§15.5) leaves no orphan lead-byte
   statement.
5. **Baseline identity.** The two calls' output, concatenated in buffer
   order, is the composite's baseline text. I1 compares each call's own
   span against pcrec's matching pre-migration span.

### 14.1 The three forms (r3 F1)

Every site pcrec writes today is one of three forms, and a site declares
which:

| form | what the kit writes | what pcrec writes around it | today's instances |
|---|---|---|---|
| EXPR | one C expression with no side effect beyond reads, and no statement | the `if (guard && …) goto`, the `size_t cand = …;`, the `… >= n) return 0;` | `pcrec_emit_run_compare` at all three callers (`ofsk_emit_verify` in `emit_dfa.c`; `vm_isl_emit` and `vm_lit` in `emit_vm.c`); every CALL of an offset-skip block |
| STMT | complete statements at `indent`, closed: every brace it opens it closes | the statements before and after it | the one-byte pre-check, N4's block, the handoff gate's declaration and miss test (§15); STAY's and the scan edge's loops (M3) |
| FUNC | a file-scope definition (`static inline <type> <name>(…) { … }` and the blank line after it) into `file_scope`, and a CALL expression per `mf_call` | the call's context; the tables it passes (rule 7) | `ofs_test_emit_fn` and its pair arm, under both of its callers (`pf_block_ofs`, `pcrec_emit_req_run_blocks`) |

A miss is never the kit's control flow. In EXPR and FUNC forms the miss is
a VALUE (`miss`), and pcrec's text tests it. In STMT form it is pcrec's
`on_miss` STATEMENT, which the kit places but never reads. That covers
`return 0;` (the pre-check, the PF `memchr` form), `break;` (the
`(?m)^` skip in `emit_attempt`) and a fall-through (the `-bounded`
forms, `MF_EMPTY_NOP`).

### 14.2 Rendering hooks: indent, notes, escapers (r3 F1, F12)

- **`indent`** is pcrec's current indent, and the kit's statements sit at
  it. A nested statement inside is at `indent` plus four spaces, which is
  every emitter's convention (`pf_emit_memchr`'s `"%s    "`). A
  continuation line is at the column the baseline arm reproduces (the
  one-byte gate's `"%s    !memchr("`).
- **`note(u, sink, part)`** writes pcrec's OWN comment for part `part`
  of a site, a statement of pcrec's FACT ("every match of this pattern
  contains the byte 64"), into the sink at the place the arm chooses.
  A baseline arm places each note exactly where pcrec's text had it. A
  comment that describes a FORM ("one memchr for its byte 114 at offset
  3, one compare of the whole run per hit") is the ARM's, not a note: the
  baseline arm carries pcrec's frozen sentence verbatim (it describes the
  baseline form, which is what it was written about). A non-baseline arm
  writes its own. Both are NONESSENTIAL (D112), and the sink gates them.
- **`note_tag(u, part)`** `[rev4.1]` (r3 addendum C1-2). A form-describing
  comment is the arm's, but its leading provenance tag is pcrec's, and it
  varies by block: the run blocks' comment reads `[OPT-REQPOS]` on the
  window block (index 0) and `[K66]` on the whole-run block (index 1)
  (`pcrec_emit_req_run_blocks`, `i ? "[K66]" : "[OPT-REQPOS]"`). pcrec returns
  the tag for part `part` through this hook, and every arm that writes a
  form comment starts it with the tag, so the kit never learns what the
  block index means. Like `note`, it is read only where the sink's comment
  gate is open.
  **`[rev4.6]`** (r5 A6) `part` is the predicate's index in the site's
  DENSE `preds[]`, for `note` and `note_tag` alike. "Index 0" and
  "index 1" above are `req_run_tests`' own block indices, not the
  composite's. In the composite site (§15.5) the window's index is 0
  with no lead and 1 with one, and pcrec maps its tag from the index it
  built. One numbering, so `-fcomments` output cannot drift between the
  two.
- **The sink is pcrec's, behind an adapter.** `mf_sink` is a table of
  operations over pcrec's `StrBuf`: `puts`, `printf`, `cmt_open(tier)`,
  `cmt_close`, `stamp(name, value)`, and pcrec's three escapers:
  `cstr` (`pcrec_sb_cstr`, a string literal's bytes), `comment_byte`
  (`emit_comment_safe_byte`) and `legend_byte`. The kit therefore never
  carries a copy of pcrec's escaping (r3 F12's second half). Comment
  gating (`-fcomments`, D108's render-time gate) and D143's prefix
  rendering stay where they are, because the bytes still pass through
  pcrec's buffer.
  **`[rev4.6]`** (r5 A11) `comment_byte` is STATEFUL. The real escaper
  is `emit_comment_safe_byte(StrBuf *, int *prevp, unsigned char,
  bool (*extra_escape)(unsigned char))`: it threads the previous byte
  across calls to catch `*/` and `/*`, and takes an extra predicate. At
  M1 no kit-written comment calls it; only pcrec's notes do. When a kit
  comment first needs it, the sink op carries the `prev` state and the
  predicate.
  **`[rev4.7]`** Two rulings (§R4.7.0):
  - **Q-G2-16.** When `cmt_open(tier)` returns open, the SINK has
    already written the comment opener, and `cmt_close` writes the
    closer. The kit writes only the body between them.
  - **Q-G2-7.** Every string a hook RETURNS (`member`, `table_name`,
    `fn_name`, `note_tag`) must stay valid until `mf_art_end`. The kit
    may hold one past later hook calls, for example a FUNC's name kept
    for `mf_call`.

### 14.3 Operations: what each returns (r3 F2, F6)

- **FIND, RETURN.** As rev 3 rule 3, restated in §14.5.
- **ALL_PRESENT with `ret_pred` (F6).** "Does every predicate hold
  somewhere in `[lo, hi)`", and where `ret_pred != 0xFF`, the result is the
  LEFTMOST position of predicate `ret_pred` (as FIND would return it).
  Predicates are tested in `preds` order in a baseline arm. Any other arm
  may reorder them, unless a predicate's position is RETURNED: that one is
  found by the FIND contract wherever in the order it runs. This is the
  K82 handoff gate as ONE site: lead byte (OPTIONAL on a DFA-scan route,
  REQUIRED on a no-DFA route, `[rev4.6]`), window run
  (REQUIRED, `ret_pred`), whole run and set rest (REQUIRED, the no-DFA
  route's proof). §15.5 renders it.
  **`[rev4.6]`** (r5 A1, A5) Two corrections. (1) The lead is OPTIONAL
  only on a DFA-scan route. On a no-DFA route it is REQUIRED (§14.5).
  (2) A reorder must keep each predicate's guards. A predicate whose
  `empty` is EXCLUDED relies on an earlier predicate having returned on
  an empty window (K27). The kit re-derives EXCLUDED whenever it
  reorders, and the composite's own site-level `empty` is MISS (§14.4).
- **ON_CAND order (F6).** Candidates are visited in ascending position
  (descending if `reverse`). No candidate is skipped, none is visited
  twice, and a reject resumes at the next position in that order (rev 3
  rule 4).
- **ADVANCE with `count` (F2).** The scan edge's bounded loop is pcrec's
  peeled guard, then the kit's loop, then pcrec's post-loop, which reads
  the counter (`emit_scan_edge`: `if (scan_run_length == 16UL)`).
  So, where `count` is non-NULL:
  - the kit DECLARES `unsigned long <count> = <count_start>;` as its
    first statement. Its type and name are the baseline's. `count_start`
    is 1 at the scan edge, because pcrec's guard has already tested one
    position;
  - on exit, `count` equals `count_start` plus the positions the loop
    advanced past, capped at `span_hi`;
  - **the cap was reached iff `count == span_hi`**. That is the one
    post-loop fact pcrec reads, and the contract states it;
  - the cursor ends at the first non-member, at the cap, or where `more`
    fails, whichever comes first.

  **`[R4h-prep]`** (Q-R4h-1 (a), ruled 2026-10-08; `MF_SITE_ABI` 5) The
  declaration above is the KIT-owned case. `mf_site.count_by_caller` = 1
  states that the CALLER declares the counter before the site, with its
  own text in between (the scan edge's peeled step, the VM span scan's
  `lim_` and cursor init), and reads it after the loop. The kit's text then
  only advances and caps it, and never declares it. `count` is required
  (a conditional `uses` entry: unstated, R1 declines, so the last row
  refuses naming `count`), and `count_start` keeps its meaning (the value
  at the kit's first statement). It is a semantic fact (shared state), not
  layout: the layout variants (G2 of the R4h notice) are the pcrec-side
  normalization pre-commit's (Q-R4h-1 (b)), after C7.
- **`peek` (F2).** The kit's membership test of the cursor's byte calls
  `member(term, peek)`, never `s[cursor]` of its own: the direction owns
  how the cursor reads (`subject[scan_position]` forward,
  `subject[rewind_position - 1]` reversed, `struct DfaDir`'s `peek`). A vector
  arm may read the bytes ahead itself, within rule 2 and `floor`.
- **`[rev4.7]` The operations' edges (§R4.7.0):**
  - **VERIFY (F1, Q-G2-17).** VERIFY answers at `cand == lo`, and
    `lo` must lie in `[lo, n − end_back)`. On an empty range it gives
    the site's `empty` outcome and reads nothing. A MISS site's text
    tests `lo + end_back < n` ahead of every term. A NOP site's
    statement already tests it. An EXCLUDED site, or a `guard_by_caller`
    one, tests nothing: pcrec's text has established the range.
  - **SKIP (Q-G2-9).** "Whose byte" is the candidate's own byte, so the
    SET term sits at offset 0. Any other offset is refused.
  - **ALL_PRESENT (Q-G2-12).** It has no reverse reading, and
    `reverse = 1` is refused.
  - **ADVANCE (Q-G2-14).** It requires `more`, `peek` and `step`. A
    NULL `cursor` is accepted.

### 14.4 Ranges: empty, bounded, never wrapped (r3 F5)

- **`hi` is never an expression that can wrap.** Today's bounded forms
  read `subject_length - 1` ONLY behind `scan_position + 1 <
  subject_length` (`pf_emit_memchr_bounded`). Rev 3's `hi` hook would have
  handed the kit `n-1` at `n == 0`. Now pcrec passes `n` and an
  `end_back` of 0 or 1, the kit's range is `[lo, n − end_back)`, and the
  kit tests emptiness in the non-wrapping spelling `lo + end_back < n`,
  the one the bounded forms use.
- **Every site declares its EMPTY outcome:**
  - `MISS`: the unbounded PF `memchr` form (`if (scan_position >=
    subject_length) return 0;`) and the offset-skip function (its loop
    guard fails, so it returns `n`);
  - `NOP`: the `-bounded` forms (nothing written, the stepped loop takes
    over);
  - `EXCLUDED`: N4's block, which runs only after the first half has
    returned on an empty window (`emit_req_set_rest`'s header). The kit
    emits no test, as today.
  
  **`[rev4.6]`** (r5 A5) EXCLUDED is a property of a PREDICATE placed
  after a guarding predicate, not of a site. A composite site (§15.5)
  declares `empty` MISS at site level: on an empty window it misses, as
  the one-byte gate's `<=` arm and the run block's loop guard make it do
  today. Inside it, part 3's bare `memchr(subject + search_from, …,
  subject_length - search_from)` is EXCLUDED only because part 0 or 1
  ran first (K27: no `memchr` there can see a NULL subject). An arm that
  reorders the set rest first, or drops a guarding predicate, must
  re-derive EXCLUDED and write the empty test itself.
- **No write on an empty range** other than what `MISS` says. ADVANCE
  leaves the cursor and `count` at their start values.
- **`[rev4.7]` The empty range, ruled (§R4.7.0):**
  - **When it is empty (Q-G2-1).** The range is empty iff
    `lo + end_back >= n`. `lo > n` is a LEGAL input and is empty. On an
    empty range the kit's text reads no byte at all, on every op,
    VERIFY included (F1).
  - **Which outcomes a site may declare.**
    - `NOP` is a STMT outcome. EXPR/FUNC with NOP is refused (Q-G2-3):
      a value form must yield something.
    - ON_CAND with NOP renders (F2). On an empty range the whole
      statement is skipped: no result write, no visit, no `on_miss`. A
      NOP ON_CAND, like a NOP ASSIGN, may not declare its result.
    - ADVANCE has no miss, so ADVANCE with MISS is refused (Q-G2-4).
      Its outcomes are NOP and EXCLUDED.
  - **OPEN (Q-G2-5).** A reverse ADVANCE at `lo == n`: pcrec's hooks
    (`more` as `cur > floor`) would move the cursor, while the rule
    above says an empty range leaves it. Unruled; no customer before
    M3.
    **`[R4h-prep]` RULED (Q-R4h-2, recorded by the pcrec manager
    2026-10-08):** ADVANCE's range IS `more`. Its empty range is NOP, and
    the kit adds no empty test: its text reads neither `lo`, `n` nor
    `floor`, and a `more` that fails at the start leaves the cursor and
    `count` where they were. The reverse case is whatever pcrec's `more`
    says. memfn.h records it at the ADVANCE hooks, with the hooks' shape
    classes (`more` CONJ, `peek` POSTFIX, `step` EXPR_STMT; fields.def).

### 14.5 REQUIRED and OPTIONAL terms; the result's promise (r3 F7)

Rev 3's rule 3 ("every term holds at `c`") contradicted two things in
the same note: `consumer`, which lets the kit verify less, and M5, which
lets the kit drop terms (`prefix_k.c` already selects a SUBSET of the
k-set, so its block returns a superset of candidates). Rule 3 is now:

> **RETURN / ASSIGN.** Let `S` be the REQUIRED terms plus the OPTIONAL
> terms the arm chose to test, fixed when the site is emitted. The
> result `c` is the leftmost position in `[lo, n − end_back)` at which
> every term of `S` holds and every term read is below `n` and at or
> above `floor`. Otherwise it is `miss`. Hence `c` is at most the true
> leftmost (the position where EVERY term holds), and every REQUIRED
> term holds at `c`.

A term is REQUIRED when a pcrec decision relies on it having been
tested. Today's cases:

- the run term of a `run-pinned` prefilter. G1 elides the run pre-check
  only because the prefilter verifies the run (`CandScan.run_verified`,
  set in `dfa_cand_scan`);
- every predicate of a no-DFA-route pre-check, `set-leads`' lead
  included (`[rev4.6]`, r5 A1). It is the call's only linear no-match
  proof, and dropping a term moves the give-up surface (K65/K66);
- the predicate whose position a handoff reads (K is measured from the
  window, so the window must hold at `c`).

A term is OPTIONAL when pcrec includes it only for speed: `prefix_k.c`'s
model-selected verify offsets and `set-leads`' lead byte on a DFA-scan
route (`[rev4.6]`). The kit may
test an OPTIONAL term or not. It may never ADD a term pcrec did not pass,
because a term pcrec did not pass is not known to be necessary.

**`[rev4.6]` The lead's need is PER ROUTE (r5 A1, the blocker).**
Revisions 4-4.5 called `set-leads`' lead OPTIONAL everywhere. That is
true only where a DFA scan is in front.
- **DFA-scan routes** (`pcrec_artifact_has_dfa_scan` true: the DFA
  routes and the VM hybrid): the lead is OPTIONAL. The scan is linear in
  the window whatever the pre-check tests, so the lead is speed only.
- **No-DFA routes** (`pcrec_artifact_has_dfa_scan` false): the lead is
  REQUIRED. `emit_req_set_rest` marks the lead's byte as already tested
  (`if (req_lead_byte(cx) >= 0) done[req_lead_byte(cx)] = true;`), so the
  set rest leaves it out. The lead is then the ONLY test of that member
  of the necessary set, and so part of K65's linear no-match proof.
  `req_set_leads_applies` has no DFA-route conjunct, so `set-leads`
  fires on these routes too.
- **Witness** (abi 61, re-run by this lane): `--features all -p rx
  --pattern '(x?)([a-z]+)+Z.user\1'` gives `RX_ENGINE "vm"` and
  `RX_VM_PREFILTER "none"`. Its pre-check is the lead
  `!memchr(…, 90, …)` and `rx_reqrun`, with no `rq_set` block. With
  `-fno-req-set-lead` the lead's three lines go and `rq_set[] = { 90 }`
  appears. pcrec's own pins: `tests/codegen/run_prechecks.sh` ("Z ...
  LEADS it ... so no member is left") and sabotage S459
  (`set_rest_retests_lead`).
- **What dropping it would do:** an arm that drops this lead turns
  NOMATCH into `PCREC_ERR_STEPS` on the `(x?)([a-z]+)+Z.@\1` give-up
  shape that `emit_req_set_rest`'s header describes.

So `mf_pred.need` for the lead is `OPTIONAL` iff
`pcrec_artifact_has_dfa_scan`, else `REQUIRED`. pcrec sets it per
instance, from the same call the set rest reads.

The K82 handoff's soundness survives the weaker promise. With `c ≤
c_true` (the leftmost window occurrence ≥ `search_from`), every match
starting at `m ≥ search_from` has its window at some `w ≥ m`, so `w ≥
c_true` and `m ≥ w − K ≥ c_true − K ≥ c − K`. A lower `lo` is sound,
only less useful.

**`use` (DELEG_SITES' new column).** `POSITION` sites have a result that
pcrec's text reads as a position: the PF and offset-skip calls
(`scan_position = cand`), and the handoff (`handoff_position`). `DISCARD`
sites only compare the result with `miss`: the run check without handoff
(`if (… >= subject_length) return 0;`). A kit arm may exploit
`DISCARD`, for example by returning any occurrence. On a `POSITION` site
it may not. C10 checks that every site whose result pcrec's text reads
as a position is a `POSITION` row.

> **`[rev4.6]`** (r5 A2) `use` is NOT a static `DELEG_SITES` column.
> Whether the PRE result is read as a position is decided PER ARTIFACT
> by `req_uses[]` (`req_use(cx)`), through the value
> `pcrec_emit_req_byte_check` returns. That value is read as `fwd.from`
> (`emit_unanchored`), as `first` (`emit_attempt`) and as the VM
> hybrid's first prefilter start (`vm_emit_search_body`). The same PRE
> kind is DISCARD on union-select (`RX_REQ_HANDOFF "none"`) and POSITION
> on cls-n-uc, userpass and mod-i. The OFS emitter (`ofs_test_emit_fn`)
> serves PF (always POSITION) and PRE (either). A static PRE=DISCARD
> would let an arm return "any occurrence" on handoff artifacts, which
> is S464's miscompile (`litscan_k82h.md` §1.1a). A static PRE=POSITION
> would make DISCARD unreachable. So:
> - `mf_site.use` is a per-instance fact, set from `req_use(cx)`, the
>   same call that sets `ret_pred`;
> - `DELEG_SITES` holds at most a CEILING ("this site may be DISCARD");
> - C10 checks PER INSTANCE: `use` is POSITION iff the result is read
>   (`pcrec_emit_req_byte_check` returned something other than its
>   `posvar`), or the site is a PF or OFS call.

### 14.6 Totality, the generic row, new shapes, shape bounds (r3 F8)

- **Every kit selection table ENDS in a generic scalar row** that applies
  to every request in its vocabulary. It is a byte loop over the
  conjunction, honouring rule 2 and `floor`. It is the row reached when
  every other row is denied or inapplicable, so no deny can ever leave a
  site without code (the property rev 3 named but did not build). G2
  tests it over a GENERATED predicate space: every term kind ×
  offsets −2..+8 × run lengths 1..33 × masks with 0, 1 and 2 free bits ×
  one to `MF_MAX_TERM` terms × every empty outcome. It is not tested
  only over the shapes pcrec happens to send.
- **A NEW shape has no pre-migration text,** for example a fused
  ALL_PRESENT for N4 or a request through §20.1. Its `baseline` profile
  is the generic scalar row, DECLARED in the manifest as
  `origin=generic`. G1 prints such a site's mover as `UNREACHED (no
  pre-migration form)`, counted. For that site, memfn-off is not D146's
  control: the revisit-when clause compares against "pcrec's
  pre-migration form", and there is none.
  **`[rev4.2]`** Dissolved by D147 (§L.3-§L.4): a new shape lands as a
  kit change with its own deny, which renders whatever the site had
  before it. G1 reaches it like any other change, and the revisit-when
  reading is "worse than the scalar layer it replaced".
- **Shape bounds are checked where they are born, not discovered at
  emission.**
  - `_Static_assert(MF_MAX_TERM >= PCREC_OFSK_MAX_SET + 1)`: 4 offsets
    plus the run term.
  - `npred` is `uint16_t`, since N4's set may hold every byte.
  - `MF_MAX_BACK` covers the largest negative offset any site sends. N3
    sends its `cand.offset`, which is ≥ 1 and small, and it is not taken
    (§9.4 M4).
  - RUN terms have NO length cap. The generic row and the `memcmp` row
    take any length, and VM literal runs are as long as their literal.
  
  pcrec's site builder asserts every bound and fails with
  `pcrec_ctx_fail`'s internal-error tier. A new check, C14, compiles the
  asserts against `limits.def`'s current values.
- **`[rev4.7]` What the kit refuses (§R4.7.0).** `mf_define` refuses
  each of these as outside the vocabulary: a loud error, never code.
  - **Out-of-enum fields (F3).** `form`, `empty`, `use`, `consumer`,
    and a term's or predicate's `need`, as already for `op`, `handoff`
    and the term kind.
  - **`nterm = 0` (Q-G2-10).** An empty conjunction is no search.
  - **A RUN term with `run_len = 0` (Q-G2-11).**
- **`[rev4.7]` What the kit does NOT refuse: a run byte with a bit its
  mask clears (Q-G2-13, revised, §R4.7.2).** Under the literal formula
  it never holds, so the site is well defined and renders. The kit may
  render that byte as constant false (`0`) provided the answer is
  unchanged, and it never normalises the byte into its mask.

### 14.7 `on_cand`, the caller guard, and the lower read limit (r3 F10, F11)

- **`on_cand` text must be DUPLICABLE (F10),** because an arm may copy it
  (an unrolled loop, two copies in a peeled arm). It may contain no label,
  no `static` declaration, no `goto`/`break`/`continue`/`return`, and no
  declaration outside its own braces. It ends in exactly one of the two
  tokens. A new check, C13, holds this structurally: a test driver renders
  every pcrec `on_cand` producer twice in one function and compiles it
  under `-Werror`. Labels and statics fail as duplicates. A `return` or
  `goto` is rejected by a token scan of the rendered hook, the one place a
  test reads pcrec's own hook text.
- **The expression-form caller guard.** Today's run compare is an EXPR
  inside `if (scan_position + 3 <= subject_length && …)`. The guard is
  pcrec's text, and the compare "reads EXACTLY those bytes"
  (`pcrec_emit_run_compare`'s header, P8). Such a site sets `guard_by_caller`. The kit
  then reads exactly `[lo + off, lo + off + len)` and nothing else: no
  vector over-read even inside a page. G2 tests it with a guard page
  placed at `lo + off + len`. Every other site keeps rev 3's rule 2: the
  read guard is the kit's.
- **The lower read limit (F11).** Offsets may be negative, and `floor`
  (default `"0"`) is the lowest index the kit may read. Rule 2 becomes:
  no `s[k]` with `k ≥ n` or `k < floor`. Today's instances are:
  - the reverse STAY skip, which reads `subject[rewind_position − 1]`
    under `rewind_position > search_from` (`dir_rev_skip`), so
    `floor = "search_from"`;
  - N3's `subject[start − offset]` under `start > search_from` or `> 0`
    (the `(?m)^` skip in `emit_attempt`).

  The offset-skip RESEED reads `subject[cand − 1]`, but it is pcrec's
  text after the site (`pf_emit_ofs_reseed`), so it needs no floor; that
  read was always pcrec's.
- **`[rev4.7]` The caller's side of these rules (§R4.7.0):**
  - **Q-G2-15.** `guard_by_caller` is accepted only on an EXPR VERIFY
    whose every term offset is ≥ 0, which is today's run compare.
    Anything else is refused. The kit then tests neither the range nor
    the reads.
  - **Q-G2-6.** `floor <= lo` is the CALLER's precondition. The kit
    bounds every TERM read by `floor`. It does not bound a candidate,
    or the bytes `on_cand` reads, by `floor`.
  - **Q-G2-8.** An `on_cand` text whose token is conditional
    (`if (x) <token>`) and falls through REJECTS. Scanning continues at
    the next candidate.

### 14.8 Form tallies, helpers, includes (r3 F4)

Today pcrec tracks three things the kit's forms decide:

- **`RUN_WORDS`.** It counts compares through the `words` form
  (`rc_emit_words`, stamped in `pcrec_emit_dfa`/`vm_emit_epilogue`),
  so it is a fact about a KIT form. It moves to the kit's stamps. pcrec
  calls `mf_stamps` at exactly the two points it calls
  `pcrec_emit_runcmp_stamp` today, and the kit writes `RUN_WORDS`
  through the sink's `stamp` op (pcrec's spelling of a stamp line). The
  value and position are unchanged, so the bytes are too. pcrec never
  reads a tally.
  **`[rev4.8]` CORRECTED (Q-M1b-2, §R4.8.1 item 1).** The sentence above
  is wrong twice. pcrec's `stamp` op QUOTES its value, so `RUN_WORDS`
  through it would read `"0"` on every artifact (a byte move and a C type
  change). And pcrec calls `mf_stamps` from its finishing pass, over the
  memfn mark, not at the two old points. So: the kit writes `RUN_WORDS`
  through the NEW unquoted op `stamp_int`, as the FIRST of `mf_stamps`'
  three lines; pcrec deletes its two `pcrec_emit_runcmp_stamp` calls,
  which sat directly above the mark, so the line lands where it was.
- **Helpers "before first use".** The `<p>_w<W>` word loads are written
  at two kinds of place today. On the DFA they go immediately before
  each file-scope block that uses them (`pcrec_runcmp_prepare` in
  `pf_block_ofs` and `pcrec_emit_req_run_blocks`). On the VM they go in
  the PROLOGUE, written after the body (`pcrec_emit_prologue`), because the
  body is written first. The rule that reproduces both:
  - a FUNC definition's `mf_emit` writes the helpers it needs and the
    artifact has not yet declared into `file_scope`, immediately before
    the definition;
  - an EXPR or STMT site inside a function body only RECORDS the need in
    `mf_art`;
  - pcrec calls `mf_flush_helpers` at a file-scope point it guarantees
    precedes that function: the prologue call site that
    `pcrec_emit_runcmp_helpers` occupies today.
  
  `mf_art` is begun per Job attempt, so `[ART-SIZE]`'s ladder re-emission
  starts clean (today's "per-attempt `Job` bitmasks", `pcrec_runcmp_prepare`).
- **Includes.** `<string.h>` is decided in the prologue
  (`pcrec_emit_prologue`). The DFA path writes its prologue BEFORE the
  sites. At M1 pcrec keeps its own predicate, which predicts every
  baseline arm's includes exactly, and asserts after emission that
  `mf_includes(art)` is a subset of what it emitted (an internal error
  otherwise). A deferred include anchor, filled after emission like
  D143's prefix, is built only when the first non-baseline arm needs a
  header pcrec's predicate does not predict (D77). It is filed in §22.

### 14.9 `plan_hint` is permanent until the model itself moves (r3 F9)

Rev 3 called `plan_hint` transitional while also freezing a baseline that
needs it. The panel offered two ways out: pcrec keeps computing
`plan_hint`, or M5 re-pins the baseline as a ruled abi event. Revision 4
takes a third that needs neither a permanent pcrec cost model (contra
D146) nor a re-pin:

1. **Until M5, `plan_hint`/`plan_pos` are pcrec's, permanent and
   required.** They name the term (and the position inside a run) that
   pcrec's text scans today. The baseline honours them byte for byte.
   Every other arm may ignore them.
   **`[rev4.6]`** (r5 A3) An arm that ignores them makes two pcrec
   statements false. `<PREFIX>_REQ_RUN`'s `@idx` is specified
   (`docs/spec/findings.md`) as "which position of the run the scan
   tests", and on the run route `<PREFIX>_REQ_BYTE` is the scan member
   (`pcrec_emit_req_byte_check`: the stamp "and the emitted `memchr`
   cannot disagree"). The entry-side `[OPT-REQPOS]` note
   (`emit_req_run_check`: "the scan is on byte %d at offset %d of the
   run") is a FORM statement. `MEMFN_FORMS` reads `none` at SIMD-off,
   so nothing would flag the drift. The fix is part of R4d's D80 spec
   hunk, not built now: re-spec `@idx` and the run-route `REQ_BYTE` as
   pcrec's rarity PICK (a fact about the pattern), and split the
   `[OPT-REQPOS]` note into a fact half (pcrec's `note`) and a form half
   (the arm's). Q55 cross-refers here.
2. **At M5, the MODEL migrates, implement-then-replace, as the BASELINE'S
   PLANNER.** `prefix_k.c`'s selection (its five constants, the 2×
   materiality bar, `verify_cost`) is transcribed into the kit as the
   planner the baseline profile runs. The shadow comparator asserts on
   every compile that the kit's baseline planner picks what `plan_hint`
   says. Then pcrec stops computing the hint, and the field leaves
   `mf_pred` in an `MF_SITE_ABI` bump. Its OUTPUT is unchanged, so no pin
   moves and no abi event fires. The baseline is still "pcrec's last
   spelling", now including pcrec's last PLAN.
   **`[rev4.2]`** Per D147 the model moves as the SCALAR LAYER's
   planner, not the baseline's frozen one: byte-identical at M5 (the
   shadow comparator is that step's comparator), then live code a kit
   lane may improve on SIMD-off acceptance, each improvement with its
   own deny and abi event.
3. **What M5 cannot move without a ruling** is ADOPTION: whether the
   offset-set row applies at all depends on the model
   (`pf_ofs_applies` reads `UnanchStart.ofsk`). That decides
   `RX_DFA_PREFILTER`'s value and whether the landing RESEEDS. §23 Q40
   asks it.

### 14.10 Denies: every shipped deny on a migrating site, and the in-emitter channel (r3 F3, G-F2)

D144 item 4: every optimization keeps its own deny, and the deny is
triage's kill switch. A deny on a migrating site is one of three kinds:

- a pcrec SELECTION deny decides WHICH site and predicate pcrec builds;
- a FACT deny changes the predicate's content;
- an IN-EMITTER deny selects among the emitted forms of one predicate.

Only the third crosses into the kit. pcrec maps it onto `mf_site.denies`
(`MF_D_*`) through one table beside `axes.def`, and every kit arm, the
baseline included, honours it.

| bit | flag | kind | site(s) | fate under delegation |
|---|---|---|---|---|
| 16 | `-fno-offset-skip` | selection (`dfa_pfs[]` offset rows) | PF/OFS | stays pcrec's. Denied, no offset site is built and T1 falls to its `memchr`/`byte-class` rows (M2 sites, pcrec's text until M2) |
| 32 | `-fno-run-prefilter` | selection (`run-pinned` rows) | PF/OFS | stays pcrec's, as bit 16 |
| 30 | `-fno-req-byte` | fact (REQ_SET, REQ_WHOLE_RUN; admission `none`) | PRE | stays pcrec's: no PRE site |
| 31 | `-fno-req-run` | fact | PRE | stays pcrec's: the PRE predicate is the one-byte one |
| 44 | `-fno-req-run-fold` | fact (the walk's position set bound is 1) | PRE/OFS | stays pcrec's: the kit sees an exact run (no mask) |
| 45 | `-fno-req-set-lead` | selection (`req_admits[]` `set-leads`) | PRE | stays pcrec's. **`[rev4.6]`** (r5 A1) DFA-scan routes: part 0 (the OPTIONAL lead) is not passed. No-DFA routes: the lead byte joins part 3, the set rest (it is REQUIRED there, §14.5). K85's interim switch keeps working unchanged |
| 46 | `-fno-req-handoff` (`lane/k82hbuild`) | selection (`req_uses[]`) | PRE | stays pcrec's: `ret_pred = 0xFF`, the handoff is ON_MISS, and pcrec writes no subtraction |
| 33 | `-fno-lit-run` | fact (VM literal run) | VMRUN | stays pcrec's: no VMRUN site, the VM's per-byte chain (VM text, never delegated) |
| 43 | `-fno-run-overlap` | **IN-EMITTER** (`pcrec_runcmp_rows`' `words` and `overlap`) | VERIFY/VMRUN and OFS's run term | **CROSSES.** pcrec maps it to `MF_D_RUN_OVERLAP`, and every kit arm honours it: exact compares go to `memcmp`, masked ones to `bytes` (`runcmp.c`'s header comment, the row table). The axis row and its `strategy_denials` mask entry (in `emit_info_def`) stay pcrec's. Not crossed in M1 (runcmp is reached through a hook, §16); crossed at M1b. **`[rev4.8]`** (Q-M1b-1, Q-M1b-3) The map is ONE pcrec table (`src/gen/memfn_sites.c`), read by `pcrec_memfn_site` (every site), by the attempt's `mf_art_begin` (the kit asserts the two agree) and, reversed, by `--list-axes`' `run-overlap` section over the kit's `mf_run_rows` |
| 21, 42 | `-fno-scan-edge`, `-fno-view-edge` | selection (`scanedge.c`) | EDGE (M3) | stays pcrec's: no EDGE site |
| 36, 38 | `-fno-cls-kit`, `-fno-cls-pack` | T4 | the `member` hook | stays pcrec's. The kit's scalar loops call `member`, so these bits keep reaching the text through the hook |
| 26/27 | `-fno-comments`/`-fcomments` | render tier | every site | stays pcrec's. The sink's `cmt_open` gates the kit's comments as it gates pcrec's |
| new | `-fno-memfn-scan`, `-fno-memfn-loop`, `memfn-native` | profile | every delegated site | §20.2. All three join `strategy_denials` (in `emit_info_def`), so a profile deny never moves `rx_info.flags`. Without this, I2's deny arm reads 5 bytes of `rx_info` moved on every artifact (reqpos's finding, `optimpl2_report.md`) |
| new **`[rev4.3]`** | `-fno-memfn-simd` / `-fmemfn-simd` (§R4.3.1) | the SIMD switch | every delegated site | replaces the row above: one pair, default OFF, both bits in `strategy_denials`. `-fno-memfn-scan`/`-loop` stay withdrawn (§R4.3.6) |

**The kit's per-form switches (G-F2).** **`[rev4.4]`** Revision 4
generated them as `axes.def` rows from `mf_switches()`. Q47 is refined
(D147 addendum 9): they are rows of the KIT'S OWN option registry,
`memfn/src/options.def`, spelled `--memfn=no-NAME`, and pcrec holds only
the opaque string (§R4.4.1). So:

- `--list-axes` lists each one in its `memfn` section, read from the
  kit's `mf_options()`;
- `test-axes` sweeps each for answer identity;
- I2 sweeps each for byte identity against its own pin once it has
  movers;
- none of them is a pcrec flag bit, so none needs a `strategy_denials`
  entry.

A regression in one kit form is still triaged by flipping one named
switch, D144's purpose, without pcrec learning what the form is.

---

## 15. M1's site shapes, each reproduced byte for byte `[rev4]`

For each shape in M1 (§16), this section gives:

- TODAY's emitted text, with comments off (D112's default) and the
  prefix rendered as `rx`;
- the `mf_site` and hooks pcrec builds;
- the line in the baseline arm that writes each piece.

The values are concrete: run `user`, scan byte `r` (114) at index 3,
necessary byte `@` (64), and so on. Every piece of text below comes from
a format string in a cited emitter, and "byte for byte" means the
baseline arm's format strings are those strings, moved. The I1 shadow
comparator (§9.3) proves it over every compile the suite makes. These
examples show only that the CONTRACT can say it, which revision 3's
could not (r3 F1).

### 15.1 FUNC / FIND / RETURN: the offset-skip block (`ofs_test_emit_fn`, `emit_dfa.c`)

Today, the run pre-check's window block for an exact 4-byte run (via
`pcrec_emit_req_run_blocks`):

```c
static inline size_t rx_reqrun(const unsigned char *subject, size_t n, size_t pos)
{
    while (pos + 3 < n) {
        size_t cand;
        const void *q = memchr(subject + pos + 3, 114, n - pos - 3);
        if (!q) return n;
        cand = (size_t)((const unsigned char *)q - subject) - 3;
        if (cand + 3 >= n) return n;
        if (!memcmp(subject + cand, "user", 4)) return cand;
        pos = cand + 1;
    }
    return n;
}

```

| field / hook | value | why |
|---|---|---|
| `op`, `form`, `handoff` | FIND, FUNC, RETURN | a file-scope function returning a position or `n` |
| `pred` | one RUN term, `offset` 0, `run` `user`, `mask` NULL, REQUIRED; `plan_hint` 0, `plan_pos` 3; `fn_ref` → `rx_reqrun` | the `req_run` fact's window; `r->idx` is the scanned position |
| `empty`, `end_back` | MISS, 0 | the loop guard fails → `return n` |
| `use`, `consumer` | DISCARD (or POSITION under the handoff, §15.5), ENGINE | the call site compares with `n`, or reads the position |
| `s`, `n`, `lo`, `miss` | `subject`, `n`, `pos`, `n` | inside a definition, the hooks are the function's own parameter names, which are the baseline's (manifest locals: `subject`, `n`, `pos`, `cand`, `q`) |
| `run_cmp` (until M1b) | pcrec's `pcrec_emit_run_compare(cx, c, "subject + cand", 0, &run)` | writes `!memcmp(subject + cand, "user", 4)` |

The baseline arm's lines are `ofs_test_emit_fn`'s format strings moved
whole:

- the signature, from `fn_name` plus the parameter list. A SET term with
  `table_ref` and more than one member adds `, const unsigned char
  *<table_name>` in term order: `ofsk_emit_params`'s rule;
- `while (pos + %d < n)`, with maxk = the largest term reach − 1;
- the `memchr` arm at `plan_pos` (offset form when > 0);
- `if (cand + %d >= n) return n;`;
- the verify chain in ASCENDING offset order. A singleton SET term is
  `subject[cand + k] == b`, a multi-member SET term is
  `<table>[subject[cand + k]]` through `table_name` (rule 7, pcrec's
  table), and the RUN term is `run_cmp`;
- `) return cand;`, `pos = cand + 1;`, `return n;\n}\n\n`.

Where the run's scanned position is a two-member cube (a mask byte other
than `0xFF` at `plan_pos`), the baseline arm takes the PAIR leapfrog
(`ofs_test_emit_pair`) first. That is the same arm order
`ofs_test_emit_fn` has. The prefilter row's block
(`pf_block_ofs`) is the same site with SET terms from the
k-set, `fn_ref` → `rx_ofsskip`, and `plan_hint` naming the scanned term.

**`[rev4.6]`** (r5 A9) The pair arm declares three more locals, which
join the manifest: `ha`, `hb` (`size_t ha = 0, hb = 0;`, the two
streams' last hits) and `fresh` (`int fresh = 1;`). The pair arm is
the gate on union-select, userpass and mod-i, three of the four R-1
cells.

**The block's comment** (`pf_block_ofs`'s offset legend, or the run
blocks' "THE NECESSARY-RUN SEARCH" paragraph) describes the FORM ("one
memchr for its byte 114 at offset 3"). So it is the baseline arm's own
frozen text, rendered from the site's values. It goes through the
sink's `legend_byte` and `comment_byte` escapers (§14.2), with
`-fno-offset-skip`/`-fno-run-prefilter`/`-fno-req-run` spelled as
frozen literals.
**`[rev4.6]`** (r5 A9) The list is incomplete. The run blocks' comments
(`pcrec_emit_req_run_blocks`) also spell `-fno-req-byte`, the masked
one spells `-fno-req-run-fold` too, and the masked one's scan clause is
either "one memchr for its byte %d" or "two memchr streams for its
bytes %d and %d". All of these
are frozen form text of the baseline arm.

**Helpers.** If `run_cmp` needs a word load (the `words`/`overlap`
rows), pcrec's `pcrec_runcmp_prepare` writes it before the comment,
exactly where it does today. That holds until M1b moves the helpers to
`mf_emit`'s "before the definition" (§14.8).

### 15.2 EXPR / FIND / RETURN: the block's CALLS (`pf_emit_ofs`, `emit_req_run_check`)

Today:

```c
            size_t cand = rx_ofsskip(subject, subject_length, scan_position, rx_ofs_k1);
```
```c
    if (rx_reqrun(subject, subject_length, search_from) >= subject_length) return 0;
```

pcrec's text is `"%s    size_t cand = "` … `");\n"` (`pf_emit_ofs`)
and `"%sif ("` … `" >= %s) return 0;\n"` (`emit_req_run_check`). The kit writes only
the call, through `mf_call(handle, hooks)` with `s` = `subject`, `n` =
`subject_length`, `lo` = `scan_position` or `search_from`. The arguments
after `lo` are the same table names, in the same order, as the
definition's parameters. The miss test, the reseed (`pf_emit_ofs`) and the
`return 0` stay pcrec's: §14.1, a miss is a value pcrec tests.

### 15.3 STMT / FIND / ON_MISS: the one-byte pre-check (`emit_req_one_byte`)

Today, indent four spaces:

```c
    if (subject_length <= search_from ||
        !memchr(subject + search_from, 64, subject_length - search_from))
        return 0;
```

| field / hook | value |
|---|---|
| `op`, `form`, `handoff` | FIND, STMT, ON_MISS |
| `pred` | one SET term `{64}`, `offset` 0, REQUIRED (OPTIONAL when it is `set-leads`' lead on a DFA-scan route; `[rev4.6]` REQUIRED as the lead on a no-DFA route, §14.5, §15.5) |
| `empty`, `end_back` | MISS, 0 (the `<=` arm, K27: an empty window cannot hold the byte) |
| `s`, `n`, `lo`, `indent`, `on_miss` | `subject`, `subject_length`, `search_from`, `"    "`, `"return 0;"` |
| `note(0)` | pcrec writes `/* [OPT-REQBYTE] every match of this pattern contains the byte\n * 64, so a window without it holds no match at all. */` |

The baseline arm writes `note(0)`, then `"%sif (%s <= %s ||\n%s
!memchr(%s + %s, %d, %s - %s))\n%s    %s\n"`, with the empty test
fused into the condition and `on_miss` at indent plus four spaces.

### 15.4 STMT / ALL_PRESENT / ON_MISS: N4's set rest (`emit_req_set_rest`)

Today (two remaining members, 65 and 66):

```c
    {
        static const unsigned char rq_set[] = { 65, 66 };
        for (size_t rq_i = 0; rq_i < sizeof rq_set; rq_i++)
            if (!memchr(subject + search_from, rq_set[rq_i], subject_length - search_from))
                return 0;
    }
```

| field / hook | value |
|---|---|
| `op`, `form`, `handoff` | ALL_PRESENT, STMT, ON_MISS; `ret_pred` 0xFF |
| `preds` | one singleton SET predicate per remaining member, ascending byte order, ALL REQUIRED (K65: the call's only linear no-match proof) |
| `empty` | EXCLUDED (the first half has already returned on an empty window). **`[rev4.6]`** (r5 A5) a property of these predicates in their place after the first half, not of the composite, whose `empty` is MISS (§14.4) |
| `s`, `n`, `lo`, `indent`, `on_miss` | as §15.3 |
| `note(3)` | pcrec's `[K65]` comment. **`[rev4.6]`** (r5 A6) read `note(i)`, `i` the index of the FIRST set-rest predicate in the site's dense `preds[]`: 0 for this standalone site, and after the lead, window and whole run in the composite (§15.5) |

The baseline arm's locals `rq_set` and `rq_i` are in the manifest. Its
`static const` table is the kit's own block-scoped datum, not one of
pcrec's 256-byte tables (rule 7 concerns those). A predicate set of size
zero emits nothing, as today (`emit_req_set_rest`'s `n == 0` return). That is a site pcrec does not
build, so `npred = 0` never reaches the kit.

### 15.5 The K82 gate, ONE composite site (r3 F6; `lane/k82hbuild`, abi 61)

On the DFA route with `set-leads` and the handoff (comments off), the
text is:

```c
    if (subject_length <= search_from ||
        !memchr(subject + search_from, 109, subject_length - search_from))
        return 0;
    size_t handoff_position = rx_reqrun(subject, subject_length, search_from);
    if (handoff_position >= subject_length) return 0;
    if (handoff_position - search_from > 3) {
        handoff_position -= 3;
    } else
        handoff_position = search_from;
```

On the no-DFA route (no handoff; [K66]'s whole run longer than the
window), it is:

```c
    if (rx_reqrun(subject, subject_length, search_from) >= subject_length) return 0;
    if (rx_reqrun_whole(subject, subject_length, search_from) >= subject_length) return 0;
    {
        static const unsigned char rq_set[] = { … };
        …
    }
```

**`[rev4.6]` On the VM hybrid route** (r5 A7: the VM engine with a DFA
prefilter in front, so `pcrec_artifact_has_dfa_scan` is true), the
handoff also applies. `req_handoff_applies` admits `ENGM_VM` with
`fit.prefilter` (less the Q10 decline and d′). The define is
`pcrec_emit_req_run_blocks`, called unconditionally in
`vm_emit_search_body`. The use is that function's
`pcrec_emit_req_byte_check` call, and its consumer is the FIRST
prefilter call, which starts at `first` (POSITION). With a DFA scan in
front there is no whole run and no set rest, so the site has the lead
(where `set-leads` applies) and the window only. This listing is from
code reading. No witness artifact was found (the r5 critic's candidates
were count-collapsed or had `VM_PREFILTER "none"`). The witness is
OWED at R4c: the I2 sweep must reach this route ([MECH-REACH]).

**One site.** `op` ALL_PRESENT, `form` STMT, with the predicates in
pcrec's order. The definitions of `rx_reqrun` and `rx_reqrun_whole` are
this site's FUNC parts, emitted earlier into `file_scope` at the point
`pcrec_emit_req_run_blocks` occupies (in `emit_unanchored`,
`emit_attempt` and `vm_emit_search_body`).

| part | predicate | need | rendered by the baseline as |
|---|---|---|---|
| 0 | `{lead byte}` | OPTIONAL on a DFA-scan route; **`[rev4.6]`** REQUIRED on a no-DFA route (K65, §14.5) | §15.3's text (present only where `set-leads` applies and bit 45 is clear) |
| 1 | the window RUN | REQUIRED | handoff (`ret_pred = 1`, ASSIGN): `"%s%s%s = "` CALL `";\n%sif (%s >= %s) %s\n"`, with `result_decl` `"size_t "`, `result` `handoff_position`, `on_miss` `"return 0;"`. No handoff (`ret_pred = 0xFF`, ON_MISS): `"%sif ("` CALL `" >= %s) %s\n"` |
| 2 | the whole RUN | REQUIRED | as part 1's ON_MISS line, with `rx_reqrun_whole` (present only on the no-DFA route, `req_run_tests`) |
| 3 | the set rest | REQUIRED | §15.4's block (present only on the no-DFA route) |

**`[rev4.6]` One numbering, the handoff rule, and the composite's
`empty` (r5 A6, A5).**
- "Part" in the table names a ROLE, not an index. The site's `preds[]`
  is DENSE: an absent part takes no index. So the lead (where present)
  is index 0, the window is the next index, then the whole run, then
  one singleton SET predicate per set-rest member (§15.4).
- `ret_pred` is the WINDOW's index: 0 with no lead, 1 with one. mod-i
  is such a cell (handoff, no lead; `gates_d4d9ed90/mi_use.txt`), where
  `ret_pred = 1` would name the wrong predicate.
- `note(i)` and `note_tag(i)` take the same index (§14.2): the lead's
  `[OPT-REQBYTE]`, the window's `[OPT-REQPOS]`, the whole run's `[K66]`,
  and `[K65]` on the first set-rest predicate.
- `mf_site.handoff` is ASSIGN iff `ret_pred != 0xFF`. Then the window's
  line is the ASSIGN text and every other predicate behaves as ON_MISS.
  With `ret_pred = 0xFF` every predicate is ON_MISS.
- The composite's site-level `empty` is MISS. Part 3's EXCLUDED holds
  only in its place after part 0 or 1 (§14.4). An arm that reorders
  re-derives it.

**`[rev4.1]` Define and use (§14.0's split).** The FUNC parts (the window
and whole-run definitions) are written at one point and the STMT at
another, so the composite is TWO calls. The define point is where
`pcrec_emit_req_run_blocks` writes today, under `fit.chosen == ENGM_DFA`
on the DFA routes and unconditionally in the VM search emitter. The use
point is the entry's pre-check, which follows `emit_search_head`, the
offset-0 start rule and the end-window clamp:

| route | `mf_define` (file scope) | `mf_use` (entry body) |
|---|---|---|
| DFA, unanchored (`emit_unanchored`) | its `pcrec_emit_req_run_blocks` call | its `pcrec_emit_req_byte_check` call (read as `fwd.from`), after the end-window clamp |
| DFA, anchored (`emit_attempt`) | its `pcrec_emit_req_run_blocks` call | its `pcrec_emit_req_byte_check` call (read as `first`), after the clamp |
| VM search entry (`vm_emit_search_body`) | its `pcrec_emit_req_run_blocks` call | its `pcrec_emit_req_byte_check` call (read as `first`), after the clamp |

Both points of a route test the same engine condition (`fit.chosen ==
ENGM_DFA`, or none on the VM), so a site defined is a site used (§14.0,
rule 1). `use`'s hooks carry the entry's names (`subject`,
`subject_length`, `search_from`) and `return 0;`. `def`'s carry `fn_name`
for `rx_reqrun`/`rx_reqrun_whole` and the block comment's `note_tag`.
Parts 1 and 2 above are the FUNC parts; parts 0 and 3 and the call lines
are the STMT. The baseline arm's define output is `ofs_test_emit_fn`'s
text unchanged, and its use output is the listing at the top of this
section.

pcrec writes everything after the site: the `[K82]` comment, the K
subtraction and the utf8 round-up (`emit_req_handoff`). That is rule 8,
unchanged. The handoff's soundness reads only part 1's promise (§14.5).
The notes are pcrec's per part: `[OPT-REQBYTE]`, `[OPT-REQPOS]`,
`[K66]`, `[K65]`.

**Why ONE site and not four.** Today the order (lead first, then run) is
a rarity choice pcrec makes (`req_set_leads_applies`), and K85
shows it can lose on match-dense text. As one site, the order is a hint
the baseline honours and a non-baseline arm may revise (lead and window
fused into one pass is twins.md T-B's shape). That is K85's general
answer under D146. Bit 45 still removes part 0.

> **`[rev4.5]`** R-1's Linux verdict (`memfnr4b_report.md` §9) corrects
> the last two sentences above: fusing the lead into the run pass is
> NOT K85's general answer. K85's cure is the fused RUN filter. The
> order is read through the subsection below.

> **`[rev4.6]`** (r5 A1) "Bit 45 still removes part 0" holds on DFA-scan
> routes only. On a no-DFA route bit 45 moves the lead's byte into part
> 3 (the set rest), because there the byte is a necessary-set member no
> other part tests.

**`[rev4.5]` The lead order and the regime boundary (R-1 §9, §6).**

1. **The lead order is part of the site's form.** It is the kit's
   per-site choice, with two values: lead first (the lead is one call,
   and the fused run pass follows it) and run first (the lead folded
   into the run's pass). **The default is lead first whenever a lead is
   present.** The evidence, at SIMD-off, gcc SSE2, Linux:
   - userpass: the lead rejects first (`=` is absent from the
     capability text). Run-first `swar` LOSES everywhere (gate 64k
     +35.6 ns, pc1024 +86). Lead-first `swlf` is null on gate and
     sweep, except sweep 1m, which loses by +3.07 ns (floor 2.53).
   - cls-n-uc (K85): the lead never rejects. Lead-first `swlf` wins
     the sweeps and the per-call rows. The cure comes from the fused
     run filter, not from fusing the lead.
2. **A possible future fact, NOT built (D77).** A pcrec "lead can
   reject on this site's text class" density fact would let the kit
   choose run-first where the lead is dense, with no cost model. Its
   trigger is a measured cell where run-first beats lead-first. Until
   then the default stands, and no field, hint or name is added to
   `mf_site`. It is filed in §22.
3. **The portable fused form has a regime boundary.** It scans at about
   0.18 ns/B (union-select 1m, no stops). glibc's AVX2 `memchr` has a
   faster raw rate. The form wins where the emitted gate pays per-stop
   costs (union-select's 1,431 `c` stops per 64 KiB; mod-i's and K85's
   find-all sweeps). It loses on early-hit single gate calls on dense
   text: mod-i gate 1m (+2.41 ns, floor 0.52) and cls-n-uc gate
   64k/256k. The SIMD-off form is not selected for such a call without
   the fact in item 2. This is a boundary of the portable form, not a
   defect.
4. **The handoff contract is unchanged.** Every fused variant returns
   the exact leftmost run position (ASSIGN, `ret_pred = 1`), and the
   probe's check proves equality with the emitted gate's value.
   (`[rev4.6]`, r5 A6: read `ret_pred` as the window's index. It is 1
   on userpass and cls-n-uc, which have a lead, and 0 on mod-i, which
   has none.)
5. **D149.** The fused form's unroll and block size follow K-7 (§8.6).
6. **`[rev4.6]` Run first must still decide the lead (r5 A1).** A
   run-first arm that folds the lead into the run's pass must still
   decide the lead over the whole window. It returns a miss for the
   lead only after proving the lead absent from all of `[lo, n)`. On a
   no-DFA route, where the lead is REQUIRED, it never returns a hit
   with the lead untested. R4d's design states this obligation (§22).
   All four R-1 cells are DFA-route sites, so R-1's verdicts stand.
7. **`[rev4.6]` pcrec's suite pins lead-first today (r5 A10).**
   `tests/codegen/run_prechecks.sh` §5.11 (the lead is the first
   `!memchr` above the first `rx_reqrun(`) and sabotage S460
   (`lead_after_run`) assert the order in pcrec's own suite. Rev 4.5
   made the order the kit's. R4d's design names both. When run-first
   lands, they re-home to kit-form checks (G2, C5) or relax.

### 15.6 EXPR / VERIFY / BOOL: the run compare (`pcrec_emit_run_compare`) — M1b, shown for the contract

Today, in the VM literal run (`vm_lit`, `emit_vm.c`), run
`abc` (the `overlap` row):

```c
    if (scan_position + 3 <= subject_length && rx_w2(subject + scan_position) == rx_w2("ab") && rx_w2(subject + scan_position + 1) == rx_w2("bc")) { scan_position += 3; goto rx_L7; }
```

| field / hook | value |
|---|---|
| `op`, `form`, `handoff` | VERIFY, EXPR, BOOL |
| `pred` | one RUN term `abc`, `offset` 0 (the island: `offset` = the node's depth, `vm_isl_emit`), REQUIRED |
| `guard_by_caller` | 1: pcrec's `scan_position + 3 <= subject_length &&` precedes it |
| `s`, `lo` | `subject`, `scan_position`; the baseline's `base` is `<s> + <lo>`, and `rc_base` appends ` + <off>` when `off ≠ 0` |
| `denies` | `MF_D_RUN_OVERLAP` iff bit 43 is set |
| `policy` | `MF_P_INLOOP` (D91 budget 2; VMRUN's row) |
| `empty` **`[rev4.8]`** | EXCLUDED (Q-M1b-5): pcrec's guard precedes the expression |
| `use` **`[rev4.8]`** | DISCARD: a BOOL is never read as a position |

The baseline arm is `runcmp.c`'s row table and three form writers,
moved whole. Each helper (`rx_w2`) is RECORDED in `mf_art`, and pcrec's
prologue calls `mf_flush_helpers` where it calls
`pcrec_emit_runcmp_helpers` today (`pcrec_emit_prologue`). The `words` tally
becomes the kit's `RUN_WORDS` stamp, written by `mf_stamps` where
`pcrec_emit_runcmp_stamp` is called (`pcrec_emit_dfa`,
`vm_emit_epilogue`). pcrec's own count of its literal-run SITES
(`VM_LIT_RUNS`, `vm_emit_stamps`) stays pcrec's, because it counts
sites, not forms. The prologue's `<string.h>` for a VM body with literal
runs (`v.nlitrun > 0`, `pcrec_emit_vm`) is predicted exactly by every baseline
form. `bytes` is the only form without `memcmp`/`memcpy`, and the VM
never takes it (it passes no mask).

### 15.7 The shapes M1 does not move, sketched so the contract is shown complete

- **The PF `memchr` form** (M2, `pf_emit_memchr`) is STMT/FIND/ASSIGN with
  `empty` MISS, `on_miss` `"return 0;"` (both the empty test and the
  NULL result run it), `result` `scan_position`, and the `pf_open` brace
  and its closing `}` as pcrec's text. **`memchr-bounded`** is the same
  with `end_back` 1, `empty` NOP and `miss` `subject_length - 1` written
  only inside the kit's non-wrapping guard (§14.4).
- **`[rev4.6]` The PF byte-class form** (r5 A12; M2, `pf_emit_bcls` and
  `pf_emit_bcls_bounded`; union-select's PF) is STMT/FIND/ASSIGN with a
  SET term reached through `table_ref` (the artifact's
  `can_begin_match` table, rule 7), `result` `scan_position`, and
  `empty` MISS (`if (scan_position >= subject_length) return 0;`).
  **`byte-class-bounded`** is the same with `end_back` 1 and `empty`
  NOP: its loop stops at `subject_length - 1` and nothing follows it.
- **`[R4g]` As BUILT (lane r4g, 2026-10-07; `docs/dev/lanes/r4g_report.md`).**
  Main's clearance kept every guard, `return 0`, entry test and re-seed
  pcrec's text (R-4's boundary rule), so the PF site is narrower than the
  two bullets above, one shape for all six PF forms and the VM hat's seek:
  FIND / STMT / ASSIGN over ONE REQUIRED SET term at offset 0, `result` the
  scan position, `use` POSITION. The memchr forms' `empty` is EXCLUDED
  (pcrec's `pos >= n` guard, or the bounded block's `pos + 1 < n`, precedes
  the site), and their statement is the search, the NULL test and the store,
  because the hit is a POINTER: a site whose result were `q` would not be a
  FIND result, and the generic row could not render it. Unbounded, a NULL
  hit runs pcrec's `on_miss` (`"return 0;"`, `on_miss_leaves` 1); bounded,
  the store takes the hit or pcrec's `miss` (`"subject_length - 1"`, the
  range's end). The table forms are the in-place walk (`result` IS `lo`),
  `empty` NOP, `miss` the range's end (MF_MISS_N, or `n - 1` bounded), no
  `on_miss`: pcrec's `if (pos >= n) return 0;` after the walk stays
  pcrec's. The kit's rows: `memfn/src/pffind.c` (`pf_memchr`,
  `pf_memchr_bounded`, `pf_walk`, `pf_walk_bounded`).
- **The STAY skip** (M3, `dir_fwd_skip`/`dir_rev_skip`) is STMT/SKIP/ADVANCE. pcrec writes
  `kw (state == K) {` and the accept store. The kit writes the one
  `while` line, with `end_back` 1 under views, `table_ref` `stay<K>`, and
  `peek` `subject[scan_position]`. Reversed, it is `floor`
  `search_from`, `peek` `subject[rewind_position - 1]`, and `reverse` 1.
- **The scan edge's loop** (M3, `emit_scan_edge`) is STMT/SKIP/ADVANCE with
  `count` `scan_run_length`, `count_start` 1, `span_hi` the edge's span,
  and `member` = `scan_test`'s T4 spelling over `peek`. pcrec's guard,
  the `scan_run_length == 16UL` test (the cap-reached contract, §14.3)
  and the accept stores stay pcrec's. **`[rev4.1]`** (r3 addendum C1-3)
  The PEELED first step stays pcrec's too: `unsigned long
  scan_run_length = 1;` and `<advance>;` (`emit_scan_edge`), written
  before the kit's `while` line, whose body is `{ <advance>;
  scan_run_length++; }`. That is why `count_start` is 1. Recommendation:
  leave it in pcrec's text. The kit's loop is complete without it, byte
  identity holds with no added vocabulary, and a `peeled` flag would be
  a new `MF_VOCAB` item for one site (D77). If a later arm wants the
  first step inside its own unrolling, it is a request (§11.3) and an
  `MF_VOCAB` bump then.
- **`(?m)^`'s skip** (M4, not taken, in `emit_attempt`) is STMT/FIND/ASSIGN with
  `on_miss` `"break;"`, a term at a NEGATIVE offset (`subject[start −
  offset] != b` guards entry), `floor` `search_from` or `0`, and a
  RESULT TRANSFORM (`+ offset`) that is the term's offset applied back.
  The contract can say it. Q42 still says not to move it.
  **`[rev4.3]`** Q42 is REVERSED (addendum 5): it migrates, as M4, by
  completeness (§R4.3.4), and C12's `memchr(` count reaches 0.
  **`[R-7]` M4 prep (kit-only, MF_SITE_ABI 6; memfn/docs/responses.md
  "R-7 (M4, MLINE): edit set and overlap", rulings Q-R7-1/2/3).** The
  sketch above is CORRECTED: `X` (`search_from` or `0`) is a start
  decision and stays in pcrec's guard; the kit's `floor` is `start`, the
  same text as `lo`. Three contract gaps closed kit-side:
  - **Q-R7-1, the read-bounded range.** A FIND whose every term reads below
    its candidate is bounded by its reads, not by the candidate's own byte:
    c in [lo, n] with every read below n − end_back (memfn.h, MF_OP_FIND),
    so `(?m)^$` on "a\n" finds 2. No `result_bias` field: the term's offset
    already says it. ([ENG-TACTICS]' "resume at hit + 1" is the same range;
    nothing is designed for it.) The generic row's FIND loop moves only for
    such sites.
  - **Q-R7-2, `MF_EMPTY_AT_N`.** A proven fact: lo <= n and the subject
    non-NULL, so the scanned bytes are empty only as lo == n over a valid
    pointer; a zero-length `memchr` is then defined and misses, so the
    memchr row writes no empty test. EXCLUDED does not suffice on a
    read-bounded range (it proves lo <= n only; at n == 0 the subject may be
    NULL, K27).
  - **Q-R7-3, LOOP_EXIT.** `on_miss` `break;` is its own class; a row may
    paste it only where its text opens no loop around it, so the generic
    row never serves it and a site no other row serves is refused.
  The row is `pf_memchr_back` (memfn/src/pffind.c): one byte at -1, floor
  = lo, AT_N, the store `+ 1`. Its fixtures and gate cases:
  tests/memfn/arm_fixtures.c, run_arm_pins.sh checks 6 and 9.
  **`[M4]` As BUILT (lane m4, 2026-10-08; `docs/dev/lanes/m4_report.md`).**
  pcrec's ONE describer was generalized, not paralleled: `PcrecFind` (now in
  `src/gen/memfn_sites.h`) gained `site` (DELEG_SITES PF or MLINE), `offset`
  (the term's offset: 0, or -1) and `floor`. `emit_attempt` keeps the guard
  line, X and every start decision, and describes the three statements
  through `pcrec_emit_find` with `site` MLINE, `offset` `-cand.offset`,
  `floor` `start`, `on_miss` `break;` and no `miss` (under Q-R7-1 `n` is a
  hit, so no text names a value no hit takes). DELEG_SITES row MLINE is
  FIND / ASSIGN / SET, DELEG_SCAN, MF_USE_POSITION. Zero movers: the I1
  shadow comparator matched 693 sites over 21,890 corpus compiles, and
  26,268 base-vs-REPLACE corpus pairs were byte-identical (990 MLINE
  sites). The manifest is 10 delegated / 3 pending; C12 has no `memchr(`
  outside the kit (5 rows / 7 forms).

---

### 15.8 STMT / MISMATCH / ON_DIFF: the encoding seam's span compare (N7) — M7, as built `[M7]`

Built by lane m7 (2026-10-08, R-8; rulings Q-R8-1..10 in
`memfn/docs/responses.md`, D58 addendum 2; report
`docs/dev/lanes/m7_report.md`). Zero movers, no abi event, no spec hunk.

- **The site** is the compare LOOP inside the residual entries
  `<p>_span_match` (byte and utf8) and the byte backend's
  `<p>_span_match_caseless` (ASCII and UCP): a statement site inside the
  backend's own exported function (Q-R8-2). The backend keeps the
  signature, the braces, the final `return (ptrdiff_t)reflen;`, the UCP fold
  function and table, and every comment and declaration.
- **The vocabulary** (MF_VOCAB 3): `MF_OP_MISMATCH` (F8: k, the least j in
  [0, reflen) with lo + j >= n or fold(s[lo + j]) != fold(ref[j]); EQUAL
  when none), `MF_H_ON_DIFF` (k written to `result`, then `on_miss`, which
  may read it; `on_miss_leaves` 1 required), `MF_T_REF` (one REQUIRED term
  at offset 0 with no data). MF_SITE_ABI 7 appends `mf_site.fold_kind` (the
  FACT: NONE / ASCII / UCP, Q-R8-4) and the hooks `ref`, `reflen`, `fold`
  (pcrec's fold TEXT, `@` the byte: FOLD_EXPR `f(@)` or FOLD_STMT statements
  over the lvalue `@`). No fold map travels (D77/D122). `empty` is NOP (an
  empty reference is EQUAL); `reverse`, `end_back` and any second term are
  refused.
- **The rows** (Q-R8-9): one renderer, `memfn/src/mismatch.c` `mm_render`.
  The generic row renders the exact and FOLD_EXPR shapes (one `if` per byte:
  `if (at + i >= n || F(s[at + i]) != F(ref[i]))` then the failure on its own
  line); the row `mismatch_inplace` renders the FOLD_STMT shape (temps `x`,
  `y`; the subject-end exit, the two loads, the fold pasted per temp, the
  compare exit). Each shape's text is frozen byte for byte from a pre-M7
  artifact (`tests/memfn/pins/n7_target/`, C5 check 10) and run against the
  contract (check 11).
- **The seam** (D58 addendum 2): the backend's text carries
  `PCREC_ENC_SITE` where the loop sat and a keyed side table of site data
  (`PcrecEncSite`: fold kind, fold text, failure statement). The gen layer
  (`emit_residual_defs`, `pcrec_memfn_span_site`, DELEG_SITES row N7,
  budget 2) describes each site, renders it through the door
  `pcrec_memfn_emit`, and passes the strings to `pcrec_enc_emit_defs`, which
  substitutes them for the tokens. enc never calls up.
- **Not migrated:** utf8's caseless compare (`u8_defs_bref_ci`) is a
  per-character decode walk (two cursors, a length-changing result), not a
  byte mismatch. It keeps its body: manifest row N7U, `pending`, trigger
  "completeness after M7 + a decode-hook vocabulary step" (Q-R8-1).
  **Retired (D147 add. 14):** not a kit site; the row is deleted.

### 15.9 STMT / SKIP / ADVANCE, STRIDED: the VM span loop at stride > 1 (VMSTRIDE) — M6, as built `[M6]`

Built by lane m6 (2026-10-08, R-10 cut to VMSTRIDE; rulings Q-R10-2..12 in
`memfn/docs/responses.md`; design `docs/dev/lanes/m6scope_report.md`;
report `docs/dev/lanes/m6_report.md`). Zero movers, no pcrec abi event, no
spec hunk, NO `MF_VOCAB` move.

- **The site** is the VM cursor rung's span loop when the body is W > 1
  bytes wide (`vm_emit_span_scan`, both of `vm_cursor_rep`'s scanning arms).
  It is the existing generic SKIP / ADVANCE over W SET terms: one step reads
  W contiguous positions, term i at offset i (Q-R10-2).
- **The contract step** (`MF_SITE_ABI` 8): Q-G2-9 relaxed on ADVANCE only
  (W REQUIRED SET terms at offsets 0..W-1, forward only; every other SKIP
  keeps one term at 0); `MF_MAX_TERM` 8 -> 32 (`VM_MAX_STRIDE`, asserted in
  `emit_vm.c` and by C14); a strided site's kit-owned reads index
  `s[cursor + i]` (Q-R10-4, so it states `s` and `cursor`); `span_hi` caps
  ITERATIONS (Q-R10-5). The gate field `stride` (ONE / MANY) makes the
  generic row USE `s`/`cursor` at MANY.
- **The render** (`stmt_advance`): R4h's frozen target with one `(member)`
  per term, ` && `-joined; frozen byte for byte from pre-M6 artifacts
  (`tests/memfn/pins/m6_target/`, C5 check 12) and run against the contract
  (check 13).
- **pcrec's side**: ONE builder, `vm_span_advance`, for every stride
  (`vm_stride_loop` deleted); `PcrecAdvance.stride` is stated by every
  builder (STAY/EDGE state 1; 0 is refused: Q-R10-12); DELEG_SITES row
  VMSTRIDE beside VMSPAN (Q-R10-6), budget 2. The block, `it_`, `lim_`, the
  cursor init, the rung, admission, possessify, MRL and every member text
  stay pcrec's (m6scope V1-V15).
- **Not migrated:** the lazy arm's rmin prefix (VMLAZY, `pending`,
  Q-R10-7; **`[R-12]` MIGRATED** by re-expression, lane vmlazy 2026-10-09: the
  same site capped at rmin, VMLAZY deleted) and N6 (Q-R10-1, Frank's; RETIRED, D147 add. 12: not a search site).

## 16. M1, narrowed and sequenced (r3 G-F10, G-F11) `[rev4]`

**The trigger's site class.** M1 exists for K82 cause (B): the
DFA-route run pre-check gate on `union-select`, `userpass` and `mod-i`.
Its fused scan+verify (twins.md T-B) is the measured customer, so the
triggering site is §15.5's composite PRE site. M1 is the CLOSURE of that
site under §9.1's rule: an emitter migrates with every caller, and a
search keeps one spelling.

| unit | why it is in M1 | why it is not wider |
|---|---|---|
| `pcrec_emit_req_byte_check` with `emit_req_one_byte`, `emit_req_run_check`, `emit_req_set_rest`, `pcrec_emit_req_run_blocks`, `req_run_tests` (all three search entries' callers: `emit_unanchored`, `emit_attempt`, `vm_emit_search_body`) | the trigger site itself. The one-byte gate and the set rest are in it because the lead byte (part 0) and the set rest (part 3) share their spellings with the non-run path, and two spellings of one presence gate is D122's violation | — |
| `ofs_test_emit_fn`, `ofs_test_emit_pair`, `ofsk_emit_verify`, `ofsk_emit_params` with BOTH callers (`pcrec_emit_req_run_blocks` and `pf_block_ofs`, T1's offset/run rows) | the run gate's definition is this emitter, and the emitter has a second caller | the T1 CALL sites (`pf_emit_ofs[_bounded]`) stay pcrec's text around an EXPR (§15.2) |
| **NOT `runcmp.c`** | the run term's compare is reached through the `run_cmp` hook (§14.0), pcrec's spelling, exactly as T4's `member`. M1 needs no VM site | runcmp has two VM callers (`vm_lit`, the island) that the trigger does not touch. Moving them is **M1b**, filed with its own trigger (§22) |

So, against revision 3's M1, M1 sheds VERIFY/VMRUN (runcmp and its
three callers) and bit 43's crossing. The `memchr(` ratchet after M1
reads 9 → 3, as in revision 3: the six texts in the pre-check and the
offset-skip trio (one each in `emit_req_set_rest` and
`emit_req_one_byte`, two each in `ofs_test_emit_pair` and
`ofs_test_emit_fn`) leave, and PF's two and N3's (`pf_emit_memchr`,
`pf_emit_memchr_bounded`, the `(?m)^` skip in `emit_attempt`) remain.
C12's ceiling is re-counted at the build commit, and the list above is a
floor.

**Sequencing (G-F10).** M1's IMPLEMENT commit freezes pcrec's
pre-migration text as the baseline (§9.2). That text must be the text
that should be frozen, and nobody may be editing it.

1. **After `lane/k82hbuild` merges** (abi 61, the handoff). The handoff
   changes `pcrec_emit_req_byte_check`'s signature and adds the
   ASSIGN-shaped part 1. Freezing first would freeze the pre-handoff
   text, and the K82 cells' twin (R4b) must be measured against what
   remains after the handoff (r2 R2).
2. **After K85's re-measure** on the post-handoff build. K85 (set-leads
   loses ~5% on `cls-n-uc`) is an OPEN regression on the very site M1
   freezes. Its disposition says "re-measure after the handoff lands
   before designing anything specific". Freezing before that re-measure
   would make K85's text the guard's OFF arm. If the re-measure closes
   K85, M1 freezes the post-handoff text. If K85 stays open, M1 still
   freezes it: the baseline is "pcrec's last spelling", regressions
   included, and K85's cure becomes the composite site's non-baseline
   arm (§15.5). The point of waiting is that the ruling is made with the
   number in hand.
3. **After migration, an edit to a delegated emitter is KIT-LANE work.**
   Any lane that would have changed `emit_req_*`/`ofs_test_*` text after
   M1's replace commit changes a kit arm instead. A non-baseline change
   is a kit change, with the abi ritual if it moves a byte (G3). A
   baseline change is a ruled abi event (Q27/Q38). The lane-briefing
   skill names the migrated emitters; §22 R4c's delivery adds them to
   `src/gen/CLAUDE.md` as "migrated: edit in `memfn/`".
4. **`[rev4.6]` The REPLACE commit re-points the mech rows (r5 A4).**
   About 28 sabotage rows under `tests/mech/sabotages/` anchor their
   `SAB_BEFORE` text inside M1 emitters (critic A's census at abi 61:
   S185, S265, S267, S277, S278, S279, S293, S447, S448, S449, S452,
   S455, S459, S460, S463, S464, S471, S472 among them). The REPLACE
   commit deletes that text, so each row would miss its target and read
   UNREACHED ([MECH-REACH]). The REPLACE commit therefore re-points
   every row whose `SAB_BEFORE` lives in a migrated emitter: into
   `memfn/`, or onto pcrec's remaining half. It states the count, taken
   at that commit from the anchors themselves. `emit_req_handoff` is
   SPLIT across the boundary: its declaration and miss test move to the
   kit (part 1's ASSIGN, §15.5), so S464 goes kit-side; the K
   subtraction, the clamp and the utf8 round-up stay pcrec's, so S463,
   S470 (the clamp, found by this lane), S471 and S472 stay pcrec-side.

> **`[rev4.2]`** (D147, §L.6) "Freeze" in this section means the step's
> byte-identity COMPARATOR, nothing longer. Both waits stand, for byte
> identity (nobody may edit the text under comparison) and because R4b
> is measured on the post-handoff build. Item 2's "K85's text becomes
> the guard's OFF arm" no longer applies: there is no permanent OFF
> arm, and K85's cure is a scalar-layer change accepted on its own SIMD-
> off reading, before or after M1. Item 3's "a baseline change is a
> ruled abi event" becomes: every scalar-arm change is an ordinary kit
> change (own deny, SIMD-off acceptance, the abi ritual when it moves a
> byte).

> **`[rev4.3]`** (Q41 RULED and Q42 REVERSED, addendum 5) Scope and
> sequence are RULED as this section states them. M1's trigger is now
> COMPLETENESS: its prerequisites only, with no performance cell (that
> cell, R4b's, gates R4d's movers instead).
>
> Status at main 7f94b0cd:
> - wait 1 is MET (`lane/k82hbuild` merged at f116cff5, abi 61);
> - wait 2, K85's re-measure on the post-handoff build, is OWED, and
>   so is the handoff's Linux alpha. (`[rev4.5]`: both MET, §R4.5.5
>   item 1.)
>
> **`[rev4.5]`** Both reads exist since this block was written:
> `docs/dev/lanes/k82halpha_report.md` is the handoff's Linux alpha and
> the K85 re-measure (§3: K85 PERSISTS, +0.023..+0.036 ns/B on
> `cls-n-uc`, new vs deny). R-1 then measured the fused forms on the
> same cell (§15.5). Whether the two waits are MET is the manager's
> reading of those reports, not this revision's (§R4.5.2).
>
> **`[rev4.6]`** (r5 B9) One authority for the waits' status: §R4.5.5
> item 1. It cites the manager's confirmation in `memfn/docs/requests.md`
> R-1 ("Confirmed 2026-10-05") and `k82halpha_report.md`. Both waits are
> MET there. The sentence above is history.
>
> M1's REPLACE commit flips its rows in the site manifest (C17) from
> `pending` to `delegated`.

---

## 17. Guards, revision 4 `[rev4]`

### 17.1 I2 sweeps every axis and every comment tier (r3 F3, G-F2)

Revision 3's I2 swept "the default, each `-fno-memfn-*` deny, every
`--tune` position, and `-e utf8`". That cannot see a SHIPPED deny on a
migrating site silently stop working. I2 now runs the movers-by-ID diff
(parent against step) at:

- **every `axes.def` axis**, one arm each (both polarities for a pair);
- **every comment tier**: the default (comments off) and `-fcomments`
  (the notes and the frozen form comments of §14.2 are reached only
  there);
- every `--tune` position and both encodings;
- **`[rev4.4]`** one arm per row of `--list-axes`' `memfn` section
  (§R4.4.1), swept for byte identity once the row has movers.

The arm count is printed, and a K35 floor holds it: born at the number
of `axes.def` rows + 2 comment tiers + 5 tune positions + 1 encoding
(+ the `memfn` section's spec-pinned floor, `[rev4.4]`, §R4.4.1), so
an axis that silently stops being enumerated is a red check. This is
the multi-hour `test-axes` shape. It runs on Linux through the
executor channel. On the Mac, a lane sweeps only its own axes plus the
comment tiers (BOILERPLATE's darwin timeouts).

### 17.2 G1, re-founded (r3 G-F4, G-F5, G-F6)

> **`[rev4.2]`** The pcrec-side population diff below now compares the
> default against the CHANGE's own deny (`--memfn-deny=NAME`,
> `[rev4.4]` now `--memfn=no-NAME`), not
> against `memfn-off`, and every reading is taken at SIMD-off and at
> SIMD-on (D147, §L.4). Pooling, the floor of 8, the declared regime,
> the per-event cadence and the armv8 statement are unchanged.

- **The population comes from pcrec, not from the kit (G-F5).** The
  movers are the artifacts whose DEFAULT compile differs byte for byte
  from their `memfn-off` compile (`-fno-memfn-scan -fno-memfn-loop`),
  over the corpus and the bench's patterns. A pcrec-side script diffs
  the two compiles, so the population shares no source with the kit;
  `mf_result.moved` plays no part. The manifest is written by the
  compile pass, never filtered by an outcome, and printed with its
  count.
- **Pooled bins with a floor.** Rev 3 binned by (step, op, length
  decade), most bins thin. G1 bins by (op, length decade) across steps,
  with a floor of 8 movers per bin. A thinner bin prints
  `UNREACHED (n < 8)`, counted, and its movers are reported unverified.
- **The regime is declared** (§21.1): two regimes, both measured, and a
  mover regressing past the floor in EITHER is a D146 revisit event.
- **Cadence: every memfn abi event (G-F6).** Every kit commit that moves
  a pcrec byte runs G1's alpha on its own movers as part of its
  delivery: a new arm, a re-tune of the kit's data, a vocabulary
  addition with a customer, a baseline change. That is D144 item 1
  applied to each event, not only to the "mover steps" R4d/R4f/R4g/
  R4h/R4j. A kit re-tune is exactly the event a step list misses.
- **armv8: there is NO verdict-grade guard (G-F4), and the spec says
  so.** The house has no quiet aarch64 Linux box. Mac timings are
  directional (D144 addendum 1), and Rosetta 2 runs x86 code, not arm
  code. So:
  - the kit does not select a native arm over its portable arm on
    aarch64 (K-4);
  - the Mac run of G1 is a regression check of the PORTABLE text, never
    a verdict;
  - `docs/spec/` states that the kit's choices on aarch64 are unmeasured
    at verdict grade (§10.6 gains a fourth limit).

> **`[rev4.3]`** (§R4.3.1) "Native arm over its portable arm" reads "a
> SIMD-on form over the scalar layer's form", and the Mac run checks
> the SIMD-OFF text. The two readings are `-fno-memfn-simd` and
> `-fmemfn-simd`.

> **`[rev4.4]`** Q43 is ruled (D147 addendum 8): a SIMD-on form tuned
> for aarch64 is not ACCEPTED until Frank admits Mac measurements as
> verdict-grade for those cells, or an aarch64 Linux box exists. x86
> Linux gives the verdicts. K-4's "no SIMD-on form is selected on
> aarch64" is the consequence, and the SIMD-off layer is unaffected.

### 17.3 C9, cross-target syntax, made to run and made non-vacuous (r3 G-F3)

- **The Mac failure.** `clang --target=x86_64-linux-gnu -fsyntax-only`
  stops at `string.h: file not found`, because there is no x86 Linux
  sysroot. The fix is a HEADER SHIM, `tests/memfn/shim/`: minimal
  `<string.h>`, `<stddef.h>`, `<stdint.h>` and `<stdlib.h>` declaring
  only what generated artifacts use (`memchr`, `memcmp`, `memcpy`,
  `size_t`, the fixed-width types). C9 compiles with `-nostdinc -isystem
  $(clang -print-resource-dir)/include -isystem tests/memfn/shim`. The
  compiler's own resource directory carries BOTH architectures'
  intrinsic headers whatever the host, so only libc needs shimming. The
  shim is deliberately not a sysroot: it type-checks calls, links
  nothing, and runs nothing.
- **Vacuity under `portable`.** In the default profile there are no
  `#if` arch arms to compile, so C9 passed by having nothing to check.
  It now runs at `-fmemfn-native` (§20.2) over the movers' patterns, and
  separately at the default.
- **A K35 floor on arms compiled.** The arm count per artifact is
  printed and summed. The total must be at least a COMMITTED floor
  (`tests/memfn/pins/c9_floor`), born at the first native arm's landing.
  `[r9 F-5]` Superseded in form: the floor is a per-level COLUMN of
  `tests/memfn/row_floors.tsv`, not its own pin file (§R4.9.8).
  Zero arms is a FAIL, not a pass. The kit-reported count (rev 3's
  comparison) is kept as a second reading, but it shares a source with
  the subject, so the floor is the independent half.
- **`[rev4.3]`** C9 runs at `-fmemfn-simd` (§R4.3.1). Its scope is
  SYNTAX per target only. Under addendum 6 a SIMD-on artifact makes no
  promise to EXECUTE on any target but its own, so C9 claims nothing
  about execution. A cascading site (§R4.3.2) contributes one arm per
  carried level.

- **`[rev4.9]`** The Linux dev box has no clang, so the `--target`
  cross check above runs only where clang is installed. On the dev box,
  C9 for the x86 levels is C9-x86 (§R4.9.8): every mover compiled by gcc
  with the harness's `-Werror` at `-march=x86-64`, `x86-64-v2`,
  `sandybridge`, `x86-64-v3` and `x86-64-v4` and at `-mgeneral-regs-only`
  (`[r9 C-8]`), with the live-arm count per level taken from `nm` of an
  `-O0` object and held to a per-level column of `row_floors.tsv`
  (`[r9 F-5]`). Batch 1 has no aarch64 level (addendum 8), so nothing
  needs an aarch64 target yet. C18 checks the no-level target (the
  preprocessed text at `-mgeneral-regs-only` equals the SIMD-off text) and,
  `[r9 C-6]`, each live level (`[D155]` `[r9b]` preprocessed-equal
  off-target; on-target, insertion plus exactly one replaced call per
  SIMD FUNC, §R4.9.8).

### 17.4 Pins live under `tests/`, per arm (r3 F12, G-F8)

- **C5's baseline pin is per ARM, not per artifact.** It lives at
  `tests/memfn/pins/arms.tsv`, one row per baseline arm × fixture
  request, holding the sha256 of the arm's rendered text. The fixtures
  are a fixed set of `mf_site`s per (emitter, op, form) shape, written in
  the same commit. The rows are RECORDED at M1's implement commit from
  pcrec's own pre-migration emitter, the side the shadow comparator
  proves equal, so their provenance is pcrec's old output. An unrelated
  abi change (a scaffolding line elsewhere) moves no arm digest and
  forces no re-pin (F12).
- **Per-pattern memfn-off pins.** `tests/memfn/pins/off.tsv` holds the
  sha256 of each manifest pattern's artifact at `memfn-off`, recorded at
  the same commit. It is re-pinned only by an abi event that touches
  scaffolding (D94's grep finds it: it is a byte-count-class reader).
- **`[rev4.2]`** (D147, §L.2-§L.3) `arms.tsv` is a CHANGE DETECTOR, not
  a freeze: recorded at the migration step from pcrec's emitter, then
  re-pinned by every kit change that moves an arm's text, in that
  change's own abi event (D94's grep must find it). `off.tsv` is
  WITHDRAWN with `memfn-off`.
- **Both are in-tree and need no history,** so a `git archive` (mech's
  tree) checks them. Revision 3's "the bytes pcrec emitted at the step's
  parent commit" needed a checkout of the parent, which mech cannot do.

### 17.5 C4's plant, stated honestly (r3 G-F7)

The plant vocabulary is derived at check time from the compilers
installed on the box (`cc -dM -E` per owned target, intrinsic names
scraped from the resource directory's headers). That makes it held out
from the REGEX AUTHOR. It does not make it complete or box-independent:
gcc-16 on the Mac and gcc-15.2 on ubuntubudu declare different macro
sets, and a target whose headers are absent contributes nothing. So:

- the claim is narrowed to "the plant is not chosen by the person who
  wrote the regex";
- the plant's size per class is printed per box, with a floor per class
  (at least one plant), so an empty class is red;
- matching is CASE-INSENSITIVE (`AVX2` in a comment and `avx2` in a
  string are one hit);
- a box-dependent plant is acceptable because C4 runs on both boxes in
  the batch gate.

### 17.6 Sabotage rows, mech-runnable (r3 G-F8)

Every row names a `SAB_FILE` inside the tree, a detector that reads only
in-tree pins, and `SAB_REACH`/`SAB_REACH_POP` (birth-time reachability,
[MECH-REACH]). Ids are taken at build (highest S on main + 1; main is at
S462, `lane/k82hbuild` reaches S477).

| sabotage | detector | `SAB_REACH` |
|---|---|---|
| one baseline arm edited by one byte | C5 (`arms.tsv`) | the arm's fixture renders |
| a kit text change that moves a pcrec byte, no abi bump | the standing identity gates + `off.tsv` | a manifest pattern's site renders it |
| one ISA word per C4 class into `src/gen/emit_dfa.c` | C4 | the plant count for that class is ≥ 1 |
| `#include "memfn/src/…"` in `src/` | C4 class 9 | — (static) |
| `strcmp` on `form_id` in `src/` | C4 class 7 | — (static) |
| a site's `MF_P_INLOOP` dropped from `DELEG_SITES` | C10 | the site's row exists |
| a `POSITION` site's row marked `DISCARD` | C10 (§14.5) | the PF/handoff rows exist |
| the stamp's value forced to `none` on a mover | C11 (§18.2) | the pcrec-side diff names ≥ 1 mover |
| a replaced `memchr(` text re-added to an emitter | C12 | — (static) |
| an `on_cand` producer with a `return` | C13 | a producer exists (R4e onward; UNREACHED before, declared) |
| `MF_MAX_TERM` lowered below `PCREC_OFSK_MAX_SET + 1` | C14 | — (compile-time) |
| **`[rev4.2]`** a kit change's `--memfn-deny=NAME` (`[rev4.4]`: `--memfn=no-NAME`) that no longer reproduces its parent | the per-change comparator at that commit (§L.3) | the change has ≥ 1 mover |
| **`[rev4.4]`** the `memfn` section's member count dropped below the spec floor, or the section not printed | the registry check against the spec-pinned floor (§R4.4.1) | a registry row exists (R4d onward; UNREACHED before, declared) |
| a profile bit left out of `strategy_denials` | I2's deny arm (rx_info moves) | the corpus has a delegated site |
| a `-fmemfn-native` arm emitting one intrinsic under default | C5's portable clause | a native arm exists (R4e′ onward) |
| the kit's guard one byte short | G2's guard-page test (the kit's mech row) | the fixture places the page |

> **`[rev4.2]`** Row 2's `off.tsv` is withdrawn (§L.3); its detector is
> the standing identity gates alone. Row 1 reads "one scalar arm edited
> by one byte without its `arms.tsv` re-pin". The per-change comparator
> row is the sabotage line added above.

> **`[rev4.3]`** Row "a `-fmemfn-native` arm emitting one intrinsic
> under default" reads `-fmemfn-simd` / `-fno-memfn-simd`. Three rows
> are added (ids at build, highest S on main + 1):
>
> | sabotage | detector | `SAB_REACH` |
> |---|---|---|
> | a C12-vocabulary search form (one `memchr(` text) planted in an emitter function no manifest row names | C17 static half | — (static) |
> | one `mf_emit_site` site's manifest row deleted | C17 dynamic half | the corpus compile pass reaches that site |
> | `MEMFN_LIBC` forced to `none` on an artifact that calls `memchr` | C11's libc assertion | the corpus has a `memchr`-calling artifact (today, every PF `memchr` row) |

> **`[rev4.6]`** (r5 A2, B3, B4) Three rows change and two are added.
> - Row "a `POSITION` site's row marked `DISCARD`" now reads: **one
>   site instance's `use` forced to DISCARD where `req_use(cx)` reads
>   the result** (a handoff artifact). Detector: C10's per-instance
>   check (§14.5). `SAB_REACH`: the corpus has a handoff artifact
>   (`RX_REQ_HANDOFF` not `none`). There is no static "handoff row".
> - Row "the stamp's value forced to `none` on a mover" is UNREACHED
>   (K35, declared, not passed) until the first SIMD-on form exists
>   (R4e′). Its `SAB_REACH`, "the pcrec-side diff names ≥ 1 mover",
>   cannot be met before then: at the default build the artifact IS its
>   SIMD-off compile, so the diff is empty. R4d's SIMD-off movers are
>   expected to read `none`.
> - The `MEMFN_LIBC` row stands, and gains two siblings, under Q53's
>   refined form (§R4.3.3; their spelling waits on Q53):
>
> | sabotage | detector | `SAB_REACH` |
> |---|---|---|
> | `memcmp` dropped from `MEMFN_LIBC` on an artifact whose code calls it | C11's libc assertion (names from the compile, §R4.3.3) | the corpus has a `memcmp`-calling artifact (today, every run compare on runcmp's `memcmp` row) |
> | `memcpy` dropped from `MEMFN_LIBC` on an artifact whose code calls it with a non-constant length | the same | the corpus has such a `memcpy` call (UNREACHED, declared, if it has none) |

---

## 18. The stamp, per Frank's Q3 (r3 G-F1) `[rev4]`

### 18.1 The rule

> **`[rev4.2]`** The stamp's VALUE is re-derived under D147 (§L.5, Q52):
> `none` iff the artifact is byte-identical to its own
> `-fno-memfn-native` compile, else the NATIVE form ids. Wherever §18
> below reads "`memfn-off`", read `-fno-memfn-native`, and "baseline
> arm" as "scalar-layer arm". The every-artifact rule, the kit as
> writer, "no kit version", and the R4a′ birth event are unchanged.
> `off.tsv` leaves §18.3's reader list.
>
> **`[rev4.3]`** (Q39 RULED, addendum 3; Q52 REJECTED, addendum 7; libc
> record, addendum 6) The rule is §R4.3.3:
> - `none` iff the artifact is byte-identical to its SIMD-off compile
>   (`-fno-memfn-simd`);
> - otherwise the forms used (every delegated site's id, in site order),
>   a cascading site carrying its levels as `ID@LEVEL+LEVEL`;
> - a second every-artifact line, `<PREFIX>_MEMFN_LIBC`, records the
>   libc functions the search code calls (Q53).
>
> Both lines are born in R4a′. Wherever this section reads `memfn-off`,
> read `-fno-memfn-simd`. Assertion 3's "non-baseline arm" reads "a
> site whose text differs from its SIMD-off rendering". Of the listed
> ids, at least one names such a site.

Revision 3 put `<PREFIX>_MEMFN` and `<PREFIX>_MEMFN_FORMS` on movers
only, citing k82hrev's Q3 recommendation. Frank REVERSED that
recommendation the same day (`litscan_k82h.md`, Rulings, Q3 (a)): "goes
on EVERY artifact of the family, `none` where the handoff does not
apply. House convention: stamps vary only by engine family, never by
presence within a family, and 'does not apply' is a value." D81 is the
same rule: a conditional stamp makes a consumer's `#if` unsafe, and
the ABSENCE of a stamp is never a discriminator. So:

- **One stamp, `<PREFIX>_MEMFN_FORMS`, on EVERY artifact of both
  engines.** Both engine families have delegable sites (the pre-check is
  in all three search entries), so "the family" is every artifact.
- **Its value is `"none"`** where the artifact is byte-identical to its
  own `memfn-off` compile, because every delegated site rendered its
  baseline arm or none was delegated. Otherwise it is the comma-joined
  list of the NON-baseline form ids, in site order. Form ids are opaque
  to pcrec and to consumers, and the spec says so.
- **No kit version, and no `MF_VOCAB`.** `mf_kit_version()` names the
  kit's TEXT and would move every artifact on every kit release,
  including releases that move no byte. That is an abi event for
  nothing, and it is exactly what the panel flagged. A form id changes
  when, and only when, a form an artifact uses changes. A vocabulary
  addition with no customer moves nothing. Rev 3's `<PREFIX>_MEMFN
  "<kit version>"` is withdrawn.
- **The kit writes it**, through `mf_stamps` and the sink's `stamp` op,
  at the stamp block where pcrec calls `pcrec_emit_runcmp_stamp` today.
  pcrec never reads the value.
- `rx_info` is unchanged (D77: no consumer has asked).

### 18.2 C11 checks the value, against a pcrec-side diff

`tests/memfn/run_stamp_census.sh` compiles every manifest pattern at the
default and at `memfn-off` and diffs the two with the stamp line
normalised out. Its assertions:

1. Every artifact carries the stamp, at both compiles. This is the
   presence half, counted.
2. The `memfn-off` value is always `none`.
3. **`[rev4.1]`** (r3 addendum C3-2) The default value is `none` ONLY IF
   the two artifacts are identical (`none` implies identical). The
   converse is NOT asserted: a non-baseline arm may render text equal to
   the baseline's on a given site. A non-`none` value must instead name
   a non-baseline arm that was RENDERED, and a G2 fixture property
   (§10.2) holds that: for every non-baseline arm, on its own fixture
   sites, the arm's text differs from the baseline arm's. So a form id
   never stamps a no-op, and the census claims no iff it cannot see. The
   count of non-`none` artifacts that are nevertheless byte-identical is
   printed (K35) and expected 0.

**`[rev4.6]`** (r5 B3) Read through §10.5's `[rev4.6]` note: at the
default build the two compiles are one compile until R4f. The census
then has 0 movers and 0 non-`none` values. That is the expected
reading, printed as UNREACHED for the FORMS half, not a pass.

The comparison shares no source with the kit: the diff is pcrec's, and
the kit's `moved` is not read (r3 G-F5). The counts of `none` and
not-`none` are printed (K35), and the movers list it produces (the
differing artifacts, a subset of the non-`none` ones) IS G1's
population (§17.2).

### 18.3 Its own abi event, before M1's replace

The stamp's birth adds a line to every artifact, so it is an every-artifact
abi event of its own. It lands as R4a′ (§22), BEFORE M1's replace
commit, so that M1 itself stays a zero-mover migration (its value
everywhere is still `none`). The ritual follows `litscan_k82h.md`
§2.3a's commands, re-run at the build commit with the digit then current
(61 if `lane/k82hbuild` has merged). That list is a floor:

- **the digit's readers**:
  - `src/gen/emit_dfa.c:52`;
  - `docs/spec/match_api.md`'s K80 `#error` text (`§1¶7`), `§6¶17`'s "abi is N"
    sentence and its change log (`docs/dev/history/abi_changelog.md`);
  - `tests/codegen/run_codegen_tests.sh`'s `ABI_EXPECT`;
  - `tests/codegen/run_recursion_identity.sh`'s `FILEPIN` and its
    `ABI_SUBJ`/`ABI_PIN` tripwire;
  - the `(abi N)` provenance comments, which do not move;
  - the alpha scripts' `norm()` patterns, which must widen;
- **the byte-count readers**, every one of which moves under
  every-artifact:
  - all 12 `EMITTED_BYTES` rows of
    `tests/codegen/manifests/m5_stage1_stamps.tsv`;
  - `tests/resource/run_resource_tests.sh`'s `a{5,25000}` byte count;
  - every row of the size log, re-baselined, against the tripwire's max
    (not near);
  - `reqcube_check.py`/`runcmp_check.py`, re-read;
  - `tests/litscan/reqcube.rxt` `[rev4.1]` (r3 addendum C3-3), beside `litrun.rxt`, re-read for any cell that pins an emitted byte count or the stamp block;
  - `c_artifact_cmp.sh`'s `emit_sweep` (a `FILEPIN` re-pin);
  - `tests/findings/manifests/*`, re-derived;
  - the new `tests/memfn/pins/off.tsv` (§17.4), born in R4c, so not yet
    a reader;
- **the contract** (D80): `match_api.md` §6.3 gains the stamp, its
  presence rule (every artifact), its value grammar (`none`, or opaque
  ids), and the sentence "bucket on `none`/not-`none`; never parse an
  id";
- **the bench** (D78): an inbox note, since the bench adapter reads the
  stamp block.

`axes.def` gains no row at this event. The three profile axes land with
R4c, in their own registry re-count (`axesn`, `registry.md`'s row/axis
sentence).

---

## 19. D146's "no cost comparison": every remaining pcrec pricing of kit-owned search code, and its fate (r3 F13) `[rev4]`

The standing rule (D146) is that pcrec carries no arch knowledge and
does no cost comparison over code the kit owns. The house refinement
(ruling 5 of §R4.0) is that MEASURED terms are acceptable and TUNED
cutoffs are not. This is every place, at main `1c2ba975` plus
`lane/k82hbuild`, where pcrec's choice among SEARCH forms or plans
depends on a cost, a rate or a compiler fact. The search is search
code the kit owns, or will own after its step. Each row gives its kind
and fate.

| # | where | what it prices | kind | fate |
|---|---|---|---|---|
| 1 | `src/opt/prefix_k.c:65-100`: `C_MEMCHR` 6, `C_BITMAP` 116, `C_VERIFY` 250, `C_ENTER` 2000, `C_MISPRED` 1500, `MATERIAL` 2×, `verify_cost` | which k-set term to scan, which to verify, and whether the skip is ADOPTED over the offset-0 filter | measured terms (one box, glibc AVX2, the C4 allowlist's code hit at `:45`) plus a ruled bar | **M5 (R4j)**: the model moves into the kit as the baseline's frozen planner (§14.9). Adoption is Q40 |
| 2 | `limits.def` `PCREC_MAX_REQ_RUN_EMIT` 8 | the longest run window the gate compares ("where gcc lowers a constant memcmp to ONE word load") | a COMPILER cost fact about a kit form | stays at M1 (byte identity: the window travels as the RUN term pcrec cut). **M5**: pcrec passes the whole run (≤ `PCREC_MAX_REQ_RUN_SCAN` 32) with per-position density hints, and the kit cuts. The limit's text then states a semantic bound only |
| 3 | `pcrec_find_run_window_start` / `pcrec_find_run_scan_index` (`src/core/findings.c`) | which window of the run, and which position, to scan: a rarity argmin over the prior | measured prior + argmin | stays at M1 as `plan_pos` and the cut window. **M5**: the kit's planner, reading the per-position hints. **`[rev4.6]`** (r5 A3) The stamps that report it (`REQ_RUN`'s `@idx`, the run-route `REQ_BYTE`) and the `[OPT-REQPOS]` note are re-specified as pcrec's PICK in R4d's spec hunk (§14.9) |
| 4 | the `req_byte` pick (`reqbyte_freq_pick.md`, argmin over byte frequency) | which necessary byte the one-byte gate scans | measured prior + argmin | stays at M1 (it is the SET term pcrec passes, and `<PREFIX>_REQ_BYTE` reports it). **M5**: pcrec passes the necessary SET as REQUIRED-of-one ("some member of this set"), with per-member hints, and the kit picks. `REQ_BYTE`'s meaning would then need a ruling (Q40) |
| 5 | `req_set_leads_applies` (`emit_dfa.c:6601`, `pcrec_find_pick`) | whether the set's pick LEADS the run (order, and adding a predicate) | rarity comparison | becomes the composite site's predicate ORDER plus an OPTIONAL lead (§15.5). The baseline honours pcrec's order, and a non-baseline arm may revise it. K85 (this choice losing on dense text) is the arm's to fix. Bit 45 keeps omitting the lead. **`[rev4.5]`** The lead order is the kit's per-site choice, default lead first (§15.5). **`[rev4.6]`** (r5 A1) The lead is OPTIONAL on DFA-scan routes only. On no-DFA routes it is REQUIRED (K65), and bit 45 moves its byte into the set rest rather than omitting it (§14.5) |
| 6 | `req_byte_dominated_by` (`emit_dfa.c:6560`) → `pcrec_find_no_commoner` | G1's elision of the pre-check when the prefilter's scan byte is no commoner than the necessary byte | rarity comparison between two kit-owned searches | the SEMANTIC half (same byte, or the run verified by the prefilter, which makes it a REQUIRED term, §14.5) stays pcrec's: it is an implication between facts. The RARITY half moves at **M2**: the necessary byte is passed as an OPTIONAL term of the PF site, and the kit decides whether testing it pays. **`[R4g ruling, main 2026-10-07]`** SUPERSEDED: the elision is an ADMISSION decision and stays pcrec's, in `cand_rows[]` after [START-TABLE] C4; the kit only ever receives the resulting text. It is its own step after C5b, re-checked against [DEC-FALLBACK]'s scope before it starts. A kit form wanting the choice brings it to main as a request |
| 7 | `dfa_cand_scan`/`pcrec_dfa_cand_ppm` (`emit_dfa.c:6429`/`:6472`; K84's `strcmp` on row names) | the candidate scan's density, read by the reseed table | a DENSITY (the prior's mass), not a price | stays pcrec's as a fact. K84's `strcmp` readers are fixed at **M2** (a `DfaPf` field), as rev 3 §9.4 had it |
| 8 | `vm_reseed_cal` (`emit_vm.c:11055`): `gap` 16/4, `block`, `cap`, `first` | the VM hybrid's retry: step the VM, or re-seed through the prefilter | measured crossovers, per program class | stays pcrec's. It prices the ENGINE's retry, not a memory function. **Coupling:** a re-seed's cost includes the PF search, so after M2 a kit change to PF text can move the crossover. Fate: the reseed witness cells (xcall/hyb, `hyb_reseed.md` §5) join G1 for every PF mover, and a re-calibration stays pcrec's measured decision |
| 9 | `litscan_k82b.md` (PROPOSED, parked): an expected-cost admission for the run gate | whether a gate pays, from rates and machine terms | a cost model over kit-owned search | **WITHDRAWN under D146.** The handoff removed its motivating rescan, and whether a speed-only gate pays is the kit's question (row 11) |
| 10 | `runcmp.c`'s `overlap` lengths {3, 5-7, 9-15} and the `words` row | gcc's lowering of a constant `memcmp` | a compiler cost fact | moves into the kit with runcmp at **M1b**, as the kit's own rows. Bit 43 travels (§14.10) |
| 11 | `PCREC_MIN_REQ_RUN_BITS` 16 (the run's admission floor) and `req_admits[]`' existence test | WHETHER a speed-only pre-check exists at all | a RULED floor ("not fitted"), but an admission decision about a speed-only search | stays pcrec's at M1. It is ruled, and on no-DFA routes the gate is a proof, not a speed choice. Filed as a design question (Q48): an OPTIONAL SITE the kit may render empty, for speed-only gates on DFA routes |
| 12 | `PCREC_MAX_REQ_RUN_POS_SET` 2 ("the emitted scan has two arms") | the masked run's position width, bounded by a FORM count | a form-shaped fact cap | stays pcrec's at M1 (byte identity). After M1 it is re-justified as a vocabulary bound: the kit's FIND accepts sets of width ≤ k, by request (§20.1) |
| — | not kit-owned, listed so the list is complete: `--tune`'s λ and `[CLS-TREE]`'s class-form choice (T4 one-position membership, never delegated); `scanedge.c`'s period/span analysis (a DFA transform); `select_engine.c` (engines) | — | — | unchanged; outside D146's scope |

> **`[rev4.3]`** Q40 is RULED (addendum 4, §R4.3.5). Rows 1 and 4's
> "Q40" fates are decided: at M5 the model moves into the kit as LIVE
> scalar-layer code (frozen only as M5's comparator). At M5′ pcrec
> keeps ONE semantic row ("a necessary byte set exists beyond offset
> 0"), the kit plans, and the reseed is unconditional. `REQ_BYTE`'s
> meaning under M5′ is that event's spec hunk (D80). Every row's fate
> holds for SIMD-off and SIMD-on alike: these are scalar-layer
> decisions.

After R4j and M2, rows 1-4 and 6 have left pcrec. Rows 5 and 10 left
at M1 and M1b. Row 9 is withdrawn. Rows 7, 8 and 11 stay, each a
FACT, an ENGINE choice or a ruled admission, not a price of kit code.
Row 12 is a vocabulary bound. The C4 allowlist's code hit
(`prefix_k.c:45`) leaves with row 1.

---

## 20. Coupling, revision 4: the request channel, the profile axis, symbols, provenance `[rev4]`

### 20.1 Two files from day one (r3 G-F13; D78)

> **`[rev4.2]`** AS BUILT (lane memfnsetup, the manager's naming): the
> pair is `memfn/docs/requests.md` (manager → kit; the ONLY writer is
> the pcrec manager, single-file `[requests]` commits on main) and
> `memfn/docs/responses.md` (kit → manager; the ONLY writer is the kit
> session, single-file `[responses]` commits on its branch, merged by
> the manager). Roles are exactly as below; read `inbox_from_pcrec.md`
> as `requests.md` and `outbox_to_pcrec.md` as `responses.md`. R-1 (the
> R4b measurement) is the first entry. Every `done:` reports both layers
> (D147).

Revision 3 used ONE ledger in-tree, to be split at extraction. One file
written by both sides breaks D78's single-writer rule. It also repeats
the rulings-file-in-worktree failure (memory
`pcrec-rulings-file-in-worktree`): a lane reads its OWN worktree's copy,
so a file both sides edit on different branches diverges silently. So:

- **`memfn/docs/inbox_from_pcrec.md`**: requests `R-n` and defects
  `D-n`. The ONLY writer is the pcrec MANAGER, as a single-file `[inbox]`
  commit on main. A pcrec lane that needs kit work says so in its report,
  and the manager files it. Each entry carries:
  - the customer row;
  - the measured cell that is the D77 trigger;
  - the SEMANTIC operation wanted, never an ISA or a kernel.
- **`memfn/docs/outbox_to_pcrec.md`**: `ack:` (plan) and `done:`
  (`MF_VOCAB`, kit commit) per item, plus the kit's own durable notices
  (a re-tune that will move bytes, a switch added). The ONLY writer is
  the kit side, as a single-file `[outbox]` commit on the kit lane's
  branch, merged by the manager.
- **The request reaches the lane by being on main before the lane is
  briefed.** The manager commits the inbox entry first. The brief names
  the `R-n`, and the lane's worktree is cut from a main that contains it.
  A mid-flight ruling to a kit lane travels in the lane's own
  `NAME_rulings.md` in its worktree, as for any lane.
- At extraction, the two files move into the kit's repository UNCHANGED
  in role. That is exactly the pcrec-bench pair.

### 20.2 The profile axis's polarity (r3 G-F12)

> **`[rev4.2]`** (D147, §L.3, Q51) The two `PCREC_NO_MEMFN_SCAN`/
> `PCREC_NO_MEMFN_LOOP` rows below are WITHDRAWN; only the
> `memfn-native` deny/force pair remains, plus the kit's generated
> `--memfn-deny=NAME` rows (Q47). Family `memfn` is `auto` / `simd` /
> `no-simd`; `memfn-off` dissolves. `no-simd` is the SIMD-off READING
> of D147 and `simd` the SIMD-on one; both run the CURRENT scalar layer
> underneath. option_sets.md's cross-note is updated in this delivery.
>
> **`[rev4.3]`** (addenda 6-7, §R4.3.1) The remaining pair is RENAMED to
> the one SIMD switch:
> `PCREC_AXIS(PCREC_NO_MEMFN_SIMD, "-fno-memfn-simd", PCREC_FORCE_MEMFN_SIMD, "-fmemfn-simd", PCREC_AXIS_DEFAULT_OFF)`.
> The polarity argument below is unchanged: a capability that ships OFF
> is enabled by its `-fX` spelling, and the pair is born whole. R4f
> changes only `default_state`, and only by Frank's ruling once the
> SIMD hold lifts. Family `memfn` is `auto` / `simd` (`memfn-simd :=
> force`) / `no-simd` (`memfn-simd := deny`). option_sets.md's
> cross-note is updated in this delivery. The `memfn-off` line below
> stays withdrawn (§R4.3.6).
>
> **`[rev4.4]`** (addendum 9) The kit's per-form rows are NOT `axes.def`
> rows and not generated axes: `--memfn=<opt>[,…]` is the kit's own
> namespace, from `memfn/src/options.def`, passed through uninterpreted
> and listed by `--list-axes`' `memfn` section (§R4.4.1). The `memfn-simd`
> pair is pcrec's only axis for this.

Revision 3 had `-fno-memfn-native` ON by default, so the default build
carried a set DENY bit. The house convention for an opt-in behaviour is
the opposite: the axis is OFF by default and its FORCE spelling turns it
on. `-fcomments` (D112, `axes.def:216-217`) and `-futf-check` (`:183`)
are the precedents. So:

```
PCREC_AXIS(PCREC_NO_MEMFN_SCAN,   "-fno-memfn-scan",   0, "", PCREC_AXIS_DEFAULT_ON)
PCREC_AXIS(PCREC_NO_MEMFN_LOOP,   "-fno-memfn-loop",   0, "", PCREC_AXIS_DEFAULT_ON)
PCREC_AXIS(PCREC_NO_MEMFN_NATIVE, "-fno-memfn-native",
           PCREC_FORCE_MEMFN_NATIVE, "-fmemfn-native", PCREC_AXIS_DEFAULT_OFF)
```

- The axis is born as a deny/force PAIR, as `comments` was, so both
  spellings exist from birth. R4f, the native flip, changes ONLY
  `default_state`, which is D112's two-event shape in reverse.
- §8.5's profile table reads: row 2 `portable` applies when
  `memfn-native` is not taken (the default, or `-fno-memfn-native`).
  Row 3 `native` applies when it is (`-fmemfn-native`, or after R4f).
- `option_sets.md`'s family `memfn` (§12.1) becomes:
  - `auto`, the empty set;
  - `simd`, which is `memfn-native := force`, i.e. `-fmemfn-native`;
  - `no-simd`, which is `memfn-native := deny`;
  - `memfn-off`, which is `-fno-memfn-scan -fno-memfn-loop`.
  
  The cross-note there is updated in this delivery.
- All three bits join `strategy_denials` (§14.10).

### 20.3 Symbols, provenance, and why `analyze/` is the inverse precedent (r3 G-F14)

- **`analyze/` links NOTHING** from `src/`; it is a leaf binary. The kit
  is the opposite: libpcrec links IT, so its symbols ship inside
  `libpcrec.a` into every program that links pcrec. An unprefixed
  `mf_emit` there is a symbol a user's program may already define.
- **Symbol policy.** Every external kit symbol is spelled through one
  macro in `memfn.h`: `MF_NS(name)`. It expands to `pcrec_mf_##name`
  in-tree and to `mf_##name` in an extracted stand-alone build. So
  `libpcrec.a` exports only `pcrec_`-prefixed names, and the kit's
  sources and pcrec's callers both write `MF_NS(emit)` once, or a
  `#define mf_emit MF_NS(emit)` shim in the header. Internal kit
  functions are `static`. A new check, C15, scans `nm -g --defined-only
  libpcrec.a`: every global defined symbol begins with `pcrec_`. It is
  born with an allowlist at whatever count today's archive measures,
  taken at the build commit.
- **Provenance per file (D145).** Every kit source file whose text can
  reach an artifact carries an SPDX line and a provenance header.
  - The kit's own text is `0BSD`.
  - A file translated from Rust `memchr` names the crate version and the
    source file, and states that it takes the crate's `Unlicense` arm of
    `Unlicense OR MIT`. That arm is on D145's list; MIT text would be
    ideas-only.
  - `memfn/PROVENANCE.md` tabulates file → source → licence → what
    derives from it (every delegated site of every artifact). That is
    `third_party/`'s shape, applied inside the kit.
  
  A new check, C16, requires each such file's SPDX tag to be in D145's
  set.

---

## 21. The three standing design questions (docs/design/CLAUDE.md) `[rev4]`

### 21.1 The measurement regime: RELEVANT

This design reads and produces measured numbers in four places: G1's
timing, R4b's twin measurement, K85's re-measure, and the pcrec terms
§19 keeps. No measured number crosses the pcrec-kit boundary. The
kit's own data is the kit's (K-1..K-5).

- **G1** measures one regime pair, each declared:
  - **THROUGHPUT**: find-all over subjects of at least 1 MiB, chained
    calls as the bench driver issues them, with hit-dense and hit-sparse
    subjects (the bench's own subject classes);
  - **PER-CALL**: one search per short subject (16 B to 1 KiB),
    isolated.
  
  Both run on ubuntubudu: x86_64, gcc 15.2 (the bench's compiler,
  pcrec's target compiler class, D2), glibc, `taskset`-pinned, quiet
  box, calibrated loops of at least ~50 ms, absolute deltas against a
  base-vs-base floor (D144 addendum 1).
  
  **A different regime CAN flip a verdict.** linux_results.md measured
  fusion winning at 64 B and below and losing from about 512 B at SSE2
  width, which is why both regimes are measured and a mover regressing
  past the floor in EITHER is a revisit event. The same holds for
  hit-dense against hit-sparse: K85 is a gate that never rejects on
  dense text.
  
  The compiler: clang numbers never form verdicts. K83 is the standing
  example of clang flipping a gcc result. The Mac is directional, and
  armv8 has no verdict box (§17.2).
- **R4b** is measured in both regimes on the POST-handoff build (§16).
  A fused arm that wins only per-call is reported as such, and R4c's
  trigger requires the win in the cell's own regime with no loss past
  the floor in the other.
  **`[rev4.5]`** R4b is MEASURED (R-1, Linux, `R4B-DONE status=0`;
  `memfnr4b_report.md` §9). union-select wins both regimes at SIMD-off.
  The regime flips verdicts here exactly as this section warns:
  mod-i's gate 1m loses by 2.41 ns while its sweeps win, and userpass
  flips on the lead order. A pointer to the regime boundary is §15.5.
- **`[rev4.2]` Both layers, in every regime (D147).** Each reading
  above is reported at SIMD-off and at SIMD-on. R4b's SIMD-off reading
  is the portable (SWAR) fused form against `emit`; its SIMD-on reading
  is the vector fused form against the SWAR form, the current best
  scalar, not against `emit` (R-1 in `memfn/docs/requests.md`).
- **pcrec's remaining terms (§19).**
  - Rows 1-4 were measured on one box: miss-heavy `memchr` throughput,
    glibc AVX2. offset_k_skip.md §4.3 records that `C_ENTER` flips 11
    of 1,352 selections between 12 and 20 cycles. They leave at M5.
  - Row 8 (reseed) is measured per program class, and its regime is
    `hyb_reseed.md` §3's.
  - Row 2 is a gcc-16/gcc-15.2 lowering fact, valid for gcc only.

### 21.2 The independent control: RELEVANT

| check or selection | checked against | independent of the subject because | who counts the population (K35) | witness reaches its site ([MECH-REACH]) |
|---|---|---|---|---|
| I1 shadow comparator | pcrec's own pre-migration emitter, run in the same compile | the other side is pcrec's code, not the kit's | every compile of `make test`; the count of sites compared is printed | n/a (every compile) |
| I2 movers by ID | pcrec's parent-commit compile | a different commit's output | per axis arm, the mover count by ID; the arm count has a floor (§17.1) | the axes registry's own count |
| C5 per-arm pins | `tests/memfn/pins/arms.tsv`, recorded from pcrec's pre-migration output | recorded once from pcrec, committed under `tests/` | rows per arm, printed | `SAB_REACH`: the fixture renders |
| G1 OFF arm | the `memfn-off` text, which is pcrec's pre-migration text pinned by C5 | not computed by the kit's data; the timing is pcrec's instrument | movers from the pcrec-side diff (§17.2); pooled bins with a floor of 8, and UNREACHED printed | the manifest is produced by a compile pass, not by outcome |
| C11 stamp value | the pcrec-side default-vs-off diff (§18.2) | the kit's `moved` is not read | `none` and not-`none` counts printed | ≥ 1 mover named. **`[rev4.6]`** (r5 B3) UNREACHED, declared, until the first SIMD-on form (R4e′) |
| C4 arch vocabulary | a plant from the compiler's installation | not chosen by the regex author (and no more than that, §17.5) | plant count per class per box, floor 1 | the plant per class |
| C9 cross-target syntax | the committed arm floor | the kit's own arm count is a SECOND reading, sharing its source; the floor is the independent half | arms compiled, summed, against the floor | a native arm exists (R4e′ onward) |
| C10 site table | D91's classification, and the emitter's own use of each result (§14.5) | a structural fact of pcrec's text | rows counted | static |
| G2 kit tests | the SCALAR BYTE LOOP, plus the generic row over a GENERATED predicate space (§14.6) | never another output of the kit's generator (§4.5) | lengths, alignments and hit offsets enumerated, printed | the guard-page fixture |
| `DELEG_SITES` op column | `mf_vocab_has` | a build-time check of a table against the kit's vocabulary: shared by design (it checks agreement, not truth) | rows counted | static |

> **`[rev4.2]`** (D147, §L.3-§L.5) Rows rewritten: **G1 OFF arm** — the
> change's own `--memfn-deny=NAME` (`[rev4.4]`: `--memfn=no-NAME`), whose text is proved equal to the
> parent commit's default by the per-change comparator at that commit
> (a different commit's output, the I2 tool); the timing is pcrec's
> instrument; read in both layers. **C5** — the per-change comparator
> plus the `-fno-memfn-native` vocabulary scan; the baseline pin is
> gone. **C11** — the `-fno-memfn-native` compile of the same build.
> The SIMD layer's control is the CURRENT scalar layer of the same
> build, never a frozen one.
>
> **`[rev4.3]`** The SIMD readings are spelled `-fno-memfn-simd` /
> `-fmemfn-simd` (§R4.3.1). Two rows are added:
>
> | check or selection | checked against | independent of the subject because | who counts the population (K35) | witness reaches its site ([MECH-REACH]) |
> |---|---|---|---|---|
> | C11's `MEMFN_LIBC` half | a pcrec-side scan of the artifact text for the functions the C9 shim declares (**`[rev4.6]`** r5 B4: under Q53's refined form, the names the COMPILE leaves undefined, `nm -u` of a `-O0 -fno-builtin -c` object, less constant-size `memcpy` loads; §R4.3.3) | the shim's list and the scan are pcrec's, and the kit's record is not read (`[rev4.6]`: the compile's symbol table shares no source with any list) | artifacts with a non-`none` value, printed | a `memchr`-calling artifact exists (every PF `memchr` row today); `[rev4.6]` plus the `memcmp` and `memcpy` rows (§17.6) |
> | C17 site manifest | the C12 vocabulary over `src/gen/` (static) and the `mf_emit_site` call census over the corpus pass (dynamic) | the manifest, the vocabulary and the census are pcrec's. Stated limit: a search spelled outside the vocabulary escapes the static half | delegated/pending row counts under a committed floor; site-call count printed | the planted-form sabotage row (§17.6) |

The one place a control still shares a source with what it controls is
the `DELEG_SITES`/`mf_vocab_has` agreement. It is an agreement check
and claims nothing more. Rev 3's C11 shared the kit's `moved`; that is
removed.

### 21.3 What moves when data is regenerated: RELEVANT

| data | regenerated by | emitted bytes that move | pins / selections that move | abi event? (D76/D94) | spec change? (D80) |
|---|---|---|---|---|---|
| the kit's measured data (`memfn/data/*`, its `generate.py`) | a kit lane | the movers' text, where a kit selection changes | the stamp's VALUE on those movers; G1 runs on them (§17.2) | **yes**, in the same commit: digit readers and the byte-count readers by grep (§18.3's list) | no, unless a stated limit changes (§10.6). Form ids are opaque |
| the baseline arms and `tests/memfn/pins/arms.tsv` | only a RULED baseline change (Q38) | the `memfn-off` text, hence every `memfn-off` pin | `arms.tsv`, `off.tsv` | yes | yes (the guard's OFF arm is caller-visible under the deny) |
| `tests/memfn/pins/off.tsv` | any scaffolding abi event | none (it is a reader) | itself, re-pinned in that event | it IS a byte-count reader of every event; D94's grep must find it (named in §18.3) | no |
| the stamp `<PREFIX>_MEMFN_FORMS` | any kit change that moves a form | one line per mover | C11's census, the bench's bucketing | yes (it is emitted text) | its GRAMMAR is spec; its values are not |
| pcrec's prior (`src/findings/default.rxt`, the byte-rate) | a findings re-measure | (a) pcrec's own picks before M5 (§19 rows 3-5), today's abi events; (b) the density HINTS the kit reads, which may move kit choices | the movers of either | yes, as today: a prior regeneration is already an abi event when it moves a pick | no |
| `prefix_k.c`'s constants (until M5) | a re-measure | the k-set plans | the OFS/PF movers | yes | no |
| `vm_reseed_cal` | a re-calibration | the hybrid's retry constants | the hybrid movers | yes | no |
| the kit's option registry (`memfn/src/options.def`; **`[rev4.4]`** replaces `mf_switches()`) | a kit row added or removed | none by itself | the `--list-axes` `memfn` section's rows, its spec-pinned floor (raised in the same change), `test-axes` and I2 arms. `registry.md`'s main-table pin does not move | no bytes; the floor is re-pinned in the same change | yes (`--list-axes` output is caller-visible) |

> **`[rev4.2]`** (D147, §L.2-§L.3) Row 2 now reads: **the scalar arms and
> `arms.tsv`** — changed by ANY kit scalar-layer change (no ruling
> needed); moves the default text on its movers; re-pins its
> `arms.tsv` rows; yes, an abi event; a spec change only where a stated
> limit moves. The `memfn-off` text and `off.tsv` no longer exist (row
> 3 is withdrawn). The stamp row's movers are NATIVE-form changes only
> (§L.5).

> **`[rev4.3]`** The stamp row follows §R4.3.3.
> - **`MEMFN_FORMS`** moves on SIMD-on artifacts (`-fmemfn-simd`)
>   whenever a SIMD form, a carried level or a site's form id changes.
>   Default artifacts read `none` until R4f.
> - **New row, `<PREFIX>_MEMFN_LIBC`**:
>   - regenerated by any change in which libc functions an artifact's
>     search code names;
>   - it moves one line per mover;
>   - its readers are C11's libc assertion and the bench's bucketing;
>   - yes, it is an abi event (emitted text);
>   - its GRAMMAR is spec, its values are not.
> - **New row, the site manifest** (`tests/memfn/site_manifest.tsv`):
>   - regenerated by each migration step's REPLACE commit;
>   - it moves no emitted bytes;
>   - C17's counts move, re-pinned in the same commit;
>   - no abi event and no spec change.

---

## 22. The build order, revision 4, and the plan-row text `[rev4]`

> **`[rev4.6]`** The r5 panel's fixes (§R4.6) land as `[rev4.6]` marks
> in the `[rev4.3]` block's R4a′, R4c, R4d and M7 rows and in "Filed,
> not scheduled". No step, prerequisite or trigger changes, except
> R4a′'s trigger reading (B7).

> **`[rev4.5]`** R4b is DONE and R4d's trigger is MET at SIMD-off
> (§R4.5.1). Every older block in this section that describes R4b as
> pending, R4d's trigger as unmet, or the abi as "the next number (61 at
> ...)" is history. The `[rev4.3]` block's rows carry the `[rev4.5]`
> marks that bring them current. The older blocks are not rewritten.

As before, each step separates its PREREQUISITE (a step that must have
landed) from its TRIGGER (a measured cell or a ruling). Nothing that
moves a DEFAULT emitted byte opens before its trigger (D77), and native
text stays opt-in until R4f.

> **`[rev4.4]`** Applied to the block below (D147 addenda 8-9):
> - **R3:** Q43-Q49 are RULED; the open questions are Q53-Q55 only.
> - **R4a:** `memfn/src/options.def` (the kit's option registry, with
>   `mf_options()` and `mf_opts_check()`) is born EMPTY with the
>   skeleton, and `--list-axes`' `memfn` section prints its header with
>   no rows. The floor check is declared UNREACHED until R4d (§R4.4.1).
> - **R4d:** its own `--memfn=no-NAME` row is the first registry row, so
>   the spec floor is born here. Q44 (the dial: `--tune` -2/-1 send
>   `MF_P_SIZE_LEANING`, ruled as a D103 diff with the movers census at
>   those positions) and Q45 (the spec's second limit names whose libc
>   was measured) are discharged in this step's spec hunk.
> - **R4e′:** Q49 applies as written (`[D155]` except R4e′.0b, §R4.9.2.6). There is no abi bump at landing,
>   and its pins, its `test-axes` arm and C9's floor are born in that
>   commit. Q43: aarch64 forms are not accepted (§17.2).
> - **Filed, not scheduled:** OPTIONAL SITES (Q48), as ruled.
> - Wherever the block below says `--memfn-deny=NAME`, read
>   `--memfn=no-NAME`.

> **`[rev4.3]` THE BUILD ORDER, REVISION 4.3** (supersedes the `[rev4.2]`
> block and the rev 4 list below wherever they differ). It folds in D147
> addenda 1-7.
>
> - **Triggers come in two kinds.** A MIGRATION step (zero movers) is
>   triggered by COMPLETENESS (Q42 reversed: its prerequisites landed,
>   no performance cell). A MOVER step keeps a measured trigger and G1's
>   alpha at both layers (D77, D144).
> - **The switch** is `memfn-simd`, default OFF (§R4.3.1).
> - **Status** is at main 7f94b0cd. `[rev4.5]`: abi and R4b/R4d statuses are current as of main 08caf4a3, per the marks below.
>
> - **R3, rulings.**
>   - RULED: Q35-Q42 and Q50.
>   - REJECTED: Q51 and Q52.
>   - Open: Q53-Q55 only (`[rev4.4]`: Q43-Q49 RULED, addenda 8-9).
> - **R4a, the kit's code skeleton** (`memfn/`, whose non-code half is
>   set up):
>   - `memfn.h` (`MF_SITE_ABI` 2, `MF_VOCAB` 2, `MF_NS`);
>   - `mf_art`/`mf_emit`/`mf_call`/`mf_flush_helpers`/`mf_includes`/
>     `mf_stamps`;
>   - the generic scalar row with G2's generated-space tests;
>   - K1 reference functions and `PROVENANCE.md`;
>   - the Makefile wiring, with C15/C16 born;
>   - **the site manifest `tests/memfn/site_manifest.tsv` and C17 born,
>     every row `pending`** (§R4.3.4).
>
>   pcrec links the kit and calls nothing, and no byte moves.
>   **Prerequisite:** none. **Trigger:** MET (Q35/Q36).
> - **R4a′, the stamp event** (§R4.3.3, §18.3): `<PREFIX>_MEMFN_FORMS
>   "none"` and `<PREFIX>_MEMFN_LIBC` on every artifact.
>   - The LIBC value comes from the pending sites, via
>     `mf_art_note_libc`. That makes it non-`none` today on every
>     artifact that names `memchr`.
>   - abi → the number current at landing, with §18.3's readers found
>     by grep (`[rev4.6]`, r5 B8: no literal; main's abi is the
>     handoff's, f116cff5);
>   - the spec hunk (both grammars) and a bench inbox note.
>   - **`[rev4.6]`** (r5 B2, B5) The spec hunk and the inbox note state
>     that the bench attributes kit state by the build recipe it
>     records (abi, pcrec commit, argv; §R4.4.1), and that
>     `MEMFN_LIBC` is a source-level inventory, not a promise of a
>     dispatched call (§R4.3.3).
>
>   **Prerequisite:** R4a. **Trigger:** MET (Q39 ruled; Q53 confirms
>   the libc line's spelling before the build). **`[rev4.6]`** (r5 B7)
>   Read: MET for the stamp; the libc line's spelling is gated on Q53.
>   **`[rev4.7]`** Q53 RULED YES (D147 addendum 10): the trigger is MET
>   for both lines, in §R4.3.3's refined form.
> - **R4b, the first customer's measurement** (R-1 in
>   `memfn/docs/requests.md`; probe only).
>   - SIMD-off: the SWAR fused form against `emit`.
>   - SIMD-on: the vector fused form against the SWAR form.
>   - Both regimes, on the post-handoff build.
>
>   It now feeds R4d's trigger only, not M1's. **Prerequisite:** none.
>   **Trigger:** `lane/k82hbuild` merged (MET, f116cff5) and
>   alpha-accepted (Linux alpha OWED).
>
>   **`[rev4.5]` DONE** (R-1: main 08caf4a3, merge 348c0a49; Linux
>   `R4B-DONE status=0`; `memfnr4b_report.md` §9). Results: R4d's
>   trigger is MET on union-select (below); the lead order is part of
>   the composite site's form (§15.5); K85's dense-text find-all loss is
>   removed by the fused forms, and single gate calls on dense text
>   still lose at SIMD-off. The "Linux alpha OWED" above is read
>   through §16's `[rev4.5]` note.
> - **R4c, M1** (composite PRE site + the offset-skip trio, zero
>   movers; Q41).
>   - Implement, then replace. `DELEG_SITES` gets its `use` column.
>     **`[rev4.6]`** (r5 A2) At most a CEILING column; `mf_site.use` is
>     set per instance from `req_use(cx)`, and C10 checks per instance
>     (§14.5).
>   - **`[rev4.6]`** (r5 A4) The REPLACE commit re-points every mech row
>     whose `SAB_BEFORE` lives in a migrated emitter, into `memfn/` or
>     onto pcrec's remaining half, and states the count (about 28 at
>     abi 61). `emit_req_handoff` is split: S464 goes kit-side; S463,
>     S470, S471 and S472 stay pcrec-side (§16 item 4).
>   - **`[rev4.6]`** (r5 A7) I2 must reach the VM hybrid handoff route
>     (§15.5). Its witness artifact is OWED here.
>   - The `memfn-simd` pair joins `strategy_denials`. Inert until R4e′:
>     both readings render the same text and are reported as
>     "identical (no SIMD form)".
>   - `arms.tsv` is recorded.
>   - Checks: C4, C5, C10, C11, C12 (9 → 3), C13, C14, and C17 (its
>     rows flip to `delegated`). I2 runs over every axis and both
>     comment tiers.
>   - Afterwards, edits to the migrated emitters are kit work.
>
>   **Prerequisites:** R4a′; `lane/k82hbuild` merged (MET); K85
>   re-measured on the post-handoff build (OWED). **Trigger:**
>   completeness.
>
>   **`[rev4.5]`** K85's re-measure is MET (§R4.5.5 item 1); R4a′ is
>   the remaining prerequisite.
> - **R4d, the first movers:** the kit's SWAR fused composite, a
>   SCALAR-layer change.
>   - It gets its own `--memfn=no-NAME` row (`[rev4.4]`), is accepted on
>     SIMD-off, and reports SIMD-on (identical until R4e′).
>   - The stamp stays `none` (it is SIMD-off text). Any `MEMFN_LIBC`
>     change is recorded.
>   - The spec hunk carries §10.6's limits.
>   - **`[rev4.5]`** The form carries the LEAD ORDER (§15.5): lead first
>     when a lead is present. Run-first needs a pcrec fact that does
>     not exist (filed below). The form is not selected for early-hit
>     single gate calls on dense text.
>   - **`[rev4.5]`** D149 (§8.6 K-7): the form starts from the plain
>     loop. Its unroll is measured or compiler-chosen. R-1's `swar` 2x
>     unroll is the first labelled unmeasured default
>     (`probes/twins/tb_r4b.c`).
>   - **`[rev4.6]`** (r5 A1) The design states the lead's need per
>     route: OPTIONAL on DFA-scan routes, REQUIRED on no-DFA routes
>     (K65, §14.5). A run-first arm that folds the lead still decides
>     it over the whole window before any miss, and never returns a hit
>     with a REQUIRED lead untested (§15.5 item 6).
>   - **`[rev4.6]`** (r5 A10) The design names
>     `tests/codegen/run_prechecks.sh` §5.11 and S460, which pin
>     lead-first in pcrec's suite. When run-first lands they re-home to
>     kit-form checks (G2, C5) or relax.
>   - **`[rev4.6]`** (r5 A3) The spec hunk (D80) re-specifies
>     `<PREFIX>_REQ_RUN`'s `@idx` and the run-route `<PREFIX>_REQ_BYTE`
>     as pcrec's rarity PICK, and the `[OPT-REQPOS]` note splits into a
>     fact half (pcrec's) and a form half (the arm's) (§14.9).
>   - **`[rev4.6]`** (r5 B3) Its SIMD-off movers are expected to read
>     `MEMFN_FORMS "none"`. C11's FORMS half stays UNREACHED until
>     R4e′.
>
>   **Prerequisite:** R4c. **Trigger:** R4b's cell. **`[rev4.5]` MET at
>   SIMD-off on union-select:** `swar` beats `emit` past the floor in
>   both regimes, 1.4-2.0x (§R4.5.1 item 4).
> - **M1b, runcmp migrates** (zero movers). Bit 43 crosses (§14.10), and
>   `RUN_WORDS` becomes the kit's stamp. **Prerequisite:** R4c.
>   **Trigger:** completeness.
>   **`[rev4.8]`** Request R-5, lane m1b: the contract is §R4.8
>   (Q-M1b-1..8, `MF_SITE_ABI` 4, `stamp_int`). **BUILT on `lane/m1b`
>   (2026-10-07)**: implement-then-replace, `src/gen/runcmp.c` deleted,
>   VERIFY and VMRUN `delegated`; I1 and the Mac sweeps read 0 movers; the
>   Linux verdict (`probes/lxrun/memfn_m1b.sh`) is the merge gate
>   (`docs/dev/lanes/m1b_report.md`).
> - **R4g, M2: PF migrates** (zero movers). K84's `strcmp` readers are
>   fixed (§19 row 7), and §19 row 6's rarity half becomes the kit's,
>   byte-identical at migration. C12: 3 → 1. **Prerequisite:** R4c.
>   **Trigger:** completeness. **PF movers** follow, triggered by U-2
>   AND a Linux cell whose time is in `pf_emit_bcls`.
>   **`[R4g]` BUILT on `lane/r4g` (2026-10-07)**, implement-then-replace:
>   DELEG_SITES row PF, the kit's `pffind` arm (four rows with
>   `uses`/`serves`), `pcrec_emit_find` the site builder (§15.7 `[R4g]`);
>   the I1 shadow comparator and the shape compiles read 0 movers. K84's
>   readers were already fixed on main (START-SET stage 1). §19 row 6's
>   rarity half is NOT moved: G1's elision (`req_byte_dominated_by`) is a
>   pre-check admission, which main's clearance keeps pcrec's; it waits for
>   a ruling (r4g_report.md). C12: `emit_dfa.c` memchr 2 → 1, walk-fmt
>   1 → 0 (the design's "3 → 1" counted before R4c). The identity gate on
>   post-C4 main is the merge gate.
> - **R4h, M3: STAY, the scan edge's loop and VMSPAN at stride 1**
>   (zero movers; ADVANCE with `count`/`peek`/`floor`). **Prerequisite:**
>   R4c. **Trigger:** completeness. **In-loop movers** follow, triggered
>   by U-3 AND a Linux cell dominated by class runs.
> - **M4, MLINE** (`(?m)^`'s `memchr('\n')`, §15.7's shape; zero
>   movers). C12: 1 → **0**. **Prerequisite:** R4c. **Trigger:**
>   completeness (Q42 reversed).
> - **R4j, M5: the planner moves LIVE** (§R4.3.5). It is byte-identical
>   by M5's own comparator; the frozen copy is that comparator only, and
>   pcrec stops computing `plan_hint`. **Prerequisites:** R4c, R4g.
>   **Trigger:** completeness.
> - **M5′, the ruled adoption event** (Q40). It is an abi event:
>   - pcrec keeps one semantic row, and the kit plans;
>   - the reseed is unconditional;
>   - `DFA_PREFILTER` reports pcrec's row;
>   - it carries a movers census, the spec hunk (`REQ_BYTE`'s meaning)
>     and a bench inbox note;
>   - acceptance is G1's alpha at both layers.
>
>   **Prerequisite:** M5. **Trigger:** RULED (Q40), accepted by its
>   alpha.
> - **M6, the remaining VM searches:** ~~N6 (`vm_rev_emit`'s backward
>   walk)~~ (**N6 RETIRED, D147 add. 12**: not a search site) and the VM span at stride > 1. Zero movers, and an `MF_VOCAB`
>   bump for the backward walk with captures in flight and the strided
>   SKIP (the bump no longer applies to N6). **Prerequisite:** R4h. **Trigger:** completeness.
> - **M7, N7** (the encoding seam's span compare). Zero movers.
>   **Prerequisite:** M1b. **Trigger:** completeness, once Q54 rules
>   its seam (**`[rev4.7]`** ruled YES, D147 addendum 10). **`[rev4.6]`** (r5 B6) It carries an `MF_VOCAB` bump (a
>   run-time-operand `mismatch` with a prefix-count return), and C17's
>   static scope gains `src/enc/` (§R4.3.4).
>   **`[M7]` BUILT** (lane m7, 2026-10-08; §15.8): N7 `delegated` for the
>   byte-wise compares (exact under both encodings, the byte backend's ASCII
>   and UCP caseless), through D58 addendum 2's site token and keyed side
>   table; utf8's caseless walk split out as **N7U** (`pending`, Q-R8-1);
>   C12's two span-index rows deleted (5 -> 3 rows); C17 14 rows, 11
>   delegated / 3 pending (N6, VMSTRIDE, N7U; N6 since retired, D147 add. 12).
>   **`[M6]` BUILT for VMSTRIDE only** (lane m6, 2026-10-08; §15.9; R-10
>   cut by ruling): the strided span is the existing SKIP / ADVANCE over W
>   SET terms (`MF_SITE_ABI` 8, NO `MF_VOCAB` bump); VMSTRIDE `delegated`,
>   the lazy rmin prefix listed as **VMLAZY** (`pending`, Q-R10-7); C12
>   3 rows (walk-open out, span-count in); C17 15 rows, 12 delegated / 3
>   pending (N6, N7U, VMLAZY). N6 waited on Frank (Q-R10-1); **RETIRED (D147 add. 12)**: C17 14 rows, 12 delegated / 2 pending (N7U, VMLAZY), C12 2 rows.
>   **`[R-12]` BUILT (lane vmlazy, 2026-10-09):** VMLAZY migrated by
>   re-expression (NORMALIZE abi 72, then a zero-mover REPLACE) and its row
>   deleted; VALID listed `pending` (Q-R12-5). C17 14 rows, 12 delegated / 2
>   pending (N7U, VALID), C12 2 rows (span-decode, swar-hibit); N7U HELD for
>   Frank's ruling (Q-R12-3). **Ruled (D147 add. 14): N7U RETIRED**; C17
>   13 rows, 12 delegated / 1 pending (VALID), C12 1 row (swar-hibit). `docs/dev/lanes/vmlazy_report.md`.
>
>   **End state: C17 reads 0 pending, and C12 reads 0 in every class
>   outside the kit.**
> - **R4e, ON_CAND's first customer.** Filed until a measured cell
>   (twins.md T-A's iterate-in-place lever on a real site). C13 goes live
>   then.
> - **R4e′, SIMD forms behind `-fmemfn-simd`** (default OFF).
>   - The kit's SIMD forms for the migrated sites, including any
>     cascade (§R4.3.2, K-6). Each must beat the CURRENT scalar layer at
>     its sites, and a cascade must also beat the single-level form.
>   - C9 at `-fmemfn-simd`, with its floor born.
>   - `test-axes` and I2 arms for the opt-in.
>   - No DEFAULT byte moves (Q49). `MEMFN_FORMS` carries ids on
>     `-fmemfn-simd` artifacts.
>   - The spec hunk states the no-portability-promise meaning.
>   - The bench `pcrec[simd]` testee is requested (D78).
>   - **`[rev4.5]` The 16 B short-path note** (R-1 §9). At AVX2, `ffl`
>     loses to `swar` by +0.64 ns (userpass pc16) and +0.36 ns
>     (cls-n-uc pc16). Short spans belong to the scalar form, inside
>     the SIMD-on cascade or short path (K-6). Everywhere else `ffl`
>     wins, at SSE2 and AVX2.
>
>   **Prerequisites:** R4c (sites migrated); R4d where its sites are
>   concerned (SIMD is measured against the current scalar).
>   **Trigger:** `[OPT-SIMD]` opened (D119: SIMD last; `[rev4.9]` superseded, D147 add. 11).
>
>   **`[rev4.9]` R4e′ is REPLACED by §R4.9** (D147 addendum 11, request
>   R-9). It now reads:
>   - **What it is.** The SIMD layer as a PARALLEL path, delivered in
>     BATCHES, each its own request. Capacity is 1 SIMD lane to 2
>     migration lanes, and heavy slots go 2:1 through main, until M5′.
>   - `[r9 F-1]` **Step R4e′.0, the seam** (§R4.9.2.1): kit-only, zero
>     movers, its own request. `fn_rows[]` with BODY and PREFIX slots.
>     **`[R4e′.0]` BUILT** (lane r4e0, 2026-10-09, R-11; §R4.9.2.1's
>     as-built block).
>   - `[D155]` **Step R4e′.0b, the routing** (§R4.9.2.6): the FUNC's loop
>     becomes `<fn>__body` and the FUNC one call. It is a pcrec abi event
>     (RQ-6), measured as G1, and lands before batch 1.
>     **`[R4e′.0b]` BUILT** (lane r4e0b, 2026-10-09, abi 69 -> 70;
>     §R4.9.2.6's as-built block).
>   - **Batch 1** (§R4.9.7): rows `vrun-w32`/`vrun-w16` in `fn_rows[]`
>     for a FUNC part whose predicate is one RUN term and its site's only
>     predicate (PRE window with no lead; OFS run-pinned by its own cell).
>   - **Prerequisites:** R4c, M1b and R4g (landed); R4e′.0; `[D155]`
>     R4e′.0b; RQ-1
>     (`--memfn=`); RQ-2 (Q-R9-3 (a)); RQ-3 (neutrality, now
>     unconditional); RQ-4 (a tier-U slot); RQ-5, the bench submission,
>     before any line is ACCEPTED (`[r9 M-1]`). R4d is NOT a prerequisite:
>     whichever of R4d and a SIMD batch lands second re-reads the other's
>     layer (C19, STALE).
>   - **Trigger:** D147 addendum 11, plus each batch's own evidence cell
>     (batch 1: R-1 on union-select and mod-i). The old trigger "SIMD
>     last" is superseded.
>   - **The bar:** §R4.9.6.
>   - **Q49 applies:** no abi bump at landing and no default byte moves.
>     `[D155]` The routing's abi event is R4e′.0b's, not the batch's.
>     Pins, the `simd` sweep arm and its projections (`[r9 F-5]`), C9-x86's
>     per-level floors, C18, C-SEL, C19, C11's FORMS half, the CANDIDATE
>     records and the spec hunks are born in the batch's commit; the kit's
>     one `MF_SITE_ABI` bump (sink ops, `plan_pos2`) takes the next number
>     at landing (M6 takes 8).
>   - **The 16 B note above is re-read by §R4.9.1 F-R9-1.** At 16 B every
>     R-1 `ffl` cell ran the scalar path, so its ±0.4-1.7 ns are not AVX2
>     (`[r9 M-13]`: placement or the prefix's effect on code generation,
>     read against the null population). Short spans fall to the scalar
>     floor by the derived reach (§R4.9.3).
> - **R4f, the SIMD default flip** (`memfn-simd` `default_state` OFF →
>   ON). Its OWN ruled abi event (addendum 7, D112 shape). After it, the
>   DEFAULT artifact no longer promises to run on any target, and the
>   bench testee becomes `pcrec[no-simd]`. **Prerequisites:** R4e′; the
>   SIMD hold (D91/D119) lifted. **Trigger:** Frank's ruling. Its
>   evidence is a Linux alpha in which SIMD-on beats the current scalar
>   layer past the floor on mover cells, in both regimes.
>   **`[rev4.9]`** Addendum 11 lifts the SIMD hold for the OPT-IN layer
>   only. The default flip stays its own ruled event, so "the SIMD hold
>   lifted" reads as "Frank rules the flip". Its evidence is the
>   ACCEPTED rows' records (`[r9 M-2]`: C19's effective state, never
>   CANDIDATE or STALE; §R4.9.6) at the bench's DEFAULT recipe, where
>   only the levels the default `-march` enables are live (Q-R9-2).
> - **R4i, declared tokens (`--isa=`): WITHDRAWN as a pcrec axis**
>   (addendum 6). A target level is a kit form question. Re-opened only
>   by a ruling.
> - **Filed, not scheduled:**
>   - the deferred include anchor (§14.8);
>   - OPTIONAL SITES (Q48);
>   - `[rev4.5]` a pcrec "lead can reject" density fact (§15.5 item 2).
>     Trigger: a measured cell where run-first beats lead-first;
>   - `[rev4.6]` an always-present `<PREFIX>_MEMFN_OPTS` line (r5 B2;
>     §R4.4.1). Trigger: a bench consumer asks (or Frank rules it into
>     R4a′ under Q55);
>   - a fused N4 arm;
>   - FIND_SEQ and F8 `mismatch` by request;
>   - extraction, which waits for Q36's ruled trigger (a stable API
>     across several migration steps AND a real second consumer), with
>     §20.1's files moving unchanged.
>
>   M4 and N6 leave this list: they are scheduled (M4, M6); N6 was later RETIRED (D147 add. 12).

> **`[rev4.2]`** (D147; Q35/Q36 RULED 2026-10-05, §23) Prerequisites and
> triggers stand; the steps read:
> - **R3**: Q35 and Q36 RULED yes; Q37-Q49 and Q50-Q52 open.
> - **R4a**: its trigger is MET. The subtree's non-code half is set up
>   (`memfn/`: CLAUDE.md, README, LICENSE, the ledger pair, journal,
>   wake template; lane memfnsetup). R4a's own delivery is the CODE
>   (`memfn.h`, the generic scalar row with G2, K1, PROVENANCE.md, the
>   Makefile wiring, C15/C16).
> - **R4b**: filed as R-1 in `memfn/docs/requests.md`; reports SIMD-off
>   (SWAR fused vs `emit`) and SIMD-on (vector fused vs SWAR fused).
> - **R4c**: lands ONE axis pair (`memfn-native`), not three; records
>   `arms.tsv` only (no `off.tsv`); C5 is the vocabulary half plus the
>   per-change comparator from the first kit change on.
> - **R4d**: the fused arm is a SCALAR-layer change: its own
>   `--memfn-deny=NAME` (`[rev4.4]`: `--memfn=no-NAME`), accepted on
>   SIMD-off; SIMD-on reported. The
>   bench testee is `pcrec[simd]`, requested when R4e′ gives it movers.
> - **R4e′/R4f**: the native arm is measured against the CURRENT scalar
>   layer (already R4f's wording); after every later scalar-layer
>   change the native arms on its movers are re-read (§L.4).
> - **R4j**: the model moves as the SCALAR layer's planner (§14.9).

> **R1d REVISION 4 DELIVERED 2026-10-05 (lane memfndel4): `docs/design/memfn/integration.md` rev 4** — the r3 panel's 27 findings applied; the contract rebuilt from the emitters' actual shapes (three site forms EXPR/STMT/FUNC; ASSIGN and ON_MISS handoffs with pcrec's `on_miss`; indent, notes, pcrec's escapers through the sink; ADVANCE's counter and `peek`; `n − end_back` ranges with declared EMPTY outcomes; negative offsets under a `floor`; REQUIRED/OPTIONAL terms; ALL_PRESENT with a RETURNED predicate; per-artifact `mf_art` with helpers before first use and kit-written stamps), with every M1 site shape reproduced byte for byte (§15). Shipped denies' fates (§14.10); the D146 pricing list (§19); the stamp per Q3 on every artifact, its own abi event (§18); M1 narrowed (runcmp via a hook; M1b separate) and sequenced after the handoff and K85's re-measure (§16); G1 re-founded on a pcrec-side diff with a declared regime (§17.2); C9 with a header shim and floor; per-arm pins under tests/; two inbox files; `memfn-native` default OFF via `-fmemfn-native`; symbol policy and per-file provenance. Q35-Q49.
> - **R3** (rulings): Q35-Q49.
> - **R4a, the kit's skeleton in-tree** (`memfn/`): `memfn.h` (`MF_SITE_ABI` 2, `MF_VOCAB` 2, `MF_NS`), `mf_art`/`mf_emit`/`mf_call`/`mf_flush_helpers`/`mf_includes`/`mf_stamps`, the GENERIC scalar row with G2's generated-space tests (§14.6), K1 reference functions, LICENSE (0BSD), PROVENANCE.md, CLAUDE.md, the two docs files (§20.1). pcrec links it and calls nothing. No byte moves. C15 and C16 born. **Prerequisite:** none. **Trigger:** Frank's Q35/Q36 ruling.
> - **R4a′, the stamp's own event** (§18): `<PREFIX>_MEMFN_FORMS "none"` on every artifact via `mf_stamps`; abi N → N+1 with §18.3's readers; the spec hunk; the bench inbox note. **Prerequisite:** R4a. **Trigger:** Frank's Q39 ruling (it lands before R4c so that M1 stays zero-mover).
> - **R4b, the first customer's measurement** (probe only): twins.md T-B on Linux ON THE POST-HANDOFF BUILD, both regimes (§21.1), a PORTABLE (SWAR) fused composite variant beside `emit` and the vector `ffl`, on the K82 cells and on K85's `cls-n-uc`. **Prerequisite:** none. **Trigger:** `lane/k82hbuild` merged and alpha-accepted.
> - **R4c, M1: the composite PRE site and the offset-skip trio migrate, zero movers** (§16): implement (baseline arms, shadow comparator) then replace; `DELEG_SITES` with its `use` column; the three profile axes (§20.2) in `strategy_denials`; `tests/memfn/pins/{arms,off}.tsv` recorded; C4, C5, C10, C11, C12 (9 → 3), C13, C14; I2 over every axis and both comment tiers. **Prerequisites:** R4a′; `lane/k82hbuild` merged; K85 re-measured on the post-handoff build. **Trigger:** R4b shows the PORTABLE fused form beating `emit` past the floor on at least one K82 cell in its own regime, with no loss past the floor in the other.
> - **R4d, the first movers: the kit's portable fused composite arm** (lead + window in one pass; K85's general answer): abi event, stamp values on movers, the spec hunk with §10.6's four limits, G1 alpha (both regimes) on the pcrec-side movers, the bench `pcrec[memfn-off]` testee requested through the inbox (D78). **Prerequisite:** R4c. **Trigger:** R4b's cell. **`[rev4.5]` History: "lead + window in one pass" is not K85's general answer; the fused run filter with the lead first is (§15.5).**
> - **R4e, ON_CAND's first customer.** Filed until a measured cell (twins.md T-A's iterate-in-place lever on a real site); C13 goes live then.
> - **R4e′, native arms behind `-fmemfn-native`** (default OFF): the kit's ISA arms for the M1 sites; C9 at `-fmemfn-native` with its floor born; `test-axes` and I2 arms for the opt-in; no DEFAULT byte moves (Q49). **Prerequisite:** R4d. **Trigger:** `[OPT-SIMD]` opened (D119: SIMD last; `[rev4.9]` superseded, D147 add. 11).
> - **R4f, the native default flip** (`memfn-native` default ON): its own ruled abi event. **Prerequisite:** R4e′. **Trigger:** a Linux alpha in which the native arm beats the portable arm past the floor on a mover cell, in both regimes. This is measurable BEFORE the flip, because R4e′ exists: rev 3's circularity, where only the flip could produce the flip's evidence, is gone (r3 G-F11).
> - **M1b, runcmp migrates** (`pcrec_emit_run_compare` with its three callers; bit 43 crosses, §14.10; `RUN_WORDS` becomes the kit's stamp). **Prerequisite:** R4c. **Trigger:** a measured cell whose time is in a VM literal-run compare or a masked run compare that a kit form would change, or any kit arm that needs to fuse the run verify itself rather than through `run_cmp`.
> - **R4g, M2: PF migrates, then PF movers** (with K84's `strcmp` readers fixed, §19 row 7, and row 6's rarity half). **Prerequisite:** R4c. **Trigger:** U-2 AND a Linux cell whose time is in `pf_emit_bcls`.
> - **R4h, M3: STAY, the scan edge's loop and VMSPAN at stride 1** (ADVANCE with `count`/`peek`/`floor`, §14.3). **Prerequisite:** R4c. **Trigger:** U-3 AND a Linux cell dominated by class runs.
> - **R4i, declared tokens (`--isa=`):** HELD (linux_results.md §5).
> - **R4j, M5: the MODEL moves as the baseline's planner** (§14.9), byte-identical; then any non-baseline plan with its movers. **Prerequisites:** R4c, R4g. **Trigger:** a mover whose kit plan differs from pcrec's and whose G1 alpha beats it past the floor (Q40 rules adoption first).
> - **Filed, not scheduled:** the deferred include anchor (the first arm needing a header pcrec's predicate does not predict, §14.8); OPTIONAL SITES (Q48); M4 MLINE (Q42); a fused N4 arm; FIND_SEQ and F8 `mismatch` by request; N6; extraction (§11.1, with §20.1's files moving unchanged).

---

## 23. Questions for Frank, revision 4 `[rev4]`

Renumbered from Q35. Revision 3's Q24-Q34 were never ruled, and each is
re-derived below against the panel's findings rather than carried. §23.1
maps them. Each question has a recommendation.

> **`[rev4.9]`** The SIMD layer's design pass's questions are in
> §R4.9.10, with their recommendations. `[r9]` After panel r9: Q-R9-1 is
> RESOLVED by D144 addendum 4; Q-R9-2..8 were OPEN (Q-R9-2 and Q-R9-4
> revised); Q-R9-9 (D84's caps and guarded bytes) was NEW. `[D155]`
> Q-R9-1..9 are RULED (D155) and Q-R9-10/11 are RULED (D155 addendum 1).

> **`[rev4.2]` RULINGS (Frank, 2026-10-05, recorded with D147):**
> - **Q35 RULED YES.** §8 as extended by §14 is the design of record,
>   revised by panels as migration finds gaps.
> - **Q36 RULED YES.** The kit lives IN-TREE as its own subtree
>   `memfn/`: own CLAUDE.md, journal, two-file request ledger,
>   `pcrec_mf_*` symbols, 0BSD. A dedicated long-lived session may work
>   it in its own worktree. Extraction to a separate repository waits
>   for a MEASURED trigger: a stable API across several migration steps
>   AND a real second consumer (narrower than §11.1's "a second consumer
>   or a ruling"). Frank's reason: the contract is pcrec's own emitted
>   text and every kit byte move is a pcrec abi event, so the projects
>   are synchronous and tightly coupled, unlike the asynchronous bench.
>   Set up by lane memfnsetup (`memfn/`).
> - **Q38 is REVISED** below by D147, and **Q39 is re-derived as Q52**.
>   Q50-Q52 are new. Q37 and Q40-Q49 stand open as written, with Q40's
>   "baseline's frozen planner" read as the scalar layer's planner.

> **`[rev4.7]` Q53-Q55 RULED (D147 addendum 10, Frank, 2026-10-05), as
> recommended.** No question for Frank is open in this section.
>
> | Q | state | where |
> |---|---|---|
> | Q53 | RULED YES: a separate `<PREFIX>_MEMFN_LIBC` line in the refined form | §R4.3.3 |
> | Q54 | RULED YES: N7 `pending`, B6's three corrections, M7 bumps `MF_VOCAB` | §R4.3.4, §22 M7 |
> | Q55 | ACCEPTED: `MEMFN_FORMS` constant `none` until R4f, attributed outside the artifact; `<PREFIX>_MEMFN_OPTS` FILED, not built | below |
>
> The kit's own contract questions from G2 (Q-G2-1..17) were the kit
> session's to rule, not Frank's (D146). They are in §R4.7.0, and
> Q-G2-5 is the one left open.

> **`[rev4.6]`** Q53-Q55 are still the only open questions. Their text
> below is REFINED from the r5 panel (`2026-10-05-r5-memfn-rev45.md`,
> "Q53-Q55 for Frank"). This revision rules none of them.

> **`[rev4.4]` THE QUESTION LIST AFTER ADDENDA 8-9.** Q43-Q49 are RULED,
> and the only open questions are Q53-Q55. The table below is the rev 4.3
> list. Read its row `Q43-Q49` through this one. Each ruled question
> below carries its mark in place.
>
> | Q | state | where |
> |---|---|---|
> | Q43 | RULED YES (addendum 8) | §17.2 |
> | Q44 | RULED YES (addendum 9) | §22 R4d |
> | Q45 | RULED YES | §10.6 |
> | Q46 | RULED YES | §20.1 |
> | Q47 | RULED, REFINED: the kit's own `--memfn=` namespace | §R4.4.1 |
> | Q48 | RULED YES: file, don't build | §19 row 11 |
> | Q49 | RULED YES | §22 R4e′ |

> **`[rev4.3]` THE QUESTION LIST AFTER FRANK'S 2026-10-05 RULINGS (D147
> addenda 1-7).** No ruled question is renumbered.
>
> | Q | state | where |
> |---|---|---|
> | Q35 | RULED yes (D147) | §8 + §14 |
> | Q36 | RULED yes (D147) | `memfn/` |
> | Q37 | RULED yes (addendum 1) | §20.3 |
> | Q38 | RULED (addendum 2), then REPLACED by addendum 6 (one switch) and addendum 7 (default OFF) | §R4.3.1 |
> | Q39 | RULED yes (addendum 3), with addendum 6's libc record | §R4.3.3 |
> | Q40 | RULED yes, as revised by D147 (addendum 4) | §R4.3.5 |
> | Q41 | RULED yes (addendum 5) | §16 |
> | Q42 | RULED REVERSED: migrate every site, under a checked manifest (addendum 5) | §R4.3.4 |
> | Q43-Q49 | OPEN, as written (spellings per §R4.3.1); **`[rev4.4]` RULED, see above** | below |
> | Q50 | RULED yes (addendum 6) | §R4.3.1 |
> | Q51 | REJECTED (addendum 7) | §R4.3.6 |
> | Q52 | REJECTED (addendum 7) | §R4.3.6 |
> | Q53-Q55 | NEW, open | below |

35. **Q35, the contract (re-derives Q24).** Adopt §8 as extended by §14
    as the design of record:
    - the three forms, and the six handoffs with pcrec's `on_miss`;
    - REQUIRED/OPTIONAL terms with §14.5's promise;
    - ALL_PRESENT's `ret_pred`;
    - `n − end_back` ranges with a declared EMPTY outcome, and `floor`;
    - `mf_art` with helpers before first use and kit-written stamps;
    - totality through a generic scalar row;
    - pcrec's two tables (`DELEG_SITES` with its `use` column, and the
      profile first-match).
    
    **Recommendation:** yes. §15 shows that every M1 shape is
    expressible byte for byte, which is the property revision 3 lacked.
36. **Q36, where the kit lives (re-derives Q25), and its symbols.**
    In-tree `memfn/`, with external symbols `pcrec_mf_*` through
    `MF_NS`, C15 over `libpcrec.a`, and extraction on a second consumer
    or your ruling. **Recommendation:** yes. Atomicity (a kit change
    and its abi bump in one commit) is still the decisive reason, and
    the symbol policy is what makes "links into libpcrec" safe for
    users.
37. **Q37, the licence (re-derives Q26).** 0BSD for the kit's own text.
    Translated Rust `memchr` files take its Unlicense arm, with an SPDX
    tag and provenance per file and C16 holding the set to D145's list.
    **Recommendation:** yes.
    **`[rev4.3]` RULED YES** (D147 addendum 1): 0BSD for the kit's own
    text, with per-file Unlicense provenance for translated Rust `memchr`.
38. **Q38, the profile axes, polarity, and the baseline's permanence
    (re-derives Q27/Q28).**
    - `-fno-memfn-scan` and `-fno-memfn-loop` are deny axes, default ON.
    - `memfn-native` is a deny/force pair, default OFF, enabled by
      `-fmemfn-native`.
    - All three are in `strategy_denials`.
    - The baseline is frozen and changed only by a ruled abi event.
    
    **Recommendation:** yes, and keep the baseline forever. It is D146's
    OFF arm and the revisit-when witness.

    **`[rev4.2]` REVISED by D147.** The recommendation above is
    WITHDRAWN. The baseline is a per-migration-step byte-identity
    comparator only (§L.2): it is not kept as an arm, not the SIMD-off
    arm, and never pins the scalar layer. The revised question:
    - `memfn-native` is a deny/force pair, default OFF, enabled by
      `-fmemfn-native`, in `strategy_denials` (unchanged);
    - `-fno-memfn-scan`/`-fno-memfn-loop` are withdrawn (Q51);
    - the OFF arm of every kit change is its own published deny, and
      D146's revisit-when compares against the scalar layer the change
      replaced (§L.4).

    **Recommendation:** yes.

    **`[rev4.3]` RULED, then REPLACED.** Addendum 2 ruled this question
    with three profiles (`-fno-memfn-simd` / portable / `-fmemfn-native`).
    Addendum 6 replaced them with ONE switch and its meaning, and addendum
    7 made it OFF by default. The axis is `memfn-simd`, a deny/force pair
    (`-fno-memfn-simd` / `-fmemfn-simd`) in `strategy_denials` (§R4.3.1).
    The frozen pre-migration text is a per-step comparator only.
39. **Q39, the stamp (G-F1).** **`[rev4.2]`** Re-derived as Q52 (its
    reference compile, `memfn-off`, no longer exists). `<PREFIX>_MEMFN_FORMS` on every artifact,
    valued `none` iff the artifact is byte-identical to its `memfn-off`
    compile, else opaque form ids. It carries no kit version and no
    vocabulary number, is written by the kit, and is checked by C11
    against a pcrec-side diff. It is born in its own abi event (R4a′)
    before M1's replace. **Recommendation:** yes.
    **`[rev4.3]` RULED YES** (D147 addendum 3), with addendum 6's libc
    record. Q52's re-derivation is REJECTED (addendum 7). The value rule,
    the carried levels and the `<PREFIX>_MEMFN_LIBC` line are §R4.3.3.
40. **Q40, the scan plan and ADOPTION (re-derives Q29; r3 F9).** The
    plan (which term and position to scan, which to verify, the window
    cut, the byte pick) moves at M5 by moving prefix_k's MODEL into the
    kit as the baseline's frozen planner. That is byte-identical, and
    pcrec stops computing `plan_hint` only then. The open part is
    ADOPTION: whether an offset-set prefilter applies at all, which
    today decides `<PREFIX>_DFA_PREFILTER`'s value and whether the
    landing reseeds.
    **Recommendation:** at M5, T1 keeps one semantic row ("a necessary
    k-set beyond offset 0 exists") and `<PREFIX>_DFA_PREFILTER` keeps
    reporting pcrec's ROW, never the kit's plan. The kit's plan is
    visible through `MEMFN_FORMS`, and the reseed becomes unconditional
    on that row (it is sound for any landing). That is an abi event
    with a movers census and a bench inbox note. The alternative is to
    keep adoption in pcrec forever, which keeps `C_ENTER` and the 2×
    bar in `src/`, contra D146.
    **`[rev4.3]` RULED YES, as revised by D147** (addendum 4). The model
    moves LIVE at M5 (a frozen copy is M5's comparator only), and M5′ is
    the adoption event (§R4.3.5, §22). Q55 asks about the plan's
    visibility at SIMD-off.
41. **Q41, M1's scope and sequence (G-F10/G-F11).**
    - M1 is the composite PRE site plus the offset-skip trio. runcmp is
      reached through a `run_cmp` hook and becomes M1b, with its own
      trigger.
    - M1 runs after `lane/k82hbuild` merges and after K85's re-measure
      on that build.
    - After M1, edits to the migrated emitters are kit-lane work.
    
    **Recommendation:** yes.
    **`[rev4.3]` RULED YES** (D147 addendum 5). The trigger becomes
    completeness (Q42 reversed); the waits stand (§16).
42. **Q42, migrate without a customer (re-derives Q30).** M4, the
    `(?m)^` `memchr('\n')`. **Recommendation:** no, unchanged. The
    contract can express it (§15.7), and the ratchet keeps it at one.
    **`[rev4.3]` RULED, REVERSED** (D147 addendum 5): migrate EVERY
    search site, M4 included, with no performance customer. This is a
    ruled D77 exception whose trigger is completeness, and each step is
    zero-mover. It comes with a CHECKED SITE MANIFEST (C17: every
    emitted search site is `delegated` or `pending`, and any unlisted
    site fails the check). The `memchr(` ratchet's end state is 0
    outside the kit (§R4.3.4).
43. **Q43, aarch64 (re-derives Q31; G-F4).** There is no verdict-grade
    armv8 guard. The kit never default-selects a native arm on aarch64,
    and the spec states that aarch64 choices are unmeasured at verdict
    grade. **Recommendation:** yes, until you admit the Mac per cell
    (D144's loop protocol) or a quiet Linux aarch64 box exists.
    **`[rev4.3]`** OPEN. Read "native arm" as "SIMD-on form": the kit
    never default-selects a SIMD-on form over the scalar form on
    aarch64. Before R4f the default is SIMD off everywhere, so this
    question binds only `-fmemfn-simd` builds and the flip.
    **`[rev4.4]` RULED YES** (D147 addendum 8): SIMD-on forms tuned for
    aarch64 are not ACCEPTED until Frank admits Mac measurements as
    verdict-grade for those cells, or an aarch64 Linux box exists. x86
    Linux gives the verdicts. The SIMD-off (portable) layer is
    unaffected.
44. **Q44, the dial (re-derives Q32).** `--tune` -2/-1 send
    `MF_P_SIZE_LEANING`. **Recommendation:** rule it at R4d as a D103
    diff, with the movers census at those positions. Unchanged.
    **`[rev4.4]` RULED YES** (D147 addendum 9), as recommended.
45. **Q45, whose libc (re-derives Q33).** The kit measured glibc and
    libSystem, and musl inherits the result. **Recommendation:** state
    it in `docs/spec/` at R4d, as §10.6's second limit. Unchanged.
    **`[rev4.4]` RULED YES** (D147 addendum 9), as recommended.
46. **Q46, the request channel (re-derives Q34; G-F13).** Two files
    from day one: `inbox_from_pcrec.md` written only by the manager on
    main, and `outbox_to_pcrec.md` written only by kit lanes. A request
    is on main before its lane is briefed. **Recommendation:** yes.
    **`[rev4.3]`** OPEN. As built (lane memfnsetup), the files are
    `memfn/docs/requests.md` and `memfn/docs/responses.md`, with
    `[requests]` and `[responses]` commits; the roles are as stated
    above. **`[rev4.4]` RULED YES** (D147 addendum 9), as recommended.
47. **Q47, the kit's switches as axes (G-F2).** Each kit row with a
    deny is published by `mf_switches()` and becomes a generated axis
    row (`--memfn-deny=NAME`), listed, swept by `test-axes` and by I2.
    pcrec never spells the names. **Recommendation:** yes. It is D144
    item 4 for kit forms, without arch knowledge in `src/`.
    **`[rev4.4]` RULED, REFINED** (D147 addendum 9). pcrec keeps exactly
    ONE axis, `-fmemfn-simd`. The kit's per-form switches live in the
    kit's OWN option namespace, `--memfn=<opt>[,<opt>…]`, defined by a
    registry inside `memfn/` (not `axes.def`) and passed through
    uninterpreted. `--list-axes` prints a `memfn` section read from that
    registry: one enumeration point for `test-axes`, the identity gates
    and the registry check. A spec-pinned floor on the section's member
    count is the independent control. D144 item 4 is met inside the
    kit's namespace. §R4.4.1 is the design.
48. **Q48, OPTIONAL SITES (new, §19 row 11).** On a DFA route a run or
    byte pre-check is speed-only. Should such a site be marked OPTIONAL,
    so the kit may render NOTHING for it when it judges the gate useless
    (K85's dense-text case)? This would move "whether a speed-only gate
    exists" out of pcrec. **Recommendation:** file it, don't build it.
    Its D77 trigger is a K85-shaped cell that the R4d fused arm does not
    already cure. On no-DFA routes the gate is a proof and is never
    optional. **`[rev4.4]` RULED YES** (D147 addendum 9): file it, don't
    build it.
49. **Q49, an opt-in-only kit arm (R4e′).** Native arms land behind
    `-fmemfn-native` (default OFF), so no DEFAULT byte moves.
    **Recommendation:** no abi bump at R4e′. Its pins, its `test-axes`
    arm and C9's floor are born in that commit, and its `docs/spec/`
    hunk lands there (D80): `-fmemfn-native`'s output is
    caller-observable. The R4f flip is the abi event.
    **`[rev4.3]`** OPEN, with the switch spelled `-fmemfn-simd`. The
    R4f flip is now a ruled event (addendum 7), not a measurement's
    consequence. **`[rev4.4]` RULED YES** (D147 addendum 9), as
    recommended: no abi bump at landing; its own pins and axes.
50. **`[rev4.2]` Q50, where the scalar layer ends (D147, §L.1).** The
    layer line is §8.5's policy line, "no text that names an ISA". So
    SWAR is scalar, and a libc call is scalar even though glibc's
    `memchr` is vectorized internally; the SIMD layer is the kit's
    native arms. The alternative is a stricter SIMD-off that also
    excludes libc's vectorized calls. It would spell every emitted
    `memchr(` call (§9.3 I5's ratchet) as a byte loop, and it would
    measure a scalar layer that no shipped pcrec has ever been.
    **Recommendation:** the policy line as stated. libc is the
    platform's scalar contract, and pcrec's pre-migration forms already
    call it. D91's concern (a SIMD crutch hiding an algorithmic
    inefficiency) is met because every native arm must beat this layer,
    and this layer's own improvements are algorithmic.
    **`[rev4.3]` RULED YES** (D147 addendum 6): SWAR and libc are scalar
    layer. The switch's meaning is §R4.3.1, and a libc call is recorded
    by `<PREFIX>_MEMFN_LIBC` (§R4.3.3).
51. **`[rev4.2]` Q51, withdraw the `memfn-off` bits (D147, §L.3).**
    Drop `-fno-memfn-scan`/`-fno-memfn-loop`, family `memfn`'s
    `memfn-off`, `off.tsv` and the `pcrec[memfn-off]` bench testee. Each
    kit change's own deny (D144 item 4) is its OFF arm, checked at its
    commit against the parent. The alternative is to keep the bits as
    "deny every kit switch on that budget". That would keep migration-
    born forms reachable forever with no acceptance role, because D147
    forbids measuring SIMD against an old scalar and scalar changes are
    measured against their parent. **Recommendation:** withdraw (D77).
    A coarse kit-off switch can be built from the kit's option registry if a
    triage need is ever measured.
    **`[rev4.3]` REJECTED** (D147 addendum 7): the SIMD-off arm is not
    withdrawn, and D147's both-layers reading stands. The frozen-baseline
    bits stay withdrawn by D147 consequence 1. That reading is stated
    for checking in §R4.3.6.
52. **`[rev4.2]` Q52, the stamp re-derived (replaces Q39; §L.5).**
    `<PREFIX>_MEMFN_FORMS` on every artifact. It is `none` iff the
    artifact is byte-identical to its own `-fno-memfn-native` compile;
    otherwise it lists the native form ids. Written by the kit, checked
    by C11 against that pcrec-side diff, born in its own abi event R4a′.
    It carries no kit version. **Recommendation:** yes. It reports the
    layer fact D147 makes every reading carry, and it keeps M1 and every
    scalar-layer change zero-stamp-mover. The stated cost: scalar-layer
    forms are attributed by movers census and switch name, not by the
    stamp, until a bench consumer asks for more (D77).
    **`[rev4.3]` REJECTED** (D147 addendum 7): Q39 as ruled stands
    (§R4.3.3).
53. **Q53, the libc record (addendum 6, §R4.3.3).** **`[rev4.6]`
    Refined (r5 B4, B5); OPEN.** **`[rev4.7]` RULED YES, option (a) as
    refined (D147 addendum 10).** Should the stamp record the libc
    functions the artifact's code calls, and in what form?
    - **(a) A second every-artifact line, `<PREFIX>_MEMFN_LIBC`.**
      **RECOMMENDED**, refined:
      - it lists the libc functions the artifact's code CALLS (the whole
        artifact, comments and strings excluded), as a SOURCE-LEVEL
        INVENTORY, not a promise of a dispatched call;
      - fixed-size idiom loads (`memcpy` of a constant 1-8 bytes) are
        EXCLUDED, because they are register loads, not calls;
      - its control derives the names from the compile (`nm -u` of a
        `-O0 -fno-builtin` object, minus the same constant-size rule),
        and shares no source with the kit's or pcrec's lists; sabotage
        rows cover `memchr`, `memcmp` and `memcpy` (§17.6);
      - it is born with `MEMFN_FORMS` in R4a′.
    - **(b) A field inside `MEMFN_FORMS`.** Rejected by addendum 3's
      `none`-iff-identical rule: a SIMD-off artifact that calls
      `memchr` must read `none`.
    - **(c) "Search code only", as rev 4.3 wrote it.** Not recommended:
      no pcrec-side check can delimit "search code", so the control
      cannot be independent.
    - **(d) The inventory WITH idiom loads.** Simpler to check, but R4d
      would read `memchr` → `memcpy`, a misleading record.

    > `[rev4.6]` Rev 4.3 asked only (a) against (b), over "the search
    > code", checked by a text scan for the C9 shim's three names. The
    > r5 panel found that control's list does not match the record's
    > definition (B4) and that recording idiom `memcpy` loads misleads
    > (B5). Options (c) and (d) name those two choices.
54. **Q54, N7 under completeness (§R4.3.4).** **`[rev4.6]` Refined (r5
    B6); OPEN.** **`[rev4.7]` RULED YES, with B6's corrections (D147
    addendum 10).** Is the encoding seam's span compare
    (`$_span_match[_caseless]`) a site in the migration's sense?
    **Recommendation: yes**, listed `pending`, with B6's corrections:
    - the seam's owner is D58/DD-12, not D23;
    - the definition widens to "search or span-compare site";
    - C17 scans `src/enc/`, with a vocabulary line for the
      `s[at + i] != ref[i]` loop;
    - M7 bumps `MF_VOCAB` for a run-time-operand `mismatch` with a
      prefix-count return.

    The fold and the encoding semantics stay the encoding's, and the
    seam entry builds the `mf_site`, as a pcrec emitter does. The
    alternative, a third manifest state ("owned elsewhere"), is the
    half-migrated bookkeeping addendum 5 rules out.

    > `[rev4.6]` Rev 4.3 cited D23 and called N7 "a VERIFY over two
    > spans". It did not widen the definition, add `src/enc/` to C17,
    > or give M7 a vocabulary bump (B6).
55. **Q55, the kit's plan at SIMD-off (§R4.3.5).** **`[rev4.6]` Refined
    (r5 B1, B2, B3, A3, B11); OPEN.** **`[rev4.7]` ACCEPTED as
    recommended (D147 addendum 10); (b) `<PREFIX>_MEMFN_OPTS` is FILED,
    not built.** Addenda 3 and 4 together mean
    `MEMFN_FORMS` is constant `none` on every default artifact until
    R4f (B1). **Recommendation: accept that**, written down:
    - At the default build, a scalar-layer change (R4d, M5′, any
      re-plan) is attributed by its abi event's movers census and its
      `--memfn=no-NAME` row. The bench labels kit state by the build
      recipe it records (abi, pcrec commit, argv; B2, §R4.4.1).
    - C11's FORMS half is UNREACHED until the first SIMD-on form (B3).
    - pcrec's own stamps and notes stop describing the scan form
      (`@idx`, the run-route `REQ_BYTE`, the `[OPT-REQPOS]` note's form
      half) in R4d's spec hunk (A3, §14.9).
    - `<PREFIX>_DFA_PREFILTER_OFFSETS` already shows M5′'s chosen offsets
      (B11).

    The alternatives, each FILED with the trigger "a bench consumer
    asks":
    - (b) an always-present `<PREFIX>_MEMFN_OPTS` line carrying the
      `--memfn=` string. Cheap, D81-compliant, and free if born in
      R4a′.
    - (c) a third line naming the kit's plan, with its own abi event.

    If you want attribution IN the artifact now, (b) is the cheaper of
    the two and should ride R4a′.

    > `[rev4.6]` Rev 4.3 said the plan is visible in the stamp on
    > `-fmemfn-simd` artifacts and attributed at SIMD-off by the movers
    > census and switch name, with a plan line built only on request.
    > The r5 panel sharpened the tension (B1), added the bench's
    > attribution rule (B2), C11's UNREACHED declaration (B3), the
    > stamps that describe the form (A3) and the offsets stamp (B11),
    > and named option (b).

### 23.1 Revision 3's questions, mapped

| rev 3 | rev 4 |
|---|---|
| Q24 the contract | Q35 (extended by §14) |
| Q25 home | Q36 (+ symbol policy) |
| Q26 licence | Q37 (+ per-file provenance) |
| Q27 deny bits / baseline | Q38 (+ polarity, `strategy_denials`) |
| Q28 the default during the SIMD hold | Q38 (the default is now "axis not taken", not "deny set") and Q49 |
| Q29 prefix_k's constants | Q40 (the model moves; adoption asked) |
| Q30 MLINE | Q42 (unchanged) |
| Q31 aarch64 | Q43 (+ stated in the spec) |
| Q32 dial | Q44 (unchanged) |
| Q33 libc | Q45 (unchanged) |
| Q34 request channel | Q46 (two files now) |
| — | Q39 stamp, Q41 M1 scope, Q47 switches, Q48 optional sites (new) |

**`[rev4.3]`** Rev 4.2 added Q50-Q52. Rev 4.3 adds Q53 (the libc
record's spelling), Q54 (N7 under completeness) and Q55 (the plan's
stamp visibility at SIMD-off). Nothing ruled is renumbered.
