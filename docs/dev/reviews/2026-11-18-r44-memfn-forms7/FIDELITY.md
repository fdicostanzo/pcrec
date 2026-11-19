# CRITIC FIDELITY: memfn-forms7

## Findings

### FIDELITY-1 (CONFIRMED; doc + design; effort S; blast: every pool, the dry run's "four phase classes" claim)
The stratification claim holds for the PRELUDE j, not for the hot loops it is meant to move. cards.py:142 says
"function entries stay 16-B aligned so the prelude still moves their phase"; FALSE as built: every odd variant
puts `rxa_search` off the 16-B grid (hex24/h8/off: v1 @0x1f89, v3 @0x2099; hex24/h0: 0x1e49, 0x1719; lit16/aa/off:
0x1629, 0x20b9; uuid36/I: 0x2549, 0x2299). r45_reply:81 "stratified so the four variants take the four 16-B phase
classes mod 64" and cards.py:154 "a pool of 4 spans the four 16-B phases mod 64 by construction" are true of j only.
Per hot loop, AS BUILT (kit pool.py, 16 pools, nm/objdump): the two EVEN variants (gcc's default alignment, the
relative layout a user's gcc -O2 build gets) differ by exactly 16 mod 64 (whole-TU shift, holds for every loop of
every pool), so the shipped relative layout is timed at TWO of the four 64-B classes per loop (hex24/h8/off: loops at
32,32 and 48,48; classes 0 and 16 never timed in that layout); the odd pair is a DIFFERENT relative layout
(rel 48/304 -> 44/286) at off-grid phases (53,39 / 5,55). The "each alignment's two variants differ by 16 B mod 32"
half HOLDS for every loop in every pool built (main excepted, below). Repro: `kit/pool.py RD hex24 h8 off`; compare
v0/v2 p64 and the odd search@ addresses. Fix: reword both claims to what is built (2 phases per relative layout,
16 apart; odd entries unaligned), or stratify the even pair over 4 classes with POOL_SIZE 8 if 64-B coverage of the
shipped layout is wanted (a measured need first).

