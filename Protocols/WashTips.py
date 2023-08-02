from opentrons import protocol_api

metadata = {
    'protocolName': 'Wash Tips',
    'author': 'Will <wobrien@neb.com>',
    'apiLevel': '2.13'
}

#list of functionss which wash tip in reservoir

def run(ctx):
    #SET UP

    #300 ul pipette and tips [RIGHT MOUNT, SLOT 11]
    tips300 = [ctx.load_labware("opentrons_96_tiprack_300ul", 11, "Tips300")]
    m300 =ctx.load_instrument('p300_multi_gen2', 'right', tip_racks = tips300)
    #20 ul pipette and tips [LEFT MOUNT, SLOT 4] 
    tips20 = [ctx.load_labware("opentrons_96_tiprack_20ul", 4, "Tips20B")]
    m20 = ctx.load_instrument('p20_multi_gen2', 'left', tip_racks = tips20)

    #reservoir [Slot 3]
    reservoir = ctx.load_labware("agilent_1_reservoir_290ml", 3, "Water")

    #wash command
    def wash20():
        m20.mix(10, 15, reservoir.wells()[0], rate = 2.95)
    def wash300():
        m300.mix(10, 150, reservoir.wells()[0], rate = 2.95)
    m20.pick_up_tip()
    wash20()
    m300.pick_up_tip()
    wash300()


hello world 

hello world v2
