# Critic B findings, integration.md rev 4.5 (lane/memfn-r45, eb484a02)

B1 MAJOR. Q55 tension is real; at SIMD-off the stamp carries no information.
 Loc: R4.3.5 "One tension, stated"; R4.3.3 "none iff byte-identical to its own SIMD-off compile".
 At -fno-memfn-simd (default until R4f) the artifact IS its own SIMD-off compile, so addendum 3 forces `none`. Addendum 4 can only hold on -fmemfn-simd artifacts. Readings: (a) "kit's plan" = SIMD-layer plan (consistent, nearly empty since M5's planner is scalar); (b) addendum 3 says "when", design hardened to "iff" (tautology still forces none). 
 Fix: R4.3.5: replace "So the plan is visible..." with "Until R4f the stamp is constant `none` on every default artifact; plan attribution at the default build rests on B2's items."

B2 MAJOR. Q55 recommendation leaves bench unable to tell same-abi artifacts differing by --memfn=no-NAME.
 Artifact at SIMD-off carries: abi number, FORMS "none", LIBC (moves only if libc-name set moves). Nothing says the --memfn= string is recorded (D81 forbids conditional stamp). R4d vs its deny: LIBC moves by accident (B5). SWAR-vs-SWAR and every M5' re-plan: indistinguishable. Identity gates/C11 compare bytes: unaffected. Bench hurt.
 Fix (either): state in R4.4.1 + spec hunk + R4a' inbox note that bench attributes via its own recorded build recipe (abi, commit, argv); or add always-present `<PREFIX>_MEMFN_OPTS` ("none" or string), born in R4a' free. Recommend first for now (D77), written explicitly.

B3 MAJOR. C11 vacuous until R4e'/R4f; its sabotage row unreachable.
 Loc: 18.2 (diff default vs -fno-memfn-simd); 17.6 "stamp forced to none on a mover | C11 | diff names >=1 mover"; 10.5 C11 row "movers by ID are non-none".
 At SIMD-off default the two compiles are the same compile: diff empty, movers 0, non-none 0. R4d's movers are SIMD-off movers and per 22 read `none`, contradicting 10.5's "movers non-none" (assertion fails as written). SAB_REACH ">=1 mover" cannot be met before R4e'. Same shape as the registry floor, which IS declared UNREACHED until R4d; C11 gets no declaration.
 Fix: rewrite 10.5 C11 row so "movers non-none" applies to SIMD-on population only; declare C11's FORMS half and the sabotage row UNREACHED (K35) until the first SIMD-on form; say R4d's SIMD-off movers are expected `none`.

B4 MAJOR. Q53 control's list != record's definition.
 Loc: R4.3.3 Coverage + "C11 gains a second assertion"; 17.3 shim declares only memchr, memcmp, memcpy.
 Record = libc functions the artifact's *search code* calls; scan = calls to shim-declared functions in artifact text. memcpy appears in non-search code (capture copies, API) and as the SWAR/vload load idiom in search code (lines 1447, 1920): sets differ, and a pcrec-side scan cannot delimit "search code". Record's own example memmem is not in the shim; M6's backward walk would use memrchr: a function the kit newly adopts is invisible to the control exactly where new. Scan must strip comments/strings and run at every comment tier (comments contain `memchr(` text, e.g. line 1967). Only sabotage witness is a memchr artifact.
 Fix: define the record as every libc function the artifact's code (comments/strings stripped) calls; make the control derive names from the compile, not a hand list (e.g. -O0 -fno-builtin -c, `nm -u`), independent of spelling and shim and matching "as written even if gcc inlines". Or make the shim list the generated union of C12 vocabulary and mf_vocab with a floor. Add sabotage rows for memcmp and memcpy.

B5 MAJOR. Q53: recording idiom memcpy makes the line mislead.
 Loc: R4.3.3 "tells a reader a SIMD-off artifact delegates to libc's own dispatch".
 Fixed-size memcpy loads, constant small memcmp/memchr are inlined/folded and never reach libc; "names as written even if gcc inlines" makes the line a source inventory, so the purpose overclaims. R4d: swar removes memchr, adds memcpy loads: LIBC goes memchr -> memcpy, reading as the opposite of what happened.
 Fix: spec says the record is a source-level inventory, not a promise of an executed libc call; exclude constant-size idiom loads or give them a distinct token; or record only functions that can reach a dispatcher (non-constant-length memchr/memcmp, memmem, memrchr).

B6 MAJOR. Q54: wrong cite and scope; manifest row would break its own check.
 Loc: Q54 "D23 makes it the encoding's"; R4.3.4 lists N7 as search site; 3046 "encoding owns it (D23)".
 D23 is the ASCII case-fold decision, not seam ownership; relevant: D58/DD-12 (backreference compare) and the seam (emit_vm.c:8485, enc_byte.c). N7 is a two-operand run-time-span compare returning a prefix count, not a "search over a byte span": the R4.3.4 definition does not cover it. C17's static half scans src/gen/ only; N7 is src/enc/enc_byte.c, a hand-written for loop (the doc's own named escape), so by C17 item 4 its pending row is stale from birth. M7 lists no MF_VOCAB bump though the op needs a run-time-operand `mismatch` with prefix-count return (3046: "later vocabulary item"); M6 carries one.
 Fix: extend C17 static scope to src/enc/ for N7 with a vocabulary line for the `s[at+i] != ref[i]` loop; add MF_VOCAB bump to M7; widen the definition to "search or span-compare"; fix the D23 cite.

