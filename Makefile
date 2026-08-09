# pcrec — GNU make build (see docs/decisions.md D2).
# Targets: all (default), test, clean.

CC      ?= gcc
CFLAGS  ?= -O2 -g
WARN     = -Wall -Wextra
ALLFLAGS = $(CFLAGS) $(WARN) -std=gnu11 -Ilib -Isrc

LIBSRCS := $(wildcard src/core/*.c) $(wildcard src/parse/*.c) \
           $(wildcard src/ir/*.c) $(wildcard src/opt/*.c) \
           $(wildcard src/gen/*.c)
LIBOBJS := $(patsubst src/%.c,build/obj/%.o,$(LIBSRCS))

all: build/pcrec build/libpcrec.a

build/obj/%.o: src/%.c src/core/internal.h lib/pcrec.h
	@mkdir -p $(dir $@)
	$(CC) $(ALLFLAGS) -c -o $@ $<

build/libpcrec.a: $(LIBOBJS)
	ar rcs $@ $^

build/pcrec: cli/main.c build/libpcrec.a lib/pcrec.h
	@mkdir -p build
	$(CC) $(ALLFLAGS) -o $@ cli/main.c build/libpcrec.a

test: all
	bash tests/harness/run.sh
	bash tests/cli/run_cli_tests.sh
	bash tests/reject/run_reject_tests.sh
	bash tests/registry/run_registry_tests.sh
	bash tests/codegen/run_codegen_tests.sh
	bash tests/codegen/run_trie_identity.sh
	bash tests/known_fail/run_known_fail.sh

bench: all
	bash tests/bench/run_bench.sh

fuzz: all
	python3 tests/fuzz/fuzz.py

clean:
	rm -rf build

.PHONY: all test bench fuzz clean
