
# - This script function start communication with the MS by means of special commands defined for the MS,
# some of this commands returns relevant information about the MS like physical parameters.

import serial, time, sys

import Maxes as Mx
import PhysicalParameters as PhP

try:  # Link between Host and MicroScribe (Writing commands and reading data).

    def protocolo(TxRx):

        TxRx.flushInput()  # flush input buffer, discarding all its contents
        TxRx.flushOutput()  # flush output buffer, aborting current output

        TxRx.write(b'BEGIN')  # - Start linking
        D_ID = Comm(TxRx)
        D_ID = D_ID.decode("utf-8")
        # print("Device ID: ", D_ID, '\n')  # MSCR

        TxRx.write(bytes.fromhex('C8'))  # Get product name
        Pnm = str(Comm(TxRx))[6:-1]
        # print("Product Name: ", Pnm, '\n')  # ÈMicroScribe3D.

        TxRx.write(bytes.fromhex('C9'))  # Get Product ID
        P_ID2 = Comm(TxRx)
        # print("Product ID2: ", P_ID2, '\n')  # ÉMSCR.

        TxRx.write(bytes.fromhex('CA'))  # Get Model Name
        MN = str(Comm(TxRx))[6:-1]
        # print("Model Name: ", MN, '\n')  # ÊDX.

        TxRx.write(bytes.fromhex('CB'))  # Get Serial Number
        SN = str(Comm(TxRx))[6:-1]
        # print("Serial Number: ", SN, '\n')  # Ë40937.

        TxRx.write(bytes.fromhex('CC'))  # Get Comment string
        CS = str(Comm(TxRx))[6:-1]
        # print("Comments: ", CS, '\n')  # ÌStandard+Beta.

        TxRx.write(bytes.fromhex('CD'))  # Get parameter format
        PF = str(Comm(TxRx))[6:-1]
        # print("Parameter format: Denavit-Hartenberg form 0.5: ", PF, '\n')  # ÍFormat DH0.5.

        TxRx.write(bytes.fromhex('CE'))  # Get version
        FV = str(Comm(TxRx))[6:-1]
        # print("Firmware Version: ", FV, '\n')  # ÎHCI 2.0.

        TxRx.write(bytes.fromhex('C6'))  # Get pulses/ rev values for each encoder.
        ME = Comm(TxRx)
        print("Pulses per revolution of the encoders: ")
        Encoderfactor = Mx.PulseRev(ME)  # Pulses/Rev
        print('#------------------------------#')

        TxRx.write(bytes.fromhex('C0'))  # Request extra parameters to compute
        # all positions and orientations (Needed cause the comment is Standard+Beta)
        EP = Comm(TxRx)
        print("Physical Parameters: \n")
        TxRx.write(bytes.fromhex('D3'))  # Get Extra Extended Physical Parameters.
        EEP = Comm(TxRx)
        print("Extended Physical Parameters: ", '\n')

        [cA, sA, A, D, cB, sB] = PhP.PhParameters(EP, EEP)

        # TxRx.write(bytes.fromhex('D1')) # set home ref
        # EB = Comm(TxRx)
        # print("Encoder bits: ", EB)

        # REPORT_MOTION   0xCF
        # SET_HOME_REF    0xD0
        # RESTORE_FACTORY 0xD1
        # INSERT_MARKER   0xD2
        # GET_EXT_PARAMS  0xD3
        return Encoderfactor, cA, sA, A, D, cB, sB, D_ID, Pnm, MN, SN, CS, PF, FV


    # ---------------------------------------------------------- #

    # - This short function ask for the quantity of data in the buffer and read it.
    def Comm(TxRx):

        TxRx.inWaiting()
        time.sleep(0.10)
        Rm = TxRx.read(TxRx.inWaiting())  # Read response data from MicroScribe.

        return Rm

except KeyboardInterrupt:

    TxRx.write(b'END')
    TxRx.flushInput()  # flush input buffer, discarding all its contents
    TxRx.flushOutput()  # flush output buffer, aborting current output
    TxRx.flush()
    TxRx.close()
    print('Communication was interrupted manually', '\n')

except serial.portNotOpenError:
    print('You are trying to use a port that is not open', '\n')
