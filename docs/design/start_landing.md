# `[START-LANDING]` — RECOVER rows that know the start without walking

**DESIGN NOTE + HAND-TWIN, PROPOSED, revision 2, nothing built.** Revision 1: lane
`landdes`, 2026-10-09, from main `e1e387b9` (abi 71). **Revision 2: lane `landrev`,
2026-10-09, from main `efc58146` (abi 71), applying the D6 panel
`../dev/reviews/2026-10-09-r-startlanding-panel.md` (24 ids, every disposition binding);
read §R2 first.** Nothing under `src/`, `cli/`, `lib/`, `tests/` or `docs/spec/`
changes. Charter: plan row `[START-LANDING]` (`../dev/plan.md`), placed by
`locate_finish.md` rev 2.1 §7.3 (LR-G10) and ordered by D156 addendum 1 (Frank: REVEND
builds first, this is designed in parallel). Evidence: `../../studies/start_landing/`
(own CLAUDE.md): a fact PROBE (a scratch patch that prints the facts and selects
nothing), the census over walk_survey's two populations, an emitter-independent twin
transformer with three guard forms, the three-answerer identity driver (artifact, twin,
libpcre2 10.46), its controls, directional timing, and (rev 2) the derived edit set,
the reader census and the witness-mover derivation.

Read before writing: `../dev/walk_survey.md` §4 K4 and K3 (the survey's class labels,
not known_issues ids); `locate_finish.md` §1.2 (the product and the `CT_*` hand
masks), §2.7 (`.needs` and the path derivation), §5 L0/L2.2, §5.1 (the stamp rule),
§7.3, §7.5, §7.6, §7.9; `start_table.md` §1.1-§1.6 (the row contract and the typed
handoffs) and the shipped `pinned` row (`src/gen/emit_dfa.c` `start_pinned_applies`
`:7910`, `cand_rows[]` RECOVER rows `:8448-8458`); `opt5_step2_twopass.md` (`pinned`'s
proof, whose shape §2 follows); the reviews
`../dev/reviews/2026-10-09-r-locfin-panel.md` LR-G10/LR-G11/LR-G14 and
`../dev/reviews/2026-10-09-r-startlanding-panel.md`.

---

## §R2. What revision 2 changed, by panel id

Every in-place edit carries an `[r2 <id>]` mark. "Applied as disposed" unless the row
says otherwise; where a disposition met the code and needed a sounder version, the row
says so and gives the evidence.

### slcrit3 — generality / family / unlocks

| id | disposition | what revision 2 did | where |
|---|---|---|---|
| SL-G1 | the skip form; re-twin in assert mode; keep the no-guard control; a hostile timing control that must read linear | BUILT SL-G1's post-loop skip ("start = the first well-formed character start at or after `L`") as the primary, with its proof written out in full (§2.5.2). Twinned in ASSERT mode beside SL-E1's Fix A on the extended ill-formed pool (§5.5): 0 differences for both. Timed on 1 MiB well-formed text and on six hostile subjects, against today and against revision 1's restart (§5.6). The restart reads quadratic (2.99 s / 4.67 s at 64 KiB, against today's 0.08 / 0.13 ms); both linear forms read linear. **Measured winner: the skip** (§2.5.5); Fix A is kept as recorded. The hostile control is a STANDING timing/sabotage cell with a 10 s wall bound (§7.3) | §2.5, §5.5, §5.6, §7.3 |
| SL-G2 | Λ.2/Λ.3/the guard over `start_cls`/`onebyte_max`; depth bounded by the walk; whether K50's gate implies Λ.2, checked | Λ is stated over the seam (§2.4): "mid-character" is "reads only bytes `PcrecEnc.start_cls` does not admit"; the guard is emitted iff the start set holds a byte above `onebyte_max`. The depth bound is the walk's (a frontier deeper than the NFA is a cycle; measured maximum 3). **K50: the GATE does not exist on Λ's population (it is built only for nullable patterns), but its OMISSION CHECK does** (`cstart_check_omission`, `src/ir/nfa.c:1107`): on every non-nullable pattern under a restricting encoding, a first byte outside `start_cls` is a compile-time internal error, checked over a superset closure. So Λ.1 implies Λ.2; Λ.2 becomes an ASSERTION (L3's shape), not a conjunct. Census: `cont-in-start-set` population 0 / 9,858 compiles, as the implication predicts | §2.4, §2.6 |
| SL-G3 | one iterator; `[bmin, bmax]` as its output | `fixed_width` is withdrawn as a separate walk. The fact is the BYTE WIDTH INTERVAL `[bmin, bmax]` from ONE union-frontier iterator with per-depth flags, which `kset_walk` already is; `W = bmin` iff `bmin == bmax`. Cross-check against revision 1's walk: 0 disagreements over 9,858 compiles. The width family is tabled (§3.1) | §3.1, §2.7 |
| SL-G4 | the hand as product masks; §7.5's "exists" mask its first producer; keep the mandatory hand and abort-on-0 | The composite's RECOVER ask hands `CT_LOWER \| CT_UPPER \| CT_START` (EXISTS: a match ends at `e`, its start lies in `[lo, e]`); `rev-end`'s ask hands `CT_LOWER \| CT_UPPER` (WINDOW: the end is speculative, `¬e`). `pinned`, `end-minus-width` and `landing` take a hand only with `e`; `reverse-pass` takes both. `CT_END`/`CT_SEED` are withdrawn as names | §4.3 |
| SL-G5 | the 2×3 grid in §10 and the listing descs; no row merge | §10's grid (start side vs end side × none / bounded / unbounded evidence); the four `.desc` strings name their cell; `pinned` keeps its stamps and deny | §4.1, §10 |
| SL-G6 | Q1: the one character is derived; state it in §2.3 | §2.3.1 derives it: past one character a criterion that does not read F's state ids is unsound (`ab` on "aab"), and the k > 1 condition IS die-together | §2.3.1 |
| SL-G7 | the leanings put to Frank | §9 restates Q1-Q5 under revision 2 with the critics' judgments beside each | §9 |
| SL-G8 | no tuning constant reaches the artifact; label the encoding literals, the two triggers, the instrument caps | §8.4: none reaches the artifact; the encoding literals are gone (SL-G2); the triggers (1 ms, 10%) and the instrument caps are labelled chosen / measured | §8.4 |
| SL-G9 | file U1 (on `[CAP-EARLY-STOP]` / D142) and U2 (on `[OPT-ENDWIN-ENC]`); U3/U4 as filed | §11, a candidates section with triggers; plan.md is the manager's | §11 |

### slcrit1 — exactness

| id | disposition | what revision 2 did | where |
|---|---|---|---|
| SL-E1 | build SL-G1's form as primary; twin both with the hostile control; take the measured winner; the timing control becomes standing | Fix A rebuilt in this lane's twin (`mktwin.py --guard=inblock`, from slcrit1's scratch form), twinned and timed beside the skip (rows above). Fix A is exact (0 differences) and linear; it is RECORDED, not chosen (§2.5.5) | §2.5.3, §5.5, §5.6 |
| SL-E2 | self-synchronization as a stated precondition; feeds `[ENC-DATA]` | §2.4's precondition P0; a non-self-synchronizing backend must decline the fact, and that is a question for `[ENC-DATA]` | §2.4 |
| SL-E3 | the decode signature, beside the guard | §2.5.4: `$_decode(s, end, p, *cp)` reads `s[p]` unguarded; both guard forms call it only at `p < e ≤ n`, and `L < e` whenever F accepts (Λ.1) | §2.5.4 |
| SL-E4 | always keep the ill-formed tokens plus one representative per multibyte lead class | `mksubj.py` rev 2 (§5.5): CLASS-OWN characters by class-product ranking, CLASS-OWN TRUNCATIONS, and fourteen fixed ill-formed tokens (lone continuation, truncated leads, `FF`, overlongs, a surrogate, > U+10FFFF, `F5`, lead runs), never thinned. Two instrument defects this lane found in its own first two pools are recorded (§5.5) | §5.5 |

### slcrit2 — fit / checks / readers / census

| id | disposition | what revision 2 did | where |
|---|---|---|---|
| SL-C1 | the empty-engine conjunct; a probe line, a census arm, witness `a\bb` | Every new row opens with the shared `recover_on_path(cx)` read that `pinned`'s P4 becomes (one function, three callers; after L0 it IS the path's RECOVER-on-the-path read). The probe prints `LANDEMPTY`; the census has an `empty` arm: 63 corpus empties, 44 with `W ≥ 0`, 0 bench. Witness `a\bb` (`W = 2`) | §2.6, §3.2, §5.2, §7 |
| SL-C2 | DERIVE the edit set by census | `edit_set.tsv` (the text SL1-SL3 change, as data) run through `start_table/sabotage_anchors.py`: 3 ANCHOR re-aims (S221, S223, S693), 21 sites re-run at SL2, 5 at SL3, 92 after. `readers.sh` (a token file, every check surface of both trees) and `witness_movers.py` (every witness the readers and the 596 sabotage rows compile, put through the probe) DERIVE the reader set and its movers; the patterns built at run time are listed as such and hand-probed, marked so. Every gate the panel named is found | §4.5, §7.4 |
| SL-C3 | the dead-group fill at every new success site, plus witnesses | ONE success-site emitter carries `caps[0]`, the K78 fill and `return 1`, and every action calls it, so a new action cannot omit the fill. Witnesses `(a){0}(b){0}c\|d` (`end-minus-width`, a shipped K78 witness that moves) and `(a){0}\w+` (`landing`, constructed), both twinned | §4.1, §7.2 |
| SL-C4 | re-aim S218/S220/S227's reach under `-fno-start-width` | DERIVED, not only the three: the reach re-aims are the rows whose witnesses move AND whose reach reads the reverse machine (S218 `$`, S220 `(?!a)` and its 4-pattern manifest, S227 `foo\B`), plus 5 `run_scan_edge_census.sh` rows; each compiles under `-fno-start-width`, which restores R. S219 does not move | §7.4 |
| SL-C5 | a standing gate in run_search_pinned's shape; the per-row reach fixed; row 3 dropped or witnessed; row 9 not a duplicate | `tests/codegen/run_start_landing.sh` (§7.3): stamp ⇔ body ⇔ mirror, floors from the census, deny identity, every-startpos sweeps including the ill-formed pool, hand witnesses, a corpus `.rxt`, the hostile cell. Row 2 now has a witness (`a\b` forced to `landing` FAILS, 64,200 call differences); row 3 is DROPPED (Λ.2 is K50-NULLGATE's checked invariant); row 4 has a witness per reachable NEXT form, `é(?:x$)?` constructed for `offset-set-bounded`, and the two `first-*` forms DECLARED UNREACHED (seeded-only rows; Λ ⇒ unseeded); row 9 is restated as distinct from S222 | §7.3, §7.5 |
| SL-C6 | the hand rides (slot, route, hand) in §2.7's closure key; L2.2 names the filter; whoever lands second carries it | §4.3: the stamp and its seven readers read RECOVER's cell from the PATH (the closure's (RECOVER, route, hand)), never a fresh hand-less ask. `locate_finish.md` L2.2 gains an `[r2-landing]` note | §4.3, `locate_finish.md` L2.2 |
| SL-C7 | a both-denied test-axes product arm with floors | The product arm `-fno-start-width -fno-start-landing` with floors: on 46 bench / 1,258 corpus rows BOTH new rows apply, and only the product arm reaches R there. `run_search_pinned.sh` §10's independent reference denies all three (25 corpus pinned rows have `W = 0` and fall to `end-minus-width` under `-fno-start-pinned` alone) | §7.2 |
| SL-C8 | B1 gets a hand-witness `--emit-facts` check; correct the count | SL1's check is a table of LITERAL expectations written from the definitions (§7.2), never read off the walk. The count: 0 of the 2,225 Λ-OK (pattern, config) compiles are seeded (revision 1 said "0 / 3,100 Λ rows", a different denominator) | §2.6, §7.2 |
| SL-C9 | regenerate the census TSVs and fix the numbers | `results/census_*.tsv` regenerated at `efc58146` with the rev-2 probe: default corpus 1,750 = 1,334 `end-minus-width` + 416 `landing`; hybrid `landing` 71; `reverse-pass` 1,100; empty 63. Coverage reproduces exactly (42.58 + 3.94 + 8.11 ms) | §4.5, §5.2, §6 |
| SL-C10 | the bench readers into the SL4 inbox note | §4.5's bench table: `tools/selfcheck.py:5871`'s hard gate, the fixture records, `testees/pcrec/list_axes.tsv:117-118`, the adapter's closed enum, the report legend, the trend META key | §4.5, §7 SL4 |
| SL-C11 | the mask derives from axes.def; PCREC_AXIS rows, pcrec.h bits, tuning.md headings; the declared listing and trace files | §4.3 and §7 SL2: two `PCREC_AXIS` rows (the K92 mask derives), two `pcrec.h` bits, two `tuning.md` headings, `listing_declared_SL2.tsv` (read by `start_table/listing_diff.py`) and `trace_declared_SL2.txt` | §4.3, §7 |

**What did not survive contact with the code, and the sounder version taken.**
- **SL-C2's "S218-S222 are re-anchored" (revision 1's §7) was a hand list, and the
  derivation splits it.** Of the five, only S221 and S223 have anchor TEXT the build
  rewrites; S218, S219, S220 and S222 anchor on text no commit touches. What moves for
  S218/S220 is REACH (their witnesses move), which is SL-C4's class, and S219/S222 move
  neither way. S693 (the abi literal) is the third anchor re-aim.
- **SL-G3's "kset_walk's own union-frontier walk" holds for the width, not for Λ.** Λ
  needs per-byte successor sets (a union frontier cannot isolate one path, the same
  reason `kset_walk` over-approximates), so Λ shares the iterator's CLOSURE STEP and
  its per-depth "assertion reached" flag, not its union. §2.7 says which object is
  shared.
- **SL-E4's "one representative per multibyte lead class" was not enough as first
  built.** The first pool (one smallest character per lead class) passed the no-guard
  control on rows whose own lead was never truncated (`(?i)s`'s `C5`, `[α-ω]`'s `CE`),
  and left 24 of 274 rows' exhaustive pools without one matching subject. The pool now
  carries class-own characters by class-product ranking AND class-own truncations
  (§5.5).

---

## 0. Answers first

1. **(a) The fact (§2).** The survey's statement, "every start-set byte takes the
   anchored machine to accepting", is sound in byte encodings and too narrow under
   utf8: a lead byte alone accepts nothing, and the two largest K4 cells are utf8. The
   fact this design reads is **Λ, the ONE-CHARACTER fact**, stated over the encoding
   seam `[r2 SL-G2]`: *from the pattern's own anchored start, every one-character path
   ends DEAD or UNCONDITIONALLY ACCEPTING, no assertion is reached before that, and the
   pattern is not nullable.* The one character is DERIVED, not chosen (§2.3.1
   `[r2 SL-G6]`). Under Λ the forward scan's LAST landing is exactly the start today's
   reverse pass returns, on every call (§2.4). That is answer identity with TODAY'S
   ARTIFACT, not only with PCRE2, and it is what makes the row NEUTRAL on hybrids.
   Under the invalid-tolerant contract one runtime step is owed where the start set
   holds a byte above `onebyte_max`: **if the character at the final landing `L` does
   not decode, the start is the first position after `L` at which one does** (the
   post-loop SKIP, `[r2 SL-G1]`, proved in §2.5.2, linear, no re-entry, no hot-path
   statement). Revision 1's restart was QUADRATIC (SL-G1/SL-E1) and is withdrawn. The
   owner is `src/facts/kset.c`, as a new E3 fact. The exact "excursion" condition admits
   more, but its measured upper bound on the bench is 0.58 ms of 54.6 ms: FILED (§2.8).
