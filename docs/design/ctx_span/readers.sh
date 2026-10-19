#!/usr/bin/env bash
# docs/design/ctx_span/readers.sh -- ctx_span.md rev 2's grep-derived reader lists, one
# section per list (B2, C1, A4, the census tables A-C). Read-only; run from the repo root:
#   bash docs/design/ctx_span/readers.sh > docs/design/ctx_span/readers.txt
# Every list here is a GREP, so a reader the note's prose forgot still appears. `command
# grep` (the interactive grep may be a ugrep function that skips worktree contents).
set -u
X=(--exclude-dir=worktrees --exclude-dir=build --exclude-dir=.git)
code() { command grep -vE '^[^:]+:[0-9]+:\s*(/?\*|//)'; }
# a docs/spec hit is printed by its PARAGRAPH id, never by line (make test-spec-history)
spec_ids() { python3 -I -c '
import re, sys
for l in sys.stdin:
    m = re.match(r"(\./)?(docs/spec/[^:]+):([0-9]+):(.*)", l)
    if not m:
        sys.stdout.write(l); continue
    f, n = m.group(2), int(m.group(3))
    pid = "?"
    for i, t in enumerate(open(f, encoding="utf-8").read().split("\n")[:n]):
        a = re.search(r"<a id=\"(s[0-9a-z-]+)\"", t)
        if a: pid = a.group(1)
    sec = pid[1:].replace("-p", "\u00b6").replace("-", ".")
    print("%s \u00a7%s:%s" % (f, sec, m.group(4)[:150]))
'; }
echo "## 1. readers of the abi NUMBER (B2): the number 80 beside abi/ABI, or as \`80\`"
echo "##    (journal/lanes/reviews are history and excluded; classify each hit reader|record)"
command grep -rnIE '(abi|ABI_EXPECT|PCREC_ARTIFACT_ABI|PCREC_RX_ABI_H)[^0-9]{0,40}\b80\b|`80`|\b80\b[^0-9]{0,25}\babi\b' "${X[@]}" . \
  | command grep -vE '^\./docs/dev/(dev_journal|lanes|reviews)/|^\./docs/dev/dev_journal|^\./studies/specclean/' | spec_ids \
  | sed -E 's#(plan\.md):([0-9]+):#\1 (line \2):#' | cut -c1-200   # PL14: no plan.md:<line> text in a tracked file
echo
echo "## 2. the multiline field and the two kinds, CODE lines in src/ (tables A, B)"
command grep -rnE 'anch\.multiline|N_BOT_M|N_EOL_M|nl_bit|CTXROW_NEWLINE|cr_nl_(reads|set)|PCREC_NO_MLINECTX' src --include=*.c --include=*.h | code | cut -c1-170
echo
echo "## 3. the same names in COMMENT lines in src/ (reworded at P2c; C1)"
command grep -rnE 'anch\.multiline|N_BOT_M|N_EOL_M|nl_bit|CTXROW_NEWLINE|PCREC_NO_MLINECTX|mlinectx' src --include=*.c --include=*.h | command grep -E '^[^:]+:[0-9]+:\s*(/?\*|//)' | cut -c1-170
echo
echo "## 4. readers of the knob and its gate OUTSIDE src/ (C1: tests, scripts, Makefile, CLAUDE.md)"
command grep -rnI 'NO_MLINECTX\|mlinectx\|run_mlinectx' "${X[@]}" tests scripts Makefile docs/testing.md \
  | command grep -v '^tests/mech/sabotages/' | cut -c1-170
echo
echo "## 5. the text-side (?m) classifier's users (tests/lib/mlscan.py; kept, comment reworded)"
command grep -rnI 'mlscan\|multiline_anchor\|multiline_caret' tests scripts | command grep -v '^tests/lib/mlscan.py' | cut -c1-170
echo
echo "## 6. truth-function readers (table C) and raw fn literals in tests (A4)"
command grep -rnE 'CTXFN_|ctxfn|u\.ctx\.fn' src --include=*.c --include=*.h | code | cut -c1-170
command grep -rnE 'pcrec_poss_ctx_admits\(0x|for \(int t = 0; t < 16' tests | cut -c1-170
echo
echo "## 7. possessify's First.nullable readers (A4: each sees today's value at P2c)"
command grep -nE '\.nullable|->nullable' src/opt/possessify.c | command grep -vE '^[0-9]+:\s*(/?\*|//)' | command grep -vE 'nullable *= ' | cut -c1-150
