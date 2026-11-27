# CRITIC scope-lifetime (opus): arenaf3
Read /var/tmp/pcrec-pcrec/scratch/crit-arenaf3/COMMON.md FIRST. Your NAME for lanecheck: `lifetime`. Your file:
/var/tmp/pcrec-pcrec/scratch/crit-arenaf3/lifetime/findings.md (pre-created; APPEND). Scratch: lifetime/ only.
Finding ids: LIFE-n.

THE ONE QUESTION. For each of the three new scopes (S10 `nb` in `target_headers_render` and S11 `tail` in
`splice_mark`, both src/gen/memfn_stamps.c; S12 `o` in `render_buf`, src/gen/part_layout.c): on EVERY exit while the
scope is open - the normal return, each refusal that can longjmp out of it (a nomem in a puts/printf/adopt, the
`pcrec_ctx_fail` calls inside render_buf, the adopt guard, anything a callee such as `stamp_lines` can raise), the
"teardown only" routes the new comments name (count_groups / syntax_dump), and any NESTED compile (compound part
compiles, a lent outer Ctx; design D-4, D-7, K163) - is each record released exactly once, in LIFO order against
every other scope that can be open on the same arena at that moment (who else opens scopes on `cx->arena` around
these calls: grep `pcrec_scope_open`), and is the storage `pcrec_sb_adopt` hands to csb/hsb/sb never freed twice and
never stranded? Trace the code by file:line (arena.c's scope API, sb.c's adopt, compile.c's handler-top unwind near
`pcrec_scope_unwind` and the success-path `pcrec_scope_check_closed`); confirm with probes where you can (the alloc
kit's `--sites` on subject; emitted-C identity BASE vs SUBJECT on a few dozen patterns that reach the three sites,
e.g. memfn/SIMD-targeted and part-layout/compound patterns; check the sites are reached).

Sub-part (b), the round's standing questions (this lens carries them): SIBLING OF A FAMILY - are there other
whole-artifact rewrites, adopt sites or hand-freed heap builders on the compile path that are the same shape and were
left hand-kept (grep `pcrec_sb_adopt`, `= { .cx = cx }`, the scanner's remaining ALLOW rows)? GENERAL FORM + UNLOCKS -
is a rewrite-then-adopt helper the general form here (name its trigger), and do the subject's stated facts hold:
"None of the three is reachable from `pcrec_facts_force_all`" (REGISTRY-1's trigger) and "the close frees an empty
buffer and nothing is copied"?
