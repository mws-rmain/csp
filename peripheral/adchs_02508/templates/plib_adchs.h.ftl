/*******************************************************************************
  ADCHS Peripheral Library Interface Header File

  Company
    Microchip Technology Inc.

  File Name
    plib_${ADCHS_INSTANCE_NAME?lower_case}.h

  Summary
    ${ADCHS_INSTANCE_NAME} peripheral library interface.

  Description
    This file defines the interface to the ADCHS peripheral library.  This
    library provides access to and control of the associated peripheral
    instance.

*******************************************************************************/

// DOM-IGNORE-BEGIN
/*******************************************************************************
* Copyright (C) 2019 Microchip Technology Inc. and its subsidiaries.
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
// DOM-IGNORE-END

#ifndef PLIB_${ADCHS_INSTANCE_NAME}_H    // Guards against multiple inclusion
#define PLIB_${ADCHS_INSTANCE_NAME}_H


// *****************************************************************************
// *****************************************************************************
// Section: Included Files
// *****************************************************************************
// *****************************************************************************

/*  This section lists the other files that are included in this file.
*/

#include "plib_adchs_common.h"

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


// *****************************************************************************
// *****************************************************************************
// Section: Interface Routines
// *****************************************************************************
// *****************************************************************************
/* The following functions make up the methods (set of possible operations) of
   this interface.
*/

void ${ADCHS_INSTANCE_NAME}_Initialize (void);

void ${ADCHS_INSTANCE_NAME}_ModulesEnable (ADCHS_MODULE_MASK modulesMask);
void ${ADCHS_INSTANCE_NAME}_ModulesDisable (ADCHS_MODULE_MASK modulesMask);

void ${ADCHS_INSTANCE_NAME}_GlobalEdgeConversionStart(void);
void ${ADCHS_INSTANCE_NAME}_GlobalLevelConversionStart(void);
void ${ADCHS_INSTANCE_NAME}_GlobalLevelConversionStop(void);
void ${ADCHS_INSTANCE_NAME}_ChannelConversionStart(ADCHS_CHANNEL_NUM channel);

void ${ADCHS_INSTANCE_NAME}_ChannelResultInterruptEnable (ADCHS_CHANNEL_NUM channel);
void ${ADCHS_INSTANCE_NAME}_ChannelResultInterruptDisable (ADCHS_CHANNEL_NUM channel);
<#if ADCHS_EARLY_INTERRUPT == true>
void ${ADCHS_INSTANCE_NAME}_ChannelEarlyInterruptEnable (ADCHS_CHANNEL_NUM channel);
void ${ADCHS_INSTANCE_NAME}_ChannelEarlyInterruptDisable (ADCHS_CHANNEL_NUM channel);
</#if>

bool ${ADCHS_INSTANCE_NAME}_ChannelResultIsReady(ADCHS_CHANNEL_NUM channel);
uint16_t ${ADCHS_INSTANCE_NAME}_ChannelResultGet(ADCHS_CHANNEL_NUM channel);

<#if ADC_IS_DMA_AVAILABLE == true && (ADC_DMA_ENABLED?? && ADC_DMA_ENABLED == true)>
void ${ADCHS_INSTANCE_NAME}_DMASampleCountBaseAddrSet(uint32_t baseAddr);
void ${ADCHS_INSTANCE_NAME}_DMAResultBaseAddrSet(uint32_t baseAddr);
<#if ADC_DMA_INT_ENABLED?? && ADC_DMA_INT_ENABLED == true>
void ${ADCHS_INSTANCE_NAME}_DMACallbackRegister(ADCHS_DMA_CALLBACK callback, uintptr_t context);
<#else>
ADCHS_DMA_STATUS ${ADCHS_INSTANCE_NAME}_DMAStatusGet(void);
</#if>
</#if>

<#if ADCHS_INTERRUPT == true>
    <#lt>void ${ADCHS_INSTANCE_NAME}_CallbackRegister(ADCHS_CHANNEL_NUM channel, ADCHS_CALLBACK callback, uintptr_t context);
</#if>

<#if ADCCON2__EOSIEN == true>
    <#lt>void ${ADCHS_INSTANCE_NAME}_EOSCallbackRegister(ADCHS_EOS_CALLBACK callback, uintptr_t context);
<#else>
    <#lt>bool ${ADCHS_INSTANCE_NAME}_EOSStatusGet(void);
</#if>

<#list 1..(ADCHS_NUM_COMPARATORS) as i>
<#assign ADCHS_ADCCMPCON_ENDCMP = "ADCCMPCON" + i + "__ENDCMP">
<#assign ADCHS_DCx_INT_ENABLED = "ADCHS_DC" + i + "_INT_ENABLED">
<#if .vars[ADCHS_ADCCMPCON_ENDCMP]?has_content && .vars[ADCHS_ADCCMPCON_ENDCMP] == true>
void ${ADCHS_INSTANCE_NAME}_Comparator${i}Enable(void);
void ${ADCHS_INSTANCE_NAME}_Comparator${i}Disable(void);
void ${ADCHS_INSTANCE_NAME}_Comparator${i}LimitSet(uint16_t low_threshold, uint16_t high_threshold);
void ${ADCHS_INSTANCE_NAME}_Comparator${i}EventModeSet(ADCHS_CMP_EVENT_MODE eventMode);
uint8_t ${ADCHS_INSTANCE_NAME}_Comparator${i}AnalogInputIDGet(void);
<#if .vars[ADCHS_DCx_INT_ENABLED] == true>
void ${ADCHS_INSTANCE_NAME}_Comparator${i}CallbackRegister(ADCHS_DC_CALLBACK callback, uintptr_t context);
<#else>
bool ${ADCHS_INSTANCE_NAME}_Comparator${i}StatusGet(void);
</#if>
</#if>
</#list>

<#list 1..(ADCHS_NUM_FILTERS) as i>
<#assign ADCFLTR_AFEN = "ADCFLTR" + i + "__AFEN">
<#assign ADCHS_DFx_INT_ENABLED = "ADCHS_DF" + i + "_INT_ENABLED">
<#if .vars[ADCFLTR_AFEN]?has_content && .vars[ADCFLTR_AFEN] == true>
uint16_t ${ADCHS_INSTANCE_NAME}_Filter${i}DataGet(void);
<#if .vars[ADCHS_DFx_INT_ENABLED] == true>
void ${ADCHS_INSTANCE_NAME}_Filter${i}CallbackRegister(ADCHS_DF_CALLBACK callback, uintptr_t context);
<#else>
bool ${ADCHS_INSTANCE_NAME}_Filter${i}IsReady(void);
</#if>
</#if>
</#list>
// *****************************************************************************

// DOM-IGNORE-BEGIN
#ifdef __cplusplus  // Provide C++ Compatibility

}
#endif
// DOM-IGNORE-END

#endif //PLIB_${ADCHS_INSTANCE_NAME}_H

/**
 End of File
*/
