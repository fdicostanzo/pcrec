# ADD2 findings

Subject: docs/design/memfn/target_seam.md rev 0 (e2f9793d1), read against D188 Addendum 2 at 6fc4b6912
(decisions.md: the only change 5b43f8e9a..6fc4b6912 is that one bullet, `git diff --stat`).
Throughout, each consequence says which part it rests on: [OWNER] = the ruled owner text (the
sentences before "Manager's reading", including the quote and "The one thing denied (owner)");
[MGR] = the "Manager's reading (not ruled detail)" sentences; [NEITHER] = stated by neither.

## Findings

### ADD2-1 (CONFIRMED, design; effort small; blast radius §0, §1, §10) Q1 is now RULED; §0/§10 still list it OPEN
- Note §10:222-223 "OPEN: (Q1) mixed-family lists ... leaning: refuse, one family per artifact".
  §1:38 non-goal "a mixed-family artifact (§10 Q1)". §0:8-26 quotes Addendum 1 only.
- [OWNER] "a CPU FAMILY is the largest scope of an artifact ... the artifact is built for ONE family
  ... the kit never emits variants for other families"; and the denial of a single multi-family file
  (owner, same day). So Q1 moves to RULED and the non-goal becomes a ruled exclusion. The note's
  leaning is upheld, but its rationale "one compiler run targets one family" is not the ruled one:
  the owner's is scope ("the largest scope of an artifact").
- [MGR] (the workaround: one artifact per family, user's build selects by conditional compilation;
  the family guard makes a wrong pick loud) is a NEW item the note lacks, and should be recorded as
  the manager's reading, not as ruled ("The workaround, agreed" does not say who agreed; read it as
  agreed with the owner only if the manager confirms).
- Fix: §0 quotes Addendum 2 with the [OWNER]/[MGR] split; §10 RULED gains "one family per artifact,
  default = the family pcrec runs on, no other family's variants, no multi-family file"; PROPOSED
  gains the [MGR] items (family word, family guard, workaround); Q1 deleted from OPEN.

### ADD2-2 (CONFIRMED, answer-neutral but design/speed; effort medium; §5 "The list", §6) The default list `{generic}` is wrong for "use simd" and was already inconsistent with today
- Note §5:147 "the default list is `generic` alone"; §6:152-153 "the features are empty, so no
  level is admitted"; §6:164 "`-fmemfn-simd` artifacts DO move: their `#if` arms go away".
- [OWNER] "If they provided the rx and 'use simd' then compiled on a cpu family, it should build for
  that family" / "by default the family pcrec runs on". So with `-fmemfn-simd` and no list, the
  default is the HOST family, not `{generic}`. [MGR] adds that the variants are "that family's
  declared, stamped default list (Addendum 1)", chosen by the once-per-process dispatch.
- Pre-existing defect the addendum exposes (repro, this box, build tree 5b43f8e9a):
  `build/pcrec -fmemfn-simd -p rx -o c-fmemfn-simd.c --pattern '(?i)cat'` then
  `gcc -O2 -c` at default -march: `objdump -d | grep -c xmm` = 14, `ymm` = 0. gcc's default x86-64
  target defines `__SSE2__` (`gcc -dM -E`), so TODAY's `-fmemfn-simd` artifact RUNS the w16 rung
  (selector lines 165-171: `#elif ... __SSE2__ -> rx_mf1_ofsskip__w16`). Under the note's
  `{generic}` with EMPTY features, `-fmemfn-simd` would admit no level and become the SIMD-off
  artifact: the opt-in flag would silently become a no-op (a speed regression vs today, and a deny
  flag with nothing to deny). The note's §6 "their #if arms go away" understates the move.
- Consequence [NEITHER]: "generic" names two different things the note conflates:
  (a) the family-free portable artifact (no family, no guard, no level) and (b) the FAMILY BASELINE
  variant, which on x86-64 guarantees SSE2 and so admits w16 (levels.def:41-43 `test_march
  "x86-64"`). Under Addendum 2 the x86-64 family's default list is something like
  {x86-64 (baseline, w16), x86-64-v3 (w32)}; its fallback variant is the baseline, never portable C,
  because the family guard (ADD2-4) already excludes non-x86 compilers. Which members are in each
  family's default list (v2? v4, given AVX-512 is NOT filed?) is unstated by both texts and is
  pcrec's target-table row; the note's §7:176 "dev box runs generic, v2, v3 and v4" presumes members
  nobody declared.
