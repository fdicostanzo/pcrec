## Findings

(Paths: W = worktrees/crit-vlb3, S = R/subject_vlookbehind.md.)

### 1 (FIXIND-1 / READY-1 / SOUND-1) -- HOLDS
- W/tests/codegen/run_encoding_checks.sh l.329-380: DD12a(i) "THE NAMED ENCODING-OWNED REGIONS -- excised from BOTH texts": (1) four residual entries, (2) "the [K49] unanchored retry advance, the one splice DD-12 (7) admits into shared emitter code outside the entries table. Anchored on the SAME guard line", (3) `.encoding = N,`, (4) K50 guard/continue/stamp, (5) encoding-keyed selections.
- l.491: `GUARD_RE = re.compile(r'^\s*if \(attempt_position >= (?:subject_length|attempt_max)\) return 0;$')`; excise l.1304-1315 fires only on a GUARD_RE line, swallowing to the next `    }`. A VM-body splice has no such line before it, so it stays in the compared text.
- K49 extraction l.2136-2141: `awk '/if \(attempt_position >= subject_length\) return 0;/{f=1;next} f&&/^    \}/{exit} f'` on the compiled `a*` witness (l.2128 adv_witness='a*') only; a range fixture is never compiled by it.
- S l.1275-1278: "It is unaffected ... A `range` fixture under `-e utf8` gives it a second site to read (§7)"; S l.1534-1536: "gives the advance-agreement check ... the bounded step to read, and it is W14's byte-step detector". Both false as read.
- Caveat: "red on a correct build" is by reading (no suite run, as mandated); the corpus-pattern count (24) is the critics' figure, not re-counted.

