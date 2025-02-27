/*******************************************************************************
  Data Type definition of Timer/Counter(TCC) PLIB

  Company:
    Microchip Technology Inc.

  File Name:
    plib_${TCC_INSTANCE_NAME?lower_case}.h

  Summary:
    Data Type definition of the TCC Peripheral Interface Plib.

  Description:
    This file defines the Data Types for the TCC Plib.

  Remarks:
    None.

*******************************************************************************/

/*******************************************************************************
* Copyright (C) 2018 Microchip Technology Inc. and its subsidiaries.
*
* Subject to your compliance with these terms, you may use Microchip software
* and any derivatives exclusively with Microchip products. It is your
* responsibility to comply with third party license terms applicable to your
* use of third party software (including open source software) that may
* accompany Microchip software.
*
* THIS SOFTWARE IS SUPPLIED BY MICROCHIP "AS IS". NO WARRANTIES, WHETHER
* EXPRESS, IMPLIED OR STATUTORY, APPLY TO THIS SOFTWARE, INCLUDING ANY IMPLIED
* WARRANTIES OF NON-INFRINGEMENT, MERCHANTABILITY, AND FITNESS FOR A
* PARTICULAR PURPOSE.
*
* IN NO EVENT WILL MICROCHIP BE LIABLE FOR ANY INDIRECT, SPECIAL, PUNITIVE,
* INCIDENTAL OR CONSEQUENTIAL LOSS, DAMAGE, COST OR EXPENSE OF ANY KIND
* WHATSOEVER RELATED TO THE SOFTWARE, HOWEVER CAUSED, EVEN IF MICROCHIP HAS
* BEEN ADVISED OF THE POSSIBILITY OR THE DAMAGES ARE FORESEEABLE. TO THE
* FULLEST EXTENT ALLOWED BY LAW, MICROCHIP'S TOTAL LIABILITY ON ALL CLAIMS IN
* ANY WAY RELATED TO THIS SOFTWARE WILL NOT EXCEED THE AMOUNT OF FEES, IF ANY,
* THAT YOU HAVE PAID DIRECTLY TO MICROCHIP FOR THIS SOFTWARE.
*******************************************************************************/

#ifndef PLIB_${TCC_INSTANCE_NAME}_H
#define PLIB_${TCC_INSTANCE_NAME}_H

#include "device.h"
#include "plib_tcc_common.h"

