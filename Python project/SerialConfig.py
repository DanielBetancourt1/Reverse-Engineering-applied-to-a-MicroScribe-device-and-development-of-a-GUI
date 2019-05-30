
# - This script receive the general serial parameters, configure the others specific parameters and
# open the serial port verifying that is linked with a MicroScribe.

import serial
import sys
import time
from serial import SerialException

try:
    
    def configport(port, brate):
        
        # - Serial port name
        TxRx = serial.Serial()  # Variable name

        TxRx.port = port  # Port is a device name: depending on operating system.
                        # e.g.'/dev/ttyUSB0' on GNU/Linux or 'COM3' on Windows
                
        # - Communication parameters
        TxRx.baudrate = brate #115200
        TxRx.DataBits = 8
        TxRx.stopbits = 1
        TxRx.parity = 'N'
          
        # - Set Timeouts
        TxRx.timeout = None 
        TxRx.read_timeout = None
        TxRx.write_timeout = None
        TxRx.ReadTotalTimeoutConstant = 0
        TxRx.WriteTotalTimeoutConstant = 0
        TxRx.ReadInterval = 0 

        # - Disable parameters RTS & DTR (Hardware flow control)
        TxRx.rtscts = False  # Disable hardware (RTS/CTS) flow control.
        TxRx.dsrdtr = False  # Disable hardware (DSR/DTR) flow control.
        TxRx.setRTS(False)  # RTS Request to send
        TxRx.setDTR(False)  # DTR Data terminal ready
         
        # - Disable software flow control
        serial.XON = 0x00 
        serial.XOFF = 0x00
        serial.xonxoff = False 

        portStt = TxRx.getSettingsDict()  # Save port settings
        
        try:
            TxRx.open()
        except SerialException:
            if TxRx.isOpen():
                print('Port already open')
            else:
                print('Port already open, in use or device unplugged')
                TxRx.close()
                sys.exit()

        TxRx.ReadInterval = 0
        serial.xonxoff = False 
        
        # - Check if port is open and print name.
        if TxRx.isOpen():
            print ('Port is open: ' + TxRx.portstr, '\n')
            
            print("Establishing communication" '\n')
        
            TxRx.write(bytes.fromhex('49 4D 4D 43'))  # b'IMMC'
            
            Rm = Comm(TxRx)  # Read the initial response (It must be IMMC).
            print("First response", Rm, '\n')
            
            if Rm != bytes.fromhex('49 4D 4D 43'):  # If the response isn't correct.
                
                print("Trying to establish communication again", '\n')
                TxRx.close()
                TxRx.open()
                print("Port restarted", '\n')
                
                TxRx.write(bytes.fromhex('C5 49 4D 4D 43'))  # b'ÅIMMC' - Retry communication with other characters.
                Rm = Comm(TxRx)  # Read response.
                TxRx.write(bytes.fromhex('C5 49 4D 4D 43'))  # b'ÅIMMC' - Retry again.
                Rm = Comm(TxRx)  # Read response.
                print("Verification response ", Rm, '\n')
                
            if (Rm == bytes.fromhex('49 4D 4D 43')) or (Rm == bytes.fromhex('C5 49 4D 4D 43')):
                print("Correct link", '\n')
            else: 
                print("The link verification response is incorrect, communication can not be initiated ", '\n')
                TxRx.write(b'END')
                TxRx.close()
                print('Communication has ended')
                sys.exit()
        else:
            print('Port is not open or available ', '\n')
            sys.exit()
         
        return TxRx,  portStt

except serial.SerialException:
    print('Port is not available', '\n')
    sys.exit()
     
except serial.portNotOpenError:
    print('You are trying to use a port that is not open', '\n')
    sys.exit()

    
def Comm(TxRx):
    TxRx.inWaiting() 
    time.sleep(0.25)
    Rm = TxRx.read(TxRx.inWaiting())  # Read response data

    return Rm