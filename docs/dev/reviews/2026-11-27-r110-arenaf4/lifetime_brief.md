# CRITIC lifetime (opus): arenaf4 (r110)
Read /var/tmp/pcrec-pcrec/scratch/crit-arenaf4/COMMON.md FIRST; it binds. Your lens dir: /var/tmp/pcrec-pcrec/scratch/crit-arenaf4/lifetime/
(OUT for kit/alloc.sh). Findings file (pre-created; APPEND only): lifetime/findings.md. Deliver file: lifetime/deliver.txt.
lanecheck NAME: lifetime. Finding ids: LIFE-n.

THE ONE QUESTION: does F4 close K163's CLASS (the lifetime and the lent channel), not only its one member?
 (a) The count: is EVERY allocating entry that holds an error channel (an Arena's or a StrBuf's `.cx`) counted through
     `pcrec_err_chan`? Enumerate them by grep yourself (arena.c, sb.c, and every other src/ file that allocates or refuses
     through an Arena or StrBuf carrying a `.cx`, e.g. scope entries, holds, adopt, the vm_stmt.c/enc.c `sb->cx` refusals
     the design leaves "outside the count"), and say for each whether a use through a LENT Ctx would be counted. Is the
     design's claim ("the count sees every allocation made through an Arena or a StrBuf that carries a `.cx`") true of
     the code?
 (b) The lifetime: walk D-4's six steps in compound.c `walk_part` and compile.c's part-facts block as built. Can any
     refusal between the two holds and the two stores strand anything (the part refusing before, during and after
     `part_forms_copy`; rc != 0 with a forms copy already stored; the outer K163 refusal; a part compile that longjmps to
     the OUTER point by a path the count does not see, leaving `lent` set; retries/attempts of the outer compile and the
     memset; a second walk_part on the same Ctx)? Is the class WIDER than one site: what else does the inner compile
     reach of the OUTER Ctx (`meas`, `emit_in`/harness, `rep`, `err`, the kit's `mf_arena` binding, options) and could
     any of it allocate or refuse through the outer channel? Any other nested `pcrec_compile_driver` call inside a compile?
Probe with the kit at runtime where you can (the compound corpus, W6, alloc.sh --sites on subject vs base).
Also carry the two standing questions: SIBLING OF A FAMILY (is this the third member of a family of "handle whose error
channel is another recovery point" fixes: K155, F1's hold, S3580...; name them) and GENERAL FORM + UNLOCKS (what the
general form would be, e.g. U8, and the trigger that should fire it; is U8's stated trigger observable today). D203:
for any defect you find, name the class, the house rule broken, and a grep count of siblings.
