# S221 ([OPT-5] STEP 2) — THE PINNED SPAN'S START IS WRITTEN AS `0` INSTEAD OF
# `search_from`: THE ABSOLUTE-OFFSET TRAP.
#
# WHAT IT BREAKS. `docs/spec/match_api.md` §3.1: "Every offset written to
# `caps` is an ABSOLUTE offset into `s`, never relative to `startpos`" — a
# MEASURED property a find-all loop depends on. The pinned form's whole
# content is that the match begins at `search_from`, and writing the literal
# `0` there is the obvious way to get it wrong: it is right at every call the
# corpus makes and wrong at every other one.
#
# ================== WHY THIS ROW EXISTS SEPARATELY ==================
#
# IT IS INVISIBLE TO EVERY SINGLE-SEARCH-AT-0 TEST, WHICH IS MOST OF THE
# CORPUS. A plain `m`/`n` `.rxt` cell searches from offset 0, where
# `search_from == 0` and the plant writes the same value the correct code
# would; only the opt-in `ms`/`ns` forms carry a nonzero startpos. So the
# detector is not a corpus cell at all — it is
# `tests/codegen/run_search_pinned.sh` §10's own driver, which sweeps EVERY
# startpos from 0 to n+1 on every subject and reads `caps[0][0]` EXPLICITLY
# against the `-fno-start-pinned` build's independently derived answer.
#
# THE POPULATION IS COUNTED, WHICH IS THE NOTE'S FIRST ACCEPTABLE DISCHARGE
# (§5.6d), AND THE WITNESSES ARE BUILT, WHICH IS ITS SECOND. MEASURED
# 2026-09-02: of the 175 corpus patterns the predicate accepts, only FIVE
# carried any `ms`/`ns` cell at all — 14 cells between them, on `x*`, `a*`,
# `(?>a?)`, `(?:ab)?+` and `\Q\E`. That is thin enough that the row does not
# rest on it: `tests/base/start_pinned_startpos.rxt` (79 cells over four
# pinned patterns at every startpos) and its seeded sibling
# `tests/assertions/start_pinned_startpos.rxt` were added with this row, and
# the floor below is on the first of them.
#
# THE `harness` ARM IS THEREFORE EXPECTED TO GO RED ON THE NEW FILE AND
# NEARLY NOWHERE ELSE, which is this row working rather than a
# half-detection — the same shape `offsetskip`'s S187 and `sizeterm`'s
# S191/S192 already have. Before those cells existed the arm would have been
# green outright.
#
# THE FAILURE MODE IS A SPAN THAT STARTS BEFORE THE SEARCH DID: on `a*` over
# "xxaa" from startpos 2 the true span is [2,4) and the planted build reports
# [0,4). A find-all loop reading `caps[0][1]` still terminates, so nothing
# hangs and nothing crashes; the reported start is simply wrong, which is
# learnings §3's blind field exactly.
SAB_ID="S221-pinned-start-written-as-zero"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="searchpinned harness"
SAB_DESC="The pinned search writes caps[0][0] = 0 instead of = search_from, so every span reported from a nonzero startpos begins before the search did -- 'a*' over \"xxaa\" from startpos 2 reports [0,4) where the true span is [2,4). Invisible to every search at startpos 0, which is most of the corpus; the detector is run_search_pinned.sh's every-startpos differential against the reverse machine's own answer"
SAB_DOC_FIGURE="PREDICTED (the canonical DETECTED figure is owed from the manager's own matrix run): searchpinned RED in §10 only, and only on the cells at startpos > 0; every structural row in that file GREEN, and the harness arm expected green or nearly so, because a startpos-0 cell cannot tell the two spellings apart."
# [MECH-REACH] THE PROBE says the pinned form still emits an offset to get
# wrong: the clean artifact writes `search_from` into caps[0][0], not a
# literal. THE FLOOR says the corpus's nonzero-startpos population — the only
# `.rxt` cells that could see this at all — still exists.
SAB_REACH='"$PCREC" --features all -p rx --no-captures -o "$REACH_TMP/o.c" -- "a*" && grep -q "capture_spans\[0\]\[0\] = (ptrdiff_t)search_from;" "$REACH_TMP/o.c" && echo REACH-PINNED-WRITES-SEARCH-FROM'
SAB_REACH_EXPECT="REACH-PINNED-WRITES-SEARCH-FROM"
SAB_REACH_POP="tests/base/start_pinned_startpos.rxt|^(ms|ns) |50"
SAB_COUNT=1
SAB_BEFORE='            "    if (capture_spans) { capture_spans[0][0] = (ptrdiff_t)search_from; capture_spans[0][1] = (ptrdiff_t)last_accept_position; }\n"'
SAB_AFTER='            /* SABOTAGE S221: the absolute-offset trap. */
            "    if (capture_spans) { capture_spans[0][0] = (ptrdiff_t)0; capture_spans[0][1] = (ptrdiff_t)last_accept_position; }\n"'
