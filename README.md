[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
```
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
  ----------------------------------------```
```
![PYDBRO SCREEN](https://raw.githubusercontent.com/mtatton/pydbro/master/pydbro.png)

 PROGRAM: PYTHON CONSOLE DATABASE BROWSER

```
Help Keyboard Controls:

?   - this help

$   - connection information
j   - move down
k   - move up
h   - move left
l   - move right
L   - shift columns right
H   - shift columns left
0   - go to upper left table corner
G   - go to lower right table corner
n   - next page of records
u   - previous page of records
s   - sort ascending by current column
S   - sort descending by current column
f   - filter (enter claus after where ... )
tab - toggle left / right panel (tables, table content) 
m   - move rows view by 1 page down (tables list)
i   - move rows view by 1 page up (tables list)
r   - reread
e   - edit current cell
d   - delete current row
a   - add new row
X   - reset view (filter, sort) on current table
@   - scroll current row to the top

Note:

Currently the insert, update, delete are only
supported on sqlite and oracle. The other databases
doesn't have rowid pseudo column.

To run this program on Windows You should need
the unofficial curses package for windows.
You can get it here:
Python Extension Packages for Windows - Christoph Gohlke
http://pythonic.zoomquiet.top/data/20101216091618/index.html

To Install use:

$ pip install pydbro

To setup connection you can use the coned program.
To run the coned just use:

$ coned

This will generate json with connectin information
to connect to the mysql, postgres or oracle database.

If You wish to open sqlite file just specify:

$ pydbro -d sqlite file.db

To connect to other databases use:

$ pydbro -d [mysql|postgres|oracle]

and connect according to connection json.

To connect to the mysql|postgres|oracle database You
would need following packages:

for MySQL:    $ pip install mysql-connector 
for Oracle:   $ pip install cx_Oracle 
for Postgres: $ pip install psycopg2-binary

To develop or use the git repository version use:

$ python3 setup.py develop

To both use the commands and run.sh

Special Thanks goes to:

Lawrence Manuel aka Smooth for the Logo

```
