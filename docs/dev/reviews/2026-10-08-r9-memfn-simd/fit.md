# R-9 panel, lens FIT / SIBLINGS / DOCS STALENESS (read-only critic)

Subject: integration.md rev 4.9 §R4.9 + every [rev4.9] mark (worktrees/r9d,
branch lane/r9d, base main 5ddd2f04) and docs/dev/lanes/r9d_report.md.
Compared against the kit as built on lane/memfn-m7 (worktrees/memfn: MF_SITE_ABI 7,
MF_VOCAB 3, M7 landed, M6 building) and R-10/M6 scoping (m6scope_report.md, responses.md).
Nothing was run except `gcc -E` on stdin and reads. Counts: 1 BLOCKER, 5 MAJOR, 9 MINOR.

## Findings

### F-1 BLOCKER (§R4.9.2 walk/ladder, §R4.9.7 batch 1): the batch-1 row cannot be a row of `arms[]` as the kit is built
Problem. §R4.9.2 says SIMD forms are rows of the existing `arms[]`, "no third table", and
batch 1's row 1 APPLIES to "a PRE composite whose preds[] is ONE predicate holding ONE RUN
term ... ASSIGN or ON_MISS", changing "only its FUNC part (rx_reqrun's body)". As built:
- The PRE composite is `precheck_arm` (STMT, ALL_PRESENT). Its FUNC part is NOT selected
  through `arms[]`: `precheck_define` (precheck.c:146) calls `ofs_fn_define` directly for
  each RUN predicate with an `fn_ref`. `ofsskip_arm` (FIND/FUNC/RETURN, DELEG_OFS) calls the
  SAME `ofs_fn_define`. So the text the SIMD form changes is produced by a shared internal
  renderer that has no row walk of its own.
- ASSIGN/ON_MISS are properties of the composite's use lines; the FUNC text is identical for a
  PRE window run and an OFS run-pinned prefilter (`ofs_site_define`: same consumer MF_C_ENGINE,
  same shape). A row keyed on "PRE composite" cannot be evaluated where the text is rendered;
  keyed on the FUNC predicate it silently also moves every OFS run-pinned site, a bin R-1
  never timed (§R4.9.7 itself lists OFS as FILED "no OFS cell timed"; §R4.9.6 item 3 forbids
  accepting a row on an untimed bin). The G1 census (pcrec-side text diff) would then show OFS
  movers that the APPLIES text says are excluded.
- "After a SIMD row is CHOSEN the composer CONTINUES the walk, collecting each later SIMD
  row, stopping at the first scalar row" is not first-match (one row executes). It is a
  decorator: the SIMD row must call the floor row's render and splice a prologue at the top of
  the FUNC body and (for STMT sites, "a later batch") wrap whole statements in #if/#else. The
  arms write straight to the sink (r4ccore; no capture), and no renderer exposes a prologue
  point. This is the "parallel mechanism / sub-walk" the house rule forbids, under a claim
  (§2.6, "rows, not a parallel mechanism") that it is not.
Fix. State the decomposition honestly before build. Either (a) make the FUNC part's form
choice an explicit row table (the FUNC op's rows: scalar `ofs_fn` first, then `vrun-w32`,
`vrun-w16`), selected inside `ofs_fn_define`, keyed on the predicate (one RUN term, window)
and on nothing about the parent; the batch-1 bin then includes OFS run-pinned sites and the
alpha times them (the bench has run-pinned prefilter artifacts), or (b) add a pcrec-stated
site/pred fact that says "this FUNC part serves a PRE window" and say that is a second
contract field (`ledger` it as RQ-n). In both cases express the ladder as ONE row carrying a
`levels` list (the row renders helpers+prefix for every level the guard text covers), not a
continue-the-walk collect, and name the floor-render seam it needs in `ofs_fn_define`.

### F-2 MAJOR (§R4.9.2 "the deny, per row", formdecl.opt, walk test 3): two existing deny mechanisms are ignored and a third is added
Problem. The kit already has two row-deny carriers: `mf_site.denies`/`mf_art.denies` (MF_D_*
bits, memfn.h:211-297; `rc_row.row.deny`, runcmp.c:180 `DENIED:<deny>`; the shipped
byte-moving kit change, run-overlap, is pcrec axis bit 43 crossed through one map table,
rev 4.8) and `mf_site.opts` (the `--memfn=` string; options.def, born EMPTY: 0 `MF_OPT` rows;
`opts` is read by no kit code today, only g2_gen.c sets it). §R4.9.2 uses only the string and
labels walk test 3 `DENIED (existing)`; in `select_arm` there is no deny test at all (it is
new there; only `rc_row_of` has one, via the bit mask). `mf_formdecl.opt` (a name into
options.def) then sits beside `rc_row.row.deny` (a bit) in the two tables the design says
"share one declaration". `mf_formdecl.layer` and `.budget` also duplicate the `layer` and
`budget` columns already in `mf_option` (options.def), with no check that they agree.
Fix. Say which carrier new kit denies use and why the run-overlap bit is the legacy exception
(Q47 ruled after it); give a SIMD row exactly one deny field (the `opt` name) and read layer
and budget through it from options.def (one source), or state the check that ties them.
Add `select_arm`'s deny test as new work and give it the same code as `rc_row_of` (see F-3).

### F-3 MAJOR (§R4.9.2 walk tests 1,2,5,6; INERT words): layer/policy/budget/reach are bolted on beside the row-contract gate, into two cloned walks
Problem. row_contracts.md rev 4.1 is the kit's per-row admission mechanism (uses/serves, R1/R2,
DECLINED with a field mask; H1 = "the kit hosts the general first-match engine; its profile
layer is the gate" with trigger "a real table wants to adopt it"). §R4.9.2 adds, for SIMD
rows, a layer test, a size-leaning test, a budget test, a reach test and a deny test, with new
trace words (`INERT:PORTABLE`, `INERT:SIZE`, `PRED_FALSE` reused for reach/budget), described
as "the existing select_arm, with two predicate columns added". Actually five of the seven
tests are new to the arms walk. `policy` is already a stated site field consumed by no kit row
(only `art->policy = policy`, compose.c:325; MF_P_PORTABLE_ONLY is never read). "A stated
value is a requirement; a row that does not serve it declines" is exactly a `policy` field in
fields.def (classes PORTABLE_ONLY / SIZE_LEANING / OTHER; scalar rows serve ANY, SIMD rows
serve none of the first two). `select_arm` (compose.c) and `rc_row_of` (runcmp.c) are already
two near-identical walks (deny, gate, predicate, trace); each new column lands twice.
Fix. Model layer/size/budget as `policy` (and `budget`) fields in fields.def with the existing
verdict words (DECLINED + field mask, hence N2's would_decline census and rows_check see
them); keep only `reach` as a row predicate (it depends on the row's VW and the site's T, so
it cannot be a field class). Extract the shared walk prefix (deny, gate, trace) once for both
tables. If instead INERT is wanted as a distinct verdict, justify it against the census and
update trace_format.md, rows_check and N2's reader in the same change. State that batch 1 is
the H1 trigger being met (or why it is not).

### F-4 MAJOR (Q-R9-1, §R4.9.5 items 1-2, §R4.9.6, simd_accept.tsv, RQ-4/RQ-5): the verdict regime predates Frank's official-vs-unofficial bench ruling
Problem. After r9d's base, the kit recorded (responses.md notice, 2026-10-08, commit
70366459, "RULING (Frank)"): short unofficial benches may run anywhere and are directional; an
OFFICIAL verdict, such as a SIMD form's acceptance, needs a pcrec-bench run (planned and
coordinated through main; the dev box can host it). Also the bench box is a Ryzen 5 1600 (Zen
1, AVX2 as 2x128, no AVX-512); kit priority is 16 B SSE first, AVX2 next (smaller gains
expected there), AVX-512 filed. r9d's design makes the dev-box taskset/SMT-idle slot the
VERDICT (Q-R9-1 (a), "the box that gives verdicts", item 1) and ubuntubudu a "second box, a
disagreement is an issue row"; `simd_accept.tsv` records a "verdict box"; RQ-5 calls the bench
testees "the batch gate's wide reading". Under the ruling that protocol is the unofficial
tier that decides what to submit, and acceptance is a bench reading on Zen 1 (w32's
per-call "MIXED" numbers come from that very box and are the ones that count).
Fix. Re-scope item 1/Q-R9-1: tier 1 (dev box, §R4.9.5 as written) = unofficial picks; tier 2
= the planned bench run = the verdict; acceptance records carry the bench pin and the bench's
CPU; Q-R9-1 becomes "which box hosts the official run" (Frank has ruled it must be the
bench). Re-read the w32 row's trigger against Zen 1. RQ-5 becomes a prerequisite of
acceptance, not of "the wide reading". The `MEMFN_OPTS` line (rev 4.6 Q55, FILED "trigger: a
bench consumer asks") is now plausibly triggered, since the bench must tell DENY/DISPLACED
arms from ON; say so.

### F-5 MAJOR (§R4.9.8 checks; §R4.9.6 records): five new check/record mechanisms are projections of one paired compile, and the per-row pin files are about to be five
Siblings and verdict.
- ON-vs-OFF paired compile over the same population, diffing different projections: G1's mover
  census (text diff), C-SEL (stamps minus FORMS + refusal keys), C11 FORMS half (FORMS vs the
  mover count), C18 (`-E -P -mgeneral-regs-only` text), and I2 at -fno-memfn-simd (OFF vs
  parent). Five members, each with its own population print and floor. emit_sweep already runs
  paired arms with pinned DIFFER cells (stc0; `--arms`), a stderr+rc stream (B0), and a stamps
  stream. Propose ONE emit_sweep arm `simd` (ON, OFF, plus the DENY arms) with named projections
  (text, stamps-minus-FORMS, refusal set, -E -P at -mgeneral-regs-only) and ONE mover census
  that feeds all of them (counted once, one K35 floor), instead of C18/C-SEL as new scripts.
- Per-row TSV keyed on the row name: rows.tsv, row_floors.tsv (already required to hold the
  same row set, run_rows.sh), arms.tsv pins, c12_ceilings.tsv, and now `simd_accept.tsv`
  (checked against rows.tsv by C19) and `pins/c9_floor`. Keep simd_accept.tsv separate (its
  grain is row x level x box x time) but give it NO new row-set check: run_rows.sh's existing
  one should read it; and make `c9_floor` a per-level column of row_floors.tsv rather than a
  new pins file.
- C9-x86 extends C9 (honestly named). "The answer sweep per level" (§R4.9.6 item 4, table row)
  and "the `test-axes` arm per level" (§R4.9.7 born list) read as the same thing twice; say
  one is the other.
- Not duplicates: C19 (comparator staleness, a new question) and levels.def (a new
  dimension). C19's shared source is honestly stated in §R4.9.9.

### F-6 MAJOR (§R4.9.7 filed list, STAY/EDGE/VMSPAN; R4.9.3): Q-R10-10 was routed to this panel and is not answered
Problem. responses.md (R-10 step 1 notice): "Q-R10-10, a SIMD note: a SIMD ADVANCE form needs a
numeric bound that ADVANCE lacks today. This goes to R-9's panel." The kit's ADVANCE render
takes `more` as a boolean text expression and `span_hi` as an iteration cap; a vector stride
needs the loop's numeric limit and the stride W. M6 (VMSTRIDE, MF_SITE_ABI 7 -> 8, building
now on lane/memfn-m6) reshapes exactly this contract (multi-term ADVANCE, MF_MAX_TERM 8 -> 32,
`span_hi` = iteration count, no silent stride default). r9d files STAY/EDGE/VMSPAN only as
"in-loop, short spans; AVX2 without a 16 B tier costs 8-16 ns at 16 B", never mentioning the
missing bound; a later SIMD ADVANCE row would force a second contract bump right after M6's.
Fix. Add the prerequisite to the filed row: "a numeric `limit` (and stride) the kit can read
for a vector ADVANCE; decide whether M6's MF_SITE_ABI 8 carries it (cheap now, one bump) or
state that SIMD ADVANCE waits for a further bump with its own trigger cell". Send Q-R10-10's
answer back through responses.md so M6's contract author sees it before the ABI is frozen.

