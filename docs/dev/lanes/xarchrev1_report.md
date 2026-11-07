# xarchrev1: target seam note rev 1 and filing review 2026-11-07 r1 (2026-11-07, lane xarchrev1, opus)

This is a docs-only lane. Nothing under `src/`, `cli/`, `lib/` or `memfn/` changed. Probes ran in
`$PCREC_TMPDIR/scratch/xarchrev1/`, using a `nice make -j4` build of the worktree (rc 0). No suite
was run.

## For the owner, in plain words

**Part 1. The review is filed.**
- The critic round on the target seam is now `docs/dev/reviews/2026-11-07-r1-xarch.md`, with its
  critic files beside it.
- Plan line-number cites were replaced by row tags.
- Spec line cites were replaced by section numbers.
- The round's two process lessons are now one sentence each in the critic skill and the critics'
  guide:
  - give a critic one narrow question, and replace a silent critic after 20 minutes;
  - compile every claim about emitted code at default flags, `-march=native` and clang.

**Part 2. The design note is at rev 1** (`docs/design/memfn/target_seam.md`).

What rev 1 now says, in short:
- **Targets.** pcrec keeps one target table. Each family (x86-64, aarch64) has a default list. The
  family-free `generic` target means no SIMD at all.
- **The flag.** `-fmemfn-simd` now just means "use the family's default list". The default (no
  SIMD) is unchanged.
- **CPU variants.** A CPU variant is one more compound part chosen by the existing controller, not
  a separate dispatcher.
- **No needless copies.** A pattern with no SIMD form gets no extra copy. That is about 99.5 % of
  patterns.

I checked three things by experiment:
- **The attribute spelling.** The review's fix for the build failures works. The new spelling
  compiled at all 6 compiler/flag combinations (gcc and clang, each at default, `-march=native` and
  x86-64-v4), with 0 wrong answers in 2.3 million checks. The old spelling failed at 3 of the 6.
  - Side effect: when the user compiles above the target, the "v3" copy can contain newer
    instructions. Clang put AVX-512 mask operations in it.
- **Today's `-fmemfn-simd` output is kept.** Building it as a single "x86-64 baseline" copy gives
  byte-identical machine code to today's at default flags (one pattern checked). The source text
  still changes, because the `#if` lines go away.
- **One new hazard.** A user who compiles with "no vector registers" (kernel style) and also asks
  for SIMD would now get SSE2 code. Today they silently get scalar. The note says such users keep
  the default.

**One reading I chose.** The brief says the x86-64 baseline "keeps today's bytes". With no `#if`
lines (D188 addendum 1), the SOURCE bytes cannot stay the same. I read it as "the compiled code is
the same", which the probe confirms. If you meant the source text, the two rulings conflict.

**Open for you:** whether the x86-64 default should later grow to two copies (baseline plus v3).
My leaning is yes, but only after a bench run shows v3 is actually faster.

## Disposition table

