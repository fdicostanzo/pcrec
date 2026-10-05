# memfn R1 probes. Never built by pcrec's make. Run from the repo root:
#   make -f docs/design/memfn/probes/probes.mk run      # both compilers, -O2
#   make -f docs/design/memfn/probes/probes.mk check    # exhaustive vs reference
#   make -f docs/design/memfn/probes/probes.mk check-asan   # same, clang ASan
#   make -f docs/design/memfn/probes/probes.mk asm      # disassembly for review
# R1b (isa_selection.md), the ISA-selection probe:
#   ... probes.mk check-isa check-asan-isa run-isa     # as above, isacost.c
#   ... probes.mk compile-x86    # Mac only: compile-check the x86 ELF/Mach-O paths
#   ... probes.mk isanote        # Linux x86 only: the loader ISA-marker probe
# Output tree: build/memfn_probe/ (gitignored). On the Linux box use
# CC_GCC=gcc CC_CLANG=clang and run under `taskset -c 2` (D144 addendum 1).
SRC      := docs/design/memfn/probes/callcost.c
ISRC     := docs/design/memfn/probes/isacost.c
NSRC     := docs/design/memfn/probes/isanote.c
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

# ---- R1b: isacost.c ----
$(OUT)/isacost.gcc: $(ISRC) | $(OUT)
	$(CC_GCC) $(CFLAGS) -o $@ $<
$(OUT)/isacost.clang: $(ISRC) | $(OUT)
	$(CC_CLANG) $(CFLAGS) -o $@ $<
$(OUT)/isacost.asan: $(ISRC) | $(OUT)
	$(CC_CLANG) -O1 -g -std=gnu11 -fsanitize=address,undefined -fno-omit-frame-pointer -o $@ $<
# the declared-ISA TU: same source, whole TU built for x86-64-v3 (Linux)
$(OUT)/isacost-v3.gcc: $(ISRC) | $(OUT)
	$(CC_GCC) $(CFLAGS) -march=x86-64-v3 -o $@ $<
$(OUT)/isacost-v3.clang: $(ISRC) | $(OUT)
	$(CC_CLANG) $(CFLAGS) -march=x86-64-v3 -o $@ $<
check-isa: $(OUT)/isacost.gcc $(OUT)/isacost.clang
	$(OUT)/isacost.gcc --check
	$(OUT)/isacost.clang --check
check-asan-isa: $(OUT)/isacost.asan
	$(OUT)/isacost.asan --check
run-isa: $(OUT)/isacost.gcc $(OUT)/isacost.clang
	$(OUT)/isacost.gcc --isa-report; $(OUT)/isacost.gcc
	$(OUT)/isacost.clang --isa-report; $(OUT)/isacost.clang
asm-isa: $(ISRC) | $(OUT)
	$(CC_GCC) $(CFLAGS) -S -o $(OUT)/isacost.gcc.s $<
	$(CC_CLANG) $(CFLAGS) -S -o $(OUT)/isacost.clang.s $<
# Mac compile-check of the x86 paths (ELF: ifunc + target_clones; Mach-O:
# neither). Borrows the macOS SDK's headers for the ELF triple: syntax and
# codegen only, never linked or run.
SDK = $(shell xcrun --show-sdk-path 2>/dev/null)
compile-x86: $(ISRC) | $(OUT)
	for m in x86-64 x86-64-v3 x86-64-v4; do \
	  $(CC_CLANG) -target x86_64-linux-gnu -march=$$m $(CFLAGS) -isystem $(SDK)/usr/include -c -o $(OUT)/isacost.elf.$$m.o $< || exit 1; \
	  $(CC_CLANG) -target x86_64-apple-macos13 -march=$$m $(CFLAGS) -c -o $(OUT)/isacost.macho.$$m.o $< || exit 1; \
	done
	$(CC_CLANG) -target x86_64-linux-gnu $(CFLAGS) -isystem $(SDK)/usr/include -c -o $(OUT)/isanote.elf.o $(NSRC)
	@echo "compile-x86: isacost.c x86-64/v3/v4 ELF+Mach-O and isanote.c ELF compile clean"
# Linux x86 only: what the loader enforces about an x86 ISA-level marker.
isanote: $(NSRC) | $(OUT)
	sh docs/design/memfn/probes/isanote.sh $(OUT) $(CC_GCC)
.PHONY: check check-asan run asm check-isa check-asan-isa run-isa asm-isa compile-x86 isanote
