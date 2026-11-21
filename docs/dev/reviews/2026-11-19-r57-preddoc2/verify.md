# r57 preddoc2: the coordinator's inline verification (plants on copies of the sample root; plant.sh/ent.py in the round dir .coord/v)

## control
--- ctl
pred_doc_lint: checks passed 154, failed 0
lint rc=0
## RULES-1 (control: no move line)
--- r1c
L4 docs/design/predicates/library_details.md:7: record title "2026-11-09 NO SUCH ENTRY" not found in docs/design/plan_row_bodies/COND-FAMILY.md
pred_doc_lint: checks passed 154, failed 1
lint rc=1
## RULES-1
--- r1
pred_doc_lint: checks passed 154, failed 0
lint rc=0
## RULES-2
--- r2
pred_doc_lint: checks passed 154, failed 0
lint rc=0
## RULES-3a / CONTRACT-4c
--- r3a
pred_doc_lint: checks passed 155, failed 0
lint rc=0
## CONTRACT-4a
--- c4a
pred_doc_lint: checks passed 155, failed 0
lint rc=0
## RULES-4
--- r4
L9 docs/design/predicates/library_details.md:11: slug 'module:' is not lower-case kebab
L9 docs/design/predicates/library_details.md:11: slug 'Bad' is not lower-case kebab
L9 docs/design/predicates/library_details.md:11: slug 'Name' is not lower-case kebab
L9 docs/design/predicates/library_details.md:12: slug 'default:' is not lower-case kebab
pred_doc_lint: checks passed 155, failed 4
lint rc=1
## CONTRACT-9c
--- c9c
pred_doc_lint: checks passed 154, failed 0
lint rc=0
## CONTRACT-9c control
--- c9cc
L8 docs/design/predicates/library.md:11: 'modes: n/a (skeleton ...)' is replaced by the line 'skeleton: yes'
pred_doc_lint: checks passed 153, failed 1
lint rc=1
## CONTRACT-9d
--- c9d
pred_doc_lint: checks passed 154, failed 0
lint rc=0
## CONTRACT-9e
--- c9e
L3 docs/design/predicates/core_details.md: no details entry for base piece core/holes/nothing/name
L3 docs/design/predicates/core_details.md:23: details entry core/holes/name has no base piece
pred_doc_lint: checks passed 152, failed 2
lint rc=1
## RULES-4 (history field)
--- r4b
pred_doc_lint: checks passed 154, failed 0
lint rc=0
## CONTRACT-9d (regex-default piece: example removed, statement names modes)
--- c9d
pred_doc_lint: checks passed 153, failed 0
lint rc=0
## CONTRACT-9d control (example removed only)
--- c9dc
pred_doc_lint: checks passed 153, failed 0
lint rc=0
pred_doc_lint: checks passed 154, failed 0
## CONTRACT-9e lint rc=0
## CONTRACT-9d control (class: example removed only)
--- c9dc2
L8 docs/design/predicates/core.md:14: no example line naming WHOLE, SEARCHED and FIND-ALL (or 'modes: n/a (<why>)')
pred_doc_lint: checks passed 152, failed 1
lint rc=1
## CONTRACT-9d (class: example removed, statement names the modes)
--- c9d2
pred_doc_lint: checks passed 153, failed 0
lint rc=0
## CONTRACT-1 live dup tag
$ entry /var/tmp/pcrec-pcrec/scratch/crit-preddoc2/.coord/v/c1 core/holes/class -l 0
### Class   [core/holes/class]   reading 2026-11-02
A hole stands for one pattern fragment of the named class.
### Name   [core/holes/class]   ?  2026-11-03
entry: 2 items (profile predicates, level 0)
entry rc=0
## CONTRACT-2
$ entry /var/tmp/pcrec-pcrec/scratch/crit-preddoc2/R/subject/scripts/tests/pred_doc/root -g core/holes/word -p predicates
entry: 0 items (profile predicates, level 0)
entry rc=1
$ entry /var/tmp/pcrec-pcrec/scratch/crit-preddoc2/R/subject/scripts/tests/pred_doc/root core/holes/word -l 0
entry: was core/holes/word -> lib/names/word
### Word   [lib/names/word]   ?  2026-11-05
entry: 1 items (profile predicates, level 0)
entry rc=0
## CONTRACT-7
--- c7
pred_doc_lint: checks passed 153, failed 0
lint rc=0
$ entry /var/tmp/pcrec-pcrec/scratch/crit-preddoc2/.coord/v/c7 lib-trim-q -l 0
entry: no item for 'lib-trim-q'
entry rc=1
## CONTRACT-3: was: line dropped, old tag reused by a new core piece
pred_doc_lint: checks passed 159, failed 0
lint rc=0
$ entry /var/tmp/pcrec-pcrec/scratch/crit-preddoc2/.coord/v/c3 core/holes/word -l 0
### Word   [core/holes/word]   ?  2026-11-07
entry: 1 items (profile predicates, level 0)
entry rc=0
## CONTRACT-8
--- c8
pred_doc_lint: checks passed 154, failed 0
lint rc=0
## CONTRACT-7 at BASE (pre-existing?)
2:394:                if not st.startswith("open ") or not SLUG_RE.match(st[4:].strip()):
3:397:                rep.fail("L4", where, "status '%s' not in ruled|reading|open <slug>|under-construction|parked|?" % st)
6:723:    ("L4", "open without a slug", lambda r: sub(r, LB, "open lib-trim-q 2026-11-04", "open 2026-11-04")),
7:724:    ("L4", "open with a non-kebab slug", lambda r: sub(r, LB, "open lib-trim-q 2026-11-04", "open Lib_Trim 2026-11-04")),
## CONTRACT-1 at BASE
473:        hits = [i for p in ctx.profiles if p["form"] == "pieces" for i in (ctx.items(p) or []) if i.id == k]
474-        if hits:
475-            return Result(hits)
476-    # 6 a lower-case kebab slug: every live pair profile's index, and every `pieces` profile's details slugs
SURVIVED V see off META
SURVIVED V skeleton off META
SURVIVED V IDENT no digits
NOMATCH  V move line keeps field (matches 0)
mut: total 5, killed 1, equivalent 0, SURVIVED 3, NOMATCH 1
