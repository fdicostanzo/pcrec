	.file	"asm_evidence.c"
# GNU C23 (Ubuntu 15.2.0-16ubuntu1) version 15.2.0 (x86_64-linux-gnu)
#	compiled by GNU C version 15.2.0, GMP version 6.3.0, MPFR version 4.2.2, MPC version 1.3.1, isl version isl-0.27-GMP

# GGC heuristics: --param ggc-min-expand=100 --param ggc-min-heapsize=131072
# options passed: -D_FORTIFY_SOURCE=3 -mtune=generic -march=x86-64 -O2 -fasynchronous-unwind-tables -fstack-protector-strong -fstack-clash-protection -fcf-protection -fzero-init-padding-bits=all
	.text
	.p2align 4
	.globl	test_or
	.type	test_or, @function
test_or:
.LFB0:
	.cfi_startproc
	endbr64	
# asm_evidence.c:16: int test_or(unsigned char c) { return c=='a' || c=='A'; }
	andl	$-33, %edi	#, _7
	xorl	%eax, %eax	# _8
	cmpb	$65, %dil	#, _7
	sete	%al	#, _8
# asm_evidence.c:16: int test_or(unsigned char c) { return c=='a' || c=='A'; }
	ret	
	.cfi_endproc
.LFE0:
	.size	test_or, .-test_or
	.p2align 4
	.globl	test_bitor
	.type	test_bitor, @function
test_bitor:
.LFB5:
	.cfi_startproc
	endbr64	
	andl	$-33, %edi	#, _8
	xorl	%eax, %eax	# _2
	cmpb	$65, %dil	#, _8
	sete	%al	#, _2
	ret	
	.cfi_endproc
.LFE5:
	.size	test_bitor, .-test_bitor
	.p2align 4
	.globl	test_fold
	.type	test_fold, @function
test_fold:
.LFB2:
	.cfi_startproc
	endbr64	
# asm_evidence.c:18: int test_fold(unsigned char c) { return (c|0x20)=='a'; }
	orl	$32, %edi	#, _1
	xorl	%eax, %eax	# _2
	cmpb	$97, %dil	#, _1
	sete	%al	#, _2
# asm_evidence.c:18: int test_fold(unsigned char c) { return (c|0x20)=='a'; }
	ret	
	.cfi_endproc
.LFE2:
	.size	test_fold, .-test_fold
	.p2align 4
	.globl	test_nonpair
	.type	test_nonpair, @function
test_nonpair:
.LFB3:
	.cfi_startproc
	endbr64	
# asm_evidence.c:19: int test_nonpair(unsigned char c) { return c=='a' || c=='z'; }
	cmpb	$97, %dil	#, c
	sete	%al	#, _1
# asm_evidence.c:19: int test_nonpair(unsigned char c) { return c=='a' || c=='z'; }
	cmpb	$122, %dil	#, c
	sete	%dl	#, _2
# asm_evidence.c:19: int test_nonpair(unsigned char c) { return c=='a' || c=='z'; }
	orl	%edx, %eax	# _2, _3
	movzbl	%al, %eax	# _3, _5
# asm_evidence.c:19: int test_nonpair(unsigned char c) { return c=='a' || c=='z'; }
	ret	
	.cfi_endproc
.LFE3:
	.size	test_nonpair, .-test_nonpair
	.ident	"GCC: (Ubuntu 15.2.0-16ubuntu1) 15.2.0"
	.section	.note.GNU-stack,"",@progbits
	.section	.note.gnu.property,"a"
	.align 8
	.long	1f - 0f
	.long	4f - 1f
	.long	5
0:
	.string	"GNU"
1:
	.align 8
	.long	0xc0000002
	.long	3f - 2f
2:
	.long	0x3
3:
	.align 8
4:
