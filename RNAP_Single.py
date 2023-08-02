from opentrons import protocol_api
metadata = {
    'protocolName': 'RNAP Single',
    'author': 'Will <wobrien@neb.com>',
    'apiLevel': '2.13'
}
#performs a single RNAP misincorporation experiment
#Pick 12 time points (in minutes)
timepoints = [0, 0.25, 0.5, 1, 2, 5, 7.5, 10, 12.5, 15, 17.5, 20]
def run(ctx):
    
    #load tips
    tips20 = [ctx.load_labware("opentrons_96_tiprack_20ul", 7, "Tips20")]
    tips300 = [ctx.load_labware("opentrons_96_tiprack_300ul", 10, "Tips300")]
    
    #load pipettes
    m20 = ctx.load_instrument('p20_multi_gen2', 'left', tip_racks = tips20)
    m300 =ctx.load_instrument('p300_multi_gen2', 'right', tip_racks = tips300)
    
    #load + set temp module
    temp_mod = ctx.load_module("temperature module gen2", 1)
    react = temp_mod.load_labware('biorad_96_wellplate_200ul_pcr', label = "Reaction")
    temp_mod.set_temperature(celsius = 25)
  
    #load plate
    final = ctx.load_labware('biorad_96_wellplate_200ul_pcr', 5, "Final Plate")

    #load water
    reservoir = ctx.load_labware('nest_12_reservoir_15ml', 3,"Water")
    
    #liquid set up
    NTP = react.wells_by_name()['A1']
    Enzyme = react.wells_by_name()['A12']
    FinalWells = final.rows()[0]
    water = reservoir.wells()[0]


    #begin protocol
    #time point 0
    m20.transfer(2, Enzyme, FinalWells[0], mix_after = (3,7))
    #begin rxn
    m300.transfer(50, NTP, Enzyme, mix_after = (6, 75))
    
    #time point function
    def taketp(tp):
         m20.transfer(10, Enzyme, FinalWells[tp], mix_after = (3,15))
    
    #take timepoints
    for n in range(len(timepoints)-1):
        ctx.delay(minutes = (timepoints[n+1]-timepoints[n]))
        taketp(n+1)
    
    #dilute with water
    m300.distribute(100, water, [FinalWells[n].top() for n in range(len(FinalWells))], new_tip = 'once')

    #deactivate heat module
    temp_mod.deactivate()