### FIDELITY-2 (CONFIRMED fixed / SUSPECTED effect; design (speed); effort M; blast: every comparison, SIMD-on layer most)
What NO pool moves: (1) the subject buffer: DRIVER mallocs n+1 = 1 MiB+1 (mmap path) and calloc's the 32 MiB
eviction buffer; both land at 16 mod 4096 on EVERY launch of EVERY arm (probe fidelity/probe/m.c: "16 16 16 evict 16"
x3 runs; glibc's mmapped-chunk header). Every 32-B AVX2 load the "on" layer issues at s+32i is 16 B off a 32-B
boundary, every second one splits a cache line, identically in I, every head, aa, and the confirm. (2) .rodata: the
matcher's table `rxa_mf1_sh` sits at 0x31c0 in all 4 variants (and in hex24 I, h8, I/on alike); data never moves.
(3) `main` (gcc puts it in .text.startup, ahead of the prelude): at 0x1200 in every variant of every pool (cards.py:137
"the artifact's functions and its driver move" is half true: `fa`/`call` move, `main` does not; main's loop is not the
per-byte hot path, so this one is doc only). (4) libc `memchr` (the short-subject record splitter, regime 1).
Consequence: head vs I is read at ONE subject phase (16 mod 64); a head whose loop gains or loses at that phase
(alignment-sensitive vector loads, the span loop's window vs the scan's) wins a cell that a user's arbitrarily aligned
subject would not show, and no estimator sees it (every A/A and hash-equal contrast holds the same phase). R2 A covers
"a layout share common to every variant of a text ... which is what ships"; a fixed SUBJECT phase is not shipped.
Fix (general form): draw the subject offset per launch too (pass an offset argument, `s = buf + off`, off drawn
like the variant and recorded), or record it as a named fixed axis in `rule`'s output. Trigger: any SIMD-on win.

### FIDELITY-3 (CONFIRMED; design + doc; effort S (doc) / M (fresh pool for the confirm); blast: the confirm predicate, step (4))
The confirm re-times STEP 1'S EXES. `pool_variants(textkey)` (cards.py:168) hashes the TEXT only ("one text, one
pool, every night", :170): no run id, no results file. `confirm_cells` -> `time_cells` -> `prepare_cell` ->
`build_cell` returns the SAME cached files `RUNDIR/bin/x_<key>_v<v>_<vk>` the night timed (traced: the exe name is
key + v + prelude/flags only). Only the per-launch DRAW is salted by the results file (:802). So a text's finite
pool-mean offset (text_var's `sL2 / POOL_SIZE` term, :1494, which the design itself calls "the pool's own draw, not
the text's speed") is the SAME in the night and the confirm: it replicates by construction, exactly rev 11's K1
mechanism ("an exe's offset replicated because the confirm re-ran the same exes", r45_reply:873) at a quarter of
the variance. The text still says the opposite: r45_reply:880 "never step 1's exes, so an offset an exe carries
cannot replicate" (left unstruck inside the rev-12 bracket) and cards.py:1864 "a layout draw cannot replicate except
by chance" (a draw does not; the 4-exe pool mean does, and with 5 draws from 4 variants most of the median does too).
The same holds across NIGHTS on one build (a repeat night re-times identical pools), so a second night is not an
independent layout sample either. The synth drill models this faithfully (synth_rows' store is held over the
confirm, :2205-2207), so the drill numbers include it; the defect is that the confirm is no longer a control for the
exe level at all and nothing says so: that level rests on `layout_text_term` alone, estimated per head text from its
own <= 6 rows and floored at 0 (:1468). Fix: state it (strike :880's clause, reword :1864), or salt the pool by run id
+ results file (a fresh pool for the confirm = 4 more compiles per confirmed arm; restores the K1 guarantee).

### FIDELITY-4 (CONFIRMED; maintenance (a hole in L6's guard); effort S; blast: a re-used RUNDIR)
The run id is the RUNDIR's, not the night's. `run_id` (cards.py:1064) is "never renewed"; `cmd_run` (:1000-1004)
refuses only while a `results*.tsv` exists. Plant (fidelity/plant/p1.py, constructed RUNDIR, no timing): night 1
records `--g2` {16}; the operator removes results.tsv (the one thing the refusal names) and runs again: the guard sees
nothing, `run_id` returns the SAME id ("renewed? False"), `night_g2` without `--g2` silently returns night 1's {16}
("recorded in rule_g2.json"), passing the NEW build's G2 list is refused ("one list a night"), and every arm's layout
draw sequence repeats exactly (C1/hex24/h8/hit-dense/off: [2,0,3,0,2] both nights). L6's stated purpose (r45_reply
rev 12 L6: "a record of another run (a reused RUNDIR) ... REFUSES") is met only when a results file survives. Fix:
`run` writes a fresh run id (and removes or refuses a `rule_g2.json` keyed to another id) at the moment it creates
results.tsv, or refuses any RUNDIR holding `run_id` + `same_as_I.json` from an earlier `run`.

### FIDELITY-5 (estimator behaviour CONFIRMED; physical premise SUSPECTED; speed/design; effort M; blast: R2 B's term, R2 C's test, the drills)
`text_effects` (cards.py:1429) fits ONE effect per variant over every regime of a text ("row level + variant
effect"), and the drill's layout model is the same shape (`synth_layout_effect`, :2159: a function of (body, phase),
no regime). Physically a variant is one exe whose hot loops ALL move: a text has several (hex24/h8: 2 loops rel
48/304; alt49/I: 9; uuid36/I: 16, kit pool.py), and the regimes spend their time in different ones (hit-dense vs
miss-heavy), so a 16-B shift can speed one regime and slow another: a variant x regime effect, which the fit averages
toward zero. Constructed drill (fidelity/plant/p3.py: 4 read regimes x 5 launches over 4 variants, 1 % launch noise,
2,000 texts each, text_effects as analyse calls it): variant-only effects read back at ratio 1.03/1.00/0.98 of the
true variance (tau 1/2/3 %); variant x regime effects of the SAME per-regime size read 0.42/0.35/0.32, and sL2 = 0
for 36/25/24 % of texts. So the per-text term (R2 B) under-floors a head whose layout sensitivity is regime-specific
by about 3x in variance, and `adjusted` (R2 C) removes the wrong per-variant effect from each row. Neither the
selftest (regime-free model) nor any control can see it. Confirm: time one multi-loop text's pool (uuid36 or alt49 at
I) in two regimes on a quiet box and compare the per-variant effects' correlation across regimes; fix (if it binds):
fit effects per (text, regime) (df permitting) or add a regime-interaction model to the drill.

### FIDELITY-6 (CONFIRMED; maintenance (a check that cannot fail on its own regression); effort S; blast: `dry`'s pool refusal)
The refusal can pass a pool that keeps every hot loop's 32-B phase fixed within each relative layout, i.e. the very
defect rev 12's PHASE_ORDER was introduced to fix (cards.py:155-157: "with (r + v) mod 4 they differed by 32 B, so
... kept every hot loop's 32-B phase in 18 of 80 pools"). `pool_proof` computes the 32-B phases (:616) but
`pool_refusal` (:620) reads only "one 64-B phase vector" and "one relative layout", and the odd alignment variant
always supplies a second relative layout. Plant (fidelity/plant/p4.py; real exes, `PHASE_ORDER = (0, 1, 2, 3)`
restored after import): hex24/h8/off v0 p32 (0,0) = v2 (0,0), v1 (5,23) = v3 (5,23); hex24/I/off v0 = v2 = 16,
v1 = v3 = 20: "each alignment pair keeps every loop's 32-B phase: True | refusal: None" for both. So in the
SHIPPED relative layout (the even pair) every 32-B (uop-cache window) phase is a constant of the text and the dry
run reads green. cards.py:154 "(the refusal is the check)" is false for both stratification claims (four 64-B classes;
16 B apart mod 32). The selftest's refusal rows (:2589-2603) plant only "one 64-B phase" and "one relative layout",
so no control covers the 32-B half (r41 L4's "one control a half" is met for the halves coded, not the halves
claimed). Fix: add the clause "within each relative layout, the variants' per-loop 32-B phase vectors differ"
(refuse otherwise) and a selftest row planting PHASE_ORDER (0,1,2,3)'s shape; consider the same per-layout reading
for the 64-B half.

### FIDELITY-7 (code difference CONFIRMED; timing effect SUSPECTED; design (speed); effort S to record, M to change; blast: every median)
Half of every pool times a body that never ships, and the rule reads the mix as the text's speed. The odd variants
compile with `-fno-align-functions -fno-align-loops -fno-align-jumps -fno-align-labels -mtune-ctrl=^align_tight_loops`
(cards.py:164): different code, not a moved copy (hex24/h8/off rel 48/304 -> 44/286, I's loop 48 -> 43, h0's four
loops 48/67/85/112 -> 44/63/81/94; `rxa_search` grows/shrinks: .text 0x1458 vs 0x160c). A user's `gcc -O2` (and the
bench's default testees) ship the EVEN body. An alignment-flag effect COMMON to both odd variants (a tight loop that
loses its 32-B alignment pays every iteration; I's one-loop scan may not) moves the head's median by up to half that
effect whichever way, and R2 A's premise ("a layout share common to every variant of a text is a property of that
BODY's own internal layout, which is what ships") does not hold for a share common to the odd pair. The drill's
"phase" model (:2159) draws 4 iid phase effects and has no alignment-pair effect, so no drill row covers it. The
kit's own sibling decided the other way: docs/design/memfn/span_cards/slot/link.py:42 "The cells time the declared
target's DEFAULT code (no alignment flag)". Cheap unlock: the `variants` column already lets `rule` print, per text,
the even-pair vs odd-pair contrast (and its effect on any win: re-read each win on even draws only); trigger to change
the pool: that contrast exceeding the floor for any winning head.

### FIDELITY-8 (design: family + general form; no defect by itself)
SIBLINGS (the same mechanism, built five times, each with its own constants and checks): docs/dev/optloop/k87twin_align.sh
and rewtwin/timing_pad.py (`.skip PAD` + -falign-functions=64, fixed pads), studies/artrev/timing.py (`--pads
16,32,48,64`, PAIRED pads orig@pK vs X@pK with a sign-agreement rule), docs/design/memfn/span_cards/slot/link.py
(per-launch pad draw P = 16 x (1 + draw mod 255) with a bounded re-draw so arm and twin differ mod 64 in EVERY launch,
read at the object's own .text alignment, default code only), pcrec-bench's `pcrec-auto-align64` testee (one fixed
placement) and cards.py rev 12's pools. They disagree on: pairing (artrev, link.py pair the arms per launch; cards.py
draws each arm independently), the alignment axis (FIDELITY-7), whether coverage is checked per launch (link.py) or per
pool (cards.py, and then not the claimed classes: FIDELITY-1/6).
GENERAL FORM: layout is a declared, recorded RANDOM FACTOR of every timed object: (text, layout draw), the draw space
declared as axes {code offset mod 64/4096 (in-TU prelude), alignment policy, data/subject offset, (later) link order,
env/stack offset}, each draw recorded per launch, coverage proved per axis against the CLAIMED stratification, and the
estimator told which axes ship (fixed, part of the body) and which do not (randomized, noise).
UNLOCKS with triggers: (1) one shared layout-draw module (draw, record, coverage proof) for cards.py, slot/link.py and
artrev/timing.py: trigger = the next harness that needs layout control or any of the three changing its draw.
(2) the subject-offset axis (FIDELITY-2): trigger = any SIMD-on win, or a bench report naming subject alignment.
(3) PAIRED draws (head and I drawn the same prelude class per round, artrev's design): trigger = the power rows staying
below accept at layout tau 1 % (r45_reply:128: 192 and 184 of 300 vs 270/255), if a measurement shows phase effects
correlated across texts. (4) the per-axis contrast printed by `rule` (even vs odd, FIDELITY-7): trigger = none needed,
the record already holds it.

### FIDELITY-9 (CONFIRMED by reading; maintenance; effort S; blast: a RUNDIR rebuilt under another compiler)
The variant cache name omits the compiler: `build_cell` (cards.py:540) names the exe `x_<key>_v<v>_<vk>`,
vk = _h(key, prelude, flags); `CC` (env, :84), the gcc version and `-O2 -std=gnu11` are in neither key nor vk, so a
RUNDIR whose `dry` ran under one compiler re-times those exes under another `CC=` with no rebuild and no line saying
so (the r41 L7 rule "a changed draw space is a new name" covers the draw, not the toolchain). Fix: hash `CC` and
`$CC --version` into vk.

## PROBED-AND-HELD

- (b) end-to-end trace, one cell (C1/hex24/h8/hit-dense/off): `launch_variant` -> `argv[c][v]` (prepare_cell's
  list, built v = 0..3 in order and every entry gated first) -> `drawn[c].append(v)` only after that launch's float
  parsed -> `row_line(..., variants=drawn[c])` -> `read_rows` (f[10]) -> `text_effects`/`adjusted` zip launches with
  variants. Timed = gated = recorded = read, by construction; a failed launch voids the row without a partial variants
  list. HELD.
- Hash-equal arms share I's pool: hex24 I = h64 (key ec49acbb...), uuid36 I = h8, alt49 I = h8: same key, same 4 exe
  files; `text_of` groups them as ("I", pat, ly) from same_as_I.json, which hashes the same artifact bytes the pool
  key hashes. HELD (3 patterns).
- A/A: aa.b compiles aa's flags (one key, one pool); draws independent of aa's (12 A/A cells: same-draw rounds
  {0:1, 1:8, 3:3} of 5). HELD.
- Draws: 1,182 step-1 arm cells x 5: variant counts 1479/1537/1497/1397 (uniform); distinct variants per arm cell
  {1:5, 2:186, 3:679, 4:312}, which `varmed5`'s uniform-iid model matches. HELD (as modelled).
- Salt: night/re-run/confirm/C3 files each salt the draw (basename); confirm rows keyed (file, cell) in the fit. HELD.
- j stratification: 20,000 text keys, 0 violate "four classes mod 4, each alignment pair 1 class apart". HELD (j).
- Within-alignment 16-B shift: every loop of every one of 16 real pools moves by exactly 16 mod 64 between the two
  variants of one alignment (whole-TU shift). HELD.
- Cold partitions: no `.cold`/`.part`/`.isra` symbols in 13 texts (a hot loop gcc moved out of .text would escape the
  prelude and the proof). HELD today; unguarded.
- rxa_search calls nothing (no call/jmp out) in 4 texts checked: the proof's "rxa_search's backward branches" are the
  matcher's hot loops. HELD.
- Pool parameter collision: 7 of 20,000 keys repeat a prelude vector; exe names carry the key, no file collision. HELD.
- Answer gate: lit16/aa/off hit-dense gated on all 4 variants (prepare_cell). HELD.
- Exes built: 56 (14 pools) + 8 (plant p4). No timing, no make, no commits.

CRITIC COMPLETE