2. **(b) `end-minus-width` (§3).** The machine's BYTE WIDTH INTERVAL `[bmin, bmax]`
   from the one frontier iterator `kset_walk` already is `[r2 SL-G3]`; `W = bmin` where
   `bmin == bmax`. Exact whenever RECOVER is handed a VERIFIED end, utf8 and ill-formed
   input included. `$`/`\Z`/`\z` do not touch it. The interaction is REVEND: `rev-end`
   asks RECOVER without existence, which neither new row may take (§3.3, §4.3).
3. **(c) The rows (§4).** RECOVER becomes `pinned`, `end-minus-width`, `landing`,
   `reverse-pass`, a 2×3 grid by evidence (§10 `[r2 SL-G5]`). The new rows are routed
   `CR_DFA` only, take only a hand that carries existence (`e`), and open with
   `recover_on_path` `[r2 SL-C1]`. Each has one deny-only bit from an `axes.def` row
   `[r2 SL-C11]`. Their `.needs` omit R, so §2.7's member fold drops the reverse machine
   with no stamp edit. ONE success-site emitter writes `caps[0]`, the K78 fill and the
   return for every action `[r2 SL-C3]`. `RX_DFA_START` and `rx_info.search_form` gain
   two values. One abi event. NEUTRAL on hybrids by window identity, verified per
   prefilter call.
4. **(d) Identity (§5).** Revision 1's twins stand: 310 bench rows and 1,750 corpus
   rows, 193.5 M per-call identity checks, 0 differences, 0 new libpcre2
   disagreements. Revision 2 adds the guard's own sweep: both linear guard forms over
   every utf8 `landing` row (54 bench, 220 corpus) on the extended ill-formed pool, plus
   constructed witnesses, with 0 differences, and two planted controls that fail
   (§5.5). Directional timing: the skip is −31% (`.`) and −39% (`\p{L}+`) against
   today on the bench's 1 MiB utf8 text, Fix A −22%/−28%; on hostile input both are
   linear, 1.8-5.3 ms per MiB, where revision 1's restart takes ~13 min (§5.6).
5. **(e) Predicted bench (§6).** Unchanged: of the 54.62 ms K3+K4 weight (default
   config), the rows take 46.52 ms (85%), `landing` 42.58 and `end-minus-width` 3.94.
6. **(f) Build (§7).** After L0, as SL1-SL4 `[r2 SL-C2]` (renamed from B1-B4, which
   `sabotage_anchors.py` already uses for `[DEC-FALLBACK]`): SL1 the facts (a no-mover,
   with the hand-witness listing check), SL2 the rows, the record and the guard (the abi
   event, with the standing gate `run_start_landing.sh`), SL3 the hand on RECOVER (if
   L2.2 has not landed it), SL4 the bench relay. The edit set, the sabotage re-aims and
   the readers are DERIVED (§7.4).

---

## 1. The question, and why the answer is an identity

RECOVER asks: *given a match END from the forward machine, where does the match
start?* (`start_table.md` §1.2). Today two rows answer it. `pinned` uses zero bytes
of evidence: the start state accepts unconditionally, so the start is `search_from`.
`reverse-pass` is the fallback: a backwards walk over the reverse machine from the
end to the furthest-back accepting position at or after `search_from`.

walk_survey found two classes where the start was known before the walk:
- K4: the match begins at the byte where the start-byte skip LANDED;
- K3: every match has the same width.

Both are new RECOVER rows that hand `SPAN` (`CT_START`) exactly as `reverse-pass`
does, so the locator's output type is unchanged and FINISH is untouched
(`locate_finish.md` §1.2, §7.3).

