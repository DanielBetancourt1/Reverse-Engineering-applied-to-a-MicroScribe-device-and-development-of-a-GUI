
# - This script function receive the byte read from microScribe, extract the encoders counters and
# return them as integers.

import struct

def bytetoint(Hexdata):
    
    some_bytes = bytes.fromhex(Hexdata)
    counter = int.from_bytes(some_bytes, byteorder='big')/2
    counter = counter + int.from_bytes(bytes.fromhex(Hexdata[2:4]), byteorder='big')/2
    return counter

def Counter(Readedbyte):

    Byteinhex = Readedbyte.hex()

    C0H = Byteinhex[4:8]  # Counter 0 in Hex.
    C0I = bytetoint(C0H) 
    #print(C0I)
    
    C1H = Byteinhex[8:12] 
    C1I = bytetoint(C1H) 
    #print(C1I)
    
    C2H = Byteinhex[12:16]
    C2I = bytetoint(C2H) 
    #print(C2I)
    
    C3H = Byteinhex[16:20]
    C3I = bytetoint(C3H) 
    #print(C3I)
    
    C4H = Byteinhex[20:24]
    C4I = bytetoint(C4H) 
    #print(C4I)
    return C0I, C1I, C2I, C3I, C4I