# This script starts the monitoring mechanism for SQL queries
# and clears the content of the dict used for the analysis.
# flake8: noqa

db.monitor_orm_statements = True
db.orm_statements.clear()
db.orm_statements_runtime.clear()
