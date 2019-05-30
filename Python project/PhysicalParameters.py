
# - This function script receives data from the initial communication with MicroScribe,
# then decode each parameter of the byte and return the Physical parameters of the MS
# as angles and lengths for the DH method

import struct
#from numpy import*
from numpy import  divide, pi, array, cos, sin

def bytetoint(Hexdata):
    
    some_bytes = bytes.fromhex(Hexdata)
    counter = int.from_bytes(some_bytes, byteorder='big', signed=True)
    return counter

def PhParameters(Readedbyte, Readedbyte2):

    Byteinhex = Readedbyte.hex()
    Byteinhex2 = Readedbyte2.hex()

    ALPHA0H = Byteinhex[4:8]  # Alpha_0 value in Hex.
    ALPHA0I = bytetoint(ALPHA0H)  # Alpha_0 value in int.
    #print(ALPHA0I)
    
    ALPHA1H = Byteinhex[8:12] 
    ALPHA1I = bytetoint(ALPHA1H) 
    #print(ALPHA1I)
    
    ALPHA2H = Byteinhex[12:16]
    ALPHA2I = bytetoint(ALPHA2H)
    #print(ALPHA2I)
    
    ALPHA3H = Byteinhex[16:20]
    ALPHA3I = bytetoint(ALPHA3H)
    #print(ALPHA3I)
    
    ALPHA4H = Byteinhex[20:24]
    ALPHA4I = bytetoint(ALPHA4H)
    #print(ALPHA4I)
    
    ALPHA5H = Byteinhex[24:28]
    ALPHA5I = bytetoint(ALPHA5H)
    #print(ALPHA5I)
    
    A0H = Byteinhex[28:32]
    A0I = bytetoint(A0H)
    #print(A0I)
    
    A1H = Byteinhex[32:36]
    A1I = bytetoint(A1H)
    #print(A1I)
    
    A2H = Byteinhex[36:40]
    A2I = bytetoint(A2H)
    #print('Link2', A2I)
    
    A3H = Byteinhex[40:44]
    A3I = bytetoint(A3H)
    #print(A3I)
    
    A4H = Byteinhex[44:48]
    A4I = bytetoint(A4H)
    #print('Link5x', A4I)
    
    A5H = Byteinhex[48:52]
    A5I = bytetoint(A5H)
    #print(A5I)
    
    D0H = Byteinhex[52:56]
    D0I = bytetoint(D0H)
    #print('Link1', D0I)
    
    D1H = Byteinhex[56:60]
    D1I = bytetoint(D1H)
    #print(D1I)
    
    D2H = Byteinhex[60:64]
    D2I = bytetoint(D2H)
    #print(D2I)
    
    D3H = Byteinhex[64:68]
    D3I = bytetoint(D3H)
    #print('Link3', D3I)
    
    D4H = Byteinhex[68:72]
    D4I = bytetoint(D4H)
    #print('Link4Z', D4I)
    
    D5H = Byteinhex[72:76]
    D5I = bytetoint(D5H)
    #print('link5', D5I)
    
    BtH = Byteinhex2[4:8]
    BtI = bytetoint(BtH)
    #print('link5', D5I)

    Alpha = pi*divide(array([ALPHA0I, ALPHA1I, ALPHA2I, ALPHA3I, ALPHA4I, ALPHA5I]),32768) #Covertion factor
    A = divide(array([A0I, A1I, A2I, A3I, A4I, A5I]), 1000)
    D = divide(array([D0I, D1I, D2I, D3I, D4I, D5I]), 1000)
    BtI = pi*BtI/32768
    
    cA = [cos(i) for i in Alpha] # Get the cosines of all Alpha angles
    sA = [sin(i) for i in Alpha]
    cB = cos(BtI)
    sB = sin(BtI)
    
    print('Alpha [Rad]: \n', Alpha, '\n', '"A" length [Inches]: \n', A, '\n' ' "D" Length [Inches]: \n', D, '\n', 'Betha [Rad]: \n', BtI, '\n')
    
    return cA, sA, A, D, cB, sB