# NuclearCTF
Own made software that edits CTF input and analyzes CTF output

## Main.py
This script aims at "homogenizing" or "re-discretizing" in the radial dimension a CTF input file made with CTF preprocessor (Avramova, M. & Salko, R.).
The mentioned script will only represent a fuel element

## MainCore.py
The purpose here is more general: to homogenize a CTF core input, also made with CTF preprocessor
### Variables list:
 * bp = bundle pitch, gets converted into m. Scalar <br/>
 * core_centX = list of the X coordinates of the centers of the FAs depending on the column -of the core- in which they are located. 1-D array (fa_numcol)  <br/>
 * core_centY = list of the Y coordinates of the centers of the FAs depending on the row -of the core- in which they are located. 1-D array (fa_numcol)  <br/>
 * core_map = 2-D array. [i][j] where [i] = row, [j] = col is the type of fuel assembly, and zero if it is a "water" FA. Different from core_map . 2-D array (fa_numrow, fa_numcol) <br/>
 * dlev = level of discretization. nchn_side must be a multiple of it. Scalar <br/>
 * fa_num = number of fuel assemblies, without counting the ones filled with water. Scalar <br/>
 * fa_numcol = number of columns in the FA array in the core. Scalar <br/>
 * fa_numrow = number of rows in the FA array in the core. Scalar <br/>
 * ftds = fuel theoretical density in the rods of a given FA type 1-D array (fa_types, 1) <br/>
  * fa_types = number of different types of FA in the core (always with the same bp and pp, number of rods, but different geometries and types of rods, including fuel density and gap conductivity. Scalar <br/>
 * gapcond = conductivity of the gap in every type of FA. It is expessed in (W/m^2-K). 1-D array (fa_types, 1) <br/>
 * gt_mat = material of the guide tubes in every type of FA. It is a list of strings. As of now, this variable is not employed.
 Vector (fa_types, 1) <br/>
 * indicradprof --under development-- it indicates whether the radial profile should be taken from the ExtraFA file (any value but 0) or from the deck.inp (value 0) -and thus it is a result of prepro-. Scalar.  <br/>
 * nchn = number of subchannels in an FA before homogenization. The number of channels per side is nchn_side = nrods_side + 1. Scalar <br/>
 * newchn = new number of channels in every FA after homogenization. Its value is newchn = nchn / (dlev^2). Scalar  <br/>
 * newchn_side = new number of channels per side in every FA after homogenization. Its value can be get from: newcnn_side = nchn_side / dlev. Scalar <br/>
 * newchn_tot = total number of real -not water- channels in the core after homogenization. Calculated as newchn_tot = fa_num * newchn  Scalar <br/>
 * newnrod_tot = same as newchn_tot. Included for completeness  Scalar <br/>
 * newcoords = coordinates along an axis for the channels in every FA after homogenization. 1-D array (nchn_side, 1) <br/>
 * ngt = number of guide tubes / water rods in each type of FA. Vector (fa_types, 1) <br/>
 * nrods = number of rods for every FA. The number of rods per side is thus nrods_side = sqrt(nrods). Scalar <br/>
 * numb_core_map = 2-D array. [i][j] where [i] = row, [j] = col is the number of fuel assembly, and zero if it is a "water" FA. Different from core_map . 2-D array <br/>
 * pp = pin pitch, gets converted into m. Scalar <br/>
 * subchannels_in_rod: 3-D array. for every rod [i] it stores the number of the channel in top left ([i][0][0]), top right ([i][0][1]), bottom left ([i][0][1]) and bottom right
 ([i][0][1]). 3-D array (nrods, 2, 2) <br/>


