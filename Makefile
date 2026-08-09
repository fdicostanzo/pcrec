# pcrec — GNU make build (see docs/decisions.md D2).
# Targets: all (default), test, clean.

CC      ?= gcc
CFLAGS  ?= -O2 -g
WARN     = -Wall -Wextra
ALLFLAGS = $(CFLAGS) $(WARN) -std=gnu11 -Ilib -Isrc

LIBSRCS := $(wildcard src/core/*.c) $(wildcard src/parse/*.c) \
           $(wildcard src/ir/*.c) $(wildcard src/gen/*.c)
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

clean:
	rm -rf build

.PHONY: all test clean
