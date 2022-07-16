#!/bin/sh
set -e ${DEBUG:+-x}

if [ -n "${POSTGRE_HOST:-}" ]; then
  echo >&3 "=> up workers..."
  #3 worker
  python3 label_studio/manage.py rqworker pre_tags >&3

  python3 label_studio/manage.py rqworker algorithm_clean >&3

  python3 label_studio/manage.py rqworker prompt >&3
  echo >&3 "=> workers up completed."
else
  echo >&3 "=> Skipping run workers."
fi