	.build_version macos, 26, 0	sdk_version 26, 5
	.section	__TEXT,__text,regular,pure_instructions
	.globl	_cmp_memcmp_1                   ## -- Begin function cmp_memcmp_1
	.p2align	4
_cmp_memcmp_1:                          ## @cmp_memcmp_1
	.cfi_startproc
## %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	leaq	1(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB0_2
## %bb.1:
	xorl	%eax, %eax
	cmpb	$97, (%rdi,%rsi)
	sete	%al
LBB0_2:
	popq	%rbp
	retq
	.cfi_endproc
                                        ## -- End function
	.globl	_cmp_memcmp_2                   ## -- Begin function cmp_memcmp_2
	.p2align	4
_cmp_memcmp_2:                          ## @cmp_memcmp_2
	.cfi_startproc
## %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	leaq	2(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB1_2
## %bb.1:
	xorl	%eax, %eax
	cmpw	$25185, (%rdi,%rsi)             ## imm = 0x6261
	sete	%al
LBB1_2:
	popq	%rbp
	retq
	.cfi_endproc
                                        ## -- End function
	.globl	_cmp_memcmp_3                   ## -- Begin function cmp_memcmp_3
	.p2align	4
_cmp_memcmp_3:                          ## @cmp_memcmp_3
	.cfi_startproc
## %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	leaq	3(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB2_2
## %bb.1:
	movzwl	(%rdi,%rsi), %ecx
	xorl	$25185, %ecx                    ## imm = 0x6261
	movzbl	2(%rdi,%rsi), %edx
	xorl	$99, %edx
	xorl	%eax, %eax
	orw	%cx, %dx
	sete	%al
LBB2_2:
	popq	%rbp
	retq
	.cfi_endproc
                                        ## -- End function
	.globl	_cmp_memcmp_4                   ## -- Begin function cmp_memcmp_4
	.p2align	4
_cmp_memcmp_4:                          ## @cmp_memcmp_4
	.cfi_startproc
## %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	leaq	4(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB3_2
## %bb.1:
	xorl	%eax, %eax
	cmpl	$1684234849, (%rdi,%rsi)        ## imm = 0x64636261
	sete	%al
LBB3_2:
	popq	%rbp
	retq
	.cfi_endproc
                                        ## -- End function
	.globl	_cmp_memcmp_5                   ## -- Begin function cmp_memcmp_5
	.p2align	4
_cmp_memcmp_5:                          ## @cmp_memcmp_5
	.cfi_startproc
## %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	leaq	5(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB4_2
## %bb.1:
	movl	$1684234849, %ecx               ## imm = 0x64636261
	xorl	(%rdi,%rsi), %ecx
	movzbl	4(%rdi,%rsi), %edx
	xorl	$101, %edx
	xorl	%eax, %eax
	orl	%ecx, %edx
	sete	%al
LBB4_2:
	popq	%rbp
	retq
	.cfi_endproc
                                        ## -- End function
	.globl	_cmp_memcmp_6                   ## -- Begin function cmp_memcmp_6
	.p2align	4
_cmp_memcmp_6:                          ## @cmp_memcmp_6
	.cfi_startproc
## %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	leaq	6(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB5_2
## %bb.1:
	movl	$1684234849, %ecx               ## imm = 0x64636261
	xorl	(%rdi,%rsi), %ecx
	movzwl	4(%rdi,%rsi), %edx
	xorl	$26213, %edx                    ## imm = 0x6665
	xorl	%eax, %eax
	orl	%ecx, %edx
	sete	%al
LBB5_2:
	popq	%rbp
	retq
	.cfi_endproc
                                        ## -- End function
	.globl	_cmp_memcmp_7                   ## -- Begin function cmp_memcmp_7
	.p2align	4
_cmp_memcmp_7:                          ## @cmp_memcmp_7
	.cfi_startproc
## %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	leaq	7(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB6_2
## %bb.1:
	movl	$1684234849, %ecx               ## imm = 0x64636261
	xorl	(%rdi,%rsi), %ecx
	movl	$1734763876, %edx               ## imm = 0x67666564
	xorl	3(%rdi,%rsi), %edx
	xorl	%eax, %eax
	orl	%ecx, %edx
	sete	%al
LBB6_2:
	popq	%rbp
	retq
	.cfi_endproc
                                        ## -- End function
	.globl	_cmp_memcmp_8                   ## -- Begin function cmp_memcmp_8
	.p2align	4
_cmp_memcmp_8:                          ## @cmp_memcmp_8
	.cfi_startproc
## %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	leaq	8(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB7_2
## %bb.1:
	movabsq	$7523094288207667809, %rcx      ## imm = 0x6867666564636261
	xorl	%eax, %eax
	cmpq	%rcx, (%rdi,%rsi)
	sete	%al
LBB7_2:
	popq	%rbp
	retq
	.cfi_endproc
                                        ## -- End function
	.globl	_cmp_memcmp_9                   ## -- Begin function cmp_memcmp_9
	.p2align	4
_cmp_memcmp_9:                          ## @cmp_memcmp_9
	.cfi_startproc
## %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	leaq	9(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB8_2
## %bb.1:
	movabsq	$7523094288207667809, %rcx      ## imm = 0x6867666564636261
	xorq	(%rdi,%rsi), %rcx
	movzbl	8(%rdi,%rsi), %edx
	xorq	$105, %rdx
	xorl	%eax, %eax
	orq	%rcx, %rdx
	sete	%al
LBB8_2:
	popq	%rbp
	retq
	.cfi_endproc
                                        ## -- End function
	.globl	_cmp_memcmp_10                  ## -- Begin function cmp_memcmp_10
	.p2align	4
_cmp_memcmp_10:                         ## @cmp_memcmp_10
	.cfi_startproc
