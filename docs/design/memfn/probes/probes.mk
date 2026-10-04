# memfn R1 probes. Never built by pcrec's make. Run from the repo root:
#   make -f docs/design/memfn/probes/probes.mk run      # both compilers, -O2
#   make -f docs/design/memfn/probes/probes.mk check    # exhaustive vs reference
#   make -f docs/design/memfn/probes/probes.mk check-asan   # same, clang ASan
#   make -f docs/design/memfn/probes/probes.mk asm      # disassembly for review
# Output tree: build/memfn_probe/ (gitignored). On the Linux box use
# CC_GCC=gcc CC_CLANG=clang and run under `taskset -c 2` (D144 addendum 1).
SRC      := docs/design/memfn/probes/callcost.c
OUT      := build/memfn_probe
CC_GCC   ?= gcc-16
CC_CLANG ?= clang
CFLAGS   ?= -O2 -std=gnu11 -Wall -Wextra

$(OUT):
	mkdir -p $@
$(OUT)/callcost.gcc: $(SRC) | $(OUT)
	$(CC_GCC) $(CFLAGS) -o $@ $<
$(OUT)/callcost.clang: $(SRC) | $(OUT)
	$(CC_CLANG) $(CFLAGS) -o $@ $<
$(OUT)/callcost.asan: $(SRC) | $(OUT)
	$(CC_CLANG) -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer -o $@ $<

check: $(OUT)/callcost.gcc $(OUT)/callcost.clang
	$(OUT)/callcost.gcc --check
	$(OUT)/callcost.clang --check
check-asan: $(OUT)/callcost.asan
	$(OUT)/callcost.asan --check
run: $(OUT)/callcost.gcc $(OUT)/callcost.clang
	$(OUT)/callcost.gcc
	$(OUT)/callcost.clang
asm: $(SRC) | $(OUT)
	$(CC_GCC) $(CFLAGS) -S -o $(OUT)/callcost.gcc.s $<
	$(CC_CLANG) $(CFLAGS) -S -o $(OUT)/callcost.clang.s $<
.PHONY: check check-asan run asm
