	.build_version macos, 26, 0	sdk_version 26, 5
	.section	__TEXT,__text,regular,pure_instructions
	.globl	_cmp_memcmp_1                   ; -- Begin function cmp_memcmp_1
	.p2align	2
_cmp_memcmp_1:                          ; @cmp_memcmp_1
	.cfi_startproc
; %bb.0:
	add	x8, x1, #1
	cmp	x8, x2
	b.ls	LBB0_2
; %bb.1:
	mov	w0, #0                          ; =0x0
	ret
LBB0_2:
	ldrb	w8, [x0, x1]
	cmp	w8, #97
	cset	w0, eq
	ret
	.cfi_endproc
                                        ; -- End function
	.globl	_cmp_memcmp_2                   ; -- Begin function cmp_memcmp_2
	.p2align	2
_cmp_memcmp_2:                          ; @cmp_memcmp_2
	.cfi_startproc
; %bb.0:
	add	x8, x1, #2
	cmp	x8, x2
	b.ls	LBB1_2
; %bb.1:
	mov	w0, #0                          ; =0x0
	ret
LBB1_2:
	ldrh	w8, [x0, x1]
	mov	w9, #25185                      ; =0x6261
	cmp	w8, w9
	cset	w0, eq
	ret
	.cfi_endproc
                                        ; -- End function
	.globl	_cmp_memcmp_3                   ; -- Begin function cmp_memcmp_3
	.p2align	2
_cmp_memcmp_3:                          ; @cmp_memcmp_3
	.cfi_startproc
; %bb.0:
	add	x8, x1, #3
	cmp	x8, x2
	b.ls	LBB2_2
; %bb.1:
	mov	w0, #0                          ; =0x0
	ret
