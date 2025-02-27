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
modelist = ["Master", "Slave"]

I2CS_RISE_SETUP_TIME = [(250, 1000), (100, 300), (50,120)]

def handleMessage(messageID, args):
    global i2cSym_OperatingMode

    result_dict = {}

    if (messageID == "I2C_MASTER_MODE"):
        if args.get("isReadOnly") != None:
            i2cSym_OperatingMode.setReadOnly(args["isReadOnly"])
        if args.get("isEnabled") != None and args["isEnabled"] == True:
            i2cSym_OperatingMode.setValue(modelist[0])

    elif (messageID == "I2C_SLAVE_MODE"):
        if args.get("isReadOnly") != None:
            i2cSym_OperatingMode.setReadOnly(args["isReadOnly"])
        if args.get("isEnabled") != None and args["isEnabled"] == True:
            i2cSym_OperatingMode.setValue(modelist[1])

    return result_dict
###################################################################################################
#################################### Global Variables #############################################
###################################################################################################

global interruptsChildren

interruptsChildren = ATDF.getNode('/avr-tools-device-file/devices/device/interrupts').getChildren()

###################################################################################################
######################################### Functions ###############################################
###################################################################################################
def getIRQnumber(string):

    for param in interruptsChildren:
        name = param.getAttribute("name")
        if string == name:
            irq_index = param.getAttribute("index")
            break

    return irq_index

def _get_enblReg_parms(vectorNumber):

    # This takes in vector index for interrupt, and returns the IECx register name as well as
    # mask and bit location within it for given interrupt
    index = int(vectorNumber / 32)
    regName = "IEC" + str(index)
    return regName

def _get_statReg_parms(vectorNumber):

    # This takes in vector index for interrupt, and returns the IFSx register name as well as
    # mask and bit location within it for given interrupt
    index = int(vectorNumber / 32)
    regName = "IFS" + str(index)
    return regName

###################################################################################################
########################################## Callbacks  #############################################
###################################################################################################

# Calculates BRG value
def baudRateCalc(clk, baud):
    # Equation from FRM
    #I2CxBRG = [PBCLK/(2*FSCK) - (PBCLK*TPGOB)/2]  - 1
    #where TPGD = 130ns

    I2CxBRG = (clk / (2 * baud) - (clk * 0.000000130) / 2)  - 1

    i2cSym_BaudError_Comment.setVisible(False)

    if I2CxBRG < 4:
        I2CxBRG = 4
        i2cSym_BaudError_Comment.setVisible(True)
    elif I2CxBRG > i2cSymMaxBRG.getValue():
        I2CxBRG = i2cSymMaxBRG.getValue()
        i2cSym_BaudError_Comment.setVisible(True)

    return int(I2CxBRG)

def baudRateTrigger(symbol, event):

    clk = int(Database.getSymbolValue("core", i2cInstanceName.getValue() + "_CLOCK_FREQUENCY"))
    baud = int(i2cSym_BAUD.getValue())

    brgVal = baudRateCalc(clk, baud)
    symbol.setValue(brgVal, 2)

def i2cSourceFreq(symbol, event):

    symbol.setValue(int(Database.getSymbolValue("core", i2cInstanceName.getValue() + "_CLOCK_FREQUENCY")), 2)

def updateI2CClockWarningStatus(symbol, event):

    symbol.setVisible(not event["value"])

def masterModeVisibility(symbol, event):
    global i2cSym_OperatingMode

    if i2cSym_OperatingMode.getValue() == "Master":
        symbol.setVisible(True)
    else:
        symbol.setVisible(False)

def slaveModeVisibility(symbol, event):
    global i2cSym_OperatingMode
    global i2csSym_A10M

    if event["id"] == "I2CS_A10M_SUPPORT":
        if i2csSym_A10M.getValue() == True:
            symbol.setLabel("I2C Slave Address (10-bit)")
        else:
            symbol.setLabel("I2C Slave Address (7-bit)")

    elif event["id"] == "I2C_OPERATING_MODE":
        if i2cSym_OperatingMode.getValue() == "Slave":
            symbol.setVisible(True)
        else:
            symbol.setVisible(False)

def masterFilesGeneration(symbol, event):
    symbol.setEnabled(i2cSym_OperatingMode.getValue() == "Master")

def slaveFilesGeneration(symbol, event):
    symbol.setEnabled(i2cSym_OperatingMode.getValue() == "Slave")

