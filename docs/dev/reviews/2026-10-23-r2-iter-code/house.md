# CRITIC house (lens: coding.md / style.md) -- iter, BASE..SUBJECT, src/

Note: /tmp/claude-1001/crit-iter/house.md (the lens file) did not exist when I started; I worked from the
one-question text in the dispatch message. Guide read from main (docs/dev/guide/ is absent in the review tree).
Finding ids are HOUSE-n. Functions reviewed length-ordered inside emit_iter.c (emit_step_own 63, emit_controllers 45,
emit_step 50, abi_types 60, rest <40); every diffed function in emit_dfa.c/emit_vm.c/emit_comb.c/entries.c/enc.c/
widths.c/dfa.c was read. Stopped at: diff hunks only for the large pre-existing functions
(vm_emit_search_body is ~1046 lines, 12549-13595; I read only its hunks).

## HOUSE-1  CONFIRMED  emitted inline comments survive -fno-comments  (size/doc, effort S, blast: emit_iter.c only)
emit_iter.c writes ~12 inline `/* ... */` into emitted text with pcrec_sb_puts/printf, not inside
pcrec_sb_cmt_open(NONESSENTIAL)/close, so the comment gate (D112 item 2, "everything else is NON-ESSENTIAL") never
drops them. Repro:
  worktrees/crit-iter/build/pcrec -p rx -fno-comments -o a.c --pattern 'a(b|c)*'; grep -n '/\*' a.c
Observed: the iterator's comments remain: "an empty match at n ended it", "K75", "the caller's storage",
"the search that ended it", "sticky", "bind; or refuse; or ENDED", "STEP writes NCAPS pairs...",
"-Wmaybe-uninitialized: ...", "nothing, in every state", "[OPT-1] the page-budgeted fast tier" (a.c lines 352,444,448,
469,477,479,487,493,494,524,526). Expected: only ESSENTIAL (provenance, contract) comments remain under -fno-comments.
Sites: emit_iter.c:226,230,246,249,252,259,349,360,362,378,402,403,424,426 and 291. The top-of-section comment
(emit_iter.c:447) and the header-setter comment (:94) ARE bracketed, so the file knows the rule.
Fix shape: bracket the comment-bearing lines, or move the explanation into the C-side header comment.

## HOUSE-2  CONFIRMED  `<p>__step_own` re-implements `fwd_own`'s tier ladder  (duplication, maintenance; effort M; blast: emit_comb.c, emit_iter.c, emit_vm.c)
emit_iter.c:270-328 (emit_step_own) writes the same three-way "declare run_state + storage, bind, call" text that
emit_comb.c `fwd_own` (:195-262) writes for the six forwarding entries: the TIERED pair (noinline deep with
`<p>_run_buffers storage`, always-inline fast with `<p>_fast_buffers fast`, FRAMES escalation, `_TIER_NOTE`), the
EMPTY (frameless, `run_state_bind(&run, NULL,0,NULL,0)`) and the plain OWN. Even the "[OPT-1] page-budgeted fast tier"
and "stamped default" comments are copied. The selector is also written twice: emit_vm.c:13795-13796 and
:13935-13936 (`en->fwd_entries ? PCREC_FWD_EMPTY : pl->tiered ? PCREC_FWD_OWN_TIERED : PCREC_FWD_OWN`).
Shared abstraction: one `pcrec_emit_own_bind(c, p, up, bind, storage, ret, name, params, callee, callargs,
deepargs, frames_code)` in emit_comb.c next to fwd_own (it already takes ret/name/params/runargs/deepargs/
frames_code; the only things it hardcodes are the callee `<name>_run` and the attribute spelling), plus a
`vm_own_bind(en, pl)` for the selector. Call sites replaced: fwd_own's three branches, emit_step_own's three cases,
2 selector sites. What varies: callee (`_run` vs `__step`, extra `at` arg), attribute prefix
(storage class vs noinline/always_inline), comment brackets (fwd_own brackets its prose, emit_step_own has none --
which is HOUSE-1 again). Risk: a third copy of the tier text makes a change to the tier protocol a 3-file edit; the
emit_step_own header even says "the way `<prefix>_search` binds it", i.e. admits it is a mirror.
emit_one's caller-buffer branch (:349-355) is a 4th variant of the bind-and-call and could share the same emitter.