### 2 (FIXIND-1 sub-claim, entry-shape knee) -- HOLDS
Chain: emit_vm.c l.10874 `en->program_bytes = pcrec_vm_stmt_program_bytes(v->sb);` -> vm_stmt.c l.1047-1049 `return pcrec_sb_len_decide(sb->b);` -> sb.c l.303 = `len_uncut - simd_guarded - layout_bytes - scaf_guarded`; used emit_vm.c l.11005-11010 `if (term==0) term = VM_INLINE_CHAIN_MAX_BYTES; if (program_bytes <= term) shape = FORWARD/INLINE else SHARED/PLAIN`. Comments ARE counted ("uncut" = the comment axis cannot reach it), so the utf8 advance text (with its K49 comment) counts, unless it were wrapped in a scaffold/SIMD bracket (today's advance text is not; the design names none). So the body length, hence the rung near the 4,096 knee, would differ by encoding.

### 3 (READY-2, K49 comment under -fno-comments) -- HOLDS
`build/pcrec --features all --engine=vm -e utf8 -fno-comments -p rx --emit-main -o R/verify/a.c --pattern 'a*'` rc=0 (flag accepted as spelled). a.c l.309: `/* [K49] The retry advance is this ENCODING's step, not `+ 1`: an unanchored search may only ever try LATER CHARACTER BOUNDARIES ...` is present. Comments in a.c: 13 `/*`; with `-fcomments` 43, so comments are otherwise cut and this one is not.

### 4 (READY-3, `(?<=a)x` is a context node) -- HOLDS
mod_lookaround.c l.524-533: "[UCP] U2 T3 FIRST ... No width rule is asked of it: one character is fixed-width by construction." `--engine=vm --emit-ir` of `(?<=a)x`: 0 lines containing "lookbehind" (it needs --engine=vm; the default run chooses DFA and refuses to list). `(?<=ab)x`: lines "lookbehind branch 1 of 1, fixed width 2: step back and run the branch FORWARD", END-CHECK etc. (Count of lookbehind lines for `(?<=ab)x` was >0, listed at L4/L6.)

### 5 (READY-4, no UTF-8 option in the named harness) -- HOLDS
`grep -n -i 'utf\|invalid\|flags'` on tests/lookaround/run_lookaround_diff.sh and tests/backrefs/bref_oracle.py: only hits are `GENCFLAGS` (gcc flags, l.62/75/150) in the .sh; zero hits of any kind in bref_oracle.py. No `-e`, no UTF, no INVALID_UTF option in either.

### 6 (READY-6, vm_slot_name vs "one owner record per low index") -- HOLDS
emit_vm.c l.1006-1010: "The classification is the SAME arithmetic vm_slot_guard/low/mark/rev/ctr use above, read backwards. It is deliberately not a second table: ... a parallel list would be a second source of truth about it". S l.749-751: "`vm_slot_name`: names every `low` slot `SLOT_SPAN_LOW<i>`, which is false for `LO_i`. One owner record per `low` index (span loop or lookbehind branch) lets the legend say `SLOT_LB_LO<i>`". An owner record per index is a per-index list; a collision as claimed (the design could still build it arithmetically; it does not say so).

### 7 (READY-7, 160-byte vm_rolef) -- HOLDS
emit_vm.c l.885-894: `vm_rolef` -> `pcrec_sb_fragfv(&v->cx->arena, ...)`; sb.c l.611-624 measures with `vsnprintf(NULL,0,..)` then arena-allocs n+1: no limit, no truncation. Stale comment emit_vm.c l.7125-7129 in vm_look_behind_branch: "`vm_rolef`'s buffer is 160 bytes and it TRUNCATES". S l.813-815: "The 160-byte `vm_rolef` limit and its truncation note apply to each."

### 8 (FIXIND-2 / READY-5, no sizing pass for VL_LB_COUNT) -- HOLDS
S l.1249: "`VK_LSET` (`VLO_ASSIGN`) on a new `VmLocalKind` member, `VL_LB_COUNT` (`<p>_lb<n>_count`, declared by the frame as the `rv` locals are)". vm_stmt.h VmFrame l.304-318 fields: ai_body, mrl_param, gst_param, trail_gc, span_cursor, nrev_total, nrevcaps, tracing, kreset, has_push, has_budget, has_linked_calls, guarded_copy -- none for lookbehind counts. The design names no field, producer or `<n>` meaning.

### 9 (FIXIND-3, S133 / S123 anchors) -- HOLDS
S133_backstep_inlined.sh l.40-41: `SAB_COUNT=1`, `SAB_BEFORE='    pcrec_vm_b_seek(v->sb, VSK_BACKSTEP, NULL, k);` (multi-line anchor, l.41-45), plus SAB_COUNT2=1 on `v->enc_mask |= PCREC_ENCE_BACK_STEP;`. S123_look_no_cursor_restore.sh l.34-35: `SAB_COUNT=1`, `SAB_BEFORE='            pcrec_vm_b_seek(v->sb, VSK_RESTORE, sl, 0);'` (emit_vm.c l.7510, vm_look). `grep -c S123` on S = 0: the design never names it. (emit_vm.c l.5894 has another VSK_RESTORE but with a different argument text, so S123's count stays 1 today.) Plan row [VMREC] at e20dee230 plan.md l.239 has no member list (not re-read in depth).

### 10 (FIXIND-4, VK_LSET cannot target a slot) -- HOLDS
vm_stmt.h l.139-141: "An untrailed matcher LOCAL an LSET may write. The span cursor, the subject cursor and run state are not members ..., so an LSET cannot be built on them"; members are the seven VL_* kinds, none a slot. S l.1484 (W-low): "`LO_i` written untrailed (`VK_LSET`)". As written it is a vocabulary extension (an LO local), not a mutation of the existing emitter.

### 11 (SOUND-4, W-low answer-level witness) -- HOLDS (with one nuance)
`(?:(?*.*(?<*a?))b)*$` on `bc`: Oracle B (`probe m ''`) `[2-2]`; Oracle A (`oracle_probe m`) `[2-2]`. Copy R/verify/lvm.py, `python3 -I lvm.py m "" - < wl.in` -> `[2-2]` (correct); `... m "" WLOW` -> `GIVEUP` (lvm's GiveUp exception: step budget/overrun, l.594). So the sabotage does move an observable (non-termination/overrun instead of the right match), contradicting S l.1484's "none at answer level ... No cell found". Nuance: the sabotaged result is a give-up, not a wrong match string; whether a real emitted matcher gives up (frames/steps) or reads out of bounds depends on the bound the real artifact has. lowmin/fuzz counts (652/2,904; 20/1,125) not re-run.

### 12 (SOUND-3, model.py cursor_branch) -- HOLDS
E/model.py l.258-276: `cursor_branch` is straight CPS code (`self.m(...)` per candidate), local `back_step` = `pos-k if pos>=k else NONE`, `advance` = `pos+1`; no frames, trail, POS/LO slots or L_n_i restore: byte-only and frame-free. cells_byte_model.out l.18: `(?<=\Aa{0,2})x	aax	pcre2=[2-3]	cursor=nomatch	range=nomatch`; 9 rows `cursor=n/a` (6 `\G`, 3 backref). S l.617-620: "(cells: `(?<=\Ga{1,2})b` from 0/1/2, `(?<=^a{0,2})x`, `(?<=\Aa{0,2})x`, all equal to libpcre2)". As a statement about the byte-mode model it is false for the `\A` cell; as a statement about the 52 libpcre2 cells' own recorded answers it is not testable from this file. Doc-level.

### 13 (READY-9, W12(a) rests on compaction trigger stopping) -- HOLDS by hand reasoning, confidence about 70%
emit_vm.c l.12650-12700 header: within one segment (between live frame marks) "every later entry for a slot the segment already holds is never the survivor of any unwind, and dropping it changes no answer"; the retry frame stays live across `L_adv_i -> L_try_i`, so under the sabotage (LO written at L_try_i) all per-candidate LO entries sit in one segment and ARE droppable (net one entry per slot). A compaction keeping `w` entries re-arms the floor only if `w + cap/4 <= floor`, else "returns never ... checkpoints stop compacting for the attempt" (l.12700-12704; and l.12708-12711: a re-arming trigger "was tried by lane trailgc3 and left holes"). With cap 5 the floor is `5 - min(nset,2)` = 3; after one compaction w is about 3, 3+1 > 3 -> never, so later candidates' writes pile up and reach `R_FRAMES`. Hence red depends on the stopped trigger (and on a checkpoint existing on the goto, true only because the SET sits inside the cycle). Not run (no sabotaged build possible read-only).

### 14 (SOUND out-of-delta, `(?<!\G|é)` on ill-formed `\xc3`) -- HOLDS; known design position, no dedicated row found
pcrec `-e utf8 --pattern '(?<!\G|é)'`, driver calling `rx_search` with the single byte C3 (R/verify/g2.c; the generated main refuses ill-formed argv): `match 1 1`. Oracle B `probe m ix` (UTF + MATCH_INVALID_UTF): `nomatch`. Per docs/design/utf8_design.md §2.6 (l.1089) "ill-formed byte sequence matches nothing, no validation pass" and §2.6.1 (l.1127-1160, "No path INVERTS for a negative assertion", ACCEPTED): a negative lookbehind at an ill-formed/mid-character position SUCCEEDS where PCRE2 skips it; the stated promise is for boundary `startpos` only. plan.md at e20dee230: only [UTF-VALID] (caller-side validation, `-futf-check`) and [UTF-EXTENT] mention ill-formed subjects; I found no row on this specific cell. So it is the documented §2.6.1 divergence, not a new finding; whether lookbehind-over-ill-formed in particular is listed is unconfirmed.

VERIFY COMPLETE
