/* Brief default interrupt handler for unused IRQs */
<#lt><#if "XC32" == COMPILER_CHOICE>
    <#lt>void __attribute__((optimize("-O1"),section(".text.DefaultInterruptHandler"),long_call, noreturn))DefaultInterruptHandler( void )
    <#lt>{
        <#lt>#if defined(__DEBUG) || defined(__DEBUG_D)
        <#lt>    asm("BKPT");
        <#lt>#endif
    <#lt>    while( true ){
    <#lt>    }
    <#lt>}
    <#lt>
<#lt><#elseif "IAR" == COMPILER_CHOICE>
    <#lt>void DefaultInterruptHandler( void )
    <#lt>{
    <#lt>    while( true ){
    <#lt>    }
    <#lt>}
    <#lt>
<#lt></#if>
${LIST_SYSTEM_INTERRUPT_WEAK_HANDLERS}
${LIST_SYSTEM_INTERRUPT_SHARED_HANDLERS}
<#lt>
