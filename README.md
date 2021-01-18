# NuclearCTF
Own made software that edits CTF input and analyzes CTF output

## Main.py
This script aims at "homogenize" or "re-discretize" in the radial dimension a CTF input file made with CTF preprocessor (Avramova, M. & Salko, R.).
The mentioned script will only represent a fuel element

## MainCore.py
The purpose here is more general: to homogenize a CTF core input
### Variables list:
 * bp = bundle pitch, gets converted into m <br/>
 * dlev = level of discretization. nchn_side must be a multiple of it <br/>
 * fa_num = number of fuel assemblies, without counting the ones filled with water <br/>
 * fa_numcol = number of columns in the FA array in the core <br/>
 * fa_numrow = number of rows in the FA array in the core <br/>
 * gapcond = conductivity of the gap in every type of FA. It is expessed in (W/m^2-K) <br/>
 * nchn = number of subchannels in an FA before homogenization. The number of channels per side is nchn_side = nrods_side + 1 <br/>
 * newchn = new number of channels in every FA after homogenization. Its value is newchn = nchn / (dlev^2)
 * nrods = number of rods in an FA. The number of rods per side is thus nrods_side = sqrt(nrods). <br/>
 * pp = pin pitch, gets converted into m <br/>
 

