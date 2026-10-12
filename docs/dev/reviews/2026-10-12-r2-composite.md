# D6 panel r1 — the COMPOSITE ARTIFACT tool (docs/design/composite.md, lane mscomp 28f97e52)

Session 109, 2026-10-12. Three read-only critics, none ran make: **sem** (opus; semantics vs libpcre2 10.46), **arch** (sonnet; architecture, generality, unlocks), **chk** (sonnet; checks and cost). Their findings are condensed below.

## Verdict
The corrected controller survives every semantic attack on DFA parts. sem could not refute next_pos(floor), the kills, the prune rules (except call targets), numbering or find-all. chk re-ran real DFA Qs (trim, wrapper, tie, outage, sem-B1, sqli's pruned Q with 23,152 matches) with 0 diffs. The NOTE is not build-ready:
1. **Cost on matching subjects (chk B1):** an unanchored Q costs forward + reverse + finish, where today's attempt reads the match once. S+F (concat-sqli) is 2.07x today on 1000-hit find-all, and 3.00x on one long match of `^q|a+b`. The note's 0.25x is no-match only, and nothing in the admission declines the matching case.
2. **B3 (rev-end one-pass walk) is unspecified (chk B2):** after it, the trailing-run-before-\n shape is still ~2.0x (reverse + forward tie) unless the finish is skipped when the end is decided and no captures are asked.
3. **Entry prologue (sem MF1/MF2/MF4 = arch M5):** -futf-check (Q validates less than P), the floor-only composite's lost -7/-9 refusals, and -fstartpos-guard=align (\G true at the aligned start; the atomic bug returns). ONE fix: the controller owns a single prologue computed from P, and the parts are compiled with the guards off.
4. **(?R)/(?0) under a tree-wrapped F (sem MF3):** a BLOCKER for B5 and the general tool. F must be a bound on P's own attempt, not `\G(?:P)`.
5. **The tool is shaped by split (arch M2/M3/M4/M6):** a bespoke controller per row (build it from locate_finish's typed vocabulary as combinators), no per-part options, a second size ladder, and a keep bitmask instead of controller edges.

## Dispositions
| id | finding | disposition |
|---|---|---|
| chk B1 | matching-subject cost of unanchored Q (2-3x) | ACCEPT. **For Frank:** the first build is PIN-ONLY (Q end-pinned, at most ~2 matches per subject, so no many-match term), and S+F waits for a bench reading of concat-sqli on its own subjects plus a derived cost conjunct |
| chk B2 | B3 unspecified; post-B3 ~2x | ACCEPT: B3 becomes its own design row + panel + gate (revend.md:699's lockstep walk), with an end-decided/no-captures finish skip; G3's bound = the true factor |
| sem MF1/2/4, arch M5 | entry prologue | ACCEPT: one controller prologue (range, align, utf-check with P's LB from P's tree before the prune); parts compiled guards-off; qf = next_pos(aligned f) |
| sem MF3 | (?R) under the wrapped F | ACCEPT: F = a bound on P's attempt (attempt-gstart, start_max = from) |
| sem S1 | the prune deletes called groups | ACCEPT: keep called groups' bodies, or decline |
| sem S3, notes | \K vs the cache; verbs/callouts decline as a registry-keyed predicate; D158 give-up surface not a subset (drop "answer for answer"); caller contract for the cache | ACCEPT |
| arch M1 | "composite" name collides with cand_rows' LOCATE row | ACCEPT: rename the artifact kind (Frank's call on the word, Q4) |
| arch M2 | bespoke controllers | ACCEPT: controller = combinators over locate_finish's typed results (first-nonzero, min-start-then-finish, locate-then-finish, select-by-arg, dispatch) |
| arch M3 | per-part options | ACCEPT: CompPart flags_set/clear + engine; no silent default |
| arch M4 | second size ladder | ACCEPT: a fit_rungs[] row drop-composite; the comp_rows choice an attempt-level state |
| arch M6 | keep = flat bitmask | ACCEPT: controller edges into [EMIT-ENTRIES]' closure; the hybrid's "static " parameter subsumed in B0 |
| arch S2 | one bit per client exhausts bits | **For Frank:** ONE family bit `-fno-composite` + rows deny-able by name (a value axis), instead of bit 55 for split alone |
| arch S1, S3-S7, N1-N4 | stamp classification (pattern- vs machine-level), table kit, noinline/noclone on parts (K24), cand_read projection, shared tables deferred, state_words reserved, `__` prefix collision, compile CPU, hybrid trigger wording, twin arms | ACCEPT for the revision |
| chk M3-M7, S8-S12 | differential on the shipped config (DFA Q, matches>0, derived Q), utf8 witness bytes, decline reasons + reach, D94 by macro NAME, attempt instrument, constants, B1/B2 validation, the 16-row landing bar, generators, Q cap | ACCEPT for the revision |

## Unlocks (arch, ranked)
1. **Captures on demand:** `caps==NULL` goes to a --no-captures part, otherwise to the VM, in ONE artifact (D119 ledgers: auto-nocaps carries 65 of 91 wins). Trigger: the caps/nocaps gap persists after the in-flight cycles.
2. Dead-arm prune as a default pass.
3. 4b.2 LS+LE / E+LE rows.
4. [FINDALL-NEXT] cache.
5. [ADAPTIVE-ARM].
6. Arch dispatch + the hybrid re-expression (needs shared tables).

---
# composite panel r1 — SEM (opus): no BLOCKER for B4 DFA-only; MF3 BLOCKER for B5/general tool
MF1 -futf-check: when from>0 no \G, Q checks [from-LB_Q,n) vs P's [from-LB_P,n); floor arm can be the only LB raiser (\A,\b,\B,lookbehind). \A\s+|\s+\z -e utf8 -futf-check on ff 20 from 1: composite (1,2), plain -9, pcre2 -23. Fix: controller guard+check once at entry with P's LB; parts compiled without -futf-check (also removes double check).
MF2 floor-only composite loses -7/-9 refusals at from>0 no \G (a{0,4}\A -e utf8 -futf-check on c3 a9 ff: -7 at 1, -9 at 2). Fix: return F(s,n,from,caps) unconditionally, or MF1 entry guard.
MF3 (BLOCKER B5/general): F = A_CAT(A_GSTART, root) changes (?R)/(?0) target -> re-enters \G(?:P). ^x|a(?R)?b on "aabb": composite (1,3), plain+pcre2 (0,4). Fix: F as a bound on P's own attempt (attempt-gstart start_max = from), not a tree wrap; or recursion -> P root; or decline (?R). Hidden today by A4 (VM-routed).
MF4 (B5) align: \G TRUE at aligned f (B.1 wrong); qf=next_pos(from)=f -> atomic bug returns ((?>\Ga|ab)c -e utf8 align on c3 a9 61 62 63 from 1: composite (2,5), plain+pcre2 none). Fix f=aligned(from); qf=next_pos(f). DFA-only parts unaffected.
S1 prune deletes a called group: (?:^(a)|b)(?1) on "xba": pcre2 (1,3), Q refused. Keep called groups' bodies (DEFINE-style) or decline; cells for backref to pruned group, (?J) refs[] as set.
S2 evidence doesn't exercise the derivation: twin Q = text kill to (?!), unpruned, mostly VM; cost.py hand-pruned; all 94 cases default options (no utf-check/align/no-startpos-guard/floor-only). (truncated)
S2 fix: G1/G5 run the DERIVED (killed+pruned) Q, every option arm, the floor-only controller and a (?R)/(?0) row.
S3 (B6) §C cache assumes no \K (qs can exceed attempt start): key on attempt start or decline cache with \K.
NOTES: verbs (*COMMIT/SKIP/PRUNE) would break controller across starts (^a(*COMMIT)b|c on "ac": pcre2 none, composite (1,2)); prune drops callouts in floor arms; make decline a registry-keyed predicate now. D158 with VM parts: composite can ANSWER where plain gives up (give-up surface not a subset either way) — "drop-in answer for answer" overclaims; return F's give-up immediately. Double utf validation at from==0/\G (fixed by MF1). §C cache keyed (s,n) assumes caller doesn't mutate subject — state caller contract.
UNREFUTED: next_pos(floor) byte/utf8 default guard/-fno-startpos-guard incl n==0, from==n, from>n, empty; ^+\G floors; false vs never node equivalence past floor (alt, atomic, possessive, lookaheads, unset backrefs, (?J), empty iteration); kill exclusions sound; prune rules sound past floor (except S1 call targets); group numbering preserved; find-all = plain; DFA-only parts immune to Finding-1 class; _match delegating to F sound; §C monotone without \K.

# composite panel r1 — ARCH (sonnet): no BLOCKER, 6 MUST-FIX, 7 SHOULD, 4 NOTE
M1 name collision: cand_rows[] LOCATE row "composite" exists (emit_dfa.c:8892, ~30 comments); rename artifact kind (assembly/compound) before B4.
M2 controller bespoke per row; relate to locate_finish.md typed vocabulary (CT_START/VERDICT/ENDSET/LOWER, FINISH nomatch/report/verify-at/search-from, O1-O10). Part = "a machine a LOCATE/FINISH row may name"; controller combinators: first-nonzero [split], min-start-then-finish [4c], locate-then-finish [D.1], select-by-arg, dispatch [arch]. Say which of D.1/4c are better as in-Job LOCATE rows.
M3 CompPart lacks per-part OPTIONS (flags_set/clear + engine); "same pcrec_options as P" is a silent default; `need` undefined.
M4 comp_fit = second size ladder; must be T1 fit_rungs[] row drop-composite; comp_rows[] choice an attempt-level state T1 can retry.
M5 controller ignores entry prologue: startpos-guard=align + \G -> qf==f' floor re-run with \G dead (atomic bug returns; witness (?>\Ga|ab)c -e utf8 align startpos 1 on c3 a9 61 62 63: P none, composite (2,5)); -futf-check LB_Q < LB_P after prune (^(?<=é)a|b) -> match where today ERR_UTF. Fix: controller owns ONE prologue with P's LB; parts compiled guards denied; qf strictly past f'. G1 cells.
M6 keep = flat bitmask; must be controller EDGES (composite entry -> part entry) feeding A.2's closure; pcrec_emit_dfa_engine(cx,fn,"static ") (emit_vm.c:12761) subsumed by pcrec_entry_linkage in B0 (hybrid first zero-mover customer).
S1 stamp truthfulness: classify every stamp pattern- vs machine-level (D156 PATH-derivation rule); defined composite values. S2 deny bits: spend ONE family bit -fno-composite now; rows addressable by name (value axis) from row 2. S3 table kit (C1 trace, --list-axes projection, roots, row-reach witness). S4 static part search inlinable into controller (K24 noclone lesson): noinline/noclone + ccdiff check. S5 admission reads through cand_read projection, declared edges. S6 shared tables deferred need (D77). S7 reserve state_words + caller-struct access now.
N1 part prefix <prefix>__f legal user prefix -> link collision; refuse __ or other scheme. N2 compile CPU (plain+F+Q) vs D45 margins. N3 hybrid re-expression trigger = "client 2 needs wider part interface". N4 twin utf8 add align + -futf-check arms.
UNLOCKS: 1 captures on demand (caps==NULL -> nocaps part, else VM) in one artifact — D119 ledgers (auto-nocaps 65/91 wins); trigger caps/nocaps gap persists. 2 dead-arm prune default pass (trigger: bench cell decided by dead arm). 3 4b.2 LS+LE/E+LE rows (K106 reach). 4 FINDALL-NEXT cache (IFACE-PUSH). 5 ADAPTIVE-ARM (needs S7). 6 arch dispatch + hybrid re-expression (need S6/N3).
§H: G4 nm -g equality shares source with B0 closure unless built from plain artifact's symbol list.

# composite panel r1 — CHK (sonnet): 2 BLOCKER, 5 MUST-FIX, 5 SHOULD
B1 cost dominance false for S+F on MATCHING subjects: 0.25-0.33x is nomatch-only (all sqli cells matches=0). With matches: concat-sqli find-all 1000 hits 2.07x (28,986 vs 14,028 loads); `select char(x ` x4000 1.48x; ^q|a+b one long match 3.00x, 1000 matches 2.67x. Cause: unanchored Q = forward + reverse + finish vs attempt reading the match once. No cost conjunct in A2-A6; G3 lacks matching/many-match cells. Fix: add cells; derived cost conjunct or declare the loss; run the bench's own concat-sqli subject before citing 0.25x.
B2 B3 unspecified and doesn't remove the 3x: revend.md:699 lockstep two-seed walk "filed, not scheduled"; Q=\s+$ on Q\t^k\n k=16000: today 16,003, composite 48,007; one-pass leaves reverse k+2 + forward tie k+1 ~2.0x; tie by accepting ends undefined (priority != longer end: \s*?$). Fix: B3 as a design row + panel + gate; state post-B3 factor; skip forward finish when no caps and end decided, or set G3 to the true factor.
M3 differential never ran shipped config: textual (?!) kill -> Q VM-routed (65 vm/unanch, 20 vm/-, 4 vm/attempt, 3 vm/rev-end, 2 dfa/attempt); ZERO dfa/unanchored or dfa/rev-end Q; 25 rows VM P (declined); 21 rows (23%) matches=0. Critic re-ran real DFA Qs (trim, wrapper, tie, outage, semB1, sqli pruned DFA Q 23,152 matches) utf8 exhaustive: 0 diffs — algorithm NOT refuted. Fix: promote as G2 seeds; require Q stamp dfa and matches>0 per ID.
M4 utf8 witnesses truncated (alpha[:7] after appending é/\x80): semB1 lacks \x80, outage/zwsp/nbsp lack their bytes. Fix: alphabet from pattern's non-ASCII + \x80/\xc3, assert witness bytes occur.
M5 decline controls: (?<=^a)b|c$ is VM (declines at A4 not A3) — record decline reason, assert per control; CMP-1/Finding I-1 UNREACHED in DFA-only B4 (all failures VM P) — declare; CMP-3/CMP-10 witnesses declined in clean build (Q keeps (?m)^ -> attempt/n) and A2 shares source with the derivation — witnesses with a live Q (\Gab|cd), A2 from an independent walk of Q's tree.
M6 D94 recipe greps route values, misses 105 files reading _DFA_SCAN/_PREFILTER/_START/_MATCH (+ unanchored/unwrapped readers, lib/pcrec.h:1161-1166). Grep by macro/field NAME.
M7 no instrument for G3's attempt clause (cost.py attempts=-1); wrapper figure is loads not attempts. Wire or drop.
S8 G3 constants c=8, growth<=4.5, k set chosen not derived. S9 B1/B2 "zero movers" vacuous: validation = one-TU -Werror probe + derive.c unit check over 35 planted; B3 validation via revend window twin. S10 G6 landing bar = 16 rows (not 5); "byte-identical to what" given COMPOSITE "none" line. S11 sizes.tsv/one_tu_probe.txt no generator. S12 Q cap (arch S3 from r1) missing.
UNREFUTED: K106 128,040,002->3 and 128,024,003->8; trim Q\t^k\n 16,003->48,007 (3.00x); wrapper 32,003->3; corrected controller sound on every DFA-Q case; sqli pruned DFA Q correct on matching subjects; population 79/56 (bench 2, corpus 24, idioms 30) + 9 floor-only reproduce (56 IDs = 47 distinct; 30 survey-author idioms); no hidden constant in A1-A6; bit 55, abi 76 current.
