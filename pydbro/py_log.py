#
# PROGRAM: PYTHON CONSOLE DATABASE BROWSER
# MODULE : LOG
#

from datetime import datetime

DEBUG = 0


def msg_log(msg):
    dt = datetime.now()
    if DEBUG == 1:
        f = open("/tmp/pydbro.log", "a")
        f.write(str(dt) + " " + msg + "\n")
        f.close()
