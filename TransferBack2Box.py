from opentrons import protocol_api

metadata = {
    'apiLevel': '2.3',
    'protocolName': 'simple protocol',
    'author': 'Will'
    }

#list of commands which transfer liquid and mix, then return tip back to box

def run(ctx):
    #300 ul pipette and tips [RIGHT MOUNT, SLOT 11]
    tips300 = [ctx.load_labware("opentrons_96_tiprack_300ul", 11, "Tips300")]
    m300 = ctx.load_instrument('p300_multi_gen2', 'right', tip_racks = tips300)
    #20 ul pipette and tips [LEFT MOUNT, SLOTS 7, 4, 10, 2] 
    tips20 = [ctx.load_labware("opentrons_96_tiprack_20ul", 7, "Tips20A"), ctx.load_labware("opentrons_96_tiprack_20ul", 4, "Tips20B")]
    m20 = ctx.load_instrument('p20_multi_gen2', 'left', tip_racks = tips20)

    def m20transfer(vol, source, dest, mixvol, mixrep):
        m20.pick_up_tip()
        m20.aspirate(vol, source)
        m20.dispense(vol, dest)
        if mixvol != 0 and mixrep != 0:
            m20.mix(mixvol, mixrep)
        m20.return_tip()
    
    def m300transfer(vol, source, dest, mixvol, mixrep):
        m300.pick_up_tip()
        m300.aspirate(vol, source)
        m300.dispense(vol, dest)
        if mixvol != 0 and mixrep != 0:
            m300.mix(mixvol, mixrep)
        m300.return_tip()