// DOM-IGNORE-BEGIN
#ifdef __cplusplus  // Provide C++ Compatibility

    extern "C" {

#endif
// DOM-IGNORE-END

// *****************************************************************************
// *****************************************************************************
// Section: Data Types
// *****************************************************************************
// *****************************************************************************
/*  The following data type definitions are used by the functions in this
    interface and should be considered part it.
*/

/* Total number of TCC channels in a module */
#define ${TCC_INSTANCE_NAME}_NUM_CHANNELS    (${TCC_NUM_CHANNELS}U)

/* TCC Channel numbers

   Summary:
    Identifies channel number within TCC module

   Description:
    This enumeration identifies TCC channel number.

   Remarks:
    None.
*/
typedef enum
{
<#list 0 ..(TCC_NUM_CHANNELS -1) as i >
    <#assign CH_NUM = i>
    ${TCC_INSTANCE_NAME}_CHANNEL${CH_NUM},
</#list>
}${TCC_INSTANCE_NAME}_CHANNEL_NUM;

// *****************************************************************************

/* TCC Channel interrupt status

   Summary:
    Identifies TCC PWM interrupt status flags

   Description:
    This enumeration identifies TCC PWM interrupt status falgs

   Remarks:
    None.
*/
typedef enum
{
    ${TCC_INSTANCE_NAME}_PWM_STATUS_OVF = TCC_INTFLAG_OVF_Msk,
    ${TCC_INSTANCE_NAME}_PWM_STATUS_FAULT_0 = TCC_INTFLAG_FAULT0_Msk,
    ${TCC_INSTANCE_NAME}_PWM_STATUS_FAULT_1 = TCC_INTFLAG_FAULT1_Msk,
<#list 0 ..(TCC_NUM_CHANNELS -1) as i >
    ${TCC_INSTANCE_NAME}_PWM_STATUS_MC_${i} = TCC_INTFLAG_MC${i}_Msk,
</#list>
}${TCC_INSTANCE_NAME}_PWM_STATUS;

<#assign TCC_INTERRUPT = false>
<#list 0..(TCC_NUM_CHANNELS-1) as i>
    <#assign TCC_INT_MC = "TCC_INTENSET_MC_" + i>
    <#if .vars[TCC_INT_MC] == true>
        <#assign TCC_INTERRUPT = true>
    </#if>
</#list>
<#if TCC_INTENSET_OVF == true || TCC_INTENSET_FAULT0 == true || TCC_INTENSET_FAULT1 == true>
    <#assign TCC_INTERRUPT = true>
</#if>
// *****************************************************************************
// *****************************************************************************
// Section: Interface Routines
// *****************************************************************************
// *****************************************************************************
/* The following functions make up the methods (set of possible operations) of
   this interface.
*/

// *****************************************************************************
void ${TCC_INSTANCE_NAME}_PWMInitialize(void);

void ${TCC_INSTANCE_NAME}_PWMStart(void);

void ${TCC_INSTANCE_NAME}_PWMStop(void);

<#if TCC_IS_DEAD_TIME == 1>
void ${TCC_INSTANCE_NAME}_PWMDeadTimeSet(uint8_t deadtime_high, uint8_t deadtime_low);
</#if>

void ${TCC_INSTANCE_NAME}_PWMForceUpdate(void);

<#if TCC_IS_PG == 1>
bool ${TCC_INSTANCE_NAME}_PWMPatternSet(uint8_t pattern_enable, uint8_t pattern_output);

</#if>

void ${TCC_INSTANCE_NAME}_PWMPeriodInterruptEnable(void);

void ${TCC_INSTANCE_NAME}_PWMPeriodInterruptDisable(void);

<#if TCC_INTERRUPT == true>
void ${TCC_INSTANCE_NAME}_PWMCallbackRegister(TCC_CALLBACK callback, uintptr_t context);
<#else>
uint32_t ${TCC_INSTANCE_NAME}_PWMInterruptStatusGet(void);
</#if>

<#if TCC_SIZE == 24>
bool ${TCC_INSTANCE_NAME}_PWM24bitPeriodSet(uint32_t period);

uint32_t ${TCC_INSTANCE_NAME}_PWM24bitPeriodGet(void);

void ${TCC_INSTANCE_NAME}_PWM24bitCounterSet(uint32_t count);

__STATIC_INLINE bool ${TCC_INSTANCE_NAME}_PWM24bitDutySet(${TCC_INSTANCE_NAME}_CHANNEL_NUM channel, uint32_t duty)
{
    bool status = false;
    if ((${TCC_INSTANCE_NAME}_REGS->TCC_STATUS & (1UL << (TCC_STATUS_${TCC_CBUF_REG_NAME}V0_Pos + (uint32_t)channel))) == 0U)
    {
        ${TCC_INSTANCE_NAME}_REGS->TCC_${TCC_CBUF_REG_NAME}[channel] = duty & 0xFFFFFFU;
        status = true;
    }
    return status;
}

<#elseif TCC_SIZE == 16>
bool ${TCC_INSTANCE_NAME}_PWM16bitPeriodSet(uint16_t period);

uint16_t ${TCC_INSTANCE_NAME}_PWM16bitPeriodGet(void);

void ${TCC_INSTANCE_NAME}_PWM16bitCounterSet(uint16_t count);

__STATIC_INLINE bool ${TCC_INSTANCE_NAME}_PWM16bitDutySet(${TCC_INSTANCE_NAME}_CHANNEL_NUM channel, uint16_t duty)
{
    bool status = false;
    if ((${TCC_INSTANCE_NAME}_REGS->TCC_STATUS & (1UL << (TCC_STATUS_${TCC_CBUF_REG_NAME}V0_Pos + (uint32_t)channel))) == 0U)
    {    
        ${TCC_INSTANCE_NAME}_REGS->TCC_${TCC_CBUF_REG_NAME}[channel] = duty;
        status = true;
    }
    return status;
}

<#elseif TCC_SIZE == 32>
bool ${TCC_INSTANCE_NAME}_PWM32bitPeriodSet(uint32_t period);

uint32_t ${TCC_INSTANCE_NAME}_PWM32bitPeriodGet(void);

void ${TCC_INSTANCE_NAME}_PWM32bitCounterSet(uint32_t count);

__STATIC_INLINE bool ${TCC_INSTANCE_NAME}_PWM32bitDutySet(${TCC_INSTANCE_NAME}_CHANNEL_NUM channel, uint32_t duty)
{
    bool status = false;
    if ((${TCC_INSTANCE_NAME}_REGS->TCC_STATUS & (1UL << (TCC_STATUS_${TCC_CBUF_REG_NAME}V0_Pos + (uint32_t)channel))) == 0U)
    {    
        ${TCC_INSTANCE_NAME}_REGS->TCC_${TCC_CBUF_REG_NAME}[channel] = duty;
        status = true;
    }
    return status;
}
</#if>
// DOM-IGNORE-BEGIN
#ifdef __cplusplus  // Provide C++ Compatibility

    }
#endif
// DOM-IGNORE-END

#endif /* PLIB_${TCC_INSTANCE_NAME}_H */
