# studies/pf_know — [PF-KNOW] (D140) measurement study. Never run by the
# top-level make. `make CC=gcc-16` builds the probe against the tree's own
# library (build it first: `make -C ../.. -j4 CC=gcc-16`).
CC ?= gcc-16
ROOT := ../..
OUT ?= /tmp/pf_know

segprobe: segprobe.c $(ROOT)/build/libpcrec.a
	$(CC) -O2 -I$(ROOT)/lib -I$(ROOT)/src -o $@ segprobe.c $(ROOT)/build/libpcrec.a

census: segprobe
	mkdir -p $(OUT)
	PCREC=$(ROOT)/build/pcrec PROBE=$(CURDIR)/segprobe CORPUS=$(ROOT) OUT=$(OUT) \
	  BENCH=$(BENCH) JOBS=4 python3 census.py

clean:
	rm -f segprobe

.PHONY: census clean
