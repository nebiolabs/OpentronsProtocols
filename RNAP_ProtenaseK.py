from opentrons import protocol_api


metadata = {
    'protocolName': 'RNAP 2 ProtenaseK',
    'author': 'Will <wobrien@neb.com>',
    'apiLevel': '2.13'
}

#Performs two RNAP misincorporation experiments sequentially and adds ProtenaseK to one

timepoints = [0, 0.25, 0.5, 1, 2, 5, 7.5, 10, 12.5, 15, 17.5, 20] #IN HOURS
def run(ctx):

    #SET-UP

    #load pipettes + tips
    tips300 = [ctx.load_labware("opentrons_96_tiprack_300ul", 11, "Tips300")]
    m300 =ctx.load_instrument('p300_multi_gen2', 'right', tip_racks = tips300)
   
    tips20 = [ctx.load_labware("opentrons_96_tiprack_20ul", 7, "Tips20A"), ctx.load_labware("opentrons_96_tiprack_20ul", 4, "Tips20B"), ctx.load_labware("opentrons_96_tiprack_20ul", 10, "Tips20C")]
    m20 = ctx.load_instrument('p20_multi_gen2', 'left', tip_racks = tips20)
 
    #load + set temp module
    temp_mod = ctx.load_module("temperature module gen2", 1)
    react = temp_mod.load_labware('biorad_96_wellplate_200ul_pcr', label = "Reaction")
    temp_mod.set_temperature(celsius = 25)
  
    #load plates
    finalA = ctx.load_labware('biorad_96_wellplate_200ul_pcr', 5, "FinalPlateA")
    finalB = ctx.load_labware('biorad_96_wellplate_200ul_pcr', 6, "FinalPlateB")
    FinalPlates = [finalA, finalB]

    #water set up
    reservoir = ctx.load_labware('nest_12_reservoir_15ml', 3,"Water")
    water = [reservoir.wells()[n] for n in range(2)]
    proK = reservoir.wells()[2]

    #liquid set up
    NTP = react.rows()[0][0:2]
    Enzyme = react.rows()[0][6:8]
    print(NTP)
    print(Enzyme)
    FinalWells = [FinalPlates[0].rows()[0]] + [FinalPlates[1].rows()[0]]

    
    #DEFINE FUNCTIONS
    #time point function
    def taketp(rxn, tp):
         m20.transfer(5, Enzyme[rxn], FinalWells[rxn][tp], mix_after = (2,10))
    
    #start plate function
    def runplate(tps, plate):
        #time point 0
        m20.transfer(2, Enzyme[plate], FinalWells[plate][0], mix_after = (2,7))
        #begin rxn
        m300.transfer(50, NTP[plate], Enzyme[plate], mix_after = (4, 75))
        #further time points
        for n in range(len(tps)-1):
            ctx.delay(minutes = (tps[n+1]-tps[n]))
            taketp(plate,n+1)
    #BEGIN PROTOCOL  
    for n in range(2):
        runplate(timepoints,n)
    
    #dilute with water
    for m in range(2):
        m300.distribute(100, water[m], [FinalWells[m][n].top() for n in range(len(FinalWells[m]))], new_tip = 'once')

    #Add ProK
    m20.distribute(1, proK, [FinalWells[0][n].top() for n in range(len(FinalWells[0]))], new_tip = 'once')
    #deactivate heat module
    temp_mod.deactivate()
