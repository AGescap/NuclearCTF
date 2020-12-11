import numpy as np


def findcardinline(doc, string, time=1):
    # so as to count the iterations. Caution is needed with the string here, because if one types
    # e.g. Card 3.3., it will find both Card 3.3 or Card 3.3.5. That motivates the use of break.
    # With the variable time, it can now look for the n-th time that the Card appears (like in axial or radial profiles)
    cont = 0
    locus = -1
    clock = 1
    for linex in doc:

        # find returns the first position of the sequence that appears in the line. Should it not appear,
        # find returns -1. The exact value does not matter, only its presence

        if linex.find(string) >= 0:
            if clock < time:
                clock = clock + 1
                cont = cont + 1
            else:
                locus = cont
                break
        else:
            cont = cont + 1
    return locus


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


# removeexcesslines takes a list of strings (the result of readlines method), sets an origin
# (ideally, a variables header) and from that, counts PRIOR lines -like the ones in Group 4 of deck.inp in CTF-
# in the new situation, ACTUAL lines must be conserved, from the position BEGIN, and thus REMOVE lines must be erased


def removeexcesslines(doc, begin, prior, actual):
    remove = prior - actual
    for i in range(0, remove):
         doc.pop(begin+actual+1)


def rewritesomelines(doc, begin, piece):
    # rewrites all the lines in piece. First one replaced is the next one to "begin"
    for i in range(0, len(piece)):
        doc[begin+1+i] = piece[i] + " \n"


# deletebetweencards looks for the position number time 1 of the Card 1 and deletes everything
# (including Card1) until it finds Card 2 (for the time2-th occasion)
def deletebetweencards(doc, card1, card2, time1=1, time2=1):
    pos1 = findcardinline(doc, card1, time1)
    pos2 = findcardinline(doc, card2, time2)
    for i in range(0, pos2 - pos1):
        doc.pop(pos1)


def chanindex_xy(x, y, numchannelside):
    # chanindex: from the x, y position (origin in bottom left corner), gets the index of the channel.
    # Numeration begins at top left and goes first rightwards and then downwards.
    # System of reference: x increases to the right, y increases from the bottom to the top
    return x+(numchannelside - y)*numchannelside


def retrieve_xy(index, numchannelside):
    # retrieve_xy: from the index and the number of channels per side, gets x and y (origin in bottom left corner). This
    # does not apply exclusively for subchannel, but for any homogenization
    y = numchannelside - (index - 1) // numchannelside
    x = index - (numchannelside - y)*numchannelside
    return [x, y]


def refchannel(numchannel, dlevel, n_sbchn_side):
    # f rom the number of a newly created channel (1,2,...N/Dlev**2), gets global index of its top left channel
    new_chn_per_side = n_sbchn_side / dlevel
    [x, y] = retrieve_xy(numchannel, new_chn_per_side)
    return 1 + (x-1) * dlevel + (new_chn_per_side - y) * n_sbchn_side * dlevel


def format_e(n):               # This function allows to write a float as a string with scientific notation
    a = '%E' % n
    return a.split('E')[0].rstrip('0').rstrip('.') + 'E' + a.split('E')[1]


