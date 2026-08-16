CC ?= cc
CFLAGS ?= -O3 -g -std=gnu11 -Wall -Wextra -mavx2

ifeq ($(WERROR),1)
CFLAGS += -Werror
endif

SRC = harness.c pattern.c candidates.c cand_gen.c \
      cand_scalar.c cand_avx2_bcast.c cand_avx2_firstlast.c \
      cand_range.c cand_shufti.c cand_alt.c cand_alt_pf.c cand_sse.c \
      cand_rare.c cand_shiftand.c cand_teddy.c cand_prefetch.c
OBJ = $(SRC:.c=.o)

.PHONY: all check bench clean distclean

all: harness

harness: $(OBJ)
	$(CC) $(CFLAGS) -o $@ $(OBJ)

%.o: %.c matcher.h pattern.h
	$(CC) $(CFLAGS) -c -o $@ $<

cand_gen.o: bcast_gen.h

# Honest SSE tier: strip AVX so any 256-bit intrinsic is a compile error,
# cap at SSSE3 (shufti); early exits use movemask, keeping SSE2+SSSE3 only.
cand_sse.o: CFLAGS += -mno-avx2 -mno-avx -mssse3

check: harness
	./harness --no-bench

coldmap: coldmap.o cand_rare.o cand_prefetch.o
	$(CC) $(CFLAGS) -o $@ coldmap.o cand_rare.o cand_prefetch.o

findall: findall.o cand_findall.o
	$(CC) $(CFLAGS) -o $@ findall.o cand_findall.o

# Self-contained: copy runext.c to any Linux/x86-64 box and build with
#   cc -O3 -mavx2 -std=gnu11 -Wall -Wextra -o runext runext.c
runext: runext.c
	$(CC) $(CFLAGS) -o $@ runext.c

findall.o cand_findall.o: findall.h

bench: harness
	./harness

clean:
	rm -f harness coldmap findall runext *.o fail_*.bin

# Also removes the 1 GiB cold-cache test file and saved bench outputs.
distclean: clean
	rm -f coldmap.dat *_bench.txt bench_results*.txt