### F-7 MINOR (§R4.9.7 filed list, §R4.9.2 op list): stale against M7/M6
- "N6, VMSTRIDE, N7 | not yet delegated (M6, M7)": N7 is delegated (M7 landed; MF_OP_MISMATCH,
  two mismatch rows in `arms[]`, utf8's caseless walk is the new pending row N7U); VMSTRIDE is
  M6 (MF_SITE_ABI 8, building); N6 is recommended RETIRED as not a search site (Q-R10-1, with
  Frank) and should not appear on a SIMD cell list at all. The lazy cursor rung's rmin prefix
  loop is a new pending span loop (Q-R10-7 YES).
- §R4.9.2 says `arms[]` serves "FIND, SKIP, ALL_PRESENT and DENSE"; the table now also serves
  ADVANCE and MISMATCH, and has 11 rows (ofsskip, precheck, precheck_assign, runcmp-adjacent
  pf_* x5, mismatch_inplace, generic). Row 3.. of the batch table omits mismatch_inplace and
  pf_memchr_back.

### F-8 MINOR (RQ-1, F-R9-6): verified genuine; scoped as a request; small gaps
Verified: cli/main.c and lib/pcrec.h carry no `--memfn=`; memfn_sites.c:153 sets
`s->opts = NULL`; options.def has 0 rows. It is a real pcrec gap, correctly filed as RQ-1 (not
designed into pcrec) and it restates §R4.4.1's already-ruled carrier (CLI, config, library
field, `mf_opts_check`). Nits: (a) "no kit row can have a reachable OFF arm" overstates;
kit tests (G2's `opts`) reach it, pcrec cannot; say pcrec-reachable. (b) The string needs a
composition rule (D93 / option_sets.md §2.5a: strings are "silent file-wins elsewhere"); state
it and whether `--memfn=no-vrun-w32` under `-fno-memfn-simd` is refused or inert (the walk
makes INERT:PORTABLE win over DENIED, so a DENY arm at SIMD-off is untestable; fine, but say
it). (c) RQ-1 also changes a public struct: it needs the lib/pcrec.h and spec hunk, say so.

### F-9 MINOR (header, rev number, CLAUDE.md): merge and numbering hazards
The kit tip's integration.md still tops out at REVISION 4.8 and annotates M7 with `[M7]` tags
(new §15.8 plus marks at §22's N7 line, the same §22 area r9d rewrites for R4e'/R4f). No
rev 4.9 exists there, so no collision today, but M6 will add its own §15/§22 text. Conflict
spots: the header paragraph, §22 R4e'/R4f vs the M7 annotation, filed-list line (F-7). The
manager should merge r9d onto the kit tip (not main 5ddd2f04) and tell the M6 lane not to claim
a revision number. docs/design/CLAUDE.md's `memfn/` entry stops at rev 4.4; r9d updated only
memfn/CLAUDE.md and docs/design/memfn/CLAUDE.md.

### F-10 MINOR (§R4.9.2 FUNC example): how the vector ops are spelled is not specified
The design shows `#if <guard w32>` helpers but not whether they use `<immintrin.h>`
intrinsics (an include inside the artifact), GNU vector extensions or builtins. This matters
for the self-contained artifact rule, clang parity (C9 on the Mac/ubuntubudu), C9's `-nostdinc
-isystem` shim (§17.3), and for MEMFN_LIBC (headers are not libc calls, but the record's
scan must not misread them). State it.

### F-11 MINOR (§R4.9.6, §R4.9.7, C19): the lifecycle of a landed-but-unaccepted row is undefined
§R4.9.7 says w32's "acceptance is open" yet "rows vrun-w32/vrun-w16 in options.def ... born
in batch 1's commit", while C19 is red for any SIMD row x level without a record. Define the
states (proposed, measured, accepted, re-opened) and whether an unaccepted row renders under
-fmemfn-simd. Natural rule: a row lands only with its record (w32 waits for its alpha), or a
`proposed` state is inert by a row predicate.

### F-12 MINOR (walk test 2, MF_P_SIZE_LEANING): pre-empts Q44 and makes an explicit flag silently inert
Q44 is ruled "the dial interaction is decided at R4d as a D103 diff"; MF_P_SIZE_LEANING is set
by nothing yet. §R4.9.2 already fixes SIMD rows as INERT under it. Under --tune -2/-1, an
explicit `-fmemfn-simd` would do nothing, with no diagnostic (option_sets.md wants constraint
rows that refuse/inert/derive and a stamp). Leave the behaviour to Q44's ruling, or put the
SIMD x tune cell into R4d's D103 diff and cite it.

### F-13 MINOR (§R4.9.8 C9-x86, §R4.9.7 per-level arms): the level list has no enumeration surface
levels.def is kit-private and unreachable by pcrec, `--list-axes`' `memfn` section lists
options not levels, and the sweeps (C9-x86, answer sweep, test-axes arm per level, G2 per level)
run at {x86-64, v3, v4}. That population is hand-listed in tests. Give the kit an accessor
(`mf_levels()`, like `mf_options()`) read by the harness, plus a literal floor, or say the
list is test-owned and add it to the K35 census. The `-march` names stay in tests (C4).

### F-14 MINOR (§R4.9.5 item 6): related existing row and measurement not cited
[EMIT-ALIGN] (plan.md, NOT TRIGGERED by bench O-69: "the per-process split is the CPU
governor at launch, not layout") is the sibling of r9d's placement control, and O-69 bears on
"min of 3 loops, median of 3 launches" and "one binary per arm". Cite both, so the
`-falign-functions=64 -falign-loops=32` band is the first instance of that row's step, not a
second ad hoc instrument; and note the governor cause in the transcript header (it already
records governor/boost).

### F-15 MINOR (§R4.9.2 stamp, floor rule, tuning.md §2.43): the stamp reports text, not behaviour
`vrun@w32+w16` says which levels were rendered; the live one depends on the consumer's
-march, and on a target with no level (Mac, aarch64 at batch 1) the stamp is non-`none` while
nothing runs. That is consistent with addendum 3 (`none` iff byte-identical) but the spec hunk
should say it, and G1's "movers" on the Mac are text movers only (the design says Mac checks
SIMD-off answers; add: stamp-only).

## Standing questions (docs/design/CLAUDE.md): answered, with these gaps
- Q1 regime: answered in substance (five dimensions, box/CPU/governor/glibc/gcc named). Gap:
  F-4 (the official tier) and F-14 (governor bimodality).
- Q2 independent control: answered with a table and plants; the one shared-source control
  (C19) is declared. Gaps: F-5 (the controls are five views of one compile), F-13 (population
  of levels).
- Q3 what moves on regeneration: answered per file; add: row_floors/c9_floor re-measure when
  a level is added; the bench pin in the acceptance record (F-4).

## What is sound
- F-R9-1 is correct against tb_r4b.c:314 (`n - pos < VW + T` returns f_swar, so every pc16 cell
  is scalar at both widths); F-R9-2 and F-R9-3 are the right corrections to R-1's reading.
- R-1 table cells copied into §R4.9.7 match readings.gcc.md (e.g. union-select gate 1m 364,078 /
  187,022 / 48,844 / 38,988, floor 1,073; mod-i sweep 1m 724,503 / 267,480 / 142,800 /
  128,456; mod-i gate 1m 73.35 / 75.75 / 21.84 / 17.41), the derived-reach and D149 table are
  disciplined, and K-1 (no lead shape) is the right fence.
- The floor rule and C18 are a good, independent idea: verified `gcc -mgeneral-regs-only`
  empties `__SSE2__`/`__SSE__`/`__MMX__` (and AVX2 with -march=x86-64-v3) while keeping
  `__x86_64__`/`__linux__`, and `-E -P` of an unguarded-vs-guarded pair is identical.
- The axis facts in §R4.9.4 match the tree (bits 48/49, masked, `pcrec_memfn_policy`), and
  RQ-1 is a real, correctly-scoped gap.
- The batch is small, evidence-gated (D77), keeps pcrec arch-blind (C4), uses no new axis and
  files everything without a cell; recommendations on Q-R9-4..8 follow the house rules.
- The three-question section is real, and the 2:1 capacity, D149 and Q49 are honoured.
