# Lane `ucpdes` — report

Opus, FEATURE tier, DESIGN. Branch `lane/ucpdes` from `main` at `4bb74bda`.
Nothing under `src/`, `cli/`, `lib/`, `tests/`, `docs/spec/`. No `make`, no
heavy suite (light 10.46 ssh-stdin probes, 10.48 local, `build/pcrec` copied
to a scratch dir for a handful of compiles).

## Delivered

- `docs/design/ucp_design.md` — the [UCP] design note, PROPOSED, light panel
  r1 applied.
- `docs/design/ucp_measurements/` — 5 probes, 9 transcripts, own CLAUDE.md
  (two instrument defects recorded).
- `docs/dev/reviews/2026-09-28-r1-ucp-design.md` — panel findings +
  dispositions (1 BLOCKER, 4 SHOULD, all applied).
- `docs/design/CLAUDE.md` rows for both.

## Decisions (UD-1..UD-8)

1. **Surface**: module `ucp`, opt-in (`--ucp`, `(*UCP)`, `.rxt` letter), not
   default under `-e utf8`. Lowering = the definitions table's `DEF_UCP` rows
   (D85's chartered hook), one tag per PCRE2 ASCII-restriction family, so
   `(?aD/aS/aW/aP/aT/a)` become real. Every UCP set is a verified 10.46 set
   equality (57/57), incl. NEW `[:graph:]`/`[:print:]` formulas (Cf minus a
   4-code-point carve-out). Caseless: `[:lower:]`/`[:upper:]` fold-INERT under
   UCP; per-contribution; ASCII-restricted sets fold by the ASCII fold.
   Byte tier = same definitions under the byte universe + Latin-1 fold.
   O-71: `-e utf8` ENABLES `unicode-props`+`ucp`; `(*UTF)` refused by name
   under `-e byte`.
2. **Normalize-then-recognize: ADAPT** — normalize to ONE node (`A_CTX`, set +
   side + truth function), not to text. `\b` builds it directly (identity-
   gated); one-character-language lookarounds reach it by recognition. Q1 no,
   Q2 yes, Q3 yes: 158 of 172 all-one-character lookaround patterns need no
   island.
3. **The island** = a character-stepped DFA mode entered through [OPT-EDGE]'s
   existing top-row stop test (no ASCII-path compare): decode, membership
   vector over the machine's non-ASCII sets (atoms), accept, resume; ⊥ for an
   ill-formed byte. UCP `\b` needs no new view kind. Serves UCP and
   [CLS-TREE]'s wide classes. Its SPEED vs a cache-resident all-byte DFA is
   UNMEASURED (size and compile-time wins are certain).
4. **Predicate forms**: the island asks for a membership vector; producers
   are the kit (first), an atom map (proposed kit member), the [UCD-RECORD]
   shared record via [XART-TABLES] — dial rows with named D77 triggers.
5. **[CLS-TREE]**: U0-U2 start now; the island (U3) needs S1 + S3, not S4;
   VM UCP `\b` (U4) needs S4.
6. **Staging** U0 → U1 → U2 → U3 → U4 with checks/abi/sabotage per stage (§6).
7. **Every selection is a first-match table** T1-T8 (§0.1), rows as listable
   data; the sectioning DP lives inside T6's `kit` row. **Panel GEN-1**: the
   context axis (`upc_of_class`'s if-chain) becomes a per-machine context-set
   TABLE with atoms — the same atom mechanism as the island (§2.4).

## Measurements (this lane, reproducible, Appendix A)

- 57 set relations × 2 versions, 0 missing their expectation (2 guessed
  expectations were wrong and are kept as recorded corrections).
- ⊥ context model vs 10.46 UCP|MIU: 209 agree / 0 disagree; controls fire
  (131, 6).
- Forward/backward segmentation: 3,368,421 strings / 0; controls fire
  (267,786; 1,895,172).
- Context-set census: 171/172 read one set; 156 byte + 2 utf8 all-byte-exact,
  14 need the island.

## Owed measurements (§7)

- Mac: U2 mover census + class-axis identity list (a1); per-machine atom-count
  census (a2); island twin correctness (a3); Latin-1 fold relation sweep (a4).
- **ubuntubudu (pcrecdev2 executor): b-island** — hand-twin island vs all-byte
  ns/char over ASCII / Latin / CJK / mixed; the D77 trigger for U3 and the
  input for θ. b-ctx — U2's moved patterns DFA vs VM, via the bench's AFTER run.

## Questions for Frank (§8, each with a recommendation)

Q1 UCP opt-in, not default under utf8 (YES). Q2 O-71 as suggested + `(*UTF)`
refused under byte (YES). Q3 refuse wide UCP sets and UCP `\b` under utf8 at
U1 until a kit-sized route exists (REFUSE). Q4 byte tier in U1 (YES). Q5
`(?a…)` knobs real at U1 (YES). Q6 U2 (`A_CTX`) ships under [UCP] before the
island (YES). Q7 U3 triggered by the b-island twin, θ proposed after it (YES).
Q8 [UCD-RECORD]/[XART-TABLES] stay unscheduled with named triggers (YES). Q9
oracle store config gains UCP at U1 (YES).

## Side findings

- `src/parse/parse.c:652-657` comment wrong in both halves (panel SEM-1); U0
  rewords it.
- Recommend a critic-run "no spiderweb" pass at the U2/U3 charter: the table
  rule arrived after the critics' reads; the lane self-checked (disclosed in
  the review).

## Disclosure

Session-root CLAUDE.md and the manager's memory index were present at spawn;
context only. pcrec-bench read-only (O-71). Critics were spawned without
names (the harness forbids a teammate spawning teammates); their reports
arrived after a resend request.
