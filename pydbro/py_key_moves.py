#
# PROGRAM: PYTHON CONSOLE DATABASE BROWSER
# MODULE : KEY PRESS PROCESSOR
#


def key_moves(
    he,  # screen height
    wi,  # screen width
    k,  # pressed keycode
    curx,  # current cell x coordinate
    cury,  # current cell y coordinate
    maxx,  # number of columns
    maxy,  # number of rows
    cur_win,  # current window [ left, right ]
    tabf,  # visible rows shift from
    tabt,  # visible rows shift number
    act,  # action
    curtabsf,  # left window visible records shift
    colshift=0,  # right window columns shift
):
    act = ""
    if k == ord("j"):
        if cury < maxy:
            cury += 1
    elif k == ord("J"):
        if tabf < maxy - 1:
            tabf += 1
    elif k == ord("k"):
        if cury > 1:
            cury -= 1
    elif k == ord("K"):
        if tabf > 0:
            tabf -= 1
    elif k == ord("@"):
        tabf += cury - 1
        cury = 1
    elif k == ord("h"):
        if curx > 0:
            curx -= 1
    elif k == ord("l"):
        if curx < maxx - colshift - 1:
            curx += 1
    elif k == ord("L"):
        if colshift < maxx - curx - 1:
            colshift += 1
    elif k == ord("H"):
        if colshift > 0:
            colshift -= 1
    elif k == ord("0"):
        curx = 0
    elif k == ord("G"):
        if cur_win == "right":
            curx = maxx - 1
            cury = maxy
    elif k == ord("n"):
        if maxy > 0:
            tabf += he - 1
            cury = 1
    elif k == ord("u"):
        if tabf > he - 1:
            tabf -= he - 1
        else:
            tabf = 0
    elif k == ord("s"):
        act = "asc"
    elif k == ord("S"):
        act = "desc"
    elif k == ord("X"):
        act = "reset_view"
    elif k == ord("f"):
        act = "filter"
    elif k == ord("\t"):
        if cur_win == "left":
            cur_win = "right"
        elif cur_win == "right":
            cur_win = "left"
    elif k == ord("m"):
        if maxy > he - 3:
            curtabsf += he - 1
        else:
            cury = maxy
    elif k == ord("i"):
        if curtabsf >= he - 1:
            curtabsf -= he - 1
        else:
            cury = 1
    elif k == ord("?"):
        act = "help"
    elif k == ord("r"):
        act = "refresh"
    elif k == ord("e"):
        act = "edit_cell"
    elif k == ord("a"):
        act = "insert_row"
    elif k == ord("d"):
        act = "delete_row"
    # elif k == ord("p"):
    #  act="query"
    elif k == ord("$"):
        act = "conn_info"
    # if cury > maxy:
    #  cury = maxy
    return (curx, cury, cur_win, tabf, tabt, act, curtabsf, colshift)
