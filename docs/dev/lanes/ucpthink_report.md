# Lane ucpthink — report

**Lane:** `ucpthink` (opus), branch `lane/ucpthink`, worktree
`worktrees/ucpthink`, off `main` at `13b7c202`.

**Charter:** plan.md [UCP], "thinking and testing now" (Frank 2026-09-28).
Study only.

**Deliverable:** `docs/dev/ucp_study.md` (§0 headlines, §A-§F as briefed,
§G side findings), with the harness and transcripts in
`studies/ucp_study/`.

**Index entries:** `docs/dev/CLAUDE.md`, `studies/CLAUDE.md`,
`studies/ucp_study/CLAUDE.md`, and a delivery note on plan.md's [UCP] row.

**Nothing touched** under `src/`, `tests/` or `docs/spec/`. No `make test`,
no mech. pcrec-bench was read only.

## What was run (all validation COMPLETE; nothing owed)

| run | where | result |
|---|---|---|
| code-point classifier, 39 spellings × {UTF, UTF\|UCP} | 10.48 local (C and Python forms, identical output), 10.46 over ssh stdin | 31 set relations, identical on both versions (sizes differ by Unicode version) |
| `\b`/`\B` vs lookaround spelling, 579,195 subjects × 3 modes | 10.48 local, 10.46 ssh | **0 disagreements**; marked-output sha1 identical across versions |
| pcrec drive of the same stream, 6 artifacts × {byte, utf8} | Mac, `build/pcrec` abi 43 | **12/12 streams equal to libpcre2's sha1** |
| point probes (46 rows) + Latin-1 UCP probe | both versions | identical answers |
| census: 3,659 unique corpus+bench patterns, default and `--no-captures` | Mac, compile-only, 3 workers, boxlock taken and released | tables in `census_*analysis.txt` |
| size probes (10 patterns × 3 engines) + rewrite sizes (4 bench patterns) | Mac, `gcc-16 -O2 -c`, object bytes | `sizes_13b7c202.tsv`, `rewrite_sizes_13b7c202.tsv` |

No timing numbers were taken. Darwin timing is not citable, and the memo's
throughput questions are listed as open (§F q7, the ubuntubudu route).

## Headlines (the memo's §0, condensed)

1. **Demand is dominated by `\b`.** 62% of the UCP-sensitive corpus
   patterns need `\b`/`\B`, and 32% of the bench's. The bench has 46 of 91
   sensitive patterns needing only small sets (`\d`/`\s`/small POSIX).
   There is no real-world UTF harvest yet ([UTF-RW] is not started). At
   least 7 of the bench's 29 wild imports come from Unicode-`\w`
   ecosystems (that attribution is unverified).
2. **Oracle semantics (10.46).**
   - UCP `\w` ≡ `\p{Xwd}` ≡ `[\p{L}\p{N}\p{Mn}\p{Pc}]`, `\d` ≡ Nd, and
     `\s` ≡ Xsp ≡ Xps.
   - Each POSIX class maps to a property; `[:xdigit:]` gains the fullwidth
     hex digits.
   - UCP does NOT change caseless literal folding under UTF.
     `(?i)[[:lower:]]` stops folding under UCP, while `(?i)\p{Ll}` folds
     either way.
   - UCP without UTF gives the Latin-1 sets plus 30 fold pairs.
   - PCRE2's own `(?aD/aS/aW/aP/aT)` knobs are a native partial UCP; pcrec
     accepts them today as no-ops.
3. **`\b` ≡ its lookaround spelling, exactly**, and pcrec agrees. As a
   rewrite, it moves 72% (default) / 85% (no-captures) of `\b` patterns
   from the DFA to the VM. Object size grows ×1.4-×1.9 on four bench
   patterns. Over `\p{Xwd}` the rewrite is REFUSED on every engine.
4. **Idea 1 fits the DFA's POSITION-VIEW mechanism** (`eolvar`/`endvar`),
   generalized to a predicate that reads the subject. It is
   direction-independent, so the reverse pass needs nothing special, and
   minimization already handles views as alphabet symbols. [OPT-EDGE]'s
   top-row renumbering would dispatch it. Seven hazards are named (H1-H7).
   General population: 492 of 1,101 no-captures VM rows are
   lookaround-only (bench: 17 of 49). This is [ENG-ISL]'s "VM in DFA"
   framing with a new zero-width island kind, and the same splice as
   [CLS-TREE]'s DFA seam.
5. **[CLS-TREE] is a hard prerequisite.**
   - `\p{Xwd}` costs 197,685 B on the DFA and is REFUSED on the VM
     (576 KB > 500 KB), so **`(\p{Xwd})`, or any captured UCP `\w`, is
     unbuildable today**.
   - `\p{Xwd}+` compiles in 66 s (99% in `make_state`'s closure).
   - The kit prices `\p{Xwd}` at ~5.3 KB.

## Side findings for the manager's triage (memo §G)

- **`(?r)` is silently ignored under `-e utf8`.** This is an answer
  divergence from 10.46 under UTF alone:

  | pattern | subject | 10.46 | pcrec |
  |---|---|---|---|
  | `(?i)(?r)k` | U+212A | nomatch | match |
  | `(?i)(?r)s` | U+017F | nomatch | match |
  | `(?i)(?r)[a-z]` | U+212A | nomatch | match |
  | `(?i)(?r)\x{212a}` | `k` | nomatch | match |

  The cause is `src/parse/mod_modifiers.c:405-406`, where `(?r)` is a
  no-op. The compliance record says it "becomes real under UTF/UCP". This
  is a tier-1 class issue, modifiers module, utf8 only.
- **`RX_ENGINE_WHY` takes the construct kind and the offset from two
  different sources** (`select_engine.c:327`: `first_dfa_excluding` vs
  `first_vmonly_pos`). For example, `x(?<=a)(?!b)` stamps
  "(?!...) at pattern offset 1", and offset 1 is the `(?<=`.
- **The `\p{Xwd}` DFA baseline has moved** (294,153 → 197,685 since
  `13b56a12`). A [CLS-TREE] design should re-baseline.
- **`\p{Xwd}+` and `\p{L}+` compile slowly** (66 s; the census held on
  `\p{L}+` for over a minute).

## For a resuming agent

There is nothing in flight. The open questions for the scheduled design are
the memo's §F list (9 items). If a follow-up round is chartered, the cheapest
next measurements are §F q6 (a machine-building census of lookahead
boundedness and view-variant counts) and q7 (throughput on ubuntubudu for
rewrite vs view vs exact). Every script in `studies/ucp_study/` takes the
pcrec binary as an argument and re-runs against a new pin.
