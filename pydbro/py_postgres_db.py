#
# PROGRAM: PYTHON CONSOLE DATABASE BROWSER
# MODULE : POSTGRES DATABASE CONNECTOR
#

import psycopg2
import traceback
import sys
import os
import json
import curses
from pydbro.py_log import msg_log

connfile = "sqlpk_conn.json"

constr = None
dsn = None


def create_con(con):
    # global con
    global constr
    if os.path.exists("sqlpk_conn.json"):
        f = open("sqlpk_conn.json", "r")
        dbcontmp = f.read()
        f.close()
        constr = json.loads(dbcontmp)
    else:
        curses.endwin()
        print("Please use coned to prepare connection")
        exit()
    # print(str(constr))
    if con is None:
        con = psycopg2.connect(**constr)
    return con


def set_conn(p_db_name):
    global connstr
    connstr = p_db_name


def get_conn():
    global connstr
    return connstr


def get_postgres_db():
    db = None
    if os.path.exists("sqlpk_conn.json"):
        f = open("sqlpk_conn.json", "r")
        dbcontmp = f.read()
        f.close()
        constr = json.loads(dbcontmp)
        # msg_log(str(constr))
        if "database" in constr:
            db = constr["database"]
            # msg_log(db)
    return db


def qry2dict(con, qry, qry_params=()):
    global constr
    # global con
    res = {}
    cols = []
    try:
        if con is None:
            con = create_con(con)
        cur = con.cursor()
        cur.execute(qry, qry_params)
        # con.commit()
        data = cur.fetchall()
        for col in cur.description:
            cols.append(col[0])
        # con.close()
        if len(data) > 0:
            i = 0
            for col in cols:
                res[col] = []
                for row in data:
                    res[col].append(row[i])
                i += 1
    except Exception as e:
        tramsg = ""
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traces = traceback.extract_tb(exc_traceback)
        for frame_summary in traces:
            tramsg += "{} {}".format(frame_summary.name, frame_summary.lineno)
        msg_log("ERROR : " + str(e) + " " + qry + " " + tramsg)
        pass
    return (con, res, cols)
