from opentrons import protocol_api


metadata = {
    'protocolName': 'SENP1 Testing',
    'author': 'Will <wobrien@neb.com>, Daisy <dconnors@neb.com>',
    'apiLevel': '2.13'
}
#preforms SENP1 cleavage kinetics assay for up to one plate of formulations

# Number of formulations (max 10 rn)
NumForms = 11
# RecA Volume (uL)
RAVol = 40
# SENP1 Volume (uL)
SenVol = 20
def run(ctx):

    #SET-UP

    #load pipettes + tips
    #300 ul pipette and tips [RIGHT MOUNT, SLOT 11]
    tips300 = [ctx.load_labware("opentrons_96_tiprack_300ul", 11, "Tips300")]
    p300=ctx.load_instrument('p300_single_gen2', 'right', tip_racks = tips300)
    #20 ul pipette and tips [LEFT MOUNT, SLOT 10] 
    tips20 = [ctx.load_labware("opentrons_96_tiprack_20ul", 10, "Tips20A")]
    p20 = ctx.load_instrument('p20_single_gen2', 'left', tip_racks = tips20) 
    
    #load labware [SLOTS 5, 6]
    TpPlate = ctx.load_labware('biorad_96_wellplate_200ul_pcr', 5, "Time Point Plate") #Change to 'nestedcemult1_96_wellplate_300ul' to use nested CE plate on biorad 96 well plate
    Timepoints = [TpPlate.columns()[n][0:7] for n in range(12)]
    FormPlate = ctx.load_labware('biorad_96_wellplate_200ul_pcr', 6, "Formulation Plate") # ''
    Formulation = [FormPlate.rows()[0][n] for n in range(12)]

    # Reagent set up [SLOT 4]
    TubeRack = ctx.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', 4,"Reagent Rack")
    RecA = TubeRack.wells()[0]
    SENP1 = TubeRack.wells()[1]
    
    #DEFINE FUNCTIONS
    #time point function
    def taketp(form,tp):
        p20.transfer(5, Formulation[form], Timepoints[form][tp], mix_after  = (5, 6))

    #Begin formulation function
    def formstart(form):
        p300.transfer(RAVol, RecA, Formulation[form], mix_after = (5, 25))
        p300.transfer(SenVol, SENP1, Formulation[form], mix_after = (5, 25))
        p20.transfer(5, Formulation[form], Timepoints[form][0], mix_after = (5, 6))


    #BEGIN PROTOCOL  
    #Each time point 10 minutes apart (-8 sec delay per other formulation)
    delay = 10/NumForms - .08*NumForms
    #start plates
    for n in range(NumForms):
        formstart(n)
        ctx.delay(minutes = delay)
    #take timepoints
    for n in range(1,7):
        for m in range(NumForms):
            taketp(m,n)
            ctx.delay(minutes = delay)

    
