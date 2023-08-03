from opentrons import protocol_api


metadata = {
    'protocolName': 'RNAP Multi Seq',
    'author': 'Will <wobrien@neb.com>',
    'apiLevel': '2.13'
}

#Performs multiple RNAP misincorporation experiments (for single plate, use RNAP Single protocol)
#Returns tip to box
#Place NTPs in first x rows, place enzyme in last x rows

#Number of Experiments (max 4, min 2)
exps = 4
#Pick 12 time points (in minutes)
timepoints = [0, 0.25, 0.5, 1, 2, 5, 7.5, 10, 12.5, 15, 17.5, 20]

def run(ctx):

    #SET-UP

    #load pipettes + tips
    #300 ul pipette and tips [RIGHT MOUNT, SLOT 11]
    tips300 = [ctx.load_labware("opentrons_96_tiprack_300ul", 11, "Tips300")]
    m300 =ctx.load_instrument('p300_multi_gen2', 'right', tip_racks = tips300)
    #20 ul pipette and tips [LEFT MOUNT, SLOTS 7, 4, 10, 2] 
    tips20 = [ctx.load_labware("opentrons_96_tiprack_20ul", 7, "Tips20A"), ctx.load_labware("opentrons_96_tiprack_20ul", 4, "Tips20B")] 
    if exps >= 3:
        tips20 = tips20 + [ctx.load_labware("opentrons_96_tiprack_20ul", 10, "Tips20C")] 
        if exps == 4:
            tips20 = tips20 + [ctx.load_labware("opentrons_96_tiprack_20ul", 2, "Tips20D")] 
    m20 = ctx.load_instrument('p20_multi_gen2', 'left', tip_racks = tips20) 
 
    #temp module [SLOT 1, 25C]
    temp_mod = ctx.load_module("temperature module gen2", 1) #[DO NOT CHANGE SLOT, ROBOT WILL COLLIDE DURING CALIBRATION]
    react = temp_mod.load_labware('biorad_96_wellplate_200ul_pcr', label = "Reaction")  #Change to 'vwr_96_aluminumblock_100ul' to use vwr 100 uL pcr plate on temp mod
    temp_mod.set_temperature(celsius=25)
  
    #load plates [SLOTS 5, 6, 8, 9]
    finalA = ctx.load_labware('biorad_96_wellplate_200ul_pcr', 5, "FinalPlateA") #Change to 'nestedcemult1_96_wellplate_300ul' to use nested CE plate on biorad 96 well plate
    finalB = ctx.load_labware('biorad_96_wellplate_200ul_pcr', 6, "FinalPlateB") # ''
    FinalPlates = [finalA, finalB]
    if exps >= 3:
        finalC = [ctx.load_labware('biorad_96_wellplate_200ul_pcr', 8, "FinalPlateC")] # ''
        FinalPlates = FinalPlates + finalC
        if exps >= 4:
            finalD = [ctx.load_labware('biorad_96_wellplate_200ul_pcr', 9, "FinalPlateD")] # ''
            FinalPlates = FinalPlates + finalD
    
    #water set up [SLOT 3]
    reservoir = ctx.load_labware('nest_12_reservoir_15ml', 3,"Water")
    water = [reservoir.wells()[n] for n in range(exps)] #Fill corresponding number of wells from L to R with water

    #liquid set up
    NTP = [react.rows()[0][n] for n in range(exps)] #Put NTP in first x rows
    Enzyme = [react.rows()[0][n+8] for n in range(exps)] #Put enzymes in x rows, starting from row 9
    FinalWells = []
    for n in range(exps):
        FinalWells = FinalWells + [FinalPlates[n].rows()[0]] #Create list of wells in CE plates
    
    #DEFINE FUNCTIONS
    #m20 transfer function
    def m20transfer(vol, source, dest, mixrep, mixvol):
        m20.pick_up_tip()
        m20.aspirate(vol, source)
        m20.dispense(vol, dest)
        if mixvol != 0 and mixrep != 0:
            m20.mix(mixrep, mixvol)
        m20.return_tip()
    
    #m300 transfer function
    def m300transfer(vol, source, dest, mixrep, mixvol):
        m300.pick_up_tip()
        m300.aspirate(vol, source)
        m300.dispense(vol, dest)
        if mixvol != 0 and mixrep != 0:
            m300.mix(mixrep, mixvol)
        m300.drop_tip()
    
    #time point function
    def taketp(rxn,tp):
        m20transfer(5, Enzyme[rxn], FinalWells[rxn][tp], 2,10)
    #runplate function
    def runplate(tps, plate):
        #time point 0
        m20transfer(2, Enzyme[plate], FinalWells[plate][0], 2,7)
        #begin rxn
        m300transfer(50, NTP[plate], Enzyme[plate], 4, 75)
        #further time points
        for n in range(len(tps)-1):
            ctx.delay(minutes = (tps[n+1]-tps[n]))
            taketp(plate,n+1)
    #BEGIN PROTOCOL  
    for n in range(exps):
        runplate(timepoints,n)
    
    #dilute with water
    for m in range(exps):
        m300.distribute(100, water[m], [FinalWells[m][n].top() for n in range(len(FinalWells[m]))], new_tip = 'once', disposal_volume = 5)

    #deactivate heat module
    temp_mod.deactivate()
