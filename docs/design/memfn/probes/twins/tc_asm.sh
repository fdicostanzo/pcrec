#!/bin/sh
# memfn twins T-C: does a compile-time-constant descriptor compile to the
# hand-specialized kernel's code? Disassembles tc_desc.c's hand_X, desc_X
# and mut_X (one object per compiler), normalizes away addresses and symbol
# names (a branch target becomes its offset in the function, a page/
# relocation operand becomes SYM), and diffs desc_X and mut_X against hand_X.
#
#   sh tc_asm.sh OUTDIR CC [CFLAGS...]     (run from the repo root)
#
# Writes OUTDIR/tc_asm.<cc>.txt: a per-set summary table (instruction
# counts, differing-line counts) followed by every diff in full.
set -u
OUT=$1 CC=$2
shift 2
SRC=docs/design/memfn/probes/twins/tc_desc.c
mkdir -p "$OUT"
tag=$(basename "$CC")
O=$OUT/tc_desc.$tag.o
"$CC" -O2 -std=gnu11 "$@" -c -o "$O" "$SRC" || exit 1
D=$OUT/tc_asm.$tag.d
mkdir -p "$D"
# one function's disassembly: llvm-objdump (Mac) or GNU objdump (Linux),
# with or without the Mach-O leading underscore
dis() {
    for sym in "_$1" "$1"; do
        if objdump --version 2>/dev/null | grep -q LLVM; then
            objdump -d --no-show-raw-insn --disassemble-symbols="$sym" "$O" 2>/dev/null
        else
            objdump -d --no-show-raw-insn --disassemble="$sym" "$O" 2>/dev/null
        fi | awk '/^[0-9a-f]+ <.*>:$/ {on=1; next} on && NF' > "$D/raw.s"
        [ -s "$D/raw.s" ] && { cat "$D/raw.s"; return; }
    done
}
fn() { # fn NAME: the normalized body of one function (BSD sed has no \b: perl)
    dis "$1" | perl -pe 's/^\s*[0-9a-f]+:\s*//; s/\s*[;#].*$//;
        s/(0x)?[0-9a-f]+ <[A-Za-z0-9_.]+\+(0x[0-9a-f]+)>/<+$2>/g;
        s/(0x)?[0-9a-f]+ <[A-Za-z0-9_.]+>/<+0>/g;
        s/^(adrp\s+\w+),.*/$1, SYM/;
        s/-?(0x)?[0-9a-f]*\(%rip\)/SYM(%rip)/g'
}
bag() { # bag FILE: the instruction MULTISET with registers renamed away
    perl -pe 's/<\+0x[0-9a-f]+>/<T>/g; s/\b[vqdswx]\d+\b/REG/g; s/%[xyz]mm\d+/REG/g; s/%r\d+[dwb]?|%[re][a-z]{2}|%[a-z][hl]\b/REG/g' "$1" | sort
}
R=$OUT/tc_asm.$tag.txt
{
    echo "# tc_asm: $("$CC" --version | head -1), flags: -O2 $*"
    echo "# diff = differing lines in order; bag = differing lines of the register- and branch-target-renamed,"
    echo "# sorted instruction multiset (0 = the same instructions, scheduled/allocated"
    echo "# differently); ICF = the compiler folded desc_X onto hand_X (one symbol)"
    echo "# set  hand-insns  desc-insns  desc-diff  desc-bag    mut-insns  mut-diff  mut-bag"
    for set in $(grep -oE '^ *X\(([a-z0-9]+),' "$SRC" | sed -E 's/.*X\(([a-z0-9]+),/\1/'); do
        fn "hand_$set" > "$D/hand_$set.s"
        [ -s "$D/hand_$set.s" ] || continue
        fn "desc_$set" > "$D/desc_$set.s"
        fn "mut_$set" > "$D/mut_$set.s"
        icf=""
        [ "$(nm "$O" | awk -v f="desc_$set" '$3 == f || $3 == "_" f {print $1}')" = \
          "$(nm "$O" | awk -v f="hand_$set" '$3 == f || $3 == "_" f {print $1}')" ] && icf=" ICF"
        dd=$(diff "$D/hand_$set.s" "$D/desc_$set.s" | grep -c '^[<>]')
        db=$(diff "$D/hand_$set.s" "$D/desc_$set.s" >/dev/null; bag "$D/hand_$set.s" > "$D/h.bag"; bag "$D/desc_$set.s" > "$D/d.bag"; diff "$D/h.bag" "$D/d.bag" | grep -c '^[<>]')
        dm=$(diff "$D/hand_$set.s" "$D/mut_$set.s" | grep -c '^[<>]')
        bag "$D/mut_$set.s" > "$D/m.bag"
        mb=$(diff "$D/h.bag" "$D/m.bag" | grep -c '^[<>]')
        printf '%-5s %10d %11d %10d %9d%-4s %9d %9d %8d\n' "$set" "$(wc -l < "$D/hand_$set.s")" \
            "$(wc -l < "$D/desc_$set.s")" "$dd" "$db" "$icf" "$(wc -l < "$D/mut_$set.s")" "$dm" "$mb"
    done
    for set in $(ls "$D" | sed -nE 's/^hand_(.*)\.s$/\1/p'); do
        echo
        echo "## diff hand_$set desc_$set (in order)"
        diff "$D/hand_$set.s" "$D/desc_$set.s"
        echo "## bag diff hand_$set desc_$set"
        bag "$D/hand_$set.s" > "$D/h.bag"; bag "$D/desc_$set.s" > "$D/d.bag"
        diff "$D/h.bag" "$D/d.bag"
    done
} > "$R"
sed -n '1,14p' "$R"
