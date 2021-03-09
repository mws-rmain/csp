"""*****************************************************************************
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
*****************************************************************************"""

def setXDMACDefaultSettings():
    triggerSettings = { "Software Trigger"  : ["MEM_TRAN", "PER2MEM", "HWR_CONNECTED", "INCREMENTED_AM", "INCREMENTED_AM", "AHB_IF1", "AHB_IF1", "BYTE", "CHK_1", "SINGLE"],
                        "Standard_Transmit" : ["PER_TRAN", "MEM2PER", "HWR_CONNECTED", "INCREMENTED_AM", "FIXED_AM",       "AHB_IF0", "AHB_IF1", "BYTE", "CHK_1", "SINGLE"],
                        "Standard_Receive"  : ["PER_TRAN", "PER2MEM", "HWR_CONNECTED", "FIXED_AM",       "INCREMENTED_AM", "AHB_IF1", "AHB_IF0", "BYTE", "CHK_1", "SINGLE"]}

    return triggerSettings

def updateLinkerScript(symbol, event):
    compiler_choice = event['source'].getSymbolByID("COMPILER_CHOICE")
    memory_loc  = event['source'].getSymbolByID("EXECUTION_MEMORY")
    if compiler_choice.getSelectedKey() == "XC32":
        if memory_loc.getValue()  == "DDR":
            symbol.setSourcePath("arm/templates/xc32/cortex_a/SAMA5D2/ddram.ld.ftl")
            symbol.setOutputName("ddr.ld")
        else:
            symbol.setSourcePath("arm/templates/xc32/cortex_a/SAMA5D2/sram.ld.ftl")
            symbol.setOutputName("sram.ld")
    else:
        if memory_loc.getValue() == "DDR":
            symbol.setSourcePath("arm/templates/iar/cortex_a/SAMA5D2/sam_a5_ddr.icf.ftl")
            symbol.setOutputName("ddr.icf")
        else:
            symbol.setSourcePath("arm/templates/iar/cortex_a/SAMA5D2/sram.icf.ftl")
            symbol.setOutputName("sram.icf")

def updateStartupFile(symbol, event):
    compiler_choice = event['source'].getSymbolByID("COMPILER_CHOICE")
    if compiler_choice.getSelectedKey() == "XC32":
        symbol.setSourcePath("arm/templates/xc32/cortex_a/SAMA5D2/cstartup.s.ftl")
        symbol.setOutputName("cstartup.S")
    else:
        symbol.setSourcePath("arm/templates/iar/cortex_a/SAMA5D2/sam_a5_cstartup.s.ftl")
        symbol.setOutputName("cstartup.s")

def setAppStartAddress(symbol, event):
    comp = event["source"]
    ddr_mem =  comp.getSymbolValue("EXECUTION_MEMORY") == "DDR"
    if ddr_mem:
        exec_addr = comp.getSymbolValue("DRAM_APP_START_ADDRESS")
        comp.setSymbolValue("APP_START_ADDRESS", exec_addr)
    else:
        comp.setSymbolValue("APP_START_ADDRESS", "0x0")

    comp.getSymbolByID("DRAM_APP_START_ADDRESS").setVisible(ddr_mem)

def setDRAMAddresses(symbol, event):
    comp = event["source"]
    no_cache_size = event["value"]
    no_cache_start = int(comp.getSymbolValue("DDRAM_NO_CACHE_START_ADDR"), 16)
    cache_end = int(comp.getSymbolValue("DDRAM_CACHE_END_ADDR"), 16)
    cache_start = no_cache_start + no_cache_size
    no_cache_end =cache_start - 1
    cache_size = cache_end - cache_start + 1
    comp.setSymbolValue("DDRAM_NO_CACHE_SIZE", "0x%08X" % no_cache_size)
    comp.setSymbolValue("DDRAM_NO_CACHE_END_ADDR", "0x%08X" % no_cache_end)
    comp.setSymbolValue("DDRAM_CACHE_START_ADDR", "0x%08X" % cache_start)
    comp.setSymbolValue("DDRAM_CACHE_SIZE", "0x%08X" % cache_size)
    
    
print ("Loading System Services for " + Variables.get("__PROCESSOR"))

deviceFamily = coreComponent.createStringSymbol("DeviceFamily", devCfgMenu)
deviceFamily.setLabel("Device Family")
deviceFamily.setDefaultValue("SAMA5D2")
deviceFamily.setReadOnly(True)
deviceFamily.setVisible(False)

