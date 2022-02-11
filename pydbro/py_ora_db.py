#
# PROGRAM: PYTHON CONSOLE DATABASE BROWSER
# MODULE : ORACLE DATABASE CONNECTOR
#

import cx_Oracle
import traceback
import sys
import os
import json
import curses
from pydbro.py_log import msg_log

connfile = "sqlok_conn.json"

constr = None
dsn = None


def read_conn(connfile):
    global constr
    if os.path.exists(connfile):
        if constr is None:
            f = open(connfile, "r")
            dbcontmp = f.read()
            f.close()
            constr = json.loads(dbcontmp)
            msg_log("-- Reading connection file")
    else:
        curses.endwin()
        print("Please use coned to prepare connection")
        exit()


def create_dsn(con, recon=0):
    read_conn(connfile)
    dsn = cx_Oracle.makedsn(
        host=constr["host"], port=constr["port"], service_name=constr["database"]
    )
    if con is None or recon == 1:
        con = cx_Oracle.connect(
            user=constr["user"], password=constr["password"], dsn=dsn
        )
        msg_log("-- Ora Creating Con")
    return con


def process_data(cur, data):
    res = {}
    cols = []
    if cur.description is not None:
        for col in cur.description:
            cols.append(col[0])
    if len(data) > 0:
        i = 0
        for col in cols:
            res[col] = []
            for row in data:
                res[col].append(row[i])
            i += 1
    return (res, cols)


def qry2dict(con, qry, qry_params=()):

    data = None
    res = {}
    cols = []

    try:
        if con is None:
            con = create_dsn(con)
        cur = con.cursor()
        try:
            cur.execute(qry, qry_params)
        except Exception as e:
            if "select" in qry:
                msg_log("-- Trying to reconnect...")
                con = create_dsn(con, recon=1)
                cur = con.cursor()
                cur.execute(qry, qry_params)
            else:
                msg_log("--! Problem executing Query: " + str(e))
                return (con, res, cols)
        try:
            data = cur.fetchall()
        except Exception as e:
            con.commit()
            return (con, res, cols)
        res, cols = process_data(cur, data)
        return (con, res, cols)
    except Exception as e:
        tramsg = ""
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traces = traceback.extract_tb(exc_traceback)
        for frame_summary in traces:
            tramsg += "{} {}".format(frame_summary.name, frame_summary.lineno)
        msg_log("ERROR : " + str(e) + " " + qry + " " + tramsg)
        pass