## %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	leaq	10(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB9_2
## %bb.1:
	movabsq	$7523094288207667809, %rcx      ## imm = 0x6867666564636261
	xorq	(%rdi,%rsi), %rcx
	movzwl	8(%rdi,%rsi), %edx
	xorq	$27241, %rdx                    ## imm = 0x6A69
	xorl	%eax, %eax
	orq	%rcx, %rdx
	sete	%al
LBB9_2:
	popq	%rbp
	retq
	.cfi_endproc
                                        ## -- End function
	.globl	_cmp_memcmp_11                  ## -- Begin function cmp_memcmp_11
	.p2align	4
_cmp_memcmp_11:                         ## @cmp_memcmp_11
	.cfi_startproc
## %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	leaq	11(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB10_2
## %bb.1:
	movabsq	$7523094288207667809, %rcx      ## imm = 0x6867666564636261
	xorq	(%rdi,%rsi), %rcx
	movabsq	$7740114806721897828, %rdx      ## imm = 0x6B6A696867666564
	xorq	3(%rdi,%rsi), %rdx
	xorl	%eax, %eax
	orq	%rcx, %rdx
	sete	%al
LBB10_2:
	popq	%rbp
	retq
	.cfi_endproc
                                        ## -- End function
	.globl	_cmp_memcmp_12                  ## -- Begin function cmp_memcmp_12
	.p2align	4
_cmp_memcmp_12:                         ## @cmp_memcmp_12
	.cfi_startproc
## %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	leaq	12(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB11_2
## %bb.1:
	movabsq	$7523094288207667809, %rcx      ## imm = 0x6867666564636261
	xorq	(%rdi,%rsi), %rcx
	movl	8(%rdi,%rsi), %edx
	xorq	$1818978921, %rdx               ## imm = 0x6C6B6A69
	xorl	%eax, %eax
	orq	%rcx, %rdx
	sete	%al
LBB11_2:
	popq	%rbp
	retq
	.cfi_endproc
                                        ## -- End function
	.globl	_cmp_memcmp_13                  ## -- Begin function cmp_memcmp_13
	.p2align	4
_cmp_memcmp_13:                         ## @cmp_memcmp_13
	.cfi_startproc
## %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	leaq	13(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB12_2
## %bb.1:
	movabsq	$7523094288207667809, %rcx      ## imm = 0x6867666564636261
	xorq	(%rdi,%rsi), %rcx
	movabsq	$7884795152398051174, %rdx      ## imm = 0x6D6C6B6A69686766
	xorq	5(%rdi,%rsi), %rdx
	xorl	%eax, %eax
	orq	%rcx, %rdx
	sete	%al
LBB12_2:
	popq	%rbp
	retq
	.cfi_endproc
                                        ## -- End function
	.globl	_cmp_memcmp_14                  ## -- Begin function cmp_memcmp_14
	.p2align	4
_cmp_memcmp_14:                         ## @cmp_memcmp_14
	.cfi_startproc
## %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	leaq	14(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB13_2
## %bb.1:
	movabsq	$7523094288207667809, %rcx      ## imm = 0x6867666564636261
	xorq	(%rdi,%rsi), %rcx
	movabsq	$7957135325236127847, %rdx      ## imm = 0x6E6D6C6B6A696867
	xorq	6(%rdi,%rsi), %rdx
	xorl	%eax, %eax
	orq	%rcx, %rdx
	sete	%al
LBB13_2:
	popq	%rbp
	retq
	.cfi_endproc
                                        ## -- End function
	.globl	_cmp_memcmp_15                  ## -- Begin function cmp_memcmp_15
	.p2align	4
_cmp_memcmp_15:                         ## @cmp_memcmp_15
	.cfi_startproc
## %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	leaq	15(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB14_2
## %bb.1:
	movabsq	$7523094288207667809, %rcx      ## imm = 0x6867666564636261
	xorq	(%rdi,%rsi), %rcx
	movabsq	$8029475498074204520, %rdx      ## imm = 0x6F6E6D6C6B6A6968
	xorq	7(%rdi,%rsi), %rdx
	xorl	%eax, %eax
	orq	%rcx, %rdx
	sete	%al
LBB14_2:
	popq	%rbp
	retq
	.cfi_endproc
                                        ## -- End function
	.section	__TEXT,__literal16,16byte_literals
	.p2align	4, 0x0                          ## -- Begin function cmp_memcmp_16
LCPI15_0:
	.byte	97                              ## 0x61
	.byte	98                              ## 0x62
	.byte	99                              ## 0x63
	.byte	100                             ## 0x64
	.byte	101                             ## 0x65
	.byte	102                             ## 0x66
	.byte	103                             ## 0x67
	.byte	104                             ## 0x68
	.byte	105                             ## 0x69
	.byte	106                             ## 0x6a
	.byte	107                             ## 0x6b
	.byte	108                             ## 0x6c
	.byte	109                             ## 0x6d
	.byte	110                             ## 0x6e
	.byte	111                             ## 0x6f
	.byte	112                             ## 0x70
	.section	__TEXT,__text,regular,pure_instructions
	.globl	_cmp_memcmp_16
	.p2align	4
_cmp_memcmp_16:                         ## @cmp_memcmp_16
	.cfi_startproc