cortexMenu = coreComponent.createMenuSymbol("CORTEX_MENU", None)
cortexMenu.setLabel("Cortex-A5 Configuration")
cortexMenu.setDescription("Configuration for Cortex A5")

freeRTOSVectors = coreComponent.createBooleanSymbol("USE_FREERTOS_VECTORS", None)
freeRTOSVectors.setVisible(False)
freeRTOSVectors.setReadOnly(True)
freeRTOSVectors.setDefaultValue(False)

threadXVectors = coreComponent.createBooleanSymbol("USE_THREADX_VECTORS", None)
threadXVectors.setVisible(False)
threadXVectors.setReadOnly(True)
threadXVectors.setDefaultValue(False)

#SRAM or DDR
memory_loc = coreComponent.createComboSymbol("EXECUTION_MEMORY", cortexMenu, ['DDR', 'SRAM'])
memory_loc.setLabel("Execution Memory")
memory_loc.setDefaultValue("DDR")
memory_loc.setDescription("Generate image to run out of either SRAM or DDR")

dramStartAddress = coreComponent.createStringSymbol("DRAM_APP_START_ADDRESS", cortexMenu)
dramStartAddress.setLabel("Execution start address in DDR")
dramStartAddress.setDefaultValue("0x26F00000")
Database.setSymbolValue("core", "APP_START_ADDRESS", dramStartAddress.getValue())

memory_loc.setDependencies(setAppStartAddress, ["EXECUTION_MEMORY", "DRAM_APP_START_ADDRESS"])

#MMU Configuration data
mmu_segments = [
                ("IROM", 0x00000000, 0x00100000, "normal", "ro", "exec"),
                ("NFC_RAM", 0x00100000, 0x00100000, "device", "rw", "no-exec"),
                ("SRAM", 0x00200000, 0x00100000, "normal", "rw", "exec"),
                ("UDPHS_RAM", 0x00300000, 0x00100000, "device", "rw", "no-exec"),
                ("UHPHS_OHCI", 0x00400000, 0x00100000, "device", "rw", "no-exec"),
                ("UHPHS_EHCI", 0x00500000, 0x00100000, "device", "rw", "no-exec"),
                ("AXIMX", 0x00600000, 0x00100000, "device", "rw", "no-exec"),
                ("DAP", 0x00700000, 0x00100000, "device", "rw", "no-exec"),
                ("PTCMEM", 0x00800000, 0x00100000, "device", "rw", "no-exec"),
                ("L2CC", 0x00A00000, 0x00200000, "device", "rw", "no-exec"),
                ("EBI_CS0", 0x10000000, 0x10000000, "strongly-ordered", "rw", "no-exec"),
                ("DDR_AES_CS", 0x40000000, 0x20000000, "normal", "rw", "exec"),
                ("EBI_CS1", 0x60000000, 0x10000000, "strongly-ordered", "rw", "no-exec"),
                ("EBI_CS2", 0x70000000, 0x10000000, "strongly-ordered", "rw", "no-exec"),
                ("EBI_CS3", 0x80000000, 0x10000000, "strongly-ordered", "rw", "no-exec"),
                ("QSPI_AES0", 0x90000000, 0x08000000, "strongly-ordered", "rw", "no-exec"),
                ("QSPI_AES1", 0x98000000, 0x08000000, "strongly-ordered", "rw", "no-exec"),
                ("SDMMC0", 0xA0000000, 0x00100000, "strongly-ordered", "rw", "no-exec"),
                ("SDMMC1", 0xB0000000, 0x00100000, "strongly-ordered", "rw", "no-exec"),
                ("NFC", 0xC0000000, 0x10000000, "strongly-ordered", "rw", "no-exec"),
                ("QSPI0MEM", 0xD0000000, 0x08000000, "strongly-ordered", "rw", "exec"),
                ("QSPI1MEM", 0xD8000000, 0x08000000, "strongly-ordered", "rw", "exec"),
                ("PERIPHERALS_0", 0xF0000000, 0x00100000, "strongly-ordered", "rw", "no-exec"),
                ("PERIPHERALS_1", 0xF8000000, 0x00100000, "strongly-ordered", "rw", "no-exec"),
                ("PERIPHERALS_2", 0xFC000000, 0x00100000, "strongly-ordered", "rw", "no-exec")
            ]


