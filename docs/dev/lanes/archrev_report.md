# Lane archrev: the memfn kit's architecture review note (R-49, [KIT-ARCH-STEP] stage 2)

Tier opus. Documents only: no code, no make, no timing, no queue jobs. Branch lane/archrev, cut from
lane/memfn-arch at T = a0f13ad83a2432f14341831ba4d1ff68964b79d9.

## Summary

I wrote `memfn/docs/arch_review_2026-11.md`, a review of the existing kit's structure. It covers each of the four
sections R-49 names, judges each against docs/dev/guide/architecture.md (the four goals, the judgement section, the
register) and against the four kit principles, and ends with one consolidated list of suggestions, smallest first:
ARV-1 to ARV-15.

Findings in brief:
- **Goal 1 is the kit's strength.** There are 8 declared tables on one walk, `kit_walk`. A 72-member decider census,
  held by a check, lists 11 named exceptions, each with a trigger.
- **Strain 1: one file holds two modules.** `window.c` (4,672 lines) holds both the planner and the emitter. Inside
  the file they are already split by a record: the planner half writes no text, and the text half reads no decision
  state (C-3, C-4). The planner's primitives are split between window.c and presence.c, and each calls the other.
- **Strain 2: small questions spelled several times.**
  - "first member of a set": 5 spellings;
  - per-level vector op spellings: 3;
  - selector writers: 2;
  - deny channels: 2;
  - span vocabularies in `mf_site`: 3.
  The kit-internal renderer interface (`plan_hint`, `plan_pos`, `rank_*`) also sits in the public `mf_pred`.
- **The near triggers are NEON V and the next MF_SITE_ABI layout event.** NEON V appears only as a trigger event and
  is not designed here.

Not answerable from this lane:
- The kit memories R-49 names. The memory directory this lane can read is empty, so the note relies on R-49's
  wording and the records that quote the memories.
- Whether [SP1E-RENDERER-TABLE]'s "layer" key was dropped by a ruling. The row looks done but not closed.

## Note

Path: `memfn/docs/arch_review_2026-11.md` (STATUS: DRAFT, for review r91 `memfn-archrev`). Sections:
- header: T, requirements, rulings crossed, the memory caveat;
- §0 Summary;
- §1 Vocabulary;
- §2 Section A: the planner and its scenario/basic-unit layer (site map A1-A12, goals, suggestions);
- §3 Section B: the emitter, form tables, SIMD rows and per-CPU dispatch (site map B1-B11);
- §4 Section C: measurement cards and scripts (C1-C7);
- §5 Section D: the seam with pcrec (D1-D10);
- §6 Register rows looked up: 7b, 10 and 12 (A-PLAN, A-KIND, H-SITES), the WHERE drift in each, five proposed rows,
  and plan-row drift;
- §7 the consolidated suggestion list, ARV-1 to ARV-15;
- §8 Open questions for the owner (one: `window-file-split`);
- §9 the standing design questions;
- §10 Commands C-1 to C-37.

Also changed: `memfn/docs/CLAUDE.md` (an entry for the new file) and the lanes history index
(`docs/dev/history/claude_md/docs__dev__lanes.md`, N-1/D149).

Top suggestions, smallest first:

| id | suggestion | size, gate |
|---|---|---|
| ARV-1 | register row by reference for the census's 11 `EXC:` rows | S, doc |
| ARV-2 | move the `MF_SITE_ABI` changelog out of memfn.h and the CLAUDE.md files | S, doc |
| ARV-5 | one byte-set primitive family in kit.h | S, no-mover |
| ARV-6 | one selector writer | S, no-mover; trigger NEON V |
| ARV-9 | split window.c along `struct wf_plan`, with [SP1D-KITSPLIT-SEAMS] | M, no-mover |
| ARV-10 | one deny channel | S-M, kit event |
| ARV-11 | one per-level C-spelling table | S-M; trigger NEON V's architecture note |
| ARV-12 | the renderer interface leaves `mf_pred` | M, kit event |

## Charter coverage

| R-49 item | answered in |
|---|---|
| SCOPE: the planner and its scenario/basic-unit layer | §2 (site map A1-A12, goals, A-s1..A-s3) |
| SCOPE: the emitter and the form tables (scalar, SIMD rows, per-CPU dispatch) | §3 (B1-B11; B5-B7 for per-CPU dispatch) |
| SCOPE: the measurement cards and their scripts | §4 (C1-C7) |
| SCOPE: the request/response seam: the site description, C text and stamps, abi coupling | §5 (D1-D10; D7 stamps, D10 coupling) |
| SCOPE: the pcrec-side callers, read-only, to judge the seam | §5 intro and D8, D9 (no pcrec-internal change proposed; D9 recorded as observed only) |
| EXCLUDED items (pcrec internals, NEON V, in-flight designs, timing) | the header's "What this note is NOT"; NEON V appears only as a trigger |
| METHOD: one note at memfn/docs/arch_review_2026-11.md | done |
| METHOD: against architecture.md's four goals | each section's "Where it serves and strains each goal" |
| METHOD: the judgement section | ARV-1 (judgement (c)); the leave-it items (judgement (a), (d)); §8's leaning |
| METHOD: part 3, the register (rows touching kit sites, plus shapes with no row) | §6 (rows 7b, 10, 12 with drift; five proposed rows) |
| METHOD: the kit principles (facts not methods, basic units, plan as text seam, first-match tables) | each section's "Kit principles" bullet; A4 for the text seam; D4 and D6 for facts not methods |
| METHOD: per section, what it is / goals with file:line / suggestions ranked smaller-first with kind, size, trigger | §2-§5, each in that order |
| METHOD: suggestions filed, never built | §7 header; no code changed |
| REVIEW (r91, mode arch) | not this lane's: the manager launches it |
| COMPILER on the Mac / BOX | not applicable (no timing in this review) |

## STATE AT HANDOFF

STATE: done. Committed on lane/archrev. The rulings file `docs/dev/lanes/archrev_rulings.md` was re-read before the
commit and before this report; it was empty both times, so no entry was applied ("last entry applied: none").
OWED runs: none. `docs/dev/lanes/archrev_deliver.txt` is the manager's file and was left untouched.