## HOUSE-3  CONFIRMED  `dfa_dir_retry` is a hand-copied `dfa_dir_anchored`  (duplication, maintenance; effort S-M; blast: emit_dfa.c)
emit_dfa.c:13936-13957 vs :9137-9158. 25 positional initializers; identical except the 5 name strings, the table
banner and one prose line. Positional init of a 25-field struct means the two can drift silently (a field added to
DfaDir has to be added by hand in both, in order). The comment says "the anchored direction's strings under the
machine name `retry`", which is exactly a derivation: either build it by copy-and-override at the one use site
(`DfaDir d = dfa_dir_anchored; d.c.name = "retry"; ...`) -- note dfa_form_derive keeps `f->dir` pointers compared with
`&dfa_dir_forward` (emit_dfa.c:7076), so the derived value must be arena/stack-stable for the call -- or give DfaDir a
small constructor macro `DFA_DIR_FWD_ANCHORED(name, Cap, UP, state, view, banner, what)`.
pcrec_emit_dfa_retry (:13962-13991) also repeats emit_anchored_match_def's tail (scan defs, `scan_position`/
`last_accept_position` declarations, scan loop, `-1` on no accept); the retry's `memset(&base,0,..); base.kind =
DFA_PF_NONE;` hand-builds the `UnanchStart` that `anch_start` documents as "DFA_PF_NONE, no reply" -- a
`anch_start_none()` helper would name it (it is redundant if DFA_PF_NONE == 0).

## HOUSE-4  CONFIRMED  dead code left by the twin rewrite of `pcrec_enc_emit_defs`  (maintenance/speed-of-compile; effort S; blast: enc.c/enc.h/emit_dfa.c)
`pcrec_enc_emit_defs` no longer reads `sites`/`nsites` (`(void)sites; (void)nsites;`, enc.c:~311) yet:
 - emit_dfa.c:3580-3583 `emit_residual_defs` still calls `residual_sites(cx, enc, false, &ns)`, which renders each
   out-of-line entry's N7 site loop through the kit (pcrec_memfn_emit) and throws the text away. And
   `pcrec_enc_emit_twins` fails with "internal error: an out-of-line residual entry states site data" if any such
   entry exists, so the call is dead in every state it can reach; it is also a hidden dependency on the kit.
 - enc.c `enc_emit_defs` is now called ONLY as `(..., inline_half=true, ..., drop=0, stat=0)` (:334), so its
   `inline_half` parameter, its `drop`/`stat` parameters and the `if (stat & t->id) pcrec_sb_puts(sb,"static ")`
   branch (:176) are dead. enc.h:545-553 still documents `sites` as substituted by `pcrec_enc_emit_defs`.
Fix: drop the parameters (the signature change is internal to two callers), delete the residual_sites(false) call,
update the enc.h comment. Confirms by grep: `grep -n "enc_emit_defs\|pcrec_enc_emit_defs" src -r`.

## HOUSE-5  CONFIRMED  hand-rolled spine walks in widths.c where PCREC_SPINE_EACH applies  (taught primitive, coding.md §2.4; effort S; blast: facts/widths.c)
`rw_alt` (widths.c ~:221) is `for(;;){ x = rw_node(a->k==A_ALT ? a->r : a); ...; if (a->k != A_ALT) return u; a = a->l; }`
and `rw_node`'s A_CAT arm is `while (a->k == A_CAT) { acc = rw_cat(rw_node(a->r,..), acc); a = a->l; }` with a
separate head step through `continue`. PCREC_SPINE_EACH(e, root, A_ALT) yields right to left, head last, which is
exactly the order both need; coding.md §2.4 says "use it rather than a hand-written `for (; a->k == A_CAT; ...)` and
its separate head step", and the macro is used 11 times in the tree. The same file's A_CAT fold is the one place
the left-nested-spine discipline (K20) is hand-copied, i.e. the exact mistake the macro exists to stop.
Also: the A_WCLASS and A_CLASS arms (:~238-245) are two identical 3-line blocks (merge the case labels).

## HOUSE-6  CONFIRMED  stale file header contradicts the code  (doc; effort XS; blast: emit_iter.c:1-2)
emit_iter.c:1-2 says "as cut by the I1 ruling: no batch ABI, no `next_n`", but the same file emits
`<prefix>_next_n` (:414-438), `rx_nextnfn` and `rx_info.next_n` (emit_dfa.c). Header (a): what it produces -- now
two controllers; rewrite and drop the history ("cut by the ruling") per coding.md §4.2 (history to docs).
Related in the same file (coding.md §4.2, "wave narratives, panel citations and change logs belong in docs"): lane
names and change history in code comments: emit_iter.c:153 ("IT1; lane iteropt: the bind used to store them a second
time"), :183 ("lane iteropt2"), :333/:369/:389/:393 ("measured, lane iteropt2", "lane iteropt: measured 6-7
instructions"), and emit_dfa.c ("i1build ruling 2"). The measurements are invariants worth keeping (the canary and
reload reasons); the lane names are not.

## HOUSE-7  CONFIRMED  `ent == PCREC_ENTRY_FIND` special-cased four times instead of a row field  (declared table as if-chain; effort S-M; blast: emit_dfa.c, entries.c)
emit_search_head (emit_dfa.c:~1887-1955) tests `ent == PCREC_ENTRY_FIND` for scaffold bracketing (`scaf`), for the
inline/noinline attribute plus the `owned_inline` side effect, and `ent != PCREC_ENTRY_FIND` for the startpos guard;
emit_attempt (:14171) tests `ent != PCREC_ENTRY_FIND` for `uncopyable`. The entries.c row table is exactly where an
entry's layout facts live (`pr_*`, `EM_ITER`), and FIND already has rows there; "scaffold head", "own prologue"
(guard/no guard) and "inline body" are per-entry facts the table should carry (memory:
pcrec-general-mechanisms-not-special-cases). Note also two derivations of the same fact -- "this body keeps label
addresses in a static table": `find_body_shared` says route == ATTEMPT (:1957), emit_attempt says `d->n > 0`
(:14171). SUSPECTED divergence: an ATTEMPT-route machine with `d->n == 0` is forced `noinline` by one and copyable by
the other; confirm by finding a pattern with route ATTEMPT and no states (none tried).
`find_body_shared` is forward-declared at :1887 only to be defined 70 lines later; define it above.

## HOUSE-8  CONFIRMED  `emit_bind_checks` decides by emitting and measuring  (side effect in predicate; effort S; blast: emit_iter.c)
emit_iter.c:125-146 renders `pcrec_emit_startpos_guard` into a throwaway StrBuf to learn whether the prologue is
non-empty (`g.len > 0 || g.cmt_dropped > 0`, reaching into StrBuf's comment-gate internals) and then copies the text.
Not a miscompile today (the guard has no Ctx side effects I could find), but the next stamp/need-flag that function
sets would fire here too, for a third emission of the same guard. A predicate (`pcrec_startpos_guard_empty(cx)`
beside `pcrec_startpos_guard_text`/`pcrec_utf_check_on`) is the named abstraction. Local named `g` for a StrBuf also
breaks the §1.7 convention (`g` is GenNames, `b` a StrBuf) in a file where `g` is the GenNames parameter of
pcrec_emit_iterate.

## HOUSE-9  CONFIRMED  enc.c twin machinery scrapes C declarations as text  (maintenance; effort M; blast: enc/)
`enc_emit_forwarder` (enc.c ~:260-295) derives a forwarder by `strchr(decls,'(')`/`strrchr(')')`, splitting on
commas and taking "the last identifier" of each parameter; `enc_entry_name` takes the first identifier after `$_`.
Any declaration with a function-pointer parameter, an array parameter or a default breaks it silently, in an
`internal error` at best. The PcrecEncEntry table already is a declared table with ids; an `args` field (or a `name`
field) per out-of-line entry is the data-driven answer (coding.md §4 Q3). Also: the identifier-char test
`isalnum(..)||'_'` is written four times (enc_entry_name, enc_emit_twin_text, enc_emit_forwarder x2) -- name
`enc_is_ident(c)`; `char nb[64]` scratch in enc_is_twinned/enc_emit_forwarder silently truncates a long name (coding.md
§2.2: no new fixed scratch; these are prefix-free so outside K38, but truncation is silent, not diagnosed).
`pcrec_enc_emit_twins` has no function header of its own (HDR-1) -- the section banner above enc_entry_name stands in.

## HOUSE-10  CONFIRMED  positional `Mach` initializer grew a middle field  (maintenance; effort XS; blast: ir/dfa.c)
ir/dfa.c:1637 `Mach m = { prune, reverse, false, has_end, has_gst, d->natoms, d->atomvec };` -- `noacc` was inserted
as the 3rd member and the literal `false` pads it. Reordering or adding one more bool compiles silently. Use
designated initializers. The notempty handling is also spread over five sites in pcrec_build_dfa (`ne`, `sm`, two
`d->notempty` bool args to make_state, the `&& !d->notempty` on s1g) -- they read as one decision ("build the start
closures as the notempty machine") and a `start_mach(d, &m, &ne)` or a local `Mach ne = {...}` constructor would keep
it in one place. dfamemo.c:73 `d_notempty` parameter name is the only `d_`-prefixed one in the function.

## HOUSE-11  CONFIRMED  `enc` twin-mark call split repeated at two sites  (duplication, small; effort XS)
`pcrec_sb_printf("...%s_", prefix); pcrec_enc_twin_mark(c); pcrec_sb_printf("name(...")` is written twice by hand
(emit_dfa.c:840-843 `valid_upto`, emit_vm.c:~12480 `var_valid`) and a third time implicitly in enc_emit_twin_text.
A `pcrec_enc_emit_call_head(c, prefix, "valid_upto")` that writes `<p>_` + mark + name (and so owns "this is a call to
an out-of-line entry, hence its twin") would remove the three-way knowledge that the mark goes between prefix and
name, and the string split in the middle of an emitted expression (the printf format is cut at `_`/`valid_upto(`) is
hard to grep for.

## HOUSE-12  SUSPECTED  caller-facing stamp values name mechanisms (D174; effort XS; blast: stamp + spec)
`<PREFIX>_ITER_RETRY` is "none" | "dfa-root" | "vm-guard" (emit_dfa.c:~15008). D174/style.md: a caller-facing
stamp value says what the caller sees; "dfa-root"/"vm-guard" are implementation names (engine + mechanism), though
neighbors such as `VM_PREFILTER`="hybrid" are of the same kind (shipped, not retroactive). New stamp, so D174 applies
unretroactively. Confirm only if the spec (match_api.md) treats it as caller-visible; if it is a test-only fact, say so
at the stamp row (stamp_kinds.c:46 comment "the shell's own iterator" is also not a reason).

## HOUSE-13  SUSPECTED  `.vars` is never set in the DFA PcrecIterText  (emit_dfa.c:15732; correctness-by-assumption)
`pcrec_emit_iterate` takes `.vars` from the caller's PcrecIterText; the VM sets it from `n_var_exps > 0`, the DFA
site `{ .vm = false, .retry = retry_ok }` never does, while `<p>__find` is emitted with `pcrec_vars_param_text(cx)`
(emit_dfa.c:1940) -- the head text is keyed on n_var_exps, the iterator's call is keyed on a literal. Safe only if a
variable-bearing pattern always takes the VM route. Derive `.vars` from `cx->n_var_exps` in the DFA site too (one
line) so both emitters use one source, or assert. Confirm by trying a `${v}` pattern with `--engine dfa`.

## HOUSE-14  nits (not numbered separately; effort XS)
- emit_controllers (emit_iter.c:395-439): one 9-argument pcrec_sb_printf whose `%s` slots are interleaved
  conditional fragments for the retry flag; build the 4 retry pieces as named locals first (`flags_decl`,
  `flags_load`, `flags_arg`, `flags_store`) -- as written a reader must align nine `%s` against nine arguments by eye
  (altitude Q1/Q2; the function is otherwise one purpose).
- emit_iter.c emit_step has `va` (:219) and emit_one has `sa` (:338) and cursor_args (:196) all spelling the same
  forwarded cursor; three spellings of one convention (coding.md §2.3).
- entries.c `entry_names[]`/emit_comb.c `comb_names[]` are positional parallel arrays to an enum; inserting `next`
  and `iterate` mid-array only works because the enum was edited in the same order. Designated initializers
  (`[PCREC_ENTRY_NEXT] = "next"`) make the pairing checkable.
- `<p>__find` names the DFA body (an entry row FIND) and the VM loop (no entry row; pr_next_vm points at SEARCH_RUN):
  one concept, two registrations.
- entries.c:56 `EM_ITER`: "nothing reads it" -- a column value with no reader (D77); fine if the kit mode fact lands, flag for the plan.
- vm_emit_search_body is 1046 lines; this diff adds ~60 and makes one good extraction (vm_emit_search_run_prologue).
  Altitude: the function is a trigger, not examined here beyond the diff.

## PROBED-AND-HELD
- emit_step / emit_one / emit_enter: each single-purpose and at one semantic level; K75 comment and COMMIT-on-1 invariant
  stated. Held (9 functions in emit_iter.c read in full).
- abi bump 83->84 present with the identity: ITER_RETRY in stamp_kinds.c, rx_info appended fields, and
  emit_rx_abi_types blocks all inside scaffold brackets (6 bracket pairs checked, balanced).
- No `default:` on any AKind switch in widths.c (rw_node covers all kinds; trailing `return acc` is unreachable under -Wswitch).
- emit_comb dispatch: `PCREC_COMB_ITERATE` has its own case, `comb_names` position matches enum (checked by hand).
- No new raw malloc/free in src/ for this diff other than dfamemo.c's existing pattern.
- Single-letter emitter locals (`c`, `p`, `t`) are the house convention (§1.7); not flagged.