#DRAM cache configuration
ddr_node = ATDF.getNode("/avr-tools-device-file/devices/device/address-spaces/address-space/memory-segment@[name=\"DDR_CS\"]")
processor = Variables.get("__PROCESSOR")
ddr_start = int(ddr_node.getAttribute("start"), 0)
#Set 16MB as non-cacheable region and rest as cacheable region
non_cacheable_size = 16 * pow(2, 20)
if processor.endswith("2G"):
    #2 Gbit memory
    ddr_size = (2 * pow(2,30)) / 8
elif processor.endswith("1G"):
    # 1 Gbit memory
    ddr_size = (1 * pow(2,30)) / 8
elif processor.endswith("5M"):
    #512 Mbit memory
    ddr_size = (512 * pow(2,20)) / 8
    #reduce the non cacheable region to 8 MB
    non_cacheable_size = 8 * pow(2, 20)
else:
    #Non SiP variants, use entire DRAM region
    ddr_size = int(ddr_node.getAttribute("size"), 0)


#DRAM coherent region
dram_coherent_region = coreComponent.createIntegerSymbol("DRAM_COHERENT_REGION_SIZE", cortexMenu)
dram_coherent_region.setLabel("Size of non-cached region in DRAM (MB)")
dram_coherent_region.setMin(2)
dram_coherent_region.setMax(ddr_size/pow(2, 20))
dram_coherent_region.setDefaultValue(non_cacheable_size/pow(2, 20))

#DRAM internal symbols for MMU and linker scripts
dram_non_cacheable_start_addr = coreComponent.createStringSymbol("DDRAM_NO_CACHE_START_ADDR", None)
dram_non_cacheable_start_addr.setVisible(False)
dram_non_cacheable_start_addr.setDefaultValue("0x%08X" % ddr_start)

dram_non_cacheable_size = coreComponent.createStringSymbol("DDRAM_NO_CACHE_SIZE", None)
dram_non_cacheable_size.setVisible(False)
dram_non_cacheable_size.setLabel("Coherent region size in DRAM")
dram_non_cacheable_size.setDefaultValue("0x%08X" % non_cacheable_size)
dram_non_cacheable_size.setDependencies(setDRAMAddresses, ["DRAM_COHERENT_REGION_SIZE"])

dram_non_cacheable_end_addr = coreComponent.createStringSymbol("DDRAM_NO_CACHE_END_ADDR", None)
dram_non_cacheable_end_addr.setVisible(False)
dram_non_cacheable_end_addr.setDefaultValue("0x%08X" % (ddr_start + non_cacheable_size - 1))

dram_cacheable_start_addr = coreComponent.createStringSymbol("DDRAM_CACHE_START_ADDR", None)
dram_cacheable_start_addr.setVisible(False)
dram_cacheable_start_addr.setDefaultValue("0x%08X" % (ddr_start + non_cacheable_size))

dram_cacheable_size = coreComponent.createStringSymbol("DDRAM_CACHE_SIZE", None)
dram_cacheable_size.setVisible(False)
dram_cacheable_size.setDefaultValue("0x%08X" % (ddr_size - non_cacheable_size))

dram_cacheable_end_addr = coreComponent.createStringSymbol("DDRAM_CACHE_END_ADDR", None)
dram_cacheable_end_addr.setVisible(False)
dram_cacheable_end_addr.setDefaultValue("0x%08X" % (ddr_start + ddr_size - 1))

dram_boundary_addr = coreComponent.createStringSymbol("DDRAM_BOUNDARY_ADDR", None)
dram_boundary_addr.setVisible(False)
dram_boundary_addr.setDefaultValue("0x%08X" % (ddr_start + ddr_size))


#load MMU with default 1:1 mapping so we can use cache
execfile(Variables.get("__CORE_DIR") + "/../peripheral/mmu_v7a/config/mmu.py")

#load Matrix -- default all peripherals to non-secure
execfile(Variables.get("__CORE_DIR") + "/../peripheral/matrix_44025/config/matrix.py")

#load L2CC
execfile(Variables.get("__CORE_DIR") + "/../peripheral/l2cc_11160/config/l2cc.py")

# load clock manager information
execfile(Variables.get("__CORE_DIR") + "/../peripheral/clk_sam_a5d2/config/clk.py")
coreComponent.addPlugin("../peripheral/clk_sam_a5d2/plugin/clk_sam_a5d2.jar")

