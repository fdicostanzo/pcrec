# VERIFIER brief — critic round `vmtrail`

Read `/var/tmp/pcrec-pcrec/scratch/crit-vmtrail/COMMON.md` first: its scope
mandate, read-only rules, denylist, tools and timing window bind you too
(EXCEPT: you MAY read the five critic files named below and their scratch
subdirectories `sound/ slots/ contract/ measure/ cost/`). Your own scratch dir
is `/var/tmp/pcrec-pcrec/scratch/crit-vmtrail/verify/`.

Your job: re-check each finding listed below INDEPENDENTLY. Never trust a
critic's consequence claim: re-run its repro yourself (regenerate the stock
matcher with the review tree's `build/pcrec`, re-apply the stated rewrite
yourself from the design document's text rather than reusing the critic's
twin file where practical, compare against libpcre2-8 10.46), quote cited
lines yourself (file:line in the review tree `worktrees/crit-vmtrail`, or the
subject docs at their frozen commits), and redo arithmetic. For a design claim,
check the documents' exact wording: is the rule really as the critic reads it,
or does another sentence in the same document close the hole? Say which.

Critic files: `sound.md`, `slots.md`, `contract.md`, `measure.md`, `cost.md`
in `/var/tmp/pcrec-pcrec/scratch/crit-vmtrail/`.

Write `/var/tmp/pcrec-pcrec/scratch/crit-vmtrail/verify.md` (it does not exist
yet) INCREMENTALLY, one finding at a time, as:

```
## <ID>
- verdict: HOLDS | REFUTED | PARTLY | not verified (why)
- how: <commands / quotes / computation, with observed output>
- note: <anything the draft must know: a narrower claim, a closing sentence the critic missed>
```

Findings to verify (grouped; one verdict per ID):

1. Event stream incompleteness: SOUND-2 (re-run the `^(?:(?:[bB]|[cC]d)(\w))+by$`
   witness on bxby), SLOTS-1, SLOTS-1a (the `(?:a|bc){3}+` listing vs C edges;
   the revdet cut logged as a note), COST-1 (the grep counts).
2. SOUND-1: `^(b)(?1)` with `--engine=vm -fno-splice-calls` on `bb`; does
   vmbc's DECLARED table (rows 1, 3, 4) make the caller's group-1 SETs dead,
   and does any other vmbc sentence (outside C's model) give the call that read?
3. SOUND-3: R leaves raw `run->resume_depth` readers (CUT mark writes); re-run
   `^(?:(?>ab|a)c|abd)` on `abd`; does trailgen's R text cover value texts?
4. SOUND-4: left recursion: `^(a|(?1)b)` on `x`/`b`, `(?:a|(?R))+` on `b`/`ab`
   stock vs D-as-tabled; quote pattern_language §9 paragraph 4a.
5. SOUND-5 + SLOTS-3 (UNTRAIL x COPY order): is the counterexample program
   valid under the tables as written? Does any sentence fix the order?
6. SOUND-6 + SLOTS-4 (forward passes and unknown successors): do the docs'
   row-11/row-13 texts define successors anywhere?
7. SLOTS-2: push-site count via the AST pre-pass vs a post-pass; check the
   `[abd]x|[acd]y|[bcd]z` class count (5 vs 2) and `tests/codegen/run_ir_listing.sh:474`'s
   direction; `vm_plan_capacities` / `vm_jump_closes_trail_cycle` timing.
8. CONTRACT-3: `--engine=vm 'a(?:\dx|[a-z]y)c'` stamps FRAMELESS 0 with one push
   whose arms are first-byte disjoint; quote match_api §6.3.8¶10.
9. CONTRACT-1: the `--no-captures` callout witness (ncap 3 vs NCAPS 1);
   re-run stock vs group-SETs-deleted on `abd`/`acd`.
10. CONTRACT-2: S179/S180 detection after B+C (the arithmetic; the S180 header
   and framebuffer.rxt cells); match_api §10.2¶4's sentence.
11. CONTRACT-4 (D size bound vs limits §8.4¶4 / tuning §2.20¶2), CONTRACT-5 +
   SLOTS-9 (no deny/stamp for B/U/C/R; D46, tuning §2¶1/§1¶7, flag-bit count in
   lib/pcrec.h), CONTRACT-6 (ir_listing §1¶4).
12. SLOTS-6 (kindrow.def PATH values for A_CALL/A_ATOMIC vs FIRST+ rows),
   SLOTS-7 (snapshot verdict in two tables), SLOTS-10 (R25 E5 witness reach:
   `--emit-ir` rungs for `(?:a|bc){3}+` under `--engine=vm`).
13. Measurement: MEASURE-2 (the six ≥10 % artifacts are all backreference
   patterns: read the bench .rx files), MEASURE-4 (recompute R on B+C for
   comment-5m), MEASURE-8 (Bd vs B columns), MEASURE-12 (trail_frames counter
   from bench records: 63 of 86 small), COST-4 (stage-1 share of D's gain),
   MEASURE-1 (no twin combines R, U and D: grep the three docs' mode lists).
14. COST-5 (SUSPECTED, optional, only if cheap and before 19:15): does
   `restrict` on the prologue's `slot_values` pointer remove the reloads in
   cscan's separate matcher function? An asm-level check (count `704(%`
   references in `gcc -O2 -S` with and without the qualifier on
   `slots/cscan.c`) is enough; mark "not verified" otherwise.

Budget: at most ~60 compiles, one process at a time, nothing after 19:15.
When done, append a final `## SUMMARY` line per verdict class with counts,
then create `verify_deliver.txt` (`report=verify.md`, `sections: SUMMARY`,
`commit: no`) and run
`( cd /var/tmp/pcrec-pcrec/scratch/crit-vmtrail && /home/pcrec/projects/pcrec/scripts/lanecheck --deliver /var/tmp/pcrec-pcrec/scratch/crit-vmtrail/verify_deliver.txt --dir /var/tmp/pcrec-pcrec/scratch/crit-vmtrail verify )`
until it prints `lanecheck: DONE rc=0`. Then END (final reply at most 100 words).
