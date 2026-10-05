# 2026-10-05 r1 — light D6 panel: the [OPT-SETS] design note

Subject: `docs/design/option_sets.md` (lane optsets, main a2b9d831). Two read-only critics:

- **setcrit1** (opus): the model and its semantics. It ran measured probes against build/pcrec at abi 60, using scratch .rxt files.
- **setcrit2** (sonnet): surfaces, stamps and checks, by reading only.

Verdict: the IDEA holds (a set as a partial assignment; families as exclusive axes; the dial's five positions as pinned members, which setcrit1 checked byte-identical cell by cell). The note is NOT ready for Frank's questions:

- It misdescribes today's cross-source composition (raw bits UNION, features WHOLE-LIST, not per-axis file-wins).
- One blocker: deny/force pairs are ONE registry row.
- Its constraint table is not first-match, because rows co-fire today.
- Its headline rules hold only within one source.
- Its new always-emitted RX_SETS stamp has no consumer, duplicates RX_TUNE, varies in length with the request, and stamps the spelling rather than the configuration.
- Its checks derive from the table they check.
- Two of its three build triggers are not independent.

All findings ACCEPTED (manager), to revision lane optsrev.

## Model and semantics (setcrit1)

| id | sev | finding | disposition |
|---|---|---|---|
| OS-M1 | BLOCKER | deny/force (`-fno-X`/`-fX`) are ONE axes.def row. Today, file `-fno-prefilter` + CLI `-fprefilter` is REFUSED, and file/CLI comments compose deny-wins (both measured). Today's rule is union-then-pair-rule, not file-wins. | Rule deny/force as ONE three-valued axis; self-contradiction refuses uniformly at every tier; state today's cross-source union; keep row 3 off raw -f bits or rule the change. Fix the §4.1/§3.4/§4.4 examples. |
| OS-M2 | MAJOR | "D93 per-axis, unchanged" is false: raw bits compose by UNION, `features` is WHOLE-LIST file-wins (measured: CLI `--features atomic-groups` dropped under a file `features` line). §4.5's model check fails. | Tabulate today's cross-source rule per axis KIND; keep the per-element reading out of the cross-source tier or rule the change. |
| OS-M3 | MAJOR | The constraint table is not first-match: rows co-fire today (`-futf-check -fstartpos-guard=align` under byte gives TWO inert stamps). | Apply every row, REFUSE rows first; first-match only per party. |
| OS-M4 | MAJOR | "Conflicts refused" and "explicit beats set" hold only within one source. Across sources a file set overrules a CLI set/explicit, with only a report. | Rule it explicitly (report-not-refuse per D93, or refuse cross-source set disagreements); state it in §0/§2.4. |
| OS-M5 | MAJOR | "Not a fifth beside them" is false: features, configs and findings include all stay separate; only the dial moves. | Reword to "a fifth that absorbs the dial"; name the features migration trigger or why it never comes. |
| OS-m6 | MINOR | Order matters on family axes (`--set=min-size,speed` ≠ reverse; `--tune` vs `--set` later-wins). | Family axes are one ordered CLI tier; explicit-over-set covers non-family axes only. |
| OS-m7 | MINOR | Meta-set resolution is circular (family resolution precedes bundle expansion). | A fixpoint step, or forbid meta-sets. |
| OS-m8 | MINOR | The tail misses cells made inert by a DOMINATING axis (`--tune=min-size -fno-size-term`). | Add a dominates relation, or narrow the claim. |
| OS-m9 | MINOR | The "weakest member" class order is incoherent with its own example; the ladder cells move the give-up surface; the class check reads a hand tag. | A partial order or explicit rules; the give-up carve-out; name DIAL-S3 as the real control. |
| OS-m10 | MINOR | Row 5 deny-wins is a fourth verdict; DERIVE also disables. | Name GRANDFATHERED-ASSIGN; define DERIVE as enable/disable. |
| OS-m11 | MINOR | Row 8 needs a FORCE the mechanism never invents; its predicate is unreachable. | Ship UNREACHED with its derivation, or drop it; "not ≥" wording. |
| OS-n12/13/14 | NOTE | The dial byte-identity is sound (with code-location corrections). The raw `--tune` path wins silently today, so row 3 adds a report. A D103 diff adding a vector deny to a pinned member turns an accepted pair into a refusal. | Apply the corrections; list the stderr change; add the refusal check to the D103 diff ritual. |

## Surfaces, stamps and checks (setcrit2)

| id | sev | finding | disposition |
|---|---|---|---|
| S1 | high | The RX_SETS tail stamps the SPELLING, not the configuration (`--set=trace -fno-comments` vs `--trace -fno-comments`). | Drop the tail, or define it as resolved assignment minus members, with no provenance. |
| S2 | high | Two stamps for one fact (RX_TUNE + RX_SETS's tune member), with different default rules. | Exclude families that own a stamp (tune, isa) from RX_SETS. |
| S3 | high | No consumer, and it is always emitted: it is built ahead of need (D77). | Emit RX_SETS only when a set is NAMED (no set: no bytes, no abi move), or gate it on the bench's answer. |
| S4 | high | The request-dependent stamp length can feed size-predicated selection (K79/K80, EMIT-VERB precedents). | Render size-neutral; add a prefix-invariance-style check. |
| S5 | med | The byte-count reader class is understated. | List it in §5.2; a by-grep sweep plus running the suites that count (D94 addendum). |
| S6 | med | Registry names become stamp vocabulary, so a rename is an abi event. | Say so, or restrict the tail to spelled axes. |
| S7 | med | Config surfaces overlap (raw `pcrec` line vs `set` line); a CLI flag silently lost to a file set leaves no trace in the artifact; the API refusal needs an error code. | Specify the tier; spec the code in match_api.md §8.2. |
| S8 | high | Three of seven sabotage rows are unreachable today, and the note admits only one. | SAB_REACH/SAB_REACH_POP declarations plus a NOW-REACHED runner check. |
| S9 | med | The conflict path may stay unreached even after the trigger fires. | Name a planned witness, or defer the join-conflict machinery. |
| S10 | high | The derived-set check shares its source with its subject (the `vector` tag). | Count the population independently (name pattern, SCAN_ROWS, emit-site grep). |
| S11 | med | Gate 3 cannot read a spec for DERIVED sets. | Pinned sets: spec table; derived sets: S10's independent count. |
| S12 | high | The test-axes job list is derived from `--list-sets`, the thing under test. | An independent member-count floor. |
| S13 | high | v4/SVE/SVE2 never run on any house box (no AVX-512, no SVE, CI runs no test-axes). | A compile-only arm on every box; name the box that owns each runtime member. |
| S14 | med | vector × isa costs 32 corpus runs. | State the size; floor the pairs rows. |
| S16 | high | Triggers 1 and 2 are not real triggers. Re-expressing the dial (Q12) moves a working mechanism with no measured need. | Tighten trigger 2; make Q12 its own step with its own D77 trigger. |

## Reflection

Third panel in two days, and the same two failure classes as the handoff panel: checks that derive their expectations from the table they check, and a stamp added to every artifact without counting its readers. The measuring critic again found what reading could not. Today's three composition rules were measured directly, and the note's description of them was wrong in a way no reader of the note alone could see.
