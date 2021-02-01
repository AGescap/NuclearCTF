import numpy as np
import os
import math

def findheaderinline(doc, string, time=1, separator=" "):
    cont = 0
    locus = -1
    clock = 1
    for linex in doc:
        if linex.replace(separator, "").find(string.replace(separator, "")) >= 0:
            if clock < time:
                clock = clock+1
                cont = cont + 1
            else:
                locus = cont
                break
        else:
            cont = cont + 1
    return locus
    
def findnextto(doc, string1, string2, time1=1, time2=1):
    start = int(findheaderinline(doc, string1, time=time1))
    aux_doc = [None]*(len(doc) - start)
    for i in range(0, len(doc) - start):
        aux_doc[i] = doc[i+start]

    finish = findheaderinline(aux_doc, string2, time=time2) + start
    return finish
    

def main():
    '''
    Opening the different output files and storing their lines. As a first approach, a series of lines
    dedicated to getting certain magnitudes will be written and commented. They should cover all possible cases,
    so that the users get a grasp of the method and can apply it to their particular needs
    
    In channels.out, for the Bundle average properties Table A, the following positions correspond to:

    *0: Number of axial node, starting from the bottom. Bottom node is 1, not 0
    *1: Axial position end of node, in m
    *2: Flow regime, isij
    *3: Liquid volume fraction, aliq
    *4: Entrained liquid volume fraction, aent
    *5: Vapor volume fraction, avap
    *6: Equilibrium quality, xeq
    *7: Flow quality, xfl
    *8: Liquid mass flow rate, fliq [kg/s]
    *9: Entrained liquid mass flow rate, fent [kg/s]
    *10: Vapor mass flow rate, fvap [kg/s],
    *11: Total mass flow rate, ftot [kg/s]
    *12: Pressure, p [bar]
    *13: Dynamic enthalpy of the mixture, hmix_fl [kJ/kg],
    *14: Temperature, T [C]

    In channels.out, for the Bundle average properties Table B, the following positions correspond to:

    *0: Number of axial node, starting from the bottom. Bottom node is 1, not 0
    *1: Axial position end of node, in m
    *2: Flow regime, isij
    *3: Heat added per node to the liquid, qliq [kW]
    *4: Heat added per node to the vapor, qvap [kW]
    *5: Total heat added per node, qtot [kW]

    In channels.out, for the Table nº1 of a channel, the following positions correspond to:
    
    *0: Number of axial node, starting from the bottom. Bottom node is 1, not 0
    *1: Axial position end of node, in m
    *2: Flow regime, isij
    *3: Liquid volume fraction, aliq 
    *4: Entrained liquid volume fraction, aent
    *5: Vapor volume fraction, avap
    *6: Equilibrium quality, xeq
    *7: Flow quality, xfl
    *8: Liquid mass flow rate, fliq [kg/s]
    *9: Entrained liquid mass flow rate [kg/s]
    *10: Vapor mass flow rate [kg/s],
    *11: Total mass flow rate [kg/s]
    *12: Liquid velocity, uliq [m/s]
    *13: Entrained liquid velocity [m/s],
    *14: Vapor velocity uvap [m/s]

    In channels.out, for the Table nº1 of a channel, the following positions correspond to:

    *0: Number of axial node, starting from the bottom. Bottom node is 1, not 0
    *1: Axial position end of node, in m
    *2: Flow regime, isij
    *3: Pressure p [bar]
    *4: Enthalpy of the liquid hliq [kJ/ kg]
    *5: Enthalpy of saturated liquid hf [kJ/kg]
    *6: hliq - hf [kJ/kg]
    *7: Enthalpy of the vapor hvap [kJ/ kg]
    *8: Enthalpy of saturated liquid hg [kJ/kg]
    *9: hvap - hg [kJ/kg]
    *10: Static enthalpy of the mixture, hmix [kJ/kg],
    *11: Dynamic enthalpy of the mixture, hmix_fl [kJ/kg],
    *12: Liquid density, rliq [kg/m3]
    *13: Vapor density, rvap [kg/m3],
    *14: Mixture density rmxix [kg/m3]
    *15: Mixture density rmix_fl [kg/m3]
    '''

    # open the files
    file = open("channels.out", "r")
    lines_chan = file.readlines()
    file.close()
    
    file = open("deck.dnb.out", "r")
    lines_dnb = file_control.readlines()
    file.close()
    
    # conversion factor, inches to mm
    in_to_m = 0.0254
    
    # for channels file
    channels_keys = [
    # for dnb file:
    
    
    
    
    
    # -----------------------------------------------------------------------DATA ANALYSIS----------------------------------------------------------------
    
    
    # -----------------------------------------------------------------------INFO STORAGE-----------------------------------------------------------------
    
    
    







main()