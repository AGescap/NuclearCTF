import numpy as np
import os
import math
import re

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

def fahrtocelsius(t):
    return (t-32.0) * 5/9
    

def main():
    '''
    Opening the different output files and storing their lines. As a first approach, a series of lines
    dedicated to getting certain magnitudes will be written and commented. They should cover all possible cases,
    so that the users get a grasp of the method and can apply it to their particular needs
    
    In channels.out, for the Bundle average properties Table A, the following positions correspond to:

    *0: Number of axial node. Numeration starts from the bottom, but the document starts from the top
        Bottom node is 1, not 0
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

    Below that table, pressure losses over total height can be found:

    "Total pressure loss over total height": look for that header, component nº6 [bar]
    "geodetical pressure loss": component nº 4 [bar]
    "accelearation pressure loss": component nº 4 [bar]
    "frictional and signle head losses": component nº 4 [bar]

    In channels.out, for the Bundle average properties Table B, the following positions correspond to:

    *0: Number of axial node, starting from the bottom. Bottom node is 1, not 0
    *1: Axial position end of node, in m
    *2: Flow regime, isij
    *3: Heat added per node to the liquid, qliq [kW]
    *4: Heat added per node to the vapor, qvap [kW]
    *5: Total heat added per node, qtot [kW]

    In channels.out, for the Table nº1 of a channel, the following positions correspond to:
    
    *0: Number of axial node. Numeration starts from the bottom, but the document starts from the top
        Bottom node is 1, not 0
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

    In channels.out, for the Table nº2 of a channel, the following positions correspond to:

    *0: Number of axial node. Numeration starts from the bottom, but the document starts from the top
        Bottom node is 1, not 0
    *1: Axial position end of node, [m]
    *2: Flow regime, isij
    *3: Pressure, p [bar]
    *4: Enthalpy of the liquid, hliq [kJ/ kg]
    *5: Enthalpy of saturated liquid, hf [kJ/kg]
    *6: hliq - hf [kJ/kg]
    *7: Enthalpy of the vapor, hvap [kJ/ kg]
    *8: Enthalpy of saturated liquid, hg [kJ/kg]
    *9: hvap - hg [kJ/kg]
    *10: Static enthalpy of the mixture, hmix [kJ/kg],
    *11: Dynamic enthalpy of the mixture, hmix_fl [kJ/kg],
    *12: Liquid density, rliq [kg/m3]
    *13: Vapor density, rvap [kg/m3],
    *14: Mixture density rmxix [kg/m3]
    *15: Mixture density rmix_fl [kg/m3]

    In channels.out, for the Table nº3 of a channel, the following positions correspond to:

    *0: Number of axial node. Numeration starts from the bottom, but the document starts from the top
        Bottom node is 1, not 0
    *1: Axial position end of node, [m]
    *2: Flow regime, isij
    *3: Heat transfer regime in the 1st surface, mode1 [str]
    *4: Heat transfer regime in the 2nd surface, mode2 [str]
    *5: Heat transfer regime in the 3rd surface, mode3 [str]
    *6: Heat transfer regime in the 4th surface, mode4 [str]
    *7: Rod surface temperature in the 1st surface, twall1 [C]
    *8: Rod surface temperature in the 2nd surface, twall2 [C]
    *9: Rod surface temperature in the 3rd surface, twall3 [C]
    *10: Rod surface temperature in the 4th surface, twall4 [C]
    *11: Saturation temperature, tf [C]
    *12: Liquid temperature, tliq [C]
    *13: Vapor temperature, tvap [C]
    *14: CHF temperature, tchf [C]
    *15: Minimum boiling temperatue, tmin [C]
    *16: Heat added per node to the liquid, qliq [kW]
    *17: Heat added per node to the vapor, qvap [kW]
    *18: Total added heat per node, qtot [kW]

    Order of appearance for the rods:
    1st: top left
    2nd: top right
    3rd: bottom left
    4th: bottom right

    In channels.out, for the Table nº4 of a channel, the following positions correspond to:

    *0: Number of axial node. Numeration starts from the bottom, but the document starts from the top
        Bottom node is 1, not 0
    *1: Axial position end of node, [m]
    *2: Flow regime, isij
    *3: Entrained liquid mass per node, sent [kg/s]
    *4: Deposition of entrained phase mass per node, sdent [kg/s]
    *5: Balance entrainment-deposition, sent-sdent [kg/s]
    *6: Evaporation per node, gama [kg/s]
    *7: Lateral -lost- liquid mass flow rate per node, wliq_sum [kg/s]
    *8: Lateral -lost- entrained phase mass flow rate per node, went_sum [kg/s]
    *9: Lateral -lost- vapor mass flow rate per node, wvap_sum [kg/s]
    *10: Lateral -lost- total mass flow rate per node, wtot_sum [kg/s]
    *11: Film thickness, dliq [mm]

    In the output files, rod surfaces are numbered as follow:
    -surface nº1: bottom left
    -surface nº2: bottom right
    -surface nº3: top left
    -surface nº4: top right

    In deck.dnb.out, for every surface of every rod, one has a table with the following fields:
    *0: Number of axial node. Numeration starts from the bottom, but the document starts from the top
        Bottom node is 1, not 0
    *1: Axial position end of node, [in]
    *2: Heat flux, Q" [BTU/h*ft**2]
    *3: Critical heat flux, CHF  [BTU/h*ft**2]
    *4: DNBR

    In deckr.out, for every surface of every rod, one has a table with the following fields:
    *0: Number of axial node. Numeration starts from the bottom, but the document starts from the top
        Bottom node is 1, not 0
    ----Remember to split the star (*) sign between 0th and 1st fields-----
    *1: Axial position end of node, [in]
    *2: Liquid temperature [ºF]
    *3: Vapor temperature [ºF]
    *4: Surface heat flux [BTU/h*ft**2]
    *5: Heat transfer mode [str]
    *6: Outside clad temperature [ºF]
    *7: Inside clad temperature [ºF]
    *8: Gap conductance [BTU/h*ft2*ºF]
    *9: Fuel surface temperature [ºF]
    *10: Fuel center temperature [ºF]

    cpld_temp_dens_summary.out only contains a summary table, with radial averaging of some magnitudes for
    every axial node:
    *0: Number of axial node, starting from the bottom. Bottom node is 1, not 0

    '''

    # open the files
    file = open("channels.out", "r")
    lines_chan = file.readlines()
    file.close()
    
    file = open("deck.dnb.out", "r")
    lines_dnb = file.readlines()
    file.close()

    file = open("deckr.out", "r")
    lines_deckr = file.readlines()
    file.close()

    file = open("cpld_temp_dens_summary.out", "r")
    lines_summary = file.readlines()
    file.close()
    
    file = open("Channelsmap.txt", "r")
    lines_channelsmap = file.readlines()
    file.close()
    
    # conversion factor, inches to mm
    cf1 = 0.0254

    # conversion factor, BTU/h-ft**2 to kW/m2
    cf2 = 0.003152481054113
    
    # for channels file
    channels_keys = []
    # for dnb file:

    # a = 'Beautiful, is; better*than\nugly'
    # re.split('; |, |\*|\n', a)
    # ['Beautiful', 'is', 'better', 'than', 'ugly']
    
    # gets the channel map
    
    linaux = lines_channelsmap[findheaderinline(lines_channelsmap, "Nº of lines to read") + 1]
    chmp_dim = int(linaux[0])
    
    channmap = np.zeros((chmp_dim, 3), dtype=int)
    for i in range(0, chmp_dim):
        linaux = lines_channelsmap[findheaderinline(lines_channelsmap, "Nº of lines to read") + 3 + i]
        chmp_dim[i, :] = [int(linaux[0]), int(linaux[1]), int(linaux[2])]

    # -----------------------------------------------------------------------DATA ANALYSIS----------------------------------------------------------------
    
    
    # -----------------------------------------------------------------------INFO STORAGE-----------------------------------------------------------------
    
    
    







main()