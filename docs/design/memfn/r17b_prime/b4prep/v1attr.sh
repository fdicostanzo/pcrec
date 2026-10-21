#!/usr/bin/env bash
# docs/design/memfn/r17b_prime/b4prep/v1attr.sh -- b4prep item 2: grid1's V1/walk arms against grid2's.
#   v1attr.sh SLOTROOT      (SLOTROOT = .../worktrees/memfn-slot; reads grid1/ and grid2/ under it, writes nothing)
# One line per cell: art.c of the V1 and walk arms byte-identical?; art.o and gdrv.o disassembly identical?
S=$1
printf 'cell\tV1_art.c\twalk_art.c\tart/new\tart/deny\tV1_art.o\tV1_gdrv.o\twalk_art.o\twalk_gdrv.o\n'
dis() { objdump -d --no-show-raw-insn "$1" | tail -n +4 | md5sum; }
for c in dig bounded dfa-hat hex-run word-eq quad; do
    r=$c
    for p in V1/art.c walk/art.c; do cmp -s "$S/grid1/bin/$c/$p" "$S/grid2/bin/$c/$p" && r="$r	same" || r="$r	DIFF"; done
    for p in new deny; do cmp -s "$S/grid1/art/$c/$p/art.c" "$S/grid2/art/$c/$p/art.c" && r="$r	same" || r="$r	DIFF"; done
    for p in V1/art.o V1/gdrv.o walk/art.o walk/gdrv.o; do
        [ "$(dis "$S/grid1/bin/$c/$p")" = "$(dis "$S/grid2/bin/$c/$p")" ] && r="$r	same" || r="$r	DIFF"; done
    printf '%s\n' "$r"
done
cmp -s "$S/grid1/lib/gdrv.c" "$S/grid2/lib/gdrv.c" && echo "gdrv.c	same" || echo "gdrv.c	DIFF"
