## Findings

HOUSE-1 (maintenance, SUSPECTED, small): memfn/src/presence.c:~224-229 landmark admission still builds a 256-bit set per run position (memset + 256-iteration loop `(b & mask) == t->run[j]`) just to call kit_mass(.set). The primitive now takes a cube directly: `kit_pos c = run_pos(t, j)` with `kit_mass(rate,&c,1,KIT_MASS_CAP)` drops `set[32]`, the loop and `sp`. Confirm: byte-equality needs run[j] & ~mask == 0 (else the set is empty, the cube is not) and cap vs rate sums; check kit_presence_check guarantees it. Same for window.c translate (~1345) which builds `cube[]` for kit_set_sum: replace by cube kit_pos. Fix: use cube positions; effort S; blast: presence/window pick answers (verify with the census/mass test).

HOUSE-2 (maintenance, CONFIRMED by grep, S): the one-position call `kit_mass(rate, &(const kit_pos){ .set = X }, 1, CAP/SUM)` is spelled 8 times in window.c (a_parked_choose, a_model_choose, a_mass_choose, run_member, translate, d_hors_holds + 2 in presence.c via `sp`/compound literal) and `kit_pos b/qp/sp/c1 = {.t,.mask}` + call 5 times in presence.c. Name the abstraction: `kit_set_mass1(rate,set,cap)` / `kit_byte_mass(rate,t,mask)` static inline wrapper in kit.h (the primitive stays one; the wrappers are call-shape sugar, not a second mass definition). Not a duplication of arithmetic, so maintenance only; presence.c's `run_pos` is already the house idiom for one-position construction, but window.c has none. Also the mask==0xFF byte case is written three ways (`{.t=..,.mask=0xFFu}` at 3 sites).

HOUSE-3 (maintenance, S): TIE enum T_* now lives in kit.h:345 but the table `wf_ties[]` and its section header (window.c:~74 "THE TIE TABLE") do not mention that the row names moved; `wf_ties[T_N]` indexes by an enum a reader must find in another file. Add one line under the window.c header ("rows named in kit.h"). Layering is otherwise defensible (presence.c is the window family's second reader), but kit_tie_takes/kit_tie_member_key are DEFINED in window.c and DECLARED in kit.h beside presence.c's mass block: the comment in kit.h says "window.c wf_ties[]" so it is truthful. kit_tie_member_key (a key builder) sits in the TIE section of window.c while its only caller is presence.c; arguably belongs in presence.c next to member_key (presence.c:100), with the 256-order rule it encodes. Design call, not defect.

HOUSE-4 (doc, S): memfn/src/window.c T_PRES_MEMBER row text and kit.h:340 say "Keys are offsets, except T_PRES_MEMBER's": kit_tie_takes' comment (window.c:~107) repeats it; fine. But T_WINDOW's TIE_LEFTMOST was previously 'no reader -> 0'; kit_tie_takes now treats it as c<b: the enum doc for TIE_LEFTMOST nowhere says "strict < over ascending, leftmost wins" beyond the basis string; acceptable.

HOUSE-5 (doc, S, stale live descriptions that should have moved):
- docs/design/memfn/units_inventory.md:66-67,89,91,180 and span_pick.md:123,145,151 name cube_mass/kit_set_mass/kit_set_sum/window_mass/tie_over/tie_takes: inventory of the BASE (history/evidence, STAY); span_pick.md:123 "as tie_over reads" is design-of-record rationale, stays.
- docs/design/stream/roadmap.md:641-642 R22/R23 counting recipes grep the old names: they must now count 0 variants/1 table — stays only if the ratchet row records the new count; check the row was updated (it is a LIVE ratchet, not history).
- memfn/docs/ideas.md:755 names `kit_set_mass` (append-only log: stays).
- tests/memfn/decider_census.py:43 BACKSTOP "tie_takes" still matches kit_tie_takes by substring: correct, but the comment on the census (line 49-51) only mentions tie_over; fine.
- src/core/findings.c uniform_mass/cube_mass: pcrec's own copy (D157), not deleted; stays. tests/mech/sabotages/S461 anchors on findings.c: stays.
- docs/design/*/call_graph*.txt, sabotage_anchors*.tsv: frozen evidence, stay.
No stale comment found in memfn/src/*.c, kit.h, mass_check.c, run_finder.sh naming a deleted memfn function (grep with exclusions, zero live hits).

HOUSE-6 (doc, S): CLAUDE.md rows. memfn/src/CLAUDE.md 11389 B (<12 KB limit, 611 B headroom); tests/memfn/CLAUDE.md 11944 B (56 B headroom: any further row breaks the 12 KB rule; run scripts/check_claudemd_size.sh before landing; next unit must prune). The presence.c row is accurate. window.c row (CLAUDE.md:39-ish) lists "the TIE table" but not that kit_tie_takes/kit_tie_member_key are its exported readers: add 5 words.

## PROBED-AND-HELD
- grep of all 7 deleted names over memfn/ src/ tests/ docs/design/ lib cli scripts with exclusions: 0 live code hits in the kit; remaining hits classified above.
- kit_tie_takes semantic: TIE_HIGHER c>b, LOWER/LEFTMOST c<b matches old tie_takes plus new LEFTMOST; presence member_key(o<<8|byte) reproduces old order-then-byte compare for order 0..256, byte 0..255 (int32 no overflow).
- kit_mass cap/NONE arithmetic read against the deleted bodies: equal for set/cube/window forms.
- 0 pcrec compiles spent. No make run. Did not verify HOUSE-1 equivalence empirically.
