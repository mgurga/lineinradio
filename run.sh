#!/bin/bash

python3 manage.py runserver 0.0.0.0:8000 &
python3 manage.py qcluster &
mpd --no-daemon radio/mpd.conf &

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?