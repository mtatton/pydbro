#
# PROGRAM: PYTHON CONSOLE DATABASE BROWSER
# MODULE : SQLITE DATABASE CONNECTOR
#

import sqlite3
import traceback
import sys

from datetime import datetime
from pydbro.py_log import msg_log

connstr = "./db/001.db"


def set_conn(p_db_name):
    global connstr
    connstr = p_db_name


def get_conn():
    global connstr
    return connstr


def qry2dict(con, qry, qry_params=(), dbfile=None):
    res = {}
    try:
        dt = str(datetime.now())
        # msg_log(dt+" "+qry+"\n")
        # if dbfile is None:
        if con is None:
            con = sqlite3.connect(get_conn())
        cur = con.cursor()
        cur.execute(qry, qry_params)
        try:
            data = cur.fetchall()
        except:
            con.commit()
            return (con, res, cols)
        cols = []
        if cur.description is not None:
            for col in cur.description:
                cols.append(col[0])
            # if dbfile is not None:
            con.commit()
            # else:
            #  con.close()
            if len(data) > 0:
                i = 0
                for col in cols:
                    res[col] = []
                    for row in data:
                        res[col].append(row[i])
                    i += 1
        return (con, res, cols)
    except Exception as e:
        # con.close()
        # traceback.print_exc(file=sys.stdout)
        # print ("ERR [ FAILED QRY DATABASE ] 001000x0010 (1) : Cannot Query Database")
        tramsg = ""
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traces = traceback.extract_tb(exc_traceback)
        for frame_summary in traces:
            tramsg += "{} {}".format(frame_summary.name, frame_summary.lineno)
        msg_log("ERROR : " + str(e) + " " + qry + " " + tramsg)
        pass
