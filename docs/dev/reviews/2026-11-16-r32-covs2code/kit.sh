#!/usr/bin/env bash
# Round crit-covs2code run kit (read-only use of the review trees; writes only under OUTDIR).
#
#   kit.sh TREE OUTDIR PATFILE SUBJFILE [pcrec args...]
#
# TREE     subject | base | trace-subject | trace-base | plant:<ROWID>   (e.g. plant:S3264)
#          trace-* compilers print the PCREC_CAND_TRACE records (MFWSTMT etc.) on stderr -> OUTDIR/trace.txt
#          base/trace-base IGNORE nothing: an option BASE does not know is refused (BASE has no --window-search-width)
# OUTDIR   a NEW directory under YOUR lens dir; the emitted C lands as OUTDIR/a.c (+ a.h).
#          For BASE vs SUBJECT byte compares, use two OUTDIRs (same basename a.c in both).
# PATFILE  a file holding the pattern bytes exactly (no trailing newline needed; one trailing \n is stripped).
# SUBJFILE one subject per line, TEXT (use \xHH? no: raw bytes; a line = a subject; empty line = empty subject)
#          or, if SUBJFILE ends in .hex, one hex subject per line.
# Flags after SUBJFILE go to pcrec (e.g. -i, -e utf8, --window-search-width=4095).
# The oracle uses ORACLE_FLAGS (default '-'; letters i/u as tests/kitproof/oracle.c) -- set it to match -i / -e utf8.
#
# Output (stdout): ROUTE=<RX_DFA_SCAN>, then per subject:  SAME|DIFF <subject-hex> pcrec=<ans> pcre2=<ans>
# Answers: kitproof drv/oracle format (rx_search at every startoffset, then '|' and the find-all loop).
# Everything is bounded by timeout; compile 120 s, run 20 s.
set -u
R=/var/tmp/pcrec-pcrec/scratch/crit-covs2code
W=/home/pcrec/projects/pcrec/worktrees/crit-covs2code
[ $# -ge 4 ] || { sed -n 2,22p "$0"; exit 2; }
tree="$1"; out="$2"; pf="$3"; sf="$4"; shift 4
case "$tree" in
  subject) P=$W/build/pcrec; SRC=$W ;;
  base) P=$R/base/build/pcrec; SRC=$R/base ;;
  trace-subject) P=$R/trace/subject/pcrec; SRC=$W ;;
  trace-base) P=$R/trace/base/pcrec; SRC=$R/base ;;
  plant:*) P=$R/plants/${tree#plant:}/tree/build/pcrec; SRC=$R/plants/${tree#plant:}/tree ;;
  *) echo "kit: unknown TREE $tree"; exit 2 ;;
esac
[ -x "$P" ] || { echo "kit: $P not built (yet?)"; exit 2; }
mkdir -p "$out"
pat="$(cat "$pf")"
nice timeout 120 "$P" -p rx "$@" -o "$out/a.c" --pattern "$pat" 2> "$out/trace.txt"; rc=$?
echo "PCREC_RC=$rc"
[ $rc -eq 0 ] || { head -5 "$out/trace.txt"; exit 1; }
echo "ROUTE=$(sed -n 's/^#define RX_DFA_SCAN "\([^"]*\)".*/\1/p' "$out/a.c")"
nice timeout 120 gcc -O1 -std=gnu11 -include "$out/a.h" -o "$out/drv" "$W/tests/kitproof/drv.c" "$out/a.c" 2> "$out/cc.txt" \
  || { echo "kit: driver compile failed"; head -5 "$out/cc.txt"; exit 1; }
[ -x $R/kit/oracle ] || gcc -O2 -std=gnu11 -o $R/kit/oracle "$W/tests/kitproof/oracle.c" -lpcre2-8
case "$sf" in
  *.hex) cp "$sf" "$out/subj.hex" ;;
  *) python3 -I -c 'import sys
d=open(sys.argv[1],"rb").read()
if d.endswith(b"\n"): d=d[:-1]
for ln in d.split(b"\n"): print(ln.hex())' "$sf" > "$out/subj.hex" ;;
esac
phex="$(printf '%s' "$pat" | xxd -p | tr -d '\n')"
timeout 20 "$out/drv" < "$out/subj.hex" > "$out/pcrec.ans"
awk -v f="${ORACLE_FLAGS:--}" -v p="$phex" '{print f "\t" p "\t" $0}' "$out/subj.hex" | timeout 20 $R/kit/oracle | cut -f4- > "$out/pcre2.ans"
paste "$out/subj.hex" "$out/pcrec.ans" "$out/pcre2.ans" | python3 -I -c '
import sys
for ln in sys.stdin:
    s, a, b = (ln.rstrip("\n").split("\t") + ["", ""])[:3]
    # oracle "x" cells (startoffset on a UTF-8 continuation byte) are not compared
    aa, bb = a.split("|")[0].split(","), b.split("|")[0].split(",")
    same = len(aa) == len(bb) and all(y == "x" or x == y for x, y in zip(aa, bb)) and a.split("|")[1:] == b.split("|")[1:]
    print(("SAME" if same else "DIFF"), s[:80], "pcrec=" + a[:300], "pcre2=" + b[:300])'