- Fix: §5 states two defaults: no "use simd" (`-fno-memfn-simd`, today's default) -> family-free
  `{generic}`; "use simd" -> the host family's declared list [OWNER default + MGR list]. §2's
  `-fno-memfn-simd maps to the generic target` (line 60) stays; "generic = empty features" is kept
  ONLY for (a).

### ADD2-3 (CONFIRMED by grep + reasoning, design/maintenance; effort medium; §6 G2, §9.3, the stamp) What G2 keeps and what now moves
- G2 at default flags SURVIVES, if ADD2-2's split is taken: today's default is `-fno-memfn-simd`
  (repro: `build/pcrec -p rx` vs `-fno-memfn-simd`: the only diff is the `#include "<name>.h"` line
  17, i.e. the output name; bytes otherwise equal). The family rule [OWNER] is conditioned on
  "use simd", so the default artifact stays family-free and box-independent; only the stamp event
  (§6:159-165) moves it. [MGR]'s "the file carries one family guard" must NOT be read as applying to
  the family-free artifact, or G2 breaks AND default output becomes box-dependent (ADD2-5). Neither
  text says which; the note must.
- `-fno-memfn-simd`: does not move beyond the stamp event (same as default).
- `-fmemfn-simd`: moves far more than "#if arms go away": host-family variants (>= 2 on x86-64 per
  ADD2-2), a pcrec dispatcher at each public entry, per-variant stems/stamps (§3, §4), the family
  guard, and a family-bearing TARGETS stamp. This is the SIMD-on abi event of §6:164-165, but it is
  now also HOST-dependent (ADD2-5).
- The stamp: §6:160 `<PREFIX>_TARGETS "generic"` must carry the FAMILY as well as the list once a
  family exists (e.g. a family value and a member list) [MGR "declared, stamped default"; OWNER "ONE
  family"]: a reader of a SIMD-on artifact must be able to tell which family it was built for
  without the guard's text. Spelling is the manager's (DD-13b-style), the field's existence is not.
- §9.3:209-210 "A kit byte move under a non-default target is a pcrec abi event only for artifacts
  that list that target" — now the x86-64-v3 variant IS in the default SIMD-on list on every x86 host,
  so a kit move in a v3 form is an abi event for every SIMD-on artifact generated on x86. §9.3 also
  needs a new "what moves" row: regenerating the same input on a box of another family moves a
  SIMD-on artifact (ADD2-5).

### ADD2-4 (CONFIRMED text analysis, design; effort small; §2 text rule, §4) The family guard vs "no #if on CPU macros"
- Note §2:67 kit text: "no `#if`/`#elif`/`#ifdef` on CPU or ISA macros"; §1 G1:32 "zero `#if`
  lines"; §4:120-121 exempts only pcrec's `#if __has_attribute(noclone)` lines.
- [MGR] "one family guard that refuses compilation under another family (a loud refusal, not an `#if`
  code arm)". It IS an `#if` on CPU macros (e.g. `#if !(defined(__x86_64__) && !defined(__ILP32__))`
  `#error ...` `#endif`), so the rule as written forbids it. Reconciliation: the rule is about KIT
  text and CODE ARMS (alternative bodies); the guard is pcrec's, file-scope, once, emitted before
  the first pragma/`#include <immintrin.h>`, and has no `#else` body. §4's out-of-scope list needs a
  second exemption: "pcrec's family guard: a refusal (`#error`), not a code path". G1's grep-count-0
  must be scoped to kit text / variant bodies or it counts the guard.