def setI2CInterruptData(interruptDict, isEnabled):
    Database.setSymbolValue("core", interruptDict["InterruptVector"], isEnabled, 1)
    Database.setSymbolValue("core", interruptDict["InterruptHandlerLock"], isEnabled, 1)
    interruptName = interruptDict["InterruptHandler"].split("_INTERRUPT_HANDLER")[0]
    if isEnabled == True:
        Database.setSymbolValue("core", interruptDict["InterruptHandler"], interruptName + "_InterruptHandler", 1)
    else:
        Database.setSymbolValue("core", interruptDict["InterruptHandler"], interruptName + "_Handler", 1)

def interruptSetupChangeHandler(symbol, event):
    interruptSetup(i2cSym_OperatingMode.getValue(), False)

def interruptSetup(mode, isUpdate):
    global InterruptList
    global i2cSymIntEnableComment
    IntEnComment = False

    for interruptDict in InterruptList:
        if (interruptDict["type"] == "Bus"):
            isEnabled = True
        elif (interruptDict["type"] == mode):
            isEnabled = True
        else:
            isEnabled = False

        if (isUpdate == True):
            setI2CInterruptData(interruptDict, isEnabled)

        # Check if interrupt got enabled or not. If not, enable the comment to indicate interrupt is not enabled
        if isEnabled == True and IntEnComment == False:
            if Database.getSymbolValue("core", interruptDict["InterruptUpdate"] ) == True:
                IntEnComment = True

    if IntEnComment == True:
        i2cSymIntEnableComment.setVisible(True)
    else:
        i2cSymIntEnableComment.setVisible(False)

def interruptSetupOnModeChange(symbol, event):
    interruptSetup(event["value"], True)

def onCapabilityConnected(event):
    localComponent = event["localComponent"]
    remoteComponent = event["remoteComponent"]

    # This message should indicate to the dependent component that PLIB has finished its initialization and
    # is ready to accept configuration parameters from the dependent component
    argDict = {"localComponentID" : localComponent.getID()}
    argDict = Database.sendMessage(remoteComponent.getID(), "REQUEST_CONFIG_PARAMS", argDict)

def coreFreqUpdate(symbol, event):
    coreTimerFreq = int(Database.getSymbolValue("core", "SYS_CLK_FREQ"))/2
    symbol.setValue(coreTimerFreq)

def calcSetupAndRiseTimeCnt(coreTimerFreq, setupRiseTime):
    #Core timer counts required for 1 nano seconds
    coreTimerCountNs = float(coreTimerFreq)/1000000000

    return int(float(coreTimerCountNs) * setupRiseTime)

def updateSetupAndRiseTime(symbol, event):
    setupRiseTimeIndex = int(event['source'].getSymbolByID("I2CS_SETUP_RISE_TIME").getValue())
    coreTimerFreq = event['source'].getSymbolByID("I2CS_CORE_TIMER_FREQUENCY").getValue()

    setupRiseTime = I2CS_RISE_SETUP_TIME[setupRiseTimeIndex]

    if symbol.getID() == "I2CS_RISE_TIME_CORE_TIMER_CNTS":
        symbol.setValue(int(calcSetupAndRiseTimeCnt(coreTimerFreq, setupRiseTime[1])))
    else:
        symbol.setValue(int(calcSetupAndRiseTimeCnt(coreTimerFreq, setupRiseTime[0])))

def updateI2CBaudHz(symbol, event):
    symbol.setValue(event["value"])
###################################################################################################
########################################## Component  #############################################
###################################################################################################

