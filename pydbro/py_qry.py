#
# PROGRAM: PYTHON CONSOLE DATABASE BROWSER
# MODULE : QUERY METHOD SETUP
#

import os


def setup_qry_method(DB, dbfile):
    qry2dict = None
    if DB == "sqlite":
        from pydbro.py_sqlite_db import qry2dict
        from pydbro.py_sqlite_db import set_conn

        set_conn(dbfile)
        if not os.path.isfile(dbfile):
            print("Invalid file specified")
            exit()
    elif DB == "mysql":
        from pydbro.py_mysql_db import qry2dict
    elif DB == "postgres":
        from pydbro.py_postgres_db import qry2dict
    elif DB == "oracle":
        import pydbro.py_ora_db
        from pydbro.py_ora_db import qry2dict
    return qry2dict
