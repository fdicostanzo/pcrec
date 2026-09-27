	.arch armv8.5-a
	.build_version macos,  26, 0
	.text
	.cstring
	.align	3
l.str.0:
	.ascii "abcdefghijklmnopqrstuvwxy\0"
	.text
	.align	2
	.p2align 5,,15
	.globl _cmp_memcmp_25
_cmp_memcmp_25:
LFB0:
	add	x3, x1, 25
	cmp	x3, x2
	bhi	L5
	adrp	x2, lC1@PAGE
	ldr	q30, [x0, x1]
	add	x3, x0, x1
	ldr	q31, [x2, #lC1@PAGEOFF]
	eor	v30.16b, v30.16b, v31.16b
	umaxp	v30.4s, v30.4s, v30.4s
	fmov	x0, d30
	cbz	x0, L7
L3:
	mov	w0, 1
	eor	w0, w0, 1
L1:
	ret
	.p2align 2,,3
L5:
	mov	w0, 0
	ret
	.p2align 2,,3
L7:
	ldr	x1, [x3, 16]
	mov	x0, 29297
	movk	x0, 0x7473, lsl 16
	movk	x0, 0x7675, lsl 32
	movk	x0, 0x7877, lsl 48
	cmp	x1, x0
	bne	L3
	ldrb	w0, [x3, 24]
	cmp	w0, 121
	bne	L3
	mov	w0, 0
	eor	w0, w0, 1
	b	L1
LFE0:
	.cstring
	.align	3
l.str.2:
	.ascii "abcdefghijklmnopqrstuvwxyz\0"
	.text
	.align	2
	.p2align 5,,15
	.globl _cmp_memcmp_26
_cmp_memcmp_26:
LFB1:
	add	x3, x1, 26
	cmp	x3, x2
	bhi	L12
	adrp	x2, lC1@PAGE
	ldr	q30, [x0, x1]
	add	x3, x0, x1
	ldr	q31, [x2, #lC1@PAGEOFF]
	eor	v30.16b, v30.16b, v31.16b
	umaxp	v30.4s, v30.4s, v30.4s
	fmov	x0, d30
	cbz	x0, L13
L10:
	mov	w0, 1
	eor	w0, w0, 1
L8:
	ret
	.p2align 2,,3
L12:
	mov	w0, 0
	ret
	.p2align 2,,3
L13:
	ldr	x1, [x3, 16]
	mov	x0, 29297
	movk	x0, 0x7473, lsl 16
	movk	x0, 0x7675, lsl 32
	movk	x0, 0x7877, lsl 48
	cmp	x1, x0
	bne	L10
	ldrh	w1, [x3, 24]
	mov	w0, 31353
	cmp	w1, w0
	bne	L10
	mov	w0, 0
	eor	w0, w0, 1
	b	L8
LFE1:
	.cstring
	.align	3
l.str.3:
	.ascii "abcdefghijklmnopqrstuvwxyzA\0"
	.text
	.align	2
	.p2align 5,,15
	.globl _cmp_memcmp_27
_cmp_memcmp_27:
LFB2:
	add	x3, x1, 27
	cmp	x3, x2
	bhi	L18
	adrp	x2, lC1@PAGE
	ldr	q30, [x0, x1]
	add	x3, x0, x1
	ldr	q31, [x2, #lC1@PAGEOFF]
	eor	v30.16b, v30.16b, v31.16b
	umaxp	v30.4s, v30.4s, v30.4s
	fmov	x0, d30
	cbz	x0, L19
L16:
	mov	w0, 1
	eor	w0, w0, 1
L14:
	ret
	.p2align 2,,3
L18:
	mov	w0, 0
	ret
	.p2align 2,,3
L19:
	ldr	x1, [x3, 16]
	mov	x0, 29297
	movk	x0, 0x7473, lsl 16
	movk	x0, 0x7675, lsl 32
	movk	x0, 0x7877, lsl 48
	cmp	x1, x0
	bne	L16
	ldrh	w1, [x3, 24]
	mov	w0, 31353
	cmp	w1, w0
	bne	L16
	ldrb	w0, [x3, 26]
	cmp	w0, 65
	bne	L16
	mov	w0, 0
	eor	w0, w0, 1
	b	L14
LFE2:
	.cstring
	.align	3
l.str.4:
	.ascii "abcdefghijklmnopqrstuvwxyzAB\0"
	.text
	.align	2
	.p2align 5,,15
	.globl _cmp_memcmp_28
_cmp_memcmp_28:
LFB3:
	add	x3, x1, 28
	cmp	x3, x2
	bhi	L24
	adrp	x2, lC1@PAGE
	ldr	q30, [x0, x1]
	add	x3, x0, x1
	ldr	q31, [x2, #lC1@PAGEOFF]
	eor	v30.16b, v30.16b, v31.16b
	umaxp	v30.4s, v30.4s, v30.4s
	fmov	x0, d30
	cbz	x0, L25
L22:
	mov	w0, 1
	eor	w0, w0, 1
L20:
	ret
	.p2align 2,,3
L24:
	mov	w0, 0
	ret
	.p2align 2,,3
L25:
	ldr	x1, [x3, 16]
	mov	x0, 29297
	movk	x0, 0x7473, lsl 16
	movk	x0, 0x7675, lsl 32
	movk	x0, 0x7877, lsl 48
	cmp	x1, x0
	bne	L22
	ldr	w1, [x3, 24]
	mov	w0, 31353
	movk	w0, 0x4241, lsl 16
	cmp	w1, w0
	bne	L22
	mov	w0, 0
	eor	w0, w0, 1
	b	L20
LFE3:
	.cstring
	.align	3
l.str.5:
	.ascii "abcdefghijklmnopqrstuvwxyzABC\0"
	.text
	.align	2
	.p2align 5,,15
	.globl _cmp_memcmp_29
_cmp_memcmp_29:
LFB4:
	add	x3, x1, 29
	cmp	x3, x2
	bhi	L30
	adrp	x2, lC1@PAGE
	ldr	q30, [x0, x1]
	add	x3, x0, x1
	ldr	q31, [x2, #lC1@PAGEOFF]
	eor	v30.16b, v30.16b, v31.16b
	umaxp	v30.4s, v30.4s, v30.4s
	fmov	x0, d30
	cbz	x0, L31
L28:
	mov	w0, 1
	eor	w0, w0, 1
L26:
	ret
	.p2align 2,,3
L30:
	mov	w0, 0
	ret
	.p2align 2,,3
L31:
	ldr	x1, [x3, 16]
	mov	x0, 29297
	movk	x0, 0x7473, lsl 16
	movk	x0, 0x7675, lsl 32
	movk	x0, 0x7877, lsl 48
	cmp	x1, x0
	bne	L28
	ldr	w1, [x3, 24]
	mov	w0, 31353
	movk	w0, 0x4241, lsl 16
	cmp	w1, w0
	bne	L28
	ldrb	w0, [x3, 28]
	cmp	w0, 67
	bne	L28
	mov	w0, 0
	eor	w0, w0, 1
	b	L26
LFE4:
	.cstring
	.align	3
l.str.6:
	.ascii "abcdefghijklmnopqrstuvwxyzABCD\0"
	.text
	.align	2
	.p2align 5,,15
	.globl _cmp_memcmp_30
_cmp_memcmp_30:
LFB5:
	add	x3, x1, 30
	cmp	x3, x2
	bhi	L36
	adrp	x2, lC1@PAGE
	ldr	q30, [x0, x1]
	add	x3, x0, x1
	ldr	q31, [x2, #lC1@PAGEOFF]
	eor	v30.16b, v30.16b, v31.16b
	umaxp	v30.4s, v30.4s, v30.4s
	fmov	x0, d30
	cbz	x0, L37
L34:
	mov	w0, 1
	eor	w0, w0, 1
L32:
	ret
	.p2align 2,,3
L36:
	mov	w0, 0
	ret
	.p2align 2,,3
L37:
	ldr	x1, [x3, 16]
	mov	x0, 29297
	movk	x0, 0x7473, lsl 16
	movk	x0, 0x7675, lsl 32
	movk	x0, 0x7877, lsl 48
	cmp	x1, x0
	bne	L34
	ldr	w1, [x3, 24]
	mov	w0, 31353
	movk	w0, 0x4241, lsl 16
	cmp	w1, w0
	bne	L34
	ldrh	w1, [x3, 28]
	mov	w0, 17475
	cmp	w1, w0
	bne	L34
	mov	w0, 0
	eor	w0, w0, 1
	b	L32
LFE5:
	.literal16
	.align	4
lC1:
	.byte	97
	.byte	98
	.byte	99
	.byte	100
	.byte	101
	.byte	102
	.byte	103
	.byte	104
	.byte	105
	.byte	106
	.byte	107
	.byte	108
	.byte	109
	.byte	110
	.byte	111
	.byte	112
	.section __TEXT,__eh_frame,coalesced,no_toc+strip_static_syms+live_support
EH_frame1:
	.set L$set$0,LECIE1-LSCIE1
	.long L$set$0
LSCIE1:
	.long	0
	.byte	0x3
	.ascii "zR\0"
	.uleb128 0x1
	.sleb128 -8
	.uleb128 0x1e
	.uleb128 0x1
	.byte	0x10
	.byte	0xc
	.uleb128 0x1f
	.uleb128 0
	.align	3
LECIE1:
LSFDE1:
	.set L$set$1,LEFDE1-LASFDE1
	.long L$set$1
LASFDE1:
	.long	LASFDE1-EH_frame1
	.quad	LFB0-.
	.set L$set$2,LFE0-LFB0
	.quad L$set$2
	.uleb128 0
	.align	3
LEFDE1:
LSFDE3:
	.set L$set$3,LEFDE3-LASFDE3
	.long L$set$3
LASFDE3:
	.long	LASFDE3-EH_frame1
	.quad	LFB1-.
	.set L$set$4,LFE1-LFB1
	.quad L$set$4
	.uleb128 0
	.align	3
LEFDE3:
LSFDE5:
	.set L$set$5,LEFDE5-LASFDE5
	.long L$set$5
LASFDE5:
	.long	LASFDE5-EH_frame1
	.quad	LFB2-.
	.set L$set$6,LFE2-LFB2
	.quad L$set$6
	.uleb128 0
	.align	3
LEFDE5:
LSFDE7:
	.set L$set$7,LEFDE7-LASFDE7
	.long L$set$7
LASFDE7:
	.long	LASFDE7-EH_frame1
	.quad	LFB3-.
	.set L$set$8,LFE3-LFB3
	.quad L$set$8
	.uleb128 0
	.align	3
LEFDE7:
LSFDE9:
	.set L$set$9,LEFDE9-LASFDE9
	.long L$set$9
LASFDE9:
	.long	LASFDE9-EH_frame1
	.quad	LFB4-.
	.set L$set$10,LFE4-LFB4
	.quad L$set$10
	.uleb128 0
	.align	3
LEFDE9:
LSFDE11:
	.set L$set$11,LEFDE11-LASFDE11
	.long L$set$11
LASFDE11:
	.long	LASFDE11-EH_frame1
	.quad	LFB5-.
	.set L$set$12,LFE5-LFB5
	.quad L$set$12
	.uleb128 0
	.align	3
LEFDE11:
	.ident	"GCC: (Homebrew GCC 16.2.0) 16.2.0"
	.subsections_via_symbols
