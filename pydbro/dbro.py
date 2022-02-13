#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# (c) MMXXII UNKNOWN
#
# PROGRAM: PYTHON CONSOLE DATABASE BROWSER
# MODULE : MAIN PROGRAM
#
# VERSION: 0.1m
#
# CHANGELOG:
#
# 20220202 INIT
#
# WORKLOG:
#
# BUGS:
#
# TBD:
#

import curses
import traceback
import os.path
import sys
import sqlite3
import json

from pydbro.py_prn_list import prn_list
from pydbro.py_curses_lib import init_colors
from pydbro.py_key_moves import key_moves
from pydbro.py_error_handler import error_handler
from pydbro.py_log import msg_log
from pydbro.py_cmd_params import cmd_params
from pydbro.py_read_str import read_str

from pydbro.py_cfg import cfg_get_value
from pydbro.py_cfg import cfg_set_value
from pydbro.py_cfg import prep_cfg_storage

import pydbro.py_break_handler

ccon = None
DB = None
screen = None
col = None
he = None
wi = None
cfg_qry2dict = None


def prn_intro_scr():
    logo = """ 

  ______   _____ ___   ___ ______    ____
  \     `\|  |  |   `\|   |\     `\/'    |
   |   T  |  |  |>    |  <__|   >  |     |
   |   '_,|__   |     |     |     /'  T  |
   |   |  __/  /|  T  |  T  |     `|  :  |
   |   | |     ||  '  |  '  |   |  |     |
   `---' `-----'`-----'-----'---'--`-----'
  %xxxxxxxxx<  CONSOLE PYTHON  >xxxxxxxxx%
  ----------< DATABASE BROWSER >----------
  %xxxxxxxxx< (c) 2022 UNKNOWN >xxxxxxxxx%
  ----------------------------------------

"""
    cls()
    curli = 0
    shift = int(wi / 4)
    for line in logo.split("\n"):
        screen.move(curli, 0 + shift)
        screen.addstr(line, col["hiGr"])
        curli += 1
    screen.move(0, wi - 1)
    screen.getch()
    cls()


str_help = """
  Help Keyboard Controls:
  
  ?   - this help        $ - connection information   r   - reread 
  
  tab      - toggle left / right panel (tables, table content)

  j,k,h,l  - move down, up, left, right
  L,H      - shift columns right, left
  0,G      - go to upper left, lower right table corner 
  n,u      - next, previous page of records
  @        - scroll current row to the top

  s,S      - sort ascending, descending by current column
  f        - filter (enter claus after where ... )
  X        - reset view (filter, sort) on current table

  m, i     - move rows view by 1 page down (tables list)
  e        - edit current cell 
  d        - delete current row
  a        - add new row

"""

sql_tab_cols = {"sqlite": "", "mysql": "", "postgres": "", "oracle": ""}

# sqlite
sql_tab_cols[
    "sqlite"
] = """-- GET TABLE COLUMNS
select group_concat(name,'|') as cols
from pragma_table_info('%TABLE%')
order by cid asc"""

# mysql
sql_tab_cols[
    "mysql"
] = """-- GET TABLE COLUMNS
select group_concat(column_name) as cols
from information_schema.columns
where table_schema = 'bhxfcz9969' 
and table_name = '%TABLE%'"""

# postgres
sql_tab_cols[
    "postgres"
] = """-- GET TABLE COLUMNS
select string_agg(column_name,'|') as cols
from information_schema.columns
where table_name = '%TABLE%'
and table_schema = 'public'
and table_catalog = 'osm'"""

# oracle
sql_tab_cols[
    "oracle"
] = """-- GET TABLE COLUMNS
select listagg(column_name,'|') as "cols"
from user_tab_columns
where table_name = '%TABLE%'
order by column_name asc"""

sql_get_tabs = {"sqlite": "", "mysql": "", "postgres": "", "oracle": ""}

