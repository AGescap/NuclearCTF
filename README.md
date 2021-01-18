# NuclearCTF
Own made software that edits CTF input and analyzes CTF output

## Main.py
This script aims at "homogenize" or "re-discretize" in the radial dimension a CTF input file made with CTF preprocessor (Avramova, M. & Salko, R.).
The mentioned script will only represent a fuel element

## MainCore.py
The purpose here is more general: to homogenize a CTF core input, also made with CTF preprocessor
### Variables list:
 * bp = bundle pitch, gets converted into m. Scalar <br/>
 * dlev = level of discretization. nchn_side must be a multiple of it. Scalar <br/>
 * fa_num = number of fuel assemblies, without counting the ones filled with water. Scalar <br/>
 * fa_numcol = number of columns in the FA array in the core. Scalar <br/>
 * fa_numrow = number of rows in the FA array in the core. Scalar <br/>
 * ftds = fuel theoretical density in the rods of a given FA type Vector (fa_types, 1) <br/>
 * gapcond = conductivity of the gap in every type of FA. It is expessed in (W/m^2-K). Vector (fa_types, 1) <br/>
 * gt_mat = material of the guide tubes in every type of FA. It is a list of strings. As of now, this variable is not employed.
 Vector (fa_types, 1) <br/>
 * nchn = number of subchannels in an FA before homogenization. The number of channels per side is nchn_side = nrods_side + 1. Scalar <br/>
 * newchn = new number of channels in every FA after homogenization. Its value is newchn = nchn / (dlev^2). Scalar  <br/>
 * newchn_side = new number of channels per side in every FA after homogenization. Its value can be get from: newcnn_side = nchn_side / dlev. Scalar <br/>
 * newcoords = coordinates in an axis for the channels in every FA after homogenization. Vector (new
 * ngt = number of guide tubes / water rods in each type of FA. Vector (fa_types, 1) <br/>
 * nrods = number of rods for every FA. The number of rods per side is thus nrods_side = sqrt(nrods). Scalar <br/>
 * pp = pin pitch, gets converted into m. Scalar <br/>