def main():
    '''
    Here the approach is that of deducting all the subchannel properties from prepro data, given that some features as
    the guide tubes location are more explicitly given in those files, rather than in deck.inp (the coordinates appear,
    whereas in deck.inp a search should be done in the radial power profile)
    '''
    # open the deck file and also the prepro files
    file = open("deck.inp", "r")
    lines = file.readlines()
    file.close()

    file_control = open("control.inp", "r")
    lines_control = file_control.readlines()
    file_control.close()

    file_geo = open("geo.inp", "r")
    lines_geo = file_geo.readlines()
    file_geo.close()

    file_assem = open("assem.inp", "r")
    lines_assem = file_assem.readlines()
    file_assem.close()

    file_power = open("power.inp", "r")
    lines_power = file_power.readlines()
    file_power.close()

    '''
    Begin the READS and simple Calculations, not DELETES nor WRITES yet
    '''
    # gets channel number in Card 2
    # stores in lists magnitudes from card 2
    nchn = int(lines[findheaderinline(lines, "NCH NDM2")+1].split()[0])
    nchn_side = int(np.sqrt(nchn))
    D_lev = 2
    anom = []
    pw = []
    xsiz = []
    ysiz = []
    for i in range(0, nchn):
        anom.append(float(lines[findheaderinline(lines, "I AN")+1+i].split()[1]))
        pw.append(float(lines[findheaderinline(lines, "I AN") + 1+i].split()[2]))
        xsiz.append(float(lines[findheaderinline(lines, "I AN") + 1+i].split()[8]))
        ysiz.append(float(lines[findheaderinline(lines, "I AN") + 1 + i].split()[9]))

    # new number of subchannels
    new_chn = int(nchn/(D_lev**2))
    new_chn_side = int(nchn_side/D_lev)

    # new number of gaps
    new_ngaps = int(2*new_chn_side*(new_chn_side - 1))

    # gets if electric or nuclear rods
    heated_type = int(lines_assem[findheaderinline(lines_assem, "Type of heated elements")+3].split()[0])

    # get number of fuel rods and guide/water rods and their geometric characteristics
    n_frods = -1
    n_gt = -1
    n_elec = -1

    '''
    Using prepro guide tube map implies, if their positions are not quarter symmetric, that you have to make some conversions
    to see where they are actually placed, in the deck.inp system of reference (origin placed at the center)
    '''
    if heated_type == 0:
        n_frods = int(lines_assem[findheaderinline(lines_assem, "Number of fuel rods")+1].split()[0])
        n_gt = int(lines_assem[findheaderinline(lines_assem, "Number of guide tubes/water rods") + 1].split()[0])
    else:
        if heated_type == 1:
            n_elec = int(lines_assem[findheaderinline(lines_assem, "Number of fuel rods") + 1].split()[0])
        else:
            pass

    # gets fuel rods outer diameter and guide tubes outer diameter, converts them into mm
    if heated_type == 0:
        od_fr = float(lines_assem[findheaderinline(lines_assem, "Cladding outer diameter") + 1].split()[0])
        od_fr = od_fr / 1000
        if n_gt > 0:
            od_gt = float(lines_assem[findheaderinline(lines_assem, "Outer diameter of guide tube") + 1].split()[0])
            od_gt = od_gt / 1000
        else:
            pass
    else:
        if heated_type == 1:
            od_electube = float(lines_assem[findheaderinline(lines_assem, "Tube outside diameter") + 1].split()[0])
            od_electube = od_electube / 1000

        pass

    # gets map of guide tubes and converts
    if n_gt > 0:
        aux = -1
        map_gt = []
        indicator_gt = [None]*n_gt
        for i in range(0, n_gt):
            map_gt.append(lines_assem[findheaderinline(lines_assem, "Use X Y format")+1+i].split())

        for i in range(0, len(map_gt)):
            for j in range(0, 2):
                map_gt[i][j] = int(map_gt[i][j])

            aux = int(map_gt[i][0])
            map_gt[i][0] = map_gt[i][1]
            map_gt[i][1] = (nchn_side - aux)
            indicator_gt[i] = (nchn_side - 1)*(nchn_side-1-map_gt[i][1]) + map_gt[i][0]

    #TODO fix this warnings if possible (dont undestand why it thinks j is a string)
    #TODO enable the option of getting the guide tube positions from the power profile

    # gets pin pitch and converts it into m

    pin_pitch = float(lines_assem[findheaderinline(lines_assem, "Pin pitch") + 1].split()[0])
    pin_pitch = pin_pitch / 1000

    # gets bundle pitch and converts it to m

    bundle_pitch = float(lines_assem[findheaderinline(lines_assem, "Bundle pitch") + 1].split()[0])
    bundle_pitch = bundle_pitch/1000

    # gets free space (free_sp) between bundle and limits

    free_sp = (bundle_pitch - (nchn_side-2)*pin_pitch)/2

    # creates new X and Y locations for the new channels

    lshort = free_sp + (D_lev-1)*pin_pitch

    # gets gap number in Card 3 and ensure everything is ok

    ngaps = int(lines[findheaderinline(lines, "NK NDM2")+1].split()[0])  # looks for the following position
    # of the header in string, splits it and gets the term, which is in first position, i.e. [0]

    # gets the number of rods from Card 8.1
    nrods = int(lines[findheaderinline(lines, "NRRD NSRD")+1].split()[0])


    '''Here it begins to re-write and compute'''

    # create an array with the subchannels that correspond to a rod
    subchannels_in_rod = np.zeros((nrods, 2, 2), dtype=int)
    for i in range(0, nrods):
        top = i+1 + i//(nchn_side-1)
        subchannels_in_rod[i][0][0] = top
        subchannels_in_rod[i][0][1] = top + 1
        subchannels_in_rod[i][1][0] = top + nchn_side
        subchannels_in_rod[i][1][1] = top + nchn_side+1

    # creates an array that stores the number of subchannels that belong to the new channel
    subchannels_in_channel = np.zeros((new_chn, D_lev, D_lev), dtype=int)
    for i in range(0, new_chn):
        for j in range(0, D_lev):
            for k in range(0, D_lev):
                subchannels_in_channel[i][j][k] = refchannel(i+1, D_lev, nchn_side) + j*nchn_side + k

    def findthechannelingaps(vgaps, val, time=1):
        # finds the first channel with number of channel val in the vector of gaps and returns the number of gap
        aux = 0
        clock = 1
        for i in range(0, ngaps):
            if vgaps[i][1] == val:
                if clock < time:
                    clock = clock +1
                else:
                    aux = i+1
                    break
        return aux

    def findsubchannelinchannel(sub2chan, subch):
        aux = 0
        for i in range(0, new_chn):
            for j in range(0, D_lev):
                for k in range(0, D_lev):
                    if sub2chan[i][j][k] == subch:
                        aux = i+1
                        break
        return aux

    # Substitutes the number of channels in Group 2

    line_aux = lines[findheaderinline(lines, "NCH NDM2")+1].split()
    line_aux[0] = str(new_chn)
    line_aux = '     ' + '    '.join(line_aux) + '\n'  # creates a sole string with the appropriate format
    lines[findheaderinline(lines, "NCH NDM2") + 1] = line_aux  # stores the modified line into its position

    # Deletes the excess of lines in Card 2.2
    removeexcesslines(lines, findheaderinline(lines, "I AN PW", time=1), nchn, new_chn)

    # Changes the number of gaps in Card 3.1
    line_aux = lines[findheaderinline(lines, "NK NDM2") + 1].split()
    line_aux[0] = str(new_ngaps)
    line_aux = '     ' + '    '.join(line_aux) + '\n'  # creates a sole string with the appropriate format
    lines[findheaderinline(lines, "NK NDM2") + 1] = line_aux  # stores the modified line into its position

    # creates a list which stores all the necessary info about gaps in subchannel. First there is number K of gap,
    # Second, there is the initial channel. Third, the final channel. Fourth, the length of the channel
    gap_data = [[0] * 6 for _ in range(ngaps)]
    for i in range(0, ngaps):
        gap_data[i][0] = int(lines[findheaderinline(lines, "K IK JK") + 3+2*i].split()[0])
        gap_data[i][1] = int(lines[findheaderinline(lines, "K IK JK") + 3+2*i].split()[1])
        gap_data[i][2] = int(lines[findheaderinline(lines, "K IK JK") + 3 + 2 * i].split()[2])
        gap_data[i][3] = float(lines[findheaderinline(lines, "K IK JK") + 3 + 2 * i].split()[3])
        gap_data[i][4] = float(lines[findheaderinline(lines, "K IK JK") + 3 + 2 * i].split()[1])
        gap_data[i][5] = float(lines[findheaderinline(lines, "K X Y NORM") + 1 + i].split()[2])

    # Deletes excess of gaps in Card 3.3
    removeexcesslines(lines, findheaderinline(lines, "K IK JK", time=1), 2+2*ngaps, 2+2*new_ngaps)

    # Deletes excess of gaps in Card 3.3.5
    removeexcesslines(lines, findheaderinline(lines, "K X Y NORM", time=1), ngaps, new_ngaps)

    # gets NONO variable and calculate new MSIM
    nono = int(lines[findheaderinline(lines, "NCHN NONO")+1].split()[2])
    new_msim = nono*new_chn

    # Changes NCHN in Card 4.2

    line_aux = lines[findheaderinline(lines, "ISEC NCHN NONO") + 1].split()
    line_aux[1] = str(new_chn)
    line_aux = '     ' + '   '.join(line_aux) + '\n'  # creates a sole string with the appropriate format
    lines[findheaderinline(lines, "ISEC NCHN NONO") + 1] = line_aux  # stores the modified line into its position

    # Changes IWDE in Card 4.5

    line_aux = lines[findheaderinline(lines, "IWDE") + 1].split()
    line_aux[0] = str(new_chn)
    line_aux = '     ' + '    '.join(line_aux) + '\n'  # creates a sole string with the appropriate format
    lines[findheaderinline(lines, "IWDE") + 1] = line_aux  # stores the modified line into its position

    # Changes MSIM in Card 4.6

    line_aux = lines[findheaderinline(lines, "MSIM") + 1].split()
    line_aux[0] = str(new_msim)
    line_aux = '     ' + '    '.join(line_aux) + '\n'  # creates a sole string with the appropriate format
    lines[findheaderinline(lines, "MSIM") + 1] = line_aux  # stores the modified line into its position

    # Deletes excess lines in Card 4.4

    removeexcesslines(lines, findheaderinline(lines, "KCHA KCHA", time=1), nchn, new_chn)

    # Reads NCD, gets the different CDL and J positions
    ncd = int(lines[findheaderinline(lines, "NCD NGT")+1].split()[0])
    ngrids = int(ncd / ((nchn + 1) // 12))
    grid_cdl = np.zeros((ngrids, 1), dtype=float)
    grid_j = np.zeros((ngrids, 1), dtype=int)
    clock = int(0)
    new_ncd = ngrids*(((new_chn-1)//12) + 1)

    # Substitutes NCD in Card 7.1
    line_aux = lines[findheaderinline(lines, "NCD NGT") + 1].split()
    line_aux[0] = str(new_ncd)
    line_aux = '     ' + '    '.join(line_aux) + '\n'
    lines[findheaderinline(lines, "NCD NGT") + 1] = line_aux

    for i in range(0, ncd):
        if i == 0:
            grid_cdl[0] = float(lines[findheaderinline(lines, "CDL J") + 1].split()[0])
            grid_j[0] = int(lines[findheaderinline(lines, "CDL J") + 1].split()[1])

        else:
            if int(lines[findheaderinline(lines, "CDL J") + 1 + i].split()[1]) != grid_j[clock] and clock < ngrids - 1:
                grid_cdl[clock+1] = float(lines[findheaderinline(lines, "CDL J") + 1 + i].split()[0])
                grid_j[clock+1] = int(lines[findheaderinline(lines, "CDL J") + 1 + i].split()[1])
                clock = clock + 1
    # Deletes excess lines in card 7.4

    removeexcesslines(lines, findheaderinline(lines, "CDL J CD1", time=1), ncd, new_ncd)

    # Creates new card
    lines_per_grid = int(new_ncd / ngrids)
    for i in range(0, new_ncd):
        line_aux = lines[findheaderinline(lines, "CDL J CD1", time=1) + 1 + i].split()
        line_aux[0] = str(float(grid_cdl[i//lines_per_grid]))
        line_aux[1] = str(int(grid_j[i//lines_per_grid]))
        line_aux[2] = str(12*(i % lines_per_grid) + 1)
        line_aux[3] = str(12*(i % lines_per_grid) + 2)
        line_aux[4] = str(12*(i % lines_per_grid) + 3)
        line_aux[5] = str(12*(i % lines_per_grid) + 4)
        line_aux[6] = str(12*(i % lines_per_grid) + 5)
        line_aux[7] = str(12*(i % lines_per_grid) + 6)
        line_aux[8] = str(12*(i % lines_per_grid) + 7)
        line_aux[9] = str(12*(i % lines_per_grid) + 8)
        line_aux[10] = str(12*(i % lines_per_grid) + 9)
        line_aux[11] = str(12*(i % lines_per_grid) + 10)
        line_aux[12] = str(12*(i % lines_per_grid) + 11)
        line_aux[13] = str(12*(i % lines_per_grid) + 12)
        if new_chn % 12 != 0:
            if (i + 1) % lines_per_grid == 0:
                for j in range(0, 12 - (new_chn % 12)):
                    line_aux[-1-j] = str(0)
        line_aux = '     ' + '    '.join(line_aux) + '\n'  # creates a sole string with the appropriate format
        lines[findheaderinline(lines, "CDL J CD1", time=1) + 1 + i] = line_aux  # stores the modified line
        # into its position

    # Changes NRRD in Card 8.1

    line_aux = lines[findheaderinline(lines, "NRRD NSRD", time=1) + 1].split()
    line_aux[0] = str(new_chn)
    line_aux = '     ' + '    '.join(line_aux) + '\n'  # creates a sole string with the appropriate format
    lines[findheaderinline(lines, "NRRD NSRD", time=1) + 1] = line_aux  # stores the modified line into its position

    # TODO create a function that performs the same as the 4 lines above

    # Deletes excess of lines in Cards (read by pairs) 8.2 and 8.3

    removeexcesslines(lines, findheaderinline(lines, "N IFTY IAXP", time=1), 2 + 2 * nrods, 2 + 2 * new_chn)

    # Changes NRT1

    line_aux = lines[findheaderinline(lines, "NRT1 NST1", time=1) + 1].split()
    line_aux[1] = str(new_chn)
    line_aux = '     ' + '    '.join(line_aux) + '\n'  # creates a sole string with the appropriate format
    lines[findheaderinline(lines, "NRT1 NST1", time=1) + 1] = line_aux  # stores the modified line into its position

    # Deletes excess of lines in Card 8.7

    removeexcesslines(lines, findheaderinline(lines, "IRTB1 IRTB2"), ((nrods - 1) // 12) + 1, ((new_chn - 1) // 12) + 1)
    if new_chn % 12 != 0:
        line_aux = lines[findheaderinline(lines, "IRTB1 IRTB2", time=1) + ((new_chn - 1) // 12) + 1].split()
        for i in range(0, 12 - (new_chn % 12)):
            line_aux[-i-1] = "  "

        line_aux = '     ' + '     '.join(line_aux) + '\n'  # creates a sole string with the appropriate format
        lines[findheaderinline(lines, "IRTB1 IRTB2", time=1) + ((new_chn - 1) // 12) + 1] = line_aux

    # Changes NFLT in Card 9.1

    line_aux = lines[findheaderinline(lines, "NFLT IRLF", time=1) + 1].split()
    line_aux[0] = "1"
    line_aux = '     ' + '    '.join(line_aux) + '\n'
    lines[findheaderinline(lines, "NFLT IRLF", time=1) + 1] = line_aux

    # Deletes Card 9.6 and 9.7

    start = findheaderinline(lines, "Card 9.6")-1
    n_oldlines = findnextto(lines, "Card 9.6", "********") - start - 1
    removeexcesslines(lines, start, n_oldlines, 0)

    # Changes NMAT in Card 10.1

    line_aux = lines[findheaderinline(lines, "NMAT NDM2", time=1) + 1].split()
    line_aux[0] = "1"
    line_aux = '     ' + '    '.join(line_aux) + '\n'
    lines[findheaderinline(lines, "NMAT NDM2", time=1) + 1] = line_aux

    # TODO be able to select the exact material table of the rod and delete the rest of them

    # Changes NAXP in Card 11.1

    line_aux = lines[findheaderinline(lines, "NQA NAXP MNXN", time=1) + 1].split()
    line_aux[1] = str(1)
    line_aux = '     ' + '   '.join(line_aux) + '\n'  # creates a sole string with the appropriate format
    lines[findheaderinline(lines, "NQA NAXP MNXN", time=1) + 1] = line_aux  # stores the modified line into its position

    # Deletes second axial profile. In future versions this could be linked to the number of axial profiles left

    deletebetweencards(lines, "Card 11.3", "Card 11.7", 2)

    # Changes number of boundary conditions in Card 13.1

    line_aux = lines[findheaderinline(lines, "NBND NKBD NFUN", time=1) + 1].split()
    line_aux[0] = str(2*new_chn)
    line_aux = '     ' + '   '.join(line_aux) + '\n'  # creates a sole string with the appropriate format
    lines[findheaderinline(lines, "NBND NKBD NFUN", time=1) + 1] = line_aux  # stores the modified line
    # into its position

    # deletes excess of boundary conditions in card 13.4
    removeexcesslines(lines, findheaderinline(lines, "IBD1 IBD2", time=1), nchn, new_chn)
    removeexcesslines(lines, findheaderinline(lines, "outlet b.c.", time=1), nchn, new_chn)

    # Stores the old radial profile. edits radial profile card. There is the need of knowing how many lines need
    # to be removed

    rad_profile = np.zeros((nrods, 1))
    for i in range(0, nrods):
        rad_profile[i] = float(lines[findheaderinline(lines, "FQR1  FQR2", time=1) + 1 + (i // 8)].split()[i % 8])

    new_rods = new_chn
    new_rad_profile = np.zeros((new_rods, 1))

    for i in range(0, nrods):
        for j in range(0, 2):
            for k in range(0, 2):
                new_rad_profile[findsubchannelinchannel(subchannels_in_channel, subchannels_in_rod[i][j][k])-1] += 0.25 * rad_profile[i]

    new_rad_profile = np.true_divide(new_rad_profile, float(sum(new_rad_profile))) * float(new_chn)

    if nrods % 8 > 0:
        nrows_lines = nrods // 8 + 1
    else:
        nrows_lines = nrods // 8

    if new_rods % 8 > 0:
        nnewrods_lines = new_rods // 8 + 1
    else:
        nnewrods_lines = new_rods // 8

    removeexcesslines(lines, findheaderinline(lines, "FQR1  FQR2", time=1), nrows_lines, nnewrods_lines)

    # Changes the rod map dimensions in Card 17.2
    line_aux = lines[findheaderinline(lines, "TOTRODSROW TOTRODSCOL", time=1) + 1].split()
    line_aux[0], line_aux[1] = str(new_chn_side), str(new_chn_side)
    line_aux = '     ' + '   '.join(line_aux) + '\n'  # creates a sole string with the appropriate format
    lines[findheaderinline(lines, "TOTRODSROW TOTRODSCOL", time=1) + 1] = line_aux  # stores the modified line
    # into its position

    # Changes the channel map dimensions in Card 17.3
    line_aux = lines[findheaderinline(lines, "TOTCHANSROW TOTCHANSCOL", time=1) + 1].split()
    line_aux[0], line_aux[1] = str(new_chn_side), str(new_chn_side)
    line_aux = '     ' + '   '.join(line_aux) + '\n'  # creates a sole string with the appropriate format
    lines[findheaderinline(lines, "TOTCHANSROW TOTCHANSCOL", time=1) + 1] = line_aux  # stores the modified line
    # into its position

    # Deletes excess of lines in rod map and channels map
    removeexcesslines(lines, findcardinline(lines, "Card 17.4 - Rod Map"), nchn_side-1, new_chn_side)
    removeexcesslines(lines, findcardinline(lines, "Card 17.4 - Channel Map"), nchn_side, new_chn_side)

    # Creates the maps
    substitute = " "
    for i in range(0, new_chn_side):
        substitute = substitute+"  1"

    substitute = substitute+"\n"

    for i in range(0, new_chn_side):
        lines[findcardinline(lines, "Card 17.4 - Rod Map")+1+i] = substitute
        lines[findcardinline(lines, "Card 17.4 - Channel Map")+1+i] = substitute

    '''This is the fun zone, do not disturb
    '''

    new_an_pw = np.zeros((new_chn, 2))
    new_sizes = np.zeros((new_chn, 2))
    new_loc_channels = np.zeros((new_chn, 2))
    for i in range(0, subchannels_in_channel.shape[0]):
        aux1 = 0
        aux2 = 0
        aux_x = 0
        aux_y = 0
        for j in range(0, subchannels_in_channel.shape[1]):
            for k in range(0,  subchannels_in_channel.shape[2]):
                aux1 += anom[int(subchannels_in_channel[i][j][k])-1]
                aux2 += pw[int(subchannels_in_channel[i][j][k])-1]
                if j == 0:
                    aux_x += xsiz[int(subchannels_in_channel[i][j][k])-1]
                if k == 0:
                    aux_y += ysiz[int(subchannels_in_channel[i][j][k])-1]

        new_an_pw[i][0] = aux1
        new_an_pw[i][1] = aux2
        new_sizes[i][0] = aux_x
        new_sizes[i][1] = aux_y
        if i == 0:
            new_loc_channels[0][0] = -bundle_pitch/2 + new_sizes[0][0]/2
            new_loc_channels[0][1] = bundle_pitch/2 - new_sizes[0][1]/2
        else:
            if ((i-1) // new_chn_side) == (i // new_chn_side):
                new_loc_channels[i][0] = new_loc_channels[i-1][0] + (new_sizes[i-1][0] + new_sizes[i][0])/2
                new_loc_channels[i][1] = new_loc_channels[i-1][1]
            else:
                new_loc_channels[i][0] = new_loc_channels[i-new_chn_side][0]
                new_loc_channels[i][1] = new_loc_channels[i-new_chn_side][1] - (new_sizes[i-new_chn_side][1]+new_sizes[i][1])/2

    # creates an array with the data for the new gaps
    new_gap_data = [[0] * 8 for _ in range(new_ngaps)]

    for i in range(0, new_ngaps):
        new_gap_data[i][0] = int(i+1)
        nrep = 2*new_chn_side-1  # number of gaps alternated
        aux = float(0)
        if i <= new_ngaps - new_chn_side:
            if (i+1) % nrep == 0:
                new_gap_data[i][5] = 'y'
                new_gap_data[i][1] = new_chn_side*((i+1) // nrep)
                new_gap_data[i][2] = new_gap_data[i][1] + new_chn_side
            else:
                if ((i+1) % nrep) % 2 == 1:
                    new_gap_data[i][5] = 'x'
                    new_gap_data[i][1] = ((i+1) // nrep) * new_chn_side + (((i+1) % nrep) // 2) + 1
                    new_gap_data[i][2] = new_gap_data[i][1] + 1
                else:
                    new_gap_data[i][5] = 'y'
                    new_gap_data[i][1] = ((i + 1) // nrep) * new_chn_side + (((i + 1) % nrep) // 2)
                    new_gap_data[i][2] = new_gap_data[i][1] + new_chn_side

        else:
            new_gap_data[i][5] = 'x'
            new_gap_data[i][1] = (new_chn_side-1)*new_chn_side + ((i + 1) % nrep)
            new_gap_data[i][2] = new_gap_data[i][1] + 1

        if new_gap_data[i][5] == 'x':
            for j in range(0, D_lev):
                search = subchannels_in_channel[new_gap_data[i][1]-1][j][D_lev - 1]
                aux += gap_data[findthechannelingaps(gap_data, search, time=1) - 1][3]
            new_gap_data[i][4] = new_loc_channels[new_gap_data[i][2]-1][0] - new_loc_channels[new_gap_data[i][1]-1][0]
            new_gap_data[i][6] = new_loc_channels[new_gap_data[i][1]-1][0] + new_sizes[new_gap_data[i][1]-1][0]/2
            if abs(new_gap_data[i][6]) < 1e-6:
                new_gap_data[i][6] = 0.0
            new_gap_data[i][7] = new_loc_channels[new_gap_data[i][1]-1][1]

        if new_gap_data[i][5] == 'y':
            for j in range(0, D_lev):
                search = subchannels_in_channel[new_gap_data[i][1]-1][D_lev-1][j]
                aux += gap_data[findthechannelingaps(gap_data, search, time=2) - 1][3]
            new_gap_data[i][4] = new_loc_channels[new_gap_data[i][1]-1][1] - new_loc_channels[new_gap_data[i][2]-1][1]
            new_gap_data[i][6] = new_loc_channels[new_gap_data[i][1]-1][0]
            new_gap_data[i][7] = new_loc_channels[new_gap_data[i][1]-1][1] - new_sizes[new_gap_data[i][1]-1][1]/2
            if abs(new_gap_data[i][7]) < 1e-6:
                new_gap_data[i][7] = 0.0
        new_gap_data[i][3] = aux  # stores the GAP magnitude

    # creates a vector with the Rmults
    rmult = np.zeros((new_chn, 1))
    for i in range(0, nrods):
        for j in range(0, 2):
            for k in range(0, 2):
                rmult[findsubchannelinchannel(subchannels_in_channel, subchannels_in_rod[i][j][k]) - 1][0] += 0.25

    # Edit CHANNEL DATA
    for i in range(0, new_chn):
        line_aux = lines[findheaderinline(lines, "I AN PW", time=1) + 1 + i].split()
        line_aux[1] = format_e(new_an_pw[i][0])
        line_aux[2] = format_e(new_an_pw[i][1])
        line_aux[6] = format_e(new_loc_channels[i][0])
        line_aux[7] = format_e(new_loc_channels[i][1])
        line_aux[8] = format_e(new_sizes[i][0])
        line_aux[9] = format_e(new_sizes[i][1])
        line_aux = '     ' + '   '.join(line_aux) + '\n'  # creates a sole string with the appropriate format
        lines[findheaderinline(lines, "I AN PW", time=1) + 1 + i] = line_aux  # stores the modified line

    # Edit GAP DATA
    for i in range(0, new_ngaps):
        line_aux = lines[findheaderinline(lines, "K IK JK") + 3 + 2 * i].split()
        line_aux1 = lines[findheaderinline(lines, "K IK JK") + 4 + 2 * i].split()
        line_aux2 = lines[findheaderinline(lines, "K X Y NORM")+1 + i].split()

        line_aux[1] = str(new_gap_data[i][1])
        line_aux[2] = str(new_gap_data[i][2])
        line_aux[3] = format_e(new_gap_data[i][3])
        line_aux[4] = format_e(new_gap_data[i][4])

        line_aux1[0] = str(D_lev)  # GMULT

        line_aux2[1] = format_e(new_gap_data[i][6])
        line_aux2[2] = format_e(new_gap_data[i][7])
        line_aux2[3] = new_gap_data[i][5]

        line_aux = '     ' + '   '.join(line_aux) + '\n'
        line_aux1 = '     ' + '   '.join(line_aux1) + '\n'
        line_aux2 = '     ' + '   '.join(line_aux2) + '\n'

        lines[findheaderinline(lines, "K IK JK") + 3 + 2 * i] = line_aux
        lines[findheaderinline(lines, "K IK JK") + 4 + 2 * i] = line_aux1
        lines[findheaderinline(lines, "K X Y NORM") + 1 + i] = line_aux2

    # EDIT ROD and conductor data

    for i in range(0, new_chn):
        line_aux = lines[findheaderinline(lines, "NSCH PIE") + 1 + 2 * i].split()
        line_aux1 = lines[findheaderinline(lines, "NSCH PIE") + 2 + 2 * i].split()

        line_aux[5] = str(float(rmult[i]))
        line_aux1[0] = line_aux[0]
        line_aux1[1] = '1.000'
        line_aux1[2] = '0'
        line_aux1[3] = '0.000'
        line_aux1[4] = '0'
        line_aux1[5] = '0.000'
        line_aux1[6] = '0'
        line_aux1[7] = '0.000'
        line_aux1[8] = '0'
        line_aux1[9] = '0.000'
        line_aux1[10] = '0'
        line_aux1[11] = '0.000'
        line_aux1[12] = '0'
        line_aux1[13] = '0.000'
        line_aux1[14] = '0'
        line_aux1[15] = '0.000'

        line_aux = '     ' + '   '.join(line_aux) + '\n'
        line_aux1 = '     ' + '   '.join(line_aux1) + '\n'

        lines[findheaderinline(lines, "NSCH PIE") + 1 + 2 * i] = line_aux
        lines[findheaderinline(lines, "NSCH PIE") + 2 + 2 * i] = line_aux1

    # Rewrite the radial profile
    lines_rp = ((new_rods - 1) // 8) + 1
    for i in range(0, lines_rp):
        if i != lines_rp - 1:
            line_aux = ['0.0']*8
            for j in range(0, 8):
                line_aux[j] = "{:.6f}".format(float(new_rad_profile[5*i + j]))

            line_aux = '     ' + '   '.join(line_aux) + '\n'
            lines[findheaderinline(lines, "FQR1 FQR2 FQR3") + 1 + i] = line_aux

        else:
            empty = 8 - int(new_rods % 8)
            if empty == 0:
                line_aux = ['0.0'] * 8
                for j in range(0, 8):
                    line_aux[j] = "{:.6f}".format(float(new_rad_profile[5 * i + j]))

                line_aux = '     ' + '   '.join(line_aux) + '\n'
                lines[findheaderinline(lines, "FQR1 FQR2 FQR3") + 1 + i] = line_aux

            else:
                line_aux = ['0.0'] * (8 - empty)
                for j in range(0, 8 - empty):
                    line_aux[j] = "{:.6f}".format(float(new_rad_profile[5 * i + j]))

                line_aux = '     ' + '   '.join(line_aux) + '\n'
                lines[findheaderinline(lines, "FQR1 FQR2 FQR3") + 1 + i] = line_aux

    # End of the track
    # open('Deck_definitivo.inp', 'x')
    file = open('deck_definitivo.inp', 'w')
    file.writelines(lines)
    file.close()

    # TODO correct the alignment when writing lines (e.g. in channels or gaps cards) -> deck.inp file is more readable


main()

