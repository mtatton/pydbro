#!/bin/bash
while true 
do
  clear
  DB="sqlite mysql postgres oracle coned exit"
  select db in $DB; do
    if [ "$db" = "sqlite" ]; then
      dbro -d sqlite ./pydbro/db/manual.db
    elif [ "$db" = "mysql" ]; then
      dbro -d mysql
    elif [ "$db" = "postgres" ]; then
      dbro -d postgres
    elif [ "$db" = "oracle" ]; then
      dbro -d oracle
    elif [ "$db" = "coned" ]; then
      coned
     elif [ "$db" = "exit" ]; then
      exit
    fi
  done
done