- [NEITHER] The guard's predicate already exists, inside the kit: levels.def:42/45 guard strings
  are "family predicate && feature macro" (`defined(__x86_64__) && !defined(__ILP32__)` + `__SSE2__`/
  `__AVX2__`; the ILP32 exclusion for x32/i686 is levels.def:17-19's [r9 C-8] fact). The note's
  guard->needs conversion (§4:111) keeps only the feature half; the family half must move to whoever
  writes the guard (pcrec), and levels.def is kit-private (C4, levels.def:7-8) so pcrec cannot read
  it. Two owners of the x86-64 predicate would be two sources of one fact. Also levels.def ALREADY
  has a `family` column (levels.def:12-14, value "x86-64"), which the note's §2 table ("today:
  implied by `__x86_64__`", line 50) and §4 table do not mention. Fix: pcrec's family table owns the
  guard predicate (incl. the ILP32 exclusion, cited); the kit's `family` column becomes the
  admission key matched against target.family (level admitted iff family equal AND needs subset of
  features).

### ADD2-5 (CONFIRMED, design/maintenance; effort medium; §6, §7, §9.2; tests) The SIMD-on default is now box-dependent output — the first in pcrec
- [OWNER] "by default the family pcrec runs on" makes the same pcrec input + `-fmemfn-simd` emit
  different bytes on the Mac (aarch64) and the Linux box (x86-64). Today it does not: grep of
  src/ cli/ lib/ for `__x86_64__|__aarch64__|uname|__arm` = 0 hits; the kit emits the x86 `#if`
  arms on every host (repro artifact lines 89, 126, 165). So pcrec output has never depended on the
  generating host; this is new and neither text says so.
- On the Mac with no aarch64 level yet (levels.def:38-39 "every aarch64 level [is] born with its
  first row"), a SIMD-on artifact has ZERO admitted levels: MEMFN_FORMS empty, no dispatcher. Answers
  are unchanged (today's arms are dead there), but every BYTE/STAMP pin taken at `-fmemfn-simd`
  fails on the Mac: tests/cli/run_cli_tests.sh:2412-2451 ("-fmemfn-simd renders the vrun-w32 helper
  above vrun-w16 (MEMFN_FORMS vrun@w32+w16)"), tests/memfn/row_floors.tsv / simd_accept.tsv /
  run_simd_floor.sh (test-memfn-simdfloor, Makefile:1485-1488), emit_sweep's `--extra=-fmemfn-simd`
  arm DIFFER_PINS (emit_sweep.py:181, :503), tests/axes memfn_arm `simd`, mech sabotages S722/S723/
  S981/S1026/S1852. CI is Linux x86-64 only (ci.yml: no Darwin/aarch64 hit), so CI stays green and
  only a Mac `make test` sees it — the classic "population nobody counts" (K35).
- emit_sweep identity (`--ref`, same box both sides) still holds per box. Any CROSS-box byte
  comparison of SIMD-on artifacts (`--ref-bin` with a binary from another box; cross-platform
  verification; pcrec-bench comparing Mac vs Linux artifacts — SUSPECTED, not checked in the bench
  repo) breaks. Corpus `.rxt` expectations are answers, not bytes: unaffected (§9.2's oracle control
  holds).
- Fix (general form): the FAMILY is an explicit input of every check; the host is only the CLI/library
  default. Every SIMD-on test pin passes the family word (x86-64) explicitly, so the suite's bytes are
  box-independent; ONE named cell checks that the host default resolves to the host family and is
  stamped. Unlock: with the word explicit, Linux CI can emit (not run) the aarch64 artifact's text and
  pin it the day the first aarch64 level lands. Trigger: the first aarch64 level row, or the first
  Mac make test after the build.
- Tension to record [NEITHER]: D188's own Why (decisions.md D188 body) rejects behaviour that
  "depend[s] on the box it was measured on, not the box it targets", and the memory rule "no silent
  defaults" flags a USED default. The host-family default is owner-ruled, so it stands; the stamp
  (ADD2-3) is what keeps it declared rather than assumed (Addendum 1 "never assumed").

### ADD2-6 (CONFIRMED text, design/interface; effort small; §2 table, §5) The cross-compile family word: owner, home, and whether it is target.family
- [MGR] only: "a cross-compile names the family as one word". The owner text does not rule the word.
- It is a CALLER input (CLI flag / pcrec_options field), resolved by pcrec, never by the kit. It IS
  the note's `target.family` value, but at a different scope: the note §2:42-50 makes target.family
  a per-ART field "pcrec -> kit, per art". Under [OWNER] "ONE family" every art in an artifact has the
  same family, so it is an ARTIFACT-level fact (one value, copied into each art). Its value set loses
  `generic` (§2:50 lists `x86-64`, `aarch64`, or `generic`): generic is a variant/the family-free
  artifact (ADD2-2), not a family. The kit needs target.family only as the admission key (ADD2-4);
  features alone are family-specific tokens, so it is also partly redundant — keep it as the key,
  say so.
- Caller-observable -> D80 spec hunk in the same change; a new option -> [IFACE-PUSH] placement (or
  explicitly with the [XARCH-DEV] build); D174: named for what the caller sees (the family it builds
  for), not "memfn"/"kit". The note's §5:148 target table ("tag, family, features, attribute string,
  probe string") needs a FAMILY table above it: family word, guard predicate, default member list.
- [NEITHER] "the family pcrec runs on" is undefined: pcrec's own compiled-for family (its build
  macros) or the running CPU? They differ under Rosetta (an x86-64 pcrec on Apple silicon emits x86;
  the user's native cc then hits the guard — loud, so safe) and for libpcrec embedded in a build tool.
  Leaning: pcrec's compiled-for family (static, deterministic); state it.
- Also [NEITHER]: an explicit Addendum 1 list whose members span families is now a refusal (a clean
  diagnostic), and an explicit list without "use simd" — the note must say whether a list implies
  "use simd".

### ADD2-7 (CONFIRMED text, doc; effort small; §1 G3, §7) G3 and the per-box variant runs
- §1:34 G3 "callers shipping to mixed CPUs" -> now mixed CPUs WITHIN one family [OWNER]; mixed
  families are served by the per-family workaround [MGR].
- §7:176 "The Mac runs aarch64" -> the Mac generates (host default) and runs aarch64 artifacts only;
  an x86-64 artifact generated on the Mac by the family word cannot even COMPILE there (guard), so it
  is emit-only on the Mac. "The dev box runs generic, v2, v3 and v4" presumes undeclared members
  (ADD2-2). §7 needs one more cell [MGR guard]: compiling an artifact under a foreign family's
  compiler (or `-m32`/`-mx32` on x86) fails with the guard's message — the loudness the workaround
  relies on, otherwise unchecked. On one x86 box: `gcc -m32`/`-mx32` (if multilib exists) or `-E`
  with `-U__x86_64__` is a priceable stand-in.

### ADD2-8 (SUSPECTED, design; unlocks lens) Consequences neither text states, with triggers
- U1 SIMD-default event (D144 add. 4 / D147): the day `-fmemfn-simd` becomes the DEFAULT, the
  default artifact becomes host-family-dependent and G2 ("one target = today's bytes") becomes a
  per-family claim; CI x86-only then covers one family of the default. Trigger: that event's ruling
  must carry the family-word-in-every-pin rule (ADD2-5).
- U2 Makefile builds (examples/makefile, [REL-1.10]/D118): generation at build time on the build
  host gives the right family natively and a LOUD guard failure in a cross build (Yocto-style); the
  example should expose the family word as a make variable. Trigger: the first cross-build user.
- U3 The denied multi-family file: the user's selection `#if` (workaround) must use the SAME
  predicate as pcrec's guard (incl. ILP32), or a selection the guard accepts may differ; publish the
  predicate per family in docs/spec (it is caller-facing). Trigger: the [XARCH-DEV] build.
- U4 Measurement sets (D188 per variant): a set is now naturally per family; a set measured on a
  family not the artifact's is inapplicable, not merely unpriced. Trigger: the first aarch64 set.
- U5 Unlock: once family is a first-class input, the kit's levels.def can hold aarch64 rows with no
  `#if` and be EMITTED and diffed on Linux CI (text only) — a cheap pre-Mac check. Trigger: first
  aarch64 row.

## PROBED-AND-HELD
- decisions.md 5b43f8e9a..6fc4b6912: one-line diff, the Addendum 2 bullet only (`git diff --stat`).
- pcrec reads no host facts today: grep src/ cli/ lib/ for `__x86_64__|__aarch64__|uname|__arm`: 0.
- Default == `-fno-memfn-simd` byte for byte except the output-name `#include` line (1 diff line,
  `(?i)cat`): G2 at default flags is not touched by the family rule if ADD2-2's split holds.
- `-fmemfn-simd` `(?i)cat`: MEMFN_FORMS "vrun@w32+w16", three CPU `#if` blocks (lines 89, 126, 165),
  as the note §4 says; at default -march the w16 rung is live (14 xmm, 0 ymm) — basis of ADD2-2.
- levels.def: 2 levels, both family "x86-64", no aarch64 row (held: Mac SIMD-on has 0 levels).
- emit_sweep `--ref` builds both sides on one box: identity per box holds under host default.
- 3 compiles of pcrec, 1 gcc -c. No make, no suites.
