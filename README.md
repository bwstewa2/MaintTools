# DeltaPy - MaintTools
## Collection of software tools for data calculations

## Developed by Bert Stewart 


## Leakback
This program is used to calculate the rate of rise and other related information associated with vacuum chamber leakback test.

### Needed before use:
- Start and end pressures for performed leakback test
- Chamber size in Liters
- Time length used in the test

### Run: 
- Input chamber size, start, length of test, and end pressure in provided fields.
- Press the calculate button.
- Press the clear button to clear all vaules. 

### Results:
- Pressure Delta: Change in pressure during test.
- Rate of Rise: Rate at which the pressure rose over the course of the test. Provides the value for pass/fail.
- Failure pressure: The pressure value at which the test would fail if the end pressure was above.

### Settings: 
- Manual size entry: Select this if chamber size is not listed, user must provide size in liters.

### Visual (Graph):
- Blue line: Approximated pressure values during test.
- Red line: Failure line. If blue line intersects this line the test has failed. 


## Parameter Check:
This program calculates the percent error between power supplly's programmable, powersupply reading and system readbacks. 
This software is tailored to the parameter check proceedures of Veeco Ionmill and DLC systems. However, can be used for any percent error calculation by providing at least two values per row.

### Needed before use:
- At least two values from one or more power supplies. 

### Run:
- Enter at least two values per row.
- Press the calculate button.
- Press the clear button to clear all vaules. 

### results: 
- Max Error: the value of error between the values. 


## Target Wear
TODO

## DeltaPy - Python version of Delta 
This program is used to assist in performing manual hand-offs with Brooks robots and inaligners.

### Needed before use:
- The Aligner ECC R value returned from a brooks aligner in tenth mils 500 = 50 mils. 
- The Aligner EEC T value returned from a brooks aligner in tenth degrees 1800 = 180 deg.
- The T parameter of the station you wish to correct in millidegrees.
- The R parameter of the station in microns. 
- 	NOTE: Brooks VT5 reports in degrees and millimeters please convert to microns and millidegrees first. (mircon = millimeters * 1000, millidegree = degrees * 1000)
	
### Run: 
- Once all parameters are entered into the the text fields press "Calculate". 
- New R and T station values should be generated.
- Put these new values in the Brooks robot and test hand off again.
	**If you are setting the aligner position hand-off select the "Station is ALIGNER" checkbox or else the calculations will be the opposite direction.

### Settings:
- Aligner Post Position: Default - 90 deg. Visual representation of the aligner post position for the wafer notch. Does not change calculation.
- Wafer size: Default - 8". Select the size of wafer used on the aligner. Changes visual representation of delta position. Does not change calculation.
- Delta Adjustment: Default - 1.0. (Rarely needed) Used to proportionately adjust the calculated R and T values due to consistent difference in calculation and needed adjustment for tool.
  You can input exact adjustment in text field, adjust with slider, or press "Reset" to reset to 1.0. 
	**Ex. for delta adjustment: Robot needs 1/2 or 2 times the adjustment as calculated values due to robot movement not consistent with input values.  
	
### Visual: 
- Blue Circle: The visual representation of the wafer, shows the wafer positioned as if the robot were directly below the wafer. 
- Black dot: represent the center of the wafer and current position of the robot's end-effector. 
- Red dot: represents the direction and magnitude of the change needed by the robots end-effector.
- Red triangle: Represents the wafer not, and aligner post position. 


## Analog Calibration:
TODO
 
Please reach out to me for corrections, suggestions, and comments.
 
 