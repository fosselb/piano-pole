# Transforming the Chinese Pole Circus Apparatus into an Interactive Musical Instrument
**Fosse Lin-Bianco and Evan Mitchell**  
Hossein Asghari, PhD  
Department of Electrical and Computer Engineering  
Loyola Marymount University  

## Abstract
The objective of this project is to create a modified version of the Chinese pole circus apparatus in order to artistically musicalize and visualize a circus performer’s movement in real time. Wireless, wearable inertial measurement units (IMUs) allow for tracking the position of the performer’s hands and feet. The vertical height of the performer is then used to play a corresponding pitch on a musical scale, while the position with respect to the other two dimensions is used to produce a bird’s-eye-view visualization. Radio-frequency identification (RFID) tags added to the pole improve the accuracy of the IMU position tracking by providing anchor points with which to recalibrate an IMU's position in space. This works to reduce the effect of drift, the result of small inaccuracies in the acceleration data collected by the IMUs which are compounded when integrating over time to determine velocity and position. This project allows an audience to experience the movement of a circus performer from a new perspective. In addition to the choreography, the audience is left with a unique musical composition and visual art pieces they can remember. More importantly, the audience can experience the movement from a perspective that cannot be experienced without the use of this technology.

## Installation
First, clone this GitHub repository to your local computer by running
```bash
git clone --recursive https://github.com/fosselb/piano-pole
```

Next, with the [Arduino IDE](https://www.arduino.cc/en/software) installed, install the [SparkFun Qwiic RFID Reader Arduino Library](https://github.com/sparkfun/SparkFun_Qwiic_RFID_Arduino_Library) from the Library Manager. Then, follow [this SparkFun setup guide](https://learn.sparkfun.com/tutorials/qwiic-pro-micro-usb-c-atmega32u4-hookup-guide#setting-up-arduino) to install the Arduino addon necessary for interfacing with the Qwiic Pro Micro.

Finally, a number of Python packages must be installed for proper operation of *piano_pole.py*: the plotting library [Matplotlib](https://pypi.org/project/matplotlib/), [NumPy](https://pypi.org/project/numpy/) for matrix support, the [playsound](https://pypi.org/project/playsound/) library for playing piano samples, [Processing Python](https://pypi.org/project/processing-py/) for graphics, the Kalman filter library [FilterPy](https://pypi.org/project/filterpy/), [SciPy](https://pypi.org/project/scipy/) for additional mathematics, and the serial communication library [pySerial](https://pypi.org/project/pyserial/). All of these packages can be installed with [PyPI](https://pypi.org/) using `pip install <package>`.

## Usage
Once the installation process is completed, and with hardware set up properly, upload the *Qwiic_Pro_Micro.ino* Arduino script to all four Qwiic Pro Micro microcontrollers. Disconnect the microcontrollers from the computer and plug in the batteries with all four IMUs oriented along the same axes. Put on the gloves and shoes and prepare to begin the performance. When ready, with the receiver XBee plugged into the computer, run *piano_pole.py*.

The Python script can be run with the serial port of the receiver XBee using the command
```bash
python piano_pole.py -p <port>
```
A sample output reflecting recorded data can be produced by running
```bash
python piano_pole.py -t -i logs/log7.txt
```
An additional flag `-o` allows for the output of readings to a .txt file.

For more information about the available flags and their operations, please run
```bash
python piano_pole.py -h
```

## Acknowledgments
Piano sample files were obtained from [MIDI.js Soundfonts](https://github.com/gleitz/midi-js-soundfonts).  
*SparkFun_BNO080_Arduino_Library* is based on the [SparkFun BNO080 IMU Library](https://github.com/sparkfun/SparkFun_BNO080_Arduino_Library).  
Kalman filter code is adapted from Roger Labbe's [Kalman and Bayesian Filters in Python](https://github.com/rlabbe/Kalman-and-Bayesian-Filters-in-Python).