| id | where rev 1 applies it |
|---|---|
| F1 | §2: one target table and a first-match list table. `-fmemfn-simd` is an alias for the family default list and `-fno-memfn-simd` for `{generic}`. `generic` is separate from the `x86-64` baseline (sse2, admits w16). §0 restores the build-time sentence. §7 G2b: today's `-fmemfn-simd` object is kept (probe: `.text` identical) |
| F2 | §0 quotes the owner text apart from the manager's reading. §2 adds family rows; `--family` is an explicit input; host resolution is row 3 only. §8: every pin is taken at `--family x86-64`, plus one host cell. §2/§3: the guard is pcrec's `#error`, with one owner (the family row); levels.def keeps `needs`. §7 corrects rev 0 §9.3 (F2(e)) |
| F3 | §6.1: additive ISA list plus the clang `#pragma clang attribute` pair. A 12-cell probe matrix: additive compiles 6/6 with 0 bad of 2,305,644 checks per cell; `arch=` fails 3/6. The above-target consequence is stated (clang x86-64-v4: AVX-512 mask ops in the v3 part). The `-mno-sse2`/`-mgeneral-regs-only` consequence is stated |
| F4 | §5: `<prefix>__<T'>` stems; the bare stem is the controller's or the lone part's; `tag` is dropped from pcrec->kit (§3); full target names |
| F5 | §5: surface classification table (shared / per-artifact / controller = max or union / per-part / per-prefix types), plus a spec inventory by section |
| F6 | §6.2: a CPU variant is a compound part with a `cpu` predicate in the controller's rows; the elision fact (§3 `target_dependent`); parts × targets compose as rows. §6.4: D155 add. 6 / [MEMFN-RTDISPATCH] addendum text, PROPOSED |
| F7 | §6.2: per-call probe priced (0.44-0.59 ns) against an `rx_iter` layout bump; leaning per-call. Continuation rule stated. D165 item 5 argued, with its own named measurement as acceptance. Q5 ifunc |
| F8 | §3: the non-document remainder is listed (sink members, `mf_hooks`); [IR-FORM] member (4) owns it |
| F9 | §4: gate field `needs ⊆ features` replaces `FLD_policy`'s SIMD reading; why `nr == 0` holds; reader list by grep; `target` column for the in-flight formhash entry table, "the kit must hear this" |
| F10 | §3: picked the include-in-text form (no new fact); probed under gcc and clang, answers equal |
| F11 | §2: target NAME is the primary column; attribute, probe and features are derived; a table check against `gcc -march -dM -E`; admission `family && needs ⊆ features` (§3); `ms` keyed by measure_store `class` with [MEASURE-SET] fallback rows. (d), the fifth hand-kept list: tests take their target list from the table and keep their own expected-ymm control (§8) |
| F12 | §6.2: `__builtin_cpu_init()` on the not-yet-true path; isa_evaluation.md's caveats restored |
| F13 | §8: which-part observable plus forced-probe lever, cpuid control; per-part instruction census; compile cells; family-guard loudness cell; RAN floor per box; v2/v4 are not rows (§2) |
| F14 | §7: the default arm is the control, the vacuous `--extra -fno-memfn-simd` is dropped, the opposite arm is `-fmemfn-simd`. §9: real controllers, elision read from `MEMFN_FORMS == "none"` (not `.text` identity), size-only scope stated, figures from the probe (6019/672) |
| F15 | §8: test-time plan (generic + top part over the corpus, other parts over the SIMD subset) with a PLAN measurement at the build. §9: benefit trigger named (bench verdict, D144 add. 4) |
| F16 | §7: no dedicated event; `<PREFIX>_TARGETS` and the guard ride the first byte-moving step via declared moves |
| F17 | §0 split into quoted / cited / ruled-by-manager (RULE2-5, RULE2-4 via [IR-FORM] member (4)). §6.4 D146 addendum (RULE2-1). §6.3 RB-3/N-4/M-5/§1 item 5 (RULE2-6). §4 fact (b) PROPOSED, read off an in-region stamp (RULE2-7). §6.4 retires item 6 / Q-R9-10 / C18 (RULE2-8). §11 D153 overlap line (RULE2-9). §2 list spelling owed with [EMIT-ENTRIES] (RULE2-13). §11 D174 names deferred to [STAMP-REVIEW] (RULE2-15) |
| F18 | §4/§5: cites re-taken at 6fc4b6912, kit-branch drift noted (runcmp.c :542-544, `mf_fn`), `mf_reach_table` added to the exceptions |
| PROBE-8 | §7 PLAN: S derived at `{generic}` vs the full table at S's landing |
| D27 at build | §8: recorded as accepted |
| L1, L2 | applied in part 1 (`.claude/skills/pcrec-critic/SKILL.md` §5 and the soundness row; `docs/dev/guide/critics.md` round block) |

Draft decision text (not filed; IDs are the manager's): §6.4's two blocks.

**Tensions surfaced, not stops:**
- The "keeps today's bytes" reading above.
- D165 item 5 says a compound's parts stay `static`, but [XARCH-DEV] rules exported per-variant
  entries. Rev 1 treats those as exported TEST entries the controller never calls through, and the
  proposed addendum must say so.

## STATE AT HANDOFF

- STATE: done.
- Commits on lane/xarchrev1:
  - e54a59287 (review filed, lessons L1/L2);
  - the rev 1 commit (note, the design CLAUDE.md line, this report, the history index line).
- Rulings file `docs/dev/lanes/xarchrev1_rulings.md`: empty at every re-read. No entry applied
  (last entry applied: none).
- Probe artifacts (not committed): `$PCREC_TMPDIR/scratch/xarchrev1/p/` (the matrix
  `o_*`/`in_*`, `today.c`/`base.c` for the `.text` identity) and `tools/xform*.py`.
- Owed runs: none.
