
# - This script function send the request coordinates command to the MicroScribe, read the response of
# serial communication, and call auxiliary functions to decode and compute the coordinates, return the end
# transformation matrix from base to stylus tip, the coordinates of the tip and the pedal status.

import serial, time
from numpy import*
import EncCounter as Enc
import DenavitH as DH

try:
    def request(TxRx):
        
        TxRx.flushInput()  # flush input buffer, discarding all its contents
        TxRx.flushOutput()  # flush output buffer, aborting current output
        TxRx.flush()
        # - Set the mode in which the data will be send from MS.

        # High speed tracking mode
        # TxRx.write(bytes.fromhex('02'))

        # Respond to motion mode
        # TxRx.write(bytes.fromhex('cf 00 32 03 0f 00 00 00 00 00 00 00 00 00 01 00 01 00 01 00 01 00 01 00 01'))

        # Encoder count mode
        TxRx.write(bytes.fromhex('03'))

    def read(TxRx, Encoderfactor, cA, sA, A, D, cB, sB):

        request(TxRx)  # Send the request command.
        TxRx.inWaiting()
        time.sleep(0.1)
        Readedbyte = TxRx.read(TxRx.inWaiting())  # Read response data from MicroScribe.
        #print(Readedbyte.hex())
        EncoderCounter = Enc.Counter(Readedbyte)
        #print(EncoderCounter)
        Th = divide(asarray(EncoderCounter),asarray(Encoderfactor))*(360)  # theta angles (Encoder angles).
        Th = insert(Th,len(Th),0)  # The last SR (In the stylus tip) doesn't have any deviation respect to the previous.
        
        for i in range(0,len(Th)):  # Check if the encoder counter exceed the value for one revolution.
            if Th[i] > 360:
                Th[i] = Th[i]-360
        
        # Apply the Denavit-Hartemberg method for direct kinematics.
        [M, coordinates] = DH.DH(Th, cA, sA, A, D, cB, sB)

        # - Check the status of the pedals
        if (bytes.fromhex('83 03') in Readedbyte):
            #Both pedals
            pedal = 'Both' 

        elif (bytes.fromhex('83 02') in Readedbyte):
            #left pedal
            pedal = 'left'

        elif (bytes.fromhex('83 01') in Readedbyte):
            #Right pedal
            pedal = 'Right'

        else:
            pedal = 'None'
        
        return M, coordinates, pedal

except KeyboardInterrupt:
    
    TxRx.write(b'END')
    TxRx.flushInput()  # flush input buffer, discarding all its contents
    TxRx.flushOutput()  # flush output buffer, aborting current output
    TxRx.flush()
    TxRx.close()
    print('Communication was interrupted manually', '\n')
    
except serial.portNotOpenError:
    print('You are trying to use a port that is not open')