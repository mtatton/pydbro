#!/usr/bin/python3
#
# PROGRAM: PYTHON CONSOLE BROWSER CONNECTION EDITOR
# MODULE : MAIN PROBRAM
#

import traceback
import sys
import os
import curses
import pydbro.py_break_handler
import json

from pydbro.py_curses_lib import init_colors

screen = None
he = None
wi = None
col = None

str_con_types = """

1] mysql
2] postres
3] oracle
4] exit

-----------"""

str_con_file = ""


def read_str(p_banner, strdef="", passwd=0):
    key = "0"
    if strdef != "":
        vstr = strdef
    else:
        vstr = ""
    screen.move(0, 0)
    screen.addstr(p_banner, col["hiGr"])
    screen.move(1, 0)
    screen.addstr("-" * (wi - 1), col["loGr"])
    screen.move(2, 0)
    if len(vstr) > 0:
        if passwd == 1:
            screen.addstr("*" * (len(vstr)), col["hiGr"])
        else:
            screen.addstr(vstr, col["hiGr"])
    while key != 10:
        # screen.clrtoeol()
        key = screen.getch()
        if (key >= ord(" ") and key <= ord("~")) or (
            key == 127 or key == 263 or key == 8
        ):
            strlen = len(vstr)
            if key == 127 or key == 263 or key == 8:
                if strlen >= 0:
                    vstr = vstr[:-1]
                    strlen = len(vstr)
                    screen.move(2, strlen)
                    screen.delch()
            else:
                vstr += chr(key)
                screen.attrset(col["hiGr"])
                if passwd == 1:
                    screen.addch("*")
                else:
                    screen.addch(chr(key))
    return vstr


def cls():
    # screen.clear()
    screen.move(0, 0)
    cy = 0
    for cy in range(0, he):
        screen.move(cy, 0)
        screen.clrtoeol()


def input_screen(input_text, def_value="", passwd=0):
    if passwd == 1:
        value = read_str(input_text, def_value, 1)
    else:
        value = read_str(input_text, def_value)
    screen.move(4, 0)
    if passwd == 1:
        screen.addstr("Entered ******", col["hiGr"])
    else:
        screen.addstr("Entered {}".format(value), col["hiGr"])
    screen.move(5, 0)
    screen.addstr("Press Any Key to next screen ...", col["loGr"])
    screen.getch()
    cls()
    return value


def read_con(DB):
    defjson = ""
    sqlcon_file = ""
    if DB == "mysql":
        sqlcon_file = "sqlmk_conn.json"
        defjson = '{ "host": "localhost", "port": "3306", "user": "user", "password": "pass", "database": "dbname" }'
    elif DB == "oracle":
        sqlcon_file = "sqlok_conn.json"
        defjson = '{"host": "localhost", "port": "1521", "database": "xe", "user": "hr", "password": "hr"}'
    elif DB == "postgres":
        sqlcon_file = "sqlpk_conn.json"
        defjson = '{"host": "localhost", "port": "5432", "database": "dbname", "user": "user", "password": "pass"}'
    if os.path.exists(sqlcon_file):
        f = open(sqlcon_file, "r")
        constr = f.read()
        f.close()
        con = json.loads(constr)
    else:
        con = json.loads(defjson)
    return con


def save_con(DB, con):
    if DB == "mysql":
        f = open("sqlmk_conn.json", "w")
    elif DB == "postgres":
        f = open("sqlpk_conn.json", "w")
    elif DB == "oracle":
        f = open("sqlok_conn.json", "w")
    f.write(json.dumps(con))
    f.close()
    return 1


def main():

    global screen
    global he
    global wi
    global col

    try:
        DB = ""
        hostname = ""
        port = ""
        username = ""
        password = ""
        database = ""
        screen = curses.initscr()
        curses.noecho()
        col = init_colors()
        he, wi = screen.getmaxyx()
        curli = 1
        for line in str_con_types.split("\n"):
            screen.move(curli, 0)
            screen.addstr(line, col["hiGr"])
            curli += 1
        value = read_str("Enter connection type [ 1-4 ]:  ")
        screen.move(10, 0)
        if value == "1":
            DB = "mysql"
        elif value == "2":
            DB = "postgres"
        elif value == "3":
            DB = "oracle"
        else:
            cls()
            curses.echo()
            curses.endwin()
            print("No Changes Made")
            exit()
        screen.addstr("selected {} {}".format(value, DB), col["hiGr"])
        screen.move(11, 0)
        screen.addstr("Press Any Key to next screen ...", col["miGr"])
        screen.getch()
        cls()
        # EDIT CONNECTION INFO
        con = read_con(DB)
        he, wi = screen.getmaxyx()
        con["host"] = input_screen("Enter " + DB + " host: ", con["host"])
        con["port"] = input_screen("Enter " + DB + " port: ", con["port"])
        con["user"] = input_screen("Enter " + DB + " user: ", con["user"])
        con["password"] = input_screen("Enter " + DB + " user: ", con["password"], 1)
        con["database"] = input_screen("Enter " + DB + " database: ", con["database"])
        curses.endwin()
        if save_con(DB, con) == 1:
            print("Connection Information for " + DB + " saved.")
        else:
            print("Connection Information for " + DB + " not saved.")
    except Exception as e:
        curses.echo()
        curses.endwin()
        traceback.print_exc(file=sys.stdout)
        exit()


def cli():
    main()


if __name__ == "__main__":
    main()