# load device specific pin manager information
execfile(Variables.get("__CORE_DIR") + "/../peripheral/pio_11264/config/pio.py")
coreComponent.addPlugin("../peripheral/pio_11264/plugin/pio_11264.jar")

# load AIC
execfile(Variables.get("__CORE_DIR") + "/../peripheral/aic_11051/config/aic.py")
coreComponent.addPlugin("../peripheral/aic_11051/plugin/aic_11051.jar")

# load dma manager information
execfile(Variables.get("__CORE_DIR") + "/../peripheral/xdmac_11161/config/xdmac.py")
coreComponent.addPlugin("../peripheral/xdmac_11161/plugin/dmamanager.jar")

# load wdt
execfile(Variables.get("__CORE_DIR") + "/../peripheral/wdt_6080/config/wdt.py")

# load ADC manager information
coreComponent.addPlugin("../peripheral/adc_44073/plugin/adc_44073.jar")
# load AIC manager information
coreComponent.addPlugin("../peripheral/aic_11051/plugin/aic_11051.jar")

compiler_choice = deviceFamily.getComponent().getSymbolByID("COMPILER_CHOICE")
if compiler_choice.getSelectedKey() == "XC32":
    armSysStartSourceFile = coreComponent.createFileSymbol("STARTUP_C", None)
    armSysStartSourceFile.setSourcePath("arm/templates/xc32/cortex_a/SAMA5D2/cstartup.s.ftl")
    armSysStartSourceFile.setOutputName("cstartup.S")
    armSysStartSourceFile.setMarkup(True)
    armSysStartSourceFile.setOverwrite(True)
    armSysStartSourceFile.setDestPath("")
    armSysStartSourceFile.setProjectPath("config/" + configName + "/")
    armSysStartSourceFile.setType("SOURCE")
    armSysStartSourceFile.setDependencies(updateStartupFile, ["COMPILER_CHOICE"])

    linkerFile = coreComponent.createFileSymbol("LINKER_SCRIPT", None)
    linkerFile.setSourcePath("arm/templates/xc32/cortex_a/SAMA5D2/ddram.ld.ftl")
    linkerFile.setOutputName("ddr.ld")
    linkerFile.setMarkup(True)
    linkerFile.setOverwrite(True)
    linkerFile.setDestPath("")
    linkerFile.setProjectPath("config/" + configName + "/")
    linkerFile.setType("LINKER")
    linkerFile.setDependencies(updateLinkerScript, ["EXECUTION_MEMORY", "COMPILER_CHOICE"])

elif compiler_choice.getSelectedKey() == "IAR":
    armSysStartSourceFile = coreComponent.createFileSymbol("STARTUP_C", None)
    armSysStartSourceFile.setSourcePath("arm/templates/iar/cortex_a/SAMA5D2/sam_a5_cstartup.s.ftl")
    armSysStartSourceFile.setOutputName("cstartup.s")
    armSysStartSourceFile.setMarkup(True)
    armSysStartSourceFile.setOverwrite(True)
    armSysStartSourceFile.setDestPath("")
    armSysStartSourceFile.setProjectPath("config/" + configName + "/")
    armSysStartSourceFile.setType("SOURCE")
    armSysStartSourceFile.setDependencies(updateStartupFile, ["COMPILER_CHOICE"])

    linkerFile = coreComponent.createFileSymbol("LINKER_SCRIPT", None)
    linkerFile.setSourcePath("arm/templates/iar/cortex_a/SAMA5D2/sam_a5_ddr.icf.ftl")
    linkerFile.setOutputName("ddr.icf")
    linkerFile.setMarkup(True)
    linkerFile.setOverwrite(True)
    linkerFile.setDestPath("")
    linkerFile.setProjectPath("config/" + configName + "/")
    linkerFile.setType("LINKER")
    linkerFile.setDependencies(updateLinkerScript, ["EXECUTION_MEMORY", "COMPILER_CHOICE"])

#default exception handlers.
faultSourceFile = coreComponent.createFileSymbol("DFLT_FAULT_HANDLER_C", None)
faultSourceFile.setSourcePath("arm/templates/common/mpu_handlers/fault_handlers.c")
faultSourceFile.setOutputName("fault_handlers.c")
faultSourceFile.setMarkup(True)
faultSourceFile.setOverwrite(True)
faultSourceFile.setDestPath("")
faultSourceFile.setProjectPath("config/" + configName + "/")
faultSourceFile.setType("SOURCE")
