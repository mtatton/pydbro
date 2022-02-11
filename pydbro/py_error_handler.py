#
# PROGRAM: PYTHON CONSOLE DATABASE BROWSER
# MODULE : CURSES ERROR HANDLER
#

import sys
import traceback


def error_handler(screen, he, wi, e, sys_exc_info):
    tramsg = ""
    exc_type, exc_value, exc_traceback = sys_exc_info
    traces = traceback.extract_tb(exc_traceback)
    for frame_summary in traces:
        tramsg += "{} {} | Any Key ...".format(frame_summary.name, frame_summary.lineno)
    screen.move(he - 1, 0)
    prnstr = str(e) + tramsg
    screen.addstr(prnstr[: wi - 1])