def instantiateComponent(i2cComponent):

    global i2cInstanceName
    global i2cSym_BAUD
    global i2cSymMaxBRG
    global i2cSym_BaudError_Comment
    global i2cSym_OperatingMode
    global i2csSym_A10M
    global masterIntDict
    global slaveIntDict
    global busIntDict
    global i2cSymIntEnableComment
    global InterruptList

    masterIntDict = {}
    slaveIntDict = {}
    busIntDict = {}
    InterruptList = []

    i2cInstanceName = i2cComponent.createStringSymbol("I2C_INSTANCE_NAME", None)
    i2cInstanceName.setVisible(False)
    i2cInstanceName.setDefaultValue(i2cComponent.getID().upper())

    i2cInstanceNum = i2cComponent.createStringSymbol("I2C_INSTANCE_NUM", None)
    i2cInstanceNum.setVisible(False)
    componentName = str(i2cComponent.getID())
    instanceNum = componentName[3]
    i2cInstanceNum.setDefaultValue(instanceNum)

    i2cSym_OperatingMode = i2cComponent.createComboSymbol("I2C_OPERATING_MODE", None, modelist)
    i2cSym_OperatingMode.setLabel("Operating Mode")
    i2cSym_OperatingMode.setDefaultValue("Master")
    i2cSym_OperatingMode.setDependencies(interruptSetupOnModeChange, ["I2C_OPERATING_MODE"])

    #Clock enable
    Database.setSymbolValue("core", i2cInstanceName.getValue() + "_CLOCK_ENABLE", True, 1)

    ## I2C Clock Frequency
    i2cSym_ClkValue = i2cComponent.createIntegerSymbol("I2C_CLOCK_FREQ", None)
    i2cSym_ClkValue.setLabel("I2C Clock Frequency")
    i2cSym_ClkValue.setMin(0)
    i2cSym_ClkValue.setReadOnly(True)
    i2cSym_ClkValue.setVisible(False)
    i2cSym_ClkValue.setDefaultValue(int(Database.getSymbolValue("core", i2cInstanceName.getValue() + "_CLOCK_FREQUENCY")))
    i2cSym_ClkValue.setDependencies(i2cSourceFreq, ["core." + i2cInstanceName.getValue() + "_CLOCK_FREQUENCY"])

    # 10-bit addressing
    i2csSym_A10M = i2cComponent.createBooleanSymbol("I2CS_A10M_SUPPORT", None)
    i2csSym_A10M.setLabel("Enable 10-bit Addressing")
    i2csSym_A10M.setVisible(False)
    i2csSym_A10M.setDefaultValue(False)
    i2csSym_A10M.setDependencies(slaveModeVisibility, ["I2C_OPERATING_MODE"])

    #Slave Address
    i2csSym_ADDR = i2cComponent.createHexSymbol("I2C_SLAVE_ADDDRESS", None)
    i2csSym_ADDR.setLabel("I2C Slave Address (7-bit)")
    i2csSym_ADDR.setMax(1023)
    i2csSym_ADDR.setVisible(False)
    i2csSym_ADDR.setDefaultValue(0x54)
    i2csSym_ADDR.setDependencies(slaveModeVisibility, ["I2C_OPERATING_MODE", "I2CS_A10M_SUPPORT"])

    #DISSLW: Slew Rate Control Disable bit
    i2cSym_SlewRateControl = i2cComponent.createBooleanSymbol("I2C_DISSLW", None)
    i2cSym_SlewRateControl.setLabel("Disable Slew Rate Control")

    #SMEN: SMBus Input Levels bit
    i2cSym_SMBusInputLevels = i2cComponent.createBooleanSymbol("I2C_SMEN", None)
    i2cSym_SMBusInputLevels.setLabel("SMBus Input Levels")

    #SIDL: Stop in Idle Mode bit
    i2cSym_StopInIdleMode = i2cComponent.createBooleanSymbol("I2C_SIDL", None)
    i2cSym_StopInIdleMode.setLabel("Stop in Idle Mode bit")

    #Baud Rate
    i2cSym_BAUD = i2cComponent.createLongSymbol("I2C_CLOCK_SPEED", None)
    i2cSym_BAUD.setLabel("I2C Baud Rate (Hz)")
    i2cSym_BAUD.setDefaultValue(50000)
    i2cSym_BAUD.setMin(1)
    i2cSym_BAUD.setMax(1000000)
    i2cSym_BAUD.setDependencies(masterModeVisibility, ["I2C_OPERATING_MODE"])

    i2cSym_BAUD_HZ = i2cComponent.createLongSymbol("I2C_CLOCK_SPEED_HZ", None)
    i2cSym_BAUD_HZ.setLabel("I2C Baud Rate (Hz)")
    i2cSym_BAUD_HZ.setDefaultValue(i2cSym_BAUD.getValue())
    i2cSym_BAUD_HZ.setVisible(False)
    i2cSym_BAUD_HZ.setDependencies(updateI2CBaudHz, ["I2C_CLOCK_SPEED"])

    #I2C Baud Rate not supported comment
    i2cSym_BaudError_Comment = i2cComponent.createCommentSymbol("I2C_BAUD_ERROR_COMMENT", None)
    i2cSym_BaudError_Comment.setLabel("********** WARNING!: Baud Rate is out of range **********")
    i2cSym_BaudError_Comment.setVisible(False)
    i2cxBRG = i2cInstanceName.getValue() + "BRG"

    i2cxBRG_Bitfield = ATDF.getNode('/avr-tools-device-file/modules/module@[name="I2C"]/register-group@[name="I2C"]/register@[name="' + i2cxBRG + '"]/bitfield@[name="I2CBRG"]')
    i2cMaxBRG = int(str(i2cxBRG_Bitfield.getAttribute("mask")), 0)

    i2cSymMaxBRG = i2cComponent.createIntegerSymbol("I2C_MAX_BRG", None)
    i2cSymMaxBRG.setDefaultValue(i2cMaxBRG)
    i2cSymMaxBRG.setVisible(False)

    ## Baud Rate Frequency dependency
    i2cSym_BRGValue = i2cComponent.createIntegerSymbol("BRG_VALUE", None)
    i2cSym_BRGValue.setVisible(False)
    i2cSym_BRGValue.setDependencies(baudRateTrigger, ["I2C_CLOCK_SPEED", "core." + i2cInstanceName.getValue() + "_CLOCK_FREQUENCY"])

    #Use setValue instead of setDefaultValue to store symbol value in default.xml
    i2cSym_BRGValue.setValue(baudRateCalc(i2cSym_ClkValue.getValue(), i2cSym_BAUD.getValue()) , 1)

    # SDAHT (SDA Hold Time Bit)
    i2cxCON = i2cInstanceName.getValue() + "CON"

    i2cxCON_SDAHT = ATDF.getNode('/avr-tools-device-file/modules/module@[name="I2C"]/register-group@[name="I2C"]/register@[name="' + i2cxCON + '"]/bitfield@[name="SDAHT"]')

    if i2cxCON_SDAHT != None:
        i2cxCON_SDAHT_ValueGroup = ATDF.getNode('/avr-tools-device-file/modules/module@[name="I2C"]/value-group@[name="' + i2cxCON_SDAHT.getAttribute("values") + '"]')

        i2cCON_SDAHT_Support = i2cComponent.createKeyValueSetSymbol("I2CS_SDAHT_SUPPORT", None)
        i2cCON_SDAHT_Support.setLabel("SDA Hold Time")
        i2cCON_SDAHT_Support.addKey(i2cxCON_SDAHT_ValueGroup.getChildren()[0].getAttribute("value"), "0" , i2cxCON_SDAHT_ValueGroup.getChildren()[0].getAttribute("caption"))
        i2cCON_SDAHT_Support.addKey(i2cxCON_SDAHT_ValueGroup.getChildren()[1].getAttribute("value"), "1" , i2cxCON_SDAHT_ValueGroup.getChildren()[1].getAttribute("caption"))
        i2cCON_SDAHT_Support.setOutputMode("Key")
        i2cCON_SDAHT_Support.setDisplayMode("Description")
        i2cCON_SDAHT_Support.setDefaultValue(1)
        i2cCON_SDAHT_Support.setVisible(True)

    #I2C Forced Write API Inclusion
    i2cSym_ForcedWrite = i2cComponent.createBooleanSymbol("I2C_INCLUDE_FORCED_WRITE_API", None)
    i2cSym_ForcedWrite.setLabel("Include Force Write I2C Function" + "\r\n" + "(Master Mode Only - Ignore NACK from Slave)")
    i2cSym_ForcedWrite.setDefaultValue(False)
    i2cSym_ForcedWrite.setVisible(True)
    i2cSym_ForcedWrite.setDependencies(masterModeVisibility, ["I2C_OPERATING_MODE"])

    ## Master Interrupt Setup (List index 0)
    i2cMasterInt = i2cInstanceName.getValue() + "_MASTER"

    masterIntDict["type"] = modelist[0]
    masterIntDict["InterruptVector"] = i2cMasterInt + "_INTERRUPT_ENABLE"
    masterIntDict["InterruptHandler"] = i2cMasterInt + "_INTERRUPT_HANDLER"
    masterIntDict["InterruptHandlerLock"] = i2cMasterInt + "_INTERRUPT_HANDLER_LOCK"
    masterIntDict["InterruptUpdate"] = i2cMasterInt + "_INTERRUPT_ENABLE_UPDATE"
    InterruptList.append(masterIntDict)

    MasterVectorNum = int(getIRQnumber(i2cMasterInt))
    enblRegName = _get_enblReg_parms(MasterVectorNum)

    statRegName = _get_statReg_parms(MasterVectorNum)

    #IEC REG
    i2cMasterIntIEC = i2cComponent.createStringSymbol("I2C_MASTER_IEC_REG", None)
    i2cMasterIntIEC.setDefaultValue(enblRegName)
    i2cMasterIntIEC.setVisible(False)

    # find the correct bit name for bus collision error interrupt IECx.BCIE or IECx.BIE
    IEC_BCIE = ATDF.getNode('/avr-tools-device-file/modules/module@[name="INT"]/register-group@[name="INT"]/register@[name="' + enblRegName + '"]/bitfield@[name="' + i2cInstanceName.getValue() + "BCIE" + '"]')
    IEC_BIE = ATDF.getNode('/avr-tools-device-file/modules/module@[name="INT"]/register-group@[name="INT"]/register@[name="' + enblRegName + '"]/bitfield@[name="' + i2cInstanceName.getValue() + "BIE" + '"]')
    i2cBusCollisionIntEnableBitName = i2cComponent.createStringSymbol("I2C_BUS_COLLISION_INT_ENABLE_BIT_NAME", None)
    i2cBusCollisionIntEnableBitName.setVisible(False)
    if IEC_BCIE is not None:
        i2cBusCollisionIntEnableBitName.setDefaultValue(IEC_BCIE.getAttribute("name"))
    elif IEC_BIE is not None:
        i2cBusCollisionIntEnableBitName.setDefaultValue(IEC_BIE.getAttribute("name"))

    #IFS REG
    i2cMasterIntIFS = i2cComponent.createStringSymbol("I2C_MASTER_IFS_REG", None)
    i2cMasterIntIFS.setDefaultValue(statRegName)
    i2cMasterIntIFS.setVisible(False)

    # find the correct bit name for bus collision error interrupt IFSx.BCIF or IFSx.BIF
    IFS_BCIE = ATDF.getNode('/avr-tools-device-file/modules/module@[name="INT"]/register-group@[name="INT"]/register@[name="' + statRegName + '"]/bitfield@[name="' + i2cInstanceName.getValue() + "BCIF" + '"]')
    IFS_BIE = ATDF.getNode('/avr-tools-device-file/modules/module@[name="INT"]/register-group@[name="INT"]/register@[name="' + statRegName + '"]/bitfield@[name="' + i2cInstanceName.getValue() + "BIF" + '"]')
    i2cBusCollisionIntFlagBitName = i2cComponent.createStringSymbol("I2C_BUS_COLLISION_INT_FLAG_BIT_NAME", None)
    i2cBusCollisionIntFlagBitName.setVisible(False)
    if IFS_BCIE is not None:
        i2cBusCollisionIntFlagBitName.setDefaultValue(IFS_BCIE.getAttribute("name"))
    elif IFS_BIE is not None:
        i2cBusCollisionIntFlagBitName.setDefaultValue(IFS_BIE.getAttribute("name"))

    ## Slave Interrupt Setup (List index 1)
    i2cSlaveInt = i2cInstanceName.getValue() + "_SLAVE"

    slaveIntDict["type"] = modelist[1]
    slaveIntDict["InterruptVector"] = i2cSlaveInt + "_INTERRUPT_ENABLE"
    slaveIntDict["InterruptHandler"] = i2cSlaveInt + "_INTERRUPT_HANDLER"
    slaveIntDict["InterruptHandlerLock"] = i2cSlaveInt + "_INTERRUPT_HANDLER_LOCK"
    slaveIntDict["InterruptUpdate"] = i2cSlaveInt + "_INTERRUPT_ENABLE_UPDATE"
    InterruptList.append(slaveIntDict)

    SlaveVectorNum = int(getIRQnumber(i2cSlaveInt))
    enblRegName = _get_enblReg_parms(SlaveVectorNum)
    statRegName = _get_statReg_parms(SlaveVectorNum)

    #IEC REG
    i2cSlaveIntIEC = i2cComponent.createStringSymbol("I2C_SLAVE_IEC_REG", None)
    i2cSlaveIntIEC.setDefaultValue(enblRegName)
    i2cSlaveIntIEC.setVisible(False)

    #IFS REG
    i2cSlaveIntIFS = i2cComponent.createStringSymbol("I2C_SLAVE_IFS_REG", None)
    i2cSlaveIntIFS.setDefaultValue(statRegName)
    i2cSlaveIntIFS.setVisible(False)

    ## Bus Error Interrupt Setup (List index 2)
    i2cBusInt = i2cInstanceName.getValue() + "_BUS"

    busIntDict["type"] = "Bus"
    busIntDict["InterruptVector"] = i2cBusInt + "_INTERRUPT_ENABLE"
    busIntDict["InterruptHandler"] = i2cBusInt + "_INTERRUPT_HANDLER"
    busIntDict["InterruptHandlerLock"] = i2cBusInt + "_INTERRUPT_HANDLER_LOCK"
    busIntDict["InterruptUpdate"] = i2cBusInt + "_INTERRUPT_ENABLE_UPDATE"
    InterruptList.append(busIntDict)

    BusVectorNum = int(getIRQnumber(i2cBusInt))
    enblRegName = _get_enblReg_parms(BusVectorNum)
    statRegName = _get_statReg_parms(BusVectorNum)

    #IEC REG
    i2cBusIntIEC = i2cComponent.createStringSymbol("I2C_BUS_IEC_REG", None)
    i2cBusIntIEC.setDefaultValue(enblRegName)
    i2cBusIntIEC.setVisible(False)

    #IFS REG
    i2cBusIntIFS = i2cComponent.createStringSymbol("I2C_BUS_IFS_REG", None)
    i2cBusIntIFS.setDefaultValue(statRegName)
    i2cBusIntIFS.setVisible(False)

    # Check if the following bit fields exist:
    i2cxCON = i2cInstanceName.getValue() + "CON"

    # AHEN (Address Hold Enable Bit)
    i2cxCON_AHEN = ATDF.getNode('/avr-tools-device-file/modules/module@[name="I2C"]/register-group@[name="I2C"]/register@[name="' + i2cxCON + '"]/bitfield@[name="AHEN"]')

    # DHEN (Data Hold Enable Bit)
    i2cxCON_DHEN = ATDF.getNode('/avr-tools-device-file/modules/module@[name="I2C"]/register-group@[name="I2C"]/register@[name="' + i2cxCON + '"]/bitfield@[name="DHEN"]')

    if i2cxCON_AHEN != None and i2cxCON_DHEN != None:
        i2cCON_AHEN_DHEN_Support = i2cComponent.createBooleanSymbol("I2CS_AHEN_DHEN_SUPPORT", None)
        i2cCON_AHEN_DHEN_Support.setLabel("Enable Address and Data Hold")
        i2cCON_AHEN_DHEN_Support.setVisible(i2cSym_OperatingMode.getValue() == "Slave")
        i2cCON_AHEN_DHEN_Support.setDefaultValue(True)
        i2cCON_AHEN_DHEN_Support.setDependencies(slaveModeVisibility, ["I2C_OPERATING_MODE"])

    # PCIE (Stop Bit Interrupt Enable Bit)
    i2cxCON_PCIE = ATDF.getNode('/avr-tools-device-file/modules/module@[name="I2C"]/register-group@[name="I2C"]/register@[name="' + i2cxCON + '"]/bitfield@[name="PCIE"]')

    if i2cxCON_PCIE != None:
        i2cCON_PCIE_Support = i2cComponent.createBooleanSymbol("I2CS_PCIE_SUPPORT", None)
        i2cCON_PCIE_Support.setLabel("Enable Stop Condition Interrupt")
        i2cCON_PCIE_Support.setVisible(False)
        i2cCON_PCIE_Support.setDefaultValue(True)

    SysClkFreq=Database.getSymbolValue("core", "SYS_CLK_FREQ")
    timerFrequency=int(SysClkFreq)/2

    i2cSymCoretimerFrequency = i2cComponent.createIntegerSymbol("I2CS_CORE_TIMER_FREQUENCY", None)
    i2cSymCoretimerFrequency.setVisible(False)
    i2cSymCoretimerFrequency.setDefaultValue(timerFrequency)
    i2cSymCoretimerFrequency.setDependencies(coreFreqUpdate, ["core.SYS_CLK_FREQ"])

    i2cSymSetupAndRiseTime = i2cComponent.createKeyValueSetSymbol("I2CS_SETUP_RISE_TIME", None)
    i2cSymSetupAndRiseTime.setLabel("Setup and Rise Time")
    i2cSymSetupAndRiseTime.addKey("0", "0" , "100 kHz - Setup time 250ns, Rise time 1000ns")
    i2cSymSetupAndRiseTime.addKey("1", "1" , "400 kHz - Setup time 100ns, Rise time 300ns")
    i2cSymSetupAndRiseTime.addKey("2", "2" , "1000 kHz - Setup time 50ns, Rise time 120ns")
    i2cSymSetupAndRiseTime.setOutputMode("Key")
    i2cSymSetupAndRiseTime.setDisplayMode("Description")
    i2cSymSetupAndRiseTime.setDefaultValue(1)
    i2cSymSetupAndRiseTime.setVisible(i2cSym_OperatingMode.getValue() == "Slave")
    i2cSymSetupAndRiseTime.setDependencies(slaveModeVisibility, ["I2C_OPERATING_MODE"])

    setupRiseTime = I2CS_RISE_SETUP_TIME[int(i2cSymSetupAndRiseTime.getValue())]

    i2cSymSetupTimeCoreTimerCnts = i2cComponent.createIntegerSymbol("I2CS_SETUP_TIME_CORE_TIMER_CNTS", None)
    i2cSymSetupTimeCoreTimerCnts.setVisible(False)
    i2cSymSetupTimeCoreTimerCnts.setValue(calcSetupAndRiseTimeCnt(i2cSymCoretimerFrequency.getValue(), setupRiseTime[0]))
    i2cSymSetupTimeCoreTimerCnts.setDependencies(updateSetupAndRiseTime, ["I2CS_SETUP_RISE_TIME", "I2CS_CORE_TIMER_FREQUENCY"])

    i2cSymRiseTimeCoreTimerCnts = i2cComponent.createIntegerSymbol("I2CS_RISE_TIME_CORE_TIMER_CNTS", None)
    i2cSymRiseTimeCoreTimerCnts.setVisible(False)
    i2cSymRiseTimeCoreTimerCnts.setValue(calcSetupAndRiseTimeCnt(i2cSymCoretimerFrequency.getValue(), setupRiseTime[1]))
    i2cSymRiseTimeCoreTimerCnts.setDependencies(updateSetupAndRiseTime, ["I2CS_SETUP_RISE_TIME", "I2CS_CORE_TIMER_FREQUENCY"])

    # Interrupt Warning
    i2cSymIntEnableComment = i2cComponent.createCommentSymbol("I2C_INTRRUPT_ENABLE_COMMENT", None)
    i2cSymIntEnableComment.setLabel("Warning!!! " + i2cInstanceName.getValue() + " Interrupt is Disabled in Interrupt Manager")
    i2cSymIntEnableComment.setVisible(False)
    i2cSymIntEnableComment.setDependencies(interruptSetupChangeHandler, ["core." + i2cInstanceName.getValue() + "_MASTER" + "_INTERRUPT_ENABLE_UPDATE", "core." + i2cInstanceName.getValue() + "_SLAVE" + "_INTERRUPT_ENABLE_UPDATE", "core." + i2cInstanceName.getValue() + "_BUS" + "_INTERRUPT_ENABLE_UPDATE"] )


    # Clock Warning
    i2cSym_ClkEnComment = i2cComponent.createCommentSymbol("I2C_CLOCK_ENABLE_COMMENT", None)
    i2cSym_ClkEnComment.setLabel("Warning!!! " + i2cInstanceName.getValue() + " Peripheral Clock is Disabled in Clock Manager")
    i2cSym_ClkEnComment.setVisible(False)
    i2cSym_ClkEnComment.setDependencies(updateI2CClockWarningStatus, ["core." + i2cInstanceName.getValue() + "_CLOCK_ENABLE"])

    # Enable interrupts in EVIC
    interruptSetup(i2cSym_OperatingMode.getValue(), True)

    ###################################################################################################
    ####################################### Driver Symbols ############################################
    ###################################################################################################

    #I2C API Prefix
    i2cSym_API_Prefix = i2cComponent.createStringSymbol("I2C_PLIB_API_PREFIX", None)
    i2cSym_API_Prefix.setDefaultValue(i2cInstanceName.getValue())
    i2cSym_API_Prefix.setVisible(False)

    ###################################################################################################
    ####################################### Code Generation  ##########################################
    ###################################################################################################

    configName = Variables.get("__CONFIGURATION_NAME")

    i2cMasterHeaderFile = i2cComponent.createFileSymbol("I2C_MASTER_HEADER", None)
    i2cMasterHeaderFile.setSourcePath("../peripheral/i2c_01441/templates/plib_i2c_master.h.ftl")
    i2cMasterHeaderFile.setOutputName("plib_" + i2cInstanceName.getValue().lower() + "_master.h")
    i2cMasterHeaderFile.setDestPath("peripheral/i2c/master")
    i2cMasterHeaderFile.setProjectPath("config/" + configName + "/peripheral/i2c/master")
    i2cMasterHeaderFile.setType("HEADER")
    i2cMasterHeaderFile.setMarkup(True)
    i2cMasterHeaderFile.setEnabled(True)
    i2cMasterHeaderFile.setDependencies(masterFilesGeneration, ["I2C_OPERATING_MODE"])

    i2cMasterCommonHeaderFile = i2cComponent.createFileSymbol("I2C_MASTER_COMMON_HEADER", None)
    i2cMasterCommonHeaderFile.setSourcePath("../peripheral/i2c_01441/plib_i2c_master_common.h")
    i2cMasterCommonHeaderFile.setOutputName("plib_i2c_master_common.h")
    i2cMasterCommonHeaderFile.setDestPath("peripheral/i2c/master")
    i2cMasterCommonHeaderFile.setProjectPath("config/" + configName + "/peripheral/i2c/master")
    i2cMasterCommonHeaderFile.setType("HEADER")
    i2cMasterCommonHeaderFile.setEnabled(True)
    i2cMasterCommonHeaderFile.setDependencies(masterFilesGeneration, ["I2C_OPERATING_MODE"])

    i2cMasterSourceFile = i2cComponent.createFileSymbol("I2C_MASTER_SOURCE", None)
    i2cMasterSourceFile.setSourcePath("../peripheral/i2c_01441/templates/plib_i2c_master.c.ftl")
    i2cMasterSourceFile.setOutputName("plib_" + i2cInstanceName.getValue().lower() + "_master.c")
    i2cMasterSourceFile.setDestPath("peripheral/i2c/master")
    i2cMasterSourceFile.setProjectPath("config/" + configName +"/peripheral/i2c/master")
    i2cMasterSourceFile.setType("SOURCE")
    i2cMasterSourceFile.setMarkup(True)
    i2cMasterSourceFile.setEnabled(True)
    i2cMasterSourceFile.setDependencies(masterFilesGeneration, ["I2C_OPERATING_MODE"])

    i2cSlaveHeaderFile = i2cComponent.createFileSymbol("I2C_SLAVE_HEADER", None)
    i2cSlaveHeaderFile.setSourcePath("../peripheral/i2c_01441/templates/plib_i2c_slave.h.ftl")
    i2cSlaveHeaderFile.setOutputName("plib_" + i2cInstanceName.getValue().lower() + "_slave.h")
    i2cSlaveHeaderFile.setDestPath("peripheral/i2c/slave")
    i2cSlaveHeaderFile.setProjectPath("config/" + configName + "/peripheral/i2c/slave")
    i2cSlaveHeaderFile.setType("HEADER")
    i2cSlaveHeaderFile.setMarkup(True)
    i2cSlaveHeaderFile.setEnabled(False)
    i2cSlaveHeaderFile.setDependencies(slaveFilesGeneration, ["I2C_OPERATING_MODE"])

    i2cSlaveCommonHeaderFile = i2cComponent.createFileSymbol("I2C_SLAVE_COMMON_HEADER", None)
    i2cSlaveCommonHeaderFile.setSourcePath("../peripheral/i2c_01441/plib_i2c_slave_common.h")
    i2cSlaveCommonHeaderFile.setOutputName("plib_i2c_slave_common.h")
    i2cSlaveCommonHeaderFile.setDestPath("peripheral/i2c/slave")
    i2cSlaveCommonHeaderFile.setProjectPath("config/" + configName + "/peripheral/i2c/slave")
    i2cSlaveCommonHeaderFile.setType("HEADER")
    i2cSlaveCommonHeaderFile.setEnabled(False)
    i2cSlaveCommonHeaderFile.setDependencies(slaveFilesGeneration, ["I2C_OPERATING_MODE"])

    i2cSlaveSourceFile = i2cComponent.createFileSymbol("I2C_SLAVE_SOURCE", None)
    i2cSlaveSourceFile.setSourcePath("../peripheral/i2c_01441/templates/plib_i2c_slave.c.ftl")
    i2cSlaveSourceFile.setOutputName("plib_" + i2cInstanceName.getValue().lower() + "_slave.c")
    i2cSlaveSourceFile.setDestPath("peripheral/i2c/slave")
    i2cSlaveSourceFile.setProjectPath("config/" + configName +"/peripheral/i2c/slave")
    i2cSlaveSourceFile.setType("SOURCE")
    i2cSlaveSourceFile.setMarkup(True)
    i2cSlaveSourceFile.setEnabled(False)
    i2cSlaveSourceFile.setDependencies(slaveFilesGeneration, ["I2C_OPERATING_MODE"])

    i2cSystemInitFile = i2cComponent.createFileSymbol("I2C_INIT", None)
    i2cSystemInitFile.setType("STRING")
    i2cSystemInitFile.setOutputName("core.LIST_SYSTEM_INIT_C_SYS_INITIALIZE_PERIPHERALS")
    i2cSystemInitFile.setSourcePath("../peripheral/i2c_01441/templates/system/initialization.c.ftl")
    i2cSystemInitFile.setMarkup(True)

    i2cSystemDefFile = i2cComponent.createFileSymbol("I2C_DEF", None)
    i2cSystemDefFile.setType("STRING")
    i2cSystemDefFile.setOutputName("core.LIST_SYSTEM_DEFINITIONS_H_INCLUDES")
    i2cSystemDefFile.setSourcePath("../peripheral/i2c_01441/templates/system/definitions.h.ftl")
    i2cSystemDefFile.setMarkup(True)
