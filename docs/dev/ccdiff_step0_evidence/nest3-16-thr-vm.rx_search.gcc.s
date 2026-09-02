0000000000002eb0 <rx_search>:
    2eb0:	endbr64
    2eb4:	push   %r13
    2eb6:	push   %r12
    2eb8:	mov    %rdx,%r12
    2ebb:	push   %rbp
    2ebc:	mov    %rsi,%rbp
    2ebf:	push   %rbx
    2ec0:	mov    %rdi,%rbx
    2ec3:	sub    $0xc58,%rsp
    2eca:	mov    %fs:0x28,%r13
    2ed3:	mov    %r13,0xc48(%rsp)
    2edb:	mov    %rcx,%r13
    2ede:	lea    0x90(%rsp),%rax
    2ee6:	mov    %rsp,%r8
    2ee9:	movq   $0x48,0x50(%rsp)
    2ef2:	mov    %rax,0x48(%rsp)
    2ef7:	lea    0x750(%rsp),%rax
    2eff:	mov    %rax,0x58(%rsp)
    2f04:	movq   $0x4f,0x60(%rsp)
    2f0d:	call   2b20 <rx_search_run>
    2f12:	cmp    $0xfffffffd,%eax
    2f15:	je     2f40 <rx_search+0x90>
    2f17:	mov    0xc48(%rsp),%rdx
    2f1f:	sub    %fs:0x28,%rdx
    2f28:	jne    2f53 <rx_search+0xa3>
    2f2a:	add    $0xc58,%rsp
    2f31:	pop    %rbx
    2f32:	pop    %rbp
    2f33:	pop    %r12
    2f35:	pop    %r13
    2f37:	ret
    2f38:	nopl   0x0(%rax,%rax,1)
    2f40:	mov    %r13,%rcx
    2f43:	mov    %r12,%rdx
    2f46:	mov    %rbp,%rsi
    2f49:	mov    %rbx,%rdi
    2f4c:	call   2c50 <rx_search_deep>
    2f51:	jmp    2f17 <rx_search+0x67>
    2f53:	call   20b0 <__stack_chk_fail@plt>
    2f58:	nopl   0x0(%rax,%rax,1)

