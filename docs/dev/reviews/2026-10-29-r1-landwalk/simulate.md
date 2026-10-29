# Critic `landwalk` — lens SIMULATE (opus), 2026-10-29

Subject: docs/dev/lanes/p1dsg_report.md @ 3afd1a439. Question: run the admission table over
real data; where does it mispick (soundness of the SELECT rows; selection over corpus/bench).
Independent model: `simulate/walk.py` (ideal walk semantics: starts(j) by libpcre2 anchored
`(?:P)L(?=<tail>\z)` per start, so context is the whole subject; `\G` spelled as a fixed
lookbehind to search_from; hats `cand` / `dfa` (reach guard forced to trip) / `lower`), oracle
libpcre2-8 10.46 via ctypes (`simulate/pcre2.py`). Nothing from p1dsg_evidence was read.

## Findings

### SIM-1 — CONFIRMED (answer, latent; doc/design): the UNIQUE sufficient form "`\b` with P's alphabet ⊆ `\w`" is false as stated
- **Where:** subject § "Admission table", paragraph **UNIQUE starts** ("Fixed width implies it. So do `\b` with P's alphabet ⊆ `\w`, ...; the census uses only these sufficient forms").
- **Claim tested:** with S reading P's groups, the per-hit attempt at s*(j) is exact when starts(j) has one member; `\b` + word-only P is offered as a sufficient form.
- **Repro** (`simulate/hand1.py`, `simulate/exhaust.py`, oracle libpcre2 10.46):
  - `\b(\w*)=x\1` (P = `\b(\w*)`, L = `=x`; exclusion holds: `=` ∉ alphabet(P)) on `"ab=x"`: starts(2) = {0, 2} (the empty `\w*` sees `\b` between `b` and `=`). libpcre2 (2,4) g1 (2,2); the excl-cand walk tries only s* = 0 → NOMATCH.
  - `(\w+)\b=x\1` (`\b` present but at P's END) on `"ab=xb"`: starts {0,1}; libpcre2 (1,5); walk NOMATCH.
  - Fuzz (`simulate/fuzz.py SIMDIR SEED N 40 wb`, seeds 5-7, 31, 32): with a `\b`-first word-only P:
    - **nullable P**: 178 wrong / 9,520 checks (238 patterns);
    - **non-nullable P**: 0 / 42,040 (1,051 patterns).

    Every observed starts(j) with two members (97 patterns) had a nullable P. Exhaustive `\b(\w*)@x\1`, subjects ≤ 6 over `ab@x␠`: 1,551 wrong / 19,530. The same pattern on the `excl-lower` hat: 0 / 19,530.
  - The `(?m)^` form held: 0 wrong / 27,040 checks (676 patterns, nullable and non-nullable P; seeds 5, 6, 21, 22), since `^` needs a `\n` that P cannot consume.
- **What is right:** the GENERAL rule ("no accepting state of rev(P) reachable from another accepting state, by-class accepts included") rejects both witnesses: the `\b`-conditioned accept at j reaches the accept at the run start. So the defect is in the stated forms. It affects every consumer that uses them: the census (which, by the report, uses ONLY the forms), the tests and sabotage built from them, and a reviewer who checks the build against them.
- **Fix:** state the forms exactly: `\b` FIRST in P, unconditional (not inside an optional, alternative or quantified group), AND P non-nullable. Likewise `(?m)^` first and unconditional. Or drop the forms and cite only the rule. Add `\b(\w*)=x\1` on `"ab=x"` to stage 1's answer net as a DECLINE witness.
- **Population exposure:** none found. Of 4,982 unique corpus patterns, the only `\b`-first patterns with a backreference are `\b(\w+)\b\s+\1\b` and its two siblings, which have no literal landmark (row 1). Bench: dup-param's P `\b(\w+)` is non-nullable and its `\b` comes first, so it is correctly unique.
- **Effort:** a doc line plus one test. **Blast radius:** the census, the stage-2 VM hat's tests, and any implementation that takes the forms as a shortcut.

### SIM-2 — SUSPECTED (answer, stage 2; design): positional accepts (`^`/`\A`/`\G`, the BOT family) are not covered by the UNIQUE rule's wording, and no admission row names them
- **Where:** subject § "Admission table" (UNIQUE rule: "by-class accepts included"; row 2 `g1` lists only "a lookaround the DFA cannot view"). Code: src/ir/nfa.c:1330-1350 (`pcrec_nfa_has_bot`: `\G`, `^`/`\A` SUBJECT_START, `(?m)^` "the reverse machine would need it at its termination boundary") and src/ir/dfa.c:789 (`\G` is a position bit that is "not a fact about the SUBJECT at all").
- **Witness (model):** `(?:^|-)([\w-]+)=\1\b` and `(?:\G|-)([\w-]+)=\1\b` on `"ab-cd=cd"`. Exclusion holds (`=` ∉ alphabet(P)). starts(5) = {0, 2}: 0 by the positional accept, 2 by `-`. libpcre2 (2,8) g1 (3,5). The per-hit attempt at s* = 0 gives NOMATCH, and `excl-lower` gives the right answer (`simulate/hand1.py`, last two lines).
  - Neither accept is a by-class accept. If W carries `^`/`\G` as a floor/position bit (as nfa.c says a reverse machine must), the rule as worded says UNIQUE, and row 6 hands CAND per hit.
- **Second gap:** today `pcrec_nfa_has_bot` routes such machines away from the reverse pass (both patterns stamp `RX_DFA_START "attempt-start"`; probed with `--emit-facts`). The design builds W "in the `revend_build_one` pattern", and REVEND declines `\G` (locate_finish §4.6 E8). Whether W declines BOT-family P or builds a floor accept is unstated, and the population does not say how it counted them.
- **Confirm:** state in the admission table whether a BOT-family node in P is a decline (row 2) or a floor accept. If the latter, count it as an accepting state in UNIQUE. Add the witness above to the stage-2 net.
- **Effort:** a doc row. **Blast radius:** the VM hat, P with `^`/`\A`/`\G` plus a backreference into P (small).

### SIM-3 — CONFIRMED (speed / doc; selection): no landmark-choice rule, and the existing fact picks the landmark that moves dup-param from `excl-cand` to `excl-lower`
- **Where:** subject § "The facts row" (value: "the landmark (which req fact, and its offset in the run)"), § "Population" (dup-param-detect listed as VM `excl-cand`, UNIQUE by `\b`), § "dup-param twin" (built on L = `=`).
- **Observed** (`build/pcrec --features all --emit-facts`, main 13056c942): dup-param has `req_set = 38,61` and `req_byte = 38` (`&`, "rate:builtin-prior"). With the fact pcrec already ranks first, L = `&`, so:
  - P = `\b(\w+)=[^&]*`. Exclusion holds, G4 holds, and starts are NOT unique.
  - The row is therefore `excl-lower`, a once-per-call LOWER(s*(j₀)), not the per-occurrence CAND the twin measured.
  - The per-hit hat on that split is wrong: `"a=1 b=2&b="` gives libpcre2 (4,10), per-hit NOMATCH (`simulate/hand1.py`).
- **Only the `=` split reproduces the claimed row, and the report never states the rule that picks it.** The same ambiguity applies to other rows: stack-frame (`req_set 32,40,41,46,97,116`, req_byte `a`, `req_run "at "@0`; `(` and `.` are both admissible inner landmarks with very different density), kv-quoted (`"` vs the run `="`; on loglines `"` is 314-351 B/hit with 3-4 % accepting, `="` is 8,161-10,190 B/hit with 100 % accepting; `simulate/density.py`), and qnt-plus-ctl (`b` vs the run `ab`).
- **Why it matters:**
  - The deciding row, the rarity price and the population all depend on L.
  - The census numbers are not reproducible from the text.
  - The x1.45 dup-param claim belongs to a split the build has no stated way to choose.
- **Fix:** add the choice to the facts row as a declared rule. Suggested: over every admissible inner landmark, take the first-match row rank (excl-cand > excl-lower), then the lowest priced density. Name dup-param's `=` and kv-quoted's `="` as the witnesses.
- **Effort:** a doc rule and its census re-run. **Blast radius:** every admitted row with |req_set| > 1. Of the 18 bench rows probed, 11 have more than one required byte.

### SIM-4 — CONFIRMED (doc; selection): `cls-s-nbsp` is fixed-width and must hit row 3 `fixed`, yet the population admits it as `excl-cand`
- **Where:** subject § "Population", bench DFA `excl-cand` list ("cls-s-nbsp / cls-s-ucp (5.5, utf8, ASCII `L`)") and § "Sensitivity" ("the five rows with a ratio of 5.5-7.5").
- **Observed:** `build/pcrec --features all -e utf8 --emit-facts=utf8 --pattern 'a\sb'` stamps `RX_DFA_START "end-minus-width"`, `req_landmark_maxoff = 2` and `RX_DFA_PREFILTER "offset-set"` with offsets `0,2*`. So the artifact itself treats `a\s` as width 2: the bench's manifest says `a\sb` is ASCII-scoped and misses NBSP. P = `a\s` is fixed-width, so row 3 declines it to the EXACT-k rows, which is where it already lives (offset-set).
  - `cls-s-ucp` (`(*UCP)`, maxoff 4, `reverse-pass`) is genuinely variable width and stays.
- **Effect:** bench excl-cand is 11, not 12. One of the "five rows at 5.5-7.5 whose admission the priced row must decide" is not the priced row's to decide. The census's width test evidently does not see the utf8 encoding's own width; check the corpus `fixed` count (105) for the same miss under utf8.
- **Effort:** census fix. **Blast radius:** utf8 rows with an ASCII-scoped class.

### SIM-5 — SUSPECTED (speed; selection): the rarity price compares against the wrong baseline for 9 of the 10 named DFA movers, which already start from the landmark today
- **Where:** subject § "Measurement card" (`p(L)·lwhit(wlen̂) < c(route) − lwbyte`, with c(route) "the DFA-step and VM-start rows the stop choice already reads", measured c ≈ 15.4 instr/B on 5b's byte-class path) and § "Build plan" ("Movers: bench 5b (x70) plus up to 9 DFA rows").
- **Observed** (`--emit-facts`, `simulate/bench_rows.tsv`): today's DFA prefilter stamps on the named rows are:

  | row | `RX_DFA_PREFILTER` |
  |---|---|
  | mask-email (5b) | `byte-class` (the only one that walks every class byte) |
  | kv-quoted | `handoff` (`RX_REQ_HANDOFF "32"`) |
  | dotted4, ipv4 | `handoff` (3) |
  | stack-frame | `offset-set-bounded` |
  | qnt-plus-ctl, cls-s-nbsp | `offset-set` |
  | csv5, qnt-plus, cls-s-ucp | `memchr` |

  On every row except 5b, the shipped search between landmark hits already runs at the find floor, and per hit it runs a forward DFA from j − maxoff (3..32 B).
- **The consequence:** landmark-walk's per-hit work on these rows is a reverse walk over the same ≤ maxoff bytes plus a forward verify, which is the same bytes plus a pass. The price `c(route) − lwbyte` (≈ 15.3 instr/B of headroom) does not exist there. So the row can admit rows where it cannot win, and the "up to 9 DFA movers" is unsupported.
- **Landmark density on the bench's own subjects** (`simulate/density.py`, bytes per hit / accepting share):

  | row | landmark | subjects | B/hit | accepting |
  |---|---|---|---|---|
  | ipv4, dotted4 | `.` | loglines | 50-65 | 66-76 % |
  | kv-quoted | `"` | loglines | 314-351 | 3-4 % |
  | stack-frame | `(` | loglines | 290-423 | 4-9 % |
  | qnt-plus | `b` | syntax | 136 | — |
  | cls-s-ucp | `b` | utf8 | 187 | — |
  | csv5 | `,` | bounded throughput | 0 hits | — |

  All are above the design's 19 B/hit break-even, but that break-even is against the 15.4 instr/B baseline these rows do not pay.
- **Confirm:** a twin vs shipped `instructions:u` pair on ipv4 and kv-quoted over loglines throughput.
- **Fix:** c(route) must be the route's PREFILTERED per-byte cost, read from the selected composite path (handoff / offset-set / memchr make it ≈ lwbyte). The relation table must also say what landmark-walk does to the DFA `handoff` and `offset-set-bounded` prefilters. It covers only the VM FIRST-slot handoff rows and the EXACT-k NEXT rows.
- **Effort:** a doc/price change plus one twin pair. **Blast radius:** every DFA row with a handoff, offset-set or memchr prefilter. That is most of the admitted DFA population.

### SIM-6 — SUSPECTED (speed, minor; design): one per-hit rarity price is applied to `excl-lower`, whose cost and benefit are per CALL
- **Where:** subject § "Admission table" row 5 (`rarity`, before rows 6 and 7) and § "Measurement card" (`lwhit` = walk + verify per hit).
- **Point:** `excl-lower` walks to the first accepting hit once per search call and hands LOWER(s*(j₀)). Its benefit is the bytes before s*(j₀), and its cost is one find plus the walks up to j₀. Neither is p(L)·lwhit per byte.
- **Example:** bak-1, `(\w+) \1` with L = space on syntax throughput, measured 6.6 B/hit, 94 % accepting. That is denser than the design's own negative control (fz-me, 10 B/hit). Under row 5 it should DECLINE, yet it is listed as admitted. As `excl-lower` it costs about one walk per call and gains nothing, because s*(j₀) is the first word.
- **Fix:** give `excl-lower` its own price (per call: expected skip vs one walk), or decline it until stage 2's card exists.
- **Effort:** doc. **Blast radius:** the 6 bench / 43 corpus `excl-lower` rows (stage 2 only).

## PROBED-AND-HELD

All against libpcre2 10.46 find-all (spans plus every capture), with the ideal-semantics model in `simulate/walk.py`.

**Hats.** Three hats were modelled:
- `cand`: one anchored attempt per hit at s*(j);
- `dfa`: `cand` plus the reach guard, forced to trip after the first failed verify, so the hand-off to search-from s*(j) is exercised;
- `lower`: search from s*(j₀).

A real build mixes per-hit attempts and guard trips; both pure strategies held.

**1. EXCLUSION arm (`excl-cand`, S reads no group of P)**
- Random P/L/S over the 8-byte alphabet `ab_=-␠\n@`, with:
  - classes, negated classes, `.`, `\w`, `\s`;
  - quantifiers, lazy forms, capture groups, alternation inside groups;
  - `\b`, `\B`, `(?m)^`, `(?m)$`, `\G`, and the 1-byte lookarounds `(?=a)`, `(?!_)`, `(?<=b)`, `(?<!=)`, `(?=\w)`;
  - one- and two-byte landmarks, including bordered (`==`) and partly-in-P (`a=`) ones.
- Result: **0 wrong / about 520,000 checks over about 6,500 patterns** (`fuzz.py`, families any/wb/bol, seeds 1-2, 5-7, 11-14, 21-22, 31-32; per-row tallies in `simulate/fuzz_{any,bol,wb}.log`).
- The rust #1354 which-occurrence shape never wins under exclusion. The periodicity argument holds: an overlapping earlier hit would put all of L's bytes inside P.

**2. `excl-lower` (S reads P's groups; LOWER(s*(j₀)) then search-from)**
- 0 wrong / 42,530 checks over 1,074 random patterns, plus these exhaustive cases:

  | case | checks |
  |---|---|
  | LF-E1 `(a+)X\1` on `"aaXa"` | the per-hit hat fails, `lower` is right |
  | `(?:([ab]+)@)+x\1` | 5,460 |
  | `(\w+)\b@x\1` | 19,530 |
  | `\b(\w*)@x\1` | 19,530 |
  | `(?:^\|-)([ab-]+)@\1` | 5,460 |
  | `(\w+)@\1` under utf8 | 19,607 |
  | dup-param split at `&` on `"a=1 b=2&b="` | — |

- The lower-bound argument (an earlier hit cannot be inside P by exclusion) held everywhere.

**3. UNIQUE forms**
- Non-nullable `\b`-first word-only P: 0 / 42,040.
- `(?m)^`-first with `\n` ∉ alphabet(P), nullable or not: 0 / 27,040.
- Fixed width is moot, because row 3 declines it first.
- The general accept-reachable-from-accept rule is sound by construction where every accept, positional ones included, is counted. Every model-observed |starts(j)| ≥ 2 is a path from accept to accept. See SIM-1 and SIM-2 for the gaps in the stated forms and the wording.

**4. Exhaustive adversarial splits** (`simulate/exhaust.py`, every subject of length ≤ 6 over the case's alphabet; 350,490 checks; all 0 wrong except the SIM-1 witness)
- L inside a quantified group: `(?:[ab]+@)+x`, plus the capture/backreference and `\b`-unique variants.
- L twice in R, with the first one chosen.
- A lookbehind in P that reads L's byte.
- A lookahead in P past L (`[ab]+(?=@x)@`): exact in the model. pcrec routes it to the VM (`RX_ENGINE_WHY "(?=...)"`), so row 2 `g1` declines it on the DFA route as the design says. The 1-byte forms `(?=@)`, `(?<=b)`, `(?<=,)` and `\b` stay `dfa`.
- `\G` alone and in a group, with `\G` held at search_from per locate_finish E8.
- `\K` in P and in S.
- An alternation prefix ambiguity in P.
- Negated classes on both sides.
- A bordered three-byte L (`@x@`), and a two-byte L with one byte in P.
- Lazy P.
- Caseless with a non-letter L.
- `(?m)$`, a possessive and a lookbehind in S.

**5. Find-all restart and empty matches**
- R is never nullable (L is non-empty), so every restart is at the previous end. Context at the floor is read from subject[lo−1], and in the model `\b`/lookbehinds see the previous match's bytes.
- 0 wrong across all of the above (every check is a find-all).

**6. utf8 with an ASCII L** (`simulate/utf8chk.py`)
- Subjects over {a, é, NBSP, @, x, space, KELVIN SIGN}, length ≤ 5; patterns `[^@]+@x`, `\w+@x`, `a\s@`, `(?i)k+@x`, `\b\w+@(\w)`, `(\w+)@\1`, `.{1,2}@x`.
- Result: 0 wrong / 254,891 checks. Floors and starts restricted to character boundaries suffice.

**7. Caseless letter landmarks**
- A caseless ASCII letter L could miss U+212A / U+017F under utf8. This never arises: `req_set`/`req_byte` are `none` for `(?i)[a-j]+k\d` and `(?i)[a-j]+s\d` in both byte and utf8 (`--emit-facts`). Landmarks come from those facts.

**8. Conditionals in S** (`(?(1)...)`)
- The per-hit hat is wrong on `(?:(a)|b)+=(?(1)x|y)` / `"ab=y"`, giving NOMATCH where libpcre2 gives (1,4).
- pcrec refuses `(?(` today ("not implemented yet"), and locate_finish LR-S5's closed G4 switch fails closed when it lands. Held.

**9. Bench selection (positives)**
- The rows the design names are consistent with the stamps for mask-email (byte-class; the only real per-byte-DFA baseline), csv5, ipv4/dotted4 (`.`, maxoff 3), and cls-s-ucp (variable width, maxoff 4).
- On the bench's own subjects the landmarks are sparse: mask-email `@` 128-520 B/hit; kv `="` over 8,000; dup-param `=` 15,664 on capability throughput, and `&` has 0 hits there, matching the report's "no `&`" note.
- So no admitted DFA row is on the losing side of the design's 19 B/hit line on bench data. The baseline question is SIM-5. bak-1 at 6.6 B/hit is the dense exception (SIM-6).

**10. Not done**
- No corpus-wide re-census. Without population.py (denylisted) the rarity ratio formula is not stated in the report, so the 149/200/33/7.5/5.5 ratios cannot be rebuilt. That is itself a doc gap: row 5 says only "ratio < F".
- Corpus grep exposure for SIM-1 is 0/4,982. No pcrec compiles beyond `--emit-facts` (about 30 probes, under the 50 limit).