LBB2_2:
	add	x8, x0, x1
	ldrh	w9, [x8]
	ldrb	w8, [x8, #2]
	mov	w10, #25185                     ; =0x6261
	cmp	w9, w10
	mov	w9, #99                         ; =0x63
	ccmp	w8, w9, #0, eq
	cset	w0, eq
	ret
	.cfi_endproc
                                        ; -- End function
	.globl	_cmp_memcmp_4                   ; -- Begin function cmp_memcmp_4
	.p2align	2
_cmp_memcmp_4:                          ; @cmp_memcmp_4
	.cfi_startproc
; %bb.0:
	add	x8, x1, #4
	cmp	x8, x2
	b.ls	LBB3_2
; %bb.1:
	mov	w0, #0                          ; =0x0
	ret
LBB3_2:
	ldr	w8, [x0, x1]
	mov	w9, #25185                      ; =0x6261
	movk	w9, #25699, lsl #16
	cmp	w8, w9
	cset	w0, eq
	ret
	.cfi_endproc
                                        ; -- End function
	.globl	_cmp_memcmp_5                   ; -- Begin function cmp_memcmp_5
	.p2align	2
_cmp_memcmp_5:                          ; @cmp_memcmp_5
	.cfi_startproc
; %bb.0:
	add	x8, x1, #5
	cmp	x8, x2
	b.ls	LBB4_2
; %bb.1:
	mov	w0, #0                          ; =0x0
	ret
LBB4_2:
	add	x8, x0, x1
	ldr	w9, [x8]
	ldrb	w8, [x8, #4]
	mov	w10, #25185                     ; =0x6261
	movk	w10, #25699, lsl #16
	cmp	w9, w10
	mov	w9, #101                        ; =0x65
	ccmp	w8, w9, #0, eq
	cset	w0, eq
	ret
	.cfi_endproc
                                        ; -- End function
	.globl	_cmp_memcmp_6                   ; -- Begin function cmp_memcmp_6
	.p2align	2
_cmp_memcmp_6:                          ; @cmp_memcmp_6
	.cfi_startproc
; %bb.0:
	add	x8, x1, #6
	cmp	x8, x2
	b.ls	LBB5_2
; %bb.1:
	mov	w0, #0                          ; =0x0
	ret
LBB5_2:
	add	x8, x0, x1
	ldr	w9, [x8]
	ldrh	w8, [x8, #4]
	mov	w10, #25185                     ; =0x6261
	movk	w10, #25699, lsl #16
	cmp	w9, w10
	mov	w9, #26213                      ; =0x6665
	ccmp	w8, w9, #0, eq
	cset	w0, eq
	ret
	.cfi_endproc
                                        ; -- End function
	.globl	_cmp_memcmp_7                   ; -- Begin function cmp_memcmp_7
	.p2align	2
_cmp_memcmp_7:                          ; @cmp_memcmp_7
	.cfi_startproc
; %bb.0:
	add	x8, x1, #7
	cmp	x8, x2
	b.ls	LBB6_2
; %bb.1:
	mov	w0, #0                          ; =0x0
	ret
LBB6_2:
	add	x8, x0, x1
	ldr	w9, [x8]
	ldur	w8, [x8, #3]
	mov	w10, #25185                     ; =0x6261
	movk	w10, #25699, lsl #16
	cmp	w9, w10
	mov	w9, #25956                      ; =0x6564
	movk	w9, #26470, lsl #16
	ccmp	w8, w9, #0, eq
	cset	w0, eq
	ret
	.cfi_endproc
                                        ; -- End function
	.globl	_cmp_memcmp_8                   ; -- Begin function cmp_memcmp_8
	.p2align	2
_cmp_memcmp_8:                          ; @cmp_memcmp_8
	.cfi_startproc
; %bb.0:
	add	x8, x1, #8
	cmp	x8, x2
	b.ls	LBB7_2
; %bb.1:
	mov	w0, #0                          ; =0x0
	ret
LBB7_2:
	ldr	x8, [x0, x1]
	mov	x9, #25185                      ; =0x6261
	movk	x9, #25699, lsl #16
	movk	x9, #26213, lsl #32
	movk	x9, #26727, lsl #48
	cmp	x8, x9
	cset	w0, eq
	ret
	.cfi_endproc
                                        ; -- End function
	.globl	_cmp_memcmp_9                   ; -- Begin function cmp_memcmp_9
	.p2align	2
_cmp_memcmp_9:                          ; @cmp_memcmp_9
	.cfi_startproc
; %bb.0:
	add	x8, x1, #9
	cmp	x8, x2
	b.ls	LBB8_2
; %bb.1:
	mov	w0, #0                          ; =0x0
	ret
LBB8_2:
	add	x8, x0, x1
	ldr	x9, [x8]
	ldrb	w8, [x8, #8]
	mov	x10, #25185                     ; =0x6261
	movk	x10, #25699, lsl #16
	movk	x10, #26213, lsl #32
	movk	x10, #26727, lsl #48
	cmp	x9, x10
	mov	w9, #105                        ; =0x69
	ccmp	w8, w9, #0, eq
	cset	w0, eq
	ret
	.cfi_endproc
                                        ; -- End function
	.globl	_cmp_memcmp_10                  ; -- Begin function cmp_memcmp_10
	.p2align	2
_cmp_memcmp_10:                         ; @cmp_memcmp_10
	.cfi_startproc
; %bb.0:
	add	x8, x1, #10
	cmp	x8, x2
	b.ls	LBB9_2
; %bb.1:
	mov	w0, #0                          ; =0x0
	ret
LBB9_2:
	add	x8, x0, x1
	ldr	x9, [x8]
	ldrh	w8, [x8, #8]
	mov	x10, #25185                     ; =0x6261
	movk	x10, #25699, lsl #16
	movk	x10, #26213, lsl #32
	movk	x10, #26727, lsl #48
	cmp	x9, x10
	mov	w9, #27241                      ; =0x6a69
	ccmp	w8, w9, #0, eq
	cset	w0, eq
	ret
	.cfi_endproc
                                        ; -- End function
	.globl	_cmp_memcmp_11                  ; -- Begin function cmp_memcmp_11
	.p2align	2
_cmp_memcmp_11:                         ; @cmp_memcmp_11
	.cfi_startproc
; %bb.0:
	add	x8, x1, #11
	cmp	x8, x2
	b.ls	LBB10_2
; %bb.1:
	mov	w0, #0                          ; =0x0
	ret
LBB10_2:
	add	x8, x0, x1
	ldr	x9, [x8]
	ldur	x8, [x8, #3]
	mov	x10, #25185                     ; =0x6261
	movk	x10, #25699, lsl #16
	movk	x10, #26213, lsl #32
	movk	x10, #26727, lsl #48
	cmp	x9, x10
	mov	x9, #25956                      ; =0x6564
	movk	x9, #26470, lsl #16
	movk	x9, #26984, lsl #32
	movk	x9, #27498, lsl #48
	ccmp	x8, x9, #0, eq
	cset	w0, eq
	ret
	.cfi_endproc
                                        ; -- End function
	.globl	_cmp_memcmp_12                  ; -- Begin function cmp_memcmp_12
	.p2align	2
_cmp_memcmp_12:                         ; @cmp_memcmp_12
	.cfi_startproc
; %bb.0:
	add	x8, x1, #12
	cmp	x8, x2
	b.ls	LBB11_2
; %bb.1:
	mov	w0, #0                          ; =0x0
	ret
LBB11_2:
	add	x8, x0, x1
	ldr	x9, [x8]
	ldr	w8, [x8, #8]
	mov	x10, #25185                     ; =0x6261
	movk	x10, #25699, lsl #16
	movk	x10, #26213, lsl #32
	movk	x10, #26727, lsl #48
	cmp	x9, x10
	mov	w9, #27241                      ; =0x6a69
	movk	w9, #27755, lsl #16
	ccmp	w8, w9, #0, eq
	cset	w0, eq
	ret
	.cfi_endproc
                                        ; -- End function
	.globl	_cmp_memcmp_13                  ; -- Begin function cmp_memcmp_13
	.p2align	2
_cmp_memcmp_13:                         ; @cmp_memcmp_13
	.cfi_startproc
; %bb.0:
	add	x8, x1, #13
	cmp	x8, x2
	b.ls	LBB12_2
; %bb.1:
	mov	w0, #0                          ; =0x0
	ret
LBB12_2:
	add	x8, x0, x1
	ldr	x9, [x8]
	ldur	x8, [x8, #5]
	mov	x10, #25185                     ; =0x6261
	movk	x10, #25699, lsl #16
	movk	x10, #26213, lsl #32
	movk	x10, #26727, lsl #48
	cmp	x9, x10
	mov	x9, #26470                      ; =0x6766
	movk	x9, #26984, lsl #16
	movk	x9, #27498, lsl #32
	movk	x9, #28012, lsl #48
	ccmp	x8, x9, #0, eq
	cset	w0, eq
	ret
	.cfi_endproc
                                        ; -- End function
	.globl	_cmp_memcmp_14                  ; -- Begin function cmp_memcmp_14
	.p2align	2
_cmp_memcmp_14:                         ; @cmp_memcmp_14
	.cfi_startproc
; %bb.0:
	add	x8, x1, #14
	cmp	x8, x2
	b.ls	LBB13_2
; %bb.1:
	mov	w0, #0                          ; =0x0
	ret
LBB13_2:
	add	x8, x0, x1
	ldr	x9, [x8]
	ldur	x8, [x8, #6]
	mov	x10, #25185                     ; =0x6261
	movk	x10, #25699, lsl #16
	movk	x10, #26213, lsl #32
	movk	x10, #26727, lsl #48
	cmp	x9, x10
	mov	x9, #26727                      ; =0x6867
	movk	x9, #27241, lsl #16
	movk	x9, #27755, lsl #32
	movk	x9, #28269, lsl #48
	ccmp	x8, x9, #0, eq
	cset	w0, eq
	ret
	.cfi_endproc
                                        ; -- End function
	.globl	_cmp_memcmp_15                  ; -- Begin function cmp_memcmp_15
	.p2align	2
_cmp_memcmp_15:                         ; @cmp_memcmp_15
	.cfi_startproc
; %bb.0:
	add	x8, x1, #15
	cmp	x8, x2
	b.ls	LBB14_2
; %bb.1:
	mov	w0, #0                          ; =0x0
	ret
LBB14_2:
	add	x8, x0, x1
	ldr	x9, [x8]
	ldur	x8, [x8, #7]
	mov	x10, #25185                     ; =0x6261
	movk	x10, #25699, lsl #16
	movk	x10, #26213, lsl #32
	movk	x10, #26727, lsl #48
	cmp	x9, x10
	mov	x9, #26984                      ; =0x6968
	movk	x9, #27498, lsl #16
	movk	x9, #28012, lsl #32
	movk	x9, #28526, lsl #48
	ccmp	x8, x9, #0, eq
	cset	w0, eq
	ret
	.cfi_endproc
                                        ; -- End function
	.globl	_cmp_memcmp_16                  ; -- Begin function cmp_memcmp_16
	.p2align	2
_cmp_memcmp_16:                         ; @cmp_memcmp_16
	.cfi_startproc
; %bb.0:
	add	x8, x1, #16
	cmp	x8, x2
	b.ls	LBB15_2
; %bb.1:
	mov	w0, #0                          ; =0x0
	ret
LBB15_2:
	add	x8, x0, x1
	ldp	x9, x8, [x8]
	mov	x10, #25185                     ; =0x6261
	movk	x10, #25699, lsl #16
	movk	x10, #26213, lsl #32
	movk	x10, #26727, lsl #48
	cmp	x9, x10
	mov	x9, #27241                      ; =0x6a69
	movk	x9, #27755, lsl #16
	movk	x9, #28269, lsl #32
	movk	x9, #28783, lsl #48
	ccmp	x8, x9, #0, eq
	cset	w0, eq
	ret
	.cfi_endproc
                                        ; -- End function
	.globl	_cmp_memcmp_17                  ; -- Begin function cmp_memcmp_17
	.p2align	2
_cmp_memcmp_17:                         ; @cmp_memcmp_17
	.cfi_startproc
; %bb.0:
	add	x8, x1, #17
	cmp	x8, x2
	b.ls	LBB16_2
; %bb.1:
	mov	w0, #0                          ; =0x0
	ret
LBB16_2:
	add	x8, x0, x1
	ldp	x9, x10, [x8]
	ldrb	w8, [x8, #16]
	mov	x11, #25185                     ; =0x6261
	movk	x11, #25699, lsl #16
	movk	x11, #26213, lsl #32
	movk	x11, #26727, lsl #48
	cmp	x9, x11
	mov	x9, #27241                      ; =0x6a69
	movk	x9, #27755, lsl #16
	movk	x9, #28269, lsl #32
	movk	x9, #28783, lsl #48
	ccmp	x10, x9, #0, eq
	mov	w9, #113                        ; =0x71
	ccmp	w8, w9, #0, eq
	cset	w0, eq
	ret
	.cfi_endproc
                                        ; -- End function
	.globl	_cmp_memcmp_20                  ; -- Begin function cmp_memcmp_20
	.p2align	2
_cmp_memcmp_20:                         ; @cmp_memcmp_20
	.cfi_startproc
; %bb.0:
	add	x8, x1, #20
	cmp	x8, x2
	b.ls	LBB17_2
; %bb.1:
	mov	w0, #0                          ; =0x0
	ret
LBB17_2:
	add	x8, x0, x1
	ldp	x9, x10, [x8]
	ldr	w8, [x8, #16]
	mov	x11, #25185                     ; =0x6261
	movk	x11, #25699, lsl #16
	movk	x11, #26213, lsl #32
	movk	x11, #26727, lsl #48
	cmp	x9, x11
	mov	x9, #27241                      ; =0x6a69
	movk	x9, #27755, lsl #16
	movk	x9, #28269, lsl #32
	movk	x9, #28783, lsl #48
	ccmp	x10, x9, #0, eq
	mov	w9, #29297                      ; =0x7271
	movk	w9, #29811, lsl #16
	ccmp	w8, w9, #0, eq
	cset	w0, eq
	ret
	.cfi_endproc
                                        ; -- End function
	.globl	_cmp_memcmp_24                  ; -- Begin function cmp_memcmp_24
	.p2align	2
_cmp_memcmp_24:                         ; @cmp_memcmp_24
	.cfi_startproc
; %bb.0:
	add	x8, x1, #24
	cmp	x8, x2
	b.ls	LBB18_2
; %bb.1:
	mov	w0, #0                          ; =0x0
	ret
LBB18_2:
	add	x8, x0, x1
	ldp	x9, x10, [x8]
	ldr	x8, [x8, #16]
	mov	x11, #25185                     ; =0x6261
	movk	x11, #25699, lsl #16
	movk	x11, #26213, lsl #32
	movk	x11, #26727, lsl #48
	cmp	x9, x11
	mov	x9, #27241                      ; =0x6a69
	movk	x9, #27755, lsl #16
	movk	x9, #28269, lsl #32
	movk	x9, #28783, lsl #48
	ccmp	x10, x9, #0, eq
	mov	x9, #29297                      ; =0x7271
	movk	x9, #29811, lsl #16
	movk	x9, #30325, lsl #32
	movk	x9, #30839, lsl #48
	ccmp	x8, x9, #0, eq
	cset	w0, eq
	ret
	.cfi_endproc
                                        ; -- End function
	.globl	_cmp_memcmp_31                  ; -- Begin function cmp_memcmp_31
	.p2align	2
_cmp_memcmp_31:                         ; @cmp_memcmp_31
	.cfi_startproc
; %bb.0:
	add	x8, x1, #31
	cmp	x8, x2
	b.ls	LBB19_2
; %bb.1:
	mov	w0, #0                          ; =0x0
	ret
LBB19_2:
	add	x8, x0, x1
	ldp	x9, x10, [x8]
	ldr	x11, [x8, #16]
	ldur	x8, [x8, #23]
	mov	x12, #25185                     ; =0x6261
	movk	x12, #25699, lsl #16
	movk	x12, #26213, lsl #32
	movk	x12, #26727, lsl #48
	cmp	x9, x12
	mov	x9, #27241                      ; =0x6a69
	movk	x9, #27755, lsl #16
	movk	x9, #28269, lsl #32
	movk	x9, #28783, lsl #48
	ccmp	x10, x9, #0, eq
	mov	x9, #29297                      ; =0x7271
	movk	x9, #29811, lsl #16
	movk	x9, #30325, lsl #32
	movk	x9, #30839, lsl #48
	ccmp	x11, x9, #0, eq
	mov	x9, #31096                      ; =0x7978
	movk	x9, #16762, lsl #16
	movk	x9, #17218, lsl #32
	movk	x9, #17732, lsl #48
	ccmp	x8, x9, #0, eq
	cset	w0, eq
	ret
	.cfi_endproc
                                        ; -- End function
	.globl	_cmp_memcmp_32                  ; -- Begin function cmp_memcmp_32
	.p2align	2
_cmp_memcmp_32:                         ; @cmp_memcmp_32
	.cfi_startproc
; %bb.0:
	add	x8, x1, #32
	cmp	x8, x2
	b.ls	LBB20_2
; %bb.1:
	mov	w0, #0                          ; =0x0
	ret
LBB20_2:
	add	x8, x0, x1
	ldp	x9, x10, [x8]
	ldp	x11, x8, [x8, #16]
	mov	x12, #25185                     ; =0x6261
	movk	x12, #25699, lsl #16
	movk	x12, #26213, lsl #32
	movk	x12, #26727, lsl #48
	cmp	x9, x12
	mov	x9, #27241                      ; =0x6a69
	movk	x9, #27755, lsl #16
	movk	x9, #28269, lsl #32
	movk	x9, #28783, lsl #48
	ccmp	x10, x9, #0, eq
	mov	x9, #29297                      ; =0x7271
	movk	x9, #29811, lsl #16
	movk	x9, #30325, lsl #32
	movk	x9, #30839, lsl #48
	ccmp	x11, x9, #0, eq
	mov	x9, #31353                      ; =0x7a79
	movk	x9, #16961, lsl #16
	movk	x9, #17475, lsl #32
	movk	x9, #17989, lsl #48
	ccmp	x8, x9, #0, eq
	cset	w0, eq
	ret
	.cfi_endproc
                                        ; -- End function
	.globl	_cmp_memcmp_33                  ; -- Begin function cmp_memcmp_33
	.p2align	2
_cmp_memcmp_33:                         ; @cmp_memcmp_33
	.cfi_startproc
; %bb.0:
	add	x8, x1, #33
	cmp	x8, x2
	b.ls	LBB21_2
; %bb.1:
	mov	w0, #0                          ; =0x0
	ret
LBB21_2:
	add	x8, x0, x1
	ldp	x9, x10, [x8]
	ldp	x11, x12, [x8, #16]
	ldrb	w8, [x8, #32]
	mov	x13, #25185                     ; =0x6261
	movk	x13, #25699, lsl #16
	movk	x13, #26213, lsl #32
	movk	x13, #26727, lsl #48
	cmp	x9, x13
	mov	x9, #27241                      ; =0x6a69
	movk	x9, #27755, lsl #16
	movk	x9, #28269, lsl #32
	movk	x9, #28783, lsl #48
	ccmp	x10, x9, #0, eq
	mov	x9, #29297                      ; =0x7271
	movk	x9, #29811, lsl #16
	movk	x9, #30325, lsl #32
	movk	x9, #30839, lsl #48
	ccmp	x11, x9, #0, eq
	mov	x9, #31353                      ; =0x7a79
	movk	x9, #16961, lsl #16
	movk	x9, #17475, lsl #32
	movk	x9, #17989, lsl #48
	ccmp	x12, x9, #0, eq
	mov	w9, #71                         ; =0x47
	ccmp	w8, w9, #0, eq
	cset	w0, eq
	ret
	.cfi_endproc
                                        ; -- End function
	.globl	_cmp_memcmp_40                  ; -- Begin function cmp_memcmp_40
	.p2align	2
_cmp_memcmp_40:                         ; @cmp_memcmp_40
	.cfi_startproc
; %bb.0:
	add	x8, x1, #40
	cmp	x8, x2
	b.ls	LBB22_2
; %bb.1:
	mov	w0, #0                          ; =0x0
	ret
LBB22_2:
	add	x8, x0, x1
	ldp	x9, x10, [x8]
	ldp	x11, x12, [x8, #16]
	ldr	x8, [x8, #32]
	mov	x13, #25185                     ; =0x6261
	movk	x13, #25699, lsl #16
	movk	x13, #26213, lsl #32
	movk	x13, #26727, lsl #48
	cmp	x9, x13
	mov	x9, #27241                      ; =0x6a69
	movk	x9, #27755, lsl #16
	movk	x9, #28269, lsl #32
	movk	x9, #28783, lsl #48
	ccmp	x10, x9, #0, eq
	mov	x9, #29297                      ; =0x7271
	movk	x9, #29811, lsl #16
	movk	x9, #30325, lsl #32
	movk	x9, #30839, lsl #48
	ccmp	x11, x9, #0, eq
	mov	x9, #31353                      ; =0x7a79
	movk	x9, #16961, lsl #16
	movk	x9, #17475, lsl #32
	movk	x9, #17989, lsl #48
	ccmp	x12, x9, #0, eq
	mov	x9, #18503                      ; =0x4847
	movk	x9, #19017, lsl #16
	movk	x9, #19531, lsl #32
	movk	x9, #20045, lsl #48
	ccmp	x8, x9, #0, eq
	cset	w0, eq
	ret
	.cfi_endproc
                                        ; -- End function
	.globl	_cmp_memcmp_48                  ; -- Begin function cmp_memcmp_48
	.p2align	2
_cmp_memcmp_48:                         ; @cmp_memcmp_48
	.cfi_startproc
; %bb.0:
	add	x8, x1, #48
	cmp	x8, x2
	b.ls	LBB23_2
; %bb.1:
	mov	w0, #0                          ; =0x0
	ret
LBB23_2:
	add	x8, x0, x1
	ldp	x9, x10, [x8]
	ldp	x11, x12, [x8, #16]
	ldp	x13, x8, [x8, #32]
	mov	x14, #25185                     ; =0x6261
	movk	x14, #25699, lsl #16
	movk	x14, #26213, lsl #32
	movk	x14, #26727, lsl #48
	cmp	x9, x14
	mov	x9, #27241                      ; =0x6a69
	movk	x9, #27755, lsl #16
	movk	x9, #28269, lsl #32
	movk	x9, #28783, lsl #48
	ccmp	x10, x9, #0, eq
	mov	x9, #29297                      ; =0x7271
	movk	x9, #29811, lsl #16
	movk	x9, #30325, lsl #32
	movk	x9, #30839, lsl #48
	ccmp	x11, x9, #0, eq
	mov	x9, #31353                      ; =0x7a79
	movk	x9, #16961, lsl #16
	movk	x9, #17475, lsl #32
	movk	x9, #17989, lsl #48
	ccmp	x12, x9, #0, eq
	mov	x9, #18503                      ; =0x4847
	movk	x9, #19017, lsl #16
	movk	x9, #19531, lsl #32
	movk	x9, #20045, lsl #48
	ccmp	x13, x9, #0, eq
	mov	x9, #20559                      ; =0x504f
	movk	x9, #21073, lsl #16
	movk	x9, #21587, lsl #32
	movk	x9, #22101, lsl #48
	ccmp	x8, x9, #0, eq
	cset	w0, eq
	ret
	.cfi_endproc
                                        ; -- End function
	.globl	_cmp_memcmp_64                  ; -- Begin function cmp_memcmp_64
	.p2align	2
_cmp_memcmp_64:                         ; @cmp_memcmp_64
	.cfi_startproc
; %bb.0:
	add	x8, x1, #64
	cmp	x8, x2
	b.ls	LBB24_2
; %bb.1:
	mov	w0, #0                          ; =0x0
	ret
LBB24_2:
	add	x8, x0, x1
	ldp	x9, x10, [x8]
	ldp	x11, x12, [x8, #16]
	ldp	x13, x14, [x8, #32]
	ldp	x15, x8, [x8, #48]
	mov	x16, #25185                     ; =0x6261
	movk	x16, #25699, lsl #16
	movk	x16, #26213, lsl #32
	movk	x16, #26727, lsl #48
	cmp	x9, x16
	mov	x9, #27241                      ; =0x6a69
	movk	x9, #27755, lsl #16
	movk	x9, #28269, lsl #32
	movk	x9, #28783, lsl #48
	ccmp	x10, x9, #0, eq
	mov	x9, #29297                      ; =0x7271
	movk	x9, #29811, lsl #16
	movk	x9, #30325, lsl #32
	movk	x9, #30839, lsl #48
	ccmp	x11, x9, #0, eq
	mov	x9, #31353                      ; =0x7a79
	movk	x9, #16961, lsl #16
	movk	x9, #17475, lsl #32
	movk	x9, #17989, lsl #48
	ccmp	x12, x9, #0, eq
	mov	x9, #18503                      ; =0x4847
	movk	x9, #19017, lsl #16
	movk	x9, #19531, lsl #32
	movk	x9, #20045, lsl #48
	ccmp	x13, x9, #0, eq
	mov	x9, #20559                      ; =0x504f
	movk	x9, #21073, lsl #16
	movk	x9, #21587, lsl #32
	movk	x9, #22101, lsl #48
	ccmp	x14, x9, #0, eq
	mov	x9, #22615                      ; =0x5857
	movk	x9, #23129, lsl #16
	movk	x9, #12592, lsl #32
	movk	x9, #13106, lsl #48
	ccmp	x15, x9, #0, eq
	mov	x9, #13620                      ; =0x3534
	movk	x9, #14134, lsl #16
	movk	x9, #14648, lsl #32
	movk	x9, #25185, lsl #48
	ccmp	x8, x9, #0, eq
	cset	w0, eq
	ret
	.cfi_endproc
                                        ; -- End function
	.globl	_cmp_mask_1                     ; -- Begin function cmp_mask_1
	.p2align	2
_cmp_mask_1:                            ; @cmp_mask_1
	.cfi_startproc
; %bb.0:
	add	x8, x1, #4
	cmp	x8, x2
	b.ls	LBB25_2
; %bb.1:
	mov	w0, #0                          ; =0x0
	ret
LBB25_2:
	ldrb	w8, [x0, x1]
	cmp	w8, #97
	cset	w0, eq
	ret
	.cfi_endproc
                                        ; -- End function
	.globl	_cmp_mask_2                     ; -- Begin function cmp_mask_2
	.p2align	2
_cmp_mask_2:                            ; @cmp_mask_2
	.cfi_startproc
; %bb.0:
	add	x8, x1, #4
	cmp	x8, x2
	b.ls	LBB26_2
; %bb.1:
	mov	w0, #0                          ; =0x0
	ret
LBB26_2:
	ldrh	w8, [x0, x1]
	mov	w9, #25185                      ; =0x6261
	cmp	w8, w9
	cset	w0, eq
	ret
	.cfi_endproc
                                        ; -- End function
	.globl	_cmp_mask_3                     ; -- Begin function cmp_mask_3
	.p2align	2
_cmp_mask_3:                            ; @cmp_mask_3
	.cfi_startproc
; %bb.0:
	add	x8, x1, #4
	cmp	x8, x2
	b.ls	LBB27_2
; %bb.1:
	mov	w0, #0                          ; =0x0
	ret
LBB27_2:
	ldr	w8, [x0, x1]
	and	w8, w8, #0xffffff
	sub	w8, w8, #1590, lsl #12          ; =6512640
	cmp	w8, #609
	cset	w0, eq
	ret
	.cfi_endproc
                                        ; -- End function
	.globl	_cmp_mask_4                     ; -- Begin function cmp_mask_4
	.p2align	2
_cmp_mask_4:                            ; @cmp_mask_4
	.cfi_startproc
; %bb.0:
	add	x8, x1, #4
	cmp	x8, x2
	b.ls	LBB28_2
; %bb.1:
	mov	w0, #0                          ; =0x0
	ret
LBB28_2:
	ldr	w8, [x0, x1]
	mov	w9, #25185                      ; =0x6261
	movk	w9, #25699, lsl #16
	cmp	w8, w9
	cset	w0, eq
	ret
	.cfi_endproc
                                        ; -- End function
	.globl	_cmp_mask_5                     ; -- Begin function cmp_mask_5
	.p2align	2
_cmp_mask_5:                            ; @cmp_mask_5
	.cfi_startproc
; %bb.0:
	add	x8, x1, #8
	cmp	x8, x2
	b.ls	LBB29_2
; %bb.1:
	mov	w0, #0                          ; =0x0
	ret
LBB29_2:
	ldr	x8, [x0, x1]
	and	x8, x8, #0xffffffffff
	mov	x9, #25185                      ; =0x6261
	movk	x9, #25699, lsl #16
	movk	x9, #101, lsl #32
	cmp	x8, x9
	cset	w0, eq
	ret
	.cfi_endproc
                                        ; -- End function
	.globl	_cmp_mask_6                     ; -- Begin function cmp_mask_6
	.p2align	2
_cmp_mask_6:                            ; @cmp_mask_6
	.cfi_startproc
; %bb.0:
	add	x8, x1, #8
	cmp	x8, x2
	b.ls	LBB30_2
; %bb.1:
	mov	w0, #0                          ; =0x0
	ret
LBB30_2:
	ldr	x8, [x0, x1]
	and	x8, x8, #0xffffffffffff
	mov	x9, #25185                      ; =0x6261
	movk	x9, #25699, lsl #16
	movk	x9, #26213, lsl #32
	cmp	x8, x9
	cset	w0, eq
	ret
	.cfi_endproc
                                        ; -- End function
	.globl	_cmp_mask_7                     ; -- Begin function cmp_mask_7
	.p2align	2
_cmp_mask_7:                            ; @cmp_mask_7
	.cfi_startproc
; %bb.0:
	add	x8, x1, #8
	cmp	x8, x2
	b.ls	LBB31_2
; %bb.1:
	mov	w0, #0                          ; =0x0
	ret
LBB31_2:
	ldr	x8, [x0, x1]
	and	x8, x8, #0xffffffffffffff
	mov	x9, #25185                      ; =0x6261
	movk	x9, #25699, lsl #16
	movk	x9, #26213, lsl #32
	movk	x9, #103, lsl #48
	cmp	x8, x9
	cset	w0, eq
	ret
	.cfi_endproc
                                        ; -- End function
	.globl	_cmp_mask_8                     ; -- Begin function cmp_mask_8
	.p2align	2
_cmp_mask_8:                            ; @cmp_mask_8
	.cfi_startproc
; %bb.0:
	add	x8, x1, #8
	cmp	x8, x2
	b.ls	LBB32_2
; %bb.1:
	mov	w0, #0                          ; =0x0
	ret
LBB32_2:
	ldr	x8, [x0, x1]
	mov	x9, #25185                      ; =0x6261
	movk	x9, #25699, lsl #16
	movk	x9, #26213, lsl #32
	movk	x9, #26727, lsl #48
	cmp	x8, x9
	cset	w0, eq
	ret
	.cfi_endproc
                                        ; -- End function
	.globl	_cmp_overlap_5                  ; -- Begin function cmp_overlap_5
	.p2align	2
_cmp_overlap_5:                         ; @cmp_overlap_5
	.cfi_startproc
; %bb.0:
	add	x8, x1, #5
	cmp	x8, x2
	b.ls	LBB33_2
; %bb.1:
	mov	w0, #0                          ; =0x0
	ret
LBB33_2:
	add	x8, x0, x1
	ldr	w9, [x8]
	ldur	w8, [x8, #1]
	mov	w10, #25185                     ; =0x6261
	movk	w10, #25699, lsl #16
	cmp	w9, w10
	mov	w9, #25442                      ; =0x6362
	movk	w9, #25956, lsl #16
	ccmp	w8, w9, #0, eq
	cset	w0, eq
	ret
	.cfi_endproc
                                        ; -- End function
	.globl	_cmp_overlap_6                  ; -- Begin function cmp_overlap_6
	.p2align	2
_cmp_overlap_6:                         ; @cmp_overlap_6
	.cfi_startproc
; %bb.0:
	add	x8, x1, #6
	cmp	x8, x2
	b.ls	LBB34_2
; %bb.1:
	mov	w0, #0                          ; =0x0
	ret
LBB34_2:
	add	x8, x0, x1
	ldr	w9, [x8]
	ldur	w8, [x8, #2]
	mov	w10, #25185                     ; =0x6261
	movk	w10, #25699, lsl #16
	cmp	w9, w10
	mov	w9, #25699                      ; =0x6463
	movk	w9, #26213, lsl #16
	ccmp	w8, w9, #0, eq
	cset	w0, eq
	ret
	.cfi_endproc
                                        ; -- End function
	.globl	_cmp_overlap_7                  ; -- Begin function cmp_overlap_7
	.p2align	2
_cmp_overlap_7:                         ; @cmp_overlap_7
	.cfi_startproc
; %bb.0:
	add	x8, x1, #7
	cmp	x8, x2
	b.ls	LBB35_2
; %bb.1:
	mov	w0, #0                          ; =0x0
	ret
LBB35_2:
	add	x8, x0, x1
	ldr	w9, [x8]
	ldur	w8, [x8, #3]
	mov	w10, #25185                     ; =0x6261
	movk	w10, #25699, lsl #16
	cmp	w9, w10
	mov	w9, #25956                      ; =0x6564
	movk	w9, #26470, lsl #16
	ccmp	w8, w9, #0, eq
	cset	w0, eq
	ret
	.cfi_endproc
                                        ; -- End function
	.section	__TEXT,__cstring,cstring_literals
l_.str.1:                               ; @.str.1
	.asciz	"ab"

l_.str.2:                               ; @.str.2
	.asciz	"abc"

l_.str.3:                               ; @.str.3
	.asciz	"abcd"

l_.str.4:                               ; @.str.4
	.asciz	"abcde"

l_.str.5:                               ; @.str.5
	.asciz	"abcdef"

l_.str.6:                               ; @.str.6
	.asciz	"abcdefg"

l_.str.7:                               ; @.str.7
	.asciz	"abcdefgh"

l_.str.8:                               ; @.str.8
	.asciz	"abcdefghi"

l_.str.9:                               ; @.str.9
	.asciz	"abcdefghij"

l_.str.10:                              ; @.str.10
	.asciz	"abcdefghijk"

l_.str.11:                              ; @.str.11
	.asciz	"abcdefghijkl"

l_.str.12:                              ; @.str.12
	.asciz	"abcdefghijklm"

l_.str.13:                              ; @.str.13
	.asciz	"abcdefghijklmn"

l_.str.14:                              ; @.str.14
	.asciz	"abcdefghijklmno"

l_.str.15:                              ; @.str.15
	.asciz	"abcdefghijklmnop"

l_.str.16:                              ; @.str.16
	.asciz	"abcdefghijklmnopq"

l_.str.17:                              ; @.str.17
	.asciz	"abcdefghijklmnopqrst"

l_.str.18:                              ; @.str.18
	.asciz	"abcdefghijklmnopqrstuvwx"

l_.str.19:                              ; @.str.19
	.asciz	"abcdefghijklmnopqrstuvwxyzABCDE"

l_.str.20:                              ; @.str.20
	.asciz	"abcdefghijklmnopqrstuvwxyzABCDEF"

l_.str.21:                              ; @.str.21
	.asciz	"abcdefghijklmnopqrstuvwxyzABCDEFG"

l_.str.22:                              ; @.str.22
	.asciz	"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMN"

l_.str.23:                              ; @.str.23
	.asciz	"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUV"

l_.str.24:                              ; @.str.24
	.asciz	"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789ab"

.subsections_via_symbols
