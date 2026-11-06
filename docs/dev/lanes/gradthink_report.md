# gradthink report: with feature families, is D37's graduation rule still needed? (lane gradthink, sonnet, 2026-11-06)

Thought lane, read-only analysis; no build, nothing run (the box lock is the kit's). Only this file and the
history-index line are written. Labels: READ = taken from a file this lane opened; INFERRED = reasoned, not
checked; nothing here is MEASURED by this lane. Rulings file `gradthink_rulings.md`: empty (no entries) at handoff.

## For Frank, in plain words

**Recommendation: (b), a reduced rule. Retire the per-module panel-and-PC-3 criterion as the trigger for going
default; replace it with a release checklist run once over the whole family set at each default move. Keep two
small things per module, both of which already exist as habits: at landing, the module has its own libpcre2
comparison (not just PC-3), and while a module is partly built, say what "built at the cut" means.**

Why retire it:

1. **The criterion never measured what it names.** D37 says "PC-3 differential coverage". PC-3 is an
   EXISTENCE check: libpcre2 must compile the probe for each not-yet-built row (READ `tests/registry/pcre2_check.c`
   header). It never compares matches. So the second half of the rule was always satisfied by every module with
   a registry row, built or not (even unbuilt `comments`/`misc` pass it). The real comparison is each module's own
   libpcre2 differential script, which the rule did not name.
2. **The panel half is already met for the modules the families contain, by the landing process.** Eleven of the
   fourteen built modules landed through a D6 design panel; the three that did not (quoting, named-groups, and
   to a degree ucp's code side) are the same two weak spots featfam found, and a per-module rule would not have
   caught them either: they were already default-OFF-eligible by the rule's text on the day nobody checked.
3. **The rule's real purpose was a protection for strangers' default**, and the thing that protects them now is the
   frozen member (a promise per VERSION, not per module) plus a check made once at the cut. A per-module panel
   that says "ok" in 2026-08 tells you little about the whole set in 2026-12 (interactions, wording, the bench list).

Why not purely (a): three concrete holes (section 3) are not caught by landing gates and need an actual
check at the cut; one OPEN wrong-answer entry (K74, `assertions`) bears on the default whichever rule stands. The
checklist is what catches them, but only if its item 2 is a real per-construct coverage table, not a sentence.

**STOP-RULE note, prominently: K74 is an open wrong-answer entry on a module in `basic1`/`extended1`.**
`$`, `\B`, `\z`, `\Z`, `(?m)$` and `(?<!.)` at the END of an ill-formed subject diverge from libpcre2 10.46 under
`-e utf8` (READ `known_issues.md:542`, widened 2026-10-22). Deferred, utf8-only, owner "the ill-formed-position family
with K75". `assertions` is the bench's biggest refuser, so it will be in the default. The checklist must say
"accept K74 with a documented divergence, or fix first": that is a ruling for you at the cut, not for this lane.
The other open K-entries on built modules are give-ups, not wrong answers: K136 (`backrefs`: the VM artifact gives
up with `PCREC_ERR_FRAMES` where libpcre2 answers, an honest give-up) and K135 (nullable prefilter decline turns an
answer into a give-up; libpcre2 also gives up). I found no open entry that returns a wrong answer for a module
outside `assertions`. I grepped K-headings marked OPEN; entries with older heading shapes (K9, K11, K12, K22, K25,
K26 "OPEN, found 2026-08") were looked at by title only: K9 is a public-API NUL truncation (not module-owned); the
others are not module wrong-answer shapes by title, but I did not read their bodies.

## 1. What the graduation rule was meant to catch

READ `decisions.md:3320` (D37, premise confirmed: "survived a checkpoint panel AND carry PC-3 differential
coverage", amended by Frank's consistency constraint) and the fourteenth-session journal (2026-08-12/13, R20 and the
`mod08` fix lanes; `dev_journal.md:6926`). The session was MOD-0.8, the checkpoint where R20 found a segfault on
the explain surface and a D27 blinded writer found a TIER-1 MISCOMPILE (`a(?i)*` accepted with the quantifier bound
to the wrong atom) in a module whose own hand-written check owned it and missed it. The criterion is that
experience written as policy: a module goes on by default only after (i) adversaries who did not write it have
tried it and (ii) an OUTSIDE authority (libpcre2) has been compared against its behaviour. The second clause was a
stated hope: the registry-vs-libpcre2 check was then new and was read as a differential. Frank's amendment is the
other half: whatever the rule, the set a developer gets must not change under them, which is the frozen-name
machinery and is independent of the criterion. **So the criterion was a quality gate on promoting a module to
strangers; the frozen sets are the honesty mechanism.** Families keep the second and replace the first's
timing: promotion is no longer one module at a time but a whole set at a version.

## 2. What each built module already has (READ, not re-run)

Gate columns: **Landing panel** = D6 file under `docs/dev/reviews/`; **libpcre2 differential** = the module's own
match/span comparison, and whether it is in `make test`'s `TEST_SECTIONS` (READ `Makefile:413`) or only opt-in;
**PC-3** = existence only (all built and unbuilt rows are covered, so it discriminates nothing); **Fuzz** =
`tests/fuzz` capturediff gate vs libpcre2 (in `make test`; its generator is base-tier, see below); **Open wrong answer**
= `known_issues.md` OPEN entries that return a wrong answer.

| module | family (featfam) | landing panel | libpcre2 differential, and in `make test`? | open wrong answer |
|---|---|---|---|---|
| classes | basic | close r16 | PC-4 62,872 cells (`run_pc4.sh`, registry section); fuzz | none found |
| modifiers | basic | close r17 + surface r20 | R20's PC-3 option-run differentials; fuzz | none found (K118 is wording, not an answer) |
| quoting | basic | none as subject (named inside design r13, r14) | `tests/quoting/d27`: 95 cells, expectations MEASURED against libpcre2 once at authoring; `checker.py` re-queries the oracle but is NOT run by `make test` (its own CLAUDE.md); no generated differential; fuzz alphabet has no `\Q` | none found |
| named-groups | basic | none as subject (inside r10, r14, r20, r32) | corpus blocks marked `# pcre2-only` were verified by translation or by libpcre2 once (`tests/named_groups/CLAUDE.md`); no differential script; fuzz alphabet has no named groups | none found |
| ucp | basic | design r1-ucp (2 critics, light) | `tests/ucp` compares every cell to libpcre2 (`test-ucp`, in TEST_SECTIONS) | none found |
| unicode-props | basic (2/3 rows built) | close r19 | `tests/uprops` whole-space `\p` membership (`test-uprops`, in TEST_SECTIONS) | none found |
| assertions | basic or extended (`\K`) | design r30 | `run_mline_diff`, `run_gstart_diff`, `run_kreset_diff` (`test-assertions`, in TEST_SECTIONS) | **K74** (utf8, ill-formed end) |
| atomic-groups | extended | design r31 (3 rounds) | `run_atomic_diff.sh` (`test-atomic`, in TEST_SECTIONS) | none found |
| backrefs | extended | design r32 (3 rounds) | `run_backref_diff`, `run_dupnames_diff` (`test-backrefs`, in TEST_SECTIONS) | none; K136 is a give-up |
| lookaround | extended | design r33 (3 rounds) | `run_lookaround_diff`, `run_expansion_diff` (`test-lookaround`, in TEST_SECTIONS) | none found |
| recursion | pcre2 | design r34, wave r35, code r36 | `run_recursion_diff.sh` (`test-recursion`, in TEST_SECTIONS); D27 blinded 1,031 cells | none found |
| callouts | none (opt-in) | none as subject; ABI in r21/r38 | `co_oracle.c` + generated differential, floor 1,000 (`test-callouts`) | n/a |
| vars | `all` only | design r1-var | PC-3 passes vacuously (libpcre2 reads `${x}` as literal; INFERRED); `test-vars` is pcrec-only | n/a |
| unbuilt: conditionals, branch-reset, verbs, comments, misc, extended-classes | named in families | none | PC-3 existence only | n/a (no producer) |

Cross-cutting (READ): the landing-identity gates (`test-atomic-identity`, `test-backrefs-identity`,
`test-recursion-identity`, `test-lookaround-identity`) are opt-in one-shot "did the module change atomic-free output
at landing" claims, deliberately not in `make test`. Mech sabotage rows exist for the registry/pc3/cli arms and the
quoting scan edge (plan_completed, M4-QUOTING battery-proven); I did not enumerate per-module mech rows. The
`reject` table and `RS_REJECTED` identity check cover refusal wording for constructs PCRE2 itself rejects.

## 3. Cases the existing gates do NOT cover (what the rule was for)

| # | gap | caught by | keeps a per-module rule? |
|---|---|---|---|
| G1 | **quoting**: no live libpcre2 comparison in `make test` (95 static cells re-checkable by hand) and the fuzz generator never produces `\Q..\E` | checklist item 2 (coverage table shows it) plus a one-time generated differential at the cut | No: a coverage table makes it a named gap to fix or accept, once |
| G2 | **named-groups**: partly translated/one-time oracle, no differential script, none in fuzz | same | No |
| G3 | **fuzz alphabet is base-tier**: lookaround, backrefs, named groups, quoting, modifiers-in-groups are not drawn (READ `fuzz.py` by grep; INFERRED beyond that); module differentials are hand-shaped, so cross-module interaction (a lookahead inside an atomic group inside a conditional) has no generated libpcre2 comparison | checklist item 3, a campaign at the cut with the set's alphabet | No: it is a property of the SET, a per-module rule cannot see it. This is the strongest argument FOR the checklist over the old rule |
| G4 | **PC-3 is existence only**, so D37's second clause is vacuous | the checklist replaces it with item 2 | The clause should be deleted, not kept |
| G5 | **K74** open wrong answer on `assertions` (utf8) | checklist item 4 | No, but needs a ruling at the cut |
| G6 | **refusal wording inside a family**: a construct the family excludes says `requires module 'X'` (fine, D26); a construct the family INCLUDES but pcrec has not built says `module 'X' is enabled but ... not implemented yet` (the 8-10 "unbuilt" bench refusals); PCRE2-rejects constructs depend on `RS_REJECTED` identity | checklist item 5, and featfam's own P2 (frozen lists only BUILT modules) removes the second shape from frozen members | No |
| G7 | **partly built modules** (`unicode-props` 2/3 rows, `misc`): what does "built at the cut" mean for a member whose rows are not all built, and what does a LATER row do to a frozen set that listed the module? | needs a rule (section 4) | A small standing rule, not a per-module panel |
| G8 | **vars/callouts** are pcrec-only: PC-3 cannot cover `vars`, and callouts' differential is pcrec's own oracle | they are in no family (by ruling), so nothing to check | n/a |

## 4. New modules landing later

Beyond the landing gates (design panel, own libpcre2 differential in `make test`, `.rxt` corpus oracle-verified per
root CLAUDE.md, spec hunk, registry rows) and "built at the cut", I see ONE thing that needs a rule, not a panel:

**A module gaining rows after a frozen set listed it.** D37 says a frozen set "compiles identically forever". With P2
(a frozen member lists only BUILT modules) the module list is fixed, but a listed module that is later extended
(`unicode-props` adding `\N{U+hhhh}`, a property gap closing) makes the frozen name ACCEPT more. featfam section 4
names this and did not choose. My lean: **frozen means (a) the list, and (b) every pattern the set accepted or
refused-with-a-gated-reason at freeze keeps its answer; rows that newly turn a refusal into an acceptance are allowed
for a listed module only if the refusal was "not implemented yet" (an unbuilt row), and the stamp is unchanged.**
That is P1-for-rows inside P2-for-modules; it matches what already happened to `classes` and `modifiers`, and it
keeps the hand-off simple: a stranger never gets a different ANSWER, only an answer where there was none. It does
need to be a stated sentence in the addendum, because Frank's consistency constraint is about being surprised, and
"a pattern that used to error now compiles" is a smaller surprise than a changed match, but it is one.

Nothing else: a new module is not in any frozen member (Frank 2026-11-06), joins `all` automatically, and joins a
family's next frozen version only if built at that cut. No per-module graduation needed.

## 5. Recommendation and draft text

**(b), reduced.** Concretely:

- RETIRE as trigger: "survived a checkpoint panel AND PC-3 differential coverage" for any module, existing or new.
- KEEP unchanged: D37's frozen-named-set mechanics, stamps, announced boundaries.
- KEEP as module-landing hygiene (already convention, not a new rule): own libpcre2 comparison in `make test` for
  every producer; `.rxt` oracle-verified; spec hunk. Nothing is added to what landing requires today.
- ADD the release checklist at each default move; its record lives in the move's announcement.

Not recommended: (a) with no checklist (G3 and G5 would go unseen: the old rule at least forced a look); (c) as it is
(clause two is vacuous and clause one is per-module so cannot see G3).

### Draft D37 addendum (NOT in decisions.md)

> **Addendum (2026-11-06, [FEAT-FAMILIES], Frank's question "do we need a rule like this at all, with the
> families"):** the graduation criterion ("checkpoint panel AND PC-3 differential coverage") is RETIRED as the
> condition for a module to be in a default. Two findings: PC-3 compares compilability, not matches, so its half
> never discriminated; and promotion is now per frozen VERSION, so a per-module verdict is the wrong grain. A
> module is in a family's next frozen member iff it is BUILT at the cut (every registry row of it that the family
> promises has a producer; unbuilt modules are listed in no frozen member, Frank 2026-11-06). The frozen-set
> mechanics of this decision are unchanged. At each move of the bare default or of a moving family name, the RELEASE
> CHECKLIST (docs/dev/release_checklist.md, to be created) is run once over the whole set and its result is recorded
> in the announcement. A later row added to a listed module may turn an "not implemented yet" refusal into an
> acceptance and never changes an answer a frozen member already gave.
> **Revisit-when:** the first default move.

### Release checklist (run at each default move; S = a script can produce it, M = manual judgment)

1. **Membership** (S): `build/pcrec --list-syntax` module column for every module in the set; each module's rows
   all non-`unbuilt` except those the set explicitly excludes; the set's expanded list equals the stamp; `basicN
   <= extendedN <= pcre2-N` and every earlier frozen member byte-identical to its committed row. (featfam's
   derivation awk plus one table compare.)
2. **Per-construct differential coverage table** (S for the table, M for the verdict): for every registry row in
   the set's modules, which libpcre2 comparison in `make test` or an opt-in battery exercises it (name the script and
   the count of cells), or `NONE`. Every `NONE` is fixed before the move or listed as a documented divergence.
   Expected `NONE` today: quoting, named-groups (G1, G2).
3. **Set-alphabet campaign** (S to run, M to triage): a fixed-seed `tests/fuzz`-style libpcre2 differential at scale
   whose generator draws the SET's constructs and their pairwise nestings (lookaround, backrefs, atomic, named
   groups, quoting, modifiers), zero content divergences or each one triaged. Needs the generator widened (G3);
   this is the one real build item the checklist implies.
4. **Open wrong-answer entries** (S for the list if K-entries gain a `module:` tag; M for the ruling): every OPEN
   `known_issues.md` entry whose heading is a wrong answer and whose construct is in the set, each ruled "fix first"
   or "accept as documented divergence"; today K74. Gives are listed separately (K136, K135).
5. **Refusal wording inside the set** (S): the `reject` table and `RS_REJECTED` identity check green; plus every
   construct the set promises but pcrec has not built produces the "not implemented yet" shape, not "requires
   module".
6. **Before/after list of what a bare compile newly accepts or changes** (S): the pattern population compiled under
   the old and new default (the bench 392 as featfam did, the `.rxt` corpus, the reject table), diffed:
   newly-compiling, newly-different artifact, newly-refused. Zero "newly refused" and zero "same pattern, different
   match" is the bar (the second is covered by item 2/3 and the corpus).
7. **Stamp and spec** (S): the abi bump ritual if the stamp text moved (D76/D94), `docs/spec/` hunk for the default,
   `docs/guide/` pointer; `make test-codegen`.
8. **Full gate on the frozen commit** (S): `make test` and the full battery green on the commit the move names
   (verdict read from the make `*** [...test-` lines, learnings).
9. **Announcement** (M): the version boundary, the new frozen name, the opt-out (`--features std1` or the old
   frozen name), and the items 2/4 divergence list in plain words.

Items producible by script today: 1, 5, 6, 7, 8 are scripts or small compositions of existing ones; 2 needs one new
script (a registry row to test-file map); 3 needs the generator widened; 4 needs a `module:` tag convention on K-entries
or stays a manual read; 9 is manual.

## 6. Open questions with leanings

1. **Is the item-3 generator widening a build, and is it the price of the family default?** It is the largest piece of
   new work the checklist implies. Lean: yes, scoped to a fixed-seed slice in `make test` plus a manual campaign,
   not a harness for its own sake (memory: harness minimal). No build go requested here.
2. **What does "built" mean for a partly built module?** Lean: a module is built iff no registry row of it is
   `unbuilt` among the rows the FAMILY promises; `unicode-props` (2/3) stays in `basic1` because the missing row
   `\N{U+hhhh}` is refused with the "not implemented yet" shape and may later become an acceptance (section 4's
   rule). Needs Frank's confirmation because it is where a frozen set quietly grows.
3. **K74 at the move:** fix first, or ship `assertions` with the utf8 divergence documented? Lean: document, the entry
   is utf8-only and deferred with a family owner, but the ruling is Frank's.
4. **Quoting and named-groups before the first move:** one generated differential each (G1, G2), a day-scale job
   each, or accept as NONE? Lean: do them; they are the two modules a stranger meets first (`\Q`, `(?<name>)`).
5. **Where the checklist lives:** a new `docs/dev/release_checklist.md` pointed at by D37's addendum, or inside
   `docs/testing.md`? Lean: its own short file; the move is rare and the list should be findable.
6. **Does a panel still run at the cut?** Lean: one light D6 panel on the WHOLE set's checklist record (what we
   found, what we accepted), as the D6 text already allows at discretion; not a per-module panel.

## STATE AT HANDOFF

Branch `lane/gradthink` off main `8fde8a30e`. Written: this report and its history-index line
(`docs/dev/history/claude_md/docs__dev__lanes.md`). `decisions.md` untouched; nothing under `src/ cli/ lib/ tests/
memfn/` touched; nothing built or run. Rulings file had no entries. The tables are READ-level; the one thing I would
recheck before relying on it is G3 (the fuzz generator's alphabet, read by grep only).
