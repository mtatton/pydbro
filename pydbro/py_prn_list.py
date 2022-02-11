#
# PROGRAM: PYTHON CONSOLE DATABASE BROWSER
# MODULE : PRINT LIST
#

from pydbro.py_list_to_str import list_to_str
from pydbro.py_get_list_vals import get_list_vals
from pydbro.py_curses_lib import init_colors
from pydbro.py_log import msg_log
import pydbro.py_qry
from datetime import datetime

# print list on curses screen
def prn_list(
    res,  # dataframe
    screen,  # curses screen
    he,  # screen height
    wi,  # screen width
    begx=0,  # starting position on screen x
    begy=0,  # starting position on screen y
    curx=0,  # current x coordinate
    cury=0,  # current y coordinate
    skip_rowid=0,  # don't print rowid
    colshift=0,  # data screen shift
):
    # default column size
    def_col_sz = 3
    # init colors
    col = init_colors()
    # width of columns
    xcolsz = []
    # convert list to string
    prn = list_to_str(res)
    # split string to rows
    rows = prn.split("\n")
    # get list keys
    list_keys = list(res.keys())
    # get data frame width
    maxx = len(list_keys) - 1
    # get data frame height
    maxy = len(rows) - 1
    # calculate the data frame max lenghts
    for i in list_keys:
        # remove empty cells
        inlist = get_list_vals(res[i])
        # get max length for given col
        if len(inlist) > 0:
            xlenstr = max(inlist)
        # or use default size
        else:
            xlenstr = def_col_sz
        # add it to size array
        xcolsz.append(xlenstr)
    # declare vars
    cur = ""
    prnx = 0
    prny = 0
    sy = begy
    curcol = 0
    # for each row
    for r in rows:
        curcol = 0
        sx = begx
        prnx = 0
        # starting columns
        skipcols = colshift
        # for each column in row
        for c in r.split("|"):
            # handle the skip rowid
            if skip_rowid == 1 and curcol == 0:
                curcol = 1
            # substract one despite rowid
            elif skipcols > 0:
                skipcols -= 1
            else:
                # save screen width
                strcut = wi - 1
                # if cell is wider than width
                if sx + len(str(c)) > wi - 1:
                    strcut = wi - 1 - sx
                # if the cell has more rows fir to the screen
                if sy + len(c.split("\n")) > he or strcut < 0:
                    break
                # move to the position
                screen.move(sy, sx)
                # set color
                clr = col["loGr"]
                # if this is the current cell
                if curx == prnx and cury == prny:
                    # set it brighter
                    clr = col["hiGr"]
                    # and prepare for return
                    cur = c
                # add string to screen
                screen.addstr(str(c)[0:strcut], clr)
                # if we've got column size
                if len(xcolsz) > 0:
                    # setup x coordinate for next column
                    sx += xcolsz[curcol + colshift] + 1
                prnx += 1
                curcol += 1
        if sy > he - 1:
            break
        screen.move(sy, 0)
        sy += 1
        prny += 1
    return (cur, maxx, maxy, xcolsz)
