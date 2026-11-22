# CRITIC SLOT (opus): r76 memfn-bsu3

Read /var/tmp/pcrec-pcrec/scratch/crit-memfn-bsu3/COMMON.md first (including its "R75 ITEMS" section).
Your lens dir: .../crit-memfn-bsu3/slot/
Findings file (pre-created, APPEND only): .../crit-memfn-bsu3/slot.md. Deliver file: .../slot_deliver.txt.

## Your ONE question
Trace every slot U3 adds or changes in memfn/src/window.c to the table or mechanism that should own
it: is anything duplicated, narrowed, unreachable, or a second mechanism beside a first ("one table
per slot"; docs/dev/guide/architecture.md and coding.md at SUBJECT)? The slots: `wf_spanrows`' new
`define` column (and the `j` numbering that now keys on it), `vs_name`, `vs_head`, `vs_table`,
`vs_w32_block` (V's own level-block writer beside ofsskip's `fn_level_block`: design §5 "V's level
block stays V's own until vany's touch" is ruled; check the code matches the ruling's stated reasons
and that the filed ride-along exists), the `art->includes` bit, the `art->forms` token write, the
`simd_open`/`simd_close` bracket and the "no bracket -> body alone" rule, `kit_selector`'s top/level
arguments, and any R75 ITEM COMMON assigns to SLOT.
- sub-part (a) the two standing questions: SIBLING OF A FAMILY (is any of these the third member of a
  family that should be unified now; name the members by file:line) and GENERAL FORM + UNLOCKS (what
  general form would these rows be one instance of, what would it unlock, and what measured trigger
  should start it).
- sub-part (b) house rules (docs/dev/guide/coding.md, style.md): duplication, altitude, tables used as
  if-chains, side effects in predicates, error paths (every kit_fail / NULL return reaches the
  caller), and D157 in comments (a kit comment must not presume pcrec's method, nor pcrec's the kit's).
Mostly a READING lens: compile cap 100 compiles. Do not plant anything.