## %bb.0:
	leaq	16(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB15_2
## %bb.1:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	movdqu	(%rdi,%rsi), %xmm0
	pxor	LCPI15_0(%rip), %xmm0
	xorl	%eax, %eax
	ptest	%xmm0, %xmm0
	sete	%al
	popq	%rbp
LBB15_2:
	retq
	.cfi_endproc
                                        ## -- End function
	.section	__TEXT,__literal16,16byte_literals
	.p2align	4, 0x0                          ## -- Begin function cmp_memcmp_17
LCPI16_0:
	.byte	97                              ## 0x61
	.byte	98                              ## 0x62
	.byte	99                              ## 0x63
	.byte	100                             ## 0x64
	.byte	101                             ## 0x65
	.byte	102                             ## 0x66
	.byte	103                             ## 0x67
	.byte	104                             ## 0x68
	.byte	105                             ## 0x69
	.byte	106                             ## 0x6a
	.byte	107                             ## 0x6b
	.byte	108                             ## 0x6c
	.byte	109                             ## 0x6d
	.byte	110                             ## 0x6e
	.byte	111                             ## 0x6f
	.byte	112                             ## 0x70
LCPI16_1:
	.long	113                             ## 0x71
	.long	0                               ## 0x0
	.long	0                               ## 0x0
	.long	0                               ## 0x0
	.section	__TEXT,__text,regular,pure_instructions
	.globl	_cmp_memcmp_17
	.p2align	4
_cmp_memcmp_17:                         ## @cmp_memcmp_17
	.cfi_startproc
## %bb.0:
	leaq	17(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB16_2
## %bb.1:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	movdqu	(%rdi,%rsi), %xmm0
	movzbl	16(%rdi,%rsi), %eax
	pxor	LCPI16_0(%rip), %xmm0
	movd	%eax, %xmm1
	pxor	LCPI16_1(%rip), %xmm1
	por	%xmm0, %xmm1
	xorl	%eax, %eax
	ptest	%xmm1, %xmm1
	sete	%al
	popq	%rbp
LBB16_2:
	retq
	.cfi_endproc
                                        ## -- End function
	.section	__TEXT,__literal16,16byte_literals
	.p2align	4, 0x0                          ## -- Begin function cmp_memcmp_20
LCPI17_0:
	.byte	113                             ## 0x71
	.byte	114                             ## 0x72
	.byte	115                             ## 0x73
	.byte	116                             ## 0x74
	.byte	0                               ## 0x0
	.byte	0                               ## 0x0
	.byte	0                               ## 0x0
	.byte	0                               ## 0x0
	.byte	0                               ## 0x0
	.byte	0                               ## 0x0
	.byte	0                               ## 0x0
	.byte	0                               ## 0x0
	.byte	0                               ## 0x0
	.byte	0                               ## 0x0
	.byte	0                               ## 0x0
	.byte	0                               ## 0x0
LCPI17_1:
	.byte	97                              ## 0x61
	.byte	98                              ## 0x62
	.byte	99                              ## 0x63
	.byte	100                             ## 0x64
	.byte	101                             ## 0x65
	.byte	102                             ## 0x66
	.byte	103                             ## 0x67
	.byte	104                             ## 0x68
	.byte	105                             ## 0x69
	.byte	106                             ## 0x6a
	.byte	107                             ## 0x6b
	.byte	108                             ## 0x6c
	.byte	109                             ## 0x6d
	.byte	110                             ## 0x6e
	.byte	111                             ## 0x6f
	.byte	112                             ## 0x70
	.section	__TEXT,__text,regular,pure_instructions
	.globl	_cmp_memcmp_20
	.p2align	4
_cmp_memcmp_20:                         ## @cmp_memcmp_20
	.cfi_startproc
## %bb.0:
	leaq	20(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB17_2
## %bb.1:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	movd	16(%rdi,%rsi), %xmm0            ## xmm0 = mem[0],zero,zero,zero
	pxor	LCPI17_0(%rip), %xmm0
	movdqu	(%rdi,%rsi), %xmm1
	pxor	LCPI17_1(%rip), %xmm1
	por	%xmm0, %xmm1
	xorl	%eax, %eax
	ptest	%xmm1, %xmm1
	sete	%al
	popq	%rbp
LBB17_2:
	retq
	.cfi_endproc
                                        ## -- End function
	.section	__TEXT,__literal16,16byte_literals
	.p2align	4, 0x0                          ## -- Begin function cmp_memcmp_24
LCPI18_0:
	.byte	113                             ## 0x71
	.byte	114                             ## 0x72
	.byte	115                             ## 0x73
	.byte	116                             ## 0x74
	.byte	117                             ## 0x75
	.byte	118                             ## 0x76
	.byte	119                             ## 0x77
	.byte	120                             ## 0x78
	.byte	0                               ## 0x0
	.byte	0                               ## 0x0
	.byte	0                               ## 0x0
	.byte	0                               ## 0x0
	.byte	0                               ## 0x0
	.byte	0                               ## 0x0
	.byte	0                               ## 0x0
	.byte	0                               ## 0x0
LCPI18_1:
	.byte	97                              ## 0x61
	.byte	98                              ## 0x62
	.byte	99                              ## 0x63
	.byte	100                             ## 0x64
	.byte	101                             ## 0x65
	.byte	102                             ## 0x66
	.byte	103                             ## 0x67
	.byte	104                             ## 0x68
	.byte	105                             ## 0x69
	.byte	106                             ## 0x6a
	.byte	107                             ## 0x6b
	.byte	108                             ## 0x6c
	.byte	109                             ## 0x6d
	.byte	110                             ## 0x6e
	.byte	111                             ## 0x6f
	.byte	112                             ## 0x70
	.section	__TEXT,__text,regular,pure_instructions
	.globl	_cmp_memcmp_24
	.p2align	4
_cmp_memcmp_24:                         ## @cmp_memcmp_24
	.cfi_startproc
## %bb.0:
	leaq	24(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB18_2
## %bb.1:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	movq	16(%rdi,%rsi), %xmm0            ## xmm0 = mem[0],zero
	pxor	LCPI18_0(%rip), %xmm0
	movdqu	(%rdi,%rsi), %xmm1
	pxor	LCPI18_1(%rip), %xmm1
	por	%xmm0, %xmm1
	xorl	%eax, %eax
	ptest	%xmm1, %xmm1
	sete	%al
	popq	%rbp
LBB18_2:
	retq
	.cfi_endproc
                                        ## -- End function
	.section	__TEXT,__literal16,16byte_literals
	.p2align	4, 0x0                          ## -- Begin function cmp_memcmp_31
LCPI19_0:
	.byte	112                             ## 0x70
	.byte	113                             ## 0x71
	.byte	114                             ## 0x72
	.byte	115                             ## 0x73
	.byte	116                             ## 0x74
	.byte	117                             ## 0x75
	.byte	118                             ## 0x76
	.byte	119                             ## 0x77
	.byte	120                             ## 0x78
	.byte	121                             ## 0x79
	.byte	122                             ## 0x7a
	.byte	65                              ## 0x41
	.byte	66                              ## 0x42
	.byte	67                              ## 0x43
	.byte	68                              ## 0x44
	.byte	69                              ## 0x45
LCPI19_1:
	.byte	97                              ## 0x61
	.byte	98                              ## 0x62
	.byte	99                              ## 0x63
	.byte	100                             ## 0x64
	.byte	101                             ## 0x65
	.byte	102                             ## 0x66
	.byte	103                             ## 0x67
	.byte	104                             ## 0x68
	.byte	105                             ## 0x69
	.byte	106                             ## 0x6a
	.byte	107                             ## 0x6b
	.byte	108                             ## 0x6c
	.byte	109                             ## 0x6d
	.byte	110                             ## 0x6e
	.byte	111                             ## 0x6f
	.byte	112                             ## 0x70
	.section	__TEXT,__text,regular,pure_instructions
	.globl	_cmp_memcmp_31
	.p2align	4
_cmp_memcmp_31:                         ## @cmp_memcmp_31
	.cfi_startproc
## %bb.0:
	leaq	31(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB19_2
## %bb.1:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	movdqu	15(%rdi,%rsi), %xmm0
	pxor	LCPI19_0(%rip), %xmm0
	movdqu	(%rdi,%rsi), %xmm1
	pxor	LCPI19_1(%rip), %xmm1
	por	%xmm0, %xmm1
	xorl	%eax, %eax
	ptest	%xmm1, %xmm1
	sete	%al
	popq	%rbp
LBB19_2:
	retq
	.cfi_endproc
                                        ## -- End function
	.section	__TEXT,__literal16,16byte_literals
	.p2align	4, 0x0                          ## -- Begin function cmp_memcmp_32
LCPI20_0:
	.byte	113                             ## 0x71
	.byte	114                             ## 0x72
	.byte	115                             ## 0x73
	.byte	116                             ## 0x74
	.byte	117                             ## 0x75
	.byte	118                             ## 0x76
	.byte	119                             ## 0x77
	.byte	120                             ## 0x78
	.byte	121                             ## 0x79
	.byte	122                             ## 0x7a
	.byte	65                              ## 0x41
	.byte	66                              ## 0x42
	.byte	67                              ## 0x43
	.byte	68                              ## 0x44
	.byte	69                              ## 0x45
	.byte	70                              ## 0x46
LCPI20_1:
	.byte	97                              ## 0x61
	.byte	98                              ## 0x62
	.byte	99                              ## 0x63
	.byte	100                             ## 0x64
	.byte	101                             ## 0x65
	.byte	102                             ## 0x66
	.byte	103                             ## 0x67
	.byte	104                             ## 0x68
	.byte	105                             ## 0x69
	.byte	106                             ## 0x6a
	.byte	107                             ## 0x6b
	.byte	108                             ## 0x6c
	.byte	109                             ## 0x6d
	.byte	110                             ## 0x6e
	.byte	111                             ## 0x6f
	.byte	112                             ## 0x70
	.section	__TEXT,__text,regular,pure_instructions
	.globl	_cmp_memcmp_32
	.p2align	4
_cmp_memcmp_32:                         ## @cmp_memcmp_32
	.cfi_startproc
## %bb.0:
	leaq	32(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB20_2
## %bb.1:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	movdqu	16(%rdi,%rsi), %xmm0
	pxor	LCPI20_0(%rip), %xmm0
	movdqu	(%rdi,%rsi), %xmm1
	pxor	LCPI20_1(%rip), %xmm1
	por	%xmm0, %xmm1
	xorl	%eax, %eax
	ptest	%xmm1, %xmm1
	sete	%al
	popq	%rbp
LBB20_2:
	retq
	.cfi_endproc
                                        ## -- End function
	.globl	_cmp_memcmp_33                  ## -- Begin function cmp_memcmp_33
	.p2align	4
_cmp_memcmp_33:                         ## @cmp_memcmp_33
	.cfi_startproc
## %bb.0:
	leaq	33(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB21_2
## %bb.1:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	addq	%rsi, %rdi
	leaq	L_.str.21(%rip), %rsi
	movl	$33, %edx
	callq	_memcmp
	movl	%eax, %ecx
	xorl	%eax, %eax
	testl	%ecx, %ecx
	sete	%al
	popq	%rbp
LBB21_2:
	retq
	.cfi_endproc
                                        ## -- End function
	.globl	_cmp_memcmp_40                  ## -- Begin function cmp_memcmp_40
	.p2align	4
_cmp_memcmp_40:                         ## @cmp_memcmp_40
	.cfi_startproc
## %bb.0:
	leaq	40(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB22_2
## %bb.1:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	addq	%rsi, %rdi
	leaq	L_.str.22(%rip), %rsi
	movl	$40, %edx
	callq	_memcmp
	movl	%eax, %ecx
	xorl	%eax, %eax
	testl	%ecx, %ecx
	sete	%al
	popq	%rbp
LBB22_2:
	retq
	.cfi_endproc
                                        ## -- End function
	.globl	_cmp_memcmp_48                  ## -- Begin function cmp_memcmp_48
	.p2align	4
_cmp_memcmp_48:                         ## @cmp_memcmp_48
	.cfi_startproc
## %bb.0:
	leaq	48(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB23_2
## %bb.1:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	addq	%rsi, %rdi
	leaq	L_.str.23(%rip), %rsi
	movl	$48, %edx
	callq	_memcmp
	movl	%eax, %ecx
	xorl	%eax, %eax
	testl	%ecx, %ecx
	sete	%al
	popq	%rbp
LBB23_2:
	retq
	.cfi_endproc
                                        ## -- End function
	.globl	_cmp_memcmp_64                  ## -- Begin function cmp_memcmp_64
	.p2align	4
_cmp_memcmp_64:                         ## @cmp_memcmp_64
	.cfi_startproc
## %bb.0:
	leaq	64(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB24_2
## %bb.1:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	addq	%rsi, %rdi
	leaq	L_.str.24(%rip), %rsi
	movl	$64, %edx
	callq	_memcmp
	movl	%eax, %ecx
	xorl	%eax, %eax
	testl	%ecx, %ecx
	sete	%al
	popq	%rbp
LBB24_2:
	retq
	.cfi_endproc
                                        ## -- End function
	.globl	_cmp_mask_1                     ## -- Begin function cmp_mask_1
	.p2align	4
_cmp_mask_1:                            ## @cmp_mask_1
	.cfi_startproc
## %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	leaq	4(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB25_2
## %bb.1:
	xorl	%eax, %eax
	cmpb	$97, (%rdi,%rsi)
	sete	%al
LBB25_2:
	popq	%rbp
	retq
	.cfi_endproc
                                        ## -- End function
	.globl	_cmp_mask_2                     ## -- Begin function cmp_mask_2
	.p2align	4
_cmp_mask_2:                            ## @cmp_mask_2
	.cfi_startproc
## %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	leaq	4(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB26_2
## %bb.1:
	xorl	%eax, %eax
	cmpw	$25185, (%rdi,%rsi)             ## imm = 0x6261
	sete	%al
LBB26_2:
	popq	%rbp
	retq
	.cfi_endproc
                                        ## -- End function
	.globl	_cmp_mask_3                     ## -- Begin function cmp_mask_3
	.p2align	4
_cmp_mask_3:                            ## @cmp_mask_3
	.cfi_startproc
## %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	leaq	4(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB27_2
## %bb.1:
	movl	$16777215, %ecx                 ## imm = 0xFFFFFF
	andl	(%rdi,%rsi), %ecx
	xorl	%eax, %eax
	cmpl	$6513249, %ecx                  ## imm = 0x636261
	sete	%al
LBB27_2:
	popq	%rbp
	retq
	.cfi_endproc
                                        ## -- End function
	.globl	_cmp_mask_4                     ## -- Begin function cmp_mask_4
	.p2align	4
_cmp_mask_4:                            ## @cmp_mask_4
	.cfi_startproc
## %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	leaq	4(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB28_2
## %bb.1:
	xorl	%eax, %eax
	cmpl	$1684234849, (%rdi,%rsi)        ## imm = 0x64636261
	sete	%al
LBB28_2:
	popq	%rbp
	retq
	.cfi_endproc
                                        ## -- End function
	.globl	_cmp_mask_5                     ## -- Begin function cmp_mask_5
	.p2align	4
_cmp_mask_5:                            ## @cmp_mask_5
	.cfi_startproc
## %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	leaq	8(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB29_2
## %bb.1:
	movabsq	$1099511627775, %rcx            ## imm = 0xFFFFFFFFFF
	andq	(%rdi,%rsi), %rcx
	movabsq	$435475931745, %rdx             ## imm = 0x6564636261
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	sete	%al
LBB29_2:
	popq	%rbp
	retq
	.cfi_endproc
                                        ## -- End function
	.globl	_cmp_mask_6                     ## -- Begin function cmp_mask_6
	.p2align	4
_cmp_mask_6:                            ## @cmp_mask_6
	.cfi_startproc
## %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	leaq	8(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB30_2
## %bb.1:
	movabsq	$281474976710655, %rcx          ## imm = 0xFFFFFFFFFFFF
	andq	(%rdi,%rsi), %rcx
	movabsq	$112585661964897, %rdx          ## imm = 0x666564636261
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	sete	%al
LBB30_2:
	popq	%rbp
	retq
	.cfi_endproc
                                        ## -- End function
	.globl	_cmp_mask_7                     ## -- Begin function cmp_mask_7
	.p2align	4
_cmp_mask_7:                            ## @cmp_mask_7
	.cfi_startproc
## %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	leaq	8(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB31_2
## %bb.1:
	movabsq	$72057594037927935, %rcx        ## imm = 0xFFFFFFFFFFFFFF
	andq	(%rdi,%rsi), %rcx
	movabsq	$29104508263162465, %rdx        ## imm = 0x67666564636261
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	sete	%al
LBB31_2:
	popq	%rbp
	retq
	.cfi_endproc
                                        ## -- End function
	.globl	_cmp_mask_8                     ## -- Begin function cmp_mask_8
	.p2align	4
_cmp_mask_8:                            ## @cmp_mask_8
	.cfi_startproc
## %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	leaq	8(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB32_2
## %bb.1:
	movabsq	$7523094288207667809, %rcx      ## imm = 0x6867666564636261
	xorl	%eax, %eax
	cmpq	%rcx, (%rdi,%rsi)
	sete	%al
LBB32_2:
	popq	%rbp
	retq
	.cfi_endproc
                                        ## -- End function
	.globl	_cmp_overlap_5                  ## -- Begin function cmp_overlap_5
	.p2align	4
_cmp_overlap_5:                         ## @cmp_overlap_5
	.cfi_startproc
## %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	leaq	5(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB33_2
## %bb.1:
	movl	1(%rdi,%rsi), %ecx
	movl	$1684234849, %edx               ## imm = 0x64636261
	xorl	(%rdi,%rsi), %edx
	xorl	$1701077858, %ecx               ## imm = 0x65646362
	xorl	%eax, %eax
	orl	%edx, %ecx
	sete	%al
LBB33_2:
	popq	%rbp
	retq
	.cfi_endproc
                                        ## -- End function
	.globl	_cmp_overlap_6                  ## -- Begin function cmp_overlap_6
	.p2align	4
_cmp_overlap_6:                         ## @cmp_overlap_6
	.cfi_startproc
## %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	leaq	6(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB34_2
## %bb.1:
	movl	2(%rdi,%rsi), %ecx
	movl	$1684234849, %edx               ## imm = 0x64636261
	xorl	(%rdi,%rsi), %edx
	xorl	$1717920867, %ecx               ## imm = 0x66656463
	xorl	%eax, %eax
	orl	%edx, %ecx
	sete	%al
LBB34_2:
	popq	%rbp
	retq
	.cfi_endproc
                                        ## -- End function
	.globl	_cmp_overlap_7                  ## -- Begin function cmp_overlap_7
	.p2align	4
_cmp_overlap_7:                         ## @cmp_overlap_7
	.cfi_startproc
## %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	leaq	7(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB35_2
## %bb.1:
	movl	3(%rdi,%rsi), %ecx
	movl	$1684234849, %edx               ## imm = 0x64636261
	xorl	(%rdi,%rsi), %edx
	xorl	$1734763876, %ecx               ## imm = 0x67666564
	xorl	%eax, %eax
	orl	%edx, %ecx
	sete	%al
LBB35_2:
	popq	%rbp
	retq
	.cfi_endproc
                                        ## -- End function
	.globl	_cmp_ovmask_3                   ## -- Begin function cmp_ovmask_3
	.p2align	4
_cmp_ovmask_3:                          ## @cmp_ovmask_3
	.cfi_startproc
## %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	leaq	3(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB36_2
## %bb.1:
	movzwl	(%rdi,%rsi), %ecx
	movzwl	1(%rdi,%rsi), %edx
	andl	$-8225, %ecx                    ## imm = 0xDFDF
	xorl	$16961, %ecx                    ## imm = 0x4241
	andl	$-8225, %edx                    ## imm = 0xDFDF
	xorl	$17218, %edx                    ## imm = 0x4342
	xorl	%eax, %eax
	orw	%cx, %dx
	sete	%al
LBB36_2:
	popq	%rbp
	retq
	.cfi_endproc
                                        ## -- End function
	.section	__TEXT,__literal16,16byte_literals
	.p2align	4, 0x0                          ## -- Begin function cmp_ovmask_4
LCPI37_0:
	.short	57311                           ## 0xdfdf
	.short	57311                           ## 0xdfdf
	.space	2
	.space	2
	.space	2
	.space	2
	.space	2
	.space	2
LCPI37_1:
	.short	16961                           ## 0x4241
	.short	17475                           ## 0x4443
	.space	2
	.space	2
	.space	2
	.space	2
	.space	2
	.space	2
	.section	__TEXT,__text,regular,pure_instructions
	.globl	_cmp_ovmask_4
	.p2align	4
_cmp_ovmask_4:                          ## @cmp_ovmask_4
	.cfi_startproc
## %bb.0:
	leaq	4(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB37_2
## %bb.1:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	movd	(%rdi,%rsi), %xmm0              ## xmm0 = mem[0],zero,zero,zero
	pand	LCPI37_0(%rip), %xmm0
	pcmpeqw	LCPI37_1(%rip), %xmm0
	pmovsxwq	%xmm0, %xmm0
	movmskpd	%xmm0, %ecx
	xorl	%eax, %eax
	cmpl	$3, %ecx
	sete	%al
	popq	%rbp
LBB37_2:
	retq
	.cfi_endproc
                                        ## -- End function
	.globl	_cmp_ovmask_5                   ## -- Begin function cmp_ovmask_5
	.p2align	4
_cmp_ovmask_5:                          ## @cmp_ovmask_5
	.cfi_startproc
## %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	leaq	5(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB38_2
## %bb.1:
	movl	1(%rdi,%rsi), %ecx
	movl	$-538976289, %edx               ## imm = 0xDFDFDFDF
	andl	(%rdi,%rsi), %edx
	xorl	$1145258561, %edx               ## imm = 0x44434241
	andl	$-538976289, %ecx               ## imm = 0xDFDFDFDF
	xorl	$1162101570, %ecx               ## imm = 0x45444342
	xorl	%eax, %eax
	orl	%edx, %ecx
	sete	%al
LBB38_2:
	popq	%rbp
	retq
	.cfi_endproc
                                        ## -- End function
	.globl	_cmp_ovmask_6                   ## -- Begin function cmp_ovmask_6
	.p2align	4
_cmp_ovmask_6:                          ## @cmp_ovmask_6
	.cfi_startproc
## %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	leaq	6(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB39_2
## %bb.1:
	movl	2(%rdi,%rsi), %ecx
	movl	$-538976289, %edx               ## imm = 0xDFDFDFDF
	andl	(%rdi,%rsi), %edx
	xorl	$1145258561, %edx               ## imm = 0x44434241
	andl	$-538976289, %ecx               ## imm = 0xDFDFDFDF
	xorl	$1178944579, %ecx               ## imm = 0x46454443
	xorl	%eax, %eax
	orl	%edx, %ecx
	sete	%al
LBB39_2:
	popq	%rbp
	retq
	.cfi_endproc
                                        ## -- End function
	.globl	_cmp_ovmask_7                   ## -- Begin function cmp_ovmask_7
	.p2align	4
_cmp_ovmask_7:                          ## @cmp_ovmask_7
	.cfi_startproc
## %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	leaq	7(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB40_2
## %bb.1:
	movl	3(%rdi,%rsi), %ecx
	movl	$-538976289, %edx               ## imm = 0xDFDFDFDF
	andl	(%rdi,%rsi), %edx
	xorl	$1145258561, %edx               ## imm = 0x44434241
	andl	$-538976289, %ecx               ## imm = 0xDFDFDFDF
	xorl	$1195787588, %ecx               ## imm = 0x47464544
	xorl	%eax, %eax
	orl	%edx, %ecx
	sete	%al
LBB40_2:
	popq	%rbp
	retq
	.cfi_endproc
                                        ## -- End function
	.section	__TEXT,__literal16,16byte_literals
	.p2align	4, 0x0                          ## -- Begin function cmp_ovmask_8
LCPI41_0:
	.long	3755991007                      ## 0xdfdfdfdf
	.long	3755991007                      ## 0xdfdfdfdf
	.space	4
	.space	4
LCPI41_1:
	.long	1145258561                      ## 0x44434241
	.long	1212630597                      ## 0x48474645
	.space	4
	.space	4
	.section	__TEXT,__text,regular,pure_instructions
	.globl	_cmp_ovmask_8
	.p2align	4
_cmp_ovmask_8:                          ## @cmp_ovmask_8
	.cfi_startproc
## %bb.0:
	leaq	8(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB41_2
## %bb.1:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	movq	(%rdi,%rsi), %xmm0              ## xmm0 = mem[0],zero
	pand	LCPI41_0(%rip), %xmm0
	pcmpeqd	LCPI41_1(%rip), %xmm0
	pmovsxdq	%xmm0, %xmm0
	movmskpd	%xmm0, %ecx
	xorl	%eax, %eax
	cmpl	$3, %ecx
	sete	%al
	popq	%rbp
LBB41_2:
	retq
	.cfi_endproc
                                        ## -- End function
	.globl	_cmp_ovmask_9                   ## -- Begin function cmp_ovmask_9
	.p2align	4
_cmp_ovmask_9:                          ## @cmp_ovmask_9
	.cfi_startproc
## %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	leaq	9(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB42_2
## %bb.1:
	movabsq	$-2314885530818453537, %rax     ## imm = 0xDFDFDFDFDFDFDFDF
	movq	(%rdi,%rsi), %rcx
	andq	%rax, %rcx
	movabsq	$5208208757389214273, %rdx      ## imm = 0x4847464544434241
	xorq	%rcx, %rdx
	andq	1(%rdi,%rsi), %rax
	movabsq	$5280548930227290946, %rcx      ## imm = 0x4948474645444342
	xorq	%rax, %rcx
	xorl	%eax, %eax
	orq	%rdx, %rcx
	sete	%al
LBB42_2:
	popq	%rbp
	retq
	.cfi_endproc
                                        ## -- End function
	.globl	_cmp_ovmask_10                  ## -- Begin function cmp_ovmask_10
	.p2align	4
_cmp_ovmask_10:                         ## @cmp_ovmask_10
	.cfi_startproc
## %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	leaq	10(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB43_2
## %bb.1:
	movabsq	$-2314885530818453537, %rax     ## imm = 0xDFDFDFDFDFDFDFDF
	movq	(%rdi,%rsi), %rcx
	andq	%rax, %rcx
	movabsq	$5208208757389214273, %rdx      ## imm = 0x4847464544434241
	xorq	%rcx, %rdx
	andq	2(%rdi,%rsi), %rax
	movabsq	$5352889103065367619, %rcx      ## imm = 0x4A49484746454443
	xorq	%rax, %rcx
	xorl	%eax, %eax
	orq	%rdx, %rcx
	sete	%al
LBB43_2:
	popq	%rbp
	retq
	.cfi_endproc
                                        ## -- End function
	.globl	_cmp_ovmask_11                  ## -- Begin function cmp_ovmask_11
	.p2align	4
_cmp_ovmask_11:                         ## @cmp_ovmask_11
	.cfi_startproc
## %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	leaq	11(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB44_2
## %bb.1:
	movabsq	$-2314885530818453537, %rax     ## imm = 0xDFDFDFDFDFDFDFDF
	movq	(%rdi,%rsi), %rcx
	andq	%rax, %rcx
	movabsq	$5208208757389214273, %rdx      ## imm = 0x4847464544434241
	xorq	%rcx, %rdx
	andq	3(%rdi,%rsi), %rax
	movabsq	$5425229275903444292, %rcx      ## imm = 0x4B4A494847464544
	xorq	%rax, %rcx
	xorl	%eax, %eax
	orq	%rdx, %rcx
	sete	%al
LBB44_2:
	popq	%rbp
	retq
	.cfi_endproc
                                        ## -- End function
	.globl	_cmp_ovmask_12                  ## -- Begin function cmp_ovmask_12
	.p2align	4
_cmp_ovmask_12:                         ## @cmp_ovmask_12
	.cfi_startproc
## %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	leaq	12(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB45_2
## %bb.1:
	movabsq	$-2314885530818453537, %rax     ## imm = 0xDFDFDFDFDFDFDFDF
	movq	(%rdi,%rsi), %rcx
	andq	%rax, %rcx
	movabsq	$5208208757389214273, %rdx      ## imm = 0x4847464544434241
	xorq	%rcx, %rdx
	andq	4(%rdi,%rsi), %rax
	movabsq	$5497569448741520965, %rcx      ## imm = 0x4C4B4A4948474645
	xorq	%rax, %rcx
	xorl	%eax, %eax
	orq	%rdx, %rcx
	sete	%al
LBB45_2:
	popq	%rbp
	retq
	.cfi_endproc
                                        ## -- End function
	.globl	_cmp_ovmask_13                  ## -- Begin function cmp_ovmask_13
	.p2align	4
_cmp_ovmask_13:                         ## @cmp_ovmask_13
	.cfi_startproc
## %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	leaq	13(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB46_2
## %bb.1:
	movabsq	$-2314885530818453537, %rax     ## imm = 0xDFDFDFDFDFDFDFDF
	movq	(%rdi,%rsi), %rcx
	andq	%rax, %rcx
	movabsq	$5208208757389214273, %rdx      ## imm = 0x4847464544434241
	xorq	%rcx, %rdx
	andq	5(%rdi,%rsi), %rax
	movabsq	$5569909621579597638, %rcx      ## imm = 0x4D4C4B4A49484746
	xorq	%rax, %rcx
	xorl	%eax, %eax
	orq	%rdx, %rcx
	sete	%al
LBB46_2:
	popq	%rbp
	retq
	.cfi_endproc
                                        ## -- End function
	.globl	_cmp_ovmask_14                  ## -- Begin function cmp_ovmask_14
	.p2align	4
_cmp_ovmask_14:                         ## @cmp_ovmask_14
	.cfi_startproc
## %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	leaq	14(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB47_2
## %bb.1:
	movabsq	$-2314885530818453537, %rax     ## imm = 0xDFDFDFDFDFDFDFDF
	movq	(%rdi,%rsi), %rcx
	andq	%rax, %rcx
	movabsq	$5208208757389214273, %rdx      ## imm = 0x4847464544434241
	xorq	%rcx, %rdx
	andq	6(%rdi,%rsi), %rax
	movabsq	$5642249794417674311, %rcx      ## imm = 0x4E4D4C4B4A494847
	xorq	%rax, %rcx
	xorl	%eax, %eax
	orq	%rdx, %rcx
	sete	%al
LBB47_2:
	popq	%rbp
	retq
	.cfi_endproc
                                        ## -- End function
	.globl	_cmp_ovmask_15                  ## -- Begin function cmp_ovmask_15
	.p2align	4
_cmp_ovmask_15:                         ## @cmp_ovmask_15
	.cfi_startproc
## %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	leaq	15(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB48_2
## %bb.1:
	movabsq	$-2314885530818453537, %rax     ## imm = 0xDFDFDFDFDFDFDFDF
	movq	(%rdi,%rsi), %rcx
	andq	%rax, %rcx
	movabsq	$5208208757389214273, %rdx      ## imm = 0x4847464544434241
	xorq	%rcx, %rdx
	andq	7(%rdi,%rsi), %rax
	movabsq	$5714589967255750984, %rcx      ## imm = 0x4F4E4D4C4B4A4948
	xorq	%rax, %rcx
	xorl	%eax, %eax
	orq	%rdx, %rcx
	sete	%al
LBB48_2:
	popq	%rbp
	retq
	.cfi_endproc
                                        ## -- End function
	.globl	_cmp_ovmask_16                  ## -- Begin function cmp_ovmask_16
	.p2align	4
_cmp_ovmask_16:                         ## @cmp_ovmask_16
	.cfi_startproc
## %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	leaq	16(%rsi), %rcx
	xorl	%eax, %eax
	cmpq	%rdx, %rcx
	ja	LBB49_2
## %bb.1:
	movabsq	$-2314885530818453537, %rax     ## imm = 0xDFDFDFDFDFDFDFDF
	movq	(%rdi,%rsi), %rcx
	andq	%rax, %rcx
	movabsq	$5208208757389214273, %rdx      ## imm = 0x4847464544434241
	xorq	%rcx, %rdx
	andq	8(%rdi,%rsi), %rax
	movabsq	$5786930140093827657, %rcx      ## imm = 0x504F4E4D4C4B4A49
	xorq	%rax, %rcx
	xorl	%eax, %eax
	orq	%rdx, %rcx
	sete	%al
LBB49_2:
	popq	%rbp
	retq
	.cfi_endproc
                                        ## -- End function
	.section	__TEXT,__cstring,cstring_literals
L_.str.1:                               ## @.str.1
	.asciz	"ab"

L_.str.2:                               ## @.str.2
	.asciz	"abc"

L_.str.3:                               ## @.str.3
	.asciz	"abcd"

L_.str.4:                               ## @.str.4
	.asciz	"abcde"

L_.str.5:                               ## @.str.5
	.asciz	"abcdef"

L_.str.6:                               ## @.str.6
	.asciz	"abcdefg"

L_.str.7:                               ## @.str.7
	.asciz	"abcdefgh"

L_.str.8:                               ## @.str.8
	.asciz	"abcdefghi"

L_.str.9:                               ## @.str.9
	.asciz	"abcdefghij"

L_.str.10:                              ## @.str.10
	.asciz	"abcdefghijk"

L_.str.11:                              ## @.str.11
	.asciz	"abcdefghijkl"

L_.str.12:                              ## @.str.12
	.asciz	"abcdefghijklm"

L_.str.13:                              ## @.str.13
	.asciz	"abcdefghijklmn"

L_.str.14:                              ## @.str.14
	.asciz	"abcdefghijklmno"

L_.str.15:                              ## @.str.15
	.asciz	"abcdefghijklmnop"

L_.str.16:                              ## @.str.16
	.asciz	"abcdefghijklmnopq"

L_.str.17:                              ## @.str.17
	.asciz	"abcdefghijklmnopqrst"

L_.str.18:                              ## @.str.18
	.asciz	"abcdefghijklmnopqrstuvwx"

L_.str.19:                              ## @.str.19
	.asciz	"abcdefghijklmnopqrstuvwxyzABCDE"

L_.str.20:                              ## @.str.20
	.asciz	"abcdefghijklmnopqrstuvwxyzABCDEF"

L_.str.21:                              ## @.str.21
	.asciz	"abcdefghijklmnopqrstuvwxyzABCDEFG"

L_.str.22:                              ## @.str.22
	.asciz	"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMN"

L_.str.23:                              ## @.str.23
	.asciz	"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUV"

L_.str.24:                              ## @.str.24
	.asciz	"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789ab"

.subsections_via_symbols