# sqlite
sql_get_tabs[
    "sqlite"
] = """-- GET TABLES
select name
from sqlite_master sm
where type in ('table','view')
order by name asc
limit ?, ?"""

# mysql
sql_get_tabs[
    "mysql"
] = """-- GET TABLES
select table_name as "name"
from information_schema.tables
where %FILTER%
and table_schema = %s
order by table_name asc
limit %s, %s"""

# postgres
sql_get_tabs[
    "postgres"
] = """-- GET TABLES
select table_name "name"
from information_schema.tables
where %FILTER%
and table_catalog = %s
and table_type = 'BASE TABLE'
and table_schema in ('public')
order by table_name asc
limit %s offset %s"""

# oracle
sql_get_tabs[
    "oracle"
] = """-- GET TABLES
select table_name as "name"
from user_tables sm
where %FILTER%
order by table_name asc
offset :1 rows fetch 
next :2 rows only"""

sql_pk_tab_col = {"sqlite": "", "mysql": "", "postgres": "", "oracle": ""}

sql_pk_tab_col[
    "mysql"
] = """-- GET PK COLS
  select column_name col
  from information_schema.columns 
  where column_key = "pri" 
  and table_schema = database()
  and table_name = %s"""

sql_pk_tab = {"sqlite": "", "mysql": "", "postgres": "", "oracle": ""}

# mysql test for primery key
sql_pk_tab[
    "mysql"
] = """-- TEST FOR PK
select _rowid rowid
from %TABLE% a
limit 1"""

sql_get_tab = {"sqlite": "", "mysql": "", "postgres": "", "oracle": ""}

# sqlite
sql_get_tab[
    "sqlite"
] = """-- GET TABLE CONTENT
select a.rowid, a.*
from %TABLE% a
where %FILTER%
order by %SORTED%
limit ?, ?"""


# mysql
sql_get_tab[
    "mysql"
] = """-- GET TABLE CONTENT
select %ROWID% rowid, a.*
from %TABLE% a
where %FILTER%
order by %SORTED%
limit %s, %s"""

# postgres
sql_get_tab[
    "postgres"
] = """-- GET TABLE CONTENT
-- select row_number() over (order by 1 asc) as rowid, a.*
select 1 as rowid, a.*
from %TABLE% a
where %FILTER%
order by %SORTED%
limit %s offset %s"""
# from %TABLE% a

# oracle
sql_get_tab[
    "oracle"
] = """-- GET TABLE CONTENT
select a.rowid as "rowid", a.*
from %TABLE% a
where %FILTER%
order by %SORTED%
offset :1 rows fetch 
next :2 rows only"""


def read_conn_info(DB):
    defjson = ""
    sqlcon_file = ""
    if DB == "mysql":
        sqlcon_file = "sqlmk_conn.json"
    elif DB == "oracle":
        sqlcon_file = "sqlok_conn.json"
    elif DB == "postgres":
        sqlcon_file = "sqlpk_conn.json"
    if os.path.exists(sqlcon_file):
        f = open(sqlcon_file, "r")
        constr = f.read()
        f.close()
        con = json.loads(constr)
    else:
        con = None
    return con


def prn_title(title):
    screen.move(he - 1, 0)
    screen.clrtoeol()
    screen.addstr(str(title), col["loGr"])


def prn_info(p_str):
    screen.move(he - 2, 0)
    screen.clrtoeol()
    screen.addstr(str(p_str), col["miGr"])


def cls():
    # screen.refresh()
    # screen.clear()
    # screen.refresh()
    screen.move(0, 0)
    cy = 0
    for cy in range(0, he):
        screen.move(cy, 0)
        screen.clrtoeol()


