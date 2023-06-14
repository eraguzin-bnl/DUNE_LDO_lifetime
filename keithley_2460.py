# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 10:51:58 2023

@author: Eraguzin
"""

class Keithley2460:
    def __init__(self, rm, json_data):
        self.rm = rm
        self.json_data = json_data
        self.keithley = self.rm.open_resource(self.json_data['keithley'])
        print(f"Keithley 2460 --> Connected to {self.keithley.query('*IDN?')}")
        self.keithley.write("*RST")
        
    def initialize(self):
        self.voltage = self.json_data['keithley_voltage']
        
        #Set the instrument to source voltage as opposed to current
        self.keithley.write(":SOURce1:FUNCtion:MODE VOLTage")
        
        #Write the actual desired voltage
        self.keithley.write(f":SOURce1:VOLT:LEVel:IMMediate:AMPLitude {self.voltage}")
        print(f"Keithley 2460 --> Wrote voltage to {self.voltage}")
        
        #Turn on autorange
        self.keithley.write(":SOURce1:CURRent:RANGe:AUTO ON")
        #Always read back measured voltage, not the set voltage
        self.keithley.write(":SOURce1:VOLTage:READ:BACK ON")
        
        #Lock front screen and require password
        self.keithley.write(":SYST:ACC LOCK")
        self.keithley.write(f":SYST:PASS:NEW '{self.json_data['keithley_password']}'")
        
        #Set measurement time for best accuracy
        self.line_freq = self.keithley.query(":SYSTem:LFRequency?")
        self.keithley.write(f":SENSe1:VOLTage:NPLCycles {self.json_data['keithley_voltage_NPLcycles']}")
        self.keithley.write(f":SENSe1:CURRent:NPLCycles {self.json_data['keithley_current_NPLcycles']}")
        #Set Autozero on
        self.keithley.write(f":SENSe1:VOLTage:AZERo {self.json_data['keithley_autozero']}")
        
        #2 wire sensing
        self.keithley.write(f":SENSe1:VOLTage:RSENse {self.json_data['keithley_4wire_measurement']}")
        
        #Voltage source setting can't be limited by measurement limits
        self.keithley.write(f":SENSe1:VOLTage:RANGe:AUTO {self.json_data['keithley_voltage_autorange']}")
        self.keithley.write(f":SENSe1:VOLTage:RANGe:AUTO:REBound {self.json_data['keithley_voltage_autorange_rebound']}")
        
        #Current measurements are auto
        self.keithley.write(f":SENSe1:CURRent:RANGe:AUTO {self.json_data['keithley_current_autorange']}")
        
        #Should we have a voltage limit or current limit? On Source or Measurement side?
        #Number of digits in ASCII response
        self.keithley.write(f":FORMat:ASCii:PRECision {self.json_data['keithley_ascii_digits']}")
        
        #When off, be in the normal state
        self.keithley.write(":OUTPut1:VOLTage:SMODe NORM")
        self.keithley.write(":OUTPut1:STATe ON")
        
        #Display on front screen
        self.keithley.write(":DISPlay:CLEar")
        self.keithley.write(f":DISPlay:USER1:TEXT:DATA '{self.json_data['keithley_front_panel1']}'")
        self.keithley.write(f":DISPlay:USER2:TEXT:DATA '{self.json_data['keithley_front_panel2']}'")
        self.keithley.write(":DISPlay:SCReen SWIPE_USER")
        
    def measure(self):
        #Make measurements, results come in like '7.999993E+00\n'
        #Remove newline at end
        voltage = self.keithley.query(":MEASure:VOLTage?").strip()
        current = self.keithley.query(":MEASure:CURRent?").strip()
        
        return float(voltage),float(current)