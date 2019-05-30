
# - This function script receives data from the initial communication with MicroScribe,
# then decode each parameter of the byte and return the pulse/revolution value for each encoder.

def bytetoint(Hexdata):
    
    some_bytes = bytes.fromhex(Hexdata)
    counter = int.from_bytes(some_bytes, byteorder='big')
    return counter

def PulseRev(Readedbyte):
    
    Byteinhex = Readedbyte.hex()

    C0H = Byteinhex[4:8] # Shoulder Yaw = Shoulder Pitch
    ShY = bytetoint(C0H) + 1
    ShP = ShY
    print('Shoulder Yaw = Shoulder Pitch ', ShY, 'Pulses/rev \n')

    C8H = Byteinhex[34:38] #Elbow = Wrist Roll
    C8I = bytetoint(C8H) + 1
    Eb = C8I
    #WR = Eb
    print('Elbow', Eb, 'Pulses/rev \n')
    
    C9H = Byteinhex[38:42] # Wrist Pitch
    C9I = bytetoint(C9H) + 1
    WP = C9I
    WR = WP
    print('Wrist Pitch = Wrist Roll ', C9I, 'Pulses/rev \n')
    
    #C10H = Byteinhex[42:46] # Wrist Pitch
    #C10I = bytetoint(C10H)
    #print(C10I)

    return ShY, ShP, Eb, WR, WP