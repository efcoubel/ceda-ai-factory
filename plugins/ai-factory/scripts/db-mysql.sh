#!/usr/bin/env bash
# Usage: db-mysql.sh <app> <environment> [tsv] < query.sql
# Runs a read-only query with a throwaway MariaDB client container, using the ~/.my.cnf section the
# ai-factory profile maps to <app>/<environment>. Refuses any environment the profile marks as
# production. tsv: raw tab-separated output for exports; otherwise a readable table.
set -euo pipefail
app=${1:?"Usage: db-mysql.sh <app> <environment> [tsv] < query.sql"}
environment=${2:?"Usage: db-mysql.sh <app> <environment> [tsv] < query.sql"}
format=-t
[ "${3:-}" = tsv ] && format=-B

section=$(python3 -I - "$app" "$environment" <<'PY'
import json, os, sys
app, environment = sys.argv[1], sys.argv[2]
directory = os.getcwd()
while True:
    path = os.path.join(directory, ".ai-factory", "profile.json")
    if os.path.isfile(path):
        break
    parent = os.path.dirname(directory)
    if parent == directory:
        sys.exit("No .ai-factory/profile.json above the current directory.")
    directory = parent
config = json.load(open(path, encoding="utf-8"))["tools"]["database"]["config"]
if environment in config.get("production_environments", ["production", "prod"]):
    sys.exit(f"Environment {environment} is production: refused.")
try:
    print(config["sections"][app][environment])
except KeyError:
    sys.exit(f"No ~/.my.cnf section mapped to {app}/{environment} in the profile.")
PY
)
grep -qx "\[$section\]" ~/.my.cnf || { echo "No [$section] section in ~/.my.cnf." >&2; exit 1; }
suffix=${section#client}
docker run --rm -i --network host -v ~/.my.cnf:/root/.my.cnf:ro "${AI_FACTORY_MYSQL_IMAGE:-mariadb:11.4}" \
  mariadb --defaults-group-suffix="$suffix" "$format" --connect-timeout=10 \
  --init-command="SET SESSION TRANSACTION READ ONLY"
