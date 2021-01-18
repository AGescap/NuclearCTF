# NuclearCTF
Own made software that edits CTF input and analyzes CTF output

## Main.py
This script aims at "homogenize" or "re-discretize" in the radial dimension a CTF input file made with CTF preprocessor (Avramova, M. & Salko, R.).
The mentioned script will only represent a fuel element

## MainCore.py
The purpose here is more general: to homogenize a CTF core input
### Variables list:
 * bp = bundle pitch, gets converted into m <br/>
 * pp = pin pitch, gets converted into m <br/>
 * nrods = number of rods in an FA. The number of rods per side is thus nrods_side = sqrt(nrods). <br/>
 * nchn = number of subchannels in an FA before homogenization. The number of channels per side is nchn_side = nrods_side + 1 <br/>