def main():

    global screen
    global col
    global he
    global wi
    global ccon
    global cfg_qry2dict

    res = None
    stodb = "db"
    stotab = "tab"
    stokey = "key"
    stoval = "val"
    cfg_dbf = ":memory:"

    try:

        # msg on pydbro init
        msg_log("|* pydbro init")
        # PROCESS PROGRAM COMMAND LINE PARAMETER
        dbfile = ""
        DB, dbfile = cmd_params(sys.argv)

        dbcon = None
        from pydbro.py_qry import setup_qry_method

        qry2dict = setup_qry_method(DB, dbfile)

        ccon = prep_cfg_storage()

        # CURSES INIT
        screen = curses.initscr()
        curses.noecho()
        col = init_colors()
        he, wi = screen.getmaxyx()

        # prn_intro_scr()

        curx = 0
        cury = 1
        maxx = 0
        maxy = 0
        k = None
        cur_win = "left"
        p_cur_win = "left"
        tabf = 0
        tabt = 0
        rcurx = 0
        rcury = 1
        rtabf = 0
        rtabt = he - 1
        rsortcol = 1
        act = ""
        is_sorted = 0
        sortdir = "asc"
        rfilter = "1=1"
        filtered = 0
        maxxd = 1
        maxyd = 1
        curtabsf = 0  # table list shift
        curtabst = he - 2  # table list shift sizeeee
        colshift = 0  # right table column shift
        voidcs = 0  # dummy colshift for left call
        lfiltered = 0  # table list filtered
        prev_tab_sql = ""
        prev_tab = ""
        prev_tab_params = None
        prev_tabs_sql = ""
        orig_tabs_sql = ""
        prev_tabs_params = None
        cols = None
        colsl = None
        # curtab=cur.replace('\n','')
        curtab = ""
        has_pk = 0
        cust_qry = "select 1 from dual"

        # MAIN INTERACTION
        while k != ord("q"):
            # get screen dimensions
            he, wi = screen.getmaxyx()
            # clear the screen
            cls()
            # store previous window
            p_cur_win = cur_win
            # process the keyboard input
            if cur_win == "left":
                curx, cury, cur_win, tabf, tabt, act, curtabsf, colshift = key_moves(
                    he,
                    wi,
                    k,
                    curx,
                    cury,
                    maxx,
                    maxy,
                    cur_win,
                    tabf,
                    tabt,
                    act,
                    curtabsf,
                    colshift,
                )
            else:
                (
                    rcurx,
                    rcury,
                    cur_win,
                    rtabf,
                    rtabt,
                    act,
                    curtabsf,
                    colshift,
                ) = key_moves(
                    he,
                    wi,
                    k,
                    rcurx,
                    rcury,
                    maxxd,
                    maxyd,
                    cur_win,
                    rtabf,
                    rtabt,
                    act,
                    curtabsf,
                    colshift,
                )
            # action for help screen
            if act == "help":
                # print introduction screen
                prn_intro_scr()
                sy = 0
                # print keyboard mapping
                for li in str_help.split("\n"):
                    screen.move(sy, 0)
                    screen.addstr(li, col["miGr"])
                    sy += 1
                screen.move(he - 1, 0)
                screen.getch()
                cls()
                action = "refresh"
            # enter query and execute
            elif act == "query":
                ck = "0"
                prev_cust_qry = ""
                while ck != ord("q"):
                    cls()
                    screen.move(0, 0)
                    cust_qry = read_str(screen, col, "Enter Query: ", cust_qry)
                    if len(cust_qry) > 0 and cust_qry[-1] == ";":
                        cust_qry = cust_qry[:-1]
                    elif len(cust_qry) == 0:
                        break
                    try:
                        dbcon, cq_res, cq_cols = qry2dict(dbcon, cust_qry, ())
                        cur, maxx, maxy, xcolsz = prn_list(
                            cq_res, screen, he, wi, 0, 3, curx, cury, 0, 0
                        )
                    except:
                        cust_qry = prev_cust_qry
                    prev_cust_qry = cust_qry
                    screen.move(he - 1, 0)
                    screen.addstr("Press <q> to return to dbro")
                    ck = screen.getch()
                cls()
                action = "refresh"
            # action for row insert
            elif act == "insert_row":
                # mysql and postgres doesn't have rowid
                if DB == "mysql" or DB == "postgres":
                    notif = "Insert action on " + DB + " is unsupported"
                    screen.move(he - 5, 0)
                    screen.addstr(notif)
                    screen.getch()
                # otherwise insert new row
                else:
                    collist = ", ".join(cols[1:])
                    colnulls = str("null," * len(cols[1:]))[:-1]
                    qry = (
                        "insert into "
                        + curtab
                        + " ("
                        + collist
                        + ") values ("
                        + colnulls
                        + ")"
                    )
                    dbcon, x, y = qry2dict(dbcon, qry, ())
                # refresh the table view
                act = "refresh"
            # edit cell action
            elif act == "edit_cell":
                # get current cell value
                curval = str(res[curcol][rcury - 1])
                # get current row identification
                currowid = res["rowid"][rcury - 1]
                # prevent user need to delete None
                if curval == "None":
                    curval = ""
                # get new value from user
                newval = read_str(screen, col, "Current Value: " + curval, curval)
                # convert rowid to string (sqlite thing)
                currowid = str(currowid)
                # mysql and postgres is not supported, doesn't provide rowid
                # if (DB == "mysql" and has_pk == 0) or DB == "postgres":
                if DB == "mysql" or DB == "postgres":
                    notif = "Update action on " + DB + " is unsupported"
                    screen.move(he - 5, 0)
                    screen.addstr(notif, col["miGr"])
                    screen.getch()
                # elif DB == "mysql" and has_pk == 1:
                #  pkc = pk_cols["col"][0]
                #  qry="update "+curtab+" set "+curcol+" = '"+newval+"' where "+str(pkc)+" = '"+currowid+"'"
                #  #msg_log(qry)
                #  qry2dict(qry,())
                # prepare the update query
                else:
                    # prevent empty cells
                    if newval == "":
                        newval = "null"
                    else:
                        # newval = """\'{}\'""".format(newval)
                        newval = newval
                    upd_qry = """update {} set {} = :1 where rowid = '{}' """.format(
                        curtab, curcol, currowid
                    )
                    upd_params = (newval,)
                    dbcon, x, y = qry2dict(dbcon, upd_qry, upd_params)
                # clear the screen anyway
                cls()
                # and refresh the table to reflect the changes
                act = "refresh"
            # delete row action
            elif act == "delete_row":
                # get current row identification
                currowid = res["rowid"][rcury - 1]
                # convert it for the sqlite purposes
                currowid = str(currowid)
                # sorry mysql neither postgres supported
                if DB == "mysql" or DB == "postgres":
                    notif = "Delete action on " + DB + " is unsupported"
                    screen.move(he - 5, 0)
                    screen.addstr(notif, col["miGr"])
                    screen.getch()
                else:
                    # prepare the delete query
                    qry = "delete from " + curtab + " where rowid = '" + currowid + "'"
                    # make sure it's a good idea
                    screen.move(0, 0)
                    screen.addstr(
                        "Do You really want to delete this row? y/n", col["hiGr"]
                    )
                    screen.move(1, 0)
                    screen.addstr("Query to be executed: " + qry, col["miGr"])
                    del_decision = screen.getch()
                    # user agrees to delete the row
                    if del_decision == ord("y"):
                        dbcon, x, y = qry2dict(dbcon, qry, ())
                        # fix row deletion cursor movement
                        if rcury >= maxyd - 1:
                            rcury = maxyd - 1
                # clear the screen anyway
                cls()
                # reread the updated table data
                act = "refresh"
            # if the current window is changed
            if cur_win != p_cur_win:
                # make sure the program won't have troubles
                rcurx = 0
                rcury = 1
                colshift = 0
                rtabf = 0
            if prev_tab != curtab:
                sortdir = "asc"
                rsortcol = 1
                rfilter = "1=1"
                filtered = 0
                is_sorted = 0
            # process the request for filter in the left window
            if act == "filter" and cur_win == "left":
                lfilter = ""
                screen.move(0, 0)
                lfilter = read_str(
                    screen, col, "Enter tables filter: lower(table) name like '%...%'"
                )
                if lfilter == "":
                    lfiltered = 0
                else:
                    lfiltered = 1
                    cury = 1
                    # when filter is apllied then move to the first table
                    tabf = 0
                    curtabsf = 0
                act = ""
                screen.move(0, 0)
                screen.clrtoeol()
                # get the new list of tables, filtered
                sql_act_tabs = sql_get_tabs[DB].replace(
                    """%FILTER%""", """lower(table_name) like '%{}%'""".format(lfilter)
                )
            # otherwise get all tables
            elif lfiltered == 0:
                lfilter = "1=1"
                sql_act_tabs = sql_get_tabs[DB].replace(
                    """%FILTER%""", """{}""".format(lfilter)
                )
                # save the vanilla query for invalid filter cases
                orig_tab_sql = sql_act_tabs
            # if we're in left window
            if cur_win == "left":
                # prepare the query parameters
                if DB == "mysql":
                    from pydbro.py_mysql_db import get_mysql_db

                    db = get_mysql_db()
                    cur_tabs_params = (
                        db,
                        curtabsf,
                        curtabst,
                    )
                elif DB == "postgres":
                    from pydbro.py_postgres_db import get_postgres_db

                    db = get_postgres_db()
                    cur_tabs_params = (
                        db,
                        curtabst,
                        curtabsf,
                    )
                else:
                    cur_tabs_params = (curtabsf, curtabst)
                # save some queries if nothing is changed
                if prev_tabs_sql != sql_act_tabs or prev_tabs_params != cur_tab_params:
                    try:
                        dbcon, resl, colsl = qry2dict(
                            dbcon, sql_act_tabs, cur_tabs_params
                        )
                        lenresl = len(resl)
                    except Exception as e:
                        # consider this as an empty query
                        lenresl = 0
                    # fallback in case no table is found by query
                    if len(resl) == 0:
                        lfiltered = 0
                        lfilter = "1=1"
                        sql_act_tabs = sql_get_tabs[DB].replace(
                            """%FILTER%""", """{}""".format(lfilter)
                        )
                        dbcon, resl, colsl = qry2dict(
                            dbcon, sql_act_tabs, cur_tabs_params
                        )
                    prev_tabs_sql = sql_act_tabs
                    prev_tab_params = cur_tabs_params
                # print the list of tables to screen
                cur, maxx, maxy, xcolsz = prn_list(
                    resl, screen, he, wi, 0, 0, curx, cury, 0, voidcs
                )
            # current table
            curtab = cur.replace("\n", "")
            # Restore Current Table Settings -- HERE --
            # get filter for current table
            valf = cfg_get_value(ccon, (curtab, "rfilter"))
            if valf is not None:
                # msg_log(curtab+" "+str(valf))
                rfilter = valf
                if rfilter == "1=1":
                    filtered = 0
                else:
                    filtered = 1
            # get sort criteria
            valsc = cfg_get_value(ccon, (curtab, "rsortcol"))
            valsd = cfg_get_value(ccon, (curtab, "sortdir"))
            if valsc is not None:
                rsortcol = valsc
                if rsortcol == "1":
                    is_sorted = 0
                else:
                    is_sorted = 1
            # get sort direction for current table
            if valsd is not None:
                sortdir = valsd
                if is_sorted == 0 and sortdir == "asc":
                    is_sorted = 0
                else:
                    is_sorted = 1
            # Restore Current Table settings -- END --
            # Prepare the query for the right window
            # reset filter view
            if act == "reset_view":
                filtered = 0
                rfilter = "1=1"
                is_sorted = 0
                sortdir = "asc"
                rsortcol = "1"
                action = "refresh"
            sql_cur_tab = sql_get_tab[DB].replace("%TABLE%", curtab)
            # test for primary key in mysql
            # not yet implemented
            # if DB == "mysql":
            #  # pesimistic
            #  has_pk = 0
            #  # check for primary key columns
            #  sql_pk_tab_q = sql_pk_tab[DB].replace('%TABLE%',curtab)
            #  # retrieve the list
            #  pk_cols, pk_cols_c = qry2dict(sql_pk_tab_col["mysql"],(curtab,))
            #  if len(pk_cols)>0:
            #    #msg_log(curtab + " "+ str(pk_cols)+" "+str(len(pk_cols)))
            #    try:
            #      sql_pk_tab_q = sql_pk_tab[DB].replace('%TABLE%',curtab)
            #      test_pk,test_pk_cols = qry2dict(sql_pk_tab_q,())
            #      sql_cur_tab = sql_cur_tab.replace('%ROWID%','_rowid')
            #      has_pk=1
            #    except:
            #      sql_cur_tab = sql_cur_tab.replace('%ROWID%','1')
            #      has_pk=0
            #      pass
            #  else:
            # Don't even try to use ROWID
            if DB == "mysql":
                sql_cur_tab = sql_cur_tab.replace("%ROWID%", "1")
            # if there is a request for the right table
            if act == "filter" and cur_win == "right":
                key = ""
                rfilter = ""
                screen.move(0, 0)
                rfilter = read_str(
                    screen, col, " Enter table filter: where ... ", curcol + " "
                )
                if curcol + " " == rfilter:
                    rfilter = "1=1"
                    filtered = 0
                elif rfilter == "":
                    rfilter = "1=1"
                    filtered = 0
                else:
                    filtered = 1
                act = ""
                # screen.move(0,0)
                # screen.clrtoeol()
                cls()
            # apply the general filter as default
            if filtered == 0:
                sql_cur_tab = sql_cur_tab.replace("""%FILTER%""", "1=1")
            # apply the input filter if requested
            else:
                sql_cur_tab = sql_cur_tab.replace("""%FILTER%""", rfilter)
            # apply the filter to the query
            sql_cur_tab = sql_cur_tab.replace("""%FILTER%""", rfilter)
            # if we have request to sort the table
            if act == "asc" or act == "desc":
                # prepare the ordinary number for the sorted column
                rsortcol = rcurx + 2
                # prepare the query
                sql_cur_tab = sql_cur_tab.replace(
                    """%SORTED%""", str(rsortcol) + " " + act
                )
                is_sorted = rsortcol
                sortdir = act
            # if noe sort is requested
            if is_sorted == 0:
                # apply the default sort by rowid
                sql_cur_tab = sql_cur_tab.replace("""%SORTED%""", "1 asc")
            else:
                # apply the user's sorting criteria
                sql_cur_tab = sql_cur_tab.replace(
                    """%SORTED%""", str(rsortcol) + " " + sortdir
                )
            # in the table browser (left window)
            if cur_win == "left":
                # calculate the shift for the rigth table view
                rwinshift = sum(xcolsz) + 1
            else:
                # oteherwise shift 2 chars
                rwinshift = 2
                # add < indicator the table browser is hidden
                screen.move(0, 0)
                screen.addstr("<", col["loGr"])
                # in case the table view is shifted
                if colshift > 0:
                    screen.move(1, 0)
                    screen.addstr("<", col["loGr"])
            # this is the main query to the table... we will TRY it
            try:
                # prepare the parameters for the query
                if DB == "postgres":
                    cur_tab_params = (
                        rtabt,
                        rtabf,
                    )
                else:
                    cur_tab_params = (
                        rtabf,
                        rtabt,
                    )
                # don't waste time if refresh is not requested
                # neither nothing has changed
                if (
                    sql_cur_tab != prev_tab_sql
                    or cur_tab_params != prev_tab_params
                    or act == "refresh"
                ):
                    try:
                        # try to get table data and column list
                        dbcon, res, cols = qry2dict(dbcon, sql_cur_tab, cur_tab_params)
                    except Exception as e:
                        # fallback on the right side
                        rfilter = "1=1"
                        filtered = 0
                    # save previous table name
                    prev_tab_sql = sql_cur_tab
                    # save preivous parameters list
                    prev_tab_params = cur_tab_params
                # print the list anyway there can be move
                # just on the table. No need to requery
                curd, maxxd, maxyd, xcoldsz = prn_list(
                    res, screen, he, wi, rwinshift, 0, rcurx, rcury, 1, colshift
                )
            except Exception as e:
                # handle complications
                error_handler(screen, he, wi, e, sys.exc_info())
                screen.refresh()
                tmp = screen.getch()
            # if we have no data
            if maxyd == 0:  # NO DATA
                # try to display at least list of columns
                screen.move(0, rwinshift)
                screen.addstr(
                    str("|".join(cols[1:]))[: (wi - 1 - rwinshift)], col["miGr"]
                )
                screen.move(1, rwinshift)
                screen.addstr("--| NO DATA |--", col["miGr"])
            # prepare current column
            curcol = ""
            # calculate the current column if there are any columns
            if len(cols) > 0:
                curcol = cols[rcurx + colshift + 1]
            # print the status (title) of the text user interface (tui)
            screen.move(he - 1, 0)
            screen.clrtoeol()
            screen.addstr(DB + " " + cur_win[0] + " ", col["loGr"])
            # print current table name
            screen.addstr(cur + " ", col["miGr"])
            # print current column name
            screen.addstr(curcol + " ", col["hiGr"])
            # print f flag if table is filtered
            if filtered == 1:
                screen.addstr("f ", col["loGr"])
            # print s flag if table is sorted
            if is_sorted > 0:
                screen.addstr("s ", col["loGr"])
            # if on mysql and table has primary key
            # if has_pk > 0 and maxyd > 0: # NO DATA
            #  screen.addstr("p "+str(res["rowid"][rcurx])+" ",col["loGr"])
            # Store Current Table View Preferences
            cfg_set_value(ccon, (stodb, curtab, "rfilter", rfilter, rfilter))
            cfg_set_value(ccon, (stodb, curtab, "rsortcol", rsortcol, rsortcol))
            cfg_set_value(ccon, (stodb, curtab, "sortdir", sortdir, sortdir))
            # move to the upper right corner
            screen.move(0, wi - 1)
            # make the cursor invisible
            curses.curs_set(0)
            # display connection info
            if act == "conn_info":
                cls()
                coninfo = read_conn_info(DB)
                sy = 1
                screen.move(sy, 0)
                if coninfo is None and DB != "sqlite":
                    screen.addstr("No Connection Information Available", col["hiGr"])
                elif DB == "sqlite":
                    screen.addstr("Connection Information", col["loGr"])
                    sy += 1
                    screen.move(sy, 0)
                    screen.addstr("{: <10s}: ".format("DB") + DB, col["miGr"])
                    sy += 1
                    screen.move(sy, 0)
                    screen.addstr("{: <10s}: ".format("db file"), col["miGr"])
                    screen.addstr(dbfile, col["hiGr"])
                else:
                    screen.addstr("Connection Information", col["loGr"])
                    sy += 1
                    screen.move(sy, 0)
                    screen.addstr("{: <10s}: ".format("DB") + DB, col["miGr"])
                    sy += 1
                    for val in coninfo:
                        screen.move(sy, 0)
                        if val != "password":
                            screen.addstr("{: <10s}: ".format(val), col["miGr"])
                            screen.addstr(coninfo[val], col["hiGr"])
                            sy += 1
                prev_tab = curtab
            # get next key
            k = screen.getch()
        dbcon.close()
        msg_log("-- Closing Connection")
        curses.endwin()
        msg_log("*| pydbro deinit")
    except Exception as e:
        curses.noecho()
        curses.endwin()
        traceback.print_exc(file=sys.stdout)
        exit()


def cli():
    main()


if __name__ == "__main__":
    main()
