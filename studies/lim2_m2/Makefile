# `CC ?= gcc-16` DOES NOT WORK: make defines CC itself, so `?=` never fires
# and every target silently builds with `cc` -- see [CC-ORIGIN],
# docs/dev/plan.md, and studies/lim2_m1/Makefile's own copy of this comment.
ifeq ($(origin CC),default)
CC := gcc-16
endif
CFLAGS ?= -O1 -g -std=gnu11 -Wall -Wextra
ROOT := ../..
LIB  := $(ROOT)/build/libpcrec.a

.PHONY: all clean

all: lim2_m2

$(LIB):
	@echo "build/libpcrec.a not found -- run 'make CC=gcc-16' in the repo root first" >&2
	@exit 1

lim2_m2: lim2_m2.c $(LIB)
	$(CC) $(CFLAGS) -I $(ROOT)/lib -I $(ROOT)/src -o $@ lim2_m2.c $(LIB) -lm

clean:
	rm -f lim2_m2
