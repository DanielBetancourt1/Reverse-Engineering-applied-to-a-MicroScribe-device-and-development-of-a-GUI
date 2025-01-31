# - This script was developed in order to generate an alternative to the original MicroScribe software, adding compatibility with multiple platforms, and OS versions 
in which python can be executed. Some additional features were added to expand the original functions of the software. 

# - This project was carried out in the EAFIT University in Medellin Colombia, where this digitizer
was about to be thrown away due to the obsolescence of the software. At the moment this device can be used to digitize data from impellers and the
obtained data can be easily used in the incorporated GUI or exported to other software.

# - # @Autor. This entire project was developed for Juan Daniel Isaza, Mechanical engineer from EAFIT University.



# - Software Setup:
 
	This script was written in Python 3.x.

	Execution: You have multiple options to run this software.

	- Windows users may use the portable file that is a version of the project compressed with pyinstaller into an exe file.

	- In all OS compatible with python you can run the .py file 'Main'.
	   NOTE: In order to use the script file 'Main.py' you must activate the virtual environment that contains all required libraries or install each one manually or
	   with the requirements.txt file (Using: pip install -r requirements.txt).

	## - Important.
	- If you don't use the virtual Environment be sure that all packages were correctly installed before execution.
	- If you are running this Script on any IDE application (Python interpreter) is highly recommended to execute this in an external system terminal.

	- MicroScribe Emulator (Arduino): This code allows to emulate the initial linking between MS and computer. To use it you must run twice the New Utility Software.


# - Hardware Setup:

	- Before turning on the MicroScribe, please put the stylus in the home position, and turn the Base joint until the mechanic limit.
	 Note: this orientation will be the rotation of XY plane about Z axis.

	- In order to start communications be sure that the MicroScribe is ON and correctly plugged, 
	if you have problems to establish connection after running this script for the first time , please restart the python kernel.

	- If you are using a Serial to Usb converter, be sure that you have the proper drivers installed.

# - Documentation:

	A paper from this project can be consulted at:

# - Contact:
	- Mail: jisazab@eafit.edu.co

# - License:
	- This is an Open Source project, Any bug, complain or extra idea must be notified via e-mail to the author.
	- Any educational or professional use of this software must be referenced and notified to the author.