**The proof obligation is stronger than "PCRE2-correct", and that is deliberate.**
Each new row is proved to return EXACTLY THE START TODAY'S REVERSE PASS RETURNS, on
every call, for every subject and `search_from`. Three things follow:
- PCRE2 agreement is inherited, not re-derived;
- the deny flags yield a genuine control: the denied build recovers the start from an
  independently built reverse machine (`tuning.md` §2.19's argument for `pinned`);
- on a VM hybrid the inlined prefilter's window is byte-for-byte today's, so no VM
  attempt moves and the give-up surface cannot move (NEUTRAL by window identity;
  `locate_finish.md` §1.5 classifies by attempts removed, and these remove none).

The twins test exactly this identity (ASSERT mode keeps the reverse pass and counts
disagreements per call, §5).

**Where to attack §1.** A RECOVER asker whose END is not the forward machine's
verified end. §3.3 names one, `rev-end`, and §4.3 gives it a hand without existence.
Is there another (the trace build's RECOVER asks are the population)?

---

## 2. (a) The `landing` fact

### 2.1 What "the landing" is in the emitted loop

The forward scan (`emit_scan_loop`) runs the NEXT row's block exactly when the
machine holds the start state with nothing accepted:
- `pf_open` (`:5979`) writes the guard `if (<state> == <s0 cell> && last == (size_t)-1) {`;
- every NEXT emitter ends inside that block with `scan_position` at its candidate,
  having re-seeded the state where it re-seeds (`pf_emit_ofs_reseed`, `:6544`).

The block is emitted exactly once, on the generic path or, where `s0` is a scan-edge
head, on the edge path (`emit_scan_loop`'s own comment: "It fires at `s0` and nowhere
else"). Every arrival at state 0 on the generic path re-enters the loop top through
`continue` (state 0 is never a stop state), so every iteration that holds `s0` with
nothing accepted runs the block.

**The record.** The landing row's emitter adds one statement, the block's LAST:
`landing_position = scan_position;`, with `size_t landing_position = <fwd.from>;`
declared beside the forward state (`fwd.from` is `search_from`, or the K82 handoff
position where `req-use` hands off). The first iteration holds `s0` with nothing
accepted on an unseeded machine, so the block runs before any accept and the
initializer is never an answer. So `landing_position` is the position the machine last
stepped from `s0` after a NEXT hand-off: the start of the current EXCURSION.

- **One shared site.** All eight NEXT emitters on `CR_DFA` close their block with one
  of two lines (`pcrec_sb_printf(c, "%s}\n", ind);` in `pf_emit_memchr` `:6140`,
  `pf_emit_bcls` `:6173`, `_bcls_bounded` `:6189`, `pf_emit_ofs` `:6586`,
  `pf_emit_first_class_bounded` `:6803`; `"%s    }\n%s}\n"` in `_memchr_bounded`
  `:6160`, `_ofs_bounded` `:6613`, `pf_emit_first_memchr_bounded` `:6789`). SL2
  replaces them with one `pf_close(c, f)` that writes the record (when `f`'s RECOVER
  action is `landing`) and the brace(s). That is one site, not eight, and a ninth NEXT
  form cannot be added without it.
- **`next-none` has no block**, so no record: `landing` declines there (§2.6 L4).
  Population: 0 of the 2,225 Λ-OK compiles select `next-none`; witness `(?s).+` (Λ
  holds, NEXT `none`, `[bmin, bmax] = [1, ∞)`, so `end-minus-width` does not take it
  either).

### 2.2 The obligation

`landing` is exact iff, on every call that reports a match, today's reverse pass
returns the row's start. The reverse pass returns the smallest `s ≥ search_from`
with `[s, e)` a match of the machine's language, where `e` is the forward machine's
reported end. The forward machine reports the priority end of the LEFTMOST start
(its existing correctness; nothing here changes it). So the obligation is:

> **(E)** whenever the forward scan accepts, the leftmost match start at or after
> `search_from` equals the row's start (the last landing, after the §2.5 guard).

### 2.3 The exact condition, and why it is not the built fact

(E) is a property of the pair (the emitted forward machine F with its state ids, the
thread started at the landing). It can be decided at compile time by a product walk:
- explore triples (F's state, the full thread content, the landing thread's NFA set)
  from (`s0`, fresh, `closure(anch_start)`) over all 256 bytes;
- FAIL if F accepts while the landing thread does not;
- FAIL if F reaches state 0 with anything but fresh threads alive.

F's state ids matter, not only NFA content: minimization can map a state that still
carries the landing thread onto state 0. `xa|a` is the witness. After `x`, the state
`{xa·1} ∪ fresh` is language-equivalent to `fresh` (every future accept of `xa`
coincides with one of `a`), so the guard re-runs and the record moves past a live
thread (control in §5.3: 55,152 wrong answers).

That product is the general form, and it is NOT what this design builds:
- **Measured reach (§2.8):** on the bench it adds at most 0.58 ms of weight over the
  one-character fact (1% of the class).
- **Cost:** it needs F's minimized state ids, so it would be a DFA-layer analysis
  rather than an NFA fact, with its own state budget.
- **Utf8:** under the invalid-tolerant contract, an excursion longer than one
  character needs every byte of `[landing, e)` well-formed, not only the first, which
  is a walk again.

#### 2.3.1 Why ONE character: derived, not chosen `[r2 SL-G6]`

Any criterion that reads only the NFA (not F's state ids) is sound for an excursion of
k characters only if no thread can START inside the excursion. Within one character
that holds: the positions inside a character hold bytes the encoding's `start_cls`
does not admit, and no thread starts there (§2.4 Λ.2, a checked invariant). Past one
character it fails: the position after the first character is a character start, a
fresh thread can begin there, and whether the landing thread or that fresh one
accepts is decided by whether F returns to state 0 when the landing thread dies, which
is a fact about F's ids.

The witness is `ab` on "aab". The NEXT row lands on 0. F reads `a` (thread 0), then
`a` at 1: thread 0 dies, thread 1 starts, and F holds `{thread 1 after a} ∪ fresh`,
never state 0, so the block does not re-run. F reads `b` and accepts at 3. The landing
says 0 and the start is 1. Every one-character path of `ab` is alive-not-accept, so
the one-character fact declines it; a two-character NFA criterion ("dead or accepting
after two characters": after `ab` accepting, after `aa` dead) admits it and is wrong.
So for k > 1 the condition must read F's states — that is the excursion condition
("every thread started inside the excursion dies no later than the landing thread",
die-together), which is the product walk above. One character is the largest k at
which an NFA-only criterion is sound.

### 2.4 The fact Λ, and its proof `[r2 SL-G2, SL-E2]`

**The seam's two fields.** Let `E` be the compile's encoding row (`PcrecEnc`):
`E.start_cls` is the set of bytes at which a character may begin (`NULL` = every
byte; utf8's is "not 0x80-0xBF", `src/enc/enc_utf8.c` `start_cls_utf8`), and
`E.onebyte_max` the largest code point written as exactly one byte equal to itself
(`byte` 0xFF, `utf8` 0x7F). No UTF-8 literal appears below; a third encoding answers
through these two fields and its `PCREC_ENCE_DECODE` row.

**P0, the precondition (SL-E2).** `E` is SELF-SYNCHRONIZING: whether a byte can begin
a character is decidable from the byte alone, so `start_cls` partitions the bytes into
character starts and bytes that only continue one. UTF-8 satisfies it. An encoding
whose trail bytes overlap its lead or one-byte ranges (Shift-JIS, GBK) does not, and
then "a byte outside `start_cls` starts nothing" is not a property of the byte, so
Lemma 1's step below fails. Such a backend must make the fact DECLINE (a seam field
naming the property, or `start_cls` refused at `pcrec_enc_start_cls_ok`). This is the
same question `[ENC-DATA]`'s ASCII-compatibility item asks, and is handed to it.

**Λ (the one-character fact).** Walk the pattern's NFA (`Job.nfa`, the machine's own
language) from `Nfa.anch_start`, closing over ε EXACTLY (an assertion node is not
passed; reaching one is a decline), and require:
1. `closure(anch_start)` holds no accept (not nullable) and reaches no assertion
   (nothing reads the start edge: no `^`, `\b`, `\G`, lookbehind, `(?m)^`, `\K`
   before the first byte);
2. **[an ASSERTION, not a conjunct, `[r2 SL-G2]`]** every byte a consuming state of
   that closure admits is in `E.start_cls` (vacuous when it is `NULL`);
3. for every byte path that consumes ONE CHARACTER from there, the frontier is
   - empty (dead), or
   - reaches accept on an assertion-free ε-path (UNCONDITIONALLY accepting), or
   - (`E.start_cls ≠ NULL` only) still MID-CHARACTER: every live consuming state
     admits only bytes OUTSIDE `E.start_cls`, and the walk continues. The depth is
     bounded by the walk: a mid-character frontier deeper than the NFA's state count
     is a cycle and declines (measured maximum depth over the census: 3).
   Anything else declines: alive-but-not-accepting after a whole character, or an
   assertion before the accept.

**Why Λ.2 is an assertion: K50's omission check implies it, checked.** K50's gate
(`N_CSTART`) is built only for NULLABLE patterns (`pcrec_startgate_needed` is
`pcrec_fact_nullable`); Λ.1 excludes them, so the gate is absent on Λ's whole
population and implies nothing. What does imply Λ.2 is the gate's OMISSION CHECK,
`cstart_check_omission` (`src/ir/nfa.c:1107`): on every non-nullable pattern wrapped
under an encoding with a `start_cls`, it walks the pattern's start closure (assertions
PASSED, a superset of Λ's exact closure) and fails the compile with an internal error
if any consuming state admits a byte outside `start_cls`. So every artifact that
exists satisfies Λ.2, by a check that runs on every compile, not by an assumption.
The census agrees: decline reason `cont-in-start-set` has population 0 over all 9,858
compiles (bench and corpus, both configs), as the implication predicts. The fact's
walk ASSERTS it (a violation is a self-check failure naming K50-NULLGATE, never a
decline), which is L3's shape. Revision 1's sabotage row 3 ("Λ.2 dropped") had no
reachable witness for exactly this reason and is dropped (§7.5).

Λ holds for `\w+`, `[a-z]+\d*`, `C`, `C+D*`, `C{1,n}`, `.+`, utf8 `.`, utf8
`\p{L}+`, `[a-zé]+`. It fails for `ab` (alive after one character), `x*y`, `\w+@`,
`\b\w+` (assertion at the start), `\w+\b` (accept only behind an assertion), and
`.{3,8}`.

**Lemma 1 (fresh at every landing).** Let `L` be a value of the record. Every thread
alive in F at `L` started at `L`, i.e. F holds only the start closure. *Proof:* by
induction over landings. At the first, the call's forward state is the start state
with no prior thread: Λ.1 implies F is unseeded (the seeds `s1u[u]` and `s1g[u]`
differ only through a left-context assertion in the start closure), so the
initializer writes `s0`. At a later landing `L'`, the previous landing `L`'s thread
consumed one character after `L` and, by Λ.3, then died or accepted. Had it accepted,
F would be accepting, the guard would be false, and no landing would follow. So it
died. Every other thread alive between `L` and `L'` started at a byte after `L` that
the machine STEPPED. A byte outside `start_cls` starts nothing (Λ.2, with P0). A
character-start byte inside the excursion is impossible under Λ, since the excursion
is one character. So at the character boundary F holds only fresh threads, which is
the start closure, which is state 0, and the guard runs at `L'`. Minimization cannot
hide a live thread here, because there is none: a thread that dies on every
completion is effectively dead and is irrelevant to the answer. Skipped bytes start no
match (the NEXT row's own soundness, `LOWER`), and a re-seeding skip writes `s0` on an
unseeded machine. ∎ (The ill-formed case, where "one character" is not one, is §2.5.)

**Lemma 2 (the first accept is the landing thread's).** After the last landing `L`,
with the character at `L` well-formed, the first position at which F accepts is one
character after `L`, and the accepting thread started at `L`. *Proof:* by Lemma 1
every thread alive at `L` started there. Threads started inside the character are at
bytes outside `start_cls` and start nothing (Λ.2). The landing thread accepts
unconditionally at the end of its character (Λ.3), and it is the only thread that
can. ∎

**Theorem.** Under Λ, with the character at the final landing well-formed, every call
that reports a match reports `start = landing_position` from today's reverse pass.
*Proof:*
- No match starts in `[search_from, L)` (§2.5.2 Claim A, which needs nothing of Λ).
- A match starts at `L` (Lemma 2), so `L` is the leftmost start.
- The forward machine's `e` is that start's priority end (unchanged code).
- The reverse pass returns the smallest start of a match ending at `e` at or after
  `search_from`, which is `L`. ∎

### 2.5 The guard (the invalid-tolerant contract) `[r2 SL-G1, SL-E1, SL-E3]`

#### 2.5.1 Where the theorem needs it, and where it is emitted

The proof's step "the landing thread consumes one CHARACTER" assumes the bytes at `L`
form one. Under the default invalid-tolerant contract (`match_api.md`, "an ill-formed
sequence matches nothing") they need not. Witness: utf8 `.` on `C3 61`. The landing
is 0 (`C3` is in the start set). The landing thread dies at `61`. The fresh thread
started at `61` accepts. F accepts at 2 without returning to state 0. The landing
says `(0,2)`; today's artifact and libpcre2 say `(1,2)`.

**The emission condition, over the seam `[r2 SL-G2]`.** The guard is emitted iff the
first-byte set of `closure(anch_start)` holds a byte above `E.onebyte_max`. Otherwise
the final landing's thread starts on a byte at most `onebyte_max`, which is by that
field's definition a whole one-byte character, well-formed; and the final landing's
thread always starts (if it did not, F would hold only fresh threads one byte later,
re-land, and `L` would not be final). Under `byte` (`onebyte_max` 0xFF) the guard is
never emitted. A backend with `onebyte_max < 0xFF` must have a `PCREC_ENCE_DECODE` row
(asserted at SL2; utf8 has one), and SL2 adds `PCREC_ENCE_DECODE` to the artifact's
entry mask where the guard is emitted. Census: emitted on 24 of the 27 bench utf8
`landing` rows (each config) and 210 of the 220 corpus default rows; the others have
ASCII-only start sets (`\w+` without UCP, `[[:alpha:]]+`,
`[^\x{80}-\x{10FFFF}]+`).

#### 2.5.2 The skip, and its proof (the design's form)

After the forward loop, before the start is read:
```c
if (!<p>_decode(subject, subject_length, landing_position, &cp)) {   /* ill-formed at L */
    do landing_position++;
    while (landing_position < last_accept_position
           && !<p>_decode(subject, subject_length, landing_position, &cp));
}
size_t match_start_position = landing_position;
```
No re-entry, no new edge, and nothing on the hot path: the statement runs once per
call that reports a match. On well-formed text its first test always succeeds.

**Definitions.** A position `p` is a CHARACTER START iff `$_decode(s, n, p) > 0`.
`L` is the final landing, `e` the reported end, and
`p* = min { p ≥ L : p is a character start }`.

**Claim (exactness).** On every call that reports a match, today's reverse pass
returns `p*`; and `p* < e`, so the loop's bound is never what stops it.

The proof uses four facts, each with its source:
- **F1, the contract.** A match spans only well-formed characters: it starts at a
  character start, and a thread started at a position that is not one never accepts.
  It dies no later than the first byte `d(q)` at which the sequence from `q` stops
  being well-formed; every position strictly between `q` and `d(q)` holds a byte
  outside `start_cls`. (The lowered classes' ill-formed set is exactly `$_decode`'s,
  as `u8_defs_decode_doc` states; `decode_eq.py` checks the seam text against an
  independent Table 3-7 spelling on all 2^32 four-byte windows and every end: 0
  disagreements over 17,179,869,184 cases, §5.5.)
- **F2, Λ.3.** A thread started at a character start `p` whose character `c` is
  well-formed is dead or accepting after `c`, and accepts nowhere inside `c` (every
  accepting path of the lowered machine consumes whole characters).
- **F3, Λ.2.** No thread starts on a byte outside `start_cls`.
- **F4, the loop.** After `L`, F is never in state 0 with nothing accepted (else the
  block would re-run and `L` would not be final); once F accepts, the block never runs
  again.

*Claim A (nothing starts before `L`; needs nothing of Λ).* Bytes a NEXT block skipped
start no match (the row's own soundness, `LOWER`). Every byte F stepped before `L` lies
in an excursion that ENDED with F in state 0 and nothing accepted, which is how a later
landing happens. A match starting inside such an excursion would end no later than the
position where every thread from it had died, and its thread would have accepted there,
so F would have recorded an accept. So no match starts in `[search_from, L)`.

*Claim B (`L` well-formed).* Then `p* = L` and the Theorem of §2.4 gives `s* = L`.

*Claim C (`L` ill-formed).* No match starts at `L` (F1). The call reports a match, so
some thread accepted; it started at a character start `q ≥ L` (at `L` F holds only
fresh threads, and F1), so `p*` exists and `p* ≤ q < e`. Consider position
`r = p* + |c*|`, where `c*` is the well-formed character at `p*`:
- every thread started in `[L, p*)` started on a position that is not a character
  start, so it never accepts (F1), and it is dead by `d(q′) + 1 ≤ p* + 1 ≤ r`: the
  positions strictly between `q′` and `d(q′)` are bytes outside `start_cls`, so if
  `d(q′)` were beyond `p*` then `p*` would be one of them and not a character start
  (and a sequence truncated by the end of the subject has no `d(q′)` only if every
  later position is a continuation byte, which `p*` is not);
- no thread starts inside `c*` (F3);
- so at `r` the live threads are the one started at `p*`, `T*`, if it is alive, and
  fresh ones. If `T*` is dead at `r` (F2), F holds only fresh threads, and no accept has
  been recorded since `L` (nothing before `p*` accepts, and `T*` accepts only at `r` and
  is dead there), so F is in state 0 with nothing accepted at `r > L`, which F4 forbids.
- Hence `T*` accepts at `r`: a match starts at `p*`. Nothing starts before it (Claim A
  for `[search_from, L)`, F1 for `[L, p*)`), so `p*` is the leftmost start, `e` is its
  priority end, and the reverse pass returns `p*`. ∎

Minimization does not change this. A state holding threads from `[L, p*)` can be
merged into state 0 only if those threads never accept (they do not), so such a merge
can only re-land earlier over doomed threads; the claims hold for whichever landing is
final.

**This is SL-G1's sketch written out**: "any well-formed `p` in `(L, s)` is dead,
contradicting finality, or accepting, contradicting leftmostness". The guard is the ⊥
rule (`ucp_design.md`: an ill-formed byte is a pseudo-character no class contains)
applied ONCE, at the one position the answer is read from. It is not a RAISE edge:
revision 1 called it E5's shape, but E5 is NEXT → VERIFIER re-entering the scan, and
the skip re-enters nothing.

#### 2.5.3 Fix A, recorded `[r2 SL-E1]`

slcrit1's in-loop form tests the candidate as the NEXT block's last statement and
steps past an ill-formed one exactly as past a non-candidate:
```c
if (scan_position < subject_length && !<p>_decode(subject, subject_length, scan_position, &cp)) { scan_position++; continue; }
landing_position = scan_position;
```
It is exact for a simpler reason: an ill-formed position starts no match (F1), so
skipping it is the NEXT row's own soundness argument, F is never stepped over it, and
every landing is well-formed, so §2.4's Theorem applies unchanged. It is linear. Its
cost is one decode per landing, on every call, on well-formed text too (§5.6).

#### 2.5.4 The decode's signature and its unguarded read `[r2 SL-E3]`

The seam's entry is `static inline size_t $_decode(const unsigned char *s, size_t end,
size_t p, unsigned *cp)` (`src/enc/enc_utf8.c` `u8_defs_decode`): the length of the
character at `p`, or 0 when it is truncated (`p + len > end`) or ill-formed. It reads
`s[p]` WITHOUT testing `p < end`. Both forms call it only where `p < n` is already
established:
- the skip: its first call is at `L`, and `L < e ≤ n` whenever F accepts (Λ.1: the
  pattern is not nullable, so every match consumes at least one byte, `e ≥ L + 1`);
  the loop tests `landing_position < last_accept_position` BEFORE each later call;
- Fix A: the call follows the block's own `if (scan_position >= subject_length)
  return 0;`, on the same `scan_position`.

`cp` is written and never read; the build passes a block-local.

#### 2.5.5 The pick: the skip, by measurement and by structure

Both linear forms are exact (§5.5: 0 differences each, over the same rows and pools).
The timing (§5.6, 7700X, loaded box, n = 21 per variant per cell; round 2 with
n = 45) reads:
- well-formed 1 MiB utf8 text, the bench's regime: the skip −30.9% / −26.9% (`.`,
  rounds 1 / 2) and −39.1% / −42.2% (`\p{L}+`) against today, every one clearing the
  2(σa+σb) bar; Fix A −22.4% / −15.4% and −28.3% / −35.1%, two of four clearing it.
  The skip is the faster form in all four comparisons; the skip-vs-Fix-A gap itself
  (727 / 940 µs on `.`, 590 / 478 µs on `\p{L}+`) does NOT clear the bar in either
  round on this loaded box, so the ordering is a consistent direction, not a
  significant difference;
- hostile input (six 1 MiB lead-run subjects): both linear, 1.8-5.3 ms per MiB against
  today's 1.27-2.09 ms; neither form wins every hostile cell (Fix A steps no DFA byte
  over an ill-formed run, the skip steps each byte and then decodes it).

The skip is the pick: it is faster where the bench measures, in all four comparisons
and in slcrit1's own measurement (5.35 vs 5.65 ms on `.`), and, which decides it where
the timing alone does not, it puts nothing on the hot path, adds no re-entry edge and
changes no NEXT emitter. Fix A is the recorded alternative; it becomes the better form only if a regime with mostly
ill-formed input is ever measured as material (none is on the bench).

Revision 1's restart (`landing + 1`, re-enter the forward scan) is withdrawn: on
`C3`×k `a` every restart lands, scans to `e` and fires again, so a call costs
Θ(k²) bytes. Measured: 2.99 s (`.`) and 4.67 s (`\p{L}+`) at k = 64 Ki, against
today's 0.08 / 0.13 ms; about 13 min per MiB.

**The standing cell.** `run_start_landing.sh` §H (§7.3) runs both landing witnesses'
find-all over 1 MiB of `C3` then `a` (and the `E2`/`F0` runs) under a 10 s wall bound
and checks the one answer; a planted re-entry (sabotage row 12) is caught by the bound.

### 2.6 The predicate (`landing`)

```
L0′ recover_on_path(cx)                           [r2 SL-C1] one shared read, P4's;
                                                   after L0 it is the path's RECOVER
                                                   member; witness a\bb (W = 2)
L1  route CR_DFA                                  (.routes; RECOVER on CR_ATTEMPT is
                                                   stamp-only and leaves at L2.1)
L2  Λ holds  (pcrec_fact_land_char(cx))           (the fact, §2.7)
L3  F unseeded: !dfa_needs_seed(F), s1u[0] == s0,  ASSERTED, not a conjunct: Λ.1
    s1g == s1u                                      implies it (the census: 0 of the
                                                   2,225 Λ-OK compiles is seeded
                                                   [r2 SL-C8]); start_pinned_
                                                   assert_routing's shape
L4  NEXT selected on CR_DFA has a block           read through cand_read (a DAG
    (map EXACT0 / EXACTK; not `next-none`)         edge RECOVER → NEXT; NEXT reads
                                                   only BOUND, so still acyclic)
L5  the ask's hand carries existence (§4.3)       rev-end asks without it
```
Not a conjunct: Λ.2 (asserted, §2.4). Not nullable (Λ.1), so no clash with `pinned`,
which needs an accepting start state.

### 2.7 Who computes it `[r2 SL-G3]`

**`src/facts/kset.c`, a new E3 fact `land_char`**, sibling of `kset_walk`. Its
header already states why this is the right place: the thread from the candidate
start ALONE exists only in the pattern's own NFA, walked from `Nfa.anch_start`. It is
sealed on the `ENG_UNANCH` branch after the wrap, where `Job.nfa` is the machine the
forward and reverse DFAs are built from (collapsed or not). The prototype
(`proto.patch`, `lp_land_fact`) is ~110 lines over the same `NState` walk.

**What is shared, and what is not.** `kset_walk` is a UNION-frontier iterator: per
byte depth, the union of consuming states, with per-depth flags (accept reached, an
assertion passed, frontier empty). It PASSES assertions: a wider frontier skips less,
the safe direction for a filter. Revision 2 makes that iterator the ONE frontier
object (§3.1): its consumers are the k-sets and the width interval. Λ is not a union
walk — it needs the successor set PER BYTE, because a union frontier cannot isolate one
path (the reason `kset_walk` over-approximates) — so Λ shares the iterator's CLOSURE
STEP and reads its "assertion reached" flag as a decline where the iterator's other
consumers read it as a pass. One closure, one flag, two readers; not a helper with a
mode, and not a second copy of `wclose`. (D120: "one owner per QUESTION".)

Not the DFA: F cannot isolate the landing thread (§2.3's `x*y`/`xa|a`), and the
anchored machine `adfa` is optional (`Dfa.optional`, dropped by the size ladder: utf8
`.` drops it today).

### 2.8 What Λ leaves, measured (the excursion condition is FILED)

On the bench (default config, the auto-caps testee), the rows leave 117 patterns on
`reverse-pass` that carry K3/K4 weight (8.11 ms). Every one was forced through the
LANDING twin in assert mode (`results/twins_residual_forced.txt`):

| outcome | patterns | est. weight | examples |
|---|---|---|---|
| WRONG: the landing is not the start on some tested subject | 34 | 7.42 ms | utf8 `.{3,8}` (2.87 ms: a newline ends the run, the next run starts later), `(a\|)*\d`, `email/orig`, json numbers |
| landing-exact on every tested subject (an UPPER bound for the excursion condition) | 77 | 0.58 ms | utf8 `[\x{400}-\x{4FF}]{4,16}`, `\w+\z`, `\s+$`, `.{80,}`, `in\|instanceof` |
| not twinnable (`next-none`) | 6 | 0.10 ms | `.{8,64}` |

So K4 is, to within 1% of its weight, exactly the Λ class. The excursion condition is
FILED as `[START-LANDING-EXC]` (BOONIES-class, memory `pcrec-high-impact-focus`).
Trigger: a bench cell whose excursion-exact weight exceeds 1 ms (a CHOSEN ranking
threshold, not a measured knee, §8.4). No measurement is chartered.

**Where to attack §2.**
- (a) Lemma 1's "the guard runs at every return to state 0": a scan form where state
  0 is reached on a path that jumps past the block. The edge path's `goto` to the view
  label is the one to read: under Λ, can a pre-accept head's `scan_next` be `s0`
  with the block on the generic path?
- (b) Λ.2 under `-i` with utf8 caseless folding: a fold that lands a byte outside
  `start_cls` in the start set (K50-NULLGATE would refuse the compile: is that a
  reachable internal error?).
- (c) §2.5.2 F1's "dies no later than `d(q)`": a lowered class whose automaton keeps
  a thread alive past the first byte that makes the sequence ill-formed.
- (d) L3 asserted rather than tested: a pattern with an assertion-free start closure
  whose machine is nevertheless seeded.
- (e) A NEXT form whose candidate re-seeds to a state other than `s0` on an unseeded
  machine.
- (f) The K82 handoff: `landing_position` starts at `fwd.from`; is there a handoff
  path on which the block does not run before the first accept?

---

## 3. (b) `end-minus-width`

### 3.1 The fact: the byte width interval `[r2 SL-G3]`

**`[bmin, bmax]`, the second output of the one frontier iterator** (`kset_walk`'s,
§2.7), walked from `Nfa.anch_start` with assertions PASSED (they consume nothing, so
passing them yields a superset of paths, and a bound proved on a superset holds on the
set): `bmin` = the first depth whose frontier reaches accept, `bmax` = the last such
depth if the frontier empties, `∞` if a frontier is still live past the NFA's state
count (a cycle). The row reads `W = bmin` where `bmin == bmax`. Prototype
`lp_width_interval`, ~30 lines; revision 1's `lp_fixed_width` ("accept in exactly one
frontier, with no consuming state there") is kept in the probe as a CROSS-CHECK and
agrees on every one of the 9,858 compiles (`W ≥ 0` iff `bmin == bmax`, and then
`W = bmin`).

**The width family.** The interval is the fifth member of a family the tree already
has, and the members do not share units:

| member | unit | over | reader |
|---|---|---|---|
| `pcrec_minw` (`src/opt/mrl.c`) | bytes, a lower bound | the AST | the MRL prune, `root_minw` |
| `pcrec_cwmin` / `pcrec_cwmax` | CHARACTERS (`A_CLASS`/`A_WCLASS` are 1 in every encoding) | the lowered tree | lookbehind widths, `end_window`'s W |
| `end_window`'s W (`src/facts/endwin.c`) | characters, declined under a multibyte encoding | the AST | WINDOW W1 |
| `kset_walk` | bytes, per-offset sets | the NFA, assertions passed | NEXT's offset-k |
| `[bmin, bmax]` (new) | BYTES, both ends | the NFA, assertions passed | RECOVER's `end-minus-width`; `[OPT-ENDWIN-ENC]`'s missing fact (§11 U2) |

**Why bytes, from the NFA, and not `pcrec_cwmin == pcrec_cwmax`.**
- The width the row needs is in BYTES (`start = e − W` is byte arithmetic).
- `pcrec_cwmax` counts CHARACTERS by definition.
- On the lowered tree it mixes units: a literal `é` is two 1-byte classes (2), but
  `.` is one `A_WCLASS` (1). Utf8 `.` is fixed in characters and variable in bytes
  (`[1, 4]`), and only a byte walk sees it.
- The NFA is also the language the machines recognise. A count-collapsed prefilter's
  NFA is the collapsed one (`X{m,n}` becomes `X{min(m,1),}`, unbounded, so not
  fixed). An erased lookaround is zero-width either way.

So one walk serves every route, with no separate `Nfa.erased` read.

### 3.2 The row's predicate, and what is exact

```
W0  recover_on_path(cx)                     [r2 SL-C1] (witness a\bb: W = 2, an empty body)
W1  route CR_DFA
W2  [bmin, bmax] = pcrec_fact_width(cx), bmin == bmax  (W = bmin)
W3  the ask's hand carries existence (§4.3)
```

**Exact everywhere it applies.** The forward machine hands a VERIFIED end `e`: some
match `[s, e)` exists with `s ≥ search_from`. Every match has exactly `W` bytes, so
`s = e − W`, and today's reverse pass returns that same `s`. This holds:
- under views, seeds and `\G`: no left-context condition is involved, the end already
  satisfied them all;
- under ill-formed utf8: an ill-formed sequence is never part of a match, and the
  match is a path of the byte NFA;
- under `\K` on a hybrid's prefilter (the window start is the ATTEMPT start; `\K`
  moves only the reported one, and the DFA route excludes `\K`).

`W = 0` (`\b`, `(?=x)`, the empty pattern) gives `start = e`. `pinned` precedes it
where the start state accepts invariantly, and the two agree where both apply.

**The empty engine (SL-C1).** A proven-empty body (`dfa_engine_is_empty`, a bare
`return 0`) has a width all the same: 44 of the 63 corpus empties have `W ≥ 0`
(`a\bb`, `\B\b`, `(*pla:a)b`). Without W0 they would stamp `end-minus-width` over a
body with no forward scan, and SL2's movers-equal-census gate would read red by 44.
W0 is `pinned`'s P4 made one shared read; after L0 it is the path's "RECOVER is a
member" (`locate_finish.md` §2.7), so the conjunct is the general fact, not a clause.

### 3.3 `$`, `\Z`, `\z`, and REVEND

**`$`/`\Z` do not change a width.** They consume nothing. `abc\Z` on `"abc\n"` ends
at 3 (the forward machine's `e`), and `e − 3 = 0`. No interaction on correctness.

**The interaction is REVEND's walk.** In `locate_finish.md` §4.1, `rev-end` "asks
RECOVER" (its walk is RECOVER's reverse block seeded at `n`, `n − 1`, so
`RX_DFA_START` reads `"reverse-pass"` truthfully). That end is SPECULATIVE: the walk
itself is what decides whether a match ends there. If RECOVER's first-match walk
were asked there unchanged:
- `end-minus-width` would answer `n − W` for an end that may not be a match end (a
  WRONG ANSWER on any subject whose tail does not match);
- `landing` has no landing at all.

So RECOVER asks carry a HAND, the mechanism FINISH already has (`CandSel.hand`, one
filter in `cand_select`, `locate_finish.md` §2.2), spelled in the product's masks
(§4.3 `[r2 SL-G4]`): the composite's ask carries existence, `rev-end`'s does not, and
the three rows that answer without walking take only an ask that carries it. This is
a general mechanism (the FINISH filter applied to one more slot), not a REVEND clause.
It needs a sabotage row whose witness is an end-pinned fixed-width pattern on a
non-matching tail (row 8, reachable after L2.2).

**Population.** 6 bench / 41 corpus `end-minus-width` patterns are end-pinned
(`view` 1/2 in walk_survey's cells). After L2.2 they go to `rev-end`, and these rows
do not apply to them. `landing` has none (`$` is an assertion).

**A sibling, FILED.** An end-pinned fixed-width pattern does not need a reverse walk
either: a match ending at `n` (or `n − 1` under the `nl_last` tie) starts at
`n − W`, and one anchored run of `W` bytes verifies it. As a LOCATE row that is
`AT(n − W)` handed to `FIN3 verify-at`, plus the tie's second point. That is REVEND's
territory: filed there as `rev-end-width` (§11 U3), trigger "a bench end-pinned
fixed-width cell where the walk exceeds 10% of the cell" (a CHOSEN threshold, §8.4),
6 bench patterns today.

**Where to attack §3.**
- (a) The iterator's cycle test on a machine whose cycle consumes nothing (an
  ε-cycle is closed, not stepped; check).
- (b) A body whose RECOVER end is not a match end of the SAME machine's language:
  hybrid superset prefilters. The reverse machine is built from `rnfa` with the same
  collapse flag; is `Job.nfa` always that language?
- (c) `W` larger than the subject: impossible, given a match exists; the twin's
  find-all covers `e − W ≥ search_from`.

---

## 4. (c) The rows, their predicates, routes, stamps and readers

### 4.1 Order and rows

`cand_rows[]` RECOVER block, first match (spelling of the new fields as
`locate_finish.md` §4.1's; the build lane's):

```c
{ .c = { "pinned", PCREC_NO_START_PINNED, start_pinned_applies },        /* S1, shipped */
  .slot = CAND_SLOT_RECOVER, .routes = CR_DFA, .tok = "pinned", .map = CM_RECOVER,
  .hands = CT_START, .take = { [CAND_ROUTE_DFA] = TAKE_EXISTS },
  .needs = { [CAND_ROUTE_DFA] = { .mach = 0 } },
  .list = { [CAND_ROUTE_DFA] = { "search-start", 1, "pinned" } },
  .desc = "start side, no evidence: the start state accepts ... so the start is search_from",
  .u.recover = { .act = CRA_SEARCH_FROM } },
{ .c = { "end-minus-width", PCREC_NO_START_WIDTH, start_width_applies },  /* S2, new */
  .slot = CAND_SLOT_RECOVER, .routes = CR_DFA, .tok = "end-minus-width", .map = CM_RECOVER,
  .hands = CT_START, .take = { [CAND_ROUTE_DFA] = TAKE_EXISTS },
  .needs = { [CAND_ROUTE_DFA] = { .mach = 0 } },
  .list = { [CAND_ROUTE_DFA] = { "search-start", 2, "end-minus-width" } },
  .desc = "end side, bounded evidence: every match has W bytes ([bmin, bmax] = [W, W]), so the start is end - W",
  .u.recover = { .act = CRA_END_MINUS_W } },
{ .c = { "landing", PCREC_NO_START_LANDING, start_landing_applies },      /* S3, new */
  .slot = CAND_SLOT_RECOVER, .routes = CR_DFA, .tok = "landing", .map = CM_RECOVER,
  .hands = CT_START, .take = { [CAND_ROUTE_DFA] = TAKE_EXISTS },
  .needs = { [CAND_ROUTE_DFA] = { .mach = 0, .asks = ASK(CAND_SLOT_NEXT) } },
  .list = { [CAND_ROUTE_DFA] = { "search-start", 3, "landing" } },
  .desc = "start side, bounded evidence: one character (the landing fact); the start is the NEXT block's last landing, skipped to the first character start where it does not decode",
  .u.recover = { .act = CRA_LANDING } },
{ .c = { "reverse-pass", 0, cand_always }, ...                            /* S4, shipped */
  .take = { [CAND_ROUTE_DFA] = TAKE_EXISTS | TAKE_WINDOW },
  .needs = { [CAND_ROUTE_DFA] = { .mach = M_R } },
  .list = { [CAND_ROUTE_DFA] = { "search-start", 4, "reverse-pass" } },
  .desc = "end side, unbounded evidence (fallback): the backwards scan over the artifact's own reverse machine",
  .u.recover = { .act = CRA_REVERSE } },
```

- **`u.recover.pinned` (bool) becomes `u.recover.act`, a four-valued action.** The
  emission dispatch switches on it. **Every action ends in ONE success-site emitter
  `[r2 SL-C3]`**, `emit_recover_success(cx, c, start_expr, end_expr, ind)`, which writes
  `caps[0]`, calls `emit_dead_group_fill` (K78: every success site of every DFA search
  form must) and returns 1. Today's two success sites (the `pinned` branch and the
  reverse-pass block, `emit_dfa.c:9858`/`:9871`) become calls to it, so an action added
  later cannot omit the fill; the `return 0` sites are untouched (K78: no write on a
  no-match). `dfa_search_is_pinned`'s readers split by what they ask:
  - "is R absent?" is §2.7's member fold at L0 (`.needs`);
  - "is the start `search_from`?" is `act == CRA_SEARCH_FROM` (the hybrid's
    bound-not-answer shape, `tests/codegen/run_search_pinned.sh`).
  Its five callers (`:4475`, `:4542`, `:4597`, `:9764`, `:10734`) and the two name
  readers (`:3215`, `:11506`) are re-classified at SL2 by that split, never by a
  comparison of the row's name (`start_table.md` [r2 sound-m2]); the edit set names them
  (§7.4).
- **`end-minus-width` before `landing`.** Where both apply (`\w`, `[a-z]`, `(?s).`;
  46 bench / 1,258 corpus compiles), the order is by DOMINANCE, not by a timing
  `[r2 SL-G7]`: the two answer identically on the overlap (both are today's reverse
  pass), and `end-minus-width`'s `.needs` is strictly smaller (no NEXT ask, no record,
  no guard, no unseeded machine). The timing agrees and does not decide it (`\w` on
  `syntax/t-1m`: 4756/4643 µs against 4796/4699 µs, inside each other's σ, §5.4).
  `pinned` stays first: its population must not move, and it agrees with
  `end-minus-width` where both apply (`W = 0`).
- **`.needs`** omit R on S1-S3, so §2.7's member fold drops the reverse machine
  (tables, accessor block, stay/scan-edge tables) with no special case, exactly as it
  does for `pinned`. R is still BUILT (`opt5_step2_twopass.md` §8 Q5's compile-CPU
  note applies unchanged; filed with it, BOONIES).

### 4.2 Route coverage

| route | RECOVER asked? | the new rows |
|---|---|---|
| `CR_DFA`, DFA artifact | yes, by the composite | apply |
| `CR_DFA`, a VM hybrid's inlined `<p>_prefilter` | yes, the same emitter (`pcrec_emit_dfa_engine`) | apply; NEUTRAL by window identity (below) |
| `CR_DFA`, the empty body | stamp-only (the body is `return 0`) | decline (W0/L0′, `[r2 SL-C1]`) |
| `CR_ATTEMPT` | stamp-only until L2.1 drops the route bit; the attempt loop's candidate IS the start | not routed |
| `CR_VM` | no RECOVER slot | — |

**Hybrids: NEUTRAL by window identity, verified, not argued.** The survey argued it
from language identity. §1's identity is stronger: per call, the prefilter's
`window[0][0]` is today's. ASSERT-mode twins of 670 hybrid rows (33 bench, 637
corpus) compared it on 68.4 M prefilter calls (every startpos, the VM's RETRY
recomputes included, since they call the same prefilter): 0 differences (§5.1, §5.2).
The superset and collapsed hybrids are covered by the same argument: Λ and `W` are
read from the NFA the prefilter's machines are built from, and the identity is with
that machine's reverse pass. `locate_finish.md` §1.5's classification: NEUTRAL (no
attempt removed). `locate_finish.md` §7.9 (LR-G14) is subsumed where Λ holds (a `SPAN`,
not merely a `LOWER`) and stays BOONIES elsewhere.

### 4.3 The hand, the deny bits, the listing

- **Hands, as product masks `[r2 SL-G4]`.** A RECOVER ask states what its asker knows
  about the end it hands, in `locate_finish.md` §1.2's vocabulary:
  - the composite's ask (VERIFIER → RECOVER): a match ENDS at `e` and its start lies in
    `[lo, e]`, existence proved — `CT_LOWER | CT_UPPER | CT_START`, the EXISTS mask
    (`([lo, e], e, D = {e})`). This is §7.5's filed "exists" mask, and the composite is
    its first real producer;
  - `rev-end`'s walk (L2.2): candidate ends `{n − 1, n}`, existence NOT proved — the
    WINDOW mask `CT_LOWER | CT_UPPER`, `¬e`.
  A row's `take` lists the masks it accepts: `pinned`, `end-minus-width` and `landing`
  take only a hand with `e` (each answers by arithmetic or bookkeeping that is exact
  only if a match ending at `e` exists); `reverse-pass` takes both (the walk decides
  existence itself). The hand is MANDATORY on a RECOVER ask: an ask with `hand == 0`
  aborts, the FINISH rule (no silent default). Revision 1's `CT_END`/`CT_SEED` are
  withdrawn: they named two points of the product the masks already name.
- **The closure key `[r2 SL-C6]`.** §2.7's path closure visits each (slot, route,
  HAND), and `RX_DFA_START`, `search_form` and every reader of the RECOVER selection
  (`dfa_search_start_of` and its seven readers, §4.1) read the cell the PATH asked,
  never a fresh hand-less ask. On an L2.2 artifact where `rev-end` is selected, the
  emitted RECOVER ask is `rev-end`'s (WINDOW), its row is `reverse-pass`, and the stamp
  says so; the composite's EXISTS ask is off the path and is not what the stamp reads
  (6 bench / 41 corpus end-pinned fixed-width artifacts, where a hand-less read would
  stamp `end-minus-width` over a reverse walk). Sequencing: whichever of
  `[START-LANDING]` and L2.2 lands second carries the hand; if L2.2 lands first it adds
  the field with `reverse-pass` taking every mask (no mover), and SL3 adds the three
  rows' `take` (`locate_finish.md` L2.2, `[r2-landing]` note).
- **Deny bits `[r2 SL-C11]`.** Two deny-only bits, `-fno-start-width` /
  `PCREC_NO_START_WIDTH` and `-fno-start-landing` / `PCREC_NO_START_LANDING` (bit
  numbers the manager's), each one `PCREC_AXIS` row in `src/core/axes.def` beside
  `PCREC_NO_START_PINNED`'s (`:174`) and one `lib/pcrec.h` bit. Since K92 the
  `strategy_denials` mask DERIVES from `axes.def` (`emit_dfa.c:3077-3086`), so they are
  masked out of `rx_info.flags` with no edit there (no answer moves, so a declined
  artifact is byte-identical under either flag). Under either deny the walk falls to
  the next row. The bottom of the chain is `reverse-pass`, an independently built
  machine; where both new rows apply, only the PRODUCT arm reaches it (§7.2,
  `[r2 SL-C7]`).
- **Listing.** Axis `search-start`: `pinned` 1, `end-minus-width` 2, `landing` 3,
  `reverse-pass` 4, each `desc` naming its grid cell (§10, `[r2 SL-G5]`).

### 4.4 Stamps, by the rule

- `RX_DFA_START` and `rx_info.search_form` read RECOVER's selected `tok` already
  (`dfa_search_start_name`), from the path's cell (§4.3). The two new values fall out
  with no stamp edit, whether this lands before or after L2.1's generated rule.
- `RX_DFA_TABLE`, `RX_DFA_UNIFORM_FOLDS` and `RX_DFA_SCAN_EDGE` fold over L0's
  members. R leaves, so a mover's values can change (e.g. `"mixed"` → `"range"` when
  only R carried the other edge form). These are SELECTION-FACT movers, inside the abi
  event.
- The orientation comment block reads RECOVER's row at L0. Its text moves on movers
  (non-essential comment, inside the event).
- No new stamp. `RX_DFA_PREFILTER` is unchanged: NEXT is unchanged, the record is one
  statement inside its block.

### 4.5 The abi event, and the readers, DERIVED `[r2 SL-C2, SL-C9, SL-C10]`

ONE event, at SL2: `PCREC_ARTIFACT_ABI` N → N+1, where N is main's number when SL2
lands (71 at this pin; 72 if REVEND's L2 lands first). Revision 1's reader list was
written by hand and missed gates (SL-C2); revision 2 DERIVES it three ways, none a hand
list, and the build lane re-runs all three at its own pin:

1. **The text the build changes** (`studies/start_landing/edit_set.tsv`: 23 entries,
   `def`/`token`/`line`, per commit) through `docs/design/start_table/sabotage_anchors.py`
   (§7.4): the sabotage rows whose anchor text moves, and the rows to re-run per commit.
2. **The vocabulary the build moves** (`reader_tokens.tsv`: nine classes — the stamp
   names, the values `reverse-pass`/`pinned`, the axis `search-start`, the reverse
   machine's text, the payload field, the abi and byte pins, the deny plumbing, the
   member-folded machine stamps) through `readers.sh`, which greps every CHECK SURFACE of
   both trees (pcrec's `tests/ scripts/ tools/ cli/ lib/ docs/spec/ src/`, pcrec-bench's
   `tools/ pcrecbench/ testees/ bench/`) and names each file's RUNNER (the Makefile line
   or test script that names it). Output `results/readers.tsv`: 250 (class, file)
   readers over 117 files, 18 of them in pcrec-bench.
3. **The witnesses that move** (`witness_movers.py`): every pattern the reader files
   and all 596 sabotage rows compile statically, through the probe, with the design's
   rows applied (`results/witness_movers.tsv`). The patterns the files build at run
   time (a loop variable, a heredoc) are COUNTED as unparsed per file, so the gap is
   visible; the ones in the gates the panel named were then probed by hand and are
   marked so (`results/hand_witnesses.tsv`).

What the census finds, by class (the gates are the build's obligations; every one the
panel named is here, found by the census and not by the panel's list):

| class | reader (runner) | what moves | the movers found |
|---|---|---|---|
| the abi number | `src/gen/emit_dfa.c:54`; `tests/codegen/run_codegen_tests.sh` `ABI_EXPECT` (make test-codegen); `tests/registry/limits_check.sh` (registry); `tests/codegen/run_recursion_identity.sh` (the identity gate's pin); `tests/mech/sabotages/S693` (anchor); `docs/spec/match_api.md` (the `#error` example and the abi history); `lib/pcrec.h`; `src/gen/CLAUDE.md` | N → N+1 | every reader by grep at SL2 (D94) |
| byte pins | `tests/codegen/manifests/m5_stage1_stamps.tsv` `EMITTED_BYTES` (`run_cpset_structure.sh`, make test-codegen); the size ladder in `tests/resource/run_resource_tests.sh`; `tools/review/out/literal_*.tsv` (generated) | movers shrink (no reverse machine); a mover that drops R may FIT a `--max-emit-bytes` rung it did not (a FIT mover, §7 attack (c)) | resource: `\p{L}`, `[^\p{C}\p{M}\p{P}]`, `(\p{L})` utf8, `(a\|b){1,30000}` `-fno-scan-edge`, `a{65535}` (collapsed prefilter) → `landing` |
| the closed value set | `tests/codegen/run_search_pinned.sh` `START_VALUES` `:128` and its §2 VALUE gate `:438` (make test-codegen, `:609`); `tests/codegen/searchpin_driver.c` | two new values: the gate goes red BY DESIGN ("a new value needs a spec hunk and a line here") | — |
| value expectations | `run_search_pinned.sh` §1 witnesses; its §2 else-arm `:476` (a non-pinned value is read as reverse-pass and must carry R) | movers lose R | §1: `abc` (W 3), `$` (W 0), `(?!a)` (W 0) → `end-minus-width` (hand-probed) |
| the K78 caps contract | `tests/codegen/run_nomatch_caps.sh` (make test-codegen, `:549`): its route labels | three witnesses relabel, and they become SL-C3's `end-minus-width` witnesses; its `empty/reverse-pass` witness is EMPTY with `W = 1`, so it is also SL-C1's (without W0 it would stamp `end-minus-width`) | `(?(DEFINE)(?<x>\b))b(?&x)` W 1, `(?(DEFINE)(?<g>a))(?&g)b` W 2, `(a){0}(b){0}c\|d` W 1; `(?(DEFINE)(?<x>a))[^\x00-\xff]` empty, W 1 (hand-probed) |
| member-folded machine stamps / edge counts | `tests/codegen/run_scan_edge_census.sh` (`:541`), `run_premul_table.sh`, `run_dfa_uniform_fold.sh`, `run_clspack.sh`, `run_form_census.sh`, `run_tune_dial.sh`, `run_encoding_checks.sh` | a mover's reverse edge counts go to 0 | scan-edge census: `(foo\B)`, `foo\B`, `\Bfoo\B`, `\bfoo\B` (all W 3, `r=1`) and `[0-9]{3}\z` (W 3, `2 1 1`) (hand-probed); they compile under `-fno-start-width` (§7.4). `\b\w\b` (W 1) loses R too, but its row reads forward edges only (`f=1`) |
| the oracle's witness set | `tests/codegen/cand_oracle_witnesses.tsv` (`run_cand_oracle.sh`) | a line per new row identity is owed (its [MECH-REACH] contract); its three RECOVER lines (`pinned a?+`, `reverse-pass -fno-start-pinned a?+`, `reverse-pass a(b\|c)+d`) do not move; 13 other lines' RECOVER moves under them | SL2 adds `end-minus-width - abcd`, `landing - \w+`, `reverse-pass -fno-start-width -fno-start-landing abcd` |
| the payload field | `tests/codegen/cand_rows_check.py` (`run_cand_rows.sh`), `u.recover` member checks | `.pinned` → `.act` | — |
| the axis and its listing | `tests/registry/axes_registry_check.sh` (reads the `match_api.md` "which of two forms" COUNT phrase, so it must change), `tests/registry/run_registry_tests.sh` (make test-registry), `scripts/emit_sweep.py`, `tests/lookaround/d27/gen_adversarial.py` | two rows; the registry's PASS count and `docs/spec/registry.md`'s row count move (slcrit2 measured 216 → 222 PASS and 157 → 159 rows with its proto; re-derived at SL2) | `axes_registry_check.sh`'s `a(b)` → `end-minus-width` |
| deny plumbing | `src/core/axes.def`, `lib/pcrec.h`, `cli/main.c`, `tests/axes/run_axes.sh` (make test-axes), `tests/codegen/run_facts_checks.sh`, `run_prechecks.sh`, `tests/island/run_island_tests.sh`, mech S65/S67/S295 | two bits; the axes sweep gains two arms and the product arm (§7.2) | `run_axes.sh`'s `x\p{Xwd}y` → `end-minus-width` |
| the sabotage rows' reach | mech rows whose witness moves AND whose reach reads the reverse machine | §7.4 | S218 `$`, S220 `(?!a)` (+ `manifests/s220_view_decliners.txt`: `\B`, `\B\B`, `(?![^a])`, `(?!a)`), S227 `foo\B` |
| other gate movers | `run_codegen_tests.sh` (`a`, `abc`, `a\nb`, `a\Kb`, `a(b\|c)d`, `(?<=a\|é)x`), `run_anchored_match.sh`, `run_recursion_identity.sh`, `run_cpset_structure.sh` (`[^a]`) | each re-run at SL2; a structural check that reads the reverse machine's TEXT on these witnesses re-aims under `-fno-start-width` | 112 of the 364 extracted (file, pattern, flags) witnesses move (`witness_movers.tsv`): 77 sabotage-row files and 10 gate files; most sabotage witnesses plant a site that is not on the reverse path (§7.4 classifies them) |
| spec | `docs/spec/match_api.md` (the `DFA_START`/`search_form` value tables, the "which of two forms" paragraph, the abi history), `tuning.md` (§2.19 generalised to the axis, two deny headings), `cli.md` (the deny list), `registry.md`, `limits.md` | D80: the contract moves | — |

**pcrec-bench (read only; relay in SL4's inbox note `[r2 SL-C10]`).** `readers.sh`
finds 18 bench files. The ones that are gates or pins:
- `tools/selfcheck.py:5871` — a HARD gate: `if st_all == ["pinned", "reverse-pass"]`
  ("dfa_start is not a constant: BOTH values on real artifacts"). Two new values make
  `st_all` four elements, and the check reads its else-arm. It must be rewritten
  (assert ⊇ {pinned, reverse-pass}, or the closed four-value set) in the bench's own
  change, before or with the pin that carries SL2;
- `testees/pcrec/list_axes.tsv:117-118` — the declared `search-start` listing, which
  the bench's check-harness diffs against `--list-axes`: two rows, and
  `reverse-pass`'s rank 2 → 4;
- `testees/pcrec/adapter.py:804` — `dfa_start`'s CLOSED enum `["pinned",
  "reverse-pass"]`, checked against the listing; `shim.c`, `driver.c`, `configs.toml`;
- the fixture records under `pcrecbench/tests/fixtures/v14_pair/store/records/` and
  `selfcheck.py`'s fixtures (`:3412-3484`: the `start-pinned` byte deltas and the
  `reverse-pass` fold control), `pcrecbench/tests/test_report.py`;
- `pcrecbench/report.py:763`, `:2542`, `:5641` (the `start=<pinned|reverse-pass>`
  legend); `tools/trend.py` / `trend_snapshot.py` (`dfa_start` is a trend META key, so
  the movers show as stamp changes in the trend).

**Where to attack §4.**
- (a) A `dfa_search_is_pinned` reader that means "R absent" but is re-keyed to
  `act == CRA_SEARCH_FROM` (or the converse).
- (b) The `take` filter's totality: for every (RECOVER ask, hand mask), the last row
  taking it is undeniable. `reverse-pass` takes both; any future RECOVER row that
  takes neither is a self-check failure.
- (c) The mandatory hand on asks that are stamp-only today (RECOVER on `CR_ATTEMPT`,
  on `empty`): which mask does a stamp-only ask carry?
- (d) A machine stamp that folds over R by a path that does not read the members.
- (e) A reader the census cannot see: a check that reads the reverse machine through
  a token not in `reader_tokens.tsv`. The token file is the census's one hand input;
  its classes are the vocabulary §4.4 says moves.

---

## 5. (d) Answer identity: hand-twins, controls, timing

### 5.1 Method and the bench population

**The twin is emitter-independent.** `mktwin.py` edits TODAY'S artifact text,
anchored on emitted lines (every anchor asserted):
- it adds the record as the NEXT block's last statement;
- under utf8 it adds the guard, in one of three forms (`--guard=skip`, the design's;
  `inblock`, Fix A; `restart`, revision 1's), calling THE SEAM'S OWN `$_decode` text,
  read from `src/enc/enc_utf8.c` at twin time `[r2 SL-E3]` (revision 1's twin carried
  its own Table 3-7 test; that spelling is now `decode_eq.py`'s independent control);
- `replace` mode deletes the reverse block;
- `assert` mode keeps the reverse block and counts, per call of the DFA body (a
  DFA artifact's `_search`, or a hybrid's `<p>_prefilter`), the calls whose row
  start differs from the reverse pass's.

**The selection is the PROBE's**, not the twin's. `census.py` runs pcrec built with
`proto.patch` (which prints the facts and selects nothing; its artifacts are
byte-identical to an unpatched build's, checked on 22 compiles at this pin with the
same output name) and applies §2.6/§3.2's predicates to the printed facts.

**The driver** (`check.c`, adapted from `studies/revend_twin/check.c`) links the
artifact, the twin and libpcre2 10.46 (utf8: `PCRE2_UTF | PCRE2_MATCH_INVALID_UTF`;
`-i`: `PCRE2_CASELESS`). For every subject it compares every `search_from` in
`[0, n+1]` (subjects over 512 bytes: 64 sampled plus the last 8) and a find-all.
Three pools per row:
- `ex`, machine-derived and exhaustive (§5.5 for revision 2's);
- the corpus and edge pool of `studies/revend_twin/mksubj.py`;
- the bench's OWN subjects for the row (throughput first, find-all over the whole
  subject).

**Bench, every design-selected row, both configs** (revision 1,
`results/twins_bench.txt`; 310 (pattern, config) rows; `end-minus-width` 191 DFA + 31
hybrid, `landing` 32 byte + 54 utf8 + 2 hybrid; the rev-2 census selects the same
rows):

| | rows | cells | twin ≠ artifact | DFA-body calls compared | call differences | libpcre2 disagreements (artifact / twin / twin-only) | find-all calls / differences |
|---|---|---|---|---|---|---|---|
| `landing`, byte | 32 | 16,391,036 | 0 | 19,203,458 | 0 | 0 / 0 / 0 | 7,490,332 / 0 |
| `landing`, utf8 (guarded) | 54 | 12,748,380 | 0 | 10,219,260 | 0 | 0 / 0 / 0 | 9,312,862 / 0 |
| `end-minus-width`, DFA | 191 | 53,083,148 | 0 | 17,965,238 | 0 | 14,504 / 14,504 / 0 | 12,243,869 / 0 |
| hybrids (`landing` 2, `end-minus-width` 31) | 33 | 9,296,618 | 0 | 2,742,756 | 0 | 0 / 0 / 0 | 1,270,273 / 0 |
| **total** | **310** | **91,519,182** | **0** | **50,130,712** | **0** | 14,504 / 14,504 / **0** | 30,317,336 / **0** |

The 14,504 libpcre2 disagreements are all utf8 `\B` (`utf8/asr-b-midchar`, `W = 0`)
at an ill-formed subject END: pcrec answers `(2,2)` on `61 C3`, libpcre2 none. That
is K74 (`../dev/known_issues.md`, OPEN, deferred), pre-existing and identical in the
artifact and the twin. The driver's find-all advances to the match end (the
pre-[K75] protocol); it is the same loop on both sides, so the identity holds under
either. Revision 1's utf8 rows carried the restart guard; its answers equal the
skip's wherever both are exact, and §5.5 re-twins every utf8 row with both linear
forms.

### 5.2 The corpus `[r2 SL-C9]`

`results/twins_corpus.txt.gz` (revision 1) covers every corpus pattern block the design
selects, in the default config, with the same three pools and two changes: the `ex`
pool capped at 12,000 subjects, and the third pool the block's own subjects
(walk_survey's synthesized 16 KiB subjects around each block's match).

**The census, regenerated at this pin with the rev-2 probe** (`results/census_*.tsv`,
`results/coverage_*.txt`): default config 1,750 rows = 1,334 `end-minus-width` + 416
`landing` (196 byte, 220 utf8); hybrids `end-minus-width` 566 and `landing` 71;
`reverse-pass` 1,100; `pinned` 192; 63 EMPTY (44 with `W ≥ 0`, §3.2); 1,457 with no DFA
body. Revision 1's "1,751 rows, 1,334 + 417" counted one row from an abandoned
fit-ladder attempt (`tests/uprops/size_ladder_prefilter_drop.rxt:15`; `census.py`
judges by the emitted artifact since report F-L4) and one more that moved since its
pin (`tests/utf8/wclass_illformed.rxt:246`); the twins below covered the 1,750.

| | rows | cells | twin ≠ artifact | DFA-body calls / diffs | libpcre2 (artifact / twin / twin-only) | find-all calls / diffs |
|---|---|---|---|---|---|---|
| all | 1,750 | 169,952,746 | 0 | 143,323,191 / 0 | 43,440 / 43,440 / **0** | 56,164,734 / 0 |
| of which hybrids | 637 | 70,893,458 | 0 | 65,703,299 / 0 | — | 17,892,005 / 0 |

The 43,440 libpcre2 disagreements are all pre-existing and identical on both sides:
- `(()|^){0}[b]` is the documented PCRE2 10.46 optimizer quirk
  (`../dev/upstream_issues.md`; `tests/base/fuzz_regressions.rxt:29`).
- utf8 `$`, `\b` and `\B` at an ill-formed END are K74.
- `(a(b)?)+` and `((?=(a+))a)+` give up on capacity (rc −3) on a 2,000-byte run, where
  libpcre2 answers. A give-up is in-contract.

Bench and corpus together (revision 1):
- 2,060 twinned rows and 261.5 M cells;
- **193.5 M per-call identity checks, 0 differences**, of which 68.4 M are hybrid
  prefilter calls;
- 86.5 M find-all calls, 0 differences.

### 5.3 Controls that fail (`results/controls.txt`, and §5.5's two)

Each control plants a fault the harness must see.

| control | what is planted | the failure seen |
|---|---|---|
| `x*y`, `xa\|a`, `ab\|x*y` forced through `landing` (Λ declines them) | a landing on a pattern where a live thread survives a return to state 0 (minimization merges `{xa·1} ∪ fresh` into `s0`) | replace mode: 55,152 / 55,152 / 17,491 twin ≠ artifact on `ex`, each also a NEW libpcre2 disagreement; assert mode: 79,756 / 79,756 / 25,499 call differences |
| utf8 `.{3,8}` forced through `landing` (guarded) | a multi-character excursion under the tolerant contract | 4 call differences (assert), 2 NEW libpcre2 disagreements (replace), e.g. `61 CE 7A 7A 61`: twin `(0,5)`, libpcre2 `(2,5)` |
| the guard REMOVED, every bench utf8 `landing` row (rev 2, extended pool) | the ill-formed first character | §5.5: fails on every row whose landing can be ill-formed |
| `a\b` forced through `landing` (rev 2, `[r2 SL-C5]` row 2's witness) | Λ with the trailing assertion PASSED (the assert-after decline removed) | 64,200 call differences (`aa`: landing 0, start 1) |
| `abcd`, utf8 `é` (W = 2 bytes), hybrid `(\d{4})` with `W + 1` | a width off by one, and in particular characters for bytes (`é`: 1 character, 2 bytes) | every call differs (252 / 44,319 / 77,517) |

Four controls do NOT fail: `ab`, `\w+@`, `\w+\b`, `\b\w+`, `[a-z]{2,}` forced through
`landing`. They are recorded because they are informative.
- `ab`'s run-pinned NEXT row only lands on full occurrences.
- The others satisfy the EXCURSION condition (§2.3): every thread dies together.

They are what §2.8's residual sweep measures at scale. `\w+\b` passing while `a\b`
fails is the point of row 2's witness: an equivalent mutant on the first is a real one
on the second, because `a\b`'s landing thread is still alive (pending its view) when a
fresh thread starts one character later.

### 5.4 Directional timing, revision 1 (`results/timing_run{1,2}.txt`, `timing_summary.txt`)

Scratch tier, per the brief's rule:
- Ryzen 7700X, gcc 15.2 `-O2`, `taskset` to one CPU (5, then 9);
- load1 11-12 from other lanes (the box was NOT quiet);
- 3 interleaved repeats × 7 find-all runs per variant (n = 21);
- the bench's own 1 MiB subject;
- span checksum equal on every line.

Median ± σ, µs; "sig" = |Δ| > 2(σ_today + σ_twin):

| cell (form) | run 1 today → twin | Δ | sig | run 2 today → twin | Δ | sig |
|---|---|---|---|---|---|---|
| `\w+` syntax/t-1m (`landing`) | 2517 ± 381 → 1752 ± 106 | −30.4% | no | 2417 ± 689 → 1722 ± 170 | −28.8% | no |
| utf8 `.` utf8/t-1m (`landing`, restart guard) | 7854 ± 135 → 4546 ± 142 | −42.1% | YES | 7724 ± 85 → 4469 ± 193 | −42.1% | YES |
| utf8 `\p{L}+` utf8/t-1m (`landing`, restart guard) | 5107 ± 102 → 3321 ± 68 | −35.0% | YES | 5072 ± 135 → 3284 ± 82 | −35.3% | YES |
| `abcd` litrun/mat-l4 (`end-minus-width`) | 335 ± 6 → 208 ± 5 | −38.0% | YES | 332 ± 12 → 210 ± 6 | −36.7% | YES |
| `\w` syntax/t-1m (`end-minus-width`) | 7874 ± 124 → 4756 ± 113 | −39.6% | YES | 7860 ± 62 → 4643 ± 84 | −40.9% | YES |
| `\w` syntax/t-1m (`landing`) | 7873 ± 86 → 4796 ± 141 | −39.1% | YES | 7838 ± 93 → 4699 ± 124 | −40.0% | YES |
| utf8 `.` (`landing`, NO guard: the guard's cost) | 7825 ± 91 → 4773 ± 228 | −39.0% | YES | 7773 ± 84 → 4520 ± 195 | −41.9% | YES |

- `\w+`'s σ is one cold outlier (5,497 µs, the first run of run 2; the other 20
  samples are 2,165-2,775 µs). Without it the gap clears the bar. As measured, it
  does not, and is reported so.
- On WELL-FORMED text the restart guard costs nothing measurable (its test fires
  never); its cost is on ill-formed input, which these cells do not contain — the
  blind spot SL-G1/SL-E1 found (§5.6 measures it).
- `end-minus-width` against `landing` on `\w`: Δ within σ in both runs.

These agree with walk_survey's twins (−20..−42% on the same cells).

### 5.5 The guard's own identity sweep, revision 2 `[r2 SL-G1, SL-E1, SL-E4]`

**The pool (`mksubj.py` rev 2, SL-E4).** Under utf8 the alphabet is three parts, and
only the first is ever thinned:
1. the ASCII class representatives (at most 6);
2. CLASS-OWN multibyte characters: per multibyte lead class of the artifact's forward
   machine (at most 8, the smallest — the pattern's own — first), every combination of
   continuation-class representatives, the well-formed ones ranked by the summed size of
   the classes they use, the 3 most specific kept;
3. the ILL-FORMED tokens, never thinned: each chosen lead class TRUNCATED (the lead
   alone, and for a 3/4-byte lead also with its first continuation), plus a lone
   continuation, truncated `C3`/`E2 82`/`F0 9F 98`, `FF`, `C0 80`, `E0 80 80`,
   `F0 80 80 80` (overlongs), `ED A0 80` (a surrogate), `F4 90 80 80` (> U+10FFFF),
   `F5 80`, and LEAD RUNS (`C3 C3 C3 C3`, `E2 E2 E2`, `F0 F0`).
Exhaustive to the length the 40,000 cap allows (2 or 3), then a seeded random tail of
4-12-token strings filling the cap.

**Two instrument defects in this lane's own first pools, recorded.** Run 1's pool took
one SMALLEST character per lead class and only the fixed truncations; the no-guard
control then passed on four bench rows whose landing can be ill-formed (`(?i)s`, whose
start set holds `C5`; `[α-ω]+`, `CE`/`CF`), because no truncation of THEIR lead was in
the pool. Run 2 added class-own truncations, and the vacuity count it also added found
the second defect: run 2's continuation variants paired each continuation class with
the first lead only, so `é(?:x$)?`'s pool held no `C3 A9`, and 24 of the 274 rows'
`ex` pools compared no DFA-body call at all (their other pools did). Run 3 is the
class-product form above. A pool that cannot contain the thing it tests is the
population-nobody-counted failure (`../dev/learnings.md` §3); `sumcheck.py` now prints
the vacuity counts beside every total.

**The sweep (run 3, assert mode; `results/twins_guard_run3.txt.gz`).** Every utf8
`landing` row: bench both configs (54 rows) and corpus default (220 rows), each twinned
with the SKIP and with Fix A; the constructed witnesses (`é(?:x$)?` for
`offset-set-bounded`, `(a){0}\w+` byte and utf8 and `(a){0}(b){0}c|d` for K78,
`(?i)s`) with both:

| sweep (assert mode) | rows | cells | DFA-body calls / differences | libpcre2 cells (artifact / twin / NEW_BAD) | find-all calls / differences |
|---|---|---|---|---|---|
| bench utf8 `landing`, both configs, SKIP | 54 | 39,381,952 | 17,961,286 / **0** | 20,489,914 (0 / 0 / **0**) | 12,289,118 / **0** |
| the same, Fix A | 54 | 39,381,952 | 17,961,286 / **0** | 20,489,914 (0 / 0 / **0**) | 12,289,118 / **0** |
| corpus utf8 `landing`, default, SKIP | 220 | 55,823,645 | 20,650,651 / **0** | 28,422,695 (0 / 0 / **0**) | 13,310,969 / **0** |
| the same, Fix A | 220 | 55,823,645 | 20,650,651 / **0** | 28,422,695 (0 / 0 / **0**) | 13,310,969 / **0** |
| constructed witnesses, SKIP (and Fix A, identical) | 5 | 3,116,047 | 1,324,496 / **0** | 2,077,185 (0 / 0 / **0**) | 570,798 / **0** |
| **SKIP total** | **279** | **98,321,644** | **39,936,433 / 0** | 50,989,794 (0 / 0 / **0**) | 26,170,885 / **0** |

Vacuity (`sumcheck.py`): no row compared zero calls over all its pools; 5 corpus rows'
`ex` pools still hold no matching subject (`tests/utf8/axis04_p_categories.rxt`, rare
general categories the class-product ranking does not reach), against 24 rows in run
2; their own and edge pools do. Runs 1 and 2 (`results/twins_guard_runs12_summary.txt`,
the earlier pools) also read 0 differences for both forms, on fewer reachable cells.

**Controls (run 3).** The guard REMOVED (`CONTROL=noguard`) over the 27 bench default
utf8 `landing` rows: **1,168,452 call differences on 22 rows**. The 5 that pass are the
two kinds §2.5.1 predicts: 3 rows with an ASCII-only start set, where the guard is not
emitted at all (`\w+` without UCP, `[[:alpha:]]+`, `[^\x{80}-\x{10FFFF}]+`), and the 2
rows below. And `a\b` forced through `landing`: 64,200 call differences (§5.3, row 2's
witness).

**Observation, not exploited.** On an `offset-set` NEXT whose candidate test covers the
first character's continuation offsets (`é+`, `é+?`), every landing is a well-formed
character by the candidate test itself, so the guard is dead there; the no-guard
control passes on exactly those two rows (with the class-own truncations in the pool,
so not for want of an ill-formed subject). The skip costs nothing on the hot path, so
eliding it there is worth nothing measurable (D77).

### 5.6 The guard's timing, revision 2 (`results/timing_guard_run{1,2}*.txt`)

Scratch tier: Ryzen 7700X, gcc 15.2 `-O2`, `taskset -c 5`; load1 8-13 from other lanes;
interleaved repeats; span checksum equal across every variant of a cell (the
summarizer refuses a cell otherwise); every binary under a 60 s wall bound (none
fired). Subjects: the bench's own utf8 `t-1m` (regenerated from
`bench/utf8/gen_throughput_subjects.py` in a scratch copy; sha256
`ec3b3110…` equals `manifest_throughput.tsv`), and the hostile controls: 2^20 × `C3`
then `a` (`h-c3`), the same with `E2` and `F0` leads, 2^19 × `E2 82` (truncated 3-byte),
349,525 × `F0 9F 98` (truncated 4-byte), and 2^16 × `C3` then `a` (`h64-c3`, the size
revision 1's restart can finish). Variants: `o` today; `s` the skip; `i` Fix A; `r`
revision 1's restart (64 KiB cells only).

Round 1 (3 repeats × 7 runs, n = 21), median ± σ in µs, Δ against today, "sig" =
|Δ| > 2(σ_today + σ_variant):

| cell | today | skip (Δ, sig) | Fix A (Δ, sig) | restart |
|---|---|---|---|---|
| `.` on utf8 t-1m | 8638.7 ± 303.3 | 5973.5 ± 672.6 (−30.9%, YES) | 6701.0 ± 785.3 (−22.4%, no) | — |
| `\p{L}+` on utf8 t-1m | 5499.9 ± 247.8 | 3352.1 ± 225.4 (−39.1%, YES) | 3942.2 ± 243.1 (−28.3%, YES) | — |
| `.` on h-c3 (1 MiB) | 1272.1 ± 41.9 | 2727.6 ± 537.9 | 2506.8 ± 841.2 | — |
| `\p{L}+` on h-c3 | 2093.8 ± 45.6 | 5308.9 ± 181.1 | 3981.8 ± 139.7 | — |
| `.` on h-e2 | 1286.7 ± 18.6 | 3357.3 ± 77.1 | 3960.2 ± 277.9 | — |
| `.` on h-f0 | 1272.8 ± 26.9 | 3108.2 ± 260.2 | 3557.7 ± 54.9 | — |
| `.` on h-e282 | 1308.1 ± 16.5 | 3122.0 ± 333.0 | 2484.7 ± 477.3 | — |
| `.` on h-f09f98 | 1312.7 ± 19.4 | 2910.1 ± 316.4 | 1827.7 ± 370.9 | — |
| `.` on h64-c3 (64 KiB) | 80.0 ± 2.9 | 216.3 ± 34.4 | 247.4 ± 40.3 | **2,985,489 ± 58,510** |
| `\p{L}+` on h64-c3 | 134.3 ± 3.3 | 322.7 ± 36.4 | 236.6 ± 18.5 | **4,673,290 ± 104,901** |

Round 2 (well-formed cells and one hostile pair, 5 repeats × 9 runs, n = 45; load1
8.5; `results/timing_guard_run2.txt`):

| cell | today | skip (Δ, sig) | Fix A (Δ, sig) | skip vs Fix A: \|d\| vs 2(σs+σi) |
|---|---|---|---|---|
| `.` on utf8 t-1m | 8174.8 ± 741.6 | 5978.8 ± 231.4 (−26.9%, YES) | 6918.7 ± 330.8 (−15.4%, no) | 940 vs 1,124: no |
| `\p{L}+` on utf8 t-1m | 6719.4 ± 698.3 | 3883.1 ± 266.3 (−42.2%, YES) | 4361.1 ± 248.5 (−35.1%, YES) | 478 vs 1,030: no |
| `.` on h-c3 | 1288.7 ± 16.9 | 3342.9 ± 147.2 | 3628.2 ± 248.2 | |
| `\p{L}+` on h-c3 | 2137.6 ± 61.7 | 5140.2 ± 131.7 | 3593.0 ± 245.7 | |

Reading:
- **Linear vs quadratic, which is what the control exists for.** On 1 MiB of a lead
  run both linear forms take 1.8-5.3 ms, 1.4-3.1× today's (today walks back one byte;
  both forms decode each byte of the run once). The restart takes 2.99 s and 4.67 s on
  64 KiB, ×37,000 today's; at 1 MiB, ~13 min (slcrit1: 7.0 s at k = 10^5).
- **The pick (§2.5.5).** On the bench's regime the skip is the faster form in both
  cells and both rounds; on hostile input neither wins every cell.
- **Why today is fast on hostile input.** Today's reverse pass walks back from `e`
  one byte and stops; the run itself is only stepped forward. The guard's extra cost is
  the price of not walking back: bounded by one decode per ill-formed byte, never by a
  re-scan.

**Where to attack §5.**
- (a) The twin and the build share `$_decode`'s text; the control that does not is
  `decode_eq.py` (§2.5.2 F1) and libpcre2 on every cell.
- (b) The pool's tokens are the forward machine's classes: a defect that only shows on
  a byte sequence spanning three class-own characters is outside the exhaustive length
  and inside only the random tail.

---

## 6. (e) Predicted bench values

`results/predict.txt` (`predict.py`). Inputs:
- the bench's own set-grain pcrec median per cell (walk_survey's `bench_times.py`:
  newest report per set, older pins, Ryzen 1600);
- two predictions:
  - `G/T`, the uniform-per-byte model: an UPPER weight, a reverse byte priced as a
    forward one;
  - `twin`, the measured median ratio (§5.4, both runs averaged), applied only to
    cells whose shape was timed.

Directional only: another box, older pins, a loaded run.

| cell (default config) | row | today | `G/T` | pred. (`G/T`) | pred. (twin) |
|---|---|---|---|---|---|
| utf8/prp-l `\p{L}+` throughput | landing | 11.77 ms | 0.35 | 7.62 | 7.63 |
| utf8/cls-dot `.` throughput | landing | 13.12 | 0.24 | 9.94 | 7.60 |
| utf8/cls-neg-single throughput | landing | 13.04 | 0.24 | 9.93 | — |
| utf8/ci-neg-fold throughput | landing | 13.03 | 0.24 | 9.92 | — |
| syntax/mod-a, syntax/cls-w `\w+` throughput | landing | 7.12 / 7.09 | 0.42 | 4.12 / 4.11 | 5.01 / 4.99 |
| utf8/cls-mixed throughput | landing | 7.98 | 0.34 | 5.26 | — |
| syntax/unp-p-lc, cls-posix throughput | landing | 6.59 / 6.56 | 0.41 | 3.91 / 3.90 | — |
| syntax/unp-p-uc throughput | landing | 5.82 | 0.30 | 4.07 | — |

The two models disagree in both directions:
- on utf8 `.` the twin saves more than `G/T` predicts (the reverse walk over utf8
  costs more per byte than the forward);
- on `\w+` it saves less (the forward scan-edge loop is the cheaper per byte).

Class totals, default config (`results/coverage_bench.txt`, regenerated at this pin,
identical to revision 1's):
- `landing` takes 42.58 ms of the 54.62 ms K3+K4 weight;
- `end-minus-width` takes 3.94 ms;
- 8.11 ms stays on `reverse-pass` (§2.8: 7.42 of it genuinely not a landing).

nocaps: 42.42 + 0.73 of 51.03 ms. The bench's own run on the targeted hardware is the
verdict (D144 addendum 4); this table ranks, it does not predict a report. The skip's
well-formed timing (§5.6) is within noise of revision 1's restart-guarded twin on the
same cells, so the twin column stands.

---

## 7. (f) The build plan, after L0 `[r2 SL-C1..C11]`

`[START-LANDING]` needs L0:
- §2.7's `.needs` and member fold, so R leaves with no stamp edit, and the path's
  RECOVER-membership read that W0/L0′ is;
- the `CandSel.hand` field FINISH introduces.

It does NOT need L2.1's generated stamp rule (§4.4). It is ordered after L0 and
otherwise independent of REVEND. If it lands after L2.2, SL3 is already done by REVEND
(or REVEND must have done it, §4.3), and the abi number is 72 → 73. Commits are named
SL1-SL4 (revision 1's B1-B4 collided with `[DEC-FALLBACK]`'s B0-B7 in
`sabotage_anchors.py`'s commit order, which gains `SL1`-`SL3`).

### 7.1 The commits

| commit | content | movers | spec | checks |
|---|---|---|---|---|
| **SL1** the facts | `kset_walk`'s frontier walk becomes the ONE iterator (per-depth flags); `land_char` (Λ, sharing its closure step) and `width` (`[bmin, bmax]`, its second output) as E3 facts in `src/facts/kset.c`, registered in `facts.def` (`PF_DERIVED` off `kset_walk` or `PF_CORE`, the facts owner's call), listed by `--emit-facts` | none (no reader) | `docs/spec/facts_listing.md` gains two rows | (a) the census agreement: the fact against the probe's printed value over bench + corpus, 0 disagreements; (b) `[r2 SL-C8]` the HAND-WITNESS listing check (§7.2), which does not share a source with either walk |
| **SL2** the rows | the two rows; `u.recover.act`; `recover_on_path` (one read, three rows); `pf_close` (the record); the skip guard where the start set holds a byte above `onebyte_max` (adds `PCREC_ENCE_DECODE` to the mask there); the one success-site emitter with the K78 fill; the dispatch; `dfa_search_is_pinned`'s readers re-classified; two `PCREC_AXIS` rows + two `pcrec.h` bits; the listing; L3's and Λ.2's assertions | **abi event**: every artifact whose RECOVER selection moves (bench 155 + 155 of 734 compiles; corpus 1,750 default / 1,751 nocaps of 9,124) | `match_api.md` (the `DFA_START`/`search_form` value tables, the "which of two forms" paragraph becomes four, the abi history), `tuning.md` (§2.19 generalised to the axis, two deny headings), `cli.md`, `registry.md` | (a) `emit_sweep` default vs parent: the movers equal the census's selected set exactly; (b) the standing gate `run_start_landing.sh` (§7.3); (c) `make test-axes` with both new denies AND the product arm with floors (§7.2); (d) the identity twins re-run on the BUILT rows (`MODE=assert`) against the triple-deny build; (e) the registry checks; (f) the declared listing file `listing_declared_SL2.tsv` (`start_table/listing_diff.py`) and the declared trace file `trace_declared_SL2.txt` (`start_table/trace_experiment.py`) `[r2 SL-C11]`; (g) the derived re-aims and re-runs (§7.4) |
| **SL3** the hand on RECOVER | `CandSel.hand` mandatory on RECOVER asks, as masks; `take` per row; `rev-end`'s ask WINDOW (only if L2.2 has landed; else L2.2 carries it); the path closure keyed (slot, route, hand); the stamp and its readers read the path's cell | none | `start_table.md`-level, no caller-visible change | the self-check's totality over (RECOVER, route, hand mask); its sabotage row (8) |
| **SL4** relay | `inbox_from_pcrec.md`: `dfa_start` gains `end-minus-width` and `landing` (closed-vocabulary event), the abi number, the expected mover cells, and §4.5's bench readers (`selfcheck.py:5871`'s hard gate first) `[r2 SL-C10]` | — | — | — |

### 7.2 The checks the panel asked for

- **The product arm `[r2 SL-C7]`.** `make test-axes` checks answers only. Two arms are
  added with FLOORS (`START-SET`'s precedent): each new deny alone, and the PRODUCT
  `-fno-start-width -fno-start-landing`. The floors are the census's: under
  `-fno-start-width` alone 46 bench / 1,258 corpus compiles go to `landing` (both rows
  apply) and 176 / 1,410 to `reverse-pass`; under the product all 310 / 3,501 SL2
  movers (both configs) reach `reverse-pass`. A single-flag arm never reaches R on the both-apply
  rows, so only the product arm is the independent reference there.
  `run_search_pinned.sh` §10's reverse reference denies all THREE bits: 25 corpus
  `pinned` rows have `W = 0` and fall to `end-minus-width`, not R, under
  `-fno-start-pinned` alone.
- **SL1's hand-witness listing `[r2 SL-C8]`.** `run_facts_checks.sh` gains a table of
  LITERAL expectations, written from the definitions (§2.4, §3.1), never read off a
  walk: `--emit-facts` must print exactly these.

  | pattern | enc | `land_char` | `width` |
  |---|---|---|---|
  | `\w+` | byte | OK | `[1, ∞)` |
  | `ab` | byte | alive-not-accept | `[2, 2]` |
  | `\b\w+` | byte | assert-at-start | `[1, ∞)` |
  | `\w+\b` | byte | assert-after | `[1, ∞)` |
  | `x*y` | byte | alive-not-accept | `[1, ∞)` |
  | `abcd` | byte | alive-not-accept | `[4, 4]` |
  | `a\bb` | byte | (empty engine) | `[2, 2]` |
  | `(?s).+` | byte | OK | `[1, ∞)` |
  | `.` | utf8 | OK | `[1, 4]` |
  | `é` | utf8 | OK | `[2, 2]` |
  | `.{3,8}` | utf8 | alive-not-accept | `[3, 32]` |
  | `[a-zé]+` | utf8 | OK | `[1, ∞)` |

  (The probe reads every row as the table says, which checks this note's derivation;
  the gate checks the BUILT fact against the table.) The count revision 1 gave is
  corrected: 0 of the 2,225 Λ-OK compiles (67 + 67 bench, 1,045 + 1,046 corpus) is
  seeded.
- **The empty arm `[r2 SL-C1]`.** The census arm counts the empties (63 corpus, 44 with
  `W ≥ 0`, 0 bench); `run_start_landing.sh` §1 holds `a\bb` at `reverse-pass` with a
  `return 0` body, and sabotage row 10 drops W0.
- **The dead-group fill `[r2 SL-C3]`.** `run_nomatch_caps.sh` gains `(a){0}\w+`
  (`landing`) beside its three relabelled `end-minus-width` witnesses; sabotage row 11
  plants the fill's omission at the success-site emitter. Both are twinned (§5.5).

### 7.3 The standing gate: `tests/codegen/run_start_landing.sh` `[r2 SL-C5, SL-G1]`

In `run_search_pinned.sh`'s shape (it is that file's sibling, joined to
`make test-codegen`), so the nine rows are no longer guarded only by studies/:
- **§1 hand witnesses**, expectations LITERAL: `abcd` → `end-minus-width`, `\w+` →
  `landing`, utf8 `.` → `landing` with the guard, `\w+` utf8 → `landing` without it (an
  ASCII start set), `a\bb` → `reverse-pass` over `return 0`, `x*y` → `reverse-pass`,
  `a*` → `pinned`; each also under the three denies;
- **§2 stamp ⇔ body ⇔ mirror** over the corpus: `landing` ⇔ the record present and no
  reverse machine; `end-minus-width` ⇔ `e − W` and no reverse machine; `reverse-pass` ⇔
  the reverse machine; the `rx_info` mirror equal to the macro;
- **§3 floors**, from the census (`landing` ≥ 416, `end-minus-width` ≥ 1,334 in the
  default corpus config; a fall below is a red naming the count, never an empty loop);
- **§4 deny identity**: a declined artifact is byte-identical under each deny; the
  product arm's artifacts carry R;
- **§5 every-startpos sweeps** of the built rows against the triple-deny build, on the
  hand witnesses and on the ill-formed pool's tokens (§5.5);
- **§6 a corpus `.rxt`**, `tests/utf8/landing_illformed.rxt`, oracle-verified against
  libpcre2 10.46 (`PCRE2_UTF|PCRE2_MATCH_INVALID_UTF`): `.` and `\p{L}+` on `C3 61`,
  `C3 C3 A9`, `E2 82 61`, `F0 9F 98 61`, `ED A0 80 61`, `C0 80 61`, at every startpos;
- **§H the hostile cell**: utf8 `.` and `\p{L}+`, find-all over 1 MiB of `C3` then `a`
  (and the `E2`, `F0` runs), each under `$TIMEOUT_BIN 10`, the answer checked (one match
  `(1048576, 1048577)`). The bound is CHOSEN with three orders of margin each way: the
  linear forms take 2-6 ms here (ASan-instrumented, under 100 ms by a 10-20× factor),
  the quadratic form ~13 min. Sabotage row 12 plants revision 1's re-entry and the bound
  fires.

**The nine rows' reach, fixed per row** (§7.5 lists the table).

### 7.4 The derived edit set, re-aims and re-runs `[r2 SL-C2, SL-C4]`

**Anchor re-aims** (`results/sabotage_anchors_sl.tsv`, `sabotage_anchors.py . CALL_GRAPH
studies/start_landing/edit_set.tsv --final after-SL3 --edit-names` at `efc58146`): 596
row files, 614 sites, 116 in the start family. **3 RE-AIM at SL2**: S221 (its anchor is
`pinned`'s `caps[0]` line, which moves into the success-site emitter), S223 (the
`start_pinned_assert_routing` line, which becomes the per-action assertion), S693 (the
abi literal). **RE-RUN**: 21 sites at SL2, 5 at SL3 (S222, S82, S235, S07, S566 by
`calls-rewritten`/edit-set), 92 once after SL3. The 3 pre-existing unresolved `src/`
sites (S176, S571, S640) are outside the family, as at L0. Revision 1's "S218-S222 are
re-anchored" is withdrawn: the derivation finds no anchor text of S218, S219, S220 or
S222 that SL1-SL3 rewrite.

**Reach re-aims** (`witness_movers.py` ∩ the readers): a row's witness moves AND its
reach or its check reads the reverse machine. Of the 112 moving witnesses, these:
- **S218** (`$`, reach greps `RX_DFA_START "reverse-pass"`) and **S220** (`(?!a)`, and
  its population manifest `s220_view_decliners.txt`, where `\B`, `\B\B`, `(?![^a])`,
  `(?!a)` all have `W = 0`): both compile under `-fno-start-width`, which restores the
  fallback chain to `pinned` → `reverse-pass`, so P1/P2's decline is again what the
  witness shows. Intents unchanged.
- **S227** (`foo\B`, reach greps `rx_reverse_seed_state` and the reverse scan-edge
  entry): `W = 3` sends it to `end-minus-width` and its reverse machine leaves;
  `-fno-start-width` restores it. This is also the default population for scan-edge
  precondition (8) on seeded reverse heads, which `run_scan_edge_census.sh`'s four
  `\B`/`\b` `r=1` rows and its `[0-9]{3}\z` VEDGE row (`2 1 1`) carry; they compile
  under `-fno-start-width` too.
- **S219** (`\bx*`, `\ba|c*`): not movers (nullable, unseeded-accept declines), so no
  re-aim.
- The other moving sabotage witnesses (77 row files move in all) (S15/S16/S20 `\d`, S237/S238 `\p{L}`, the
  findings rows' `abc`, the UCP and context-node rows, ...) plant sites that are not on
  the reverse path (the parser, the facts, the prefilter, the VM): their RECOVER moves
  and their planted site does not. Each still re-runs at SL2 by `sabotage_anchors.py`'s
  `rerun_at` where its owner is in the family; the rest re-run after SL3.

**Unparsed witnesses, counted.** `witness_movers.py` could not read 34 files' run-time
pattern lists (e.g. `run_search_pinned.sh` 5/5, `run_nomatch_caps.sh` 1/1,
`run_scan_edge_census.sh` 4/4, `run_codegen_tests.sh` 26/61); the three gates the panel
named among them were probed by hand (`results/hand_witnesses.tsv`, marked as
hand-extracted). The build lane re-derives at its own pin and runs the gates
themselves, which see everything.

### 7.5 Sabotage: the rows and their reach `[r2 SL-C5]`

| row | planted fault | witness / detector | reach |
|---|---|---|---|
| 1 | Λ widened (alive-not-accept read as accept) | `xa\|a`, `ab` on "aab" (§5.3: 55,152 wrong) | reached |
| 2 | Λ's assertion test passed rather than declined | `a\b` under `-fno-start-width` on "aa" (§5.3: 64,200 call differences); revision 1 had only equivalent mutants (`\w+\b`, `\b\w+`) | reached (constructed) |
| 3 | ~~Λ.2 dropped~~ | DROPPED: Λ.2 is K50-NULLGATE's checked invariant (§2.4); its own rows (S236, S303) plant that check | — |
| 4 | the record omitted from one NEXT form (at `pf_close`) | one witness per reachable form: `byte-class` `\w+`, `byte-class-bounded` (census: 28 rows), `memchr` `f\|frank`, `memchr-bounded` `(?:ab$\|a)`, `offset-set` utf8 `é+`, `offset-set-bounded` utf8 `é(?:x$)?` (constructed, twinned); `first-memchr-bounded` and `first-class-bounded` DECLARED UNREACHED: both are seeded-machine-only rows (the START-SET DFA hat), and Λ ⇒ unseeded (0 of 2,225) | 6 of 8 forms reached; 2 unreachable by an argument |
| 5 | the guard dropped | utf8 `.` on `C3 61`, and the extended pool (§5.5) | reached |
| 6 | the width in characters | utf8 `é` (W = 2 bytes, 1 character) | reached |
| 7 | the width off by one | `abcd` | reached |
| 8 | the RECOVER hand filter dropped | an end-pinned fixed-width pattern on a non-matching tail | UNREACHED until L2.2 (declared; becomes reachable with the first WINDOW asker) |
| 9 | the dispatch emits one action while the stamp names another (stamp ⇔ body on the NEW values) | `run_start_landing.sh` §2 on `\w+` (`landing`) and `abcd` (`end-minus-width`). NOT S222's duplicate: S222 forks the stamp FUNCTION from the selection and is witnessed by `(?m)a*$`, a `reverse-pass` row neither new action touches; row 9 plants a dispatch arm, where S222's witness cannot see it | reached |
| 10 | `recover_on_path` (W0/L0′) dropped | `a\bb`: the stamp would read `end-minus-width` over `return 0` | reached |
| 11 | the K78 fill omitted at the success-site emitter | `run_nomatch_caps.sh`: `(a){0}(b){0}c\|d`, `(a){0}\w+` | reached |
| 12 | the guard re-enters the scan (revision 1's restart) | §H's 10 s bound on 1 MiB of `C3` then `a` | reached |
| 13 | the stamp reads a hand-less ask (SL-C6) | an L2.2 artifact with `rev-end` and `W ≥ 0` | UNREACHED until L2.2 (declared) |

Ids are the manager's allocation at build (none taken here: the kit reserves ranges).

**Where to attack §7.**
- (a) SL2's movers are "the census's selected set": the census reads the PROTOTYPE's
  facts, so SL1's agreement check and the hand-witness listing are what make that a
  control and not an echo.
- (b) The twins re-run on the built rows. Against what? The triple-deny build's
  independently built reverse machine, not the twin transformer.
- (c) Mover byte counts against `--max-emit-bytes` rungs: a mover that drops R may
  now FIT a rung it did not, which is a fit mover (a different machine set chosen),
  not only a byte mover. `run_resource_tests.sh`'s five moving witnesses are where.

---

## 8. Standing questions (`docs/design/CLAUDE.md`)

### 8.1 The measurement regime — RELEVANT

- **Compile-side, regime-free:** the census and coverage numbers (the prototype's
  facts over walk_survey's populations); the derived edit set and readers.
- **Correctness, regime-free:** the identity sweeps; `decode_eq.py`.
- **Timing (§5.4, §5.6), scratch tier:**
  - throughput regime (a dense find-all over the bench's own 1 MiB subjects) and the
    hostile regime (a find-all over a lead run, one or two calls per subject);
  - independent calls (stateless re-entry);
  - Linux 7700X, gcc 15.2, glibc;
  - a LOADED box (load1 8-13), stated per run with σ and the 2(σa+σb) test.
- **Weights (§6):** walk_survey's older-pin Ryzen 1600 medians, so a ranking, not a
  prediction.

Could another regime flip a decision?
- A short-subject `search` regime shrinks the walk (the reverse pass is bounded by
  the match).
- The rows never add work on well-formed text: the record is one store per landing,
  the skip one decode per reported match. On ill-formed text the skip adds at most one
  decode per ill-formed byte of the final excursion, never a re-scan; today's reverse
  pass is cheaper there (it walks back one byte), which no bench cell measures.
- The guard pick (§2.5.5) would flip only in a regime dominated by ill-formed input,
  where Fix A wins some cells. None is on the bench; the hostile cell guards linearity,
  not the pick.
- The ordering decision (`end-minus-width` before `landing`) rests on dominance, not
  on a timing.

### 8.2 The independent control — RELEVANT

- **The fact's selection** (the probe) is checked against ANSWERS: the twin is built
  from today's artifact text, not from the emitter, and is compared with the
  artifact's own reverse pass per call and with libpcre2 per cell. Neither the
  probe's predicate nor the twin's form shares a source with the reverse machine.
- **The decode** is shared by twin and build (the seam's text); `decode_eq.py`'s
  Table 3-7 spelling is the control that does not share it.
- **The controls (§5.3, §5.5)** show the harness sees a wrong landing, a missing guard
  (on class-own truncations, after two pool defects this lane found in itself), a
  passed assertion and a wrong width.
- **The population is counted by walk_survey's** `pop_bench.py` / `pop_corpus.py`
  (K35: who counts is named) and joined on `(pid, config)` with its committed cells.
- **The readers are derived** (§4.5) by three methods that share no source: the
  edit-set anchors, a token grep over both trees, and the witnesses through the probe;
  their one hand input (the token file) is named.
- **After the build:** the deny chain ends at an independently built machine, the
  product arm reaches it where both rows apply, and `run_start_landing.sh` is the
  shipped control.
- **[MECH-REACH]:** §7.5 names each row's witness and the two declared-unreached ones'
  arguments.

### 8.3 What moves when data is regenerated — RELEVANT, little

- No calibration, prior or data file is read. Λ and `[bmin, bmax]` are per-compile NFA
  facts.
- What moves on regeneration of the PATTERN (SL2's abi event): `RX_DFA_START` and
  `search_form` values, the member-folded machine stamps, the reverse tables and
  accessor block (removed), the orientation comment, the NEXT block's one statement,
  the guard where emitted, and artifact byte counts (down).
- The study's results move with the tree; nothing reads them. `readers.tsv` and
  `witness_movers.tsv` are re-derived at the build's pin.
- A spec change (§7 SL2).

### 8.4 Constants `[r2 SL-G8]`

- **No tuning constant reaches the artifact.** The rows read two facts and emit
  arithmetic or a store; the guard's condition reads two seam fields. There is no
  threshold, width cap or cut-over in the emitted code.
- **Encoding literals:** none remain in the design (SL-G2); the seam's `start_cls`,
  `onebyte_max` and `$_decode` carry them, owned by `src/enc/`.
- **Trigger thresholds, CHOSEN (not measured knees):** `[START-LANDING-EXC]`'s 1 ms
  bench cell (§2.8) and `rev-end-width`'s 10% of a cell (§3.3) rank filed rows; neither
  gates a build.
- **The standing cell's wall bound, CHOSEN:** 10 s, with three orders of margin each
  way from MEASURED values (2-6 ms linear, ~13 min quadratic at 1 MiB).
- **Instrument caps (the study's, never the artifact's):** the probe's width walk stops
  at depth `LP_MAXW` = 4096 (a width above it reads "not fixed": `a{65535}` does) and Λ's
  walk at 200,000 steps; the pool cap 40,000 subjects (12,000 on the corpus); subjects
  over 512 bytes sampled at 64 positions plus the last 8; timing 3 × 7 and 5 × 9 runs;
  the twin driver's 900 s per pool and the timing's 60 s per binary.

---

## 9. Questions for Frank (discussion, each with a leaning and the critics' judgments) `[r2 SL-G7]`

**Q1. The fact: one character now, the excursion condition filed?**
- *Problem:* the exact condition (§2.3) is a product walk over the emitted machine;
  the one-character fact is an NFA walk.
- *Forces:* the general form is the house preference (memory
  `pcrec-general-mechanisms-not-special-cases`); its measured extra reach is ≤ 0.58 ms
  of 54.6 (§2.8); it is a different layer's analysis (minimized state ids); under
  tolerant utf8 it needs a whole-span validity walk.
- *What revision 2 adds:* the one character is not a stopping point chosen for
  convenience; it is the largest k for which an NFA-only criterion is sound (§2.3.1).
  So "build Λ, file the excursion" is not a special case of the general form waiting to
  be replaced: it is the general form's NFA-layer projection, and the excursion
  condition is a different layer's fact.
- *Critics:* slcrit3 (SL-G6): "Λ's one character is DERIVED, not chosen"; slcrit1
  upheld Λ's sufficiency on 265 new twinned shapes, 0 differences.
- *Leaning:* build Λ; keep `[START-LANDING-EXC]` filed with its 1 ms trigger.

**Q2. The tolerant-utf8 guard: which form, and is a guard right at all?**
- *Problem:* without a guard, `landing` under utf8 is limited to `-futf-check`
  artifacts, and the bench does not compile with `-futf-check`, so the two largest
  cells (utf8 `.`, `\p{L}+`, ~10 ms of weight) would be lost.
- *Forces:* revision 1's restart was quadratic on attacker-controlled bytes (13 min per
  MiB) — the panel's headline finding, and invisible to every check revision 1 ran.
  Two linear forms are exact. The skip puts nothing on the hot path and re-enters
  nothing; Fix A changes every NEXT emitter's block and pays one decode per landing.
- *Measured:* the skip −31%/−39% against today on the bench's text, Fix A −22%/−28%;
  both linear on hostile input (1.8-5.3 ms per MiB); a standing 10 s cell guards it.
- *Critics:* slcrit3 (SL-G1/SL-G7 Q2): "the guard, in the skip form"; slcrit1 (SL-E1)
  built Fix A and measured it linear and ~6% behind the post-loop form on `.`.
- *Leaning:* the skip, with Fix A recorded and the hostile cell standing.

**Q3. RECOVER asks carry a hand.**
- *Problem:* `rev-end`'s walk asks RECOVER at a SPECULATIVE end; taking the
  composite's rows there is a wrong answer (§3.3).
- *Forces:* the hand is FINISH's existing filter on one more slot, now spelled in the
  product's masks (EXISTS vs WINDOW), which gives §7.5's filed EXISTS mask its first
  producer and keeps one vocabulary across the composite and the LOCATE → FINISH
  boundary. The alternatives are a `rev-end` clause in three predicates (a special
  case) or `rev-end` not asking RECOVER (its `RX_DFA_START` would then need its own
  spelling, LR-G4's problem). The stamp must follow the path's ask (SL-C6).
- *Critics:* slcrit3 (SL-G4/SL-G7 Q3): "the hand, in SL-G4's vocabulary"; slcrit2
  (SL-C6): the hand rides the closure key, and L2.2 must name it.
- *Leaning:* the hand as masks, built by whichever of `[START-LANDING]` and L2.2 lands
  second; `locate_finish.md` L2.2 carries a note saying so.

**Q4. `end-minus-width` before `landing`.**
- *Forces:* information order says "how much evidence", which puts `landing` (one
  character) before an end subtraction. Cost is equal (measured). The two answer
  identically where both apply, and `end-minus-width` needs strictly less (no record,
  no NEXT ask, no guard, no unseeded machine).
- *Critics:* slcrit3 (SL-G7 Q4): "emw first by DOMINANCE (identical answers on the
  overlap, strictly smaller `.needs`), not by timing"; slcrit1 forced `landing` first on
  the 66 both-apply bench rows: 7.89 M cells, 0 differences (the order is answer-free);
  slcrit2 (SL-C7): the order means a single-flag deny never reaches R on the overlap,
  hence the product arm.
- *Leaning:* `end-minus-width` second, by dominance; the survey's and LR-G10's order
  is the other defensible reading, and no answer depends on it.

**Q5. Filing `rev-end-width`** (§3.3, §11 U3) on REVEND's side: an end-pinned
fixed-width pattern needs one anchored run of `W` bytes, not a walk.
- *Critics:* slcrit3 (SL-G7 Q5): "file rev-end-width and label its 10% threshold".
- *Leaning:* file with its trigger, the 10% labelled CHOSEN; 6 bench patterns.

---

## 10. The lenses

**The RECOVER grid `[r2 SL-G5]`.** RECOVER's rows are not a ranked list of four; they
are cells of a 2×3 grid, by WHERE the evidence about the start comes from and HOW MUCH
of it there is:

| | no evidence | bounded evidence | unbounded evidence |
|---|---|---|---|
| **start side** (what the forward scan recorded) | `pinned`: the start state accepts, start = `search_from` | `landing`: one character, start = the last landing | the excursion condition (`[START-LANDING-EXC]`, FILED); `candidate-verify` (`locate_finish.md` §7.6) |
| **end side** (what the end implies) | — (an end alone fixes no start) | `end-minus-width`: `W` bytes, start = `e − W` | `reverse-pass`: a walk back from `e` |

`pinned` and `landing` are one ACTION ("start = the start-side record", the record being
`search_from` or `landing_position`), but they stay two rows: `pinned` keeps its stamp
value, its deny and its own population, which must not move. The listing descs name the
cell (§4.1).

| lens | reading |
|---|---|
| specific vs general | two cells of the RECOVER grid, and one general mechanism (the hand, in the product's masks) applied to one more slot. The excursion condition is the general fact; Λ is its NFA-layer projection, and the one character is derived (§2.3.1) |
| core vs derived | both facts are derived from the NFA the machines are built from, by one frontier iterator and its closure step; nothing new is stored |
| applicable vs assumption-changing | applicable: identity with today's reverse pass, so no answer, attempt or give-up moves. Precondition P0 (self-synchronization) is stated, and a backend without it declines |
| fits the architecture vs refactor | fits L0's `.needs`/member fold and FINISH's hand filter; the one refactor is `u.recover.pinned` → `act`, which the third and fourth rows force, plus one success-site emitter that makes the K78 obligation structural |
| D124 shared question / engine hat | RECOVER is asked only by the DFA hat (`CR_DFA`), on DFA artifacts and on the hybrid's inlined body alike; the ATTEMPT hat's candidate is its start, and the VM hat has no RECOVER |
| forest for the trees | the RECOVER family is the grid above plus filed siblings: `candidate-verify` (§7.6), `rev-end-width` (§3.3), the excursion condition (§2.8) and LR-G14 (§4.2). The width interval is the fifth member of a width family (§3.1) whose units differ; a sixth member is a consumer of the iterator, not a walk |

---

## 11. Candidates, filed with triggers (not designed beyond the trigger) `[r2 SL-G9]`

The manager files these into `../dev/plan.md`; this note does not edit it.

- **U1 — FIXED-MARGIN CAPTURES, a note on `[CAP-EARLY-STOP]` and D142.** Where every
  capture group's boundaries sit at fixed BYTE offsets from the match start or end on
  every path (`"([^"]*)"`, `<(\w+)>`, `(\d{4})-(\d{2})-(\d{2})`), an EXACT hybrid knows
  the captures by arithmetic once it has the span: `report` writes them with no VM run.
  It is `[CAP-EARLY-STOP]`'s degenerate case (the walk stops before it starts) and a
  member of D142's family (what a successful prefilter proves to the VM). The fact is a
  per-group byte-offset interval from both ends, the same frontier iterator walked to
  each group boundary. **Trigger:** D142's (a match-dense bench cell where a hybrid's VM
  share is ≥ 10% of time on Linux), RESTRICTED to cells whose pattern is all
  fixed-margin, counted by a census of such patterns first.
- **U2 — the byte max width for `[OPT-ENDWIN-ENC]`.** The end window declines under a
  multibyte encoding (`decline:enc-multibyte`) because its W is in characters; `bmax`
  (§3.1) is the byte bound W1 needs there. Population at this pin: 32 end-pinned
  multibyte declines in `studies/locate_finish`'s rows (4 bench), 22 of them with a
  finite character width (locate_finish C3's declared exception). **Trigger:**
  `[OPT-ENDWIN-ENC]`'s own (a cell where the end window is material, the utf8@0.1
  re-read), now with its missing fact named.
- **U3 — `rev-end-width`** (§3.3), on REVEND's side: trigger as stated there.
- **U4 — `candidate-verify`** (`locate_finish.md` §7.6) reuses SL2's record site, and the
  skip (§2.5.2) is its DECODE-verifier instance: a candidate that does not decode is
  stepped past without a verifier run. As filed there.
- **The excursion condition** `[START-LANDING-EXC]` (§2.8): as filed.

No material unlock for the VM hat, ATTEMPT, or `[FINDALL-REENTRY]` (slcrit3).
