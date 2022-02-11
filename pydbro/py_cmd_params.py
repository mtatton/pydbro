#
# PROGRAM: PYTHON CONSOLE DATABASE BROWSER
# MODULE : COMMAND LINE PARAMETERS PROCESSOR
#

import getopt

cmd_help = """Python Console Database Browser

Specify database type using -d or --db_type")

Supported databases: sqlite, mysql, postres, oracle")

e.g. "+sys.argv[0]+" -d sqlite <filename>")"""


def prn_cmd_help():
    for line in cmd_help.split("\n"):
        print(line)


def cmd_params(argv):
    dbfile = ""
    DB = None
    try:
        optlist, args = getopt.getopt(argv[1:], "hd:", ["help", "db_type"])
        for name, value in optlist:
            if name in ["-h", "--help"]:
                prn_cmd_help()
                exit()
            elif name in ["-d", "--db_type"]:
                DB = value
        if DB is None:
            prn_cmd_help()
            exit()
        if len(args) == 1 and DB == "sqlite":
            dbfile = args[0]
        return (DB, dbfile)
    except Exception as e:
        print("Error Message " + str(e))
        exit()
