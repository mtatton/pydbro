# -*- coding: utf-8 -*-
#
# PROGRAM: PYTHON CONSOLE DATABASE BROWSER
# MODULE : READ USER INPUT AS STRING
#

import curses
from pydbro.py_ugetch import ugetch
from pydbro.py_log import msg_log


def read_str(screen, col, p_banner, strdef="", passwd=0):

    curses.curs_set(1)
    curses.noecho()
    ch = 0
    prev_ch = 0
    if strdef != "":
        vstr = strdef
    else:
        vstr = ""
    screen.move(0, 0)
    screen.addstr(p_banner, col["miGr"])
    # screen.move(1,0)
    # screen.addstr("-"*(wi-1),col["loGr"])
    screen.move(1, 0)
    curx = 0
    cury = 0
    curword = 0
    if len(vstr) > 0:
        if passwd == 1:
            screen.addstr("*" * (len(vstr)), col["hiGr"])
        else:
            screen.addstr(vstr, col["hiGr"])
    screen.attrset(col["hiGr"])
    while ch != 10:
        ch = ugetch(screen)
        screen.move(1, 0)
        screen.clrtoeol()
        if ch == 127 or ch == 263 or ch == 8:
            vstr = vstr[:-1]
        else:
            vstr += chr(ch)
        if passwd == 0:
            screen.addstr(vstr)
        else:
            screen.addstr("*" * len(vstr))
    vstr = vstr[:-1]
    # msg_log(vstr)
    curses.curs_set(0)
    return vstr


## UNIT TEST
# from py_curses_lib import init_colors
# screen = curses.initscr()
# col = init_colors()
# read_str(screen, col, "test", "select 1 from dual union all select 1", passwd = 0)
# curses.endwin()
