#
# PROGRAM: PYTHON CONSOLE DATABASE BROWSER
# MODULE : QUERY METHOD SETUP
#

import os
import sqlite3

from pydbro.py_sqlite_db import qry2dict as cfg_qry2dict

cfg_dbf = ":memory:"


def prep_cfg_storage():
    ccon = sqlite3.connect(cfg_dbf)
    ccon, cfg, cfgcol = cfg_qry2dict(
        ccon,
        "create table if not exists cfg (db text, tab text, key text, value text, primary key(db,tab,key))",
        (),
        cfg_dbf,
    )
    return ccon


def cfg_get_value(ccon, params):
    # Restore Current Table settings BEGIN
    ccon, cfg, cfgcol = cfg_qry2dict(
        ccon, "select * from cfg where tab = ? and key = ?", params, cfg_dbf
    )
    if "value" in cfg:
        return cfg["value"][0]
    else:
        return None


def cfg_set_value(ccon, params):
    # Store Current Table Settings
    ccon, cfg, cfgcol = cfg_qry2dict(
        ccon,
        """insert into cfg values (?,?,?,?)
       on conflict (db,tab,key)
       do update set value = ?""",
        params,
        cfg_dbf,
    )


def cfg_get_all(ccon):
    ccon, cfg, cfgcol = cfg_qry2dict("select * from cfg", (), cfg_dbf, ccon)
    return cfg


def cfg_path():
    cfg_dbf = ""
    try:
        home = os.path.expanduser("~")
    except Exception as e:
        pass
    try:
        os.mkdir(home + os.sep + ".config")
    except Exception as e:
        pass
    try:
        os.mkdir(home + os.sep + ".config" + os.sep + "pydbro")
    except Exception as e:
        pass
    try:
        cfg_dbf = home + os.sep + ".config" + os.sep + "pydbro" + os.sep + "cfg.db"
    except Exception as e:
        msg_log(str(e))
        cfg_dbf = "cfg.db"
        pass
    return cfg_dbf