B7 MINOR. R4a' "Trigger: MET (Q39 ruled; Q53 confirms ... before the build)" depends on open Q53. Fix: "MET for the stamp; the libc line's spelling is gated on Q53."

B8 MINOR. abi literal despite "never a literal": R4.3.3 "so the next number is 62 if nothing lands first. It is still never a literal"; 22 R4a' "(62 if nothing lands first)". Drop 62; say "the number current at landing".

B9 MINOR. Wait-status ownership stated two ways: R4.5.2/R4.5.5 declare wait 2 MET; 16's note says whether MET "is the manager's reading ... not this revision's". Fix: 16 points to R4.5.5 item 1, or R4.5.5 cites requests.md as authority; one owner.

B10 MINOR. Stale lines: memfn/CLAUDE.md:14 "(rev 4.4; read its R4.4, then R4.3, first)" -> rev 4.5, R4.5 first. memfn/docs/wake.md (template, low priority): s2 item 4 "R4.4 and R4.3 first"; s4 "Open requests: R-1 (R4b measurement)", "Last journal entry ... (subtree set up)" now false. 10.5 C11 row "movers non-none" (B3). No --memfn-deny/mf_switches stragglers outside annotated history; "R4b pending" (~3729) is history annotated at 22's head; docs/design/memfn/CLAUDE.md is current at 4.5.

B11 NOTE. M5' planner output is not wholly stamp-invisible: the chosen offset-set shows in <PREFIX>_DFA_PREFILTER_OFFSETS (match_api.md:2816). Q55 text should say so; it narrows what a bench consumer misses.

VERDICTS
Q53: spelling (separate line) stands: addendum 3 forbids folding libc into FORMS; a marker in FORMS would also make C11 compare one value against two references. Definition does not: B4, B5. Missed options: whole-artifact record; exclude idiom memcpy; nm-based control. Needed before build: B4's control change plus sabotage rows beyond memchr.
Q54: stands in substance (a third "owned elsewhere" state contradicts addendum 5's two-state vocabulary). Needs B6: cite, definition, C17 scope incl. src/enc/, M7 vocab bump.
Q55: stands (no reading of the rulings does better; at SIMD-off "none when identical" is a tautology). Add B2 (explicit bench attribution rule) and B3 (declare C11 UNREACHED). Missed option: always-present MEMFN_OPTS value line: cheaper than a plan line, D81-compliant, free in R4a'; keep filed with trigger "a bench consumer asks", like the plan-record option.
