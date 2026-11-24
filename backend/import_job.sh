#!/usr/bin/env bash
# The owb-import cron job (render.yaml): bring the database in step with the
# content/ it was deployed with. This used to be owb-api's pre-deploy, where
# it ran up to 25 of Render's 30 allowed minutes on every deploy, billed as
# pipeline minutes, and each new language added about a minute.
#
# Load any missing source texts, import the content/ files that changed and
# update the search entries that changed, then email the super admins if the
# import failed or left work (send_alerts). import_content stops starting
# files after BUDGET, search languages after SEARCH_BUDGET and writes nothing
# after the deadline; what is left waits for the next run, which starts
# where this one stopped. The deadline stays under the hourly schedule.
set -u
cd "$(dirname "$0")/.."

BUDGET=${OWB_IMPORT_BUDGET:-1800}
SEARCH_BUDGET=${OWB_IMPORT_SEARCH_BUDGET:-2700}
END=$(( $(date +%s) + ${OWB_IMPORT_DEADLINE:-3000} ))

# owb-api's pre-deploy applies migrations. Until it has, this job's code may
# expect tables the database doesn't have yet: skip this run.
if ! python backend/manage.py migrate --check >/dev/null 2>&1; then
  echo "Migrations not applied yet (owb-api applies them when it deploys); nothing imported this run."
  exit 0
fi

python backend/manage.py import_texts --missing || exit $?
python backend/manage.py import_content --if-texts-loaded --budget "$BUDGET" \
  --search-budget "$SEARCH_BUDGET" --deadline "$END" --separate-processes
status=$?
python backend/manage.py send_alerts
exit $status
