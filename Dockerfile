#--==================================================--
#  ______   _____ ___   ___ ______    ____
#  \     `\|  |  |   `\|   |\     `\/'    |
#   |   T  |  |  |>    |  <__|   >  |     |
#   |   '_,|__   |     |     |     /'  T  |
#   |   |  __/  /|  T  |  T  |     `|  :  |
#   |   | |     ||  '  |  '  |   |  |     |
#   `---' `-----'`-----'-----'---'--`-----'
#
#                                         [ DOKR FILE ]
#
#--==================================================--
# NBTERMIX DOCKER FILE
FROM debian:latest
# INSTALL PKGS
RUN apt-get update && apt-get install -y python3-pip python3
# INSTALL PYDBRO
RUN pip install pydbro
